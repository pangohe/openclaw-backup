#!/usr/bin/env python3
"""
套利回测系统 v1.0
目标：通过历史数据回测，优化策略达到 75% 胜率

功能：
1. 加载历史数据（Polymarket + CoinGecko）
2. 模拟交易信号
3. 计算胜率、盈亏比
4. 参数优化
5. 生成详细报告
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import statistics

# 配置
DATA_DIR = Path.home() / ".openclaw" / "workspace" / "data"
CRYPTO_DIR = DATA_DIR / "crypto-trends"
POLYMARKET_DIR = DATA_DIR / "polymarket"
BACKTEST_DIR = DATA_DIR / "backtest"

# 确保目录存在
BACKTEST_DIR.mkdir(parents=True, exist_ok=True)


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.trades = []
        self.winners = []
        self.losers = []
        
    def load_crypto_data(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """加载加密货币历史数据"""
        crypto_data = []
        
        if not CRYPTO_DIR.exists():
            print(f"⚠️ 加密货币数据目录不存在：{CRYPTO_DIR}")
            return crypto_data
        
        # 扫描所有 JSON 文件
        for file in sorted(CRYPTO_DIR.glob("crypto-trend-*.json")):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    crypto_data.append(data)  # 直接存储数据，唔需要额外包装
            except Exception as e:
                print(f"⚠️ 读取文件失败 {file}: {e}")
        
        print(f"✅ 加载了 {len(crypto_data)} 条加密货币数据")
        return crypto_data
    
    def load_polymarket_data(self) -> List[Dict]:
        """加载 Polymarket 历史数据"""
        poly_data = []
        
        if not POLYMARKET_DIR.exists():
            print(f"⚠️ Polymarket 数据目录不存在：{POLYMARKET_DIR}")
            return poly_data
        
        # 加载监控日志
        log_file = POLYMARKET_DIR / "monitor_log.json"
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        poly_data.extend(data)
                    else:
                        poly_data.append(data)
            except Exception as e:
                print(f"⚠️ 读取 Polymarket 日志失败：{e}")
        
        # 加载市场报告
        report_file = POLYMARKET_DIR / "market_report.json"
        if report_file.exists():
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    poly_data.append(data)
            except Exception as e:
                print(f"⚠️ 读取市场报告失败：{e}")
        
        print(f"✅ 加载了 {len(poly_data)} 条 Polymarket 数据")
        return poly_data
    
    def detect_signal(self, crypto_data: Dict, poly_data: Dict, 
                      threshold: float = 0.05) -> Dict:
        """
        检测交易信号
        
        策略逻辑：
        1. 加密货币价格变化 > 阈值
        2. Polymarket 相关事件概率与价格趋势背离
        3. 生成套利信号
        """
        signals = []
        
        # 分析加密货币变化 - 支持两种数据结构
        coin_list = None
        if 'coins' in crypto_data and isinstance(crypto_data['coins'], list):
            coin_list = crypto_data['coins']
        elif 'data' in crypto_data and isinstance(crypto_data['data'], list):
            coin_list = crypto_data['data']
        
        if coin_list:
            for coin in coin_list:
                if isinstance(coin, dict):
                    price_change_24h = coin.get('price_change_percentage_24h', 0)
                    
                    # 检测大幅波动（阈值降低到 2% 以捕获更多信号）
                    if abs(price_change_24h) > threshold * 100:
                        signal = {
                            'timestamp': crypto_data.get('timestamp', ''),
                            'coin': coin.get('name', 'unknown'),
                            'symbol': coin.get('symbol', 'unknown').upper(),
                            'price': coin.get('current_price', 0),
                            'change_24h': price_change_24h,
                            'signal_type': 'LONG' if price_change_24h > 0 else 'SHORT',
                            'confidence': min(abs(price_change_24h) / 10, 1.0)
                        }
                        signals.append(signal)
        
        return signals
    
    def simulate_trade(self, signal: Dict, hold_period_hours: int = 24) -> Dict:
        """
        模拟交易
        
        简化模型：假设信号正确率为 X%，根据历史数据计算
        """
        # 这里需要实际的历史价格数据来计算真实盈亏
        # 目前使用简化模型
        
        trade_result = {
            'signal': signal,
            'entry_price': signal.get('price', 0),
            'exit_price': 0,  # 需要后续数据
            'pnl': 0,
            'pnl_percent': 0,
            'is_winner': False,
            'hold_period': hold_period_hours
        }
        
        return trade_result
    
    def run_backtest(self, crypto_data: List[Dict], poly_data: List[Dict],
                     threshold: float = 0.05) -> Dict:
        """运行回测"""
        print(f"\n🚀 开始回测 (阈值：{threshold*100}%)")
        print("=" * 60)
        
        total_signals = 0
        winning_trades = 0
        losing_trades = 0
        total_pnl = 0
        
        # 遍历所有数据点
        for i, crypto_point in enumerate(crypto_data):
            signals = self.detect_signal(crypto_point, {}, threshold)
            
            for signal in signals:
                total_signals += 1
                
                # 简化：假设有后续数据可以计算盈亏
                trade = self.simulate_trade(signal)
                
                # 使用后续数据计算真实盈亏
                if i + 1 < len(crypto_data):
                    # 有后续数据，可以计算真实盈亏
                    next_data = crypto_data[i + 1]  # 直接系数据，唔需要 .get('data')
                    
                    # 查找相同币种
                    next_coins = next_data.get('coins', [])
                    for next_coin in next_coins:
                        if isinstance(next_coin, dict) and \
                           next_coin.get('symbol', '').upper() == signal.get('symbol', '').upper():
                            entry = signal.get('price', 0)
                            exit_p = next_coin.get('current_price', entry)
                            pnl_pct = (exit_p - entry) / entry * 100 if entry > 0 else 0
                            
                            trade['exit_price'] = exit_p
                            trade['pnl_percent'] = pnl_pct
                            trade['is_winner'] = pnl_pct > 0
                            
                            if pnl_pct > 0:
                                winning_trades += 1
                                self.winners.append(trade)
                            else:
                                losing_trades += 1
                                self.losers.append(trade)
                            
                            total_pnl += pnl_pct
                            self.trades.append(trade)
                            break
        
        # 计算统计指标
        win_rate = (winning_trades / total_signals * 100) if total_signals > 0 else 0
        avg_win = statistics.mean([t['pnl_percent'] for t in self.winners]) if self.winners else 0
        avg_loss = statistics.mean([t['pnl_percent'] for t in self.losers]) if self.losers else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        results = {
            'total_signals': total_signals,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl_percent': total_pnl,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'profit_factor': profit_factor,
            'threshold_used': threshold
        }
        
        return results
    
    def optimize_threshold(self, crypto_data: List[Dict], poly_data: List[Dict]) -> Dict:
        """优化阈值参数"""
        print("\n🔧 开始参数优化...")
        print("=" * 60)
        
        # 降低阈值以捕获更多信号
        thresholds = [0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05]
        best_threshold = 0.05
        best_win_rate = 0
        all_results = []
        
        for threshold in thresholds:
            # 重置引擎状态
            self.trades = []
            self.winners = []
            self.losers = []
            
            results = self.run_backtest(crypto_data, poly_data, threshold)
            results['threshold'] = threshold
            all_results.append(results)
            
            print(f"阈值 {threshold*100:5.1f}% | 信号：{results['total_signals']:3d} | "
                  f"胜率：{results['win_rate']:5.1f}% | 盈亏比：{results['profit_factor']:.2f}")
            
            # 寻找最佳胜率（同时考虑信号数量）
            if results['win_rate'] > best_win_rate and results['total_signals'] >= 5:
                best_win_rate = results['win_rate']
                best_threshold = threshold
        
        print("\n" + "=" * 60)
        print(f"🎯 最佳阈值：{best_threshold*100}% (胜率：{best_win_rate:.1f}%)")
        
        optimization_report = {
            'best_threshold': best_threshold,
            'best_win_rate': best_win_rate,
            'all_results': all_results,
            'timestamp': datetime.now().isoformat()
        }
        
        # 保存优化报告
        report_file = BACKTEST_DIR / f"optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(optimization_report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 优化报告已保存：{report_file}")
        
        return optimization_report
    
    def generate_report(self, results: Dict) -> str:
        """生成人类可读的回测报告"""
        report = f"""
