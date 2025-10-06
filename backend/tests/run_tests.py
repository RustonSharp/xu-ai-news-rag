#!/usr/bin/env python3
"""
测试运行脚本
支持运行不同类型的测试
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests(test_type="all", verbose=False, coverage=False, parallel=False):
    """
    运行测试
    
    Args:
        test_type: 测试类型 (all, unit, integration, api)
        verbose: 是否显示详细输出
        coverage: 是否生成覆盖率报告
        parallel: 是否并行运行测试
    """
    # 设置环境变量
    os.environ['TESTING'] = 'true'
    os.environ['EMBEDDING_MODEL_NAME'] = 'sentence-transformers/all-MiniLM-L6-v2'
    os.environ['RERANK_MODEL_NAME'] = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
    os.environ['TAVILY_API_KEY'] = 'test_key'
    
    # 构建pytest命令
    cmd = ['python', '-m', 'pytest']
    
    # 添加测试目录
    if test_type == "all":
        cmd.append('tests/')
    elif test_type == "unit":
        cmd.append('tests/unit/')
    elif test_type == "integration":
        cmd.append('tests/integration/')
    elif test_type == "api":
        cmd.append('tests/api/')
    else:
        print(f"未知的测试类型: {test_type}")
        return False
    
    # 添加选项
    if verbose:
        cmd.append('-v')
    
    if parallel:
        cmd.extend(['-n', 'auto'])
    
    if coverage:
        cmd.extend([
            '--cov=.',
            '--cov-report=html',
            '--cov-report=term-missing'
        ])
    
    # 添加其他选项
    cmd.extend([
        '--tb=short',  # 简短的traceback
        '--strict-markers',  # 严格的标记
        '--disable-warnings',  # 禁用警告
        '--color=yes'  # 彩色输出
    ])
    
    print(f"运行命令: {' '.join(cmd)}")
    
    # 运行测试
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"运行测试时出错: {e}")
        return False


def run_specific_test(test_file, test_function=None):
    """
    运行特定测试文件或函数
    
    Args:
        test_file: 测试文件路径
        test_function: 特定测试函数名（可选）
    """
    os.environ['TESTING'] = 'true'
    os.environ['EMBEDDING_MODEL_NAME'] = 'sentence-transformers/all-MiniLM-L6-v2'
    os.environ['RERANK_MODEL_NAME'] = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
    os.environ['TAVILY_API_KEY'] = 'test_key'
    
    cmd = ['python', '-m', 'pytest', test_file]
    
    if test_function:
        cmd.append(f'::{test_function}')
    
    cmd.extend(['-v', '--tb=short'])
    
    print(f"运行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"运行测试时出错: {e}")
        return False


def install_test_dependencies():
    """安装测试依赖"""
    dependencies = [
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'pytest-xdist>=3.0.0',
        'pytest-mock>=3.10.0',
        'pytest-html>=3.1.0',
        'pytest-json-report>=1.5.0'
    ]
    
    print("安装测试依赖...")
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], check=True)
            print(f"✓ {dep}")
        except subprocess.CalledProcessError as e:
            print(f"✗ {dep}: {e}")
            return False
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='运行测试')
    parser.add_argument(
        '--type', 
        choices=['all', 'unit', 'integration', 'api'],
        default='all',
        help='测试类型'
    )
    parser.add_argument(
        '--file',
        help='特定测试文件'
    )
    parser.add_argument(
        '--function',
        help='特定测试函数'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出'
    )
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='生成覆盖率报告'
    )
    parser.add_argument(
        '--parallel', '-p',
        action='store_true',
        help='并行运行测试'
    )
    parser.add_argument(
        '--install-deps',
        action='store_true',
        help='安装测试依赖'
    )
    
    args = parser.parse_args()
    
    if args.install_deps:
        if install_test_dependencies():
            print("测试依赖安装完成")
        else:
            print("测试依赖安装失败")
            return 1
    
    if args.file:
        success = run_specific_test(args.file, args.function)
    else:
        success = run_tests(
            test_type=args.type,
            verbose=args.verbose,
            coverage=args.coverage,
            parallel=args.parallel
        )
    
    if success:
        print("\n✓ 所有测试通过")
        return 0
    else:
        print("\n✗ 测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())

