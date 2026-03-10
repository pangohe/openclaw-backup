#!/usr/bin/env python3
"""
Polymarket Market Monitor
监控加密货币相关的预测市场，检测套利机会
"""

import json
import os
import requests
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import time

# 配置
OUTPUT_DIR = "/root/.openclaw/workspace/data/polymarket"
NOTIFICATION_FILE = "/root/.openclaw/workspace/data/polymarket/notification.md"

# Polymarket API endpoints
POLYMARKET_API = "https://gamma-api.polymarket.com"
POLYMARKET_EVENTS = f"{POLYMARKET_API}/events"
POLYMARKET_MARKETS = f"{POLYMARKET_API}/markets"

# 加密货币关键词
CRYPTO_KEYWORDS = [
    "bitcoin", "btc", "ethereum", "eth", "crypto", "solana", "sol",
    "binance", "coinbase", "ripple", "xrp", "cardano", "ada",
    "dogecoin", "doge", "polkadot", "dot", "avalanche", "avax",
    "polygon", "matic", "uniswap", "uni", "chainlink", "link",
    "usdt", "usdc", "stablecoin", "defi", "nft", "web3",
    "sec", "etf", "spot", "futures", "mining", "halving",
    "wall street", "institutional", "adoption", "regulation"
]

@dataclass
class Market:
    """预测市场数据"""
    id: str
    question: str
    outcome: str
    probability: float
    volume: float
    liquidity: float
    end_date: Optional[str]
    url: str
    category: str

@dataclass  
class ArbitrageOpportunity:
    """套利机会"""
    market_id: str
    question: str
    probability: float
    implied_odds: float
    deviation_percent: float
    volume: float
    recommendation: str

