#!/usr/bin/env python3
"""
Token Watcher - 智能token监控和压缩
优化版：确保聊天流畅，自动提醒和压缩
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
STATE_FILE = WORKSPACE / "token-state.json"
ALERT_FILE = WORKSPACE / "TOKEN_ALERT.txt"

# 阈值配置（UltraConservative 模式 - 更早触发）
THRESHOLDS = {
    "warning": 60,      # 60% (120k / 200k)
    "compress": 70,    # 70% (140k / 200k)
    "critical": 80,    # 80% (160k / 200k)
    "emergency": 90    # 90% (180k / 200k)
}

# 模型上下文大小（GLM4.7）
CONTEXT_WINDOW = 200000  # tokens

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_session_info(session_file):
    """获取会话信息"""
    try:
        size = session_file.stat().st_size
        lines = sum(1 for _ in open(session_file))
        
        # 粗略估算：1行 ≈ 1条消息，1条消息平均 400 tokens
        estimated_tokens = min(lines * 400, CONTEXT_WINDOW)
        token_percent = (estimated_tokens / CONTEXT_WINDOW) * 100
        
        return {
            "file": session_file.name,
            "size_mb": round(size / 1024 / 1024, 2),
            "lines": lines,
            "estimated_tokens": estimated_tokens,
            "token_percent": round(token_percent, 1)
        }
    except Exception as e:
        log(f"❌ 读取会话失败: {e}")
        return None

def load_state():
    """加载状态"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "timestamp": datetime.now().isoformat(),
            "last_check": None,
            "last_compression": None,
            "compression_count": 0,
            "alerts_sent": 0
        }

def save_state(state):
    """保存状态"""
    state["timestamp"] = datetime.now().isoformat()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_status_level(percent):
    """获取状态级别"""
    if percent >= THRESHOLDS["emergency"]:
        return "EMERGENCY"
    elif percent >= THRESHOLDS["critical"]:
        return "CRITICAL"
    elif percent >= THRESHOLDS["compress"]:
        return "COMPRESS"
    elif percent >= THRESHOLDS["warning"]:
        return "WARNING"
    else:
        return "OK"

def create_alert(message):
    """创建提醒文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ALERT_FILE, 'w') as f:
        f.write(f"⚠️ Token 警告\n")
        f.write(f"时间: {timestamp}\n\n")
        f.write(f"{message}\n\n")
        f.write(f"建议操作:\n")
        f.write(f"1. 运行: openclaw compress --session <session-id>\n")
        f.write(f"2. 或重启: openclaw gateway restart\n")
    log(f"🚨 警告文件已创建: {ALERT_FILE}")

def main():
    """主函数"""
    log("🔍 Token Watcher 开始检查...")
    
    # 获取所有会话
    sessions = []
    if SESSIONS_DIR.exists():
        for session_file in SESSIONS_DIR.glob("*.jsonl"):
            info = get_session_info(session_file)
            if info:
                sessions.append(info)
    
    if not sessions:
        log("ℹ️  没有找到会话文件")
        return
    
    # 找出最大的会话
    main_session = max(sessions, key=lambda x: x["token_percent"])
    state = load_state()
    
    log(f"📊 主会话: {main_session['file']}")
    log(f"   大小: {main_session['size_mb']} MB")
    log(f"   消息数: {main_session['lines']}")
    log(f"   Token使用: {main_session['estimated_tokens']:,} / {CONTEXT_WINDOW:,} ({main_session['token_percent']}%)")
    
    # 判断状态
    status = get_status_level(main_session["token_percent"])
    log(f"📈 状态: {status}")
    
    # 更新状态
    state["last_check"] = datetime.now().isoformat()
    state["percent"] = main_session["token_percent"]
    state["messages"] = main_session["lines"]
    
    # 处理不同状态
    if status == "EMERGENCY":
        log("⚠️  Token使用量极高！")
        create_alert(f"Token使用量达到 {main_session['token_percent']}%，建议立即压缩会话")
        state["alerts_sent"] += 1
        
    elif status == "CRITICAL":
        log("⚠️  Token使用量很高")
        create_alert(f"Token使用量达到 {main_session['token_percent']}%，建议压缩会话")
        state["alerts_sent"] += 1
        
    elif status == "COMPRESS":
        log("📢 Token使用量较高，建议压缩")
        if main_session["token_percent"] > state.get("last_warning_percent", 0):
            create_alert(f"Token使用量达到 {main_session['token_percent']}%，建议压缩以保持流畅")
            state["alerts_sent"] += 1
            state["last_warning_percent"] = main_session["token_percent"]
            
    elif status == "WARNING":
        log("ℹ️  Token使用量正常")
        
    # 保存状态
    save_state(state)
    
    log("✅ 检查完成")
    return status

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true", help="静默模式")
    args = parser.parse_args()
    
    if args.quiet:
        # 重定向输出到日志
        log_file = WORKSPACE / "token_watcher.log"
        sys.stdout = open(log_file, 'a')
        sys.stderr = sys.stdout
        status = main()
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    else:
        status = main()
