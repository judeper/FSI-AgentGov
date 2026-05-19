# Verification & Testing: Control 2.17 — Multi-Agent Orchestration Limits

**Last Updated:** April 2026
**Audience:** AI Governance Lead, Power Platform Admin, Compliance Officer (evidence sign-off)
**Cadence:** Initial implementation + quarterly attestation; ad-hoc on every change to the orchestration graph

!!! warning "What this control verifies"
    These tests verify *custom orchestration controls*, not built-in platform features. If your organization has not yet implemented the depth tracking, circuit breaker, HITL, and telemetry described in the *Portal Walkthrough*, the tests below will surface a control gap — not a configuration drift.

---

## Test Scenarios

The seven manual tests below validate every governance objective in the control. Each test should be executed in a **non-production environment** that mirrors the orchestration graph, then re-confirmed in production via the read-only PowerShell evidence script.

### Test 1 — Delegation Depth Enforcement

**Objective:** Confirm a request that would exceed the per-zone depth limit is blocked at the orchestration layer, not at the platform.

1. In a non-prod environment, configure a deliberate over-depth chain (e.g., for Zone 2, build A → B → C → D where the limit is 2).
2. Trigger the root agent with a request that exercises the full chain.
3. Capture the agent response, the audit-log entry, and the Application Insights `Orchestration.DelegationStart` events.

**Expected:** The fourth-level invocation is blocked with a structured error referencing the depth limit. A `depth-violation` event is emitted to telemetry. The chain does not silently proceed.

**Evidence:** Audit log export (CSV), App Insights query result, agent response transcript.

---

### Test 2 — Circuit Breaker Activation

**Objective:** Confirm cascading failures open the circuit and stop further delegations.

1. In non-prod, force a downstream agent to return errors (e.g., revoke its connector, point it at an unreachable endpoint).
2. Send N+1 requests through the root agent (where N is the configured failure threshold; default 3 for Zone 3).
3. Inspect the `fsi_CircuitBreakerState` Dataverse table and the `Orchestration.CircuitBreakerOpen` custom event.

**Expected:** Circuit transitions to `Open` after exactly N failures. Request N+1 returns the circuit-open error path *without* invoking the unhealthy downstream. Telemetry event fires once per state transition.

---

### Test 3 — Circuit Breaker Reset (Half-Open Probe)

**Objective:** Confirm the circuit recovers safely after the reset timeout.

1. After Test 2, restore downstream health.
2. Wait for the configured reset timeout (default 60s for Zone 3).
3. Send one request — observe state transitions to `HalfOpen`, the probe call succeeds, and the state returns to `Closed`.
4. Send a second request — observe normal flow.

**Expected:** Recovery happens automatically; no human intervention required. State transitions are emitted as telemetry events.

---

### Test 4 — Per-Call and Total-Chain Timeout

**Objective:** Confirm timeouts prevent runaway orchestrations from consuming resources or stalling the user.

1. Configure a downstream agent to delay responses past the per-call timeout (e.g., 60s when the limit is 30s).
2. Trigger orchestration; capture the response time.

**Expected:** Per-call timeout fires within tolerance (±10%). Total-chain timeout (e.g., 90s for Zone 3) is enforced as an upper bound regardless of how the per-call timeouts compose. The user receives a deterministic timeout error, not a stalled session.

---

### Test 5 — HITL Checkpoint Pause and Resume

**Objective:** Confirm Zone 3 customer-impacting actions pause for human approval and resume correctly.

1. Trigger an orchestration that hits a HITL checkpoint (e.g., a transaction action above the documented threshold).
2. Confirm the adaptive card is delivered to the configured approver group with the correct `correlationId` and action summary.
3. Approve via the card; confirm the orchestration resumes from the checkpoint, not from the start.
4. Capture the persisted approval record (`approverUpn`, `decision`, `decisionUtc`).

**Expected:** Approval persisted with full audit trail; orchestration resumes within seconds of approval. No PII is embedded in the approval card body.

---

### Test 6 — HITL Timeout Escalation

**Objective:** Confirm an unapproved HITL request escalates rather than silently abandoning.

1. Trigger a HITL checkpoint and do not approve.
2. Wait for the configured timeout (e.g., 4 business hours for customer-impacting; 24h for non-urgent).

**Expected:** The request is routed to the secondary approver group on timeout. The original requester is notified. No orchestration silently proceeds or silently terminates without a recorded decision.

---

### Test 7 — Telemetry Completeness

**Objective:** Confirm every orchestration step produces an audit-defensible event chain.

1. Run a representative end-to-end chain (root → leaf → return).
2. Query Application Insights and the Microsoft 365 Unified Audit Log for the `correlationId`.

**Expected:** A complete event chain is recoverable from telemetry alone:

- One `Orchestration.DelegationStart` per parent→child edge
- One `Orchestration.DelegationEnd` matching each start (with duration and success)
- Audit log `CopilotInteraction` records correlated by `correlationId`
- For chains touching MCP: one `Orchestration.MCP.ToolInvocation` per tool call with `dataClassification`

**Critical:** If telemetry cannot reconstruct the chain end-to-end, the control is not yet meeting FINRA Rule 4511 / SEC 17a-4 recordkeeping expectations for agentic workflows — flag as a control gap.

---

## FSI-Specific Test Scenarios (Zone 3)

In addition to Tests 1–7, Zone 3 deployments should run these FSI-grounded scenarios at least annually:

