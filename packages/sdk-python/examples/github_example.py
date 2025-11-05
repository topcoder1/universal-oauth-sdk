"""Example: GitHub OAuth Flow

This example demonstrates OAuth flow with GitHub.

Prerequisites:
1. Create OAuth App at https://github.com/settings/developers
2. Set Authorization callback URL to http://localhost:8787/callback
3. Set environment variables:
   - GITHUB_CLIENT_ID
   - GITHUB_CLIENT_SECRET

Usage:
    python examples/github_example.py
"""

import asyncio
import os
from dotenv import load_dotenv

from oauth_sdk import OAuthClient, MemoryStore

load_dotenv()


async def main():
    """GitHub OAuth flow example"""
    
    client_id = os.getenv("GITHUB_CLIENT_ID")
    client_secret = os.getenv("GITHUB_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Missing GITHUB_CLIENT_ID or GITHUB_CLIENT_SECRET")
        return
    
    print("GitHub OAuth Example")
    print("=" * 50)
    
    # Create client with in-memory storage
    client = OAuthClient(
        provider="github",
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:8787/callback",
        store=MemoryStore(),  # In-memory storage (not persistent)
    )
    
    try:
        # Authorize
        print("\n🔐 Authorizing with GitHub...")
        token = await client.authorize()
        
        # Get user info
        print("\n📡 Fetching user info...")
        response = await client.request("https://api.github.com/user")
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Logged in as: {user['login']}")
            print(f"   Name: {user.get('name', 'N/A')}")
            print(f"   Public repos: {user['public_repos']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
