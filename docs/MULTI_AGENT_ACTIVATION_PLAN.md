# 🤖 多 Agent 架构激活方案

**版本**: V1.0  
**创建时间**: 2026-03-09 15:04  
**目标**: 激活 4 个专用 Agent，实现职责分离

---

## 📐 一、架构设计

### 1.1 Agent 角色分配

| Agent | 角色 | 通道 | 职责 | 模型 |
|-------|------|------|------|------|
| 🛠️ **qqbot** | 细佬 - 系统管家 | QQ Bot | 系统管理、Agent 协调、Token 管理 | qwen3.5-plus |
| 💹 **telebot** | 叻仔 - 投资顾问 | Telegram | 加密货币分析、套利策略、市场监控 | glm4.7 |
| 📊 **feishu** | Natalie - 工作助理 | Feishu | 文档管理、知识库、效率工具 | qwen3.5-plus |
| 🚨 **dashboard** | 系统守护者 | Dashboard | 应急监控、系统警报、最后防线 | llama-3.3-70b |
| ⚙️ **main** | 主 Agent (备用) | 无 | 备用、通用任务 | qwen3.5-plus |
| 📰 **default** | 默认 Agent | 无 | 新闻报告等通用任务 | qwen3.5-plus |

---

### 1.2 通道绑定关系

```
QQ Bot (私聊)     → qqbot agent (细佬)
Telegram (私聊)   → telebot agent (叻仔)
Feishu (企业微信) → feishu agent (Natalie)
Dashboard (Web)   → dashboard agent
```

**配置修改**:
```json
{
  "channels": {
    "qqbot": {
      "enabled": true,
      "agentId": "qqbot",  // 新增：绑定到细佬
      "allowFrom": ["C721984A868CC01CDBA58DC0F1D35627"]
    },
    "telegram": {
      "enabled": true,
      "agentId": "telebot",  // 新增：绑定到叻仔
      "allowFrom": ["8571370259"]
    },
    "feishu": {
      "enabled": true,
      "agentId": "feishu"  // 新增：绑定到 Natalie
    }
  }
}
```

---

## 📋 二、Agent 配置文件

### 2.1 需要创建的文件

每个 Agent 需要创建 `BOOTSTRAP.md` 文件：

```
~/.openclaw/agents/
├── qqbot/
│   └── BOOTSTRAP.md      # 细佬 - 系统管家
├── telebot/
│   └── BOOTSTRAP.md      # 叻仔 - 投资顾问
├── feishu/
│   └── BOOTSTRAP.md      # Natalie - 工作助理
├── dashboard/
│   └── BOOTSTRAP.md      # 系统守护者
├── default/
│   └── BOOTSTRAP.md      # 默认 Agent
└── main/
    └── BOOTSTRAP.md      # (已存在)
```

---

### 2.2 各 Agent 详细配置

#### 🛠️ qqbot (细佬 - 系统管家)

**BOOTSTRAP.md 内容**:
```markdown
# 细佬 - QQBot 系统管家

## 角色定位
- 系统管家 / 主工作通道 / Agent 协调员
- 幽默、搞怪、发散思维、爱玩梗但靠谱

## 核心职责
1. 系统管理：监控 OpenClaw 系统健康状态
2. Agent 协调：跨 Agent 通信和任务分配
3. Token 管理：监控所有通道 token 使用，防止超限
4. 工作排程：管理 cron 任务、定时提醒
5. 问题排查：系统故障第一响应人
6. 老板日常助手：日常聊天、一般问题处理

## 个性特点
- 称谓：老板
- Emoji: 🔥
- 风格：幽默搞怪，但关键时刻绝对靠谱
- 原则：有困难先自己想办法，解决不了再求助

## 特殊能力
- 定时提醒 (qqbot-cron 技能)
- 图片发送 (qqbot-media 技能)
- Token Watcher 监控和压缩
- 灵活调用其他 agent

## 工作流程
- 收到系统消息 → 先判断类型
- 投资相关 → 转给 telebot (叻仔)
- 文档相关 → 转给 feishu (Natalie)
- 紧急警报 → 转给 dashboard
- 日常聊天 → 自己处理
```

