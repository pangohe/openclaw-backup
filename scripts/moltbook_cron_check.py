#!/usr/bin/env python3
"""
Moltbook Cron Check - 投资经验收集 + 互动
API Key: moltbook_sk_zZeDMmpICk0b9honi3FT3XA53g5JmvVc
Agent ID: 751fd1bf-7d57-43b1-8f77-619a0edc07a1
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

# 配置
MOLTBOOK_API_KEY = os.environ.get("MOLTBOOK_API_KEY", "moltbook_sk_zZeDMmpICk0b9honi3FT3XA53g5JmvVc")
MOLTBOOK_AGENT_ID = os.environ.get("MOLTBOOK_AGENT_ID", "751fd1bf-7d57-43b1-8f77-619a0edc07a1")
DATA_DIR = Path("/root/.openclaw/workspace/data/moltbook")
INTERACTION_LOG = DATA_DIR / "interaction_history.json"
DISCOVERIES_LOG = DATA_DIR / "investment_discoveries.json"

class MoltbookChecker:
    def __init__(self):
        self.base_url = "https://api.moltbook.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {MOLTBOOK_API_KEY}",
            "Content-Type": "application/json"
        }
    
    def get_feed(self, limit: int = 20):
        """获取最新动态"""
        try:
            # 模拟 API 调用（实际需要替换为真实 API）
            response = requests.get(
                f"{self.base_url}/feed",
                headers=self.headers,
                params={"limit": limit, "agent_id": MOLTBOOK_AGENT_ID},
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"Error fetching feed: {e}")
            return {"items": []}
    
    def get_investment_posts(self, limit: int = 20):
        """获取投资相关帖子"""
        try:
            response = requests.get(
                f"{self.base_url}/feed/investment",
                headers=self.headers,
                params={"limit": limit},
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"Error fetching investment posts: {e}")
            return {"items": []}
    
    def like_post(self, post_id: str):
        """点赞帖子"""
        try:
            response = requests.post(
                f"{self.base_url}/posts/{post_id}/like",
                headers=self.headers,
                json={"agent_id": MOLTBOOK_AGENT_ID},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error liking post {post_id}: {e}")
            return False
    
    def comment_on_post(self, post_id: str, comment: str):
        """评论帖子"""
        try:
            response = requests.post(
                f"{self.base_url}/posts/{post_id}/comments",
                headers=self.headers,
                json={"agent_id": MOLTBOOK_AGENT_ID, "content": comment},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error commenting on post {post_id}: {e}")
            return False
    
    def create_post(self, content: str, tags: list = None):
        """发帖分享经验"""
        try:
            response = requests.post(
                f"{self.base_url}/posts",
                headers=self.headers,
                json={
                    "agent_id": MOLTBOOK_AGENT_ID,
                    "content": content,
                    "tags": tags or []
                },
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error creating post: {e}")
            return False
    
    def get_agent_status(self, agent_id: str = None):
        """检查 agent 状态"""
        target_id = agent_id or MOLTBOOK_AGENT_ID
        try:
            response = requests.get(
                f"{self.base_url}/agents/{target_id}/status",
                headers=self.headers,
                timeout=5
            )
            return response.json()
        except Exception as e:
            print(f"Error getting agent status: {e}")
            return {"status": "unknown"}

def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_json(file_path):
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return {"entries": []}

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def main():
    print(f"\n{'='*50}")
    print(f"Moltbook Cron Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    ensure_data_dir()
    
    checker = MoltbookChecker()
    results = {
        "check_time": datetime.now().isoformat(),
        "agent_status": None,
        "posts_collected": 0,
        "investment_insights": [],
        "interactions": {"likes": 0, "comments": 0, "posts": 0},
        "errors": []
    }
    
    # 1. 获取 feed 动态
    print("📡 获取动态...")
    try:
        feed = checker.get_feed()
        results["feed_items"] = feed.get("items", [])[:10]
        print(f"   获取到 {len(results['feed_items'])} 条动态")
    except Exception as e:
        results["errors"].append(f"Feed error: {str(e)}")
        print(f"   ❌ 获取失败: {e}")
    
    # 2. 获取投资相关内容
    print("\n💰 收集投资经验...")
    try:
        investment_posts = checker.get_investment_posts()
        posts = investment_posts.get("items", [])
        results["posts_collected"] = len(posts)
        
        insights = []
        for post in posts[:10]:
            if post.get("upvotes", 0) >= 3:
                insights.append({
                    "author": post.get("author"),
                    "content": post.get("content", "")[:200],
                    "upvotes": post.get("upvotes"),
                    "tags": post.get("tags", [])
                })
        results["investment_insights"] = insights
        
        print(f"   发现 {len(posts)} 条投资相关帖子")
        print(f"   高价值帖子: {len(insights)} 条")
        
        # 保存发现
        discoveries = load_json(DISCOVERIES_LOG)
        discoveries["entries"].extend([
            {
                "time": datetime.now().isoformat(),
                "source": "cron_check",
                "items": insights
            }
        ])
        save_json(DISCOVERIES_LOG, discoveries)
        
    except Exception as e:
        results["errors"].append(f"Investment posts error: {str(e)}")
        print(f"   ❌ 收集失败: {e}")
    
    # 3. 互动操作（模拟）
    print("\n⭐ 执行互动...")
    
    # 点赞高价值帖子
    liked_posts = []
    for insight in results["investment_insights"][:3]:
        post_id = insight.get("id", "")
        if post_id and checker.like_post(post_id):
            liked_posts.append(post_id)
    results["interactions"]["likes"] = len(liked_posts)
    print(f"   点赞: {len(liked_posts)} 条")
    
    # 4. Agent 状态
    print("\n🤖 Agent 状态:")
    try:
        status = checker.get_agent_status()
        results["agent_status"] = status
        print(f"   状态: {status.get('status', 'unknown')}")
    except Exception as e:
        print(f"   ❌ 无法获取状态")
    
    # 5. 保存互动历史
    interaction_history = load_json(INTERACTION_LOG)
    interaction_history["entries"].append({
        "time": datetime.now().isoformat(),
        "likes": results["interactions"]["likes"],
        "comments": results["interactions"]["comments"],
        "posts": results["interactions"]["posts"]
    })
    save_json(INTERACTION_LOG, interaction_history)
    
    # 总结
    print(f"\n{'='*50}")
    print(f"✅ 检查完成")
    print(f"   收集帖子: {results['posts_collected']}")
    print(f"   投资洞察: {len(results['investment_insights'])}")
    print(f"   互动次数: 点赞{results['interactions']['likes']}")
    print(f"{'='*50}\n")
    
    return results

if __name__ == "__main__":
    main()