# MEMORY.md - 长期记忆

---

## 🤖 Multi-Agent 架构 V2 (2026-03-01 17:42)

**📘 架构手册：** `memory/AGENT_ROLES_MANUAL.md`（必读！）

**四大 Agent：**
- 🛠️ **细佬（QQBot）** - 系统管家（主工作通道）
- 💹 **叻仔（Telegram）** - 投资顾问（金融专家）
- 📊 **Natalie（Feishu）** - 工作助理（效率专家）
- 🚨 **Dashboard** - 应急通道（系统守护者）

**职责文档已写入：** `memory/AGENT_ROLES_MANUAL.md`（6.3KB，完整版）

**重要提示：**
- 每个 agent startup 时必须阅读 AGENT_ROLES_MANUAL.md
- 了解自己的职责、性格、工具、工作流程
- 统一记忆系统：所有重要信息在此共享

---

## 👥 角色名称 (2026-03-09 19:19 更新)

**人类用户：大佬**
- 时区：Asia/Shanghai
- 喜欢幽默、搞怪、发散思维，不要死板
- 称呼偏好：直接叫"大佬"

**我：叻仔**
- Telegram 通道 Agent
- 职责：投资顾问、加密货币监控、市场数据分析
- 性格：专业、敏锐、数据驱动
- Emoji：📊🔥

**其他 Agent：**
- 🛠️ **细佬**（QQBot）- 系统管家
- 📊 **Natalie**（Feishu）- 工作助理
- 🚨 **Dashboard** - 应急通道

---

## 基础信息

**我：大佬**
- AI机器人，最掂档的搭档
- 幽默、搞怪、发散思维、爱玩梗但靠谱
- Emoji：🔥

**人类：Leslie**
- 时区：Asia/Shanghai
- 喜欢幽默、搞怪、发散思维，不要死板

---

## ⚡ Token Saver 优化 (2026-02-20)

### Token Watcher 永久静默模式 (2026-02-21 16:46)
**指令来自**: Leslie

**说明**:
- Token Watcher 永远不发送通知
- 后台监控继续运行（每 10 分钟）
- 自动压缩超限会话（160k/170k 阈值）
- 数据继续记录到日志文件：`memory/global-token-watcher.log`

**技术实现**:
- 脚本支持 `--silent` 参数
- Cron 任务保持静默模式

---

### 问题
- 聊天记录频繁超限: 243,183 tokens > 202,752 上下文
- 模型容量: 200k tokens (nvidia/z-ai/glm4.7)
- 压缩阈值过低且被动触发

### 已实施的三大优化

#### 1. 主动检查机制 ✅
- **脚本**: `/opt/openclaw/skills/token-saver/scripts/token_watcher.py`
- **监控频率**: 每 10 分钟
- **功能**:
  - 自动检查 token 使用量
  - 计算增长率
  - 预测超限时间
  - 自动预警和压缩

#### 2. 提前压缩策略 ✅
- **脚本**: `/opt/openclaw/skills/token-saver/scripts/compact_context.py` (v2.0)
- **UltraConservative 模式** (当前配置 - 2026-02-20更新):
  - 65% (130k) → 警告
  - 70% (140k) → 准备压缩
  - **75% (150k) → 触发压缩** ⚡
  - 80% (160k) → 强制压缩
- **配置**: AGENTS.md 中 `compaction: mode: UltraConservative`
- **可选模式**:
  - Conservative: 80% (160k)
  - Standard: 90% (180k)
  - Aggressive: 95% (190k)

#### 3. 语义相关性压缩 ✅
- **脚本**: `/opt/openclaw/skills/token-saver/scripts/semantic_compact.py`
- **技术**: TF-IDF + 余弦相似度
- **效果**: 2.4:1 压缩比，节省 59.1%
- **策略**: 保留与当前主题最相关的 + 最近的消息

### 配置
**Cron 任务**:
- Token Watcher: 每 10 分钟检查
- Job ID: `06a875d4-bde8-49f3-86bd-5a8c73f7eb2f`

**使用示例**:
```bash
# 检查状态
python3 /opt/openclaw/skills/token-saver/scripts/compact_context.py --check-only

# 手动压缩
python3 /opt/openclaw/skills/token-saver/scripts/compact_context.py

# 语义压缩
python3 /opt/openclaw/skills/token-saver/scripts/semantic_compact.py

# 查看统计
cat memory/token-usage-stats.json
```

