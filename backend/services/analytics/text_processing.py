"""
Text processing utilities for analytics and clustering.
"""
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from collections import Counter
from utils.logging_config import app_logger


class TextProcessingService:
    """Service for text processing operations."""
    
    def __init__(self):
        self.custom_stop_words = self._get_custom_stop_words()
    
    def _get_custom_stop_words(self) -> List[str]:
        """Get custom stop words for text processing."""
        return [
            # Chinese stop words
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '作者', '笔者', '日电', '她说', '另有', '今年', '去年', '明年', '早些',
            # English stop words
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'am',
            # Technical terms
            'http', 'https', 'www', 'com', 'cn', 'org', 'net', 'href', 'target', 'blank', 'src', 'img', 'figure', 'figcaption', 'div', 'class', 'style', 'id', 'title', 'alt', 'author',
            # Common words
            'as', 'it', 'than', 'said', 'say', 'new', 'old', 'up', 'more', 'he', 'she', 'him', 'her', 'me', 'my', 'mine'
        ]
    
    def clean_text(self, raw: str) -> str:
        """
        Clean HTML/Markdown text to plain text.
        
        Args:
            raw: Raw text content
            
        Returns:
            Cleaned text
        """
        if not isinstance(raw, str):
            raw = str(raw or "")
        
        text = raw
        
        # Remove HTML tags
        try:
            text = BeautifulSoup(text, 'html.parser').get_text(separator=' ')
        except Exception:
            pass
        
        # Remove Markdown images ![alt](url)
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
        
        # Convert Markdown links [text](url) to just text
        text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
        
        # Remove code blocks and inline code
        text = re.sub(r"```[\s\S]*?```", " ", text)
        text = re.sub(r"`([^`]*)`", r"\1", text)
        
        # Remove headers, lists, quotes
        text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s{0,3}[-*+]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s{0,3}>\s+", "", text, flags=re.MULTILINE)
        
        # Remove bold/italic markers
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)
        
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        
        return text
    
    def preprocess_text(self, text: str, tags: str = None) -> str:
        """
        Preprocess text for clustering analysis.
        
        Args:
            text: Text content
            tags: Tags string
            
        Returns:
            Preprocessed text
        """
        # Clean the text
        text = self.clean_text(text)
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove special characters, keep Chinese and English
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z\s]', ' ', text)
        
        # Remove banned tokens
        banned_tokens = [
            'dir', 'ltr', 'rtl', 'align', 'center', 'left', 'right', 'nbsp', 'nbspnbsp',
            'figcaption', 'caption', 'blockquote', 'figure', 'video', 'pagevideo', 'poster', 'style'
        ]
        
        # Remove single banned tokens
        pattern_single = r'\b(' + '|'.join(banned_tokens) + r')\b'
        text = re.sub(pattern_single, ' ', text, flags=re.IGNORECASE)
        
        # Remove bigrams with banned tokens
        pattern_bigram = r'\b(?:\w+\s+)?(' + '|'.join(banned_tokens) + r')(?:\s+\w+)?\b'
        text = re.sub(pattern_bigram, ' ', text, flags=re.IGNORECASE)
        
        # Process tags
        if tags and isinstance(tags, str):
            tag_words = [tag.strip() for tag in tags.split(',') if tag.strip()]
            if tag_words:
                text = text + ' ' + ' '.join(tag_words * 3)  # Weight tags higher
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def is_meaningful_word(self, word: str) -> bool:
        """
        Check if a word is meaningful for clustering.
        
        Args:
            word: Word to check
            
        Returns:
            True if word is meaningful
        """
        if len(word) < 2:
            return False
        
        # Single character words (except meaningful ones)
        if len(word) == 1 and word not in ['水', '火', '土', '金', '木', '车', '路', '桥', '药', '病', '法', '税', '政', '军', '国']:
            return False
        
        # Banned substrings
        banned_substrings = [
            'dir', 'ltr', 'rtl', 'align', 'center', 'left', 'right', 'nbsp',
            'figcaption', 'caption', 'blockquote', 'figure', 'video', 'pagevideo', 'poster', 'style'
        ]
        if any(sub in word.lower() for sub in banned_substrings):
            return False
        
        # Too long words
        if len(word) > 15:
            return False
        
        # Meaningless suffixes
        meaningless_suffixes = ['的', '了', '着', '过', '们', '中', '内', '外', '上', '下', '左', '右', '前', '后', '里', '间', '侧', '边', '面', '头', '尾', '部', '分']
        if word.endswith(tuple(meaningless_suffixes)):
            return False
        
        # Meaningless prefixes
        meaningless_prefixes = ['非', '无', '不', '没', '未', '别', '莫', '勿']
        if word.startswith(tuple(meaningless_prefixes)) and len(word) <= 3:
            return False
        
        # Pure numbers
        if word.isdigit() or (len(word) > 1 and word[0].isdigit()):
            return False
        
        # Repeated characters
        if len(set(word)) == 1 and len(word) > 2:
            return False
        
        # HTML/XML terms
        html_terms = ['href', 'src', 'img', 'div', 'class', 'style', 'id', 'title', 'alt', 'http', 'https', 'www', 'com', 'cn', 'org', 'net', 'target', 'blank', '_blank']
        if word in html_terms:
            return False
        
        return True
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of keywords
        """
        # Clean and preprocess text
        clean_text = self.preprocess_text(text)
        
        # Extract words
        words = re.findall(r'\b\w+\b', clean_text.lower())
        
        # Count word frequency
        word_freq = Counter(words)
        
        # Filter meaningful words
        meaningful_words = [
            (word, freq) for word, freq in word_freq.most_common()
            if word not in self.custom_stop_words and self.is_meaningful_word(word)
        ]
        
        # Return top keywords
        return [word for word, freq in meaningful_words[:max_keywords]]
    
    def generate_cluster_label(self, keywords: List[str]) -> str:
        """
        Generate a descriptive label for a cluster based on keywords.
        
        Args:
            keywords: List of keywords
            
        Returns:
            Cluster label
        """
        if not keywords:
            return "未分类"
        
        # Topic keyword mapping
        topic_keywords = {
            "政治": ["政府", "国家", "总统", "领导人", "选举", "政策", "议会", "党派", "政治", "外交"],
            "经济": ["经济", "金融", "市场", "股票", "投资", "贸易", "货币", "银行", "财政", "GDP"],
            "科技": ["科技", "技术", "人工智能", "数据", "互联网", "软件", "计算机", "数字", "创新", "研发"],
            "军事": ["军事", "军队", "国防", "武器", "战争", "冲突", "安全", "演习", "基地", "武装"],
            "社会": ["社会", "文化", "教育", "健康", "医疗", "环境", "气候", "人口", "社区", "民生"],
            "体育": ["体育", "足球", "篮球", "比赛", "运动员", "奥运", "世界杯", "冠军", "联赛", "教练"],
            "娱乐": ["娱乐", "电影", "音乐", "明星", "演员", "歌手", "节目", "表演", "艺术", "媒体"],
            "国际": ["国际", "联合国", "全球", "世界", "外交", "合作", "峰会", "协议", "组织", "多边"],
            "灾难": ["灾难", "地震", "洪水", "火灾", "事故", "救援", "伤亡", "损失", "紧急", "危险"],
            "犯罪": ["犯罪", "案件", "警察", "调查", "逮捕", "审判", "法律", "法院", "嫌疑", "证据"]
        }
        
        # Calculate topic scores
        topic_scores = {}
        for topic, topic_kw in topic_keywords.items():
            score = sum(1 for kw in keywords if kw in topic_kw)
            if score > 0:
                topic_scores[topic] = score
        
        # Return best matching topic or first keyword
        if topic_scores:
            best_topic = max(topic_scores, key=topic_scores.get)
            if topic_scores[best_topic] >= 2:
                return f"{best_topic}相关"
            else:
                matched_keyword = next((kw for kw in keywords if kw in topic_keywords[best_topic]), None)
                if matched_keyword:
                    return f"{best_topic}({matched_keyword})"
                else:
                    return f"{best_topic}相关"
        else:
            return f"{keywords[0]}相关" if keywords else "未分类"


# Global service instance
text_processing_service = TextProcessingService()
