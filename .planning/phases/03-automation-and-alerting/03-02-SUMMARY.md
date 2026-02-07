---
phase: 03-automation-and-alerting
plan: 02
subsystem: session-security-configurator
tags: [power-automate, adaptive-cards, teams, azure-automation, alerting]

# Dependency graph
requires:
  - phase-03-plan-01: "Start-SessionValidationRunbook.ps1 JSON output schema (9 properties)"
  - phase-02-plans: [02-01, 02-02]
    provides: "Dataverse schema (ValidationHistory, SessionBaseline), connection references"
provides:
  - artifact: adaptive-card-session-alert.json
    capability: "Teams adaptive card template for session security drift alerts with SSC validators"
  - artifact: session-validation-flow.json
    capability: "Power Automate daily validation orchestrator with drift-based alert routing"
  - artifact: FLOW_SETUP.md
    capability: "Complete flow deployment guide with multi-zone patterns and troubleshooting"
affects:
  - phase-03-plan-03: "Flow provides alerting foundation for notification enhancements"
  - phase-04: "Documentation may reference flow setup for production deployment"

# Tech tracking
tech-stack:
  added: [adaptive-cards-1.4, logic-apps-workflow-2016-06-01]
  patterns: [daily-recurrence-trigger, scope-try-catch-error-handling, severity-based-alert-routing, inline-adaptive-card-json]

key-files:
  created:
    - session-security-configurator/src/adaptive-card-session-alert.json
    - session-security-configurator/src/session-validation-flow.json
    - session-security-configurator/docs/FLOW_SETUP.md
  modified: []

decisions:
  - id: INLINE-CARD-JSON
    decision: "Embed adaptive card JSON inline in flow with nested replace() calls"
    rationale: "Power Automate teams connector requires inline card content. Separate template file would need custom parser. ACV pattern proven reliable with 11 replace() calls."
    alternatives: ["Store card in Dataverse and retrieve", "Use Power Automate variables for each field"]
    trade-offs: "Long replace() chain (harder to read) vs runtime flexibility and no external dependencies"
  - id: SEVERITY-ROUTING
    decision: "Teams card posted only for Failed/Error severity; email sent for all drift alerts"
    rationale: "Teams cards are high-visibility interruptions. Reserve for critical failures. Email provides permanent audit trail for all drift events including Warning severity."
    alternatives: ["Post card for all drift", "Email only (no Teams)"]
    trade-offs: "Operators may miss Warning drift vs alert noise for every minor drift"
  - id: CONFIGPATH-PARAMETER
    decision: "Add ConfigPath parameter to runbook job invocation (tenant-config.json)"
    rationale: "SSC runbook accepts optional ConfigPath for tenant-specific configuration overrides. Not used in daily validation (defaults work) but enables flexibility for multi-tenant deployments."
    alternatives: ["Omit ConfigPath entirely", "Hard-code in runbook"]
    trade-offs: "Extra parameter (unused in typical deployment) vs future extensibility"

patterns-established:
  - "Adaptive card placeholders use ${variableName} convention replaceable by Power Automate replace() function"
  - "Parse JSON schema matches runbook output structure exactly (9 properties: RunType, Timestamp, Zone, OverallStatus, Reason, Validators, Drift, AlertRequired, AlertSeverity)"
  - "Alert routing logic: Check AlertRequired flag first, then Check_Severity_For_Teams for Teams card vs email-only"
  - "Scope_Try/Scope_Catch pattern for error handling with CRITICAL email notification when flow execution fails"
  - "Variable initialization chained sequentially via runAfter for deterministic execution order"

# Metrics
duration: 4min
completed: 2026-02-07
commits: 2
files-created: 3
lines-added: 1049
---

# Phase 3 Plan 2: Daily Validation Flow and Adaptive Card Summary

**Power Automate daily orchestrator (6 AM UTC) with Teams adaptive card alerts for Failed/Error drift, email routing for all severities, and complete multi-zone deployment guide**

## Performance

- **Duration:** 4 minutes
- **Started:** 2026-02-07T03:32:58Z
- **Completed:** 2026-02-07T03:37:40Z
- **Tasks:** 2
- **Files created:** 3

## Accomplishments

