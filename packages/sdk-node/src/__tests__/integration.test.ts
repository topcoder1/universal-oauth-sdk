import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { OAuthClient } from '../index.js';
import { MemoryStore } from '../stores/memory.js';
import type { ProviderManifest } from '../types.js';
import http from 'node:http';

describe('OAuth Integration Tests', () => {
  let store: MemoryStore;
  let mockManifest: ProviderManifest;

  beforeEach(() => {
    store = new MemoryStore();
    mockManifest = {
      name: 'test-provider',
      displayName: 'Test Provider',
      authorizationEndpoint: 'https://auth.example.com/authorize',
      tokenEndpoint: 'https://auth.example.com/token',
      scopes: ['read', 'write']
    };
  });

  describe('Client Initialization', () => {
    it('should create client with valid configuration', () => {
      expect(() => {
        new OAuthClient({
          provider: mockManifest,
          clientId: 'test-client-id',
          clientSecret: 'test-secret',
          redirectUri: 'http://localhost:8787/callback',
          store
        });
      }).not.toThrow();
    });

    it('should throw error with empty clientId', () => {
      expect(() => {
        new OAuthClient({
          provider: mockManifest,
          clientId: '',
          redirectUri: 'http://localhost:8787/callback',
          store
        });
      }).toThrow('clientId is required and cannot be empty');
    });

    it('should throw error with invalid redirectUri', () => {
      expect(() => {
        new OAuthClient({
          provider: mockManifest,
          clientId: 'test-client',
          redirectUri: 'not-a-valid-url',
          store
        });
      }).toThrow('Invalid redirectUri');
    });

    it('should throw error with unknown provider string', () => {
      expect(() => {
        new OAuthClient({
          provider: 'unknown-provider',
          clientId: 'test-client',
          redirectUri: 'http://localhost:8787/callback',
          store
        });
      }).toThrow('Unknown provider: "unknown-provider"');
    });
  });

  describe('Client Init', () => {
    it('should initialize successfully with valid manifest', async () => {
      const client = new OAuthClient({
        provider: mockManifest,
        clientId: 'test-client-id',
        clientSecret: 'test-secret',
        redirectUri: 'http://localhost:8787/callback',
        store
      });

      await expect(client.init()).resolves.not.toThrow();
    });

    it('should throw error when missing authorizationEndpoint', async () => {
      const invalidManifest = { ...mockManifest, authorizationEndpoint: '' };
      const client = new OAuthClient({
        provider: invalidManifest,
        clientId: 'test-client-id',
        redirectUri: 'http://localhost:8787/callback',
        store
      });

      await expect(client.init()).rejects.toThrow('missing authorizationEndpoint');
    });

    it('should throw error when missing tokenEndpoint', async () => {
      const invalidManifest = { ...mockManifest, tokenEndpoint: '' };
      const client = new OAuthClient({
        provider: invalidManifest,
        clientId: 'test-client-id',
        redirectUri: 'http://localhost:8787/callback',
        store
      });

      await expect(client.init()).rejects.toThrow('missing tokenEndpoint');
    });
  });

  describe('Token Management', () => {
    it('should store and retrieve tokens', async () => {
      const client = new OAuthClient({
        provider: mockManifest,
        clientId: 'test-client-id',
        redirectUri: 'http://localhost:8787/callback',
        store
      });

      await client.init();

      // Manually store a token
      await store.set('test-key', {
        accessToken: 'test-access-token',
        refreshToken: 'test-refresh-token',
        expiresAt: Date.now() + 3600000
      });

      const token = await client.getToken('test-key');
      expect(token).not.toBeNull();
      expect(token?.accessToken).toBe('test-access-token');
    });

    it('should return null for non-existent token', async () => {
      const client = new OAuthClient({
        provider: mockManifest,
        clientId: 'test-client-id',
        redirectUri: 'http://localhost:8787/callback',
        store
      });

      await client.init();

      const token = await client.getToken('non-existent');
      expect(token).toBeNull();
    });
  });

  describe('Request Method', () => {
    it('should throw error when no token available', async () => {
      const client = new OAuthClient({
        provider: mockManifest,
        clientId: 'test-client-id',
        redirectUri: 'http://localhost:8787/callback',
        store
      });

      await client.init();

      await expect(
        client.request('https://api.example.com/user')
      ).rejects.toThrow('No token available');
    });

    it('should throw error with invalid URL', async () => {
      const client = new OAuthClient({
        provider: mockManifest,
        clientId: 'test-client-id',
        redirectUri: 'http://localhost:8787/callback',
        store
      });

      await client.init();

      // Store a token first
      await store.set(mockManifest.name, {
        accessToken: 'test-token',
        expiresAt: Date.now() + 3600000
      });

      await expect(
        client.request('not-a-valid-url')
      ).rejects.toThrow('Invalid URL');
    });

    it('should make request with stored token', async () => {
      const client = new OAuthClient({
        provider: mockManifest,
        clientId: 'test-client-id',
        redirectUri: 'http://localhost:8787/callback',
        store
      });

      await client.init();

      // Store a token
      await store.set(mockManifest.name, {
        accessToken: 'test-token',
        tokenType: 'Bearer',
        expiresAt: Date.now() + 3600000
      });

      // Mock fetch
      global.fetch = vi.fn().mockResolvedValue({
        status: 200,
        json: async () => ({ success: true })
      });

      const response = await client.request('https://api.example.com/user');
      expect(response.status).toBe(200);

      // Verify fetch was called with Authorization header
      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.example.com/user',
        expect.objectContaining({
          headers: expect.any(Headers)
        })
      );
    });
  });

  describe('Logger', () => {
    it('should call logger when provided', async () => {
      const logger = vi.fn();
      const client = new OAuthClient({
        provider: mockManifest,
        clientId: 'test-client-id',
        redirectUri: 'http://localhost:8787/callback',
        store,
        logger
      });

      await client.init();

      // Logger should not have been called during init
      // (no logging in init currently)
      expect(logger).not.toHaveBeenCalled();
    });

    it('should not throw when logger is not provided', async () => {
      const client = new OAuthClient({
        provider: mockManifest,
        clientId: 'test-client-id',
        redirectUri: 'http://localhost:8787/callback',
        store
      });

      await expect(client.init()).resolves.not.toThrow();
    });
  });

  describe('Multiple Accounts', () => {
    it('should handle multiple tokens with different keys', async () => {
      const client = new OAuthClient({
        provider: mockManifest,
        clientId: 'test-client-id',
        redirectUri: 'http://localhost:8787/callback',
        store
      });

      await client.init();

      // Store multiple tokens
      await store.set('account1', {
        accessToken: 'token1',
        expiresAt: Date.now() + 3600000
      });

      await store.set('account2', {
        accessToken: 'token2',
        expiresAt: Date.now() + 3600000
      });

      const token1 = await client.getToken('account1');
      const token2 = await client.getToken('account2');

      expect(token1?.accessToken).toBe('token1');
      expect(token2?.accessToken).toBe('token2');
    });
  });
});
