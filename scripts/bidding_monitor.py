#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广东装修项目投标监控系统
功能：自动抓取政府投标网站，筛选装修项目（50-150 万），推送到飞书
作者：大佬 AI
版本：1.0
"""

import json
import hashlib
import requests
from datetime import datetime, timedelta
from pathlib import Path
import time
import re

# ==================== 配置区域 ====================

# 飞书 Webhook URL（需要用户配置）
FEISHU_WEBHOOK = ""  # 从飞书机器人获取

# 监控关键词
KEYWORDS = ['装修', '装饰', '改造', '修缮', '翻新', '室内工程', '建筑装修', '幕墙']

# 预算范围（元）
BUDGET_MIN = 500000  # 50 万
BUDGET_MAX = 1500000  # 150 万

# 地区关键词
REGIONS = ['广东', '广州', '深圳', '佛山', '东莞', '珠海', '中山', '惠州', '肇庆', '江门', '汕头', '湛江']

# 数据存储路径
DATA_DIR = Path('/root/.openclaw/workspace/data/bidding_monitor')
HISTORY_FILE = DATA_DIR / 'history.json'
LOG_FILE = DATA_DIR / 'monitor.log'

# 主要监控网站
WEBSITES = [
    {
        'name': '广东省政府采购网',
        'url': 'https://gdgp.czt.gd.gov.cn/',
        'search_url': 'https://gdgp.czt.gd.gov.cn/search/searchList',
        'enabled': True
    },
    {
        'name': '广州市公共资源交易中心',
        'url': 'https://www.gzggzy.cn/',
        'search_url': 'https://www.gzggzy.cn/jyxx/search',
        'enabled': True
    },
    {
        'name': '深圳公共资源交易中心',
        'url': 'https://www.szggzy.com/',
        'search_url': 'https://www.szggzy.com/jyxx/search',
        'enabled': True
    },
    {
        'name': '中国政府采购网',
        'url': 'http://www.ccgp.gov.cn/',
        'search_url': 'http://www.ccgp.gov.cn/search/search',
        'enabled': True
    }
]

# ==================== 工具函数 ====================

def log_message(message):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    # 写入日志文件
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    except Exception as e:
        print(f"日志写入失败：{e}")

def load_history():
    """加载历史记录"""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {'projects': [], 'last_check': None}

def save_history(history):
    """保存历史记录"""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_message(f"保存历史失败：{e}")

def generate_project_id(project):
    """生成项目唯一 ID"""
    text = f"{project['title']}{project['budget']}{project['date']}"
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def extract_budget(text):
    """从文本中提取预算金额"""
    if not text:
        return None
    
    # 匹配万元
    match = re.search(r'(\d+(?:\.\d+)?)\s*万元', text)
    if match:
        return float(match.group(1)) * 10000
    
    # 匹配元
    match = re.search(r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*元', text)
    if match:
        return float(match.group(1).replace(',', ''))
    
    # 匹配数字
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    if match:
        num = float(match.group(1))
        # 如果是小数，可能是万元
        if num < 1000:
            return num * 10000
        return num
    
    return None

def is_relevant_project(title, description=''):
    """判断项目是否相关"""
    text = title + ' ' + description
    
    # 检查关键词
    has_keyword = any(kw in text for kw in KEYWORDS)
    
    # 检查地区
    has_region = any(region in text for region in REGIONS)
    
    return has_keyword and has_region

# ==================== 爬虫函数 ====================

def fetch_gdgp_projects():
    """抓取广东省政府采购网项目"""
    projects = []
    log_message("开始抓取广东省政府采购网...")
    
    try:
        # 模拟搜索请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
        }
        
        # 注意：实际使用时需要根据网站 API 调整
        # 这里提供框架，具体实现需要分析网站结构
        log_message("广东省政府采购网 - 需要配置具体 API")
        
    except Exception as e:
        log_message(f"广东省政府采购网抓取失败：{e}")
    
    return projects

def fetch_gzggzy_projects():
    """抓取广州市公共资源交易中心项目"""
    projects = []
    log_message("开始抓取广州市公共资源交易中心...")
    
    try:
        # 类似上面的实现
        log_message("广州市公共资源交易中心 - 需要配置具体 API")
        
    except Exception as e:
        log_message(f"广州市公共资源交易中心抓取失败：{e}")
    
    return projects

# ==================== 模拟数据（测试用） ====================

def get_mock_projects():
    """获取模拟项目数据（用于测试）"""
    return [
        {
            'title': '广州市某单位办公室装修工程',
            'budget': 850000,
            'budget_text': '85 万元',
            'region': '广州',
            'date': '2026-03-09',
            'deadline': '2026-03-25',
            'url': 'https://gdgp.czt.gd.gov.cn/project/123',
            'website': '广东省政府采购网',
            'description': '办公室室内装修，包括吊顶、地面、墙面等'
        },
        {
            'title': '深圳市某学校教室改造修缮项目',
            'budget': 1200000,
            'budget_text': '120 万元',
            'region': '深圳',
            'date': '2026-03-09',
            'deadline': '2026-03-28',
            'url': 'https://www.szggzy.com/project/456',
            'website': '深圳公共资源交易中心',
            'description': '教室装修改造，含电路改造、墙面翻新'
        },
        {
            'title': '佛山市某医院室内装饰工程',
            'budget': 950000,
            'budget_text': '95 万元',
            'region': '佛山',
            'date': '2026-03-08',
            'deadline': '2026-03-22',
            'url': 'https://www.fsggzy.cn/project/789',
            'website': '佛山公共资源交易中心',
            'description': '医院室内装饰装修工程'
        }
    ]

# ==================== 筛选函数 ====================

def filter_projects(projects):
    """筛选符合条件的项目"""
    filtered = []
    
    for project in projects:
        # 检查预算
        budget = project.get('budget')
        if not budget:
            budget = extract_budget(project.get('budget_text', ''))
        
        if not budget or budget < BUDGET_MIN or budget > BUDGET_MAX:
            continue
        
        # 检查相关性
        if not is_relevant_project(project.get('title', ''), project.get('description', '')):
            continue
        
        # 添加预算信息
        project['budget'] = budget
        project['budget_text'] = f"¥{budget/10000:.1f}万"
        
        filtered.append(project)
        log_message(f"筛选到项目：{project['title']} ({project['budget_text']})")
    
    return filtered

# ==================== 飞书推送 ====================

def send_to_feishu(projects):
    """发送项目到飞书"""
    if not FEISHU_WEBHOOK:
        log_message("⚠️ 飞书 Webhook 未配置，跳过推送")
        print("\n=== 飞书 Webhook 配置指引 ===")
        print("1. 打开飞书 → 群聊 → 添加机器人")
        print("2. 选择「自定义机器人」")
        print("3. 复制 Webhook 地址")
        print("4. 填入脚本中的 FEISHU_WEBHOOK 变量")
        print("=" * 30)
        return False
    
    if not projects:
        log_message("今日无符合条件的新项目")
        return True
    
    # 构建飞书消息卡片
    cards = []
    
    # 标题
    cards.append({
        "tag": "header",
        "data": {
            "template": "blue",
            "title": {
                "content": f"🔔 装修投标项目提醒 - {datetime.now().strftime('%Y-%m-%d')}",
                "tag": "plain_text"
            }
        }
    })
    
    # 统计信息
    total_budget = sum(p.get('budget', 0) for p in projects)
    cards.append({
        "tag": "div",
        "data": {
            "text": {
                "content": f"**今日新增**: {len(projects)} 个项目 | **总预算**: ¥{total_budget/10000:.1f}万",
                "tag": "lark_md"
            }
        }
    })
    
    cards.append({"tag": "hr"})
    
    # 项目列表
    for i, project in enumerate(projects, 1):
        budget_text = project.get('budget_text', '未知')
        region = project.get('region', '广东')
        deadline = project.get('deadline', '未知')
        title = project.get('title', '无标题')
        website = project.get('website', '未知')
        url = project.get('url', '#')
        
        cards.append({
            "tag": "div",
            "data": {
                "text": {
                    "content": f"**{i}. {title}**\n💰 预算：{budget_text} | 📍 地区：{region}\n📅 截止：{deadline} | 🌐 来源：{website}\n[查看详情]({url})",
                    "tag": "lark_md"
                }
            }
        })
        
        if i < len(projects):
            cards.append({"tag": "hr"})
    
    # 底部说明
    cards.append({
        "tag": "note",
        "data": {
            "elements": [{
                "content": "每日上午 10 点自动推送 | 监控范围：广东地区装修项目 50-150 万",
                "tag": "plain_text"
            }]
        }
    })
    
    # 构建消息
    message = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "header": cards[0],
            "elements": cards[1:]
        }
    }
    
    # 发送请求
    try:
        response = requests.post(
            FEISHU_WEBHOOK,
            json=message,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            log_message(f"✅ 飞书推送成功，共 {len(projects)} 个项目")
            return True
        else:
            log_message(f"❌ 飞书推送失败：{response.text}")
            return False
            
    except Exception as e:
        log_message(f"❌ 飞书推送异常：{e}")
        return False

# ==================== 主函数 ====================

def main():
    """主函数"""
    log_message("=" * 50)
    log_message("开始执行投标项目监控...")
    
    # 加载历史记录
    history = load_history()
    
    # 获取项目（实际使用时替换为真实爬虫）
    # all_projects = fetch_all_projects()  # 真实爬虫
    all_projects = get_mock_projects()  # 测试用模拟数据
    
    log_message(f"共获取 {len(all_projects)} 个项目")
    
    # 筛选项目
    filtered_projects = filter_projects(all_projects)
    log_message(f"筛选后 {len(filtered_projects)} 个项目")
    
    # 去重
    new_projects = []
    for project in filtered_projects:
        project_id = generate_project_id(project)
        if project_id not in [p.get('id') for p in history.get('projects', [])]:
            project['id'] = project_id
            new_projects.append(project)
    
    log_message(f"新项目 {len(new_projects)} 个")
    
    # 更新历史记录（保留最近 100 条）
    history['projects'] = ([{'id': p.get('id')} for p in new_projects] + 
                          history.get('projects', []))[:100]
    history['last_check'] = datetime.now().isoformat()
    save_history(history)
    
    # 推送到飞书
    if new_projects:
        send_to_feishu(new_projects)
    else:
        log_message("今日无新项目，跳过推送")
    
    log_message("监控执行完成")
    log_message("=" * 50)
    
    return len(new_projects)

if __name__ == '__main__':
    main()
