#!/usr/bin/env python3
"""
Token Watcher V2 - 增强版智能token监控和自动压缩
基于 Zilliz 最佳实践：BM25 + 话题分组 + 重要性评分

支持以下压缩模式：
- 原生压缩：内置的简单压缩算法
- 增强压缩：使用 EnhancedCompressor（BM25 + 重要性评分）
"""
import json
import os
import re
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple
import math

# 配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
STATE_FILE = WORKSPACE / "token-state-v2.json"
LOG_FILE = WORKSPACE / "memory" / "token-watcher.log"

# 阈值配置（UltraConservative 模式 - 更早触发，防止超限）
THRESHOLDS = {
    "warning": 50,      # 50% (100k / 200k) - 提前警告
    "compress": 60,    # 60% (120k / 200k) - 主动压缩
    "critical": 70,    # 70% (140k / 200k) - 强制压缩
    "emergency": 80    # 80% (160k / 200k) - 立即处理
}

# 通道压缩策略（多agent优化版）
CHANNEL_CONFIG = {
    "dashboard": {
        "keep_messages": 10,      # Dashboard保留10条（应急通道，最少）
        "keep_days": 1,           # 最近1天（应急通道，最新）
        "importance": 1.0,        # 最高优先级（应急用）
        "priority": "emergency"   # 紧急级别
    },
    "qqbot": {
        "keep_messages": 25,      # QQ Bot保留25条（降低）
        "keep_days": 7,           # 最近7天
        "importance": 0.9,
        "priority": "high"
    },
    "telegram": {
        "keep_messages": 25,      # Telegram保留25条（降低）
        "keep_days": 14,          # 最近14天
        "importance": 0.85,
        "priority": "high"
    },
    "whatsapp": {
        "keep_messages": 15,      # WhatsApp保留15条
        "keep_days": 3,           # 最近3天
        "importance": 0.7,
        "priority": "medium"
    },
    "main": {
        "keep_messages": 40,      # 主通道保留40条（降低）
        "keep_days": 30,          # 最近30天
        "importance": 1.0,
        "priority": "high"
    },
    "default": {
        "keep_messages": 20,
        "keep_days": 7,
        "importance": 0.5,
        "priority": "low"
    }
}

# 模型上下文大小（GLM4.7）
CONTEXT_WINDOW = 200000  # tokens

# BM25 参数
BM25_K1 = 1.2
BM25_B = 0.75

def log(message, quiet=False):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)

    if not quiet:
        # 写入日志文件
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')

# ==================== 增强压缩模式 ====================
USE_ENHANCED_COMPACT = True  # 是否使用增强压缩器（False = 使用原生压缩）
ENHANCED_AVAILABLE = False

if USE_ENHANCED_COMPACT:
    try:
        WORKSPACE_ADJUSTED = Path("/root/.openclaw/workspace")
        ENHANCED_COMPACT_PATH = WORKSPACE_ADJUSTED / "skills" / "token-saver-v2" / "scripts"
        sys.path.insert(0, str(ENHANCED_COMPACT_PATH))
        from enhanced_compact import EnhancedCompressor
        ENHANCED_AVAILABLE = True
        log("✅ 增强压缩模式已启用", quiet=True)
    except ImportError as e:
        log(f"⚠️  增强压缩器导入失败，使用原生压缩: {e}", quiet=True)
        ENHANCED_AVAILABLE = False
        USE_ENHANCED_COMPACT = False
else:
    ENHANCED_AVAILABLE = False
# =================================================================

def identify_channel(session_id: str, messages: List[Dict] = None) -> str:
    """识别会话通道 - 基于 session ID 和会话内容"""
    session_id_lower = session_id.lower()

    # Dashboard 通道识别（优先级最高 - 应急通道）
    if "dashboard" in session_id_lower or "tui" in session_id_lower:
        return "dashboard"

    # 从 session ID 判断
    if "qqbot" in session_id_lower or "c2c" in session_id_lower:
        return "qqbot"
    elif "telegram" in session_id_lower:
        return "telegram"
    elif "whatsapp" in session_id_lower:
        return "whatsapp"
    elif "main" in session_id_lower:
        return "main"

    # 如果 ID 无法判断，从消息内容中判断
    if messages:
        # 合并所有消息内容
        all_text = ""
        for msg in messages:
            if 'content' in msg:
                content = str(msg['content'])
                all_text += content.lower()

        # 搜索关键词
        if "dashboard" in all_text or "tui" in all_text or "终端" in all_text:
            return "dashboard"
        elif "qqbot" in all_text or "c2c" in all_text:
            return "qqbot"
        elif "telegram" in all_text or "lesliehehebot" in all_text:
            return "telegram"
        elif "whatsapp" in all_text:
            return "whatsapp"

    # 默认
    return "default"

