# 大模型性能对比测试方案 🧪

## 测试模型 (5个)

1. **nvidia/z-ai/glm4.7** - 默认模型
2. **nvidia/minimaxai/minimax-m2.1** - NVIDIA 多语言模型
3. **groq/llama-3.3-70b-versatile** - Groq 超快推理模型
4. **coding-aliyuncs/kimi-k2.5** - Kimi (阿里云)
5. **custom-coding-dashscope-aliyuncs-com/qwen3.5-plus** - Qwen 3.5 Plus (阿里云)

## 测试问题 (4个)

### 1️⃣ 简单计算
```
1+1等于几？只回答数字。
```
**测试目的**: 基础推理速度

### 2️⃣ 中文知识
```
广州是哪个省份的省会？用一句话回答。
```
**测试目的**: 中文知识库和准确性

### 3️⃣ 代码任务
```
用Python写一个计算斐波那契数列第n项的函数。
```
**测试目的**: 代码生成能力

### 4️⃣ 英文推理
```
Explain quantum computing in one simple sentence.
```
**测试目的**: 英文理解和简洁表达

## 测试流程

对每个模型，按顺序回答以上4个问题，并记录：

| 模型 | Q1 (1+1) | Q2 (广州) | Q3 (代码) | Q4 (量子) | 平均时间 |
|------|----------|-----------|-----------|-----------|----------|
| GLM4.7 | - | - | - | - | - |
| MiniMax | - | - | - | - | - |
| Groq | - | - | - | - | - |
| Kimi | - | - | - | - | - |
| Qwen | - | - | - | - | - |

## 测试指令

使用以下命令切换模型并测试：

```bash
# 切换到 GLM4.7
openclaw config set agents.defaults.model.primary "nvidia/z-ai/glm4.7"

# 切换到 MiniMax
openclaw config set agents.defaults.model.primary "nvidia/minimaxai/minimax-m2.1"

# 切换到 Groq
openclaw config set agents.defaults.model.primary "groq/llama-3.3-70b-versatile"

# 切换到 Kimi
openclaw config set agents.defaults.model.primary "coding-aliyuncs/kimi-k2.5"

# 切换到 Qwen
openclaw config set agents.defaults.model.primary "custom-coding-dashscope-aliyuncs-com/qwen3.5-plus"
```

每个模型切换后需要重启 Gateway：
```bash
openclaw gateway restart
```

## 预期结果

基于模型特性预期：

| 模型 | 预期优势 | 预期劣势 |
|------|----------|----------|
| GLM4.7 | 中文能力强，稳定 | 响应速度中等 |
| MiniMax | 多语言优秀 | 中文略弱于GLM |
| Groq | 响应速度最快 | 中文理解可能有限 |
| Kimi | 代码能力强 | 可能需要更长响应时间 |
| Qwen | 中文好，大上下文 | API 可能不稳定 |

---
*测试时间：2026-03-01*
*测试目的：对比不同模型的响应速度和回答质量*
