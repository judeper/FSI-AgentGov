import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { execFileSync } from "node:child_process";
import { copyFileSync, mkdirSync, mkdtempSync, rmSync } from "node:fs";
import { basename, delimiter, join } from "node:path";
import {
  assertProbeResults,
  assertSafeRollbackTarget,
  loadAppContract,
  loadRulesetPlan,
} from "../../scripts/trusted/trusted-dependency-ruleset.mjs";
import { repoRoot } from "./_gitTreeFixtures.mjs";

const cultures = ["Invariant", "fi-FI", "ar-SA", "fr-FR"];
const repository = "judeper/FSI-AgentGov";
const apiRoot = `https://api.github.com/repos/${repository}`;
const appId = 8675309;
const repo = {
  id: 1117160053, name: "FSI-AgentGov", full_name: repository, url: apiRoot,
  owner: { type: "User" }, default_branch: "main", permissions: { admin: true },
  allow_merge_commit: true, allow_squash_merge: true, allow_rebase_merge: true,
};
const baseSha = "54969197caca8e4b06a0826ee3acd3c2d1754945";

function probe(number, negative) {
  const { full_name: _fullName, ...compactRepo } = repo;
  const pull = {
    id: 2_000_000 + number, number, url: `${apiRoot}/pulls/${number}`,
    state: "open", draft: false, mergeable: true,
    mergeable_state: negative ? "blocked" : "clean",
    head: { ref: `probe-${number}`, sha: (negative ? "b" : "a").repeat(40), repo: { ...repo } },
    base: { ref: "main", sha: baseSha, repo: { ...repo } },
  };
  const run = {
    id: 22_000_000 + number, url: `${apiRoot}/check-runs/${22_000_000 + number}`,
    name: "trusted-dependency-artifact", head_sha: pull.head.sha,
    app: { id: appId, slug: "trusted-dependency-artifact-app" },
    status: "completed", conclusion: negative ? "failure" : "success",
    details_url: `https://trusted-evaluator.example/runs/${number}`,
    external_id: "", started_at: null, completed_at: null,
    pull_requests: [{
      id: pull.id, number, url: pull.url,
      head: { ...pull.head, repo: { ...compactRepo } },
      base: { ...pull.base, repo: { ...compactRepo } },
    }],
  };
  const runs = [run];
  if (negative) {
    runs.push({
      ...structuredClone(run), id: run.id + 1000,
      url: `${apiRoot}/check-runs/${run.id + 1000}`,
      app: { id: 15368, slug: "github-actions" }, conclusion: "success",
    });
  }
  return { pull, checkRunPages: [{ total_count: runs.length, check_runs: runs }] };
}

function payload() {
  const contract = loadAppContract();
  const checks = loadRulesetPlan().legacyBranchProtection.expectedRequiredStatusChecks;
  return {
    repository: repo,
    app: { id: appId, slug: "trusted-dependency-artifact-app" },
    installation: {
      id: 60_000_001, app_id: appId, target_type: "User", account: { login: "judeper" },
      repository_selection: "selected", suspended_at: null,
      permissions: contract.allowedRepositoryPermissions,
      events: contract.requiredWebhookEvents,
    },
    branchProtection: {
      required_status_checks: {
        strict: true, contexts: checks.map(check => check.context), checks,
      },
      enforce_admins: { enabled: true }, required_pull_request_reviews: null, restrictions: null,
      required_linear_history: { enabled: false }, required_signatures: { enabled: false },
      allow_force_pushes: { enabled: false }, allow_deletions: { enabled: false },
      required_conversation_resolution: { enabled: false },
    },
    positive: probe(101, false),
    negative: probe(102, true),
  };
}

function runTransaction(culture, scenario, { nodePath = process.execPath, env = process.env } = {}) {
  const before = Date.now();
  const output = execFileSync("pwsh", [
    "-NoProfile", "-NonInteractive", "-File",
    join(repoRoot, "tests", "fixtures", "trusted-ruleset-clock.ps1"),
  ], {
    cwd: repoRoot, encoding: "utf8", timeout: 30_000, env,
    input: JSON.stringify({
      culture, scenario, nodePath,
      payloadBase64: Buffer.from(JSON.stringify(payload())).toString("base64"),
    }),
  });
  expect(output).not.toMatch(/TEST(?:[._]FIXTURE)|PRIVATE_KEY|Bearer /);
  return { ...JSON.parse(output), before, after: Date.now() };
}

function modelCalls(result, operation) {
  return result.calls.filter(call => call.kind === "model" && call.operation === operation)
    .map(call => ({ ...call, evidence: JSON.parse(call.inputJson) }));
}

function expectGeneratedUtc(value, result) {
  expect(value).toMatch(/^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,7})?Z$/);
  expect(Date.parse(value)).toBeGreaterThanOrEqual(result.before);
  expect(Date.parse(value)).toBeLessThanOrEqual(result.after);
  expect(value.slice(0, 10)).toBe(new Date(Date.parse(value)).toISOString().slice(0, 10));
}

function expectCleanup(result) {
  expect(result.revocations).toBeGreaterThan(0);
  expect(result.tokenCleared).toBe(true);
  expectGeneratedUtc(result.tokenExpiresAt, {
    before: result.before + 1800_000, after: result.after + 1800_000,
  });
  expect(result.calls.filter(call => call.kind === "app" && call.endpoint === "installation/token"))
    .toHaveLength(result.revocations);
}

