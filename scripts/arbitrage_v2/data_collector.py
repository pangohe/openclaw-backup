#!/usr/bin/env python3
"""
跨交易所数据收集器 v1.0
独立系统 B - 跨交易所套利

功能：
1. 从多个交易所获取实时价格
2. 计算价差
3. 保存到独立数据目录
4. 支持 Binance/OKX/Bybit

API 文档：
- Binance: https://binance-docs.github.io/apidocs/
- OKX: https://www.okx.com/docs-v5/en/
- Bybit: https://bybit-exchange.github.io/docs/
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 配置 - 独立系统 B
CONFIG_DIR = Path.home() / ".openclaw" / "workspace" / "config"
DATA_DIR = Path.home() / ".openclaw" / "workspace" / "data" / "arbitrage_v2"

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 交易所 API 配置（全部免费）
EXCHANGES = {
    'binance': {
        'name': 'Binance',
        'api_base': 'https://api.binance.com/api/v3',
        'ticker_endpoint': '/ticker/price',
        'book_endpoint': '/depth',
        'fee_rate': 0.001,  # 0.1%
        'note': '流动性最好，API 最稳定 ✅'
    },
    'okx': {
        'name': 'OKX',
        'api_base': 'https://www.okx.com/api/v5/market',
        'ticker_endpoint': '/ticker',
        'book_endpoint': '/books',
        'fee_rate': 0.0008,  # 0.08%
        'note': '费率最低，API 友好 ✅'
    },
    'kucoin': {
        'name': 'KuCoin',
        'api_base': 'https://api.kucoin.com/api/v1/market',
        'ticker_endpoint': '/allTickers',
        'book_endpoint': '/orderbook/level2',
        'fee_rate': 0.001,  # 0.1%
        'note': '币种多，套利机会多 ⏳'
    }
}

# 监控的币种
MONITORED_SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT',
    'ADAUSDT', 'DOGEUSDT', 'DOTUSDT', 'MATICUSDT', 'AVAXUSDT'
]


class ExchangeDataCollector:
    """交易所数据收集器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.last_update = {}
    
    def fetch_binance_prices(self) -> Optional[Dict]:
        """从 Binance 获取价格"""
        try:
            url = f"{EXCHANGES['binance']['api_base']}{EXCHANGES['binance']['ticker_endpoint']}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                prices = {}
                for item in data:
                    symbol = item.get('symbol', '')
                    if symbol in MONITORED_SYMBOLS:
                        prices[symbol] = {
                            'price': float(item.get('price', 0)),
                            'exchange': 'binance',
                            'timestamp': datetime.now().isoformat()
                        }
                return prices
            else:
                print(f"❌ Binance API 错误：{response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Binance 请求失败：{e}")
            return None
    
    def fetch_okx_prices(self) -> Optional[Dict]:
        """从 OKX 获取价格"""
        try:
            prices = {}
            for symbol in MONITORED_SYMBOLS:
                # OKX 需要转换币种对格式（BTC-USDT）
                inst_id = symbol.replace('USDT', '-USDT')
                url = f"{EXCHANGES['okx']['api_base']}{EXCHANGES['okx']['ticker_endpoint']}?instId={inst_id}"
                
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == '0' and data.get('data'):
                        ticker = data['data'][0]
                        prices[symbol] = {
                            'price': float(ticker.get('last', 0)),
                            'exchange': 'okx',
                            'timestamp': datetime.now().isoformat()
                        }
                
                time.sleep(0.1)  # 避免频率限制
            
            return prices if prices else None
            
        except Exception as e:
            print(f"❌ OKX 请求失败：{e}")
            return None
    
    def fetch_kucoin_prices(self) -> Optional[Dict]:
        """从 KuCoin 获取价格（免费 API）"""
        try:
            url = f"{EXCHANGES['kucoin']['api_base']}{EXCHANGES['kucoin']['ticker_endpoint']}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '200000' and data.get('data'):
                    prices = {}
                    # KuCoin 返回的是 ticker 列表
                    tickers = data['data'] if isinstance(data['data'], list) else data['data'].get('tickers', [])
                    for item in tickers:
                        symbol = item.get('symbol', '')
                        # KuCoin 格式：BTC-USDT → BTCUSDT
                        symbol_normalized = symbol.replace('-', '')
                        if symbol_normalized in MONITORED_SYMBOLS:
                            prices[symbol_normalized] = {
                                'price': float(item.get('last', 0)),
                                'exchange': 'kucoin',
                                'timestamp': datetime.now().isoformat()
                            }
                    return prices
            else:
                print(f"❌ KuCoin API 错误：{response.status_code}")
            return None
                
        except Exception as e:
            print(f"❌ KuCoin 请求失败：{e}")
            return None
    
    def fetch_all_exchanges(self) -> Dict:
        """从所有交易所获取价格"""
        all_prices = {}
        
        print(f"\n📊 [{datetime.now().strftime('%H:%M:%S')}] 开始获取价格...")
        
        # Binance
        binance_prices = self.fetch_binance_prices()
        if binance_prices:
            all_prices['binance'] = binance_prices
            print(f"  ✅ Binance: {len(binance_prices)} 个币种")
        else:
            print(f"  ❌ Binance: 获取失败")
        
        # OKX
        okx_prices = self.fetch_okx_prices()
        if okx_prices:
            all_prices['okx'] = okx_prices
            print(f"  ✅ OKX: {len(okx_prices)} 个币种")
        else:
            print(f"  ❌ OKX: 获取失败")
        
        # KuCoin
        kucoin_prices = self.fetch_kucoin_prices()
        if kucoin_prices:
            all_prices['kucoin'] = kucoin_prices
            print(f"  ✅ KuCoin: {len(kucoin_prices)} 个币种")
        else:
            print(f"  ⏳ KuCoin: 获取失败（可忽略，非核心交易所）")
        
        self.last_update = {
            'timestamp': datetime.now().isoformat(),
            'exchanges': list(all_prices.keys())
        }
        
        return all_prices
    
    def save_data(self, all_prices: Dict):
        """保存数据到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存到带时间戳的文件
        file_path = DATA_DIR / f"prices_{timestamp}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'exchanges': all_prices,
            'symbols': MONITORED_SYMBOLS
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 同时更新最新数据文件
        latest_path = DATA_DIR / "latest_prices.json"
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  💾 数据已保存：{file_path.name}")
    
    def run_collection(self, interval_minutes: int = 1):
        """运行数据收集（循环）"""
        print("=" * 60)
        print("🚀 跨交易所数据收集器 v1.0")
        print("=" * 60)
        print(f"监控币种：{len(MONITORED_SYMBOLS)} 个")
        print(f"交易所：{', '.join(EXCHANGES.keys())}")
        print(f"收集间隔：{interval_minutes} 分钟")
        print("=" * 60)
        
        try:
            while True:
                all_prices = self.fetch_all_exchanges()
                
                if all_prices:
                    self.save_data(all_prices)
                
                next_run = datetime.now().timestamp() + (interval_minutes * 60)
                print(f"\n⏳ 下次收集：{datetime.fromtimestamp(next_run).strftime('%H:%M:%S')}")
                
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  数据收集已停止")


def main():
    """主函数"""
    collector = ExchangeDataCollector()
    
    # 单次测试
    print("=" * 60)
    print("🚀 跨交易所数据收集器 v1.0 - 测试模式")
    print("=" * 60)
    
    all_prices = collector.fetch_all_exchanges()
    
    if all_prices:
        collector.save_data(all_prices)
        
        # 显示价差分析
        print("\n" + "=" * 60)
        print("📊 价差分析")
        print("=" * 60)
        
        # 合并所有价格
        symbol_prices = {}
        for exchange, prices in all_prices.items():
            for symbol, data in prices.items():
                if symbol not in symbol_prices:
                    symbol_prices[symbol] = {}
                symbol_prices[symbol][exchange] = data['price']
        
        # 计算价差
        for symbol, prices in symbol_prices.items():
            if len(prices) >= 2:
                price_list = list(prices.values())
                min_price = min(price_list)
                max_price = max(price_list)
                spread_pct = (max_price - min_price) / min_price * 100
                
                if spread_pct > 0.1:  # 只显示价差>0.1%的
                    print(f"\n{symbol}:")
                    for exchange, price in prices.items():
                        print(f"  {exchange}: ${price:,.2f}")
                    print(f"  价差：${max_price - min_price:.2f} ({spread_pct:.3f}%)")
        
        print("\n" + "=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)
    else:
        print("\n❌ 获取价格失败")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        # 连续收集模式
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        collector = ExchangeDataCollector()
        collector.run_collection(interval_minutes=interval)
    else:
        # 单次测试模式
        main()
