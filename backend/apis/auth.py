from flask import Blueprint, request, jsonify
from sqlmodel import Session, create_engine, select
from models.user import User
from utils.jwt_utils import create_access_token, create_refresh_token, verify_token
from utils.logging_config import app_logger
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import datetime

# 加载环境变量
load_dotenv()

# 创建蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# 获取数据库引擎
def get_db_engine():
    db_path = os.getenv("DATABASE_PATH")
    if not db_path:
        raise ValueError("DATABASE_PATH environment variable is not set")
    return create_engine(f"sqlite:///{db_path}")

# 用户登录
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        app_logger.info("POST /api/auth/login - Request received")
        data = request.get_json()
        
        if not data or not all(key in data for key in ['email', 'password']):
            return jsonify({
                "code": 400,
                "message": "Missing required fields: email, password",
                "data": None
            }), 400
        
        email = data['email']
        password = data['password']
        
        engine = get_db_engine()
        with Session(engine) as session:
            # 查找用户
            user = session.exec(select(User).where(User.email == email)).first()
            
            if not user or not user.check_password(password):
                app_logger.warning(f"Login failed for email: {email}")
                return jsonify({
                    "code": 401,
                    "message": "Invalid email or password",
                    "data": None
                }), 401
            
            # 生成token
            access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
            refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})
            
            app_logger.info(f"User {email} logged in successfully")
            
            return jsonify({
                "code": 200,
                "message": "Login successful",
                "data": {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "role": user.role,
                        "createdAt": user.created_at.isoformat()
                    },
                    "token": access_token,
                    "refreshToken": refresh_token
                }
            })
    
    except Exception as e:
        app_logger.error(f"Error in login: {str(e)}")
        return jsonify({
            "code": 500,
            "message": "Internal server error",
            "data": None
        }), 500

# 用户注册
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        app_logger.info("POST /api/auth/register - Request received")
        data = request.get_json()
        
        if not data or not all(key in data for key in ['email', 'password']):
            return jsonify({
                "code": 400,
                "message": "Missing required fields: email, password",
                "data": None
            }), 400
        
        email = data['email']
        password = data['password']
        username = data.get('username', email.split('@')[0])  # 默认用户名为邮箱前缀
        
        engine = get_db_engine()
        with Session(engine) as session:
            # 检查邮箱是否已存在
            existing_user = session.exec(select(User).where(User.email == email)).first()
            if existing_user:
                return jsonify({
                    "code": 400,
                    "message": "Email already registered",
                    "data": None
                }), 400
            
            # 创建新用户
            new_user = User(
                email=email,
                username=username
            )
            new_user.set_password(password)
            
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            
            app_logger.info(f"New user registered: {email}")
            
            return jsonify({
                "code": 201,
                "message": "Registration successful",
                "data": {
                    "message": "Registration successful, please login"
                }
            }), 201
    
    except Exception as e:
        app_logger.error(f"Error in register: {str(e)}")
        return jsonify({
            "code": 500,
            "message": "Internal server error",
            "data": None
        }), 500

# 刷新token
@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    try:
        app_logger.info("POST /api/auth/refresh - Request received")
        data = request.get_json()
        
        if not data or 'refreshToken' not in data:
            return jsonify({
                "code": 400,
                "message": "Refresh token is required",
                "data": None
            }), 400
        
        refresh_token = data['refreshToken']
        
        # 验证刷新令牌
        payload = verify_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return jsonify({
                "code": 401,
                "message": "Invalid or expired refresh token",
                "data": None
            }), 401
        
        user_id = payload.get('sub')
        if not user_id:
            return jsonify({
                "code": 401,
                "message": "Invalid token payload",
                "data": None
            }), 401
        
        engine = get_db_engine()
        with Session(engine) as session:
            # 查找用户
            user = session.exec(select(User).where(User.id == int(user_id))).first()
            
            if not user:
                return jsonify({
                    "code": 401,
                    "message": "User not found",
                    "data": None
                }), 401
            
            # 生成新的访问令牌和刷新令牌
            new_access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
            new_refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})
            
            app_logger.info(f"Token refreshed for user: {user.email}")
            
            return jsonify({
                "code": 200,
                "message": "Token refreshed successfully",
                "data": {
                    "token": new_access_token,
                    "refreshToken": new_refresh_token
                }
            })
    
    except Exception as e:
        app_logger.error(f"Error in refresh token: {str(e)}")
        return jsonify({
            "code": 500,
            "message": "Internal server error",
            "data": None
        }), 500

