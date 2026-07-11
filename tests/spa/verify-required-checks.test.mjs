import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { extractJobNames } from "../../scripts/verify-required-checks.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..", "..");

describe("verify-required-checks matrix expansion", () => {
  it("expands real CodeQL matrix job names", () => {
    const codeqlPath = join(repoRoot, ".github", "workflows", "codeql.yml");
    const codeql = readFileSync(codeqlPath, "utf8");
    const names = extractJobNames(codeql);

    expect(names).toContain("Analyze (python)");
    expect(names).toContain("Analyze (javascript)");
    expect(names).not.toContain("Analyze (${{ matrix.language }})");
  });

  it("expands multidimensional cartesian products across inline and block lists", () => {
    const yaml = `
jobs:
  build:
    name: Build (\${{ matrix.os }} / \${{ matrix.node }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        os:
          - ubuntu-latest
          - windows-latest
        node: [20, 22]
    steps:
      - run: echo test
`;
    const names = extractJobNames(yaml).sort();

    expect(names).toEqual([
      "Build (ubuntu-latest / 20)",
      "Build (ubuntu-latest / 22)",
      "Build (windows-latest / 20)",
      "Build (windows-latest / 22)",
    ]);
  });

  it("keeps non-matrix names and unnamed job keys", () => {
    const yaml = `
jobs:
  lint:
    runs-on: ubuntu-latest
  build:
    name: Build docs
    runs-on: ubuntu-latest
    strategy:
      matrix:
        os:
          - ubuntu-latest
          - windows-latest
        node: [20, 22]
    steps:
      - run: echo hello
`;
    const names = extractJobNames(yaml);

    expect(names).toContain("lint");
    expect(names).toContain("Build docs");
    expect(names).not.toContain("Build docs (ubuntu-latest / 20)");
  });

  it("integration: CLI exits zero and emits no FAIL lines", () => {
    const scriptPath = join(repoRoot, "scripts", "verify-required-checks.mjs");
    const result = spawnSync("node", [scriptPath], {
      cwd: repoRoot,
      encoding: "utf8",
    });

    const combinedOutput = `${result.stdout ?? ""}\n${result.stderr ?? ""}`;
    expect(result.status).toBe(0);
    expect(combinedOutput).not.toMatch(/(^|\n)FAIL\s+/);
  });
});
