"""
Teamily AI Core - Memory System
记忆存储与检索系统
"""

import os
import json
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

class MemoryType(Enum):
    WORKING = "working"      # 短期记忆
    LONG_TERM = "long_term"  # 长期记忆
    VECTOR = "vector"        # 向量记忆

@dataclass
class Memory:
    key: str
    value: str
    memory_type: MemoryType
    importance: float = 0.5
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)
    embeddings: Optional[List[float]] = None

class MemoryStore:
    """记忆存储基类"""
    
    def __init__(self, store_type: str = "json"):
        self.store_type = store_type
        self.memories: Dict[str, List[Memory]] = {
            MemoryType.WORKING: [],
            MemoryType.LONG_TERM: [],
            MemoryType.VECTOR: []
        }
    
    def remember(self, key: str, value: str, 
                 memory_type: MemoryType = MemoryType.LONG_TERM,
                 importance: float = 0.5,
                 metadata: Dict = None,
                 embeddings: List[float] = None) -> Memory:
        """存储记忆"""
        memory = Memory(
            key=key,
            value=value,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata or {},
            embeddings=embeddings
        )
        
        if key not in self.memories[memory_type]:
            self.memories[memory_type].append(memory)
        else:
            # 更新已存在的记忆
            self.memories[memory_type] = [
                m if m.key != key else memory 
                for m in self.memories[memory_type]
            ]
        
        return memory
    
    def recall(self, query: str = None, 
               memory_type: MemoryType = None,
               top_k: int = 5) -> List[Memory]:
        """检索记忆"""
        if memory_type:
            memories = self.memories[memory_type]
        else:
            # 合并所有类型的记忆
            memories = (
                self.memories[MemoryType.WORKING] +
                self.memories[MemoryType.LONG_TERM] +
                self.memories[MemoryType.VECTOR]
            )
        
        # 按重要性排序
        memories = sorted(memories, key=lambda m: m.importance, reverse=True)
        
        return memories[:top_k]
    
    def recall_by_key(self, key: str, memory_type: MemoryType = None) -> Optional[Memory]:
        """根据 key 检索"""
        if memory_type:
            memories = self.memories[memory_type]
        else:
            memories = (
                self.memories[MemoryType.WORKING] +
                self.memories[MemoryType.LONG_TERM] +
                self.memories[MemoryType.VECTOR]
            )
        
        for m in memories:
            if m.key == key:
                return m
        return None
    
    def forget(self, key: str, memory_type: MemoryType = None):
        """删除记忆"""
        if memory_type:
            self.memories[memory_type] = [
                m for m in self.memories[memory_type] if m.key != key
            ]
        else:
            for mtype in MemoryType:
                self.memories[mtype] = [
                    m for m in self.memories[mtype] if m.key != key
                ]
    
    def clear(self, memory_type: MemoryType = None):
        """清空记忆"""
        if memory_type:
            self.memories[memory_type] = []
        else:
            for mtype in MemoryType:
                self.memories[mtype] = []
    
    def get_stats(self) -> Dict:
        """获取记忆统计"""
        return {
            "working": len(self.memories[MemoryType.WORKING]),
            "long_term": len(self.memories[MemoryType.LONG_TERM]),
            "vector": len(self.memories[MemoryType.VECTOR]),
            "total": sum(len(v) for v in self.memories.values())
        }


class VectorMemoryStore(MemoryStore):
    """向量记忆存储（支持语义检索）"""
    
    def __init__(self, embedder=None):
        super().__init__("vector")
        self.embedder = embedder or self._default_embedder
    
    def _default_embedder(self, text: str) -> List[float]:
        """简单的词嵌入模拟（实际应使用真实嵌入模型）"""
        # 实际使用时替换为 OpenAI text-embedding-3-small 或其他嵌入模型
        import hashlib
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        # 返回模拟的嵌入向量
        return [(hash_val >> (i * 8)) % 256 / 255.0 for i in range(64)]
    
    def remember(self, key: str, value: str,
                 memory_type: MemoryType = MemoryType.VECTOR,
                 importance: float = 0.5,
                 metadata: Dict = None,
                 embeddings: List[float] = None) -> Memory:
        """存储带向量 embadding 的记忆"""
        if embeddings is None:
            embeddings = self.embedder(value)
        
        return super().remember(key, value, memory_type, importance, metadata, embeddings)
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Memory]:
        """语义检索"""
        query_embedding = self.embedder(query)
        
        # 计算余弦相似度
        def cosine_similarity(a: List[float], b: List[float]) -> float:
            dot_product = sum(x * y for x, y in zip(a, b))
            norm_a = sum(x * x for x in a) ** 0.5
            norm_b = sum(x * x for x in b) ** 0.5
            return dot_product / (norm_a * norm_b) if (norm_a * norm_b) > 0 else 0
        
        # 排序
        vector_memories = self.memories[MemoryType.VECTOR]
        scored = [
            (m, cosine_similarity(query_embedding, m.embeddings))
            for m in vector_memories
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [m for m, _ in scored[:top_k]]


class HybridMemoryStore:
    """混合记忆系统（整合所有类型）"""
    
    def __init__(self):
        self.working = MemoryStore("working")
        self.long_term = MemoryStore("long_term")
        self.vector = VectorMemoryStore()
    
    def remember(self, key: str, value: str, 
                importance: float = 0.5,
                metadata: Dict = None):
        """自动选择记忆类型"""
        if importance > 0.8:
            # 高重要性：同时存储到长期和向量
            self.long_term.remember(key, value, MemoryType.LONG_TERM, importance, metadata)
            self.vector.remember(key, value, MemoryType.VECTOR, importance, metadata)
        elif importance > 0.5:
            # 中等重要性：存储到长期记忆
            self.long_term.remember(key, value, MemoryType.LONG_TERM, importance, metadata)
        else:
            # 低重要性：仅工作记忆
            self.working.remember(key, value, MemoryType.WORKING, importance, metadata)
    
    def recall(self, query: str = None, top_k: int = 5) -> List[Memory]:
        """统一检索接口"""
        if query:
            # 语义检索
            return self.vector.semantic_search(query, top_k)
        else:
            # 返回所有最近记忆
            all_memories = (
                self.working.recall(top_k=top_k) +
                self.long_term.recall(top_k=top_k)
            )
            return sorted(all_memories, key=lambda m: m.timestamp, reverse=True)[:top_k]
    
    def get_context_for_agent(self, agent_name: str, max_tokens: int = 2000) -> str:
        """为智能体获取上下文"""
        memories = self.recall(top_k=10)
        
        context_parts = ["## 历史记忆\n"]
        for m in memories:
            context_parts.append(f"- **{m.key}**: {m.value[:200]}")
        
        return "\n".join(context_parts)


if __name__ == "__main__":
    # 测试
    store = HybridMemoryStore()
    
    # 存储记忆
    store.remember("project_goals", "目标是打造最好的AI协作平台", importance=0.9)
    store.remember("team_members", "团队有5个人：Alice, Bob, Carol, Dave, Eve", importance=0.7)
    store.remember("meeting_time", "每周二下午3点例会", importance=0.4)
    
    # 检索
    results = store.recall(query="项目目标")
    print("搜索结果:")
    for r in results:
        print(f"- {r.key}: {r.value}")
