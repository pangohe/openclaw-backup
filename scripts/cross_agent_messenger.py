#!/usr/bin/env python3
# 跨 Agent 通信系统
import json

AGENTS = {
    'qqbot': {'name': '细佬', 'channel': 'qqbot'},
    'telebot': {'name': '叻仔', 'channel': 'telegram'},
    'feishu': {'name': 'Natalie', 'channel': 'feishu'}
}

def send_message(from_agent, to_agent, message, priority='normal'):
    sender = AGENTS[from_agent]['name']
    receiver = AGENTS[to_agent]['name']
    formatted_msg = f"【{sender} → {receiver}】{message}"
    print(f"发送: {formatted_msg}")
    return {'status': 'success', 'from': sender, 'to': receiver}

if __name__ == '__main__':
    send_message('telebot', 'qqbot', '套利系统API超时', 'urgent')
