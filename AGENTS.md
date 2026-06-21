# AGENTS.md - Instructions for AI Agents

This file provides guidance for autonomous AI agents working on this repository. It is tool-neutral and readable by Codex CLI and GitHub Copilot.

## Project Overview

**FSI Agent Governance Framework v1.6.2** — A governance framework for Microsoft 365 AI agents in US financial services organizations.

- **79 controls** across 4 pillars (Security, Management, Reporting, SharePoint)
- **3 governance zones** (Personal Productivity, Team Collaboration, Enterprise Managed)
- **3-layer documentation** (Framework → Controls → Playbooks)
- **Target regulations:** FINRA 4511/3110, SEC 17a-3/4, SOX 302/404, GLBA 501(b), OCC Bulletin 2026-13 (formerly OCC 2011-12), Fed SR 26-2 (formerly Fed SR 11-7), CFTC 1.31
- **Monitored proposals:** FINRA RN 25-07 (RFC — workplace modernization touching AI-generated communications recordkeeping; not yet adopted)
- **Audience:** M365 administrators in US financial services

**Full context:** See `.github/copilot-instructions.md` for complete repository structure and design decisions.

**Companion Repository:** `FSI-AgentGov-Solutions` contains 36 companion solution implementations (35 live + 1 preview) mapped to the current 79-control framework baseline. See `docs/reference/solutions-index.md` for the current catalog.

**Key reference documents:**
- `docs/reference/csa-quick-reference.md` — CSA Quick Reference for partner/CSA engagement
- `docs/reference/csa-positioning-guide.md` — CSA Positioning Guide
- `docs/images/diagrams/` — Exportable architecture diagrams (PNG/SVG)
- The current control catalog includes automation indicators identifying automation feasibility

## Before Making Changes

1. **Read `.github/copilot-instructions.md`** for full repository context
2. **Understand the task scope** — is it a control edit, nav update, or new feature?
3. **Check related files** — controls often reference each other
4. **If coordinating with other agents, use separate worktrees/branches** — see Multi-Agent Coordination below

## GitHub Accounts & Push/Merge Workflow

The repo owner uses two GitHub accounts on this machine, and AI tooling must pick the right one for write operations:

| Account | Purpose | Can write to `judeper/FSI-AgentGov`? |
|---------|---------|--------------------------------------|
| `judep_microsoft` (Enterprise Managed User) | Required to be the active `gh` account for the **Copilot CLI license** to remain active | ❌ — blocked by EMU policy |
| `judeper` (personal) | Owner of this repo; required for **`git push`**, **`gh pr merge`**, **`gh pr close`**, **`gh pr comment`**, **workflow re-runs** | ✅ |

**Symptoms of the wrong account being active:**
- `git push` → `remote: Permission to judeper/FSI-AgentGov.git denied to judep_microsoft. ... 403`
- `gh pr merge` / `gh pr close` / `gh pr comment` → `GraphQL: Unauthorized: As an Enterprise Managed User, you cannot access this content (mergePullRequest|addComment)`
- `gh run rerun` → `Must have admin rights to Repository`

**Switch commands:**

```powershell
# Before any push/merge/close/comment work:
gh auth switch -u judeper

# When work is done, restore EMU as active so Copilot CLI keeps its license:
gh auth switch -u judep_microsoft
```

**Verification:**

```powershell
gh auth status          # confirms which account is active in keyring
gh api user -q '.login' # confirms which account the API actually resolves to
```

These two can disagree if the account silently flips mid-session — always re-check with `gh api user` before a sensitive write operation. If they disagree, run `gh auth switch -u judeper` again.

**Git credential helper notes:**
- Windows credential manager (`credential.helper=manager`) caches the EMU token and will override the `gh` credential helper for `git push`. Workaround when push fails: push via tokenized URL, e.g. `git push "https://judeper:$(gh auth token --user judeper)@github.com/judeper/FSI-AgentGov.git" <branch>`.
- A repo-local override of `credential.helper` to `!gh auth git-credential` is not always sufficient on Windows. The tokenized-URL workaround is the most reliable.

