"""Token storage implementations

This module will be populated with AI-translated code from Node SDK in Day 3-4.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import aiosqlite
import json

from oauth_sdk.models import Token
from oauth_sdk.exceptions import StorageError


class TokenStore(ABC):
    """Abstract base class for token storage"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Token]:
        """Retrieve token by key"""
        pass

    @abstractmethod
    async def set(self, key: str, token: Token) -> None:
        """Store token with key"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete token by key"""
        pass

    @abstractmethod
    async def has(self, key: str) -> bool:
        """Check if token exists"""
        pass


class MemoryStore(TokenStore):
    """In-memory token storage
    
    TODO (Day 3-4): Translate from Node SDK
    - Simple dict-based storage
    - No persistence
    - Good for development/testing
    """

    def __init__(self):
        """Initialize memory store"""
        self._tokens: Dict[str, Token] = {}

    async def get(self, key: str) -> Optional[Token]:
        """Retrieve token by key"""
        return self._tokens.get(key)

    async def set(self, key: str, token: Token) -> None:
        """Store token with key"""
        self._tokens[key] = token

    async def delete(self, key: str) -> None:
        """Delete token by key"""
        self._tokens.pop(key, None)

    async def has(self, key: str) -> bool:
        """Check if token exists"""
        return key in self._tokens


class SQLiteStore(TokenStore):
    """SQLite-based token storage
    
    Persistent storage with async SQLite operations.
    Based on Node SDK sqlite.ts implementation.
    """

    def __init__(self, db_path: str = "tokens.db"):
        """Initialize SQLite store
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._db: Optional[aiosqlite.Connection] = None

    async def _init_db(self) -> None:
        """Initialize database and create tables"""
        if self._db is None:
            self._db = await aiosqlite.connect(self.db_path)
            # Simple schema matching Node SDK: key-value pairs with JSON
            await self._db.execute(
                """
                CREATE TABLE IF NOT EXISTS tokens (
                    k TEXT PRIMARY KEY,
                    v TEXT NOT NULL
                )
                """
            )
            await self._db.commit()

    async def get(self, key: str) -> Optional[Token]:
        """Retrieve token by key"""
        await self._init_db()
        
        cursor = await self._db.execute("SELECT v FROM tokens WHERE k=?", (key,))
        row = await cursor.fetchone()
        
        if not row or not row[0]:
            return None
        
        # Parse JSON and reconstruct Token
        try:
            data = json.loads(row[0])
            return Token.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            raise StorageError(f"Failed to parse token data: {e}") from e

    async def set(self, key: str, token: Token) -> None:
        """Store token with key"""
        await self._init_db()
        
        # Serialize token to JSON
        token_json = json.dumps(token.to_dict())
        
        # Insert or replace
        await self._db.execute(
            "INSERT OR REPLACE INTO tokens(k, v) VALUES(?, ?)",
            (key, token_json)
        )
        await self._db.commit()

    async def delete(self, key: str) -> None:
        """Delete token by key"""
        await self._init_db()
        
        await self._db.execute("DELETE FROM tokens WHERE k=?", (key,))
        await self._db.commit()

    async def has(self, key: str) -> bool:
        """Check if token exists"""
        await self._init_db()
        
        cursor = await self._db.execute("SELECT 1 FROM tokens WHERE k=?", (key,))
        row = await cursor.fetchone()
        return row is not None

    async def list(self, prefix: str = "") -> list[str]:
        """List all keys with optional prefix filter"""
        await self._init_db()
        
        if prefix:
            cursor = await self._db.execute(
                "SELECT k FROM tokens WHERE k LIKE ?",
                (f"{prefix}%",)
            )
        else:
            cursor = await self._db.execute("SELECT k FROM tokens")
        
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

    async def close(self) -> None:
        """Close database connection"""
        if self._db:
            await self._db.close()
            self._db = None

    async def __aenter__(self) -> "SQLiteStore":
        """Async context manager entry"""
        await self._init_db()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        await self.close()
