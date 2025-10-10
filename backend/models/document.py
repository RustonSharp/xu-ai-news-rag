from typing import Optional, List
from sqlmodel import SQLModel, Field
import datetime

class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: int = Field(default=None, primary_key=True)
    title: str
    link: str
    description: str
    pub_date: Optional[datetime.datetime] = None
    author: Optional[str] = None
    tags: str = Field(default="")
    source_id: int = Field(foreign_key="sources.id", description="统一数据源ID")
    crawled_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