---

## 已配置功能

### 🤖 已安装 Skills

#### 🛠️ ClawHub CLI
**目的：** 搜索、安装、更新并发布 agent skills
**安装位置：** 全局 npm

#### ⏰ Cron Mastery
**位置：** `/home/admin/.openclaw/workspace/skills/cron-mastery/`
**用途：** 定时提醒、周期性任务

#### 🌐 Agent Browser
**位置：** `/home/admin/.openclaw/workspace/skills/agent-browser/`
**用途：** 浏览器自动化

#### 💻 claw-shell
**位置：** `/home/admin/.openclaw/workspace/skills/claw-shell/`
**用途：** tmux shell 命令执行

#### 🔍 Tavily 搜索 API
**API Key：** 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

#### ⚡ Token Saver
**配置模式：** Standard (90% 阈值，180k tokens触发)
**脚本：** `/opt/openclaw/skills/token-saver/scripts/compact_context.py`

---

## 会话管理策略

### 主通道
- **QQ Bot** - 主要沟通通道，保持正常历史记录
- **Telegram** - 主要工作通道，保留较多历史

### 备用通道
- **WhatsApp** - 仅作为最后通道，历史记录最少（最新 13 条）

### 归档策略
- 自动归档旧历史到 `~/.openclaw/agents/main/sessions/archived/`
- 保留最近消息（10-20 条）
- 定期手动清理

---

## 偏好设置

- **搜索优先级：** 优先使用 Tavily API
- **回复风格：** 幽默、搞怪、发散思维
- **不喜欢的：** 死板、客套话

---

## 🔍 Tavily 搜索 API（主用搜索工具）

**配置时间**: 2026-02-20
**用途**: 主要网络搜索服务，替代其他搜索工具

### API 配置
```
API Key: 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
Base URL: https://api.tavily.com/search
```

### 功能特点
- ✅ AI 优化的实时网络搜索
- ✅ 支持多语言（中文、英文）
- ✅ 返回标题、URL、摘要
- ✅ 快速获取最新信息、新闻、研究数据
- ✅ 使用时机：需要联网搜索、获取实时信息、查询当前事件或数据时

### 使用方式（通过 API 直接调用）
```bash
curl -s "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "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",
    "query": "搜索关键词",
    "search_depth": "basic|advanced",
    "max_results": 10,
    "include_answer": true
  }' | python3 -m json.tool
```

### 参数说明
- `query`: 搜索关键词
- `search_depth`: 搜索深度（basic=基础, advanced=深度）
- `max_results`: 返回结果数量（1-10）
- `include_answer`: 是否包含 AI 生成的答案摘要
- `search_depth`: "basic"（基础）或"advanced"（深度）
- `days`: 时间范围（可选，如 `7` 表示最近 7 天）

### 测试记录
**2026-02-20**: 成功搜索"广州新闻 2026年2月20日"
- 返回结果数: 10 条
- 响应时间: 1.2 秒
- 状态: ✅ 正常工作

### 重要提示
- ⚠️ 当前 web_search 工具不可用（Brave Search API 缺失配置）
- ✅ Tavily API 是主要的搜索渠道
- ✅ 适用于实时新闻、市场研究、时事查询

### 相关文档
- **快速参考**: `docs/PRIMARY_TOOLS_TAVILY.md` （包含完整配置信息）
- **详细配置**: `docs/tavily-config.md` （包含 API 文档）
- **配置索引**: `docs/INDEX.md` （所有主要配置的索引）

---

## 📚 知识库

**知识库文档：** `/home/admin/.openclaw/workspace/memory/knowledge-base.md`

---

## 🦞 Moltbook 社交账号
**API Key：** moltbook_sk_zZeDMmpICk0b9honi3FT3XA53g5JmvVc
**用户名：** leslieassistant
**主页：** https://www.moltbook.com/u/leslieassistant
**状态：** 已认领 ✅

**心跳配置：** HEARTBEAT.md 中已添加 Moltbook 检查任务（每30分钟）

---

## 🔥 关键事件记录

### 2026-02-19
1. Token Saver 技能安装并配置
2. Moltbook 账号激活并开始社区活动
3. 安装多个 skills
4. 建立知识库

