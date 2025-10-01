from flask import Blueprint, request, jsonify
from utils.logging_config import app_logger
from assistant import create_assistant, query_with_sources

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
        
        # 使用新的查询函数获取答案、原始来源和来源类型
        result = query_with_sources(query)
        
        # 提取答案、原始来源和来源类型
        final_answer = result.get("answer", "")
        raw_sources = result.get("raw_sources", [])
        origin = result.get("origin", "knowledge_base")
        
        # 格式化sources信息
        sources = []
        if isinstance(raw_sources, list):
            for i, source in enumerate(raw_sources):
                if isinstance(source, dict):
                    sources.append({
                        "id": str(i + 1),
                        "title": source.get("metadata", {}).get("title", f"文档片段 {i + 1}"),
                        "content": source.get("content", ""),
                        "url": "",
                        "score": 1.0 - (i * 0.1),
                        "type": "document",
                        "source": source.get("metadata", {}).get("source", "知识库"),
                        "relevance": 1.0 - (i * 0.1),
                        "timestamp": source.get("metadata", {}).get("pub_date", "")
                    })
        
        if sources == [] or sources[0]['title'] == "":
            sources = []
        # 返回结果，格式化为前端期望的结构
        return jsonify({
            "query": query,
            "response": final_answer,
            "answer": final_answer,
            "sources": sources,
            "raw_answer": raw_sources,  # 添加原始来源信息
            "origin": origin,
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