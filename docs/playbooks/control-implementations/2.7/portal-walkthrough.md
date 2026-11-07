# Control 2.7: Vendor and Third-Party Risk Management — Portal Walkthrough

> Companion to [Control 2.7](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md). Provides portal-driven configuration to inventory third-party connectors, restrict high-risk publishers, govern Microsoft Copilot Studio plugins/MCP, and stand up ongoing monitoring aligned to the Interagency 2023 Third-Party Guidance, OCC 2013-29, GLBA Safeguards Rule (16 CFR Part 314), FINRA 3110/4511, and SEC 17a-4(f).

---

**Last Verified:** 2026-11-06

**Verification scope:** Official Microsoft documentation only. No tenant UI, screenshots, API calls, or policy enforcement tests were performed. Portal instructions require validation in the target environment.

## Audience and Prerequisites

- **Primary admins:** Power Platform Admin, AI Administrator
- **Supporting:** Purview Compliance Admin (DLP/audit evidence), Procurement (contract artifacts), Compliance Officer (regulatory sign-off)
- **Tenant prerequisites:**
    - Managed Environments enabled for any environment hosting Zone 2 or Zone 3 agents (see [Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md))
    - Microsoft Purview Audit enabled for supported administrative activities; separately configured agent/server telemetry for tool execution evidence
    - Established environment-to-zone mapping (Zone 1 / 2 / 3)

!!! warning "Read-only first"
    Inventory review is read-only; policy creation, tool removal, and model/provider changes are mutations. Even a new policy can suspend or quarantine existing resources and disable connections. Require a documented change ticket, impact assessment, representative non-production test, and rollback plan before publishing. Microsoft documents enforcement usually within an hour, but full enforcement can take 24 hours ([policy-change process](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention)). Historical April 2026 UI evidence is not renewed by this documentation check.

---

## Part 1 — Build the Connector Inventory (PPAC)

**Portal path:** `Power Platform admin center` → `Manage` → `Inventory`.

