#!/usr/bin/env python3
"""
测试运行示例脚本
展示如何运行不同类型的测试
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"运行: {description}")
    print(f"命令: {cmd}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"退出码: {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        print(f"运行命令时出错: {e}")
        return False

def main():
    """主函数"""
    print("新闻知识库系统 - 测试运行示例")
    print("="*60)
    
    # 确保在正确的目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 激活conda环境
    conda_env = "news-rag11"
    
    # 1. 运行简单测试
    print("\n1. 运行简单测试")
    cmd = f"conda activate {conda_env} && python -m pytest tests/simple_test.py -v"
    run_command(cmd, "简单功能测试")
    
    # 2. 运行示例测试
    print("\n2. 运行示例测试")
    cmd = f"conda activate {conda_env} && python -m pytest tests/example_test.py -v"
    run_command(cmd, "新闻知识库系统示例测试")
    
    # 3. 运行所有测试（不包括有问题的单元测试）
    print("\n3. 运行所有可用测试")
    cmd = f"conda activate {conda_env} && python -m pytest tests/simple_test.py tests/example_test.py -v"
    run_command(cmd, "所有可用测试")
    
    # 4. 运行测试并生成覆盖率报告
    print("\n4. 运行测试并生成覆盖率报告")
    cmd = f"conda activate {conda_env} && python -m pytest tests/simple_test.py tests/example_test.py --cov=. --cov-report=html --cov-report=term-missing --cov-exclude=tests/* -v"
    run_command(cmd, "测试覆盖率分析")
    
    # 5. 运行特定测试类
    print("\n5. 运行特定测试类")
    cmd = f"conda activate {conda_env} && python -m pytest tests/example_test.py::TestNewsRAGSystem -v"
    run_command(cmd, "新闻RAG系统测试类")
    
    # 6. 运行特定测试方法
    print("\n6. 运行特定测试方法")
    cmd = f"conda activate {conda_env} && python -m pytest tests/example_test.py::TestNewsRAGSystem::test_query_processing_workflow -v"
    run_command(cmd, "查询处理工作流程测试")
    
    # 7. 并行运行测试
    print("\n7. 并行运行测试")
    cmd = f"conda activate {conda_env} && python -m pytest tests/simple_test.py tests/example_test.py -n auto -v"
    run_command(cmd, "并行测试执行")
    
    # 8. 运行测试并生成详细报告
    print("\n8. 运行测试并生成详细报告")
    cmd = f"conda activate {conda_env} && python -m pytest tests/simple_test.py tests/example_test.py --html=test_report.html --self-contained-html -v"
    run_command(cmd, "生成HTML测试报告")
    
    print("\n" + "="*60)
    print("测试运行完成！")
    print("="*60)
    
    # 显示可用的测试文件
    print("\n可用的测试文件:")
    test_files = [
        "tests/simple_test.py - 基础功能测试",
        "tests/example_test.py - 新闻知识库系统示例测试",
        "tests/unit/test_assistant.py - 助手单元测试（需要修复）",
        "tests/unit/test_tools.py - 工具单元测试（需要修复）",
        "tests/integration/test_knowledge_base.py - 知识库集成测试（需要修复）",
        "tests/api/test_assistant_api.py - API测试（需要修复）",
        "tests/api/test_other_apis.py - 其他API测试（需要修复）"
    ]
    
    for test_file in test_files:
        print(f"  - {test_file}")
    
    print("\n运行测试的命令示例:")
    print("  python -m pytest tests/simple_test.py -v")
    print("  python -m pytest tests/example_test.py -v")
    print("  python -m pytest tests/ --cov=. --cov-report=html")
    print("  python -m pytest tests/ -n auto")
    print("  python -m pytest tests/ --html=report.html")

if __name__ == "__main__":
    main()
