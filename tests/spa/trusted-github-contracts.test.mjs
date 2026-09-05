import { describe, expect, it } from "vitest";
import { execFileSync } from "node:child_process";
import { join } from "node:path";
import {
  assertFreshEvaluatorCheck,
  buildProbeEvidence,
  collectCheckRunPages,
  encodeEvaluatorExternalId,
  loadAppContract,
} from "../../scripts/trusted/trusted-dependency-ruleset.mjs";
import { repoRoot } from "./_gitTreeFixtures.mjs";

const repository = "judeper/FSI-AgentGov";
const repoUrl = `https://api.github.com/repos/${repository}`;
const repo = { id: 1117160053, name: "FSI-AgentGov", full_name: repository, url: repoUrl };
const headSha = "29322b476c0f4f917d54b63095bdc262678ce519";
const baseSha = "54969197caca8e4b06a0826ee3acd3c2d1754945";
const nonce = "35".repeat(32);
const policyDigest = "9e".repeat(32);
const appId = 8675309;
const pullNumber = 101;
const now = "2026-09-05T05:00:00Z";
const created = "2026-09-05T04:59:00Z";
const fullPull = () => ({
  id: 2_000_101, number: pullNumber, url: `${repoUrl}/pulls/${pullNumber}`,
  state: "open", draft: false, mergeable: true, mergeable_state: "clean",
  head: { ref: "probe-positive", sha: headSha, repo: { ...repo } },
  base: { ref: "main", sha: baseSha, repo: { ...repo } },
});
function checkRun(id = 22_000_101) {
  const pull = fullPull();
  const { full_name: _fullName, ...compactRepo } = repo;
  return {
    id, node_id: `CR_fixture_${id}`, url: `${repoUrl}/check-runs/${id}`,
    name: "trusted-dependency-artifact", head_sha: headSha,
    app: { id: appId, slug: "trusted-dependency-artifact-app" },
    status: "completed", conclusion: "success",
    started_at: "2026-09-05T04:59:20Z", completed_at: "2026-09-05T04:59:30Z",
    details_url: "https://trusted-evaluator.example/runs/101",
    external_id: encodeEvaluatorExternalId({
      nonce, repository, pull_request: pullNumber, head_sha: headSha, base_sha: baseSha,
      policy_digest: policyDigest, policy_version: 2, mode: "not-applicable",
      issued_at: "2026-09-05T04:59:10Z",
    }),
    pull_requests: [{
      id: pull.id, number: pull.number, url: pull.url,
      head: { ref: pull.head.ref, sha: pull.head.sha, repo: { ...compactRepo } },
      base: { ref: pull.base.ref, sha: pull.base.sha, repo: { ...compactRepo } },
    }],
  };
}
const evidenceInput = () => ({
  pull: fullPull(), after: fullPull(), checkRunPages: [{ total_count: 1, check_runs: [checkRun()] }],
  pullNumber, repository,
});
const freshArgs = checkRuns => ({
  checkRuns, targetSha: headSha, baseSha, pullNumber, repository, appId,
  checkName: "trusted-dependency-artifact", policyDigest, policyVersion: 2, expectedNonce: nonce,
  evaluatorOrigin: "https://trusted-evaluator.example", expectedMode: "not-applicable",
  expectedConclusion: "success", rulesetCreatedAt: created, observedAt: now,
});

