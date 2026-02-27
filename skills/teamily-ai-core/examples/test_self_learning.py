#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自我学习系统演示
遇到问题自动搜索学习并解决
"""
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ["NVIDIA_API_KEY"] = "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"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_self_learning():
    """测试自我学习系统"""
    print("="*60)
    print("自我学习系统测试")
    print("="*60)
    
    from scripts.agent_manager import AgentManager
    from scripts.self_learning import SelfLearningSystem, AdaptiveAgent
    
    # 1. 创建AI智能体
    manager = AgentManager()
    agent = manager.create_agent(
        "学习助手",
        "meta/llama-3.1-70b-instruct",
        "专业的AI助手，擅长学习和解决问题"
    )
    
    # 2. 创建自我学习系统
    learning = SelfLearningSystem(agent)
    
    # 3. 模拟问题场景
    print("\n📚 场景1: 学习如何抓取动态加载的网页")
    print("-"*60)
    
    problem = "如何抓取内蒙古政府采购网这种动态加载的Vue.js网站？"
    
    print(f"\n问题: {problem}")
    print("\n🔍 分析问题...")
    
    # 分析问题
    analysis = await learning._analyze_problem(problem)
    print(f"分析结果: {analysis.get('type', 'unknown')} 类型")
    print(f"关键词: {analysis.get('keywords', [])}")
    
    print("\n📖 学习解决方案...")
    
    # 搜索和学习
    solutions = await learning._search_solutions(analysis)
    learned = await learning._learn_solutions(solutions)
    
    print(f"\n学到了 {len(learned)} 个解决方案")
    
    # 应用
    print("\n💡 应用解决方案...")
    result = await learning._apply_solution(problem, learned)
    
    if result.get("success"):
        print("\n✅ 问题解决:")
        print("-"*60)
        print(result.get("solution", "")[:1000])
    
    # 4. 知识沉淀
    print("\n\n💾 知识沉淀...")
    await learning._沉淀knowledge(problem, analysis, learned, result)
    print("已保存到知识库")
    
    # 5. 查询知识库
    print("\n📚 查询知识库:")
    knowledge = learning.get_knowledge("动态网页")
    print(f"找到 {len(knowledge)} 条相关知识")
    
    print("\n" + "="*60)
    print("测试完成!")
    print("="*60)


async def test_adaptive_agent():
    """测试自适应智能体"""
    print("\n\n" + "="*60)
    print("自适应智能体测试")
    print("="*60)
    
    from scripts.agent_manager import AgentManager
    from scripts.self_learning import AdaptiveAgent
    
    # 创建智能体
    manager = AgentManager()
    agent = manager.create_agent(
        "助手",
        "meta/llama-3.1-70b-instruct",
        "AI助手"
    )
    
    # 创建自适应智能体
    adaptive = AdaptiveAgent(agent)
    
    # 尝试执行任务
    print("\n🚀 执行任务...")
    result = await adaptive.execute_task("你好，请介绍一下自己")
    
    if result.get("success"):
        print("\n✅ 任务成功:")
        print(result.get("result", "")[:300])
    else:
        print(f"\n❌ 任务失败: {result.get('error', 'unknown')}")
    
    # 手动教学
    print("\n📚 手动教学...")
    msg = adaptive.learn(
        "内蒙古政府采购网采集",
        "需要使用Playwright或Selenium等浏览器自动化工具，先等待页面JavaScript加载完成后再提取数据"
    )
    print(f"✅ {msg}")
    
    # 查询
    print("\n🔍 查询知识库...")
    knowledge = adaptive.get_knowledge("采购")
    print(f"找到 {len(knowledge)} 条知识")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    import asyncio
    
    print("="*60)
    print("Teamily AI Core - 自我学习系统")
    print("="*60)
    
    asyncio.run(test_self_learning())
    asyncio.run(test_adaptive_agent())
