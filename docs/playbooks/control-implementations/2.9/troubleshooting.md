# Troubleshooting: Control 2.9 - Agent Performance Monitoring and Optimization

**Last Updated:** April 2026
**Audience:** M365 administrators investigating monitoring gaps that could create false-clean evidence for FINRA / SEC / OCC examinations.

---

## Quick reference

| Symptom | Likely cause | First action |
|---|---|---|
| Analytics dashboard empty for new agents | Pre-populate window (24–48 h) not elapsed; or analytics disabled | Confirm in PPAC → Analytics → Microsoft Copilot Studio |
| Sovereign tenant returns no data | Wrong `-Endpoint` on `Add-PowerAppsAccount`; commercial endpoint hit instead of GCC / GCC High / DoD | Re-run with the correct endpoint per the [PowerShell baseline](../../_shared/powershell-baseline.md) |
| App Insights "configured" but no telemetry | Connection string typo; ingestion lag; sampling at 0% | Run Script 2 in `powershell-setup.md`; check sampling settings |
| Power BI dashboard stale | Dataflow refresh failure; ADLS export lag; gateway down | Check refresh history; manually refresh |
| Alerts not firing | Power Automate flow disabled; threshold above current values; smart detection still in baselining | Verify flow run history; lower threshold to test |
| CSAT empty | Survey topic not published or not routed at end of conversation | Add satisfaction survey topic to agent |
| Get-AdminPowerAppEnvironmentRoleAssignment empty on Dataverse env | Documented Microsoft behavior — these cmdlets do not work on Dataverse-backed environments | Use PPAC Dataverse Security Roles |

---

## Detailed troubleshooting

### Issue 1 — Copilot Studio analytics empty after deployment

**Symptoms:** No sessions, conversations, topic resolution, or CSAT visible for an agent that is in production use.

**Investigation:**

1. Confirm the agent is **published** (analytics aggregates only published-channel sessions, not test-pane traffic).
2. Confirm at least 24 h has elapsed since first user session — initial population is not real-time.
3. Confirm the user viewing analytics has either **AI Administrator**, **Power Platform Admin**, or **environment Maker** role on the environment.
4. In sovereign tenants, confirm the analytics service is **GA in your cloud** — GCC High / DoD historically lag commercial by several months.

**Resolution:** Wait the documented lag, then verify role and publication. If still empty after 72 h with confirmed user activity, open a Microsoft support ticket — this is platform-side.

---

### Issue 2 — False-clean evidence in sovereign clouds

**Symptoms:** PowerShell scripts complete with `Write-Host "PASS"` lines but report zero environments / zero agents in a tenant known to have many.

**Root cause:** `Add-PowerAppsAccount` was called without an `-Endpoint` parameter (or with `prod`), authenticating against the commercial cloud while the tenant lives in `usgov`, `usgovhigh`, or `dod`. **No error is thrown** — the cmdlet returns an empty collection.

**Resolution:** Always parameterize the endpoint per the [PowerShell baseline](../../_shared/powershell-baseline.md). Add a guard:

```powershell
$envs = Get-AdminPowerAppEnvironment
if (-not $envs) {
    throw "No environments returned. Verify the -Endpoint parameter matches your tenant's sovereign cloud."
}
```

**FSI impact:** Any monitoring evidence collected with the wrong endpoint must be discarded and the run repeated. Document the corrected run in your audit trail.

---

### Issue 3 — Application Insights linked but no telemetry ingested

**Symptoms:** Settings → Application Insights shows a connection string; KQL `requests | where timestamp > ago(24h) | count` returns 0.

**Investigation steps:**

1. **Sampling:** check `customDimensions['samplingRate']`. If set to 0% by an `applicationinsights.config` override or telemetry processor, all data is dropped.
2. **Ingestion lag:** new resources can take 10–15 minutes for first events; if the link was just configured, wait.
3. **Connection string mismatch:** confirm the string in Copilot Studio resolves to the same App Insights resource you are querying. A common error is pasting the string from a sibling environment.
4. **Daily cap:** Application Insights has a configurable daily cap; if hit, ingestion stops until the next UTC day.
5. **Network egress:** if your tenant uses Private Link / restricted egress, confirm Copilot Studio's egress is allowlisted to the App Insights ingestion endpoint.

**Resolution:** Address the specific failure. After fix, allow 30 minutes and re-query.

---

### Issue 4 — Power BI dashboard not refreshing

**Symptoms:** Dashboard tiles show stale timestamps or refresh history shows failures.

**Investigation:**

