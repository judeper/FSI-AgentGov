---
phase: 07-control-enhancements-role-updates
plan: 03
subsystem: reporting-governance
tags: [copilot-hub, ai-feature-access-control, admin-exclusion-groups, deployment-groups, web-search-control, zone-based-enablement]
requires:
  - phase: 06
    plan: all
    reason: "Agent 365 and Control 3.8 baseline established"
provides:
  - capability: "AI Feature Access Control governance documentation"
    scope: "User-level restrictions, zone-based enablement, admin exclusion groups, deployment groups"
  - capability: "Comprehensive Control 3.8 playbooks for AI feature access"
    scope: "Portal configuration, PowerShell automation, verification testing, troubleshooting"
affects:
  - phase: future
    area: "Copilot rollout implementations"
    nature: "Organizations can implement zone-aligned phased rollouts using documented deployment group patterns"
tech-stack:
  added: []
  patterns:
    - "Admin Exclusion Group pattern (CopilotForM365AdminExclude)"
    - "Phased deployment group rollout (Pilot → Wave 1 → Wave 2 → Wave 3)"
    - "Zone-based AI feature enablement matrix"
key-files:
  created: []
  modified:
    - path: "docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md"
      lines_added: 98
      significance: "Expanded AI Feature Access Control section with zone-based enablement, admin exclusion groups, deployment groups, and comprehensive FSI guidance"
    - path: "docs/playbooks/control-implementations/3.8/portal-walkthrough.md"
      lines_added: ~250
      significance: "Added detailed AI feature access configuration steps with zone-specific guidance"
    - path: "docs/playbooks/control-implementations/3.8/powershell-setup.md"
      lines_added: ~210
      significance: "Added PowerShell functions for admin exclusion group management and compliance export"
    - path: "docs/playbooks/control-implementations/3.8/verification-testing.md"
      lines_added: ~180
      significance: "Added three new test cases (FAC-01, FAC-02, FAC-03) for AI feature access validation"
    - path: "docs/playbooks/control-implementations/3.8/troubleshooting.md"
      lines_added: ~120
      significance: "Added troubleshooting for admin exclusion, deployment groups, and web search control"
decisions:
  - id: "CTRL-03-ZONES"
    what: "Zone-based AI feature enablement matrix with regulatory rationale per zone"
    why: "FSI organizations need clear guidance on how to configure AI feature access controls aligned with three-zone governance model"
    alternatives: "Generic configuration guidance without zone differentiation"
    impact: "Enables zone-specific rollout strategies (Zone 1: all users, Zone 2: phased, Zone 3: strict controls)"
  - id: "CTRL-03-EXCLUSION"
    what: "Admin Exclusion Group pattern using CopilotForM365AdminExclude security group"
    why: "Microsoft-documented pattern for excluding users from Copilot regardless of license"
    alternatives: "License-based removal (slower, more complex), Conditional Access (broader scope)"
    impact: "FSI organizations can quickly exclude traders during blackouts, employees under investigation, restricted persons"
  - id: "CTRL-03-PHASED"
    what: "Four-phase deployment group rollout (Pilot, Wave 1, Wave 2, Wave 3)"
    why: "Regulatory compliance requires controlled change management with validation gates"
    alternatives: "Big-bang rollout, zone-only rollout (no phasing within zones)"
    impact: "Supports SEC/SOX controlled change requirements, enables rollback at each phase"
  - id: "CTRL-03-PROPAGATION"
    what: "Document 24-hour propagation for exclusion groups, 8-hour for settings"
    why: "Critical for compliance planning — exclusion not immediate"
    alternatives: "Assume real-time enforcement (incorrect)"
    impact: "FSI organizations can plan blackout period exclusions with appropriate lead time"
metrics:
  duration: "~90 minutes"
  completed: "2026-02-06"
  files_modified: 5
  commits: 2
  test_cases_added: 3
  functions_added: 6
---

# Phase 07 Plan 03: AI Feature Access Control in Control 3.8 Summary

**One-liner:** Comprehensive AI Feature Access Control documentation in Control 3.8 with zone-based enablement matrix, admin exclusion groups (CopilotForM365AdminExclude pattern), deployment group phased rollout, and FSI-specific governance guidance across all four playbooks.

---

## What Was Done

### Control Enhancement

