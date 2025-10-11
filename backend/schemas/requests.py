"""
Request schemas for all API endpoints.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from models.source import SourceType, SourceInterval


# Source-related request schemas
class SourceCreate(BaseModel):
    """Create data source request schema."""
    name: str = Field(..., min_length=1, max_length=200, description="数据源名称")
    url: str = Field(..., min_length=1, max_length=500, description="数据源URL")
    source_type: SourceType = Field(default=SourceType.RSS, description="数据源类型")
    interval: SourceInterval = Field(default=SourceInterval.ONE_DAY, description="同步间隔")
    description: Optional[str] = Field(None, max_length=1000, description="数据源描述")
    tags: Optional[str] = Field(None, max_length=500, description="标签")
    config: Optional[Dict[str, Any]] = Field(None, description="数据源特定配置")


class SourceUpdate(BaseModel):
    """Update data source request schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[str] = Field(None, min_length=1, max_length=500)
    source_type: Optional[SourceType] = None
    interval: Optional[SourceInterval] = None
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[str] = Field(None, max_length=500)
    config: Optional[Dict[str, Any]] = None
    is_paused: Optional[bool] = None
    is_active: Optional[bool] = None


class SourceSearchParams(BaseModel):
    """Data source search parameters schema."""
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    search: Optional[str] = Field(None, max_length=200)
    source_type: Optional[SourceType] = None
    interval: Optional[SourceInterval] = None
    is_paused: Optional[bool] = None
    is_active: Optional[bool] = None
    tags: Optional[str] = Field(None, max_length=200)


# Document-related request schemas
class DocumentCreate(BaseModel):
    """Create document request schema."""
    title: str = Field(..., min_length=1, max_length=500)
    link: str = Field(..., min_length=1, max_length=1000)
    description: str = Field(..., min_length=1)
    author: Optional[str] = Field(None, max_length=200)
    tags: Optional[str] = Field(None, max_length=1000)
    pub_date: Optional[datetime] = None
    source_id: int


class DocumentUpdate(BaseModel):
    """Update document request schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    link: Optional[str] = Field(None, min_length=1, max_length=1000)
    description: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, max_length=200)
    tags: Optional[str] = Field(None, max_length=1000)
    pub_date: Optional[datetime] = None


# Analytics-related request schemas
class ClusterAnalysisRequest(BaseModel):
    """Cluster analysis request schema."""
    force_refresh: bool = False
    max_clusters: Optional[int] = Field(None, ge=2, le=50)


# Assistant-related request schemas
class AssistantQueryRequest(BaseModel):
    """Assistant query request schema."""
    query: str = Field(..., min_length=1, max_length=1000)
    options: Optional[dict] = Field(default_factory=dict)


class KnowledgeBaseStoreRequest(BaseModel):
    """Knowledge base store request schema."""
    action: str = Field(..., pattern="^(store|retrieve|cluster_analysis)$")
    documents: Optional[List[dict]] = None
    query: Optional[str] = None
    k: int = Field(3, ge=1, le=20)
    rerank: bool = False


# Auth-related request schemas
class UserLoginRequest(BaseModel):
    """User login request schema."""
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=100)


class UserRegisterRequest(BaseModel):
    """User registration request schema."""
    username: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1, max_length=100)
    full_name: Optional[str] = Field(None, max_length=200)


class UserUpdateRequest(BaseModel):
    """User update request schema."""
    email: Optional[str] = Field(None, min_length=1, max_length=200)
    full_name: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


# Scheduler-related request schemas
class SchedulerTriggerRequest(BaseModel):
    """Scheduler trigger request schema."""
    source_id: Optional[int] = None
    force: bool = False


# Source configuration schemas
class SourceConfigSchema(BaseModel):
    """Data source configuration schema."""
    # RSS配置
    rss_encoding: Optional[str] = Field(None, description="RSS编码")
    rss_timeout: Optional[int] = Field(None, ge=1, le=300, description="RSS超时时间(秒)")
    
    # Web爬取配置
    web_headers: Optional[Dict[str, str]] = Field(None, description="Web请求头")
    web_timeout: Optional[int] = Field(None, ge=1, le=300, description="Web超时时间(秒)")
    web_selector: Optional[str] = Field(None, description="Web内容选择器")
    web_depth: Optional[int] = Field(None, ge=1, le=5, description="爬取深度")
    
    # 通用配置
    max_documents: Optional[int] = Field(None, ge=1, le=10000, description="最大文档数")
    content_selector: Optional[str] = Field(None, description="内容选择器")
    title_selector: Optional[str] = Field(None, description="标题选择器")
    date_selector: Optional[str] = Field(None, description="日期选择器")
    author_selector: Optional[str] = Field(None, description="作者选择器")
    
    @field_validator('web_headers')
    @classmethod
    def validate_web_headers(cls, v):
        if v is not None:
            for key, value in v.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError('Web headers must be string key-value pairs')
        return v


# Document Search Parameters
class DocumentSearchParams(BaseModel):
    """Schema for document search parameters."""
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    search: Optional[str] = Field(None, max_length=200)
    doc_type: Optional[str] = Field(None, max_length=100)
    source: Optional[str] = Field(None, max_length=200)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
