---
phase: 2
plan: 1
status: complete
started: 2026-02-11
completed: 2026-02-11
---

# Summary 02-01: Language Linter & CI Integration

## Status: COMPLETE

## Requirements Delivered

- **QAI-01:** `scripts/verify_language_rules.py` created — scans 477 docs, catches 5 prohibited phrase patterns, exits 0 on current corpus
- **QAI-02:** `.github/workflows/publish_docs.yml` updated — `verify_controls.py` and `verify_language_rules.py` steps added before `mkdocs build --strict`

## Commits

| Hash | Message |
|------|---------|
| fad8cd1 | feat(quality): add FSI language linter and CI validation steps (QAI-01, QAI-02) |

## File Manifest

| File | Action | Description |
|------|--------|-------------|
| `scripts/verify_language_rules.py` | CREATED | FSI language rules linter (5 prohibited patterns, excludes templates + disclaimer) |
| `.github/workflows/publish_docs.yml` | MODIFIED | Added 2 validation steps before mkdocs build |
| `docs/playbooks/advanced-implementations/platform-change-governance/architecture.md` | MODIFIED | Fixed "Retry Guarantees" → "Retry Assurances" (linter violation) |

## Decisions Made

- **Disclaimer exclusion:** `docs/disclaimer.md` excluded from language scanning — legal disclaimers appropriately use words like "ensure compliance" and "guarantee" in cautionary/negative context
- **Architecture fix:** "ADO Service Hook Retry Guarantees" renamed to "Retry Assurances" in architecture.md table (technical term, but matched linter pattern)

## Validation

- `python scripts/verify_language_rules.py` → exit 0 (0 violations)
- `python scripts/verify_controls.py` → exit 0
- `mkdocs build --strict` → success

---
*Summary created: 2026-02-11*
