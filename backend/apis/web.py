from flask import Blueprint, request, jsonify
from sqlmodel import Session, create_engine, select
from models.web_source import WebSource
import os
from dotenv import load_dotenv
from utils.logging_config import app_logger
from models.document import Document

# 加载环境变量
load_dotenv()

# 创建蓝图
web_bp = Blueprint('web', __name__, url_prefix='/api/web')

# 获取数据库引擎
def get_db_engine():
    db_path = os.getenv("DATABASE_PATH")
    if not db_path:
        raise ValueError("DATABASE_PATH environment variable is not set")
    return create_engine(f"sqlite:///{db_path}")

# 获取所有Web源
@web_bp.route('/sources', methods=['GET'])
def get_web_sources():
    try:
        app_logger.info("GET /api/web/sources - Request received")
        engine = get_db_engine()
        with Session(engine) as session:
            # 从数据库查询所有Web源
            app_logger.info("Querying all Web sources from database...")
            web_sources = session.exec(select(WebSource)).all()
            # 暂时将文档计数设为0，因为Document模型还不支持web_source_id
            # TODO: 当Document模型支持web_source_id后，可以重新启用文档计数功能
            document_counts = {}
            app_logger.info(f"Found {len(web_sources)} Web sources in database.")
            return jsonify([{
                "id": source.id,
                "name": source.name,
                "url": source.url,
                "interval": source.interval,
                "is_paused": source.is_paused,
                "last_sync": source.last_sync.isoformat() if source.last_sync else None,
                "next_sync": source.next_sync.isoformat() if source.next_sync else None,
                "document_count": document_counts.get(source.id, 0)
            } for source in web_sources])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 获取单个Web源
