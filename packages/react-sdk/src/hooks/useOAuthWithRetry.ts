import { useState, useEffect, useCallback } from 'react'
import type { UseOAuthOptions, UseOAuthReturn, OAuthProvider, Connection } from '../types'
import { retryWithBackoff, OAuthError, ERROR_CODES, parseAPIError } from '../utils/errors'

/**
 * Enhanced OAuth hook with retry logic and better error handling
 */
export function useOAuth(options: UseOAuthOptions): UseOAuthReturn {
  const { apiKey, userId, apiUrl = 'http://localhost:8000' } = options

  const [providers, setProviders] = useState<OAuthProvider[]>([])
  const [connections, setConnections] = useState<Connection[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const [retrying, setRetrying] = useState(false)

  /**
   * Fetch available OAuth providers with retry logic
   */
  const fetchProviders = useCallback(async () => {
    try {
      const data = await retryWithBackoff(async () => {
        const response = await fetch(`${apiUrl}/api/v1/providers`, {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw parseAPIError({ status: response.status, data: errorData })
        }

        return response.json()
      }, 3, 1000)

      setProviders(data.providers || [])
      setError(null)
    } catch (err) {
      const error = err instanceof OAuthError ? err : new OAuthError(
        'Failed to fetch providers',
        ERROR_CODES.API_ERROR,
        undefined,
        true
      )
      setError(error)
      console.error('Error fetching providers:', error)
    }
  }, [apiKey, apiUrl])

  /**
   * Fetch user's existing connections with retry logic
   */
  const fetchConnections = useCallback(async () => {
    try {
      const data = await retryWithBackoff(async () => {
        const response = await fetch(`${apiUrl}/api/v1/tokens?user_id=${userId}`, {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw parseAPIError({ status: response.status, data: errorData })
        }

        return response.json()
      }, 3, 1000)

      setConnections(data.tokens || [])
      setError(null)
    } catch (err) {
      const error = err instanceof OAuthError ? err : new OAuthError(
        'Failed to fetch connections',
        ERROR_CODES.API_ERROR,
        undefined,
        true
      )
      setError(error)
      console.error('Error fetching connections:', error)
    }
  }, [apiKey, apiUrl, userId])

  /**
   * Refresh providers and connections
   */
  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    setRetrying(false)

    try {
      await Promise.all([fetchProviders(), fetchConnections()])
    } finally {
      setLoading(false)
    }
  }, [fetchProviders, fetchConnections])

  /**
   * Retry failed requests
   */
  const retry = useCallback(async () => {
    setRetrying(true)
    await refresh()
    setRetrying(false)
  }, [refresh])

  /**
   * Initiate OAuth connection flow for a provider
   */
  const connect = useCallback(async (providerId: string) => {
    try {
      // Create state parameter with provider and user info
      const state = btoa(JSON.stringify({
        provider: providerId,
        user_id: userId,
        timestamp: Date.now()
      }))

      const data = await retryWithBackoff(async () => {
        const response = await fetch(`${apiUrl}/api/v1/oauth/authorize`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            provider: providerId,
            user_id: userId,
            redirect_uri: `${window.location.origin}/oauth/callback`,
            state
          })
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw parseAPIError({ status: response.status, data: errorData })
        }

        return response.json()
      }, 2, 1000)

      // Redirect to OAuth provider
      if (data.authorization_url) {
        window.location.href = data.authorization_url
      }
    } catch (err) {
      const error = err instanceof OAuthError ? err : new OAuthError(
        'Failed to initiate OAuth flow',
        ERROR_CODES.API_ERROR
      )
      setError(error)
      console.error('Error connecting provider:', error)
      throw error
    }
  }, [apiKey, apiUrl, userId])

  /**
   * Disconnect (revoke) an OAuth connection
   */
  const disconnect = useCallback(async (providerId: string) => {
    try {
      const connection = connections.find(c => c.provider === providerId)
      if (!connection) {
        throw new OAuthError(
          'Connection not found',
          ERROR_CODES.INVALID_PARAMETER
        )
      }

      await retryWithBackoff(async () => {
        const response = await fetch(`${apiUrl}/api/v1/tokens/${connection.id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw parseAPIError({ status: response.status, data: errorData })
        }
      }, 2, 1000)

      // Refresh connections after disconnect
      await fetchConnections()
    } catch (err) {
      const error = err instanceof OAuthError ? err : new OAuthError(
        'Failed to disconnect provider',
        ERROR_CODES.API_ERROR
      )
      setError(error)
      console.error('Error disconnecting provider:', error)
      throw error
    }
  }, [apiKey, apiUrl, connections, fetchConnections])

  // Initial load
  useEffect(() => {
    refresh()
  }, [refresh])

  return {
    providers,
    connections,
    loading,
    error,
    connect,
    disconnect,
    refresh,
    retry,
    retrying
  } as UseOAuthReturn & { retry: () => Promise<void>; retrying: boolean }
}
