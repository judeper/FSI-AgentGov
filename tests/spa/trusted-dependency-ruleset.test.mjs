import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { generateKeyPairSync } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import {
  assertExpectedSourceCheck,
  assertRulesetPlan,
  assertRulesetReadBack,
  assertAppContract,
  assertAppInstallationPayload,
  assertOwnerIdentity,
  assertProbeResults,
  assertSafeRollbackTarget,
  assertSpoofedSourceRejected,
  assertUnrelatedSecurityStatePreserved,
  digestSecuritySnapshot,
  loadAppContract,
  loadRulesetPlan,
  materializeRuleset,
  normalizeRulesetForSecurity,
  securitySnapshot,
} from "../../scripts/trusted/trusted-dependency-ruleset.mjs";
import { createGitHubAppJwt } from "../../scripts/trusted/github-app-jwt.mjs";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const plan = loadRulesetPlan();
const APP_ID = 8675309;
const HEAD_SHA = "a".repeat(40);
const MERGE_SHA = "b".repeat(40);
const LEGACY_CHECKS = [
  ["e2e-smoke", 15368],
  ["gitleaks", 15368],
  ["dependency-review", 15368],
  ["Analyze (python)", 15368],
  ["Analyze (javascript)", 15368],
  ["mkdocs-strict", 15368],
  ["verify_version_stamps", 15368],
  ["ruff", 15368],
  ["pytest (assessment + scripts)", 15368],
  ["manifest / index / nav drift", 15368],
  ["FSI language rules", 15368],
  ["autodoc-redirect-verify", 15368],
  ["autodoc-verify", 15368],
];

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
    name: "trusted-dependency-artifact-app-gate",
    target: "branch",
    enforcement: "active",
    bypass_actors: [],
    conditions: { ref_name: { include: ["refs/heads/main"], exclude: [] } },
    rules: [
      {
        type: "pull_request",
        parameters: {
          allowed_merge_methods: ["squash"],
          dismiss_stale_reviews_on_push: true,
          require_code_owner_review: true,
          require_last_push_approval: true,
          required_approving_review_count: 1,
          required_review_thread_resolution: true,
        },
      },
      {
        type: "required_status_checks",
        parameters: {
          do_not_enforce_on_create: false,
          strict_required_status_checks_policy: true,
          required_status_checks: [
            { context: "trusted-dependency-artifact", integration_id: APP_ID },
          ],
        },
      },
      { type: "non_fast_forward" },
      { type: "deletion" },
      { type: "required_linear_history" },
    ],
    node_id: "RRS_fixture",
    created_at: "2026-09-05T01:00:00Z",
    updated_at: "2026-09-05T01:00:00Z",
  };
}

