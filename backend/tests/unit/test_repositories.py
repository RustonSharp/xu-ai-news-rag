"""
仓库层单元测试
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from repositories.base_repository import BaseRepository
from repositories.user_repository import UserRepository
from repositories.document_repository import DocumentRepository
from repositories.source_repository import SourceRepository
from repositories.analysis_repository import AnalysisRepository
from models.user import User
from models.document import Document
from models.source import Source
from models.analysis import Analysis


class TestBaseRepository:
    """基础仓库测试"""
    
    def test_base_repository_initialization(self):
        """测试基础仓库初始化"""
        repository = BaseRepository()
        
        # 验证
        assert repository is not None
        assert hasattr(repository, 'get_by_id')
        assert hasattr(repository, 'get_all')
        assert hasattr(repository, 'create')
        assert hasattr(repository, 'update')
        assert hasattr(repository, 'delete')
    
    def test_get_by_id_success(self, mock_database_session, mock_user):
        """测试根据ID获取成功"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_user
        
        # 创建仓库实例
        repository = BaseRepository()
        
        # 执行测试
        result = repository.get_by_id(User, 1, mock_database_session)
        
        # 验证
        assert result is not None
        assert result.id == 1
        assert result.username == "test_user"
    
    def test_get_by_id_not_found(self, mock_database_session):
        """测试根据ID获取不存在"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = None
        
        # 创建仓库实例
        repository = BaseRepository()
        
        # 执行测试
        result = repository.get_by_id(User, 999, mock_database_session)
        
        # 验证
        assert result is None
    
    def test_get_all_success(self, mock_database_session, mock_user):
        """测试获取所有成功"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_user]
        
        # 创建仓库实例
        repository = BaseRepository()
        
        # 执行测试
        result = repository.get_all(User, mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 1
        assert result[0].username == "test_user"
    
    def test_get_all_empty(self, mock_database_session):
        """测试获取所有为空"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = []
        
        # 创建仓库实例
        repository = BaseRepository()
        
        # 执行测试
        result = repository.get_all(User, mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 0
    
    def test_create_success(self, mock_database_session):
        """测试创建成功"""
        # 创建仓库实例
        repository = BaseRepository()
        
        # 执行测试
        user_data = {
            'username': 'new_user',
            'email': 'new@example.com',
            'hashed_password': 'hashed_password'
        }
        
        with patch('repositories.base_repository.User') as mock_user_class:
            mock_user_instance = Mock()
            mock_user_class.return_value = mock_user_instance
            
            result = repository.create(User, user_data, mock_database_session)
            
            # 验证
            assert result is not None
            mock_database_session.add.assert_called_once()
            mock_database_session.commit.assert_called_once()
    
    def test_update_success(self, mock_database_session, mock_user):
        """测试更新成功"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_user
        
        # 创建仓库实例
        repository = BaseRepository()
        
        # 执行测试
        update_data = {'username': 'updated_user'}
        result = repository.update(User, 1, update_data, mock_database_session)
        
        # 验证
        assert result is not None
        assert mock_user.username == 'updated_user'
        mock_database_session.commit.assert_called_once()
    
    def test_update_not_found(self, mock_database_session):
        """测试更新不存在"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = None
        
        # 创建仓库实例
        repository = BaseRepository()
        
        # 执行测试
        update_data = {'username': 'updated_user'}
        result = repository.update(User, 999, update_data, mock_database_session)
        
        # 验证
        assert result is None
    
    def test_delete_success(self, mock_database_session, mock_user):
        """测试删除成功"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_user
        
        # 创建仓库实例
        repository = BaseRepository()
        
        # 执行测试
        result = repository.delete(User, 1, mock_database_session)
        
        # 验证
        assert result is True
        mock_database_session.delete.assert_called_once()
        mock_database_session.commit.assert_called_once()
    
    def test_delete_not_found(self, mock_database_session):
        """测试删除不存在"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = None
        
        # 创建仓库实例
        repository = BaseRepository()
        
        # 执行测试
        result = repository.delete(User, 999, mock_database_session)
        
        # 验证
        assert result is False


class TestUserRepository:
    """用户仓库测试"""
    
    def test_get_by_username_success(self, mock_database_session, mock_user):
        """测试根据用户名获取成功"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_user
        
        # 创建仓库实例
        repository = UserRepository()
        
        # 执行测试
        result = repository.get_by_username("test_user", mock_database_session)
        
        # 验证
        assert result is not None
        assert result.username == "test_user"
    
    def test_get_by_username_not_found(self, mock_database_session):
        """测试根据用户名获取不存在"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = None
        
        # 创建仓库实例
        repository = UserRepository()
        
        # 执行测试
        result = repository.get_by_username("nonexistent_user", mock_database_session)
        
        # 验证
        assert result is None
    
    def test_get_by_email_success(self, mock_database_session, mock_user):
        """测试根据邮箱获取成功"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_user
        
        # 创建仓库实例
        repository = UserRepository()
        
        # 执行测试
        result = repository.get_by_email("test@example.com", mock_database_session)
        
        # 验证
        assert result is not None
        assert result.email == "test@example.com"
    
    def test_get_by_email_not_found(self, mock_database_session):
        """测试根据邮箱获取不存在"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = None
        
        # 创建仓库实例
        repository = UserRepository()
        
        # 执行测试
        result = repository.get_by_email("nonexistent@example.com", mock_database_session)
        
        # 验证
        assert result is None


class TestDocumentRepository:
    """文档仓库测试"""
    
    def test_get_by_source_success(self, mock_database_session, mock_document):
        """测试根据源获取文档成功"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_document]
        
        # 创建仓库实例
        repository = DocumentRepository()
        
        # 执行测试
        result = repository.get_by_source(1, mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 1
        assert result[0].source_id == 1
    
    def test_get_by_source_empty(self, mock_database_session):
        """测试根据源获取文档为空"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = []
        
        # 创建仓库实例
        repository = DocumentRepository()
        
        # 执行测试
        result = repository.get_by_source(999, mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 0
    
    def test_search_by_title_success(self, mock_database_session, mock_document):
        """测试根据标题搜索成功"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_document]
        
        # 创建仓库实例
        repository = DocumentRepository()
        
        # 执行测试
        result = repository.search_by_title("测试", mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 1
        assert "测试" in result[0].title
    
    def test_search_by_content_success(self, mock_database_session, mock_document):
        """测试根据内容搜索成功"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_document]
        
        # 创建仓库实例
        repository = DocumentRepository()
        
        # 执行测试
        result = repository.search_by_content("测试", mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 1
        assert "测试" in result[0].content
    
    def test_get_by_date_range_success(self, mock_database_session, mock_document):
        """测试根据日期范围获取成功"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_document]
        
        # 创建仓库实例
        repository = DocumentRepository()
        
        # 执行测试
        from datetime import date
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        result = repository.get_by_date_range(start_date, end_date, mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 1
    
    def test_get_count_success(self, mock_database_session):
        """测试获取计数成功"""
        # 设置mock
        mock_database_session.exec.return_value.one.return_value = 100
        
        # 创建仓库实例
        repository = DocumentRepository()
        
        # 执行测试
        result = repository.get_count(mock_database_session)
        
        # 验证
        assert result == 100


class TestSourceRepository:
    """源仓库测试"""
    
    def test_get_active_sources_success(self, mock_database_session, mock_rss_source):
        """测试获取活跃源成功"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_rss_source]
        
        # 创建仓库实例
        repository = SourceRepository()
        
        # 执行测试
        result = repository.get_active_sources(mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 1
        assert result[0].is_active is True
    
    def test_get_paused_sources_success(self, mock_database_session, mock_rss_source):
        """测试获取暂停源成功"""
        # 设置mock
        mock_rss_source.is_paused = True
        mock_database_session.exec.return_value.all.return_value = [mock_rss_source]
        
        # 创建仓库实例
        repository = SourceRepository()
        
        # 执行测试
        result = repository.get_paused_sources(mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 1
        assert result[0].is_paused is True
    
    def test_get_by_url_success(self, mock_database_session, mock_rss_source):
        """测试根据URL获取成功"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_rss_source
        
        # 创建仓库实例
        repository = SourceRepository()
        
        # 执行测试
        result = repository.get_by_url("http://test.com/rss", mock_database_session)
        
        # 验证
        assert result is not None
        assert result.url == "http://test.com/rss"
    
    def test_get_by_url_not_found(self, mock_database_session):
        """测试根据URL获取不存在"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = None
        
        # 创建仓库实例
        repository = SourceRepository()
        
        # 执行测试
        result = repository.get_by_url("http://nonexistent.com/rss", mock_database_session)
        
        # 验证
        assert result is None


class TestAnalysisRepository:
    """分析仓库测试"""
    
    def test_get_by_type_success(self, mock_database_session):
        """测试根据类型获取成功"""
        # 创建模拟分析
        mock_analysis = Mock()
        mock_analysis.id = 1
        mock_analysis.analysis_type = "clustering"
        mock_analysis.title = "测试分析"
        
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_analysis]
        
        # 创建仓库实例
        repository = AnalysisRepository()
        
        # 执行测试
        result = repository.get_by_type("clustering", mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 1
        assert result[0].analysis_type == "clustering"
    
    def test_get_by_type_empty(self, mock_database_session):
        """测试根据类型获取为空"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = []
        
        # 创建仓库实例
        repository = AnalysisRepository()
        
        # 执行测试
        result = repository.get_by_type("nonexistent_type", mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 0
    
    def test_get_latest_success(self, mock_database_session):
        """测试获取最新分析成功"""
        # 创建模拟分析
        mock_analysis = Mock()
        mock_analysis.id = 1
        mock_analysis.analysis_type = "clustering"
        mock_analysis.created_at = "2025-01-01T12:00:00"
        
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_analysis
        
        # 创建仓库实例
        repository = AnalysisRepository()
        
        # 执行测试
        result = repository.get_latest("clustering", mock_database_session)
        
        # 验证
        assert result is not None
        assert result.analysis_type == "clustering"
