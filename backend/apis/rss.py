from flask import Blueprint, request, jsonify
from sqlmodel import Session, create_engine, select
from models.rss_source import RssSource
from models.enums.interval import IntervalEnum
import os
from dotenv import load_dotenv
from utils.logging_config import app_logger

# 加载环境变量
load_dotenv()

# 创建蓝图
rss_bp = Blueprint('rss', __name__, url_prefix='/api/rss')

# 获取数据库引擎
def get_db_engine():
    db_path = os.getenv("DATABASE_PATH")
    if not db_path:
        raise ValueError("DATABASE_PATH environment variable is not set")
    return create_engine(f"sqlite:///{db_path}")

# 获取所有RSS源
@rss_bp.route('/sources', methods=['GET'])
def get_rss_sources():
    try:
        app_logger.info("GET /api/rss/sources - Request received")
        engine = get_db_engine()
        with Session(engine) as session:
            # 从数据库查询所有RSS源
            app_logger.info("Querying all RSS sources from database...")
            rss_sources = session.exec(select(RssSource)).all()
            app_logger.info(f"Found {len(rss_sources)} RSS sources in database.")
            return jsonify([{
                "id": source.id,
                "name": source.name,
                "url": source.url,
                "interval": source.interval.value
            } for source in rss_sources])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 获取单个RSS源
@rss_bp.route('/sources/<int:source_id>', methods=['GET'])
def get_rss_source(source_id):
    try:
        engine = get_db_engine()
        with Session(engine) as session:
            rss_source = session.exec(select(RssSource).where(RssSource.id == source_id)).first()
            if not rss_source:
                return jsonify({"error": "RSS source not found"}), 404
            return jsonify({
                "id": rss_source.id,
                "name": rss_source.name,
                "url": rss_source.url,
                "interval": rss_source.interval.value
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 创建新的RSS源
@rss_bp.route('/sources', methods=['POST'])
def create_rss_source():
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ['name', 'url']):
            return jsonify({"error": "Missing required fields: name, url"}), 400
        
        engine = get_db_engine()
        with Session(engine) as session:
            # 检查URL是否已存在
            existing_source = session.exec(select(RssSource).where(RssSource.url == data['url'])).first()
            if existing_source:
                return jsonify({"error": "RSS source with this URL already exists"}), 400
            
            # 创建新的RSS源
            interval = data.get('interval', IntervalEnum.MINUTE.value)
            try:
                interval_enum = IntervalEnum(interval)
            except ValueError:
                return jsonify({"error": f"Invalid interval value. Must be one of: {[e.value for e in IntervalEnum]}"}), 400
            
            new_source = RssSource(
                name=data['name'],
                url=data['url'],
                interval=interval_enum
            )
            session.add(new_source)
            session.commit()
            session.refresh(new_source)
            
            return jsonify({
                "id": new_source.id,
                "name": new_source.name,
                "url": new_source.url,
                "interval": new_source.interval.value
            }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 更新RSS源
@rss_bp.route('/sources/<int:source_id>', methods=['PUT'])
def update_rss_source(source_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        engine = get_db_engine()
        with Session(engine) as session:
            rss_source = session.exec(select(RssSource).where(RssSource.id == source_id)).first()
            if not rss_source:
                return jsonify({"error": "RSS source not found"}), 404
            
            # 更新字段
            if 'name' in data:
                rss_source.name = data['name']
            if 'url' in data:
                # 检查URL是否已被其他源使用
                app_logger.info(f"Checking if URL {data['url']} is already in use by another source...")
                existing_source = session.exec(select(RssSource).where(
                    RssSource.url == data['url'], 
                    RssSource.id != source_id
                )).first()
                if existing_source:
                    app_logger.info(f"URL {data['url']} is already in use by source ID {existing_source.id}")
                    return jsonify({"error": "RSS source with this URL already exists"}), 400
                rss_source.url = data['url']
            if 'interval' in data:
                try:
                    app_logger.info(f"Updating interval to {data['interval']} for source ID {source_id}")
                    rss_source.interval = IntervalEnum(data['interval'])
                except ValueError:
                    app_logger.error(f"Invalid interval value {data['interval']} for source ID {source_id}")
                    return jsonify({"error": f"Invalid interval value. Must be one of: {[e.value for e in IntervalEnum]}"}), 400
            
            session.commit()
            session.refresh(rss_source)
            app_logger.info(f"RSS source ID {source_id} updated successfully.")
            return jsonify({
                "id": rss_source.id,
                "name": rss_source.name,
                "url": rss_source.url,
                "interval": rss_source.interval.value
            })
    except Exception as e:
        app_logger.error(f"Error updating RSS source ID {source_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 删除RSS源
@rss_bp.route('/sources/<int:source_id>', methods=['DELETE'])
def delete_rss_source(source_id):
    try:
        app_logger.info(f"DELETE /api/rss/sources/{source_id} - Request received")
        engine = get_db_engine()
        with Session(engine) as session:
            rss_source = session.exec(select(RssSource).where(RssSource.id == source_id)).first()
            if not rss_source:
                app_logger.error(f"DELETE /api/rss/sources/{source_id} - RSS source not found")
                return jsonify({"error": "RSS source not found"}), 404
            
            session.delete(rss_source)
            session.commit()
            app_logger.info(f"DELETE /api/rss/sources/{source_id} - RSS source ID {source_id} deleted successfully")
            return jsonify({"message": "RSS source deleted successfully"})
    except Exception as e:
        app_logger.error(f"DELETE /api/rss/sources/{source_id} - Error deleting RSS source ID {source_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 获取RSS订阅内容
@rss_bp.route('/feeds/<int:source_id>', methods=['GET'])
def get_rss_feeds(source_id):
    try:
        from fetch_document import fetch_rss_feeds
        app_logger.info(f"GET /api/rss/feeds/{source_id} - Request received")
        
        engine = get_db_engine()
        with Session(engine) as session:
            # 检查RSS源是否存在
            rss_source = session.exec(select(RssSource).where(RssSource.id == source_id)).first()
            if not rss_source:
                app_logger.error(f"GET /api/rss/feeds/{source_id} - RSS source not found")
                return jsonify({"error": "RSS source not found"}), 404
            
            # 获取RSS订阅内容
            fetch_rss_feeds(source_id, session)
            
            return jsonify({"message": "RSS feeds fetched successfully"})
    except Exception as e:
        app_logger.error(f"GET /api/rss/feeds/{source_id} - Error fetching RSS feeds for source ID {source_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

