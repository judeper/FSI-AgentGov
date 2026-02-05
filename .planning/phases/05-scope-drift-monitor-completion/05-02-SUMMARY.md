---
phase: 05-scope-drift-monitor-completion
plan: 02
subsystem: scope-drift-monitor-solution
tags: [power-platform, dataverse, power-automate, solution-package, audit-log, adaptive-cards]
requires:
  - phase: 05-01
    provides: planning, research, context
provides:
  - unpacked-solution-source
  - dataverse-schema-definitions
  - detection-flow
  - alert-flow
  - connection-references
  - environment-variables
affects: [05-03, 05-04]
tech-stack:
  added: []
  patterns: [power-platform-solution-packaging, workflow-definition-language, office-365-management-api]
key-files:
  created:
    - scope-drift-monitor/src/ScopeDriftMonitor/Other/Solution.xml
    - scope-drift-monitor/src/ScopeDriftMonitor/Other/Customizations.xml
    - scope-drift-monitor/src/ScopeDriftMonitor/[Content_Types].xml
    - scope-drift-monitor/src/ScopeDriftMonitor/Workflows/SDM-DriftDetector.json
    - scope-drift-monitor/src/ScopeDriftMonitor/Workflows/SDM-AlertDispatcher.json
    - scope-drift-monitor/src/ScopeDriftMonitor/connectionreferences.json
    - scope-drift-monitor/src/ScopeDriftMonitor/environmentvariables.json
  modified: []
key-decisions:
  - id: unpacked-solution-format
    choice: Use unpacked solution directory structure following Compliance Dashboard pattern
    rationale: Enables version control and pac CLI packaging
  - id: flow-language
    choice: Workflow Definition Language (JSON) for flow definitions
    rationale: Standard Power Automate format for solution packaging
  - id: connection-parameterization
    choice: Connection references + environment variables for all configurable settings
    rationale: Allows customer configuration during import without flow edits
  - id: graceful-degradation
    choice: Continue detection with reduced coverage when audit sources unavailable
    rationale: Per CONTEXT.md - log warning and continue, never fail entire detection run
  - id: dual-delivery
    choice: Both Teams Adaptive Card and email for each violation
    rationale: Per CONTEXT.md decision for alert behavior
patterns-established:
  - "Office 365 Management API polling: Use HTTP with Azure AD connector, handle 90-min latency"
  - "Violation creation pattern: Set status to Open (1), detect on trigger to Under Investigation (2)"
  - "Connection reference naming: fsi_cr_ prefix for all connection references"
  - "Environment variable naming: fsi_SDM_ prefix for Scope Drift Monitor variables"
duration: 6m
completed: 2026-02-05
---

# Phase 05 Plan 02: Solution Package Source Creation Summary

**Complete Power Platform solution source with 4-table Dataverse schema, 15-minute detection flow polling Office 365 Management API, and dual-delivery alert flow with Teams Adaptive Cards**

## Performance

- **Duration:** 6 minutes
- **Started:** 2026-02-05T01:36:55Z
- **Completed:** 2026-02-05T01:42:48Z
- **Tasks:** 3/3
- **Files created:** 7

## Accomplishments

- Created unpacked Power Platform solution source (v1.1.0) with FSIAgentGov publisher
- Defined complete Dataverse schema for 4 tables (60+ attributes across fsi_agentscope, fsi_scopeitem, fsi_scopeviolation, fsi_expansionrequest)
- Implemented SDM-DriftDetector flow with 15-minute scheduled polling of Office 365 Management API
- Implemented SDM-AlertDispatcher flow with Teams Adaptive Card and email dual delivery
- Parameterized solution with 5 connection references and 6 environment variables

## Task Commits

Each task was committed atomically:

1. **Task 1: Create solution package source structure with Dataverse schema** - `9c8d330` (feat)
2. **Task 2: Create SDM-DriftDetector and SDM-AlertDispatcher flow definitions** - `1287606` (feat)
3. **Task 3: Add connection references and environment variables** - `eb867f4` (feat)

**Repository:** FSI-AgentGov-Solutions (cross-repo work from FSI-AgentGov)

## Files Created

| File | Size | Purpose |
|------|------|---------|
| `src/ScopeDriftMonitor/Other/Solution.xml` | 2.9 KB | Solution manifest (v1.1.0, FSIAgentGov publisher) |
| `src/ScopeDriftMonitor/Other/Customizations.xml` | 27 KB | 4 Dataverse tables with all attributes and relationships |
| `src/ScopeDriftMonitor/[Content_Types].xml` | 466 B | Standard content type mappings |
| `src/ScopeDriftMonitor/Workflows/SDM-DriftDetector.json` | 21 KB | 15-minute detection flow |
| `src/ScopeDriftMonitor/Workflows/SDM-AlertDispatcher.json` | 11 KB | Alert delivery flow |
| `src/ScopeDriftMonitor/connectionreferences.json` | 1.4 KB | 5 connection references |
| `src/ScopeDriftMonitor/environmentvariables.json` | 1.9 KB | 6 environment variables |

**Total:** ~65 KB of solution source across 7 files

## Decisions Made

### Unpacked Solution Format

**Context:** Power Platform solutions can be stored as zip files or unpacked directories.

**Choice:** Unpacked solution directory structure following Compliance Dashboard pattern from Phase 4.

