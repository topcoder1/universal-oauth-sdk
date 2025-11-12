"""Drop the old constraint that's causing issues"""
from sqlalchemy import text
from app.database import engine

def drop_old_constraint():
    print("🔧 Dropping old constraint...\n")
    
    with engine.connect() as conn:
        trans = conn.begin()
        
        try:
            # Drop the old constraint with the correct name
            print("Dropping ix_tokens_tenant_key...")
            conn.execute(text("""
                DROP INDEX IF EXISTS ix_tokens_tenant_key;
            """))
            
            trans.commit()
            print("✅ Old constraint dropped successfully!")
            print("   Now only the correct constraint remains:")
            print("   UNIQUE (tenant_id, key, provider)")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error: {e}")
            raise

if __name__ == "__main__":
    drop_old_constraint()
