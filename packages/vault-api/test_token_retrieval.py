"""Test token retrieval and identify issues"""
from app.database import SessionLocal
from app.models.token import Token
from app.core.encryption import get_encryption

db = SessionLocal()

try:
    # Get all tokens
    tokens = db.query(Token).all()
    print(f"📊 Found {len(tokens)} token(s) in database\n")
    
    if tokens:
        encryption = get_encryption()
        
        for token in tokens:
            print(f"Token ID: {token.id}")
            print(f"  Provider: {token.provider}")
            print(f"  Key: {token.key}")
            print(f"  Created: {token.created_at}")
            
            # Try to decrypt
            try:
                decrypted = encryption.decrypt(token.access_token_encrypted)
                print(f"  ✅ Decryption successful")
            except Exception as e:
                print(f"  ❌ Decryption failed: {e}")
            
            print()
    else:
        print("No tokens found. Database is empty.")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
