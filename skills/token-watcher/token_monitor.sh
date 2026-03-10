#!/bin/bash
# Token Monitor - 智能监控 OpenClaw Token 使用量
# 检测 completions 目录增长趋势和 session 压力

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_FILE="$HOME/.openclaw/workspace/memory/token-state.json"
LOG_FILE="$HOME/.openclaw/logs/token-monitor.log"
ALERT_FILE="$HOME/.openclaw/workspace/memory/token-alert.txt"

# 创建日志目录
mkdir -p "$HOME/.openclaw/logs"
mkdir -p "$HOME/.openclaw/workspace/memory"

# 阈值设置
WARNING_MB=30      # 30MB 警告
CRITICAL_MB=50     # 50MB 严重警告
URGENT_MB=80       # 80MB 紧急（必须立即清理）
MAX_FILES=300      # 最多 300 个 completion 文件

# 获取目录大小 (MB)
get_dir_size_mb() {
    du -sm "$1" 2>/dev/null | cut -f1 || echo "0"
}

# 获取文件数量
get_file_count() {
    ls -1 "$1"/*.json 2>/dev/null | wc -l || echo "0"
}

# 计算增长率
calculate_growth() {
    local current=$1
    if [ -f "$STATE_FILE" ]; then
        local previous=$(cat "$STATE_FILE" | grep -o '"completions_mb":[0-9]*' | cut -d: -f2)
        if [ -n "$previous" ] && [ "$previous" -gt 0 ]; then
            local growth=$((current - previous))
            echo "$growth"
            return
        fi
    fi
    echo "0"
}

# 主监控逻辑
main() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 获取目录信息
    local comp_size=$(get_dir_size_mb "$HOME/.openclaw/completions")
    local logs_size=$(get_dir_size_mb "$HOME/.openclaw/logs")
    local total_size=$((comp_size + logs_size))
    local comp_files=$(get_file_count "$HOME/.openclaw/completions")
    local growth=$(calculate_growth $comp_size)
    
    # 计算使用率百分比
    local max_expected=100
    local percentage=$((comp_size * 100 / max_expected))
    if [ $percentage -gt 100 ]; then
        percentage=100
    fi
    
    # 输出状态
    echo "[$timestamp] Token 监控报告"
    echo "  📁 Completions: ${comp_size}MB (${comp_files} 个文件)"
    echo "  📈 增长: ${growth}MB"
    echo "  📝 Logs: ${logs_size}MB"
    echo "  💾 Total: ${total_size}MB"
    echo "  📊 使用率: ${percentage}%"
    
    # 保存状态
    cat > "$STATE_FILE" << EOF
{
  "timestamp": "$timestamp",
  "completions_mb": $comp_size,
  "completions_files": $comp_files,
  "logs_mb": $logs_size,
  "total_mb": $total_size,
  "percentage": $percentage,
  "growth_mb": $growth
}
EOF

    # 检查阈值并发出警告
    local alert_level="normal"
    local actions=""
    local should_alert=false
    
    # 清除旧警报
    rm -f "$ALERT_FILE"
    
    if [ $comp_size -ge $URGENT_MB ]; then
        alert_level="URGENT"
        should_alert=true
        echo ""
        echo "  🚨 URGENT: Token 缓存达到 ${comp_size}MB！聊天已严重卡顿！"
        echo "  🔴 必须立即执行以下操作："
        echo ""
        echo "     ⚡ 发送 /reset 或 /new 开启新会话"
        echo ""
        actions="RESET_NOW"
        
        # 写入警报文件供 heartbeat 读取
        echo "🚨 Token 缓存已达 ${comp_size}MB，请立即发送 /new 开启新会话！" > "$ALERT_FILE"
        
    elif [ $comp_size -ge $CRITICAL_MB ]; then
        alert_level="CRITICAL"
        should_alert=true
        echo ""
        echo "  🔴 CRITICAL: Token 缓存达到 ${comp_size}MB！"
        echo "  ⚠️  聊天即将变得卡顿，请尽快执行："
        echo ""
        echo "     1️⃣  发送 /reset 或 /new 开启新会话"
        echo "     2️⃣  或运行: rm ~/.openclaw/completions/*.json"
        echo ""
        actions="RESET_REQUIRED"
        echo "⚠️ Token 缓存已达 ${comp_size}MB，建议发送 /new 开启新会话" > "$ALERT_FILE"
        
    elif [ $comp_size -ge $WARNING_MB ]; then
        alert_level="WARNING"
        should_alert=true
        echo ""
        echo "  🟡 WARNING: Token 缓存达到 ${comp_size}MB"
        echo "  💡 建议开启新会话或准备清理"
        echo ""
        actions="RESET_RECOMMENDED"
        
    else
        local remaining=$((WARNING_MB - comp_size))
        echo "  ✅ 状态正常，距离警告阈值还有 ${remaining}MB"
    fi
    
    # 快速增长检测
    if [ $growth -gt 10 ]; then
        echo "  ⚡ 注意: Completions 在过去周期增长了 ${growth}MB"
        if [ "$should_alert" = false ]; then
            echo "  💡 对话活跃，token 消耗较快"
        fi
    fi
    
    # 检查文件数量
    if [ $comp_files -gt $MAX_FILES ]; then
        echo "  📋 注意: Completion 文件数量较多 ($comp_files 个)，建议清理"
    fi
    
    # 记录到日志
    echo "[$timestamp] level=$alert_level comp=${comp_size}MB growth=${growth}MB files=$comp_files action=$actions" >> "$LOG_FILE"
    
    # 如果超过阈值，返回非零退出码
    if [ $comp_size -ge $WARNING_MB ]; then
        return 2
    fi
    
    return 0
}

main "$@"
