"""
简单测试文件，用于验证测试框架是否工作
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_basic_functionality():
    """基本功能测试"""
    assert 1 + 1 == 2
    assert "hello" == "hello"
    assert True is True


def test_string_operations():
    """字符串操作测试"""
    text = "Hello World"
    assert len(text) == 11
    assert text.upper() == "HELLO WORLD"
    assert text.lower() == "hello world"


def test_list_operations():
    """列表操作测试"""
    numbers = [1, 2, 3, 4, 5]
    assert len(numbers) == 5
    assert sum(numbers) == 15
    assert max(numbers) == 5
    assert min(numbers) == 1


def test_dictionary_operations():
    """字典操作测试"""
    data = {"name": "test", "value": 42}
    assert "name" in data
    assert data["value"] == 42
    assert len(data) == 2


class TestBasicClass:
    """基本类测试"""
    
    def test_class_instantiation(self):
        """测试类实例化"""
        class SimpleClass:
            def __init__(self, value):
                self.value = value
            
            def get_value(self):
                return self.value
        
        obj = SimpleClass(10)
        assert obj.get_value() == 10
    
    def test_class_methods(self):
        """测试类方法"""
        class Calculator:
            def add(self, a, b):
                return a + b
            
            def multiply(self, a, b):
                return a * b
        
        calc = Calculator()
        assert calc.add(2, 3) == 5
        assert calc.multiply(4, 5) == 20


@pytest.mark.parametrize("input_value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (10, 20),
])
def test_parametrized(input_value, expected):
    """参数化测试"""
    assert input_value * 2 == expected


def test_exception_handling():
    """异常处理测试"""
    with pytest.raises(ValueError):
        raise ValueError("Test exception")
    
    with pytest.raises(ZeroDivisionError):
        1 / 0


def test_skip_test():
    """跳过测试示例"""
    pytest.skip("This test is skipped for demonstration")


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python 3.8+")
def test_python_version():
    """Python版本测试"""
    assert sys.version_info >= (3, 8)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

