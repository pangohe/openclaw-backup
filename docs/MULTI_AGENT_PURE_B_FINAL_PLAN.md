# 🤖 多 Agent 纯方案 B - 最终实施版本

**版本**: V3.0 - 纯 B 增强版  
**创建时间**: 2026-03-09 16:43  
**核心**: 完全独立 + 跨 Agent 通信 + 数据迁移 + 维护策略

---

## 📋 一、用户需求确认

### 1.1 为什么选择纯方案 B？

**问题**: 混合方案经常聊天记录串来串去 ❌

**原因**:
- 共享 MEMORY.md 导致上下文混乱
- QQ 的对话出现在 Telegram
- Telegram 的对话出现在 Feishu
- 用户体验差

**解决**: 纯方案 B - 完全隔离 ✅

---

### 1.2 核心要求

1. ✅ **完全独立** - 每个 Agent 独立 SOUL + MEMORY + 配置
2. ✅ **跨 Agent 通信** - 需要明确协议，避免混乱
3. ✅ **数据迁移** - 保留现有聊天记录和记忆
4. ✅ **维护策略** - 明确单独修改 vs 全局修改

---

## 🏗️ 二、架构设计 (纯方案 B)

### 2.1 完全隔离的文件结构

```
/root/.openclaw/
│
├── workspace/                    # 基础工作区 (只读模板)
│   ├── SOUL.md.template          # 灵魂模板 (仅供参考)
│   ├── AGENTS.md.template        # 规则模板 (仅供参考)
│   └── scripts/                  # 共享脚本库
│       ├── cross_agent_protocol.py  ← 跨 Agent 通信协议
│       └── ...
│
└── agents/
    │
    ├── qqbot/                    # 🔥 细佬 - 系统管家
    │   ├── BOOTSTRAP.md          # 启动配置
    │   ├── SOUL.md               # ✅ 独立灵魂 (不共享)
    │   ├── MEMORY.md             # ✅ 独立记忆 (不共享)
    │   ├── AGENTS.md             # ✅ 独立规则 (不共享)
    │   ├── HEARTBEAT.md          # ✅ 独立心跳 (不共享)
    │   ├── TOOLS.md              # ✅ 独立工具笔记
    │   ├── agent/
    │   │   ├── models.json       # ✅ 独立模型配置
    │   │   └── auth-profiles.json # ✅ 独立认证
    │   ├── sessions/
    │   │   └── sessions.json     # ✅ 独立会话 (从 main 迁移)
    │   └── scripts/              # ✅ 独立脚本
    │       ├── token_watcher.py
    │       └── cron_manager.py
    │
    ├── telebot/                  # 💹 叻仔 - 投资顾问
    │   ├── BOOTSTRAP.md
    │   ├── SOUL.md               # ✅ 独立灵魂 (投资专家人格)
    │   ├── MEMORY.md             # ✅ 独立记忆 (从 main 迁移投资相关)
    │   ├── AGENTS.md
    │   ├── HEARTBEAT.md
    │   ├── TOOLS.md
    │   ├── agent/
    │   │   ├── models.json       # ✅ 独立模型 (GLM4.7)
    │   │   └── auth-profiles.json
    │   ├── sessions/
    │   │   └── sessions.json     # ✅ 独立会话 (从 main 迁移 Telegram)
    │   └── scripts/
    │       ├── crypto_collector.py
    │       └── polymarket_monitor.py
    │
    ├── feishu/                   # 📊 Natalie - 工作助理
    │   ├── BOOTSTRAP.md
    │   ├── SOUL.md               # ✅ 独立灵魂 (专业助理人格)
    │   ├── MEMORY.md             # ✅ 独立记忆 (从 main 迁移工作相关)
    │   ├── AGENTS.md
    │   ├── HEARTBEAT.md
    │   ├── TOOLS.md
    │   ├── agent/
    │   │   ├── models.json       # ✅ 独立模型 (qwen3.5-plus)
    │   │   └── auth-profiles.json
    │   ├── sessions/
    │   │   └── sessions.json     # ✅ 独立会话 (从 main 迁移 Feishu)
    │   └── scripts/
    │       └── doc_manager.py
    │
    ├── dashboard/                # 🚨 系统守护者
    │   ├── BOOTSTRAP.md
    │   ├── SOUL.md               # ✅ 独立灵魂 (守护者人格)
    │   ├── MEMORY.md             # ✅ 独立记忆 (新建)
    │   ├── AGENTS.md
    │   ├── HEARTBEAT.md
    │   ├── agent/
    │   │   ├── models.json       # ✅ 独立模型 (llama-3.3)
    │   │   └── auth-profiles.json
    │   └── sessions/
    │       └── sessions.json     # ✅ 独立会话 (新建)
    │
    ├── default/                  # 📰 默认 Agent
    │   ├── BOOTSTRAP.md
    │   ├── SOUL.md
    │   ├── MEMORY.md
    │   ├── agent/
    │   │   └── models.json
    │   └── sessions/
    │       └── sessions.json
    │
    └── main/                     # ⚙️ 主 Agent (备用/归档)
        ├── BOOTSTRAP.md          # ✅ 保留 (备份)
        ├── SOUL.md               # ✅ 保留 (备份)
        ├── MEMORY.md             # ✅ 保留 (备份)
        ├── agent/
        └── sessions/             # ✅ 保留 (归档，不再使用)
```

