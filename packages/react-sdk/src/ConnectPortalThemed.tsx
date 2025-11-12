import { useEffect, useRef } from 'react'
import type { Theme } from './types/theme'
import { ThemeProvider, useTheme, useThemeVariables } from './context/ThemeContext'
import { ProviderList } from './components/ProviderListTailwind'
import { useOAuth } from './hooks/useOAuth'

export interface ConnectPortalThemedProps {
  apiKey: string
  userId: string
  apiUrl?: string
  theme?: Partial<Theme>
  category?: string
  providers?: string[]
  className?: string
  onConnect?: (provider: any, connection: any) => void
  onDisconnect?: (providerId: string) => void
  onError?: (error: Error) => void
  showThemeToggle?: boolean
}

function ConnectPortalContent({
  apiKey,
  userId,
  apiUrl,
  category,
  providers: providerFilter,
  className,
  onConnect,
  onDisconnect,
  onError,
  showThemeToggle = false
}: Omit<ConnectPortalThemedProps, 'theme'>) {
  const containerRef = useRef<HTMLDivElement>(null)
  const { theme, toggleMode, resolvedMode } = useTheme()
  const cssVars = useThemeVariables()

  const {
    providers,
    connections,
    loading,
    error,
    connect,
    disconnect,
    refresh
  } = useOAuth({ apiKey, userId, apiUrl })

  // Apply theme CSS variables to container
  useEffect(() => {
    if (!containerRef.current) return

    Object.entries(cssVars).forEach(([key, value]) => {
      containerRef.current!.style.setProperty(key, value)
    })
  }, [cssVars])

  // Handle errors
  useEffect(() => {
    if (error && onError) {
      onError(error)
    }
  }, [error, onError])

  // Filter providers
  const filteredProviders = providers.filter(provider => {
    if (category && provider.category !== category) return false
    if (providerFilter && !providerFilter.includes(provider.id)) return false
    return true
  })

  const handleConnect = async (providerId: string) => {
    try {
      await connect(providerId)
      const provider = providers.find(p => p.id === providerId)
      const connection = connections.find(c => c.provider === providerId)
      if (provider && connection && onConnect) {
        onConnect(provider, connection)
      }
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

  return (
    <div
      ref={containerRef}
      className={`oauth-portal oauth-theme-${resolvedMode} oauth-variant-${theme.variant || 'default'} ${className || ''}`}
      style={{
        fontFamily: theme.typography?.fontFamily,
        backgroundColor: theme.colors?.background,
        borderRadius: theme.spacing?.borderRadius,
        padding: theme.spacing?.padding?.lg
      }}
    >
      {/* Header with optional theme toggle */}
      <div className="oauth-portal-header" style={{ marginBottom: theme.spacing?.gap?.lg }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {theme.branding?.logo && (
            <img
              src={theme.branding.logo}
              alt={theme.branding.logoAlt || 'Logo'}
              style={{ height: '32px', marginBottom: theme.spacing?.gap?.md }}
            />
          )}
          
          {showThemeToggle && (
            <button
              onClick={toggleMode}
              className="oauth-theme-toggle"
              style={{
                background: theme.colors?.surface,
                border: `1px solid ${theme.colors?.border}`,
                borderRadius: theme.spacing?.borderRadius,
                padding: `${theme.spacing?.padding?.sm} ${theme.spacing?.padding?.md}`,
                color: theme.colors?.text,
                cursor: 'pointer',
                fontSize: theme.typography?.fontSize?.sm,
                transition: `all ${theme.animations?.duration?.normal}`
              }}
              aria-label="Toggle theme"
            >
              {resolvedMode === 'light' ? '🌙 Dark' : '☀️ Light'}
            </button>
          )}
        </div>

        <h2
          className="oauth-portal-title"
          style={{
            fontSize: theme.typography?.fontSize?.['2xl'],
            fontWeight: theme.typography?.fontWeight?.semibold,
            color: theme.colors?.text,
            textAlign: 'center',
            marginTop: theme.spacing?.gap?.md,
            marginBottom: theme.spacing?.gap?.lg
          }}
        >
          Connect Your Accounts
        </h2>
      </div>

      {/* Error banner */}
      {error && (
        <div
          className="oauth-error-banner"
          style={{
            backgroundColor: theme.colors?.errorBg,
            border: `1px solid ${theme.colors?.error}`,
            color: theme.colors?.error,
            padding: theme.spacing?.padding?.md,
            borderRadius: theme.spacing?.borderRadius,
            marginBottom: theme.spacing?.gap?.lg,
            display: 'flex',
            alignItems: 'start',
            gap: theme.spacing?.gap?.sm
          }}
        >
          <svg
            style={{ width: '20px', height: '20px', flexShrink: 0, marginTop: '2px' }}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <strong style={{ fontWeight: theme.typography?.fontWeight?.medium }}>Error:</strong>
            <span style={{ marginLeft: theme.spacing?.gap?.xs }}>{error.message}</span>
            <button
              onClick={refresh}
              style={{
                marginLeft: theme.spacing?.gap?.md,
                background: 'transparent',
                border: 'none',
                color: theme.colors?.error,
                textDecoration: 'underline',
                cursor: 'pointer',
                fontSize: theme.typography?.fontSize?.sm
              }}
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Provider list */}
      <ProviderList
        providers={filteredProviders}
        connections={connections}
        loading={loading}
        onConnect={handleConnect}
        onDisconnect={handleDisconnect}
      />

      {/* Footer */}
      {theme.branding?.showPoweredBy !== false && (
        <div
          className="oauth-portal-footer"
          style={{
            marginTop: theme.spacing?.gap?.lg,
            paddingTop: theme.spacing?.padding?.md,
            borderTop: `1px solid ${theme.colors?.border}`,
            textAlign: 'center',
            fontSize: theme.typography?.fontSize?.xs,
            color: theme.colors?.textMuted
          }}
        >
          {theme.branding?.customFooter || (
            <>
              Powered by{' '}
              <a
                href="https://oauth-sdk.dev"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: theme.colors?.primary, textDecoration: 'none' }}
              >
                OAuth SDK
              </a>
            </>
          )}
        </div>
      )}
    </div>
  )
}

export function ConnectPortalThemed(props: ConnectPortalThemedProps) {
  const { theme, ...rest } = props

  return (
    <ThemeProvider theme={theme}>
      <ConnectPortalContent {...rest} />
    </ThemeProvider>
  )
}
