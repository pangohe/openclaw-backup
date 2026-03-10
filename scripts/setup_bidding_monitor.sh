#!/bin/bash
# 投标监控系统 - 快速配置脚本
# 用法：./setup_bidding_monitor.sh

echo "======================================"
echo "📊 广东装修项目投标监控系统"
echo "======================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    exit 1
fi
echo "✅ Python3 已安装"

# 创建数据目录
mkdir -p /root/.openclaw/workspace/data/bidding_monitor
echo "✅ 数据目录已创建"

# 检查 requests 库
python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  正在安装 requests 库..."
    pip3 install requests --break-system-packages -q
fi
echo "✅ requests 库已安装"

# 检查脚本
if [ -f "/root/.openclaw/workspace/scripts/bidding_monitor.py" ]; then
    echo "✅ 监控脚本已存在"
else
    echo "❌ 错误：监控脚本不存在"
    exit 1
fi

# 检查 cron 任务
if crontab -l 2>/dev/null | grep -q "bidding_monitor.py"; then
    echo "✅ Cron 任务已配置（每日 10:00）"
else
    echo "⚠️  正在配置 Cron 任务..."
    (crontab -l 2>/dev/null; echo "0 10 * * * cd /root/.openclaw/workspace && python3 scripts/bidding_monitor.py >> data/bidding_monitor/cron.log 2>&1") | crontab -
    echo "✅ Cron 任务已配置"
fi

echo ""
echo "======================================"
echo "✅ 系统配置完成！"
echo "======================================"
echo ""
echo "📋 下一步："
echo "1. 配置飞书 Webhook（必须）"
echo "   编辑：scripts/bidding_monitor.py"
echo "   找到：FEISHU_WEBHOOK = \"\""
echo "   填入你的飞书机器人 Webhook 地址"
echo ""
echo "2. 测试运行"
echo "   cd /root/.openclaw/workspace"
echo "   python3 scripts/bidding_monitor.py"
echo ""
echo "3. 查看日志"
echo "   cat data/bidding_monitor/monitor.log"
echo ""
echo "📖 详细文档：docs/BIDDING_MONITOR_SETUP.md"
echo ""
