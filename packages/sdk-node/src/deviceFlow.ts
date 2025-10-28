import type { BaseClient } from "openid-client";
import type { TokenSet, TokenStore } from "./types.js";

export interface DeviceAuthorizationResponse {
  deviceCode: string;
  userCode: string;
  verificationUri: string;
  verificationUriComplete?: string;
  expiresIn: number;
  interval: number;
}

export interface DeviceFlowOptions {
  client: BaseClient;
  store: TokenStore;
  scopes?: string[];
  pollInterval?: number;
  timeout?: number;
  onUserCode?: (userCode: string, verificationUri: string) => void;
  logger?: (msg: string, meta?: Record<string, unknown>) => void;
}

/**
 * Device Authorization Flow (RFC 8628)
 * For devices with limited input capabilities (CLI, TV, IoT)
 * 
 * @example
 * ```typescript
 * const result = await authorizeDevice({
 *   client,
 *   store,
 *   scopes: ['openid', 'email'],
 *   onUserCode: (code, uri) => {
 *     console.log(`Visit: ${uri}`);
 *     console.log(`Code: ${code}`);
 *   }
 * });
 * ```
 */
export async function authorizeDevice(
  options: DeviceFlowOptions,
  key = "device"
): Promise<TokenSet> {
  const {
    client,
    store,
    scopes = [],
    pollInterval = 5000,
    timeout = 300000, // 5 minutes
    onUserCode,
    logger = () => {}
  } = options;

  // Step 1: Request device code
  logger("device_authorization_start", { scopes });
  
  const deviceAuthResponse = await requestDeviceCode(client, scopes);
  
  logger("device_code_received", {
    userCode: deviceAuthResponse.userCode,
    verificationUri: deviceAuthResponse.verificationUri,
    expiresIn: deviceAuthResponse.expiresIn
  });

  // Step 2: Display user code to user
  if (onUserCode) {
    onUserCode(deviceAuthResponse.userCode, deviceAuthResponse.verificationUri);
  }

  // Step 3: Poll for authorization
  const tokens = await pollForToken(
    client,
    deviceAuthResponse,
    pollInterval,
    timeout,
    logger
  );

  // Step 4: Store tokens
  await store.set(key, tokens);
  
  logger("device_authorization_complete", { key });
  
  return tokens;
}

/**
 * Request device code from authorization server
 */
async function requestDeviceCode(
  client: BaseClient,
  scopes: string[]
): Promise<DeviceAuthorizationResponse> {
  const issuer = client.issuer;
  
  // Check if device authorization endpoint exists
  const deviceAuthEndpoint = (issuer as any).device_authorization_endpoint;
  
  if (!deviceAuthEndpoint) {
    throw new Error(
      "Provider does not support device authorization flow. " +
      "Missing device_authorization_endpoint in provider configuration."
    );
  }

  const params = new URLSearchParams({
    client_id: client.metadata.client_id!,
    scope: scopes.join(" ")
  });

  const response = await fetch(deviceAuthEndpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: params.toString()
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Device authorization request failed: ${error}`);
  }

  const data = await response.json();

  return {
    deviceCode: data.device_code,
    userCode: data.user_code,
    verificationUri: data.verification_uri,
    verificationUriComplete: data.verification_uri_complete,
    expiresIn: data.expires_in,
    interval: data.interval || 5
  };
}

/**
 * Poll token endpoint until user authorizes or timeout
 */
async function pollForToken(
  client: BaseClient,
  deviceAuth: DeviceAuthorizationResponse,
  pollInterval: number,
  timeout: number,
  logger: (msg: string, meta?: Record<string, unknown>) => void
): Promise<TokenSet> {
  const startTime = Date.now();
  const interval = Math.max(deviceAuth.interval * 1000, pollInterval);
  
  logger("polling_start", { interval, timeout });

  while (true) {
    // Check timeout
    if (Date.now() - startTime > timeout) {
      throw new Error(`Device authorization timeout after ${timeout}ms`);
    }

    // Wait before polling
    await sleep(interval);

    try {
      logger("polling_attempt", {});
      
      const tokenSet = await client.grant({
        grant_type: "urn:ietf:params:oauth:grant-type:device_code",
        device_code: deviceAuth.deviceCode,
        client_id: client.metadata.client_id!
      });

      logger("polling_success", {});

      return {
        accessToken: tokenSet.access_token!,
        refreshToken: tokenSet.refresh_token,
        idToken: tokenSet.id_token,
        expiresAt: tokenSet.expires_at,
        scope: tokenSet.scope,
        tokenType: tokenSet.token_type || "Bearer"
      };
      
    } catch (error: any) {
      // Handle expected errors during polling
      if (error.error === "authorization_pending") {
        // User hasn't authorized yet, continue polling
        logger("polling_pending", {});
        continue;
      }
      
      if (error.error === "slow_down") {
        // Server requests slower polling
        logger("polling_slow_down", {});
        await sleep(interval);
        continue;
      }
      
      if (error.error === "access_denied") {
        throw new Error("User denied authorization");
      }
      
      if (error.error === "expired_token") {
        throw new Error("Device code expired. Please try again.");
      }

      // Unknown error
      throw new Error(`Device authorization failed: ${error.message || error.error || "Unknown error"}`);
    }
  }
}

/**
 * Sleep utility
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
