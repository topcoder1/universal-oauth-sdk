# Usage Guide

## Getting Started

### Prerequisites

- Node.js 18+ or 20+
- pnpm, npm, or yarn
- OAuth credentials from your provider (Google, GitHub, etc.)

### Installation

```bash
pnpm add @oauth-kit/sdk
```

### Basic Setup

1. **Get OAuth Credentials**

For Google:
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project or select existing
- Enable APIs you need (e.g., Google+ API)
- Go to "Credentials" → "Create Credentials" → "OAuth client ID"
- Choose "Web application"
- Add redirect URI: `http://localhost:8787/callback`
- Copy Client ID and Client Secret

2. **Create Your First OAuth Client**

```typescript
import { createClient, SQLiteStore } from "@oauth-kit/sdk";

const client = createClient({
  provider: "google",
  clientId: "your-client-id.apps.googleusercontent.com",
  clientSecret: "your-client-secret",
  redirectUri: "http://localhost:8787/callback",
  store: new SQLiteStore("tokens.db")
});

await client.init();
```

3. **Authorize**

```typescript
// This will open browser and wait for authorization
await client.authorize();
console.log("✅ Authorization successful!");
```

4. **Make API Requests**

```typescript
const response = await client.request("https://www.googleapis.com/oauth2/v2/userinfo");
const user = await response.json();
console.log("User:", user);
```

## Common Use Cases

### Web Application

```typescript
import express from "express";
import { createClient, SQLiteStore } from "@oauth-kit/sdk";

const app = express();

const client = createClient({
  provider: "google",
  clientId: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  redirectUri: "http://localhost:3000/auth/callback",
  store: new SQLiteStore("tokens.db")
});

await client.init();

app.get("/login", async (req, res) => {
  try {
    const userId = req.session.userId;
    await client.authorize(userId);
    res.redirect("/dashboard");
  } catch (err) {
    res.status(500).send("Authorization failed");
  }
});

app.get("/api/user", async (req, res) => {
  try {
    const userId = req.session.userId;
    const response = await client.request(
      "https://www.googleapis.com/oauth2/v2/userinfo",
      {},
      userId
    );
    const user = await response.json();
    res.json(user);
  } catch (err) {
    res.status(401).send("Not authorized");
  }
});

app.listen(3000);
```

### CLI Application

```typescript
#!/usr/bin/env node
import { createClient, SQLiteStore } from "@oauth-kit/sdk";
import { Command } from "commander";

const program = new Command();

program
  .name("my-cli")
  .description("CLI tool with OAuth")
  .version("1.0.0");

program
  .command("login")
  .description("Authenticate with Google")
  .action(async () => {
    const client = createClient({
      provider: "google",
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      redirectUri: "http://localhost:8787/callback",
      store: new SQLiteStore("~/.my-cli/tokens.db")
    });

    await client.init();
    await client.authorize();
    console.log("✅ Logged in successfully!");
  });

program
  .command("whoami")
  .description("Show current user")
  .action(async () => {
    const client = createClient({
      provider: "google",
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      redirectUri: "http://localhost:8787/callback",
      store: new SQLiteStore("~/.my-cli/tokens.db")
    });

    await client.init();
    const response = await client.request("https://www.googleapis.com/oauth2/v2/userinfo");
    const user = await response.json();
    console.log(`Logged in as: ${user.email}`);
  });

program.parse();
```

### Desktop Application (Electron)

```typescript
import { app, BrowserWindow } from "electron";
import { createClient, SQLiteStore } from "@oauth-kit/sdk";
import path from "path";

const client = createClient({
  provider: "google",
  clientId: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  redirectUri: "http://localhost:8787/callback",
  store: new SQLiteStore(path.join(app.getPath("userData"), "tokens.db"))
});

app.whenReady().then(async () => {
  await client.init();
  
  // Authorize on first run
  const tokens = await client.getToken();
  if (!tokens) {
    await client.authorize();
  }
  
  // Create main window
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600
  });
  
  mainWindow.loadFile("index.html");
});
```

### Serverless Function

