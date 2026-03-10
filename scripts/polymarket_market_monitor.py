#!/usr/bin/env python3
"""
Polymarket Market Monitor - 获取真实市场数据
"""
import json
import requests
from datetime import datetime
from pathlib import Path

# 数据目录
DATA_DIR = Path("/root/.openclaw/workspace/data/polymarket")
REPORT_FILE = DATA_DIR / "market_report.json"
ALERT_FILE = DATA_DIR / "alert.json"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def fetch_polymarket_events():
    """获取Polymarket事件列表"""
    try:
        url = "https://gamma-api.polymarket.com/events"
        params = {"limit": 50, "order": "volume", "ascending": False}
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            log(f"❌ Polymarket API错误: {response.status_code}")
            return None
    except Exception as e:
        log(f"❌ 获取Polymarket事件失败: {e}")
        return None

def analyze_crypto_events(events):
    """分析与加密货币相关的预测事件"""
    crypto_keywords = [
        "bitcoin", "btc", "ethereum", "eth", "crypto", "cryptocurrency",
        "solana", "bnb", "xrp", "cardano", "polkadot", "dogecoin",
        "ripple", "binance", "coinbase", "defi", "token", "altcoin"
    ]
    
    crypto_events = []
    if not events:
        return crypto_events
    
    for event in events:
        title = (event.get("title") or "").lower()
        description = (event.get("description") or "").lower()
        category = (event.get("category") or "").lower()
        
        combined = title + " " + description + " " + category
        
        if any(keyword in combined for keyword in crypto_keywords):
            markets = event.get("markets", [])
            outcome_prices = []
            if markets and len(markets) > 0:
                market = markets[0]
                outcome_prices_str = market.get("outcomePrices", "[]")
                try:
                    outcome_prices = json.loads(outcome_prices_str)
                except:
                    pass
            
            prob = 0
            if outcome_prices and len(outcome_prices) >= 2:
                try:
                    prob = float(outcome_prices[0])
                except:
                    pass
            
            volume = event.get("volume", 0)
            
            crypto_events.append({
                "name": event.get("title", ""),
                "slug": event.get("slug", ""),
                "probability": prob,
                "volume": volume,
                "end_date": event.get("endDate", ""),
                "category": event.get("category", ""),
                "url": f"https://polymarket.com/market/{event.get('slug', '')}"
            })
    
    return crypto_events

def detect_arbitrage_opportunities(events):
    """检测套利机会"""
    opportunities = []
    if not events:
        return opportunities
    
    for event in events:
        volume = event.get("volume", 0)
        markets = event.get("markets", [])
        
        if markets and len(markets) > 0:
            market = markets[0]
            outcome_prices_str = market.get("outcomePrices", "[]")
            try:
                outcome_prices = json.loads(outcome_prices_str)
                if len(outcome_prices) >= 2:
                    yes_prob = float(outcome_prices[0])
                    no_prob = float(outcome_prices[1])
                    
                    # 检测价格偏离（套利空间）
                    spread = abs(yes_prob + no_prob - 1.0)
                    
                    if spread > 0.01:  # 超过1%的套利空间
                        opportunities.append({
                            "type": "price_misalignment",
                            "event": event.get("title", ""),
                            "yes_probability": yes_prob,
                            "no_probability": no_prob,
                            "spread": spread,
                            "volume": volume,
                            "note": f"价格偏离 {spread:.2%}, 可能存在套利机会"
                        })
                    
                    # 边缘概率 + 高流动性
                    if (yes_prob > 0.45 and yes_prob < 0.55) and volume > 50000:
                        opportunities.append({
                            "type": "edge_uncertainty",
                            "event": event.get("title", ""),
                            "probability": yes_prob,
                            "volume": volume,
                            "note": "高流动性市场概率接近50%，信息不对称机会"
                        })
            except:
                pass
    
    return opportunities

def save_report(events, crypto_events, opportunities):
    """保存市场报告"""
    report = {
        "check_time": datetime.now().isoformat(),
        "total_events": len(events) if events else 0,
        "crypto_events": crypto_events,
        "arbitrage_opportunities": opportunities
    }
    
    try:
        with open(REPORT_FILE, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        log(f"✅ 报告已保存: {REPORT_FILE}")
    except Exception as e:
        log(f"❌ 保存报告失败: {e}")
    
    return report

def create_alert(opportunities):
    """创建警报"""
    significant = [o for o in opportunities if o["type"] == "price_misalignment" and o["spread"] > 0.02]
    
    if not significant:
        if ALERT_FILE.exists():
            ALERT_FILE.unlink()
        return None
    
    alert = {
        "created_at": datetime.now().isoformat(),
        "opportunity_count": len(significant),
        "opportunities": significant[:5]
    }
    
    try:
        with open(ALERT_FILE, 'w') as f:
            json.dump(alert, f, indent=2, ensure_ascii=False)
        log(f"⚠️ 警报已创建: {ALERT_FILE}")
    except Exception as e:
        log(f"❌ 创建警报失败: {e}")
    
    return alert

def main():
    log("🚀 Polymarket Market Monitor 开始运行...")
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    log("📊 获取Polymarket市场数据...")
    events = fetch_polymarket_events()
    
    if events:
        log(f"✅ 获取到 {len(events)} 个市场事件")
        
        crypto_events = analyze_crypto_events(events)
        log(f"🔗 发现 {len(crypto_events)} 个加密货币相关市场")
        
        for event in crypto_events[:5]:
            log(f" - {event['name'][:60]}...: 概率={event['probability']:.1%}, 成交量=${event['volume']:,.0f}")
        
        opportunities = detect_arbitrage_opportunities(events)
        log(f"🎯 发现 {len(opportunities)} 个潜在套利/机会")
        
        for opp in opportunities[:3]:
            log(f" → {opp['event'][:50]}...: {opp['note']}")
        
        save_report(events, crypto_events, opportunities)
        alert = create_alert(opportunities)
        
        if alert:
            log(f"⚠️ 重大套利机会: {alert['opportunity_count']} 个 (>2%偏离)")
    else:
        log("❌ 无法获取市场数据")
    
    log("✅ 监控完成")

if __name__ == "__main__":
    main()