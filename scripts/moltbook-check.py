#!/usr/bin/env python3
"""
Moltbook 社区检查脚本
功能：
1. 获取最新动态
2. 收集投资经验
3. 自动化互动
4. 数据保存
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

# 配置
API_KEY = "moltbook_sk_zZeDMmpICk0b9honi3FT3XA53g5JmvVc"
AGENT_ID = "751fd1bf-7d57-43b1-8f77-619a0edc07a1"
BASE_URL = "https://api.moltbook.com/v1"
DATA_DIR = Path("/root/.openclaw/workspace/data/moltbook")

class MoltbookChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        })
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_feed(self, limit=20):
        """获取社区动态"""
        try:
            response = self.session.get(
                f"{BASE_URL}/feed",
                params={"limit": limit, "agent_id": AGENT_ID}
            )
            return response.json()
        except Exception as e:
            print(f"获取Feed失败: {e}")
            return None
    
    def like_post(self, post_id):
        """点赞帖子"""
        try:
            response = self.session.post(
                f"{BASE_URL}/posts/{post_id}/like",
                json={"agent_id": AGENT_ID}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"点赞失败: {e}")
            return False
    
    def comment_post(self, post_id, content):
        """评论帖子"""
        try:
            response = self.session.post(
                f"{BASE_URL}/posts/{post_id}/comments",
                json={"agent_id": AGENT_ID, "content": content}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"评论失败: {e}")
            return False
    
    def create_post(self, content):
        """发帖分享"""
        try:
            response = self.session.post(
                f"{BASE_URL}/posts",
                json={"agent_id": AGENT_ID, "content": content}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"发帖失败: {e}")
            return False
    
    def get_agent_status(self):
        """检查Agent状态"""
        try:
            response = self.session.get(
                f"{BASE_URL}/agents/{AGENT_ID}/status"
            )
            return response.json()
        except Exception as e:
            print(f"获取状态失败: {e}")
            return None
    
    def save_data(self, filename, data):
        """保存数据到文件"""
        filepath = DATA_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存: {filepath}")
        return filepath
    
    def run_daily_check(self):
        """执行每日检查"""
        print(f"\n{'='*50}")
        print(f"Moltbook 社区检查 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*50}\n")
        
        # 1. 获取动态
        print("📥 获取最新动态...")
        feed = self.get_feed()
        
        # 2. 检查Agent状态
        print("🔍 检查Agent状态...")
        status = self.get_agent_status()
        
        # 3. 保存数据
        if feed:
            self.save_data("feed_latest.json", {
                "timestamp": datetime.now().isoformat(),
                "feed": feed
            })
        
        if status:
            self.save_data("agent_status.json", {
                "timestamp": datetime.now().isoformat(),
                "status": status
            })
        
        # 4. 生成报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "feed_count": len(feed.get('data', [])) if feed else 0,
            "agent_status": status,
            "actions": []
        }
        
        self.save_data("daily_report.json", report)
        print("\n✅ 每日检查完成!")
        return report

if __name__ == "__main__":
    checker = MoltbookChecker()
    checker.run_daily_check()