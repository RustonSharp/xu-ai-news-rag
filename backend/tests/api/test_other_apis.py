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
    
    def test_upload_document_success(self, test_client, auth_headers):
        """测试文档上传成功"""
        with patch('apis.document.upload_document') as mock_upload:
            # 设置mock
            mock_upload.return_value = {
                'message': '文档上传成功',
                'document_id': 'test_doc_123'
            }
            
            # 发送请求
            response = test_client.post(
                '/api/document/upload',
                headers=auth_headers,
                json={
                    'title': '测试文档',
                    'content': '测试内容',
                    'source': 'test_source'
                }
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert data['message'] == '文档上传成功'
    
    def test_get_documents_success(self, test_client, auth_headers):
        """测试获取文档列表成功"""
        with patch('apis.document.get_documents') as mock_get_docs:
            # 设置mock
            mock_get_docs.return_value = [
                {
                    'id': 1,
                    'title': '测试文档1',
                    'source': 'test_source',
                    'created_at': '2025-01-01T00:00:00'
                },
                {
                    'id': 2,
                    'title': '测试文档2',
                    'source': 'test_source',
                    'created_at': '2025-01-02T00:00:00'
                }
            ]
            
            # 发送请求
            response = test_client.get(
                '/api/document/list',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'documents' in data
            assert len(data['documents']) == 2
    
    def test_delete_document_success(self, test_client, auth_headers):
        """测试删除文档成功"""
        with patch('apis.document.delete_document') as mock_delete:
            # 设置mock
            mock_delete.return_value = {'message': '文档删除成功'}
            
            # 发送请求
            response = test_client.delete(
                '/api/document/1',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert data['message'] == '文档删除成功'
    
    def test_document_not_found(self, test_client, auth_headers):
        """测试文档不存在"""
        with patch('apis.document.delete_document') as mock_delete:
            # 设置mock抛出异常
            mock_delete.side_effect = Exception("文档不存在")
            
            # 发送请求
            response = test_client.delete(
                '/api/document/999',
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
        with patch('apis.rss.get_rss_sources') as mock_get_sources:
            # 设置mock
            mock_get_sources.return_value = [
                {
                    'id': 1,
                    'name': '测试RSS源',
                    'url': 'https://example.com/rss',
                    'is_active': True
                }
            ]
            
            # 发送请求
            response = test_client.get(
                '/api/rss/sources',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'sources' in data
            assert len(data['sources']) == 1
    
    def test_add_rss_source_success(self, test_client, auth_headers):
        """测试添加RSS源成功"""
        with patch('apis.rss.add_rss_source') as mock_add_source:
            # 设置mock
            mock_add_source.return_value = {
                'message': 'RSS源添加成功',
                'source_id': 1
            }
            
            # 发送请求
            response = test_client.post(
                '/api/rss/sources',
                headers=auth_headers,
                json={
                    'name': '新RSS源',
                    'url': 'https://example.com/new-rss',
                    'interval': 3600
                }
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert data['message'] == 'RSS源添加成功'
    
    def test_update_rss_source_success(self, test_client, auth_headers):
        """测试更新RSS源成功"""
        with patch('apis.rss.update_rss_source') as mock_update_source:
            # 设置mock
            mock_update_source.return_value = {'message': 'RSS源更新成功'}
            
            # 发送请求
            response = test_client.put(
                '/api/rss/sources/1',
                headers=auth_headers,
                json={
                    'name': '更新的RSS源',
                    'url': 'https://example.com/updated-rss',
                    'is_active': True
                }
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert data['message'] == 'RSS源更新成功'
    
    def test_delete_rss_source_success(self, test_client, auth_headers):
        """测试删除RSS源成功"""
        with patch('apis.rss.delete_rss_source') as mock_delete_source:
            # 设置mock
            mock_delete_source.return_value = {'message': 'RSS源删除成功'}
            
            # 发送请求
            response = test_client.delete(
                '/api/rss/sources/1',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert data['message'] == 'RSS源删除成功'


class TestSchedulerAPI:
    """调度器API测试"""
    
    def test_get_scheduler_status_success(self, test_client, auth_headers):
        """测试获取调度器状态成功"""
        with patch('apis.scheduler.get_scheduler_status') as mock_get_status:
            # 设置mock
            mock_get_status.return_value = {
                'is_running': True,
                'last_run': '2025-01-01T12:00:00',
                'next_run': '2025-01-01T13:00:00',
                'total_sources': 5,
                'active_sources': 3
            }
            
            # 发送请求
            response = test_client.get(
                '/api/scheduler/status',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'is_running' in data
            assert data['is_running'] is True
    
    def test_start_scheduler_success(self, test_client, auth_headers):
        """测试启动调度器成功"""
        with patch('apis.scheduler.start_scheduler') as mock_start:
            # 设置mock
            mock_start.return_value = {'message': '调度器启动成功'}
            
            # 发送请求
            response = test_client.post(
                '/api/scheduler/start',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert data['message'] == '调度器启动成功'
    
    def test_stop_scheduler_success(self, test_client, auth_headers):
        """测试停止调度器成功"""
        with patch('apis.scheduler.stop_scheduler') as mock_stop:
            # 设置mock
            mock_stop.return_value = {'message': '调度器停止成功'}
            
            # 发送请求
            response = test_client.post(
                '/api/scheduler/stop',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert data['message'] == '调度器停止成功'
    
    def test_trigger_scheduler_success(self, test_client, auth_headers):
        """测试手动触发调度器成功"""
        with patch('apis.scheduler.trigger_scheduler') as mock_trigger:
            # 设置mock
            mock_trigger.return_value = {
                'message': '调度器触发成功',
                'processed_sources': 3,
                'new_documents': 5
            }
            
            # 发送请求
            response = test_client.post(
                '/api/scheduler/trigger',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert data['message'] == '调度器触发成功'


class TestAnalyticsAPI:
    """分析API测试"""
    
    def test_get_analytics_success(self, test_client, auth_headers):
        """测试获取分析数据成功"""
        with patch('apis.analytics.get_analytics') as mock_get_analytics:
            # 设置mock
            mock_get_analytics.return_value = {
                'total_documents': 100,
                'total_sources': 5,
                'documents_by_source': [
                    {'source': 'source1', 'count': 50},
                    {'source': 'source2', 'count': 30},
                    {'source': 'source3', 'count': 20}
                ],
                'documents_by_date': [
                    {'date': '2025-01-01', 'count': 10},
                    {'date': '2025-01-02', 'count': 15}
                ]
            }
            
            # 发送请求
            response = test_client.get(
                '/api/analytics',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'total_documents' in data
            assert data['total_documents'] == 100
    
    def test_get_analytics_with_filters(self, test_client, auth_headers):
        """测试带过滤器的分析数据"""
        with patch('apis.analytics.get_analytics') as mock_get_analytics:
            # 设置mock
            mock_get_analytics.return_value = {
                'total_documents': 50,
                'total_sources': 3,
                'documents_by_source': [
                    {'source': 'filtered_source', 'count': 50}
                ]
            }
            
            # 发送请求
            response = test_client.get(
                '/api/analytics?start_date=2025-01-01&end_date=2025-01-31&source=filtered_source',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'total_documents' in data
            assert data['total_documents'] == 50


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

