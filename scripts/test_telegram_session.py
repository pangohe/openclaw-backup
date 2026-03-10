#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Telegram sessions_send 不同 timeout 设置
"""

import subprocess
import json
import sys

def test_sessions_send(timeout_seconds):
    """测试 sessions_send 指定 timeout"""
    
    session_key = "agent:main:telegram:direct:8571370259"
    message = f"测试消息 - timeout={timeout_seconds}秒"
    
    cmd = [
        'openclaw', 'sessions', 'send',
        '--sessionKey', session_key,
        '--message', message,
        '--timeoutSeconds', str(timeout_seconds)
    ]
    
    print(f"\n🧪 测试 timeout={timeout_seconds}秒...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds + 10)
    
    if result.returncode == 0:
        print(f"✅ 成功 (timeout={timeout_seconds}s)")
        try:
            output = json.loads(result.stdout)
            print(f"   状态：{output.get('status', 'unknown')}")
            if output.get('status') == 'ok':
                print(f"   ✅ 消息已送达！")
            return True
        except:
            print(f"   输出：{result.stdout[:200]}")
            return True
    else:
        print(f"❌ 失败 (timeout={timeout_seconds}s)")
        print(f"   错误：{result.stderr[:200]}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🧪 Telegram sessions_send Timeout 测试")
    print("=" * 60)
    
    # 测试不同 timeout 值
    timeouts = [5, 10, 15, 30]
    results = {}
    
    for timeout in timeouts:
        try:
            results[timeout] = test_sessions_send(timeout)
        except subprocess.TimeoutExpired:
            print(f"⏰ 超时 (timeout={timeout}s)")
            results[timeout] = False
        except Exception as e:
            print(f"❌ 错误：{e}")
            results[timeout] = False
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    for timeout, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"timeout={timeout}s: {status}")
    
    # 推荐
    print("\n" + "=" * 60)
    print("💡 推荐配置")
    print("=" * 60)
    
    # 找出最小成功 timeout
    successful_timeouts = [t for t, s in results.items() if s]
    if successful_timeouts:
        min_success = min(successful_timeouts)
        recommended = min_success + 5  # 加 5 秒 buffer
        print(f"最小成功 timeout: {min_success}秒")
        print(f"推荐设置：{recommended}秒")
        print(f"\n使用示例:")
        print(f"  sessions_send(")
        print(f"    sessionKey='agent:main:telegram:direct:8571370259',")
        print(f"    message='...',")
        print(f"    timeoutSeconds={recommended}  # ← 推荐值")
        print(f"  )")
    else:
        print("⚠️ 所有 timeout 都失败，可能需要检查 Telegram 通道配置")
    
    print("\n" + "=" * 60)
