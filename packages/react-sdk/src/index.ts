/**
 * @oauth-sdk/react
 * 
 * React components for OAuth token management with embedded UI
 * 
 * @example
 * ```tsx
 * import { ConnectPortal } from '@oauth-sdk/react'
 * 
 * function App() {
 *   return (
 *     <ConnectPortal
 *       apiKey="vk_live_..."
 *       userId="user_123"
 *       onConnect={(provider, connection) => {
 *         console.log('Connected:', provider.name)
 *       }}
 *     />
 *   )
 * }
 * ```
 */

// Main component
export { ConnectPortal } from './ConnectPortal'

// Hooks
export { useOAuth } from './hooks/useOAuth'

// Components (for advanced usage)
export { ProviderList } from './components/ProviderList'
export { OAuthCallback } from './components/OAuthCallback'

// Types
export type {
  OAuthProvider,
  Connection,
  ConnectPortalTheme,
  ConnectPortalProps,
  UseOAuthOptions,
  UseOAuthReturn
} from './types'
