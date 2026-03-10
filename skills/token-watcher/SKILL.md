# Token Watcher - Token 使用量监控

监控 OpenClaw 的 token 使用情况，防止因缓存过大导致聊天卡顿。

## 快速开始

```bash
# 手动检查当前状态
~/.openclaw/workspace/skills/token-watcher/token_monitor.sh

# 或者使用快捷命令
token-check
```

## 自动监控

已配置 cron 定时任务，每 30 分钟自动检查一次：

```bash
# 查看定时任务
crontab -l | grep token

# 手动运行测试
~/.openclaw/workspace/skills/token-watcher/token_monitor.sh
```

## 阈值说明

| 级别 | Completions 大小 | 建议操作 |
|------|------------------|----------|
| 🟢 正常 | < 50MB | 无需操作 |
| 🟡 警告 | 50-80MB | 建议开启新会话 |
| 🔴 严重 | > 80MB | **立即清理或重启** |

## 清理方法

当达到警告阈值时，执行以下任一操作：

1. **开启新会话** (推荐)
   ```
   /reset
   # 或
   /new
   ```

2. **清理缓存文件**
   ```bash
   rm ~/.openclaw/completions/*.json
   ```

3. **重启 Gateway**
   ```bash
   openclaw gateway restart
   ```

## 状态文件

监控数据保存在：
- 最新状态：`~/.openclaw/workspace/memory/token-state.json`
- 历史日志：`~/.openclaw/logs/token-monitor.log`

## 模型 Context Window 参考

| 模型 | Context Window |
|------|----------------|
| kimi-k2.5 | 262k |
| qwen3.5-plus | 1000k |
| GLM4.7 (NVIDIA) | 128k |
| MiniMax M2.1 (NVIDIA) | 256k |

## Heartbeat 集成

HEARTBEAT.md 中已添加检查任务，每次心跳时会自动运行监控。
