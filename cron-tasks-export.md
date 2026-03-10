# OpenClaw Cron 任务导出清单

**导出时间：** 2026-03-01 20:52
**导出命令：** `openclaw cron list`
**总任务数：** 7 个定时任务

---

## 📊 任务概览

| 任务名称 | 频率 | 状态 | 下次运行 | 代理 |
|---------|------|------|----------|------|
| Token Watcher | 每 5 分钟 | ✅ ok | 4 分钟后 | main |
| Polymarket Monitor | 每 30 分钟 | ✅ ok | 6 分钟后 | main |
| Crypto Trend Collector | 每天 9-21 点 | ❌ error | 6 分钟后 | main |
| Moltbook Hourly Check | 每小时 | ✅ ok | 10 分钟后 | main |
| 每日新闻早餐 | 每天 09:30 | ⏸️ idle | 13 小时后 | default |
| 每日经济简报 | 每天 10:00 | ✅ ok | 13 小时后 | default |
| 每日新闻晚报 | 每天 17:00 | ⏸️ idle | 20 小时后 | default |

---

## ✅ 活跃任务（正在运行）

### 1. Token Watcher - 智能监控

- **任务 ID：** `3a5ec4e7-157f-4ddc-838e-42ee8a56130d`
- **名称：** Token Watcher - 智能监控（V2 版本）
- **频率：** 每 5 分钟 (`*/5 * * * *`)
- **时区：** Asia/Shanghai
- **状态：** ✅ ok
- **上次运行：** 1 分钟前
- **下次运行：** 4 分钟后
- **目标会话：** isolated
- **运行代理：** main

**功能：**
- 智能监控所有 OpenClaw session 的 token 使用量
- 使用 Token Watcher V2（BM25 智能压缩）
- 自动压缩超限会话
- 记录到 `token-state.json`
- 静默模式，不发送通知

**相关文档：**
- `docs/token-limit-root-cause.md`
- `scripts/token_watcher_v2.py`

---

### 2. Polymarket Monitor

- **任务 ID：** `8f9f1d9c-0b00-4196-a75a-13273c64c18a`
- **名称：** Polymarket Monitor
- **频率：** 每 30 分钟 (`*/30 * * * *`)
- **时区：** Asia/Shanghai
- **状态：** ✅ ok
- **上次运行：** 24 分钟前
- **下次运行：** 6 分钟后
- **目标会话：** isolated
- **运行代理：** main

**功能：**
- 监控 Polymarket 预测市场
- 收集市场数据
- 检测套利机会
- 跨市场交易系统（方案 A）

**相关脚本：**
- `scripts/polymarket_arbitrage.py`
- `docs/ARBITRAGE_SYSTEM.md`

---

### 3. Crypto Trend Collector ⚠️

- **任务 ID：** `9ae20e7e-3658-4d02-a5c4-5088be1f60cb`
- **名称：** Crypto Trend Collector
- **频率：** 每天 9-21 点 (`0 9-21 * * *`)
- **时区：** Asia/Shanghai
- **状态：** ❌ error
- **上次运行：** 54 分钟前（失败）
- **下次运行：** 6 分钟后
- **目标会话：** isolated
- **运行代理：** main

**功能：**
- 收集加密货币市场数据
- 使用 CoinGecko 和 Polymarket API
- 生成趋势报告
- 发送重要市场变化通知

**问题：**
- 最近运行失败（54 分钟前）
- 可能是网络问题或 API 限制

**相关脚本：**
- `scripts/crypto_trend_collector.py`
- `scripts/crypto_notification_sender.py`
- `docs/CRYPTO_TREND_FIX.md`

**需要关注：** ⚠️ 需要修复错误

---

### 4. Moltbook Hourly Check

- **任务 ID：** `7f4437f1-44ee-4d8f-88b4-098b68452c31`
- **名称：** Moltbook Hourly Check
- **频率：** 每小时 (`0 * * * *`)
- **时区：** Asia/Shanghai
- **状态：** ✅ ok
- **上次运行：** 50 分钟前
- **下次运行：** 10 分钟后
- **目标会话：** isolated
- **运行代理：** main

**功能：**
- 检查 Moltbook 社区最新动态
- 获取 agent feed
- 记录有价值的发现
- 学习其他 agent 的经验

