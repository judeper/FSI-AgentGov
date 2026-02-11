# Phase 3 Research: Orchestration & Alerting for DEC

**Phase:** 3 — Orchestration & Alerting
**Researched:** 2026-02-10
**Goal:** Automate daily deny event extraction and correlation with Power Automate orchestration and Teams alerting for high-severity patterns

## Established Orchestration Patterns (v4-v8)

### Proven 3-Plan Split for Phase 3

Every automation/alerting phase since v4 follows this pattern:

| Plan | Wave | Scope |
|------|------|-------|
| XX-03 | 1 | Severity classification, alert functions in *Client.psm1, anomaly/drift logic |
| XX-01 | 2 | Power Automate flow JSON definition, FLOW_SETUP.md |
| XX-02 | 2 | Adaptive card template JSON, Teams notification integration |

### Flow Architecture Convention

```
Daily Recurrence trigger (06:00 UTC)
  → Variable initialization (runId, timestamp, alertRequired)
  → Scope_Try
      → Create Azure Automation Job (Invoke-DailyDenyReport.ps1)
      → Poll until complete (Do Until loop)
      → Get Job Output → Parse JSON
      → Write ValidationHistory (audit-first pattern)
      → Check AlertRequired (severity evaluation)
      → Condition: AlertRequired = true
          → Route by Severity
              → Critical/Failed → Teams adaptive card + email
              → Warning → email only
              → Passed/Info → log only
  → Scope_Catch
      → Send CRITICAL error email (flow failure)
```

### DEC-Specific Architecture Differences

DEC has **3 unique characteristics** vs v4-v8 solutions:

1. **Three data sources** (App Insights, Exchange Online, Dataverse) vs single source
   - `Invoke-DailyDenyReport.ps1` already coordinates all 3 extractions + correlation
   - Flow only needs to trigger this one script, not 3 separate runbooks

2. **Anomaly detection (statistical)** vs drift detection (configuration diff)
   - v4-v8 compare current config against baseline → drift/no-drift
   - DEC computes >2σ deviation from 7-day rolling baseline → volume anomaly
   - Correlation engine already computes 7-day trend with stddev in `Invoke-DenyEventCorrelation.ps1`

3. **Alert persistence** via `fsi_denyalert` table
   - v4-v8 don't persist alert history to Dataverse (alerts are ephemeral Teams/email messages)
   - DEC has a dedicated `fsi_denyalert` table for alert audit trail
   - Supports FINRA 4511 communications retention for alert records

## Existing DEC Infrastructure (Phase 1-2 Complete)

### Scripts Already Built

| Script | Purpose | Phase |
|--------|---------|-------|
| `Invoke-DailyDenyReport.ps1` | Orchestration entrypoint — 3 extractions + correlation + blob upload | 1 (created), 2 (correlation added) |
| `Invoke-DenyEventCorrelation.ps1` | Daily correlation engine with 7-day trend and stddev | 2 |
| `Export-CopilotDenyEvents.ps1` | Purview Audit CopilotInteraction extraction | 1 |
| `Export-DlpCopilotEvents.ps1` | Purview DLP extraction | 1 |
| `Export-RaiTelemetry.ps1` | App Insights RAI extraction (Entra ID auth) | 1 |
| `Set-DECRetentionRules.ps1` | Zone-based bulk delete retention jobs | 2 |

### DECClient.psm1 Functions (15 exported)

| Function | Category |
|----------|----------|
| `Connect-DECAppInsights` | Connection |
| `Connect-DECExchangeOnline` | Connection |
| `Connect-DECServices` | Connection (master) |
| `Connect-DECDataverse` | Connection (Dataverse) |
| `Invoke-DECAppInsightsQuery` | Query |
| `Get-DECEnvironmentVariable` | Config |
| `Write-DECDenyEvent` | Dataverse write |
| `Write-DECDenyEventBatch` | Dataverse batch write |
| `Write-DECCorrelation` | Dataverse write |
| `Write-DECValidationHistory` | Dataverse audit trail |
| `Read-DECDenyEvents` | Dataverse read |
| `Read-DECCorrelations` | Dataverse read |