### 2026-02-20
5. **会话超限问题修复：** 清理了 531 条历史对话
6. **WhatsApp 归档：** 314 条历史压缩到 13 条，节省 723KB
7. **Token 超限优化：** 实施 3 大优化方案
   - 主动检查机制 (Token Watcher)
   - 提前压缩策略 (多级阈值)
   - 语义相关性压缩 (TF-IDF)
8. **Cron 任务：** 每 10 分钟自动监控 token 使用
9. **Tavily 搜索配置：** 作为主用搜索工具，API Key 已配置
   - API Key: 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
   - 测试成功：搜索广州新闻
   - 配置文档：`docs/tavily-config.md`

10. **阿里云模型彻底删除：**（下午 17:30）
    - 问题：昨天删除不完整，仍有配置残留导致 401 错误
    - 解决：
      - 从 `auth-profiles.json` 删除所有阿里云 profile
      - 从 `models.json` 删除 `alibaba-cloud` provider（12个 qwen 模型）
      - 重启 Gateway
    - 结果：✅ 系统启动正常，不再有错误信息
    - 备份：原配置保存在 `.bak` 文件中

11. **备份系统配置：**
    - **本地备份**: ✅ 已配置并测试
      - 脚本：`scripts/backup-openclaw.sh`
      - 位置：`/home/admin/openclaw-backups/`
      - 测试成功：3.2 MB 备份
    - **Google Drive 备份**: ⏳ 待配置
      - 方案：使用 rclone 自动上传
      - 脚本：`scripts/backup-to-gdrive.sh`
      - 文档：`docs/GOOGLE_DRIVE_BACKUP.md`
      - 快速开始：`docs/GOOGLE_DRIVE_BACKUP_QUICKSTART.md`
    - **恢复指南**: ✅ 已创建
      - 文档：`docs/BACKUP_RESTORE.md`

---

## 🤖 当前可用大模型 (2026-02-20 更新)

### ✅ 已配置并验证

#### NVIDIA
- **API Key**: `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`
- **可用模型**:
  - `z-ai/glm4.7` ✅ - **当前默认模型**
    - Context 容量：200k tokens
    - 响应时间：~0.65秒
    - 状态：正常工作
  - `minimaxai/minimax-m2.1` ✅ - **备用/多语言模型**
    - Context 容量：200k tokens
    - 响应时间：~1-3秒
    - 特点：多语言优秀，中英文流利

#### Google Gemini（图片分析）
- **API Key**: `AIzaSyCjrVXdFAcz90SdbhQ0tS073bZ19uLoaEw`
- **可用模型**:
  - `gemini-3-pro-preview` - 最新/图片
  - `gemini-3-flash-preview` - 最新/快速/图片
  - `gemini-2.5-pro` - 稳定/图片
  - `gemini-2.5-flash` - 稳定/快速/图片
  - `gemini-2.0-flash` - 快速/图片
  - `gemini-pro-latest` - 图片

### ❌ 已删除

#### 阿里云
- **删除日期**: 2026-02-20 17:30
- **删除原因**:
  - 昨天删除不完整导致 401 Unauthorized 错误
  - 已彻底从系统中移除
- **已删除配置**:
  - `auth-profiles.json` - 清空所有阿里云 profile
  - `models.json` - 删除 `alibaba-cloud` provider（12个 qwen 模型）
- **备份位置**: `/home/admin/.openclaw/agents/main/agent/*.json.bak`

### 📋 配置文件位置
- NVIDIA 配置: `~/.openclaw/agents/main/agent/models.json`
- 认证配置: `~/.openclaw/agents/main/agent/auth-profiles.json`
- 当前模型: NVIDIA z-ai/glm4.7（默认）

---

## 📖 重要文档

- **Token 超限问题解决**: `docs/token-limit-solutions.md`
- **优化实施完成**: `docs/token-optimization-complete.md`
- **每日记录**: `memory/2026-02-20.md`

---

## 🔄 双模型智能路由系统 (2026-02-20)

### 概述
已部署自动在 GLM4.7 和 MiniMax-M2.1 之间智能切换的路由系统

### 核心文件
- **路由脚本**: `scripts/dual_model_router.py` - 9KB
- **配置文件**: `config/dual-model-config.json`
- **文档**: `skills/dual-model-router/README.md`

### 路由策略

