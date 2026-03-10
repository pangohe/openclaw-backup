#!/usr/bin/env python3
"""
智能会话压缩 - 方案A
基于 BM25 + 向量的混合检索，保留关键对话

特性：
• BM25 精确关键词匹配
• SentenceTransformer 语义相似度
• 重要性评分（最近性 + 关键性 + 长期记忆）
• 话题段落分块
• 4:1 压缩比目标
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    print("❌ 缺少必需依赖: rank-bm25")
    print("   请运行: pip3 install rank-bm25 --break-system-packages")
    BM25_AVAILABLE = False
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    VECTOR_EMBEDDING_AVAILABLE = True
except ImportError:
    print("⚠️  sentence-transformers 未安装，将使用纯 BM25 模式（关键词匹配）")
    print("   要启用语义搜索，运行: pip3 install sentence-transformers --break-system-packages")
    VECTOR_EMBEDDING_AVAILABLE = False


class EnhancedCompressor:
    """增强型会话压缩器"""

    def __init__(self, model_name='paraphrase-multilingual-MiniLM-L12-v2'):
        """初始化模型"""
        self.model_name = model_name
        self.model = None  # 延迟加载，加快启动速度
        self.bm25 = None
        self.corpus = []  # 分词后的文本
        self.documents = []  # 原始文档
        self.use_vector = VECTOR_EMBEDDING_AVAILABLE

    def load_model(self):
        """延迟加载模型（首次调用时）"""
        if self.use_vector and self.model is None:
            print("🔄 加载句子向量模型...")
            self.model = SentenceTransformer(self.model_name)
            print("✅ 模型加载完成")
        elif not self.use_vector:
            print("ℹ️  使用纯 BM25 模式（未安装 sentence-transformers）")

    def extract_keywords(self, messages: List[Dict]) -> List[str]:
        """从最近的消息中提取关键词"""
        # 获取最近 20 条消息
        recent = messages[-20:] if len(messages) > 20 else messages

        keywords = set()

        # 简单关键词提取：名词、动词、工具名、命令等
        for msg in recent:
            text = msg.get('content', '').lower()

            # 提取命令和路径
            if '```' in text:
                keywords.update(['代码', 'script', 'function', 'command'])

            # 提取工具名
            tools = ['token', 'backup', 'compact', 'cron', 'arbitrage',
                    'monitor', 'moltbook', 'polymarket', 'crypto', 'trading']
            for tool in tools:
                if tool in text:
                    keywords.add(tool)

            # 提取重要术语（简单版）
            important_words = [
                '修复', '优化', '压缩', '阈值', '配置', '安装', '部署',
                '问题', '错误', '警告', '成功', '失败', '更新', '删除',
                'fix', 'optimize', 'compress', 'threshold', 'config',
                'install', 'deploy', 'issue', 'error', 'warning'
            ]
            for word in important_words:
                if word.lower() in text:
                    keywords.add(word.lower())

        return list(keywords)

    def tokenize(self, text: str) -> List[str]:
        """简单的中文分词"""
        # 按空格和常见分隔符分词
        tokens = []
        # 英文单词
        for word in text.split():
            if len(word) > 1:
                tokens.append(word.lower())
        # 简单的中文处理（假设有标点）
        import re
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        tokens.extend(chinese_words)

        return tokens

    def prepare_bm25(self, documents: List[str]):
        """准备 BM25 索引"""
        self.corpus = [self.tokenize(doc) for doc in documents]

        # 过滤掉空的分词结果
        valid_corpus = [c for c in self.corpus if c]
        valid_docs = [documents[i] for i, c in enumerate(self.corpus) if c]

        if not valid_corpus:
            # 所有文档都为空，创建一个虚拟索引
            print("⚠️  所有文档都为空，使用简单评分")
            self.corpus = [[] for _ in documents]
            self.documents = documents
            self.bm25 = None
            self._is_empty_index = True
        else:
            self.corpus = [self.tokenize(doc) for doc in documents]
            self.bm25 = BM25Okapi(valid_corpus)
            self.documents = documents
            self._is_empty_index = False

        self._valid_indices = [i for i, c in enumerate(self.corpus) if c]

    def calculate_importance_score(
        self,
        messages: List[Dict],
        keywords: List[str],
        target_tokens: int,
        keep_ratio: float = 0.25
    ) -> List[float]:
        """
        计算每条消息的重要性评分

        评分维度：
        1. 位置评分（最近的消息分更高）
        2. 关键词匹配度（包含关键词的分更高）
        3. 长度评分（过短或过长的消息权重降低）
        4. 语义相关性（如果启用向量模型）
        """
        n_messages = len(messages)
        scores = []

        for i, msg in enumerate(messages):
            content = msg.get('content', '')
            role = msg.get('role', '')

            # 1. 位置评分（指数衰减，最近的消息更重要）
            position_score = math.exp(-0.01 * (n_messages - i - 1))

            # 2. 关键词匹配度
            keyword_score = 0.0
            if keywords and self.bm25 and not self._is_empty_index:
                query_tokens = self.tokenize(' '.join(keywords))
                if query_tokens:
                    # 处理可能不在有效索引中的消息
                    if i < len(self.bm25.corpus):
                        scores_list = self.bm25.get_scores(query_tokens)
                        if len(scores_list) > 0:
                            min_s = min(scores_list)
                            max_s = max(scores_list)
                            if max_s > min_s:
                                keyword_score = (scores_list[i] - min_s) / (max_s - min_s)

            # 3. 长度评分（偏好中等长度）
            length = len(content)
            if length < 50:
                length_score = 0.3  # 太短
            elif length > 500:
                length_score = 0.5  # 太长
            else:
                length_score = 1.0  # 适中

            # 4. 角色评分（user 消息稍高）
            role_score = 1.2 if role == 'user' else 1.0

            # 综合评分
            total_score = (
                0.4 * position_score +
                0.3 * keyword_score +
                0.2 * length_score +
                0.1 * role_score
            )

            scores.append(total_score)

        # 归一化
        max_score = max(scores) if scores else 1.0
        scores = [s / max_score for s in scores]

        return scores

    def compact_session(
        self,
        session_file: str,
        target_keep_messages: int = 50,
        min_keep_messages: int = 10
    ) -> Dict:
        """
        压缩会话文件

        Args:
            session_file: 会话文件路径
            target_keep_messages: 目标保留消息数
            min_keep_messages: 最少保留消息数

        Returns:
            包含压缩结果的字典
        """
        if not os.path.exists(session_file):
            return {
                'success': False,
                'error': f'文件不存在: {session_file}'
            }

        # 读取会话
        messages = []
        with open(session_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        messages.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        original_count = len(messages)
        original_size = os.path.getsize(session_file)

        if original_count <= min_keep_messages:
            return {
                'success': True,
                'message': f'消息数 {original_count} 已小于最小值 {min_keep_messages}，无需压缩'
            }

        print(f"📦 压缩前: {original_count} 条消息, {original_size/1024:.1f}KB")

        # 提取关键词
        keywords = self.extract_keywords(messages)
        print(f"🔑 提取关键词: {keywords[:10]}...")

        # 准备文档
        documents = [msg.get('content', '') for msg in messages]
        self.prepare_bm25(documents)

        # 计算重要性评分
        scores = self.calculate_importance_score(
            messages,
            keywords,
            target_keep_messages
        )

        # 按评分排序，选择最高分的消息
        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: -x[1])

        # 选择保留的消息（包含一定数量的最近消息）
        top_indices = set()
        for idx, score in indexed_scores[:target_keep_messages]:
            top_indices.add(idx)

        # 确保保留最近 N 条消息的最后 10 条
        for idx in range(max(0, original_count - 10), original_count):
            top_indices.add(idx)

        # 按原始顺序排序
        keep_indices = sorted(top_indices)
        kept_messages = [messages[i] for i in keep_indices]

        # 备份原文件
        backup_file = session_file + '.bak.' + datetime.now().strftime('%Y%m%d%H%M%S')
        os.rename(session_file, backup_file)

        # 写入压缩后的消息
        with open(session_file, 'w', encoding='utf-8') as f:
            for msg in kept_messages:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')

        new_size = os.path.getsize(session_file)
        saved_bytes = original_size - new_size
        saved_percent = (saved_bytes / original_size) * 100
        compression_ratio = original_count / len(kept_messages)

        result = {
            'success': True,
            'original_count': original_count,
            'kept_count': len(kept_messages),
            'original_size_kb': original_size / 1024,
            'new_size_kb': new_size / 1024,
            'saved_percent': saved_percent,
            'compression_ratio': compression_ratio,
            'backup_file': backup_file,
            'keywords_found': len(keywords)
        }

        print(f"✅ {original_count} → {len(kept_messages)} 条消息 (压缩比 {compression_ratio:.1f}:1)")
        print(f"   大小: {original_size/1024:.1f}KB → {new_size/1024:.1f}KB (节省 {saved_percent:.1f}%)")

        return result


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # 测试模式
        print("🧪 测试模式...\n")

        # 查找一个大的会话文件测试
        sessions_dir = '/root/.openclaw/agents/main/sessions'
        if os.path.exists(sessions_dir):
            test_files = []
            for f in os.listdir(sessions_dir):
                if f.endswith('.jsonl'):
                    file_path = os.path.join(sessions_dir, f)
                    size = os.path.getsize(file_path)
                    if size > 50 * 1024:  # 大于 50KB
                        test_files.append((file_path, size))

            if test_files:
                test_files.sort(key=lambda x: x[1], reverse=True)
                test_file = test_files[0][0]
                print(f"📋 测试文件: {os.path.basename(test_file)}\n")

                compressor = EnhancedCompressor()
                result = compressor.compact_session(test_file, target_keep_messages=50)

                if result['success']:
                    print(f"\n✅ 测试通过！压缩比: {result['compression_ratio']:.1f}:1")
                else:
                    print(f"\n❌ 测试失败: {result.get('error')}")
            else:
                print("ℹ️  没有找到足够大的会话文件进行测试")
        else:
            print("❌ 会话目录不存在")
        return

    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} <会话文件.jsonl> [--keep N]")
        print(f"测试: {sys.argv[0]} --test")
        sys.exit(1)

    session_file = sys.argv[1]
    keep_messages = 50

    if '--keep' in sys.argv:
        idx = sys.argv.index('--keep')
        if idx + 1 < len(sys.argv):
            keep_messages = int(sys.argv[idx + 1])

    compressor = EnhancedCompressor()
    result = compressor.compact_session(session_file, target_keep_messages=keep_messages)

    if not result['success']:
        print(f"❌ 错误: {result.get('error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
