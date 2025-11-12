"""Clear all tokens from the database"""
from app.database import SessionLocal
from app.models.token import Token

db = SessionLocal()

try:
    # Delete all tokens
    count = db.query(Token).delete()
    db.commit()
    
    print(f"✅ Cleared {count} token(s) from database")
    print("Database is now clean and ready for new tokens with the correct encryption key!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
