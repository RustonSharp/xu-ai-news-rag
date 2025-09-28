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
from tools import create_knowledge_base_tool

# 定义一个函数，用于从RSS源中获取数据
def fetch_rss_feeds(id:int, session:Session) -> bool:
    rss_source = session.exec(select(RssSource).where(RssSource.id == id)).first()
    if rss_source:
        # 解析RSS源
        app_logger.info(f"Fetching RSS feeds from {rss_source.url}")    
        rss_feed = feedparser.parse(rss_source.url)
        app_logger.info(f"完整信息: {rss_feed}")
        if rss_feed.entries:
            app_logger.info(f"Successfully fetched {len(rss_feed.entries)} entries from {rss_source.url}")
            document_list = []
            # 处理每个条目
            for entry in rss_feed.entries:
                app_logger.info(f"Entry Title: {entry.title}")
                app_logger.info(f"Entry Link: {entry.link}")
                app_logger.info(f"Entry Description: {entry.description}")
                app_logger.info("="*40)  # 分隔线
                # 检查数据库中是否已存在相同的链接
                existing_doc = session.exec(select(Document).where(Document.link == entry.link)).first()
                if not existing_doc:
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
                        title=entry.title,
                        link=entry.link,
                        description=entry.description,
                        tags=",".join(tag_strings),
                        pub_date=datetime.datetime(*entry.get("published_parsed", time.struct_time((1970, 1, 1, 0, 0, 0, 0, 1, 0)))[:6]) if entry.get("published_parsed") else None,
                        author=entry.get("author", None),
                        rss_source_id=id
                    )
                    session.add(document)
                    session.commit()
                    # 刷新对象以确保所有属性都已正确设置
                    session.refresh(document)
                    app_logger.info(f"Added new document: {entry.title}")
                    document_list.append(document)
                else:
                    app_logger.info(f"Document already exists in DB: {entry.title}")
        else:
            app_logger.warning(f"No entries found in RSS feed from {rss_source.url}")
            return False
        
        # 调用工具函数创建知识库 - 异步写入
        # 启动异步写入进程
        tool = create_knowledge_base_tool()
        # 确保所有文档都已正确保存并刷新后再转换为字典
        try:
            # 执行写入操作
            result = tool.run({"action": "store", "documents": document_list})
            # 记录结果
            app_logger.info(f"Knowledge Base Tool Result: {result}")
        except Exception as e:
            app_logger.error(f"Failed to process documents for knowledge base: {str(e)}")
            # 即使知识库存储失败，也继续执行其他任务
            pass

        # 主进程可以继续执行其他任务，不会被阻塞
        return True


