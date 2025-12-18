"""
Financial AI Assistant - Main Application Entry Point

This module serves the web frontend and API endpoints in a single application.

Usage:
    uv run app.py
    or
    uvicorn app:app --reload
    
Then open: http://localhost:8000

Endpoints:
    GET  /               - Web frontend (index.html)
    GET  /static/*       - Static files (CSS, JS)
    GET  /api            - API info (moved from /)
    POST /query          - Process financial query (API)
    GET  /docs           - API documentation
    GET  /health         - Health check
    ... (see api.server for full API)
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# Create a new FastAPI app for the combined frontend + API
app = FastAPI(
    title="Financial AI Assistant",
    description="AI-powered financial analysis with web interface and REST API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Import and include API routes
from api.server import (
    health_check, process_query, get_stock_data, 
    compare_stocks, clear_cache, get_stock_chart,
    get_comparison_chart, get_status
)

# Register API endpoints
app.get("/health", tags=["Health"])(health_check)
app.post("/query", tags=["Query"])(process_query)
app.get("/stocks/{ticker}", tags=["Stocks"])(get_stock_data)
app.post("/compare-stocks", tags=["Stocks"])(compare_stocks)
app.post("/clear-cache", tags=["Admin"])(clear_cache)
app.get("/chart/{ticker}", tags=["Charts"])(get_stock_chart)
app.post("/chart/compare", tags=["Charts"])(get_comparison_chart)
app.get("/status", tags=["Health"])(get_status)

# API info endpoint (moved from /)
@app.get("/api", tags=["Info"])
async def api_info():
    """
    API information endpoint.
    
    Returns:
        API details and available endpoints
    """
    return {
        "message": "Financial AI Assistant API",
        "version": "2.0.0",
        "architecture": "Tool-First (prevents hallucinations)",
        "frontend": "/",
        "docs": "/docs",
        "health": "/health"
    }

# Serve frontend at root
@app.get("/", include_in_schema=False)
async def serve_frontend():
    """
    Serve the web chatbot interface.
    
    Returns:
        HTML file with the chat interface
    """
    index_path = os.path.join(static_dir, "index.html")
    return FileResponse(index_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