def get_session_info(session_file: Path) -> Dict:
    """获取会话信息 - 准确计算实际 token 使用量"""
    try:
        size = session_file.stat().st_size

        # 统计实际消息并读取 usage 信息
        messages = []
        actual_tokens = 0
        has_usage_data = False
        message_count = 0

        with open(session_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        msg = json.loads(line)

                        # 优先读取实际的 usage 数据（最准确）
                        if 'usage' in msg:
                            usage = msg['usage']
                            # OpenAI 格式: input, output, totalTokens
                            input_tokens = usage.get('input', 0)
                            output_tokens = usage.get('output', 0)
                            total_tokens = usage.get('totalTokens', 0)

                            if total_tokens > 0:
                                actual_tokens += total_tokens
                            else:
                                actual_tokens += (input_tokens + output_tokens)

                            has_usage_data = True
                            message_count += 1

                        # 统计消息数（只统计有 role 或 content 的消息类型）
                        if 'message' in msg and msg['message'].get('role'):
                            messages.append(msg['message'])

                    except:
                        # 忽略解析失败的行
                        pass

        total_messages = len(messages)

        # 如果没有 usage 数据，基于消息内容长度估算
        if not has_usage_data or actual_tokens == 0:
            content_length = 0
            for msg in messages:
                content = str(msg.get('content', ''))
                content_length += len(content)

            # 中文：2-3字符/token，英文：4字符/token
            # 取保守估计：3字符 ≈ 1 token
            estimated_tokens = int(content_length / 3)
        else:
            estimated_tokens = actual_tokens

        token_percent = min((estimated_tokens / CONTEXT_WINDOW) * 100, 100)

        # 识别通道（传入消息用于内容判断）
        channel = identify_channel(session_file.stem, messages)

        return {
            "file": session_file.name,
            "path": str(session_file),
            "channel": channel,
            "size_mb": round(size / 1024 / 1024, 2),
            "total_messages": total_messages,
            "messages_sample": messages[-10:],  # 最近10条用于分析
            "estimated_tokens": estimated_tokens,
            "token_percent": round(token_percent, 1),
            "has_usage_data": has_usage_data,
            "message_count_with_usage": message_count,
            "config": CHANNEL_CONFIG.get(channel, CHANNEL_CONFIG["default"])
        }
    except Exception as e:
        log(f"❌ 读取会话失败 {session_file.name}: {e}")
        return None

def calculate_idf(doc_freq: int, total_docs: int) -> float:
    """计算 IDF"""
    if doc_freq == 0:
        return 0
    return math.log((total_docs - doc_freq + 0.5) / (doc_freq + 0.5))

def bm25_score(query_terms: List[str], doc_terms: List[str], doc_freqs: Dict[str, int], total_docs: int, doc_len: int, avg_doc_len: float) -> float:
    """BM25 评分"""
    score = 0
    for term in query_terms:
        if term in doc_terms:
            # 词频
            tf = doc_terms.count(term)

            # IDF
            idf = calculate_idf(doc_freqs.get(term, 0), total_docs)

            # BM25 公式
            score += idf * (tf * (BM25_K1 + 1)) / (tf + BM25_K1 * (1 - BM25_B + BM25_B * doc_len / avg_doc_len))

    return score

def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """提取关键词（简单的中文分词）"""
    # 移除特殊字符和emoji
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
    text = text.lower()

    # 中文分词（简单按字拆分，实际应用可用 jieba）
    words = []
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 中文字符
            words.append(char)
        elif char.isalnum():  # 英文/数字
            words.append(char)

    # 过滤停用词（简化版）
    stopwords = {'的', '了', '是', '在', '我', '你', '他', '她', '它', '把', '被', '将', 'the', 'a', 'an', 'is', 'are'}
    words = [w for w in words if w and w not in stopwords and len(w) > 1]

    # 统计词频
    from collections import Counter
    word_counts = Counter(words)

    # 返回词频最高的词
    return [word for word, _ in word_counts.most_common(top_n)]

def calculate_message_importance(message: Dict, recent_keywords: List[str], recency_score: float) -> float:
    """计算消息重要性"""
    text = str(message.get('content', ''))
    role = message.get('role', '')

    # 1. 关键词匹配（BM25 简化版）
    keyword_score = 0
    if recent_keywords:
        msg_words = extract_keywords(text, top_n=20)
        matches = len(set(msg_words) & set(recent_keywords))
        keyword_score = min(matches / len(recent_keywords), 1.0) if recent_keywords else 0

    # 2. 角色权重（用户/assistant更重要）
    role_weights = {
        'user': 1.2,
        'assistant': 1.1,
        'system': 0.5,
        'tool': 0.3
    }
    role_score = role_weights.get(role, 1.0)

    # 3. 新鲜度（recency_score 传入）
    # 4. 内容长度（太短/太长降低权重）
    length = len(text)
    if length < 10 or length > 5000:
        length_score = 0.7
    elif length < 50 or length > 2000:
        length_score = 0.9
    else:
        length_score = 1.0

    # 综合得分
    total_score = (
        recency_score * 0.4 +
        keyword_score * 0.3 +
        role_score * 0.2 +
        length_score * 0.1
    )

    return round(total_score, 3)

def smart_compact_session(session_info: Dict, priority_level: str = None, quiet=False) -> Dict:
    """智能压缩会话 - 支持优先级"""
    session_path = Path(session_info['path'])
    config = session_info['config']

    # 根据优先级调整保留数量
    keep_messages = config['keep_messages']
    channel = session_info['channel']
    token_percent = session_info['token_percent']

    # 高优先级通道更积极压缩
    if priority_level == "emergency":
        keep_messages = max(5, keep_messages // 2)  # Dashboard: 最多5条
        log(f"🚨 应急通道 [{channel}] 激进压缩: {keep_messages} 条", quiet)
    elif priority_level == "high" and token_percent > 70:
        keep_messages = max(10, keep_messages // 1.5)  # 主通道: 降为2/3
        log(f"⚡ 高优先级通道 [{channel}] 激进压缩: {keep_messages} 条", quiet)

    # 原生压缩模式（降级或默认）
    log(f"🗑️  开始智能压缩: {session_info['file']}", quiet)
    keep_days = config['keep_days']

    try:
        # 读取所有消息
        all_messages = []
        with open(session_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    all_messages.append(json.loads(line))

        if len(all_messages) <= keep_messages:
            log(f"   消息数 ({len(all_messages)}) 少于保留阈值 ({keep_messages})，无需压缩", quiet)
            return {"success": False, "reason": "too_small"}

        # 1. 提取最近关键词（消息采样）
        sample_size = min(100, len(all_messages))
        sample_messages = all_messages[-sample_size:]
        all_text = " ".join([str(m.get('content', '')) for m in sample_messages])
        recent_keywords = extract_keywords(all_text, top_n=10)

        log(f"   检测到关键词: {recent_keywords}", quiet)

        # 2. 计算每条消息的重要性
        scored_messages = []
        cutoff_time = datetime.now() - timedelta(days=keep_days)

        for idx, msg in enumerate(all_messages):
            # 新鲜度得分（最近的消息得分更高）
            freshness = idx / len(all_messages)

            # 计算重要性
            score = calculate_message_importance(msg, recent_keywords, freshness)

            scored_messages.append({
                'msg': msg,
                'score': score,
                'index': idx
            })

            # 强制保留最近N条（不管分数）
            if idx >= len(all_messages) - keep_messages:
                scored_messages[-1]['forced_keep'] = True

        # 3. 分数排序，保留高分的
        scored_messages.sort(key=lambda x: x['score'], reverse=True)

        kept_messages = []
        for item in scored_messages:
            if len(kept_messages) >= keep_messages:
                break
            if item.get('forced_keep'):
                # 强制保留的放到最前面
                item['msg']['_forced'] = True
                kept_messages.insert(0, item['msg'])
            else:
                kept_messages.append(item['msg'])

        # 4. 按原始顺序重新排序
        kept_messages.sort(key=lambda x: all_messages.index(x) if x not in all_messages else len(all_messages))

        # 备份原文件
        backup_path = session_path.with_suffix('.jsonl.bak')
        if backup_path.exists():
            # 删除旧备份
            backup_path.unlink()
        shutil.copy2(session_path, backup_path)
        log(f"   ✅ 备份到: {backup_path.name}", quiet)

        # 写入压缩后的文件
        with open(session_path, 'w', encoding='utf-8') as f:
            for msg in kept_messages:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')

        # 统计
        original_size = len(all_messages)
        compressed_size = len(kept_messages)
        compression_ratio = round((1 - compressed_size / original_size) * 100, 1)

        log(f"   ✅ 压缩完成: {original_size} → {compressed_size} 条消息 (节省 {compression_ratio}%)", quiet)

        return {
            "success": True,
            "original": original_size,
            "compressed": compressed_size,
            "saved_percent": compression_ratio,
            "keywords": recent_keywords,
            "mode": "native"
        }

    except Exception as e:
        log(f"   ❌ 压缩失败: {e}", quiet)
        return {"success": False, "reason": str(e)}

def load_state():
    """加载状态"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "timestamp": datetime.now().isoformat(),
            "last_check": None,
            "sessions": {},
            "compressions": []
        }

def save_state(state):
    """保存状态"""
    state["timestamp"] = datetime.now().isoformat()
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def get_status_level(percent):
    """获取状态级别"""
    if percent >= THRESHOLDS["emergency"]:
        return "EMERGENCY"
    elif percent >= THRESHOLDS["critical"]:
        return "CRITICAL"
    elif percent >= THRESHOLDS["compress"]:
        return "COMPRESS"
    elif percent >= THRESHOLDS["warning"]:
        return "WARNING"
    else:
        return "OK"

def prevent_repeat_compression(state: Dict, session_id: str, min_minutes: int = 5) -> bool:
    """防止短时间内重复压缩"""
    compressions = state.get("compressions", [])

    if not compressions:
        return False

    last_compress = compressions[-1]
    if last_compress.get("session") == session_id:
        last_time = datetime.fromisoformat(last_compress.get("time", ""))
        if datetime.now() - last_time < timedelta(minutes=min_minutes):
            return True

    return False

def check_and_compress_all(sessions: List[Dict], state: Dict, quiet=False) -> Dict:
    """检查并压缩所有超限会话 - 优先级支持"""
    results = {
        "checked": len(sessions),
        "compressed": 0,
        "saved_total_messages": 0,
        "sessions_compressed": [],
        "channels_compressed": {}
    }

    log(f"\n🔍 检查 {len(sessions)} 个会话...", quiet)

    # 按token使用率排序（处理超限最严重的优先）
    sessions_sorted = sorted(sessions, key=lambda x: x['token_percent'], reverse=True)

    for session in sessions_sorted:
        file = session['file']
        channel = session['channel']
        percent = session['token_percent']
        config = session['config']

        status = get_status_level(percent)
        priority = config.get('priority', 'low')

        log(f"\n[{channel}] {file}: {percent}% ({status}) [优先级: {priority}]", quiet)

        # 判断是否需要压缩（根据优先级调整）
        should_compress = False
        compress_priority = None

        if status == "EMERGENCY":
            # 紧急状态：所有通道都压缩
            should_compress = True
            compress_priority = "emergency"
        elif status == "CRITICAL":
            # 严重状态：high+优先级压缩
            if priority in ['high', 'emergency']:
                should_compress = True
                compress_priority = "high"
        elif status == "COMPRESS":
            # 压缩状态：emergency优先级压缩
            if priority == 'emergency':
                should_compress = True
                compress_priority = "emergency"
            elif priority == 'high':
                should_compress = True
                compress_priority = "normal"

        if should_compress:
            # 检查是否刚压缩过（emergency通道冷却时间更短）
            cooldown = 3 if priority == 'emergency' else 5
            if prevent_repeat_compression(state, file, min_minutes=cooldown):
                log(f"   ⏭️  {cooldown}分钟内已压缩过，跳过", quiet)
                continue

            # 执行压缩（传入优先级）
            result = smart_compact_session(session, priority_level=compress_priority, quiet=quiet)

            if result.get("success"):
                results["compressed"] += 1
                results["saved_total_messages"] += (result["original"] - result["compressed"])
                results["sessions_compressed"].append({
                    "file": file,
                    "channel": channel,
                    "original": result["original"],
                    "compressed": result["compressed"],
                    "saved_percent": result["saved_percent"],
                    "priority": priority
                })

                # 记录通道压缩统计
                if channel not in results["channels_compressed"]:
                    results["channels_compressed"][channel] = 0
                results["channels_compressed"][channel] += 1

                # 记录压缩历史
                state["compressions"].append({
                    "time": datetime.now().isoformat(),
                    "session": file,
                    "channel": channel,
                    "original": result["original"],
                    "compressed": result["compressed"],
                    "saved_percent": result["saved_percent"],
                    "keywords": result.get("keywords", []),
                    "priority": priority
                })

                state["sessions"][file] = {
                    "last_compression": datetime.now().isoformat(),
                    "channel": channel,
                    "priority": priority
                }

        elif status == "WARNING":
            log(f"   ⚠️  Token使用量偏高，但未到压缩阈值", quiet)

        else:
            log(f"   ✅ 状态正常", quiet)

    return results

def main():
    """主函数"""
    quiet_mode = '--quiet' in sys.argv or '-q' in sys.argv
    check_only = '--check-only' in sys.argv

    log("🚀 Token Watcher V2 启动...", quiet=quiet_mode)

    # 获取所有会话
    sessions = []
    if SESSIONS_DIR.exists():
        for session_file in SESSIONS_DIR.glob("*.jsonl"):
            info = get_session_info(session_file)
            if info:
                sessions.append(info)

    if not sessions:
        log("ℹ️  没有找到会话文件", quiet=quiet_mode)
        return

    # 按通道分组统计
    by_channel = defaultdict(list)
    total_tokens = 0
    max_percent = 0

    for session in sessions:
        channel = session['channel']
        by_channel[channel].append(session)
        total_tokens += session['estimated_tokens']
        max_percent = max(max_percent, session['token_percent'])

    # 统计概览
    log(f"\n📊 Token Watcher V2 统计概览", quiet=quiet_mode)
    log(f"   会话总数: {len(sessions)}", quiet=quiet_mode)
    log(f"   总 Token: {total_tokens:,}", quiet=quiet_mode)
    log(f"   最高使用率: {max_percent}%", quiet=quiet_mode)

    log(f"\n📡 各通道详情:", quiet=quiet_mode)
    for channel, channel_sessions in by_channel.items():
        channel_tokens = sum(s['estimated_tokens'] for s in channel_sessions)
        channel_avg_percent = sum(s['token_percent'] for s in channel_sessions) / len(channel_sessions)
        config = CHANNEL_CONFIG.get(channel, CHANNEL_CONFIG["default"])

        log(f"   [{channel.upper()}]", quiet=quiet_mode)
        log(f"     会话数: {len(channel_sessions)}", quiet=quiet_mode)
        log(f"     Token: {channel_tokens:,}", quiet=quiet_mode)
        log(f"     平均使用率: {channel_avg_percent:.1f}%", quiet=quiet_mode)
        log(f"     保留策略: {config['keep_messages']}条 / {config['keep_days']}天", quiet=quiet_mode)

    # 加载状态
    state = load_state()

    # 检查并压缩
    if not check_only:
        results = check_and_compress_all(sessions, state, quiet=quiet_mode)

        if results["compressed"] > 0:
            log(f"\n✅ 压缩完成！", quiet=quiet_mode)
            log(f"   压缩会话数: {results['compressed']}", quiet=quiet_mode)
            log(f"   节省消息数: {results['saved_total_messages']:,}", quiet=quiet_mode)

            # 按通道分组显示
            log(f"\n   📊 按通道统计:", quiet=quiet_mode)
            for channel, count in results["channels_compressed"].items():
                log(f"      {channel.upper()}: {count} 个会话", quiet=quiet_mode)

            log(f"\n   压缩详情:", quiet=quiet_mode)
            for item in results["sessions_compressed"]:
                priority_icon = "🚨" if item["priority"] == "emergency" else "⚡" if item["priority"] == "high" else "  "
                log(f"   {priority_icon} {item['file']} ({item['channel']}): {item['original']} → {item['compressed']} 条 (节省 {item['saved_percent']}%)", quiet=quiet_mode)
        else:
            log(f"\n✅ 所有必要会话已在良好状态", quiet=quiet_mode)

    # 保存状态
    state["last_check"] = datetime.now().isoformat()
    save_state(state)

    log(f"\n✅ 检查完成 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})", quiet=quiet_mode)

    return {"max_percent": max_percent, "compressed": results.get("compressed", 0) if not check_only else 0}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Token Watcher V2 - 增强版智能监控和压缩")
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式，只记录到日志")
    parser.add_argument("--check-only", action="store_true", help="仅检查，不执行压缩")
    args = parser.parse_args()

    try:
        result = main()
        if not args.quiet:
            print(f"\n状态代码: {result}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)
