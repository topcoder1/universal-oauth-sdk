"""Data models for OAuth SDK"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class Token:
    """OAuth token with metadata"""

    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    expires_at: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if token is expired"""
        if self.expires_at is None:
            return False
        return datetime.now().timestamp() >= self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary"""
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
            "expires_at": self.expires_at,
            "raw": self.raw,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Token":
        """Create token from dictionary"""
        return cls(
            access_token=data["access_token"],
            token_type=data.get("token_type", "Bearer"),
            expires_in=data.get("expires_in"),
            refresh_token=data.get("refresh_token"),
            scope=data.get("scope"),
            expires_at=data.get("expires_at"),
            raw=data.get("raw", {}),
        )


@dataclass
class Provider:
    """OAuth provider configuration"""

    id: str
    name: str
    auth_url: str
    token_url: str
    scopes: List[str] = field(default_factory=list)
    default_scopes: List[str] = field(default_factory=list)
    pkce: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OAuthConfig:
    """OAuth client configuration"""

    provider: str
    client_id: str
    client_secret: Optional[str] = None
    redirect_uri: str = "http://localhost:3000/callback"
    scopes: Optional[List[str]] = None
    state: Optional[str] = None
    pkce: bool = False
