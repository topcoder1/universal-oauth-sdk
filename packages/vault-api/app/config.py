"""Application configuration"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/v1"
    PROJECT_NAME: str = "Vault API"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/vault_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ENCRYPTION_KEY: str = "your-32-byte-encryption-key"  # v1 key
    ENCRYPTION_KEY_V2: str = ""  # v2 key for rotation (optional)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID: str = ""
    
    # Monitoring
    SENTRY_DSN: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
