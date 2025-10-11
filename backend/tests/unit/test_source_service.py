"""
源服务单元测试
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.source_service import SourceService
from models.source import Source


class TestSourceService:
    """源服务测试"""
    
    def test_get_rss_sources_success(self, mock_database_session, mock_rss_source):
        """测试获取RSS源列表成功"""
        # 设置mock - 让exec返回可迭代对象
        mock_database_session.exec.return_value = [mock_rss_source]
        
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # 执行测试
        result = source_service.get_rss_sources(mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 1
        assert result[0].name == "测试RSS源"
    
    def test_get_rss_sources_empty(self, mock_database_session):
        """测试获取空RSS源列表"""
        # 设置mock
        mock_database_session.exec.return_value = []
        
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # 执行测试
        result = source_service.get_rss_sources(mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 0
    
    def test_get_rss_source_by_id_success(self, mock_database_session, mock_rss_source):
        """测试根据ID获取RSS源成功"""
        # 设置mock - get_by_id使用session.get()方法
        mock_database_session.get.return_value = mock_rss_source
        
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # 执行测试
        result = source_service.get_rss_source_by_id(1, mock_database_session)
        
        # 验证
        assert result is not None
        assert result.id == 1
        assert result.name == "测试RSS源"
    
    def test_get_rss_source_by_id_not_found(self, mock_database_session):
        """测试根据ID获取RSS源不存在"""
        # 设置mock - get_by_id使用session.get()方法
        mock_database_session.get.return_value = None
        
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # 执行测试
        result = source_service.get_rss_source_by_id(999, mock_database_session)
        
        # 验证
        assert result is None
    
    def test_create_rss_source_success(self, mock_database_session):
        """测试创建RSS源成功"""
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # 执行测试
        source_data = {
            'name': '新RSS源',
            'url': 'http://new.com/rss',
            'interval': 'ONE_DAY',
            'is_paused': False
        }
        
        # Mock source_repo.create方法
        from datetime import datetime
        mock_created_source = Mock()
        mock_created_source.id = 1
        mock_created_source.name = '新RSS源'
        mock_created_source.url = 'http://new.com/rss'
        mock_created_source.source_type = 'rss'
        mock_created_source.interval = 'ONE_DAY'
        mock_created_source.description = ''
        mock_created_source.tags = None
        mock_created_source.config = {}  # 字典而不是字符串
        mock_created_source.is_paused = False
        mock_created_source.is_active = True
        mock_created_source.total_documents = 0
        mock_created_source.last_document_count = 0
        mock_created_source.sync_errors = 0
        mock_created_source.last_error = None
        mock_created_source.last_sync = None
        mock_created_source.next_sync = None
        mock_created_source.created_at = datetime.now()
        mock_created_source.updated_at = datetime.now()
        
        # Mock the create_source method instead of repository
        with patch.object(source_service, 'create_source', return_value=mock_created_source):
            result = source_service.create_rss_source(source_data, mock_database_session)
            
            # 验证
            assert result is not None
            assert result.id == 1
            assert result.name == '新RSS源'
    
    def test_create_rss_source_duplicate_url(self, mock_database_session, mock_rss_source):
        """测试创建重复URL的RSS源"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_rss_source
        
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # 执行测试
        source_data = {
            'name': '重复RSS源',
            'url': 'http://test.com/rss',  # 重复的URL
            'interval': 'ONE_DAY',
            'is_paused': False
        }
        
        # 验证应该抛出异常
        with pytest.raises(ValueError, match="RSS源URL已存在"):
            source_service.create_rss_source(source_data, mock_database_session)
    
    def test_update_rss_source_success(self, mock_database_session, mock_rss_source):
        """测试更新RSS源成功"""
        # 设置mock - get_by_id使用session.get()方法
        mock_database_session.get.return_value = mock_rss_source
        
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # 执行测试
        update_data = {'name': '更新的RSS源'}
        result = source_service.update_rss_source(1, update_data, mock_database_session)
        
        # 验证
        assert result is not None
        mock_database_session.commit.assert_called_once()
    
    def test_update_rss_source_not_found(self, mock_database_session):
        """测试更新不存在的RSS源"""
        # 设置mock - get_by_id使用session.get()方法
        mock_database_session.get.return_value = None
        
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # 执行测试
        update_data = {'name': '更新的RSS源'}
        result = source_service.update_rss_source(999, update_data, mock_database_session)
        
        # 验证
        assert result is None
    
    def test_delete_rss_source_success(self, mock_database_session, mock_rss_source):
        """测试删除RSS源成功"""
        # 设置mock - get_by_id使用session.get()方法
        mock_database_session.get.return_value = mock_rss_source
        
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # 执行测试
        result = source_service.delete_rss_source(1, mock_database_session)
        
        # 验证
        assert result is True
        mock_database_session.delete.assert_called_once()
        mock_database_session.commit.assert_called_once()
    
    def test_delete_rss_source_not_found(self, mock_database_session):
        """测试删除不存在的RSS源"""
        # 设置mock - get_by_id使用session.get()方法
        mock_database_session.get.return_value = None
        
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # 执行测试
        result = source_service.delete_rss_source(999, mock_database_session)
        
        # 验证
        assert result is False
    
    def test_pause_rss_source_success(self, mock_database_session, mock_rss_source):
        """测试暂停RSS源成功"""
        # 设置mock - get_by_id使用session.get()方法
        mock_database_session.get.return_value = mock_rss_source
        
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # 执行测试
        result = source_service.pause_rss_source(1, mock_database_session)
        
        # 验证
        assert result is True
        assert mock_rss_source.is_paused is True
        mock_database_session.commit.assert_called_once()
    
    def test_resume_rss_source_success(self, mock_database_session, mock_rss_source):
        """测试恢复RSS源成功"""
        # 设置mock
        mock_rss_source.is_paused = True
        mock_database_session.get.return_value = mock_rss_source
        
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # 执行测试
        result = source_service.resume_rss_source(1, mock_database_session)
        
        # 验证
        assert result is True
        assert mock_rss_source.is_paused is False
        mock_database_session.commit.assert_called_once()
    
    def test_get_active_rss_sources_success(self, mock_database_session, mock_rss_source):
        """测试获取活跃RSS源成功"""
        # 设置mock
        mock_database_session.exec.return_value = [mock_rss_source]
        
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # 执行测试
        result = source_service.get_active_rss_sources(mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 1
        assert result[0].is_active is True
    
    def test_validate_rss_url_success(self, mock_database_session):
        """测试验证RSS URL成功"""
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # Mock feedparser.parse
        with patch('services.source_service.feedparser.parse') as mock_parse:
            mock_feed = Mock()
            mock_feed.entries = [Mock(), Mock()]  # 模拟有2个条目
            mock_parse.return_value = mock_feed
            
            # 执行测试
            result = source_service.validate_rss_url("http://example.com/rss")
            
            # 验证
            assert result is True
    
    def test_validate_rss_url_invalid(self, mock_database_session):
        """测试验证无效RSS URL"""
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # 执行测试
        result = source_service.validate_rss_url("invalid_url")
        
        # 验证
        assert result is False
    
    def test_get_rss_source_statistics_success(self, mock_database_session):
        """测试获取RSS源统计成功"""
        # 创建服务实例
        source_service = SourceService(mock_database_session)
        
        # Mock source_repo.get_source_statistics方法
        mock_stats = {
            'total_sources': 5,
            'active_sources': 4,
            'paused_sources': 1,
            'sources_due': 2,
            'total_documents': 100,
            'last_sync_errors': 0
        }
        # Mock the _get_source_statistics method instead of repository
        with patch.object(source_service, '_get_source_statistics', return_value=mock_stats):
            # 执行测试
            result = source_service.get_rss_source_statistics(mock_database_session)
            
            # 验证
            assert result is not None
            assert result['total_sources'] == 5
            assert 'total_sources' in result
            assert result['total_sources'] == 5
