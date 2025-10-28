/**
 * Demo 1: Basic OAuth Flow
 * 
 * This demo shows the simplest way to use the Universal OAuth SDK
 * to authenticate with Google and fetch user information.
 */

import { createClient, SQLiteStore } from '@topcoder1/oauth-sdk';

async function main() {
  console.log('🔐 Universal OAuth SDK - Basic Demo\n');

  // Create OAuth client
  const client = createClient({
    provider: 'google',
    clientId: process.env.GOOGLE_CLIENT_ID || 'your-client-id',
    clientSecret: process.env.GOOGLE_CLIENT_SECRET || 'your-secret',
    redirectUri: 'http://localhost:8787/callback',
    store: new SQLiteStore('tokens.db')
  });

  // Initialize the client
  await client.init();
  console.log('✅ Client initialized\n');

  // Start OAuth flow
  console.log('🌐 Starting OAuth flow...');
  console.log('👉 A browser window will open for authentication\n');
  
  await client.authorize();
  console.log('✅ Authentication successful!\n');

  // Fetch user information
  console.log('📥 Fetching user information...');
  const response = await client.request('https://www.googleapis.com/oauth2/v2/userinfo');
  const user = await response.json();

  console.log('\n👤 User Information:');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`Name: ${user.name}`);
  console.log(`Email: ${user.email}`);
  console.log(`Picture: ${user.picture}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  console.log('✨ Demo complete!');
}

main().catch(console.error);
