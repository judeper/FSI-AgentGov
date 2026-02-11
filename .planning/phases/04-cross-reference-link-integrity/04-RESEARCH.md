# Phase 4 Research: Cross-Reference & Link Integrity

**Date:** 2026-02-11
**Phase Goal:** Fix broken cross-references, missing solution mappings, and path errors across controls, playbooks, and reference docs
**Requirements:** XRL-01 through XRL-06

## Findings Summary

| Req | Files Affected | Severity | Complexity |
|-----|---------------|----------|------------|
| XRL-01 | 2 control files | Medium | Low — additive admonition blocks |
| XRL-02 | 1 reference file | Medium | Medium — count recalculation |
| XRL-03 | 1 reference file | Medium | Medium — same file as XRL-02 |
| XRL-04 | 1 playbook | Low | Low — path corrections |
| XRL-05 | 4 playbooks | Low | Low — text replacements |
| XRL-06 | 3+ playbook/reference files | Medium | Medium — naming convention decision |

## XRL-01: CAA Solution References in Controls 1.23 and 1.18

**Files:**
- `docs/controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md`
- `docs/controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`

**Problem:** Both controls are listed as CAA target controls in `solutions-index.md`, but neither has a direct CAA admonition block. They reference CAA only indirectly via the 1.11 relationship in Related Controls.

**Pattern (from Control 1.11):**
```markdown
!!! tip "Automated Compliance: Conditional Access Automation"
    For automated CA policy deployment, daily compliance scanning, and drift detection...
    **Deployable Solution:** [conditional-access-automation](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation)
```

**Fix:** Add CAA tip admonition block to Section 8 (Implementation Guides) of both control files.

## XRL-02: Control 1.8 Missing from DEC Coverage

**File:** `docs/reference/solutions-coverage-gaps.md`

**Problem:** `solutions-index.md` lists DEC as covering Controls 1.5, 1.7, 1.8, 3.4, but `solutions-coverage-gaps.md` only shows 1.5, 1.7, 3.4 — Control 1.8 is missing.

**Impact on counts:**
- Covered Controls: 17 → 18
- Controls Without Solutions: 45 → 44
- Overall coverage: 27.4% → 29.0%
- Pillar 1: 4 → 5 covered, 16.7% → 20.8%
- Remove 1.8 from "Zone 3 Controls Without Solutions" table

**Cross-dependency:** Must coordinate with XRL-03 edits to same file.

## XRL-03: AAM and FUS Missing from Coverage Gaps

**File:** `docs/reference/solutions-coverage-gaps.md`

**Abbreviation clarification:**
- **AAM** = Agent Access Governance Monitor (covers Control 3.8)
- **FUS** = File Upload Security Configurator (covers Controls 1.14, 1.8, 1.4)

**Additional missing Tier 2 solutions:**
- ACV (Audit Configuration Validator → 1.7)
- SSC (Session Security Configurator → 1.23, 1.11)
- CMM (Content Moderation Governance Monitor → 1.8)

**Approach:** Add all missing Tier 2 solutions to coverage-gaps.md in a single pass with XRL-02 to compute final counts once.

## XRL-04: Broken Paths in evidence-pack-assembly.md

**File:** `docs/playbooks/compliance-and-audit/evidence-pack-assembly.md`

**Broken paths (9 occurrences):**

| Broken Path | Correct Relative Path |
|------------|----------------------|
| `templates/agent-inventory-entry.md` | `../agent-lifecycle/agent-inventory-entry.md` |
| `templates/action-authorization-matrix.md` | `../governance-operations/action-authorization-matrix.md` |
| `templates/per-agent-data-policy.md` | `../agent-lifecycle/per-agent-data-policy.md` |
| `templates/escalation-matrix.md` | `../governance-operations/escalation-matrix.md` |
| `templates/decision-log-schema.md` | `../governance-operations/decision-log-schema.md` |
| `specs/real-time-compliance-dashboard.md` | `../monitoring-and-validation/real-time-compliance-dashboard.md` |
| `specs/scope-creep-detection.md` | `../monitoring-and-validation/scope-creep-detection.md` |
| `templates/supply-chain-risk-register-entry.md` | `../regulatory-modules/supply-chain-risk-register-entry.md` |
| `templates/colorado-ai-impact-assessment.md` | `../regulatory-modules/colorado-ai-impact-assessment.md` |

## XRL-05: Legacy "Gap N" Placeholder References

**8 occurrences across 4 files:**

| File | Reference | Replacement |
|------|-----------|-------------|
| `real-time-compliance-dashboard.md` | `(Gap 2)` | Link to `decision-log-schema.md` |
| `real-time-compliance-dashboard.md` | `(Gap 3)` | Link to `scope-creep-detection.md` |
| `real-time-compliance-dashboard.md` | `(Gap 4)` | Link to `confidence-and-routing.md` |
| `scope-creep-detection.md` | `(Gap 2)` | Link to `decision-log-schema.md` |
| `scope-creep-detection.md` | `(Gap 7 dashboard feeders)` | Link to `real-time-compliance-dashboard.md` |
| `escalation-matrix.md` | `Gap 2 decision log` | Link to `decision-log-schema.md` |
| `escalation-matrix.md` | `(Gap 7)` | Link to `real-time-compliance-dashboard.md` |
| `confidence-and-routing.md` | `(tie to Gap 2 decision logs)` | Link to `decision-log-schema.md` |

**Gap numbering decoded:** Gap 2 = Decision Log Schema, Gap 3 = Scope Creep Detection, Gap 4 = Confidence & Routing, Gap 7 = Real-time Compliance Dashboard.

## XRL-06: ELM Environment Group Names & solutions-index Versions

**Environment group naming discrepancy:**

| Zone | Control 2.2 Walkthrough | ELM Provisioning |
|------|------------------------|-----------------|
| Zone 1 | `FSI-Personal-Dev` | `FSI-Zone1-PersonalProductivity` |
| Zone 2 | `FSI-Team-Collaboration` | `FSI-Zone2-TeamCollaboration` |
| Zone 3 | `FSI-Enterprise-Production` | `FSI-Zone3-EnterpriseManagedEnvironment` |

**Recommendation:** Standardize on Control 2.2 naming convention (shorter, already in portal walkthrough). Update ELM provisioning playbook and labs to match.

**Files to update:**
- `docs/playbooks/advanced-implementations/environment-lifecycle-management/implementation-provisioning.md`
- `docs/playbooks/advanced-implementations/environment-lifecycle-management/labs.md`

**solutions-index.md versions:** No critical mismatches found in solution version listings. Minor footer version discrepancy (`v1.2.36` in coverage-gaps vs `v1.2.40` in solutions-index) should be normalized as part of cleanup.

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|-----------|
| XRL-02/03 count math errors | Medium — misleading coverage stats | Calculate all counts in single pass |
| ELM naming change breaks deployed tenants | Medium — existing deployments may use old names | Add migration note in provisioning guide |
| Missing Tier 2 solutions in coverage-gaps | Low — scope expansion beyond original requirement | Limit to AAM/FUS per requirement, note others as TODO |

## Recommended Approach

1. **Plan A (04-01):** Handle XRL-01, XRL-02, XRL-03. Edit solutions-coverage-gaps.md once with all count changes combined. Add CAA admonitions to 1.23 and 1.18 separately.
2. **Plan B (04-02):** Handle XRL-04, XRL-05, XRL-06. These are fully independent file sets with no overlap with Plan A.
3. Both plans run `mkdocs build --strict` as validation.

---
*Research completed: 2026-02-11*
