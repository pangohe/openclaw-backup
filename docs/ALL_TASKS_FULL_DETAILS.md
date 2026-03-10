# 📋 全部任务完整配置明细

**导出时间**: 2026-03-09 12:36  
**系统版本**: OpenClaw 2026.2.26  
**备份来源**: 3 月 1 日恢复版本

---

## 📡 目录

1. [Cron 任务明细](#1-cron-任务明细)
2. [HEARTBEAT 任务明细](#2-heartbeat-任务明细)
3. [脚本工具明细](#3-脚本工具明细)
4. [通道配置明细](#4-通道配置明细)
5. [Agent 配置明细](#5-agent-配置明细)

---

## 1️⃣ Cron 任务明细

### 任务 1: Token Watcher - 智能监控（优化版）

**基本信息**
```json
{
  "id": "3a5ec4e7-157f-4ddc-838e-42ee8a56130d",
  "agentId": "main",
  "sessionKey": "agent:main:telegram:direct:8571370259",
  "name": "Token Watcher - 智能监控（优化版）",
  "enabled": true,
  "createdAtMs": 1772305353165,
  "updatedAtMs": 1773030185353
}
```

**调度配置**
```json
{
  "schedule": {
    "kind": "every",
    "everyMs": 300000,  // 每 5 分钟 (300 秒)
    "anchorMs": 1772305353165
  },
  "sessionTarget": "isolated",
  "wakeMode": "now"
}
```

**执行内容**
```python
# payload.message 内容：
运行 token watcher 检查：

1. 执行：python3 /root/.openclaw/workspace/scripts/token_watcher.py --quiet
2. 读取 token-state.json 获取最新状态
3. 如果 token 使用超过 70%，创建提醒文件 TOKEN_ALERT.txt
4. 结果以静默方式保存，不需要发送通知
```

**模型配置**
```json
{
  "model": "nvidia/z-ai/glm4.7"
}
```

**投递配置**
```json
{
  "delivery": {
    "mode": "none"  // 静默模式，不发送通知
  }
}
```

**脚本详情**: `/root/.openclaw/workspace/scripts/token_watcher.py`
- **功能**: 监控主会话 token 使用量
- **阈值**: UltraConservative 模式
  - WARNING: 60% (120k tokens)
  - COMPRESS: 70% (140k tokens)
  - CRITICAL: 80% (160k tokens)
  - EMERGENCY: 90% (180k tokens)
- **输出**: 
  - 日志文件：`token_watcher.log`
  - 状态文件：`token-state.json`
  - 警告文件：`TOKEN_ALERT.txt` (超限时)

**运行状态**
```json
{
  "nextRunAtMs": 1773030453173,
  "lastRunAtMs": 1773030153173,
  "lastRunStatus": "ok",
  "lastDurationMs": 32180,
  "consecutiveErrors": 0
}
```

---

### 任务 2: 每日新闻晚报 - 17:00

**基本信息**
```json
{
  "id": "1b254063-e6c4-4d68-99b3-fff6ff79a620",
  "agentId": "default",
  "name": "每日新闻晚报 - 17:00",
  "enabled": true,
  "createdAtMs": 1772368343337,
  "updatedAtMs": 1773029387406
}
```

**调度配置**
```json
{
  "schedule": {
    "kind": "cron",
    "expr": "0 17 * * *",  // 每天 17:00
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now"
}
```

**执行内容**
```bash
python3 /root/.openclaw/workspace/scripts/daily_news_report.py evening
```

**投递配置**
```json
{
  "delivery": {
    "mode": "announce",
    "channel": "last"  // 发送到上次使用的通道
  }
}
```

**脚本详情**: `/root/.openclaw/workspace/scripts/daily_news_report.py`
- **功能**: 使用 Tavily API 搜索全球新闻
- **API Key**: `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`
- **搜索类别**:
  - 国际新闻
  - 财经新闻
  - 科技新闻
  - 体育新闻
  - 娱乐新闻
- **输出格式**: Markdown 格式新闻报告
- **每条新闻包含**: 标题、日期、摘要、URL

**运行状态**
```json
{
  "nextRunAtMs": 1773046800000,
  "lastRunAtMs": 1773029309000,
  "lastRunStatus": "ok",
  "lastDurationMs": 78406,
  "lastDelivered": true
}
```

---

### 任务 3: 每日新闻早餐 - 9:30

**基本信息**
```json
{
  "id": "739685ac-24cb-4576-883f-8ccd222710d1",
  "agentId": "default",
  "name": "每日新闻早餐 - 9:30",
  "enabled": true,
  "createdAtMs": 1772368332511,
  "updatedAtMs": 1773029309000
}
```

**调度配置**
```json
{
  "schedule": {
    "kind": "cron",
    "expr": "30 9 * * *",  // 每天 9:30
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now"
}
```

**执行内容**
```bash
python3 /root/.openclaw/workspace/scripts/daily_news_report.py morning
```

**投递配置**
```json
{
  "delivery": {
    "mode": "announce",
    "channel": "last"
  }
}
```

**脚本详情**: 同晚报脚本
- **区别**: morning 模式搜索前一天 24 小时的新闻

**运行状态**
```json
{
  "nextRunAtMs": 1773106200000,
  "lastRunAtMs": 1773029258909,
  "lastRunStatus": "ok",
  "lastDurationMs": 50091,
  "lastDelivered": true
}
```

---

## 2️⃣ HEARTBEAT 任务明细

**配置文件**: `/root/.openclaw/workspace/HEARTBEAT.md`

### 任务 2.1: Token Watcher V2 检查

**触发条件**: 每次心跳（每 30 分钟）

**执行命令**
```bash
python3 /root/.openclaw/workspace/scripts/token_watcher_v2.py --quiet
```

**脚本详情**: `/root/.openclaw/workspace/scripts/token_watcher_v2.py` (24.9KB)

**核心功能**:
- ✅ 监控所有通道（161 个会话）
- ✅ BM25 智能压缩（保留关键词相关对话）
- ✅ 通道级别策略（QQ/TG/WA 不同保留规则）
- ✅ 自动执行压缩（达到阈值自动处理）
- ✅ 5 分钟冷却期（防止重复压缩）

**阈值配置（UltraConservative 模式）**
| 状态 | 阈值 | Tokens | 动作 |
|------|------|--------|------|
| OK | < 60% | < 120k | 无操作 |
| WARNING | ≥ 60% | ≥ 120k | 记录警告 |
| COMPRESS | ≥ 70% | ≥ 140k | ⚡ 自动执行智能压缩 |
| CRITICAL | ≥ 80% | ≥ 160k | 🚨 必须压缩 |
| EMERGENCY | ≥ 90% | ≥ 180k | 💥 立即处理 |

**通道保留策略**
| 通道 | 保留消息 | 保留天数 | 优先级 |
|------|---------|---------|--------|
| main | 50 条 | 30 天 | high |
| qqbot | 30 条 | 7 天 | high |
| telegram | 30 条 | 14 天 | high |
| whatsapp | 15 条 | 3 天 | medium |
| default | 20 条 | 7 天 | low |
| dashboard | 10 条 | 1 天 | emergency |

**输出文件**:
- 状态文件：`token-state-v2.json`
- 日志文件：`memory/token-watcher.log`

---

### 任务 2.2: Moltbook 检查

**触发条件**: 每 30 分钟（如果距离上次检查超过 30 分钟）

**执行命令**
```bash
# 获取 feed
curl "https://www.moltbook.com/api/v1/feed?sort=new&limit=10" \
  -H "Authorization: Bearer moltbook_sk_zZeDMmpICk0b9honi3FT3XA53g5JmvVc"

# 检查 agent 状态
curl https://www.moltbook.com/api/v1/agents/status \
  -H "Authorization: Bearer moltbook_sk_zZeDMmpICk0b9honi3FT3XA53g5JmvVc"
```

**账号信息**
```yaml
用户名：leslieassistant
Agent ID: 751fd1bf-7d57-43b1-8f77-619a0edc07a1
API Key: moltbook_sk_zZeDMmpICk0b9honi3FT3XA53g5JmvVc
验证码：claw-XC7L
状态：已认领 ✅
主页：https://www.moltbook.com/u/leslieassistant
```

**脚本详情**: `/root/.openclaw/workspace/scripts/moltbook_hourly_check.py` (7.1KB)

**功能**:
- 获取 Moltbook feed 最新动态（10 条）
- 检查 agent 认领状态
- 分析 feed 内容，筛选感兴趣话题
- 记录有价值的发现

**关键词过滤**
```python
KEYWORDS = [
    "agent", "ai", "bot", "赚钱", "business", "startup", "自动化",
    "trading", "arbitrage", "strategies", "success", "case study",
    "python", "script", "automation", "workflow", "integration"
]
MIN_UPVOTES = 3  # 最少 3 个赞
```

**输出文件**:
- 状态文件：`data/moltbook/hourly_check_state.json`
- 日志文件：`data/moltbook/hourly_check_log.json`

**用途**:
- 学习其他成功 agent 的经验
- 寻找赚钱机会和商业机会
- 广州城中村改造项目业务拓展
- Business development 经验分享
- AI Agent 技术交流和最佳实践

---

### 任务 2.3: 加密货币通知队列发送

**触发条件**: 每次心跳

**执行命令**
```bash
python3 /home/admin/.openclaw/workspace/scripts/crypto_notification_sender.py
```

**功能**:
- 检查加密货币通知队列
- 推送未发送的通知到 Telegram
- 标记已发送的通知

**队列位置**
```
/home/admin/.openclaw/workspace/data/crypto-trends/notifications/
```

**通知格式**
```json
{
  "created_at": "2026-03-09T12:00:00",
  "type": "crypto_trend",
  "sent": false,
  "channel": "telegram",
  "message": "🚨 加密货币重要变化：\n\n..."
}
```

**数据来源**: `crypto_trend_collector.py` 收集的数据

---

## 3️⃣ 脚本工具明细

### 3.1 Token 管理类

#### token_watcher.py (5.7KB)
- **路径**: `/root/.openclaw/workspace/scripts/token_watcher.py`
- **功能**: 监控主会话 token 使用量
- **阈值**: UltraConservative 模式
- **输出**: 日志 + 状态文件 + 警告文件

#### token_watcher_v2.py (24.9KB)
- **路径**: `/root/.openclaw/workspace/scripts/token_watcher_v2.py`
- **功能**: 全局 token 监控 + 智能压缩
- **特性**: BM25 算法 + 通道级别策略
- **压缩模式**: 原生压缩 / 增强压缩（可选）

#### unified_token_manager.py (3.2KB)
- **路径**: `/root/.openclaw/workspace/scripts/unified_token_manager.py`
- **功能**: 统一 token 管理
- **用途**: 跨通道 token 统计和管理

#### compact_session.py (2.2KB)
- **路径**: `/root/.openclaw/workspace/scripts/compact_session.py`
- **功能**: 会话压缩
- **用途**: 手动压缩指定会话

#### emergency_compressor.py (1.2KB)
- **路径**: `/root/.openclaw/workspace/scripts/emergency_compressor.py`
- **功能**: 紧急压缩
- **用途**: 超限时快速压缩到安全水平

#### priority_compressor.py (2.4KB)
- **路径**: `/root/.openclaw/workspace/scripts/priority_compressor.py`
- **功能**: 优先级压缩
- **用途**: 根据重要性压缩不同会话

---

### 3.2 数据收集类

#### crypto_trend_collector.py (4.4KB)
- **路径**: `/root/.openclaw/workspace/scripts/crypto_trend_collector.py`
- **功能**: 收集加密货币走势数据
- **数据源**: CoinGecko API
- **监控币种**: 9 个主流币种
  - Bitcoin, Ethereum, BNB, Solana, XRP, Cardano, Dogecoin, Polkadot, Tron
- **触发阈值**: 5% 价格变化
- **输出**: 
  - 数据文件：`data/crypto-trends/crypto-trend-{timestamp}.json`
  - 通知队列：`data/crypto-trends/notifications/notification-{timestamp}.json`

#### moltbook_hourly_check.py (7.1KB)
- **路径**: `/root/.openclaw/workspace/scripts/moltbook_hourly_check.py`
- **功能**: Moltbook 社区动态监控
- **API**: Moltbook API v1
- **输出**: 发现记录 + agent 状态

#### moltbook_polymarket_monitor.py (5.3KB)
- **路径**: `/root/.openclaw/workspace/scripts/moltbook_polymarket_monitor.py`
- **功能**: Polymarket 预测市场监控
- **用途**: 套利机会检测

#### daily_news_report.py (6.1KB)
- **路径**: `/root/.openclaw/workspace/scripts/daily_news_report.py`
- **功能**: 每日新闻报告生成
- **API**: Tavily Search API
- **模式**: morning / evening
- **输出**: Markdown 格式新闻报告

---

### 3.3 系统维护类

#### analyze_telegram_backup.py (2.2KB)
- **路径**: `/root/.openclaw/workspace/scripts/analyze_telegram_backup.py`
- **功能**: Telegram 备份分析

#### compare_telegram_sessions.py (3.3KB)
- **路径**: `/root/.openclaw/workspace/scripts/compare_telegram_sessions.py`
- **功能**: 比较不同 Telegram 会话

#### model_benchmark.py (8.2KB)
- **路径**: `/root/.openclaw/workspace/scripts/model_benchmark.py`
- **功能**: 模型性能基准测试

#### model_benchmark_v2.py (5.9KB)
- **路径**: `/root/.openclaw/workspace/scripts/model_benchmark_v2.py`
- **功能**: 模型性能基准测试 V2

#### model_benchmark_api.py (9.8KB)
- **路径**: `/root/.openclaw/workspace/scripts/model_benchmark_api.py`
- **功能**: API 方式模型基准测试

#### test_model_speed.py (5.5KB)
- **路径**: `/root/.openclaw/workspace/scripts/test_model_speed.py`
- **功能**: 模型响应速度测试

---

### 3.4 Agent 协作类

#### cross_agent_messenger.py (654B)
- **路径**: `/root/.openclaw/workspace/scripts/cross_agent_messenger.py`
- **功能**: 跨 Agent 消息传递

#### test_cross_agent.py (2.4KB)
- **路径**: `/root/.openclaw/workspace/scripts/test_cross_agent.py`
- **功能**: 跨 Agent 通信测试

#### weekly_agents_sync.py (727B)
- **路径**: `/root/.openclaw/workspace/scripts/weekly_agents_sync.py`
- **功能**: 每周 Agent 同步

#### deploy_agents.sh (6.2KB)
- **路径**: `/root/.openclaw/workspace/scripts/deploy_agents.sh`
- **功能**: Agent 部署脚本

---

### 3.5 备份类

#### full-system-backup.sh (8.6KB)
- **路径**: `/root/.openclaw/workspace/scripts/full-system-backup.sh`
- **功能**: 完整系统备份
- **备份内容**: 配置、会话、数据、脚本

---

### 3.6 增强压缩（技能）

#### enhanced_compact.py
- **路径**: `/root/.openclaw/workspace/skills/token-saver-v2/scripts/enhanced_compact.py`
- **功能**: BM25 增强压缩器
- **特性**: 话题分组 + 重要性评分

#### chat_indexer.py
- **路径**: `/root/.openclaw/workspace/skills/token-saver-v2/scripts/chat_indexer.py`
- **功能**: 聊天内容索引

---

## 4️⃣ 通道配置明细

### 4.1 Telegram

**配置状态**
```yaml
Account: default (telegram-main)
Status: OK
Token: config (sha256:07e0991c · len 46)
Bot: @LeslieHeHeBot
Allow: 8571370259  # 仅允许指定用户
```

**会话统计**
- 总会话数：1
- 最后活跃：15 分钟前
- Token 使用：57k/1000k (6%)

**用途**: 主要工作通道、投资顾问（叻仔）

---

### 4.2 QQ Bot

**配置状态**
```yaml
Account: default
Status: OK
Token: config
Allow: *  # 允许所有人 ⚠️
```

**会话统计**
- 总会话数：1
- 最后活跃：1 分钟前
- Token 使用：28k/1000k (3%)

**用途**: 系统管家（细佬）、日常对话

**安全警告**: 允许所有人访问，建议限制

---

### 4.3 Feishu

**配置状态**
```yaml
Account: default
Status: OK
连接模式：WebSocket
```

**已授予权限** (26 个)
- `im:message` - 消息发送和接收
- `im:chat:readonly` - 聊天信息读取
- `contact:contact.base:readonly` - 联系人信息
- `docx:document:readonly` - 文档读取
- `aily:*` - Aily AI 相关权限

**已注册工具**
1. `feishu_doc` - 飞书文档操作
2. `feishu_wiki` - 飞书知识库
3. `feishu_drive` - 飞书云存储
4. `feishu_bitable` - 多维表格
5. `feishu_app_scopes` - 应用权限管理

**用途**: 工作助理（Natalie）、文档管理

---

## 5️⃣ Agent 配置明细

### 5.1 main (主 Agent)

**状态**: ✅ 活跃（1 分钟前）

**会话数**: 19

**Bootstrap 文件**: ✅ 存在

**会话存储**: `~/.openclaw/agents/main/sessions/sessions.json`

**活跃会话**
| 会话 Key | 类型 | 最后活跃 | 模型 | Token 使用 |
|---------|------|---------|------|-----------|
| agent:main:qqbot:direct:c721984… | direct | 1m ago | qwen3.5-plus | 28k/1000k (3%) |
| agent:main:main | direct | 14m ago | qwen3.5-plus | 59k/1000k (6%) |
| agent:main:telegram:direct:8571… | direct | 15m ago | qwen3.5-plus | 57k/1000k (6%) |
| agent:main:cron:* | cron | 2-17m ago | 多种 | 15-17k/128k |

**默认模型**: `bailian/qwen3.5-plus` (1000k context)

---

### 5.2 dashboard

**状态**: ⏸️ 未激活

**会话数**: 0

**Bootstrap 文件**: ❌ 不存在

**用途**: 应急通道、系统监控

---

### 5.3 default

**状态**: ⏸️ 未激活

**会话数**: 0

**Bootstrap 文件**: ❌ 不存在

**用途**: 默认 Agent、新闻报告

---

### 5.4 feishu

**状态**: ⏸️ 未激活

**会话数**: 0

**Bootstrap 文件**: ❌ 不存在

**用途**: 飞书工作助理（Natalie）

---

### 5.5 qqbot

**状态**: ⏸️ 未激活

**会话数**: 0

**Bootstrap 文件**: ❌ 不存在

**用途**: QQ 系统管家（细佬）

---

### 5.6 telebot

**状态**: ⏸️ 未激活

**会话数**: 0

**Bootstrap 文件**: ❌ 不存在

**用途**: Telegram 投资顾问（叻仔）

---

## ⚠️ 安全问题

### 1. plugins.allow 未设置
**风险**: 扩展插件可能自动加载
**修复**: 在配置中设置 `plugins.allow` 明确列出信任的插件

### 2. QQ Bot 允许所有人
**风险**: 任何人都可以通过 QQ 发送指令
**修复**: 限制 `allowFrom` 为特定用户 ID

### 3. 反向代理未配置
**风险**: 如暴露 Control UI，X-Forwarded-For 可能被伪造
**修复**: 配置 `gateway.trustedProxies`

### 4. 多 Agent 未激活
**风险**: 所有通道共用 main agent，无隔离
**建议**: 激活专用 agent 实现职责分离

---

## 📊 统计汇总

| 类别 | 数量 |
|------|------|
| Cron 任务 | 3 个 |
| HEARTBEAT 任务 | 3 个 |
| Python 脚本 | 19 个 |
| Shell 脚本 | 1 个 |
| 通道 | 3 个 |
| Agent | 6 个 (1 活跃) |
| 总会话 | 19 个 |
| 总 Token 使用 | ~200k/6000k (3.3%) |

---

**文档位置**: `/root/.openclaw/workspace/docs/ALL_TASKS_FULL_DETAILS.md`  
**文件大小**: ~15KB  
**最后更新**: 2026-03-09 12:36