Expanded Control 3.8's existing AI Feature Access Control subsection from basic 6-row feature table to comprehensive governance documentation:

1. **GA Feature Admonition**: Added `!!! info "GA Feature"` clarifying AI Feature Access Control settings are generally available
2. **Zone-Based AI Feature Enablement Matrix**: Created comprehensive table mapping six settings (User Access, Admin Exclusion Groups, Deployment Groups, Web Search, Copilot Chat Pinning, Agent Access Control) across three zones with regulatory rationale (SOX 404, FINRA 3110, SEC, GLBA 501(b), FINRA 4511)
3. **Admin Exclusion Group Configuration**: Documented `CopilotForM365AdminExclude` security group pattern with FSI use cases (traders during blackouts, compliance investigations, restricted persons lists, customer-facing trial periods)
4. **Deployment Group Rollout Strategy**: Defined four-phase rollout pattern (Pilot: 4-6 weeks, Wave 1: 8-12 weeks, Wave 2: 12-16 weeks, Wave 3: ongoing) with zone-aligned recommendations and rollback procedures
5. **FSI Governance Guidance**: Expanded from single paragraph to comprehensive subsection with regulatory mapping (FINRA 4511, GLBA 501(b), SOX 404, SEC 17a-3), recommended control configuration, and monthly governance review checklist
6. **Roles & Responsibilities Update**: Added Compliance Officer responsibility for reviewing and approving Admin Exclusion Group membership

### Playbook Updates

Updated all four Control 3.8 playbooks with AI feature access-specific content:

**portal-walkthrough.md:**
- Step-by-step Admin Exclusion Group creation in Entra ID (exact group naming, membership management, FSI population examples)
- Deployment group configuration with four-phase rollout structure
- Zone-specific configuration guidance for User Access, Data Access, Actions, and End-User Experience settings
- Propagation delay warnings (24 hours for exclusion groups, 8 hours for settings)
- Verification steps for settings propagation with zone-specific test scenarios

**powershell-setup.md:**
- `New-CopilotAdminExclusionGroup`: Create exclusion group with validation
- `Add-UsersToAdminExclusionGroup`: Add users by UPN array
- `Import-AdminExclusionGroupFromCSV`: Bulk operations from CSV (supports Reason, AddedBy, AddedDate columns)
- `Export-AdminExclusionGroupMembers`: Export for compliance evidence
- `Get-CopilotSettings`: Query Copilot settings via Microsoft Graph API
- `Export-CopilotConfigurationForCompliance`: Generate audit package with exclusion group membership, settings, and audit events

**verification-testing.md:**
- **Test Case FAC-01**: Verify Admin Exclusion Group correctly removes Copilot access (includes 24-hour propagation validation, license assignment verification, restoration test)
- **Test Case FAC-02**: Verify Deployment Group limits Copilot availability to specified user population (two-user test, license vs. group isolation)
- **Test Case FAC-03**: Verify web search disabled prevents external data access (baseline test, propagation validation, organizational data verification)
- Expanded evidence collection with AI feature access control artifacts (exclusion group exports, deployment group assignments, web search settings, propagation validation evidence)

**troubleshooting.md:**
- User still has Copilot access after exclusion: 24-hour propagation, exact group name validation, nested group checks, conflicting policies, token refresh
- Deployment group not limiting access: Security group type verification, license assignment checks, 8-hour propagation, exclusion group precedence
- Web search still returning results: 8-hour propagation, tenant-level scope verification, organizational data vs. web data distinction, user-level override checks

---

## Deviations from Plan

None — plan executed exactly as written. All required enhancements completed:

- ✅ GA admonition added
- ✅ Zone-based AI feature enablement matrix created
- ✅ Admin Exclusion Group configuration documented with CopilotForM365AdminExclude pattern
- ✅ Deployment Group rollout strategy defined with four phases
- ✅ FSI governance guidance expanded with regulatory mapping and monthly review checklist
- ✅ All 4 playbooks updated with AI feature access-specific sections
- ✅ PowerShell functions for exclusion group management and Graph API queries
- ✅ Three new test cases (FAC-01, FAC-02, FAC-03)
- ✅ Troubleshooting entries for common AI feature access issues

---

## Task Commits

