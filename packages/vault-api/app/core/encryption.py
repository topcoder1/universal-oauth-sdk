"""Token encryption utilities using AES-256-GCM with key versioning"""

import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from typing import Dict


class TokenEncryption:
    """Handle token encryption and decryption with key versioning"""
    
    def __init__(self, encryption_keys: Dict[str, str] = None, current_version: str = 'v1'):
        """
        Initialize encryption with versioned keys.
        
        Args:
            encryption_keys: Dict of version -> base64-encoded 32-byte key
            current_version: Version to use for new encryptions
        """
        if encryption_keys:
            self.keys = {
                version: AESGCM(base64.b64decode(key))
                for version, key in encryption_keys.items()
            }
            self.current_version = current_version
        else:
            # Generate a random key (for development only)
            random_key = AESGCM.generate_key(bit_length=256)
            self.keys = {'v1': AESGCM(random_key)}
            self.current_version = 'v1'
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a token with current key version.
        
        Args:
            plaintext: The token to encrypt
            
        Returns:
            str: Versioned encrypted token (format: "v1:base64data")
        """
        if not plaintext:
            return None
        
        # Get current key
        aesgcm = self.keys[self.current_version]
        
        # Generate random nonce
        nonce = os.urandom(12)
        
        # Encrypt
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
        
        # Combine nonce + ciphertext and encode
        encrypted = base64.b64encode(nonce + ciphertext).decode('utf-8')
        
        # Prepend version for key rotation support
        return f"{self.current_version}:{encrypted}"
    
    def decrypt(self, encrypted: str) -> str:
        """
        Decrypt a token using the appropriate key version.
        
        Args:
            encrypted: Versioned encrypted token (format: "v1:base64data")
            
        Returns:
            str: Decrypted token
        """
        if not encrypted:
            return None
        
        # Extract version and data
        if ':' in encrypted:
            version, data_str = encrypted.split(':', 1)
        else:
            # Backward compatibility: assume v1 if no version prefix
            version = 'v1'
            data_str = encrypted
        
        # Get appropriate key
        if version not in self.keys:
            raise ValueError(f"Unknown encryption key version: {version}")
        
        aesgcm = self.keys[version]
        
        # Decode
        data = base64.b64decode(data_str)
        
        # Split nonce and ciphertext
        nonce = data[:12]
        ciphertext = data[12:]
        
        # Decrypt
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        return plaintext.decode('utf-8')


# Global encryption instance (initialized with config)
_encryption = None


def get_encryption() -> TokenEncryption:
    """Get global encryption instance with key versioning"""
    global _encryption
    if _encryption is None:
        from app.config import settings
        
        # Support multiple encryption keys for rotation
        encryption_keys = {'v1': settings.ENCRYPTION_KEY}
        
        # Add v2 key if configured (for rotation)
        if hasattr(settings, 'ENCRYPTION_KEY_V2') and settings.ENCRYPTION_KEY_V2:
            encryption_keys['v2'] = settings.ENCRYPTION_KEY_V2
        
        # Determine current version (use v2 if available)
        current_version = 'v2' if 'v2' in encryption_keys else 'v1'
        
        _encryption = TokenEncryption(encryption_keys, current_version)
    return _encryption
