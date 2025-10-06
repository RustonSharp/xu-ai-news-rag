"""
assistant.py 单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assistant import create_assistant, query_with_sources


class TestCreateAssistant:
    """测试create_assistant函数"""
    
    @patch('assistant.create_knowledge_base_tool')
    @patch('assistant.create_online_search_tool')
    @patch('assistant.Ollama')
    @patch('assistant.initialize_agent')
    def test_create_assistant_success(self, mock_agent, mock_ollama, mock_online_tool, mock_kb_tool):
        """测试成功创建助手"""
        # 设置mock
        mock_kb_tool.return_value = Mock()
        mock_online_tool.return_value = Mock()
        mock_llm = Mock()
        mock_ollama.return_value = mock_llm
        mock_agent.return_value = Mock()
        
        # 执行测试
        result = create_assistant()
        
        # 验证
        assert result is not None
        mock_ollama.assert_called_once_with(model="qwen2.5:3b", temperature=0)
        mock_agent.assert_called_once()
    
    @patch('assistant.create_knowledge_base_tool')
    @patch('assistant.create_online_search_tool')
    @patch('assistant.Ollama')
    def test_create_assistant_tool_creation(self, mock_ollama, mock_online_tool, mock_kb_tool):
        """测试工具创建"""
        # 设置mock
        mock_kb_tool.return_value = Mock()
        mock_online_tool.return_value = Mock()
        mock_llm = Mock()
        mock_ollama.return_value = mock_llm
        
        with patch('assistant.initialize_agent') as mock_agent:
            mock_agent.return_value = Mock()
            
            # 执行测试
            create_assistant()
            
            # 验证工具被创建
            mock_kb_tool.assert_called_once()
            mock_online_tool.assert_called_once()


class TestQueryWithSources:
    """测试query_with_sources函数"""
    
    @patch('assistant.create_online_search_tool')
    @patch('assistant.create_knowledge_base_tool')
    @patch('assistant.Ollama')
    def test_query_with_sources_knowledge_base_success(self, mock_ollama, mock_kb_tool, mock_online_tool):
        """测试知识库查询成功的情况"""
        # 设置mock
        mock_llm = Mock()
        mock_llm.invoke.return_value = "相关"
        mock_ollama.return_value = mock_llm
        
        mock_kb = Mock()
        mock_kb.invoke.return_value = [
            {
                "content": "相关文档内容",
                "metadata": {"title": "测试标题"}
            }
        ]
        mock_kb_tool.return_value = mock_kb
        
        # 执行测试
        result = query_with_sources("测试问题")
        
        # 验证
        assert result['origin'] == 'knowledge_base'
        assert 'answer' in result
        mock_kb.invoke.assert_called_once()
        # 注意：在线搜索工具会被创建但不会被调用
        mock_online_tool.assert_called_once()
    
    @patch('assistant.create_online_search_tool')
    @patch('assistant.create_knowledge_base_tool')
    @patch('assistant.Ollama')
    def test_query_with_sources_fallback_to_online(self, mock_ollama, mock_kb_tool, mock_online_tool):
        """测试fallback到在线搜索的情况"""
        # 设置mock
        mock_llm = Mock()
        mock_llm.invoke.return_value = "不相关"  # 知识库结果不相关
        mock_ollama.return_value = mock_llm
        
        mock_kb = Mock()
        mock_kb.invoke.return_value = [
            {
                "content": "不相关文档内容",
                "metadata": {"title": "不相关标题"}
            }
        ]
        mock_kb_tool.return_value = mock_kb
        
        mock_online = Mock()
        mock_online.invoke.return_value = [
            {
                "content": "在线搜索结果",
                "title": "在线标题",
                "url": "https://example.com"
            }
        ]
        mock_online_tool.return_value = mock_online
        
        # 执行测试
        result = query_with_sources("测试问题")
        
        # 验证
        assert result['origin'] == 'online_search'
        assert 'answer' in result
        mock_kb.invoke.assert_called_once()
        mock_online.invoke.assert_called_once()
    
    @patch('assistant.create_online_search_tool')
    @patch('assistant.create_knowledge_base_tool')
    @patch('assistant.Ollama')
    def test_query_with_sources_empty_knowledge_base(self, mock_ollama, mock_kb_tool, mock_online_tool):
        """测试知识库为空的情况"""
        # 设置mock
        mock_llm = Mock()
        mock_llm.invoke.return_value = "关键词分析结果"
        mock_ollama.return_value = mock_llm
        
        mock_kb = Mock()
        mock_kb.invoke.return_value = []  # 空结果
        mock_kb_tool.return_value = mock_kb
        
        mock_online = Mock()
        mock_online.invoke.return_value = [
            {
                "content": "在线搜索结果",
                "title": "在线标题"
            }
        ]
        mock_online_tool.return_value = mock_online
        
        # 执行测试
        result = query_with_sources("测试问题")
        
        # 验证
        assert result['origin'] == 'online_search'
        assert 'answer' in result
        mock_online.invoke.assert_called_once()
    
    @patch('assistant.create_online_search_tool')
    @patch('assistant.create_knowledge_base_tool')
    @patch('assistant.Ollama')
    def test_query_with_sources_placeholder_text(self, mock_ollama, mock_kb_tool, mock_online_tool):
        """测试知识库返回占位符文本的情况"""
        # 设置mock
        mock_llm = Mock()
        mock_llm.invoke.return_value = "关键词分析结果"
        mock_ollama.return_value = mock_llm
        
        mock_kb = Mock()
        mock_kb.invoke.return_value = [
            {
                "content": "Placeholder text",  # 占位符文本
                "metadata": {"title": "测试标题"}
            }
        ]
        mock_kb_tool.return_value = mock_kb
        
        mock_online = Mock()
        mock_online.invoke.return_value = [
            {
                "content": "在线搜索结果",
                "title": "在线标题"
            }
        ]
        mock_online_tool.return_value = mock_online
        
        # 执行测试
        result = query_with_sources("测试问题")
        
        # 验证
        assert result['origin'] == 'online_search'
        assert 'answer' in result
        mock_online.invoke.assert_called_once()


class TestAssistantIntegration:
    """测试助手集成功能"""
    
    @patch('assistant.create_knowledge_base_tool')
    @patch('assistant.create_online_search_tool')
    @patch('assistant.Ollama')
    @patch('assistant.initialize_agent')
    def test_assistant_agent_creation(self, mock_agent, mock_ollama, mock_online_tool, mock_kb_tool):
        """测试智能体创建"""
        # 设置mock
        mock_kb_tool.return_value = Mock()
        mock_online_tool.return_value = Mock()
        mock_llm = Mock()
        mock_ollama.return_value = mock_llm
        
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        
        # 执行测试
        assistant = create_assistant()
        
        # 验证
        assert assistant == mock_agent_instance
        mock_agent.assert_called_once()
        
        # 验证agent参数
        call_args = mock_agent.call_args
        assert 'tools' in call_args.kwargs
        assert 'llm' in call_args.kwargs
        assert 'agent' in call_args.kwargs
        assert 'agent_kwargs' in call_args.kwargs
        
        # 验证系统消息包含正确的指导
        system_message = call_args.kwargs['agent_kwargs']['system_message']
        assert "本地新闻知识库" in system_message
        assert "优先使用" in system_message
        assert "在线搜索" in system_message

