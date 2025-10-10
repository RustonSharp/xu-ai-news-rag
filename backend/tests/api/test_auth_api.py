"""
认证API测试
"""
import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestAuthAPI:
    """认证API测试"""
    
    def test_register_user_success(self, test_client):
        """测试用户注册成功"""
        with patch('apis.auth.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_session.exec.return_value.first.return_value = None  # 用户不存在
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            with patch('apis.auth.User') as mock_user_class:
                mock_user_instance = Mock()
                mock_user_instance.id = 1
                mock_user_instance.username = 'test_user'
                mock_user_instance.email = 'test@example.com'
                mock_user_class.return_value = mock_user_instance
                
                # 发送请求
                response = test_client.post(
                    '/api/auth/register',
                    json={
                        'username': 'test_user',
                        'email': 'test@example.com',
                        'password': 'password123'
                    }
                )
                
                # 验证响应
                assert response.status_code == 201
                data = json.loads(response.data)
                assert 'message' in data
                assert 'user' in data
                assert data['user']['username'] == 'test_user'
    
    def test_register_user_duplicate_username(self, test_client):
        """测试重复用户名注册"""
        with patch('apis.auth.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_existing_user = Mock()
            mock_existing_user.username = 'test_user'
            mock_session.exec.return_value.first.return_value = mock_existing_user
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.post(
                '/api/auth/register',
                json={
                    'username': 'test_user',
                    'email': 'test@example.com',
                    'password': 'password123'
                }
            )
            
            # 验证响应
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'username' in data['error']
    
    def test_register_user_duplicate_email(self, test_client):
        """测试重复邮箱注册"""
        with patch('apis.auth.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_existing_user = Mock()
            mock_existing_user.email = 'test@example.com'
            mock_session.exec.return_value.first.return_value = mock_existing_user
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.post(
                '/api/auth/register',
                json={
                    'username': 'new_user',
                    'email': 'test@example.com',
                    'password': 'password123'
                }
            )
            
            # 验证响应
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'email' in data['error']
    
    def test_register_user_missing_fields(self, test_client):
        """测试缺少必填字段注册"""
        # 发送请求
        response = test_client.post(
            '/api/auth/register',
            json={
                'username': 'test_user'
                # 缺少email和password
            }
        )
        
        # 验证响应
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_register_user_invalid_email(self, test_client):
        """测试无效邮箱注册"""
        # 发送请求
        response = test_client.post(
            '/api/auth/register',
            json={
                'username': 'test_user',
                'email': 'invalid_email',
                'password': 'password123'
            }
        )
        
        # 验证响应
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_login_success(self, test_client):
        """测试用户登录成功"""
        with patch('apis.auth.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = 'test_user'
            mock_user.email = 'test@example.com'
            mock_user.is_active = True
            mock_user.hashed_password = 'hashed_password'
            mock_session.exec.return_value.first.return_value = mock_user
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            with patch('apis.auth.verify_password') as mock_verify_password:
                mock_verify_password.return_value = True
                
                with patch('apis.auth.create_access_token') as mock_create_token:
                    mock_create_token.return_value = 'test_jwt_token'
                    
                    # 发送请求
                    response = test_client.post(
                        '/api/auth/login',
                        json={
                            'username': 'test_user',
                            'password': 'password123'
                        }
                    )
                    
                    # 验证响应
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert 'access_token' in data
                    assert 'token_type' in data
                    assert data['access_token'] == 'test_jwt_token'
                    assert data['token_type'] == 'bearer'
    
    def test_login_invalid_credentials(self, test_client):
        """测试无效凭据登录"""
        with patch('apis.auth.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_session.exec.return_value.first.return_value = None  # 用户不存在
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.post(
                '/api/auth/login',
                json={
                    'username': 'nonexistent_user',
                    'password': 'password123'
                }
            )
            
            # 验证响应
            assert response.status_code == 401
            data = json.loads(response.data)
            assert 'error' in data
            assert 'credentials' in data['error']
    
    def test_login_wrong_password(self, test_client):
        """测试错误密码登录"""
        with patch('apis.auth.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = 'test_user'
            mock_user.email = 'test@example.com'
            mock_user.is_active = True
            mock_user.hashed_password = 'hashed_password'
            mock_session.exec.return_value.first.return_value = mock_user
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            with patch('apis.auth.verify_password') as mock_verify_password:
                mock_verify_password.return_value = False
                
                # 发送请求
                response = test_client.post(
                    '/api/auth/login',
                    json={
                        'username': 'test_user',
                        'password': 'wrong_password'
                    }
                )
                
                # 验证响应
                assert response.status_code == 401
                data = json.loads(response.data)
                assert 'error' in data
                assert 'credentials' in data['error']
    
    def test_login_inactive_user(self, test_client):
        """测试非活跃用户登录"""
        with patch('apis.auth.Session') as mock_session_class:
            # 设置mock
            mock_session = Mock()
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = 'test_user'
            mock_user.email = 'test@example.com'
            mock_user.is_active = False  # 非活跃用户
            mock_user.hashed_password = 'hashed_password'
            mock_session.exec.return_value.first.return_value = mock_user
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # 发送请求
            response = test_client.post(
                '/api/auth/login',
                json={
                    'username': 'test_user',
                    'password': 'password123'
                }
            )
            
            # 验证响应
            assert response.status_code == 401
            data = json.loads(response.data)
            assert 'error' in data
            assert 'inactive' in data['error']
    
    def test_login_missing_fields(self, test_client):
        """测试缺少必填字段登录"""
        # 发送请求
        response = test_client.post(
            '/api/auth/login',
            json={
                'username': 'test_user'
                # 缺少password
            }
        )
        
        # 验证响应
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_current_user_success(self, test_client, auth_headers):
        """测试获取当前用户成功"""
        with patch('apis.auth.verify_token') as mock_verify_token:
            # 设置mock
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = 'test_user'
            mock_user.email = 'test@example.com'
            mock_user.is_active = True
            mock_verify_token.return_value = mock_user
            
            # 发送请求
            response = test_client.get(
                '/api/auth/me',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['id'] == 1
            assert data['username'] == 'test_user'
            assert data['email'] == 'test@example.com'
    
    def test_get_current_user_invalid_token(self, test_client):
        """测试无效令牌获取当前用户"""
        with patch('apis.auth.verify_token') as mock_verify_token:
            # 设置mock
            mock_verify_token.return_value = None
            
            # 发送请求
            response = test_client.get(
                '/api/auth/me',
                headers={'Authorization': 'Bearer invalid_token'}
            )
            
            # 验证响应
            assert response.status_code == 401
            data = json.loads(response.data)
            assert 'error' in data
            assert 'token' in data['error']
    
    def test_get_current_user_no_token(self, test_client):
        """测试无令牌获取当前用户"""
        # 发送请求
        response = test_client.get('/api/auth/me')
        
        # 验证响应
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert 'token' in data['error']
    
    def test_logout_success(self, test_client, auth_headers):
        """测试用户登出成功"""
        with patch('apis.auth.verify_token') as mock_verify_token:
            # 设置mock
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = 'test_user'
            mock_verify_token.return_value = mock_user
            
            # 发送请求
            response = test_client.post(
                '/api/auth/logout',
                headers=auth_headers
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
    
    def test_logout_invalid_token(self, test_client):
        """测试无效令牌登出"""
        with patch('apis.auth.verify_token') as mock_verify_token:
            # 设置mock
            mock_verify_token.return_value = None
            
            # 发送请求
            response = test_client.post(
                '/api/auth/logout',
                headers={'Authorization': 'Bearer invalid_token'}
            )
            
            # 验证响应
            assert response.status_code == 401
            data = json.loads(response.data)
            assert 'error' in data
            assert 'token' in data['error']
    
    def test_refresh_token_success(self, test_client, auth_headers):
        """测试刷新令牌成功"""
        with patch('apis.auth.verify_token') as mock_verify_token:
            # 设置mock
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = 'test_user'
            mock_user.email = 'test@example.com'
            mock_user.is_active = True
            mock_verify_token.return_value = mock_user
            
            with patch('apis.auth.create_access_token') as mock_create_token:
                mock_create_token.return_value = 'new_jwt_token'
                
                # 发送请求
                response = test_client.post(
                    '/api/auth/refresh',
                    headers=auth_headers
                )
                
                # 验证响应
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'access_token' in data
                assert 'token_type' in data
                assert data['access_token'] == 'new_jwt_token'
                assert data['token_type'] == 'bearer'
    
    def test_refresh_token_invalid_token(self, test_client):
        """测试无效令牌刷新"""
        with patch('apis.auth.verify_token') as mock_verify_token:
            # 设置mock
            mock_verify_token.return_value = None
            
            # 发送请求
            response = test_client.post(
                '/api/auth/refresh',
                headers={'Authorization': 'Bearer invalid_token'}
            )
            
            # 验证响应
            assert response.status_code == 401
            data = json.loads(response.data)
            assert 'error' in data
            assert 'token' in data['error']
    
    def test_change_password_success(self, test_client, auth_headers):
        """测试修改密码成功"""
        with patch('apis.auth.verify_token') as mock_verify_token:
            # 设置mock
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = 'test_user'
            mock_user.email = 'test@example.com'
            mock_user.is_active = True
            mock_user.hashed_password = 'old_hashed_password'
            mock_verify_token.return_value = mock_user
            
            with patch('apis.auth.Session') as mock_session_class:
                mock_session = Mock()
                mock_session.exec.return_value.first.return_value = mock_user
                mock_session_class.return_value.__enter__.return_value = mock_session
                
                with patch('apis.auth.verify_password') as mock_verify_password:
                    mock_verify_password.return_value = True
                    
                    with patch('apis.auth.hash_password') as mock_hash_password:
                        mock_hash_password.return_value = 'new_hashed_password'
                        
                        # 发送请求
                        response = test_client.post(
                            '/api/auth/change-password',
                            headers=auth_headers,
                            json={
                                'old_password': 'old_password',
                                'new_password': 'new_password'
                            }
                        )
                        
                        # 验证响应
                        assert response.status_code == 200
                        data = json.loads(response.data)
                        assert 'message' in data
    
    def test_change_password_wrong_old_password(self, test_client, auth_headers):
        """测试错误旧密码修改密码"""
        with patch('apis.auth.verify_token') as mock_verify_token:
            # 设置mock
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = 'test_user'
            mock_user.email = 'test@example.com'
            mock_user.is_active = True
            mock_user.hashed_password = 'old_hashed_password'
            mock_verify_token.return_value = mock_user
            
            with patch('apis.auth.Session') as mock_session_class:
                mock_session = Mock()
                mock_session.exec.return_value.first.return_value = mock_user
                mock_session_class.return_value.__enter__.return_value = mock_session
                
                with patch('apis.auth.verify_password') as mock_verify_password:
                    mock_verify_password.return_value = False
                    
                    # 发送请求
                    response = test_client.post(
                        '/api/auth/change-password',
                        headers=auth_headers,
                        json={
                            'old_password': 'wrong_old_password',
                            'new_password': 'new_password'
                        }
                    )
                    
                    # 验证响应
                    assert response.status_code == 400
                    data = json.loads(response.data)
                    assert 'error' in data
                    assert 'old_password' in data['error']
    
    def test_change_password_missing_fields(self, test_client, auth_headers):
        """测试缺少必填字段修改密码"""
        with patch('apis.auth.verify_token') as mock_verify_token:
            # 设置mock
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = 'test_user'
            mock_verify_token.return_value = mock_user
            
            # 发送请求
            response = test_client.post(
                '/api/auth/change-password',
                headers=auth_headers,
                json={
                    'old_password': 'old_password'
                    # 缺少new_password
                }
            )
            
            # 验证响应
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