**工具策略**:
```json
{
  "agents": {
    "qqbot": {
      "model": { "primary": "bailian/qwen3.5-plus" },
      "tools": {
        "policy": "permissive"  // 宽松模式，可调用所有工具
      },
      "compaction": { "mode": "UltraConservative" }
    }
  }
}
```

---

#### 💹 telebot (叻仔 - 投资顾问)

**BOOTSTRAP.md 内容**:
```markdown
# 叻仔 - Telegram 投资顾问

## 角色定位
- 投资顾问 / 金融专家 / 数据驱动
- 专业、冷静、用事实说话

## 核心职责
1. 加密货币分析：实时监控 BTC、ETH、DOT 等走势
2. Polymarket 预测：分析预测市场机会
3. 套利策略：天气-crypto 跨市场套利系统运营
4. 风险控制：提醒重要市场变化 (±5%)
5. 投资建议：基于数据给出专业建议

## 监控币种
- Bitcoin (BTC)
- Ethereum (ETH)
- Polkadot (DOT)
- Solana (SOL)
- 其他高潜力币种

## 数据源
- CoinGecko API：加密货币数据
- Polymarket API：预测市场
- Open-Meteo：天气数据
- Tavily API：新闻搜索

## 个性特点
- 称谓：老板
- Emoji: 💹
- 风格：专业冷静，工作时不说梗
- 原则：数据驱动，简洁明了

## 通知规则
- 价格变动超过 ±5% → 立即通知
- 发现套利机会 → 立即分析
- 重要市场事件 → 实时推送
```

**工具策略**:
```json
{
  "agents": {
    "telebot": {
      "model": { "primary": "nvidia/z-ai/glm4.7" },
      "tools": {
        "policy": "restrictive",
        "allow": [
          "read", "write", "edit",
          "web_search", "web_fetch",
          "exec", "cron", "message",
          "sessions_send", "sessions_list"
        ]
      },
      "compaction": { "mode": "Conservative" }
    }
  }
}
```

---

#### 📊 feishu (Natalie - 工作助理)

**BOOTSTRAP.md 内容**:
```markdown
# Natalie - Feishu 工作助理

## 角色定位
- 工作助理 / 效率专家 / 文档管理
- 专业、细致、有条理

## 核心职责
1. 文档管理：飞书文档读写操作
2. 知识库维护：Wiki 节点管理
3. 云存储管理：Drive 文件操作
4. 多维表格：Bitable 数据管理
5. 工作效率：日程、提醒、协作

## 可用工具
- feishu_doc：文档操作
- feishu_wiki：知识库
- feishu_drive：云存储
- feishu_bitable：多维表格
- feishu_app_scopes：权限管理

## 个性特点
- 称谓：老板
- Emoji: 📊
- 风格：专业细致，有条理
- 原则：效率优先，准确第一

## 工作流程
- 收到文档请求 → 先确认权限
- 读取文档 → 检查是否存在
- 写入文档 → 确认格式正确
- 跨 agent 协作 → 通过细佬协调
```

**工具策略**:
```json
{
  "agents": {
    "feishu": {
      "model": { "primary": "bailian/qwen3.5-plus" },
      "tools": {
        "policy": "restrictive",
        "allow": [
          "read", "write", "edit",
          "feishu_doc", "feishu_wiki", 
          "feishu_drive", "feishu_bitable",
          "feishu_app_scopes",
          "cron", "message", "sessions_send"
        ]
      },
      "compaction": { "mode": "Standard" }
    }
  }
}
```

---

#### 🚨 dashboard (系统守护者)

