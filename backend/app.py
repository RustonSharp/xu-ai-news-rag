from flask import Flask, jsonify
from flask_cors import CORS
from apis.rss import rss_bp
from apis.web import web_bp
from apis.document import document_bp
from apis.auth import auth_bp
from apis.assistant import assistant_bp
from apis.scheduler import scheduler_bp
from dotenv import load_dotenv
import os
from utils.logging_config import app_logger
from utils.init_sqlite import init_db
from rss_scheduler import rss_scheduler
# 加载环境变量
load_dotenv()

def create_app():
    """创建Flask应用实例"""
    # 执行初始化程序，不会覆盖或删除现有数据，会创建缺失的表，不会修改表结构
    init_db()

    # 初始化日志配置
    app_logger.info("Initializing application...")

    app = Flask(__name__)
    
    # 配置CORS，允许前端应用访问
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # 注册RSS API蓝图
    app.register_blueprint(rss_bp)
    # 注册Web API蓝图
    app.register_blueprint(web_bp)
    # 注册文档API蓝图
    app.register_blueprint(document_bp)
    # 注册鉴权API蓝图
    app.register_blueprint(auth_bp)
    # 注册助手API蓝图
    app.register_blueprint(assistant_bp)
    # 注册调度器API蓝图
    app.register_blueprint(scheduler_bp)

    @app.route('/')
    def hello_world():
        app_logger.info("Root endpoint accessed")
        return jsonify({"message": "Welcome to the API!"})
    
    return app

app = create_app()

# 从环境变量获取配置
host = os.getenv("APP_HOST", "0.0.0.0")
port = int(os.getenv("APP_PORT", 5001))
debug = os.getenv("APP_DEBUG", "true").lower() == "true"
auto_start_scheduler = os.getenv("AUTO_START_SCHEDULER", "true").lower() == "true"

# 根据环境变量决定是否自动启动RSS定时任务调度器
if auto_start_scheduler:
    app_logger.info("Auto-starting RSS scheduler")
    rss_scheduler.start()
else:
    app_logger.info("RSS scheduler auto-start disabled")


if __name__ == '__main__':
    app_logger.info(f"Starting Flask app on {host}:{port} with debug={debug}")
    app.run(host=host, port=port, debug=debug)
