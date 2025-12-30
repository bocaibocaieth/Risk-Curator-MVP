"""Application middleware."""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.exceptions import AppException, AuthenticationError

logger = logging.getLogger(__name__)


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Optional API key authentication middleware."""

    # Paths that don't require authentication
    EXEMPT_PATHS = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip authentication if no API key is configured
        if not settings.api_key:
            return await call_next(request)

        # Skip exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Skip if path starts with /docs or /redoc
        if request.url.path.startswith(("/docs", "/redoc", "/openapi")):
            return await call_next(request)

        # Check API key
        api_key = request.headers.get(settings.api_key_header)
        if not api_key or api_key != settings.api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "AUTHENTICATION_ERROR",
                    "message": "Invalid or missing API key",
                },
            )

        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Generate request ID
        request_id = request.headers.get("X-Request-ID", str(time.time_ns()))

        # Log request
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
            },
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log response
        log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            log_level,
            f"Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Global exception handler middleware."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except AppException as e:
            logger.warning(
                f"Application error: {e.message}",
                extra={
                    "error_code": e.error_code,
                    "status_code": e.status_code,
                    "details": e.details,
                },
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": e.error_code,
                    "message": e.message,
                    "details": e.details if settings.debug else {},
                },
            )
        except Exception as e:
            logger.exception(f"Unhandled exception: {e}")

            # In production, don't expose internal error details
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
                        "message": str(e),
                    },
                )
