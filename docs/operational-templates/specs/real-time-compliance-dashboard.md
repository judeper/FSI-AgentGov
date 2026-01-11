# Spec: Real-time Compliance Dashboard (Continuous Controls Monitoring)

**Purpose:** Provide near-real-time governance visibility for Copilot/agent usage, data access, and policy enforcement—so compliance can evidence continuous monitoring rather than periodic reviews.  
**Applies to:** Zone 3 (required), Zone 2 (recommended for medium/high impact), Zone 1 (optional summary view).  
**Evidence grounding:** Microsoft Purview audit logs for Copilot and AI interactions include `AccessedResources` (including sensitivity labels and policy restriction details), plus `AgentId`, `AgentName`, and `AgentVersion`, enabling dashboards to summarize what data was accessed and which agents were involved. [page:16]  
**Control grounding:** Microsoft Purview supports auditing, retention, eDiscovery, and compliance controls for AI interactions, and emphasizes using these capabilities to manage the risks of AI usage across supported Copilots and agents. [page:17]

---

## 1) Dashboard objectives (what it must answer)

1. **Which agents are active right now?** (Inventory + last-seen activity)
2. **Are required logs present?** (Audit completeness + decision log completeness)
3. **Are data boundaries being respected?** (Label/DLP/policy blocks)
4. **Is scope drifting?** (Connector/data drift events)
5. **Are escalations happening and within SLA?** (EDM/incident workflow)
6. **Which agents/users are riskiest?** (hotspots and trends)

---

## 2) Data sources (minimum viable)

### S1) Purview Audit (CopilotInteraction)
Use for:
- interaction volume and trends
- resources accessed and label context
- policy blocks/restrictions
- agent identity (AgentId/Name/Version)

Purview audit records include `AccessedResources` (with `SensitivityLabelId`, `PolicyDetails`, and `XPIADetected` flags) and agent identifiers like `AgentId`, `AgentName`, and `AgentVersion`. [page:16]

### S2) Decision logs (Gap 2)
Use for:
- reasoning and confidence
- action attempts and results
- escalation triggers and outcomes

### S3) Escalation/ticketing system
Use for:
- SLA tracking
- MTTR/MTTD measurement
- audit evidence pack links

### S4) Agent inventory
Use for:
- expected zones/levels
- owners and approval states
- links to AAM/PDHP/EDM artifacts

---

## 3) Role-based access (RBA) model

- **Compliance dashboard view:** aggregated metrics + drill-down to evidence IDs
- **Security/SecOps view:** drift, policy blocks, XPIA, anomalous behavior
- **Business owner view:** only their agents + remediation tasks
- **Auditor view:** read-only evidence pack exports (time-boxed)

Dashboards should avoid exposing prompt content by default; rely on IDs and metadata unless explicitly authorized and supported. [page:17]

---

## 4) Metrics catalog (MVP)

### 4.1 Inventory & lifecycle
- Total agents (by zone)
- Agents with missing required artifacts (AAM/PDHP/EDM links)
- Agents with unapproved versions observed in audit logs (`AgentVersion` drift) [page:16]

### 4.2 Audit and evidence completeness
- % interactions with valid `AgentId`
- % interactions with non-empty `AccessedResources` [page:16]
- Decision-log coverage rate (decision logs per material interaction)
- Exportable evidence pack readiness (Yes/No per Zone 3 agent)

### 4.3 Data boundary and policy enforcement
- Count of interactions accessing Confidential vs Restricted labels (via `SensitivityLabelId`) [page:16]
- Count of policy restricted/blocked resources (via `PolicyDetails`) [page:16]
- DLP rule match counts (if integrated via DSPM/Activity Explorer—optional)

### 4.4 Scope creep / drift (Gap 3)
- Drift events by type (new SiteUrl, new connector, new action category)
- Drift severity (S1/S2/S3)
- Top agents by drift rate
- Time-to-detect (MTTD)

### 4.5 Prompt-injection / attack surface (optional but recommended)
- XPIA detections count (`XPIADetected == true`) [page:16]
- JailbreakDetected counts if captured via message metadata (where available) [page:16]

### 4.6 Escalation and incident operations
- Escalations by severity per week
- SLA adherence rate (met/missed)
- MTTR for S1 and S2 incidents
- Override rate (and top reasons)

### 4.7 Confidence and quality (Gap 4)
- Distribution of confidence bands (High/Med/Low)
- Low-confidence rate by agent
- Review outcomes for Low confidence (approved/rejected/modified)

---

## 5) Drill-down views (must-have)

### D1) “Agent detail” page (one agent)
Show:
- identity + owners + zone/level
- last 7/30/90 day activity counts (from audit)
- top accessed resources (SiteUrl/type) [page:16]
- label distribution (SensitivityLabelId) [page:16]
- policy blocks summary (PolicyDetails) [page:16]
- drift events summary
- escalation + SLA summary
- links to:
  - Action Authorization Matrix
  - Per-agent Data Policy
  - Escalation Matrix
  - last quarterly review record

### D2) “Policy block explorer”
Show:
- blocked resources and reasons
- agent versions involved
- trends over time
- the “top 10” policies that blocked access

### D3) “Evidence export” view
Provide a one-click path (or documented runbook) to export:
- the relevant audit log window
- the relevant decision logs
- the relevant tickets
- into a single evidence package for auditors

---

## 6) Data refresh and retention requirements

- **Refresh:** near real-time where possible; otherwise hourly is acceptable for MVP.
- **Retention:** align with your records policy; maintain long enough to support exams/investigations.
- **Immutability:** evidence exports should be stored append-only (or immutable storage).

Microsoft Purview highlights auditing, retention, and eDiscovery as mechanisms to manage AI interaction compliance obligations. [page:17]

---

## 7) Implementation approach (pragmatic MVP)

1. **Phase 0:** define metric computation logic + field mappings (especially from `AccessedResources`, `SensitivityLabelId`, `PolicyDetails`, `AgentId`, `AgentVersion`). [page:16]
2. **Phase 1:** implement dashboard with 10–15 core metrics for Zone 3.
3. **Phase 2:** add drill-downs + evidence export runbook.
4. **Phase 3:** add automated weekly compliance summary + anomaly detection.

---

## 8) “Done” criteria

- A compliance user can answer, within 5 minutes:
  - which Zone 3 agents are active
  - whether required logs are being produced
  - whether policy blocks/drift escalations occurred
  - whether escalations met SLA
  - and can export an evidence pack for a date range and agent/version.

---

## 9) Appendix: Key Purview audit fields used

Purview Copilot audit logs include `AccessedResources` with `SensitivityLabelId`, `PolicyDetails`, and `XPIADetected`, and include agent identity fields like `AgentId`, `AgentName`, and `AgentVersion`. [page:16]  
Purview also supports compliance operations for AI interactions including auditing and eDiscovery/retention, which should be referenced as part of the governance evidence approach. [page:17]