# API Documentation

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Classes](#core-classes)
- [Token Stores](#token-stores)
- [Provider Registry](#provider-registry)
- [Types](#types)
- [Error Handling](#error-handling)

## Installation

```bash
pnpm add @oauth-kit/sdk
# or
npm install @oauth-kit/sdk
```

## Quick Start

```typescript
import { createClient, SQLiteStore } from "@oauth-kit/sdk";

// Create OAuth client
const client = createClient({
  provider: "google",
  clientId: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  redirectUri: "http://localhost:8787/callback",
  store: new SQLiteStore("tokens.db")
});

// Initialize the client
await client.init();

// Authorize and get tokens
await client.authorize();

// Make authenticated API requests
const response = await client.request("https://www.googleapis.com/oauth2/v2/userinfo");
const user = await response.json();
console.log(user);
```

## Core Classes

### `OAuthClient`

The main OAuth client class that handles the authorization flow.

#### Constructor

```typescript
new OAuthClient(options: CreateClientOptions, registry?: ProviderRegistry)
```

**Parameters:**
- `options.provider` - Provider manifest or provider name (string)
- `options.clientId` - OAuth client ID (required)
- `options.clientSecret` - OAuth client secret (optional for public clients)
- `options.redirectUri` - Redirect URI for OAuth callback (required)
- `options.store` - Token storage implementation (required)
- `options.logger` - Optional logging function
- `registry` - Optional provider registry for resolving provider names

**Throws:**
- Error if provider is unknown
- Error if clientId is empty
- Error if redirectUri is invalid

#### Methods

##### `async init(): Promise<void>`

Initializes the OAuth client and validates the provider configuration.

**Throws:**
- Error if provider is missing required endpoints
- Error if client initialization fails

**Example:**
```typescript
await client.init();
```

##### `async authorize(key?: string): Promise<TokenSet>`

Starts the OAuth authorization flow. Opens the browser and waits for callback.

**Parameters:**
- `key` - Storage key for the token (defaults to provider name)

**Returns:** `TokenSet` - The obtained tokens

**Throws:**
- Error on authorization timeout (default: 5 minutes)
- Error on OAuth errors from provider
- Error on state mismatch

**Example:**
```typescript
const tokens = await client.authorize("my-google-account");
```

##### `async getToken(key?: string): Promise<TokenSet | null>`

Retrieves stored tokens without refreshing.

**Parameters:**
- `key` - Storage key (defaults to provider name)

**Returns:** `TokenSet | null` - The stored tokens or null if not found

**Example:**
```typescript
const tokens = await client.getToken();
if (tokens) {
  console.log("Access token:", tokens.accessToken);
}
```

##### `async request(url: string, init?: RequestInit, key?: string): Promise<Response>`

Makes an authenticated HTTP request with automatic token refresh.

**Parameters:**
- `url` - The URL to request (required)
- `init` - Fetch API request options (optional)
- `key` - Storage key for tokens (defaults to provider name)

**Returns:** `Response` - Fetch API Response object

**Throws:**
- Error if URL is invalid
- Error if no token is available
- Error if token refresh fails
- Error if request fails

**Example:**
```typescript
// GET request
const response = await client.request("https://api.example.com/user");
const data = await response.json();

// POST request
const response = await client.request("https://api.example.com/data", {
  method: "POST",
  body: JSON.stringify({ name: "test" }),
  headers: { "Content-Type": "application/json" }
});
```

### `createClient()`

Helper function to create an OAuth client with a simplified API.

```typescript
function createClient(options: CreateClientOptions & { registry?: ProviderRegistry })
```

**Returns:** Object with methods:
- `init(): Promise<void>`
- `authorize(key?: string): Promise<TokenSet>`
- `getToken(key?: string): Promise<TokenSet | null>`
- `request(url: string, init?: RequestInit, key?: string): Promise<Response>`

**Example:**
```typescript
const client = createClient({
  provider: "github",
  clientId: "your-client-id",
  clientSecret: "your-secret",
  redirectUri: "http://localhost:8787/callback",
  store: new MemoryStore()
});
```

## Token Stores

### `MemoryStore`

In-memory token storage. Tokens are lost when the process exits.

```typescript
import { MemoryStore } from "@oauth-kit/sdk";

const store = new MemoryStore();
```

**Methods:**
- `async get(key: string): Promise<TokenSet | null>`
- `async set(key: string, value: TokenSet): Promise<void>`
- `async delete(key: string): Promise<void>`
- `async list(prefix?: string): Promise<string[]>`

**Use Cases:**
- Development and testing
- Short-lived processes
- Serverless functions with external token storage

### `SQLiteStore`

Persistent token storage using SQLite database.

```typescript
import { SQLiteStore } from "@oauth-kit/sdk";

const store = new SQLiteStore("tokens.db");
```

**Constructor:**
```typescript
new SQLiteStore(path?: string)
```

**Parameters:**
- `path` - Database file path (default: "tokens.db")

**Methods:**
- `async get(key: string): Promise<TokenSet | null>`
- `async set(key: string, value: TokenSet): Promise<void>`
- `async delete(key: string): Promise<void>`
- `async list(prefix?: string): Promise<string[]>`
- `close(): void` - Close database connection

**Important:** Always call `close()` when done to release the database lock.

**Example:**
```typescript
const store = new SQLiteStore("tokens.db");

// Use the store...
await store.set("user:123", tokens);

// Close when done
store.close();
```

### Custom Token Store

Implement the `TokenStore` interface for custom storage:

```typescript
interface TokenStore {
  get(key: string): Promise<TokenSet | null>;
  set(key: string, value: TokenSet): Promise<void>;
  delete(key: string): Promise<void>;
  list?(prefix?: string): Promise<string[]>;
}
```

**Example:**
```typescript
class RedisStore implements TokenStore {
  constructor(private redis: RedisClient) {}
  
  async get(key: string): Promise<TokenSet | null> {
    const data = await this.redis.get(key);
    return data ? JSON.parse(data) : null;
  }
  
  async set(key: string, value: TokenSet): Promise<void> {
    await this.redis.set(key, JSON.stringify(value));
  }
  
  async delete(key: string): Promise<void> {
    await this.redis.del(key);
  }
  
  async list(prefix = ""): Promise<string[]> {
    return await this.redis.keys(`${prefix}*`);
  }
}
```

## Provider Registry

### `ProviderRegistry`

Manages OAuth provider configurations.

```typescript
import { ProviderRegistry } from "@oauth-kit/sdk";
```

#### Constructor

```typescript
new ProviderRegistry(manifests?: ProviderManifest[])
```

#### Methods

##### `add(manifest: ProviderManifest): void`

Add a provider manifest to the registry.

```typescript
registry.add({
  name: "custom-provider",
  displayName: "Custom Provider",
  authorizationEndpoint: "https://provider.com/oauth/authorize",
  tokenEndpoint: "https://provider.com/oauth/token",
  scopes: ["read", "write"]
});
```

##### `get(name: string): ProviderManifest | undefined`

Get a provider manifest by name.

```typescript
const google = registry.get("google");
```

##### `static loadFromDir(dir: string): ProviderRegistry`

Load all provider manifests from a directory.

```typescript
const registry = ProviderRegistry.loadFromDir("./manifests");
```

## Types

### `TokenSet`

```typescript
interface TokenSet {
  accessToken: string;
  refreshToken?: string;
  idToken?: string;
  expiresAt?: number;
  scope?: string;
  tokenType?: string;
}
```

### `ProviderManifest`

```typescript
interface ProviderManifest {
  name: string;
  displayName: string;
  authorizationEndpoint: string;
  tokenEndpoint: string;
  revocationEndpoint?: string;
  scopes: string[];
  tokenEndpointAuthMethods?: Array<"client_secret_post" | "client_secret_basic" | "none">;
  pkceRecommended?: boolean;
  deviceCodeSupported?: boolean;
  refreshTokenExpected?: boolean;
  extraAuthorizeParams?: Record<string, string>;
  notes?: string;
}
```

### `CreateClientOptions`

```typescript
interface CreateClientOptions {
  provider: ProviderManifest | string;
  clientId: string;
  clientSecret?: string;
  redirectUri: string;
  store: TokenStore;
  logger?: (msg: string, meta?: Record<string, unknown>) => void;
  extraAuthorizeParams?: Record<string, string>;
}
```

## Error Handling

### Common Errors

#### Invalid Configuration
```typescript
try {
  const client = createClient({
    provider: "unknown",
    clientId: "",
    redirectUri: "invalid-url",
    store: new MemoryStore()
  });
} catch (err) {
  // Error: Unknown provider: "unknown"
  // Error: clientId is required and cannot be empty
  // Error: Invalid redirectUri: invalid-url
}
```

#### Authorization Timeout
```typescript
try {
  await client.authorize();
} catch (err) {
  // Error: Authorization timeout after 300000ms
}
```

#### Token Refresh Failure
```typescript
try {
  await client.request("https://api.example.com/data");
} catch (err) {
  // Error: Token refresh failed for key "google"
}
```

### Custom Error Handling

```typescript
const client = createClient({
  provider: "google",
  clientId: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  redirectUri: "http://localhost:8787/callback",
  store: new SQLiteStore("tokens.db"),
  logger: (msg, meta) => {
    console.log(`[OAuth] ${msg}`, meta);
  }
});

try {
  await client.init();
  await client.authorize();
  const response = await client.request("https://www.googleapis.com/oauth2/v2/userinfo");
  const user = await response.json();
  console.log("User:", user);
} catch (err) {
  if (err instanceof Error) {
    console.error("OAuth error:", err.message);
  }
}
```

## Advanced Usage

### Multiple Providers

```typescript
const googleClient = createClient({
  provider: "google",
  clientId: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  redirectUri: "http://localhost:8787/callback",
  store: new SQLiteStore("tokens.db")
});

const githubClient = createClient({
  provider: "github",
  clientId: process.env.GITHUB_CLIENT_ID!,
  clientSecret: process.env.GITHUB_CLIENT_SECRET!,
  redirectUri: "http://localhost:8787/callback",
  store: new SQLiteStore("tokens.db")
});

await googleClient.init();
await githubClient.init();

await googleClient.authorize("google-account");
await githubClient.authorize("github-account");
```

### Custom Scopes

```typescript
const client = createClient({
  provider: {
    name: "google",
    displayName: "Google",
    authorizationEndpoint: "https://accounts.google.com/o/oauth2/v2/auth",
    tokenEndpoint: "https://oauth2.googleapis.com/token",
    scopes: ["openid", "email", "profile", "https://www.googleapis.com/auth/drive.readonly"]
  },
  clientId: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  redirectUri: "http://localhost:8787/callback",
  store: new SQLiteStore("tokens.db")
});
```

### Token Inspection

```typescript
const tokens = await client.getToken();

if (tokens) {
  console.log("Access Token:", tokens.accessToken);
  console.log("Refresh Token:", tokens.refreshToken);
  console.log("Expires At:", new Date(tokens.expiresAt! * 1000));
  console.log("Scope:", tokens.scope);
  console.log("Token Type:", tokens.tokenType);
}
```
