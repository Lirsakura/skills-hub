#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试主动介入智能体 - 像群友一样自然互动
"""
import os
import sys

# 修复编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ["NVIDIA_API_KEY"] = "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"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.agent_manager import AgentManager
from scripts.proactive_agent import (
    ProactiveAgent, ActiveGroupChat, Trigger, TriggerType, Action
)


def test_keyword_trigger():
    """测试关键词触发"""
    print("\n" + "="*60)
    print("测试1: 关键词触发 - @AI 时回应")
    print("="*60)
    
    manager = AgentManager()
    agent = manager.create_agent(
        "小助手",
        "meta/llama-3.1-70b-instruct",
        "一个活跃的群友，喜欢分享有趣的内容"
    )
    
    proactive = ProactiveAgent(agent, "小助手")
    proactive.config["cooldown"] = 1  # 降低冷却
    
    # 模拟群聊
    chat = ActiveGroupChat("测试群")
    chat.add_agent(proactive)
    
    # 有人发消息
    chat.on_message("张三", "今天天气不错")
    chat.on_message("李四", "大家周末有什么计划？")
    
    # @AI
    actions = chat.on_message("王五", "@小助手 推荐一部电影吧")
    
    # 执行动作
    for action in actions:
        response = proactive.execute_action(action)
        if response:
            print(f"\n【小助手】: {response[:200]}...")


def test_question_trigger():
    """测试问题触发"""
    print("\n" + "="*60)
    print("测试2: 问题触发 - 有人问问题时回应")
    print("="*60)
    
    manager = AgentManager()
    agent = manager.create_agent(
        "技术达",
        "meta/llama-3.1-70b-instruct",
        "技术大牛，乐于解答技术问题"
    )
    
    proactive = ProactiveAgent(agent, "技术达")
    proactive.config["cooldown"] = 1
    
    chat = ActiveGroupChat("技术群")
    chat.add_agent(proactive)
    
    # 日常聊天
    chat.on_message("小明", "这个项目用什么框架比较好？")
    
    # 有人问问题
    actions = chat.on_message("小红", "有人知道 Python 怎么实现异步吗？")
    
    for action in actions:
        response = proactive.execute_action(action)
        if response:
            print(f"\n【技术达】: {response[:200]}...")


def test_context_understanding():
    """测试上下文理解"""
    print("\n" + "="*60)
    print("测试3: 上下文理解 - 基于对话历史回应")
    print("="*60)
    
    manager = AgentManager()
    agent = manager.create_agent(
        "电影迷",
        "meta/llama-3.1-70b-instruct",
        "电影爱好者，喜欢讨论电影"
    )
    
    proactive = ProactiveAgent(agent, "电影迷")
    proactive.config["cooldown"] = 1  # 降低冷却
    
    chat = ActiveGroupChat("电影群")
    chat.add_agent(proactive)
    
    # 建立上下文
    chat.on_message("影评人", "最近看了《流浪地球2》，太震撼了！")
    chat.on_message("观众A", "是啊，特效超级棒")
    chat.on_message("观众B", "剧情也很感人")
    
    # 继续讨论
    actions = chat.on_message("新成员", "有什么类似的好电影推荐吗？")
    
    for action in actions:
        response = proactive.execute_action(action)
        print(f"\n【电影迷】: {response[:300]}...")


def test_multiple_agents():
    """测试多智能体"""
    print("\n" + "="*60)
    print("测试4: 多智能体群聊")
    print("="*60)
    
    manager = AgentManager()
    
    # 创建多个智能体
    agents = [
        ("技术达", "meta/llama-3.1-70b-instruct", "技术专家"),
        ("产品侠", "meta/llama-3.1-70b-instruct", "产品经理"),
        ("设计师", "meta/llama-3.1-70b-instruct", "UI设计师")
    ]
    
    chat = ActiveGroupChat("产品讨论群")
    
    for name, model, role in agents:
        agent = manager.create_agent(name, model, role)
        proactive = ProactiveAgent(agent, name)
        proactive.config["cooldown"] = 1
        chat.add_agent(proactive)
    
    # 触发多个智能体
    actions = chat.on_message("产品经理", "我们讨论一下新App的界面设计吧")
    
    print(f"\n触发了 {len(actions)} 个智能体响应:")
    for action in actions:
        # 找到对应的智能体
        for agent in chat.agents:
            response = agent.execute_action(action)
            if response:
                print(f"\n【{agent.name}】: {response[:150]}...")


def test_recommend_scenario():
    """测试推荐场景"""
    print("\n" + "="*60)
    print("测试5: 智能推荐场景")
    print("="*60)
    
    manager = AgentManager()
    agent = manager.create_agent(
        "推荐官",
        "meta/llama-3.1-70b-instruct",
        "擅长根据氛围推荐内容"
    )
    
    proactive = ProactiveAgent(agent, "推荐官")
    proactive.config["cooldown"] = 1
    
    # 注册推荐处理器
    def handle_recommend(content):
        # 这里可以集成真实的推荐系统
        print(f"   [系统]: 执行推荐: {content[:50]}...")
        return content
    
    proactive.register_action_handler("recommend", handle_recommend)
    
    chat = ActiveGroupChat("娱乐群")
    chat.add_agent(proactive)
    
    # 讨论氛围
    chat.on_message("网友A", "周末无聊，想看点轻松的东西")
    chat.on_message("网友B", "同意，最好是搞笑的")
    
    # 触发推荐
    actions = chat.on_message("网友C", "有啥推荐的吗？")
    
    for action in actions:
        response = proactive.execute_action(action)
        if response:
            print(f"\n【推荐官】: {response[:300]}...")


def test_silence_break():
    """测试打破沉默"""
    print("\n" + "="*60)
    print("测试6: 打破沉默")
    print("="*60)
    
    manager = AgentManager()
    agent = manager.create_agent(
        "活跃分子",
        "meta/llama-3.1-70b-instruct",
        "群里的活跃分子"
    )
    
    # 自定义沉默触发器
    silence_trigger = Trigger(
        trigger_type=TriggerType.SILENCE,
        silence_seconds=10,  # 10秒无消息就触发（测试用）
        config={"action_type": "break_silence"}
    )
    
    proactive = ProactiveAgent(agent, "活跃分子")
    proactive.add_trigger(silence_trigger)
    proactive.config["cooldown"] = 1
    
    chat = ActiveGroupChat("测试群")
    chat.add_agent(proactive)
    
    # 发送消息
    chat.on_message("用户A", "今天讨论什么？")
    chat.on_message("用户B", "不知道")
    
    import time
    # 模拟时间流逝
    time.sleep(0.1)
    
    # 再发一条，触发沉默检测
    actions = chat.on_message("用户C", "有人吗？")
    
    for action in actions:
        response = proactive.execute_action(action)
        if response:
            print(f"\n【活跃分子】: {response}")


if __name__ == "__main__":
    print("="*60)
    print("主动介入智能体测试 - 像群友一样自然互动")
    print("="*60)
    
    test_keyword_trigger()
    test_question_trigger()
    test_context_understanding()
    test_multiple_agents()
    test_recommend_scenario()
    test_silence_break()
    
    print("\n" + "="*60)
    print("测试完成!")
    print("="*60)
