# Express.js OAuth Example

A complete Express.js web application demonstrating OAuth authentication with the Universal OAuth SDK.

## Features

- 🔐 OAuth 2.0 authentication with multiple providers
- 🔄 Automatic token refresh
- 💾 Persistent token storage with SQLite
- 👤 User profile display
- 🎨 Clean, modern UI
- 🔒 Session management

## Supported Providers

- Google
- GitHub
- Microsoft

## Setup

1. **Install dependencies:**
   ```bash
   pnpm install
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your OAuth credentials
   ```

3. **Get OAuth credentials:**

   **Google:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project → APIs & Services → Credentials
   - Create OAuth 2.0 Client ID
   - Add redirect URI: `http://localhost:3000/auth/google/callback`

   **GitHub:**
   - Go to Settings → Developer settings → OAuth Apps
   - Create new OAuth App
   - Authorization callback URL: `http://localhost:3000/auth/github/callback`

   **Microsoft:**
   - Go to [Azure Portal](https://portal.azure.com/)
   - App registrations → New registration
   - Add redirect URI: `http://localhost:3000/auth/microsoft/callback`

4. **Run the application:**
   ```bash
   pnpm dev
   ```

5. **Open your browser:**
   ```
   http://localhost:3000
   ```

## How It Works

1. User clicks "Sign in with [Provider]"
2. App redirects to provider's authorization page
3. User grants permission
4. Provider redirects back to app with authorization code
5. SDK exchanges code for access token
6. Token is stored in SQLite database
7. App makes authenticated API requests
8. Token is automatically refreshed when needed

## Project Structure

```
express-app/
├── src/
│   └── index.js          # Main application
├── .env.example          # Environment template
├── package.json          # Dependencies
└── README.md            # This file
```

## API Endpoints

- `GET /` - Home page with login options
- `GET /auth/:provider` - Start OAuth flow
- `GET /auth/:provider/callback` - OAuth callback
- `GET /dashboard` - Protected dashboard (requires auth)
- `GET /logout` - Logout and clear session

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SESSION_SECRET` | Secret for session encryption |
| `PORT` | Server port (default: 3000) |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth client secret |
| `MICROSOFT_CLIENT_ID` | Microsoft OAuth client ID |
| `MICROSOFT_CLIENT_SECRET` | Microsoft OAuth client secret |

## Security Notes

- Never commit `.env` file
- Use strong `SESSION_SECRET` in production
- Enable `secure` cookies in production (HTTPS)
- Implement CSRF protection for production
- Add rate limiting for production

## Troubleshooting

**"Unknown provider" error:**
- Check that provider manifests are in the correct location
- Verify provider name matches manifest filename

**"No token available" error:**
- Complete the OAuth flow first
- Check that tokens.db has correct permissions

**Redirect URI mismatch:**
- Ensure redirect URI in OAuth app matches exactly
- Include protocol (http/https) and port

## Next Steps

- Add more providers (Slack, Salesforce, etc.)
- Implement user database
- Add profile editing
- Implement token encryption
- Add API endpoints for your application
- Deploy to production

## License

MIT
