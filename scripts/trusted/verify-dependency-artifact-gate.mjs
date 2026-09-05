/*
 * Base-controlled dependency-artifact preflight evaluator.
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
 *   - The candidate's verifier, hard-coded hashes, workflows and tests are
 *     never executed or trusted. Where the approved activation set requires
 *     them, their bytes are compared with immutable base-policy pins only.
 *     Coherent malicious edits across all of them cannot influence this result.
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
import { appendFileSync, readFileSync } from "node:fs";
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
const C0_C1_CONTROL = /[\u0000-\u001f\u007f-\u009f]/u;
const BIDI_CONTROL = /[\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069]/u;
const CHECKOUT_IGNORABLE =
  /[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff\ufe00-\ufe0f]|[\u{e0100}-\u{e01ef}]/u;
const WINDOWS_DEVICE_STEM =
  /^(?:con|prn|aux|nul|clock\$|conin\$|conout\$|com[1-9]|lpt[1-9]|com[¹²³]|lpt[¹²³])$/iu;
const DOS_SHORT_NAME_ALIAS =
  /^(?:[^.\/]{1,6}|\.git)~[1-9][0-9]*(?:\.[^.\/]*)?$/iu;

const BLOB_MODE_REGULAR = "100644";
const BLOB_MODE_EXECUTABLE = "100755";
const BLOB_MODE_SYMLINK = "120000";
const BLOB_MODE_GITLINK = "160000";
const PINNABLE_BLOB_MODES = new Set([BLOB_MODE_REGULAR, BLOB_MODE_EXECUTABLE]);

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
    "documentation",
    "renames",
    "rotation",
    "activation",
    "rootScripts",
    "forbiddenTree",
    "gitattributes",
  ]) {
    if (!(key in policy)) throw new Error(`trusted policy is missing '${key}'`);
  }
  for (const [path, pin] of Object.entries(policy.digestPins)) {
    if (!/^[0-9a-f]{64}$/.test(pin.sha256) || (pin.blob && !FULL_OBJECT_ID.test(pin.blob))) {
      throw new Error(`trusted policy digest for '${path}' is not a SHA-256`);
    }
    if (!Number.isSafeInteger(pin.size) || pin.size <= 0) {
      throw new Error(`trusted policy size for '${path}' is not a positive integer`);
    }
  }
  if (!policy.vendor.allowedFiles.includes(policy.package.artifactPath)) {
    throw new Error("trusted policy artifactPath is not in the vendor allowlist");
  }
  const vendorReadme = policy.documentation?.vendorReadme;
  if (
    !vendorReadme ||
    !policy.vendor.allowedFiles.includes(vendorReadme.path) ||
    policy.digestPins[vendorReadme.path]?.sha256 !== vendorReadme.sha256 ||
    policy.digestPins[vendorReadme.path]?.size !== vendorReadme.size ||
    !/^[0-9a-f]{64}$/.test(vendorReadme.templateSha256 ?? "") ||
    !Number.isSafeInteger(vendorReadme.templateSize) ||
    vendorReadme.templateSize <= 0
  ) {
    throw new Error("trusted policy vendor README must be an exact digest-pinned vendor file");
  }
  if (policy.renames.allowProtectedPathRenames !== false) {
    throw new Error("trusted policy must reject protected-path renames");
  }
  if (
    policy.rotation?.policyFirst !== true ||
    policy.rotation?.artifactAfterPolicy !== true ||
    policy.rotation?.noUnguardedWindow !== true
  ) {
    throw new Error("trusted policy must require policy-first artifact rotation");
  }
  const activation = policy.activation;
  if (
    activation?.strategy !== "base-relative-exact-tree-delta" ||
    activation?.requiredBasePolicyVersion !== policy.policyVersion ||
    activation?.requiresCompleteSet !== true ||
    !Array.isArray(activation?.allowedFiles) ||
    activation.allowedFiles.length === 0 ||
    !activation?.basePins ||
    !activation?.pins ||
    Object.keys(activation.basePins).length !== activation.allowedFiles.length ||
    Object.keys(activation.pins).length !== activation.allowedFiles.length ||
    !/^[0-9a-f]{64}$/.test(activation?.patchSha256 ?? "")
  ) {
    throw new Error("trusted policy activation must enumerate an exact non-empty file set");
  }
  const activationPaths = new Set(activation.allowedFiles);
  if (activationPaths.size !== activation.allowedFiles.length) {
    throw new Error("trusted policy activation contains a duplicate path");
  }
  const activationFolded = new Map();
  const trustedFolded = new Set(
    policy.trustedPaths.map(path => {
      const identity = canonicalRepositoryPathIdentity(path);
      if (identity.unsafe) throw new Error("trusted policy contains an unsafe trusted path");
      return identity.folded;
    }),
  );
  for (const path of activation.allowedFiles) {
    const identity = canonicalRepositoryPathIdentity(path);
    if (identity.unsafe) throw new Error("trusted policy activation contains an unsafe path");
    if (
      activationFolded.has(identity.folded) &&
      activationFolded.get(identity.folded) !== identity.canonical
    ) {
      throw new Error("trusted policy activation contains a case or NFC collision");
    }
    if (trustedFolded.has(identity.folded)) {
      throw new Error(`activation path '${path}' overlaps a trusted path`);
    }
    activationFolded.set(identity.folded, identity.canonical);
  }
  for (const requiredPath of [
    "package.json",
    "package-lock.json",
    ".gitattributes",
    policy.package?.artifactPath,
    policy.package?.provenancePath,
    policy.documentation?.vendorReadme?.path,
  ]) {
    if (!policy.digestPins[requiredPath]) {
      throw new Error(`trusted policy is missing the exact post-activation pin for '${requiredPath}'`);
    }
  }
  for (const [path, pin] of Object.entries(activation.pins)) {
    if (!activationPaths.has(path)) {
      throw new Error(`activation pin '${path}' is outside the allowed activation file set`);
    }
    const identity = canonicalRepositoryPathIdentity(path);
    if (identity.unsafe || activationFolded.get(identity.folded) !== identity.canonical) {
      throw new Error(`activation pin '${path}' does not match its canonical allowed path`);
    }
    if (
      !/^[0-9a-f]{64}$/.test(pin.sha256) ||
      !FULL_OBJECT_ID.test(pin.blob ?? "") ||
      !PINNABLE_BLOB_MODES.has(pin.mode) ||
      JSON.stringify(Object.keys(pin).sort()) !==
        JSON.stringify(["blob", "mode", "sha256", "size"])
    ) {
      throw new Error(`activation pin for '${path}' is not an exact Git blob and SHA-256`);
    }
    if (!Number.isSafeInteger(pin.size) || pin.size <= 0) {
      throw new Error(`activation pin for '${path}' has an invalid size`);
    }
  }
  for (const [path, pin] of Object.entries(activation.basePins)) {
    if (!activationPaths.has(path)) {
      throw new Error(`activation base pin '${path}' is outside the allowed activation file set`);
    }
    if (pin?.absent === true) {
      if (Object.keys(pin).length !== 1) {
        throw new Error(`activation base pin for '${path}' mixes absent and present state`);
      }
      continue;
    }
    if (
      !FULL_OBJECT_ID.test(pin?.blob ?? "") ||
      !PINNABLE_BLOB_MODES.has(pin?.mode) ||
      JSON.stringify(Object.keys(pin ?? {}).sort()) !== JSON.stringify(["blob", "mode"])
    ) {
      throw new Error(`activation base pin for '${path}' is not an exact Git blob and mode`);
    }
  }
  if (activationPatchDigest(activation) !== activation.patchSha256) {
    throw new Error("trusted policy activation patch digest does not match its exact pins");
  }
  buildPathIdentityIndex(policy);
  return policy;
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

export function activationPatchDigest(activation) {
  const records = [...(activation?.allowedFiles ?? [])]
    .sort()
    .map(path => ({
      path,
      base: activation?.basePins?.[path]?.absent === true
        ? { absent: true }
        : {
            mode: activation?.basePins?.[path]?.mode,
            blob: activation?.basePins?.[path]?.blob,
          },
      target: {
        mode: activation?.pins?.[path]?.mode,
        blob: activation?.pins?.[path]?.blob,
        sha256: activation?.pins?.[path]?.sha256,
        size: activation?.pins?.[path]?.size,
      },
    }));
  return sha256Hex(Buffer.from(JSON.stringify(records), "utf8"));
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

export function asciiCaseFold(path) {
  return typeof path === "string"
    ? path.replace(/[A-Z]/g, character => character.toLowerCase())
    : path;
}

function isCheckoutUnsafeSegment(segment) {
  const deviceStem = segment.split(".", 1)[0].replace(/[ .]+$/u, "");
  if (
    segment === "" ||
    segment === "." ||
    segment === ".." ||
    /[ .]$/u.test(segment) ||
    segment.includes(":") ||
    C0_C1_CONTROL.test(segment) ||
    BIDI_CONTROL.test(segment) ||
    CHECKOUT_IGNORABLE.test(segment) ||
    WINDOWS_DEVICE_STEM.test(deviceStem) ||
    DOS_SHORT_NAME_ALIAS.test(segment) ||
    asciiCaseFold(segment) === ".git"
  ) {
    return true;
  }
  return false;
}

function canonicalRepositoryPathOrNull(path) {
  if (
    typeof path !== "string" ||
    path.length === 0 ||
    path.length > 400 ||
    path.startsWith("/") ||
    path.includes("\\") ||
    C0_C1_CONTROL.test(path) ||
    BIDI_CONTROL.test(path)
  ) {
    return null;
  }
  const canonical = path.normalize("NFC");
  if (
    canonical.length === 0 ||
    canonical.length > 400 ||
    canonical.startsWith("/") ||
    canonical.includes("\\") ||
    C0_C1_CONTROL.test(canonical) ||
    BIDI_CONTROL.test(canonical)
  ) {
    return null;
  }
  const segments = canonical.split("/");
  if (segments.length > 32 || segments.some(isCheckoutUnsafeSegment)) return null;
  return canonical;
}

export function isUnsafeRepositoryPath(path) {
  return canonicalRepositoryPathOrNull(path) === null;
}

export function normalizeRepositoryPath(path) {
  return canonicalRepositoryPathOrNull(path);
}

/*
 * GitHub stores repository paths with forward slashes, while Windows
 * checkouts and case-insensitive filesystems can make several spellings refer
 * to the same object.  This is the only path identity function used by the
 * evaluator.  `canonical` preserves spelling after NFC normalization and
 * `folded` is the collision-safe identity used for policy matching.
 */
