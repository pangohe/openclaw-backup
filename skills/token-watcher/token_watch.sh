#!/bin/bash
# Token Watcher - 监控 OpenClaw token 使用量

COMPLETIONS_DIR="$HOME/.openclaw/completions"
LOGS_DIR="$HOME/.openclaw/logs"

# 获取目录大小（以 MB 为单位）
get_size_mb() {
    du -sm "$1" 2>/dev/null | cut -f1
}

# 检查 completions 大小
if [ -d "$COMPLETIONS_DIR" ]; then
    COMP_SIZE=$(get_size_mb "$COMPLETIONS_DIR")
    echo "Completions: ${COMP_SIZE}MB"
    
    # 如果超过 50MB，发出警告
    if [ "$COMP_SIZE" -gt 50 ]; then
        echo "⚠️ 警告: Completions 目录超过 50MB，建议清理"
        echo "运行: rm ~/.openclaw/completions/*.json"
    fi
fi

# 检查 logs 大小
if [ -d "$LOGS_DIR" ]; then
    LOGS_SIZE=$(get_size_mb "$LOGS_DIR")
    echo "Logs: ${LOGS_SIZE}MB"
    
    if [ "$LOGS_SIZE" -gt 100 ]; then
        echo "⚠️ 警告: Logs 目录超过 100MB"
    fi
fi

# 总体建议
TOTAL=$((COMP_SIZE + LOGS_SIZE))
echo "总计: ${TOTAL}MB"

if [ "$TOTAL" -gt 80 ]; then
    echo "💡 建议重启 Gateway 清理缓存: openclaw gateway restart"
fi
