"""
Teamily AI Core - Agent Manager
智能体生命周期管理
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

class ModelProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    NVIDIA = "nvidia"

    @property
    def is_openai_compatible(self):
        return self in (ModelProvider.OPENAI, ModelProvider.OPENROUTER, ModelProvider.NVIDIA)

@dataclass
class AgentConfig:
    name: str
    model: str
    role: str
    tools: List[str] = field(default_factory=list)
    system_prompt: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096

class Agent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.provider = self._get_provider(config.model)
        self._client = None
    
    def _get_provider(self, model: str) -> ModelProvider:
        # 检查是否使用 OpenRouter
        if model.startswith("openrouter/"):
            return ModelProvider.OPENROUTER
        elif "/" in model:
            # 检查是否是 NVIDIA 模型
            if model.startswith("meta/") or model.startswith("mistralai/") or model.startswith("nvidia/"):
                return ModelProvider.NVIDIA
            return ModelProvider.OPENROUTER
        elif model.startswith("claude"):
            return ModelProvider.ANTHROPIC
        return ModelProvider.OPENAI
    
    def _get_client(self):
        if self._client is None:
            if self.provider == ModelProvider.ANTHROPIC:
                import anthropic
                self._client = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
            elif self.provider == ModelProvider.NVIDIA:
                # 使用 LangChain NVIDIA wrapper
                from langchain_nvidia_ai_endpoints import ChatNVIDIA
                self._client = ChatNVIDIA(
                    model=self.config.model,
                    nvidia_api_key=os.getenv("NVIDIA_API_KEY")
                )
            else:
                import openai
                # 根据 provider 选择 API key
                api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
                
                openai.api_key = api_key
                
                # OpenRouter 使用自定义端点
                if self.provider == ModelProvider.OPENROUTER:
                    openai.base_url = "https://openrouter.ai/api/v1"
                
                self._client = openai
        return self._client
    
    def chat(self, message: str, context: Dict = None) -> str:
        client = self._get_client()
        
        # LangChain NVIDIA wrapper
        if self.provider == ModelProvider.NVIDIA:
            # 构建消息
            messages = []
            if self.config.system_prompt or self.config.role:
                messages.append(("system", self.config.system_prompt or self.config.role))
            messages.append(("user", message))
            
            # 重新创建 client 以确保使用正确的模型
            from langchain_nvidia_ai_endpoints import ChatNVIDIA
            llm = ChatNVIDIA(
                model=self.config.model,
                nvidia_api_key=os.getenv("NVIDIA_API_KEY")
            )
            result = llm.invoke(messages)
            return result.content
        
        # 提取实际模型名称
        model = self.config.model
        if "/" in model:
            model = model.split("/")[-1]
        
        if self.provider == ModelProvider.ANTHROPIC:
            response = client.messages.create(
                model=model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=self.config.system_prompt or self.config.role,
                messages=[{"role": "user", "content": message}]
            )
            return response.content[0].text
        else:
            # OpenAI compatible (OpenAI, OpenRouter)
            try:
                response = client.chat.completions.create(
                    model=model,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    messages=[
                        {"role": "system", "content": self.config.system_prompt or self.config.role},
                        {"role": "user", "content": message}
                    ]
                )
                if hasattr(response, 'choices'):
                    return response.choices[0].message.content
                return str(response)
            except Exception as e:
                return f"Error: {str(e)}"
    
    def tool_call(self, tool_name: str, **kwargs) -> Any:
        """调用工具"""
        # TODO: 实现工具调用逻辑
        pass
    
    def __repr__(self):
        return f"Agent({self.config.name}, {self.config.model})"


class AgentManager:
    """智能体管理器"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
    
    def create_agent(self, name: str, model: str, role: str, **kwargs) -> Agent:
        config = AgentConfig(
            name=name,
            model=model,
            role=role,
            **kwargs
        )
        agent = Agent(config)
        self.agents[name] = agent
        return agent
    
    def get_agent(self, name: str) -> Optional[Agent]:
        return self.agents.get(name)
    
    def list_agents(self) -> List[Agent]:
        return list(self.agents.values())
    
    def remove_agent(self, name: str):
        if name in self.agents:
            del self.agents[name]


if __name__ == "__main__":
    # 示例用法
    manager = AgentManager()
    
    # 创建智能体
    researcher = manager.create_agent(
        name="Researcher",
        model="claude-sonnet-4-20250514",
        role="你是一个专业的研究员，擅长信息收集和分析"
    )
    
    writer = manager.create_agent(
        name="Writer", 
        model="gpt-4o",
        role="你是一个专业的技术作家，擅长撰写技术文档"
    )
    
    # 测试对话
    result = researcher.chat("请介绍一下人工智能的发展历史")
    print(f"Researcher: {result[:200]}...")