**Rationale:**
- Enables line-by-line version control and diffs
- Supports code review for XML/JSON changes
- Standard Power Platform ALM practice
- pac CLI handles packaging: `pac solution pack --zipfile output.zip --folder src/ScopeDriftMonitor`

### Flow Language (Workflow Definition Language)

**Context:** Power Automate flows can be defined in multiple formats.

**Choice:** Workflow Definition Language (JSON) - official Power Automate schema format.

**Rationale:**
- Documented at https://learn.microsoft.com/en-us/power-automate/workflow-definition-language
- Compatible with solution packaging
- Human-readable and editable as code

### Connection Parameterization

**Context:** Flows need connections to Dataverse, Outlook, Teams, HTTP, and Approvals.

**Choice:** Connection references + environment variables (5 connections, 6 variables).

**Rationale:**
- Customer selects their own connections during import
- No hardcoded credentials or connection IDs
- Environment variables enable post-deployment configuration changes

### Graceful Degradation

**Context:** Detection flow queries multiple audit sources.

**Choice:** Continue detection with reduced coverage when sources unavailable.

**Rationale:** Per CONTEXT.md decision - log warning to SourceStatus array and continue. Never fail entire detection run because one source is unavailable.

### Dual Alert Delivery

**Context:** How to notify stakeholders of violations.

**Choice:** Both Teams Adaptive Card and email for each violation.

**Rationale:** Per CONTEXT.md decision for alert behavior. Recipients are agent owner + Security team distribution list.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all files created and validated successfully.

## Technical Implementation Notes

### Dataverse Schema (Customizations.xml)

4 tables defined with full attribute specifications:

| Table | Attributes | Choice Fields | Relationships |
|-------|-----------|---------------|---------------|
| fsi_agentscope | 16 | zone (3), status (5) | Parent of scopeitem, scopeviolation, expansionrequest |
| fsi_scopeitem | 12 | itemtype (7), accesslevel (3) | Child of agentscope |
| fsi_scopeviolation | 15 | violationtype (6), severity (4), status (6), resolutiontype (5) | Child of agentscope, parent of expansionrequest |
| fsi_expansionrequest | 17 | requesttype (5), status (6), approval (4 x2) | Child of agentscope and scopeviolation |

All relationships use RemoveLink cascade behavior (preserves orphaned records for audit).

### SDM-DriftDetector Flow

**Trigger:** Recurrence every 15 minutes (UTC)

**Detection sequence:**
1. Initialize variables (LastCheckTime, SourceStatus, ViolationsFound, AuditEvents)
2. List active agent scopes (fsi_status eq 2)
3. Scope: Query Unified Audit Log via Office 365 Management API (`manage.office.com`)
4. Filter CopilotInteraction events (RecordType=261)
5. For each event: Match to scope, check accessed resources against allowed lists
6. Create violations with appropriate type and severity:
   - Connector: severity=High (2), type=1
   - SharePoint Site: severity=Medium (3), type=2
   - External API: severity=High (2), type=4
   - No Baseline: severity=High (2), type=6
7. Compose detection summary with source status and violation count

**Graceful degradation:** UAL_Error_Handler runs on Failed/TimedOut, appends unavailable status, flow continues.

### SDM-AlertDispatcher Flow

**Trigger:** When fsi_scopeviolation row is added (Dataverse webhook)

**Alert sequence:**
1. Get violation details with expanded agentscope and owner
2. Compute labels (severity, violation type, zone)
3. Build Adaptive Card with FactSet and action buttons
4. Post to Teams channel (environment variable for channel/group IDs)
5. Build HTML email body with styled table
6. Send email to agent owner + security team
7. Update violation status to Under Investigation (2)

**Dual delivery:** Email sends even if Teams posting fails (parallel failure paths).

## Verification Results

All verification checks passed:

1. Solution source directory structure exists at src/ScopeDriftMonitor/ with 7 files
2. All 3 XML and 4 JSON files pass syntax validation
3. Solution.xml has version 1.1.0 with FSIAgentGov publisher
4. Customizations.xml defines all 4 Dataverse tables (fsi_agentscope, fsi_scopeitem, fsi_scopeviolation, fsi_expansionrequest)
5. SDM-DriftDetector.json implements 15-minute scheduled detection with manage.office.com reference
6. SDM-AlertDispatcher.json implements Dataverse trigger on fsi_scopeviolation with AdaptiveCard
7. Connection references (5) and environment variables (6) all use fsi_ prefix

## Next Phase Readiness

### For Phase 05 Plan 03 (Deployment Documentation)

**Provided:**
- Complete solution source ready for `pac solution pack`
- Dataverse schema matches docs/dataverse-schema.md
- Flows implement detection and alerting per CONTEXT.md decisions
- Parameterization allows customer configuration during import

**Documentation needed:**
- Deployment guide (pac CLI commands, import steps)
- Connection configuration steps
- Environment variable setup
- Flow testing procedures
- Prerequisites (E5 Compliance for CopilotInteraction events)

### For Phase 05 Plan 04 (Testing & Final Verification)

**Testable artifacts:**
- Solution can be imported to test environment
- Detection flow can be manually triggered
- Alert flow triggers on violation creation
- Connection references can be validated
- Environment variables can be configured

---

*Phase: 05-scope-drift-monitor-completion*
*Plan: 02*
*Completed: 2026-02-05*
