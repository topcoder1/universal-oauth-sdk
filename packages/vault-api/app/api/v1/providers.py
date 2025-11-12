"""OAuth Providers API endpoints"""

from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

# OAuth provider configurations
OAUTH_PROVIDERS: List[Dict[str, Any]] = [
    {
        "id": "google",
        "name": "Google",
        "icon": "https://www.google.com/favicon.ico",
        "category": "productivity",
        "description": "Connect your Google account",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": ["openid", "email", "profile"],
        "tags": ["popular", "productivity"]
    },
    {
        "id": "github",
        "name": "GitHub",
        "icon": "https://github.com/favicon.ico",
        "category": "development",
        "description": "Connect your GitHub account",
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "scopes": ["user", "repo"],
        "tags": ["popular", "development"]
    },
    {
        "id": "slack",
        "name": "Slack",
        "icon": "https://slack.com/favicon.ico",
        "category": "communication",
        "description": "Connect your Slack workspace",
        "auth_url": "https://slack.com/oauth/v2/authorize",
        "token_url": "https://slack.com/api/oauth.v2.access",
        "scopes": ["channels:read", "chat:write"],
        "tags": ["popular", "communication"]
    }
]


@router.get("/providers")
async def get_providers(
    category: str = None
):
    """
    Get list of available OAuth providers
    
    This endpoint is public and does not require authentication.
    """
    providers = OAUTH_PROVIDERS
    
    # Filter by category if provided
    if category:
        providers = [p for p in providers if p.get("category") == category]
    
    return {
        "providers": providers,
        "total": len(providers)
    }


@router.get("/providers/{provider_id}")
async def get_provider(provider_id: str):
    """
    Get details for a specific OAuth provider
    
    This endpoint is public and does not require authentication.
    """
    provider = next((p for p in OAUTH_PROVIDERS if p["id"] == provider_id), None)
    
    if not provider:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return provider
