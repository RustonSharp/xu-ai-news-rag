"""
调度器服务单元测试
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os
import threading
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.scheduler_service import SchedulerService


class TestSchedulerService:
    """调度器服务测试"""
    
    def test_scheduler_initialization(self):
        """测试调度器初始化"""
        # 创建服务实例
        scheduler = SchedulerService()
        
        # 验证
        assert scheduler is not None
        assert hasattr(scheduler, 'running')
        assert hasattr(scheduler, 'threads')
        assert hasattr(scheduler, 'lock')
        assert scheduler.running is False
        assert len(scheduler.threads) == 0
    
    def test_start_scheduler_success(self, mock_database_session, mock_rss_source):
        """测试启动调度器成功"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_rss_source]
        
        # 创建服务实例
        scheduler = SchedulerService()
        
        # 执行测试
        with patch('services.scheduler_service.fetch_rss_feeds') as mock_fetch:
            mock_fetch.return_value = True
            
            result = scheduler.start(mock_database_session)
            
            # 验证
            assert result is True
            assert scheduler.running is True
    
    def test_start_scheduler_already_running(self, mock_database_session):
        """测试启动已运行的调度器"""
        # 创建服务实例
        scheduler = SchedulerService()
        scheduler.running = True
        
        # 执行测试
        result = scheduler.start(mock_database_session)
        
        # 验证
        assert result is False
    
    def test_stop_scheduler_success(self):
        """测试停止调度器成功"""
        # 创建服务实例
        scheduler = SchedulerService()
        scheduler.running = True
        
        # 执行测试
        result = scheduler.stop()
        
        # 验证
        assert result is True
        assert scheduler.running is False
    
    def test_stop_scheduler_not_running(self):
        """测试停止未运行的调度器"""
        # 创建服务实例
        scheduler = SchedulerService()
        scheduler.running = False
        
        # 执行测试
        result = scheduler.stop()
        
        # 验证
        assert result is False
    
    def test_get_status_running(self):
        """测试获取运行状态"""
        # 创建服务实例
        scheduler = SchedulerService()
        scheduler.running = True
        scheduler.threads = {1: Mock(), 2: Mock()}
        
        # 执行测试
        status = scheduler.get_status()
        
        # 验证
        assert status is not None
        assert status['running'] is True
        assert status['thread_count'] == 2
    
    def test_get_status_stopped(self):
        """测试获取停止状态"""
        # 创建服务实例
        scheduler = SchedulerService()
        scheduler.running = False
        scheduler.threads = {}
        
        # 执行测试
        status = scheduler.get_status()
        
        # 验证
        assert status is not None
        assert status['running'] is False
        assert status['thread_count'] == 0
    
    def test_fetch_rss_source_success(self, mock_database_session, mock_rss_source):
        """测试获取特定RSS源成功"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_rss_source
        
        # 创建服务实例
        scheduler = SchedulerService()
        
        # 执行测试
        with patch('services.scheduler_service.fetch_rss_feeds') as mock_fetch:
            mock_fetch.return_value = True
            
            result = scheduler.fetch_rss_source(1, mock_database_session)
            
            # 验证
            assert result is True
    
    def test_fetch_rss_source_not_found(self, mock_database_session):
        """测试获取不存在的RSS源"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = None
        
        # 创建服务实例
        scheduler = SchedulerService()
        
        # 执行测试
        result = scheduler.fetch_rss_source(999, mock_database_session)
        
        # 验证
        assert result is False
    
    def test_fetch_rss_source_paused(self, mock_database_session, mock_rss_source):
        """测试获取暂停的RSS源"""
        # 设置mock
        mock_rss_source.is_paused = True
        mock_database_session.exec.return_value.first.return_value = mock_rss_source
        
        # 创建服务实例
        scheduler = SchedulerService()
        
        # 执行测试
        result = scheduler.fetch_rss_source(1, mock_database_session)
        
        # 验证
        assert result is False
    
    def test_schedule_rss_source_success(self, mock_database_session, mock_rss_source):
        """测试调度RSS源成功"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_rss_source
        
        # 创建服务实例
        scheduler = SchedulerService()
        
        # 执行测试
        with patch('services.scheduler_service.fetch_rss_feeds') as mock_fetch:
            mock_fetch.return_value = True
            
            result = scheduler.schedule_rss_source(1, mock_database_session)
            
            # 验证
            assert result is True
            assert 1 in scheduler.threads
    
    def test_unschedule_rss_source_success(self):
        """测试取消调度RSS源成功"""
        # 创建服务实例
        scheduler = SchedulerService()
        mock_thread = Mock()
        scheduler.threads[1] = mock_thread
        
        # 执行测试
        result = scheduler.unschedule_rss_source(1)
        
        # 验证
        assert result is True
        assert 1 not in scheduler.threads
        mock_thread.join.assert_called_once()
    
    def test_unschedule_rss_source_not_found(self):
        """测试取消调度不存在的RSS源"""
        # 创建服务实例
        scheduler = SchedulerService()
        
        # 执行测试
        result = scheduler.unschedule_rss_source(999)
        
        # 验证
        assert result is False
    
    def test_cleanup_finished_threads(self):
        """测试清理完成的线程"""
        # 创建服务实例
        scheduler = SchedulerService()
        
        # 创建模拟线程
        mock_thread1 = Mock()
        mock_thread1.is_alive.return_value = False
        mock_thread2 = Mock()
        mock_thread2.is_alive.return_value = True
        
        scheduler.threads = {1: mock_thread1, 2: mock_thread2}
        
        # 执行测试
        scheduler.cleanup_finished_threads()
        
        # 验证
        assert 1 not in scheduler.threads
        assert 2 in scheduler.threads
    
    def test_get_thread_info_success(self):
        """测试获取线程信息成功"""
        # 创建服务实例
        scheduler = SchedulerService()
        
        # 创建模拟线程
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        mock_thread.name = "RSS-Thread-1"
        
        scheduler.threads = {1: mock_thread}
        
        # 执行测试
        info = scheduler.get_thread_info(1)
        
        # 验证
        assert info is not None
        assert info['thread_id'] == 1
        assert info['is_alive'] is True
        assert info['name'] == "RSS-Thread-1"
    
    def test_get_thread_info_not_found(self):
        """测试获取不存在的线程信息"""
        # 创建服务实例
        scheduler = SchedulerService()
        
        # 执行测试
        info = scheduler.get_thread_info(999)
        
        # 验证
        assert info is None
    
    def test_restart_scheduler_success(self, mock_database_session, mock_rss_source):
        """测试重启调度器成功"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_rss_source]
        
        # 创建服务实例
        scheduler = SchedulerService()
        scheduler.running = True
        
        # 执行测试
        with patch('services.scheduler_service.fetch_rss_feeds') as mock_fetch:
            mock_fetch.return_value = True
            
            result = scheduler.restart(mock_database_session)
            
            # 验证
            assert result is True
            assert scheduler.running is True
    
    def test_restart_scheduler_not_running(self, mock_database_session, mock_rss_source):
        """测试重启未运行的调度器"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_rss_source]
        
        # 创建服务实例
        scheduler = SchedulerService()
        scheduler.running = False
        
        # 执行测试
        with patch('services.scheduler_service.fetch_rss_feeds') as mock_fetch:
            mock_fetch.return_value = True
            
            result = scheduler.restart(mock_database_session)
            
            # 验证
            assert result is True
            assert scheduler.running is True
