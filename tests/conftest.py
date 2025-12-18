"""
Pytest configuration and shared fixtures
"""
import pytest
import asyncio
from typing import Generator
import os

# Set test environment
os.environ['TESTING'] = '1'

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_ticker():
    """Sample ticker for testing"""
    return "AAPL"

@pytest.fixture
def sample_tickers():
    """Sample list of tickers for comparison tests"""
    return ["AAPL", "MSFT", "GOOGL"]

@pytest.fixture
def mock_stock_data():
    """Mock stock data response"""
    return {
        "current_price": 150.25,
        "currency": "USD",
        "low": 148.50,
        "high": 151.75,
        "volume": 50000000,
        "market_cap": 2500000000000,
        "pe_ratio": 25.5,
        "52_week_low": 120.00,
        "52_week_high": 180.00,
        "timestamp": "2025-12-14T12:00:00"
    }

@pytest.fixture
def mock_analyst_data():
    """Mock analyst recommendations"""
    return {
        "recommendation": "buy",
        "num_analysts": 35,
        "target_mean": 175.50,
        "target_high": 200.00,
        "target_low": 150.00
    }

@pytest.fixture
def mock_fundamentals():
    """Mock fundamental data"""
    return {
        "profit_margins": 0.25,
        "revenue_growth": 0.15,
        "return_on_equity": 0.45,
        "debt_to_equity": 1.2
    }

@pytest.fixture
def mock_news():
    """Mock news items"""
    return [
        {
            "title": "Company Reports Strong Earnings",
            "publisher": "Financial Times",
            "link": "https://example.com/news1"
        },
        {
            "title": "Stock Price Hits New High",
            "publisher": "Bloomberg",
            "link": "https://example.com/news2"
        }
    ]

@pytest.fixture
def mock_web_search_results():
    """Mock web search results"""
    return [
        {
            "title": "Test Result 1",
            "snippet": "This is a test snippet",
            "link": "https://example.com/1",
            "source": "example.com"
        },
        {
            "title": "Test Result 2",
            "snippet": "Another test snippet",
            "link": "https://example.com/2",
            "source": "example.com"
        }
    ]

@pytest.fixture(autouse=True)
def clean_charts_dir():
    """Clean up charts directory after tests"""
    yield
    # Cleanup code here if needed
    import shutil
    chart_dir = "charts/test_charts"
    if os.path.exists(chart_dir):
        shutil.rmtree(chart_dir)
