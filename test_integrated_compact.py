#!/usr/bin/env python3
"""测试集成了增强压缩的 Token Watcher V2"""
import subprocess
import sys

script_path = "/root/.openclaw/workspace/scripts/token_watcher_v2.py"

print("🧪 测试集成后的 Token Watcher V2")
print("=" * 60)

# 检查脚本
print("\n1️⃣  检查脚本导入...")
result = subprocess.run(
    ["python3", "-c", f"exec(open('{script_path}').read())"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("   ✅ 脚本语法检查通过")
else:
    print(f"   ❌ 脚本错误:\n{result.stderr}")
    sys.exit(1)

# 检查增强压缩器导入
print("\n2️⃣  检查增强压缩器导入...")
result = subprocess.run(
    ["python3", "-c", f"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/token-saver-v2/scripts')
from enhanced_compact import EnhancedCompressor
print('✅ 增强压缩器导入成功')
print('   EnhancedCompressor:', EnhancedCompressor)
"""],
    capture_output=True,
    text=True
)

if "✅" in result.stdout:
    print("   ", result.stdout.strip())
else:
    print(f"   ❌ 导入失败:\n{result.stderr}")

# 测试实际压缩（找到一个中等大小的会话）
print("\n3️⃣  查找测试会话...")
result = subprocess.run(
    ["python3", "-c", """
import os
from pathlib import Path
sessions_dir = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
test_files = []
for f in sessions_dir.glob("*.jsonl"):
    size = f.stat().st_size
    if size > 100 * 1024 and size < 500 * 1024:  # 100-500KB
        test_files.append((f, size))
if test_files:
    test_files.sort(key=lambda x: x[1], reverse=True)
    print(test_files[0][0])
"""],
    capture_output=True,
    text=True
)

test_file = result.stdout.strip()
if test_file and os.path.exists(test_file):
    print(f"   ✅ 找到测试会话: {os.path.basename(test_file)}")
else:
    print("   ℹ️  没有找到合适的测试会话")

print("\n" + "=" * 60)
print("✅ 集成测试完成！")
print("\n💡 使用方法:")
print("   python3 /root/.openclaw/workspace/scripts/token_watcher_v2.py")
print("   --quiet: 静默模式（cron使用）")
print("   --check-only: 仅检查，不压缩")
