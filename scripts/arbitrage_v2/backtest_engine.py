#!/usr/bin/env python3
"""
跨交易所套利回测引擎 v1.0
独立系统 B - 跨交易所套利

功能：
1. 加载历史价格数据
2. 模拟套利交易
3. 计算收益率
4. 风险评估
5. 生成回测报告
"""

import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 配置
DATA_DIR = Path.home() / ".openclaw" / "workspace" / "data" / "arbitrage_v2"
BACKTEST_DIR = DATA_DIR / "backtest"

# 确保目录存在
BACKTEST_DIR.mkdir(parents=True, exist_ok=True)

# 回测配置
BACKTEST_CONFIG = {
    'initial_capital': 10000.0,  # 初始资金 10000 USDT
    'position_size': 100.0,      # 每次套利 100 USDT
    'max_position_pct': 0.5,     # 最大仓位 50%
    'trading_fee': 0.001,        # 交易费率 0.1%
    'slippage': 0.001,           # 滑点 0.1%
    'min_spread_pct': 0.3,       # 最小价差 0.3%
}


class ArbitrageBacktest:
    """套利回测引擎"""
    
    def __init__(self, config: Dict = None):
        self.config = config or BACKTEST_CONFIG
        self.capital = self.config['initial_capital']
        self.initial_capital = self.config['initial_capital']
        self.trades = []
        self.equity_curve = []
        
        # 统计
        self.total_trades = 0
        self.winners = 0
        self.losers = 0
        self.total_profit = 0
        self.max_drawdown = 0
        self.peak_capital = self.initial_capital
    
    def load_historical_data(self, days: int = 7) -> List[Dict]:
        """加载历史价格数据"""
        all_data = []
        
        print(f"📂 加载最近 {days} 天的价格数据...")
        
        # 扫描数据文件
        pattern = "prices_*.json"
        files = sorted(DATA_DIR.glob(pattern))
        
        # 只取最近的文件
        recent_files = files[-days*24:] if len(files) > days*24 else files
        
        for file in recent_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.append(data)
            except Exception as e:
                print(f"⚠️ 读取失败 {file.name}: {e}")
        
        print(f"✅ 加载了 {len(all_data)} 个数据点")
        return all_data
    
    def detect_opportunities(self, price_data: Dict) -> List[Dict]:
        """检测套利机会"""
        opportunities = []
        
        exchanges_data = price_data.get('exchanges', {})
        symbols = price_data.get('symbols', [])
        
        for symbol in symbols:
            # 收集价格
            symbol_prices = {}
            for exchange, prices in exchanges_data.items():
                if symbol in prices:
                    symbol_prices[exchange] = prices[symbol]['price']
            
            if len(symbol_prices) < 2:
                continue
            
            # 计算价差
            exchanges = list(symbol_prices.keys())
            for i in range(len(exchanges)):
                for j in range(i + 1, len(exchanges)):
                    exchange_a = exchanges[i]
                    exchange_b = exchanges[j]
                    
                    price_a = symbol_prices[exchange_a]
                    price_b = symbol_prices[exchange_b]
                    
                    if price_a > 0 and price_b > 0:
                        if price_a < price_b:
                            buy_exchange = exchange_a
                            sell_exchange = exchange_b
                            buy_price = price_a
                            sell_price = price_b
                        else:
                            buy_exchange = exchange_b
                            sell_exchange = exchange_a
                            buy_price = price_b
                            sell_price = price_a
                        
                        spread_pct = (sell_price - buy_price) / buy_price * 100
                        
                        # 过滤：只保留有利可图的机会
                        if spread_pct >= self.config['min_spread_pct']:
                            # 计算净利润（简化）
                            total_fees = spread_pct * 0.5  # 估算总成本
                            net_profit_pct = spread_pct - total_fees
                            
                            if net_profit_pct > 0:
                                opportunities.append({
                                    'symbol': symbol,
                                    'buy_exchange': buy_exchange,
                                    'sell_exchange': sell_exchange,
                                    'buy_price': buy_price,
                                    'sell_price': sell_price,
                                    'spread_pct': spread_pct,
                                    'net_profit_pct': net_profit_pct,
                                    'timestamp': price_data.get('timestamp', '')
                                })
        
        return opportunities
    
    def simulate_trade(self, opportunity: Dict) -> Optional[Dict]:
        """模拟套利交易"""
        position_size = min(
            self.config['position_size'],
            self.capital * self.config['max_position_pct']
        )
        
        if position_size < 10:  # 最小仓位
            return None
        
        # 计算利润
        profit = position_size * opportunity['net_profit_pct'] / 100
        
        # 更新资金
        self.capital += profit
        
        # 更新峰值和回撤
        if self.capital > self.peak_capital:
            self.peak_capital = self.capital
        
        drawdown = self.peak_capital - self.capital
        drawdown_pct = drawdown / self.peak_capital * 100 if self.peak_capital > 0 else 0
        
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
        
        # 记录交易
        trade = {
            'trade_id': len(self.trades) + 1,
            'symbol': opportunity['symbol'],
            'buy_exchange': opportunity['buy_exchange'],
            'sell_exchange': opportunity['sell_exchange'],
            'spread_pct': opportunity['spread_pct'],
            'net_profit_pct': opportunity['net_profit_pct'],
            'position_size': position_size,
            'profit': profit,
            'capital_after': self.capital,
            'drawdown_pct': drawdown_pct,
            'timestamp': opportunity['timestamp']
        }
        
        self.trades.append(trade)
        self.total_trades += 1
        
        if profit > 0:
            self.winners += 1
        else:
            self.losers += 1
        
        self.total_profit += profit
        
        # 记录资金曲线
        self.equity_curve.append({
            'trade_id': trade['trade_id'],
            'capital': self.capital,
            'profit': profit
        })
        
        return trade
    
    def run_backtest(self, historical_data: List[Dict]) -> Dict:
        """运行回测"""
        print(f"\n🚀 开始回测")
        print(f"初始资金：${self.initial_capital:,.2f}")
        print(f"数据点数：{len(historical_data)}")
        print("=" * 60)
        
        # 重置状态
        self.capital = self.initial_capital
        self.peak_capital = self.initial_capital
        self.trades = []
        self.equity_curve = []
        self.total_trades = 0
        self.winners = 0
        self.losers = 0
        self.total_profit = 0
        self.max_drawdown = 0
        
        total_opportunities = 0
        
        # 遍历所有数据点
        for data in historical_data:
            opportunities = self.detect_opportunities(data)
            total_opportunities += len(opportunities)
            
            # 模拟交易（取最好的机会）
            if opportunities:
                # 按净利润排序，取前 3 个
                opportunities.sort(key=lambda x: x['net_profit_pct'], reverse=True)
                
                for opp in opportunities[:3]:  # 每次最多交易 3 个
                    trade = self.simulate_trade(opp)
                    if not trade:
                        break
        
        # 计算统计指标
        return self.calculate_metrics(total_opportunities)
    
    def calculate_metrics(self, total_opportunities: int) -> Dict:
        """计算回测指标"""
        win_rate = self.winners / self.total_trades * 100 if self.total_trades > 0 else 0
        
        # 平均盈亏
        avg_profit = statistics.mean([t['profit'] for t in self.trades]) if self.trades else 0
        avg_profit_pct = statistics.mean([t['net_profit_pct'] for t in self.trades]) if self.trades else 0
        
        # 总收益率
        total_return_pct = (self.capital - self.initial_capital) / self.initial_capital * 100
        
        # 夏普比率（简化）
        if len(self.equity_curve) > 10:
            returns = [self.equity_curve[i]['profit'] / self.initial_capital 
                      for i in range(1, len(self.equity_curve))]
            if returns:
                avg_return = statistics.mean(returns)
                std_return = statistics.stdev(returns) if len(returns) > 1 else 1
                sharpe_ratio = (avg_return / std_return) * 252 ** 0.5 if std_return > 0 else 0
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        # 最大回撤百分比
        max_drawdown_pct = self.max_drawdown / self.peak_capital * 100 if self.peak_capital > 0 else 0
        
        metrics = {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_return_pct': total_return_pct,
            'total_trades': self.total_trades,
            'total_opportunities': total_opportunities,
            'winners': self.winners,
            'losers': self.losers,
            'win_rate': win_rate,
            'total_profit': self.total_profit,
            'avg_profit': avg_profit,
            'avg_profit_pct': avg_profit_pct,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'max_drawdown_pct': max_drawdown_pct,
            'config': self.config.copy()
        }
        
        return metrics
    
    def generate_report(self, metrics: Dict) -> str:
        """生成回测报告"""
        report = f"""
# 📊 跨交易所套利回测报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 回测配置

| 参数 | 值 |
|------|-----|
| 初始资金 | ${metrics['initial_capital']:,.2f} |
| 每次仓位 | ${metrics['config']['position_size']} |
| 最大仓位 | {metrics['config']['max_position_pct']*100}% |
| 交易费率 | {metrics['config']['trading_fee']*100}% |
| 最小价差 | {metrics['config']['min_spread_pct']}% |

## 📈 核心表现

| 指标 | 数值 | 评估 |
|------|------|------|
| 最终资金 | **${metrics['final_capital']:,.2f}** | - |
| 总收益 | **{metrics['total_return_pct']:+.2f}%** | - |
| 总交易数 | {metrics['total_trades']} | - |
| 总机会数 | {metrics['total_opportunities']} | - |
| 盈利交易 | {metrics['winners']} | - |
| 亏损交易 | {metrics['losers']} | - |
| **胜率** | **{metrics['win_rate']:.2f}%** | {'✅ >60%' if metrics['win_rate'] >= 60 else '⚠️ >50%' if metrics['win_rate'] >= 50 else '❌ <50%'} |
| 平均利润 | ${metrics['avg_profit']:.2f} ({metrics['avg_profit_pct']:.3f}%) | - |
| 总利润 | ${metrics['total_profit']:.2f} | - |

## 🎯 风险指标

| 指标 | 数值 | 评估 |
|------|------|------|
| 最大回撤 | ${metrics['max_drawdown']:.2f} ({metrics['max_drawdown_pct']:.2f}%) | {'✅ <10%' if metrics['max_drawdown_pct'] < 10 else '⚠️ <20%' if metrics['max_drawdown_pct'] < 20 else '❌ >20%'} |
| 夏普比率 | {metrics['sharpe_ratio']:.2f} | {'✅ >1' if metrics['sharpe_ratio'] >= 1 else '⚠️ >0' if metrics['sharpe_ratio'] >= 0 else '❌ <0'} |

## 📊 资金曲线分析

"""
        if self.equity_curve:
            start_cap = self.equity_curve[0]['capital']
            end_cap = self.equity_curve[-1]['capital']
            peak = max([e['capital'] for e in self.equity_curve])
            
            report += f"- 起始资金：${start_cap:,.2f}\n"
            report += f"- 最高资金：${peak:,.2f}\n"
            report += f"- 最终资金：${end_cap:,.2f}\n"
            
            # 计算胜率趋势
            if len(self.trades) > 10:
                first_half_wins = sum(1 for t in self.trades[:len(self.trades)//2] if t['profit'] > 0)
                second_half_wins = sum(1 for t in self.trades[len(self.trades)//2:] if t['profit'] > 0)
                first_half_rate = first_half_wins / (len(self.trades)//2) * 100
                second_half_rate = second_half_wins / (len(self.trades) - len(self.trades)//2) * 100
                
                report += f"- 前半段胜率：{first_half_rate:.1f}%\n"
                report += f"- 后半段胜率：{second_half_rate:.1f}%\n"
        
        # 策略评估
        total_return = metrics['total_return_pct']
        win_rate = metrics['win_rate']
        
        report += f"""
## 🎯 策略评估

"""
        if total_return > 20 and win_rate >= 60:
            report += "✅ **优秀** - 盈利可观，胜率高，可以考虑实盘！\n"
        elif total_return > 10 and win_rate >= 55:
            report += "⚠️ **良好** - 有盈利，可以继续优化\n"
        elif total_return > 0:
            report += "⚠️ **微利** - 勉强盈利，需要优化参数\n"
        else:
            report += "❌ **亏损** - 策略需要调整\n"
        
        report += f"""
## 📝 详细交易记录（前 20 笔）

| # | 币种 | 买入 | 卖出 | 价差% | 利润% | 利润$ | 资金 |
|---|------|------|------|-------|-------|-------|------|
"""
        for trade in self.trades[:20]:
            report += f"| {trade['trade_id']} | "
            report += f"{trade['symbol']} | "
            report += f"{trade['buy_exchange']} | "
            report += f"{trade['sell_exchange']} | "
            report += f"{trade['spread_pct']:.3f}% | "
            report += f"{trade['net_profit_pct']:.3f}% | "
            report += f"${trade['profit']:+.2f} | "
            report += f"${trade['capital_after']:,.2f} |\n"
        
        if len(self.trades) > 20:
            report += f"\n_... 还有 {len(self.trades) - 20} 笔交易_\n"
        
        return report
    
    def save_report(self, report: str, metrics: Dict):
        """保存报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存 Markdown 报告
        report_file = BACKTEST_DIR / f"backtest_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 保存 JSON 数据
        json_file = BACKTEST_DIR / f"backtest_data_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metrics': metrics,
                'trades': self.trades,
                'equity_curve': self.equity_curve
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 报告已保存：{report_file.name}")


def main():
    """主函数"""
    print("=" * 60)
    print("📊 跨交易所套利回测引擎 v1.0")
    print("=" * 60)
    
    # 创建回测引擎
    backtest = ArbitrageBacktest(BACKTEST_CONFIG)
    
    # 加载历史数据
    historical_data = backtest.load_historical_data(days=7)
    
    if not historical_data:
        print("\n❌ 错误：没有历史数据")
        print("💡 提示：先运行 data_collector.py 收集数据")
        return
    
    # 运行回测
    metrics = backtest.run_backtest(historical_data)
    
    # 生成报告
    report = backtest.generate_report(metrics)
    
    # 保存报告
    backtest.save_report(report, metrics)
    
    # 打印报告
    print("\n" + "=" * 60)
    print(report)


if __name__ == "__main__":
    main()
