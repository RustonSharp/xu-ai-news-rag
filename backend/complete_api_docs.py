"""
完整的API文档生成器
包含所有API端点的详细文档
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_restx import Api, Resource, fields
from flask_cors import CORS

def create_complete_docs_app():
    """创建包含所有API的完整文档"""
    app = Flask(__name__)
    CORS(app)
    
    # 配置API文档
    api = Api(
        app,
        version='1.0',
        title='AI News RAG API - 完整文档',
        description='''
        # AI News RAG API 完整文档
        
        智能新闻检索增强生成系统的完整API文档，包含所有端点。
        
        ## 🚀 功能模块
        - **🔐 认证模块**: 用户注册、登录、JWT管理
        - **📰 数据源模块**: RSS/Web/File数据源管理
        - **📄 文档模块**: 文档CRUD、Excel导入、聚类分析
        - **🤖 助手模块**: AI智能查询
        - **⏰ 调度器模块**: 定时任务控制
        - **📊 分析模块**: 数据统计和聚类分析
        
        ## 🔑 认证方式
        在请求头中添加：`Authorization: Bearer <your_jwt_token>`
        ''',
        doc='/api/docs/',
        prefix='/api',
        authorizations={
            'Bearer Auth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'JWT token格式: Bearer <token>'
            }
        }
    )
    
    # 定义命名空间
    auth_ns = api.namespace('auth', description='🔐 用户认证相关API')
    source_ns = api.namespace('sources', description='📰 数据源管理API')
    document_ns = api.namespace('documents', description='📄 文档管理API')
    assistant_ns = api.namespace('assistant', description='🤖 AI助手API')
    scheduler_ns = api.namespace('scheduler', description='⏰ 调度器API')
    analytics_ns = api.namespace('analytics', description='📊 数据分析API')
    
    # ==================== 数据模型定义 ====================
    
    # 用户相关模型
    user_model = api.model('User', {
        'id': fields.Integer(description='用户ID'),
        'email': fields.String(required=True, description='邮箱地址'),
        'username': fields.String(required=True, description='用户名'),
        'role': fields.String(description='用户角色', default='user'),
        'is_active': fields.Boolean(description='是否激活'),
        'createdAt': fields.DateTime(description='创建时间')
    })
    
    login_request = api.model('LoginRequest', {
        'email': fields.String(required=True, description='邮箱地址', example='user@example.com'),
        'password': fields.String(required=True, description='密码', example='password123')
    })
    
    login_response = api.model('LoginResponse', {
        'code': fields.Integer(description='状态码'),
        'message': fields.String(description='消息'),
        'data': fields.Nested(api.model('LoginData', {
            'user': fields.Nested(user_model),
            'token': fields.String(description='访问令牌'),
            'refreshToken': fields.String(description='刷新令牌')
        }))
    })
    
    # 数据源相关模型
    source_model = api.model('Source', {
        'id': fields.Integer(description='数据源ID'),
        'name': fields.String(required=True, description='数据源名称'),
        'url': fields.String(required=True, description='数据源URL'),
        'source_type': fields.String(required=True, description='数据源类型', 
                                   enum=['rss', 'web', 'file']),
        'interval': fields.String(description='同步间隔', 
                                enum=['SIX_HOUR', 'TWELVE_HOUR', 'ONE_DAY', 'THREE_DAY', 'WEEKLY']),
        'is_paused': fields.Boolean(description='是否暂停'),
        'is_active': fields.Boolean(description='是否激活'),
        'last_sync': fields.DateTime(description='最后同步时间'),
        'next_sync': fields.DateTime(description='下次同步时间'),
        'document_count': fields.Integer(description='文档数量'),
        'description': fields.String(description='描述'),
        'tags': fields.String(description='标签'),
        'created_at': fields.DateTime(description='创建时间'),
        'updated_at': fields.DateTime(description='更新时间')
    })
    
    source_create = api.model('SourceCreate', {
        'name': fields.String(required=True, description='数据源名称'),
        'url': fields.String(required=True, description='数据源URL'),
        'source_type': fields.String(required=True, description='数据源类型', 
                                   enum=['rss', 'web', 'file']),
        'interval': fields.String(description='同步间隔', default='ONE_DAY'),
        'description': fields.String(description='描述'),
        'tags': fields.String(description='标签'),
        'config': fields.Raw(description='配置信息')
    })
    
    source_update = api.model('SourceUpdate', {
        'name': fields.String(description='数据源名称'),
        'url': fields.String(description='数据源URL'),
        'source_type': fields.String(description='数据源类型'),
        'interval': fields.String(description='同步间隔'),
        'description': fields.String(description='描述'),
        'tags': fields.String(description='标签'),
        'config': fields.Raw(description='配置信息'),
        'is_paused': fields.Boolean(description='是否暂停'),
        'is_active': fields.Boolean(description='是否激活')
    })
    
    # 文档相关模型
    document_model = api.model('Document', {
        'id': fields.Integer(description='文档ID'),
        'title': fields.String(description='标题'),
        'link': fields.String(description='链接'),
        'description': fields.String(description='描述'),
        'pub_date': fields.DateTime(description='发布日期'),
        'author': fields.String(description='作者'),
        'tags': fields.List(fields.String, description='标签'),
        'source_id': fields.Integer(description='数据源ID'),
        'crawled_at': fields.DateTime(description='抓取时间')
    })
    
    document_page_response = api.model('DocumentPageResponse', {
        'items': fields.List(fields.Nested(document_model)),
        'total': fields.Integer(description='总数量'),
        'page': fields.Integer(description='当前页'),
        'size': fields.Integer(description='每页大小'),
        'total_pages': fields.Integer(description='总页数')
    })
    
    # 助手相关模型
    assistant_query = api.model('AssistantQuery', {
        'query': fields.String(required=True, description='查询内容', 
                              example='人工智能在医疗领域的应用')
    })
    
    assistant_response = api.model('AssistantResponse', {
        'query': fields.String(description='原始查询'),
        'response': fields.String(description='AI回答'),
        'answer': fields.String(description='答案'),
        'sources': fields.List(fields.Raw, description='来源信息'),
        'origin': fields.String(description='信息来源', 
                              enum=['knowledge_base', 'online_search']),
        'status': fields.String(description='处理状态')
    })
    
    # 调度器相关模型
    scheduler_status = api.model('SchedulerStatus', {
        'running': fields.Boolean(description='是否运行中'),
        'rss_sources': fields.List(fields.Nested(api.model('RSSSourceStatus', {
            'id': fields.Integer(description='RSS源ID'),
            'name': fields.String(description='RSS源名称'),
            'url': fields.String(description='RSS源URL'),
            'interval': fields.String(description='同步间隔'),
            'is_paused': fields.Boolean(description='是否暂停'),
            'active': fields.Boolean(description='是否活跃')
        })))
    })
    
    # 分析相关模型
    cluster_analysis_request = api.model('ClusterAnalysisRequest', {
        'force_refresh': fields.Boolean(description='强制刷新', default=False)
    })
    
    cluster_analysis_response = api.model('ClusterAnalysisResponse', {
        'clusters': fields.List(fields.Nested(api.model('Cluster', {
            'id': fields.Integer(description='聚类ID'),
            'percentage': fields.Float(description='百分比'),
            'keyword': fields.String(description='关键词')
        }))),
        'total_documents': fields.Integer(description='总文档数'),
        'total_clusters': fields.Integer(description='总聚类数'),
        'silhouette_score': fields.Float(description='轮廓系数'),
        'clustering_method': fields.String(description='聚类方法'),
        'analysis_date': fields.String(description='分析日期')
    })
    
    # ==================== 认证API ====================
    
    @auth_ns.route('/login')
    class Login(Resource):
        @auth_ns.expect(login_request)
        @auth_ns.marshal_with(login_response)
        @auth_ns.doc('user_login', description='用户登录，返回JWT令牌')
        def post(self):
            """
            用户登录
            
            使用邮箱和密码登录系统，成功后返回JWT访问令牌和刷新令牌。
            
            **示例请求：**
            ```json
            {
                "email": "user@example.com",
                "password": "password123"
            }
            ```
            """
            pass
    
    @auth_ns.route('/register')
    class Register(Resource):
        @auth_ns.expect(login_request)
        @auth_ns.doc('user_register', description='用户注册')
        def post(self):
            """
            用户注册
            
            创建新的用户账号。
            """
            pass
    
    @auth_ns.route('/refresh')
    class Refresh(Resource):
        @auth_ns.expect(api.model('RefreshRequest', {
            'refreshToken': fields.String(required=True, description='刷新令牌')
        }))
        @auth_ns.doc('refresh_token', description='刷新访问令牌')
        def post(self):
            """
            刷新访问令牌
            
            使用刷新令牌获取新的访问令牌。
            """
            pass
    
    @auth_ns.route('/logout')
    class Logout(Resource):
        @auth_ns.doc('user_logout', description='用户登出')
        def post(self):
            """
            用户登出
            
            登出当前用户。
            """
            pass
    
    @auth_ns.route('/profile')
    class Profile(Resource):
        @auth_ns.marshal_with(user_model)
        @auth_ns.doc('get_profile', description='获取用户信息', security='Bearer Auth')
        def get(self):
            """
            获取用户信息
            
            获取当前登录用户的详细信息。
            """
            pass
        
        @auth_ns.expect(user_model)
        @auth_ns.marshal_with(user_model)
        @auth_ns.doc('update_profile', description='更新用户信息', security='Bearer Auth')
        def put(self):
            """
            更新用户信息
            
            更新当前登录用户的信息。
            """
            pass
    
    # ==================== 数据源API ====================
    
    @source_ns.route('/')
    class SourceList(Resource):
        @source_ns.marshal_list_with(source_model)
        @source_ns.doc('get_sources', description='获取数据源列表')
        def get(self):
            """
            获取数据源列表
            
            获取所有数据源的列表，支持分页和筛选。
            
            **查询参数：**
            - page: 页码 (默认: 1)
            - size: 每页大小 (默认: 20)
            - search: 搜索关键词
            - type: 数据源类型 (rss/web/file)
            - interval: 同步间隔
            - is_paused: 是否暂停
            - is_active: 是否激活
            - tags: 标签筛选
            """
            pass
        
        @source_ns.expect(source_create)
        @source_ns.marshal_with(source_model)
        @source_ns.doc('create_source', description='创建新数据源')
        def post(self):
            """
            创建新数据源
            
            添加新的RSS、Web或File类型数据源。
            """
            pass
    
    @source_ns.route('/<int:source_id>')
    class SourceDetail(Resource):
        @source_ns.marshal_with(source_model)
        @source_ns.doc('get_source', description='获取数据源详情')
        def get(self, source_id):
            """
            获取数据源详情
            
            根据ID获取特定数据源的详细信息。
            """
            pass
        
        @source_ns.expect(source_update)
        @source_ns.marshal_with(source_model)
        @source_ns.doc('update_source', description='更新数据源')
        def put(self, source_id):
            """
            更新数据源
            
            更新指定数据源的信息。
            """
            pass
        
        @source_ns.doc('delete_source', description='删除数据源')
        def delete(self, source_id):
            """
            删除数据源
            
            删除指定的数据源。
            """
            pass
    
    @source_ns.route('/<int:source_id>/collect')
    class SourceCollect(Resource):
        @source_ns.doc('trigger_collection', description='触发数据源采集')
        def post(self, source_id):
            """
            触发数据源采集
            
            立即触发指定数据源的数据采集。
            """
            pass
    
    @source_ns.route('/stats')
    class SourceStats(Resource):
        @source_ns.doc('get_source_stats', description='获取数据源统计信息')
        def get(self):
            """
            获取数据源统计信息
            
            获取数据源的统计信息，包括总数、类型分布等。
            """
            pass
    
    @source_ns.route('/due-for-sync')
    class SourcesDueForSync(Resource):
        @source_ns.doc('get_sources_due_for_sync', description='获取需要同步的数据源')
        def get(self):
            """
            获取需要同步的数据源
            
            获取所有需要同步的数据源列表。
            """
            pass
    
    # ==================== 文档API ====================
    
    @document_ns.route('/')
    class DocumentList(Resource):
        @document_ns.marshal_list_with(document_model)
        @document_ns.doc('get_documents', description='获取文档列表')
        def get(self):
            """
            获取文档列表
            
            获取所有文档的列表。
            """
            pass
    
    @document_ns.route('/page')
    class DocumentPage(Resource):
        @document_ns.marshal_with(document_page_response)
        @document_ns.doc('get_documents_page', description='分页获取文档')
        def get(self):
            """
            分页获取文档
            
            支持分页、搜索和筛选的文档列表。
            
            **查询参数：**
            - page: 页码 (默认: 1)
            - size: 每页大小 (默认: 20)
            - search: 搜索关键词
            - type: 文档类型
            - source: 数据源筛选
            - start: 开始日期
            - end: 结束日期
            """
            pass
    
    @document_ns.route('/<int:doc_id>')
    class DocumentDetail(Resource):
        @document_ns.marshal_with(document_model)
        @document_ns.doc('get_document', description='获取文档详情')
        def get(self, doc_id):
            """
            获取文档详情
            
            根据ID获取特定文档的详细信息。
            """
            pass
    
    @document_ns.route('/get_documents_by_source_id/<int:source_id>')
    class DocumentsBySource(Resource):
        @document_ns.marshal_list_with(document_model)
        @document_ns.doc('get_documents_by_source', description='获取指定数据源的文档')
        def get(self, source_id):
            """
            获取指定数据源的文档
            
            获取特定数据源的所有文档。
            """
            pass
    
    @document_ns.route('/upload_excel')
    class DocumentUpload(Resource):
        @document_ns.doc('upload_excel', description='上传Excel文件导入文档')
        def post(self):
            """
            上传Excel文件导入文档
            
            通过Excel文件批量导入文档。
            
            **支持格式：** .xlsx, .xls
            **最大文件大小：** 10MB
            """
            pass
    
    @document_ns.route('/batch')
    class DocumentBatch(Resource):
        @document_ns.doc('batch_delete_documents', description='批量删除文档')
        def delete(self):
            """
            批量删除文档
            
            根据文档ID列表批量删除文档。
            
            **请求体：**
            ```json
            {
                "ids": [1, 2, 3, 4, 5]
            }
            ```
            """
            pass
    
    @document_ns.route('/cluster_analysis')
    class DocumentClusterAnalysis(Resource):
        @document_ns.marshal_with(cluster_analysis_response)
        @document_ns.doc('get_cluster_analysis', description='执行聚类分析')
        def get(self):
            """
            执行聚类分析
            
            对文档进行聚类分析，自动分类。
            """
            pass
    
    @document_ns.route('/cluster_analysis/latest')
    class DocumentLatestClusterAnalysis(Resource):
        @document_ns.marshal_with(cluster_analysis_response)
        @document_ns.doc('get_latest_cluster_analysis', description='获取最新聚类分析结果')
        def get(self):
            """
            获取最新聚类分析结果
            
            获取最近一次的聚类分析结果。
            """
            pass
    
    # ==================== 助手API ====================
    
    @assistant_ns.route('/query')
    class AssistantQuery(Resource):
        @assistant_ns.expect(assistant_query)
        @assistant_ns.marshal_with(assistant_response)
        @assistant_ns.doc('query_assistant', description='提交查询到AI助手')
        def post(self):
            """
            提交查询到AI助手
            
            向AI助手提交问题，获取智能回答。
            
            **功能特性：**
            - 优先使用本地知识库
            - 自动fallback到在线搜索
            - 提供来源引用
            - 支持中文查询
            """
            pass
    
    @assistant_ns.route('/health')
    class AssistantHealth(Resource):
        @assistant_ns.doc('assistant_health', description='检查助手服务健康状态')
        def get(self):
            """
            检查助手服务健康状态
            
            检查AI助手服务的运行状态。
            """
            pass
    
    # ==================== 调度器API ====================
    
    @scheduler_ns.route('/status')
    class SchedulerStatus(Resource):
        @scheduler_ns.marshal_with(scheduler_status)
        @scheduler_ns.doc('get_scheduler_status', description='获取调度器状态')
        def get(self):
            """
            获取调度器状态
            
            获取调度器的运行状态和RSS源状态。
            """
            pass
    
    @scheduler_ns.route('/start')
    class SchedulerStart(Resource):
        @scheduler_ns.doc('start_scheduler', description='启动调度器')
        def post(self):
            """
            启动调度器
            
            启动数据采集调度器。
            """
            pass
    
    @scheduler_ns.route('/stop')
    class SchedulerStop(Resource):
        @scheduler_ns.doc('stop_scheduler', description='停止调度器')
        def post(self):
            """
            停止调度器
            
            停止数据采集调度器。
            """
            pass
    
    @scheduler_ns.route('/fetch/<int:rss_id>')
    class SchedulerFetch(Resource):
        @scheduler_ns.doc('fetch_rss_now', description='立即获取指定RSS源的新闻')
        def post(self, rss_id):
            """
            立即获取指定RSS源的新闻
            
            立即触发指定RSS源的数据采集。
            """
            pass
    
    # ==================== 分析API ====================
    
    @analytics_ns.route('/')
    class Analytics(Resource):
        @analytics_ns.doc('get_analytics', description='获取分析数据')
        def get(self):
            """
            获取分析数据
            
            获取最新的分析数据。
            """
            pass
    
    @analytics_ns.route('/cluster')
    class AnalyticsCluster(Resource):
        @analytics_ns.expect(cluster_analysis_request)
        @analytics_ns.marshal_with(cluster_analysis_response)
        @analytics_ns.doc('perform_cluster_analysis', description='执行聚类分析')
        def post(self):
            """
            执行聚类分析
            
            对文档集合执行聚类分析。
            
            **请求参数：**
            - force_refresh: 是否强制刷新分析结果
            """
            pass
    
    return app

if __name__ == '__main__':
    app = create_complete_docs_app()
    print("🚀 启动完整API文档服务器...")
    print("📖 文档地址: http://localhost:5002/api/docs/")
    print("🛑 按 Ctrl+C 停止服务器")
    app.run(host='0.0.0.0', port=5002, debug=True)
