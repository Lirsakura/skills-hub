"""
企业微信机器人 - Teamily AI Core 接入
让 AI 智能体入驻企业微信群聊
"""

import os
import json
import time
import requests
from typing import List, Optional
from dataclasses import dataclass


class WeComBot:
    """
    企业微信机器人
    
    使用方式:
    1. 登录企业微信管理后台 https://work.weixin.qq.com/
    2. 创建自建应用
    3. 获取 CorpID、Secret、AgentID
    """
    
    def __init__(self, corp_id: str, secret: str, agent_id: str):
        self.corp_id = corp_id
        self.secret = secret
        self.agent_id = agent_id
        self.access_token = None
        self.token_expires = 0
        
        # API 地址
        self.api_host = "https://qyapi.weixin.qq.com"
    
    def _get_access_token(self) -> str:
        """获取 access_token"""
        now = time.time()
        if self.access_token and now < self.token_expires:
            return self.access_token
        
        url = f"{self.api_host}/cgi-bin/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.secret
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("errcode") == 0:
            self.access_token = data["access_token"]
            self.token_expires = now + data["expires_in"] - 300
            return self.access_token
        else:
            raise Exception(f"获取 access_token 失败: {data}")
    
    def send_text(self, user_id: str, content: str):
        """发送文本消息给用户"""
        token = self._get_access_token()
        
        url = f"{self.api_host}/cgi-bin/message/send"
        params = {"access_token": token}
        
        data = {
            "touser": user_id,
            "msgtype": "text",
            "agentid": self.agent_id,
            "text": {"content": content}
        }
        
        response = requests.post(url, params=params, json=data, timeout=10)
        result = response.json()
        
        if result.get("errcode") != 0:
            print(f"发送失败: {result}")
        return result
    
    def send_to_group(self, chat_id: str, content: str):
        """发送消息到群聊"""
        token = self._get_access_token()
        
        url = f"{self.api_host}/cgi-bin/appchat/send"
        params = {"access_token": token}
        
        data = {
            "chatid": chat_id,
            "msgtype": "text",
            "text": {"content": content}
        }
        
        response = requests.post(url, params=params, json=data, timeout=10)
        return response.json()
    
    def create_group(self, name: str, owner: str, user_list: List[str]) -> str:
        """创建群聊"""
        token = self._get_access_token()
        
        url = f"{self.api_host}/cgi-bin/appchat/create"
        params = {"access_token": token}
        
        data = {
            "name": name,
            "owner": owner,
            "userlist": user_list
        }
        
        response = requests.post(url, params=params, json=data, timeout=10)
        result = response.json()
        
        if result.get("errcode") == 0:
            return result["chatid"]
        else:
            raise Exception(f"创建群聊失败: {result}")
    
    def get_callback_ip(self) -> List[str]:
        """获取企业微信服务器 IP"""
        token = self._get_access_token()
        
        url = f"{self.api_host}/cgi-bin/getcallbackip"
        params = {"access_token": token}
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("errcode") == 0:
            return data["ip_list"]
        return []


