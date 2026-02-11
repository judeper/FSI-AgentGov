---
phase: 1
plan: 1
title: "Navigation & Solution Doc Sync"
status: Complete
---

# Plan 01-01 Summary: Navigation & Solution Doc Sync

## Objective

Fix user-facing broken links caused by exclude_docs configuration, add regulatory-mappings.md to site navigation, redirect CONTROL-INDEX.md links, and synchronize solution statuses between solutions-integration.md and solutions-index.md.

## Status: Complete

All 5 tasks completed successfully. `mkdocs build --strict` passes with zero warnings/errors.

## Tasks Completed

### Task 1: Fix exclude_docs and nav (BLK-01, BLK-02)
- **Commit:** `e12a872` — `fix(nav): remove regulatory-mappings from exclude_docs and add to nav`
- Removed `reference/regulatory-mappings.md` from `exclude_docs` in mkdocs.yml
- Added `Regulatory Mappings: reference/regulatory-mappings.md` to nav under Reference, after "NIST AI RMF Crosswalk"
- `controls/CONTROL-INDEX.md` remains excluded (intentional duplicate)

### Task 2: Redirect CONTROL-INDEX.md links (BLK-01, BLK-03)
- **Commit:** `e55465b` — `fix(docs): redirect CONTROL-INDEX.md links to controls/index.md`
- Updated 3 files:
  - `docs/getting-started/quick-start.md` — `[Control Index](../controls/CONTROL-INDEX.md)` → `[Control Index](../controls/index.md)`
  - `docs/reference/faq.md` — `[Control Index](../controls/CONTROL-INDEX.md)` → `[Control Index](../controls/index.md)`
  - `docs/reference/solutions-coverage-gaps.md` — `[CONTROL-INDEX](../controls/CONTROL-INDEX.md)` → `[Control Index](../controls/index.md)`
- Zero links to `CONTROL-INDEX.md` remain in published docs

### Task 3: Add Tier clarification in solutions-coverage-gaps.md (CSW-02 partial)
- **Commit:** absorbed into terminology sweep (`16eaae3`) or standalone (`6040af4`)
- Changed "Tier 1" → "Priority Tier 1" at 3 occurrences (lines 95, 135, 137)
- Changed "materiality (Tier 1/2/3)" → "materiality tier (Tier 1/2/3)" at line 214
- Tier usage now clearly distinguished from governance Zone concept

### Task 4: Sync solutions-integration.md with solutions-index.md (CSW-03)
- **Commit:** `7e68471` — `docs(solutions): sync solutions-integration.md statuses, versions, and Tier 2 entries with solutions-index.md`
- **Status updates (4):**
  - Deny Event Correlation: Work In Progress → Completed
  - Conditional Access Automation: Work In Progress → Completed
  - Compliance Dashboard: Work In Progress (Beta) → Completed
  - Scope Drift Monitor: Work In Progress → Completed
- **Version updates (3) in Repository Structure:**
  - deny-event-correlation-report: v1.1.0 → v2.0.0
  - conditional-access-automation: v1.0.0 → v1.1.0
  - scope-drift-monitor: v1.0.0 → v1.1.0
  - compliance-dashboard: v1.0.0-beta → v1.0.0
- **Added 5 Tier 2 solution references:**
  - Session Security Configurator — Solution-to-Control Mapping section + zone matrix + overview mermaid
  - File Upload Security Configurator — Solution-to-Control Mapping section + zone matrix + overview mermaid
  - Audit Configuration Validator — Solution-to-Control Mapping section + zone matrix + overview mermaid
  - Agent Access Governance Monitor — Solution-to-Control Mapping section + zone matrix + overview mermaid
  - Content Moderation Governance Monitor — Solution-to-Control Mapping section + zone matrix + overview mermaid
- **Updated deployment sequence** to reflect Phase 2 as Completed and reorganized phases
- **Updated Pillar Coverage** table with Tier 2 solutions
- **Updated summary statistics** (Pillar 1: 4→7 solutions)
- **Updated footer** version: v1.2.37 → v1.2.38

### Task 5: Update Cross-Solution Integration status (CSW-04)
- **Commit:** `f6b424d` — `docs(solutions): update Cross-Solution Integration status to Completed`
- Changed Cross-Solution Integration status from "Work In Progress" to "Completed" in solutions-index.md
- Updated Repository Structure entry in solutions-integration.md
- Updated summary statistics: Completed 8→9, Work In Progress 7→6

## File Manifest

| File | Action | Status |
|------|--------|--------|
| mkdocs.yml | Edited — exclude_docs + nav | ✅ |
| docs/getting-started/quick-start.md | Edited — CONTROL-INDEX link redirect | ✅ |
| docs/reference/faq.md | Edited — CONTROL-INDEX link redirect | ✅ |
| docs/reference/solutions-coverage-gaps.md | Edited — CONTROL-INDEX link + Tier clarification | ✅ |
| docs/framework/solutions-integration.md | Edited — statuses, versions, Tier 2 entries, stats | ✅ |
| docs/reference/solutions-index.md | Edited — Cross-Solution Integration → Completed | ✅ |

## Decisions Made

1. **Tier 2 solution sections** — Added dedicated Solution-to-Control Mapping subsections for all 5 Tier 2 solutions (SSC, FUS, ACV, AAM, CMM) rather than just cross-references, to maintain consistency with existing solution entries
2. **Overview mermaid diagram** — Added all 5 Tier 2 solutions with their pillar connections to make the 19-solution count visually accurate
3. **Deployment sequence reorganization** — Moved completed solutions (SDM, DEC, CD, CAA, SSC) into Phase 2 as "Completed"; added CSI to Phase 3; renumbered items 4-15
4. **Priority Tier disambiguation** — Used "Priority Tier" prefix and "materiality tier" phrasing to distinguish from Zone concept without adding a footnote

## Discovered Work

- The `docs/reference/solutions-coverage-gaps.md` line 118 still references Compliance Dashboard as "(beta)" — could be updated in a follow-up
- Several `docs/reference/solutions-coverage-gaps.md` Category 2/3 entries reference solutions that are now Completed (strikethrough with ADDRESSED links) — these are informational and don't need changes
- The 62-control count in quick-start.md line 238 says "61 total" — minor discrepancy that could be addressed separately

## Validation Results

- `mkdocs build --strict`: **PASS** (zero warnings, zero errors, built in ~25 seconds)
- All 3 CONTROL-INDEX redirects resolve correctly
- regulatory-mappings.md appears in nav under Reference
- All solution statuses in solutions-integration.md match solutions-index.md
- Summary statistics are internally consistent (9 Completed + 1 Validated + 6 WIP + 3 Planned = 19)
