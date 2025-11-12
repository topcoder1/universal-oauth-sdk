"""
Integration tests for OAuth flow
"""
import pytest
from fastapi.testclient import TestClient
from test_server_v2 import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Health endpoint should return 200"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["database"] == "connected"


class TestOAuthEndpoints:
    """Test OAuth authorization and token endpoints"""
    
    def test_get_authorization_url_google(self):
        """Should generate Google OAuth URL"""
        response = client.post(
            "/api/v1/oauth/authorize",
            json={
                "provider": "google",
                "redirect_uri": "http://localhost:3000/oauth/callback",
                "state": "test-state-123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert "https://accounts.google.com" in data["authorization_url"]
        assert "test-state-123" in data["authorization_url"]
    
    def test_get_authorization_url_github(self):
        """Should generate GitHub OAuth URL"""
        response = client.post(
            "/api/v1/oauth/authorize",
            json={
                "provider": "github",
                "redirect_uri": "http://localhost:3000/oauth/callback",
                "state": "test-state-456"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert "https://github.com" in data["authorization_url"]
        assert "test-state-456" in data["authorization_url"]
    
    def test_invalid_provider(self):
        """Should reject invalid provider"""
        response = client.post(
            "/api/v1/oauth/authorize",
            json={
                "provider": "invalid-provider",
                "redirect_uri": "http://localhost:3000/oauth/callback",
                "state": "test-state"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_token_exchange_invalid_code(self):
        """Should reject invalid authorization code"""
        response = client.post(
            "/api/v1/oauth/token",
            json={
                "provider": "google",
                "code": "invalid-code-12345",
                "redirect_uri": "http://localhost:3000/oauth/callback"
            }
        )
        # Should return 400 with error from Google
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data


class TestTokenManagement:
    """Test token listing and management"""
    
    def test_list_tokens(self):
        """Should list all tokens"""
        response = client.get("/api/v1/tokens")
        assert response.status_code == 200
        data = response.json()
        assert "tokens" in data
        assert "total" in data
        assert isinstance(data["tokens"], list)
        assert data["total"] == len(data["tokens"])
    
    def test_delete_nonexistent_token(self):
        """Should return 404 for nonexistent token"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/api/v1/tokens/{fake_uuid}")
        assert response.status_code == 404
    
    def test_refresh_nonexistent_token(self):
        """Should return 404 when refreshing nonexistent token"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.post(f"/api/v1/tokens/{fake_uuid}/refresh")
        assert response.status_code == 404


class TestProviders:
    """Test provider listing"""
    
    def test_list_providers(self):
        """Should list available OAuth providers"""
        response = client.get("/api/v1/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        providers = data["providers"]
        assert len(providers) > 0
        
        # Check provider structure
        for provider in providers:
            assert "id" in provider
            assert "name" in provider
            assert "auth_url" in provider


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
