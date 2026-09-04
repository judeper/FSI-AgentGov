/*
 * Publishes the authoritative `trusted-dependency-artifact` check run.
 *
 * WHY THIS EXISTS
 * ---------------
 * A `pull_request_target` workflow runs from the default branch and its
 * automatically created check run is attached to that branch's commit, not to
 * the pull request head. Branch rulesets evaluate required status checks on the
 * pull request head SHA, so a `pull_request_target` job's own check cannot be
 * required. This publisher closes that gap explicitly: it creates a check run
 * whose `head_sha` is the pull request head from the event payload, using a
 * stable name that a ruleset can require.
 *
 * TRUST RULES
 * -----------
 *   - This is the only job in the gate holding a write scope (`checks: write`).
 *     It never reads the candidate tree, never checks out candidate code, and
 *     never executes anything the candidate supplied.
 *   - The verdict arrives base64-encoded from the validate job, so no candidate
 *     derived text is ever interpolated into YAML, a shell, or a template.
 *   - The verdict is re-validated here against a strict schema and re-sanitized
 *     before it reaches the check-run summary.
 *   - Any uncertainty — missing verdict, malformed verdict, a validate job that
 *     did not report success — publishes `failure`. There is no path that
 *     reports success on incomplete evidence.
 */

import { readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const defaultRepoRoot = resolve(__dirname, "..", "..");

const FULL_OBJECT_ID = /^[0-9a-f]{40}$/;
const SAFE_TEXT = /[^A-Za-z0-9 ._/@:+()',=-]/g;
const REPOSITORY = /^([A-Za-z0-9][A-Za-z0-9._-]{0,99})\/([A-Za-z0-9][A-Za-z0-9._-]{0,99})$/;
const ALLOWED_MODES = new Set([
  "artifact",
  "guard-only",
  "policy-only",
  "not-applicable",
  "mixed-trusted-and-guarded",
  "unsafe-path",
  "unbounded-change",
  "invalid-base",
  "invalid-event",
  "gate-error",
  "unknown",
]);

export function sanitizeLine(value, maxLength = 200) {
  return String(value ?? "")
    .replace(/\s+/g, " ")
    .replace(SAFE_TEXT, "?")
    .slice(0, maxLength);
}

/*
 * Re-parse the validate job's verdict. Anything unexpected degrades to a
 * failing verdict rather than being trusted or repaired.
 */
export function decodeVerdict(encoded, jobResult) {
  if (jobResult !== "success" && jobResult !== "failure") {
    return {
      conclusion: "failure",
      mode: "gate-error",
      messages: [`validate job reported '${sanitizeLine(jobResult, 40)}'`],
    };
  }
  let parsed;
  try {
    parsed = JSON.parse(Buffer.from(String(encoded ?? ""), "base64").toString("utf8"));
  } catch {
    return {
      conclusion: "failure",
      mode: "gate-error",
      messages: ["validate job produced no readable verdict"],
    };
  }
  if (
    !parsed ||
    typeof parsed !== "object" ||
    (parsed.conclusion !== "success" && parsed.conclusion !== "failure") ||
    !ALLOWED_MODES.has(parsed.mode) ||
    !Array.isArray(parsed.messages)
  ) {
    return {
      conclusion: "failure",
      mode: "gate-error",
      messages: ["validate job produced a malformed verdict"],
    };
  }
  /* A verdict may only claim success when the job that produced it succeeded. */
  const conclusion = jobResult === "success" ? parsed.conclusion : "failure";
  return {
    conclusion,
    mode: parsed.mode,
    messages: parsed.messages.slice(0, 40).map((message) => sanitizeLine(message)),
  };
}

export function buildCheckRun({ policy, headSha, verdict, runUrl }) {
  const passed = verdict.conclusion === "success";
  const title = passed
    ? `Base-controlled validation passed (${verdict.mode})`
    : `Base-controlled validation failed (${verdict.mode})`;
  const lines = [
    "This check is produced by the protected default branch.",
    "The pull request head is read as data only; none of its workflows, verifiers,",
    "hashes, tests, package scripts or documentation influence this result.",
    "",
    `Mode: ${sanitizeLine(verdict.mode, 64)}`,
    `Head: ${headSha}`,
    "",
    "Findings:",
    ...(verdict.messages.length > 0
      ? verdict.messages.map((message) => `- ${message}`)
      : ["- (none reported)"]),
  ];
  if (runUrl) lines.push("", `Run: ${sanitizeLine(runUrl, 200)}`);
  return {
    name: policy.checkName,
    head_sha: headSha,
    status: "completed",
    conclusion: passed ? "success" : "failure",
    output: { title: sanitizeLine(title, 200), summary: lines.join("\n").slice(0, 60000) },
  };
}

export async function main({ fetchImpl = fetch } = {}) {
  const repoRoot = process.env.GATE_REPO_ROOT || defaultRepoRoot;
  const policy = JSON.parse(
    readFileSync(
      join(repoRoot, ".github", "trusted-policy", "dependency-artifact-policy.json"),
      "utf8",
    ),
  );

  const repository = String(process.env.GATE_REPOSITORY ?? "");
  const match = repository.match(REPOSITORY);
  if (!match) throw new Error("repository coordinates failed validation");
  const headSha = String(process.env.GATE_HEAD_SHA ?? "");
  if (!FULL_OBJECT_ID.test(headSha)) throw new Error("head SHA failed validation");
  const token = process.env.GATE_TOKEN;
  if (!token) throw new Error("missing checks token");

  const verdict = decodeVerdict(process.env.GATE_VERDICT, process.env.GATE_JOB_RESULT);
  const body = buildCheckRun({
    policy,
    headSha,
    verdict,
    runUrl: process.env.GATE_RUN_URL,
  });

  const apiUrl = (process.env.GITHUB_API_URL || "https://api.github.com").replace(/\/+$/, "");
  const response = await fetchImpl(`${apiUrl}/repos/${match[1]}/${match[2]}/check-runs`, {
    method: "POST",
    headers: {
      accept: "application/vnd.github+json",
      "x-github-api-version": "2022-11-28",
      "user-agent": "trusted-dependency-artifact-gate",
      "content-type": "application/json",
      authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`could not publish check run: GitHub API ${response.status}`);
  }

  process.stdout.write(
    `${policy.checkName}: ${body.conclusion} (${verdict.mode}) on ${headSha}\n`,
  );
  /* The published check run, not this job, is the required gate. Exiting
   * non-zero here would only hide a successfully published failure. */
  return 0;
}

export function isCliExecution(argv = process.argv, moduleUrl = import.meta.url) {
  if (!argv || !argv[1]) return false;
  return pathToFileURL(argv[1]).href === moduleUrl;
}

if (isCliExecution()) {
  process.exit(await main());
}