---

## 🔗 三、跨 Agent 通信协议 (重点)

### 3.1 设计原则

**核心**: **明确边界 + 标准格式 + 异步通信**

```
┌─────────────────────────────────────────────────────────┐
│                   跨 Agent 通信协议                       │
├─────────────────────────────────────────────────────────┤
│ 1. 明确发送方和接收方                                    │
│ 2. 标准化消息格式                                        │
│ 3. 异步通信 (不阻塞)                                     │
│ 4. 有确认机制                                            │
│ 5. 有超时处理                                            │
│ 6. 有错误处理                                            │
└─────────────────────────────────────────────────────────┘
```

---

### 3.2 消息格式标准

```json
{
  "protocol": "cross-agent-v1",
  "message_id": "uuid-xxx-xxx-xxx",
  "timestamp": "2026-03-09T16:43:00+08:00",
  "from": {
    "agent": "qqbot",
    "channel": "qqbot",
    "user_id": "C721984A868CC01CDBA58DC0F1D35627"
  },
  "to": {
    "agent": "telebot",
    "channel": "telegram"
  },
  "type": "request|response|notification|forward",
  "priority": "low|normal|high|urgent",
  "content": {
    "action": "analyze|save|query|notify|coordinate",
    "subject": "消息主题",
    "body": "消息内容",
    "context": {
      "original_message": "原始消息",
      "user_intent": "用户意图",
      "expected_response": "期望响应"
    }
  },
  "metadata": {
    "requires_response": true,
    "timeout_seconds": 30,
    "retry_count": 0,
    "max_retries": 3
  }
}
```

---

### 3.3 通信场景分类

#### 场景 1: 请求 - 响应模式

**示例**: QQ 用户问投资问题

```
┌──────────┐                      ┌──────────┐
│  qqbot   │                      │ telebot  │
│  (细佬)  │                      │  (叻仔)  │
└────┬─────┘                      └────┬─────┘
     │                                 │
     │  1. 收到 QQ 用户问题              │
     │  "比特币点样？"                 │
     │                                 │
     │  2. 判断：投资相关              │
     │     → 需要 telebot 处理           │
     │                                 │
     │──── sessions_send ─────────────▶│
     │  {                               │
     │    "type": "request",           │
     │    "action": "analyze",         │
     │    "subject": "BTC 价格分析",     │
     │    "body": "老板问比特币走势",   │
     │    "requires_response": true,   │
     │    "timeout_seconds": 30        │
     │  }                               │
     │                                 │
     │  3. 分析中...                   │
     │                                 │
     │◀──── sessions_send ─────────────│
     │  {                               │
     │    "type": "response",          │
     │    "in_reply_to": "uuid-xxx",   │
     │    "content": {                 │
     │      "analysis": "BTC +5.8%",   │
     │      "recommendation": "持有"   │
     │    }                             │
     │  }                               │
     │                                 │
     │  4. 转发给 QQ 用户                │
     │                                 │
```

**代码实现**:
```python
# qqbot 发送请求
def send_to_telebot(user_question):
    message = {
        "protocol": "cross-agent-v1",
        "message_id": generate_uuid(),
        "from": {"agent": "qqbot", "channel": "qqbot"},
        "to": {"agent": "telebot"},
        "type": "request",
        "action": "analyze",
        "subject": "BTC 价格分析",
        "body": f"老板问：{user_question}",
        "requires_response": True,
        "timeout_seconds": 30
    }
    
    # 发送到 telebot
    result = sessions_send(
        sessionKey="agent:telebot:main",
        message=json.dumps(message, ensure_ascii=False)
    )
    
    # 等待响应 (带超时)
    response = wait_for_response(
        message_id=message["message_id"],
        timeout=30
    )
    
    return response

# telebot 处理请求
def handle_request_from_qqbot(message):
    # 解析请求
    action = message["content"]["action"]
    subject = message["content"]["subject"]
    
    # 执行分析
    if action == "analyze":
        result = analyze_crypto(subject)
    
    # 发送响应
    response = {
        "protocol": "cross-agent-v1",
        "type": "response",
        "in_reply_to": message["message_id"],
        "content": {
            "analysis": result["analysis"],
            "recommendation": result["recommendation"]
        }
    }
    
    sessions_send(
        sessionKey="agent:qqbot:main",
        message=json.dumps(response, ensure_ascii=False)
    )
```

---

#### 场景 2: 通知模式 (无需响应)

**示例**: Dashboard 发现 Token 超限，通知 qqbot

