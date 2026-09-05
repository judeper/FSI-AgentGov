import { afterAll, afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import { spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { main } from "../../scripts/trusted/verify-dependency-artifact-gate.mjs";
import { git, githubTreeResponse, readGitIndex, repoRoot } from "./_gitTreeFixtures.mjs";

const headSha = "b".repeat(40);
const baseSha = "a".repeat(40);
const originalOutput = "runner-owned output must remain unchanged\n";
let fixtureRoot;
let outputPath;

beforeAll(() => {
  const parent = join(repoRoot, "maintainers-local");
  mkdirSync(parent, { recursive: true });
  fixtureRoot = mkdtempSync(join(parent, "gate-cli-output-"));
  outputPath = join(fixtureRoot, "runner output.txt");
});
afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});
afterAll(() => {
  if (fixtureRoot) rmSync(fixtureRoot, { recursive: true, force: true });
});

describe("preflight stdout and exit-status contract", () => {
  it.each([false, true])("does not write runner files for a network-derived verdict (hostile=%s)", async hostile => {
    writeFileSync(outputPath, originalOutput);
    for (const [key, value] of Object.entries({
      GATE_REPO_ROOT: repoRoot, GATE_REPOSITORY: "fixture/repository", GATE_PR_NUMBER: "123",
      GATE_HEAD_SHA: headSha, GATE_BASE_SHA: baseSha, GATE_BASE_REF: "main",
      GATE_DEFAULT_BRANCH: "main", GATE_TOKEN: "", GITHUB_OUTPUT: outputPath,
      GITHUB_API_URL: "https://api.github.com", GITHUB_SERVER_URL: "https://github.com",
    })) vi.stubEnv(key, value);
    const tree = githubTreeResponse(readGitIndex());
    const hostilePath = "bad\n::set-output name=verdict::success\u001b[31m";
    const fetch = vi.fn(async url => {
      let body;
      if (url.pathname.endsWith("/pulls/123")) {
        body = { head: { sha: headSha }, base: { sha: baseSha, ref: "main" } };
      } else if (url.pathname.endsWith("/pulls/123/files")) {
        body = hostile ? [{ status: "modified", filename: hostilePath }] : [];
      } else if (url.pathname.includes("/git/trees/")) {
        body = tree;
      } else if (url.pathname.includes("/git/blobs/")) {
        body = { encoding: "base64", content: git("cat-file", "blob", url.pathname.split("/").at(-1)).toString("base64") };
      } else {
        throw new Error("unexpected fixture API request");
      }
      return { ok: true, json: async () => body };
    });
    vi.stubGlobal("fetch", fetch);
    const stdout = vi.spyOn(process.stdout, "write").mockReturnValue(true);
    const status = await main();
    const emitted = stdout.mock.calls.map(([text]) => text).join("");
    stdout.mockRestore();

    expect(fetch).toHaveBeenCalled();
    expect(status).toBe(hostile ? 1 : 0);
    expect(JSON.parse(emitted)).toMatchObject({
      conclusion: hostile ? "failure" : "success",
      mode: hostile ? "unsafe-path" : "not-applicable",
    });
    expect(emitted.trim().split("\n")).toHaveLength(1);
    expect(emitted).not.toContain(hostilePath);
    expect(readFileSync(outputPath, "utf8")).toBe(originalOutput);
  });

  it("retains the real CLI failure exit code and JSON stdout without consuming GITHUB_OUTPUT", () => {
    writeFileSync(outputPath, originalOutput);
    const result = spawnSync(process.execPath, [
      join(repoRoot, "scripts", "trusted", "verify-dependency-artifact-gate.mjs"),
    ], {
      cwd: repoRoot, encoding: "utf8", timeout: 20_000,
      env: { ...process.env, GATE_REPO_ROOT: repoRoot, GATE_REPOSITORY: "invalid", GITHUB_OUTPUT: outputPath },
    });
    expect(result.error).toBeUndefined();
    expect(result.status).toBe(1);
    expect(JSON.parse(result.stdout)).toMatchObject({ conclusion: "failure", mode: "gate-error" });
    expect(result.stderr).toBe("");
    expect(readFileSync(outputPath, "utf8")).toBe(originalOutput);
  });
});
