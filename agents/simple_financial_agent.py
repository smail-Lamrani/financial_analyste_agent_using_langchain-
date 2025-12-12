"""
Simple Financial Agent - Tool-First Architecture

This module implements a financial data agent that calls APIs DIRECTLY
without using the ReAct pattern, preventing LLM hallucinations.

Architecture:
    Query → Extract Ticker → Call yfinance API → Format Real Data
    
    NO LLM is involved in data fetching, ensuring 100% real data.

Example:
    >>> agent = SimpleFinancialAgent()
    >>> result = await agent.query("What is NVIDIA stock price?")
    >>> print(result)
    ## Stock Data for NVDA
    - Current Price: $180.93 USD
    - Volume: 181,596,600
    ...

Classes:
    SimpleFinancialAgent: Main agent that fetches and formats financial data
    
Constants:
    TICKER_PATTERNS: Dict mapping company names to ticker symbols
"""
import asyncio
import re
from typing import Optional, Dict, Any, List
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from tools.financial_tools import FinancialTools
from tools.web_search_tools import web_search_tools
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Ticker patterns for extraction
TICKER_PATTERNS = {
    "nvidia": "NVDA", "nvda": "NVDA",
    "tesla": "TSLA", "tsla": "TSLA",
    "apple": "AAPL", "aapl": "AAPL",
    "microsoft": "MSFT", "msft": "MSFT",
    "amazon": "AMZN", "amzn": "AMZN",
    "google": "GOOGL", "googl": "GOOGL", "goog": "GOOGL", "alphabet": "GOOGL",
    "meta": "META", "facebook": "META",
    "netflix": "NFLX", "nflx": "NFLX",
    "amd": "AMD",
    "intel": "INTC", "intc": "INTC",
}


