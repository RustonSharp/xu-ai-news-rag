#!/usr/bin/env python3
"""
API文档服务启动脚本
"""
import sys
import os
import subprocess

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask_restx
        print("✅ Flask-RESTX 已安装")
    except ImportError:
        print("❌ Flask-RESTX 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_docs.txt"])
        print("✅ 依赖安装完成")

def start_docs_server():
    """启动文档服务器"""
    print("🚀 启动API文档服务器...")
    print("📖 文档地址:")
    print("   - Swagger UI: http://localhost:5002/api/docs/")
    print("   - ReDoc: http://localhost:5002/api/docs/redoc/")
    print("   - JSON: http://localhost:5002/api/swagger.json")
    print("\n按 Ctrl+C 停止服务器")
    
    try:
        from api_docs_generator import create_docs_app
        from config.settings import settings
        
        app = create_docs_app()
        app.run(host=settings.APP_HOST, port=5002, debug=settings.APP_DEBUG)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    print("🔧 AI News RAG API 文档服务器")
    print("=" * 50)
    
    # 检查依赖
    check_dependencies()
    
    # 启动服务器
    start_docs_server()