1. Sign in to <https://admin.powerplatform.microsoft.com> as **Power Platform Admin**.
2. Open **Manage → Inventory**. Review the **Connectors** column on resource grids and each resource's **Details → Connectors**. Use **Download** for CSV inventory evidence; record filters, resource types, collection time, and missing coverage. Microsoft documents connector inventory fields as generally available ([inventory](https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory), [schema and limitations](https://learn.microsoft.com/en-us/power-platform/admin/inventory-schema)).
3. Supplement inventory with **Manage → Products → Power Apps** / **Power Automate** analytics. These store at most **28 days**, refresh about every 24 hours, and are not complete inventory. Power Apps covers canvas apps only; its Connectors report is limited to admin/admin-team-owned connections and has **no download feature**. Power Automate excludes solution-aware flows and desktop-flow insights; export available visual data through **… → Export data** ([Power Apps](https://learn.microsoft.com/en-us/power-platform/admin/analytics-powerapps), [Power Automate](https://learn.microsoft.com/en-us/power-platform/admin/analytics-flow)).
4. Reconcile custom connectors with the [PowerShell inventory](powershell-setup.md), agent **Tools**, and approved vendor records. Built-in HTTP actions are absent from connector inventory, tabular connectors can omit operation IDs, and classic chatbots require separate discovery. Review those resources and their endpoints explicitly; absence from a connector export is not proof of no external access. The PowerShell custom-connector read omits **solution-packaged** custom connectors (documented limitation), so also review solution contents; an empty or short export never shows that no custom connector exists.
5. Consolidate into the workbook below. Distinguish catalog availability, configured resource usage, and observed execution. A connector publisher can differ from the underlying service owner; for example, Microsoft may publish a connector for a third-party service ([data policy attributes](https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss)).

### Inventory schema (one row per connector × environment)

| Field | Source | Notes |
|-------|--------|-------|
| Connector display name | Connector catalog / resource details | Reconcile by connector ID; not every usage record contains display names |
| Connector ID | Inventory resource connector references | Preserve identifier and source |
| Publisher and service owner | Connector catalog / connector reference / vendor record | Record both; Microsoft publication does not make the destination Microsoft-owned |
| Environment and consuming resource | Resource inventory / custom connector enumeration | Map to Zone 1/2/3; explicitly resolve missing environment data |
| Data classes carried | Business owner attestation | Customer NPI, MNPI, supervisory data, etc. |
| Business owner (named individual) | Procurement / governance intake | Required for Zone 2/3 |
| Risk tier | Section "Connector risk tiers" below | Drives DLP placement |
| SOC 2 status | Vendor file | Date / window / accepted alternative |
| Contract reference | Procurement | Contract ID + AI clauses flag |
| Last reviewed | Governance log | Refresh per cadence in Part 6 |

### Connector risk tiers

These tiers, placements, and cadences are organizational requirements, not Microsoft product risk ratings or a guarantee that every connector is blockable. Assess the actual service, hosting route, data, and subprocessors, not only the publisher or protocol.

| Tier | Examples | Default DLP placement | Reassessment cadence |
|------|----------|------------------------|----------------------|
| T1 — Microsoft first-party | Dataverse, SharePoint, Teams, M365 Graph | Business | Annual |
| T2 — Certified third-party | Salesforce, ServiceNow, SAP, Workday | Business with restrictions | Semi-annual |
| T3 — Independent publisher | Community connectors | Non-business or Blocked by default | Quarterly |
| T4 — Custom (org-built) | Internal APIs | Non-business unless reviewed | Quarterly |
| T5 — AI / LLM service routes | Azure-hosted models, directly accessed third-party models, external AI tools | Restricted; explicit approval per route | Quarterly |

---

## Part 2 — Configure DLP and Connector Policies

**Portal path:** `Power Platform admin center` → `Security` → `Data and privacy` → `Data policy`.

1. Open **Data policies** and select (or create) the policy that covers your Zone 2/3 environments.
2. On **Connectors**, classify supported prebuilt connectors into **Business**, **Non-business**, or **Blocked** per the firm's risk tier and actual blockability. Review custom connectors separately in the next step.
3. For an **environment-level** policy, classify custom connectors **by name on the Connectors page**, and set the default group explicitly. For a **tenant-level** policy, use the **Custom connectors** page's ordered Host URL patterns: approved hosts first, final `*` set to **Blocked**. New tenant policies default that wildcard to **Ignore**, not Blocked. Existing by-name assignments supersede patterns; environment-admin visibility is limited to owned/shared custom connectors, and dynamic **Set Host URL** changes occur after policy evaluation ([custom connector policy rules](https://learn.microsoft.com/en-us/power-platform/admin/dlp-custom-connector-parity)).
4. Configure **Advanced connector policies** separately under **Security → Data and privacy**, or **Manage → Environment groups → Rules** (see [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md)). ACP supports certified connector/action allowlisting and MCP **server-level** blocking, not custom, HTTP, or virtual connectors. Retain classic DLP in **mixed mode** for those gaps; ACP-only mode ignores classic policies. Managed Environments are needed to block otherwise nonblockable connectors ([ACP support and limits](https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies)).
5. Apply the policy to the targeted environments (or to **All environments** with explicit exclusions).
6. Document the change in your change-management system before publishing; capture screenshots of the final connector classification page as evidence.

!!! note "Policy precedence"
    Classic DLP policies are tenant- or environment-level, with tenant policy inclusion/exclusion of environments; they are not user/security-group-scoped policies. All applicable policies must be satisfied; an environment policy cannot override a tenant policy. Review **Scope / Applied to**, every applicable classification, and mixed-mode ACP, then test enforcement. Do not assume a **Policy effects** view exists ([manage data policies](https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss)).

---

## Part 3 — Govern Copilot Studio Plugins, Generative Actions, and MCP

**Portal paths (standard harness):** `Copilot Studio` (<https://copilotstudio.microsoft.com>) → select agent → **Tools**; primary model selection is on **Overview → Model**.

1. With authorized access to the agent, open each Zone 2/3 agent and review **Tools**. An administrative role is not a substitute for verifying agent/environment permissions.
2. Confirm only allowlisted tools are present. Remove or disable independent-publisher or community plugins lacking a documented vendor assessment.
3. For **MCP** (Model Context Protocol), record server publisher, hosting operator, endpoint, authentication, exposed tools, and downstream services. Copilot Studio supports **prebuilt Microsoft MCP connectors as well as custom/third-party servers**; MCP alone does not establish vendor tier. On the server's agent settings page, turn **Allow all** off and approve only needed tools: tools are all on initially, but newly added tools are off by default after **Allow all** is off ([MCP tools and policy controls](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-components-to-agent)). Require:
    - Documented vendor/service record with a risk tier based on actual destination and data handling
    - Verified supported network path; corporate device egress controls do not automatically govern Microsoft-hosted SaaS calls
    - Tested execution logging coverage, identities, redaction and retention; missing tool input/output evidence must be recorded as a gap, not assumed available in Purview Audit ([agent telemetry configuration](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-bot-framework-composer-capture-telemetry))
4. On **Overview → Model**, record the selected primary model, provider, release tag, region, and any retirement/fallback behavior. Prompt builder and other model settings are separate. Use the [live model-selection matrix](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-select-agent-model), not a blanket April 2026 GA claim; preview/experimental models are not intended for production. Distinguish Azure-hosted, Microsoft-subprocessor, and independently operated external routes.
5. For external models, verify provider access in **Microsoft 365 admin center** and the separate environment **Manage → Environments → [environment] → Settings → Product → Features** settings or environment-group rules in PPAC ([external model controls](https://learn.microsoft.com/en-us/power-platform/admin/allow-llm-generative-responses)). Review data movement on the environment's **Generative AI features → Edit** card separately. The cross-region checkbox is not displayed for US environments and does not universally constrain all models ([data movement limitations](https://learn.microsoft.com/en-us/power-platform/admin/geographical-availability-copilot)). Review CMK as its own enterprise policy/configuration, not a combined tenant Generative AI switch ([CMK](https://learn.microsoft.com/en-us/power-platform/admin/customer-managed-key)).

For Microsoft 365/Agent 365 registered plugins and servers, review **Agents → Settings → Agent and plugin access** (publisher categories), individual plugin user availability under **Agents → Tools → Plugins**, and registered MCP **Block / Unblock** under **Agents → Tools → Registry**. MCP registration **Requests (preview)** require approval plus consent. Individual-tool runtime controls are rolling out for supported Agent 365 server types through its Tooling Gateway; they are separate from ACP and agent maker toggles. Blocking one plugin does not universally block its MCP server for other plugins. The registry's Power Platform connector usage view is **preview visibility only**, not complete inventory or connector management ([registered tools](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-tools-overview), [plugin/MCP governance](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-plugins-skills-mcp-servers)). Validate actual tenant support; do not infer a universal marketplace allowlist or auto-update-disable switch.

!!! note "Provider terms are route- and model-specific"
    Anthropic is a **Microsoft subprocessor**, not a Microsoft first-party provider. Microsoft Product Terms/DPA apply to covered Claude usage, **except** models labeled **Anthropic models with Data Retention**, which require separate enablement and Anthropic terms; Anthropic acts as an independent processor for that route. Verify actual provider/user access, PPAC controls, applicable terms and processing commitments before approval ([Microsoft's Anthropic guidance](https://learn.microsoft.com/en-us/copilot/implement/connect-to-ai-subprocessor)). Native model selection does not automatically establish identical contractual, residency, certification, or retention coverage across providers. Preserve Control 2.6 assessment and this control's vendor review.

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

The **Microsoft Service Trust Portal** (<https://servicetrust.microsoft.com>) supplies Microsoft's audit reports and attestations. Check the actual report scope, service, period, exclusions, and applicable subprocessor/provider evidence; a report does not automatically cover every model route. Protected materials require an eligible organizational account and NDA/license acceptance, and some documents need specific permissions ([STP access](https://learn.microsoft.com/en-us/compliance/assurance/stp-get-started)).

---

## Part 5 — Contract Clauses for AI / Connector Vendors

Procurement should confirm the following clauses are present (or risk-accepted with sign-off) for every Tier T2–T5 vendor:

The minimums below are firm procurement requirements, not promised Microsoft platform settings or notification SLAs.

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
| Continuous (where configured and tested) | Supported connector/agent telemetry, configured DLP alerting, vendor security advisory feeds; document coverage gaps | Security Team |
| Weekly | Microsoft 365 Message Center review for Power Platform / Copilot Studio | Power Platform Admin |
| Monthly | Inventory delta review (new connectors, new plugins, new MCP endpoints) | AI Governance Lead |
| Quarterly | Tier T3–T5 reassessment; vendor scorecard refresh; transitive data-flow map review | Vendor Risk + Security |
| Semi-annual | Tier T2 reassessment; SOC 2 currency check | Procurement |
| Annual | Tier T1 reassessment; full policy review; exit-plan tabletop for Zone 3 critical vendors | AI Governance Lead + Compliance |

---

## Evidence to Capture for Audit

- Inventory workbook export (with timestamps and reviewer initials)
- Raw DLP policy reads and separate custom Host URL patterns/connector configurations, reconciled with portal scope and ACP settings (see [PowerShell Setup](powershell-setup.md)); do not assume a native policy **Export** button. `Get-DlpPolicy` output omits never-moved default-group connectors and can show stale connector names, and the default group is not necessarily Non-business, so reconcile classifications with the portal policy view
- Copilot Studio **Overview → Model**, **Tools**, MCP **Allow all**/tool selections, and applicable provider/environment settings screenshots, captured during a separately approved tenant verification
- Vendor due diligence pack per Tier T2–T5 vendor
- Quarterly vendor risk report delivered to governance committee
- Records-management log proving retention per FINRA 4511 / SEC 17a-4 schedules

---

[Back to Control 2.7](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) · [PowerShell Setup](powershell-setup.md) · [Verification & Testing](verification-testing.md) · [Troubleshooting](troubleshooting.md)

---

*Updated: November 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (documentation-only verification; no tenant UI or screenshots tested)*
