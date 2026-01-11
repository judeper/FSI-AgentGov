# Template: Per-Agent Data Handling Policy (PDHP)

**Purpose:** Define, per agent, what data it can access, how it can use it, and what protections apply (labels, DLP, retention, eDiscovery posture).  
**Applies to:** All zones (Zone 1–3), with the strictest requirements in Zone 3.  
**Microsoft grounding:** Microsoft Purview provides data security/compliance controls for Copilot and agents, including sensitivity labels, DLP, auditing, eDiscovery, and retention for AI interactions. [page:9]  
**Audit grounding:** Purview audit logs for Copilot/AI interactions include references to accessed resources and their sensitivity labels (SensitivityLabelId) and policy block details (PolicyDetails). [page:10]  
**Related controls (examples):** 1.5 DLP & sensitivity labels, 1.6 Purview DSPM for AI, 1.9 retention, 4.1 SharePoint IAG, 3.3 compliance reporting. [page:3]

---

## 1) Policy metadata

- **Agent name:**
- **Agent ID:**
- **Agent version:**
- **Zone:** Zone 1 / Zone 2 / Zone 3
- **Governance level:** Baseline / Recommended / Regulated
- **Business owner:**
- **Technical owner:**
- **Data owner(s):**
- **Compliance approver:**
- **Effective date:**
- **Next review date:** (recommended: quarterly for Zone 3)

---

## 2) Data classification model used

### Sensitivity labels in scope
List your org’s labels (example only):
- Public
- Internal
- Confidential
- Restricted / Highly Confidential
- Regulated (GLBA/PII), etc.

> Microsoft Purview integrates with sensitivity labels and enforces access controls such that AI apps won’t return data a user doesn’t have access to, with additional protections when encryption/labels are used. [page:9]

### Sensitive information types (SITs) / classifiers in scope
- (e.g., SSN, account numbers, credit card, taxpayer ID, etc.)

---

## 3) Allowed data sources (positive allowlist)

Only list the sources the agent may use.

| Source type | Source location / scope | Allowed labels | Allowed operations | Notes |
|---|---|---|---|---|
| SharePoint | `https://tenant.sharepoint.com/sites/...` | Internal, Confidential | Read | Restricted excluded |
| OneDrive | By user scope | Internal only | Read | No cross-user access |
| Dataverse | Environment: Prod | Internal | Create draft | No delete |
| Exchange/Outlook | Mailbox items | Internal | Summarize | No external send |

---

## 4) Prohibited data sources (deny list)

| Source type | Scope | Reason | Enforcement |
|---|---|---|---|
| SharePoint | HR site collection | Privacy | Restricted discovery + deny |
| External web | Any | Data leakage risk | Disable web search/plugin |
| Personal storage | Any | Unmanaged | Block via policy |

---

## 5) Label handling rules (what the agent may do with labeled content)

> Purview audit logs can include AccessedResources with SensitivityLabelId and PolicyDetails when access is restricted/blocked, which supports evidencing policy enforcement. [page:10]

### 5.1 Read rules (retrieval)
| Label | Agent may retrieve? | Conditions |
|---|---|---|
| Public | Yes | — |
| Internal | Yes | — |
| Confidential | Yes | Only Zone 2/3; log sources |
| Restricted | No (default) | Only with explicit exception + approval |

### 5.2 Write rules (generation/storage)
| Label | Agent may create content at this label? | Conditions |
|---|---|---|
| Internal | Yes | Auto-apply label where possible |
| Confidential | Yes (Zone 3 only) | Must log decision + sources |
| Restricted | No | Human-only |

### 5.3 Redaction / masking rules
- List what must be masked in outputs (e.g., SSN, full account numbers).
- Specify whether partial display is allowed (last 4 digits only).

---

## 6) DLP policy requirements

> Microsoft Purview DLP can monitor and help protect against leakage of sensitive information, and can also apply to AI interactions depending on configuration and supported apps. [page:9]

- **DLP policies required for this agent:** (names/IDs)
- **Block vs warn vs allow-override:** (per DLP rule)
- **Override policy:** who can override, what must be logged, and duration.

---

## 7) AI interaction logging requirements

> Microsoft Purview auditing captures user interactions with Copilot/AI apps and includes references to resources Copilot accessed, including sensitivity labels. [page:10]

### Minimum logging (all zones)
- agent_id / agent_version
- interaction timestamp
- user identifier (pseudonymous where possible)
- accessed resource references (IDs/URLs) where available
- decision log record ID (if applicable)

### Zone 3 additional logging
- decision reasoning logs (schema)
- confidence band and routing
- scope drift events and alerts
- policy blocks (PolicyDetails) references

---

## 8) Retention, eDiscovery, and records posture

> Microsoft Purview supports auditing, eDiscovery, and retention for AI interactions, including prompts/responses stored and searchable for compliance and investigations. [page:9]

- **Decision log retention period:** (e.g., 7 years / per SEC 17a-4-like policy if applicable)
- **AI interaction retention period:** (per org policy)
- **eDiscovery hold process:** (who can place holds, escalation trigger)
- **Record declaration rules:** (if applicable)

---

## 9) Data residency and US-only scope statement

- **Deployment region(s):** (US-only)
- **Cross-border restrictions:** (state “not permitted” unless explicitly approved)
- **Third-party processing:** list if any (LLM endpoints, vendors) and tie to supply chain register.

---

## 10) Risk review checklist (required before production)

- [ ] Allowed data sources are explicitly enumerated (no wildcards).
- [ ] Prohibited sources are explicitly blocked (technical + policy).
- [ ] Label rules defined for read/write.
- [ ] DLP rules verified with test events.
- [ ] Logging is enabled and verifiable via audit search.
- [ ] Retention and eDiscovery posture defined and tested.

---

## 11) Approvals and versioning

- **Policy version:**
- **Approved by (Data owner):**
- **Approved by (Compliance/Risk):**
- **Approved by (Platform owner):**
- **Approval date:**
- **Change record (ticket/PR):**