| Task | Description | Commit | Files Modified |
|------|-------------|--------|----------------|
| 1 | Expand AI Feature Access Control in Control 3.8 | `cfa29df` | 3.8-copilot-hub-and-governance-dashboard.md |
| 2 | Update Control 3.8 Playbooks for AI Feature Access Control | `b12e87b` | portal-walkthrough.md, powershell-setup.md, verification-testing.md, troubleshooting.md |

---

## Decisions Made

### Zone-Based AI Feature Enablement Matrix

**Decision**: Created comprehensive zone-based enablement matrix mapping six AI feature access settings across three governance zones with regulatory rationale per setting.

**Rationale**: FSI organizations implementing the three-zone model need explicit guidance on how to configure AI feature access controls aligned with zone risk profiles. Generic "configure to meet your needs" guidance insufficient for regulated environments requiring documented control decisions.

**Impact**: Organizations can now implement zone-specific Copilot rollouts with clear regulatory justification:
- Zone 1 (Personal): Permissive settings, all licensed users, optional deployment groups
- Zone 2 (Team): Moderate restrictions, MNPI team web search disabled, recommended phased rollout
- Zone 3 (Enterprise): Strictest controls, specific user groups only, mandatory phased rollout, organizational agents only

**Example**: Web search setting guidance differs by zone — enabled in Zone 1 (personal productivity has lower data exposure risk), disabled for MNPI teams in Zone 2, disabled organization-wide in Zone 3 (GLBA 501(b) rationale: prevent external data leakage from customer interactions).

### Admin Exclusion Group Pattern

**Decision**: Documented `CopilotForM365AdminExclude` security group pattern as primary mechanism for excluding users from Copilot regardless of license assignment.

**Rationale**: Microsoft-documented exclusion group pattern provides faster, more targeted control than license removal (which affects billing and may require re-provisioning) or Conditional Access policies (which have broader scope and complexity).

**Impact**: FSI organizations can now quickly exclude specific user populations for compliance reasons:
- Traders during quarterly blackout periods (temporary, FINRA/SEC insider trading prevention)
- Employees under compliance investigation (temporary, FINRA 3110 enhanced supervision)
- Restricted persons lists (permanent/semi-permanent, FINRA 2111 conflict management)
- Customer-facing roles during pilot phase (temporary, risk management)

**Critical detail**: 24-hour propagation delay documented — exclusion NOT real-time. Organizations must plan exclusions with appropriate lead time (add trader to exclusion group 24 hours before blackout period starts).

### Four-Phase Deployment Group Rollout

**Decision**: Defined four-phase deployment group rollout pattern (Pilot: 4-6 weeks → Wave 1: 8-12 weeks → Wave 2: 12-16 weeks → Wave 3: ongoing) with validation criteria and rollback procedures per phase.

**Rationale**: Regulatory compliance (SEC controlled change management, SOX 404 documented IT controls) requires staged rollout with validation gates. Big-bang Copilot deployment introduces excessive risk for customer-facing FSI environments.

**Impact**: Organizations have documented rollout pattern aligned with regulatory requirements:
- Pilot phase validates feature functionality and compliance controls with IT/Compliance users (low risk)
- Wave 1 expands to non-customer-facing business units with usage metrics validation
- Wave 2 introduces customer-facing roles with supervision workflow validation (highest risk, longest validation period)
- Wave 3 full rollout after all controls validated

**Rollback procedure documented**: Remove users from deployment group (takes effect within 8 hours), document rollback reason, conduct root cause analysis, update validation criteria before resuming.

### Propagation Delay Documentation

**Decision**: Explicitly document 24-hour propagation for Admin Exclusion Group membership changes and 8-hour propagation for Copilot settings changes throughout control and playbooks.

**Rationale**: Compliance teams planning trader blackout exclusions or emergency Copilot access removals must understand enforcement is NOT real-time. Undocumented propagation delays lead to compliance incidents (trader gains Copilot access during blackout because exclusion not yet propagated).

**Impact**: All playbooks now include propagation delay warnings at configuration steps and verification test cases validate propagation timing. Organizations can plan exclusions and settings changes with appropriate lead time.

---

## Integration Points

### With Existing Controls

