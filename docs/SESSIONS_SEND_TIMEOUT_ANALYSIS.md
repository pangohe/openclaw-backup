# Sessions Send Timeout 问题分析与解决方案

**创建时间：** 2026-03-01 20:10
**问题：** sessions_send 工具超时
**影响：** Telegram 和 Feishu 通道无法跨 session 通信

---

## 🔍 问题现象

### 症状
1. **Telegram 通道：** sessions_send 在 5 秒后 timeout
2. **Feishu 通道：** sessions_send 在 5 秒后 timeout
3. **Gateway 状态：** 所有通道显示 OK
4. **Token 使用：** 正常（最高 40.9%）
5. **Session 状态：** 未中断，abortedLastRun = false

### 错误信息
```json
{
  "status": "timeout",
  "error": "Operation timed out",
  "sessionKey": "agent:main:telegram:direct:8571370259"
}
```

---

## 🔬 根本原因分析

### 1. 并发限制（最可能的原因）

**配置：**
```json5
{
  agents: {
    defaults: {
      maxConcurrent: 4,  // ← 核心：最多同时处理 4 个 agent run
    },
  },
}
```

**问题：**
当 4 个并发 slot 都被占用时：
- 新的 sessions_send 请求进入队列
- 如果已有任务处理时间 > 5 秒 → timeout
- 特别是 cron 任务 + 用户的交互任务 + sessions_send

**证据：**
```bash
# 当前活跃任务（来自 openclaw status）
├─ 6 个 cron sessions (每 5 分钟运行)
├─ 1 个 Telegram session
├─ 1 个 Feishu session
├─ 1 个 QQBot session
└─ 用户交互

总计：9+ 个活跃 sessions，但 maxConcurrent = 4
```

### 2. Session 阻塞

**可能情况：**
- Session 正在处理复杂的工具调用（如 exec, web_fetch）
- Model API 响应慢（MiniMax, GLM4.7）
- 网络延迟或超时

**证据：**
- Telegram session 使用 MiniMax 模型，有时响应较慢
- QQBot session 最近一直在处理大量交互

### 3. Timeout 设置过短

**当前设置：**
```javascript
sessions_send(
  sessionKey="...",
  message="...",
  timeoutSeconds=5  // ← 只有 5 秒！
)
```

**问题：**
- 5 秒太短了
- Agent run 通常需要：
  - 读取 MEMORY.md: 0.5-1 秒
  - 分析消息: 1-2 秒
  - 调用工具: 1-3 秒
  - 生成回复: 1-3 秒
  - **总计：4-9 秒**

**结论：** 5 秒 timeout 处于边界，很容易超时。

---

## ✅ 解决方案

### 方案 1：增加 maxConcurrent（推荐）⭐

**修改前：**
```json5
{
  agents: {
    defaults: {
      maxConcurrent: 4,  // 太少
    },
  },
}
```

**修改后：**
```json5
{
  agents: {
    defaults: {
      maxConcurrent: 8,  // 增加到 8
    },
  },
}
```

**效果：**
- ✅ 允许更多并发任务
- ✅ 减少排队时间
- ✅ 降低 timeout 概率

**风险：**
- ⚠️ CPU 和内存占用增加
- ⚠️ LLM API 调用成本增加（如果按 token 付费）

### 方案 2：增加 timeout（必须同时实施）⭐⭐

**修改前：**
```javascript
sessions_send(
  sessionKey="...",
  message="...",
  timeoutSeconds=5  // 太短
)
```

**修改后：**
```javascript
sessions_send(
  sessionKey="...",
  message="...",
  timeoutSeconds=15  // 增加到 15 秒
)
```

**效果：**
- ✅ 给更多时间处理
- ✅ 减少 timeout
- ✅ 适应慢速模型

**最佳实践：**
- 简单任务：10 秒
- 复杂任务：20 秒
- fire-and-forget：`timeoutSeconds=0`

### 方案 3：优化并发策略（高级）⭐⭐⭐

**配置：**
```json5
{
  agents: {
    defaults: {
      maxConcurrent: 8,
      subagents: {
        maxConcurrent: 12,  // subagents 可以更多并发
      },
      queue: {
        // （如果支持）优化队列策略
        priority: "sessions_send",  // 优先处理跨 session 通信
      },
    },
  },
}
```

