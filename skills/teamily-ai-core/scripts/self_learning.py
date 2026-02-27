"""
Teamily AI Core - 自我学习与问题解决系统
遇到问题自动搜索学习并解决
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .agent_manager import Agent
from .memory_store import HybridMemoryStore


@dataclass
class Problem:
    """问题记录"""
    id: str
    description: str
    category: str  # technical, business, etc.
    status: str  # pending, solving, solved, failed
    attempts: List[Dict] = field(default_factory=list)
    solution: str = ""
    learned: List[str] = field(default_factory=list)


class SelfLearningSystem:
    """
    自我学习系统
    
    核心能力：
    1. 问题识别 - 分析问题类型
    2. 方案搜索 - 网上搜索解决方案
    3. 学习理解 - 理解并记录解决方案
    4. 应用解决 - 尝试解决问题
    5. 知识沉淀 - 将解决方案加入知识库
    """
    
    def __init__(self, agent: Agent = None):
        self.agent = agent
        self.memory = HybridMemoryStore()
        self.problems: Dict[str, Problem] = {}
        self.knowledge_base: Dict[str, Any] = {}
        
        # 学习配置
        self.config = {
            "max_attempts": 3,      # 最大尝试次数
            "search_depth": 5,       # 搜索深度
            "learn_from_failure": True,  # 从失败中学习
        }
    
    def set_agent(self, agent: Agent):
        """设置AI智能体"""
        self.agent = agent
    
    async def solve_problem(self, problem: str, context: Dict = None) -> Dict:
        """
        解决问题 - 核心方法
        
        自动执行：分析 → 搜索 → 学习 → 尝试 → 解决
        """
        
        # 1. 问题识别
        analysis = await self._analyze_problem(problem, context)
        
        # 2. 搜索解决方案
        solutions = await self._search_solutions(analysis, context)
        
        # 3. 学习理解
        learned = await self._learn_solutions(solutions)
        
        # 4. 应用解决
        result = await self._apply_solution(problem, learned, context)
        
        # 5. 知识沉淀
        if result["success"]:
            await self._沉淀knowledge(problem, analysis, learned, result)
        
        return result
    
    async def _analyze_problem(self, problem: str, context: Dict = None) -> Dict:
        """分析问题"""
        
        if not self.agent:
            # 无AI时返回基础分析
            return {
                "type": "general",
                "keywords": problem.split()[:5],
                "category": self._categorize(problem)
            }
        
        prompt = f"""请分析以下问题：

问题：{problem}

请从以下角度分析：
1. 问题的核心是什么？
2. 属于什么类型的问题？（技术/业务/工具/环境等）
3. 需要什么技能或工具来解决？
4. 关键词有哪些？

请用JSON格式返回分析结果。"""
        
        response = self.agent.chat(prompt)
        
        try:
            # 尝试解析JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = {"raw_analysis": response}
        except:
            analysis = {"raw_analysis": response}
        
        analysis["original_problem"] = problem
        return analysis
    
    def _categorize(self, problem: str) -> str:
        """简单问题分类"""
        problem_lower = problem.lower()
        
        if any(k in problem_lower for k in ["爬虫", "抓取", "采集", "scrape", "crawl"]):
            return "web_scraping"
        elif any(k in problem_lower for k in ["网站", "网页", "web", "html"]):
            return "web"
        elif any(k in problem_lower for k in ["api", "接口", "调用"]):
            return "api"
        elif any(k in problem_lower for k in ["安装", "配置", "环境", "install", "setup"]):
            return "environment"
        else:
            return "general"
    
    async def _search_solutions(self, analysis: Dict, context: Dict = None) -> List[Dict]:
        """搜索解决方案"""
        
        problem = analysis.get("original_problem", "")
        keywords = analysis.get("keywords", problem.split()[:5])
        
        # 构建搜索查询
        search_queries = [
            problem,
            f"how to fix {problem}",
        ]
        
        # 添加关键词搜索
        if len(keywords) >= 2:
            search_queries.append(f"{keywords[0]} {keywords[1]} solution")
        
        solutions = []
        
        # 这里需要接入搜索能力
        # 可以使用 agent-reach 或其他搜索工具
        # 暂时返回搜索查询，实际搜索由外部执行
        
        return [
            {
                "query": q,
                "source": "search",
                "status": "pending_search"
            }
            for q in search_queries[:3]
        ]
    
    async def _learn_solutions(self, solutions: List[Dict]) -> List[str]:
        """学习理解解决方案"""
        
        learned = []
        
        for sol in solutions:
            query = sol.get("query", "")
            
            if not self.agent:
                learned.append(f"需要搜索: {query}")
                continue
            
            # 让AI学习这个解决方案
            prompt = f"""请解释并总结以下问题的解决方案：

