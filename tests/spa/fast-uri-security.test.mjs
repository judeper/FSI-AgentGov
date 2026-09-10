import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import fastUri from "fast-uri";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..", "..");
const expectedIntegrity =
  "sha512-dOvZVzjdZdz7phd9v6jCbwxrBW3fK6n8Rc0CtdmM4bumzMnxywBYhuph6J819RRw/ku+rLbelwfMunktuzVVHg==";

describe("fast-uri security release", () => {
  it("locks and installs the reviewed 3.1.7 package", () => {
    const lock = JSON.parse(
      readFileSync(join(repoRoot, "package-lock.json"), "utf8"),
    );
    const installed = JSON.parse(
      readFileSync(join(repoRoot, "node_modules", "fast-uri", "package.json"), "utf8"),
    );
    const locked = lock.packages["node_modules/fast-uri"];

    expect(locked.version).toBe("3.1.7");
    expect(locked.integrity).toBe(expectedIntegrity);
    expect(installed.version).toBe("3.1.7");
  });

  it("rejects percent-encoded scheme authority injection", () => {
    const input = "%2f%2fevil.example:/pwn";

    expect(fastUri.parse(input).error).toBe("URI scheme is malformed.");
    expect(fastUri.normalize(input)).toBe(input);
  });

  it("does not double-decode an encoded hostname", () => {
    const input =
      "http://%256c%256f%2563%2561%256c%2568%256f%2573%2574/";

    expect(fastUri.normalize(input)).toBe(input);
    expect(fastUri.parse(fastUri.normalize(input)).host).not.toBe("localhost");
  });

  it("rejects malformed bracketed IPv6 literals", () => {
    const input = "http://[::not-valid]/private";

    expect(fastUri.parse(input).error).toBe("URI host is malformed.");
    expect(fastUri.normalize(input)).toBe(input);
  });

  it("canonicalizes scheme-relative IDN hosts before policy checks", () => {
    const output = fastUri.resolve(
      "http://trusted.example/base",
      "//127。0。0。1/private",
    );

    expect(output).toBe("http://127.0.0.1/private");
    expect(fastUri.parse(output).host).toBe("127.0.0.1");
  });

  it("rejects authority injection through a malformed port", () => {
    expect(() =>
      fastUri.serialize({
        scheme: "http",
        host: "trusted.example",
        port: "@127.0.0.1:8124",
        path: "/app",
      }),
    ).toThrow(/URI port is malformed\./);
  });

  it("rejects unclosed-bracket host confusion", () => {
    const input = "http://user@[@127.0.0.1:8123/admin";

    expect(fastUri.parse(input).error).toBe("URI host is malformed.");
    expect(fastUri.equal(input, input)).toBe(false);
  });
});
