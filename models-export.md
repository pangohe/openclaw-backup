# OpenClaw 大模型导出清单

**导出时间：** 2026-03-01 20:51
**总计模型数量：** 1000+ 个模型
**导出命令：** `openclaw models list --all`

---

## ✅ 已配置模型（有 API Key）

### 1. z-ai/glm4.7（默认）
- **Provider:** nvidia
- **类型:** text
- **Context:** 125k tokens
- **本地部署:** no
- **认证:** yes (default, configured)
- **用途:** 默认主模型，中文任务

### 2. minimaxai/minimax-m2.1
- **Provider:** nvidia
- **类型:** text
- **Context:** 250k tokens
- **本地部署:** no
- **认证:** yes (configured)
- **用途:** 多语言备用模型

### 3. kimi-coding/k2p5
- **Provider:** coding-aliyuncs/kimi-k2.5
- **类型:** text+image
- **Context:** 256k tokens
- **本地部署:** no
- **认证:** yes (configured)
- **用途:** 图片分析

### 4. custom-coding-dashscope-aliyuncs-com/qw...（Qwen3.5-Plus）
- **Provider:** custom-coding-dashscope-aliyuncs-com
- **类型:** text
- **Context:** 977k tokens
- **本地部署:** no
- **认证:** yes (configured)
- **用途:** ACP coding agent

### 5. groq/llama-3.3-70b-versatile
- **Provider:** groq
- **类型:** text
- **Context:** 128k tokens
- **本地部署:** no
- **认证:** yes (configured)
- **用途:** Groq fast inference

---

## 📊 主要模型分类

### OpenAI GPT 系列
- **GPT-5 系列:** gpt-5, gpt-5.1, gpt-5.2, gpt-5.3-codex
- **GPT-4 系列:** gpt-4, gpt-4o, gpt-4.1
- **O 系列:** o1, o3, o4-mini (推理模型)
- **Codex:** gpt-5.1-codex, gpt-5.2-codex

### Anthropic Claude 系列
- **Claude 4.x:** claude-3-haiku-4-5, claude-opus-4-6, claude-sonnet-4-6
- **Claude 3.7.x:** claude-3-7-sonnet
- **Claude 3.5.x:** claude-3-5-haiku, claude-3-5-sonnet

### Google Gemini 系列
- **Gemini 3.x:** gemini-3-flash-preview, gemini-3-pro-preview
- **Gemini 2.5.x:** gemini-2-5-flash, gemini-2-5-pro
- **Gemini 2.0.x:** gemini-2.0-flash, gemini-2.0-flash-lite
- **最大 Context:** 1024k tokens (1M tokens)

### ZAI GLM 系列
- **GLM 5:** glm-5 (200k tokens)
- **GLM 4.7:** glm-4.7 (200k tokens) ✅ 已配置
- **GLM 4.6:** glm-4.6 (200k tokens)
- **GLM 4.5:** glm-4.5 (128k tokens)

### Qwen 通义千问系列
- **Qwen 3.5:** qwen3-5-397b-a17b (256k tokens)
- **Qwen 3:** qwen3-next-80b-a3b (256k tokens)
- **Qwen 3 Coder:** qwen3-coder-480b-a35b (256k tokens)
- **Qwen Max:** qwen-max (977k tokens)

### MiniMax 系列
- **MiniMax M2.5:** minimax-m2.5 (200k tokens)
- **MiniMax M2.1:** minimax-m2.1 (200k tokens) ✅ 已配置

### Mistral 系列
- **Mistral Large:** mistral-large-latest (256k tokens)
- **Mistral Medium:** mistral-medium-latest (256k tokens)
- **Devstral:** devstral-medium-latest (256k tokens, 代码模型)

### DeepSeek 系列
- **DeepSeek V3.2:** DeepSeek-V3.2 (160k tokens)
- **DeepSeek R1:** deepseek-r1-distill-llama-70b (128k tokens)
- **DeepSeek Chat:** deepseek-chat-v3.2 (160k tokens)

### Kimi 系列月之暗面
- **Kimi K2.5:** kimi-k2.5 (256k tokens)
- **Kimi K2:** kimi-k2-thinking (256k tokens)
- **Kimi K2 Coding:** kimi-coding/k2p5 (256k tokens) ✅ 已配置

### Groq 系列（快速推理）
- **Llama 3.3:** llama-3-3-70b-versatile (128k tokens) ✅ 已配置
- **Gemma 2:** gemma2-9b-it (8k tokens)
- **Qwen:** qwen3-32b (128k tokens)

### xAI Grok 系列
- **Grok 4:** grok-4-fast (1953k tokens) 🚀 最大
- **Grok 4.1:** grok-4-1-fast (1953k tokens) 🚀 最大
- **Grok 3:** grok-3, grok-3-mini (128k tokens)
- **Grok Code:** grok-code-fast-1 (250k tokens)

