import { generators, Issuer, BaseClient } from "openid-client";
import type { CreateClientOptions, TokenSet, ProviderManifest, TokenStore } from "./types.js";
import { ProviderRegistry } from "./providerRegistry.js";
import http from "node:http";
import { URL } from "node:url";

export * from "./types.js";
export { ProviderRegistry } from "./providerRegistry.js";
export { SQLiteStore } from "./stores/sqlite.js";
export { MemoryStore } from "./stores/memory.js";
export { EncryptedSQLiteStore } from "./stores/encrypted.js";
export { authorizeDevice } from "./deviceFlow.js";
export type { DeviceAuthorizationResponse, DeviceFlowOptions } from "./deviceFlow.js";

export class OAuthClient {
  private manifest: ProviderManifest;
  private client!: BaseClient;
  private store: TokenStore;
  private clientId: string;
  private clientSecret?: string;
  private redirectUri: string;
  private logger: (msg: string, meta?: Record<string, unknown>) => void;

  constructor(opts: CreateClientOptions, reg?: ProviderRegistry) {
    const manifest = typeof opts.provider === "string" ? reg?.get(opts.provider) : opts.provider;
    if (!manifest) {
      const providerName = typeof opts.provider === "string" ? opts.provider : "unknown";
      throw new Error(`Unknown provider: "${providerName}". Provide a valid manifest or registry.`);
    }
    
    // Validate required fields
    if (!opts.clientId || opts.clientId.trim() === "") {
      throw new Error("clientId is required and cannot be empty");
    }
    if (!opts.redirectUri || opts.redirectUri.trim() === "") {
      throw new Error("redirectUri is required and cannot be empty");
    }
    
    // Validate redirectUri format
    try {
      new URL(opts.redirectUri);
    } catch (err) {
      throw new Error(`Invalid redirectUri: ${opts.redirectUri}`);
    }
    
    this.manifest = manifest;
    this.clientId = opts.clientId;
    this.clientSecret = opts.clientSecret;
    this.redirectUri = opts.redirectUri;
    this.store = opts.store;
    this.logger = opts.logger ?? (() => {});
  }

  async init() {
    // Validate manifest has required endpoints
    if (!this.manifest.authorizationEndpoint) {
      throw new Error(`Provider "${this.manifest.name}" missing authorizationEndpoint`);
    }
    if (!this.manifest.tokenEndpoint) {
      throw new Error(`Provider "${this.manifest.name}" missing tokenEndpoint`);
    }
    
    const issuer = {
      issuer: this.manifest.displayName,
      authorization_endpoint: this.manifest.authorizationEndpoint,
      token_endpoint: this.manifest.tokenEndpoint,
      revocation_endpoint: this.manifest.revocationEndpoint
    } as const;
    
    try {
      const Iss = new Issuer(issuer);
      this.client = new Iss.Client({
        client_id: this.clientId,
        client_secret: this.clientSecret
      });
    } catch (err) {
      if (err instanceof Error) {
        throw new Error(`Failed to initialize OAuth client: ${err.message}`);
      }
      throw err;
    }
  }

  async authorize(key = this.manifest.name) {
    const codeVerifier = generators.codeVerifier();
    const codeChallenge = generators.codeChallenge(codeVerifier);
    const state = generators.state();
    const nonce = generators.nonce();

    const url = new URL(this.manifest.authorizationEndpoint);
    url.searchParams.set("response_type", "code");
    url.searchParams.set("client_id", this.clientId);
    url.searchParams.set("redirect_uri", this.redirectUri);
    url.searchParams.set("scope", this.manifest.scopes.join(" "));
    url.searchParams.set("code_challenge", codeChallenge);
    url.searchParams.set("code_challenge_method", "S256");
    url.searchParams.set("state", state);
    url.searchParams.set("nonce", nonce);
    for (const [k,v] of Object.entries(this.manifest.extraAuthorizeParams ?? {})) url.searchParams.set(k, v);

    // Open system browser if available (best-effort)
    try {
      const open = await import("node:child_process");
      const cmd = process.platform === "darwin" ? "open" : process.platform === "win32" ? "start" : "xdg-open";
      open.exec(`${cmd} "${url.toString()}"`);
    } catch {}

    const code = await this.waitForCallback(this.redirectUri, state);
    const params: any = {
      code,
      redirect_uri: this.redirectUri,
      code_verifier: codeVerifier
    };
    const token = await this.client.callback(this.redirectUri, params, { state, nonce });
    const tokens: TokenSet = {
      accessToken: token.access_token!,
      refreshToken: token.refresh_token ?? undefined,
      idToken: token.id_token ?? undefined,
      expiresAt: token.expires_at ?? undefined,
      scope: token.scope ?? undefined,
      tokenType: token.token_type ?? "Bearer"
    };
    await this.store.set(key, tokens);
    return tokens;
  }

