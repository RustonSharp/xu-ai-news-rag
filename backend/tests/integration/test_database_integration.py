"""
数据库集成测试
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os
import tempfile
import shutil
from datetime import datetime, date

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.database import get_database_session
from models.user import User
from models.document import Document
from models.source import Source
from models.analysis import Analysis
from services.auth_service import AuthService
from services.document_service import DocumentService
from services.source_service import SourceService
from services.analytics_service import AnalyticsService


class TestDatabaseIntegration:
    """数据库集成测试"""
    
    @pytest.fixture
    def temp_db_dir(self):
        """临时数据库目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_user_workflow_integration(self, temp_db_dir):
        """测试用户工作流集成"""
        # 设置测试数据库
        test_db_path = os.path.join(temp_db_dir, "test.db")
        
        with patch('core.database.engine') as mock_engine:
            # 模拟数据库操作
            mock_session = Mock()
            mock_session.exec.return_value.first.return_value = None  # 用户不存在
            mock_session.exec.return_value.all.return_value = []
            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None
            
            # 创建认证服务
            auth_service = AuthService()
            
            # 测试用户注册
            user_data = {
                'username': 'test_user',
                'email': 'test@example.com',
                'password': 'password123'
            }
            
            with patch('services.auth_service.get_session') as mock_get_session:
                mock_get_session.return_value.__enter__.return_value = mock_session
                
                # 注册用户
                user = auth_service.register_user(user_data)
                
                # 验证
                assert user is not None
                assert user.username == 'test_user'
                assert user.email == 'test@example.com'
    
    def test_document_workflow_integration(self, temp_db_dir):
        """测试文档工作流集成"""
        # 设置测试数据库
        test_db_path = os.path.join(temp_db_dir, "test.db")
        
        with patch('core.database.engine') as mock_engine:
            # 模拟数据库操作
            mock_session = Mock()
            mock_doc = Mock()
            mock_doc.id = 1
            mock_doc.title = "测试文档"
            mock_doc.content = "测试内容"
            mock_doc.link = "http://test.com"
            mock_doc.description = "测试描述"
            mock_doc.author = "测试作者"
            mock_doc.tags = "tag1,tag2"
            mock_doc.source_id = 1
            mock_doc.crawled_at = datetime(2025, 1, 1, 12, 0, 0)
            
            mock_session.exec.return_value.all.return_value = [mock_doc]
            mock_session.exec.return_value.first.return_value = mock_doc
            mock_session.exec.return_value.one.return_value = 1
            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None
            
            # 创建文档服务
            document_service = DocumentService()
            
            with patch('services.document_service.get_session') as mock_get_session:
                mock_get_session.return_value.__enter__.return_value = mock_session
                
                # 测试获取文档列表
                documents = document_service.get_documents()
                
                # 验证
                assert documents is not None
                assert len(documents) == 1
                assert documents[0].title == "测试文档"
                
                # 测试根据ID获取文档
                document = document_service.get_document_by_id(1)
                
                # 验证
                assert document is not None
                assert document.id == 1
                assert document.title == "测试文档"
    
    def test_rss_source_workflow_integration(self, temp_db_dir):
        """测试RSS源工作流集成"""
        # 设置测试数据库
        test_db_path = os.path.join(temp_db_dir, "test.db")
        
        with patch('core.database.engine') as mock_engine:
            # 模拟数据库操作
            mock_session = Mock()
            mock_source = Mock()
            mock_source.id = 1
            mock_source.name = "测试RSS源"
            mock_source.url = "http://test.com/rss"
            mock_source.interval = "ONE_DAY"
            mock_source.is_paused = False
            mock_source.is_active = True
            
            mock_session.exec.return_value.all.return_value = [mock_source]
            mock_session.exec.return_value.first.return_value = mock_source
            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None
            
            # 创建源服务
            source_service = SourceService()
            
            with patch('services.source_service.get_session') as mock_get_session:
                mock_get_session.return_value.__enter__.return_value = mock_session
                
                # 测试获取RSS源列表
                sources = source_service.get_rss_sources()
                
                # 验证
                assert sources is not None
                assert len(sources) == 1
                assert sources[0].name == "测试RSS源"
                
                # 测试根据ID获取RSS源
                source = source_service.get_rss_source_by_id(1)
                
                # 验证
                assert source is not None
                assert source.id == 1
                assert source.name == "测试RSS源"
    
    def test_analytics_workflow_integration(self, temp_db_dir):
        """测试分析工作流集成"""
        # 设置测试数据库
        test_db_path = os.path.join(temp_db_dir, "test.db")
        
        with patch('core.database.engine') as mock_engine:
            # 模拟数据库操作
            mock_session = Mock()
            mock_analysis = Mock()
            mock_analysis.id = 1
            mock_analysis.title = "测试分析"
            mock_analysis.content = "分析内容"
            mock_analysis.analysis_type = "clustering"
            mock_analysis.parameters = {"k": 5}
            mock_analysis.results = {"clusters": 3}
            mock_analysis.created_at = datetime(2025, 1, 1, 12, 0, 0)
            
            mock_session.exec.return_value.all.return_value = [mock_analysis]
            mock_session.exec.return_value.first.return_value = mock_analysis
            mock_session.exec.return_value.one.return_value = 1
            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None
            
            # 创建分析服务
            analytics_service = AnalyticsService()
            
            with patch('services.analytics_service.get_session') as mock_get_session:
                mock_get_session.return_value.__enter__.return_value = mock_session
                
                # 测试获取分析列表
                analyses = analytics_service.get_analyses()
                
                # 验证
                assert analyses is not None
                assert len(analyses) == 1
                assert analyses[0].title == "测试分析"
                
                # 测试根据类型获取分析
                clustering_analyses = analytics_service.get_analyses_by_type("clustering")
                
                # 验证
                assert clustering_analyses is not None
                assert len(clustering_analyses) == 1
                assert clustering_analyses[0].analysis_type == "clustering"


