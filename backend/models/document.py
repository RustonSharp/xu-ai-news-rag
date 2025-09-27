from typing import Optional
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
    rss_source_id: int = Field(foreign_key="rss_sources.id")
    crawled_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
