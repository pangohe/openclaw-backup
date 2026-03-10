#!/usr/bin/env python3
import os

session_file = '/root/.openclaw/agents/main/sessions/2ea5280b-42d0-4e90-8b4f-fe825603f3ef.jsonl'

# 读取所有行
with open(session_file, 'r') as f:
    lines = f.readlines()

original = len(lines)
original_size = os.path.getsize(session_file)

# 只保留最后 5 行
keep = 5
keep_lines = lines[-keep:]

# 备份
backup = session_file + '.bak2'
os.rename(session_file, backup)

# 写入
with open(session_file, 'w') as f:
    f.writelines(keep_lines)

new_size = os.path.getsize(session_file)

print(f"✅ 激进压缩完成!")
print(f"   行数: {original} → {keep}")
print(f"   大小: {original_size/1024:.1f}KB → {new_size/1024:.1f}KB")
print(f"   备份: {backup}")
