from flask import Flask, jsonify
from apis.rss import rss_bp
from dotenv import load_dotenv
import os
from utils.logging_config import app_logger

# 加载环境变量
load_dotenv()

# 初始化日志配置
app_logger.info("Starting application...")

app = Flask(__name__)

# 注册RSS API蓝图
app.register_blueprint(rss_bp)

@app.route('/')
def hello_world():
    app_logger.info("Root endpoint accessed")
    return jsonify({"message": "Welcome to the API!"})

if __name__ == '__main__':
    # 从环境变量获取配置
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 5001))
    debug = os.getenv("APP_DEBUG", "true").lower() == "true"
    
    app_logger.info(f"Starting Flask app on {host}:{port} with debug={debug}")
    app.run(host=host, port=port, debug=debug)
