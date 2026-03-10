# Token Watcher V2 - 增强版智能监控和压缩

## 🚀 核心升级

### 相比 V1 的改进

| 功能 | V1 (旧版) | V2 (增强版) |
|------|---------|-------------|
| **监控范围** | 仅主会话 | **所有通道** (161 个会话) ✅ |
| **压缩策略** | 按时间保留 | **BM25 + 重要性评分** ✅ |
| **自动压缩** | 仅提醒不执行 | **自动智能压缩** ✅ |
| **通道隔离** | 无差异化 | **按通道定制策略** ✅ |
| **防止重复** | 无 | **5 分钟冷却** ✅ |
| **关键词提取** | 无 | **智能提取** ✅ |

---

## 📊 通道压缩策略

每类通道有自己的保留规则，确保聊天顺畅：

| 通道 | 保留消息 | 保留天数 | 重要性 | 说明 |
|------|---------|---------|--------|------|
| **main** | 50 条 | 30 天 | 1.0 | 主通道，长期记忆重要 |
| **qqbot** | 30 条 | 7 天 | 0.9 | QQ Bot，近期历史重要 |
| **telegram** | 30 条 | 14 天 | 0.85 | Telegram，适中策略 |
| **whatsapp** | 15 条 | 3 天 | 0.7 | WhatsApp，仅用于紧急场景 |
| **default** | 20 条 | 7 天 | 0.5 | 其他通道 |

---

## 🧠 智能压缩算法

### 1. BM25 简化版 - 关键词匹配
```
从最近 100 条消息中提取 Top 10 关键词
→ 保留包含这些关键词的历史消息
→ 确保话题连贯性
```

### 2. 重要性评分 (4 维度)
```python
总体得分 = 新鲜度(40%) + 关键词匹配(30%) + 角色权重(20%) + 内容长度(10%)
```

- **新鲜度**: 最近的消息得分更高
- **关键词匹配**: 包含当前话题关键词的优先保留
- **角色权重**: 用户/assistant > 工具调用
- **内容长度**: 中等长度的消息（50-2000 字符）优先

### 3. 强制保留规则
- 所有通道**强制保留最近 N 条**（按通道配置）
- 不管重要性得分如何，最近的对话一定保留

---

## 🛠️ 使用方式

### 检查状态（不压缩）
```bash
python3 /root/.openclaw/workspace/scripts/token_watcher_v2.py --check-only
```

### 运行检查并压缩
```bash
python3 /root/.openclaw/workspace/scripts/token_watcher_v2.py
```

### 静默模式（仅记录日志）
```bash
python3 /root/.openclaw/workspace/scripts/token_watcher_v2.py --quiet
```

### Cron 任务集成
```bash
# 在 HEARTBEAT.md 中添加
python3 /root/.openclaw/workspace/scripts/token_watcher_v2.py --quiet
```

---

## 📈 运行示例

```
🚀 Token Watcher V2 启动...

📊 Token Watcher V2 统计概览
   会话总数: 161
   总 Token: 1,128,052
   最高使用率: 100%

📡 各通道详情:
   [DEFAULT]
     会话数: 161
     Token: 1,128,052
     平均使用率: 3.4%
     保留策略: 20条 / 7天

✅ 检查完成
```

---

## 🔄 压缩示例

当某个会话达到 70% 阈值时：

```
[qqbot] xxx-xxx-xxx.jsonl: 75.3% (COMPRESS)
🗑️  开始智能压缩: xxx-xxx-xxx.jsonl
   检测到关键词: ['token', '压缩', '脚本', '通道', '优化']
   ✅ 备份到: xxx-xxx-xxx.jsonl.bak
   ✅ 压缩完成: 150 → 30 条消息 (节省 80.0%)

✅ 压缩完成！
   压缩会话数: 1
   节省消息数: 120
   - xxx-xxx-xxx.jsonl (qqbot): 150 → 30 条 (节省 80.0%)
```

---

## 🔒 安全机制

### 防止重复压缩
- **5 分钟冷却期**: 同一会话 5 分钟内不会重复压缩
- **自动备份**: 压缩前自动备份为 `.jsonl.bak`
- **只减不减**: 压缩后只保留高质量消息，不会新增

### 紧急恢复
```bash
# 恢复备份
mv /root/.openclaw/agents/main/sessions/xxx-xxx-xxx.jsonl.bak \
   /root/.openclaw/agents/main/sessions/xxx-xxx-xxx.jsonl
```

---

## 📝 压缩历史记录

压缩记录保存在 `token-state-v2.json`：

```json
{
  "compressions": [
    {
      "time": "2026-03-01T13:23:49.123456",
      "session": "xxx-xxx-xxx.jsonl",
      "channel": "qqbot",
      "original": 150,
      "compressed": 30,
      "saved_percent": 80.0,
      "keywords": ["token", "压缩", "脚本", "通道", "优化"]
    }
  ]
}
```

---

## 🎯 预期效果

- ✅ **自动压缩**: 达到阈值自动执行，无需手动干预
- ✅ **话题连贯**: BM25 算法确保相关话题保留
- ✅ **通道优化**: 每类通道独立策略，确保聊天顺畅
- ✅ **压缩比提升**: 从 2.4:1 提升到 **4:1+**（目标）
- ✅ **更少干扰**: 5 分钟冷却，避免频繁压缩

---

## 🔧 下一步集成

1. **更新 HEARTBEAT.md**: 加入 V2 调用
2. **更新 Cron**: 使用 `--quiet` 模式
3. **监控日志**: 检查 `memory/token-watcher.log`
4. **性能对比**: 观察 1-2 周，对比 V1 效果

---

_基于 Zilliz 最佳实践：BM25 + 话题分组 + 重要性评分_
