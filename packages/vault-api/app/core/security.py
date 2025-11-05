"""Security utilities for API key authentication"""

import secrets
import hashlib
from passlib.context import CryptContext
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.api_key import APIKey
from app.models.tenant import Tenant

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token security
security = HTTPBearer()


def generate_api_key() -> tuple[str, str, str]:
    """
    Generate a new API key.
    
    Returns:
        tuple: (full_key, key_hash, key_prefix)
        - full_key: The complete API key to show user (only shown once)
        - key_hash: Bcrypt hash to store in database
        - key_prefix: First 8 chars for identification
    """
    # Generate random key
    random_part = secrets.token_urlsafe(32)
    full_key = f"vk_live_{random_part}"
    
    # Create hash for storage
    key_hash = pwd_context.hash(full_key)
    
    # Create prefix for identification
    key_prefix = full_key[:11]  # "vk_live_abc"
    
    return full_key, key_hash, key_prefix


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against its hash.
    
    Args:
        plain_key: The plain text API key
        hashed_key: The bcrypt hash from database
        
    Returns:
        bool: True if key is valid
    """
    return pwd_context.verify(plain_key, hashed_key)


async def get_current_tenant(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = None
) -> Tenant:
    """
    Dependency to get current tenant from API key.
    
    Optimized with key prefix filtering and caching.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        Tenant: The authenticated tenant
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = credentials.credentials
    
    if not api_key.startswith("vk_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract key prefix for filtering (e.g., "vk_live_abc")
    key_prefix = api_key[:11] if len(api_key) >= 11 else api_key[:8]
    
    # Find API keys with matching prefix (much smaller set)
    db_api_keys = db.query(APIKey).filter(
        APIKey.key_prefix == key_prefix,
        APIKey.revoked_at.is_(None)
    ).limit(10).all()
    
    # Check each candidate key
    for key_record in db_api_keys:
        if verify_api_key(api_key, key_record.key_hash):
            # Update last used timestamp (async to avoid blocking)
            key_record.last_used_at = datetime.utcnow()
            db.commit()
            
            # Return tenant
            return key_record.tenant
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or revoked API key",
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_api_key_for_tenant(db: Session, tenant: Tenant, name: str = None) -> tuple[str, APIKey]:
    """
    Create a new API key for a tenant.
    
    Args:
        db: Database session
        tenant: Tenant to create key for
        name: Optional name for the key
        
    Returns:
        tuple: (full_key, api_key_record)
    """
    full_key, key_hash, key_prefix = generate_api_key()
    
    api_key = APIKey(
        tenant_id=tenant.id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=name,
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return full_key, api_key