# 用户登出
@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        app_logger.info("POST /api/auth/logout - Request received")
        
        # 在实际应用中，你可能想要将token加入黑名单
        # 这里我们只是返回一个成功的响应
        
        return jsonify({
            "code": 200,
            "message": "Logout successful",
            "data": {
                "message": "Logout successful"
            }
        })
    
    except Exception as e:
        app_logger.error(f"Error in logout: {str(e)}")
        return jsonify({
            "code": 500,
            "message": "Internal server error",
            "data": None
        }), 500

# 获取用户信息
@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    try:
        app_logger.info("GET /api/auth/profile - Request received")
        
        # 从请求头获取Authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                "code": 401,
                "message": "Authorization header is missing or invalid",
                "data": None
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # 验证token
        payload = verify_token(token)
        if not payload or payload.get('type') != 'access':
            return jsonify({
                "code": 401,
                "message": "Invalid or expired token",
                "data": None
            }), 401
        
        user_id = payload.get('sub')
        if not user_id:
            return jsonify({
                "code": 401,
                "message": "Invalid token payload",
                "data": None
            }), 401
        
        engine = get_db_engine()
        with Session(engine) as session:
            # 查找用户
            user = session.exec(select(User).where(User.id == int(user_id))).first()
            
            if not user:
                return jsonify({
                    "code": 401,
                    "message": "User not found",
                    "data": None
                }), 401
            
            app_logger.info(f"Profile retrieved for user: {user.email}")
            
            return jsonify({
                "code": 200,
                "message": "Profile retrieved successfully",
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "role": user.role,
                    "createdAt": user.created_at.isoformat()
                }
            })
    
    except Exception as e:
        app_logger.error(f"Error in get profile: {str(e)}")
        return jsonify({
            "code": 500,
            "message": "Internal server error",
            "data": None
        }), 500

# 更新用户信息
@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    try:
        app_logger.info("PUT /api/auth/profile - Request received")
        
        # 从请求头获取Authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                "code": 401,
                "message": "Authorization header is missing or invalid",
                "data": None
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # 验证token
        payload = verify_token(token)
        if not payload or payload.get('type') != 'access':
            return jsonify({
                "code": 401,
                "message": "Invalid or expired token",
                "data": None
            }), 401
        
        user_id = payload.get('sub')
        if not user_id:
            return jsonify({
                "code": 401,
                "message": "Invalid token payload",
                "data": None
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                "code": 400,
                "message": "No data provided",
                "data": None
            }), 400
        
        engine = get_db_engine()
        with Session(engine) as session:
            # 查找用户
            user = session.exec(select(User).where(User.id == int(user_id))).first()
            
            if not user:
                return jsonify({
                    "code": 401,
                    "message": "User not found",
                    "data": None
                }), 401
            
            # 更新用户信息
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                # 检查邮箱是否已被其他用户使用
                existing_user = session.exec(select(User).where(
                    User.email == data['email'], 
                    User.id != int(user_id)
                )).first()
                if existing_user:
                    return jsonify({
                        "code": 400,
                        "message": "Email already in use by another user",
                        "data": None
                    }), 400
                user.email = data['email']
            
            # 更新时间戳
            user.updated_at = datetime.datetime.utcnow()
            
            session.commit()
            session.refresh(user)
            
            app_logger.info(f"Profile updated for user: {user.email}")
            
            return jsonify({
                "code": 200,
                "message": "Profile updated successfully",
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "role": user.role,
                    "createdAt": user.created_at.isoformat()
                }
            })
    
    except Exception as e:
        app_logger.error(f"Error in update profile: {str(e)}")
        return jsonify({
            "code": 500,
            "message": "Internal server error",
            "data": None
        }), 500