```
┌───────────┐                      ┌──────────┐
│ dashboard │                      │  qqbot   │
│ (守护者)  │                      │  (细佬)  │
└─────┬─────┘                      └────┬─────┘
      │                                 │
      │  1. 监控发现 qqbot Token 75%     │
      │     → 超过阈值 (70%)             │
      │                                 │
      │──── sessions_send ─────────────▶│
      │  {                               │
      │    "type": "notification",      │
      │    "priority": "high",          │
      │    "content": {                 │
      │      "alert_type": "token_limit",│
      │      "agent": "qqbot",          │
      │      "current": "75%",          │
      │      "threshold": "70%",        │
      │      "action_required": True    │
      │    }                             │
      │  }                               │
      │                                 │
      │  2. 收到通知                    │
      │     → 立即压缩会话              │
      │                                 │
      │  3. (可选) 发送确认             │
      │◀──── sessions_send ─────────────│
      │  {                               │
      │    "type": "response",          │
      │    "in_reply_to": "uuid-xxx",   │
      │    "content": {                 │
      │      "status": "handled",       │
      │      "action": "compressed"     │
      │    }                             │
      │  }                               │
      │                                 │
```

---

#### 场景 3: 转发模式

**示例**: Telegram 用户要保存文档，转发给 feishu

```
┌──────────┐                      ┌──────────┐
│ telebot  │                      │  feishu  │
│  (叻仔)  │                      │ (Natalie)│
└────┬─────┘                      └────┬─────┘
     │                                 │
     │  1. 收到 Telegram 用户请求        │
     │  "帮我保存呢个文档"             │
     │                                 │
     │  2. 判断：文档相关              │
     │     → 需要 feishu 处理            │
     │                                 │
     │──── sessions_send ─────────────▶│
     │  {                               │
     │    "type": "forward",           │
     │    "priority": "normal",        │
     │    "content": {                 │
     │      "original_channel": "tg",  │
     │      "original_user": "8571...",│
     │      "action": "save_doc",      │
     │      "document": {...}          │
     │    }                             │
     │  }                               │
     │                                 │
     │  3. 保存文档                    │
     │                                 │
     │◀──── sessions_send ─────────────│
     │  {                               │
     │    "type": "response",          │
     │    "content": {                 │
     │      "status": "success",       │
     │      "doc_url": "https://..."   │
     │    }                             │
     │  }                               │
     │                                 │
     │  4. 转发结果给 Telegram 用户       │
     │                                 │
```

---

### 3.4 通信协议实现脚本

**文件**: `/root/.openclaw/workspace/scripts/cross_agent_protocol.py`

