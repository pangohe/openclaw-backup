# Token Saver V2 - 智能会话压缩（方案A）

## 🎯 概述

基于 BM25 + 重要性评分的智能会话压缩系统，实现 4:1 压缩比，同时保留关键对话。

### 特性

- ✅ **BM25 关键词检索** - 精确匹配关键词，保留相关历史
- ✅ **重要性评分** - 综合最近性、关键性、长度、角色
- ✅ **话题段落分块** - 按消息相关性选择，不只是保留最近N条
- ✅ **降级模式** - 可在没有 sentence-transformers 时运行（纯 BM25）
- ✅ **会话索引** - 快速检索历史对话
- ✅ **智能备份** - 自动创建带时间戳的备份

## 📁 文件结构

```
skills/token-saver-v2/
├── scripts/
│   ├── enhanced_compact.py    # 增强压缩器（12KB）
│   ├── chat_indexer.py        # 会话索引器（9KB）
│   └── integrate_watch.py     # 集成到 Token Watcher
└── README.md                  # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 必需（BM25 模式）
pip3 install rank-bm25 numpy --break-system-packages

# 可选（启用语义搜索）
pip3 install sentence-transformers --break-system-packages
```

### 2. 测试压缩

```bash
# 测试模式（对最大会话测试）
python3 /root/.openclaw/workspace/skills/token-saver-v2/scripts/enhanced_compact.py --test

# 手动压缩指定会话
python3 /root/.openclaw/workspace/skills/token-saver-v2/scripts/enhanced_compact.py \
  /root/.openclaw/agents/main/sessions/SESSION.jsonl \
  --keep 50
```

### 3. 建立索引

```bash
# 更新所有会话索引
python3 /root/.openclaw/workspace/skills/token-saver-v2/scripts/chat_indexer.py update

# 搜索历史对话
python3 /root/.openclaw/workspace/skills/token-saver-v2/scripts/chat_indexer.py \
  search SESSION "token压缩"

# 查看索引状态
python3 /root/.openclaw/workspace/skills/token-saver-v2/scripts/chat_indexer.py status
```

## 🎯 核心算法

### 重要性评分公式

```
score = 0.4 × position_score +
        0.3 × keyword_score +
        0.2 × length_score +
        0.1 × role_score
```

**评分维度：**

1. **position_score** - 位置评分（指数衰减）
   - 最近的消息得分更高
   - `exp(-0.01 × (total - index - 1))`

2. **keyword_score** - 关键词匹配度（BM25）
   - 从最近 20 条消息提取关键词
   - 使用 BM25 计算相关度

3. **length_score** - 长度评分
   - 偏好中等长度（50-500 字符）
   - 过短（<50）：0.3 分
   - 过长（>500）：0.5 分
   - 适中：1.0 分

4. **role_score** - 角色评分
   - user 消息：1.2 分
   - assistant 消息：1.0 分

## 📊 压缩策略

1. 计算所有消息的重要性评分
2. 按评分排序，选择前 N 条消息
3. **强制保留**最近 10 条消息
4. 按原始顺序输出

## 🔧 集成到 Token Watcher

```bash
python3 /root/.openclaw/workspace/skills/token-saver-v2/scripts/integrate_watch.py
```

这会自动更新 Token Watcher，使其达到阈值时调用智能压缩。

## 📈 性能目标

| 指标 | 当前 | 目标 |
|------|------|------|
| 压缩比 | 2.4:1 | **4:1** |
| 压缩时间 | - | **1-2秒** |
| 检索速度 | - | **<100ms** |
| 关键对话保留率 | - | **>90%** |

## 🔄 使用模式

### 纯 BM25 模式（默认）

- ✅ 无需安装 sentence-transformers
- ✅ 启动快，内存占用小
- ✅ 关键词匹配精确

### BM25 + 语义搜索（高级）

```python
from skills.token_saver_v2.scripts.enhanced_compact import EnhancedCompressor

# 激活向量模型
compressor = EnhancedCompressor()
compressor.load_model()  # 加载 SentenceTransformer

# 压缩时混合使用 BM25 + 向量相似度
```

## 📝 使用示例

### Python API

```python
from skills.token_saver_v2.scripts.enhanced_compact import EnhancedCompressor

# 创建压缩器
compressor = EnhancedCompressor()

# 压缩会话
result = compressor.compact_session(
    session_file='/root/.openclaw/agents/main/sessions/xxx.jsonl',
    target_keep_messages=50  # 目标保留消息数
)

if result['success']:
    print(f"压缩比: {result['compression_ratio']:.1f}:1")
    print(f"节省: {result['saved_percent']:.1f}%")
```

### 会话检索

```python
from skills.token_saver_v2.scripts.chat_indexer import ChatIndexer

# 创建索引器
indexer = ChatIndexer()

# 更新索引
indexer.update_all()

# 搜索
results = indexer.search(
    session_name='agent:main:main',
    query='token压缩优化',
    top_k=5
)

for doc, score in results:
    print(f"[{score:.3f}] {doc}")
```

## 🐛 故障排除

### 问题：ZeroDivisionError

- **原因**：所有分词结果为空
- **解决**：脚本会自动降级为简单评分

### 问题：sentence-transformers 未安装

- **影响**：无法使用语义搜索，但 BM25 模式仍然工作
- **解决**：安装库或继续使用纯 BM25 模式

### 问题：压缩比太低

- **原因**：会话消息数太少
- **建议**：只在消息数 > 100 时压缩

## 📚 相关文档

- Token 优化：`docs/token-limit-solutions.md`
- Token Watcher：`scripts/token_watcher_v2.py`
- 语义压缩：`skills/token-saver/scripts/semantic_compact.py`

## 🔜 后续优化

- [ ] 集成到 Token Watcher（自动触发）
- [ ] 实现实时监听模式（watchdog）
- [ ] 支持多 Agent 架构
- [ ] WebSocket 实时推送压缩通知

---

**版本**: v1.0.0
**更新时间**: 2026-03-01
**作者**: 大佬 🔥
