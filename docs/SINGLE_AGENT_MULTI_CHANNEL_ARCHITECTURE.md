# 单 Agent 多通道架构

**创建时间：** 2026-03-01
**架构类型：** 一个 main agent + 多个通道绑定
**状态：** ✅ 生产就绪

---

## 📐 架构概览

### 核心概念
```
Single Main Agent
    │
    ├─ QQBot Channel → 细佬（系统管家）
    ├─ Telegram Channel → 叻仔（投资顾问）
    ├─ Feishu Channel → Natalie（工作助理）
    └─ Dashboard Channel → 应急通道（永不超限）
```

### 关键点
- **只有一个 agent**（`agent:main`）
- **只有一个 workspace**（`/root/.openclaw/workspace`）
- **共享所有记忆**（MEMORY.md 自动同步）
- **跨通道互通**（`sessions_send` 直接通信）

---

## 🔧 技术实现

### 1. 配置（openclaw.json）
```json5
{
  agents: {
    defaults: {
      workspace: "/root/.openclaw/workspace",
    },
  },
  channels: {
    telegram: { enabled: true },
    feishu: { enabled: true },
    qqbot: { enabled: true },
  },
  tools: {
    sessions: {
      visibility: "all",  // ✅ 关键配置
    },
  },
}
```

### 2. Session 绑定
```
agent:main:qqbot:direct:<user_id>          → 细佬（系统管家）
agent:main:telegram:direct:<user_id>       → 叻仔（投资顾问）
agent:main:feishu:direct:<user_id>         → Natalie（工作助理）
agent:main:<dashboard_key>                 → 应急通道
```

### 3. 角色区分（在 AGENTS.md 中定义）
```markdown
## 你是谁

当前的通道决定了你的角色：
- QQBot → 你是细佬，系统管家...
- Telegram → 你是叻仔，投资顾问...
- Feishu → 你是 Natalie，工作助理...
- Dashboard → 你是系统守护者...
```

---

## 🔄 跨通道通信

### 使用 sessions_send
```javascript
// 细佬 -> 叻仔
sessions_send(
  sessionKey="agent:main:telegram:direct:8571370259",
  message="叻仔，帮我查 BTC 最新价格！",
  timeoutSeconds=10
)

// 叻仔 -> 细佬
sessions_send(
  sessionKey="agent:main:qqbot:direct:c721984a868cc01cdba58dc0f1d35627",
  message="细佬，BTC 价格是 $XX,XXX",
  timeoutSeconds=10
)
```

### 共享记忆
```markdown
# MEMORY.md（自动共享）
所有 session 都能看到：
- 重要决策
- 用户偏好
- 系统配置
- 历史记录
```

### 示例流程
```
用户（QQ）: "帮我查一下 BTC 价格"
  ↓
细佬（QQ）: 收到请求
  ↓
细佬: sessions_send(telegram, "叻仔，帮我查 BTC 价格")
  ↓
叻仔（Telegram）: 查 CoinGecko API
  ↓
叻仔: sessions_send(qqbot, "细佬，BTC 价格是 $95,200")
  ↓
细佬（QQ）: 回复用户 "老板，BTC 价格是 $95,200 💹"
```

---

## 🛡️ Dashboard 应急通道

### 目的
防止任何通道因为 token 超限而失联。

### 配置
```markdown
# Dashboard 特性
- 最大消息数：10 条
- 最大 token：25%
- 限制：永不超限
- 用途：系统危急时的最后通信渠道
```

### 应急协议
```
检测到 token 超限（>85%）
  ↓
1. 切换到 Dashboard
  ↓
2. 压缩超限 session
  ↓
3. 通过 Dashboard 通知老板
  ↓
4. 恢复正常通信
```

---

## 📊 性能优势

| 指标 | 单 Agent 多通道 | 多 Agent | 优势 |
|------|---------------|---------|------|
| **Workspace 数量** | 1 个 | N 个 | 减少 N-1 个 |
| **存储占用** | ~100MB | ~400MB (4 agents) | 减少 75% |
| **配置文件** | 1 个 | N 个 | 简化 N 倍 |
| **共享记忆** | ✅ 自动共享 | ❌ 需手动同步 | 自动化 |
| **跨通道通信** | ✅ sessions_send | ✅ agentToAgent | 相同 |
| **Gateway 负担** | 低 | 高 | 降低 N 倍 |
| **维护复杂度** | 低 | 高 | 简化 N 倍 |