describe("GitHub-shaped checks and separately verified PR associations", () => {
  it("joins compact Checks associations to full authenticated PR read-back without weakening full_name", () => {
    const input = evidenceInput();
    expect(() => assertFreshEvaluatorCheck(freshArgs(input.checkRunPages[0].check_runs))).toThrow(/association/);
    const evidence = buildProbeEvidence(input);
    expect(evidence.checkRuns[0].pull_requests[0].head.repo.full_name).toBe(repository);
    expect(() => assertFreshEvaluatorCheck(freshArgs(evidence.checkRuns))).not.toThrow();
    expect(input.checkRunPages[0].check_runs[0].pull_requests[0].head.repo.full_name).toBeUndefined();
  });

  it("fails every incomplete or stale compact association instead of filling fields from expectations", () => {
    for (const mutate of [
      value => { delete value.pull.head.repo.full_name; },
      value => { delete value.after.base.repo.full_name; },
      value => { value.after.head.repo.full_name = "attacker/FSI-AgentGov"; },
      value => { value.after.head.sha = "f".repeat(40); },
      value => { value.after.base.sha = "e".repeat(40); },
      value => { value.after.number = 102; },
      value => { value.after.id++; },
      value => { value.after.state = "closed"; },
      value => { value.after.draft = true; },
      value => { value.checkRunPages[0].check_runs[0].url = "https://attacker.example/check-runs/1"; },
      value => { value.checkRunPages[0].check_runs[0].pull_requests = []; },
      value => { value.checkRunPages[0].check_runs[0].pull_requests.push(value.checkRunPages[0].check_runs[0].pull_requests[0]); },
      ...["head", "base"].flatMap(side => [
        value => { delete value.checkRunPages[0].check_runs[0].pull_requests[0][side].repo.id; },
        value => { delete value.checkRunPages[0].check_runs[0].pull_requests[0][side].repo.url; },
        value => { delete value.checkRunPages[0].check_runs[0].pull_requests[0][side].repo.name; },
        value => { delete value.checkRunPages[0].check_runs[0].pull_requests[0][side].sha; },
        value => { value.checkRunPages[0].check_runs[0].pull_requests[0][side].ref = "stale"; },
        value => { value.checkRunPages[0].check_runs[0].pull_requests[0][side].repo.full_name = "attacker/other"; },
      ]),
    ]) {
      const input = evidenceInput();
      mutate(input);
      expect(() => buildProbeEvidence(input)).toThrow();
    }
  });

  it("uses final mergeability, not a stale first observation", () => {
    const input = evidenceInput();
    input.after.mergeable_state = "blocked";
    expect(buildProbeEvidence(input).pull.mergeable_state).toBe("blocked");
    input.after.mergeable = null;
    expect(() => buildProbeEvidence(input)).toThrow(/ambiguous/);
  });

  it("ignores historical associations but never substitutes them for the latest source run", () => {
    const input = evidenceInput();
    const older = checkRun(22_000_100);
    older.pull_requests[0].base.sha = "f".repeat(40);
    older.started_at = "2026-09-05T04:59:00Z";
    input.checkRunPages = [{ total_count: 2, check_runs: [older, checkRun()] }];
    const evidence = buildProbeEvidence(input);
    expect(() => assertFreshEvaluatorCheck(freshArgs(evidence.checkRuns))).not.toThrow();
    input.checkRunPages[0].check_runs[1].pull_requests[0].base.sha = "e".repeat(40);
    expect(() => buildProbeEvidence(input)).toThrow(/stale/);
  });

  it("requires every page, stable total_count, unique IDs, and the exact page sizes", () => {
    const runs = Array.from({ length: 101 }, (_, i) => checkRun(22_000_101 + i));
    const pages = [
      { total_count: 101, check_runs: runs.slice(0, 100) },
      { total_count: 101, check_runs: runs.slice(100) },
    ];
    expect(collectCheckRunPages(pages).map(run => run.id)).toEqual(runs.map(run => run.id));
    for (const broken of [
      [], pages.slice(0, 1),
      [{ total_count: 101, check_runs: runs.slice(0, 99) }, pages[1]],
      [pages[0], { total_count: 102, check_runs: runs.slice(100) }],
      [pages[0], { total_count: 101, check_runs: [runs[0]] }],
      [{ check_runs: [runs[0]] }], [{ total_count: 1, check_runs: [[runs[0]]] }],
    ]) expect(() => collectCheckRunPages(broken)).toThrow();
  });

  it("does not cherry-pick a fresh success after a newer failure, queued run or malformed association", () => {
    const valid = buildProbeEvidence(evidenceInput()).checkRuns[0];
    for (const mutation of [
      { conclusion: "failure" }, { status: "queued", conclusion: null },
      { pull_requests: [] }, { external_id: "tdag.v1.invalid" },
      { started_at: "2026-09-05T05:00:01Z" },
      { details_url: "https://user:password@trusted-evaluator.example/runs/101" },
    ]) {
      const newer = { ...structuredClone(valid), id: valid.id + 1, ...mutation };
      expect(() => assertFreshEvaluatorCheck(freshArgs([valid, newer]))).toThrow();
    }
    expect(() => assertFreshEvaluatorCheck(freshArgs([valid, valid]))).toThrow(/duplicate/);
    const incomplete = structuredClone(valid);
    delete incomplete.pull_requests[0].base.repo.full_name;
    expect(() => assertFreshEvaluatorCheck(freshArgs([incomplete]))).toThrow(/association/);
    for (const origin of ["https://127.1.2.3", "https://[::1]"]) {
      expect(() => assertFreshEvaluatorCheck({ ...freshArgs([valid]), evaluatorOrigin: origin })).toThrow(/external HTTPS/);
    }
  });
});

function runOperator(input) {
  const output = execFileSync("pwsh", [
    "-NoProfile", "-NonInteractive", "-File", join(repoRoot, "tests", "fixtures", "trusted-ruleset-operator.ps1"),
  ], { cwd: repoRoot, input: JSON.stringify(input), encoding: "utf8", timeout: 20_000 });
  expect(output).not.toContain("TEST_FIXTURE_INSTALLATION");
  expect(output).not.toContain("TEST_FIXTURE_JWT");
  return JSON.parse(output);
}
const installation = () => ({
  id: 60_000_001, app_id: appId, target_type: "User", account: { login: "judeper" },
  repository_selection: "selected", suspended_at: null,
  permissions: { ...loadAppContract().allowedRepositoryPermissions },
  events: [...loadAppContract().requiredWebhookEvents],
});
const installationInput = () => ({
  operation: "assert-installation", app: { id: appId, slug: "trusted-dependency-artifact-app" },
  installations: [installation()], installation: installation(),
  permissions: { ...loadAppContract().allowedRepositoryPermissions },
  expiry: 3500, revokeFails: false,
  pages: [{ total_count: 1, repositories: [{ ...repo }] }],
});

