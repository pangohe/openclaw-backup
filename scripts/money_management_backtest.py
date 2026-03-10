#!/usr/bin/env python3
"""
资金管理系统回测 v3.0
目标：测试不同资金管理策略下的长期表现

功能：
1. 固定仓位测试（5 元/次）
2. 复利增长测试
3. 凯利公式优化
4. 破产风险评估
5. 最大回撤分析
6. 夏普比率计算
"""

import json
import statistics
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 配置
DATA_DIR = Path.home() / ".openclaw" / "workspace" / "data"
CRYPTO_DIR = DATA_DIR / "crypto-trends"
BACKTEST_DIR = DATA_DIR / "backtest"
MONEY_MGMT_DIR = BACKTEST_DIR / "money_management"

# 确保目录存在
MONEY_MGMT_DIR.mkdir(parents=True, exist_ok=True)


class MoneyManagementBacktest:
    """资金管理回测系统"""
    
    def __init__(self, initial_capital: float = 1000.0, 
                 position_size: float = 5.0,
                 position_type: str = 'fixed'):
        """
        参数:
            initial_capital: 初始本金（默认 1000 元）
            position_size: 每次交易金额（默认 5 元）
            position_type: 仓位类型
                - 'fixed': 固定仓位
                - 'percentage': 固定比例（如每次 1%）
                - 'kelly': 凯利公式优化
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position_size = position_size
        self.position_type = position_type
        self.position_percentage = 0.01  # 1% for percentage type
        
        # 交易记录
        self.trades = []
        self.equity_curve = []  # 资金曲线
        self.drawdowns = []  # 回撤记录
        
        # 统计指标
        self.total_trades = 0
        self.winners = 0
        self.losers = 0
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.max_consecutive_wins = 0
        self.max_consecutive_losses = 0
        self.max_drawdown = 0
        self.max_drawdown_pct = 0
        self.peak_capital = initial_capital
    
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
            except:
                pass
        
        return crypto_data
    
    def detect_signal(self, crypto_data: List[Dict], idx: int, 
                      threshold: float = 0.03) -> List[Dict]:
        """检测交易信号"""
        signals = []
        
        if idx >= len(crypto_data):
            return signals
        
        current_data = crypto_data[idx]
        coins = current_data.get('coins', [])
        
        for coin in coins:
            if not isinstance(coin, dict):
                continue
            
            price_change = coin.get('price_change_percentage_24h', 0)
            
            if abs(price_change) >= threshold * 100:
                signal = {
                    'index': idx,
                    'timestamp': current_data.get('timestamp', ''),
                    'symbol': coin.get('symbol', '').upper(),
                    'price': coin.get('current_price', 0),
                    'change_24h': price_change,
                    'signal_type': 'LONG' if price_change > 0 else 'SHORT'
                }
                signals.append(signal)
        
        return signals
    
    def calculate_position_size(self) -> float:
        """根据策略计算当前仓位大小"""
        if self.position_type == 'fixed':
            # 固定仓位
            return min(self.position_size, self.capital * 0.95)  # 保留 5% 现金
        
        elif self.position_type == 'percentage':
            # 固定比例
            position = self.capital * self.position_percentage
            return min(position, self.capital * 0.95)
        
        elif self.position_type == 'kelly':
            # 凯利公式
            if self.total_trades < 10:
                # 数据不足，使用固定比例
                return self.capital * 0.01
            
            win_rate = self.winners / self.total_trades if self.total_trades > 0 else 0.5
            avg_win = statistics.mean([t['pnl_pct'] for t in self.trades if t['pnl_pct'] > 0]) if self.winners > 0 else 0
            avg_loss = abs(statistics.mean([t['pnl_pct'] for t in self.trades if t['pnl_pct'] < 0])) if self.losers > 0 else 0
            
            if avg_loss == 0:
                return self.capital * 0.01
            
            # 凯利公式：f = (p * b - q) / b
            # p = 胜率, q = 败率, b = 盈亏比
            p = win_rate
            q = 1 - win_rate
            b = avg_win / avg_loss if avg_loss > 0 else 1
            
            kelly_fraction = (p * b - q) / b
            
            # 限制凯利比例（通常使用半凯利或四分之一凯利）
            kelly_fraction = max(0.01, min(0.1, kelly_fraction / 2))  # 半凯利，1-10%
            
            return self.capital * kelly_fraction
        
        return self.position_size
    
    def simulate_trade(self, signal: Dict, crypto_data: List[Dict], 
                       start_idx: int, position_size: float) -> Optional[Dict]:
        """模拟单笔交易"""
        entry_price = signal.get('price', 0)
        signal_type = signal.get('signal_type', 'LONG')
        
        if entry_price <= 0 or position_size <= 0:
            return None
        
        # 计算可购买数量
        quantity = position_size / entry_price
        
        # 止损止盈参数
        stop_loss_pct = 0.05  # 5% 止损
        take_profit_pct = 0.10  # 10% 止盈
        
        exit_price = 0
        pnl_pct = 0
        pnl_amount = 0
        exit_reason = ''
        hold_periods = 0
        current_price = entry_price  # 初始化
        
        # 遍历后续数据
        for i in range(start_idx + 1, min(start_idx + 48, len(crypto_data))):
            hold_periods += 1
            
            next_data = crypto_data[i]
            next_coins = next_data.get('coins', [])
            
            found = False
            for next_coin in next_coins:
                if next_coin.get('symbol', '').upper() != signal.get('symbol', '').upper():
                    continue
                
                current_price = next_coin.get('current_price', entry_price)
                found = True
                
                # 计算盈亏
                if signal_type == 'LONG':
                    pnl_pct = (current_price - entry_price) / entry_price
                else:
                    pnl_pct = (entry_price - current_price) / entry_price
                
                pnl_amount = pnl_pct * position_size
                
                # 检查止损
                if pnl_pct <= -stop_loss_pct:
                    exit_price = current_price
                    exit_reason = 'STOP_LOSS'
                    break
                
                # 检查止盈
                if pnl_pct >= take_profit_pct:
                    exit_price = current_price
                    exit_reason = 'TAKE_PROFIT'
                    break
            
            if exit_price > 0:
                break
            
            if not found:
                # 找不到该币种，跳过
                continue
        
        # 如果没有触发止损/止盈
        if exit_price == 0:
            exit_price = current_price
            exit_reason = 'END_OF_DATA'
        
        trade = {
            'trade_id': len(self.trades) + 1,
            'signal': signal,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'position_size': position_size,
            'quantity': quantity,
            'pnl_pct': pnl_pct * 100,
            'pnl_amount': pnl_amount,
            'exit_reason': exit_reason,
            'hold_periods': hold_periods
        }
        
        return trade
    
    def update_statistics(self, trade: Dict):
        """更新统计信息"""
        pnl = trade['pnl_amount']
        self.capital += pnl
        
        # 更新峰值
        if self.capital > self.peak_capital:
            self.peak_capital = self.capital
        
        # 计算回撤
        drawdown = self.peak_capital - self.capital
        drawdown_pct = drawdown / self.peak_capital * 100 if self.peak_capital > 0 else 0
        self.drawdowns.append({
            'trade_id': trade['trade_id'],
            'drawdown': drawdown,
            'drawdown_pct': drawdown_pct
        })
        
        # 更新最大回撤
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
            self.max_drawdown_pct = drawdown_pct
        
        # 记录资金曲线
        self.equity_curve.append({
            'trade_id': trade['trade_id'],
            'capital': self.capital,
            'pnl': pnl
        })
        
        # 更新交易统计
        self.trades.append(trade)
        self.total_trades += 1
        
        if pnl > 0:
            self.winners += 1
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            if self.consecutive_wins > self.max_consecutive_wins:
                self.max_consecutive_wins = self.consecutive_wins
        else:
            self.losers += 1
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            if self.consecutive_losses > self.max_consecutive_losses:
                self.max_consecutive_losses = self.consecutive_losses
    
    def run_backtest(self, crypto_data: List[Dict], 
                     threshold: float = 0.03) -> Dict:
        """运行完整回测"""
        print(f"\n💰 开始资金管理回测")
        print(f"初始本金：${self.initial_capital:,.2f}")
        print(f"仓位策略：{self.position_type}")
        print(f"阈值：{threshold*100}%")
        print("=" * 60)
        
        # 重置状态
        self.capital = self.initial_capital
        self.peak_capital = self.initial_capital
        self.trades = []
        self.equity_curve = []
        self.drawdowns = []
        self.total_trades = 0
        self.winners = 0
        self.losers = 0
        
        # 遍历所有数据点
        for i in range(len(crypto_data)):
            signals = self.detect_signal(crypto_data, i, threshold)
            
            for signal in signals:
                # 检查是否破产
                if self.capital < 1:
                    print(f"\n💥 破产！在第 {len(self.trades)} 笔交易后资金归零")
                    break
                
                # 计算仓位大小
                position_size = self.calculate_position_size()
                
                # 模拟交易
                trade = self.simulate_trade(signal, crypto_data, i, position_size)
                
                if trade:
                    self.update_statistics(trade)
        
        # 计算最终统计指标
        return self.calculate_metrics()
    
    def calculate_metrics(self) -> Dict:
        """计算回测指标"""
        win_rate = self.winners / self.total_trades * 100 if self.total_trades > 0 else 0
        
        # 平均盈亏
        avg_win = statistics.mean([t['pnl_amount'] for t in self.trades if t['pnl_amount'] > 0]) if self.winners > 0 else 0
        avg_loss = statistics.mean([t['pnl_amount'] for t in self.trades if t['pnl_amount'] < 0]) if self.losers > 0 else 0
        
        # 盈亏比
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # 总收益
        total_return = (self.capital - self.initial_capital) / self.initial_capital * 100
        
        # 夏普比率（简化版）
        if len(self.equity_curve) > 1:
            returns = [self.equity_curve[i]['pnl'] / self.initial_capital 
                      for i in range(1, len(self.equity_curve))]
            avg_return = statistics.mean(returns) if returns else 0
            std_return = statistics.stdev(returns) if len(returns) > 1 else 1
            sharpe_ratio = (avg_return / std_return) * math.sqrt(252) if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # 最大连续亏损/盈利
        max_cons_loss = self.max_consecutive_losses
        max_cons_win = self.max_consecutive_wins
        
        # 破产风险
        ruin_probability = self.calculate_ruin_probability()
        
        metrics = {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_return_pct': total_return,
            'total_trades': self.total_trades,
            'winners': self.winners,
            'losers': self.losers,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'max_drawdown_pct': self.max_drawdown_pct,
            'max_consecutive_wins': max_cons_win,
            'max_consecutive_losses': max_cons_loss,
            'ruin_probability': ruin_probability,
            'position_type': self.position_type,
            'position_size': self.position_size
        }
        
        return metrics
    
    def calculate_ruin_probability(self) -> float:
        """
        计算破产概率（简化模型）
        使用赌徒破产理论
        """
        if self.total_trades < 10:
            return 0
        
        win_rate = self.winners / self.total_trades
        avg_win_pct = statistics.mean([t['pnl_pct'] for t in self.trades if t['pnl_pct'] > 0]) if self.winners > 0 else 0
        avg_loss_pct = abs(statistics.mean([t['pnl_pct'] for t in self.trades if t['pnl_pct'] < 0])) if self.losers > 0 else 0
        
        if avg_loss_pct == 0:
            return 0
        
        # 期望值
        expected_value = win_rate * avg_win_pct - (1 - win_rate) * avg_loss_pct
        
        # 如果期望值为正，破产概率很低
        if expected_value > 0:
            return max(0, 1 - (self.capital / self.initial_capital) * (expected_value / avg_loss_pct))
        else:
            # 期望值为负，长期必然破产
            return min(1, abs(expected_value) / avg_loss_pct)
    
    def generate_report(self, metrics: Dict) -> str:
        """生成回测报告"""
        report = f"""
