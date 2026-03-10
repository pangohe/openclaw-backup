#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Binance 历史 K 线数据导入器
下载指定时间段嘅 5 分钟 K 线数据
"""

import requests
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import time

class BinanceHistoryDownloader:
    """Binance 历史数据下载器"""
    
    def __init__(self, symbol: str = "BTCUSDT", interval: str = "5m"):
        self.symbol = symbol
        self.interval = interval
        self.base_url = "https://api.binance.com/api/v3/klines"
        self.data_dir = Path("../data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def download_date_range(self, start_date: str, end_date: str, limit_per_request: int = 1000) -> List[Dict]:
        """
        下载指定日期范围嘅 K 线数据
        
        Args:
            start_date: 开始日期 (格式：YYYY-MM-DD)
            end_date: 结束日期 (格式：YYYY-MM-DD)
            limit_per_request: 每次请求最大条数 (最多 1000)
        """
        print(f"\n🚀 开始下载历史数据")
        print(f"📊 交易对：{self.symbol}")
        print(f"⏱️  周期：{self.interval}")
        print(f"📅 范围：{start_date} 至 {end_date}")
        print("=" * 70)
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        all_klines = []
        current_start = start_dt
        
        while current_start < end_dt:
            # 计算结束时间 (最多 1000 条 K 线)
            current_end = current_start + timedelta(minutes=limit_per_request * 5)
            if current_end > end_dt:
                current_end = end_dt
            
            # 转换时间戳
            start_ts = int(current_start.timestamp() * 1000)
            end_ts = int(current_end.timestamp() * 1000)
            
            print(f"\n📥 下载：{current_start.strftime('%Y-%m-%d %H:%M')} → {current_end.strftime('%Y-%m-%d %H:%M')}")
            
            try:
                response = requests.get(
                    self.base_url,
                    params={
                        "symbol": self.symbol,
                        "interval": self.interval,
                        "startTime": start_ts,
                        "endTime": end_ts,
                        "limit": limit_per_request
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 转换数据格式
                    for k in data:
                        kline = {
                            "timestamp": datetime.fromtimestamp(k[0]/1000).isoformat(),
                            "open": float(k[1]),
                            "high": float(k[2]),
                            "low": float(k[3]),
                            "close": float(k[4]),
                            "volume": float(k[5]),
                            "quote_volume": float(k[7]),
                            "trades": int(k[8])
                        }
                        all_klines.append(kline)
                    
                    print(f"✅ 获取 {len(data)} 条数据")
                    
                    if len(data) < limit_per_request:
                        print(f"⚠️  数据已取完")
                        break
                else:
                    print(f"❌ API 错误：{response.status_code}")
                    print(f"   {response.text}")
                    
            except Exception as e:
                print(f"❌ 下载失败：{e}")
            
            # 移动时间窗口
            current_start = current_end
            
            # 避免 API 限制
            time.sleep(0.5)
        
        print(f"\n✅ 下载完成！共 {len(all_klines)} 条 K 线")
        return all_klines
    
    def save_klines(self, klines: List[Dict], filename: str = None):
        """保存 K 线数据到文件"""
        if not filename:
            filename = f"klines_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_file = self.data_dir / filename
        
        # 读取现有数据 (如果有)
        existing_klines = []
        history_file = self.data_dir / "klines_history.json"
        
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    existing_klines = json.load(f)
                print(f"📖 读取现有数据：{len(existing_klines)} 条")
            except:
                existing_klines = []
        
        # 合并数据 (去重)
        existing_timestamps = {k['timestamp'] for k in existing_klines}
        new_klines = [k for k in klines if k['timestamp'] not in existing_timestamps]
        
        all_klines = existing_klines + new_klines
        
        # 按时间排序
        all_klines.sort(key=lambda x: x['timestamp'])
        
        # 保存
        with open(output_file, 'w') as f:
            json.dump(all_klines, f, indent=2, ensure_ascii=False)
        
        # 同时更新 klines_history.json
        with open(history_file, 'w') as f:
            json.dump(all_klines, f, indent=2, ensure_ascii=False)
        
        print(f"💾 数据已保存：{output_file}")
        print(f"📊 总数据量：{len(all_klines)} 条 K 线")
        print(f"🆕 新增数据：{len(new_klines)} 条")
        
        # 计算时间跨度
        if all_klines:
            first_time = datetime.fromisoformat(all_klines[0]['timestamp'])
            last_time = datetime.fromisoformat(all_klines[-1]['timestamp'])
            time_span = last_time - first_time
            
            print(f"📅 时间跨度：{first_time} 至 {last_time}")
            print(f"⏱️  总时长：{time_span.days} 天 {time_span.seconds // 3600} 小时")
            print(f"📈 约 {time_span.total_seconds() / 300:.0f} 个 5 分钟周期")
        
        return output_file
    
    def download_and_save(self, days: int = 7):
        """下载最近 N 日嘅数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        klines = self.download_date_range(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        self.save_klines(klines)
        
        return klines


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Binance 历史 K 线数据下载器")
    print("=" * 70)
    
    downloader = BinanceHistoryDownloader(symbol="BTCUSDT", interval="5m")
    
    # 询问下载天数
    print("\n💡 推荐选项:")
    print("   7 日  = ~2,000 条  (基础回测)")
    print("   30 日 = ~8,600 条  (充分回测)")
    print("   180 日= ~52,000 条 (6 个月，训练 ML 模型)")
    print("   365 日= ~105,000 条 (1 年，完整周期)")
    
    try:
        days_input = input("\n要下载几日嘅数据？(默认 180): ").strip()
        days = int(days_input) if days_input else 180
    except:
        days = 180
    
    print(f"\n✅ 开始下载最近 {days} 日数据...")
    
    klines = downloader.download_and_save(days=days)
    
    print("\n" + "=" * 70)
    print("🎉 历史数据导入完成！")
    print("=" * 70)
    print(f"\n下一步:")
    print("1. 运行 simulator.py 进行回测")
    print("2. 运行 strategy_optimizer.py 优化策略")
    print("3. 查看 web_dashboard/index.html 可视化界面")
    print("=" * 70)
