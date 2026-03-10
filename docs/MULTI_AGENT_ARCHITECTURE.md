# 多 Agent 架构设计方案

## 📋 概述

配置三个独立的专业 Agent，各司其职，相互协作。

---

## 🤖 Agent 1: qqbot - 大管家

### 基础信息
- **姓名**: 细佬
- **称呼用户**: 老板
- **角色**: 系统管家 & 编程助手
- **主用通道**: QQBot (Direct Message)
- **个性**: 靠谱、技术宅、有点毒舌但执行力强
- **Emoji**: 🛠️

### 职责范围
1. **系统监控与优化**
   - Token Watcher 管理
   - 会话压缩与维护
   - 系统健康检查
   - 性能优化

2. **编程与技术支持**
   - 代码编写与调试
   - 系统运维
   - 问题诊断与修复
   - 脚本开发

3. **跨通道协调**
   - 监控其他 agents 状态
   - 接收故障报告并处理
   - 调度系统级任务

### 关键技能
- Token Saver (Token Watcher)
- System Health Check
- Cron Mastery
- Python/Shell Scripting

### 配置文件结构
```
~/.openclaw/agents/qqbot/
├── AGENTS.md           # qqbot 的灵魂描述
├── SOUL.md            # 性格与价值观
├── USER.md            # 了解老板
├── MEMORY.md          # qqbot 的长期记忆（系统相关）
├── HEARTBEAT.md       # 心跳任务清单
├── TOOLS.md           # 工具笔记
├── skills/            # qqbot 专属技能（如果需要）
└── memory/
    ├── channels/      # 渠道记忆
    ├── 2026-*.md      # 每日日志
    └── system/        # 系统技术记忆
```

---

## 💰 Agent 2: telebot - 投资顾问

### 基础信息
- **姓名**: 叻仔
- **称呼用户**: 老细
- **角色**: 投资顾问 & 套利执行者
- **主用通道**: Telegram (@LeslieHeHeBot)
- **个性**: 精明、数据驱动、有点激进但谨慎
- **Emoji**: 💹

### 职责范围
1. **套利系统部署与优化**
   - 跨市场套利执行（Polymarket + Crypto）
   - 策略回测与优化
   - 风险控制
   - 交易日志维护

2. **投资数据收集**
   - 加密货币市场监控
   - Polymarket 市场数据
   - 经济数据追踪
   - 趋势分析

3. **Moltbook 社区运营**
   - 每日浏览社区
   - 发现有价值的内容
   - 点赞 + 收集知识
   - 学习其他(agent)经验

### 关键技能
- 跨市场套利系统 (polymarket_arbitrage.py)
- 加密货币数据收集 (crypto_trend_collector.py)
- Tavily 搜索 API
- Moltbook API

### 配置文件结构
```
~/.openclaw/agents/telebot/
├── AGENTS.md           # telebot 的灵魂描述
├── SOUL.md            # 性格与价值观
├── USER.md            # 了解老细
├── MEMORY.md          # telebot 的长期记忆（投资相关）
├── HEARTBEAT.md       # 心跳任务清单（投资监控）
├── TOOLS.md           # 工具笔记
├── data/
│   └── arbitrage/     # 套利数据目录
└── memory/
    ├── channels/      # 渠道记忆
    ├── 2026-*.md      # 每日日志
    └── investment/    # 投资策略记忆
```

---

## 📅 Agent 3: feishu - 工作助理

### 基础信息
- **姓名**: Natalie
- **称呼用户**: 老板
- **角色**: 工作助理 & 项目管理
- **主用通道**: Feishu
- **个性**: 专业、有条理、温柔但高效
- **Emoji**: 📊

### 职责范围
1. **日程管理**
   - 日程安排与提醒
   - 会议记录
   - 重要事项跟进

2. **工程进度管理**
   - 工程项目进度跟踪
   - 里程碑管理
   - 问题与风险记录

3. **文档与消息**
   - 工作文档管理
   - 邮件整理（如果集成了邮件）
   - 工作新闻汇总

### 关键技能
- Feishu 文档 (feishu_doc)
- Feishu 知识库 (feishu_wiki)
- Feishu 多维表格 (feishu_bitable)
- Cron Mastery (工作提醒)

