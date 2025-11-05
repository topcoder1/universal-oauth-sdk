"""Token model"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Token(Base):
    """OAuth token model with encryption"""
    
    __tablename__ = "tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    # User-defined key (e.g., "user:123")
    key = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)
    
    # Encrypted token data
    access_token_encrypted = Column(Text, nullable=False)
    refresh_token_encrypted = Column(Text)
    
    # Token metadata
    token_type = Column(String(50), default="Bearer")
    expires_at = Column(DateTime(timezone=True))
    scope = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_refreshed_at = Column(DateTime(timezone=True))
    
    # Relationships
    tenant = relationship("Tenant", backref="tokens")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_key', 'tenant_id', 'key', unique=True),
        Index('idx_expires_at', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<Token {self.provider}:{self.key}>"