```python
#!/usr/bin/env python3
"""
跨 Agent 通信协议实现
版本：v1.0
功能：标准化跨 Agent 消息传递
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import time

class CrossAgentProtocol:
    """跨 Agent 通信协议"""
    
    PROTOCOL_VERSION = "cross-agent-v1"
    TIMEOUT_DEFAULT = 30  # 秒
    MAX_RETRIES = 3
    
    def __init__(self, current_agent: str):
        self.current_agent = current_agent
        self.pending_requests = {}  # 等待响应的请求
    
    def generate_message_id(self) -> str:
        """生成唯一消息 ID"""
        return f"{self.current_agent}-{uuid.uuid4().hex[:12]}"
    
    def create_request(
        self,
        to_agent: str,
        action: str,
        subject: str,
        body: str,
        requires_response: bool = True,
        timeout_seconds: int = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """创建请求消息"""
        message_id = self.generate_message_id()
        
        message = {
            "protocol": self.PROTOCOL_VERSION,
            "message_id": message_id,
            "timestamp": datetime.now().isoformat(),
            "from": {
                "agent": self.current_agent
            },
            "to": {
                "agent": to_agent
            },
            "type": "request",
            "priority": priority,
            "content": {
                "action": action,
                "subject": subject,
                "body": body
            },
            "metadata": {
                "requires_response": requires_response,
                "timeout_seconds": timeout_seconds or self.TIMEOUT_DEFAULT,
                "retry_count": 0,
                "max_retries": self.MAX_RETRIES
            }
        }
        
        # 记录等待响应
        if requires_response:
            self.pending_requests[message_id] = {
                "created_at": time.time(),
                "timeout": timeout_seconds or self.TIMEOUT_DEFAULT,
                "to_agent": to_agent,
                "response": None
            }
        
        return message
    
    def create_response(
        self,
        in_reply_to: str,
        content: Dict[str, Any],
        status: str = "success"
    ) -> Dict[str, Any]:
        """创建响应消息"""
        return {
            "protocol": self.PROTOCOL_VERSION,
            "message_id": self.generate_message_id(),
            "timestamp": datetime.now().isoformat(),
            "from": {
                "agent": self.current_agent
            },
            "type": "response",
            "in_reply_to": in_reply_to,
            "content": {
                "status": status,
                **content
            }
        }
    
    def create_notification(
        self,
        to_agent: str,
        alert_type: str,
        content: Dict[str, Any],
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """创建通知消息"""
        return {
            "protocol": self.PROTOCOL_VERSION,
            "message_id": self.generate_message_id(),
            "timestamp": datetime.now().isoformat(),
            "from": {
                "agent": self.current_agent
            },
            "to": {
                "agent": to_agent
            },
            "type": "notification",
            "priority": priority,
            "content": {
                "alert_type": alert_type,
                **content
            }
        }
    
    def send_message(
        self,
        target_agent: str,
        message: Dict[str, Any]
    ) -> bool:
        """发送消息到目标 Agent"""
        try:
            # 使用 sessions_send 发送
            from sessions_send import sessions_send
            
            session_key = f"agent:{target_agent}:main"
            message_json = json.dumps(message, ensure_ascii=False)
            
            result = sessions_send(
                sessionKey=session_key,
                message=message_json
            )
            
            return True
        except Exception as e:
            print(f"❌ 发送消息失败：{e}")
            return False
    
    def wait_for_response(
        self,
        message_id: str,
        timeout: int = None
    ) -> Optional[Dict[str, Any]]:
        """等待响应 (带超时)"""
        if message_id not in self.pending_requests:
            return None
        
        request = self.pending_requests[message_id]
        timeout = timeout or request["timeout"]
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if request["response"]:
                # 收到响应
                del self.pending_requests[message_id]
                return request["response"]
            time.sleep(0.5)
        
        # 超时
        del self.pending_requests[message_id]
        raise TimeoutError(f"等待响应超时：{message_id}")
    
    def receive_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """接收并处理消息"""
        message_type = message.get("type")
        
        if message_type == "request":
            return self.handle_request(message)
        elif message_type == "response":
            return self.handle_response(message)
        elif message_type == "notification":
            return self.handle_notification(message)
        else:
            raise ValueError(f"未知消息类型：{message_type}")
    
    def handle_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求 (子类实现)"""
        raise NotImplementedError
    
    def handle_response(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理响应"""
        in_reply_to = message.get("in_reply_to")
        if in_reply_to in self.pending_requests:
            self.pending_requests[in_reply_to]["response"] = message
        return {"status": "received"}
    
    def handle_notification(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理通知 (子类实现)"""
        raise NotImplementedError


# ==================== 各 Agent 实现 ====================

class QQBotHandler(CrossAgentProtocol):
    """qqbot (细佬) 的消息处理"""
    
    def __init__(self):
        super().__init__("qqbot")
    
    def handle_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message["content"]["action"]
        
        if action == "analyze":
            # 转发给 telebot
            return self.forward_to_telebot(message)
        elif action == "save_doc":
            # 转发给 feishu
            return self.forward_to_feishu(message)
        else:
            return {"status": "error", "message": "未知操作"}
    
    def handle_notification(self, message: Dict[str, Any]) -> Dict[str, Any]:
        alert_type = message["content"]["alert_type"]
        
        if alert_type == "token_limit":
            # Token 超限，立即压缩
            self.compress_session()
            return {"status": "handled", "action": "compressed"}
        elif alert_type == "system_error":
            # 系统错误，通知用户
            self.notify_user(message["content"])
            return {"status": "handled", "action": "notified"}
        else:
            return {"status": "ignored"}
    
    def forward_to_telebot(self, message: Dict[str, Any]):
        """转发给 telebot"""
        # 实现转发逻辑
        pass
    
    def forward_to_feishu(self, message: Dict[str, Any]):
        """转发给 feishu"""
        # 实现转发逻辑
        pass
    
    def compress_session(self):
        """压缩会话"""
        # 实现压缩逻辑
        pass
    
    def notify_user(self, content: Dict[str, Any]):
        """通知用户"""
        # 实现通知逻辑
        pass


class TelebotHandler(CrossAgentProtocol):
    """telebot (叻仔) 的消息处理"""
    
    def __init__(self):
        super().__init__("telebot")
    
    def handle_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message["content"]["action"]
        
        if action == "analyze":
            # 分析加密货币
            result = self.analyze_crypto(message["content"]["subject"])
            return self.create_response(
                in_reply_to=message["message_id"],
                content=result
            )
        elif action == "market_alert":
            # 市场警报
            self.check_market_alert(message["content"])
            return {"status": "handled"}
        else:
            return {"status": "error", "message": "未知操作"}
    
    def handle_notification(self, message: Dict[str, Any]) -> Dict[str, Any]:
        alert_type = message["content"]["alert_type"]
        
        if alert_type == "price_change":
            # 价格变化通知
            self.process_price_alert(message["content"])
            return {"status": "handled"}
        else:
            return {"status": "ignored"}
    
    def analyze_crypto(self, subject: str) -> Dict[str, Any]:
        """分析加密货币"""
        # 实现分析逻辑
        return {
            "analysis": "BTC +5.8%",
            "recommendation": "持有"
        }
    
    def check_market_alert(self, content: Dict[str, Any]):
        """检查市场警报"""
        # 实现警报检查逻辑
        pass
    
    def process_price_alert(self, content: Dict[str, Any]):
        """处理价格警报"""
        # 实现处理逻辑
        pass


class FeishuHandler(CrossAgentProtocol):
    """feishu (Natalie) 的消息处理"""
    
    def __init__(self):
        super().__init__("feishu")
    
    def handle_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message["content"]["action"]
        
        if action == "save_doc":
            # 保存文档
            doc_url = self.save_document(message["content"]["document"])
            return self.create_response(
                in_reply_to=message["message_id"],
                content={"doc_url": doc_url}
            )
        elif action == "query_doc":
            # 查询文档
            result = self.query_document(message["content"]["query"])
            return self.create_response(
                in_reply_to=message["message_id"],
                content=result
            )
        else:
            return {"status": "error", "message": "未知操作"}
    
    def handle_notification(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # feishu 通常不处理通知
        return {"status": "ignored"}
    
    def save_document(self, document: Dict[str, Any]) -> str:
        """保存文档"""
        # 实现保存逻辑
        return "https://feishu.cn/docx/xxx"
    
    def query_document(self, query: str) -> Dict[str, Any]:
        """查询文档"""
        # 实现查询逻辑
        return {"results": []}


class DashboardHandler(CrossAgentProtocol):
    """dashboard (守护者) 的消息处理"""
    
    def __init__(self):
        super().__init__("dashboard")
    
    def handle_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # dashboard 通常不处理请求
        return {"status": "ignored"}
    
    def handle_notification(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # dashboard 发送通知，不接收
        return {"status": "ignored"}
    
    def monitor_all_agents(self):
        """监控所有 Agent"""
        # 实现监控逻辑
        # 发现异常时发送通知
        pass


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # qqbot 发送请求给 telebot
    qqbot = QQBotHandler()
    
    request = qqbot.create_request(
        to_agent="telebot",
        action="analyze",
        subject="BTC 价格",
        body="老板问比特币走势",
        requires_response=True,
        timeout_seconds=30
    )
    
    # 发送
    qqbot.send_message("telebot", request)
    
    # 等待响应
    try:
        response = qqbot.wait_for_response(request["message_id"])
        print(f"收到响应：{response}")
    except TimeoutError as e:
        print(f"超时：{e}")
```

