# Phase 1 Research: Control Documentation & Playbooks

## Phase Goal

Create Control 2.22 (Inactivity Timeout Enforcement) documentation following the 10-section template, 4 implementation playbooks, and screenshot specification. This is a Management Pillar control governing Power Platform user inactivity timeout settings with zone-based policy-driven maximum duration requirements.

## Requirements Covered

- **CTL-01:** Control 2.22 documentation (10-section template)
- **CTL-02:** 4 playbooks (portal-walkthrough, powershell-setup, verification-testing, troubleshooting)
- **CTL-03:** Screenshot specification (EXPECTED.md)

## Technical Analysis

### Control Template Structure (from `docs/templates/control-setup-template.md`)

**Header metadata (5+ fields):**
- Control ID, Pillar, Regulatory Reference, Last UI Verified, Governance Levels
- Extra `**Last Verified:**` field for consistency with recent controls (2.21 pattern)

**10 mandatory sections:**

| # | Section | Content Pattern |
|---|---------|-----------------|
| 1 | Objective | Single paragraph, concise purpose |
| 2 | Why This Matters for FSI | Bulleted list: `**[Regulation]:** [Hedged description]` |
| 3 | Control Description | Multi-paragraph technical; capability tables, sub-headings |
| 4 | Key Configuration Points | Bulleted list of specific settings |
| 5 | Zone-Specific Requirements | 3-row table: Zone 1/2/3 with Requirement and Rationale |
| 6 | Roles & Responsibilities | 2-column table: Role / Responsibility |
| 7 | Related Controls | 2-column table: Control (relative link) / Relationship |
| 8 | Implementation Playbooks | Info admonition with 4 playbook links |
| 9 | Verification Criteria | Numbered checklist (5-6 items) |
| 10 | Additional Resources | Bulleted Microsoft Learn links |

**Footer metadata:**
```
*Updated: February 2026 | Version: v1.3 | UI Verification Status: Current*
```

**Exemplar enrichments (from Control 2.21):**
- Extra `**Last Verified:**` field after Governance Levels
- `!!! info` process context admonition after Section 3 heading
- `!!! tip "Implementation Approach"` admonition in Implementation Playbooks section
- Rich control description with capability comparison tables
- Sub-headed Key Configuration Points (grouped by category)

### Playbook Structure Patterns (from 2.21 exemplar)

**Portal Walkthrough:**
- Title: `# Portal Walkthrough: Control X.X - [Name]`
- Metadata: Last Updated, Portal, Estimated Time
- Prerequisites: Checkbox list
- Body: Numbered `### Step N:` sections with portal paths
- Governance table by zone; validation checklist; footer nav

**PowerShell Setup:**
- Title: `# PowerShell Setup: Control X.X - [Name]`
- Metadata: Last Updated, Modules Required
- Prerequisites: Install-Module commands
- Scripts with comment-based help (.SYNOPSIS, .EXAMPLE)
- Validation script with [PASS]/[FAIL]/[INFO] pattern
- Complete configuration script with param() and try/catch/finally
- Footer nav

**Verification & Testing:**
- Title: `# Verification & Testing: Control X.X - [Name]`
- Manual verification: `### Test N:` with `**EXPECTED:**`
- Test cases table (TC-X.X-NN format)
- Evidence collection checklist, attestation template
- Zone-specific testing requirements table
- Footer nav

**Troubleshooting:**
- Title: `# Troubleshooting: Control X.X - [Name]`
- Common issues summary table (Issue / Cause / Resolution)
- Detailed `### Issue:` sections with Symptoms, Resolution, Portal Path
- Escalation path, known limitations table
- Diagnostic commands, related documentation links
- Footer nav

### EXPECTED.md Format

H3-based descriptive format (consistent with 2.21 pattern):

```markdown
# Control X.X: [Name] - Screenshot Specifications

## Required Screenshots

### Screenshot N: [Descriptive Title]
**Portal Path:** [Portal] → [Menu] → [Submenu] → [Page]
**What to capture:**
- [Specific UI element 1]
- [Specific UI element 2]
```

### Cross-Reference Link Conventions

- Same-pillar: `[2.1 - Managed Environments](2.1-managed-environments.md)`
- Cross-pillar: `[1.23 - Step-Up Authentication](../pillar-1-security/1.23-step-up-authentication-for-agent-operations.md)`
- Reporting: `[3.7 - PPAC Security Posture](../pillar-3-reporting/3.7-ppac-security-posture-assessment.md)`

## Architecture Decisions

