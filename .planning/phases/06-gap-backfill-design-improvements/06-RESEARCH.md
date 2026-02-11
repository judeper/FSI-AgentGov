# Phase 6 Research: Gap Backfill & Design Improvements

**Date:** 2026-02-11
**Phase:** 6 of 6 — v11 Technical Remediation
**Goal:** Create missing deployment guides, operational playbooks, and design improvements identified during audit

## Requirements Overview

| Req | Description | Plan | Complexity |
|-----|-------------|------|-----------|
| GBD-01 | Create CAA end-to-end deployment guide | 06-01 | Complex |
| GBD-02 | Document ELM approval flow implementation | 06-01 | Medium |
| GBD-03 | Backfill P4 portal walkthrough caveats | 06-01 | Simple |
| GBD-04 | Add DSPM portal deployment steps | 06-01 | Medium |
| GBD-05 | Interlink spec-level playbooks | 06-02 | Simple |
| GBD-06 | FAQ timeline reconciliation note | 06-02 | Simple |
| GBD-07 | Fix footnote markers in governance-ops | 06-02 | Medium |
| GBD-08 | Remove quick-start emojis (optional) | 06-02 | Simple |

## Analysis by Requirement

### GBD-01: CAA End-to-End Deployment Guide

**Current state:** CAA has scripts (`Start-CAAValidationRunbook.ps1`, `Test-PolicyCompliance.ps1`, `caa_client.py`, `CAAClient.psm1`, private helpers) and a module manifest but no unified deployment guide. No `conditional-access-automation/` directory exists under `docs/playbooks/advanced-implementations/`.

**Existing pattern:** DEC report has a 6-file advanced implementation structure (index, purview-audit-extraction, dlp-event-extraction, app-insights-rai-telemetry, power-bi-correlation, deployment-guide). CAA is simpler — it's primarily PowerShell + Azure Automation + Dataverse.

**Approach:** Create a minimal 2-file structure (index + deployment-guide) rather than the full DEC pattern. The CAA solution is a validation/compliance tool, not a multi-source extraction pipeline.

**Files to create:**
- `docs/playbooks/advanced-implementations/conditional-access-automation/index.md`
- `docs/playbooks/advanced-implementations/conditional-access-automation/deployment-guide.md`

**Files to modify:** `mkdocs.yml` (add nav entries)

### GBD-02: ELM Approval Flow Implementation

**Current state:** ELM has 6 playbooks. The architecture doc defines the state machine (Draft → Submitted → PendingApproval → Approved/Rejected → Provisioning). The intake doc references steps 5-8 for approval (high-level). The provisioning doc triggers on `er_state eq 'Approved'`. **No dedicated approval flow implementation document exists.**

**Approach:** Create `implementation-approval.md` following the same structural pattern as `implementation-provisioning.md` and `implementation-copilot-intake.md`. Documents the Power Automate Approval flow connecting intake to provisioning, including multi-level approval routing (Zone 3 = manager + compliance).

**Files to create:** `docs/playbooks/advanced-implementations/environment-lifecycle-management/implementation-approval.md`

**Files to modify:** `mkdocs.yml`, ELM `index.md` (update Playbook Structure table)

### GBD-03: P4 Portal Walkthrough Caveats

**Current state:** Parent controls document reindexing latency (4.1), EEEU risk (4.7), and discovery amplification (4.7). But the corresponding portal walkthroughs do not include warning admonitions about these operational caveats.

**Approach:** Add MkDocs `!!! warning` admonition blocks to portal walkthroughs for 4.1, 4.2, 4.6, and 4.7:
- **4.1:** Reindexing latency caveat after RCD enable step
- **4.2:** EEEU report priority note
- **4.6:** Reindexing caveat for grounding scope changes
- **4.7:** EEEU risk and discovery amplification warnings

**Files to modify:** 4 portal walkthrough files in `docs/playbooks/control-implementations/`

### GBD-04: DSPM Portal Deployment Steps

**Current state:** `dspm-for-ai-policy-pack.md` (123 lines) has prerequisites, rollout strategy, policy list, and scoping rules — but no portal step-by-step deployment instructions. It's a policy template, not a walkthrough.

**Approach:** Insert a "Portal Deployment Steps" section with specific navigation paths (`purview.microsoft.com > Solutions > DSPM for AI > Overview > Policies`) and step-by-step for enabling each default policy. Reference Control 1.6 portal walkthrough for DSPM basics.

**Files to modify:** `docs/playbooks/advanced-implementations/dspm-for-ai-policy-pack.md`

### GBD-05: Interlink Spec-Level Playbooks

**Current state:** Three spec documents exist (confidence-and-routing.md, human-in-the-loop-triggers.md, zone1-min-explainability.md) but none have cross-reference sections linking to the other two. Inline mentions don't use actual markdown links.

**Approach:** Add a "Related Specifications" section at the end of each document with links to the other two. Fix inline text references to be proper markdown links.

**Files to modify:** 3 spec playbook files

### GBD-06: FAQ Timeline Reconciliation Note

