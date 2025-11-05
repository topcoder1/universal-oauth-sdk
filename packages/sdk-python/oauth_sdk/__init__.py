"""Universal OAuth SDK - Python

Multi-language OAuth SDK for connecting to 50+ OAuth providers.
"""

__version__ = "0.1.0"

from oauth_sdk.client import OAuthClient
from oauth_sdk.store import MemoryStore, SQLiteStore, TokenStore
from oauth_sdk.models import Token, OAuthConfig, Provider
from oauth_sdk.provider_registry import ProviderRegistry
from oauth_sdk.exceptions import (
    OAuthError,
    TokenExpiredError,
    InvalidTokenError,
    ProviderNotFoundError,
    AuthorizationError,
    TokenExchangeError,
    TokenRefreshError,
    StorageError,
)

__all__ = [
    "OAuthClient",
    "MemoryStore",
    "SQLiteStore",
    "TokenStore",
    "Token",
    "OAuthConfig",
    "Provider",
    "ProviderRegistry",
    "OAuthError",
    "TokenExpiredError",
    "InvalidTokenError",
    "ProviderNotFoundError",
    "AuthorizationError",
    "TokenExchangeError",
    "TokenRefreshError",
    "StorageError",
]
