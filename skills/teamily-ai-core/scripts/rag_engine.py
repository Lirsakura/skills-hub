"""
Teamily AI Core - RAG Engine
RAG 知识检索增强生成引擎
"""

import os
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import hashlib

class EmbeddingModel(Enum):
    OPENAI_ADA = "text-embedding-3-small"
    CLAUDE = "claude-embedding"  # 需要额外配置

@dataclass
class Document:
    id: str
    content: str
    metadata: Dict
    embedding: Optional[List[float]] = None

class RAGEngine:
    """RAG 知识检索引擎"""
    
    def __init__(self, 
                 embedding_model: str = "text-embedding-3-small",
                 chunk_size: int = 500,
                 chunk_overlap: int = 50):
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.documents: Dict[str, Document] = {}
        self.chunks: List[Document] = []
    
    def _get_embedding(self, text: str) -> List[float]:
        """获取文本嵌入向量"""
        try:
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
            response = openai.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            # 降级：返回简单 hash
            return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str) -> List[float]:
        """简单的文本嵌入（降级方案）"""
        hash_val = int(hashlib.sha256(text.encode()).hexdigest(), 16)
        return [(hash_val >> (i * 8)) % 256 / 255.0 for i in range(64)]
    
    def _chunk_text(self, text: str) -> List[str]:
        """将文本分块"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # 尝试在句子边界分割
            if end < len(text):
                for sep in ['。', '！', '？', '\n', '. ', '! ', '? ']:
                    last_sep = text.rfind(sep, start, end)
                    if last_sep > start:
                        end = last_sep + 1
                        break
            
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
        
        return chunks
    
    def add_document(self, content: str, metadata: Dict = None) -> str:
        """添加文档"""
        doc_id = hashlib.md5(content.encode()).hexdigest()[:16]
        
        # 如果文档已存在，更新
        if doc_id in self.documents:
            return doc_id
        
        document = Document(
            id=doc_id,
            content=content,
            metadata=metadata or {}
        )
        self.documents[doc_id] = document
        
        # 分块并添加
        chunks = self._chunk_text(content)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{i}"
            chunk_doc = Document(
                id=chunk_id,
                content=chunk,
                metadata={**metadata, "parent_doc": doc_id, "chunk_index": i},
                embedding=self._get_embedding(chunk)
            )
            self.chunks.append(chunk_doc)
        
        return doc_id
    
    def add_documents(self, documents: List[Dict]) -> List[str]:
        """批量添加文档"""
        return [self.add_document(doc["content"], doc.get("metadata", {})) 
                for doc in documents]
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """语义检索"""
        query_embedding = self._get_embedding(query)
        
        # 计算相似度
        def cosine_similarity(a: List[float], b: List[float]) -> float:
            dot_product = sum(x * y for x, y in zip(a, b))
            norm_a = sum(x * x for x in a) ** 0.5
            norm_b = sum(x * x for x in b) ** 0.5
            return dot_product / (norm_a * norm_b) if (norm_a * norm_b) > 0 else 0
        
        # 排序
        scored = [
            (chunk, cosine_similarity(query_embedding, chunk.embedding))
            for chunk in self.chunks
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # 返回 top_k
        return [
            {
                "content": chunk.content,
                "score": score,
                "metadata": chunk.metadata
            }
            for chunk, score in scored[:top_k]
        ]
    
    def get_context(self, query: str, max_tokens: int = 2000) -> str:
        """获取检索到的上下文"""
        results = self.search(query, top_k=5)
        
        context_parts = ["## 知识库检索结果\n"]
        for r in results:
            context_parts.append(
                f"**相关度: {r['score']:.2f}**\n{r['content']}\n"
            )
        
        return "\n".join(context_parts)
    
    def answer(self, query: str, llm_func: callable) -> str:
        """RAG + LLM 回答"""
        context = self.get_context(query)
        
        prompt = f"""基于以下知识库内容回答问题。如果知识库中没有相关信息，请说明不知道。

知识库内容:
{context}

问题: {query}

回答:"""
        
        return llm_func(prompt)
    
    def delete_document(self, doc_id: str):
        """删除文档"""
        if doc_id in self.documents:
            del self.documents[doc_id]
        
        # 删除关联的 chunks
        self.chunks = [
            c for c in self.chunks 
            if c.metadata.get("parent_doc") != doc_id
        ]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_documents": len(self.documents),
            "total_chunks": len(self.chunks),
            "chunk_size": self.chunk_size
        }


class MultiSourceRAG(RAGEngine):
    """多源 RAG 系统"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sources: Dict[str, RAGEngine] = {}
    
    def create_source(self, name: str, **kwargs) -> RAGEngine:
        """创建独立知识源"""
        source = RAGEngine(**kwargs)
        self.sources[name] = source
        return source
    
    def search_all(self, query: str, top_k: int = 3) -> Dict[str, List[Dict]]:
        """在所有源中搜索"""
        results = {}
        for name, source in self.sources.items():
            results[name] = source.search(query, top_k)
        return results
    
    def search_source(self, source: str, query: str, top_k: int = 5) -> List[Dict]:
        """在指定源中搜索"""
        if source in self.sources:
            return self.sources[source].search(query, top_k)
        return []


if __name__ == "__main__":
    # 测试
    rag = RAGEngine()
    
    # 添加文档
    rag.add_document(
        "人工智能是计算机科学的一个分支，致力于开发能够执行通常需要人类智能的任务的系统，包括视觉感知、语音识别、决策制定和语言翻译等。",
        metadata={"source": "wiki", "topic": "AI"}
    )
    
    rag.add_document(
        "机器学习是人工智能的一个子集，专注于开发能够从数据中学习并改进性能的算法。深度学习是机器学习的一个分支，使用多层神经网络。",
        metadata={"source": "wiki", "topic": "ML"}
    )
    
    # 搜索
    results = rag.search("什么是人工智能？")
    print("搜索结果:")
    for r in results:
        print(f"- 相关度: {r['score']:.2f}")
        print(f"  内容: {r['content'][:50]}...")