**Missing for Phase 3:**
- `Write-DECAlert` — persist alert records to `fsi_denyalert`
- `Read-DECAlerts` — query alert history
- `Get-DECAlertThresholds` — read anomaly thresholds from environment variables

### Dataverse Tables

| Table | Status | Notes |
|-------|--------|-------|
| `fsi_denyevent` | ✅ Deployed | Phase 2 — ingestion working |
| `fsi_denycorrelation` | ✅ Deployed | Phase 2 — correlation engine writes |
| `fsi_denyalert` | ✅ Schema defined | Phase 2 — table created but NOT populated |
| `fsi_denyvalidationhistory` | ✅ Deployed | Phase 2 — audit trail working |

### Environment Variables (Ready for Phase 3)

| Variable | Default | Phase 3 Usage |
|----------|---------|---------------|
| `fsi_DEC_AnomalyThresholdSigma` | 2.0 | Volume anomaly detection threshold |
| `fsi_DEC_TeamsGroupId` | *(blank)* | Teams alert destination group |
| `fsi_DEC_TeamsChannelId` | *(blank)* | Teams alert destination channel |
| `fsi_DEC_ScanFrequencyHours` | 24 | Flow recurrence interval |

### Connection References (Ready for Phase 3)

| Reference | Connector | Phase 3 Usage |
|-----------|-----------|---------------|
| `fsi_cr_dataverse_denyeventcorrelation` | Dataverse | Read correlations, write alerts |
| `fsi_cr_office365_denyeventcorrelation` | Office 365 | Email-based alert delivery |
| `fsi_cr_teams_denyeventcorrelation` | Teams | Adaptive card alert delivery |

## Severity Classification Design

### Cross-Solution Standard (v4-v8)

All solutions use `fsi_acv_severity` option set with values 1-5. For DEC alerting,
the mapping translates deny event characteristics to alert severity:

| Severity | Option Value | DEC Trigger | Example |
|----------|-------------|-------------|---------|
| Critical | 4 (Failed) | Zone 3 jailbreak attempt or XPIA detection | Enterprise agent processes prompt injection |
| High | 4 (Failed) | Volume anomaly (>2σ) or Zone 2 policy block | 30 deny events when baseline is 5±3 |
| Warning | 2 (Warning) | Zone 1 RAI content filter trigger | Personal agent hits content moderation |
| Info | 1 (Passed) | Routine DLP match, normal filtering | Standard DLP policy match |

**Note:** Critical and High both map to option value 4 (Failed) in the shared option set,
but are distinguished by `fsi_alert_type` values: `ZoneCritical` vs `VolumeAnomaly`.

### Alert Type Taxonomy

| Alert Type | Trigger Logic | Severity |
|------------|--------------|----------|
| `VolumeAnomaly` | Daily count > 7-day average + (threshold_sigma × stddev) | High |
| `NewAgent` | Agent ID appears in deny events for first time (no prior correlations) | High |
| `ZoneCritical` | Zone 3 deny event with filter_category = Jailbreak or XPIA | Critical |
| `RoutineDeny` | Zone 1 RAI filter or Zone 2 standard policy match | Warning/Info |

### Anomaly Detection Algorithm

```
threshold = average_7day + (sigma × stddev_7day)

For each (AgentId, Zone) correlation today:
  1. Query last 7 days of fsi_denycorrelation for same (AgentId, Zone)
  2. Compute mean and stddev of fsi_event_count
  3. If today's count > mean + (sigma * stddev):
     → Alert: VolumeAnomaly, Severity: High
  4. If no prior correlations exist for this AgentId:
     → Alert: NewAgent, Severity: High
  5. If Zone = 3 AND filter_category ∈ [Jailbreak, XPIA]:
     → Alert: ZoneCritical, Severity: Critical
```