export function canonicalRepositoryPathIdentity(path) {
  const canonical = canonicalRepositoryPathOrNull(path);
  if (canonical === null) {
    return {
      original: path,
      normalized: null,
      canonical: null,
      folded: null,
      unsafe: true,
    };
  }
  return {
    original: path,
    normalized: canonical,
    canonical,
    folded: asciiCaseFold(canonical),
    unsafe: false,
  };
}

export const canonicalizeRepositoryPath = canonicalRepositoryPathIdentity;

function patternIdentity(pattern, kind) {
  if (typeof pattern !== "string") {
    throw new Error(`trusted policy ${kind} contains an unsafe path pattern`);
  }
  let marker = "";
  let body = pattern;
  if (kind === "prefix") {
    if (!pattern.endsWith("/")) {
      throw new Error("trusted policy prefix must end with '/'");
    }
    body = pattern.slice(0, -1);
    marker = "/";
  } else if (kind === "suffix") {
    if (!pattern.startsWith("/")) {
      throw new Error("trusted policy suffix must start with '/'");
    }
    body = pattern.slice(1);
    marker = "/";
  }
  const identity = canonicalRepositoryPathIdentity(body);
  if (identity.unsafe || (kind === "forbidden basename" && identity.canonical.includes("/"))) {
    throw new Error(`trusted policy ${kind} contains an unsafe path pattern`);
  }
  const canonical =
    kind === "suffix" ? `${marker}${identity.canonical}` : `${identity.canonical}${marker}`;
  return { canonical, folded: asciiCaseFold(canonical) };
}

function addIdentity(map, identity, value) {
  if (!map.has(identity.folded)) map.set(identity.folded, new Set());
  map.get(identity.folded).add(value);
}

function addProtectedPath(index, path, kind) {
  const identity = canonicalRepositoryPathIdentity(path);
  if (identity.unsafe) throw new Error(`trusted policy ${kind} contains an unsafe path`);
  addIdentity(index.protectedExact, identity, identity.canonical);
  if (kind === "trusted") addIdentity(index.trustedExact, identity, identity.canonical);
  if (kind === "guarded") addIdentity(index.guardedExact, identity, identity.canonical);
  if (kind === "forbidden") addIdentity(index.forbiddenExact, identity, identity.canonical);
  index.protectedCanonical.add(identity.canonical);
}

function addProtectedPattern(index, pattern, kind) {
  const identity = patternIdentity(pattern, kind);
  const target = kind === "prefix" ? index.guardedPrefixes : index.guardedSuffixes;
  target.push(identity);
}

function addPathLikePolicyValues(index, policy, values, kind) {
  for (const value of values ?? []) {
    if (typeof value === "string") addProtectedPath(index, value, kind);
  }
}

/*
 * Build all policy identities once for a classification pass.  In addition
 * to the visible trusted/guarded declarations, package, artifact, provenance,
 * documentation, verifier, activation, and forbidden identities are included
 * so a candidate cannot hide a protected path by changing case or NFC form.
 */
