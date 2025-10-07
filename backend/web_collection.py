import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
from typing import Dict, List, Optional
from utils.logging_config import app_logger


def crawl_web_page(url: str, max_content_length: int = 10000) -> Dict:
    """
    爬取网页内容并提取有用信息
    
    Args:
        url (str): 要爬取的网页URL
        max_content_length (int): 最大内容长度限制
        
    Returns:
        Dict: 包含爬取数据的字典
    """
    try:
        app_logger.info(f"Starting web crawl for URL: {url}")
        
        # 设置请求头，模拟真实浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 发送HTTP请求
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 解析HTML内容
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 提取基本信息
        title = extract_title(soup)
        description = extract_description(soup)
        content = extract_main_content(soup, max_content_length)
        links = extract_links(soup, url)
        images = extract_images(soup, url)
        metadata = extract_metadata(soup)
        
        # 计算内容统计
        word_count = len(content.split()) if content else 0
        char_count = len(content) if content else 0
        
        result = {
            'url': url,
            'title': title,
            'description': description,
            'content': content,
            'word_count': word_count,
            'char_count': char_count,
            'links': links,
            'images': images,
            'metadata': metadata,
            'crawl_time': time.time(),
            'status': 'success'
        }
        
        app_logger.info(f"Successfully crawled {url}: {word_count} words, {char_count} characters")
        return result
        
    except requests.exceptions.RequestException as e:
        app_logger.error(f"Request error while crawling {url}: {str(e)}")
        return {
            'url': url,
            'status': 'error',
            'error': f'Request failed: {str(e)}',
            'crawl_time': time.time()
        }
    except Exception as e:
        app_logger.error(f"Unexpected error while crawling {url}: {str(e)}")
        return {
            'url': url,
            'status': 'error',
            'error': f'Unexpected error: {str(e)}',
            'crawl_time': time.time()
        }


def extract_title(soup: BeautifulSoup) -> str:
    """提取网页标题"""
    # 尝试多种方式获取标题
    title = None
    
    # 1. 从title标签获取
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    
    # 2. 从h1标签获取
    if not title:
        h1 = soup.find('h1')
        if h1 and h1.get_text():
            title = h1.get_text().strip()
    
    # 3. 从meta title获取
    if not title:
        meta_title = soup.find('meta', {'property': 'og:title'})
        if meta_title and meta_title.get('content'):
            title = meta_title.get('content').strip()
    
    return title or "No title found"


def extract_description(soup: BeautifulSoup) -> str:
    """提取网页描述"""
    description = None
    
    # 1. 从meta description获取
    meta_desc = soup.find('meta', {'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        description = meta_desc.get('content').strip()
    
    # 2. 从og:description获取
    if not description:
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            description = og_desc.get('content').strip()
    
    # 3. 从第一个p标签获取
    if not description:
        first_p = soup.find('p')
        if first_p and first_p.get_text():
            description = first_p.get_text().strip()[:200]  # 限制长度
    
    return description or "No description found"


def extract_main_content(soup: BeautifulSoup, max_length: int) -> str:
    """提取主要内容"""
    # 移除不需要的标签
    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
        tag.decompose()
    
    # 尝试找到主要内容区域
    main_content = None
    
    # 1. 查找main标签
    main_tag = soup.find('main')
    if main_tag:
        main_content = main_tag.get_text()
    
    # 2. 查找article标签
    if not main_content:
        article_tag = soup.find('article')
        if article_tag:
            main_content = article_tag.get_text()
    
    # 3. 查找class包含content的div
    if not main_content:
        content_div = soup.find('div', class_=re.compile(r'content|main|body', re.I))
        if content_div:
            main_content = content_div.get_text()
    
    # 4. 如果都没找到，使用body标签
    if not main_content:
        body = soup.find('body')
        if body:
            main_content = body.get_text()
    
    # 清理文本内容
    if main_content:
        # 移除多余的空白字符
        main_content = re.sub(r'\s+', ' ', main_content).strip()
        # 限制长度
        if len(main_content) > max_length:
            main_content = main_content[:max_length] + "..."
    
    return main_content or "No content found"


def extract_links(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    """提取页面链接"""
    links = []
    base_domain = urlparse(base_url).netloc
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        text = link.get_text().strip()
        
        # 转换为绝对URL
        absolute_url = urljoin(base_url, href)
        
        # 只保留同域名的链接
        if urlparse(absolute_url).netloc == base_domain:
            links.append({
                'url': absolute_url,
                'text': text,
                'title': link.get('title', '')
            })
    
    return links[:20]  # 限制链接数量


def extract_images(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    """提取页面图片"""
    images = []
    
    for img in soup.find_all('img', src=True):
        src = img['src']
        alt = img.get('alt', '')
        title = img.get('title', '')
        
        # 转换为绝对URL
        absolute_url = urljoin(base_url, src)
        
        images.append({
            'url': absolute_url,
            'alt': alt,
            'title': title
        })
    
    return images[:10]  # 限制图片数量


def extract_metadata(soup: BeautifulSoup) -> Dict:
    """提取页面元数据"""
    metadata = {}
    
    # 提取meta标签
    for meta in soup.find_all('meta'):
        name = meta.get('name') or meta.get('property')
        content = meta.get('content')
        
        if name and content:
            metadata[name] = content
    
    # 提取语言信息
    html_tag = soup.find('html')
    if html_tag and html_tag.get('lang'):
        metadata['language'] = html_tag.get('lang')
    
    return metadata


def crawl_multiple_pages(urls: List[str], max_content_length: int = 10000) -> List[Dict]:
    """
    批量爬取多个网页
    
    Args:
        urls (List[str]): 要爬取的URL列表
        max_content_length (int): 最大内容长度限制
        
    Returns:
        List[Dict]: 包含所有爬取结果的列表
    """
    results = []
    
    for url in urls:
        result = crawl_web_page(url, max_content_length)
        results.append(result)
        
        # 添加延迟避免请求过于频繁
        time.sleep(1)
    
    return results


# 示例使用
if __name__ == "__main__":
    # 测试单个网页爬取
    test_url = "https://news.qq.com/"
    result = crawl_web_page(test_url)
    print(f"Crawl result: {result}")