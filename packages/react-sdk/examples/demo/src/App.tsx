import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { ConnectPortal, OAuthCallback } from '../../../src'

function HomePage() {
  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <header style={{ marginBottom: '40px', textAlign: 'center' }}>
        <h1>OAuth SDK React - Demo</h1>
        <p style={{ color: '#666', fontSize: '18px' }}>
          Test the ConnectPortal component
        </p>
      </header>

      <ConnectPortal
        apiKey="vk_test_demo_key"
        userId="demo_user_123"
        apiUrl="http://localhost:8000"
        onConnect={(provider, connection) => {
          console.log('Connected to:', provider)
          console.log('Connection:', connection)
          alert(`Successfully connected to ${provider.name}!`)
        }}
        onDisconnect={(providerId) => {
          console.log('Disconnected from:', providerId)
          alert(`Disconnected from ${providerId}`)
        }}
        onError={(error) => {
          console.error('OAuth error:', error)
          alert(`Error: ${error.message}`)
        }}
        theme={{
          primaryColor: '#007bff',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px'
        }}
      />

      <footer style={{ marginTop: '60px', textAlign: 'center', color: '#999' }}>
        <p>
          <Link to="/oauth/callback" style={{ color: '#007bff' }}>
            OAuth Callback Page
          </Link>
        </p>
      </footer>
    </div>
  )
}

function CallbackPage() {
  return (
    <OAuthCallback
      apiKey="vk_test_demo_key"
      apiUrl="http://localhost:8000"
      onSuccess={(provider, connection) => {
        console.log('OAuth success:', provider, connection)
        // Redirect to home after 2 seconds
        setTimeout(() => {
          window.location.href = '/'
        }, 2000)
      }}
      onError={(error) => {
        console.error('OAuth error:', error)
        // Redirect to home after 3 seconds
        setTimeout(() => {
          window.location.href = '/'
        }, 3000)
      }}
    />
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/oauth/callback" element={<CallbackPage />} />
      </Routes>
    </BrowserRouter>
  )
}
