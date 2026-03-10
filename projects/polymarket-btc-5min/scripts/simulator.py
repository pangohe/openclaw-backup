#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 模拟交易系统
模拟 5 分钟 BTC 涨跌预测交易
"""

import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from technical_analysis import TechnicalAnalyzer

class PolymarketSimulator:
    """Polymarket 模拟交易器"""
    
    def __init__(self, initial_balance: float = 1000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = []
        self.trades = []
        self.stats = {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "total_profit": 0,
            "roi": 0
        }
        
    def place_bet(self, direction: str, amount: float, odds: float, entry_price: float):
        """
        下注
        
        Args:
            direction: "YES" (涨) 或 "NO" (跌)
            amount: 下注金额
            odds: 赔率 (如 0.65 表示 65% 概率)
            entry_price: 入场时 BTC 价格
        """
        if amount > self.balance:
            print(f"❌ 余额不足！当前余额：${self.balance:.2f}")
            return None
        
        # 扣除下注金额
        self.balance -= amount
        
        position = {
            "id": len(self.positions) + 1,
            "direction": direction,
            "amount": amount,
            "odds": odds,
            "entry_price": entry_price,
            "entry_time": datetime.now().isoformat(),
            "status": "OPEN",
            "payout": 0
        }
        
        self.positions.append(position)
        print(f"✅ 下注成功：{direction} ${amount:.2f} @ {odds:.2f} (BTC: ${entry_price:,.2f})")
        
        return position
    
    def settle_position(self, position_id: int, exit_price: float):
        """
        结算仓位
        
        Args:
            position_id: 仓位 ID
            exit_price: 结算时 BTC 价格
        """
        position = None
        for p in self.positions:
            if p["id"] == position_id and p["status"] == "OPEN":
                position = p
                break
        
        if not position:
            print(f"❌ 未找到仓位 {position_id}")
            return
        
        # 判断输赢
        entry_price = position["entry_price"]
        direction = position["direction"]
        
        if direction == "YES":
            # 预测涨
            if exit_price > entry_price:
                # 赢
                payout = position["amount"] / position["odds"]
                position["payout"] = payout
                self.balance += payout
                self.stats["wins"] += 1
                profit = payout - position["amount"]
            else:
                # 输
                position["payout"] = 0
                self.stats["losses"] += 1
                profit = -position["amount"]
        else:
            # 预测跌 (NO)
            if exit_price < entry_price:
                # 赢
                payout = position["amount"] / position["odds"]
                position["payout"] = payout
                self.balance += payout
                self.stats["wins"] += 1
                profit = payout - position["amount"]
            else:
                # 输
                position["payout"] = 0
                self.stats["losses"] += 1
                profit = -position["amount"]
        
        position["status"] = "CLOSED"
        position["exit_price"] = exit_price
        position["exit_time"] = datetime.now().isoformat()
        position["profit"] = profit
        
        self.trades.append(position)
        
        # 更新统计
        self.stats["total_trades"] += 1
        self.stats["total_profit"] += profit
        self.stats["win_rate"] = (self.stats["wins"] / self.stats["total_trades"]) * 100
        self.stats["roi"] = (self.stats["total_profit"] / self.initial_balance) * 100
        
        result = "🎉 赢" if profit > 0 else "💸 输"
        print(f"{result} | 仓位 #{position_id} | 盈利：${profit:+.2f} | 余额：${self.balance:.2f}")
    
    def get_stats(self) -> Dict:
        """获取统计数据"""
        return {
            **self.stats,
            "balance": self.balance,
            "initial_balance": self.initial_balance,
            "open_positions": len([p for p in self.positions if p["status"] == "OPEN"]),
            "total_positions": len(self.positions)
        }
    
    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print("📊 模拟交易统计")
        print("=" * 60)
        
        print(f"\n💰 账户信息:")
        print(f"   初始资金：${stats['initial_balance']:,.2f}")
        print(f"   当前余额：${stats['balance']:,.2f}")
        print(f"   总盈亏：${stats['total_profit']:+,.2f}")
        print(f"   ROI: {stats['roi']:+.2f}%")
        
        print(f"\n📈 交易统计:")
        print(f"   总交易数：{stats['total_trades']}")
        print(f"   盈利：{stats['wins']}")
        print(f"   亏损：{stats['losses']}")
        print(f"   胜率：{stats['win_rate']:.1f}%")
        print(f"   未平仓：{stats['open_positions']}")
        
        # 盈亏目标线
        print(f"\n🎯 胜率目标：75%")
        if stats['win_rate'] >= 75:
            print(f"✅ 已达到实盘标准！")
        else:
            gap = 75 - stats['win_rate']
            print(f"⏳ 距离实盘还差：{gap:.1f}%")
        
        print("\n" + "=" * 60)
    
    def save_results(self, output_file: str = "../data/simulation_results.json"):
        """保存结果"""
        results = {
            "stats": self.get_stats(),
            "trades": self.trades,
            "positions": self.positions,
            "timestamp": datetime.now().isoformat()
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 结果已保存：{output_path}")


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, klines: List[Dict], initial_balance: float = 1000.0):
        self.klines = klines
        self.simulator = PolymarketSimulator(initial_balance)
        self.analyzer = TechnicalAnalyzer()
        self.analyzer.klines = klines
        
    def run_backtest(self, bet_amount: float = 50.0, min_confidence: int = 60):
        """
        运行回测
        
        Args:
            bet_amount: 每笔下注金额
            min_confidence: 最小置信度 (%)
        """
        print(f"\n🚀 开始回测...")
        print(f"📊 数据量：{len(self.klines)} 条 K 线")
        print(f"💰 每笔下注：${bet_amount}")
        print(f"📈 最小置信度：{min_confidence}%")
        print("=" * 60)
        
        # 至少需要 30 条数据才能计算指标
        for i in range(30, len(self.klines) - 1):
            # 使用历史数据模拟
            self.analyzer.klines = self.klines[:i+1]
            
            # 生成信号
            signal = self.analyzer.generate_signal()
            
            # 检查是否符合交易条件
            if signal["signal"] in ["BUY", "SELL"] and signal["confidence"] >= min_confidence:
                # 确定方向
                direction = "YES" if signal["signal"] == "BUY" else "NO"
                
                # 模拟赔率 (根据置信度)
                odds = 0.5 + (signal["confidence"] / 200)  # 0.5-0.9
                
                # 入场价格
                entry_price = self.klines[i]["close"]
                
                # 下注
                position = self.simulator.place_bet(
                    direction=direction,
                    amount=bet_amount,
                    odds=odds,
                    entry_price=entry_price
                )
                
                if position:
                    # 5 分钟后结算 (下一条 K 线)
                    exit_price = self.klines[i+1]["close"]
                    self.simulator.settle_position(position["id"], exit_price)
        
        # 打印结果
        self.simulator.print_stats()
        self.simulator.save_results()
        
        return self.simulator.get_stats()


if __name__ == "__main__":
    print("=" * 60)
    print("🎮 Polymarket BTC 5 分钟模拟交易系统")
    print("=" * 60)
    
    # 查找 K 线文件
    data_dir = Path("../data")
    kline_files = list(data_dir.glob("klines_*.json"))
    
    if not kline_files:
        print("\n❌ 未找到 K 线数据文件")
        print("💡 请先运行 data_collector.py 收集数据")
        exit(1)
    
    # 使用最新文件
    latest_file = max(kline_files, key=lambda p: p.stat().st_mtime)
    print(f"\n📁 使用数据文件：{latest_file}")
    
    # 加载数据
    with open(latest_file, 'r') as f:
        klines = json.load(f)
    
    print(f"📊 加载 {len(klines)} 条 K 线数据")
    
    # 运行回测
    backtest = BacktestEngine(klines, initial_balance=1000.0)
    stats = backtest.run_backtest(bet_amount=50.0, min_confidence=60)
    
    # 保存统计
    stats_file = data_dir / "backtest_stats.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\n💾 统计已保存：{stats_file}")
