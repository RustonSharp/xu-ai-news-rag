# 测试文档

本目录包含新闻知识库系统的完整测试套件，包括单元测试、集成测试和API测试。

## 目录结构

```
tests/
├── conftest.py              # 测试配置和fixtures
├── run_tests.py             # 测试运行脚本
├── fixtures/                # 测试数据
│   └── test_data.json       # 测试数据文件
├── unit/                    # 单元测试
│   ├── test_assistant.py    # 助手模块测试
│   └── test_tools.py        # 工具模块测试
├── integration/             # 集成测试
│   └── test_knowledge_base.py # 知识库集成测试
└── api/                     # API测试
    ├── test_assistant_api.py # 助手API测试
    └── test_other_apis.py   # 其他API测试
```

## 测试类型

### 1. 单元测试 (Unit Tests)
- **位置**: `tests/unit/`
- **目的**: 测试单个函数或类的功能
- **特点**: 快速、独立、可重复
- **覆盖**: 核心业务逻辑

#### 测试模块
- `test_assistant.py`: 测试助手创建和查询功能
- `test_tools.py`: 测试知识库和在线搜索工具

### 2. 集成测试 (Integration Tests)
- **位置**: `tests/integration/`
- **目的**: 测试多个模块协同工作
- **特点**: 测试真实的数据流和交互
- **覆盖**: 端到端功能

#### 测试模块
- `test_knowledge_base.py`: 测试知识库完整工作流程

### 3. API测试 (API Tests)
- **位置**: `tests/api/`
- **目的**: 测试HTTP接口
- **特点**: 测试完整的请求-响应流程
- **覆盖**: 所有REST API端点

#### 测试模块
- `test_assistant_api.py`: 测试助手API接口
- `test_other_apis.py`: 测试文档、RSS、调度器等API

## 运行测试

### 安装测试依赖

```bash
# 安装所有测试依赖
python tests/run_tests.py --install-deps

# 或手动安装
pip install pytest pytest-cov pytest-xdist pytest-mock
```

### 运行所有测试

```bash
# 运行所有测试
python tests/run_tests.py

# 或使用pytest
pytest
```

### 运行特定类型的测试

```bash
# 只运行单元测试
python tests/run_tests.py --type unit

# 只运行集成测试
python tests/run_tests.py --type integration

# 只运行API测试
python tests/run_tests.py --type api
```

### 运行特定测试文件

```bash
# 运行特定文件
python tests/run_tests.py --file tests/unit/test_assistant.py

# 运行特定函数
python tests/run_tests.py --file tests/unit/test_assistant.py --function test_create_assistant_success
```

### 高级选项

```bash
# 详细输出
python tests/run_tests.py --verbose

# 生成覆盖率报告
python tests/run_tests.py --coverage

# 并行运行测试
python tests/run_tests.py --parallel
```

## 测试配置

### 环境变量

测试使用以下环境变量：

```bash
export TESTING=true
export EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
export RERANK_MODEL_NAME=cross-encoder/ms-marco-MiniLM-L-6-v2
export TAVILY_API_KEY=test_key
```

### 测试数据

测试数据存储在 `tests/fixtures/test_data.json` 中，包括：
- 示例文档
- 示例查询
- RSS源配置
- 分析数据
- 测试配置

## 测试标记

使用pytest标记来分类测试：

```python
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration
def test_integration_workflow():
    pass

@pytest.mark.api
def test_api_endpoint():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

### 运行特定标记的测试

```bash
# 只运行单元测试
pytest -m unit

# 跳过慢速测试
pytest -m "not slow"

# 运行需要网络的测试
pytest -m requires_network
```

## Mock和Fixtures

### 常用Fixtures

- `mock_llm`: 模拟LLM
- `mock_knowledge_base_tool`: 模拟知识库工具
- `mock_online_search_tool`: 模拟在线搜索工具
- `test_app`: 测试Flask应用
- `test_client`: 测试HTTP客户端
- `auth_headers`: 认证头

### 使用示例

```python
def test_with_mocks(mock_llm, mock_knowledge_base_tool):
    # 设置mock返回值
    mock_llm.invoke.return_value = "测试回答"
    mock_knowledge_base_tool.invoke.return_value = [{"content": "测试内容"}]
    
    # 执行测试
    result = some_function()
    
    # 验证结果
    assert result == "预期结果"
```

## 覆盖率报告

### 生成覆盖率报告

```bash
# 生成HTML报告
python tests/run_tests.py --coverage

# 查看覆盖率报告
open htmlcov/index.html
```

### 覆盖率目标

- 单元测试: > 90%
- 集成测试: > 80%
- API测试: > 85%
- 总体覆盖率: > 85%

## 持续集成

### GitHub Actions

测试在每次推送和PR时自动运行：

- Python 3.9, 3.10, 3.11
- 单元测试 + 覆盖率
- 集成测试
- API测试
- 代码质量检查

### 本地CI

```bash
# 运行完整的CI流程
python tests/run_tests.py --type all --coverage --verbose
```

## 故障排除

### 常见问题

1. **导入错误**
   ```bash
   # 确保在项目根目录运行
   cd /path/to/project/backend
   python tests/run_tests.py
   ```

2. **依赖问题**
   ```bash
   # 重新安装依赖
   pip install -r requirements.txt
   python tests/run_tests.py --install-deps
   ```

3. **网络问题**
   ```bash
   # 跳过需要网络的测试
   pytest -m "not requires_network"
   ```

4. **模型加载问题**
   ```bash
   # 使用测试模式
   export TESTING=true
   python tests/run_tests.py
   ```

### 调试测试

```bash
# 详细输出
python tests/run_tests.py --verbose

# 在第一个失败时停止
pytest -x

# 显示print输出
pytest -s

# 调试特定测试
pytest tests/unit/test_assistant.py::TestCreateAssistant::test_create_assistant_success -v -s
```

## 最佳实践

1. **测试命名**: 使用描述性的测试名称
2. **测试独立性**: 每个测试应该独立运行
3. **Mock使用**: 适当使用mock来隔离测试
4. **数据清理**: 测试后清理临时数据
5. **错误测试**: 测试正常和异常情况
6. **文档更新**: 及时更新测试文档

## 贡献指南

1. 为新功能添加测试
2. 确保测试通过
3. 保持测试覆盖率
4. 更新测试文档
5. 遵循测试命名约定

