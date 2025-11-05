/**
 * OAuth SDK React - Type Definitions
 */

export interface OAuthProvider {
  id: string
  name: string
  icon?: string
  category?: string
  description?: string
  authUrl?: string
  tokenUrl?: string
  scopes?: string[]
}

export interface Connection {
  id: string
  provider: string
  userId: string
  status: 'active' | 'expired' | 'error'
  createdAt: string
  expiresAt?: string
  metadata?: Record<string, any>
}

export interface ConnectPortalTheme {
  primaryColor?: string
  secondaryColor?: string
  backgroundColor?: string
  textColor?: string
  borderRadius?: string
  fontFamily?: string
  logo?: string
}

export interface ConnectPortalProps {
  /**
   * API key for authentication with the Vault API
   */
  apiKey: string

  /**
   * User ID for the current user
   */
  userId: string

  /**
   * Callback function when a provider is successfully connected
   */
  onConnect?: (provider: OAuthProvider, connection: Connection) => void

  /**
   * Callback function when a provider is disconnected
   */
  onDisconnect?: (provider: string) => void

  /**
   * Callback function when an error occurs
   */
  onError?: (error: Error) => void

  /**
   * Custom theme configuration
   */
  theme?: ConnectPortalTheme

  /**
   * Vault API base URL (default: http://localhost:8000)
   */
  apiUrl?: string

  /**
   * Filter providers by category
   */
  category?: string

  /**
   * Show only specific providers
   */
  providers?: string[]

  /**
   * Custom CSS class name
   */
  className?: string
}

export interface UseOAuthOptions {
  apiKey: string
  userId: string
  apiUrl?: string
}

export interface UseOAuthReturn {
  providers: OAuthProvider[]
  connections: Connection[]
  loading: boolean
  error: Error | null
  connect: (providerId: string) => Promise<void>
  disconnect: (providerId: string) => Promise<void>
  refresh: () => Promise<void>
}
