# 方案A - 快速开始指南 🚀

## ✅ 部署完成！立即可用

**完成度**: 100%
**状态**: 所有功能已测试通过

---

## 🎯 3秒上手

### 自动模式（推荐） 💫

Token Watcher V2 已经自动启用增强压缩！

```bash
# 查看状态（不需要做任何事）
python3 /root/.openclaw/workspace/scripts/token_watcher_v2.py
```

**自动触发**:
- Token 使用 ≥ 70% 时自动压缩
- 自动选择最高分消息保留
- 自动备份完整历史

---

## 🛠️ 手动操作

### 压缩特定会话

```bash
python3 /root/.openclaw/workspace/skills/token-saver-v2/scripts/enhanced_compact.py \
  /root/.openclaw/agents/main/sessions/SESSION.jsonl --keep 50
```

### 建立会话索引

```bash
# 索引所有会话
python3 /root/.openclaw/workspace/skills/token-saver-v2/scripts/chat_indexer.py update

# 搜索历史对话
python3 /root/.openclaw/workspace/skills/token-saver-v2/scripts/chat_indexer.py \
  search SESSION "关键词"
```

---

## 📊 测试结果

```
会话: 2ea5280b-42d0-4e90-8b4f-fe825603f3ef.jsonl

✅ 压缩成功！
   原始: 64 条消息, 210.5 KB
   压缩后: 30 条消息, 24.3 KB
   压缩比: 2.1:1
   节省: 88.4% 🎉
```

---

## 🔧 配置

文件: `/root/.openclaw/workspace/scripts/token_watcher_v2.py`

```python
USE_ENHANCED_COMPACT = True  # 启用增强压缩

THRESHOLDS = {
    "compress": 70,    # 70% 时自动触发
}

CHANNEL_CONFIG = {
    "main": {"keep_messages": 50},
    "qqbot": {"keep_messages": 30},
    "telegram": {"keep_messages": 30}
}
```

---

## 📚 完整文档

| 文档 | 位置 |
|------|------|
| **使用指南** | skills/token-saver-v2/README.md |
| **部署总结** | 方案A部署总结.md |
| **完整报告** | 方案A完整部署报告.md |
| **本指南** | 方案A快速指南.md |

---

## 💡 提示

- ✅ **自动运行** - Token Watcher 每分钟监控，无需手动
- ✅ **安全备份** - 所有压缩都自动备份（带时间戳）
- ✅ **智能保留** - 关键对话评分优先保留
- ✅ **降级模式** - 无 sentence-transformers 也能用

---

**享受智能压缩！** 🔥

如有任何问题，参考 README.md 或使用 `--help` 参数。
