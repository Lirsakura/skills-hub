"""
Teamily AI Core - 群体智能协作引擎
通过多人+多AI的迭代协作产生复利效应
"""

import time
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field

from .agent_manager import Agent
from .memory_store import HybridMemoryStore
from .group_manager import Group


@dataclass
class Thought:
    """思考节点"""
    author: str
    content: str
    timestamp: float = field(default_factory=time.time)
    parent: Optional[str] = None  # 父思考 ID
    metadata: Dict = field(default_factory=dict)


class SwarmIntelligence:
    """
    群体智能引擎
    
    核心思想：通过多轮迭代让 AI 互相评论、改进，
    产生 1+1>2 的复利效应
    """
    
    def __init__(self, name: str):
        self.name = name
        self.agents: List[Agent] = []
        self.humans: List[str] = []
        self.memory = HybridMemoryStore()
        self.thoughts: List[Thought] = []
        
        # 协作配置
        self.config = {
            "max_rounds": 5,           # 最大讨论轮数
            "critique_enabled": True,  # 启用批评
            "build_on_others": True,   # 基于他人观点改进
            "consensus_threshold": 0.7  # 共识阈值
        }
    
    def add_agent(self, agent: Agent):
        """添加 AI 智能体"""
        self.agents.append(agent)
    
    def add_human(self, name: str):
        """添加人类参与者"""
        self.humans.append(name)
    
    def _build_system_prompt(self, role: str, others_context: str = "") -> str:
        """构建系统提示"""
        base = f"""你是 {role}。
团队成员: {[a.config.name for a in self.agents]}
人类成员: {self.humans}

团队目标: 通过协作产生最佳解决方案。"""
        
        if others_context:
            base += f"""

其他成员的观点:
{others_context}

请在回复中回应或引用他人的观点。"""
        
        return base
    
    def collaborative_think(self, 
                           problem: str,
                           strategy: str = "debate") -> Dict:
        """
        协作思考 - 核心方法
        
        策略:
        - debate: 辩论式 (各抒己见)
        - iterative: 迭代式 (基于他人改进)
        - critique: 评审式 (产出+批评+改进)
        """
        
        if strategy == "debate":
            return self._debate(problem)
        elif strategy == "iterative":
            return self._iterative(problem)
        elif strategy == "critique":
            return self._critique_loop(problem)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _debate(self, problem: str) -> Dict:
        """辩论式 - 各抒己见，最后汇总"""
        
        # 存储问题
        self.memory.remember(
            key=f"problem_{int(time.time())}",
            value=problem,
            importance=0.9
        )
        
        responses = []
        
        # 每个 AI 独立发表观点
        for agent in self.agents:
            prompt = f"""问题: {problem}

请从你的专业角度分析这个问题，提出你的观点和解决方案。
注意：你不需要与他人一致，保持独立思考。"""
            
            response = agent.chat(prompt)
            responses.append({
                "author": agent.config.name,
                "role": agent.config.role,
                "response": response
            })
            
            # 存储思考
            thought = Thought(
                author=agent.config.name,
                content=response,
                metadata={"problem": problem, "strategy": "debate"}
            )
            self.thoughts.append(thought)
        
        # 汇总
        summary = self._summarize(responses, problem)
        
        return {
            "strategy": "debate",
            "problem": problem,
            "responses": responses,
            "summary": summary
        }
    
    def _iterative(self, problem: str, max_rounds: int = None) -> Dict:
        """迭代式 - 多轮讨论，基于他人观点改进"""
        
        max_rounds = max_rounds or self.config["max_rounds"]
        all_responses = []
        
        for round_num in range(max_rounds):
            round_responses = []
            others_context = self._build_context(all_responses)
            
            for agent in self.agents:
                # 构建基于上下文的提示
                prompt = f"""问题: {problem}

这是第 {round_num + 1} 轮讨论。

{others_context}

请基于以上讨论，提出你的观点或改进他人的想法。
如果同意某人观点，可以 building on it。
如果不同意，说明理由并提出替代方案。"""
                
                response = agent.chat(prompt)
                round_responses.append({
                    "round": round_num + 1,
                    "author": agent.config.name,
                    "response": response
                })
                
                # 存储
                thought = Thought(
                    author=agent.config.name,
                    content=response,
                    parent=f"round_{round_num}",
                    metadata={"problem": problem, "round": round_num}
                )
                self.thoughts.append(thought)
            
            all_responses.extend(round_responses)
            
            # 检查是否已达成共识
            if self._check_convergence(all_responses):
                break
        
        summary = self._summarize(
            [{"author": r["author"], "response": r["response"]} 
             for r in all_responses],
            problem
        )
        
        return {
            "strategy": "iterative",
            "problem": problem,
            "rounds": max_rounds,
            "responses": all_responses,
            "summary": summary,
            "converged": self._check_convergence(all_responses)
        }
    
    def _critique_loop(self, problem: str) -> Dict:
        """评审式 - 产出 → 批评 → 改进 → 迭代"""
        
        best_response = None
        best_score = 0
        all_iterations = []
        
        for iteration in range(3):  # 3 轮评审
            iteration_results = []
            
            # 阶段 1: 产出方案
            for agent in self.agents:
                context = ""
                if best_response:
                    context = f"""

当前最佳方案:
{best_response}

请基于这个方案改进，或提出更好的替代方案。"""
                
                prompt = f"""任务: {problem}

{context}

请提出你的解决方案。"""
                
                response = agent.chat(prompt)
                iteration_results.append({
                    "stage": "proposal",
                    "author": agent.config.name,
                    "response": response
                })
            
            # 阶段 2: 互相批评 (如果启用)
            if self.config["critique_enabled"]:
                for agent in self.agents:
                    # 获取其他人的方案
                    others = [r for r in iteration_results 
                             if r["author"] != agent.config.name]
                    others_text = "\n\n".join([
                        f"{r['author']}: {r['response'][:300]}..."
                        for r in others
                    ])
                    
                    prompt = f"""请批评以下方案，提出优缺点:

{others_text}

请给出建设性的改进建议。"""
                    
                    critique = agent.chat(prompt)
                    iteration_results.append({
                        "stage": "critique",
                        "author": agent.config.name,
                        "response": critique
                    })
            
            all_iterations.append(iteration_results)
            
            # 选择最佳方案
            if iteration_results:
                # 让最后一个 agent 选择最佳
                selector = self.agents[-1]
                options = "\n\n".join([
                    f"{r['author']}: {r['response'][:200]}..."
                    for r in iteration_results 
                    if r["stage"] == "proposal"
                ])
                
                prompt = f"""从以下方案中选择最佳的一个，只返回方案内容:

{options}"""

                best_response = selector.chat(prompt)
        
        return {
            "strategy": "critique",
            "problem": problem,
            "iterations": all_iterations,
            "best_response": best_response
        }
    
    def _build_context(self, previous_responses: List[Dict]) -> str:
        """构建上下文"""
        if not previous_responses:
            return ""
        
        context = "之前讨论:\n"
        for r in previous_responses[-10:]:  # 只取最近10条
            context += f"\n[{r.get('author', 'Unknown')}]: {r.get('response', '')[:200]}..."
        
        return context
    
    def _summarize(self, responses: List[Dict], problem: str) -> str:
        """汇总所有观点"""
        
        if not self.agents:
            return "No agents available"
        
        # 让一个 agent 做总结
        summarizer = self.agents[0]
        
        all_views = "\n\n".join([
            f"{r['author']}: {r['response'][:300]}..."
            for r in responses
        ])
        
        prompt = f"""问题: {problem}

以下是团队成员的观点:

{all_views}

请总结各方观点，找出共识和分歧，并提出一个综合方案。"""
        
        return summarizer.chat(prompt)
    
    def _check_convergence(self, responses: List[Dict], 
                          threshold: float = None) -> bool:
        """检查是否达成共识"""
        
        threshold = threshold or self.config["consensus_threshold"]
        
        # 简化版：检查最近几轮观点是否相似
        if len(responses) < 4:
            return False
        
        recent = responses[-4:]
        if len(set(r["author"] for r in recent)) < 2:
            return False
        
        # TODO: 实际应该用 embedding 相似度
        return False
    
    def get_wisdom(self) -> str:
        """获取群体智慧 - 基于所有历史讨论"""
        
        if not self.thoughts:
            return "还没有产生任何思考"
        
        # 获取最近的思考
        recent = self.thoughts[-20:]
        
        context = "## 群体思考历史\n\n"
        for thought in recent:
            context += f"**{thought.author}**: {thought.content[:150]}...\n\n"
        
        # 让一个 agent 总结智慧
        if self.agents:
            prompt = f"""基于以下群体讨论，总结核心洞见:

{context}

请用 200 字总结关键结论和洞见。"""
            
            return self.agents[0].chat(prompt)
        
        return context
    
    def human_join(self, name: str, message: str):
        """人类加入讨论"""
        thought = Thought(
            author=name,
            content=message,
            metadata={"type": "human"}
        )
        self.thoughts.append(thought)
        
        # 让 AI 回应人类
        if self.agents:
            context = self._build_context([
                {"author": t.author, "response": t.content}
                for t in self.thoughts[-10:]
            ])
            
            for agent in self.agents:
                prompt = f"""人类 {name} 发言: {message}

团队讨论上下文:
{context}

请回应人类的发言。"""
                
                response = agent.chat(prompt)
                
                thought = Thought(
                    author=agent.config.name,
                    content=response,
                    metadata={"type": "response_to_human", "human": name}
                )
                self.thoughts.append(thought)


# 便捷函数
def create_swarm(name: str, 
                agents: List[tuple],  # [(name, model, role), ...]
                humans: List[str] = None) -> SwarmIntelligence:
    """
    快速创建群体智能
    
    Example:
        swarm = create_swarm(
            "产品团队",
            [
                ("技术专家", "meta/llama-3.1-70b-instruct", "技术架构师"),
                ("产品经理", "meta/llama-3.1-70b-instruct", "产品策略专家"),
                ("设计师", "meta/llama-3.1-70b-instruct", "用户体验设计师")
            ],
            ["张三", "李四"]
        )
    """
    from .agent_manager import AgentManager
    
    swarm = SwarmIntelligence(name)
    manager = AgentManager()
    
    for name, model, role in agents:
        agent = manager.create_agent(name, model, role)
        swarm.add_agent(agent)
    
    if humans:
        for h in humans:
            swarm.add_human(h)
    
    return swarm


__all__ = ["SwarmIntelligence", "Thought", "create_swarm"]
