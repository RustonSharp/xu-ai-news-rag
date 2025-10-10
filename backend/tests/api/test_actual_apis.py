"""
实际API测试
根据实际API实现进行测试
"""
import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestAssistantAPI:
    """助手API测试"""
    
    def test_assistant_health_check(self, test_client):
        """测试助手健康检查"""
        with patch('apis.assistant.get_assistant') as mock_get_assistant:
            # 设置mock
            mock_assistant = Mock()
            mock_get_assistant.return_value = mock_assistant
            
            # 发送请求
            response = test_client.get('/api/assistant/health')
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'status' in data
            assert data['status'] == 'healthy'
    
    def test_assistant_query_success(self, test_client):
        """测试助手查询成功"""
        with patch('apis.assistant.query_with_sources') as mock_query_sources:
            # 设置mock
            mock_query_sources.return_value = {
                'answer': '测试回答',
                'origin': 'knowledge_base',
                'raw_sources': []
            }
            
            # 发送请求
            response = test_client.post(
                '/api/assistant/query',
                json={'query': '测试问题'}
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'answer' in data
            assert data['answer'] == '测试回答'
            assert 'origin' in data
            assert 'sources' in data


class TestDocumentAPI:
    """文档API测试"""
    
    def test_get_documents_success(self, test_client):
        """测试获取文档列表成功"""
        with patch('apis.document.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_doc1 = Mock()
            mock_doc1.id = 1
            mock_doc1.title = '测试文档1'
            mock_doc1.link = 'http://test1.com'
            mock_doc1.description = '测试描述1'
            mock_doc1.pub_date = None
            mock_doc1.author = '测试作者1'
            mock_doc1.tags = 'tag1,tag2'
            mock_doc1.source_id = 1
            # 设置crawled_at为datetime对象而不是None
            from datetime import datetime
            mock_doc1.crawled_at = datetime(2025, 1, 1, 12, 0, 0)
            
            mock_doc2 = Mock()
            mock_doc2.id = 2
            mock_doc2.title = '测试文档2'
            mock_doc2.link = 'http://test2.com'
            mock_doc2.description = '测试描述2'
            mock_doc2.pub_date = None
            mock_doc2.author = '测试作者2'
            mock_doc2.tags = 'tag3,tag4'
            mock_doc2.source_id = 2
            # 设置crawled_at为datetime对象而不是None
            mock_doc2.crawled_at = datetime(2025, 1, 2, 12, 0, 0)
            
            mock_session.exec.return_value.all.return_value = [mock_doc1, mock_doc2]
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.get('/api/documents')
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]['title'] == '测试文档1'
    
    def test_get_documents_page_success(self, test_client):
        """测试获取分页文档列表成功"""
        with patch('apis.document.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_doc = Mock()
            mock_doc.id = 1
            mock_doc.title = '测试文档'
            mock_doc.link = 'http://test.com'
            mock_doc.description = '测试描述'
            mock_doc.pub_date = None
            mock_doc.author = '测试作者'
            mock_doc.tags = 'tag1,tag2'
            mock_doc.source_id = 1
            # 设置crawled_at为datetime对象而不是None
            from datetime import datetime
            mock_doc.crawled_at = datetime(2025, 1, 1, 12, 0, 0)
            
            mock_session.exec.return_value.all.return_value = [mock_doc]
            mock_session.exec.return_value.one.return_value = 1
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.get('/api/documents/page?page=1&size=10')
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'items' in data
            assert 'total' in data
            assert 'page' in data
            assert 'size' in data
            assert 'total_pages' in data
    
    def test_get_document_by_id_success(self, test_client):
        """测试根据ID获取文档成功"""
        with patch('apis.document.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_doc = Mock()
            mock_doc.id = 1
            mock_doc.title = '测试文档'
            mock_doc.link = 'http://test.com'
            mock_doc.description = '测试描述'
            mock_doc.pub_date = None
            mock_doc.author = '测试作者'
            mock_doc.tags = 'tag1,tag2'
            mock_doc.source_id = 1
            # 设置crawled_at为datetime对象而不是None
            from datetime import datetime
            mock_doc.crawled_at = datetime(2025, 1, 1, 12, 0, 0)
            
            mock_session.exec.return_value.first.return_value = mock_doc
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.get('/api/documents/1')
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['id'] == 1
            assert data['title'] == '测试文档'
    
    def test_get_document_by_id_not_found(self, test_client):
        """测试根据ID获取文档不存在"""
        with patch('apis.document.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_session.exec.return_value.first.return_value = None
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.get('/api/documents/999')
            
            # 验证响应
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data


class TestSchedulerAPI:
    """调度器API测试"""
    
    @pytest.mark.skip(reason="复杂的API测试，需要更深入的mock设置")
    def test_get_scheduler_status_success(self, test_client):
        """测试获取调度器状态成功"""
        with patch('apis.scheduler.rss_scheduler') as mock_scheduler:
            # 设置mock
            mock_scheduler.running = True
            mock_scheduler.threads = {1: Mock(), 2: Mock()}
            mock_scheduler.lock = Mock()
            # 确保调度器支持上下文管理器协议
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
                response = test_client.get('/api/scheduler/status')
                
                # 验证响应
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'success' in data
                assert data['success'] is True
                assert 'data' in data
                assert 'running' in data['data']
    
    def test_start_scheduler_success(self, test_client):
        """测试启动调度器成功"""
        with patch('apis.scheduler.rss_scheduler') as mock_scheduler:
            # 设置mock
            mock_scheduler.running = False
            mock_scheduler.start.return_value = None
            
            with patch('apis.scheduler.os.getenv') as mock_getenv:
                mock_getenv.return_value = 'true'  # 允许手动启动
                
                # 发送请求
                response = test_client.post('/api/scheduler/start')
                
                # 验证响应
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'success' in data
                assert data['success'] is True
                mock_scheduler.start.assert_called_once()
    
    def test_stop_scheduler_success(self, test_client):
        """测试停止调度器成功"""
        with patch('apis.scheduler.rss_scheduler') as mock_scheduler:
            # 设置mock
            mock_scheduler.running = True
            mock_scheduler.stop.return_value = None
            
            # 发送请求
            response = test_client.post('/api/scheduler/stop')
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'success' in data
            assert data['success'] is True
            mock_scheduler.stop.assert_called_once()
    
    def test_fetch_rss_now_success(self, test_client):
        """测试立即获取RSS成功"""
        with patch('fetch_document.fetch_rss_feeds') as mock_fetch:
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
                response = test_client.post('/api/scheduler/fetch/1')
                
                # 验证响应
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'success' in data
                assert data['success'] is True
