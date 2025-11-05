"""Tenant model"""

from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enum"""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


class Tenant(Base):
    """Tenant model for multi-tenancy"""
    
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    
    # Stripe
    stripe_customer_id = Column(String(255), unique=True)
    subscription_status = Column(
        Enum(SubscriptionStatus),
        default=SubscriptionStatus.TRIALING
    )
    plan = Column(String(50), default="starter")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Tenant {self.email}>"
