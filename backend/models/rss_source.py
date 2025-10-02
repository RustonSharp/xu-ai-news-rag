from sqlmodel import SQLModel, Field
import datetime


class RssSource(SQLModel, table=True):
    __tablename__ = "rss_sources"
    
    id: int = Field(default=None, primary_key=True)
    name: str
    url: str
    interval: str = Field(default="ONE_DAY")
    is_paused: bool = Field(default=False)
    last_sync: datetime.datetime = Field(default=None)
    next_sync: datetime.datetime = Field(default=None)
