"""
Assistant-related Pydantic schemas for request/response validation.
"""
from typing import Optional, List, Any, Union
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Schema for search result."""
    id: str
    title: str
    content: str
    url: str = ""
    score: float = 0.0
    type: str = "document"
    source: str = "知识库"
    relevance: float = 0.0
    timestamp: str = ""


class AssistantQueryRequest(BaseModel):
    """Schema for assistant query request."""
    query: str = Field(..., min_length=1, max_length=1000)
    options: Optional[dict] = Field(default_factory=dict)


class AssistantQueryResponse(BaseModel):
    """Schema for assistant query response."""
    query: str
    response: str
    answer: Union[str, dict]
    sources: List[SearchResult] = []
    raw_answer: Optional[Any] = None
    origin: str = "knowledge_base"
    status: str = "success"


class AssistantHealthResponse(BaseModel):
    """Schema for assistant health check response."""
    status: str
    message: Optional[str] = None
    error: Optional[str] = None


class KnowledgeBaseStoreRequest(BaseModel):
    """Schema for knowledge base store request."""
    action: str = Field(..., pattern="^(store|retrieve|cluster_analysis)$")
    documents: Optional[List[dict]] = None
    query: Optional[str] = None
    k: int = Field(3, ge=1, le=20)
    rerank: bool = True


class KnowledgeBaseResponse(BaseModel):
    """Schema for knowledge base response."""
    result: Any
    success: bool
    message: Optional[str] = None
