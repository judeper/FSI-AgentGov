# Plan 03-02 Summary: Alert & Orchestration Layer

**Phase:** 03 - Automation and Alerting v6
**Plan:** 02/03
**Wave:** 2
**Status:** Complete
**Executed:** 2025-07-17

## Dependency Graph

```
Plan 03-01 (Core Scripts) ──► Plan 03-02 (Alert & Orchestration) ──► Plan 03-03 (Integration & QA)
       ✅ Complete                      ✅ Complete                         ⬜ Not Started
```

## Deliverables

| # | Task | File | Status |
|---|------|------|--------|
| 1 | Adaptive card for Teams alerts | `agent-access-monitor/src/adaptive-card-access-alert.json` | ✅ Created |
| 2 | Power Automate flow definition | `agent-access-monitor/src/access-validation-flow.json` | ✅ Created |
| 3 | Flow setup documentation | `agent-access-monitor/docs/FLOW_SETUP.md` | ✅ Created |

## Commit

| Hash | Message | Files |
|------|---------|-------|
| `25b29d6` | feat(aam): add automation flow, adaptive card, and setup guide | 3 files, 1244 insertions |

## Technical Decisions

### Adaptive Card Design (adaptive-card-access-alert.json)

- **Schema version:** 1.4 (minimum for ColumnSet styling used)
- **Sections:** Header with severity accent, run summary, zone summary (3 zones), violations table, drift detection table, action buttons
- **Placeholder convention:** `${VariableName}` matching flow variable names
- **Zone colors:** Zone 1 = Good (green), Zone 2 = Accent (blue), Zone 3 = Attention (red)
- **Action buttons:** "View Full Report" and "Open Admin Center" with configurable URLs

### Flow Architecture (access-validation-flow.json)

- **Trigger:** Daily Recurrence at 6:00 AM UTC
- **Pattern:** Scope_Try / Scope_Catch (learned from SSC solution)
- **Audit-before-alert:** `Write_Validation_History` runs BEFORE `Check_Alert_Required` to help ensure audit trail exists even if alerting fails. This is a gap fix identified from SSC Phase 7 lessons.
- **runAfter resilience:** `Check_Alert_Required` has `runAfter: ["Succeeded", "Failed"]` on Write_Validation_History, so alerting proceeds even if Dataverse write fails
- **10 Initialize_Variable actions** for all configurable parameters (no hardcoded values in actions)
- **Alert routing:** Critical/Failed/Error → Teams card + email (High importance); High/Warning → email only (Normal importance)
- **Connection references:** azureautomation, teams, office365 (matching AAM solution schema)
- **Parse_Results schema** matches runbook output: RunType, Timestamp, TotalEnvironments, OverallStatus, Reason, ZoneSummary, Violations[], Drift[], AlertRequired, AlertSeverity

### FLOW_SETUP.md Design

- **Follows SSC FLOW_SETUP.md pattern** but adapted for AAM-specific:
  - Different runbook name (`Start-AccessValidationRunbook`)
  - Different connection references (`fsi_cr_*_accessmonitor`)
  - No Zone variable (AAM scans all zones automatically)
  - Added baseline capture section (Step 7) — unique to AAM
  - Added Validation History Write section (Step 4) — documents Dataverse write troubleshooting
- **Alert routing summary table** provides quick reference for severity-to-channel mapping
- **Troubleshooting section** covers: Azure Automation job failures, Teams channel issues, JSON schema mismatches, Dataverse write errors, flow-level errors

## Validation

- Both JSON files validated with `ConvertFrom-Json` — parsed without errors
- FLOW_SETUP.md follows FSI language rules (no overclaim language)
- All placeholder variable names consistent across card, flow, and setup doc

## Notes

- Flow definition uses Power Automate schema but is designed for import — actual connection binding happens during deployment
- The adaptive card uses Adaptive Cards schema 1.4; older Teams clients may not render all styling features
- Dataverse entity set name `fsi_accessvalidationhistorys` uses the standard OData pluralization
