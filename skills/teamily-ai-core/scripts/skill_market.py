"""
Teamily AI Core - 技能市场
智能技能执行系统
"""

import json
import time
import importlib
import subprocess
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class SkillCategory(Enum):
    """技能分类"""
    RESEARCH = "research"          # 调研
    WRITING = "writing"           # 写作
    DESIGN = "design"             # 设计
    CODING = "coding"             # 编程
    DATA = "data"                 # 数据分析
    SOCIAL = "social"            # 社交
    CREATIVE = "creative"          # 创意
    UTILITY = "utility"          # 工具
    CUSTOM = "custom"             # 自定义


@dataclass
class Skill:
    """技能定义"""
    id: str
    name: str
    description: str
    category: SkillCategory
    version: str = "1.0.0"
    author: str = ""
    
    # 执行配置
    prompt_template: str = ""           # 主提示词
    agent_config: Dict = field(default_factory=dict)  # Agent 配置
    required_skills: List[str] = field(default_factory=list)  # 依赖技能
    parameters: List[Dict] = field(default_factory=list)  # 参数定义
    
    # 执行器
    executor: Callable = None           # 自定义执行器
    script_path: str = ""               # 脚本路径
    
    # 元数据
    tags: List[str] = field(default_factory=list)
    examples: List[Dict] = field(default_factory=list)
    rating: float = 0.0
    usage_count: int = 0


@dataclass
class SkillExecution:
    """技能执行记录"""
    id: str
    skill_id: str
    input: Dict
    output: Any
    status: str  # success, failed, pending
    error: str = ""
    duration: float = 0.0
    timestamp: float = field(default_factory=time.time)