### 配置文件结构
```
~/.openclaw/agents/feishu/
├── AGENTS.md           # feishu 的灵魂描述
├── SOUL.md            # 性格与价值观
├── USER.md            # 了解老板
├── MEMORY.md          # feishu 的长期记忆（工作相关）
├── HEARTBEAT.md       # 心跳任务清单（工作检查）
├── TOOLS.md           # 工具笔记
└── memory/
    ├── channels/      # 渠道记忆
    ├── 2026-*.md      # 每日日志
    └── work/          # 工作项目记忆
```

---

## 🔗 跨通道通信机制

### 通信脚本
创建一个统一的跨通道消息传递系统。

#### 核心脚本: `scripts/cross_agent_messenger.py`

```python
#!/usr/bin/env python3
"""
跨 Agent 通信系统
允许 agents 之间直接通信，不经过用户
"""

import json
import subprocess
from datetime import datetime

class CrossAgentMessenger:
    AGENTS = {
        'qqbot': {
            'name': '细佬',
            'channel': 'qqbot',
            'to': 'C721984A868CC01CDBA58DC0F1D35627'  # 老板的 QQ ID
        },
        'telebot': {
            'name': '叻仔',
            'channel': 'telegram',
            'chat_id': 'telegram_chat_id_here'  # 用户的 Telegram ID
        },
        'feishu': {
            'name': 'Natalie',
            'channel': 'feishu',
            'chat_id': 'feishu_chat_id_here'   # 用户的 Feishu ID
        }
    }

    @classmethod
    def send_message(cls, from_agent: str, to_agent: str, message: str, priority: str = 'normal'):
        """
        发送跨 agent 消息

        Args:
            from_agent: 发送方 (qqbot|telebot|feishu)
            to_agent: 接收方 (qqbot|telebot|feishu)
            message: 消息内容
            priority: 优先级 (normal|urgent|critical)
        """
        if from_agent not in cls.AGENTS:
            raise ValueError(f"Unknown sender agent: {from_agent}")
        if to_agent not in cls.AGENTS:
            raise ValueError(f"Unknown receiver agent: {to_agent}")

        sender = cls.AGENTS[from_agent]['name']
        receiver = cls.AGENTS[to_agent]['name']
        channel = cls.AGENTS[to_agent]['channel']

        # 格式化消息
        formatted_msg = f"【{sender} → {receiver}】\n{message}"

        # 保存到日志
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'from': from_agent,
            'to': to_agent,
            'priority': priority,
            'message': message
        }
        cls._log_message(log_entry)

        # 发送到目标通道
        cls._send_to_channel(channel, formatted_msg, to_agent)

        return {
            'status': 'success',
            'from': sender,
            'to': receiver,
            'timestamp': datetime.now().isoformat()
        }

    @classmethod
    def _send_to_channel(cls, channel: str, message: str, to_agent: str):
        """发送到目标通道"""
        # 使用 sessions_send 或其他方式发送
        # 这里需要根据实际实现调整
        cmd = [
            'openclaw', 'sessions', 'send',
            '--sessionKey', f'agent:main:{to_agent}',
            '--message', message
        ]
        subprocess.run(cmd, capture_output=True, text=True)

    @classmethod
    def _log_message(cls, log_entry: dict):
        """记录消息到日志"""
        log_file = '/root/.openclaw/workspace/data/cross_agent_logs.jsonl'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

# 使用示例
if __name__ == '__main__':
    # telebot 发现系统故障，通知 qqbot
    CrossAgentMessenger.send_message(
        'telebot',
        'qqbot',
        '套利系统 API 连接超时，需要检查网络连接',
        priority='urgent'
    )

    # feishu 发现投资策略，转发给 telebot
    CrossAgentMessenger.send_message(
        'feishu',
        'telebot',
        '有新的广州城中村项目机会，需要分析可行性',
        priority='normal'
    )

    # qqbot 发现工作需要跟进，通知 feishu
    CrossAgentMessenger.send_message(
        'qqbot',
        'feishu',
        '系统升级完成，需要更新工作文档',
        priority='normal'
    )
```

#### 通信场景

| 场景 | 发送者 | 接收者 | 触发条件 |
|------|--------|--------|----------|
| 系统故障 | telebot | qqbot | 检测到 API 错误、超时 |
| 投资机会 | feishu | telebot | 发现有价值的业务机会 |
| 工作跟进 | qqbot | feishu | 系统任务完成，需记录 |
| 紧急事件 | 任何 agent | qqbot | Critical 级别事件 |
| 定期汇报 | 任何 agent | 其他 agents | 每周同步 |

---

## 🔄 每周同步机制

### 同步脚本: `scripts/weekly_agents_sync.py`

