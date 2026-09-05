import { describe, expect, it } from "vitest";
import {
  collectProtectedPathIdentityProblems,
  createGitHubReader,
  diffImmutableTrees,
  evaluateCandidate,
  loadPolicy,
} from "../../scripts/trusted/verify-dependency-artifact-gate.mjs";
import { fixtureBlob, git, githubTreeResponse, readGitIndex, readGitTree, repoRoot } from "./_gitTreeFixtures.mjs";

const policy = loadPolicy(repoRoot);
const base = readGitIndex();
const localBlobs = new Map();
function blob(path, content, mode) {
  const entry = fixtureBlob(path, content, mode);
  localBlobs.set(entry.sha, Buffer.from(content));
  return entry;
}
function judge(before, after, overrides = {}) {
  return evaluateCandidate({
    policy, baseRef: "main", defaultBranch: "main",
    eventBaseSha: "a".repeat(40), eventHeadSha: "b".repeat(40),
    baseTreeEntries: before, treeEntries: after, changedFiles: [],
    readBlob: async sha => {
      if (!localBlobs.has(sha)) localBlobs.set(sha, git("cat-file", "blob", sha));
      return localBlobs.get(sha);
    },
    ...overrides,
  });
}

describe("real Git trees and trusted-mode continuity", () => {
  it("blocks the three-step trusted JWT symlink escape without executing either helper", async () => {
    const helper = "scripts/trusted/github-app-jwt.mjs";
    const destination = "scripts/shared-jwt-helper.mjs";
    expect(base.find(entry => entry.path === helper)).toMatchObject({ type: "blob", mode: "100644" });
    expect((await judge(base, base)).toJSON()).toMatchObject({ conclusion: "success", mode: "not-applicable" });

    const linked = [
      ...base.filter(entry => entry.path !== helper),
      blob(helper, "../shared-jwt-helper.mjs", "120000"),
      blob(destination, "export const reviewed = true;\n"),
    ];
    const substitution = await judge(base, linked);
    expect(substitution.failed).toBe(true);
    expect(substitution.messages.join("\n")).toMatch(/trusted.*regular blob|trusted.*approved mode/);

    const poisonedBase = linked;
    const later = [
      ...linked.filter(entry => entry.path !== destination),
      blob(destination, "export const reviewed = false;\n"),
    ];
    const followup = await judge(poisonedBase, later);
    expect(followup.failed).toBe(true);
    expect(followup.messages.join("\n")).toMatch(/base.*trusted.*regular blob|base.*trusted.*approved mode/);
  });

  it("accepts actual NUL-delimited ls-tree -r and GitHub-style recursive directories", async () => {
    const committedLeaves = readGitTree("HEAD");
    const recursive = readGitTree("HEAD", true);
    expect(recursive.some(entry => entry.type === "tree" && entry.mode === "040000")).toBe(true);
    expect(collectProtectedPathIdentityProblems(policy, recursive, recursive)).toEqual([]);
    expect(diffImmutableTrees(committedLeaves, recursive).changes).toEqual([]);
    const response = githubTreeResponse(committedLeaves);
    expect(response.sha).toBe(git("rev-parse", "HEAD^{tree}").toString("utf8").trim());
    const currentRecursive = githubTreeResponse(base).tree;
    expect((await judge(base, base)).failed).toBe(false);
    expect((await judge(currentRecursive, currentRecursive)).failed).toBe(false);
  });

  it("diffs leaf changes, not the incidental SHA changes of their ancestor directories", () => {
    const before = githubTreeResponse([fixtureBlob("docs/reference/index.md", "before\n")]).tree;
    const after = githubTreeResponse([fixtureBlob("docs/reference/index.md", "after\n")]).tree;
    expect(diffImmutableTrees(before, after).changes.map(change => change.filename)).toEqual(["docs/reference/index.md"]);
    expect(collectProtectedPathIdentityProblems(policy, before, after)).toEqual([]);
  });

  it("rejects real file/directory collisions and implied directory aliases", () => {
    for (const entries of [
      [fixtureBlob("package.json/child", "payload")],
      [fixtureBlob("docs/Prefix", "file"), fixtureBlob("docs/Prefix/child", "child")],
      [fixtureBlob("Docs/a.md", "a"), fixtureBlob("docs/b.md", "b")],
      [fixtureBlob("caf\u00e9/a.md", "a"), fixtureBlob("cafe\u0301/b.md", "b")],
    ]) {
      expect(collectProtectedPathIdentityProblems(policy, [], entries).length).toBeGreaterThan(0);
    }
  });

  it.each(["120000", "160000", "040000", "100755", "100600", "", undefined])(
    "rejects trusted material with unexpected mode %s on either immutable side", async mode => {
      const target = "scripts/trusted/github-app-jwt.mjs";
      const invalid = base.map(entry => entry.path === target
        ? { ...entry, mode, type: mode === "160000" ? "commit" : mode === "040000" ? "tree" : "blob" }
        : entry);
      expect((await judge(base, invalid)).failed).toBe(true);
      expect((await judge(invalid, base)).failed).toBe(true);
    },
  );

  it.each(policy.trustedPaths)("rejects a missing trusted file on either immutable side: %s", async trusted => {
    const missing = base.filter(entry => entry.path !== trusted);
    expect((await judge(base, missing)).failed, trusted).toBe(true);
    expect((await judge(missing, base)).failed, trusted).toBe(true);
  });

  it("validates tree response shape, object modes, object IDs and bounds without coercion", async () => {
    const response = githubTreeResponse(base);
    const readerFor = payload => createGitHubReader({
      apiUrl: "https://api.github.com", owner: "judeper", repo: "FSI-AgentGov",
      fetchImpl: async () => ({ ok: true, json: async () => payload }),
    });
    const realistic = await readerFor(response).readTree("a".repeat(40));
    expect((await judge(realistic.entries, realistic.entries)).failed).toBe(false);
    for (const malformed of [
      {}, { ...response, truncated: undefined }, { ...response, truncated: "false" },
      { ...response, tree: {} }, { ...response, sha: "short" },
    ]) {
      await expect(readerFor(malformed).readTree("a".repeat(40))).rejects.toThrow();
    }
    for (const mutation of [
      { type: "unknown" }, { type: "tree", mode: "100644" }, { sha: "short" }, { mode: "100600" },
    ]) {
      const entries = [...base, { ...fixtureBlob("docs/malformed.md", "x"), ...mutation }];
      expect((await judge(base, entries)).failed).toBe(true);
    }
    expect((await judge(base, base, { policy: { ...policy, limits: { ...policy.limits, maxTreeEntries: 1 } } })).failed).toBe(true);
  });
});
