#!/usr/bin/env python3
"""
Crypto Trend Collector - 每小时收集加密货币走势数据
收集时间：每天 09:00 - 22:00
"""
import json
import requests
from datetime import datetime
from pathlib import Path

# API配置
TAVILY_API_KEY = "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"
COINGECKO_API = "https://api.coingecko.com/api/v3"

# 数据目录
DATA_DIR = Path.home() / ".openclaw" / "workspace" / "data" / "crypto-trends"
NOTIFICATIONS_DIR = DATA_DIR / "notifications"

# 监控的加密货币
COINS = ["bitcoin", "ethereum", "binancecoin", "solana", "ripple", "cardano", "dogecoin", "polkadot", "tron"]

# 重要变化阈值
IMPORTANT_CHANGE = 5.0  # 5%变化触发通知

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def fetch_crypto_trends():
    """从CoinGecko获取加密货币走势"""
    try:
        coin_ids = ",".join(COINS)
        url = f"{COINGECKO_API}/coins/markets?vs_currency=usd&ids={coin_ids}&order=market_cap_desc&per_page=10&page=1&sparkline=false&price_change_percentage=24h,7d"
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            return response.json()
        else:
            log(f"❌ CoinGecko API错误: {response.status_code}")
            return None

    except Exception as e:
        log(f"❌ 获取加密货币数据失败: {e}")
        return None

def analyze_changes(data):
    """分析价格变化，找出重要变化"""
    important = []

    if not data:
        return []

    for coin in data:
        change_24h = coin.get("price_change_percentage_24h", 0) or 0

        if abs(change_24h) >= IMPORTANT_CHANGE:
            important.append({
                "name": coin["name"],
                "symbol": coin["symbol"].upper(),
                "price": coin["current_price"],
                "change_24h": change_24h,
                "timestamp": datetime.now().isoformat()
            })

    return important

def save_data(data):
    """保存数据到文件"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    filename = DATA_DIR / f"crypto-trend-{timestamp}.json"

    try:
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "coins": data
            }, f, indent=2)

        log(f"✅ 数据已保存: {filename}")

    except Exception as e:
        log(f"❌ 保存数据失败: {e}")

def create_notification(important_changes):
    """创建通知"""
    if not important_changes:
        return None

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = NOTIFICATIONS_DIR / f"notification-{timestamp}.json"

    notification = {
        "created_at": datetime.now().isoformat(),
        "type": "crypto_trend",
        "sent": False,
        "channel": "telegram",
        "message": f"🚨 加密货币重要变化：\n\n"
    }

    for change in important_changes:
        emoji = "📈" if change["change_24h"] > 0 else "📉"
        notification["message"] += f"{emoji} {change['name']} ({change['symbol']}): ${change['price']:,.2f} ({change['change_24h']:+.2f}%)\n"

    try:
        with open(filename, 'w') as f:
            json.dump(notification, f, indent=2)

        log(f"✅ 通知已创建: {filename}")
        return filename

    except Exception as e:
        log(f"❌ 创建通知失败: {e}")
        return None

def is_business_hours():
    """检查是否在工作时间 (09:00 - 22:00)"""
    hour = datetime.now().hour
    return 9 <= hour < 22

def main():
    """主函数"""
    log("🔍 Crypto Trend Collector 开始运行...")

    # 检查工作时间
    if not is_business_hours():
        log("ℹ️  当前不在工作时间 (09:00-22:00)，跳过收集")
        return

    # 创建目录
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    NOTIFICATIONS_DIR.mkdir(parents=True, exist_ok=True)

    # 获取数据
    data = fetch_crypto_trends()

    if data:
        # 分析变化
        important_changes = analyze_changes(data)

        # 保存数据
        save_data(data)

        # 创建通知
        if important_changes:
            create_notification(important_changes)

        log("✅ 收集完成")

    else:
        log("❌ 没有获取到数据")

if __name__ == "__main__":
    main()
