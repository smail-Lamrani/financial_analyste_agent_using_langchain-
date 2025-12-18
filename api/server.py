"""
Financial AI Assistant - REST API Server

This module provides a FastAPI-based REST API for the Financial Assistant.

Endpoints:
    GET  /health         - Health check
    POST /query          - Process financial query
    GET  /stocks/{ticker} - Get stock data
    POST /clear-cache    - Clear cache
    GET  /docs           - OpenAPI documentation (auto-generated)

Usage:
    # Development server
    uvicorn api.server:app --reload
    
    # Production server
    uvicorn api.server:app --host 0.0.0.0 --port 8000

Example Request:
    curl -X POST "http://localhost:8000/query" \\
         -H "Content-Type: application/json" \\
         -d '{"query": "What is NVIDIA stock price?"}'

Example Response:
    {
      "response": "## Stock Data for NVDA\\n- Current Price: $180.93 USD...",
      "success": true,
      "response_time": 2.45
    }
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
import logging
import time

from agents.orchestrator import MultiAgentOrchestrator
from agents.simple_financial_agent import SimpleFinancialAgent
from tools.chart_tools import ChartTools
from fastapi.responses import FileResponse
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Financial AI Assistant API",
    description="AI-powered financial analysis with real-time data (Tool-First Architecture)",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for web client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
orchestrator = MultiAgentOrchestrator()
financial_agent = SimpleFinancialAgent()
chart_tools = ChartTools()

# ============================================================================
# Pydantic Models
# ============================================================================

class QueryRequest(BaseModel):
    """Request model for /query endpoint"""
    query: str = Field(..., description="Natural language financial question", min_length=3)
    user_id: Optional[str] = Field(None, description="Optional user identifier for tracking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the current stock price of NVIDIA?",
                "user_id": "user123"
            }
        }

class QueryResponse(BaseModel):
    """Response model for /query endpoint"""
    response: str = Field(..., description="AI assistant response with real data")
    success: bool = Field(..., description="Whether query was successful")
    response_time: float = Field(..., description="Query processing time in seconds")
    
class StockRequest(BaseModel):
    """Request model for /stocks endpoint"""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., NVDA, AAPL)", min_length=1, max_length=5)

class HealthResponse(BaseModel):
    """Response model for /health endpoint"""
    status: str
    service: str
    version: str
    timestamp: float

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    error_type: str

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        API welcome message and links
    """
    return {
        "message": "Financial AI Assistant API",
        "version": "2.0.0",
        "architecture": "Tool-First (prevents hallucinations)",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": "financial_assistant",
        "version": "2.0.0",
        "timestamp": time.time()
    }

@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def process_query(request: QueryRequest):
    """
    Process a natural language financial query.
    
    This endpoint uses the MultiAgentOrchestrator which:
    - Analyzes the query to determine data sources
    - Fetches REAL data from yfinance and DuckDuckGo
    - Optionally synthesizes response with LLM
    
    Args:
        request: Query request with natural language question
    
    Returns:
        QueryResponse with AI assistant answer
    
    Raises:
        HTTPException: 500 if query processing fails
    
    Example:
        ```json
        POST /query
        {
          "query": "What is NVIDIA stock price and recent news?"
        }
        ```
    """
    try:
        start_time = time.time()
        
        logger.info(f"Processing query: {request.query[:50]}...")
        response = await orchestrator.query(request.query)
        response_time = time.time() - start_time
        
        logger.info(f"Query completed in {response_time:.2f}s")
        
        return QueryResponse(
            response=response,
            success=True,
            response_time=response_time
        )
        
    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )

@app.get("/stocks/{ticker}", tags=["Stocks"])
async def get_stock_data(ticker: str):
    """
    Get detailed stock data for a specific ticker.
    
    This endpoint directly calls the SimpleFinancialAgent for fast,
    real-time stock data from yfinance.
    
    Args:
        ticker: Stock ticker symbol (e.g., NVDA, AAPL)
    
    Returns:
        Formatted stock data with price, fundamentals, and news
    
    Example:
        ```
        GET /stocks/NVDA
        ```
    """
    try:
        start_time = time.time()
        
        query = f"Get detailed stock data for {ticker}"
        response = await financial_agent.query(query)
        response_time = time.time() - start_time
        
        return {
            "ticker": ticker.upper(),
            "data": response,
            "success": True,
            "response_time": response_time,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Stock data error for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch data for {ticker}: {str(e)}"
        )

