#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术分析模块
计算各种技术指标，生成交易信号
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class TechnicalAnalyzer:
    """技术分析器"""
    
    def __init__(self):
        self.klines = []
        
    def load_klines(self, kline_file: str):
        """加载 K 线数据"""
        with open(kline_file, 'r') as f:
            self.klines = json.load(f)
        print(f"✅ 加载 {len(self.klines)} 条 K 线数据")
    
    def calculate_sma(self, period: int = 20) -> List[float]:
        """简单移动平均线 (SMA)"""
        if len(self.klines) < period:
            return []
        
        sma = []
        for i in range(period - 1, len(self.klines)):
            prices = [float(k['close']) for k in self.klines[i-period+1:i+1]]
            sma.append(sum(prices) / period)
        return sma
    
    def calculate_ema(self, period: int = 12) -> List[float]:
        """指数移动平均线 (EMA)"""
        if len(self.klines) < period:
            return []
        
        ema = []
        multiplier = 2 / (period + 1)
        
        # 第一个 EMA 用 SMA
        prices = [float(k['close']) for k in self.klines[:period]]
        ema.append(sum(prices) / period)
        
        # 计算后续 EMA
        for i in range(period, len(self.klines)):
            price = float(self.klines[i]['close'])
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    def calculate_rsi(self, period: int = 14) -> List[float]:
        """相对强弱指标 (RSI)"""
        if len(self.klines) < period + 1:
            return []
        
        rsi = []
        gains = []
        losses = []
        
        # 计算价格变化
        for i in range(1, len(self.klines)):
            change = float(self.klines[i]['close']) - float(self.klines[i-1]['close'])
            gains.append(max(0, change))
            losses.append(max(0, -change))
        
        # 第一个 RSI
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))
        
        # 后续 RSI (平滑)
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))
        
        return rsi
    
    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """MACD 指标"""
        ema_fast = self.calculate_ema(fast)
        ema_slow = self.calculate_ema(slow)
        
        if len(ema_fast) < signal or len(ema_slow) < signal:
            return {"macd": [], "signal": [], "histogram": []}
        
        # MACD 线
        macd_line = []
        for i in range(len(ema_slow)):
            offset = len(ema_fast) - len(ema_slow)
            macd_line.append(ema_fast[i + offset] - ema_slow[i])
        
        # Signal 线 (MACD 的 EMA)
        multiplier = 2 / (signal + 1)
        signal_line = [sum(macd_line[:signal]) / signal]
        
        for i in range(signal, len(macd_line)):
            signal_line.append((macd_line[i] - signal_line[-1]) * multiplier + signal_line[-1])
        
        # Histogram
        histogram = [macd_line[i] - signal_line[i] for i in range(len(signal_line))]
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }
    
    def calculate_bollinger_bands(self, period: int = 20, std_dev: int = 2) -> Dict:
        """布林带"""
        sma = self.calculate_sma(period)
        
        if len(sma) == 0:
            return {"upper": [], "middle": [], "lower": []}
        
        upper = []
        lower = []
        
        for i in range(len(sma)):
            kline_idx = i + period - 1
            prices = [float(self.klines[j]['close']) for j in range(kline_idx - period + 1, kline_idx + 1)]
            
            # 计算标准差
            mean = sum(prices) / period
            variance = sum((p - mean) ** 2 for p in prices) / period
            std = variance ** 0.5
            
            upper.append(sma[i] + std_dev * std)
            lower.append(sma[i] - std_dev * std)
        
        return {
            "upper": upper,
            "middle": sma,
            "lower": lower
        }
    
    def generate_signal(self) -> Dict:
        """生成交易信号"""
        if len(self.klines) < 30:
            return {"signal": "HOLD", "confidence": 0, "reason": "数据不足"}
        
        # 计算所有指标
        rsi = self.calculate_rsi()
        macd = self.calculate_macd()
        bb = self.calculate_bollinger_bands()
        
        if not rsi or not macd['macd'] or not bb['upper']:
            return {"signal": "HOLD", "confidence": 0, "reason": "指标计算失败"}
        
        # 获取最新值
        current_rsi = rsi[-1]
        current_macd = macd['macd'][-1]
        current_signal = macd['signal'][-1]
        current_histogram = macd['histogram'][-1]
        current_price = float(self.klines[-1]['close'])
        bb_upper = bb['upper'][-1]
        bb_lower = bb['lower'][-1]
        
        # 信号评分
        score = 0
        reasons = []
        
        # RSI 信号
        if current_rsi < 30:
            score += 2
            reasons.append(f"RSI 超卖 ({current_rsi:.1f})")
        elif current_rsi > 70:
            score -= 2
            reasons.append(f"RSI 超买 ({current_rsi:.1f})")
        
        # MACD 信号
        if current_macd > current_signal:
            score += 1
            reasons.append("MACD 金叉")
        else:
            score -= 1
            reasons.append("MACD 死叉")
        
        # Histogram 动量
        if current_histogram > 0:
            score += 1
            reasons.append("MACD 动量向上")
        else:
            score -= 1
            reasons.append("MACD 动量向下")
        
        # 布林带信号
        if current_price < bb_lower:
            score += 2
            reasons.append("价格触及布林带下轨")
        elif current_price > bb_upper:
            score -= 2
            reasons.append("价格触及布林带上轨")
        
        # 生成最终信号
        if score >= 3:
            signal = "BUY"
            confidence = min(100, score * 20)
        elif score <= -3:
            signal = "SELL"
            confidence = min(100, abs(score) * 20)
        else:
            signal = "HOLD"
            confidence = abs(score) * 20
        
        return {
            "signal": signal,
            "confidence": confidence,
            "reasons": reasons,
            "score": score,
            "indicators": {
                "rsi": current_rsi,
                "macd": current_macd,
                "macd_signal": current_signal,
                "histogram": current_histogram,
                "price": current_price,
                "bb_upper": bb_upper,
                "bb_lower": bb_lower
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_and_print(self):
        """分析并打印结果"""
        print("\n" + "=" * 60)
        print("📊 技术分析报告")
        print("=" * 60)
        
        signal = self.generate_signal()
        
        print(f"\n🎯 交易信号：{signal['signal']}")
        print(f"📈 置信度：{signal['confidence']}%")
        print(f"💡 原因:")
        for reason in signal['reasons']:
            print(f"   - {reason}")
        
        print(f"\n📉 技术指标:")
        indicators = signal['indicators']
        print(f"   RSI: {indicators['rsi']:.2f}")
        print(f"   MACD: {indicators['macd']:.4f}")
        print(f"   MACD Signal: {indicators['macd_signal']:.4f}")
        print(f"   Histogram: {indicators['histogram']:.4f}")
        print(f"   当前价格：${indicators['price']:,.2f}")
        print(f"   布林带上轨：${indicators['bb_upper']:,.2f}")
        print(f"   布林带下轨：${indicators['bb_lower']:,.2f}")
        
        print("\n" + "=" * 60)
        
        return signal


if __name__ == "__main__":
    analyzer = TechnicalAnalyzer()
    
    # 查找 K 线文件
    data_dir = Path("../data")
    kline_files = list(data_dir.glob("klines_*.json"))
    
    if not kline_files:
        print("❌ 未找到 K 线数据文件")
        print("💡 请先运行 data_collector.py 收集数据")
        exit(1)
    
    # 使用最新文件
    latest_file = max(kline_files, key=lambda p: p.stat().st_mtime)
    print(f"📁 使用数据文件：{latest_file}")
    
    analyzer.load_klines(str(latest_file))
    analyzer.analyze_and_print()
