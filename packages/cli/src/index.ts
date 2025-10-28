#!/usr/bin/env node
import { Command } from "commander";
import inquirer from "inquirer";
import { ProviderRegistry, createClient, SQLiteStore } from "@topcoder1/oauth-sdk";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const program = new Command();
program.name("oauth").description("Universal OAuth CLI").version("0.1.0");

const __dirname = fileURLToPath(new URL(".", import.meta.url));

function loadRegistry() {
  const catalogDir = resolve(__dirname, "../../provider-catalog/manifests");
  return ProviderRegistry.loadFromDir(catalogDir);
}

program
  .command("connect")
  .argument("<provider>", "provider name (e.g., google, github)")
  .option("--client-id <id>")
  .option("--client-secret <secret>")
  .option("--redirect <uri>", "redirect URI", "http://localhost:8787/callback")
  .action(async (provider, opts) => {
    const reg = loadRegistry();
    const manifest = reg.get(provider);
    if (!manifest) {
      console.error("Unknown provider:", provider);
      process.exit(1);
    }
    const answers = await inquirer.prompt([
      { type: "input", name: "clientId", message: "Client ID:", default: opts.clientId },
      { type: "password", name: "clientSecret", message: "Client Secret (leave empty if public client):", default: opts.clientSecret, mask: "*" },
      { type: "input", name: "redirectUri", message: "Redirect URI:", default: opts.redirect }
    ]);
    const store = new SQLiteStore("tokens.db");
    const sdk = createClient({
      provider: manifest,
      clientId: answers.clientId,
      clientSecret: answers.clientSecret || undefined,
      redirectUri: answers.redirectUri,
      store
    });
    await sdk.init();
    await sdk.authorize(provider);
    console.log("✅ Authorized and stored token for:", provider);
  });

program
  .command("token")
  .argument("<provider>", "provider name")
  .action(async (provider) => {
    const store = new SQLiteStore("tokens.db");
    const t = await store.get(provider);
    if (!t) return console.log("No token found.");
    console.log(JSON.stringify({ ...t, accessToken: "***redacted***" }, null, 2));
  });

program
  .command("list")
  .description("List all stored tokens")
  .option("--prefix <prefix>", "Filter by prefix")
  .action(async (opts) => {
    const store = new SQLiteStore("tokens.db");
    try {
      const keys = await store.list(opts.prefix || "");
      
      if (keys.length === 0) {
        console.log("No tokens found.");
        return;
      }

      console.log(`\nFound ${keys.length} token(s):\n`);
      
      for (const key of keys) {
        const token = await store.get(key);
        if (token) {
          const expiresIn = token.expiresAt 
            ? Math.floor((token.expiresAt - Date.now()) / 1000)
            : null;
          
          const status = expiresIn === null 
            ? "no expiry"
            : expiresIn > 0 
              ? `expires in ${Math.floor(expiresIn / 60)}m`
              : "expired";
          
          console.log(`  • ${key} (${status})`);
        }
      }
      console.log();
    } finally {
      store.close();
    }
  });

program
  .command("info")
  .argument("<key>", "token key/provider name")
  .description("Show detailed token information")
  .action(async (key) => {
    const store = new SQLiteStore("tokens.db");
    try {
      const token = await store.get(key);
      
      if (!token) {
        console.error(`No token found for key: ${key}`);
        process.exit(1);
      }

      console.log(`\nToken Information for: ${key}\n`);
      console.log(`  Access Token: ${token.accessToken.substring(0, 20)}...`);
      console.log(`  Token Type: ${token.tokenType || "Bearer"}`);
      console.log(`  Refresh Token: ${token.refreshToken ? "Yes" : "No"}`);
      console.log(`  ID Token: ${token.idToken ? "Yes" : "No"}`);
      console.log(`  Scope: ${token.scope || "N/A"}`);
      
      if (token.expiresAt) {
        const expiresDate = new Date(token.expiresAt);
        const expiresIn = Math.floor((token.expiresAt - Date.now()) / 1000);
        console.log(`  Expires At: ${expiresDate.toLocaleString()}`);
        console.log(`  Status: ${expiresIn > 0 ? `Valid (${Math.floor(expiresIn / 60)} minutes remaining)` : "Expired"}`);
      } else {
        console.log(`  Expires At: Never`);
      }
      console.log();
    } finally {
      store.close();
    }
  });

program
  .command("refresh")
  .argument("<key>", "token key/provider name")
  .description("Manually refresh a token")
  .action(async (key) => {
    const store = new SQLiteStore("tokens.db");
    try {
      const token = await store.get(key);
      
      if (!token) {
        console.error(`No token found for key: ${key}`);
        process.exit(1);
      }

      if (!token.refreshToken) {
        console.error("Token does not have a refresh token");
        process.exit(1);
      }

      // Get provider manifest
      const reg = loadRegistry();
      const manifest = reg.get(key);
      
      if (!manifest) {
        console.error(`Unknown provider: ${key}`);
        console.error("Cannot refresh without provider configuration");
        process.exit(1);
      }

      console.log(`Refreshing token for: ${key}...`);
      
      // Create client and refresh
      const sdk = createClient({
        provider: manifest,
        clientId: "dummy", // Not needed for refresh
        redirectUri: "http://localhost:8787/callback",
        store
      });

      await sdk.init();
      
      // Note: The SDK doesn't expose refreshIfNeeded publicly
      // We'd need to add a public refresh method or make a request to trigger refresh
      console.log("⚠️  Token refresh requires making an API request to trigger auto-refresh");
      console.log("Consider using the 'connect' command to re-authorize instead");
      
    } finally {
      store.close();
    }
  });

program
  .command("revoke")
  .argument("<key>", "token key/provider name")
  .description("Revoke and delete a token")
  .option("--force", "Skip confirmation")
  .action(async (key, opts) => {
    const store = new SQLiteStore("tokens.db");
    try {
      const token = await store.get(key);
      
      if (!token) {
        console.error(`No token found for key: ${key}`);
        process.exit(1);
      }

      if (!opts.force) {
        const answers = await inquirer.prompt([
          {
            type: "confirm",
            name: "confirm",
            message: `Are you sure you want to revoke the token for "${key}"?`,
            default: false
          }
        ]);

        if (!answers.confirm) {
          console.log("Cancelled.");
          return;
        }
      }

      await store.delete(key);
      console.log(`✅ Token for "${key}" has been revoked and deleted`);
      
    } finally {
      store.close();
    }
  });

program.parseAsync();