**Best practice for AI sessions:**
1. At session start, leave `judep_microsoft` active (Copilot CLI needs it).
2. When write operations are needed, switch to `judeper`, do all writes in one batch, then switch back.
3. If `gh api user` returns the wrong account between operations, re-switch before continuing — the account can flip mid-session.

### REST-API Workaround for `gh` GraphQL Failures

Some `gh` subcommands route through the GitHub GraphQL API and surface
the EMU `Unauthorized` error even when the keyring's active account
should be permitted. When that happens, the same operation called via
the REST API directly with an explicit `judeper` token works because
REST honors the bearer token in the request rather than the keyring's
"active" cookie. **Use this whenever a `gh` command fails with a
GraphQL `Unauthorized` error and you've already confirmed `judeper` is
active.**

Pattern (PowerShell):

```powershell
$token = gh auth token --user judeper
$headers = @{ Authorization = "Bearer $token"; Accept = "application/vnd.github+json" }
# Then use Invoke-RestMethod with the GitHub REST endpoint.
```

**Five operations confirmed working via REST when `gh` fails:**

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Create PR | `/repos/judeper/FSI-AgentGov/pulls` | POST `{title, head, base, body}` |
| Merge PR | `/repos/judeper/FSI-AgentGov/pulls/{n}/merge` | PUT `{merge_method, sha}` |
| Comment on PR | `/repos/judeper/FSI-AgentGov/issues/{n}/comments` | POST `{body}` |
| Add labels | `/repos/judeper/FSI-AgentGov/issues/{n}/labels` | POST `{labels: [...]}` |
| Reopen PR | `/repos/judeper/FSI-AgentGov/pulls/{n}` | PATCH `{state: "open"}` |

### Branch Deletion Closes Its PR (And It Can't Always Be Reopened)

Deleting the branch behind an open PR causes GitHub to auto-close that
PR. Reopening that PR via PATCH `state=open` can fail with HTTP 422:

```
state cannot be changed. The <branch> branch was force-pushed or recreated.
```

This is permanent for that PR -- the only recovery path is to re-push
the branch and **create a new PR** against the same base. Therefore:
**never delete a branch with an open PR unless you've already merged
it (or genuinely intend to abandon the change).**

### `git push --force-with-lease` "Stale Info" Workaround

When `git push --force-with-lease <branch>` fails with `stale info`,
the local remote-tracking ref disagrees with the actual remote tip
(common after a rebase + a CI auto-commit on the same branch).
Resolve in this order:

1. `git fetch <remote> <branch>` to refresh the tracking ref, then
   retry `--force-with-lease`. Safe; preserves the lease semantics.
2. If step 1 still rejects (e.g. because credential helper is using
   the wrong account, see "Git credential helper notes" above),
   fall back to a tokenized push via REST-friendly URL:
   `git push "https://judeper:$(gh auth token --user judeper)@github.com/judeper/FSI-AgentGov.git" <branch>`
3. **Last resort only:** `git push --force <branch>`. Drops the
   lease check entirely; only safe when you've manually verified
   no one else (including CI bots) pushed to the branch since you
   last fetched.

### `gh pr checks` Truncation

`gh pr checks <n>` truncates output and may show fewer rows than the
actual check-run count. To get the complete list of all check runs
for a commit (useful when monitoring 11 required gates on a busy PR):

```powershell
$sha = gh pr view <n> --json headRefOid -q '.headRefOid'
gh api "repos/judeper/FSI-AgentGov/commits/$sha/check-runs?per_page=100" `
  -q '.check_runs[] | "\(.name): \(.conclusion // .status)"'