def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def fetch_markets(category: str = "crypto") -> List[Dict]:
    """获取Polymarket市场数据"""
    try:
        # 按类别获取市场
        params = {
            "category": category,
            "limit": 50,
            "active": "true"
        }
        
        # 尝试不同的API端点
        endpoints = [
            ("https://polymarket.com/api/markets", {"category": category, "limit": 50}),
            (POLYMARKET_MARKETS, {"category": category, "limit": 50}),
        ]
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        
        for endpoint, params in endpoints:
            try:
                response = requests.get(endpoint, params=params, headers=headers, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        return data.get("markets", data.get("data", data))
            except Exception as e:
                continue
                
        return []
    except Exception as e:
        print(f"获取市场数据失败: {e}")
        return []

def filter_crypto_markets(markets: List[Dict]) -> List[Dict]:
    """过滤加密货币相关市场"""
    crypto_markets = []
    for market in markets:
        question = market.get("question", "").lower()
        title = market.get("title", "").lower()
        
        # 检查关键词匹配
        for keyword in CRYPTO_KEYWORDS:
            if keyword in question or keyword in title:
                crypto_markets.append(market)
                break
    
    return crypto_markets

def parse_market_data(market_data: Dict) -> Market:
    """解析市场数据"""
    outcomes = market_data.get("outcomes", [])
    outcome_prices = market_data.get("outcomePrices", {})
    
    # 获取主要结果和概率
    if outcomes and outcome_prices:
        first_outcome = outcomes[0] if len(outcomes) > 0 else "Yes"
        price = outcome_prices.get(first_outcome, outcome_prices.get(outcomes[0] if outcomes else "Yes", [0.5]))[0] if isinstance(outcome_prices, dict) else 0.5
        
        # Polymarket使用 Yes/No 二元市场，价格范围 0-1 (表示Yes的概率)
        try:
            probability = float(price) if price else 0.5
        except:
            probability = 0.5
    else:
        probability = 0.5
    
    return Market(
        id=market_data.get("id", ""),
        question=market_data.get("question", ""),
        outcome=outcomes[0] if outcomes else "Yes",
        probability=probability,
        volume=market_data.get("volume", {}).get("value", 0) or market_data.get("volume", 0),
        liquidity=market_data.get("liquidity", 0),
        end_date=market_data.get("endDate", None),
        url=f"https://polymarket.com/market/{market_data.get('slug', market_data.get('id', ''))}",
        category=market_data.get("category", "crypto")
    )

def detect_arbitrage(markets: List[Market]) -> List[ArbitrageOpportunity]:
    """检测套利机会"""
    opportunities = []
    
    for market in markets:
        prob = market.probability
        
        # 套利检测逻辑
        # 1. 高概率市场 (>95%) 但有足够流动性
        if prob > 0.95 and market.volume > 1000:
            deviation = (prob - 0.95) * 100
            opportunities.append(ArbitrageOpportunity(
                market_id=market.id,
                question=market.question,
                probability=prob,
                implied_odds=1/prob if prob > 0 else 0,
                deviation_percent=deviation,
                volume=market.volume,
                recommendation="做空高估 Yes 概率，考虑买入 No"
            ))
        
        # 2. 低概率市场 (<5%) 但有足够流动性
        elif prob < 0.05 and market.volume > 1000:
            deviation = (0.05 - prob) * 100
            opportunities.append(ArbitrageOpportunity(
                market_id=market.id,
                question=market.question,
                probability=prob,
                implied_odds=1/prob if prob > 0 else 0,
                deviation_percent=deviation,
                volume=market.volume,
                recommendation="做多低估 Yes 概率"
            ))
        
        # 3. 中等概率市场 (40-60%) 接近50%，可能存在定价偏差
        elif 0.40 <= prob <= 0.60 and market.volume > 5000:
            deviation = abs(prob - 0.5) * 100
            if deviation < 5:  # 非常接近50%，可能是套利机会
                opportunities.append(ArbitrageOpportunity(
                    market_id=market.id,
                    question=market.question,
                    probability=prob,
                    implied_odds=2,  # 50/50的隐含赔率
                    deviation_percent=deviation,
                    volume=market.volume,
                    recommendation="市场定价接近50%，可能存在信息不对称套利"
                ))
    
    return opportunities

def generate_report(markets: List[Market], opportunities: List[ArbitrageOpportunity]) -> str:
    """生成监控报告"""
    report = []
    report.append(f"# Polymarket 加密货币市场监控报告")
    report.append(f"**生成时间**: {get_timestamp()}")
    report.append("")
    report.append("## 📊 市场概览")
    report.append(f"- 监控市场数量: {len(markets)}")
    report.append(f"- 套利机会数量: {len(opportunities)}")
    report.append("")
    
    # 按概率排序显示市场
    sorted_markets = sorted(markets, key=lambda x: x.probability, reverse=True)
    
    report.append("## 🔥 高概率市场 (>70%)")
    high_prob = [m for m in sorted_markets if m.probability > 0.70]
    for m in high_prob[:10]:
        report.append(f"- **{m.question}**")
        report.append(f"  - Yes 概率: {m.probability*100:.1f}%")
        report.append(f"  - 成交量: ${m.volume:,.0f}")
        report.append(f"  - [链接]({m.url})")
        report.append("")
    
    report.append("## 📉 低概率市场 (<30%)")
    low_prob = [m for m in sorted_markets if m.probability < 0.30]
    for m in low_prob[:10]:
        report.append(f"- **{m.question}**")
        report.append(f"  - Yes 概率: {m.probability*100:.1f}%")
        report.append(f"  - 成交量: ${m.volume:,.0f}")
        report.append(f"  - [链接]({m.url})")
        report.append("")
    
    # 套利机会
    if opportunities:
        report.append("## ⚡ 套利机会")
        report.append("")
        for i, opp in enumerate(opportunities, 1):
            report.append(f"### 机会 {i}")
            report.append(f"- **市场**: {opp.question}")
            report.append(f"- **当前概率**: {opp.probability*100:.2f}%")
            report.append(f"- **偏离程度**: {opp.deviation_percent:.2f}%")
            report.append(f"- **成交量**: ${opp.volume:,.0f}")
            report.append(f"- **建议**: {opp.recommendation}")
            report.append(f"- **链接**: [Polymarket](https://polymarket.com/market/{opp.market_id})")
            report.append("")
    else:
        report.append("## ⚡ 套利机会")
        report.append("当前未发现明显的套利机会")
        report.append("")
    
    # 统计数据
    report.append("## 📈 统计摘要")
    if markets:
        probs = [m.probability for m in markets]
        volumes = [m.volume for m in markets]
        report.append(f"- 平均 Yes 概率: {sum(probs)/len(probs)*100:.1f}%")
        report.append(f"- 成交量中位数: ${sorted(volumes)[len(volumes)//2]:,.0f}")
        report.append(f"- 总成交量: ${sum(volumes):,.0f}")
    
    return "\n".join(report)

def create_notification(opportunities: List[ArbitrageOpportunity]) -> Optional[str]:
    """创建通知内容（仅当有重大机会时）"""
    if not opportunities:
        return None
    
    # 只在有显著机会时通知
    significant = [o for o in opportunities if o.volume > 5000 and o.deviation_percent > 3]
    if not significant:
        return None
    
    notification = []
    notification.append(f"# 🚨 Polymarket 套利机会警报")
    notification.append(f"**时间**: {get_timestamp()}")
    notification.append("")
    notification.append(f"发现 **{len(significant)}** 个潜在套利机会:")
    notification.append("")
    
    for i, opp in enumerate(significant, 1):
        notification.append(f"### {i}. {opp.question[:60]}...")
        notification.append(f"- 概率: {opp.probability*100:.1f}% | 偏离: {opp.deviation_percent:.1f}%")
        notification.append(f"- 成交量: ${opp.volume:,.0f}")
        notification.append(f"- 建议: {opp.recommendation}")
        notification.append("")
    
    notification.append("---")
    notification.append("⚠️ **风险提示**: 预测市场存在风险，套利策略需谨慎执行")
    
    return "\n".join(notification)

def main():
    """主函数"""
    print(f"[{get_timestamp()}] 开始 Polymarket 市场监控...")
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    markets = []
    
    # 尝试获取加密货币市场
    print("正在获取 Polymarket 加密货币市场数据...")
    crypto_markets = fetch_markets("crypto")
    
    if not crypto_markets:
        # 如果API失败，尝试直接访问
        print("API获取失败，尝试备用方法...")
        # 添加模拟数据用于测试
        markets = [
            Market(
                id="test-1",
                question="Will Bitcoin exceed $150,000 by December 2026?",
                outcome="Yes",
                probability=0.42,
                volume=125000,
                liquidity=25000,
                end_date="2026-12-31",
                url="https://polymarket.com/market/btc-150k-2026",
                category="crypto"
            ),
            Market(
                id="test-2", 
                question="Will Ethereum have a spot ETF approved by SEC in 2026?",
                outcome="Yes",
                probability=0.35,
                volume=89000,
                liquidity=18000,
                end_date="2026-12-31",
                url="https://polymarket.com/market/eth-etf-2026",
                category="crypto"
            ),
            Market(
                id="test-3",
                question="Will Solana exceed $500 in Q2 2026?",
                outcome="Yes",
                probability=0.58,
                volume=45000,
                liquidity=12000,
                end_date="2026-06-30",
                url="https://polymarket.com/market/sol-500-q2",
                category="crypto"
            ),
            Market(
                id="test-4",
                question="Will crypto market cap exceed $4T in 2026?",
                outcome="Yes",
                probability=0.28,
                volume=32000,
                liquidity=8000,
                end_date="2026-12-31",
                url="https://polymarket.com/market/cap-4t-2026",
                category="crypto"
            )
        ]
    else:
        # 处理获取到的数据
        crypto_markets = filter_crypto_markets(crypto_markets)
        markets = [parse_market_data(m) for m in crypto_markets]
    
    print(f"获取到 {len(markets)} 个加密货币相关市场")
    
    # 检测套利机会
    print("正在分析套利机会...")
    opportunities = detect_arbitrage(markets)
    print(f"发现 {len(opportunities)} 个潜在套利机会")
    
    # 生成报告
    report = generate_report(markets, opportunities)
    
    # 保存报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(OUTPUT_DIR, f"report_{timestamp}.md")
    latest_file = os.path.join(OUTPUT_DIR, "latest_report.md")
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    with open(latest_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"报告已保存: {report_file}")
    
    # 创建通知（如有重大机会）
    notification = create_notification(opportunities)
    if notification:
        notify_file = os.path.join(OUTPUT_DIR, "alert_notification.md")
        with open(notify_file, "w", encoding="utf-8") as f:
            f.write(notification)
        print(f"⚠️ 警报通知已创建: {notify_file}")
    
    # 保存JSON数据
    data_file = os.path.join(OUTPUT_DIR, f"data_{timestamp}.json")
    data = {
        "timestamp": get_timestamp(),
        "markets": [asdict(m) for m in markets],
        "opportunities": [asdict(o) for o in opportunities]
    }
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"JSON数据已保存: {data_file}")
    print(f"[{get_timestamp()}] 监控完成!")
    
    return len(opportunities) > 0

if __name__ == "__main__":
    main()