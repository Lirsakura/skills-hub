#!/usr/bin/env python
"""
Teamily AI Core - 使用示例
演示多智能体协作的各种场景
"""

import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.agent_manager import Agent, AgentConfig, AgentManager
from scripts.memory_store import HybridMemoryStore
from scripts.group_manager import Group, CollaborationStrategy
from scripts.rag_engine import RAGEngine


def example_basic_agent():
    """示例1: 基础智能体"""
    print("\n=== 示例1: 基础智能体 ===")
    
    manager = AgentManager()
    
    # 创建智能体
    agent = manager.create_agent(
        name="Assistant",
        model="claude-sonnet-4-20250514",
        role="你是一个有帮助的AI助手"
    )
    
    # 对话
    response = agent.chat("你好！请介绍一下自己")
    print(f"Agent: {response[:200]}...")


def example_group_chat():
    """示例2: 群组聊天"""
    print("\n=== 示例2: 群组聊天 ===")
    
    # 创建群组
    group = Group(name="产品讨论组", members=["Alice", "Bob"])
    
    # 添加智能体
    manager = AgentManager()
    tech_agent = manager.create_agent(
        name="TechExpert",
        model="gpt-4o",
        role="技术专家，负责技术方案评估"
    )
    business_agent = manager.create_agent(
        name="BusinessExpert", 
        model="claude-sonnet-4-20250514",
        role="业务专家，负责商业模式分析"
    )
    
    group.add_agent(tech_agent)
    group.add_agent(business_agent)
    
    # 添加人类消息
    group.add_message("Alice", "我们来讨论一下新产品设计方案")
    
    # 发起讨论
    result = group.discuss(
        topic="移动端 vs Web端：先做哪个平台？",
        context={"资源": "5人团队", "时间": "3个月"}
    )
    
    print(f"讨论主题: {result.topic}")
    for msg in result.messages:
        print(f"  {msg['agent']}: {msg['response'][:100]}...")


def example_task_assignment():
    """示例3: 任务分配"""
    print("\n=== 示例3: 任务分配 ===")
    
    manager = AgentManager()
    researcher = manager.create_agent("Researcher", "claude-sonnet-4-20250514", "调研专家")
    writer = manager.create_agent("Writer", "gpt-4o", "写作专家")
    
    group = Group(name="内容团队", members=["Tom"])
    group.add_agent(researcher)
    group.add_agent(writer)
    
    # 顺序执行
    result = group.assign_task(
        goal="完成AI行业趋势报告",
        agents=[researcher, writer],
        strategy=CollaborationStrategy.SEQUENTIAL
    )
    
    print(f"策略: {result.strategy}")
    for r in result.results:
        print(f"  {r['agent']}: 完成")


def example_memory():
    """示例4: 记忆系统"""
    print("\n=== 示例4: 记忆系统 ===")
    
    memory = HybridMemoryStore()
    
    # 存储记忆
    memory.remember("project_name", "Teamily AI", importance=0.9)
    memory.remember("team_size", "5人", importance=0.6)
    memory.remember("meeting_notes", "每周二下午3点例会", importance=0.3)
    
    # 检索
    results = memory.recall(query="项目信息")
    print(f"检索到 {len(results)} 条记忆:")
    for r in results:
        print(f"  - {r.key}: {r.value}")


def example_rag():
    """示例5: RAG 知识检索"""
    print("\n=== 示例5: RAG 知识检索 ===")
    
    rag = RAGEngine()
    
    # 添加知识文档
    rag.add_document(
        "Teamily AI 是一个人类-AI协作平台，支持多智能体在群组中协同工作。",
        metadata={"source": "产品文档", "topic": "产品介绍"}
    )
    
    rag.add_document(
        "平台支持三种协作模式：顺序、并行和讨论模式。",
        metadata={"source": "产品文档", "topic": "功能"}
    )
    
    rag.add_document(
        "记忆系统包括短期、长期和向量三种类型。",
        metadata={"source": "技术文档", "topic": "架构"}
    )
    
    # 检索
    results = rag.search("Teamily AI 有什么功能？")
    print(f"检索到 {len(results)} 条结果:")
    for r in results:
        print(f"  相关度: {r['score']:.2f}")
        print(f"  内容: {r['content']}")


def example_full_workflow():
    """示例6: 完整工作流"""
    print("\n=== 示例6: 完整工作流 ===")
    
    # 初始化
    manager = AgentManager()
    memory = HybridMemoryStore()
    rag = RAGEngine()
    
    # 创建知识库
    rag.add_document(
        "2024年新能源汽车销量同比增长35%，达到950万辆。",
        metadata={"source": "report_2024", "topic": "市场"}
    )
    
    # 创建智能体
    researcher = manager.create_agent(
        name="Researcher",
        model="claude-sonnet-4-20250514", 
        role="专业研究员，擅长数据分析"
    )
    writer = manager.create_agent(
        name="Writer",
        model="gpt-4o",
        role="专业作家，擅长商业写作"
    )
    
    # 创建群组
    group = Group(name="市场分析组", members=["产品经理"])
    group.add_agent(researcher)
    group.add_agent(writer)
    
    # 存储项目背景
    memory.remember("project", "年度市场分析报告", importance=0.9)
    
    # 任务分配 - 顺序执行
    task_result = group.assign_task(
        goal="完成新能源汽车市场分析报告",
        agents=[researcher, writer],
        strategy=CollaborationStrategy.SEQUENTIAL
    )
    
    print("任务完成!")
    print(f"执行策略: {task_result.strategy}")


def main():
    """运行所有示例"""
    print("Teamily AI Core 使用示例")
    print("=" * 50)
    
    # 设置 API Key (请替换为真实的)
    # os.environ["ANTHROPIC_API_KEY"] = "your-key"
    # os.environ["OPENAI_API_KEY"] = "your-key"
    
    # 运行示例 (注释掉需要 API 的示例)
    example_memory()
    example_rag()
    
    # 以下示例需要真实的 API Key
    # example_basic_agent()
    # example_group_chat()
    # example_task_assignment()
    # example_full_workflow()
    
    print("\n" + "=" * 50)
    print("示例完成!")


if __name__ == "__main__":
    main()
