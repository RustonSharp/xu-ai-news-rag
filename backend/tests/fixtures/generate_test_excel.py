#!/usr/bin/env python3
"""
生成测试upload_excel接口的Excel文档
"""

import pandas as pd
from datetime import datetime, timedelta
import os

def create_test_excel():
    """创建用于测试upload_excel接口的Excel文档"""
    
    # 创建测试数据
    test_data = [
        {
            'title': '人工智能在医疗领域的应用',
            'link': 'https://example.com/ai-healthcare',
            'description': '探讨人工智能技术在医疗诊断、药物研发和健康管理方面的最新进展',
            'pub_date': datetime.now() - timedelta(days=5),
            'author': '张医生',
            'tags': 'AI,医疗,科技'
        },
        {
            'title': '量子计算的未来发展趋势',
            'link': 'https://example.com/quantum-computing',
            'description': '分析量子计算技术的发展现状、面临的挑战以及未来可能的应用场景',
            'pub_date': datetime.now() - timedelta(days=10),
            'author': '李研究员',
            'tags': '量子计算,科技,未来'
        },
        {
            'title': '区块链技术在金融领域的应用',
            'link': 'https://example.com/blockchain-finance',
            'description': '介绍区块链技术如何改变传统金融行业，包括支付、清算和资产管理等方面',
            'pub_date': datetime.now() - timedelta(days=15),
            'author': '王分析师',
            'tags': '区块链,金融,技术'
        },
        {
            'title': '可持续能源技术的发展',
            'link': 'https://example.com/sustainable-energy',
            'description': '探讨太阳能、风能等可再生能源技术的最新进展及其对环境的影响',
            'pub_date': datetime.now() - timedelta(days=20),
            'author': '陈工程师',
            'tags': '可再生能源,环保,技术'
        },
        {
            'title': '5G技术对社会的影响',
            'link': 'https://example.com/5g-impact',
            'description': '分析5G技术如何改变人们的生活方式、工作模式和社交互动',
            'pub_date': datetime.now() - timedelta(days=25),
            'author': '赵专家',
            'tags': '5G,通信,社会'
        }
    ]
    
    # 创建DataFrame
    df = pd.DataFrame(test_data)
    
    # 确保输出目录存在
    output_dir = '/Users/yans/Code/xu-ai-news-rag/test_data'
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存为Excel文件
    output_path = os.path.join(output_dir, 'test_documents.xlsx')
    df.to_excel(output_path, index=False)
    
    print(f"测试Excel文档已生成: {output_path}")
    print(f"包含 {len(test_data)} 条测试数据")
    
    return output_path

if __name__ == '__main__':
    create_test_excel()