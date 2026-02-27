#!/usr/bin -*- coding: utf-8 -*-
"""
AI团队并行工作流示例
市场调研 + 竞品分析 + 视觉设计 + 跨群同步
"""
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ["NVIDIA_API_KEY"] = "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"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.agent_manager import AgentManager
from scripts.memory_store import HybridMemoryStore
from scripts.swarm_intelligence import create_swarm


class CrossGroupMemory:
    """
    跨群组记忆系统
    
    多个群组共享同一记忆，确保上下文连贯
    """
    
    def __init__(self):
        self.global_memory = HybridMemoryStore()
        self.group_contexts = {}  # 群组特定上下文
        
    def remember(self, key: str, value: str, group: str = None, importance: float = 0.8):
        """跨群记忆"""
        metadata = {"group": group} if group else {}
        self.global_memory.remember(key, value, importance, metadata)
        
    def recall(self, query: str = None, group: str = None, top_k: int = 5) -> list:
        """跨群检索"""
        memories = self.global_memory.recall(query, top_k)
        
        # 过滤特定群组
        if group:
            memories = [m for m in memories if m.metadata.get("group") == group]
            
        return memories
    
    def sync_to_group(self, target_group: str, source_groups: list = None):
        """同步到目标群组"""
        # 获取所有相关记忆
        memories = self.global_memory.recall(top_k=20)
        
        # 存储到目标群上下文
        self.group_contexts[target_group] = [
            m for m in memories 
            if not source_groups or m.metadata.get("group") in source_groups
        ]
        
    def get_context(self, group: str) -> str:
        """获取群组上下文"""
        if group in self.group_contexts:
            memories = self.group_contexts[group]
        else:
            memories = self.global_memory.recall(top_k=10)
            
        if not memories:
            return "暂无历史上下文"
        
        context = "## 跨群记忆同步\n\n"
        for m in memories:
            context += f"- **{m.key}**: {m.value[:100]}...\n"
        
        return context


class AIProjectTeam:
    """
    AI项目团队
    
    并行执行多任务，跨群同步上下文
    """
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.memory = CrossGroupMemory()
        self.manager = AgentManager()
        
        # 创建专业AI团队
        self.team = self._create_team()
        
    def _create_team(self) -> dict:
        """创建专业AI团队"""
        
        agents = {
            "researcher": self.manager.create_agent(
                "市场调研员",
                "meta/llama-3.1-70b-instruct",
                "专业市场调研分析师，擅长收集数据、分析趋势、撰写报告"
            ),
            "competitor": self.manager.create_agent(
                "竞品分析师",
                "meta/llama-3.1-70b-instruct",
                "资深竞品分析专家，擅长功能对比、商业模式分析"
            ),
            "designer": self.manager.create_agent(
                "视觉设计师",
                "meta/llama-3.1-70b-instruct",
                "创意设计师，擅长视觉设计、品牌定位、UI设计"
            ),
            "writer": self.manager.create_agent(
                "文案写手",
                "meta/llama-3.1-70b-instruct",
                "专业文案，擅长产品文案、营销内容、品牌故事"
            ),
        }
        
        return agents
    
    def execute_parallel(self, tasks: list) -> dict:
        """
        并行执行任务
        
        tasks: [{"task": "任务描述", "agent": "agent_key", "context": "上下文"}]
        """
        import concurrent.futures
        
        results = {}
        
        def run_task(task):
            agent_key = task["agent"]
            agent = self.team[agent_key]
            
            # 获取上下文
            context = self.memory.get_context(task.get("group", "default"))
            
            prompt = f"""项目: {self.project_name}

{context}

任务: {task['task']}

请完成此任务，要求专业、详细。"""

            result = agent.chat(prompt)
            
            # 存储结果到记忆
            self.memory.remember(
                key=f"{agent_key}_{task['task'][:20]}",
                value=result,
                group=task.get("group", "default"),
                importance=0.9
            )
            
            return agent_key, result
        
        # 并行执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(run_task, task): task for task in tasks}
            
            for future in concurrent.futures.as_completed(futures):
                agent_key, result = future.result()
                results[agent_key] = result
        
        return results
    
    def sync_to_groups(self, target_groups: list):
        """同步到多个群组"""
        for group in target_groups:
            self.memory.sync_to_group(group)
    
    def generate_report(self) -> str:
        """生成综合报告"""
        
        # 获取所有记忆
        memories = self.memory.global_memory.recall(top_k=10)
        
        prompt = f"""项目: {self.project_name}

基于以下团队工作成果，生成一份完整的项目报告:

"""
        
        for m in memories:
            prompt += f"## {m.key}\n{m.value[:500]}...\n\n"
        
        prompt += """
请整合以上内容，生成结构清晰的项目报告。"""
        
        # 让写手生成报告
        report = self.team["writer"].chat(prompt)
        
        return report


