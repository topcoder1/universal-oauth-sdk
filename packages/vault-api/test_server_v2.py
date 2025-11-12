"""Vault API with OAuth endpoints - PostgreSQL + Encryption Version"""
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Import database and models
from app.database import get_db, engine, Base
from app.models.token import Token
from app.core.encryption import get_encryption

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vault API v2", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth provider configurations
OAUTH_CONFIGS = {
    "google": {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "scopes": ["openid", "email", "profile"],
    },
    "github": {
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "scopes": ["user:email", "read:user"],
    },
    "slack": {
        "auth_url": "https://slack.com/oauth/v2/authorize",
        "token_url": "https://slack.com/api/oauth.v2.access",
        "client_id": os.getenv("SLACK_CLIENT_ID"),
        "client_secret": os.getenv("SLACK_CLIENT_SECRET"),
        "scopes": ["users:read", "users:read.email"],
    }
}

# Pydantic models
class OAuthAuthorizeRequest(BaseModel):
    provider: str
    redirect_uri: str
    state: Optional[str] = None
    scopes: Optional[list] = None

class OAuthTokenRequest(BaseModel):
    provider: str
    code: str
    redirect_uri: str

# Root endpoint
@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Vault API v2 - OAuth Token Management with PostgreSQL",
        "version": "2.0.0",
        "features": ["PostgreSQL Storage", "Token Encryption", "Persistent Tokens"]
    }

# Health check
@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status
    }

# List providers
@app.get("/api/v1/providers")
def get_providers():
    providers = []
    for provider_id, config in OAUTH_CONFIGS.items():
        if config["client_id"] and config["client_id"] != f"your-{provider_id}-client-id":
            providers.append({
                "id": provider_id,
                "name": provider_id.capitalize(),
                "category": "productivity" if provider_id == "google" else "development" if provider_id == "github" else "communication",
                "configured": True
            })
    return {"providers": providers}

# OAuth authorize - initiate OAuth flow
@app.post("/api/v1/oauth/authorize")
async def oauth_authorize(
    request: OAuthAuthorizeRequest,
    authorization: Optional[str] = Header(None)
):
    """Initiate OAuth flow and return authorization URL"""
    provider = request.provider.lower()
    
    if provider not in OAUTH_CONFIGS:
        raise HTTPException(status_code=400, detail=f"Provider {provider} not supported")
    
    config = OAUTH_CONFIGS[provider]
    if not config["client_id"]:
        raise HTTPException(status_code=400, detail=f"Provider {provider} not configured")
    
    # Build authorization URL
    scopes = request.scopes or config["scopes"]
    scope_str = " ".join(scopes)
    
    state = request.state or str(uuid.uuid4())
    
    params = {
        "client_id": config["client_id"],
        "redirect_uri": request.redirect_uri,
        "response_type": "code",
        "scope": scope_str,
        "state": state,
    }
    
    # Add provider-specific params
    if provider == "google":
        params["access_type"] = "offline"
        params["prompt"] = "consent"
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    auth_url = f"{config['auth_url']}?{query_string}"
    
    return {
        "auth_url": auth_url,
        "authorization_url": auth_url,  # SDK expects this
        "state": state
    }

