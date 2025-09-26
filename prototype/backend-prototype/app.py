from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# 启用CORS
CORS(app)

# 初始化JWT
jwt = JWTManager(app)

# 数据库初始化
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建文档表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            source TEXT,
            url TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建任务表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            payload TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# 认证相关API
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': '邮箱和密码不能为空'}), 400
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, password_hash, role FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            access_token = create_access_token(identity=user[0])
            return jsonify({
                'token': access_token,
                'user': {
                    'id': user[0],
                    'email': user[1],
                    'role': user[3]
                },
                'expires_in': 86400
            })
        else:
            return jsonify({'message': '邮箱或密码错误'}), 401
            
    except Exception as e:
        return jsonify({'message': '登录失败，请稍后重试'}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': '邮箱和密码不能为空'}), 400
        
        if len(password) < 6:
            return jsonify({'message': '密码长度至少6位'}), 400
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # 检查用户是否已存在
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'message': '该邮箱已被注册'}), 400
        
        # 创建新用户
        password_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, password_hash))
        conn.commit()
        conn.close()
        
        return jsonify({'message': '注册成功'}), 201
        
    except Exception as e:
        return jsonify({'message': '注册失败，请稍后重试'}), 500

# 文档管理API
@app.route('/api/docs', methods=['GET'])
@jwt_required()
def get_documents():
    try:
        # 获取查询参数
        doc_type = request.args.get('type')
        source = request.args.get('source')
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if doc_type:
            where_conditions.append('type = ?')
            params.append(doc_type)
        
        if source:
            where_conditions.append('source = ?')
            params.append(source)
        
        where_clause = ' WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
        
        # 获取总数
        cursor.execute(f'SELECT COUNT(*) FROM documents{where_clause}', params)
        total = cursor.fetchone()[0]
        
        # 获取分页数据
        offset = (page - 1) * size
        cursor.execute(f'''
            SELECT id, title, type, source, url, tags, created_at, updated_at 
            FROM documents{where_clause} 
            ORDER BY updated_at DESC 
            LIMIT ? OFFSET ?
        ''', params + [size, offset])
        
        documents = []
        for row in cursor.fetchall():
            documents.append({
                'id': str(row[0]),
                'title': row[1],
                'type': row[2],
                'source': row[3],
                'url': row[4],
                'tags': row[5].split(',') if row[5] else [],
                'created_at': row[6],
                'updated_at': row[7]
            })
        
        conn.close()
        
        return jsonify({
            'total': total,
            'page': page,
            'size': size,
            'items': documents
        })
        
    except Exception as e:
        return jsonify({'message': '获取文档列表失败'}), 500

# 健康检查
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 创建默认用户（仅用于演示）
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', ('demo@example.com',))
        if not cursor.fetchone():
            password_hash = generate_password_hash('123456')
            cursor.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', ('demo@example.com', password_hash))
            conn.commit()
        conn.close()
    except:
        pass
    
    print('Flask后端服务启动中...')
    print('API文档: http://localhost:5001/api/health')
    print('演示账号: demo@example.com / 123456')
    app.run(debug=True, host='0.0.0.0', port=5001)