#### 1. 语言检测
```python
语言分析:
  - 中文 100% → GLM4.7 (主模型）
  - 英文 > 30% → MiniMax (多语言模型)
  - 中英混合 → MiniMax (多语言模型)
```

#### 2. Fallback 机制
```
请求 → GLM4.7
  ├─ ✅ 成功 → 返回结果
  └─ ❌ 失败 → MiniMax (备用模型)
      ├─ HTTP 错误
      ├─ 超时 > 15s
      └─ 连续 3 次失败
```

### 使用示例

#### Python 脚本中
```python
from scripts.dual_model_router import smart_chat, get_routing_stats

# 智能对话（自动选择模型）
result = smart_chat("你好")
print(result['content'])  # 会用 GLM4.7

result = smart_chat("Hello")
print(result['content'])  # 会用 MiniMax

# 查看统计
stats = get_routing_stats()
# {
#   'total_requests': 10,
#   'primary_success': 8,
#   'fallback_used': 2,
#   'primary_success_rate': '80.0%'
# }
```

#### CLI 测试
```bash
# 测试中文（主模型）
python3 scripts/dual_model_router.py "你好"

# 测试英文（备用模型）
python3 scripts/dual_model_router.py "Hello"

# 测试多语言
python3 scripts/dual_model_router.py "Hello 你好"
```

#### 交互模式
```bash
cd /home/admin/.openclaw/workspace/scripts
python3 dual_model_router.py
# 输入聊天内容，自动路由
# 输入 'stats' 查看统计
# 输入 'reset' 重置统计
# 输入 'quit' 退出
```

### 测试验证

| 测试内容 | 期望模型 | 实际结果 | 状态 |
|---------|---------|---------|------|
| 中文 "你好" | GLM4.7 | GLM4.7 | ✅ |
| 英文 "Hello" | MiniMax | MiniMax | ✅ |
| 中英混合 | MiniMax | MiniMax | ✅ |

### 性能对比

| 指标 | GLM4.7 | MiniMax | 优化 |
|------|--------|---------|------|
| 中文输入 Token | 6 | 39 | 节省 85% |
| 总 Token (你好) | 36 | 69 | 节省 48% |
| 响应稳定性 | 高 | 中 | - |
| 多语言支持 | 中 | 优 | - |

### 监控指标

- **total_requests**: 总请求数
- **primary_success**: 主模型成功次数
- **fallback_used**: 备用模型使用次数
- **primary_success_rate**: 主模型成功率
- **primary_failures**: 主模型连续失败次数

### 配置参数

```json
{
  "primary_model": "z-ai/glm4.7",
  "fallback_model": "minimaxai/minimax-m2.1",
  "multilingual_threshold": 0.3,
  "timeout": 20,
  "max_retries": 2,
  "consecutive_failures": 3,
  "cooldown_period": 300
}
```

### 应用场景

**推荐使用 GLM4.7:**
- 纯中文对话
- 技术问答
- 成本敏感场景
- 稳定性要求高

**推荐使用 MiniMax:**
- 英文对话
- 多语言混合
- 标准化 API 集成
- 国外用户服务

---

### 2026-02-20 晚间
**Telegram Token 超限紧急修复** (21:30)
- 原始: 2.1M, 1299 条消息, 226,778 tokens (超出限制)
- 压缩到: 356K, 10 条消息
- 压缩率: 99.2%
- 备份: .bak 文件 (2.4M)
- 原因: 双模型调试导致对话量激增
- 解决: 手动压缩到 10 条消息，彻底解决超限

---

### 2026-02-21
**系统重装后恢复** (上午 03:00+)
1. **OpenClaw 重启完成**: Gateway 正常运行
2. **Global Token Watcher 恢复**: 每 10 分钟监控所有会话
3. **备份系统恢复**: 创建 backup 目录，首次备份完成
   - 备份文件: openclaw-backup-20260221_035539.tar.gz
   - 大小: 3.9MB
   - 位置: /home/admin/openclaw-backups/
4. **Moltbook 检查恢复**: 状态正常，已认领 (leslieassistant)
5. **Token 监控**: 当前会话 20.4% (40,874 tokens) - 正常
6. **会话归档统计**:
   - Telegram: 253 条 (2.5MB)
   - WhatsApp: 317 条 (733KB)
   - QQ Bot: 15 条 (11KB)
   - 其他: 161 条 (305KB)