# OAuth token exchange with PostgreSQL storage
@app.post("/api/v1/oauth/token")
async def oauth_token_exchange(
    request: OAuthTokenRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Exchange authorization code for access token and store in PostgreSQL"""
    provider = request.provider.lower()
    
    if provider not in OAUTH_CONFIGS:
        raise HTTPException(status_code=400, detail=f"Provider {provider} not supported")
    
    config = OAUTH_CONFIGS[provider]
    
    # Exchange code for token
    import httpx
    
    token_data = {
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "code": request.code,
        "redirect_uri": request.redirect_uri,
        "grant_type": "authorization_code"
    }
    
    headers = {"Accept": "application/json"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config["token_url"],
                data=token_data,
                headers=headers
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Token exchange failed: {response.text}"
                )
            
            token_response = response.json()
            
            # Get encryption instance
            encryption = get_encryption()
            
            # Encrypt tokens
            access_token_encrypted = encryption.encrypt(token_response.get("access_token"))
            refresh_token_encrypted = encryption.encrypt(token_response.get("refresh_token")) if token_response.get("refresh_token") else None
            
            # Calculate expiration
            expires_in = token_response.get("expires_in")
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in) if expires_in else None
            
            # Extract user ID from authorization header (or use a default tenant)
            # For now, we'll use a default tenant ID
            tenant_id = uuid.UUID("00000000-0000-0000-0000-000000000001")  # Default tenant
            user_key = authorization.replace("Bearer ", "") if authorization else "anonymous"
            
            # Delete any existing token for this tenant/key/provider (upsert behavior)
            existing_token = db.query(Token).filter(
                Token.tenant_id == tenant_id,
                Token.key == user_key,
                Token.provider == provider
            ).first()
            
            if existing_token:
                print(f"🔄 Updating existing {provider} token")
                db.delete(existing_token)
                db.flush()  # Flush the delete before inserting
            
            # Store token in PostgreSQL
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
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(token)
            db.commit()
            db.refresh(token)
            
            return {
                "id": str(token.id),
                "provider": provider,
                "status": "active",
                "created_at": token.created_at.isoformat(),
                "expires_at": token.expires_at.isoformat() if token.expires_at else None
            }
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Failed to exchange token: {str(e)}")

# List tokens/connections from PostgreSQL
@app.get("/api/v1/tokens")
async def list_tokens(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """List all stored tokens from PostgreSQL"""
    try:
        # For now, return all tokens (in production, filter by user)
        tokens = db.query(Token).all()
        
        token_list = []
        for token in tokens:
            # Handle timezone-aware datetime comparison
            is_expired = False
            if token.expires_at:
                # Make utcnow timezone-aware to match token.expires_at
                from datetime import timezone
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
        
        return {"tokens": token_list, "total": len(token_list)}
    except Exception as e:
        print(f"❌ Error in list_tokens: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to list tokens: {str(e)}")

# Refresh token endpoint
@app.post("/api/v1/tokens/{token_id}/refresh")
async def refresh_token(
    token_id: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Refresh an expired or expiring token"""
    try:
        token_uuid = uuid.UUID(token_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token ID")
    
    # Get the token from database
    token = db.query(Token).filter(Token.id == token_uuid).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    # Check if provider supports refresh
    if not token.refresh_token_encrypted:
        raise HTTPException(status_code=400, detail=f"{token.provider} does not support token refresh")
    
    # Get provider config
    config = OAUTH_CONFIGS.get(token.provider)
    if not config:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {token.provider}")
    
    # Decrypt refresh token
    encryption = get_encryption()
    refresh_token = encryption.decrypt(token.refresh_token_encrypted)
    
    # Prepare refresh request
    refresh_data = {
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config["token_url"],
                data=refresh_data,
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Token refresh failed: {response.text}"
                )
            
            token_response = response.json()
            
            # Encrypt new tokens
            new_access_token = encryption.encrypt(token_response.get("access_token"))
            new_refresh_token = encryption.encrypt(token_response.get("refresh_token")) if token_response.get("refresh_token") else token.refresh_token_encrypted
            
            # Calculate new expiration
            expires_in = token_response.get("expires_in")
            from datetime import timezone
            new_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in) if expires_in else None
            
            # Update token in database
            token.access_token_encrypted = new_access_token
            token.refresh_token_encrypted = new_refresh_token
            token.expires_at = new_expires_at
            token.last_refreshed_at = datetime.now(timezone.utc)
            token.updated_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(token)
            
            print(f"🔄 Token refreshed successfully for {token.provider}")
            
            return {
                "id": str(token.id),
                "provider": token.provider,
                "status": "active",
                "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                "last_refreshed_at": token.last_refreshed_at.isoformat() if token.last_refreshed_at else None
            }
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh token: {str(e)}")

# Delete token from PostgreSQL
@app.delete("/api/v1/tokens/{token_id}")
async def delete_token(
    token_id: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Delete token from PostgreSQL"""
    try:
        token_uuid = uuid.UUID(token_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token ID format")
    
    token = db.query(Token).filter(Token.id == token_uuid).first()
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    db.delete(token)
    db.commit()
    
    return {"success": True, "message": "Token deleted"}

# Get decrypted token (for testing)
@app.get("/api/v1/tokens/{token_id}/decrypt")
async def get_decrypted_token(
    token_id: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get decrypted token (for testing only - remove in production)"""
    try:
        token_uuid = uuid.UUID(token_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token ID format")
    
    token = db.query(Token).filter(Token.id == token_uuid).first()
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    # Decrypt tokens
    encryption = get_encryption()
    
    return {
        "id": str(token.id),
        "provider": token.provider,
        "access_token": encryption.decrypt(token.access_token_encrypted),
        "refresh_token": encryption.decrypt(token.refresh_token_encrypted) if token.refresh_token_encrypted else None,
        "token_type": token.token_type,
        "expires_at": token.expires_at.isoformat() if token.expires_at else None
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Vault API v2 (PostgreSQL + Encryption) on http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("💾 Database: PostgreSQL with encrypted token storage")
    uvicorn.run(app, host="0.0.0.0", port=8000)
