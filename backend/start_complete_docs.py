#!/usr/bin/env python3
"""
启动完整API文档服务器
包含所有API端点的详细文档
"""
import sys
import os
import subprocess

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask_restx
        print("✅ Flask-RESTX 已安装")
        return True
    except ImportError:
        print("❌ Flask-RESTX 未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask-restx"])
            print("✅ Flask-RESTX 安装完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ Flask-RESTX 安装失败")
            return False

def start_complete_docs():
    """启动完整API文档服务器"""
    print("🔧 AI News RAG - 完整API文档服务器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，请手动安装 flask-restx")
        return
    
    print("🚀 启动完整API文档服务器...")
    print("📖 文档地址:")
    print("   - Swagger UI: http://localhost:5002/api/docs/")
    print("   - ReDoc: http://localhost:5002/api/docs/redoc/")
    print("   - JSON: http://localhost:5002/api/swagger.json")
    print("\n📋 包含的API模块:")
    print("   - 🔐 认证模块 (auth)")
    print("   - 📰 数据源模块 (sources)")
    print("   - 📄 文档模块 (documents)")
    print("   - 🤖 助手模块 (assistant)")
    print("   - ⏰ 调度器模块 (scheduler)")
    print("   - 📊 分析模块 (analytics)")
    print("\n🛑 按 Ctrl+C 停止服务器")
    
    try:
        from complete_api_docs import create_complete_docs_app
        app = create_complete_docs_app()
        app.run(host='0.0.0.0', port=5002, debug=True)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    start_complete_docs()
