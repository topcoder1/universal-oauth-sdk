/**
 * Demo 2: Device Code Flow
 * 
 * This demo shows how to use device flow for CLI applications,
 * TV apps, or IoT devices without a browser.
 */

import { createClient, MemoryStore } from '@topcoder1/oauth-sdk';

async function main() {
  console.log('📱 Universal OAuth SDK - Device Flow Demo\n');

  // Create OAuth client
  const client = createClient({
    provider: 'github',
    clientId: process.env.GITHUB_CLIENT_ID || 'your-client-id',
    redirectUri: 'http://localhost:8787/callback',
    store: new MemoryStore()
  });

  // Initialize the client
  await client.init();
  console.log('✅ Client initialized\n');

  // Start device flow
  console.log('🔐 Starting Device Authorization Flow...\n');
  
  await client.authorizeDevice(undefined, (userCode, verificationUri) => {
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📱 DEVICE AUTHORIZATION REQUIRED');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(`\n1. Visit: ${verificationUri}`);
    console.log(`2. Enter code: ${userCode}\n`);
    console.log('⏳ Waiting for authorization...\n');
  });

  console.log('✅ Authorization successful!\n');

  // Fetch user information
  console.log('📥 Fetching user information...');
  const response = await client.request('https://api.github.com/user');
  const user = await response.json();

  console.log('\n👤 GitHub User Information:');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`Username: ${user.login}`);
  console.log(`Name: ${user.name || 'N/A'}`);
  console.log(`Bio: ${user.bio || 'N/A'}`);
  console.log(`Public Repos: ${user.public_repos}`);
  console.log(`Followers: ${user.followers}`);
  console.log(`Profile: ${user.html_url}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  console.log('✨ Demo complete!');
}

main().catch(console.error);
