from sqlmodel import SQLModel, Field
from enum import Enum
from typing import Optional
import datetime


class SourceType(str, Enum):
    """数据源类型枚举"""
    RSS = "rss"
    WEB = "web"
    FILE = "file"


class SourceInterval(str, Enum):
    """数据源同步间隔枚举"""
    SIX_HOUR = "SIX_HOUR"
    TWELVE_HOUR = "TWELVE_HOUR"
    ONE_DAY = "ONE_DAY"
    THREE_DAY = "THREE_DAY"
    WEEKLY = "WEEKLY"


class Source(SQLModel, table=True):
    """统一的数据源模型，支持RSS、Web爬取等多种类型"""
    __tablename__ = "sources"
    
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=200, description="数据源名称")
    url: str = Field(max_length=500, description="数据源URL")
    source_type: SourceType = Field(default=SourceType.RSS, description="数据源类型")
    interval: SourceInterval = Field(default=SourceInterval.ONE_DAY, description="同步间隔")
    is_paused: bool = Field(default=False, description="是否暂停")
    last_sync: Optional[datetime.datetime] = Field(default=None, nullable=True, description="最后同步时间")
    next_sync: Optional[datetime.datetime] = Field(default=None, nullable=True, description="下次同步时间")
    
    # 扩展配置字段（JSON格式存储）
    config: Optional[str] = Field(default=None, nullable=True, description="数据源特定配置")
    
    # 元数据字段
    description: Optional[str] = Field(default=None, nullable=True, max_length=1000, description="数据源描述")
    tags: Optional[str] = Field(default=None, nullable=True, max_length=500, description="标签")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="创建时间")
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="更新时间")
    
    # 统计字段
    total_documents: int = Field(default=0, description="总文档数")
    last_document_count: int = Field(default=0, description="上次同步文档数")
    
    # 状态字段
    is_active: bool = Field(default=True, description="是否激活")
    sync_errors: int = Field(default=0, description="同步错误次数")
    last_error: Optional[str] = Field(default=None, nullable=True, description="最后错误信息")
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Source(id={self.id}, name='{self.name}', type='{self.source_type}')"
    
    def __eq__(self, other) -> bool:
        """相等性比较"""
        if not isinstance(other, Source):
            return False
        return self.id == other.id and self.name == other.name