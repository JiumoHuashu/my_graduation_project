import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os
import sys
import io

# 强制标准输出使用 utf-8 编码，防止在 Windows 环境下输出 GBK 导致乱码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- 配置区域 ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://b.faloo.com/',
}

AD_KEYWORDS = ['充值', '点券', '赠送', '活动时间', '立即抢充', '清明读书', 'VIP', '赠500', '抢充', '点券']

SAVE_DIR = "book"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def get_book_ids_from_list(list_url):
    """精准提取：第5本到第34本"""
    try:
        print(f"\n[列表页] 正在扫描: {list_url}")
        sys.stdout.flush()
        res = requests.get(list_url, headers=HEADERS, timeout=10)
        res.encoding = 'gbk'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        main_list = soup.find('div', class_='ff_list_three') or soup.find('div', class_='ListMain01')
        search_area = main_list if main_list else soup
        
        all_links = search_area.find_all('a', href=re.compile(r'//b\.faloo\.com/\d+\.html'))
        
        raw_ids = []
        for a in all_links:
            if a.get('title') or a.get_text(strip=True):
                href = a.get('href', '')
                match = re.search(r'/(\d+)\.html', href)
                if match:
                    bid = match.group(1)
                    if bid not in raw_ids:
                        raw_ids.append(bid)
        
        target_ids = raw_ids[4:34]
        print(f"--- 页面总识别 {len(raw_ids)} 本，已截取第5-34位共 {len(target_ids)} 本 ---")
        sys.stdout.flush()
        return target_ids
    except Exception as e:
        print(f"[错误] 列表页解析异常: {e}")
        sys.stdout.flush()
        return []

