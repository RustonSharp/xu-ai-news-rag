"""
Authentication service for user management.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlmodel import Session
from repositories.user_repository import UserRepository
from models.user import User
from utils.jwt_utils import create_access_token, verify_token
from utils.logging_config import app_logger
from config.settings import settings

# 使用bcrypt替代passlib
import bcrypt


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
    
    def authenticate_user(self, username: str, password: str, session: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password."""
        try:
            user = self.user_repo.authenticate_user(username, password)
            if not user:
                return None
            
            # Update last login
            self.user_repo.update_last_login(user.id)
            
            # Create access token
            token_data = {
                "sub": str(user.id),
                "username": user.username,
                "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
            }
            
            access_token = create_access_token(token_data)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_active": user.is_active
                }
            }
        except Exception as e:
            app_logger.error(f"Error authenticating user {username}: {str(e)}")
            return None
    
    def create_user(self, username: str, email: str, password: str, 
                   full_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user."""
        try:
            user = self.user_repo.create_user(username, email, password, full_name)
            
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat()
            }
        except Exception as e:
            app_logger.error(f"Error creating user {username}: {str(e)}")
            raise
    
    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from JWT token."""
        try:
            payload = verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            user = self.user_repo.get_by_id(User, int(user_id))
            if not user or not user.is_active:
                return None
            
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        except Exception as e:
            app_logger.error(f"Error getting user by token: {str(e)}")
            return None
    
    def refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token."""
        try:
            payload = verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            user = self.user_repo.get_by_id(User, int(user_id))
            if not user or not user.is_active:
                return None
            
            # Create new token
            token_data = {
                "sub": str(user.id),
                "username": user.username,
                "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
            }
            
            access_token = create_access_token(token_data)
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
        except Exception as e:
            app_logger.error(f"Error refreshing token: {str(e)}")
            return None
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        try:
            return self.user_repo.deactivate_user(user_id)
        except Exception as e:
            app_logger.error(f"Error deactivating user {user_id}: {str(e)}")
            return False
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            return self.user_repo.get_user_statistics()
        except Exception as e:
            app_logger.error(f"Error getting user statistics: {str(e)}")
            return {
                "total_users": 0,
                "active_users": 0,
                "new_users_last_30_days": 0
            }
    
    def search_users(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Search users by username, email, or full name."""
        try:
            users = self.user_repo.search_users(search_term, skip, limit)
            return [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
                for user in users
            ]
        except Exception as e:
            app_logger.error(f"Error searching users: {str(e)}")
            return []
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get active users."""
        try:
            users = self.user_repo.get_active_users(skip, limit)
            return [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
                for user in users
            ]
        except Exception as e:
            app_logger.error(f"Error getting active users: {str(e)}")
            return []
    
    # Additional methods for backward compatibility
    def create_access_token(self, user) -> str:
        """Create access token for user."""
        try:
            token_data = {
                "sub": str(user.id),
                "username": user.username,
                "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
            }
            return create_access_token(token_data)
        except Exception as e:
            app_logger.error(f"Error creating access token: {str(e)}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token."""
        try:
            return verify_token(token)
        except Exception as e:
            app_logger.error(f"Error verifying token: {str(e)}")
            return None
    
    def register_user(self, username: str, email: str, password: str, 
                     full_name: Optional[str] = None) -> Dict[str, Any]:
        """Register a new user (alias for create_user)."""
        return self.create_user(username, email, password, full_name)
    
    def hash_password(self, password: str) -> str:
        """Hash password."""
        try:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        except Exception as e:
            app_logger.error(f"Error hashing password: {str(e)}")
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password."""
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            app_logger.error(f"Error verifying password: {str(e)}")
            return False
