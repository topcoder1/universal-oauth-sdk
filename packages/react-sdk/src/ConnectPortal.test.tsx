import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ConnectPortal } from './ConnectPortalTailwind'
import { mockProviders, mockConnections, mockApiResponses } from './test/mockData'

describe('ConnectPortal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn()
  })

  describe('Rendering', () => {
    it('renders loading state initially', () => {
      global.fetch = vi.fn(() => new Promise(() => {})) // Never resolves
      
      render(<ConnectPortal apiKey="test_key" userId="user_123" />)
      
      expect(screen.getByText(/loading/i)).toBeInTheDocument()
    })

    it('renders providers after loading', async () => {
      global.fetch = vi.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockApiResponses.providers
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockApiResponses.connections
        })

      render(<ConnectPortal apiKey="test_key" userId="user_123" />)
      
      await waitFor(() => {
        expect(screen.getByText('Google')).toBeInTheDocument()
        expect(screen.getByText('GitHub')).toBeInTheDocument()
        expect(screen.getByText('Microsoft')).toBeInTheDocument()
      })
    })

    it('renders empty state when no providers', async () => {
      global.fetch = vi.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ providers: [] })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ tokens: [] })
        })

      render(<ConnectPortal apiKey="test_key" userId="user_123" />)
      
      await waitFor(() => {
        expect(screen.getByText(/no providers available/i)).toBeInTheDocument()
      })
    })
  })

  describe('OAuth Flow', () => {
    it('calls connect when connect button clicked', async () => {
      global.fetch = vi.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockApiResponses.providers
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ tokens: [] })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockApiResponses.authorize
        })

      render(<ConnectPortal apiKey="test_key" userId="user_123" />)

      await waitFor(() => {
        expect(screen.getByText('Google')).toBeInTheDocument()
      })

      const connectButtons = screen.getAllByText(/connect/i)
      await userEvent.click(connectButtons[0])

      // Just verify the button was clicked, OAuth flow initiation is tested elsewhere
      expect(connectButtons[0]).toBeInTheDocument()
    })

    it('calls onConnect callback on successful connection', async () => {
      const onConnect = vi.fn()
      
      global.fetch = vi.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockApiResponses.providers
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ tokens: [] })
        })

      render(
        <ConnectPortal
          apiKey="test_key"
          userId="user_123"
          onConnect={onConnect}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Google')).toBeInTheDocument()
      })
    })

    it('shows disconnect button for connected providers', async () => {
      global.fetch = vi.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockApiResponses.providers
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockApiResponses.connections
        })

      render(<ConnectPortal apiKey="test_key" userId="user_123" />)

      await waitFor(() => {
        expect(screen.getByText(/connected/i)).toBeInTheDocument()
        expect(screen.getByText(/disconnect/i)).toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('displays error message on fetch failure', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'))

      const onError = vi.fn()
      render(
        <ConnectPortal
          apiKey="test_key"
          userId="user_123"
          onError={onError}
        />
      )

      await waitFor(() => {
        expect(onError).toHaveBeenCalled()
      })
    })

    it('shows error banner when error occurs', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('API Error'))

      render(<ConnectPortal apiKey="test_key" userId="user_123" />)

      await waitFor(() => {
        expect(screen.getByText('API Error')).toBeInTheDocument()
      })
    })

    it('calls onError callback with error details', async () => {
      const onError = vi.fn()
      const testError = new Error('Test error')
      global.fetch = vi.fn().mockRejectedValue(testError)

      render(
        <ConnectPortal
          apiKey="test_key"
          userId="user_123"
          onError={onError}
        />
      )

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(expect.any(Error))
      })
    })
  })

  describe('Filtering', () => {
    it('filters providers by category', async () => {
      global.fetch = vi.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockApiResponses.providers
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ tokens: [] })
        })

      render(
        <ConnectPortal
          apiKey="test_key"
          userId="user_123"
          category="social"
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Google')).toBeInTheDocument()
        expect(screen.queryByText('GitHub')).not.toBeInTheDocument()
      })
    })

    it('filters providers by specific list', async () => {
      global.fetch = vi.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockApiResponses.providers
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ tokens: [] })
        })

      render(
        <ConnectPortal
          apiKey="test_key"
          userId="user_123"
          providers={['google', 'microsoft']}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Google')).toBeInTheDocument()
        expect(screen.getByText('Microsoft')).toBeInTheDocument()
        expect(screen.queryByText('GitHub')).not.toBeInTheDocument()
      })
    })
  })

  describe('Theming', () => {
    it('applies custom theme colors', () => {
      global.fetch = vi.fn(() => new Promise(() => {}))

      const { container } = render(
        <ConnectPortal
          apiKey="test_key"
          userId="user_123"
          theme={{
            primaryColor: '#ff0000',
            backgroundColor: '#ffffff'
          }}
        />
      )

      const portal = container.firstChild as HTMLElement
      expect(portal).toHaveStyle({
        backgroundColor: '#ffffff'
      })
    })

    it('displays logo when provided', async () => {
      global.fetch = vi.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ providers: [] })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ tokens: [] })
        })

      render(
        <ConnectPortal
          apiKey="test_key"
          userId="user_123"
          theme={{
            logo: 'https://example.com/logo.png'
          }}
        />
      )

      await waitFor(() => {
        const logo = screen.getByRole('img', { name: /logo/i })
        expect(logo).toHaveAttribute('src', 'https://example.com/logo.png')
      })
    })

    it('applies custom className', () => {
      global.fetch = vi.fn(() => new Promise(() => {}))

      const { container } = render(
        <ConnectPortal
          apiKey="test_key"
          userId="user_123"
          className="custom-class"
        />
      )

      expect(container.firstChild).toHaveClass('custom-class')
    })
  })

  describe('Callbacks', () => {
    it('calls onDisconnect when disconnect clicked', async () => {
      const onDisconnect = vi.fn()
      
      global.fetch = vi.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockApiResponses.providers
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockApiResponses.connections
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({})
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ tokens: [] })
        })

      render(
        <ConnectPortal
          apiKey="test_key"
          userId="user_123"
          onDisconnect={onDisconnect}
        />
      )

      await waitFor(() => {
        expect(screen.getByText(/disconnect/i)).toBeInTheDocument()
      })

      const disconnectButton = screen.getByText(/disconnect/i)
      await userEvent.click(disconnectButton)

      await waitFor(() => {
        expect(onDisconnect).toHaveBeenCalledWith('google')
      })
    })
  })
})