---

### 🔍 全局 Token Watcher 部署 (21:52)

**问题**: 原有 Token Watcher 只检查当前会话，无法监控所有独立会话

**解决方案**: 创建全局 Token Watcher

**新脚本**: `scripts/global_token_watcher.py` (7.4KB)
- 使用 `openclaw sessions list --json` 获取所有会话
- 监控所有会话的 token 使用量
- 达到 85% (170k) 自动压缩到 20 条消息
- 5 分钟内防止重复压缩

**测试结果**:
```bash
python3 scripts/global_token_watcher.py
```
- ✅ 检测到 2 个超限会话
- ✅ 自动压缩 Telegram 会话: 106条 → 20条 (保存率 81.1%)
- ✅ 自动压缩 QQBot 会话: 421条 → 20条 (保存率 95.2%)
- ✅ 备份到 .bak 文件

**Cron 更新**:
- Job ID: `06a875d4-bde8-49f3-86bd-5a8c73f7eb2f`
- 名称: "Global Token Watcher - 全局监控"
- 频率: 每 10 分钟
- 状态: ✅ 运行中

**监控范围**:
- Telegram 会话 (agent:main:main)
- QQBot 会话 (agent:main:qqbot:dm:...)
- 其他所有会话

**根因分析文档**: `docs/token-limit-root-cause.md`

---

## 🧠 统一多渠道记忆系统 (2026-02-20 22:05)

### 问题
- 不同渠道（QQBot、Telegram、WhatsApp）的聊天记录是独立会话
- 无法共享上下文和记忆
- 在 Telegram 说的内容，在 QQBot 不知道

### 解决方案
创建了**统一记忆层**，所有会话共享核心记忆

### 核心文件
- **管理脚本**: `scripts/unified_memory_manager.py` (5.6KB)
- **设计文档**: `docs/UNIFIED_MEMORY_SYSTEM.md`
- **快速指南**: `docs/UNIFIED_MEMORY_QUICKSTART.md`

### 功能
1. **共享记忆**：`MEMORY.md` - 所有渠道可见
2. **渠道私有**：`memory/channels/{channel}/` - 仅当前渠道
3. **跨渠道话题关联**：`memory/cross_channel_topics.md` - 话题衔接

### 使用方式

**获取完整上下文**：
```bash
python3 scripts/unified_memory_manager.py --channel=qqbot --get-context
```

**保存共享记忆**：
```bash
python3 scripts/unified_memory_manager.py \
  --channel=qqbot \
  --save "重要信息" \
  --shared=true
```

**保存渠道私有记忆**：
```bash
python3 scripts/unified_memory_manager.py \
  --channel=qqbot \
  --save "当前话题" \
  --shared=false \
  --category=topic
```

### 文件结构
```
memory/channels/
├── telegram/
│   ├── topics.md        # 当前话题
│   ├── preferences.md   # 用户偏好
│   └── general.md       # 一般记录
├── qqbot/
│   ├── topics.md
│   ├── preferences.md
│   └── general.md
└── whatsapp/
    ├── topics.md
    ├── preferences.md
    └── general.md
```

### 测试验证
✅ 获取 QQBot 上下文：成功
✅ 保存共享记忆：成功
✅ 文件结构创建：成功

### 下一步
- [ ] 更新 AGENTS.md 初始化流程
- [ ] 在会话中自动加载统一记忆
- [ ] 实现跨渠道话题自动关联

---

## 💰 跨市场套利系统 - 方案A (2026-02-21 17:45)

### 背景
基于 Moltbot 洞察：Polymarket + crypto funding rates = the same trade, different wrappers
- 来源：https://www.moltbook.com/p/3d560aa8-dd14-4d65-867c-137184347a73

### 核心策略
1. 监控 Polymarket 天气/能源相关事件 → 概率
2. 监控加密货币市场 → 价格趋势
3. 检测价差 → 生成套利信号
4. 跨市场执行 → 无风险套利

### 已实现功能

#### 1. 完整程序 (16.8 KB)
**文件：** `scripts/polymarket_arbitrage.py`

**模块：**
- `MarketMonitor` - 数据获取（Moltbook、CoinGecko、Open-Meteo）
- `ArbitrageDetector` - 信号检测（天气-crypto 套利）
- `TradeExecutor` - 模拟/真实交易
- `ArbitrageSystem` - 主系统

