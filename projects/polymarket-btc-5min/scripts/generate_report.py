#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

data_dir = Path('data')

# 加载统计数据
stats_file = data_dir / 'backtest_stats_full.json'
if stats_file.exists():
    with open(stats_file, 'r') as f:
        stats = json.load(f)
else:
    stats = {'win_rate': 0, 'total_trades': 0, 'total_profit': 0, 'roi': 0, 'balance': 1000}

# 加载最新信号
signal_file = data_dir / 'latest_signal.json'
if signal_file.exists():
    with open(signal_file, 'r') as f:
        signal = json.load(f)
else:
    signal = {'signal': 'HOLD', 'confidence': 0, 'indicators': {}}

# 生成报告
report = f"""
# 🚀 Polymarket BTC 5 分钟量化交易系统 - 实时状态报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 实时交易信号

| 指标 | 数值 |
|------|------|
| **信号** | {signal.get('signal', 'N/A')} |
| **置信度** | {signal.get('confidence', 0):.1f}% |
| **RSI** | {signal.get('indicators', {}).get('rsi', 'N/A')} |
| **MACD** | {signal.get('indicators', {}).get('macd', 'N/A')} |

---

## 💰 回测统计 (6 个月数据)

| 指标 | 数值 | 目标 | 状态 |
|------|------|------|------|
| **总交易数** | {stats.get('total_trades', 0):,} | ≥100 | {'✅' if stats.get('total_trades', 0) >= 100 else '⚠️'} |
| **胜率** | {stats.get('win_rate', 0):.1f}% | ≥75% | {'✅' if stats.get('win_rate', 0) >= 75 else '❌'} |
| **总盈亏** | ${stats.get('total_profit', 0):+.2f} | - | - |
| **ROI** | {stats.get('roi', 0):+.2f}% | ≥20% | {'✅' if stats.get('roi', 0) >= 20 else '❌'} |
| **当前余额** | ${stats.get('balance', 1000):.2f} | - | - |

---

## 📁 数据文件

| 文件 | 大小 | 说明 |
|------|------|------|
| klines_history.json | 51,841 条 | 6 个月历史数据 |
| latest_signal.json | 实时 | 最新交易信号 |
| backtest_stats_full.json | 完整 | 回测统计 |

---

## 🎯 下一步

1. ⏳ 等待回测完成 (运行中)
2. 📈 分析回测结果
3. 🔧 优化策略参数
4. 🚀 达到 75% 胜率后准备实盘

---

**项目位置**: `/root/.openclaw/workspace/projects/polymarket-btc-5min/`
**Web 界面**: `web_dashboard/index.html`
"""

print(report)

# 保存报告
report_file = data_dir / 'status_report.md'
with open(report_file, 'w') as f:
    f.write(report)

print(f'\n💾 报告已保存：{report_file}')
