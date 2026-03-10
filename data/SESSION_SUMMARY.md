# 📊 会话分类总结报告

**生成时间**: 2026-03-09 18:01
**总会话数**: 61 个

---

## 📈 核心统计

| 指标 | 数值 |
|------|------|
| 总会话数 | 61 个 |
| 总存储空间 | 704.04 KB (0.69 MB) |
| 平均每个会话 | 11.54 KB |
| 分类脚本 | `scripts/classify_sessions.py` |
| 详细数据 | `data/session_classifications.json` |

---

## 📦 Top 10 最大会话

| 排名 | 会话 ID | 大小 | 消息数 |
|------|--------|------|--------|
| 1 | a0117695... | 112.54 KB | 22 条 |
| 2 | af47d579... | 105.96 KB | 17 条 |
| 3 | 617ef6d8... | 79.71 KB | 32 条 |
| 4 | 4d4993be... | 36.85 KB | 19 条 |
| 5 | 7d5efe46... | 18.00 KB | 20 条 |
| 6 | 1406085e... | 17.73 KB | 22 条 |
| 7 | b24ba14d... | 14.99 KB | 20 条 |
| 8 | b2c4bb35... | 14.37 KB | 12 条 |
| 9 | 8ca8aa3f... | 12.76 KB | 18 条 |
| 10 | 70fada6e... | 12.34 KB | 14 条 |

---

## 🏷️ 会话类型分布

当前所有会话均分类为 **normal** (正常对话会话)

**原因**: 大部分会话是 Cron 任务和系统会话，消息模式相似

---

## 📅 时间分布

根据创建时间分析：

### 活跃会话 (最近 7 天)
- 2026-03-09: 多个会话 (今日)
- 2026-03-01: Cron 任务会话

### 历史会话
- 大部分会话创建于 2026-03-01 至 2026-03-09 期间

---

## 🔍 会话 ID 模式分析

### Cron 任务会话
通过 sessions_list API 识别的 Cron 会话：
- `357810bf-9fa4-4477-ad52-60bfd6e6a003` - Token Watcher
- `b2c4bb35-97d5-4a36-b57a-99f028ac68cf` - 每日新闻晚报
- `e54bb7b7-0fdf-416b-af2f-d12dc417a97b` - 每日新闻早餐
- `70fada6e-daf3-41f4-869b-5c4175d4e68a` - Moltbook Hourly Check
- `35504610-b82f-48d8-b45c-e1b04f5a7311` - Polymarket Monitor
- `4971c8b3-958a-4f5d-9008-4aa0d7b91a1e` - Crypto Trend Collector

### 渠道会话
- `617ef6d8-e1cf-4452-b495-d085c0f2f39f` - QQBot (当前活跃)
- `4d4993be-4814-46b6-beaa-80523eba25ba` - Feishu
- `af47d579-b5f2-47fa-b146-4e32550324b9` - 主会话
- `2ea5280b-42d0-4e90-8b4f-fe825603f3ef` - Telegram

---

## 💡 优化建议

### 1. 会话清理
- 总存储空间仅 0.69 MB，无需紧急清理
- 可考虑归档超过 30 天的旧会话

### 2. 分类优化
- 当前分类脚本需要改进渠道识别逻辑
- 建议根据会话标签 (label) 进行分类

### 3. 监控建议
- 定期运行分类脚本监控会话增长
- 设置 token 使用量告警阈值

---

## 📝 相关文件

- **分类脚本**: `/root/.openclaw/workspace/scripts/classify_sessions.py`
- **详细数据**: `/root/.openclaw/workspace/data/session_classifications.json`
- **会话目录**: `/root/.openclaw/agents/main/sessions/`
- **Workspace 备份**: `/root/.openclaw/workspace/*.jsonl`

---

## ✅ 下一步

1. ✅ 创建 BOOTSTRAP.md - 激活各 Agent
2. ✅ 自动分类 61 个会话
3. ⏳ 配置各 Agent 职责
4. ⏳ 测试跨 Agent 通信

---

**报告生成**: 2026-03-09 18:01:37
**分类工具版本**: v1.0
