import { useState, useMemo } from 'react'
import type { OAuthProvider, Connection } from '../types'

export interface ProviderMarketplaceProps {
  providers: OAuthProvider[]
  connections: Connection[]
  onConnect: (providerId: string) => void
  onDisconnect: (providerId: string) => void
  loading?: boolean
  showSearch?: boolean
  showFilters?: boolean
  showCategories?: boolean
  gridColumns?: 2 | 3 | 4
  theme?: 'light' | 'dark'
}

export function ProviderMarketplace({
  providers,
  connections,
  onConnect,
  onDisconnect,
  loading = false,
  showSearch = true,
  showFilters = true,
  showCategories = true,
  gridColumns = 3,
  theme = 'light'
}: ProviderMarketplaceProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'name' | 'popular' | 'recent'>('name')

  // Extract categories
  const categories = useMemo(() => {
    const cats = new Set(providers.map(p => p.category).filter(Boolean))
    return ['all', ...Array.from(cats)]
  }, [providers])

  // Filter and sort providers
  const filteredProviders = useMemo(() => {
    let filtered = [...providers]

    // Filter by search
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(query) ||
        p.description?.toLowerCase().includes(query)
      )
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(p => p.category === selectedCategory)
    }

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === 'name') {
        return a.name.localeCompare(b.name)
      }
      // Add more sorting logic as needed
      return 0
    })

    return filtered
  }, [providers, searchQuery, selectedCategory, sortBy])

  const isConnected = (providerId: string) => {
    return connections.some(c => c.provider === providerId && c.status === 'active')
  }

  const isDark = theme === 'dark'
  const bgColor = isDark ? '#1a1a1a' : '#ffffff'
  const surfaceColor = isDark ? '#2d2d2d' : '#f8f9fa'
  const textColor = isDark ? '#f8f9fa' : '#212529'
  const borderColor = isDark ? '#495057' : '#dee2e6'

  return (
    <div
      className="provider-marketplace"
      style={{
        backgroundColor: bgColor,
        color: textColor,
        padding: '24px',
        borderRadius: '12px'
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h2
          style={{
            fontSize: '24px',
            fontWeight: 600,
            marginBottom: '8px'
          }}
        >
          Provider Marketplace
        </h2>
        <p style={{ color: isDark ? '#adb5bd' : '#6c757d', fontSize: '14px' }}>
          Browse and connect to {providers.length} OAuth providers
        </p>
      </div>

      {/* Search and Filters */}
      {(showSearch || showFilters) && (
        <div
          style={{
            display: 'flex',
            gap: '16px',
            marginBottom: '24px',
            flexWrap: 'wrap'
          }}
        >
          {showSearch && (
            <input
              type="text"
              placeholder="Search providers..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                flex: 1,
                minWidth: '200px',
                padding: '10px 16px',
                borderRadius: '8px',
                border: `1px solid ${borderColor}`,
                backgroundColor: surfaceColor,
                color: textColor,
                fontSize: '14px'
              }}
            />
          )}

          {showFilters && (
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: `1px solid ${borderColor}`,
                backgroundColor: surfaceColor,
                color: textColor,
                fontSize: '14px'
              }}
            >
              <option value="name">Sort by Name</option>
              <option value="popular">Most Popular</option>
              <option value="recent">Recently Added</option>
            </select>
          )}
        </div>
      )}

      {/* Categories */}
      {showCategories && categories.length > 1 && (
        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => cat && setSelectedCategory(cat)}
                style={{
                  padding: '8px 16px',
                  borderRadius: '20px',
                  border: selectedCategory === cat
                    ? '2px solid #007bff'
                    : `1px solid ${borderColor}`,
                  backgroundColor: selectedCategory === cat
                    ? isDark ? '#1864ab' : '#e7f5ff'
                    : surfaceColor,
                  color: selectedCategory === cat
                    ? isDark ? '#fff' : '#007bff'
                    : textColor,
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: selectedCategory === cat ? 600 : 400,
                  transition: 'all 0.2s'
                }}
              >
                {cat ? cat.charAt(0).toUpperCase() + cat.slice(1) : ''}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Provider Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px' }}>
          <div style={{ fontSize: '16px', color: isDark ? '#adb5bd' : '#6c757d' }}>
            Loading providers...
          </div>
        </div>
      ) : filteredProviders.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '48px' }}>
          <div style={{ fontSize: '16px', color: isDark ? '#adb5bd' : '#6c757d' }}>
            No providers found
          </div>
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${gridColumns}, 1fr)`,
            gap: '16px'
          }}
        >
          {filteredProviders.map(provider => {
            const connected = isConnected(provider.id)

            return (
              <div
                key={provider.id}
                style={{
                  backgroundColor: surfaceColor,
                  border: `1px solid ${borderColor}`,
                  borderRadius: '12px',
                  padding: '20px',
                  transition: 'all 0.2s',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)'
                  e.currentTarget.style.boxShadow = isDark
                    ? '0 4px 12px rgba(0,0,0,0.3)'
                    : '0 4px 12px rgba(0,0,0,0.1)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)'
                  e.currentTarget.style.boxShadow = 'none'
                }}
              >
                {/* Provider Icon & Name */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                  {provider.icon && (
                    <img
                      src={provider.icon}
                      alt={provider.name}
                      style={{ width: '40px', height: '40px', borderRadius: '8px' }}
                    />
                  )}
                  <div>
                    <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0 }}>
                      {provider.name}
                    </h3>
                    {provider.category && (
                      <span style={{ fontSize: '12px', color: isDark ? '#adb5bd' : '#6c757d' }}>
                        {provider.category}
                      </span>
                    )}
                  </div>
                </div>

                {/* Description */}
                {provider.description && (
                  <p
                    style={{
                      fontSize: '14px',
                      color: isDark ? '#adb5bd' : '#6c757d',
                      marginBottom: '16px',
                      lineHeight: 1.5
                    }}
                  >
                    {provider.description}
                  </p>
                )}

                {/* Connect Button */}
                <button
                  onClick={() => connected ? onDisconnect(provider.id) : onConnect(provider.id)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: '8px',
                    border: 'none',
                    backgroundColor: connected
                      ? isDark ? '#495057' : '#e9ecef'
                      : '#007bff',
                    color: connected
                      ? textColor
                      : '#ffffff',
                    fontSize: '14px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  {connected ? '✓ Connected' : 'Connect'}
                </button>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
