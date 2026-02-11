# Phase 2 Research: Quality Automation & Infrastructure

**Phase:** 02-quality-automation-infrastructure
**Date:** 2026-02-11
**Researcher:** copilot

## Phase Goal

Build automated quality gates (language linter, CI integration) and align templates/validation scripts with current conventions.

## Requirements

| ID | Description | Target Files |
|----|-------------|--------------|
| QAI-01 | Create verify_language_rules.py linter | scripts/verify_language_rules.py (new) |
| QAI-02 | Add verify_controls.py to CI workflow | .github/workflows/publish_docs.yml |
| QAI-03 | Sync control-setup-template.md with conventions | docs/templates/control-setup-template.md |
| QAI-04 | Update verify_templates.py for current footers | scripts/verify_templates.py |
| QAI-05 | Add playbook existence check to verify_controls.py | scripts/verify_controls.py |

## Current State Analysis

### QAI-01: Language Linter (NEW FILE)

**Target:** `scripts/verify_language_rules.py` — does not exist yet.

**Source of truth:** `.github/instructions/fsi-language-rules.instructions.md` defines:

| Category | Patterns |
|----------|----------|
| Prohibited phrases | "ensures compliance", "guarantees", "will prevent", "eliminates risk" |
| Overclaim patterns | "ensures you meet", "guarantees regulatory compliance", "eliminates the need for" |
| Role naming violations | "Global Administrator" (use "Entra Global Admin"), "Compliance Administrator" (use "Purview Compliance Admin") |

**Design considerations:**
- Should scan all `docs/**/*.md` files
- Should exclude template files (they contain placeholder text)
- Should report file, line number, and matching phrase
- Exit code 1 on any violation (for CI integration)
- Case-insensitive matching
- Pattern-based: regex for phrase detection, not exact string match (handles plurals, variations)
- Must handle Windows UTF-8 encoding (consistent with existing scripts)

**Existing patterns to follow:** `verify_controls.py` uses `Path`, `re`, `sys` with Windows encoding fix. Follow same structure.

### QAI-02: CI Integration

**Target:** `.github/workflows/publish_docs.yml`

**Current state:** Workflow runs on `push` to `main`. Steps:
1. Checkout
2. Block internal artifacts
3. Configure git credentials
4. Setup Python 3.x
5. Cache MkDocs material
6. Install MkDocs
7. `mkdocs build --strict`
8. Deploy to GitHub Pages

**Gap:** `verify_controls.py` is not executed. It should run after Python setup and before deploy.

**Design considerations:**
- Add step after "Install MkDocs" step (Python is already set up at that point)
- Step name: "Validate Control Structure"
- Command: `python scripts/verify_controls.py`
- Should fail the build on validation errors (script already exits with code 1 on failure)
- Consider also adding `verify_language_rules.py` to CI since we're creating it in QAI-01

### QAI-03: Template Sync

**Target:** `docs/templates/control-setup-template.md`

**Current template state:**
- Uses `## Implementation Guides` ← should be `## Implementation Playbooks` (all 62 controls use "Playbooks")
- Footer: `*Updated: January 2026 | Version: v1.2 | UI Verification Status: Current*`
- Should be: `*Updated: February 2026 | Version: v1.3 | UI Verification Status: Current*`

**Changes needed:**
1. Rename `## Implementation Guides` → `## Implementation Playbooks`
2. Update footer date: `January 2026` → `February 2026`
3. Update footer version: `v1.2` → `v1.3`

### QAI-04: verify_templates.py Footer Values

**Target:** `scripts/verify_templates.py`

**Current state:** Script checks for these required snippets in the template:
```python
required_snippets = [
    "**Control ID:**",
    "**Pillar:**",
    "**Regulatory Reference:**",
    "Updated: January 2026",
    "Version: v1.1",
    "UI Verification Status:",
]
```

**Gap:** `"Updated: January 2026"` and `"Version: v1.1"` are stale. After QAI-03, template will have `February 2026` and `v1.3`.

**Also:** The required_sections list has `"## Implementation Guides"` — should be `"## Implementation Playbooks"` to match the template after QAI-03 change.

**Changes needed:**
1. Update `"Updated: January 2026"` → `"Updated: February 2026"`
2. Update `"Version: v1.1"` → `"Version: v1.3"`
3. Update `"## Implementation Guides"` → `"## Implementation Playbooks"` in required_sections

### QAI-05: Playbook Existence Check in verify_controls.py

**Target:** `scripts/verify_controls.py`

**Current state:** Script validates control file structure (headings, metadata, footers) but does NOT check that the 4 standard playbook files exist per control.

**Current playbook state:** All 62 controls have all 4 files:
- `portal-walkthrough.md`
- `powershell-setup.md`
- `verification-testing.md`
- `troubleshooting.md`

Located in: `docs/playbooks/control-implementations/{control-id}/`

**Design considerations:**
- Extract control ID from filename (e.g., `1.1-restrict-...md` → `1.1`)
- Check for directory: `docs/playbooks/control-implementations/{id}/`
- Check for 4 required files in that directory
- Report missing files as validation failures
- This is a regression guard — currently all 62 controls pass

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Language linter false positives | Dev friction, ignored linter | Careful regex design; exclude template files; test against full corpus before merge |
| CI step slows deployment | Longer deploy times | verify_controls.py runs in ~2s locally; minimal impact |
| Template footer churn | Frequent updates needed | Accept that footer values change with each release; document update process |

## Recommendations

1. **Plan A (Worktree A):** Language linter + CI integration — these are new files / workflow changes that don't touch existing docs or validation scripts
2. **Plan B (Worktree B):** Template + validation scripts — these modify existing files in docs/templates/ and scripts/
3. **No file overlap** between plans — safe for parallel worktree execution
4. Both plans are Wave 1 (independent of each other)

---
*Research completed: 2026-02-11*
