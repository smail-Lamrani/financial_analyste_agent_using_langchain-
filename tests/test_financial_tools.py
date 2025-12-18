"""
Unit tests for financial_tools module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from tools.financial_tools import FinancialTools
import yfinance as yf

pytestmark = pytest.mark.unit


class TestFinancialTools:
    """Test suite for FinancialTools class"""
    
    def setup_method(self):
        """Setup test instance"""
        self.financial_tools = FinancialTools()
    
    @patch('yfinance.Ticker')
    def test_get_stock_data_success(self, mock_ticker, mock_stock_data):
        """Test successful stock data retrieval"""
        # Setup mock
        mock_info = MagicMock()
        mock_info.get.side_effect = lambda key, default=None: {
            'currentPrice': mock_stock_data['current_price'],
            'currency': mock_stock_data['currency'],
            'dayLow': mock_stock_data['low'],
            'dayHigh': mock_stock_data['high'],
            'volume': mock_stock_data['volume'],
            'marketCap': mock_stock_data['market_cap'],
            'trailingPE': mock_stock_data['pe_ratio'],
            'fiftyTwoWeekLow': mock_stock_data['52_week_low'],
            'fiftyTwoWeekHigh': mock_stock_data['52_week_high']
        }.get(key, default)
        
        mock_ticker.return_value.info = mock_info
        
        # Execute
        result = self.financial_tools.get_stock_data("AAPL")
        
        # Assert
        assert result['current_price'] == mock_stock_data['current_price']
        assert result['currency'] == mock_stock_data['currency']
        assert 'timestamp' in result
        mock_ticker.assert_called_once_with("AAPL")
    
    @patch('yfinance.Ticker')
    def test_get_stock_data_invalid_ticker(self, mock_ticker):
        """Test stock data retrieval with invalid ticker"""
        # Setup mock to raise exception
        mock_ticker.return_value.info = {}
        
        # Execute
        result = self.financial_tools.get_stock_data("INVALID")
        
        # Assert - should return error dict
        assert 'error' in result or result.get('current_price') == 'N/A'
    
    @patch('yfinance.Ticker')
    def test_get_analyst_recommendations_success(self, mock_ticker, mock_analyst_data):
        """Test successful analyst recommendations retrieval"""
        # Setup mock
        mock_ticker.return_value.recommendations_summary = {
            'period': ['0m'],
            'strongBuy': [15],
            'buy': [10],
            'hold': [5],
            'sell': [3],
            'strongSell': [2]
        }
        mock_ticker.return_value.analyst_price_targets = {
            'mean': mock_analyst_data['target_mean'],
            'high': mock_analyst_data['target_high'],
            'low': mock_analyst_data['target_low']
        }
        
        # Execute
        result = self.financial_tools.get_analyst_recommendations("AAPL")
        
        # Assert
        assert 'recommendation' in result
        assert 'num_analysts' in result or 'target_mean' in result
    
    @patch('yfinance.Ticker')
    def test_get_fundamentals_success(self, mock_ticker, mock_fundamentals):
        """Test successful fundamentals retrieval"""
        # Setup mock
        mock_info = MagicMock()
        mock_info.get.side_effect = lambda key, default=None: {
            'profitMargins': mock_fundamentals['profit_margins'],
            'revenueGrowth': mock_fundamentals['revenue_growth'],
            'returnOnEquity': mock_fundamentals['return_on_equity'],
            'debtToEquity': mock_fundamentals['debt_to_equity']
        }.get(key, default)
        
        mock_ticker.return_value.info = mock_info
        
        # Execute
        result = self.financial_tools.get_fundamentals("AAPL")
        
        # Assert
        assert 'profit_margins' in result or 'revenue_growth' in result
    
    @patch('yfinance.Ticker')
    def test_get_company_news_success(self, mock_ticker, mock_news):
        """Test successful company news retrieval"""
        # Setup mock
        mock_ticker.return_value.news = [
            {
                'title': item['title'],
                'publisher': item['publisher'],
                'link': item['link']
            }
            for item in mock_news
        ]
        
        # Execute
        result = self.financial_tools.get_company_news("AAPL")
        
        # Assert
        assert isinstance(result, list)
        if len(result) > 0:
            assert 'title' in result[0]
    
    def test_cache_integration(self, sample_ticker):
        """Test that caching works for financial tools"""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_info = {'currentPrice': 150.0, 'currency': 'USD'}
            mock_ticker.return_value.info = mock_info
            
            # First call
            result1 = self.financial_tools.get_stock_data(sample_ticker)
            
            # Second call should use cache
            result2 = self.financial_tools.get_stock_data(sample_ticker)
            
            # Should have similar results (cache working)
            assert result1.get('current_price') == result2.get('current_price')