**效果：**
- ✅ 给跨 session 通信更高优先级
- ✅ 避免被 cron 任务阻塞
- ✅ 提高响应速度

### 方案 4：使用 fire-and-forget 模式（适用于通知）

**修改前：**
```javascript
sessions_send(
  sessionKey="...",
  message="...",
  timeoutSeconds=5
)
```

**修改后：**
```javascript
sessions_send(
  sessionKey="...",
  message="...",
  timeoutSeconds=0  // ← fire-and-forget
)
```

**效果：**
- ✅ 立即返回，不等待
- ✅ 适用于通知类消息
- ❌ 无法确认是否送达

### 方案 5：检查和清理僵死 sessions

**操作：**
```bash
# 查找长期未更新的 sessions
openclaw sessions list --json > sessions.json
cat sessions.json | jq '.sessions[] | select(.updatedAt < NOW - 3600000)'  # 超过 1 小时未更新

# 手动清空或归档
openclaw sessions patch <sessionKey> --reset
```

**效果：**
- ✅ 释放被占用的 slot
- ✅ 减少系统负担
- ⚠️ 会清除历史记录

---

## 🎯 推荐方案组合

### 立即实施（紧急修复）

```json5
{
  agents: {
    defaults: {
      maxConcurrent: 8,  // 从 4 增加到 8
    },
  },
}

// 代码中
sessions_send(
  sessionKey="...",
  message="...",
  timeoutSeconds=15  // 从 5 增加到 15
)
```

### 短期优化（1-2 周内）

1. **监控并发使用率**
   ```bash
   # 创建监控脚本
   # 每 5 分钟检查 active sessions 数量
   # 如果经常接近 maxConcurrent，考虑进一步增加
   ```

2. **优化 cron 任务调度**
   ```json5
   {
     cron: {
       tasks: {
         "Token Watcher": {
           schedule: "*/5 * * * *",
           cooldown: 120,  // 增加冷却时间，避免频繁触发
         },
       },
     },
   }
   ```

3. **清理旧 sessions**
   ```bash
   # 自动归档超过 24 小时未活跃的 sessions
   openclaw sessions prune --older-than 24h
   ```

### 长期改进（1-2 个月内）

1. **实现优先级队列**
   ```json5
   {
     agents: {
       defaults: {
         queue: {
           priority: [
             "user_interaction",    // 最高优先级
             "sessions_send",        // 高优先级
             "cron",                 // 中等优先级
             "background",           // 最低优先级
           ],
         },
       },
     },
   }
   ```

2. **分布式架构**
   ```markdown
   如果负载持续过高：
   - 部署多个 Gateway 实例
   - 使用负载均衡器
   - 分离不同类型的 session（如一个 Gateway 专门处理 cron 任务）
   ```

---

## 📊 监控指标

### 关键指标

1. **并发使用率**
   ```bash
   # 当前活跃 sessions / maxConcurrent
   active_sessions / maxConcurrent
   # 目标：< 70%
   # 警告：> 80%
   # 紧急：> 90%
   ```

2. **Sessions_send 成功率**
   ```bash
   successful_sends / total_sends
   # 目标：> 95%
   ```

3. **平均响应时间**
   ```bash
   avg(timeout_seconds)
   # 目标：< 10 秒
   ```

4. **Token 使用率**
   ```bash
   # 部分超时可能是由于 token 超限导致模型响应慢
   avg(tokens) / max_tokens
   # 目标：< 60%
   ```

### 监控脚本

```python
#!/usr/bin/env python3
# 监控 OpenClaw 并发使用率
import json, subprocess, time

def check_concurrency():
    result = subprocess.run(
        ['openclaw', 'sessions', 'list', '--json'],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)

    active_sessions = len([s for s in data['sessions'] if s.get('updatedAt', 0) > time.time() - 600000])
    max_concurrent = 8  # 从配置读取

    usage_rate = active_sessions / max_concurrent * 100

    print(f"Active sessions: {active_sessions}")
    print(f"Max concurrent: {max_concurrent}")
    print(f"Usage rate: {usage_rate:.1f}%")

    if usage_rate > 90:
        print("🚨 紧急：并发使用率过高！")
    elif usage_rate > 80:
        print("⚠️ 警告：并发使用率较高")
    else:
        print("✅ 正常")

if __name__ == '__main__':
    check_concurrency()
```

