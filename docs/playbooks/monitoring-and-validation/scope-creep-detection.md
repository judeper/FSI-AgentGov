# Spec: Scope Creep Detection (Access Drift + Behavior Drift)

**Purpose:** Detect and contain “agent drift” where an agent’s *effective scope* expands over time (new data sources, connectors, permissions, actions, or emergent behaviors) beyond the approved baseline.  
**Applies to:** Zone 3 (required), and Zone 2 agents that access Confidential/Restricted data or initiate workflows/actions.  
**Regulatory driver:** FINRA’s 2026 oversight report highlights that AI agents may act beyond intended “scope and authority” and calls for monitoring agent system access and data handling, tracking agent actions and decisions, and establishing guardrails to limit agent behavior. <sup>[16]</sup>  
**Evidence driver:** Microsoft Purview “CopilotInteraction” audit records include `AccessedResources` (including sensitivity label IDs and policy restriction details), and agent identifiers such as `AgentId`, `AgentName`, and `AgentVersion`, enabling drift detection and correlation to specific agents/versions. <sup>[16]</sup>

---

## Definitions

- **Scope baseline:** The approved set of (a) connectors/tools, (b) data sources, (c) permissions, and (d) action types the agent is allowed to use, as documented in the Action Authorization Matrix and Per-Agent Data Policy.
- **Access drift:** The agent begins accessing resources or scopes not in the baseline (new site collections, new environments, new label classes).
- **Behavior drift:** The agent’s behavior changes (new action sequences, abnormal volume patterns, unusually broad retrieval, or higher policy hit rates) even if nominal permissions haven’t changed.
- **Material drift:** Drift that increases regulatory, privacy, security, or consumer harm exposure, or violates baseline controls.

---

## Inputs (required telemetry sources)

### T1) Agent inventory (authoritative list)
- Agent ID, name, version, zone, owner, status
- Link to AAM and PDHP

### T2) Audit telemetry
- Purview Copilot audit logs:
  - `AgentId`, `AgentName`, `AgentVersion` <sup>[16]</sup>
  - `AccessedResources` including `SiteUrl`, `ID`, `Type`, `Action`, `Status`, `SensitivityLabelId`, and `PolicyDetails` <sup>[16]</sup>
  - Optional: `XPIADetected` for cross prompt injection detection <sup>[16]</sup>

### T3) [Decision Logs](../governance-operations/decision-log-schema.md)
- decision_id, confidence band, routing, action_result, policy IDs invoked, tool calls

### T4) Platform configuration & access control state
- Allowed connectors and policies (DLP, ACP)
- RBAC group membership for agent-run identities (if applicable)
- SharePoint/Graph scopes and permissions

---

## Scope baseline model (required)

For each governed agent, define baseline as:

### B1) Connector/tool allowlist
- Allowed connectors/tools and allowed operations (read/write/execute).

### B2) Data source allowlist
- SharePoint site(s), libraries, folders (or patterns)
- Dataverse environments/tables
- Any other enterprise sources

### B3) Sensitivity label boundary
- Allowed label set (e.g., Internal+Confidential)
- Prohibited label set (e.g., Restricted)

### B4) Action envelope
- Allowed action categories:
  - Read / Generate / DraftWrite / Notify / Execute / Block / Escalate
- Any “Execute” action requires explicit listing and limits.

### B5) Volume and timing bounds
- Max actions/minute
- Max notifications/hour
- Business-hours-only rules (if required)

---

## Detection requirements (MVP)

### D1) New connector/tool usage (hard signal)
**Trigger:** Agent uses a connector/tool not on the baseline allowlist.  
**Action:** Block (where possible) + create S1 escalation + log decision + open ticket.

### D2) New data scope access (hard signal)
**Trigger:** `AccessedResources.SiteUrl` (or resource identifiers) fall outside baseline allowlist. <sup>[16]</sup>  
**Action:** Alert + optionally block; create escalation ticket.

### D3) Label boundary breach (hard signal)
**Trigger:** `AccessedResources.SensitivityLabelId` indicates prohibited class OR `PolicyDetails` indicates block/restriction. <sup>[16]</sup>  
**Action:** Escalate; treat as S1 if prohibited label boundary is crossed.

### D4) Abnormal volume / anomalous behavior (soft signal with thresholds)
**Trigger:** Interaction/action counts exceed baseline thresholds (e.g., 3x weekly median).  
**Action:** Throttle + escalate to owner for review; tune threshold to reduce false positives.

### D5) Rising policy hit rate (soft signal)
**Trigger:** Increasing frequency of `PolicyDetails` blocks or DLP matches (week-over-week). <sup>[16]</sup>  
**Action:** Review prompt patterns, data sources, and update controls.

### D6) Agent version change without governance review (hard signal)
**Trigger:** New `AgentVersion` observed in audit logs without corresponding change ticket approval. <sup>[16]</sup>  
**Action:** Escalate; optionally disable agent until approved.

---

## Enforcement actions (what “stop the drift” means)

Order of preference:
1. **Prevent**: deny connector permissions, restrict SharePoint scopes, enforce label-based access.
2. **Block**: agent-level policy blocks; DLP blocks (block-without-override for prohibited categories).
3. **Throttle**: rate-limits to stop runaway automation.
4. **Disable**: temporarily block the agent (admin center controls) for severe/unknown drift.

FINRA highlights autonomy and scope/authority risks in agents and calls for guardrails to limit agent behavior, actions, or decisions. <sup>[16]</sup>

---

## Alerting and escalation (must integrate with EDM)

Every D1–D3 event must map to an Escalation Matrix entry:
- Severity: S1 default
- SLA: 15–30 minutes for initial triage
- Required evidence: audit log excerpt + decision log ID + baseline reference

---

## Metrics and reporting ([Real-time Compliance Dashboard](real-time-compliance-dashboard.md) feeders)

Minimum metrics per agent (weekly):
- drift_events_total
- drift_events_by_type (D1–D6)
- blocked_vs_allowed actions
- top new SiteUrl/resources
- top policy blocks (PolicyDetails)
- MTTD / MTTR for S1 events

---

## Testing plan (required)

### Negative tests (must pass)
- Attempt to access non-allowlisted SharePoint site ⇒ alert/block + logged. <sup>[16]</sup>
- Attempt to invoke prohibited connector ⇒ blocked + logged.
- Attempt to access prohibited label class ⇒ blocked or policy restricted + escalated. <sup>[16]</sup>

### Regression tests
- New approved scope change should not generate drift alerts after baseline update.

---

## “Done” criteria (audit-ready)

- Baseline exists for every Zone 3 agent (AAM + PDHP + baseline config record).
- Drift signals are detected from audit logs and/or platform telemetry.
- Alerts are routed and tracked (ticket IDs).
- Evidence is reproducible from Purview export (operation filter + offline filtering by AgentId/version). <sup>[16]</sup>
- Quarterly governance review includes drift summary and remediation actions.

---

## Implementation notes (pragmatic)

- Use Purview audit logs as the canonical “what resources were accessed” signal for Copilot/agent interactions, because records include `AccessedResources` and label IDs. <sup>[16]</sup>
- Decision logs provide the “why” and “what was attempted,” which complements audit metadata.
- Keep false positives low by separating “hard” drift (policy boundary crossings) from “soft” drift (anomalies) and requiring human review before enforcement escalation for soft signals.
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
