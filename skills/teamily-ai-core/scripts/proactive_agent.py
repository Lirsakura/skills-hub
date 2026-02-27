"""
Teamily AI Core - 主动介入智能体
让 AI 像群友一样主动参与对话
"""

import time
import re
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

from .agent_manager import Agent


class TriggerType(Enum):
    """触发类型"""
    KEYWORD = "keyword"           # 关键词触发
    EMOTION = "emotion"           # 情绪触发
    QUESTION = "question"         # 问题触发
    SILENCE = "silence"           # 沉默触发
    CONTEXT = "context"           # 上下文触发
    TIMED = "timed"               # 定时触发
    RANDOM = "random"             # 随机触发


@dataclass
class Trigger:
    """触发器配置"""
    trigger_type: TriggerType
    config: Dict = field(default_factory=dict)
    
    # 关键词配置
    keywords: List[str] = field(default_factory=list)
    case_sensitive: bool = False
    
    # 情绪配置
    emotions: List[str] = field(default_factory=list)  # positive, negative, neutral
    
    # 沉默配置
    silence_seconds: int = 300  # 沉默多久触发
    
    # 随机配置
    probability: float = 0.1   # 触发概率 0-1
    
    # 上下文配置
    context_patterns: List[str] = field(default_factory=list)


@dataclass
class Action:
    """动作配置"""
    action_type: str              # respond, recommend, play, remind, etc.
    content: str                  # 响应内容
    delay_seconds: float = 0     # 延迟响应
    probability: float = 1.0     # 执行概率


@dataclass
class Message:
    """群聊消息"""
    id: str
    author: str
    content: str
    timestamp: float = field(default_factory=time.time)
    is_human: bool = True
    metadata: Dict = field(default_factory=dict)


