"""
Integration tests for SimpleFinancialAgent
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from agents.simple_financial_agent import SimpleFinancialAgent

pytestmark = pytest.mark.integration


class TestSimpleFinancialAgent:
    """Test suite for SimpleFinancialAgent"""
    
    def setup_method(self):
        """Setup test instance"""
        self.agent = SimpleFinancialAgent()
    
    def test_extract_ticker_company_name(self):
        """Test ticker extraction from company names"""
        test_cases = [
            ("What is NVIDIA stock price?", "NVDA"),
            ("Apple stock analysis", "AAPL"),
            ("Tell me about Tesla", "TSLA"),
            ("Microsoft fundamentals", "MSFT"),
            ("GOOGL price", "GOOGL")
        ]
        
        for query, expected_ticker in test_cases:
            result = self.agent._extract_ticker(query)
            assert result == expected_ticker, f"Failed for query: {query}"
    
    def test_extract_ticker_explicit(self):
        """Test ticker extraction with explicit ticker"""
        query = "Get data for AAPL"
        result = self.agent._extract_ticker(query)
        assert result == "AAPL"
    
    def test_extract_ticker_none(self):
        """Test ticker extraction when no ticker found"""
        query = "general market news"
        result = self.agent._extract_ticker(query)
        assert result is None
    
    @pytest.mark.asyncio
    @patch('tools.financial_tools.FinancialTools.get_stock_data')
    @patch('tools.financial_tools.FinancialTools.get_analyst_recommendations')
    @patch('tools.financial_tools.FinancialTools.get_fundamentals')
    @patch('tools.financial_tools.FinancialTools.get_company_news')
    async def test_query_success(self, mock_news, mock_fundamentals, mock_analysts, mock_stock):
        """Test successful query processing"""
        # Setup mocks
        mock_stock.return_value = {
            'current_price': 150.0,
            'currency': 'USD',
            'volume': 1000000,
            'market_cap': 2000000000000
        }
        mock_analysts.return_value = {
            'recommendation': 'buy',
            'num_analysts': 30
        }
        mock_fundamentals.return_value = {
            'profit_margins': 0.25
        }
        mock_news.return_value = []
        
        # Execute
        result = await self.agent.query("What is Apple stock price?")
        
        # Assert
        assert isinstance(result, str)
        assert len(result) > 0
        assert 'AAPL' in result or 'Stock Data' in result
    
    @pytest.mark.asyncio
    @patch('tools.financial_tools.FinancialTools.get_stock_data')
    async def test_compare_stocks_success(self, mock_stock):
        """Test successful stock comparison"""
        # Setup mock
        mock_stock.return_value = {
            'current_price': 150.0,
            'currency': 'USD',
            'market_cap': 2000000000000,
            'pe_ratio': 25.0
        }
        
        # Execute
        result = await self.agent.compare_stocks(["AAPL", "MSFT", "GOOGL"])
        
        # Assert
        assert isinstance(result, str)
        assert 'Comparison' in result or 'AAPL' in result
    
    @pytest.mark.asyncio
    async def test_compare_stocks_too_few(self):
        """Test comparison with too few tickers"""
        result = await self.agent.compare_stocks(["AAPL"])
        
        assert "at least 2 tickers" in result.lower()
    
    @pytest.mark.asyncio
    async def test_compare_stocks_too_many(self):
        """Test comparison with too many tickers"""
        result = await self.agent.compare_stocks(
            ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA"]
        )
        
        assert "maximum" in result.lower() or "5 tickers" in result.lower()
    
    @pytest.mark.asyncio
    @patch('tools.web_search_tools.WebSearchTools.search_web')
    async def test_query_no_ticker(self, mock_search):
        """Test query when no ticker is found (falls back to web search)"""
        # Setup mock
        mock_search.return_value = [
            {'title': 'Test', 'snippet': 'Body', 'source': 'test.com'}
        ]
        
        # Execute
        result = await self.agent.query("general financial news")
        
        # Assert
        assert isinstance(result, str)
    
    def test_format_response(self, mock_stock_data, mock_analyst_data):
        """Test response formatting"""
        data = {
            'stock': mock_stock_data,
            'analysts': mock_analyst_data,
            'fundamentals': {},
            'news': []
        }
        
        # Execute
        result = self.agent._format_response("AAPL", data)
        
        # Assert
        assert isinstance(result, str)
        assert len(result) > 0
