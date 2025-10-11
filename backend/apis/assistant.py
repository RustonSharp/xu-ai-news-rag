from flask import Blueprint, request, jsonify
from utils.logging_config import app_logger
from core.dependencies import get_db_session_sync
from services.assistant_service import AssistantService
from schemas.assistant_schema import AssistantQueryRequest, AssistantHealthResponse

# 创建蓝图
assistant_bp = Blueprint('assistant', __name__, url_prefix='/api/assistant')

def get_assistant_service():
    """获取助手服务实例"""
    session = get_db_session_sync()
    return AssistantService(session)

def get_assistant():
    """获取助手实例（用于测试兼容性）"""
    return get_assistant_service()

def create_assistant():
    """创建助手实例（用于测试兼容性）"""
    return get_assistant_service()

def query_with_sources(query: str) -> dict:
    """查询助手并返回结果（用于测试兼容性）"""
    try:
        assistant_service = get_assistant_service()
        query_request = AssistantQueryRequest(query=query)
        result = assistant_service.process_query(query_request)
        return result.dict()
    except Exception as e:
        app_logger.error(f"Error in query_with_sources: {str(e)}")
        return {"error": str(e)}

@assistant_bp.route('/query', methods=['POST'])
def query_assistant():
    """处理用户查询的API端点"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Missing required field: query"}), 400
        
        query = data['query']
        app_logger.info(f"POST /api/assistant/query - Query received: {query}")
        
        # 创建请求对象
        query_request = AssistantQueryRequest(query=query)
        
        # 获取助手服务并处理查询
        assistant_service = get_assistant_service()
        result = assistant_service.process_query(query_request)
        
        # 返回结果
        return jsonify(result.dict())
    
    except Exception as e:
        app_logger.error(f"POST /api/assistant/query - Error processing query: {str(e)}")
        return jsonify({"error": str(e)}), 500

@assistant_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        # 获取助手服务并检查健康状态
        assistant_service = get_assistant_service()
        health_response = assistant_service.health_check()
        
        if health_response.status == "healthy":
            return jsonify(health_response.dict())
        else:
            return jsonify(health_response.dict()), 500
    except Exception as e:
        app_logger.error(f"GET /api/assistant/health - Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500