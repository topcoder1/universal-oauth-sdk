# Demo 2: Device Code Flow

Demonstration of OAuth Device Flow for CLI applications, TV apps, and IoT devices.

## What is Device Flow?

Device flow (RFC 8628) allows devices with limited input capabilities to authenticate users. Perfect for:
- CLI applications
- Smart TV apps
- IoT devices
- Devices without browsers

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure GitHub OAuth:**
   
   Set environment variable:
   ```bash
   export GITHUB_CLIENT_ID="your-client-id"
   ```

3. **Get GitHub OAuth credentials:**
   - Go to https://github.com/settings/developers
   - Create new OAuth App
   - Add redirect URI: `http://localhost:8787/callback`
   - **Important:** GitHub device flow requires organization approval

## Run

```bash
npm start
```

## How It Works

1. ✅ App requests device code from GitHub
2. ✅ User sees verification URL and code
3. ✅ User visits URL on any device
4. ✅ User enters code and authorizes
5. ✅ App polls GitHub until authorized
6. ✅ App receives access token
7. ✅ App fetches user data

## Expected Output

```
📱 Universal OAuth SDK - Device Flow Demo

✅ Client initialized

🔐 Starting Device Authorization Flow...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 DEVICE AUTHORIZATION REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Visit: https://github.com/login/device
2. Enter code: ABCD-1234

⏳ Waiting for authorization...

✅ Authorization successful!

📥 Fetching user information...

👤 GitHub User Information:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Username: topcoder1
Name: John Doe
Bio: Software Developer
Public Repos: 42
Followers: 123
Profile: https://github.com/topcoder1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Demo complete!
```

## Use Cases

- **CLI Tools:** Authenticate users without opening browsers
- **Smart TVs:** Users can auth on their phone
- **IoT Devices:** Devices without screens
- **CI/CD:** Secure authentication in pipelines