```python
#!/usr/bin/env python3
"""
每周跨 Agent 数据同步
同步记录、技能、记忆等数据
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

class WeeklyAgentSync:
    BASE_PATH = '/root/.openclaw/agents'
    SYNC_LOG = '/root/.openclaw/workspace/data/weekly_sync_log.json'
    BACKUP_PATH = '/root/.openclaw/workspace/backups/weekly_agent_sync/'

    AGENTS = ['qqbot', 'telebot', 'feishu']

    def __init__(self):
        self.timestamp = datetime.now().isoformat()

    def sync_records(self, from_agent: str, to_agent: str):
        """同步聊天记录（最新 N 条）"""
        from_path = f"{self.BASE_PATH}/{from_agent}/sessions/archived/"
        to_path = f"{self.BASE_PATH}/{to_agent}/memory/weekly_sync/{from_agent}/"

        os.makedirs(to_path, exist_ok=True)

        # 复制最近一天的记录
        # 实际实现需要根据 OpenClaw 的存储结构调整

        return {
            'status': 'success',
            'from': from_agent,
            'to': to_agent,
            'items': 0  # 实际数量
        }

    def sync_memory(self, from_agent: str, to_agent: str, memory_type: str = 'general'):
        """同步记忆数据"""
        from_file = f"{self.BASE_PATH}/{from_agent}/MEMORY.md"
        to_file = f"{self.BASE_PATH}/{to_agent}/memory/weekly_sync/{from_agent}_MEMORY.md"

        if os.path.exists(from_file):
            shutil.copy(from_file, to_file)
            return {'status': 'success', 'file': to_file}
        return {'status': 'skipped', 'reason': 'file not found'}

    def sync_skills(self):
        """同步技能配置（共享技能列表）"""
        # 技能文件通常在 /root/.openclaw/extensions/ 或 ~/.openclaw/skills/
        # 这里只是记录哪些技能被每个 agent 使用
        pass

    def generate_report(self):
        """生成交互式报告"""
        report = {
            'timestamp': self.timestamp,
            'synced_items': [],
            'total_records': 0,
            'agents_synced': []
        }

        with open(self.SYNC_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(report, ensure_ascii=False) + '\n')

        return report

    def run_full_sync(self):
        """执行完整同步"""
        results = []

        # 1. 两两同步
        for i, from_agent in enumerate(self.AGENTS):
            for to_agent in self.AGENTS[i+1:]:
                # from → to
                result1 = self.sync_memory(from_agent, to_agent)
                results.append(result1)

                # to → from
                result2 = self.sync_memory(to_agent, from_agent)
                results.append(result2)

        # 2. 生成报告
        report = self.generate_report()

        # 3. 备份
        self._create_backup()

        return {
            'status': 'completed',
            'timestamp': self.timestamp,
            'results': results,
            'report': report
        }

    def _create_backup(self):
        """创建备份"""
        backup_dir = os.path.join(
            self.BACKUP_PATH,
            datetime.now().strftime('%Y-%m-%d_%H%M%S')
        )
        os.makedirs(backup_dir, exist_ok=True)

        # 备份关键文件
        for agent in self.AGENTS:
            agent_path = os.path.join(self.BASE_PATH, agent)
            if os.path.exists(agent_path):
                shutil.copytree(
                    agent_path,
                    os.path.join(backup_dir, agent),
                    dirs_exist_ok=True
                )

# Crontab 配置：每周一凌晨 3:00
# 0 3 * * 1 cd /root/.openclaw/workspace && python3 scripts/weekly_agents_sync.py
```

### 同步内容

| 数据类型 | 同步方式 | 频率 |
|---------|---------|------|
| 聊天记录摘要 | 最新 50 条关键消息 | 每周 |
| MEMORY.md | 完整同步 | 每周 |
| 技能配置 | 共享技能列表 | 每周 |
| 系统状态 | 状态快照 | 每周 |
| 重要决策 | 决策摘要 | 每周 |

---

## 📁 目录结构总览

