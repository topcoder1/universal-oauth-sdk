"""Example: Google OAuth Flow

This example demonstrates a complete OAuth flow with Google.

Prerequisites:
1. Create OAuth credentials at https://console.cloud.google.com/apis/credentials
2. Add http://localhost:8787/callback as redirect URI
3. Set environment variables:
   - GOOGLE_CLIENT_ID
   - GOOGLE_CLIENT_SECRET

Usage:
    python examples/google_example.py
"""

import asyncio
import os
from dotenv import load_dotenv

from oauth_sdk import OAuthClient, SQLiteStore

# Load environment variables
load_dotenv()


async def main():
    """Complete Google OAuth flow example"""
    
    # Get credentials from environment
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Error: Missing credentials")
        print("   Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables")
        print("   Or create a .env file with these values")
        return
    
    print("=" * 60)
    print("Google OAuth Example")
    print("=" * 60)
    
    # Create OAuth client
    client = OAuthClient(
        provider="google",
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:8787/callback",
        store=SQLiteStore("tokens.db"),
    )
    
    try:
        # Initialize client (loads provider manifest)
        print("\n📋 Initializing OAuth client...")
        await client.init()
        print(f"   Provider: {client.manifest.name}")
        print(f"   Scopes: {', '.join(client.scopes)}")
        
        # Complete authorization flow
        print("\n🔐 Starting authorization flow...")
        token = await client.authorize(
            key="google_user",
            open_browser=True,
            timeout=300,  # 5 minutes
        )
        
        # Make authenticated API request
        print("\n📡 Testing API request...")
        response = await client.request(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            key="google_user",
        )
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ API request successful!")
            print(f"   User: {user_info.get('name', 'Unknown')}")
            print(f"   Email: {user_info.get('email', 'Unknown')}")
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"   {response.text}")
        
        # Test token refresh
        print("\n🔄 Testing token refresh...")
        refreshed_token = await client.refresh_if_needed("google_user")
        if refreshed_token:
            print(f"✅ Token is fresh")
            print(f"   Expires in: {refreshed_token.expires_at - int(asyncio.get_event_loop().time())}s")
        
        print("\n" + "=" * 60)
        print("✅ Example completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
