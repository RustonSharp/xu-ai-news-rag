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
    role: str = Field(default="user")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def set_password(self, password: str):
        """设置密码哈希"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))