import { useState, useEffect, useMemo } from 'react'
import type { OAuthProvider } from '../types'

export interface UseProvidersOptions {
  apiKey: string
  apiUrl?: string
  category?: string
  search?: string
  tags?: string[]
  enabled?: boolean
}

export interface UseProvidersReturn {
  providers: OAuthProvider[]
  filteredProviders: OAuthProvider[]
  loading: boolean
  error: Error | null
  refresh: () => Promise<void>
  searchProviders: (query: string) => OAuthProvider[]
  filterByCategory: (category: string) => OAuthProvider[]
  filterByTags: (tags: string[]) => OAuthProvider[]
  categories: string[]
  allTags: string[]
}

export function useProviders(options: UseProvidersOptions): UseProvidersReturn {
  const { apiKey, apiUrl = 'http://localhost:8000', category, search, tags, enabled = true } = options

  const [providers, setProviders] = useState<OAuthProvider[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchProviders = async () => {
    if (!enabled) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${apiUrl}/providers`, {
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
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProviders()
  }, [apiKey, apiUrl, enabled])

  // Extract unique categories
  const categories = useMemo(() => {
    const cats = new Set(providers.map(p => p.category).filter(Boolean))
    return Array.from(cats) as string[]
  }, [providers])

  // Extract all tags
  const allTags = useMemo(() => {
    const tagSet = new Set<string>()
    providers.forEach(p => {
      if (p.tags) {
        p.tags.forEach(tag => tagSet.add(tag))
      }
    })
    return Array.from(tagSet)
  }, [providers])

  // Filter providers
  const filteredProviders = useMemo(() => {
    let filtered = [...providers]

    // Filter by category
    if (category) {
      filtered = filtered.filter(p => p.category === category)
    }

    // Filter by search
    if (search) {
      const query = search.toLowerCase()
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(query) ||
        p.description?.toLowerCase().includes(query) ||
        p.id.toLowerCase().includes(query)
      )
    }

    // Filter by tags
    if (tags && tags.length > 0) {
      filtered = filtered.filter(p =>
        p.tags && tags.some(tag => p.tags!.includes(tag))
      )
    }

    return filtered
  }, [providers, category, search, tags])

  // Search function
  const searchProviders = (query: string): OAuthProvider[] => {
    const q = query.toLowerCase()
    return providers.filter(p =>
      p.name.toLowerCase().includes(q) ||
      p.description?.toLowerCase().includes(q) ||
      p.id.toLowerCase().includes(q)
    )
  }

  // Filter by category
  const filterByCategory = (cat: string): OAuthProvider[] => {
    return providers.filter(p => p.category === cat)
  }

  // Filter by tags
  const filterByTags = (filterTags: string[]): OAuthProvider[] => {
    return providers.filter(p =>
      p.tags && filterTags.some(tag => p.tags!.includes(tag))
    )
  }

  return {
    providers,
    filteredProviders,
    loading,
    error,
    refresh: fetchProviders,
    searchProviders,
    filterByCategory,
    filterByTags,
    categories,
    allTags
  }
}
