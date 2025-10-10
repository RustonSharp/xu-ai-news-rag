"""
数据模型单元测试
"""
import pytest
from unittest.mock import Mock
import sys
import os
from datetime import datetime, date

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.user import User
from models.document import Document
from models.source import Source
from models.analysis import Analysis
from models.enums.interval import IntervalEnum


class TestUserModel:
    """用户模型测试"""
    
    def test_user_creation(self):
        """测试用户创建"""
        user = User(
            username="test_user",
            email="test@example.com",
            password_hash="hashed_password",
            is_active=True
        )
        
        # 验证
        assert user.username == "test_user"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.is_active is True
        assert user.id is None  # 未保存到数据库
    
    def test_user_creation_with_id(self):
        """测试带ID的用户创建"""
        user = User(
            id=1,
            username="test_user",
            email="test@example.com",
            password_hash="hashed_password",
            is_active=True
        )
        
        # 验证
        assert user.id == 1
        assert user.username == "test_user"
    
    def test_user_str_representation(self):
        """测试用户字符串表示"""
        user = User(
            username="test_user",
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        # 验证
        assert str(user) == "User(id=None, username='test_user', email='test@example.com')"
    
    def test_user_equality(self):
        """测试用户相等性"""
        user1 = User(id=1, username="test_user", email="test@example.com")
        user2 = User(id=1, username="test_user", email="test@example.com")
        user3 = User(id=2, username="test_user", email="test@example.com")
        
        # 验证
        assert user1 == user2
        assert user1 != user3


class TestDocumentModel:
    """文档模型测试"""
    
    def test_document_creation(self):
        """测试文档创建"""
        document = Document(
            title="测试文档",
            link="http://test.com",
            description="测试描述",
            author="测试作者",
            tags="tag1,tag2",
            source_id=1
        )
        
        # 验证
        assert document.title == "测试文档"
        # content 字段不存在于模型中
        assert document.link == "http://test.com"
        assert document.description == "测试描述"
        assert document.author == "测试作者"
        assert document.tags == "tag1,tag2"
        assert document.source_id == 1
        assert document.id is None
    
    def test_document_creation_with_dates(self):
        """测试带日期的文档创建"""
        pub_date = datetime(2025, 1, 1, 12, 0, 0)
        crawled_at = datetime(2025, 1, 1, 13, 0, 0)
        
        document = Document(
            title="测试文档",
            link="http://test.com",
            pub_date=pub_date,
            crawled_at=crawled_at,
            source_id=1
        )
        
        # 验证
        assert document.pub_date == pub_date
        assert document.crawled_at == crawled_at
    
    def test_document_str_representation(self):
        """测试文档字符串表示"""
        document = Document(
            title="测试文档",
            link="http://test.com",
            source_id=1
        )
        
        # 验证
        assert "测试文档" in str(document)
        assert "http://test.com" in str(document)
    
    def test_document_equality(self):
        """测试文档相等性"""
        doc1 = Document(id=1, title="测试文档", source_id=1)
        doc2 = Document(id=1, title="测试文档", source_id=1)
        doc3 = Document(id=2, title="测试文档", source_id=1)
        
        # 验证
        assert doc1 == doc2
        assert doc1 != doc3


class TestSourceModel:
    """源模型测试"""
    
    def test_source_creation(self):
        """测试源创建"""
        source = Source(
            name="测试源",
            url="http://test.com/rss",
            interval="ONE_DAY",
            is_paused=False
        )
        
        # 验证
        assert source.name == "测试源"
        assert source.url == "http://test.com/rss"
        assert source.interval == "ONE_DAY"
        assert source.is_paused is False
        assert source.id is None
    
    def test_source_creation_with_all_fields(self):
        """测试带所有字段的源创建"""
        last_sync = datetime(2025, 1, 1, 12, 0, 0)
        
        source = Source(
            id=1,
            name="测试源",
            url="http://test.com/rss",
            interval="TWELVE_HOUR",
            is_paused=True,
            is_active=False,
            last_sync=last_sync
        )
        
        # 验证
        assert source.id == 1
        assert source.name == "测试源"
        assert source.url == "http://test.com/rss"
        assert source.interval == "TWELVE_HOUR"
        assert source.is_paused is True
        assert source.is_active is False
        assert source.last_sync == last_sync
    
    def test_source_str_representation(self):
        """测试源字符串表示"""
        source = Source(
            name="测试源",
            url="http://test.com/rss",
            interval="ONE_DAY"
        )
        
        # 验证
        assert "测试源" in str(source)
        assert "http://test.com/rss" in str(source)
    
    def test_source_equality(self):
        """测试源相等性"""
        source1 = Source(id=1, name="测试源", url="http://test.com/rss")
        source2 = Source(id=1, name="测试源", url="http://test.com/rss")
        source3 = Source(id=2, name="测试源", url="http://test.com/rss")
        
        # 验证
        assert source1 == source2
        assert source1 != source3


class TestAnalysisModel:
    """分析模型测试"""
    
    def test_analysis_creation(self):
        """测试分析创建"""
        analysis = Analysis(
            method="clustering",
            silhouette_score=0.8,
            total_documents=100,
            total_clusters=5,
            report_json='{"clusters": 3, "parameters": {"k": 5}}'
        )
        
        # 验证
        assert analysis.method == "clustering"
        assert analysis.silhouette_score == 0.8
        assert analysis.total_documents == 100
        assert analysis.total_clusters == 5
        assert analysis.report_json == '{"clusters": 3, "parameters": {"k": 5}}'
        assert analysis.id is None
    
    def test_analysis_creation_with_dates(self):
        """测试带日期的分析创建"""
        created_at = datetime(2025, 1, 1, 12, 0, 0)
        
        analysis = Analysis(
            title="测试分析",
            content="分析内容",
            analysis_type="clustering",
            created_at=created_at
        )
        
        # 验证
        assert analysis.created_at == created_at
    
    def test_analysis_str_representation(self):
        """测试分析字符串表示"""
        analysis = Analysis(
            method="clustering",
            silhouette_score=0.8,
            total_documents=100,
            total_clusters=5,
            report_json='{"clusters": 3}'
        )
        
        # 验证
        assert "clustering" in str(analysis)
        assert "100" in str(analysis)
    
    def test_analysis_equality(self):
        """测试分析相等性"""
        analysis1 = Analysis(id=1, method="clustering", report_json='{"test": 1}')
        analysis2 = Analysis(id=1, method="clustering", report_json='{"test": 1}')
        analysis3 = Analysis(id=2, method="clustering", report_json='{"test": 2}')
        
        # 验证
        assert analysis1 == analysis2
        assert analysis1 != analysis3


class TestIntervalEnum:
    """间隔枚举测试"""
    
    def test_interval_values(self):
        """测试间隔值"""
        # 验证
        assert IntervalEnum.SIX_HOUR == "SIX_HOUR"
        assert IntervalEnum.TWELVE_HOUR == "TWELVE_HOUR"
        assert IntervalEnum.ONE_DAY == "ONE_DAY"
    
    def test_interval_from_string(self):
        """测试从字符串创建间隔"""
        # 验证
        assert IntervalEnum("SIX_HOUR") == IntervalEnum.SIX_HOUR
        assert IntervalEnum("ONE_DAY") == IntervalEnum.ONE_DAY
        assert IntervalEnum("TWELVE_HOUR") == IntervalEnum.TWELVE_HOUR
    
    def test_interval_invalid_value(self):
        """测试无效间隔值"""
        with pytest.raises(ValueError):
            IntervalEnum("INVALID_INTERVAL")
    
    def test_interval_str_representation(self):
        """测试间隔字符串表示"""
        # 验证
        assert str(IntervalEnum.SIX_HOUR) == "IntervalEnum.SIX_HOUR"
        assert str(IntervalEnum.ONE_DAY) == "IntervalEnum.ONE_DAY"