---

## 📦 四、数据迁移方案

### 4.1 迁移原则

1. **保留所有历史** - 不删除任何聊天记录
2. **按通道分离** - QQ/Telegram/Feishu 分开
3. **保持上下文** - 保留重要记忆
4. **可回滚** - 保留备份

---

### 4.2 迁移脚本

**文件**: `/root/.openclaw/workspace/scripts/migrate_to_multi_agent.py`

```python
#!/usr/bin/env python3
"""
多 Agent 数据迁移脚本
功能：将 main agent 的会话迁移到各专用 agent
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

# 配置
MAIN_SESSIONS_DIR = Path("/root/.openclaw/agents/main/sessions")
TARGET_AGENTS = {
    "qqbot": {
        "channel_keywords": ["qqbot", "c2c", "C721984A868CC01CDBA58DC0F1D35627"],
        "memory_keywords": ["系统", "管理", "提醒", "cron"],
        "target_dir": Path("/root/.openclaw/agents/qqbot/sessions")
    },
    "telebot": {
        "channel_keywords": ["telegram", "8571370259", "LeslieHeHeBot"],
        "memory_keywords": ["投资", "加密货币", "BTC", "ETH", "市场"],
        "target_dir": Path("/root/.openclaw/agents/telebot/sessions")
    },
    "feishu": {
        "channel_keywords": ["feishu", "fly", "bitable", "docx"],
        "memory_keywords": ["文档", "知识库", "表格", "飞书"],
        "target_dir": Path("/root/.openclaw/agents/feishu/sessions")
    }
}

def load_main_sessions():
    """加载 main agent 的所有会话"""
    sessions = []
    for session_file in MAIN_SESSIONS_DIR.glob("*.jsonl"):
        with open(session_file, 'r', encoding='utf-8') as f:
            messages = [json.loads(line) for line in f]
            sessions.append({
                "file": session_file.name,
                "messages": messages,
                "size": len(messages)
            })
    return sessions

def classify_session(session):
    """分类会话到对应 agent"""
    messages = session["messages"]
    
    # 合并所有消息内容
    all_text = ""
    for msg in messages:
        if 'content' in msg:
            all_text += str(msg['content']).lower()
    
    # 根据关键词分类
    for agent, config in TARGET_AGENTS.items():
        for keyword in config["channel_keywords"]:
            if keyword.lower() in all_text:
                return agent
    
    # 无法分类的归入 main (备用)
    return "main"

def migrate_sessions():
    """执行迁移"""
    print("📦 开始迁移会话...")
    
    # 加载所有会话
    sessions = load_main_sessions()
    print(f"找到 {len(sessions)} 个会话")
    
    # 分类和迁移
    stats = {agent: 0 for agent in TARGET_AGENTS}
    stats["main"] = 0
    
    for session in sessions:
        target_agent = classify_session(session)
        
        if target_agent == "main":
            # 保留在 main (归档)
            stats["main"] += 1
            continue
        
        # 复制到目标 agent
        target_dir = TARGET_AGENTS[target_agent]["target_dir"]
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_file = target_dir / session["file"]
        shutil.copy2(
            MAIN_SESSIONS_DIR / session["file"],
            target_file
        )
        
        stats[target_agent] += 1
        print(f"  ✅ {session['file']} → {target_agent}")
    
    # 输出统计
    print("\n📊 迁移统计:")
    for agent, count in stats.items():
        print(f"  {agent}: {count} 个会话")
    
    return stats

def migrate_memory():
    """迁移记忆"""
    print("\n📝 开始迁移记忆...")
    
    main_memory = Path("/root/.openclaw/workspace/MEMORY.md")
    
    if not main_memory.exists():
        print("  ⚠️  MEMORY.md 不存在")
        return
    
    # 读取主记忆
    with open(main_memory, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 为每个 agent 创建独立记忆
    for agent, config in TARGET_AGENTS.items():
        target_file = Path(f"/root/.openclaw/agents/{agent}/MEMORY.md")
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 过滤相关记忆 (简单实现：复制全部，后续手动清理)
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(f"# {agent} 的独立记忆\n\n")
            f.write(f"## 迁移时间：{datetime.now()}\n\n")
            f.write(f"## 原始记忆 (从 main 迁移)\n\n")
            f.write(content)
        
        print(f"  ✅ {agent}/MEMORY.md")
    
    # 备份原始记忆
    backup_file = Path("/root/.openclaw/workspace/MEMORY.md.bak.pre-multi-agent")
    shutil.copy2(main_memory, backup_file)
    print(f"  ✅ 备份：{backup_file}")

def migrate_soul():
    """迁移灵魂配置"""
    print("\n🎭 开始迁移灵魂配置...")
    
    main_soul = Path("/root/.openclaw/workspace/SOUL.md")
    
    if not main_soul.exists():
        print("  ⚠️  SOUL.md 不存在")
        return
    
    # 为每个 agent 创建独立 SOUL
    soul_templates = {
        "qqbot": "细佬 - 系统管家",
        "telebot": "叻仔 - 投资顾问",
        "feishu": "Natalie - 工作助理",
        "dashboard": "守护者 - 系统监控"
    }
    
    for agent, role in soul_templates.items():
        target_file = Path(f"/root/.openclaw/agents/{agent}/SOUL.md")
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(f"# SOUL.md - {role}\n\n")
            f.write(f"## 创建时间：{datetime.now()}\n\n")
            f.write(f"## 说明\n\n")
            f.write(f"这是 {agent} ({role}) 的独立灵魂配置。\n\n")
            f.write(f"## 原始 SOUL.md (参考)\n\n")
            with open(main_soul, 'r', encoding='utf-8') as original:
                f.write(original.read())
        
        print(f"  ✅ {agent}/SOUL.md")
    
    # 备份原始 SOUL
    backup_file = Path("/root/.openclaw/workspace/SOUL.md.bak.pre-multi-agent")
    shutil.copy2(main_soul, backup_file)
    print(f"  ✅ 备份：{backup_file}")

if __name__ == "__main__":
    print("="*60)
    print("多 Agent 数据迁移脚本")
    print("="*60)
    
    # 1. 迁移会话
    session_stats = migrate_sessions()
    
    # 2. 迁移记忆
    migrate_memory()
    
    # 3. 迁移灵魂配置
    migrate_soul()
    
    print("\n" + "="*60)
    print("✅ 迁移完成！")
    print("="*60)
    print("\n下一步:")
    print("1. 检查各 agent 的会话是否正确")
    print("2. 编辑各 agent 的 SOUL.md (个性化)")
    print("3. 编辑各 agent 的 MEMORY.md (清理不相关内容)")
    print("4. 修改 openclaw.json (绑定通道到 agent)")
    print("5. 重启 Gateway: openclaw gateway restart")
```

