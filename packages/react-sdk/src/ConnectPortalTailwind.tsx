import React from 'react'
import { useOAuth } from './hooks/useOAuth'
import { ProviderList } from './components/ProviderListTailwind'
import type { ConnectPortalProps } from './types'

export function ConnectPortal({
  apiKey,
  userId,
  onConnect,
  onDisconnect,
  onError,
  theme,
  apiUrl = 'http://localhost:8000',
  category,
  providers: providerFilter,
  className
}: ConnectPortalProps) {
  // Suppress unused variable warning
  void onConnect

  const {
    providers,
    connections,
    loading,
    error,
    connect,
    disconnect
  } = useOAuth({ apiKey, userId, apiUrl })

  React.useEffect(() => {
    if (error && onError) {
      onError(error)
    }
  }, [error, onError])

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

  const handleConnect = async (providerId: string) => {
    try {
      await connect(providerId)
    } catch (err) {
      if (onError) {
        onError(err as Error)
      }
    }
  }

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

  const primaryColor = theme?.primaryColor || '#007bff'
  const backgroundColor = theme?.backgroundColor || '#f8f9fa'
  const textColor = theme?.textColor || '#333'
  const borderRadius = theme?.borderRadius || '12px'
  const fontFamily = theme?.fontFamily || 'system-ui, -apple-system, sans-serif'

  return (
    <div
      className={`${className || ''} animate-fade-in`}
      style={{
        fontFamily,
        backgroundColor,
        borderRadius,
        padding: '20px',
        '--primary-color': primaryColor,
        '--text-color': textColor
      } as React.CSSProperties}
    >
      {theme?.logo && (
        <div className="text-center mb-6 pb-4 border-b border-gray-200 animate-slide-up">
          <img
            src={theme.logo}
            alt="Logo"
            className="max-h-12 max-w-[200px] mx-auto"
          />
        </div>
      )}

      <div>
        <h2
          className="text-2xl font-semibold text-center mb-6 animate-slide-up"
          style={{ color: textColor, animationDelay: '100ms' }}
        >
          Connect Your Accounts
        </h2>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-5 animate-slide-up" style={{ animationDelay: '200ms' }}>
            <div className="flex items-start">
              <svg className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div>
                <strong className="font-medium">Error:</strong>
                <span className="ml-1">{error.message}</span>
              </div>
            </div>
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
