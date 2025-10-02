from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class Analysis(SQLModel, table=True):
    __tablename__ = "analyses"

    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now, index=True)
    method: str = Field(default="unknown")
    silhouette_score: Optional[float] = Field(default=None)
    total_documents: Optional[int] = Field(default=None)
    total_clusters: Optional[int] = Field(default=None)
    # 存储完整报告的JSON字符串
    report_json: str


