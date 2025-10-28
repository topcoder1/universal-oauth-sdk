# Demo 4: Multi-Provider Support

Demonstration of authenticating with multiple OAuth providers simultaneously.

## Features

- ✅ Authenticate with multiple providers
- ✅ Manage multiple accounts
- ✅ Unified token storage
- ✅ Consistent API across providers

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure OAuth credentials:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Get OAuth credentials for each provider:**

   **Google:**
   - https://console.cloud.google.com/
   - Create OAuth 2.0 credentials
   - Add redirect: `http://localhost:8787/callback`

   **GitHub:**
   - https://github.com/settings/developers
   - Create OAuth App
   - Add redirect: `http://localhost:8787/callback`

   **Microsoft:**
   - https://portal.azure.com/
   - Register application
   - Add redirect: `http://localhost:8787/callback`

## Run

```bash
npm start
```

## What It Does

1. ✅ Attempts to authenticate with all configured providers
2. ✅ Stores tokens for each provider separately
3. ✅ Fetches user information from each provider
4. ✅ Displays unified summary of all accounts

## Expected Output

```
🌐 Universal OAuth SDK - Multi-Provider Demo

This demo authenticates with multiple OAuth providers
and demonstrates managing multiple accounts.

🔐 Authenticating with GOOGLE...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ google authentication successful!

🔐 Authenticating with GITHUB...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ github authentication successful!

🔐 Authenticating with MICROSOFT...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ microsoft authentication successful!


📊 AUTHENTICATED ACCOUNTS SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔹 GOOGLE
   Name: John Doe
   Email: john@gmail.com

🔹 GITHUB
   Username: topcoder1
   Name: John Doe

🔹 MICROSOFT
   Name: John Doe
   Email: john@company.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Successfully authenticated with 3 provider(s)!

✨ Demo complete!
```

## Use Cases

- **Social Login:** Let users choose their preferred provider
- **Data Aggregation:** Pull data from multiple services
- **Cross-Platform Apps:** Sync across different platforms
- **Enterprise SSO:** Support multiple identity providers
- **Developer Tools:** Integrate with multiple APIs

## Supported Providers

The SDK includes 11 pre-configured providers:
- Google
- GitHub
- Microsoft
- Salesforce
- Slack
- LinkedIn
- Dropbox
- Shopify
- Twitter/X
- Discord
- Spotify
