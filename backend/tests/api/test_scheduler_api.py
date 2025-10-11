"""
调度器API测试
"""
import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestSchedulerAPI:
    """调度器API测试"""
    
    def test_get_scheduler_status_success(self, test_client, auth_headers):
        """测试获取调度器状态成功"""
        with patch('apis.scheduler.scheduler_service') as mock_scheduler:
            # 设置mock
            mock_scheduler.running = True
            mock_scheduler.threads = {1: Mock(), 2: Mock()}
            mock_scheduler.lock = Mock()
            mock_scheduler.__enter__ = Mock(return_value=mock_scheduler)
            mock_scheduler.__exit__ = Mock(return_value=None)
            
            with patch('apis.scheduler.Session') as mock_session_class:
                mock_session = Mock()
                mock_rss_source = Mock()
                mock_rss_source.id = 1
                mock_rss_source.name = '测试RSS源'
                mock_rss_source.url = 'http://test.com/rss'
                mock_rss_source.interval = 'ONE_DAY'
                mock_rss_source.is_paused = False
                
                mock_session.exec.return_value.all.return_value = [mock_rss_source]
                mock_session_class.return_value.__enter__.return_value = mock_session
                
                # 发送请求
                response = test_client.get(
                    '/api/scheduler/status',
                    headers=auth_headers
                )
                
                # 验证响应
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'success' in data
                assert data['success'] is True
                assert 'data' in data
                assert 'running' in data['data']
                assert data['data']['running'] is True
                assert 'thread_count' in data['data']
                assert data['data']['thread_count'] == 2
    
    def test_get_scheduler_status_stopped(self, test_client, auth_headers):
        """测试获取停止状态的调度器"""
        with patch('apis.scheduler.scheduler_service') as mock_scheduler:
            # 设置mock
            mock_scheduler.running = False
            mock_scheduler.threads = {}
            mock_scheduler.lock = Mock()
            mock_scheduler.__enter__ = Mock(return_value=mock_scheduler)
            mock_scheduler.__exit__ = Mock(return_value=None)
            
            with patch('apis.scheduler.Session') as mock_session_class:
                mock_session = Mock()
                mock_session.exec.return_value.all.return_value = []
                mock_session_class.return_value.__enter__.return_value = mock_session
                
                # 发送请求
                response = test_client.get(
                    '/api/scheduler/status',
                    headers=auth_headers
                )
                
                # 验证响应
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'success' in data
                assert data['success'] is True
                assert 'data' in data
                assert 'running' in data['data']
                assert data['data']['running'] is False
                assert 'thread_count' in data['data']
                assert data['data']['thread_count'] == 0
    
    def test_start_scheduler_success(self, test_client, auth_headers):
        """测试启动调度器成功"""
        with patch('apis.scheduler.scheduler_service') as mock_scheduler:
            # 设置mock
            mock_scheduler.running = False
            mock_scheduler.start.return_value = None
            mock_scheduler.__enter__ = Mock(return_value=mock_scheduler)
            mock_scheduler.__exit__ = Mock(return_value=None)
            
            with patch('apis.scheduler.Session') as mock_session_class:
                mock_session = Mock()
                mock_rss_source = Mock()
                mock_rss_source.id = 1
                mock_rss_source.name = '测试RSS源'
                mock_rss_source.url = 'http://test.com/rss'
                mock_rss_source.interval = 'ONE_DAY'
                mock_rss_source.is_paused = False
                
                mock_session.exec.return_value.all.return_value = [mock_rss_source]
                mock_session_class.return_value.__enter__.return_value = mock_session
                
                with patch('apis.scheduler.os.getenv') as mock_getenv:
                    mock_getenv.return_value = 'true'  # 允许手动启动
                    
                    # 发送请求
                    response = test_client.post(
                        '/api/scheduler/start',
                        headers=auth_headers
                    )
                    
                    # 验证响应
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert 'success' in data
                    assert data['success'] is True
                    assert 'message' in data
                    mock_scheduler.start.assert_called_once()
    
    def test_start_scheduler_already_running(self, test_client, auth_headers):
        """测试启动已运行的调度器"""
        with patch('apis.scheduler.scheduler_service') as mock_scheduler:
            # 设置mock
            mock_scheduler.running = True
            mock_scheduler.__enter__ = Mock(return_value=mock_scheduler)
            mock_scheduler.__exit__ = Mock(return_value=None)
            
            with patch('apis.scheduler.Session') as mock_session_class:
                mock_session = Mock()
                mock_session.exec.return_value.all.return_value = []
                mock_session_class.return_value.__enter__.return_value = mock_session
                
                # 发送请求
                response = test_client.post(
                    '/api/scheduler/start',
                    headers=auth_headers
                )
                
                # 验证响应
                assert response.status_code == 400
                data = json.loads(response.data)
                assert 'error' in data
                assert 'already running' in data['error']
    
    def test_start_scheduler_not_allowed(self, test_client, auth_headers):
        """测试不允许手动启动调度器"""
        with patch('apis.scheduler.scheduler_service') as mock_scheduler:
            # 设置mock
            mock_scheduler.running = False
            mock_scheduler.__enter__ = Mock(return_value=mock_scheduler)
            mock_scheduler.__exit__ = Mock(return_value=None)
            
            with patch('apis.scheduler.Session') as mock_session_class:
                mock_session = Mock()
                mock_session.exec.return_value.all.return_value = []
                mock_session_class.return_value.__enter__.return_value = mock_session
                
                with patch('apis.scheduler.os.getenv') as mock_getenv:
                    mock_getenv.return_value = 'false'  # 不允许手动启动
                    
                    # 发送请求
                    response = test_client.post(
                        '/api/scheduler/start',
                        headers=auth_headers
                    )
                    
                    # 验证响应
                    assert response.status_code == 403
                    data = json.loads(response.data)
                    assert 'error' in data
                    assert 'not allowed' in data['error']
    
    def test_stop_scheduler_success(self, test_client, auth_headers):
        """测试停止调度器成功"""
        with patch('apis.scheduler.scheduler_service') as mock_scheduler:
            # 设置mock
            mock_scheduler.running = True
            mock_scheduler.stop.return_value = None
            
            # 发送请求
            response = test_client.post(
                '/api/scheduler/stop',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'success' in data
            assert data['success'] is True
            assert 'message' in data
            mock_scheduler.stop.assert_called_once()
    
    def test_stop_scheduler_not_running(self, test_client, auth_headers):
        """测试停止未运行的调度器"""
        with patch('apis.scheduler.scheduler_service') as mock_scheduler:
            # 设置mock
            mock_scheduler.running = False
            
            # 发送请求
            response = test_client.post(
                '/api/scheduler/stop',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'not running' in data['error']
    
    def test_restart_scheduler_success(self, test_client, auth_headers):
        """测试重启调度器成功"""
        with patch('apis.scheduler.scheduler_service') as mock_scheduler:
            # 设置mock
            mock_scheduler.running = True
            mock_scheduler.stop.return_value = None
            mock_scheduler.start.return_value = None
            mock_scheduler.__enter__ = Mock(return_value=mock_scheduler)
            mock_scheduler.__exit__ = Mock(return_value=None)
            
            with patch('apis.scheduler.Session') as mock_session_class:
                mock_session = Mock()
                mock_rss_source = Mock()
                mock_rss_source.id = 1
                mock_rss_source.name = '测试RSS源'
                mock_rss_source.url = 'http://test.com/rss'
                mock_rss_source.interval = 'ONE_DAY'
                mock_rss_source.is_paused = False
                
                mock_session.exec.return_value.all.return_value = [mock_rss_source]
                mock_session_class.return_value.__enter__.return_value = mock_session
                
                with patch('apis.scheduler.os.getenv') as mock_getenv:
                    mock_getenv.return_value = 'true'  # 允许手动启动
                    
                    # 发送请求
                    response = test_client.post(
                        '/api/scheduler/restart',
                        headers=auth_headers
                    )
                    
                    # 验证响应
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert 'success' in data
                    assert data['success'] is True
                    assert 'message' in data
                    mock_scheduler.stop.assert_called_once()
                    mock_scheduler.start.assert_called_once()
    
    def test_fetch_rss_source_success(self, test_client, auth_headers):
        """测试立即获取RSS源成功"""
        with patch('apis.scheduler.fetch_rss_feeds') as mock_fetch:
            # 设置mock
            mock_fetch.return_value = True
            
            with patch('apis.scheduler.Session') as mock_session_class:
                mock_session = Mock()
                mock_rss_source = Mock()
                mock_rss_source.id = 1
                mock_rss_source.name = '测试RSS源'
                mock_rss_source.url = 'http://test.com/rss'
                mock_rss_source.interval = 'ONE_DAY'
                mock_rss_source.is_paused = False
                mock_rss_source.is_active = True
                
                mock_session.exec.return_value.first.return_value = mock_rss_source
                mock_session_class.return_value.__enter__.return_value = mock_session
                
                # 发送请求
                response = test_client.post(
                    '/api/scheduler/fetch/1',
                    headers=auth_headers
                )
                
                # 验证响应
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'success' in data
                assert data['success'] is True
                assert 'message' in data
    
    def test_fetch_rss_source_not_found(self, test_client, auth_headers):
        """测试获取不存在的RSS源"""
        with patch('apis.scheduler.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_session.exec.return_value.first.return_value = None
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.post(
                '/api/scheduler/fetch/999',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
            assert 'not found' in data['error']
    
    def test_fetch_rss_source_paused(self, test_client, auth_headers):
        """测试获取暂停的RSS源"""
        with patch('apis.scheduler.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_rss_source = Mock()
            mock_rss_source.id = 1
            mock_rss_source.name = '测试RSS源'
            mock_rss_source.url = 'http://test.com/rss'
            mock_rss_source.interval = 'ONE_DAY'
            mock_rss_source.is_paused = True  # 暂停状态
            mock_rss_source.is_active = True
            
            mock_session.exec.return_value.first.return_value = mock_rss_source
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.post(
                '/api/scheduler/fetch/1',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'paused' in data['error']
    
    def test_fetch_rss_source_inactive(self, test_client, auth_headers):
        """测试获取非活跃的RSS源"""
        with patch('apis.scheduler.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_rss_source = Mock()
            mock_rss_source.id = 1
            mock_rss_source.name = '测试RSS源'
            mock_rss_source.url = 'http://test.com/rss'
            mock_rss_source.interval = 'ONE_DAY'
            mock_rss_source.is_paused = False
            mock_rss_source.is_active = False  # 非活跃状态
            
            mock_session.exec.return_value.first.return_value = mock_rss_source
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.post(
                '/api/scheduler/fetch/1',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'inactive' in data['error']
    
    def test_fetch_rss_source_failure(self, test_client, auth_headers):
        """测试RSS源获取失败"""
        with patch('apis.scheduler.fetch_rss_feeds') as mock_fetch:
            # 设置mock
            mock_fetch.return_value = False
            
            with patch('apis.scheduler.Session') as mock_session_class:
                mock_session = Mock()
                mock_rss_source = Mock()
                mock_rss_source.id = 1
                mock_rss_source.name = '测试RSS源'
                mock_rss_source.url = 'http://test.com/rss'
                mock_rss_source.interval = 'ONE_DAY'
                mock_rss_source.is_paused = False
                mock_rss_source.is_active = True
                
                mock_session.exec.return_value.first.return_value = mock_rss_source
                mock_session_class.return_value.__enter__.return_value = mock_session
                
                # 发送请求
                response = test_client.post(
                    '/api/scheduler/fetch/1',
                    headers=auth_headers
                )
                
                # 验证响应
                assert response.status_code == 500
                data = json.loads(response.data)
                assert 'error' in data
                assert 'failed' in data['error']
    
    def test_fetch_all_rss_sources_success(self, test_client, auth_headers):
        """测试获取所有RSS源成功"""
        with patch('apis.scheduler.fetch_rss_feeds') as mock_fetch:
            # 设置mock
            mock_fetch.return_value = True
            
            with patch('apis.scheduler.Session') as mock_session_class:
                mock_session = Mock()
                mock_rss_source1 = Mock()
                mock_rss_source1.id = 1
                mock_rss_source1.name = '测试RSS源1'
                mock_rss_source1.url = 'http://test1.com/rss'
                mock_rss_source1.interval = 'ONE_DAY'
                mock_rss_source1.is_paused = False
                mock_rss_source1.is_active = True
                
                mock_rss_source2 = Mock()
                mock_rss_source2.id = 2
                mock_rss_source2.name = '测试RSS源2'
                mock_rss_source2.url = 'http://test2.com/rss'
                mock_rss_source2.interval = 'TWELVE_HOUR'
                mock_rss_source2.is_paused = False
                mock_rss_source2.is_active = True
                
                mock_session.exec.return_value.all.return_value = [mock_rss_source1, mock_rss_source2]
                mock_session_class.return_value.__enter__.return_value = mock_session
                
                # 发送请求
                response = test_client.post(
                    '/api/scheduler/fetch-all',
                    headers=auth_headers
                )
                
                # 验证响应
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'success' in data
                assert data['success'] is True
                assert 'message' in data
                assert 'processed' in data
                assert data['processed'] == 2
    
    def test_get_scheduler_logs_success(self, test_client, auth_headers):
        """测试获取调度器日志成功"""
        with patch('apis.scheduler.scheduler_service') as mock_scheduler:
            # 设置mock
            mock_scheduler.get_logs.return_value = [
                {'timestamp': '2025-01-01T12:00:00', 'level': 'INFO', 'message': '调度器启动'},
                {'timestamp': '2025-01-01T12:01:00', 'level': 'INFO', 'message': '开始获取RSS源'},
                {'timestamp': '2025-01-01T12:02:00', 'level': 'ERROR', 'message': '获取失败'}
            ]
            
            # 发送请求
            response = test_client.get(
                '/api/scheduler/logs',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'logs' in data
            assert isinstance(data['logs'], list)
            assert len(data['logs']) == 3
            assert data['logs'][0]['level'] == 'INFO'
            assert data['logs'][2]['level'] == 'ERROR'
    
    def test_get_scheduler_logs_with_limit(self, test_client, auth_headers):
        """测试获取限制数量的调度器日志"""
        with patch('apis.scheduler.scheduler_service') as mock_scheduler:
            # 设置mock
            mock_scheduler.get_logs.return_value = [
                {'timestamp': '2025-01-01T12:00:00', 'level': 'INFO', 'message': '调度器启动'},
                {'timestamp': '2025-01-01T12:01:00', 'level': 'INFO', 'message': '开始获取RSS源'}
            ]
            
            # 发送请求
            response = test_client.get(
                '/api/scheduler/logs?limit=2',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'logs' in data
            assert isinstance(data['logs'], list)
            assert len(data['logs']) == 2
    
    def test_get_scheduler_metrics_success(self, test_client, auth_headers):
        """测试获取调度器指标成功"""
        with patch('apis.scheduler.scheduler_service') as mock_scheduler:
            # 设置mock
            mock_scheduler.get_metrics.return_value = {
                'total_fetches': 100,
                'successful_fetches': 95,
                'failed_fetches': 5,
                'average_fetch_time': 2.5,
                'last_fetch_time': '2025-01-01T12:00:00',
                'uptime': 3600
            }
            
            # 发送请求
            response = test_client.get(
                '/api/scheduler/metrics',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'metrics' in data
            assert data['metrics']['total_fetches'] == 100
            assert data['metrics']['successful_fetches'] == 95
            assert data['metrics']['failed_fetches'] == 5
            assert data['metrics']['average_fetch_time'] == 2.5
    
    def test_clear_scheduler_logs_success(self, test_client, auth_headers):
        """测试清空调度器日志成功"""
        with patch('apis.scheduler.scheduler_service') as mock_scheduler:
            # 设置mock
            mock_scheduler.clear_logs.return_value = None
            
            # 发送请求
            response = test_client.delete(
                '/api/scheduler/logs',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'success' in data
            assert data['success'] is True
            assert 'message' in data
            mock_scheduler.clear_logs.assert_called_once()
    
    def test_unauthorized_access(self, test_client):
        """测试未授权访问"""
        # 发送请求（无认证头）
        response = test_client.get('/api/scheduler/status')
        
        # 验证响应
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert 'token' in data['error']
    
    def test_invalid_endpoint(self, test_client, auth_headers):
        """测试无效端点"""
        # 发送请求
        response = test_client.get(
            '/api/scheduler/invalid',
            headers=auth_headers
        )
        
        # 验证响应
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