class SkillMarket:
    """
    技能市场
    
    功能：
    - 注册技能
    - 搜索技能
    - 执行技能
    - 技能编排
    """
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.executions: List[SkillExecution] = []
        self.categories = {c.value: [] for c in SkillCategory}
        
        # 初始化内置技能
        self._register_builtin_skills()
    
    def _register_builtin_skills(self):
        """注册内置技能"""
        
        # 1. 市场调研技能
        self.register(Skill(
            id="market_research",
            name="市场调研",
            description="深入分析市场规模、趋势、竞争格局",
            category=SkillCategory.RESEARCH,
            prompt_template="""请对{topic}进行深入的市场调研，包括：
1. 市场规模和增长趋势
2. 主要玩家和市场份额
3. 用户需求和痛点
4. 发展机会和建议
请提供详细的数据和分析。""",
            parameters=[
                {"name": "topic", "type": "string", "required": True, "description": "调研主题"},
                {"name": "depth", "type": "string", "default": "详细", "description": "调研深度"}
            ],
            tags=["市场", "调研", "分析"]
        ))
        
        # 2. 竞品分析技能
        self.register(Skill(
            id="competitor_analysis",
            name="竞品分析",
            description="对比分析竞争对手的产品、策略",
            category=SkillCategory.RESEARCH,
            prompt_template="""请对{competitors}进行竞品分析：
1. 产品功能对比
2. 商业模式分析
3. 优劣势总结
4. 差异化建议""",
            parameters=[
                {"name": "competitors", "type": "string", "required": True, "description": "竞品列表"}
            ],
            tags=["竞品", "对比", "分析"]
        ))
        
        # 3. 文案写作技能
        self.register(Skill(
            id="copywriting",
            name="文案写作",
            description="根据主题创作吸引人的文案",
            category=SkillCategory.WRITING,
            prompt_template="""请为{topic}创作文案：
类型: {type}
风格: {style}
目标受众: {audience}

要求：{requirements}""",
            parameters=[
                {"name": "topic", "type": "string", "required": True, "description": "主题"},
                {"name": "type", "type": "string", "default": "宣传文案", "description": "文案类型"},
                {"name": "style", "type": "string", "default": "专业", "description": "风格"},
                {"name": "audience", "type": "string", "default": "大众", "description": "目标受众"}
            ],
            tags=["文案", "写作", "营销"]
        ))
        
        # 4. 视觉设计技能
        self.register(Skill(
            id="visual_design",
            name="视觉设计",
            description="生成设计概念和视觉方案",
            category=SkillCategory.DESIGN,
            prompt_template="""请为{project}设计视觉方案：
1. 风格定位: {style}
2. 配色方案
3. 关键视觉元素
4. 应用场景建议""",
            parameters=[
                {"name": "project", "type": "string", "required": True, "description": "项目名称"},
                {"name": "style", "type": "string", "default": "现代简约", "description": "风格"}
            ],
            tags=["设计", "视觉", "UI"]
        ))
        
        # 5. 代码开发技能
        self.register(Skill(
            id="code_development",
            name="代码开发",
            description="根据需求生成代码",
            category=SkillCategory.CODING,
            prompt_template="""请用{language}开发{feature}：

需求: {requirements}

要求：
- 代码规范
- 注释清晰
- 考虑可维护性""",
            parameters=[
                {"name": "feature", "type": "string", "required": True, "description": "功能描述"},
                {"name": "language", "type": "string", "default": "Python", "description": "编程语言"},
                {"name": "requirements", "type": "string", "required": True, "description": "需求详情"}
            ],
            tags=["代码", "开发", "编程"]
        ))
        
        # 6. 数据分析技能
        self.register(Skill(
            id="data_analysis",
            name="数据分析",
            description="分析数据并生成洞察",
            category=SkillCategory.DATA,
            prompt_template="""请分析以下数据：
{data_description}

目标: {objective}
请提供：
1. 数据概况
2. 关键发现
3. 建议""",
            parameters=[
                {"name": "data_description", "type": "string", "required": True, "description": "数据描述"},
                {"name": "objective", "type": "string", "default": "发现 insights", "description": "分析目标"}
            ],
            tags=["数据", "分析", "洞察"]
        ))
        
        # 7. 头脑风暴技能
        self.register(Skill(
            id="brainstorming",
            name="头脑风暴",
            description="针对主题进行创意发散",
            category=SkillCategory.CREATIVE,
            prompt_template="""请围绕"{topic}"进行头脑风暴：
方向: {direction}
数量: {count}个想法

请提供有创意、可落地的想法。""",
            parameters=[
                {"name": "topic", "type": "string", "required": True, "description": "主题"},
                {"name": "direction", "type": "string", "default": "产品创新", "description": "方向"},
                {"name": "count", "type": "int", "default": 10, "description": "想法数量"}
            ],
            tags=["创意", "头脑风暴", "想法"]
        ))
        
        # 8. 社交媒体运营技能
        self.register(Skill(
            id="social_media",
            name="社交媒体运营",
            description="生成社交媒体内容",
            category=SkillCategory.SOCIAL,
            prompt_template="""请为{platform}创作内容：
主题: {topic}
风格: {style}
字数: {length}字

要求：{requirements}""",
            parameters=[
                {"name": "platform", "type": "string", "required": True, "description": "平台"},
                {"name": "topic", "type": "string", "required": True, "description": "主题"},
                {"name": "style", "type": "string", "default": "活泼", "description": "风格"},
                {"name": "length", "type": "int", "default": 150, "description": "字数"}
            ],
            tags=["社交媒体", "运营", "内容"]
        ))
    
    def register(self, skill: Skill):
        """注册技能"""
        self.skills[skill.id] = skill
        self.categories[skill.category.value].append(skill.id)
        
        # 更新类别列表
        for tag in skill.tags:
            pass  # 可以添加标签索引
    
    def get(self, skill_id: str) -> Optional[Skill]:
        """获取技能"""
        return self.skills.get(skill_id)
    
    def search(self, query: str, category: SkillCategory = None, tags: List[str] = None) -> List[Skill]:
        """搜索技能"""
        results = []
        
        for skill in self.skills.values():
            # 类别过滤
            if category and skill.category != category:
                continue
            
            # 标签过滤
            if tags and not any(t in skill.tags for t in tags):
                continue
            
            # 关键词匹配
            query_lower = query.lower()
            if (query_lower in skill.name.lower() or 
                query_lower in skill.description.lower() or
                any(query_lower in tag.lower() for tag in skill.tags)):
                results.append(skill)
        
        # 按使用量排序
        results.sort(key=lambda s: s.usage_count, reverse=True)
        
        return results
    
    def list_by_category(self, category: SkillCategory) -> List[Skill]:
        """列出某分类的技能"""
        skill_ids = self.categories.get(category.value, [])
        return [self.skills[sid] for sid in skill_ids if sid in self.skills]
    
    def list_all(self) -> List[Skill]:
        """列出所有技能"""
        return list(self.skills.values())
    
    def execute(self, skill_id: str, params: Dict, agent=None) -> SkillExecution:
        """执行技能"""
        skill = self.get(skill_id)
        if not skill:
            return SkillExecution(
                id=str(time.time()),
                skill_id=skill_id,
                input=params,
                output=None,
                status="failed",
                error=f"Skill not found: {skill_id}"
            )
        
        execution = SkillExecution(
            id=str(time.time()),
            skill_id=skill_id,
            input=params,
            output=None,
            status="pending"
        )
        
        start_time = time.time()
        
        try:
            # 检查依赖
            for dep_skill_id in skill.required_skills:
                self.execute(dep_skill_id, params, agent)
            
            # 构建提示词
            prompt = skill.prompt_template
            for key, value in params.items():
                prompt = prompt.replace(f"{{{key}}}", str(value))
            
            # 执行
            if skill.executor:
                output = skill.executor(params)
            elif agent:
                output = agent.chat(prompt)
            elif skill.script_path:
                output = subprocess.run(
                    ["python", skill.script_path],
                    input=json.dumps(params),
                    capture_output=True,
                    text=True
                ).stdout
            else:
                output = prompt  # 返回提示词作为输出
            
            execution.output = output
            execution.status = "success"
            skill.usage_count += 1
            
        except Exception as e:
            execution.output = None
            execution.status = "failed"
            execution.error = str(e)
        
        execution.duration = time.time() - start_time
        self.executions.append(execution)
        
        return execution
    
    def execute_pipeline(self, skill_ids: List[str], params: Dict, agent=None) -> List[SkillExecution]:
        """执行技能管道"""
        results = []
        context = params.copy()
        
        for skill_id in skill_ids:
            result = self.execute(skill_id, context, agent)
            results.append(result)
            
            if result.status == "success" and result.output:
                # 将输出添加到上下文
                context[f"{skill_id}_output"] = result.output
        
        return results
    
    def get_popular(self, limit: int = 10) -> List[Skill]:
        """获取热门技能"""
        return sorted(self.skills.values(), 
                     key=lambda s: s.usage_count, 
                     reverse=True)[:limit]
    
    def get_statistics(self) -> Dict:
        """获取统计数据"""
        return {
            "total_skills": len(self.skills),
            "total_executions": len(self.executions),
            "successful_executions": len([e for e in self.executions if e.status == "success"]),
            "by_category": {
                cat: len(sids) for cat, sids in self.categories.items()
            },
            "popular_skills": [
                {"id": s.id, "name": s.name, "usage": s.usage_count}
                for s in self.get_popular(5)
            ]
        }


# 全局技能市场实例
_market = None

def get_skill_market() -> SkillMarket:
    """获取技能市场实例"""
    global _market
    if _market is None:
        _market = SkillMarket()
    return _market


__all__ = ["Skill", "SkillExecution", "SkillMarket", "SkillCategory", "get_skill_market"]
