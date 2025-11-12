"""Fix token table constraint to allow multiple providers per user"""
from sqlalchemy import text
from app.database import engine

def fix_constraint():
    print("🔧 Fixing token table constraint...")
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # Drop the old constraint
            print("1. Dropping old unique constraint on (tenant_id, key)...")
            conn.execute(text("""
                DROP INDEX IF EXISTS idx_tenant_key;
            """))
            
            # Create new constraint with provider
            print("2. Creating new unique constraint on (tenant_id, key, provider)...")
            conn.execute(text("""
                CREATE UNIQUE INDEX idx_tenant_key_provider 
                ON tokens (tenant_id, key, provider);
            """))
            
            trans.commit()
            print("✅ Constraint fixed successfully!")
            print("   Users can now have multiple OAuth providers")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error: {e}")
            raise

if __name__ == "__main__":
    fix_constraint()
