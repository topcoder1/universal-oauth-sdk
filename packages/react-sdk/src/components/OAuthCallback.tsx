import { useEffect, useState } from 'react'

interface OAuthCallbackProps {
  apiKey: string
  apiUrl?: string
  onSuccess?: (provider: string, connection: any) => void
  onError?: (error: Error) => void
}

/**
 * OAuthCallback - Handles OAuth redirect callbacks
 * 
 * This component should be rendered on your OAuth callback route
 * (e.g., /oauth/callback)
 * 
 * @example
 * ```tsx
 * // pages/oauth/callback.tsx
 * import { OAuthCallback } from '@oauth-sdk/react'
 * 
 * export default function CallbackPage() {
 *   return (
 *     <OAuthCallback
 *       apiKey="vk_live_..."
 *       onSuccess={(provider, connection) => {
 *         console.log('Connected:', provider)
 *         window.location.href = '/dashboard'
 *       }}
 *       onError={(error) => {
 *         console.error('OAuth failed:', error)
 *         window.location.href = '/error'
 *       }}
 *     />
 *   )
 * }
 * ```
 */
export function OAuthCallback({
  apiKey,
  apiUrl = 'http://localhost:8000',
  onSuccess,
  onError
}: OAuthCallbackProps) {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [error, setError] = useState<Error | null>(null)
  const [provider, setProvider] = useState<string>('')

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Parse URL parameters
        const params = new URLSearchParams(window.location.search)
        const code = params.get('code')
        const state = params.get('state')
        const errorParam = params.get('error')
        const errorDescription = params.get('error_description')

        // Check for OAuth errors
        if (errorParam) {
          throw new Error(errorDescription || errorParam)
        }

        // Validate required parameters
        if (!code) {
          throw new Error('Missing authorization code')
        }

        if (!state) {
          throw new Error('Missing state parameter')
        }

        // Parse state to get provider and user_id
        const stateData = JSON.parse(atob(state))
        const { provider: providerName, user_id } = stateData

        setProvider(providerName)

        // Exchange authorization code for tokens
        const response = await fetch(`${apiUrl}/api/v1/oauth/callback`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            code,
            state,
            provider: providerName,
            user_id,
            redirect_uri: window.location.origin + window.location.pathname
          })
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Failed to exchange authorization code')
        }

        const connection = await response.json()

        // Success!
        setStatus('success')

        if (onSuccess) {
          onSuccess(providerName, connection)
        }
      } catch (err) {
        const error = err as Error
        setError(error)
        setStatus('error')

        if (onError) {
          onError(error)
        }
      }
    }

    handleCallback()
  }, [apiKey, apiUrl, onSuccess, onError])

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        {status === 'loading' && (
          <>
            <div style={styles.spinner}></div>
            <h2 style={styles.title}>Connecting...</h2>
            <p style={styles.message}>
              Please wait while we complete the authorization
            </p>
          </>
        )}

        {status === 'success' && (
          <>
            <div style={styles.successIcon}>✓</div>
            <h2 style={styles.title}>Successfully Connected!</h2>
            <p style={styles.message}>
              You've successfully connected to {provider}
            </p>
            <p style={styles.submessage}>
              Redirecting...
            </p>
          </>
        )}

        {status === 'error' && (
          <>
            <div style={styles.errorIcon}>✕</div>
            <h2 style={styles.title}>Connection Failed</h2>
            <p style={styles.message}>
              {error?.message || 'An error occurred during authorization'}
            </p>
            <button
              onClick={() => window.history.back()}
              style={styles.button}
            >
              Go Back
            </button>
          </>
        )}
      </div>
    </div>
  )
}

const styles = {
  container: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    backgroundColor: '#f8f9fa',
    padding: '20px'
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: '12px',
    padding: '48px 32px',
    maxWidth: '400px',
    width: '100%',
    textAlign: 'center' as const,
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
  },
  spinner: {
    width: '48px',
    height: '48px',
    border: '4px solid #f3f3f3',
    borderTop: '4px solid #007bff',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    margin: '0 auto 24px'
  },
  successIcon: {
    width: '64px',
    height: '64px',
    backgroundColor: '#d4edda',
    color: '#155724',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '32px',
    fontWeight: 'bold',
    margin: '0 auto 24px'
  },
  errorIcon: {
    width: '64px',
    height: '64px',
    backgroundColor: '#f8d7da',
    color: '#721c24',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '32px',
    fontWeight: 'bold',
    margin: '0 auto 24px'
  },
  title: {
    fontSize: '24px',
    fontWeight: '600',
    color: '#333',
    marginBottom: '12px'
  },
  message: {
    fontSize: '16px',
    color: '#666',
    marginBottom: '8px',
    lineHeight: '1.5'
  },
  submessage: {
    fontSize: '14px',
    color: '#999',
    marginTop: '16px'
  },
  button: {
    marginTop: '24px',
    padding: '12px 24px',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'background-color 0.2s'
  }
}
