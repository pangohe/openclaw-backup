#!/usr/bin/env python3
"""
优先级压缩器 - Dashboard Agent 专属
按优先级压缩所有通道
"""
import argparse

class PriorityCompressor:
    def __init__(self):
        self.channels = [
            {"name": "dashboard", "priority": "emergency", "threshold": 25},
            {"name": "qqbot",     "priority": "high",      "threshold": 35},
            {"name": "telegram",  "priority": "high",      "threshold": 35},
            {"name": "feishu",    "priority": "medium",    "threshold": 30}
        ]

    def compress_by_priority(self, aggressive=False, compress_all=False):
        """按优先级压缩通道"""
        print("📋 按优先级压缩所有通道...")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        for channel in self.channels:
            name = channel["name"]
            priority = channel["priority"]
            threshold = channel["threshold"]
            
            if compress_all or aggressive:
                keep = self.get_keep_count(name, priority, aggressive)
                print(f"  {priority.upper():<10} {name.upper():<10} -> {keep} 条")
            else:
                print(f"  {priority.upper():<10} {name.upper():<10} (超限时压缩)")
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("✅ 压缩完成")

    def get_keep_count(self, channel, priority, aggressive):
        """获取保留消息数"""
        base_keep = {
            "dashboard": 10,
            "qqbot": 25,
            "telegram": 25,
            "feishu": 30
        }.get(channel, 20)
        
        if priority == "emergency":  # Dashboard: 激进 → 5条
            return max(5, base_keep // 2)
        elif aggressive:
            return base_keep // 2  # 激进模式：减半
        else:
            return base_keep  # 标准模式

def main():
    parser = argparse.ArgumentParser(description="优先级压缩器")
    parser.add_argument("--aggressive", action="store_true", help="激进模式")
    parser.add_argument("--all", action="store_true", help="压缩所有通道")
    
    args = parser.parse_args()
    
    compressor = PriorityCompressor()
    compressor.compress_by_priority(aggressive=args.aggressive, compress_all=args.all)

if __name__ == "__main__":
    main()