@app.post("/compare-stocks", tags=["Stocks"])
async def compare_stocks(tickers: List[str]):
    """
    Compare multiple stocks side-by-side.
    
    Fetches real-time data for 2-5 stocks and generates a
    comparison table with key metrics.
    
    Args:
        tickers: List of 2-5 ticker symbols to compare
    
    Returns:
        Markdown-formatted comparison table with:
        - Current prices and volumes
        - Market caps and P/E ratios
        - Fundamentals (margins, growth, ROE)
        - Analyst recommendations
    
    Example Request:
        ```json
        POST /compare-stocks
        ["NVDA", "AMD", "INTC"]
        ```
    
    Example Response:
        ```json
        {
          "tickers": ["NVDA", "AMD", "INTC"],
          "comparison": "# Stock Comparison\n## Prices\n...",
          "success": true,
          "response_time": 3.45
        }
        ```
    """
    try:
        if not tickers or len(tickers) < 2:
            raise HTTPException(
                status_code=400,
                detail="Please provide at least 2 tickers to compare"
            )
        
        if len(tickers) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 tickers allowed for comparison"
            )
        
        start_time = time.time()
        
        logger.info(f"Comparing stocks: {', '.join(tickers)}")
        comparison = await financial_agent.compare_stocks(tickers)
        response_time = time.time() - start_time
        
        logger.info(f"Comparison completed in {response_time:.2f}s")
        
        return {
            "tickers": [t.upper() for t in tickers],
            "comparison": comparison,
            "success": True,
            "response_time": response_time,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare stocks: {str(e)}"
        )

@app.post("/clear-cache", tags=["Admin"])
async def clear_cache():
    """
    Clear the application cache (Redis + in-memory).
    
    Useful for forcing fresh data retrieval.
    
    Returns:
        Success message
    """
    try:
        orchestrator.clear_memory()
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )

@app.get("/chart/{ticker}", tags=["Charts"])
async def get_stock_chart(
    ticker: str,
    period: str = "1y",
    show_ma: bool = True,
    show_volume: bool = True
):
    """
    Generate and serve a stock price chart.
    
    Creates a historical price chart with optional moving averages
    and volume bars, then serves the PNG image.
    
    Args:
        ticker: Stock ticker symbol (e.g., NVDA, AAPL)
        period: Time period ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y")
        show_ma: Show moving averages (MA50, MA200)
        show_volume: Show volume bars
    
    Returns:
        PNG image file
    
    Example:
        ```
        GET /chart/NVDA?period=6mo&show_ma=true
        ```
    """
    try:
        logger.info(f"Generating chart for {ticker} ({period})")
        
        # Generate chart
        chart_path = chart_tools.plot_stock_history(
            ticker=ticker,
            period=period,
            show_ma=show_ma,
            show_volume=show_volume
        )
        
        # Return image file
        if os.path.exists(chart_path):
            return FileResponse(
                chart_path,
                media_type="image/png",
                filename=os.path.basename(chart_path)
            )
        else:
            raise HTTPException(status_code=404, detail="Chart not found")
            
    except Exception as e:
        logger.error(f"Chart generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate chart: {str(e)}"
        )

@app.post("/chart/compare", tags=["Charts"])
async def get_comparison_chart(tickers: List[str], period: str = "1y", normalize: bool = True):
    """
    Generate and serve a stock comparison chart.
    
    Args:
        tickers: List of 2-5 ticker symbols
        period: Time period
        normalize: Normalize to percentage change
    
    Returns:
        PNG image file
    
    Example:
        ```json
        POST /chart/compare
        {
          "tickers": ["NVDA", "AMD", "INTC"],
          "period": "1y",
          "normalize": true
        }
        ```
    """
    try:
        if not tickers or len(tickers) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 tickers")
        
        if len(tickers) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 tickers")
        
        logger.info(f"Generating comparison chart for {', '.join(tickers)}")
        
        # Generate chart
        chart_path = chart_tools.plot_comparison_chart(
            tickers=tickers,
            period=period,
            normalize=normalize
        )
        
        # Return image
        if os.path.exists(chart_path):
            return FileResponse(
                chart_path,
                media_type="image/png",
                filename=os.path.basename(chart_path)
            )
        else:
            raise HTTPException(status_code=404, detail="Chart not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comparison chart error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate comparison chart: {str(e)}"
        )

@app.get("/status", tags=["Health"])
async def get_status():
    """
    Get detailed service status including agents.
    
    Returns:
        Comprehensive service status
    """
    return {
        "service": "financial_assistant",
        "version": "2.0.0",
        "architecture": "Tool-First",
        "agents": {
            "orchestrator": "active",
            "financial_agent": "active"
        },
        "data_sources": {
            "yfinance": "active",
            "duckduckgo": "active"
        },
        "cache": "redis/in-memory",
        "timestamp": time.time()
    }

# ============================================================================
# Server Startup
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting Financial AI Assistant API...")
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )