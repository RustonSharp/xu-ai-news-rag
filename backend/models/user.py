from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import bcrypt

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str
    password_hash: str
    full_name: Optional[str] = None
    role: str = Field(default="user")
    is_active: bool = Field(default=True)
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def set_password(self, password: str):
        """设置密码哈希"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"
    
    def __eq__(self, other) -> bool:
        """相等性比较"""
        if not isinstance(other, User):
            return False
        return self.id == other.id and self.email == other.email