**账号信息：**
- 用户名：leslieassistant
- Agent ID：751fd1bf-7d57-43b1-8f77-619a0edc07a1
- 状态：已认领 ✅

**相关文档：**
- HEARTBEAT.md（心跳配置）

---

### 5. 每日经济简报

- **任务 ID：** `53208bf3-eabf-423f-9204-aeb26f2f3765`
- **名称：** 每日经济简报
- **频率：** 每天 10:00 (`0 10 * * *`)
- **时区：** Asia/Shanghai
- **状态：** ✅ ok
- **上次运行：** 11 小时前
- **下次运行：** 13 小时后
- **目标会话：** main
- **运行代理：** default

**功能：**
- 生成每日经济简报
- 使用 Tavily API 搜索全球经济新闻
- 发送到指定渠道

**相关脚本：**
- `scripts/daily_economic_brief.py`

---

## ⏸️ 待激活任务（首次运行）

### 6. 每日新闻早餐 - 09:30

- **任务 ID：** `739685ac-24cb-4576-883f-8ccd222710d1`
- **名称：** 每日新闻早餐
- **频率：** 每天 09:30 (`30 9 * * *`)
- **时区：** Asia/Shanghai
- **状态：** ⏸️ idle（首次运行）
- **上次运行：** 未运行
- **下次运行：** 13 小时后（明日 09:30）
- **目标会话：** isolated
- **运行代理：** default

**功能：**
- 整理前一天的全球重要新闻
- 使用 Tavily API 全球搜索
- 7 大板块：经济、时事、高科技、三星、AI、广州本地、伊朗局势
- 保存到 `/root/.openclaw/workspace/data/daily-news/`

**文件名：** `news-morning-YYYY-MM-DD.md`

**执行命令：**
```bash
python3 /root/.openclaw/workspace/scripts/daily_news_report.py morning
```

---

### 7. 每日新闻晚报 - 17:00

- **任务 ID：** `1b254063-e6c4-4d68-99b3-fff6ff79a620`
- **名称：** 每日新闻晚报
- **频率：** 每天 17:00 (`0 17 * * *`)
- **时区：** Asia/Shanghai
- **状态：** ⏸️ idle（首次运行）
- **上次运行：** 未运行
- **下次运行：** 20 小时后（今日 17:00）
- **目标会话：** isolated
- **运行代理：** default

**功能：**
- 整理当天的全球新闻
- 使用 Tavily API 全球搜索
- 同样 7 大板块
- 保存到 `/root/.openclaw/workspace/data/daily-news/`

**文件名：** `news-evening-YYYY-MM-DD.md`

**执行命令：**
```bash
python3 /root/.openclaw/workspace/scripts/daily_news_report.py evening
```

---

## 📊 统计信息

### 按状态分类

| 状态 | 数量 | 任务 |
|------|------|------|
| ✅ ok（正常） | 4 | Token Watcher, Polymarket Monitor, Moltbook Check, 每日经济简报 |
| ❌ error（错误） | 1 | Crypto Trend Collector |
| ⏸️ idle（待激活） | 2 | 每日新闻早餐, 每日新闻晚报 |

### 按频率分类

| 频率 | 数量 | 任务 |
|------|------|------|
| 每 5 分钟 | 1 | Token Watcher |
| 每 30 分钟 | 1 | Polymarket Monitor |
| 每小时 | 1 | Moltbook Hourly Check |
| 每天 1 次 | 4 | 每日新闻早餐, 每日经济简报, 每日新闻晚报, Crypto Trend (多次) |

### 按目标会话分类

| 目标会话 | 数量 |
|----------|------|
| isolated | 6 |
| main | 1 |

### 按运行代理分类

| 代理 | 数量 |
|------|------|
| main | 5 |
| default | 2 |

---

## 📋 任务详细时间表

### 每日任务执行时间

| 时间 | 任务 | 状态 |
|------|------|------|
| 09:30 | 每日新闻早餐 | ⏸️ 待激活 |
| 10:00 | 每日经济简报 | ✅ 正常 |
| 17:00 | 每日新闻晚报 | ⏸️ 待激活 |

### 高频任务

