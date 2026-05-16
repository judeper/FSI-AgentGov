/**
 * generate-render-expectations.mjs
 *
 * Scans docs/**\/*.md and builds a per-page oracle used by Playwright spec 31:
 *   - expected_mermaid_count  : fenced ```mermaid blocks
 *   - expected_diagram_links  : resolved paths to images/diagrams/*.png|svg
 *   - expected_asset_links    : resolved paths to downloads/*.xlsx
 *
 * Why: the site has ~40 Mermaid blocks that render as raw <pre> (CSP blocks
 * unpkg.com) and ~30 "Download diagram" links that 404 (mkdocs exclude_docs:
 * images/). A positive oracle detects both regressions and silent removals.
 *
 * Usage:
 *   node scripts/generate-render-expectations.mjs --out tests/e2e/fixtures/render-expectations.json
 *   node scripts/generate-render-expectations.mjs --out <path> --check
 *
 * The --check flag exits non-zero if re-generating would change the file
 * (ignoring the generated_at timestamp). Used by CI for idempotency checks.
 *
 * Dependencies: Node built-ins only (fs, path, url). No npm packages needed.
 */

import { readFileSync, writeFileSync, readdirSync, existsSync } from "fs";
import { join, relative, dirname, resolve } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const REPO_ROOT = resolve(__dirname, "..");
const DOCS_ROOT = join(REPO_ROOT, "docs");

// Confirmed in mkdocs.yml: use_directory_urls is not set → defaults to true.
// site_url from mkdocs.yml line 4.
const SITE_URL = "https://judeper.github.io/FSI-AgentGov/";

// Top-level docs/ subdirectories excluded from the published site
// (per mkdocs.yml exclude_docs block). We skip scanning them entirely.
const SKIP_TOP_DIRS = new Set(["images", "scripts", "templates", ".snippets"]);

// ── File collection ──────────────────────────────────────────────────────────

/**
 * Recursively collect all *.md files under `dir`, skipping excluded subtrees.
 */
function collectMdFiles(dir, root, results = []) {
  const entries = readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      // Only check top-level dirs against the skip list
      const relToRoot = relative(root, full);
      const topLevel = relToRoot.split(/[\\/]/)[0];
      if (SKIP_TOP_DIRS.has(topLevel)) continue;
      collectMdFiles(full, root, results);
    } else if (entry.isFile() && entry.name.endsWith(".md")) {
      results.push(full);
    }
  }
  return results;
}

// ── Frontmatter ─────────────────────────────────────────────────────────────

/**
 * Returns true if the file has `draft: true` in its YAML frontmatter.
 */
function isDraft(content) {
  if (!content.startsWith("---")) return false;
  const closeIdx = content.indexOf("\n---", 3);
  if (closeIdx === -1) return false;
  const fm = content.slice(0, closeIdx + 4);
  return /^\s*draft\s*:\s*true\s*$/im.test(fm);
}

// ── URL path conversion ──────────────────────────────────────────────────────

/**
 * Convert an absolute source .md path to its deployed URL path segment
 * (without the site base URL). Applies MkDocs use_directory_urls=true logic.
 *
 * Examples:
 *   docs/index.md                                   → /
 *   docs/getting-started/index.md                   → /getting-started/
 *   docs/controls/pillar-1-security/1.1-foo.md      → /controls/pillar-1-security/1.1-foo/
 */
function sourcePathToUrlPath(absPath) {
  // Normalise to forward slashes for consistency
  const rel = relative(DOCS_ROOT, absPath).replace(/\\/g, "/");

  if (rel === "index.md") return "/";
  if (rel.endsWith("/index.md")) return "/" + rel.slice(0, -"index.md".length);
  return "/" + rel.slice(0, -".md".length) + "/";
}

// ── Link resolution ──────────────────────────────────────────────────────────

/**
 * Resolve a markdown link href to a site-root-relative path (docs/ stripped).
 * Returns null for external links or links that escape the docs tree.
 *
 * `absSourcePath` is the absolute path of the .md file containing the link.
 */
