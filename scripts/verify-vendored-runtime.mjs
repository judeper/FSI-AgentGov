/*
 * Fail-closed policy for reviewed vendored dependencies.
 *
 * npm audit only sees the Node toolchain in this repository. The assessment
 * SPA also ships a vendored SheetJS bundle, so this check binds that deployed
 * asset to the reviewed official package, version, hash, SRI literal, and
 * package-lock entry. The same command also verifies the exceptional local
 * fast-uri npm tarball through verify-fast-uri-artifact.mjs. A future rotation
 * must update policy and evidence together; vulnerable or unreviewed versions
 * do not pass.
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import {
  FAST_URI_POLICY,
  verifyFastUriArtifactFromRepo,
} from "./verify-fast-uri-artifact.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..");

export const SHEETJS_POLICY = Object.freeze({
  packageName: "xlsx",
  version: "0.20.3",
  packageSpec: "https://cdn.sheetjs.com/xlsx-0.20.3/xlsx-0.20.3.tgz",
  resolved: "https://cdn.sheetjs.com/xlsx-0.20.3/xlsx-0.20.3.tgz",
  integrity:
    "sha512-oLDq3jw7AcLqKWH2AhCpVTZl8mf6X2YReP+Neh0SJUzV/BdZYjth94tG5toiMB1PPrYtxOCfaoUCkvtuH+3AJA==",
  file: "lib/xlsx.full.min.js",
  sha256: "cc015130aa8521e7f088f88898eba949ccdcbfb38df0bd129b44b7273c3a6f41",
  sri: "sha256-zAFRMKqFIefwiPiImOupSczcv7ON8L0Sm0S3Jzw6b0E=",
  source:
    "https://cdn.sheetjs.com/xlsx-0.20.3/xlsx-0.20.3.tgz (dist/xlsx.full.min.js)",
});

function parseMarkdownCells(line) {
  return line
    .split("|")
    .slice(1, -1)
    .map((cell) => cell.trim().replace(/^`|`$/g, ""));
}

export function parseSheetJsManifest(manifestSrc) {
  const line = manifestSrc
    .split(/\r?\n/)
    .find((candidate) => /^\|\s*SheetJS\s*\|/.test(candidate));
  return line ? parseMarkdownCells(line) : null;
}

function sha256Hex(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function sriSha256(bytes) {
  return `sha256-${createHash("sha256").update(bytes).digest("base64")}`;
}

function findSheetJsIntegrity(appSrc) {
  const fileIndex = appSrc.indexOf("xlsx.full.min.js");
  if (fileIndex === -1) return null;
  const nearby = appSrc.slice(Math.max(0, fileIndex - 1200), fileIndex + 1200);
  return nearby.match(/\.integrity\s*=\s*"([^"]+)"/)?.[1] ?? null;
}

export function verifyVendoredRuntime({
  manifestSrc,
  packageJsonSrc,
  packageLockSrc,
  appSrc,
  vendorBytes,
}) {
  const errors = [];
  const manifest = parseSheetJsManifest(manifestSrc);

  if (!manifest || manifest.length < 6) {
    errors.push("VENDOR-MANIFEST.md has no complete SheetJS inventory row");
  } else {
    const [name, version, file, sha256, sri, source] = manifest;
    if (name !== "SheetJS") errors.push(`manifest library is '${name}', not SheetJS`);
    if (version !== SHEETJS_POLICY.version) {
      errors.push(
        `SheetJS ${version} is not approved; the shipped runtime must use ` +
          `${SHEETJS_POLICY.version} (known vulnerable 0.18.x versions are prohibited)`,
      );
    }
    if (file !== SHEETJS_POLICY.file) {
      errors.push(`manifest file '${file}' does not match '${SHEETJS_POLICY.file}'`);
    }
    if (sha256.toLowerCase() !== SHEETJS_POLICY.sha256) {
      errors.push(`manifest SHA-256 '${sha256}' does not match the approved artifact`);
    }
    if (sri !== SHEETJS_POLICY.sri) {
      errors.push(`manifest SRI '${sri}' does not match the approved artifact`);
    }
    if (source !== SHEETJS_POLICY.source) {
      errors.push(`manifest source '${source}' is not the approved official artifact`);
    }
  }

  let packageJson;
  let packageLock;
  try {
    packageJson = JSON.parse(packageJsonSrc);
  } catch (error) {
    errors.push(`package.json is not valid JSON: ${error.message}`);
  }
  try {
    packageLock = JSON.parse(packageLockSrc);
  } catch (error) {
    errors.push(`package-lock.json is not valid JSON: ${error.message}`);
  }

  if (packageJson) {
    const devSpec = packageJson.devDependencies?.[SHEETJS_POLICY.packageName];
    const prodSpec = packageJson.dependencies?.[SHEETJS_POLICY.packageName];
    if (devSpec !== SHEETJS_POLICY.packageSpec) {
      errors.push(
        `package.json devDependency xlsx must remain pinned to ${SHEETJS_POLICY.packageSpec}`,
      );
    }
    if (prodSpec !== undefined) {
      errors.push("SheetJS must remain a vendored build-time dependency, not a runtime npm dependency");
    }
  }

  const locked = packageLock?.packages?.[`node_modules/${SHEETJS_POLICY.packageName}`];
  if (!locked) {
    errors.push("package-lock.json has no locked xlsx package entry");
  } else {
    if (locked.version !== SHEETJS_POLICY.version) {
      errors.push(`package-lock.json locks xlsx ${locked.version}, not ${SHEETJS_POLICY.version}`);
    }
    if (locked.resolved !== SHEETJS_POLICY.resolved) {
      errors.push("package-lock.json xlsx source is not the approved official CDN tarball");
    }
    if (locked.integrity !== SHEETJS_POLICY.integrity) {
      errors.push("package-lock.json xlsx integrity does not match the approved official tarball");
    }
  }

  if (!vendorBytes) {
    errors.push(`missing shipped vendor file ${SHEETJS_POLICY.file}`);
  } else {
    const actualSha256 = sha256Hex(vendorBytes);
    const actualSri = sriSha256(vendorBytes);
    if (actualSha256 !== SHEETJS_POLICY.sha256) {
      errors.push(`shipped ${SHEETJS_POLICY.file} SHA-256 is ${actualSha256}, not the approved artifact`);
    }
    if (actualSri !== SHEETJS_POLICY.sri) {
      errors.push(`shipped ${SHEETJS_POLICY.file} SRI is ${actualSri}, not the approved artifact`);
    }
  }

  const appIntegrity = findSheetJsIntegrity(appSrc);
  if (appIntegrity !== SHEETJS_POLICY.sri) {
    errors.push(
      `assessment-app.js SheetJS integrity is '${appIntegrity ?? "(missing)"}', not the approved SRI`,
    );
  }

  return { ok: errors.length === 0, errors };
}

function readRepoInputs() {
  const vendorPath = resolve(repoRoot, "docs/javascripts", SHEETJS_POLICY.file);
  return {
    manifestSrc: readFileSync(resolve(repoRoot, "docs/javascripts/lib/VENDOR-MANIFEST.md"), "utf8"),
    packageJsonSrc: readFileSync(resolve(repoRoot, "package.json"), "utf8"),
    packageLockSrc: readFileSync(resolve(repoRoot, "package-lock.json"), "utf8"),
    appSrc: readFileSync(resolve(repoRoot, "docs/javascripts/assessment-app.js"), "utf8"),
    vendorBytes: readFileSync(vendorPath),
  };
}

export function main() {
  let result;
  try {
    result = verifyVendoredRuntime(readRepoInputs());
  } catch (error) {
    console.error(`VENDOR-RUNTIME: unable to verify shipped runtime: ${error.message}`);
    return 1;
  }

  if (!result.ok) {
    for (const error of result.errors) console.error(`FAIL: ${error}`);
    console.error(
      `VENDOR-RUNTIME: blocked — ${result.errors.length} policy failure(s); ` +
        "the deployed SheetJS runtime is not approved",
    );
    return 1;
  }

  const fastUriResult = verifyFastUriArtifactFromRepo(repoRoot);
  if (!fastUriResult.ok) {
    for (const error of fastUriResult.errors) console.error(`FAIL: ${error}`);
    console.error(
      `VENDOR-RUNTIME: blocked — ${fastUriResult.errors.length} fast-uri ` +
        "artifact policy failure(s)",
    );
    return 1;
  }

  console.log(
    `VENDOR-RUNTIME: OK — SheetJS ${SHEETJS_POLICY.version} ` +
      `matches the locked official artifact and shipped SRI; ` +
      `${FAST_URI_POLICY.packageName}@${FAST_URI_POLICY.version} matches the ` +
      "reviewed local artifact, lockfile, and installed payload",
  );
  return 0;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.exitCode = main();
}
