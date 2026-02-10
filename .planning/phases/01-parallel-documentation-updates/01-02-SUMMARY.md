---
phase: 1
plan: 2
title: "Agent 365 GA Readiness Review"
status: complete
started: 2026-02-10
completed: 2026-02-10
---

# Summary: Plan 01-02 — Agent 365 GA Readiness Review

## Status: COMPLETE

## Requirements Delivered

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FCR-04 | ✅ Complete | agent-identity-architecture.md already had meeting findings in Preview Features warning (lines 5-20) |
| FCR-05 | ✅ Complete | Controls 1.11, 2.12, 3.8 updated with Agent 365 GA/preview status and registry findings |
| FCR-06 | ✅ Complete | role-catalog.md — AI Admin limitations admonition added |
| FCR-07 | ✅ Complete | Controls 1.5, 1.6, 1.8 — security event visibility gap warnings added |
| FCR-08 | ✅ Complete | Preview admonitions updated across all modified controls |

## Changes Made

### Files Modified

| File | Change |
|------|--------|
| `docs/controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md` | Updated Agent 365 tip with GA status and agent registry visibility findings; version footer to v1.3/Feb 2026 |
| `docs/controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md` | Updated Frontier preview admonition with Feb 2026 GA/preview status and observability integration note; version footer to v1.3/Feb 2026 |
| `docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md` | Expanded preview status table with GA features (Entra Agent ID, Conditional Access, Admin Center Settings) and preview features (Unified Control Plane, Observability); added declarative agent deployment constraint |
| `docs/reference/role-catalog.md` | Added `!!! note "Agent 365 Role Limitations (February 2026)"` at AI Administrator entry — documents GA role access limitations |
| `docs/controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md` | Added `!!! warning "Security Event Visibility Gap"` about blocked prompt events in Defender advanced hunting |
| `docs/controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md` | Added `!!! note "Security Event Consistency"` about DSPM Activity Explorer completeness; version footer to v1.3/Feb 2026 |
| `docs/controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md` | Added `!!! note "DLP Deny Event Visibility"` about Defender advanced hunting gaps; version footer to v1.3/Feb 2026 |

### Files Not Modified (Confirmed Correct)

| File | Reason |
|------|--------|
| `docs/framework/agent-identity-architecture.md` | Already contained all 7 meeting findings in Preview Features warning section |
| `docs/framework/agent-365-architecture.md` | Redirect stub — correctly left in place |

## Decisions Made

- agent-identity-architecture.md Task 1 was already complete — all 7 meeting findings were present in the existing `!!! warning "Preview Features"` section
- Used `!!! warning` for 1.8 (most severe — blocked prompts not appearing) and `!!! note` for 1.5/1.6 (informational — downstream impact)
- 3.8 preview table expanded significantly to distinguish GA features from preview features

## Verification

- `mkdocs build --strict`: PASS
- `python scripts/verify_controls.py`: PASS (62/62 controls valid)
- FSI language compliance: Verified — uses "may not consistently", "under review", "organizations should"

---
*Completed: 2026-02-10*