function legacyProtection() {
  return {
    required_status_checks: {
      strict: true,
      contexts: LEGACY_CHECKS.map(([context]) => context),
      checks: LEGACY_CHECKS.map(([context, app_id]) => ({ context, app_id })),
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
  it("creates a short-lived RS256 App JWT without exposing key material", () => {
    const { privateKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });
    const token = createGitHubAppJwt({
      appId: APP_ID,
      privateKey: privateKey.export({ type: "pkcs8", format: "pem" }),
      nowSeconds: 1_788_570_000,
    });
    const [header, payload, signature] = token.split(".");
    expect(header).toBeTruthy();
    expect(signature).toBeTruthy();
    expect(JSON.parse(Buffer.from(payload, "base64url").toString("utf8"))).toEqual({
      iat: 1_788_569_940,
      exp: 1_788_570_540,
      iss: APP_ID,
    });
  });

  it("validates the exact least-privilege App contract", () => {
    expect(() => assertAppContract(loadAppContract())).not.toThrow();
  });

  it("keeps owner and App credentials distinct and rejects permission drift", () => {
    const contract = loadAppContract();
    const app = { id: APP_ID, slug: "trusted-artifact-app" };
    const installation = {
      app_id: APP_ID,
      account: { login: "judeper" },
      target_type: "User",
      repository_selection: "selected",
      permissions: { metadata: "read", contents: "read", pull_requests: "read", checks: "write" },
      events: ["pull_request", "check_suite", "check_run"],
      repositories: [{ full_name: "judeper/FSI-AgentGov" }],
    };
    expect(() =>
      assertOwnerIdentity({
        login: "judeper",
        repository: { permissions: { admin: true } },
      }),
    ).not.toThrow();
    expect(() =>
      assertAppInstallationPayload({ app, installation, contract, appId: APP_ID }),
    ).not.toThrow();
    expect(() =>
      assertAppInstallationPayload({
        app,
        installation: {
          ...installation,
          permissions: { ...installation.permissions, pull_requests: undefined },
        },
        contract,
        appId: APP_ID,
      }),
    ).toThrow(/permissions/);
    expect(() =>
      assertAppInstallationPayload({
        app: { id: APP_ID + 1, slug: "trusted-artifact-app" },
        installation,
        contract,
        appId: APP_ID,
      }),
    ).toThrow(/App JWT identity/);
    expect(() =>
      assertAppInstallationPayload({
        app,
        installation: {
          ...installation,
          permissions: { ...installation.permissions, administration: "write" },
        },
        contract,
        appId: APP_ID,
      }),
    ).toThrow(/permissions/);
    expect(() =>
      assertOwnerIdentity({
        login: "judep_microsoft",
        repository: { permissions: { admin: true } },
      }),
    ).toThrow(/owner credential/);
  });

  it("treats a JWT endpoint 401 fixture as a hard provisioning failure", () => {
    const contract = loadAppContract();
    expect(() =>
      assertAppInstallationPayload({
        app: null,
        installation: null,
        contract,
        appId: APP_ID,
      }),
    ).toThrow(/App JWT identity/);
  });

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

  it("requires a negative spoof probe to be blocked, not merely renamed", () => {
    const spoof = {
      name: "trusted-dependency-artifact",
      head_sha: HEAD_SHA,
      app: { id: 15368, slug: "github-actions" },
      status: "completed",
      conclusion: "success",
    };
    expect(() =>
      assertSpoofedSourceRejected({
        checkRuns: [spoof],
        targetSha: HEAD_SHA,
        appId: APP_ID,
        checkName: "trusted-dependency-artifact",
        mergeable: false,
        mergeableState: "blocked",
      }),
    ).not.toThrow();
    expect(() =>
      assertSpoofedSourceRejected({
        checkRuns: [spoof],
        targetSha: HEAD_SHA,
        appId: APP_ID,
        checkName: "trusted-dependency-artifact",
        mergeable: true,
        mergeableState: "clean",
      }),
    ).toThrow(/blocked/);
  });

  it("requires both positive App and negative spoof probes", () => {
    const positive = {
      pull: { headSha: HEAD_SHA, mergeable: true, mergeable_state: "clean" },
      checkRuns: [
        {
          name: "trusted-dependency-artifact",
          head_sha: HEAD_SHA,
          app: { id: APP_ID, slug: "trusted-artifact-app" },
          status: "completed",
          conclusion: "success",
        },
      ],
    };
    const negative = {
      pull: { headSha: MERGE_SHA, mergeable: false, mergeable_state: "blocked" },
      checkRuns: [
        {
          name: "trusted-dependency-artifact",
          head_sha: MERGE_SHA,
          app: { id: 15368, slug: "github-actions" },
          status: "completed",
          conclusion: "success",
        },
      ],
    };
    expect(() =>
      assertProbeResults({
        positive,
        negative,
        appId: APP_ID,
        checkName: "trusted-dependency-artifact",
      }),
    ).not.toThrow();
    expect(() =>
      assertProbeResults({
        positive,
        negative: {},
        appId: APP_ID,
        checkName: "trusted-dependency-artifact",
      }),
    ).toThrow(/both positive App and negative spoof/);
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
        branchProtection: legacyProtection(),
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

  it("fails read-back when active legacy protection is missing instead of treating 404 as absence", () => {
    expect(() =>
      assertRulesetReadBack({
        plan,
        appId: APP_ID,
        repository: repository(),
        ruleset: managedRuleset(),
        branchProtection: null,
      }),
    ).toThrow(/legacy branch protection is missing/);
  });

  it("accepts realistic server-added defaults without weakening security comparison", () => {
    const response = {
      ...managedRuleset(),
      current_user_can_bypass: false,
      node_id: "RRS_server",
      url: "https://api.github.com/repos/judeper/FSI-AgentGov/rulesets/42",
      _links: { self: { href: "https://api.github.com/" } },
      rules: managedRuleset().rules.map(rule => ({
        ...rule,
        ...(rule.type === "non_fast_forward" ? { parameters: {} } : {}),
      })),
    };
    expect(normalizeRulesetForSecurity(response)).toEqual(
      normalizeRulesetForSecurity({
        ...managedRuleset(),
        source_type: "Repository",
        source: "judeper/FSI-AgentGov",
      }),
    );
    expect(() =>
      assertRulesetReadBack({
        plan,
        appId: APP_ID,
        repository: repository(),
        ruleset: response,
        branchProtection: legacyProtection(),
      }),
    ).not.toThrow();
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
    expect(script).toContain("Invoke-SafeRollback");
    expect(script).toContain('Method "DELETE"');
    expect(script).toContain("SpoofProbePullRequest");
    expect(script).toContain("GITHUB_APP_PRIVATE_KEY_PATH");
    expect(script).not.toMatch(/branches\/main\/protection.*Method\s+"PUT"/s);
  });

  it("uses a JWT-only App identity probe and fails closed on App auth errors", () => {
    const script = readFileSync(
      join(repoRoot, "scripts", "trusted", "Invoke-TrustedDependencyArtifactRuleset.ps1"),
      "utf8",
    );
    expect(script).toContain('Invoke-AppJson -Endpoint "app" -Jwt $Jwt');
    expect(script).toContain('Invoke-AppJson -Endpoint "repos/$Repository/installation" -Jwt $Jwt');
    expect(script).toContain('GITHUB_APP_PRIVATE_KEY_PATH');
    expect(script).toContain('throw "GitHub App GET $Endpoint failed"');
    expect(script).not.toContain('repos/$Repository/installation" -AllowNotFound');
  });

  it("proves safe rollback is limited to the just-created ruleset", () => {
    const created = {
      ...managedRuleset(),
      created_at: "2026-09-05T01:00:00Z",
    };
    expect(() =>
      assertSafeRollbackTarget({
        beforeRulesetIds: [8],
        createdRuleset: created,
        readBackRuleset: created,
        history: [
          {
            actor: { id: 99, type: "User" },
            updated_at: "2026-09-05T01:00:01Z",
          },
        ],
        ownerId: 99,
        expectedRuleset: materializeRuleset(plan, APP_ID),
        startedAt: "2026-09-05T00:59:00Z",
        endedAt: "2026-09-05T01:01:00Z",
      }),
    ).not.toThrow();
    expect(() =>
      assertSafeRollbackTarget({
        beforeRulesetIds: [42],
        createdRuleset: created,
        readBackRuleset: created,
        history: [],
        ownerId: 99,
        expectedRuleset: materializeRuleset(plan, APP_ID),
        startedAt: "2026-09-05T00:59:00Z",
        endedAt: "2026-09-05T01:01:00Z",
      }),
    ).toThrow(/newly created/);
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
