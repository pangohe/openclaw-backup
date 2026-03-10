#!/usr/bin/env python3
"""
统一的 Token 管理器
由 Dashboard Agent 统一管理所有通道的 token
"""
import json
from datetime import datetime
from pathlib import Path

class UnifiedTokenManager:
    """统一的 Token 管理 - Dashboard Agent 独享权限"""

    def __init__(self):
        self.monitoring_channels = {
            "dashboard": {"threshold": 25, "priority": "emergency", "keep": 5},
            "qqbot":     {"threshold": 35, "priority": "high",     "keep": 20},
            "telegram":  {"threshold": 35, "priority": "high",     "keep": 20},
            "feishu":    {"threshold": 30, "priority": "medium",   "keep": 30},
            "other":     {"threshold": 25, "priority": "low",      "keep": 20}
        }

    def check_all_channels(self):
        """检查所有通道 token 使用情况"""
        print("📊 检查所有通道 token 使用情况...")
        
        # 模拟数据（实际应该从 Token Watcher V3 获取）
        simulated_usage = {
            "dashboard": 4.5,
            "qqbot": 35.2,
            "telegram": 28.7,
            "feishu": 19.3
        }

        for channel, config in self.monitoring_channels.items():
            if channel not in simulated_usage:
                continue
                
            usage = simulated_usage[channel]["percent"] if isinstance(simulated_usage[channel], dict) else simulated_usage[channel]
            threshold = config["threshold"]
            priority = config["priority"]
            
            if usage > threshold:
                print(f"⚠️  {channel.upper()}: {usage}% > {threshold}% (阈值)")
                self.compress_channel(channel, priority, usage)
            else:
                print(f"✅ {channel.upper()}: {usage}% (正常)")

    def compress_channel(self, channel, priority, usage):
        """按优先级压缩通道"""
        config = self.monitoring_channels[channel]
        
        if priority == "emergency":
            keep = max(5, config["keep"] // 2)  # Dashboard: 最多5条
            print(f"🚨 应急通道 [{channel}] 激进压缩: {keep} 条")
        elif priority == "high" and usage > 70:
            keep = max(10, config["keep"] * 2 // 3)  # 降为2/3
            print(f"⚡ 高优先级通道 [{channel}] 激进压缩: {keep} 条")
        else:
            keep = config["keep"]
            print(f"📊 标准压缩 [{channel}]: {keep} 条")

        return {"channel": channel, "keep": keep, "priority": priority}

    def get_emergency_channel_status(self):
        """检查应急通道状态"""
        return {
            "channel": "dashboard",
            "status": "available",
            "token_usage": 4.5,
            "threshold": 25,
            "max_messages": 10
        }

if __name__ == "__main__":
    manager = UnifiedTokenManager()
    manager.check_all_channels()
    
    print("\n🚨 Dashboard 应急通道状态:")
    status = manager.get_emergency_channel_status()
    print(f"   状态: {status['status']}")
    print(f"   Token: {status['token_usage']}% / {status['threshold']}%")
    print(f"   最大消息: {status['max_messages']} 条")