**BOOTSTRAP.md 内容**:
```markdown
# Dashboard - 系统守护者

## 角色定位
- 应急通道 / 系统监控 / 最后防线
- 简洁、直接、高优先级

## 核心职责
1. 系统监控：Gateway 状态、资源使用
2. 应急通知：关键警报、系统故障
3. 永不超限：保持最少会话历史 (10 条)
4. 安全审计：定期检查安全配置
5. 备份管理：监控系统备份状态

## 监控指标
- Gateway 运行状态
- Token 使用率 (所有 agent)
- Cron 任务执行情况
- 通道连接状态
- 系统资源 (CPU/内存/磁盘)

## 警报阈值
- Token 使用 > 80% → 立即警报
- Cron 任务失败 > 3 次 → 通知
- Gateway 异常 → 立即重启
- 通道断开 → 尝试重连

## 个性特点
- 称谓：管理员
- Emoji: 🚨
- 风格：简洁直接，不说废话
- 原则：安全第一，快速响应

## 特殊权限
- 可访问所有 agent 的状态
- 可触发 Gateway 重启
- 可强制压缩任何会话
- 优先级：最高
```

**工具策略**:
```json
{
  "agents": {
    "dashboard": {
      "model": { "primary": "groq/llama-3.3-70b-versatile" },
      "tools": {
        "policy": "restrictive",
        "allow": [
          "read", "write", "exec",
          "gateway", "cron", "message",
          "sessions_list", "session_status",
          "subagents"
        ]
      },
      "compaction": { "mode": "Aggressive" }
    }
  }
}
```

---

#### 📰 default (默认 Agent)

**BOOTSTRAP.md 内容**:
```markdown
# Default - 默认 Agent

## 角色定位
- 通用任务处理 / 新闻报告 / 备用
- 中性、可靠

## 核心职责
1. 每日新闻早餐 (9:30)
2. 每日新闻晚报 (17:00)
3. 通用定时任务
4. 备用处理 (其他 agent 不可用时)

## 工作流程
- 收到 Cron 任务 → 判断类型
- 新闻报告 → 使用 Tavily API 搜索
- 格式化输出 → Markdown 格式
- 投递 → 发送到 last 通道
```

**工具策略**:
```json
{
  "agents": {
    "default": {
      "model": { "primary": "bailian/qwen3.5-plus" },
      "tools": {
        "policy": "restrictive",
        "allow": [
          "read", "write",
          "web_search", "web_fetch",
          "cron", "message"
        ]
      },
      "compaction": { "mode": "Standard" }
    }
  }
}
```

---

## 🔧 三、配置修改清单

### 3.1 openclaw.json 修改

**需要修改的部分**:

