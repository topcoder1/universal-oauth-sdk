"""Check what constraints exist on tokens table"""
from sqlalchemy import text
from app.database import engine

def check_constraints():
    print("🔍 Checking constraints on tokens table...\n")
    
    with engine.connect() as conn:
        # Check indexes
        result = conn.execute(text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'tokens'
            ORDER BY indexname;
        """))
        
        print("Indexes on tokens table:")
        for row in result:
            print(f"  - {row[0]}")
            print(f"    {row[1]}")
            print()

if __name__ == "__main__":
    check_constraints()
