#!/usr/bin/env python3
"""
生成回测测试数据
用于在真实数据不足时测试回测系统

功能：
1. 生成模拟的加密货币价格数据
2. 生成模拟的 Polymarket 事件
3. 创建已知胜率的测试场景
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# 配置
DATA_DIR = Path.home() / ".openclaw" / "workspace" / "data"
CRYPTO_DIR = DATA_DIR / "crypto-trends"
POLYMARKET_DIR = DATA_DIR / "polymarket"
BACKTEST_DIR = DATA_DIR / "backtest"

# 确保目录存在
for dir_path in [CRYPTO_DIR, POLYMARKET_DIR, BACKTEST_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


def generate_crypto_data(days: int = 30, target_win_rate: float = 0.75) -> list:
    """
    生成模拟加密货币数据
    
    参数:
        days: 生成多少天的数据
        target_win_rate: 目标胜率（用于控制信号质量）
    """
    print(f"📊 生成 {days} 天的模拟加密货币数据...")
    
    coins_config = [
        {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "base_price": 67000},
        {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "base_price": 2000},
        {"id": "solana", "symbol": "sol", "name": "Solana", "base_price": 100},
        {"id": "binancecoin", "symbol": "bnb", "name": "BNB", "base_price": 350},
        {"id": "ripple", "symbol": "xrp", "name": "XRP", "base_price": 0.5},
    ]
    
    all_data = []
    start_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        # 每天生成多个时间点（模拟每小时数据）
        for hour in range(9, 23):  # 9:00 - 22:00
            timestamp = current_date.replace(hour=hour, minute=0)
            
            coins_data = []
            for coin in coins_config:
                # 随机价格波动（-5% 到 +5%）
                volatility = random.gauss(0, 2.5)
                price = coin["base_price"] * (1 + volatility / 100)
                
                # 24 小时变化（用于生成信号）
                change_24h = random.gauss(0, 3.0)
                
                coin_data = {
                    "id": coin["id"],
                    "symbol": coin["symbol"],
                    "name": coin["name"],
                    "current_price": round(price, 2),
                    "price_change_percentage_24h": round(change_24h, 2),
                    "market_cap": int(price * 1000000),
                    "total_volume": int(price * 10000),
                    "high_24h": price * 1.02,
                    "low_24h": price * 0.98,
                }
                coins_data.append(coin_data)
            
            # 更新基础价格（随机游走）
            for coin in coins_config:
                coin["base_price"] *= (1 + random.gauss(0, 1) / 100)
            
            data_point = {
                "timestamp": timestamp.isoformat(),
                "coins": coins_data
            }
            all_data.append(data_point)
            
            # 保存到文件
            filename = f"crypto-trend-{timestamp.strftime('%Y%m%d-%H%M')}.json"
            filepath = CRYPTO_DIR / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_point, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 生成了 {len(all_data)} 条加密货币数据")
    return all_data


def generate_polymarket_data(days: int = 30) -> list:
    """生成模拟 Polymarket 数据"""
    print(f"📊 生成 {days} 天的模拟 Polymarket 数据...")
    
    events_templates = [
        {
            "name": "Will Bitcoin hit ${price}K in {month}?",
            "slug": "bitcoin-price-{month}",
            "category": "Crypto"
        },
        {
            "name": "Will Ethereum ETF be approved in {month}?",
            "slug": "ethereum-etf-{month}",
            "category": "Crypto"
        },
        {
            "name": "Will Fed raise rates in {month}?",
            "slug": "fed-rates-{month}",
            "category": "Economy"
        },
    ]
    
    months = ["January", "February", "March", "April", "May", "June"]
    all_data = []
    
    start_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        markets = []
        for i, template in enumerate(events_templates):
            month = months[day % len(months)]
            price = 70 + (day % 20)
            
            market = {
                "name": template["name"].format(price=price, month=month),
                "slug": template["slug"].format(month=month.lower()),
                "probability": random.uniform(0.2, 0.8),
                "volume": random.uniform(1000000, 100000000),
                "end_date": (current_date + timedelta(days=30)).isoformat(),
                "category": template["category"],
                "url": f"https://polymarket.com/market/{template['slug'].format(month=month.lower())}"
            }
            markets.append(market)
        
        data_point = {
            "check_time": current_date.isoformat(),
            "total_events": len(markets),
            "crypto_events": markets,
            "arbitrage_opportunities": []
        }
        all_data.append(data_point)
    
    # 保存到文件
    report_file = POLYMARKET_DIR / "historical_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 生成了 {len(all_data)} 条 Polymarket 数据")
    return all_data


def generate_known_outcome_signals(num_signals: int = 100, win_rate: float = 0.75) -> list:
    """
    生成已知结果的交易信号（用于验证回测系统）
    
    参数:
        num_signals: 信号数量
        win_rate: 期望胜率
    """
    print(f"🎯 生成 {num_signals} 个已知结果的交易信号（目标胜率：{win_rate*100}%）...")
    
    signals = []
    num_winners = int(num_signals * win_rate)
    num_losers = num_signals - num_winners
    
    # 生成盈利交易
    for i in range(num_winners):
        signal = {
            "id": f"signal_{i:03d}",
            "timestamp": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "coin": random.choice(["Bitcoin", "Ethereum", "Solana"]),
            "symbol": random.choice(["BTC", "ETH", "SOL"]),
            "price": random.uniform(1000, 70000),
            "change_24h": random.uniform(2, 10),
            "signal_type": "LONG",
            "outcome": "WIN",
            "pnl_percent": random.uniform(1, 8)  # 盈利 1-8%
        }
        signals.append(signal)
    
    # 生成亏损交易
    for i in range(num_losers):
        signal = {
            "id": f"signal_{num_winners + i:03d}",
            "timestamp": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "coin": random.choice(["Bitcoin", "Ethereum", "Solana"]),
            "symbol": random.choice(["BTC", "ETH", "SOL"]),
            "price": random.uniform(1000, 70000),
            "change_24h": random.uniform(-10, -2),
            "signal_type": "SHORT",
            "outcome": "LOSS",
            "pnl_percent": random.uniform(-8, -1)  # 亏损 -8% 到 -1%
        }
        signals.append(signal)
    
    # 打乱顺序
    random.shuffle(signals)
    
    # 保存到文件
    signals_file = BACKTEST_DIR / "known_outcome_signals.json"
    with open(signals_file, 'w', encoding='utf-8') as f:
        json.dump(signals, f, indent=2, ensure_ascii=False)
    
    actual_win_rate = num_winners / num_signals * 100
    print(f"✅ 生成了 {num_winners} 个盈利交易，{num_losers} 个亏损交易 (实际胜率：{actual_win_rate:.1f}%)")
    print(f"📄 信号已保存：{signals_file}")
    
    return signals


def main():
    """主函数"""
    print("=" * 60)
    print("🎲 回测数据生成器")
    print("=" * 60)
    
    # 生成模拟数据
    crypto_data = generate_crypto_data(days=30, target_win_rate=0.75)
    poly_data = generate_polymarket_data(days=30)
    
    # 生成已知结果的信号
    signals = generate_known_outcome_signals(num_signals=100, win_rate=0.75)
    
    print("\n" + "=" * 60)
    print("✅ 数据生成完成！")
    print("=" * 60)
    print(f"\n数据位置:")
    print(f"  - 加密货币数据：{CRYPTO_DIR}")
    print(f"  - Polymarket 数据：{POLYMARKET_DIR}")
    print(f"  - 回测数据：{BACKTEST_DIR}")
    print(f"\n下一步:")
    print(f"  1. 运行回测：python3 scripts/arbitrage_backtest.py")
    print(f"  2. 查看报告：data/backtest/backtest_report_*.md")


if __name__ == "__main__":
    main()