- **Control 1.1 (Restrict Agent Publishing)**: Admin Exclusion Groups and deployment groups control who can ACCESS agents; Control 1.1 controls who can PUBLISH agents — complementary controls
- **Control 1.2 (Agent Registry)**: Agent Access Control setting (organizational only / Microsoft verified / all agents) determines what appears in registry for each user population
- **Control 3.2 (Usage Analytics)**: Deployment group phased rollout generates usage metrics per phase for validation before proceeding to next wave
- **Control 3.7 (PPAC Security Posture)**: Web search control and external AI provider blocking enhance overall security posture assessed in Control 3.7

### With Solutions

- **FSI-AgentGov-Solutions/conditional-access-automation**: Admin Exclusion Groups complement Conditional Access policies for Copilot access control (exclusion groups = user-level, CA = device/location/risk-level)
- **FSI-AgentGov-Solutions/compliance-dashboard**: Deployment group assignments and Admin Exclusion Group membership should feed compliance dashboard for rollout status visualization

---

## Testing & Validation

### Test Cases Created

**Test Case FAC-01: Admin Exclusion Group Correctly Removes Copilot Access**
- **Scope**: User-level exclusion enforcement
- **Validation**: User in exclusion group cannot access Copilot despite valid license
- **Evidence**: Screenshots before/after exclusion, Entra ID audit log, 24-hour propagation verification
- **Regulatory Mapping**: FINRA 3110, SOX 404

**Test Case FAC-02: Deployment Group Limits Copilot Availability**
- **Scope**: Deployment group enforcement
- **Validation**: User inside deployment group has access, user outside (with license) does not
- **Evidence**: Deployment group membership list, license assignment report, access screenshots for both users
- **Regulatory Mapping**: SEC controlled change management, SOX 404

**Test Case FAC-03: Web Search Disabled Prevents External Data Access**
- **Scope**: Web search control enforcement
- **Validation**: With web search disabled, Copilot cannot access external web data
- **Evidence**: Baseline test with web enabled, post-change test with web disabled, organizational data verification
- **Regulatory Mapping**: GLBA 501(b), FINRA MNPI protection

### Evidence Collection

Expanded evidence collection guidance to include:
- Admin Exclusion Group membership exports (monthly)
- Deployment group assignments per phase
- Web search control settings per zone
- Agent access control settings per zone
- Copilot Chat pinning configuration per department/role
- 24-hour propagation validation evidence for exclusion groups
- 8-hour propagation validation evidence for settings

---

## Next Phase Readiness

### Blockers

None identified. Control 3.8 enhancements complete and verified (mkdocs build passes).

### Concerns

None. AI Feature Access Control capabilities are GA (not preview), reducing future update risk.

### Recommendations for Future Work

1. **Monitor Microsoft roadmap for unified Copilot governance**: As Microsoft Agent 365 matures, Admin Exclusion Groups and deployment groups may consolidate into unified governance experience — plan to update documentation when GA
2. **Track propagation delay improvements**: Microsoft may reduce 24-hour exclusion group propagation in future — monitor for updates to improve compliance response time
3. **Deployment group automation**: Consider FSI-AgentGov-Solutions implementation for automated deployment group management (CSV-based wave assignments, approval workflow integration)
4. **Integration with FINRA supervision workflows**: Admin Exclusion Group membership changes should trigger supervision system notifications when excluding/restoring traders or customer-facing roles

---

## Self-Check: PASSED

**Files Created:**
- ✅ `.planning/phases/07-control-enhancements-role-updates/07-03-SUMMARY.md` (this file)

**Files Modified (verified existence):**
- ✅ `docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- ✅ `docs/playbooks/control-implementations/3.8/portal-walkthrough.md`
- ✅ `docs/playbooks/control-implementations/3.8/powershell-setup.md`
- ✅ `docs/playbooks/control-implementations/3.8/verification-testing.md`
- ✅ `docs/playbooks/control-implementations/3.8/troubleshooting.md`

**Commits (verified existence):**
- ✅ `cfa29df`: feat(07-03): expand AI Feature Access Control in Control 3.8
- ✅ `b12e87b`: feat(07-03): update Control 3.8 playbooks for AI Feature Access Control

**Build Verification:**
- ✅ `mkdocs build --strict` passes with zero errors

---

*Phase: 07-control-enhancements-role-updates*
*Plan: 03 of 05*
*Completed: 2026-02-06*
*Duration: ~90 minutes*
*Status: COMPLETE*
