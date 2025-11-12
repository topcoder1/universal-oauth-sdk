# @oauth-sdk/react - API Reference

Complete API documentation for the OAuth SDK React components.

---

## Table of Contents

- [Installation](#installation)
- [Components](#components)
  - [ConnectPortal](#connectportal)
  - [OAuthCallback](#oauthcallback)
  - [Toast](#toast)
- [Hooks](#hooks)
  - [useOAuth](#useoauth)
  - [useToast](#usetoast)
- [Types](#types)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## Installation

```bash
npm install @oauth-sdk/react
```

### Import Styles

```tsx
import '@oauth-sdk/react/styles.css'
```

---

## Components

### ConnectPortal

Main component for displaying OAuth connection interface.

#### Props

```tsx
interface ConnectPortalProps {
  // Required
  apiKey: string
  userId: string
  
  // Optional
  apiUrl?: string
  theme?: ConnectPortalTheme
  category?: string
  providers?: string[]
  className?: string
  
  // Callbacks
  onConnect?: (provider: OAuthProvider, connection: Connection) => void
  onDisconnect?: (providerId: string) => void
  onError?: (error: Error) => void
}
```

#### Required Props

**`apiKey`** `string`
- Your Vault API key
- Format: `vk_live_...` or `vk_test_...`
- Get from dashboard

**`userId`** `string`
- Unique identifier for the current user
- Used to associate OAuth connections with users

#### Optional Props

**`apiUrl`** `string`
- Vault API base URL
- Default: `http://localhost:8000`
- Production: `https://api.oauth-sdk.dev`

**`theme`** `ConnectPortalTheme`
- Customize colors, fonts, logo
- See [Theme Configuration](#theme-configuration)

**`category`** `string`
- Filter providers by category
- Options: `'social'`, `'productivity'`, `'crm'`, `'finance'`, etc.

**`providers`** `string[]`
- Show only specific providers
- Example: `['google', 'github', 'microsoft']`

**`className`** `string`
- Custom CSS class for the container

#### Callbacks

**`onConnect`** `(provider, connection) => void`
- Called when provider is successfully connected
- `provider`: Provider information
- `connection`: Connection details with tokens

**`onDisconnect`** `(providerId) => void`
- Called when provider is disconnected
- `providerId`: ID of disconnected provider

**`onError`** `(error) => void`
- Called when an error occurs
- `error`: Error object with message and code

#### Theme Configuration

```tsx
interface ConnectPortalTheme {
  primaryColor?: string        // Brand color (default: '#007bff')
  secondaryColor?: string      // Secondary color
  backgroundColor?: string     // Background color (default: '#f8f9fa')
  textColor?: string          // Text color (default: '#333')
  borderRadius?: string       // Border radius (default: '12px')
  fontFamily?: string         // Font family
  logo?: string              // Logo URL
}
```

#### Example

```tsx
<ConnectPortal
  apiKey="vk_live_abc123"
  userId="user_123"
  apiUrl="https://api.oauth-sdk.dev"
  category="social"
  providers={['google', 'github']}
  theme={{
    primaryColor: '#6366f1',
    logo: 'https://yourapp.com/logo.png',
    borderRadius: '16px'
  }}
  onConnect={(provider, connection) => {
    console.log(`Connected to ${provider.name}`)
    // Save connection ID to your database
    saveConnection(connection.id)
  }}
  onDisconnect={(providerId) => {
    console.log(`Disconnected from ${providerId}`)
  }}
  onError={(error) => {
    console.error('OAuth error:', error)
    alert(error.message)
  }}
/>
```

---

### OAuthCallback

Component for handling OAuth redirect callbacks.

#### Props

```tsx
interface OAuthCallbackProps {
  // Required
  apiKey: string
  
  // Optional
  apiUrl?: string
  
  // Callbacks
  onSuccess?: (provider: string, connection: any) => void
  onError?: (error: Error) => void
}
```

#### Required Props

**`apiKey`** `string`
- Your Vault API key

#### Optional Props

**`apiUrl`** `string`
- Vault API base URL
- Default: `http://localhost:8000`

#### Callbacks

**`onSuccess`** `(provider, connection) => void`
- Called when OAuth flow completes successfully
- `provider`: Provider name (e.g., 'google')
- `connection`: Connection object with tokens

**`onError`** `(error) => void`
- Called when OAuth flow fails
- `error`: Error object

#### Example

```tsx
// pages/oauth/callback.tsx
import { OAuthCallback } from '@oauth-sdk/react'

export default function CallbackPage() {
  return (
    <OAuthCallback
      apiKey="vk_live_abc123"
      onSuccess={(provider, connection) => {
        console.log('Success:', provider)
        // Redirect to dashboard
        window.location.href = '/dashboard'
      }}
      onError={(error) => {
        console.error('Failed:', error)
        // Redirect to error page
        window.location.href = '/error'
      }}
    />
  )
}
```

---

### Toast

Toast notification component.

#### Props

```tsx
interface ToastProps {
  message: string
  type: 'success' | 'error' | 'info' | 'warning'
  duration?: number
  onClose: () => void
}
```

#### Example

```tsx
<Toast
  message="Successfully connected!"
  type="success"
  duration={5000}
  onClose={() => console.log('Toast closed')}
/>
```

---

## Hooks

### useOAuth

Main hook for OAuth operations.

#### Signature

```tsx
function useOAuth(options: UseOAuthOptions): UseOAuthReturn
```

#### Options

```tsx
interface UseOAuthOptions {
  apiKey: string
  userId: string
  apiUrl?: string
}
```

#### Return Value

```tsx
interface UseOAuthReturn {
  // Data
  providers: OAuthProvider[]
  connections: Connection[]
  
  // State
  loading: boolean
  error: Error | null
  retrying: boolean
  
  // Actions
  connect: (providerId: string) => Promise<void>
  disconnect: (providerId: string) => Promise<void>
  refresh: () => Promise<void>
  retry: () => Promise<void>
}
```

#### Example

```tsx
import { useOAuth } from '@oauth-sdk/react'

function MyComponent() {
  const {
    providers,
    connections,
    loading,
    error,
    connect,
    disconnect,
    retry
  } = useOAuth({
    apiKey: 'vk_live_abc123',
    userId: 'user_123'
  })

  if (loading) return <div>Loading...</div>
  if (error) return <button onClick={retry}>Retry</button>

  return (
    <div>
      {providers.map(provider => (
        <button
          key={provider.id}
          onClick={() => connect(provider.id)}
        >
          Connect {provider.name}
        </button>
      ))}
    </div>
  )
}
```

---

### useToast

Hook for managing toast notifications.

#### Signature

```tsx
function useToast(): UseToastReturn
```

#### Return Value

```tsx
interface UseToastReturn {
  toasts: ToastMessage[]
  addToast: (message: string, type: ToastType) => string
  removeToast: (id: string) => void
  success: (message: string) => string
  error: (message: string) => string
  info: (message: string) => string
  warning: (message: string) => string
}
```

#### Example

```tsx
import { useToast, ToastContainer } from '@oauth-sdk/react'

function MyComponent() {
  const { toasts, removeToast, success, error } = useToast()

  const handleConnect = async () => {
    try {
      await connectProvider()
      success('Successfully connected!')
    } catch (err) {
      error('Failed to connect')
    }
  }

  return (
    <>
      <button onClick={handleConnect}>Connect</button>
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </>
  )
}
```

---

## Types

### OAuthProvider

```tsx
interface OAuthProvider {
  id: string
  name: string
  icon?: string
  category?: string
  description?: string
  authUrl?: string
  tokenUrl?: string
  scopes?: string[]
}
```

### Connection

```tsx
interface Connection {
  id: string
  provider: string
  userId: string
  status: 'active' | 'expired' | 'error'
  createdAt: string
  expiresAt?: string
  metadata?: Record<string, any>
}
```

### OAuthError

```tsx
class OAuthError extends Error {
  code: string
  statusCode?: number
  retryable: boolean
}
```

### Error Codes

```tsx
const ERROR_CODES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT: 'TIMEOUT',
  INVALID_GRANT: 'INVALID_GRANT',
  ACCESS_DENIED: 'ACCESS_DENIED',
  API_ERROR: 'API_ERROR',
  RATE_LIMIT: 'RATE_LIMIT',
  SERVER_ERROR: 'SERVER_ERROR',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  // ... more codes
}
```

---

## Error Handling

### Automatic Retry

The SDK automatically retries failed requests with exponential backoff:

```tsx
// Retries: 1s, 2s, 4s (max 3 attempts)
const data = await retryWithBackoff(fetchData, 3, 1000)
```

### Manual Retry

```tsx
const { error, retry, retrying } = useOAuth({ ... })

if (error) {
  return (
    <button onClick={retry} disabled={retrying}>
      {retrying ? 'Retrying...' : 'Retry'}
    </button>
  )
}
```

### User-Friendly Messages

```tsx
import { getUserFriendlyMessage } from '@oauth-sdk/react/utils'

try {
  await connect('google')
} catch (error) {
  const message = getUserFriendlyMessage(error)
  alert(message) // "Unable to connect. Please check your internet connection."
}
```

### Error Callbacks

```tsx
<ConnectPortal
  apiKey="..."
  userId="..."
  onError={(error) => {
    if (error.code === 'RATE_LIMIT') {
      alert('Too many requests. Please wait.')
    } else if (error.retryable) {
      alert('Error occurred. Retrying...')
    } else {
      alert(error.message)
    }
  }}
/>
```

---

## Examples

### Basic Usage

```tsx
import { ConnectPortal } from '@oauth-sdk/react'
import '@oauth-sdk/react/styles.css'

function App() {
  return (
    <ConnectPortal
      apiKey="vk_live_abc123"
      userId="user_123"
    />
  )
}
```

### With Custom Theme

```tsx
<ConnectPortal
  apiKey="vk_live_abc123"
  userId="user_123"
  theme={{
    primaryColor: '#6366f1',
    backgroundColor: '#ffffff',
    borderRadius: '16px',
    fontFamily: 'Inter, sans-serif',
    logo: 'https://yourapp.com/logo.png'
  }}
/>
```

### With Callbacks

```tsx
<ConnectPortal
  apiKey="vk_live_abc123"
  userId="user_123"
  onConnect={(provider, connection) => {
    // Save to database
    fetch('/api/connections', {
      method: 'POST',
      body: JSON.stringify({
        userId: 'user_123',
        provider: provider.id,
        connectionId: connection.id
      })
    })
    
    // Show success message
    toast.success(`Connected to ${provider.name}!`)
  }}
  onDisconnect={(providerId) => {
    // Remove from database
    fetch(`/api/connections/${providerId}`, {
      method: 'DELETE'
    })
    
    toast.info('Disconnected')
  }}
  onError={(error) => {
    console.error(error)
    toast.error(error.message)
  }}
/>
```

### With Filters

```tsx
// Show only social providers
<ConnectPortal
  apiKey="vk_live_abc123"
  userId="user_123"
  category="social"
/>

// Show specific providers
<ConnectPortal
  apiKey="vk_live_abc123"
  userId="user_123"
  providers={['google', 'github', 'microsoft']}
/>
```

### Headless Mode

```tsx
import { useOAuth } from '@oauth-sdk/react'

function CustomUI() {
  const {
    providers,
    connections,
    loading,
    connect,
    disconnect
  } = useOAuth({
    apiKey: 'vk_live_abc123',
    userId: 'user_123'
  })

  if (loading) return <Spinner />

  return (
    <div className="my-custom-ui">
      {providers.map(provider => {
        const isConnected = connections.some(
          c => c.provider === provider.id
        )

        return (
          <div key={provider.id}>
            <img src={provider.icon} alt={provider.name} />
            <h3>{provider.name}</h3>
            {isConnected ? (
              <button onClick={() => disconnect(provider.id)}>
                Disconnect
              </button>
            ) : (
              <button onClick={() => connect(provider.id)}>
                Connect
              </button>
            )}
          </div>
        )
      })}
    </div>
  )
}
```

### With Toast Notifications

```tsx
import { ConnectPortal, useToast, ToastContainer } from '@oauth-sdk/react'

function App() {
  const { toasts, removeToast, success, error } = useToast()

  return (
    <>
      <ConnectPortal
        apiKey="vk_live_abc123"
        userId="user_123"
        onConnect={(provider) => {
          success(`Connected to ${provider.name}!`)
        }}
        onError={(err) => {
          error(err.message)
        }}
      />
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </>
  )
}
```

---

## Best Practices

### 1. Store API Keys Securely

```tsx
// ❌ Don't hardcode API keys
<ConnectPortal apiKey="vk_live_abc123" ... />

// ✅ Use environment variables
<ConnectPortal apiKey={process.env.NEXT_PUBLIC_OAUTH_API_KEY} ... />
```

### 2. Handle Errors Gracefully

```tsx
<ConnectPortal
  apiKey="..."
  userId="..."
  onError={(error) => {
    // Log to error tracking service
    Sentry.captureException(error)
    
    // Show user-friendly message
    toast.error(getUserFriendlyMessage(error))
  }}
/>
```

### 3. Save Connection IDs

```tsx
<ConnectPortal
  apiKey="..."
  userId="..."
  onConnect={(provider, connection) => {
    // Save connection ID to your database
    await saveToDatabase({
      userId: currentUser.id,
      provider: provider.id,
      connectionId: connection.id,
      expiresAt: connection.expiresAt
    })
  }}
/>
```

### 4. Implement Retry Logic

```tsx
const { error, retry, retrying } = useOAuth({ ... })

if (error && error.retryable) {
  return (
    <div>
      <p>Error: {error.message}</p>
      <button onClick={retry} disabled={retrying}>
        {retrying ? 'Retrying...' : 'Try Again'}
      </button>
    </div>
  )
}
```

### 5. Use TypeScript

```tsx
import type { OAuthProvider, Connection } from '@oauth-sdk/react'

const handleConnect = (
  provider: OAuthProvider,
  connection: Connection
) => {
  // Full type safety
  console.log(provider.name)
  console.log(connection.id)
}
```

---

## Support

- **Documentation:** https://oauth-sdk.dev/docs
- **GitHub:** https://github.com/yourusername/universal-oauth-sdk
- **Issues:** https://github.com/yourusername/universal-oauth-sdk/issues
- **Discord:** https://discord.gg/oauth-sdk

---

## License

MIT © 2025