def demo_market_research():
    """演示：AI团队并行完成市场调研项目"""
    
    print("="*70)
    print("AI项目团队演示：新产品市场调研")
    print("="*70)
    
    # 1. 创建项目团队
    team = AIProjectTeam("智能家居APP市场调研")
    
    # 2. 定义并行任务
    tasks = [
        {
            "task": "调研智能家居市场规模、增长趋势、主要玩家",
            "agent": "researcher",
            "group": "市场部"
        },
        {
            "task": "分析米家、华为HiLink、苹果HomeKit的差异",
            "agent": "competitor", 
            "group": "产品部"
        },
        {
            "task": "设计APP的视觉风格、配色方案、logo概念",
            "agent": "designer",
            "group": "设计部"
        },
    ]
    
    # 3. 并行执行
    print("\n🚀 启动AI团队并行工作...\n")
    results = team.execute_parallel(tasks)
    
    # 4. 展示结果
    print("\n" + "="*70)
    print("📊 各团队工作成果")
    print("="*70)
    
    agent_names = {
        "researcher": "【市场调研员】",
        "competitor": "【竞品分析师】", 
        "designer": "【视觉设计师】"
    }
    
    for key, result in results.items():
        print(f"\n{agent_names.get(key, key)}:")
        print("-"*50)
        print(result[:400] + "...")
    
    # 5. 跨群同步
    print("\n" + "="*70)
    print("🔄 跨群同步项目上下文")
    print("="*70)
    
    team.sync_to_groups(["市场部", "产品部", "设计部", "管理层"])
    
    print("\n已同步到群组:")
    for group in ["市场部", "产品部", "设计部", "管理层"]:
        context = team.memory.get_context(group)
        print(f"  ✓ {group}")
    
    # 6. 生成报告
    print("\n" + "="*70)
    print("📄 生成综合项目报告")
    print("="*70)
    
    report = team.generate_report()
    print("\n" + report[:800] + "...")
    
    print("\n" + "="*70)
    print("✅ 项目完成！AI团队已并行完成所有任务并同步上下文")
    print("="*70)


def demo_creative_project():
    """演示：创意项目 - 睡前故事"""
    
    print("\n\n" + "="*70)
    print("AI创意团队演示：家庭睡前故事")
    print("="*70)
    
    team = AIProjectTeam("睡前故事创作")
    
    # 家庭成员偏好
    team.memory.remember(
        "user_preferences",
        "爸爸喜欢科幻，妈妈喜欢温馨，小明(6岁)喜欢恐龙",
        importance=0.9
    )
    
    tasks = [
        {
            "task": "创作一个关于恐龙的睡前故事，要求温馨有趣",
            "agent": "writer",
            "group": "家庭群"
        },
        {
            "task": "设计故事配图风格：可爱恐龙、暖色调、童趣",
            "agent": "designer",
            "group": "家庭群"
        },
    ]
    
    results = team.execute_parallel(tasks)
    
    print("\n📖 故事创作:")
    print(results.get("writer", "")[:300] + "...")
    
    print("\n🎨 视觉设计:")
    print(results.get("designer", "")[:200] + "...")


if __name__ == "__main__":
    demo_market_research()
    demo_creative_project()
