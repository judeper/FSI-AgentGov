# Phase 1 Research: Broken Links & Content Consistency

**Researcher:** copilot
**Date:** 2026-02-11
**Phase goal:** Resolve user-facing broken links caused by exclude_docs and complete the Azure AD / Tier→Zone terminology sweeps started in v11

---

## BLK-01: exclude_docs Broken Links

### Current State

The `exclude_docs` block in mkdocs.yml (lines 54-59) excludes six paths:

```yaml
exclude_docs: |
  images/
  scripts/
  templates/
  reference/raci-matrix.md
  reference/regulatory-mappings.md
  controls/CONTROL-INDEX.md
```

### Broken Link Instances

**Links to `reference/regulatory-mappings.md` (2 inbound):**

| Source File | Line | Link Text |
|------------|------|-----------|
| docs/reference/nist-ai-rmf-crosswalk.md | 63 | `[Regulatory Mappings](regulatory-mappings.md)` |
| docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md | 105 | `[Regulatory Mappings](../../reference/regulatory-mappings.md)` |

**Links to `controls/CONTROL-INDEX.md` (3 inbound):**

| Source File | Line | Link Text |
|------------|------|-----------|
| docs/reference/faq.md | 169 | `[Control Index](../controls/CONTROL-INDEX.md)` |
| docs/reference/solutions-coverage-gaps.md | 354 | `[CONTROL-INDEX](../controls/CONTROL-INDEX.md)` |
| docs/getting-started/quick-start.md | 229 | `[Control Index](../controls/CONTROL-INDEX.md)` |

**Links to `reference/raci-matrix.md`:** 0 inbound — no fix needed.
**Links to `templates/`, `images/`, `scripts/`:** No navigable markdown links — no fix needed.

### Recommended Approach

- **regulatory-mappings.md:** Remove from `exclude_docs` and add to mkdocs.yml `nav:` under Reference. It's core content for the FSI audience.
- **CONTROL-INDEX.md:** Update the 3 inbound links → `controls/index.md` (which is already in nav). Avoids duplication with controls/index.md.

---

## BLK-02: regulatory-mappings.md Reachability

- **File exists:** Yes, at docs/reference/regulatory-mappings.md
- **In mkdocs.yml nav:** No
- **In exclude_docs:** Yes
- **Inbound links:** 2 docs link to it

**Action:** Remove from exclude_docs, add to nav under Reference (after NIST AI RMF Crosswalk). Low risk — file is complete and useful.

---

## BLK-03: CONTROL-INDEX.md Reachability

- **File exists:** Yes, at docs/controls/CONTROL-INDEX.md
- **In mkdocs.yml nav:** No — controls/index.md serves as the nav entry
- **In exclude_docs:** Yes
- **Inbound links:** 3 docs link to it

**Action:** Redirect 3 inbound links to controls/index.md. Keep CONTROL-INDEX.md excluded to avoid duplication.

---

## CSW-01: Azure AD → Microsoft Entra ID Sweep

### 17 True Instances Found

| # | File | Line | Context | Replacement |
|---|------|------|---------|-------------|
| 1 | docs/reference/portal-paths-quick-reference.md | 111 | "Azure AD Admin Center" | "Microsoft Entra admin center" |
| 2 | docs/playbooks/validation-testing/script-validation-guide.md | 190 | "Azure AD sign-in data" (comment) | "Entra ID sign-in data" |
| 3 | docs/playbooks/validation-testing/script-validation-guide.md | 241 | "Azure AD sign-ins" (table) | "Microsoft Entra ID sign-ins" |
| 4 | docs/playbooks/validation-testing/script-validation-guide.md | 242 | "Azure AD directory changes" | "Microsoft Entra ID directory changes" |
| 5 | docs/playbooks/validation-testing/script-validation-guide.md | 291 | "Azure AD logs" | "Microsoft Entra ID logs" |
| 6 | docs/controls/pillar-1-security/1.22-information-barriers.md | 31 | "Azure AD attributes" | "Microsoft Entra ID attributes" |
| 7 | docs/playbooks/control-implementations/2.15/troubleshooting.md | 76 | "exist in Azure AD" | "exist in Microsoft Entra ID" |
| 8 | docs/playbooks/control-implementations/2.15/troubleshooting.md | 116 | "valid Azure AD group" | "valid Microsoft Entra ID group" |
| 9 | docs/playbooks/control-implementations/2.14/powershell-setup.md | 29 | "Queries Azure AD for users" | "Queries Microsoft Entra ID for users" |
| 10 | docs/playbooks/control-implementations/1.8/powershell-setup.md | 62 | "Azure AD tenant ID" | "Microsoft Entra ID tenant ID" |
| 11 | docs/playbooks/control-implementations/1.8/powershell-setup.md | 438 | "Azure AD tenant ID" | "Microsoft Entra ID tenant ID" |
| 12 | docs/playbooks/control-implementations/1.18/portal-walkthrough.md | 59 | "Azure AD roles > Roles" | "Microsoft Entra roles > Roles" |
| 13 | docs/playbooks/control-implementations/1.12/portal-walkthrough.md | 58 | "Azure AD deletion" | "Microsoft Entra ID deletion" |
| 14 | docs/playbooks/control-implementations/1.12/troubleshooting.md | 47 | "Azure AD integration" | "Microsoft Entra ID integration" |
| 15 | docs/playbooks/control-implementations/1.16/troubleshooting.md | 59 | "authenticate to Azure AD" | "authenticate to Microsoft Entra ID" |
| 16 | docs/playbooks/advanced-implementations/microsoft-audit-reporting-tools.md | 96 | "Azure AD app registration" | "Microsoft Entra app registration" |
| 17 | docs/playbooks/advanced-implementations/platform-change-governance/implementation-path-a.md | 26 | "Azure AD app registration" | "Microsoft Entra app registration" |

