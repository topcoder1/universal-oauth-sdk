import express from 'express';
import session from 'express-session';
import { createClient, SQLiteStore, ProviderRegistry } from '@oauth-kit/sdk';
import { config } from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

config();

const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 3000;

// Session configuration
app.use(session({
  secret: process.env.SESSION_SECRET || 'your-secret-key-change-in-production',
  resave: false,
  saveUninitialized: false,
  cookie: { 
    secure: process.env.NODE_ENV === 'production',
    maxAge: 24 * 60 * 60 * 1000 // 24 hours
  }
}));

// Load provider registry
const catalogDir = resolve(__dirname, '../../../provider-catalog/manifests');
const registry = ProviderRegistry.loadFromDir(catalogDir);

// Create OAuth client factory
function createOAuthClient(provider, userId) {
  const manifest = registry.get(provider);
  if (!manifest) {
    throw new Error(`Unknown provider: ${provider}`);
  }

  const clientIdKey = `${provider.toUpperCase()}_CLIENT_ID`;
  const clientSecretKey = `${provider.toUpperCase()}_CLIENT_SECRET`;

  return createClient({
    provider: manifest,
    clientId: process.env[clientIdKey],
    clientSecret: process.env[clientSecretKey],
    redirectUri: `http://localhost:${PORT}/auth/${provider}/callback`,
    store: new SQLiteStore('tokens.db'),
    logger: (msg, meta) => console.log(`[OAuth ${provider}]`, msg, meta)
  });
}

// Middleware to check authentication
function requireAuth(req, res, next) {
  if (!req.session.userId) {
    return res.redirect('/');
  }
  next();
}

