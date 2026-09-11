import { describe, expect, it } from "vitest";
import { activationPatchDigest, assertPolicyShape, loadPolicy } from "../../scripts/trusted/verify-dependency-artifact-gate.mjs";
import { git, readGitIndex, repoRoot } from "./_gitTreeFixtures.mjs";

const policy = loadPolicy(repoRoot);
const index = new Map(readGitIndex().map(entry => [entry.path, entry]));
describe("policy-stage activation assets", () => {
  it("retains the v3 exact-pins schema and two-file activation transaction", () => {
    expect(() => assertPolicyShape(policy)).not.toThrow();
    expect(policy.policyVersion).toBe(3);
    expect(policy.activation.validationMode).toBe("exact-pins");
    expect(policy.activation.allowedFiles).toEqual([
      "package-lock.json",
      "tests/spa/fast-uri-security.test.mjs",
    ]);
    expect(activationPatchDigest(policy.activation)).toBe(policy.activation.patchSha256);
    expect(policy.activation.allowedFiles.filter(path => policy.trustedPaths.includes(path))).toEqual([]);
  });

  it("matches the checked-out branch to one complete exact activation state", () => {
    const matchingStates = [
      policy.activation.basePins,
      policy.activation.pins,
    ].filter(pins =>
      policy.activation.allowedFiles.every(path => {
        const entry = index.get(path);
        const pin = pins[path];
        return pin.absent === true
          ? entry === undefined
          : entry?.type === "blob" &&
              entry.mode === pin.mode &&
              entry.sha === pin.blob;
      }),
    );

    expect(matchingStates).toHaveLength(1);
  });
});

const targetObjectsAvailable = Object.values(policy.activation.pins).every(pin => {
  try {
    git("cat-file", "-e", `${pin.blob}^{blob}`);
    return true;
  } catch {
    return false;
  }
});

// A policy-only fresh clone may not have the future activation objects. The
// activation branch always has them; a local object replay remains opt-in.
if (targetObjectsAvailable || process.env.TRUSTED_GATE_VALIDATE_PLANNED_BLOBS === "1") {
  await import("../../.github/trusted-policy/trusted-gate-artifact-acceptance.template.mjs");
}
