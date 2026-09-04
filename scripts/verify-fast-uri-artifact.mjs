/*
 * Fail-closed verification for the exceptional in-repository fast-uri package.
 *
 * GitHub-generated source archives are not a stable package distribution
 * boundary. This verifier binds the checked-in npm tarball to its reviewed
 * upstream commit/tree, exact packlist, lockfile SRI, safe tar structure, and
 * installed node_modules payload.
 */

import { createHash } from "node:crypto";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import {
  existsSync,
  lstatSync,
  readFileSync,
  readdirSync,
} from "node:fs";
import { createRequire } from "node:module";
import { dirname, relative, resolve, sep } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { gunzipSync } from "node:zlib";

const __dirname = dirname(fileURLToPath(import.meta.url));
const defaultRepoRoot = resolve(__dirname, "..");
const require = createRequire(import.meta.url);

export const FAST_URI_POLICY = Object.freeze({
  packageName: "fast-uri",
  version: "3.1.7",
  license: "BSD-3-Clause",
  upstreamCommit: "412e40abd4eb8beabfb952d80abf949a2baf27a3",
  upstreamTree: "a1ec2b29b5d2493a9ba4d2de480a062b08f72558",
  upstreamTrackedFileCount: 46,
  artifactFileCount: 44,
  canonicalTarMtime: 499162500,
  artifactRelativePath:
    "vendor/npm/fast-uri/3.1.7/fast-uri-3.1.7.tgz",
  provenanceRelativePath:
    "vendor/npm/fast-uri/3.1.7/provenance.json",
  packageSpec:
    "file:vendor/npm/fast-uri/3.1.7/fast-uri-3.1.7.tgz",
  overrideSpec: "$fast-uri",
  lockResolved:
    "file:vendor/npm/fast-uri/3.1.7/fast-uri-3.1.7.tgz",
  lockPackagePath: "node_modules/fast-uri",
  sha256:
    "3fa380284be4ecbf471c1dbb8c5da6f517c95f54279f88c2037985d03fdc6d92",
  sha512:
    "74ebd95738dd65dcfba6177dbfa8c26f0c6b056ddf2ba9fc45cd02b5d98ce1bba6ccc9f1cb005886ea61e89f35f51470fe4bbeacb6de9707ccba792dbb35551e",
  integrity:
    "sha512-dOvZVzjdZdz7phd9v6jCbwxrBW3fK6n8Rc0CtdmM4bumzMnxywBYhuph6J819RRw/ku+rLbelwfMunktuzVVHg==",
  artifactSize: 43760,
  artifactUnpackedSize: 218619,
  provenanceSha256:
    "bfaada6d35b9b09bdbd28b0dd0575ded1515c2f3a232ceccc17389548123eba8",
});

const LIFECYCLE_SCRIPTS = Object.freeze([
  "preinstall",
  "install",
  "postinstall",
  "prepack",
  "prepare",
  "postpack",
]);

export const FAST_URI_SECURITY_REGRESSIONS = Object.freeze([
  {
    advisory: "GHSA-jqff-g426-hqxp",
    verify(fastUri) {
      const input = "%2f%2fevil.example:/pwn";
      assert.equal(fastUri.parse(input).error, "URI scheme is malformed.");
      assert.equal(fastUri.normalize(input), input);
    },
  },
  {
    advisory: "GHSA-fph4-wmhf-6fwf",
    verify(fastUri) {
      const input =
        "http://%256c%256f%2563%2561%256c%2568%256f%2573%2574/";
      assert.equal(fastUri.normalize(input), input);
      assert.notEqual(fastUri.parse(fastUri.normalize(input)).host, "localhost");
    },
  },
  {
    advisory: "GHSA-f65p-4m7j-42xc",
    verify(fastUri) {
      const input = "http://[::not-valid]/private";
      assert.equal(fastUri.parse(input).error, "URI host is malformed.");
      assert.equal(fastUri.normalize(input), input);
    },
  },
  {
    advisory: "GHSA-5jgf-p345-68v8",
    verify(fastUri) {
      const output = fastUri.resolve(
        "http://trusted.example/base",
        "//127。0。0。1/private",
      );
      assert.equal(output, "http://127.0.0.1/private");
      assert.equal(fastUri.parse(output).host, "127.0.0.1");
    },
  },
  {
    advisory: "GHSA-qw65-cvwx-89v3",
    verify(fastUri) {
      assert.throws(
        () =>
          fastUri.serialize({
            scheme: "http",
            host: "trusted.example",
            port: "@127.0.0.1:8124",
            path: "/app",
          }),
        /URI port is malformed\./,
      );
    },
  },
  {
    advisory: "GHSA-58mr-gqgx-xq4g",
    verify(fastUri) {
      const input = "http://user@[@127.0.0.1:8123/admin";
      assert.equal(fastUri.parse(input).error, "URI host is malformed.");
      assert.equal(fastUri.equal(input, input), false);
    },
  },
]);

