# Testing Guide - Python SDK

This guide walks you through testing the Python SDK with real OAuth providers.

## Prerequisites

1. **Python SDK installed:**
   ```bash
   cd packages/sdk-python
   pip install -e .
   pip install python-dotenv
   ```

2. **Provider manifests available:**
   - Located in `../provider-catalog/manifests/`
   - Should have: google.json, github.json, microsoft.json, etc.

---

## Option 1: Test with Google OAuth (Recommended)

### Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project (or select existing)
3. Click **"Create Credentials"** → **"OAuth 2.0 Client ID"**
4. Configure consent screen if prompted:
   - User Type: External
   - App name: "OAuth SDK Test"
   - Support email: your email
   - Scopes: Leave default
   - Test users: Add your email
5. Application type: **Web application**
6. Name: "OAuth SDK Test"
7. Authorized redirect URIs: `http://localhost:8787/callback`
8. Click **Create**
9. Copy **Client ID** and **Client Secret**

### Step 2: Create .env File

```bash
cd packages/sdk-python/examples
cp .env.example .env
```

Edit `.env`:
```bash
GOOGLE_CLIENT_ID=your-actual-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret-here
```

### Step 3: Run Google Example

```bash
python examples/google_example.py
```

**Expected output:**
```
============================================================
Google OAuth Example
============================================================

📋 Initializing OAuth client...
   Provider: Google
   Scopes: openid, profile, email

🔐 Starting authorization flow...
🌐 Opening browser for authorization...
   If browser doesn't open, visit: https://accounts.google.com/o/oauth2/v2/auth?...
⏳ Waiting for authorization (timeout: 300s)...
✅ Authorization code received!
🔄 Exchanging code for access token...
✅ Token saved successfully!
   Access token: ya29.a0AfH6SMBw...
   Expires: 2025-11-03 18:34:56

📡 Testing API request...
✅ API request successful!
   User: Your Name
   Email: your.email@gmail.com

🔄 Testing token refresh...
✅ Token is fresh
   Expires in: 3599s

============================================================
✅ Example completed successfully!
============================================================
```

### Step 4: Verify Token Storage

```bash
# Check that token was saved
ls -la tokens.db

# Optional: View token (SQLite)
sqlite3 tokens.db "SELECT * FROM tokens;"
```

---

## Option 2: Test with GitHub OAuth

### Step 1: Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **"New OAuth App"**
3. Fill in:
   - Application name: "OAuth SDK Test"
   - Homepage URL: `http://localhost`
   - Authorization callback URL: `http://localhost:8787/callback`
4. Click **Register application**
5. Copy **Client ID**
6. Click **Generate a new client secret**
7. Copy **Client Secret**

### Step 2: Update .env

```bash
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### Step 3: Run GitHub Example

```bash
python examples/github_example.py
```

---

## Troubleshooting

### Issue: Browser doesn't open

**Solution 1:** Manually copy URL from console
```
🔗 Please visit this URL to authorize:
   https://accounts.google.com/o/oauth2/v2/auth?...
```
Copy and paste this URL into your browser.

**Solution 2:** Disable auto-open
```python
token = await client.authorize(open_browser=False)
```

---

### Issue: "Port 8787 already in use"

**Solution:** Change redirect URI port
```python
client = OAuthClient(
    provider="google",
    redirect_uri="http://localhost:9999/callback",  # Different port
    ...
)
```

Then update redirect URI in Google Console to match.

---

### Issue: "redirect_uri_mismatch"

**Error message:**
```
Error 400: redirect_uri_mismatch
The redirect URI in the request, http://localhost:8787/callback, 
does not match the ones authorized for the OAuth client.
```

**Solution:** Ensure redirect URI matches EXACTLY:
1. In your code: `http://localhost:8787/callback`
2. In Google Console: `http://localhost:8787/callback`
3. No trailing slash
4. Exact port number
5. http (not https) for localhost

---

