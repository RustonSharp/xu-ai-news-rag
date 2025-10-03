from flask import Blueprint, request, jsonify
from sqlmodel import Session, create_engine, select
from models.rss_source import RssSource
import os
from dotenv import load_dotenv
from utils.logging_config import app_logger
from rss_scheduler import rss_scheduler
from models.document import Document

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
            # 修复: 正确计算每个RSS源的文档数量
            source_ids = [source.id for source in rss_sources]
            if source_ids:
                document_counts = {}
                docs = session.exec(select(Document).where(Document.rss_source_id.in_(source_ids))).all()
                for doc in docs:
                    document_counts[doc.rss_source_id] = document_counts.get(doc.rss_source_id, 0) + 1
            else:
                document_counts = {}
            app_logger.info(f"Found {len(rss_sources)} RSS sources in database.")
            return jsonify([{
                "id": source.id,
                "name": source.name,
                "url": source.url,
                "interval": source.interval,
                "last_sync": source.last_sync.isoformat() if source.last_sync else None,
                "next_sync": source.next_sync.isoformat() if source.next_sync else None,
                "document_count": document_counts.get(source.id, 0)
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
                "interval": rss_source.interval
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
            interval = data.get('interval', 'ONE_DAY')
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
            
            new_source = RssSource(
                name=data['name'],
                url=data['url'],
                interval=interval,
                last_sync=None,
                next_sync=next_sync
            )
            session.add(new_source)
            session.commit()
            session.refresh(new_source)
            
            # 重启调度器以包含新添加的RSS源
            auto_start_scheduler = os.getenv("AUTO_START_SCHEDULER", "true").lower() == "true"
            if rss_scheduler.running and auto_start_scheduler:
                app_logger.info("Restarting RSS scheduler to include new RSS source")
                rss_scheduler.stop()
                import time
                time.sleep(1)  # 等待调度器完全停止
                rss_scheduler.start()
            
            return jsonify({
                "id": new_source.id,
                "name": new_source.name,
                "url": new_source.url,
                "interval": new_source.interval
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
                # 验证interval值是否有效
                valid_intervals = ['SIX_HOUR', 'TWELVE_HOUR', 'ONE_DAY']
                if data['interval'] not in valid_intervals:
                    app_logger.error(f"Invalid interval value {data['interval']} for source ID {source_id}")
                    return jsonify({"error": f"Invalid interval value. Must be one of: {valid_intervals}"}), 400
                app_logger.info(f"Updating interval to {data['interval']} for source ID {source_id}")
                rss_source.interval = data['interval']
                
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
                
                rss_source.next_sync = next_sync
            
            session.commit()
            session.refresh(rss_source)
            app_logger.info(f"RSS source ID {source_id} updated successfully.")
            
            # 重启调度器以应用RSS源更改
            auto_start_scheduler = os.getenv("AUTO_START_SCHEDULER", "true").lower() == "true"
            if rss_scheduler.running and auto_start_scheduler:
                app_logger.info("Restarting RSS scheduler to apply RSS source changes")
                rss_scheduler.stop()
                import time
                time.sleep(1)  # 等待调度器完全停止
                rss_scheduler.start()
            
            return jsonify({
                "id": rss_source.id,
                "name": rss_source.name,
                "url": rss_source.url,
                "interval": rss_source.interval
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
            
            # 重启调度器以移除已删除的RSS源
            auto_start_scheduler = os.getenv("AUTO_START_SCHEDULER", "true").lower() == "true"
            if rss_scheduler.running and auto_start_scheduler:
                app_logger.info("Restarting RSS scheduler to remove deleted RSS source")
                rss_scheduler.stop()
                import time
                time.sleep(1)  # 等待调度器完全停止
                rss_scheduler.start()
            
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

# 触发RSS采集
@rss_bp.route('/feeds/<int:source_id>', methods=['POST'])
def trigger_rss_collection(source_id):
    try:
        from fetch_document import fetch_rss_feeds
        app_logger.info(f"POST /api/rss/feeds/{source_id} - Request received")
        
        engine = get_db_engine()
        with Session(engine) as session:
            # 检查RSS源是否存在
            rss_source = session.exec(select(RssSource).where(RssSource.id == source_id)).first()
            if not rss_source:
                app_logger.error(f"POST /api/rss/feeds/{source_id} - RSS source not found")
                return jsonify({"error": "RSS source not found"}), 404
            
            # 触发RSS采集
            fetch_rss_feeds(source_id, session)
            
            # 更新上次执行时间
            from datetime import datetime
            rss_source.last_sync = datetime.now()
            session.commit()
            
            return jsonify({"message": "RSS collection triggered successfully"})
    except Exception as e:
        app_logger.error(f"POST /api/rss/feeds/{source_id} - Error triggering RSS collection for source ID {source_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

