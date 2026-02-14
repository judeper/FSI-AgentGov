# Contributing to FSI Agent Governance Framework

Thank you for your interest in contributing to the FSI Agent Governance Framework!

## How to Contribute

### Reporting Issues

1. Check existing [Issues](https://github.com/judeper/FSI-AgentGov/issues) to avoid duplicates
2. Use the appropriate issue template (Bug Report or Feature Request)
3. Provide as much detail as possible

### Suggesting Enhancements

- For new controls: Include regulatory reference and implementation guidance
- For documentation: Describe the gap and proposed content
- For templates: Explain the use case and expected format

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test with `mkdocs build --strict`
5. Submit a pull request with a clear description

## Style Guidelines

### Documentation
- Use Markdown with consistent formatting
- Include version footer on all pages
- Reference control IDs where applicable

### Control Files

Control files in `docs/controls/pillar-*/` must follow the standard structure:

**Required Sections:**

Controls follow a standardized format with header metadata, 10 sections, and footer metadata:

**Header Metadata:**
- Control ID, Pillar, Regulatory Reference, Last UI Verified, Governance Levels

**10 Required Sections:**
1. **Objective** - Concise purpose statement
2. **Why This Matters for FSI** - Regulatory bullet points
3. **Control Description** - Detailed technical explanation
4. **Key Configuration Points** - Bulleted configuration items
5. **Zone-Specific Requirements** - Zone 1/2/3 table with requirements and rationale
6. **Roles & Responsibilities** - Admin roles table
7. **Related Controls** - Cross-reference table with relationships
8. **Implementation Guides** - Links to 4 playbooks (portal, powershell, verification, troubleshooting)
9. **Verification Criteria** - Verification checklist
10. **Additional Resources** - Microsoft Learn links

**Footer Metadata:**
- *Updated: Month-Year | Version: v1.1 | UI Verification Status: Current*

**Administrator Role Naming:**
- Use the framework's canonical short role names (e.g., "Power Platform Admin", "Purview Compliance Admin").
- Avoid inconsistent synonyms ("Global Admin" vs "Global Administrator").
- See `docs/reference/role-catalog.md` for canonical names and accepted aliases.

**Language Guidelines:**
- Avoid overclaims like "ensures compliance" or "guarantees"
- Use "supports compliance with" instead of "ensures compliance with"
- Use "required for" or "helps meet" instead of "guarantees"
- Include implementation caveats where appropriate

**Regulatory Mapping:**
- Reference specific regulation sections (e.g., "SEC 17a-3/4" not just "SEC")
- Map to FINRA, SEC, SOX, GLBA, OCC, or Fed SR 11-7 as applicable
- Update `docs/reference/regulatory-mappings.md` if adding new mappings

**Testing:**
```bash
mkdocs build --strict  # Validates links and structure
mkdocs serve           # Preview locally at http://localhost:8000
```

## AI Agent Context

If you're using AI assistants with this repository:

- **`.github/copilot-instructions.md`** - Repository-wide context for GitHub Copilot
- **`.claude/CLAUDE.md`** - Core instructions for Claude Code
- **`.claude/skills/`** - On-demand workflow guides for Claude Code:
  - `/update-control` - Modifying existing controls
  - `/add-control` - Adding new controls
  - `/update-excel` - Excel template maintenance
  - `/verify-ui` - Screenshot verification
  - `/review-learn-changes` - Learn Monitor change report review
- **`AGENTS.md`** - Instructions for autonomous agent tasks
- **`docs/templates/README.md`** - Guide to using control templates

These files help AI assistants understand the project structure, coding conventions, and common workflows.

## Screenshot Verification

Screenshots for verifying portal instructions are stored locally (not pushed to GitHub):

- **Location:** `docs/images/{control-id}/`
- **EXPECTED.md** in each folder lists required screenshots
- **README.md** and **VERIFY.md** explain conventions and workflow

See `docs/images/VERIFY.md` for the full verification process.

## Maintainers: Public Release Checklist

When preparing a public/beta update, confirm these repo-level settings and docs are consistent:

- **GitHub Pages**: Enabled and publishing via **GitHub Actions** (or correctly configured `gh-pages`), and the site is publicly accessible at the configured `site_url`.
- **Repo “About” metadata**: Add a short description, relevant topics, and set the **Website** field to the docs URL.
- **Offline deliverables scope**: Ensure user-facing docs consistently state **web docs + Excel templates only** (no Word/PDF bundle).
- **CI health**: `publish_docs.yml` and `link-check.yml` are green on `main`.

## Maintainer Machine Setup

This section walks through setting up a fresh machine to work on this repository. It covers both macOS and Windows.

### Prerequisites

| Tool | Required For | Install |
|------|-------------|---------|
| Python 3.9+ | Validation scripts, MkDocs | python.org or package manager |
| Git | Version control | git-scm.com |
| VS Code + GitHub Copilot | GSD workflows, documentation editing | VS Code marketplace |
| Claude Code CLI | Alternative GSD interface, cross-repo QA | anthropic.com (optional) |
| Codex CLI | GPT code generation with named profiles | openai.com — requires OpenAI subscription (optional) |
| Node.js 18+ | claude-mem MCP plugin | nodejs.org (only if using Claude Code + claude-mem) |

### Repository Setup

```bash
# Clone both repositories
git clone https://github.com/judeper/FSI-AgentGov.git
git clone https://github.com/judeper/FSI-AgentGov-Solutions.git

# Install Python dependencies
cd FSI-AgentGov
pip install -r scripts/requirements.txt
pip install mkdocs-material

# Verify the build
mkdocs build --strict
python scripts/verify_controls.py
```

### GSD Workflow Setup (No Installation Required)

GSD is **not a package to install**. It is 32 prompt files, 13 agent files, and 12 instruction files committed directly to this repository under `.github/prompts/`, `.github/agents/`, and `.github/instructions/`.

- **VS Code + Copilot Chat:** Copy the example settings file, then use GSD commands in Copilot Chat:
  ```bash
  cp .vscode/settings.json.example .vscode/settings.json
  ```
  Open Copilot Chat and type `/gsd:help` to confirm GSD is available.

- **Claude Code CLI:** GSD commands are available automatically via the `/gsd:` prefix. Type `/gsd:help` to see available commands.

- **Terminal `gh copilot`:** No GSD support. The `gh copilot` CLI is limited to quick shell help and does not load prompt/agent files.

### Claude Code Setup (Optional)

For maintainers using the Claude Code CLI, create `.claude/settings.local.json` with local overrides. This file is gitignored and not committed:

```json
{
  "includeCoAuthoredBy": false,
  "permissions": {
    "allow": [
      "WebFetch(domain:www.microsoft.com)",
      "WebFetch(domain:learn.microsoft.com)",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:judeper.github.io)",
      "Bash(gh run list:*)"
    ]
  }
}
```

What each setting does:

- **`WebFetch` domains** — Allows fetching Microsoft Learn docs, GitHub issues, and the project's GitHub Pages site without per-request approval.
- **`gh run list`** — Allows monitoring GitHub Actions workflow status.
- **`includeCoAuthoredBy: false`** — Produces cleaner git history without Co-authored-by trailers on commits.

### claude-mem Plugin Setup (Optional — Claude Code Only)

The claude-mem plugin provides cross-session memory (decisions, learnings, observations) for Claude Code. It is not required for Copilot users.

1. **Install from the plugin marketplace** — Open Claude Code and install `claude-mem@thedotmack`.
2. **Enable in global settings** — Add to `~/.claude/settings.json`:
   ```json
   { "enabledPlugins": { "claude-mem@thedotmack": true } }
   ```
3. **Restart Claude Code** — The plugin auto-registers its MCP server.
4. **Verify** — The tools `search`, `get_observations`, `save_memory`, and `timeline` should appear in available tools.

Memory is persisted as JSONL files under `~/.claude/projects/`. Requires Node.js 18+ for the MCP server process.

### Codex CLI Setup (Optional — Requires OpenAI Subscription)

Codex CLI is OpenAI's terminal tool for GPT-powered code generation. It requires a separate OpenAI account and API access — a GitHub Copilot license alone is not sufficient.

For maintainers with OpenAI access, the project includes a pre-configured `.codex/config.toml` with three named profiles:

| Profile | Command | Use When |
|---------|---------|----------|
| `budget` | `codex --profile budget` | Typos, single-file edits |
| *(default)* | `codex` | Multi-file control + playbook updates |
| `quality` | `codex --profile quality` | Net-new design, cross-repo alignment |

No additional configuration is needed — `.codex/config.toml` is committed to the repository. See `AGENTS.md` "Codex CLI Model Selection" for the full task-to-profile mapping.

> **Note:** Codex CLI does not support GSD workflows, and uses personal OpenAI quota. For GSD phase planning and execution from the terminal, use Claude Code CLI (`/gsd:` commands). For code assistance covered by your enterprise license, use VS Code Copilot Chat or `gh copilot`.

### Files That Need Manual Transfer Between Machines

Most gitignored content can be regenerated. Only two directories contain non-regenerable content:

| Path | Purpose | Transfer? | Can Regenerate? |
|------|---------|-----------|-----------------|
| `maintainers-local/notes/` | CLI workflow guides (Copilot, Claude Code, Codex) | Copy if available | No (written manually) |
| `maintainers-local/reference-pack/` | Whitepapers and extracted references | Copy if needed | No (collected manually) |
| `maintainers-local/researcher-package/` | Compiled controls for review | Skip | Yes: `python scripts/compile_researcher_package.py` |
| `maintainers-local/reports/` | Generated analysis reports | Skip | Yes (regenerated by scripts) |
| `maintainers-local/tenant-evidence/` | Portal screenshots for UI verification | Machine-specific | No (tenant-specific captures) |
| `maintainers-local/tmp/` | Scratch artifacts | Skip | Not needed |
| `.claude/settings.local.json` | Claude Code local overrides | Recreate from docs above | Yes (content documented in this guide) |
| `.vscode/settings.json` | VS Code + Copilot config | Copy from example | Yes: `cp .vscode/settings.json.example .vscode/settings.json` |

**Bottom line:** Only `maintainers-local/notes/` and `maintainers-local/reference-pack/` contain non-regenerable content worth transferring.

### Verification Checklist

After setup, confirm everything works:

```bash
# Documentation builds clean
mkdocs build --strict

# Controls validate
python scripts/verify_controls.py
```

For GSD verification:

- **VS Code Copilot Chat:** Type `/gsd:help` — should list available GSD commands.
- **Claude Code CLI:** Type `/gsd:help` — should list available GSD commands.

## Questions?

Open an [Issue](https://github.com/judeper/FSI-AgentGov/issues) or contact the maintainers.

---

*FSI Agent Governance Framework v1.2.48 - February 2026*