```

The `?per_page=100` query string is mandatory -- the default is small
enough to cause silent truncation on PRs with many checks.

## Multi-Agent Coordination

Two common tool surfaces operate on this repository:

| Tool | Primary Role | Config Location |
|------|-------------|-----------------|
| **Codex CLI** | Documentation generation and repo maintenance | `.codex/config.toml` |
| **GitHub Copilot** | Prompt-driven repo assistance | `.github/copilot-instructions.md`, `.github/prompts/`, `.github/instructions/` |

When multiple agents are active, prefer one branch/worktree per agent. Avoid concurrent edits to the same file and hand off work through branches, commits, or PRs rather than shared planning-state files.

### Parallel Agent Runs with Worktrunk

This repository uses [Worktrunk](https://worktrunk.dev/) for git worktree management, enabling multiple AI agents to work in parallel on isolated branches.

**Why worktrees?** Each agent gets its own working directory backed by the same `.git` database — no stashing, no conflicts, no waiting for another agent to finish.

**Windows note:** On Windows, `wt` is taken by Windows Terminal. Worktrunk installs as `git-wt` via winget. Alternatively, disable the Windows Terminal alias (Settings → Privacy & security → For developers → App Execution Aliases → disable "Windows Terminal") to use `wt` directly. The examples below use `git-wt` for Windows compatibility.

**Fallback when Worktrunk is unavailable:** Worktrunk is optional. If `git-wt` is not installed on the current machine (e.g., no winget access, fresh CI runner, or a tool conflict), fall back to plain `git worktree`:

```powershell
git worktree add -b feature-name ../FSI-AgentGov.feature-name
git worktree list
git worktree remove ../FSI-AgentGov.feature-name
```

The pre-merge validation (`mkdocs build --strict`, `python scripts/verify_controls.py`) must still run before merging; without Worktrunk's hooks you invoke them manually. Single-worktree workflows (no parallel agents) are also acceptable — branch off `main`, work, push, merge through a PR like any other change.

**Core commands:**

| Task | Command |
|------|---------|
| Create worktree + branch | `git-wt switch --create feature-name` |
| Switch to existing worktree | `git-wt switch feature-name` |
| List all worktrees with status | `git-wt list` |
| Remove worktree + branch | `git-wt remove` |
| Merge back to main | `git-wt merge main` |

**Running parallel agents:**

```bash
# Launch multiple Copilot CLI sessions on separate features
git-wt switch --create control-1-23-update
git-wt switch --create playbook-fixes
git-wt switch --create nav-restructure
```

Each worktree is a full working directory at `../FSI-AgentGov.{branch-name}/`.

**Project hooks** (`.config/wt.toml`):
- **post-create**: Copies `.venv/`, `site/`, and other gitignored files from the base worktree via `git-wt step copy-ignored`
- **pre-merge**: Runs `mkdocs build --strict` and `python scripts/verify_controls.py` before merging


### Codex CLI Model Selection

Pick the cheapest model that can hold the relevant context in one pass and will not invent control IDs, file paths, or implementation steps. Three named profiles are defined in `.codex/config.toml`:

| Profile | Model | Reasoning | Use When |
|---------|-------|-----------|----------|
| `budget` | gpt-5.1-codex-mini | low | Typos, single-file edits, heading normalization |
| *(default)* | gpt-5.1-codex | high | Multi-file control + playbook updates, bounded solution work |
| `quality` | gpt-5.3-codex | xhigh | Net-new solution design, cross-repo alignment, multi-control reasoning |

Activate with `codex --profile budget` or `codex --profile quality`. The default (no flag) uses gpt-5.1-codex.

**Task examples:**

| Task | Profile |
|------|---------|
| Fix typos, normalize headings, tighten wording in framework docs | `--profile budget` |
| Update a single control doc without touching playbooks | `--profile budget` |
| Update a control and its 4 playbooks | Default |
| Add a new solution folder patterned after an existing one | Default |
| Net-new solution design mapped to multiple controls | `--profile quality` |
| Cross-repo alignment (solution control mappings vs control catalog) | `--profile quality` (plan) → default (edit) |

**Workflow:**
1. Run a "plan-only" prompt first — get the file list and diff outline before generating changes
2. Simple patches (1–2 files): `codex --profile budget`; multi-file: use the default
3. One control (or one solution) per commit for reviewable diffs
4. Run `mkdocs build --strict` / `verify_controls.py` after each change set; escalate to `--profile quality` when validation failures need cross-file reasoning


## Agent Workflows

### Add a New Control

1. Read `docs/templates/control-setup-template.md` for required structure
2. Copy template to correct pillar folder: `docs/controls/pillar-{n}-{name}/`
3. Name file: `{id}-{kebab-case-name}.md` (e.g., `1.20-new-control.md`)
4. Fill all 10 sections (plus header and footer metadata) — do not skip any
5. Update these files:
   - `docs/controls/CONTROL-INDEX.md` — add the new control to the master index
   - `mkdocs.yml` — add to navigation under correct pillar
6. Create `docs/images/{control-id}/EXPECTED.md` for screenshot specs
7. Validate: `mkdocs build --strict`

### Update Existing Control

1. Read current control file completely
2. Preserve all 10 sections — do not remove any
3. Update "Updated" in footer (Month-Year)
4. If portal paths changed, update `docs/images/{control-id}/EXPECTED.md`
5. Validate: `mkdocs build --strict`

### Verify Screenshots

See `docs/images/VERIFY.md` for the screenshot verification workflow.

### Update Navigation

Edit `mkdocs.yml` `nav:` section. Maintain numerical order within pillars. Validate: `mkdocs build --strict`

## Language Guidelines

When writing control documentation:
- **NEVER use:** "ensures compliance", "guarantees", "will prevent", "eliminates risk"
- **ALWAYS use:** "supports compliance with", "helps meet", "required for", "recommended to", "aids in"
- Include caveats about implementation requirements
- Use canonical role names from `docs/reference/role-catalog.md`

## Validation Commands

Always run before completing work:

```bash
mkdocs build --strict                # Validates links and structure
python scripts/verify_build_output.py  # Verifies built site completeness
python scripts/verify_controls.py    # Validates control files
# Cross-reference integrity (Control X.Y IDs + inline labels)
python scripts/verify_xref_graph.py
```

Additional validations (when applicable):
```bash
python scripts/verify_excel_templates.py        # After template changes
python scripts/compile_researcher_package.py    # After pillar control changes
cd assessment && pytest tests/ -v               # After assessment engine changes