function buildPathIdentityIndex(policy) {
  const index = {
    trustedExact: new Map(),
    guardedExact: new Map(),
    forbiddenExact: new Map(),
    protectedExact: new Map(),
    protectedCanonical: new Set(),
    guardedPrefixes: [],
    guardedSuffixes: [],
    forbiddenBasenames: new Map(),
    activationAllowed: new Map(),
  };

  addPathLikePolicyValues(index, policy, policy.trustedPaths, "trusted");
  addPathLikePolicyValues(index, policy, policy.guardedPaths?.exact, "guarded");
  for (const prefix of policy.guardedPaths?.prefixes ?? []) {
    addProtectedPattern(index, prefix, "prefix");
  }
  for (const suffix of policy.guardedPaths?.suffixes ?? []) {
    addProtectedPattern(index, suffix, "suffix");
  }

  addPathLikePolicyValues(index, policy, Object.keys(policy.digestPins ?? {}), "guarded");
  addPathLikePolicyValues(index, policy, policy.vendor?.allowedFiles, "guarded");
  if (typeof policy.vendor?.root === "string") {
    const root = policy.vendor.root.endsWith("/")
      ? policy.vendor.root.slice(0, -1)
      : policy.vendor.root;
    addProtectedPattern(index, `${root}/`, "prefix");
  }
  addPathLikePolicyValues(index, policy, [
    policy.package?.artifactPath,
    policy.package?.provenancePath,
    policy.package?.lockPath,
    policy.package?.workspacePath,
    ...(Array.isArray(policy.package?.workspaces)
      ? policy.package.workspaces
      : typeof policy.package?.workspaces === "string"
        ? [policy.package.workspaces]
        : []),
    policy.package?.configPath,
    ...(policy.package?.configPaths ?? []),
    policy.verifierPolicyLiterals?.path,
    policy.documentation?.vendorReadme?.path,
    policy.documentation?.vendorReadme?.templatePath,
    ...(policy.documentation?.trustedPreTrustPaths ?? []),
    ...(policy.workspacePaths ?? []),
    ...(policy.configPaths ?? []),
    ...(policy.forbiddenTree?.configPaths ?? []),
  ], "protected");

  addPathLikePolicyValues(index, policy, policy.forbiddenTree?.exact, "forbidden");
  for (const basename of policy.forbiddenTree?.basenames ?? []) {
    const identity = patternIdentity(basename, "forbidden basename");
    addIdentity(index.forbiddenBasenames, identity, identity.canonical);
    index.protectedCanonical.add(identity.canonical);
  }

  for (const path of policy.activation?.allowedFiles ?? []) {
    const identity = canonicalRepositoryPathIdentity(path);
    if (identity.unsafe) throw new Error("trusted policy activation contains an unsafe path");
    index.activationAllowed.set(identity.canonical, identity);
    addIdentity(index.protectedExact, identity, identity.canonical);
    index.protectedCanonical.add(identity.canonical);
  }
  for (const [path, pin] of Object.entries(policy.activation?.pins ?? {})) {
    const identity = canonicalRepositoryPathIdentity(path);
    if (identity.unsafe) throw new Error("trusted policy activation pin contains an unsafe path");
    index.activationAllowed.set(identity.canonical, identity);
    addIdentity(index.protectedExact, identity, identity.canonical);
    index.protectedCanonical.add(identity.canonical);
  }
  return index;
}

function matchingProtectedAliases(index, identity) {
  const aliases = [];
  for (const [folded, canonicals] of index.protectedExact) {
    if (folded !== identity.folded) continue;
    for (const canonical of canonicals) {
      if (canonical !== identity.canonical || identity.original !== identity.canonical) {
        aliases.push(canonical);
      }
    }
  }
  for (const prefix of index.guardedPrefixes) {
    if (
      identity.folded.startsWith(prefix.folded) &&
      (!identity.canonical.startsWith(prefix.canonical) ||
        identity.original !== identity.canonical)
    ) {
      aliases.push(prefix.canonical);
    }
  }
  for (const suffix of index.guardedSuffixes) {
    if (
      identity.folded.endsWith(suffix.folded) &&
      (!identity.canonical.endsWith(suffix.canonical) ||
        identity.original !== identity.canonical)
    ) {
      aliases.push(suffix.canonical);
    }
  }
  const basename = identity.canonical.slice(identity.canonical.lastIndexOf("/") + 1);
  const foldedBasename = asciiCaseFold(basename);
  for (const [folded, canonicals] of index.forbiddenBasenames) {
    if (folded !== foldedBasename) continue;
    for (const canonical of canonicals) {
      if (canonical !== basename || basename !== identity.original.slice(identity.original.lastIndexOf("/") + 1)) {
        aliases.push(canonical);
      }
    }
  }
  return [...new Set(aliases)].sort();
}

function classifyRepositoryPath(policy, path, index = buildPathIdentityIndex(policy)) {
  const identity = canonicalRepositoryPathIdentity(path);
  if (identity.unsafe) {
    return {
      original: path,
      canonical: null,
      folded: null,
      trusted: false,
      guarded: false,
      activation: false,
      forbidden: false,
      alias: false,
      aliases: [],
      unsafe: true,
    };
  }
  const { canonical, folded } = identity;
  const trusted = index.trustedExact.has(folded);
  const guarded =
    index.guardedExact.has(folded) ||
    index.guardedPrefixes.some(prefix => folded.startsWith(prefix.folded)) ||
    index.guardedSuffixes.some(suffix => folded.endsWith(suffix.folded));
  const basename = canonical.slice(canonical.lastIndexOf("/") + 1);
  const forbidden =
    index.forbiddenExact.has(folded) ||
    index.forbiddenBasenames.has(asciiCaseFold(basename));
  const activation = index.activationAllowed.has(canonical);
  const aliases = matchingProtectedAliases(index, identity);
  return {
    original: path,
    canonical,
    folded,
    unsafe: false,
    trusted,
    guarded,
    activation,
    forbidden,
    alias: aliases.length > 0,
    aliases,
  };
}

export function classifyChangedPaths(policy, changedPaths) {
  const trusted = [];
  const guarded = [];
  const activation = [];
  const unsafe = [];
  const aliases = [];
  const forbidden = [];
  const canonicalPaths = [];
  const identities = [];
  const index = buildPathIdentityIndex(policy);

  for (const path of changedPaths ?? []) {
    const classification = classifyRepositoryPath(policy, path, index);
    if (classification.unsafe) {
      unsafe.push(path);
      continue;
    }
    canonicalPaths.push(classification.canonical);
    identities.push(classification);
    if (classification.trusted) trusted.push(path);
    if (classification.guarded) guarded.push(path);
    if (classification.activation) activation.push(path);
    if (classification.alias) aliases.push(path);
    if (classification.forbidden) forbidden.push(path);
  }
  return {
    trusted,
    guarded,
    activation,
    unsafe,
    aliases,
    forbidden,
    canonicalPaths,
    identities,
  };
}

export function classifyChangedFiles(policy, files) {
  const paths = [];
  for (const file of files ?? []) {
    if (!file || typeof file !== "object") {
      paths.push(null);
      continue;
    }
    paths.push(file.filename);
    if (file.previous_filename !== undefined) paths.push(file.previous_filename);
  }
  return classifyChangedPaths(policy, paths);
}

