import feedparser
import json
import os
from datetime import datetime
import translators as ts
import requests

# ================== 配置区 ==================
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")  # 从GitHub Secrets读取

# 你关注的X账号RSS列表（替换成你自己的）
RSS_FEEDS = {
    "Andrej Karpathy": "https://rss.app/feeds/a9lJPdAKebaicrbk.xml",   # ← 替换成实际RSS
    "Bill Ackman": "https://rss.app/feeds/DajF9ntMOk0t95QQ.xml",
    # 继续添加更多账号...
}

# 翻译引擎（中国用户推荐 youdao 或 baidu，免费额度够用）
TRANSLATOR = "baidu"   # 可选: youdao, baidu, google, bing 等  
翻译 = "goo"  # 可选： youdao， baidu， google， bing 等

DATA_FILE = "last_seen.json"
# ============================================
FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true

# 加载上次抓取记录
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        last_seen = json.load(f)
else:
    last_seen = {}

messages = []

for username, rss_url in RSS_FEEDS.items():
    feed = feedparser.parse(rss_url)
    new_posts = []
    
    for entry in feed.entries:
        entry_id = entry.id if hasattr(entry, "id") else entry.link
        if username not in last_seen or entry_id != last_seen[username]:
            # 翻译成中文
            # 翻译成中文（临时关闭翻译，先测试能否推送）
            translated = (entry.title + "\n\n" + entry.description)[:500] + "\n\n（翻译功能已临时关闭，成功后可重新开启）"
            # 翻译失败就用原文
            
            post_time = entry.published if hasattr(entry, "published") else "未知时间"
            
            new_posts.append(f"**@{username}**  {post_time}\n\n{translated}\n\n原文链接：{entry.link}\n---")
            last_seen[username] = entry_id  # 更新最后一条
    
    if new_posts:
        messages.extend(new_posts)

# 如果有新内容，发送推送
if messages:
    content = "\n\n".join(messages)
    title = f"X每日精选 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    url = f"https://www.pushplus.plus/send?token={PUSHPLUS_TOKEN}&title={title}&content={content}&template=markdown"
    requests.get(url)
    print(f"✅ 已推送 {len(messages)} 条新内容")
else:
    print("🟡 今天没有新内容")

# 保存抓取记录
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(last_seen, f, ensure_ascii=False, indent=2)
