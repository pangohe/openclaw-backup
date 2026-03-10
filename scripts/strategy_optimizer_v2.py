#!/usr/bin/env python3
"""
套利策略优化器 v2.0 - 多因子模型
目标：通过多因子分析，将胜率从 48% 提升到 75%

优化方向：
1. 多因子确认（价格 + 成交量 + 波动率）
2. 时间过滤（避开低质量时段）
3. 趋势过滤（只在明确趋势时交易）
4. 动态阈值（根据市场状态调整）
5. 出场优化（止损/止盈策略）
"""

import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import math

# 配置
DATA_DIR = Path.home() / ".openclaw" / "workspace" / "data"
CRYPTO_DIR = DATA_DIR / "crypto-trends"
POLYMARKET_DIR = DATA_DIR / "polymarket"
BACKTEST_DIR = DATA_DIR / "backtest"
OPTIMIZATION_DIR = BACKTEST_DIR / "optimization_v2"

# 确保目录存在
OPTIMIZATION_DIR.mkdir(parents=True, exist_ok=True)


class MultiFactorStrategy:
    """多因子套利策略"""
    
    def __init__(self):
        # 策略参数（可优化）
        self.params = {
            # 价格因子
            'price_change_threshold': 0.03,  # 价格变化阈值 3%
            'volume_confirmation': True,     # 需要成交量确认
            'volume_multiplier': 1.5,        # 成交量倍数（高于平均）
            
            # 波动率因子
            'volatility_filter': True,       # 启用波动率过滤
            'min_volatility': 0.02,          # 最小波动率 2%
            'max_volatility': 0.15,          # 最大波动率 15%
            
            # 时间因子
            'time_filter': False,            # 暂时不启用
            'trading_hours': (9, 22),        # 交易时段
            
            # 趋势因子
            'trend_confirmation': True,      # 需要趋势确认
            'trend_periods': 3,              # 看几个周期确认趋势
            
            # 出场策略
            'stop_loss': 0.03,               # 止损 3%
            'take_profit': 0.06,             # 止盈 6%
            'time_stop_hours': 12,           # 时间止损（小时）
        }
        
        self.trades = []
        self.winners = []
        self.losers = []
    
    def load_crypto_data(self) -> List[Dict]:
        """加载加密货币数据"""
        crypto_data = []
        
        if not CRYPTO_DIR.exists():
            return crypto_data
        
        for file in sorted(CRYPTO_DIR.glob("crypto-trend-*.json")):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    crypto_data.append(data)
            except Exception as e:
                pass
        
        return crypto_data
    
    def calculate_volatility(self, coin_data: Dict) -> float:
        """计算波动率（24 小时高低价差）"""
        high = coin_data.get('high_24h', 0)
        low = coin_data.get('low_24h', 0)
        current = coin_data.get('current_price', 1)
        
        if high > 0 and low > 0 and current > 0:
            return (high - low) / current
        return 0
    
    def check_volume_confirmation(self, coin_data: Dict, avg_volume: float) -> bool:
        """检查成交量确认"""
        current_volume = coin_data.get('total_volume', 0)
        
        if avg_volume > 0:
            return current_volume >= avg_volume * self.params['volume_multiplier']
        return False
    
    def check_trend(self, crypto_data: List[Dict], coin_symbol: str, 
                    current_idx: int, signal_type: str) -> bool:
        """检查趋势确认"""
        if not self.params['trend_confirmation']:
            return True
        
        periods = self.params['trend_periods']
        if current_idx < periods:
            return True  # 数据不足，默认通过
        
        # 检查过去几个周期的价格趋势
        prices = []
        for i in range(periods + 1):
            idx = current_idx - i
            if idx >= 0:
                data = crypto_data[idx]
                coins = data.get('coins', [])
                for coin in coins:
                    if coin.get('symbol', '').upper() == coin_symbol.upper():
                        prices.append(coin.get('current_price', 0))
                        break
        
        if len(prices) < periods + 1:
            return True
        
        # 计算趋势
        if signal_type == 'LONG':
            # 看涨信号：价格应该在上升
            return prices[0] > prices[-1]
        else:
            # 看跌信号：价格应该在下降
            return prices[0] < prices[-1]
    
    def detect_signal(self, crypto_data: List[Dict], current_idx: int, 
                      threshold: float = 0.03) -> List[Dict]:
        """
        检测交易信号（多因子确认）
        """
        signals = []
        
        if current_idx >= len(crypto_data):
            return signals
        
        current_data = crypto_data[current_idx]
        coins = current_data.get('coins', [])
        
        # 计算平均成交量（用于确认）
        avg_volume = 0
        if current_idx >= 5:
            volumes = []
            for i in range(5):
                idx = current_idx - i
                if idx >= 0:
                    data = crypto_data[idx]
                    for coin in data.get('coins', []):
                        vol = coin.get('total_volume', 0)
                        if vol > 0:
                            volumes.append(vol)
            avg_volume = statistics.mean(volumes) if volumes else 0
        
        for coin in coins:
            if not isinstance(coin, dict):
                continue
            
            symbol = coin.get('symbol', '').upper()
            price_change = coin.get('price_change_percentage_24h', 0)
            
            # 因子 1: 价格变化阈值
            if abs(price_change) < threshold * 100:
                continue
            
            # 因子 2: 波动率过滤
            if self.params['volatility_filter']:
                volatility = self.calculate_volatility(coin)
                if volatility < self.params['min_volatility'] or \
                   volatility > self.params['max_volatility']:
                    continue
            
            # 因子 3: 成交量确认
            if self.params['volume_confirmation'] and avg_volume > 0:
                if not self.check_volume_confirmation(coin, avg_volume):
                    continue
            
            # 因子 4: 趋势确认
            signal_type = 'LONG' if price_change > 0 else 'SHORT'
            if not self.check_trend(crypto_data, symbol, current_idx, signal_type):
                continue
            
            # 所有因子通过，生成信号
            signal = {
                'index': current_idx,
                'timestamp': current_data.get('timestamp', ''),
                'coin': coin.get('name', 'unknown'),
                'symbol': symbol,
                'price': coin.get('current_price', 0),
                'change_24h': price_change,
                'signal_type': signal_type,
                'volatility': self.calculate_volatility(coin),
                'volume': coin.get('total_volume', 0),
                'confidence': min(abs(price_change) / 10, 1.0),
                'factors': {
                    'price_change': True,
                    'volatility': True,
                    'volume': True,
                    'trend': True
                }
            }
            signals.append(signal)
        
        return signals
    
    def simulate_trade(self, signal: Dict, crypto_data: List[Dict], 
                       start_idx: int) -> Optional[Dict]:
        """
        模拟交易（带止损/止盈）
        """
        entry_price = signal.get('price', 0)
        signal_type = signal.get('signal_type', 'LONG')
        
        if entry_price <= 0:
            return None
        
        # 遍历后续数据，找出场点
        stop_loss_pct = self.params['stop_loss']
        take_profit_pct = self.params['take_profit']
        
        exit_price = 0
        exit_reason = ''
        pnl_pct = 0
        hold_periods = 0
        
        for i in range(start_idx + 1, min(start_idx + 24, len(crypto_data))):
            hold_periods += 1
            
            # 查找后续价格
            next_data = crypto_data[i]
            next_coins = next_data.get('coins', [])
            
            for next_coin in next_coins:
                if next_coin.get('symbol', '').upper() != signal.get('symbol', '').upper():
                    continue
                
                current_price = next_coin.get('current_price', entry_price)
                
                # 计算盈亏
                if signal_type == 'LONG':
                    pnl_pct = (current_price - entry_price) / entry_price * 100
                else:
                    pnl_pct = (entry_price - current_price) / entry_price * 100
                
                # 检查止损
                if pnl_pct <= -stop_loss_pct * 100:
                    exit_price = current_price
                    exit_reason = 'STOP_LOSS'
                    break
                
                # 检查止盈
                if pnl_pct >= take_profit_pct * 100:
                    exit_price = current_price
                    exit_reason = 'TAKE_PROFIT'
                    break
            
            if exit_price > 0:
                break
        
        # 如果没有触发止损/止盈，使用最后一个价格
        if exit_price == 0:
            # 时间止损
            if hold_periods >= self.params['time_stop_hours']:
                exit_price = current_price
                exit_reason = 'TIME_STOP'
            else:
                # 持有到最后
                exit_price = current_price
                exit_reason = 'END_OF_DATA'
        
        trade = {
            'signal': signal,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'pnl_percent': pnl_pct,
            'is_winner': pnl_pct > 0,
            'exit_reason': exit_reason,
            'hold_periods': hold_periods
        }
        
        return trade
    
    def run_backtest(self, crypto_data: List[Dict], 
                     threshold: float = 0.03) -> Dict:
        """运行回测"""
        print(f"\n🚀 运行多因子策略回测 (阈值：{threshold*100}%)")
        print("=" * 60)
        
        self.trades = []
        self.winners = []
        self.losers = []
        
        total_signals = 0
        
        # 遍历所有数据点
        for i in range(len(crypto_data)):
            signals = self.detect_signal(crypto_data, i, threshold)
            
            for signal in signals:
                total_signals += 1
                trade = self.simulate_trade(signal, crypto_data, i)
                
                if trade:
                    self.trades.append(trade)
                    if trade['is_winner']:
                        self.winners.append(trade)
                    else:
                        self.losers.append(trade)
        
        # 计算统计指标
        win_rate = (len(self.winners) / total_signals * 100) if total_signals > 0 else 0
        avg_win = statistics.mean([t['pnl_percent'] for t in self.winners]) if self.winners else 0
        avg_loss = statistics.mean([t['pnl_percent'] for t in self.losers]) if self.losers else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # 分析出场原因
        exit_reasons = {}
        for trade in self.trades:
            reason = trade.get('exit_reason', 'UNKNOWN')
            exit_reasons[reason] = exit_reasons.get(reason, 0) + 1
        
        results = {
            'total_signals': total_signals,
            'winning_trades': len(self.winners),
            'losing_trades': len(self.losers),
            'win_rate': win_rate,
            'total_pnl_percent': sum([t['pnl_percent'] for t in self.trades]),
            'average_win': avg_win,
            'average_loss': avg_loss,
            'profit_factor': profit_factor,
            'threshold_used': threshold,
            'exit_reasons': exit_reasons,
            'params_used': self.params.copy()
        }
        
        return results
    
    def optimize_params(self, crypto_data: List[Dict]) -> Dict:
        """参数优化"""
        print("\n🔧 开始参数优化...")
        print("=" * 60)
        
        # 测试不同的阈值组合
        thresholds = [0.02, 0.025, 0.03, 0.035, 0.04, 0.05]
        stop_losses = [0.02, 0.03, 0.04]
        take_profits = [0.04, 0.06, 0.08]
        
        best_result = None
        best_win_rate = 0
        
        test_count = 0
        for threshold in thresholds:
            for sl in stop_losses:
                for tp in take_profits:
                    # 更新参数
                    self.params['price_change_threshold'] = threshold
                    self.params['stop_loss'] = sl
                    self.params['take_profit'] = tp
                    
                    result = self.run_backtest(crypto_data, threshold)
                    test_count += 1
                    
                    # 寻找最佳胜率（同时考虑交易数量）
                    if result['win_rate'] > best_win_rate and result['total_signals'] >= 50:
                        best_win_rate = result['win_rate']
                        best_result = result.copy()
                    
                    if test_count % 10 == 0:
                        print(f"已测试 {test_count} 组参数... 当前最佳：{best_win_rate:.1f}%")
        
        print(f"\n✅ 完成 {test_count} 组参数测试")
        print(f"🎯 最佳胜率：{best_win_rate:.1f}%")
        
        return best_result
    
    def generate_report(self, results: Dict) -> str:
        """生成回测报告"""
        report = f"""
# 📊 多因子策略回测报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 策略参数

| 参数 | 值 |
|------|-----|
| 价格变化阈值 | {self.params['price_change_threshold']*100}% |
| 止损 | {self.params['stop_loss']*100}% |
| 止盈 | {self.params['take_profit']*100}% |
| 时间止损 | {self.params['time_stop_hours']} 小时 |
| 波动率过滤 | {'启用' if self.params['volatility_filter'] else '禁用'} |
| 成交量确认 | {'启用' if self.params['volume_confirmation'] else '禁用'} |
| 趋势确认 | {'启用' if self.params['trend_confirmation'] else '禁用'} |

## 📈 核心指标

| 指标 | 数值 | 目标 |
|------|------|------|
| 总信号数 | {results.get('total_signals', 0)} | - |
| 盈利交易 | {results.get('winning_trades', 0)} | - |
| 亏损交易 | {results.get('losing_trades', 0)} | - |
| **胜率** | **{results.get('win_rate', 0):.2f}%** | **75%** |
| 总盈亏 | {results.get('total_pnl_percent', 0):.2f}% | - |
| 平均盈利 | {results.get('average_win', 0):.2f}% | - |
| 平均亏损 | {results.get('average_loss', 0):.2f}% | - |
| 盈亏比 | {results.get('profit_factor', 0):.2f} | >1.5 |

## 🚪 出场原因分析

"""
        exit_reasons = results.get('exit_reasons', {})
        for reason, count in sorted(exit_reasons.items(), key=lambda x: x[1], reverse=True):
            pct = count / results.get('total_signals', 1) * 100
            report += f"- {reason}: {count} 次 ({pct:.1f}%)\n"
        
        # 策略评估
        win_rate = results.get('win_rate', 0)
        report += f"""
## 🎯 策略评估

"""
        if win_rate >= 75:
            report += "✅ **优秀** - 胜率达到目标 (≥75%)，可以进入实盘测试！\n"
        elif win_rate >= 65:
            report += "⚠️ **良好** - 胜率接近目标，继续优化参数\n"
        elif win_rate >= 55:
            report += "⚠️ **有潜力** - 需要进一步优化策略\n"
        else:
            report += "❌ **需改进** - 胜率较低，需要重新设计策略\n"
        
        report += f"""
## 📝 详细交易记录（前 20 笔）

"""
        if self.trades:
            report += "| 时间 | 币种 | 方向 | 入场 | 出场 | 盈亏% | 出场原因 |\n"
            report += "|------|------|------|------|------|-------|----------|\n"
            for trade in self.trades[:20]:
                signal = trade.get('signal', {})
                report += f"| {signal.get('timestamp', 'N/A')[:16]} | "
                report += f"{signal.get('symbol', 'N/A')} | "
                report += f"{signal.get('signal_type', 'N/A')} | "
                report += f"${trade.get('entry_price', 0):,.2f} | "
                report += f"${trade.get('exit_price', 0):,.2f} | "
                report += f"{trade.get('pnl_percent', 0):+.2f}% | "
                report += f"{trade.get('exit_reason', 'N/A')} |\n"
        else:
            report += "_暂无交易记录_\n"
        
        return report


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 套利策略优化器 v2.0 - 多因子模型")
    print("=" * 60)
    
    # 创建策略
    strategy = MultiFactorStrategy()
    
    # 加载数据
    print("\n📂 加载数据...")
    crypto_data = strategy.load_crypto_data()
    
    if not crypto_data:
        print("\n❌ 错误：没有可用的加密货币数据")
        return
    
    print(f"✅ 加载了 {len(crypto_data)} 条数据")
    
    # 运行参数优化
    best_result = strategy.optimize_params(crypto_data)
    
    if best_result:
        # 生成报告
        report = strategy.generate_report(best_result)
        
        # 保存报告
        report_file = OPTIMIZATION_DIR / f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 详细报告已保存：{report_file}")
        print("\n" + "=" * 60)
        print(report)
    else:
        print("\n❌ 优化失败，未找到有效结果")


if __name__ == "__main__":
    main()
