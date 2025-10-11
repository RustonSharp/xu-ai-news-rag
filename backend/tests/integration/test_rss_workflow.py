"""
RSS工作流集成测试
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os
import tempfile
import shutil
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.scheduler_service import SchedulerService
from services.source_service import SourceService
from services.document_service import DocumentService
from services.web_scraper_service import WebScraperService


class TestRSSWorkflowIntegration:
    """RSS工作流集成测试"""
    
    @pytest.fixture
    def temp_db_dir(self):
        """临时数据库目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_rss_source_creation_to_document_processing(self, temp_db_dir):
        """测试RSS源创建到文档处理的完整工作流"""
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
            mock_doc.link = "http://test.com/article1"
            mock_doc.description = "测试描述"
            mock_doc.author = "测试作者"
            mock_doc.tags = "tag1,tag2"
            mock_doc.source_id = 1
            mock_doc.crawled_at = datetime(2025, 1, 1, 12, 0, 0)
            
            mock_session.exec.return_value.all.return_value = [mock_source]
            mock_session.exec.return_value.first.return_value = mock_source
            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None
            
            # 创建服务
            source_service = SourceService()
            document_service = DocumentService()
            scheduler_service = SchedulerService()
            
            with patch('services.source_service.get_session') as mock_get_session_source, \
                 patch('services.document_service.get_session') as mock_get_session_doc, \
                 patch('services.scheduler_service.get_session') as mock_get_session_scheduler:
                
                mock_get_session_source.return_value.__enter__.return_value = mock_session
                mock_get_session_doc.return_value.__enter__.return_value = mock_session
                mock_get_session_scheduler.return_value.__enter__.return_value = mock_session
                
                # 1. 创建RSS源
                source_data = {
                    'name': '测试RSS源',
                    'url': 'http://test.com/rss',
                    'interval': 'ONE_DAY',
                    'is_paused': False
                }
                
                with patch('services.source_service.Source') as mock_source_class:
                    mock_source_instance = Mock()
                    mock_source_instance.id = 1
                    mock_source_instance.name = "测试RSS源"
                    mock_source_class.return_value = mock_source_instance
                    
                    source = source_service.create_rss_source(source_data)
                    
                    # 验证源创建
                    assert source is not None
                    assert source.name == "测试RSS源"
                
                # 2. 启动调度器
                with patch('services.scheduler_service.fetch_rss_feeds') as mock_fetch:
                    mock_fetch.return_value = True
                    
                    scheduler_started = scheduler_service.start()
                    
                    # 验证调度器启动
                    assert scheduler_started is True
                    assert scheduler_service.running is True
                
                # 3. 模拟RSS获取和文档处理
                with patch('services.web_scraper_service.fetch_rss_feeds') as mock_web_scraper:
                    mock_web_scraper.return_value = [mock_doc]
                    
                    # 模拟文档创建
                    with patch('services.document_service.Document') as mock_document_class:
                        mock_document_instance = Mock()
                        mock_document_instance.id = 1
                        mock_document_instance.title = "测试文档"
                        mock_document_class.return_value = mock_document_instance
                        
                        # 获取文档
                        documents = document_service.get_documents()
                        
                        # 验证文档处理
                        assert documents is not None
                        assert len(documents) == 1
    
    def test_rss_source_pause_resume_workflow(self, temp_db_dir):
        """测试RSS源暂停和恢复工作流"""
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
            
            mock_session.exec.return_value.first.return_value = mock_source
            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None
            
            # 创建服务
            source_service = SourceService()
            scheduler_service = SchedulerService()
            
            with patch('services.source_service.get_session') as mock_get_session_source, \
                 patch('services.scheduler_service.get_session') as mock_get_session_scheduler:
                
                mock_get_session_source.return_value.__enter__.return_value = mock_session
                mock_get_session_scheduler.return_value.__enter__.return_value = mock_session
                
                # 1. 暂停RSS源
                paused = source_service.pause_rss_source(1)
                
                # 验证暂停
                assert paused is True
                assert mock_source.is_paused is True
                
                # 2. 尝试获取暂停的RSS源
                with patch('services.scheduler_service.fetch_rss_feeds') as mock_fetch:
                    mock_fetch.return_value = False
                    
                    fetch_result = scheduler_service.fetch_rss_source(1)
                    
                    # 验证获取失败（因为源被暂停）
                    assert fetch_result is False
                
                # 3. 恢复RSS源
                mock_source.is_paused = True  # 设置为暂停状态
                resumed = source_service.resume_rss_source(1)
                
                # 验证恢复
                assert resumed is True
                assert mock_source.is_paused is False
    
    def test_rss_source_error_handling_workflow(self, temp_db_dir):
        """测试RSS源错误处理工作流"""
        # 设置测试数据库
        test_db_path = os.path.join(temp_db_dir, "test.db")
        
        with patch('core.database.engine') as mock_engine:
            # 模拟数据库操作
            mock_session = Mock()
            
            # 模拟RSS源
            mock_source = Mock()
            mock_source.id = 1
            mock_source.name = "测试RSS源"
            mock_source.url = "http://invalid-url.com/rss"
            mock_source.interval = "ONE_DAY"
            mock_source.is_paused = False
            mock_source.is_active = True
            
            mock_session.exec.return_value.first.return_value = mock_source
            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None
            
            # 创建服务
            source_service = SourceService()
            scheduler_service = SchedulerService()
            
            with patch('services.source_service.get_session') as mock_get_session_source, \
                 patch('services.scheduler_service.get_session') as mock_get_session_scheduler:
                
                mock_get_session_source.return_value.__enter__.return_value = mock_session
                mock_get_session_scheduler.return_value.__enter__.return_value = mock_session
                
                # 1. 验证RSS URL
                is_valid = source_service.validate_rss_url("http://invalid-url.com/rss")
                
                # 验证URL验证
                assert is_valid is False
                
                # 2. 尝试获取无效RSS源
                with patch('services.web_scraper_service.fetch_rss_feeds') as mock_web_scraper:
                    mock_web_scraper.side_effect = Exception("RSS获取失败")
                    
                    fetch_result = scheduler_service.fetch_rss_source(1)
                    
                    # 验证获取失败
                    assert fetch_result is False
    
    def test_rss_source_scheduling_workflow(self, temp_db_dir):
        """测试RSS源调度工作流"""
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
            
            mock_session.exec.return_value.all.return_value = [mock_source]
            mock_session.exec.return_value.first.return_value = mock_source
            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None
            
            # 创建服务
            scheduler_service = SchedulerService()
            
            with patch('services.scheduler_service.get_session') as mock_get_session_scheduler:
                mock_get_session_scheduler.return_value.__enter__.return_value = mock_session
                
                # 1. 启动调度器
                with patch('services.scheduler_service.fetch_rss_feeds') as mock_fetch:
                    mock_fetch.return_value = True
                    
                    scheduler_started = scheduler_service.start()
                    
                    # 验证调度器启动
                    assert scheduler_started is True
                    assert scheduler_service.running is True
                
                # 2. 获取调度器状态
                status = scheduler_service.get_status()
                
                # 验证状态
                assert status is not None
                assert status['running'] is True
                
                # 3. 停止调度器
                scheduler_stopped = scheduler_service.stop()
                
                # 验证停止
                assert scheduler_stopped is True
                assert scheduler_service.running is False
                
                # 4. 再次获取状态
                status_after_stop = scheduler_service.get_status()
                
                # 验证停止后状态
                assert status_after_stop is not None
                assert status_after_stop['running'] is False
    
    def test_rss_source_cleanup_workflow(self, temp_db_dir):
        """测试RSS源清理工作流"""
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
            
            mock_session.exec.return_value.first.return_value = mock_source
            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None
            
            # 创建服务
            source_service = SourceService()
            scheduler_service = SchedulerService()
            
            with patch('services.source_service.get_session') as mock_get_session_source, \
                 patch('services.scheduler_service.get_session') as mock_get_session_scheduler:
                
                mock_get_session_source.return_value.__enter__.return_value = mock_session
                mock_get_session_scheduler.return_value.__enter__.return_value = mock_session
                
                # 1. 创建RSS源
                source_data = {
                    'name': '测试RSS源',
                    'url': 'http://test.com/rss',
                    'interval': 'ONE_DAY',
                    'is_paused': False
                }
                
                with patch('services.source_service.Source') as mock_source_class:
                    mock_source_instance = Mock()
                    mock_source_instance.id = 1
                    mock_source_instance.name = "测试RSS源"
                    mock_source_class.return_value = mock_source_instance
                    
                    source = source_service.create_rss_source(source_data)
                    
                    # 验证源创建
                    assert source is not None
                
                # 2. 删除RSS源
                deleted = source_service.delete_rss_source(1)
                
                # 验证删除
                assert deleted is True
                
                # 3. 尝试获取已删除的源
                source_after_delete = source_service.get_rss_source_by_id(1)
                
                # 验证源不存在
                assert source_after_delete is None