function sha256Hex(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function sha512Hex(bytes) {
  return createHash("sha512").update(bytes).digest("hex");
}

function sha512Integrity(bytes) {
  return `sha512-${createHash("sha512").update(bytes).digest("base64")}`;
}

function gitBlobSha1(bytes) {
  return createHash("sha1")
    .update(`blob ${bytes.length}\0`)
    .update(bytes)
    .digest("hex");
}

function nullTerminatedAscii(field) {
  const end = field.indexOf(0);
  return field.subarray(0, end === -1 ? field.length : end).toString("ascii");
}

function parseTarOctal(field, label) {
  const value = nullTerminatedAscii(field).trim();
  if (value === "") return 0;
  if (!/^[0-7]+$/.test(value)) {
    throw new Error(`tar ${label} is not canonical octal`);
  }
  return Number.parseInt(value, 8);
}

function tarHeaderChecksum(header) {
  let total = 0;
  for (let index = 0; index < header.length; index += 1) {
    total += index >= 148 && index < 156 ? 0x20 : header[index];
  }
  return total;
}

function isZeroBlock(block) {
  return block.every((byte) => byte === 0);
}

function assertSafePackagePath(path) {
  if (!path.startsWith("package/")) {
    throw new Error(`tar entry '${path}' is outside the npm package root`);
  }
  const packagePath = path.slice("package/".length);
  const segments = packagePath.split("/");
  if (
    packagePath.length === 0 ||
    packagePath.includes("\\") ||
    packagePath.startsWith("/") ||
    segments.some((segment) => segment === "" || segment === "." || segment === "..")
  ) {
    throw new Error(`tar entry '${path}' has an unsafe path`);
  }
  return packagePath;
}

export function parseNpmTarball(artifactBytes) {
  if (
    artifactBytes.length < 18 ||
    artifactBytes[0] !== 0x1f ||
    artifactBytes[1] !== 0x8b ||
    artifactBytes[2] !== 0x08
  ) {
    throw new Error("artifact is not a gzip-compressed npm tarball");
  }
  if (artifactBytes[3] !== 0 || artifactBytes.readUInt32LE(4) !== 0) {
    throw new Error("gzip header is not canonical (flags/mtime must be zero)");
  }

  const tarBytes = gunzipSync(artifactBytes);
  const entries = [];
  let offset = 0;
  let foundEnd = false;

  while (offset + 512 <= tarBytes.length) {
    const header = tarBytes.subarray(offset, offset + 512);
    if (isZeroBlock(header)) {
      foundEnd = true;
      break;
    }

    const name = nullTerminatedAscii(header.subarray(0, 100));
    const prefix = nullTerminatedAscii(header.subarray(345, 500));
    const tarPath = prefix ? `${prefix}/${name}` : name;
    const packagePath = assertSafePackagePath(tarPath);
    const mode = parseTarOctal(header.subarray(100, 108), "mode");
    const uid = parseTarOctal(header.subarray(108, 116), "uid");
    const gid = parseTarOctal(header.subarray(116, 124), "gid");
    const size = parseTarOctal(header.subarray(124, 136), "size");
    const mtime = parseTarOctal(header.subarray(136, 148), "mtime");
    const expectedChecksum = parseTarOctal(
      header.subarray(148, 156),
      "checksum",
    );
    const actualChecksum = tarHeaderChecksum(header);
    const typeFlag = header[156];
    const linkName = nullTerminatedAscii(header.subarray(157, 257));
    const userName = nullTerminatedAscii(header.subarray(265, 297));
    const groupName = nullTerminatedAscii(header.subarray(297, 329));

    if (expectedChecksum !== actualChecksum) {
      throw new Error(`tar entry '${tarPath}' has an invalid header checksum`);
    }
    if (typeFlag !== 0 && typeFlag !== 0x30) {
      throw new Error(
        `tar entry '${tarPath}' is not a regular file (type ${typeFlag})`,
      );
    }
    if (linkName) {
      throw new Error(`tar entry '${tarPath}' contains a link target`);
    }
    if ((mode & 0o111) !== 0) {
      throw new Error(`tar entry '${tarPath}' has executable mode ${mode.toString(8)}`);
    }
    if (uid !== 0 || gid !== 0 || userName || groupName) {
      throw new Error(`tar entry '${tarPath}' has non-canonical ownership metadata`);
    }
    if (mtime !== FAST_URI_POLICY.canonicalTarMtime) {
      throw new Error(`tar entry '${tarPath}' has non-canonical mtime ${mtime}`);
    }

    const contentStart = offset + 512;
    const contentEnd = contentStart + size;
    if (contentEnd > tarBytes.length) {
      throw new Error(`tar entry '${tarPath}' extends beyond the archive`);
    }

    entries.push({
      path: packagePath,
      mode,
      size,
      bytes: tarBytes.subarray(contentStart, contentEnd),
    });
    offset = contentStart + Math.ceil(size / 512) * 512;
  }

  if (!foundEnd) {
    throw new Error("tarball has no zero-block terminator");
  }
  if (!isZeroBlock(tarBytes.subarray(offset))) {
    throw new Error("tarball contains data after its zero-block terminator");
  }

  return entries;
}

function collectInstalledFiles(root) {
  const files = new Map();
  const errors = [];

  function walk(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const fullPath = resolve(directory, entry.name);
      const stat = lstatSync(fullPath);
      const packagePath = relative(root, fullPath).split(sep).join("/");

      if (stat.isSymbolicLink()) {
        errors.push(`installed fast-uri contains symlink '${packagePath}'`);
      } else if (stat.isDirectory()) {
        walk(fullPath);
      } else if (stat.isFile()) {
        if ((stat.mode & 0o111) !== 0) {
          errors.push(`installed fast-uri file '${packagePath}' is executable`);
        }
        files.set(packagePath, readFileSync(fullPath));
      } else {
        errors.push(`installed fast-uri entry '${packagePath}' is not a regular file`);
      }
    }
  }

  walk(root);
  return { files, errors };
}

