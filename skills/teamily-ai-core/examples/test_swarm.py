#!/usr/bin/env python
"""
测试群体智能 - 复利效应演示
"""
import os
import sys

os.environ["NVIDIA_API_KEY"] = "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"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.agent_manager import AgentManager
from scripts.swarm_intelligence import SwarmIntelligence, create_swarm


def test_swarm_debate():
    """测试辩论式协作"""
    print("\n" + "="*60)
    print("测试1: 辩论式 - 各抒己见")
    print("="*60)
    
    swarm = SwarmIntelligence("产品评审")
    manager = AgentManager()
    
    # 添加 3 个不同角色的 AI
    tech = manager.create_agent("技术专家", "meta/llama-3.1-70b-instruct",
                               "擅长技术架构，关注系统性能和可维护性")
    product = manager.create_agent("产品经理", "meta/llama-3.1-70b-instruct",
                                   "擅长用户需求分析和产品策略")
    design = manager.create_agent("设计师", "meta/llama-3.1-70b-instruct",
                                  "擅长用户体验和交互设计")
    
    swarm.add_agent(tech)
    swarm.add_agent(product)
    swarm.add_agent(design)
    
    # 发起问题
    result = swarm.collaborative_think(
        problem="设计一个 AI 聊天助手，应该先做网页版还是移动 App？",
        strategy="debate"
    )
    
    print(f"\n问题: {result['problem']}")
    print("\n--- 各方观点 ---")
    for r in result['responses']:
        print(f"\n【{r['author']}】({r['role']}):")
        print(f"  {r['response'][:300]}...")
    
    print("\n--- 汇总 ---")
    print(result['summary'][:500])


def test_swarm_iterative():
    """测试迭代式协作"""
    print("\n" + "="*60)
    print("测试2: 迭代式 - 基于他人观点改进")
    print("="*60)
    
    swarm = create_swarm(
        "产品团队",
        agents=[
            ("A君", "meta/llama-3.1-70b-instruct", "市场分析师"),
            ("B君", "meta/llama-3.1-70b-instruct", "数据科学家"),
            ("C君", "meta/llama-3.1-70b-instruct", "商业顾问")
        ],
        humans=["产品负责人"]
    )
    
    result = swarm.collaborative_think(
        problem="如何提升用户留存率？",
        strategy="iterative"
    )
    
    print(f"\n问题: {result['problem']}")
    print(f"策略: {result['strategy']}")
    print(f"轮数: {result['rounds']}")
    
    # 显示每轮讨论
    rounds = {}
    for r in result['responses']:
        round_num = r['round']
        if round_num not in rounds:
            rounds[round_num] = []
        rounds[round_num].append(r)
    
    for rd in sorted(rounds.keys()):
        print(f"\n--- 第 {rd} 轮 ---")
        for r in rounds[rd]:
            print(f"【{r['author']}】: {r['response'][:200]}...")
    
    print("\n--- 最终汇总 ---")
    print(result['summary'][:500])


def test_swarm_critique():
    """测试评审式协作"""
    print("\n" + "="*60)
    print("测试3: 评审式 - 产出→批评→改进")
    print("="*60)
    
    swarm = create_swarm(
        "方案评审会",
        agents=[
            ("架构师", "meta/llama-3.1-70b-instruct", "系统架构专家"),
            ("安全专家", "meta/llama-3.1-70b-instruct", "安全工程专家")
        ]
    )
    
    result = swarm.collaborative_think(
        problem="设计一个用户登录系统，需要支持第三方登录（Google、GitHub）",
        strategy="critique"
    )
    
    print(f"\n问题: {result['problem']}")
    print(f"迭代次数: {len(result['iterations'])}")
    
    print("\n--- 最佳方案 ---")
    print(result['best_response'][:800])


def test_human_ai_collaboration():
    """测试人类+AI协作"""
    print("\n" + "="*60)
    print("测试4: 人类 + AI 协作")
    print("="*60)
    
    swarm = create_swarm(
        "讨论组",
        agents=[
            ("AI助手1", "meta/llama-3.1-70b-instruct", "专业助手"),
            ("AI助手2", "meta/llama-3.1-70b-instruct", "创意顾问")
        ],
        humans=["张三"]
    )
    
    # 人类发言
    swarm.human_join("张三", "我们讨论一下新产品命名吧！")
    
    # AI 回应
    print("\n【张三】: 我们讨论一下新产品命名吧！")
    
    for thought in swarm.thoughts[-2:]:
        print(f"\n【{thought.author}】: {thought.content[:200]}...")
    
    # 继续讨论
    result = swarm.collaborative_think(
        problem="为一款 AI 协作工具起一个响亮的名字",
        strategy="iterative"
    )
    
    print("\n--- 名字建议 ---")
    print(result['summary'][:300])


def test_wisdom():
    """测试获取群体智慧"""
    print("\n" + "="*60)
    print("测试5: 获取群体智慧")
    print("="*60)
    
    swarm = create_swarm(
        "智慧库",
        agents=[
            ("思考者A", "meta/llama-3.1-70b-instruct", "分析师"),
            ("思考者B", "meta/llama-3.1-70b-instruct", "策略师")
        ]
    )
    
    # 先产生一些讨论
    swarm.collaborative_think("什么是创新？", strategy="debate")
    swarm.collaborative_think("如何衡量成功？", strategy="debate")
    
    # 获取智慧
    wisdom = swarm.get_wisdom()
    print("\n--- 群体智慧 ---")
    print(wisdom[:500])


if __name__ == "__main__":
    print("="*60)
    print("群体智能测试 - 复利效应演示")
    print("="*60)
    
    # 运行测试
    test_swarm_debate()
    test_swarm_iterative()
    test_swarm_critique()
    test_human_ai_collaboration()
    test_wisdom()
    
    print("\n" + "="*60)
    print("测试完成!")
    print("="*60)
