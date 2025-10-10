"""
其他API测试
测试文档、RSS、调度器等API接口
"""
import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestDocumentAPI:
    """文档API测试"""
    
    def test_upload_excel_success(self, test_client, auth_headers):
        """测试Excel文档上传成功"""
        # 创建测试Excel文件
        import io
        import pandas as pd
        
        # 创建测试数据
        test_data = {
            'title': ['测试文档1', '测试文档2'],
            'content': ['测试内容1', '测试内容2'],
            'link': ['http://test1.com', 'http://test2.com'],
            'description': ['测试描述1', '测试描述2'],
            'author': ['作者1', '作者2'],
            'tags': ['tag1,tag2', 'tag3,tag4']
        }
        
        # 创建DataFrame并转换为Excel
        df = pd.DataFrame(test_data)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        # 发送请求
        response = test_client.post(
            '/api/documents/upload-excel',
            headers=auth_headers,
            data={
                'file': (excel_buffer, 'test.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
    
    def test_get_documents_success(self, test_client, auth_headers):
        """测试获取文档列表成功"""
        # 实际API路径是 /api/documents 而不是 /api/document/list
        response = test_client.get(
            '/api/documents',
            headers=auth_headers
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_delete_document_success(self, test_client, auth_headers):
        """测试删除文档成功"""
        with patch('apis.document.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_doc = Mock()
            mock_doc.id = 1
            mock_doc.title = '测试文档'
            mock_session.exec.return_value.first.return_value = mock_doc
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.delete(
                '/api/documents/1',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
    
    def test_document_not_found(self, test_client, auth_headers):
        """测试文档不存在"""
        with patch('apis.document.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_session.exec.return_value.first.return_value = None
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.delete(
                '/api/documents/999',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data


class TestRSSAPI:
    """RSS API测试"""
    
    def test_get_rss_sources_success(self, test_client, auth_headers):
        """测试获取RSS源成功"""
        # 发送请求
        response = test_client.get(
            '/api/rss/sources',
            headers=auth_headers
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_add_rss_source_success(self, test_client):
        """测试添加RSS源成功"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_session.exec.return_value.first.return_value = None  # 没有重复的URL
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            with patch('apis.source.RSSSource') as mock_source_class:
                mock_source_instance = Mock()
                mock_source_instance.id = 1
                mock_source_instance.name = '新RSS源'
                mock_source_instance.url = 'https://example.com/new-rss'
                mock_source_instance.interval = 'ONE_DAY'
                mock_source_class.return_value = mock_source_instance
                
                # 发送请求
                response = test_client.post(
                    '/api/rss/sources',
                    json={
                        'name': '新RSS源',
                        'url': 'https://example.com/new-rss',
                        'interval': 'ONE_DAY'
                    }
                )
                
                # 验证响应
                assert response.status_code == 201
                data = json.loads(response.data)
                assert data['name'] == '新RSS源'
    
    def test_update_rss_source_success(self, test_client):
        """测试更新RSS源成功"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_source = Mock()
            mock_source.id = 1
            mock_source.name = '测试RSS源'
            mock_source.url = 'https://example.com/test-rss'
            mock_source.interval = 'ONE_DAY'
            mock_session.exec.return_value.first.return_value = mock_source
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 更新RSS源
            response = test_client.put(
                '/api/rss/sources/1',
                json={
                    'name': '更新RSS源',
                    'url': 'https://example.com/updated-rss',
                    'interval': 'TWELVE_HOUR'
                }
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['name'] == '更新RSS源'
    
    def test_delete_rss_source_success(self, test_client, auth_headers):
        """测试删除RSS源成功"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_source = Mock()
            mock_source.id = 1
            mock_source.name = '测试RSS源'
            mock_session.exec.return_value.first.return_value = mock_source
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 删除RSS源
            response = test_client.delete(
                '/api/rss/sources/1',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data


class TestSchedulerAPI:
    """调度器API测试"""
    
    def test_get_scheduler_status_success(self, test_client, auth_headers):
        """测试获取调度器状态成功"""
        # 发送请求
        response = test_client.get(
            '/api/scheduler/status',
            headers=auth_headers
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
        assert 'data' in data
    
    def test_start_scheduler_success(self, test_client):
        """测试启动调度器成功"""
        with patch('apis.scheduler.scheduler_service') as mock_scheduler:
            # 设置mock
            mock_scheduler.running = False
            mock_scheduler.start.return_value = None
            
            with patch('apis.scheduler.Session') as mock_session_class:
                mock_session = Mock()
                mock_rss_source = Mock()
                mock_rss_source.id = 1
                mock_rss_source.name = '测试RSS源'
                mock_rss_source.is_paused = False
                
                mock_session.exec.return_value.all.return_value = [mock_rss_source]
                mock_session_class.return_value.__enter__.return_value = mock_session
                
                with patch('apis.scheduler.os.getenv') as mock_getenv:
                    mock_getenv.return_value = 'true'  # 允许手动启动
                    
                    # 发送请求
                    response = test_client.post('/api/scheduler/start')
                    
                    # 验证响应
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert 'success' in data
                    assert data['success'] is True
    
    def test_stop_scheduler_success(self, test_client, auth_headers):
        """测试停止调度器成功"""
        # 发送请求
        response = test_client.post(
            '/api/scheduler/stop',
            headers=auth_headers
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
    
    def test_fetch_rss_now_success(self, test_client, auth_headers):
        """测试立即获取RSS成功"""
        with patch('apis.scheduler.fetch_rss_feeds') as mock_fetch:
            # 设置mock
            mock_fetch.return_value = True
            
            with patch('apis.scheduler.Session') as mock_session_class:
                mock_session = Mock()
                mock_rss_source = Mock()
                mock_rss_source.id = 1
                mock_rss_source.name = '测试RSS源'
                mock_rss_source.is_paused = False
                
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


class TestAnalyticsAPI:
    """分析API测试"""
    
    def test_get_analytics_success(self, test_client, auth_headers):
        """测试获取分析数据成功"""
        with patch('apis.analytics.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_analysis = Mock()
            mock_analysis.id = 1
            mock_analysis.title = '测试分析'
            mock_analysis.analysis_type = 'clustering'
            mock_analysis.results = {'clusters': 3}
            
            mock_session.exec.return_value.all.return_value = [mock_analysis]
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.get(
                '/api/analytics',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]['title'] == '测试分析'
    
    def test_get_analytics_with_filters(self, test_client, auth_headers):
        """测试带过滤器的分析数据"""
        with patch('apis.analytics.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_analysis = Mock()
            mock_analysis.id = 1
            mock_analysis.title = '测试分析'
            mock_analysis.analysis_type = 'clustering'
            mock_analysis.results = {'clusters': 3}
            
            mock_session.exec.return_value.all.return_value = [mock_analysis]
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.get(
                '/api/analytics?type=clustering',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]['analysis_type'] == 'clustering'


class TestErrorHandling:
    """错误处理测试"""
    
    def test_invalid_endpoint(self, test_client, auth_headers):
        """测试无效端点"""
        response = test_client.get(
            '/api/invalid/endpoint',
            headers=auth_headers
        )
        
        # 验证响应
        assert response.status_code == 404
    
    def test_method_not_allowed(self, test_client, auth_headers):
        """测试不允许的HTTP方法"""
        response = test_client.put(
            '/api/assistant/query',
            headers=auth_headers,
            json={'query': '测试'}
        )
        
        # 验证响应
        assert response.status_code == 405
    
    def test_server_error(self, test_client, auth_headers):
        """测试服务器错误"""
        with patch('apis.assistant.get_assistant') as mock_get_assistant:
            # 设置mock抛出异常
            mock_get_assistant.side_effect = Exception("服务器内部错误")
            
            # 发送请求
            response = test_client.post(
                '/api/assistant/query',
                headers=auth_headers,
                json={'query': '测试查询'}
            )
            
            # 验证响应
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

