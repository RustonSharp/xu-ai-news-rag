"""
Response schemas for all API endpoints.
"""
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
from models.source import SourceType, SourceInterval


# Source-related response schemas
class SourceResponse(BaseModel):
    """Data source response schema."""
    id: int
    name: str
    url: str
    source_type: SourceType
    interval: SourceInterval
    description: Optional[str] = None
    tags: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_paused: bool
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    total_documents: int = 0
    last_document_count: int = 0
    is_active: bool = True
    sync_errors: int = 0
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SourceListResponse(BaseModel):
    """Data source list response schema."""
    sources: List[SourceResponse]
    total: int
    page: int
    size: int
    total_pages: int


class SourceStatsResponse(BaseModel):
    """Data source statistics response schema."""
    total_sources: int
    sources_by_type: Dict[str, int]
    sources_by_interval: Dict[str, int]
    active_sources: int
    paused_sources: int
    sources_due_for_sync: int
    total_documents: int


class SourceTriggerResponse(BaseModel):
    """Data source trigger response schema."""
    message: str
    success: bool
    documents_fetched: int = 0
    source_type: str
    sync_duration: Optional[float] = None


# Document-related response schemas
class DocumentResponse(BaseModel):
    """Document response schema."""
    id: int
    title: str
    link: str
    description: str
    author: Optional[str] = None
    tags: Optional[str] = None
    pub_date: Optional[datetime] = None
    source_id: int
    crawled_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Document list response schema."""
    items: List[DocumentResponse]
    total: int
    page: int
    size: int
    total_pages: int


class DocumentStatsResponse(BaseModel):
    """Document statistics response schema."""
    total_documents: int
    documents_by_source: Dict[int, int]
    documents_by_date: Dict[str, int]
    top_tags: List[Dict[str, Any]]
    recent_documents: List[Dict[str, Any]]


# Analytics-related response schemas
class ClusterInfo(BaseModel):
    """Cluster information schema."""
    cluster_id: int
    cluster_label: str
    document_count: int
    percentage: float
    keywords: List[str] = []


class ClusterAnalysisResponse(BaseModel):
    """Cluster analysis response schema."""
    clusters: List[ClusterInfo]
    total_documents: int
    total_clusters: int
    silhouette_score: float
    clustering_method: str
    analysis_date: str


class AnalyticsStatsResponse(BaseModel):
    """Analytics statistics response schema."""
    total_documents: int
    total_sources: int
    total_clusters: int
    last_analysis_date: Optional[str] = None
    knowledge_base_size: int = 0


# Assistant-related response schemas
class SearchResult(BaseModel):
    """Search result schema."""
    id: str
    title: str
    content: str
    url: str = ""
    score: float = 0.0
    type: str = "document"
    source: str = "知识库"
    relevance: float = 0.0
    timestamp: str = ""


class AssistantQueryResponse(BaseModel):
    """Assistant query response schema."""
    query: str
    response: str
    answer: Union[str, dict]
    sources: List[SearchResult] = []
    raw_answer: Optional[Any] = None
    origin: str = "knowledge_base"
    status: str = "success"


class AssistantHealthResponse(BaseModel):
    """Assistant health check response schema."""
    status: str
    message: Optional[str] = None
    error: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    """Knowledge base response schema."""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


# Auth-related response schemas
class UserResponse(BaseModel):
    """User response schema."""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response schema."""
    access_token: str
    token_type: str
    user: UserResponse


class TokenRefreshResponse(BaseModel):
    """Token refresh response schema."""
    access_token: str
    token_type: str


# Scheduler-related response schemas
class SchedulerStatusResponse(BaseModel):
    """Scheduler status response schema."""
    is_running: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    total_sources: int
    active_sources: int
    sources_due_for_sync: int


class SchedulerTriggerResponse(BaseModel):
    """Scheduler trigger response schema."""
    success: bool
    message: str
    sources_processed: int = 0
    documents_fetched: int = 0
    errors: List[str] = []


# Common response schemas
class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseModel):
    """Success response schema."""
    success: bool
    message: str
    data: Optional[Any] = None


class PaginationResponse(BaseModel):
    """Pagination response schema."""
    page: int
    size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response."""
    message: str
    documents_processed: int
    success: bool
