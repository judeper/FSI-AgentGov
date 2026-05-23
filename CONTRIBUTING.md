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
6. If using AI-assisted tools, review `AGENTS.md` for multi-agent conventions and session ownership protocol

## Style Guidelines

### Documentation
- Use Markdown with consistent formatting
- Include version footer on all pages
- Reference control IDs where applicable
- Avoid Material icon shortcodes (`:material-*:`) in page content; with the current MkDocs emoji/CSP configuration they may render as literal text on GitHub Pages
- Prefer plain text labels (for example `Start Here ->`) or standard Unicode symbols in Markdown content

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
- *Updated: Month-Year | Version: v1.6.2 | UI Verification Status: Current*

**Automation Indicators:**
- Each control must include an automation indicator identifying whether the control can be automated, partially automated, or requires manual implementation.

**CSA Reference Pages:**
- `docs/reference/csa-quick-reference.md` and `docs/reference/csa-positioning-guide.md` provide partner/CSA engagement materials. Update these when adding controls with CSA relevance.

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
- Map to FINRA, SEC, SOX, GLBA, OCC Bulletin 2026-13 / Fed SR 26-2, or other mapped frameworks (for example CFTC Rule 1.31, Reg S-P, NAIC AI, NFA 2-9) as applicable
- Update `docs/reference/regulatory-mappings.md` if adding new mappings

**Testing:**
```bash
mkdocs build --strict  # Validates links and structure
mkdocs serve           # Preview locally at http://localhost:8000
```

## Assessment Manifest (Single Source of Truth)

The `assessment/manifest/controls.json` file is the authoritative source for all 78 controls, used by both the Python scoring engine and the browser-based assessment SPA.

**Key principles:**
- **Single source of truth**: All control metadata, verification procedures, scoring thresholds, regulatory mappings, role assignments, and solution references live in this manifest
- **Additive schema**: The v1.4 extended schema adds 11 fields per control while preserving backward compatibility with existing engine fields
- **Static asset delivery**: The mkdocs hook `scripts/hooks/copy_assessment_data.py` (registered in `mkdocs.yml`) copies the manifest to `docs/assessment/data/controls.json` as a static asset, enabling runtime SPA access via `/assessment/data/controls.json`
- **Validation required**: After any manifest edit, run `python scripts/validate_manifest.py --allow-todo` to verify schema compliance

**Solution IDs:**
- Solution references in `controls.json` use kebab-case folder names from the companion FSI-AgentGov-Solutions repository (e.g., `["agent-observability-foundation", "audit-compliance-manager"]`)
- Rich solution metadata (display name, version, tier, description, URL, prerequisites, verification) lives in `assessment/data/solutions-lock.json`
- The lock file is committed locally and refreshed only when the companion repository cuts a new tag: `python scripts/refresh_solutions_lock.py --tag vX.Y.Z`
- Never reference solution metadata directly in `controls.json`—use the lock-file lookup pattern for reproducible builds

**Author-judgment fields:**
Some fields require human expertise and may contain `TODO:` placeholders until content review completes:
- `priority` (1–5 scale)
- `yesBar`, `partialBar`, `noBar` (threshold descriptions)
- `facilitatorNotes` (facilitator hints, follow-up questions, time budgets)
- `sectorYesBar` (sector-specific threshold overrides for 8 institution types)

The validator's `--allow-todo` mode permits CI to pass during progressive maturation. Strict mode (no flag) is used for production release gates.

## AI Agent Context

If you're using AI assistants with this repository:

- **`.github/copilot-instructions.md`** - Repository-wide context for GitHub Copilot
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
| VS Code + GitHub Copilot | Repository prompts, documentation editing | VS Code marketplace |
| Codex CLI | GPT code generation with named profiles | openai.com — requires OpenAI subscription (optional) |

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

### GitHub Copilot Setup (No Additional Repository Installation Required)

Repository-specific Copilot prompts are committed under `.github/prompts/`.

- **VS Code + Copilot Chat:** Copy the example settings file, then use repository prompts in Copilot Chat:
  ```bash
  cp .vscode/settings.json.example .vscode/settings.json
  ```
  Open Copilot Chat and run `/review-learn-changes` to confirm the prompt is available.

- **Terminal `gh copilot`:** Quick shell help only. It does not load repository prompt files.

### Codex CLI Setup (Optional — Requires OpenAI Subscription)

Codex CLI is OpenAI's terminal tool for GPT-powered code generation. It requires a separate OpenAI account and API access — a GitHub Copilot license alone is not sufficient.

For maintainers with OpenAI access, the project includes a pre-configured `.codex/config.toml` with three named profiles:

| Profile | Command | Use When |
|---------|---------|----------|
| `budget` | `codex --profile budget` | Typos, single-file edits |
| *(default)* | `codex` | Multi-file control + playbook updates |
| `quality` | `codex --profile quality` | Net-new design, cross-repo alignment |

No additional configuration is needed — `.codex/config.toml` is included in the repository (maintained locally via `.gitignore`). See `AGENTS.md` "Codex CLI Model Selection" for the full task-to-profile mapping.

> **Note:** Codex CLI uses personal OpenAI quota and does not load repository prompt files. For repository-specific prompts such as `/review-learn-changes`, use VS Code Copilot Chat. For quick terminal assistance covered by your enterprise license, use `gh copilot`.

### Files That Need Manual Transfer Between Machines

Most gitignored content can be regenerated. Only two directories contain non-regenerable content:

| Path | Purpose | Transfer? | Can Regenerate? |
|------|---------|-----------|-----------------|
| `maintainers-local/notes/` | CLI workflow guides (Copilot, Codex) | Copy if available | No (written manually) |
| `maintainers-local/reference-pack/` | Whitepapers and extracted references | Copy if needed | No (collected manually) |
| `maintainers-local/researcher-package/` | Compiled controls for review | Skip | Yes: `python scripts/compile_researcher_package.py` |
| `maintainers-local/reports/` | Generated analysis reports | Skip | Yes (regenerated by scripts) |
| `maintainers-local/tenant-evidence/` | Portal screenshots for UI verification | Machine-specific | No (tenant-specific captures) |
| `maintainers-local/tmp/` | Scratch artifacts | Skip | Not needed |
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

For Copilot prompt verification:

- **VS Code Copilot Chat:** Type `/review-learn-changes` — the repository prompt should be available.
- **Terminal `gh copilot`:** Expected behavior is quick shell help only; repository prompts are not loaded there.

## Questions?

Open an [Issue](https://github.com/judeper/FSI-AgentGov/issues) or contact the maintainers.

---

*FSI Agent Governance Framework v1.6.2 - May 2026*
