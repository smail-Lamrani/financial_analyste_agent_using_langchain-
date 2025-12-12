"""
Multi-Agent Orchestrator - Tool-First with Strict LLM Synthesis

This module orchestrates financial and web search agents, combining
real API data with optional LLM synthesis for formatting.

Architecture:
    Query → Analyze → Fetch Real Data (Tool-First) → Optional LLM Synthesis
    
Key Features:
    - Tool-First: APIs called BEFORE LLM (prevents hallucinations)
    - Dual-source: yfinance (financial) + DuckDuckGo (news)
    - Smart routing: Detects financial vs general queries
    - ThreadPoolExecutor: Fixes StopIteration issues
    - Clean fallback: Returns raw data if synthesis fails

Example:
    >>> orchestrator = MultiAgentOrchestrator()
    >>> response = await orchestrator.query("NVIDIA stock price and news")
    >>> # Returns: Real yfinance data + DuckDuckGo news, optionally formatted

Fixed Issues:
    - StopIteration error → ThreadPoolExecutor
    - Hallucinations → Tool-First architecture
    - Empty news → Filtered in SimpleFinancialAgent
"""
from typing import Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from agents.simple_financial_agent import SimpleFinancialAgent
from tools.web_search_tools import web_search_tools
from cache.cache_manager import cache_manager
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Thread pool for LLM calls to avoid StopIteration issues
_executor = ThreadPoolExecutor(max_workers=2)


