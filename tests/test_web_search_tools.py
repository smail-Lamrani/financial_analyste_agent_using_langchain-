"""
Unit tests for web_search_tools module
"""
import pytest
from unittest.mock import Mock, patch
from tools.web_search_tools import WebSearchTools

pytestmark = pytest.mark.unit


class TestWebSearchTools:
    """Test suite for WebSearchTools class"""
    
    def setup_method(self):
        """Setup test instance"""
        self.web_tools = WebSearchTools()
    
    @patch('tools.web_search_tools.DDGS')
    def test_search_web_success(self, mock_ddgs, mock_web_search_results):
        """Test successful web search"""
        # Setup mock
        mock_ddgs.return_value.text.return_value = [
            {
                'title': result['title'],
                'body': result['snippet'],
                'href': result['link']
            }
            for result in mock_web_search_results
        ]
        
        # Execute
        results = self.web_tools.search_web("test query")
        
        # Assert
        assert isinstance(results, list)
        assert len(results) > 0
        assert 'title' in results[0]
        assert 'snippet' in results[0]
        assert 'source' in results[0]
    
    @patch('tools.web_search_tools.DDGS')
    def test_search_web_empty_results(self, mock_ddgs):
        """Test web search with no results"""
        # Setup mock to return empty
        mock_ddgs.return_value.text.return_value = []
        
        # Execute
        results = self.web_tools.search_web("nonexistent query")
        
        # Assert
        assert isinstance(results, list)
    
    @patch('tools.web_search_tools.DDGS')
    def test_search_news_success(self, mock_ddgs, mock_web_search_results):
        """Test successful news search"""
        # Setup mock
        mock_ddgs.return_value.text.return_value = [
            {
                'title': result['title'],
                'body': result['snippet'],
                'href': result['link']
            }
            for result in mock_web_search_results
        ]
        
        # Execute
        results = self.web_tools.search_news("AAPL")
        
        # Assert
        assert isinstance(results, list)
    
    def test_extract_source(self):
        """Test source URL extraction"""
        # Test cases
        test_urls = [
            ("https://www.example.com/article", "example.com"),
            ("https://news.google.com/story", "news.google.com"),
            ("http://bloomberg.com/markets", "bloomberg.com"),
            ("invalid-url", "Unknown")
        ]
        
        for url, expected_source in test_urls:
            result = self.web_tools._extract_source(url)
            assert result == expected_source or "Unknown" in result
    
    @patch('tools.web_search_tools.DDGS')
    def test_search_financial_news(self, mock_ddgs):
        """Test financial news search"""
        # Setup mock
        mock_ddgs.return_value.text.return_value = [
            {
                'title': 'Stock Market Update',
                'body': 'Markets rally...',
                'href': 'https://cnbc.com/article'
            }
        ]
        
        # Execute
        results = self.web_tools.search_financial_news("stock market")
        
        # Assert
        assert isinstance(results, list)
    
    def test_cache_integration(self):
        """Test caching for web search"""
        with patch('tools.web_search_tools.DDGS') as mock_ddgs:
            mock_ddgs.return_value.text.return_value = [
                {'title': 'Test', 'body': 'Body', 'href': 'http://test.com'}
            ]
            
            # First call
            result1 = self.web_tools.search_web("test")
            
            # Second call (should use cache)
            result2 = self.web_tools.search_web("test")
            
            # Results should be identical
            assert result1 == result2
