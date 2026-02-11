# Phase 3 Research: Playbook Remediation

**Phase:** 3 of 4
**Goal:** Update 14 playbooks (7 portal-walkthrough + 7 verification-testing) to reflect SSPM-aligned controls and add hardening baseline cross-links to control Section 8s
**Researcher:** copilot
**Date:** 2026-02-11

---

## Executive Summary

Phase 3 has **three deliverables** across 21 files (14 playbooks + 7 controls). Research reveals that portal-walkthrough SSPM steps were already added during Phase 1, reducing the portal-walkthrough scope to footer consistency fixes. The verification-testing playbooks are the **primary remediation target** — all 7 need new SSPM-informed test cases. Section 8 cross-links to the Configuration Hardening Baseline are entirely absent.

---

## Current State Analysis

### Portal-Walkthrough Playbooks (7 files)

| Control | File | Lines | SSPM Steps? | Footer Status | Remediation Needed |
|---------|------|-------|-------------|---------------|-------------------|
| 1.1 | portal-walkthrough.md | 213 | YES (Steps 6-9) | No version footer | Add v1.3 footer |
| 1.7 | portal-walkthrough.md | 224 | YES (Dataverse audit) | v1.3, Feb 2026 | None (complete) |
| 1.8 | portal-walkthrough.md | 418 | YES (Items 15-16) | v1.2, Feb 2026 | Bump to v1.3 |
| 1.18 | portal-walkthrough.md | 144 | YES (Steps 7-9) | Jan 2026, no version | Update to Feb 2026 v1.3 |
| 2.1 | portal-walkthrough.md | 295 | YES (Steps 7-10) | Jan 2026, no version | Update to Feb 2026 v1.3 |
| 3.7 | portal-walkthrough.md | 161 | YES (Step 9) | v1.3, Feb 2026 | None (complete) |
| 3.8 | portal-walkthrough.md | 438 | YES (Part 4, Steps 11-15) | v1.3, Feb 2026 | None (complete) |

**Finding:** SSPM portal steps are present in all 7 — added during Phase 1. Only 4 files need footer updates.

### Verification-Testing Playbooks (7 files) — PRIMARY GAP

| Control | File | Lines | SSPM Tests? | Missing Test Cases |
|---------|------|-------|-------------|-------------------|
| 1.1 | verification-testing.md | 158 | NO | Auth mode != "No Auth", manual auth requires sign-in, auth enforcement = "Always", sharing != "Anyone", AI publishing disabled, unapproved agents blocked |
| 1.7 | verification-testing.md | 66 | NO | Dataverse env-level auditing enabled, retention ≥ 180 days, tenant-level Dataverse auditing |
| 1.8 | verification-testing.md | 263 | PARTIAL | Content moderation = High for Zone 2/3, no agents below Medium without risk acceptance |
| 1.18 | verification-testing.md | 95 | NO | Action consent enabled, connected agents disabled, admin count < 10, RPA/service accounts not admin |
| 2.1 | verification-testing.md | 222 | NO | Env creation restricted, env routing configured, tenant isolation enabled, security groups assigned |
| 3.7 | verification-testing.md | 104 | NO | Hardening baseline review completed, no config drift detected, evidence archived |
| 3.8 | verification-testing.md | 362 | PARTIAL | AI Prompts off, Generative Actions off, File Analysis off, Model Knowledge off, Semantic Search off, Move Data off, Bing off, transcript access restricted, DLP for publishing |

**Finding:** 0 of 7 verification-testing playbooks have complete SSPM test coverage. This is the core Phase 3 deliverable.

### Control Section 8 — Hardening Baseline Cross-Links

All 7 controls use the identical Section 8 format with 4 playbook links (Portal Walkthrough, PowerShell Setup, Verification & Testing, Troubleshooting). **None** include a link to the Configuration Hardening Baseline advanced implementation.

Control 3.7 references the hardening baseline in Section 3 (Control Description) via a tip admonition, but NOT in Section 8.

**Target pattern for Section 8 addition:**
```markdown
!!! tip "Advanced Implementation: Configuration Hardening Baseline"
    
    This control is covered by the [Configuration Hardening Baseline](../../playbooks/advanced-implementations/configuration-hardening-baseline/index.md), which consolidates SSPM-detectable settings across all 7 mapped controls into a single reviewable checklist with automation classification and evidence export procedures.
```

### Configuration Hardening Baseline (Cross-Link Target)

- **Path:** `docs/playbooks/advanced-implementations/configuration-hardening-baseline/index.md`
- **Version:** v1.1, February 2026
- **Content:** 27-item master checklist, automation classification, zone-specific cadence, evidence export procedures
- **Status:** Complete (delivered in Phase 2)

---

## File Overlap Analysis

| Plan | Files Modified | Overlap? |
|------|---------------|----------|
| Plan A (PLB-01 + PLB-03) | 4 portal-walkthrough.md files (footer fixes) + 7 control files (Section 8 cross-links) | None with Plan B |
| Plan B (PLB-02) | 7 verification-testing.md files | None with Plan A |

