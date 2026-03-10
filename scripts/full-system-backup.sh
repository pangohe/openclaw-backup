#!/bin/bash
# 完整系统备份脚本
# 备份所有 OpenClaw 相关配置、数据、文档

set -e

# 配置
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/admin/openclaw-backups/full"
BACKUP_FILE="openclaw-full-backup-${TIMESTAMP}.tar.gz"
TEMP_DIR="/tmp/openclaw-backup-${TIMESTAMP}"
LOG_FILE="${BACKUP_DIR}/backup-${TIMESTAMP}.log"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 创建目录
mkdir -p "${BACKUP_DIR}"
mkdir -p "${TEMP_DIR}"

# 日志函数
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}✗${NC} $1" | tee -a "${LOG_FILE}"
}

start_backup() {
    log "=========================================="
    log "开始完整系统备份"
    log "备份文件: ${BACKUP_FILE}"
    log "=========================================="
}

backup_openclaw_config() {
    log ""
    log "1. 备份 OpenClaw 配置文件..."

    # 主配置目录
    mkdir -p "${TEMP_DIR}/openclaw-config"

    if [ -d "/root/.openclaw" ]; then
        cp -r /root/.openclaw/* "${TEMP_DIR}/openclaw-config/" 2>/dev/null || true
        log_success "OpenClaw 主配置已备份"
    else
        log_warning "未找到 /root/.openclaw"
    fi

    # Agent 配置
    if [ -d "/root/.openclaw/agents" ]; then
        cp -r /root/.openclaw/agents "${TEMP_DIR}/openclaw-config/agents-backup" 2>/dev/null || true
        log_success "Agent 配置已备份"
    fi
}

backup_workspace() {
    log ""
    log "2. 备份 Workspace..."

    if [ -d "/root/.openclaw/workspace" ]; then
        cp -r /root/.openclaw/workspace "${TEMP_DIR}/workspace-backup"
        log_success "Workspace 已备份"
    else
        log_warning "未找到 workspace"
    fi
}

backup_skills() {
    log ""
    log "3. 备份 Skills..."

    mkdir -p "${TEMP_DIR}/skills-backup"

    # 本地 skills
    if [ -d "/root/.openclaw/skills" ]; then
        cp -r /root/.openclaw/skills/* "${TEMP_DIR}/skills-backup/" 2>/dev/null || true
        log_success "本地 skills 已备份"
    fi

    # 扩展 skills
    if [ -d "/usr/lib/node_modules/openclaw/extensions" ]; then
        cp -r /usr/lib/node_modules/openclaw/extensions "${TEMP_DIR}/skills-extensions" 2>/dev/null || true
        log_success "扩展 skills 已备份"
    fi

    # 用户 skills
    if [ -d "/root/.openclaw/extensions" ]; then
        cp -r /root/.openclaw/extensions "${TEMP_DIR}/skills-user" 2>/dev/null || true
        log_success "用户 skills 已备份"
    fi
}

backup_cron_jobs() {
    log ""
    log "4. 备份 Cron 任务..."

    mkdir -p "${TEMP_DIR}/cron-backup"

    # 导出所有 cron 任务
    crontab -l > "${TEMP_DIR}/cron-backup/crontab-backup.txt" 2>/dev/null || true

    # OpenClaw cron 配置
    if [ -f "/root/.openclaw/agents/main/agent/cron-jobs.json" ]; then
        cp /root/.openclaw/agents/main/agent/cron-jobs.json "${TEMP_DIR}/cron-backup/" || true
    fi

    # OpenClaw 数据库中的 cron（如果有）
    if command -v openclaw &> /dev/null; then
        openclaw cron list --json 2>/dev/null > "${TEMP_DIR}/cron-backup/cron-list.json" || true
    fi

    log_success "Cron 任务已备份"
}

backup_channels() {
    log ""
    log "5. 备份通道配置..."

    mkdir -p "${TEMP_DIR}/channels-backup"

    # Gateway 配置
    if [ -d "/root/.openclaw/gateway" ]; then
        cp -r /root/.openclaw/gateway/* "${TEMP_DIR}/channels-backup/" 2>/dev/null || true
    fi

    # 通道特定配置
    if [ -f "/root/.openclaw/agents/main/agent/channels.json" ]; then
        cp /root/.openclaw/agents/main/agent/channels.json "${TEMP_DIR}/channels-backup/" || true
    fi

    log_success "通道配置已备份"
}

backup_data() {
    log ""
    log "6. 备份数据目录..."

    if [ -d "/root/.openclaw/workspace/data" ]; then
        cp -r /root/.openclaw/workspace/data "${TEMP_DIR}/data-backup"
        log_success "数据目录已备份"
    else
        log_warning "未找到 data 目录"
    fi
}

backup_memory() {
    log ""
    log "7. 备份记忆文件..."

    if [ -d "/root/.openclaw/workspace/memory" ]; then
        cp -r /root/.openclaw/workspace/memory "${TEMP_DIR}/memory-backup"
        log_success "记忆文件已备份"
    fi

    # AGENTS.md 等核心文件
    for file in AGENTS.md SOUL.md USER.md IDENTITY.md MEMORY.md HEARTBEAT.md TOOLS.md; do
        if [ -f "/root/.openclaw/workspace/${file}" ]; then
            cp "/root/.openclaw/workspace/${file}" "${TEMP_DIR}/" || true
        fi
    done

    log_success "核心文件已备份"
}

backup_docs() {
    log ""
    log "8. 备份文档..."

    if [ -d "/root/.openclaw/workspace/docs" ]; then
        cp -r /root/.openclaw/workspace/docs "${TEMP_DIR}/docs-backup"
        log_success "文档已备份"
    fi
}

backup_system() {
    log ""
    log "9. 备份系统配置..."

    mkdir -p "${TEMP_DIR}/system-backup"

    # OpenClaw 版本信息
    if command -v openclaw &> /dev/null; then
        openclaw --version > "${TEMP_DIR}/system-backup/openclaw-version.txt" 2>&1 || true
        openclaw status > "${TEMP_DIR}/system-backup/openclaw-status.txt" 2>&1 || true
    fi

    # Node.js 版本
    node --version > "${TEMP_DIR}/system-backup/node-version.txt" 2>&1 || true
    npm list -g openclaw > "${TEMP_DIR}/system-backup/npm-openclaw.txt" 2>&1 || true

    # 系统信息
    uname -a > "${TEMP_DIR}/system-backup/system-info.txt" 2>&1

    log_success "系统配置已备份"
}

create_manifest() {
    log ""
    log "10. 生成备份清单..."

    # 生成备份清单
    cat > "${TEMP_DIR}/BACKUP_MANIFEST.txt" << EOF
========================================
OpenClaw 完整系统备份清单
========================================
备份时间: ${TIMESTAMP}
备份类型: 完整备份
备份脚本: full-system-backup.sh

备份内容:
----------------------------------------
1. OpenClaw 配置
2. Workspace (scripts, skills, data, docs, memory)
3. Skills (本地, 扩展, 用户)
4. Cron 任务
5. 通道配置
6. 数据目录
7. 记忆文件
8. 文档
9. 系统配置

目录结构:
----------------------------------------
EOF

    tree "${TEMP_DIR}" -L 2 >> "${TEMP_DIR}/BACKUP_MANIFEST.txt" 2>/dev/null || ls -laR "${TEMP_DIR}" >> "${TEMP_DIR}/BACKUP_MANIFEST.txt"

    # 统计信息
    echo "" >> "${TEMP_DIR}/BACKUP_MANIFEST.txt"
    echo "统计信息:" >> "${TEMP_DIR}/BACKUP_MANIFEST.txt"
    echo "文件数: $(find "${TEMP_DIR}" -type f | wc -l)" >> "${TEMP_DIR}/BACKUP_MANIFEST.txt"
    echo "目录数: $(find "${TEMP_DIR}" -type d | wc -l)" >> "${TEMP_DIR}/BACKUP_MANIFEST.txt"
    echo "总大小: $(du -sh "${TEMP_DIR}" | cut -f1)" >> "${TEMP_DIR}/BACKUP_MANIFEST.txt"

    log_success "备份清单已生成"
}

compress_backup() {
    log ""
    log "11. 压缩备份..."

    cd "${TEMP_DIR}/.."
    tar czf "${BACKUP_DIR}/${BACKUP_FILE}" -C "${TEMP_DIR}" .

    # 获取备份大小
    BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)

    log_success "备份已压缩: ${BACKUP_FILE} (${BACKUP_SIZE})"
}

cleanup() {
    log ""
    log "12. 清理临时文件..."

    rm -rf "${TEMP_DIR}"
    log_success "临时文件已清理"
}

display_summary() {
    log ""
    log "=========================================="
    log "✓ 备份完成！"
    log "=========================================="
    log ""
    log "备份文件: ${BACKUP_DIR}/${BACKUP_FILE}"
    log "备份大小: $(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)"
    log "日志文件: ${LOG_FILE}"
    log ""
    log "恢复命令:"
    log "  tar xzf ${BACKUP_DIR}/${BACKUP_FILE} -C /tmp/restore"
    log ""
    log "=========================================="
}

# 显示备份清单
display_manifest() {
    echo ""
    echo "========================================"
    echo "备份清单"
    echo "========================================"
    cat "${TEMP_DIR}/BACKUP_MANIFEST.txt" || echo "清单生成失败"
    echo "========================================"
}

# 主流程
main() {
    start_backup
    backup_openclaw_config
    backup_workspace
    backup_skills
    backup_cron_jobs
    backup_channels
    backup_data
    backup_memory
    backup_docs
    backup_system
    create_manifest

    # 显示清单
    display_manifest

    compress_backup
    cleanup
    display_summary
}

# 执行主流程
main

exit 0
