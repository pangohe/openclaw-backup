# 🤖 飞书机器人配置指引

## 3 分钟搞定飞书推送

### 步骤 1：创建飞书机器人

1. 打开飞书，进入你想接收通知的群聊（或者创建一个只有你自己的群）

2. 点击右上角「···」或「设置」图标

3. 选择「添加机器人」

4. 选择「自定义机器人」

5. 填写信息：
   - **名称**：投标监控助手
   - **头像**：随便选一个
   - **发送消息**：✅ 开启
   - **获取机器人所在群信息**：✅ 开启

6. 点击「添加」

---

### 步骤 2：复制 Webhook 地址

添加成功后，你会看到：

```
Webhook 地址：
https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

点击「复制」按钮 📋

---

### 步骤 3：配置到脚本

**方法 A：直接编辑**
```bash
nano /root/.openclaw/workspace/scripts/bidding_monitor.py
```

找到第 19 行：
```python
FEISHU_WEBHOOK = ""  # 从飞书机器人获取
```

改成：
```python
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/你的 webhook 地址"
```

保存：`Ctrl+O` → `Enter` → `Ctrl+X`

**方法 B：用命令替换**
```bash
# 把 YOUR_WEBHOOK_HERE 替换成你的实际地址
sed -i 's|FEISHU_WEBHOOK = ""|FEISHU_WEBHOOK = "YOUR_WEBHOOK_HERE"|' /root/.openclaw/workspace/scripts/bidding_monitor.py
```

---

### 步骤 4：测试推送

```bash
cd /root/.openclaw/workspace
python3 scripts/bidding_monitor.py
```

如果配置正确，你会在飞书收到消息：

```
🔔 装修投标项目提醒 - 2026-03-10

今日新增：3 个项目 | 总预算：¥300.0 万
...
```

---

## ❓ 常见问题

### Q1: 收不到消息？
**检查**：
- Webhook 地址是否正确复制（完整 URL）
- 机器人是否在群聊中
- 脚本是否报错（查看日志）

### Q2: 报错 "Webhook invalid"？
**解决**：
- 重新复制 Webhook 地址
- 确认没有多余空格
- 确认以 `https://open.feishu.cn/open-apis/bot/v2/hook/` 开头

### Q3: 想在私人对话接收？
**方法**：
1. 飞书 → 创建群聊
2. 只拉你自己进群
3. 在群里添加机器人
4. 这样只有你能看到消息

---

## 🔐 安全提示

- ⚠️ Webhook 地址相当于密码，不要公开分享
- ⚠️ 如果泄露，可以在飞书删除机器人重新创建
- ✅ 机器人只能发送消息到你配置的群聊

---

需要帮助？随时揾大佬 AI！🔥