1. **Source credentials:** dataflow / dataset credentials may have expired (especially OAuth tokens). Re-authenticate.
2. **ADLS Gen2 connector:** verify the service principal still has `Storage Blob Data Reader` on the container.
3. **On-premises gateway** (if used): confirm the gateway service is running and the Power BI tenant shows it as Online.
4. **Schema drift:** if an analytics export added or removed columns, the dataset may fail with "column not found." Edit the dataflow to remove the reference or add a default.
5. **Capacity throttling:** Premium / Fabric capacity nearing CU exhaustion can throttle scheduled refresh. Inspect capacity metrics.

**Resolution:** Address the root cause and trigger a manual refresh to confirm. Document the cause in the change log if customer-facing reporting was affected.

---

### Issue 5 — Alert flow / rule not triggering on threshold breach

**Symptoms:** Threshold is clearly exceeded in the dashboard but no notification arrived.

**Power Automate path:**

1. Confirm flow status is **On** (a tenant DLP policy change can disable flows that use a now-blocked connector).
2. Inspect the last 5 runs — common failures: 401 from Power BI dataset (refresh stale credentials); type mismatch in the threshold condition (string vs number).
3. Verify the Teams / email connector still has a valid principal — service-account password rotations break unattended flows.

**Azure Monitor path:**

1. Confirm the alert rule is **Enabled** and the action group has at least one receiver.
2. Smart Detection alerts require 7+ days of baseline data — newly created resources will not fire smart alerts.
3. Confirm the metric being evaluated is the right one — `requests/failed` vs `requests/duration` are distinct signals.
4. Check the action group history — Teams webhooks expire if the channel is deleted.

**Resolution:** Fix the failure, then run the Test 4 procedure in `verification-testing.md` to confirm and document.

---

### Issue 6 — Performance degradation detected

**Symptoms:** Error rate or p95 latency exceeds zone threshold sustained over multiple intervals.

**Triage:**

1. **Recent changes:** review the agent change log (Control 2.5) for topic edits, model swaps, knowledge source updates, or connector changes in the last 7 days.
2. **Backend dependencies:** check Service Health (Azure + M365), then any custom APIs the agent calls.
3. **Capacity:** environment capacity metrics in PPAC — sessions per minute hitting the environment limit causes 429s that surface as errors.
4. **Model degradation:** for Zone 3, request a hallucination / grounding sample from the Model Risk Manager — performance drops can correlate with model behavior changes after platform updates.
5. **Knowledge source freshness:** SharePoint or web-source indexing failures can degrade generative answer quality without changing the agent.

**Resolution:** roll back the most recent change if correlated; otherwise file a Microsoft support ticket and document the incident under Control 2.7 (Incident Management).

---

### Issue 7 — Hallucination / grounding metrics absent (Zone 3)

**Symptoms:** RAI dashboard shows no events or zero rate.

**Likely causes:**

1. The Azure AI Evaluation SDK pipeline is not running. Confirm the scheduled job (Azure Function / Logic App / Power Automate) executed in the last interval.
2. Custom events emitted by the evaluator are written to a different App Insights resource than the dashboard queries.
3. The sampling rate is too low — at 1% sampling on a low-volume agent, weeks may pass with zero captured events.

**Resolution:** Verify the evaluator is running, points to the correct App Insights, and the sampling rate is calibrated for agent volume. Document the sampling methodology in the MRM memo.

---

## Escalation path

1. **Agent Owner** — agent-specific issues, topic edits
2. **Power Platform Admin / AI Administrator** — analytics, App Insights linkage, environment capacity
3. **AI Governance Lead** — KPI definitions, threshold tuning, cross-zone trends
4. **Model Risk Manager** — sustained Zone 3 degradation, MRM memo updates (OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7))
5. **Microsoft Support** — platform issues confirmed reproducible after triage

---

## Known limitations

| Limitation | Impact | Workaround |
|---|---|---|
| 24–48 h lag for first analytics population | New deployments have a blind window | Combine with App Insights (near real-time) for the first week |
| CSAT requires user prompt | No score without a survey topic | Publish satisfaction survey at end of conversation |
| Cross-environment views in PPAC are limited | Multi-environment tenants need manual aggregation | Use ADLS export + Power BI to unify |
| Application Insights minimum sampling | Very low-traffic agents may not show events | Set sampling to 100% for Zone 3 small-volume agents |
| Sovereign cloud feature drift | Some features lag commercial by months | Verify feature parity each quarter; document gaps |
| `*-AdminPowerAppEnvironmentRoleAssignment` does not work on Dataverse-backed environments | Returns empty silently | Use PPAC Dataverse Security Roles per the [PowerShell baseline](../../_shared/powershell-baseline.md) |

---

[Back to Control 2.9](../../../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
