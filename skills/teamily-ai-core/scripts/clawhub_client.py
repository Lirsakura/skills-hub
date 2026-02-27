"""
Teamily AI Core - ClawHub 技能市场客户端
接入 OpenClaw 官方技能市场 (3000+ 技能)
"""

import json
import subprocess
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import urllib.request
import urllib.parse


@dataclass
class ClawHubSkill:
    """ClawHub 技能定义"""
    name: str
    description: str
    category: str
    author: str
    stars: int
    tags: List[str]
    repo_url: str
    installed: bool = False


class ClawHubMarket:
    """
    ClawHub 技能市场客户端
    
    功能：
    - 搜索 ClawHub 技能
    - 安装/卸载技能
    - 列出已安装技能
    """
    
    def __init__(self, skills_dir: str = None):
        self.skills_dir = skills_dir or os.path.expanduser("~/.claude/skills")
        self.cache_file = os.path.expanduser("~/.teamily_clawhub_cache.json")
        self.cached_skills: List[ClawHubSkill] = []
    
    def search(self, query: str, category: str = None) -> List[ClawHubSkill]:
        """
        搜索 ClawHub 技能
        
        Args:
            query: 搜索关键词
            category: 可选，按分类筛选
            
        Returns:
            技能列表
        """
        # 使用 ClawHub API 搜索
        # 注意：这是模拟实现，实际需要根据 ClawHub API 调整
        base_url = "https://api.clawhub.io/skills/search"
        params = {"q": query}
        if category:
            params["category"] = category
        
        try:
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            # 实际 API 调用
            # response = urllib.request.urlopen(url)
            # data = json.loads(response.read())
            
            # 返回示例数据（实际使用时替换为真实 API）
            return self._get_mock_skills(query)
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def _get_mock_skills(self, query: str) -> List[ClawHubSkill]:
        """返回模拟技能数据（实际使用时应替换为真实 API）"""
        mock_skills = [
            ClawHubSkill(
                name="gmail",
                description="发送和读取 Gmail 邮件，管理邮件标签",
                category="communication",
                author="openclaw",
                stars=1250,
                tags=["email", "gmail", "google"],
                repo_url="https://github.com/openclaw-skills/gmail"
            ),
            ClawHubSkill(
                name="github",
                description="GitHub 操作：创建 issue、PR、代码审查",
                category="developer",
                author="openclaw",
                stars=980,
                tags=["github", "git", "devops"],
                repo_url="https://github.com/openclaw-skills/github"
            ),
            ClawHubSkill(
                name="slack",
                description="Slack 消息发送和频道管理",
                category="communication",
                author="openclaw",
                stars=856,
                tags=["slack", "chat", "team"],
                repo_url="https://github.com/openclaw-skills/slack"
            ),
            ClawHubSkill(
                name="notion",
                description="Notion 页面创建、编辑和管理",
                category="productivity",
                author="openclaw",
                stars=723,
                tags=["notion", "wiki", "notes"],
                repo_url="https://github.com/openclaw-skills/notion"
            ),
            ClawHubSkill(
                name="google-search",
                description="Google 搜索和新闻获取",
                category="research",
                author="openclaw",
                stars=654,
                tags=["search", "google", "web"],
                repo_url="https://github.com/openclaw-skills/google-search"
            ),
            ClawHubSkill(
                name="spotify",
                description="播放音乐、控制 Spotify",
                category="entertainment",
                author="openclaw",
                stars=543,
                tags=["music", "spotify", "audio"],
                repo_url="https://github.com/openclaw-skills/spotify"
            ),
            ClawHubSkill(
                name="calendar",
                description="Google 日历事件管理",
                category="productivity",
                author="openclaw",
                stars=489,
                tags=["calendar", "schedule", "google"],
                repo_url="https://github.com/openclaw-skills/calendar"
            ),
            ClawHubSkill(
                name="youtube",
                description="YouTube 视频搜索和播放",
                category="entertainment",
                author="openclaw",
                stars=432,
                tags=["youtube", "video", "streaming"],
                repo_url="https://github.com/openclaw-skills/youtube"
            ),
            ClawHubSkill(
                name="twitter",
                description="Twitter/X 发推和搜索",
                category="social",
                author="openclaw",
                stars=398,
                tags=["twitter", "social", "x"],
                repo_url="https://github.com/openclaw-skills/twitter"
            ),
            ClawHubSkill(
                name="database",
                description="SQL 数据库操作",
                category="developer",
                author="openclaw",
                stars=367,
                tags=["database", "sql", "postgres"],
                repo_url="https://github.com/openclaw-skills/database"
            ),
        ]
        
        # 根据查询过滤
        query_lower = query.lower()
        return [s for s in mock_skills if query_lower in s.name.lower() or query_lower in s.description.lower()]
    
    def install(self, skill_name: str) -> bool:
        """
        安装技能
        
        Args:
            skill_name: 技能名称
            
        Returns:
            是否安装成功
        """
        # 方法1：使用 git clone
        skill_url = f"https://github.com/openclaw-skills/{skill_name}.git"
        target_dir = os.path.join(self.skills_dir, skill_name)
        
        if os.path.exists(target_dir):
            print(f"技能 {skill_name} 已安装")
            return True
        
        try:
            # 克隆技能仓库
            result = subprocess.run(
                ["git", "clone", skill_url, target_dir],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"✓ 技能 {skill_name} 安装成功")
                return True
            else:
                print(f"✗ 安装失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ 安装失败: {e}")
            return False
    
    def uninstall(self, skill_name: str) -> bool:
        """
        卸载技能
        
        Args:
            skill_name: 技能名称
            
        Returns:
            是否卸载成功
        """
        target_dir = os.path.join(self.skills_dir, skill_name)
        
        if not os.path.exists(target_dir):
            print(f"技能 {skill_name} 未安装")
            return True
        
        try:
            import shutil
            shutil.rmtree(target_dir)
            print(f"✓ 技能 {skill_name} 已卸载")
            return True
        except Exception as e:
            print(f"✗ 卸载失败: {e}")
            return False
    
    def list_installed(self) -> List[str]:
        """列出已安装的技能"""
        if not os.path.exists(self.skills_dir):
            return []
        
        installed = []
        for item in os.listdir(self.skills_dir):
            item_path = os.path.join(self.skills_dir, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "SKILL.md")):
                installed.append(item)
        
        return installed
    
    def get_categories(self) -> Dict[str, int]:
        """获取技能分类统计"""
        categories = {
            "communication": 0,
            "developer": 0,
            "productivity": 0,
            "research": 0,
            "social": 0,
            "entertainment": 0,
            "finance": 0,
            "other": 0
        }
        
        for skill in self.cached_skills:
            cat = skill.category if skill.category in categories else "other"
            categories[cat] += 1
        
        return categories


def demo():
    """演示 ClawHub 技能市场"""
    market = ClawHubMarket()
    
    print("=" * 50)
    print("ClawHub 技能市场演示")
    print("=" * 50)
    
    # 搜索技能
    print("\n📦 搜索 'email' 相关技能:")
    skills = market.search("email")
    for s in skills:
        print(f"  - {s.name}: {s.description}")
        print(f"    ⭐ {s.stars} | 作者: {s.author}")
    
    # 列出已安装
    print("\n✅ 已安装的技能:")
    installed = market.list_installed()
    if installed:
        for s in installed:
            print(f"  - {s}")
    else:
        print("  (暂无)")
    
    # 分类统计
    print("\n📊 分类统计:")
    cats = market.get_categories()
    for cat, count in cats.items():
        print(f"  - {cat}: {count}")


if __name__ == "__main__":
    demo()
