#!/usr/bin/env python
"""
测试 Teamily AI Core - 需要 API Key
"""
import os
import sys

# 设置你的 API Key (直接在这里填写或使用环境变量)
os.environ["NVIDIA_API_KEY"] = "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"
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.agent_manager import AgentManager
from scripts.group_manager import Group, CollaborationStrategy


def test_agent():
    """测试智能体"""
    print("\n=== 测试智能体 ===")
    
    if not os.environ.get("NVIDIA_API_KEY"):
        print("⚠️  缺少 API Key")
        return
    
    manager = AgentManager()
    
    # 使用 NVIDIA 模型
    agent = manager.create_agent(
        name="Assistant",
        model="meta/llama-3.1-70b-instruct",
        role="你是一个专业的AI助手"
    )
    
    response = agent.chat("你好！用一句话介绍自己")
    print(f"Agent: {response}")


def test_group_discuss():
    """测试群组讨论"""
    print("\n=== 测试群组讨论 ===")
    
    if not os.environ.get("NVIDIA_API_KEY"):
        print("⚠️  缺少 API Key")
        return
    
    manager = AgentManager()
    
    # 使用 NVIDIA 模型
    tech = manager.create_agent(
        name="技术专家",
        model="meta/llama-3.1-70b-instruct",
        role="技术专家，擅长分析技术方案的优缺点"
    )
    
    business = manager.create_agent(
        name="业务专家", 
        model="meta/llama-3.1-70b-instruct",
        role="业务专家，擅长分析市场需求和商业模式"
    )
    
    # 创建群组
    group = Group(name="产品讨论组", members=["产品经理"])
    group.add_agent(tech)
    group.add_agent(business)
    
    # 添加人类消息
    group.add_message("产品经理", "我们来讨论一下新产品应该先做移动端还是Web端")
    
    # 发起讨论
    result = group.discuss(
        topic="移动端 vs Web端：先做哪个平台？",
        context={"团队": "5人", "时间": "3个月"}
    )
    
    print(f"讨论主题: {result.topic}")
    for msg in result.messages:
        print(f"\n【{msg['agent']}】:")
        print(f"  {msg['response'][:300]}...")


def test_task_assignment():
    """测试任务分配"""
    print("\n=== 测试任务分配 ===")
    
    if not os.environ.get("NVIDIA_API_KEY"):
        print("⚠️  缺少 API Key")
        return
    
    manager = AgentManager()
    
    # 使用较小的模型加快测试
    researcher = manager.create_agent(
        name="调研员",
        model="meta/llama-3.1-8b-instruct",
        role="专业研究员，擅长收集和分析信息"
    )
    
    writer = manager.create_agent(
        name="写手",
        model="meta/llama-3.1-8b-instruct",
        role="专业作家，擅长撰写清晰易懂的文档"
    )
    
    group = Group(name="内容团队", members=["组长"])
    group.add_agent(researcher)
    group.add_agent(writer)
    
    # 顺序执行任务
    result = group.assign_task(
        goal="用100字介绍什么是AI",
        agents=[researcher, writer],
        strategy=CollaborationStrategy.SEQUENTIAL
    )
    
    print(f"策略: {result.strategy}")
    for r in result.results:
        print(f"\n【{r['agent']}】输出:")
        print(f"  {r['result'][:200]}...")


if __name__ == "__main__":
    print("=" * 50)
    print("Teamily AI Core API 测试")
    print("=" * 50)
    
    test_agent()
    test_group_discuss()  
    test_task_assignment()
    
    print("\n" + "=" * 50)
    print("测试完成!")
