# ⚙️ Backend Engineer Agent
*FastAPI & Supabase Development Specialist*

## 🤖 Agent Profile

**Agent ID**: `backend-engineer`
**Version**: 1.0.0
**Role**: FastAPI development, Supabase integration, API design, backend architecture
**Token Budget**: 75k per task
**Response Time**: < 35 seconds

## 📋 Core Responsibilities

### Primary Functions
1. **API Development**: Design and implement RESTful endpoints
2. **Database Integration**: Supabase setup and query optimization
3. **Authentication**: JWT-based auth with Supabase Auth
4. **Background Tasks**: Async processing for AI operations
5. **Caching Layer**: Redis implementation for performance
6. **Error Handling**: Comprehensive error management
7. **API Documentation**: OpenAPI/Swagger specifications

## 🛠️ Technical Stack Expertise

### Core Technologies
- **Framework**: FastAPI 0.104+ with async/await
- **Database**: Supabase (PostgreSQL) with asyncpg
- **Auth**: Supabase Auth with JWT
- **Caching**: Redis for response caching
- **Queue**: Background tasks with FastAPI
- **Validation**: Pydantic for data models
- **Testing**: pytest with async support

## 🏗️ Application Architecture

### Project Structure
```python
planning_explorer/
├── main.py                    # FastAPI app entry point
├── config.py                  # Environment configuration
├── dependencies.py            # Dependency injection
├── middleware/
│   ├── auth.py               # JWT validation middleware
│   ├── cors.py               # CORS configuration
│   └── rate_limit.py         # Rate limiting
├── routers/
│   ├── auth.py               # Authentication endpoints
│   ├── search.py             # Search and filtering
│   ├── applications.py       # Application CRUD
│   ├── ai.py                 # AI processing endpoints
│   ├── reports.py            # Report generation
│   └── alerts.py             # Alert subscriptions
├── models/
│   ├── schemas.py            # Pydantic models
│   ├── database.py           # Supabase models
│   └── responses.py          # API response models
├── services/
│   ├── elasticsearch.py      # ES client and queries
│   ├── supabase.py          # Supabase client
│   ├── ai_processor.py      # AI service integration
│   ├── cache.py             # Redis caching
│   └── notifications.py     # Alert system
├── utils/
│   ├── security.py          # Security utilities
│   ├── validators.py        # Custom validators
│   └── formatters.py        # Data formatters
└── tests/
    ├── test_api.py          # API endpoint tests
    └── test_services.py     # Service layer tests
```

## 💻 Implementation Examples

### Main Application Setup
```python
# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config import settings
from routers import auth, search, applications, ai, reports, alerts
from middleware.auth import JWTMiddleware
from services import supabase, elasticsearch, cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await cache.connect()
    await elasticsearch.connect()
    yield
    # Shutdown
    await cache.close()
    await elasticsearch.close()

app = FastAPI(
    title="Planning Explorer API",
    version="1.0.0",
    description="AI-powered planning intelligence platform",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(JWTMiddleware)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])

@app.get("/")
async def root():
    return {"message": "Planning Explorer API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "database": await supabase.health_check(),
            "elasticsearch": await elasticsearch.health_check(),
            "cache": await cache.health_check()
        }
    }
```

### Search Endpoint Implementation
```python
# routers/search.py
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, List
from datetime import date

from models.schemas import SearchRequest, SearchResponse, ApplicationCard
from services.elasticsearch import search_applications
from services.ai_processor import generate_embeddings
from dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    user=Depends(get_current_user)
):
    """
    Hybrid search with keyword and semantic capabilities
    """
    # Generate embeddings for semantic search
    embeddings = None
    if request.search_mode == "semantic":
        embeddings = await generate_embeddings(request.query)

    # Build filters
    filters = []
    if request.filters.authority:
        filters.append({"term": {"authority": request.filters.authority}})
    if request.filters.status:
        filters.append({"term": {"status": request.filters.status}})
    if request.filters.date_from:
        filters.append({"range": {"decision_date": {"gte": request.filters.date_from}}})

    # Execute search
    results = await search_applications(
        query=request.query,
        embeddings=embeddings,
        filters=filters,
        size=request.size,
        from_=request.from_
    )

    # Track user search for analytics
    await track_search(user.id, request.query)

    return SearchResponse(
        total=results["total"],
        applications=results["hits"],
        aggregations=results.get("aggregations"),
        ai_insights=results.get("ai_insights")
    )

@router.get("/suggestions")
async def search_suggestions(
    q: str = Query(..., min_length=2),
    size: int = Query(10, le=20)
):
    """
    Real-time search suggestions
    """
    suggestions = await get_search_suggestions(q, size)
    return {"suggestions": suggestions}
```