// Routes
app.get('/', (req, res) => {
  if (req.session.userId) {
    return res.redirect('/dashboard');
  }

  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>OAuth Example - Express</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          max-width: 800px;
          margin: 50px auto;
          padding: 20px;
          background: #f5f5f5;
        }
        .container {
          background: white;
          padding: 40px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        .providers {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
          margin-top: 30px;
        }
        .provider-btn {
          display: block;
          padding: 15px 20px;
          background: #0066cc;
          color: white;
          text-decoration: none;
          border-radius: 6px;
          text-align: center;
          font-weight: 500;
          transition: background 0.2s;
        }
        .provider-btn:hover {
          background: #0052a3;
        }
        .google { background: #4285f4; }
        .google:hover { background: #3367d6; }
        .github { background: #24292e; }
        .github:hover { background: #1b1f23; }
        .microsoft { background: #00a4ef; }
        .microsoft:hover { background: #0078d4; }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>🔐 Universal OAuth SDK</h1>
        <p>Express.js Example Application</p>
        <p>Choose a provider to sign in:</p>
        
        <div class="providers">
          <a href="/auth/google" class="provider-btn google">Sign in with Google</a>
          <a href="/auth/github" class="provider-btn github">Sign in with GitHub</a>
          <a href="/auth/microsoft" class="provider-btn microsoft">Sign in with Microsoft</a>
        </div>
      </div>
    </body>
    </html>
  `);
});

app.get('/auth/:provider', async (req, res) => {
  const { provider } = req.params;
  
  try {
    // Generate a session ID for this user
    const userId = `user_${Date.now()}`;
    req.session.userId = userId;
    req.session.provider = provider;
    
    const client = createOAuthClient(provider, userId);
    await client.init();
    
    // Start authorization (this will open browser and wait for callback)
    // In a real app, you'd redirect to the authorization URL instead
    res.send(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Authorizing...</title>
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 600px;
            margin: 100px auto;
            text-align: center;
            padding: 20px;
          }
          .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #0066cc;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
          }
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        </style>
      </head>
      <body>
        <h2>Redirecting to ${provider}...</h2>
        <div class="spinner"></div>
        <p>Please complete the authorization in the browser window that opened.</p>
        <p><a href="/">Cancel</a></p>
      </body>
      </html>
    `);
    
    // Authorize in background
    client.authorize(userId).then(() => {
      console.log(`✅ Authorization complete for ${userId}`);
    }).catch(err => {
      console.error(`❌ Authorization failed:`, err);
    });
    
  } catch (error) {
    console.error('Auth error:', error);
    res.status(500).send(`Error: ${error.message}`);
  }
});

app.get('/auth/:provider/callback', async (req, res) => {
  // This route is called by the OAuth provider after authorization
  // The SDK handles the callback automatically
  res.redirect('/dashboard');
});

app.get('/dashboard', requireAuth, async (req, res) => {
  const { userId, provider } = req.session;
  
  try {
    const client = createOAuthClient(provider, userId);
    await client.init();
    
    const token = await client.getToken(userId);
    
    if (!token) {
      return res.redirect('/');
    }
    
    // Make an API request to get user info
    let userInfo = { name: 'Unknown', email: 'unknown@example.com' };
    
    try {
      if (provider === 'google') {
        const response = await client.request('https://www.googleapis.com/oauth2/v2/userinfo', {}, userId);
        userInfo = await response.json();
      } else if (provider === 'github') {
        const response = await client.request('https://api.github.com/user', {}, userId);
        userInfo = await response.json();
        userInfo.email = userInfo.email || 'Not public';
      } else if (provider === 'microsoft') {
        const response = await client.request('https://graph.microsoft.com/v1.0/me', {}, userId);
        userInfo = await response.json();
        userInfo.name = userInfo.displayName;
        userInfo.email = userInfo.userPrincipalName;
      }
    } catch (apiError) {
      console.error('API request failed:', apiError);
    }
    
    const expiresIn = token.expiresAt 
      ? Math.floor((token.expiresAt - Date.now()) / 1000 / 60)
      : null;
    
    res.send(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Dashboard - OAuth Example</title>
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
          }
          .container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          }
          .user-info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
          }
          .token-info {
            background: #e7f3ff;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
            font-family: monospace;
            font-size: 14px;
          }
          .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #dc3545;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin-top: 20px;
          }
          .btn:hover {
            background: #c82333;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>✅ Authenticated!</h1>
          
          <div class="user-info">
            <h2>User Information</h2>
            <p><strong>Name:</strong> ${userInfo.name || userInfo.login || 'N/A'}</p>
            <p><strong>Email:</strong> ${userInfo.email || 'N/A'}</p>
            <p><strong>Provider:</strong> ${provider}</p>
          </div>
          
          <div class="token-info">
            <h3>Token Status</h3>
            <p><strong>Access Token:</strong> ${token.accessToken.substring(0, 20)}...</p>
            <p><strong>Has Refresh Token:</strong> ${token.refreshToken ? 'Yes' : 'No'}</p>
            <p><strong>Token Type:</strong> ${token.tokenType || 'Bearer'}</p>
            ${expiresIn !== null ? `<p><strong>Expires In:</strong> ${expiresIn} minutes</p>` : ''}
            <p><strong>Scope:</strong> ${token.scope || 'N/A'}</p>
          </div>
          
          <a href="/logout" class="btn">Logout</a>
        </div>
      </body>
      </html>
    `);
    
  } catch (error) {
    console.error('Dashboard error:', error);
    res.status(500).send(`Error: ${error.message}`);
  }
});

app.get('/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/');
});

app.listen(PORT, () => {
  console.log(`\n🚀 Express OAuth Example running on http://localhost:${PORT}`);
  console.log(`\n📝 Make sure to set these environment variables:`);
  console.log(`   GOOGLE_CLIENT_ID`);
  console.log(`   GOOGLE_CLIENT_SECRET`);
  console.log(`   GITHUB_CLIENT_ID`);
  console.log(`   GITHUB_CLIENT_SECRET`);
  console.log(`   MICROSOFT_CLIENT_ID`);
  console.log(`   MICROSOFT_CLIENT_SECRET\n`);
});