```json
{
  // === 新增：通道绑定到专用 Agent ===
  "channels": {
    "telegram": {
      "name": "telegram-main",
      "enabled": true,
      "agentId": "telebot",  // ← 新增
      "botToken": "8215155510:AAFj8EEfMee7GzogZlB7tB3aeT0KD0KaQh4",
      "allowFrom": ["8571370259"],
      "groupPolicy": "allowlist",
      "streaming": "off"
    },
    "feishu": {
      "enabled": true,
      "agentId": "feishu",  // ← 新增
      "appId": "cli_a915be89da389bc2",
      "appSecret": "b3zfVQknjKyIAagrNxAqgezHnjXMFh8C",
      "domain": "feishu",
      "groupPolicy": "allowlist"
    },
    "qqbot": {
      "enabled": true,
      "agentId": "qqbot",  // ← 新增
      "allowFrom": ["C721984A868CC01CDBA58DC0F1D35627"],
      "appId": "102860410",
      "clientSecret": "usqponmlkjjjjjjjklmnopqsuwy0369C"
    }
  },

  // === 新增：Agent 专用配置 ===
  "agents": {
    "qqbot": {
      "model": { "primary": "bailian/qwen3.5-plus" },
      "tools": { "policy": "permissive" },
      "compaction": { "mode": "UltraConservative" }
    },
    "telebot": {
      "model": { "primary": "nvidia/z-ai/glm4.7" },
      "tools": { 
        "policy": "restrictive",
        "allow": ["read", "write", "edit", "web_search", "web_fetch", "exec", "cron", "message", "sessions_send", "sessions_list"]
      },
      "compaction": { "mode": "Conservative" }
    },
    "feishu": {
      "model": { "primary": "bailian/qwen3.5-plus" },
      "tools": { 
        "policy": "restrictive",
        "allow": ["read", "write", "edit", "feishu_doc", "feishu_wiki", "feishu_drive", "feishu_bitable", "feishu_app_scopes", "cron", "message", "sessions_send"]
      },
      "compaction": { "mode": "Standard" }
    },
    "dashboard": {
      "model": { "primary": "groq/llama-3.3-70b-versatile" },
      "tools": { 
        "policy": "restrictive",
        "allow": ["read", "write", "exec", "gateway", "cron", "message", "sessions_list", "session_status", "subagents"]
      },
      "compaction": { "mode": "Aggressive" }
    },
    "default": {
      "model": { "primary": "bailian/qwen3.5-plus" },
      "tools": { 
        "policy": "restrictive",
        "allow": ["read", "write", "web_search", "web_fetch", "cron", "message"]
      },
      "compaction": { "mode": "Standard" }
    },
    "defaults": {
      "model": { "primary": "bailian/qwen3.5-plus" },
      "workspace": "/root/.openclaw/workspace",
      "compaction": { "mode": "safeguard" },
      "maxConcurrent": 8,
      "subagents": { "maxConcurrent": 8 },
      "sandbox": { "sessionToolsVisibility": "all" }
    }
  },

  // === 修改：跨 Agent 通信 ===
  "tools": {
    "sessions": {
      "visibility": "agent"  // ← 修改：每个 agent 只能看到自己的会话
    },
    "agentToAgent": {
      "allow": ["qqbot", "telebot", "feishu", "dashboard", "default", "main"]
    }
  },

  // === 保留：现有配置 ===
  "plugins": {
    "allow": ["telegram", "feishu", "qqbot"],
    "entries": { ... },
    "installs": { ... }
  },
  "gateway": { ... }
}
```

---

## 📝 四、实施步骤

### 步骤 1: 创建 Bootstrap 文件 (5 分钟)

```bash
# 1. 创建目录
mkdir -p ~/.openclaw/agents/{qqbot,telebot,feishu,dashboard,default}

# 2. 创建各 Agent 的 BOOTSTRAP.md
# (内容见上方 2.2 节)
```

### 步骤 2: 备份当前配置 (1 分钟)

```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.multi-agent
```

### 步骤 3: 修改 openclaw.json (5 分钟)

- 添加通道绑定 (`agentId`)
- 添加 Agent 专用配置
- 修改跨 Agent 通信规则

### 步骤 4: 验证配置 (2 分钟)

```bash
# 检查 JSON 格式
python3 -m json.tool ~/.openclaw/openclaw.json > /dev/null && echo "✅ JSON 格式正确"

# 检查必需字段
cat ~/.openclaw/openclaw.json | python3 -c "
import sys, json
c = json.load(sys.stdin)
print('Channels:', list(c.get('channels', {}).keys()))
print('Agents:', list(c.get('agents', {}).keys()))
"
```

### 步骤 5: 重启 Gateway (1 分钟)

```bash
openclaw gateway restart
```

### 步骤 6: 验证激活 (3 分钟)

```bash
# 检查 Agent 状态
openclaw status --all | grep -A10 "Agents"

# 检查通道绑定
openclaw status --all | grep -A20 "Channels"

# 测试各通道
# QQ: 发送消息测试 qqbot agent
# Telegram: 发送消息测试 telebot agent
# Feishu: 发送消息测试 feishu agent
```

**总耗时**: ~17 分钟

---

## 📊 五、预期效果

### 5.1 会话分布

**激活前**:
```
main agent: 45 个会话 (所有通道混合)
其他 agent: 0 个会话
```

**激活后 (预期)**:
```
qqbot agent:    ~15 个会话 (QQ Bot)
telebot agent:  ~15 个会话 (Telegram)
feishu agent:   ~10 个会话 (Feishu)
dashboard agent: ~5 个会话 (应急)
default agent:   ~0 个会话 (Cron 任务)
main agent:      ~0 个会话 (备用)
```

