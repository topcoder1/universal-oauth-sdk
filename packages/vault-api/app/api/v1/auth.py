"""Authentication endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import uuid

from app.database import get_db
from app.models.tenant import Tenant
from app.core.security import create_api_key_for_tenant

router = APIRouter()


class TenantCreate(BaseModel):
    """Schema for creating a tenant"""
    email: EmailStr
    name: str = None


class TenantResponse(BaseModel):
    """Schema for tenant response"""
    id: uuid.UUID
    email: str
    name: str = None
    
    class Config:
        from_attributes = True


class APIKeyResponse(BaseModel):
    """Schema for API key response"""
    api_key: str
    key_prefix: str
    tenant: TenantResponse


@router.post("/register", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def register_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new tenant and generate an API key.
    
    This is a simplified registration for MVP.
    In production, add email verification, etc.
    """
    # Check if tenant already exists
    existing = db.query(Tenant).filter(Tenant.email == tenant_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create tenant
    tenant = Tenant(
        id=uuid.uuid4(),
        email=tenant_data.email,
        name=tenant_data.name,
    )
    
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    # Create API key
    api_key, key_record = create_api_key_for_tenant(db, tenant, name="Default Key")
    
    return APIKeyResponse(
        api_key=api_key,
        key_prefix=key_record.key_prefix,
        tenant=TenantResponse.from_orm(tenant)
    )
