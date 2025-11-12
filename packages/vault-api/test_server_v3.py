"""
Enhanced Vault API Test Server v3
With Rate Limiting, Request Validation, and Structured Logging
"""
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta, timezone
import httpx
import uuid

# Database and models
from app.database import SessionLocal, engine, Base
from app.models.token import Token
from app.models.tenant import Tenant
from app.core.encryption import get_encryption
from app.config import settings

# Phase 2: New imports
from app.core.rate_limiter import limiter, rate_limit_exceeded_handler, get_rate_limit
from app.models.requests import (
    OAuthAuthorizeRequest,
    TokenExchangeRequest,
    OAuthProvider
)
from app.core.logging_config import setup_logging, security_logger, get_correlation_id
from slowapi.errors import RateLimitExceeded

# Setup structured logging
logger = setup_logging(log_level="INFO")

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="Universal OAuth Vault API v3",
    description="OAuth token management with rate limiting and structured logging",
    version="3.0.0"
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS
cors_origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth configurations
OAUTH_CONFIGS = {
    "google": {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scope": "openid email profile"
    },
    "github": {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "scope": "read:user user:email"
    },
    "slack": {
        "client_id": settings.SLACK_CLIENT_ID,
        "client_secret": settings.SLACK_CLIENT_SECRET,
        "auth_url": "https://slack.com/oauth/v2/authorize",
        "token_url": "https://slack.com/api/oauth.v2.access",
        "scope": "identity.basic identity.email"
    }
}

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check
@app.get("/health")
@limiter.limit(get_rate_limit("health"))
async def health_check(request: Request, db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "version": "3.0.0"
    }

# List providers
@app.get("/api/v1/providers")
@limiter.limit("60/minute")
async def list_providers(request: Request):
    """List available OAuth providers"""
    providers = []
    for provider_id, config in OAUTH_CONFIGS.items():
        providers.append({
            "id": provider_id,
            "name": provider_id.capitalize(),
            "auth_url": config["auth_url"],
            "scope": config["scope"]
        })
    
    logger.info(f"Listed {len(providers)} providers")
    return {"providers": providers}

# OAuth authorization
@app.post("/api/v1/oauth/authorize")
@limiter.limit(get_rate_limit("oauth_authorize"))
async def oauth_authorize(req: Request, request: OAuthAuthorizeRequest):
    """Generate OAuth authorization URL with request validation"""
    correlation_id = get_correlation_id()
    
    try:
        provider = request.provider.value
        config = OAUTH_CONFIGS.get(provider)
        
        if not config:
            logger.warning(f"Invalid provider requested: {provider}", extra={'correlation_id': correlation_id})
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        # Build authorization URL
        auth_url = (
            f"{config['auth_url']}?"
            f"client_id={config['client_id']}&"
            f"redirect_uri={request.redirect_uri}&"
            f"response_type=code&"
            f"scope={request.scope or config['scope']}&"
            f"state={request.state}"
        )
        
        logger.info(
            f"OAuth authorization URL generated for {provider}",
            extra={
                'correlation_id': correlation_id,
                'provider': provider,
                'redirect_uri': str(request.redirect_uri)
            }
        )
        
        return {"authorization_url": auth_url}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating auth URL: {e}", extra={'correlation_id': correlation_id})
        raise HTTPException(status_code=500, detail=str(e))

