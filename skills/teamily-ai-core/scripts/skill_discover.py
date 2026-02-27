"""
Teamily AI Core - 技能发现与自动加载
自动从官方技能库和网上搜索相关技能
"""

import os
import json
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class AvailableSkill:
    """可用技能"""
    name: str
    path: str
    description: str
    category: str


class SkillDiscover:
    """
    技能发现系统
    
    功能：
    1. 扫描本地技能库
    2. 根据需求搜索相关技能
    3. 自动加载和使用技能
    """
    
    def __init__(self):
        self.skills_dir = os.path.expanduser("~/.config/opencode/skills")
        self.skillshub_dir = os.path.expanduser("~/.skillshub")
        self.available_skills: List[AvailableSkill] = []
        
        # 扫描可用技能
        self._scan_skills()
    
    def _scan_skills(self):
        """扫描所有可用技能"""
        
        # 扫描 skills 目录
        if os.path.exists(self.skills_dir):
            for item in os.listdir(self.skills_dir):
                path = os.path.join(self.skills_dir, item)
                if os.path.isdir(path):
                    skill = self._parse_skill_dir(item, path)
                    if skill:
                        self.available_skills.append(skill)
        
        # 扫描 skillshub 目录
        if os.path.exists(self.skillshub_dir):
            for item in os.listdir(self.skillshub_dir):
                path = os.path.join(self.skillshub_dir, item)
                if os.path.isdir(path):
                    skill = self._parse_skill_dir(item, path)
                    if skill:
                        self.available_skills.append(skill)
    
    def _parse_skill_dir(self, name: str, path: str) -> Optional[AvailableSkill]:
        """解析技能目录"""
        skill_file = os.path.join(path, "SKILL.md")
        
        if os.path.exists(skill_file):
            try:
                with open(skill_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # 提取描述
                description = ""
                for line in content.split("\n"):
                    if line.startswith("description:"):
                        description = line.split(":", 1)[1].strip()
                        break
                
                # 推断分类
                category = self._infer_category(name, description)
                
                return AvailableSkill(
                    name=name,
                    path=path,
                    description=description,
                    category=category
                )
            except:
                pass
        
        return None
    
    def _infer_category(self, name: str, description: str) -> str:
        """推断分类"""
        text = (name + " " + description).lower()
        
        if any(k in text for k in ["image", "图片", "画", "设计"]):
            return "design"
        elif any(k in text for k in ["video", "视频", "剪辑"]):
            return "video"
        elif any(k in text for k in ["document", "文档", "pdf", "word"]):
            return "document"
        elif any(k in text for k in ["data", "分析", "chart"]):
            return "data"
        elif any(k in text for k in ["web", "browser", "浏览器"]):
            return "web"
        elif any(k in text for k in ["code", "开发", "编程"]):
            return "coding"
        else:
            return "other"
    
    def search(self, query: str) -> List[AvailableSkill]:
        """搜索相关技能"""
        query_lower = query.lower()
        results = []
        
        for skill in self.available_skills:
            # 计算相关性
            score = 0
            
            # 名称匹配
            if query_lower in skill.name.lower():
                score += 10
            
            # 描述匹配
            if query_lower in skill.description.lower():
                score += 5
            
            # 关键词匹配
            keywords = query_lower.split()
            for kw in keywords:
                if kw in skill.name.lower() or kw in skill.description.lower():
                    score += 2
            
            if score > 0:
                results.append((skill, score))
        
        # 按相关性排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return [r[0] for r in results]
    
    def find_skill_for_task(self, task: str) -> Optional[AvailableSkill]:
        """
        根据任务自动找到合适的技能
        
        例如：
        - task: "生成一张图片" -> 返回图片生成技能
        - task: "分析这个PDF" -> 返回文档处理技能
        """
        # 搜索相关技能
        results = self.search(task)
        
        if results:
            return results[0]
        
        return None
    
    def get_all_skills(self) -> List[AvailableSkill]:
        """获取所有技能"""
        return self.available_skills
    
    def list_by_category(self, category: str) -> List[AvailableSkill]:
        """按分类列出技能"""
        return [s for s in self.available_skills if s.category == category]
    
    def get_skill_path(self, name: str) -> Optional[str]:
        """获取技能路径"""
        for skill in self.available_skills:
            if skill.name == name:
                return skill.path
        return None


# 全局实例
_discover = None

def get_skill_discover() -> SkillDiscover:
    """获取技能发现实例"""
    global _discover
    if _discover is None:
        _discover = SkillDiscover()
    return _discover


# 使用示例
def auto_solve_task(task: str) -> Dict:
    """
    自动解决任务 - 核心功能
    
    1. 分析任务
    2. 搜索相关技能
    3. 返回建议
    """
    discover = get_skill_discover()
    
    # 搜索相关技能
    related_skills = discover.search(task)
    
    # 找到最佳匹配
    best_skill = related_skills[0] if related_skills else None
    
    return {
        "task": task,
        "found_skills": [
            {"name": s.name, "description": s.description}
            for s in related_skills[:5]
        ],
        "recommended": {
            "name": best_skill.name,
            "path": best_skill.path,
            "description": best_skill.description
        } if best_skill else None
    }


__all__ = ["SkillDiscover", "AvailableSkill", "get_skill_discover", "auto_solve_task"]
