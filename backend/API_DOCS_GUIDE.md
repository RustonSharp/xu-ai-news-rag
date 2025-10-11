# API文档更新指南

## 📖 如何查看API文档

### 方法1：使用文档生成器（推荐）

```bash
# 1. 安装依赖
pip install -r requirements_docs.txt

# 2. 启动文档服务器
python start_docs.py
# 或者
python api_docs_generator.py

# 3. 访问文档
# 浏览器打开: http://localhost:5002/api/docs/
```

### 方法2：查看现有README

项目README.md中已包含基本API端点列表：
- 认证API：`/api/auth/*`
- 数据源API：`/api/sources/*`
- 文档API：`/api/documents/*`
- 助手API：`/api/assistant/*`
- 调度器API：`/api/scheduler/*`
- 分析API：`/api/analytics/*`

## 🔧 如何更新API文档

### 1. 更新Flask-RESTX文档

编辑 `api_docs_generator.py` 文件：

```python
# 添加新的API端点
@source_ns.route('/new-endpoint')
class NewEndpoint(Resource):
    @source_ns.expect(new_model)
    @source_ns.marshal_with(response_model)
    def post(self):
        """新API端点描述"""
        pass
```

### 2. 更新数据模型

```python
# 定义新的数据模型
new_model = api.model('NewModel', {
    'field1': fields.String(required=True, description='字段1描述'),
    'field2': fields.Integer(description='字段2描述'),
    'field3': fields.Boolean(description='字段3描述')
})
```

### 3. 更新README文档

编辑 `README.md` 文件，在API Endpoints部分添加新端点：

```markdown
### 新功能API (`/api/new-feature`)
- `GET /` - 获取新功能列表
- `POST /` - 创建新功能
- `PUT /<id>` - 更新新功能
- `DELETE /<id>` - 删除新功能
```

## 📝 文档最佳实践

### 1. API描述规范

```python
@api.doc('endpoint_name', description='简洁的API描述')
def method_name(self):
    """
    详细的API说明
    
    **功能描述：**
    这个API用于...
    
    **参数说明：**
    - param1: 参数1的详细说明
    - param2: 参数2的详细说明
    
    **示例请求：**
    ```json
    {
        "key": "value"
    }
    ```
    
    **示例响应：**
    ```json
    {
        "code": 200,
        "message": "success",
        "data": {}
    }
    ```
    
    **错误码：**
    - 400: 请求参数错误
    - 401: 未授权
    - 500: 服务器错误
    """
```

### 2. 数据模型规范

```python
# 请求模型
request_model = api.model('RequestModel', {
    'required_field': fields.String(required=True, description='必填字段'),
    'optional_field': fields.String(description='可选字段'),
    'enum_field': fields.String(enum=['value1', 'value2'], description='枚举字段'),
    'nested_field': fields.Nested(api.model('NestedModel', {
        'nested_key': fields.String(description='嵌套字段')
    }))
})

# 响应模型
response_model = api.model('ResponseModel', {
    'code': fields.Integer(description='状态码'),
    'message': fields.String(description='消息'),
    'data': fields.Raw(description='数据')
})
```

### 3. 认证配置

```python
# 在API配置中添加认证
api = Api(
    app,
    authorizations={
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT token格式: Bearer <token>'
        }
    }
)

# 在需要认证的端点添加装饰器
@api.doc(security='Bearer Auth')
def protected_endpoint(self):
    pass
```

## 🚀 自动化文档更新

### 1. 创建文档更新脚本

```python
# update_docs.py
import os
import subprocess

def update_docs():
    """更新API文档"""
    print("🔄 更新API文档...")
    
    # 重新生成文档
    subprocess.run(["python", "api_docs_generator.py"])
    
    # 更新README
    subprocess.run(["python", "update_readme.py"])
    
    print("✅ 文档更新完成")

if __name__ == "__main__":
    update_docs()
```

### 2. 集成到CI/CD

```yaml
# .github/workflows/docs.yml
name: Update API Docs
on:
  push:
    paths:
      - 'apis/**'
      - 'schemas/**'
      - 'models/**'

jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Update API Documentation
        run: |
          pip install -r requirements_docs.txt
          python api_docs_generator.py
```

## 📊 文档质量检查

### 1. 检查清单

- [ ] 所有API端点都有文档
- [ ] 请求/响应模型完整
- [ ] 示例数据准确
- [ ] 错误码说明完整
- [ ] 认证方式明确
- [ ] 参数验证规则清晰

### 2. 测试文档

```bash
# 测试API文档是否可访问
curl http://localhost:5002/api/swagger.json

# 测试Swagger UI
curl http://localhost:5002/api/docs/
```

## 🔍 常见问题

### Q: 文档页面无法访问？
A: 检查端口5002是否被占用，或修改端口号

### Q: 模型定义不显示？
A: 确保使用了正确的装饰器：`@api.expect()` 和 `@api.marshal_with()`

### Q: 认证测试失败？
A: 确保在Swagger UI中正确设置了Authorization header

### Q: 如何添加更多示例？
A: 在API方法中添加更详细的docstring，包含更多示例

## 📚 相关资源

- [Flask-RESTX文档](https://flask-restx.readthedocs.io/)
- [OpenAPI规范](https://swagger.io/specification/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [ReDoc](https://redoc.ly/)

## 🎯 下一步计划

1. **集成真实API**：将文档生成器与实际API端点连接
2. **添加更多示例**：为每个API提供详细的请求/响应示例
3. **自动化测试**：基于API文档生成自动化测试
4. **多语言支持**：添加英文API文档
5. **版本管理**：支持API版本控制和文档版本管理
