# Spec: Zone 1 Minimum Explainability + Evidence Logging

**Purpose:** Establish a lightweight, privacy-aware “minimum explainability” baseline for **Zone 1 (Personal Productivity)** agents so the organization can evidence supervision/monitoring without treating low-risk chat like a regulated autonomous system.  
**Applies to:** Zone 1 agents (required baseline), and optionally Zone 2 where informational-only assistants exist.  
**Regulatory driver (SEC priorities):** SEC 2026 priorities explicitly expand attention to firms’ use of AI and other automated technologies and emphasize evaluating procedures to monitor and/or supervise AI technologies, including for automation of internal processes. [page:18]  
**Telemetry grounding:** Microsoft Purview audit logs for Copilot/AI interactions include “who/when/where” metadata and references to resources accessed to generate responses, including sensitivity label IDs and policy restriction details. [page:19]

---

## 1) Zone 1 scope and philosophy

Zone 1 agents are informational/personal productivity assistants with:
- no autonomous execution of business actions,
- minimal data sensitivity by default,
- limited blast radius (single user).

Even so, they must produce evidence that:
- usage is observable,
- policy boundaries are enforced,
- risky patterns can be detected and escalated.

---

## 2) Minimum required logging (Zone 1)

### 2.1 Required fields (store as “interaction record”)
For each interaction (prompt-response pair or “session”):
- `timestamp_utc`
- `user_id_hash` (pseudonymous)
- `agent_id` / `agent_name` / `agent_version` (if present)
- `app_host` (e.g., Teams, Word, BizChat)
- `operation` / `recordType` (e.g., CopilotInteraction)
- `output_category` (informational / policy / research / admin help / other)
- `confidence_band` (High/Med/Low) (policy-driven heuristic; see confidence spec)
- `accessed_resources_count`
- `labels_seen_summary` (counts by class, not the label IDs list if you want extra minimization)
- `policy_block_count` (count of blocked/restricted resources)
- `escalation_flag` (true/false)

Purview Copilot audit records contain `AccessedResources` with `SensitivityLabelId`, `PolicyDetails`, and `Status`, enabling a Zone 1 evidence record to summarize “what data was accessed” and “was anything blocked.” [page:19]

### 2.2 Explicitly excluded by default (privacy guardrail)
Do **not** log:
- full prompt text,
- full response text,
- full filenames or message contents,
unless there is an approved collection policy and a clear purpose/need with privacy sign-off.

Microsoft notes audit records reference resources accessed and include metadata rather than requiring you to store full content in custom logs. [page:19]

---

## 3) Minimum explainability fields (what makes this “explainable”)

Zone 1 explainability is “traceability,” not model introspection:
- **What was requested (category):** classify the request type (e.g., summarize, draft, search).
- **What sources were used:** count and references to resource types (SharePoint/Email/Teams).
- **What boundaries applied:** whether any policy restricted access (PolicyDetails present). [page:19]
- **What confidence was assigned:** band + reason codes (optional).
- **What happened next:** allow vs escalate.

---

## 4) Escalation triggers (Zone 1)

Even in Zone 1, certain events should escalate to Zone 2/3 processes:

### 4.1 Mandatory escalation triggers
- Any attempt to access Restricted/Highly Confidential label classes (if observable)
- Any policy restriction/block in `PolicyDetails` for sensitive content [page:19]
- Any prompt jailbreak attempt flagged via `Messages[].JailbreakDetected == true` [page:19]
- Any cross prompt injection flag via `AccessedResources[].XPIADetected == true` [page:19]
- Repeated low-confidence outcomes for the same user/session (pattern)

### 4.2 Routing
- Escalate to: Compliance/SecOps queue depending on category
- SLA: 1 business day (Zone 1), unless it’s a security signal (then treat as S1/S2)

---

## 5) Audit query standard (how to retrieve evidence)

Microsoft states you can access Copilot audit logs in the Purview portal (Audit) and filter using **Activities – operation names** (Operation/RecordType/Workload), and if you need to filter by AppIdentity you export and filter offline. [page:19]

Minimum saved query:
- Operation = `CopilotInteraction`
- Workload = `Copilot`
- Time window = last 7 days
- Export cadence = weekly for baseline governance sampling

---

## 6) Reporting metrics (Zone 1 dashboard slice)

Weekly:
- total interactions (Zone 1)
- top hosts (Teams/Word/etc.)
- policy blocks count
- jailbreak / XPIA counts
- escalation events count
- “unknown agent_id” rate (if some events do not include agent identity)

---

## 7) Testing plan (minimum)

- Verify CopilotInteraction audit events are visible for Zone 1 users. [page:19]
- Verify `AccessedResources` appears for interactions that use internal content. [page:19]
- Trigger a known DLP/policy block scenario and verify PolicyDetails is logged. [page:19]
- Confirm that Zone 1 custom logging does not store prompt/response content by default.

---

## 8) Done criteria

- Zone 1 evidence records exist and can be produced for any date range via audit export.
- Escalation triggers are documented and route correctly.
- Privacy sign-off exists for the logging scope (especially if any content capture is enabled).
- Governance can demonstrate it is "monitoring and supervising" AI usage at a baseline level consistent with SEC 2026 priorities language. [page:18]

---

*FSI Agent Governance Framework v1.2 - January 2026*