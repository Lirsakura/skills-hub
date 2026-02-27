"""
Teamily AI Core - 工作流管理系统
类似 Manus 的自动化工作流
"""

import json
import time
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from .agent_manager import Agent
from .swarm_intelligence import create_swarm


class NodeType(Enum):
    """节点类型"""
    AGENT = "agent"           # AI 智能体
    HUMAN = "human"           # 人类审批
    CONDITION = "condition"   # 条件判断
    WAIT = "wait"             # 等待
    ACTION = "action"         # 执行动作
    LOOP = "loop"             # 循环
    PARALLEL = "parallel"     # 并行


class NodeStatus(Enum):
    """节点状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING =waiting = "waiting"


@dataclass
class WorkflowNode:
    """工作流节点"""
    id: str
    name: str
    node_type: NodeType
    config: Dict = field(default_factory=dict)
    inputs: Dict = field(default_factory=dict)
    outputs: Dict = field(default_factory=dict)
    status: NodeStatus = NodeStatus.PENDING
    error: str = ""


@dataclass
class Workflow:
    """工作流"""
    id: str
    name: str
    description: str
    nodes: List[WorkflowNode] = field(default_factory=list)
    edges: List[Dict] = field(default_factory=list)  # 连接关系
    variables: Dict = field(default_factory=dict)  # 全局变量
    status: str = "draft"  # draft, active, paused, completed


class WorkflowEngine:
    """
    工作流引擎
    
    支持：
    - 顺序执行
    - 条件分支
    - 并行执行
    - 循环
    - 人工审批
    """
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.current_workflow: Optional[Workflow] = None
        self.current_node: Optional[WorkflowNode] = None
        
        # 回调函数
        self.handlers: Dict[str, Callable] = {
            "on_node_start": None,
            "on_node_complete": None,
            "on_node_error": None,
            "on_human_approval": None,
        }
    
    def create_workflow(self, name: str, description: str = "") -> Workflow:
        """创建工作流"""
        workflow = Workflow(
            id=str(time.time()),
            name=name,
            description=description
        )
        self.workflows[workflow.id] = workflow
        return workflow
    
    def add_node(self, workflow: Workflow, node: WorkflowNode):
        """添加节点"""
        workflow.nodes.append(node)
    
    def add_edge(self, workflow: Workflow, from_node: str, to_node: str, condition: str = None):
        """添加连接"""
        workflow.edges.append({
            "from": from_node,
            "to": to_node,
            "condition": condition  # 条件表达式
        })
    
    def set_variable(self, workflow: Workflow, key: str, value: Any):
        """设置变量"""
        workflow.variables[key] = value
    
    def get_variable(self, workflow: Workflow, key: str, default: Any = None) -> Any:
        """获取变量"""
        return workflow.variables.get(key, default)
    
    async def execute(self, workflow: Workflow, context: Dict = None) -> Dict:
        """执行工作流"""
        self.current_workflow = workflow
        
        # 初始化上下文
        ctx = context or {}
        ctx.update(workflow.variables)
        
        # 找到起始节点
        start_node = self._find_start_node(workflow)
        if not start_node:
            return {"status": "error", "message": "未找到起始节点"}
        
        # 执行
        result = await self._execute_node(start_node, ctx)
        
        return {
            "status": "completed",
            "workflow_id": workflow.id,
            "result": result,
            "variables": ctx
        }
    
    async def _execute_node(self, node: WorkflowNode, context: Dict) -> Any:
        """执行单个节点"""
        node.status = NodeStatus.RUNNING
        self.current_node = node
        
        # 触发回调
        if self.handlers["on_node_start"]:
            self.handlers["on_node_start"](node, context)
        
        try:
            result = None
            
            if node.node_type == NodeType.AGENT:
                result = await self._execute_agent(node, context)
            elif node.node_type == NodeType.HUMAN:
                result = await self._execute_human(node, context)
            elif node.node_type == NodeType.CONDITION:
                result = await self._execute_condition(node, context)
            elif node.node_type == NodeType.ACTION:
                result = await self._execute_action(node, context)
            elif node.node_type == NodeType.PARALLEL:
                result = await self._execute_parallel(node, context)
            
            node.outputs = result or {}
            node.status = NodeStatus.COMPLETED
            
            # 触发回调
            if self.handlers["on_node_complete"]:
                self.handlers["on_node_complete"](node, context)
            
            # 执行下一个节点
            next_node = self._find_next_node(node)
            if next_node:
                return await self._execute_node(next_node, context)
            
            return result
            
        except Exception as e:
            node.status = NodeStatus.FAILED
            node.error = str(e)
            
            if self.handlers["on_node_error"]:
                self.handlers["on_node_error"](node, context, e)
            
            raise
    
    async def _execute_agent(self, node: WorkflowNode, context: Dict) -> str:
        """执行 AI 节点"""
        agent = node.config.get("agent")
        prompt_template = node.config.get("prompt", "")
        
        # 替换变量
        prompt = prompt_template
        for key, value in context.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        
        # 执行
        result = agent.chat(prompt)
        
        # 保存输出到上下文
        output_key = node.config.get("output_key", node.id)
        context[output_key] = result
        
        return result
    
    async def _execute_human(self, node: WorkflowNode, context: Dict) -> str:
        """执行人工审批节点"""
        # 触发人工审批回调
        if self.handlers["on_human_approval"]:
            approval = await self.handlers["on_human_approval"](node, context)
            context[f"{node.id}_approval"] = approval
            return approval
        
        # 默认通过
        return "approved"
    
    async def _execute_condition(self, node: WorkflowNode, context: Dict) -> str:
        """执行条件节点"""
        condition = node.config.get("condition", "")
        
        # 简单条件判断
        for key, value in context.items():
            condition = condition.replace(f"{{{key}}}", f'"{value}"')
        
        # 执行条件
        result = eval(condition)
        context[f"{node.id}_result"] = result
        
        return str(result)
    
    async def _execute_action(self, node: WorkflowNode, context: Dict) -> Any:
        """执行动作节点"""
        action = node.config.get("action")
        
        if action == "send_notification":
            # 发送通知
            return {"sent": True}
        elif action == "save_to_db":
            # 保存到数据库
            return {"saved": True}
        elif action == "call_api":
            # 调用 API
            return {"api_called": True}
        
        return {"action": action}
    
    async def _execute_parallel(self, node: WorkflowNode, context: Dict) -> List:
        """执行并行节点"""
        import asyncio
        
        tasks = node.config.get("tasks", [])
        results = await asyncio.gather(*[
            self._execute_agent(task, context) for task in tasks
        ])
        
        return results
    
    def _find_start_node(self, workflow: Workflow) -> Optional[WorkflowNode]:
        """找到起始节点"""
        # 找没有入边的节点
        targets = [e["to"] for e in workflow.edges]
        
        for node in workflow.nodes:
            if node.id not in targets:
                return node
        
        return workflow.nodes[0] if workflow.nodes else None
    
    def _find_next_node(self, current: WorkflowNode) -> Optional[WorkflowNode]:
        """找到下一个节点"""
        workflow = self.current_workflow
        
        for edge in workflow.edges:
            if edge["from"] == current.id:
                # 检查条件
                if edge.get("condition"):
                    condition = edge["condition"]
                    for key, value in self.current_workflow.variables.items():
                        condition = condition.replace(f"{{{key}}}", str(value))
                    
                    if not eval(condition):
                        continue
                
                # 找到目标节点
                for node in workflow.nodes:
                    if node.id == edge["to"]:
                        return node
        
        return None
    
    def on(self, event: str, handler: Callable):
        """注册事件处理"""
        if event in self.handlers:
            self.handlers[event] = handler


# 预设工作流模板
class WorkflowTemplates:
    """工作流模板"""
    
    @staticmethod
    def market_research(agents: Dict[str, Agent]) -> Workflow:
        """市场调研工作流"""
        engine = WorkflowEngine()
        wf = engine.create_workflow("市场调研", "自动完成市场调研")
        
        # 节点1: 收集数据
        node1 = WorkflowNode(
            id="collect_data",
            name="收集数据",
            node_type=NodeType.AGENT,
            config={"agent": agents["researcher"], "output_key": "market_data"}
        )
        
        # 节点2: 分析竞品
        node2 = WorkflowNode(
            id="analyze_competitor",
            name="竞品分析",
            node_type=NodeType.AGENT,
            config={"agent": agents["competitor"], "output_key": "competitor_analysis"}
        )
        
        # 节点3: 人工审核
        node3 = WorkflowNode(
            id="human_review",
            name="审核",
            node_type=NodeType.HUMAN,
            config={"approver": "manager"}
        )
        
        # 节点4: 生成报告
        node4 = WorkflowNode(
            id="generate_report",
            name="生成报告",
            node_type=NodeType.AGENT,
            config={"agent": agents["writer"], "output_key": "report"}
        )
        
        # 添加节点
        engine.add_node(wf, node1)
        engine.add_node(wf, node2)
        engine.add_node(wf, node3)
        engine.add_node(wf, node4)
        
        # 添加连接
        engine.add_edge(wf, "collect_data", "analyze_competitor")
        engine.add_edge(wf, "analyze_competitor", "human_review")
        engine.add_edge(wf, "human_review", "generate_report", "{review_approved} == true")
        
        return wf
    
    @staticmethod
    def content_creation(agents: Dict[str, Agent]) -> Workflow:
        """内容创作工作流"""
        engine = WorkflowEngine()
        wf = engine.create_workflow("内容创作", "自动创作内容")
        
        # 构思 -> 写作 -> 配图 -> 审核 -> 发布
        nodes = [
            ("ideation", "构思", "researcher"),
            ("writing", "写作", "writer"),
            ("designing", "配图", "designer"),
            ("review", "审核", "human"),
            ("publishing", "发布", "action"),
        ]
        
        prev = None
        for node_id, name, agent_type in nodes:
            if agent_type == "human":
                node = WorkflowNode(id=node_id, name=name, node_type=NodeType.HUMAN)
            elif agent_type == "action":
                node = WorkflowNode(id=node_id, name=name, node_type=NodeType.ACTION,
                                  config={"action": "publish"})
            else:
                node = WorkflowNode(id=node_id, name=name, node_type=NodeType.AGENT,
                                  config={"agent": agents[agent_type], "output_key": node_id})
            
            engine.add_node(wf, node)
            
            if prev:
                engine.add_edge(wf, prev, node_id)
            
            prev = node_id
        
        return wf


__all__ = ["WorkflowEngine", "Workflow", "WorkflowNode", "NodeType", "WorkflowTemplates"]
