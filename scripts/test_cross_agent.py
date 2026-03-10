#!/usr/bin/env python3
"""测试跨 Agent 通信（含 Dashboard）"""

def test_communication():
    """所有 agents 测试通信"""
    
    scenarios = [
        ("Dashboard", "qqbot", "系统检查完成，一切正常"),
        ("telebot", "qqbot", "套利系统API超时，需要检查"),
        ("qqbot", "feishu", "系统升级完成，更新文档"),
        ("feishu", "telebot", "有新的投资机会"),
        ("telebot", "Dashboard", "发现异常，需要紧急处理"),
        ("qqbot", "Dashboard", "Token 超限警告"),
        ("Dashboard", "telegram", "系统故障，立即响应"),
        ("feishu", "qqbot", "工作进度更新"),
        ("qqbot", "telebot", "系统修复完成"),
        ("Dashboard", "feishu", "本周报告已生成")
    ]
    
    print("📮 跨 Agent 通信测试")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    for i, (from_agent, to_agent, message) in enumerate(scenarios, 1):
        print(f"{i}. 【{from_agent.upper().replace('QQBOT','细佬').replace('TELEBOT','叻仔').replace('FEISHU','Natalie').replace('DASHBOARD','🚨')} → {to_agent.upper().replace('QQBOT','细佬').replace('TELEBOT','叻仔').replace('FEISHU','Natalie').replace('DASHBOARD','🚨')}】 {message}")
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ 测试完成：{len(scenarios)} 个场景")

if __name__ == "__main__":
    test_communication()
