---
phase: 4
plan: 1
title: "Solution Cross-Reference Fixes"
status: complete
---

# Plan 04-01 Summary: Solution Cross-Reference Fixes

## Status: ✅ Complete

## Commits

| Hash | Description |
|------|-------------|
| `05ecce5` | feat(04-01): add CAA admonitions to Controls 1.23, 1.18 and update solutions coverage gaps |

## File Manifest

| Action | File | Change |
|--------|------|--------|
| MODIFIED | `docs/controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md` | Added CAA tip admonition before Section 8 with step-up-auth-specific capabilities |
| MODIFIED | `docs/controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md` | Added CAA tip admonition before Section 8 with RBAC-specific capabilities |
| MODIFIED | `docs/reference/solutions-coverage-gaps.md` | Added DEC coverage of 1.8, AAM (3.8), FUS (1.4, 1.8, 1.14); updated all counts/percentages |

## Tasks Completed

### Task 1: CAA Admonition in Control 1.23
- Added `!!! tip "Automated Compliance: Conditional Access Automation"` block before Implementation Playbooks section
- Capabilities tailored to step-up auth: authentication context CA policies (c1–c5), zone-specific MFA enforcement, drift detection for step-up scenarios
- Links to `conditional-access-automation` in FSI-AgentGov-Solutions repo

### Task 2: CAA Admonition in Control 1.18
- Added `!!! tip "Automated Compliance: Conditional Access Automation"` block before Implementation Playbooks section
- Capabilities tailored to RBAC: CA policies for role-based access, app consent and authorization controls, drift affecting RBAC enforcement
- Links to `conditional-access-automation` in FSI-AgentGov-Solutions repo

### Task 3: Solutions Coverage Gaps Updates
- **DEC + Control 1.8:** Added 1.8 (Runtime Protection) to Deny Event Correlation Report coverage
- **AAM solution:** Added Agent Access Governance Monitor covering Control 3.8 (Copilot Hub)
- **FUS solution:** Added File Upload Security Configurator covering Controls 1.4, 1.8, 1.14
- **Coverage metrics updated:** 17 → 20 controls covered, 27.4% → 32.3% overall
- **Pillar 1:** 4 → 6 covered (16.7% → 25.0%)
- **Pillar 3:** 3 → 4 covered (30.0% → 40.0%)
- **Zone 3 table:** Struck through 1.4 and 1.8 as ADDRESSED
- **Category 1 table:** Struck through 1.4, 1.8, 3.8 as now having solutions
- **Duplicate Coverage section:** Updated to include 1.8 in DEC multi-control note; added FUS multi-control note
- **Version stamp:** Updated to v1.2.38

### Task 4: Validation
- `mkdocs build --strict` — passed (0 errors)
- `verify_controls.py` — all 62 controls validated, structure and anchor checks passed

## Decisions Made

1. **AAM/FUS confirmed in solutions-index.md** — Both solutions exist as "Work In Progress" entries with defined control mappings, confirming they are real solutions to include
2. **Admonition placement** — Placed before Section 8 (Implementation Playbooks), consistent with 1.11 pattern but after the Related Controls section (matching existing 1.23 structure that already has an SSC admonition)
3. **FUS already covers 1.14** — Since 1.14 was already covered by Scope Drift Monitor, FUS adds redundant coverage (noted in Duplicate Coverage section) but doesn't change the covered count for 1.14

## Discovered Work

- None. All requirements (XRL-01, XRL-02, XRL-03) fully addressed.
