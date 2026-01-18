# Template: Supply Chain / Third-Party AI Risk Register Entry (AI-TPRM)

**Purpose:** Document third-party AI dependencies (models, endpoints, plugins, connectors, tools, data providers) and the governance controls needed to manage operational, security, compliance, and resilience risk.  
**Applies to:** Zone 3 agents (required); Zone 2 where third-party components process sensitive data or influence consequential decisions.  
**Regulatory driver (FINRA):** FINRA’s 2026 oversight messaging on GenAI highlights that firms remain responsible for regulatory obligations even when GenAI is sourced via third-party vendors and emphasizes governance/testing/monitoring expectations, including for AI agents. [web:21]  
**Regulatory driver (SEC):** SEC 2026 priorities emphasize AI as a cross-cutting risk area and highlight third-party vendor management as part of operational resiliency and cybersecurity expectations. [web:92]  
**Related controls (examples):** 2.7 Vendor and Third-Party Risk Management, 2.4 BC/DR, 2.3 Change management, 1.7 Audit logging, 3.3 Compliance reporting. [page:3]

---

## 1) Registration metadata

- **Register entry ID:**
- **Agent(s) impacted:** (IDs/names)
- **Zone:** Zone 2 / Zone 3
- **Owner (TPRM):**
- **Owner (Engineering):**
- **Compliance approver:**
- **Effective date:**
- **Review cadence:** (recommended: quarterly; monthly for critical dependencies)

---

## 2) Third-party component identification

| Component category | Vendor / provider | Component name | Purpose | Criticality (Low/Med/High) |
|---|---|---|---|---|
| LLM endpoint | | | | |
| Plugin / connector | | | | |
| Retrieval store | | | | |
| Data provider | | | | |
| Evaluation/red-team tooling | | | | |
| Hosting / cloud | | | | |

---

## 3) Data processing and access

- **Data classes processed:** (Public/Internal/Confidential/Restricted/PII/GLBA/etc.)
- **Data residency:** (US-only required? yes/no)
- **Does vendor receive prompts/responses?** (Yes/No/Unknown)
- **Does vendor log prompts/responses?** (Yes/No/Configurable/Unknown)
- **Training use:** Are prompts/outputs used for training? (Yes/No/Opt-out/Unknown)
- **Subprocessors:** list known subprocessors or link to vendor subprocessor page.

---

## 4) Security and compliance controls (evidence required)

### Vendor controls checklist
- [ ] SOC 2 Type II (or equivalent)
- [ ] ISO 27001 (optional)
- [ ] Pen test summary / vuln mgmt process
- [ ] Encryption at rest/in transit
- [ ] Access controls and least privilege
- [ ] Incident response SLA + notification terms

### Contractual clauses checklist
- [ ] Data use limitations (no training unless explicitly allowed)
- [ ] Breach notification timelines
- [ ] Right to audit / evidence provision
- [ ] Subprocessor controls
- [ ] Termination + data deletion requirements

---

## 5) Operational resiliency (BC/DR)

SEC priorities emphasize operational resiliency and vendor management as an examination area, including third-party oversight. [web:92]

- **Dependency type:** (critical path vs non-critical)
- **RTO / RPO expectations:**
- **Failover plan:** (alternate vendor/model, degrade-to-read-only, disable actions, etc.)
- **Runbook link:** (incident response + rollback)
- **Tabletop exercise date:**
- **Last incident date:** (if any)

---

## 6) Change management triggers (when re-approval is required)

Re-approval required if any of the following changes occur:
- new model version or major behavior change
- new subprocessor
- new region/data residency change
- new logging/training terms
- new plugin/connector permissions
- pricing/quotas that affect availability

- **Re-approval workflow link:** (ticket/PR)
- **Decision authority:** (TPRM + Compliance + Platform Owner)

---

## 7) Risk assessment (qualitative + scoring)

### Risk categories (rate each Low/Med/High)
- Confidentiality:
- Integrity:
- Availability:
- Privacy:
- Regulatory/recordkeeping:
- Model risk / hallucination:
- Bias/fairness (if applicable):

### Overall risk rating
- **Overall:** Low / Medium / High
- **Rationale:**

---

## 8) Monitoring requirements

FINRA highlights the need for ongoing monitoring and governance for GenAI and AI agents. [web:21]

- **What will be monitored:** uptime, error rates, response latency, policy blocks, drift indicators.
- **Alert thresholds:** (define)
- **Reporting cadence:** weekly/monthly
- **Owner:** (who triages)

---

## 9) Evidence pack links (attach artifacts)

- Vendor due diligence packet:
- Contract summary:
- Security review:
- DR runbook:
- Monitoring dashboard link:
- Last quarterly review notes:

---

## 10) Approval record

- **Approved by (TPRM):**
- **Approved by (Compliance/Risk):**
- **Approved by (Security):**
- **Approved date:**
- **Version:**
- **Next review date:**