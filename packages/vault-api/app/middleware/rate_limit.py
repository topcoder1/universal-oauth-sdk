"""Rate limiting middleware using Redis"""

import time
from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Redis client
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis not available: {e}. Rate limiting disabled.")
    redis_client = None


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with Redis backend"""
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Skip if Redis not available
        if not redis_client:
            return await call_next(request)
        
        # Get API key from request (if authenticated)
        api_key = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            api_key = auth_header[7:]
        
        # Use IP address if no API key
        identifier = api_key or request.client.host
        
        # Check rate limit
        if not await self._check_rate_limit(identifier):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute.",
                headers={"Retry-After": "60"}
            )
        
        return await call_next(request)
    
    async def _check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limit"""
        try:
            key = f"ratelimit:{identifier}:minute"
            
            # Increment counter
            count = redis_client.incr(key)
            
            # Set expiry on first request
            if count == 1:
                redis_client.expire(key, 60)
            
            # Check if over limit
            return count <= self.requests_per_minute
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Allow request if Redis fails
            return True


def get_rate_limit_info(identifier: str) -> dict:
    """Get current rate limit status for an identifier"""
    if not redis_client:
        return {"available": True, "remaining": None}
    
    try:
        key = f"ratelimit:{identifier}:minute"
        count = redis_client.get(key)
        count = int(count) if count else 0
        
        return {
            "limit": settings.RATE_LIMIT_PER_MINUTE,
            "used": count,
            "remaining": max(0, settings.RATE_LIMIT_PER_MINUTE - count),
            "reset_in": redis_client.ttl(key) if count > 0 else 60
        }
    except Exception as e:
        logger.error(f"Failed to get rate limit info: {e}")
        return {"available": True, "remaining": None}
