"""
Web scraper service for web page crawling and content extraction.
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
from typing import Dict, List, Optional
from utils.logging_config import app_logger


class WebScraperService:
    """Service for web scraping operations."""
    
    def __init__(self):
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def crawl_web_page(self, url: str, max_content_length: int = 10000) -> Dict:
        """
        Crawl web page content and extract useful information.
        
        Args:
            url (str): URL of the web page to crawl
            max_content_length (int): Maximum content length limit
            
        Returns:
            Dict: Dictionary containing crawled data
        """
        try:
            app_logger.info(f"Starting web crawl for URL: {url}")
            
            # Normalize URL
            normalized_url = self._normalize_url(url)
            if not normalized_url:
                raise ValueError(f"Invalid URL: {url}")
            
            # Send HTTP request
            response = requests.get(normalized_url, headers=self.default_headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information
            title = self._extract_title(soup)
            description = self._extract_description(soup)
            content = self._extract_main_content(soup, max_content_length)
            links = self._extract_links(soup, url)
            images = self._extract_images(soup, url)
            metadata = self._extract_metadata(soup)
            
            # Calculate content statistics
            word_count = len(content.split()) if content else 0
            char_count = len(content) if content else 0
            
            result = {
                'url': normalized_url,
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
                'url': normalized_url if 'normalized_url' in locals() else url,
                'status': 'error',
                'error': f'Request failed: {str(e)}',
                'crawl_time': time.time()
            }
        except Exception as e:
            app_logger.error(f"Unexpected error while crawling {url}: {str(e)}")
            return {
                'url': normalized_url if 'normalized_url' in locals() else url,
                'status': 'error',
                'error': f'Unexpected error: {str(e)}',
                'crawl_time': time.time()
            }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract web page title."""
        # Try multiple ways to get title
        title = None
        
        # 1. Get from title tag
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        
        # 2. Get from h1 tag
        if not title:
            h1 = soup.find('h1')
            if h1 and h1.get_text():
                title = h1.get_text().strip()
        
        # 3. Get from meta title
        if not title:
            meta_title = soup.find('meta', {'property': 'og:title'})
            if meta_title and meta_title.get('content'):
                title = meta_title.get('content').strip()
        
        return title or "No title found"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract web page description."""
        description = None
        
        # 1. Get from meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc.get('content').strip()
        
        # 2. Get from og:description
        if not description:
            og_desc = soup.find('meta', {'property': 'og:description'})
            if og_desc and og_desc.get('content'):
                description = og_desc.get('content').strip()
        
        # 3. Get from first p tag
        if not description:
            first_p = soup.find('p')
            if first_p and first_p.get_text():
                description = first_p.get_text().strip()[:200]  # Limit length
        
        return description or "No description found"

    def _extract_main_content(self, soup: BeautifulSoup, max_length: int) -> str:
        """Extract main content."""
        # Remove unwanted tags
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            tag.decompose()
        
        # Try to find main content area
        main_content = None
        
        # 1. Look for main tag
        main_tag = soup.find('main')
        if main_tag:
            main_content = main_tag.get_text()
        
        # 2. Look for article tag
        if not main_content:
            article_tag = soup.find('article')
            if article_tag:
                main_content = article_tag.get_text()
        
        # 3. Look for div with content class
        if not main_content:
            content_div = soup.find('div', class_=re.compile(r'content|main|body', re.I))
            if content_div:
                main_content = content_div.get_text()
        
        # 4. If nothing found, use body tag
        if not main_content:
            body = soup.find('body')
            if body:
                main_content = body.get_text()
        
        # Clean text content
        if main_content:
            # Remove extra whitespace
            main_content = re.sub(r'\s+', ' ', main_content).strip()
            # Limit length
            if len(main_content) > max_length:
                main_content = main_content[:max_length] + "..."
        
        return main_content or "No content found"

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract page links."""
        links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            
            # Convert to absolute URL
            absolute_url = urljoin(base_url, href)
            
            # Only keep same domain links
            if urlparse(absolute_url).netloc == base_domain:
                links.append({
                    'url': absolute_url,
                    'text': text,
                    'title': link.get('title', '')
                })
        
        return links[:20]  # Limit number of links

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract page images."""
        images = []
        
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '')
            title = img.get('title', '')
            
            # Convert to absolute URL
            absolute_url = urljoin(base_url, src)
            
            images.append({
                'url': absolute_url,
                'alt': alt,
                'title': title
            })
        
        return images[:10]  # Limit number of images

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract page metadata."""
        metadata = {}
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            
            if name and content:
                metadata[name] = content
        
        # Extract language information
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['language'] = html_tag.get('lang')
        
        return metadata

    def crawl_multiple_pages(self, urls: List[str], max_content_length: int = 10000) -> List[Dict]:
        """
        Batch crawl multiple web pages.
        
        Args:
            urls (List[str]): List of URLs to crawl
            max_content_length (int): Maximum content length limit
            
        Returns:
            List[Dict]: List containing all crawl results
        """
        results = []
        
        for url in urls:
            result = self.crawl_web_page(url, max_content_length)
            results.append(result)
            
            # Add delay to avoid too frequent requests
            time.sleep(1)
        
        return results

    def _normalize_url(self, url: str) -> str:
        """Normalize URL to ensure it has a scheme."""
        if not url:
            return None
        
        url = url.strip()
        
        # If URL already has a scheme, return as is
        if url.startswith(('http://', 'https://')):
            return url
        
        # If URL starts with //, add https://
        if url.startswith('//'):
            return f"https:{url}"
        
        # If URL doesn't have a scheme, add https://
        if not url.startswith(('http://', 'https://', 'ftp://', 'file://')):
            return f"https://{url}"
        
        return url

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def get_domain(self, url: str) -> str:
        """Get domain from URL."""
        try:
            return urlparse(url).netloc
        except Exception:
            return ""

    def clean_url(self, url: str) -> str:
        """Clean and normalize URL."""
        try:
            result = urlparse(url)
            # Remove fragment and query parameters for normalization
            return f"{result.scheme}://{result.netloc}{result.path}"
        except Exception:
            return url


# Global service instance
web_scraper_service = WebScraperService()
