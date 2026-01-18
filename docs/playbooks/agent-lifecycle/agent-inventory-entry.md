# Template: Agent Inventory & Registration Entry (AIR)

**Purpose:** Standardize the metadata captured for every agent so governance controls (zones, approvals, logging, data policy, escalation, vendor risk) can be applied consistently.  
**Applies to:** All zones (Zone 1–3).  
**Microsoft grounding:** Microsoft 365 admins can manage Copilot agents (deploy/assign/block/remove) through the Microsoft 365 admin center, treating agents as manageable assets at tenant scope. [web:119]  
**Audit grounding:** Microsoft Purview audit logs for Copilot/AI interactions include details like accessed resources (including sensitivity label IDs) and policy restriction details, which can be correlated back to an agent inventory. [web:118]  
**Related controls (examples):** 3.1 Agent Inventory and Registration, 2.3 Change management, 2.12 Supervision/oversight, 1.7 Audit logging. [page:3]

---

## 1) Identity

- **Agent name:**
- **Agent ID (unique):**
- **Agent type:** (M365 Copilot agent / Copilot Studio agent / other)
- **Tenant/environment:** (Prod / Test / Sandbox)
- **Primary surfaces:** (Teams / Outlook / Word / M365 Copilot chat / other)
- **Owner (business):**
- **Owner (technical):**
- **Backup owner:**
- **Approver (Compliance/Risk):**
- **Status:** (Draft / Pilot / Production / Retired)
- **Go-live date:**
- **Last modified date:**
- **Change record / PR / ticket link:**

---

## 2) Zone + governance level assignment

- **Zone:** Zone 1 / Zone 2 / Zone 3
- **Governance level:** Baseline / Recommended / Regulated
- **Justification (one paragraph):**
  - Data sensitivity:
  - Autonomy/actionability:
  - Blast radius:
  - Customer/consequential impact:

---

## 3) Use case and constraints

- **Business use case:**
- **User population:** (groups/roles)
- **In-scope tasks:** (bullets)
- **Out-of-scope tasks:** (bullets)
- **Customer-facing?** (Yes/No)
- **Consequence-bearing decision?** (Yes/No; if yes, describe)

---

## 4) Data access profile (high-level)

Link to the agent’s detailed Per-Agent Data Handling Policy.

- **Per-agent data policy link:** `../templates/per-agent-data-policy.md`
- **Allowed sensitivity labels:** (bullets)
- **Prohibited sensitivity labels:** (bullets)
- **Primary repositories:** (SharePoint sites, Dataverse envs, etc.)

---

## 5) Actions, tools, and connectors

> “Actions” should be constrained via an Action Authorization Matrix (AAM) for any agent that can initiate workflows or modify records.

- **Action Authorization Matrix link:** `../templates/action-authorization-matrix.md`
- **Allowed connectors/tools:** (bullets)
- **Denied connectors/tools:** (bullets)
- **Key permissions/RBAC groups:** (bullets)

---

## 6) Logging + evidence

> Purview audit logs for Copilot/AI interactions can include AccessedResources and sensitivity label IDs, and PolicyDetails when access is blocked/restricted, supporting evidence of data protection and policy enforcement. [web:118]

- **Audit logging enabled?** (Yes/No)
- **Audit search query saved?** (link or description)
- **Decision log schema used?** (Yes/No; link)
- **Retention tag for logs:** (e.g., 7 years)

---

## 7) Escalation + incident response

- **Escalation matrix link:** `../templates/escalation-matrix.md`
- **On-call route:** (Teams channel / DL)
- **SLA:** (e.g., 15 min for S1)

---

## 8) Risk assessments (attach links)

- **Model/agent risk assessment:** (link)
- **Bias/fairness testing (if applicable):** (link)
- **Threat model / security review:** (link)
- **Vendor/supply chain register entry:** (link)
- **BC/DR assessment:** (link)

---

## 9) Compliance mapping

- **Primary regulatory lenses:** (FINRA / SEC / GLBA / SOX / OCC / SR 11-7, etc.)
- **Records obligations:** (what retention/regulatory recordkeeping applies)
- **Disclosures/communications constraints:** (if customer-facing)

---

## 10) Approvals

- **Business owner approval:** (name/date)
- **Compliance approval:** (name/date)
- **Security approval:** (name/date)
- **Go-live authorization:** (name/date)

---

## 11) Review cadence

- **Zone 1:** (recommended: semiannual)
- **Zone 2:** (recommended: quarterly)
- **Zone 3:** (recommended: quarterly + post-change review)

---

## 12) Notes

Free-form notes for anything unusual (exception approvals, known limitations, roadmap).