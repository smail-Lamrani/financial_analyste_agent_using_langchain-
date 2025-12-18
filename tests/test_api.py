"""
API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient
from api.server import app

pytestmark = pytest.mark.api


class TestAPIEndpoints:
    """Test suite for API endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'version' in data
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'service' in data
    
    def test_status_endpoint(self):
        """Test status endpoint"""
        response = self.client.get("/status")
        
        assert response.status_code == 200
        data = response.json()
        assert 'service' in data
        assert 'agents' in data
    
    @pytest.mark.slow
    def test_query_endpoint_valid(self):
        """Test query endpoint with valid request"""
        response = self.client.post(
            "/query",
            json={"query": "What is AAPL stock price?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'response' in data
        assert 'success' in data
        assert 'response_time' in data
        assert data['success'] is True
    
    def test_query_endpoint_invalid(self):
        """Test query endpoint with invalid request"""
        response = self.client.post(
            "/query",
            json={"query": ""}  # Empty query
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.slow
    def test_stocks_endpoint(self):
        """Test get stock data endpoint"""
        response = self.client.get("/stocks/AAPL")
        
        assert response.status_code == 200
        data = response.json()
        assert 'ticker' in data
        assert data['ticker'] == 'AAPL'
        assert 'data' in data
    
    @pytest.mark.slow
    def test_compare_stocks_endpoint(self):
        """Test compare stocks endpoint"""
        response = self.client.post(
            "/compare-stocks",
            json=["AAPL", "MSFT"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'tickers' in data
        assert 'comparison' in data
        assert data['success'] is True
    
    def test_compare_stocks_too_few(self):
        """Test compare stocks with insufficient tickers"""
        response = self.client.post(
            "/compare-stocks",
            json=["AAPL"]
        )
        
        assert response.status_code == 400
    
    def test_compare_stocks_too_many(self):
        """Test compare stocks with too many tickers"""
        response = self.client.post(
            "/compare-stocks",
            json=["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA"]
        )
        
        assert response.status_code == 400
    
    @pytest.mark.slow
    def test_chart_endpoint(self):
        """Test chart generation endpoint"""
        response = self.client.get("/chart/AAPL?period=1mo")
        
        # Should return image or error
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            assert response.headers['content-type'] == 'image/png'
    
    def test_clear_cache_endpoint(self):
        """Test cache clear endpoint"""
        response = self.client.post("/clear-cache")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.get("/health")
        
        # Check CORS headers
        assert 'access-control-allow-origin' in response.headers
    
    def test_docs_endpoint(self):
        """Test OpenAPI docs endpoint"""
        response = self.client.get("/docs")
        
        assert response.status_code == 200
    
    def test_openapi_json(self):
        """Test OpenAPI JSON schema"""
        response = self.client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert 'openapi' in data
        assert 'info' in data
        assert 'paths' in data
