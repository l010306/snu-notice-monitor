# snu-notice-monitor
An automated notification system for SNU official announcements. Sends instant email alerts for new updates to keep students and staff informed.

# SNU 公告监控系统项目说明

## 📋 项目简介

这是一个用于监控**首尔大学（Seoul National University, SNU）**官网公告的自动化监控系统。当有新公告发布时，会通过电子邮件自动通知用户，帮助留学生和相关人员及时获取学校的重要信息。

### 🎯 核心功能

- ✅ **自动抓取公告**：定时访问SNU官网，获取最新公告列表
- ✅ **智能对比**：与历史记录比对，识别新发布的公告
- ✅ **邮件通知**：发现新公告后自动发送邮件提醒
- ✅ **多站点监控**：同时监控多个学院/部门网站
- ✅ **断点重试**：网络失败自动重试（指数退避）
- ✅ **环境变量保护**：邮箱密码等敏感信息使用环境变量
- ✅ **完整日志**：记录所有运行过程，便于追踪和调试
- ✅ **干运行模式**：测试用，不发送邮件

### 🏗️ 项目架构

```
SNU_Notice_Notifier/
├── snu_config.py                 # 配置模块 - 管理所有参数
├── snu_notifier_optimized.py     # 主程序 - 监控核心逻辑
├── snu_test.py                   # 测试脚本 - 验证爬虫功能
├── announcement_history.json     # 历史记录（自动生成）
└── logs/                         # 日志目录（自动生成）
    └── snu_notifier.log
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install requests beautifulsoup4
```

### 2. 配置QQ邮箱

**获取QQ邮箱授权码**：

