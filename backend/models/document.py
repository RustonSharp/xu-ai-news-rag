from typing import Optional
from sqlmodel import SQLModel, Field
import datetime

class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: int = Field(default=None, primary_key=True)
    title: str
    author: Optional[str] = None
    content: str
    source: str
    url: str
    crawled_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
