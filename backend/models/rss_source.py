from sqlmodel import SQLModel, Field
from models.enums.interval import IntervalEnum


class RssSource(SQLModel, table=True):
    __tablename__ = "rss_sources"
    
    id: int = Field(default=None, primary_key=True)
    name: str
    url: str
    interval: IntervalEnum = Field(default=IntervalEnum.MINUTE)
