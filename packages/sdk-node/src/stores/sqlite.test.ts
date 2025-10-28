import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { SQLiteStore } from './sqlite.js';
import type { TokenSet } from '../types.js';
import { unlinkSync, existsSync } from 'node:fs';

describe('SQLiteStore', () => {
  const testDbPath = 'test-tokens.db';
  let store: SQLiteStore;

  beforeEach(() => {
    // Clean up any existing test database
    if (existsSync(testDbPath)) {
      unlinkSync(testDbPath);
    }
    store = new SQLiteStore(testDbPath);
  });

  afterEach(() => {
    // Close database connection before cleanup
    store.close();
    
    // Clean up test database
    if (existsSync(testDbPath)) {
      unlinkSync(testDbPath);
    }
  });

  describe('set and get', () => {
    it('should store and retrieve a token', async () => {
      const token: TokenSet = {
        accessToken: 'test-access-token',
        refreshToken: 'test-refresh-token',
        expiresAt: Date.now() + 3600000,
        tokenType: 'Bearer',
        scope: 'read write'
      };

      await store.set('test-key', token);
      const retrieved = await store.get('test-key');

      expect(retrieved).toEqual(token);
    });

    it('should return null for non-existent key', async () => {
      const result = await store.get('non-existent');
      expect(result).toBeNull();
    });

    it('should overwrite existing token', async () => {
      const token1: TokenSet = { accessToken: 'token1' };
      const token2: TokenSet = { accessToken: 'token2' };

      await store.set('key', token1);
      await store.set('key', token2);

      const retrieved = await store.get('key');
      expect(retrieved).toEqual(token2);
    });

    it('should persist data across instances', async () => {
      const token: TokenSet = { accessToken: 'persistent-token' };
      
      await store.set('key', token);
      
      // Create new instance with same database
      const store2 = new SQLiteStore(testDbPath);
      const retrieved = await store2.get('key');
      store2.close();
      
      expect(retrieved).toEqual(token);
    });
  });

  describe('delete', () => {
    it('should delete a token', async () => {
      const token: TokenSet = { accessToken: 'test-token' };
      
      await store.set('key', token);
      await store.delete('key');
      
      const retrieved = await store.get('key');
      expect(retrieved).toBeNull();
    });

    it('should not throw when deleting non-existent key', async () => {
      await expect(store.delete('non-existent')).resolves.not.toThrow();
    });
  });

  describe('list', () => {
    it('should list all keys', async () => {
      await store.set('key1', { accessToken: 'token1' });
      await store.set('key2', { accessToken: 'token2' });
      await store.set('key3', { accessToken: 'token3' });

      const keys = await store.list();
      expect(keys).toHaveLength(3);
      expect(keys).toContain('key1');
      expect(keys).toContain('key2');
      expect(keys).toContain('key3');
    });

    it('should filter by prefix', async () => {
      await store.set('user:1', { accessToken: 'token1' });
      await store.set('user:2', { accessToken: 'token2' });
      await store.set('app:1', { accessToken: 'token3' });

      const userKeys = await store.list('user:');
      expect(userKeys).toHaveLength(2);
      expect(userKeys).toContain('user:1');
      expect(userKeys).toContain('user:2');
      expect(userKeys).not.toContain('app:1');
    });

    it('should return empty array when no keys match', async () => {
      await store.set('key1', { accessToken: 'token1' });
      
      const keys = await store.list('nonexistent:');
      expect(keys).toHaveLength(0);
    });
  });

  describe('database initialization', () => {
    it('should create database file if it does not exist', () => {
      const newDbPath = 'new-test-db.db';
      
      // Ensure it doesn't exist
      if (existsSync(newDbPath)) {
        unlinkSync(newDbPath);
      }
      
      const newStore = new SQLiteStore(newDbPath);
      
      expect(existsSync(newDbPath)).toBe(true);
      
      // Clean up
      newStore.close();
      unlinkSync(newDbPath);
    });
  });
});
