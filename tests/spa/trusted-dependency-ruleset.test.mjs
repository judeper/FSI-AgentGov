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
  assertFreshEvaluatorCheck,
  assertLegacyBaseline,
  assertOwnerIdentity,
  assertProbeResults,
  assertSafeRollbackTarget,
  assertSpoofedSourceRejected,
  assertUnrelatedSecurityStatePreserved,
  digestSecuritySnapshot,
  encodeEvaluatorExternalId,
  getPolicyEvidence,
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
const BASE_SHA = "c".repeat(40);
const POLICY_DIGEST = "d".repeat(64);
const RULESET_CREATED_AT = "2026-09-05T03:47:10Z";
const OBSERVED_AT = "2026-09-05T03:48:00Z";
const EVALUATOR_ORIGIN = "https://trusted-evaluator.example";
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
    allow_merge_commit: true,
    allow_squash_merge: true,
    allow_rebase_merge: true,
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
    required_pull_request_reviews: null,
    restrictions: null,
    required_linear_history: { enabled: false },
    required_signatures: { enabled: false },
    allow_force_pushes: { enabled: false },
    allow_deletions: { enabled: false },
    required_conversation_resolution: { enabled: false },
  };
}

function pullAssociation(number, headSha, baseSha = BASE_SHA) {
  return {
    number,
    head: {
      sha: headSha,
      repo: { full_name: "judeper/FSI-AgentGov" },
    },
    base: {
      sha: baseSha,
      repo: { full_name: "judeper/FSI-AgentGov" },
    },
  };
}

function evaluatorExternalId({
  nonce,
  pullNumber,
  headSha,
  baseSha = BASE_SHA,
  mode,
  issuedAt = "2026-09-05T03:47:20Z",
  overrides = {},
}) {
  return encodeEvaluatorExternalId({
    nonce,
    repository: "judeper/FSI-AgentGov",
    pull_request: pullNumber,
    head_sha: headSha,
    base_sha: baseSha,
    policy_digest: POLICY_DIGEST,
    policy_version: 2,
    mode,
    issued_at: issuedAt,
    ...overrides,
  });
}

function evaluatorRun({
  id,
  pullNumber,
  headSha,
  mode,
  conclusion,
  nonce,
  baseSha = BASE_SHA,
  issuedAt = "2026-09-05T03:47:20Z",
  startedAt = "2026-09-05T03:47:21Z",
  completedAt = "2026-09-05T03:47:30Z",
}) {
  return {
    id,
    name: "trusted-dependency-artifact",
    head_sha: headSha,
    app: { id: APP_ID, slug: "trusted-artifact-app" },
    status: "completed",
    conclusion,
    details_url: `${EVALUATOR_ORIGIN}/runs/${id}`,
    external_id: evaluatorExternalId({
      nonce,
      pullNumber,
      headSha,
      baseSha,
      mode,
      issuedAt,
    }),
    started_at: startedAt,
    completed_at: completedAt,
    pull_requests: [pullAssociation(pullNumber, headSha, baseSha)],
  };
}