1. **Control filename:** `2.22-inactivity-timeout-enforcement.md` (per ROADMAP.md file manifest)
2. **Zone model:** Zone 1 = Optional (personal agents, low risk); Zone 2 = Required ≤120 min (team collaboration); Zone 3 = Required ≤60 min (enterprise/customer-facing)
3. **API endpoint:** BAP Admin API privacy settings endpoint — NOT Graph API (Graph is for SSC/v5/Control 1.23)
4. **Canonical identifier:** EnvironmentName (Power Platform Environment Name) — NOT display name
5. **Policy-driven:** Zone requirements stored in `fsi_environmentpolicy` Dataverse table; no hard-coded thresholds
6. **Missing policy → Unknown:** No silent defaults; MissingPolicy logged to error log table
7. **Complementary controls:**
   - 1.23 (Step-Up Authentication) — SSC controls session authentication; 2.22 controls inactivity timeout duration
   - 2.1 (Managed Environments) — Environment governance scope
   - 3.7 (PPAC Security Posture) — Existing SSPM-3.7-06 item checks inactivity timeout; 2.22 provides dedicated governance
   - 3.8 (Copilot Hub and Governance Dashboard) — Compliance scan results feed governance dashboard
8. **Hardening baseline item 30:** Currently references `[3.7]` — Phase 5 updates to `[2.22, 3.7]`
9. **Regulatory mapping:** GLBA 501(b) information safeguards, SOX 302 management responsibility, FINRA 4511 record-keeping, NIST 800-53 AC-11 (session lock), AC-12 (session termination)

## Canonical Role Names (from role-catalog.md)

| Role | Responsibility for 2.22 |
|------|------------------------|
| **Power Platform Admin** | Configure inactivity timeout in PPAC; run remediation scripts |
| **Environment Admin** | Environment-level timeout settings |
| **AI Governance Lead** | Define zone policy requirements; review compliance scan results |
| **Compliance Officer** | Review compliance reports; audit attestation |

## Existing Inactivity Timeout References

| Location | Reference | Relevance |
|----------|-----------|-----------|
| `3.7/verification-testing.md` line 116 | SSPM-3.7-06 inactivity timeout check item | 2.22 provides dedicated governance for this item |
| `3.7/portal-walkthrough.md` line 162 | Inactivity timeout enabled ≤120 min | Baseline check; 2.22 adds zone-specific enforcement |
| Hardening baseline `index.md` line 104 | Item 30: Inactivity timeout, PPAC Privacy + Security | 2.22 provides full control and automation |

## Risk Assessment

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 1 | BAP Admin API privacy settings endpoint may have changed | Medium | Mark `Last UI Verified: February 2026`; define EXPECTED.md screenshots for future verification |
| 2 | Zone requirements (≤120/≤60) need validation against industry standards | Low | Use NIST 800-53 AC-11/AC-12 as authoritative source |
| 3 | Overlap with SSPM-3.7-06 may confuse readers | Medium | Clearly document 2.22 as dedicated governance; 3.7 as basic posture check |
| 4 | PowerShell playbook references Set-InactivityTimeout.ps1 (Phase 4 deliverable) | Low | Reference by design intent; playbook describes anticipated script interface |
| 5 | FSI language rule violations | Low | Apply hedged language throughout; verification by verify_language_rules.py |
| 6 | Portal path: PPAC → Environment → Settings → Privacy + Security may vary | Medium | Document current known path; mark for UI verification |

## Recommended Approach

### Plan A: Control 2.22 Document (01-01-PLAN.md)
- Create `docs/controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md`
- Follow 10-section template with 2.21 enrichment patterns
- Header: Control ID 2.22, Pillar Management, GLBA/SOX/FINRA/NIST references
- Zone table: Zone 1 Optional / Zone 2 ≤120 min / Zone 3 ≤60 min
- Related controls: 1.23, 2.1, 3.7, 3.8 with correct relative links
- Capability table: BAP Admin API, policy-driven compliance, Dataverse persistence
- Roles: Power Platform Admin, Environment Admin, AI Governance Lead, Compliance Officer
- Implementation playbook links to Phase 1 Plan B deliverables
- FSI-safe language throughout

### Plan B: Playbooks + EXPECTED.md (01-02-PLAN.md)
- Create 4 playbooks in `docs/playbooks/control-implementations/2.22/`
  - Portal walkthrough: PPAC Privacy + Security settings → inactivity timeout
  - PowerShell setup: Set-InactivityTimeout.ps1 usage (reference Phase 4 script)
  - Verification testing: Dataverse compliance records review, flow output validation
  - Troubleshooting: MissingPolicy, 401/403/404/429 errors, BAP API connectivity
- Create `docs/images/2.22/EXPECTED.md` with 4 screenshots
- Follow 2.21 playbook patterns exactly
- FSI-safe language throughout

### Wave Assignment
Both plans target non-overlapping file sets → **Wave 1** (parallel-eligible).
- Plan A: `docs/controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md`
- Plan B: `docs/playbooks/control-implementations/2.22/*`, `docs/images/2.22/EXPECTED.md`

---
*Research completed: 2026-02-12*
*Phase: 01 — Control Documentation & Playbooks*
*Milestone: v19 — Inactivity Timeout Enforcement*