describe("executed PowerShell API contracts (all network mocked)", () => {
  it("enumerates a non-enumerated REST installation array and every page into scalar records", () => {
    const values = Array.from({ length: 101 }, (_, i) => ({ ...installation(), id: 60_000_001 + i }));
    const result = runOperator({ operation: "installations", pages: [values.slice(0, 100), values.slice(100)] });
    expect(result.ok).toBe(true);
    expect(result.value).toHaveLength(101);
    expect(result.value.every(item => !Array.isArray(item))).toBe(true);
    expect(result.calls.map(call => call.endpoint)).toEqual([
      "app/installations?per_page=100&page=1", "app/installations?per_page=100&page=2",
    ]);
  });

  it("flattens repository pages and preserves one repository as an array of one object", () => {
    const single = runOperator({ operation: "repositories", pages: [{ total_count: 1, repositories: [repo] }] });
    expect(single.ok).toBe(true);
    expect(single.value).toEqual([repo]);
    const values = Array.from({ length: 101 }, (_, i) => ({ ...repo, id: repo.id + i, full_name: `owner/repo-${i}` }));
    const result = runOperator({ operation: "repositories", pages: [
      { total_count: 101, repositories: values.slice(0, 100) },
      { total_count: 101, repositories: values.slice(100) },
    ] });
    expect(result.ok).toBe(true);
    expect(result.value).toEqual(values);
  });

  it.each([
    [{ total_count: 2, repositories: [repo] }],
    [{ total_count: 1, repositories: [[repo]] }],
    [{ repositories: [repo] }],
    [{ total_count: 1, repositories: {} }],
    [{ total_count: 2, repositories: [repo, repo] }],
    [{ total_count: "1", repositories: [repo] }],
  ].map(pages => [pages]))("fails malformed or incomplete repository pagination %#", pages => {
    expect(runOperator({ operation: "repositories", pages }).ok).toBe(false);
  });

  it.each(["changed-total", "duplicate-page"])("rejects %s across installation-repository pages", problem => {
    const first = Array.from({ length: 100 }, (_, i) => ({ ...repo, id: repo.id + i, full_name: `owner/repo-${i}` }));
    const second = { total_count: 101, repositories: [{ ...repo, id: repo.id + 100, full_name: "owner/repo-100" }] };
    if (problem === "changed-total") second.total_count = 102;
    if (problem === "duplicate-page") second.repositories = [first[0]];
    const result = runOperator({ operation: "repositories", pages: [
      { total_count: 101, repositories: first }, second,
    ] });
    expect(result.ok).toBe(false);
    expect(result.calls).toHaveLength(2);
  });

  it("proves exactly one authorized repository with separated credentials and revocation", () => {
    const result = runOperator(installationInput());
    expect(result.ok).toBe(true);
    expect(result.calls.filter(call => call.endpoint.startsWith("app/") || call.endpoint === "app" ||
      call.endpoint.endsWith("/installation")).every(call => call.appCredential && !call.installationCredential)).toBe(true);
    expect(result.calls.filter(call => call.endpoint.startsWith("installation/")).every(call =>
      call.installationCredential && !call.appCredential)).toBe(true);
    expect(result.calls.at(-1)).toMatchObject({ endpoint: "installation/token", method: "DELETE" });
  });

  it.each(["extra-repository", "wrong-repository", "extra-installation", "expired", "overlong", "bad-expiry", "pagination", "permissions"])(
    "rejects %s and revokes the installation token on the failure path", scenario => {
      const input = installationInput();
      if (scenario === "extra-repository") input.pages[0] = { total_count: 2, repositories: [repo, { ...repo, id: repo.id + 1, full_name: "attacker/other" }] };
      if (scenario === "wrong-repository") input.pages[0].repositories[0].full_name = "attacker/other";
      if (scenario === "extra-installation") input.installations.push({ ...installation(), id: 60_000_002 });
      if (scenario === "expired") input.expiry = -1;
      if (scenario === "overlong") input.expiry = 3900;
      if (scenario === "bad-expiry") input.expiry = "not-a-time";
      if (scenario === "pagination") input.pages[0].total_count = 2;
      if (scenario === "permissions") input.permissions.contents = "write";
      const result = runOperator(input);
      expect(result.ok, scenario).toBe(false);
      expect(result.calls.at(-1), scenario).toMatchObject({ endpoint: "installation/token", method: "DELETE" });
    },
  );

  it("fails closed on revocation failure and does not report verification success", () => {
    const input = installationInput();
    input.revokeFails = true;
    const result = runOperator(input);
    expect(result.ok).toBe(false);
    expect(result.error).toMatch(/revocation/);
  });

  it.each([false, true])("pins REST origin and disables redirects without exposing exception tokens (failure=%s)", fail => {
    const result = runOperator({ operation: "transport", fail });
    expect(result.ok).toBe(!fail);
    expect(result.calls).toEqual([{
      uri: `${"https://api.github.com"}/installation/repositories`,
      method: "GET", redirections: 0, installationCredential: true,
    }]);
    if (fail) expect(result.error).toBe("GitHub App GET installation/repositories failed");
  });
});