function uniqueSorted(values) {
  return [...new Set(values)].sort();
}

export function collectProtectedPathIdentityProblems(policy, baseEntries, headEntries) {
  const problems = [];
  const index = buildPathIdentityIndex(policy);
  const byCanonical = new Map();
  const byNfc = new Map();
  const byCaseFold = new Map();
  const allEntries = [
    ...(baseEntries ?? []).map(entry => ({ ...entry, side: "base" })),
    ...(headEntries ?? []).map(entry => ({ ...entry, side: "candidate" })),
  ];

  const addRecord = (path, side) => {
    const identity = canonicalRepositoryPathIdentity(path);
    if (identity.unsafe) {
      problems.push(`${side} tree contains an unsafe path '${sanitizeToken(path, 100)}'`);
      return;
    }
    const record = { ...identity, side };
    if (!byCanonical.has(identity.canonical)) byCanonical.set(identity.canonical, []);
    byCanonical.get(identity.canonical).push(record);
    if (!byNfc.has(identity.canonical)) byNfc.set(identity.canonical, new Set());
    byNfc.get(identity.canonical).add(path);
    if (!byCaseFold.has(identity.folded)) byCaseFold.set(identity.folded, new Set());
    byCaseFold.get(identity.folded).add(path);
    if (side === "candidate") {
      const classification = classifyRepositoryPath(policy, path, index);
      if (classification.alias) {
        problems.push(
          `candidate path '${sanitizeToken(path, 100)}' aliases protected identity '${sanitizeToken(classification.aliases[0], 100)}'`,
        );
      }
    }
  };

  for (const entry of allEntries) addRecord(entry?.path, entry?.side ?? "tree");

  for (const canonical of index.protectedCanonical) {
    if (!byCanonical.has(canonical)) {
      const identity = canonicalRepositoryPathIdentity(canonical);
      if (!identity.unsafe) {
        if (!byNfc.has(identity.canonical)) byNfc.set(identity.canonical, new Set());
        byNfc.get(identity.canonical).add(identity.canonical);
        if (!byCaseFold.has(identity.folded)) byCaseFold.set(identity.folded, new Set());
        byCaseFold.get(identity.folded).add(identity.canonical);
      }
    }
  }

  for (const [canonical, records] of byCanonical) {
    const originals = new Set(records.map(record => record.original));
    if (originals.size > 1) {
      problems.push(`tree contains duplicate canonical path '${sanitizeToken(canonical, 100)}'`);
    }
  }
  for (const [normalized, originals] of byNfc) {
    if (originals.size > 1) {
      problems.push(
        `tree has a Unicode-normalization collision at '${sanitizeToken(normalized, 100)}'`,
      );
    }
  }
  for (const [folded, originals] of byCaseFold) {
    if (originals.size > 1) {
      problems.push(`tree has an ASCII-case collision at '${sanitizeToken(folded, 100)}'`);
    }
  }

  /*
   * Include every real tree path plus base protected identities.  A file named
   * `package.json/child` or `vendor/child` is a directory/file collision even
   * when the policy's canonical file is absent from the candidate.
   */
  const prefixPaths = new Set([...byCaseFold.keys()]);
  for (const path of [...prefixPaths].sort()) {
    const segments = path.split("/");
    for (let indexPart = 1; indexPart < segments.length; indexPart += 1) {
      const ancestor = segments.slice(0, indexPart).join("/");
      if (prefixPaths.has(ancestor)) {
        problems.push(
          `tree contains a directory/file prefix collision between '${sanitizeToken(ancestor, 100)}' and '${sanitizeToken(path, 100)}'`,
        );
      }
    }
  }
  return uniqueSorted(problems);
}

export function diffImmutableTrees(baseEntries, headEntries, policy = null) {
  const base = new Map();
  const head = new Map();
  const duplicates = [];
  const keyFor = (entry, side, index) => {
    const identity = canonicalRepositoryPathIdentity(entry?.path);
    if (identity.unsafe) return `${side}:unsafe:${index}:${String(entry?.path ?? "")}`;
    return identity.canonical;
  };
  for (const [index, entry] of (baseEntries ?? []).entries()) {
    const key = keyFor(entry, "base", index);
    if (base.has(key)) duplicates.push(`base:${entry?.path ?? ""}`);
    base.set(key, entry);
  }
  for (const [index, entry] of (headEntries ?? []).entries()) {
    const key = keyFor(entry, "head", index);
    if (head.has(key)) duplicates.push(`head:${entry?.path ?? ""}`);
    head.set(key, entry);
  }

  const changes = [];
  for (const path of uniqueSorted([...base.keys(), ...head.keys()])) {
    const before = base.get(path);
    const after = head.get(path);
    if (
      before &&
      after &&
      before.sha === after.sha &&
      before.mode === after.mode &&
      before.type === after.type
    ) {
      continue;
    }
    changes.push({
      status: before && after ? "modified" : before ? "removed" : "added",
      filename: after?.path ?? before?.path,
      previous_filename: before && !after ? before.path : undefined,
      canonical_filename: path,
      before,
      after,
    });
  }

  const removedBySha = new Map();
  const addedBySha = new Map();
  for (const change of changes) {
    if (change.status === "removed" && change.before?.sha) {
      if (!removedBySha.has(change.before.sha)) removedBySha.set(change.before.sha, []);
      removedBySha.get(change.before.sha).push(change);
    }
    if (change.status === "added" && change.after?.sha) {
      if (!addedBySha.has(change.after.sha)) addedBySha.set(change.after.sha, []);
      addedBySha.get(change.after.sha).push(change);
    }
  }
  const inferredRenames = [];
  for (const [sha, removed] of removedBySha) {
    const added = addedBySha.get(sha) ?? [];
    if (removed.length === 1 && added.length === 1) {
      inferredRenames.push({
        status: "renamed",
        filename: added[0].filename,
        previous_filename: removed[0].filename,
      });
    }
  }
  return { base, head, changes, inferredRenames, duplicates };
}