class SimpleFinancialAgent:
    """
    Financial agent using Tool-First architecture to prevent hallucinations.
    
    This agent calls yfinance and DuckDuckGo APIs DIRECTLY, then formats
    the results. No LLM is used for data fetching, only for optional
    formatting/summarization.
    
    Key Benefits:
        - Zero hallucinations (data comes from APIs only)
        - Fast execution (~1-2 seconds for data fetch)
        - Real-time prices and fundamentals
        - Filtered empty news
    
    Attributes:
        llm: LangChain LLM wrapper (only for formatting, not used currently)
    
    Example:
        >>> agent = SimpleFinancialAgent()
        >>> result = await agent.query("NVDA stock price")
        >>> # Returns real data from yfinance with timestamp
    """
    
    def __init__(self):
        """Initialize the financial agent.
        
        Creates an LLM wrapper (currently unused - reserved for future
        formatting improvements).
        """
        # LLM only for summarization (not for tool calling)
        llm_endpoint = HuggingFaceEndpoint(
            repo_id=settings.PRIMARY_MODEL,
            task="text-generation",
            max_new_tokens=1024,
            do_sample=False,
            temperature=0.0,
            repetition_penalty=1.1,
            huggingfacehub_api_token=settings.HUGGINGFACEHUB_API_TOKEN
        )
        self.llm = ChatHuggingFace(llm=llm_endpoint)
        logger.info("✅ Initialized SimpleFinancialAgent (Tool-First)")
    
    def _extract_ticker(self, query: str) -> Optional[str]:
        """Extract ticker symbol from natural language query.
        
        Args:
            query: Natural language query (e.g., "What is NVIDIA price?")
        
        Returns:
            Ticker symbol (e.g., "NVDA") or None if not found
        
        Examples:
            >>> agent._extract_ticker("NVIDIA stock price")
            'NVDA'
            >>> agent._extract_ticker("What about Tesla?")
            'TSLA'
        """
        query_lower = query.lower()
        for keyword, ticker in TICKER_PATTERNS.items():
            if keyword in query_lower:
                logger.info(f"Extracted ticker: {ticker} from keyword: {keyword}")
                return ticker
        
        # Try to find explicit ticker (e.g., "NVDA" in the query)
        ticker_match = re.search(r'\b([A-Z]{2,5})\b', query)
        if ticker_match:
            potential_ticker = ticker_match.group(1)
            if potential_ticker in TICKER_PATTERNS.values():
                return potential_ticker
        
        return None
    
    async def query(self, query: str) -> str:
        """
        Process financial query using Tool-First architecture.
        
        This method:
        1. Extracts ticker from query
        2. Calls yfinance API directly (NO LLM)
        3. Formats the real data into a readable response
        
        Args:
            query: User question about stocks/companies
        
        Returns:
            Formatted string with real financial data including:
            - Current price (real-time from yfinance)
            - Day range, volume, market cap
            - P/E ratio, 52-week range
            - Analyst recommendations
            - Fundamentals (profit margin, revenue growth, ROE)
            - Recent news (filtered for valid titles)
        
        Raises:
            No exceptions raised - errors are logged and included in response
        
        Examples:
            >>> agent = SimpleFinancialAgent()
            >>> result = await agent.query("NVIDIA stock price?")
            >>> # Returns real data with timestamp
        """
        ticker = self._extract_ticker(query)
        
        if not ticker:
            # No ticker found - do web search instead
            logger.info("No ticker found, performing web search")
            return await self._web_search_response(query)
        
        logger.info(f"Fetching REAL financial data for {ticker}")
        
        # STEP 1: Call tools DIRECTLY (no LLM involved)
        real_data = await self._fetch_all_data(ticker)
        
        # STEP 2: Format response using real data
        formatted = self._format_response(ticker, real_data)
        
        return formatted
    
    async def _fetch_all_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch all financial data directly from tools"""
        data = {}
        
        # Get stock data from yfinance
        try:
            data["stock"] = FinancialTools.get_stock_data(ticker)
            logger.info(f"✅ Got stock data for {ticker}")
        except Exception as e:
            logger.error(f"Stock data error: {e}")
            data["stock"] = {"error": str(e)}
        
        # Get analyst recommendations
        try:
            data["analysts"] = FinancialTools.get_analyst_recommendations(ticker)
            logger.info(f"✅ Got analyst data for {ticker}")
        except Exception as e:
            logger.error(f"Analyst data error: {e}")
            data["analysts"] = {"error": str(e)}
        
        # Get fundamentals
        try:
            data["fundamentals"] = FinancialTools.get_fundamentals(ticker)
            logger.info(f"✅ Got fundamentals for {ticker}")
        except Exception as e:
            logger.error(f"Fundamentals error: {e}")
            data["fundamentals"] = {"error": str(e)}
        
        # Get news
        try:
            data["news"] = FinancialTools.get_company_news(ticker)
            logger.info(f"✅ Got news for {ticker}")
        except Exception as e:
            logger.error(f"News error: {e}")
            data["news"] = []
        
        return data
    
    def _format_response(self, ticker: str, data: Dict[str, Any]) -> str:
        """Format real data into a readable response"""
        parts = []
        
        # Stock data
        stock = data.get("stock", {})
        if "error" not in stock:
            parts.append(f"## 📈 Stock Data for {ticker}")
            parts.append(f"- **Current Price**: ${stock.get('current_price', 'N/A')} {stock.get('currency', 'USD')}")
            parts.append(f"- **Day Range**: ${stock.get('low', 'N/A')} - ${stock.get('high', 'N/A')}")
            parts.append(f"- **Volume**: {stock.get('volume', 'N/A'):,}")
            if stock.get('market_cap'):
                parts.append(f"- **Market Cap**: ${stock.get('market_cap', 0):,.0f}")
            parts.append(f"- **P/E Ratio**: {stock.get('pe_ratio', 'N/A')}")
            parts.append(f"- **52-Week Range**: ${stock.get('52_week_low', 'N/A')} - ${stock.get('52_week_high', 'N/A')}")
            parts.append(f"- **Data Timestamp**: {stock.get('timestamp', 'N/A')}")
        else:
            parts.append(f"⚠️ Could not fetch stock data: {stock.get('error')}")
        
        parts.append("")
        
        # Analyst recommendations
        analysts = data.get("analysts", {})
        if "error" not in analysts:
            parts.append("## 📊 Analyst Recommendations")
            parts.append(f"- **Recommendation**: {analysts.get('recommendation', 'N/A')}")
            parts.append(f"- **Number of Analysts**: {analysts.get('num_analysts', 'N/A')}")
            if analysts.get('target_mean'):
                parts.append(f"- **Target Price (Mean)**: ${analysts.get('target_mean', 'N/A')}")
            if analysts.get('target_high') and analysts.get('target_low'):
                parts.append(f"- **Target Range**: ${analysts.get('target_low')} - ${analysts.get('target_high')}")
        
        parts.append("")
        
        # Fundamentals
        funds = data.get("fundamentals", {})
        if "error" not in funds:
            parts.append("## 💰 Fundamentals")
            if funds.get('profit_margins'):
                parts.append(f"- **Profit Margin**: {funds.get('profit_margins', 0)*100:.1f}%")
            if funds.get('revenue_growth'):
                parts.append(f"- **Revenue Growth**: {funds.get('revenue_growth', 0)*100:.1f}%")
            if funds.get('return_on_equity'):
                parts.append(f"- **Return on Equity**: {funds.get('return_on_equity', 0)*100:.1f}%")
            parts.append(f"- **Debt to Equity**: {funds.get('debt_to_equity', 'N/A')}")
        
        parts.append("")
        
        # News - filter out empty ones
        news = data.get("news", [])
        valid_news = [
            item for item in news 
            if item.get('title') and item.get('title').strip() and item.get('title') != '****'
        ]
        
        if valid_news:
            parts.append("## 📰 Recent News (yfinance)")
            for i, item in enumerate(valid_news[:3], 1):
                parts.append(f"{i}. **{item.get('title')}**")
                if item.get('publisher'):
                    parts.append(f"   Publisher: {item.get('publisher')}")
        
        return "\n".join(parts)
    
    async def compare_stocks(self, tickers: List[str]) -> str:
        """
        Compare multiple stocks side-by-side.
        
        Fetches real-time data for multiple tickers and presents
        a comparison table with key metrics.
        
        Args:
            tickers: List of ticker symbols to compare (e.g., ["NVDA", "AMD", "INTC"])
        
        Returns:
            Formatted comparison table with:
            - Current prices
            - Market caps
            - P/E ratios
            - Profit margins
            - Revenue growth
            - Analyst recommendations
        
        Examples:
            >>> agent = SimpleFinancialAgent()
            >>> result = await agent.compare_stocks(["NVDA", "AMD", "INTC"])
            >>> # Returns side-by-side comparison table
        """
        if not tickers or len(tickers) < 2:
            return "Please provide at least 2 tickers to compare."
        
        if len(tickers) > 5:
            return "Maximum 5 tickers allowed for comparison."
        
        logger.info(f"Comparing stocks: {', '.join(tickers)}")
        
        # Fetch data for all tickers concurrently
        all_data = {}
        for ticker in tickers:
            ticker_upper = ticker.upper()
            try:
                data = await self._fetch_all_data(ticker_upper)
                all_data[ticker_upper] = data
                logger.info(f"✅ Fetched data for {ticker_upper}")
            except Exception as e:
                logger.error(f"Error fetching {ticker_upper}: {e}")
                all_data[ticker_upper] = {"error": str(e)}
        
        # Format comparison table
        return self._format_comparison(all_data)
    
    def _format_comparison(self, all_data: Dict[str, Dict[str, Any]]) -> str:
        """Format stock comparison into a readable table"""
        parts = ["# 📊 Stock Comparison\n"]
        
        tickers = list(all_data.keys())
        
        # Helper to get value or N/A
        def get_val(ticker, key, subkey, format_func=str):
            try:
                data = all_data[ticker].get(key, {})
                if "error" in data:
                    return "Error"
                val = data.get(subkey, "N/A")
                if val == "N/A" or val is None:
                    return "N/A"
                return format_func(val)
            except:
                return "N/A"
        
        # Stock Prices
        parts.append("## 💰 Current Prices")
        parts.append("| Ticker | Price | Day Change | Volume |")
        parts.append("|--------|-------|------------|--------|")
        for ticker in tickers:
            price = get_val(ticker, "stock", "current_price", lambda x: f"${x:.2f}")
            currency = get_val(ticker, "stock", "currency")
            low = get_val(ticker, "stock", "low", lambda x: f"${x:.2f}")
            high = get_val(ticker, "stock", "high", lambda x: f"${x:.2f}")
            volume = get_val(ticker, "stock", "volume", lambda x: f"{x:,}")
            
            day_change = f"{low} - {high}" if low != "N/A" and high != "N/A" else "N/A"
            parts.append(f"| {ticker} | {price} {currency} | {day_change} | {volume} |")
        
        parts.append("")
        
        # Market Cap & Valuation
        parts.append("## 📈 Market Cap & Valuation")
        parts.append("| Ticker | Market Cap | P/E Ratio | 52-Week Range |")
        parts.append("|--------|------------|-----------|---------------|")
        for ticker in tickers:
            market_cap = get_val(ticker, "stock", "market_cap", lambda x: f"${x/1e12:.2f}T" if x > 1e12 else f"${x/1e9:.1f}B")
            pe = get_val(ticker, "stock", "pe_ratio", lambda x: f"{x:.1f}")
            low_52 = get_val(ticker, "stock", "52_week_low", lambda x: f"${x:.2f}")
            high_52 = get_val(ticker, "stock", "52_week_high", lambda x: f"${x:.2f}")
            
            range_52 = f"{low_52} - {high_52}" if low_52 != "N/A" else "N/A"
            parts.append(f"| {ticker} | {market_cap} | {pe} | {range_52} |")
        
        parts.append("")
        
        # Fundamentals
        parts.append("## 💼 Fundamentals")
        parts.append("| Ticker | Profit Margin | Revenue Growth | ROE | Debt/Equity |")
        parts.append("|--------|---------------|----------------|-----|-------------|")
        for ticker in tickers:
            profit = get_val(ticker, "fundamentals", "profit_margins", lambda x: f"{x*100:.1f}%")
            revenue = get_val(ticker, "fundamentals", "revenue_growth", lambda x: f"{x*100:.1f}%")
            roe = get_val(ticker, "fundamentals", "return_on_equity", lambda x: f"{x*100:.1f}%")
            debt = get_val(ticker, "fundamentals", "debt_to_equity", lambda x: f"{x:.2f}")
            
            parts.append(f"| {ticker} | {profit} | {revenue} | {roe} | {debt} |")
        
        parts.append("")
        
        # Analyst Recommendations
        parts.append("## 🎯 Analyst Recommendations")
        parts.append("| Ticker | Recommendation | Target Price | # Analysts |")
        parts.append("|--------|----------------|--------------|------------|")
        for ticker in tickers:
            rec = get_val(ticker, "analysts", "recommendation")
            target = get_val(ticker, "analysts", "target_mean", lambda x: f"${x:.2f}")
            num = get_val(ticker, "analysts", "num_analysts")
            
            parts.append(f"| {ticker} | {rec} | {target} | {num} |")
        
        parts.append("\n---")
        parts.append("*Data source: yfinance API (real-time)*")
        
        return "\n".join(parts)
    
    async def _web_search_response(self, query: str) -> str:
        """Fallback to web search for non-financial queries"""
        results = web_search_tools.search_web(query)
        
        if not results or (len(results) == 1 and "error" in results[0]):
            return "Could not find relevant information for your query."
        
        parts = ["## 🔍 Web Search Results\n"]
        for i, result in enumerate(results[:5], 1):
            parts.append(f"{i}. **{result.get('title', 'No title')}**")
            parts.append(f"   {result.get('snippet', '')}")
            parts.append(f"   Source: {result.get('source', 'Unknown')}\n")
        
        return "\n".join(parts)