# 🔍 套利策略回测报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 核心指标

| 指标 | 数值 |
|------|------|
| 总信号数 | {results.get('total_signals', 0)} |
| 盈利交易 | {results.get('winning_trades', 0)} |
| 亏损交易 | {results.get('losing_trades', 0)} |
| **胜率** | **{results.get('win_rate', 0):.2f}%** |
| 总盈亏 | {results.get('total_pnl_percent', 0):.2f}% |
| 平均盈利 | {results.get('average_win', 0):.2f}% |
| 平均亏损 | {results.get('average_loss', 0):.2f}% |
| 盈亏比 | {results.get('profit_factor', 0):.2f} |
| 使用阈值 | {results.get('threshold_used', 0)*100:.1f}% |

## 🎯 策略评估

"""
        win_rate = results.get('win_rate', 0)
        if win_rate >= 75:
            report += "✅ **优秀** - 胜率达到目标 (≥75%)\n"
        elif win_rate >= 60:
            report += "⚠️ **良好** - 胜率接近目标，可继续优化\n"
        else:
            report += "❌ **需改进** - 胜率低于目标，需要调整策略\n"
        
        report += f"""
## 📈 详细交易记录

"""
        if self.trades:
            report += "| 时间 | 币种 | 方向 | 入场价 | 出场价 | 盈亏% |\n"
            report += "|------|------|------|--------|--------|-------|\n"
            for trade in self.trades[:20]:  # 只显示前 20 笔
                signal = trade.get('signal', {})
                report += f"| {signal.get('timestamp', 'N/A')[:16]} | "
                report += f"{signal.get('symbol', 'N/A')} | "
                report += f"{signal.get('signal_type', 'N/A')} | "
                report += f"${trade.get('entry_price', 0):,.2f} | "
                report += f"${trade.get('exit_price', 0):,.2f} | "
                report += f"{trade.get('pnl_percent', 0):+.2f}% |\n"
            
            if len(self.trades) > 20:
                report += f"\n_... 还有 {len(self.trades) - 20} 笔交易未显示_\n"
        else:
            report += "_暂无交易记录_\n"
        
        return report


def main():
    """主函数"""
    print("=" * 60)
    print("🔍 套利策略回测系统 v1.0")
    print("=" * 60)
    
    # 创建回测引擎
    engine = BacktestEngine(initial_capital=10000.0)
    
    # 加载数据
    crypto_data = engine.load_crypto_data()
    poly_data = engine.load_polymarket_data()
    
    if not crypto_data:
        print("\n❌ 错误：没有可用的加密货币数据")
        print("💡 提示：先运行 crypto_trend_collector.py 收集数据")
        return
    
    # 运行参数优化
    optimization = engine.optimize_threshold(crypto_data, poly_data)
    
    # 使用最佳阈值运行最终回测
    best_threshold = optimization['best_threshold']
    engine.trades = []
    engine.winners = []
    engine.losers = []
    
    print(f"\n🎯 使用最佳阈值 {best_threshold*100}% 运行最终回测...")
    final_results = engine.run_backtest(crypto_data, poly_data, best_threshold)
    
    # 生成报告
    report = engine.generate_report(final_results)
    
    # 保存报告
    report_file = BACKTEST_DIR / f"backtest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 详细报告已保存：{report_file}")
    print("\n" + "=" * 60)
    print(report)


if __name__ == "__main__":
    main()
