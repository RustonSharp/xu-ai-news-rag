from flask import Blueprint, request, jsonify
from sqlmodel import Session
from core.dependencies import get_db_session_sync
from services.document_service import DocumentService
from services.analytics_service import AnalyticsService
from schemas.document_schema import (
    DocumentSearchParams, DocumentUploadResponse
)
from schemas.analytics_schema import ClusterAnalysisRequest
from utils.logging_config import app_logger
from werkzeug.utils import secure_filename
import pandas as pd
import json

# 创建蓝图
document_bp = Blueprint('document', __name__, url_prefix='/api/documents')

def get_document_service():
    """获取文档服务实例"""
    session = get_db_session_sync()
    return DocumentService(session)

def get_analytics_service():
    """获取分析服务实例"""
    session = get_db_session_sync()
    return AnalyticsService(session)

# 获取聚类分布
@document_bp.route('cluster_analysis', methods=['GET'])
def get_cluster_analysis():
    try:
        app_logger.info("GET /api/documents/cluster_analysis - Request received")
        
        # 获取分析服务并执行聚类分析
        analytics_service = get_analytics_service()
        request_data = ClusterAnalysisRequest(force_refresh=True)
        result = analytics_service.perform_cluster_analysis(request_data)
        
        # 返回聚类结果
        return jsonify({
            "clusters": [
                {
                    "id": cluster.cluster_id,
                    "percentage": cluster.percentage,
                    "keyword": cluster.cluster_label
                }
                for cluster in result.clusters
            ]
        })
    except Exception as e:
        app_logger.error(f"Error in cluster analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 返回最新的一次聚类分析结果
@document_bp.route('cluster_analysis/latest', methods=['GET'])
def get_latest_cluster_analysis():
    try:
        app_logger.info("GET /api/documents/cluster_analysis/latest - Request received")
        
        # 获取分析服务并获取最新聚类分析
        analytics_service = get_analytics_service()
        result = analytics_service.get_latest_cluster_analysis()
        
        # 返回聚类结果
        return jsonify({
            "clusters": [
                {
                    "id": cluster.cluster_id,
                    "percentage": cluster.percentage,
                    "keyword": cluster.cluster_label
                }
                for cluster in result.clusters
            ]
        })
    except Exception as e:
        app_logger.error(f"Error getting latest cluster analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 获取所有文档
@document_bp.route('', methods=['GET'])
def get_documents():
    try:
        app_logger.info("GET /api/documents - Request received")
        
        # 创建搜索参数
        search_params = DocumentSearchParams(
            page=1,
            size=1000  # Get all documents
        )
        
        # 获取文档服务并查询文档
        document_service = get_document_service()
        result = document_service.get_documents(search_params)
        
        # 转换为前端期望的格式
        documents_data = []
        for doc in result.items:
            documents_data.append({
                "id": doc.id,
                "title": doc.title,
                "link": doc.link,
                "description": doc.description,
                "pub_date": doc.pub_date.isoformat() if doc.pub_date else None,
                "author": doc.author,
                "tags": doc.tags.split(",") if doc.tags else [],
                "source_id": doc.source_id,
                "crawled_at": doc.crawled_at.isoformat()
            })
        
        return jsonify(documents_data)
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
        
        # 创建搜索参数
        search_params = DocumentSearchParams(
            page=page,
            size=size,
            search=search if search else None,
            doc_type=doc_type if doc_type else None,
            source=source if source else None,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None
        )
        
        # 获取文档服务并查询文档
        document_service = get_document_service()
        result = document_service.get_documents(search_params)
        
        # 转换为前端期望的格式
        items_data = []
        for doc in result.items:
            items_data.append({
                "id": doc.id,
                "title": doc.title,
                "link": doc.link,
                "description": doc.description,
                "pub_date": doc.pub_date.isoformat() if doc.pub_date else None,
                "author": doc.author,
                "tags": doc.tags.split(",") if doc.tags else [],
                "source_id": doc.source_id,
                "crawled_at": doc.crawled_at.isoformat()
            })
        
        return jsonify({
            "items": items_data,
            "total": result.total,
            "page": result.page,
            "size": result.size,
            "total_pages": result.total_pages
        })
    except Exception as e:
        app_logger.error(f"Error getting documents: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 获取单个文档
@document_bp.route('/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    try:
        app_logger.info(f"GET /api/documents/{doc_id} - Request received")
        
        # 获取文档服务并查询文档
        document_service = get_document_service()
        document = document_service.get_document(doc_id)
        
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
            "source_id": document.source_id,
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
        
        # 获取文档服务并查询特定RSS源的文档
        document_service = get_document_service()
        documents = document_service.get_documents_by_source(source_id)
        
        # 转换为前端期望的格式
        documents_data = []
        for doc in documents:
            documents_data.append({
                "id": doc.id,
                "title": doc.title,
                "link": doc.link,
                "description": doc.description,
                "pub_date": doc.pub_date.isoformat() if doc.pub_date else None,
                "author": doc.author,
                "tags": doc.tags.split(",") if doc.tags else [],
                "source_id": doc.source_id,
                "crawled_at": doc.crawled_at.isoformat()
            })
        
        return jsonify(documents_data)
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
            
            # Convert DataFrame to list of dictionaries
            documents_data = []
            for _, row in df.iterrows():
                doc_data = {
                    "title": row.get('title', ''),
                    "link": row.get('link', ''),
                    "description": row.get('description', ''),
                    "pub_date": row.get('pub_date', None),
                    "author": row.get('author', ''),
                    "tags": ','.join(map(str, row.get('tags', []))) if isinstance(row.get('tags', []), list) else str(row.get('tags', ''))
                }
                documents_data.append(doc_data)
            
            # Process documents using service
            document_service = get_document_service()
            result = document_service.upload_excel_documents(documents_data, filename)
            
            return jsonify({
                "message": result["message"],
                "documents_processed": result["documents_processed"],
                "success": result["success"]
            }), 201
        else:
            app_logger.error("Invalid file type")
            return jsonify({"error": "Invalid file type, only .xlsx and .xls are allowed"}), 400
    except Exception as e:
        app_logger.error(f"Error in uploading Excel file: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Batch delete documents
@document_bp.route('/batch', methods=['DELETE'])
def batch_delete_documents():
    try:
        app_logger.info("DELETE /api/documents/batch - Request received")
        
        # Get document IDs from request body
        data = request.get_json()
        if not data or 'ids' not in data:
            app_logger.error("No document IDs provided")
            return jsonify({"error": "No document IDs provided"}), 400
        
        document_ids = data['ids']
        if not isinstance(document_ids, list) or len(document_ids) == 0:
            app_logger.error("Invalid document IDs format")
            return jsonify({"error": "Invalid document IDs format"}), 400
        
        # Process documents using service
        document_service = get_document_service()
        result = document_service.batch_delete_documents(document_ids)
        
        return jsonify({
            "message": result["message"],
            "deleted_count": result["deleted_count"],
            "success": result["success"]
        }), 200
        
    except Exception as e:
        app_logger.error(f"Error in batch deleting documents: {str(e)}")
        return jsonify({"error": str(e)}), 500