---

### 4.3 执行迁移

```bash
# 1. 备份当前配置
cp -r /root/.openclaw/agents/main \
      /root/.openclaw/agents/main.bak.pre-migration

# 2. 运行迁移脚本
python3 /root/.openclaw/workspace/scripts/migrate_to_multi_agent.py

# 3. 验证迁移结果
ls -la /root/.openclaw/agents/qqbot/sessions/
ls -la /root/.openclaw/agents/telebot/sessions/
ls -la /root/.openclaw/agents/feishu/sessions/

# 4. 检查记忆文件
cat /root/.openclaw/agents/qqbot/MEMORY.md | head -20
cat /root/.openclaw/agents/telebot/MEMORY.md | head -20
cat /root/.openclaw/agents/feishu/MEMORY.md | head -20
```

---

## 🔧 五、维护策略

### 5.1 修改类型分类

| 修改类型 | 范围 | 示例 | 操作方式 |
|---------|------|------|---------|
| **全局修改** | 所有 Agent | 安全配置、工具策略、通道绑定 | 修改 openclaw.json |
| **单独修改** | 单个 Agent | SOUL.md、MEMORY.md、HEARTBEAT.md | 修改对应 agent 文件 |
| **模板修改** | 未来 Agent | 基础规则、默认配置 | 修改 workspace 模板 |
| **共享脚本** | 所有 Agent | 跨 Agent 协议、通用工具 | 修改 workspace/scripts |

