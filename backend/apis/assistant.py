from flask import Blueprint, request, jsonify
from utils.logging_config import app_logger
from assistant import create_assistant

# 创建蓝图
assistant_bp = Blueprint('assistant', __name__, url_prefix='/api/assistant')

# 全局变量存储助手实例
assistant_instance = None

def get_assistant():
    """获取或创建助手实例"""
    global assistant_instance
    if assistant_instance is None:
        try:
            assistant_instance = create_assistant()
            app_logger.info("Assistant instance created successfully")
        except Exception as e:
            app_logger.error(f"Failed to create assistant instance: {str(e)}")
            raise e
    return assistant_instance

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
        
        # 获取助手实例
        assistant = get_assistant()
        
        # 处理查询
        result = assistant.invoke(query)
        
        # 提取sources信息
        sources = []
        
        # 尝试从result中提取sources
        # 如果result是字符串，则sources为空数组
        if isinstance(result, str):
            answer = result
        # 如果result是字典且包含sources字段
        elif isinstance(result, dict) and 'sources' in result:
            answer = result.get('answer', str(result))
            sources = result.get('sources', [])
        # 如果result是字典但不包含sources字段
        elif isinstance(result, dict):
            answer = result.get('answer', str(result))
            # 尝试从其他字段提取sources
            if 'source_documents' in result:
                sources = result['source_documents']
            elif 'documents' in result:
                sources = result['documents']
        # 其他情况
        else:
            answer = str(result)
        
        # 返回结果，格式化为前端期望的结构
        return jsonify({
            "query": query,
            "response": result,
            "answer": answer,
            "sources": sources,
            "status": "success"
        })
    
    except Exception as e:
        app_logger.error(f"POST /api/assistant/query - Error processing query: {str(e)}")
        return jsonify({"error": str(e)}), 500

@assistant_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        # 尝试获取助手实例，确保助手可以正常初始化
        assistant = get_assistant()
        
        return jsonify({
            "status": "healthy",
            "message": "Assistant is ready to process queries"
        })
    except Exception as e:
        app_logger.error(f"GET /api/assistant/health - Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500