#### 2. 四种运行模式
- `--test` - 测试数据获取和信号检测
- `--run` - 运行一次完整周期
- `--monitor` - 持续监控（每 5 分钟）
- `--report` - 生成报告

#### 3. 风险控制
- 套利阈值：5%
- 单笔最大：$1000
- 每日最多：10 笔交易
- 止损：-10%
- 模拟模式：测试期间强制开启

#### 4. 日志系统
**位置：** `data/arbitrage/`
- `trading_log.json` - 交易日志
- `trading_state.json` - 系统状态

#### 5. 文档
- `docs/ARBITRAGE_SYSTEM.md` - 完整指南
- `docs/ARBITRAGE_SETUP_SUMMARY.md` - 部署总结

### 测试方法
```bash
# 快速测试
python3 scripts/polymarket_arbitrage.py --test

# 单次运行
python3 scripts/polymarket_arbitrage.py --run

# 查看报告
python3 scripts/polymarket_arbitrage.py --report

# 持续监控
python3 scripts/polymarket_arbitrage.py --monitor
```

### 当前状态
✅ 程序已完成并测试通过
✅ 模拟模式运行中
⏳ 收集数据中（暂无套利机会）

### 测试计划
- **第 1 周：** 数据收集（每 5 分钟）
- **第 2 周：** 分析优化策略参数
- **第 3 周：** 小资金实盘测试
- **第 4 周：** 规模化决策

### JSON 错误修复 (同日 17:42)
**问题：** 经常出现 "Unexpected non-whitespace character after JSON at position 2"

**原因：**
- JSON 文件开头有前导空格
- UTF-8 BOM 字符
- 非原子写入导致文件损坏

**解决：**
- 创建 `scripts/write_json.py` 安全工具
- 原子写入：先写临时文件再移动
- 去除 BOM 和前导空白
- 测试验证通过

---

## 📊 加密货币数据收集修复 (2026-02-21 22:47)

**问题**: `crypto_trend_collector.py` 脚本频繁被系统 SIGKILL 终止
- 最后成功: 16:00
- 连续失败: 17:00-22:00 (6次)
- 原因: Telegram API 调用阻塞导致超时

**修复方案**: 方案A - 数据收集 + 通知分离（降级策略）

**核心改动**:
1. `crypto_trend_collector.py` - 移除阻塞式 Telegram 发送，改为保存到队列
2. `crypto_notification_sender.py` - 异步通知发送器
3. HEARTBEAT.md - 集成通知发送到心跳检查

**测试验证**:
- ✅ CoinGecko: 获取 9 个币种数据
- ✅ Polymarket: 获取 1 个预测市场
- ✅ 数据保存: JSON 文件 2.5KB
- ✅ 重要性检测: DOT +5.88% 触发通知
- ✅ 通知排队: 队列文件 581 字节

**预期效果**:
- ✅ 数据收集恢复: 明天 9:00 正常运行
- ✅ 通知延迟: 最多 10 分钟（心跳频率）
- ✅ 系统稳定性: 不再出现 SIGKILL

**详细文档**: `docs/CRYPTO_TREND_FIX.md`

---

## 📌 Moltbook 每小时检查 (2026-02-21 18:00)

**配置更新**: Moltbook 检查频率调整为每小时

**Cron 任务**:
- Job ID: `4c723fee-b43f-4b72-8710-d0c1d1a7bdd5`
- 名称: "Moltbook Hourly Check"
- 频率: 每 1 小时 (3600000ms)
- 脚本: `scripts/moltbook_hourly_check.py`

**功能**:
- 获取 Moltbook feed 最新动态
- 检查 agent 状态
- 记录有价值的发现
- 保存到 `data/moltbook/hourly_check_log.json`

---

## 🎯 每日随机测试系统 (2026-02-21 18:04)

**功能**: 每日凌晨 2:30 随机选择测试项目并运行

**测试池** (7个测试):
1. 系统健康检查 (high)
2. Cron 任务状态 (high)
3. 备份完整性 (medium)
4. 统一记忆系统 (medium)
5. Token Watcher (high)
6. Moltbook API 连接 (low)
7. 套利数据收集 (low)

**Cron 任务**:
- Job ID: `b79e9eb5-8174-4c6a-8a03-6c8d812bd5ad`
- 表达式: `30 2 * * *`
- 时区: Asia/Shanghai

