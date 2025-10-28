/**
 * Demo 4: Multi-Provider Support
 * 
 * This demo shows how to authenticate with multiple OAuth providers
 * and manage multiple accounts simultaneously.
 */

import { createClient, SQLiteStore } from '@topcoder1/oauth-sdk';

const providers = [
  {
    name: 'google',
    clientId: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    userInfoUrl: 'https://www.googleapis.com/oauth2/v2/userinfo'
  },
  {
    name: 'github',
    clientId: process.env.GITHUB_CLIENT_ID,
    clientSecret: process.env.GITHUB_CLIENT_SECRET,
    userInfoUrl: 'https://api.github.com/user'
  },
  {
    name: 'microsoft',
    clientId: process.env.MICROSOFT_CLIENT_ID,
    clientSecret: process.env.MICROSOFT_CLIENT_SECRET,
    userInfoUrl: 'https://graph.microsoft.com/v1.0/me'
  }
];

async function authenticateProvider(provider) {
  console.log(`\n🔐 Authenticating with ${provider.name.toUpperCase()}...`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  if (!provider.clientId) {
    console.log(`⚠️  Skipping ${provider.name} (no credentials configured)\n`);
    return null;
  }

  const client = createClient({
    provider: provider.name,
    clientId: provider.clientId,
    clientSecret: provider.clientSecret,
    redirectUri: 'http://localhost:8787/callback',
    store: new SQLiteStore('multi-provider-tokens.db')
  });

  await client.init();
  await client.authorize(provider.name);
  
  console.log(`✅ ${provider.name} authentication successful!`);

  // Fetch user info
  const response = await client.request(provider.userInfoUrl, {}, provider.name);
  const user = await response.json();

  return { provider: provider.name, user };
}

async function main() {
  console.log('🌐 Universal OAuth SDK - Multi-Provider Demo\n');
  console.log('This demo authenticates with multiple OAuth providers');
  console.log('and demonstrates managing multiple accounts.\n');

  const results = [];

  // Authenticate with each provider
  for (const provider of providers) {
    try {
      const result = await authenticateProvider(provider);
      if (result) {
        results.push(result);
      }
    } catch (error) {
      console.log(`❌ ${provider.name} authentication failed: ${error.message}\n`);
    }
  }

  // Display all authenticated accounts
  if (results.length > 0) {
    console.log('\n\n📊 AUTHENTICATED ACCOUNTS SUMMARY');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

    results.forEach(({ provider, user }) => {
      console.log(`🔹 ${provider.toUpperCase()}`);
      
      if (provider === 'google') {
        console.log(`   Name: ${user.name}`);
        console.log(`   Email: ${user.email}`);
      } else if (provider === 'github') {
        console.log(`   Username: ${user.login}`);
        console.log(`   Name: ${user.name || 'N/A'}`);
      } else if (provider === 'microsoft') {
        console.log(`   Name: ${user.displayName}`);
        console.log(`   Email: ${user.mail || user.userPrincipalName}`);
      }
      
      console.log('');
    });

    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    console.log(`✅ Successfully authenticated with ${results.length} provider(s)!`);
  } else {
    console.log('\n⚠️  No providers were authenticated.');
    console.log('💡 Configure credentials in .env file to test multiple providers.\n');
  }

  console.log('\n✨ Demo complete!');
}

main().catch(console.error);
