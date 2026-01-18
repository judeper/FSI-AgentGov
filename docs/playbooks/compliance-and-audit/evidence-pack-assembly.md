text
# Spec: Evidence Pack Assembly (Exam-Ready Bundle)

**Purpose:** Define a repeatable process to assemble an audit/exam-ready evidence pack for a given agent, date range, or regulatory request—linking together inventory, audit logs, decision logs, approvals, test results, and governance artifacts.  
**Applies to:** Zone 3 (required for every agent), Zone 2 (recommended for medium/high impact).  
**Regulatory driver:** FINRA emphasizes that firms must maintain books and records relating to GenAI use and highlights supervision/oversight expectations under FINRA Rule 3110, including testing, monitoring, and logging of AI agent activities. [web:21]  
**SEC driver:** SEC 2026 priorities expand scrutiny of AI usage and emphasize that examiners will evaluate whether firms have procedures to monitor/supervise AI, including for internal operations. [web:92]

---

## 1) What is an "evidence pack"?

An evidence pack is a **curated folder/bundle** containing:
- **who** (agent identity + owners),
- **what** (actions taken + data accessed),
- **when** (date range),
- **how** (decision reasoning + confidence),
- **controls** (what boundaries/policies applied),
- **approvals** (who authorized what),
- **testing** (how controls were validated),
- **escalations** (what went wrong + remediation).

It is designed to answer an examiner's question: *"Show me how you govern this agent."*

---

## 2) When to assemble an evidence pack

### 2.1 Scheduled (proactive)
- **Quarterly** for every Zone 3 agent (regulatory readiness)
- **Semiannually** for Zone 2 agents that touch Confidential data

### 2.2 Event-triggered (reactive)
- Regulatory exam/request
- Internal audit
- Major incident (S1 escalation)
- Agent version change or material scope change
- Third-party vendor audit

---

## 3) Evidence pack structure (recommended folder layout)

/evidence-packs/
/<agent-id>-<agent-name>-<YYYY-MM>/
01-SUMMARY.md
02-IDENTITY/
agent-inventory-entry.md
action-authorization-matrix.md
per-agent-data-policy.md
escalation-matrix.md
03-APPROVALS/
business-owner-approval.pdf
compliance-approval.pdf
change-tickets-summary.md
04-AUDIT-LOGS/
purview-copilot-interactions-export.csv
audit-query-metadata.md
05-DECISION-LOGS/
decision-log-export.json
decision-log-schema.md
sample-redacted-decisions.md
06-TESTING/
negative-test-results.md
positive-test-results.md
drift-detection-tests.md
07-MONITORING/
dashboard-snapshot.pdf
drift-events-summary.md
escalation-summary.md
08-INCIDENTS/
s1-incidents-summary.md
remediation-tickets.md
root-cause-analysis.md
09-RISK-ASSESSMENTS/
supply-chain-risk-entry.md
bias-fairness-assessment.md (if applicable)
threat-model.md
10-REGULATORY-MAPPINGS/
finra-control-mapping.md
sec-control-mapping.md
colorado-impact-assessment.md (if applicable)

text

---

## 4) Content requirements (per section)

### 4.1 SUMMARY (01-SUMMARY.md)
One-page executive summary:
- Agent name, ID, version
- Zone + governance level
- Business use case
- Date range of evidence
- Key metrics (interactions, policy blocks, escalations)
- Material changes in the period
- Compliance posture statement (green/yellow/red)

### 4.2 IDENTITY (02-IDENTITY/)
Include the four core templates:
- **Agent Inventory Entry** (from `templates/agent-inventory-entry.md`)
- **Action Authorization Matrix** (from `templates/action-authorization-matrix.md`)
- **Per-Agent Data Policy** (from `templates/per-agent-data-policy.md`)
- **Escalation Matrix** (from `templates/escalation-matrix.md`)

All must be current versions as of the evidence date.

### 4.3 APPROVALS (03-APPROVALS/)
Evidence of authorization:
- Business owner sign-off (go-live, quarterly review)
- Compliance/Risk approval
- Security review sign-off
- Change management tickets/PRs for material changes
- Version history log

### 4.4 AUDIT LOGS (04-AUDIT-LOGS/)
Purview Copilot audit export for the date range:
- Export metadata: query used, date range, export date, who ran it
- CSV/JSON of `CopilotInteraction` events filtered by `AgentId` (if available) [page:19]
- Include fields: `AgentId`, `AgentName`, `AgentVersion`, `AccessedResources`, `SensitivityLabelId`, `PolicyDetails`, `JailbreakDetected`, `XPIADetected` [page:19]
- Redacted sample rows (3–5 examples) for quick review

