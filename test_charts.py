"""
Test script for chart generation functionality
"""
import asyncio
from tools.chart_tools import ChartTools

def test_single_stock_chart():
    """Test generating a single stock chart"""
    print("=" * 60)
    print("Test 1: Creating NVIDIA 6-month price chart")
    print("=" * 60)
    
    charts = ChartTools()
    
    # Generate chart
    path = charts.plot_stock_history("NVDA", period="6mo", show_ma=True, show_volume=True)
    print(f"✅ Chart saved to: {path}")
    
def test_comparison_chart():
    """Test generating comparison chart"""
    print("\n" + "=" * 60)
    print("Test 2: Creating GPU companies comparison")
    print("=" * 60)
    
    charts = ChartTools()
    
    # Generate comparison
    path = charts.plot_comparison_chart(
        ["NVDA", "AMD", "INTC"],
        period="1y",
        normalize=True
    )
    print(f"✅ Comparison chart saved to: {path}")

def test_multiple_charts():
    """Test generating multiple charts"""
    print("\n" + "=" * 60)
    print("Test 3: Creating charts for tech giants")
    print("=" * 60)
    
    charts = ChartTools()
    tickers = ["AAPL", "MSFT", "GOOGL"]
    
    for ticker in tickers:
        path = charts.plot_stock_history(ticker, period="1y", show_ma=True)
        print(f"✅ {ticker}: {path}")

def run_all_tests():
    """Run all chart tests"""
    print("\n🎨 Testing Chart Generation\n")
    
    try:
        test_single_stock_chart()
        test_comparison_chart()
        test_multiple_charts()
        
        print("\n" + "=" * 60)
        print("✅ All chart tests completed successfully!")
        print("=" * 60)
        print("\nGenerated charts are in the 'charts/' directory")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    run_all_tests()
