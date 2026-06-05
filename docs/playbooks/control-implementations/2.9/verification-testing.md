# Verification & Testing: Control 2.9 - Agent Performance Monitoring and Optimization

**Last Updated:** April 2026
**Audience:** M365 administrators preparing audit-ready evidence for FINRA / SEC / OCC examinations of AI agent monitoring.

---

## How verification maps to regulatory ask

| Test | Helps demonstrate |
|---|---|
| TC-2.9-01 to TC-2.9-04 | FINRA 4511 / SEC 17a-3/4 record-keeping; FINRA RN 24-09 + Rule 3110 supervisory review |
| TC-2.9-05 to TC-2.9-07 | OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) ongoing model performance monitoring |
| TC-2.9-08 to TC-2.9-09 | SOX 404 control-effectiveness testing |
| TC-2.9-10 | GLBA 501(b) integrity of customer-information processing |

---

## Manual verification steps

### Test 1 — Native analytics data flow (TC-2.9-01)

1. Open PPAC → **Analytics** → **Microsoft Copilot Studio**.
2. Select an environment with Zone 2/3 agents.
3. Confirm sessions, resolution rate, and CSAT data for the trailing 7+ days.
4. **Expected:** non-zero sessions, recent timestamps, no banner indicating analytics is disabled.
5. **Evidence:** screenshot to `maintainers-local/tenant-evidence/2.9/`.

### Test 2 — Application Insights linkage (TC-2.9-02)

1. In Copilot Studio, open each Zone 2/3 agent → **Settings** → **Advanced** → **Application Insights**.
2. Confirm a connection string is configured.
3. In Azure Portal, run KQL: `requests | where timestamp > ago(24h) | summarize count()`.
4. **Expected:** count > 0 within 24 h. An empty result with a "configured" string is a **monitoring gap** — escalate.

### Test 3 — Power BI dashboard accuracy (TC-2.9-03)

1. Open the `Agent-Performance-Analytics` workspace.
2. Compare KPI card values to the raw query in PPAC and Application Insights.
3. Verify the dataset refresh timestamp is within the configured SLA (Zone 3: ≤ 1 hour).
4. **Expected:** values match within the refresh window.

### Test 4 — Alert triggering (TC-2.9-04)

1. Temporarily lower an alert threshold (e.g., error rate > 0.1%).
2. Wait for the next evaluation interval (Power Automate ≤ 1 h, Azure Monitor ≤ 5 min).
3. Confirm the notification arrives in Teams / email / paging system.
4. **Restore the threshold immediately and record the test in the change log.**
5. **Expected:** alert delivered to all configured channels within the documented SLA.

### Test 5 — Latency percentile evidence (TC-2.9-05)

1. Run the KPI script (`Get-AgentKpis.ps1`) for the trailing 30 days.
2. Verify p50 / p95 / p99 are populated for every Zone 2/3 agent.
3. **Expected:** percentiles within the zone targets; outliers documented in the optimization backlog.

### Test 6 — Quarterly model performance memo (TC-2.9-06, Zone 3 only)

1. Confirm the Model Risk Manager has produced a quarterly memo summarizing:
    - KPI trend versus prior quarter
    - Drift indicators (input distribution, output quality)
    - Hallucination / grounding metrics where measured
    - Optimization actions taken and their results
2. **Expected:** memo exists, dated within the prior quarter, referenced in MRM register per OCC Bulletin 2026-13 (formerly OCC 2011-12).

### Test 7 — Hallucination / grounding telemetry (TC-2.9-07, Zone 3 — if implemented)

1. Confirm a custom event (e.g., `customEvents | where name == "HallucinationDetected"`) returns rows.
2. Compare against the documented sampling methodology (e.g., 5% of sessions evaluated by Azure AI Evaluation SDK).
3. **Expected:** non-zero events; rate trends visible on the RAI dashboard.

### Test 8 — Review meeting cadence (TC-2.9-08)

1. Inspect the calendar series for weekly / monthly / quarterly reviews.
2. Pull the last 3 months of meeting minutes from WORM-capable storage.
3. **Expected:** every meeting documented with attendees, KPI snapshot, and decisions.

### Test 9 — Data export to immutable storage (TC-2.9-09)

