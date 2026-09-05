/**
 * verify-required-checks.mjs
 *
 * Validates the committed plan for the one non-spoofable dependency-artifact
 * requirement. Generic required-check names are intentionally not treated as
 * authority: the planned ruleset binds its context to a dedicated GitHub App
 * integration ID at apply time.
 *
 * It retains the small workflow-name parser because existing tests use it for
 * matrix expansion. It must never promote a matching Actions job name into an
 * accepted source for `trusted-dependency-artifact`.
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
 *   0 — the planned expected-source binding is structurally sound
 *   1 — the plan is absent, malformed, or encodes a spoofable source
 */
import { existsSync, readdirSync, statSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join } from "node:path";
import {
  RULESET_PLAN_FILE,
  assertRulesetPlan,
  loadRulesetPlan,
} from "./trusted/trusted-dependency-ruleset.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..");
export const WORKFLOWS_DIR = join(repoRoot, ".github", "workflows");

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
  planFile = RULESET_PLAN_FILE,
  log = console.log,
  error = console.error,
} = {}) {
  if (!existsSync(planFile)) {
    error(`FAIL  expected-source ruleset plan is missing: ${planFile}`);
    return { ok: false, failed: 1, requiredCount: 1 };
  }
  try {
    const plan = loadRulesetPlan(planFile);
    assertRulesetPlan(plan);
    log(
      `OK    ${plan.expectedSource.checkName} is planned for dedicated GitHub App source binding; no name-only check is accepted.`,
    );
    return { ok: true, failed: 0, requiredCount: 1 };
  } catch (cause) {
    error(`FAIL  expected-source ruleset plan: ${cause.message}`);
    return { ok: false, failed: 1, requiredCount: 1 };
  }
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
