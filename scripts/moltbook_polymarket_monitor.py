#!/usr/bin/env python3
"""
Polymarket Monitor - 每30分钟监控Polymarket套利机会
监控频率：每30分钟
"""
import json
import requests
from datetime import datetime
from pathlib import Path

# API配置
MOLTBOOK_API_KEY = "moltbook_sk_zZeDMmpICk0b9honi3FT3XA53g5JmvVc"
MOLTBOOK_FEED_URL = "https://www.moltbook.com/api/v1/feed?sort=new&limit=50"

# 数据目录
DATA_DIR = Path.home() / ".openclaw" / "workspace" / "data" / "polymarket"
LOG_FILE = DATA_DIR / "monitor_log.json"

# 关键词 - 更专注于Polymarket交易相关内容
KEYWORDS = [
    "arbitrage",      # 套利
    "gap",            # 缺口
    "position",       # 头寸
    "leverage",       # 杠杆
    "odds",           # 赔率/概率
    "polymarket",     # Polymarket平台
    "market making",  # 做市
    "slippage",       # 滑点
    "liquidity",      # 流动性
    "spread",         # 价差
    "volatility",     # 波动性
    "hedging",        # 对冲
]
MIN_UPVOTES = 5

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def fetch_moltbook_feed():
    """获取Moltbook feed"""
    try:
        headers = {
            "Authorization": f"Bearer {MOLTBOOK_API_KEY}"
        }
        response = requests.get(MOLTBOOK_FEED_URL, headers=headers, timeout=15)

        if response.status_code == 200:
            return response.json()
        else:
            log(f"❌ Moltbook API错误: {response.status_code}")
            return None

    except Exception as e:
        log(f"❌ 获取Moltbook feed失败: {e}")
        return None

def analyze_feed(feed):
    """分析feed，找出有价值的内容"""
    valuable = []

    if not feed:
        return []

    # Feed是一个dict，从'posts'键获取实际帖子列表
    posts = feed.get("posts", [])

    for item in posts:
        # 确保item是字典
        if not isinstance(item, dict):
            continue

        # 检查upvotes
        upvotes = item.get("upvotes", 0)
        if upvotes < MIN_UPVOTES:
            continue

        # 检查内容（处理None值）
        content = (item.get("content") or "").lower()
        title = (item.get("title") or "").lower()
        combined_text = content + " " + title

        if not combined_text.strip():
            continue

        # 检查关键词
        has_keyword = any(keyword in combined_text for keyword in KEYWORDS)

        if has_keyword:
            # 获取作者名（使用name而不是displayName）
            author_info = item.get("author", {})
            if isinstance(author_info, dict):
                author = author_info.get("name", "Unknown")
            else:
                author = "Unknown"

            valuable.append({
                "author": author,
                "upvotes": upvotes,
                "title": item.get("title", "")[:200],  # 限制标题长度
                "content": content[:500],  # 限制内容长度
                "url": item.get("url", ""),
                "timestamp": item.get("created_at", ""),
                "discovered_at": datetime.now().isoformat()
            })

    return valuable

def save_log(valuable_items):
    """保存监控日志"""
    log_entry = {
        "check_time": datetime.now().isoformat(),
        "total_items": len(valuable_items),
        "items": valuable_items
    }

    try:
        logs = []
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)

        logs.append(log_entry)

        # 只保留最近100条
        if len(logs) > 100:
            logs = logs[-100:]

        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)

        log(f"✅ 日志已保存 (共 {len(logs)} 条)")

    except Exception as e:
        log(f"❌ 保存日志失败: {e}")

def check_agent_status():
    """检查agent状态"""
    try:
        headers = {
            "Authorization": f"Bearer {MOLTBOOK_API_KEY}"
        }
        response = requests.get(
            "https://www.moltbook.com/api/v1/agents/status",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except Exception as e:
        log(f"❌ 检查agent状态失败: {e}")
        return None

def main():
    """主函数"""
    log("🔍 Polymarket Monitor 开始运行...")

    # 创建目录
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 检查agent状态
    agent_status = check_agent_status()
    if agent_status:
        log(f"✅ Agent状态: {agent_status}")

    # 获取feed
    feed = fetch_moltbook_feed()

    if feed:
        # 分析
        valuable_items = analyze_feed(feed)

        # 保存日志
        save_log(valuable_items)

        if valuable_items:
            log(f"🎯 发现 {len(valuable_items)} 个有价值内容")
            for item in valuable_items[:3]:  # 显示前3个
                log(f"   - {item['author']} ({item['upvotes']}赞): {item['content'][:100]}...")
        else:
            log("ℹ️  没有发现有价值内容")

    else:
        log("❌ 没有获取到feed")

    log("✅ 监控完成")

if __name__ == "__main__":
    main()
