# Next.js OAuth Example

Modern Next.js 14 App Router example with Universal OAuth SDK.

## Features

- ✅ Next.js 14 App Router
- ✅ Server-side OAuth flow
- ✅ Secure token storage
- ✅ Automatic token refresh
- ✅ TypeScript support
- ✅ Tailwind CSS styling
- ✅ Protected routes
- ✅ User session management

## Setup

1. **Install dependencies:**
   ```bash
   cd packages/examples/nextjs-app
   pnpm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your OAuth credentials
   ```

3. **Run development server:**
   ```bash
   pnpm dev
   ```

4. **Open browser:**
   ```
   http://localhost:3000
   ```

## Environment Variables

Create `.env.local`:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-secret

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-secret

# Session secret
SESSION_SECRET=your-random-secret-key
```

## Project Structure

```
nextjs-app/
├── app/
│   ├── page.tsx              # Home page
│   ├── api/
│   │   └── auth/
│   │       └── [provider]/
│   │           ├── route.ts  # OAuth initiation
│   │           └── callback/
│   │               └── route.ts  # OAuth callback
│   └── dashboard/
│       └── page.tsx          # Protected dashboard
├── lib/
│   └── oauth.ts              # OAuth client setup
├── .env.example
└── README.md
```

## How It Works

1. User clicks "Sign in with [Provider]"
2. Next.js API route initiates OAuth flow
3. User authorizes on provider's site
4. Provider redirects to callback route
5. Callback exchanges code for tokens
6. Tokens stored in SQLite
7. User redirected to dashboard
8. Dashboard makes authenticated API requests

## Note

This example requires Next.js dependencies to be installed. The TypeScript errors you see are expected until you run `pnpm install` in this directory.

## License

MIT