- **adaptive-card-session-alert.json** — Adaptive Card v1.4 template with 12 placeholders for drift details, SSC-specific validator status (Session Controls, Auth Strength, PIM Settings, Break-Glass), and action buttons
- **session-validation-flow.json** — Complete Power Automate flow definition with daily Recurrence trigger (6 AM UTC), 10 variable initializations, Scope_Try/Scope_Catch error handling, Azure Automation job execution, Parse JSON with SSC schema, and severity-based alert routing
- **FLOW_SETUP.md** — Comprehensive 364-line deployment guide with step-by-step import instructions, variable configuration table, multi-zone deployment patterns, alert routing summary, and 8 troubleshooting scenarios

## Task Commits

Each task was committed atomically to FSI-AgentGov-Solutions repo:

1. **Task 1: Create adaptive-card-session-alert.json and session-validation-flow.json** - `99b3f61` (feat)
2. **Task 2: Create FLOW_SETUP.md guide** - `a7908a3` (docs)

## Files Created/Modified

**Created:**
- `session-security-configurator/src/adaptive-card-session-alert.json` (140 lines) — Teams adaptive card with SSC validators and 12 placeholders
- `session-security-configurator/src/session-validation-flow.json` (545 lines) — Power Automate flow with Logic Apps workflow schema
- `session-security-configurator/docs/FLOW_SETUP.md` (364 lines) — Flow deployment and configuration guide

**Modified:** None

## Decisions Made

### 1. Inline Adaptive Card JSON (INLINE-CARD-JSON)

**Decision:** Embed the adaptive card JSON inline in the Post_Teams_Card action with nested replace() calls for all 12 placeholders.

**Rationale:**
- Power Automate Teams connector requires inline card content (not file reference)
- ACV v4 demonstrated this pattern works reliably with 11 replace() calls
- Separate template file would require custom parser or HTTP action to retrieve
- Single-file flow definition simplifies import/export

**Implementation:**
- Adaptive card JSON minified to single-line string
- 11 nested replace() functions substitute placeholders:
  - `${overallStatus}` → `body('Parse_Results')?['OverallStatus']`
  - `${timestamp}` → `body('Parse_Results')?['Timestamp']`
  - `${zone}` → `body('Parse_Results')?['Zone']`
  - `${baselineStatus}` → `body('Parse_Results')?['Drift']?['BaselineStatus']`
  - `${currentStatus}` → `body('Parse_Results')?['Drift']?['CurrentStatus']`
  - `${baselineDate}` → `body('Parse_Results')?['Drift']?['BaselineDate']`
  - `${reason}` → `body('Parse_Results')?['Reason']`
  - `${sessionControlsStatus}` → `body('Parse_Results')?['Validators']?['SessionControls']?['Status']`
  - `${authStrengthStatus}` → `body('Parse_Results')?['Validators']?['AuthStrength']?['Status']`
  - `${pimStatus}` → `body('Parse_Results')?['Validators']?['PimRoleSettings']?['Status']`
  - `${breakGlassStatus}` → `body('Parse_Results')?['Validators']?['BreakGlass']?['Status']`
  - `${validationHistoryUrl}` → `concat(variables('DataverseUrl'), '/main.aspx')`

**Alternatives considered:**
- Store card template in Dataverse and retrieve via HTTP action (rejected: adds external dependency, requires Dataverse query permissions)
- Use Power Automate variables for each field (rejected: 12 Initialize Variable actions adds clutter, harder to maintain)

**Trade-offs:**
- Long replace() chain is harder to read and edit
- Runtime flexibility (no compilation step, operators can edit directly in flow designer)
- No external dependencies (flow is self-contained)

### 2. Severity-Based Alert Routing (SEVERITY-ROUTING)

**Decision:** Post Teams adaptive card only for Failed/Error severity. Send email for all drift alerts (Failed, Error, Warning).

**Rationale:**
- Teams cards are high-visibility interruptions posted to shared channel
- Reserve Teams for critical failures that require immediate attention
- Email provides permanent audit trail and distribution list notifications
- Warning severity drift may indicate gradual degradation (still needs tracking)

**Implementation:**
- `Check_Alert_Required` condition: `AlertRequired == true`
- `Check_Severity_For_Teams` nested condition: `OverallStatus == "Failed" OR "Error"`
- If true: Post_Teams_Card + Send_Alert_Email (after Teams action completes)
- If false (Warning): Send_Alert_Email only
- Email importance: High for Failed/Error, Normal for Warning

