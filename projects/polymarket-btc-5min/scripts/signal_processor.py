#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比特币信号处理器
处理和更新最新的交易信号
"""

import json
import numpy as np
from datetime import datetime
from pathlib import Path


class SignalProcessor:
    """信号处理器"""
    
    def __init__(self, data_dir: str = "../data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def calculate_signal(self, price_data):
        """计算交易信号"""
        if len(price_data) < 2:
            return {"signal": "HOLD", "confidence": 0.5, "reason": "Insufficient data"}
        
        # 计算最近的价格变化
        current_price = price_data[-1]['close'] if isinstance(price_data[-1], dict) else price_data[-1]
        previous_price = price_data[-2]['close'] if isinstance(price_data[-2], dict) else price_data[-2]
        
        price_change = (current_price - previous_price) / previous_price
        price_change_pct = price_change * 100
        
        # 基于价格变化确定信号
        if price_change_pct > 0.5:
            signal = "BUY"
            confidence = min(0.8, abs(price_change_pct) / 2)
            reason = f"Strong upward momentum ({price_change_pct:+.2f}%)"
        elif price_change_pct < -0.5:
            signal = "SELL" 
            confidence = min(0.8, abs(price_change_pct) / 2)
            reason = f"Strong downward momentum ({price_change_pct:+.2f}%)"
        else:
            signal = "HOLD"
            confidence = 0.5 - abs(price_change_pct) / 10
            reason = f"Stable movement ({price_change_pct:+.2f}%)"
        
        return {
            "signal": signal,
            "confidence": round(confidence, 2),
            "reason": reason,
            "price_change_pct": round(price_change_pct, 2)
        }
    
    def update_latest_signal(self):
        """更新最新的信号文件"""
        # 获取最新的K线数据
        today_str = datetime.now().strftime('%Y%m%d')
        kline_file = self.data_dir / f"klines_{today_str}.json"
        
        if not kline_file.exists():
            # 尝试昨天的数据文件
            from datetime import timedelta
            yesterday = datetime.now() - timedelta(days=1)
            kline_file = self.data_dir / f"klines_{yesterday.strftime('%Y%m%d')}.json"
        
        if kline_file.exists():
            try:
                with open(kline_file, 'r') as f:
                    kline_data = json.load(f)
                
                if kline_data:
                    # 获取最新价格
                    latest_kline = kline_data[-1]
                    current_price = latest_kline['close']
                    
                    # 计算信号
                    signal_info = self.calculate_signal(kline_data)
                    
                    # 创建信号对象
                    signal_obj = {
                        "price": current_price,
                        "timestamp": datetime.now().isoformat(),
                        "klines_count": len(kline_data),
                        "signal": signal_info["signal"],
                        "confidence": signal_info["confidence"],
                        "reason": signal_info["reason"],
                        "price_change_pct": signal_info["price_change_pct"]
                    }
                    
                    # 保存到latest_signal.json
                    signal_file = self.data_dir / "latest_signal.json"
                    with open(signal_file, 'w') as f:
                        json.dump(signal_obj, f, indent=2, ensure_ascii=False)
                    
                    print(f"✅ 信号已更新：{signal_info['signal']} (信心: {signal_info['confidence']})")
                    return signal_obj
                    
            except Exception as e:
                print(f"❌ 更新信号时出错：{e}")
        
        # 如果无法从K线数据计算，则尝试从现有latest_signal.json更新时间戳
        signal_file = self.data_dir / "latest_signal.json"
        if signal_file.exists():
            try:
                with open(signal_file, 'r') as f:
                    signal_data = json.load(f)
                
                # 只更新时间戳，保持其他数据不变
                signal_data["timestamp"] = datetime.now().isoformat()
                
                with open(signal_file, 'w') as f:
                    json.dump(signal_data, f, indent=2, ensure_ascii=False)
                
                print("✅ 信号时间戳已更新")
                return signal_data
                
            except Exception as e:
                print(f"❌ 更新信号时间戳时出错：{e}")
        
        return None


if __name__ == "__main__":
    processor = SignalProcessor()
    result = processor.update_latest_signal()
    if result:
        print(f"📊 最新信号：{result}")
    else:
        print("❌ 未能更新信号")