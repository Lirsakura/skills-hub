#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
采集内蒙古政府采购网 - 过滤预公告版
只采集预公告，不采集成交公告
"""
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import time
from playwright.sync_api import sync_playwright

def filter_announcements(links):
    """过滤只保留预公告"""
    
    # 预公告关键词（需要保留）
    pre_keywords = [
        "采购意向",    # 采购意向
        "招标公告",    # 招标公告
        "采购公告",    # 采购公告
        "竞价采购公告", # 竞价采购
        "竞争性磋商",  # 竞争性磋商
        "竞争性谈判",  # 竞争性谈判
        "询价公告",    # 询价公告
        "更正公告",    # 更正公告
        "变更公告",    # 变更公告
        "单一来源",    # 单一来源采购
        "采购预告",    # 采购预告
    ]
    
    # 成交公告关键词（需要排除）
    exclude_keywords = [
        "中标",        # 中标结果
        "成交",        # 成交结果
        "结果公告",   # 结果公告
        "合同公告",    # 合同公告
        "履约",        # 履约验收
        "验收",        # 验收公告
    ]
    
    filtered = []
    
    for link in links:
        text = link.get("text", "")
        
        # 排除成交公告
        if any(k in text for k in exclude_keywords):
            continue
        
        # 必须包含预公告关键词
        if any(k in text for k in pre_keywords):
            filtered.append(link)
    
    return filtered


def capture_wy_filtered():
    print("="*60)
    print("内蒙古政府采购网 - 预公告采集（过滤成交）")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        print("\n[1] 访问搜索页面...")
        url = "https://www.ccgp-neimenggu.gov.cn/maincms-web/fullSearchingNm?searchKey=物业"
        page.goto(url, timeout=30000)
        
        print("[2] 等待页面加载...")
        page.wait_for_load_state("domcontentloaded")
        
        try:
            page.wait_for_selector("#app", timeout=10000)
        except:
            pass
        
        # 等待数据加载
        time.sleep(10)
        
        # 截图
        page.screenshot(path="C:/Users/haiming/wy_filtered.png", full_page=True)
        
        # 提取链接
        all_links = page.locator("a").all()
        
        keywords = ["招标", "采购", "公告", "物业", "项目", "意向", "竞价"]
        
        bid_links = []
        for link in all_links:
            try:
                text = link.inner_text().strip()
                href = link.get_attribute("href") or ""
                
                if any(k in text for k in keywords) and len(text) > 2:
                    bid_links.append({
                        "text": text[:100], 
                        "href": href
                    })
            except:
                pass
        
        # 过滤
        print("\n[3] 过滤预公告...")
        pre_announcements = filter_announcements(bid_links)
        
        # 去重
        seen = set()
        unique = []
        for item in pre_announcements:
            if item["text"] not in seen:
                seen.add(item["text"])
                unique.append(item)
        
        print(f"   过滤后: {len(unique)} 条预公告")
        
        # 保存
        with open("C:/Users/haiming/wy_pre_bids.txt", "w", encoding="utf-8") as f:
            f.write(f"# 物业采购预公告（仅预公告）\n")
            f.write(f"# 采集时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 数据来源: 内蒙古自治区政府采购网\n\n")
            
            for i, item in enumerate(unique, 1):
                f.write(f"{i}. {item['text']}\n")
                f.write(f"   链接: {item['href']}\n\n")
        
        print(f"\n[4] 预公告列表:")
        for i, item in enumerate(unique[:15], 1):
            print(f"   {i}. {item['text'][:50]}")
        
        print(f"\n[5] 已保存到: C:/Users/haiming/wy_pre_bids.txt")
        
        browser.close()
        
        print("\n" + "="*60)
        print("完成!")
        print("="*60)
        
        return unique

if __name__ == "__main__":
    capture_wy_filtered()
