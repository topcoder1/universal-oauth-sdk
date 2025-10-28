import type { TokenSet, TokenStore } from "../types.js";

export class MemoryStore implements TokenStore {
  private mem = new Map<string, TokenSet>();
  async get(key: string) { return this.mem.get(key) ?? null; }
  async set(key: string, value: TokenSet) { this.mem.set(key, value); }
  async delete(key: string) { this.mem.delete(key); }
  async list(prefix = "") { 
    return Array.from(this.mem.keys()).filter(k => k.startsWith(prefix)); 
  }
}
