"""Test configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import Tenant, APIKey, Token
from app.core.security import create_api_key_for_tenant
import uuid

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def tenant(db):
    """Create a test tenant"""
    tenant = Tenant(
        id=uuid.uuid4(),
        email="test@example.com",
        name="Test Tenant",
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@pytest.fixture
def api_key(db, tenant):
    """Create an API key for test tenant"""
    full_key, key_record = create_api_key_for_tenant(db, tenant, name="Test Key")
    return full_key


@pytest.fixture
def auth_headers(api_key):
    """Create authorization headers"""
    return {"Authorization": f"Bearer {api_key}"}
