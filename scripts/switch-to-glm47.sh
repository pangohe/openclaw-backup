#!/bin/bash
# 切换到 NVIDIA GLM4.7 模型

echo "🔄 正在切换到 NVIDIA GLM4.7..."

# 读取当前会话 ID
SESSION_FILE=$(ls -t /root/.openclaw/agents/feishu/sessions/*.jsonl 2>/dev/null | head -1)

if [ -z "$SESSION_FILE" ]; then
    echo "❌ 未找到会话文件"
    exit 1
fi

echo "📋 当前会话：$SESSION_FILE"

# 创建模型切换事件
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
EVENT_ID="model_switch_$(date +%s)"

# 追加模型切换事件到会话文件
cat >> "$SESSION_FILE" << EOF
{"type":"model_change","id":"$EVENT_ID","parentId":null,"timestamp":"$TIMESTAMP","provider":"nvidia","modelId":"z-ai/glm4.7"}
EOF

echo "✅ 已切换到 NVIDIA GLM4.7"
echo ""
echo "📊 模型信息:"
echo "   Provider: nvidia"
echo "   Model: z-ai/glm4.7"
echo "   Context: 128k tokens"
echo "   特点：快速、稳定、中文优秀"
echo ""
echo "⚠️ 注意：需要重启 Gateway 或开始新对话才能生效"
