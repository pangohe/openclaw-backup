#!/bin/bash
# Token Compact - 自动压缩和清理 OpenClaw Token 缓存
# 当达到阈值时自动执行清理

COMPLETIONS_DIR="$HOME/.openclaw/completions"
LOGS_DIR="$HOME/.openclaw/logs"
BACKUP_DIR="$HOME/.openclaw/backups"

# 阈值
COMPACT_THRESHOLD_MB=50    # 超过此值执行压缩
CLEAR_THRESHOLD_MB=80      # 超过此值清空

# 获取目录大小
get_size_mb() {
    du -sm "$1" 2>/dev/null | cut -f1 || echo "0"
}

# 备份重要数据
backup_if_needed() {
    local size=$(get_size_mb "$COMPLETIONS_DIR")
    if [ $size -gt 30 ]; then
        mkdir -p "$BACKUP_DIR"
        local backup_name="completions-$(date +%Y%m%d-%H%M%S).tar.gz"
        echo "📦 备份 completions 到 $backup_name..."
        tar -czf "$BACKUP_DIR/$backup_name" -C "$COMPLETIONS_DIR" . 2>/dev/null
        echo "✅ 备份完成: $backup_name ($(du -sh "$BACKUP_DIR/$backup_name" | cut -f1))"
    fi
}

# 智能压缩 - 保留最近的，删除旧的
smart_compact() {
    echo "🧹 执行智能压缩..."
    
    # 保留最近 50 个 completion 文件
    local files_to_keep=50
    local total_files=$(ls -1 "$COMPLETIONS_DIR"/*.json 2>/dev/null | wc -l)
    
    if [ $total_files -gt $files_to_keep ]; then
        local files_to_delete=$((total_files - files_to_keep))
        echo "  将删除 $files_to_delete 个旧文件，保留最新的 $files_to_keep 个"
        
        # 按时间排序，删除最旧的
        ls -t "$COMPLETIONS_DIR"/*.json 2>/dev/null | tail -n $files_to_delete | xargs rm -f
        
        echo "✅ 压缩完成"
    else
        echo "  文件数量正常 ($total_files 个)，无需压缩"
    fi
}

# 完全清理
full_clear() {
    echo "🗑️  执行完全清理..."
    rm -f "$COMPLETIONS_DIR"/*.json
    echo "✅ 已清空所有 completions"
}

# 主函数
main() {
    echo "=== Token Compact ==="
    echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    local comp_size=$(get_size_mb "$COMPLETIONS_DIR")
    echo "当前 Completions: ${comp_size}MB"
    
    if [ $comp_size -ge $CLEAR_THRESHOLD_MB ]; then
        echo "⚠️  超过紧急阈值 (${CLEAR_THRESHOLD_MB}MB)，执行完全清理"
        backup_if_needed
        full_clear
        echo ""
        echo "🔴 请发送 /new 开启新会话以恢复流畅度"
        
    elif [ $comp_size -ge $COMPACT_THRESHOLD_MB ]; then
        echo "⚡ 超过压缩阈值 (${COMPACT_THRESHOLD_MB}MB)，执行智能压缩"
        smart_compact
        echo ""
        echo "🟡 建议发送 /new 开启新会话"
        
    else
        echo "✅ 当前大小正常，无需操作"
    fi
    
    # 显示清理后的大小
    local new_size=$(get_size_mb "$COMPLETIONS_DIR")
    echo ""
    echo "清理后: ${new_size}MB (释放 $((comp_size - new_size))MB)"
}

main "$@"