@web_bp.route('/sources/<int:source_id>', methods=['GET'])
def get_web_source(source_id):
    try:
        engine = get_db_engine()
        with Session(engine) as session:
            web_source = session.exec(select(WebSource).where(WebSource.id == source_id)).first()
            if not web_source:
                return jsonify({"error": "Web source not found"}), 404
            return jsonify({
                "id": web_source.id,
                "name": web_source.name,
                "url": web_source.url,
                "interval": web_source.interval,
                "is_paused": web_source.is_paused,
                "last_sync": web_source.last_sync.isoformat() if web_source.last_sync else None,
                "next_sync": web_source.next_sync.isoformat() if web_source.next_sync else None
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 创建新的Web源
@web_bp.route('/sources', methods=['POST'])
def create_web_source():
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ['name', 'url']):
            return jsonify({"error": "Missing required fields: name, url"}), 400
        
        engine = get_db_engine()
        with Session(engine) as session:
            # 检查URL是否已存在
            existing_source = session.exec(select(WebSource).where(WebSource.url == data['url'])).first()
            if existing_source:
                return jsonify({"error": "Web source with this URL already exists"}), 400
            
            # 创建新的Web源
            interval = data.get('interval', 'ONE_DAY')
            is_paused = data.get('is_paused', False)
            
            # 验证interval值是否有效
            valid_intervals = ['SIX_HOUR', 'TWELVE_HOUR', 'ONE_DAY']
            if interval not in valid_intervals:
                return jsonify({"error": f"Invalid interval value. Must be one of: {valid_intervals}"}), 400
            
            # 根据interval设置下次运行时间
            from datetime import datetime, timedelta
            now = datetime.now()
            if interval == 'SIX_HOUR':
                # 每天早上6点运行
                next_sync = now.replace(hour=6, minute=0, second=0, microsecond=0)
                if next_sync < now:
                    next_sync += timedelta(days=1)
            elif interval == 'TWELVE_HOUR':
                # 每天中午12点运行
                next_sync = now.replace(hour=12, minute=0, second=0, microsecond=0)
                if next_sync < now:
                    next_sync += timedelta(days=1)
            else:  # ONE_DAY
                # 每天凌晨运行
                next_sync = now.replace(hour=0, minute=0, second=0, microsecond=0)
                next_sync += timedelta(days=1)
            
            new_source = WebSource(
                name=data['name'],
                url=data['url'],
                interval=interval,
                is_paused=is_paused,
                last_sync=None,
                next_sync=next_sync
            )
            session.add(new_source)
            session.commit()
            session.refresh(new_source)
            
            return jsonify({
                "id": new_source.id,
                "name": new_source.name,
                "url": new_source.url,
                "interval": new_source.interval,
                "is_paused": new_source.is_paused,
                "last_sync": new_source.last_sync.isoformat() if new_source.last_sync else None,
                "next_sync": new_source.next_sync.isoformat() if new_source.next_sync else None
            }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 更新Web源
@web_bp.route('/sources/<int:source_id>', methods=['PUT'])
def update_web_source(source_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        engine = get_db_engine()
        with Session(engine) as session:
            web_source = session.exec(select(WebSource).where(WebSource.id == source_id)).first()
            if not web_source:
                return jsonify({"error": "Web source not found"}), 404
            
            # 更新字段
            if 'name' in data:
                web_source.name = data['name']
            if 'url' in data:
                # 检查URL是否已被其他源使用
                app_logger.info(f"Checking if URL {data['url']} is already in use by another source...")
                existing_source = session.exec(select(WebSource).where(
                    WebSource.url == data['url'], 
                    WebSource.id != source_id
                )).first()
                if existing_source:
                    app_logger.info(f"URL {data['url']} is already in use by source ID {existing_source.id}")
                    return jsonify({"error": "Web source with this URL already exists"}), 400
                web_source.url = data['url']
            if 'interval' in data:
                # 验证interval值是否有效
                valid_intervals = ['SIX_HOUR', 'TWELVE_HOUR', 'ONE_DAY']
                if data['interval'] not in valid_intervals:
                    app_logger.error(f"Invalid interval value {data['interval']} for source ID {source_id}")
                    return jsonify({"error": f"Invalid interval value. Must be one of: {valid_intervals}"}), 400
                app_logger.info(f"Updating interval to {data['interval']} for source ID {source_id}")
                web_source.interval = data['interval']
                
                # 根据新的interval设置下次运行时间
                from datetime import datetime, timedelta
                now = datetime.now()
                if data['interval'] == 'SIX_HOUR':
                    # 每天早上6点运行
                    next_sync = now.replace(hour=6, minute=0, second=0, microsecond=0)
                    if next_sync < now:
                        next_sync += timedelta(days=1)
                elif data['interval'] == 'TWELVE_HOUR':
                    # 每天中午12点运行
                    next_sync = now.replace(hour=12, minute=0, second=0, microsecond=0)
                    if next_sync < now:
                        next_sync += timedelta(days=1)
                else:  # ONE_DAY
                    # 每天凌晨运行
                    next_sync = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    next_sync += timedelta(days=1)
                
                web_source.next_sync = next_sync
            if 'is_paused' in data:
                web_source.is_paused = data['is_paused']
            
            session.commit()
            session.refresh(web_source)
            app_logger.info(f"Web source ID {source_id} updated successfully.")
            
            return jsonify({
                "id": web_source.id,
                "name": web_source.name,
                "url": web_source.url,
                "interval": web_source.interval,
                "is_paused": web_source.is_paused,
                "last_sync": web_source.last_sync.isoformat() if web_source.last_sync else None,
                "next_sync": web_source.next_sync.isoformat() if web_source.next_sync else None
            })
    except Exception as e:
        app_logger.error(f"Error updating Web source ID {source_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 删除Web源
@web_bp.route('/sources/<int:source_id>', methods=['DELETE'])
def delete_web_source(source_id):
    try:
        app_logger.info(f"DELETE /api/web/sources/{source_id} - Request received")
        engine = get_db_engine()
        with Session(engine) as session:
            web_source = session.exec(select(WebSource).where(WebSource.id == source_id)).first()
            if not web_source:
                app_logger.error(f"DELETE /api/web/sources/{source_id} - Web source not found")
                return jsonify({"error": "Web source not found"}), 404
            
            session.delete(web_source)
            session.commit()
            app_logger.info(f"DELETE /api/web/sources/{source_id} - Web source ID {source_id} deleted successfully")
            
            return jsonify({"message": "Web source deleted successfully"})
    except Exception as e:
        app_logger.error(f"DELETE /api/web/sources/{source_id} - Error deleting Web source ID {source_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500
