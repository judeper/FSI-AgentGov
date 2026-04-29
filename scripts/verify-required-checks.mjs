#!/usr/bin/env node
/**
 * verify-required-checks.mjs
 *
 * Asserts that every context listed in
 * .github/branch-protection.json -> required_status_checks.contexts
 * matches a workflow job's *display name* (the `jobs.<key>.name` field, or
 * the job key itself if no `name:` is set).
 *
 * GITHUB FOOTGUN:
 *   Required status checks are matched against the job's display name. A
 *   single typo in branch-protection.json (or renaming a job's `name:`
 *   without updating protection) silently means "no check is required" —
 *   the PR can be merged green without ever running CI for that context.
 *   This verifier turns that silent failure into a loud one.
 *
 * LIMITATIONS:
 *   We do not depend on js-yaml. Instead we extract `name:` lines that sit
 *   under `jobs:` blocks via regex. This is "good enough" for the simple
 *   single-document workflows in this repo (no anchors, no folded scalars
 *   for job names). If we ever need stricter parsing, swap in js-yaml.
 *
 * Exit codes:
 *   0 — all required contexts found (or branch-protection.json absent)
 *   1 — at least one required context not matched
 */
import { readFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..");
const PROTECTION_FILE = join(repoRoot, ".github", "branch-protection.json");
const WORKFLOWS_DIR = join(repoRoot, ".github", "workflows");

if (!existsSync(PROTECTION_FILE)) {
  console.log("branch-protection.json not yet created; nothing to verify.");
  process.exit(0);
}

const protection = JSON.parse(readFileSync(PROTECTION_FILE, "utf8"));
const required =
  (protection.required_status_checks && protection.required_status_checks.contexts) ||
  protection.contexts ||
  [];

if (!required.length) {
  console.log("No required_status_checks.contexts listed; nothing to verify.");
  process.exit(0);
}

if (!existsSync(WORKFLOWS_DIR)) {
  console.error(`FAIL: ${WORKFLOWS_DIR} does not exist but contexts are required:\n  - ${required.join("\n  - ")}`);
  process.exit(1);
}

const workflowFiles = readdirSync(WORKFLOWS_DIR)
  .filter(f => f.endsWith(".yml") || f.endsWith(".yaml"))
  .map(f => join(WORKFLOWS_DIR, f))
  .filter(f => statSync(f).isFile());

/**
 * Extract job display names from a workflow YAML file.
 * Strategy: find the top-level `jobs:` block, then for each job key
 * (2-space indent under jobs:), capture an optional `name:` directive at
 * 4-space indent. If no `name:` is present, the job key is the display name.
 */
function extractJobNames(yamlText) {
  const lines = yamlText.split(/\r?\n/);
  const names = [];
  let inJobs = false;
  let currentJobKey = null;
  let currentJobName = null;

  const flush = () => {
    if (currentJobKey) {
      names.push(currentJobName ?? currentJobKey);
    }
    currentJobKey = null;
    currentJobName = null;
  };

  for (const raw of lines) {
    const line = raw.replace(/\t/g, "  ");
    if (/^jobs:\s*$/.test(line)) {
      inJobs = true;
      continue;
    }
    if (!inJobs) continue;
    // A new top-level key (no leading space) ends the jobs block.
    if (/^\S/.test(line) && !/^\s/.test(line) && line.trim().length) {
      flush();
      inJobs = false;
      continue;
    }
    // Job key: exactly 2 spaces of indent, then `key:`
    const jobKeyMatch = line.match(/^ {2}([A-Za-z0-9_\-]+):\s*$/);
    if (jobKeyMatch) {
      flush();
      currentJobKey = jobKeyMatch[1];
      currentJobName = null;
      continue;
    }
    // Job-scoped name: 4 spaces of indent, then `name:`
    const nameMatch = line.match(/^ {4}name:\s*(.+?)\s*$/);
    if (nameMatch && currentJobKey && currentJobName === null) {
      let val = nameMatch[1];
      // Strip surrounding quotes.
      if ((val.startsWith('"') && val.endsWith('"')) ||
          (val.startsWith("'") && val.endsWith("'"))) {
        val = val.slice(1, -1);
      }
      currentJobName = val;
    }
  }
  flush();
  return names;
}

const allJobNames = new Map(); // displayName -> [files...]
for (const wf of workflowFiles) {
  const text = readFileSync(wf, "utf8");
  const names = extractJobNames(text);
  for (const n of names) {
    if (!allJobNames.has(n)) allJobNames.set(n, []);
    allJobNames.get(n).push(wf);
  }
}

let failed = 0;
for (const ctx of required) {
  if (allJobNames.has(ctx)) {
    const where = allJobNames.get(ctx).map(f => f.replace(repoRoot + "\\", "").replace(repoRoot + "/", "")).join(", ");
    console.log(`OK    ${ctx}  (${where})`);
  } else {
    failed += 1;
    console.error(`FAIL  ${ctx}  — no workflow job has this display name`);
  }
}

if (failed > 0) {
  console.error(`\nverify-required-checks: ${failed} unmatched context(s).`);
  console.error("Tip: required status checks match jobs.<key>.name (or the job key if name is omitted).");
  process.exit(1);
}
console.log(`\nverify-required-checks: all ${required.length} required context(s) matched.`);
process.exit(0);
