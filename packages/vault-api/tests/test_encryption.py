"""Tests for token encryption"""

import pytest
from app.core.encryption import TokenEncryption


def test_encrypt_decrypt():
    """Test basic encryption and decryption"""
    encryption = TokenEncryption()
    
    plaintext = "my_secret_token_12345"
    encrypted = encryption.encrypt(plaintext)
    decrypted = encryption.decrypt(encrypted)
    
    assert encrypted != plaintext
    assert decrypted == plaintext


def test_encrypt_none():
    """Test encrypting None returns None"""
    encryption = TokenEncryption()
    assert encryption.encrypt(None) is None


def test_decrypt_none():
    """Test decrypting None returns None"""
    encryption = TokenEncryption()
    assert encryption.decrypt(None) is None


def test_different_encryptions():
    """Test same plaintext produces different ciphertexts (due to random nonce)"""
    encryption = TokenEncryption()
    
    plaintext = "test_token"
    encrypted1 = encryption.encrypt(plaintext)
    encrypted2 = encryption.encrypt(plaintext)
    
    assert encrypted1 != encrypted2
    assert encryption.decrypt(encrypted1) == plaintext
    assert encryption.decrypt(encrypted2) == plaintext


def test_long_token():
    """Test encrypting long tokens"""
    encryption = TokenEncryption()
    
    long_token = "a" * 1000
    encrypted = encryption.encrypt(long_token)
    decrypted = encryption.decrypt(encrypted)
    
    assert decrypted == long_token
