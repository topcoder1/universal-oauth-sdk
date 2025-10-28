# Demo 1: Basic OAuth Usage

Simple demonstration of OAuth authentication with Google.

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure OAuth credentials:**
   
   Create a `.env` file:
   ```env
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-secret
   ```

   Or set environment variables:
   ```bash
   export GOOGLE_CLIENT_ID="your-client-id"
   export GOOGLE_CLIENT_SECRET="your-secret"
   ```

3. **Get Google OAuth credentials:**
   - Go to https://console.cloud.google.com/
   - Create a new project or select existing
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add redirect URI: `http://localhost:8787/callback`

## Run

```bash
npm start
```

## What It Does

1. ✅ Initializes OAuth client with Google
2. ✅ Opens browser for authentication
3. ✅ Handles OAuth callback
4. ✅ Fetches user information
5. ✅ Displays user profile

## Expected Output

```
🔐 Universal OAuth SDK - Basic Demo

✅ Client initialized

🌐 Starting OAuth flow...
👉 A browser window will open for authentication

✅ Authentication successful!

📥 Fetching user information...

👤 User Information:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: John Doe
Email: john@example.com
Picture: https://...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Demo complete!
```