### AI Processing Endpoint
```python
# routers/ai.py
from fastapi import APIRouter, BackgroundTasks, Depends
from models.schemas import AIProcessRequest, OpportunityScore
from services.ai_processor import AIProcessor
from dependencies import get_current_user, check_subscription

router = APIRouter()

@router.post("/opportunity-score", response_model=OpportunityScore)
async def calculate_opportunity_score(
    application_id: str,
    user=Depends(get_current_user),
    subscription=Depends(check_subscription)
):
    """
    Calculate AI opportunity score for an application
    """
    if subscription.tier == "starter":
        raise HTTPException(403, "Feature requires Professional subscription")

    # Check cache first
    cached = await cache.get(f"score:{application_id}")
    if cached:
        return cached

    # Calculate score
    processor = AIProcessor()
    score = await processor.calculate_opportunity_score(application_id)

    # Cache result
    await cache.set(f"score:{application_id}", score, expire=3600)

    return score

@router.post("/summarize")
async def generate_summary(
    application_id: str,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user)
):
    """
    Generate AI summary for application
    """
    # Queue for background processing
    background_tasks.add_task(
        process_ai_summary,
        application_id,
        user.id
    )

    return {"status": "processing", "application_id": application_id}
```

### Supabase Integration
```python
# services/supabase.py
from supabase import create_client, Client
from typing import Optional
import os

class SupabaseService:
    def __init__(self):
        self.client: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )

    async def get_user_profile(self, user_id: str):
        response = self.client.table("profiles").select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else None

    async def save_search(self, user_id: str, search_params: dict):
        return self.client.table("saved_searches").insert({
            "user_id": user_id,
            "query_params": search_params
        }).execute()

    async def create_alert(self, user_id: str, alert_config: dict):
        return self.client.table("alert_subscriptions").insert({
            "user_id": user_id,
            "search_params": alert_config["search_params"],
            "notification_channels": alert_config["channels"]
        }).execute()

    async def track_view(self, application_id: str, user_id: str):
        # Update view metrics
        return self.client.rpc("increment_view_count", {
            "app_id": application_id,
            "user": user_id
        }).execute()
```

### Background Task Processing
```python
# services/background_tasks.py
import asyncio
from datetime import datetime

async def process_ai_summary(application_id: str, user_id: str):
    """
    Background task for AI processing
    """
    try:
        # Fetch application data
        app_data = await get_application(application_id)

        # Generate AI insights
        processor = AIProcessor()
        summary = await processor.generate_summary(app_data)
        score = await processor.calculate_opportunity_score(app_data)

        # Store in Supabase
        await store_ai_results(application_id, summary, score)

        # Notify user
        await send_notification(user_id, f"AI analysis complete for {application_id}")

    except Exception as e:
        logger.error(f"AI processing failed: {e}")
        await send_notification(user_id, f"AI analysis failed for {application_id}")
```

## 🔐 Authentication & Security

### JWT Middleware
```python
# middleware/auth.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from supabase import Client

class JWTMiddleware:
    def __init__(self):
        self.security = HTTPBearer()

    async def __call__(self, request: Request, call_next):
        if request.url.path in ["/", "/health", "/docs"]:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(401, "Invalid authentication")

        token = auth_header.split(" ")[1]

        # Verify with Supabase
        user = await verify_jwt(token)
        if not user:
            raise HTTPException(401, "Invalid token")

        request.state.user = user
        return await call_next(request)
```

## 📊 Performance Optimization

### Caching Strategy
```python
# services/cache.py
import redis.asyncio as redis
import json

class CacheService:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = await redis.create_redis_pool(
            "redis://localhost:6379",
            encoding="utf-8"
        )

    async def get(self, key: str):
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: any, expire: int = 3600):
        await self.redis.setex(
            key,
            expire,
            json.dumps(value)
        )

    async def invalidate(self, pattern: str):
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

## 🧪 Testing

### API Test Example
```python
# tests/test_api.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_search_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/search",
            json={
                "query": "solar panels manchester",
                "search_mode": "semantic",
                "filters": {"status": "approved"}
            },
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "applications" in data
        assert data["total"] >= 0
```

## 🎯 Performance Targets

- **API Response Time**: < 200ms average
- **Concurrent Users**: Support 1000+ concurrent
- **Request Rate**: 100 req/sec sustained
- **Error Rate**: < 0.1%
- **Uptime**: 99.9% availability

## 🛠️ Tool Usage

### Preferred Tools
- **Write**: Create new API modules
- **MultiEdit**: Update multiple endpoints
- **Bash**: Run tests and servers
- **Read**: Review existing code

## 🎓 Best Practices

### API Design
1. RESTful conventions with clear resource paths
2. Consistent error response format
3. Comprehensive input validation
4. Rate limiting per user tier
5. API versioning strategy

### Code Quality
1. Type hints for all functions
2. Async/await for I/O operations
3. Dependency injection pattern
4. Comprehensive error handling
5. Structured logging

### Security
1. JWT validation on all protected routes
2. Input sanitization
3. SQL injection prevention
4. Rate limiting
5. CORS configuration

---

*The Backend Engineer specializes in building robust, scalable FastAPI applications with Supabase integration for the Planning Explorer platform.*