class ProactiveAgent:
    """
    主动介入智能体
    
    核心能力：
    1. 监听群聊
    2. 理解上下文
    3. 决策是否介入
    4. 执行动作
    """
    
    def __init__(self, agent: Agent, name: str = None):
        self.agent = agent
        self.name = name or agent.config.name
        
        # 配置
        self.config = {
            "max_response_length": 200,    # 最大响应长度
            "min_interval": 30,            # 最小介入间隔(秒)
            "cooldown": 60,                # 冷却时间
            "max_daily_responses": 50,     # 每日最大响应数
        }
        
        # 触发器列表
        self.triggers: List[Trigger] = []
        
        # 动作响应模板
        self.response_templates: Dict[str, List[str]] = {
            "greeting": ["大家好！", "来了来了~", "嗨"],
            "agree": ["同意！", "说得对", "+1"],
            "question": ["我在思考这个问题...", "好问题！"],
            "help": ["需要帮忙吗？", "有什么我能帮的？"],
            "default": ["嗯嗯", "确实", "可以的"]
        }
        
        # 状态追踪
        self.last_response_time = 0
        self.daily_response_count = 0
        self.last_reset_date = time.strftime("%Y-%m-%d")
        self.conversation_context: List[Message] = []
        
        # 注册的动作处理器
        self.action_handlers: Dict[str, Callable] = {}
        
        # 默认设置一些触发器
        self._setup_default_triggers()
    
    def _setup_default_triggers(self):
        """设置默认触发器"""
        # 关键词触发 - 被@时
        self.add_trigger(Trigger(
            trigger_type=TriggerType.KEYWORD,
            keywords=[self.name, "艾特", "@"],
            config={"respond_always": True}
        ))
        
        # 问题触发 - 问号
        self.add_trigger(Trigger(
            trigger_type=TriggerType.QUESTION,
            config={"question_mark_count": 1}
        ))
        
        # 沉默触发 - 5分钟无消息
        self.add_trigger(Trigger(
            trigger_type=TriggerType.SILENCE,
            silence_seconds=300,
            config={"action_type": "break_silence"}
        ))
    
    def add_trigger(self, trigger: Trigger):
        """添加触发器"""
        self.triggers.append(trigger)
    
    def register_action_handler(self, action_type: str, handler: Callable):
        """注册动作处理器"""
        self.action_handlers[action_type] = handler
    
    def on_message(self, message: Message) -> Optional[Action]:
        """
        处理新消息 - 核心方法
        
        返回 Action 或 None
        """
        # 添加到上下文
        self.conversation_context.append(message)
        
        # 保持上下文长度
        max_context = 20
        if len(self.conversation_context) > max_context:
            self.conversation_context = self.conversation_context[-max_context:]
        
        # 检查冷却
        if not self._check_cooldown():
            return None
        
        # 检查每日限制
        if not self._check_daily_limit():
            return None
        
        # 决策是否介入
        decision = self._should_respond(message)
        
        if decision.should_respond:
            action = self._generate_action(message, decision)
            self._update_response_state()
            return action
        
        return None
    
    def _check_cooldown(self) -> bool:
        """检查冷却"""
        now = time.time()
        if now - self.last_response_time < self.config["cooldown"]:
            return False
        return True
    
    def _check_daily_limit(self) -> bool:
        """检查每日限制"""
        today = time.strftime("%Y-%m-%d")
        if today != self.last_reset_date:
            self.daily_response_count = 0
            self.last_reset_date = today
        
        if self.daily_response_count >= self.config["max_daily_responses"]:
            return False
        return True
    
    def _should_respond(self, message: Message) -> 'ResponseDecision':
        """决策是否响应"""
        decision = ResponseDecision(should_respond=False, reason="", confidence=0.0)
        
        # 跳过自己的消息
        if message.author == self.name:
            return decision
        
        for trigger in self.triggers:
            if self._match_trigger(message, trigger):
                # 检查是否应该响应
                should, reason, confidence = self._evaluate_trigger(message, trigger)
                if should:
                    decision.should_respond = True
                    decision.reason = reason
                    decision.confidence = confidence
                    decision.trigger = trigger
                    return decision
        
        return decision
    
    def _match_trigger(self, message: Message, trigger: Trigger) -> bool:
        """匹配触发器"""
        if trigger.trigger_type == TriggerType.KEYWORD:
            return self._match_keyword(message, trigger)
        elif trigger.trigger_type == TriggerType.QUESTION:
            return self._match_question(message)
        elif trigger.trigger_type == TriggerType.SILENCE:
            return self._match_silence(message, trigger)
        elif trigger.trigger_type == TriggerType.RANDOM:
            return self._match_random(trigger)
        elif trigger.trigger_type == TriggerType.EMOTION:
            return self._match_emotion(message, trigger)
        
        return False
    
    def _match_keyword(self, message: Message, trigger: Trigger) -> bool:
        """关键词匹配"""
        content = message.content
        if not trigger.case_sensitive:
            content = content.lower()
            trigger.keywords = [k.lower() for k in trigger.keywords]
        
        for keyword in trigger.keywords:
            if keyword in content:
                return True
        return False
    
    def _match_question(self, message: Message) -> bool:
        """问题匹配"""
        # 检查问号
        if "？" in message.content or "?" in message.content:
            return True
        return False
    
    def _match_silence(self, message: Message, trigger: Trigger) -> bool:
        """沉默匹配 - 如果消息间隔超过阈值"""
        if len(self.conversation_context) < 2:
            return False
        
        last_msg = self.conversation_context[-2]
        gap = message.timestamp - last_msg.timestamp
        
        return gap > trigger.silence_seconds
    
    def _match_random(self, trigger: Trigger) -> bool:
        """随机匹配"""
        import random
        return random.random() < trigger.probability
    
    def _match_emotion(self, message: Message, trigger: Trigger) -> bool:
        """情绪匹配 - 简单版：检测感叹号、表情等"""
        content = message.content
        
        # 简单情绪检测
        if "！" in content or "!" in content:
            return "positive" in trigger.emotions or "negative" in trigger.emotions
        
        # 检测表情符号
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]'
        if re.search(emoji_pattern, content):
            return "positive" in trigger.emotions
        
        return False
    
    def _evaluate_trigger(self, message: Message, trigger: Trigger) -> tuple:
        """评估触发器，决定是否响应"""
        
        if trigger.trigger_type == TriggerType.KEYWORD:
            # 检查配置
            if trigger.config.get("respond_always"):
                return True, "被@", 0.9
        
        elif trigger.trigger_type == TriggerType.QUESTION:
            # 问题给予更高优先级
            return True, "问题是", 0.7
        
        elif trigger.trigger_type == TriggerType.SILENCE:
            return True, "打破沉默", 0.5
        
        elif trigger.trigger_type == TriggerType.RANDOM:
            return True, "随机", 0.3
        
        return False, "", 0.0
    
    def _generate_action(self, message: Message, decision: 'ResponseDecision') -> Action:
        """生成动作"""
        
        # 决定响应类型
        response_type = self._decide_response_type(message, decision)
        
        # 生成内容
        content = self._generate_response(message, response_type)
        
        # 决定延迟
        delay = self._calculate_delay(decision)
        
        # 决定是否执行
        probability = 1.0 if decision.confidence > 0.5 else 0.7
        
        return Action(
            action_type=response_type,
            content=content,
            delay_seconds=delay,
            probability=probability
        )
    
    def _decide_response_type(self, message: Message, decision: 'ResponseDecision') -> str:
        """决定响应类型"""
        content = message.content.lower()
        
        # 问候
        if any(w in content for w in ["你好", "hi", "hello", "嗨", "在吗"]):
            return "greeting"
        
        # 同意/支持
        if any(w in content for w in ["同意", "对", "没错", "说得对"]):
            return "agree"
        
        # 问题
        if "？" in message.content or "?" in message.content:
            return "question"
        
        # 帮助请求
        if any(w in content for w in ["帮忙", "帮", "求助", "请问"]):
            return "help"
        
        # 沉默打破
        if decision.reason == "打破沉默":
            return "break_silence"
        
        return "default"
    
    def _generate_response(self, message: Message, response_type: str) -> str:
        """生成响应内容"""
        
        # 构建上下文
        context = self._build_context()
        
        # 决定使用模板还是 AI 生成
        if response_type in self.response_templates and len(context) < 3:
            # 使用模板（简单场景）
            import random
            templates = self.response_templates[response_type]
            return random.choice(templates)
        
        # 使用 AI 生成（复杂场景）
        prompt = f"""你是一个群聊中的活跃成员 "{self.name}"。

最近的聊天记录:
{context}

最新消息: "{message.content}"

请作为 {self.agent.config.role}，给出一个自然的群聊回复。
要求：
- 简短口语化，不超过 {self.config['max_response_length']} 字
- 像真实的群友一样自然
- 如果是问题，给出有价值的回答
- 可以适当加入表情

回复:"""

        response = self.agent.chat(prompt)
        return response
    
    def _build_context(self) -> str:
        """构建上下文"""
        if not self.conversation_context:
            return ""
        
        recent = self.conversation_context[-10:]
        context = []
        for msg in recent:
            author = "我" if msg.author == self.name else msg.author
            context.append(f"{author}: {msg.content[:50]}")
        
        return "\n".join(context)
    
    def _calculate_delay(self, decision: 'ResponseDecision') -> float:
        """计算延迟 - 让响应更自然"""
        import random
        
        base_delay = 1.0  # 基础延迟 1 秒
        
        # 根据置信度调整
        if decision.confidence > 0.7:
            return base_delay + random.uniform(0, 1)
        elif decision.confidence > 0.5:
            return base_delay + random.uniform(1, 3)
        else:
            return base_delay + random.uniform(2, 5)
    
    def _update_response_state(self):
        """更新响应状态"""
        self.last_response_time = time.time()
        self.daily_response_count += 1
    
    def execute_action(self, action: Action) -> str:
        """执行动作"""
        import random
        
        # 概率检查
        if random.random() > action.probability:
            return ""  # 决定不执行
        
        # 延迟执行
        if action.delay_seconds > 0:
            time.sleep(action.delay_seconds)
        
        # 调用处理器
        if action.action_type in self.action_handlers:
            handler = self.action_handlers[action.action_type]
            return handler(action.content)
        
        # 默认返回响应
        return action.content
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "name": self.name,
            "daily_responses": self.daily_response_count,
            "last_response": self.last_response_time,
            "context_length": len(self.conversation_context),
            "triggers_count": len(self.triggers)
        }


