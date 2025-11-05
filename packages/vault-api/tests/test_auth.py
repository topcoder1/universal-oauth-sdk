"""Tests for authentication endpoints"""

import pytest
from fastapi import status


def test_register_tenant(client):
    """Test tenant registration"""
    response = client.post(
        "/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "name": "New User"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "api_key" in data
    assert data["api_key"].startswith("vk_live_")
    assert data["tenant"]["email"] == "newuser@example.com"


def test_register_duplicate_email(client, tenant):
    """Test registering with duplicate email fails"""
    response = client.post(
        "/v1/auth/register",
        json={
            "email": tenant.email,
            "name": "Duplicate"
        }
    )
    
    assert response.status_code == status.HTTP_409_CONFLICT


def test_invalid_email(client):
    """Test registration with invalid email"""
    response = client.post(
        "/v1/auth/register",
        json={
            "email": "not-an-email",
            "name": "Test"
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
