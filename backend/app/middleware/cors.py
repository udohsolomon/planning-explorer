"""
CORS middleware configuration for Planning Explorer API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


def setup_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI application

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        expose_headers=[
            "X-Total-Count",
            "X-Page-Count",
            "X-Current-Page",
            "X-Per-Page",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Limit",
            "X-Response-Time"
        ]
    )