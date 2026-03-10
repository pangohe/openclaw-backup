# 多 Agent 配置方案

## 方案概述

**目标：** 管理 4 个通道的 token，确保不会超过 100%

**通道分配：**
1. **QQBot** (主要) -日常对话
2. **Telegram** (主要) - 工作协作
3. **Feishu** (新增) - 文档管理
4. **Dashboard** (应急) - 故障维修

---

## Token Watcher V3 配置

### 优化策略（已实施）

#### 1. 降低压缩阈值（更早触发）

```python
# 之前（UltraConservative模式）
THRESHOLDS = {
    "warning": 60,      # 60% (120k)
    "compress": 70,    # 70% (140k)
    "critical": 80,    # 80% (160k)
    "emergency": 90    # 90% (180k)
}

# 现在（Aggressive模式）
THRESHOLDS = {
    "warning": 50,      # 50% (100k)  ← 提前10%
    "compress": 60,    # 60% (120k)  ← 提前10%
    "critical": 70,    # 70% (140k)  ← 提前10%
    "emergency": 80    # 80% (160k)  ← 提前10%
}
```

**改进：** 主动压缩，提前预防超限

#### 2. 通道优先级（新增 Dashboard）

```python
CHANNEL_CONFIG = {
    "dashboard": {
        "keep_messages": 10,      # 10条（最少）
        "keep_days": 1,           # 1天（最新）
        "priority": "emergency"   # 紧急级别
    },
    "qqbot": {
        "keep_messages": 25,      # 25条（降低）
        "keep_days": 7,           # 7天
        "priority": "high"
    },
    "telegram": {
        "keep_messages": 25,      # 25条（降低）
        "keep_days": 14,          # 14天
        "priority": "high"
    },
    "whatsapp": {
        "keep_messages": 15,      # 15条
        "keep_days": 3,           # 3天
        "priority": "medium"
    },
    "main": {
        "keep_messages": 40,      # 40条（降低）
        "keep_days": 30,          # 30天
        "priority": "high"
    },
    "default": {
        "keep_messages": 20,
        "keep_days": 7,
        "priority": "low"
    }
}
```

**优先级规则：**
1. 🚨 **Emergency** (Dashboard): 激进压缩，最多 5 条
2. ⚡ **High** (QQBot/Telegram): 超限 >70% 时降为 2/3
3. 📊 **Normal** (其他): 按配置压缩
4. 🟡 **Low** (Default): 最后处理

#### 3. 激进压缩策略（新增）

```python
# Emergency 通道
if priority_level == "emergency":
    keep_messages = max(5, keep_messages // 2)  # 最多5条
    log(f"🚨 应急通道 [{channel}] 激进压缩: {keep_messages} 条", quiet)

# High 通道（超限>70%）
elif priority_level == "high" and token_percent > 70:
    keep_messages = max(10, keep_messages // 1.5)  # 降为2/3
    log(f"⚡ 高优先级通道 [{channel}] 激进压缩: {keep_messages} 条", quiet)
```

---

## 通道 Token 配额分配

### 系统总容量：200k tokens (GLM4.7)

### 分配方案（预留 20% safety margin）

| 通道 | 保留消息 | 保留天数 | 预估最大 Token | 告警阈值 | 压缩阈值 |
|------|---------|---------|---------------|---------|---------|
| QQBot | 25 | 7 | 60k | 30% (60k) | 35% (70k) |
| Telegram | 25 | 14 | 60k | 30% (60k) | 35% (70k) |
| Feishu | 30 | 7 | 50k | 25% (50k) | 30% (60k) |
| Dashboard | 10 | 1 | 20k | 20% (40k) | 25% (50k) |
| Other | 20 | 7 | 30k | 20% (40k) | 25% (50k) |
| **总计** | - | - | **220k** | **40%** | **50%** |

### 动态调度策略

**原则：** 确保任何时候Dashboard通道可用（应急用）

1. **Dashboard 通道（优先级最高）**
   - 保留 10 条（1天内）
   - 阈值：25% → 立即压缩到 5 条
   - 冷却时间：3 分钟（最快响应）

2. **QQBot / Telegram 通道（高优先级）**
   - 保留 25 条
   - 阈值：35% → 压缩
   - 阈值 >70% → 激进压缩（降为 15 条）
   - 冷却时间：5 分钟

3. **Feishu 通道（中优先级）**
   - 保留 30 条
   - 阈值：30% → 压缩
   - 冷却时间：5 分钟

4. **其他通道（低优先级）**
   - 保留 20 条
   - 阈值：25% → 压缩
   - 冷却时间：10 分钟

---

## Cron 任务配置

### 1. Token Watcher（全局监控）

```bash
# 每 3 分钟检查（提高频率）
Job ID: 3a5ec4e7-157f-4ddc-838e-42ee8a56130d
Frequency: every 3m
Script: python3 scripts/token_watcher_v2.py --quiet
Action: 自动压缩超限会话
```

### 2. Dashboard 通道专属监控

```bash
# 每 1 分钟检查（应急通道需要更快响应）
Job ID: (新增)
Frequency: every 1m
Script: python3 scripts/emergency_compressor.py --channel dashboard
Action: Dashboard 超限 >25% 立即压缩
```

### 3. 通道优先级压缩任务

```bash
# 每 5 分钟按优先级压缩
Job ID: (新增)
Frequency: every 5m
Script: python3 scripts/priority_compressor.py
Action: 按优先级压缩所有通道
Order: Dashboard > QQBot > Telegram > Feishu > Other
```

---

## Agent 配置建议

### Agent 1: QQBot (主要)

