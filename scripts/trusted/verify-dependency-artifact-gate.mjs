/*
 * Authoritative, base-controlled dependency-artifact gate.
 *
 * TRUST MODEL
 * -----------
 * Every byte executed by this file comes from the protected default branch. It
 * is dispatched by `.github/workflows/trusted-dependency-artifact.yml`, a
 * `pull_request_target` workflow that never checks out, merges, or executes the
 * candidate pull request. The candidate tree is retrieved through the GitHub
 * REST API as *data* and is only ever parsed — never imported, evaluated,
 * installed, spawned, or written to a candidate-controlled path.
 *
 * What makes this different from the pull-request-controlled `sri-check`
 * workflow, which can only ever attest to itself:
 *
 *   - Expected pins live in `.github/trusted-policy/dependency-artifact-policy.json`
 *     on the default branch. A candidate cannot move them: a pull request that
 *     edits a trusted path *and* a guarded dependency path fails closed.
 *   - The candidate's verifier, its hard-coded hashes, its workflows and its
 *     tests are never consulted for the pass/fail decision. Coherent malicious
 *     edits across all of them cannot influence this result.
 *   - No npm, package script, lifecycle hook, `.npmrc`, `node_modules/.bin`
 *     entry, or candidate JavaScript is executed. The job has no `node_modules`.
 *
 * Whether the reviewed artifact is *required* is derived from the base checkout,
 * not from policy text and never from the candidate. That keeps the gate honest
 * before the artifact lands (it cannot demand bytes that do not exist yet) and
 * after it lands (a candidate cannot escape validation by deleting it).
 *
 * Node built-ins only. Pure functions are exported so the attack fixtures in
 * `tests/spa/trusted-dependency-gate.test.mjs` can drive the whole decision
 * offline, with no network and no checkout.
 */

import { createHash } from "node:crypto";
import { appendFileSync, existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { gunzipSync } from "node:zlib";

const __dirname = dirname(fileURLToPath(import.meta.url));
const defaultRepoRoot = resolve(__dirname, "..", "..");

export const POLICY_RELATIVE_PATH =
  ".github/trusted-policy/dependency-artifact-policy.json";

const FULL_OBJECT_ID = /^[0-9a-f]{40}$/;
const UNSAFE_MESSAGE_CHARACTER = /[^A-Za-z0-9 ._/@:+()',=-]/g;
const OWNER_NAME = /^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,98}[A-Za-z0-9_-])?$/;

const BLOB_MODE_REGULAR = "100644";
const BLOB_MODE_EXECUTABLE = "100755";
const BLOB_MODE_SYMLINK = "120000";
const BLOB_MODE_GITLINK = "160000";

/* ------------------------------------------------------------------ *
 * Policy loading
 * ------------------------------------------------------------------ */

export function loadPolicy(repoRoot = defaultRepoRoot) {
  const policy = JSON.parse(
    readFileSync(join(repoRoot, ...POLICY_RELATIVE_PATH.split("/")), "utf8"),
  );
  assertPolicyShape(policy);
  return policy;
}

export function assertPolicyShape(policy) {
  for (const key of [
    "policyVersion",
    "checkName",
    "defaultBranch",
    "limits",
    "trustedPaths",
    "guardedPaths",
    "digestPins",
    "vendor",
    "package",
    "verifierPolicyLiterals",
    "documentScan",
    "rootScripts",
    "forbiddenTree",
    "gitattributes",
  ]) {
    if (!(key in policy)) throw new Error(`trusted policy is missing '${key}'`);
  }
  for (const [path, pin] of Object.entries(policy.digestPins)) {
    if (!/^[0-9a-f]{64}$/.test(pin.sha256)) {
      throw new Error(`trusted policy digest for '${path}' is not a SHA-256`);
    }
    if (!Number.isSafeInteger(pin.size) || pin.size <= 0) {
      throw new Error(`trusted policy size for '${path}' is not a positive integer`);
    }
  }
  if (!policy.vendor.allowedFiles.includes(policy.package.artifactPath)) {
    throw new Error("trusted policy artifactPath is not in the vendor allowlist");
  }
  return policy;
}

/*
 * The base checkout decides whether the reviewed artifact must exist. Nothing
 * the candidate controls participates in this answer.
 */
export function artifactRequiredByBase(policy, repoRoot = defaultRepoRoot) {
  return existsSync(join(repoRoot, ...policy.package.artifactPath.split("/")));
}

/* ------------------------------------------------------------------ *
 * Pure helpers
 * ------------------------------------------------------------------ */

