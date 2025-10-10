"""
测试配置文件
提供测试用的fixtures和配置
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入服务模块
from services.assistant_service import AssistantService
from services.knowledge_base.vector_store_service import VectorStoreService
from services.search.online_search_service import OnlineSearchService
from services.auth_service import AuthService
from services.document_service import DocumentService
from services.source_service import SourceService
from services.scheduler_service import SchedulerService


@pytest.fixture(scope="session")
def test_config():
    """测试配置"""
    return {
        "test_db_path": ":memory:",  # 使用内存数据库
        "test_embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "test_rerank_model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
        "test_tavily_api_key": "test_key",
        "test_ollama_model": "qwen2.5:3b"
    }


@pytest.fixture(scope="function")
def temp_dir():
    """临时目录fixture"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def mock_llm():
    """模拟LLM"""
    mock_llm = Mock()
    mock_llm.invoke.return_value = "测试回答"
    return mock_llm


@pytest.fixture(scope="function")
def mock_knowledge_base_tool():
    """模拟知识库工具"""
    mock_tool = Mock()
    mock_tool.invoke.return_value = [
        {
            "id": 1,
            "content": "测试文档内容",
            "metadata": {
                "title": "测试标题",
                "source": "test_doc",
                "pub_date": "2025-01-01"
            }
        }
    ]
    return mock_tool


@pytest.fixture(scope="function")
def mock_online_search_tool():
    """模拟在线搜索工具"""
    mock_tool = Mock()
    mock_tool.invoke.return_value = [
        {
            "content": "在线搜索结果",
            "title": "在线搜索标题",
            "url": "https://example.com"
        }
    ]
    return mock_tool


@pytest.fixture(scope="function")
def sample_documents():
    """测试文档数据"""
    return [
        {
            "id": 1,
            "content": "人工智能在医疗领域的应用越来越广泛，包括医学影像诊断、药物发现等。",
            "metadata": {
                "title": "AI医疗应用",
                "source": "medical_news",
                "pub_date": "2025-01-01",
                "tags": "AI,医疗"
            }
        },
        {
            "id": 2,
            "content": "最新的股市行情显示，科技股表现强劲，投资者信心增强。",
            "metadata": {
                "title": "科技股行情",
                "source": "finance_news",
                "pub_date": "2025-01-02",
                "tags": "股市,科技"
            }
        }
    ]


@pytest.fixture(scope="function")
def mock_embeddings():
    """模拟嵌入模型"""
    mock_embeddings = Mock()
    mock_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3] * 384]  # 模拟384维向量
    mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3] * 384
    return mock_embeddings


@pytest.fixture(scope="function")
def mock_reranker():
    """模拟重排模型"""
    mock_reranker = Mock()
    mock_reranker.predict.return_value = [0.8, 0.6, 0.4]  # 模拟相关性分数
    return mock_reranker


@pytest.fixture(scope="function")
def test_app():
    """测试Flask应用"""
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture(scope="function")
def test_client(test_app):
    """测试客户端"""
    return test_app.test_client()


@pytest.fixture(scope="function")
def auth_headers():
    """认证头"""
    return {
        'Authorization': 'Bearer test_token',
        'Content-Type': 'application/json'
    }


@pytest.fixture(scope="function")
def mock_database_session():
    """模拟数据库会话"""
    mock_session = Mock()
    
    # 创建Mock查询结果
    mock_query_result = Mock()
    mock_query_result.all.return_value = []
    mock_query_result.first.return_value = None
    mock_query_result.one.return_value = 0
    
    # 设置exec方法的返回值 - 让它返回一个可迭代的Mock对象
    mock_session.exec.return_value = mock_query_result
    
    # 让exec方法本身也返回可迭代对象（用于直接调用list()的情况）
    def mock_exec(statement):
        # 返回一个可迭代的Mock对象
        iterable_mock = Mock()
        iterable_mock.__iter__ = Mock(return_value=iter([]))
        iterable_mock.all.return_value = []
        iterable_mock.first.return_value = None
        iterable_mock.one.return_value = 0
        return iterable_mock
    
    # 不要覆盖exec方法，让测试可以设置return_value
    # mock_session.exec = mock_exec
    
    # 其他方法
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None
    mock_session.delete.return_value = None
    
    return mock_session


@pytest.fixture(scope="function")
def mock_user():
    """模拟用户"""
    mock_user = Mock()
    mock_user.id = 1
    mock_user.username = "test_user"
    mock_user.email = "test@example.com"
    mock_user.is_active = True
    return mock_user


@pytest.fixture(scope="function")
def mock_document():
    """模拟文档"""
    mock_doc = Mock()
    mock_doc.id = 1
    mock_doc.title = "测试文档"
    mock_doc.content = "测试内容"
    mock_doc.link = "http://test.com"
    mock_doc.description = "测试描述"
    mock_doc.pub_date = None
    mock_doc.author = "测试作者"
    mock_doc.tags = "tag1,tag2"
    mock_doc.source_id = 1
    from datetime import datetime
    mock_doc.crawled_at = datetime(2025, 1, 1, 12, 0, 0)
    return mock_doc


@pytest.fixture(scope="function")
def mock_rss_source():
    """模拟RSS源"""
    from models.source import SourceType, SourceInterval
    from datetime import datetime
    
    mock_source = Mock()
    mock_source.id = 1
    mock_source.name = "测试RSS源"
    mock_source.url = "http://test.com/rss"
    mock_source.source_type = SourceType.RSS
    mock_source.interval = SourceInterval.ONE_DAY
    mock_source.description = "测试描述"
    mock_source.tags = "test,tag"
    mock_source.config = {"test": "config"}
    mock_source.is_paused = False
    mock_source.is_active = True
    mock_source.last_sync = datetime(2025, 1, 1, 12, 0, 0)
    mock_source.next_sync = datetime(2025, 1, 2, 12, 0, 0)
    mock_source.total_documents = 10
    mock_source.last_document_count = 5
    mock_source.sync_errors = 0
    mock_source.last_error = None
    mock_source.created_at = datetime(2025, 1, 1, 10, 0, 0)
    mock_source.updated_at = datetime(2025, 1, 1, 10, 0, 0)
    return mock_source


@pytest.fixture(scope="function")
def mock_jwt_token():
    """模拟JWT令牌"""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MzcwNzIwMDB9.test_signature"