---

## 🎯 顶级推荐（按用途）

### 🥇 最大 Context（超长文本）
1. **Grok 4.1 Fast** - 1953k tokens (xai/grok-4-1-fast)
2. **OpenRouter Auto** - 1953k tokens (openrouter/auto)
3. **Meta Llama 4 Scout** - 320k tokens (llama-4-scout)

### 💬 日常对话（高性价比）
1. **GLM 4.7** ✅ 已配置 - 200k tokens
2. **GLM 4.6** - 200k tokens
3. **MiniMax M2.1** ✅ 已配置 - 200k tokens
4. **Qwen 3.5 Plus** - 512k tokens

### 💻 编程代码
1. **Qwen 3 Coder** - 256k tokens
2. **GPT 5.3 Codex** - 391k tokens
3. **Mistral Codestral** - 250k tokens
4. **Grok Code Fast** - 250k tokens

### 🎨 多模态（图片+文本）
1. **Claude 3.7 Sonnet** - 195k tokens
2. **GPT 5.1** - 391k tokens
3. **Gemini 3 Pro Preview** - 977k tokens
4. **Llama 4 Maverick** - 1024k tokens

### 🚀 推理思考
1. **DeepSeek R1** - 160k tokens
2. **Qwen 3 Thinking** - 256k tokens
3. **GPT O4 Mini Deep Research** - 195k tokens
4. **OpenAI O3 Pro** - 195k tokens

### 🧮 高性能推理
1. **Groq Llama 3.3** ✅ 已配置 - 极快响应
2. **Groq Qwen** - 极快响应
3. **MiniMax M2.5 Highspeed** - 超快响应

---

## 📈 Context 容量对比

| 容量 | 模型 | 用途 |
|------|------|------|
| **1953k (1.9M)** | Grok 4.1 Fast, OpenRouter Auto | 超长文本分析 |
| **1024k (1M)** | Llama 4 Scout, Gemini 3 | 百万级上下文 |
| **977k** | Gemini 3, Qwen Max | 长文本分析 |
| **512k** | Qwen 3.5 Plus | 中长文本 |
| **256k** | DeepSeek V3.2, Qwen 3 Coder | 标准长文本 |
| **200k** | GLM 4.7, MiniMax M2.1 ✅ | 日常使用 |
| **128k** | GPT 5, Claude 4 | 标准上下文 |
| **125k** | GPT 4o, Claude 3.5 | 短文本 |
| **64k** | GLM 4.5v | 短对话 |

---

## 🔑 Provider 分类

### 已配置（有 API Key）
- ✅ NVIDIA: z-ai/glm4.7, minimaxai/minimax-m2.1
- ✅ Coding AliyunCS: kimi-coding/k2p5, qwen3.5-plus
- ✅ Groq: llama-3-3-70b-versatile

### 可用（无配置，可添加）
- 🟡 OpenAI: GPT 系列
- 🟡 Anthropic: Claude 系列
- 🟡 Google: Gemini 系列
- 🟡 ZAI: GLM 系列
- 🟡 MiniMax: MiniMax 系列
- 🟡 DeepSeek: DeepSeek 系列
- 🟡 xAI: Grok 系列
- 🟡 Mistral: Mistral 系列
- 🟡 OpenRouter: 聚合平台
- 🟡 Amazon Bedrock: AWS 云端
- 🟡 Azure OpenAI: 微软云端

---

## 💰 成本建议

### 免费或低成本
1. **Groq** - 免费额度，极快速度
2. **OpenRouter Free** - 免费模型
3. **Qwen 4b:free** - 免费使用

### 中等成本
- GLM 4.7 ✅ 已配置
- MiniMax M2.1 ✅ 已配置
- Claude Haiku
- GPT 4o Mini

### 高成本（性能最佳）
- GPT 5/5.1 Pro
- Claude Opus 4.6
- Grok 4.1 Fast
- Gemini 3 Pro

---

## 🚀 快速切换

### 切换默认模型
```bash
# 切换到 MiniMax M2.1
openclaw models set nvidia/minimaxai/minimax-m2.1

# 切换回 GLM 4.7
openclaw models set nvidia/z-ai/glm4.7
```

### 临时使用特定模型
在对话中指定：
```
请使用 gemini-2.5-pro 回答这个问题
```

---

## 📝 配置状态

| 模型 | API Key | 状态 |
|------|----------|------|
| nvidia/z-ai/glm4.7 | ✅ | ✅ default |
| nvidia/minimaxai/minimax-m2.1 | ✅ | ✅ configured |
| coding-aliyuncs/kimi-k2.5 | ✅ | ✅ configured |
| custom-coding/qwen3.5-plus | ✅ | ✅ configured |
| groq/llama-3.3-70b-versatile | ✅ | ✅ configured |

---

**导出完成！** 🔥

已保存到：`/root/.openclaw/workspace/models-export.md`
