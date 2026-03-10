#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话自动分类脚本
自动分析并分类所有会话文件
"""

import json
import os
from pathlib import Path
from datetime import datetime

SESSIONS_DIR = Path("/root/.openclaw/agents/main/sessions")
WORKSPACE = Path("/root/.openclaw/workspace")

def load_session_metadata(session_id):
    """加载会话的元数据"""
    # 尝试从 workspace 的 jsonl 文件获取信息
    jsonl_path = WORKSPACE / f"{session_id}.jsonl"
    if not jsonl_path.exists():
        jsonl_path = SESSIONS_DIR / f"{session_id}.jsonl"
    
    if not jsonl_path.exists():
        return None
    
    try:
        # 读取第一行获取基本信息
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if first_line.strip():
                data = json.loads(first_line)
                return data
    except Exception as e:
        return None
    
    return None

def classify_session(session_id, metadata):
    """分类单个会话"""
    classification = {
        'session_id': session_id,
        'type': 'unknown',
        'channel': 'unknown',
        'created_at': None,
        'message_count': 0,
        'size_kb': 0,
        'description': ''
    }
    
    jsonl_path = WORKSPACE / f"{session_id}.jsonl"
    if not jsonl_path.exists():
        jsonl_path = SESSIONS_DIR / f"{session_id}.jsonl"
    
    if not jsonl_path.exists():
        return classification
    
    # 获取文件大小
    classification['size_kb'] = round(jsonl_path.stat().st_size / 1024, 2)
    
    # 统计消息数量
    message_count = 0
    first_timestamp = None
    last_timestamp = None
    channels = set()
    roles = {'user': 0, 'assistant': 0, 'system': 0}
    
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        message_count += 1
                        
                        # 获取时间戳
                        ts = data.get('timestamp')
                        if ts:
                            if not first_timestamp:
                                first_timestamp = ts
                            last_timestamp = ts
                        
                        # 获取角色
                        role = data.get('role', 'unknown')
                        if role in roles:
                            roles[role] += 1
                        
                        # 获取渠道信息
                        if role == 'user':
                            content = data.get('content', [])
                            if isinstance(content, list):
                                for item in content:
                                    if item.get('type') == 'text':
                                        text = item.get('text', '')
                                        if 'qqbot' in text.lower():
                                            channels.add('qqbot')
                                        elif 'telegram' in text.lower():
                                            channels.add('telegram')
                                        elif 'feishu' in text.lower():
                                            channels.add('feishu')
                    except:
                        continue
    except Exception as e:
        pass
    
    classification['message_count'] = message_count
    classification['created_at'] = first_timestamp
    classification['last_activity'] = last_timestamp
    classification['channels_detected'] = list(channels)
    classification['role_distribution'] = roles
    
    # 根据 session_id 前缀和元数据分类
    if 'cron' in session_id.lower():
        classification['type'] = 'cron_task'
        classification['description'] = '定时任务会话'
    elif message_count == 0:
        classification['type'] = 'empty'
        classification['description'] = '空会话'
    elif message_count < 5:
        classification['type'] = 'minimal'
        classification['description'] = '极少消息会话'
    elif roles['assistant'] > roles['user'] * 2:
        classification['type'] = 'assistant_heavy'
        classification['description'] = '助手主导会话'
    else:
        classification['type'] = 'normal'
        classification['description'] = '正常对话会话'
    
    # 根据渠道分类
    if channels:
        classification['channel'] = channels[0] if len(channels) == 1 else 'multi'
    
    # 根据时间分类（30 天为界）
    if last_timestamp:
        # 确保时间戳是数字
        try:
            last_ts = float(last_timestamp) if not isinstance(last_timestamp, (int, float)) else last_timestamp
            days_ago = (datetime.now().timestamp() * 1000 - last_ts) / (1000 * 60 * 60 * 24)
            if days_ago > 30:
                classification['age_category'] = 'old'
                classification['description'] += ' (超过 30 天)'
            elif days_ago > 7:
                classification['age_category'] = 'recent'
            else:
                classification['age_category'] = 'active'
                classification['description'] += ' (活跃)'
        except:
            classification['age_category'] = 'unknown'
    
    return classification

def main():
    print("🔍 开始会话自动分类...\n")
    
    # 获取所有会话文件
    session_files = list(SESSIONS_DIR.glob("*.jsonl"))
    
    if not session_files:
        print("❌ 未找到会话文件")
        return
    
    print(f"📊 找到 {len(session_files)} 个会话文件\n")
    
    # 分类所有会话
    classifications = []
    type_stats = {}
    channel_stats = {}
    age_stats = {}
    
    for session_file in session_files:
        session_id = session_file.stem
        metadata = load_session_metadata(session_id)
        classification = classify_session(session_id, metadata)
        classifications.append(classification)
        
        # 统计
        type_stats[classification['type']] = type_stats.get(classification['type'], 0) + 1
        channel_stats[classification['channel']] = channel_stats.get(classification['channel'], 0) + 1
        age_stats[classification.get('age_category', 'unknown')] = age_stats.get(classification.get('age_category', 'unknown'), 0) + 1
    
    # 输出统计
    print("=" * 60)
    print("📈 会话分类统计")
    print("=" * 60)
    
    print(f"\n📁 总会话数：{len(classifications)}")
    
    print(f"\n🏷️ 按类型分类:")
    for type_name, count in sorted(type_stats.items(), key=lambda x: -x[1]):
        print(f"  - {type_name}: {count} 个")
    
    print(f"\n📱 按渠道分类:")
    for channel, count in sorted(channel_stats.items(), key=lambda x: -x[1]):
        print(f"  - {channel}: {count} 个")
    
    print(f"\n⏰ 按活跃度分类:")
    for age, count in sorted(age_stats.items(), key=lambda x: -x[1]):
        print(f"  - {age}: {count} 个")
    
    # 计算总大小
    total_size = sum(c['size_kb'] for c in classifications)
    print(f"\n💾 总存储空间：{total_size:.2f} KB ({total_size/1024:.2f} MB)")
    
    # 保存分类结果
    output_path = WORKSPACE / "data" / "session_classifications.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_sessions': len(classifications),
            'statistics': {
                'by_type': type_stats,
                'by_channel': channel_stats,
                'by_age': age_stats,
                'total_size_kb': total_size
            },
            'classifications': classifications
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 分类结果已保存至：{output_path}")
    
    # 显示最大的 10 个会话
    print(f"\n📦 最大的 10 个会话:")
    sorted_by_size = sorted(classifications, key=lambda x: -x['size_kb'])[:10]
    for i, session in enumerate(sorted_by_size, 1):
        print(f"  {i}. {session['session_id'][:8]}... - {session['size_kb']:.2f} KB ({session['message_count']} 条消息)")
    
    print("\n" + "=" * 60)
    print("✅ 会话分类完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
