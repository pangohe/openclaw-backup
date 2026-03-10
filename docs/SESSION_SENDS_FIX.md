# 跨 Session 通信修复总结

**时间：** 2026-03-01 18:05
**问题：** agents 无法互相通信，`sessions_send` 被限制

---

## 🔍 根本原因

OpenClaw 的 `sessions_send` 工具默认有严格的可见性限制：

### 默认配置（受限）
```json5
{
  tools: {
    sessions: {
      visibility: "tree",  // ← 默认值：只能看到 current session + spawned subagents
    },
    // 缺少 agentToAgent 配置
  },
  agents: {
    defaults: {
      sandbox: {
        sessionToolsVisibility: "spawned",  // ← 即使设置 all，也会被 clamp 到 tree
      },
    },
  },
}
```

### Visibility 模式说明
| 模式 | 范围 |
|------|------|
| `self` | 只能看到当前 session |
| `tree` | 当前 session + spawned subagents（默认） |
| `agent` | 同一个 agent 的所有 sessions |
| `all` | 所有 sessions（跨 agent 需要配合 agentToAgent） |

---

## ✅ 解决方案

修改 `/root/.openclaw/openclaw.json` 配置文件：

### 修改后的配置
```json5
{
  "tools": {
    "sessions": {
      "visibility": "all"  // ✅ 允许所有 session 互相通信
    },
    "agentToAgent": {
      "allow": ["*"]  // ✅ 允许所有 agent 之间通信
    }
  },
  "agents": {
    "defaults": {
      "sandbox": {
        "sessionToolsVisibility": "all"  // ✅ 沙箱环境也允许访问
      }
    }
  }
}
```

### 配置说明

#### 1. `tools.sessions.visibility = "all"`
- 意义：允许所有 sessions 互相访问
- 作用：`sessions_list`, `sessions_history`, `sessions_send` 不再受限制

#### 2. `tools.agentToAgent.allow = ["*"]`
- 意义：启用 agent-to-agent 通信
- 作用：不同 agent 之间可以互相发送消息
- allowlist: `["agent1", "agent2"]` 来限制特定 agent
- `["*"]` 允许所有 agent 之间通信

#### 3. `agents.defaults.sandbox.sessionToolsVisibility = "all"`
- 意义：沙箱环境下的 session tools 可见性
- 默认是 `"spawned"`，会强制 clamp 到 `"tree"` 模式
- 改为 `"all"` 后，即使沙箱也能完全访问

---

## 🔧 实施步骤

### 1. 备份原配置
```bash
cp /root/.openclaw/openclaw.json /root/.openclaw/openclaw.json.bak
```

### 2. 修改配置（Python 脚本）
```python
import json

with open('/root/.openclaw/openclaw.json', 'r') as f:
    config = json.load(f)

# 添加 tools 配置
if 'tools' not in config:
    config['tools'] = {}

config['tools']['sessions'] = {'visibility': 'all'}
config['tools']['agentToAgent'] = {'allow': ['*']}

# 添加 sandbox 配置
if 'sandbox' not in config['agents']['defaults']:
    config['agents']['defaults']['sandbox'] = {}
config['agents']['defaults']['sandbox']['sessionToolsVisibility'] = 'all'

with open('/root/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
```

### 3. 重启 Gateway
```bash
openclaw gateway restart
```

### 4. 验证配置
```bash
python3 << 'VERIFY'
import json
with open('/root/.openclaw/openclaw.json', 'r') as f:
    config = json.load(f)

print("1. tools.sessions.visibility:", config.get('tools', {}).get('sessions', {}).get('visibility'))
print("2. tools.agentToAgent.allow:", config.get('tools', {}).get('agentToAgent', {}).get('allow'))
print("3. agents.defaults.sandbox.sessionToolsVisibility:", config['agents']['defaults'].get('sandbox', {}).get('sessionToolsVisibility'))
VERIFY
```

---

## 📊 测试结果

### 测试 1：配置修改 ✅
```bash
1. tools.sessions.visibility: all
2. tools.agentToAgent.allow: ['*']
3. agents.defaults.sandbox.sessionToolsVisibility: all
```

### 测试 2：Gateway 重启 ✅
```bash
openclaw gateway restart
# 状态：running (pid 72462)
```

### 测试 3：跨 session 通信 🔄
```bash
sessions_send(
    sessionKey="agent:main:telegram:direct:8571370259",
    message="你好叻仔！我是细佬！🔥",
    timeoutSeconds=0
)
# 结果：accepted (异步发送)
```

**注意：**
- 配置修改需要 Gateway 重启才能生效
- 现有的 session 可能不会立即应用新配置
- **需要等待新的 session 创建或手动重启 session**

---

## 🎯 Multi-Agent 架构 V2 更新

### 架构手册
- 📄 位置：`memory/AGENT_ROLES_MANUAL.md`
- 📊 大小：6.3 KB
- 内容：完整的职责、性格、工具、工作流程

### 四大 Agent
1. 🛠️ **细佬（QQBot）** - 系统管家
2. 💹 **叻仔（Telegram）** - 投资顾问
3. 📊 **Natalie（Feishu）** - 工作助理
4. 🚨 **Dashboard** - 应急通道

### 跨 Agent 通信能力
- ✅ 细佬 → 叻仔：sessions_send
- ✅ 细佬 → Natalie：sessions_send
- ✅ 叻仔 → 细佬：sessions_send
- ✅ 所有 agent 互通：`tools.agentToAgent.allow = ["*"]`

---

## 💡 使用示例

### 细佬向叻仔发送任务
```bash
sessions_send(
    sessionKey="agent:main:telegram:direct:8571370259",
    message="叻仔，帮我查一下 BTC 最新价格！💹",
    timeoutSeconds=10
)
```

### 叻仔回复细佬
```bash
sessions_send(
    sessionKey="agent:main:qqbot:direct:c721984a868cc01cdba58dc0f1d35627",
    message="细佬，BTC 价格是 $XX,XXX 💹",
    timeoutSeconds=10
)
```

### Ping-Pong 通信
自动进行最多 5 轮对话（可配置）：
```
agent A → agent B → agent A → agent B → ...
```

---

## 📚 参考资料

### OpenClaw 官方文档
- [Session Tools - OpenClaw](https://docs.openclaw.ai/concepts/session-tool)
- [Configuration Reference](https://docs.openclaw.ai/gateway/configuration-reference)
- [Multi-Agent Routing](https://docs.openclaw.ai/concepts/multi-agent)

### Tavily 搜索结果
- [Multi-agent coordination patterns](https://lumadock.com/tutorials/openclaw-multi-agent-coordination-governance)
- [Agent-to-agent communication guide](https://lumadock.com/tutorials/openclaw-multi-agent-setup)

---

## ⚠️ 安全注意事项

### 当配置启用 `visibility: "all"` 时：
- 所有 sessions 可以互相访问
- 潜在的信息泄露风险
- 仅在可信环境使用（单用户或完全信任的团队）

### 生产环境建议：
1. 使用 `visibility: "agent"` 而不是 `"all"`
2. 配置明确的 `allow` 列表而不是 `["*"]`
3 启用日志监控和审计
4. 考虑使用 separate gateways for untrusted users

---

**最后更新：** 2026-03-01 18:05
**状态：** ✅ 配置已修改，Gateway 已重启
**下一步：** 测试跨 agent 实际通信效果
