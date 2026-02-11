---
phase: 1
plan: 2
title: "Terminology Sweep"
status: Complete
started: 2026-02-11
completed: 2026-02-11
---

# Plan 01-02 Summary: Terminology Sweep

## Objective

Complete the Azure AD → Microsoft Entra ID rename and Tier → Zone normalization across all published documentation.

## Status: Complete

## Tasks Completed

### Task 1: Azure AD → Microsoft Entra ID (17 instances across 12 files)

**Commit:** `d78b94d` — fix(terminology): rename Azure AD to Microsoft Entra ID across 12 files

All 17 "Azure AD" instances replaced with correct Microsoft branding:
- "Microsoft Entra admin center" for portal references (1 instance)
- "Microsoft Entra roles" for Entra-specific features (1 instance)
- "Microsoft Entra ID" for service references (13 instances)
- "Microsoft Entra app registration" for app registration references (2 instances)

**Verification:** `Select-String -Pattern "Azure AD"` returns only "Azure Administrator" (false positive — not an Azure AD reference).

### Task 2: Tier → Zone Normalization (governance zone references across 16 files)

**Commit:** `16eaae3` — fix(terminology): normalize Tier to Zone for governance zone references across 16 files

Changes by file:
- **2.8, 2.15, 2.17, 2.18, 2.19 portal-walkthroughs** — Governance level table headers: "Baseline (Tier 1)" → "Baseline (Zone 1)" etc.
- **2.9/portal-walkthrough.md** — Table headers, threshold table ("Tier" column → "Zone"), YAML config block ("KPIs by Tier" → "KPIs by Zone", zone labels updated)
- **2.9/verification-testing.md** — KPI tier references → Zone
- **2.9/powershell-setup.md** — Added inline comment `# Zone 2 governance classification` to `-Tier 2` code parameter
- **3.2/portal-walkthrough.md** — Alert names, KPI table headers, validation checklist, "Tier-specific" → "Zone-specific"
- **3.2/verification-testing.md** — Alert checklist, KPI verification table headers
- **4.1/portal-walkthrough.md** — "Tier 2+ sites" → "Zone 2+ sites", "Tier 3 sites" → "Zone 3 sites"
- **1.7 control** — "Tier 2-3" → "Zone 2-3"
- **2.2/verification-testing.md** — 24 instances: title, test cases, test tables, evidence checklists, attestation template
- **2.2/troubleshooting.md** — Issue title, symptoms, resolution text
- **2.1/verification-testing.md** — Attestation statement
- **1.2/verification-testing.md** — Expected result

### Task 3: Verify governance-fundamentals.md Level Context

**Result:** No change needed. Lines 167-178 clearly define "Governance Maturity Levels" (Level 1/2-3/4) as maturity levels mapped to Zones, with an info admonition reinforcing the distinction.

## File Manifest

| File | Changes |
|------|---------|
| docs/reference/portal-paths-quick-reference.md | 1 Azure AD rename |
| docs/playbooks/validation-testing/script-validation-guide.md | 4 Azure AD renames |
| docs/controls/pillar-1-security/1.22-information-barriers.md | 1 Azure AD rename |
| docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md | 1 Tier→Zone |
| docs/playbooks/control-implementations/2.15/troubleshooting.md | 2 Azure AD renames |
| docs/playbooks/control-implementations/2.14/powershell-setup.md | 1 Azure AD rename |
| docs/playbooks/control-implementations/1.8/powershell-setup.md | 2 Azure AD renames |
| docs/playbooks/control-implementations/1.18/portal-walkthrough.md | 1 Azure AD rename |
| docs/playbooks/control-implementations/1.12/portal-walkthrough.md | 1 Azure AD rename |
| docs/playbooks/control-implementations/1.12/troubleshooting.md | 1 Azure AD rename |
| docs/playbooks/control-implementations/1.16/troubleshooting.md | 1 Azure AD rename |
| docs/playbooks/advanced-implementations/microsoft-audit-reporting-tools.md | 1 Azure AD rename |
| docs/playbooks/advanced-implementations/platform-change-governance/implementation-path-a.md | 1 Azure AD rename |
| docs/playbooks/control-implementations/2.8/portal-walkthrough.md | Tier→Zone header |
| docs/playbooks/control-implementations/2.9/portal-walkthrough.md | Tier→Zone (table, headers, YAML) |
| docs/playbooks/control-implementations/2.9/verification-testing.md | Tier→Zone (3 KPI lines) |
| docs/playbooks/control-implementations/2.9/powershell-setup.md | Zone comment added |
| docs/playbooks/control-implementations/2.17/portal-walkthrough.md | Tier→Zone header |
| docs/playbooks/control-implementations/2.15/portal-walkthrough.md | Tier→Zone header |
| docs/playbooks/control-implementations/2.18/portal-walkthrough.md | Tier→Zone header |
| docs/playbooks/control-implementations/2.19/portal-walkthrough.md | Tier→Zone header |
| docs/playbooks/control-implementations/3.2/portal-walkthrough.md | Tier→Zone (alerts, KPIs, checklist) |
| docs/playbooks/control-implementations/3.2/verification-testing.md | Tier→Zone (checklist, KPI table) |
| docs/playbooks/control-implementations/4.1/portal-walkthrough.md | Tier→Zone (RCD table) |
| docs/playbooks/control-implementations/2.2/verification-testing.md | Tier→Zone (24 instances) |
| docs/playbooks/control-implementations/2.2/troubleshooting.md | Tier→Zone (3 instances) |
| docs/playbooks/control-implementations/2.1/verification-testing.md | Tier→Zone (attestation) |
| docs/playbooks/control-implementations/1.2/verification-testing.md | Tier→Zone (expected result) |
| docs/framework/governance-fundamentals.md | Verified — no change needed |

## Decisions Made

1. "Azure Administrator" on line 133 of 1.7 control file is NOT "Azure AD" — left unchanged (correct)
2. `-Tier 2` code parameter in 2.9/powershell-setup.md kept as-is (code parameter) with inline Zone clarification comment
3. Out-of-scope Tier usages confirmed unchanged: 2.4/* (DR tiers), 2.6/* (model risk tiers), 2.7/* (vendor tiers), solutions-integration.md (solution maturity)
4. Many additional files with "Tier 1/2/3" governance-zone references exist beyond this plan's scope (1.5, 1.11, 1.14-1.23, etc.) — these should be captured as discovered work

## Discovered Work

- **~50+ additional Tier→Zone conversions** exist across playbook files not listed in this plan (1.5, 1.11, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19, 1.20, 1.21, 1.22, 1.23, 1.4, 1.2/portal-walkthrough, 1.2/troubleshooting, and more). These should be addressed in a follow-up plan.

## Validation Results

- `mkdocs build --strict`: **PASS** — zero errors, zero warnings (built in 27.01 seconds)
- Azure AD grep verification: **PASS** — zero matches (excluding "Azure Administrator" false positive)
- Tier→Zone verification: **PASS** — all plan-listed files converted; out-of-scope files confirmed unchanged
