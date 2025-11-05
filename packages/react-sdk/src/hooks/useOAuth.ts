import { useState, useEffect, useCallback } from 'react'
import type { UseOAuthOptions, UseOAuthReturn, OAuthProvider, Connection } from '../types'

/**
 * Custom hook for OAuth operations
 * Handles provider fetching, connection management, and OAuth flow
 */
export function useOAuth(options: UseOAuthOptions): UseOAuthReturn {
  const { apiKey, userId, apiUrl = 'http://localhost:8000' } = options

  const [providers, setProviders] = useState<OAuthProvider[]>([])
  const [connections, setConnections] = useState<Connection[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  /**
   * Fetch available OAuth providers from the Vault API
   */
  const fetchProviders = useCallback(async () => {
    try {
      const response = await fetch(`${apiUrl}/api/v1/providers`, {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch providers: ${response.statusText}`)
      }

      const data = await response.json()
      setProviders(data.providers || [])
    } catch (err) {
      setError(err as Error)
      console.error('Error fetching providers:', err)
    }
  }, [apiKey, apiUrl])

  /**
   * Fetch user's existing connections
   */
  const fetchConnections = useCallback(async () => {
    try {
      const response = await fetch(`${apiUrl}/api/v1/tokens?user_id=${userId}`, {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch connections: ${response.statusText}`)
      }

      const data = await response.json()
      setConnections(data.tokens || [])
    } catch (err) {
      setError(err as Error)
      console.error('Error fetching connections:', err)
    }
  }, [apiKey, apiUrl, userId])

  /**
   * Refresh providers and connections
   */
  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      await Promise.all([fetchProviders(), fetchConnections()])
    } finally {
      setLoading(false)
    }
  }, [fetchProviders, fetchConnections])

  /**
   * Initiate OAuth connection flow for a provider
   */
  const connect = useCallback(async (providerId: string) => {
    try {
      // Generate OAuth authorization URL
      const response = await fetch(`${apiUrl}/api/v1/oauth/authorize`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          provider: providerId,
          user_id: userId,
          redirect_uri: `${window.location.origin}/oauth/callback`
        })
      })

      if (!response.ok) {
        throw new Error(`Failed to initiate OAuth: ${response.statusText}`)
      }

      const data = await response.json()
      
      // Redirect to OAuth provider
      if (data.authorization_url) {
        window.location.href = data.authorization_url
      }
    } catch (err) {
      setError(err as Error)
      console.error('Error connecting provider:', err)
      throw err
    }
  }, [apiKey, apiUrl, userId])

  /**
   * Disconnect (revoke) an OAuth connection
   */
  const disconnect = useCallback(async (providerId: string) => {
    try {
      const connection = connections.find(c => c.provider === providerId)
      if (!connection) {
        throw new Error('Connection not found')
      }

      const response = await fetch(`${apiUrl}/api/v1/tokens/${connection.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to disconnect: ${response.statusText}`)
      }

      // Refresh connections after disconnect
      await fetchConnections()
    } catch (err) {
      setError(err as Error)
      console.error('Error disconnecting provider:', err)
      throw err
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
    refresh
  }
}