export function validateChangedFileRecords(policy, files) {
  const problems = [];
  const index = buildPathIdentityIndex(policy);
  for (const file of files ?? []) {
    if (!file || typeof file !== "object") {
      problems.push("pull-file record is malformed");
      continue;
    }
    const status = String(file.status ?? "");
    const filename = file.filename;
    const next = classifyRepositoryPath(policy, filename, index);
    if (next.unsafe) {
      problems.push(`pull-file record has an unsafe path '${sanitizeToken(filename, 100)}'`);
      continue;
    }
    if (next.alias) {
      problems.push(
        `pull-file record path '${sanitizeToken(filename, 100)}' aliases protected identity '${sanitizeToken(next.aliases[0], 100)}'`,
      );
    }
    if (status === "renamed") {
      if (typeof file.previous_filename !== "string") {
        problems.push("renamed pull-file record omits previous_filename");
        continue;
      }
      const previous = classifyRepositoryPath(policy, file.previous_filename, index);
      if (previous.unsafe) {
        problems.push(
          `renamed pull-file record has an unsafe previous path '${sanitizeToken(file.previous_filename, 100)}'`,
        );
        continue;
      }
      if (previous.alias) {
        problems.push(
          `pull-file previous path '${sanitizeToken(file.previous_filename, 100)}' aliases protected identity '${sanitizeToken(previous.aliases[0], 100)}'`,
        );
      }
      if (
        !policy.renames.allowProtectedPathRenames &&
        (next.trusted || next.guarded || previous.trusted || previous.guarded)
      ) {
        problems.push(
          `protected-path rename '${sanitizeToken(file.previous_filename, 90)}' -> '${sanitizeToken(filename, 90)}' is forbidden`,
        );
      }
    }
  }
  return uniqueSorted(problems);
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

function checkExactBytePin(
  verdict,
  path,
  bytes,
  pin,
  label = "pinned file",
  entry = undefined,
) {
  if (!pin || !bytes || (pin.mode && !entry)) {
    verdict.fail(`${label} '${sanitizeToken(path, 100)}' is missing`);
    return;
  }
  if (pin.mode && entry.mode !== pin.mode) {
    verdict.fail(
      `${label} '${sanitizeToken(path, 100)}' mode ${sanitizeToken(entry.mode, 10)} does not match approved mode ${pin.mode}`,
    );
  }
  if (!Number.isSafeInteger(pin.size) || bytes.length !== pin.size) {
    verdict.fail(
      `${label} '${sanitizeToken(path, 100)}' is ${bytes.length} bytes, expected ${sanitizeToken(pin.size, 20)}`,
    );
    return;
  }
  const actualSha256 = sha256Hex(bytes);
  if (actualSha256 !== pin.sha256) {
    verdict.fail(
      `${label} '${sanitizeToken(path, 100)}' SHA-256 does not match the approved bytes`,
    );
  }
  if (pin.blob && gitBlobId(bytes) !== pin.blob) {
    verdict.fail(
      `${label} '${sanitizeToken(path, 100)}' Git blob does not match the approved bytes`,
    );
  }
}

function effectiveDigestPins(policy) {
  return {
    ...(policy.digestPins ?? {}),
    ...(policy.activation?.pins ?? {}),
  };
}

function sameSet(left, right) {
  if (left.size !== right.size) return false;
  return [...left].every(value => right.has(value));
}

function checkActivationBasePins(policy, baseBlobs, verdict) {
  for (const path of policy.activation.allowedFiles) {
    const expected = policy.activation.basePins[path];
    const actual = baseBlobs.get(path);
    if (expected.absent === true) {
      if (actual) {
        verdict.fail(
          `activation base path '${sanitizeToken(path, 100)}' must be absent for this approved patch`,
        );
      }
      continue;
    }
    if (!actual || actual.type !== "blob") {
      verdict.fail(
        `activation base path '${sanitizeToken(path, 100)}' is missing from the immutable base`,
      );
      continue;
    }
    if (actual.sha !== expected.blob || actual.mode !== expected.mode) {
      verdict.fail(
        `activation base path '${sanitizeToken(path, 100)}' does not match the approved base blob and mode`,
      );
    }
  }
}

/* ------------------------------------------------------------------ *
 * Retired evaluator retained only for local source compatibility
 * ------------------------------------------------------------------ */

async function legacyEvaluateCandidate({
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

  const { trusted, guarded, activation, unsafe } = classifyChangedPaths(policy, changedPaths);
  if (unsafe.length > 0) {
    verdict.mode = "unsafe-path";
    return verdict.fail(`pull request contains an unsafe path '${sanitizeToken(unsafe[0], 100)}'`);
  }
  if (trusted.length > 0 && (guarded.length > 0 || activation.length > 0)) {
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
  if (guarded.length === 0 && activation.length === 0) {
    verdict.mode = "not-applicable";
    return verdict.note("no guarded dependency-artifact path changed");
  }

  if (!artifactRequired) {
    verdict.mode = "activation-rejected";
    return verdict.fail(
      "the retired evaluator cannot authorize pre-activation protected-path changes",
    );
  }
  verdict.mode = "artifact";

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
    ...(validateArtifact
      ? [...policy.vendor.allowedFiles, ...Object.keys(effectiveDigestPins(policy))]
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
  for (const [path, pin] of Object.entries(effectiveDigestPins(policy))) {
    const bytes = contents.get(path);
    checkExactBytePin(verdict, path, bytes, pin, "pinned file", byPath.get(path));
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

function asChangedFileRecords(changedFiles, changedPaths) {
  if (Array.isArray(changedFiles)) return changedFiles;
  return (changedPaths ?? []).map(filename => ({ status: "modified", filename }));
}

function treeBlobMap(entries, side, verdict) {
  const blobs = new Map();
  const seen = new Set();
  for (const entry of entries ?? []) {
    if (!entry || typeof entry !== "object" || typeof entry.path !== "string") {
      verdict.fail(`${side} tree contains a malformed entry`);
      continue;
    }
    const identity = canonicalRepositoryPathIdentity(entry.path);
    if (identity.unsafe) {
      verdict.fail(`${side} tree contains an unsafe path '${sanitizeToken(entry.path, 100)}'`);
      continue;
    }
    if (seen.has(identity.canonical)) {
      verdict.fail(`${side} tree contains duplicate path '${sanitizeToken(entry.path, 100)}'`);
      continue;
    }
    seen.add(identity.canonical);
    if (entry.type === "commit" || entry.mode === BLOB_MODE_GITLINK) {
      verdict.fail(`${side} tree contains a submodule at '${sanitizeToken(entry.path, 100)}'`);
      continue;
    }
    if (entry.type === "blob") {
      if (!FULL_OBJECT_ID.test(String(entry.sha ?? ""))) {
        verdict.fail(`${side} tree blob '${sanitizeToken(entry.path, 100)}' has an invalid object id`);
        continue;
      }
      blobs.set(identity.canonical, { ...entry, canonicalPath: identity.canonical });
    }
  }
  return blobs;
}

function hasTreePath(blobs, path) {
  const identity = canonicalRepositoryPathIdentity(path);
  return !identity.unsafe && blobs.has(identity.canonical);
}

function artifactState(policy, baseBlobs, headBlobs, verdict) {
  const required = policy.vendor.allowedFiles;
  const basePresent = required.filter(path => hasTreePath(baseBlobs, path));
  const headPresent = required.filter(path => hasTreePath(headBlobs, path));
  const baseHasArtifact = hasTreePath(baseBlobs, policy.package.artifactPath);
  const headHasArtifact = hasTreePath(headBlobs, policy.package.artifactPath);

  if (basePresent.length !== 0 && basePresent.length !== required.length) {
    verdict.fail("base tree contains an incomplete reviewed artifact set");
  }
  if (baseHasArtifact && basePresent.length !== required.length) {
    verdict.fail("base tree artifact lacks required reviewed companion files");
  }
  if (baseHasArtifact && headPresent.length !== required.length) {
    verdict.fail(
      "candidate removes or moves a reviewed dependency artifact; removal requires a trusted policy rotation first",
    );
  }
  if (!baseHasArtifact && headPresent.length !== 0 && headPresent.length !== required.length) {
    verdict.fail("candidate adds an incomplete reviewed artifact set");
  }

  return {
    artifactRequired: baseHasArtifact,
    validateArtifact: baseHasArtifact || headHasArtifact,
    baseHasArtifact,
    headHasArtifact,
    activationCandidate: !baseHasArtifact && headHasArtifact,
  };
}

function classifyAllChanges(policy, changedFiles, treeChanges) {
  const paths = [];
  for (const file of [...changedFiles, ...treeChanges]) {
    if (!file || typeof file !== "object") {
      paths.push(null);
      continue;
    }
    paths.push(file.filename);
    if (file.previous_filename !== undefined) paths.push(file.previous_filename);
  }
  return classifyChangedPaths(policy, paths);
}

function failOnProtectedRename(policy, verdict, rename) {
  const classification = classifyChangedFiles(policy, [rename]);
  if (
    !policy.renames.allowProtectedPathRenames &&
    (classification.trusted.length > 0 || classification.guarded.length > 0)
  ) {
    verdict.fail(
      `protected-path rename '${sanitizeToken(rename.previous_filename, 90)}' -> '${sanitizeToken(rename.filename, 90)}' is forbidden`,
    );
  }
}

function requireTrustedPathContinuity(policy, baseBlobs, headBlobs, verdict) {
  const index = buildPathIdentityIndex(policy);
  for (const path of baseBlobs.keys()) {
    const classification = classifyRepositoryPath(policy, path, index);
    if (classification.trusted && !headBlobs.has(classification.canonical)) {
      verdict.fail(
        `trusted path '${sanitizeToken(path, 100)}' was removed or moved; policy rotations must modify trusted paths in place`,
      );
    }
  }
}

function checkRace(verdict, {
  eventHeadSha,
  eventBaseSha,
  baseRef,
  currentHeadSha,
  currentBaseSha,
  currentBaseRef,
}) {
  if (currentHeadSha !== undefined && currentHeadSha !== eventHeadSha) {
    verdict.fail("pull request head moved during validation; re-run against the new head");
  }
  if (currentBaseSha !== undefined && currentBaseSha !== eventBaseSha) {
    verdict.fail("pull request base moved during validation; re-run against the new base");
  }
  if (currentBaseRef !== undefined && currentBaseRef !== baseRef) {
    verdict.fail("pull request base ref changed during validation; re-run against the new base");
  }
}

/*
 * The only active evaluator. It independently compares immutable base/head
 * trees; `/pulls/{n}/files` is retained for rename evidence but is never the
 * sole source of path classification.
 */
export async function evaluateCandidate({
  policy,
  baseRef,
  defaultBranch,
  eventHeadSha,
  eventBaseSha,
  currentHeadSha,
  currentBaseSha,
  currentBaseRef,
  changedFiles,
  changedPaths,
  changedFilesTruncated = false,
  changedPathsTruncated = false,
  baseTreeEntries = [],
  baseTreeTruncated = false,
  treeEntries = [],
  treeTruncated = false,
  readBlob,
}) {
  const verdict = new Verdict(policy.limits);
  const fileRecords = asChangedFileRecords(changedFiles, changedPaths);
  const pathIndex = buildPathIdentityIndex(policy);

  if (!FULL_OBJECT_ID.test(String(eventHeadSha ?? ""))) {
    verdict.mode = "invalid-event";
    return verdict.fail("pull request head SHA is not a full object id");
  }
  if (!FULL_OBJECT_ID.test(String(eventBaseSha ?? ""))) {
    verdict.mode = "invalid-event";
    return verdict.fail("pull request base SHA is not a full object id");
  }
  if (baseRef !== defaultBranch) {
    verdict.mode = "invalid-base";
    return verdict.fail(
      `pull request targets '${sanitizeToken(baseRef, 60)}', but the gate only authorizes '${sanitizeToken(defaultBranch, 60)}'`,
    );
  }
  if (baseTreeTruncated || treeTruncated) {
    verdict.mode = "unbounded-change";
    return verdict.fail("base or candidate tree listing was truncated; refusing to judge a partial view");
  }

  const baseBlobs = treeBlobMap(baseTreeEntries, "base", verdict);
  const headBlobs = treeBlobMap(treeEntries, "candidate", verdict);
  const identityProblems = collectProtectedPathIdentityProblems(
    policy,
    baseTreeEntries,
    treeEntries,
  );
  for (const problem of identityProblems) {
    verdict.fail(problem);
  }

  const immutableDiff = diffImmutableTrees(baseTreeEntries, treeEntries, policy);
  for (const duplicate of immutableDiff.duplicates) {
    verdict.fail(`immutable tree diff contains duplicate path '${sanitizeToken(duplicate, 100)}'`);
  }
  if (immutableDiff.changes.length > policy.limits.maxChangedFiles) {
    verdict.mode = "unbounded-change";
    return verdict.fail(
      `immutable base/head tree diff changes ${immutableDiff.changes.length} files, above the reviewable limit`,
    );
  }
  for (const problem of validateChangedFileRecords(policy, fileRecords)) {
    verdict.fail(problem);
  }
  for (const inferredRename of immutableDiff.inferredRenames) {
    failOnProtectedRename(policy, verdict, inferredRename);
  }

  const classification = classifyAllChanges(policy, fileRecords, immutableDiff.changes);
  if (classification.unsafe.length > 0) {
    verdict.fail(
      `pull request contains an unsafe path '${sanitizeToken(classification.unsafe[0], 100)}'`,
    );
  }
  if (classification.aliases.length > 0) {
    verdict.fail(
      `pull request contains a protected-path alias '${sanitizeToken(classification.aliases[0], 100)}'`,
    );
  }
  if (
    (changedFilesTruncated || changedPathsTruncated) &&
    (
      classification.trusted.length > 0 ||
      classification.guarded.length > 0 ||
      classification.activation.length > 0
    )
  ) {
    verdict.fail(
      "pull-file listing was incomplete while immutable tree diff showed protected-path changes",
    );
  }

  const { artifactRequired, validateArtifact } = artifactState(
    policy,
    baseBlobs,
    headBlobs,
    verdict,
  );
  requireTrustedPathContinuity(policy, baseBlobs, headBlobs, verdict);

  const immutableChangedCanonicalPaths = new Set(
    immutableDiff.changes
      .map(change => canonicalRepositoryPathIdentity(change.filename))
      .filter(identity => !identity.unsafe)
      .map(identity => identity.canonical),
  );
  const activationAllowed = new Set([...pathIndex.activationAllowed.keys()]);
  const preActivationProtectedChange =
    !artifactRequired &&
    (classification.guarded.length > 0 || classification.activation.length > 0);
  const activationScope =
    !artifactRequired &&
    validateArtifact &&
    sameSet(immutableChangedCanonicalPaths, activationAllowed);
  if (preActivationProtectedChange) {
    if (!activationScope) {
      verdict.fail(
        "before artifact activation, every guarded or activation path change must equal the exact policy-approved activation file set",
      );
    } else {
      checkActivationBasePins(policy, baseBlobs, verdict);
      for (const path of activationAllowed) {
        const entry = headBlobs.get(path);
        const pin = policy.activation.pins[path];
        if (!entry) {
          verdict.fail(
            `activation file '${sanitizeToken(path, 100)}' is missing from the candidate tree`,
          );
        } else if (entry.sha !== pin.blob || entry.mode !== pin.mode) {
          verdict.fail(
            `activation file '${sanitizeToken(path, 100)}' does not match the approved Git blob and mode`,
          );
        }
      }
    }
  }

  if (
    classification.trusted.length > 0 &&
    classification.guarded.length > 0 &&
    !activationScope
  ) {
    verdict.mode = "mixed-trusted-and-guarded";
    verdict.fail(
      "trusted policy paths and guarded dependency paths must not change in the same pull request",
    );
  } else if (activationScope) {
    verdict.mode = "activation";
  } else if (preActivationProtectedChange) {
    verdict.mode = "activation-rejected";
  } else if (validateArtifact) {
    verdict.mode = "artifact";
  } else if (classification.trusted.length > 0) {
    verdict.mode = "policy-only";
  } else if (classification.guarded.length > 0 || classification.activation.length > 0) {
    verdict.mode = "activation-rejected";
    verdict.fail("pre-activation protected-path changes require the exact activation delta");
  } else {
    verdict.mode = "not-applicable";
  }
  if (classification.unsafe.length > 0) {
    verdict.mode = "unsafe-path";
  } else if (classification.aliases.length > 0) {
    verdict.mode = "path-alias";
  } else if (identityProblems.length > 0) {
    verdict.mode = "path-identity";
  } else if (changedFilesTruncated || changedPathsTruncated) {
    verdict.mode = "unbounded-change";
  }

  /* Nothing may re-enable npm configuration or a competing lockfile. */
  let forbiddenTreePath = false;
  for (const entry of treeEntries ?? []) {
    const path = entry?.path;
    const classification = classifyRepositoryPath(policy, path, pathIndex);
    if (classification.unsafe) continue;
    const canonical = classification.canonical;
    const basename = canonical.slice(canonical.lastIndexOf("/") + 1);
    if (classification.forbidden && policy.forbiddenTree.basenames.some(
      forbidden => asciiCaseFold(forbidden) === asciiCaseFold(basename),
    )) {
      forbiddenTreePath = true;
      verdict.fail(
        `candidate tree contains a forbidden '${sanitizeToken(basename, 40)}' at '${sanitizeToken(path, 100)}'`,
      );
    }
    if (classification.forbidden && pathIndex.forbiddenExact.has(classification.folded)) {
      forbiddenTreePath = true;
      verdict.fail(`candidate tree contains a forbidden '${sanitizeToken(path, 60)}'`);
    }
  }
  if (forbiddenTreePath && verdict.mode === "not-applicable") verdict.mode = "forbidden-path";

  /* The vendor directory holds only reviewed regular blobs. */
  for (const [path, entry] of headBlobs) {
    const identity = canonicalRepositoryPathIdentity(path);
    if (identity.unsafe || !identity.folded.startsWith("vendor/")) continue;
    if (entry.mode === BLOB_MODE_SYMLINK) {
      verdict.fail(`vendor path '${sanitizeToken(path, 100)}' is a symlink`);
    } else if (entry.mode === BLOB_MODE_EXECUTABLE) {
      verdict.fail(`vendor path '${sanitizeToken(path, 100)}' is executable`);
    } else if (entry.mode !== BLOB_MODE_REGULAR) {
      verdict.fail(
        `vendor path '${sanitizeToken(path, 100)}' has mode ${sanitizeToken(entry.mode, 10)}`,
      );
    }
    if (!policy.vendor.allowedFiles.some(
      allowed => asciiCaseFold(allowed) === identity.folded,
    )) {
      verdict.fail(
        `vendor path '${sanitizeToken(path, 100)}' is outside the reviewed allowlist`,
      );
    }
  }

  const wanted = new Set(["package.json", "package-lock.json", ".gitattributes"]);
  if (validateArtifact) {
    for (const path of [...policy.vendor.allowedFiles, ...Object.keys(effectiveDigestPins(policy))]) {
      wanted.add(path);
    }
  }
  if (activationScope) {
    for (const path of Object.keys(policy.activation?.pins ?? {})) wanted.add(path);
    for (const path of policy.activation?.allowedFiles ?? []) wanted.add(path);
  }

  const contents = new Map();
  let totalBytes = 0;
  for (const path of wanted) {
    const pathIdentity = canonicalRepositoryPathIdentity(path);
    const entry = pathIdentity.unsafe ? undefined : headBlobs.get(pathIdentity.canonical);
    if (!entry) {
      if (
        (validateArtifact &&
          (effectiveDigestPins(policy)[path] || policy.vendor.allowedFiles.includes(path))) ||
        (activationScope && policy.activation?.pins?.[path])
      ) {
        verdict.fail(`required file '${sanitizeToken(path, 100)}' is missing from the candidate tree`);
      }
      continue;
    }
    if (typeof entry.size === "number" && entry.size > policy.limits.maxBlobBytes) {
      verdict.fail(`candidate file '${sanitizeToken(path, 100)}' exceeds the blob size limit`);
      continue;
    }
    let bytes;
    try {
      bytes = await readBlob(entry.sha, path);
    } catch (error) {
      verdict.fail(
        `could not read '${sanitizeToken(path, 80)}': ${sanitizeToken(error?.message, 60)}`,
      );
      continue;
    }
    if (bytes.length > policy.limits.maxBlobBytes) {
      verdict.fail(`candidate file '${sanitizeToken(path, 100)}' exceeds the blob size limit`);
      continue;
    }
    totalBytes += bytes.length;
    if (totalBytes > policy.limits.maxTotalBlobBytes) {
      verdict.fail("candidate inspection exceeded the total download limit");
      continue;
    }
    if (gitBlobId(bytes) !== entry.sha) {
      verdict.fail(
        `candidate file '${sanitizeToken(path, 100)}' did not match its Git object id`,
      );
      continue;
    }
    contents.set(pathIdentity.canonical, bytes);
  }

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
    checkGitattributes(
      verdict,
      policy,
      Buffer.from(contents.get(".gitattributes")).toString("utf8"),
    );
  }

  if (!validateArtifact) {
    const spec = policy.package.spec;
    const referenced =
      packageJson?.devDependencies?.[policy.package.name] === spec ||
      packageLock?.packages?.[policy.package.lockPath]?.resolved === spec;
    if (referenced) {
      verdict.fail(
        "package metadata references the reviewed artifact spec but the artifact bytes are absent",
      );
    }
    checkRace(verdict, {
      eventHeadSha,
      eventBaseSha,
      baseRef,
      currentHeadSha,
      currentBaseSha,
      currentBaseRef,
    });
    if (!verdict.failed) {
      verdict.note(
        verdict.mode === "policy-only"
          ? "policy-only change; no reviewed artifact exists in the immutable base tree"
          : "no reviewed artifact exists in the immutable base tree",
      );
    }
    return verdict;
  }

  for (const [path, pin] of Object.entries(effectiveDigestPins(policy))) {
    const bytes = contents.get(path);
    checkExactBytePin(verdict, path, bytes, pin, "pinned file", headBlobs.get(path));
  }
  if (activationScope) {
    for (const [path, pin] of Object.entries(policy.activation?.pins ?? {})) {
      const identity = canonicalRepositoryPathIdentity(path);
      checkExactBytePin(
        verdict,
        path,
        identity.unsafe ? undefined : contents.get(identity.canonical),
        pin,
        "activation file",
        identity.unsafe ? undefined : headBlobs.get(identity.canonical),
      );
    }
  }

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

  let tarEntries;
  try {
    tarEntries = parseCandidateTarball(contents.get(policy.package.artifactPath), policy);
  } catch (error) {
    verdict.fail(`candidate artifact rejected: ${sanitizeToken(error?.message, 120)}`);
  }
  const artifactBytes = contents.get(policy.package.artifactPath);
  if (artifactBytes && sha512Hex(artifactBytes) !== policy.package.tar.sha512) {
    verdict.fail("candidate artifact SHA-512 does not match base policy");
  }
  if (tarEntries) {
    if (tarEntries.length !== policy.package.tar.fileCount) {
      verdict.fail(
        `candidate artifact packs ${tarEntries.length} files, expected ${policy.package.tar.fileCount}`,
      );
    }
    checkPackedManifest(verdict, policy, tarEntries);
  }
  if (packageJson) checkArtifactPackageJson(verdict, policy, packageJson);
  if (packageLock) checkArtifactPackageLock(verdict, policy, packageLock);
  try {
    checkProvenance(
      verdict,
      policy,
      parseCandidateJson(contents.get(policy.package.provenancePath), "provenance.json", policy),
      tarEntries ?? [],
    );
  } catch (error) {
    verdict.fail(`provenance.json rejected: ${sanitizeToken(error?.message, 100)}`);
  }

  checkRace(verdict, {
    eventHeadSha,
    eventBaseSha,
    baseRef,
    currentHeadSha,
    currentBaseSha,
    currentBaseRef,
  });
  if (!verdict.failed) {
    verdict.note(
      `validated ${sanitizeToken(eventHeadSha.slice(0, 12), 12)} against immutable base ${sanitizeToken(eventBaseSha.slice(0, 12), 12)}`,
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
  if (apiUrl !== "https://api.github.com") {
    throw new Error("GitHub API origin must be exactly https://api.github.com");
  }
  const base = `https://api.github.com/repos/${owner}/${repo}`;
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
      const files = [];
      for (let page = 1; page <= 10; page += 1) {
        const batch = await get(`/pulls/${pullNumber}/files`, { per_page: 100, page });
        if (!Array.isArray(batch)) throw new Error("unexpected pull files payload");
        for (const file of batch) {
          files.push({
            status: String(file?.status ?? ""),
            filename: typeof file?.filename === "string" ? file.filename : null,
            ...(typeof file?.previous_filename === "string"
              ? { previous_filename: file.previous_filename }
              : {}),
          });
        }
        if (batch.length < 100) return { files, truncated: false };
        if (files.length > maxFiles) return { files, truncated: true };
      }
      return { files, truncated: true };
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
    async readPull(pullNumber) {
      const pull = await get(`/pulls/${pullNumber}`);
      return {
        headSha: String(pull?.head?.sha ?? ""),
        baseSha: String(pull?.base?.sha ?? ""),
        baseRef: String(pull?.base?.ref ?? ""),
      };
    },
  };
}

export async function main() {
  const repoRoot = process.env.GATE_REPO_ROOT || defaultRepoRoot;
  const policy = loadPolicy(repoRoot);
  let verdict;
  try {
    const coordinates = requireEnv("GATE_REPOSITORY").split("/");
    if (coordinates.length !== 2) {
      throw new Error("repository coordinates failed validation");
    }
    const [owner, repo] = coordinates;
    const pullNumber = Number(requireEnv("GATE_PR_NUMBER"));
    if (!Number.isSafeInteger(pullNumber) || pullNumber <= 0) {
      throw new Error("pull request number failed validation");
    }
    const eventHeadSha = requireEnv("GATE_HEAD_SHA");
    const eventBaseSha = requireEnv("GATE_BASE_SHA");
    const baseRef = requireEnv("GATE_BASE_REF");
    const defaultBranch = process.env.GATE_DEFAULT_BRANCH || policy.defaultBranch;

    if (
      process.env.GITHUB_API_URL &&
      process.env.GITHUB_API_URL.replace(/\/+$/, "") !== "https://api.github.com"
    ) {
      throw new Error("ambient GITHUB_API_URL override is not permitted");
    }
    if (
      process.env.GITHUB_SERVER_URL &&
      process.env.GITHUB_SERVER_URL.replace(/\/+$/, "") !== "https://github.com"
    ) {
      throw new Error("ambient GITHUB_SERVER_URL override is not permitted");
    }
    const reader = createGitHubReader({
      apiUrl: "https://api.github.com",
      owner,
      repo,
      token: process.env.GATE_TOKEN,
    });

    const before = await reader.readPull(pullNumber);
    if (
      before.headSha !== eventHeadSha ||
      before.baseSha !== eventBaseSha ||
      before.baseRef !== baseRef
    ) {
      throw new Error("pull request changed before immutable evaluation began");
    }
    const changed = await reader.listChangedFiles(pullNumber, policy.limits.maxChangedFiles);
    const [baseTree, tree] = await Promise.all([
      reader.readTree(eventBaseSha),
      reader.readTree(eventHeadSha),
    ]);
    const after = await reader.readPull(pullNumber);

    verdict = await evaluateCandidate({
      policy,
      baseRef,
      defaultBranch,
      eventHeadSha,
      eventBaseSha,
      currentHeadSha: after.headSha,
      currentBaseSha: after.baseSha,
      currentBaseRef: after.baseRef,
      changedFiles: changed.files,
      changedFilesTruncated: changed.truncated,
      baseTreeEntries: baseTree.entries,
      baseTreeTruncated: baseTree.truncated,
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
