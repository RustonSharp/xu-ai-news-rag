"""
统一数据源Service，支持RSS、Web爬取等多种类型的数据源管理。
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlmodel import Session, select, func, and_, or_, desc
from models.source import Source, SourceType, SourceInterval
from schemas.requests import (
    SourceCreate, SourceUpdate, SourceSearchParams
)
from schemas.responses import (
    SourceResponse, SourceListResponse, SourceStatsResponse, SourceTriggerResponse
)
from services.knowledge_base.vector_store_service import vector_store_service
from utils.logging_config import app_logger
import feedparser
import requests
from bs4 import BeautifulSoup
import threading
from utils.email_sender import send_notification_email
from config.settings import settings
import json


class SourceService:
    """统一数据源Service，支持多种数据源类型"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_source(self, source_data: SourceCreate) -> SourceResponse:
        """创建新的数据源"""
        try:
            # 检查URL是否已存在
            existing_source = self._get_by_url(source_data.url)
            if existing_source:
                raise ValueError("数据源URL已存在")
            
            # 计算下次同步时间
            next_sync = self._calculate_next_sync_time(source_data.interval)
            
            # 创建数据源模型实例
            source = Source(
                name=source_data.name,
                url=source_data.url,
                source_type=source_data.source_type,
                interval=source_data.interval,
                description=source_data.description,
                tags=source_data.tags,
                config=json.dumps(source_data.config) if source_data.config else None,
                next_sync=next_sync,
                last_sync=None,
                is_paused=False,
                is_active=True,
                total_documents=0,
                last_document_count=0,
                sync_errors=0,
                last_error=None
            )
            
            self.session.add(source)
            self.session.commit()
            self.session.refresh(source)
            
            return SourceResponse.model_validate(source)
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"Error creating source: {str(e)}")
            raise
    
    def get_source(self, source_id: int) -> Optional[SourceResponse]:
        """获取数据源详情"""
        try:
            source = self._get_by_id(source_id)
            if not source:
                return None
            return SourceResponse.model_validate(source)
        except Exception as e:
            app_logger.error(f"Error getting source {source_id}: {str(e)}")
            raise
    
    def get_sources(self, search_params: SourceSearchParams) -> SourceListResponse:
        """获取数据源列表"""
        try:
            # 构建过滤条件
            filters = {}
            if search_params.source_type:
                filters['source_type'] = search_params.source_type
            if search_params.interval:
                filters['interval'] = search_params.interval
            if search_params.is_paused is not None:
                filters['is_paused'] = search_params.is_paused
            if search_params.is_active is not None:
                filters['is_active'] = search_params.is_active
            
            # 获取数据源
            if search_params.search:
                sources = self._search_sources(
                    search_params.search,
                    skip=(search_params.page - 1) * search_params.size,
                    limit=search_params.size
                )
                total = len(sources)  # 简化处理
            else:
                sources = self._filter_by(
                    filters,
                    skip=(search_params.page - 1) * search_params.size,
                    limit=search_params.size
                )
                total = self._count()
            
            # 转换为响应格式
            source_responses = [SourceResponse.from_orm(source) for source in sources]
            total_pages = (total + search_params.size - 1) // search_params.size
            
            return SourceListResponse(
                sources=source_responses,
                total=total,
                page=search_params.page,
                size=search_params.size,
                total_pages=total_pages
            )
        except Exception as e:
            app_logger.error(f"Error getting sources: {str(e)}")
            raise
    
    def update_source(self, source_id: int, update_data: SourceUpdate) -> Optional[SourceResponse]:
        """更新数据源"""
        try:
            # 检查URL是否被其他数据源使用
            if update_data.url:
                existing_source = self._get_by_url(update_data.url)
                if existing_source and existing_source.id != source_id:
                    raise ValueError("数据源URL已被其他数据源使用")
            
            # 转换更新数据
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
            
            # 处理配置字段
            if 'config' in update_dict and update_dict['config']:
                update_dict['config'] = json.dumps(update_dict['config'])
            
            # 更新下次同步时间
            if 'interval' in update_dict:
                update_dict['next_sync'] = self._calculate_next_sync_time(update_dict['interval'])
            
            source = self._update(source_id, update_dict)
            if not source:
                return None
            
            return SourceResponse.model_validate(source)
        except ValueError as e:
            raise
        except Exception as e:
            app_logger.error(f"Error updating source {source_id}: {str(e)}")
            raise
    
    def delete_source(self, source_id: int) -> bool:
        """删除数据源"""
        try:
            return self._delete(source_id)
        except Exception as e:
            app_logger.error(f"Error deleting source {source_id}: {str(e)}")
            raise
    
    def trigger_collection(self, source_id: int) -> SourceTriggerResponse:
        """触发数据源采集"""
        try:
            source = self._get_by_id(source_id)
            if not source:
                return SourceTriggerResponse(
                    message="数据源不存在",
                    success=False,
                    source_type="unknown"
                )
            
            start_time = datetime.now()
            
            # 根据数据源类型进行采集
            if source.source_type == "rss":
                documents_fetched = self._fetch_rss_feeds(source)
            elif source.source_type == "web":
                documents_fetched = self._fetch_web_content(source)
            else:
                return SourceTriggerResponse(
                    message=f"不支持的数据源类型: {source.source_type}",
                    success=False,
                    source_type=source.source_type
                )
            
            # 更新同步时间
            now = datetime.now()
            next_sync = self._calculate_next_sync_time(source.interval)
            self._update_sync_time(
                source_id, now, next_sync, 
                documents_fetched, 0, None
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return SourceTriggerResponse(
                message="数据采集完成",
                success=True,
                documents_fetched=documents_fetched,
                source_type=source.source_type,
                sync_duration=duration
            )
        except Exception as e:
            app_logger.error(f"Error triggering collection for source {source_id}: {str(e)}")
            return SourceTriggerResponse(
                message=f"数据采集失败: {str(e)}",
                success=False,
                source_type="unknown"
            )
    
    def get_sources_due_for_sync(self) -> List[SourceResponse]:
        """获取需要同步的数据源"""
        try:
            sources = self._get_sources_due_for_sync()
            return [SourceResponse.model_validate(source) for source in sources]
        except Exception as e:
            app_logger.error(f"Error getting sources due for sync: {str(e)}")
            raise
    
    def get_source_statistics(self) -> SourceStatsResponse:
        """获取数据源统计信息"""
        try:
            stats = self._get_source_statistics()
            return SourceStatsResponse(**stats)
        except Exception as e:
            app_logger.error(f"Error getting source statistics: {str(e)}")
            raise
    
    def _calculate_next_sync_time(self, interval: str) -> datetime:
        """计算下次同步时间"""
        now = datetime.now()
        
        if interval == 'SIX_HOUR':
            next_sync = now.replace(hour=6, minute=0, second=0, microsecond=0)
            if next_sync < now:
                next_sync += timedelta(days=1)
        elif interval == 'TWELVE_HOUR':
            next_sync = now.replace(hour=12, minute=0, second=0, microsecond=0)
            if next_sync < now:
                next_sync += timedelta(days=1)
        elif interval == 'THREE_DAY':
            next_sync = now.replace(hour=0, minute=0, second=0, microsecond=0)
            next_sync += timedelta(days=3)
        elif interval == 'WEEKLY':
            next_sync = now.replace(hour=0, minute=0, second=0, microsecond=0)
            next_sync += timedelta(days=7)
        else:  # ONE_DAY
            next_sync = now.replace(hour=0, minute=0, second=0, microsecond=0)
            next_sync += timedelta(days=1)
        
        return next_sync
    
    def _fetch_rss_feeds(self, source) -> int:
        """获取RSS订阅内容"""
        try:
            app_logger.info(f"Fetching RSS feeds from {source.url}")
            
            # 验证和规范化URL
            url = self._normalize_url(source.url)
            if not url:
                raise ValueError(f"Invalid URL: {source.url}")
            
            # 解析RSS订阅
            rss_feed = feedparser.parse(url)
            if not rss_feed.entries:
                app_logger.warning(f"No entries found in RSS feed from {source.url}")
                return 0
            
            app_logger.info(f"Successfully fetched {len(rss_feed.entries)} entries from {source.url}")
            
            documents_created = 0
            document_list = []
            
            for entry in rss_feed.entries:
                try:
                    # 检查文档是否已存在
                    from services.document_service import DocumentService
                    doc_service = DocumentService(self.session)
                    existing_doc = doc_service._get_by_link(entry.link)
                    
                    if existing_doc:
                        continue
                    
                    # 清理和处理条目数据
                    clean_title = self._clean_text(entry.title if hasattr(entry, 'title') else entry.get('title', ''))
                    clean_description = self._clean_text(entry.description if hasattr(entry, 'description') else entry.get('summary', ''))
                    
                    # 处理标签
                    tags_list = entry.get("tags", [])
                    tag_strings = []
                    for tag in tags_list:
                        if isinstance(tag, dict) and 'term' in tag:
                            tag_strings.append(tag['term'])
                        elif isinstance(tag, str):
                            tag_strings.append(tag)
                    
                    # 创建文档
                    from models.document import Document
                    from services.document_service import DocumentService
                    doc_service = DocumentService(self.session)
                    document = Document(
                        title=clean_title,
                        link=entry.link,
                        description=clean_description,
                        tags=",".join(tag_strings),
                        pub_date=self._parse_pub_date(entry),
                        author=entry.get("author", None),
                        source_id=source.id
                    )
                    
                    # 创建文档
                    document = doc_service._create(document)
                    documents_created += 1
                    
                    # 准备知识库数据
                    document_list.append({
                        "title": document.title,
                        "description": document.description,
                        "tags": document.tags,
                        "pub_date": document.pub_date.isoformat() if document.pub_date else "",
                        "author": document.author
                    })
                    
                    app_logger.info(f"Created document: {clean_title}")
                    
                except Exception as e:
                    app_logger.error(f"Error processing RSS entry: {str(e)}")
                    continue
            
            # 添加到知识库
            if document_list:
                self._add_to_knowledge_base_async(document_list)
                self._send_notification_email(source, documents_created, document_list)
            
            return documents_created
            
        except Exception as e:
            app_logger.error(f"Error fetching RSS feeds: {str(e)}")
            raise
    
    def _fetch_web_content(self, source) -> int:
        """获取Web内容"""
        try:
            app_logger.info(f"Fetching web content from {source.url}")
            
            # 解析配置
            config = json.loads(source.config) if source.config else {}
            headers = config.get('web_headers', {})
            timeout = config.get('web_timeout', 30)
            
            # 验证和规范化URL
            url = self._normalize_url(source.url)
            if not url:
                raise ValueError(f"Invalid URL: {source.url}")
            
            # 发送HTTP请求
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取内容
            title_selector = config.get('title_selector', 'h1, h2, h3')
            content_selector = config.get('content_selector', 'p, div')
            
            titles = soup.select(title_selector)
            contents = soup.select(content_selector)
            
            documents_created = 0
            document_list = []
            
            for i, (title_elem, content_elem) in enumerate(zip(titles, contents)):
                try:
                    title = self._clean_text(title_elem.get_text())
                    content = self._clean_text(content_elem.get_text())
                    
                    if not title or not content:
                        continue
                    
                    # 创建文档
                    from models.document import Document
                    from services.document_service import DocumentService
                    # DocumentRepository functionality is now in DocumentService
                    doc_service = DocumentService(self.session)
                    document = Document(
                        title=title,
                        link=source.url,
                        description=content,
                        tags=source.tags or "",
                        pub_date=datetime.now(),
                        author=None,
                        source_id=source.id
                    )
                    
                    # 创建文档
                    document = doc_service._create(document)
                    documents_created += 1
                    
                    # 准备知识库数据
                    document_list.append({
                        "title": document.title,
                        "description": document.description,
                        "tags": document.tags,
                        "pub_date": document.pub_date.isoformat() if document.pub_date else "",
                        "author": document.author
                    })
                    
                except Exception as e:
                    app_logger.error(f"Error processing web content item {i}: {str(e)}")
                    continue
            
            # 添加到知识库
            if document_list:
                self._add_to_knowledge_base_async(document_list)
                self._send_notification_email(source, documents_created, document_list)
            
            return documents_created
            
        except Exception as e:
            app_logger.error(f"Error fetching web content: {str(e)}")
            raise
    
    def _normalize_url(self, url: str) -> str:
        """规范化URL，确保包含scheme"""
        if not url:
            return None
        
        url = url.strip()
        
        # 如果URL已经包含scheme，直接返回
        if url.startswith(('http://', 'https://')):
            return url
        
        # 如果URL以//开头，添加https://
        if url.startswith('//'):
            return f"https:{url}"
        
        # 如果URL不包含scheme，添加https://
        if not url.startswith(('http://', 'https://', 'ftp://', 'file://')):
            return f"https://{url}"
        
        return url
    
    def _clean_text(self, raw: str) -> str:
        """清理HTML/Markdown文本为纯文本"""
        if not isinstance(raw, str):
            raw = str(raw or "")
        
        text = raw
        try:
            text = BeautifulSoup(text, 'html.parser').get_text(separator=' ')
        except Exception:
            pass
        
        # 移除Markdown和其他格式
        import re
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
        text = re.sub(r"```[\s\S]*?```", " ", text)
        text = re.sub(r"`([^`]*)`", r"\1", text)
        text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s{0,3}[-*+]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s{0,3}>\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)
        text = re.sub(r"\s+", " ", text).strip()
        
        return text
    
    def _parse_pub_date(self, entry) -> Optional[datetime]:
        """解析发布日期"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                import time
                return datetime(*entry.published_parsed[:6])
        except Exception:
            pass
        return None
    
    def _add_to_knowledge_base_async(self, document_list: List[Dict[str, Any]]):
        """异步添加文档到知识库"""
        def add_to_kb():
            try:
                vector_store_service.add_documents(document_list)
                app_logger.info(f"Added {len(document_list)} documents to knowledge base")
            except Exception as e:
                app_logger.error(f"Error adding documents to knowledge base: {str(e)}")
        
        thread = threading.Thread(target=add_to_kb)
        thread.daemon = True
        thread.start()
    
    def _send_notification_email(self, source, documents_created: int, document_list: List[Dict[str, Any]]):
        """发送通知邮件"""
        try:
            if not settings.NOTIFICATION_EMAILS:
                return
            
            subject = f"New Documents from {source.source_type.upper()} Source: {source.name}"
            message = f"Fetched and stored {documents_created} new documents from {source.source_type} source: {source.url}\n\n"
            
            for doc in document_list[:5]:  # 显示前5个文档
                message += f"- {doc['title']}\n"
            
            if len(document_list) > 5:
                message += f"... and {len(document_list) - 5} more documents\n"
            
            send_notification_email(settings.NOTIFICATION_EMAILS, subject, message)
        except Exception as e:
            app_logger.error(f"Error sending notification email: {str(e)}")
    
    # RSS-specific methods for backward compatibility
    def get_rss_sources(self, session: Session) -> List[SourceResponse]:
        """获取RSS源列表（向后兼容）"""
        try:
            sources = self._filter_by({'source_type': 'rss'})
            return [SourceResponse.model_validate(source) for source in sources]
        except Exception as e:
            app_logger.error(f"Error getting RSS sources: {str(e)}")
            raise
    
    def get_rss_source_by_id(self, source_id: int, session: Session) -> Optional[SourceResponse]:
        """根据ID获取RSS源（向后兼容）"""
        try:
            source = self._get_by_id(source_id)
            if not source or source.source_type != 'rss':
                return None
            return SourceResponse.model_validate(source)
        except Exception as e:
            app_logger.error(f"Error getting RSS source {source_id}: {str(e)}")
            raise
    
    def create_rss_source(self, source_data: Dict[str, Any], session: Session) -> SourceResponse:
        """创建RSS源（向后兼容）"""
        try:
            # 检查URL是否已存在
            existing_source = self._get_by_url(source_data['url'])
            if existing_source:
                raise ValueError("RSS源URL已存在")
            
            # 创建SourceCreate对象
            from schemas.requests import SourceCreate
            create_data = SourceCreate(
                name=source_data['name'],
                url=source_data['url'],
                source_type='rss',
                interval=source_data.get('interval', 'ONE_DAY'),
                description=source_data.get('description', ''),
                tags=','.join(source_data.get('tags', [])) if source_data.get('tags') else None,
                config=source_data.get('config', {})
            )
            
            return self.create_source(create_data)
        except Exception as e:
            app_logger.error(f"Error creating RSS source: {str(e)}")
            raise
    
    def update_rss_source(self, source_id: int, update_data: Dict[str, Any], session: Session) -> Optional[SourceResponse]:
        """更新RSS源（向后兼容）"""
        try:
            from schemas.requests import SourceUpdate
            update_schema = SourceUpdate(**update_data)
            return self.update_source(source_id, update_schema)
        except Exception as e:
            app_logger.error(f"Error updating RSS source {source_id}: {str(e)}")
            raise
    
    def delete_rss_source(self, source_id: int, session: Session) -> bool:
        """删除RSS源（向后兼容）"""
        try:
            return self.delete_source(source_id)
        except Exception as e:
            app_logger.error(f"Error deleting RSS source {source_id}: {str(e)}")
            raise
    
    def pause_rss_source(self, source_id: int, session: Session) -> bool:
        """暂停RSS源"""
        try:
            source = self._get_by_id(source_id)
            if not source or source.source_type != 'rss':
                return False
            
            update_data = {'is_paused': True}
            updated_source = self._update(source_id, update_data)
            return updated_source is not None
        except Exception as e:
            app_logger.error(f"Error pausing RSS source {source_id}: {str(e)}")
            raise
    
    def resume_rss_source(self, source_id: int, session: Session) -> bool:
        """恢复RSS源"""
        try:
            source = self._get_by_id(source_id)
            if not source or source.source_type != 'rss':
                return False
            
            update_data = {'is_paused': False}
            updated_source = self._update(source_id, update_data)
            return updated_source is not None
        except Exception as e:
            app_logger.error(f"Error resuming RSS source {source_id}: {str(e)}")
            raise
    
    def get_active_rss_sources(self, session: Session) -> List[SourceResponse]:
        """获取活跃的RSS源"""
        try:
            sources = self._filter_by({
                'source_type': 'rss',
                'is_paused': False,
                'is_active': True
            })
            return [SourceResponse.model_validate(source) for source in sources]
        except Exception as e:
            app_logger.error(f"Error getting active RSS sources: {str(e)}")
            raise
    
    def validate_rss_url(self, url: str) -> bool:
        """验证RSS URL"""
        try:
            normalized_url = self._normalize_url(url)
            if not normalized_url:
                return False
            
            # 尝试解析RSS feed
            rss_feed = feedparser.parse(normalized_url)
            return len(rss_feed.entries) > 0
        except Exception as e:
            app_logger.error(f"Error validating RSS URL {url}: {str(e)}")
            return False
    
    def get_rss_source_statistics(self, session: Session) -> Dict[str, Any]:
        """获取RSS源统计信息"""
        try:
            stats = self._get_source_statistics()
            # 过滤只返回RSS源的统计
            rss_stats = {
                'total_sources': stats.get('total_sources', 0),
                'active_sources': stats.get('active_sources', 0),
                'paused_sources': stats.get('paused_sources', 0),
                'total_documents': stats.get('total_documents', 0),
                'last_24h_documents': stats.get('last_24h_documents', 0)
            }
            return rss_stats
        except Exception as e:
            app_logger.error(f"Error getting RSS source statistics: {str(e)}")
            raise
    
    # Private helper methods (formerly in SourceRepository)
    def _get_by_id(self, source_id: int) -> Optional[Source]:
        """Get source by ID."""
        try:
            return self.session.get(Source, source_id)
        except Exception as e:
            app_logger.error(f"Error getting source by ID {source_id}: {str(e)}")
            raise
    
    def _get_by_url(self, url: str, session: Optional[Session] = None) -> Optional[Source]:
        """Get source by URL."""
        try:
            current_session = session or self.session
            statement = select(Source).where(Source.url == url)
            return current_session.exec(statement).first()
        except Exception as e:
            app_logger.error(f"Error getting source by URL {url}: {str(e)}")
            raise
    
    def _update(self, source_id: int, update_data: Dict[str, Any], session: Optional[Session] = None) -> Optional[Source]:
        """Update source by ID."""
        try:
            current_session = session or self.session
            source = current_session.get(Source, source_id)
            if not source:
                return None
            
            for key, value in update_data.items():
                if hasattr(source, key):
                    setattr(source, key, value)
            
            current_session.commit()
            current_session.refresh(source)
            app_logger.info(f"Updated source with ID: {source_id}")
            return source
        except Exception as e:
            current_session.rollback()
            app_logger.error(f"Error updating source with ID {source_id}: {str(e)}")
            raise
    
    def _delete(self, source_id: int, session: Optional[Session] = None) -> bool:
        """Delete source by ID."""
        try:
            current_session = session or self.session
            source = current_session.get(Source, source_id)
            if not source:
                return False
            
            current_session.delete(source)
            current_session.commit()
            app_logger.info(f"Deleted source with ID: {source_id}")
            return True
        except Exception as e:
            current_session.rollback()
            app_logger.error(f"Error deleting source with ID {source_id}: {str(e)}")
            raise
    
    def _count(self) -> int:
        """Count total sources."""
        try:
            statement = select(func.count()).select_from(Source)
            return self.session.exec(statement).one()
        except Exception as e:
            app_logger.error(f"Error counting sources: {str(e)}")
            raise
    
    def _search_sources(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Source]:
        """Search sources by name, URL, or description."""
        try:
            statement = (
                select(Source)
                .where(
                    or_(
                        Source.name.contains(search_term),
                        Source.url.contains(search_term),
                        Source.description.contains(search_term),
                        Source.tags.contains(search_term)
                    )
                )
                .order_by(Source.name.asc())
                .offset(skip)
                .limit(limit)
            )
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error searching sources: {str(e)}")
            raise
    
    def _filter_by(self, filters: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Source]:
        """Filter sources by multiple criteria."""
        try:
            conditions = []
            for field, value in filters.items():
                if hasattr(Source, field):
                    field_attr = getattr(Source, field)
                    if isinstance(value, list):
                        conditions.append(field_attr.in_(value))
                    else:
                        conditions.append(field_attr == value)
            
            if not conditions:
                statement = select(Source).offset(skip).limit(limit)
            else:
                statement = select(Source).where(and_(*conditions)).offset(skip).limit(limit)
            
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error filtering sources: {str(e)}")
            raise
    
    def _get_sources_due_for_sync(self) -> List[Source]:
        """Get sources due for sync."""
        try:
            now = datetime.now()
            statement = (
                select(Source)
                .where(
                    and_(
                        Source.is_active == True,
                        Source.is_paused == False,
                        or_(
                            Source.next_sync <= now,
                            Source.next_sync.is_(None)
                        )
                    )
                )
                .order_by(Source.next_sync.asc())
            )
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting sources due for sync: {str(e)}")
            raise
    
    def _update_sync_time(self, source_id: int, last_sync: datetime, next_sync: datetime, 
                        documents_fetched: int = 0, sync_errors: int = 0, last_error: str = None) -> bool:
        """Update source sync time."""
        try:
            source = self._get_by_id(source_id)
            if not source:
                return False
            
            source.last_sync = last_sync
            source.next_sync = next_sync
            source.last_document_count = documents_fetched
            source.total_documents += documents_fetched
            source.sync_errors = sync_errors
            source.last_error = last_error
            source.updated_at = datetime.now()
            
            self.session.commit()
            self.session.refresh(source)
            app_logger.info(f"Updated sync time for source ID: {source_id}")
            return True
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"Error updating sync time for source ID {source_id}: {str(e)}")
            raise
    
    def _get_source_statistics(self) -> Dict[str, Any]:
        """Get source statistics."""
        try:
            total_sources = self._count()
            
            # 按类型统计
            statement = (
                select(Source.source_type, func.count(Source.id))
                .group_by(Source.source_type)
            )
            type_counts = dict(self.session.exec(statement).all())
            
            # 按间隔统计
            statement = (
                select(Source.interval, func.count(Source.id))
                .group_by(Source.interval)
            )
            interval_counts = dict(self.session.exec(statement).all())
            
            # 活跃数据源
            statement = select(func.count(Source.id)).where(Source.is_active == True)
            active_sources = self.session.exec(statement).one()
            
            # 暂停的数据源
            statement = select(func.count(Source.id)).where(Source.is_paused == True)
            paused_sources = self.session.exec(statement).one()
            
            # 需要同步的数据源
            sources_due = len(self._get_sources_due_for_sync())
            
            # 总文档数
            statement = select(func.sum(Source.total_documents))
            total_documents = self.session.exec(statement).one() or 0
            
            return {
                "total_sources": total_sources,
                "sources_by_type": type_counts,
                "sources_by_interval": interval_counts,
                "active_sources": active_sources,
                "paused_sources": paused_sources,
                "sources_due_for_sync": sources_due,
                "total_documents": total_documents
            }
        except Exception as e:
            app_logger.error(f"Error getting source statistics: {str(e)}")
            raise