"""
Analysis repository for database operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select, func, desc
from models.analysis import Analysis
from repositories.base_repository import BaseRepository
from utils.logging_config import app_logger


class AnalysisRepository(BaseRepository[Analysis]):
    """Repository for analysis operations."""
    
    def __init__(self, session: Session):
        super().__init__(session, Analysis)
    
    def get_latest_analysis(self) -> Optional[Analysis]:
        """Get the latest analysis by creation date."""
        try:
            statement = select(Analysis).order_by(desc(Analysis.created_at)).limit(1)
            return self.session.exec(statement).first()
        except Exception as e:
            app_logger.error(f"Error getting latest analysis: {str(e)}")
            raise
    
    def get_analyses_by_method(self, method: str, skip: int = 0, limit: int = 100) -> List[Analysis]:
        """Get analyses by method type."""
        try:
            statement = (
                select(Analysis)
                .where(Analysis.method == method)
                .order_by(desc(Analysis.created_at))
                .offset(skip)
                .limit(limit)
            )
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting analyses by method {method}: {str(e)}")
            raise
    
    def get_analyses_by_date_range(self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100) -> List[Analysis]:
        """Get analyses within a date range."""
        try:
            statement = (
                select(Analysis)
                .where(
                    Analysis.created_at >= start_date,
                    Analysis.created_at <= end_date
                )
                .order_by(desc(Analysis.created_at))
                .offset(skip)
                .limit(limit)
            )
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting analyses by date range: {str(e)}")
            raise
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics."""
        try:
            total_analyses = self.count()
            
            # Get analyses by method
            statement = (
                select(Analysis.method, func.count(Analysis.id))
                .group_by(Analysis.method)
            )
            method_counts = dict(self.session.exec(statement).all())
            
            # Get latest analysis info
            latest = self.get_latest_analysis()
            latest_date = latest.created_at.isoformat() if latest else None
            
            # Get average silhouette score
            statement = select(func.avg(Analysis.silhouette_score))
            avg_silhouette = self.session.exec(statement).one()
            
            return {
                "total_analyses": total_analyses,
                "method_distribution": method_counts,
                "latest_analysis_date": latest_date,
                "average_silhouette_score": float(avg_silhouette) if avg_silhouette else None
            }
        except Exception as e:
            app_logger.error(f"Error getting analysis statistics: {str(e)}")
            raise
    
    def get_recent_analyses(self, days: int = 30, limit: int = 10) -> List[Analysis]:
        """Get recent analyses within specified days."""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            statement = (
                select(Analysis)
                .where(Analysis.created_at >= cutoff_date)
                .order_by(desc(Analysis.created_at))
                .limit(limit)
            )
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting recent analyses: {str(e)}")
            raise
    
    def create_cluster_analysis(self, method: str, silhouette_score: float, 
                              total_documents: int, total_clusters: int, 
                              report_json: str) -> Analysis:
        """Create a new cluster analysis record."""
        try:
            analysis = Analysis(
                method=method,
                silhouette_score=silhouette_score,
                total_documents=total_documents,
                total_clusters=total_clusters,
                report_json=report_json
            )
            return self.create(analysis)
        except Exception as e:
            app_logger.error(f"Error creating cluster analysis: {str(e)}")
            raise
    
    def get_analysis_trends(self, days: int = 90) -> List[Dict[str, Any]]:
        """Get analysis trends over time."""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            statement = (
                select(
                    func.date(Analysis.created_at).label('date'),
                    func.count(Analysis.id).label('count'),
                    func.avg(Analysis.silhouette_score).label('avg_silhouette')
                )
                .where(Analysis.created_at >= cutoff_date)
                .group_by(func.date(Analysis.created_at))
                .order_by(func.date(Analysis.created_at))
            )
            
            results = self.session.exec(statement).all()
            trends = []
            
            for result in results:
                trends.append({
                    "date": result.date.isoformat(),
                    "analysis_count": result.count,
                    "average_silhouette_score": float(result.avg_silhouette) if result.avg_silhouette else None
                })
            
            return trends
        except Exception as e:
            app_logger.error(f"Error getting analysis trends: {str(e)}")
            raise