```json
{
  "name": "qqbot-agent",
  "channel": "qqbot",
  "model": "z-ai/glm4.7",
  "context": "200k",
  "memory_retention": {
    "messages": 25,
    "days": 7,
    "priority": "high"
  },
  "auto_compact": {
    "threshold": 35,  // 35% → 压缩
    "aggressive_at": 70  // 70% → 激进压缩
  }
}
```

### Agent 2: Telegram (主要)

```json
{
  "name": "telegram-agent",
  "channel": "telegram",
  "model": "z-ai/glm4.7",
  "context": "200k",
  "memory_retention": {
    "messages": 25,
    "days": 14,
    "priority": "high"
  },
  "auto_compact": {
    "threshold": 35,
    "aggressive_at": 70
  }
}
```

### Agent 3: Feishu (新增)

```json
{
  "name": "feishu-agent",
  "channel": "feishu",
  "model": "z-ai/glm4.7",
  "context": "200k",
  "memory_retention": {
    "messages": 30,
    "days": 7,
    "priority": "medium"
  },
  "auto_compact": {
    "threshold": 30,
    "aggressive_at": 65
  }
}
```

### Agent 4: Dashboard (应急)

```json
{
  "name": "dashboard-agent",
  "channel": "dashboard",
  "model": "z-ai/glm4.7",
  "context": "200k",
  "memory_retention": {
    "messages": 10,  // 最少
    "days": 1,  // 最新
    "priority": "emergency"
  },
  "auto_compact": {
    "threshold": 25,  // 最低阈值
    "aggressive_at": 50,  // 50% → 5条
    "cooldown": 180  // 3分钟冷却
  }
}
```

---

## 监控和报警

### 实时监控指标

```json
{
  "channels": {
    "qqbot": {
      "current_tokens": 45000,
      "percent": 22.5,
      "status": "OK"
    },
    "telegram": {
      "current_tokens": 38000,
      "percent": 19.0,
      "status": "OK"
    },
    "feishu": {
      "current_tokens": 25000,
      "percent": 12.5,
      "status": "OK"
    },
    "dashboard": {
      "current_tokens": 8000,
      "percent": 4.0,
      "status": "OK"
    }
  },
  "total_usage": 116000,
  "total_percent": 58.0,
  "free_capacity": 84000
}
```

### 报警机制

| 级别 | 触发条件 | 动作 |
|------|---------|------|
| 🟢 OK | 所有通道 < 30% | 无 |
| 🟡 WARNING | 任意通道 > 30% | 记录日志 |
| 🟠 COMPRESS | 任意通道 > 35% | 自动压缩 |
| 🔴 CRITICAL | Dashboard > 40% | 激进压缩 |
| 💥 EMERGENCY | Dashboard > 50% 或 总和 > 80% | 立即压缩所有通道 |

---

## 部署检查清单

### Phase 1: Token Watcher V3

- [x] 降低压缩阈值（50% → 60%）
- [x] 添加 Dashboard 通道配置
- [x] 实现通道优先级
- [x] 激进压缩策略
- [ ] 测试 Dashboard 通道

### Phase 2: Cron 任务配置

- [ ] Token Watcher 提高到每 3 分钟
- [ ] 新增 Dashboard 专属监控（每 1 分钟）
- [ ] 新增优先级压缩任务（每 5 分钟）

### Phase 3: Agent 部署

- [ ] 配置 QQBot Agent
- [ ] 配置 Telegram Agent
- [ ] 配置 Feishu Agent
- [ ] 配置 Dashboard Agent
- [ ] 测试跨通道协调

### Phase 4: 监控和验证

- [ ] 运行 24 小时负载测试
- [ ] 验证所有阈值触发正常
- [ ] 验证 Dashboard 通道始终可用
- [ ] 调优压缩参数

---

## 应急预案

### 场景 1: Dashboard 通道超限（> 50%）

```bash
# 立即执行
python3 scripts/emergency_compressor.py --channel dashboard --aggressive

# 查看状态
python3 scripts/token_watcher_v2.py --channel dashboard
```

### 场景 2: 所有通道总和超限（> 80%）

```bash
# 按优先级激进压缩
python3 scripts/priority_compressor.py --aggressive --all

# Dashboard → QQBot → Telegram → Feishu → Other
```

### 场景 3: 通道 Token 持续增长

```bash
# 检查增长趋势
python3 scripts/token_trend_analyzer.py --channel <channel>

# 调低保留数量
# 编辑 CHANNEL_CONFIG，降低 keep_messages
```

---

## 性能优化建议

### 1. 减少历史消息

```python
# 当前：25条
qqbot keep_messages = 25

# 优化：15条（token 减少约 40%）
qqbot keep_messages = 15
```

### 2. 分离工具调用记录

```python
# 保留完整消息（包括工具调用）
keep_full_message = True

# 优化：只保留关键对话（删除工具调用详情）
keep_tool_calls = False  // 节省约 30% token
```

### 3. 周期性归档

```bash
# 每天凌晨 2:00 归档所有会话
0 2 * * * python3 scripts/archive_sessions.py --all
```

---

## 下一步

1. **测试 Token Watcher V3**
   ```bash
   python3 scripts/token_watcher_v2.py --check-only
   ```

2. **Dashboard 通道压力测试**
   ```bash
   python3 scripts/test_dashboard_compression.py
   ```

3. **部署 Cron 任务**
   ```bash
   openclaw cron add <配置文件>
   ```

4. **部署 Agent**
   ```bash
   openclaw agent create <agent-config>
   ```

5. **24小时监控**
   - 观察各通道 token 使用情况
   - 验证阈值触发正常
   - 调优参数

---

**文档版本：** v1.0
**最后更新：** 2026-03-01
**状态：** 待测试
