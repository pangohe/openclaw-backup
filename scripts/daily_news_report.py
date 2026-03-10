#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日全球新闻整理
- 早上 9:30：整理前一天的全球重要新闻
- 下午 17:00：整理当天的全球新闻
"""

import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os

TAVILY_API_KEY = "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"
TAVILY_API_URL = "https://api.tavily.com/search"


def tavily_search(query: str, days: int = 1, max_results: int = 5, topic: str = "news") -> Dict[str, Any]:
    """使用 Tavily API 搜索"""
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "topic": topic,
        "days": days,
        "max_results": max_results,
        "include_answer": True,
    }

    try:
        response = requests.post(TAVILY_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ 搜索失败 [{query}]: {e}")
        return {"answer": "", "results": []}


def format_news_item(item: Dict[str, Any], idx: int) -> str:
    """格式化单条新闻"""
    title = item.get("title", "无标题")
    url = item.get("url", "")
    published_date = item.get("published_date", "")
    content = item.get("content", item.get("snippet", ""))[:150]

    date_str = f" ({published_date[:10]})" if published_date else ""
    return f"{idx + 1}. **{title}**{date_str}\n   {content}...\n   {url}\n"


def search_category(category_name: str, keywords: List[str], days: int = 1) -> str:
    """搜索某个类别的新闻"""
    print(f"🔍 搜索 {category_name}...")

    all_results = []
    for keyword in keywords:
        print(f"   - 关键词: {keyword}")
        result = tavily_search(keyword, days=days, max_results=3, topic="news")
        all_results.extend(result.get("results", []))

    # 去重（基于 URL）
    seen_urls = set()
    unique_results = []
    for item in all_results:
        url = item.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(item)

    # 格式化输出
    output = f"### {category_name}\n\n"
    if unique_results:
        for i, item in enumerate(unique_results[:8]):  # 最多 8 条
            output += format_news_item(item, i)
    else:
        output += "暂无相关新闻\n"

    output += "\n"
    return output


def generate_report(report_type: str = "morning" or "evening") -> str:
    """生成新闻报告"""

    now = datetime.now()

    if report_type == "morning":
        # 早上 9:30：搜索前一天的新闻
        target_date = now - timedelta(days=1)
        days = 2  # 搜索最近 2 天（覆盖昨天的新闻）
        title_date = target_date.strftime("%Y年%m月%d日")
        report_title = f"📰 每日全球新闻早餐 - {title_date}"
    else:
        # 下午 17:00：搜索当天的新闻
        target_date = now
        days = 1
        title_date = target_date.strftime("%Y年%m月%d日")
        report_title = f"📰 每日全球新闻晚报 - {title_date}"

    print(f"\n{'='*60}")
    print(f"{report_title}")
    print(f"{'='*60}\n")

    report = f"# {report_title}\n\n"
    report += f"⏰ 生成时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    report += "---\n\n"

    # 搜索类别
    categories = {
        "💹 经济新闻": ["全球经济 news", "股票市场", "经济数据", "央行政策"],
        "🌍 时事新闻": ["国际新闻", "政治新闻", "重大事件"],
        "🚀 高科技": ["高科技 news", "科技新闻", "前沿技术"],
        "📱 三星": ["Samsung news", "三星新闻", "Galaxy", "三星电子"],
        "🤖 AI 人工智能": ["AI news", "人工智能", "机器学习", "ChatGPT"],
        "🏙️ 广州本地新闻": ["广州新闻", "广东新闻 local", "广州 local news"],
        "🇮🇷 伊朗局势": ["Iran news", "伊朗局势", "中东局势 Iran"],
    }

    for category_name, keywords in categories.items():
        category_report = search_category(category_name, keywords, days=days)
        report += category_report

    report += "---\n\n"
    report += "**来源：** Tavily API 全球搜索\n"
    report += f"**统计：** 搜索了 {len(categories)} 个类别，共 {days} 天的新闻\n"

    return report


def save_report(report: str, report_type: str) -> str:
    """保存报告到文件"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    report_dir = "/root/.openclaw/workspace/data/daily-news"
    os.makedirs(report_dir, exist_ok=True)

    filename = f"{report_dir}/news-{report_type}-{date_str}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ 报告已保存: {filename}")
    return filename


def send_to_feishu(report: str) -> bool:
    """发送报告到飞书（可选）"""
    try:
        # 这里需要通过 message 工具发送
        # 暂时返回 False，表示不自动发送
        return False
    except Exception as e:
        print(f"❌ 发送到飞书失败: {e}")
        return False


def main():
    """主函数"""
    import sys

    # 确定报告类型（早上或下午）
    now = datetime.now()
    hour = now.hour

    if 6 <= hour < 12:
        report_type = "morning"
    elif 12 <= hour < 18:
        report_type = "afternoon"
    else:
        report_type = "evening"

    # 也可以通过参数指定
    if len(sys.argv) > 1:
        report_type_arg = sys.argv[1]
        if report_type_arg in ["morning", "evening", "afternoon"]:
            report_type = report_type_arg

    print(f"📊 生成 {report_type} 报告...")

    # 生成报告
    report = generate_report(report_type)

    # 保存报告
    filename = save_report(report, report_type)

    # 发送到飞书（可选）
    # send_to_feishu(report)

    # 输出报告
    print("\n" + "="*60)
    print("📰 报告内容预览（前 500 字）：")
    print("="*60)
    print(report[:500])
    print("...")
    print("="*60)

    return report, filename


if __name__ == "__main__":
    main()
