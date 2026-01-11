# Template: Decision Log Schema (Reasoning + Confidence)

**Purpose:** Define a *structured*, auditable “decision object” for each material agent recommendation or action, so you can evidence supervision, traceability, and review outcomes.  
**Applies to:** Zone 3 (required), Zone 2 (recommended for medium/high impact agents).  
**Related controls (examples):** 1.7 Audit logging, 2.5 QA/validation, 2.9 Performance monitoring, 3.2 Usage analytics, 3.3 Compliance reporting. [page:3]

> Implementation note (Copilot Studio): Copilot Studio activities are available in Microsoft Purview Audit, and user interaction events (CopilotInteraction) include a transcript thread ID; full chat text is not in the Purview Audit event itself and is retrieved via DSPM for AI in supported scenarios. [page:6]  
> Implementation note (DSPM for AI): DSPM for AI depends on Purview auditing being enabled and has prerequisites and collection/policy concepts that affect whether prompt/response content is captured and visible. [page:7]

---

## 1) Decision object (logical schema)

Store this record in a tamper-evident store (e.g., append-only log, immutable storage, or equivalent) and link it to:
- the relevant Purview Audit event(s)
- the agent version/release
- any case/ticket created by escalation

### 1.1 Required fields (minimum viable)

| Field | Type | Required | Description |
|---|---|---:|---|
| decision_id | string (UUID) | Yes | Unique identifier for this decision record |
| timestamp_utc | datetime | Yes | When the agent produced the recommendation/action |
| agent_id | string | Yes | Unique agent identifier (tie to inventory) |
| agent_name | string | Yes | Human-readable name |
| agent_version | string | Yes | Release/version of agent configuration |
| zone | enum | Yes | Zone1 / Zone2 / Zone3 |
| governance_level | enum | Yes | Baseline / Recommended / Regulated |
| request_id | string | Yes | Correlation ID across logs/telemetry |
| user_id_hash | string | Yes | Pseudonymous user identifier (minimize PII) |
| user_role | string | Yes | Role/category (e.g., Advisor, Analyst, Ops) |
| channel | string | Yes | Where interaction happened (Teams, M365 Copilot, etc.) |
| decision_type | enum | Yes | Inform / Recommend / Execute / Block / Escalate |
| summary_of_request | string | Yes | Short, PII-minimized description of intent |
| knowledge_sources | array<object> | Yes | What sources were used (IDs/URLs), not necessarily content |
| policy_ids_invoked | array<string> | Yes | Policy/prompt policy IDs or control references invoked |
| output_category | enum | Yes | e.g., “customer comms”, “research”, “ops”, “policy”, “code” |
| action_attempted | boolean | Yes | True if the agent attempted an action/tool call |
| action_result | enum | Yes | Allowed / Blocked / NeedsApproval / Executed / Failed |
| confidence_band | enum | Yes | High / Medium / Low |
| uncertainty_reason_codes | array<string> | No | Categorize uncertainty (missing data, conflicting sources, etc.) |
| human_review_required | boolean | Yes | Derived from zone + confidence + action type |
| human_review_outcome | enum | No | Approved / Rejected / Modified / NotRequired |
| reviewer_id_hash | string | No | Pseudonymous reviewer identifier |
| escalation_ticket_id | string | No | Link to case/ticket if escalated |
| retention_tag | string | Yes | Retention category/tag for the decision record |
| sensitivity_context | object | Yes | Labels/classes encountered (no content) |

### 1.2 Recommended fields (audit depth)

| Field | Type | Description |
|---|---|---|
| prompt_policy_version | string | Version of policy/ruleset used |
| model_or_system_fingerprint | string | A fingerprint of the underlying system/config (if available) |
| tool_calls | array<object> | Captures tool/connector calls (names + targets + result) |
| data_minimization_notes | string | What was intentionally not collected or logged |
| exception_flags | array<string> | e.g., “scope_drift_detected”, “dlp_rule_match” |
| related_audit_event_ids | array<string> | Purview Audit event IDs / correlation |

