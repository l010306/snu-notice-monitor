"""
SNU公告监控系统测试脚本
用于测试爬虫是否能正常抓取公告
"""
import requests
from bs4 import BeautifulSoup
from snu_config import Config


def test_scraper():
    """测试所有监控网站"""
    print("=" * 60)
    print("SNU公告监控系统 - 测试模式")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for site in Config.TARGETS:
        print(f"\n--- 正在测试: {site['name']} ---")
        print(f"URL: {site['url']}")
        
        try:
            # 请求页面
            print("正在请求页面...")
            response = requests.get(
                site['url'],
                headers=headers,
                timeout=Config.REQUEST_TIMEOUT
            )
            response.encoding = 'utf-8'
            print(f"✓ 请求成功 (状态码: {response.status_code})")
            
            # 解析HTML
            print(f"正在解析HTML（选择器: {site['selector']}）...")
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select(site['selector'])
            
            if not items:
                print("❌ 未匹配到任何内容")
                print("提示：网站可能改版，请检查CSS选择器")
                continue
            
            print(f"✓ 成功匹配到 {len(items)} 条公告")
            
            # 显示前5条
            print("\n前5条公告：")
            for i, item in enumerate(items[:5], 1):
                title = item.get_text(strip=True)
                href = item.get('href', '')
                
                # 处理相对URL
                if href and not href.startswith('http'):
                    url = site['base_url'] + href
                else:
                    url = href
                
                print(f"\n[{i}] {title}")
                print(f"    URL: {url}")
            
            print(f"\n✅ {site['name']} 测试通过！")
            
        except requests.Timeout:
            print(f"❌ 请求超时（超过 {Config.REQUEST_TIMEOUT} 秒）")
        except requests.RequestException as e:
            print(f"❌ 请求失败: {e}")
        except Exception as e:
            print(f"❌ 解析失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_scraper()
