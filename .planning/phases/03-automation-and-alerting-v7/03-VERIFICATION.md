# Phase 3 Verification: Automation and Alerting

## Verification Status: PASSED

## Goal Assessment

**Goal:** Content moderation violations are automatically detected daily and operators receive classified alerts when agent moderation settings deviate from zone requirements

**→ DELIVERED.** The solution provides a complete automation pipeline: a Power Automate flow triggers daily at 06:00 UTC, executes an Azure Automation runbook that scans all agents across all zones, compares current moderation levels against baselines for drift detection, writes immutable validation history to Dataverse, and routes severity-classified alerts to Teams (Critical/Failed/Error) and email (all alert-worthy results).

## Success Criteria Verification

### SC-1: Daily Power Automate flow runs daily moderation validation

- **Evidence:** `content-moderation-monitor/src/moderation-validation-flow.json` — `Recurrence` trigger with `frequency: Day`, `interval: 1`, `hours: [6]`, `minutes: [0]`, `timeZone: UTC`
- **Flow chain:** `Create_Automation_Job` (runs `Start-ModerationValidationRunbook`) → `Wait_For_Job` (30s poll, 2h max) → `Get_Job_Output` → `Parse_Results` (typed JSON schema with 24 properties) → `Write_Validation_History` (Dataverse POST to `fsi_moderationvalidationhistory`) → `Check_Alert_Required` → conditional alerting
- **Runbook:** `content-moderation-monitor/scripts/Start-ModerationValidationRunbook.ps1` (537 lines) — certificate-based auth, dot-sources `Test-ContentModerationCompliance`, scans all zones with `-IncludeCompliant $true`, builds ZoneSummary, classifies violations by severity, emits structured JSON
- **Immutable write sequencing:** `Write_Validation_History` runs after `Parse_Results [Succeeded]`; `Check_Alert_Required` runs after `Write_Validation_History [Succeeded, Failed]` — audit trail written before alert routing
- **Status: PASS**

### SC-2: Teams adaptive card alerts with severity classification

- **Evidence:** `content-moderation-monitor/src/adaptive-card-moderation-alert.json` (366 lines) — full template with AlertSeverity, Timestamp, OverallStatus, TotalAgents, TotalEnvironments, Reason, per-zone summary (Z1/Z2/Z3 Compliant/Total), violation details (AgentName, EnvironmentName, Zone, Expected/Actual moderation, Severity, RegulatoryContext), drift details (DriftedAgents, Direction, BaselineLevel, CurrentLevel)
- **Severity routing in flow:** `Check_Severity_For_Teams` — Critical/Failed/Error → `Post_Teams_Card` + `Send_Alert_Email` (High importance); High/Warning → `Send_Alert_Email` only (Normal importance); Passed → no alert
- **Severity classification in runbook:** AlertSeverity derived from highest violation severity (Critical > High > Warning > Info); Zone 3 weakened drift automatically escalates to Critical
- **Inline card in flow:** Simplified summary card posted via `@replace()` chain substituting `${AlertSeverity}`, `${Timestamp}`, `${OverallStatus}`, `${TotalAgents}`, `${TotalEnvironments}`, `${Reason}` placeholders; full template available in `adaptive-card-moderation-alert.json` for customization
- **Status: PASS**

### SC-3: Baseline capture and comparison with violation detection

- **Evidence:**
  - `content-moderation-monitor/scripts/Invoke-ModerationBaselineCapture.ps1` (412 lines) — operator-initiated capture, queries live agent moderation settings via `Get-AgentModerationSettings`, writes per-agent baselines to Dataverse, supports zone/environment/agent filtering, WhatIf mode, interactive and certificate auth
  - `content-moderation-monitor/scripts/private/CMMClient.psm1` — `Save-CMMBaseline` deactivates previous active baseline (`fsi_is_active = false`) before creating new one; `Get-ModerationBaseline -ActiveOnly` batch-queries all active baselines with OData paging
  - `Start-ModerationValidationRunbook.ps1` lines 300-380 — batch baseline query → hashtable construction → per-agent O(1) drift lookup → `Get-ModerationDriftDirection` classification (Weakened if currentRank > baselineRank, Strengthened if <, Changed if unknown rank)
- **Edge cases handled:** No baseline → `IsFirstRun = true`; baseline query failure → `$baselineQueryFailed = true` → fail open; all first run → `HasDrift = false`
- **Status: PASS**

### SC-4: Immutable validation history in Dataverse

