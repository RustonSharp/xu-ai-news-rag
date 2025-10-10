"""
RSS源管理API测试
"""
import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestRSSSourceAPI:
    """RSS源管理API测试"""
    
    def test_get_rss_sources_success(self, test_client, auth_headers):
        """测试获取RSS源列表成功"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_source1 = Mock()
            mock_source1.id = 1
            mock_source1.name = '测试RSS源1'
            mock_source1.url = 'http://test1.com/rss'
            mock_source1.interval = 'ONE_DAY'
            mock_source1.is_paused = False
            mock_source1.is_active = True
            
            mock_source2 = Mock()
            mock_source2.id = 2
            mock_source2.name = '测试RSS源2'
            mock_source2.url = 'http://test2.com/rss'
            mock_source2.interval = 'TWELVE_HOUR'
            mock_source2.is_paused = True
            mock_source2.is_active = True
            
            mock_session.exec.return_value.all.return_value = [mock_source1, mock_source2]
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.get(
                '/api/rss/sources',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]['name'] == '测试RSS源1'
            assert data[1]['name'] == '测试RSS源2'
    
    def test_get_rss_sources_empty(self, test_client, auth_headers):
        """测试获取空RSS源列表"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_session.exec.return_value.all.return_value = []
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.get(
                '/api/rss/sources',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) == 0
    
    def test_get_rss_source_by_id_success(self, test_client, auth_headers):
        """测试根据ID获取RSS源成功"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_source = Mock()
            mock_source.id = 1
            mock_source.name = '测试RSS源'
            mock_source.url = 'http://test.com/rss'
            mock_source.interval = 'ONE_DAY'
            mock_source.is_paused = False
            mock_source.is_active = True
            
            mock_session.exec.return_value.first.return_value = mock_source
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.get(
                '/api/rss/sources/1',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['id'] == 1
            assert data['name'] == '测试RSS源'
            assert data['url'] == 'http://test.com/rss'
    
    def test_get_rss_source_by_id_not_found(self, test_client, auth_headers):
        """测试根据ID获取RSS源不存在"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_session.exec.return_value.first.return_value = None
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.get(
                '/api/rss/sources/999',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_create_rss_source_success(self, test_client, auth_headers):
        """测试创建RSS源成功"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_session.exec.return_value.first.return_value = None  # 没有重复的URL
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            with patch('apis.source.RSSSource') as mock_source_class:
                mock_source_instance = Mock()
                mock_source_instance.id = 1
                mock_source_instance.name = '新RSS源'
                mock_source_instance.url = 'http://new.com/rss'
                mock_source_instance.interval = 'ONE_DAY'
                mock_source_instance.is_paused = False
                mock_source_instance.is_active = True
                mock_source_class.return_value = mock_source_instance
                
                # 发送请求
                response = test_client.post(
                    '/api/rss/sources',
                    headers=auth_headers,
                    json={
                        'name': '新RSS源',
                        'url': 'http://new.com/rss',
                        'interval': 'ONE_DAY'
                    }
                )
                
                # 验证响应
                assert response.status_code == 201
                data = json.loads(response.data)
                assert data['name'] == '新RSS源'
                assert data['url'] == 'http://new.com/rss'
                assert data['interval'] == 'ONE_DAY'
    
    def test_create_rss_source_duplicate_url(self, test_client, auth_headers):
        """测试创建重复URL的RSS源"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_existing_source = Mock()
            mock_existing_source.url = 'http://existing.com/rss'
            mock_session.exec.return_value.first.return_value = mock_existing_source
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.post(
                '/api/rss/sources',
                headers=auth_headers,
                json={
                    'name': '重复RSS源',
                    'url': 'http://existing.com/rss',
                    'interval': 'ONE_DAY'
                }
            )
            
            # 验证响应
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'url' in data['error']
    
    def test_create_rss_source_invalid_url(self, test_client, auth_headers):
        """测试创建无效URL的RSS源"""
        # 发送请求
        response = test_client.post(
            '/api/rss/sources',
            headers=auth_headers,
            json={
                'name': '无效RSS源',
                'url': 'invalid_url',
                'interval': 'ONE_DAY'
            }
        )
        
        # 验证响应
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'url' in data['error']
    
    def test_create_rss_source_missing_fields(self, test_client, auth_headers):
        """测试缺少必填字段创建RSS源"""
        # 发送请求
        response = test_client.post(
            '/api/rss/sources',
            headers=auth_headers,
            json={
                'name': '测试RSS源'
                # 缺少url和interval
            }
        )
        
        # 验证响应
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_rss_source_success(self, test_client, auth_headers):
        """测试更新RSS源成功"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_source = Mock()
            mock_source.id = 1
            mock_source.name = '测试RSS源'
            mock_source.url = 'http://test.com/rss'
            mock_source.interval = 'ONE_DAY'
            mock_source.is_paused = False
            mock_source.is_active = True
            
            mock_session.exec.return_value.first.return_value = mock_source
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.put(
                '/api/rss/sources/1',
                headers=auth_headers,
                json={
                    'name': '更新的RSS源',
                    'url': 'http://updated.com/rss',
                    'interval': 'TWELVE_HOUR'
                }
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['name'] == '更新的RSS源'
            assert data['url'] == 'http://updated.com/rss'
            assert data['interval'] == 'TWELVE_HOUR'
    
    def test_update_rss_source_not_found(self, test_client, auth_headers):
        """测试更新不存在的RSS源"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_session.exec.return_value.first.return_value = None
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.put(
                '/api/rss/sources/999',
                headers=auth_headers,
                json={
                    'name': '更新的RSS源',
                    'url': 'http://updated.com/rss',
                    'interval': 'TWELVE_HOUR'
                }
            )
            
            # 验证响应
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_update_rss_source_duplicate_url(self, test_client, auth_headers):
        """测试更新为重复URL的RSS源"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_source = Mock()
            mock_source.id = 1
            mock_source.name = '测试RSS源'
            mock_source.url = 'http://test.com/rss'
            mock_source.interval = 'ONE_DAY'
            mock_source.is_paused = False
            mock_source.is_active = True
            
            mock_existing_source = Mock()
            mock_existing_source.id = 2
            mock_existing_source.url = 'http://existing.com/rss'
            
            # 第一次查询返回要更新的源，第二次查询返回已存在的源
            mock_session.exec.return_value.first.side_effect = [mock_source, mock_existing_source]
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.put(
                '/api/rss/sources/1',
                headers=auth_headers,
                json={
                    'name': '更新的RSS源',
                    'url': 'http://existing.com/rss',  # 重复的URL
                    'interval': 'TWELVE_HOUR'
                }
            )
            
            # 验证响应
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'url' in data['error']
    
    def test_delete_rss_source_success(self, test_client, auth_headers):
        """测试删除RSS源成功"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_source = Mock()
            mock_source.id = 1
            mock_source.name = '测试RSS源'
            mock_source.url = 'http://test.com/rss'
            mock_source.interval = 'ONE_DAY'
            mock_source.is_paused = False
            mock_source.is_active = True
            
            mock_session.exec.return_value.first.return_value = mock_source
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.delete(
                '/api/rss/sources/1',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
    
    def test_delete_rss_source_not_found(self, test_client, auth_headers):
        """测试删除不存在的RSS源"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_session.exec.return_value.first.return_value = None
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.delete(
                '/api/rss/sources/999',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_pause_rss_source_success(self, test_client, auth_headers):
        """测试暂停RSS源成功"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_source = Mock()
            mock_source.id = 1
            mock_source.name = '测试RSS源'
            mock_source.url = 'http://test.com/rss'
            mock_source.interval = 'ONE_DAY'
            mock_source.is_paused = False
            mock_source.is_active = True
            
            mock_session.exec.return_value.first.return_value = mock_source
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.post(
                '/api/rss/sources/1/pause',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert mock_source.is_paused is True
    
    def test_resume_rss_source_success(self, test_client, auth_headers):
        """测试恢复RSS源成功"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_source = Mock()
            mock_source.id = 1
            mock_source.name = '测试RSS源'
            mock_source.url = 'http://test.com/rss'
            mock_source.interval = 'ONE_DAY'
            mock_source.is_paused = True  # 设置为暂停状态
            mock_source.is_active = True
            
            mock_session.exec.return_value.first.return_value = mock_source
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.post(
                '/api/rss/sources/1/resume',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert mock_source.is_paused is False
    
    def test_pause_rss_source_not_found(self, test_client, auth_headers):
        """测试暂停不存在的RSS源"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_session.exec.return_value.first.return_value = None
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.post(
                '/api/rss/sources/999/pause',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_resume_rss_source_not_found(self, test_client, auth_headers):
        """测试恢复不存在的RSS源"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_session.exec.return_value.first.return_value = None
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.post(
                '/api/rss/sources/999/resume',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_get_rss_source_statistics_success(self, test_client, auth_headers):
        """测试获取RSS源统计成功"""
        with patch('apis.source.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_session.exec.return_value.one.return_value = 5  # 总源数
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.get(
                '/api/rss/sources/statistics',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'total_sources' in data
            assert data['total_sources'] == 5
    
    def test_validate_rss_url_success(self, test_client, auth_headers):
        """测试验证RSS URL成功"""
        with patch('apis.source.validate_rss_url') as mock_validate:
            # 设置mock
            mock_validate.return_value = True
            
            # 发送请求
            response = test_client.post(
                '/api/rss/sources/validate-url',
                headers=auth_headers,
                json={'url': 'http://test.com/rss'}
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'valid' in data
            assert data['valid'] is True
    
    def test_validate_rss_url_invalid(self, test_client, auth_headers):
        """测试验证无效RSS URL"""
        with patch('apis.source.validate_rss_url') as mock_validate:
            # 设置mock
            mock_validate.return_value = False
            
            # 发送请求
            response = test_client.post(
                '/api/rss/sources/validate-url',
                headers=auth_headers,
                json={'url': 'invalid_url'}
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'valid' in data
            assert data['valid'] is False
    
    def test_validate_rss_url_missing_url(self, test_client, auth_headers):
        """测试验证缺少URL参数"""
        # 发送请求
        response = test_client.post(
            '/api/rss/sources/validate-url',
            headers=auth_headers,
            json={}
        )
        
        # 验证响应
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'url' in data['error']
