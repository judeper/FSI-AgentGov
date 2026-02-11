---
phase: 1
title: "Broken Links & Content Consistency"
verification_date: 2026-02-11
overall_status: gaps_found
---

# Phase 01 Verification: Broken Links & Content Consistency

## Phase Goal

Resolve user-facing broken links caused by `exclude_docs` and complete the Azure AD / Tier→Zone terminology sweeps started in v11.

## Plans Reviewed

- `01-01-SUMMARY.md` — Navigation & Solution Doc Sync (Complete)
- `01-02-SUMMARY.md` — Terminology Sweep (Complete)

---

## Per-Criterion Verification

### Criterion 1: No docs link to files excluded via `exclude_docs` (or exclusions removed)

**Result: PASSED**

Current `exclude_docs` block (mkdocs.yml lines 54-59):

```yaml
exclude_docs: |
  images/
  scripts/
  templates/
  reference/raci-matrix.md
  controls/CONTROL-INDEX.md
```

Evidence:
- `reference/raci-matrix.md` — zero inbound links from published docs (`grep` returned 0 matches)
- `controls/CONTROL-INDEX.md` — only link is in `docs/templates/README.md` (line 46), which is itself excluded via `templates/`
- `images/`, `scripts/`, `templates/` — infrastructure directories, not linked from content docs

No published doc links to any excluded file.

---

### Criterion 2: `regulatory-mappings.md` reachable from site navigation

**Result: PASSED**

Evidence: mkdocs.yml line 590:
```yaml
- Regulatory Mappings: reference/regulatory-mappings.md
```

Listed under Reference section in navigation. Confirmed reachable in built site.

---

### Criterion 3: `CONTROL-INDEX.md` reachable from site navigation (or linking docs updated)

**Result: PASSED**

`CONTROL-INDEX.md` remains excluded (intentional — `controls/index.md` serves as the published equivalent). All 3 inbound links were redirected in Plan 01-01:
- `docs/getting-started/quick-start.md` → now links to `../controls/index.md`
- `docs/reference/faq.md` → now links to `../controls/index.md`
- `docs/reference/solutions-coverage-gaps.md` → now links to `../controls/index.md`

Grep for `CONTROL-INDEX.md` in `docs/` returns only `docs/templates/README.md` (excluded via `templates/`).

---

### Criterion 4: Zero "Azure AD" instances remain in published docs

**Result: PASSED**

Grep for "Azure AD" in `docs/` returns 1 match:
- `docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md` line 133: `"Azure Administrator"` — this is a role name, NOT an "Azure AD" reference. Confirmed false positive.

All 17 actual "Azure AD" instances were renamed in Plan 01-02 commit `d78b94d`.

---

### Criterion 5: Zero "Tier 1/2/3" or "Level 1/2/3" instances remain without mapping note

**Result: FAILED — ~80 governance-zone "Tier" references remain unconverted across ~35 files**

#### "Tier 1/2/3" Analysis

Plan 01-02 converted Tier→Zone in 16 files but acknowledged **"~50+ additional Tier→Zone conversions exist across playbook files not listed in this plan"** as discovered work.

Verified remaining "Tier [123]" instances (excluding legitimate uses in 2.4/DR, 2.6/model-risk, 2.7/vendor playbooks and solutions-* files):

**Control files with unconverted governance-zone Tier references (8 files, ~20 instances):**
- `1.6`, `1.8`, `1.11`, `1.14`, `1.15` (Pillar 1)
- `2.1`, `2.2`, `2.9`, `2.10` (Pillar 2)

**Playbook files with unconverted governance-zone Tier references (~27 files, ~60 instances):**
- `1.2`, `1.4`, `1.5`, `1.7`, `1.8`, `1.11`, `1.14`, `1.15`, `1.16`, `1.17`, `1.18`, `1.19`, `1.20`, `1.21`, `1.22`, `1.23` portal-walkthroughs
- `1.5`, `1.8`, `1.11` verification-testing
- `1.2` troubleshooting
- `2.1`, `2.2`, `2.10`, `2.11`, `2.12`, `2.13`, `2.14`, `2.16`, `2.20` portal-walkthroughs

Common patterns remaining:
- `"Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3)"` table headers → should be Zone
- `"Tier 1 / Tier 2 / Tier 3"` governance classification references → should be Zone
- `2.2/portal-walkthrough.md`: 11 instances including section headings like "Tier 1 - Personal Productivity Rules"

**Legitimate "Tier" references confirmed (no action needed):**
- `2.4/*` — DR/BCP recovery tiers (Tier 1 Critical, Tier 2 High, Tier 3 Medium)
- `2.6/*` — Model risk tiers per Fed SR 11-7 (Tier 1 High Risk, Tier 2 Medium Risk, Tier 3 Low Risk)
- `2.7/*` — Vendor assessment tiers
- `solutions-index.md` — "Tier 2 solutions" (solution maturity classification)
- `solutions-coverage-gaps.md` — "Priority Tier 1" (disambiguated in Plan 01-01)
- `2.9/powershell-setup.md` — `-Tier 2` code parameter (kept with inline Zone comment)

#### "Level 1/2/3" Analysis

