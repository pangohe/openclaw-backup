# 🚨 OpenClaw 系统恢复指南

> **紧急恢复手册** - 从 GitHub 备份恢复整个系统

---

## 📋 目录

1. [快速恢复](#快速恢复)
2. [完整恢复步骤](#完整恢复步骤)
3. [恢复验证](#恢复验证)
4. [常见问题](#常见问题)
5. [紧急恢复脚本](#紧急恢复脚本)

---

## ⚡ 快速恢复

### 方式一：一条命令恢复（推荐）

```bash
cd /root && \
git clone git@github.com:pangohe/openclaw-backup.git openclaw-restore && \
cd openclaw-restore && \
cp -r * /root/.openclaw/workspace/ && \
cp -r .[^.]* /root/.openclaw/workspace/ 2>/dev/null || true
```

### 方式二：手动恢复

```bash
# 1. 进入工作目录
cd /root/.openclaw/workspace

# 2. 备份当前状态（以防万一）
cp -r /root/.openclaw/workspace /root/.openclaw/workspace.backup.$(date +%Y%m%d_%H%M%S)

# 3. 拉取最新备份
git fetch origin main
git reset --hard origin/main

# 4. 重启 OpenClaw
openclaw gateway restart
```

---

## 📖 完整恢复步骤

### 步骤 1: 确认 SSH 密钥已配置

```bash
# 检查 SSH 密钥
ls -la ~/.ssh/id_rsa.pub

# 如果不存在，生成新密钥
ssh-keygen -t ed25519 -C "backup@openclaw.local"
cat ~/.ssh/id_rsa.pub
```

**然后添加到 GitHub：**
- 访问：https://github.com/settings/keys
- 添加上面的公钥

### 步骤 2: 克隆备份仓库

```bash
# 方式 A：完全替换（推荐用于系统重装后）
cd /root
rm -rf openclaw-backup
git clone git@github.com:pangohe/openclaw-backup.git openclaw-backup
cd openclaw-backup

# 方式 B：覆盖现有 workspace
cd /root/.openclaw/workspace
git init
git remote add origin git@github.com:pangohe/openclaw-backup.git
git fetch origin main
git reset --hard origin/main
```

### 步骤 3: 恢复配置文件

```bash
# 恢复 OpenClaw 主配置
cp -r /root/openclaw-backup/.openclaw/workspace-state.json /root/.openclaw/ 2>/dev/null || true

# 恢复 cron 任务
crontab -l 2>/dev/null || echo "无现有 crontab"
```

### 步骤 4: 恢复定时任务

```bash
# 添加自动备份任务
echo "0 3 * * * /root/.openclaw/workspace/scripts/github-auto-backup.sh >> /root/.openclaw/workspace/logs/github-backup.log 2>&1" | crontab -

# 验证
crontab -l
```

### 步骤 5: 重启系统

```bash
# 重启 OpenClaw Gateway
openclaw gateway restart

# 检查状态
openclaw status
```

---

## ✅ 恢复验证

执行以下命令验证恢复是否成功：

```bash
# 1. 检查文件
ls -la /root/.openclaw/workspace/

# 2. 检查脚本
ls /root/.openclaw/workspace/scripts/*.sh

# 3. 检查 cron
crontab -l

# 4. 检查 Git
cd /root/.openclaw/workspace && git status

# 5. 检查系统状态
openclaw status
```

### 预期结果

- ✅ 文件数量 ≈ 230+
- ✅ 脚本数量 ≈ 40+
- ✅ cron 任务已添加
- ✅ Git 状态正常
- ✅ OpenClaw 运行正常

---

## 🔧 常见问题

### Q1: SSH 连接失败

```bash
# 测试连接
ssh -T git@github.com

# 如果失败，添加known_hosts
ssh-keyscan github.com >> ~/.ssh/known_hosts
```

### Q2: 权限错误

```bash
# 修复权限
chmod -R 755 /root/.openclaw/workspace/scripts/*.sh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### Q3: Git 分支不匹配

```bash
# 如果提示 main 不存在
git branch -a
git checkout master  # 或 main
```

### Q4: OpenClaw 无法启动

```bash
# 重启 Gateway
openclaw gateway restart

# 查看日志
tail -50 /root/.openclaw/workspace/logs/openclaw.log 2>/dev/null || echo "无日志"
```

### Q5: 想保留部分当前文件

```bash
# 只恢复特定目录
cd /root/.openclaw/workspace
git checkout origin/main -- scripts/ memory/ data/
```

---

## 🚀 紧急恢复脚本

创建一个一键恢复脚本：

```bash
#!/bin/bash
# 文件名: emergency-restore.sh
# 用途: 一键恢复 OpenClaw 系统

set -e

echo "🚀 OpenClaw 紧急恢复开始..."

# 备份当前状态
if [ -d "/root/.openclaw/workspace/.git" ]; then
    BACKUP_DIR="/root/.openclaw/workspace.backup.$(date +%Y%m%d_%H%M%S)"
    echo "📦 备份当前状态到: $BACKUP_DIR"
    cp -r /root/.openclaw/workspace "$BACKUP_DIR"
fi

# 拉取备份
cd /root/.openclaw/workspace
echo "📥 从 GitHub 拉取备份..."
git fetch origin main
git reset --hard origin/main

# 恢复 cron
echo "⏰ 恢复定时任务..."
echo "0 3 * * * /root/.openclaw/workspace/scripts/github-auto-backup.sh >> /root/.openclaw/workspace/logs/github-backup.log 2>&1" | crontab -

# 重启
echo "🔄 重启 OpenClaw..."
openclaw gateway restart 2>/dev/null || echo "⚠️  重启命令失败，请手动执行: openclaw gateway restart"

echo ""
echo "✅ 恢复完成！"
echo "📁 备份位置: $BACKUP_DIR"
echo "🔗 GitHub: https://github.com/pangohe/openclaw-backup"
echo ""
echo "验证命令:"
echo "  ls /root/.openclaw/workspace/scripts/*.sh | wc -l"
echo "  crontab -l"
echo "  openclaw status"
```

**使用方法：**
```bash
# 保存脚本
curl -o /root/emergency-restore.sh https://raw.githubusercontent.com/pangohe/openclaw-backup/main/scripts/emergency-restore.sh
chmod +x /root/emergency-restore.sh

# 执行恢复
bash /root/emergency-restore.sh
```

---

## 📞 紧急联系人

如果以上步骤都无法解决问题：

1. **查看日志**: `/root/.openclaw/workspace/logs/`
2. **GitHub Issues**: https://github.com/pangohe/openclaw-backup/issues
3. **手动检查**: 运行 `openclaw status` 查看详细错误

---

## 📚 相关资源

- **GitHub 仓库**: https://github.com/pangohe/openclaw-backup
- **备份脚本**: `/root/.openclaw/workspace/scripts/github-auto-backup.sh`
- **恢复脚本**: `/root/emergency-restore.sh`
- **定时任务**: 每天凌晨 3 点自动备份

---

> **最后更新**: 2026-03-10  
> **维护者**: OpenClaw System