  private waitForCallback(redirectUri: string, expectedState: string, timeoutMs = 300000): Promise<string> {
    return new Promise((resolve, reject) => {
      const u = new URL(redirectUri);
      let timeoutId: NodeJS.Timeout;
      
      const server = http.createServer((req, res) => {
        if (!req.url) return;
        const incoming = new URL(req.url, `http://${req.headers.host}`);
        if (incoming.pathname !== u.pathname) {
          res.writeHead(404).end();
          return;
        }
        
        // Check for error response
        const error = incoming.searchParams.get("error");
        if (error) {
          const errorDesc = incoming.searchParams.get("error_description") || error;
          res.writeHead(400, { "Content-Type": "text/plain" });
          res.end(`Authorization failed: ${errorDesc}`);
          clearTimeout(timeoutId);
          server.close();
          return reject(new Error(`OAuth error: ${errorDesc}`));
        }
        
        const code = incoming.searchParams.get("code");
        const state = incoming.searchParams.get("state");
        if (!code || !state || state !== expectedState) {
          res.writeHead(400).end("Invalid state or missing code");
          clearTimeout(timeoutId);
          server.close();
          return reject(new Error("Invalid callback: state mismatch or missing code"));
        }
        res.writeHead(200, { "Content-Type": "text/plain" });
        res.end("Authorization complete. You can close this window.");
        clearTimeout(timeoutId);
        server.close();
        resolve(code);
      });
      
      const port = Number(u.port) || 8787;
      server.on('error', (err) => {
        clearTimeout(timeoutId);
        reject(new Error(`Failed to start callback server: ${err.message}`));
      });
      
      server.listen(port, u.hostname, () => {
        this.logger("callback_server_listening", { host: u.hostname, port });
        
        // Set timeout
        timeoutId = setTimeout(() => {
          server.close();
          reject(new Error(`Authorization timeout after ${timeoutMs}ms`));
        }, timeoutMs);
      });
    });
  }

  async getToken(key = this.manifest.name): Promise<TokenSet | null> {
    return await this.store.get(key);
  }

  async refreshIfNeeded(key = this.manifest.name): Promise<TokenSet | null> {
    const t = await this.store.get(key);
    if (!t) return null;
    const now = Math.floor(Date.now() / 1000);
    if (t.expiresAt && t.expiresAt - now > 60) return t; // fresh
    if (!t.refreshToken) return t; // cannot refresh
    const refreshed = await this.client.refresh(t.refreshToken);
    const next: TokenSet = {
      accessToken: refreshed.access_token!,
      refreshToken: refreshed.refresh_token ?? t.refreshToken,
      idToken: refreshed.id_token ?? t.idToken,
      expiresAt: refreshed.expires_at ?? t.expiresAt,
      scope: refreshed.scope ?? t.scope,
      tokenType: refreshed.token_type ?? t.tokenType
    };
    await this.store.set(key, next);
    return next;
  }

  async request(url: string, init: RequestInit = {}, key = this.manifest.name) {
    // Validate URL
    try {
      new URL(url);
    } catch (err) {
      throw new Error(`Invalid URL: ${url}`);
    }
    
    const t = await this.refreshIfNeeded(key);
    if (!t) {
      throw new Error(`No token available for key "${key}". Call authorize() first.`);
    }
    
    const headers = new Headers(init.headers ?? {});
    headers.set("Authorization", `${t.tokenType || 'Bearer'} ${t.accessToken}`);
    headers.set("Accept", "application/json");
    
    try {
      const res = await fetch(url, { ...init, headers });
      
      if (res.status === 401) {
        // Attempt one refresh then retry
        this.logger("token_expired_retrying", { key, url });
        await this.refreshIfNeeded(key);
        const t2 = await this.getToken(key);
        
        if (!t2) {
          throw new Error(`Token refresh failed for key "${key}"`);
        }
        
        headers.set("Authorization", `${t2.tokenType || 'Bearer'} ${t2.accessToken}`);
        return fetch(url, { ...init, headers });
      }
      
      return res;
    } catch (err) {
      if (err instanceof Error) {
        throw new Error(`Request failed: ${err.message}`);
      }
      throw err;
    }
  }

  async authorizeDevice(
    key = this.manifest.name,
    onUserCode?: (userCode: string, verificationUri: string) => void
  ): Promise<TokenSet> {
    const { authorizeDevice: deviceFlow } = await import("./deviceFlow.js");
    
    return deviceFlow(
      {
        client: this.client,
        store: this.store,
        scopes: this.manifest.scopes,
        onUserCode,
        logger: this.logger
      },
      key
    );
  }
}

export function createClient(opts: CreateClientOptions & { registry?: ProviderRegistry }) {
  const client = new OAuthClient(opts, opts.registry);
  return {
    init: () => client.init(),
    authorize: (key?: string) => client.authorize(key),
    authorizeDevice: (key?: string, onUserCode?: (code: string, uri: string) => void) => 
      client.authorizeDevice(key, onUserCode),
    getToken: (key?: string) => client.getToken(key),
    request: (url: string, init?: RequestInit, key?: string) => client.request(url, init, key)
  };
}