- **Evidence:**
  - Flow `Write_Validation_History` action POSTs to `fsi_moderationvalidationhistory` with 8 columns: `fsi_name`, `fsi_run_id` (guid), `fsi_overall_status`, `fsi_violation_count`, `fsi_total_agents`, `fsi_environments_scanned`, `fsi_summary_json` (full JSON output), `fsi_validation_time`
  - Column names verified against `create_dataverse_schema.py` — 5 mismatches found and fixed in Plan 03-03 (`fsi_runid` → `fsi_run_id`, `fsi_overallstatus` → `fsi_overall_status`, etc.)
  - Write action runs for ALL scans (not just failures) — audit trail is comprehensive
  - Dataverse table is OrganizationOwned (immutable by design, no user-level delete)
  - CMMClient.psm1 `Write-ModerationValidationHistory` provides PowerShell-side persist capability
- **Status: PASS**

## Requirement Coverage

| Requirement | Status | Evidence |
|---|---|---|
| DDA-01: Detect content moderation setting drift | COVERED | `Start-ModerationValidationRunbook.ps1` — per-agent drift detection via `Get-ModerationDriftDirection` (Weakened/Strengthened/Changed/Unchanged), batch baseline query from `Get-ModerationBaseline -ActiveOnly`, hashtable O(1) lookup |
| DDA-02: Teams adaptive card alerts with severity | COVERED | `adaptive-card-moderation-alert.json` (full template), flow `Post_Teams_Card` with inline card, severity routing (Critical→Teams+email, High→email), Zone 3 weakened→Critical escalation |
| DDA-03: Dataverse immutable validation history | COVERED | Flow `Write_Validation_History` → `fsi_moderationvalidationhistory` POST with 8 columns, runs before alerting, all scans persisted |
| DDA-04: Baseline capture and comparison | COVERED | `Invoke-ModerationBaselineCapture.ps1` captures baselines per agent; `Save-CMMBaseline` manages active baseline lifecycle (deactivate old, create new); `Get-ModerationBaseline -ActiveOnly` enables batch comparison |
| INF-04: Power Automate scheduled daily scan flow | COVERED | `moderation-validation-flow.json` — Recurrence trigger (Day/1/06:00 UTC), Azure Automation connector, Scope_Try/Scope_Catch error handling, connection references for Dataverse/Teams/Office365 |

## Build Validation

- **mkdocs build --strict:** PASS — Built in 30.55 seconds, INFO-level messages about excluded file links only (not errors)
- **verify_controls.py:** PASS — 62 controls found in index, 62 content files in pillars, all structure and footer standards met, no broken doc anchors

## Script Validation

- **Start-ModerationValidationRunbook.ps1:** PARSE OK
- **Invoke-ModerationBaselineCapture.ps1:** PARSE OK
- **CMMClient.psm1:** PARSE OK (Version 0.3.0 confirmed)
- **moderation-validation-flow.json:** VALID JSON (ConvertFrom-Json succeeds)
- **adaptive-card-moderation-alert.json:** VALID JSON (ConvertFrom-Json succeeds)

## Plan Execution Summary

| Plan | Status | Commits | Key Deliverables |
|------|--------|---------|-----------------|
| 03-01 | Complete | `9c5ace5`, `54014a7`, `1202cb3` | Save-CMMBaseline deactivation, Get-ModerationBaseline -AgentId/-ActiveOnly, Start-ModerationValidationRunbook.ps1, Invoke-ModerationBaselineCapture.ps1 |
| 03-02 | Complete | `d414372`, `a2ec6a9`, `53a7afa` | adaptive-card-moderation-alert.json, moderation-validation-flow.json, FLOW_SETUP.md |
| 03-03 | Complete | `d64fa5a` | Fixed 5 Dataverse column names in flow/docs, CHANGELOG v0.3.0 entry, end-to-end structural verification |

## Gaps Found

None identified. All 4 success criteria are fully delivered, all 5 requirements are covered.

**Cosmetic note (non-blocking):** The inline adaptive card in the flow's `Post_Teams_Card` action is a simplified summary-only version. Zone placeholder replaces (`${Z1Total}`, `${Z1Compliant}`, etc.) are present in the replace chain but their placeholders don't appear in the simplified inline card — these are no-ops at runtime with no functional impact. The full card template in `adaptive-card-moderation-alert.json` contains all sections for organizations wanting to customize. Documented in 03-03-SUMMARY.md as discovered work.

## Discovered Risk

1. **Power Automate Premium license required** — Azure Automation connector is a premium connector; organizations without Premium licenses cannot deploy this flow as-is.
2. **Certificate lifecycle management** — Certificate-based authentication requires proactive certificate renewal before expiration; expired certificates will cause silent scan failures (mitigated by `Scope_Catch` email notification).
3. **Inline card vs. full template divergence** — The inline card in the flow is a simplified subset. If organizations modify the runbook output schema, both the inline card and the full template need updating independently.
