#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级技术分析模块
包含更多技术指标：KDJ, STOCH, ADX, CCI, Williams %R 等
"""

import json
import math
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class AdvancedTechnicalAnalyzer:
    """高级技术分析器"""
    
    def __init__(self):
        self.klines = []
        
    def load_klines(self, kline_file: str):
        """加载 K 线数据"""
        with open(kline_file, 'r') as f:
            self.klines = json.load(f)
        print(f"✅ 加载 {len(self.klines)} 条 K 线数据")
    
    # ========== 基础指标 ==========
    
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
        
        prices = [float(k['close']) for k in self.klines[:period]]
        ema.append(sum(prices) / period)
        
        for i in range(period, len(self.klines)):
            price = float(self.klines[i]['close'])
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    # ========== RSI 系列 ==========
    
    def calculate_rsi(self, period: int = 14) -> List[float]:
        """相对强弱指标 (RSI)"""
        if len(self.klines) < period + 1:
            return []
        
        rsi = []
        gains = []
        losses = []
        
        for i in range(1, len(self.klines)):
            change = float(self.klines[i]['close']) - float(self.klines[i-1]['close'])
            gains.append(max(0, change))
            losses.append(max(0, -change))
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))
        
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))
        
        return rsi
    
    # ========== KDJ 指标 ==========
    
    def calculate_kdj(self, n: int = 9, m1: int = 3, m2: int = 3) -> Dict:
        """KDJ 随机指标"""
        if len(self.klines) < n:
            return {"k": [], "d": [], "j": []}
        
        k_values = []
        d_values = []
        j_values = []
        
        for i in range(n - 1, len(self.klines)):
            # 计算 RSV
            highest = max(float(self.klines[j]['high']) for j in range(i-n+1, i+1))
            lowest = min(float(self.klines[j]['low']) for j in range(i-n+1, i+1))
            close = float(self.klines[i]['close'])
            
            if highest == lowest:
                rsv = 50
            else:
                rsv = ((close - lowest) / (highest - lowest)) * 100
            
            # 计算 K 值
            if len(k_values) == 0:
                k_values.append(50)  # 初始值
            else:
                k_values.append(((m1 - 1) * k_values[-1] + rsv) / m1)
            
            # 计算 D 值
            if len(d_values) == 0:
                d_values.append(50)  # 初始值
            else:
                d_values.append(((m2 - 1) * d_values[-1] + k_values[-1]) / m2)
            
            # 计算 J 值
            j_values.append(3 * k_values[-1] - 2 * d_values[-1])
        
        return {"k": k_values, "d": d_values, "j": j_values}
    
    # ========== MACD 指标 ==========
    
    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """MACD 指标"""
        ema_fast = self.calculate_ema(fast)
        ema_slow = self.calculate_ema(slow)
        
        if len(ema_fast) < signal or len(ema_slow) < signal:
            return {"macd": [], "signal": [], "histogram": []}
        
        macd_line = []
        for i in range(len(ema_slow)):
            offset = len(ema_fast) - len(ema_slow)
            macd_line.append(ema_fast[i + offset] - ema_slow[i])
        
        multiplier = 2 / (signal + 1)
        signal_line = [sum(macd_line[:signal]) / signal]
        
        for i in range(signal, len(macd_line)):
            signal_line.append((macd_line[i] - signal_line[-1]) * multiplier + signal_line[-1])
        
        histogram = [macd_line[i] - signal_line[i] for i in range(len(signal_line))]
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }
    
    # ========== 布林带 ==========
    
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
    
    # ========== STOCH 随机指标 ==========
    
    def calculate_stoch(self, k_period: int = 14, d_period: int = 3) -> Dict:
        """STOCH 随机指标"""
        if len(self.klines) < k_period:
            return {"k": [], "d": []}
        
        k_values = []
        d_values = []
        
        for i in range(k_period - 1, len(self.klines)):
            highest = max(float(self.klines[j]['high']) for j in range(i-k_period+1, i+1))
            lowest = min(float(self.klines[j]['low']) for j in range(i-k_period+1, i+1))
            close = float(self.klines[i]['close'])
            
            if highest == lowest:
                k_values.append(50)
            else:
                k_values.append(((close - lowest) / (highest - lowest)) * 100)
            
            # 计算 D 值 (K 的移动平均)
            if len(k_values) >= d_period:
                d_values.append(sum(k_values[-d_period:]) / d_period)
        
        return {"k": k_values, "d": d_values}
    
    # ========== ADX 趋势强度指标 ==========
    
    def calculate_adx(self, period: int = 14) -> Dict:
        """ADX 平均趋向指数"""
        if len(self.klines) < period * 2 + 1:
            return {"adx": [], "plus_di": [], "minus_di": []}
        
        plus_dm = []
        minus_dm = []
        tr = []
        
        for i in range(1, len(self.klines)):
            high = float(self.klines[i]['high'])
            low = float(self.klines[i]['low'])
            prev_high = float(self.klines[i-1]['high'])
            prev_low = float(self.klines[i-1]['low'])
            prev_close = float(self.klines[i-1]['close'])
            
            # +DM 和 -DM
            up_move = high - prev_high
            down_move = prev_low - low
            
            if up_move > down_move and up_move > 0:
                plus_dm.append(up_move)
            else:
                plus_dm.append(0)
            
            if down_move > up_move and down_move > 0:
                minus_dm.append(down_move)
            else:
                minus_dm.append(0)
            
            # True Range
            tr.append(max(high - low, abs(high - prev_close), abs(low - prev_close)))
        
        # 平滑计算
        plus_di = []
        minus_di = []
        dx = []
        adx = []
        
        for i in range(period - 1, len(tr)):
            if i == period - 1:
                sum_plus_dm = sum(plus_dm[:period])
                sum_minus_dm = sum(minus_dm[:period])
                sum_tr = sum(tr[:period])
            else:
                sum_plus_dm = plus_di[-1] * (period - 1) + plus_dm[i]
                sum_minus_dm = minus_di[-1] * (period - 1) + minus_dm[i]
                sum_tr = adx[-1] * (period - 1) + tr[i] if adx else sum(tr[:period])
            
            plus_di.append((sum_plus_dm / sum_tr * 100) if sum_tr > 0 else 0)
            minus_di.append((sum_minus_dm / sum_tr * 100) if sum_tr > 0 else 0)
            
            if plus_di[-1] + minus_di[-1] > 0:
                dx.append(abs(plus_di[-1] - minus_di[-1]) / (plus_di[-1] + minus_di[-1]) * 100)
            else:
                dx.append(0)
            
            if len(dx) >= period:
                if len(adx) == 0:
                    adx.append(sum(dx[:period]) / period)
                elif i < len(dx):
                    adx.append((adx[-1] * (period - 1) + dx[i]) / period)
        
        return {"adx": adx, "plus_di": plus_di, "minus_di": minus_di}
    
    # ========== CCI 商品通道指标 ==========
    
    def calculate_cci(self, period: int = 20) -> List[float]:
        """CCI 商品通道指标"""
        if len(self.klines) < period:
            return []
        
        cci = []
        
        for i in range(period - 1, len(self.klines)):
            # 计算典型价格
            typical_prices = []
            for j in range(i-period+1, i+1):
                tp = (float(self.klines[j]['high']) + 
                      float(self.klines[j]['low']) + 
                      float(self.klines[j]['close'])) / 3
                typical_prices.append(tp)
            
            # 计算 SMA
            sma_tp = sum(typical_prices) / period
            
            # 计算平均偏差
            mean_deviation = sum(abs(tp - sma_tp) for tp in typical_prices) / period
            
            if mean_deviation == 0:
                cci.append(0)
            else:
                current_tp = (float(self.klines[i]['high']) + 
                             float(self.klines[i]['low']) + 
                             float(self.klines[i]['close'])) / 3
                cci.append((current_tp - sma_tp) / (0.015 * mean_deviation))
        
        return cci
    
    # ========== Williams %R ==========
    
    def calculate_williams_r(self, period: int = 14) -> List[float]:
        """Williams %R 指标"""
        if len(self.klines) < period:
            return []
        
        wr = []
        
        for i in range(period - 1, len(self.klines)):
            highest = max(float(self.klines[j]['high']) for j in range(i-period+1, i+1))
            lowest = min(float(self.klines[j]['low']) for j in range(i-period+1, i+1))
            close = float(self.klines[i]['close'])
            
            if highest == lowest:
                wr.append(-50)
            else:
                wr.append(((highest - close) / (highest - lowest)) * -100)
        
        return wr
    
    # ========== 综合信号生成 ==========
    
    def generate_advanced_signal(self) -> Dict:
        """生成高级交易信号 (多指标组合)"""
        if len(self.klines) < 50:
            return {"signal": "HOLD", "confidence": 0, "reason": "数据不足"}
        
        # 计算所有指标
        rsi = self.calculate_rsi()
        kdj = self.calculate_kdj()
        macd = self.calculate_macd()
        bb = self.calculate_bollinger_bands()
        stoch = self.calculate_stoch()
        adx = self.calculate_adx()
        cci = self.calculate_cci()
        wr = self.calculate_williams_r()
        
        if not all([rsi, kdj['k'], macd['macd'], bb['upper'], stoch['k'], cci, wr]):
            return {"signal": "HOLD", "confidence": 0, "reason": "指标计算失败"}
        
        # 获取最新值
        current_price = float(self.klines[-1]['close'])
        
        indicators = {
            "rsi": rsi[-1],
            "kdj_k": kdj['k'][-1],
            "kdj_d": kdj['d'][-1],
            "kdj_j": kdj['j'][-1],
            "macd": macd['macd'][-1],
            "macd_signal": macd['signal'][-1],
            "macd_hist": macd['histogram'][-1],
            "bb_upper": bb['upper'][-1],
            "bb_lower": bb['lower'][-1],
            "bb_middle": bb['middle'][-1],
            "stoch_k": stoch['k'][-1],
            "stoch_d": stoch['d'][-1] if stoch['d'] else 50,
            "adx": adx['adx'][-1] if adx['adx'] else 0,
            "cci": cci[-1],
            "williams_r": wr[-1]
        }
        
        # 信号评分系统 (加权)
        score = 0
        reasons = []
        weights = {
            "rsi": 2,
            "kdj": 2,
            "macd": 2,
            "bb": 2,
            "stoch": 1,
            "adx": 1,
            "cci": 1,
            "wr": 1
        }
        
        # RSI 信号
        if indicators["rsi"] < 30:
            score += weights["rsi"] * 2
            reasons.append(f"RSI 超卖 ({indicators['rsi']:.1f})")
        elif indicators["rsi"] > 70:
            score -= weights["rsi"] * 2
            reasons.append(f"RSI 超买 ({indicators['rsi']:.1f})")
        
        # KDJ 信号
        if indicators["kdj_k"] < 20 and indicators["kdj_j"] < 0:
            score += weights["kdj"] * 2
            reasons.append("KDJ 超卖区")
        elif indicators["kdj_k"] > 80 and indicators["kdj_j"] > 100:
            score -= weights["kdj"] * 2
            reasons.append("KDJ 超买区")
        
        # MACD 信号
        if indicators["macd"] > indicators["macd_signal"]:
            score += weights["macd"]
            reasons.append("MACD 金叉")
        else:
            score -= weights["macd"]
            reasons.append("MACD 死叉")
        
        # MACD Histogram 动量
        if indicators["macd_hist"] > 0:
            score += weights["macd"]
            reasons.append("MACD 动量向上")
        else:
            score -= weights["macd"]
            reasons.append("MACD 动量向下")
        
        # 布林带信号
        if current_price < indicators["bb_lower"]:
            score += weights["bb"] * 2
            reasons.append("价格触及布林带下轨")
        elif current_price > indicators["bb_upper"]:
            score -= weights["bb"] * 2
            reasons.append("价格触及布林带上轨")
        
        # STOCH 信号
        if indicators["stoch_k"] < 20:
            score += weights["stoch"]
            reasons.append("STOCH 超卖")
        elif indicators["stoch_k"] > 80:
            score -= weights["stoch"]
            reasons.append("STOCH 超买")
        
        # ADX 趋势强度
        if indicators["adx"] > 25:
            if indicators["macd"] > indicators["macd_signal"]:
                score += weights["adx"]
                reasons.append(f"强趋势向上 (ADX: {indicators['adx']:.1f})")
            else:
                score -= weights["adx"]
                reasons.append(f"强趋势向下 (ADX: {indicators['adx']:.1f})")
        
        # CCI 信号
        if indicators["cci"] < -100:
            score += weights["cci"]
            reasons.append("CCI 超卖")
        elif indicators["cci"] > 100:
            score -= weights["cci"]
            reasons.append("CCI 超买")
        
        # Williams %R 信号
        if indicators["williams_r"] < -80:
            score += weights["wr"]
            reasons.append("Williams %R 超卖")
        elif indicators["williams_r"] > -20:
            score -= weights["wr"]
            reasons.append("Williams %R 超买")
        
        # 生成最终信号
        max_score = sum(weights.values()) * 4  # 最大可能分数
        confidence = (abs(score) / max_score) * 100
        
        if score >= 8:
            signal = "BUY"
        elif score <= -8:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        return {
            "signal": signal,
            "confidence": min(100, confidence),
            "reasons": reasons,
            "score": score,
            "indicators": indicators,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_and_print(self):
        """分析并打印结果"""
        print("\n" + "=" * 70)
        print("📊 高级技术分析报告")
        print("=" * 70)
        
        signal = self.generate_advanced_signal()
        
        print(f"\n🎯 交易信号：{signal['signal']}")
        print(f"📈 置信度：{signal['confidence']:.1f}%")
        print(f"💡 原因 ({len(signal['reasons'])} 个):")
        for reason in signal['reasons'][:5]:  # 最多显示 5 个
            print(f"   - {reason}")
        
        print(f"\n📉 技术指标:")
        ind = signal['indicators']
        print(f"   RSI: {ind['rsi']:.2f}")
        print(f"   KDJ: K={ind['kdj_k']:.2f}, D={ind['kdj_d']:.2f}, J={ind['kdj_j']:.2f}")
        print(f"   MACD: {ind['macd']:.4f}, Signal: {ind['macd_signal']:.4f}")
        print(f"   STOCH: K={ind['stoch_k']:.2f}, D={ind['stoch_d']:.2f}")
        print(f"   ADX: {ind['adx']:.2f}")
        print(f"   CCI: {ind['cci']:.2f}")
        print(f"   Williams %R: {ind['williams_r']:.2f}")
        print(f"   当前价格：${ind.get('price', float(self.klines[-1]['close'])):,.2f}")
        
        print("\n" + "=" * 70)
        
        return signal


if __name__ == "__main__":
    analyzer = AdvancedTechnicalAnalyzer()
    
    # 查找 K 线文件
    data_dir = Path("../data")
    kline_files = list(data_dir.glob("klines_*.json"))
    
    if not kline_files:
        print("❌ 未找到 K 线数据文件")
        exit(1)
    
    latest_file = max(kline_files, key=lambda p: p.stat().st_mtime)
    print(f"📁 使用数据文件：{latest_file}")
    
    analyzer.load_klines(str(latest_file))
    analyzer.analyze_and_print()
