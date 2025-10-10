"""
统一数据源Repository，支持RSS、Web爬取等多种类型的数据源管理。
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select, func, and_, or_, desc
from models.source import Source, SourceType, SourceInterval
from repositories.base_repository import BaseRepository
from utils.logging_config import app_logger


class SourceRepository(BaseRepository[Source]):
    """统一数据源Repository，支持多种数据源类型"""
    
    def __init__(self, session: Optional[Session] = None):
        super().__init__(session, Source)
    
    def get_by_url(self, url: str, session: Optional[Session] = None) -> Optional[Source]:
        """根据URL获取数据源"""
        try:
            current_session = session or self.session
            statement = select(Source).where(Source.url == url)
            return current_session.exec(statement).first()
        except Exception as e:
            app_logger.error(f"Error getting source by URL {url}: {str(e)}")
            raise
    
    def get_by_type(self, source_type: SourceType, skip: int = 0, limit: int = 100) -> List[Source]:
        """根据类型获取数据源"""
        try:
            statement = (
                select(Source)
                .where(Source.source_type == source_type)
                .order_by(Source.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting sources by type {source_type}: {str(e)}")
            raise
    
    def get_sources_with_document_counts(self) -> List[Dict[str, Any]]:
        """获取数据源及其文档数量"""
        try:
            # 获取所有数据源
            sources = self.get_all()
            source_ids = [source.id for source in sources]
            
            # 获取文档数量
            from models.document import Document
            document_counts = {}
            if source_ids:
                statement = (
                    select(Document.source_id, func.count(Document.id))
                    .where(Document.source_id.in_(source_ids))
                    .group_by(Document.source_id)
                )
                results = self.session.exec(statement).all()
                document_counts = {source_id: count for source_id, count in results}
            
            # 合并数据源和文档数量
            sources_with_counts = []
            for source in sources:
                source_dict = {
                    "id": source.id,
                    "name": source.name,
                    "url": source.url,
                    "source_type": source.source_type,
                    "interval": source.interval,
                    "is_paused": source.is_paused,
                    "is_active": source.is_active,
                    "last_sync": source.last_sync.isoformat() if source.last_sync else None,
                    "next_sync": source.next_sync.isoformat() if source.next_sync else None,
                    "document_count": document_counts.get(source.id, 0),
                    "total_documents": source.total_documents,
                    "sync_errors": source.sync_errors,
                    "last_error": source.last_error,
                    "created_at": source.created_at.isoformat(),
                    "updated_at": source.updated_at.isoformat()
                }
                sources_with_counts.append(source_dict)
            
            return sources_with_counts
        except Exception as e:
            app_logger.error(f"Error getting sources with document counts: {str(e)}")
            raise
    
    def get_sources_due_for_sync(self) -> List[Source]:
        """获取需要同步的数据源"""
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
    
    def update_sync_time(self, source_id: int, last_sync: datetime, next_sync: datetime, 
                        documents_fetched: int = 0, sync_errors: int = 0, last_error: str = None) -> bool:
        """更新数据源同步时间"""
        try:
            source = self.get_by_id(source_id)
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
    
    def get_sources_by_interval(self, interval: SourceInterval) -> List[Source]:
        """根据同步间隔获取数据源"""
        try:
            statement = select(Source).where(Source.interval == interval)
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting sources by interval {interval}: {str(e)}")
            raise
    
    def get_source_statistics(self) -> Dict[str, Any]:
        """获取数据源统计信息"""
        try:
            total_sources = self.count()
            
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
            sources_due = len(self.get_sources_due_for_sync())
            
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
    
    def search_sources(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Source]:
        """搜索数据源"""
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
    
    def get_sources_by_tags(self, tags: List[str], skip: int = 0, limit: int = 100) -> List[Source]:
        """根据标签获取数据源"""
        try:
            conditions = []
            for tag in tags:
                conditions.append(Source.tags.contains(tag))
            
            if not conditions:
                return []
            
            statement = (
                select(Source)
                .where(or_(*conditions))
                .order_by(Source.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting sources by tags: {str(e)}")
            raise
    
    def get_recent_sources(self, days: int = 7, limit: int = 10) -> List[Source]:
        """获取最近创建的数据源"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            statement = (
                select(Source)
                .where(Source.created_at >= cutoff_date)
                .order_by(desc(Source.created_at))
                .limit(limit)
            )
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting recent sources: {str(e)}")
            raise
    
    def get_error_sources(self, limit: int = 50) -> List[Source]:
        """获取有错误的数据源"""
        try:
            statement = (
                select(Source)
                .where(Source.sync_errors > 0)
                .order_by(desc(Source.sync_errors))
                .limit(limit)
            )
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting error sources: {str(e)}")
            raise
    
    def reset_source_errors(self, source_id: int) -> bool:
        """重置数据源错误计数"""
        try:
            source = self.get_by_id(source_id)
            if not source:
                return False
            
            source.sync_errors = 0
            source.last_error = None
            source.updated_at = datetime.now()
            
            self.session.commit()
            self.session.refresh(source)
            app_logger.info(f"Reset errors for source ID: {source_id}")
            return True
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"Error resetting errors for source ID {source_id}: {str(e)}")
            raise
    
    def get_active_sources(self, session: Optional[Session] = None) -> List[Source]:
        """获取活跃的数据源"""
        try:
            current_session = session or self.session
            statement = (
                select(Source)
                .where(and_(Source.is_active == True, Source.is_paused == False))
                .order_by(Source.created_at.desc())
            )
            return list(current_session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting active sources: {str(e)}")
            raise
    
    def get_paused_sources(self, session: Optional[Session] = None) -> List[Source]:
        """获取暂停的数据源"""
        try:
            current_session = session or self.session
            statement = (
                select(Source)
                .where(Source.is_paused == True)
                .order_by(Source.created_at.desc())
            )
            return list(current_session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting paused sources: {str(e)}")
            raise
