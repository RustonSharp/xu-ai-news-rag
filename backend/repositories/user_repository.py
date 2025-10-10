"""
User repository for database operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select, func, and_, or_, desc
from models.user import User
from repositories.base_repository import BaseRepository
from utils.logging_config import app_logger


class UserRepository(BaseRepository[User]):
    """Repository for user operations."""
    
    def __init__(self, session: Session):
        super().__init__(session, User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            statement = select(User).where(User.username == username)
            return self.session.exec(statement).first()
        except Exception as e:
            app_logger.error(f"Error getting user by username {username}: {str(e)}")
            raise
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            statement = select(User).where(User.email == email)
            return self.session.exec(statement).first()
        except Exception as e:
            app_logger.error(f"Error getting user by email {email}: {str(e)}")
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        try:
            user = self.get_by_username(username)
            if user and user.check_password(password):
                return user
            return None
        except Exception as e:
            app_logger.error(f"Error authenticating user {username}: {str(e)}")
            raise
    
    def create_user(self, username: str, email: str, password: str, 
                   full_name: Optional[str] = None) -> User:
        """Create a new user."""
        try:
            # Check if username or email already exists
            if self.get_by_username(username):
                raise ValueError(f"Username {username} already exists")
            
            if self.get_by_email(email):
                raise ValueError(f"Email {email} already exists")
            
            user = User(
                username=username,
                email=email,
                full_name=full_name or username
            )
            user.set_password(password)
            
            return self.create(user)
        except Exception as e:
            app_logger.error(f"Error creating user {username}: {str(e)}")
            raise
    
    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login time."""
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
            
            user.last_login = datetime.now()
            self.session.commit()
            self.session.refresh(user)
            app_logger.info(f"Updated last login for user ID: {user_id}")
            return True
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"Error updating last login for user ID {user_id}: {str(e)}")
            raise
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users (those who have logged in recently)."""
        try:
            from datetime import timedelta
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
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting active users: {str(e)}")
            raise
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            total_users = self.count()
            
            # Get active users count
            statement = select(func.count(User.id)).where(User.is_active == True)
            active_users = self.session.exec(statement).one()
            
            # Get users created in last 30 days
            from datetime import timedelta
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
            raise
    
    def search_users(self, search_term: str, skip: int = 0, limit: int = 100) -> List[User]:
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
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error searching users: {str(e)}")
            raise
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
            
            user.is_active = False
            self.session.commit()
            self.session.refresh(user)
            app_logger.info(f"Deactivated user ID: {user_id}")
            return True
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"Error deactivating user ID {user_id}: {str(e)}")
            raise
