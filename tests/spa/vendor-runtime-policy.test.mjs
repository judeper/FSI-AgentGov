import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
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
});