```typescript
// Using MemoryStore since function is stateless
import { createClient, MemoryStore } from "@oauth-kit/sdk";

export async function handler(event) {
  // Get token from external storage (e.g., DynamoDB, Redis)
  const tokenData = await getTokenFromDatabase(event.userId);
  
  const store = new MemoryStore();
  if (tokenData) {
    await store.set("user", tokenData);
  }
  
  const client = createClient({
    provider: "google",
    clientId: process.env.GOOGLE_CLIENT_ID!,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    redirectUri: process.env.REDIRECT_URI!,
    store
  });
  
  await client.init();
  
  const response = await client.request("https://www.googleapis.com/oauth2/v2/userinfo");
  const user = await response.json();
  
  // Save updated token back to database
  const updatedToken = await client.getToken("user");
  if (updatedToken) {
    await saveTokenToDatabase(event.userId, updatedToken);
  }
  
  return {
    statusCode: 200,
    body: JSON.stringify(user)
  };
}
```

## Working with Multiple Accounts

```typescript
import { createClient, SQLiteStore } from "@oauth-kit/sdk";

const store = new SQLiteStore("tokens.db");

const client = createClient({
  provider: "google",
  clientId: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  redirectUri: "http://localhost:8787/callback",
  store
});

await client.init();

// Authorize multiple accounts
await client.authorize("work-account");
await client.authorize("personal-account");

// Use specific account
const workResponse = await client.request(
  "https://www.googleapis.com/oauth2/v2/userinfo",
  {},
  "work-account"
);

const personalResponse = await client.request(
  "https://www.googleapis.com/oauth2/v2/userinfo",
  {},
  "personal-account"
);

// List all accounts
const accounts = await store.list();
console.log("Accounts:", accounts);
```

## Error Handling Best Practices

### Graceful Degradation

```typescript
async function getUserInfo(client, accountKey) {
  try {
    const response = await client.request(
      "https://www.googleapis.com/oauth2/v2/userinfo",
      {},
      accountKey
    );
    return await response.json();
  } catch (err) {
    if (err.message.includes("No token available")) {
      console.log("User not logged in, redirecting to login...");
      await client.authorize(accountKey);
      return getUserInfo(client, accountKey); // Retry
    }
    
    if (err.message.includes("Token refresh failed")) {
      console.log("Token expired and refresh failed, need to re-authorize");
      await client.authorize(accountKey);
      return getUserInfo(client, accountKey);
    }
    
    throw err; // Re-throw unknown errors
  }
}
```

### Timeout Handling

```typescript
import { createClient, SQLiteStore } from "@oauth-kit/sdk";

const client = createClient({
  provider: "google",
  clientId: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  redirectUri: "http://localhost:8787/callback",
  store: new SQLiteStore("tokens.db")
});

await client.init();

try {
  // Authorization has 5-minute default timeout
  await client.authorize();
} catch (err) {
  if (err.message.includes("timeout")) {
    console.error("Authorization timed out. Please try again.");
    process.exit(1);
  }
  throw err;
}
```

### Logging

```typescript
const client = createClient({
  provider: "google",
  clientId: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  redirectUri: "http://localhost:8787/callback",
  store: new SQLiteStore("tokens.db"),
  logger: (msg, meta) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${msg}`, JSON.stringify(meta));
  }
});
```

## Testing

### Mocking for Tests

```typescript
import { describe, it, expect, vi } from "vitest";
import { createClient, MemoryStore } from "@oauth-kit/sdk";

describe("My App", () => {
  it("should fetch user data", async () => {
    const mockStore = new MemoryStore();
    await mockStore.set("test", {
      accessToken: "mock-token",
      tokenType: "Bearer"
    });
    
    const client = createClient({
      provider: {
        name: "mock",
        displayName: "Mock Provider",
        authorizationEndpoint: "https://mock.com/auth",
        tokenEndpoint: "https://mock.com/token",
        scopes: ["read"]
      },
      clientId: "test-client",
      redirectUri: "http://localhost:8787/callback",
      store: mockStore
    });
    
    await client.init();
    
    // Mock fetch
    global.fetch = vi.fn().mockResolvedValue({
      json: async () => ({ name: "Test User" })
    });
    
    const response = await client.request("https://api.example.com/user", {}, "test");
    const user = await response.json();
    
    expect(user.name).toBe("Test User");
  });
});
```

## Security Best Practices

### 1. Never Hardcode Credentials

❌ **Bad:**
```typescript
const client = createClient({
  clientId: "123456.apps.googleusercontent.com",
  clientSecret: "GOCSPX-abc123def456",
  // ...
});
```

✅ **Good:**
```typescript
const client = createClient({
  clientId: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  // ...
});
```

### 2. Secure Token Storage

For production, consider encrypting tokens at rest:

```typescript
import { createCipheriv, createDecipheriv, randomBytes } from "crypto";