All 17 are straightforward renames. No historical/version context requires keeping old name.

---

## CSW-02: Tier/Level → Zone Terminology Sweep

### Terminology Definitions

Per docs/framework/zones-and-tiers.md:
- **Zone** = agent governance classification (risk level): Zone 1/2/3
- **Tier** = environment classification (Dev/Test/Prod) — valid distinct concept

### Category Analysis

**Category A — Correct "Tier" usage (NO CHANGE):** solutions-integration.md and solutions-index.md use "Tier 2 solutions" for solution maturity tier.

**Category B — "Tier" used where "Zone" is intended (NEEDS FIX):**

| # | File | Lines | Context |
|---|------|-------|---------|
| 1 | docs/playbooks/control-implementations/2.9/portal-walkthrough.md | 62-64, 92, 113-124 | "Tier 1/2/3" with "Internal/Team/Customer-Facing" = governance zones |
| 2 | docs/playbooks/control-implementations/2.8/portal-walkthrough.md | 92 | "Baseline (Tier 1)", "Recommended (Tier 2)", "Regulated (Tier 3)" |
| 3 | docs/playbooks/control-implementations/2.17/portal-walkthrough.md | 99 | Same pattern as 2.8 |
| 4 | docs/playbooks/control-implementations/2.9/verification-testing.md | 73-75 | "Tier 1/2/3" error rate targets |
| 5 | docs/playbooks/control-implementations/3.2/verification-testing.md | 186, 204 | "Tier 2+ agents", "Tier 1/2/3 Target" |
| 6 | docs/playbooks/control-implementations/4.1/portal-walkthrough.md | 104 | "Tier 2+ sites", "Tier 3 sites" |
| 7 | docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md | 97 | "Tier 2-3" |
| 8 | docs/reference/solutions-coverage-gaps.md | 95, 135, 137, 214 | "Tier 1 (Critical)" materiality — add clarifying note |
| 9 | docs/playbooks/control-implementations/2.15/portal-walkthrough.md | 78 | "Baseline (Tier 1/2/3)" pattern |
| 10 | docs/playbooks/control-implementations/2.18/portal-walkthrough.md | 112 | "Baseline (Tier 1/2/3)" pattern |
| 11 | docs/playbooks/control-implementations/2.19/portal-walkthrough.md | 116 | "Baseline (Tier 1/2/3)" pattern |
| 12 | docs/playbooks/control-implementations/3.2/portal-walkthrough.md | 55, 70, 82, 131, 156 | "Tier 1/2/3 Target" KPI tables |
| 13 | docs/playbooks/control-implementations/2.2/verification-testing.md | 11-217 (24+) | "Tier 1 (Personal Productivity)" explicit zone context |
| 14 | docs/playbooks/control-implementations/2.2/troubleshooting.md | 195, 206, 242 | "governance tier (Tier 1/2/3)" |
| 15 | docs/playbooks/control-implementations/2.1/verification-testing.md | 208 | "governance tier [Tier 1/2/3]" |
| 16 | docs/playbooks/control-implementations/1.2/verification-testing.md | 30 | "Tier 2-3 agents" |

**Category C — Correct "Level" usage (NO CHANGE):** governance-fundamentals.md defines Level 1-4 as maturity levels. faq.md and playbooks use Level for maturity scoring. Valid, distinct concept.

**Category D — Escalation levels (NO CHANGE):** remediation-tracking.md and troubleshooting docs use Level for support escalation. Not governance context.

