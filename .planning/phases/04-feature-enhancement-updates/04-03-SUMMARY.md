---
phase: 04-feature-enhancement-updates
plan: 03
subsystem: reporting-governance
tags: [copilot-hub, ai-administrator, feature-access-control, role-catalog, permission-matrix]
requires:
  - phase-03-agent-365-strategic-architecture
  - control-3.8-existing-implementation
provides:
  - ai-feature-access-control-capabilities
  - ai-administrator-role-catalog-entry
  - permission-matrix-comparison
  - fsi-least-privilege-guidance
affects:
  - future-copilot-governance-enhancements
  - ai-administrator-role-assignments
tech-stack:
  added: []
  patterns:
    - ai-feature-access-control-table-format
    - permission-matrix-with-checkmarks
key-files:
  created: []
  modified:
    - docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md
    - docs/reference/role-catalog.md
    - docs/playbooks/control-implementations/3.8/portal-walkthrough.md
    - docs/playbooks/control-implementations/3.8/verification-testing.md
key-decisions:
  - id: ai-feature-access-control-scope
    choice: Enhance existing Control 3.8 (not standalone control)
    rationale: AI Feature Access Control is governance capability area within Copilot Hub, not discrete product
  - id: ai-administrator-role-type
    choice: Standalone entry in Entra (Identity) section
    rationale: AI Administrator is established Entra built-in role (Microsoft 365 AI Administrator)
  - id: defender-xdr-admin-handling
    choice: Informal alias for Entra Security Admin
    rationale: No built-in "Defender XDR Administrator" role exists — Security Administrator has Defender XDR access
  - id: permission-matrix-format
    choice: Checkmarks (✓/✗) across 3 roles with 11 permissions
    rationale: Clear visual comparison for FSI least-privilege role selection
duration: 7m17s
completed: 2026-02-03
---

# Phase 04 Plan 03: AI Feature Access Control & Role Catalog Enhancement Summary

**One-liner:** Enhanced Control 3.8 with AI Feature Access Control capabilities (6 governance features) and added AI Administrator role with permission matrix comparison for FSI least-privilege guidance.

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| **Execution Duration** | 7 minutes 17 seconds |
| **Start Time** | 2026-02-03T21:41:03Z |
| **End Time** | 2026-02-03T21:48:05Z |
| **Tasks Completed** | 3/3 (100%) |
| **Files Modified** | 4 |
| **Commits** | 3 |
| **Build Status** | ✓ PASSING (mkdocs build --strict) |

---

## Accomplishments

### Control 3.8 Enhancement

Enhanced Control 3.8 (Copilot Hub and Governance Dashboard) with AI Feature Access Control section documenting 6 governance capabilities:

| Feature | Status | Configuration |
|---------|--------|---------------|
| License-Based Restrictions | GA | M365 Admin > Licenses |
| Admin Exclusion Groups | GA | Copilot > Settings > User access |
| Copilot Chat Pinning | GA | Copilot > Settings > End-User Experience |
| Deployment Groups | GA | Copilot > Settings > Deployment |
| Web Search Control | GA | Copilot > Settings > Data access |
| Agent Access Control | GA | Copilot > Settings > Actions |

**FSI Governance Guidance Added:**
- Admin Exclusion Groups for compliance-sensitive roles (traders during quiet periods, employees under investigation)
- Deployment Groups for phased rollout (Zone 1 → Zone 2/3)
- Web Search Control for MNPI environments

**Control Updates:**
- Added AI Feature Access Control section after January 2026 Enhancements
- Updated Key Configuration Points with feature access steps
- Added AI Administrator to Roles & Responsibilities table
- Enhanced Verification Criteria with Admin Exclusion Groups and deployment groups

### Role Catalog Enhancement

Added **AI Administrator** as standalone entry in Entra (Identity) section:

| Role | Responsibilities | Aliases |
|------|------------------|---------|
| AI Administrator | Manage M365 Copilot settings, AI services, and connector delegation | Microsoft 365 AI Administrator |

Updated **Entra Security Admin** to include Defender XDR Admin as informal alias:

| Role | Responsibilities | Aliases |
|------|------------------|---------|
| Entra Security Admin | Security configuration, policy, and Defender XDR access | Security Administrator, Defender XDR Admin (informal) |

**AI Governance Permission Matrix:**

Created comparison table with 11 permissions across 3 roles:

| Permission | AI Admin | Global Admin | Security Admin |
|------------|----------|--------------|----------------|
| Manage Copilot settings | ✓ | ✓ | ✗ |
| Manage Copilot connectors | ✓ | ✓ | ✗ |
| Register Entra apps (delegated) | ✓* | ✓ | ✗ |
| Consent to ExternalItem/ExternalConnection APIs | ✓ | ✓ | ✗ |
| Consent to all Graph APIs | ✗ | ✓ | ✗ |
| View Copilot usage reports | ✓ | ✓ | ✗ |
| Create support tickets | ✓ | ✓ | ✓ |
| Configure Defender XDR | ✗ | ✓ | ✓ |
| Manage Defender policies | ✗ | ✓ | ✓ |
| View Defender alerts | ✗ | ✓ | ✓ |
| Configure DLP policies | ✗ | ✓ | ✗ |

*Footnote: Requires delegation via Entra admin consent or custom role for app registration and limited API consent scope.

**FSI Least-Privilege Role Assignment Guidance:**

Added admonition with 5 guidance points:
- Prefer AI Administrator over Global Admin for agent governance
- AI Administrator sufficient for most connector delegation
- Use Entra Security Admin (not Global Admin) for Defender XDR operations
- Global Admin required only for initial setup and broad Graph API consent
- FINRA-regulated firms must document role assignments per Rule 3110

### Playbook Updates

