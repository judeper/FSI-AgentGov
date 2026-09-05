/*
 * Generate a short-lived GitHub App JWT without persisting or printing the
 * private key. The operator supplies the key through a secure local path or
 * runtime-only environment secret.
 */

import { createSign } from "node:crypto";
import { readFileSync } from "node:fs";

const APP_ID_PATTERN = /^[1-9][0-9]*$/;

function base64Url(value) {
  return Buffer.from(value)
    .toString("base64")
    .replaceAll("+", "-")
    .replaceAll("/", "_")
    .replaceAll("=", "");
}

function readArguments(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 1) {
    if (argv[index] !== "--app-id") {
      throw new Error(`unexpected argument '${argv[index] ?? ""}'`);
    }
    values.appId = argv[++index];
    if (values.appId === undefined) throw new Error("missing value for --app-id");
  }
  return values;
}

function getPrivateKey() {
  const keyPath = process.env.GITHUB_APP_PRIVATE_KEY_PATH;
  const inlineKey = process.env.GITHUB_APP_PRIVATE_KEY;
  if (keyPath && inlineKey) {
    throw new Error("provide the App private key through a path or environment secret, not both");
  }
  if (keyPath) {
    try {
      return readFileSync(keyPath, "utf8");
    } catch {
      throw new Error("could not read the App private key from the supplied secure path");
    }
  }
  if (inlineKey) return inlineKey;
  throw new Error(
    "missing App private key; set GITHUB_APP_PRIVATE_KEY_PATH or GITHUB_APP_PRIVATE_KEY at runtime",
  );
}

export function createGitHubAppJwt({
  appId,
  privateKey,
  nowSeconds = Math.floor(Date.now() / 1000),
}) {
  const normalizedAppId = String(appId ?? "");
  if (!APP_ID_PATTERN.test(normalizedAppId)) {
    throw new Error("a non-zero App ID is required");
  }
  if (typeof privateKey !== "string" || privateKey.length === 0) {
    throw new Error("an App private key is required");
  }
  const header = { alg: "RS256", typ: "JWT" };
  const payload = {
    iat: nowSeconds - 60,
    exp: nowSeconds + 540,
    iss: Number(normalizedAppId),
  };
  const unsigned = `${base64Url(JSON.stringify(header))}.${base64Url(
    JSON.stringify(payload),
  )}`;
  const signer = createSign("RSA-SHA256");
  signer.update(unsigned);
  signer.end();
  return `${unsigned}.${base64Url(signer.sign(privateKey))}`;
}

export function isCliExecution(argv = process.argv) {
  return argv[1]?.endsWith("github-app-jwt.mjs") === true;
}

if (isCliExecution()) {
  try {
    const { appId } = readArguments(process.argv.slice(2));
    const jwt = createGitHubAppJwt({
      appId,
      privateKey: getPrivateKey(),
    });
    process.stdout.write(`${jwt}\n`);
  } catch (error) {
    process.stderr.write(`github-app-jwt: ${error.message}\n`);
    process.exitCode = 1;
  }
}