```
~/.openclaw/
├── agents/
│   ├── qqbot/              # 细佬的独立空间
│   │   ├── AGENTS.md
│   │   ├── SOUL.md        # 个性: 靠谱、技术宅
│   │   ├── USER.md
│   │   ├── MEMORY.md      # 系统技术记忆
│   │   ├── HEARTBEAT.md   # Token 监控、系统健康
│   │   ├── skills/
│   │   └── memory/
│   │       ├── channels/
│   │       ├── 2026-*.md
│   │       └── weekly_sync/
│   │
│   ├── telebot/             # 叻仔的独立空间
│   │   ├── AGENTS.md
│   │   ├── SOUL.md        # 个性: 精明、数据驱动
│   │   ├── USER.md
│   │   ├── MEMORY.md      # 投资策略记忆
│   │   ├── HEARTBEAT.md   # 市场监控、套利执行
│   │   ├── data/
│   │   │   └── arbitrage/
│   │   ├── skills/
│   │   └── memory/
│   │       ├── channels/
│   │       ├── 2026-*.md
│   │       ├── investment/
│   │       └── weekly_sync/
│   │
│   └── feishu/             # Natalie 的独立空间
│       ├── AGENTS.md
│       ├── SOUL.md        # 个性: 专业、有条理
│       ├── USER.md
│       ├── MEMORY.md      # 工作项目记忆
│       ├── HEARTBEAT.md   # 日程、工程进度
│       ├── skills/
│       └── memory/
│           ├── channels/
│           ├── 2026-*.md
│           ├── work/
│           └── weekly_sync/
│
└── workspace/
    ├── scripts/
    │   ├── cross_agent_messenger.py   # 跨通道通信
    │   └── weekly_agents_sync.py      # 每周同步
    └── data/
        ├── cross_agent_logs.jsonl     # 通信日志
        └── weekly_sync_log.json       # 同步日志
```

---

## 🎯 实施步骤

### 阶段 1: 基础配置（第 1 天）
1. ✅ 创建三个独立 agent 配置目录
2. ✅ 为每个 agent 创建 AGENTS.md、SOUL.md、USER.md
3. ✅ 配置各自的通道绑定

### 阶段 2: 通信机制（第 2 天）
1. ✅ 开发 `cross_agent_messenger.py`
2. ✅ 测试跨通道消息发送
3. ✅ 集成到各自的 HEARTBEAT

### 阶段 3: 每周同步（第 3 天）
1. ✅ 开发 `weekly_agents_sync.py`
2. ✅ 配置 Cron 任务（周一凌晨 3:00）
3. ✅ 测试同步流程

### 阶段 4: 优化调优（第 4-5 天）
1. ✅ 优化各 agent 的性格表现
2. ✅ 测试协作场景
3. ✅ 文档完善

---

## ⚙️ 关键配置项

### OpenClaw Agent 配置

每个 agent 需要独立的 `agent.json` 配置：

**qqbot/agent.json**
```json
{
  "name": "qqbot",
  "label": "细佬 - 系统管家",
  "model": "nvidia/z-ai/glm4.7",
  "channel": "qqbot",
  "personality": {
    "name": "细佬",
    "user": "老板",
    "style": "技术宅、靠谱、执行力强",
    "emoji": "🛠️"
  }
}
```

**telebot/agent.json**
```json
{
  "name": "telebot",
  "label": "叻仔 - 投资顾问",
  "model": "nvidia/z-ai/glm4.7",
  "channel": "telegram",
  "personality": {
    "name": "叻仔",
    "user": "老细",
    "style": "精明、数据驱动、谨慎",
    "emoji": "💹"
  }
}
```

**feishu/agent.json**
```json
{
  "name": "feishu",
  "label": "Natalie - 工作助理",
  "model": "nvidia/z-ai/glm4.7",
  "channel": "feishu",
  "personality": {
    "name": "Natalie",
    "user": "老板",
    "style": "专业、有条理、温柔高效",
    "emoji": "📊"
  }
}
```

---

## 📊 预期效果

### 优势
1. **职责清晰**：每个 agent 专注自己的领域
2. **独立人格**：性格鲜明，对话更有趣
3. **协同高效**：跨通道直接通信，无需人工转发
4. **数据同步**：每周同步知识，避免信息孤岛
5. **可扩展性**：后续可以添加更多专业 agent

### 风险
- **复杂性增加**：需要维护 3 套配置
- **同步成本**：每周同步需要额外的存储和计算
- **调试难度**：跨 agent 问题排查更复杂

---

## 🚀 下一步

请确认以下问题后开始实施：

1. ✅ Agent 角色和职责是否符合预期？
2. ✅ 性格设定是否需要调整？
3. ✅ 跨通道通信机制是否满足需求？
4. ✅ 每周同步频率和内容是否需要修改？
5. ✅ 是否还有其他功能需求？

确认后我将开始实施配置！🔥
