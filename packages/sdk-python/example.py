"""Example usage of Universal OAuth SDK - Python

This is a placeholder example. Full implementation in Day 3-4.
"""

import asyncio
from oauth_sdk import OAuthClient, MemoryStore, Token


async def main():
    """Example OAuth flow"""
    print("Universal OAuth SDK - Python v0.1.0")
    print("=" * 50)
    
    # Create a token (for testing)
    token = Token(
        access_token="example_token",
        token_type="Bearer",
        expires_in=3600,
    )
    
    print(f"✅ Token created: {token.access_token}")
    print(f"   Type: {token.token_type}")
    print(f"   Expires in: {token.expires_in}s")
    
    # Test memory store
    store = MemoryStore()
    await store.set("test_key", token)
    retrieved = await store.get("test_key")
    
    print(f"\n✅ Token stored and retrieved from MemoryStore")
    print(f"   Retrieved token: {retrieved.access_token if retrieved else 'None'}")
    
    # TODO (Day 3-4): Add full OAuth flow example
    print("\n⚠️  Full OAuth client implementation coming in Day 3-4")
    print("   - Authorization URL generation")
    print("   - Token exchange")
    print("   - Token refresh")
    print("   - Provider registry")


if __name__ == "__main__":
    asyncio.run(main())