class WeComMessageHandler:
    """
    企业微信消息处理器
    
    对接 Teamily AI Core 的主动介入智能体
    """
    
    def __init__(self, corp_id: str, secret: str, agent_id: str):
        self.bot = WeComBot(corp_id, secret, agent_id)
        self.agent = None  # ProactiveAgent
        self.group_chat_id = None
        
        # 消息队列
        self.message_cache = {}
    
    def set_agent(self, agent):
        """设置主动介入智能体"""
        self.agent = agent
    
    def set_group(self, chat_id: str):
        """设置群聊 ID"""
        self.group_chat_id = chat_id
    
    def handle_message(self, msg_data: dict) -> Optional[str]:
        """
        处理收到的消息
        
        企业微信回调消息格式:
        {
            "msgtype": "text",
            "from_user_name": "用户A",
            "content": "消息内容",
            "agent_id": "agentid",
            ...
        }
        """
        msg_type = msg_data.get("msgtype")
        
        if msg_type == "text":
            return self._handle_text(msg_data)
        elif msg_type == "event":
            return self._handle_event(msg_data)
        
        return None
    
    def _handle_text(self, msg_data: dict) -> Optional[str]:
        """处理文本消息"""
        # 解析消息
        from_user = msg_data.get("from_user_name", "unknown")
        content = msg_data.get("content", "")
        
        print(f"收到消息 from {from_user}: {content[:50]}...")
        
        # 如果设置了智能体，让它处理
        if self.agent:
            # 模拟 ProactiveAgent 的 Message 格式
            from scripts.proactive_agent import Message
            
            msg = Message(
                id=str(time.time()),
                author=from_user,
                content=content,
                is_human=True
            )
            
            # 获取响应
            action = self.agent.on_message(msg)
            
            if action:
                response = self.agent.execute_action(action)
                
                # 发送到群聊
                if self.group_chat_id:
                    self.bot.send_to_group(
                        self.group_chat_id, 
                        f"@{from_user} {response}"
                    )
                
                return response
        
        return None
    
    def _handle_event(self, msg_data: dict) -> Optional[str]:
        """处理事件消息"""
        event_type = msg_data.get("event", "")
        
        if event_type == "enter_agent":
            # 用户进入应用
            return "你好！我是 AI 助手，有什么可以帮你的？"
        
        return None
    
    def start_callback_server(self, port: int = 8000):
        """
        启动回调服务器
        
        需要配置企业微信的回调 URL 指向此服务器
        """
        # 这个需要配合 Web 框架使用，如 Flask/FastAPI
        # 这里只提供处理逻辑
        print(f"回调服务器需要 Web 框架支持，请使用 run_callback_server()")
    
    def reply_to_user(self, user_id: str, content: str):
        """回复用户"""
        self.bot.send_text(user_id, content)


def create_wecom_bot(corp_id: str = None, secret: str = None, agent_id: str = None):
    """
    创建企业微信机器人
    
    环境变量:
    - WECOM_CORP_ID
    - WECOM_SECRET
    - WECOM_AGENT_ID
    """
    corp_id = corp_id or os.getenv("WECOM_CORP_ID")
    secret = secret or os.getenv("WECOM_SECRET")
    agent_id = agent_id or os.getenv("WECOM_AGENT_ID")
    
    if not all([corp_id, secret, agent_id]):
        raise ValueError("缺少企业微信配置，请设置环境变量或传入参数")
    
    return WeComBot(corp_id, secret, agent_id)


# 完整示例
def demo():
    """完整示例"""
    from scripts.agent_manager import AgentManager
    from scripts.proactive_agent import ProactiveAgent
    
    # 1. 创建 AI 智能体
    manager = AgentManager()
    agent = manager.create_agent(
        "小助手",
        "meta/llama-3.1-70b-instruct",
        "企业微信群里的活跃助手"
    )
    
    # 2. 创建主动介入智能体
    proactive = ProactiveAgent(agent, "小助手")
    proactive.config["cooldown"] = 10  # 10秒冷却
    
    # 3. 创建企业微信处理器
    handler = WeComMessageHandler(
        corp_id=os.getenv("WECOM_CORP_ID", ""),
        secret=os.getenv("WECOM_SECRET", ""),
        agent_id=os.getenv("WECOM_AGENT_ID", "")
    )
    
    # 4. 对接
    handler.set_agent(proactive)
    handler.set_group("your_group_chat_id")
    
    # 5. 处理消息（企业微信回调）
    # msg = {"msgtype": "text", "from_user_name": "张三", "content": "推荐一部电影"}
    # handler.handle_message(msg)
    
    print("企业微信机器人已配置完成！")
    print("需要配置企业微信:")
    print("1. 登录 https://work.weixin.qq.com/")
    print("2. 创建自建应用")
    print("3. 设置可信 IP")
    print("4. 配置回调 URL")


__all__ = ["WeComBot", "WeComMessageHandler", "create_wecom_bot", "demo"]
