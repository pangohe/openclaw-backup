# 📋 Cron 任务与多通道配置完整导出

**导出时间**: 2026-03-09 12:27  
**系统版本**: OpenClaw 2026.2.26  
**备份来源**: 3 月 1 日恢复版本

---

## 🔄 Cron 任务列表 (共 3 个)

### 1️⃣ Token Watcher - 智能监控（优化版）
```json
{
  "id": "3a5ec4e7-157f-4ddc-838e-42ee8a56130d",
  "agentId": "main",
  "sessionKey": "agent:main:telegram:direct:8571370259",
  "name": "Token Watcher - 智能监控（优化版）",
  "enabled": true,
  "schedule": {
    "kind": "every",
    "everyMs": 300000  // 每 5 分钟
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "运行 token watcher 检查：\n\n1. 执行：python3 /root/.openclaw/workspace/scripts/token_watcher.py --quiet\n2. 读取 token-state.json 获取最新状态\n3. 如果 token 使用超过 70%，创建提醒文件 TOKEN_ALERT.txt\n4. 结果以静默方式保存，不需要发送通知",
    "model": "nvidia/z-ai/glm4.7"
  },
  "delivery": {
    "mode": "none"  // 静默模式，不发送通知
  }
}
```
**状态**: ✅ 运行中 | 上次执行：成功 | 下次执行：5 分钟内

---

### 2️⃣ 每日新闻晚报 - 17:00
```json
{
  "id": "1b254063-e6c4-4d68-99b3-fff6ff79a620",
  "agentId": "default",
  "name": "每日新闻晚报 - 17:00",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 17 * * *",  // 每天 17:00
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "python3 /root/.openclaw/workspace/scripts/daily_news_report.py evening"
  },
  "delivery": {
    "mode": "announce",
    "channel": "last"  // 发送到上次使用的通道
  }
}
```
**状态**: ✅ 运行中 | 下次执行：今天 17:00

---

### 3️⃣ 每日新闻早餐 - 9:30
```json
{
  "id": "739685ac-24cb-4576-883f-8ccd222710d1",
  "agentId": "default",
  "name": "每日新闻早餐 - 9:30",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "30 9 * * *",  // 每天 9:30
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "python3 /root/.openclaw/workspace/scripts/daily_news_report.py morning"
  },
  "delivery": {
    "mode": "announce",
    "channel": "last"  // 发送到上次使用的通道
  }
}
```
**状态**: ✅ 运行中 | 下次执行：明天 9:30

---

## 📡 多通道配置

### 已启用通道 (3 个)

| 通道 | 状态 | 配置详情 |
|------|------|---------|
| **Telegram** | ✅ ON | Bot: @LeslieHeHeBot · 允许用户：8571370259 |
| **QQ Bot** | ✅ ON | 允许用户：* (所有人) |
| **Feishu** | ✅ ON | 已配置 · WebSocket 连接模式 |

---

### Telegram 配置
```yaml
Account: default (telegram-main)
Status: OK
Token: config (sha256:07e0991c · len 46)
Allow: 8571370259
```

---

### QQ Bot 配置
```yaml
Account: default
Status: OK
Token: config
Allow: *  # 允许所有人
```

---

### Feishu 配置
```yaml
Account: default
Status: OK
权限：26 个已授予
工具：feishu_doc, feishu_wiki, feishu_drive, feishu_bitable
```

---

## 🤖 Agent 配置

| Agent | 会话数 | 最后活跃 | 状态 |
|-------|--------|---------|------|
| **main** | 19 | 1 分钟前 | ✅ 活跃 |
| dashboard | 0 | unknown | 未激活 |
| default | 0 | unknown | 未激活 |
| feishu | 0 | unknown | 未激活 |
| qqbot | 0 | unknown | 未激活 |
| telebot | 0 | unknown | 未激活 |

---

## 📜 HEARTBEAT.md 任务

### Token Watcher V2（每次心跳）
- **脚本**: `python3 /root/.openclaw/workspace/scripts/token_watcher_v2.py --quiet`
- **频率**: 每 5 分钟
- **功能**: 
  - 监控所有通道（161 个会话）
  - BM25 智能压缩
  - 通道级别策略（QQ/TG/WA 不同保留规则）
  - 自动执行压缩（达到 70% 阈值）

**阈值配置（UltraConservative 模式）**:
- OK: < 60% (120k tokens)
- WARNING: ≥ 60% (120k)
- COMPRESS: ≥ 70% (140k) ⚡ 自动执行
- CRITICAL: ≥ 80% (160k) 🚨 必须压缩
- EMERGENCY: ≥ 90% (180k) 💥 立即处理

---

### Moltbook 检查（每 30 分钟）
- **API**: `https://www.moltbook.com/api/v1/feed?sort=new&limit=10`
- **账号**: leslieassistant
- **Agent ID**: 751fd1bf-7d57-43b1-8f77-619a0edc07a1
- **状态**: 已认领 ✅

---

### 加密货币通知队列发送（每次心跳）
- **脚本**: `python3 /home/admin/.openclaw/workspace/scripts/crypto_notification_sender.py`
- **队列位置**: `/home/admin/.openclaw/workspace/data/crypto-trends/notifications/`
- **投递**: Telegram

---

## 🛠️ 可用脚本工具

| 脚本 | 用途 |
|------|------|
| `token_watcher.py` | Token 使用监控 |
| `token_watcher_v2.py` | 全局 Token 监控（161 会话） |
| `daily_news_report.py` | 每日新闻报告（早/晚） |
| `crypto_trend_collector.py` | 加密货币数据收集 |
| `crypto_notification_sender.py` | 加密货币通知发送 |
| `moltbook_hourly_check.py` | Moltbook 每小时检查 |
| `moltbook_polymarket_monitor.py` | Polymarket 监控 |
| `compact_session.py` | 会话压缩 |
| `emergency_compressor.py` | 紧急压缩 |
| `priority_compressor.py` | 优先级压缩 |
| `unified_token_manager.py` | 统一 Token 管理 |
| `cross_agent_messenger.py` | 跨 Agent 消息 |
| `weekly_agents_sync.py` | 每周 Agent 同步 |
| `deploy_agents.sh` | Agent 部署 |
| `full-system-backup.sh` | 完整系统备份 |

---

## ⚠️ 安全警告

1. **plugins.allow 未设置** - 存在扩展插件自动加载风险
2. **QQ Bot 允许所有人** - `allowFrom: ["*"]` 建议限制
3. **反向代理未配置** - 如暴露 Control UI 需配置 trustedProxies

---

## 📝 优化建议

### 待优化项
1. **Cron 任务较少** - 仅 3 个，HEARTBEAT.md 中的任务未转为独立 Cron
2. **多 Agent 未激活** - dashboard/feishu/qqbot/telebot 均未激活
3. **通道隔离** - 所有通道共用 main agent，未实现真正的多 Agent 架构
4. **安全配置** - 需要设置 plugins.allow 和限制 QQ Bot 访问

### 建议添加的 Cron 任务
- [ ] Moltbook 每小时检查（目前是 HEARTBEAT 手动检查）
- [ ] 加密货币数据收集（目前是 HEARTBEAT 手动检查）
- [ ] 系统健康检查（每日）
- [ ] 备份完整性检查（每周）
- [ ] 会话归档（每周）

---

**文档位置**: `/root/.openclaw/workspace/docs/cron-and-channels-config.md`  
**最后更新**: 2026-03-09 12:27
