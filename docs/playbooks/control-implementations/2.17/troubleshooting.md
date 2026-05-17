# Troubleshooting: Control 2.17 — Multi-Agent Orchestration Limits

**Last Updated:** April 2026

This guide covers the high-frequency failure modes observed when implementing the orchestration controls. The emphasis is on **false-clean** patterns — situations where the control *appears* to be working but is silently failing — because those are the highest-risk failures for FSI audit defensibility.

---

## Quick Reference

| Symptom | Most likely cause | Fix |
|---------|------------------|-----|
| Audit query returns zero events | Wrong cloud endpoint, audit logging disabled, or record type renamed | Verify `-Endpoint` / `-ExchangeEnvironmentName`; confirm Control 1.7 is implemented; cross-check current Microsoft Learn record types |
| Depth limit not enforcing | Tracking variable not incremented or not passed to child agents | Audit topic flow; confirm increment occurs *before* delegation |
| Circuit breaker stuck Open | Reset timeout too long, downstream still failing, or half-open probe failing | Manually inspect `fsi_CircuitBreakerState`; verify downstream health independently |
| Cascade failures still occurring | Circuit breaker not invoked on every delegation edge | Audit topic flow for missed `fsi-CircuitBreaker-Check` calls |
| HITL approvals abandoned by users | Timeout too short, approver group unstaffed, or card lacks context | Tune timeout; configure secondary approver chain; enrich card metadata |
| MCP tool invoked from unapproved server | DLP gap or registry not synced to Copilot Studio | Tighten Power Platform DLP (Control 2.14); audit registry sync |
| App Insights events missing dimensions | Custom event call missing required custom-dimension keys | Update topic / flow; re-test with Test 7 from *Verification & Testing* |
| Cross-environment depth tracking returns null | Dataverse row not written or `If-Match` ETag conflict not handled | Add retry-on-conflict in the flow; confirm row retention policy |

---

## False-Clean Patterns (Highest Audit Risk)

These patterns produce evidence that *looks* compliant but is not. Hunt them actively during quarterly reviews.

### Pattern 1 — Sovereign-cloud endpoint omission

**Symptom:** PowerShell evidence script reports zero orchestration events; tenant clearly has Copilot Studio activity.

**Root cause:** Cmdlet authenticated against commercial endpoints from a GCC / GCC High / DoD operator workstation. Output is real but from the wrong tenant — likely empty or from an unrelated commercial tenant.

**Detection:** Compare the tenant ID returned by `Get-MgContext` (or `Get-AdminPowerAppEnvironment | Select -First 1`) against the expected target tenant ID before treating evidence as authoritative.

**Fix:** Always pass `-Endpoint` (Power Apps) and `-ExchangeEnvironmentName` (EXO) explicitly. See PowerShell baseline §3.

---

### Pattern 2 — Depth variable not threaded through child agents

**Symptom:** Each individual agent appears to enforce depth correctly; Test 1 (depth violation) passes locally per agent. But end-to-end test exceeds the limit.

**Root cause:** Each child agent reinitializes `OrchestrationDepth = 0` because the parent did not pass the current depth as an input parameter on invocation.

**Fix:** Confirm every delegation node passes `Topic.OrchestrationDepth` as an input. For Pattern B (cross-environment), confirm every agent reads from the same Dataverse row keyed by `correlationId`, not a per-agent local copy.

---

### Pattern 3 — HITL timestamp drift indicating rubber-stamping

**Symptom:** HITL telemetry shows uniformly short `waitDurationMs` (e.g., consistently <30 seconds across all approvers).

**Root cause:** Approvers are clicking through without reviewing context. Audit-defensibility under FINRA Rule 3110 requires *meaningful* supervisory review, not just a click.

**Fix:** Sample 5% of approvals quarterly for quality review; consider adding mandatory free-text justification on the adaptive card; train approvers on context expectations.

---

### Pattern 4 — Audit log retention shorter than 6 years

**Symptom:** Quarterly evidence pack succeeds for the 90-day window but historical reconstruction fails for prior periods.

**Root cause:** Microsoft 365 Audit (Standard) retains 180 days; Audit (Premium) retains 1 year by default. SEC 17a-4 recordkeeping for FSI typically requires 6 years.

**Fix:** Configure long-term retention per Control 1.7. Forward audit events to immutable storage (Sentinel + Storage with immutability policy, or Purview Data Lifecycle Management retention lock) to span the full 6 years independently of the M365 retention setting.

---

### Pattern 5 — Telemetry emitted but not correlated

**Symptom:** Custom events visible in App Insights and audit records visible in Purview, but no way to reconstruct an end-to-end chain.

**Root cause:** `correlationId` not threaded consistently across (a) the originating agent, (b) Power Automate flows, (c) custom event emissions, and (d) Microsoft-emitted audit records (which use their own `OperationId`).

