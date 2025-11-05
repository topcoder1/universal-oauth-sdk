"""OAuth SDK Exceptions"""


class OAuthError(Exception):
    """Base exception for OAuth errors"""

    pass


class TokenExpiredError(OAuthError):
    """Token has expired and needs refresh"""

    pass


class InvalidTokenError(OAuthError):
    """Token is invalid or malformed"""

    pass


class ProviderNotFoundError(OAuthError):
    """OAuth provider not found in registry"""

    pass


class AuthorizationError(OAuthError):
    """Authorization flow failed"""

    pass


class TokenExchangeError(OAuthError):
    """Failed to exchange authorization code for token"""

    pass


class TokenRefreshError(OAuthError):
    """Failed to refresh access token"""

    pass


class StorageError(OAuthError):
    """Token storage operation failed"""

    pass
