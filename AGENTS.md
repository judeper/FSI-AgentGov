# AGENTS.md - Instructions for AI Agents

This file provides guidance for autonomous AI agents working on this repository. It is tool-neutral and readable by Codex CLI, GitHub Copilot, and Claude Code.

## Project Overview

**FSI Agent Governance Framework v1.2.46** — A governance framework for Microsoft 365 AI agents in US financial services organizations.

- **71 controls** across 4 pillars (Security, Management, Reporting, SharePoint)
- **3 governance zones** (Personal Productivity, Team Collaboration, Enterprise Managed)
- **3-layer documentation** (Framework → Controls → Playbooks)
- **Target regulations:** FINRA 4511/3110/25-07, SEC 17a-3/4, SOX 302/404, GLBA 501(b), OCC 2011-12, Fed SR 11-7, CFTC 1.31
- **Audience:** M365 administrators in US financial services

**Full context:** See `.github/copilot-instructions.md` for complete repository structure and design decisions.

**Companion Repository:** `FSI-AgentGov-Solutions` contains deployable solution artifacts (25 solutions covering 28+ controls). See `docs/reference/solutions-index.md` for catalog.

## Before Making Changes

1. **Read `.github/copilot-instructions.md`** for full repository context
2. **Understand the task scope** — is it a control edit, nav update, or new feature?
3. **Check related files** — controls often reference each other
4. **Check session ownership** — see Multi-Agent Coordination below

## Multi-Agent Coordination

Three tools operate on this repository:

| Tool | Primary Role | Config Location |
|------|-------------|-----------------|
| **Codex CLI** | Documentation generation | `.codex/config.toml` |
| **GitHub Copilot** | Documentation writing, GSD workflows | `.github/agents/`, `.github/prompts/` |
| **Claude Code** | Verification, QA, GSD workflows | `.claude/CLAUDE.md`, `.claude/skills/` |

### Session Ownership Protocol

Only one tool writes to GSD shared state files at a time.

**Rules:**
- Whichever tool starts a session owns GSD writes for that session
- The session owner updates `STATE.md` with `Active Tool` at session start
- Handoff requires the current owner to update STATE.md before the other tool begins
- Both tools can always **read** all `.planning/` files
- Only the session owner **writes** to `STATE.md`, `ROADMAP.md`, `config.json`
- Phase artifacts (`PLAN.md`, `SUMMARY.md`, `RESEARCH.md`) are written by whichever tool executes the plan

**Handoff format** (add to STATE.md Session Continuity section):
```markdown
**Active Tool:** copilot | claude-code | codex
**Session Started:** YYYY-MM-DD HH:MM
**Handoff Summary:** [What was done, what's next]
```

### Conflict Prevention

- Before writing to `.planning/`, check `STATE.md` for `Active Tool`
- If another tool owns the session, only read — do not write
- If `Active Tool` is missing, claim the session by updating STATE.md
- Phase execution artifacts are safe to write — they are scoped to the executing plan

### Parallel Agent Runs with Worktrunk

