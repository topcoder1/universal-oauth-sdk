import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import type { ProviderManifest } from "./types.js";

export class ProviderRegistry {
  private byName = new Map<string, ProviderManifest>();
  constructor(manifests?: ProviderManifest[]) {
    manifests?.forEach(m => this.byName.set(m.name, m));
  }
  add(m: ProviderManifest) { this.byName.set(m.name, m); }
  get(name: string): ProviderManifest | undefined { return this.byName.get(name); }

  static loadFromDir(dir: string): ProviderRegistry {
    const reg = new ProviderRegistry();
    const files = readdirSync(dir).filter((f: string) => f.endsWith(".json"));
    for (const f of files) {
      const raw = readFileSync(join(dir, f), "utf-8");
      const m = JSON.parse(raw) as ProviderManifest;
      reg.add(m);
    }
    return reg;
  }
}