def get_chapter_content(url):
    """抓取单章内容"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200: return None, "请求失败"
        response.encoding = 'gbk'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "未知章节"
        content_div = soup.find('div', class_='noveContent') or soup.find('div', id='content')
        
        if content_div:
            paragraphs = content_div.find_all('p')
            clean_lines = [p.get_text(strip=True) for p in paragraphs if not any(word in p.text for word in AD_KEYWORDS)]
            return title, "\n".join(clean_lines)
        return title, "内容提取失败"
    except Exception as e:
        return None, str(e)

def scrape_book_to_json(book_id):
    """全字段动态抓取：修复统计数据与入站时间固定问题"""
    main_url = f"https://b.faloo.com/{book_id}.html"
    try:
        res = requests.get(main_url, headers=HEADERS, timeout=10)
        res.encoding = 'gbk'
        soup = BeautifulSoup(res.text, 'html.parser')
        full_text = soup.get_text()

        # 1. 基础元数据解析
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else f"ID_{book_id}"
        author_tag = soup.find('a', class_=lambda x: x and 'fs14' in x and 'colorQianHui' in x)
        author = author_tag.get_text(strip=True) if author_tag else "未知作者"

        # 2. 封面与标签
        cover_url = "未找到封面链接"
        img_tag = soup.find('img', class_='imgcss')
        if img_tag:
            cover_url = img_tag.get('src', '')
            if cover_url.startswith('//'): cover_url = 'http:' + cover_url
        tags_list = soup.find_all('a', class_='LXbq')
        tags_str = " / ".join([t.get_text(strip=True) for t in tags_list]) if tags_list else "无标签"

        # 3. 分类提取
        main_category, sub_category = "未知分类", "未知子类"
        m_span = soup.find(lambda t: t.name == "span" and "小说分类" in t.text)
        if m_span and m_span.find('a'): main_category = m_span.find('a').get_text(strip=True)
        s_span = soup.find(lambda t: t.name == "span" and "小说子类" in t.text)
        if s_span and s_span.find('a'): sub_category = s_span.find('a').get_text(strip=True)

        # 查找包含所有元数据的容器（包括入站时间、字数等）
        def get_meta_value(keyword):
            """通用提取器：查找包含keyword的标签，并返回其内部数值标签的内容"""
            # 这里的 target 可能是 span, div 等
            target = soup.find(lambda tag: tag.name == "span" and keyword in tag.text)
            if target:
                # 尝试寻找内部包裹数值的 span (如 class colorHui 或 colorHei)
                val_tag = target.find('span')
                return val_tag.get_text(strip=True) if val_tag else "0"
            return "未知"

        # 动态获取
        onboarding_time = get_meta_value('入站时间')
        m_read = get_meta_value('月阅读数')
        m_flower = get_meta_value('月鲜花数')
        t_read = get_meta_value('总阅读数')
        t_flower = get_meta_value('总鲜花数')
        
        # 更新时间与字数（使用正则作为双重保险）
        u_match = re.search(r'更新时间：(\d{4}-\d{2}-\d{2}\s\d+时)', full_text)
        update_time = u_match.group(1) if u_match else "未知时间"
        w_match = re.search(r'已写(\d+)个字', full_text)
        word_count = w_match.group(1) if w_match else "0"
        
        # 简介
        intro_box = soup.find('div', class_='T-L-T-C-Box1')
        intro = "\n".join([p.get_text(strip=True) for p in intro_box.find_all('p') if '提醒您' not in p.text]) if intro_box else "简介提取失败"

        # 5. 章节正文 (前3章)
        chapters = []
        for i in range(1, 4):
            c_url = f"https://b.faloo.com/{book_id}_{i}.html"
            c_title, c_content = get_chapter_content(c_url)
            if c_title:
                chapters.append({"chapter_num": i, "chapter_title": c_title, "chapter_content": c_content})
            time.sleep(0.4)

        # 6. 构造最终 JSON
        book_data = {
            "book_id": book_id,
            "title": title,
            "author": author,
            "cover_url": cover_url,
            "onboarding_time": onboarding_time,
            "update_time": update_time,
            "category": {
                "main_category": main_category,
                "sub_category": sub_category
            },
            "read_count": t_read,
            "word_count": word_count,
            "monthly_stats": {
                "monthly_read": m_read,
                "monthly_flowers": m_flower
            },
            "total_stats": {
                "total_read": t_read,
                "total_flowers": t_flower
            },
            "tags": tags_str,
            "introduction": intro,
            "chapters": chapters
        }

        # 保存文件
        file_path = os.path.join(SAVE_DIR, f"{book_id}.json")
        with open(file_path, "w", encoding="utf-8") as jf:
            json.dump(book_data, jf, ensure_ascii=False, indent=4)

        print(f"   >> [完成] 《{title}》 | 入站:{onboarding_time} | 总读:{t_read}")
        sys.stdout.flush()
        return True
    except Exception as e:
        print(f"      [报错] 书籍 {book_id} 处理异常: {e}")
        sys.stdout.flush()
        return False

if __name__ == "__main__":
    # 默认值
    start_page = 81
    end_page = 101
    
    # 从命令行参数获取
    if len(sys.argv) > 1:
        try:
            start_page = int(sys.argv[1])
        except ValueError:
            print("起始页码必须是数字，使用默认值 81")
            sys.stdout.flush()
    
    if len(sys.argv) > 2:
        try:
            end_page = int(sys.argv[2])
        except ValueError:
            print("结束页码必须是数字，使用默认值 101")
            sys.stdout.flush()
    
    print(f"开始爬取页码范围: {start_page} - {end_page}")
    sys.stdout.flush()
    
    for page in range(start_page, end_page + 1):
        list_url = f"https://b.faloo.com/y_0_0_0_0_3_5_{page}.html"
        book_ids = get_book_ids_from_list(list_url)
        for index, bid in enumerate(book_ids):
            print(f"[{page}页-第{index+5}位] 处理 ID: {bid}")
            sys.stdout.flush()
            scrape_book_to_json(bid)
            time.sleep(1.2)
    print("\n--- 任务全部完成 ---")
    sys.stdout.flush()