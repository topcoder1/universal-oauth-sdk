"""Tests for data models"""

import pytest
from datetime import datetime, timedelta

from oauth_sdk.models import Token, Provider, OAuthConfig


def test_token_creation():
    """Test token creation"""
    token = Token(
        access_token="test_token",
        token_type="Bearer",
        expires_in=3600,
    )
    
    assert token.access_token == "test_token"
    assert token.token_type == "Bearer"
    assert token.expires_in == 3600


def test_token_is_expired():
    """Test token expiration check"""
    # Not expired
    future_time = int((datetime.now() + timedelta(hours=1)).timestamp())
    token = Token(access_token="test", expires_at=future_time)
    assert not token.is_expired()
    
    # Expired
    past_time = int((datetime.now() - timedelta(hours=1)).timestamp())
    token_expired = Token(access_token="test", expires_at=past_time)
    assert token_expired.is_expired()
    
    # No expiration
    token_no_expiry = Token(access_token="test")
    assert not token_no_expiry.is_expired()


def test_token_to_dict():
    """Test token serialization"""
    token = Token(
        access_token="test_token",
        token_type="Bearer",
        expires_in=3600,
        refresh_token="refresh_token",
    )
    
    data = token.to_dict()
    assert data["access_token"] == "test_token"
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] == 3600
    assert data["refresh_token"] == "refresh_token"


def test_token_from_dict():
    """Test token deserialization"""
    data = {
        "access_token": "test_token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "refresh_token",
    }
    
    token = Token.from_dict(data)
    assert token.access_token == "test_token"
    assert token.token_type == "Bearer"
    assert token.expires_in == 3600
    assert token.refresh_token == "refresh_token"
