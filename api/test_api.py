"""
API Test Suite - Manual Testing Script

This script demonstrates how to use the Financial AI Assistant API.
Run the server first: uvicorn api.server:app --reload

Then run this script: python api/test_api.py
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test /health endpoint"""
    print_section("Test 1: Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health check passed")

def test_root():
    """Test root endpoint"""
    print_section("Test 2: Root Endpoint")
    
    response = requests.get(BASE_URL)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✅ Root endpoint passed")

def test_query_nvidia():
    """Test /query endpoint with NVIDIA"""
    print_section("Test 3: Query NVIDIA Stock Price")
    
    payload = {
        "query": "What is the current stock price of NVIDIA?",
        "user_id": "test_user"
    }
    
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/query",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    elapsed = time.time() - start
    
    print(f"Status Code: {response.status_code}")
    print(f"Request took: {elapsed:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response Time: {data['response_time']:.2f}s")
        print(f"Success: {data['success']}")
        print(f"\nResponse Preview (first 500 chars):")
        print(data['response'][:500] + "...")
        print("✅ NVIDIA query passed")
    else:
        print(f"❌ Error: {response.text}")

def test_stock_endpoint():
    """Test /stocks/{ticker} endpoint"""
    print_section("Test 4: Direct Stock Data (AAPL)")
    
    response = requests.get(f"{BASE_URL}/stocks/AAPL")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Ticker: {data['ticker']}")
        print(f"Response Time: {data['response_time']:.2f}s")
        print(f"\nData Preview (first 400 chars):")
        print(data['data'][:400] + "...")
        print("✅ Stock endpoint passed")
    else:
        print(f"❌ Error: {response.text}")

def test_french_query():
    """Test French language query"""
    print_section("Test 5: French Language Query")
    
    payload = {
        "query": "Donne-moi une analyse de Tesla"
    }
    
    response = requests.post(
        f"{BASE_URL}/query",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Response Time: {data['response_time']:.2f}s")
        print(f"\nResponse Preview:")
        print(data['response'][:300] + "...")
        print("✅ French query passed")
    else:
        print(f"❌ Error: {response.text}")

def test_clear_cache():
    """Test /clear-cache endpoint"""
    print_section("Test 6: Clear Cache")
    
    response = requests.post(f"{BASE_URL}/clear-cache")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Cache cleared successfully")
    else:
        print(f"❌ Error: {response.text}")

def test_status():
    """Test /status endpoint"""
    print_section("Test 7: Service Status")
    
    response = requests.get(f"{BASE_URL}/status")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Status endpoint passed")
    else:
        print(f"❌ Error: {response.text}")

def run_all_tests():
    """Run all tests"""
    print("\n🚀 Starting API Test Suite")
    print(f"Target: {BASE_URL}")
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("NVIDIA Query", test_query_nvidia),
        ("Stock Endpoint", test_stock_endpoint),
        ("French Query", test_french_query),
        ("Clear Cache", test_clear_cache),
        ("Service Status", test_status),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ Test '{name}' failed: {e}")
            failed += 1
    
    print_section("Test Summary")
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")

if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Make sure the server is running:")
        print("  uvicorn api.server:app --reload")
