#!/usr/bin/env python3
"""对比 Telegram 备份与当前系统，生成去重报告"""
import json
import os

def extract_messages(jsonl_path):
    """从 jsonl 文件提取用户消息"""
    messages = []
    if not os.path.exists(jsonl_path):
        return messages
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
                        if content and len(content.strip()) > 10:  # 忽略太短的消息
                            messages.append({
                                'timestamp': data.get('timestamp', ''),
                                'content': content.strip()
                            })
            except:
                continue
    return messages

def get_message_hash(msg):
    """生成消息的唯一标识（基于内容）"""
    return hash(msg['content'][:200])

print("=" * 70)
print("Telegram 聊天记录对比报告")
print("=" * 70)

# 备份文件
backup_path = '/tmp/backup-20260225/.openclaw/agents/main/sessions/e50d1e62-68c2-4e60-9aa1-2a4087a5a9a5.jsonl'
backup_msgs = extract_messages(backup_path)

# 当前系统文件
current_paths = [
    '/root/.openclaw/agents/main/sessions/1d0786db-45d8-4e62-9966-a63d7b551dc0.jsonl',
    '/root/.openclaw/agents/main/sessions/2ea5280b-42d0-4e90-8b4f-fe825603f3ef.jsonl'
]
current_msgs = []
for path in current_paths:
    current_msgs.extend(extract_messages(path))

print(f"\n📊 统计:")
print(f"   备份文件消息数：{len(backup_msgs)} 条")
print(f"   当前系统消息数：{len(current_msgs)} 条")

# 去重对比
current_hashes = {get_message_hash(msg) for msg in current_msgs}
new_messages = []
duplicate_count = 0

for msg in backup_msgs:
    msg_hash = get_message_hash(msg)
    if msg_hash in current_hashes:
        duplicate_count += 1
    else:
        new_messages.append(msg)
        current_hashes.add(msg_hash)

print(f"\n📈 对比结果:")
print(f"   重复消息：{duplicate_count} 条")
print(f"   新增消息：{len(new_messages)} 条")

if new_messages:
    print(f"\n📋 新增消息预览 (前 20 条):")
    print("-" * 70)
    for i, msg in enumerate(new_messages[:20], 1):
        ts = msg['timestamp'][:10] if msg['timestamp'] else 'N/A'
        content = msg['content'][:80].replace('\n', ' ')
        print(f"{i:2}. [{ts}] {content}...")
    
    if len(new_messages) > 20:
        print(f"\n   ... 还有 {len(new_messages) - 20} 条消息")
    
    # 保存新消息到文件
    with open('/root/.openclaw/workspace/data/telegram_new_messages.json', 'w', encoding='utf-8') as f:
        json.dump(new_messages, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完整新消息列表已保存到:")
    print(f"   /root/.openclaw/workspace/data/telegram_new_messages.json")
else:
    print(f"\n✅ 没有新消息需要导入")

print("\n" + "=" * 70)
