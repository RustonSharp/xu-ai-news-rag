"""
Online search service using Tavily API.
"""
import os
import requests
import json
import getpass
from typing import List, Dict, Any, Optional
from langchain_core.tools import Tool
from utils.logging_config import app_logger
from config.settings import settings


class OnlineSearchService:
    """Service for online search operations using Tavily API."""
    
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self._initialize_api_key()
    
    def _initialize_api_key(self):
        """Initialize API key from environment or user input."""
        if not self.api_key:
            app_logger.warning("TAVILY_API_KEY not found in environment variables")
            try:
                self.api_key = getpass.getpass("请输入Tavily API密钥：")
                os.environ["TAVILY_API_KEY"] = self.api_key
            except Exception as e:
                app_logger.error(f"Failed to get API key: {str(e)}")
                self.api_key = None
    
    def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Perform online search using Tavily API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        if not self.api_key:
            app_logger.error("Tavily API key not available")
            return self._get_mock_results(query)
        
        try:
            app_logger.info(f"🌐 Starting online search: '{query}'")
            
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": max_results,
                "include_answer": False,
                "include_raw_content": False,
                "include_images": False
            }
            
            app_logger.info(f"📋 Search parameters: {payload}")
            
            response = requests.post(url, json=payload)
            app_logger.info(f"📡 Received response, status code: {response.status_code}")
            
            if response.status_code != 200:
                app_logger.error(f"❌ Search request failed, status code: {response.status_code}")
                return self._get_error_results(response.status_code, response.text)
            
            results = response.json()
            app_logger.info("✅ JSON parsing successful")
            
            if "results" not in results:
                app_logger.error("❌ Search results format incorrect, missing 'results' field")
                return self._get_error_results(400, "Invalid response format")
            
            formatted_results = self._format_results(results["results"])
            app_logger.info(f"🎯 Online search completed, returning {len(formatted_results)} formatted results")
            
            return formatted_results
            
        except requests.RequestException as e:
            app_logger.error(f"❌ Search request error: {str(e)}")
            return self._get_error_results(500, f"Request error: {str(e)}")
        except Exception as e:
            app_logger.error(f"❌ Search error: {str(e)}")
            return self._get_error_results(500, f"Search error: {str(e)}")
    
    def _format_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format search results for consistent output."""
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_result = {
                "content": result.get("content", ""),
                "url": result.get("url", ""),
                "title": result.get("title", ""),
                "published_date": "",
                "score": 1.0 - (i * 0.1),
                "is_direct_answer": False
            }
            formatted_results.append(formatted_result)
            app_logger.info(f"📄 Result {i}: {formatted_result['title'][:50]}...")
        
        return formatted_results
    
    def _get_mock_results(self, query: str) -> List[Dict[str, Any]]:
        """Get mock results when API is not available."""
        app_logger.warning("Using mock search results")
        return [
            {
                "content": f"这是关于'{query}'的模拟搜索结果。",
                "url": "https://example.com",
                "title": f"模拟结果: {query}",
                "published_date": "",
                "score": 1.0,
                "is_direct_answer": False
            }
        ]
    
    def _get_error_results(self, status_code: int, error_message: str) -> List[Dict[str, Any]]:
        """Get error results when search fails."""
        return [
            {
                "content": f"搜索请求失败，状态码：{status_code}，错误信息：{error_message}",
                "url": "",
                "title": "搜索错误",
                "published_date": "",
                "score": 0.0,
                "is_direct_answer": False
            }
        ]
    
    def create_search_tool(self) -> Tool:
        """Create a LangChain tool for online search."""
        return Tool(
            name="OnlineSearch",
            func=self.search,
            description="用于搜索最新的网络信息，当你需要最新的、实时的或者知识库中没有的信息时使用此工具"
        )


# Global service instance
online_search_service = OnlineSearchService()
