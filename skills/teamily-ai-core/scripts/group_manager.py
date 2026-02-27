"""
Teamily AI Core - Group Manager
群组协作管理系统
"""

import time
import uuid
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

from .agent_manager import Agent, AgentManager
from .memory_store import HybridMemoryStore, MemoryType

class CollaborationStrategy(Enum):
    SEQUENTIAL = "sequential"   # 顺序执行
    PARALLEL = "parallel"       # 并行执行
    DISCUSSION = "discussion"    # 讨论模式

@dataclass
class Message:
    id: str
    author: str
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)

@dataclass
class Task:
    id: str
    description: str
    assignee: Agent
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Any = None
    dependencies: List[str] = field(default_factory=list)

class Group:
    """协作群组"""
    
    def __init__(self, name: str, members: List[str] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.human_members = members or []
        
        self.agents = AgentManager()
        self.memory = HybridMemoryStore()
        
        self.messages: List[Message] = []
        self.tasks: Dict[str, Task] = {}
        
        self.event_handlers: Dict[str, List[Callable]] = {
            "message": [],
            "task_complete": [],
            "task_failed": []
        }
    
    def add_agent(self, agent: Agent):
        """添加 AI 智能体"""
        self.agents.agents[agent.config.name] = agent
    
    def remove_agent(self, name: str):
        """移除智能体"""
        if name in self.agents.agents:
            del self.agents.agents[name]
    
    def on(self, event: str, handler: Callable):
        """注册事件处理器"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def _emit(self, event: str, *args, **kwargs):
        """触发事件"""
        for handler in self.event_handlers.get(event, []):
            try:
                handler(*args, **kwargs)
            except Exception as e:
                print(f"Event handler error: {e}")
    
    def add_message(self, author: str, content: str, metadata: Dict = None):
        """添加消息"""
        msg = Message(
            id=str(uuid.uuid4()),
            author=author,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(msg)
        
        # 存储到记忆
        self.memory.remember(
            key=f"msg_{msg.id[:8]}",
            value=f"{author}: {content}",
            importance=0.3
        )
        
        self._emit("message", msg)
        return msg
    
    def discuss(self, topic: str, context: Dict = None) -> 'DiscussionResult':
        """发起讨论"""
        # 构建上下文
        context_str = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        history = self._get_conversation_history()
        
        results = []
        
        # 让每个智能体参与讨论
        for agent in self.agents.list_agents():
            prompt = f"""讨论主题: {topic}
{context_str}

历史对话:
{history}

请作为 {agent.config.name}（{agent.config.role}）参与讨论，发表你的观点。"""
            
            response = agent.chat(prompt)
            results.append({
                "agent": agent.config.name,
                "response": response
            })
            
            # 添加到群聊
            self.add_message(agent.config.name, response)
        
        return DiscussionResult(topic=topic, messages=results)
    
    def discuss_until_consensus(self, topic: str, 
                                max_rounds: int = 5) -> str:
        """多轮讨论直到达成共识"""
        context = {"topic": topic}
        
        for round_num in range(max_rounds):
            # 收集所有智能体的观点
            responses = []
            for agent in self.agents.list_agents():
                history = self._get_conversation_history()
                prompt = f"""讨论主题: {topic}

当前是第 {round_num + 1} 轮讨论。
历史对话:
{history}

请作为 {agent.config.name} 发表观点，并尝试总结当前共识或分歧。"""
                
                response = agent.chat(prompt)
                responses.append(response)
                self.add_message(agent.config.name, response)
            
            # 检查是否达成共识（简化版：检查是否有相似的总结）
            if self._check_consensus(responses):
                return f"在第 {round_num + 1} 轮达成共识"
        
        return f"未能在 {max_rounds} 轮内达成共识"
    
    def _check_consensus(self, responses: List[str]) -> bool:
        """简单的一致性检查"""
        # TODO: 实现更复杂的共识检测
        return False
    
    def assign_task(self, goal: str, 
                   agents: List[Agent] = None,
                   strategy: CollaborationStrategy = CollaborationStrategy.SEQUENTIAL) -> 'TaskResult':
        """分配任务"""
        if agents is None:
            agents = self.agents.list_agents()
        
        if strategy == CollaborationStrategy.SEQUENTIAL:
            return self._assign_sequential(goal, agents)
        elif strategy == CollaborationStrategy.PARALLEL:
            return self._assign_parallel(goal, agents)
        else:
            return self._assign_discussion(goal, agents)
    
    def _assign_sequential(self, goal: str, agents: List[Agent]) -> 'TaskResult':
        """顺序执行任务"""
        results = []
        shared_context = {"goal": goal}
        
        for agent in agents:
            prompt = f"""任务目标: {goal}

之前的任务结果:
{shared_context}

请作为 {agent.config.name}（{agent.config.role}）执行你的部分任务。"""
            
            result = agent.chat(prompt)
            results.append({"agent": agent.config.name, "result": result})
            
            shared_context[agent.config.name] = result
            
            # 创建任务记录
            task = Task(
                id=str(uuid.uuid4()),
                description=goal,
                assignee=agent,
                status="completed",
                result=result
            )
            self.tasks[task.id] = task
            self._emit("task_complete", task)
        
        return TaskResult(strategy="sequential", results=results)
    
    def _assign_parallel(self, goal: str, agents: List[Agent]) -> 'TaskResult':
        """并行执行任务"""
        # 简化版：实际应使用并发
        results = []
        
        for agent in agents:
            prompt = f"""任务目标: {goal}

请作为 {agent.config.name}（{agent.config.role}）独立完成这个任务。"""
            
            result = agent.chat(prompt)
            results.append({"agent": agent.config.name, "result": result})
            
            task = Task(
                id=str(uuid.uuid4()),
                description=goal,
                assignee=agent,
                status="completed",
                result=result
            )
            self.tasks[task.id] = task
            self._emit("task_complete", task)
        
        return TaskResult(strategy="parallel", results=results)
    
    def _assign_discussion(self, goal: str, agents: List[Agent]) -> 'TaskResult':
        """讨论模式分配任务"""
        # 先讨论，再执行
        discussion_result = self.discuss(f"如何完成: {goal}")
        
        # 汇总讨论结果
        summary_prompt = f"""任务目标: {goal}

讨论内容:
{discussion_result}

请总结出一个可行的执行方案。"""
        
        # 让第一个智能体总结
        if agents:
            summary = agents[0].chat(summary_prompt)
        else:
            summary = "No agents available"
        
        return TaskResult(strategy="discussion", 
                         results=[{"summary": summary}])
    
    def _get_conversation_history(self, max_messages: int = 10) -> str:
        """获取对话历史"""
        recent = self.messages[-max_messages:]
        return "\n".join([
            f"{msg.author}: {msg.content}"
            for msg in recent
        ])
    
    def get_context(self, for_agent: str = None) -> str:
        """获取智能体上下文"""
        memory_context = self.memory.get_context_for_agent(for_agent or "agent")
        history = self._get_conversation_history()
        
        return f"""## 群组信息
群组名称: {self.name}
成员: {', '.join(self.human_members)}
AI智能体: {', '.join(a.config.name for a in self.agents.list_agents())}

{memory_context}

## 当前对话
{history}
"""


@dataclass
class DiscussionResult:
    topic: str
    messages: List[Dict]


@dataclass
class TaskResult:
    strategy: str
    results: List[Dict]


# 导出
__all__ = [
    "Group",
    "Message", 
    "Task",
    "DiscussionResult",
    "TaskResult",
    "CollaborationStrategy"
]