export function sha256Hex(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

export function sha512Hex(bytes) {
  return createHash("sha512").update(bytes).digest("hex");
}

export function gitBlobId(bytes) {
  const buffer = Buffer.from(bytes);
  return createHash("sha1")
    .update(Buffer.concat([Buffer.from(`blob ${buffer.length}\u0000`, "utf8"), buffer]))
    .digest("hex");
}

/*
 * Candidate text reaches a check-run summary, so it is reduced to a bounded
 * token drawn from a conservative allowlist. Markdown and HTML metacharacters
 * (backtick, #, <, >, *, _, ~, [, ], |, !) are all outside the allowlist, so a
 * candidate cannot inject headings, links, images or code spans into the
 * rendered summary.
 */
export function sanitizeToken(value, maxLength = 120) {
  return String(value ?? "")
    .replace(/\s+/g, " ")
    .replace(UNSAFE_MESSAGE_CHARACTER, "?")
    .slice(0, maxLength);
}

export class Verdict {
  constructor(limits) {
    this.limits = limits;
    this.messages = [];
    this.failed = false;
    this.mode = "unknown";
  }

  note(message) {
    if (this.messages.length >= this.limits.maxMessages) return this;
    this.messages.push(sanitizeToken(message, this.limits.maxMessageLength));
    return this;
  }

  fail(message) {
    this.failed = true;
    return this.note(message);
  }

  toJSON() {
    return {
      conclusion: this.failed ? "failure" : "success",
      mode: sanitizeToken(this.mode, 64),
      messages: this.messages,
    };
  }
}

/* ------------------------------------------------------------------ *
 * Path classification
 * ------------------------------------------------------------------ */

export function isUnsafeRepositoryPath(path) {
  if (typeof path !== "string" || path.length === 0 || path.length > 400) return true;
  if (path.startsWith("/") || /^[A-Za-z]:/.test(path)) return true;
  if (path.includes("\\")) return true;
  if (/[\u0000-\u001f\u007f]/.test(path)) return true;
  const segments = path.split("/");
  if (segments.length > 32) return true;
  return segments.some((segment) => segment === "" || segment === "." || segment === "..");
}

export function classifyChangedPaths(policy, changedPaths) {
  const trusted = [];
  const guarded = [];
  const unsafe = [];
  const { exact, prefixes, suffixes } = policy.guardedPaths;
  const trustedSet = new Set(policy.trustedPaths);

  for (const path of changedPaths) {
    if (isUnsafeRepositoryPath(path)) {
      unsafe.push(path);
      continue;
    }
    if (trustedSet.has(path)) trusted.push(path);
    if (
      exact.includes(path) ||
      prefixes.some((prefix) => path.startsWith(prefix)) ||
      suffixes.some((suffix) => path.endsWith(suffix))
    ) {
      guarded.push(path);
    }
  }
  return { trusted, guarded, unsafe };
}

/* ------------------------------------------------------------------ *
 * Documentation scanner — the base-controlled half of HIGH findings 1 and 2.
 *
 * A reviewer instruction that runs `npm ci`, `npm run …`, `npm test`, or a
 * `node_modules/.bin` shim before trust is established re-opens candidate
 * controlled lifecycle hooks, `.npmrc` injection, and bin shadowing. The
 * candidate cannot suppress this scan, because it runs from base policy.
 * ------------------------------------------------------------------ */

export function extractFencedCodeBlocks(markdown) {
  const blocks = [];
  const lines = markdown.split(/\r?\n/);
  let fence = null;
  let current = [];
  for (let index = 0; index < lines.length; index += 1) {
    const match = lines[index].match(/^\s{0,3}(`{3,}|~{3,})(.*)$/);
    if (match) {
      if (fence === null) {
        fence = match[1];
        current = [];
        continue;
      }
      if (match[1][0] === fence[0] && match[1].length >= fence.length) {
        blocks.push(current);
        fence = null;
        current = [];
        continue;
      }
    }
    if (fence !== null) current.push({ number: index + 1, text: lines[index] });
  }
  return blocks;
}

/* Resolve the program a shell would execute for one command segment. */
export function commandProgram(commandLine) {
  let text = String(commandLine).trim();
  if (text === "" || text.startsWith("#")) return null;
  text = text.replace(/^(?:PS[^>]*>|>>>|\$|>)\s+/, "");
  let previous = null;
  while (previous !== text) {
    previous = text;
    text = text.replace(/^[A-Za-z_][A-Za-z0-9_]*=(?:"[^"]*"|'[^']*'|[^\s]*)\s+/, "");
  }
  const token = text.split(/\s+/)[0] ?? "";
  return token === "" ? null : token.replace(/^['"]+|['"]+$/g, "");
}

export function scanDocumentForForbiddenCommands(policy, markdown, label) {
  const errors = [];
  const { forbiddenPrograms, forbiddenFragments, negationMarkers } = policy.documentScan;
  const programs = new Set(forbiddenPrograms);
  const isForbidden = (token) =>
    token !== null &&
    (programs.has(token) || forbiddenFragments.some((fragment) => token.includes(fragment)));

  for (const block of extractFencedCodeBlocks(markdown)) {
    for (const { number, text } of block) {
      for (const segment of text.split(/&&|\|\||[;|]/)) {
        const program = commandProgram(segment);
        if (isForbidden(program)) {
          errors.push(`${label}:${number} runs '${program}' before trust is established`);
        }
      }
    }
  }

  /* Inline code spans are instructions too, unless the sentence disclaims them. */
  const lines = markdown.split(/\r?\n/);
  let insideFence = false;
  for (let index = 0; index < lines.length; index += 1) {
    if (/^\s{0,3}(`{3,}|~{3,})/.test(lines[index])) {
      insideFence = !insideFence;
      continue;
    }
    if (insideFence) continue;
    const lower = lines[index].toLowerCase();
    if (negationMarkers.some((marker) => lower.includes(marker))) continue;
    for (const span of lines[index].match(/`[^`]+`/g) ?? []) {
      const program = commandProgram(span.slice(1, -1));
      if (isForbidden(program)) {
        errors.push(`${label}:${index + 1} shows '${program}' without a do-not marker`);
      }
    }
  }
  return errors;
}

/* ------------------------------------------------------------------ *
 * Candidate tar parsing — data only, hard-bounded, fail closed
 * ------------------------------------------------------------------ */

function nullTerminatedAscii(field) {
  const end = field.indexOf(0);
  return field.subarray(0, end === -1 ? field.length : end).toString("ascii");
}

function tarOctal(field, label) {
  const value = nullTerminatedAscii(field).trim();
  if (value === "") return 0;
  if (!/^[0-7]+$/.test(value)) throw new Error(`tar ${label} is not canonical octal`);
  return Number.parseInt(value, 8);
}

function tarChecksum(header) {
  let total = 0;
  for (let index = 0; index < header.length; index += 1) {
    total += index >= 148 && index < 156 ? 0x20 : header[index];
  }
  return total;
}

function isZeroBlock(block) {
  return block.every((byte) => byte === 0);
}

export function parseCandidateTarball(artifactBytes, policy) {
  const { limits } = policy;
  const expected = policy.package.tar;
  const bytes = Buffer.from(artifactBytes ?? []);
  const label = (path) => sanitizeToken(path, 80);

  if (bytes.length !== expected.size) {
    throw new Error(`artifact is ${bytes.length} bytes, expected ${expected.size}`);
  }
  if (bytes.length < 18 || bytes[0] !== 0x1f || bytes[1] !== 0x8b || bytes[2] !== 0x08) {
    throw new Error("artifact is not a gzip-compressed npm tarball");
  }
  if (bytes[3] !== 0 || bytes.readUInt32LE(4) !== 0) {
    throw new Error("gzip header is not canonical (flags and mtime must be zero)");
  }

  const tarBytes = gunzipSync(bytes, { maxOutputLength: limits.maxUnpackedBytes });
  const entries = [];
  let offset = 0;
  let terminated = false;
  let unpacked = 0;

  while (offset + 512 <= tarBytes.length) {
    const header = tarBytes.subarray(offset, offset + 512);
    if (isZeroBlock(header)) {
      terminated = true;
      break;
    }
    if (entries.length >= limits.maxTarEntries) {
      throw new Error(`tarball exceeds ${limits.maxTarEntries} entries`);
    }

    const name = nullTerminatedAscii(header.subarray(0, 100));
    const prefix = nullTerminatedAscii(header.subarray(345, 500));
    const tarPath = prefix ? `${prefix}/${name}` : name;

    if (tarOctal(header.subarray(148, 156), "checksum") !== tarChecksum(header)) {
      throw new Error(`tar entry '${label(tarPath)}' has an invalid header checksum`);
    }
    const typeFlag = header[156];
    if (typeFlag !== 0 && typeFlag !== 0x30) {
      throw new Error(`tar entry '${label(tarPath)}' is not a regular file (type ${typeFlag})`);
    }
    if (nullTerminatedAscii(header.subarray(157, 257))) {
      throw new Error(`tar entry '${label(tarPath)}' contains a link target`);
    }
    if (!tarPath.startsWith(expected.prefix)) {
      throw new Error(`tar entry '${label(tarPath)}' escapes the package root`);
    }
    const packagePath = tarPath.slice(expected.prefix.length);
    if (isUnsafeRepositoryPath(packagePath)) {
      throw new Error(`tar entry '${label(tarPath)}' has an unsafe path`);
    }

    const mode = tarOctal(header.subarray(100, 108), "mode");
    const uid = tarOctal(header.subarray(108, 116), "uid");
    const gid = tarOctal(header.subarray(116, 124), "gid");
    const size = tarOctal(header.subarray(124, 136), "size");
    const mtime = tarOctal(header.subarray(136, 148), "mtime");

    if ((mode & 0o111) !== 0) {
      throw new Error(`tar entry '${label(tarPath)}' has executable mode`);
    }
    if (
      uid !== 0 ||
      gid !== 0 ||
      nullTerminatedAscii(header.subarray(265, 297)) ||
      nullTerminatedAscii(header.subarray(297, 329))
    ) {
      throw new Error(`tar entry '${label(tarPath)}' has non-canonical ownership`);
    }
    if (mtime !== expected.mtime) {
      throw new Error(`tar entry '${label(tarPath)}' has non-canonical mtime`);
    }
    if (size > limits.maxTarEntryBytes) {
      throw new Error(`tar entry '${label(tarPath)}' exceeds the entry size limit`);
    }
    unpacked += size;
    if (unpacked > limits.maxUnpackedBytes) {
      throw new Error("tarball exceeds the unpacked size limit");
    }

    const start = offset + 512;
    const end = start + size;
    if (end > tarBytes.length) {
      throw new Error(`tar entry '${label(tarPath)}' extends beyond the archive`);
    }
    entries.push({ path: packagePath, mode, size, bytes: tarBytes.subarray(start, end) });
    offset = start + Math.ceil(size / 512) * 512;
  }

  if (!terminated) throw new Error("tarball has no zero-block terminator");
  if (!isZeroBlock(tarBytes.subarray(offset))) {
    throw new Error("tarball contains data after its zero-block terminator");
  }
  return entries;
}

/* ------------------------------------------------------------------ *
 * Literal extraction from the candidate verifier — parsing, never evaluation
 * ------------------------------------------------------------------ */

export function extractPolicyLiterals(source, objectName) {
  const anchor = source.indexOf(`${objectName} = Object.freeze({`);
  if (anchor === -1) throw new Error(`candidate verifier does not declare ${objectName}`);
  const start = source.indexOf("{", anchor);
  let depth = 0;
  let end = -1;
  for (let index = start; index < source.length; index += 1) {
    if (source[index] === "{") depth += 1;
    else if (source[index] === "}") {
      depth -= 1;
      if (depth === 0) {
        end = index;
        break;
      }
    }
  }
  if (end === -1) throw new Error(`${objectName} literal is unterminated`);

  const literals = new Map();
  const pattern =
    /(?:^|[,{])\s*([A-Za-z_$][A-Za-z0-9_$]*)\s*:\s*(?:"((?:[^"\\]|\\.)*)"|(-?\d+))/g;
  const body = source.slice(start + 1, end);
  let match;
  while ((match = pattern.exec(body)) !== null) {
    const [, key, stringValue, numberValue] = match;
    if (literals.has(key)) continue;
    literals.set(
      key,
      stringValue === undefined ? Number(numberValue) : stringValue.replace(/\\(.)/g, "$1"),
    );
  }
  return literals;
}

export function extractAdvisoryIds(source) {
  return [...source.matchAll(/advisory:\s*"(GHSA-[a-z0-9-]{4,64})"/g)].map((match) => match[1]);
}

/* ------------------------------------------------------------------ *
 * Candidate manifest checks
 * ------------------------------------------------------------------ */

function parseCandidateJson(bytes, label, policy) {
  if (!bytes) throw new Error(`${label} is missing`);
  if (bytes.length > policy.limits.maxJsonBytes) {
    throw new Error(`${label} exceeds the JSON size limit`);
  }
  const text = Buffer.from(bytes).toString("utf8");
  if (text.includes("\u0000")) throw new Error(`${label} contains NUL bytes`);
  return JSON.parse(text);
}

export function checkRootScripts(verdict, policy, packageJson, label) {
  const scripts = packageJson.scripts ?? {};
  const names = Object.keys(scripts);
  const forbidden = new Set(policy.rootScripts.forbiddenNames);
  for (const name of names) {
    if (forbidden.has(name)) {
      verdict.fail(`${label} declares lifecycle script '${sanitizeToken(name, 40)}'`);
      continue;
    }
    for (const prefix of policy.rootScripts.forbiddenPrefixes) {
      if (!name.startsWith(prefix)) continue;
      const target = name.slice(prefix.length);
      if (target && names.includes(target)) {
        verdict.fail(
          `${label} declares hook script '${sanitizeToken(name, 40)}' wrapping '${sanitizeToken(target, 40)}'`,
        );
      }
    }
  }
}

export function checkLockBinShadowing(verdict, policy, lock) {
  for (const [path, node] of Object.entries(lock.packages ?? {})) {
    const bin = node?.bin;
    if (!bin || typeof bin !== "object") continue;
    for (const binName of Object.keys(bin)) {
      if (policy.forbiddenTree.shadowableBins.includes(binName)) {
        verdict.fail(
          `package-lock.json exposes a ${sanitizeToken(binName, 8)}-shadowing bin at '${sanitizeToken(path, 80)}'`,
        );
      }
    }
  }
}

function checkArtifactPackageJson(verdict, policy, packageJson) {
  const dev = packageJson.devDependencies ?? {};
  const prod = packageJson.dependencies ?? {};
  if (dev[policy.package.name] !== policy.package.spec) {
    verdict.fail(
      `package.json devDependencies.${policy.package.name} is '${sanitizeToken(dev[policy.package.name], 60)}', expected the pinned local spec`,
    );
  }
  if (policy.package.name in prod) {
    verdict.fail(`package.json promotes ${policy.package.name} to a production dependency`);
  }
  const override = packageJson.overrides?.[policy.package.overrideParent]?.[policy.package.name];
  if (override !== policy.package.overrideSpec) {
    verdict.fail(
      `package.json override ${policy.package.overrideParent}.${policy.package.name} is '${sanitizeToken(override, 40)}', expected '${policy.package.overrideSpec}'`,
    );
  }
}

function checkArtifactPackageLock(verdict, policy, lock) {
  const packages = lock.packages ?? {};
  const entry = packages[policy.package.lockPath];
  if (!entry) {
    verdict.fail(`package-lock.json has no '${policy.package.lockPath}' entry`);
    return;
  }
  if (entry.version !== policy.package.version) {
    verdict.fail(
      `locked ${policy.package.name} version is '${sanitizeToken(entry.version, 40)}', expected ${policy.package.version}`,
    );
  }
  if (entry.resolved !== policy.package.spec) {
    verdict.fail(
      `locked ${policy.package.name} resolved is '${sanitizeToken(entry.resolved, 80)}', expected the pinned local spec`,
    );
  }
  if (entry.integrity !== policy.package.integrity) {
    verdict.fail(`locked ${policy.package.name} integrity does not match the pinned SRI`);
  }
  if (entry.dev !== true) {
    verdict.fail(`locked ${policy.package.name} is not marked development-only`);
  }

  const copies = Object.keys(packages).filter(
    (path) => path === policy.package.lockPath || path.endsWith(`/${policy.package.lockPath}`),
  );
  if (copies.length !== 1) {
    verdict.fail(
      `package-lock.json contains ${copies.length} ${policy.package.name} copies, expected 1`,
    );
  }

  for (const path of Object.keys(packages)) {
    if (
      path !== `node_modules/${policy.package.overrideParent}` &&
      !path.endsWith(`/node_modules/${policy.package.overrideParent}`)
    ) {
      continue;
    }
    const range = packages[path]?.dependencies?.[policy.package.name];
    if (range !== undefined && range !== policy.package.dependentRange) {
      verdict.fail(
        `${policy.package.overrideParent} declares ${policy.package.name} '${sanitizeToken(range, 30)}', expected '${policy.package.dependentRange}'`,
      );
    }
  }
}

function checkProvenance(verdict, policy, provenance, tarEntries) {
  const files = provenance?.files;
  if (!Array.isArray(files)) {
    verdict.fail("provenance.json has no file manifest array");
    return;
  }
  if (files.length !== policy.package.tar.fileCount) {
    verdict.fail(
      `provenance.json lists ${files.length} files, expected ${policy.package.tar.fileCount}`,
    );
    return;
  }
  const byPath = new Map();
  for (const file of files) {
    if (!file || typeof file.path !== "string" || typeof file.sha256 !== "string") {
      verdict.fail("provenance.json contains a malformed file record");
      return;
    }
    if (isUnsafeRepositoryPath(file.path)) {
      verdict.fail(`provenance.json lists an unsafe path '${sanitizeToken(file.path, 80)}'`);
      return;
    }
    if (typeof file.mode === "number" && (file.mode & 0o111) !== 0) {
      verdict.fail(`provenance.json lists an executable entry '${sanitizeToken(file.path, 80)}'`);
      return;
    }
    byPath.set(file.path, file);
  }
  for (const entry of tarEntries) {
    const record = byPath.get(entry.path);
    if (!record) {
      verdict.fail(`tar entry '${sanitizeToken(entry.path, 80)}' is absent from provenance.json`);
      return;
    }
    if (record.sha256 !== sha256Hex(entry.bytes)) {
      verdict.fail(
        `tar entry '${sanitizeToken(entry.path, 80)}' does not match its provenance digest`,
      );
      return;
    }
    if (typeof record.size === "number" && record.size !== entry.size) {
      verdict.fail(
        `tar entry '${sanitizeToken(entry.path, 80)}' size disagrees with provenance.json`,
      );
      return;
    }
  }
}

function checkPackedManifest(verdict, policy, tarEntries) {
  const manifest = tarEntries.find((entry) => entry.path === "package.json");
  if (!manifest) {
    verdict.fail("packed artifact has no package.json");
    return;
  }
  let parsed;
  try {
    parsed = JSON.parse(Buffer.from(manifest.bytes).toString("utf8"));
  } catch {
    verdict.fail("packed package.json is not valid JSON");
    return;
  }
  if (parsed.name !== policy.package.name || parsed.version !== policy.package.version) {
    verdict.fail(
      `packed identity is '${sanitizeToken(parsed.name, 40)}@${sanitizeToken(parsed.version, 20)}', expected ${policy.package.name}@${policy.package.version}`,
    );
  }
  if (parsed.license !== policy.package.license) {
    verdict.fail(`packed license is '${sanitizeToken(parsed.license, 40)}'`);
  }
  for (const name of Object.keys(parsed.scripts ?? {})) {
    if (policy.rootScripts.forbiddenNames.includes(name)) {
      verdict.fail(`packed artifact declares lifecycle script '${sanitizeToken(name, 40)}'`);
    }
  }
  if (parsed.bin) verdict.fail("packed artifact declares bin entries");
}

export function checkGitattributes(verdict, policy, text) {
  for (const line of policy.gitattributes.requiredLines) {
    if (!text.includes(line)) {
      verdict.fail(`.gitattributes is missing required line '${sanitizeToken(line, 60)}'`);
    }
  }
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (line === "" || line.startsWith("#")) continue;
    const [pattern, ...attributes] = line.split(/\s+/);
    if (
      !policy.gitattributes.attributeGuardedPathPrefixes.some((prefix) =>
        pattern.startsWith(prefix),
      )
    ) {
      continue;
    }
    for (const attribute of attributes) {
      if (
        policy.gitattributes.forbiddenAttributePrefixes.some((prefix) =>
          attribute.startsWith(prefix),
        )
      ) {
        verdict.fail(
          `.gitattributes applies '${sanitizeToken(attribute, 40)}' to guarded pattern '${sanitizeToken(pattern, 60)}'`,
        );
      }
    }
  }
}

/* ------------------------------------------------------------------ *
 * The authoritative evaluation
 * ------------------------------------------------------------------ */

export async function evaluateCandidate({
  policy,
  baseRef,
  defaultBranch,
  eventHeadSha,
  currentHeadSha,
  changedPaths,
  changedPathsTruncated = false,
  treeEntries = [],
  treeTruncated = false,
  artifactRequired = false,
  readBlob,
}) {
  const verdict = new Verdict(policy.limits);

  if (!FULL_OBJECT_ID.test(String(eventHeadSha ?? ""))) {
    verdict.mode = "invalid-event";
    return verdict.fail("pull request head SHA is not a full object id");
  }
  if (baseRef !== defaultBranch) {
    verdict.mode = "invalid-base";
    return verdict.fail(
      `pull request targets '${sanitizeToken(baseRef, 60)}', but the gate only authorizes '${sanitizeToken(defaultBranch, 60)}'`,
    );
  }
  if (changedPathsTruncated) {
    verdict.mode = "unbounded-change";
    return verdict.fail("changed-file listing was truncated; refusing to judge a partial view");
  }
  if (changedPaths.length > policy.limits.maxChangedFiles) {
    verdict.mode = "unbounded-change";
    return verdict.fail(
      `pull request changes ${changedPaths.length} files, above the reviewable limit`,
    );
  }

  const { trusted, guarded, unsafe } = classifyChangedPaths(policy, changedPaths);
  if (unsafe.length > 0) {
    verdict.mode = "unsafe-path";
    return verdict.fail(`pull request contains an unsafe path '${sanitizeToken(unsafe[0], 100)}'`);
  }
  if (trusted.length > 0 && guarded.length > 0) {
    verdict.mode = "mixed-trusted-and-guarded";
    return verdict.fail(
      "trusted policy paths and guarded dependency paths must not change in the same pull request",
    );
  }
  if (trusted.length > 0) {
    verdict.mode = "policy-only";
    return verdict.note(
      "policy-only change; CODEOWNERS review governs it and no artifact was validated",
    );
  }
  if (guarded.length === 0) {
    verdict.mode = "not-applicable";
    return verdict.note("no guarded dependency-artifact path changed");
  }

  verdict.mode = artifactRequired ? "artifact" : "guard-only";

  if (treeTruncated) {
    return verdict.fail("candidate tree listing was truncated; refusing to judge a partial view");
  }
  if (treeEntries.length > policy.limits.maxTreeEntries) {
    return verdict.fail("candidate tree exceeds the reviewable entry limit");
  }

  const byPath = new Map();
  for (const entry of treeEntries) {
    if (entry.type === "commit" || entry.mode === BLOB_MODE_GITLINK) {
      return verdict.fail(
        `candidate tree contains a submodule at '${sanitizeToken(entry.path, 100)}'`,
      );
    }
    if (entry.type === "blob") byPath.set(entry.path, entry);
  }

  /* 1. Nothing that re-enables npm configuration or a competing lockfile. */
  for (const path of byPath.keys()) {
    const basename = path.slice(path.lastIndexOf("/") + 1);
    if (policy.forbiddenTree.basenames.includes(basename)) {
      verdict.fail(
        `candidate tree contains a forbidden '${sanitizeToken(basename, 40)}' at '${sanitizeToken(path, 100)}'`,
      );
    }
    if (policy.forbiddenTree.exact.includes(path)) {
      verdict.fail(`candidate tree contains a forbidden '${sanitizeToken(path, 60)}'`);
    }
  }

  /* 2. The vendor directory holds only reviewed files, as plain regular blobs. */
  for (const path of [...byPath.keys()].filter((entry) => entry.startsWith("vendor/"))) {
    const entry = byPath.get(path);
    if (entry.mode === BLOB_MODE_SYMLINK) {
      return verdict.fail(`vendor path '${sanitizeToken(path, 100)}' is a symlink`);
    }
    if (entry.mode === BLOB_MODE_EXECUTABLE) {
      return verdict.fail(`vendor path '${sanitizeToken(path, 100)}' is executable`);
    }
    if (entry.mode !== BLOB_MODE_REGULAR) {
      return verdict.fail(
        `vendor path '${sanitizeToken(path, 100)}' has mode ${sanitizeToken(entry.mode, 10)}`,
      );
    }
    if (!policy.vendor.allowedFiles.includes(path)) {
      return verdict.fail(
        `vendor path '${sanitizeToken(path, 100)}' is outside the reviewed allowlist`,
      );
    }
  }

  const artifactPresent = byPath.has(policy.package.artifactPath);
  if (artifactRequired && !artifactPresent) {
    return verdict.fail(
      "candidate removes the reviewed dependency artifact; removal requires a trusted policy change first",
    );
  }
  const validateArtifact = artifactRequired || artifactPresent;
  if (validateArtifact) {
    for (const required of policy.vendor.allowedFiles) {
      if (!byPath.has(required)) {
        return verdict.fail(`reviewed vendor file '${sanitizeToken(required, 100)}' is missing`);
      }
    }
  }

  /* 3. Fetch only the blobs we must inspect, content-addressed. */
  const wanted = new Set([
    "package.json",
    "package-lock.json",
    ".gitattributes",
    ...policy.documentScan.paths,
    ...(validateArtifact
      ? [...policy.vendor.allowedFiles, ...Object.keys(policy.digestPins)]
      : []),
  ]);
  const contents = new Map();
  let totalBytes = 0;
  for (const path of wanted) {
    const entry = byPath.get(path);
    if (!entry) {
      if (validateArtifact && (policy.digestPins[path] || policy.vendor.allowedFiles.includes(path))) {
        return verdict.fail(
          `required file '${sanitizeToken(path, 100)}' is missing from the candidate tree`,
        );
      }
      continue;
    }
    if (typeof entry.size === "number" && entry.size > policy.limits.maxBlobBytes) {
      return verdict.fail(`candidate file '${sanitizeToken(path, 100)}' exceeds the blob size limit`);
    }
    let bytes;
    try {
      bytes = await readBlob(entry.sha, path);
    } catch (error) {
      return verdict.fail(
        `could not read '${sanitizeToken(path, 80)}': ${sanitizeToken(error?.message, 60)}`,
      );
    }
    if (bytes.length > policy.limits.maxBlobBytes) {
      return verdict.fail(`candidate file '${sanitizeToken(path, 100)}' exceeds the blob size limit`);
    }
    totalBytes += bytes.length;
    if (totalBytes > policy.limits.maxTotalBlobBytes) {
      return verdict.fail("candidate inspection exceeded the total download limit");
    }
    if (gitBlobId(bytes) !== entry.sha) {
      return verdict.fail(
        `candidate file '${sanitizeToken(path, 100)}' did not match its Git object id`,
      );
    }
    contents.set(path, bytes);
  }

  /* 4. Always-on guard invariants, artifact present or not. */
  let packageJson = null;
  let packageLock = null;
  try {
    packageJson = parseCandidateJson(contents.get("package.json"), "package.json", policy);
    checkRootScripts(verdict, policy, packageJson, "package.json");
  } catch (error) {
    verdict.fail(`package.json rejected: ${sanitizeToken(error?.message, 100)}`);
  }
  try {
    packageLock = parseCandidateJson(contents.get("package-lock.json"), "package-lock.json", policy);
    checkLockBinShadowing(verdict, policy, packageLock);
  } catch (error) {
    verdict.fail(`package-lock.json rejected: ${sanitizeToken(error?.message, 100)}`);
  }
  if (contents.has(".gitattributes") && validateArtifact) {
    checkGitattributes(verdict, policy, Buffer.from(contents.get(".gitattributes")).toString("utf8"));
  }

  /* Reviewer-facing documentation must not re-open pre-trust execution. */
  for (const path of policy.documentScan.paths) {
    const bytes = contents.get(path);
    if (!bytes) continue;
    if (bytes.length > policy.limits.maxDocumentBytes) {
      verdict.fail(`document '${sanitizeToken(path, 80)}' exceeds the scan size limit`);
      continue;
    }
    for (const error of scanDocumentForForbiddenCommands(
      policy,
      Buffer.from(bytes).toString("utf8"),
      path,
    )) {
      verdict.fail(error);
    }
  }

  if (!validateArtifact) {
    /* The artifact is not in base yet. Referencing it without shipping it is a
     * lockfile that cannot install, so it fails closed rather than passing. */
    const spec = policy.package.spec;
    const referenced =
      packageJson?.devDependencies?.[policy.package.name] === spec ||
      packageLock?.packages?.[policy.package.lockPath]?.resolved === spec;
    if (referenced) {
      verdict.fail(
        "package metadata references the reviewed artifact spec but the artifact bytes are absent",
      );
    }
    if (currentHeadSha !== undefined && currentHeadSha !== eventHeadSha) {
      verdict.fail("pull request head moved during validation; re-run against the new head");
    }
    if (!verdict.failed) verdict.note("guard invariants held; no reviewed artifact in scope");
    return verdict;
  }

  /* 5. Byte pins straight from base policy. The candidate cannot move these. */
  for (const [path, pin] of Object.entries(policy.digestPins)) {
    const bytes = contents.get(path);
    if (!bytes) {
      verdict.fail(`pinned file '${sanitizeToken(path, 100)}' is missing`);
      continue;
    }
    if (bytes.length !== pin.size) {
      verdict.fail(
        `pinned file '${sanitizeToken(path, 100)}' is ${bytes.length} bytes, expected ${pin.size}`,
      );
      continue;
    }
    const actual = sha256Hex(bytes);
    if (actual !== pin.sha256) {
      verdict.fail(
        `pinned file '${sanitizeToken(path, 100)}' digest ${actual.slice(0, 16)} does not match base policy`,
      );
    }
  }
  if (verdict.failed) return verdict;

  /* 6. The candidate verifier's own constants must equal base policy values. */
  const verifierSource = Buffer.from(
    contents.get(policy.verifierPolicyLiterals.path) ?? Buffer.alloc(0),
  ).toString("utf8");
  try {
    const literals = extractPolicyLiterals(
      verifierSource,
      policy.verifierPolicyLiterals.objectName,
    );
    const expectations = {
      ...policy.verifierPolicyLiterals.required,
      ...policy.verifierPolicyLiterals.requiredNumbers,
    };
    for (const [key, expected] of Object.entries(expectations)) {
      if (literals.get(key) !== expected) {
        verdict.fail(
          `candidate ${policy.verifierPolicyLiterals.objectName}.${sanitizeToken(key, 40)} does not match base policy`,
        );
      }
    }
  } catch (error) {
    verdict.fail(`candidate verifier literals unreadable: ${sanitizeToken(error?.message, 80)}`);
  }
  const advisories = extractAdvisoryIds(verifierSource);
  for (const advisory of policy.verifierPolicyLiterals.requiredAdvisories) {
    if (!advisories.includes(advisory)) {
      verdict.fail(`candidate verifier no longer covers ${sanitizeToken(advisory, 40)}`);
    }
  }

  /* 7. Declarative reading of the candidate artifact and its manifests. */
  let tarEntries;
  try {
    tarEntries = parseCandidateTarball(contents.get(policy.package.artifactPath), policy);
  } catch (error) {
    return verdict.fail(`candidate artifact rejected: ${sanitizeToken(error?.message, 120)}`);
  }
  const artifactBytes = contents.get(policy.package.artifactPath);
  if (sha512Hex(artifactBytes) !== policy.package.tar.sha512) {
    verdict.fail("candidate artifact SHA-512 does not match base policy");
  }
  if (tarEntries.length !== policy.package.tar.fileCount) {
    verdict.fail(
      `candidate artifact packs ${tarEntries.length} files, expected ${policy.package.tar.fileCount}`,
    );
  }
  checkPackedManifest(verdict, policy, tarEntries);
  if (packageJson) checkArtifactPackageJson(verdict, policy, packageJson);
  if (packageLock) checkArtifactPackageLock(verdict, policy, packageLock);
  try {
    checkProvenance(
      verdict,
      policy,
      parseCandidateJson(contents.get(policy.package.provenancePath), "provenance.json", policy),
      tarEntries,
    );
  } catch (error) {
    verdict.fail(`provenance.json rejected: ${sanitizeToken(error?.message, 100)}`);
  }

  /* 8. Force-push read-back. Blobs are content-addressed, so a moved head can
   *    only mean the judged tree is no longer the tree under review. */
  if (currentHeadSha !== undefined && currentHeadSha !== eventHeadSha) {
    verdict.fail("pull request head moved during validation; re-run against the new head");
  }

  if (!verdict.failed) {
    verdict.note(
      `validated ${sanitizeToken(eventHeadSha.slice(0, 12), 12)} against base policy v${policy.policyVersion}`,
    );
  }
  return verdict;
}

/* ------------------------------------------------------------------ *
 * GitHub REST reader — read-only, no candidate code, no shell
 * ------------------------------------------------------------------ */

function requireEnv(name) {
  const value = process.env[name];
  if (!value) throw new Error(`missing required environment variable ${name}`);
  return value;
}

export function createGitHubReader({ apiUrl, owner, repo, token, fetchImpl = fetch }) {
  if (!OWNER_NAME.test(owner ?? "") || !OWNER_NAME.test(repo ?? "")) {
    throw new Error("repository coordinates failed validation");
  }
  const base = `${String(apiUrl).replace(/\/+$/, "")}/repos/${owner}/${repo}`;
  const headers = {
    accept: "application/vnd.github+json",
    "x-github-api-version": "2022-11-28",
    "user-agent": "trusted-dependency-artifact-gate",
    ...(token ? { authorization: `Bearer ${token}` } : {}),
  };

  async function get(path, searchParams = {}) {
    const url = new URL(`${base}${path}`);
    for (const [key, value] of Object.entries(searchParams)) {
      url.searchParams.set(key, String(value));
    }
    const response = await fetchImpl(url, { headers });
    if (!response.ok) throw new Error(`GitHub API ${response.status} for ${path}`);
    return response.json();
  }

  return {
    async listChangedFiles(pullNumber, maxFiles) {
      const paths = [];
      for (let page = 1; page <= 10; page += 1) {
        const batch = await get(`/pulls/${pullNumber}/files`, { per_page: 100, page });
        if (!Array.isArray(batch)) throw new Error("unexpected pull files payload");
        for (const file of batch) paths.push(String(file.filename));
        if (batch.length < 100) return { paths, truncated: false };
        if (paths.length > maxFiles) return { paths, truncated: true };
      }
      return { paths, truncated: true };
    },
    async readTree(sha) {
      if (!FULL_OBJECT_ID.test(sha)) throw new Error("tree id failed validation");
      const tree = await get(`/git/trees/${sha}`, { recursive: 1 });
      return {
        truncated: Boolean(tree.truncated),
        entries: (tree.tree ?? []).map((entry) => ({
          path: String(entry.path),
          mode: String(entry.mode),
          type: String(entry.type),
          sha: String(entry.sha),
          size: typeof entry.size === "number" ? entry.size : undefined,
        })),
      };
    },
    async readBlob(sha) {
      if (!FULL_OBJECT_ID.test(sha)) throw new Error("blob id failed validation");
      const blob = await get(`/git/blobs/${sha}`);
      if (blob.encoding !== "base64") throw new Error("unexpected blob encoding");
      return Buffer.from(String(blob.content), "base64");
    },
    async currentHeadSha(pullNumber) {
      const pull = await get(`/pulls/${pullNumber}`);
      return String(pull?.head?.sha ?? "");
    },
  };
}

export async function main() {
  const repoRoot = process.env.GATE_REPO_ROOT || defaultRepoRoot;
  const policy = loadPolicy(repoRoot);
  let verdict;
  try {
    const [owner, repo] = requireEnv("GATE_REPOSITORY").split("/");
    const pullNumber = Number(requireEnv("GATE_PR_NUMBER"));
    if (!Number.isSafeInteger(pullNumber) || pullNumber <= 0) {
      throw new Error("pull request number failed validation");
    }
    const eventHeadSha = requireEnv("GATE_HEAD_SHA");
    const baseRef = requireEnv("GATE_BASE_REF");
    const defaultBranch = process.env.GATE_DEFAULT_BRANCH || policy.defaultBranch;

    const reader = createGitHubReader({
      apiUrl: process.env.GITHUB_API_URL || "https://api.github.com",
      owner,
      repo,
      token: process.env.GATE_TOKEN,
    });

    const changed = await reader.listChangedFiles(pullNumber, policy.limits.maxChangedFiles);
    const preliminary = classifyChangedPaths(policy, changed.paths);
    const inspect =
      preliminary.guarded.length > 0 &&
      preliminary.trusted.length === 0 &&
      preliminary.unsafe.length === 0 &&
      FULL_OBJECT_ID.test(eventHeadSha);

    /* The tree is addressed by the event head SHA and every blob is verified
     * against its own Git object id, so a force-push cannot substitute content
     * mid-run; the read-back below turns a moved head into an explicit failure. */
    const tree = inspect
      ? await reader.readTree(eventHeadSha)
      : { truncated: false, entries: [] };

    verdict = await evaluateCandidate({
      policy,
      baseRef,
      defaultBranch,
      eventHeadSha,
      currentHeadSha: inspect ? await reader.currentHeadSha(pullNumber) : undefined,
      changedPaths: changed.paths,
      changedPathsTruncated: changed.truncated,
      artifactRequired: artifactRequiredByBase(policy, repoRoot),
      treeEntries: tree.entries,
      treeTruncated: tree.truncated,
      readBlob: (sha) => reader.readBlob(sha),
    });
  } catch (error) {
    verdict = new Verdict(policy.limits);
    verdict.mode = "gate-error";
    verdict.fail(`gate could not complete: ${sanitizeToken(error?.message, 140)}`);
  }

  const payload = JSON.stringify(verdict.toJSON());
  process.stdout.write(`${payload}\n`);
  if (process.env.GITHUB_OUTPUT) {
    appendFileSync(
      process.env.GITHUB_OUTPUT,
      `verdict=${Buffer.from(payload, "utf8").toString("base64")}\n`,
    );
  }
  return verdict.failed ? 1 : 0;
}

export function isCliExecution(argv = process.argv, moduleUrl = import.meta.url) {
  if (!argv || !argv[1]) return false;
  return pathToFileURL(argv[1]).href === moduleUrl;
}

if (isCliExecution()) {
  process.exit(await main());
}
