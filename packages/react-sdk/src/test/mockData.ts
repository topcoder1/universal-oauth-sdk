import type { OAuthProvider, Connection } from '../types'

export const mockProviders: OAuthProvider[] = [
  {
    id: 'google',
    name: 'Google',
    icon: 'https://example.com/google.png',
    category: 'social',
    description: 'Connect your Google account',
    authUrl: 'https://accounts.google.com/o/oauth2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    scopes: ['email', 'profile']
  },
  {
    id: 'github',
    name: 'GitHub',
    icon: 'https://example.com/github.png',
    category: 'developer',
    description: 'Connect your GitHub account',
    authUrl: 'https://github.com/login/oauth/authorize',
    tokenUrl: 'https://github.com/login/oauth/access_token',
    scopes: ['user', 'repo']
  },
  {
    id: 'microsoft',
    name: 'Microsoft',
    icon: 'https://example.com/microsoft.png',
    category: 'productivity',
    description: 'Connect your Microsoft account',
    authUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    tokenUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
    scopes: ['User.Read']
  }
]

export const mockConnections: Connection[] = [
  {
    id: 'conn_1',
    provider: 'google',
    userId: 'user_123',
    status: 'active',
    createdAt: '2025-11-01T00:00:00Z',
    expiresAt: '2025-12-01T00:00:00Z',
    metadata: {}
  }
]

export const mockApiResponses = {
  providers: {
    providers: mockProviders
  },
  connections: {
    tokens: mockConnections
  },
  authorize: {
    authorization_url: 'https://provider.com/oauth/authorize?client_id=123'
  }
}
