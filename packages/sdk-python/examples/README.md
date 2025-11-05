# Python SDK Examples

Working examples demonstrating OAuth flows with different providers.

## Setup

1. **Install the SDK:**
   ```bash
   cd packages/sdk-python
   pip install -e .
   ```

2. **Install python-dotenv:**
   ```bash
   pip install python-dotenv
   ```

3. **Create `.env` file:**
   ```bash
   # Copy example and fill in your credentials
   cp .env.example .env
   ```

## Examples

### Google OAuth

**File:** `google_example.py`

**Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID
3. Add `http://localhost:8787/callback` as redirect URI
4. Copy Client ID and Client Secret to `.env`

**Run:**
```bash
python examples/google_example.py
```

**What it does:**
- Completes OAuth flow with Google
- Fetches user profile information
- Demonstrates token storage with SQLite
- Shows token refresh

---

### GitHub OAuth

**File:** `github_example.py`

**Setup:**
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Create New OAuth App
3. Set Authorization callback URL to `http://localhost:8787/callback`
4. Copy Client ID and Client Secret to `.env`

**Run:**
```bash
python examples/github_example.py
```

**What it does:**
- Completes OAuth flow with GitHub
- Fetches authenticated user info
- Uses in-memory storage (not persistent)

---

## Environment Variables

Create a `.env` file in the `examples/` directory:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Microsoft OAuth (optional)
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
```

## How OAuth Flow Works

1. **Client creates authorization URL** with PKCE challenge
2. **Browser opens** to provider's authorization page
3. **User authorizes** the application
4. **Provider redirects** to callback URL with authorization code
5. **Local server receives** the callback
6. **Client exchanges** code for access token
7. **Token is saved** to storage (SQLite or Memory)
8. **Client can make** authenticated API requests

## Troubleshooting

### Browser doesn't open
- Manually copy the URL from console and paste in browser
- Or set `open_browser=False` and handle URL yourself

### Callback server fails to start
- Check if port 8787 is already in use
- Change `redirect_uri` to use different port
- Make sure firewall allows localhost connections

### Token exchange fails
- Verify redirect URI matches exactly in provider settings
- Check client ID and secret are correct
- Ensure provider manifest is loaded correctly

### API requests fail with 401
- Token may be expired - client auto-refreshes if refresh token available
- Check scopes are sufficient for the API endpoint
- Verify token is saved correctly

## Next Steps

- Try other providers (Microsoft, Slack, Spotify)
- Build a real application using the SDK
- Implement token refresh in long-running apps
- Add error handling for production use

## Support

- [Documentation](https://oauth-sdk.dev/docs/python)
- [GitHub Issues](https://github.com/topcoder1/universal-oauth-sdk/issues)
- [Provider Catalog](../../provider-catalog/manifests/)
