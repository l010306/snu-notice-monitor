"""
SNU公告监控系统优化版
用于监控首尔大学官网公告，发现新公告时发送邮件通知
"""
import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import logging
import time
import argparse
from datetime import datetime
from snu_config import Config

# 配置日志
Config.ensure_dirs()
handlers = []
if Config.LOG_TO_FILE:
    handlers.append(logging.FileHandler(Config.get_log_file(), encoding='utf-8'))
if Config.LOG_TO_CONSOLE:
    handlers.append(logging.StreamHandler())

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)


class SNUNotifier:
    """SNU公告监控类"""
    
    def __init__(self):
        """初始化监控器"""
        logger.info("=" * 60)
        logger.info("SNU公告监控系统启动")
        logger.info("=" * 60)
        
        # 验证配置
        try:
            Config.validate_email_config()
            logger.info("✓ 邮件配置验证通过")
        except ValueError as e:
            logger.error(str(e))
            raise
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def _fetch_with_retry(self, url, max_retries=None):
        """
        带重试机制的HTTP请求
        
        Args:
            url: 请求URL
            max_retries: 最大重试次数（默认使用配置）
            
        Returns:
            Response对象，失败返回None
        """
        max_retries = max_retries or Config.MAX_RETRIES
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"正在请求: {url} (尝试 {attempt + 1}/{max_retries})")
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=Config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                response.encoding = 'utf-8'
                return response
                
            except requests.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    delay = Config.RETRY_DELAY * (2 ** attempt)  # 指数退避
                    logger.info(f"等待 {delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    logger.error(f"达到最大重试次数，放弃请求: {url}")
                    return None
        
        return None
    
    def _validate_announcement(self, title, url):
        """
        验证公告数据有效性
        
        Args:
            title: 公告标题
            url: 公告链接
            
        Returns:
            是否有效
        """
        if not title or not url:
            logger.debug("标题或URL为空")
            return False
        
        title = title.strip()
        
        # 检查标题长度
        if len(title) < Config.MIN_TITLE_LENGTH:
            logger.debug(f"标题过短: {title}")
            return False
        
        if len(title) > Config.MAX_TITLE_LENGTH:
            logger.warning(f"标题过长，可能有误: {title[:50]}...")
            return False
        
        # 检查URL格式
        if not url.startswith('http'):
            logger.debug(f"URL格式错误: {url}")
            return False
        
        return True
    
    def get_announcements(self):
        """
        抓取所有目标网站的公告
        
        Returns:
            字典，格式：{"网站名": [{"title": "...", "url": "..."}]}
        """
        logger.info(f"开始抓取 {len(Config.TARGETS)} 个网站...")
        results = {}
        
        for site in Config.TARGETS:
            site_name = site['name']
            logger.info(f"正在抓取: {site_name}")
            
            try:
                # 请求页面
                response = self._fetch_with_retry(site['url'])
                if not response:
                    logger.error(f"❌ {site_name} 抓取失败")
                    results[site_name] = []
                    continue
                
                # 解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                items = soup.select(site['selector'])
                
                if not items:
                    logger.warning(f"⚠️  {site_name} 未匹配到公告")
                    results[site_name] = []
                    continue
                
                # 提取公告数据
                announcements = []
                for item in items[:Config.MAX_ITEMS_PER_SITE]:
                    title = item.get_text(strip=True)
                    href = item.get('href', '')
                    
                    # 处理相对URL
                    if href and not href.startswith('http'):
                        url = site['base_url'] + href
                    else:
                        url = href
                    
                    # 验证数据
                    if self._validate_announcement(title, url):
                        announcements.append({
                            "title": title,
                            "url": url
                        })
                
                results[site_name] = announcements
                logger.info(f"✓ {site_name} 抓取成功，获得 {len(announcements)} 条公告")
                
            except Exception as e:
                logger.error(f"❌ 抓取 {site_name} 时出错: {e}")
                results[site_name] = []
        
        return results
    
    def load_history(self):
        """
        加载历史记录
        
        Returns:
            历史数据字典
        """
        if not Config.HISTORY_FILE.exists():
            logger.info("历史文件不存在，创建新的")
            return {}
        
        try:
            with open(Config.HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
            logger.info(f"✓ 加载历史记录成功")
            return history
        except Exception as e:
            logger.error(f"❌ 加载历史记录失败: {e}")
            return {}
    
    def save_history(self, data):
        """
        保存历史记录
        
        Args:
            data: 要保存的数据
        """
        try:
            with open(Config.HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("✓ 历史记录已更新")
        except Exception as e:
            logger.error(f"❌ 保存历史记录失败: {e}")
    
    def find_new_announcements(self, current_data, history):
        """
        找出新公告
        
        Args:
            current_data: 当前抓取的数据
            history: 历史数据
            
        Returns:
            新公告列表
        """
        new_updates = []
        
        for site_name, announcements in current_data.items():
            # 获取历史标题
            old_titles = [item['title'] for item in history.get(site_name, [])]
            
            # 查找新公告
            for item in announcements:
                if item['title'] not in old_titles:
                    new_updates.append({
                        'site': site_name,
                        'title': item['title'],
                        'url': item['url']
                    })
                    logger.info(f"🆕 发现新公告: [{site_name}] {item['title'][:50]}...")
        
        return new_updates
    
    def send_email(self, new_updates):
        """
        发送邮件通知
        
        Args:
            new_updates: 新公告列表
        """
        # 格式化邮件内容
        updates_text = []
        for update in new_updates:
            updates_text.append(
                f"📌 {update['site']}\n"
                f"标题: {update['title']}\n"
                f"地址: {update['url']}"
            )
        
        body = Config.EMAIL_TEMPLATE.format(updates="\n\n".join(updates_text))
        
        # 创建邮件
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = Header(Config.EMAIL_SUBJECT, 'utf-8')
        msg['From'] = Config.SENDER_EMAIL
        msg['To'] = Config.RECEIVER_EMAIL
        
        # 发送邮件
        try:
            logger.info("正在发送邮件...")
            with smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
                server.sendmail(
                    Config.SENDER_EMAIL,
                    [Config.RECEIVER_EMAIL],
                    msg.as_string()
                )
            logger.info("✓ 邮件发送成功！")
            return True
        except Exception as e:
            logger.error(f"❌ 邮件发送失败: {e}")
            return False
    
    def run(self, dry_run=False):
        """
        运行监控
        
        Args:
            dry_run: 如果为True，不发送邮件，只显示内容
        """
        logger.info("开始检查官网更新...")
        
        # 抓取当前数据
        current_data = self.get_announcements()
        
        # 加载历史
        history = self.load_history()
        
        # 找出新公告
        new_updates = self.find_new_announcements(current_data, history)
        
        # 更新历史记录
        self.save_history(current_data)
        
        # 处理结果
        if new_updates:
            logger.info(f"🎉 检测到 {len(new_updates)} 条新公告")
            
            if dry_run:
                logger.info("【干运行模式】不发送邮件，内容如下：")
                for update in new_updates:
                    print(f"\n📌 {update['site']}")
                    print(f"标题: {update['title']}")
                    print(f"地址: {update['url']}")
            else:
                self.send_email(new_updates)
        else:
            logger.info("✅ 暂无新公告")
        
        logger.info("=" * 60)
        logger.info("检查完成")
        logger.info("=" * 60)


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='SNU公告监控系统 - 自动监控首尔大学官网公告'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='干运行模式，不发送邮件，只显示新公告内容'
    )
    args = parser.parse_args()
    
    try:
        notifier = SNUNotifier()
        notifier.run(dry_run=args.dry_run)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  用户中断程序")
    except Exception as e:
        logger.error(f"\n❌ 程序执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        exit(1)


if __name__ == "__main__":
    main()