function resolveHref(href, absSourcePath) {
  // Strip any fragment or query string
  const clean = href.split("#")[0].split("?")[0].trim();
  if (!clean) return null;

  // External links
  if (/^https?:\/\//i.test(clean) || clean.startsWith("//")) return null;

  if (clean.startsWith("/")) {
    // Absolute path — strip the GitHub Pages base if present
    const base = "/FSI-AgentGov/";
    const stripped = clean.startsWith(base) ? clean.slice(base.length) : clean.slice(1);
    return stripped || null;
  }

  // Relative path — resolve from the source file's directory
  const srcDir = dirname(absSourcePath);
  const resolved = resolve(srcDir, clean);
  const rel = relative(DOCS_ROOT, resolved).replace(/\\/g, "/");

  // Reject if it escapes the docs tree
  if (rel.startsWith("..")) return null;

  return rel;
}

// ── Counters / extractors ────────────────────────────────────────────────────

/**
 * Count fenced ```mermaid code blocks (case-insensitive tag).
 * Matches ``` mermaid (with optional leading whitespace).
 */
function countMermaidBlocks(content) {
  // Match opening fences only; case-insensitive
  const matches = content.match(/^[ \t]*```+\s*mermaid\b/gim);
  return matches ? matches.length : 0;
}

/**
 * Find all markdown links pointing to images/diagrams/*.png or *.svg.
 * Returns an array of site-root-relative paths, deduplicated.
 *
 * Handles: relative (../images/..., ../../images/...), absolute (/FSI-AgentGov/images/...)
 */
function findDiagramLinks(content, absSourcePath) {
  // Match [any text](href) where href contains images/diagrams/ and ends with .png or .svg
  const re = /\[[^\]]*\]\(([^)]*images\/diagrams\/[^)\s]*\.(?:png|svg))(?:\s[^)]*)?\)/gi;
  const seen = new Set();
  let m;
  while ((m = re.exec(content)) !== null) {
    const resolved = resolveHref(m[1], absSourcePath);
    if (resolved) seen.add(resolved);
  }
  return [...seen].sort();
}

/**
 * Find all markdown links pointing to downloads/*.xlsx.
 * Returns an array of site-root-relative paths, deduplicated.
 */
function findAssetLinks(content, absSourcePath) {
  const re = /\[[^\]]*\]\(([^)]*downloads\/[^)\s]*\.xlsx)(?:\s[^)]*)?\)/gi;
  const seen = new Set();
  let m;
  while ((m = re.exec(content)) !== null) {
    const resolved = resolveHref(m[1], absSourcePath);
    if (resolved) seen.add(resolved);
  }
  return [...seen].sort();
}

// ── Main generation ──────────────────────────────────────────────────────────

function generate() {
  const files = collectMdFiles(DOCS_ROOT, DOCS_ROOT);

  // Sort for deterministic output
  files.sort();

  const pages = {};

  for (const absPath of files) {
    const content = readFileSync(absPath, "utf8");

    if (isDraft(content)) continue;

    const urlPath = sourcePathToUrlPath(absPath);
    const sourceMd = "docs/" + relative(DOCS_ROOT, absPath).replace(/\\/g, "/");

    pages[urlPath] = {
      source_md: sourceMd,
      expected_mermaid_count: countMermaidBlocks(content),
      expected_diagram_links: findDiagramLinks(content, absPath),
      expected_asset_links: findAssetLinks(content, absPath),
    };
  }

  // Summary rollup
  const pageValues = Object.values(pages);
  const totalMermaid = pageValues.reduce((s, p) => s + p.expected_mermaid_count, 0);
  const pagesWithMermaid = pageValues.filter((p) => p.expected_mermaid_count > 0).length;
  const totalDiagramLinks = pageValues.reduce((s, p) => s + p.expected_diagram_links.length, 0);
  const totalAssetLinks = pageValues.reduce((s, p) => s + p.expected_asset_links.length, 0);

  return {
    generated_at: new Date().toISOString(),
    source_root: "docs/",
    site_url: SITE_URL,
    pages,
    summary: {
      total_pages: pageValues.length,
      pages_with_mermaid: pagesWithMermaid,
      total_mermaid_blocks: totalMermaid,
      total_diagram_links: totalDiagramLinks,
      total_asset_links: totalAssetLinks,
    },
  };
}

// ── CLI entry point ──────────────────────────────────────────────────────────

function parseArgs(argv) {
  const outIdx = argv.indexOf("--out");
  return {
    out: outIdx !== -1 ? argv[outIdx + 1] : null,
    check: argv.includes("--check"),
  };
}

/**
 * Normalise a fixture JSON string for structural comparison (strips timestamp).
 */
function normaliseForCompare(jsonStr) {
  const obj = JSON.parse(jsonStr);
  obj.generated_at = "";
  return JSON.stringify(obj, null, 2);
}

const { out, check } = parseArgs(process.argv.slice(2));

if (!out) {
  console.error(
    "Usage: node scripts/generate-render-expectations.mjs --out <path> [--check]",
  );
  process.exit(1);
}

const data = generate();
const newJson = JSON.stringify(data, null, 2) + "\n";

if (check) {
  if (!existsSync(out)) {
    console.error(`[check] FAIL — file does not exist: ${out}`);
    process.exit(1);
  }
  const existing = readFileSync(out, "utf8");
  if (normaliseForCompare(existing) !== normaliseForCompare(newJson)) {
    console.error(
      `[check] FAIL — ${out} is stale; re-run without --check to regenerate.`,
    );
    process.exit(1);
  }
  console.log("[check] OK — render-expectations.json is up to date.");
} else {
  writeFileSync(out, newJson, "utf8");
  console.log(`[generate] Written: ${out}`);
  console.log("[summary]", JSON.stringify(data.summary, null, 2));
}
