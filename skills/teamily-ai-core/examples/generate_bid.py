#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
物业采购投标书生成器
基于采集的招标信息自动生成投标书
"""
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ["NVIDIA_API_KEY"] = "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"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_bid_document(project_info: dict):
    """生成投标书"""
    from scripts.agent_manager import AgentManager
    from scripts.swarm_intelligence import create_swarm
    
    # 创建投标团队
    swarm = create_swarm(
        "投标团队",
        agents=[
            ("项目负责人", "meta/llama-3.1-70b-instruct", "资深项目经理，擅长投标文件编制"),
            ("技术专家", "meta/llama-3.1-70b-instruct", "物业管理技术专家"),
            ("商务专家", "meta/llama-3.1-70b-instruct", "投标商务专家，擅长报价策略")
        ]
    )
    
    project_name = project_info.get("name", "物业服务项目")
    budget = project_info.get("budget", "")
    location = project_info.get("location", "")
    unit = project_info.get("unit", "")
    
    # 执行投标文件生成
    result = swarm.collaborative_think(
        problem=f"""请为以下项目生成一份完整的投标书（标书）：

项目名称：{project_name}
项目地点：{location}
采购单位：{unit}
预算金额：{budget}

请按照以下结构生成投标书：
1. 投标函
2. 法定代表人身份证明
3. 投标保证金
4. 资格证明文件（营业执照、资质证书等）
5. 项目实施方案
6. 服务团队配置
7. 物业管理方案
8. 报价文件
9. 业绩证明
10. 承诺书

要求：专业、完整、可直接使用。""",
        strategy="iterative"
    )
    
    return result


def main():
    # 采集到的招标信息
    projects = [
        {
            "name": "鄂托克前旗党政集中办公区物业管理服务项目",
            "location": "鄂尔多斯市鄂托克前旗",
            "unit": "鄂托克前旗机关事务服务中心",
            "budget": "约2130万元",
            "type": "招标公告"
        },
        {
            "name": "国泰广场行政办公区物业管理服务",
            "location": "鄂尔多斯市",
            "unit": "鄂尔多斯市机关事务服务中心",
            "budget": "21,281,360.00元",
            "type": "招标公告"
        },
        {
            "name": "包头职业技术学院综合物业服务项目",
            "location": "包头市",
            "unit": "包头职业技术学院",
            "budget": "4,300,000.00元",
            "type": "招标公告"
        },
        {
            "name": "市本级集中办公区物业管理服务",
            "location": "呼和浩特市",
            "unit": "呼和浩特市机关事务管理局",
            "budget": "2,562,900.00元",
            "type": "招标公告"
        }
    ]
    
    print("="*70)
    print("物业采购投标书生成器")
    print("="*70)
    
    print("\n📋 采集到的招标信息：")
    for i, p in enumerate(projects, 1):
        print(f"\n{i}. {p['name']}")
        print(f"   地点: {p['location']}")
        print(f"   单位: {p['unit']}")
        print(f"   预算: {p['budget']}")
        print(f"   类型: {p['type']}")
    
    # 选择第一个项目生成标书
    print("\n" + "="*70)
    print(f"📝 为第一个项目生成投标书...")
    print("="*70)
    
    result = generate_bid_document(projects[0])
    
    print("\n" + "="*70)
    print("生成的投标书")
    print("="*70)
    
    # 打印汇总
    if 'summary' in result:
        print(result['summary'])
    else:
        # 打印各方观点
        for msg in result.get('responses', []):
            print(f"\n【{msg['author']}】:")
            print(msg['response'][:800])
            print("-"*50)


if __name__ == "__main__":
    main()
