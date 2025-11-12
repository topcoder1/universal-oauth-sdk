"""Create default tenant for testing"""
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.tenant import Tenant

# Create tables
Base.metadata.create_all(bind=engine)

def create_default_tenant():
    """Create a default tenant for testing"""
    db = SessionLocal()
    
    try:
        # Check if default tenant exists
        default_tenant_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
        existing = db.query(Tenant).filter(Tenant.id == default_tenant_id).first()
        
        if existing:
            print(f"✅ Default tenant already exists: {existing.name}")
            return existing
        
        # Create default tenant
        tenant = Tenant(
            id=default_tenant_id,
            name="Default Tenant",
            email="admin@example.com",
            subscription_status="active",
            plan="starter",
            created_at=datetime.utcnow()
        )
        
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        
        print(f"✅ Created default tenant: {tenant.name} (ID: {tenant.id})")
        return tenant
        
    except Exception as e:
        print(f"❌ Error creating default tenant: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Creating default tenant...")
    create_default_tenant()
    print("✅ Done!")