@dataclass
class ResponseDecision:
    """响应决策"""
    should_respond: bool
    reason: str
    confidence: float
    trigger: Trigger = None


class ActiveGroupChat:
    """
    主动群聊系统
    
    管理多个主动智能体
    """
    
    def __init__(self, group_name: str):
        self.group_name = group_name
        self.agents: List[ProactiveAgent] = []
        self.messages: List[Message] = []
        self.message_handlers: List[Callable] = []
    
    def add_agent(self, agent: ProactiveAgent):
        """添加主动智能体"""
        self.agents.append(agent)
    
    def on_message(self, author: str, content: str, is_human: bool = True) -> List[Action]:
        """处理消息 - 返回所有智能体的动作"""
        
        message = Message(
            id=str(time.time()),
            author=author,
            content=content,
            is_human=is_human
        )
        
        self.messages.append(message)
        
        # 保持消息历史
        if len(self.messages) > 100:
            self.messages = self.messages[-100:]
        
        # 让每个智能体处理消息
        actions = []
        for agent in self.agents:
            action = agent.on_message(message)
            if action:
                actions.append(action)
        
        # 通知处理器
        for handler in self.message_handlers:
            handler(message, actions)
        
        return actions
    
    def simulate_message(self, author: str, content: str):
        """模拟消息 - 用于测试"""
        actions = self.on_message(author, content)
        
        print(f"\n【{author}】: {content}")
        
        for action in actions:
            response = self.agents[0].execute_action(action)
            if response:
                print(f"\n【{self.agents[0].name}】: {response}")
        
        return actions


# 便捷函数
def create_proactive_agent(agent: Agent, 
                          name: str = None,
                          triggers: List[Trigger] = None) -> ProactiveAgent:
    """创建主动智能体"""
    proactive = ProactiveAgent(agent, name)
    
    if triggers:
        for t in triggers:
            proactive.add_trigger(t)
    
    return proactive


__all__ = [
    "ProactiveAgent",
    "ActiveGroupChat", 
    "Trigger",
    "TriggerType",
    "Action",
    "Message",
    "ResponseDecision",
    "create_proactive_agent"
]
