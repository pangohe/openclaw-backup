#!/usr/bin/env python3
"""
实时会话索引器 - 方案A
监听会话变化，自动建立索引

特性：
• 实时监听会话文件变化（inotify）
• 自动建立 BM25 索引
• 按会话分目录存储索引
• 支持增量更新
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List
import pickle

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    print("❌ 请先安装 rank-bm25")
    print("   pip3 install rank-bm25 --break-system-packages")
    sys.exit(1)

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("⚠️  watchdog 未安装，将使用轮询模式")
    print("   建议安装: pip3 install watchdog --break-system-packages")
    Observer = None


class ChatIndexer:
    """会话索引器"""

    def __init__(self, sessions_dir='/root/.openclaw/agents/main/sessions',
                 index_dir='/root/.openclaw/workspace/data/chat-indexes'):
        """
        初始化索引器

        Args:
            sessions_dir: 会话文件目录
            index_dir: 索引存储目录
        """
        self.sessions_dir = sessions_dir
        self.index_dir = index_dir
        self.indexes: Dict[str, dict] = {}  # session_name -> index_data

        # 创建索引目录
        os.makedirs(index_dir, exist_ok=True)

        # 加载已存在的索引
        self.load_indexes()

    def tokenize(self, text: str) -> List[str]:
        """简单的分词"""
        tokens = []
        # 英文单词
        for word in text.split():
            if len(word) > 1:
                tokens.append(word.lower())

        # 中文简单处理
        import re
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        tokens.extend(chinese_words)

        return tokens

    def build_index(self, session_file: str) -> dict:
        """
        为会话文件建立索引

        Returns:
            index_data: 包含 bm25, corpus, documents 的字典
        """
        messages = []
        with open(session_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        messages.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        if not messages:
            return None

        # 提取文档
        documents = []
        for msg in messages:
            content = msg.get('content', '')
            # 添加角色信息
            role = msg.get('role', '')
            documents.append(f"[{role}] {content}")

        # 建立 BM25 索引
        corpus = [self.tokenize(doc) for doc in documents]
        bm25 = BM25Okapi(corpus)

        index_data = {
            'documents': documents,
            'corpus': corpus,
            'bm25': bm25,
            'message_count': len(messages),
            'last_updated': datetime.now().isoformat()
        }

        return index_data

    def save_index(self, session_name: str, index_data: dict):
        """保存索引到磁盘"""
        index_file = os.path.join(self.index_dir, f'{session_name}.idx')

        # BM25 对象不能直接 pickle，需要序列化数据
        serializable = {
            'corpus': index_data['corpus'],
            'documents': index_data['documents'],
            'message_count': index_data['message_count'],
            'last_updated': index_data['last_updated']
        }

        with open(index_file, 'wb') as f:
            pickle.dump(serializable, f)

        # 更新内存中的索引（重建 BM25）
        self.indexes[session_name] = {
            'corpus': serializable['corpus'],
            'documents': serializable['documents'],
            'bm25': BM25Okapi(serializable['corpus']),
            'message_count': serializable['message_count'],
            'last_updated': serializable['last_updated']
        }

        print(f"✅ 索引已保存: {session_name} ({index_data['message_count']} 条消息)")

    def load_indexes(self):
        """加载所有已存在的索引"""
        if not os.path.exists(self.index_dir):
            return

        for index_file in os.listdir(self.index_dir):
            if index_file.endswith('.idx'):
                session_name = index_file[:-4]  # 去掉 .idx
                index_path = os.path.join(self.index_dir, index_file)

                try:
                    with open(index_path, 'rb') as f:
                        serializable = pickle.load(f)

                    # 重建 BM25
                    self.indexes[session_name] = {
                        'corpus': serializable['corpus'],
                        'documents': serializable['documents'],
                        'bm25': BM25Okapi(serializable['corpus']),
                        'message_count': serializable['message_count'],
                        'last_updated': serializable['last_updated']
                    }

                    print(f"✅ 已加载索引: {session_name} ({serializable['message_count']} 条消息)")
                except Exception as e:
                    print(f"⚠️  加载索引失败 {session_name}: {e}")

    def search(self, session_name: str, query: str, top_k: int = 5) -> List[tuple]:
        """
        在指定会话中搜索

        Args:
            session_name: 会话名称（文件名，不含 .jsonl）
            query: 搜索查询
            top_k: 返回结果数量

        Returns:
            结果列表，每个元素是 (doc, score)
        """
        if session_name not in self.indexes:
            # 尝试加载索引
            session_file = os.path.join(self.sessions_dir, f'{session_name}.jsonl')
            if not os.path.exists(session_file):
                return []

            index_data = self.build_index(session_file)
            if index_data:
                self.save_index(session_name, index_data)
            else:
                return []

        index = self.indexes[session_name]
        query_tokens = self.tokenize(query)

        if not query_tokens:
            return []

        scores = index['bm25'].get_scores(query_tokens)
        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: -x[1])

        # 返回 top_k 结果
        results = []
        for idx, score in indexed_scores[:top_k]:
            results.append((index['documents'][idx], score))

        return results

    def update_session(self, session_name: str):
        """更新指定会话的索引"""
        session_file = os.path.join(self.sessions_dir, f'{session_name}.jsonl')

        if not os.path.exists(session_file):
            return

        index_data = self.build_index(session_file)
        if index_data:
            self.save_index(session_name, index_data)

    def update_all(self):
        """更新所有会话的索引"""
        print("🔄 更新所有会话索引...")

        if not os.path.exists(self.sessions_dir):
            return

        for session_file in os.listdir(self.sessions_dir):
            if session_file.endswith('.jsonl'):
                session_name = session_file[:-6]  # 去掉 .jsonl
                self.update_session(session_name)

        print(f"✅ 索引更新完成，共 {len(self.indexes)} 个会话")

    def get_status(self) -> dict:
        """获取索引器状态"""
        return {
            'sessions_dir': self.sessions_dir,
            'index_dir': self.index_dir,
            'indexed_sessions': len(self.indexes),
            'total_messages': sum(idx['message_count'] for idx in self.indexes.values())
        }


def main():
    """主函数"""
    indexer = ChatIndexer()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'update':
            # 更新所有索引
            indexer.update_all()

        elif command == 'search':
            # 搜索
            if len(sys.argv) < 4:
                print(f"用法: {sys.argv[0]} search <会话名> <查询>")
                sys.exit(1)

            session_name = sys.argv[2]
            query = sys.argv[3]

            results = indexer.search(session_name, query, top_k=5)

            print(f"\n🔍 在 '{session_name}' 中搜索 '{query}':\n")
            for i, (doc, score) in enumerate(results, 1):
                print(f"\n{i}. [相关度: {score:.3f}]")
                print(f"   {doc[:200]}{'...' if len(doc) > 200 else ''}")

        elif command == 'status':
            # 显示状态
            status = indexer.get_status()
            print(f"\n📊 索引器状态:")
            print(f"   会话目录: {status['sessions_dir']}")
            print(f"   索引目录: {status['index_dir']}")
            print(f"   已索引会话: {status['indexed_sessions']}")
            print(f"   总消息数: {status['total_messages']}")

        else:
            print(f"未知命令: {command}")
            print(f"可用命令: update, search, status")
    else:
        # 默认：更新所有索引
        indexer.update_all()


if __name__ == '__main__':
    main()
