export interface ProviderManifest {
  name: string;
  displayName: string;
  authorizationEndpoint: string;
  tokenEndpoint: string;
  revocationEndpoint?: string;
  scopes: string[];
  tokenEndpointAuthMethods?: Array<"client_secret_post"|"client_secret_basic"|"none">;
  pkceRecommended?: boolean;
  deviceCodeSupported?: boolean;
  refreshTokenExpected?: boolean;
  extraAuthorizeParams?: Record<string, string>;
  notes?: string;
}

export interface TokenSet {
  accessToken: string;
  refreshToken?: string;
  idToken?: string;
  expiresAt?: number;
  scope?: string;
  tokenType?: string;
}

export interface TokenStore {
  get(key: string): Promise<TokenSet | null>;
  set(key: string, value: TokenSet): Promise<void>;
  delete(key: string): Promise<void>;
  list?(prefix?: string): Promise<string[]>;
  close?(): void;
}

export interface CreateClientOptions {
  provider: ProviderManifest | string;
  clientId: string;
  clientSecret?: string;
  redirectUri: string;
  store: TokenStore;
  logger?: (msg: string, meta?: Record<string, unknown>) => void;
  extraAuthorizeParams?: Record<string, string>;
}
