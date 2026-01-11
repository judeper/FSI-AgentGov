# Template: Agent Action Authorization Matrix (AAM)

**Purpose:** Provide an auditable, enforceable definition of what an agent *may* and *may not* do, including hard limits and escalation triggers.  
**Applies to:** Zone 3 agents by default; Zone 2 agents when they can initiate workflows/actions or touch sensitive systems/data.  
**Related controls (examples):** 1.14 (Agent scope control), 1.18 (RBAC), 2.12 (Supervision & oversight), 3.1 (Inventory/registration). [page:3]

---

## 1) Agent identity

- **Agent name:**
- **Agent ID (unique):**
- **Agent type:** (M365 Copilot Agent / Copilot Studio Agent used with M365 Copilot)
- **Owner (business):**
- **Owner (technical):**
- **Approver (Compliance/Risk):**
- **Zone:** (Zone 1 / Zone 2 / Zone 3)
- **Governance level:** (Baseline / Recommended / Regulated)
- **Production status:** (Draft / Pilot / Production / Retired)
- **Last reviewed date:**
- **Next review date:** (recommended: quarterly for Zone 3)

---

## 2) Intended purpose and boundaries

### Intended purpose (one paragraph)
Describe what the agent is supposed to do and for whom.

### Out-of-scope behaviors (bullet list)
- Examples: “Cannot provide investment advice”, “Cannot approve credit”, “Cannot contact customers directly”, “Cannot change records”.

---

## 3) Authorized capabilities (Allowed actions)

List actions the agent is explicitly authorized to perform.

| Action category | Action | Target system | Preconditions | Evidence/log requirement |
|---|---|---|---|---|
| Read | Read documents | SharePoint site(s): ___ | User has access + label allowed | Log: resource ID + label |
| Generate | Draft summary | Word/Outlook | Non-confidential only | Log: prompt category + output category |
| Workflow | Create a draft case | Case mgmt tool | Must assign to human reviewer | Log: case ID + reviewer |
| Notify | Notify compliance queue | Teams/Email | Only approved distribution list | Log: notification ID |

**Notes**
- “Action category” should align to a simple taxonomy: **Read / Write / Execute / Notify / Approve / Block / Escalate**.
- Prefer **draft** creation over **final execution** for regulated decisions.

---

## 4) Prohibited capabilities (Disallowed actions)

Explicitly list what the agent must never do.

| Prohibited action | Reason | Enforcement mechanism | Detection/alert |
|---|---|---|---|
| Execute financial transaction | Customer harm + control bypass | Technical block (no connector permission) | Alert if attempted |
| Modify official records | Recordkeeping integrity | Role denies write | Sentinel alert |
| Delete logs | Audit destruction | WORM store + no delete perms | Alert + incident |
| Access HR/medical data | Privacy/HIPAA concerns | DLP + restricted discovery | Alert if access attempted |

---

## 5) Connector / tool authorization (technical scope)

### Allowed connectors / integrations
List **only** approved connectors/tools.

| Connector/tool | Environment | Allowed operations | Data classes allowed | Notes |
|---|---|---|---|---|
| Microsoft Graph | Prod | Read only | Internal / Confidential? | Restrict endpoints |
| SharePoint | Prod | Read + Draft write | By label rules | Restrict sites |
| Dataverse | Prod | Create draft row | Internal only | No delete |

### Denied connectors / integrations
- List explicitly (e.g., “No external web browsing”, “No personal email”, “No consumer storage”).

---

## 6) Data access policy (high-level reference)

Point to the agent’s detailed data policy (Template: Per-agent Data Handling Policy).
- **Data policy link:** `../templates/per-agent-data-policy.md` (or your final location)

---

## 7) Hard limits (guardrails that cannot be overridden)

| Limit type | Limit | Rationale | Enforcement |
|---|---|---|---|
| Rate limit | Max ___ actions/min | Prevent runaway automation | Platform throttling |
| Dollar limit | Max $___ per day | Risk control | Workflow approval gate |
| Scope limit | Only business unit ___ | Least privilege | Environment scoping |
| Time limit | Only business hours | Reduce unattended risk | Scheduler constraint |
| Volume limit | Max ___ notifications/hour | Avoid alert fatigue | Rate limiter |

---

## 8) Human oversight + escalation triggers

### Escalation triggers (examples)
- Any “Execute” action attempted
- Any access to Confidential/Restricted labels
- Any confidence level = Low
- Any scope drift detected
- Any policy violation

### Escalation routing
- **Primary reviewer role:**
- **Secondary reviewer role:**
- **On-call / after-hours route:**
- **SLA for response:**
- **Fallback if SLA missed:**

(Reference the Escalation Decision Matrix template.)

---

## 9) Logging and evidence requirements

> Copilot Studio activities can be audited via Microsoft Purview audit logs, with additional transcript access via DSPM for AI in some cases. [web:112][web:107]

Minimum evidence for Zone 3:
- Audit logging enabled and verified (Purview audit). [web:112]
- Decision logs (schema from Decision Log template) stored immutably.
- Scope drift logs + alerts are retained and reviewable.
- Quarterly AAM review evidence (sign-off).

---

## 10) Testing plan (required before production)

### Negative tests (must pass)
- Attempt prohibited connector access → blocked + logged.
- Attempt prohibited action → blocked + logged.
- Attempt to exceed rate limits → throttled + logged.

### Positive tests (must pass)
- Allowed actions work only within defined scope.
- Alerts route correctly.
- Logs are complete and retrievable.

---

## 11) Approvals and change control

- **Approved by (Compliance/Risk):**
- **Approved by (Platform owner):**
- **Approval date:**
- **Change ticket ID / PR link:**
- **Version:**

> Any update to allowed/prohibited actions should go through formal change management (align to your existing management controls). [page:3]