# 💰 资金管理回测报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 策略配置

| 参数 | 值 |
|------|-----|
| 初始本金 | ${metrics['initial_capital']:,.2f} |
| 仓位策略 | {metrics['position_type']} |
| 基础仓位 | ${metrics['position_size']} |

## 📈 核心表现

| 指标 | 数值 | 评估 |
|------|------|------|
| 最终资金 | **${metrics['final_capital']:,.2f}** | - |
| 总收益 | **{metrics['total_return_pct']:+.2f}%** | - |
| 总交易数 | {metrics['total_trades']} | - |
| 盈利交易 | {metrics['winners']} | - |
| 亏损交易 | {metrics['losers']} | - |
| **胜率** | **{metrics['win_rate']:.2f}%** | {'✅ 优秀' if metrics['win_rate'] >= 60 else '⚠️ 一般' if metrics['win_rate'] >= 45 else '❌ 需改进'} |
| 平均盈利 | ${metrics['avg_win']:.2f} | - |
| 平均亏损 | ${metrics['avg_loss']:.2f} | - |
| 盈亏比 | {metrics['profit_factor']:.2f} | {'✅ >1.5' if metrics['profit_factor'] >= 1.5 else '⚠️ >1' if metrics['profit_factor'] >= 1 else '❌ <1'} |