问题：{query}

请：
1. 解释问题原因
2. 提供详细的解决步骤
3. 给出代码示例（如果适用）
4. 列出注意事项

请用简洁易懂的语言解释。"""
            
            explanation = self.agent.chat(prompt)
            learned.append(explanation)
        
        return learned
    
    async def _apply_solution(self, problem: str, learned: List[str], 
                             context: Dict = None) -> Dict:
        """应用解决方案"""
        
        if not learned:
            return {
                "success": False,
                "problem": problem,
                "message": "没有找到解决方案"
            }
        
        if not self.agent:
            # 无AI时返回学习的方案
            return {
                "success": True,
                "problem": problem,
                "solutions": learned,
                "message": "已找到解决方案，请查看"
            }
        
        # 让AI根据学习的方案尝试解决问题
        solutions_text = "\n\n".join([
            f"方案{i+1}:\n{s}" for i, s in enumerate(learned)
        ])
        
        prompt = f"""原始问题：{problem}

学习到的解决方案：
{solutions_text}

请根据这些解决方案，尝试给出最终的问题解答或代码实现。
如果解决方案不完整，请说明还需要什么信息。"""
        
        result = self.agent.chat(prompt)
        
        return {
            "success": True,
            "problem": problem,
            "solution": result,
            "learned": learned
        }
    
    async def _沉淀knowledge(self, problem: str, analysis: Dict,
                            learned: List[str], result: Dict):
        """知识沉淀 - 将解决方案加入知识库"""
        
        # 提取关键信息
        key = f"problem_{hash(problem) % 100000}"
        
        knowledge = {
            "problem": problem,
            "category": analysis.get("category", "general"),
            "type": analysis.get("type", "general"),
            "keywords": analysis.get("keywords", []),
            "solution": result.get("solution", ""),
            "learned": learned,
            "timestamp": str(time.time())
        }
        
        self.knowledge_base[key] = knowledge
        
        # 存入记忆系统
        self.memory.remember(
            key=key,
            value=json.dumps(knowledge),
            importance=0.8
        )
    
    def get_knowledge(self, query: str = None) -> List[Dict]:
        """获取知识库"""
        if query:
            # 搜索知识库
            memories = self.memory.recall(query, top_k=5)
            return [json.loads(m.value) for m in memories if m.value]
        
        return list(self.knowledge_base.values())
    
    def teach(self, topic: str, knowledge: str):
        """手动教学 - 用户教AI新知识"""
        
        key = f"manual_{hash(topic) % 100000}"
        
        self.knowledge_base[key] = {
            "topic": topic,
            "knowledge": knowledge,
            "source": "manual",
            "timestamp": str(time.time())
        }
        
        self.memory.remember(
            key=key,
            value=knowledge,
            importance=0.9
        )
        
        return f"已学会: {topic}"


class AdaptiveAgent:
    """
    自适应智能体
    
    具备自我学习能力的智能体
    """
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.learning = SelfLearningSystem(agent)
    
    async def execute_task(self, task: str, context: Dict = None) -> Dict:
        """执行任务，遇到问题自动学习解决"""
        
        # 尝试直接执行
        try:
            result = self.agent.chat(task)
            return {
                "success": True,
                "result": result,
                "learned": False
            }
        except Exception as e:
            error_msg = str(e)
            
            # 遇到问题，启动自我学习
            print(f"遇到问题: {error_msg}")
            print("启动自我学习...")
            
            # 学习解决
            solution = await self.learning.solve_problem(
                f"{task} - 错误: {error_msg}",
                context
            )
            
            return {
                "success": solution.get("success", False),
                "error": error_msg,
                "solution": solution,
                "learned": True
            }
    
    def learn(self, topic: str, knowledge: str):
        """教学 - 告诉AI新知识"""
        return self.learning.teach(topic, knowledge)
    
    def get_knowledge(self, query: str = None):
        """查询知识库"""
        return self.learning.get_knowledge(query)


import time

__all__ = ["SelfLearningSystem", "AdaptiveAgent", "Problem"]
