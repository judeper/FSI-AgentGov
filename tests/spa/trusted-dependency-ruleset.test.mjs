import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import {
  assertExpectedSourceCheck,
  assertRulesetPlan,
  assertRulesetReadBack,
  assertUnrelatedSecurityStatePreserved,
  digestSecuritySnapshot,
  loadRulesetPlan,
  materializeRuleset,
  securitySnapshot,
} from "../../scripts/trusted/trusted-dependency-ruleset.mjs";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const plan = loadRulesetPlan();
const APP_ID = 8675309;
const HEAD_SHA = "a".repeat(40);
const MERGE_SHA = "b".repeat(40);

function repository() {
  return {
    id: 1117160053,
    full_name: "judeper/FSI-AgentGov",
    owner: { type: "User" },
    default_branch: "main",
  };
}

function managedRuleset() {
  return {
    id: 42,
    source_type: "Repository",
    source: "judeper/FSI-AgentGov",
    ...materializeRuleset(plan, APP_ID),
  };
}

function legacyProtection() {
  return {
    required_status_checks: {
      strict: true,
      checks: [{ context: "existing-ci", app_id: 1234 }],
    },
    enforce_admins: { enabled: true },
    required_pull_request_reviews: {
      dismiss_stale_reviews: true,
      require_code_owner_reviews: true,
      required_approving_review_count: 2,
      require_last_push_approval: true,
    },
    restrictions: {
      users: [{ login: "maintainer", id: 11 }],
      teams: [],
      apps: [],
    },
    required_linear_history: { enabled: true },
    required_signatures: { enabled: true },
    allow_force_pushes: { enabled: false },
    allow_deletions: { enabled: false },
    required_conversation_resolution: { enabled: true },
  };
}

describe("planned expected-source GitHub App ruleset", () => {
  it("is explicitly planned, source-bound, strict, and not a required-workflow claim", () => {
    expect(() => assertRulesetPlan(plan)).not.toThrow();
    expect(plan.state).toBe("planned-not-applied");
    expect(plan.requiredWorkflowBinding.status).toBe("unavailable-for-this-repository");

    const statusRule = plan.ruleset.rules.find(rule => rule.type === "required_status_checks");
    expect(statusRule.parameters.strict_required_status_checks_policy).toBe(true);
    expect(statusRule.parameters.required_status_checks).toEqual([
      {
        context: "trusted-dependency-artifact",
        integration_id: "${DEDICATED_GITHUB_APP_ID}",
      },
    ]);
    expect(plan.ruleset.rules.map(rule => rule.type)).not.toContain("workflows");
  });

  it("materializes an App ID only at owner apply time", () => {
    const desired = materializeRuleset(plan, APP_ID);
    const expected = desired.rules.find(rule => rule.type === "required_status_checks");
    expect(expected.parameters.required_status_checks).toEqual([
      { context: "trusted-dependency-artifact", integration_id: APP_ID },
    ]);
    expect(() => materializeRuleset(plan, 0)).toThrow(/App ID/);
  });

  it("does not allow a same-name GitHub Actions check on a PR head or test merge", () => {
    const spoofed = [
      {
        name: "trusted-dependency-artifact",
        head_sha: HEAD_SHA,
        app: { id: 15368, slug: "github-actions" },
        status: "completed",
        conclusion: "success",
      },
      {
        name: "trusted-dependency-artifact",
        head_sha: MERGE_SHA,
        app: { id: 15368, slug: "github-actions" },
        status: "completed",
        conclusion: "success",
      },
    ];
    expect(() =>
      assertExpectedSourceCheck({
        checkRuns: spoofed,
        targetSha: HEAD_SHA,
        appId: APP_ID,
        checkName: "trusted-dependency-artifact",
      }),
    ).toThrow(/expected GitHub App/);
    expect(() =>
      assertExpectedSourceCheck({
        checkRuns: spoofed,
        targetSha: MERGE_SHA,
        appId: APP_ID,
        checkName: "trusted-dependency-artifact",
      }),
    ).toThrow(/expected GitHub App/);
  });

  it("requires the expected App on the exact SHA GitHub is evaluating", () => {
    const runs = [
      {
        name: "trusted-dependency-artifact",
        head_sha: HEAD_SHA,
        app: { id: APP_ID },
        status: "completed",
        conclusion: "success",
      },
    ];
    expect(() =>
      assertExpectedSourceCheck({
        checkRuns: runs,
        targetSha: HEAD_SHA,
        appId: APP_ID,
        checkName: "trusted-dependency-artifact",
      }),
    ).not.toThrow();
    expect(() =>
      assertExpectedSourceCheck({
        checkRuns: runs,
        targetSha: MERGE_SHA,
        appId: APP_ID,
        checkName: "trusted-dependency-artifact",
      }),
    ).toThrow(/expected GitHub App/);
  });
});

