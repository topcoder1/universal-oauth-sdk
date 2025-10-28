import type { TokenSet, TokenStore } from "../types.js";
import Database from "better-sqlite3";

export class SQLiteStore implements TokenStore {
  private db: Database.Database;
  constructor(path = "tokens.db") {
    this.db = new Database(path);
    this.db.exec(`CREATE TABLE IF NOT EXISTS tokens(
      k TEXT PRIMARY KEY, v TEXT NOT NULL
    );`);
  }
  async get(key: string) {
    const row = this.db.prepare("SELECT v FROM tokens WHERE k=?").get(key) as {v?: string} | undefined;
    if (!row?.v) return null;
    return JSON.parse(row.v) as TokenSet;
  }
  async set(key: string, value: TokenSet) {
    this.db.prepare("INSERT OR REPLACE INTO tokens(k,v) VALUES(?,?)").run(key, JSON.stringify(value));
  }
  async delete(key: string) {
    this.db.prepare("DELETE FROM tokens WHERE k=?").run(key);
  }
  async list(prefix = "") {
    const rows = this.db.prepare("SELECT k FROM tokens WHERE k LIKE ?").all(`${prefix}%`) as Array<{ k: string }>;
    return rows.map((r) => r.k);
  }
  
  close() {
    this.db.close();
  }
}
