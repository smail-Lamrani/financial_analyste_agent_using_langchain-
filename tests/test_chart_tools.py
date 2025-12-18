"""
Unit tests for chart_tools module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from tools.chart_tools import ChartTools, plot_stock, plot_comparison
import os
import tempfile

pytestmark = pytest.mark.unit


class TestChartTools:
    """Test suite for ChartTools class"""
    
    def setup_method(self):
        """Setup test instance with temp directory"""
        self.test_dir = tempfile.mkdtemp()
        self.chart_tools = ChartTools(chart_dir=self.test_dir)
    
    def teardown_method(self):
        """Cleanup test charts"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('yfinance.Ticker')
    def test_plot_stock_history_success(self, mock_ticker):
        """Test successful stock chart generation"""
        # Setup mock data
        import pandas as pd
        from datetime import datetime, timedelta
        
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        mock_hist = pd.DataFrame({
            'Open': [100 + i for i in range(100)],
            'Close': [101 + i for i in range(100)],
            'High': [102 + i for i in range(100)],
            'Low': [99 + i for i in range(100)],
            'Volume': [1000000 + i*10000 for i in range(100)]
        }, index=dates)
        
        mock_ticker.return_value.history.return_value = mock_hist
        
        # Execute
        chart_path = self.chart_tools.plot_stock_history(
            "AAPL", 
            period="3mo",
            show_ma=True,
            show_volume=True
        )
        
        # Assert
        assert os.path.exists(chart_path)
        assert chart_path.endswith('.png')
        assert 'AAPL' in chart_path
    
    @patch('yfinance.Ticker')
    def test_plot_stock_history_no_volume(self, mock_ticker):
        """Test chart generation without volume"""
        import pandas as pd
        from datetime import datetime
        
        dates = pd.date_range(end=datetime.now(), periods=50, freq='D')
        mock_hist = pd.DataFrame({
            'Open': [100] * 50,
            'Close': [101] * 50,
            'High': [102] * 50,
            'Low': [99] * 50,
            'Volume': [1000000] * 50
        }, index=dates)
        
        mock_ticker.return_value.history.return_value = mock_hist
        
        # Execute
        chart_path = self.chart_tools.plot_stock_history(
            "MSFT",
            period="1mo",
            show_ma=False,
            show_volume=False
        )
        
        # Assert
        assert os.path.exists(chart_path)
    
    @patch('yfinance.Ticker')
    def test_plot_stock_history_empty_data(self, mock_ticker):
        """Test chart generation with empty data"""
        import pandas as pd
        
        # Setup mock to return empty DataFrame
        mock_ticker.return_value.history.return_value = pd.DataFrame()
        
        # Execute & Assert
        with pytest.raises(ValueError, match="No data available"):
            self.chart_tools.plot_stock_history("INVALID")
    
    @patch('yfinance.Ticker')
    def test_plot_comparison_chart_success(self, mock_ticker):
        """Test successful comparison chart generation"""
        import pandas as pd
        from datetime import datetime
        
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        
        # Mock different data for each ticker
        def mock_history(period):
            import random
            base = random.randint(50, 200)
            return pd.DataFrame({
                'Open': [base + i for i in range(100)],
                'Close': [base + i + 1 for i in range(100)],
                'High': [base + i + 2 for i in range(100)],
                'Low': [base + i - 1 for i in range(100)],
                'Volume': [1000000] * 100
            }, index=dates)
        
        mock_ticker.return_value.history = mock_history
        
        # Execute
        chart_path = self.chart_tools.plot_comparison_chart(
            ["AAPL", "MSFT", "GOOGL"],
            period="1y",
            normalize=True
        )
        
        # Assert
        assert os.path.exists(chart_path)
        assert 'comparison' in chart_path
    
    @patch('yfinance.Ticker')
    def test_plot_comparison_chart_normalized(self, mock_ticker):
        """Test comparison chart with normalization"""
        import pandas as pd
        from datetime import datetime
        
        dates = pd.date_range(end=datetime.now(), periods=50, freq='D')
        mock_hist = pd.DataFrame({
            'Close': [100 + i*2 for i in range(50)]
        }, index=dates)
        
        mock_ticker.return_value.history.return_value = mock_hist
        
        # Execute
        chart_path = self.chart_tools.plot_comparison_chart(
            ["AAPL", "MSFT"],
            period="1mo",
            normalize=True
        )
        
        # Assert
        assert os.path.exists(chart_path)
    
    def test_chart_directory_creation(self):
        """Test that chart directory is created"""
        new_dir = os.path.join(self.test_dir, "new_charts")
        charts = ChartTools(chart_dir=new_dir)
        
        assert os.path.exists(new_dir)
    
    @patch('yfinance.Ticker')
    def test_convenience_function_plot_stock(self, mock_ticker):
        """Test convenience function for plotting stock"""
        import pandas as pd
        from datetime import datetime
        
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        mock_hist = pd.DataFrame({
            'Open': [100] * 30,
            'Close': [101] * 30,
            'High': [102] * 30,
            'Low': [99] * 30,
            'Volume': [1000000] * 30
        }, index=dates)
        
        mock_ticker.return_value.history.return_value = mock_hist
        
        # Execute
        with patch.object(ChartTools, '__init__', lambda x, chart_dir='charts': setattr(x, 'chart_dir', self.test_dir)):
            chart_path = plot_stock("AAPL", period="1mo")
        
        # Should not raise errors
        assert isinstance(chart_path, str)