---

## ✅ 实施步骤

### Step 1：修改配置

```bash
# 备份配置
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup_$(date +%Y%m%d_%H%M%S)

# 修改 maxConcurrent
python3 << 'PYTHON'
import json
with open('/root/.openclaw/openclaw.json', 'r') as f:
    config = json.load(f)

config['agents']['defaults']['maxConcurrent'] = 8

with open('/root/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("✅ maxConcurrent updated: 4 → 8")
PYTHON

# 重启 Gateway
openclaw gateway restart
```

### Step 2：测试 sessions_send

```bash
# 测试 1：短消息，15s timeout
sessions_send(
  sessionKey="agent:main:telegram:direct:8571370259",
  message="测试消息",
  timeoutSeconds=15
)

# 测试 2：使用 fire-and-forget
sessions_send(
  sessionKey="agent:main:telegram:direct:8571370259",
  message="通知消息",
  timeoutSeconds=0
)

# 测试 3：复杂任务，30s timeout
sessions_send(
  sessionKey="agent:main:feishu:direct:...",
  message="创建文档...",
  timeoutSeconds=30
)
```

### Step 3：验证

```bash
# 检查 Gateway 状态
openclaw status

# 检查 sessions_send 日志
# （需要查看具体日志文件）

# 验证跨 session 通信
# 手动在 Telegram/Feishu 接收到消息
```

---

## 📝 最佳实践

### 1. 根据 task 类型选择 timeout

| Task 类型 | Timeout | 说明 |
|-----------|---------|------|
| 简单通知 | 0 秒 | fire-and-forget |
| 一般消息 | 10 秒 | 标准响应时间 |
| 复杂任务 | 20 秒 | 可能需要调用工具 |
| 极端情况 | 30 秒 | 最大值，超过说明有问题 |

### 2. 优先使用 fire-and-forget（timeout=0）

**适用场景：**
- 通知类消息
- 不需要确认送达
- 批量发送

**不适用场景：**
- 需要回复的任务
- 关键消息
- 需要确认结果

### 3. 监控和预警

```bash
# 创建 cron 任务监控并发使用率
*/5 * * * * /root/.openclaw/workspace/scripts/monitor_concurrency.sh
```

### 4. 定期清理旧 sessions

```bash
# 自动归档
0 2 * * * openclaw sessions prune --older-than 24h
```

---

## 🔒 预防措施

### 1. 配置文件版本控制

```bash
# 使用 git 管理配置文件
cd ~/.openclaw
git init
git add openclaw.json
git commit -m 'Initial config'
```

### 2. 配置审计

```bash
# 每次修改配置后记录
echo "$(date): Modified maxConcurrent from 4 to 8" >> ~/.openclaw/changes.log
```

### 3. 回滚机制

```bash
# 快速回滚脚本
#!/bin/bash
BACKUP=$(ls -t ~/.openclaw/openclaw.json.backup_* | head -1)
cp "$BACKUP" ~/.openclaw/openclaw.json
openclaw gateway restart
```

---

## 🎯 总结

### 问题根源
1. **maxConcurrent = 4 太少** - 不能满足当前负载
2. **timeoutSeconds = 5 太短** - Agent run 通常需要 4-9 秒
3. **Cron 任务占用资源** - 频繁的 cron 任务占用 slot

### 解决方案
1. ✅ **增加 maxConcurrent 从 4 到 8**
2. ✅ **增加 timeoutSeconds 从 5 到 15**
3. ✅ **使用 fire-and-forget（timeout=0）处理通知**
4. ✅ **清理旧 sessions，释放 slot**
5. ✅ **监控并发使用率，及时扩容**

### 防止复发
1. ✅ 实施监控脚本
2. ✅ 定期审查配置
3. ✅ 优化 cron 任务调度
4. ✅ 建立告警机制

---

**最后更新：** 2026-03-01 20:10
**状态：** 需要立即实施
**优先级：** 高
**负责人：** 细佬（QQBot）
