import { describe, expect, it } from "vitest";
import { execFileSync } from "node:child_process";
import {
  cpSync,
  existsSync,
  mkdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  SHEETJS_POLICY,
  verifyVendoredRuntime,
} from "../../scripts/verify-vendored-runtime.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..", "..");

function readInputs() {
  return {
    manifestSrc: readFileSync(
      join(repoRoot, "docs", "javascripts", "lib", "VENDOR-MANIFEST.md"),
      "utf8",
    ),
    packageJsonSrc: readFileSync(join(repoRoot, "package.json"), "utf8"),
    packageLockSrc: readFileSync(join(repoRoot, "package-lock.json"), "utf8"),
    appSrc: readFileSync(
      join(repoRoot, "docs", "javascripts", "assessment-app.js"),
      "utf8",
    ),
    vendorBytes: readFileSync(
      join(repoRoot, "docs", "javascripts", SHEETJS_POLICY.file),
    ),
  };
}

describe("shipped vendored runtime policy", () => {
  it("accepts the reviewed official SheetJS artifact and all consistency links", () => {
    const result = verifyVendoredRuntime(readInputs());
    expect(result).toEqual({ ok: true, errors: [] });
  });

  it("rejects a known vulnerable SheetJS version in the inventory", () => {
    const inputs = readInputs();
    inputs.manifestSrc = inputs.manifestSrc.replace(
      /(\|\s*SheetJS\s*\|\s*)0\.20\.3/,
      (_, prefix) => `${prefix}0.18.5`,
    );

    const result = verifyVendoredRuntime(inputs);
    expect(result.ok).toBe(false);
    expect(result.errors.join("\n")).toMatch(/0\.18\.x|not approved/);
  });

  it("rejects runtime hash drift even when metadata is unchanged", () => {
    const inputs = readInputs();
    inputs.vendorBytes = Buffer.from(inputs.vendorBytes);
    inputs.vendorBytes[0] ^= 0xff;

    const result = verifyVendoredRuntime(inputs);
    expect(result.ok).toBe(false);
    expect(result.errors.join("\n")).toMatch(/SHA-256|SRI/);
  });

  it("does not execute fast-uri regressions when the installed payload differs", () => {
    const scratchRoot = join(
      repoRoot,
      "maintainers-local",
      "tests",
      "fast-uri-tampered-install",
    );
    const fixtureRoot = join(scratchRoot, "repo");
    const markerPath = join(scratchRoot, "tamper-marker.txt");

    rmSync(scratchRoot, { recursive: true, force: true });
    try {
      mkdirSync(join(fixtureRoot, "scripts"), { recursive: true });
      mkdirSync(join(fixtureRoot, "vendor", "npm", "fast-uri"), {
        recursive: true,
      });
      mkdirSync(join(fixtureRoot, "node_modules"), { recursive: true });
      cpSync(
        join(repoRoot, "scripts", "verify-fast-uri-artifact.mjs"),
        join(fixtureRoot, "scripts", "verify-fast-uri-artifact.mjs"),
      );
      cpSync(join(repoRoot, "package.json"), join(fixtureRoot, "package.json"));
      cpSync(
        join(repoRoot, "package-lock.json"),
        join(fixtureRoot, "package-lock.json"),
      );
      cpSync(
        join(repoRoot, "vendor", "npm", "fast-uri", "3.1.7"),
        join(fixtureRoot, "vendor", "npm", "fast-uri", "3.1.7"),
        { recursive: true },
      );
      cpSync(
        join(repoRoot, "node_modules", "fast-uri"),
        join(fixtureRoot, "node_modules", "fast-uri"),
        { recursive: true },
      );
      writeFileSync(
        join(fixtureRoot, "node_modules", "fast-uri", "index.js"),
        [
          `require("node:fs").writeFileSync(${JSON.stringify(markerPath)}, "executed");`,
          "module.exports = {};",
          "",
        ].join("\n"),
      );

      let failure;
      try {
        execFileSync(
          process.execPath,
          [join(fixtureRoot, "scripts", "verify-fast-uri-artifact.mjs")],
          {
            cwd: fixtureRoot,
            encoding: "utf8",
            stdio: ["ignore", "pipe", "pipe"],
          },
        );
      } catch (error) {
        failure = error;
      }

      expect(failure).toBeDefined();
      expect(failure.status).not.toBe(0);
      expect(String(failure?.stderr ?? "")).toContain(
        "FAIL: installed fast-uri file 'index.js' differs from the reviewed artifact",
      );
      expect(String(failure?.stderr ?? "")).toContain(
        "FAIL: fast-uri security regressions skipped because installed payload differs from the reviewed artifact",
      );
      expect(existsSync(markerPath)).toBe(false);
    } finally {
      rmSync(scratchRoot, { recursive: true, force: true });
    }
  });
});