**Current state:** FAQ/checklist use an "8-week phased approach" while adoption-roadmap uses "Phase 0 (0-60 days) / Phase 1 (2-6 months) / Phase 2 (6-12 months)". No reconciliation note explains the mapping.

**Approach:** Add an `!!! info` admonition after the FAQ's 8-week phase listing explaining that the FAQ phases correspond to Phase 0 in the adoption roadmap.

**Files to modify:** `docs/reference/faq.md`

### GBD-07: Fix Footnote Markers in Governance-Ops

**Current state:** `<sup>[N]</sup>` markers appear in escalation-matrix.md, decision-log-schema.md, and action-authorization-matrix.md with no corresponding footnotes section. Also found in dspm-for-ai-policy-pack.md, zone1-min-explainability.md, and confidence-and-routing.md (with `[web:NN]` variants).

**Approach:** Convert orphaned markers to inline descriptive text or remove them. This is the safest approach since the original source numbering context is not available in the repository.

**Files to modify:** 6 files across governance-operations/ and advanced-implementations/

**Overlap with GBD-05:** Both touch confidence-and-routing.md and zone1-min-explainability.md. Since both are in Plan 06-02, tasks will be ordered to handle GBD-07 first (clean up markers), then GBD-05 (add cross-references).

### GBD-08: Remove Quick-Start Emojis

**Current state:** `docs/getting-started/quick-start.md` uses emoji prefixes in 6 section headers (🚀, 📋, 📚, 🔑, ✅, 💬).

**Approach:** Remove emoji prefixes from section headers. Simple find/replace.

**Files to modify:** `docs/getting-started/quick-start.md`

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|-----------|
| GBD-01 scope creep — CAA deployment guide could expand to 5+ docs | Medium | Limit to 2 files (index + deployment guide). Defer lab exercises. |
| GBD-07 citation resolution — original source context unknown | Low | Convert to inline text rather than fabricating footnotes. |
| GBD-05 + GBD-07 file overlap in Plan B | Low | Order tasks: markers first, cross-refs second. |
| GBD-04 DSPM portal paths may change | Low | Add "UI Verification" note per standard framework pattern. |

## File Overlap Analysis

**Plan A (06-01) files:**
- NEW: `docs/playbooks/advanced-implementations/conditional-access-automation/index.md`
- NEW: `docs/playbooks/advanced-implementations/conditional-access-automation/deployment-guide.md`
- NEW: `docs/playbooks/advanced-implementations/environment-lifecycle-management/implementation-approval.md`
- MODIFY: `docs/playbooks/advanced-implementations/environment-lifecycle-management/index.md`
- MODIFY: `docs/playbooks/control-implementations/4.1/portal-walkthrough.md`
- MODIFY: `docs/playbooks/control-implementations/4.2/portal-walkthrough.md`
- MODIFY: `docs/playbooks/control-implementations/4.6/portal-walkthrough.md`
- MODIFY: `docs/playbooks/control-implementations/4.7/portal-walkthrough.md`
- MODIFY: `docs/playbooks/advanced-implementations/dspm-for-ai-policy-pack.md` (new section only)
- MODIFY: `mkdocs.yml` (add CAA + ELM approval nav entries)

**Plan B (06-02) files:**
- MODIFY: `docs/playbooks/advanced-implementations/confidence-and-routing.md`
- MODIFY: `docs/playbooks/advanced-implementations/human-in-the-loop-triggers.md`
- MODIFY: `docs/playbooks/advanced-implementations/zone1-min-explainability.md`
- MODIFY: `docs/reference/faq.md`
- MODIFY: `docs/playbooks/governance-operations/escalation-matrix.md`
- MODIFY: `docs/playbooks/governance-operations/decision-log-schema.md`
- MODIFY: `docs/playbooks/governance-operations/action-authorization-matrix.md`
- MODIFY: `docs/playbooks/advanced-implementations/dspm-for-ai-policy-pack.md` (footnote cleanup only)
- MODIFY: `docs/getting-started/quick-start.md`

**Overlap:** `dspm-for-ai-policy-pack.md` appears in both plans. Plan A adds a new section (portal steps), Plan B fixes footnote markers in existing content. Since these target different parts of the file and both plans are Wave 1, the overlap is manageable if edits are to non-adjacent sections. However, to be safe, GBD-07's dspm-for-ai-policy-pack.md cleanup should be Wave 2 or handled within Plan A.

**Resolution:** Move the dspm-for-ai-policy-pack.md footnote cleanup from GBD-07 to GBD-04 (Plan A, Task 2 addendum), since Plan A already modifies that file. This eliminates the file overlap between plans.

## Recommended Approach

- **Wave 1:** Both plans execute in parallel (no cross-dependencies)
- **Plan A (06-01):** GBD-01 through GBD-04 — gap backfill, new files + portal modifications
- **Plan B (06-02):** GBD-05 through GBD-08 — design improvements, cross-linking + cleanup
- **Validation:** `mkdocs build --strict` after both plans

---
*Research completed: 2026-02-11*