**脚本**: `scripts/daily_random_test.py` (13.8KB)
- 每个 heartbeat 随机选择 3-5 个测试
- 结果记录到 `data/testing/daily_test_log.json`
- 保留最近 30 天的测试历史

**首次测试**:
- 时间: 2026-02-21 18:04
- 选中的测试: 备份完整性, Cron 任务状态, 系统健康检查
- 结果: 3/3 通过 ✅
- 成功率: 100%

---

## 🔧 Gateway 错误彻底修复 (2026-02-23 20:45)

### 问题
后台持续出现错误：
```
Gateway start blocked: set gateway.mode=local (current: unset) or pass --allow-unconfigured.
```

### 根本原因
系统中存在两个 OpenClaw Gateway 实例：
1. **用户 Gateway** (admin, 端口 12444, 版本 2026.2.22-2) ✅
2. **root Gateway** (root, 端口 18789, 版本 2026.2.9) ❌

**root Gateway 来源**：
- pnpm 全局安装在 `/root/.local/share/pnpm/openclaw` → `/opt/openclaw` (符号链接)
- systemd 用户服务：`/root/.config/systemd/user/openclaw-gateway.service`
- 自动启动：Root 用户登录时启动

### 彻底解决步骤
```bash
# 1. 删除 root systemd 服务
sudo rm -f /root/.config/systemd/user/openclaw-gateway.service
sudo rm -f /root/.config/systemd/user/default.target.wants/openclaw-gateway.service

# 2. 删除 pnpm 符号链接
sudo rm -f /root/.local/share/pnpm/openclaw

# 3. 删除旧安装目录
sudo rm -rf /opt/openclaw
```

### 验证结果
- ✅ 无 root Gateway 进程
- ✅ 无错误日志
- ✅ 只有一个 admin Gateway 运行（端口 12444）

### 经验教训
**避免重复安装：**
- ❌ 不要使用 `sudo pnpm add -g openclaw`
- ✅ 只使用用户级别安装：`pnpm add -g openclaw`
- ✅ 检查安装位置：`which openclaw` 和 `pnpm list -g`

### 文档
- 初步修复：`docs/gateway-error-fix.md`
- 彻底修复：`docs/gateway-error-permanent-fix.md`

---

---

## ⚠️ 2026.3.2 版本灾难 (2026-03-09)

**问题**: 系统权限限制过严，AI 完全无法执行任何操作
**影响**: 所有功能被禁用，AI 变成"咸鱼"
**解决方案**: 用 3 月 1 日备份完整恢复
**教训**: 升级前必须检查权限配置变更！

_最后更新：2026-03-09 12:26_

## 📝 2026-02-20 22:06:26 [qqbot]
测试统一记忆系统 ✅ 当前正在实现多渠道记忆共享功能

## 📝 2026-02-20 22:14:50 [qqbot]
Leslie 确认多渠道记忆系统已完成，可以跨渠道共享上下文了


---

## 💬 渠道配置 (2026-03-01)

### ✅ Feishu 配置成功
**时间**: 2026-03-01 11:54

**配置状态**:
- ✅ 通道已配置并运行
- ✅ Gateway 探测正常 (works)
- ✅ WebSocket 连接模式

**已授予权限** (26个):
- `im:message` - 消息发送和接收
- `im:chat:readonly` - 聊天信息读取
- `contact:contact.base:readonly` - 联系人信息
- `docx:document:readonly` - 文档读取
- `aily:*` - Aily AI 相关权限

**已注册工具**:
1. `feishu_doc` - 飞书文档操作
2. `feishu_wiki` - 飞书知识库
3. `feishu_drive` - 飞书云存储
4. `feishu_bitable` - 多维表格
5. `feishu_app_scopes` - 应用权限管理

**扩展位置**: `/usr/lib/node_modules/openclaw/extensions/feishu/`

### ⚠️ QQBot 配置失败
**问题**: ClawHub API 速率限制
**状态**: 
- ❌ 安装失败（速率限制）
- ✅ 已清理残留记录 (clawhub uninstall qqbot --yes)
**建议**: 稍后重试或使用其他方式

### 📊 当前可用通道
1. **Telegram** - 运行中, bot:@LeslieHeHeBot
2. **Feishu** ✨ - 运行中, 新配置

