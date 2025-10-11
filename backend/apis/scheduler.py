from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from utils.logging_config import app_logger
from services.scheduler_service import scheduler_service
from core.database import db_manager
from sqlmodel import Session, select
from models.source import Source
from config.settings import settings
import os

# 创建RSS调度器API蓝图
scheduler_bp = Blueprint('scheduler', __name__, url_prefix='/api/scheduler')

@scheduler_bp.route('/status', methods=['GET'])
@cross_origin()
def get_scheduler_status():
    """获取调度器状态"""
    try:
        with db_manager.get_session() as session:
            # 获取所有RSS源
            rss_sources = session.exec(select(Source).where(Source.source_type == "rss")).all()
            
            # 获取当前活动的线程
            active_threads = {}
            with scheduler_service.lock:
                for rss_id, thread in scheduler_service.threads.items():
                    if thread.is_alive():
                        active_threads[rss_id] = True
            
            # 构建响应数据
            status_data = {
                "running": scheduler_service.running,
                "rss_sources": []
            }
            
            for rss_source in rss_sources:
                status_data["rss_sources"].append({
                    "id": rss_source.id,
                    "name": rss_source.name,
                    "url": rss_source.url,
                    "interval": rss_source.interval,
                    "is_paused": getattr(rss_source, 'is_paused', False),
                    "active": rss_source.id in active_threads
                })
            
            return jsonify({
                "success": True,
                "data": status_data
            })
    except Exception as e:
        app_logger.error(f"Error getting scheduler status: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取调度器状态失败: {str(e)}"
        }), 500

@scheduler_bp.route('/start', methods=['POST'])
@cross_origin()
def start_scheduler():
    """启动调度器"""
    try:
        # 检查是否允许手动启动调度器
        allow_manual_start = settings.ALLOW_MANUAL_SCHEDULER_START
        if not allow_manual_start:
            return jsonify({
                "success": False,
                "message": "调度器手动启动已禁用"
            }), 400
            
        if scheduler_service.running:
            return jsonify({
                "success": False,
                "message": "调度器已经在运行中"
            }), 400
        
        scheduler_service.start()
        app_logger.info("RSS scheduler started via API")
        
        return jsonify({
            "success": True,
            "message": "调度器已成功启动"
        })
    except Exception as e:
        app_logger.error(f"Error starting scheduler: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"启动调度器失败: {str(e)}"
        }), 500

@scheduler_bp.route('/stop', methods=['POST'])
@cross_origin()
def stop_scheduler():
    """停止调度器"""
    try:
        if not scheduler_service.running:
            return jsonify({
                "success": False,
                "message": "调度器未在运行"
            }), 400
        
        scheduler_service.stop()
        app_logger.info("RSS scheduler stopped via API")
        
        return jsonify({
            "success": True,
            "message": "调度器已成功停止"
        })
    except Exception as e:
        app_logger.error(f"Error stopping scheduler: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"停止调度器失败: {str(e)}"
        }), 500

@scheduler_bp.route('/fetch/<int:rss_id>', methods=['POST'])
@cross_origin()
def fetch_rss_now(rss_id):
    """立即获取指定RSS源的新闻"""
    try:
        from services.document_service import DocumentService
        
        with db_manager.get_session() as session:
            # 检查RSS源是否存在
            rss_source = session.exec(select(Source).where(Source.id == rss_id, Source.source_type == "rss")).first()
            if not rss_source:
                return jsonify({
                    "success": False,
                    "message": f"未找到ID为 {rss_id} 的RSS源"
                }), 404
            
            # 检查RSS源是否暂停
            if hasattr(rss_source, 'is_paused') and rss_source.is_paused:
                return jsonify({
                    "success": False,
                    "message": f"RSS源 {rss_source.name} 已暂停，无法获取新闻"
                }), 400
            
            # 立即获取RSS
            document_service = DocumentService(session)
            success = document_service.fetch_rss_feeds(rss_id)
            
            if success:
                app_logger.info(f"Manual RSS fetch triggered for source {rss_source.name} (ID: {rss_id})")
                return jsonify({
                    "success": True,
                    "message": f"成功获取RSS源 {rss_source.name} 的新闻"
                })
            else:
                return jsonify({
                    "success": False,
                    "message": f"获取RSS源 {rss_source.name} 的新闻失败"
                }), 500
    except Exception as e:
        app_logger.error(f"Error fetching RSS for source {rss_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取RSS失败: {str(e)}"
        }), 500