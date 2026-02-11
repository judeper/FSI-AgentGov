---
phase: 3
plan: 2
title: "Housekeeping — EXPECTED.md + v11 REQUIREMENTS"
status: complete
started: 2026-02-11
completed: 2026-02-11
---

# Plan 03-02 Summary: Housekeeping — Screenshot Specs & v11 Requirements

## Status: COMPLETE

## Commits

| Hash | Message |
|------|---------|
| `8926b68` | `docs(images): create EXPECTED.md specs for 10 missing controls` |
| `35cbffd` | `docs(planning): update v11 REQUIREMENTS.md delivery status` |

## Tasks Completed

### Task 1: Create 10 Missing EXPECTED.md Files (HSK-02)

Created screenshot specification files for all 10 controls that were missing EXPECTED.md. Each file was derived by reading the actual control document and extracting portal paths, configuration points, and verification criteria.

| File | Control | Screenshots Specified |
|------|---------|---------------------|
| `docs/images/1.22/EXPECTED.md` | Information Barriers for AI Agents | 5 (Purview segments, barrier policies, SharePoint alignment, wall-crossing, PowerShell) |
| `docs/images/1.23/EXPECTED.md` | Step-Up Authentication for Agent Operations | 6 (auth contexts, CA policy, auth strength, session controls, PIM, report-only) |
| `docs/images/1.24/EXPECTED.md` | Defender AI-SPM | 6 (AI-SPM plan, workload discovery, attack path, recommendations, multi-cloud, dashboard) |
| `docs/images/2.17/EXPECTED.md` | Multi-Agent Orchestration Limits | 4 (Copilot Studio orchestration, App Insights telemetry, PPAC monitoring, combined Agent Card) |
| `docs/images/2.18/EXPECTED.md` | Automated Conflict of Interest Testing | 5 (evaluation framework, COI scenarios, pipeline, prompt audit, conflict report) |
| `docs/images/2.19/EXPECTED.md` | Customer AI Disclosure and Transparency | 5 (AI greeting, capability disclosure, transfer to agent, data use, state-specific) |
| `docs/images/2.20/EXPECTED.md` | Adversarial Testing and Red Team Framework | 5 (red team docs, attack library, golden dataset, CI/CD pipeline, remediation tracking) |
| `docs/images/2.21/EXPECTED.md` | AI Marketing Claims and Substantiation | 5 (claims inventory, review workflow, substantiation library, quarterly review, FINRA 2210) |
| `docs/images/3.10/EXPECTED.md` | Hallucination Feedback Loop | 6 (CSAT settings, analytics, tracking list, remediation workflow, trend dashboard, App Insights) |
| `docs/images/4.7/EXPECTED.md` | Microsoft 365 Copilot Data Governance | 7 (M365 Admin Copilot, license inventory, RCD, plugins, web search, usage analytics, PowerShell) |

### Task 2: Update v11 REQUIREMENTS.md Checkboxes (HSK-03)

Marked all 38 requirements (RTF-01 through RTF-10, RTA-01 through RTA-10, TVN-01 through TVN-06, XRL-01 through XRL-06, SCF-01 through SCF-06, GBD-01 through GBD-08) as delivered `[x]`.

**Evidence basis:**
- v11-ROADMAP.md shows all 6 phases and 12 plans marked complete `[x]`
- SUMMARY files in phases 4, 5, 6 explicitly confirm all XRL, SCF, GBD requirements delivered
- Codebase spot-checks confirm key deliverables:
  - RTF-01: `fsi_results_json` (plural) present in both flow JSON files
  - RTA-01: "24 controls" in executive-summary.md, "62 controls" in governance-fundamentals.md
  - TVN-05: "Agent 365" entry present in glossary.md
  - SCF-01: `$isBlock` recalculated inside foreach loop in Test-PolicyCompliance.ps1
  - SCF-02: `FunctionsToExport = @()` in conditional-access-automation.psd1
  - SCF-03: `SkuPartNumber` used in 4.7/powershell-setup.md
- RTF-04 addressed via alternative approach in SCF-02 (manifest exports emptied rather than creating the 3 helper scripts)

## File Manifest

| Action | File |
|--------|------|
| Created | `docs/images/1.22/EXPECTED.md` |
| Created | `docs/images/1.23/EXPECTED.md` |
| Created | `docs/images/1.24/EXPECTED.md` |
| Created | `docs/images/2.17/EXPECTED.md` |
| Created | `docs/images/2.18/EXPECTED.md` |
| Created | `docs/images/2.19/EXPECTED.md` |
| Created | `docs/images/2.20/EXPECTED.md` |
| Created | `docs/images/2.21/EXPECTED.md` |
| Created | `docs/images/3.10/EXPECTED.md` |
| Created | `docs/images/4.7/EXPECTED.md` |
| Modified | `.planning/milestones/v11-REQUIREMENTS.md` |

## Decisions Made

1. **RTF-04 marked as delivered** — The runtime issue (module manifest referencing non-existent functions) was resolved by SCF-02's approach of emptying `FunctionsToExport` rather than creating the 3 helper scripts. The requirement's "or" phrasing ("remove exports for non-existent functions, or create the functions") in SCF-02 confirms this was an accepted alternative.
2. **All 38 requirements marked delivered** — v11-ROADMAP.md unanimously marks all phases complete, corroborated by SUMMARY files and codebase evidence. No requirement showed evidence of incomplete delivery.
3. **Process-based controls (2.17, 2.18, 2.20, 2.21)** — EXPECTED.md files for these controls note that screenshots demonstrate custom implementations and process artifacts rather than platform configuration, consistent with the controls' nature.

## Discovered Work

- None. Both tasks completed cleanly with no blockers.
