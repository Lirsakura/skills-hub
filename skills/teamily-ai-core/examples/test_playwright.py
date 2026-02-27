#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
测试 Playwright 采集内蒙古政府采购网
"""
import time
from playwright.sync_api import sync_playwright

def test_capture():
    print("="*60)
    print("Playwright采集测试")
    print("="*60)
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("\n[1] 访问内蒙古政府采购网...")
        
        # 设置下载处理
        page.on("download", lambda download: print(f"   触发下载: {download.url}"))
        
        try:
            page.goto("https://www.ccgp-neimenggu.gov.cn/maincms-web/fullSearchingNm?searchKey=物业", 
                     timeout=30000, wait_until="networkidle")
        except Exception as e:
            print(f"   访问出错，尝试其他方式: {e}")
            # 尝试直接访问首页
            page.goto("https://www.ccgp-neimenggu.gov.cn", timeout=30000)
        
        # 等待页面加载
        print("[2] 等待页面加载...")
        time.sleep(5)  # 等待JS执行
        
        # 获取页面标题
        title = page.title()
        print(f"\n[3] 页面标题: {title}")
        
        # 截图
        page.screenshot(path="C:/Users/haiming/wy_page.png", full_page=True)
        print("[4] 截图保存到: C:/Users/haiming/wy_page.png")
        
        # 尝试提取内容
        print("\n[5] 提取内容...")
        
        # 尝试查找表格
        try:
            table = page.locator("table").first
            if table.count() > 0:
                print(f"   找到表格")
                rows = table.locator("tr").all()
                print(f"   行数: {len(rows)}")
        except Exception as e:
            print(f"   未找到表格: {e}")
        
        # 获取页面文本
        content = page.content()
        print(f"\n[6] 页面HTML长度: {len(content)} 字符")
        
        # 保存HTML
        with open("C:/Users/haiming/wy_page.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("[7] HTML保存到: C:/Users/haiming/wy_page.html")
        
        browser.close()
        
        print("\n" + "="*60)
        print("采集完成!")
        print("="*60)

if __name__ == "__main__":
    test_capture()