function actionsRun({
  id,
  pullNumber,
  headSha,
  baseSha = BASE_SHA,
  startedAt = "2026-09-05T03:47:22Z",
  completedAt = "2026-09-05T03:47:31Z",
}) {
  return {
    id,
    name: "trusted-dependency-artifact",
    head_sha: headSha,
    app: { id: 15368, slug: "github-actions" },
    status: "completed",
    conclusion: "success",
    started_at: startedAt,
    completed_at: completedAt,
    pull_requests: [pullAssociation(pullNumber, headSha, baseSha)],
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
    const contract = loadAppContract();
    expect(() => assertAppContract(contract)).not.toThrow();
    expect(contract.apiOrigins).toEqual({
      rest: "https://api.github.com",
      web: "https://github.com",
      rejectAmbientOverrides: true,
    });

    expect(contract.evaluator).toMatchObject({
      deployment: "independently-reviewed-external-service",
      mustBeDeployedBeforeApply: true,
      signedWebhookRequired: true,
      probeControlPlane: "authenticated-out-of-band-owner-trigger",
      externalId: {
        prefix: "tdag.v1.",
        policyDigestAlgorithm: "sha256(canonical-json)",
        requireExactOperatorChallenge: true,
      },
    });
    expect(contract.installationVerification).toMatchObject({
      enumerateRepositoriesEndpoint: "GET /installation/repositories",
      requirePagination: true,
      requireRevocation: true,
    });
  });

  it("binds evaluator evidence to a canonical policy digest independent of line endings", () => {
    const evidence = getPolicyEvidence(
      join(repoRoot, ".github", "trusted-policy", "dependency-artifact-policy.json"),
    );
    expect(evidence).toMatchObject({ version: 2 });
    expect(evidence.digest).toMatch(/^[0-9a-f]{64}$/);
  });

  it("keeps owner and App credentials distinct and rejects permission drift", () => {
    const contract = loadAppContract();
    const app = { id: APP_ID, slug: "trusted-artifact-app" };
    const installation = {
      id: 777,
      app_id: APP_ID,
      account: { login: "judeper" },
      target_type: "User",
      repository_selection: "selected",
      permissions: { metadata: "read", contents: "read", pull_requests: "read", checks: "write" },
      events: ["pull_request", "check_suite", "check_run"],
    };
    const installations = [installation];
    const repositories = [{ full_name: "judeper/FSI-AgentGov" }];
    const tokenPermissions = { ...installation.permissions };
    expect(() =>
      assertOwnerIdentity({
        login: "judeper",
        repository: { permissions: { admin: true } },
      }),
    ).not.toThrow();
    expect(() =>
      assertAppInstallationPayload({
        app,
        installations,
        installation,
        repositories,
        tokenPermissions,
        contract,
        appId: APP_ID,
      }),
    ).not.toThrow();
    expect(() =>
      assertAppInstallationPayload({
        app,
        installations,
        installation: {
          ...installation,
          permissions: { ...installation.permissions, pull_requests: undefined },
        },
        repositories,
        tokenPermissions,
        contract,
        appId: APP_ID,
      }),
    ).toThrow(/permissions/);
    expect(() =>
      assertAppInstallationPayload({
        app: { id: APP_ID + 1, slug: "trusted-artifact-app" },
        installations,
        installation,
        repositories,
        tokenPermissions,
        contract,
        appId: APP_ID,
      }),
    ).toThrow(/App JWT identity/);
    expect(() =>
      assertAppInstallationPayload({
        app,
        installations,
        installation: {
          ...installation,
          permissions: { ...installation.permissions, administration: "write" },
        },
        repositories,
        tokenPermissions,
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

    expect(() =>
      assertAppInstallationPayload({
        app,
        installations: [
          installation,
          { ...installation, id: 778, account: { login: "other-owner" } },
        ],
        installation,
        repositories,
        tokenPermissions,
        contract,
        appId: APP_ID,
      }),
    ).toThrow(/unapproved installation/);
    expect(() =>
      assertAppInstallationPayload({
        app,
        installations,
        installation,
        repositories: [...repositories, { full_name: "judeper/other" }],
        tokenPermissions,
        contract,
        appId: APP_ID,
      }),
    ).toThrow(/repository selection/);
    expect(() =>
      assertAppInstallationPayload({
        app,
        installations,
        installation,
        repositories,
        tokenPermissions: { ...tokenPermissions, administration: "write" },
        contract,
        appId: APP_ID,
      }),
    ).toThrow(/token permissions/);
  });

  it("treats a JWT endpoint 401 fixture as a hard provisioning failure", () => {
    const contract = loadAppContract();
    expect(() =>
      assertAppInstallationPayload({
        app: null,
        installations: [],
        installation: null,
        repositories: [],
        tokenPermissions: {},
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
        mergeable: true,
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

  it("requires fresh post-creation positive App and negative Actions probes", () => {
    const positive = {
      pull: {
        number: 101,
        repository: "judeper/FSI-AgentGov",
        headSha: HEAD_SHA,
        baseSha: BASE_SHA,
        mergeable: true,
        mergeable_state: "clean",
      },
      checkRuns: [
        evaluatorRun({
          id: 1001,
          pullNumber: 101,
          headSha: HEAD_SHA,
          mode: "not-applicable",
          conclusion: "success",
          nonce: "1".repeat(64),
        }),
      ],
    };
    const negative = {
      pull: {
        number: 102,
        repository: "judeper/FSI-AgentGov",
        headSha: MERGE_SHA,
        baseSha: BASE_SHA,
        mergeable: true,
        mergeable_state: "blocked",
      },
      checkRuns: [
        evaluatorRun({
          id: 1002,
          pullNumber: 102,
          headSha: MERGE_SHA,
          mode: "activation-rejected",
          conclusion: "failure",
          nonce: "2".repeat(64),
        }),
        actionsRun({ id: 1003, pullNumber: 102, headSha: MERGE_SHA }),
      ],
    };
    expect(() =>
      assertProbeResults({
        positive,
        negative,
        appId: APP_ID,
        checkName: "trusted-dependency-artifact",
        policyDigest: POLICY_DIGEST,
        policyVersion: 2,
        positiveNonce: "1".repeat(64),
        negativeNonce: "2".repeat(64),
        evaluatorOrigin: EVALUATOR_ORIGIN,
        rulesetCreatedAt: RULESET_CREATED_AT,
        observedAt: OBSERVED_AT,
      }),
    ).not.toThrow();
    expect(() =>
      assertProbeResults({
        positive,
        negative: {},
        appId: APP_ID,
        checkName: "trusted-dependency-artifact",
        policyDigest: POLICY_DIGEST,
        policyVersion: 2,
        positiveNonce: "1".repeat(64),
        negativeNonce: "2".repeat(64),
        evaluatorOrigin: EVALUATOR_ORIGIN,
        rulesetCreatedAt: RULESET_CREATED_AT,
        observedAt: OBSERVED_AT,
      }),
    ).toThrow(/both positive App and negative spoof/);
  });

  it("rejects stale, pre-ruleset, unassociated, or incorrectly bound evaluator checks", () => {
    const baseline = evaluatorRun({
      id: 2001,
      pullNumber: 101,
      headSha: HEAD_SHA,
      mode: "not-applicable",
      conclusion: "success",
      nonce: "3".repeat(64),
    });
    const argumentsFor = checkRuns => ({
      checkRuns,
      targetSha: HEAD_SHA,
      baseSha: BASE_SHA,
      pullNumber: 101,
      appId: APP_ID,
      checkName: "trusted-dependency-artifact",
      policyDigest: POLICY_DIGEST,
      policyVersion: 2,
      expectedNonce: "3".repeat(64),
      evaluatorOrigin: EVALUATOR_ORIGIN,
      expectedMode: "not-applicable",
      expectedConclusion: "success",
      rulesetCreatedAt: RULESET_CREATED_AT,
      observedAt: OBSERVED_AT,
      maxAgeSeconds: 300,
    });
    expect(() => assertFreshEvaluatorCheck(argumentsFor([baseline]))).not.toThrow();

    const stale = {
      ...baseline,
      started_at: "2026-09-05T03:40:00Z",
      completed_at: "2026-09-05T03:40:10Z",
    };
    expect(() => assertFreshEvaluatorCheck(argumentsFor([stale]))).toThrow(/stale|precedes/);

    const unassociated = {
      ...baseline,
      pull_requests: [pullAssociation(999, HEAD_SHA)],
    };
    expect(() => assertFreshEvaluatorCheck(argumentsFor([unassociated]))).toThrow(/association/);

    const wrongBinding = {
      ...baseline,
      external_id: evaluatorExternalId({
        nonce: "4".repeat(64),
        pullNumber: 101,
        headSha: HEAD_SHA,
        mode: "artifact",
      }),
    };
    expect(() => assertFreshEvaluatorCheck(argumentsFor([wrongBinding]))).toThrow(/exact probe/);
  });

  it("rejects every mutated external_id binding field", () => {
    const mutations = [
      { nonce: "4".repeat(64) },
      { repository: "judeper/other" },
      { pull_request: 999 },
      { head_sha: "e".repeat(40) },
      { base_sha: "f".repeat(40) },
      { policy_digest: "0".repeat(64) },
      { policy_version: 3 },
      { mode: "artifact" },
      { issued_at: "2026-09-05T03:30:00Z" },
      { extra: "unreviewed" },
    ];
    for (const overrides of mutations) {
      const run = evaluatorRun({
        id: 2100,
        pullNumber: 101,
        headSha: HEAD_SHA,
        mode: "not-applicable",
        conclusion: "success",
        nonce: "3".repeat(64),
      });
      run.external_id = evaluatorExternalId({
        nonce: "3".repeat(64),
        pullNumber: 101,
        headSha: HEAD_SHA,
        mode: "not-applicable",
        overrides,
      });
      expect(() =>
        assertFreshEvaluatorCheck({
          checkRuns: [run],
          targetSha: HEAD_SHA,
          baseSha: BASE_SHA,
          pullNumber: 101,
          appId: APP_ID,
          checkName: "trusted-dependency-artifact",
          policyDigest: POLICY_DIGEST,
          policyVersion: 2,
          expectedNonce: "3".repeat(64),
          evaluatorOrigin: EVALUATOR_ORIGIN,
          expectedMode: "not-applicable",
          expectedConclusion: "success",
          rulesetCreatedAt: RULESET_CREATED_AT,
          observedAt: OBSERVED_AT,
          maxAgeSeconds: 300,
        }),
      ).toThrow(/exact probe|fields are not exact|stale|non-causal/);
    }

    const wrongOrigin = evaluatorRun({
      id: 2101,
      pullNumber: 101,
      headSha: HEAD_SHA,
      mode: "not-applicable",
      conclusion: "success",
      nonce: "3".repeat(64),
    });
    wrongOrigin.details_url = "https://github.com/judeper/FSI-AgentGov/actions/runs/1";
    expect(() =>
      assertFreshEvaluatorCheck({
        checkRuns: [wrongOrigin],
        targetSha: HEAD_SHA,
        baseSha: BASE_SHA,
        pullNumber: 101,
        appId: APP_ID,
        checkName: "trusted-dependency-artifact",
        policyDigest: POLICY_DIGEST,
        policyVersion: 2,
        expectedNonce: "3".repeat(64),
        evaluatorOrigin: EVALUATOR_ORIGIN,
        expectedMode: "not-applicable",
        expectedConclusion: "success",
        rulesetCreatedAt: RULESET_CREATED_AT,
        observedAt: OBSERVED_AT,
      }),
    ).toThrow(/reviewed evaluator origin/);
    expect(() =>
      assertFreshEvaluatorCheck({
        checkRuns: [
          evaluatorRun({
            id: 2102,
            pullNumber: 101,
            headSha: HEAD_SHA,
            mode: "not-applicable",
            conclusion: "success",
            nonce: "3".repeat(64),
          }),
        ],
        targetSha: HEAD_SHA,
        baseSha: BASE_SHA,
        pullNumber: 101,
        appId: APP_ID,
        checkName: "trusted-dependency-artifact",
        policyDigest: POLICY_DIGEST,
        policyVersion: 2,
        expectedNonce: "3".repeat(64),
        evaluatorOrigin: "https://github.com",
        expectedMode: "not-applicable",
        expectedConclusion: "success",
        rulesetCreatedAt: RULESET_CREATED_AT,
        observedAt: OBSERVED_AT,
      }),
    ).toThrow(/external HTTPS origin/);
  });

  it("rejects nonce reuse and stale or unassociated same-name Actions evidence", () => {
    const positive = {
      pull: {
        number: 101,
        repository: "judeper/FSI-AgentGov",
        headSha: HEAD_SHA,
        baseSha: BASE_SHA,
        mergeable: true,
        mergeable_state: "clean",
      },
      checkRuns: [
        evaluatorRun({
          id: 3001,
          pullNumber: 101,
          headSha: HEAD_SHA,
          mode: "not-applicable",
          conclusion: "success",
          nonce: "5".repeat(64),
        }),
      ],
    };
    const negativeEvaluator = evaluatorRun({
      id: 3002,
      pullNumber: 102,
      headSha: MERGE_SHA,
      mode: "activation-rejected",
      conclusion: "failure",
      nonce: "5".repeat(64),
    });
    const negative = {
      pull: {
        number: 102,
        repository: "judeper/FSI-AgentGov",
        headSha: MERGE_SHA,
        baseSha: BASE_SHA,
        mergeable: true,
        mergeable_state: "blocked",
      },
      checkRuns: [
        negativeEvaluator,
        actionsRun({ id: 3003, pullNumber: 102, headSha: MERGE_SHA }),
      ],
    };
    const args = {
      positive,
      negative,
      appId: APP_ID,
      checkName: "trusted-dependency-artifact",
      policyDigest: POLICY_DIGEST,
      policyVersion: 2,
      positiveNonce: "5".repeat(64),
      negativeNonce: "5".repeat(64),
      evaluatorOrigin: EVALUATOR_ORIGIN,
      rulesetCreatedAt: RULESET_CREATED_AT,
      observedAt: OBSERVED_AT,
    };
    expect(() => assertProbeResults(args)).toThrow(/distinct fresh operator nonces/);

    negative.checkRuns[0] = {
      ...negativeEvaluator,
      external_id: evaluatorExternalId({
        nonce: "6".repeat(64),
        pullNumber: 102,
        headSha: MERGE_SHA,
        mode: "activation-rejected",
      }),
    };
    args.negativeNonce = "6".repeat(64);
    negative.checkRuns[1] = {
      ...negative.checkRuns[1],
      started_at: "2026-09-05T03:40:00Z",
      completed_at: "2026-09-05T03:40:10Z",
    };
    expect(() => assertProbeResults(args)).toThrow(/fresh associated GitHub Actions/);

    negative.checkRuns[1] = {
      ...actionsRun({ id: 3004, pullNumber: 102, headSha: MERGE_SHA }),
      pull_requests: [pullAssociation(999, MERGE_SHA)],
    };
    expect(() => assertProbeResults(args)).toThrow(/fresh associated GitHub Actions/);
  });
});

describe("ruleset planner and read-back", () => {
  it("validates the owner-authenticated legacy baseline before any create", () => {
    expect(
      assertLegacyBaseline({
        plan,
        repository: repository(),
        branchProtection: legacyProtection(),
      }),
    ).toEqual({
      observedAt: "2026-09-05T03:47:06Z",
      requiredChecks: 13,
      additiveOnly: true,
    });
  });

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

  it("fails invented legacy review, signature, restriction, or merge-method state", () => {
    for (const mutate of [
      protection => {
        protection.required_pull_request_reviews = {
          required_approving_review_count: 1,
        };
      },
      protection => {
        protection.required_signatures.enabled = true;
      },
      protection => {
        protection.restrictions = { users: [], teams: [], apps: [] };
      },
    ]) {
      const protection = legacyProtection();
      mutate(protection);
      expect(() =>
        assertRulesetReadBack({
          plan,
          appId: APP_ID,
          repository: repository(),
          ruleset: managedRuleset(),
          branchProtection: protection,
        }),
      ).toThrow(/owner-authenticated snapshot/);
    }
    expect(() =>
      assertRulesetReadBack({
        plan,
        appId: APP_ID,
        repository: { ...repository(), allow_rebase_merge: false },
        ruleset: managedRuleset(),
        branchProtection: legacyProtection(),
      }),
    ).toThrow(/merge-method state/);
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

  it("preserves the observed legacy protection and sibling rulesets", () => {
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
    const changedRepository = structuredClone(before);
    changedRepository.repository.allow_rebase_merge = false;
    expect(digestSecuritySnapshot(changedRepository)).not.toBe(
      digestSecuritySnapshot(before),
    );
    expect(securitySnapshot(before).branchProtection.required_signatures.enabled).toBe(false);
  });

  it("aborts if concurrent drift changes a restriction or review", () => {
    const before = {
      repository: repository(),
      branchProtection: legacyProtection(),
      rulesets: [],
    };
    const changed = structuredClone(before);
    changed.branchProtection.allow_force_pushes.enabled = true;
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
    expect(script).toContain("EvaluatorOrigin");
    expect(script).toContain("$validatedEvaluatorOrigin|$LiveDigest");
    expect(script.indexOf('"assert-legacy-baseline"')).toBeLessThan(
      script.indexOf('Method "POST" -Body $desired'),
    );
    expect(script).toContain("Invoke-SafeRollback");
    expect(script).toContain('Method "DELETE"');
    expect(script).toContain("SpoofProbePullRequest");
    expect(script).toContain("GITHUB_APP_PRIVATE_KEY_PATH");
    expect(script).toMatch(/"api",\r?\n\s+"--hostname", "github\.com"/);
    expect(script).toContain("ambient GITHUB_API_URL overrides are not permitted");
    expect(script).not.toMatch(/branches\/main\/protection.*Method\s+"PUT"/s);
    expect(script.indexOf('Method "POST" -Body $desired')).toBeLessThan(
      script.lastIndexOf("[void](Assert-PostReadBack"),
    );
  });

  it("uses JWT/App-installation credentials, paginates repositories, and revokes the token", () => {
    const script = readFileSync(
      join(repoRoot, "scripts", "trusted", "Invoke-TrustedDependencyArtifactRuleset.ps1"),
      "utf8",
    );
    expect(script).toContain('Invoke-AppJson -Endpoint "app" -BearerToken $Jwt');
    expect(script).toContain('-Endpoint "repos/$Repository/installation"');
    expect(script).toContain('app/installations/$([Int64]$installation.id)/access_tokens');
    expect(script).toContain('installation/repositories?per_page=100&page=$page');
    expect(script).toContain('-Endpoint "installation/token"');
    expect(script).toContain('-Method "DELETE"');
    expect(script).toContain('GITHUB_APP_PRIVATE_KEY_PATH');
    expect(script).toContain('throw "GitHub App $Method $Endpoint failed"');
    expect(script).toContain('$githubApiOrigin = "https://api.github.com"');
    expect(script).toContain('$githubWebOrigin = "https://github.com"');
    expect(script).toContain("Get-ValidatedEvaluatorOrigin");
    expect(script).not.toMatch(/\$apiUrl\s*=\s*\[string\]\(\$env:GITHUB_API_URL\)/);
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