### Issue: "invalid_client"

**Solution:** Check client ID and secret
- Verify you copied them correctly
- No extra spaces
- No quotes around values in .env file

---

### Issue: Token exchange fails

**Check:**
1. Client secret is correct
2. Redirect URI matches exactly
3. Provider manifest is loaded correctly
4. Network connection is working

**Debug:**
```python
# Add error details
try:
    token = await client.authorize()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

---

### Issue: API request returns 401

**Possible causes:**
1. Token expired (should auto-refresh)
2. Scopes insufficient for API endpoint
3. Token not saved correctly

**Solution:**
```python
# Check token
token = await client.get_token("google_user")
print(f"Token: {token}")
print(f"Expired: {token.is_expired() if token else 'N/A'}")

# Force refresh
token = await client.refresh_if_needed("google_user")
```

---

## Testing Checklist

### ✅ Basic Flow
- [ ] Client initializes without errors
- [ ] Authorization URL is generated
- [ ] Browser opens automatically
- [ ] Callback server starts on port 8787
- [ ] User can authorize in browser
- [ ] Callback is received
- [ ] Token is exchanged successfully
- [ ] Token is saved to storage

### ✅ Token Management
- [ ] Token is retrieved from storage
- [ ] Token expiration is checked correctly
- [ ] Token refreshes when expired
- [ ] Refreshed token is saved

### ✅ API Requests
- [ ] Authenticated request succeeds
- [ ] Authorization header is set correctly
- [ ] 401 triggers automatic refresh
- [ ] Retry after refresh succeeds

### ✅ Error Handling
- [ ] Invalid credentials show clear error
- [ ] Timeout works correctly
- [ ] State mismatch is detected
- [ ] Network errors are handled

---

## Manual Test Script

Create `test_manual.py`:

```python
"""Manual test script for Python SDK"""
import asyncio
import os
from dotenv import load_dotenv
from oauth_sdk import OAuthClient, SQLiteStore

load_dotenv()

async def test_google():
    """Test Google OAuth flow"""
    print("\n" + "="*60)
    print("Testing Google OAuth")
    print("="*60)
    
    client = OAuthClient(
        provider="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        redirect_uri="http://localhost:8787/callback",
        store=SQLiteStore("test_tokens.db"),
    )
    
    try:
        # Test authorization
        print("\n1. Testing authorization...")
        token = await client.authorize(key="test_google")
        print(f"✅ Token obtained: {token.access_token[:20]}...")
        
        # Test API request
        print("\n2. Testing API request...")
        response = await client.request(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            key="test_google"
        )
        print(f"✅ API response: {response.status_code}")
        print(f"   User: {response.json()}")
        
        # Test token refresh
        print("\n3. Testing token refresh...")
        refreshed = await client.refresh_if_needed("test_google")
        print(f"✅ Token refreshed: {refreshed is not None}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_google())
```

Run:
```bash
python test_manual.py
```

---

## Next Steps

After successful testing:

1. **Clean up test tokens:**
   ```bash
   rm tokens.db test_tokens.db
   ```

2. **Test with other providers:**
   - GitHub
   - Microsoft
   - Any provider with manifest

3. **Start adding new providers:**
   - See `ADDING_PROVIDERS.md`
   - Create manifests for Stripe, Zoom, Notion, etc.

---

## Getting Help

If you encounter issues:

1. **Check logs:** Look for error messages in console
2. **Verify credentials:** Double-check client ID/secret
3. **Check manifests:** Ensure provider JSON is valid
4. **Test network:** Verify you can reach OAuth endpoints
5. **Read errors:** OAuth errors are usually descriptive

**Common OAuth errors:**
- `invalid_client` - Wrong client ID/secret
- `redirect_uri_mismatch` - Redirect URI doesn't match
- `invalid_grant` - Authorization code expired or invalid
- `invalid_scope` - Requested scope not allowed

---

**Last Updated:** November 3, 2025
