from models.rss_source import RssSource
from sqlmodel import Session, select
from utils.logging_config import app_logger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.rss_source import RssSource
from models.document import Document
import feedparser
import time
import datetime
import threading
from tools import create_knowledge_base_tool
import re
from bs4 import BeautifulSoup
from utils.email_sender import send_notification_email

def clean_text(raw: str) -> str:
    """
    将HTML/Markdown清洗为纯文本：
    - 去除所有HTML标签
    - 处理常见Markdown（图片、链接、代码、标题、列表、加粗/斜体、引用）
    - 合并多余空白
    """
    if not isinstance(raw, str):
        raw = str(raw or "")

    text = raw
    # 先用BeautifulSoup去除HTML标签
    try:
        text = BeautifulSoup(text, 'html.parser').get_text(separator=' ')
    except Exception:
        pass

    # 去除Markdown图片 ![alt](url)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    # 将Markdown链接 [text](url) 保留text
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    # 去除行内代码和代码块
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    # 去除标题/列表/引用等标记
    text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s{0,3}[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s{0,3}>\s+", "", text, flags=re.MULTILINE)
    # 去除加粗/斜体标记
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    # 合并空白
    text = re.sub(r"\s+", " ", text).strip()
    return text

def store_documents_in_knowledge_base(document_list):
    """
    将文档存储到知识库中的函数，用于在线程中执行
    """
    tool = create_knowledge_base_tool()
    try:
        # 执行写入操作
        result = tool.run({"action": "store", "documents": document_list})
        # 记录结果
        app_logger.info(f"Knowledge Base Tool Result: {result}")
    except Exception as e:
        app_logger.error(f"Failed to process documents for knowledge base: {str(e)}")
        # 即使知识库存储失败，也继续执行其他任务
        pass

# 定义一个函数，用于从RSS源中获取数据
def fetch_rss_feeds(id:int, session:Session) -> bool:
    rss_source = session.exec(select(RssSource).where(RssSource.id == id)).first()
    document_list = []
    if rss_source:
        # 解析RSS源
        app_logger.info(f"Fetching RSS feeds from {rss_source.url}")    
        rss_feed = feedparser.parse(rss_source.url)
        app_logger.info(f"完整信息: {rss_feed}")
        if rss_feed.entries:
            app_logger.info(f"Successfully fetched {len(rss_feed.entries)} entries from {rss_source.url}")
            # 处理每个条目
            for entry in rss_feed.entries:
                app_logger.info(f"Entry Title: {entry.title}")
                app_logger.info(f"Entry Link: {entry.link}")
                app_logger.info(f"Entry Description: {entry.description}")
                app_logger.info("="*40)  # 分隔线
                # 检查数据库中是否已存在相同的链接
                existing_doc = session.exec(select(Document).where(Document.link == entry.link)).first()
                if not existing_doc:
                    # 清洗标题与描述
                    raw_title = entry.title if hasattr(entry, 'title') else entry.get('title', '')
                    raw_description = entry.description if hasattr(entry, 'description') else entry.get('summary', '')
                    clean_title = clean_text(raw_title)
                    clean_description = clean_text(raw_description)
                    # 处理标签数据，确保将FeedParserDict对象转换为字符串
                    tags_list = entry.get("tags", [])
                    tag_strings = []
                    for tag in tags_list:
                        if isinstance(tag, dict) and 'term' in tag:
                            tag_strings.append(tag['term'])
                        elif isinstance(tag, str):
                            tag_strings.append(tag)
                    
                    # 创建新的Document实例
                    document = Document(
                        title=clean_title,
                        link=entry.link,
                        description=clean_description,
                        tags=",".join(tag_strings),
                        pub_date=datetime.datetime(*entry.get("published_parsed", time.struct_time((1970, 1, 1, 0, 0, 0, 0, 1, 0)))[:6]) if entry.get("published_parsed") else None,
                        author=entry.get("author", None),
                        rss_source_id=id
                    )
                    session.add(document)
                    session.commit()
                    # 刷新对象以确保所有属性都已正确设置
                    session.refresh(document)
                    app_logger.info(f"Added new document: {clean_title}")
                    document_list.append({
                        "id": document.id,
                        "title": document.title,
                        "link": document.link,
                        "description": document.description,
                        "tags": document.tags,
                        "pub_date": document.pub_date.isoformat() if document.pub_date else None,
                        "author": document.author
                    })  
                else:
                    app_logger.info(f"Document already exists in DB: {entry.title}")
        else:
            app_logger.warning(f"No entries found in RSS feed from {rss_source.url}")
            return False
        
        # 在新线程中执行知识库存储操作
        if document_list:  # 只有当有文档需要存储时才创建线程
            # 发送邮件通知
            try:
                to_emails = os.getenv("NOTIFICATION_EMAILS", "").split(",")
                subject = f"New Documents from RSS Source ID {rss_source.id}"
                message = f"Fetched and stored {len(document_list)} new documents from RSS source: {rss_source.url}\n\n"
                for doc in document_list:
                    message += f"- {doc['title']} ({doc['link']})\n"
                send_notification_email(to_emails, subject, message)
            except Exception as e:
                app_logger.error(f"Failed to send notification email: {str(e)}")
                # 即使邮件发送失败，也继续执行知识库存储
                pass
            kb_thread = threading.Thread(target=store_documents_in_knowledge_base, args=(document_list,))
            kb_thread.daemon = True  # 设置为守护线程，主线程退出时自动结束
            kb_thread.start()
            app_logger.info(f"Started background thread to store {len(document_list)} documents in knowledge base")
        
        # 主进程可以继续执行其他任务，不会被阻塞
        return True


