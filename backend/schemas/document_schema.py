"""
Document-related Pydantic schemas for request/response validation.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base document schema."""
    title: str = Field(..., min_length=1, max_length=500)
    link: str = Field(..., min_length=1, max_length=1000)
    description: str = Field(..., min_length=1)
    author: Optional[str] = Field(None, max_length=200)
    tags: Optional[str] = Field(None, max_length=1000)
    pub_date: Optional[datetime] = None
    source_id: int


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    pass


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    link: Optional[str] = Field(None, min_length=1, max_length=1000)
    description: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, max_length=200)
    tags: Optional[str] = Field(None, max_length=1000)
    pub_date: Optional[datetime] = None


class DocumentResponse(DocumentBase):
    """Schema for document response."""
    id: int
    crawled_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for paginated document list response."""
    items: List[DocumentResponse]
    total: int
    page: int
    size: int
    total_pages: int


class DocumentSearchParams(BaseModel):
    """Schema for document search parameters."""
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    search: Optional[str] = Field(None, max_length=200)
    doc_type: Optional[str] = Field(None, max_length=100)
    source: Optional[str] = Field(None, max_length=200)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response."""
    message: str
    documents_processed: int
    success: bool