function verifySecurityRegressions(installedRoot) {
  const errors = [];
  let fastUri;
  try {
    fastUri = require(resolve(installedRoot, "index.js"));
  } catch (error) {
    return [`unable to load installed fast-uri for regression checks: ${error.message}`];
  }

  for (const regression of FAST_URI_SECURITY_REGRESSIONS) {
    try {
      regression.verify(fastUri);
    } catch (error) {
      errors.push(`${regression.advisory} regression failed: ${error.message}`);
    }
  }
  return errors;
}

function parseJson(source, label, errors) {
  try {
    return JSON.parse(source);
  } catch (error) {
    errors.push(`${label} is not valid JSON: ${error.message}`);
    return null;
  }
}

function runText(executable, args) {
  return execFileSync(executable, args, {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  }).trim();
}

export function verifyFastUriSourceCheckout(sourceRoot, provenanceSrc) {
  const errors = [];
  const provenance = parseJson(provenanceSrc, "fast-uri provenance.json", errors);
  if (!provenance) return { ok: false, errors };

  let commit;
  let tree;
  let trackedOutput;
  try {
    commit = runText("git", ["-C", sourceRoot, "rev-parse", "HEAD"]);
    tree = runText("git", ["-C", sourceRoot, "rev-parse", "HEAD^{tree}"]);
    trackedOutput = execFileSync(
      "git",
      ["-C", sourceRoot, "ls-tree", "-r", "-z", "--full-tree", "HEAD"],
      { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] },
    );
  } catch (error) {
    return {
      ok: false,
      errors: [`unable to inspect upstream fast-uri checkout: ${error.message}`],
    };
  }

  if (commit !== FAST_URI_POLICY.upstreamCommit) {
    errors.push(`upstream checkout is commit ${commit}, not ${FAST_URI_POLICY.upstreamCommit}`);
  }
  if (tree !== FAST_URI_POLICY.upstreamTree) {
    errors.push(`upstream checkout is tree ${tree}, not ${FAST_URI_POLICY.upstreamTree}`);
  }

  const tracked = new Map();
  for (const record of trackedOutput.split("\0").filter(Boolean)) {
    const [metadata, path] = record.split("\t");
    const [mode, type, blob] = metadata.split(" ");
    if (type !== "blob") {
      errors.push(`upstream entry '${path}' is ${type}, not a regular blob`);
      continue;
    }
    tracked.set(path, { mode, blob });
  }
  if (tracked.size !== FAST_URI_POLICY.upstreamTrackedFileCount) {
    errors.push(
      `upstream tree contains ${tracked.size} files, not ` +
        `${FAST_URI_POLICY.upstreamTrackedFileCount}`,
    );
  }

  const reviewedPaths = new Set();
  const reviewedFiles = [
    ...(provenance.files ?? []),
    ...(provenance.upstream?.npmPackOmissions ?? []),
  ];
  for (const file of reviewedFiles) {
    reviewedPaths.add(file.path);
    const trackedEntry = tracked.get(file.path);
    if (!trackedEntry) {
      errors.push(`upstream tree is missing reviewed path '${file.path}'`);
      continue;
    }
    const sourcePath = resolve(sourceRoot, ...file.path.split("/"));
    const stat = lstatSync(sourcePath);
    if (!stat.isFile() || stat.isSymbolicLink()) {
      errors.push(`upstream path '${file.path}' is not a regular file`);
      continue;
    }
    const bytes = readFileSync(sourcePath);
    if (
      file.sha256 !== sha256Hex(bytes) ||
      file.upstreamGitBlob !== gitBlobSha1(bytes) ||
      trackedEntry.blob !== file.upstreamGitBlob
    ) {
      errors.push(`upstream path '${file.path}' differs from provenance`);
    }
  }
  for (const path of tracked.keys()) {
    if (!reviewedPaths.has(path)) {
      errors.push(`upstream tree has unreviewed path '${path}'`);
    }
  }

  try {
    if (!process.env.npm_execpath) {
      throw new Error("npm_execpath is unavailable; invoke this check through npm run");
    }
    const dryRun = JSON.parse(
      runText(process.execPath, [
        process.env.npm_execpath,
        "pack",
        sourceRoot,
        "--dry-run",
        "--ignore-scripts",
        "--json",
      ]),
    )[0];
    const dryRunFiles = [...dryRun.files]
      .sort((left, right) => left.path.localeCompare(right.path))
      .map(({ path, size, mode }) => ({
        path,
        size,
        mode: mode.toString(8).padStart(4, "0"),
      }));
    const provenanceFiles = [...(provenance.files ?? [])]
      .sort((left, right) => left.path.localeCompare(right.path))
      .map(({ path, size, mode }) => ({ path, size, mode }));
    if (JSON.stringify(dryRunFiles) !== JSON.stringify(provenanceFiles)) {
      errors.push("npm pack dry-run file list differs from provenance");
    }
  } catch (error) {
    errors.push(`unable to verify npm pack file list: ${error.message}`);
  }

  return { ok: errors.length === 0, errors };
}

