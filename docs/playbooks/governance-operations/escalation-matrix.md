# Template: Escalation Decision Matrix (EDM)

**Purpose:** Define auditable escalation triggers, routing, SLAs, and approval authority for agent behaviors—especially where agents may touch sensitive data or take actions.  
**Applies to:** Zone 2 (recommended) and Zone 3 (required).  
**Regulatory driver:** FINRA emphasizes that GenAI can implicate supervision and recordkeeping and highlights the need for governance, testing, and ongoing monitoring (including prompt/output logs, model version tracking, and human-in-the-loop review). [page:8]  
**Related controls (examples):** 2.12 Supervision & Oversight, 3.4 Incident Reporting/RCA, 1.7 Audit logging, 3.3 Compliance reporting. [page:3]

---

## 1) Matrix metadata

- **Matrix name:** (e.g., “Zone 3 Autonomous Agents – Escalation Matrix”)
- **Business unit / function:**
- **Applies to agent(s):** (IDs/names)
- **Zone:** Zone 2 / Zone 3
- **Governance level:** Recommended / Regulated
- **Owner (Compliance):**
- **Owner (Engineering/Platform):**
- **Approver (Risk/Legal):**
- **Effective date:**
- **Next review date:** (recommended: quarterly for Zone 3)

---

## 2) Severity model (choose one and standardize)

### Option A: 3-level severity (simple)
- **S1 (Critical):** Immediate customer/regulatory harm likely, or security breach indicators.
- **S2 (High):** Material policy violation, sensitive data exposure risk, repeated failures.
- **S3 (Medium):** Non-material issue, degraded performance, isolated minor policy warnings.

### Option B: 4-level severity (more granular)
- **P0 / P1 / P2 / P3** (incident-response style)

Pick one model for the entire program to ensure reporting consistency.

---

## 3) Escalation triggers table (core of the matrix)

| Trigger category | Trigger condition (objective) | Severity | Auto action | Escalate to (role) | SLA | Required evidence |
|---|---|---:|---|---|---|---|
| Unauthorized action | Agent attempts prohibited action from AAM | S1 | Block + alert | Compliance On-Call + SecOps | 15 min | Decision log + audit event IDs |
| Scope drift | New connector/data scope detected (not approved) | S1 | Block + alert | SecOps + Platform Owner | 30 min | Drift signal + baseline |
| Sensitive data event | Confidential/Restricted label accessed unexpectedly | S1 | Alert; optional block | Data Protection Officer | 30 min | DLP match + resource IDs |
| Low confidence | confidence_band = Low for “recommend/execute” | S2 | Require human review | Assigned Reviewer | 4 hrs | Decision log + rationale |
| Hallucination risk | Conflicting sources or “unsupported claim” flags | S2 | Require review | SME Reviewer | 8 hrs | Source list + output category |
| High volume | Rate anomaly exceeds threshold | S2 | Throttle | Platform Owner | 4 hrs | Telemetry + threshold |
| Repeated minor issues | 3+ S3 within 7 days | S2 | Review required | Compliance Lead | 1 biz day | Summary report |
| Policy exception request | User requests override | S2 | Block until approved | Approver role | 1 biz day | Override request record |
| Minor QA issue | Non-critical formatting/UX defect | S3 | Log only | Product Owner | 5 biz days | Issue ticket |

**Notes**
- “Trigger condition” must be measurable (avoid subjective language).
- “Auto action” must be explicit (Block, Throttle, Require Review, Log Only).
- “Required evidence” must reference the specific logs/artifacts (Gap 2 decision log + Purview audit references where applicable).

---

## 4) Routing map (who gets notified)

### Routing roles (fill in with org-specific groups)
- **Compliance on-call:** (name / DL / Teams channel)
- **SecOps on-call:** (name / DL / Teams channel)
- **Data Protection:** (name / DL)
- **Business owner:** (name / DL)
- **Model/AI owner:** (name / DL)
- **Legal:** (name / DL)
- **Incident commander:** (name / DL)

### Notification channels
- Teams channel:
- Email distribution list:
- Ticketing system queue:
- Pager/on-call tool:

---

## 5) Override policy (how exceptions are handled)

FINRA notes that supervisory systems must be tailored and that firms should consider integrity/reliability/accuracy where AI is used, with ongoing monitoring and human-in-the-loop review. [page:8]  
Overrides must therefore be rare, explicit, and auditable.

- **What can be overridden?** (e.g., throttling, non-critical blocks)
- **What cannot be overridden?** (e.g., prohibited actions, sensitive data boundary violations)
- **Approval authority:** (role-based)
- **Override duration:** (time-boxed)
- **Logging:** every override generates a decision log record + ticket.

---

## 6) Evidence bundle checklist (for audits/exams)

For each S1/S2 escalation:
- [ ] Decision log record ID(s)
- [ ] Audit log event reference(s)
- [ ] Scope baseline reference (if drift)
- [ ] AAM clause reference (if unauthorized action)
- [ ] Ticket ID and timestamps (SLA evidence)
- [ ] Root cause analysis summary (if incident)
- [ ] Corrective action + prevention (CAPA) entry

---

## 7) Operational metrics (monthly reporting)

- Count of S1/S2/S3 events by agent and category
- SLA adherence (met vs missed)
- Override rate
- Repeat event rate (“recurrence”)
- Mean time to detect (MTTD) and mean time to respond (MTTR)

These feed the “Real-time Compliance Dashboard” spec (Gap 7) and compliance reporting controls in your Reporting pillar. [page:3]

---

## 8) Approvals and versioning

- **Version:**
- **Approved by (Compliance):**
- **Approved by (Risk/Legal):**
- **Approved by (Platform owner):**
- **Approval date:**
- **Change record (ticket/PR):**