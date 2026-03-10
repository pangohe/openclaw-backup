#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版回测系统
- 更小下注金额 ($10)
- 更高置信度阈值 (80%)
- 更好嘅资金管理
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from advanced_technical_analysis import AdvancedTechnicalAnalyzer

class OptimizedSimulator:
    """优化版模拟器"""
    
    def __init__(self, initial_balance: float = 1000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.trades = []
        self.stats = {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "total_profit": 0,
            "roi": 0,
            "max_drawdown": 0,
            "sharpe_ratio": 0
        }
        self.balance_history = []
        
    def place_bet(self, direction: str, amount: float, odds: float, entry_price: float):
        """下注"""
        # 动态调整下注金额 (不超过余额 5%)
        actual_amount = min(amount, self.balance * 0.05)
        
        if actual_amount < 1:
            return None
        
        self.balance -= actual_amount
        
        position = {
            "id": len(self.trades) + 1,
            "direction": direction,
            "amount": actual_amount,
            "odds": odds,
            "entry_price": entry_price,
            "entry_time": datetime.now().isoformat(),
            "status": "OPEN"
        }
        
        return position
    
    def settle_position(self, position: Dict, exit_price: float) -> float:
        """结算仓位"""
        entry_price = position["entry_price"]
        direction = position["direction"]
        amount = position["amount"]
        odds = position["odds"]
        
        if direction == "YES":
            won = exit_price > entry_price
        else:
            won = exit_price < entry_price
        
        if won:
            payout = amount / odds
            profit = payout - amount
            self.balance += payout
            self.stats["wins"] += 1
        else:
            payout = 0
            profit = -amount
            self.stats["losses"] += 1
        
        position["status"] = "CLOSED"
        position["exit_price"] = exit_price
        position["profit"] = profit
        position["exit_time"] = datetime.now().isoformat()
        
        self.trades.append(position)
        self.balance_history.append(self.balance)
        
        # 更新统计
        self.stats["total_trades"] += 1
        self.stats["total_profit"] += profit
        self.stats["win_rate"] = (self.stats["wins"] / self.stats["total_trades"]) * 100
        self.stats["roi"] = (self.stats["total_profit"] / self.initial_balance) * 100
        
        # 计算最大回撤
        peak = max(self.balance_history) if self.balance_history else self.initial_balance
        drawdown = (peak - self.balance) / peak * 100
        self.stats["max_drawdown"] = max(self.stats["max_drawdown"], drawdown)
        
        return profit
    
    def print_stats(self):
        """打印统计"""
        stats = self.stats
        
        print("\n" + "=" * 70)
        print("📊 优化版回测统计")
        print("=" * 70)
        
        print(f"\n💰 账户信息:")
        print(f"   初始资金：${stats.get('initial_balance', self.initial_balance):,.2f}")
        print(f"   最终余额：${self.balance:,.2f}")
        print(f"   总盈亏：${stats['total_profit']:+,.2f}")
        print(f"   ROI: {stats['roi']:+.2f}%")
        print(f"   最大回撤：{stats['max_drawdown']:.2f}%")
        
        print(f"\n📈 交易统计:")
        print(f"   总交易数：{stats['total_trades']}")
        print(f"   盈利：{stats['wins']} ({stats['win_rate']:.1f}%)")
        print(f"   亏损：{stats['losses']} ({100-stats['win_rate']:.1f}%)")
        
        print(f"\n🎯 胜率目标：75%")
        if stats['win_rate'] >= 75:
            print(f"   ✅ 已达到实盘标准！")
        else:
            gap = 75 - stats['win_rate']
            print(f"   ⏳ 距离实盘还差：{gap:.1f}%")
        
        print("=" * 70)
    
    def save_results(self, output_file: str = "../data/optimized_backtest.json"):
        """保存结果"""
        results = {
            "stats": {
                **self.stats,
                "balance": self.balance,
                "initial_balance": self.initial_balance
            },
            "trades": self.trades[-100:],  # 只保存最后 100 笔
            "balance_history": self.balance_history[-1000:],  # 只保存最后 1000 个
            "timestamp": datetime.now().isoformat()
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 结果已保存：{output_path}")


def run_optimized_backtest(klines: List[Dict], bet_amount: float = 10.0, min_confidence: int = 80):
    """运行优化版回测"""
    print(f"\n🚀 开始优化版回测...")
    print(f"📊 数据量：{len(klines):,} 条 K 线")
    print(f"💰 每笔下注：${bet_amount} (动态调整)")
    print(f"📈 最小置信度：{min_confidence}%")
    print("=" * 70)
    
    simulator = OptimizedSimulator(initial_balance=1000.0)
    analyzer = AdvancedTechnicalAnalyzer()
    
    trades_count = 0
    
    # 至少需要 50 条数据才能计算高级指标
    for i in range(50, len(klines) - 1):
        analyzer.klines = klines[:i+1]
        
        # 生成信号
        signal = analyzer.generate_advanced_signal()
        
        # 检查是否符合交易条件
        if signal["signal"] in ["BUY", "SELL"] and signal["confidence"] >= min_confidence:
            direction = "YES" if signal["signal"] == "BUY" else "NO"
            
            # 根据置信度调整赔率估计
            odds = 0.5 + (signal["confidence"] / 200)
            
            entry_price = klines[i]["close"]
            
            # 下注
            position = simulator.place_bet(
                direction=direction,
                amount=bet_amount,
                odds=odds,
                entry_price=entry_price
            )
            
            if position:
                # 5 分钟后结算
                exit_price = klines[i+1]["close"]
                profit = simulator.settle_position(position, exit_price)
                trades_count += 1
                
                # 每 100 笔交易打印进度
                if trades_count % 100 == 0:
                    print(f"   已交易 {trades_count} 笔 | 余额：${simulator.balance:.2f} | 胜率：{simulator.stats['win_rate']:.1f}%")
    
    # 打印结果
    simulator.print_stats()
    simulator.save_results()
    
    return simulator.stats


if __name__ == "__main__":
    print("=" * 70)
    print("🎯 优化版回测系统")
    print("=" * 70)
    
    # 加载数据
    data_dir = Path("../data")
    kline_file = data_dir / "klines_history.json"
    
    if not kline_file.exists():
        print(f"\n❌ 数据文件不存在：{kline_file}")
        exit(1)
    
    with open(kline_file, 'r') as f:
        klines = json.load(f)
    
    print(f"\n📊 加载 {len(klines):,} 条 K 线数据")
    print(f"📅 时间范围：{klines[0]['timestamp']} 至 {klines[-1]['timestamp']}")
    
    # 运行回测
    stats = run_optimized_backtest(
        klines,
        bet_amount=10.0,      # 降低到$10
        min_confidence=80     # 提高到 80%
    )
    
    print(f"\n✅ 回测完成！")