export function verifyFastUriArtifact({
  packageJsonSrc,
  packageLockSrc,
  provenanceSrc,
  artifactBytes,
  installedRoot,
}) {
  const errors = [];
  const packageJson = parseJson(packageJsonSrc, "package.json", errors);
  const packageLock = parseJson(packageLockSrc, "package-lock.json", errors);
  const provenanceBytes = Buffer.from(provenanceSrc, "utf8");
  if (sha256Hex(provenanceBytes) !== FAST_URI_POLICY.provenanceSha256) {
    errors.push("fast-uri provenance.json SHA-256 does not match the reviewed manifest");
  }
  const provenance = parseJson(provenanceSrc, "fast-uri provenance.json", errors);

  if (!artifactBytes) {
    errors.push(`missing ${FAST_URI_POLICY.artifactRelativePath}`);
    return { ok: false, errors };
  }

  const actualSha256 = sha256Hex(artifactBytes);
  const actualSha512 = sha512Hex(artifactBytes);
  const actualIntegrity = sha512Integrity(artifactBytes);
  if (actualSha256 !== FAST_URI_POLICY.sha256) {
    errors.push(`fast-uri artifact SHA-256 is ${actualSha256}, not the reviewed artifact`);
  }
  if (actualSha512 !== FAST_URI_POLICY.sha512) {
    errors.push(`fast-uri artifact SHA-512 is ${actualSha512}, not the reviewed artifact`);
  }
  if (actualIntegrity !== FAST_URI_POLICY.integrity) {
    errors.push(`fast-uri artifact SRI is ${actualIntegrity}, not the reviewed artifact`);
  }

  if (packageJson) {
    const override =
      packageJson.overrides?.ajv?.[FAST_URI_POLICY.packageName];
    if (override !== FAST_URI_POLICY.overrideSpec) {
      errors.push(
        `package.json must bind Ajv's fast-uri to ${FAST_URI_POLICY.overrideSpec}`,
      );
    }
    if (
      packageJson.devDependencies?.[FAST_URI_POLICY.packageName] !==
      FAST_URI_POLICY.packageSpec
    ) {
      errors.push(
        `package.json must anchor fast-uri to ${FAST_URI_POLICY.packageSpec}`,
      );
    }
    if (packageJson.dependencies?.[FAST_URI_POLICY.packageName] !== undefined) {
      errors.push("fast-uri must not become a production dependency");
    }
  }

  const lockedRoot = packageLock?.packages?.[""];
  const lockedAjv = packageLock?.packages?.["node_modules/ajv"];
  const lockedFastUri =
    packageLock?.packages?.[FAST_URI_POLICY.lockPackagePath];
  const lockedFastUriPaths = Object.keys(packageLock?.packages ?? {}).filter(
    (path) =>
      path === `node_modules/${FAST_URI_POLICY.packageName}` ||
      path.endsWith(`/node_modules/${FAST_URI_POLICY.packageName}`),
  );
  if (lockedAjv?.dependencies?.[FAST_URI_POLICY.packageName] !== "^3.0.1") {
    errors.push("package-lock.json no longer records fast-uri as Ajv's ^3.0.1 dependency");
  }
  if (
    lockedRoot?.devDependencies?.[FAST_URI_POLICY.packageName] !==
    FAST_URI_POLICY.packageSpec
  ) {
    errors.push("package-lock.json root metadata does not pin the local fast-uri artifact");
  }
  if (
    lockedFastUriPaths.length !== 1 ||
    lockedFastUriPaths[0] !== FAST_URI_POLICY.lockPackagePath
  ) {
    errors.push("package-lock.json must contain exactly one fast-uri package entry");
  }
  if (!lockedFastUri) {
    errors.push("package-lock.json has no locked fast-uri package entry");
  } else {
    if (lockedFastUri.version !== FAST_URI_POLICY.version) {
      errors.push(
        `package-lock.json locks fast-uri ${lockedFastUri.version}, not ${FAST_URI_POLICY.version}`,
      );
    }
    if (lockedFastUri.resolved !== FAST_URI_POLICY.lockResolved) {
      errors.push("package-lock.json fast-uri source is not the reviewed repo-relative artifact");
    }
    if (lockedFastUri.integrity !== FAST_URI_POLICY.integrity) {
      errors.push("package-lock.json fast-uri integrity does not match the reviewed artifact");
    }
    if (lockedFastUri.license !== FAST_URI_POLICY.license) {
      errors.push(`package-lock.json fast-uri license is not ${FAST_URI_POLICY.license}`);
    }
  }

  const expectedManifest = new Map();
  if (provenance) {
    if (
      provenance.package?.name !== FAST_URI_POLICY.packageName ||
      provenance.package?.version !== FAST_URI_POLICY.version ||
      provenance.package?.license !== FAST_URI_POLICY.license
    ) {
      errors.push("fast-uri provenance package identity does not match policy");
    }
    if (
      provenance.upstream?.commit !== FAST_URI_POLICY.upstreamCommit ||
      provenance.upstream?.tree !== FAST_URI_POLICY.upstreamTree ||
      provenance.upstream?.trackedFileCount !==
        FAST_URI_POLICY.upstreamTrackedFileCount
    ) {
      errors.push("fast-uri provenance does not match the reviewed upstream commit/tree");
    }
    if (
      provenance.artifact?.sha256 !== FAST_URI_POLICY.sha256 ||
      provenance.artifact?.sha512 !== FAST_URI_POLICY.sha512 ||
      provenance.artifact?.integrity !== FAST_URI_POLICY.integrity ||
      provenance.artifact?.fileCount !== FAST_URI_POLICY.artifactFileCount ||
      provenance.artifact?.size !== FAST_URI_POLICY.artifactSize ||
      provenance.artifact?.unpackedSize !==
        FAST_URI_POLICY.artifactUnpackedSize ||
      provenance.artifact?.canonicalTarMtime !==
        FAST_URI_POLICY.canonicalTarMtime
    ) {
      errors.push("fast-uri provenance artifact metadata does not match policy");
    }
    const omittedPaths = provenance.upstream?.npmPackOmissions?.map(
      (entry) => entry.path,
    );
    if (
      provenance.upstream?.npmPackFileCount !==
        FAST_URI_POLICY.artifactFileCount ||
      JSON.stringify(omittedPaths) !== JSON.stringify([".gitignore", ".npmrc"])
    ) {
      errors.push("fast-uri provenance npm packlist boundary does not match policy");
    }

    if (!Array.isArray(provenance.files)) {
      errors.push("fast-uri provenance has no included-file manifest");
    } else {
      for (const file of provenance.files) {
        if (expectedManifest.has(file.path)) {
          errors.push(`fast-uri provenance repeats '${file.path}'`);
        }
        expectedManifest.set(file.path, file);
      }
    }
  }

  let entries = [];
  try {
    entries = parseNpmTarball(artifactBytes);
  } catch (error) {
    errors.push(`fast-uri artifact structure is unsafe or invalid: ${error.message}`);
  }

  const artifactFiles = new Map();
  for (const entry of entries) {
    if (artifactFiles.has(entry.path)) {
      errors.push(`fast-uri artifact repeats '${entry.path}'`);
      continue;
    }
    artifactFiles.set(entry.path, entry);
    const expected = expectedManifest.get(entry.path);
    if (!expected) {
      errors.push(`fast-uri artifact has unreviewed file '${entry.path}'`);
      continue;
    }
    if (
      expected.size !== entry.size ||
      expected.mode !== entry.mode.toString(8).padStart(4, "0") ||
      expected.sha256 !== sha256Hex(entry.bytes) ||
      expected.upstreamGitBlob !== gitBlobSha1(entry.bytes)
    ) {
      errors.push(`fast-uri artifact file '${entry.path}' does not match provenance`);
    }
  }

  for (const path of expectedManifest.keys()) {
    if (!artifactFiles.has(path)) {
      errors.push(`fast-uri artifact is missing reviewed file '${path}'`);
    }
  }
  if (
    entries.length !== FAST_URI_POLICY.artifactFileCount ||
    expectedManifest.size !== FAST_URI_POLICY.artifactFileCount
  ) {
    errors.push(
      `fast-uri artifact/manifest must contain exactly ${FAST_URI_POLICY.artifactFileCount} files`,
    );
  }

  const packagedManifest = artifactFiles.get("package.json");
  if (!packagedManifest) {
    errors.push("fast-uri artifact has no package.json");
  } else {
    const packagedJson = parseJson(
      packagedManifest.bytes.toString("utf8"),
      "packaged fast-uri package.json",
      errors,
    );
    if (packagedJson) {
      if (
        packagedJson.name !== FAST_URI_POLICY.packageName ||
        packagedJson.version !== FAST_URI_POLICY.version ||
        packagedJson.license !== FAST_URI_POLICY.license
      ) {
        errors.push("packaged fast-uri identity/license does not match policy");
      }
      const lifecycleScripts = LIFECYCLE_SCRIPTS.filter(
        (name) => packagedJson.scripts?.[name] !== undefined,
      );
      if (lifecycleScripts.length > 0) {
        errors.push(
          `packaged fast-uri contains lifecycle scripts: ${lifecycleScripts.join(", ")}`,
        );
      }
      if (packagedJson.bin !== undefined) {
        errors.push("packaged fast-uri unexpectedly exposes executable bin entries");
      }
    }
  }

  if (!installedRoot || !existsSync(installedRoot)) {
    errors.push("installed node_modules/fast-uri is missing; run npm ci before verification");
  } else {
    const errorsBeforeInstalledPayload = errors.length;
    const installed = collectInstalledFiles(installedRoot);
    errors.push(...installed.errors);
    for (const [path, entry] of artifactFiles) {
      const installedBytes = installed.files.get(path);
      if (!installedBytes) {
        errors.push(`installed fast-uri is missing '${path}'`);
      } else if (sha256Hex(installedBytes) !== sha256Hex(entry.bytes)) {
        errors.push(`installed fast-uri file '${path}' differs from the reviewed artifact`);
      }
    }
    for (const path of installed.files.keys()) {
      if (!artifactFiles.has(path)) {
        errors.push(`installed fast-uri has extra file '${path}'`);
      }
    }
    if (errorsBeforeInstalledPayload === 0 && errors.length === errorsBeforeInstalledPayload) {
      errors.push(...verifySecurityRegressions(installedRoot));
    } else {
      errors.push(
        errors.length === errorsBeforeInstalledPayload
          ? "fast-uri security regressions skipped because artifact, lockfile, or provenance checks failed before package execution"
          : "fast-uri security regressions skipped because installed payload differs from the reviewed artifact",
      );
    }
  }

  return { ok: errors.length === 0, errors };
}

