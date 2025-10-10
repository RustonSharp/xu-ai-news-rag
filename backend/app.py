from flask import Flask, jsonify
from flask_cors import CORS
from apis.source import source_bp
from apis.document import document_bp
from apis.auth import auth_bp
from apis.assistant import assistant_bp
from apis.scheduler import scheduler_bp
from utils.logging_config import app_logger
from utils.init_sqlite import init_db
from services.scheduler_service import scheduler_service
from config.settings import settings

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
            "origins": settings.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # 注册统一数据源API蓝图
    app.register_blueprint(source_bp)
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

# 根据环境变量决定是否自动启动RSS定时任务调度器
if settings.AUTO_START_SCHEDULER:
    app_logger.info("Auto-starting RSS scheduler")
    scheduler_service.start()
else:
    app_logger.info("RSS scheduler auto-start disabled")


if __name__ == '__main__':
    app_logger.info(f"Starting Flask app on {settings.APP_HOST}:{settings.APP_PORT} with debug={settings.APP_DEBUG}")
    app.run(host=settings.APP_HOST, port=settings.APP_PORT, debug=settings.APP_DEBUG)