1. Navigate to the ADLS Gen2 container or storage account holding the export.
2. Verify recent files (daily cadence) and the immutability policy is enabled in time-based retention mode.
3. **Expected:** files present; retention policy locked; deletion attempts denied (test with `Remove-AzStorageBlob -WhatIf`).

### Test 10 — End-to-end customer-impact scenario (TC-2.9-10, Zone 3)

1. Replay a synthetic customer transcript known to stress the agent.
2. Observe latency, error rate, escalation, and CSAT proxy in the dashboard.
3. **Expected:** all signals captured; alerts behave per design; transcripts retained per SEC 17a-4.

---

## Test case matrix

| Test ID | Scenario | Expected | Pass / Fail |
|---|---|---|---|
| TC-2.9-01 | Native analytics shows agent data | Sessions, CSAT visible (≤ 48 h lag) | |
| TC-2.9-02 | App Insights ingesting telemetry | Last 24 h count > 0 | |
| TC-2.9-03 | Power BI dashboard accurate | Matches source within refresh window | |
| TC-2.9-04 | Alert triggers on threshold breach | Notification delivered to all channels | |
| TC-2.9-05 | Latency percentiles available | p50 / p95 / p99 populated | |
| TC-2.9-06 | Quarterly MRM memo exists | Dated within prior quarter | |
| TC-2.9-07 | RAI / hallucination telemetry | Events emitted per sampling design | |
| TC-2.9-08 | Review cadence honored | Minutes for last 3 months on WORM | |
| TC-2.9-09 | ADLS export immutable | Files present, retention locked | |
| TC-2.9-10 | Synthetic customer scenario | All signals + alert behaviors correct | |

---

## Evidence collection checklist

- [ ] Screenshot: PPAC → Analytics → Copilot Studio
- [ ] Screenshot: Copilot Studio agent → Settings → Application Insights connection
- [ ] Screenshot: Power BI dashboard KPI cards with refresh timestamp
- [ ] Screenshot: Alert notification (Teams / email / paging system)
- [ ] Screenshot: ADLS Gen2 container with files + immutability policy detail
- [ ] Export: `agent-inventory-*.json` + manifest with SHA-256 (Script 1)
- [ ] Export: `appinsights-linkage-*.json` (Script 2)
- [ ] Export: `kpis-30-day-*.json` (Script 3)
- [ ] Document: quarterly MRM memo (Zone 3)
- [ ] Document: review meeting calendar series + last 3 months of minutes
- [ ] Document: change log entry for each alert threshold test (Test 4)

Stage all evidence under `maintainers-local/tenant-evidence/2.9/`. The folder is gitignored — never commit tenant data.

---

## Attestation statement template

```markdown
## Control 2.9 Attestation - Agent Performance Monitoring and Optimization

**Organization:** [Organization Name]
**Control Owner:** [Name / Role]
**Tenant ID:** [Tenant ID]
**Period:** [YYYY-Q#]

I attest that, for the period above:

1. Copilot Studio analytics is enabled and producing data for all in-scope agents.
2. Application Insights is linked to every Zone 2 and Zone 3 agent and ingesting telemetry.
3. Performance KPIs are defined and approved per zone:
    - Zone 1: error rate < [X]%, p95 < [X] s
    - Zone 2: error rate < [X]%, p95 < [X] s, CSAT ≥ [X]
    - Zone 3: error rate < [X]%, p95 < [X] s, CSAT ≥ [X]
4. Alerts are configured for error rate, latency, and (Zone 2/3) CSAT, with escalation
   paths through [Teams / email / paging] and tested within the period (date: [date]).
5. Review cadence is operating:
    - Weekly operational: [day / time]
    - Monthly business: [day / time]
    - Quarterly executive: [day / time]
    - Quarterly model risk (Zone 3): [day / time], memo dated [date]
6. Telemetry is retained for [N] days in Application Insights and [N] days on WORM-capable
   storage to help meet SEC 17a-4(f) and FINRA 4511 record-keeping requirements.
7. Telemetry retention periods meet SEC 17a-4(f) and FINRA 4511 requirements.

**Agents monitored:** [Count]
**Evidence package:** [path / SHA-256 of manifest]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 2.9](../../../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
