"""
Authentication service for user management.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlmodel import Session, select, func, and_, or_, desc
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
    
    def authenticate_user(self, username: str, password: str, session: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password."""
        try:
            current_session = session or self.session
            user = self._get_by_username(username, current_session)
            if not user or not user.check_password(password):
                return None
            
            # Update last login
            self._update_last_login(user.id, current_session)
            
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
            # Check if username or email already exists
            if self._get_by_username(username):
                raise ValueError(f"Username {username} already exists")
            
            if self._get_by_email(email):
                raise ValueError(f"Email {email} already exists")
            
            user = User(
                username=username,
                email=email,
                full_name=full_name or username
            )
            user.set_password(password)
            
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat()
            }
        except Exception as e:
            self.session.rollback()
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
            
            user = self._get_by_id(int(user_id))
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
            
            user = self._get_by_id(int(user_id))
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
            user = self._get_by_id(user_id)
            if not user:
                return False
            
            user.is_active = False
            self.session.commit()
            self.session.refresh(user)
            app_logger.info(f"Deactivated user ID: {user_id}")
            return True
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"Error deactivating user {user_id}: {str(e)}")
            return False
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            total_users = self._count()
            
            # Get active users count
            statement = select(func.count(User.id)).where(User.is_active == True)
            active_users = self.session.exec(statement).one()
            
            # Get users created in last 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            statement = select(func.count(User.id)).where(User.created_at >= cutoff_date)
            new_users = self.session.exec(statement).one()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "new_users_last_30_days": new_users
            }
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
            statement = (
                select(User)
                .where(
                    or_(
                        User.username.contains(search_term),
                        User.email.contains(search_term),
                        User.full_name.contains(search_term)
                    )
                )
                .order_by(User.username.asc())
                .offset(skip)
                .limit(limit)
            )
            users = list(self.session.exec(statement))
            
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
            cutoff_date = datetime.now() - timedelta(days=30)
            statement = (
                select(User)
                .where(
                    and_(
                        User.is_active == True,
                        User.last_login >= cutoff_date
                    )
                )
                .order_by(desc(User.last_login))
                .offset(skip)
                .limit(limit)
            )
            users = list(self.session.exec(statement))
            
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
    
    # Private helper methods (formerly in UserRepository)
    def _get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            return self.session.get(User, user_id)
        except Exception as e:
            app_logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            raise
    
    def _get_by_username(self, username: str, session: Optional[Session] = None) -> Optional[User]:
        """Get user by username."""
        try:
            current_session = session or self.session
            statement = select(User).where(User.username == username)
            return current_session.exec(statement).first()
        except Exception as e:
            app_logger.error(f"Error getting user by username {username}: {str(e)}")
            raise
    
    def _get_by_email(self, email: str, session: Optional[Session] = None) -> Optional[User]:
        """Get user by email."""
        try:
            current_session = session or self.session
            statement = select(User).where(User.email == email)
            return current_session.exec(statement).first()
        except Exception as e:
            app_logger.error(f"Error getting user by email {email}: {str(e)}")
            raise
    
    def _update_last_login(self, user_id: int, session: Optional[Session] = None) -> bool:
        """Update user's last login time."""
        try:
            current_session = session or self.session
            user = current_session.get(User, user_id)
            if not user:
                return False
            
            user.last_login = datetime.now()
            current_session.commit()
            current_session.refresh(user)
            app_logger.info(f"Updated last login for user ID: {user_id}")
            return True
        except Exception as e:
            current_session.rollback()
            app_logger.error(f"Error updating last login for user ID {user_id}: {str(e)}")
            raise
    
    def _count(self) -> int:
        """Count total users."""
        try:
            statement = select(func.count()).select_from(User)
            return self.session.exec(statement).one()
        except Exception as e:
            app_logger.error(f"Error counting users: {str(e)}")
            raise
