---
name: map-generator
description: 绘制旅行路线地图。当需要可视化行程路线、生成地图图片时使用。
---

# 地图绘制指南

## 功能说明

使用 Python 生成旅行路线地图，保存为图片文件。

## 实现方式

### 方式一：使用 folium（交互式HTML地图）

```python
import folium
from folium import plugins
import os

def create_travel_map(locations, output_path="旅行计划/route_map.html"):
    """
    创建旅行路线地图
    
    locations: list of dict, 每个包含:
        - name: 地点名称
        - lat: 纬度
        - lon: 经度
        - day: 第几天（可选）
        - type: 类型（景点/酒店/餐厅）
    """
    
    # 计算地图中心
    center_lat = sum(loc['lat'] for loc in locations) / len(locations)
    center_lon = sum(loc['lon'] for loc in locations) / len(locations)
    
    # 创建地图
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # 颜色映射
    colors = {
        '景点': 'red',
        '酒店': 'blue', 
        '餐厅': 'orange',
        '交通': 'gray'
    }
    
    # 添加标记点
    for i, loc in enumerate(locations):
        color = colors.get(loc.get('type', '景点'), 'red')
        
        # 创建标记
        folium.Marker(
            location=[loc['lat'], loc['lon']],
            popup=f"<b>{loc['name']}</b><br>Day {loc.get('day', '?')}",
            tooltip=loc['name'],
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
        
        # 添加序号标签
        folium.Marker(
            location=[loc['lat'], loc['lon']],
            icon=folium.DivIcon(
                html=f'<div style="font-size: 12pt; color: white; background: {color}; border-radius: 50%; width: 24px; height: 24px; text-align: center; line-height: 24px;">{i+1}</div>'
            )
        ).add_to(m)
    
    # 绘制路线
    route_coords = [[loc['lat'], loc['lon']] for loc in locations]
    folium.PolyLine(
        route_coords,
        weight=3,
        color='blue',
        opacity=0.8
    ).add_to(m)
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 保存地图
    m.save(output_path)
    print(f"✅ 地图已保存: {output_path}")
    
    return output_path


# 使用示例
locations = [
    {"name": "景福宫 Gyeongbokgung", "lat": 37.5796, "lon": 126.9770, "day": 1, "type": "景点"},
    {"name": "北村韩屋村 Bukchon", "lat": 37.5826, "lon": 126.9850, "day": 1, "type": "景点"},
    {"name": "明洞 Myeongdong", "lat": 37.5636, "lon": 126.9869, "day": 2, "type": "景点"},
    {"name": "首尔塔 N Seoul Tower", "lat": 37.5512, "lon": 126.9882, "day": 2, "type": "景点"},
]

create_travel_map(locations, "旅行计划/首尔行程地图.html")
```

### 方式二：使用 matplotlib + cartopy（静态图片）

```python
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def create_route_image(locations, output_path="旅行计划/route_map.png", title="旅行路线图"):
    """
    创建简单的路线示意图
    """
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # 提取坐标
    lats = [loc['lat'] for loc in locations]
    lons = [loc['lon'] for loc in locations]
    names = [loc['name'] for loc in locations]
    
    # 绘制路线
    ax.plot(lons, lats, 'b-', linewidth=2, alpha=0.6, label='行程路线')
    
    # 绘制点和标注
    colors = {'景点': 'red', '酒店': 'blue', '餐厅': 'orange'}
    
    for i, loc in enumerate(locations):
        color = colors.get(loc.get('type', '景点'), 'red')
        ax.scatter(loc['lon'], loc['lat'], c=color, s=100, zorder=5)
        ax.annotate(
            f"{i+1}. {loc['name']}", 
            (loc['lon'], loc['lat']),
            xytext=(10, 10),
            textcoords='offset points',
            fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7)
        )
    
    # 设置标题和标签
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('经度 Longitude')
    ax.set_ylabel('纬度 Latitude')
    
    # 添加图例
    ax.legend(loc='upper right')
    
    # 添加网格
    ax.grid(True, alpha=0.3)
    
    # 设置边界（留一点边距）
    margin = 0.02
    ax.set_xlim(min(lons) - margin, max(lons) + margin)
    ax.set_ylim(min(lats) - margin, max(lats) + margin)
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    # 保存图片
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 地图已保存: {output_path}")
    return output_path
```

### 方式三：生成文字版路线图（无需依赖）

```python
def create_text_route_map(locations, output_path="旅行计划/route_map.txt"):
    """
    创建文字版路线示意图（无需任何库）
    """
    
    output = []
    output.append("=" * 60)
    output.append("🗺️ 旅行路线示意图")
    output.append("=" * 60)
    output.append("")
    
    for i, loc in enumerate(locations):
        day = loc.get('day', '?')
        loc_type = loc.get('type', '景点')
        
        # 图标
        icons = {'景点': '🏛️', '酒店': '🏨', '餐厅': '🍜', '交通': '🚗'}
        icon = icons.get(loc_type, '📍')
        
        output.append(f"  {icon} [{i+1}] {loc['name']}")
        output.append(f"      Day {day} | {loc_type}")
        output.append(f"      📍 ({loc['lat']:.4f}, {loc['lon']:.4f})")
        
        if i < len(locations) - 1:
            output.append("      │")
            output.append("      ▼")
        
        output.append("")
    
    output.append("=" * 60)
    
    content = "\n".join(output)
    
    # 保存文件
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 路线图已保存: {output_path}")
    return output_path
```

## 完整地图生成脚本

