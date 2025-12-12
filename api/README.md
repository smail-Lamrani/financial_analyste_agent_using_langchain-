# API Usage Guide

## Quick Start

### 1. Start the Server

```bash
# Development mode (auto-reload)
uvicorn api.server:app --reload

# Production mode
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

### 2. View Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Available Endpoints

### 📊 Query Endpoint (Main)

**POST /query**

Process natural language financial questions.

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current stock price of NVIDIA?"
  }'
```

**Response:**
```json
{
  "response": "## 📈 Stock Data for NVDA\n- Current Price: $180.93 USD\n- Volume: 181,596,600\n...",
  "success": true,
  "response_time": 2.34
}
```

### 📈 Stock Data Endpoint

**GET /stocks/{ticker}**

Get detailed stock data for a specific ticker.

```bash
curl "http://localhost:8000/stocks/AAPL"
```

**Response:**
```json
{
  "ticker": "AAPL",
  "data": "## 📈 Stock Data for AAPL\n- Current Price: $278.03 USD\n...",
  "success": true,
  "response_time": 1.23,
  "timestamp": 1702389421.5
}
```

### 🏥 Health Check

**GET /health**

Check service health.

```bash
curl "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "service": "financial_assistant",
  "version": "2.0.0",
  "timestamp": 1702389421.5
}
```

### 🔄 Clear Cache

**POST /clear-cache**

Clear the application cache.

```bash
curl -X POST "http://localhost:8000/clear-cache"
```

### 📊 Service Status

**GET /status**

Get detailed service status.

```bash
curl "http://localhost:8000/status"
```

---

## Python Examples

### Using `requests` library

```python
import requests

# Query endpoint
response = requests.post(
    "http://localhost:8000/query",
    json={"query": "NVIDIA stock price and news"}
)

data = response.json()
print(data['response'])
print(f"Took {data['response_time']:.2f}s")
```

### Using `httpx` (async)

```python
import httpx
import asyncio

async def query_api():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/query",
            json={"query": "Tesla fundamentals"}
        )
        return response.json()

result = asyncio.run(query_api())
print(result['response'])
```

---

## Example Queries

### Stock Prices
```json
{"query": "What is the current price of Apple stock?"}
{"query": "NVDA stock price"}
{"query": "Prix de l'action Microsoft"}
```

### Financial Analysis
```json
{"query": "Analyze Tesla fundamentals"}
{"query": "Analyst recommendations for NVIDIA"}
{"query": "Donne-moi une analyse complète de AAPL"}
```

### News
```json
{"query": "Latest news about Amazon"}
{"query": "What's happening with AMD stock today?"}
{"query": "Actualités récentes sur Apple"}
```

---

## Testing

Run the test suite:

```bash
# Make sure server is running first
uvicorn api.server:app --reload

# In another terminal
python api/test_api.py
```

Or use pytest (if configured):

```bash
pytest api/test_api.py -v
```

---

## Docker Deployment

### Build image

```bash
docker build -t financial-api .
```

### Run container

```bash
docker run -d \
  -p 8000:8000 \
  -e HUGGINGFACEHUB_API_TOKEN=your_token \
  --name financial-api \
  financial-api
```

### With docker-compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HUGGINGFACEHUB_API_TOKEN=${HUGGINGFACEHUB_API_TOKEN}
    depends_on:
      - redis
```

---

## Error Handling

All endpoints return proper HTTP status codes:

- `200`: Success
- `422`: Validation error (invalid request)
- `500`: Server error

Example error response:

```json
{
  "detail": "Query processing failed: connection timeout"
}
```

---

## Rate Limiting (Future)

Currently no rate limiting. For production, consider:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/query")
@limiter.limit("10/minute")
async def process_query(request: QueryRequest):
    ...
```

---

## CORS Configuration

CORS is enabled for all origins (`*`). For production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```
