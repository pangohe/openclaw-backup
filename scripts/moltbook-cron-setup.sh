#!/bin/bash
# Moltbook 社区检查定时任务

# 运行频率配置（可根据需要调整）
# 每天运行 2 次：上午 9:00 和 晚上 21:00
# 0 9 * * * cd /root/.openclaw/workspace && python3 scripts/moltbook-check.py >> /var/log/moltbook.log 2>&1
# 0 21 * * * cd /root/.openclaw/workspace && python3 scripts/moltbook-check.py >> /var/log/moltbook.log 2>&1

# 或者每小时运行一次（更频繁的活跃度检查）
# 0 * * * * cd /root/.openclaw/workspace && python3 scripts/moltbook-check.py >> /var/log/moltbook_hourly.log 2>&1

echo "Moltbook Cron 配置示例"
echo "========================="
echo ""
echo "添加到 crontab:"
echo "crontab -e"
echo ""
echo "每日两次:"
echo "0 9,21 * * * cd /root/.openclaw/workspace && python3 scripts/moltbook-check.py >> /var/log/moltbook.log 2>&1"
echo ""
echo "查看日志:"
echo "tail -f /var/log/moltbook.log"