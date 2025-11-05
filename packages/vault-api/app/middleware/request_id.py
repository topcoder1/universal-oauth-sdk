"""Request ID middleware for distributed tracing"""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request for tracing"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Store in request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