class TestCrossServiceIntegration:
    """跨服务集成测试"""
    
    def test_document_source_integration(self, temp_db_dir):
        """测试文档和源服务集成"""
        # 设置测试数据库
        test_db_path = os.path.join(temp_db_dir, "test.db")
        
        with patch('core.database.engine') as mock_engine:
            # 模拟数据库操作
            mock_session = Mock()
            
            # 模拟RSS源
            mock_source = Mock()
            mock_source.id = 1
            mock_source.name = "测试RSS源"
            mock_source.url = "http://test.com/rss"
            mock_source.interval = "ONE_DAY"
            mock_source.is_paused = False
            mock_source.is_active = True
            
            # 模拟文档
            mock_doc = Mock()
            mock_doc.id = 1
            mock_doc.title = "测试文档"
            mock_doc.content = "测试内容"
            mock_doc.source_id = 1
            mock_doc.crawled_at = datetime(2025, 1, 1, 12, 0, 0)
            
            mock_session.exec.return_value.all.return_value = [mock_source, mock_doc]
            mock_session.exec.return_value.first.return_value = mock_source
            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None
            
            # 创建服务
            source_service = SourceService()
            document_service = DocumentService()
            
            with patch('services.source_service.get_session') as mock_get_session_source, \
                 patch('services.document_service.get_session') as mock_get_session_doc:
                
                mock_get_session_source.return_value.__enter__.return_value = mock_session
                mock_get_session_doc.return_value.__enter__.return_value = mock_session
                
                # 测试获取源和其文档
                sources = source_service.get_rss_sources()
                documents = document_service.get_documents_by_source(1)
                
                # 验证
                assert sources is not None
                assert documents is not None
                assert len(sources) == 1
                assert len(documents) == 1
                assert sources[0].id == documents[0].source_id
    
    def test_user_document_integration(self, temp_db_dir):
        """测试用户和文档服务集成"""
        # 设置测试数据库
        test_db_path = os.path.join(temp_db_dir, "test.db")
        
        with patch('core.database.engine') as mock_engine:
            # 模拟数据库操作
            mock_session = Mock()
            
            # 模拟用户
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = "test_user"
            mock_user.email = "test@example.com"
            mock_user.is_active = True
            
            # 模拟文档
            mock_doc = Mock()
            mock_doc.id = 1
            mock_doc.title = "测试文档"
            mock_doc.content = "测试内容"
            mock_doc.crawled_at = datetime(2025, 1, 1, 12, 0, 0)
            
            mock_session.exec.return_value.all.return_value = [mock_user, mock_doc]
            mock_session.exec.return_value.first.return_value = mock_user
            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None
            
            # 创建服务
            auth_service = AuthService()
            document_service = DocumentService()
            
            with patch('services.auth_service.get_session') as mock_get_session_user, \
                 patch('services.document_service.get_session') as mock_get_session_doc:
                
                mock_get_session_user.return_value.__enter__.return_value = mock_session
                mock_get_session_doc.return_value.__enter__.return_value = mock_session
                
                # 测试用户认证和文档访问
                user = auth_service.authenticate_user("test_user", "password123")
                documents = document_service.get_documents()
                
                # 验证
                assert user is not None
                assert documents is not None
                assert user.username == "test_user"
                assert len(documents) == 1
