---
phase: 1
plan: 4
title: "Playbook File Tier→Zone Sweep"
status: complete
started: 2026-02-11
completed: 2026-02-11
gap_closure: true
---

# Summary: Plan 01-04 — Playbook File Tier→Zone Sweep

## Result: COMPLETE

All governance-zone "Tier 1/2/3" references converted to "Zone 1/2/3" in 29 playbook files.

## Commits

| Commit | Description | Files |
|--------|-------------|-------|
| `069325a` | fix(playbooks): complete Tier→Zone sweep in 29 playbook files (01-04) | 29 files |

## Changes by File (29 files, 64 substitutions)

### High-Instance Files

| File | Substitutions |
|------|:---:|
| 2.2/portal-walkthrough.md | 14 |
| 1.5/portal-walkthrough.md | 10 |
| 1.11/verification-testing.md | 8 |
| 2.1/portal-walkthrough.md | 7 |
| 1.7/portal-walkthrough.md | 4 |
| 1.15/portal-walkthrough.md | 3 |

### Standard-Instance Files

| File | Substitutions |
|------|:---:|
| 1.2/portal-walkthrough.md | 2 |
| 1.4/portal-walkthrough.md | 2 |
| 1.5/verification-testing.md | 2 |
| 1.8/portal-walkthrough.md | 2 |
| 1.8/verification-testing.md | 2 |
| 1.11/portal-walkthrough.md | 2 |

### Single-Instance Files (1 each)

1.2/troubleshooting.md, 1.14/portal-walkthrough.md, 1.16/portal-walkthrough.md, 1.17/portal-walkthrough.md, 1.18/portal-walkthrough.md, 1.19/portal-walkthrough.md, 1.20/portal-walkthrough.md, 1.21/portal-walkthrough.md, 1.22/portal-walkthrough.md, 1.23/portal-walkthrough.md, 2.10/portal-walkthrough.md, 2.11/portal-walkthrough.md, 2.12/portal-walkthrough.md, 2.13/portal-walkthrough.md, 2.14/portal-walkthrough.md, 2.16/portal-walkthrough.md, 2.20/portal-walkthrough.md

## Exclusions Confirmed

- 2.4/* playbooks — DR/BCP recovery tiers (legitimate)
- 2.6/* playbooks — Model risk tiers per Fed SR 11-7 (legitimate)
- 2.7/verification-testing.md — Vendor assessment tiers (legitimate)
- 2.9/powershell-setup.md — `-Tier 2` code parameter (already has Zone comment)

## Discovered Work (Out of Scope)

Additional "Tier" references found outside the 29 planned files:
- 1.1/portal-walkthrough.md — "Governance Tier" column name (1 instance)
- 1.17/powershell-setup.md — `FSI-Endpoint-Tier3` policy name in code (2 instances)
- 1.24/powershell-setup.md — `PricingTier` Azure API property (4 instances, NOT governance-zone)
- 2.2/powershell-setup.md — control name references "Tier Classification" (4 instances)
- 2.2/troubleshooting.md — control name + "Tier classification" text (2 instances)
- 3.1/portal-walkthrough.md — "Governance Tier" + "Criticality Tier" (2 instances)
- 3.1/verification-testing.md — "Governance Tier-Specific Testing" (1 instance)
- 3.2/verification-testing.md — "Governance Tier-Specific Testing" (1 instance)

Most are column headers, code identifiers, or control-name references — not straightforward governance-zone Tier→Zone conversions.

## Validation

- `mkdocs build --strict` — PASSED
- 29/29 files successfully converted