**Fix:** Standardize on a single `correlationId` field at the root agent and propagate through every downstream call. Where Microsoft-emitted IDs differ, persist the mapping (`fsi_correlationId ↔ ms_operationId`) in Dataverse so audit reconstruction can join across sources.

---

## Detailed Issues

### Issue: Delegation depth limit not enforcing

**Diagnostic:**

1. Open the root agent topic in Copilot Studio.
2. Confirm `Topic.OrchestrationDepth` exists as a topic-scoped variable initialized to `0`.
3. Confirm every delegation node is preceded by:
    - A `Set variable` node incrementing depth
    - A `Condition` node comparing `Topic.OrchestrationDepth` against the per-zone max
4. Confirm the `Condition` node's true branch *blocks* the delegation (returns an error or routes to escalation), not merely logs and proceeds.

**Resolution:** If any step is missing, restore per *Portal Walkthrough* Step 3. For chains spanning environments, escalate to Pattern B (Dataverse correlation-ID-scoped depth).

---

### Issue: Circuit breaker stuck Open

**Diagnostic:**

1. Inspect `fsi_CircuitBreakerState` row for the affected `targetAgentId`. Note `state`, `openedUtc`, `consecutiveFailures`.
2. Independently invoke the downstream agent (bypassing the orchestrator) and confirm health.
3. If downstream is healthy: confirm the half-open probe flow is firing. The probe call must update `state = 'Closed'` on success.
4. Check for ETag conflicts: if the probe and a fresh failure race, the probe's update may be lost.

**Resolution:** Add explicit retry-on-conflict to the probe flow. If timeout intervals are too long for operations, tune downward (but do not below 30s for Zone 3, otherwise probes can mask intermittent downstream issues).

---

### Issue: HITL escalations missed by approvers

**Diagnostic:**

1. Confirm the secondary approver group is populated and members have access to the channel/mailbox where adaptive cards are delivered.
2. Verify the escalation path triggers *automatically* on timeout — not via a manual workflow step that may not be running.
3. Sample escalation events in App Insights to confirm `Orchestration.HitlDecision` events fire with `decision = 'EscalatedTimeout'`.

**Resolution:** Treat any silently abandoned approval as a Control 3.4 incident (failure to obtain human approval before a customer-impacting action). Tune timeouts to realistic approval SLAs; never set timeout to "infinite" because that masks abandonment as in-progress.

---

### Issue: MCP tool invoked from unapproved server

**Diagnostic:**

1. Query App Insights for `Orchestration.MCP.ToolInvocation` events; group by `mcpServer`.
2. Diff against the approved MCP server registry.
3. If unapproved entries exist, identify which agent registered the tool and when (Copilot Studio agent activity log).

**Resolution:** Block at two layers:

- **Power Platform DLP** (Control 2.14): place the MCP HTTP connector in the *Blocked* group for non-business-data environments; in the *Business* group for governed environments where it is needed.
- **Registry sync**: if you maintain the MCP registry as a SharePoint list or Dataverse table, build a daily Power Automate flow that reconciles registered MCP servers in production agents against the approved list and opens an incident on drift.

Treat any drift event as a Control 3.4 incident and document in the quarterly attestation.

---

## Known Limitations (April 2026)

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| No native depth-tracking primitive in Copilot Studio | All depth enforcement is custom (topic variables or Dataverse) | Use Patterns A/B; treat the absence as control debt and lobby Microsoft via the Power Platform Ideas portal |
| No native circuit breaker | Custom Power Automate flow required | Documented in *Portal Walkthrough* Step 4 |
| Limited cross-environment orchestration visibility | Reconstructing chains spanning environments requires manual correlation | Use Pattern B + correlation-ID propagation; consider keeping Zone 3 chains within a single environment |
| HITL via adaptive cards uses polling | Latency between approval and resume | Use Microsoft Agent Framework HITL primitives where available — they integrate with checkpoint persistence |
| Custom MCP servers in preview (April 2026) | Behavior may change before GA | Do not promote custom MCP servers to Zone 3 production until GA confirmed on Microsoft Learn |
| 128-tool-per-agent ceiling | Large delegation trees can hit ceiling silently | Run Section 4 of *PowerShell Setup* monthly to track headroom |

---

## Escalation Path

If the issue persists after diagnostic steps:

1. **Power Platform Admin** — environment, DLP, connector, or PPAC configuration questions
2. **Copilot Studio Agent Author** — topic, variable, and tool-registration issues
3. **AI Governance Lead** — policy, limits, registry, or attestation-quality questions
4. **Compliance Officer** — supervisory-review (FINRA 3110), recordkeeping (FINRA 4511 / SEC 17a-4), or model-risk (OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)) interpretation
5. **Microsoft Support** — platform behavior gaps, audit record-type changes, or suspected platform regressions; cite Microsoft Learn references and your tenant ID

For incidents involving customer impact, regulated data, or material financial decisions: open a Control 3.4 incident *first*, then troubleshoot.

---

[Back to Control 2.17](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
