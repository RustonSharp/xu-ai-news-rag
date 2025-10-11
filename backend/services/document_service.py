"""
Document service for document fetching and knowledge base operations.
"""
import threading
import datetime
import time
import re
from datetime import timedelta
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select, func, and_, or_, desc
from bs4 import BeautifulSoup
from models.source import Source, SourceType
from models.document import Document
from services.knowledge_base.vector_store_service import vector_store_service
from utils.logging_config import app_logger
from utils.email_sender import send_notification_email
import os


class DocumentService:
    """Service for document operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def _get_or_create_file_source(self) -> Source:
        """
        Get or create a FILE type source for Excel uploads.
        
        Returns:
            Source: The FILE type source
        """
        # Try to find existing FILE type source
        file_source = self.session.exec(
            select(Source).where(Source.source_type == SourceType.FILE)
        ).first()
        
        if not file_source:
            # Create new FILE type source
            file_source = Source(
                name="Excel Uploads",
                url="file://excel_uploads",
                source_type=SourceType.FILE,
                description="Documents uploaded via Excel files",
                tags="excel,upload,file"
            )
            self.session.add(file_source)
            self.session.commit()
            self.session.refresh(file_source)
            app_logger.info(f"Created new FILE type source with ID: {file_source.id}")
        
        return file_source
    
    def _create_excel_source(self, filename: str) -> Source:
        """
        Create a unique FILE type source for a specific Excel file.
        
        Args:
            filename: Name of the Excel file
            
        Returns:
            Source: The newly created FILE type source
        """
        # Generate source name with filename and timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        source_name = f"{filename}_{timestamp}"
        
        # Create new FILE type source for this Excel file
        file_source = Source(
            name=source_name,
            url=f"file://excel_uploads/{filename}",
            source_type=SourceType.FILE,
            description=f"Documents uploaded from Excel file: {filename}",
            tags=f"excel,upload,file,{filename}"
        )
        
        self.session.add(file_source)
        self.session.commit()
        self.session.refresh(file_source)
        app_logger.info(f"Created new FILE type source for Excel '{filename}' with ID: {file_source.id}")
        
        return file_source
    
    def clean_text(self, raw: str) -> str:
        """
        Clean HTML/Markdown to plain text:
        - Remove all HTML tags
        - Handle common Markdown (images, links, code, headers, lists, bold/italic, quotes)
        - Merge extra whitespace
        """
        if not isinstance(raw, str):
            raw = str(raw or "")

        text = raw
        # First use BeautifulSoup to remove HTML tags
        try:
            text = BeautifulSoup(text, 'html.parser').get_text(separator=' ')
        except Exception:
            pass

        # Remove Markdown images ![alt](url)
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
        # Keep text from Markdown links [text](url)
        text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
        # Remove inline code and code blocks
        text = re.sub(r"```[\s\S]*?```", " ", text)
        text = re.sub(r"`([^`]*)`", r"\1", text)
        # Remove header/list/quote markers
        text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s{0,3}[-*+]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s{0,3}>\s+", "", text, flags=re.MULTILINE)
        # Remove bold/italic markers
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)
        # Merge whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def store_documents_in_knowledge_base(self, document_list: List[Dict[str, Any]]):
        """
        Store documents in knowledge base (for execution in thread).
        """
        try:
            # Execute write operation
            result = vector_store_service.add_documents(document_list)
            app_logger.info(f"Knowledge Base Tool Result: {result}")
        except Exception as e:
            app_logger.error(f"Failed to process documents for knowledge base: {str(e)}")
            # Continue with other tasks even if knowledge base storage fails
            pass

    def fetch_rss_feeds(self, source_id: int) -> bool:
        """
        Fetch RSS feeds from a source.
        
        Args:
            source_id: ID of the RSS source
            
        Returns:
            True if successful, False otherwise
        """
        try:
            rss_source = self.session.exec(
                select(Source).where(Source.id == source_id, Source.source_type == "rss")
            ).first()
            
            if not rss_source:
                app_logger.warning(f"RSS source with ID {source_id} not found")
                return False
            
            document_list = []
            
            # Parse RSS source
            app_logger.info(f"Fetching RSS feeds from {rss_source.url}")
            import feedparser
            rss_feed = feedparser.parse(rss_source.url)
            app_logger.info(f"Complete info: {rss_feed}")
            
            if rss_feed.entries:
                app_logger.info(f"Successfully fetched {len(rss_feed.entries)} entries from {rss_source.url}")
                
                # Process each entry
                for entry in rss_feed.entries:
                    app_logger.info(f"Entry Title: {entry.title}")
                    app_logger.info(f"Entry Link: {entry.link}")
                    app_logger.info(f"Entry Description: {entry.description}")
                    app_logger.info("="*40)  # Separator
                    
                    # Check if document with same link already exists in database
                    existing_doc = self.session.exec(
                        select(Document).where(Document.link == entry.link)
                    ).first()
                    
                    if not existing_doc:
                        # Clean title and description
                        raw_title = entry.title if hasattr(entry, 'title') else entry.get('title', '')
                        raw_description = entry.description if hasattr(entry, 'description') else entry.get('summary', '')
                        clean_title = self.clean_text(raw_title)
                        clean_description = self.clean_text(raw_description)
                        
                        # Process tags data, ensure FeedParserDict objects are converted to strings
                        tags_list = entry.get("tags", [])
                        tag_strings = []
                        for tag in tags_list:
                            if isinstance(tag, dict) and 'term' in tag:
                                tag_strings.append(tag['term'])
                            elif isinstance(tag, str):
                                tag_strings.append(tag)
                        
                        # Create new Document instance
                        document = Document(
                            title=clean_title,
                            link=entry.link,
                            description=clean_description,
                            tags=",".join(tag_strings),
                            pub_date=datetime.datetime(*entry.get("published_parsed", time.struct_time((1970, 1, 1, 0, 0, 0, 0, 1, 0)))[:6]) if entry.get("published_parsed") else None,
                            author=entry.get("author", None),
                            source_id=source_id
                        )
                        
                        self.session.add(document)
                        self.session.commit()
                        # Refresh object to ensure all attributes are properly set
                        self.session.refresh(document)
                        app_logger.info(f"Added new document: {clean_title}")
                        
                        document_list.append({
                            "id": document.id,
                            "title": document.title,
                            "link": document.link,
                            "description": document.description,
                            "tags": document.tags,
                            "pub_date": document.pub_date.isoformat() if document.pub_date else None,
                            "author": document.author,
                            "source_id": document.source_id
                        })
                    else:
                        app_logger.info(f"Document already exists in DB: {entry.title}")
            else:
                app_logger.warning(f"No entries found in RSS feed from {rss_source.url}")
                return False
            
            # Execute knowledge base storage in new thread
            if document_list:  # Only create thread if there are documents to store
                # Send email notification
                try:
                    to_emails = os.getenv("NOTIFICATION_EMAILS", "").split(",")
                    subject = f"New Documents from RSS Source ID {rss_source.id}"
                    message = f"Fetched and stored {len(document_list)} new documents from RSS source: {rss_source.url}\n\n"
                    for doc in document_list:
                        message += f"- {doc['title']} ({doc['link']})\n"
                    send_notification_email(to_emails, subject, message)
                except Exception as e:
                    app_logger.error(f"Failed to send notification email: {str(e)}")
                    # Continue with knowledge base storage even if email fails
                    pass
                
                kb_thread = threading.Thread(
                    target=self.store_documents_in_knowledge_base, 
                    args=(document_list,)
                )
                kb_thread.daemon = True  # Set as daemon thread, auto-end when main thread exits
                kb_thread.start()
                app_logger.info(f"Started background thread to store {len(document_list)} documents in knowledge base")
            
            # Main process can continue with other tasks without blocking
            return True
            
        except Exception as e:
            app_logger.error(f"Error fetching RSS feeds for source {source_id}: {str(e)}")
            return False

    def get_documents_by_source(self, source_id: int, limit: int = 20, offset: int = 0) -> List[Document]:
        """Get documents by source ID."""
        return self._get_by_source_id(source_id, limit, offset)

    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        return self._get_by_id(document_id)
    
    def delete_document(self, document_id: int) -> bool:
        """Delete document by ID."""
        return self._delete(document_id)

    def search_documents(self, query: str, limit: int = 20, offset: int = 0) -> List[Document]:
        """Search documents by title or description."""
        return self._search(query, limit, offset)

    def get_recent_documents(self, days: int = 7, limit: int = 20) -> List[Document]:
        """Get recent documents."""
        return self._get_recent_documents(days, limit)

    def get_document_count_by_source(self) -> Dict[str, int]:
        """Get document count by source."""
        return self._get_document_count_by_source()

    def get_top_tags(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top tags."""
        return self._get_top_tags(limit)
    
    def get_documents_with_params(self, search_params) -> Dict[str, Any]:
        """Get documents with pagination and filtering."""
        from schemas.responses import DocumentListResponse, DocumentResponse
        
        # Calculate offset
        offset = (search_params.page - 1) * search_params.size
        
        # Get documents from repository
        documents = self._get_paginated(
            page=search_params.page,
            size=search_params.size,
            search=search_params.search,
            doc_type=search_params.doc_type,
            source=search_params.source,
            start_date=search_params.start_date,
            end_date=search_params.end_date
        )
        
        # Convert to response format
        document_responses = []
        for doc in documents['items']:
            document_responses.append(DocumentResponse(
                id=doc.id,
                title=doc.title,
                link=doc.link,
                description=doc.description,
                author=doc.author,
                tags=doc.tags,
                pub_date=doc.pub_date,
                source_id=doc.source_id,
                crawled_at=doc.crawled_at
            ))
        
        return DocumentListResponse(
            items=document_responses,
            total=documents['total'],
            page=search_params.page,
            size=search_params.size,
            total_pages=documents['total_pages']
        )
    
    # Additional methods for backward compatibility
    def get_documents(self, session: Session) -> List[Document]:
        """Get all documents (backward compatibility)."""
        try:
            return self._get_all()
        except Exception as e:
            app_logger.error(f"Error getting documents: {str(e)}")
            raise
    
    def get_document_by_id(self, document_id: int, session: Session) -> Optional[Document]:
        """Get document by ID (backward compatibility)."""
        try:
            return self._get_by_id(document_id)
        except Exception as e:
            app_logger.error(f"Error getting document {document_id}: {str(e)}")
            raise
    
    def get_documents_paginated(self, page: int, size: int, session: Session) -> List[Document]:
        """Get paginated documents (backward compatibility)."""
        try:
            offset = (page - 1) * size
            return self._get_paginated(page, size)['items']
        except Exception as e:
            app_logger.error(f"Error getting paginated documents: {str(e)}")
            raise
    
    def search_documents(self, query: str, session: Session) -> List[Document]:
        """Search documents (backward compatibility)."""
        try:
            return self._search(query)
        except Exception as e:
            app_logger.error(f"Error searching documents: {str(e)}")
            raise
    
    def get_documents_by_source(self, source_id: int, session: Session) -> List[Document]:
        """Get documents by source (backward compatibility)."""
        try:
            return self._get_by_source_id(source_id)
        except Exception as e:
            app_logger.error(f"Error getting documents by source {source_id}: {str(e)}")
            raise
    
    def get_documents_by_date_range(self, start_date, end_date, session: Session) -> List[Document]:
        """Get documents by date range (backward compatibility)."""
        try:
            return self._get_by_date_range(start_date, end_date)
        except Exception as e:
            app_logger.error(f"Error getting documents by date range: {str(e)}")
            raise
    
    def get_document_statistics(self, session: Session) -> Dict[str, Any]:
        """Get document statistics (backward compatibility)."""
        try:
            return self._get_statistics()
        except Exception as e:
            app_logger.error(f"Error getting document statistics: {str(e)}")
            raise
    
    def create_document(self, document_data: Dict[str, Any], session: Session) -> Document:
        """Create document (backward compatibility)."""
        try:
            document = Document(**document_data)
            return self._create(document)
        except Exception as e:
            app_logger.error(f"Error creating document: {str(e)}")
            raise
    
    def update_document(self, document_id: int, update_data: Dict[str, Any], session: Session) -> Optional[Document]:
        """Update document (backward compatibility)."""
        try:
            return self._update(document_id, update_data)
        except Exception as e:
            app_logger.error(f"Error updating document {document_id}: {str(e)}")
            raise
    
    def delete_document(self, document_id: int, session: Session) -> bool:
        """Delete document (backward compatibility)."""
        try:
            return self._delete(document_id)
        except Exception as e:
            app_logger.error(f"Error deleting document {document_id}: {str(e)}")
            raise

    def upload_excel_documents(self, documents_data: List[Dict[str, Any]], filename: str) -> Dict[str, Any]:
        """
        Upload documents from Excel data.
        
        Args:
            documents_data: List of document dictionaries from Excel
            filename: Name of the Excel file
            
        Returns:
            Dict with upload result information
        """
        try:
            processed_count = 0
            document_list = []
            
            # Create a unique source for this Excel file
            file_source = self._create_excel_source(filename)
            
            for doc_data in documents_data:
                # Clean the text content
                clean_title = self.clean_text(doc_data.get('title', ''))
                clean_description = self.clean_text(doc_data.get('description', ''))
                
                # Create new Document instance
                # Always use the FILE type source for Excel uploads
                document = Document(
                    title=clean_title,
                    link=doc_data.get('link', ''),
                    description=clean_description,
                    tags=doc_data.get('tags', ''),
                    pub_date=doc_data.get('pub_date'),
                    author=doc_data.get('author'),
                    source_id=file_source.id
                )
                
                self.session.add(document)
                self.session.commit()
                self.session.refresh(document)
                
                processed_count += 1
                app_logger.info(f"Added document from Excel: {clean_title}")
                
                # Prepare for knowledge base storage
                document_list.append({
                    "id": document.id,
                    "title": document.title,
                    "link": document.link,
                    "description": document.description,
                    "tags": document.tags,
                    "pub_date": document.pub_date.isoformat() if document.pub_date else None,
                    "author": document.author,
                    "source_id": document.source_id
                })
            
            # Store in knowledge base in background thread
            if document_list:
                kb_thread = threading.Thread(
                    target=self.store_documents_in_knowledge_base, 
                    args=(document_list,)
                )
                kb_thread.daemon = True
                kb_thread.start()
                app_logger.info(f"Started background thread to store {len(document_list)} Excel documents in knowledge base")
            
            return {
                "success": True,
                "message": f"Successfully processed {processed_count} documents from Excel",
                "documents_processed": processed_count
            }
            
        except Exception as e:
            app_logger.error(f"Error processing Excel documents: {str(e)}")
            return {
                "success": False,
                "message": f"Error processing Excel documents: {str(e)}",
                "documents_processed": 0
            }
    
    def batch_delete_documents(self, document_ids: List[int]) -> Dict[str, Any]:
        """
        Batch delete documents by their IDs.
        
        Args:
            document_ids: List of document IDs to delete
            
        Returns:
            Dict with deletion result information
        """
        try:
            deleted_count = 0
            
            for doc_id in document_ids:
                # Find the document
                document = self.session.get(Document, doc_id)
                if document:
                    # Delete from knowledge base first (if exists)
                    try:
                        vector_store_service.delete_document(doc_id)
                        app_logger.info(f"Deleted document {doc_id} from knowledge base")
                    except Exception as e:
                        app_logger.warning(f"Failed to delete document {doc_id} from knowledge base: {str(e)}")
                    
                    # Delete from database
                    self.session.delete(document)
                    self.session.commit()
                    deleted_count += 1
                    app_logger.info(f"Deleted document with ID: {doc_id}")
                else:
                    app_logger.warning(f"Document with ID {doc_id} not found")
            
            return {
                "success": True,
                "message": f"Successfully deleted {deleted_count} documents",
                "deleted_count": deleted_count
            }
            
        except Exception as e:
            app_logger.error(f"Error batch deleting documents: {str(e)}")
            return {
                "success": False,
                "message": f"Error batch deleting documents: {str(e)}",
                "deleted_count": 0
            }
    
    # Private helper methods (formerly in DocumentRepository)
    def _get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        try:
            return self.session.get(Document, document_id)
        except Exception as e:
            app_logger.error(f"Error getting document by ID {document_id}: {str(e)}")
            raise

    def _get_by_link(self, link: str) -> Optional[Document]:
        """Get document by link."""
        try:
            statement = select(Document).where(Document.link == link)
            return self.session.exec(statement).first()
        except Exception as e:
            app_logger.error(f"Error getting document by link {link}: {str(e)}")
            raise
    
    def _get_by_source_id(self, source_id: int, skip: int = 0, limit: int = 100) -> List[Document]:
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
    
    def _get_by_date_range(self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100) -> List[Document]:
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
    
    def _search(self, query: str, skip: int = 0, limit: int = 100) -> List[Document]:
        """Search documents by title or content."""
        try:
            statement = (
                select(Document)
                .where(
                    or_(
                        Document.title.contains(query),
                        Document.content.contains(query)
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
    
    def _get_recent_documents(self, days: int = 7, limit: int = 10) -> List[Document]:
        """Get recent documents."""
        try:
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
    
    def _get_document_count_by_source(self) -> Dict[int, int]:
        """Get document count by source."""
        try:
            statement = (
                select(Document.source_id, func.count(Document.id))
                .group_by(Document.source_id)
            )
            results = self.session.exec(statement).all()
            return {source_id: count for source_id, count in results}
        except Exception as e:
            app_logger.error(f"Error getting document count by source: {str(e)}")
            raise
    
    def _get_top_tags(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top tags."""
        try:
            # This is a simplified implementation
            # In practice, you might want to implement proper tag extraction and counting
            statement = (
                select(Document.tags, func.count(Document.id))
                .where(Document.tags.isnot(None))
                .group_by(Document.tags)
                .order_by(desc(func.count(Document.id)))
                .limit(limit)
            )
            results = self.session.exec(statement).all()
            return [{"tag": tag, "count": count} for tag, count in results]
        except Exception as e:
            app_logger.error(f"Error getting top tags: {str(e)}")
            raise
    
    def _get_paginated(self, page: int, size: int, search: Optional[str] = None, 
                      doc_type: Optional[str] = None, source: Optional[str] = None,
                      start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get paginated documents with filtering."""
        try:
            skip = (page - 1) * size
            
            # Build base query
            statement = select(Document)
            count_statement = select(func.count()).select_from(Document)
            
            # Apply filters
            conditions = []
            
            # Search filter (title or description)
            if search:
                search_condition = or_(
                    Document.title.contains(search),
                    Document.description.contains(search)
                )
                conditions.append(search_condition)
            
            # Source filter
            if source:
                try:
                    source_id = int(source)
                    conditions.append(Document.source_id == source_id)
                except ValueError:
                    # If source is not a valid integer, ignore it
                    pass
            
            # Date range filter
            if start_date:
                try:
                    start_dt = datetime.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    conditions.append(Document.crawled_at >= start_dt)
                except ValueError:
                    # If date format is invalid, ignore it
                    pass
            
            if end_date:
                try:
                    end_dt = datetime.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    conditions.append(Document.crawled_at <= end_dt)
                except ValueError:
                    # If date format is invalid, ignore it
                    pass
            
            # Apply conditions to both statements
            if conditions:
                statement = statement.where(and_(*conditions))
                count_statement = count_statement.where(and_(*conditions))
            
            # Apply ordering, offset, and limit
            statement = statement.order_by(desc(Document.crawled_at)).offset(skip).limit(size)
            
            # Execute queries
            documents = list(self.session.exec(statement))
            total = self.session.exec(count_statement).one()
            
            return {
                "items": documents,
                "total": total,
                "page": page,
                "size": size,
                "total_pages": (total + size - 1) // size
            }
        except Exception as e:
            app_logger.error(f"Error getting paginated documents: {str(e)}")
            raise
    
    def _get_all(self, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get all documents."""
        try:
            statement = select(Document).order_by(desc(Document.crawled_at)).offset(skip).limit(limit)
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting all documents: {str(e)}")
            raise
    
    def _create(self, document: Document) -> Document:
        """Create a new document."""
        try:
            self.session.add(document)
            self.session.commit()
            self.session.refresh(document)
            app_logger.info(f"Created document with ID: {document.id}")
            return document
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"Error creating document: {str(e)}")
            raise
    
    def _update(self, document_id: int, update_data: Dict[str, Any]) -> Optional[Document]:
        """Update document by ID."""
        try:
            document = self.session.get(Document, document_id)
            if not document:
                return None
            
            for key, value in update_data.items():
                if hasattr(document, key):
                    setattr(document, key, value)
            
            self.session.commit()
            self.session.refresh(document)
            app_logger.info(f"Updated document with ID: {document_id}")
            return document
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"Error updating document with ID {document_id}: {str(e)}")
            raise
    
    def _delete(self, document_id: int) -> bool:
        """Delete document by ID."""
        try:
            document = self.session.get(Document, document_id)
            if not document:
                return False
            
            self.session.delete(document)
            self.session.commit()
            app_logger.info(f"Deleted document with ID: {document_id}")
            return True
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"Error deleting document with ID {document_id}: {str(e)}")
            raise
    
    def _get_statistics(self) -> Dict[str, Any]:
        """Get document statistics."""
        try:
            total_documents = self.session.exec(select(func.count()).select_from(Document)).one()
            
            # Get documents by source
            statement = (
                select(Document.source_id, func.count(Document.id))
                .group_by(Document.source_id)
            )
            by_source = dict(self.session.exec(statement).all())
            
            # Get recent documents count (last 7 days)
            cutoff_date = datetime.now() - timedelta(days=7)
            recent_count = self.session.exec(
                select(func.count()).select_from(Document).where(Document.crawled_at >= cutoff_date)
            ).one()
            
            return {
                "total_documents": total_documents,
                "documents_by_source": by_source,
                "recent_documents": recent_count
            }
        except Exception as e:
            app_logger.error(f"Error getting document statistics: {str(e)}")
            raise