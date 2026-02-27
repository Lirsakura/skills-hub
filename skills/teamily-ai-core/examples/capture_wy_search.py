#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
采集内蒙古政府采购网 - 搜索版
"""
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import time
from playwright.sync_api import sync_playwright

def search_and_capture():
    print("="*60)
    print("内蒙古政府采购网 - 关键词搜索采集")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        print("\n[1] 访问搜索页面...")
        # 直接访问搜索URL
        url = "https://www.ccgp-neimenggu.gov.cn/maincms-web/fullSearchingNm?searchKey=物业"
        page.goto(url, timeout=30000)
        
        print("[2] 等待页面...")
        page.wait_for_load_state("domcontentloaded")
        
        # 等待Vue应用
        try:
            page.wait_for_selector("#app", timeout=10000)
        except:
            print("   未找到#app")
        
        # 等待数据加载
        time.sleep(10)
        
        # 尝试等待表格出现
        print("[3] 等待搜索结果...")
        try:
            page.wait_for_selector("table", timeout=15000)
            print("   表格出现")
        except:
            print("   未找到表格，尝试其他方式...")
        
        # 尝试查找搜索结果容器
        selectors_to_try = [
            ".el-table",
            ".search-result",
            ".result-list", 
            ".news-list",
            "[class*='table']",
            "[class*='list']"
        ]
        
        results = []
        for sel in selectors_to_try:
            try:
                elements = page.locator(sel).all()
                if elements:
                    print(f"   找到 {sel}: {len(elements)} 个元素")
                    results.extend(elements)
            except:
                pass
        
        # 获取页面内容
        content = page.content()
        
        # 截图
        print("[4] 截图...")
        page.screenshot(path="C:/Users/haiming/wy_search.png", full_page=True)
        
        # 保存完整HTML
        with open("C:/Users/haiming/wy_search.html", "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"\n[5] 提取公告链接...")
        
        # 查找所有可能包含公告的链接
        all_links = page.locator("a").all()
        print(f"   总链接数: {len(all_links)}")
        
        # 提取链接
        bid_links = []
        keywords = ["招标", "采购", "公告", "物业", "项目", "中标", "预公告"]
        
        for link in all_links:
            try:
                text = link.inner_text().strip()
                href = link.get_attribute("href") or ""
                
                # 检查是否包含关键词
                if any(k in text for k in keywords) and len(text) > 2:
                    bid_links.append({
                        "text": text[:100], 
                        "href": href[:200]
                    })
            except:
                pass
        
        # 去重
        seen = set()
        unique_links = []
        for item in bid_links:
            if item["text"] not in seen:
                seen.add(item["text"])
                unique_links.append(item)
        
        print(f"   找到 {len(unique_links)} 条相关链接")
        
        # 保存链接
        with open("C:/Users/haiming/wy_bids.txt", "w", encoding="utf-8") as f:
            f.write(f"# 物业采购公告 - 采集时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for i, item in enumerate(unique_links[:30], 1):
                f.write(f"{i}. {item['text']}\n")
                f.write(f"   URL: {item['href']}\n\n")
        
        # 打印前10条
        print("\n[6] 公告列表(前10条):")
        for i, item in enumerate(unique_links[:10], 1):
            print(f"   {i}. {item['text'][:60]}")
        
        print(f"\n[7] 文件已保存:")
        print("   - 截图: C:/Users/haiming/wy_search.png")
        print("   - HTML: C:/Users/haiming/wy_search.html")
        print("   - 公告: C:/Users/haiming/wy_bids.txt")
        
        browser.close()
        
        print("\n" + "="*60)
        print("完成!")
        print("="*60)
        
        return unique_links

if __name__ == "__main__":
    search_and_capture()
