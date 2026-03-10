# GitHub 自动备份系统

## 概述

每天凌晨 3 点自动将 OpenClaw 配置、数据和脚本备份到 GitHub 仓库。

## 快速开始

### 1. 部署备份系统

```bash
bash /root/.openclaw/workspace/scripts/setup-github-backup.sh
```

### 2. 添加 SSH 公钥到 GitHub

运行部署脚本后，会显示 SSH 公钥。将它添加到：
- GitHub → Settings → SSH and GPG keys → New SSH key

### 3. 创建定时任务

```bash
openclaw cron add \
  --name 'GitHub Auto Backup' \
  --schedule 'cron 0 3 * * * Asia/Shanghai' \
  --payload 'bash /root/.openclaw/workspace/scripts/github-auto-backup.sh' \
  --delivery announce
```

## 手动执行备份

```bash
bash /root/.openclaw/workspace/scripts/github-auto-backup.sh
```

## 查看备份日志

```bash
tail -f /root/.openclaw/workspace/logs/github-backup.log
```

## 备份内容

- ✅ OpenClaw 配置 (`~/.openclaw/`)
- ✅ Workspace (`/root/.openclaw/workspace/`)
  - scripts/
  - skills/
  - memory/
  - docs/
  - data/
  - config/
- ✅ 项目文件
- ✅ 记忆文件 (AGENTS.md, MEMORY.md, 等)

## 文件结构

```
/root/.openclaw/workspace/
├── scripts/
│   ├── github-auto-backup.sh    # 备份主脚本
│   └── setup-github-backup.sh   # 部署脚本
├── logs/
│   └── github-backup.log        # 备份日志
└── docs/
    └── GITHUB_BACKUP_README.md  # 本文档
```

## 故障排除

### SSH 连接失败

```bash
# 测试 SSH 连接
ssh -T git@github.com

# 如果需要，确认主机密钥
ssh-keyscan github.com >> ~/.ssh/known_hosts
```

### 推送失败

```bash
# 手动拉取并解决冲突
cd /root/.openclaw/workspace
git pull --rebase origin main
git push origin main
```

### 权限错误

确保 SSH 密钥权限正确：
```bash
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

## 配置说明

在 `github-auto-backup.sh` 中可以修改：

```bash
GITHUB_REPO="your-username/your-repo"  # GitHub 仓库地址
BRANCH="main"                           # 分支名称
```

## 恢复备份

从 GitHub 恢复：

```bash
cd /root/.openclaw/workspace
git pull origin main
```

## 注意事项

1. 首次运行需要 SSH 密钥已添加到 GitHub
2. 确保仓库存在且有写入权限
3. 大文件建议使用 Git LFS

## 创建 GitHub 仓库（如果不存在）

```bash
# 使用 GitHub CLI（如果已安装）
gh repo create openclaw-backup --public --description "OpenClaw 自动备份"

# 或手动在 GitHub 网站创建
# https://github.com/new
```