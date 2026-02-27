"""
Teamily AI Core - GUI 自动化模块
集成 PyAutoGUI 实现桌面自动化
"""

import os
import sys
import json
import time
from typing import Optional, Tuple, List, Dict

# 自动安装依赖
try:
    import pyautogui
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pyautogui", "-q"])
    import pyautogui

# 安全设置
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5


class GUIAutomation:
    """
    GUI 自动化工具
    
    让 AI 能够控制鼠标、键盘、截图等
    """
    
    def __init__(self):
        self.screen_size = pyautogui.size()
    
    def get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕分辨率"""
        return self.screen_size
    
    def get_mouse_position(self) -> Dict:
        """获取鼠标当前位置"""
        x, y = pyautogui.position()
        return {"x": x, "y": y, "screen_width": self.screen_size[0], "screen_height": self.screen_size[1]}
    
    def move_mouse(self, x: int, y: int, duration: float = 0) -> bool:
        """移动鼠标"""
        pyautogui.moveTo(x, y, duration=duration)
        return True
    
    def click(self, x: int = None, y: int = None, 
              button: str = "left", clicks: int = 1) -> bool:
        """点击鼠标"""
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, button=button)
        else:
            pyautogui.click(clicks=clicks, button=button)
        return True
    
    def double_click(self, x: int = None, y: int = None) -> bool:
        """双击"""
        return self.click(x, y, clicks=2)
    
    def right_click(self, x: int = None, y: int = None) -> bool:
        """右键点击"""
        return self.click(x, y, button="right")
    
    def type_text(self, text: str, interval: float = 0) -> bool:
        """输入文本"""
        pyautogui.typewrite(text, interval=interval)
        return True
    
    def press_key(self, key: str) -> bool:
        """按键"""
        pyautogui.press(key)
        return True
    
    def hotkey(self, *keys) -> bool:
        """组合键"""
        pyautogui.hotkey(*keys)
        return True
    
    def screenshot(self, filename: str = None) -> str:
        """截图"""
        if filename is None:
            filename = f"screenshot_{int(time.time())}.png"
        pyautogui.screenshot(filename)
        return filename
    
    def get_pixel_color(self, x: int, y: int) -> Dict:
        """获取像素颜色"""
        color = pyautogui.pixel(x, y)
        return {
            "rgb": color,
            "hex": "#{:02x}{:02x}{:02x}".format(*color)
        }
    
    def find_color(self, rgb: Tuple[int, int, int], 
                   region: Tuple[int, int, int, int] = None,
                   tolerance: int = 0) -> Optional[Tuple[int, int]]:
        """查找颜色位置"""
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
        
        width, height = screenshot.size
        
        for x in range(width):
            for y in range(height):
                pixel = screenshot.getpixel((x, y))
                if all(abs(pixel[i] - rgb[i]) <= tolerance for i in range(3)):
                    if region:
                        return (x + region[0], y + region[1])
                    return (x, y)
        
        return None
    
    def locate_on_screen(self, image_path: str, confidence: float = 0.9) -> Optional[Dict]:
        """在屏幕上查找图片"""
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                return {
                    "left": location.left,
                    "top": location.top,
                    "width": location.width,
                    "height": location.height,
                    "center": pyautogui.center(location)
                }
        except Exception as e:
            return {"error": str(e)}
        return None
    
    def scroll(self, amount: int, x: int = None, y: int = None) -> bool:
        """滚动"""
        if x is not None and y is not None:
            pyautogui.scroll(amount, x, y)
        else:
            pyautogui.scroll(amount)
        return True


def create_automation_task(task: str, gui: GUIAutomation = None) -> Dict:
    """
    从自然语言创建自动化任务
    
    例如: "点击屏幕中央的按钮"
    """
    from scripts.agent_manager import AgentManager
    
    if gui is None:
        gui = GUIAutomation()
    
    # 获取屏幕信息
    screen = gui.get_screen_size()
    mouse_pos = gui.get_mouse_position()
    
    # 让 AI 决定具体操作
    manager = AgentManager()
    agent = manager.create_agent(
        "自动化助手",
        "meta/llama-3.1-70b-instruct",
        "擅长自动化任务的AI助手"
    )
    
    prompt = f"""屏幕分辨率: {screen}
鼠标位置: {mouse_pos}

用户要求: {task}

请给出具体的自动化操作步骤。例如：
- 如果要点击按钮: click --x 100 --y 200
- 如果要输入文字: type_text --text "内容"
- 如果要按快捷键: hotkey --keys ctrl,v

只返回操作命令，不需要解释。"""
    
    response = agent.chat(prompt)
    
    return {
        "task": task,
        "ai_suggestion": response,
        "screen_size": screen,
        "mouse_position": mouse_pos
    }


# 便捷函数
automation = GUIAutomation()

__all__ = ["GUIAutomation", "automation", "create_automation_task"]
