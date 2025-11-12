# @oauth-sdk/react - Integration Guide

Complete guide for integrating OAuth SDK React into your application.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Setup](#setup)
3. [Basic Integration](#basic-integration)
4. [Advanced Features](#advanced-features)
5. [Customization](#customization)
6. [Error Handling](#error-handling)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- React 18+
- Node.js 16+
- Vault API running (or use hosted version)
- API key from dashboard

### Installation

```bash
npm install @oauth-sdk/react
```

---

## Setup

### 1. Import Styles

Add to your main app file:

```tsx
// App.tsx or _app.tsx
import '@oauth-sdk/react/styles.css'
```

### 2. Get API Key

1. Sign up at https://oauth-sdk.dev
2. Create a project
3. Copy your API key (starts with `vk_live_` or `vk_test_`)

### 3. Set Environment Variables

```bash
# .env.local
NEXT_PUBLIC_OAUTH_API_KEY=vk_live_abc123
NEXT_PUBLIC_OAUTH_API_URL=https://api.oauth-sdk.dev
```

---

## Basic Integration

### Step 1: Add ConnectPortal

```tsx
// pages/connections.tsx
import { ConnectPortal } from '@oauth-sdk/react'

export default function ConnectionsPage() {
  return (
    <div>
      <h1>Connect Your Accounts</h1>
      <ConnectPortal
        apiKey={process.env.NEXT_PUBLIC_OAUTH_API_KEY!}
        userId="user_123" // Replace with actual user ID
      />
    </div>
  )
}
```

### Step 2: Add Callback Route

```tsx
// pages/oauth/callback.tsx
import { OAuthCallback } from '@oauth-sdk/react'

export default function CallbackPage() {
  return (
    <OAuthCallback
      apiKey={process.env.NEXT_PUBLIC_OAUTH_API_KEY!}
      onSuccess={() => {
        window.location.href = '/connections'
      }}
      onError={() => {
        window.location.href = '/error'
      }}
    />
  )
}
```

### Step 3: Test

1. Start your app: `npm run dev`
2. Navigate to `/connections`
3. Click "Connect" on a provider
4. Complete OAuth flow
5. Get redirected back to `/connections`

---

## Advanced Features

### Save Connections to Database

```tsx
<ConnectPortal
  apiKey={apiKey}
  userId={currentUser.id}
  onConnect={async (provider, connection) => {
    // Save to your database
    await fetch('/api/connections', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id,
        provider: provider.id,
        connectionId: connection.id,
        providerName: provider.name,
        expiresAt: connection.expiresAt
      })
    })
    
    // Show success message
    toast.success(`Connected to ${provider.name}!`)
  }}
/>
```

### Filter Providers

```tsx
// Show only social providers
<ConnectPortal
  apiKey={apiKey}
  userId={userId}
  category="social"
/>

// Show specific providers
<ConnectPortal
  apiKey={apiKey}
  userId={userId}
  providers={['google', 'github', 'microsoft']}
/>
```

### Custom UI with Headless Mode

```tsx
import { useOAuth } from '@oauth-sdk/react'

function CustomConnectionUI() {
  const {
    providers,
    connections,
    loading,
    error,
    connect,
    disconnect
  } = useOAuth({
    apiKey: process.env.NEXT_PUBLIC_OAUTH_API_KEY!,
    userId: currentUser.id
  })

  if (loading) return <Spinner />
  if (error) return <Error message={error.message} />

  return (
    <div className="grid grid-cols-3 gap-4">
      {providers.map(provider => {
        const isConnected = connections.some(
          c => c.provider === provider.id && c.status === 'active'
        )

        return (
          <Card key={provider.id}>
            <img src={provider.icon} alt={provider.name} />
            <h3>{provider.name}</h3>
            <p>{provider.description}</p>
            {isConnected ? (
              <Button
                variant="secondary"
                onClick={() => disconnect(provider.id)}
              >
                Disconnect
              </Button>
            ) : (
              <Button
                variant="primary"
                onClick={() => connect(provider.id)}
              >
                Connect
              </Button>
            )}
          </Card>
        )
      })}
    </div>
  )
}
```

---

## Customization

### Theme Customization

```tsx
<ConnectPortal
  apiKey={apiKey}
  userId={userId}
  theme={{
    // Colors
    primaryColor: '#6366f1',
    secondaryColor: '#8b5cf6',
    backgroundColor: '#ffffff',
    textColor: '#1f2937',
    
    // Typography
    fontFamily: 'Inter, system-ui, sans-serif',
    
    // Spacing
    borderRadius: '16px',
    
    // Branding
    logo: 'https://yourapp.com/logo.png'
  }}
/>
```

### CSS Customization

```css
/* Override default styles */
.oauth-sdk-portal {
  max-width: 1400px;
  margin: 0 auto;
}

.oauth-sdk-card {
  border: 2px solid #e5e7eb;
  transition: all 0.3s;
}

.oauth-sdk-card:hover {
  border-color: #6366f1;
  transform: translateY(-2px);
}

.oauth-sdk-button {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
```

---

## Error Handling

### Display Errors to Users

```tsx
import { useToast, ToastContainer } from '@oauth-sdk/react'

function App() {
  const { toasts, removeToast, error } = useToast()

  return (
    <>
      <ConnectPortal
        apiKey={apiKey}
        userId={userId}
        onError={(err) => {
          error(err.message)
        }}
      />
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </>
  )
}
```

### Retry Failed Requests

```tsx
const { error, retry, retrying } = useOAuth({ apiKey, userId })

if (error) {
  return (
    <div className="error-container">
      <h3>Something went wrong</h3>
      <p>{error.message}</p>
      <button
        onClick={retry}
        disabled={retrying}
        className="retry-button"
      >
        {retrying ? 'Retrying...' : 'Try Again'}
      </button>
    </div>
  )
}
```

### Log Errors to Service

```tsx
import * as Sentry from '@sentry/react'

<ConnectPortal
  apiKey={apiKey}
  userId={userId}
  onError={(error) => {
    // Log to Sentry
    Sentry.captureException(error, {
      tags: {
        component: 'ConnectPortal',
        userId: userId
      }
    })
    
    // Show user-friendly message
    toast.error('Failed to connect. Please try again.')
  }}
/>
```

---

## Production Deployment

### Environment Variables

```bash
# Production
NEXT_PUBLIC_OAUTH_API_KEY=vk_live_abc123
NEXT_PUBLIC_OAUTH_API_URL=https://api.oauth-sdk.dev

# Staging
NEXT_PUBLIC_OAUTH_API_KEY=vk_test_xyz789
NEXT_PUBLIC_OAUTH_API_URL=https://api-staging.oauth-sdk.dev
```

### Security Best Practices

1. **Never expose API keys in client code**
   ```tsx
   // ❌ Bad
   const apiKey = 'vk_live_abc123'
   
   // ✅ Good
   const apiKey = process.env.NEXT_PUBLIC_OAUTH_API_KEY!
   ```

2. **Validate user IDs**
   ```tsx
   // Get user ID from authenticated session
   const { user } = useAuth()
   
   <ConnectPortal
     apiKey={apiKey}
     userId={user.id} // From authenticated session
   />
   ```

3. **Use HTTPS in production**
   ```tsx
   const apiUrl = process.env.NODE_ENV === 'production'
     ? 'https://api.oauth-sdk.dev'
     : 'http://localhost:8000'
   ```

### Performance Optimization

1. **Lazy load the component**
   ```tsx
   import dynamic from 'next/dynamic'
   
   const ConnectPortal = dynamic(
     () => import('@oauth-sdk/react').then(mod => mod.ConnectPortal),
     { ssr: false }
   )
   ```

2. **Memoize callbacks**
   ```tsx
   const handleConnect = useCallback((provider, connection) => {
     saveConnection(connection)
   }, [])
   
   <ConnectPortal
     apiKey={apiKey}
     userId={userId}
     onConnect={handleConnect}
   />
   ```

---

## Troubleshooting

### Common Issues

#### 1. "Failed to fetch providers"

**Cause:** API key is invalid or Vault API is not running

**Solution:**
- Check API key is correct
- Verify Vault API is running
- Check network connectivity

```tsx
// Test API connection
fetch('https://api.oauth-sdk.dev/health')
  .then(res => res.json())
  .then(data => console.log('API Status:', data))
```

#### 2. OAuth callback not working

**Cause:** Redirect URI mismatch

**Solution:**
- Ensure callback route exists at `/oauth/callback`
- Check redirect URI in provider settings
- Verify URL matches exactly (including protocol)

```tsx
// Callback route must be accessible
// pages/oauth/callback.tsx or app/oauth/callback/page.tsx
```

#### 3. Providers not showing

**Cause:** No providers configured in Vault

**Solution:**
- Add providers in Vault dashboard
- Check provider manifests are loaded
- Verify API response

```tsx
// Debug: Log providers
const { providers } = useOAuth({ apiKey, userId })
console.log('Providers:', providers)
```

#### 4. Styling not applied

**Cause:** CSS not imported

**Solution:**
```tsx
// Add to _app.tsx or layout.tsx
import '@oauth-sdk/react/styles.css'
```

#### 5. TypeScript errors

**Cause:** Missing type definitions

**Solution:**
```bash
npm install --save-dev @types/react @types/react-dom
```

### Debug Mode

Enable debug logging:

```tsx
// Set in development
if (process.env.NODE_ENV === 'development') {
  window.OAUTH_SDK_DEBUG = true
}

<ConnectPortal
  apiKey={apiKey}
  userId={userId}
  onError={(error) => {
    console.error('OAuth Error:', {
      message: error.message,
      code: error.code,
      stack: error.stack
    })
  }}
/>
```

### Getting Help

1. **Check documentation:** https://oauth-sdk.dev/docs
2. **Search issues:** https://github.com/yourusername/universal-oauth-sdk/issues
3. **Ask on Discord:** https://discord.gg/oauth-sdk
4. **Email support:** support@oauth-sdk.dev

---

## Next Steps

- [API Reference](./API.md) - Complete API documentation
- [Examples](./examples/) - Example applications
- [Changelog](./CHANGELOG.md) - Version history
- [Contributing](./CONTRIBUTING.md) - Contribution guidelines

---

## License

MIT © 2025
