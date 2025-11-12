"""Custom error handlers and exceptions"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any


class OAuthError(HTTPException):
    """Base OAuth error"""
    def __init__(self, status_code: int, error: str, error_description: str = None):
        detail = {"error": error}
        if error_description:
            detail["error_description"] = error_description
        super().__init__(status_code=status_code, detail=detail)


class TokenExpiredError(OAuthError):
    """Token has expired"""
    def __init__(self, provider: str):
        super().__init__(
            status_code=401,
            error="token_expired",
            error_description=f"{provider} token has expired. Please refresh or re-authenticate."
        )


class TokenNotFoundError(OAuthError):
    """Token not found"""
    def __init__(self, token_id: str):
        super().__init__(
            status_code=404,
            error="token_not_found",
            error_description=f"Token {token_id} not found."
        )


class InvalidProviderError(OAuthError):
    """Invalid OAuth provider"""
    def __init__(self, provider: str):
        super().__init__(
            status_code=400,
            error="invalid_provider",
            error_description=f"Provider '{provider}' is not supported."
        )


class RefreshNotSupportedError(OAuthError):
    """Provider doesn't support token refresh"""
    def __init__(self, provider: str):
        super().__init__(
            status_code=400,
            error="refresh_not_supported",
            error_description=f"{provider} does not provide refresh tokens."
        )


def create_error_response(
    error: str,
    error_description: str = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """Create standardized error response"""
    response = {"error": error}
    if error_description:
        response["error_description"] = error_description
    return response


async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"error": str(exc.detail)}
    )
