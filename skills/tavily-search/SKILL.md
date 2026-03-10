---
name: tavily-search
description: 使用 Tavily API 搜索全球网络资源，获取实时新闻、经济数据、行业信息等。适用于每日经济简报、市场调研、竞品分析等场景。
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"], "python_packages": ["tavily-python"] },
        "env": ["TAVILY_API_KEY"],
      },
  }
---

# Tavily Search 技能

## 配置

在 `TOOLS.md` 中记录 Tavily API Key，或设置环境变量：

```bash
export TAVILY_API_KEY=tvly-dev-YOUR_KEY
```

## 使用方法

### 基础搜索

```python
from tavily import TavilyClient

client = TavilyClient(api_key="YOUR_API_KEY")
response = client.search("query", search_depth="basic")
```

### 高级搜索

```python
# 深度搜索
response = client.search("query", search_depth="advanced")

# 指定时间范围
response = client.search("query", days=7)  # 最近 7 天

# 指定结果数量
response = client.search("query", max_results=10)
```

### 获取新闻

```python
response = client.search("全球经济新闻", topic="news", days=1)
```

## 示例：每日经济简报

搜索内容：
- 全球主要股市动态
- 重要经济数据和政策
- 汇率和大宗商品
- 工程行业动态

## API 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| query | 搜索查询 | 必填 |
| search_depth | basic / advanced | basic |
| topic | general / news / finance | general |
| days | 最近 N 天 | 无限制 |
| max_results | 最大结果数 | 5 |
| include_answer | 是否包含 AI 摘要 | false |
| include_raw_content | 是否包含原始内容 | false |
