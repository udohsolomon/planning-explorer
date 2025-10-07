"""
API v1 router configuration for Planning Explorer
"""
from fastapi import APIRouter

from app.api.endpoints import search, applications, auth, user, ai, personalization, reports, pseo

# Create API v1 router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    search.router,
    tags=["Search"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    applications.router,
    tags=["Planning Applications"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    reports.router,
    tags=["Reports"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    auth.router,
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}}
)

api_router.include_router(
    user.router,
    tags=["User Management"],
    responses={401: {"description": "Unauthorized"}}
)

api_router.include_router(
    ai.router,
    tags=["AI Features"],
    responses={401: {"description": "Unauthorized"}}
)

api_router.include_router(
    personalization.router,
    prefix="/ai/personalization",
    tags=["AI Personalization"],
    responses={401: {"description": "Unauthorized"}}
)

api_router.include_router(
    pseo.router,
    prefix="/pseo",
    tags=["pSEO"],
    responses={404: {"description": "Not found"}}
)