**Conclusion:** Plans A and B can run in parallel (Wave 1). No file overlap.

---

## SSPM Alert-to-Test Case Mapping

The following maps each SSPM configuration point to the verification test case needed:

### Control 1.1 — Agent Authentication & Publishing

| SSPM Ref | Configuration Point | Test Case |
|----------|-------------------|-----------|
| 2 | Authentication mode | Verify agent authentication is NOT set to "No Authentication" |
| 3 | Manual authentication sign-in | Verify manual auth requires "Require users to sign in" |
| 4 | Authentication enforcement | Verify enforcement = "Always" (not "Only for published agents") |
| 5 | Sharing scope | Verify sharing is NOT set to "Anyone with the link" |
| 6 | Publish bots with AI features | Verify "Publish bots with AI features" is disabled |
| 9 | Unapproved agent blocking | Verify unapproved agents are blocked from Teams channels |

### Control 1.7 — Audit Logging

| SSPM Ref | Configuration Point | Test Case |
|----------|-------------------|-----------|
| 11 | Dataverse environment auditing | Verify env-level auditing is enabled in Dataverse |
| 14 | Audit log retention | Verify retention ≥ 180 days (Zone 1), ≥ 365 days (Zone 2), ≥ 730 days (Zone 3) |
| 18 | Tenant-level Dataverse auditing | Verify tenant-level auditing enabled with User Sign-In and Activity |

### Control 1.8 — Content Moderation

| SSPM Ref | Configuration Point | Test Case |
|----------|-------------------|-----------|
| 20 | Content moderation level | Verify moderation = High for Zone 2/3 agents |
| 21 | Minimum moderation threshold | Verify no agents below Medium without documented risk acceptance |

### Control 1.18 — RBAC

| SSPM Ref | Configuration Point | Test Case |
|----------|-------------------|-----------|
| 23 | Agent action consent | Verify action consent enabled for all published agents |
| 24 | Connected agents | Verify connected agents disabled (or restricted to approved list) |
| 25 | Admin count | Verify < 10 environment-level admins per environment |
| 38 | RPA admin roles | Verify RPA/service accounts not assigned admin roles |

### Control 2.1 — Environment Strategy

| SSPM Ref | Configuration Point | Test Case |
|----------|-------------------|-----------|
| 26 | Environment creation | Verify set to "Only specific admins" |
| 27 | Environment routing | Verify environment routing rules configured |
| 28 | Tenant isolation | Verify tenant isolation enabled |
| 29 | Security groups | Verify security groups assigned to Zone 2/3 environments |

### Control 3.7 — PPAC Security Posture

| SSPM Ref | Configuration Point | Test Case |
|----------|-------------------|-----------|
| 30 | Baseline review | Verify hardening baseline review completed per documented cadence |
| 31 | Configuration drift | Verify no unresolved configuration drift items |
| 32 | Evidence archival | Verify evidence archived with SHA-256 hash per review cycle |

### Control 3.8 — Agent Analytics & AI Feature Access

| SSPM Ref | Configuration Point | Test Case |
|----------|-------------------|-----------|
| 33 | AI Prompts | Verify AI Prompts toggle disabled at tenant level |
| 34 | Generative Actions | Verify Generative Actions toggle disabled |
| 35 | File Analysis | Verify File Analysis Models disabled |
| 36 | Model Knowledge | Verify Model Knowledge disabled |
| 37 | Semantic Search | Verify Semantic Search with AI disabled |
| 40 | Move Data Across Regions | Verify Move Data Across Regions disabled |
| 42 | Bing Search | Verify Bing Search disabled |
| — | Transcript access | Verify transcript access restricted to compliance roles |
| — | DLP for publishing | Verify DLP policy enforcement active for publishing |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Footer updates introduce formatting inconsistency | Low | Low | Use consistent footer pattern from 1.7/3.7/3.8 as reference |
| Test case descriptions don't match portal-walkthrough steps | Medium | Medium | Cross-reference each test against corresponding portal-walkthrough step |
| Section 8 admonition link path incorrect | Low | High | Use relative paths validated by mkdocs build --strict |
| Verification-testing playbooks have varying structures | Medium | Medium | Preserve existing structure; append new test cases section after existing content |

---

## Recommended Approach

1. **Plan A (Wave 1):** Footer fixes for 4 portal-walkthroughs + Section 8 cross-links for 7 controls — 11 files, low complexity
2. **Plan B (Wave 1):** SSPM test cases for 7 verification-testing playbooks — 7 files, medium complexity (content authoring)
3. **Both plans Wave 1** — no file overlap, can execute in parallel
4. **Validation:** `mkdocs build --strict` after both plans complete

---

*Research completed: 2026-02-11*
*Source: Phase 1/2 outputs, SSPM alert mapping, live playbook/control analysis*
