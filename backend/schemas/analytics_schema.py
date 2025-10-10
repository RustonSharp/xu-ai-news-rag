"""
Analytics-related Pydantic schemas for request/response validation.
"""
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class ClusterInfo(BaseModel):
    """Schema for cluster information."""
    cluster_id: int
    cluster_label: str
    document_count: int
    percentage: float
    keywords: List[str] = []


class ClusterAnalysisResponse(BaseModel):
    """Schema for cluster analysis response."""
    clusters: List[ClusterInfo]
    total_documents: int
    total_clusters: int
    silhouette_score: float
    clustering_method: str
    analysis_date: str


class ClusterAnalysisRequest(BaseModel):
    """Schema for cluster analysis request."""
    force_refresh: bool = False
    max_clusters: Optional[int] = Field(None, ge=2, le=50)


class AnalyticsStatsResponse(BaseModel):
    """Schema for analytics stats response."""
    total_documents: int
    total_sources: int
    total_clusters: int
    last_analysis_date: Optional[str] = None
    knowledge_base_size: int = 0


class DocumentStatsResponse(BaseModel):
    """Schema for document statistics response."""
    total_documents: int
    documents_by_source: dict[str, int]
    documents_by_date: dict[str, int]
    top_tags: List[dict[str, Any]]
    recent_documents: List[dict[str, Any]]