**Alternatives considered:**
- Post card for all drift (rejected: alert noise, Teams channel overwhelmed with minor drift)
- Email only, no Teams (rejected: critical failures need immediate visibility)
- Separate Teams channels by severity (rejected: over-engineering for single-zone deployment)

**Trade-offs:**
- Operators may miss Warning severity drift if they don't monitor email regularly
- Balances alert noise reduction vs ensuring critical failures get immediate attention
- Email distribution list provides audit trail and broader notification reach

### 3. ConfigPath Parameter (CONFIGPATH-PARAMETER)

**Decision:** Include ConfigPath parameter in Azure Automation job invocation with default value "tenant-config.json".

**Rationale:**
- Start-SessionValidationRunbook.ps1 accepts optional ConfigPath for tenant-specific overrides
- Not actively used in typical deployments (runbook defaults work)
- Enables future multi-tenant scenarios where each tenant has custom baseline thresholds
- ACV includes similar parameter for environment-specific configs

**Implementation:**
- Create_Automation_Job body includes: `"ConfigPath": "tenant-config.json"`
- Runbook treats this as optional override file (not required to exist)
- Flow doesn't expose ConfigPath as variable (uses static default)

**Alternatives considered:**
- Omit ConfigPath entirely (rejected: removes flexibility for future use cases)
- Make ConfigPath a flow variable (rejected: adds complexity for unused feature)

**Trade-offs:**
- Extra parameter that's unused in 99% of deployments
- Future-proofs for multi-tenant or custom baseline scenarios
- Matches ACV pattern for consistency

## Deviations from Plan

None — plan executed exactly as written.

## Verification Results

All verification checks passed:

