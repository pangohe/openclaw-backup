# HEARTBEAT.md

## Token Watcher V2 检查（每次心跳）✨ 新版
智能监控所有通道，自动压缩，确保聊天顺畅。

**检查命令：**
```bash
python3 /root/.openclaw/workspace/scripts/token_watcher_v2.py --quiet
```

**V2 核心改进：**
- ✅ 监控所有通道（161个会话）
- ✅ BM25 智能压缩（保留关键词相关对话）
- ✅ 通道级别策略（QQ/TG/WA 不同保留规则）
- ✅ 自动执行压缩（达到阈值自动处理）
- ✅ 5 分钟冷却期（防止重复压缩）

**阈值配置（UltraConservative 模式）：**
- OK: < 60% (120k tokens)
- WARNING: ≥ 60% (120k)
- COMPRESS: ≥ 70% (140k) ⚡ **自动执行智能压缩**
- CRITICAL: ≥ 80% (160k) 🚨 **必须压缩**
- EMERGENCY: ≥ 90% (180k) 💥 **立即处理**

**通道保留策略：**
| 通道 | 保留消息 | 保留天数 |
|------|---------|---------|
| main | 50 条 | 30 天 |
| qqbot | 30 条 | 7 天 |
| telegram | 30 条 | 14 天 |
| whatsapp | 15 条 | 3 天 |
| default | 20 条 | 7 天 |

**自动监控：**
- Cron任务：每5分钟自动静默检查
- 状态文件：`token-state.json`
- 提醒文件：超限时自动创建 `TOKEN_ALERT.txt`

**查看状态：**
```bash
python3 /root/.openclaw/workspace/scripts/token_watcher.py
cat /root/.openclaw/workspace/token-state.json
```

---

## 夜间任务原则 ⚠️
**时间范围**: 23:00-08:00
**执行规则**:
- ❌ 夜间任务的消息不主动推送
- ✅ 只在总结到有价值的知识时汇报
- ✅ 静默执行，积累信息再输出

**适用场景**:
- 心跳检查（邮件、日历、通知等）
- Token 监控 ✅ 最高优先级
- Moltbook 检查
- 其他定时任务

---

## Moltbook 检查（每 30 分钟）
如果距离上次检查 Moltbook 超过 30 分钟：
1. 获取 https://www.moltbook.com/heartbeat.md 并执行
2. 更新 heartbeat-state.json 中的 lastMoltbookCheck

**检查命令：**
```bash
curl "https://www.moltbook.com/api/v1/feed?sort=new&limit=10" \
  -H "Authorization: Bearer moltbook_sk_zZeDMmpICk0b9honi3FT3XA53g5JmvVc"
```

**检查是否被认领：**
```bash
curl https://www.moltbook.com/api/v1/agents/status \
  -H "Authorization: Bearer moltbook_sk_zZeDMmpICk0b9honi3FT3XA53g5JmvVc"
```

**账号信息：**
- 用户名：leslieassistant
- Agent ID：751fd1bf-7d57-43b1-8f77-619a0edc07a1
- API Key：moltbook_sk_zZeDMmpICk0b9honi3FT3XA53g5JmvVc
- 验证码：claw-XC7L
- 状态：已认领 ✅
- 主页：https://www.moltbook.com/u/leslieassistant
- Claim URL：https://www.moltbook.com/claim/moltbook_claim_klBSlXxdSx9zeDq_U-05-SM_euW46Sxf

**Moltbook 用途：**
- 学习其他成功 agent 的经验
- 寻找赚钱机会和商业机会
- 广州城中村改造项目业务拓展
- Business development 经验分享
- AI Agent 技术交流和最佳实践

---

## 加密货币通知队列发送（每次心跳）
每次心跳检查时，推送加密货币通知队列中的消息到 Telegram

**检查命令：**
```bash
python3 /home/admin/.openclaw/workspace/scripts/crypto_notification_sender.py
```

**队列位置：**
- `/home/admin/.openclaw/workspace/data/crypto-trends/notifications/`
- 每个重要市场变化会生成一个 `notification-*.json` 文件
- 发送后会标记为已发送（`"sent": true`）
