"""Tests for token storage

TODO (Day 8-10): Add more comprehensive tests after implementation
"""

import pytest

from oauth_sdk import MemoryStore, SQLiteStore, Token


@pytest.mark.asyncio
async def test_memory_store_set_get():
    """Test memory store basic operations"""
    store = MemoryStore()
    
    token = Token(access_token="test_token", token_type="Bearer")
    await store.set("test_key", token)
    
    retrieved = await store.get("test_key")
    assert retrieved is not None
    assert retrieved.access_token == "test_token"


@pytest.mark.asyncio
async def test_memory_store_delete():
    """Test memory store deletion"""
    store = MemoryStore()
    
    token = Token(access_token="test_token")
    await store.set("test_key", token)
    
    assert await store.has("test_key")
    
    await store.delete("test_key")
    
    assert not await store.has("test_key")
    assert await store.get("test_key") is None


@pytest.mark.asyncio
async def test_memory_store_has():
    """Test memory store existence check"""
    store = MemoryStore()
    
    assert not await store.has("nonexistent")
    
    token = Token(access_token="test_token")
    await store.set("test_key", token)
    
    assert await store.has("test_key")


@pytest.mark.asyncio
async def test_sqlite_store_persistence():
    """Test SQLite store persistence"""
    import tempfile
    import os
    
    # Use temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        # Create store and save token
        async with SQLiteStore(db_path) as store:
            token = Token(access_token="test_token", token_type="Bearer")
            await store.set("test_key", token)
            
            # Verify it's there
            retrieved = await store.get("test_key")
            assert retrieved is not None
            assert retrieved.access_token == "test_token"
        
        # Open again and verify persistence
        async with SQLiteStore(db_path) as store2:
            retrieved2 = await store2.get("test_key")
            assert retrieved2 is not None
            assert retrieved2.access_token == "test_token"
    
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.mark.asyncio
async def test_sqlite_store_list():
    """Test SQLiteStore list functionality"""
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        async with SQLiteStore(db_path) as store:
            # Add multiple tokens
            await store.set("user:123", Token(access_token="token1"))
            await store.set("user:456", Token(access_token="token2"))
            await store.set("app:789", Token(access_token="token3"))
            
            # List all
            all_keys = await store.list()
            assert len(all_keys) == 3
            assert "user:123" in all_keys
            
            # List with prefix
            user_keys = await store.list("user:")
            assert len(user_keys) == 2
            assert "user:123" in user_keys
            assert "user:456" in user_keys
            assert "app:789" not in user_keys
    
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
