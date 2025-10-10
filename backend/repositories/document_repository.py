"""
Document repository for database operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select, func, and_, or_, desc
from models.document import Document
from models.source import Source
from repositories.base_repository import BaseRepository
from utils.logging_config import app_logger


class DocumentRepository(BaseRepository[Document]):
    """Repository for document operations."""
    
    def __init__(self, session: Session):
        super().__init__(session, Document)
    
    def get_by_source_id(self, source_id: int, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get documents by source ID."""
        try:
            statement = (
                select(Document)
                .where(Document.source_id == source_id)
                .order_by(desc(Document.crawled_at))
                .offset(skip)
                .limit(limit)
            )
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting documents by source ID {source_id}: {str(e)}")
            raise
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get documents by date range."""
        try:
            statement = (
                select(Document)
                .where(
                    and_(
                        Document.crawled_at >= start_date,
                        Document.crawled_at <= end_date
                    )
                )
                .order_by(desc(Document.crawled_at))
                .offset(skip)
                .limit(limit)
            )
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting documents by date range: {str(e)}")
            raise
    
    def search_documents(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Document]:
        """Search documents by title and description."""
        try:
            statement = (
                select(Document)
                .where(
                    or_(
                        Document.title.contains(search_term),
                        Document.description.contains(search_term)
                    )
                )
                .order_by(desc(Document.crawled_at))
                .offset(skip)
                .limit(limit)
            )
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error searching documents: {str(e)}")
            raise
    
    def get_by_tags(self, tags: List[str], skip: int = 0, limit: int = 100) -> List[Document]:
        """Get documents by tags."""
        try:
            conditions = []
            for tag in tags:
                conditions.append(Document.tags.contains(tag))
            
            if not conditions:
                return []
            
            statement = (
                select(Document)
                .where(or_(*conditions))
                .order_by(desc(Document.crawled_at))
                .offset(skip)
                .limit(limit)
            )
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting documents by tags: {str(e)}")
            raise
    
    def get_document_count_by_source(self) -> Dict[int, int]:
        """Get document count grouped by RSS source."""
        try:
            statement = (
                select(Document.rss_source_id, func.count(Document.id))
                .group_by(Document.rss_source_id)
            )
            results = self.session.exec(statement).all()
            return {source_id: count for source_id, count in results if source_id is not None}
        except Exception as e:
            app_logger.error(f"Error getting document count by source: {str(e)}")
            raise
    
    def get_recent_documents(self, days: int = 7, limit: int = 10) -> List[Document]:
        """Get recent documents within specified days."""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            statement = (
                select(Document)
                .where(Document.crawled_at >= cutoff_date)
                .order_by(desc(Document.crawled_at))
                .limit(limit)
            )
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting recent documents: {str(e)}")
            raise
    
    def get_top_tags(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most common tags."""
        try:
            # This is a simplified implementation
            # In a real scenario, you might want to use a more sophisticated approach
            all_docs = self.get_all(limit=1000)  # Get a large sample
            tag_counts = {}
            
            for doc in all_docs:
                if doc.tags:
                    tags = [tag.strip() for tag in doc.tags.split(',') if tag.strip()]
                    for tag in tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Sort by count and return top tags
            sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            return [{"tag": tag, "count": count} for tag, count in sorted_tags[:limit]]
        except Exception as e:
            app_logger.error(f"Error getting top tags: {str(e)}")
            raise
    
    def get_documents_with_source_info(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get documents with RSS source information."""
        try:
            statement = (
                select(Document, Source)
                .join(Source, Document.source_id == Source.id)
                .order_by(desc(Document.crawled_at))
                .offset(skip)
                .limit(limit)
            )
            
            results = self.session.exec(statement).all()
            documents_with_source = []
            
            for doc, source in results:
                doc_dict = {
                    "id": doc.id,
                    "title": doc.title,
                    "link": doc.link,
                    "description": doc.description,
                    "author": doc.author,
                    "tags": doc.tags.split(",") if doc.tags else [],
                    "pub_date": doc.pub_date.isoformat() if doc.pub_date else None,
                    "crawled_at": doc.crawled_at.isoformat(),
                    "rss_source": {
                        "id": source.id,
                        "name": source.name,
                        "url": source.url
                    }
                }
                documents_with_source.append(doc_dict)
            
            return documents_with_source
        except Exception as e:
            app_logger.error(f"Error getting documents with source info: {str(e)}")
            raise
    
    def get_paginated(self, page: int = 1, size: int = 20, search: Optional[str] = None, 
                     doc_type: Optional[str] = None, source: Optional[str] = None,
                     start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get paginated documents with optional filtering."""
        try:
            # Calculate offset
            offset = (page - 1) * size
            
            # Build base query
            statement = select(Document)
            count_statement = select(func.count(Document.id))
            
            # Apply filters
            conditions = []
            
            if search:
                conditions.append(
                    or_(
                        Document.title.contains(search),
                        Document.description.contains(search)
                    )
                )
            
            if doc_type:
                # For now, we'll use tags to filter by type
                conditions.append(Document.tags.contains(doc_type))
            
            if source:
                # Join with Source table to filter by source name
                statement = statement.join(Source, Document.source_id == Source.id)
                count_statement = count_statement.join(Source, Document.source_id == Source.id)
                conditions.append(Source.name.contains(source))
            
            if start_date:
                conditions.append(Document.crawled_at >= start_date)
            
            if end_date:
                conditions.append(Document.crawled_at <= end_date)
            
            # Apply conditions
            if conditions:
                statement = statement.where(and_(*conditions))
                count_statement = count_statement.where(and_(*conditions))
            
            # Get total count
            total = self.session.exec(count_statement).one()
            
            # Get paginated results
            statement = statement.order_by(desc(Document.crawled_at)).offset(offset).limit(size)
            documents = list(self.session.exec(statement))
            
            # Calculate total pages
            total_pages = (total + size - 1) // size
            
            return {
                "items": documents,
                "total": total,
                "page": page,
                "size": size,
                "total_pages": total_pages
            }
        except Exception as e:
            app_logger.error(f"Error getting paginated documents: {str(e)}")
            raise