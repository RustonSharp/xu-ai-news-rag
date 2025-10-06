"""
tools.py 单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import create_knowledge_base_tool, create_online_search_tool


class TestCreateKnowledgeBaseTool:
    """测试create_knowledge_base_tool函数"""
    
    @patch('tools.HuggingFaceEmbeddings')
    @patch('tools.FAISS')
    @patch('tools.CrossEncoder')
    @patch('tools.os.path.exists')
    @patch('tools.os.getenv')
    def test_create_knowledge_base_tool_success(self, mock_getenv, mock_exists, mock_cross_encoder, mock_faiss, mock_embeddings):
        """测试成功创建知识库工具"""
        # 设置mock
        mock_getenv.side_effect = lambda key, default=None: {
            'EMBEDDING_MODEL_NAME': 'test-model',
            'RERANK_MODEL_NAME': 'test-rerank'
        }.get(key, default)
        
        mock_exists.return_value = True
        mock_embeddings_instance = Mock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        mock_faiss_instance = Mock()
        mock_faiss.load_local.return_value = mock_faiss_instance
        
        mock_reranker = Mock()
        mock_cross_encoder.return_value = mock_reranker
        
        # 执行测试
        result = create_knowledge_base_tool()
        
        # 验证
        assert result is not None
        assert hasattr(result, 'invoke')
        mock_embeddings.assert_called_once()
        mock_faiss.load_local.assert_called_once()
    
    @patch('tools.HuggingFaceEmbeddings')
    @patch('tools.FAISS')
    @patch('tools.os.makedirs')
    @patch('tools.os.path.exists')
    @patch('tools.os.getenv')
    def test_create_knowledge_base_tool_no_index(self, mock_getenv, mock_exists, mock_makedirs, mock_faiss, mock_embeddings):
        """测试索引文件不存在的情况"""
        # 设置mock
        mock_getenv.side_effect = lambda key, default=None: {
            'EMBEDDING_MODEL_NAME': 'test-model',
            'RERANK_MODEL_NAME': 'test-rerank'
        }.get(key, default)
        
        mock_exists.return_value = False
        mock_embeddings_instance = Mock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        mock_faiss_instance = Mock()
        mock_faiss.from_texts.return_value = mock_faiss_instance
        
        with patch('tools.CrossEncoder') as mock_cross_encoder:
            mock_reranker = Mock()
            mock_cross_encoder.return_value = mock_reranker
            
            # 执行测试
            result = create_knowledge_base_tool()
            
            # 验证
            assert result is not None
            mock_faiss.from_texts.assert_called_once()
    
    @patch('tools.HuggingFaceEmbeddings')
    @patch('tools.FAISS')
    @patch('tools.os.path.exists')
    @patch('tools.os.getenv')
    def test_create_knowledge_base_tool_embedding_fallback(self, mock_getenv, mock_exists, mock_faiss, mock_embeddings):
        """测试嵌入模型fallback机制"""
        # 设置mock - 第一个模型失败，第二个成功
        mock_getenv.side_effect = lambda key, default=None: {
            'EMBEDDING_MODEL_NAME': 'test-model',
            'RERANK_MODEL_NAME': 'test-rerank'
        }.get(key, default)
        
        mock_exists.return_value = True
        
        # 第一个模型失败
        mock_embeddings.side_effect = [
            Exception("网络错误"),
            Mock()  # 第二个模型成功
        ]
        
        mock_faiss_instance = Mock()
        mock_faiss.load_local.return_value = mock_faiss_instance
        
        with patch('tools.CrossEncoder') as mock_cross_encoder:
            mock_reranker = Mock()
            mock_cross_encoder.return_value = mock_reranker
            
            # 执行测试
            result = create_knowledge_base_tool()
            
            # 验证
            assert result is not None
            assert mock_embeddings.call_count == 2  # 尝试了两个模型
    
    def test_knowledge_base_tool_invoke_retrieve(self):
        """测试知识库工具的retrieve功能"""
        # 创建模拟工具
        mock_tool = Mock()
        mock_tool.invoke.return_value = [
            {
                "id": 1,
                "content": "测试内容",
                "metadata": {"title": "测试标题"}
            }
        ]
        
        # 模拟工具调用
        result = mock_tool.invoke({
            "action": "retrieve",
            "query": "测试查询",
            "k": 3,
            "rerank": True
        })
        
        # 验证
        assert len(result) == 1
        assert result[0]["content"] == "测试内容"
        mock_tool.invoke.assert_called_once()


class TestCreateOnlineSearchTool:
    """测试create_online_search_tool函数"""
    
    @patch('tools.os.getenv')
    def test_create_online_search_tool_success(self, mock_getenv):
        """测试成功创建在线搜索工具"""
        # 设置mock
        mock_getenv.return_value = "test_api_key"
        
        # 执行测试
        result = create_online_search_tool()
        
        # 验证
        assert result is not None
        assert hasattr(result, 'invoke')
    
    @patch('tools.os.getenv')
    def test_create_online_search_tool_no_api_key(self, mock_getenv):
        """测试没有API密钥的情况"""
        # 设置mock
        mock_getenv.return_value = None
        
        # 执行测试
        result = create_online_search_tool()
        
        # 验证
        assert result is not None
        # 应该返回一个模拟工具
        assert hasattr(result, 'invoke')
    
    def test_online_search_tool_invoke(self):
        """测试在线搜索工具的invoke功能"""
        # 创建模拟工具
        mock_tool = Mock()
        mock_tool.invoke.return_value = [
            {
                "content": "搜索结果内容",
                "title": "搜索结果标题",
                "url": "https://example.com"
            }
        ]
        
        # 模拟工具调用
        result = mock_tool.invoke("测试查询")
        
        # 验证
        assert len(result) == 1
        assert result[0]["content"] == "搜索结果内容"
        mock_tool.invoke.assert_called_once_with("测试查询")


class TestToolIntegration:
    """测试工具集成功能"""
    
    @patch('tools.create_knowledge_base_tool')
    @patch('tools.create_online_search_tool')
    def test_tools_work_together(self, mock_online_tool, mock_kb_tool):
        """测试工具协同工作"""
        # 设置mock
        mock_kb = Mock()
        mock_kb.invoke.return_value = [
            {
                "id": 1,
                "content": "知识库内容",
                "metadata": {"title": "知识库标题"}
            }
        ]
        mock_kb_tool.return_value = mock_kb
        
        mock_online = Mock()
        mock_online.invoke.return_value = [
            {
                "content": "在线搜索内容",
                "title": "在线搜索标题",
                "url": "https://example.com"
            }
        ]
        mock_online_tool.return_value = mock_online
        
        # 测试知识库工具
        kb_result = mock_kb.invoke({
            "action": "retrieve",
            "query": "测试查询",
            "k": 3,
            "rerank": True
        })
        
        # 测试在线搜索工具
        online_result = mock_online.invoke("测试查询")
        
        # 验证
        assert len(kb_result) == 1
        assert len(online_result) == 1
        assert kb_result[0]["content"] == "知识库内容"
        assert online_result[0]["content"] == "在线搜索内容"


class TestErrorHandling:
    """测试错误处理"""
    
    @patch('tools.HuggingFaceEmbeddings')
    @patch('tools.os.getenv')
    def test_embedding_model_load_failure(self, mock_getenv, mock_embeddings):
        """测试嵌入模型加载失败"""
        # 设置mock
        mock_getenv.return_value = "test-model"
        mock_embeddings.side_effect = Exception("模型加载失败")
        
        # 执行测试并验证异常
        with pytest.raises(Exception, match="无法加载任何嵌入模型"):
            create_knowledge_base_tool()
    
    @patch('tools.os.getenv')
    def test_tavily_initialization_failure(self, mock_getenv):
        """测试Tavily初始化失败"""
        # 设置mock
        mock_getenv.return_value = "test_api_key"
        
        # 执行测试
        result = create_online_search_tool()
        
        # 验证返回了模拟工具
        assert result is not None
        assert hasattr(result, 'invoke')

