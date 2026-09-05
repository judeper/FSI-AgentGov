import { describe, expect, it } from "vitest";
import { createHash } from "node:crypto";
import {
  activationPatchDigest,
  assertPolicyShape,
  diffImmutableTrees,
  evaluateCandidate,
  gitBlobId,
  loadPolicy,
} from "../../scripts/trusted/verify-dependency-artifact-gate.mjs";
import { git, githubTreeResponse, readGitIndex, repoRoot } from "../../tests/spa/_gitTreeFixtures.mjs";

const policy = loadPolicy(repoRoot);
const index = readGitIndex();
const indexed = new Map(index.map(entry => [entry.path, entry]));
const bytes = new Map();
const readBlob = async sha => {
  if (!bytes.has(sha)) bytes.set(sha, git("cat-file", "blob", sha));
  return bytes.get(sha);
};
const expectedPaths = [
  ".gitattributes",
  ".github/workflows/security-scan.yml",
  ".github/workflows/sri-check.yml",
  "package-lock.json",
  "package.json",
  "scripts/verify-fast-uri-artifact.mjs",
  "scripts/verify-fast-uri-bootstrap.mjs",
  "scripts/verify-vendored-runtime.mjs",
  "tests/spa/docs-safe-procedure.test.mjs",
  "tests/spa/fast-uri-artifact-race.test.mjs",
  "tests/spa/fast-uri-security-workflow.test.mjs",
  "tests/spa/trusted-gate-artifact-acceptance.test.mjs",
  "tests/spa/vendor-runtime-policy.test.mjs",
  "vendor/npm/fast-uri/3.1.7/README.md",
  "vendor/npm/fast-uri/3.1.7/fast-uri-3.1.7.tgz",
  "vendor/npm/fast-uri/3.1.7/provenance.json",
];

// Project the approved transaction from content-addressed blobs, never execute
// candidate files, and retain every unrelated/trusted path from the captured index.
function project(pins) {
  return [
    ...index.filter(entry => !expectedPaths.includes(entry.path)),
    ...expectedPaths.flatMap(path => pins[path].absent === true ? [] : [{
      path, mode: pins[path].mode, type: "blob", sha: pins[path].blob,
    }]),
  ];
}
const base = project(policy.activation.basePins);
const candidate = project(policy.activation.pins);
const headSha = git("rev-parse", "HEAD").toString("utf8").trim();
const judge = (before, after) => evaluateCandidate({
  policy, baseRef: "main", defaultBranch: "main",
  eventHeadSha: headSha, eventBaseSha: headSha,
  changedFiles: [], baseTreeEntries: before, treeEntries: after, readBlob,
});

describe("current policy contract and exact pinned activation", () => {
  it("uses the current policy schema, all 16 paths and no trusted overlap", () => {
    expect(() => assertPolicyShape(policy)).not.toThrow();
    expect(policy.policyVersion).toBe(2);
    expect(policy.activation.allowedFiles).toEqual(expectedPaths);
    expect(expectedPaths.filter(path => policy.trustedPaths.includes(path))).toEqual([]);
    expect(activationPatchDigest(policy.activation)).toBe(policy.activation.patchSha256);
    expect(diffImmutableTrees(base, candidate).changes.map(change => change.filename).sort()).toEqual(expectedPaths);
  });

  it("keeps the captured index in either the exact pre-activation or exact activated state", () => {
    const pins = indexed.has(policy.package.artifactPath) ? policy.activation.pins : policy.activation.basePins;
    for (const path of expectedPaths) {
      const entry = indexed.get(path);
      if (pins[path].absent) expect(entry, path).toBeUndefined();
      else expect(entry, path).toMatchObject({ type: "blob", mode: pins[path].mode, sha: pins[path].blob });
    }
  });

  it("pins the replacement acceptance test to this tracked template, not a removed export", async () => {
    const source = indexed.get(".github/trusted-policy/trusted-gate-artifact-acceptance.template.mjs");
    expect(source?.sha).toBe(policy.activation.pins["tests/spa/trusted-gate-artifact-acceptance.test.mjs"].blob);
    expect((await readBlob(source.sha)).toString("utf8")).not.toMatch(/\bartifactRequiredByBase\b/);
  });

  for (const path of expectedPaths) {
    it(`verifies the regular Git blob, raw-byte size and SHA-256 for ${path}`, async () => {
      const pin = policy.activation.pins[path];
      const content = await readBlob(pin.blob);
      expect(pin.mode).toBe("100644");
      expect(content.length).toBe(pin.size);
      expect(gitBlobId(content)).toBe(pin.blob);
      expect(createHash("sha256").update(content).digest("hex")).toBe(pin.sha256);
    });
  }

  it("accepts exact activation with real recursive-directory response shapes", async () => {
    const verdict = await judge(githubTreeResponse(base).tree, githubTreeResponse(candidate).tree);
    expect(verdict.toJSON(), verdict.messages.join("\n")).toMatchObject({ conclusion: "success", mode: "activation" });
  });

  it("accepts the same exact bytes after activation without a removed artifactRequired override", async () => {
    const verdict = await judge(candidate, candidate);
    expect(verdict.toJSON(), verdict.messages.join("\n")).toMatchObject({ conclusion: "success", mode: "artifact" });
  });

  it.each(expectedPaths)("rejects a partial activation consisting only of %s", async path => {
    const partial = [...base.filter(entry => entry.path !== path), candidate.find(entry => entry.path === path)];
    expect((await judge(base, partial)).failed, path).toBe(true);
  });

  it.each(expectedPaths)("rejects post-activation mode replacement at %s on either immutable side", async path => {
    for (const mode of ["120000", "160000", "100755", "100600"]) {
      const replacement = candidate.map(entry => entry.path !== path ? entry :
        { ...entry, mode, type: mode === "160000" ? "commit" : "blob" });
      expect((await judge(candidate, replacement)).failed, `${path}:candidate:${mode}`).toBe(true);
      expect((await judge(replacement, candidate)).failed, `${path}:base:${mode}`).toBe(true);
    }
  });
});
