import { describe, expect, it } from "vitest";
import { createHash } from "node:crypto";
import { activationPatchDigest, assertPolicyShape, loadPolicy } from "../../scripts/trusted/verify-dependency-artifact-gate.mjs";
import { git, readGitIndex, repoRoot } from "./_gitTreeFixtures.mjs";

const policy = loadPolicy(repoRoot);
const index = new Map(readGitIndex().map(entry => [entry.path, entry]));
describe("policy-stage activation assets", () => {
  it("retains the complete current schema and 16-path activation transaction", () => {
    expect(() => assertPolicyShape(policy)).not.toThrow();
    expect(policy.activation.allowedFiles).toHaveLength(16);
    expect(activationPatchDigest(policy.activation)).toBe(policy.activation.patchSha256);
    expect(policy.activation.allowedFiles.filter(path => policy.trustedPaths.includes(path))).toEqual([]);
  });
  it.each([
    [".github/trusted-policy/trusted-gate-artifact-acceptance.template.mjs", "tests/spa/trusted-gate-artifact-acceptance.test.mjs"],
    [".github/trusted-policy/security-scan.activation.yml", ".github/workflows/security-scan.yml"],
  ])("preserves the canonical Git blob of %s for its later activation destination", (source, destination) => {
    const entry = index.get(source);
    const pin = policy.activation.pins[destination];
    expect(entry?.sha).toBe(pin.blob);
    expect(entry?.mode).toBe(pin.mode);
    const bytes = git("cat-file", "blob", entry.sha);
    expect(bytes.length).toBe(pin.size);
    expect(createHash("sha256").update(bytes).digest("hex")).toBe(pin.sha256);
  });
});

// A policy-only fresh clone intentionally has no artifact objects. The actual
// artifact branch always runs acceptance; a local reviewed-object replay is opt-in.
if (index.has(policy.package.artifactPath) || process.env.TRUSTED_GATE_VALIDATE_PLANNED_BLOBS === "1") {
  await import("../../.github/trusted-policy/trusted-gate-artifact-acceptance.template.mjs");
}
