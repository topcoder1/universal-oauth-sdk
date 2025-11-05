"""Token schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class TokenCreate(BaseModel):
    """Schema for creating a token"""
    key: str = Field(..., description="User-defined key (e.g., 'user:123')")
    provider: str = Field(..., description="OAuth provider (e.g., 'google')")
    access_token: str = Field(..., description="OAuth access token")
    refresh_token: Optional[str] = Field(None, description="OAuth refresh token")
    token_type: str = Field("Bearer", description="Token type")
    expires_in: Optional[int] = Field(None, description="Expires in seconds")
    scope: Optional[str] = Field(None, description="OAuth scopes")


class TokenResponse(BaseModel):
    """Schema for token response"""
    id: UUID
    key: str
    provider: str
    token_type: str
    expires_at: Optional[datetime]
    scope: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    last_refreshed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TokenDetail(TokenResponse):
    """Schema for detailed token response (includes decrypted tokens)"""
    access_token: str
    refresh_token: Optional[str]


class TokenList(BaseModel):
    """Schema for token list response"""
    data: list[TokenResponse]
    total: int
    limit: int
    offset: int