Microsoft Purview audit logs for Copilot/AI interactions include `AccessedResources` with sensitivity label IDs and policy restriction details, making them the canonical "what happened" source. [page:19]

### 4.5 DECISION LOGS (05-DECISION-LOGS/)
Structured reasoning logs (from `templates/decision-log-schema.md`):
- Export of decision log records for the date range
- Schema documentation
- Sample redacted decision records (3–5 examples showing High/Med/Low confidence routing)
- Correlation to audit event IDs where possible

### 4.6 TESTING (06-TESTING/)
Validation evidence:
- **Negative tests:** attempts to violate AAM/PDHP/boundaries → blocked + logged
- **Positive tests:** allowed actions work as expected
- **Drift detection tests:** new connector/scope attempt → detected + alerted
- Test dates, testers, pass/fail results

### 4.7 MONITORING (07-MONITORING/)
Continuous controls evidence:
- Dashboard snapshot (from `specs/real-time-compliance-dashboard.md`)
- Drift events summary (from `specs/scope-creep-detection.md`)
- Escalation summary (from `templates/escalation-matrix.md`)
- SLA adherence metrics

### 4.8 INCIDENTS (08-INCIDENTS/)
If any S1/S2 events occurred:
- Incident summaries
- Root cause analysis (from control 3.4) [page:3]
- Remediation/CAPA tickets
- Lessons learned

### 4.9 RISK ASSESSMENTS (09-RISK-ASSESSMENTS/)
Supporting risk artifacts:
- Supply chain risk register entry (from `templates/supply-chain-risk-register-entry.md`)
- Bias/fairness assessment (from control 2.11) [page:3]
- Threat model / security review
- BC/DR assessment

### 4.10 REGULATORY MAPPINGS (10-REGULATORY-MAPPINGS/)
Explicit control-to-regulation mapping:
- FINRA: which controls map to Rule 3110 supervision, recordkeeping (4510/4511), communications (2210)
- SEC: which controls map to Advisers Act 206(4)-7 compliance rule, recordkeeping
- Colorado AI Act: impact assessment if applicable (from `templates/colorado-ai-impact-assessment.md`)

---

## 5) Assembly checklist (per agent, per period)

- [ ] Evidence date range defined (start/end)
- [ ] All 10 sections populated
- [ ] Redactions complete (no unintended PII/confidential content)
- [ ] Cross-references verified (decision log IDs ↔ audit event IDs)
- [ ] Approvals signed and dated
- [ ] Version numbers match (agent version in inventory = version in logs)
- [ ] Evidence stored immutably (append-only / restricted access)
- [ ] Access log for the evidence pack itself (who viewed when)

---

## 6) Automation opportunities (roadmap)

- **Auto-export:** scheduled Purview audit queries + decision log exports
- **Auto-populate:** inventory/AAM/PDHP from governance repository
- **Auto-snapshot:** dashboard metrics on last day of quarter
- **Auto-package:** zip/PDF bundle with table of contents

Even with automation, manual QA + redaction review is required.

---

## 7) Retention and access

- **Retention:** align to your records policy (typically 7 years for regulated FSI records)
- **Access controls:** Compliance + Audit + Legal only; time-boxed access for external auditors
- **Immutability:** evidence packs should be stored in append-only or WORM storage
- **Audit trail:** log who accessed which pack when

FINRA emphasizes books and records requirements and supervision/recordkeeping obligations related to GenAI. [web:21]

---

## 8) "Done" criteria

An evidence pack is complete when:
- A compliance officer or auditor can open the folder and understand the agent's governance posture in < 30 minutes.
- Every claim in the SUMMARY is supported by artifacts in the other 9 sections.
- All artifacts are current as of the evidence date.
- The pack can be handed to an examiner with confidence.

---

## 9) Example SUMMARY snippet

```markdown
# Evidence Pack Summary

**Agent:** PolicyAssist-Z3 (AGT-000123)  
**Version:** 2026.01.0  
**Zone:** Zone 3 (Enterprise Managed)  
**Governance Level:** Regulated/High-Risk  
**Evidence Period:** 2025-10-01 to 2025-12-31 (Q4 2025)  

## Key Metrics (Q4 2025)
- Total interactions: 1,247
- Unique users: 38
- Confidential label access events: 203
- Policy blocks: 4 (all expected; no violations)
- Drift events: 0
- Escalations: 1 (S2, resolved in SLA)
- Low confidence interactions: 12 (all reviewed and approved)

## Compliance Posture: GREEN
- All controls operational
- No material findings
- Quarterly review complete (approved 2026-01-05)