---

### 5.2 全局修改 (需要修改 openclaw.json)

**场景**:
- 添加新通道
- 修改工具权限
- 修改模型配置
- 修改安全策略

**操作方式**:
```bash
# 1. 备份配置
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak

# 2. 编辑配置
vim ~/.openclaw/openclaw.json

# 3. 验证 JSON 格式
python3 -m json.tool ~/.openclaw/openclaw.json > /dev/null

# 4. 重启 Gateway
openclaw gateway restart
```

**影响范围**: 所有 Agent

---

### 5.3 单独修改 (只影响单个 Agent)

**场景**:
- 修改某个 Agent 的人格 (SOUL.md)
- 修改某个 Agent 的记忆 (MEMORY.md)
- 修改某个 Agent 的心跳任务 (HEARTBEAT.md)
- 添加某个 Agent 的专用脚本

**操作方式**:
```bash
# 示例：修改 qqbot 的 SOUL.md
vim /root/.openclaw/agents/qqbot/SOUL.md

# 示例：修改 telebot 的 MEMORY.md
vim /root/.openclaw/agents/telebot/MEMORY.md

# 示例：添加 feishu 的专用脚本
vim /root/.openclaw/agents/feishu/scripts/doc_manager.py
```

**影响范围**: 仅该 Agent

---

### 5.4 维护责任矩阵

| 任务 | 负责人 | 频率 | 方式 |
|------|--------|------|------|
| 系统安全更新 | 细佬 (qqbot) | 每周 | 全局修改 |
| Token 监控 | 细佬 (qqbot) | 每 5 分钟 | 自动 |
| 投资分析 | 叻仔 (telebot) | 实时 | 自动 |
| 文档管理 | Natalie (feishu) | 按需 | 单独修改 |
| 系统监控 | Dashboard | 持续 | 自动 |
| 跨 Agent 协调 | 细佬 (qqbot) | 按需 | 跨 Agent 通信 |
| 配置备份 | Dashboard | 每周 | 自动 |

---

### 5.5 修改流程

```
用户提出修改需求
       │
       ▼
┌─────────────────┐
│ 判断修改类型     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
全局修改    单独修改
    │         │
    ▼         ▼
修改        修改
openclaw.json  对应 agent 文件
    │         │
    ▼         ▼
重启        无需重启
Gateway     (可选重载)
    │
    ▼
验证效果
```

---

### 5.6 版本控制 (推荐)

```bash
# 创建 git 仓库
cd /root/.openclaw
git init

# 添加重要文件
git add agents/qqbot/SOUL.md
git add agents/telebot/SOUL.md
git add agents/feishu/SOUL.md
git add openclaw.json
git add workspace/scripts/

# 提交变更
git commit -m "多 Agent 架构部署"

# 每次修改后提交
git add -A
git commit -m "修改 qqbot SOUL - 添加新职责"
```

---

## 📋 六、实施步骤

### 步骤 1: 创建目录结构 (5 分钟)

```bash
# 创建各 agent 目录
mkdir -p /root/.openclaw/agents/{qqbot,telebot,feishu,dashboard,default}/\
{agent,sessions,scripts,memory}

# 复制模型配置
for agent in qqbot telebot feishu dashboard default; do
    cp /root/.openclaw/agents/main/agent/models.json \
       /root/.openclaw/agents/$agent/agent/
    cp /root/.openclaw/agents/main/agent/auth-profiles.json \
       /root/.openclaw/agents/$agent/agent/
done
```

### 步骤 2: 创建跨 Agent 通信协议 (10 分钟)

```bash
# 创建协议脚本
cp /root/.openclaw/workspace/scripts/cross_agent_protocol.py \
   /root/.openclaw/agents/qqbot/scripts/
cp /root/.openclaw/workspace/scripts/cross_agent_protocol.py \
   /root/.openclaw/agents/telebot/scripts/
cp /root/.openclaw/workspace/scripts/cross_agent_protocol.py \
   /root/.openclaw/agents/feishu/scripts/
cp /root/.openclaw/workspace/scripts/cross_agent_protocol.py \
   /root/.openclaw/agents/dashboard/scripts/
```

### 步骤 3: 执行数据迁移 (15 分钟)

```bash
# 运行迁移脚本
python3 /root/.openclaw/workspace/scripts/migrate_to_multi_agent.py

# 验证迁移结果
echo "QQ Bot 会话数：$(ls /root/.openclaw/agents/qqbot/sessions/*.jsonl 2>/dev/null | wc -l)"
echo "Telegram 会话数：$(ls /root/.openclaw/agents/telebot/sessions/*.jsonl 2>/dev/null | wc -l)"
echo "Feishu 会话数：$(ls /root/.openclaw/agents/feishu/sessions/*.jsonl 2>/dev/null | wc -l)"
```