# Token exchange
@app.post("/api/v1/oauth/token")
@limiter.limit(get_rate_limit("oauth_token"))
async def oauth_token_exchange(
    req: Request,
    request: TokenExchangeRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Exchange authorization code for access token with validation"""
    correlation_id = get_correlation_id()
    provider = request.provider.value
    
    try:
        config = OAUTH_CONFIGS.get(provider)
        if not config:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        # Exchange code for token
        token_data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": request.code,
            "redirect_uri": str(request.redirect_uri),
            "grant_type": "authorization_code"
        }
        
        headers = {"Accept": "application/json"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config["token_url"],
                data=token_data,
                headers=headers
            )
            
            if response.status_code != 200:
                error_detail = f"Token exchange failed: {response.text}"
                logger.error(error_detail, extra={'correlation_id': correlation_id, 'provider': provider})
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
            
            token_response = response.json()
            
            # Get encryption instance
            encryption = get_encryption()
            
            # Encrypt tokens
            access_token_encrypted = encryption.encrypt(token_response.get("access_token"))
            refresh_token_encrypted = encryption.encrypt(token_response.get("refresh_token")) if token_response.get("refresh_token") else None
            
            # Calculate expiration
            expires_in = token_response.get("expires_in")
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in) if expires_in else None
            
            # Extract user ID from authorization header
            tenant_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
            user_key = authorization.replace("Bearer ", "") if authorization else "anonymous"
            
            # Delete existing token for this provider (upsert)
            existing_token = db.query(Token).filter(
                Token.tenant_id == tenant_id,
                Token.key == user_key,
                Token.provider == provider
            ).first()
            
            if existing_token:
                logger.info(f"Updating existing {provider} token", extra={'correlation_id': correlation_id})
                db.delete(existing_token)
                db.flush()
            
            # Store new token
            token = Token(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                key=user_key,
                provider=provider,
                access_token_encrypted=access_token_encrypted,
                refresh_token_encrypted=refresh_token_encrypted,
                token_type=token_response.get("token_type", "Bearer"),
                expires_at=expires_at,
                scope=token_response.get("scope"),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            db.add(token)
            db.commit()
            db.refresh(token)
            
            # Log security event
            security_logger.log_token_operation("created", str(token.id), user_key, provider)
            
            logger.info(
                f"Token stored successfully for {provider}",
                extra={
                    'correlation_id': correlation_id,
                    'provider': provider,
                    'token_id': str(token.id)
                }
            )
            
            return {
                "id": str(token.id),
                "provider": provider,
                "status": "active",
                "created_at": token.created_at.isoformat(),
                "expires_at": token.expires_at.isoformat() if token.expires_at else None
            }
    
    except httpx.RequestError as e:
        logger.error(f"HTTP request error: {e}", extra={'correlation_id': correlation_id})
        raise HTTPException(status_code=500, detail=f"Failed to exchange token: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", extra={'correlation_id': correlation_id})
        raise HTTPException(status_code=500, detail=str(e))

# List tokens
@app.get("/api/v1/tokens")
@limiter.limit(get_rate_limit("token_list"))
async def list_tokens(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """List all stored tokens"""
    try:
        tokens = db.query(Token).all()
        
        token_list = []
        for token in tokens:
            is_expired = False
            if token.expires_at:
                now_utc = datetime.now(timezone.utc)
                is_expired = token.expires_at < now_utc
            
            token_list.append({
                "id": str(token.id),
                "provider": token.provider,
                "status": "expired" if is_expired else "active",
                "created_at": token.created_at.isoformat() if token.created_at else None,
                "updated_at": token.updated_at.isoformat() if token.updated_at else None,
                "expires_at": token.expires_at.isoformat() if token.expires_at else None
            })
        
        logger.info(f"Listed {len(token_list)} tokens")
        return {"tokens": token_list, "total": len(token_list)}
    
    except Exception as e:
        logger.error(f"Error listing tokens: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list tokens: {str(e)}")

# Refresh token
@app.post("/api/v1/tokens/{token_id}/refresh")
@limiter.limit(get_rate_limit("token_refresh"))
async def refresh_token(
    request: Request,
    token_id: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Refresh an expired or expiring token"""
    correlation_id = get_correlation_id()
    
    try:
        token_uuid = uuid.UUID(token_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token ID")
    
    token = db.query(Token).filter(Token.id == token_uuid).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    if not token.refresh_token_encrypted:
        raise HTTPException(status_code=400, detail=f"{token.provider} does not support token refresh")
    
    config = OAUTH_CONFIGS.get(token.provider)
    if not config:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {token.provider}")
    
    try:
        encryption = get_encryption()
        refresh_token_value = encryption.decrypt(token.refresh_token_encrypted)
        
        refresh_data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "refresh_token": refresh_token_value,
            "grant_type": "refresh_token"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config["token_url"],
                data=refresh_data,
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                error_detail = f"Token refresh failed: {response.text}"
                logger.error(error_detail, extra={'correlation_id': correlation_id})
                raise HTTPException(status_code=response.status_code, detail=error_detail)
            
            token_response = response.json()
            
            # Encrypt new tokens
            new_access_token = encryption.encrypt(token_response.get("access_token"))
            new_refresh_token = encryption.encrypt(token_response.get("refresh_token")) if token_response.get("refresh_token") else token.refresh_token_encrypted
            
            # Calculate new expiration
            expires_in = token_response.get("expires_in")
            new_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in) if expires_in else None
            
            # Update token
            token.access_token_encrypted = new_access_token
            token.refresh_token_encrypted = new_refresh_token
            token.expires_at = new_expires_at
            token.last_refreshed_at = datetime.now(timezone.utc)
            token.updated_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(token)
            
            # Log security event
            security_logger.log_token_operation("refreshed", str(token.id), token.key, token.provider)
            
            logger.info(
                f"Token refreshed successfully for {token.provider}",
                extra={'correlation_id': correlation_id, 'token_id': str(token.id)}
            )
            
            return {
                "id": str(token.id),
                "provider": token.provider,
                "status": "active",
                "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                "last_refreshed_at": token.last_refreshed_at.isoformat() if token.last_refreshed_at else None
            }
    
    except httpx.RequestError as e:
        logger.error(f"HTTP request error during refresh: {e}", extra={'correlation_id': correlation_id})
        raise HTTPException(status_code=500, detail=f"Failed to refresh token: {str(e)}")

# Delete token
@app.delete("/api/v1/tokens/{token_id}")
@limiter.limit(get_rate_limit("token_delete"))
async def delete_token(
    request: Request,
    token_id: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Delete token from database"""
    try:
        token_uuid = uuid.UUID(token_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token ID")
    
    token = db.query(Token).filter(Token.id == token_uuid).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    provider = token.provider
    user_key = token.key
    
    db.delete(token)
    db.commit()
    
    # Log security event
    security_logger.log_token_operation("deleted", token_id, user_key, provider)
    
    logger.info(f"Token {token_id} deleted successfully")
    return {"message": "Token deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Vault API v3 (with Rate Limiting & Structured Logging)")
    print("📊 Features: Rate Limiting, Request Validation, Structured Logging")
    print("🔒 Rate limits active on all endpoints")
    print("📝 JSON structured logging enabled")
    uvicorn.run(app, host="0.0.0.0", port=8000)
