# Control 2.7: Vendor and Third-Party Risk Management — Portal Walkthrough

> Companion to [Control 2.7](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md). Provides portal-driven configuration to inventory third-party connectors, restrict high-risk publishers, govern Copilot Studio plugins/MCP, and stand up ongoing monitoring aligned to the Interagency 2023 Third-Party Guidance, OCC 2013-29, GLBA Safeguards Rule (16 CFR Part 314), FINRA 3110/4511, and SEC 17a-4(f).

---

## Audience and Prerequisites

- **Primary admins:** Power Platform Admin, AI Administrator
- **Supporting:** Purview Compliance Admin (DLP/audit evidence), Procurement (contract artifacts), Compliance Officer (regulatory sign-off)
- **Tenant prerequisites:**
    - Managed Environments enabled for any environment hosting Zone 2 or Zone 3 agents (see [Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md))
    - Microsoft Purview Audit (Standard or Premium) enabled for connector and plugin telemetry
    - Established environment-to-zone mapping (Zone 1 / 2 / 3)

!!! warning "Read-only first"
    All portal steps below are read-only or policy-additive. Do not modify production DLP policies until a documented change ticket and rollback plan exist. UI verified April 2026; portal paths can shift between Power Platform monthly releases.

---

## Part 1 — Build the Connector Inventory (PPAC)

**Portal path:** `Power Platform admin center` → `Resources` → `Capacity` and `Analytics` → `Power Apps` / `Power Automate` / `Copilot Studio`.

1. Sign in to <https://admin.powerplatform.microsoft.com> as **Power Platform Admin**.
2. From the left rail, open **Analytics** → choose **Power Apps**, **Power Automate**, and **Copilot Studio** in turn.
3. For each workload, set the time range to the last **30 days** and download the connector usage CSVs (per-environment).
4. From **Resources** → **Connectors**, review the **Custom connectors** and **Independent publisher** tabs for every Zone 2/3 environment.
5. Consolidate into a single inventory workbook with the columns below.

### Inventory schema (one row per connector × environment)

| Field | Source | Notes |
|-------|--------|-------|
| Connector display name | Analytics export | Use Microsoft canonical name |
| Connector ID | Analytics export | Stable identifier for audit |
| Publisher | Connector blade | Microsoft / Verified / Independent / Custom |
| Environment | Analytics export | Map to Zone 1/2/3 |
| Data classes carried | Business owner attestation | Customer NPI, MNPI, supervisory data, etc. |
| Business owner (named individual) | Procurement / governance intake | Required for Zone 2/3 |
| Risk tier | Section "Connector risk tiers" below | Drives DLP placement |
| SOC 2 status | Vendor file | Date / window / accepted alternative |
| Contract reference | Procurement | Contract ID + AI clauses flag |
| Last reviewed | Governance log | Refresh per cadence in Part 6 |

### Connector risk tiers

| Tier | Examples | Default DLP placement | Reassessment cadence |
|------|----------|------------------------|----------------------|
| T1 — Microsoft first-party | Dataverse, SharePoint, Teams, M365 Graph | Business | Annual |
| T2 — Certified third-party | Salesforce, ServiceNow, SAP, Workday | Business with restrictions | Semi-annual |
| T3 — Independent publisher | Community connectors | Non-business or Blocked by default | Quarterly |
| T4 — Custom (org-built) | Internal APIs | Non-business unless reviewed | Quarterly |
| T5 — External AI / LLM providers | Azure OpenAI, third-party LLM endpoints, MCP tool servers | Restricted; explicit allowlist | Quarterly |

---

## Part 2 — Configure DLP and Connector Policies

**Portal path:** `Power Platform admin center` → `Policies` → `Data policies`.

1. Open **Data policies** and select (or create) the policy that covers your Zone 2/3 environments.
2. On **Prebuilt connectors**, place every inventoried connector into **Business**, **Non-business**, or **Blocked** per its risk tier. Independent-publisher and unreviewed custom connectors should land in **Blocked** by default.
3. On **Custom connectors**, set the default behavior to **Blocked** and define explicit URL patterns for approved internal APIs only.
4. On **Connector configurations** (Advanced Connector Policies — see [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md)), restrict high-risk actions (e.g., HTTP, file system writes, send-as) where the connector vendor supports it.
5. Apply the policy to the targeted environments (or to **All environments** with explicit exclusions).
6. Document the change in your change-management system before publishing; capture screenshots of the final connector classification page as evidence.

!!! note "Policy precedence"
    Power Platform applies the **most restrictive** matching policy across environment-, security-group-, and tenant-scoped policies. Validate effective policy after publish using the **Policy effects** view.

---

## Part 3 — Govern Copilot Studio Plugins, Generative Actions, and MCP