## 🎯 风险指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 最大回撤 | ${metrics['max_drawdown']:.2f} ({metrics['max_drawdown_pct']:.2f}%) | 最大资金下降 |
| 夏普比率 | {metrics['sharpe_ratio']:.2f} | {'✅ >1' if metrics['sharpe_ratio'] >= 1 else '⚠️ >0' if metrics['sharpe_ratio'] >= 0 else '❌ <0'} |
| 破产概率 | {metrics['ruin_probability']*100:.2f}% | {'✅ 低' if metrics['ruin_probability'] < 0.1 else '⚠️ 中' if metrics['ruin_probability'] < 0.5 else '❌ 高'} |
| 最大连胜 | {metrics['max_consecutive_wins']} 场 | - |
| 最大连败 | {metrics['max_consecutive_losses']} 场 | - |

## 📊 资金曲线分析

"""
        # 分析资金曲线
        if self.equity_curve:
            start_cap = self.equity_curve[0]['capital']
            end_cap = self.equity_curve[-1]['capital']
            peak = max([e['capital'] for e in self.equity_curve])
            trough = min([e['capital'] for e in self.equity_curve])
            
            report += f"- 起始资金：${start_cap:,.2f}\n"
            report += f"- 最高资金：${peak:,.2f}\n"
            report += f"- 最低资金：${trough:,.2f}\n"
            report += f"- 最终资金：${end_cap:,.2f}\n"
            
            # 计算波动性
            if len(self.equity_curve) > 10:
                mid_point = len(self.equity_curve) // 2
                first_half_avg = statistics.mean([e['capital'] for e in self.equity_curve[:mid_point]])
                second_half_avg = statistics.mean([e['capital'] for e in self.equity_curve[mid_point:]])
                trend = "📈 上升" if second_half_avg > first_half_avg else "📉 下降"
                report += f"- 趋势：{trend}\n"
        
        # 策略评估
        total_return = metrics['total_return_pct']
        win_rate = metrics['win_rate']
        
        report += f"""
