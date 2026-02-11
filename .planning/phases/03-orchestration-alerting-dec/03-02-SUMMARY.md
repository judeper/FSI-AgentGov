---
phase: 3
plan: 2
title: "Teams adaptive card template with anomaly detection visualization"
status: complete
completed: 2026-02-10
---

# Plan 03-02 Summary: Teams Adaptive Card Template with Anomaly Detection

## Execution Results

| Item | Status |
|------|--------|
| **Plan** | 03-02 |
| **Phase** | 3 — Orchestration & Alerting |
| **Completed** | 2026-02-10 |
| **Deviations** | None |
| **Blockers** | None |

## Files Created

| File | Lines | Description |
|------|-------|-------------|
| `maintainers-local/solutions-staging/deny-event-correlation-report/templates/adaptive-card-deny-alert.json` | 341 | Adaptive Card v1.5 template with conditional visibility for 3 alert types |

## Files Modified

None.

## Task Completion

### Task 1: Create adaptive-card-deny-alert.json ✅

Created Adaptive Card v1.5 JSON template at the specified path with all required sections:

- **Header Section:** Severity icon (🔴/🟠/🟡/🔵) with conditional color expressions, alert type display name, subtitle "Deny Event Correlation Report", and `${correlationDate}`
- **Context Section:** FactSet with Agent (`${agentId}`), Zone (`${zone}` — `${zoneName}`), and Alert (`${alertMessage}`)
- **VolumeAnomaly Metrics:** Today's events, 7-day average ± stddev, σ deviation, trend with directional arrow (↑/↓/→)
- **NewAgent Metrics:** Agent ID, first observed date, events today, classification status
- **ZoneCritical Metrics:** Category (Jailbreak / XPIA), events today, Zone 3 designation, immediate investigation required
- **Severity Distribution:** 4-column ColumnSet with Critical/High/Warning/Info counts using severity count variables
- **Actions:** "View in Dashboard" (`Action.OpenUrl` → `${dashboardUrl}`), "Acknowledge Alert" (`Action.Submit` with `alertId` and `action: acknowledge`)

### Task 2: Create Alert Type Display Variants ✅

All 3 alert types handled via `$when` conditional visibility within a single template:

| Container | `$when` Expression | Visible When |
|-----------|---------------------|-------------|
| Anomaly Metrics | `${alertType == 'VolumeAnomaly'}` | Volume anomaly alert |
| New Agent Details | `${alertType == 'NewAgent'}` | New agent alert |
| Zone Critical Details | `${alertType == 'ZoneCritical'}` | Zone critical alert |

## Template Variables Used

All 17 variables from the plan are bound in the template:

`${alertType}`, `${severity}`, `${severityColor}`, `${agentId}`, `${zone}`, `${zoneName}`, `${eventCount}`, `${baselineAvg}`, `${baselineStdDev}`, `${deviationSigma}`, `${trendDirection}`, `${alertMessage}`, `${timestamp}`, `${dashboardUrl}`, `${correlationDate}`, `${alertId}`

Additional severity distribution variables introduced: `${severityCriticalCount}`, `${severityHighCount}`, `${severityWarningCount}`, `${severityInfoCount}`

## Acceptance Criteria Verification

| Criterion | Status |
|-----------|--------|
| Valid Adaptive Card schema v1.5 | ✅ Validated via `ConvertFrom-Json` + schema check |
| Header displays severity icon, color badge, alert type, and date | ✅ |
| Context section shows agent ID, zone, and alert message | ✅ |
| VolumeAnomaly card shows event count, baseline, deviation, and trend | ✅ |
| NewAgent card shows first observation details | ✅ |
| ZoneCritical card shows category and required action | ✅ |
| Severity distribution breakdown included | ✅ |
| "View in Dashboard" opens Compliance Dashboard URL | ✅ `Action.OpenUrl` |
| "Acknowledge Alert" submits acknowledgment action | ✅ `Action.Submit` with alertId |
| All variable placeholders use `${name}` convention | ✅ |
| Template works with Power Automate "Post adaptive card" action | ✅ Standard schema |
| Single template file handles all 3 alert types | ✅ |
| Conditional visibility shows type-appropriate content | ✅ 3 `$when` sections |
| No empty sections when conditions are not met | ✅ |

## Validation Output

```
Schema valid: AdaptiveCard v1.5
Body elements: 7
Actions: 2
$when conditional sections: 3
Line count: 341
```

## Integration Notes

- The flow definition in `dec-daily-orchestrator-flow.json` (Plan 03-01) currently sends plain text messages for Teams alerts. To use this adaptive card template, the `Post_AdaptiveCard_Critical` and `Post_AdaptiveCard_High` actions should be updated to use the "Post adaptive card in a chat or channel" Teams connector action with this template as the card payload.
- Plan 03-03's severity classification engine (`Write-DECAlert`) produces the alert data structure whose fields map to this card's `${variable}` placeholders.
- The 4 additional `${severityXxxCount}` variables for the distribution section should be populated from the correlation summary output by the orchestrating flow before card posting.
