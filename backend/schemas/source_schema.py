"""
统一数据源相关的Pydantic schemas，支持RSS、Web爬取等多种类型。
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from models.source import SourceType, SourceInterval


class SourceBase(BaseModel):
    """基础数据源schema"""
    name: str = Field(..., min_length=1, max_length=200, description="数据源名称")
    url: str = Field(..., min_length=1, max_length=500, description="数据源URL")
    source_type: SourceType = Field(default=SourceType.RSS, description="数据源类型")
    interval: SourceInterval = Field(default=SourceInterval.ONE_DAY, description="同步间隔")
    description: Optional[str] = Field(None, max_length=1000, description="数据源描述")
    tags: Optional[str] = Field(None, max_length=500, description="标签")
    config: Optional[Dict[str, Any]] = Field(None, description="数据源特定配置")


class SourceCreate(SourceBase):
    """创建数据源的schema"""
    pass


class SourceUpdate(BaseModel):
    """更新数据源的schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[str] = Field(None, min_length=1, max_length=500)
    source_type: Optional[SourceType] = None
    interval: Optional[SourceInterval] = None
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[str] = Field(None, max_length=500)
    config: Optional[Dict[str, Any]] = None
    is_paused: Optional[bool] = None
    is_active: Optional[bool] = None


class SourceResponse(SourceBase):
    """数据源响应schema"""
    id: int
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
    """数据源列表响应schema"""
    sources: List[SourceResponse]
    total: int
    page: int
    size: int
    total_pages: int


class SourceStatsResponse(BaseModel):
    """数据源统计响应schema"""
    total_sources: int
    sources_by_type: Dict[str, int]
    sources_by_interval: Dict[str, int]
    active_sources: int
    paused_sources: int
    sources_due_for_sync: int
    total_documents: int


class SourceTriggerResponse(BaseModel):
    """数据源触发响应schema"""
    message: str
    success: bool
    documents_fetched: int = 0
    source_type: str
    sync_duration: Optional[float] = None


class SourceSearchParams(BaseModel):
    """数据源搜索参数schema"""
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    search: Optional[str] = Field(None, max_length=200)
    source_type: Optional[SourceType] = None
    interval: Optional[SourceInterval] = None
    is_paused: Optional[bool] = None
    is_active: Optional[bool] = None
    tags: Optional[str] = Field(None, max_length=200)


class SourceConfigSchema(BaseModel):
    """数据源配置schema"""
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