class MultiAgentOrchestrator:
    """
    Orchestrator that routes queries to appropriate agents and synthesizes responses.
    
    This class implements a hybrid architecture:
    1. **Tool-First Data Fetching**: Calls real APIs (yfinance, DuckDuckGo) first
    2. **Optional LLM Synthesis**: Uses Mixtral-8x7B for formatting (with fallback)
    
    The orchestrator analyzes queries to determine which data sources to use:
    - Financial keywords → SimpleFinancialAgent (yfinance)
    - News keywords → DuckDuckGo web search
    - Both → Fetch both + synthesize
    
    Attributes:
        financial_agent (SimpleFinancialAgent): Tool-First financial data agent
        synthesis_llm (ChatHuggingFace): LLM for optional synthesis
    
    Example:
        >>> orchestrator = MultiAgentOrchestrator()
        >>> 
        >>> # Financial query
        >>> result = await orchestrator.query("NVIDIA stock price")
        >>> # → Returns yfinance data only
        >>> 
        >>> # News query
        >>> result = await orchestrator.query("Latest Tesla news")
        >>> # → Returns DuckDuckGo search only
        >>> 
        >>> # Combined
        >>> result = await orchestrator.query("Apple stock analysis")
        >>> # → Returns yfinance + DuckDuckGo + synthesis
    """
    
    def __init__(self):
        """Initialize the orchestrator with agents and LLM.
        
        Creates:
            - SimpleFinancialAgent for Tool-First data fetching
            - Mixtral-8x7B LLM for optional synthesis
            - ThreadPoolExecutor for async LLM calls
        """
        self.financial_agent = SimpleFinancialAgent()
        
        # Use a better model for synthesis - Mixtral is more instruction-following
        synthesis_endpoint = HuggingFaceEndpoint(
            repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",  # Better at following instructions
            task="text-generation",
            max_new_tokens=800,
            do_sample=False,  # Deterministic - no creativity
            temperature=0.0,
            repetition_penalty=1.1,
            huggingfacehub_api_token=settings.HUGGINGFACEHUB_API_TOKEN
        )
        self.synthesis_llm = ChatHuggingFace(llm=synthesis_endpoint)
        
        logger.info("✅ Initialized MultiAgentOrchestrator (Tool-First + Mixtral Synthesis)")
    
    def _analyze_query(self, query: str) -> Dict[str, bool]:
        """Analyze query to determine which data sources are needed.
        
        Args:
            query: User's natural language query
        
        Returns:
            Dict with keys:
                - needs_financial (bool): True if financial data needed
                - needs_news (bool): True if web search needed
        
        Examples:
            >>> orchestrator._analyze_query("NVIDIA stock price")
            {'needs_financial': True, 'needs_news': False}
            
            >>> orchestrator._analyze_query("Latest Tesla news")
            {'needs_financial': True, 'needs_news': True}
        """
        query_lower = query.lower()
        
        financial_keywords = [
            "stock", "price", "share", "market", "ticker", "symbol",
            "earnings", "revenue", "profit", "dividend", "pe ratio",
            "analyst", "recommendation", "target", "fundamental",
            "action", "bourse", "cours", "résultats", "analyse"
        ]
        
        company_keywords = [
            "nvidia", "nvda", "tesla", "tsla", "apple", "aapl",
            "microsoft", "msft", "amazon", "amzn", "google", "googl",
            "meta", "facebook", "netflix", "nflx", "amd", "intel", "intc"
        ]
        
        news_keywords = [
            "news", "latest", "recent", "today", "breaking", "update",
            "actualité", "dernières", "récentes", "contexte", "marché"
        ]
        
        has_financial = any(k in query_lower for k in financial_keywords)
        has_company = any(k in query_lower for k in company_keywords)
        has_news = any(k in query_lower for k in news_keywords)
        
        return {
            "needs_financial": has_financial or has_company,
            "needs_news": has_news,
        }
    
    async def query(self, query: str) -> str:
        """Process user query using Tool-First + optional synthesis.
        
        Workflow:
            1. Analyze query to determine data sources
            2. Fetch REAL data from APIs (yfinance, DuckDuckGo)
            3. Optionally synthesize with LLM (if both sources)
            4. Cache and return result
        
        Args:
            query: User's natural language question
        
        Returns:
            Formatted response with real data. Either:
            - Raw financial data (if only yfinance)
            - Raw web search (if only DuckDuckGo)
            - Synthesized response (if both sources + LLM succeeds)
            - Clean fallback (if synthesis fails)
        
        Raises:
            No exceptions raised - errors logged and returned as string
        
        Examples:
            >>> result = await orchestrator.query("What is NVIDIA price?")
            >>> # Returns real yfinance data
            
            >>> result = await orchestrator.query("Latest Apple news")
            >>> # Returns DuckDuckGo search results
        """
        
        # Check cache
        cache_key = cache_manager._generate_key("orchestrator", query)
        cached = cache_manager.get(cache_key)
        if cached:
            logger.info("Using cached response")
            return cached
        
        analysis = self._analyze_query(query)
        
        try:
            financial_data = ""
            web_data = ""
            
            # STEP 1: Fetch REAL data
            if analysis["needs_financial"]:
                logger.info("📊 Fetching REAL financial data...")
                financial_data = await self.financial_agent.query(query)
            
            if analysis["needs_news"] or not analysis["needs_financial"]:
                logger.info("🔍 Fetching REAL web search data...")
                web_data = self._fetch_web_data(query)
            
            # STEP 2: Synthesis with strict prompt
            if financial_data and web_data:
                response = await self._strict_synthesis(query, financial_data, web_data)
            elif financial_data:
                # Just reformat the financial data
                response = await self._reformat_data(query, financial_data, "financial")
            elif web_data:
                response = await self._reformat_data(query, web_data, "web")
            else:
                response = "Could not find relevant information."
            
            # Cache response
            cache_manager.set(cache_key, response, ttl=settings.CACHE_TTL)
            return response
            
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return f"Error: {str(e)}"
    
    def _fetch_web_data(self, query: str) -> str:
        """Fetch web search data"""
        try:
            search_query = self._simplify_query(query)
            results = web_search_tools.search_web(search_query)
            
            if not results or (len(results) == 1 and "error" in results[0]):
                return ""
            
            parts = []
            for i, result in enumerate(results[:5], 1):
                parts.append(f"{i}. {result.get('title', 'No title')}")
                parts.append(f"   {result.get('snippet', '')}")
                parts.append(f"   Source: {result.get('source', 'Unknown')}")
            
            return "\n".join(parts)
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return ""
    
    def _simplify_query(self, query: str) -> str:
        """Simplify query for better search"""
        query_lower = query.lower()
        
        companies = {
            "aapl": "AAPL Apple stock news 2024",
            "apple": "AAPL Apple stock news 2024",
            "nvda": "NVDA NVIDIA stock news 2024",
            "nvidia": "NVDA NVIDIA stock news 2024",
            "tsla": "TSLA Tesla stock news 2024",
            "tesla": "TSLA Tesla stock news 2024",
            "msft": "MSFT Microsoft stock news 2024",
            "googl": "GOOGL Google stock news 2024",
            "amzn": "AMZN Amazon stock news 2024",
            "meta": "META stock news 2024",
            "amd": "AMD stock news 2024",
            "intel": "INTC Intel stock news 2024",
        }
        
        for keyword, search_term in companies.items():
            if keyword in query_lower:
                return search_term
        
        return query
    
    async def _strict_synthesis(self, query: str, financial_data: str, web_data: str) -> str:
        """
        Ultra-strict synthesis prompt with explicit rules and examples.
        """
        
        # Detect language
        is_french = any(w in query.lower() for w in ["analyse", "action", "bourse", "cours", "résultats", "marché", "donnez", "donne"])
        lang = "French" if is_french else "English"
        
        prompt = f"""[INST] You are a financial data formatter. Your ONLY job is to reorganize the data below.

## ABSOLUTE RULES - VIOLATION = FAILURE

1. **COPY-PASTE ONLY**: Every number in your response MUST appear exactly in the SOURCE DATA below
2. **NO INVENTION**: Do NOT create any numbers, percentages, prices, or dates
3. **NO EXTERNAL KNOWLEDGE**: Ignore everything you know about stocks. Use ONLY the data below.
4. **CITE SOURCES**: Every data point must mention its source (yfinance or DuckDuckGo)

## FORBIDDEN (examples of what NOT to do):
❌ "The stock is expected to reach $500" (if 500 is not in the data)
❌ "Revenue grew 45% in Q3" (if 45% and Q3 are not in the data)
❌ "According to Bloomberg..." (if Bloomberg is not mentioned in sources)
❌ Adding any analysis, predictions, or opinions

## REQUIRED OUTPUT FORMAT:

### Résumé (if {lang}=French) / Summary (if {lang}=English)
- List 3-5 key facts using ONLY numbers from the data

### Données Financières / Financial Data
- Copy the key metrics from yfinance data below

### Actualités / News
- Summarize headlines from web search below (cite source)

### Sources
- yfinance API (real-time data)
- DuckDuckGo Search

---

## SOURCE DATA (use ONLY this):

### From yfinance API:
{financial_data}

### From DuckDuckGo Search:
{web_data}

---

Now write the formatted response in {lang}. Remember: COPY numbers, don't invent them. [/INST]"""

        try:
            # Use executor to avoid StopIteration issues with asyncio.to_thread
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(_executor, self.synthesis_llm.invoke, prompt)
            return response.content
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            # Fallback: return clean formatted raw data
            return self._format_fallback(financial_data, web_data)
    
    async def _reformat_data(self, query: str, data: str, data_type: str) -> str:
        """Reformat a single data source"""
        
        is_french = any(w in query.lower() for w in ["analyse", "action", "bourse", "cours", "donne"])
        lang = "French" if is_french else "English"
        
        source = "yfinance API" if data_type == "financial" else "DuckDuckGo"
        
        prompt = f"""[INST] Reformat this {data_type} data in {lang}. 

RULES:
- COPY all numbers exactly as they appear
- Do NOT add any new data
- Do NOT make predictions

DATA:
{data}

Write a clean, formatted version in {lang}. End with: "Source: {source}" [/INST]"""

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(_executor, self.synthesis_llm.invoke, prompt)
            return response.content
        except Exception as e:
            logger.error(f"Reformat error: {e}")
            return data
    
    def _format_fallback(self, financial_data: str, web_data: str) -> str:
        """Clean fallback format when synthesis fails"""
        parts = []
        
        if financial_data:
            parts.append("## 📊 Données Financières (yfinance API)")
            parts.append(financial_data)
        
        if web_data:
            parts.append("\n## 📰 Actualités (DuckDuckGo)")
            parts.append(web_data)
        
        parts.append("\n---")
        parts.append("*Sources: yfinance API (données en temps réel), DuckDuckGo (actualités)*")
        
        return "\n".join(parts)
    
    def clear_memory(self):
        """Clear cache"""
        cache_manager.clear()
        logger.info("Cache cleared")
