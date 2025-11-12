/**
 * Error handling utilities for OAuth SDK
 */

export class OAuthError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode?: number,
    public retryable: boolean = false
  ) {
    super(message)
    this.name = 'OAuthError'
  }
}

export const ERROR_CODES = {
  // Network errors
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT: 'TIMEOUT',
  
  // OAuth errors
  INVALID_GRANT: 'INVALID_GRANT',
  ACCESS_DENIED: 'ACCESS_DENIED',
  INVALID_REQUEST: 'INVALID_REQUEST',
  UNAUTHORIZED_CLIENT: 'UNAUTHORIZED_CLIENT',
  UNSUPPORTED_GRANT_TYPE: 'UNSUPPORTED_GRANT_TYPE',
  
  // API errors
  API_ERROR: 'API_ERROR',
  RATE_LIMIT: 'RATE_LIMIT',
  SERVER_ERROR: 'SERVER_ERROR',
  
  // Validation errors
  MISSING_PARAMETER: 'MISSING_PARAMETER',
  INVALID_PARAMETER: 'INVALID_PARAMETER',
  
  // Token errors
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  TOKEN_REVOKED: 'TOKEN_REVOKED',
  TOKEN_INVALID: 'TOKEN_INVALID',
} as const

export function getErrorMessage(error: unknown): string {
  if (error instanceof OAuthError) {
    return error.message
  }
  
  if (error instanceof Error) {
    return error.message
  }
  
  if (typeof error === 'string') {
    return error
  }
  
  return 'An unknown error occurred'
}

export function getUserFriendlyMessage(error: unknown): string {
  const message = getErrorMessage(error)
  
  // Map technical errors to user-friendly messages
  const friendlyMessages: Record<string, string> = {
    [ERROR_CODES.NETWORK_ERROR]: 'Unable to connect. Please check your internet connection.',
    [ERROR_CODES.TIMEOUT]: 'The request timed out. Please try again.',
    [ERROR_CODES.ACCESS_DENIED]: 'Access was denied. Please try connecting again.',
    [ERROR_CODES.INVALID_GRANT]: 'The authorization code is invalid or expired. Please try again.',
    [ERROR_CODES.RATE_LIMIT]: 'Too many requests. Please wait a moment and try again.',
    [ERROR_CODES.SERVER_ERROR]: 'Server error. Please try again later.',
    [ERROR_CODES.TOKEN_EXPIRED]: 'Your session has expired. Please reconnect.',
    [ERROR_CODES.TOKEN_REVOKED]: 'Access has been revoked. Please reconnect.',
  }
  
  // Check if we have a friendly message for this error code
  if (error instanceof OAuthError && friendlyMessages[error.code]) {
    return friendlyMessages[error.code]
  }
  
  // Return the original message if no friendly version exists
  return message
}

export function isRetryableError(error: unknown): boolean {
  if (error instanceof OAuthError) {
    return error.retryable
  }
  
  // Network errors and timeouts are retryable
  const message = getErrorMessage(error).toLowerCase()
  return (
    message.includes('network') ||
    message.includes('timeout') ||
    message.includes('fetch') ||
    message.includes('econnrefused')
  )
}

export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  initialDelay: number = 1000
): Promise<T> {
  let lastError: unknown
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error
      
      // Don't retry if error is not retryable
      if (!isRetryableError(error)) {
        throw error
      }
      
      // Don't retry on last attempt
      if (attempt === maxRetries) {
        throw error
      }
      
      // Exponential backoff: 1s, 2s, 4s, 8s...
      const delay = initialDelay * Math.pow(2, attempt)
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
  
  throw lastError
}

export function parseAPIError(response: any): OAuthError {
  const statusCode = response.status
  const data = response.data || {}
  
  // Check for OAuth error response
  if (data.error) {
    const code = data.error.toUpperCase()
    const message = data.error_description || data.message || 'OAuth error occurred'
    const retryable = statusCode >= 500 || statusCode === 429
    
    return new OAuthError(message, code, statusCode, retryable)
  }
  
  // Check for API error response
  if (data.detail) {
    const message = data.detail
    const code = statusCode >= 500 ? ERROR_CODES.SERVER_ERROR : ERROR_CODES.API_ERROR
    const retryable = statusCode >= 500 || statusCode === 429
    
    return new OAuthError(message, code, statusCode, retryable)
  }
  
  // Generic error
  const message = `Request failed with status ${statusCode}`
  const code = statusCode >= 500 ? ERROR_CODES.SERVER_ERROR : ERROR_CODES.API_ERROR
  const retryable = statusCode >= 500 || statusCode === 429
  
  return new OAuthError(message, code, statusCode, retryable)
}
