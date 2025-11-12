"""Vault API with OAuth endpoints for webapp integration"""
import os
import uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Vault API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (will be replaced with PostgreSQL)
tokens_db = {}
connections_db = {}

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

# Models
class OAuthAuthorizeRequest(BaseModel):
    provider: str
    redirect_uri: str
    state: Optional[str] = None
    scopes: Optional[list[str]] = None

class OAuthTokenRequest(BaseModel):
    provider: str
    code: str
    redirect_uri: str

class TokenResponse(BaseModel):
    id: str
    provider: str
    status: str
    created_at: str
    updated_at: str

# Root endpoint
@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Vault API - OAuth Token Management",
        "version": "1.0.0"
    }

# Health check
@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

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

# OAuth token exchange
@app.post("/api/v1/oauth/token")
async def oauth_token_exchange(
    request: OAuthTokenRequest,
    authorization: Optional[str] = Header(None)
):
    """Exchange authorization code for access token"""
    provider = request.provider.lower()
    
    if provider not in OAUTH_CONFIGS:
        raise HTTPException(status_code=400, detail=f"Provider {provider} not supported")
    
    config = OAUTH_CONFIGS[provider]
    
    # Exchange code for token (simplified - in production, call provider's token endpoint)
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
            
            # Store token in database
            token_id = str(uuid.uuid4())
            connection_data = {
                "id": token_id,
                "provider": provider,
                "access_token": token_response.get("access_token"),
                "refresh_token": token_response.get("refresh_token"),
                "expires_at": None,  # Calculate from expires_in
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            tokens_db[token_id] = connection_data
            
            return {
                "id": token_id,
                "provider": provider,
                "status": "active",
                "created_at": connection_data["created_at"]
            }
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Failed to exchange token: {str(e)}")

# List tokens/connections
@app.get("/api/v1/tokens")
async def list_tokens(authorization: Optional[str] = Header(None)):
    """List all stored tokens"""
    tokens = []
    for token_id, token_data in tokens_db.items():
        tokens.append({
            "id": token_data["id"],
            "provider": token_data["provider"],
            "status": token_data["status"],
            "created_at": token_data["created_at"],
            "updated_at": token_data["updated_at"],
        })
    
    return {"tokens": tokens, "total": len(tokens)}

# Delete token
@app.delete("/api/v1/tokens/{token_id}")
async def delete_token(token_id: str, authorization: Optional[str] = Header(None)):
    """Delete a token"""
    if token_id not in tokens_db:
        raise HTTPException(status_code=404, detail="Token not found")
    
    del tokens_db[token_id]
    return {"message": "Token deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Vault API on http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000)