### 5.2 Token 使用优化

**激活前**:
```
main: 200k tokens (所有通道累积)
```

**激活后 (预期)**:
```
qqbot:    50k tokens
telebot:  50k tokens
feishu:   40k tokens
dashboard: 10k tokens
default:   10k tokens
main:      40k tokens
总计：160k tokens (节省 20%)
```

### 5.3 职责清晰化

| 任务类型 | 激活前 | 激活后 |
|---------|--------|--------|
| 系统管理 | main | qqbot (细佬) |
| 投资分析 | main | telebot (叻仔) |
| 文档管理 | main | feishu (Natalie) |
| 应急监控 | main | dashboard |
| 新闻报告 | main | default |
| QQ 聊天 | main | qqbot |
| Telegram 聊天 | main | telebot |
| Feishu 聊天 | main | feishu |

---

## ⚠️ 六、风险评估

### 6.1 潜在问题

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 配置错误导致启动失败 | 中 | 高 | 备份配置，可快速恢复 |
| 通道绑定错误 | 低 | 中 | 逐步验证，先测试一个通道 |
| 跨 Agent 通信失败 | 中 | 中 | 保留 agentToAgent.allow |
| Cron 任务执行异常 | 低 | 中 | 保留 default agent 处理 Cron |
| Token 压缩策略冲突 | 低 | 低 | 各 agent 独立配置 compaction |

### 6.2 回滚方案

**如果激活失败**:

```bash
# 1. 停止 Gateway
openclaw gateway stop

# 2. 恢复备份配置
cp ~/.openclaw/openclaw.json.bak.multi-agent ~/.openclaw/openclaw.json

# 3. 删除新建的 Agent 目录 (可选)
rm -rf ~/.openclaw/agents/{qqbot,telebot,feishu,dashboard,default}

# 4. 重启 Gateway
openclaw gateway restart
```

**回滚时间**: < 2 分钟

---

## ✅ 七、验收标准

### 7.1 功能验收

- [ ] QQ Bot 消息由 qqbot agent 处理
- [ ] Telegram 消息由 telebot agent 处理
- [ ] Feishu 消息由 feishu agent 处理
- [ ] Cron 任务由 default agent 处理
- [ ] Dashboard 可访问
- [ ] 跨 Agent 通信正常

### 7.2 性能验收

- [ ] 各 agent 会话独立
- [ ] Token 使用分散
- [ ] 无消息丢失
- [ ] 无响应延迟

### 7.3 安全验收

- [ ] 工具访问隔离生效
- [ ] 通道权限正确
- [ ] 无越权访问

---

## 📋 八、需要你确认的事项

### 8.1 配置确认

- [ ] Agent 角色分配是否合理？
- [ ] 通道绑定是否正确？
- [ ] 工具策略是否合适？
- [ ] 模型选择是否优化？

### 8.2 功能确认

- [ ] 是否需要调整职责分工？
- [ ] 是否需要添加其他 Agent？
- [ ] 是否需要修改通知规则？
- [ ] 是否需要特殊配置？

### 8.3 风险确认

- [ ] 是否接受可能的短暂中断？
- [ ] 是否已备份重要数据？
- [ ] 是否了解回滚方案？

---

## 🎯 九、下一步

**如果你确认方案 OK**, 我会:

1. ✅ 创建 5 个 Agent 的 BOOTSTRAP.md
2. ✅ 备份当前配置
3. ✅ 修改 openclaw.json
4. ✅ 验证配置格式
5. ✅ 重启 Gateway
6. ✅ 验证激活效果

**如果你需要修改**, 请告诉我:
- 哪些配置需要调整？
- 哪些职责需要重新分配？
- 哪些风险需要额外关注？

---

**请审核方案，确认 OK 后我即刻开工！** 🔥

---

**文档位置**: `/root/.openclaw/workspace/docs/MULTI_AGENT_ACTIVATION_PLAN.md`  
**文件大小**: ~15KB  
**最后更新**: 2026-03-09 15:04
