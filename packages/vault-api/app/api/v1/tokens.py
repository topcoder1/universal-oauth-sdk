"""Token CRUD endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.models.tenant import Tenant
from app.models.token import Token
from app.schemas.token import TokenCreate, TokenResponse, TokenDetail, TokenList
from app.core.security import get_current_tenant
from app.core.encryption import get_encryption

router = APIRouter()


@router.post("/", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def create_token(
    token_data: TokenCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Create a new token.
    
    Encrypts and stores the OAuth token securely.
    """
    # Check if token with same key already exists
    existing = db.query(Token).filter(
        Token.tenant_id == tenant.id,
        Token.key == token_data.key
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Token with key '{token_data.key}' already exists"
        )
    
    # Encrypt tokens
    encryption = get_encryption()
    access_token_encrypted = encryption.encrypt(token_data.access_token)
    refresh_token_encrypted = encryption.encrypt(token_data.refresh_token) if token_data.refresh_token else None
    
    # Calculate expiration
    expires_at = None
    if token_data.expires_in:
        expires_at = datetime.utcnow() + timedelta(seconds=token_data.expires_in)
    
    # Create token record
    token = Token(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        key=token_data.key,
        provider=token_data.provider,
        access_token_encrypted=access_token_encrypted,
        refresh_token_encrypted=refresh_token_encrypted,
        token_type=token_data.token_type,
        expires_at=expires_at,
        scope=token_data.scope,
    )
    
    db.add(token)
    db.commit()
    db.refresh(token)
    
    return token


@router.get("/{token_id}", response_model=TokenDetail)
async def get_token(
    token_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Retrieve a token by ID.
    
    Returns decrypted token data.
    """
    token = db.query(Token).filter(
        Token.id == token_id,
        Token.tenant_id == tenant.id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    # Decrypt tokens
    encryption = get_encryption()
    access_token = encryption.decrypt(token.access_token_encrypted)
    refresh_token = encryption.decrypt(token.refresh_token_encrypted) if token.refresh_token_encrypted else None
    
    # Return with decrypted tokens
    return TokenDetail(
        id=token.id,
        key=token.key,
        provider=token.provider,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type=token.token_type,
        expires_at=token.expires_at,
        scope=token.scope,
        created_at=token.created_at,
        updated_at=token.updated_at,
        last_refreshed_at=token.last_refreshed_at,
    )


@router.get("/", response_model=TokenList)
async def list_tokens(
    provider: Optional[str] = Query(None, description="Filter by provider"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    List all tokens for the authenticated tenant.
    
    Supports filtering and pagination.
    """
    query = db.query(Token).filter(Token.tenant_id == tenant.id)
    
    # Apply provider filter
    if provider:
        query = query.filter(Token.provider == provider)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    tokens = query.offset(offset).limit(limit).all()
    
    return TokenList(
        data=[TokenResponse.from_orm(t) for t in tokens],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.delete("/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_token(
    token_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Delete a token.
    
    Permanently removes the token from storage.
    """
    token = db.query(Token).filter(
        Token.id == token_id,
        Token.tenant_id == tenant.id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    db.delete(token)
    db.commit()
    
    return None


@router.put("/{token_id}", response_model=TokenResponse)
async def update_token(
    token_id: uuid.UUID,
    token_data: TokenCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Update a token.
    
    Useful for refreshing tokens or updating metadata.
    """
    token = db.query(Token).filter(
        Token.id == token_id,
        Token.tenant_id == tenant.id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    # Encrypt new tokens
    encryption = get_encryption()
    token.access_token_encrypted = encryption.encrypt(token_data.access_token)
    if token_data.refresh_token:
        token.refresh_token_encrypted = encryption.encrypt(token_data.refresh_token)
    
    # Update metadata
    token.provider = token_data.provider
    token.token_type = token_data.token_type
    token.scope = token_data.scope
    
    # Update expiration
    if token_data.expires_in:
        token.expires_at = datetime.utcnow() + timedelta(seconds=token_data.expires_in)
    
    token.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(token)
    
    return token
