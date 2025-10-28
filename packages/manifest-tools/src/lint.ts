import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import Ajv from "ajv";
import addFormats from "ajv-formats";
import { glob } from "glob";

async function main() {
  const [manifestsDir, schemaPath] = process.argv.slice(2);
  if (!manifestsDir || !schemaPath) {
    console.error("Usage: oauth-manifest-lint <manifestsDir> <schema.json>");
    process.exit(1);
  }
  const ajv = new (Ajv as any)({ allErrors: true });
  (addFormats as any)(ajv);
  const schema = JSON.parse(readFileSync(schemaPath, "utf-8"));
  const validate = ajv.compile(schema);
  const files = await glob("*.json", { cwd: manifestsDir, absolute: true });
  let ok = true;
  for (const f of files) {
    const data = JSON.parse(readFileSync(f, "utf-8"));
    const valid = validate(data);
    if (!valid) {
      ok = false;
      console.error(`❌ ${f}`);
      console.error(validate.errors);
    } else {
      console.log(`✅ ${f}`);
    }
  }
  process.exit(ok ? 0 : 2);
}

main().catch(e => {
  console.error(e);
  process.exit(2);
});
