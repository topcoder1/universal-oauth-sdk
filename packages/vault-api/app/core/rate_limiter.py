"""Rate limiting for API endpoints"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import redis
from typing import Optional

# Initialize Redis client (optional, falls back to in-memory)
try:
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )
    redis_client.ping()
    print("✅ Redis connected for rate limiting")
    storage_uri = "redis://localhost:6379"
except:
    print("⚠️  Redis not available, using in-memory rate limiting")
    storage_uri = None

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=storage_uri,
    default_limits=["100/minute"]  # Global default
)

# Custom rate limit exceeded handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "error_description": "Too many requests. Please try again later.",
            "retry_after": exc.detail
        },
        headers={
            "Retry-After": str(exc.detail),
            "X-RateLimit-Limit": str(exc.detail),
            "X-RateLimit-Remaining": "0"
        }
    )

# Rate limit configurations for different endpoints
RATE_LIMITS = {
    "oauth_authorize": "10/minute",      # OAuth authorization
    "oauth_token": "5/minute",           # Token exchange
    "token_refresh": "20/hour",          # Token refresh
    "token_list": "30/minute",           # List tokens
    "token_delete": "10/minute",         # Delete tokens
    "health": "60/minute"                # Health check
}

def get_rate_limit(endpoint: str) -> str:
    """Get rate limit for specific endpoint"""
    return RATE_LIMITS.get(endpoint, "30/minute")
