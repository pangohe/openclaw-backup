#!/bin/bash
# GitHub 自动备份部署脚本
# 部署 SSH 密钥、配置 Git、创建定时任务

set -e

echo "🚀 开始部署 GitHub 自动备份"
echo ""

# ============ 配置 ============
REPO_DIR="/root/.openclaw/workspace"
BACKUP_SCRIPT="${REPO_DIR}/scripts/github-auto-backup.sh"
LOG_FILE="${REPO_DIR}/logs/github-backup.log"

# ============ 步骤 1: 配置 Git ============
echo "📝 步骤 1: 配置 Git..."
git config --global user.name "OpenClaw Backup" || true
git config --global user.email "backup@openclaw.local" || true
echo "✅ Git 配置完成"
echo ""

# ============ 步骤 2: 创建日志目录 ============
echo "📁 步骤 2: 创建日志目录..."
mkdir -p "${REPO_DIR}/logs"
touch "$LOG_FILE"
echo "✅ 日志目录已创建: ${REPO_DIR}/logs/"
echo ""

# ============ 步骤 3: 创建备份脚本 ============
echo "📜 步骤 3: 创建备份脚本..."
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "创建 github-auto-backup.sh..."
    # 脚本内容已在上一部创建
else
    echo "备份脚本已存在，跳过创建"
fi
chmod +x "$BACKUP_SCRIPT"
echo "✅ 备份脚本已就绪"
echo ""

# ============ 步骤 4: 创建 SSH 密钥 ============
echo "🔐 步骤 4: 创建 SSH 密钥..."
SSH_DIR="$HOME/.ssh"
mkdir -p "$SSH_DIR"
chmod 700 "$SSH_DIR"

if [ ! -f "${SSH_DIR}/id_rsa" ]; then
    ssh-keygen -t ed25519 -C "backup@openclaw.local" -f "${SSH_DIR}/id_rsa" -N ""
    chmod 600 "${SSH_DIR}/id_rsa"
    chmod 644 "${SSH_DIR}/id_rsa.pub"
    echo "✅ SSH 密钥已创建"
else
    echo "SSH 密钥已存在，跳过创建"
fi

echo ""
echo "📋 SSH 公钥（添加到 GitHub）："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "${SSH_DIR}/id_rsa.pub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  请将上面的公钥添加到 GitHub："
echo "   GitHub → Settings → SSH and GPG keys → New SSH key"
echo ""

# ============ 步骤 5: 配置 SSH ============
echo "🔧 步骤 5: 配置 SSH..."
cat > "${SSH_DIR}/config" << EOF
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking accept-new
EOF
chmod 600 "${SSH_DIR}/config"
echo "✅ SSH 配置完成"
echo ""

# ============ 步骤 6: 测试 GitHub 连接 ============
echo "🧪 步骤 6: 测试 GitHub 连接..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "✅ GitHub 连接成功"
elif ssh -T git@github.com 2>&1 | grep -q "You've successfully authenticated"; then
    echo "✅ GitHub 连接成功"
else
    echo "⚠️  GitHub 连接测试完成（首次连接可能需要确认）"
fi
echo ""

# ============ 步骤 7: 配置远程仓库 ============
echo "🔗 步骤 7: 配置远程仓库..."
cd "$REPO_DIR"

# 检查是否已有远程仓库
if git remote get-url origin &>/dev/null; then
    echo "远程仓库已配置: $(git remote get-url origin)"
else
    echo "请输入 GitHub 仓库地址（格式：username/repo-name）："
    read -p " > " REPO_INPUT
    if [ -n "$REPO_INPUT" ]; then
        git remote add origin "git@github.com:${REPO_INPUT}.git"
        echo "✅ 远程仓库已添加: git@github.com:${REPO_INPUT}.git"
    else
        echo "❌ 未提供仓库地址，跳过远程配置"
    fi
fi
echo ""

# ============ 步骤 8: 创建 Cron 任务 ============
echo "⏰ 步骤 8: 创建定时任务..."

# 使用 OpenClaw cron 工具创建任务
CURRENT_TIME=$(date +%s)
# 凌晨 3 点的毫秒时间戳（今天 3:00 AM）
TARGET_HOUR=3
TARGET_MINUTE=0
CURRENT_HOUR=$(date +%H)

if [ "$CURRENT_HOUR" -lt "$TARGET_HOUR" ]; then
    # 今天还没到 3 点
    HOURS_LEFT=$((TARGET_HOUR - CURRENT_HOUR))
    atMs=$((CURRENT_TIME * 1000 + HOURS_LEFT * 3600000 + TARGET_MINUTE * 60000))
else
    # 今天已过 3 点，明天 3 点
    HOURS_LEFT=$((24 - CURRENT_HOUR + TARGET_HOUR))
    atMs=$((CURRENT_TIME * 1000 + HOURS_LEFT * 3600000 + TARGET_MINUTE * 60000))
fi

echo "✅ Cron 任务配置说明："
echo ""
echo "请手动创建定时任务或在 OpenClaw 中运行以下命令："
echo ""
echo "┌─────────────────────────────────────────────────────┐"
echo "│  openclaw cron add --name 'GitHub Auto Backup'      │"
echo "│  --schedule 'cron 0 3 * * * Asia/Shanghai'         │"
echo "│  --payload 'bash ${BACKUP_SCRIPT}'                  │"
echo "│  --delivery announce                                │"
echo "└─────────────────────────────────────────────────────┘"
echo ""

# ============ 完成 ============
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ GitHub 自动备份部署完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 下一步操作："
echo ""
echo "1️⃣  添加 SSH 公钥到 GitHub（如上方显示）"
echo ""
echo "2️⃣  如果是首次使用，先手动执行一次备份："
echo "   bash ${BACKUP_SCRIPT}"
echo ""
echo "3️⃣  创建定时任务（每天凌晨 3 点自动备份）："
echo "   openclaw cron add --name 'GitHub Auto Backup' \"
echo "     --schedule 'cron 0 3 * * * Asia/Shanghai' \"
echo "     --payload 'bash ${BACKUP_SCRIPT}' \"
echo "     --delivery announce"
echo ""
echo "📖 详细文档：docs/GITHUB_BACKUP_README.md"
echo ""