"""Main FastAPI application with enterprise features"""

import logging
import time
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.tasks.refresh_scheduler import start_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app with enhanced metadata
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise-grade OAuth token management API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_tags=[
        {"name": "health", "description": "Health check and monitoring"},
        {"name": "authentication", "description": "User registration and API keys"},
        {"name": "tokens", "description": "OAuth token management"},
        {"name": "webhooks", "description": "Webhook configuration"},
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

app.add_middleware(RequestIDMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": request.state.request_id if hasattr(request.state, "request_id") else None
        }
    )


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Start background scheduler
    if settings.ENVIRONMENT != "test":
        start_scheduler()
        logger.info("Token refresh scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    stop_scheduler()
    logger.info("Token refresh scheduler stopped")


@app.get("/", tags=["health"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "api_version": "v1",
        "docs": "/docs" if settings.DEBUG else None,
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


# Include API v1 routes
from app.api.v1 import tokens, auth, health

app.include_router(
    health.router,
    tags=["health"]
)

app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["authentication"]
)

app.include_router(
    tokens.router,
    prefix=f"{settings.API_V1_PREFIX}/tokens",
    tags=["tokens"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