保存为 `generate_map.py`，放在行程文件夹中：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旅行路线地图生成器
使用方法: python generate_map.py
"""

import os
import sys

# 行程数据（根据实际行程修改）
TRIP_DATA = {
    "title": "首尔4日游路线图",
    "locations": [
        # Day 1
        {"name": "仁川机场 Incheon Airport", "lat": 37.4602, "lon": 126.4407, "day": 1, "type": "交通"},
        {"name": "明洞 Myeongdong", "lat": 37.5636, "lon": 126.9869, "day": 1, "type": "景点"},
        
        # Day 2
        {"name": "景福宫 Gyeongbokgung", "lat": 37.5796, "lon": 126.9770, "day": 2, "type": "景点"},
        {"name": "北村韩屋村 Bukchon", "lat": 37.5826, "lon": 126.9850, "day": 2, "type": "景点"},
        {"name": "仁寺洞 Insadong", "lat": 37.5743, "lon": 126.9856, "day": 2, "type": "景点"},
        
        # Day 3
        {"name": "梨泰院 Itaewon", "lat": 37.5345, "lon": 126.9946, "day": 3, "type": "景点"},
        {"name": "首尔塔 N Seoul Tower", "lat": 37.5512, "lon": 126.9882, "day": 3, "type": "景点"},
        
        # Day 4
        {"name": "弘大 Hongdae", "lat": 37.5563, "lon": 126.9237, "day": 4, "type": "景点"},
        {"name": "仁川机场 Incheon Airport", "lat": 37.4602, "lon": 126.4407, "day": 4, "type": "交通"},
    ]
}


def try_folium_map(data, output_dir):
    """尝试使用 folium 生成交互式地图"""
    try:
        import folium
        
        locations = data["locations"]
        center_lat = sum(loc['lat'] for loc in locations) / len(locations)
        center_lon = sum(loc['lon'] for loc in locations) / len(locations)
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
        
        colors = {'景点': 'red', '酒店': 'blue', '餐厅': 'orange', '交通': 'gray'}
        
        for i, loc in enumerate(locations):
            color = colors.get(loc.get('type'), 'red')
            folium.Marker(
                [loc['lat'], loc['lon']],
                popup=f"<b>{loc['name']}</b><br>Day {loc.get('day', '?')}",
                tooltip=loc['name'],
                icon=folium.Icon(color=color)
            ).add_to(m)
        
        # 绘制路线
        coords = [[loc['lat'], loc['lon']] for loc in locations]
        folium.PolyLine(coords, weight=2, color='blue', opacity=0.7).add_to(m)
        
        output_path = os.path.join(output_dir, "route_map.html")
        m.save(output_path)
        print(f"✅ 交互式地图已保存: {output_path}")
        print("   用浏览器打开即可查看")
        return True
        
    except ImportError:
        print("⚠️ folium 未安装，跳过交互式地图")
        return False


def try_matplotlib_map(data, output_dir):
    """尝试使用 matplotlib 生成静态图片"""
    try:
        import matplotlib.pyplot as plt
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        locations = data["locations"]
        fig, ax = plt.subplots(figsize=(12, 10))
        
        lats = [loc['lat'] for loc in locations]
        lons = [loc['lon'] for loc in locations]
        
        ax.plot(lons, lats, 'b-', linewidth=2, alpha=0.6)
        
        colors = {'景点': 'red', '酒店': 'blue', '餐厅': 'orange', '交通': 'gray'}
        
        for i, loc in enumerate(locations):
            color = colors.get(loc.get('type'), 'red')
            ax.scatter(loc['lon'], loc['lat'], c=color, s=100, zorder=5)
            ax.annotate(f"{i+1}. {loc['name']}", (loc['lon'], loc['lat']),
                       xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        ax.set_title(data["title"], fontsize=14)
        ax.grid(True, alpha=0.3)
        
        output_path = os.path.join(output_dir, "route_map.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 静态地图已保存: {output_path}")
        return True
        
    except ImportError:
        print("⚠️ matplotlib 未安装，跳过静态地图")
        return False


def create_text_map(data, output_dir):
    """生成文字版路线图（始终可用）"""
    
    locations = data["locations"]
    lines = [
        "=" * 50,
        f"🗺️ {data['title']}",
        "=" * 50,
        ""
    ]
    
    icons = {'景点': '🏛️', '酒店': '🏨', '餐厅': '🍜', '交通': '✈️'}
    
    current_day = None
    for i, loc in enumerate(locations):
        day = loc.get('day', '?')
        
        if day != current_day:
            lines.append(f"\n📅 Day {day}")
            lines.append("-" * 30)
            current_day = day
        
        icon = icons.get(loc.get('type'), '📍')
        lines.append(f"  {icon} [{i+1}] {loc['name']}")
        lines.append(f"      坐标: ({loc['lat']:.4f}, {loc['lon']:.4f})")
        
        if i < len(locations) - 1 and locations[i+1].get('day') == day:
            lines.append("      ↓")
    
    lines.extend(["", "=" * 50])
    
    output_path = os.path.join(output_dir, "route_map.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    
    print(f"✅ 文字路线图已保存: {output_path}")
    return True


def main():
    output_dir = "旅行计划"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n🗺️ 正在生成 {TRIP_DATA['title']}...\n")
    
    # 尝试各种方式
    try_folium_map(TRIP_DATA, output_dir)
    try_matplotlib_map(TRIP_DATA, output_dir)
    create_text_map(TRIP_DATA, output_dir)
    
    print("\n✅ 地图生成完成！")


if __name__ == "__main__":
    main()
```

## 使用流程

1. **生成行程后**，提取所有地点的坐标信息
2. **创建 Python 脚本**，填入地点数据
3. **运行脚本**生成地图
4. **验证**地图文件是否生成成功

## 依赖安装

```bash
# 交互式地图
pip install folium

# 静态图片
pip install matplotlib
```

如果用户没有安装这些库，会自动降级为文字版路线图。
