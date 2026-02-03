---
phase: 04-feature-enhancement-updates
plan: "01"
subsystem: data-protection
tags: [dlp, virtual-connectors, copilot-studio, power-platform, fsi-compliance]
requires:
  - 01-comprehensive-audit (Control 1.5 baseline)
  - 03-agent-365-architecture (Zone 3 governance patterns)
provides:
  - Complete virtual governance connector documentation for Control 1.5
  - FSI-specific DLP classification guidance for 11 connectors
  - Portal configuration steps for virtual connector DLP
  - Verification test cases for virtual connector enforcement
affects:
  - Future Control 2.x enhancements (may reference virtual connector DLP patterns)
  - Control 1.6 DSPM integration (virtual connector telemetry)
tech-stack:
  added: []
  patterns:
    - Standardized Feature | Status | Description | Configuration table format
    - Virtual governance connector classification (Business/Non-Business/Blocked)
    - HTTP endpoint filtering for external API control
key-files:
  created: []
  modified:
    - docs/controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md
    - docs/playbooks/control-implementations/1.5/portal-walkthrough.md
    - docs/playbooks/control-implementations/1.5/verification-testing.md
key-decisions:
  - decision: "Integrate virtual connector table into existing DLP section without creating standalone subsection"
    rationale: "Seamless integration per Phase 4 CONTEXT.md pattern; avoids temporal section headings"
    impact: "Natural extension of existing connector categories table"
  - decision: "Zone 3 blocks HTTP Webhook and Custom Website Channel by default"
    rationale: "FSI risk posture requires authenticated calls and approved publishing channels"
    impact: "FSI organizations have clear default posture for high-risk connectors"
  - decision: "HTTP endpoint filtering configuration included in portal walkthrough"
    rationale: "Critical Zone 3 control for external API access"
    impact: "Administrators have step-by-step guidance for endpoint allow/block lists"
metrics:
  duration: "5 minutes 10 seconds"
  started: "2026-02-03T21:38:55Z"
  completed: "2026-02-03T21:44:04Z"
  tasks: 2
  files_modified: 3
  commits: 2
---

# Phase 04 Plan 01: Virtual Governance Connector Documentation Summary

**One-liner:** Enhanced Control 1.5 DLP guidance with complete 11-connector virtual governance table, FSI classification recommendations, and playbook configuration/verification steps for Power Platform connector enforcement.

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| **Execution Time** | 5 minutes 10 seconds (310 seconds) |
| **Started** | 2026-02-03T21:38:55Z |
| **Completed** | 2026-02-03T21:44:04Z |
| **Tasks Completed** | 2/2 (100%) |
| **Files Modified** | 3 |
| **Commits Created** | 2 task commits |

---

## What Was Accomplished

### Control 1.5 Enhancement

Enhanced Control 1.5 (DLP and Sensitivity Labels) with comprehensive virtual governance connector documentation:

1. **Standardized Connector Table** - Added Feature | Status | Description | Configuration table listing all 11 Copilot Studio virtual governance connectors:
   - AI Builder (GPT)
   - AI Builder (Document Processing)
   - Copilot Studio Topics
   - Copilot Studio Skills
   - Copilot Studio Knowledge
   - HTTP with Microsoft Entra ID
   - HTTP Webhook
   - Direct Line
   - Microsoft Teams Channel
   - SharePoint Channel
   - Custom Website Channel

2. **FSI Governance Recommendations** - Provided Zone 3-specific guidance:
   - Block HTTP Webhook and Custom Website Channel by default
   - Business-classify AI Builder and core Copilot Studio connectors
   - Require Control 1.3 SharePoint governance before allowing Knowledge connector
   - HTTP endpoint filtering for authenticated HTTP calls

3. **Seamless Integration** - Virtual connector table integrated naturally into existing "Copilot Studio DLP Connector Categories" section without temporal headings or standalone subsections

### Portal Walkthrough Playbook

Updated `portal-walkthrough.md` with new Step 2: Configure Virtual Governance Connectors:

- Step-by-step connector classification in Power Platform Admin Center
- FSI-specific classification table for Zone 3 environments
- HTTP endpoint filtering configuration (allow list/block list)
- Verification steps to confirm all 11 connectors classified

### Verification Testing Playbook

Updated `verification-testing.md` with 6 new virtual connector test cases (VC-01 through VC-06):

- VC-01: Agent creation with blocked connector
- VC-02: HTTP call to non-allowlisted endpoint
- VC-03: Verify all 11 connectors classified
- VC-04: Knowledge Source connector with approved SharePoint
- VC-05: Channel connector enforcement
- VC-06: AI Builder GPT connector usage

Added evidence collection requirements for virtual connector DLP compliance.

---

## Task Commits

| Task | Description | Commit | Files Modified |
|------|-------------|--------|----------------|
| 1 | Enhance Control 1.5 with standardized virtual connector table | 29b4e60 | 1.5-data-loss-prevention-dlp-and-sensitivity-labels.md |
| 2 | Update playbooks with virtual connector configuration and verification | 99366a9 | portal-walkthrough.md, verification-testing.md |