---

## 2) Field definitions (recommended object shapes)

### 2.1 knowledge_sources (array of objects)
Each entry should look like:

- source_type: SharePoint / File / Site / Dataverse / Web / InternalKB
- source_id: stable ID (URL, GUID, item ID)
- label: sensitivity label (if known)
- access_mode: Read / Write / Execute
- retrieval_method: Search / Explicit / RAG / DirectLink

### 2.2 sensitivity_context (object)
- labels_seen: array<string>
- dlp_rule_matches: array<string>
- restricted_sites_accessed: array<string>
- pii_detected: boolean (if known via tooling)

---

## 3) Confidence policy (how to use confidence_band)

### 3.1 Default routing policy (recommended)
- Zone 3:
  - Execute decision_type requires **High** confidence AND action must be allowed by the Action Authorization Matrix.
  - Low confidence => must escalate and block auto-execution.
- Zone 2:
  - Recommendations allowed, but Low confidence => escalate to reviewer.
- Zone 1:
  - Confidence captured as a band; no autonomous execution.

(Adjust these rules per your framework and risk appetite.)

### 3.2 Calibration and review cadence
- Define how confidence bands are assigned (heuristic vs model-provided).
- Define monthly/quarterly calibration reviews with sample-based evaluation.

---

## 4) Integration with Purview Audit and DSPM for AI

Copilot Studio audit events are available in Microsoft Purview Audit, and user interaction events include metadata such as organization, user/resource IDs, and a transcript thread ID. [page:6]  
The audit event itself does not contain the full transcript text; DSPM for AI can retrieve chat text related to certain events and surface resource links where supported. [page:6]  
DSPM for AI prerequisites include Purview auditing being enabled and licensing/permissions requirements, and content capture depends on the policy configuration. [page:7]

### 4.1 Recommended linkage fields
- purview_operation: e.g., `CopilotInteraction` (for interactions) [page:6]
- purview_event_id: the audit log entry GUID (if captured)
- transcript_thread_id: if present in event metadata [page:6]

---

## 5) Example JSON (for implementation)

> Use this as a structural example only; do not log sensitive content unless policy explicitly allows it.

```json
{
  "decision_id": "2d5e9b3a-7a1e-45d5-9b57-3fe2b2d7c6aa",
  "timestamp_utc": "2026-01-10T23:05:11Z",
  "agent_id": "AGT-000123",
  "agent_name": "PolicyAssist-Z3",
  "agent_version": "2026.01.0",
  "zone": "Zone3",
  "governance_level": "Regulated",
  "request_id": "REQ-9f0c6c1a",
  "user_id_hash": "u:9af3e1...",
  "user_role": "ComplianceAnalyst",
  "channel": "Teams",
  "decision_type": "Recommend",
  "summary_of_request": "Summarize policy differences for retention settings.",
  "knowledge_sources": [
    {
      "source_type": "SharePoint",
      "source_id": "https://tenant.sharepoint.com/sites/policies/...",
      "label": "Confidential",
      "access_mode": "Read",
      "retrieval_method": "Search"
    }
  ],
  "policy_ids_invoked": ["POL-RETENTION-001", "CTRL-1.7", "CTRL-1.9"],
  "output_category": "policy",
  "action_attempted": false,
  "action_result": "Allowed",
  "confidence_band": "Medium",
  "human_review_required": true,
  "retention_tag": "FSI-DecisionLogs-7Y",
  "sensitivity_context": {
    "labels_seen": ["Confidential"],
    "dlp_rule_matches": [],
    "restricted_sites_accessed": [],
    "pii_detected": false
  },
  "related_audit_event_ids": ["a8e2d1f7-..."]
}
6) Approval and lifecycle
Owner (Compliance):

Owner (Engineering):

Approved date:

Version:

Next review:

Changes to the schema should be treated like a governed interface (versioned, backward-compatible where possible) to preserve audit continuity.