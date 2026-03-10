#!/bin/bash
# GitHub 自动备份脚本
# 每天凌晨 3 点自动执行
# 将 OpenClaw 配置备份到 GitHub

set -e

# ============ 配置 ============
REPO_DIR="/root/.openclaw/workspace"
LOG_FILE="${REPO_DIR}/logs/github-backup.log"
GITHUB_REPO="leslieassistant/openclaw-backup"  # 修改为你的仓库地址
BRANCH="main"

# ============ 日志函数 ============
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1" | tee -a "$LOG_FILE"
}

# ============ 初始化 ============
log "========================================"
log "🚀 开始 GitHub 自动备份"
log "仓库: ${GITHUB_REPO}"
log "分支: ${BRANCH}"
log "========================================"

# 创建日志目录
mkdir -p "${REPO_DIR}/logs"
touch "$LOG_FILE"

# ============ 导航到仓库 ============
cd "$REPO_DIR"

# ============ 配置 Git ============
export GIT_TERMINAL_PROMPT=0
git config --global user.name "OpenClaw Backup" 2>/dev/null || true
git config --global user.email "backup@openclaw.local" 2>/dev/null || true

# ============ 检查 Git ============
if ! command -v git &> /dev/null; then
    log_error "Git 未安装"
    exit 1
fi

# ============ 检查远程仓库 ============
if ! git remote get-url origin &>/dev/null; then
    log "未配置远程仓库，添加 GitHub 仓库..."
    git remote add origin "git@github.com:${GITHUB_REPO}.git" 2>/dev/null || {
        log_error "无法配置远程仓库"
        exit 1
    }
fi

REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
log "远程仓库: ${REMOTE_URL}"

# ============ 拉取最新代码 ============
log "📥 拉取最新代码..."
if git fetch origin "$BRANCH" 2>/dev/null; then
    if git diff --quiet HEAD origin/"$BRANCH" 2>/dev/null; then
        log_success "本地已是最新版本"
    else
        log "有远程更新，尝试合并..."
        git pull origin "$BRANCH" --no-rebase 2>/dev/null || {
            log_warning "拉取冲突，手动处理中..."
            git pull origin "$BRANCH" --allow-unrelated-histories -m "merge" 2>/dev/null || true
        }
        log_success "代码已更新"
    fi
else
    log_warning "无法连接远程仓库，继续执行本地备份"
fi

# ============ 暂存所有更改 ============
log "📦 暂存所有文件..."
git add -A 2>/dev/null || {
    log_error "无法暂存文件"
    exit 1
}

# ============ 检查是否有更改 ============
if git diff --cached --quiet; then
    log_success "没有需要提交的更改"
    log "========================================"
    log "✅ 备份完成（无新更改）"
    log "========================================"
    exit 0
fi

# ============ 获取变更统计 ============
CHANGED_FILES=$(git diff --cached --name-only | wc -l)
log "变更文件数: ${CHANGED_FILES}"

# ============ 创建提交 ============
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
COMMIT_MSG="Auto backup: ${TIMESTAMP}"

log "📝 创建提交..."
if git commit -m "$COMMIT_MSG" 2>/dev/null; then
    log_success "提交已创建"
else
    log_error "无法创建提交"
    exit 1
fi

# ============ 推送到 GitHub ============
log "🚀 推送到 GitHub..."
if git push origin "$BRANCH" 2>&1; then
    log_success "✅ 备份成功推送到 GitHub！"
    log ""
    log "📊 备份摘要："
    log "   - 仓库: ${GITHUB_REPO}"
    log "   - 分支: ${BRANCH}"
    log "   - 变更文件: ${CHANGED_FILES}"
    log "   - 提交: ${COMMIT_MSG}"
else
    log_error "推送失败，尝试解决..."
    
    # 尝试强制推送（如果本地是最新）
    log "尝试 --force-with-lease..."
    git push origin "$BRANCH" --force-with-lease 2>&1 && {
        log_success "强制推送成功"
        exit 0
    }
    
    log_error "无法推送到 GitHub"
    log "可能的原因："
    log "  1. SSH 密钥未添加到 GitHub"
    log "  2. 仓库不存在或无权限"
    log "  3. 网络连接问题"
    exit 1
fi

log "========================================"
log "✅ GitHub 自动备份完成！"
log "========================================"
exit 0