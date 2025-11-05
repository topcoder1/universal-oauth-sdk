"""Webhook model"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Webhook(Base):
    """Webhook model for event notifications"""
    
    __tablename__ = "webhooks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    # Webhook configuration
    url = Column(String(500), nullable=False)
    events = Column(ARRAY(String), default=["token.refreshed", "token.expired"])
    secret = Column(String(255))  # For signature verification
    enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tenant = relationship("Tenant", backref="webhooks")
    
    def __repr__(self):
        return f"<Webhook {self.url}>"
