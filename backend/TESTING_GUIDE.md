# 新闻知识库系统 - 测试指南

## 概述

本测试指南介绍了如何为新闻知识库系统运行和管理测试。系统使用pytest作为测试框架，支持单元测试、集成测试和API测试。

## 测试框架

### 依赖包
- `pytest`: 主要测试框架
- `pytest-cov`: 代码覆盖率分析
- `pytest-xdist`: 并行测试执行
- `pytest-mock`: Mock和Stub支持
- `pytest-html`: HTML测试报告
- `pytest-json-report`: JSON测试报告

### 安装测试依赖
```bash
pip install pytest pytest-cov pytest-xdist pytest-mock pytest-html pytest-json-report
```

## 测试结构

```
backend/
├── tests/
│   ├── conftest.py              # pytest配置和fixtures
│   ├── simple_test.py           # 基础功能测试
│   ├── example_test.py          # 新闻知识库系统示例测试
│   ├── unit/                    # 单元测试
│   │   ├── test_assistant.py   # 助手模块测试
│   │   └── test_tools.py       # 工具模块测试
│   ├── integration/             # 集成测试
│   │   └── test_knowledge_base.py
│   ├── api/                     # API测试
│   │   ├── test_assistant_api.py
│   │   └── test_other_apis.py
│   └── fixtures/                # 测试数据
│       └── test_data.json
├── pytest.ini                  # pytest配置文件
├── run_tests.py                # 测试运行脚本
└── run_test_examples.py        # 测试示例脚本
```

## 运行测试

### 1. 基础测试运行

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/simple_test.py -v
python -m pytest tests/example_test.py -v

# 运行特定测试类
python -m pytest tests/example_test.py::TestNewsRAGSystem -v

# 运行特定测试方法
python -m pytest tests/example_test.py::TestNewsRAGSystem::test_query_processing_workflow -v
```

### 2. 覆盖率测试

```bash
# 生成覆盖率报告
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# 查看HTML覆盖率报告
open htmlcov/index.html
```

### 3. 并行测试

```bash
# 并行运行测试
python -m pytest tests/ -n auto

# 指定并行进程数
python -m pytest tests/ -n 4
```

### 4. 测试报告

```bash
# 生成HTML报告
python -m pytest tests/ --html=test_report.html --self-contained-html

# 生成JSON报告
python -m pytest tests/ --json-report --json-report-file=test_report.json
```

## 测试类型

### 1. 单元测试 (Unit Tests)

测试单个函数或方法的功能：

```python
def test_keyword_extraction():
    """测试关键词提取功能"""
    query = "人工智能在医疗领域的应用"
    keywords = extract_keywords(query)
    assert "人工智能" in keywords
    assert "医疗" in keywords
```

### 2. 集成测试 (Integration Tests)

测试多个组件之间的交互：

```python
def test_knowledge_base_integration():
    """测试知识库集成功能"""
    # 测试知识库搜索
    results = knowledge_base.search("AI医疗")
    assert len(results) > 0
    
    # 测试结果处理
    processed = process_results(results)
    assert processed["answer"] is not None
```

### 3. API测试 (API Tests)

测试API端点的功能：

```python
def test_assistant_api():
    """测试助手API端点"""
    response = client.post("/api/assistant/query", 
                          json={"query": "测试查询"})
    assert response.status_code == 200
    assert "answer" in response.json()
```

## 测试示例

### 新闻RAG系统测试示例

```python
class TestNewsRAGSystem:
    """新闻知识库系统测试"""
    
    def test_query_processing_workflow(self):
        """测试查询处理工作流程"""
        query = "人工智能在医疗领域的应用"
        
        # 1. 关键词提取
        keywords = self.extract_keywords(query)
        assert "人工智能" in keywords
        
        # 2. 知识库搜索
        kb_results = self.mock_knowledge_base_search(keywords)
        assert isinstance(kb_results, list)
        
        # 3. 相关性判断
        is_relevant = self.check_relevance(query, kb_results)
        assert isinstance(is_relevant, bool)
    
    def test_fallback_mechanism(self):
        """测试fallback机制"""
        query = "最新股市行情"
        kb_results = []  # 空结果
        
        # 应该触发在线搜索
        should_fallback = len(kb_results) == 0
        assert should_fallback is True
```

## Mock和Stub

### 使用Mock测试外部依赖

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """使用Mock测试外部依赖"""
    with patch('tools.create_knowledge_base_tool') as mock_tool:
        mock_tool.return_value = Mock()
        result = create_assistant()
        assert result is not None
        mock_tool.assert_called_once()
```

### 使用Fixture提供测试数据

```python
@pytest.fixture
def sample_document():
    """提供示例文档数据"""
    return {
        "title": "AI医疗应用",
        "content": "人工智能在医疗领域的应用...",
        "metadata": {"source": "medical_news"}
    }

def test_document_processing(sample_document):
    """测试文档处理"""
    processed = process_document(sample_document)
    assert processed["title"] == "AI医疗应用"
```

## 测试配置

### pytest.ini配置

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes
markers =
    unit: 单元测试
    integration: 集成测试
    api: API测试
    slow: 慢速测试
```

## 持续集成

### GitHub Actions配置

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m pytest tests/ --cov=. --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 测试最佳实践

### 1. 测试命名
- 测试函数名应该描述测试的内容
- 使用`test_`前缀
- 使用描述性的名称，如`test_user_login_with_valid_credentials`

### 2. 测试结构
- 使用AAA模式：Arrange, Act, Assert
- 每个测试只测试一个功能
- 保持测试简单和独立

### 3. 测试数据
- 使用fixture提供测试数据
- 避免硬编码的测试数据
- 使用工厂模式创建测试对象

### 4. 错误处理
- 测试正常情况和异常情况
- 使用`pytest.raises`测试异常
- 验证错误消息和状态码

### 5. 性能测试
- 测试响应时间
- 测试内存使用
- 使用`pytest-benchmark`进行性能测试

## 故障排除

### 常见问题

1. **导入错误**
   ```bash
   # 确保在正确的目录运行测试
   cd /path/to/backend
   python -m pytest tests/
   ```

2. **依赖问题**
   ```bash
   # 安装所有依赖
   pip install -r requirements.txt
   ```

3. **环境问题**
   ```bash
   # 激活conda环境
   conda activate news-rag11
   python -m pytest tests/
   ```

### 调试测试

```bash
# 运行特定测试并显示详细输出
python -m pytest tests/example_test.py::TestNewsRAGSystem::test_query_processing_workflow -v -s

# 在第一个失败时停止
python -m pytest tests/ -x

# 显示本地变量
python -m pytest tests/ --tb=long
```

## 测试覆盖率

当前测试覆盖率：**21%**

### 覆盖率目标
- 单元测试：80%+
- 集成测试：70%+
- API测试：90%+

### 提高覆盖率
1. 添加更多单元测试
2. 测试边界条件
3. 测试错误处理
4. 测试所有代码路径

## 总结

本测试框架为新闻知识库系统提供了完整的测试支持，包括：

- ✅ 基础测试框架设置
- ✅ 单元测试、集成测试、API测试
- ✅ 代码覆盖率分析
- ✅ 并行测试执行
- ✅ 测试报告生成
- ✅ Mock和Stub支持
- ✅ 持续集成配置

通过遵循本指南，您可以有效地测试和维护新闻知识库系统的质量。
