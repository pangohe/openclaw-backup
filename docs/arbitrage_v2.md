# 🚀 跨交易所套利系统 v1.0

**独立系统 B** - 完全独立于比特币预测系统

---

## 📋 系统概述

**定位**：跨交易所价差套利

**特点**：
- ✅ 完全独立架构
- ✅ 不与其他系统混用
- ✅ 专注跨交易所套利
- ✅ 支持多交易所

**目标**：
- 🎯 胜率：>60%
- 💰 月收益：5-15%
- 📊 最大回撤：<20%
- ⚡ 交易频率：每日 5-20 次

---

## 🏗️ 系统架构

```
跨交易所套利系统
├── scripts/arbitrage_v2/
│   ├── data_collector.py    # 数据收集
│   ├── spread_detector.py   # 价差检测
│   └── backtest_engine.py   # 回测引擎
├── config/arbitrage_v2.json # 配置文件
├── data/arbitrage_v2/       # 数据目录
│   ├── prices_*.json        # 价格数据
│   ├── signals/             # 交易信号
│   └── backtest/            # 回测报告
└── docs/arbitrage_v2.md     # 文档
```

---

## 🔧 功能模块

### 1. 数据收集器 (data_collector.py)

**功能**：
- 从多个交易所获取实时价格
- 支持的交易所：Binance、OKX、Bybit
- 监控币种：BTC、ETH、SOL 等 10 个主流币
- 收集频率：每分钟 1 次

**使用方法**：
```bash
# 单次测试
python3 scripts/arbitrage_v2/data_collector.py

# 连续收集（每分钟）
python3 scripts/arbitrage_v2/data_collector.py --continuous 1
```

**输出**：
- `data/arbitrage_v2/prices_YYYYMMDD_HHMMSS.json`
- `data/arbitrage_v2/latest_prices.json`

---

### 2. 价差检测器 (spread_detector.py)

**功能**：
- 计算跨交易所价差
- 考虑交易成本（手续费、滑点、提现费）
- 检测套利机会
- 生成交易信号

**套利逻辑**：
```
1. 发现交易所 A 价格 < 交易所 B 价格
2. 计算价差：(B - A) / A * 100%
3. 扣除成本：手续费 + 滑点 + 提现费
4. 净利润 > 0 → 生成套利信号
```

**使用方法**：
```bash
python3 scripts/arbitrage_v2/spread_detector.py
```

**输出**：
- `data/arbitrage_v2/signals/signals_YYYYMMDD_HHMMSS.json`
- `data/arbitrage_v2/signals/latest_signals.json`

---

### 3. 回测引擎 (backtest_engine.py)

**功能**：
- 加载历史价格数据
- 模拟套利交易
- 计算收益率和风险指标
- 生成详细回测报告

**使用方法**：
```bash
python3 scripts/arbitrage_v2/backtest_engine.py
```

**输出**：
- `data/arbitrage_v2/backtest/backtest_report_YYYYMMDD_HHMMSS.md`
- `data/arbitrage_v2/backtest/backtest_data_YYYYMMDD_HHMMSS.json`

---

## 📊 交易策略

### 跨交易所套利

**原理**：
- 同一币种在不同交易所存在价差
- 低价买入，高价卖出
- 赚取价差利润

**示例**：
```
BTC 价格：
- Binance: $67,000
- OKX: $67,200
- 价差：$200 (0.298%)

操作：
1. Binance 买入 1 BTC @ $67,000
2. OKX 卖出 1 BTC @ $67,200
3. 毛利：$200
4. 扣除成本（手续费 + 滑点）：~$134
5. 净利润：~$66 (0.098%)
```

**成本结构**：
- 交易费：0.1%（买入）+ 0.1%（卖出）
- 滑点：0.1%
- 提现费：0.05%（如需跨交易所转账）
- 总成本：约 0.25-0.35%

**盈利条件**：
- 价差 > 0.3% 才考虑
- 目标价差：0.5%+
- 净利润率：0.1%+

---

## ⚙️ 配置参数

### 交易配置 (config/arbitrage_v2.json)

```json
{
  "trading": {
    "initial_capital_usdt": 10000,  // 初始资金
    "position_size_usdt": 100,      // 每次仓位
    "max_position_pct": 0.5,        // 最大仓位比例
    "max_daily_trades": 20          // 每日最大交易
  },
  
  "arbitrage": {
    "min_spread_pct": 0.3,          // 最小价差
    "target_spread_pct": 0.5,       // 目标价差
    "trading_fee_rate": 0.001,      // 交易费率
    "slippage_pct": 0.001           // 滑点
  },
  
  "risk_control": {
    "stop_loss_pct": 0.5,           // 止损
    "max_drawdown_pct": 20,         // 最大回撤
    "daily_loss_limit_usdt": 500    // 每日亏损限额
  }
}
```

---

## 📈 开发计划

### Week 1-2：基础搭建 ✅
- [x] 数据收集模块
- [x] 价差检测模块
- [x] 基础回测框架
- [ ] API 密钥配置（实盘用）

### Week 3-4：策略开发
- [ ] 优化价差检测算法
- [ ] 添加更多交易所
- [ ] 支持更多币种
- [ ] 实时信号推送

### Week 5-6：模拟交易
- [ ] 模拟交易执行
- [ ] 性能监控
- [ ] 日志系统
- [ ] 回测优化

### Week 7-8：风控系统
- [ ] 实时风险监控
- [ ] 自动止损
- [ ] 仓位管理
- [ ] 异常处理

### Week 9-12：实盘测试
- [ ] 小额实盘（$100/次）
- [ ] 性能优化
- [ ] 稳定性测试
- [ ] 文档完善

---

## 🎯 关键指标

### 胜率目标
- **保守**：55-60%
- **中性**：60-70%
- **乐观**：70%+

### 收益目标
- **月收益**：5-15%
- **年化**：60-180%
- **夏普比率**：>1.5

### 风险控制
- **最大回撤**：<20%
- **单笔亏损**：<1%
- **每日亏损**：<5%

---

## 📝 使用流程

### 1. 数据收集（持续运行）
```bash
# 后台运行数据收集
python3 scripts/arbitrage_v2/data_collector.py --continuous 1
```

### 2. 检测机会（每分钟）
```bash
# 检测套利机会
python3 scripts/arbitrage_v2/spread_detector.py
```

### 3. 回测验证（定期）
```bash
# 运行回测
python3 scripts/arbitrage_v2/backtest_engine.py
```

### 4. 查看报告
```bash
# 查看最新回测报告
cat data/arbitrage_v2/backtest/backtest_report_*.md
```

---

## ⚠️ 风险提示

1. **交易所风险**：交易所可能宕机、限制提现
2. **执行风险**：价格快速变动导致套利失败
3. **流动性风险**：大额交易可能影响价格
4. **技术风险**：API 限制、网络延迟
5. **监管风险**：政策变化可能影响交易

**建议**：
- 从小额开始测试
- 严格止损
- 分散多个交易所
- 持续监控系统

---

## 📞 支持

**问题反馈**：查看日志文件
- `data/arbitrage_v2/*.log`

**性能优化**：调整配置参数
- `config/arbitrage_v2.json`

**实盘部署**：联系管理员配置 API 密钥

---

_最后更新：2026-03-09_