class EncryptedSQLiteStore extends SQLiteStore {
  private key: Buffer;
  
  constructor(path: string, encryptionKey: string) {
    super(path);
    this.key = Buffer.from(encryptionKey, "hex");
  }
  
  async set(key: string, value: TokenSet): Promise<void> {
    const iv = randomBytes(16);
    const cipher = createCipheriv("aes-256-cbc", this.key, iv);
    const encrypted = Buffer.concat([
      cipher.update(JSON.stringify(value)),
      cipher.final()
    ]);
    
    const data = {
      ...value,
      accessToken: `${iv.toString("hex")}:${encrypted.toString("hex")}`
    };
    
    await super.set(key, data);
  }
  
  async get(key: string): Promise<TokenSet | null> {
    const data = await super.get(key);
    if (!data) return null;
    
    const [ivHex, encryptedHex] = data.accessToken.split(":");
    const iv = Buffer.from(ivHex, "hex");
    const encrypted = Buffer.from(encryptedHex, "hex");
    
    const decipher = createDecipheriv("aes-256-cbc", this.key, iv);
    const decrypted = Buffer.concat([
      decipher.update(encrypted),
      decipher.final()
    ]);
    
    return JSON.parse(decrypted.toString());
  }
}
```

### 3. Validate Redirect URIs

Always use exact redirect URI matching:

```typescript
// In your OAuth provider settings, whitelist exact URIs:
// ✅ http://localhost:8787/callback
// ✅ https://myapp.com/auth/callback

// ❌ Don't use wildcards or open redirects
```

### 4. Use HTTPS in Production

```typescript
const redirectUri = process.env.NODE_ENV === "production"
  ? "https://myapp.com/auth/callback"
  : "http://localhost:8787/callback";

const client = createClient({
  // ...
  redirectUri
});
```

## Troubleshooting

### Common Issues

#### "Unknown provider" Error

**Problem:** Provider name not found in registry

**Solution:**
```typescript
// Option 1: Use full manifest
const client = createClient({
  provider: {
    name: "custom",
    displayName: "Custom Provider",
    authorizationEndpoint: "https://...",
    tokenEndpoint: "https://...",
    scopes: ["read"]
  },
  // ...
});

// Option 2: Load from registry
import { ProviderRegistry } from "@oauth-kit/sdk";
const registry = ProviderRegistry.loadFromDir("./manifests");
const client = new OAuthClient({
  provider: "custom",
  // ...
}, registry);
```

#### "Authorization timeout" Error

**Problem:** User didn't complete authorization within 5 minutes

**Solution:** The timeout is currently hardcoded. For longer timeouts, you'll need to modify the source or complete authorization faster.

#### "Token refresh failed" Error

**Problem:** Refresh token is invalid or expired

**Solution:** Re-authorize the user:
```typescript
try {
  await client.request(url);
} catch (err) {
  if (err.message.includes("Token refresh failed")) {
    await client.authorize(); // Re-authorize
  }
}
```

#### Database Locked Error (SQLite)

**Problem:** SQLiteStore not closed properly

**Solution:**
```typescript
const store = new SQLiteStore("tokens.db");

try {
  // Use store...
} finally {
  store.close(); // Always close
}
```

## Next Steps

- Read the [API Documentation](./API.md) for detailed reference
- Check out the [examples](../packages/examples/) for more code samples
- Review the [provider catalog](../packages/provider-catalog/manifests/) for supported providers
- Contribute new providers or features via GitHub
