# @oauth-sdk/react

React components for OAuth token management with embedded UI.

## Installation

```bash
npm install @oauth-sdk/react
```

## Quick Start

```tsx
import { ConnectPortal } from '@oauth-sdk/react'

function App() {
  return (
    <ConnectPortal
      apiKey="vk_live_..."
      userId="user_123"
      onConnect={(provider, connection) => {
        console.log('Connected:', provider.name)
      }}
      theme={{
        primaryColor: '#007bff',
        logo: 'https://yourapp.com/logo.png'
      }}
    />
  )
}
```

## Features

- ✅ **Beautiful UI** - Pre-built, customizable OAuth connection interface
- ✅ **One-line Integration** - Add OAuth to your app in minutes
- ✅ **White-label** - Fully customizable theming
- ✅ **Mobile Responsive** - Works on all devices
- ✅ **TypeScript** - Full type safety
- ✅ **Headless Mode** - Use the `useOAuth` hook for custom UIs

## Components

### ConnectPortal

Main component for OAuth connection management.

```tsx
<ConnectPortal
  apiKey="vk_live_..."
  userId="user_123"
  onConnect={(provider, connection) => {}}
  onDisconnect={(providerId) => {}}
  onError={(error) => {}}
  theme={{
    primaryColor: '#007bff',
    secondaryColor: '#6c757d',
    backgroundColor: '#f8f9fa',
    textColor: '#333',
    borderRadius: '8px',
    fontFamily: 'Inter, sans-serif',
    logo: 'https://yourapp.com/logo.png'
  }}
  apiUrl="http://localhost:8000"
  category="social"
  providers={['google', 'github']}
  className="my-connect-portal"
/>
```

### useOAuth Hook (Headless Mode)

For building custom UIs:

```tsx
import { useOAuth } from '@oauth-sdk/react'

function CustomUI() {
  const {
    providers,
    connections,
    loading,
    error,
    connect,
    disconnect,
    refresh
  } = useOAuth({
    apiKey: 'vk_live_...',
    userId: 'user_123',
    apiUrl: 'http://localhost:8000'
  })

  return (
    <div>
      {providers.map(provider => (
        <button key={provider.id} onClick={() => connect(provider.id)}>
          Connect {provider.name}
        </button>
      ))}
    </div>
  )
}
```

## Props

### ConnectPortalProps

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `apiKey` | `string` | ✅ | API key for Vault authentication |
| `userId` | `string` | ✅ | User ID for the current user |
| `onConnect` | `(provider, connection) => void` | ❌ | Callback when provider connected |
| `onDisconnect` | `(providerId) => void` | ❌ | Callback when provider disconnected |
| `onError` | `(error) => void` | ❌ | Callback when error occurs |
| `theme` | `ConnectPortalTheme` | ❌ | Custom theme configuration |
| `apiUrl` | `string` | ❌ | Vault API base URL (default: localhost:8000) |
| `category` | `string` | ❌ | Filter providers by category |
| `providers` | `string[]` | ❌ | Show only specific providers |
| `className` | `string` | ❌ | Custom CSS class name |

### ConnectPortalTheme

| Property | Type | Description |
|----------|------|-------------|
| `primaryColor` | `string` | Primary brand color |
| `secondaryColor` | `string` | Secondary color |
| `backgroundColor` | `string` | Background color |
| `textColor` | `string` | Text color |
| `borderRadius` | `string` | Border radius (e.g., '8px') |
| `fontFamily` | `string` | Font family |
| `logo` | `string` | Logo URL |

## Examples

### Basic Usage

```tsx
<ConnectPortal
  apiKey="vk_live_..."
  userId="user_123"
/>
```

### Custom Theme

```tsx
<ConnectPortal
  apiKey="vk_live_..."
  userId="user_123"
  theme={{
    primaryColor: '#6366f1',
    borderRadius: '12px',
    fontFamily: 'Inter, sans-serif'
  }}
/>
```

### Filter Providers

```tsx
<ConnectPortal
  apiKey="vk_live_..."
  userId="user_123"
  providers={['google', 'github', 'microsoft']}
/>
```

### With Callbacks

```tsx
<ConnectPortal
  apiKey="vk_live_..."
  userId="user_123"
  onConnect={(provider, connection) => {
    console.log(`Connected to ${provider.name}`)
    // Update your app state
  }}
  onDisconnect={(providerId) => {
    console.log(`Disconnected from ${providerId}`)
  }}
  onError={(error) => {
    console.error('OAuth error:', error)
  }}
/>
```

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm test
```

## Requirements

- React 18+
- Vault API running (see [universal-oauth-sdk](https://github.com/yourusername/universal-oauth-sdk))

## License

MIT

## Links

- [Documentation](https://oauth-sdk.dev/docs)
- [GitHub](https://github.com/yourusername/universal-oauth-sdk)
- [Issues](https://github.com/yourusername/universal-oauth-sdk/issues)
