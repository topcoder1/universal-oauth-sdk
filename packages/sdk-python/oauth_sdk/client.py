"""OAuth Client - Main SDK interface

Simplified Python implementation based on Node SDK.
Note: Node SDK uses openid-client library. Python implementation is manual.
"""

from typing import Optional, Dict, Any
from urllib.parse import urlencode, parse_qs, urlparse
import httpx
import secrets
import hashlib
import base64
import time
import webbrowser

from oauth_sdk.models import Token, Provider
from oauth_sdk.store import TokenStore, MemoryStore
from oauth_sdk.provider_registry import ProviderRegistry
from oauth_sdk.callback_server import CallbackServer
from oauth_sdk.exceptions import (
    OAuthError,
    AuthorizationError,
    TokenExchangeError,
    TokenRefreshError,
)


class OAuthClient:
    """OAuth 2.0 client for authorization flows
    
    Simplified implementation for MVP. Supports:
    - Authorization Code flow with PKCE
    - Token exchange
    - Token refresh
    - Automatic token refresh
    """

    def __init__(
        self,
        provider: str,
        client_id: str,
        client_secret: Optional[str] = None,
        redirect_uri: str = "http://localhost:8787/callback",
        store: Optional[TokenStore] = None,
        scopes: Optional[list[str]] = None,
        registry: Optional[ProviderRegistry] = None,
    ):
        """Initialize OAuth client
        
        Args:
            provider: Provider ID (e.g., 'google', 'github')
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: Callback URL
            store: Token storage implementation
            scopes: List of OAuth scopes (overrides provider defaults)
            registry: Provider registry (optional)
        """
        # Validate inputs
        if not client_id or client_id.strip() == "":
            raise ValueError("client_id is required and cannot be empty")
        if not redirect_uri or redirect_uri.strip() == "":
            raise ValueError("redirect_uri is required and cannot be empty")
        
        # Validate redirect_uri format
        try:
            parsed = urlparse(redirect_uri)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid redirectUri: {redirect_uri}")
        except Exception as e:
            raise ValueError(f"Invalid redirectUri: {redirect_uri}") from e
        
        self.provider_id = provider
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.store = store or MemoryStore()
        self.registry = registry or ProviderRegistry()
        self.http_client = httpx.AsyncClient()
        
        # Load provider manifest
        self.manifest: Optional[Provider] = None
        self.scopes = scopes
        
        # PKCE state
        self._code_verifier: Optional[str] = None
        self._state: Optional[str] = None

    async def init(self) -> None:
        """Initialize client and load provider manifest"""
        self.manifest = await self.registry.get_provider(self.provider_id)
        
        # Validate manifest
        if not self.manifest.auth_url:
            raise OAuthError(f"Provider '{self.manifest.name}' missing authorizationEndpoint")
        if not self.manifest.token_url:
            raise OAuthError(f"Provider '{self.manifest.name}' missing tokenEndpoint")
        
        # Use provider default scopes if not specified
        if self.scopes is None:
            self.scopes = self.manifest.default_scopes or []

    def _generate_pkce(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge"""
        # Generate code verifier (43-128 characters)
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        # Generate code challenge (SHA256 hash of verifier)
        challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge

    def _generate_state(self) -> str:
        """Generate random state parameter"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

    async def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate OAuth authorization URL
        
        Args:
            state: Optional state parameter (generated if not provided)
            
        Returns:
            Authorization URL to redirect user to
        """
        if not self.manifest:
            await self.init()
        
        # Generate PKCE parameters
        self._code_verifier, code_challenge = self._generate_pkce()
        self._state = state or self._generate_state()
        
        # Build authorization URL
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes or []),
            "state": self._state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        
        # Add any extra provider-specific parameters
        if self.manifest and self.manifest.metadata.get("extraAuthorizeParams"):
            params.update(self.manifest.metadata["extraAuthorizeParams"])
        
        auth_url = f"{self.manifest.auth_url}?{urlencode(params)}"
        return auth_url

    async def authorize(
        self,
        key: Optional[str] = None,
        open_browser: bool = True,
        timeout: int = 300,
    ) -> Token:
        """Complete OAuth authorization flow
        
        This is the main method for OAuth authorization. It:
        1. Generates authorization URL
        2. Starts local callback server
        3. Opens browser to authorization URL
        4. Waits for callback
        5. Exchanges code for token
        6. Saves token to storage
        
        Args:
            key: Storage key for token (defaults to provider name)
            open_browser: Whether to auto-open browser (default: True)
            timeout: Timeout in seconds (default: 300 = 5 minutes)
            
        Returns:
            Token object with access token
            
        Raises:
            AuthorizationError: If authorization fails
            TimeoutError: If user doesn't complete auth within timeout
        """
        if not self.manifest:
            await self.init()
        
        key = key or self.provider_id
        
        # Generate authorization URL
        auth_url = await self.get_authorization_url()
        
        # Start callback server
        server = CallbackServer(self.redirect_uri, timeout=timeout)
        
        try:
            server.start()
            
            # Open browser
            if open_browser:
                print(f"🌐 Opening browser for authorization...")
                print(f"   If browser doesn't open, visit: {auth_url}")
                webbrowser.open(auth_url)
            else:
                print(f"🔗 Please visit this URL to authorize:")
                print(f"   {auth_url}")
            
            # Wait for callback
            print(f"⏳ Waiting for authorization (timeout: {timeout}s)...")
            code, state = server.wait_for_callback(expected_state=self._state)
            
            print(f"✅ Authorization code received!")
            
            # Exchange code for token
            print(f"🔄 Exchanging code for access token...")
            token = await self.exchange_code(code, state)
            
            # Save token
            await self.store.set(key, token)
            
            print(f"✅ Token saved successfully!")
            print(f"   Access token: {token.access_token[:20]}...")
            if token.expires_at:
                from datetime import datetime
                expires = datetime.fromtimestamp(token.expires_at)
                print(f"   Expires: {expires}")
            
            return token
            
        except TimeoutError as e:
            raise AuthorizationError(f"Authorization timeout: {e}") from e
        except ValueError as e:
            raise AuthorizationError(f"Authorization failed: {e}") from e
        except Exception as e:
            raise AuthorizationError(f"Authorization error: {e}") from e
        finally:
            server.stop()

    async def exchange_code(self, code: str, state: Optional[str] = None) -> Token:
        """Exchange authorization code for access token
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback (for validation)
            
        Returns:
            Token object with access token and metadata
        """
        if not self.manifest:
            await self.init()
        
        # Validate state if provided
        if state and self._state and state != self._state:
            raise AuthorizationError("State mismatch - possible CSRF attack")
        
        # Prepare token request
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
        }
        
        # Add PKCE verifier
        if self._code_verifier:
            data["code_verifier"] = self._code_verifier
        
        # Add client secret if provided
        if self.client_secret:
            data["client_secret"] = self.client_secret
        
        try:
            response = await self.http_client.post(
                self.manifest.token_url,
                data=data,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            token_data = response.json()
        except httpx.HTTPStatusError as e:
            raise TokenExchangeError(f"Token exchange failed: {e.response.text}") from e
        except Exception as e:
            raise TokenExchangeError(f"Token exchange failed: {str(e)}") from e
        
        # Parse token response
        token = Token(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in"),
            refresh_token=token_data.get("refresh_token"),
            scope=token_data.get("scope"),
            raw=token_data,
        )
        
        # Calculate expiration timestamp
        if token.expires_in:
            token.expires_at = int(time.time()) + token.expires_in
        
        return token

    async def refresh_token_obj(self, token: Token) -> Token:
        """Refresh an access token
        
        Args:
            token: Token object with refresh_token
            
        Returns:
            New token object with refreshed access token
        """
        if not token.refresh_token:
            raise TokenRefreshError("No refresh token available")
        
        if not self.manifest:
            await self.init()
        
        # Prepare refresh request
        data = {
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
            "client_id": self.client_id,
        }
        
        if self.client_secret:
            data["client_secret"] = self.client_secret
        
        try:
            response = await self.http_client.post(
                self.manifest.token_url,
                data=data,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            token_data = response.json()
        except httpx.HTTPStatusError as e:
            raise TokenRefreshError(f"Token refresh failed: {e.response.text}") from e
        except Exception as e:
            raise TokenRefreshError(f"Token refresh failed: {str(e)}") from e
        
        # Parse refreshed token
        new_token = Token(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", token.token_type),
            expires_in=token_data.get("expires_in"),
            refresh_token=token_data.get("refresh_token", token.refresh_token),
            scope=token_data.get("scope", token.scope),
            raw=token_data,
        )
        
        # Calculate expiration timestamp
        if new_token.expires_in:
            new_token.expires_at = int(time.time()) + new_token.expires_in
        
        return new_token

    async def get_token(self, key: Optional[str] = None) -> Optional[Token]:
        """Get stored token
        
        Args:
            key: Storage key (defaults to provider name)
            
        Returns:
            Token object or None if not found
        """
        key = key or self.provider_id
        return await self.store.get(key)

    async def save_token(self, token: Token, key: Optional[str] = None) -> None:
        """Save token to storage
        
        Args:
            token: Token object to save
            key: Storage key (defaults to provider name)
        """
        key = key or self.provider_id
        await self.store.set(key, token)

    async def refresh_if_needed(self, key: Optional[str] = None) -> Optional[Token]:
        """Get token and refresh if expired
        
        Args:
            key: Storage key (defaults to provider name)
            
        Returns:
            Fresh token or None if no token stored
        """
        key = key or self.provider_id
        token = await self.store.get(key)
        
        if not token:
            return None
        
        # Check if token is expired (with 60 second buffer)
        if token.expires_at:
            now = int(time.time())
            if token.expires_at - now > 60:
                return token  # Still fresh
        
        # Try to refresh
        if token.refresh_token:
            try:
                new_token = await self.refresh_token_obj(token)
                await self.store.set(key, new_token)
                return new_token
            except TokenRefreshError:
                return token  # Return old token if refresh fails
        
        return token

    async def request(
        self,
        url: str,
        method: str = "GET",
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make authenticated API request
        
        Args:
            url: API endpoint URL
            method: HTTP method
            key: Storage key for token
            **kwargs: Additional arguments for httpx.request
            
        Returns:
            HTTP response object
        """
        # Get fresh token
        token = await self.refresh_if_needed(key)
        if not token:
            raise OAuthError(f"No token available. Call authorize() first.")
        
        # Add authorization header
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"{token.token_type} {token.access_token}"
        headers["Accept"] = "application/json"
        
        # Make request
        try:
            response = await self.http_client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs,
            )
            
            # Handle 401 - try refresh and retry once
            if response.status_code == 401:
                token = await self.refresh_if_needed(key)
                if token:
                    headers["Authorization"] = f"{token.token_type} {token.access_token}"
                    response = await self.http_client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        **kwargs,
                    )
            
            return response
        except Exception as e:
            raise OAuthError(f"Request failed: {str(e)}") from e

    async def close(self) -> None:
        """Close HTTP client"""
        await self.http_client.aclose()

    async def __aenter__(self) -> "OAuthClient":
        """Async context manager entry"""
        await self.init()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        await self.close()
