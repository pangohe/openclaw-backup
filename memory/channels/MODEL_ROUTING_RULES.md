# 🧠 智能模型路由系统

**创建时间**: 2026-03-01 22:12
**状态**: ✅ 已激活

---

## 📊 模型性能测试结果

| 模型 | 对话 | 编程 | 图片 | 速度 | Context | 用途 |
|------|------|------|------|------|---------|------|
| **bailian/qwen3.5-plus** | ✅ | ✅ | ✅ | 快 | 100 万 | **主用模型** |
| **bailian/kimi-k2.5** | ✅ | ✅ | ✅ | 快 | 26 万 | 图片理解 |
| **bailian/qwen3-coder-plus** | ✅ | ✅⚡ | ❌ | 快 | 100 万 | 编程专用 |
| **bailian/MiniMax-M2.5** | ✅ | ✅ | ❌ | 快 | 20 万 | 长文本 |
| **bailian/glm-4.7** | ✅ | ✅ | ❌ | 中 | 20 万 | 备用 |
| **groq/llama-3.3-70b** | ✅ | ✅ | ❌ | ⚡超快 | 128k | 快速响应 |
| **nvidia/z-ai/glm4.7** | ⚠️ | ⚠️ | ❌ | 中 | 125k | 备用 |
| **nvidia/minimax-m2.1** | ✅ | ✅ | ❌ | 中 | 250k | 多语言 |

---

## 🎯 模型分配规则

### 1️⃣ 日常对话 (默认)
**使用**: `bailian/qwen3.5-plus`
- 通用聊天、问答、咨询
- 复杂推理、分析
- 长文档理解（100 万 context）
- 多轮对话

### 2️⃣ 图片理解
**使用**: `bailian/kimi-k2.5` 或 `bailian/qwen3.5-plus`
- 图片内容识别
- 图表分析
- OCR 文字提取
- 视觉推理

**优先级**: kimi-k2.5 > qwen3.5-plus

### 3️⃣ 编程任务
**使用**: `bailian/qwen3-coder-plus`
- 代码编写
- 代码审查
- Bug 修复
- 技术方案设计
- 算法实现

**触发关键词**: "代码"、"编程"、"写个函数"、"debug"、"修复 bug"

### 4️⃣ 快速响应
**使用**: `groq/llama-3.3-70b-versatile`
- 简单问答
- 事实查询
- 翻译
- 摘要
- 需要毫秒级响应的场景

**触发条件**: 用户需要快速答案，问题简单

### 5️⃣ 长文本分析
**使用**: `bailian/MiniMax-M2.5` (20 万 context) 或 `bailian/qwen3.5-plus` (100 万 context)
- 长文档总结
- 多文件分析
- 历史记录回顾

### 6️⃣ 多语言支持
**使用**: `nvidia/minimaxai/minimax-m2.1`
- 英文对话
- 多语言混合
- 国际化场景

---

## 🔄 自动路由逻辑

```python
def select_model(user_input, has_image=False, is_code=False):
    # 1. 有图片 → 用 kimi-k2.5
    if has_image:
        return "bailian/kimi-k2.5"
    
    # 2. 编程任务 → 用 qwen3-coder-plus
    if is_code or any(kw in user_input for kw in ['代码', '编程', '函数', 'bug', 'debug']):
        return "bailian/qwen3-coder-plus"
    
    # 3. 简单问题 → 用 Groq (超快)
    if len(user_input) < 20 and '?' in user_input:
        return "groq/llama-3.3-70b-versatile"
    
    # 4. 英文为主 → 用 MiniMax
    if is_mostly_english(user_input):
        return "nvidia/minimaxai/minimax-m2.1"
    
    # 5. 默认 → 用 qwen3.5-plus (主用)
    return "bailian/qwen3.5-plus"
```

---

## 📋 配置位置

**主配置文件**: `/root/.openclaw/openclaw.json`

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "bailian/qwen3.5-plus"
      }
    }
  }
}
```

---

## 🚀 执行方式

### 方式 1: 修改 AGENTS.md
在 AGENTS.md 中添加模型选择规则，让 AI 根据任务类型自动选择。

### 方式 2: 创建路由 Skill
创建 `skills/model-router/SKILL.md`，实现自动路由逻辑。

### 方式 3: 手动指定
在对话中明确指定使用哪个模型。

---

## 📈 优化建议

1. **监控性能** - 记录每个模型的响应时间和质量
2. **动态调整** - 根据实际使用情况优化路由规则
3. **成本控制** - 优先使用免费/低价模型
4. **质量优先** - 关键任务使用最强模型 (qwen3.5-plus)

---

## ⚠️ 注意事项

1. **图片理解** - 必须用支持图片的模型 (kimi-k2.5, qwen3.5-plus)
2. **编程任务** - 优先用 coder 系列模型
3. **长文本** - 注意 context 限制，选择合适的模型
4. **备用方案** - 主模型失败时自动切换到备用模型

---

**最后更新**: 2026-03-01 22:12
**状态**: ✅ 全局执行中
