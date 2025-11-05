# Universal OAuth SDK - Python

Multi-language OAuth SDK for connecting to 50+ OAuth providers.

## Status

🚧 **Alpha** - Python SDK v0.1.0 in development

## Features

- 🔐 **50+ OAuth Providers** - Google, GitHub, Microsoft, Salesforce, and more
- 🐍 **Modern Python** - Async/await, type hints, Python 3.10+
- 💾 **Built-in Token Storage** - Memory, SQLite, or custom stores
- 🔄 **Token Lifecycle** - Automatic refresh, revocation
- 🎯 **Simple API** - Get started in 5 minutes

## Installation

```bash
pip install universal-oauth-sdk
```

## Quick Start

```python
import asyncio
from oauth_sdk import OAuthClient, SQLiteStore

async def main():
    # Create client
    client = OAuthClient(
        provider="google",
        client_id="your-client-id",
        client_secret="your-client-secret",
        redirect_uri="http://localhost:8787/callback",
        store=SQLiteStore("tokens.db")
    )
    
    # Complete OAuth flow (opens browser, handles callback)
    token = await client.authorize()
    
    # Make authenticated API request
    response = await client.request("https://www.googleapis.com/oauth2/v1/userinfo")
    user_info = response.json()
    print(f"Hello, {user_info['name']}!")
    
    await client.close()

asyncio.run(main())
```

**That's it!** The SDK handles:
- ✅ Authorization URL generation with PKCE
- ✅ Local callback server
- ✅ Browser auto-open
- ✅ Token exchange
- ✅ Token storage
- ✅ Automatic token refresh

## Supported Providers

- Google
- GitHub
- Microsoft
- Salesforce
- Slack
- Spotify
- LinkedIn
- Twitter
- Discord
- Dropbox
- Shopify
- ...and 40+ more

## Documentation

Full documentation: https://oauth-sdk.dev/docs/python

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black oauth_sdk/

# Type check
mypy oauth_sdk/

# Lint
ruff oauth_sdk/
```

## License

MIT

## Links

- [GitHub](https://github.com/topcoder1/universal-oauth-sdk)
- [Documentation](https://oauth-sdk.dev)
- [Node.js SDK](../sdk-node)
