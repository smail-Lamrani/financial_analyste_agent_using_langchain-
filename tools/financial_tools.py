import yfinance as yf
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from cache.cache_manager import cache_manager
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class FinancialTools:
    """Clean financial data tools with caching"""
    
    @staticmethod
    def get_stock_data(ticker: str) -> Dict[str, Any]:
        """Get comprehensive stock data"""
        cache_key = cache_manager._generate_key("stock_data", ticker)
        
        # Check cache
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1mo")
            
            if hist.empty:
                raise ValueError(f"No data found for {ticker}")
            
            latest = hist.iloc[-1]
            
            data = {
                "ticker": ticker,
                "current_price": info.get("currentPrice", latest["Close"]),
                "open": float(latest["Open"]),
                "high": float(latest["High"]),
                "low": float(latest["Low"]),
                "close": float(latest["Close"]),
                "volume": int(latest["Volume"]),
                "currency": info.get("currency", "USD"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the result
            cache_manager.set(cache_key, data, ttl=300)  # 5 minutes
            return data
            
        except Exception as e:
            logger.error(f"Stock data error for {ticker}: {e}")
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def get_analyst_recommendations(ticker: str) -> Dict[str, Any]:
        """Get analyst recommendations"""
        cache_key = cache_manager._generate_key("analyst_recs", ticker)
        
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            data = {
                "ticker": ticker,
                "recommendation": info.get("recommendationKey", "N/A"),
                "mean_recommendation": info.get("recommendationMean"),
                "num_analysts": info.get("numberOfAnalystOpinions"),
                "target_mean": info.get("targetMeanPrice"),
                "target_high": info.get("targetHighPrice"),
                "target_low": info.get("targetLowPrice"),
                "timestamp": datetime.now().isoformat()
            }
            
            cache_manager.set(cache_key, data, ttl=3600)  # 1 hour
            return data
            
        except Exception as e:
            logger.error(f"Analyst recommendations error: {e}")
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def get_company_news(ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get latest company news"""
        cache_key = cache_manager._generate_key("company_news", f"{ticker}_{limit}")
        
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            stock = yf.Ticker(ticker)
            news_items = stock.news[:limit] if stock.news else []
            
            formatted_news = []
            for item in news_items:
                formatted_news.append({
                    "title": item.get("title", ""),
                    "publisher": item.get("publisher", ""),
                    "link": item.get("link", ""),
                    "published": item.get("providerPublishTime"),
                    "related_tickers": item.get("relatedTickers", [])
                })
            
            cache_manager.set(cache_key, formatted_news, ttl=300)  # 5 minutes
            return formatted_news
            
        except Exception as e:
            logger.error(f"Company news error: {e}")
            return [{"error": str(e)}]
    
    @staticmethod
    def get_fundamentals(ticker: str) -> Dict[str, Any]:
        """Get company fundamentals"""
        cache_key = cache_manager._generate_key("fundamentals", ticker)
        
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            data = {
                "ticker": ticker,
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "debt_to_equity": info.get("debtToEquity"),
                "return_on_equity": info.get("returnOnEquity"),
                "profit_margins": info.get("profitMargins"),
                "operating_margins": info.get("operatingMargins"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "timestamp": datetime.now().isoformat()
            }
            
            cache_manager.set(cache_key, data, ttl=3600)  # 1 hour
            return data
            
        except Exception as e:
            logger.error(f"Fundamentals error: {e}")
            return {"error": str(e), "ticker": ticker}