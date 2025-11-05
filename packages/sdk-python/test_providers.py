"""Test script to verify all provider manifests load correctly"""

import asyncio
from oauth_sdk import ProviderRegistry


async def main():
    """Test loading all providers"""
    print("=" * 60)
    print("Provider Registry Test")
    print("=" * 60)
    
    # Create registry
    registry = ProviderRegistry()
    
    # List all available providers
    print("\n📋 Listing all available providers...")
    providers = await registry.list_providers()
    print(f"   Found {len(providers)} providers")
    
    # Test loading each provider
    print("\n🔍 Testing each provider manifest...")
    success_count = 0
    failed = []
    
    for provider_id in sorted(providers):
        try:
            provider = await registry.get_provider(provider_id)
            print(f"   ✅ {provider.name:15} - {provider.auth_url[:50]}...")
            success_count += 1
        except Exception as e:
            print(f"   ❌ {provider_id:15} - Error: {e}")
            failed.append((provider_id, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Successfully loaded: {success_count}/{len(providers)}")
    if failed:
        print(f"❌ Failed to load: {len(failed)}")
        for provider_id, error in failed:
            print(f"   - {provider_id}: {error}")
    else:
        print("🎉 All providers loaded successfully!")
    print("=" * 60)
    
    # Show provider details
    print("\n📊 Provider Details:")
    print("-" * 60)
    for provider_id in sorted(providers):
        try:
            provider = await registry.get_provider(provider_id)
            print(f"\n{provider.name} ({provider.id})")
            print(f"  Auth URL: {provider.auth_url}")
            print(f"  Token URL: {provider.token_url}")
            print(f"  Scopes: {', '.join(provider.scopes[:3])}{'...' if len(provider.scopes) > 3 else ''}")
            print(f"  PKCE: {'Yes' if provider.pkce else 'No'}")
        except Exception as e:
            print(f"\n{provider_id}: Error loading - {e}")


if __name__ == "__main__":
    asyncio.run(main())