### 步骤 4: 创建独立 SOUL.md (15 分钟)

为每个 agent 创建独立的 SOUL.md (参考第二节的内容)

### 步骤 5: 修改 openclaw.json (10 分钟)

添加通道绑定和 agent 配置 (参考之前的方案)

### 步骤 6: 验证配置 (5 分钟)

```bash
# 验证 JSON 格式
python3 -m json.tool /root/.openclaw/openclaw.json > /dev/null && echo "✅ JSON 格式正确"

# 检查必需配置
cat /root/.openclaw/openclaw.json | python3 -c "
import sys, json
c = json.load(sys.stdin)
print('通道绑定:')
for ch, cfg in c.get('channels', {}).items():
    print(f'  {ch}: {cfg.get(\"agentId\", \"未绑定\")}')
"
```

### 步骤 7: 重启 Gateway (1 分钟)

```bash
openclaw gateway restart
```

### 步骤 8: 验证运行 (10 分钟)

```bash
# 检查各 agent 状态
openclaw status --all | grep -A10 "Agents"

# 测试 QQ Bot
# 发送消息测试 qqbot

# 测试 Telegram
# 发送消息测试 telebot

# 测试 Feishu
# 发送消息测试 feishu

# 测试跨 Agent 通信
# QQ 问投资问题 → 应该转发给 telebot
```

**总耗时**: ~71 分钟

---

## ✅ 七、验收标准

### 7.1 独立性验收

- [ ] 每个 agent 有独立 SOUL.md ✅
- [ ] 每个 agent 有独立 MEMORY.md ✅
- [ ] 每个 agent 有独立会话目录 ✅
- [ ] 每个 agent 有独立 HEARTBEAT.md ✅
- [ ] 聊天记录不再串来串去 ✅

### 7.2 通信验收

- [ ] qqbot 可以发送请求给 telebot ✅
- [ ] telebot 可以响应 qqbot ✅
- [ ] dashboard 可以发送通知 ✅
- [ ] 跨 agent 通信延迟 < 2 秒 ✅
- [ ] 超时处理正常 ✅

### 7.3 数据验收

- [ ] QQ 会话已迁移到 qqbot ✅
- [ ] Telegram 会话已迁移到 telebot ✅
- [ ] Feishu 会话已迁移到 feishu ✅
- [ ] 主会话已备份 (main.bak) ✅
- [ ] 记忆文件已迁移 ✅

### 7.4 功能验收

- [ ] QQ Bot 正常工作 ✅
- [ ] Telegram 正常工作 ✅
- [ ] Feishu 正常工作 ✅
- [ ] Cron 任务正常执行 ✅
- [ ] Token Watcher 正常监控 ✅

---

## 📊 八、预期效果

### 8.1 隔离效果

```
QQ 用户聊天:
  → qqbot 处理
  → 记录到 qqbot/MEMORY.md
  → ❌ 不会出现在 Telegram
  → ❌ 不会出现在 Feishu

Telegram 用户聊天:
  → telebot 处理
  → 记录到 telebot/MEMORY.md
  → ❌ 不会出现在 QQ
  → ❌ 不会出现在 Feishu

Feishu 用户聊天:
  → feishu 处理
  → 记录到 feishu/MEMORY.md
  → ❌ 不会出现在 QQ
  → ❌ 不会出现在 Telegram
```

### 8.2 协作效果

```
QQ 用户问："比特币点样？"

1. qqbot 收到 → 判断：投资相关
2. qqbot → telebot (跨 Agent 请求)
   {
     "type": "request",
     "action": "analyze",
     "subject": "BTC 价格"
   }
3. telebot 分析 → 返回结果
4. qqbot → 回复 QQ 用户

结果:
✅ QQ 用户得到答案
✅ 聊天记录只在 qqbot
✅ telebot 知道老板关心 BTC (记录到 telebot/MEMORY.md)
✅ 不会串频道
```

---

## 🎯 九、总结

### 核心改进

1. ✅ **完全独立** - 每个 Agent 独立 SOUL + MEMORY
2. ✅ **跨 Agent 通信** - 标准化协议，避免混乱
3. ✅ **数据迁移** - 保留所有历史聊天记录
4. ✅ **维护策略** - 明确全局 vs 单独修改

### 解决的问题

| 问题 | 解决方案 |
|------|---------|
| 聊天记录串来串去 | 完全独立 MEMORY.md |
| 人格混乱 | 独立 SOUL.md |
| 跨 Agent 协作困难 | 标准化通信协议 |
| 数据丢失风险 | 完整迁移 + 备份 |
| 维护责任不清 | 明确维护矩阵 |

---

**方案已优化完成！你确认 OK 后，我即刻开工实施！** 🔥

---

**文档位置**: `/root/.openclaw/workspace/docs/MULTI_AGENT_PURE_B_FINAL_PLAN.md`  
**文件大小**: ~25KB  
**最后更新**: 2026-03-09 16:43