| Scenario | Validates | Regulatory anchor |
|----------|-----------|-------------------|
| Cumulative financial stop-loss across a chain | Chain-level financial cap is enforced even when no single agent breaches its individual limit | FINRA RN 24-09 + Rule 3110; OCC Bulletin 2026-13 (formerly OCC 2011-12) |
| Combined model-risk evaluation for the chain as a single composite model | Chain has a written Combined Model Risk Card (Control 2.6) | Fed SR 26-2 (formerly SR 11-7) |
| HITL approval review for rubber-stamping (sample 5% of approvals quarterly) | Approver attention quality, not just presence | FINRA Rule 3110 supervisory review |
| MCP allow-list drift | No production orchestration invokes an MCP server outside the approved registry | FINRA RN 24-09 + Rule 3110; vendor risk management |
| Cross-environment correlation-ID continuity | Pattern B depth tracking survives environment boundaries | SEC 17a-4 recordkeeping completeness |

---

## Test Case Tracking

| Test ID | Scenario | Expected | Pass/Fail | Evidence Ref |
|---------|----------|----------|-----------|--------------|
| TC-2.17-01 | Depth limit enforced | Fourth-level call blocked | | |
| TC-2.17-02 | Circuit opens on threshold | State = Open after N failures | | |
| TC-2.17-03 | Circuit half-open recovery | Returns to Closed on success probe | | |
| TC-2.17-04 | Timeout enforcement | Deterministic timeout error | | |
| TC-2.17-05 | HITL pause/resume | Approval persisted, chain resumes | | |
| TC-2.17-06 | HITL timeout escalation | Secondary approver routed | | |
| TC-2.17-07 | Telemetry completeness | End-to-end chain recoverable | | |
| TC-2.17-08 | Financial stop-loss (Zone 3) | Chain cap enforced | | |
| TC-2.17-09 | MCP allow-list drift (Zone 3) | No unapproved invocations | | |

---

## Evidence Collection Checklist

### Architecture and Policy

- [ ] Delegation graph diagram (PNG / Mermaid / Visio) — one per orchestration pattern
- [ ] Documented per-zone limits (depth, timeouts, failure thresholds, financial caps, HITL conditions)
- [ ] Combined Model Risk Card for each Zone 3 chain (Control 2.6 cross-reference)
- [ ] Approved MCP server registry export (if applicable)

### Configuration

- [ ] Screenshots: depth-tracking variable / Dataverse row schema
- [ ] Screenshots / flow exports: `fsi-CircuitBreaker-Check` and `fsi-CircuitBreaker-Record` Power Automate flows
- [ ] Screenshots: HITL adaptive card definition and approval-routing configuration
- [ ] Screenshots: Application Insights custom event configuration; alert-rule JSON

### Test Evidence

- [ ] Audit-log export covering test window (JSON + CSV with SHA-256 manifest)
- [ ] App Insights KQL output for test correlation IDs
- [ ] Approval records (Dataverse export) for HITL tests
- [ ] Circuit-breaker state-transition log

### Quarterly Attestation

- [ ] Quarterly attestation pack from `Get-Quarterly-2.17.ps1` with cover sheet signed by AI Governance Lead
- [ ] Sample of HITL approvals reviewed for rubber-stamping (Zone 3)
- [ ] MCP registry review confirming no unapproved-server activity

---

## Evidence Artifact Naming Convention

```
Control-2.17_<ArtifactType>_<YYYYMMDD>.<ext>

Examples:
  Control-2.17_DelegationGraph_20260415.png
  Control-2.17_AuditLog_20260415.json
  Control-2.17_AppInsights_TC-07_20260415.csv
  Control-2.17_HITL_ApprovalSample_20260415.xlsx
  Control-2.17_QuarterlyAttestation_2026Q2.pdf
```

Lodge artifacts in WORM-configured storage (Microsoft Purview Data Lifecycle Management retention lock or Azure Storage immutability policy). Recommended retention: **6 years** to support SEC 17a-4 expectations for FSI; check your firm's written supervisory procedures (WSPs) for the authoritative retention period.

---

## Attestation Statement Template

```markdown
## Control 2.17 Attestation — Multi-Agent Orchestration Limits

**Organization:** [Organization Name]
**Control Owner:** [AI Governance Lead — Name]
**Period:** [YYYY-MM-DD to YYYY-MM-DD]
**Attestation Date:** [YYYY-MM-DD]

I have reviewed the evidence pack referenced below and attest to the following for the period above:

1. The delegation graph for every production orchestration is documented, current, and aligned to the per-zone depth limits.
2. Circuit breakers are deployed for every Zone 2/3 orchestrating agent and have been tested within the period.
3. HITL checkpoints are configured at the action boundary for customer-impacting, regulated-data, and material financial decisions in Zone 3.
4. Telemetry completeness has been verified end-to-end for at least one representative chain per orchestration pattern.
5. No production orchestration invoked an MCP server outside the approved registry during the period (or, if it did, an incident record has been opened per Control 3.4).
6. A sample of HITL approvals has been reviewed for supervisory-quality (FINRA Rule 3110); findings are recorded with the evidence pack.
7. Combined Model Risk Cards are current for every Zone 3 chain (Control 2.6).

**Evidence pack location (WORM):** _______________________
**Evidence pack SHA-256 manifest reference:** _______________________

**Signature:** _______________________
**Role:** AI Governance Lead
**Date:** _______________________
```

---

[Back to Control 2.17](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
