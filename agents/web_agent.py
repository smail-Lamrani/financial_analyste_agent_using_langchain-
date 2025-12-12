from langchain.tools import BaseTool, tool
from langchain_community.tools import DuckDuckGoSearchRun
from agents.base_agent import BaseAgent
from config.settings import settings
from tools.web_search_tools import web_search_tools
import logging

logger = logging.getLogger(__name__)

# Create tool functions with proper decorators
@tool
def search_web_tool(query: str) -> str:
    """Search the web using DuckDuckGo. Use this for general questions about companies, stocks, or current events. Input should be a search query string."""
    try:
        results = web_search_tools.search_web(query)
        if not results or (len(results) == 1 and "error" in results[0]):
            return "No results found or error in search."
        
        formatted = "Web Search Results:\n"
        for i, result in enumerate(results[:3], 1):
            formatted += f"\n{i}. {result.get('title', 'No title')}\n"
            formatted += f"   {result.get('snippet', 'No description')}\n"
            formatted += f"   Source: {result.get('source', 'Unknown')}\n"
        return formatted
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return f"Error performing web search: {str(e)}"

@tool
def search_news_tool(query: str) -> str:
    """Search for recent news articles using DuckDuckGo News. Use this for breaking news or recent developments. Input should be a search query string."""
    try:
        results = web_search_tools.search_news(query)
        if not results or (len(results) == 1 and "error" in results[0]):
            return "No news found or error in search."
        
        formatted = "News Results:\n"
        for i, result in enumerate(results[:3], 1):
            formatted += f"\n{i}. {result.get('title', 'No title')}\n"
            formatted += f"   {result.get('summary', 'No summary')}\n"
            formatted += f"   Source: {result.get('source', 'Unknown')}\n"
        return formatted
    except Exception as e:
        logger.error(f"News search error: {e}")
        return f"Error searching news: {str(e)}"

@tool
def search_financial_news_tool(company: str) -> str:
    """Search for financial news about a specific company. Use this for stock-related news and earnings reports. Input should be a company name or ticker symbol."""
    try:
        results = web_search_tools.search_financial_news(company)
        if not results or (len(results) == 1 and "error" in results[0]):
            return f"No financial news found for {company}."
        
        formatted = f"Financial News for {company}:\n"
        for i, result in enumerate(results[:3], 1):
            formatted += f"\n{i}. {result.get('title', 'No title')}\n"
            formatted += f"   {result.get('summary', 'No summary')}\n"
            formatted += f"   Source: {result.get('source', 'Unknown')}\n"
        return formatted
    except Exception as e:
        logger.error(f"Financial news search error: {e}")
        return f"Error searching financial news: {str(e)}"

class WebSearchAgent(BaseAgent):
    """Web search agent for current information"""
    
    def __init__(self):
        # Create web search tools using the new tool decorator
        tools = [
            search_web_tool,
            search_news_tool,
            search_financial_news_tool
        ]
        
        # Define agent role
        role = (
            "A senior macroeconomic and geopolitical research analyst responsible for "
            "monitoring global financial markets. You identify, summarize, and cite "
            "relevant, reliable information from trusted sources like Reuters, Bloomberg, "
            "Financial Times, and central banks. Always provide sources and links."
        )
        
        super().__init__(
            name="Web Search Agent",
            role=role,
            tools=tools,
            model_name=settings.PRIMARY_MODEL
        )