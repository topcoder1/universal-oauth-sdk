"""Request validation models using Pydantic"""
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional
from enum import Enum


class OAuthProvider(str, Enum):
    """Supported OAuth providers"""
    GOOGLE = "google"
    GITHUB = "github"
    SLACK = "slack"


class OAuthAuthorizeRequest(BaseModel):
    """Request model for OAuth authorization"""
    provider: OAuthProvider
    redirect_uri: HttpUrl
    state: str = Field(min_length=8, max_length=128, description="CSRF protection state")
    scope: Optional[str] = Field(None, max_length=500, description="OAuth scopes")
    
    @validator('redirect_uri')
    def validate_redirect_uri(cls, v):
        """Validate redirect URI is in whitelist"""
        allowed_uris = [
            "http://localhost:3000/oauth/callback",
            "http://localhost:8000/oauth/callback",
            "https://yourdomain.com/oauth/callback"
        ]
        if str(v) not in allowed_uris:
            raise ValueError(f"Redirect URI not in whitelist: {v}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "provider": "google",
                "redirect_uri": "http://localhost:3000/oauth/callback",
                "state": "random-state-string-12345",
                "scope": "openid email profile"
            }
        }


class TokenExchangeRequest(BaseModel):
    """Request model for token exchange"""
    provider: OAuthProvider
    code: str = Field(min_length=1, max_length=512, description="Authorization code")
    redirect_uri: HttpUrl
    
    @validator('redirect_uri')
    def validate_redirect_uri(cls, v):
        """Validate redirect URI matches authorization"""
        allowed_uris = [
            "http://localhost:3000/oauth/callback",
            "http://localhost:8000/oauth/callback",
            "https://yourdomain.com/oauth/callback"
        ]
        if str(v) not in allowed_uris:
            raise ValueError(f"Redirect URI not in whitelist: {v}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "provider": "google",
                "code": "4/0AY0e-g7...",
                "redirect_uri": "http://localhost:3000/oauth/callback"
            }
        }


class TokenRefreshRequest(BaseModel):
    """Request model for token refresh (optional body)"""
    force: bool = Field(False, description="Force refresh even if not expired")
    
    class Config:
        schema_extra = {
            "example": {
                "force": False
            }
        }


class WebhookRegisterRequest(BaseModel):
    """Request model for webhook registration"""
    url: HttpUrl = Field(description="Webhook endpoint URL")
    events: list[str] = Field(description="Events to subscribe to")
    secret: Optional[str] = Field(None, min_length=16, description="Webhook signature secret")
    
    @validator('events')
    def validate_events(cls, v):
        """Validate event types"""
        allowed_events = [
            "token.created",
            "token.refreshed",
            "token.expired",
            "token.deleted",
            "token.refresh_failed"
        ]
        for event in v:
            if event not in allowed_events:
                raise ValueError(f"Invalid event type: {event}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://yourdomain.com/webhooks/oauth",
                "events": ["token.created", "token.refreshed"],
                "secret": "your-webhook-secret-key"
            }
        }
