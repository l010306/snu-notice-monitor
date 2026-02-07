"""
SNU公告监控系统配置文件
"""
import os
from pathlib import Path

class Config:
    """配置类 - 集中管理所有配置参数"""
    
    # ==================== 文件路径 ====================
    BASE_DIR = Path(__file__).parent
    HISTORY_FILE = BASE_DIR / "announcement_history.json"
    LOG_DIR = BASE_DIR / "logs"
    
    # ==================== 邮件配置 ====================
    SMTP_SERVER = "smtp.qq.com"
    SMTP_PORT = 465
    
    # 从环境变量读取（必须设置）
    SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
    SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')
    RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')
    
    # ==================== 监控网站配置 ====================
    TARGETS = [
        {
            "name": "SNU OIA (国际处)",
            "url": "https://oia.snu.ac.kr/notice-all",
            "selector": "td.views-field-title a",
            "base_url": "https://oia.snu.ac.kr"
        },
        {
            "name": "SNU CBA (经营大学)",
            "url": "https://cba.snu.ac.kr/newsroom/notice?sc=y",
            "selector": "td.title.noti-tit a",
            "base_url": "https://cba.snu.ac.kr"
        }
    ]
    
    # ==================== 抓取设置 ====================
    REQUEST_TIMEOUT = 15        # 请求超时（秒）
    MAX_ITEMS_PER_SITE = 10     # 每个网站抓取公告数量
    MAX_RETRIES = 3             # 最大重试次数
    RETRY_DELAY = 2             # 重试延迟（秒）
    
    # ==================== 邮件内容 ====================
    EMAIL_SUBJECT = "【自动提醒】首尔大学官网有新公告更新！"
    EMAIL_TEMPLATE = "发现以下新通知，请及时查看：\n\n{updates}"
    
    # ==================== 日志配置 ====================
    LOG_LEVEL = "INFO"          # 日志级别: DEBUG, INFO, WARNING, ERROR
    LOG_TO_FILE = True          # 是否保存日志到文件
    LOG_TO_CONSOLE = True       # 是否在控制台显示日志
    
    # ==================== 数据验证 ====================
    MIN_TITLE_LENGTH = 3        # 最小标题长度
    MAX_TITLE_LENGTH = 500      # 最大标题长度
    
    @classmethod
    def validate_email_config(cls):
        """验证邮件配置是否完整"""
        missing = []
        if not cls.SENDER_EMAIL:
            missing.append('SENDER_EMAIL')
        if not cls.SENDER_PASSWORD:
            missing.append('SENDER_PASSWORD')
        if not cls.RECEIVER_EMAIL:
            missing.append('RECEIVER_EMAIL')
        
        if missing:
            raise ValueError(
                f"❌ 缺少环境变量: {', '.join(missing)}\n\n"
                f"请设置环境变量：\n"
                f"  export SENDER_EMAIL='your_email@qq.com'\n"
                f"  export SENDER_PASSWORD='your_qq_auth_code'\n"
                f"  export RECEIVER_EMAIL='receiver@example.com'\n\n"
                f"详细说明请查看 SNU公告监控使用说明.md"
            )
    
    @classmethod
    def ensure_dirs(cls):
        """确保必要的目录存在"""
        if cls.LOG_TO_FILE:
            cls.LOG_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_log_file(cls):
        """获取日志文件路径"""
        if not cls.LOG_TO_FILE:
            return None
        return cls.LOG_DIR / "snu_notifier.log"