1. ✅ adaptive-card-session-alert.json is valid JSON
2. ✅ Adaptive Card schema version 1.4
3. ✅ 12 placeholders found: overallStatus, timestamp, zone, baselineStatus, currentStatus, baselineDate, reason, sessionControlsStatus, authStrengthStatus, pimStatus, breakGlassStatus, validationHistoryUrl
4. ✅ SSC validators in card: Session Controls, Auth Strength, PIM Settings, Break-Glass
5. ✅ session-validation-flow.json is valid JSON
6. ✅ Logic Apps workflow schema 2016-06-01
7. ✅ Recurrence trigger: Daily at 6:00 AM UTC
8. ✅ 10 Initialize Variable actions (sequential runAfter chain)
9. ✅ Runbook name: Start-SessionValidationRunbook (NOT ACV's Start-TenantValidationRunbook)
10. ✅ ConfigPath parameter present in job body
11. ✅ Parse JSON schema matches SSC validators: SessionControls, AuthStrength, PimRoleSettings, BreakGlass
12. ✅ Drift structure is flat (DriftDetected, CurrentStatus, BaselineStatus, BaselineDate, IsFirstRun)
13. ✅ Check_Alert_Required routes on AlertRequired boolean
14. ✅ Check_Severity_For_Teams posts card for Failed/Error only
15. ✅ Scope_Catch sends CRITICAL error email on flow failure
16. ✅ FLOW_SETUP.md has all 10 required sections
17. ✅ Variable table has 10 variables with descriptions
18. ✅ References Start-SessionValidationRunbook.ps1 and Invoke-BaselineCapture.ps1
19. ✅ Alert routing summary table present
20. ✅ Multi-zone deployment guidance (three flow instances, staggered schedules)

## Integration Points

### Upstream Dependencies (Phase 3 Plan 1)

- **Start-SessionValidationRunbook.ps1**: Flow executes this runbook daily via Azure Automation Create Job action
- **JSON output schema**: Parse_Results schema matches 9-property output (RunType, Timestamp, Zone, OverallStatus, Reason, Validators, Drift, AlertRequired, AlertSeverity)
- **AlertRequired flag**: Simple boolean for alert routing decision (no complex drift logic in flow)

### Downstream Dependencies (This Phase)

- **Plan 03-03**: May add notification enhancements (Dataverse DriftViolation writes, compliance report generation)

### Cross-Solution Integration

- **ACV (v4)**: Flow structure follows proven tenant-validation-flow.json pattern
- **ACV (v4)**: Adaptive card layout mirrors adaptive-card-tenant-alert.json (attention style, FactSet sections, action buttons)
- **Connection references**: Reuses fsi_cr_ naming convention established in Phase 2

## Next Phase Readiness

**Phase 3 Plan 3 can proceed** — Alerting infrastructure complete.

**Readiness checklist:**
- ✅ Adaptive card template ready for Teams notifications
- ✅ Flow JSON ready for Power Automate import
- ✅ Alert routing logic implemented (severity-based)
- ✅ Deployment guide complete with troubleshooting
- ✅ Multi-zone deployment pattern documented

**Blockers:** None

**Concerns:** None

**Recommendations for next plan:**

1. Consider adding Dataverse DriftViolation record creation when drift detected (for historical tracking beyond ValidationHistory)
2. Daily validation flow could trigger remediation workflows for non-Zone-3 environments (Zone 1/2 auto-remediation allowed)
3. Compliance report aggregation (weekly summary email with trend analysis)
4. Integration with ELM solution for environment lifecycle events

## Usage Patterns

### Flow Import and Configuration

```powershell
# 1. Navigate to Power Automate
https://make.powerautomate.com

# 2. Select target environment (same as Dataverse schema deployment)

# 3. Import flow JSON
My flows > Import > Import Package (Legacy)
Upload: session-validation-flow.json

# 4. Map connection references
Azure Automation → Select existing connection
Microsoft Teams → fsi_cr_teams_sessionvalidation
Office 365 Outlook → fsi_cr_office365_sessionvalidation

# 5. Update variables (see FLOW_SETUP.md Step 2 for details)
DataverseUrl: https://your-org.crm.dynamics.com
TenantId: your-tenant.onmicrosoft.com
ClientId: your-client-id
CertificateThumbprint: your-cert-thumbprint
SubscriptionId: your-subscription-id
ResourceGroup: rg-session-validation
AutomationAccount: aa-session-validator
TeamsChannelId: 19:xxxx... (get from Teams channel link)
ComplianceDistributionList: alerts@your-org.com
Zone: Zone3

# 6. Test manually
Test > Manually > Test

# 7. Enable daily schedule
Automatically enabled after successful test (runs at 6:00 AM UTC)
```

### Multi-Zone Deployment

```powershell
# Create three flow instances for all zones

# Zone 1 flow
Name: SSC - Session Validation Zone1 (Daily)
Zone variable: Zone1
Schedule: 6:00 AM UTC

# Zone 2 flow
Name: SSC - Session Validation Zone2 (Daily)
Zone variable: Zone2
Schedule: 6:15 AM UTC (stagger to avoid load spike)

# Zone 3 flow
Name: SSC - Session Validation Zone3 (Daily)
Zone variable: Zone3
Schedule: 6:30 AM UTC (stagger to avoid load spike)

# Optional: Zone-specific Teams channels
Create channels: #session-security-zone1, #session-security-zone2, #session-security-zone3
Update TeamsChannelId variable in each flow
```

### Baseline Capture (Required Before First Run)

```powershell
# After flow is deployed, capture initial baseline
.\Invoke-BaselineCapture.ps1 `
    -Zone Zone3 `
    -DataverseUrl "https://your-org.crm.dynamics.com" `
    -TenantId "your-tenant.onmicrosoft.com" `
    -ClientId "your-client-id" `
    -CertificateThumbprint "your-cert-thumbprint" `
    -Interactive

# Output includes BaselineId (stored in Dataverse fsi_sessionbaselines table)
# Drift detection compares daily runs to this baseline
```

## Repository Context

**Solution repository:** FSI-AgentGov-Solutions
**Commits:** 99b3f61, a7908a3 (committed to FSI-AgentGov-Solutions)
**Documentation repository:** FSI-AgentGov
**Planning docs:** .planning/phases/03-automation-and-alerting/

## Self-Check: PASSED

All verification checks passed:
- ✅ adaptive-card-session-alert.json exists on disk
- ✅ session-validation-flow.json exists on disk
- ✅ FLOW_SETUP.md exists on disk
- ✅ Commit 99b3f61 exists in git log
- ✅ Commit a7908a3 exists in git log
