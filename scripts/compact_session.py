#!/usr/bin/env python3
"""
快速压缩会话文件到指定行数
"""
import json
import os
import sys
from datetime import datetime

def compact_session(session_file, keep_lines=20):
    """压缩会话文件到指定行数"""
    if not os.path.exists(session_file):
        print(f"❌ 文件不存在: {session_file}")
        return

    # 读取所有行
    with open(session_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    original_lines = len(lines)
    original_size = os.path.getsize(session_file)

    if original_lines <= keep_lines:
        print(f"✅ {session_file}: {original_lines} 行，无需压缩")
        return

    # 保留最后 N 行
    keep_lines_data = lines[-keep_lines:]

    # 备份原文件
    backup_file = session_file + '.bak'
    os.rename(session_file, backup_file)

    # 写入压缩后的数据
    with open(session_file, 'w', encoding='utf-8') as f:
        f.writelines(keep_lines_data)

    new_size = os.path.getsize(session_file)
    saved_bytes = original_size - new_size
    saved_percent = (saved_bytes / original_size) * 100

    print(f"✅ 已压缩: {os.path.basename(session_file)}")
    print(f"   行数: {original_lines} → {keep_lines} (保留率 {keep_lines/original_lines*100:.1f}%)")
    print(f"   大小: {original_size/1024:.1f}KB → {new_size/1024:.1f}KB (节省 {saved_percent:.1f}%)")
    print(f"   备份: {backup_file}")

if __name__ == '__main__':
    # 检查所有大的会话文件
    sessions_dir = '/root/.openclaw/agents/main/sessions'

    # 按大小排序
    session_files = []
    for f in os.listdir(sessions_dir):
        if f.endswith('.jsonl'):
            file_path = os.path.join(sessions_dir, f)
            size = os.path.getsize(file_path)
            session_files.append((file_path, size))

    # 排序并压缩超过 50KB 的文件
    session_files.sort(key=lambda x: x[1], reverse=True)

    print("🔍 扫描会话文件...")
    for file_path, size in session_files:
        if size > 50 * 1024:  # 大于 50KB
            print(f"\n📦 {os.path.basename(file_path)}: {size/1024:.1f}KB")
            compact_session(file_path, keep_lines=20)

    print("\n✅ 压缩完成！")
