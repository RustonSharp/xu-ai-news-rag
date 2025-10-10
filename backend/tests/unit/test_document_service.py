"""
文档服务单元测试
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.document_service import DocumentService
from models.document import Document


class TestDocumentService:
    """文档服务测试"""
    
    def test_get_documents_success(self, mock_database_session, mock_document):
        """测试获取文档列表成功"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_document]
        
        # 创建服务实例
        document_service = DocumentService(mock_database_session)
        
        # 执行测试
        result = document_service.get_documents(mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 1
        assert result[0].title == "测试文档"
    
    def test_get_documents_empty(self, mock_database_session):
        """测试获取空文档列表"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = []
        
        # 创建服务实例
        document_service = DocumentService(mock_database_session)
        
        # 执行测试
        result = document_service.get_documents(mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 0
    
    def test_get_document_by_id_success(self, mock_database_session, mock_document):
        """测试根据ID获取文档成功"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_document
        
        # 创建服务实例
        document_service = DocumentService(mock_database_session)
        
        # 执行测试
        result = document_service.get_document_by_id(1, mock_database_session)
        
        # 验证
        assert result is not None
        assert result.id == 1
        assert result.title == "测试文档"
    
    def test_get_document_by_id_not_found(self, mock_database_session):
        """测试根据ID获取文档不存在"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = None
        
        # 创建服务实例
        document_service = DocumentService(mock_database_session)
        
        # 执行测试
        result = document_service.get_document_by_id(999, mock_database_session)
        
        # 验证
        assert result is None
    
    def test_get_documents_paginated_success(self, mock_database_session, mock_document):
        """测试分页获取文档成功"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_document]
        mock_database_session.exec.return_value.one.return_value = 1
        
        # 创建服务实例
        document_service = DocumentService(mock_database_session)
        
        # 执行测试
        result = document_service.get_documents_paginated(1, 10, mock_database_session)
        
        # 验证
        assert result is not None
        assert 'items' in result
        assert 'total' in result
        assert 'page' in result
        assert 'size' in result
        assert 'total_pages' in result
        assert len(result['items']) == 1
    
    def test_search_documents_success(self, mock_database_session, mock_document):
        """测试搜索文档成功"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_document]
        
        # 创建服务实例
        document_service = DocumentService(mock_database_session)
        
        # 执行测试
        result = document_service.search_documents("测试", mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 1
        assert result[0].title == "测试文档"
    
    def test_search_documents_no_results(self, mock_database_session):
        """测试搜索文档无结果"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = []
        
        # 创建服务实例
        document_service = DocumentService(mock_database_session)
        
        # 执行测试
        result = document_service.search_documents("不存在的关键词", mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 0
    
    def test_get_documents_by_source_success(self, mock_database_session, mock_document):
        """测试根据源获取文档成功"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_document]
        
        # 创建服务实例
        document_service = DocumentService(mock_database_session)
        
        # 执行测试
        result = document_service.get_documents_by_source(1, mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 1
        assert result[0].source_id == 1
    
    def test_get_documents_by_date_range_success(self, mock_database_session, mock_document):
        """测试根据日期范围获取文档成功"""
        # 设置mock
        mock_database_session.exec.return_value.all.return_value = [mock_document]
        
        # 创建服务实例
        document_service = DocumentService(mock_database_session)
        
        # 执行测试
        from datetime import datetime, date
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        result = document_service.get_documents_by_date_range(start_date, end_date, mock_database_session)
        
        # 验证
        assert result is not None
        assert len(result) == 1
    
    def test_get_document_statistics_success(self, mock_database_session):
        """测试获取文档统计成功"""
        # 设置mock
        mock_database_session.exec.return_value.one.return_value = 100
        
        # 创建服务实例
        document_service = DocumentService(mock_database_session)
        
        # 执行测试
        result = document_service.get_document_statistics(mock_database_session)
        
        # 验证
        assert result is not None
        assert 'total_documents' in result
        assert result['total_documents'] == 100
    
    def test_create_document_success(self, mock_database_session):
        """测试创建文档成功"""
        # 创建服务实例
        document_service = DocumentService(mock_database_session)
        
        # 执行测试
        document_data = {
            'title': '新文档',
            'content': '新内容',
            'link': 'http://new.com',
            'description': '新描述',
            'author': '新作者',
            'tags': 'tag1,tag2',
            'source_id': 1
        }
        
        with patch('services.document_service.Document') as mock_document_class:
            mock_document_instance = Mock()
            mock_document_class.return_value = mock_document_instance
            
            result = document_service.create_document(document_data, mock_database_session)
            
            # 验证
            assert result is not None
            mock_database_session.add.assert_called_once()
            mock_database_session.commit.assert_called_once()
    
    def test_update_document_success(self, mock_database_session, mock_document):
        """测试更新文档成功"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_document
        
        # 创建服务实例
        document_service = DocumentService(mock_database_session)
        
        # 执行测试
        update_data = {'title': '更新的标题'}
        result = document_service.update_document(1, update_data, mock_database_session)
        
        # 验证
        assert result is not None
        mock_database_session.commit.assert_called_once()
    
    def test_delete_document_success(self, mock_database_session, mock_document):
        """测试删除文档成功"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = mock_document
        
        # 创建服务实例
        document_service = DocumentService(mock_database_session)
        
        # 执行测试
        result = document_service.delete_document(1, mock_database_session)
        
        # 验证
        assert result is True
        mock_database_session.delete.assert_called_once()
        mock_database_session.commit.assert_called_once()
    
    def test_delete_document_not_found(self, mock_database_session):
        """测试删除不存在的文档"""
        # 设置mock
        mock_database_session.exec.return_value.first.return_value = None
        
        # 创建服务实例
        document_service = DocumentService(mock_database_session)
        
        # 执行测试
        result = document_service.delete_document(999, mock_database_session)
        
        # 验证
        assert result is False
