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
      <div style={styles.loading}>
        <div style={styles.spinner}></div>
        <p>Loading providers...</p>
      </div>
    )
  }

  if (providers.length === 0) {
    return (
      <div style={styles.empty}>
        <p>No providers available</p>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <div style={styles.grid}>
        {providers.map((provider) => {
          const connected = isConnected(provider.id)
          const connection = getConnection(provider.id)

          return (
            <div key={provider.id} style={styles.card}>
              <div style={styles.cardHeader}>
                {provider.icon && (
                  <img 
                    src={provider.icon} 
                    alt={provider.name}
                    style={styles.icon}
                  />
                )}
                <h3 style={styles.providerName}>{provider.name}</h3>
              </div>

              {provider.description && (
                <p style={styles.description}>{provider.description}</p>
              )}

              <div style={styles.cardFooter}>
                {connected ? (
                  <>
                    <span style={styles.statusBadge}>
                      ✓ Connected
                    </span>
                    <button
                      onClick={() => onDisconnect(provider.id)}
                      style={{...styles.button, ...styles.disconnectButton}}
                    >
                      Disconnect
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => onConnect(provider.id)}
                    style={{...styles.button, ...styles.connectButton}}
                  >
                    Connect
                  </button>
                )}
              </div>

              {connection?.expiresAt && (
                <div style={styles.metadata}>
                  <small>Expires: {new Date(connection.expiresAt).toLocaleDateString()}</small>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// Basic inline styles (will be replaced with proper styling later)
const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '20px'
  },
  card: {
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    padding: '20px',
    backgroundColor: '#fff',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    transition: 'box-shadow 0.2s',
    ':hover': {
      boxShadow: '0 4px 8px rgba(0,0,0,0.15)'
    }
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '12px'
  },
  icon: {
    width: '32px',
    height: '32px',
    borderRadius: '4px'
  },
  providerName: {
    margin: 0,
    fontSize: '18px',
    fontWeight: '600',
    color: '#333'
  },
  description: {
    fontSize: '14px',
    color: '#666',
    marginBottom: '16px',
    lineHeight: '1.5'
  },
  cardFooter: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '12px'
  },
  button: {
    padding: '8px 16px',
    borderRadius: '6px',
    border: 'none',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s',
    flex: 1
  },
  connectButton: {
    backgroundColor: '#007bff',
    color: '#fff',
    ':hover': {
      backgroundColor: '#0056b3'
    }
  },
  disconnectButton: {
    backgroundColor: '#6c757d',
    color: '#fff',
    ':hover': {
      backgroundColor: '#545b62'
    }
  },
  statusBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '4px 8px',
    backgroundColor: '#d4edda',
    color: '#155724',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: '500'
  },
  metadata: {
    marginTop: '12px',
    paddingTop: '12px',
    borderTop: '1px solid #e0e0e0',
    color: '#666',
    fontSize: '12px'
  },
  loading: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px',
    color: '#666'
  },
  spinner: {
    width: '40px',
    height: '40px',
    border: '4px solid #f3f3f3',
    borderTop: '4px solid #007bff',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    marginBottom: '16px'
  },
  empty: {
    textAlign: 'center' as const,
    padding: '40px',
    color: '#666'
  }
}
