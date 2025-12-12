"""
Test script for stock comparison feature
"""
import asyncio
from agents.simple_financial_agent import SimpleFinancialAgent

async def test_comparison():
    print("🧪 Testing Stock Comparison Feature\n")
    
    agent = SimpleFinancialAgent()
    
    # Test 1: Compare GPU companies
    print("=" * 60)
    print("Test 1: Comparing GPU Makers (NVDA vs AMD vs INTC)")
    print("=" * 60)
    
    result = await agent.compare_stocks(["NVDA", "AMD", "INTC"])
    print(result)
    
    print("\n" + "=" * 60)
    print("Test 2: Comparing Tech Giants (AAPL vs MSFT)")
    print("=" * 60)
    
    result2 = await agent.compare_stocks(["AAPL", "MSFT"])
    print(result2)
    
    print("\n✅ Tests completed!")

if __name__ == "__main__":
    asyncio.run(test_comparison())
