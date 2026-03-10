#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比特币数据收集器
实时收集 BTC 价格数据，用于 5 分钟涨跌预测
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

class BTCDataCollector:
    """BTC 数据收集器"""
    
    def __init__(self, data_dir: str = "../data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # API 配置
        self.binance_api = "https://api.binance.com/api/v3"
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        
        # 数据存储
        self.price_history = []
        self.current_price = None
        
    def get_binance_price(self):
        """从 Binance 获取实时价格"""
        try:
            response = requests.get(
                f"{self.binance_api}/ticker/price",
                params={"symbol": "BTCUSDT"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "price": float(data["price"]),
                    "timestamp": datetime.now().isoformat(),
                    "source": "binance"
                }
        except Exception as e:
            print(f"❌ Binance API 错误：{e}")
        return None
    
    def get_coingecko_price(self):
        """从 CoinGecko 获取价格"""
        try:
            response = requests.get(
                f"{self.coingecko_api}/simple/price",
                params={
                    "ids": "bitcoin",
                    "vs_currencies": "usd",
                    "include_24hr_change": True
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "price": data["bitcoin"]["usd"],
                    "change_24h": data["bitcoin"]["usd_24h_change"],
                    "timestamp": datetime.now().isoformat(),
                    "source": "coingecko"
                }
        except Exception as e:
            print(f"❌ CoinGecko API 错误：{e}")
        return None
    
    def get_kline_data(self, interval="5m", limit=100):
        """获取 K 线数据"""
        try:
            response = requests.get(
                f"{self.binance_api}/klines",
                params={
                    "symbol": "BTCUSDT",
                    "interval": interval,
                    "limit": limit
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                klines = []
                for k in data:
                    klines.append({
                        "timestamp": datetime.fromtimestamp(k[0]/1000).isoformat(),
                        "open": float(k[1]),
                        "high": float(k[2]),
                        "low": float(k[3]),
                        "close": float(k[4]),
                        "volume": float(k[5])
                    })
                return klines
        except Exception as e:
            print(f"❌ K 线数据错误：{e}")
        return []
    
    def collect_and_save(self):
        """收集并保存数据"""
        print(f"\n📊 [{datetime.now().strftime('%H:%M:%S')}] 开始收集数据...")
        
        # 获取实时价格
        binance_data = self.get_binance_price()
        if binance_data:
            self.current_price = binance_data["price"]
            self.price_history.append(binance_data)
            print(f"✅ Binance: ${binance_data['price']:,.2f}")
        
        # 获取 K 线数据
        klines = self.get_kline_data()
        if klines:
            print(f"✅ 获取 {len(klines)} 条 K 线数据")
        
        # 保存到文件
        self._save_data(klines)
        
        return {
            "current_price": self.current_price,
            "klines": klines,
            "timestamp": datetime.now().isoformat()
        }
    
    def _save_data(self, klines):
        """保存数据到文件"""
        # 保存 K 线数据
        kline_file = self.data_dir / f"klines_{datetime.now().strftime('%Y%m%d')}.json"
        
        # 读取现有数据
        existing_data = []
        if kline_file.exists():
            try:
                with open(kline_file, 'r') as f:
                    existing_data = json.load(f)
            except:
                existing_data = []
        
        # 合并新数据
        for k in klines:
            if k not in existing_data:
                existing_data.append(k)
        
        # 保留最新 1000 条
        existing_data = existing_data[-1000:]
        
        # 保存
        with open(kline_file, 'w') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 数据已保存：{kline_file}")
    
    def run_continuous(self, interval=10):
        """持续收集数据"""
        print(f"🚀 开始持续收集数据 (每{interval}秒)...")
        print(f"📁 数据保存位置：{self.data_dir.absolute()}")
        
        try:
            while True:
                self.collect_and_save()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n⏹️  停止数据收集")


if __name__ == "__main__":
    collector = BTCDataCollector()
    
    # 测试单次收集
    print("=" * 50)
    print("🔍 测试数据收集器")
    print("=" * 50)
    
    result = collector.collect_and_save()
    
    print(f"\n📊 当前价格：${result['current_price']:,.2f}")
    print(f"📈 K 线数据：{len(result['klines'])} 条")
    
    # 询问是否持续运行
    print("\n" + "=" * 50)
    choice = input("是否持续收集数据？(y/n): ").strip().lower()
    if choice == 'y':
        collector.run_continuous(interval=10)