## 🎯 策略评估

"""
        if total_return > 50 and win_rate >= 55:
            report += "✅ **优秀** - 盈利可观，胜率稳定，可以考虑实盘！\n"
        elif total_return > 20 and win_rate >= 50:
            report += "⚠️ **良好** - 有盈利，但需要继续优化\n"
        elif total_return > 0:
            report += "⚠️ **微利** - 勉强盈利，需要大幅提升胜率\n"
        else:
            report += "❌ **亏损** - 策略不可行，需要重新设计\n"
        
        report += f"""
## 📝 详细交易记录（前 30 笔）

| # | 币种 | 方向 | 仓位 | 入场 | 出场 | 盈亏$ | 盈亏% | 原因 |
|---|------|------|------|------|------|-------|-------|------|
"""
        for trade in self.trades[:30]:
            signal = trade.get('signal', {})
            report += f"| {trade['trade_id']} | "
            report += f"{signal.get('symbol', 'N/A')} | "
            report += f"{signal.get('signal_type', 'N/A')} | "
            report += f"${trade['position_size']:.2f} | "
            report += f"${trade['entry_price']:,.2f} | "
            report += f"${trade['exit_price']:,.2f} | "
            report += f"{trade['pnl_amount']:+.2f} | "
            report += f"{trade['pnl_pct']:+.2f}% | "
            report += f"{trade['exit_reason']} |\n"
        
        if len(self.trades) > 30:
            report += f"\n_... 还有 {len(self.trades) - 30} 笔交易_\n"
        
        return report
    
    def compare_strategies(self, crypto_data: List[Dict], 
                           threshold: float = 0.03) -> Dict:
        """比较不同资金管理策略"""
        print("\n🔄 比较不同资金管理策略...")
        print("=" * 60)
        
        strategies = [
            ('fixed', 5.0, '固定 5 元'),
            ('fixed', 10.0, '固定 10 元'),
            ('fixed', 20.0, '固定 20 元'),
            ('percentage', 0.01, '1% 仓位'),
            ('percentage', 0.02, '2% 仓位'),
            ('kelly', 0, '凯利公式'),
        ]
        
        results = []
        
        for pos_type, pos_size, name in strategies:
            print(f"\n测试策略：{name}")
            
            # 创建新实例
            backtest = MoneyManagementBacktest(
                initial_capital=self.initial_capital,
                position_size=pos_size,
                position_type=pos_type
            )
            
            # 运行回测
            metrics = backtest.run_backtest(crypto_data, threshold)
            metrics['strategy_name'] = name
            
            results.append(metrics)
            
            print(f"  最终资金：${metrics['final_capital']:,.2f} ({metrics['total_return_pct']:+.2f}%)")
            print(f"  胜率：{metrics['win_rate']:.1f}% | 夏普：{metrics['sharpe_ratio']:.2f}")
        
        # 排序（按总收益）
        results.sort(key=lambda x: x['total_return_pct'], reverse=True)
        
        print("\n" + "=" * 60)
        print("🏆 策略排名（按总收益）:")
        for i, r in enumerate(results[:3], 1):
            print(f"  {i}. {r['strategy_name']}: ${r['final_capital']:,.2f} ({r['total_return_pct']:+.2f}%)")
        
        return {
            'strategies': results,
            'best_strategy': results[0] if results else None
        }


def main():
    """主函数"""
    print("=" * 60)
    print("💰 资金管理系统回测 v3.0")
    print("=" * 60)
    
    # 创建回测系统
    backtest = MoneyManagementBacktest(
        initial_capital=1000.0,  # 1000 元本金
        position_size=5.0,       # 5 元每次
        position_type='fixed'    # 固定仓位
    )
    
    # 加载数据
    print("\n📂 加载数据...")
    crypto_data = backtest.load_crypto_data()
    
    if not crypto_data:
        print("\n❌ 错误：没有可用的加密货币数据")
        return
    
    print(f"✅ 加载了 {len(crypto_data)} 条数据")
    
    # 比较不同策略
    comparison = backtest.compare_strategies(crypto_data, threshold=0.03)
    
    # 使用最佳策略运行详细回测
    if comparison['best_strategy']:
        best = comparison['best_strategy']
        print(f"\n🏆 最佳策略：{best['strategy_name']}")
        
        # 生成详细报告
        report = backtest.generate_report(best)
        
        # 保存报告
        report_file = MONEY_MGMT_DIR / f"money_mgmt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 详细报告已保存：{report_file}")
        print("\n" + "=" * 60)
        print(report)


if __name__ == "__main__":
    main()
