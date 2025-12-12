from ddgs import DDGS
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from cache.cache_manager import cache_manager
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class WebSearchTools:
    """Web search tools using DuckDuckGo"""
    
    def __init__(self):
        self.ddgs = DDGS()
        self.max_results = 5
    
    def search_web(self, query: str, region: str = "wt-wt") -> List[Dict[str, Any]]:
        """Search the web for information"""
        cache_key = cache_manager._generate_key("web_search", query)
        
        # Check cache
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            results = list(self.ddgs.text(
                query,
                region=region,
                max_results=self.max_results,
                timelimit="none"  # Past week
            ))
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("body", ""),
                    "link": result.get("href", ""),
                    "source": self._extract_source(result.get("href", "")),
                    "timestamp": datetime.now().isoformat()
                })
            
            # Cache for 5 minutes (news changes fast)
            cache_manager.set(cache_key, formatted_results, ttl=300)
            return formatted_results
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return [{"error": str(e), "query": query}]
    
    def search_news(self, query: str, region: str = "wt-wt") -> List[Dict[str, Any]]:
        """Search for news articles"""
        cache_key = cache_manager._generate_key("news_search", query)
        
        # Check cache
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            results = list(self.ddgs.news(
                query,
                region=region,
                max_results=self.max_results,
                timelimit="d"  # Past day
            ))
            
            formatted_news = []
            for result in results:
                formatted_news.append({
                    "title": result.get("title", ""),
                    "summary": result.get("body", ""),
                    "link": result.get("url", ""),
                    "source": result.get("source", ""),
                    "date": result.get("date", ""),
                    "image": result.get("image", ""),
                    "timestamp": datetime.now().isoformat()
                })
            
            # Cache for 10 minutes (news changes fast)
            cache_manager.set(cache_key, formatted_news, ttl=600)
            return formatted_news
            
        except Exception as e:
            logger.error(f"News search error: {e}")
            return [{"error": str(e), "query": query}]
    
    def _extract_source(self, url: str) -> str:
        """Extract source domain from URL"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # Remove www. prefix
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return "Unknown"
    
    def search_financial_news(self, company: str) -> List[Dict[str, Any]]:
        """Search for financial news about a specific company"""
        query = f"{company} stock news earnings financial results"
        return self.search_news(query)
    
    def search_market_analysis(self, topic: str) -> List[Dict[str, Any]]:
        """Search for market analysis on a specific topic"""
        query = f"{topic} market analysis outlook forecast"
        return self.search_web(query)

# Create a global instance
web_search_tools = WebSearchTools()