---

## Files Created

None (enhancements to existing files only).

---

## Files Modified

| File | Changes |
|------|---------|
| `docs/controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md` | Added Virtual Governance Connectors section with 11-connector table and FSI recommendations (24 lines added) |
| `docs/playbooks/control-implementations/1.5/portal-walkthrough.md` | Added Step 2 with virtual connector classification guidance, FSI Zone 3 table, and HTTP endpoint filtering steps (97 lines added, 10 renumbered) |
| `docs/playbooks/control-implementations/1.5/verification-testing.md` | Added 6 virtual connector test cases (VC-01 through VC-06) and updated confirmation checklist (33 lines added) |

---

## Decisions Made

### 1. Integration Pattern
**Decision:** Integrated virtual connector table into existing "Copilot Studio DLP Connector Categories" section rather than creating a new standalone subsection.

**Rationale:** Per Phase 4 CONTEXT.md guidance, new features should integrate seamlessly without temporal section headings like "New Features" or "2026 Updates."

**Impact:** Virtual connector documentation feels like a natural extension of existing DLP guidance, maintaining documentation cohesion.

### 2. Zone 3 Default Posture
**Decision:** Recommend blocking HTTP Webhook and Custom Website Channel connectors by default for Zone 3 environments.

**Rationale:** FSI risk posture requires authenticated external calls and approved publishing channels. HTTP Webhook allows unauthenticated calls (data exfiltration risk), and Custom Website Channel enables publishing to external websites without security review.

**Impact:** FSI organizations have clear, conservative default recommendations for high-risk connectors.

### 3. HTTP Endpoint Filtering
**Decision:** Include HTTP endpoint filtering configuration in portal walkthrough Step 2.

**Rationale:** HTTP endpoint filtering is a critical Zone 3 control for preventing agent data exfiltration via external API calls. Configuration steps are non-obvious and require allow list/block list pattern guidance.

**Impact:** Administrators have complete guidance for restricting HTTP calls to approved internal APIs.

### 4. Test Case Structure
**Decision:** Created 6 dedicated virtual connector test cases (VC-01 through VC-06) separate from existing AI test cases (AI-01 through AI-05).

**Rationale:** Virtual connector DLP enforcement is a distinct capability from content-based DLP (SIT detection, label enforcement). Separate test case IDs enable clear evidence collection and audit trail.

**Impact:** Verification testing playbook provides comprehensive coverage of both content-based DLP and connector-based DLP enforcement.

---

## Deviations from Plan

None. Plan executed exactly as written.

---

## Issues Encountered

None. All tasks completed without errors or blockers.

---

## Verification Results

All verification criteria met:

- [x] `python3 -m mkdocs build --strict` passes with zero errors
- [x] Control 1.5 contains standardized connector table with all 11 virtual governance connectors
- [x] Portal walkthrough includes virtual connector configuration steps (Step 2)
- [x] Verification testing includes 6 virtual connector test cases (VC-01 through VC-06)
- [x] No "New Features" or temporal section headings created (seamless integration confirmed)

---

## Next Phase Readiness

### Ready for Next Plan (04-02)

Control 1.5 now provides complete virtual governance connector documentation, enabling Phase 4 to proceed with additional feature enhancements across other controls.

### Dependencies Created

Future Control 1.6 (DSPM for AI) enhancements may reference virtual connector telemetry integration for AI observability.

### No Blockers Identified

All 11 connectors documented with GA status. No preview features or external dependencies.

---

## Key Learnings

1. **Seamless Integration Works:** Adding the virtual connector table as a natural extension of existing DLP connector categories (rather than a standalone section) maintains documentation cohesion and avoids visible temporal seams.

2. **FSI Guidance Value:** Providing Zone 3-specific connector classifications (Business/Non-Business/Blocked) gives FSI administrators actionable default posture without requiring deep risk analysis.

3. **Test Case Separation:** Using distinct test case ID prefixes (VC-01 vs AI-01) clarifies coverage across different DLP enforcement mechanisms (connector-based vs content-based).

4. **HTTP Endpoint Filtering Critical:** HTTP connector configuration is complex (allow list vs block list, pattern matching) and warrants detailed step-by-step guidance for Zone 3 environments.

---

## Recommended Follow-up

1. **Learn Monitor Update:** Add the following Microsoft Learn URLs to `scripts/learn_monitor.py` for ongoing virtual connector guidance monitoring:
   - `https://learn.microsoft.com/en-us/power-platform/admin/dlp-connector-classification`
   - `https://learn.microsoft.com/en-us/power-platform/admin/dlp-http-endpoint-filtering`

2. **Control 1.6 Integration:** Consider enhancing Control 1.6 (DSPM for AI) with virtual connector telemetry guidance when Agent 365 Observability SDK documentation becomes available.

3. **Solutions Coverage:** FSI-AgentGov-Solutions `conditional-access-automation` solution could be enhanced to validate virtual connector DLP policy configuration as part of compliance dashboard metrics.

---

*Plan completed: 2026-02-03T21:44:04Z | Duration: 5 minutes 10 seconds | Status: Success*
