"""
Document service for document fetching and knowledge base operations.
"""
import threading
import datetime
import time
import re
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from bs4 import BeautifulSoup
from models.source import Source
from models.document import Document
from repositories.document_repository import DocumentRepository
from services.knowledge_base.vector_store_service import vector_store_service
from utils.logging_config import app_logger
from utils.email_sender import send_notification_email
import os


class DocumentService:
    """Service for document operations."""
    
    def __init__(self, session: Session):
        self.session = session
        self.document_repo = DocumentRepository(session)
    
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
                            rss_source_id=source_id
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
                            "author": document.author
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
        return self.document_repo.get_by_source_id(source_id, limit, offset)

    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        return self.document_repo.get_by_id(document_id)
    
    def delete_document(self, document_id: int) -> bool:
        """Delete document by ID."""
        return self.document_repo.delete(document_id)

    def search_documents(self, query: str, limit: int = 20, offset: int = 0) -> List[Document]:
        """Search documents by title or description."""
        return self.document_repo.search(query, limit, offset)

    def get_recent_documents(self, days: int = 7, limit: int = 20) -> List[Document]:
        """Get recent documents."""
        return self.document_repo.get_recent_documents(days, limit)

    def get_document_count_by_source(self) -> Dict[str, int]:
        """Get document count by source."""
        return self.document_repo.get_document_count_by_source()

    def get_top_tags(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top tags."""
        return self.document_repo.get_top_tags(limit)
    
    def get_documents(self, search_params) -> Dict[str, Any]:
        """Get documents with pagination and filtering."""
        from schemas.document_schema import DocumentListResponse, DocumentResponse
        
        # Calculate offset
        offset = (search_params.page - 1) * search_params.size
        
        # Get documents from repository
        documents = self.document_repo.get_paginated(
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
                rss_source_id=doc.rss_source_id,
                crawled_at=doc.crawled_at
            ))
        
        return DocumentListResponse(
            items=document_responses,
            total=documents['total'],
            page=search_params.page,
            size=search_params.size,
            total_pages=documents['total_pages']
        )