**Portal path:** `Copilot Studio` (<https://copilotstudio.microsoft.com>) → select agent → `Settings` → `Generative AI` and `Tools` / `Plugins`.

1. As **AI Administrator**, open each Zone 2/3 agent and review the **Tools / Plugins** tab.
2. Confirm only allowlisted tools are present. Remove or disable independent-publisher or community plugins lacking a documented vendor assessment.
3. For **MCP** (Model Context Protocol) tool servers — which are non-Microsoft by definition — require:
    - Documented vendor record in the inventory (Tier T5)
    - Network egress through approved gateways only
    - Logging of every tool call with request/response metadata (see verification playbook)
4. In **Settings → Generative AI**, review the selected model provider. Native Copilot Studio model options (Microsoft, Azure OpenAI, Anthropic Claude, OpenAI GPT-5) inherit Microsoft platform terms; non-native LLM endpoints require a direct vendor agreement and Tier T5 assessment.
5. In the **Power Platform admin center** → `Settings` → `Generative AI`, confirm **tenant-level** controls for cross-geo data movement, customer-managed keys, and external model usage match the tenant's vendor risk decisions.

!!! tip "Anthropic and OpenAI native integration"
    With Anthropic Claude and OpenAI GPT-5 generally available as native Copilot Studio model providers (April 2026), reclassify those vendors as **Microsoft-mediated platform services** in the inventory. The direct vendor relationship is replaced by Microsoft's data-handling commitments, but the underlying model risk (Control 2.6) and supply-chain risk (this control) still apply.

---

## Part 4 — Vendor Due Diligence Pack

For every Tier T2–T5 vendor, collect and store under records management:

- SOC 2 Type II report (within validity window) or accepted alternative (ISO 27001 + bridge letter, FedRAMP Moderate/High, or independent assessment)
- SOC 1 Type II where the vendor influences SOX-relevant processes
- Penetration test summary (within last 12 months)
- Subprocessor list and notification mechanism
- Data residency and cross-border transfer commitments
- Incident response plan and breach notification SLA
- Business continuity / disaster recovery test results
- For AI/LLM vendors only: model card(s), training-data governance summary, evaluation/red-team results, and explicit no-training-on-customer-data attestation

The **Microsoft Service Trust Portal** (<https://servicetrust.microsoft.com>) is the canonical source for Microsoft first-party attestations covering Power Platform, Copilot Studio, Microsoft 365 Copilot, and Azure OpenAI.

---

## Part 5 — Contract Clauses for AI / Connector Vendors

Procurement should confirm the following clauses are present (or risk-accepted with sign-off) for every Tier T2–T5 vendor:

| Clause | Minimum standard |
|--------|-------------------|
| Material model change notification | At least 30 days advance notice |
| No training on customer data | Explicit prohibition without written consent |
| AI incident notification | Within 24 hours for incidents impacting integrity, confidentiality, or availability |
| Audit rights | Annual right to audit or accept SOC 2 Type II in lieu |
| Data residency | Named region(s); written approval required to change |
| Subprocessor approval | Notification with right to object |
| Records-handling commitments | Where vendor stores books-and-records per SEC 17a-4 / FINRA 4511 |
| Exit assistance | Data return / destruction within defined window post-termination |

---

## Part 6 — Ongoing Monitoring Cadence

| Cadence | Activity | Owner |
|---------|----------|-------|
| Continuous (automated) | Connector telemetry, DLP exception alerts, vendor security advisory feeds | Security Team |
| Weekly | Microsoft 365 Message Center review for Power Platform / Copilot Studio | Power Platform Admin |
| Monthly | Inventory delta review (new connectors, new plugins, new MCP endpoints) | AI Governance Lead |
| Quarterly | Tier T3–T5 reassessment; vendor scorecard refresh; transitive data-flow map review | Vendor Risk + Security |
| Semi-annual | Tier T2 reassessment; SOC 2 currency check | Procurement |
| Annual | Tier T1 reassessment; full policy review; exit-plan tabletop for Zone 3 critical vendors | AI Governance Lead + Compliance |

---

## Evidence to Capture for Audit

- Inventory workbook export (with timestamps and reviewer initials)
- DLP policy export (Power Platform admin center → policy → **Export**)
- Copilot Studio agent settings screenshots (model provider, plugins/tools list)
- Vendor due diligence pack per Tier T2–T5 vendor
- Quarterly vendor risk report delivered to governance committee
- Records-management log proving retention per FINRA 4511 / SEC 17a-4 schedules

---

[Back to Control 2.7](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) · [PowerShell Setup](powershell-setup.md) · [Verification & Testing](verification-testing.md) · [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.3.3 | UI Verification Status: Current*
