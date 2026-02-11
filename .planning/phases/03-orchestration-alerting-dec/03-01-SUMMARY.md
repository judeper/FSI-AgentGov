---
phase: 3
plan: 1
title: "DEC-DailyOrchestrator Power Automate flow definition and setup guide"
status: complete
completed: 2026-02-10
files_created:
  - path: maintainers-local/solutions-staging/deny-event-correlation-report/templates/dec-daily-orchestrator-flow.json
    lines: 957
    description: Power Automate cloud flow definition JSON for DEC-DailyOrchestrator
  - path: maintainers-local/solutions-staging/deny-event-correlation-report/docs/FLOW_SETUP.md
    lines: 445
    description: Administrator guide for importing, configuring, and verifying the flow
files_modified: []
---

# Plan 03-01 Summary: DEC-DailyOrchestrator Power Automate Flow Definition

## Completed

### Task 1: dec-daily-orchestrator-flow.json (957 lines)

Power Automate cloud flow definition with:

- **Trigger:** Recurrence — daily at 06:00 UTC
- **Variables:** varRunId (guid), varTimestamp (ISO 8601), varAlertRequired (boolean), varJobStatus (string), varPollCount (integer)
- **Scope_Try:**
  - Creates Azure Automation job targeting `Invoke-DailyDenyReport` runbook with parameters: TenantId, ClientId, KeyVaultName, AppInsightsAppId, WriteToDataverse=true, DaysBack=1
  - Do Until loop: polls job status every 60 seconds, max 30 iterations / 30-minute timeout
  - On Completed: Get Job Output → Parse JSON (schema matches Invoke-DailyDenyReport return object including nested AlertResult) → Write fsi_denyvalidationhistory (audit-first, type=DailyOrchestration) → If alerts generated: ForEach alert → Switch on Severity (Critical → Teams + Email, High → Teams + Email, Warning → Email only, Info → log only with Compose action)
  - On Failed: Get error stream → Send CRITICAL email → Write fsi_denyvalidationhistory (JobFailure)
  - Timeout check: If varPollCount ≥ 30 and job not completed → CRITICAL email
- **Scope_Catch** (runAfter: Scope_Try [Failed, TimedOut]):
  - Send CRITICAL email with Scope_Try result details
  - Write fsi_denyvalidationhistory (type=FlowFailure)
- **Connection references:** All 3 DEC connection references used (Dataverse, Office 365, Teams)
- **Parameters:** 11 configurable parameters including Azure subscription/RG/Automation account, DEC credentials, Teams IDs, alert recipient email
- **JSON validated:** ConvertFrom-Json succeeds without errors

### Task 2: FLOW_SETUP.md (445 lines)

Administrator setup guide with 6 sections:

1. **Prerequisites** — Licenses (Power Automate Premium, Azure subscription, Dataverse, Teams, Exchange Online), Azure Automation requirements (PS 7.x, modules, runbook), identity/credentials, connection references, Teams configuration
2. **Import Flow** — 3-step process: prepare package, import into Power Automate with connection mapping, configure 11 flow parameters
3. **Configure Environment Variables** — TeamsGroupId, TeamsChannelId, AnomalyThresholdSigma, ScanFrequencyHours; includes instructions for finding Teams group/channel IDs
4. **Azure Automation Setup** — 5 steps: create account, configure managed identity permissions, install modules (Az.Accounts, Az.KeyVault, ExchangeOnlineManagement, DECClient), upload runbook and scripts, test independently
5. **Verify** — 5 verification checks: manual trigger, Dataverse validation history, Teams card, email notification, enable scheduled trigger
6. **Troubleshooting** — 7 scenarios: job timeout, connection errors, no alerts, Teams errors, email failures, Scope_Catch triggered, module import failures

Architecture reference appendix includes flow execution sequence diagram, alert severity routing table, and connection reference mapping.

FSI language validated — no instances of "ensures compliance", "guarantees", "will prevent", or "eliminates risk". Uses hedged language throughout ("supports compliance evidence collection", "organizations should validate", "no automation tool can guarantee compliance").

## Acceptance Criteria

- [x] dec-daily-orchestrator-flow.json is valid parseable JSON
- [x] Flow triggers daily at 06:00 UTC via Recurrence
- [x] Flow invokes Invoke-DailyDenyReport.ps1 via Azure Automation with -WriteToDataverse
- [x] Flow parses structured output with schema matching actual return object
- [x] Audit-first pattern: validation history written before alert routing
- [x] Routes Critical/High alerts to Teams + email
- [x] Routes Warning alerts to email only
- [x] Info alerts logged in Dataverse only (no notification)
- [x] Scope_Try/Scope_Catch error handling with CRITICAL email on failure
- [x] Timeout handler (30 min / 30 polls) with CRITICAL email
- [x] Uses all 3 connection references defined in baseline JSON
- [x] FLOW_SETUP.md covers prerequisites, import, config, verification, troubleshooting
- [x] FSI hedged language — no overclaims

## Deviations from Plan

1. **Added varPollCount variable** — Not in original plan but needed for timeout detection (track polling iterations to identify 30-minute timeout condition)
2. **Added varJobStatus variable** — Needed to track Do Until exit condition and reuse in Condition_Job_Completed
3. **Added DEC_AlertRecipientEmail parameter** — Plan specified email sending but didn't define the recipient parameter; added as a configurable flow parameter
4. **Added Condition_Timeout_Check** — Plan mentioned "timeout handler" but didn't specify implementation; added as explicit condition after Condition_Job_Completed checking varPollCount ≥ 30
5. **Added JobFailure Dataverse record** — Plan specified audit-first for success path; added matching validation history record for job failure path (consistent audit trail)

## Blockers

None.

---

*Completed: 2026-02-10 | Phase 3, Plan 1 of 3*
