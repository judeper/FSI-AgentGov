/*
 * Pure model for the planned, expected-source GitHub App ruleset.
 *
 * This module does not call GitHub. The PowerShell operator script owns remote
 * reads and the one explicit create operation plus an identity-checked rollback
 * delete; keeping this model pure makes the plan, digest, read-back, and
 * spoofing tests deterministic.
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { assertPolicyShape } from "./verify-dependency-artifact-gate.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "..", "..");
export const RULESET_PLAN_FILE = join(
  repoRoot,
  ".github",
  "trusted-policy",
  "trusted-dependency-artifact-ruleset.plan.json",
);
export const APP_CONTRACT_FILE = join(
  repoRoot,
  ".github",
  "trusted-policy",
  "trusted-dependency-artifact-app-contract.json",
);

const FULL_OBJECT_ID = /^[0-9a-f]{40}$/;
const APP_ID = /^[1-9][0-9]*$/;
const ISO_TIMESTAMP = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/;
const SHA256 = /^[0-9a-f]{64}$/;
const EXTERNAL_ID_PREFIX = "tdag.v1.";
const CHECK_ASSOCIATION_REPOSITORY = "judeper/FSI-AgentGov";

function clone(value) {
  return structuredClone(value);
}

function sortObject(value) {
  if (Array.isArray(value)) return value.map(sortObject);
  if (!value || typeof value !== "object") return value;
  return Object.fromEntries(
    Object.keys(value)
      .sort()
      .map(key => [key, sortObject(value[key])]),
  );
}

export function canonicalJson(value) {
  return JSON.stringify(sortObject(value));
}

export function sha256Hex(value) {
  return createHash("sha256").update(value).digest("hex");
}

export function digestJson(value) {
  return sha256Hex(canonicalJson(value));
}

export function loadRulesetPlan(file = RULESET_PLAN_FILE) {
  const plan = JSON.parse(readFileSync(file, "utf8"));
  assertRulesetPlan(plan);
  return plan;
}

export function loadAppContract(file = APP_CONTRACT_FILE) {
  const contract = JSON.parse(readFileSync(file, "utf8"));
  assertAppContract(contract);
  return contract;
}

export function getPolicyEvidence(file) {
  const policy = JSON.parse(readFileSync(file, "utf8"));
  assertPolicyShape(policy);
  return {
    digest: digestJson(policy),
    version: policy.policyVersion,
  };
}

export function assertAppContract(contract) {
  if (!contract || typeof contract !== "object") {
    throw new Error("GitHub App contract is not an object");
  }
  if (contract.schemaVersion !== 3) {
    throw new Error("GitHub App contract schema version is unsupported");
  }
  if (
    contract.repository !== "judeper/FSI-AgentGov" ||
    contract.checkName !== "trusted-dependency-artifact"
  ) {
    throw new Error("GitHub App contract is bound to the wrong repository or check");
  }
  if (
    contract.apiOrigins?.rest !== "https://api.github.com" ||
    contract.apiOrigins?.web !== "https://github.com" ||
    contract.apiOrigins?.rejectAmbientOverrides !== true
  ) {
    throw new Error("GitHub App contract API origins are not pinned");
  }
  const expectedPermissions = {
    metadata: "read",
    contents: "read",
    pull_requests: "read",
    checks: "write",
  };
  if (canonicalJson(contract.minimumPermissions) !== canonicalJson(expectedPermissions)) {
    throw new Error("GitHub App contract minimum permissions drifted");
  }
  if (
    canonicalJson(contract.allowedRepositoryPermissions) !==
    canonicalJson(expectedPermissions)
  ) {
    throw new Error("GitHub App contract allowed permissions drifted");
  }
  if (
    canonicalJson(contract.requiredWebhookEvents) !==
      canonicalJson(["pull_request", "check_suite", "check_run"]) ||
    contract.rejectUnapprovedPermissions !== true ||
    contract.rejectUnapprovedWebhookEvents !== true
  ) {
    throw new Error("GitHub App contract webhook or least-privilege policy drifted");
  }
  if (
    contract.installationVerification?.requireOnlyAppInstallation !== true ||
    contract.installationVerification?.createTokenEndpoint !==
      "POST /app/installations/{installation_id}/access_tokens" ||
    contract.installationVerification?.enumerateRepositoriesEndpoint !==
      "GET /installation/repositories" ||
    contract.installationVerification?.revokeTokenEndpoint !==
      "DELETE /installation/token" ||
    contract.installationVerification?.requirePagination !== true ||
    contract.installationVerification?.requireRevocation !== true ||
    contract.installationVerification?.maxTokenLifetimeSeconds !== 3600
  ) {
    throw new Error("GitHub App installation-token verification contract drifted");
  }
  if (
    contract.mergeQueue?.enabledByThisPlan !== false ||
    contract.mergeQueue?.permission !== "merge_queues" ||
    canonicalJson(contract.mergeQueue?.events) !== canonicalJson(["merge_group"])
  ) {
    throw new Error("GitHub App contract merge-queue contract drifted");
  }
  if (
    contract.webhookSecurity?.signatureHeader !== "X-Hub-Signature-256" ||
    contract.webhookSecurity?.algorithm !== "HMAC-SHA256" ||
    contract.webhookSecurity?.deliveryHeader !== "X-GitHub-Delivery" ||
    contract.webhookSecurity?.timestampSource !==
      "trusted receiver clock at receipt; GitHub supplies no signed timestamp header" ||
    contract.webhookSecurity?.maxReplaySeconds !== 300 ||
    contract.webhookSecurity?.requireDeliveryDeduplication !== true ||
    contract.webhookSecurity?.requireRepositoryAndInstallationMatch !== true ||
    contract.webhookSecurity?.requireSignatureBeforeEvaluation !== true
  ) {
    throw new Error("GitHub App webhook replay and signature contract drifted");
  }
  const externalId = contract.evaluator?.externalId;
  if (
    contract.evaluator?.deployment !== "independently-reviewed-external-service" ||
    contract.evaluator?.mustBeDeployedBeforeApply !== true ||
    contract.evaluator?.candidateCodeExecutionForbidden !== true ||
    contract.evaluator?.signedWebhookRequired !== true ||
    contract.evaluator?.endpointSuppliedAtRuntime !== true ||
    contract.evaluator?.requireExternalDetailsUrlOrigin !== true ||
    externalId?.prefix !== EXTERNAL_ID_PREFIX ||
    externalId?.encoding !== "base64url(canonical-json)" ||
    externalId?.noncePattern !== "^[0-9a-f]{64}$" ||
    externalId?.policyDigestAlgorithm !== "sha256(canonical-json)" ||
    externalId?.probeNonceSource !==
      "operator-generated-256-bit-challenge-after-ruleset-read-back" ||
    externalId?.requireExactOperatorChallenge !== true ||
    canonicalJson(externalId?.requiredFields) !==
      canonicalJson([
        "nonce",
        "repository",
        "pull_request",
        "head_sha",
        "base_sha",
        "policy_digest",
        "policy_version",
        "mode",
        "issued_at",
      ]) ||
    externalId?.maxAgeSeconds !== 300 ||
    externalId?.requirePullRequestAssociation !== true ||
    externalId?.requireStartedAfterRulesetCreation !== true ||
    externalId?.requireCompletedAfterRulesetCreation !== true ||
    contract.evaluator?.probeControlPlane !==
      "authenticated-out-of-band-owner-trigger"
  ) {
    throw new Error("GitHub App evaluator deployment or external_id contract drifted");
  }
  return contract;
}

export function assertOwnerIdentity({
  login,
  repository,
  requiredLogin = "judeper",
}) {
  if (login !== requiredLogin) {
    throw new Error("owner credential does not authenticate as the repository owner");
  }
  if (repository?.permissions?.admin !== true) {
    throw new Error("owner credential lacks repository administration permission");
  }
  return true;
}

export function assertAppInstallationPayload({
  app,
  installations,
  installation,
  repositories,
  tokenPermissions,
  contract,
  appId,
  repository = "judeper/FSI-AgentGov",
}) {
  assertAppContract(contract);
  if (
    contract.installation?.account !== "judeper" ||
    contract.installation?.repository !== repository ||
    contract.installation?.selection !== "selected" ||
    contract.installation?.onlyRepository !== true
  ) {
    throw new Error("GitHub App contract installation scope drifted");
  }
  if (Number(app?.id) !== Number(appId) || app?.slug === "github-actions") {
    throw new Error("App JWT identity does not match the dedicated GitHub App");
  }
  if (
    Number(installation?.app_id) !== Number(appId) ||
    installation?.target_type !== "User" ||
    installation?.account?.login !== "judeper" ||
    installation?.repository_selection !== "selected" ||
    installation?.suspended_at != null
  ) {
    throw new Error("GitHub App installation is not scoped to the target repository");
  }
  if (
    !Array.isArray(installations) ||
    installations.length !== 1 ||
    Number(installations[0]?.id) !== Number(installation?.id) ||
    Number(installations[0]?.app_id) !== Number(appId) ||
    installations[0]?.target_type !== "User" ||
    installations[0]?.account?.login !== "judeper" ||
    installations[0]?.suspended_at != null
  ) {
    throw new Error("GitHub App has an unapproved installation");
  }
  const expected = { ...contract.allowedRepositoryPermissions };
  const expectedEvents = [...contract.requiredWebhookEvents];
  if (contract.mergeQueue?.enabledByThisPlan === true) {
    expected[contract.mergeQueue.permission] = "read";
    expectedEvents.push(...contract.mergeQueue.events);
  }
  const actual = installation.permissions ?? {};
  if (canonicalJson(actual) !== canonicalJson(expected)) {
    throw new Error("GitHub App installation permissions are missing or over-privileged");
  }
  if (canonicalJson(tokenPermissions ?? {}) !== canonicalJson(expected)) {
    throw new Error("GitHub App installation token permissions are missing or over-privileged");
  }
  if (
    canonicalJson([...(installation.events ?? [])].sort()) !==
    canonicalJson(expectedEvents.sort())
  ) {
    throw new Error("GitHub App installation webhook events are not exact");
  }
  if (
    !Array.isArray(repositories) ||
    repositories.length !== 1 ||
    repositories[0]?.full_name !== repository
  ) {
    throw new Error("GitHub App installation repository selection is not exact");
  }
  return true;
}

function findRule(plan, type) {
  const matches = plan.ruleset.rules.filter(rule => rule?.type === type);
  if (matches.length !== 1) {
    throw new Error(`ruleset plan must contain exactly one '${type}' rule`);
  }
  return matches[0];
}

export function assertRulesetPlan(plan) {
  if (!plan || typeof plan !== "object") throw new Error("ruleset plan is not an object");
  for (const key of [
    "schemaVersion",
    "state",
    "repository",
    "ownerType",
    "defaultBranch",
    "managedRulesetName",
    "applicationMode",
    "requiredWorkflowBinding",
    "expectedSource",
    "ruleset",
    "legacyBranchProtection",
    "mergeQueue",
    "preflight",
  ]) {
    if (!(key in plan)) throw new Error(`ruleset plan is missing '${key}'`);
  }
  if (
    plan.schemaVersion !== 2 ||
    plan.state !== "planned-not-applied" ||
    plan.applicationMode !== "create-only-additive"
  ) {
    throw new Error("ruleset plan must explicitly remain planned-not-applied");
  }
  if (plan.ownerType !== "User" || plan.repository !== "judeper/FSI-AgentGov") {
    throw new Error("ruleset plan is bound to the wrong repository owner");
  }
  if (plan.defaultBranch !== "main") throw new Error("ruleset plan must target main");
  if (
    plan.requiredWorkflowBinding?.status !== "unavailable-for-this-repository" ||
    plan.expectedSource?.kind !== "dedicated-github-app" ||
    plan.expectedSource?.appId !== "${DEDICATED_GITHUB_APP_ID}" ||
    plan.expectedSource?.rejectGitHubActions !== true
  ) {
    throw new Error("ruleset plan must require a dedicated GitHub App source");
  }
  if (
    plan.ruleset?.target !== "branch" ||
    plan.ruleset?.enforcement !== "active" ||
    !Array.isArray(plan.ruleset?.bypass_actors) ||
    plan.ruleset.bypass_actors.length !== 0
  ) {
    throw new Error("ruleset plan must enforce a no-bypass branch ruleset");
  }
  const refs = plan.ruleset?.conditions?.ref_name;
  if (
    !refs ||
    canonicalJson(refs.include) !== canonicalJson(["refs/heads/main"]) ||
    canonicalJson(refs.exclude) !== canonicalJson([])
  ) {
    throw new Error("ruleset plan must target only refs/heads/main");
  }

  const pullRequest = findRule(plan, "pull_request").parameters;
  const expectedReview = {
    allowed_merge_methods: ["squash"],
    dismiss_stale_reviews_on_push: true,
    require_code_owner_review: true,
    require_last_push_approval: true,
    required_approving_review_count: 1,
    required_review_thread_resolution: true,
  };
  if (canonicalJson(pullRequest) !== canonicalJson(expectedReview)) {
    throw new Error("ruleset plan pull-request protections drifted");
  }

  const statusChecks = findRule(plan, "required_status_checks").parameters;
  const expectedChecks = [
    {
      context: plan.expectedSource.checkName,
      integration_id: "${DEDICATED_GITHUB_APP_ID}",
    },
  ];
  if (
    statusChecks.do_not_enforce_on_create !== false ||
    statusChecks.strict_required_status_checks_policy !== true ||
    canonicalJson(statusChecks.required_status_checks) !== canonicalJson(expectedChecks)
  ) {
    throw new Error("ruleset plan required status check source drifted");
  }
  for (const type of ["non_fast_forward", "deletion", "required_linear_history"]) {
    findRule(plan, type);
  }
  if (plan.ruleset.rules.some(rule => rule?.type === "workflows" || rule?.type === "merge_queue")) {
    throw new Error("this personal-repository plan must not claim required-workflow or merge-queue enforcement");
  }
  const legacy = plan.legacyBranchProtection;
  if (
    legacy?.preserveExactly !== true ||
    legacy?.requirePresent !== true ||
    legacy?.requireAdminEnforcementIfPresent !== true ||
    legacy?.observedAt !== "2026-09-05T03:47:06Z" ||
    canonicalJson(legacy?.expectedState) !==
      canonicalJson({
        enforceAdmins: true,
        requiredStatusChecksStrict: true,
        requiredPullRequestReviews: null,
        restrictions: null,
        requiredLinearHistory: false,
        requiredSignatures: false,
        allowForcePushes: false,
        allowDeletions: false,
        requiredConversationResolution: false,
      }) ||
    !Array.isArray(legacy.expectedRequiredStatusChecks) ||
    legacy.expectedRequiredStatusChecks.length !== 13
  ) {
    throw new Error("ruleset plan must preserve the existing strict 13-check branch protection");
  }
  for (const check of legacy.expectedRequiredStatusChecks) {
    if (
      typeof check?.context !== "string" ||
      !Number.isSafeInteger(check?.app_id) ||
      check.app_id <= 0
    ) {
      throw new Error("ruleset plan contains an invalid legacy required check");
    }
  }
  if (
    plan.preflight?.requirePositiveAppProbe !== true ||
    plan.preflight?.requireNegativeActionsProbe !== true ||
    plan.preflight?.requireProbePullRequests !== true ||
    plan.preflight?.requirePostCreationCausalProbes !== true ||
    plan.preflight?.requireOperatorNonceChallenge !== true ||
    plan.preflight?.requireExternalEvaluatorOrigin !== true ||
    plan.preflight?.requireNegativeAppFailure !== true ||
    plan.preflight?.maxEvidenceAgeSeconds !== 300 ||
    plan.preflight?.positiveEvaluatorMode !== "not-applicable" ||
    plan.preflight?.negativeEvaluatorMode !== "activation-rejected" ||
    plan.preflight?.positiveMergeability !== "clean" ||
    plan.preflight?.negativeMergeability !== "blocked"
  ) {
    throw new Error("ruleset plan must require positive and negative App probes");
  }
  return plan;
}

export function materializeRuleset(plan, appId) {
  assertRulesetPlan(plan);
  const normalizedAppId = String(appId ?? "");
  if (!APP_ID.test(normalizedAppId)) {
    throw new Error("a non-zero dedicated GitHub App ID is required");
  }
  const ruleset = clone(plan.ruleset);
  const statusRule = findRule({ ...plan, ruleset }, "required_status_checks");
  const materializedStatus = ruleset.rules.find(rule => rule.type === "required_status_checks");
  materializedStatus.parameters.required_status_checks = statusRule.parameters.required_status_checks.map(
    check => ({
      ...check,
      integration_id: Number(normalizedAppId),
    }),
  );
  return {
    name: plan.managedRulesetName,
    target: ruleset.target,
    enforcement: ruleset.enforcement,
    bypass_actors: ruleset.bypass_actors,
    conditions: ruleset.conditions,
    rules: ruleset.rules,
  };
}

function stripVolatile(value) {
  if (Array.isArray(value)) return value.map(stripVolatile);
  if (!value || typeof value !== "object") return value;
  const omitted = new Set([
    "url",
    "html_url",
    "node_id",
    "_links",
    "created_at",
    "updated_at",
    "contexts_url",
    "users_url",
    "teams_url",
    "apps_url",
  ]);
  return Object.fromEntries(
    Object.entries(value)
      .filter(([key]) => !omitted.has(key))
      .map(([key, nested]) => [key, stripVolatile(nested)]),
  );
}

function normalizedRuleset(ruleset) {
  return normalizeRulesetForSecurity(ruleset);
}

function normalizeRuleForSecurity(rule) {
  if (!rule || typeof rule !== "object") return rule;
  const normalized = { type: rule.type };
  if (rule.parameters && typeof rule.parameters === "object") {
    if (Object.keys(rule.parameters).length > 0) {
      normalized.parameters = stripVolatile(rule.parameters);
    }
  }
  return normalized;
}

export function normalizeRulesetForSecurity(ruleset) {
  if (!ruleset || typeof ruleset !== "object") return ruleset;
  const normalized = {
    name: ruleset.name,
    target: ruleset.target,
    source_type: ruleset.source_type,
    source: ruleset.source,
    enforcement: ruleset.enforcement,
    bypass_actors: stripVolatile(ruleset.bypass_actors ?? []),
    conditions: stripVolatile(ruleset.conditions),
    rules: (ruleset.rules ?? [])
      .map(normalizeRuleForSecurity)
      .sort((left, right) =>
        `${left?.type ?? ""}:${canonicalJson(left?.parameters ?? {})}`.localeCompare(
          `${right?.type ?? ""}:${canonicalJson(right?.parameters ?? {})}`,
        ),
      ),
  };
  return normalized;
}

export function securitySnapshot({ repository, branchProtection, rulesets }) {
  if (!repository || typeof repository !== "object") {
    throw new Error("live repository payload is missing");
  }
  const normalizedRulesets = (rulesets ?? [])
    .map(normalizedRuleset)
    .sort((left, right) =>
      `${left.name ?? ""}:${left.id ?? ""}`.localeCompare(`${right.name ?? ""}:${right.id ?? ""}`),
    );
  return {
    repository: {
      id: repository.id,
      full_name: repository.full_name,
      owner_type: repository.owner?.type ?? repository.owner_type,
      default_branch: repository.default_branch,
      allow_merge_commit: repository.allow_merge_commit,
      allow_squash_merge: repository.allow_squash_merge,
      allow_rebase_merge: repository.allow_rebase_merge,
    },
    branchProtection: branchProtection === null ? null : stripVolatile(branchProtection),
    rulesets: normalizedRulesets,
  };
}

export function digestSecuritySnapshot(live) {
  return digestJson(securitySnapshot(live));
}

export function findManagedRulesets(rulesets, plan) {
  assertRulesetPlan(plan);
  return (rulesets ?? []).filter(
    ruleset =>
      ruleset?.name === plan.managedRulesetName &&
      (ruleset?.source_type === undefined || ruleset.source_type === "Repository"),
  );
}

function assertLegacyProtectionCompatibility(plan, branchProtection) {
  if (!branchProtection) {
    if (plan.legacyBranchProtection.requirePresent) {
      throw new Error("legacy branch protection is missing");
    }
    return;
  }
  const enabledFlag = value =>
    typeof value === "object" && value !== null ? value.enabled : value;
  const enforceAdmins = branchProtection.enforce_admins;
  const enabled = enabledFlag(enforceAdmins);
  if (
    plan.legacyBranchProtection.requireAdminEnforcementIfPresent &&
    enabled !== true
  ) {
    throw new Error("legacy branch protection does not enforce administrators");
  }
  const required = branchProtection.required_status_checks;
  if (!required || required.strict !== true || !Array.isArray(required.checks)) {
    throw new Error("legacy branch protection is not strict");
  }
  const actualChecks = required.checks
    .map(check => ({ context: check?.context, app_id: check?.app_id }))
    .sort((left, right) =>
      `${left.context ?? ""}:${left.app_id ?? ""}`.localeCompare(
        `${right.context ?? ""}:${right.app_id ?? ""}`,
      ),
    );
  const expectedChecks = plan.legacyBranchProtection.expectedRequiredStatusChecks
    .map(check => ({ context: check.context, app_id: check.app_id }))
    .sort((left, right) =>
      `${left.context}:${left.app_id}`.localeCompare(`${right.context}:${right.app_id}`),
    );
  if (canonicalJson(actualChecks) !== canonicalJson(expectedChecks)) {
    throw new Error("legacy branch protection required checks drifted");
  }
  const actualContexts = (required.contexts ?? []).slice().sort();
  const expectedContexts = expectedChecks.map(check => check.context).sort();
  if (canonicalJson(actualContexts) !== canonicalJson(expectedContexts)) {
    throw new Error("legacy branch protection required check contexts drifted");
  }
  const expectedState = plan.legacyBranchProtection.expectedState;
  const actualState = {
    enforceAdmins: enabled,
    requiredStatusChecksStrict: required.strict,
    requiredPullRequestReviews: branchProtection.required_pull_request_reviews ?? null,
    restrictions: branchProtection.restrictions ?? null,
    requiredLinearHistory: enabledFlag(branchProtection.required_linear_history),
    requiredSignatures: enabledFlag(branchProtection.required_signatures),
    allowForcePushes: enabledFlag(branchProtection.allow_force_pushes),
    allowDeletions: enabledFlag(branchProtection.allow_deletions),
    requiredConversationResolution: enabledFlag(
      branchProtection.required_conversation_resolution,
    ),
  };
  if (canonicalJson(actualState) !== canonicalJson(expectedState)) {
    throw new Error("legacy branch protection differs from the owner-authenticated snapshot");
  }
}

function assertRepositoryBaseline(plan, repository) {
  if (
    repository?.full_name !== plan.repository ||
    (repository?.owner?.type ?? repository?.owner_type) !== plan.ownerType ||
    repository?.default_branch !== plan.defaultBranch ||
    repository?.allow_merge_commit !== true ||
    repository?.allow_squash_merge !== true ||
    repository?.allow_rebase_merge !== true
  ) {
    throw new Error(
      "read-back is for the wrong repository, owner type, default branch, or merge-method state",
    );
  }
}

export function assertLegacyBaseline({
  plan,
  repository,
  branchProtection,
}) {
  assertRulesetPlan(plan);
  assertRepositoryBaseline(plan, repository);
  assertLegacyProtectionCompatibility(plan, branchProtection);
  return {
    observedAt: plan.legacyBranchProtection.observedAt,
    requiredChecks: plan.legacyBranchProtection.expectedRequiredStatusChecks.length,
    additiveOnly: plan.applicationMode === "create-only-additive",
  };
}

export function assertRulesetReadBack({
  plan,
  appId,
  repository,
  ruleset,
  branchProtection = null,
}) {
  assertRulesetPlan(plan);
  assertRepositoryBaseline(plan, repository);
  const expected = materializeRuleset(plan, appId);
  if (ruleset?.source_type !== "Repository" || ruleset?.source !== plan.repository) {
    throw new Error("managed ruleset source does not match the repository");
  }
  if (!Number.isSafeInteger(Number(ruleset?.id)) || Number(ruleset.id) <= 0) {
    throw new Error("managed ruleset read-back does not contain a valid ID");
  }
  const expectedSecurity = normalizeRulesetForSecurity({
    ...expected,
    source_type: "Repository",
    source: plan.repository,
  });
  const actualSecurity = normalizeRulesetForSecurity(ruleset);
  if (canonicalJson(actualSecurity) !== canonicalJson(expectedSecurity)) {
    throw new Error("managed ruleset read-back does not exactly match the reviewed intent");
  }
  assertLegacyProtectionCompatibility(plan, branchProtection);
  return {
    checkName: plan.expectedSource.checkName,
    integrationId: Number(appId),
    strict: true,
    codeOwnerReview: true,
    reviews: 1,
    conversationResolution: true,
    forcePushBlocked: true,
    deletionBlocked: true,
    linearHistory: true,
    bypassActors: 0,
  };
}

export function assertUnrelatedSecurityStatePreserved({
  before,
  after,
  managedRulesetName,
}) {
  const withoutManaged = snapshot =>
    securitySnapshot(snapshot).rulesets.filter(rule => rule.name !== managedRulesetName);
  const beforeSnapshot = securitySnapshot(before);
  const afterSnapshot = securitySnapshot(after);
  if (
    canonicalJson({
      repository: beforeSnapshot.repository,
      branchProtection: beforeSnapshot.branchProtection,
      rulesets: withoutManaged(before),
    }) !==
    canonicalJson({
      repository: afterSnapshot.repository,
      branchProtection: afterSnapshot.branchProtection,
      rulesets: withoutManaged(after),
    })
  ) {
    throw new Error("unrelated branch protection, restrictions, signatures, or rulesets drifted");
  }
  return true;
}

export function encodeEvaluatorExternalId(payload) {
  return `${EXTERNAL_ID_PREFIX}${Buffer.from(canonicalJson(payload), "utf8").toString("base64url")}`;
}

export function parseEvaluatorExternalId(value) {
  if (typeof value !== "string" || !value.startsWith(EXTERNAL_ID_PREFIX)) {
    throw new Error("evaluator check external_id has the wrong prefix");
  }
  const encoded = value.slice(EXTERNAL_ID_PREFIX.length);
  let payload;
  try {
    payload = JSON.parse(Buffer.from(encoded, "base64url").toString("utf8"));
  } catch {
    throw new Error("evaluator check external_id is not valid base64url canonical JSON");
  }
  if (
    !payload ||
    typeof payload !== "object" ||
    Array.isArray(payload) ||
    encodeEvaluatorExternalId(payload) !== value
  ) {
    throw new Error("evaluator check external_id is not canonical");
  }
  return payload;
}

function parseTimestamp(value, label) {
  const text = String(value ?? "");
  if (!ISO_TIMESTAMP.test(text)) {
    throw new Error(`${label} is not an ISO timestamp`);
  }
  const milliseconds = Date.parse(text);
  if (!Number.isFinite(milliseconds)) {
    throw new Error(`${label} is invalid`);
  }
  return milliseconds;
}

function assertPullRequestAssociation(run, {
  repository,
  pullNumber,
  headSha,
  baseSha,
}) {
  const associations = run?.pull_requests;
  if (!Array.isArray(associations) || associations.length !== 1) {
    throw new Error("check run is not associated with exactly one probe pull request");
  }
  const association = associations[0];
  if (
    Number(association?.number) !== Number(pullNumber) ||
    association?.head?.sha !== headSha ||
    association?.base?.sha !== baseSha ||
    association?.head?.repo?.full_name !== repository ||
    association?.base?.repo?.full_name !== repository
  ) {
    throw new Error("check run pull-request association does not match the probe");
  }
}

function assertFreshRunWindow(run, {
  rulesetCreatedAt,
  observedAt,
  maxAgeSeconds,
}) {
  const rulesetCreated = parseTimestamp(rulesetCreatedAt, "ruleset creation time");
  const observed = parseTimestamp(observedAt, "probe observation time");
  const started = parseTimestamp(run?.started_at, "check started_at");
  const completed = parseTimestamp(run?.completed_at, "check completed_at");
  if (
    started < rulesetCreated ||
    completed < rulesetCreated ||
    completed < started ||
    started > observed + 30_000 ||
    completed > observed + 30_000 ||
    observed - started > maxAgeSeconds * 1000
  ) {
    throw new Error("check run timestamps are stale or precede ruleset creation");
  }
  return { rulesetCreated, observed, started, completed };
}

export function assertFreshEvaluatorCheck({
  checkRuns,
  targetSha,
  baseSha,
  pullNumber,
  repository = CHECK_ASSOCIATION_REPOSITORY,
  appId,
  checkName,
  policyDigest,
  policyVersion,
  expectedNonce,
  evaluatorOrigin,
  expectedMode,
  expectedConclusion,
  rulesetCreatedAt,
  observedAt,
  maxAgeSeconds = 300,
}) {
  if (
    !FULL_OBJECT_ID.test(String(targetSha ?? "")) ||
    !FULL_OBJECT_ID.test(String(baseSha ?? "")) ||
    !SHA256.test(String(policyDigest ?? "")) ||
    !SHA256.test(String(expectedNonce ?? "")) ||
    !APP_ID.test(String(appId ?? "")) ||
    !Number.isSafeInteger(Number(policyVersion)) ||
    Number(policyVersion) <= 0 ||
    !Number.isSafeInteger(Number(pullNumber)) ||
    Number(pullNumber) <= 0 ||
    !/^[a-z][a-z0-9-]{0,63}$/.test(String(expectedMode ?? "")) ||
    !Number.isSafeInteger(Number(maxAgeSeconds)) ||
    Number(maxAgeSeconds) <= 0
  ) {
    throw new Error("fresh evaluator probe coordinates are invalid");
  }
  let evaluatorUrl;
  try {
    evaluatorUrl = new URL(evaluatorOrigin);
  } catch {
    throw new Error("evaluator origin is invalid");
  }
  const normalizedEvaluatorOrigin = evaluatorUrl.origin;
  if (
    normalizedEvaluatorOrigin !== evaluatorOrigin ||
    !normalizedEvaluatorOrigin.startsWith("https://") ||
    normalizedEvaluatorOrigin === "https://github.com" ||
    normalizedEvaluatorOrigin === "https://api.github.com" ||
    evaluatorUrl.hostname === "localhost" ||
    evaluatorUrl.hostname.endsWith(".localhost") ||
    evaluatorUrl.hostname === "127.0.0.1" ||
    evaluatorUrl.hostname === "::1"
  ) {
    throw new Error("evaluator origin must be an exact external HTTPS origin");
  }
  const candidates = (checkRuns ?? []).filter(
    run =>
      run?.name === checkName &&
      run?.head_sha === targetSha &&
      Number(run?.app?.id) === Number(appId) &&
      run?.status === "completed" &&
      run?.conclusion === expectedConclusion,
  );
  const failures = [];
  for (const run of candidates) {
    try {
      assertPullRequestAssociation(run, {
        repository,
        pullNumber,
        headSha: targetSha,
        baseSha,
      });
      if (new URL(run.details_url).origin !== evaluatorOrigin) {
        throw new Error("check run details_url is not owned by the reviewed evaluator origin");
      }
      const times = assertFreshRunWindow(run, {
        rulesetCreatedAt,
        observedAt,
        maxAgeSeconds,
      });
      const payload = parseEvaluatorExternalId(run.external_id);
      const expectedFields = [
        "nonce",
        "repository",
        "pull_request",
        "head_sha",
        "base_sha",
        "policy_digest",
        "policy_version",
        "mode",
        "issued_at",
      ].sort();
      if (canonicalJson(Object.keys(payload).sort()) !== canonicalJson(expectedFields)) {
        throw new Error("evaluator check external_id fields are not exact");
      }
      if (
        payload.nonce !== expectedNonce ||
        payload.repository !== repository ||
        Number(payload.pull_request) !== Number(pullNumber) ||
        payload.head_sha !== targetSha ||
        payload.base_sha !== baseSha ||
        payload.policy_digest !== policyDigest ||
        Number(payload.policy_version) !== Number(policyVersion) ||
        payload.mode !== expectedMode
      ) {
        throw new Error("evaluator check external_id is not bound to the exact probe");
      }
      const issued = parseTimestamp(payload.issued_at, "external_id issued_at");
      if (
        issued < times.rulesetCreated ||
        issued > times.observed + 30_000 ||
        issued > times.completed ||
        times.observed - issued > maxAgeSeconds * 1000 ||
        times.started < issued - 30_000
      ) {
        throw new Error("evaluator check external_id timestamp is stale or non-causal");
      }
      return { nonce: payload.nonce, runId: Number(run.id), payload };
    } catch (error) {
      failures.push(error.message);
    }
  }
  throw new Error(
    failures[0] ??
      "no fresh required check was produced by the expected GitHub App for the probe",
  );
}

export function assertExpectedSourceCheck({
  checkRuns,
  targetSha,
  appId,
  checkName,
}) {
  if (!FULL_OBJECT_ID.test(String(targetSha ?? ""))) {
    throw new Error("target SHA must be a full Git object id");
  }
  if (!APP_ID.test(String(appId ?? ""))) {
    throw new Error("expected source App ID is invalid");
  }
  const expectedAppId = Number(appId);
  const matching = (checkRuns ?? []).filter(
    run =>
      run?.name === checkName &&
      run?.head_sha === targetSha &&
      Number(run?.app?.id) === expectedAppId,
  );
  const passing = matching.some(
    run => run.status === "completed" && run.conclusion === "success",
  );
  if (!passing) {
    throw new Error(
      "no successful required check was produced by the expected GitHub App on the evaluated SHA",
    );
  }
  return true;
}

export function assertSpoofedSourceRejected({
  checkRuns,
  targetSha,
  appId,
  checkName,
  mergeable,
  mergeableState,
}) {
  if (!FULL_OBJECT_ID.test(String(targetSha ?? ""))) {
    throw new Error("spoof probe SHA must be a full Git object id");
  }
  if (!APP_ID.test(String(appId ?? ""))) {
    throw new Error("spoof probe App ID is invalid");
  }
  const expectedAppId = Number(appId);
  const expectedSuccess = (checkRuns ?? []).some(
    run =>
      run?.name === checkName &&
      run?.head_sha === targetSha &&
      Number(run?.app?.id) === expectedAppId &&
      run?.status === "completed" &&
      run?.conclusion === "success",
  );
  if (expectedSuccess) {
    throw new Error("negative spoof probe also contains the expected App check");
  }
  const spoof = (checkRuns ?? []).filter(
    run =>
      run?.name === checkName &&
      run?.head_sha === targetSha &&
      Number(run?.app?.id) !== expectedAppId &&
      run?.app?.slug === "github-actions" &&
      run?.status === "completed" &&
      run?.conclusion === "success",
  );
  if (spoof.length === 0) {
    throw new Error("negative spoof probe did not contain a successful same-name GitHub Actions run");
  }
  if (typeof mergeable !== "boolean" || mergeableState !== "blocked") {
    throw new Error(
      "negative spoof probe was not blocked by the source-bound required check; mergeability is ambiguous",
    );
  }
  return true;
}

export function assertProbeResults({
  positive,
  negative,
  appId,
  checkName,
  policyDigest,
  policyVersion,
  rulesetCreatedAt,
  observedAt,
  positiveMode = "not-applicable",
  negativeMode = "activation-rejected",
  maxAgeSeconds = 300,
  positiveNonce,
  negativeNonce,
  evaluatorOrigin,
}) {
  if (!positive?.pull || !negative?.pull) {
    throw new Error("both positive App and negative spoof pull-request probes are required");
  }
  const positiveSha = positive.pull.headSha ?? positive.pull.head_sha;
  const negativeSha = negative.pull.headSha ?? negative.pull.head_sha;
  const positiveBaseSha = positive.pull.baseSha ?? positive.pull.base_sha;
  const negativeBaseSha = negative.pull.baseSha ?? negative.pull.base_sha;
  const positiveRepository =
    positive.pull.repository ?? positive.pull.base?.repo?.full_name;
  const negativeRepository =
    negative.pull.repository ?? negative.pull.base?.repo?.full_name;
  if (!FULL_OBJECT_ID.test(String(positiveSha ?? "")) || !FULL_OBJECT_ID.test(String(negativeSha ?? ""))) {
    throw new Error("both source probes must identify exact pull-request heads");
  }
  if (positiveSha === negativeSha) {
    throw new Error("positive and negative source probes must use different pull-request heads");
  }
  if (
    !SHA256.test(String(positiveNonce ?? "")) ||
    !SHA256.test(String(negativeNonce ?? "")) ||
    positiveNonce === negativeNonce
  ) {
    throw new Error("positive and negative probes require distinct fresh operator nonces");
  }
  if (
    positiveRepository !== CHECK_ASSOCIATION_REPOSITORY ||
    negativeRepository !== CHECK_ASSOCIATION_REPOSITORY ||
    !FULL_OBJECT_ID.test(String(positiveBaseSha ?? "")) ||
    !FULL_OBJECT_ID.test(String(negativeBaseSha ?? ""))
  ) {
    throw new Error("probe pull requests are not bound to the expected repository and base SHA");
  }
  const positiveProof = assertFreshEvaluatorCheck({
    checkRuns: positive.checkRuns,
    targetSha: positiveSha,
    baseSha: positiveBaseSha,
    pullNumber: positive.pull.number,
    repository: positiveRepository,
    appId,
    checkName,
    policyDigest,
    policyVersion,
    expectedNonce: positiveNonce,
    evaluatorOrigin,
    expectedMode: positiveMode,
    expectedConclusion: "success",
    rulesetCreatedAt,
    observedAt,
    maxAgeSeconds,
  });
  const positiveMergeable =
    positive.pull.mergeable === true &&
    positive.pull.mergeable_state === "clean";
  if (!positiveMergeable) {
    throw new Error("positive App probe did not report an unambiguous mergeable state");
  }
  const negativeProof = assertFreshEvaluatorCheck({
    checkRuns: negative.checkRuns,
    targetSha: negativeSha,
    baseSha: negativeBaseSha,
    pullNumber: negative.pull.number,
    repository: negativeRepository,
    appId,
    checkName,
    policyDigest,
    policyVersion,
    expectedNonce: negativeNonce,
    evaluatorOrigin,
    expectedMode: negativeMode,
    expectedConclusion: "failure",
    rulesetCreatedAt,
    observedAt,
    maxAgeSeconds,
  });
  const actionsRuns = (negative.checkRuns ?? []).filter(
    run =>
      run?.name === checkName &&
      run?.head_sha === negativeSha &&
      Number(run?.app?.id) === 15368 &&
      run?.app?.slug === "github-actions" &&
      run?.status === "completed" &&
      run?.conclusion === "success",
  );
  let actionsAccepted = false;
  for (const run of actionsRuns) {
    try {
      assertPullRequestAssociation(run, {
        repository: negativeRepository,
        pullNumber: negative.pull.number,
        headSha: negativeSha,
        baseSha: negativeBaseSha,
      });
      assertFreshRunWindow(run, { rulesetCreatedAt, observedAt, maxAgeSeconds });
      actionsAccepted = true;
      break;
    } catch {
      // Try another same-name Actions run; stale or unassociated runs are not evidence.
    }
  }
  if (!actionsAccepted) {
    throw new Error("negative spoof probe lacks a fresh associated GitHub Actions success");
  }
  if (
    typeof negative.pull.mergeable !== "boolean" ||
    negative.pull.mergeable_state !== "blocked"
  ) {
    throw new Error(
      "negative spoof probe was not blocked by the source-bound required check; mergeability is ambiguous",
    );
  }
  return {
    positive: true,
    negative: true,
    positiveNonce: positiveProof.nonce,
    negativeNonce: negativeProof.nonce,
  };
}

export function assertSafeRollbackTarget({
  beforeRulesetIds = [],
  createdRuleset,
  readBackRuleset,
  history,
  ownerId,
  expectedRuleset,
  expectedRepository = "judeper/FSI-AgentGov",
  startedAt,
  endedAt,
}) {
  const id = Number(createdRuleset?.id);
  if (!Number.isSafeInteger(id) || id <= 0 || beforeRulesetIds.map(Number).includes(id)) {
    throw new Error("rollback target is not a newly created ruleset");
  }
  if (
    createdRuleset?.name !== expectedRuleset?.name ||
    Number(readBackRuleset?.id) !== id ||
    readBackRuleset?.name !== expectedRuleset?.name
  ) {
    throw new Error("rollback target name or ID could not be confirmed");
  }
  if (
    readBackRuleset?.source_type !== "Repository" ||
    typeof readBackRuleset?.source !== "string" ||
    readBackRuleset.source !== expectedRepository
  ) {
    throw new Error("rollback target repository source could not be confirmed");
  }
  const createdAt = String(readBackRuleset?.created_at ?? createdRuleset?.created_at ?? "");
  if (!ISO_TIMESTAMP.test(createdAt)) {
    throw new Error("rollback target creation time is unavailable");
  }
  const createdMillis = Date.parse(createdAt);
  const startMillis = Date.parse(String(startedAt ?? ""));
  const endMillis = Date.parse(String(endedAt ?? ""));
  if (
    !Number.isFinite(createdMillis) ||
    !Number.isFinite(startMillis) ||
    !Number.isFinite(endMillis) ||
    createdMillis < startMillis - 300_000 ||
    createdMillis > endMillis + 300_000
  ) {
    throw new Error("rollback target creation time is outside the apply transaction");
  }
  const latest = (history ?? [])
    .filter(entry => ISO_TIMESTAMP.test(String(entry?.updated_at ?? "")))
    .sort((left, right) => Date.parse(right.updated_at) - Date.parse(left.updated_at))[0];
  if (
    !latest ||
    latest.actor?.type !== "User" ||
    Number(latest.actor?.id) !== Number(ownerId)
  ) {
    throw new Error("rollback target creator could not be confirmed as the owner");
  }
  const historyMillis = Date.parse(latest.updated_at);
  if (
    !Number.isFinite(historyMillis) ||
    historyMillis < startMillis - 300_000 ||
    historyMillis > endMillis + 300_000
  ) {
    throw new Error("rollback target history timestamp is outside the apply transaction");
  }
  const expectedSecurity = normalizeRulesetForSecurity({
    ...expectedRuleset,
    source_type: "Repository",
    source: expectedRepository,
  });
  if (
    canonicalJson(normalizeRulesetForSecurity(readBackRuleset)) !==
    canonicalJson(expectedSecurity)
  ) {
    throw new Error("rollback target security digest does not match the intended ruleset");
  }
  return true;
}

function parseCliArguments(argv) {
  const [operation, ...rest] = argv;
  const values = {};
  for (let index = 0; index < rest.length; index += 1) {
    if (!rest[index].startsWith("--")) throw new Error(`unexpected argument '${rest[index]}'`);
    const key = rest[index].slice(2);
    const value = rest[index + 1];
    if (value === undefined || value.startsWith("--")) throw new Error(`missing value for --${key}`);
    values[key] = value;
    index += 1;
  }
  return { operation, values };
}

async function readStdinJson() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  const text = Buffer.concat(chunks).toString("utf8").trim();
  if (!text) throw new Error("expected JSON on stdin");
  return JSON.parse(text);
}

async function runCli() {
  const { operation, values } = parseCliArguments(process.argv.slice(2));
  if (operation === "validate-plan") {
    const plan = loadRulesetPlan(values.plan);
    process.stdout.write(`${JSON.stringify({ ok: true, state: plan.state })}\n`);
    return;
  }
  if (operation === "validate-contract") {
    const contract = loadAppContract(values.contract);
    process.stdout.write(`${JSON.stringify({ ok: true, state: contract.state })}\n`);
    return;
  }
  if (operation === "materialize") {
    const plan = loadRulesetPlan(values.plan);
    process.stdout.write(`${JSON.stringify(materializeRuleset(plan, values["app-id"]))}\n`);
    return;
  }
  if (operation === "policy-evidence") {
    process.stdout.write(`${JSON.stringify(getPolicyEvidence(values.policy))}\n`);
    return;
  }
  const input = await readStdinJson();
  if (operation === "assert-app-installation") {
    assertAppInstallationPayload(input);
    process.stdout.write('{"ok":true}\n');
    return;
  }
  if (operation === "assert-owner") {
    assertOwnerIdentity(input);
    process.stdout.write('{"ok":true}\n');
    return;
  }
  if (operation === "assert-legacy-baseline") {
    const plan = loadRulesetPlan(values.plan);
    process.stdout.write(`${JSON.stringify(assertLegacyBaseline({ ...input, plan }))}\n`);
    return;
  }
  if (operation === "digest") {
    process.stdout.write(`${JSON.stringify({ digest: digestJson(input) })}\n`);
    return;
  }
  if (operation === "snapshot") {
    process.stdout.write(`${JSON.stringify({ snapshot: securitySnapshot(input), digest: digestSecuritySnapshot(input) })}\n`);
    return;
  }
  if (operation === "assert-readback") {
    const plan = loadRulesetPlan(values.plan);
    process.stdout.write(
      `${JSON.stringify(assertRulesetReadBack({ ...input, plan, appId: values["app-id"] }))}\n`,
    );
    return;
  }
  if (operation === "assert-unrelated-preserved") {
    assertUnrelatedSecurityStatePreserved(input);
    process.stdout.write('{"ok":true}\n');
    return;
  }
  if (operation === "assert-probes") {
    process.stdout.write(`${JSON.stringify(assertProbeResults(input))}\n`);
    return;
  }
  if (operation === "assert-safe-rollback") {
    assertSafeRollbackTarget(input);
    process.stdout.write('{"ok":true}\n');
    return;
  }
  throw new Error(`unsupported operation '${operation ?? ""}'`);
}

if (pathToFileURL(process.argv[1] ?? "").href === import.meta.url) {
  runCli().catch(error => {
    process.stderr.write(`trusted-dependency-ruleset: ${error.message}\n`);
    process.exitCode = 1;
  });
}
