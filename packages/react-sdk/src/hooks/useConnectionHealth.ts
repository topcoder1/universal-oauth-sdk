import { useState, useEffect, useCallback } from 'react'
import type { Connection } from '../types'

export type ConnectionStatus = 'healthy' | 'expiring' | 'expired' | 'error' | 'unknown'

export interface ConnectionHealth {
  connectionId: string
  status: ConnectionStatus
  expiresAt?: string
  daysUntilExpiry?: number
  lastChecked: string
  error?: string
}

export interface UseConnectionHealthOptions {
  connections: Connection[]
  checkInterval?: number // milliseconds
  expiryWarningDays?: number // days before expiry to warn
}

export interface UseConnectionHealthReturn {
  healthStatus: Map<string, ConnectionHealth>
  getHealth: (connectionId: string) => ConnectionHealth | undefined
  isHealthy: (connectionId: string) => boolean
  isExpiring: (connectionId: string) => boolean
  isExpired: (connectionId: string) => boolean
  expiringConnections: ConnectionHealth[]
  expiredConnections: ConnectionHealth[]
  healthyConnections: ConnectionHealth[]
  refresh: () => void
}

export function useConnectionHealth(
  options: UseConnectionHealthOptions
): UseConnectionHealthReturn {
  const { connections, checkInterval = 60000, expiryWarningDays = 7 } = options

  const [healthStatus, setHealthStatus] = useState<Map<string, ConnectionHealth>>(new Map())

  const checkConnectionHealth = useCallback((connection: Connection): ConnectionHealth => {
    const now = new Date()
    const health: ConnectionHealth = {
      connectionId: connection.id,
      status: 'unknown',
      lastChecked: now.toISOString()
    }

    // Check if connection has expiry date
    if (connection.expiresAt) {
      health.expiresAt = connection.expiresAt
      const expiryDate = new Date(connection.expiresAt)
      const daysUntilExpiry = Math.floor((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
      health.daysUntilExpiry = daysUntilExpiry

      if (daysUntilExpiry < 0) {
        health.status = 'expired'
      } else if (daysUntilExpiry <= expiryWarningDays) {
        health.status = 'expiring'
      } else {
        health.status = 'healthy'
      }
    } else {
      // No expiry date, assume healthy if status is active
      health.status = connection.status === 'active' ? 'healthy' : 'error'
    }

    // Check connection status
    if (connection.status === 'error') {
      health.status = 'error'
      health.error = 'Connection error'
    } else if (connection.status === 'expired') {
      health.status = 'expired'
    }

    return health
  }, [expiryWarningDays])

  const checkAllConnections = useCallback(() => {
    const newHealthStatus = new Map<string, ConnectionHealth>()

    connections.forEach(connection => {
      const health = checkConnectionHealth(connection)
      newHealthStatus.set(connection.id, health)
    })

    setHealthStatus(newHealthStatus)
  }, [connections, checkConnectionHealth])

  // Initial check and periodic refresh
  useEffect(() => {
    checkAllConnections()

    if (checkInterval > 0) {
      const interval = setInterval(checkAllConnections, checkInterval)
      return () => clearInterval(interval)
    }
  }, [checkAllConnections, checkInterval])

  const getHealth = (connectionId: string): ConnectionHealth | undefined => {
    return healthStatus.get(connectionId)
  }

  const isHealthy = (connectionId: string): boolean => {
    return healthStatus.get(connectionId)?.status === 'healthy'
  }

  const isExpiring = (connectionId: string): boolean => {
    return healthStatus.get(connectionId)?.status === 'expiring'
  }

  const isExpired = (connectionId: string): boolean => {
    const status = healthStatus.get(connectionId)?.status
    return status === 'expired'
  }

  // Get connections by status
  const expiringConnections = Array.from(healthStatus.values()).filter(
    h => h.status === 'expiring'
  )

  const expiredConnections = Array.from(healthStatus.values()).filter(
    h => h.status === 'expired'
  )

  const healthyConnections = Array.from(healthStatus.values()).filter(
    h => h.status === 'healthy'
  )

  return {
    healthStatus,
    getHealth,
    isHealthy,
    isExpiring,
    isExpired,
    expiringConnections,
    expiredConnections,
    healthyConnections,
    refresh: checkAllConnections
  }
}
