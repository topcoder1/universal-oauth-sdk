"""Generate a valid encryption key for the Vault API"""
import base64
import os

# Generate a random 32-byte key
key = os.urandom(32)

# Encode it as base64
key_b64 = base64.b64encode(key).decode('utf-8')

print("🔐 Generated Encryption Key")
print("=" * 60)
print(f"ENCRYPTION_KEY={key_b64}")
print("=" * 60)
print("\nCopy this line to your .env file!")
print("Replace the existing ENCRYPTION_KEY line with this one.")