describe("ruleset planner and read-back", () => {
  it("accepts only a complete matching read-back", () => {
    expect(() =>
      assertRulesetReadBack({
        plan,
        appId: APP_ID,
        repository: repository(),
        ruleset: managedRuleset(),
      }),
    ).not.toThrow();
  });

  it("fails a wrong repository or branch before reporting success", () => {
    expect(() =>
      assertRulesetReadBack({
        plan,
        appId: APP_ID,
        repository: { ...repository(), full_name: "other/repository" },
        ruleset: managedRuleset(),
      }),
    ).toThrow(/wrong repository/);
    expect(() =>
      assertRulesetReadBack({
        plan,
        appId: APP_ID,
        repository: { ...repository(), default_branch: "release" },
        ruleset: managedRuleset(),
      }),
    ).toThrow(/wrong repository/);
  });

  it("fails partial App-source or review protection read-back", () => {
    const sourceMismatch = managedRuleset();
    sourceMismatch.rules
      .find(rule => rule.type === "required_status_checks")
      .parameters.required_status_checks[0].integration_id = 999;
    expect(() =>
      assertRulesetReadBack({
        plan,
        appId: APP_ID,
        repository: repository(),
        ruleset: sourceMismatch,
      }),
    ).toThrow(/exactly match/);

    const missingCodeOwner = managedRuleset();
    delete missingCodeOwner.rules.find(rule => rule.type === "pull_request").parameters
      .require_code_owner_review;
    expect(() =>
      assertRulesetReadBack({
        plan,
        appId: APP_ID,
        repository: repository(),
        ruleset: missingCodeOwner,
      }),
    ).toThrow(/exactly match/);
  });

  it("fails a legacy protection state that excludes administrators", () => {
    const protection = legacyProtection();
    protection.enforce_admins.enabled = false;
    expect(() =>
      assertRulesetReadBack({
        plan,
        appId: APP_ID,
        repository: repository(),
        ruleset: managedRuleset(),
        branchProtection: protection,
      }),
    ).toThrow(/does not enforce administrators/);
  });

  it("preserves pre-existing reviews, restrictions, signatures, and sibling rulesets", () => {
    const sibling = {
      id: 8,
      name: "existing-governance",
      target: "branch",
      source_type: "Repository",
      source: "judeper/FSI-AgentGov",
      enforcement: "active",
      bypass_actors: [],
      conditions: { ref_name: { include: ["refs/heads/main"], exclude: [] } },
      rules: [{ type: "required_signatures" }],
    };
    const before = {
      repository: repository(),
      branchProtection: legacyProtection(),
      rulesets: [sibling],
    };
    const after = {
      repository: repository(),
      branchProtection: legacyProtection(),
      rulesets: [sibling, managedRuleset()],
    };
    expect(() =>
      assertUnrelatedSecurityStatePreserved({
        before,
        after,
        managedRulesetName: plan.managedRulesetName,
      }),
    ).not.toThrow();
    expect(digestSecuritySnapshot(before)).toBe(digestSecuritySnapshot(before));
    expect(securitySnapshot(before).branchProtection.required_signatures.enabled).toBe(true);
  });

  it("aborts if concurrent drift changes a restriction or review", () => {
    const before = {
      repository: repository(),
      branchProtection: legacyProtection(),
      rulesets: [],
    };
    const changed = structuredClone(before);
    changed.branchProtection.restrictions.users = [];
    changed.rulesets = [managedRuleset()];
    expect(() =>
      assertUnrelatedSecurityStatePreserved({
        before,
        after: changed,
        managedRulesetName: plan.managedRulesetName,
      }),
    ).toThrow(/drifted/);
  });

  it("uses create-only ruleset application, never a stale whole-document PUT", () => {
    const script = readFileSync(
      join(repoRoot, "scripts", "trusted", "Invoke-TrustedDependencyArtifactRuleset.ps1"),
      "utf8",
    );
    expect(script).toContain('Method "POST"');
    expect(script).not.toMatch(/-X\s+PUT|Method\s+"PUT"/);
    expect(script).toContain("ExpectedLiveDigest");
    expect(script).toContain("ExpectedIntendedRulesetDigest");
    expect(script).toContain("ConfirmationToken");
  });
});

describe("trusted-path ownership", () => {
  it("places the gate configuration and operator assets behind the final CODEOWNERS rules", () => {
    const owners = readFileSync(join(repoRoot, ".github", "CODEOWNERS"), "utf8");
    const genericWorkflow = owners.indexOf("/.github/workflows/");
    const trustedPolicy = owners.indexOf("/.github/trusted-policy/");
    expect(genericWorkflow).toBeGreaterThanOrEqual(0);
    expect(trustedPolicy).toBeGreaterThan(genericWorkflow);
    const lines = owners.split(/\r?\n/);
    for (const path of [
      "/.github/trusted-policy/",
      "/.github/TRUSTED-DEPENDENCY-GATE.md",
      "/SECURITY.md",
      "/scripts/trusted/",
      "/scripts/verify-required-checks.mjs",
    ]) {
      expect(
        lines.some(line => line.trimStart().startsWith(path) && line.trimEnd().endsWith("@judeper")),
        path,
      ).toBe(true);
    }
  });
});
