import type { OAuthProvider, Connection } from '../types'

interface ProviderListProps {
  providers: OAuthProvider[]
  connections: Connection[]
  onConnect: (providerId: string) => void
  onDisconnect: (providerId: string) => void
  loading?: boolean
}

export function ProviderList({
  providers,
  connections,
  onConnect,
  onDisconnect,
  loading = false
}: ProviderListProps) {
  const isConnected = (providerId: string) => {
    return connections.some(c => c.provider === providerId && c.status === 'active')
  }

  const getConnection = (providerId: string) => {
    return connections.find(c => c.provider === providerId)
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 animate-fade-in">
        <div className="w-12 h-12 border-4 border-gray-200 border-t-primary-500 rounded-full animate-spin"></div>
        <p className="mt-4 text-gray-600">Loading providers...</p>
      </div>
    )
  }

  if (providers.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center animate-fade-in">
        <svg className="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
        <p className="text-gray-600 text-lg">No providers available</p>
        <p className="text-gray-400 text-sm mt-2">Check back later or contact support</p>
      </div>
    )
  }

  return (
    <div className="p-5 max-w-7xl mx-auto">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {providers.map((provider, index) => {
          const connected = isConnected(provider.id)
          const connection = getConnection(provider.id)

          return (
            <div
              key={provider.id}
              className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:shadow-md transition-all duration-200 animate-slide-up"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* Header */}
              <div className="flex items-center gap-3 mb-3">
                {provider.icon && (
                  <img
                    src={provider.icon}
                    alt={provider.name}
                    className="w-8 h-8 rounded"
                  />
                )}
                <h3 className="text-lg font-semibold text-gray-900 truncate">
                  {provider.name}
                </h3>
              </div>

              {/* Description */}
              {provider.description && (
                <p className="text-sm text-gray-600 mb-4 line-clamp-2 leading-relaxed">
                  {provider.description}
                </p>
              )}

              {/* Footer */}
              <div className="flex items-center justify-between gap-3 mt-auto">
                {connected ? (
                  <>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      Connected
                    </span>
                    <button
                      onClick={() => onDisconnect(provider.id)}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                    >
                      Disconnect
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => onConnect(provider.id)}
                    className="w-full px-4 py-2 text-sm font-medium text-white bg-primary-500 rounded-md hover:bg-primary-600 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 shadow-sm"
                  >
                    Connect
                  </button>
                )}
              </div>

              {/* Connection metadata */}
              {connection?.expiresAt && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <p className="text-xs text-gray-500">
                    Expires: {new Date(connection.expiresAt).toLocaleDateString()}
                  </p>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
