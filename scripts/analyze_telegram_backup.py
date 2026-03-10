#!/usr/bin/env python3
"""分析 Telegram 备份聊天记录并与当前系统对比去重"""
import json
import sys

def extract_messages(jsonl_path):
    """从 jsonl 文件提取用户消息"""
    messages = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                if data.get('type') == 'message':
                    msg = data.get('message', {})
                    if msg.get('role') == 'user':
                        content = ''
                        for item in msg.get('content', []):
                            if isinstance(item, dict) and item.get('type') == 'text':
                                content += item.get('text', '')
                        if content:
                            messages.append({
                                'timestamp': data.get('timestamp', ''),
                                'content': content[:500]  # 限制长度
                            })
            except:
                continue
    return messages

print("=" * 60)
print("备份文件分析")
print("=" * 60)

backup_path = '/tmp/backup-20260225/.openclaw/agents/main/sessions/e50d1e62-68c2-4e60-9aa1-2a4087a5a9a5.jsonl'
backup_msgs = extract_messages(backup_path)
print(f"\n备份文件：{len(backup_msgs)} 条用户消息")
print(f"时间范围：{backup_msgs[0]['timestamp'] if backup_msgs else 'N/A'} - {backup_msgs[-1]['timestamp'] if backup_msgs else 'N/A'}")

# 显示前 5 条和后 5 条
print("\n--- 前 5 条消息 ---")
for i, msg in enumerate(backup_msgs[:5], 1):
    print(f"{i}. [{msg['timestamp'][:10]}] {msg['content'][:100]}...")

print("\n--- 后 5 条消息 ---")
for i, msg in enumerate(backup_msgs[-5:], len(backup_msgs)-4):
    print(f"{i}. [{msg['timestamp'][:10]}] {msg['content'][:100]}...")

# 保存消息内容到文件供对比
with open('/root/.openclaw/workspace/data/backup_messages.txt', 'w', encoding='utf-8') as f:
    for msg in backup_msgs:
        f.write(f"{msg['timestamp']}|{msg['content']}\n")

print(f"\n✅ 消息列表已保存到 /root/.openclaw/workspace/data/backup_messages.txt")
