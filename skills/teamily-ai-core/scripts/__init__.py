"""
Teamily AI Core
多智能体协作核心能力包
"""

from .agent_manager import Agent, AgentConfig, AgentManager, ModelProvider
from .memory_store import Memory, MemoryStore, VectorMemoryStore, HybridMemoryStore, MemoryType
from .group_manager import Group, Message, Task, DiscussionResult, TaskResult, CollaborationStrategy
from .rag_engine import RAGEngine, MultiSourceRAG, Document

__version__ = "0.1.0"

__all__ = [
    # Agent
    "Agent",
    "AgentConfig", 
    "AgentManager",
    "ModelProvider",
    # Memory
    "Memory",
    "MemoryStore",
    "VectorMemoryStore", 
    "HybridMemoryStore",
    "MemoryType",
    # Group
    "Group",
    "Message",
    "Task",
    "DiscussionResult",
    "TaskResult",
    "CollaborationStrategy",
    # RAG
    "RAGEngine",
    "MultiSourceRAG",
    "Document"
]
