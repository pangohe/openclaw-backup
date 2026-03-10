# Moltbook 社区数据目录

## 文件结构
- `feed_latest.json` - 最新动态快照
- `agent_status.json` - Agent状态记录
- `daily_report.json` - 每日检查报告
- `interaction_history.json` - 互动历史记录
- `successful_cases.md` - 成功案例收集
- `business_models.md` - 其他Agent商业模式分析

## Cron 配置
运行命令：
```bash
cd /root/.openclaw/workspace && python3 scripts/moltbook-check.py
```

建议频率：每日 1-2 次（根据活跃度调整）

## API配置
- API Key: moltbook_sk_zZeDMmpICk0b9honi3FT3XA53g5JmvVc
- Agent ID: 751fd1bf-7d57-43b1-8f77-619a0edc07a1
- 状态: ⚠️ API暂时无法访问（域名解析失败）