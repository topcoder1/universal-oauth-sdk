import { useEffect, useState } from 'react'

interface OAuthCallbackProps {
  apiKey: string
  apiUrl?: string
  onSuccess?: (provider: string, connection: any) => void
  onError?: (error: Error) => void
}

export function OAuthCallback({
  apiKey,
  apiUrl = 'http://localhost:8000',
  onSuccess,
  onError
}: OAuthCallbackProps) {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [error, setError] = useState<Error | null>(null)
  const [provider, setProvider] = useState<string>('')

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const params = new URLSearchParams(window.location.search)
        const code = params.get('code')
        const state = params.get('state')
        const errorParam = params.get('error')
        const errorDescription = params.get('error_description')

        if (errorParam) {
          throw new Error(errorDescription || errorParam)
        }

        if (!code) {
          throw new Error('Missing authorization code')
        }

        if (!state) {
          throw new Error('Missing state parameter')
        }

        const stateData = JSON.parse(atob(state))
        const { provider: providerName, user_id } = stateData

        setProvider(providerName)

        const response = await fetch(`${apiUrl}/api/v1/oauth/callback`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            code,
            state,
            provider: providerName,
            user_id,
            redirect_uri: window.location.origin + window.location.pathname
          })
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Failed to exchange authorization code')
        }

        const connection = await response.json()

        setStatus('success')

        if (onSuccess) {
          onSuccess(providerName, connection)
        }
      } catch (err) {
        const error = err as Error
        setError(error)
        setStatus('error')

        if (onError) {
          onError(error)
        }
      }
    }

    handleCallback()
  }, [apiKey, apiUrl, onSuccess, onError])

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 p-5">
      <div className="bg-white rounded-xl p-12 max-w-md w-full text-center shadow-lg animate-fade-in">
        {status === 'loading' && (
          <div className="animate-slide-up">
            <div className="w-16 h-16 border-4 border-gray-200 border-t-primary-500 rounded-full animate-spin mx-auto mb-6"></div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              Connecting...
            </h2>
            <p className="text-gray-600 leading-relaxed">
              Please wait while we complete the authorization
            </p>
          </div>
        )}

        {status === 'success' && (
          <div className="animate-slide-up">
            <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              Successfully Connected!
            </h2>
            <p className="text-gray-600 mb-2">
              You've successfully connected to <span className="font-medium text-gray-900">{provider}</span>
            </p>
            <p className="text-sm text-gray-500 mt-4">
              Redirecting...
            </p>
          </div>
        )}

        {status === 'error' && (
          <div className="animate-slide-up">
            <div className="w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              Connection Failed
            </h2>
            <p className="text-gray-600 mb-6 leading-relaxed">
              {error?.message || 'An error occurred during authorization'}
            </p>
            <button
              onClick={() => window.history.back()}
              className="px-6 py-3 text-base font-medium text-white bg-primary-500 rounded-lg hover:bg-primary-600 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 shadow-sm"
            >
              Go Back
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
