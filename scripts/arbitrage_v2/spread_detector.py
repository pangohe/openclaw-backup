#!/usr/bin/env python3
"""
跨交易所价差检测器 v1.0
独立系统 B - 跨交易所套利

功能：
1. 读取价格数据
2. 计算跨交易所价差
3. 检测套利机会
4. 考虑交易成本
5. 生成套利信号
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 配置
DATA_DIR = Path.home() / ".openclaw" / "workspace" / "data" / "arbitrage_v2"
SIGNALS_DIR = DATA_DIR / "signals"

# 确保目录存在
SIGNALS_DIR.mkdir(parents=True, exist_ok=True)

# 套利配置
ARBITRAGE_CONFIG = {
    'min_spread_pct': 0.3,      # 最小价差阈值 0.3%
    'max_spread_pct': 5.0,      # 最大价差阈值 5%
    'min_volume_usdt': 100,     # 最小交易量 100 USDT
    'position_size_usdt': 100,  # 每次套利金额 100 USDT
    
    # 交易成本
    'trading_fee_rate': 0.001,  # 交易费率 0.1%
    'withdrawal_fee_pct': 0.0005,  # 提现费率 0.05%
    'slippage_pct': 0.001,      # 滑点 0.1%
    
    # 风险控制
    'max_daily_trades': 20,     # 每日最大交易次数
    'max_position_usdt': 1000,  # 最大持仓
}


class SpreadDetector:
    """价差检测器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or ARBITRAGE_CONFIG
        self.opportunities = []
        self.signals = []
    
    def load_latest_prices(self) -> Optional[Dict]:
        """加载最新价格数据"""
        latest_file = DATA_DIR / "latest_prices.json"
        
        if not latest_file.exists():
            print(f"⚠️ 价格文件不存在：{latest_file}")
            return None
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ 加载价格数据：{data.get('timestamp', 'N/A')}")
            return data
        except Exception as e:
            print(f"❌ 加载失败：{e}")
            return None
    
    def calculate_spread(self, prices: Dict[str, float]) -> List[Dict]:
        """
        计算交易所之间的价差
        
        返回：
            价差列表，包含买入交易所、卖出交易所、价差等
        """
        spreads = []
        
        if len(prices) < 2:
            return spreads
        
        # 两两比较
        exchanges = list(prices.keys())
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                exchange_a = exchanges[i]
                exchange_b = exchanges[j]
                
                price_a = prices[exchange_a]
                price_b = prices[exchange_b]
                
                if price_a > 0 and price_b > 0:
                    # 计算价差
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
                    
                    spread = sell_price - buy_price
                    spread_pct = spread / buy_price * 100
                    
                    spreads.append({
                        'symbol': None,  # 会在外部设置
                        'buy_exchange': buy_exchange,
                        'sell_exchange': sell_exchange,
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'spread': spread,
                        'spread_pct': spread_pct,
                        'timestamp': datetime.now().isoformat()
                    })
        
        return spreads
    
    def calculate_profit(self, spread_data: Dict, position_size: float) -> Dict:
        """
        计算套利利润（考虑所有成本）
        
        成本包括：
        - 买入交易费
        - 卖出交易费
        - 提现费
        - 滑点
        """
        buy_price = spread_data['buy_price']
        sell_price = spread_data['sell_price']
        spread_pct = spread_data['spread_pct']
        
        # 计算数量
        quantity = position_size / buy_price
        
        # 买入成本
        buy_fee = position_size * self.config['trading_fee_rate']
        buy_slippage = position_size * self.config['slippage_pct']
        total_buy_cost = position_size + buy_fee + buy_slippage
        
        # 卖出收入
        sell_revenue = quantity * sell_price
        sell_fee = sell_revenue * self.config['trading_fee_rate']
        sell_slippage = sell_revenue * self.config['slippage_pct']
        
        # 提现成本（如果需要跨交易所转账）
        withdrawal_fee = position_size * self.config['withdrawal_fee_pct']
        
        # 净利润
        net_revenue = sell_revenue - sell_fee - sell_slippage - withdrawal_fee
        net_profit = net_revenue - total_buy_cost
        net_profit_pct = net_profit / total_buy_cost * 100
        
        return {
            'gross_spread_pct': spread_pct,
            'net_profit': net_profit,
            'net_profit_pct': net_profit_pct,
            'total_costs': (buy_fee + buy_slippage + sell_fee + sell_slippage + withdrawal_fee),
            'cost_breakdown': {
                'buy_fee': buy_fee,
                'sell_fee': sell_fee,
                'buy_slippage': buy_slippage,
                'sell_slippage': sell_slippage,
                'withdrawal_fee': withdrawal_fee
            },
            'quantity': quantity,
            'buy_cost': total_buy_cost,
            'sell_revenue': net_revenue
        }
    
    def detect_opportunities(self, price_data: Dict) -> List[Dict]:
        """检测套利机会"""
        opportunities = []
        
        exchanges_data = price_data.get('exchanges', {})
        symbols = price_data.get('symbols', [])
        
        print(f"\n🔍 检测套利机会...")
        print(f"  交易所：{len(exchanges_data)} 个")
        print(f"  币种：{len(symbols)} 个")
        
        # 对每个币种计算价差
        for symbol in symbols:
            # 收集该币种在所有交易所的价格
            symbol_prices = {}
            for exchange, prices in exchanges_data.items():
                if symbol in prices:
                    symbol_prices[exchange] = prices[symbol]['price']
            
            # 需要至少 2 个交易所的价格
            if len(symbol_prices) < 2:
                continue
            
            # 计算价差
            spreads = self.calculate_spread(symbol_prices)
            
            for spread in spreads:
                spread['symbol'] = symbol
                
                # 计算利润
                profit_data = self.calculate_profit(
                    spread, 
                    self.config['position_size_usdt']
                )
                
                # 合并数据
                opportunity = {
                    **spread,
                    **profit_data,
                    'position_size': self.config['position_size_usdt'],
                    'is_profitable': profit_data['net_profit'] > 0,
                    'confidence': 'HIGH' if profit_data['net_profit_pct'] > 0.5 else 
                                  'MEDIUM' if profit_data['net_profit_pct'] > 0.2 else 'LOW'
                }
                
                # 过滤：只保留有利可图的机会
                if opportunity['is_profitable'] and \
                   profit_data['net_profit_pct'] >= self.config['min_spread_pct']:
                    opportunities.append(opportunity)
        
        # 按净利润排序
        opportunities.sort(key=lambda x: x['net_profit'], reverse=True)
        
        self.opportunities = opportunities
        return opportunities
    
    def generate_signals(self, opportunities: List[Dict]) -> List[Dict]:
        """生成交易信号"""
        signals = []
        
        for opp in opportunities:
            signal = {
                'signal_id': f"arb_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{opp['symbol']}",
                'type': 'ARBITRAGE',
                'symbol': opp['symbol'],
                'action': 'BUY_SELL',
                'buy_exchange': opp['buy_exchange'],
                'sell_exchange': opp['sell_exchange'],
                'buy_price': opp['buy_price'],
                'sell_price': opp['sell_price'],
                'position_size': opp['position_size'],
                'expected_profit': opp['net_profit'],
                'expected_profit_pct': opp['net_profit_pct'],
                'confidence': opp['confidence'],
                'timestamp': datetime.now().isoformat(),
                'status': 'PENDING',
                'expires_at': None  # 信号有效期
            }
            signals.append(signal)
        
        self.signals = signals
        return signals
    
    def save_signals(self, signals: List[Dict]):
        """保存信号到文件"""
        if not signals:
            print("  ℹ️  无新信号")
            return
        
        # 保存到信号文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        signal_file = SIGNALS_DIR / f"signals_{timestamp}.json"
        
        with open(signal_file, 'w', encoding='utf-8') as f:
            json.dump(signals, f, indent=2, ensure_ascii=False)
        
        # 更新最新信号
        latest_file = SIGNALS_DIR / "latest_signals.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_signals': len(signals),
                'signals': signals
            }, f, indent=2, ensure_ascii=False)
        
        print(f"  💾 保存 {len(signals)} 个信号到：{signal_file.name}")
    
    def print_opportunities(self, opportunities: List[Dict]):
        """打印套利机会"""
        if not opportunities:
            print("\n❌ 暂无套利机会")
            return
        
        print(f"\n🎯 发现 {len(opportunities)} 个套利机会")
        print("=" * 80)
        
        for i, opp in enumerate(opportunities[:10], 1):  # 只显示前 10 个
            print(f"\n{i}. {opp['symbol']}")
            print(f"   买入：{opp['buy_exchange']} @ ${opp['buy_price']:,.2f}")
            print(f"   卖出：{opp['sell_exchange']} @ ${opp['sell_price']:,.2f}")
            print(f"   价差：${opp['spread']:.2f} ({opp['gross_spread_pct']:.3f}%)")
            print(f"   净利润：${opp['net_profit']:.2f} ({opp['net_profit_pct']:.3f}%)")
            print(f"   仓位：${opp['position_size']:.2f}")
            print(f"   信心：{opp['confidence']}")
            print(f"   总成本：${opp['total_costs']:.4f}")
        
        if len(opportunities) > 10:
            print(f"\n... 还有 {len(opportunities) - 10} 个机会")
        
        print("=" * 80)


def main():
    """主函数"""
    print("=" * 60)
    print("🔍 跨交易所价差检测器 v1.0")
    print("=" * 60)
    
    # 创建检测器
    detector = SpreadDetector(ARBITRAGE_CONFIG)
    
    # 加载价格数据
    price_data = detector.load_latest_prices()
    
    if not price_data:
        print("\n❌ 错误：没有价格数据")
        print("💡 提示：先运行 data_collector.py 收集价格")
        return
    
    # 检测套利机会
    opportunities = detector.detect_opportunities(price_data)
    
    # 打印机会
    detector.print_opportunities(opportunities)
    
    # 生成信号
    if opportunities:
        signals = detector.generate_signals(opportunities)
        detector.save_signals(signals)
    
    print("\n✅ 检测完成！")


if __name__ == "__main__":
    main()