---

## 🎯 使用场景

### 场景 1：日常任务分配
```
用户: "帮我安排下周的工作计划"
  ↓
细佬（QQ）: 接收任务，分配给 Natalie
  ↓
sessions_send(feishu, "Natalie，帮我安排下周工作计划")
  ↓
Natalie（Feishu）: 在飞书中创建计划
  ↓
sessions_send(qqbot, "细佬，计划已创建，飞书链接：...")
  ↓
细佬（QQ）: 回复用户 "老板，计划已安排好！📊"
```

### 场景 2：投资决策
```
用户: "最近 BTC 怎么样？值得买吗？"
  ↓
叻仔（Telegram）: 分析市场数据
  ↓
发现套利机会
  ↓
sessions_send(qqbot, "细佬，发现套利机会，建议老板关注")
  ↓
细佬（QQ）: 提醒用户 "老板，叻仔发现套利机会！💹"
```

### 场景 3：系统故障
```
监控检测到 token 超限
  ↓
自动切换到 Dashboard
  ↓
sessions_send(dashboard, "告老板：QQBot session 超限 88%")
  ↓
Dashboard: 通知老板 "🚨 通道超限警告"
  ↓
老板收到通知
  ↓
手动压缩或自动处理
```

---

## 🚀 最佳实践

### 1. 角色定义清晰
```markdown
## 你的角色

### QQBot（细佬）
- 系统管家
- 负责协调其他 channel
- 日常助手

### Telegram（叻仔）
- 投资顾问
- 加密货币分析
- 套利系统运营

### Feishu（Natalie）
- 工作助理
- 文档管理
- 项目协调

### Dashboard
- 系统守护者
- 应急通道
- 永不超限
```

### 2. 通信规范
```markdown
## 跨通道消息格式

从 细佬 → 叻仔：
"叻仔，[任务描述]。请[具体要求]。——细佬 🔥"

从 叻仔 → 细佬：
"细佬，[结果]。[附加信息]。——叻仔 💹"

从 Natalie → 细佬：
"细佬，[文档/计划已创建]。链接：[...] ——Natalie 📊"
```

### 3. Dashboard 使用
```markdown
## Dashboard 规则

- 仅用于：系统危急、紧急通知
- 保持清洁：最多 10 条消息
- 限制：25% token
- 定期归档：保持通信畅通
```

---

## 💡 为什么不用真正的 Multi-Agent？

### 真正 Multi-Agent 的问题
1. ❌ 资源占用高（4 个 workspace = 400MB）
2. ❌ 配置复杂（4 套 AGENTS.md）
3. ❌ 记忆不同步（MEMORY.md 需要手动同步）
4. ❌ 维护困难（4 套配置、4 套备份）
5. ❌ Gateway 负担高（4 倍并发处理）

### 单 Agent 多通道的优势
1. ✅ 轻量级（1 个 workspace = 100MB）
2. ✅ 配置简单（1 套 AGENTS.md）
3. ✅ 记忆自动共享（MEMORY.md 通用）
4. ✅ 维护容易（1 套配置、1 套备份）
5. ✅ Gateway 负担低（1 个 agent）

---

## 📚 参考

### 官方文档
- [OpenClaw Session Tools](https://docs.openclaw.ai/concepts/session-tool)
- [Multi-Agent Routing](https://docs.openclaw.ai/concepts/multi-agent)
- [Configuration Reference](https://docs.openclaw.ai/gateway/configuration-reference)

### 本地文档
- `/root/.openclaw/workspace/AGENTS.md` - Agent 角色定义
- `/root/.openclaw/workspace/MEMORY.md` - 共享记忆
- `/root/.openclaw/workspace/docs/SESSION_SENDS_FIX.md` - 跨通道通信修复

---

**最后更新：** 2026-03-01
**状态：** ✅ 生产就绪
**结论：** 推荐单 Agent 多通道架构
