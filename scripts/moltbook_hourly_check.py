#!/usr/bin/env python3
"""
Moltbook Hourly Check - 每小时检查Moltbook社区动态
合并功能：学习 + 发现 + agent状态
频率：每小时
"""
import json
import requests
from datetime import datetime
from pathlib import Path

# API配置
MOLTBOOK_API_KEY = "moltbook_sk_zZeDMmpICk0b9honi3FT3XA53g5JmvVc"
MOLTBOOK_FEED_URL = "https://www.moltbook.com/api/v1/feed?sort=new&limit=10"

# 数据目录
DATA_DIR = Path.home() / ".openclaw" / "workspace" / "data" / "moltbook"
STATE_FILE = DATA_DIR / "hourly_check_state.json"
LOG_FILE = DATA_DIR / "hourly_check_log.json"

# Agent信息
AGENT_USERNAME = "leslieassistant"
AGENT_ID = "751fd1bf-7d57-43b1-8f77-619a0edc07a1"

# 感兴趣的关键词
KEYWORDS = [
    "agent", "ai", "bot", "赚钱", "business", "startup", "自动化",
    "trading", "arbitrage", "strategies", "success", "case study",
    "python", "script", "automation", "workflow", "integration"
]
MIN_UPVOTES = 3

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def load_state():
    """加载状态"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "last_check": None,
            "check_count": 0,
            "discoveries": []
        }

def save_state(state):
    """保存状态"""
    state["last_check"] = datetime.now().isoformat()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

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
            status = response.json()
            log(f"✅ Agent状态: 已认领")
            return status
        else:
            log(f"⚠️  Agent状态: 未认领")
            return None

    except Exception as e:
        log(f"❌ 检查agent状态失败: {e}")
        return None

def analyze_feed(feed):
    """分析feed"""
    discoveries = []
    learning_opportunities = []

    if not feed:
        return [], []

    # API返回格式: {"success": true, "posts": [...]}
    posts = feed.get("posts", []) if isinstance(feed, dict) else feed
    if not posts:
        return [], []

    for item in posts:
        # 兼容不同的API响应格式
        if isinstance(item, str):
            # 如果是字符串格式，跳过
            continue

        author_obj = item.get("author", {})
        if isinstance(author_obj, str):
            # 如果author是字符串
            author = author_obj
        elif isinstance(author_obj, dict):
            # 如果author是对象
            author = author_obj.get("displayName", author_obj.get("name", "Unknown"))
        else:
            author = "Unknown"

        upvotes = item.get("upvotes", 0)
        content = item.get("content", "")

        # 只处理有upvotes的内容
        if upvotes < MIN_UPVOTES:
            continue

        content_lower = content.lower()
        has_keyword = any(keyword in content_lower for keyword in KEYWORDS)

        # 高价值内容
        if upvotes >= 10:
            discoveries.append({
                "author": author,
                "upvotes": upvotes,
                "content": content[:300],
                "url": item.get("url", ""),
                "timestamp": item.get("createdAt", ""),
                "discovered_at": datetime.now().isoformat()
            })

        # 学习机会
        elif has_keyword and author != AGENT_USERNAME:
            learning_opportunities.append({
                "author": author,
                "upvotes": upvotes,
                "content": content[:200],
                "tags": [k for k in KEYWORDS if k in content_lower],
                "timestamp": item.get("createdAt", "")
            })

    return discoveries, learning_opportunities

def save_log(discoveries, learning_opportunities):
    """保存检查日志"""
    log_entry = {
        "check_time": datetime.now().isoformat(),
        "feed_count": len(discoveries) + len(learning_opportunities),
        "discoveries": discoveries,
        "learning_opportunities": learning_opportunities
    }

    try:
        logs = []
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)

        logs.append(log_entry)

        # 只保留最近168条（一周）
        if len(logs) > 168:
            logs = logs[-168:]

        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)

        log(f"✅ 日志已保存 (共 {len(logs)} 条检查记录)")

    except Exception as e:
        log(f"❌ 保存日志失败: {e}")

def update_memory_summary(state, discoveries, learning):
    """更新memory中的总结"""
    # 如果有高价值发现，记录到memory
    if discoveries:
        recent = state["discoveries"]
        for d in discoveries:
            recent.append({
                "time": d["discovered_at"],
                "author": d["author"],
                "upvotes": d["upvotes"],
                "summary": d["content"][:100]
            })

        # 只保留最近50个
        if len(recent) > 50:
            state["discoveries"] = recent[-50:]

    return state

def main():
    """主函数"""
    log("🔍 Moltbook Hourly Check 开始运行...")

    # 创建目录
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 加载状态
    state = load_state()
    state["check_count"] += 1

    # 检查agent状态
    agent_status = check_agent_status()

    # 获取feed
    feed = fetch_moltbook_feed()

    if feed:
        # 分析
        discoveries, learning = analyze_feed(feed)

        # 保存日志
        save_log(discoveries, learning)

        # 更新memory
        state = update_memory_summary(state, discoveries, learning)

        # 输出结果
        if discoveries:
            log(f"🎯 发现 {len(discoveries)} 个高价值内容")
            for item in discoveries[:2]:
                log(f"   - {item['author']} ({item['upvotes']}赞): {item['content'][:80]}...")

        if learning:
            log(f"📚 学习机会: {len(learning)} 个")

        log(f"✅ Feed分析完成")

    else:
        log("❌ 没有获取到feed")

    # 保存状态
    save_state(state)

    log(f"✅ 检查完成 (第 {state['check_count']} 次)")

if __name__ == "__main__":
    main()
