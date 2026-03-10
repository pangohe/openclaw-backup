#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LSTM 机器学习价格预测模型
用于预测 BTC 5 分钟后嘅价格涨跌
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from collections import deque

# 尝试导入 TensorFlow/Keras
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    Sequential = type(None)  # 占位符
    print("⚠️  TensorFlow 未安装，使用简化版预测模型")


class LSTMPredictor:
    """LSTM 价格预测器"""
    
    def __init__(self, lookback: int = 60, prediction_horizon: int = 1):
        """
        Args:
            lookback: 回溯时间步 (用过去多少条 K 线预测)
            prediction_horizon: 预测未来多少条 K 线
        """
        self.lookback = lookback
        self.prediction_horizon = prediction_horizon
        self.model = None
        self.scaler = None
        self.training_history = None
        
    def prepare_data(self, klines: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """准备训练数据"""
        # 提取收盘价
        prices = np.array([float(k['close']) for k in klines], dtype=np.float32)
        
        # 归一化
        self.scaler = {
            'mean': np.mean(prices),
            'std': np.std(prices)
        }
        normalized_prices = (prices - self.scaler['mean']) / self.scaler['std']
        
        # 创建序列数据
        X, y = [], []
        for i in range(self.lookback, len(normalized_prices) - self.prediction_horizon):
            X.append(normalized_prices[i-self.lookback:i])
            # 预测未来价格是涨还是跌 (1=涨，0=跌)
            future_price = normalized_prices[i + self.prediction_horizon]
            current_price = normalized_prices[i]
            y.append(1 if future_price > current_price else 0)
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape: Tuple) -> Sequential:
        """构建 LSTM 模型"""
        if not TENSORFLOW_AVAILABLE:
            return None
        
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25, activation='relu'),
            Dense(1, activation='sigmoid')  # 二分类：涨/跌
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train(self, klines: List[Dict], epochs: int = 50, batch_size: int = 32, validation_split: float = 0.2):
        """训练模型"""
        if not TENSORFLOW_AVAILABLE:
            print("⚠️  使用简化版训练")
            return self._train_simple(klines)
        
        print(f"\n🚀 开始训练 LSTM 模型")
        print(f"📊 数据量：{len(klines)} 条 K 线")
        print(f"⏱️  回溯窗口：{self.lookback} 步")
        print(f"📈 预测范围：{self.prediction_horizon} 步")
        
        # 准备数据
        X, y = self.prepare_data(klines)
        X = X.reshape((X.shape[0], X.shape[1], 1))  # LSTM 需要 3D 输入
        
        print(f"✅ 训练数据形状：X={X.shape}, y={y.shape}")
        print(f"📊 类别分布：涨={sum(y)} 跌={len(y)-sum(y)}")
        
        # 构建模型
        self.model = self.build_model((X.shape[1], 1))
        print(f"\n🏗️  模型结构:")
        self.model.summary()
        
        # 训练
        print(f"\n📚 开始训练 (epochs={epochs}, batch_size={batch_size})...")
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1
        )
        
        self.training_history = history.history
        
        # 保存模型
        self.save_model()
        
        return history
    
    def _train_simple(self, klines: List[Dict]):
        """简化版训练 (无 TensorFlow 时使用)"""
        print(f"\n🚀 使用简化版训练 (统计模型)")
        
        # 准备数据
        X, y = self.prepare_data(klines)
        
        # 简单统计：计算不同模式下的涨跌概率
        self.simple_model = {
            'up_probability': np.mean(y),
            'recent_trend': np.mean(y[-20:]) if len(y) >= 20 else np.mean(y),
            'training_samples': len(y)
        }
        
        print(f"✅ 简化模型训练完成")
        print(f"   基础上涨概率：{self.simple_model['up_probability']:.2%}")
        print(f"   近期趋势：{self.simple_model['recent_trend']:.2%}")
        
        return self.simple_model
    
    def predict(self, klines: List[Dict]) -> Dict:
        """预测未来价格涨跌"""
        if len(klines) < self.lookback:
            return {
                "prediction": "HOLD",
                "confidence": 0,
                "reason": "数据不足"
            }
        
        if TENSORFLOW_AVAILABLE and self.model:
            return self._predict_keras(klines)
        else:
            return self._predict_simple(klines)
    
    def _predict_keras(self, klines: List[Dict]) -> Dict:
        """使用 Keras 模型预测"""
        # 准备最后 lookback 条数据
        recent_prices = np.array([float(k['close']) for k in klines[-self.lookback:]], dtype=np.float32)
        normalized = (recent_prices - self.scaler['mean']) / self.scaler['std']
        X = normalized.reshape((1, self.lookback, 1))
        
        # 预测
        prediction = self.model.predict(X, verbose=0)[0][0]
        
        # 转换为信号
        if prediction > 0.6:
            signal = "BUY"
            confidence = (prediction - 0.5) * 2 * 100
        elif prediction < 0.4:
            signal = "SELL"
            confidence = (0.5 - prediction) * 2 * 100
        else:
            signal = "HOLD"
            confidence = abs(prediction - 0.5) * 2 * 100
        
        return {
            "prediction": signal,
            "confidence": min(100, confidence),
            "probability": float(prediction),
            "model_type": "LSTM",
            "timestamp": datetime.now().isoformat()
        }
    
    def _predict_simple(self, klines: List[Dict]) -> Dict:
        """简化版预测"""
        if not hasattr(self, 'simple_model'):
            return {
                "prediction": "HOLD",
                "confidence": 0,
                "reason": "模型未训练"
            }
        
        # 分析近期趋势
        recent_prices = [float(k['close']) for k in klines[-20:]]
        price_changes = [recent_prices[i] - recent_prices[i-1] for i in range(1, len(recent_prices))]
        
        up_count = sum(1 for change in price_changes if change > 0)
        up_ratio = up_count / len(price_changes) if price_changes else 0.5
        
        # 结合基础概率和近期趋势
        base_prob = self.simple_model['up_probability']
        recent_trend = self.simple_model['recent_trend']
        
        # 加权预测
        final_prob = (base_prob * 0.4 + up_ratio * 0.4 + recent_trend * 0.2)
        
        if final_prob > 0.6:
            signal = "BUY"
            confidence = (final_prob - 0.5) * 2 * 100
        elif final_prob < 0.4:
            signal = "SELL"
            confidence = (0.5 - final_prob) * 2 * 100
        else:
            signal = "HOLD"
            confidence = abs(final_prob - 0.5) * 2 * 100
        
        return {
            "prediction": signal,
            "confidence": min(100, confidence),
            "probability": float(final_prob),
            "up_ratio": float(up_ratio),
            "model_type": "Statistical",
            "timestamp": datetime.now().isoformat()
        }
    
    def save_model(self, model_dir: str = "../models"):
        """保存模型"""
        model_path = Path(model_dir)
        model_path.mkdir(parents=True, exist_ok=True)
        
        if TENSORFLOW_AVAILABLE and self.model:
            model_file = model_path / "lstm_model.h5"
            self.model.save(str(model_file))
            print(f"💾 模型已保存：{model_file}")
        
        # 保存 scaler
        scaler_file = model_path / "scaler.json"
        with open(scaler_file, 'w') as f:
            json.dump(self.scaler, f, indent=2)
        print(f"💾 Scaler 已保存：{scaler_file}")
        
        # 保存训练历史
        if self.training_history:
            history_file = model_path / "training_history.json"
            with open(history_file, 'w') as f:
                json.dump(self.training_history, f, indent=2)
            print(f"💾 训练历史已保存：{history_file}")
    
    def load_model(self, model_dir: str = "../models"):
        """加载模型"""
        model_path = Path(model_dir)
        
        if TENSORFLOW_AVAILABLE:
            model_file = model_path / "lstm_model.h5"
            if model_file.exists():
                self.model = load_model(str(model_file))
                print(f"✅ 模型已加载：{model_file}")
        
        scaler_file = model_path / "scaler.json"
        if scaler_file.exists():
            with open(scaler_file, 'r') as f:
                self.scaler = json.load(f)
            print(f"✅ Scaler 已加载：{scaler_file}")


