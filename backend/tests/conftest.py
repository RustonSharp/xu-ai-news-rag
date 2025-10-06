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

from assistant import create_assistant, query_with_sources
from tools import create_knowledge_base_tool, create_online_search_tool


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