# Cross-source consistency (79 control IDs in manifest, CONTROL-INDEX, and mkdocs nav)
python scripts/check_manifest_doc_drift.py --check

# Honest assessment-engine coverage report (regenerate after wiring evaluators)
python scripts/generate_coverage_matrix.py --check     # CI-style fail-on-drift
python scripts/generate_coverage_matrix.py             # write the file

# FSI-banned-phrase linter (rejects "ensures compliance", "guarantees", etc.)
python scripts/verify_language_rules.py

# Python lint (ruff config in pyproject.toml — F, B, I)
ruff check assessment scripts

# PowerShell static analysis (settings at PSScriptAnalyzerSettings.psd1)
pwsh -c "Invoke-ScriptAnalyzer -Path scripts,assessment/collectors,assessment/run-assessment.ps1 -Recurse -Settings ./PSScriptAnalyzerSettings.psd1"
```

CI enforces all of the above. See `.github/workflows/python-quality.yml`, `powershell-quality.yml`, `secret-scanning.yml`, `dependency-review.yml`, `codeql.yml`, and `release-artifacts.yml`. Release tags trigger CycloneDX SBOM generation and Sigstore keyless signing per the [Versioning and Support policy](docs/reference/versioning-and-support.md).

### Workflow patterns (`.github/workflows/`)

Three workflow-level patterns established during the May 2026 backlog drain — read `.github/AUDIT-METHODOLOGY.md` Lessons 16–18 before editing any workflow:

- **Required-check shims** (`required-check-shims.yml` for `e2e-smoke`, `required-check-shim-mkdocs.yml` for `mkdocs-strict`): bot PRs that touch only paths outside a real workflow's `paths:` (e.g. `data/**`, `reports/monitoring/**`, `scripts/requirements.txt`) cannot trigger that real workflow. Each shim lives in its own file and emits a success status for its required check name on a `paths-ignore:` that is the EXACT complement (mirror) of its own real workflow's `paths:` — the two real workflows have different `paths:`, so a single shared `paths-ignore` (the union) would over-include and reopen the deadlock. Exact complement means **neither-fires is impossible**: for each required check, every-file-matches → real fires/shim skips; no-file-matches → real skips/shim fires. A **mixed PR** (some files in the real `paths:`, some not) fires both the real workflow and the shim; this is benign for green runs, but because GitHub evaluates the latest run for a check name, an always-success shim that completes after a failed real run could mask that failure — keep each shim's `paths-ignore:` exactly equal to its real workflow's `paths:` and no wider. When you edit a real workflow's `paths:`, mirror the change in the matching shim's `paths-ignore:` in the same commit.
- **Workflow-only and changelog-only PR coverage in `python-quality.yml`**: keep `.github/workflows/**` and `CHANGELOG.md` in the `pull_request.paths` filter so workflow-only PRs (for example `publish_docs.yml`) and changelog-only PRs still report the required named checks. This prevents the "11 of 11 expected" deadlock on branch-protected PRs.
- **No invented CLI flags in workflow YAML**: `mkdocs gh-deploy` does **not** accept `--site-url` (only `mkdocs build`/`serve` do). Always run `<tool> <subcommand> --help` locally before "hardening" a workflow with a new flag. The defense-in-depth equivalent of an explicit `site_url` at deploy time is a grep-based pre-deploy assertion step, not a CLI flag.
- **Autonomous autodoc pipeline** (`autodoc-verify.yml` + `scripts/autodoc_*.py`, driven by a local, unattended GitHub Copilot CLI drafter): a fail-closed, human-merge-gated loop that drafts and independently verifies doc edits from Learn Monitor changes. **Off by default** (`AUTODOC_ENABLED` repo variable). `automerge_eligible` is redirect-only; regulatory content is triage-only. Operations + provisioning (kill-switch, escalation) are in **`.github/AUTODOC-RUNBOOK.md`** — read it before editing any autodoc workflow or script.

## Auditing for repo-wide drift

When making changes that could plausibly affect multiple file types or directories — version bumps, count changes, structural renames, repo-wide claims — use the **Scorched-Earth Enumeration + Classify-Then-Act** methodology in `.github/AUDIT-METHODOLOGY.md`. Do NOT rely on "deep audits" by sampling — every prior sampling pass missed P0 issues that a fourth pass surfaced. The methodology is mandatory for these change classes; for single-file fixes or typo passes it is not needed. (See `.github/AUDIT-METHODOLOGY.md` Lessons 19-23 for May 2026 audit triage lessons including multi-audit cross-reference, parallel sub-agent fleet, mergeStateStatus quirks, CHANGELOG paths fix, and scoped-sweep enumeration discipline.)

## Automated Assessment Engine

The `assessment/` directory contains a programmatic assessment engine that collects tenant configuration via APIs, scores all 79 controls against zone thresholds, and generates pre-filled reports with a focused manual questionnaire.

**Structure:**
- `manifest/controls.json` — machine-readable 79-control manifest (checks, zone thresholds, manual questions)
- `collectors/` — 5 PowerShell collectors: Collect-PPAC, Collect-Graph, Collect-Purview, Collect-SharePoint, Collect-Sentinel
- `engine/score.py` — Python scoring engine (evaluates pass_conditions, derives maturity 0–4, sets confidence)
- `engine/report.py` — generates assessment-prefilled.md, manual-questionnaire.md, assessment-summary.json
- `run-assessment.ps1` — orchestrator (validates, runs collectors, calls scoring + reporting)
- `tests/` — pytest suite with fixture data for 5 representative controls

**When editing assessment code:**
1. Run `cd assessment && pytest tests/ -v` to verify no regressions
2. If modifying `controls.json`, ensure all 79 entries are present with required schema fields
3. `assessment/output/` is gitignored — customer data must never be committed

## Advanced Implementations

Complex multi-control solutions in `docs/playbooks/advanced-implementations/`:

- **Platform Change Governance** — Dataverse-based Message Center change management
- **Environment Lifecycle Management** — Automated environment provisioning with zone classification
- **Configuration Hardening Baseline** — 32-item security configuration verification checklist with automated PowerShell validation

All have companion deployment scripts or governance automation in FSI-AgentGov-Solutions.

## Files to Never Modify Without Permission

- `LICENSE` — Legal file
- `SECURITY.md` — Security policy
- `CODE_OF_CONDUCT.md` — Community standards

## Error Handling

If you encounter:
- **Broken links:** Check `mkdocs.yml` nav entries match actual file paths
- **Missing sections in controls:** Refer to `docs/templates/control-setup-template.md`
- **Build failures:** Run `mkdocs build --strict` and fix reported issues
- **Concurrent edits:** Use separate branches/worktrees and avoid editing the same file from multiple sessions

## Tool-Specific Configuration

| Tool | Config | Details |
|------|--------|---------|
| **Codex CLI** | `.codex/config.toml` | Model, sandbox, approval policy (local only, gitignored) |
| **Copilot Context** | `.github/copilot-instructions.md` | Repository structure, workflow guardrails, and design context |
| **Copilot Prompts** | `.github/prompts/` | Workspace prompts, including `repo-health-check*.prompt.md` and `review-learn-changes.prompt.md` |
| **Copilot Instructions** | `.github/instructions/` | Auto-included rules, including `fsi-language-rules`, `fsi-control-template`, `build-validation`, and `git-integration` |
| **Worktrunk** | `.config/wt.toml` | Worktree hooks for parallel agent runs |

### Copilot Tool Alias Notes

Agent and prompt files use GitHub Copilot's recognized built-in aliases: `read`, `edit`, `search`, `execute`, `agent`, `web`, `todo`. Unrecognized names are silently ignored (falling back to unrestricted access).

**Platform differences:** The `web` and `todo` aliases are supported in VS Code Copilot Chat but are currently not applicable to the GitHub.com Copilot coding agent. Prompts that reference these tools should be resilient without them — they enhance the workflow in VS Code but are safely ignored on GitHub.com.

## Troubleshooting: prompt files not showing in `/`

If you type `/` in Copilot Chat and don't see the workspace prompt files from `.github/prompts/`:

- Open the **Chat view** and use **Diagnostics** (right-click inside Chat → **Diagnostics**) to see whether prompt files were **Loaded**, **Skipped**, or **Failed**, and why.
- Check **Workspace Trust**: if VS Code shows **Restricted Mode**, trust the workspace and reload.
- Confirm you're on a recent VS Code version that supports prompt files (prompt files are `.prompt.md` and show up as slash commands).
- If your org restricts chat customization, the diagnostics view typically indicates policy-based blocking.

## E2E Test Suite

The customer-facing assessment SPA at `/assessment/` is gated by a Playwright suite under `tests/e2e/` (forthcoming in plan v3.1, Phase C). Until that lands, the suite covers:

- **Smoke set** (~90s wall): happy path, autofill defenses, PDF print spy, import roundtrip, axe a11y baseline.
- **Full suite**: ~28 specs across exports (JSON/XLSX/CSV/PDF/MD), state restoration, hash routing, multi-tab race, XSS matrix, mobile viewport, keyboard nav, perf budget, CSP+asset-skew, collector injection, cross-origin localStorage.

Vitest layer (`tests/spa/`) covers contracts: JSON envelope schema, CSV escape, MD anchor, persona-fixture parity, XLSX cell shape, prototype-pollution validator, filter-loop perf.

### Running locally

```bash
npm test                    # vitest contracts
npm run test:e2e:smoke      # Playwright smoke (~90s)
npm run test:e2e            # Playwright full
```

### Snapshot regeneration

PNG snapshots are Linux-baseline only. Regenerate via the manual-dispatch workflow `.github/workflows/update-snapshots.yml`. Do NOT commit Windows/macOS-generated snapshots.

### CI gating

PRs require `e2e/smoke` (Required Status Check) before merge. `prod-smoke.yml` runs after deploy, polling `/version.json` for the deployed SHA before exercising the production URL.

### Failure triage

Failed Playwright runs upload trace + screenshot artifacts. Reproduce locally with `npx playwright test <spec> --trace on --headed`.