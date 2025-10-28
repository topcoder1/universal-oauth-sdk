import { createCipheriv, createDecipheriv, randomBytes } from "node:crypto";
import { SQLiteStore } from "./sqlite.js";
import type { TokenSet } from "../types.js";

/**
 * Encrypted token storage using AES-256-CBC encryption.
 * Extends SQLiteStore to provide encryption at rest.
 * 
 * @example
 * ```typescript
 * // Generate encryption key (do this once):
 * // node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
 * 
 * const store = new EncryptedSQLiteStore(
 *   "tokens.db",
 *   process.env.ENCRYPTION_KEY! // 64-char hex string
 * );
 * ```
 */
export class EncryptedSQLiteStore extends SQLiteStore {
  private encryptionKey: Buffer;
  private algorithm = "aes-256-cbc";

  /**
   * Create an encrypted SQLite token store.
   * 
   * @param path - Path to SQLite database file
   * @param encryptionKey - 64-character hex string (32 bytes)
   */
  constructor(path: string, encryptionKey: string) {
    super(path);
    
    if (!encryptionKey || encryptionKey.length !== 64) {
      throw new Error(
        "Encryption key must be a 64-character hex string (32 bytes). " +
        "Generate with: node -e \"console.log(require('crypto').randomBytes(32).toString('hex'))\""
      );
    }
    
    this.encryptionKey = Buffer.from(encryptionKey, "hex");
  }

  /**
   * Encrypt a token before storing.
   */
  private encrypt(data: string): string {
    const iv = randomBytes(16);
    const cipher = createCipheriv(this.algorithm, this.encryptionKey, iv);
    
    let encrypted = cipher.update(data, "utf8", "hex");
    encrypted += cipher.final("hex");
    
    // Return IV + encrypted data (IV needed for decryption)
    return iv.toString("hex") + ":" + encrypted;
  }

  /**
   * Decrypt a token after retrieving.
   */
  private decrypt(encryptedData: string): string {
    const parts = encryptedData.split(":");
    if (parts.length !== 2) {
      throw new Error("Invalid encrypted data format");
    }
    
    const iv = Buffer.from(parts[0], "hex");
    const encrypted = parts[1];
    
    const decipher = createDecipheriv(this.algorithm, this.encryptionKey, iv);
    
    let decrypted = decipher.update(encrypted, "hex", "utf8");
    decrypted += decipher.final("utf8");
    
    return decrypted;
  }

  /**
   * Store an encrypted token.
   */
  async set(key: string, value: TokenSet): Promise<void> {
    const json = JSON.stringify(value);
    const encrypted = this.encrypt(json);
    
    // Store encrypted data as a special TokenSet
    const encryptedToken: TokenSet = {
      accessToken: encrypted,
      tokenType: "__encrypted__"
    };
    
    await super.set(key, encryptedToken);
  }

  /**
   * Retrieve and decrypt a token.
   */
  async get(key: string): Promise<TokenSet | null> {
    const encryptedToken = await super.get(key);
    
    if (!encryptedToken) {
      return null;
    }
    
    // Check if this is an encrypted token
    if (encryptedToken.tokenType !== "__encrypted__") {
      // Return as-is if not encrypted (backward compatibility)
      return encryptedToken;
    }
    
    try {
      const decrypted = this.decrypt(encryptedToken.accessToken);
      return JSON.parse(decrypted) as TokenSet;
    } catch (err) {
      throw new Error(
        `Failed to decrypt token for key "${key}". ` +
        `Ensure the encryption key is correct. Error: ${err instanceof Error ? err.message : String(err)}`
      );
    }
  }
}