### Decision Needed

- solutions-coverage-gaps.md uses "Tier 1 (Critical)" as a materiality classification. This is in Plan A's file list. Add a clarifying parenthetical: "Priority Tier 1 (Critical)" to distinguish from Zone.

---

## CSW-03: solutions-integration.md vs. solutions-index.md Sync

### Status Discrepancies (6 conflicts)

| Solution | solutions-index.md | solutions-integration.md | Fix |
|----------|-------------------|-------------------------|-----|
| Deny Event Correlation | Completed | Work In Progress | → Completed |
| Conditional Access Automation | Completed | Work In Progress | → Completed |
| Compliance Dashboard | Completed | Work In Progress (Beta) | → Completed |
| Scope Drift Monitor | Completed | Work In Progress | → Completed |
| Session Security Configurator | Completed | Missing | Add entry |
| File Upload Security | Work In Progress | Missing | Add entry |

### Version Discrepancies (3 conflicts)

| Solution | solutions-index.md | solutions-integration.md | Fix |
|----------|-------------------|-------------------------|-----|
| Deny Event Correlation | v2.0.0 | v1.1.0 | → v2.0.0 |
| Conditional Access Automation | v1.1.0 | v1.0.0 | → v1.1.0 |
| Scope Drift Monitor | v1.1.0 | v1.0.0 | → v1.1.0 |

### Summary Statistics

The solutions-integration.md summary section contradicts its own body. Must recalculate after syncing all statuses.

---

## CSW-04: Cross-Solution Integration Status

| Location | Current | Target |
|----------|---------|--------|
| solutions-index.md (line ~37) | Work In Progress | Completed |
| solutions-integration.md summary | Counted in WIP | Count in Completed |

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| solutions-integration.md has many stale entries | Medium — large edit surface | Systematic section-by-section update |
| Tier/Zone ambiguity in solutions-coverage-gaps.md | Low — owned by Plan A | Add clarifying parenthetical |
| 17 Azure AD renames across 12 files | Low — all straightforward | Verify no false positives |
| File overlap between plans | Medium | solutions-coverage-gaps.md Tier changes handled in Plan A only |

---

## File Allocation (No Overlap)

### Plan A (01-01): Navigation & Solution Doc Sync
- mkdocs.yml
- docs/getting-started/quick-start.md
- docs/reference/faq.md
- docs/reference/solutions-coverage-gaps.md (BLK-03 link + CSW-02 Tier clarification)
- docs/framework/solutions-integration.md
- docs/reference/solutions-index.md

### Plan B (01-02): Terminology Sweep
- docs/reference/portal-paths-quick-reference.md
- docs/playbooks/validation-testing/script-validation-guide.md
- docs/controls/pillar-1-security/1.22-information-barriers.md
- docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md
- docs/playbooks/control-implementations/2.15/troubleshooting.md
- docs/playbooks/control-implementations/2.15/portal-walkthrough.md
- docs/playbooks/control-implementations/2.14/powershell-setup.md
- docs/playbooks/control-implementations/1.8/powershell-setup.md
- docs/playbooks/control-implementations/1.18/portal-walkthrough.md
- docs/playbooks/control-implementations/1.12/portal-walkthrough.md
- docs/playbooks/control-implementations/1.12/troubleshooting.md
- docs/playbooks/control-implementations/1.16/troubleshooting.md
- docs/playbooks/advanced-implementations/microsoft-audit-reporting-tools.md
- docs/playbooks/advanced-implementations/platform-change-governance/implementation-path-a.md
- docs/playbooks/control-implementations/2.8/portal-walkthrough.md
- docs/playbooks/control-implementations/2.9/portal-walkthrough.md
- docs/playbooks/control-implementations/2.9/verification-testing.md
- docs/playbooks/control-implementations/2.9/powershell-setup.md
- docs/playbooks/control-implementations/2.17/portal-walkthrough.md
- docs/playbooks/control-implementations/2.18/portal-walkthrough.md
- docs/playbooks/control-implementations/2.19/portal-walkthrough.md
- docs/playbooks/control-implementations/3.2/verification-testing.md
- docs/playbooks/control-implementations/3.2/portal-walkthrough.md
- docs/playbooks/control-implementations/4.1/portal-walkthrough.md
- docs/playbooks/control-implementations/2.2/verification-testing.md
- docs/playbooks/control-implementations/2.2/troubleshooting.md
- docs/playbooks/control-implementations/2.1/verification-testing.md
- docs/playbooks/control-implementations/1.2/verification-testing.md
- docs/framework/governance-fundamentals.md

---

*Research completed: 2026-02-11*
