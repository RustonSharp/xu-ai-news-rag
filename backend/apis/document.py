from flask import Blueprint, request, jsonify
from sqlmodel import Session, create_engine, select
from models.document import Document
from models.rss_source import RssSource
import os
from dotenv import load_dotenv
from utils.logging_config import app_logger
from tools import knowledge_base_cluster_analysis
# 加载环境变量
load_dotenv()

# 创建蓝图
document_bp = Blueprint('document', __name__, url_prefix='/api/documents')

# 获取数据库引擎
def get_db_engine():
    db_path = os.getenv("DATABASE_PATH")
    if not db_path:
        raise ValueError("DATABASE_PATH environment variable is not set")
    return create_engine(f"sqlite:///{db_path}")

# 获取聚类分布
@document_bp.route('cluster_analysis',methods=['GET'])
def get_cluster_analysis():
    try:
        app_logger.info("GET /api/documents/cluster_analysis - Request received")
        # 获取聚类分析结果
        cluster_analysis = knowledge_base_cluster_analysis()
        # 确保只保留前10个聚类类别
        if "top_clusters" in cluster_analysis:
            cluster_analysis["top_clusters"] = cluster_analysis["top_clusters"][:10]
        
        # 导入assistant模块
        from assistant import create_assistant
        # 创建assistant实例
        assistant = create_assistant()
        
        # 提取每个聚类的id、percentage和关键词
        cluster_results = []
        for cluster in cluster_analysis.get("top_clusters", []):
            # 获取聚类ID
            cluster_id = cluster.get("cluster_id", 0)
            
            # 获取百分比
            percentage = cluster.get("percentage", 0)
            
            # 获取关键词列表
            keywords = cluster.get("keywords", [])
            
            # 使用assistant为聚类生成一个总结性的关键词
            if keywords:
                # 准备提示词，要求assistant根据关键词列表生成一个总结性的词
                keyword_prompt = f"""
                请根据以下关键词列表，为这个文档聚类生成一个最能代表该类别的总结性词语：

                关键词列表：{', '.join(keywords)}

                要求：
                1. 只返回一个词语，不要有多余的解释
                2. 这个词语应该能够概括整个聚类的主题
                """
                
                # 使用assistant生成总结性关键词
                keyword_result = assistant.invoke(keyword_prompt)
                
                # 处理assistant的响应，确保它是字符串格式
                if isinstance(keyword_result, dict):
                    # 如果响应是字典，尝试获取输出内容
                    if "output" in keyword_result:
                        keyword = keyword_result["output"].strip()
                    else:
                        # 如果没有output字段，将整个字典转换为字符串
                        keyword = str(keyword_result).strip()
                else:
                    # 如果响应不是字典，直接使用
                    keyword = str(keyword_result).strip()
                
                # 确保keyword是一个词，去除多余的内容
                keyword = keyword.split()[0] if keyword else keywords[0]
            else:
                keyword = ""
            
            cluster_results.append({
                "id": cluster_id,
                "percentage": percentage,
                "keyword": keyword
            })
        
        # 返回聚类结果
        return jsonify({
            "clusters": cluster_results
        })
    except Exception as e:
        app_logger.error(f"Error in cluster analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
    

# 获取所有文档
@document_bp.route('', methods=['GET'])
def get_documents():
    try:
        app_logger.info("GET /api/documents - Request received")
        engine = get_db_engine()
        with Session(engine) as session:
            # 从数据库查询所有文档
            app_logger.info("Querying all documents from database...")
            documents = session.exec(select(Document)).all()
            app_logger.info(f"Found {len(documents)} documents in database.")
            return jsonify([{
                "id": doc.id,
                "title": doc.title,
                "link": doc.link,
                "description": doc.description,
                "pub_date": doc.pub_date.isoformat() if doc.pub_date else None,
                "author": doc.author,
                "tags": doc.tags.split(",") if doc.tags else [],
                "rss_source_id": doc.rss_source_id,
                "crawled_at": doc.crawled_at.isoformat()
            } for doc in documents])
    except Exception as e:
        app_logger.error(f"Error getting documents: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 获取单个文档
@document_bp.route('/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    try:
        app_logger.info(f"GET /api/documents/{doc_id} - Request received")
        engine = get_db_engine()
        with Session(engine) as session:
            document = session.exec(select(Document).where(Document.id == doc_id)).first()
            if not document:
                app_logger.error(f"Document with ID {doc_id} not found")
                return jsonify({"error": "Document not found"}), 404
            
            return jsonify({
                "id": document.id,
                "title": document.title,
                "link": document.link,
                "description": document.description,
                "pub_date": document.pub_date.isoformat() if document.pub_date else None,
                "author": document.author,
                "tags": document.tags.split(",") if document.tags else [],
                "rss_source_id": document.rss_source_id,
                "crawled_at": document.crawled_at.isoformat()
            })
    except Exception as e:
        app_logger.error(f"Error getting document with ID {doc_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 获取特定RSS源的所有文档
@document_bp.route('/get_documents_by_source_id/<int:source_id>', methods=['GET'])
def get_documents_by_source_id(source_id):
    try:
        app_logger.info(f"GET /api/documents/get_documents_by_source_id/{source_id} - Request received")    
        engine = get_db_engine()
        with Session(engine) as session:
            # 检查RSS源是否存在
            rss_source = session.exec(select(RssSource).where(RssSource.id == source_id)).first()
            if not rss_source:
                app_logger.error(f"RSS source with ID {source_id} not found")
                return jsonify({"error": "RSS source not found"}), 404
            
            # 获取该RSS源的所有文档
            documents = session.exec(select(Document).where(Document.rss_source_id == source_id)).all()
            app_logger.info(f"Found {len(documents)} documents for RSS source ID {source_id}")
            
            return jsonify([{
                "id": doc.id,
                "title": doc.title,
                "link": doc.link,
                "description": doc.description,
                "pub_date": doc.pub_date.isoformat() if doc.pub_date else None,
                "author": doc.author,
                "tags": doc.tags.split(",") if doc.tags else [],
                "rss_source_id": doc.rss_source_id,
                "crawled_at": doc.crawled_at.isoformat()
            } for doc in documents])
    except Exception as e:
        app_logger.error(f"Error getting documents for RSS source ID {source_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500