"""Local callback server for OAuth authorization flow

Starts a temporary HTTP server to receive OAuth callback.
Based on Node SDK's waitForCallback implementation.
"""

from typing import Optional, Callable
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback"""
    
    # Class variables to store callback data
    authorization_code: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None
    error_description: Optional[str] = None
    
    def log_message(self, format: str, *args) -> None:
        """Suppress default logging"""
        pass  # Silent by default
    
    def do_GET(self) -> None:
        """Handle GET request (OAuth callback)"""
        # Parse query parameters
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        # Check for error
        if 'error' in params:
            CallbackHandler.error = params['error'][0]
            CallbackHandler.error_description = params.get('error_description', [CallbackHandler.error])[0]
            
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
                <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #d32f2f;">❌ Authorization Failed</h1>
                    <p style="font-size: 18px;">{CallbackHandler.error_description}</p>
                    <p style="color: #666;">You can close this window.</p>
                </body>
                </html>
            """.encode())
            return
        
        # Extract code and state
        code = params.get('code', [None])[0]
        state = params.get('state', [None])[0]
        
        if code and state:
            CallbackHandler.authorization_code = code
            CallbackHandler.state = state
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("""
                <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #4caf50;">✅ Authorization Successful!</h1>
                    <p style="font-size: 18px;">You can close this window and return to your application.</p>
                    <script>
                        setTimeout(function() {
                            window.close();
                        }, 2000);
                    </script>
                </body>
                </html>
            """.encode())
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Invalid callback: missing code or state")


class CallbackServer:
    """Local HTTP server for OAuth callback
    
    Starts a temporary server to receive OAuth authorization callback.
    """
    
    def __init__(self, redirect_uri: str, timeout: int = 300):
        """Initialize callback server
        
        Args:
            redirect_uri: OAuth redirect URI (e.g., http://localhost:8787/callback)
            timeout: Timeout in seconds (default: 300 = 5 minutes)
        """
        parsed = urlparse(redirect_uri)
        self.host = parsed.hostname or 'localhost'
        self.port = parsed.port or 8787
        self.path = parsed.path or '/callback'
        self.timeout = timeout
        
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
    
    def start(self) -> None:
        """Start the callback server in a background thread"""
        # Reset handler state
        CallbackHandler.authorization_code = None
        CallbackHandler.state = None
        CallbackHandler.error = None
        CallbackHandler.error_description = None
        
        # Create server
        self.server = HTTPServer((self.host, self.port), CallbackHandler)
        
        # Start in background thread
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
    
    def _run_server(self) -> None:
        """Run server (called in background thread)"""
        if self.server:
            self.server.serve_forever()
    
    def wait_for_callback(self, expected_state: Optional[str] = None) -> tuple[str, str]:
        """Wait for OAuth callback
        
        Args:
            expected_state: Expected state parameter for validation
            
        Returns:
            Tuple of (authorization_code, state)
            
        Raises:
            TimeoutError: If callback not received within timeout
            ValueError: If state mismatch or error in callback
        """
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            # Check for error
            if CallbackHandler.error:
                self.stop()
                raise ValueError(f"OAuth error: {CallbackHandler.error_description}")
            
            # Check for successful callback
            if CallbackHandler.authorization_code and CallbackHandler.state:
                code = CallbackHandler.authorization_code
                state = CallbackHandler.state
                
                # Validate state if provided
                if expected_state and state != expected_state:
                    self.stop()
                    raise ValueError("State mismatch - possible CSRF attack")
                
                self.stop()
                return code, state
            
            # Sleep briefly to avoid busy waiting
            time.sleep(0.1)
        
        # Timeout
        self.stop()
        raise TimeoutError(f"Authorization timeout after {self.timeout} seconds")
    
    def stop(self) -> None:
        """Stop the callback server"""
        if self.server:
            self.server.shutdown()
            self.server = None
        if self.thread:
            self.thread.join(timeout=1)
            self.thread = None
