"""
Analytics API for data analysis operations.
"""
from flask import Blueprint, request, jsonify
from core.dependencies import get_db_session_sync
from services.analytics_service import AnalyticsService
from schemas.analytics_schema import ClusterAnalysisRequest
from utils.logging_config import app_logger

# 创建蓝图
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

def get_analytics_service():
    """获取分析服务实例"""
    session = get_db_session_sync()
    return AnalyticsService(session)

@analytics_bp.route('/', methods=['GET'])
def get_analytics():
    """获取分析数据"""
    try:
        analytics_service = get_analytics_service()
        result = analytics_service.get_latest_cluster_analysis()
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        app_logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@analytics_bp.route('/cluster', methods=['POST'])
def perform_cluster_analysis():
    """执行聚类分析"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        request_data = ClusterAnalysisRequest(**data)
        analytics_service = get_analytics_service()
        result = analytics_service.perform_cluster_analysis(request_data)
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        app_logger.error(f"Error performing cluster analysis: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
