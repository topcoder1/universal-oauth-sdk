"""API Key model"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class APIKey(Base):
    """API Key model for authentication"""
    
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    # Key storage (hashed)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    key_prefix = Column(String(20), nullable=False)  # vk_abc123...
    
    # Metadata
    name = Column(String(255))
    last_used_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked_at = Column(DateTime(timezone=True))
    
    # Relationships
    tenant = relationship("Tenant", backref="api_keys")
    
    def __repr__(self):
        return f"<APIKey {self.key_prefix}>"