The correlation engine (`Invoke-DenyEventCorrelation.ps1`) already computes 7-day trend
with `Average`, `StdDev`, and `Direction` — but does NOT currently evaluate alerts.
Alert evaluation should be added as a post-correlation step.

## Adaptive Card Design

### Template Variables

Based on v4-v8 patterns, the DEC adaptive card template needs:

```json
{
  "${alertType}": "VolumeAnomaly | NewAgent | ZoneCritical",
  "${severity}": "Critical | High | Warning | Info",
  "${agentId}": "Agent identifier",
  "${zone}": "Zone 1 | Zone 2 | Zone 3",
  "${eventCount}": "Today's deny event count",
  "${baselineAvg}": "7-day average",
  "${baselineStdDev}": "7-day standard deviation",
  "${deviationSigma}": "How many σ above baseline",
  "${trendDirection}": "Increasing | Decreasing | Stable",
  "${topDenyReasons}": "Most common filter reasons",
  "${timestamp}": "Alert generation time",
  "${dashboardUrl}": "Link to Compliance Dashboard"
}
```

### Card Layout

```
┌─────────────────────────────────────────────────┐
│ ⚠️ DEC Alert: {alertType}          [{severity}] │
│ Agent: {agentId}   Zone: {zone}                 │
├─────────────────────────────────────────────────┤
│ Daily Summary                                    │
│   Events today: {eventCount}                    │
│   7-day average: {baselineAvg} ± {stdDev}       │
│   Deviation: {deviationSigma}σ above baseline   │
│   Trend: {trendDirection}                       │
├─────────────────────────────────────────────────┤
│ Top Deny Reasons                                 │
│   1. {reason1} (n events)                       │
│   2. {reason2} (n events)                       │
│   3. {reason3} (n events)                       │
├─────────────────────────────────────────────────┤
│ [View in Dashboard]    [Acknowledge Alert]      │
└─────────────────────────────────────────────────┘
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Azure Automation job timeout | Flow waits indefinitely | Set 30-min timeout with error reporting |
| No prior correlation data (cold start) | Anomaly detection fails on first run | Skip anomaly check when <3 days of history |
| Teams connector rate limits | Alert delivery fails for high-volume days | Batch alerts into single card per zone |
| fsi_denyalert table unbounded growth | Storage costs | Apply same zone-based retention as deny events |

## File Manifest (Phase 3 Deliverables)

### New Files

| File | Location | Purpose |
|------|----------|---------|
| `adaptive-card-deny-alert.json` | solutions-staging/.../templates/ | Adaptive card template |
| `dec-daily-orchestrator-flow.json` | solutions-staging/.../templates/ | Power Automate flow definition |
| `FLOW_SETUP.md` | solutions-staging/.../docs/ | Flow setup guide |
| `Invoke-DECAlertEvaluation.ps1` | solutions-staging/.../scripts/ | Alert evaluation engine |

### Modified Files

| File | Changes |
|------|---------|
| `DECClient.psm1` | Add Write-DECAlert, Read-DECAlerts, Get-DECAlertThresholds |
| `Invoke-DailyDenyReport.ps1` | Add alert evaluation step after correlation |
| `deny-event-baseline.json` | Add alert threshold defaults |

## Technical Approach

### Wave 1 (Foundation — Plan 03-03)
Severity classification and alert infrastructure:
- Add Write-DECAlert, Read-DECAlerts, Get-DECAlertThresholds to DECClient.psm1
- Create Invoke-DECAlertEvaluation.ps1 with anomaly detection + severity classification
- Update Invoke-DailyDenyReport.ps1 to call alert evaluation after correlation
- Update deny-event-baseline.json with alert threshold defaults

### Wave 2 (Artifacts — Plans 03-01 and 03-02, independent)
Power Automate flow and adaptive card artifacts:
- 03-01: dec-daily-orchestrator-flow.json + FLOW_SETUP.md
- 03-02: adaptive-card-deny-alert.json

---

*Researched: 2026-02-10 | Phase 3 of 5*