**Portal Walkthrough (portal-walkthrough.md):**

Added Step 3A for AI Feature Access Control configuration:
- 7-step configuration process (licenses, exclusion groups, deployment groups)
- FSI governance best practice admonition
- 8-hour propagation timing guidance
- Updated validation checklist with 7 items (added feature access verification)

**Verification Testing (verification-testing.md):**

Added 5 new test cases for feature access control:
1. Admin Exclusion Group access control
2. Deployment group restrictions
3. Web search control disabled
4. Agent access restrictions
5. AI Administrator role permissions

Renumbered existing test cases (6-8) and enhanced evidence collection with feature access documentation.

---

## Task Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Enhance Control 3.8 with AI Feature Access Control | `156b3d0` | 3.8-copilot-hub-and-governance-dashboard.md |
| 2 | Update role catalog with AI Administrator and permission matrix | `7df9824` | role-catalog.md |
| 3 | Update playbooks with feature access control configuration | `9832a15` | portal-walkthrough.md, verification-testing.md |

---

## Files Created/Modified

### Modified

**Control Files (1):**
- `docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
  - Added AI Feature Access Control section (6 features)
  - Updated Key Configuration Points (3 new items)
  - Added AI Administrator to Roles & Responsibilities
  - Enhanced Verification Criteria (8 items, added Admin Exclusion Groups and deployment groups)

**Reference Files (1):**
- `docs/reference/role-catalog.md`
  - Added AI Administrator as standalone entry
  - Updated Entra Security Admin with Defender XDR Admin alias
  - Added AI Governance Permission Matrix (11 permissions × 3 roles)
  - Added FSI Least-Privilege Role Assignment guidance admonition

**Playbook Files (2):**
- `docs/playbooks/control-implementations/3.8/portal-walkthrough.md`
  - Added Step 3A for AI Feature Access Control configuration
  - Added FSI governance best practice admonition
  - Updated validation checklist (7 items)
- `docs/playbooks/control-implementations/3.8/verification-testing.md`
  - Added 5 feature access control test cases
  - Renumbered existing test cases (6-8)
  - Enhanced evidence collection section

---

## Decisions Made

### 1. AI Feature Access Control Scope

**Decision:** Enhance existing Control 3.8 (not create standalone control)

**Rationale:** AI Feature Access Control is a governance capability area within the Copilot Hub (M365 Admin Center), not a discrete product. It encompasses license-based restrictions, Admin Exclusion Groups, deployment groups, web search control, and agent access control. This aligns with CONTEXT.md guidance to integrate features into existing controls rather than creating standalone sections.

**Impact:** Control 3.8 now comprehensively covers Copilot Hub governance capabilities including user-level feature restrictions.

### 2. AI Administrator Role Type

**Decision:** Add AI Administrator as standalone entry in Entra (Identity) section

**Rationale:** AI Administrator is an established Entra built-in role (full name: "Microsoft 365 AI Administrator") with specific permissions for Copilot settings, AI services, and connector delegation. It deserves standalone entry rather than being buried in aliases.

**Impact:** FSI organizations can now assign AI Administrator role for least-privilege Copilot governance instead of elevating users to Global Admin.

### 3. Defender XDR Admin Handling

**Decision:** Document Defender XDR Admin as informal alias for Entra Security Admin

**Rationale:** No built-in "Defender XDR Administrator" role exists in Entra. The Security Administrator role provides Defender XDR access, and "Defender XDR Admin" is an informal term used in some Microsoft documentation. Clarifying this prevents confusion.

**Impact:** Role catalog accurately reflects Entra built-in roles while acknowledging informal terminology.

### 4. Permission Matrix Format

**Decision:** Use checkmarks (✓/✗) across 3 roles with 11 permissions

**Rationale:** Clear visual comparison enables FSI administrators to make least-privilege role selection decisions. Comparing AI Administrator vs. Global Admin vs. Security Admin shows when elevation is necessary.

**Impact:** FSI organizations can justify AI Administrator assignments for Copilot governance while reserving Global Admin for scenarios requiring broader permissions.

---

## Deviations from Plan

None. Plan executed exactly as written.

---

## Issues Encountered

None. All tasks completed successfully with zero errors.

---

## Next Phase Readiness

### Immediate Follow-On Opportunities

1. **Control 1.8 (Runtime Protection and External Threat Detection):**
   - Reference AI Administrator and Defender XDR Admin roles from role catalog
   - Link permission matrix for Defender XDR access comparison

2. **Other Copilot-Related Controls:**
   - Reference AI Administrator role for least-privilege assignments
   - Link to AI Feature Access Control capabilities in Control 3.8

3. **FSI-AgentGov-Solutions Repository:**
   - Consider deployable solution for automated Admin Exclusion Group management
   - Consider solution for deployment group orchestration

### Validation Requirements

- [ ] Verify AI Administrator role assignment procedures in FSI environments
- [ ] Test Admin Exclusion Group propagation timing (8-hour window)
- [ ] Validate deployment group staged rollout across zones
- [ ] Confirm permission matrix accuracy with Entra role definitions

### Known Limitations

None identified. AI Feature Access Control capabilities are GA, and AI Administrator is an established Entra built-in role.

---

## Regulatory Alignment

**FINRA Rule 3110:**
- FSI Least-Privilege guidance includes FINRA requirement to document role assignments in supervisory procedures

**SOX 404:**
- Control 3.8 enhancement supports IT controls for AI systems with documented governance

**GLBA 501(b):**
- Admin Exclusion Groups enable access control for customer data compliance

**SEC 17a-3/4:**
- Feature access control documentation supports books and records requirements

---

*Plan completed: 2026-02-03T21:48:05Z*
*Duration: 7 minutes 17 seconds*
*Status: ✓ ALL TASKS COMPLETE*
