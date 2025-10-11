"""
认证服务单元测试
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth_service import AuthService
from models.user import User


class TestAuthService:
    """认证服务测试"""
    
    def test_authenticate_user_success(self, mock_database_session, mock_user):
        """测试用户认证成功"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_user
        
        # 创建服务实例
        auth_service = AuthService(mock_database_session)
        
        # 执行测试
        result = auth_service.authenticate_user("test_user", "password123", mock_database_session)
        
        # 验证
        assert result is not None
        assert result["user"]["username"] == "test_user"
    
    def test_authenticate_user_not_found(self, mock_database_session):
        """测试用户不存在"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = None
        
        # 创建服务实例
        auth_service = AuthService(mock_database_session)
        
        # 执行测试
        result = auth_service.authenticate_user("nonexistent_user", "password123", mock_database_session)
        
        # 验证
        assert result is None
    
    def test_authenticate_user_wrong_password(self, mock_database_session, mock_user):
        """测试密码错误"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_user
        
        # 创建服务实例
        auth_service = AuthService(mock_database_session)
        
        # 执行测试
        result = auth_service.authenticate_user("test_user", "wrong_password", mock_database_session)
        
        # 验证
        assert result is None
    
    def test_create_access_token(self, mock_database_session, mock_user):
        """测试创建访问令牌"""
        # 创建服务实例
        auth_service = AuthService(mock_database_session)
        
        # 执行测试
        token = auth_service.create_access_token(mock_user)
        
        # 验证
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token_success(self, mock_database_session, mock_jwt_token, mock_user):
        """测试令牌验证成功"""
        # 创建服务实例
        auth_service = AuthService(mock_database_session)
        
        # 执行测试
        with patch.object(auth_service.user_repo, 'get_by_id') as mock_get_user:
            mock_get_user.return_value = mock_user
            result = auth_service.verify_token(mock_jwt_token)
            
            # 验证
            assert result is not None
    
    def test_verify_token_invalid(self, mock_database_session):
        """测试无效令牌"""
        # 创建服务实例
        auth_service = AuthService(mock_database_session)
        
        # 执行测试
        result = auth_service.verify_token("invalid_token")
        
        # 验证
        assert result is None
    
    def test_verify_token_expired(self, mock_database_session):
        """测试过期令牌"""
        # 创建服务实例
        auth_service = AuthService(mock_database_session)
        
        # 使用过期的令牌
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2MDAwMDAwMDB9.expired_signature"
        
        # 执行测试
        result = auth_service.verify_token(expired_token)
        
        # 验证
        assert result is None


class TestUserRegistration:
    """用户注册测试"""
    
    def test_register_user_success(self, mock_database_session):
        """测试用户注册成功"""
        # 创建服务实例
        auth_service = AuthService(mock_database_session)
        
        # 执行测试
        with patch('services.auth_service.User') as mock_user_class:
            mock_user_instance = Mock()
            mock_user_class.return_value = mock_user_instance
            
            result = auth_service.register_user(
                "new_user", 
                "new@example.com", 
                "password123", 
                mock_database_session
            )
            
            # 验证
            assert result is not None
            mock_database_session.add.assert_called_once()
            mock_database_session.commit.assert_called_once()
    
    def test_register_user_duplicate_username(self, mock_database_session, mock_user):
        """测试重复用户名注册"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_user
        
        # 创建服务实例
        auth_service = AuthService(mock_database_session)
        
        # 执行测试
        result = auth_service.register_user(
            "test_user", 
            "new@example.com", 
            "password123", 
            mock_database_session
        )
        
        # 验证
        assert result is None
    
    def test_register_user_duplicate_email(self, mock_database_session, mock_user):
        """测试重复邮箱注册"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_user
        
        # 创建服务实例
        auth_service = AuthService(mock_database_session)
        
        # 执行测试
        result = auth_service.register_user(
            "new_user", 
            "test@example.com", 
            "password123", 
            mock_database_session
        )
        
        # 验证
        assert result is None


class TestPasswordHashing:
    """密码哈希测试"""
    
    def test_hash_password(self, mock_database_session):
        """测试密码哈希"""
        # 创建服务实例
        auth_service = AuthService(mock_database_session)
        
        # 执行测试
        hashed = auth_service.hash_password("test_password")
        
        # 验证
        assert hashed is not None
        assert hashed != "test_password"
        assert len(hashed) > 0
    
    def test_verify_password_correct(self, mock_database_session):
        """测试密码验证正确"""
        # 创建服务实例
        auth_service = AuthService(mock_database_session)
        
        # 执行测试
        hashed = auth_service.hash_password("test_password")
        result = auth_service.verify_password("test_password", hashed)
        
        # 验证
        assert result is True
    
    def test_verify_password_incorrect(self, mock_database_session):
        """测试密码验证错误"""
        # 创建服务实例
        auth_service = AuthService(mock_database_session)
        
        # 执行测试
        hashed = auth_service.hash_password("test_password")
        result = auth_service.verify_password("wrong_password", hashed)
        
        # 验证
        assert result is False
