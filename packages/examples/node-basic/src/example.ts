import { createClient, ProviderRegistry, SQLiteStore } from "@oauth-kit/sdk";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));

async function main() {
  const reg = ProviderRegistry.loadFromDir(resolve(__dirname, "../../provider-catalog/manifests"));
  const google = reg.get("google");
  if (!google) throw new Error("google manifest not found");

  const sdk = createClient({
    provider: google,
    clientId: process.env.GOOGLE_CLIENT_ID!,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    redirectUri: "http://localhost:8787/callback",
    store: new SQLiteStore("tokens.db"),
    registry: reg
  });

  await sdk.init();
  if (!(await sdk.getToken("google"))) {
    console.log("Authorizing with Google...");
    await sdk.authorize("google");
  }

  const res = await sdk.request("https://www.googleapis.com/oauth2/v2/userinfo");
  const body = await res.json();
  console.log("Userinfo:", body);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
