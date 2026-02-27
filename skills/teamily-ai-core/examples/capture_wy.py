#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
采集内蒙古政府采购网 - 完整版
"""
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import time
from playwright.sync_api import sync_playwright

def capture_wy():
    print("="*60)
    print("内蒙古政府采购网采集")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 设置视口
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        print("\n[1] 访问网站...")
        try:
            page.goto("https://www.ccgp-neimenggu.gov.cn", timeout=30000)
        except Exception as e:
            print(f"   初始访问: {e}")
        
        # 等待页面基本加载
        print("[2] 等待基础加载...")
        page.wait_for_load_state("domcontentloaded")
        
        # 等待Vue应用挂载
        print("[3] 等待Vue应用...")
        page.wait_for_selector("#app", timeout=10000)
        
        # 等待更长时间让数据加载
        print("[4] 等待数据加载...")
        time.sleep(8)
        
        # 尝试等待网络空闲
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except:
            print("   网络未完全空闲，继续...")
        
        # 截图
        print("[5] 截图...")
        page.screenshot(path="C:/Users/haiming/wy_capture.png", full_page=True)
        
        # 获取页面内容
        content = page.content()
        
        # 尝试提取表格数据
        print("\n[6] 提取数据...")
        
        # 查找所有表格
        tables = page.locator("table").all()
        print(f"   找到 {len(tables)} 个表格")
        
        # 查找所有链接（采购公告）
        links = page.locator("a").all()
        print(f"   找到 {len(links)} 个链接")
        
        # 提取公告链接
        bid_links = []
        for link in links[:50]:  # 取前50个
            try:
                text = link.inner_text()
                href = link.get_attribute("href")
                if text and "物业" in text:
                    bid_links.append({"text": text[:50], "href": href})
            except:
                pass
        
        print(f"   找到 {len(bid_links)} 个物业相关链接")
        
        # 保存完整HTML
        with open("C:/Users/haiming/wy_full.html", "w", encoding="utf-8") as f:
            f.write(content)
        
        # 保存链接列表
        with open("C:/Users/haiming/wy_links.txt", "w", encoding="utf-8") as f:
            for item in bid_links:
                f.write(f"{item['text']} | {item['href']}\n")
        
        print(f"\n[7] 文件已保存:")
        print("   - 截图: C:/Users/haiming/wy_capture.png")
        print("   - HTML: C:/Users/haiming/wy_full.html")
        print("   - 链接: C:/Users/haiming/wy_links.txt")
        
        browser.close()
        
        print("\n" + "="*60)
        print("采集完成!")
        print("="*60)
        
        return bid_links

if __name__ == "__main__":
    capture_wy()
