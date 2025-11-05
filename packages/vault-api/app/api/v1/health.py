"""Enhanced health check endpoints for monitoring"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import redis

from app.database import get_db
from app.config import settings

router = APIRouter()


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check including dependencies.
    
    Returns 200 if healthy, 503 if any dependency is unhealthy.
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }
    
    is_healthy = True
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        is_healthy = False
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database error: {str(e)}"
        }
    
    # Check Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        # Redis is optional, mark as degraded not unhealthy
        health_status["checks"]["redis"] = {
            "status": "degraded",
            "message": f"Redis unavailable: {str(e)}"
        }
        if health_status["status"] == "healthy":
            health_status["status"] = "degraded"
    
    # Overall status
    if not is_healthy:
        health_status["status"] = "unhealthy"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return health_status


@router.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe.
    
    Returns 200 if application is running.
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe(db: Session = Depends(get_db)):
    """
    Kubernetes readiness probe.
    
    Returns 200 if application is ready to serve traffic.
    """
    try:
        # Check if database is accessible
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "reason": str(e)}
        )
