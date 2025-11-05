"""Tests for token CRUD endpoints"""

import pytest
from fastapi import status


def test_create_token(client, auth_headers):
    """Test creating a token"""
    response = client.post(
        "/v1/tokens/",
        headers=auth_headers,
        json={
            "key": "user:123",
            "provider": "google",
            "access_token": "ya29.a0...",
            "refresh_token": "1//...",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "openid email profile"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["key"] == "user:123"
    assert data["provider"] == "google"
    assert "id" in data


def test_create_duplicate_token(client, auth_headers):
    """Test creating duplicate token fails"""
    token_data = {
        "key": "user:123",
        "provider": "google",
        "access_token": "token1",
    }
    
    # Create first token
    response1 = client.post("/v1/tokens/", headers=auth_headers, json=token_data)
    assert response1.status_code == status.HTTP_201_CREATED
    
    # Try to create duplicate
    response2 = client.post("/v1/tokens/", headers=auth_headers, json=token_data)
    assert response2.status_code == status.HTTP_409_CONFLICT


def test_get_token(client, auth_headers):
    """Test retrieving a token"""
    # Create token
    create_response = client.post(
        "/v1/tokens/",
        headers=auth_headers,
        json={
            "key": "user:456",
            "provider": "github",
            "access_token": "gho_abc123",
        }
    )
    token_id = create_response.json()["id"]
    
    # Get token
    response = client.get(f"/v1/tokens/{token_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["key"] == "user:456"
    assert data["access_token"] == "gho_abc123"  # Decrypted


def test_get_nonexistent_token(client, auth_headers):
    """Test getting non-existent token returns 404"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/v1/tokens/{fake_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_tokens(client, auth_headers):
    """Test listing tokens"""
    # Create multiple tokens
    for i in range(3):
        client.post(
            "/v1/tokens/",
            headers=auth_headers,
            json={
                "key": f"user:{i}",
                "provider": "google",
                "access_token": f"token{i}",
            }
        )
    
    # List tokens
    response = client.get("/v1/tokens/", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 3
    assert len(data["data"]) == 3


def test_list_tokens_with_filter(client, auth_headers):
    """Test listing tokens with provider filter"""
    # Create tokens with different providers
    client.post("/v1/tokens/", headers=auth_headers, json={
        "key": "user:1", "provider": "google", "access_token": "token1"
    })
    client.post("/v1/tokens/", headers=auth_headers, json={
        "key": "user:2", "provider": "github", "access_token": "token2"
    })
    
    # Filter by provider
    response = client.get("/v1/tokens/?provider=google", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["provider"] == "google"


def test_delete_token(client, auth_headers):
    """Test deleting a token"""
    # Create token
    create_response = client.post(
        "/v1/tokens/",
        headers=auth_headers,
        json={
            "key": "user:789",
            "provider": "google",
            "access_token": "token",
        }
    )
    token_id = create_response.json()["id"]
    
    # Delete token
    response = client.delete(f"/v1/tokens/{token_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify deleted
    get_response = client.get(f"/v1/tokens/{token_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_update_token(client, auth_headers):
    """Test updating a token"""
    # Create token
    create_response = client.post(
        "/v1/tokens/",
        headers=auth_headers,
        json={
            "key": "user:999",
            "provider": "google",
            "access_token": "old_token",
        }
    )
    token_id = create_response.json()["id"]
    
    # Update token
    response = client.put(
        f"/v1/tokens/{token_id}",
        headers=auth_headers,
        json={
            "key": "user:999",
            "provider": "google",
            "access_token": "new_token",
            "refresh_token": "new_refresh",
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    # Verify updated
    get_response = client.get(f"/v1/tokens/{token_id}", headers=auth_headers)
    data = get_response.json()
    assert data["access_token"] == "new_token"
    assert data["refresh_token"] == "new_refresh"


def test_unauthorized_access(client):
    """Test accessing endpoints without authentication"""
    response = client.get("/v1/tokens/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_invalid_api_key(client):
    """Test accessing with invalid API key"""
    headers = {"Authorization": "Bearer invalid_key"}
    response = client.get("/v1/tokens/", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