50 matches found. All are legitimate uses falling into two categories:

1. **Support escalation levels** (~20 instances across troubleshooting files): "Level 1: SharePoint Admin", "Level 2: Microsoft 365 Admin", "Level 3: Microsoft Support" — standard IT escalation, not governance zones.

2. **Governance maturity levels** (~30 instances across portal-walkthroughs and verification files): "Baseline (Level 1)", "Recommended (Level 2-3)", "Regulated (Level 4)" — defined in `governance-fundamentals.md` lines 167-178 with info admonition distinguishing from zones.

**Level references: No gaps.** All are contextually distinct from governance zones.

---

### Criterion 6: `solutions-integration.md` statuses and versions match `solutions-index.md`

**Result: PASSED**

Cross-referenced all 19 solutions:

| Solution | solutions-index.md | solutions-integration.md | Match |
|----------|-------------------|--------------------------|-------|
| ELM | v1.1.2 / Completed | Completed | ✓ |
| MCM | v2.1.1 / Completed | Completed | ✓ |
| PGC | v1.0.8 / Completed | Completed | ✓ |
| DEC | v2.0.0 / Completed | Completed | ✓ |
| FUS | v1.0.0 / WIP | Work In Progress | ✓ |
| ACV | v1.0.0 / WIP | Work In Progress | ✓ |
| SSC | v1.0.0 / Completed | Completed | ✓ |
| AAM | v1.0.0 / WIP | Work In Progress | ✓ |
| CMM | v1.0.0 / WIP | Work In Progress | ✓ |
| FINRA | v1.0.0 / Validated | Validated | ✓ |
| CAA | v1.1.0 / Completed | Completed | ✓ |
| CD | v1.0.0 / Completed | Completed | ✓ |
| SoDD | v1.0.0 / WIP | Work In Progress | ✓ |
| SDM | v1.1.0 / Completed | Completed | ✓ |
| RSV | v1.0.0 / WIP | Work In Progress | ✓ |
| COI | v1.0.0 / Planned | Planned | ✓ |
| HT | v1.0.0 / Planned | Planned | ✓ |
| DRT | v1.0.0 / Planned | Planned | ✓ |
| CSI | v1.0.0 / Completed | Completed | ✓ |

All 19 statuses match. Version updates (DEC v2.0.0, CAA v1.1.0, SDM v1.1.0, CD v1.0.0) applied in Plan 01-01.

---

### Criterion 7: Cross-Solution Integration status updated from WIP to Completed

**Result: PASSED**

Evidence:
- `solutions-index.md` line 37: `| Cross-Solution Integration | v1.0.0 | Completed |`
- `solutions-integration.md` line 515: Repository link present under Cross-Solution Integration section
- Updated in Plan 01-01 commit `f6b424d`

---

## Build Validation

```
$ python -m mkdocs build --strict
INFO - Cleaning site directory
INFO - Building documentation to directory: C:\dev\FSI-AgentGov\site
INFO - Documentation built in 33.89 seconds
```

**Result: PASSED** — zero warnings, zero errors.

## Control Validation

```
$ python scripts/verify_controls.py
✓ Docs anchor validation passed (no broken #fragments).
Found 62 controls in Index.
Found 62 content files in Pillars.
SUCCESS: All controls have corresponding files.
✓ All control files meet required beta structure + footer standards.
```

**Result: PASSED** — 62/62 controls valid.

---

## Overall Status: **GAPS_FOUND**

| # | Criterion | Result |
|---|-----------|--------|
| 1 | No docs link to excluded files | **PASSED** |
| 2 | regulatory-mappings.md in nav | **PASSED** |
| 3 | CONTROL-INDEX.md links updated | **PASSED** |
| 4 | Zero "Azure AD" instances | **PASSED** |
| 5 | Zero "Tier/Level" without mapping note | **FAILED** |
| 6 | solutions-integration.md sync | **PASSED** |
| 7 | Cross-Solution Integration → Completed | **PASSED** |

**6 of 7 criteria passed. 1 criterion failed.**

## Gaps Requiring Follow-Up

### Gap 1: ~80 governance-zone "Tier 1/2/3" references remain across ~35 files

The Plan 01-02 terminology sweep converted Tier→Zone in 16 files but scoped out the remaining ~35 files as discovered work. These files use "Tier 1/2/3" to mean governance zones (Zone 1/2/3) without disambiguation notes.

**Recommended follow-up:** A dedicated Tier→Zone sweep phase targeting:
- ~8 control files (controls that use "Tier" for zone-specific configuration tables)
- ~27 playbook files (portal-walkthroughs and verification-testing with "Baseline (Tier 1)" pattern)
- Special handling for control 2.2 "Environment Groups and Tier Classification" which uses "Tier" in its control name

**Not in scope:** Legitimate Tier references in 2.4 (DR), 2.6 (model risk), 2.7 (vendor), solutions files — these are correctly distinct concepts.

### Discovered Issues (Minor)

From Plan 01-01 Summary:
- `solutions-coverage-gaps.md` line 118 still references Compliance Dashboard as "(beta)"
- `quick-start.md` line 238 says "61 total" controls (should be 62)
