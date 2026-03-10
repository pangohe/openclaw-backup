#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略优化器
自动测试不同参数组合，寻找最优策略
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from technical_analysis import TechnicalAnalyzer
from simulator import BacktestEngine

class StrategyOptimizer:
    """策略优化器"""
    
    def __init__(self, klines: List[Dict]):
        self.klines = klines
        self.results = []
        
    def test_parameters(self, min_confidence_list: List[int], bet_amount_list: List[float]):
        """测试不同参数组合"""
        print("\n" + "=" * 70)
        print("🔬 策略参数优化测试")
        print("=" * 70)
        
        for min_conf in min_confidence_list:
            for bet_amount in bet_amount_list:
                print(f"\n📊 测试参数：置信度≥{min_conf}%, 下注${bet_amount}")
                print("-" * 70)
                
                # 运行回测
                backtest = BacktestEngine(self.klines, initial_balance=1000.0)
                stats = backtest.run_backtest(bet_amount=bet_amount, min_confidence=min_conf)
                
                # 记录结果
                result = {
                    "min_confidence": min_conf,
                    "bet_amount": bet_amount,
                    "win_rate": stats["win_rate"],
                    "total_profit": stats["total_profit"],
                    "roi": stats["roi"],
                    "total_trades": stats["total_trades"],
                    "timestamp": datetime.now().isoformat()
                }
                self.results.append(result)
        
        # 打印汇总
        self.print_summary()
        
        # 保存结果
        self.save_results()
        
        return self.results
    
    def print_summary(self):
        """打印汇总结果"""
        print("\n" + "=" * 70)
        print("📊 策略优化结果汇总")
        print("=" * 70)
        
        # 按胜率排序
        sorted_results = sorted(self.results, key=lambda x: x["win_rate"], reverse=True)
        
        print(f"\n{'置信度':<10} {'下注金额':<10} {'胜率':<10} {'交易数':<10} {'盈亏':<12} {'ROI':<10}")
        print("-" * 70)
        
        for r in sorted_results[:10]:  # 显示前 10 个
            profit_str = f"${r['total_profit']:+.2f}"
            print(f"{r['min_confidence']:<10} ${r['bet_amount']:<9} {r['win_rate']:>6.1f}%    {r['total_trades']:<10} {profit_str:<12} {r['roi']:>+6.2f}%")
        
        # 找出最佳策略
        best = sorted_results[0]
        print("\n" + "=" * 70)
        print("🏆 最佳策略")
        print("=" * 70)
        print(f"置信度阈值：≥{best['min_confidence']}%")
        print(f"每笔下注：${best['bet_amount']}")
        print(f"胜率：{best['win_rate']:.1f}%")
        print(f"总交易：{best['total_trades']} 笔")
        print(f"总盈亏：${best['total_profit']:+.2f}")
        print(f"ROI: {best['roi']:+.2f}%")
        
        if best['win_rate'] >= 75:
            print("\n✅ 已达到实盘标准！")
        else:
            gap = 75 - best['win_rate']
            print(f"\n⏳ 距离实盘还差：{gap:.1f}% 胜率")
            print("💡 建议：收集更多数据或优化技术指标")
        
        print("=" * 70)
    
    def save_results(self, output_file: str = "../data/strategy_optimization.json"):
        """保存优化结果"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        results_data = {
            "all_results": self.results,
            "best_strategy": max(self.results, key=lambda x: x["win_rate"]) if self.results else None,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(output_path, 'w') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 优化结果已保存：{output_path}")


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Polymarket BTC 5 分钟策略优化器")
    print("=" * 70)
    
    # 加载 K 线数据
    data_dir = Path("../data")
    kline_files = list(data_dir.glob("klines_*.json"))
    
    if not kline_files:
        print("\n❌ 未找到 K 线数据文件")
        print("💡 请先收集数据")
        exit(1)
    
    latest_file = max(kline_files, key=lambda p: p.stat().st_mtime)
    print(f"\n📁 使用数据文件：{latest_file}")
    
    with open(latest_file, 'r') as f:
        klines = json.load(f)
    
    print(f"📊 加载 {len(klines)} 条 K 线数据")
    
    if len(klines) < 200:
        print(f"\n⚠️  警告：数据量较少 ({len(klines)} 条)")
        print(f"💡 建议：至少 200 条 K 线才能获得可靠结果")
        print(f"   当前数据约等于 {len(klines) * 5 / 60:.1f} 小时")
    
    # 创建优化器
    optimizer = StrategyOptimizer(klines)
    
    # 使用默认参数测试
    min_confidence_list = [50, 60, 70, 80]
    bet_amount_list = [25, 50, 100]
    
    print(f"\n📋 测试计划:")
    print(f"   置信度阈值：{min_confidence_list}")
    print(f"   下注金额：{bet_amount_list}")
    print(f"   总测试次数：{len(min_confidence_list) * len(bet_amount_list)} 次")
    print(f"\n🚀 开始自动测试...\n")
    
    optimizer.test_parameters(min_confidence_list, bet_amount_list)
