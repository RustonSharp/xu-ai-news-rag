"""
Analytics service for data analysis operations.
"""
from typing import Dict, Any, List, Optional
from sqlmodel import Session
from repositories.analysis_repository import AnalysisRepository
from repositories.document_repository import DocumentRepository
from repositories.source_repository import SourceRepository
from services.analytics.clustering_service import clustering_service
from schemas.analytics_schema import (
    ClusterAnalysisResponse, ClusterAnalysisRequest, 
    AnalyticsStatsResponse, DocumentStatsResponse
)
from utils.logging_config import app_logger
import json


class AnalyticsService:
    """Service for analytics operations."""
    
    def __init__(self, session: Session):
        self.session = session
        self.analysis_repo = AnalysisRepository(session)
        self.document_repo = DocumentRepository(session)
        self.source_repo = SourceRepository(session)
    
    def perform_cluster_analysis(self, request: ClusterAnalysisRequest) -> ClusterAnalysisResponse:
        """Perform cluster analysis on documents."""
        try:
            app_logger.info("Starting cluster analysis")
            
            # Check if we should use cached results
            if not request.force_refresh:
                latest_analysis = self.analysis_repo.get_latest_analysis()
                if latest_analysis:
                    app_logger.info("Using cached cluster analysis results")
                    return self._format_cluster_analysis_response(latest_analysis)
            
            # Perform new clustering analysis
            analysis_result = clustering_service.perform_clustering_analysis()
            
            if "error" in analysis_result:
                return ClusterAnalysisResponse(
                    clusters=[],
                    total_documents=0,
                    total_clusters=0,
                    silhouette_score=0.0,
                    clustering_method="error",
                    analysis_date=""
                )
            
            # Save analysis to database
            analysis_record = self.analysis_repo.create_cluster_analysis(
                method=analysis_result.get("clustering_method", "unknown"),
                silhouette_score=analysis_result.get("silhouette_score", 0.0),
                total_documents=analysis_result.get("total_documents", 0),
                total_clusters=analysis_result.get("total_clusters", 0),
                report_json=json.dumps(analysis_result, ensure_ascii=False)
            )
            
            app_logger.info("Cluster analysis completed and saved")
            return self._format_cluster_analysis_response(analysis_record)
            
        except Exception as e:
            app_logger.error(f"Error performing cluster analysis: {str(e)}")
            return ClusterAnalysisResponse(
                clusters=[],
                total_documents=0,
                total_clusters=0,
                silhouette_score=0.0,
                clustering_method="error",
                analysis_date=""
            )
    
    def get_latest_cluster_analysis(self) -> ClusterAnalysisResponse:
        """Get the latest cluster analysis results."""
        try:
            latest_analysis = self.analysis_repo.get_latest_analysis()
            if not latest_analysis:
                return ClusterAnalysisResponse(
                    clusters=[],
                    total_documents=0,
                    total_clusters=0,
                    silhouette_score=0.0,
                    clustering_method="none",
                    analysis_date=""
                )
            
            return self._format_cluster_analysis_response(latest_analysis)
        except Exception as e:
            app_logger.error(f"Error getting latest cluster analysis: {str(e)}")
            return ClusterAnalysisResponse(
                clusters=[],
                total_documents=0,
                total_clusters=0,
                silhouette_score=0.0,
                clustering_method="error",
                analysis_date=""
            )
    
    def get_analytics_stats(self) -> AnalyticsStatsResponse:
        """Get overall analytics statistics."""
        try:
            # Get basic counts
            total_documents = self.document_repo.count()
            total_sources = self.source_repo.count()
            
            # Get latest analysis info
            latest_analysis = self.analysis_repo.get_latest_analysis()
            last_analysis_date = latest_analysis.created_at.isoformat() if latest_analysis else None
            total_clusters = latest_analysis.total_clusters if latest_analysis else 0
            
            # Get knowledge base size (simplified)
            from services.knowledge_base.vector_store_service import vector_store_service
            kb_stats = vector_store_service.get_stats()
            knowledge_base_size = kb_stats.get("total_documents", 0)
            
            return AnalyticsStatsResponse(
                total_documents=total_documents,
                total_sources=total_sources,
                total_clusters=total_clusters,
                last_analysis_date=last_analysis_date,
                knowledge_base_size=knowledge_base_size
            )
        except Exception as e:
            app_logger.error(f"Error getting analytics stats: {str(e)}")
            return AnalyticsStatsResponse(
                total_documents=0,
                total_sources=0,
                total_clusters=0,
                last_analysis_date=None,
                knowledge_base_size=0
            )
    
    def get_document_stats(self) -> DocumentStatsResponse:
        """Get document statistics."""
        try:
            # Get total documents
            total_documents = self.document_repo.count()
            
            # Get documents by source
            documents_by_source = self.document_repo.get_document_count_by_source()
            
            # Get recent documents
            recent_documents = self.document_repo.get_recent_documents(days=7, limit=10)
            recent_docs_data = []
            for doc in recent_documents:
                recent_docs_data.append({
                    "id": doc.id,
                    "title": doc.title,
                    "crawled_at": doc.crawled_at.isoformat(),
                    "rss_source_id": doc.rss_source_id
                })
            
            # Get top tags
            top_tags = self.document_repo.get_top_tags(limit=20)
            
            # Get documents by date (last 30 days)
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            documents_by_date = {}
            
            # This is a simplified implementation
            # In practice, you might want to implement proper date grouping
            for i in range(30):
                date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                documents_by_date[date] = 0  # Placeholder
            
            return DocumentStatsResponse(
                total_documents=total_documents,
                documents_by_source=documents_by_source,
                documents_by_date=documents_by_date,
                top_tags=top_tags,
                recent_documents=recent_docs_data
            )
        except Exception as e:
            app_logger.error(f"Error getting document stats: {str(e)}")
            return DocumentStatsResponse(
                total_documents=0,
                documents_by_source={},
                documents_by_date={},
                top_tags=[],
                recent_documents=[]
            )
    
    def get_analysis_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get analysis history."""
        try:
            analyses = self.analysis_repo.get_recent_analyses(days=days, limit=50)
            
            history = []
            for analysis in analyses:
                history.append({
                    "id": analysis.id,
                    "method": analysis.method,
                    "silhouette_score": analysis.silhouette_score,
                    "total_documents": analysis.total_documents,
                    "total_clusters": analysis.total_clusters,
                    "created_at": analysis.created_at.isoformat()
                })
            
            return history
        except Exception as e:
            app_logger.error(f"Error getting analysis history: {str(e)}")
            return []
    
    def _format_cluster_analysis_response(self, analysis_record) -> ClusterAnalysisResponse:
        """Format cluster analysis response from database record."""
        try:
            # Parse the stored JSON report
            report_data = json.loads(analysis_record.report_json)
            
            # Extract cluster information
            clusters = []
            for cluster_data in report_data.get("top_clusters", []):
                clusters.append({
                    "cluster_id": cluster_data.get("cluster_id", 0),
                    "cluster_label": cluster_data.get("cluster_label", ""),
                    "document_count": cluster_data.get("document_count", 0),
                    "percentage": cluster_data.get("percentage", 0.0),
                    "keywords": cluster_data.get("keywords", [])
                })
            
            return ClusterAnalysisResponse(
                clusters=clusters,
                total_documents=analysis_record.total_documents,
                total_clusters=analysis_record.total_clusters,
                silhouette_score=analysis_record.silhouette_score,
                clustering_method=analysis_record.method,
                analysis_date=analysis_record.created_at.isoformat()
            )
        except Exception as e:
            app_logger.error(f"Error formatting cluster analysis response: {str(e)}")
            return ClusterAnalysisResponse(
                clusters=[],
                total_documents=0,
                total_clusters=0,
                silhouette_score=0.0,
                clustering_method="error",
                analysis_date=""
            )
