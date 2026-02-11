---
phase: 1
plan: 3
title: "Control File Tier→Zone Sweep + Minor Fixes"
status: complete
started: 2026-02-11
completed: 2026-02-11
gap_closure: true
---

# Summary: Plan 01-03 — Control File Tier→Zone Sweep + Minor Fixes

## Result: COMPLETE

All governance-zone "Tier 1/2/3" references converted to "Zone 1/2/3" in 9 control files. Minor fixes applied.

## Commits

| Commit | Description | Files |
|--------|-------------|-------|
| `e4517c4` | fix(controls): complete Tier→Zone sweep in 9 control files + minor fixes (01-03) | 11 files |

## Changes by File

### Tier→Zone Conversions (9 control files, 28 substitutions)

| File | Substitutions |
|------|:---:|
| 1.6-microsoft-purview-dspm-for-ai.md | 1 |
| 1.8-runtime-protection-and-external-threat-detection.md | 2 |
| 1.11-conditional-access-and-phishing-resistant-mfa.md | 3 |
| 1.14-data-minimization-and-agent-scope-control.md | 5 |
| 1.15-encryption-data-in-transit-and-at-rest.md | 4 |
| 2.1-managed-environments.md | 5 |
| 2.2-environment-groups-and-tier-classification.md | 7 (title preserved) |
| 2.9-agent-performance-monitoring-and-optimization.md | 4 |
| 2.10-patch-management-and-system-updates.md | 2 |

### Minor Fixes (2 files)

| File | Change |
|------|--------|
| quick-start.md | "61 total" → "62 total" (control count) |
| solutions-coverage-gaps.md | Removed 3 "(beta)" refs + 1 "v1.0.0-beta" → "v1.0.0" |

## Exclusions Confirmed

- Control 2.4 (DR/BCP recovery tiers) — legitimate, not changed
- Control 2.6 (model risk tiers per Fed SR 11-7) — legitimate, not changed
- Control 2.7 (vendor assessment tiers) — legitimate, not changed
- Control 2.2 filename — kept as-is (renaming would break links)
- Control 2.2 title "Tier Classification" — preserved per plan

## Decisions Made

- Control 1.11: "enterprise tier" rewritten as "enterprise zone", "tier requirements" → "zone requirements" (contextual conversion beyond simple Tier→Zone)
- Control 1.14: "tiered" adjective → "zone-based" (contextual conversion)
- Control 2.2: Title "Tier Classification" preserved; all body text Tier→Zone converted

## Validation

- `mkdocs build --strict` — PASSED
- `python scripts/verify_controls.py` — PASSED (62/62 controls valid)
