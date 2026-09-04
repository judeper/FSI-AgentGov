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
 *   We do not depend on js-yaml. We parse only the simple YAML constructs we
 *   use here:
 *   - jobs.<id>.name scalars
 *   - strategy.matrix with inline [a, b] lists
 *   - strategy.matrix with block lists (- a)
 *   - matrix placeholders in job names (${{ matrix.foo }})
 *   If we ever need full YAML support, swap in js-yaml.
 *
 * Exit codes:
 *   0 — all required contexts found (or branch-protection.json absent)
 *   1 — at least one required context not matched
 */
import { readFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join, relative } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..");
export const PROTECTION_FILE = join(repoRoot, ".github", "branch-protection.json");
export const PROTECTION_META_FILE = join(
  repoRoot,
  ".github",
  "branch-protection.meta.json",
);
export const WORKFLOWS_DIR = join(repoRoot, ".github", "workflows");

/*
 * Some required contexts are not workflow job display names. A
 * `pull_request_target` gate's automatic check run attaches to the default
 * branch commit rather than the pull request head, so it can never satisfy a
 * required status check; those gates publish a check run against the head SHA
 * through the Checks API instead.
 *
 * Such a context is only accepted when .github/branch-protection.meta.json
 * declares it AND the declared workflow, publisher, and policy all exist AND the
 * policy's own check-name field still equals the required context. That turns
 * a rename or a deleted gate into a loud failure instead of a silently
 * unenforced rule.
 */
export function resolveApiPublishedContexts({
  metaFile = PROTECTION_META_FILE,
  root = repoRoot,
} = {}) {
  const resolved = new Map();
  const problems = [];
  if (!existsSync(metaFile)) return { resolved, problems };

  const meta = JSON.parse(readFileSync(metaFile, "utf8"));
  for (const [context, declaration] of Object.entries(
    meta.api_published_contexts ?? {},
  )) {
    const missing = ["workflow", "publisher", "policy"].filter(key => {
      const value = declaration?.[key];
      return typeof value !== "string" || !existsSync(join(root, value));
    });
    if (missing.length > 0) {
      problems.push(`${context} — declared ${missing.join(", ")} not found on disk`);
      continue;
    }
    const policy = JSON.parse(
      readFileSync(join(root, declaration.policy), "utf8"),
    );
    const policyKey = declaration.policy_key ?? "checkName";
    if (policy[policyKey] !== context) {
      problems.push(
        `${context} — ${declaration.policy}.${policyKey} is "${policy[policyKey]}"`,
      );
      continue;
    }
    resolved.set(context, `${declaration.workflow} -> ${declaration.publisher}`);
  }
  return { resolved, problems };
}

function normalizeLine(rawLine) {
  return rawLine.replace(/\t/g, "  ");
}

function indentation(line) {
  const match = line.match(/^ */);
  return match ? match[0].length : 0;
}