class CombinedPredictor:
    """结合技术分析 + LSTM 的混合预测器"""
    
    def __init__(self):
        self.lstm_predictor = LSTMPredictor(lookback=60)
        self.technical_signals = []
        
    def train_lstm(self, klines: List[Dict], epochs: int = 30):
        """训练 LSTM 模型"""
        return self.lstm_predictor.train(klines, epochs=epochs)
    
    def generate_combined_signal(self, klines: List[Dict], technical_analyzer) -> Dict:
        """生成混合信号 (技术分析 + LSTM)"""
        # 获取技术分析信号
        tech_signal = technical_analyzer.generate_advanced_signal()
        
        # 获取 LSTM 预测
        lstm_prediction = self.lstm_predictor.predict(klines)
        
        # 融合两个信号
        combined_score = 0
        reasons = tech_signal.get('reasons', [])
        
        # 技术分析权重 60%
        tech_score = tech_signal.get('score', 0)
        combined_score += tech_score * 0.6
        
        # LSTM 权重 40%
        if lstm_prediction['prediction'] == 'BUY':
            combined_score += lstm_prediction['confidence'] * 0.4
            reasons.append(f"LSTM 看涨 ({lstm_prediction['confidence']:.0f}%)")
        elif lstm_prediction['prediction'] == 'SELL':
            combined_score -= lstm_prediction['confidence'] * 0.4
            reasons.append(f"LSTM 看跌 ({lstm_prediction['confidence']:.0f}%)")
        
        # 生成最终信号
        if combined_score >= 8:
            signal = "BUY"
        elif combined_score <= -8:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        # 计算综合置信度
        tech_conf = tech_signal.get('confidence', 0)
        lstm_conf = lstm_prediction.get('confidence', 0)
        combined_confidence = (tech_conf * 0.6 + lstm_conf * 0.4)
        
        return {
            "signal": signal,
            "confidence": min(100, combined_confidence),
            "reasons": reasons,
            "score": combined_score,
            "technical_signal": tech_signal.get('signal'),
            "lstm_signal": lstm_prediction.get('prediction'),
            "technical_confidence": tech_conf,
            "lstm_confidence": lstm_conf,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    print("=" * 70)
    print("🤖 LSTM BTC 价格预测模型")
    print("=" * 70)
    
    # 加载数据
    data_dir = Path("../data")
    kline_file = data_dir / "klines_history.json"
    
    if not kline_file.exists():
        print(f"\n❌ 数据文件不存在：{kline_file}")
        print("💡 请先运行 history_downloader.py 下载历史数据")
        exit(1)
    
    with open(kline_file, 'r') as f:
        klines = json.load(f)
    
    print(f"\n📊 加载 {len(klines)} 条 K 线数据")
    print(f"📅 时间范围：{klines[0]['timestamp']} 至 {klines[-1]['timestamp']}")
    
    # 创建预测器
    predictor = LSTMPredictor(lookback=60)
    
    # 询问是否训练
    print(f"\n{'=' * 70}")
    print("📚 模型训练")
    print(f"{'=' * 70}")
    
    if TENSORFLOW_AVAILABLE:
        choice = input("\n是否训练 LSTM 模型？(y/n): ").strip().lower()
        if choice == 'y':
            epochs = input("训练轮数 (默认 30): ").strip()
            epochs = int(epochs) if epochs else 30
            predictor.train(klines, epochs=epochs)
        else:
            # 尝试加载现有模型
            predictor.load_model()
    else:
        print("\n⚠️  TensorFlow 不可用，使用简化统计模型")
        predictor.train(klines)
    
    # 预测
    print(f"\n{'=' * 70}")
    print("🔮 价格预测")
    print(f"{'=' * 70}")
    
    prediction = predictor.predict(klines)
    
    print(f"\n📊 预测结果:")
    print(f"   信号：{prediction['prediction']}")
    print(f"   置信度：{prediction['confidence']:.1f}%")
    print(f"   概率：{prediction.get('probability', 0):.2%}")
    print(f"   模型：{prediction.get('model_type', 'Unknown')}")
    
    print(f"\n{'=' * 70}")
    print("✅ 完成！")
    print(f"{'=' * 70}")
