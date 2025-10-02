from flask import Blueprint, request, jsonify
from sqlmodel import Session, create_engine, select, func
from models.document import Document
from models.rss_source import RssSource
from models.analysis import Analysis
import os
import pandas as pd
import threading
from dotenv import load_dotenv
from utils.logging_config import app_logger
from tools import knowledge_base_cluster_analysis
from werkzeug.utils import secure_filename
from fetch_document import store_documents_in_knowledge_base
import json

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
        
        # 将完整分析结果保存到数据库
        engine = get_db_engine()
        with Session(engine) as session:
            analysis = Analysis(
                method=cluster_analysis.get("clustering_method", "unknown"),
                silhouette_score=cluster_analysis.get("silhouette_score"),
                total_documents=cluster_analysis.get("total_documents"),
                total_clusters=cluster_analysis.get("total_clusters"),
                report_json=json.dumps({
                    "clusters": cluster_results,
                    "raw": cluster_analysis
                }, ensure_ascii=False)
            )
            session.add(analysis)
            session.commit()

        # 返回聚类结果（精简版供前端使用）
        return jsonify({
            "clusters": cluster_results
        })
    except Exception as e:
        app_logger.error(f"Error in cluster analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 返回最新的一次聚类分析结果
@document_bp.route('cluster_analysis/latest', methods=['GET'])
def get_latest_cluster_analysis():
    try:
        app_logger.info("GET /api/documents/cluster_analysis/latest - Request received")
        engine = get_db_engine()
        with Session(engine) as session:
            latest = session.exec(
                select(Analysis).order_by(Analysis.created_at.desc())
            ).first()
            if not latest:
                return jsonify({"clusters": [], "message": "no analysis found"})

            data = json.loads(latest.report_json)
            # 尽量返回与现有前端一致的结构
            clusters = data.get("clusters")
            return jsonify({
                "clusters": clusters if clusters is not None else []
            })
    except Exception as e:
        app_logger.error(f"Error getting latest cluster analysis: {str(e)}")
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

@document_bp.route('/page', methods=['GET'])
def get_documents_page():
    try:
        app_logger.info("GET /api/documents/page - Request received")   
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 20, type=int)
        search = request.args.get('search', '', type=str)
        doc_type = request.args.get('type', '', type=str)
        source = request.args.get('source', '', type=str)
        start_date = request.args.get('start', '', type=str)
        end_date = request.args.get('end', '', type=str)
        
        # 计算偏移量
        offset = (page - 1) * size
        
        engine = get_db_engine()
        with Session(engine) as session:
            # 构建查询
            query = select(Document)
            
            # 添加搜索条件
            if search:
                query = query.where(Document.title.contains(search) | Document.description.contains(search))
            
            # 添加类型过滤
            if doc_type:
                # 假设类型存储在tags字段中，可以根据实际情况调整
                query = query.where(Document.tags.contains(doc_type))
            
            # 添加来源过滤
            if source:
                # 需要关联RSS源表进行过滤
                query = query.join(RssSource).where(RssSource.name.contains(source))
            
            # 添加日期范围过滤
            if start_date:
                query = query.where(Document.crawled_at >= start_date)
            if end_date:
                query = query.where(Document.crawled_at <= end_date)
            
            # 获取总数
            count_query = select(func.count()).select_from(query.subquery())
            total = session.exec(count_query).one()
            
            # 添加分页和排序
            query = query.order_by(Document.crawled_at.desc()).offset(offset).limit(size)
            
            # 执行查询
            app_logger.info("Querying documents from database...")
            documents = session.exec(query).all()
            app_logger.info(f"Found {len(documents)} documents in database.")
            
            # 计算总页数
            total_pages = (total + size - 1) // size
            
            return jsonify({
                "items": [{
                    "id": doc.id,
                    "title": doc.title,
                    "link": doc.link,
                    "description": doc.description,
                    "pub_date": doc.pub_date.isoformat() if doc.pub_date else None,
                    "author": doc.author,
                    "tags": doc.tags.split(",") if doc.tags else [],
                    "rss_source_id": doc.rss_source_id,
                    "crawled_at": doc.crawled_at.isoformat()
                } for doc in documents],
                "total": total,
                "page": page,
                "size": size,
                "total_pages": total_pages
            })
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


# Add these file extensions according to your requirements
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload Excel file to add documents
@document_bp.route('/upload_excel', methods=['POST'])
def upload_excel():
    try:
        app_logger.info("POST /api/documents/upload_excel - Request received")
        # Check if the post request has the file part
        if 'file' not in request.files:
            app_logger.error("No file part in the request")
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            app_logger.error("No selected file")
            return jsonify({"error": "No selected file"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Read Excel file
            try:
                df = pd.read_excel(file)
            except Exception as e:
                app_logger.error(f"Error reading Excel file: {str(e)}")
                return jsonify({"error": f"Error reading Excel file: {str(e)}"}), 400
            
            document_list = []
            engine = get_db_engine()
            with Session(engine) as session:
                for _, row in df.iterrows():
                    try:
                        # Create a new Document instance
                        new_doc = Document(
                            title=row.get('title', ''),
                            link=row.get('link', ''),
                            description=row.get('description', ''),
                            pub_date=row.get('pub_date', None),
                            author=row.get('author', ''),
                            tags=','.join(map(str, row.get('tags', []))) if isinstance(row.get('tags', []), list) else str(row.get('tags', '')),
                            rss_source_id=row.get('rss_source_id', None),
                            crawled_at=row.get('crawled_at', None)
                        )
                        session.add(new_doc)
                        session.commit()
                        # 刷新对象以确保所有属性都已正确设置
                        session.refresh(new_doc)
                        # 将文档数据转换为字典格式，避免会话绑定问题
                        document_list.append({
                            "id": new_doc.id,
                            "title": new_doc.title,
                            "link": new_doc.link,
                            "description": new_doc.description,
                            "tags": new_doc.tags,
                            "pub_date": new_doc.pub_date.isoformat() if new_doc.pub_date else None,
                            "author": new_doc.author
                        })
                    except Exception as e:
                        app_logger.error(f"Error creating document from Excel row: {str(e)}")
                        continue
                app_logger.info(f"Successfully added {len(df)} documents from {filename}")
                 # 在新线程中执行知识库存储操作
                if document_list:  # 只有当有文档需要存储时才创建线程
                    kb_thread = threading.Thread(target=store_documents_in_knowledge_base, args=(document_list,))
                    kb_thread.daemon = True  # 设置为守护线程，主线程退出时自动结束
                    kb_thread.start()
                    app_logger.info(f"Started background thread to store {len(document_list)} documents in knowledge base")
                return jsonify({"message": f"Successfully added {len(df)} documents from {filename}"}), 201
        else:
            app_logger.error("Invalid file type")
            return jsonify({"error": "Invalid file type, only .xlsx and .xls are allowed"}), 400
    except Exception as e:
        app_logger.error(f"Error in uploading Excel file: {str(e)}")
        return jsonify({"error": str(e)}), 500
