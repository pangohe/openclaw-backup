# 🚀 Polymarket BTC 5 分钟量化交易系统

比特币 5 分钟涨跌预测 · 模拟交易 · 实盘准备

---

## 📋 项目结构

```
polymarket-btc-5min/
├── scripts/
│   ├── data_collector.py       # 数据收集器
│   ├── technical_analysis.py   # 技术分析模块
│   └── simulator.py            # 模拟交易系统
├── web_dashboard/
│   └── index.html              # 可视化界面 (适配折叠屏)
├── data/                       # 数据存储
│   ├── klines_*.json           # K 线数据
│   ├── simulation_results.json # 模拟结果
│   └── backtest_stats.json     # 回测统计
├── models/                     # 模型文件
├── config/                     # 配置文件
└── README.md                   # 本文件
```

---

## 🎯 系统特点

### 1. 实时数据收集
- ✅ Binance API 实时价格
- ✅ 5 分钟 K 线数据
- ✅ 自动保存历史数据

### 2. 技术分析
- ✅ RSI (相对强弱指标)
- ✅ MACD (移动平均收敛发散)
- ✅ 布林带 (Bollinger Bands)
- ✅ SMA/EMA 移动平均线

### 3. 交易信号
- ✅ 自动生成 BUY/SELL/HOLD 信号
- ✅ 置信度评分 (0-100%)
- ✅ 多指标组合判断

### 4. 模拟交易
- ✅ Polymarket 模拟下注
- ✅ 自动结算 (5 分钟周期)
- ✅ 胜率统计
- ✅ 盈亏追踪

### 5. 可视化界面
- ✅ 实时信号显示
- ✅ 资金曲线图表
- ✅ 交易记录列表
- ✅ 三星折叠屏适配

---

## 🚀 快速开始

### 步骤 1: 收集数据

```bash
cd /root/.openclaw/workspace/projects/polymarket-btc-5min/scripts

# 运行数据收集器
python3 data_collector.py

# 按提示选择是否持续收集
```

### 步骤 2: 技术分析

```bash
# 运行技术分析
python3 technical_analysis.py
```

### 步骤 3: 模拟交易回测

```bash
# 运行回测
python3 simulator.py
```

### 步骤 4: 查看可视化界面

```bash
# 启动简单 HTTP 服务器
cd /root/.openclaw/workspace/projects/polymarket-btc-5min/web_dashboard
python3 -m http.server 8080

# 浏览器访问
http://localhost:8080
```

---

## 📊 交易策略

### 信号生成逻辑

| 指标 | 条件 | 评分 |
|------|------|------|
| **RSI** | < 30 (超卖) | +2 |
| **RSI** | > 70 (超买) | -2 |
| **MACD** | 金叉 | +1 |
| **MACD** | 死叉 | -1 |
| **Histogram** | 向上动量 | +1 |
| **Histogram** | 向下动量 | -1 |
| **布林带** | 触及下轨 | +2 |
| **布林带** | 触及上轨 | -2 |

### 信号阈值

- **BUY**: 总分 ≥ 3，置信度 ≥ 60%
- **SELL**: 总分 ≤ -3，置信度 ≥ 60%
- **HOLD**: 其他情况

### 实盘标准

- ✅ 胜率 ≥ 75%
- ✅ 总交易数 ≥ 100
- ✅ ROI ≥ 20%

---

## 📈 模拟交易流程

```
1. 收集实时 BTC 价格数据
        ↓
2. 计算技术指标 (RSI, MACD, 布林带)
        ↓
3. 生成交易信号 (BUY/SELL/HOLD)
        ↓
4. 模拟 Polymarket 下注
        ↓
5. 5 分钟后结算
        ↓
6. 统计胜率 + 盈亏
        ↓
7. 胜率>75% → 准备实盘
```

---

## 🎨 可视化界面功能

### 主界面显示

- **实时 BTC 价格**
- **当前交易信号** (BUY/SELL/HOLD)
- **置信度进度条**
- **技术指标面板** (RSI, MACD, 布林带)

### 统计数据

- **胜率** (%)
- **总交易数**
- **总盈亏** (USD)
- **ROI** (%)
- **当前余额** (USD)

### 图表

- **胜率趋势图** (折线图)
- **资金曲线图** (折线图)

### 交易记录

- 最近 10 笔交易
- 盈亏颜色标记 (绿盈红亏)

---

## ⚙️ 配置选项

### 模拟交易参数

```python
# simulator.py
initial_balance = 1000.0    # 初始资金
bet_amount = 50.0           # 每笔下注金额
min_confidence = 60         # 最小置信度 (%)
```

### 数据收集参数

```python
# data_collector.py
interval = 10               # 收集间隔 (秒)
kline_limit = 100           # K 线数量
```

---

## 📁 数据文件说明

### klines_YYYYMMDD.json

```json
[
  {
    "timestamp": "2026-03-09T19:00:00",
    "open": 67650.00,
    "high": 67700.00,
    "low": 67600.00,
    "close": 67680.00,
    "volume": 123.45
  }
]
```

### simulation_results.json

```json
{
  "stats": {
    "total_trades": 50,
    "wins": 38,
    "losses": 12,
    "win_rate": 76.0,
    "total_profit": 234.50,
    "roi": 23.45
  },
  "trades": [...]
}
```

---

## 🎯 下一步计划

### 第一阶段 (已完成) ✅
- [x] 数据收集模块
- [x] 技术分析模块
- [x] 模拟交易系统
- [x] 可视化界面

### 第二阶段 (进行中) 🚧
- [ ] Polymarket API 集成
- [ ] 实盘交易模块
- [ ] 风险管理引擎
- [ ] 自动部署系统 (胜率>75%)

### 第三阶段 (计划) 📅
- [ ] 机器学习模型 (LSTM)
- [ ] 更多技术指标
- [ ] 移动端 APP
- [ ] 多市场支持

---

## ⚠️ 风险提示

1. **模拟交易 ≠ 实盘盈利**
   - 模拟环境无滑点、无手续费
   - 实盘需考虑市场冲击

2. **5 分钟超短期风险**
   - 波动大，预测难度高
   - 建议小资金测试

3. **Polymarket 平台风险**
   - 确认 API 可用性
   - 注意提现限制

4. **资金管理**
   - 单笔下注 ≤ 总资金 5%
   - 设置止损线

---

## 📞 技术支持

遇到问题？检查以下事项：

1. **数据收集失败** → 检查网络连接
2. **API 错误** → 确认 API Key 有效
3. **图表不显示** → 检查数据文件是否存在
4. **胜率低** → 优化策略参数

---

## 🏆 目标

**短期目标**: 模拟胜率 ≥ 75%  
**中期目标**: 实盘月收益 ≥ 30%  
**长期目标**: 稳定盈利系统

---

**加油大佬！小投入大盈利！💰🔥**

_最后更新：2026-03-09_
