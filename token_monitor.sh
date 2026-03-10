#!/bin/bash
# Token Monitor - 后台监控 token 使用量并在阈值时提醒

THRESHOLD_MB=80  # 警告阈值
CHECK_INTERVAL=300  # 检查间隔（秒）

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> ~/.openclaw/workspace/token_monitor.log
}

while true; do
    # 获取最新的会话文件大小
    LATEST_SESSION=$(ls -t ~/.openclaw/completions/*.json 2>/dev/null | head -1)
    
    if [ -n "$LATEST_SESSION" ]; then
        SESSION_SIZE=$(stat -c%s "$LATEST_SESSION" 2>/dev/null)
        SESSION_MB=$((SESSION_SIZE / 1024 / 1024))
        
        log_message "检查: 当前会话 ${SESSION_MB}MB"
        
        if [ $SESSION_MB -gt $THRESHOLD_MB ]; then
            log_message "⚠️ 警告：Token 使用量超过 ${THRESHOLD_MB}MB，建议重启 Gateway"
            
            # 创建提醒文件
            echo "Token 使用量较高 (${SESSION_MB}MB)，建议运行: openclaw gateway restart" > ~/.openclaw/workspace/TOKEN_WARNING.txt
        fi
    fi
    
    sleep $CHECK_INTERVAL
done