This repository uses [Worktrunk](https://worktrunk.dev/) for git worktree management, enabling multiple AI agents to work in parallel on isolated branches.

**Why worktrees?** Each agent gets its own working directory backed by the same `.git` database — no stashing, no conflicts, no waiting for another agent to finish.

**Windows note:** On Windows, `wt` is taken by Windows Terminal. Worktrunk installs as `git-wt` via winget. Alternatively, disable the Windows Terminal alias (Settings → Privacy & security → For developers → App Execution Aliases → disable "Windows Terminal") to use `wt` directly. The examples below use `git-wt` for Windows compatibility.

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

**Integration with session ownership:** Worktrees provide filesystem isolation, but the GSD session ownership protocol (STATE.md `Active Tool`) still applies when writing to `.planning/` shared state files. Each worktree agent should check STATE.md before writing.

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

> **Note:** Profiles control the LLM model and reasoning effort. GSD model profiles (`quality`/`balanced`/`budget` in `.planning/config.json`) control workflow behavior — research depth, verification thoroughness. They are complementary: pick a Codex profile for the LLM, and a GSD profile for the workflow.

## GSD Planning Structure

The `.planning/` directory contains project management state for the GSD (Get Stuff Done) workflow.

```
.planning/
├── PROJECT.md          # Project identity, scope, key decisions
├── ROADMAP.md          # Phase breakdown with success criteria
├── STATE.md            # Current position, session continuity
├── REQUIREMENTS.md     # Requirements with traceability matrix
├── MILESTONES.md       # Historical milestone achievements
├── config.json         # Workflow toggles and model profile
├── phases/             # Phase execution artifacts
│   └── {NN}-{kebab-name}/
│       ├── {NN}-RESEARCH.md    # Phase research
│       ├── {NN}-{PP}-PLAN.md   # Execution plans (PP = plan number)
│       ├── {NN}-{PP}-SUMMARY.md # Execution summaries
│       └── {NN}-VERIFICATION.md # Phase verification
├── research/           # Cross-phase research documents
├── codebase/           # Codebase analysis documents
└── todos/pending/      # Deferred work items
```

**Naming conventions:**
- Phase directories: `{NN}-{kebab-case-name}/` (e.g., `01-powershell-tech-debt/`)
- Plan files: `{NN}-{PP}-PLAN.md` with YAML frontmatter (phase, plan, wave, dependencies)
- Summary files: `{NN}-{PP}-SUMMARY.md` with dependency graph, tech stack, key files
- This repo uses `.planning/` — NOT `.gsd/`

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
mkdocs build --strict              # Validates links and structure
python scripts/verify_controls.py  # Validates control files
```

Additional validations (when applicable):
```bash
python scripts/verify_excel_templates.py        # After template changes
python scripts/compile_researcher_package.py    # After pillar control changes
```

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
- **GSD state conflicts:** Check `STATE.md` for session ownership before writing

## Tool-Specific Configuration

| Tool | Config | Details |
|------|--------|---------|
| **Claude Code** | `.claude/CLAUDE.md` | Full project context, skills, hooks |
| **Claude Code Skills** | `.claude/skills/` | On-demand workflows (`/update-control`, `/add-control`, etc.) |
| **Codex CLI** | `.codex/config.toml` | Model, sandbox, approval policy |
| **Copilot Agents** | `.github/agents/` | Custom agents (doc-writer, GSD workflow agents) |
| **Copilot Prompts** | `.github/prompts/` | GSD commands adapted for Copilot |
| **Copilot Instructions** | `.github/instructions/` | Auto-included rules by file path |
| **Worktrunk** | `.config/wt.toml` | Worktree hooks for parallel agent runs |

### Copilot Tool Alias Notes

Agent and prompt files use GitHub Copilot's recognized built-in aliases: `read`, `edit`, `search`, `execute`, `agent`, `web`, `todo`. Unrecognized names are silently ignored (falling back to unrestricted access).

**Platform differences:** The `web` and `todo` aliases are supported in VS Code Copilot Chat but are currently not applicable to the GitHub.com Copilot coding agent. Prompts that reference these tools should be resilient without them — they enhance the workflow in VS Code but are safely ignored on GitHub.com.

## Troubleshooting: prompt files not showing in `/`

If you type `/` in Copilot Chat and don"t see the workspace prompt files from `.github/prompts/`:

- Open the **Chat view** and use **Diagnostics** (right-click inside Chat → **Diagnostics**) to see whether prompt files were **Loaded**, **Skipped**, or **Failed**, and why.
- Check **Workspace Trust**: if VS Code shows **Restricted Mode**, trust the workspace and reload.
- Confirm you"re on a recent VS Code version that supports prompt files (prompt files are `.prompt.md` and show up as slash commands).
- If your org restricts chat customization, the diagnostics view typically indicates policy-based blocking.
