/**
 * Demo 3: Encrypted Token Storage
 * 
 * This demo shows how to use encrypted storage to protect
 * OAuth tokens at rest using AES-256-CBC encryption.
 */

import { createClient, EncryptedSQLiteStore } from '@topcoder1/oauth-sdk';
import { randomBytes } from 'crypto';

async function main() {
  console.log('🔐 Universal OAuth SDK - Encrypted Storage Demo\n');

  // Generate encryption key (do this once and store securely!)
  const encryptionKey = process.env.ENCRYPTION_KEY || randomBytes(32).toString('hex');
  
  if (!process.env.ENCRYPTION_KEY) {
    console.log('⚠️  No ENCRYPTION_KEY found in environment');
    console.log('📝 Generated new key (save this securely!):\n');
    console.log(`   ENCRYPTION_KEY=${encryptionKey}\n`);
  }

  // Create encrypted store
  const store = new EncryptedSQLiteStore('encrypted-tokens.db', encryptionKey);
  console.log('✅ Encrypted store initialized\n');

  // Create OAuth client
  const client = createClient({
    provider: 'microsoft',
    clientId: process.env.MICROSOFT_CLIENT_ID || 'your-client-id',
    clientSecret: process.env.MICROSOFT_CLIENT_SECRET || 'your-secret',
    redirectUri: 'http://localhost:8787/callback',
    store
  });

  // Initialize the client
  await client.init();
  console.log('✅ Client initialized\n');

  // Start OAuth flow
  console.log('🌐 Starting OAuth flow...');
  console.log('👉 A browser window will open for authentication\n');
  
  await client.authorize();
  console.log('✅ Authentication successful!\n');

  console.log('🔒 Token Security:');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('✅ Tokens encrypted with AES-256-CBC');
  console.log('✅ Random IV for each token');
  console.log('✅ Secure storage in SQLite database');
  console.log('✅ Protected against unauthorized access');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  // Fetch user information
  console.log('📥 Fetching user information...');
  const response = await client.request('https://graph.microsoft.com/v1.0/me');
  const user = await response.json();

  console.log('\n👤 Microsoft User Information:');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`Name: ${user.displayName}`);
  console.log(`Email: ${user.mail || user.userPrincipalName}`);
  console.log(`Job Title: ${user.jobTitle || 'N/A'}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  console.log('✨ Demo complete!');
  console.log('\n💡 Tip: Your tokens are safely encrypted in encrypted-tokens.db');
}

main().catch(console.error);
