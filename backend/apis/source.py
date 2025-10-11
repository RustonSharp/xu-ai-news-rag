"""
统一数据源API，支持RSS、Web爬取等多种类型的数据源管理。
"""
from flask import Blueprint, request, jsonify
from sqlmodel import Session
from core.dependencies import get_db_session_sync
from services.source_service import SourceService
from schemas.requests import (
    SourceCreate, SourceUpdate, SourceSearchParams
)
from schemas.responses import (
    SourceTriggerResponse
)
from utils.logging_config import app_logger
from services.scheduler_service import scheduler_service

# 创建蓝图
source_bp = Blueprint('source', __name__, url_prefix='/api/sources')

def get_source_service():
    """获取数据源服务实例"""
    session = get_db_session_sync()
    return SourceService(session)

# 获取所有数据源
@source_bp.route('', methods=['GET'])
def get_sources():
    try:
        app_logger.info("GET /api/sources - Request received")
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 20, type=int)
        search = request.args.get('search', '', type=str)
        source_type = request.args.get('type', '', type=str)
        interval = request.args.get('interval', '', type=str)
        is_paused = request.args.get('is_paused', None, type=bool)
        is_active = request.args.get('is_active', None, type=bool)
        tags = request.args.get('tags', '', type=str)
        
        # 创建搜索参数
        search_params = SourceSearchParams(
            page=page,
            size=size,
            search=search if search else None,
            source_type=source_type if source_type else None,
            interval=interval if interval else None,
            is_paused=is_paused,
            is_active=is_active,
            tags=tags if tags else None
        )
        
        # 获取数据源服务并查询数据源
        source_service = get_source_service()
        result = source_service.get_sources(search_params)
        
        # 转换为前端期望的格式
        sources_data = []
        for source in result.sources:
            sources_data.append({
                "id": source.id,
                "name": source.name,
                "url": source.url,
                "source_type": source.source_type,
                "interval": source.interval,
                "is_paused": source.is_paused,
                "is_active": source.is_active,
                "last_sync": source.last_sync.isoformat() if source.last_sync else None,
                "next_sync": source.next_sync.isoformat() if source.next_sync else None,
                "document_count": source.total_documents,
                "last_document_count": source.last_document_count,
                "sync_errors": source.sync_errors,
                "last_error": source.last_error,
                "description": source.description,
                "tags": source.tags,
                "created_at": source.created_at.isoformat(),
                "updated_at": source.updated_at.isoformat()
            })
        
        return jsonify({
            "sources": sources_data,
            "total": result.total,
            "page": result.page,
            "size": result.size,
            "total_pages": result.total_pages
        })
    except Exception as e:
        app_logger.error(f"Error getting sources: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 获取单个数据源
@source_bp.route('/<int:source_id>', methods=['GET'])
def get_source(source_id):
    try:
        app_logger.info(f"GET /api/sources/{source_id} - Request received")
        
        # 获取数据源服务并查询数据源
        source_service = get_source_service()
        source = source_service.get_source(source_id)
        
        if not source:
            return jsonify({"error": "数据源不存在"}), 404
        
        return jsonify({
            "id": source.id,
            "name": source.name,
            "url": source.url,
            "source_type": source.source_type,
            "interval": source.interval,
            "is_paused": source.is_paused,
            "is_active": source.is_active,
            "last_sync": source.last_sync.isoformat() if source.last_sync else None,
            "next_sync": source.next_sync.isoformat() if source.next_sync else None,
            "document_count": source.total_documents,
            "last_document_count": source.last_document_count,
            "sync_errors": source.sync_errors,
            "last_error": source.last_error,
            "description": source.description,
            "tags": source.tags,
            "config": source.config,
            "created_at": source.created_at.isoformat(),
            "updated_at": source.updated_at.isoformat()
        })
    except Exception as e:
        app_logger.error(f"Error getting source {source_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 创建新的数据源
@source_bp.route('', methods=['POST'])
def create_source():
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ['name', 'url', 'source_type']):
            return jsonify({"error": "缺少必需字段: name, url, source_type"}), 400
        
        # 创建数据源请求对象
        source_data = SourceCreate(
            name=data['name'],
            url=data['url'],
            source_type=data['source_type'],
            interval=data.get('interval', 'ONE_DAY'),
            description=data.get('description'),
            tags=data.get('tags'),
            config=data.get('config')
        )
        
        # 获取数据源服务并创建数据源
        source_service = get_source_service()
        source = source_service.create_source(source_data)
        
        # 重启调度器以包含新添加的数据源
        from config.settings import settings
        if scheduler_service.running and settings.AUTO_START_SCHEDULER:
            app_logger.info("Restarting scheduler to include new source")
            scheduler_service.stop()
            import time
            time.sleep(1)
            scheduler_service.start()
        
        return jsonify({
            "id": source.id,
            "name": source.name,
            "url": source.url,
            "source_type": source.source_type,
            "interval": source.interval
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app_logger.error(f"Error creating source: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 更新数据源
@source_bp.route('/<int:source_id>', methods=['PUT'])
def update_source(source_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "未提供数据"}), 400
        
        # 创建更新数据对象
        update_data = SourceUpdate(
            name=data.get('name'),
            url=data.get('url'),
            source_type=data.get('source_type'),
            interval=data.get('interval'),
            description=data.get('description'),
            tags=data.get('tags'),
            config=data.get('config'),
            is_paused=data.get('is_paused'),
            is_active=data.get('is_active')
        )
        
        # 获取数据源服务并更新数据源
        source_service = get_source_service()
        source = source_service.update_source(source_id, update_data)
        
        if not source:
            return jsonify({"error": "数据源不存在"}), 404
        
        # 重启调度器以应用数据源更改
        from config.settings import settings
        if scheduler_service.running and settings.AUTO_START_SCHEDULER:
            app_logger.info("Restarting scheduler to apply source changes")
            scheduler_service.stop()
            import time
            time.sleep(1)
            scheduler_service.start()
        
        return jsonify({
            "id": source.id,
            "name": source.name,
            "url": source.url,
            "source_type": source.source_type,
            "interval": source.interval
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app_logger.error(f"Error updating source {source_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 删除数据源
@source_bp.route('/<int:source_id>', methods=['DELETE'])
def delete_source(source_id):
    try:
        app_logger.info(f"DELETE /api/sources/{source_id} - Request received")
        
        # 获取数据源服务并删除数据源
        source_service = get_source_service()
        success = source_service.delete_source(source_id)
        
        if not success:
            return jsonify({"error": "数据源不存在"}), 404
        
        app_logger.info(f"Source ID {source_id} deleted successfully")
        
        # 重启调度器以移除已删除的数据源
        from config.settings import settings
        if scheduler_service.running and settings.AUTO_START_SCHEDULER:
            app_logger.info("Restarting scheduler to remove deleted source")
            scheduler_service.stop()
            import time
            time.sleep(1)
            scheduler_service.start()
        
        return jsonify({"message": "数据源删除成功"})
    except Exception as e:
        app_logger.error(f"Error deleting source {source_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 触发数据源采集
@source_bp.route('/<int:source_id>/collect', methods=['POST'])
def trigger_collection(source_id):
    try:
        app_logger.info(f"POST /api/sources/{source_id}/collect - Request received")
        
        # 获取数据源服务并触发采集
        source_service = get_source_service()
        result = source_service.trigger_collection(source_id)
        
        if result.success:
            return jsonify({
                "message": result.message,
                "documents_fetched": result.documents_fetched,
                "source_type": result.source_type,
                "sync_duration": result.sync_duration
            })
        else:
            return jsonify({"error": result.message}), 500
    except Exception as e:
        app_logger.error(f"Error triggering collection for source {source_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 获取数据源统计信息
@source_bp.route('/stats', methods=['GET'])
def get_source_stats():
    try:
        app_logger.info("GET /api/sources/stats - Request received")
        
        # 获取数据源服务并获取统计信息
        source_service = get_source_service()
        stats = source_service.get_source_statistics()
        
        return jsonify({
            "total_sources": stats.total_sources,
            "sources_by_type": stats.sources_by_type,
            "sources_by_interval": stats.sources_by_interval,
            "active_sources": stats.active_sources,
            "paused_sources": stats.paused_sources,
            "sources_due_for_sync": stats.sources_due_for_sync,
            "total_documents": stats.total_documents
        })
    except Exception as e:
        app_logger.error(f"Error getting source stats: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 获取需要同步的数据源
@source_bp.route('/due-for-sync', methods=['GET'])
def get_sources_due_for_sync():
    try:
        app_logger.info("GET /api/sources/due-for-sync - Request received")
        
        # 获取数据源服务并获取需要同步的数据源
        source_service = get_source_service()
        sources = source_service.get_sources_due_for_sync()
        
        # 转换为前端期望的格式
        sources_data = []
        for source in sources:
            sources_data.append({
                "id": source.id,
                "name": source.name,
                "url": source.url,
                "source_type": source.source_type,
                "interval": source.interval,
                "next_sync": source.next_sync.isoformat() if source.next_sync else None
            })
        
        return jsonify({"sources": sources_data})
    except Exception as e:
        app_logger.error(f"Error getting sources due for sync: {str(e)}")
        return jsonify({"error": str(e)}), 500

def validate_rss_url(url: str) -> bool:
    """验证RSS URL（用于测试兼容性）"""
    try:
        source_service = get_source_service()
        return source_service.validate_rss_url(url)
    except Exception as e:
        app_logger.error(f"Error validating RSS URL: {str(e)}")
        return False