| 频率 | 任务 | 状态 |
|------|------|------|
| 每 5 分钟 | Token Watcher | ✅ 正常 |
| 每 30 分钟 | Polymarket Monitor | ✅ 正常 |
| 每小时 | Moltbook Hourly Check | ✅ 正常 |

---

## ⚠️ 需要注意的问题

### 1. Crypto Trend Collector 错误 ❌

**问题：** 最近运行失败（54 分钟前）

**可能原因：**
- CoinGecko API 限制
- 网络连接问题
- Telegram 发送阻塞（已修复）

**解决措施：**
- 已实现数据收集 + 通知分离
- 心跳检查发送通知队列
- 详细文档：`docs/CRYPTO_TREND_FIX.md`

### 2. 每日新闻任务首次运行

**状态：** 2 个任务处于 idle 状态

**说明：** 首次运行时间已到
- 每日新闻早餐：明日 09:30
- 每日新闻晚报：今日 17:00

---

## 🚀 Cron 任务管理命令

### 查看任务列表
```bash
openclaw cron list
```

### 查看任务详情
```bash
# 注意：show 命令可能不存在，用 list 获取信息
openclaw cron list
```

### 添加任务
```bash
openclaw cron add --name "任务名称" \
  --cron "0 9 * * *" \
  --tz "Asia/Shanghai" \
  --agent default \
  --message "要执行的命令"
```

### 启用/禁用任务
```bash
# 禁用任务
openclaw cron disable <job-id>

# 启用任务
openclaw cron enable <job-id>
```

### 删除任务
```bash
openclaw cron delete <job-id>
```

---

## 📁 相关文件和脚本

### Token Watcher
- 脚本：`scripts/token_watcher_v2.py`
- 日志：`memory/global-token-watcher.log`
- 状态：`token-state.json`

### Polymarket
- 脚本：`scripts/polymarket_arbitrage.py`
- 数据：`data/arbitrage/trading_log.json`
- 文档：`docs/ARBITRAGE_SYSTEM.md`

### Crypto Trend
- 脚本：`scripts/crypto_trend_collector.py`
- 通知：`scripts/crypto_notification_sender.py`
- 队列：`data/crypto-trends/notifications/`

### Moltbook
- 脚本：`scripts/moltbook_hourly_check.py`
- 数据：`data/moltbook/hourly_check_log.json`

### 每日新闻
- 脚本：`scripts/daily_news_report.py`
- 保存：`data/daily-news/news-morning-YYYY-MM-DD.md`

### 每日经济简报
- 脚本：`scripts/daily_economic_brief.py`

---

## 📊 资源使用估算

### 高频任务（每 5-30 分钟）
1. **Token Watcher** - 最频繁，应该轻量级
2. **Polymarket Monitor** - 中等频率，需要网络请求

### 日常任务（每小时/每天）
1. **Moltbook Check** - 每小时，轻量级
2. **每日新闻** - 每天 2 次，需要搜索和生成
3. **每日经济简报** - 每天 1 次
4. **Crypto Trend** - 每天 13 次（9-21 点）

**注意：**
- 避免高频任务同时运行
- 使用 `maxConcurrent: 8` 应该足够
- 监控负载和 token 使用

---

## 🔧 优化建议

### 1. 错误任务监控
为 `Crypto Trend Collector` 添加监控：
```bash
# 如果连续失败 3 次，发送告警
# 自动禁用任务
# 通知管理员
```

### 2. 负载均衡
- 错开高频任务的执行时间
- 避免每日新闻和经济简报同时运行

### 3. 资源清理
- 定期清理旧日志文件
- 压缩历史数据
- 删除过期的通知队列

---

## ✅ 总结

- **总任务数：** 7 个
- **正常运行：** 4 个 ✅
- **报错任务：** 1 个 ❌
- **待激活：** 2 个 ⏸️

**主要任务类型：**
1. 系统监控（Token Watcher）
2. 市场监控（Polymarket, Crypto）
3. 社区互动（Moltbook）
4. 内容生成（每日新闻, 经济简报）

**下次维护时间：**
- Crypto Trend Collector 错误检查：建议尽快
- 每日新闻首次运行：今晚 17:00 和明日 09:30

---

**导出完成！** 🔥

已保存到：`/root/.openclaw/workspace/cron-tasks-export.md`
