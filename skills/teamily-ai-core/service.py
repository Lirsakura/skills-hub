"""
Teamily AI Core - 服务入口
24/7 运行，支持企业微信、消息监听
"""

import os
import sys
import time
import json
import signal
from datetime import datetime

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from agent_manager import AgentManager
from group_manager import GroupManager
from memory_store import MemoryStore
from wecom_integration import WeComBot


class TeamilyService:
    """Teamily AI Core 服务"""
    
    def __init__(self):
        self.running = False
        self.agent_mgr = AgentManager()
        self.group_mgr = GroupManager()
        self.memory = MemoryStore()
        self.wecom = None
        
        # 加载配置
        self.config = self._load_config()
        
        # 信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self):
        """加载配置"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "wecom_enabled": True,
            "auto_reply": True,
            "listen_groups": []
        }
    
    def _signal_handler(self, signum, frame):
        """处理退出信号"""
        print("\n🛑 收到停止信号，正在关闭...")
        self.running = False
    
    def start(self):
        """启动服务"""
        self.running = True
        
        print("=" * 50)
        print("🤖 Teamily AI Core 服务启动")
        print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # 初始化 Agent
        print("\n📡 初始化智能体...")
        agents = self.agent_mgr.list_available_agents()
        print(f"   已加载 {len(agents)} 个智能体")
        
        # 初始化群组
        print("\n📂 加载群组...")
        groups = self.group_mgr.list_groups()
        print(f"   已加载 {len(groups)} 个群组")
        
        # 启动企业微信监听
        if self.config.get("wecom_enabled", True):
            print("\n💬 启动企业微信监听...")
            try:
                self.wecom = WeComBot()
                self.wecom.start_listening()
                print("   ✅ 企业微信已连接")
            except Exception as e:
                print(f"   ⚠️ 企业微信连接失败: {e}")
        else:
            print("\n⏭️ 企业微信已禁用")
        
        print("\n" + "=" * 50)
        print("✅ 服务运行中... (按 Ctrl+C 停止)")
        print("=" * 50)
        
        # 主循环
        self._main_loop()
    
    def _main_loop(self):
        """主循环"""
        while self.running:
            try:
                # 处理待处理任务
                self._process_tasks()
                
                # 检查企业微信消息
                if self.wecom and self.wecom.is_running:
                    self._check_wecom_messages()
                
                # 休眠
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ 错误: {e}")
                time.sleep(5)
    
    def _process_tasks(self):
        """处理任务队列"""
        # TODO: 实现任务队列处理
        pass
    
    def _check_wecom_messages(self):
        """检查企业微信消息"""
        # TODO: 实现消息检查
        pass
    
    def stop(self):
        """停止服务"""
        self.running = False
        
        if self.wecom:
            self.wecom.stop_listening()
        
        print("\n✅ 服务已停止")


def main():
    """主入口"""
    service = TeamilyService()
    service.start()


if __name__ == "__main__":
    main()
