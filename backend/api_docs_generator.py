"""
API文档自动生成器
使用Flask-RESTX生成交互式API文档
"""
from flask import Flask
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from apis.source import source_bp
from apis.document import document_bp
from apis.auth import auth_bp
from apis.assistant import assistant_bp
from apis.scheduler import scheduler_bp
from apis.analytics import analytics_bp
from utils.init_sqlite import init_db
from config.settings import settings

def create_docs_app():
    """创建带API文档的Flask应用"""
    # 初始化数据库
    init_db()
    
    app = Flask(__name__)
    CORS(app)
    
    # 配置API文档
    api = Api(
        app,
        version='1.0',
        title='AI News RAG API',
        description='''
        # AI News RAG API 文档
        
        智能新闻检索增强生成系统API文档
        
        ## 功能特性
        - 🔐 JWT用户认证
        - 📰 多源数据采集（RSS/Web/File）
        - 🤖 AI智能助手
        - 📊 文档聚类分析
        - ⏰ 定时任务调度
        
        ## 快速开始
        1. 注册用户账号
        2. 登录获取访问令牌
        3. 添加数据源
        4. 查询AI助手
        
        ## 认证方式
        在请求头中添加：`Authorization: Bearer <your_token>`
        ''',
        doc='/api/docs/',  # Swagger UI路径
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
    auth_ns = api.namespace('auth', description='用户认证相关API')
    source_ns = api.namespace('sources', description='数据源管理API')
    document_ns = api.namespace('documents', description='文档管理API')
    assistant_ns = api.namespace('assistant', description='AI助手API')
    scheduler_ns = api.namespace('scheduler', description='调度器API')
    analytics_ns = api.namespace('analytics', description='数据分析API')
    
    # 定义数据模型
    user_model = api.model('User', {
        'id': fields.Integer(description='用户ID'),
        'email': fields.String(required=True, description='邮箱地址'),
        'username': fields.String(required=True, description='用户名'),
        'role': fields.String(description='用户角色'),
        'createdAt': fields.DateTime(description='创建时间')
    })
    
    login_model = api.model('LoginRequest', {
        'email': fields.String(required=True, description='邮箱地址'),
        'password': fields.String(required=True, description='密码')
    })
    
    login_response_model = api.model('LoginResponse', {
        'code': fields.Integer(description='状态码'),
        'message': fields.String(description='消息'),
        'data': fields.Nested(api.model('LoginData', {
            'user': fields.Nested(user_model),
            'token': fields.String(description='访问令牌'),
            'refreshToken': fields.String(description='刷新令牌')
        }))
    })
    
    source_model = api.model('Source', {
        'id': fields.Integer(description='数据源ID'),
        'name': fields.String(required=True, description='数据源名称'),
        'url': fields.String(required=True, description='数据源URL'),
        'source_type': fields.String(required=True, description='数据源类型', enum=['rss', 'web', 'file']),
        'interval': fields.String(description='同步间隔', enum=['SIX_HOUR', 'TWELVE_HOUR', 'ONE_DAY', 'THREE_DAY', 'WEEKLY']),
        'is_paused': fields.Boolean(description='是否暂停'),
        'is_active': fields.Boolean(description='是否激活'),
        'description': fields.String(description='描述'),
        'tags': fields.String(description='标签')
    })
    
    source_create_model = api.model('SourceCreate', {
        'name': fields.String(required=True, description='数据源名称'),
        'url': fields.String(required=True, description='数据源URL'),
        'source_type': fields.String(required=True, description='数据源类型', enum=['rss', 'web', 'file']),
        'interval': fields.String(description='同步间隔', default='ONE_DAY'),
        'description': fields.String(description='描述'),
        'tags': fields.String(description='标签'),
        'config': fields.Raw(description='配置信息')
    })
    
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
    
    assistant_query_model = api.model('AssistantQuery', {
        'query': fields.String(required=True, description='查询内容')
    })
    
    assistant_response_model = api.model('AssistantResponse', {
        'query': fields.String(description='原始查询'),
        'response': fields.String(description='AI回答'),
        'sources': fields.List(fields.Raw, description='来源信息'),
        'origin': fields.String(description='信息来源', enum=['knowledge_base', 'online_search']),
        'status': fields.String(description='处理状态')
    })
    
    # 认证API文档
    @auth_ns.route('/login')
    class Login(Resource):
        @auth_ns.expect(login_model)
        @auth_ns.marshal_with(login_response_model)
        @auth_ns.doc('user_login', description='用户登录，返回访问令牌和刷新令牌')
        def post(self):
            """
            用户登录
            
            使用邮箱和密码登录，成功后返回JWT访问令牌和刷新令牌。
            
            **示例请求：**
            ```json
            {
                "email": "user@example.com",
                "password": "password123"
            }
            ```
            
            **示例响应：**
            ```json
            {
                "code": 200,
                "message": "Login successful",
                "data": {
                    "user": {
                        "id": 1,
                        "email": "user@example.com",
                        "username": "user",
                        "role": "user"
                    },
                    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                }
            }
            ```
            """
            pass
    
    @auth_ns.route('/register')
    class Register(Resource):
        @auth_ns.expect(login_model)
        def post(self):
            """用户注册"""
            pass
    
    @auth_ns.route('/refresh')
    class Refresh(Resource):
        @auth_ns.expect(api.model('RefreshRequest', {
            'refreshToken': fields.String(required=True, description='刷新令牌')
        }))
        def post(self):
            """刷新访问令牌"""
            pass
    
    @auth_ns.route('/profile')
    class Profile(Resource):
        @auth_ns.marshal_with(user_model)
        def get(self):
            """获取用户信息"""
            pass
        
        @auth_ns.expect(user_model)
        @auth_ns.marshal_with(user_model)
        def put(self):
            """更新用户信息"""
            pass
    
    # 数据源API文档
    @source_ns.route('/')
    class SourceList(Resource):
        @source_ns.marshal_list_with(source_model)
        def get(self):
            """获取数据源列表"""
            pass
        
        @source_ns.expect(source_create_model)
        @source_ns.marshal_with(source_model)
        def post(self):
            """创建新数据源"""
            pass
    
    @source_ns.route('/<int:source_id>')
    class SourceDetail(Resource):
        @source_ns.marshal_with(source_model)
        def get(self, source_id):
            """获取数据源详情"""
            pass
        
        @source_ns.expect(source_model)
        @source_ns.marshal_with(source_model)
        def put(self, source_id):
            """更新数据源"""
            pass
        
        def delete(self, source_id):
            """删除数据源"""
            pass
    
    @source_ns.route('/<int:source_id>/collect')
    class SourceCollect(Resource):
        def post(self, source_id):
            """触发数据源采集"""
            pass
    
    @source_ns.route('/stats')
    class SourceStats(Resource):
        def get(self):
            """获取数据源统计信息"""
            pass
    
    # 文档API文档
    @document_ns.route('/')
    class DocumentList(Resource):
        @document_ns.marshal_list_with(document_model)
        def get(self):
            """获取文档列表"""
            pass
    
    @document_ns.route('/page')
    class DocumentPage(Resource):
        @document_ns.marshal_with(api.model('DocumentPageResponse', {
            'items': fields.List(fields.Nested(document_model)),
            'total': fields.Integer(description='总数量'),
            'page': fields.Integer(description='当前页'),
            'size': fields.Integer(description='每页大小'),
            'total_pages': fields.Integer(description='总页数')
        }))
        def get(self):
            """分页获取文档"""
            pass
    
    @document_ns.route('/<int:doc_id>')
    class DocumentDetail(Resource):
        @document_ns.marshal_with(document_model)
        def get(self, doc_id):
            """获取文档详情"""
            pass
    
    @document_ns.route('/upload_excel')
    class DocumentUpload(Resource):
        def post(self):
            """上传Excel文件导入文档"""
            pass
    
    @document_ns.route('/cluster_analysis')
    class ClusterAnalysis(Resource):
        def get(self):
            """执行聚类分析"""
            pass
    
    # 助手API文档
    @assistant_ns.route('/query')
    class AssistantQuery(Resource):
        @assistant_ns.expect(assistant_query_model)
        @assistant_ns.marshal_with(assistant_response_model)
        def post(self):
            """提交查询到AI助手"""
            pass
    
    @assistant_ns.route('/health')
    class AssistantHealth(Resource):
        def get(self):
            """检查助手服务健康状态"""
            pass
    
    # 调度器API文档
    @scheduler_ns.route('/status')
    class SchedulerStatus(Resource):
        def get(self):
            """获取调度器状态"""
            pass
    
    @scheduler_ns.route('/start')
    class SchedulerStart(Resource):
        def post(self):
            """启动调度器"""
            pass
    
    @scheduler_ns.route('/stop')
    class SchedulerStop(Resource):
        def post(self):
            """停止调度器"""
            pass
    
    @scheduler_ns.route('/fetch')
    class SchedulerFetch(Resource):
        def post(self):
            """触发立即数据采集"""
            pass
    
    # 分析API文档
    @analytics_ns.route('/stats')
    class AnalyticsStats(Resource):
        def get(self):
            """获取分析统计信息"""
            pass
    
    @analytics_ns.route('/cluster_analysis')
    class AnalyticsCluster(Resource):
        def get(self):
            """获取聚类分析结果"""
            pass
        
        def post(self):
            """触发新的聚类分析"""
            pass
    
    return app

if __name__ == '__main__':
    app = create_docs_app()
    app.run(host=settings.APP_HOST, port=5002, debug=settings.APP_DEBUG)
