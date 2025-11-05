import React from 'react'
import { useOAuth } from './hooks/useOAuth'
import { ProviderList } from './components/ProviderList'
import type { ConnectPortalProps } from './types'

/**
 * ConnectPortal - Main OAuth connection component
 * 
 * Provides a beautiful embedded UI for managing OAuth connections
 * 
 * @example
 * ```tsx
 * <ConnectPortal
 *   apiKey="vk_live_..."
 *   userId="user_123"
 *   onConnect={(provider, connection) => console.log('Connected:', provider)}
 *   theme={{
 *     primaryColor: '#007bff',
 *     logo: 'https://yourapp.com/logo.png'
 *   }}
 * />
 * ```
 */
export function ConnectPortal({
  apiKey,
  userId,
  onConnect, // TODO: Will be used when OAuth callback handling is implemented
  onDisconnect,
  onError,
  theme,
  apiUrl = 'http://localhost:8000',
  category,
  providers: providerFilter,
  className
}: ConnectPortalProps) {
  // Suppress unused variable warning for onConnect (will be used in callback handler)
  void onConnect
  const {
    providers,
    connections,
    loading,
    error,
    connect,
    disconnect
  } = useOAuth({ apiKey, userId, apiUrl })

  // Handle errors
  React.useEffect(() => {
    if (error && onError) {
      onError(error)
    }
  }, [error, onError])

  // Filter providers if needed
  const filteredProviders = React.useMemo(() => {
    let filtered = providers

    if (category) {
      filtered = filtered.filter(p => p.category === category)
    }

    if (providerFilter && providerFilter.length > 0) {
      filtered = filtered.filter(p => providerFilter.includes(p.id))
    }

    return filtered
  }, [providers, category, providerFilter])

  // Handle connect
  const handleConnect = async (providerId: string) => {
    try {
      await connect(providerId)
      
      // Note: onConnect will be called after OAuth callback completes
      // This is just initiating the flow
    } catch (err) {
      if (onError) {
        onError(err as Error)
      }
    }
  }

  // Handle disconnect
  const handleDisconnect = async (providerId: string) => {
    try {
      await disconnect(providerId)
      
      if (onDisconnect) {
        onDisconnect(providerId)
      }
    } catch (err) {
      if (onError) {
        onError(err as Error)
      }
    }
  }

  // Apply theme
  const containerStyle: React.CSSProperties = {
    fontFamily: theme?.fontFamily || 'system-ui, -apple-system, sans-serif',
    backgroundColor: theme?.backgroundColor || '#f8f9fa',
    borderRadius: theme?.borderRadius || '8px',
    padding: '20px',
    ...(theme?.primaryColor && {
      '--primary-color': theme.primaryColor
    } as any)
  }

  return (
    <div className={className} style={containerStyle}>
      {theme?.logo && (
        <div style={styles.header}>
          <img src={theme.logo} alt="Logo" style={styles.logo} />
        </div>
      )}

      <div style={styles.content}>
        <h2 style={{
          ...styles.title,
          color: theme?.textColor || '#333'
        }}>
          Connect Your Accounts
        </h2>

        {error && (
          <div style={styles.errorBanner}>
            <strong>Error:</strong> {error.message}
          </div>
        )}

        <ProviderList
          providers={filteredProviders}
          connections={connections}
          onConnect={handleConnect}
          onDisconnect={handleDisconnect}
          loading={loading}
        />
      </div>
    </div>
  )
}

const styles = {
  header: {
    textAlign: 'center' as const,
    marginBottom: '24px',
    paddingBottom: '16px',
    borderBottom: '1px solid #e0e0e0'
  },
  logo: {
    maxHeight: '48px',
    maxWidth: '200px'
  },
  content: {
    // Content styles
  },
  title: {
    fontSize: '24px',
    fontWeight: '600',
    marginBottom: '24px',
    textAlign: 'center' as const
  },
  errorBanner: {
    backgroundColor: '#f8d7da',
    color: '#721c24',
    padding: '12px 16px',
    borderRadius: '6px',
    marginBottom: '20px',
    border: '1px solid #f5c6cb'
  }
}