export function verifyFastUriArtifactFromRepo(repoRoot = defaultRepoRoot) {
  try {
    return verifyFastUriArtifact({
      packageJsonSrc: readFileSync(resolve(repoRoot, "package.json"), "utf8"),
      packageLockSrc: readFileSync(resolve(repoRoot, "package-lock.json"), "utf8"),
      provenanceSrc: readFileSync(
        resolve(repoRoot, FAST_URI_POLICY.provenanceRelativePath),
        "utf8",
      ),
      artifactBytes: readFileSync(
        resolve(repoRoot, FAST_URI_POLICY.artifactRelativePath),
      ),
      installedRoot: resolve(
        repoRoot,
        "node_modules",
        FAST_URI_POLICY.packageName,
      ),
    });
  } catch (error) {
    return {
      ok: false,
      errors: [`unable to verify fast-uri artifact: ${error.message}`],
    };
  }
}

export function main(args = process.argv.slice(2)) {
  const result = verifyFastUriArtifactFromRepo();
  if (!result.ok) {
    for (const error of result.errors) console.error(`FAIL: ${error}`);
    console.error(
      `FAST-URI-ARTIFACT: blocked — ${result.errors.length} policy failure(s)`,
    );
    return 1;
  }

  const sourceIndex = args.indexOf("--source");
  if (sourceIndex !== -1) {
    const sourceArgument = args[sourceIndex + 1];
    if (!sourceArgument) {
      console.error("FAST-URI-ARTIFACT: --source requires a checkout path");
      return 1;
    }
    const sourceResult = verifyFastUriSourceCheckout(
      resolve(sourceArgument),
      readFileSync(
        resolve(defaultRepoRoot, FAST_URI_POLICY.provenanceRelativePath),
        "utf8",
      ),
    );
    if (!sourceResult.ok) {
      for (const error of sourceResult.errors) console.error(`FAIL: ${error}`);
      console.error(
        `FAST-URI-ARTIFACT: blocked — ${sourceResult.errors.length} upstream ` +
          "source provenance failure(s)",
      );
      return 1;
    }
  }

  console.log(
    `FAST-URI-ARTIFACT: OK — ${FAST_URI_POLICY.packageName}@${FAST_URI_POLICY.version} ` +
      `matches commit ${FAST_URI_POLICY.upstreamCommit}, the local SRI-locked artifact, ` +
      `the installed ${FAST_URI_POLICY.artifactFileCount}-file payload, and all ` +
      `${FAST_URI_SECURITY_REGRESSIONS.length} HIGH-advisory regressions` +
      (sourceIndex === -1 ? "" : "; upstream source/tree and npm packlist verified"),
  );
  return 0;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.exitCode = main();
}