1. 登录 [QQ邮箱网页版](https://mail.qq.com)
2. 点击 **设置** → **账户**
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务**
4. 开启 **POP3/SMTP服务** 或 **IMAP/SMTP服务**
5. 点击 **生成授权码**
6. 按提示发送短信
7. 复制生成的授权码（16位）

**重要**：授权码不是邮箱密码！

### 3. 设置环境变量

**macOS/Linux**：

```bash
# 临时设置（当前终端有效）
export SENDER_EMAIL="your_email@qq.com"
export SENDER_PASSWORD="你的QQ邮箱授权码"
export RECEIVER_EMAIL="receiver@example.com"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export SENDER_EMAIL="your_email@qq.com"' >> ~/.zshrc
echo 'export SENDER_PASSWORD="你的授权码"' >> ~/.zshrc
echo 'export RECEIVER_EMAIL="receiver@example.com"' >> ~/.zshrc
source ~/.zshrc
```

**Windows PowerShell**：

```powershell
$env:SENDER_EMAIL="your_email@qq.com"
$env:SENDER_PASSWORD="你的QQ邮箱授权码"
$env:RECEIVER_EMAIL="receiver@example.com"
```

**验证配置**：

```bash
echo $SENDER_EMAIL
```

### 4. 测试爬虫功能

运行测试脚本，确保能正常抓取公告：

```bash
python snu_test.py
```

**成功输出示例**：

```
============================================================
SNU公告监控系统 - 测试模式
============================================================

--- 正在测试: SNU OIA (国际处) ---
URL: https://oia.snu.ac.kr/notice-all
正在请求页面...
✓ 请求成功 (状态码: 200)
正在解析HTML（选择器: td.views-field-title a）...
✓ 成功匹配到 20 条公告

前5条公告：

[1] 2026学年春季学期交换生申请通知
    URL: https://oia.snu.ac.kr/notice/12345

✅ SNU OIA (国际处) 测试通过！
```

### 5. 运行监控系统

**干运行模式**（测试用，不发邮件）：

```bash
python snu_notifier_optimized.py --dry-run
```

**正常模式**（发送邮件）：

```bash
python snu_notifier_optimized.py
```

### 6. 设置定时任务

**macOS/Linux (cron)**：

```bash
# 编辑定时任务
crontab -e

# 每小时运行一次（在第0分钟）
0 * * * * cd /path/to/SNU_Notice_Notifier && python3 snu_notifier_optimized.py

# 每天早上9点和下午5点运行
0 9,17 * * * cd /path/to/SNU_Notice_Notifier && python3 snu_notifier_optimized.py

# 工作日每天早上10点运行
0 10 * * 1-5 cd /path/to/SNU_Notice_Notifier && python3 snu_notifier_optimized.py
```

**Windows (任务计划程序)**：

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（例如：每天10:00）
4. 操作：启动程序 `python snu_notifier_optimized.py`
5. 工作目录：设置为项目路径

---

## 📁 文件详解

### 1. snu_config.py - 配置模块

**作用**：集中管理所有配置参数，方便维护和修改。

**主要配置项**：

```python
class Config:
    # ==================== 文件路径 ====================
    HISTORY_FILE = "announcement_history.json"  # 历史记录文件
    LOG_DIR = "logs/"                           # 日志目录
    
    # ==================== 邮件配置 ====================
    SMTP_SERVER = "smtp.qq.com"  # QQ邮箱SMTP服务器
    SMTP_PORT = 465              # SSL端口
    
    # 从环境变量读取（安全）
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
    MAX_ITEMS_PER_SITE = 10     # 每个网站抓取数量
    MAX_RETRIES = 3             # 最大重试次数
    RETRY_DELAY = 2             # 重试延迟（秒）
    
    # ==================== 邮件内容 ====================
    EMAIL_SUBJECT = "【自动提醒】首尔大学官网有新公告更新！"
    EMAIL_TEMPLATE = "发现以下新通知，请及时查看：\n\n{updates}"
    
    # ==================== 日志配置 ====================
    LOG_LEVEL = "INFO"          # 日志级别
    LOG_TO_FILE = True          # 是否保存日志到文件
    LOG_TO_CONSOLE = True       # 是否在控制台显示
```

---

### 2. snu_notifier_optimized.py - 主程序

**作用**：监控核心逻辑，负责抓取、对比、通知。

**核心类**：`SNUNotifier`

**主要方法**：

| 方法 | 功能 |
|------|------|
| `__init__()` | 初始化，验证邮件配置 |
| `_fetch_with_retry()` | 带重试机制的HTTP请求 |
| `_validate_announcement()` | 验证公告数据有效性 |
| `get_announcements()` | 抓取所有网站的公告 |
| `load_history()` | 加载历史记录 |
| `save_history()` | 保存历史记录 |
| `find_new_announcements()` | 对比找出新公告 |
| `send_email()` | 发送邮件通知 |
| `run()` | 主流程（可指定干运行） |

**工作流程**：

```
1. 验证环境变量配置
   ↓
2. 抓取所有目标网站的公告
   ↓
3. 加载历史记录（announcement_history.json）
   ↓
4. 对比新旧数据，找出新公告
   ↓
5. 更新历史记录
   ↓
6. 如果有新公告：
   - 干运行模式：打印到控制台
   - 正常模式：发送邮件
   否则：
   - 记录"暂无新公告"
```

**重试机制**（第54-90行）：

```python
def _fetch_with_retry(self, url, max_retries=3):
    """带指数退避的重试机制"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=15)
            return response
        except Exception as e:
            if attempt < max_retries - 1:
                delay = 2 * (2 ** attempt)  # 2秒、4秒、8秒
                time.sleep(delay)
```

---

### 3. snu_test.py - 测试脚本

**作用**：验证爬虫功能是否正常，不需要配置邮箱即可运行。

**测试内容**：

1. ✅ 网络连接是否正常
2. ✅ 网页是否能访问
3. ✅ CSS选择器是否有效
4. ✅ 能否成功提取公告

**使用场景**：

- 首次部署时测试
- 网站改版后验证
- 定期检查系统状态

---

## 🔑 核心技术解析

### 1. 环境变量验证

**问题**：如果不验证，程序会在发送邮件时才报错，浪费时间。

**解决方案**（第59-78行）：

```python
@classmethod
def validate_email_config(cls):
    """启动时验证环境变量"""
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
            f"  export RECEIVER_EMAIL='receiver@example.com'"
        )
```

**优势**：
- ✅ 启动时立即发现配置问题
- ✅ 提供详细的错误提示
- ✅ 避免运行到一半才失败

---

### 2. 历史记录对比

**数据结构**（`announcement_history.json`）：

```json
{
  "SNU OIA (国际处)": [
    {
      "title": "2026学年春季学期交换生申请通知",
      "url": "https://oia.snu.ac.kr/notice/12345"
    },
    {
      "title": "关于签证延期的通知",
      "url": "https://oia.snu.ac.kr/notice/12346"
    }
  ],
  "SNU CBA (经营大学)": [...]
}
```

**对比逻辑**（第218-245行）：

```python
def find_new_announcements(self, current_data, history):
    """找出新公告"""
    new_updates = []
    
    for site_name, announcements in current_data.items():
        # 获取历史标题列表
        old_titles = [item['title'] for item in history.get(site_name, [])]
        
        # 查找新公告（标题不在历史记录中）
        for item in announcements:
            if item['title'] not in old_titles:
                new_updates.append({
                    'site': site_name,
                    'title': item['title'],
                    'url': item['url']
                })
    
    return new_updates
```

---

### 3. 指数退避重试

**策略**：

- 第1次失败：等待 2 秒
- 第2次失败：等待 4 秒
- 第3次失败：放弃

**实现**（第82-85行）：

```python
delay = Config.RETRY_DELAY * (2 ** attempt)
# attempt=0: 2 * (2^0) = 2秒
# attempt=1: 2 * (2^1) = 4秒
# attempt=2: 2 * (2^2) = 8秒
time.sleep(delay)
```

**优势**：
- ✅ 避免频繁请求导致被封IP
- ✅ 给服务器恢复时间
- ✅ 提高成功率

---

## 📊 运行效果

### 首次运行（建立历史记录）

```bash
$ python snu_notifier_optimized.py
============================================================
SNU公告监控系统启动
============================================================
✓ 邮件配置验证通过
开始检查官网更新...
开始抓取 2 个网站...
正在抓取: SNU OIA (国际处)
✓ SNU OIA (国际处) 抓取成功，获得 10 条公告
正在抓取: SNU CBA (经营大学)
✓ SNU CBA (经营大学) 抓取成功，获得 10 条公告
历史文件不存在，创建新的
✓ 历史记录已更新
✅ 暂无新公告
============================================================
检查完成
============================================================
```

→ 生成 `announcement_history.json`，记录当前所有公告

### 发现新公告

```bash
$ python snu_notifier_optimized.py
============================================================
SNU公告监控系统启动
============================================================
✓ 邮件配置验证通过
开始检查官网更新...
开始抓取 2 个网站...
正在抓取: SNU OIA (国际处)
✓ SNU OIA (国际处) 抓取成功，获得 10 条公告
正在抓取: SNU CBA (经营大学)
✓ SNU CBA (经营大学) 抓取成功，获得 10 条公告
✓ 加载历史记录成功
🆕 发现新公告: [SNU OIA (国际处)] 2026学年春季学期交换生申请通知
✓ 历史记录已更新
🎉 检测到 1 条新公告
正在发送邮件...
✓ 邮件发送成功！
============================================================
检查完成
============================================================
```

### 干运行模式

```bash
$ python snu_notifier_optimized.py --dry-run
...
🎉 检测到 1 条新公告
【干运行模式】不发送邮件，内容如下：

📌 SNU OIA (国际处)
标题: 2026学年春季学期交换生申请通知
地址: https://oia.snu.ac.kr/notice/12345
```

---

## ⚙️ 配置说明

### 添加监控网站

编辑 `snu_config.py`：

```python
TARGETS = [
    {"name": "SNU OIA", ...},
    {"name": "SNU CBA", ...},
    # 添加新网站
    {
        "name": "新网站名称",
        "url": "网站地址",
        "selector": "CSS选择器",  # 使用snu_test.py测试
        "base_url": "基础URL"
    }
]
```

### 修改抓取数量

```python
MAX_ITEMS_PER_SITE = 20  # 改为抓取前20条公告
```

### 修改邮件内容

```python
EMAIL_SUBJECT = "🔔 SNU新公告提醒"
EMAIL_TEMPLATE = "亲爱的同学，发现以下新公告:\n\n{updates}"
```

### 修改重试设置

```python
MAX_RETRIES = 5        # 最多重试5次
RETRY_DELAY = 3        # 第一次重试等待3秒
REQUEST_TIMEOUT = 20   # 请求超时改为20秒
```

---

## 🛠️ 后期维护指南

### 维护场景1：网站改版，CSS选择器失效

**症状**：

```bash
运行 snu_test.py 输出：
❌ 未匹配到任何内容
提示：网站可能改版，请检查CSS选择器
```

**解决步骤**：

1. **打开网站**：在浏览器中访问目标网站
2. **检查元素**：
   - 按 F12 打开开发者工具
   - 点击选择器工具（左上角箭头图标）
   - 点击任意一条公告链接
   - 查看HTML结构
3. **找到新选择器**：
   ```html
   <!-- 旧结构（已失效） -->
   <td class="views-field-title">
       <a href="/notice/123">公告标题</a>
   </td>
   
   <!-- 新结构（需要更新） -->
   <div class="notice-item">
       <a class="notice-link" href="/notice/123">公告标题</a>
   </div>
   ```
4. **更新配置**：编辑 `snu_config.py`
   ```python
   TARGETS = [
       {
           "name": "SNU OIA (国际处)",
           "url": "https://oia.snu.ac.kr/notice-all",
           "selector": "div.notice-item a.notice-link",  # ← 更新这里
           "base_url": "https://oia.snu.ac.kr"
       }
   ]
   ```
5. **测试验证**：
   ```bash
   python snu_test.py
   ```
6. **确认成功**：看到"✓ 成功匹配到 X 条公告"

**预防措施**：

- 定期（每月）运行 `python snu_test.py` 检查
- 设置监控脚本，如果连续3天无新公告，可能是爬虫失效

---

### 维护场景2：邮件发送失败

**症状**：

```bash
❌ 邮件发送失败: (535, b'Login Fail...')
```

**可能原因**：

1. **QQ邮箱授权码过期**
2. **环境变量未设置**
3. **QQ邮箱开启了设备锁**

**解决步骤**：

**情况1：授权码过期**

1. 重新生成QQ邮箱授权码（见"快速开始"→"配置QQ邮箱"）
2. 更新环境变量：
   ```bash
   export SENDER_PASSWORD="新的授权码"
   ```

**情况2：环境变量未设置**

1. 检查环境变量：
   ```bash
   echo $SENDER_EMAIL
   echo $SENDER_PASSWORD
   echo $RECEIVER_EMAIL
   ```
2. 如果为空，重新设置（见"快速开始"→"设置环境变量"）

**情况3：设备锁**

1. 登录QQ邮箱网页版
2. 查看是否有"新设备登录"提示
3. 确认允许该设备登录

---

### 维护场景3：历史记录损坏

**症状**：

```bash
❌ 加载历史记录失败: JSONDecodeError
```

**解决方案**：

1. **备份损坏文件**：
   ```bash
   mv announcement_history.json announcement_history.json.bak
   ```

2. **删除并重建**：
   ```bash
   # 手动创建空历史文件
   echo '{}' > announcement_history.json
   
   # 或者删除后让程序自动创建
   rm announcement_history.json
   python snu_notifier_optimized.py
   ```

3. **首次运行不会发邮件**（因为当前所有公告都是"新的"）

**预防措施**：

- 定期备份 `announcement_history.json`：
  ```bash
  cp announcement_history.json announcement_history_backup_$(date +%Y%m%d).json
  ```

---

### 维护场景4：定时任务不运行

**症状**：设置了 cron，但没有收到邮件。

**检查步骤**：

1. **检查 cron 是否运行**：
   ```bash
   crontab -l  # 查看定时任务列表
   ```

2. **检查 cron 日志**：
   ```bash
   # macOS
   tail -f /var/log/system.log | grep cron
   
   # Linux
   tail -f /var/log/syslog | grep CRON
   ```

3. **检查环境变量**：
   
   cron 环境与终端环境不同，环境变量可能未加载！
   
   **解决方案**：在 crontab 中显式设置：
   ```bash
   crontab -e
   
   # 添加以下内容
   SENDER_EMAIL=your_email@qq.com
   SENDER_PASSWORD=你的授权码
   RECEIVER_EMAIL=receiver@example.com
   
   0 * * * * cd /path/to/SNU_Notice_Notifier && python3 snu_notifier_optimized.py
   ```

4. **检查路径**：
   
   使用绝对路径：
   ```bash
   # ❌ 错误（相对路径）
   0 * * * * python snu_notifier_optimized.py
   
   # ✅ 正确（绝对路径）
   0 * * * * cd /Users/xxx/Desktop/SNU_Notice_Notifier && /usr/bin/python3 snu_notifier_optimized.py
   ```

5. **测试执行**：
   ```bash
   # 手动执行 cron 命令测试
   cd /path/to/SNU_Notice_Notifier && python3 snu_notifier_optimized.py
   ```

---

### 维护场景5：添加新监控网站

**需求**：想监控SNU工学院的公告。

**步骤**：

1. **找到网站URL和选择器**：
   
   - 访问：https://eng.snu.ac.kr/notice
   - F12 查看公告链接的HTML结构
   - 确定CSS选择器，例如：`div.notice-list a.title`

2. **测试选择器**：
   
   创建临时测试脚本：
   ```python
   import requests
   from bs4 import BeautifulSoup
   
   url = "https://eng.snu.ac.kr/notice"
   response = requests.get(url)
   soup = BeautifulSoup(response.text, 'html.parser')
   items = soup.select("div.notice-list a.title")
   
   print(f"找到 {len(items)} 条公告")
   for i, item in enumerate(items[:3], 1):
       print(f"{i}. {item.get_text(strip=True)}")
   ```

3. **更新配置**：编辑 `snu_config.py`
   ```python
   TARGETS = [
       {"name": "SNU OIA (国际处)", ...},
       {"name": "SNU CBA (经营大学)", ...},
       # 添加新网站
       {
           "name": "SNU 工学院",
           "url": "https://eng.snu.ac.kr/notice",
           "selector": "div.notice-list a.title",
           "base_url": "https://eng.snu.ac.kr"
       }
   ]
   ```

4. **测试验证**：
   ```bash
   python snu_test.py
   ```

5. **运行干运行**：
   ```bash
   python snu_notifier_optimized.py --dry-run
   ```

---

### 维护场景6：日志文件过大

**症状**：`logs/snu_notifier.log` 文件几百MB。

**解决方案**：

**方案1：定期清理**

```bash
# 删除超过30天的日志
find logs/ -name "*.log" -mtime +30 -delete

# 或者只保留最新100行
tail -n 100 logs/snu_notifier.log > logs/snu_notifier.log.tmp
mv logs/snu_notifier.log.tmp logs/snu_notifier.log
```

**方案2：日志轮转**

安装 `logrotate`（Linux）或使用Python的 `RotatingFileHandler`：

编辑 `snu_notifier_optimized.py`：

```python
from logging.handlers import RotatingFileHandler

# 替换原有的日志配置
handler = RotatingFileHandler(
    Config.get_log_file(),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,          # 保留5个备份
    encoding='utf-8'
)
```

---

### 维护场景7：换用其他邮箱（Gmail/Outlook）

**Gmail 配置**：

1. **开启两步验证**
2. **生成应用专用密码**：https://myaccount.google.com/apppasswords
3. **更新配置**（`snu_config.py`）：
   ```python
   SMTP_SERVER = "smtp.gmail.com"
   SMTP_PORT = 587  # 或 465（SSL）
   ```
4. **更新环境变量**：
   ```bash
   export SENDER_EMAIL="your_gmail@gmail.com"
   export SENDER_PASSWORD="应用专用密码"
   ```

**Outlook/Hotmail 配置**：

```python
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587
```

---

## 💡 常见问题

### 1. 首次运行发送了大量邮件

**问题**：首次运行时，所有公告都是"新的"，发邮件数量很多。

**解决方案**：

- **方案1**：首次使用干运行模式
  ```bash
  python snu_notifier_optimized.py --dry-run
  ```
  
- **方案2**：首次运行后立即删除历史文件
  ```bash
  python snu_notifier_optimized.py  # 建立历史
  rm announcement_history.json      # 删除
  # 下次运行才会正常监控
  ```

### 2. 长时间无新公告

**可能原因**：
- 学校确实没发新公告
- 爬虫失效（网站改版）

**检查方法**：
```bash
python snu_test.py  # 测试爬虫功能
```

### 3. 网络不稳定导致频繁失败

**解决方案**：增加重试次数和超时时间

```python
# snu_config.py
MAX_RETRIES = 5        # 改为5次
REQUEST_TIMEOUT = 30   # 改为30秒
```

---

## 🎯 最佳实践

### 1. 设置合理的运行频率

**建议**：
- 学期初（申请季）：每2小时检查一次
- 平时：每天2次（早上10点、下午5点）
- 假期：每天1次或暂停

### 2. 邮件内容优化

**添加紧急标记**：

```python
# snu_config.py
if '紧急' in update['title'] or '截止' in update['title']:
    EMAIL_SUBJECT = "🚨【紧急】首尔大学官网重要公告！"
```

### 3. 多收件人

```python
# 修改 snu_notifier_optimized.py 第268-278行
RECEIVER_LIST = [
    Config.RECEIVER_EMAIL,
    "another_email@example.com"
]

server.sendmail(
    Config.SENDER_EMAIL,
    RECEIVER_LIST,  # 改为列表
    msg.as_string()
)
```

### 4. 数据备份

```bash
# 每周备份一次历史文件
0 0 * * 0 cp /path/to/announcement_history.json /path/to/backup/history_$(date +\%Y\%m\%d).json
```

---

## 📝 技术栈

| 技术 | 用途 |
|------|------|
| **requests** | HTTP 请求 |
| **BeautifulSoup4** | HTML 解析 |
| **smtplib** | 发送邮件 |
| **logging** | 日志记录 |
| **argparse** | 命令行参数 |
| **Python 3.7+** | 编程语言 |

---

## 🎓 项目特点

### 代码质量
- ✅ 模块化设计（配置与逻辑分离）
- ✅ 面向对象编程（`SNUNotifier` 类）
- ✅ 完善的错误处理
- ✅ 详细的日志记录
- ✅ 类型提示（Type Hints）
- ✅ 详细的文档字符串

### 安全性
- ✅ 环境变量保护敏感信息
- ✅ 启动时验证配置
- ✅ 不在代码中硬编码密码

### 可维护性
- ✅ 集中配置管理
- ✅ 清晰的代码结构
- ✅ 完整的测试脚本
- ✅ 详细的维护文档

---

## 🚨 法律声明

- ⚠️ 本项目仅供个人学习和使用
- ⚠️ 请遵守网站的 robots.txt 和服务条款
- ⚠️ 控制访问频率，不要给服务器造成压力
- ⚠️ 不要用于商业目的

---

**Happy Monitoring! 🎓📧**
