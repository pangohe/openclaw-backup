#!/bin/bash
# Token Watcher - 监控 OpenClaw token 使用量

echo "🔍 Token 使用情况检查"
echo "====================="

# 检查 completions 目录
COMPLETIONS_DIR="$HOME/.openclaw/completions"
LOGS_DIR="$HOME/.openclaw/logs"

if [ -d "$COMPLETIONS_DIR" ]; then
    COMPLETIONS_SIZE=$(du -sh "$COMPLETIONS_DIR" 2>/dev/null | cut -f1)
    COMPLETIONS_COUNT=$(ls -1 "$COMPLETIONS_DIR"/*.json 2>/dev/null | wc -l)
    echo "📁 Completions: $COMPLETIONS_SIZE ($COMPLETIONS_COUNT 文件)"
fi

if [ -d "$LOGS_DIR" ]; then
    LOGS_SIZE=$(du -sh "$LOGS_DIR" 2>/dev/null | cut -f1)
    echo "📝 Logs: $LOGS_SIZE"
fi

# 检查当前会话大小
SESSION_KEY=$(ls -t ~/.openclaw/completions/*.json 2>/dev/null | head -1)
if [ -n "$SESSION_KEY" ]; then
    SESSION_SIZE=$(stat -c%s "$SESSION_KEY" 2>/dev/null)
    SESSION_MB=$((SESSION_SIZE / 1024 / 1024))
    echo "💬 当前会话: ${SESSION_MB}MB"
    
    if [ $SESSION_MB -gt 50 ]; then
        echo "⚠️ 警告：当前会话较大，建议重启 Gateway 或清理历史"
    fi
fi

# 检查模型使用情况
echo ""
echo "🤖 当前模型:"
openclaw models list 2>/dev/null | grep -E "default|configured" || echo "  (无法获取模型列表)"

echo ""
echo "💡 提示：如果聊天变慢，运行 'openclaw gateway restart' 清理缓存"