describe.each(cultures)("production generated-clock callers under %s", culture => {
  it.each(["success", "retry"])("runs plan, apply, serialized probe poll and read-back (%s)", scenario => {
    const result = runTransaction(culture, scenario);
    expect(result.ok, result.error).toBe(true);
    expect(result.value).toMatchObject({ mode: "apply", verified: true });
    expect(result.rulesetRemaining).toBe(true);
    expect(result.deleted).toBe(0);
    expect(result.sleeps).toBe(scenario === "retry" ? 1 : 0);
    const polls = modelCalls(result, "assert-probes");
    expect(polls).toHaveLength(scenario === "retry" ? 2 : 1);
    expect(polls.at(-1).accepted).toBe(true);
    for (const poll of polls) expectGeneratedUtc(poll.evidence.observedAt, result);
    expectGeneratedUtc(result.challenge.rulesetCreatedAt, result);
    expect(() => assertProbeResults(polls.at(-1).evidence)).not.toThrow();
    if (scenario === "retry") {
      expect(polls[0].accepted).toBe(false);
      expect(() => assertProbeResults(polls[0].evidence)).toThrow(/stale|precedes/);
    }
    expectCleanup(result);
  }, 35_000);

  it.each([
    "probe-malformed", "probe-stale", "probe-future", "lost-create-response",
    "lost-create-response-second-precision",
  ])(
    "fails closed and proves actual apply-start/rollback-end bounds and cleanup (%s)",
    scenario => {
      const result = runTransaction(culture, scenario);
      expect(result.ok).toBe(false);
      expect(result.error).toMatch(/the just-created ruleset was automatically rolled back/);
      expect(result.deleted).toBe(1);
      expect(result.rulesetRemaining).toBe(false);
      const rollbacks = modelCalls(result, "assert-safe-rollback");
      expect(rollbacks).toHaveLength(1);
      const { evidence, accepted } = rollbacks[0];
      expect(accepted).toBe(true);
      expectGeneratedUtc(evidence.startedAt, result);
      expectGeneratedUtc(evidence.endedAt, result);
      const earliestCreation = scenario === "lost-create-response-second-precision"
        ? Math.floor(Date.parse(evidence.startedAt) / 1000) * 1000
        : Date.parse(evidence.startedAt);
      expect(earliestCreation).toBeLessThanOrEqual(Date.parse(evidence.createdRuleset.created_at));
      expect(Date.parse(evidence.createdRuleset.created_at)).toBeLessThanOrEqual(Date.parse(evidence.endedAt));
      expect(Date.parse(evidence.history[0].updated_at)).toBeLessThanOrEqual(Date.parse(evidence.endedAt));
      expect(() => assertSafeRollbackTarget(evidence)).not.toThrow();
      expect(modelCalls(result, "assert-probes").every(call => !call.accepted)).toBe(true);
      expectCleanup(result);
    },
    35_000,
  );

  it.each([
    "rollback-stale", "rollback-future", "rollback-malformed",
    "rollback-history-future", "rollback-history-before-create",
  ])("does not delete a non-causal or malformed rollback target (%s)", scenario => {
    const result = runTransaction(culture, scenario);
    expect(result.ok).toBe(false);
    expect(result.error).toMatch(/owner attention/);
    expect(result.deleted).toBe(0);
    expect(result.rulesetRemaining).toBe(true);
    const rollbacks = modelCalls(result, "assert-safe-rollback");
    if (scenario === "rollback-malformed") {
      expect(rollbacks).toHaveLength(0);
    } else {
      expect(rollbacks).toHaveLength(1);
      expectGeneratedUtc(rollbacks[0].evidence.startedAt, result);
      expectGeneratedUtc(rollbacks[0].evidence.endedAt, result);
      expect(rollbacks[0].accepted).toBe(false);
      expect(() => assertSafeRollbackTarget(rollbacks[0].evidence)).toThrow(/outside the apply transaction/);
    }
    expectCleanup(result);
  }, 35_000);
});

describe("generated-clock Node executable boundary", () => {
  let fixtureRoot;
  let nodePath;
  let env;
  beforeAll(() => {
    const parent = join(repoRoot, "maintainers-local");
    mkdirSync(parent, { recursive: true });
    fixtureRoot = mkdtempSync(join(parent, "clock-node-path-"));
    const directories = ["first Node with spaces", "second Node with spaces"]
      .map(name => join(fixtureRoot, name));
    for (const directory of directories) {
      mkdirSync(directory);
      copyFileSync(process.execPath, join(directory, basename(process.execPath)));
    }
    nodePath = join(directories[0], basename(process.execPath));
    const entries = Object.entries(process.env);
    const inheritedPath = entries.find(([key]) => key.toLowerCase() === "path")?.[1] ?? "";
    env = Object.fromEntries(entries.filter(([key]) => key.toLowerCase() !== "path"));
    env.PATH = [...directories, inheritedPath].join(delimiter);
  }, 20_000);
  afterAll(() => {
    if (fixtureRoot) rmSync(fixtureRoot, { recursive: true, force: true });
  });

  it.each(cultures)("preserves a spaced executable with multiple Node applications on PATH under %s", culture => {
    const result = runTransaction(culture, "success", { nodePath, env });
    expect(result.ok, result.error).toBe(true);
    expect(result.value).toMatchObject({ mode: "apply", verified: true });
    expect(modelCalls(result, "assert-probes")).toHaveLength(1);
    expectCleanup(result);
  }, 35_000);
});
