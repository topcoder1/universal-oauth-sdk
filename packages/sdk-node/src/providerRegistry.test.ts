import { describe, it, expect, beforeEach } from 'vitest';
import { ProviderRegistry } from './providerRegistry.js';
import type { ProviderManifest } from './types.js';

describe('ProviderRegistry', () => {
  let registry: ProviderRegistry;
  let googleManifest: ProviderManifest;
  let githubManifest: ProviderManifest;

  beforeEach(() => {
    registry = new ProviderRegistry();
    
    googleManifest = {
      name: 'google',
      displayName: 'Google',
      authorizationEndpoint: 'https://accounts.google.com/o/oauth2/v2/auth',
      tokenEndpoint: 'https://oauth2.googleapis.com/token',
      scopes: ['openid', 'email', 'profile']
    };

    githubManifest = {
      name: 'github',
      displayName: 'GitHub',
      authorizationEndpoint: 'https://github.com/login/oauth/authorize',
      tokenEndpoint: 'https://github.com/login/oauth/access_token',
      scopes: ['user', 'repo']
    };
  });

  describe('Constructor', () => {
    it('should create empty registry', () => {
      const emptyRegistry = new ProviderRegistry();
      expect(emptyRegistry.get('google')).toBeUndefined();
    });

    it('should create registry with initial manifests', () => {
      const registryWithManifests = new ProviderRegistry([googleManifest, githubManifest]);
      expect(registryWithManifests.get('google')).toEqual(googleManifest);
      expect(registryWithManifests.get('github')).toEqual(githubManifest);
    });
  });

  describe('add', () => {
    it('should add a manifest', () => {
      registry.add(googleManifest);
      expect(registry.get('google')).toEqual(googleManifest);
    });

    it('should add multiple manifests', () => {
      registry.add(googleManifest);
      registry.add(githubManifest);
      
      expect(registry.get('google')).toEqual(googleManifest);
      expect(registry.get('github')).toEqual(githubManifest);
    });

    it('should overwrite existing manifest with same name', () => {
      registry.add(googleManifest);
      
      const updatedManifest = {
        ...googleManifest,
        displayName: 'Google Updated'
      };
      
      registry.add(updatedManifest);
      expect(registry.get('google')?.displayName).toBe('Google Updated');
    });
  });

  describe('get', () => {
    beforeEach(() => {
      registry.add(googleManifest);
      registry.add(githubManifest);
    });

    it('should retrieve existing manifest', () => {
      const manifest = registry.get('google');
      expect(manifest).toEqual(googleManifest);
    });

    it('should return undefined for non-existent manifest', () => {
      const manifest = registry.get('non-existent');
      expect(manifest).toBeUndefined();
    });

    it('should be case-sensitive', () => {
      const manifest = registry.get('Google');
      expect(manifest).toBeUndefined();
    });
  });

  describe('loadFromDir', () => {
    it('should load manifests from directory', () => {
      // This tests the actual provider catalog
      const catalogRegistry = ProviderRegistry.loadFromDir(
        '../provider-catalog/manifests'
      );

      // Should have loaded Google and GitHub manifests
      const google = catalogRegistry.get('google');
      const github = catalogRegistry.get('github');

      expect(google).toBeDefined();
      expect(google?.name).toBe('google');
      expect(google?.authorizationEndpoint).toContain('google');

      expect(github).toBeDefined();
      expect(github?.name).toBe('github');
      expect(github?.authorizationEndpoint).toContain('github');
    });
  });

  describe('Edge Cases', () => {
    it('should handle manifest with optional fields', () => {
      const manifestWithOptionals: ProviderManifest = {
        name: 'custom',
        displayName: 'Custom Provider',
        authorizationEndpoint: 'https://custom.com/auth',
        tokenEndpoint: 'https://custom.com/token',
        revocationEndpoint: 'https://custom.com/revoke',
        scopes: ['read'],
        pkceRecommended: true,
        deviceCodeSupported: false,
        refreshTokenExpected: true,
        notes: 'Test notes'
      };

      registry.add(manifestWithOptionals);
      const retrieved = registry.get('custom');

      expect(retrieved).toEqual(manifestWithOptionals);
      expect(retrieved?.revocationEndpoint).toBe('https://custom.com/revoke');
      expect(retrieved?.pkceRecommended).toBe(true);
    });

    it('should handle manifest with minimal required fields', () => {
      const minimalManifest: ProviderManifest = {
        name: 'minimal',
        displayName: 'Minimal',
        authorizationEndpoint: 'https://minimal.com/auth',
        tokenEndpoint: 'https://minimal.com/token',
        scopes: []
      };

      registry.add(minimalManifest);
      const retrieved = registry.get('minimal');

      expect(retrieved).toEqual(minimalManifest);
      expect(retrieved?.scopes).toEqual([]);
    });
  });
});
