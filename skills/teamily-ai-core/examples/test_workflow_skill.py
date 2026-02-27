#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试工作流引擎和技能市场
"""
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ["NVIDIA_API_KEY"] = "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"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_skill_market():
    """测试技能市场"""
    print("="*60)
    print("技能市场测试")
    print("="*60)
    
    from scripts.skill_market import get_skill_market, SkillCategory
    
    market = get_skill_market()
    
    # 列出所有技能
    print("\n📦 所有技能:")
    for skill in market.list_all():
        print(f"  • {skill.name} - {skill.description[:40]}...")
    
    # 搜索技能
    print("\n🔍 搜索'调研':")
    results = market.search("调研")
    for s in results:
        print(f"  • {s.name}")
    
    # 按分类查看
    print("\n📂 写作类技能:")
    for s in market.list_by_category(SkillCategory.WRITING):
        print(f"  • {s.name}")
    
    # 统计
    print("\n📊 统计:")
    stats = market.get_statistics()
    print(f"  总技能数: {stats['total_skills']}")
    print(f"  总执行次数: {stats['total_executions']}")
    
    print("\n✅ 技能市场测试完成")


def test_workflow_engine():
    """测试工作流引擎"""
    print("\n" + "="*60)
    print("工作流引擎测试")
    print("="*60)
    
    from scripts.workflow_engine import WorkflowEngine, WorkflowNode, NodeType
    from scripts.agent_manager import AgentManager
    
    # 创建 Agent
    manager = AgentManager()
    researcher = manager.create_agent("调研员", "meta/llama-3.1-70b-instruct", "专业研究员")
    writer = manager.create_agent("写手", "meta/llama-3.1-70b-instruct", "专业作家")
    designer = manager.create_agent("设计师", "meta/llama-3.1-70b-instruct", "专业设计师")
    
    # 创建工作流引擎
    engine = WorkflowEngine()
    
    # 创建工作流
    wf = engine.create_workflow("内容创作", "自动创作内容")
    
    # 添加节点
    node1 = WorkflowNode(
        id="research",
        name="调研",
        node_type=NodeType.AGENT,
        config={"agent": researcher, "output_key": "research_result"}
    )
    
    node2 = WorkflowNode(
        id="write",
        name="写作",
        node_type=NodeType.AGENT,
        config={"agent": writer, "output_key": "article"}
    )
    
    node3 = WorkflowNode(
        id="design",
        name="设计配图",
        node_type=NodeType.AGENT,
        config={"agent": designer, "output_key": "images"}
    )
    
    engine.add_node(wf, node1)
    engine.add_node(wf, node2)
    engine.add_node(wf, node3)
    
    # 添加连接
    engine.add_edge(wf, "research", "write")
    engine.add_edge(wf, "write", "design")
    
    # 设置变量
    engine.set_variable(wf, "topic", "人工智能对未来工作的影响")
    
    print(f"\n📋 工作流: {wf.name}")
    print(f"  节点数: {len(wf.nodes)}")
    print(f"  连接数: {len(wf.edges)}")
    
    print("\n节点列表:")
    for node in wf.nodes:
        print(f"  [{node.node_type.value}] {node.name} ({node.id})")
    
    print("\n连接关系:")
    for edge in wf.edges:
        print(f"  {edge['from']} → {edge['to']}")
    
    print("\n✅ 工作流引擎测试完成")


def test_skill_execution():
    """测试技能执行"""
    print("\n" + "="*60)
    print("技能执行测试")
    print("="*60)
    
    from scripts.skill_market import get_skill_market
    from scripts.agent_manager import AgentManager
    
    market = get_skill_market()
    
    # 创建 Agent
    manager = AgentManager()
    agent = manager.create_agent("助手", "meta/llama-3.1-70b-instruct", "AI助手")
    
    # 执行技能
    print("\n🚀 执行'文案写作'技能:")
    result = market.execute("copywriting", {
        "topic": "新产品发布",
        "type": "宣传文案",
        "style": "活泼",
        "audience": "年轻人",
        "requirements": "吸引眼球，有传播性"
    }, agent)
    
    print(f"  状态: {result.status}")
    print(f"  耗时: {result.duration:.2f}秒")
    if result.output:
        print(f"  输出: {result.output[:200]}...")
    
    print("\n✅ 技能执行测试完成")


if __name__ == "__main__":
    print("="*60)
    print("Teamily AI Core - 工作流 & 技能市场")
    print("="*60)
    
    test_skill_market()
    test_workflow_engine()
    test_skill_execution()
    
    print("\n" + "="*60)
    print("全部测试完成!")
    print("="*60)
