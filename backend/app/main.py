"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db, close_db
from app.api.v1 import router as api_v1_router
from app.exceptions import AppException
from app.middleware import (
    APIKeyAuthMiddleware,
    RequestLoggingMiddleware,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting application in {settings.environment} mode")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down application")
    await close_db()


app = FastAPI(
    title="DeFi Risk Curator",
    description="DeFi风控监控系统 MVP",
    version="0.1.0",
    lifespan=lifespan,
    # Disable docs in production if needed
    docs_url="/docs" if settings.debug or not settings.is_production else None,
    redoc_url="/redoc" if settings.debug or not settings.is_production else None,
)


# Global exception handler for AppException
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details if settings.debug else {},
        },
    )


# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions."""
    logger.exception(f"Unhandled exception: {exc}")

    if settings.is_production:
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": str(exc),
            },
        )


# Add middleware (order matters - last added is first executed)
# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# API key authentication middleware (optional, enabled via API_KEY env var)
app.add_middleware(APIKeyAuthMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_v1_router, prefix=settings.api_prefix)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.environment,
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "DeFi Risk Curator API",
        "docs": "/docs",
        "health": "/health",
    }