function stripWrappingQuotes(value) {
  const trimmed = value.trim();
  if (trimmed.length < 2) {
    return trimmed;
  }
  if (
    (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
    (trimmed.startsWith("'") && trimmed.endsWith("'"))
  ) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function splitSimpleList(csvText) {
  const values = [];
  let current = "";
  let quote = null;
  for (let i = 0; i < csvText.length; i += 1) {
    const ch = csvText[i];
    if ((ch === "'" || ch === '"') && (i === 0 || csvText[i - 1] !== "\\")) {
      if (quote === ch) {
        quote = null;
      } else if (quote === null) {
        quote = ch;
      }
      current += ch;
      continue;
    }
    if (ch === "," && quote === null) {
      const cleaned = stripWrappingQuotes(current);
      if (cleaned.length) {
        values.push(cleaned);
      }
      current = "";
      continue;
    }
    current += ch;
  }
  const last = stripWrappingQuotes(current);
  if (last.length) {
    values.push(last);
  }
  return values;
}

function parseInlineList(value) {
  const trimmed = value.trim();
  const match = trimmed.match(/^\[(.*)\]$/);
  if (!match) {
    return null;
  }
  return splitSimpleList(match[1]);
}

function cartesianProduct(arrays) {
  if (!arrays.length) {
    return [[]];
  }
  return arrays.reduce(
    (acc, values) =>
      acc.flatMap(prefix => values.map(value => [...prefix, value])),
    [[]]
  );
}

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function expandMatrixPlaceholders(displayName, matrixDimensions) {
  const refs = [
    ...new Set(
      Array.from(
        displayName.matchAll(/\$\{\{\s*matrix\.([A-Za-z0-9_-]+)\s*\}\}/g),
        match => match[1]
      )
    ),
  ];

  if (!refs.length) {
    return [displayName];
  }

  const lists = refs.map(ref => matrixDimensions[ref]);
  if (lists.some(list => !Array.isArray(list) || list.length === 0)) {
    return [displayName];
  }

  const combos = cartesianProduct(lists);
  return combos.map(combo => {
    let expanded = displayName;
    refs.forEach((ref, index) => {
      const pattern = new RegExp(`\\$\\{\\{\\s*matrix\\.${escapeRegex(ref)}\\s*\\}\\}`, "g");
      expanded = expanded.replace(pattern, combo[index]);
    });
    return expanded;
  });
}

function extractJobBlocks(yamlText) {
  const lines = yamlText.split(/\r?\n/).map(normalizeLine);
  const blocks = [];
  let inJobs = false;
  let current = null;

  const flush = () => {
    if (current) {
      blocks.push(current);
      current = null;
    }
  };

  for (const line of lines) {
    const trimmed = line.trim();

    if (!inJobs) {
      if (/^jobs:\s*$/.test(line)) {
        inJobs = true;
      }
      continue;
    }

    if (indentation(line) === 0 && trimmed.length && !/^jobs:\s*$/.test(line)) {
      flush();
      inJobs = false;
      continue;
    }

    const jobKeyMatch = line.match(/^ {2}([A-Za-z0-9_-]+):\s*$/);
    if (jobKeyMatch) {
      flush();
      current = { key: jobKeyMatch[1], lines: [line] };
      continue;
    }

    if (current) {
      current.lines.push(line);
    }
  }

  flush();
  return blocks;
}

function extractJobName(jobBlock) {
  for (const line of jobBlock.lines.slice(1)) {
    const match = line.match(/^ {4}name:\s*(.+?)\s*$/);
    if (match) {
      return stripWrappingQuotes(match[1]);
    }
  }
  return jobBlock.key;
}

function extractMatrixDimensions(jobBlock) {
  const dims = {};
  let inStrategy = false;
  let inMatrix = false;
  let activeListKey = null;

  for (const line of jobBlock.lines.slice(1)) {
    const indent = indentation(line);
    const trimmed = line.trim();
    if (!trimmed.length || trimmed.startsWith("#")) {
      continue;
    }

    if (!inStrategy) {
      if (/^ {4}strategy:\s*$/.test(line)) {
        inStrategy = true;
      }
      continue;
    }

    if (indent <= 4) {
      inStrategy = false;
      inMatrix = false;
      activeListKey = null;
      continue;
    }

    if (!inMatrix) {
      if (/^ {6}matrix:\s*$/.test(line)) {
        inMatrix = true;
      }
      continue;
    }

    if (indent <= 6) {
      inMatrix = false;
      activeListKey = null;
      continue;
    }

    const dimMatch = line.match(/^ {8}([A-Za-z0-9_-]+):\s*(.*?)\s*$/);
    if (dimMatch) {
      const [, key, rest] = dimMatch;
      const inline = parseInlineList(rest);
      if (inline) {
        dims[key] = inline;
        activeListKey = null;
      } else if (rest.length === 0) {
        dims[key] = [];
        activeListKey = key;
      } else {
        activeListKey = null;
      }
      continue;
    }

    if (activeListKey) {
      const itemMatch = line.match(/^ {10}-\s+(.+?)\s*$/);
      if (itemMatch) {
        dims[activeListKey].push(stripWrappingQuotes(itemMatch[1]));
        continue;
      }
      if (indent <= 8) {
        activeListKey = null;
      }
    }
  }

  for (const [key, values] of Object.entries(dims)) {
    if (!Array.isArray(values) || values.length === 0) {
      delete dims[key];
    }
  }

  return dims;
}

/**
 * Extract job display names from a workflow YAML file.
 * Expands simple matrix placeholders when strategy.matrix provides list values.
 */
export function extractJobNames(yamlText) {
  const names = [];
  for (const jobBlock of extractJobBlocks(yamlText)) {
    const displayName = extractJobName(jobBlock);
    const matrixDims = extractMatrixDimensions(jobBlock);
    const expanded = expandMatrixPlaceholders(displayName, matrixDims);
    names.push(...expanded);
  }
  return names;
}

export function listWorkflowFiles(workflowsDir = WORKFLOWS_DIR) {
  return readdirSync(workflowsDir)
    .filter(file => file.endsWith(".yml") || file.endsWith(".yaml"))
    .map(file => join(workflowsDir, file))
    .filter(file => statSync(file).isFile());
}

export function verifyRequiredChecks({
  protectionFile = PROTECTION_FILE,
  metaFile = PROTECTION_META_FILE,
  workflowsDir = WORKFLOWS_DIR,
  root = repoRoot,
  log = console.log,
  error = console.error,
} = {}) {
  if (!existsSync(protectionFile)) {
    log("branch-protection.json not yet created; nothing to verify.");
    return { ok: true, failed: 0, requiredCount: 0 };
  }

  const protection = JSON.parse(readFileSync(protectionFile, "utf8"));
  const required =
    (protection.required_status_checks && protection.required_status_checks.contexts) ||
    protection.contexts ||
    [];

  if (!required.length) {
    log("No required_status_checks.contexts listed; nothing to verify.");
    return { ok: true, failed: 0, requiredCount: 0 };
  }

  if (!existsSync(workflowsDir)) {
    error(`FAIL: ${workflowsDir} does not exist but contexts are required:\n  - ${required.join("\n  - ")}`);
    return { ok: false, failed: required.length, requiredCount: required.length };
  }

  const workflowFiles = listWorkflowFiles(workflowsDir);
  const allJobNames = new Map(); // displayName -> [files...]
  for (const wf of workflowFiles) {
    const text = readFileSync(wf, "utf8");
    const names = extractJobNames(text);
    for (const name of names) {
      if (!allJobNames.has(name)) {
        allJobNames.set(name, []);
      }
      allJobNames.get(name).push(wf);
    }
  }

  let failed = 0;
  const { resolved: apiPublished, problems } = resolveApiPublishedContexts({
    metaFile,
    root,
  });
  for (const problem of problems) {
    failed += 1;
    error(`FAIL  ${problem}`);
  }

  for (const context of required) {
    if (allJobNames.has(context)) {
      const where = allJobNames
        .get(context)
        .map(file => relative(repoRoot, file).replace(/\\/g, "/"))
        .join(", ");
      log(`OK    ${context}  (${where})`);
    } else if (apiPublished.has(context)) {
      log(`OK    ${context}  (check-run API: ${apiPublished.get(context)})`);
    } else {
      failed += 1;
      error(
        `FAIL  ${context}  — no workflow job has this display name and no api_published_contexts declaration covers it`,
      );
    }
  }

  if (failed > 0) {
    error(`\nverify-required-checks: ${failed} unmatched context(s).`);
    error("Tip: required status checks match jobs.<key>.name (or the job key if name is omitted).");
    return { ok: false, failed, requiredCount: required.length };
  }

  log(`\nverify-required-checks: all ${required.length} required context(s) matched.`);
  return { ok: true, failed: 0, requiredCount: required.length };
}

export function runCli() {
  const result = verifyRequiredChecks();
  return result.ok ? 0 : 1;
}

export function isCliExecution(argv = process.argv, moduleUrl = import.meta.url) {
  if (!argv || !argv[1]) {
    return false;
  }
  return pathToFileURL(argv[1]).href === moduleUrl;
}

if (isCliExecution()) {
  process.exit(runCli());
}
