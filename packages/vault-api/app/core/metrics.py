"""Prometheus metrics for monitoring"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from fastapi.responses import Response as FastAPIResponse
import time
from typing import Callable

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# OAuth metrics
oauth_requests_total = Counter(
    'oauth_requests_total',
    'Total OAuth authorization requests',
    ['provider']
)

oauth_success_total = Counter(
    'oauth_success_total',
    'Successful OAuth token exchanges',
    ['provider']
)

oauth_failure_total = Counter(
    'oauth_failure_total',
    'Failed OAuth token exchanges',
    ['provider', 'error_type']
)

# Token metrics
token_operations_total = Counter(
    'token_operations_total',
    'Total token operations',
    ['operation', 'provider']
)

token_refresh_total = Counter(
    'token_refresh_total',
    'Total token refresh attempts',
    ['provider', 'status']
)

tokens_stored_total = Gauge(
    'tokens_stored_total',
    'Total number of tokens stored',
    ['provider']
)

tokens_expired_total = Gauge(
    'tokens_expired_total',
    'Total number of expired tokens',
    ['provider']
)

# Rate limiting metrics
rate_limit_exceeded_total = Counter(
    'rate_limit_exceeded_total',
    'Total rate limit exceeded events',
    ['endpoint']
)

# Database metrics
database_connections_active = Gauge(
    'database_connections_active',
    'Active database connections'
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)


async def metrics_middleware(request: Request, call_next: Callable):
    """Middleware to track request metrics"""
    start_time = time.time()
    
    # Get endpoint path
    endpoint = request.url.path
    method = request.method
    
    try:
        # Process request
        response = await call_next(request)
        status = response.status_code
        
        # Record metrics
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        duration = time.time() - start_time
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        return response
    
    except Exception as e:
        # Record error
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=500
        ).inc()
        
        duration = time.time() - start_time
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        raise


def get_metrics_response():
    """Generate Prometheus metrics response"""
    return FastAPIResponse(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


class MetricsCollector:
    """Helper class for collecting metrics"""
    
    @staticmethod
    def record_oauth_request(provider: str):
        """Record OAuth authorization request"""
        oauth_requests_total.labels(provider=provider).inc()
    
    @staticmethod
    def record_oauth_success(provider: str):
        """Record successful OAuth token exchange"""
        oauth_success_total.labels(provider=provider).inc()
        token_operations_total.labels(operation='created', provider=provider).inc()
    
    @staticmethod
    def record_oauth_failure(provider: str, error_type: str):
        """Record failed OAuth token exchange"""
        oauth_failure_total.labels(provider=provider, error_type=error_type).inc()
    
    @staticmethod
    def record_token_refresh(provider: str, success: bool):
        """Record token refresh attempt"""
        status = 'success' if success else 'failure'
        token_refresh_total.labels(provider=provider, status=status).inc()
        if success:
            token_operations_total.labels(operation='refreshed', provider=provider).inc()
    
    @staticmethod
    def record_token_delete(provider: str):
        """Record token deletion"""
        token_operations_total.labels(operation='deleted', provider=provider).inc()
    
    @staticmethod
    def record_rate_limit(endpoint: str):
        """Record rate limit exceeded"""
        rate_limit_exceeded_total.labels(endpoint=endpoint).inc()
    
    @staticmethod
    def update_token_counts(db):
        """Update token count gauges"""
        from app.models.token import Token
        from datetime import datetime, timezone
        
        try:
            # Get all tokens grouped by provider
            tokens = db.query(Token).all()
            
            # Count by provider
            provider_counts = {}
            expired_counts = {}
            
            for token in tokens:
                provider = token.provider
                provider_counts[provider] = provider_counts.get(provider, 0) + 1
                
                # Check if expired
                if token.expires_at:
                    now_utc = datetime.now(timezone.utc)
                    if token.expires_at < now_utc:
                        expired_counts[provider] = expired_counts.get(provider, 0) + 1
            
            # Update gauges
            for provider, count in provider_counts.items():
                tokens_stored_total.labels(provider=provider).set(count)
            
            for provider, count in expired_counts.items():
                tokens_expired_total.labels(provider=provider).set(count)
        
        except Exception as e:
            print(f"Error updating token counts: {e}")


# Create global collector instance
metrics_collector = MetricsCollector()
