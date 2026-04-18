# Portal Walkthrough — Control 2.24: Agent Feature Enablement and Restriction Governance

!!! danger "READ FIRST — Scope and Sibling Routing"
    **This playbook configures feature-level governance for Microsoft 365 Copilot, Copilot Studio, declarative agents, Microsoft Agent Framework, and MCP-connector tools** across the **Microsoft 365 Copilot admin center**, the **Power Platform admin center Copilot hub**, **PPAC environment features**, **Copilot Studio per-agent settings**, the **feature catalog** (Dataverse or SharePoint), and **Purview / DLP** enforcement surfaces required to satisfy Verification Criteria 1–10 of [Control 2.24](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md).

    **This walkthrough IS for:**

    | In Scope | Surface | Outcome |
    |---|---|---|
    | Enabling / disabling tenant-level declarative-agent capabilities (web search, code interpreter, image generation, file search, actions/MCP) | M365 admin center → Copilot → Settings → Agents & connectors | Per-capability toggles recorded with author + change ticket |
    | Tenant-wide Copilot Studio feature toggles | PPAC → Copilot (hub) | Tenant baseline aligned with Zone 3 defaults |
    | Per-environment feature flags and preview-feature exposure | PPAC → Environments → [env] → Settings → Product → Features | Preview features off in Z3; documented exceptions in Z2 |
    | Per-agent tool, knowledge-source, authentication, and publishing configuration | Copilot Studio → [agent] → Settings / Tools / Knowledge | Agent-level configuration matches feature catalog |
    | Feature catalog authoring and change workflow (forward **and reverse**) | Dataverse table / SharePoint list + ServiceNow / Jira / SPO | Every Z2/Z3 capability has an authorised record with expiration, risk rating, and reverse-change path |
    | MCP connector and Agent Framework feature-flag governance (external tool egress) | PPAC → Data policies + Copilot Studio → [agent] → Actions → MCP | External tool egress is allowlisted, justified, and monitored |
    | Voice and image-upload toggles (recording consent + Purview DLP for images) | M365 admin center → Copilot → Voice; Purview → DLP | Consent banner and DLP classifier coverage verified |
    | Sovereign-cloud compensating feature catalog (GCC / GCC High / DoD) | Separate catalog instance + attestation workbook | Cloud-specific allow-list with no inheritance from Commercial |

    **This walkthrough is NOT for:**

    | Out of Scope | Use Instead |
    |---|---|
    | Restricting **who** can publish an agent at all (authorisation gate) | [Control 1.1 — Restrict Agent Publishing by Authorization](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) |
    | Inventorying which agents exist and what they currently use | [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |
    | Connector-level allow / block / block-custom DLP classification | [Control 1.4 — Advanced Connector Policies (ACP)](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) |
    | Communication-compliance monitoring of what enabled capabilities produce | [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) |
    | Environment-tier zoning decisions themselves | [Control 2.2 — Environment Groups and Tier Classification](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) |
    | The MRM re-validation that feature-enablement triggers | [Control 2.6 — Model Risk Management (OCC 2011-12 / SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) |
    | Supervisory procedures update that feature-enablement triggers | [Control 2.12 — Supervision and Oversight (FINRA 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |
    | Orchestration-specific depth, hop, and token-budget limits | [Control 2.17 — Multi-Agent Orchestration Limits](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) |
    | The Agent 365 console used to surface / block individual agents | [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) |
    | PowerShell / Graph automation of the same surfaces | [`./powershell-setup.md`](./powershell-setup.md) |
    | Test cases, evidence-collection scripts, and sample queries | [`./verification-testing.md`](./verification-testing.md) |
    | Missing blades, greyed-out toggles, propagation delays, and remediation steps | [`./troubleshooting.md`](./troubleshooting.md) |

!!! warning "Hedged-Language Reminder"
    This playbook helps your organization **support compliance with** SOX §302/404 (internal controls over financial reporting), FINRA Rule 3110 (supervision), FINRA Rule 4511 / SEC 17a-4 (recordkeeping), Federal Reserve SR 11-7 / OCC Bulletin 2011-12 (model risk management), FFIEC IT Risk Management Handbook, GLBA 501(b) (safeguards), and, for SCI entities, SEC Regulation SCI §242.1001(a) / §242.1003. It does **not** by itself guarantee any regulatory outcome. Implementation requires Microsoft 365 Copilot licensing, Power Platform administrative access, validated change-control procedures, documented supervisory procedures, and independent testing by your compliance function. Organizations should verify all configurations against their own regulatory examination workpapers and legal counsel before treating these procedures as adequate evidence. FINRA Notice 25-07 is cited in the parent control as industry consultation only; it is an RFC, not binding guidance.

!!! danger "Non-Substitution Principle — Feature Toggles Do NOT Replace MRM, Supervision, or Publishing Authorisation"
    A feature toggle restricts what a capability **can do** at runtime. It does **not** validate that the capability is **fit for purpose** and it does **not** grant anyone permission to deploy an agent that uses it. Enabling a capability on a Zone 2 or Zone 3 agent should **trigger — not replace**:

    - A **Model Risk Management re-validation** under [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) (SR 11-7 §V treats capability changes as material model changes).
    - A **supervisory-procedures update** under [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) (FINRA 3110).
    - An **AI guardrails reassessment** and publishing-authorisation review under [Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md).
    - A connector-policy impact assessment under [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) if the capability reaches external data or egress.

    Treat this control as the **enforcement and evidence layer** that presupposes an **approval layer elsewhere**. "The toggle is on" is never a complete answer to an examiner.

!!! warning "Sovereign Cloud Caveat (GCC / GCC High / DoD)"
    Microsoft 365 Copilot, Copilot Studio, declarative-agent capabilities, MCP connectors, and Agent Framework tools reach General Availability on the **Commercial cloud first**. M365 GCC, GCC High, DoD, and other sovereign clouds typically lag Commercial by **6–18 months**, and some preview capabilities (select MCP connectors, image-generation models, third-party plugin types, voice) may **never** become available in sovereign clouds. FSI organisations operating in sovereign tenants must:

    - Maintain a **separate feature catalog per cloud** (Commercial vs GCC vs GCC High vs DoD) — never a shared catalog.
    - Treat any "allow in Zone 2/3" decision in Commercial as **not inherited** into sovereign; each cloud requires its own approval record, change ticket, and MRM re-validation trigger.
    - Verify capability availability against the cloud-specific service description (Microsoft 365 for Government, Copilot for GCC / GCC High) before publishing a feature allow-list entry.
    - Record capabilities that are **unavailable** in the sovereign cloud as a **product unavailability** line item in examination briefings — not as a policy exception or compensating control.

    See [§9 — Sovereign Cloud Compensating Control](#9-sovereign-cloud-compensating-control-gcc-gcc-high-dod) for the concrete dual-catalog procedure.

!!! info "License, Role, and Program Requirements"
    | Requirement | Why | Where to verify |
    |---|---|---|
    | Microsoft 365 Copilot per agent sponsor | Required to author and own declarative / Copilot Studio agents | M365 admin center → Billing → Licenses |
    | Power Platform per user / per app as required | Required to author Copilot Studio agents and use premium connectors | PPAC → Licensing |
    | **AI Administrator** role (Entra, assigned via PIM) | Day-to-day governance of Copilot admin-center capability toggles — **prefer over Entra Global Admin** per role catalog | Entra → Roles & admins → filter "AI Administrator"; assign via PIM eligibility |
    | **Power Platform Admin** | PPAC Copilot hub, environment features, DLP policies | PPAC → Admins |
    | **Compliance Officer** | Approves Z2/Z3 capability changes; reviews regulatory impact | Purview → Roles & scopes |
    | **AI Governance Lead** | Maintains feature catalog; runs quarterly risk assessment | Governance RACI document |
    | **Change Management Team** | Processes feature-enablement CRs (forward **and reverse**) | ServiceNow / Jira / SPO change register |
    | **Entra Global Admin** | **Exceptional only** — initial setup, emergency rollback, tenant-wide Copilot program enrolment; not used for routine capability toggles | Entra → Roles & admins |
    | Microsoft Purview Audit (Standard or Premium) | Retains admin-center and PPAC change events for the 6-year SEC 17a-4 horizon | Purview → Audit → Audit retention policies |
    | Dataverse database (governance environment) **or** SharePoint Online site (governance site) | Hosts the feature catalog | Power Apps → Tables; or SPO admin |

!!! tip "Portal Navigation May Shift"
    Microsoft has restructured the Copilot admin and PPAC Copilot-hub navigation **multiple times in the last 12 months**. If a blade name in this playbook does not match what you see, search the admin center for the underlying noun ("Copilot", "Agents & connectors", "Governance", "Features") and consult [`learn.microsoft.com/copilot/`](https://learn.microsoft.com/copilot/) and [`learn.microsoft.com/power-platform/admin/`](https://learn.microsoft.com/power-platform/admin/). Screenshot anchors in this playbook record the navigation that was verified at the **Last UI Verified** date in the control header (February 2026). **Re-verify labels quarterly.**

!!! info "Reframing: 'Dataverse Policy Enforcement' Is Not a Microsoft Enforcement Plane"
    Some older governance material describes a "Dataverse policy enforcement" plane. In this control, the Dataverse table (or SharePoint list) is a **customer-built register** — it records approvals, risk ratings, expiration dates, and change tickets. It does **not** itself block features at runtime. Runtime enforcement is achieved by (a) admin-center and PPAC toggles (**primary**), (b) DLP connector policies under Control 1.4 (**secondary**), (c) agent-level Copilot Studio configuration (**tertiary**), and (d) supervisory detective controls under Controls 1.10 and 2.12. Treat the Dataverse/SharePoint feature catalog as **evidence**, not as **enforcement**.

---

## Document Map

| § | Section | Verification Criterion Evidenced |
|---|---|---|
| 0 | [Pre-flight Prerequisites and Triage](#0-pre-flight-prerequisites-and-triage) | All — gating checks |
| 1 | [Microsoft 365 Copilot Admin Center — Declarative-Agent Capability Toggles](#1-microsoft-365-copilot-admin-center-declarative-agent-capability-toggles) | VC-1, VC-3, VC-5 |
| 2 | [Power Platform Admin Center — Tenant-Wide Copilot Hub](#2-power-platform-admin-center-tenant-wide-copilot-hub) | VC-1, VC-3 |
| 3 | [PPAC — Per-Environment Feature Flags and Preview Features](#3-ppac-per-environment-feature-flags-and-preview-features) | VC-1, VC-2, VC-5 |
| 4 | [Copilot Studio — Per-Agent Tool, Knowledge, Auth, and Publishing Configuration](#4-copilot-studio-per-agent-tool-knowledge-auth-and-publishing-configuration) | VC-5, VC-8 |
| 5 | [Feature Catalog Authoring (Dataverse or SharePoint)](#5-feature-catalog-authoring-dataverse-or-sharepoint) | VC-4, VC-9 |
| 6 | [Change-Management Workflow — Forward and Reverse](#6-change-management-workflow-forward-and-reverse) | VC-7 |
| 7 | [MCP Connectors and Agent Framework Feature Flags](#7-mcp-connectors-and-agent-framework-feature-flags) | VC-6, VC-8 |
| 8 | [Voice and Image-Upload Toggles (Consent and DLP)](#8-voice-and-image-upload-toggles-consent-and-dlp) | VC-5, VC-6 |
| 9 | [Sovereign Cloud Compensating Control (GCC / GCC High / DoD)](#9-sovereign-cloud-compensating-control-gcc-gcc-high-dod) | All (substitute path) |
| 10 | [Zone Cadence Checklists (Z1 / Z2 / Z3)](#10-zone-cadence-checklists-z1-z2-z3) | VC-10 |
| 11 | [Evidence Capture per Session](#11-evidence-capture-per-session) | All (evidence) |
| 12 | [Cross-References and Sibling Routing](#12-cross-references-and-sibling-routing) | Operational reference |
| ★ | [Closing Decision Matrix and Readiness Checklist](#closing-decision-matrix-and-readiness-checklist) | Operational reference |

---

## 0. Pre-flight Prerequisites and Triage

Before you click anything in any portal, run through this gate. Skipping a gate produces silent failures later — for example, the **Agents & connectors** settings blade does not render capability sub-toggles unless the tenant has at least one Copilot-licensed user, and environment-level preview-feature toggles are hidden for environments the signed-in principal does not administer.

### 0.1 Confirm tenant cloud and Copilot program posture

1. Sign in to [`https://admin.microsoft.com`](https://admin.microsoft.com) as an account that holds at least **AI Administrator** (preferred) or **Entra Global Admin** (exceptional only).
2. In the upper-right corner, click your profile photo → **Switch tenant** if you are a multi-tenant operator. Confirm you are in the tenant you intend to govern and capture the **Tenant ID** GUID and **Primary domain** for your runbook (Settings → Org settings → Organization profile).
3. Inspect the URL bar:
    - `admin.microsoft.com` → M365 Commercial. Continue with §1–§8.
    - `portal.office365.us` / `admin.microsoft.us` → **sovereign cloud**. Stop and jump to [§9](#9-sovereign-cloud-compensating-control-gcc-gcc-high-dod).
4. Navigate to **Copilot → Overview**. Confirm Copilot is provisioned for the tenant — if you see a "Get started with Copilot" splash instead of the Overview tiles, return to licensing in §0.3.

*Screenshot anchor: `docs/images/2.24/EXPECTED.md#0-1-copilot-overview` — M365 admin center Copilot Overview blade with tenant-ID banner visible.*

!!! warning "Tenant Cloud Detection Is the First Branch"
    Every subsequent section assumes Commercial. If you continue in a `*.us` or DoD tenant, capability toggles for preview features, MCP connectors, voice, and image upload will not render — and the resulting blank-screen output can be misread as "feature is disabled" when in fact the **feature does not exist** in that cloud. Record the cloud at the top of your evidence pack.

### 0.2 Confirm role assignments (PIM-aware)

| Role | Required for | Where to assign |
|---|---|---|
| **AI Administrator** | M365 admin center Copilot → Settings → Agents & connectors capability toggles (§1); routine governance | Entra → Roles & admins → "AI Administrator" — assign via **PIM eligibility**, activate Just-in-Time with ticket reference |
| **Power Platform Admin** | PPAC Copilot hub (§2), environment features (§3), DLP (§7) | PPAC → Admins |
| **Copilot Studio Agent Author** | Per-agent configuration (§4) in authoring environments | Environment security role `Copilot Studio Author` |
| **Compliance Officer** | Review / approve Z2 / Z3 capability changes (§6) | Purview → Roles & scopes |
| **AI Governance Lead** | Feature catalog authority (§5), quarterly risk assessment (§10) | Governance RACI; typically granted Dataverse `Feature Catalog Owner` security role or SPO list owner |
| **Security Architect** | Compensating-control design for high-risk capabilities | Governance RACI |
| **Change Management Team** | Forward / reverse change processing (§6) | ServiceNow / Jira / SPO |
| **Entra Global Admin** | **Exceptional only** — program enrolment, emergency rollback | Entra → Roles & admins (break-glass only) |

1. In Entra, navigate to **Identity → Roles & admins → Roles**.
2. Search for each role above and confirm at minimum **two named human accounts** (no service principals, no break-glass) hold each role per FINRA Rule 3110 dual-control expectations.
3. For **AI Administrator**, confirm assignments are **PIM-eligible, not permanent active** — permanent activation on a governance role is itself an audit finding in an FSI examination.
4. If any role shows zero or one assignee, open a ticket with your Entra owner before proceeding.

*Screenshot anchor: `docs/images/2.24/EXPECTED.md#0-2-role-assignments` — Roles & admins grid filtered to "AI Administrator" and "Power Platform Admin" with PIM eligibility visible.*

!!! example "Examiner Evidence Box — Role Coverage"
    | Element | Value |
    |---|---|
    | Artifact produced | CSV export of `directoryRole` membership for AI Administrator, Power Platform Admin, and Entra Global Admin (PIM-aware) + PIM activation history for the last 30 days |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervision — dual control), SOX §404 (segregation of duties), GLBA 501(b) (access accountability) |

### 0.3 Confirm licensing, Dataverse / SharePoint backing store, and Purview Audit

1. **M365 admin → Billing → Licenses** — confirm Microsoft 365 Copilot licences are assigned to the human accounts who will sponsor agents.
2. **PPAC → Licensing** — confirm Power Platform licensing covers the environments that will host Copilot Studio agents.
3. **Power Apps → Environments** — confirm the **governance environment** that will host the `fsi_featurecatalog` Dataverse table exists and has a Dataverse database provisioned (this should be a **dedicated environment**, not a default environment, and it should be Zone-2-classified at minimum per Control 2.2). If you prefer SharePoint as the backing store, identify the governance site collection now.
4. **Purview → Audit → Audit retention policies** — confirm a policy exists that retains at minimum `AzureActiveDirectory`, `PowerPlatformAdmin`, and `MicrosoftTeams` workload events for **2190 days** (6 years).

!!! warning "Governance Environment Must Not Be the Default Environment"
    Authoring the feature catalog in the tenant default environment is a common mistake. The default environment is Zone 1 by definition, lacks DLP segregation, and is inappropriate for a governance artefact that drives Zone 3 decisions. Create a purpose-built governance environment per Control 2.2 and host the feature catalog there.

### 0.4 Pre-flight gate summary

Do not proceed past this section unless **all** of the following are true:

- [ ] You are signed in to the correct tenant and have captured the tenant ID.
- [ ] Tenant cloud is identified (Commercial → §1–§8; sovereign → §9).
- [ ] At least two named humans hold each governance role in §0.2, **AI Administrator is PIM-eligible not permanent**.
- [ ] Microsoft 365 Copilot and Power Platform licences are assigned to intended sponsors and authors.
- [ ] A dedicated governance environment (Dataverse) or governance SPO site exists to host the feature catalog.
- [ ] Purview Audit retention policy ≥ 2190 days covers AzureActiveDirectory + PowerPlatformAdmin workloads.
- [ ] Zone classifications from Control 2.2 are published and every in-scope environment has a zone tag.

!!! tip "If a Gate Fails"
    Open [`./troubleshooting.md`](./troubleshooting.md) and search for the gate name (e.g., "AI Administrator role not visible"). Do not attempt workarounds in production until the gate clears — most workarounds for missing licensing or roles create their own audit findings.

---

## 1. Microsoft 365 Copilot Admin Center — Declarative-Agent Capability Toggles

**Verification Criteria evidenced:** VC-1 (feature restrictions aligned with zones), VC-3 (generative-AI restrictions with approval in Z2/Z3), VC-5 (high-risk features disabled in Z2/Z3).

The M365 admin center is the **tenant-scoped** control surface for Microsoft 365 Copilot and declarative-agent capabilities. These toggles govern what **declarative agents** (JSON-packaged agents distributed via the Microsoft 365 Agents SDK and the Microsoft 365 marketplace) are permitted to do **regardless of which environment an author uses**. For Copilot Studio agents (Power Platform-hosted), add PPAC controls in §2–§3.

### 1.1 Open the Copilot capability surface

1. Sign in to [`https://admin.microsoft.com`](https://admin.microsoft.com) as **AI Administrator** (activate PIM eligibility with a change-ticket reference — do **not** use Entra Global Admin unless §0.2 has documented an exceptional need).
2. In the left navigation, expand **Copilot** and click **Settings**.
3. Select the **Agents & connectors** tab. The right pane shows a card per capability category:
    - **Web search**
    - **Code interpreter** (a.k.a. Python / data-analysis capability)
    - **Image generation**
    - **File search** (Graph-grounded retrieval)
    - **Actions** (first-party and third-party connector actions)
    - **MCP connectors** (external Model Context Protocol endpoints — see §7 for the deep dive)
    - **Voice** (see §8)
    - **Image upload** (see §8)

*Screenshot anchor: `docs/images/2.24/EXPECTED.md#1-1-agents-connectors` — M365 admin Copilot → Settings → Agents & connectors with all capability cards visible and Tenant ID banner.*

!!! warning "Capability Cards Are Tenant-Wide — Environment Overrides Live in §3"
    The toggles in this blade apply across **every** environment in the tenant for declarative agents, and they form the **ceiling** for Copilot Studio agents. An environment-level override in PPAC (§3) can only **reduce** capability below this ceiling — it cannot raise it. Set this blade to the **most permissive posture required by any in-scope use case**, then reduce per environment in §3. This matches the "policy ceiling + per-environment floor" pattern documented in the parent control.

### 1.2 Baseline the current state (before you change anything)

1. For each capability card, click the card to open its detail pane. Capture the current state in your runbook:
    - On / Off
    - **Who can use** scope (All users / Specific groups / None)
    - Last modified date and modifier UPN
    - Any linked DLP or sensitivity-label requirement
2. Export a CSV of current capability state: click the ellipsis (…) → **Export settings** (if present) or screenshot every card.
3. Commit the baseline CSV to your governance repository as `Control-2.24/baseline/<YYYY-MM-DD>/copilot-capability-baseline.csv`. **Never** change toggles without a baseline — you will not be able to answer "what did we change?" in an examiner walkthrough otherwise.

*Screenshot anchor: `docs/images/2.24/EXPECTED.md#1-2-capability-baseline` — Capability detail pane showing On/Off state, scope, and last-modified metadata.*

!!! example "Examiner Evidence Box — Capability Baseline"
    | Element | Value |
    |---|---|
    | Artifact produced | Capability baseline CSV + dated screenshots of each capability detail pane |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | SOX §404 (IT general controls — baseline documentation), FINRA 3110 (supervisory change tracking) |

### 1.3 Configure web search

**Default posture by zone (recommended):** Z1 On for all users; Z2 On for approved agents only (via Entra group scope); Z3 Off with explicit allow-list per approved agent.

1. Open the **Web search** card → **Edit**.
2. Set **State** = **On** (tenant ceiling).
3. Set **Who can use** = **Specific groups** and select an Entra security group named `fsi-copilot-websearch-allowed` (create the group first if it does not exist, membership gated by Control 1.1 publishing authorisation).
4. If the blade exposes **Allowed domains / Denied domains** (preview in some tenants), configure an allow-list aligned with your firm's list of approved market-data, legal-research, and regulatory-filing hostnames.
5. Set **Query logging** = **On** — required for downstream Communication Compliance review under Control 1.10.
6. Click **Save**. Capture the confirmation banner.
7. Record the change in the feature catalog (§5): FeatureName `Web search (declarative)`, Surface `M365 admin center`, CloudScope `Commercial`, Z1/Z2/Z3 status, Approval ticket, Risk rating `Medium`.

*Screenshot anchor: `docs/images/2.24/EXPECTED.md#1-3-websearch-edit` — Web search Edit pane with group scope and query logging configured.*

### 1.4 Configure code interpreter

**Default posture by zone:** Z1 On (personal productivity); Z2 Off unless specific approved agent; Z3 Off with very narrow allow-list.

1. Open the **Code interpreter** card → **Edit**.
2. Set **State** = **On** only if at least one approved Z1/Z2 agent requires it. Many FSI tenants set this to **Off** at the tenant ceiling and grant per-agent exceptions through Copilot Studio (§4) in a dedicated Zone 1 sandbox environment only.
3. If On, set **Who can use** = **Specific groups** → `fsi-copilot-codeinterpreter-allowed` (membership gated by publishing authorisation AND MRM sign-off per Control 2.6).
4. Confirm **Session egress** (if exposed) = **No outbound network** — the Python sandbox should not be able to exfiltrate data to arbitrary hosts.
5. Click **Save**. Record the change in the feature catalog with Risk rating `High`.

!!! danger "Code Interpreter Is an MRM Trigger"
    Enabling code interpreter on any agent that participates in decisioning, supervision, or financial reporting is a **material model change** under SR 11-7 §V. Open the Control 2.6 MRM re-validation ticket **before** the toggle flip, not after. Attach the MRM validation report to the change record in §6 before closing the change.

### 1.5 Configure image generation

**Default posture by zone:** Z1 On; Z2 Off unless approved marketing-type agent; Z3 Off.

1. Open the **Image generation** card → **Edit**.
2. For Z3-only tenants, set **State** = **Off** and record this in the feature catalog with Risk rating `Medium` and a justification tied to FINRA 2210 (communications with the public) and FTC UDAP considerations.
3. For mixed-zone tenants, set **State** = **On** with scope limited to `fsi-copilot-imagegen-allowed`.
4. If the blade exposes **Content-safety classifier** level, set to **Strict**.
5. Click **Save**. Record the change.

### 1.6 Configure file search (Graph-grounded retrieval)

**Default posture by zone:** Z1 On; Z2 On; Z3 On with sensitivity-label restrictions enforced by Purview under Controls 2.4–2.10.

1. Open the **File search** card → **Edit**.
2. Confirm **State** = **On** (most FSI deployments need file search for basic Copilot functionality).
3. Critically, confirm **Respect sensitivity labels** = **On** and **Respect Purview DLP** = **On**. These are the enforcement hooks that prevent Copilot from summarising labelled content in agent responses.
4. Click **Save**. Record the change with Risk rating `Low` (label-gated).

!!! warning "File Search Is a Purview-Dependency, Not a Standalone Control"
    File search is only as safe as the Purview label and DLP coverage underneath it. If you have not completed Controls 2.4 (Sensitivity Labels), 2.5 (DLP Baseline), and 2.9 (Records Retention), **do not treat file search as Z3-safe**. Flag the residual risk in the feature catalog and in the Control 2.12 supervisory register.

### 1.7 Configure actions (first-party connectors)

1. Open the **Actions** card → **Edit**.
2. Review the list of first-party actions available (Outlook, Teams, Planner, Dataverse, etc.). Each has its own toggle.
3. Set posture per action aligned with the zone-based matrix in the parent control. For Z3, set most actions to **Off** except those with a documented approval in the feature catalog.
4. For third-party / customer connector actions, coordinate with Control 1.4 — DLP classification there is authoritative.
5. Click **Save**. Record each action change individually in the feature catalog.

### 1.8 (Brief pointer) MCP connectors, voice, image upload

These are covered in dedicated sections:

- **MCP connectors** — see [§7](#7-mcp-connectors-and-agent-framework-feature-flags).
- **Voice** — see [§8.1](#81-voice-capability-and-call-recording-consent).
- **Image upload** — see [§8.2](#82-image-upload-and-purview-dlp-for-images).

### 1.9 Verify and capture evidence

1. Re-open the **Agents & connectors** blade and re-export the capability state CSV.
2. Compare to the §1.2 baseline — every delta should match a change-management ticket.
3. Query Purview Audit for the activity `Updated Copilot capability setting` (or workload `AzureActiveDirectory` / operation `Update copilot settings`) in the window of your changes. Export JSON.
4. Store both artefacts under `Control-2.24/VC-1/capability-toggles/<YYYY-MM-DD>/`.

!!! example "Examiner Evidence Box — Capability Configuration"
    | Element | Value |
    |---|---|
    | Artifact produced | Before-and-after capability CSVs + Purview audit JSON of each toggle change + linked change-ticket IDs |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervisory system change-control), SOX §404 (IT general controls — change management), SR 11-7 / OCC 2011-12 (capability-as-model-change) |

!!! tip "Cross-Reference"
    The PowerShell / Graph equivalent of every capability toggle is documented at [`./powershell-setup.md`](./powershell-setup.md). For "capability card greyed out" or "save button not enabled" symptoms, see [`./troubleshooting.md`](./troubleshooting.md).

---

## 2. Power Platform Admin Center — Tenant-Wide Copilot Hub

**Verification Criteria evidenced:** VC-1, VC-3.

PPAC's Copilot hub is the **tenant-scoped** control surface for **Copilot Studio** (as distinct from Microsoft 365 Copilot). The capability ceiling you configured in §1 for declarative agents does **not** automatically apply to Copilot Studio agents — you must align both surfaces.

### 2.1 Open the PPAC Copilot hub

1. Sign in to [`https://admin.powerplatform.microsoft.com`](https://admin.powerplatform.microsoft.com) as **Power Platform Admin**.
2. In the left navigation, click **Copilot**. (In some tenants this is under **Resources → Copilot** or **Settings → Copilot**; search the admin center for "Copilot" if the blade is not immediately visible.)
3. Review the hub landing page. Expect to see, at minimum:
    - **Tenant settings** — tenant-wide Copilot Studio feature toggles
    - **Agents** — tenant-wide Copilot Studio agent inventory (overlap with Control 1.2 — this page is read-only here)
    - **Governance** — cross-environment governance toggles where exposed

*Screenshot anchor: `docs/images/2.24/EXPECTED.md#2-1-ppac-copilot-hub` — PPAC Copilot hub landing page with Tenant settings, Agents, and Governance cards visible.*

!!! warning "PPAC Navigation Moves Often"
    Microsoft has renamed and re-parented the PPAC Copilot hub at least three times in 2025–2026. If labels in this playbook diverge, use the URL fragment as the authoritative signal: the hub typically lives under `/manage/copilot` or `/copilot`.

### 2.2 Configure tenant-wide Copilot Studio toggles

1. Open **Copilot → Tenant settings**.
2. Review each tenant-wide toggle. Typical toggles include:
    - **Copilot Studio enabled** — master toggle (must be **On** for Copilot Studio to function anywhere)
    - **Agent sharing outside the organisation** — **Off** for Z3 tenants; Microsoft's default may be On for new tenants
    - **Publish to Microsoft 365 channels** — gated per Control 1.1
    - **Generative actions tenant default** — **Off** (require environment-level opt-in)
    - **Preview features tenant default** — **Off** (require environment-level opt-in per §3)
    - **Multi-agent orchestration tenant default** — **Off** (environment-level opt-in; orchestration-specific controls live in Control 2.17)
    - **Allow agents to publish to consumer channels** (WhatsApp, SMS, Facebook Messenger) — **Off** for FSI unless an explicit customer-communications allow-list exists under Control 1.10 and FINRA 2210 review

For each toggle:

1. Capture the current state in your runbook **before** changing.
2. Change to the FSI-recommended state per the table above.
3. Click **Save** (per-toggle or per-section, depending on UI version).
4. Record the change in the feature catalog (§5).

*Screenshot anchor: `docs/images/2.24/EXPECTED.md#2-2-tenant-toggles` — Tenant settings pane with each toggle visible and last-modified metadata.*

### 2.3 Configure DLP default for new environments

1. Open **Copilot → Governance** (or **Data policies** under the main PPAC left nav — the Governance card typically links through).
2. Confirm that a **default DLP policy for new environments** exists with a Z3-equivalent connector posture (most connectors in `Blocked` or `Non-business`). This is a cross-reference to Control 1.4; the relevance here is that a new environment must not be able to use generative AI or MCP connectors **before** it has been zoned and a tailored DLP applied.
3. If no default-new-environment DLP exists, create one now (see Control 1.4 playbook).

### 2.4 Verify hub-level posture and capture evidence

1. Export the tenant-settings CSV (if available) or screenshot the entire Tenant settings pane.
2. Query Purview Audit for workload `PowerPlatformAdmin` activities in the window of your changes. Export JSON.
3. Store under `Control-2.24/VC-1/ppac-hub/<YYYY-MM-DD>/`.

!!! example "Examiner Evidence Box — PPAC Hub Baseline"
    | Element | Value |
    |---|---|
    | Artifact produced | Tenant-settings CSV / screenshots + default-new-environment DLP screenshot + Purview audit JSON |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110, SOX §404, GLBA 501(b) |

!!! tip "Cross-Reference"
    The PowerShell equivalent via `Microsoft.PowerApps.Administration.PowerShell` and the `pac` CLI is at [`./powershell-setup.md`](./powershell-setup.md). For "Tenant settings pane empty" symptoms, see [`./troubleshooting.md`](./troubleshooting.md).

---

## 3. PPAC — Per-Environment Feature Flags and Preview Features

**Verification Criteria evidenced:** VC-1 (environment-specific feature restrictions aligned with zones), VC-2 (Z3 preview features Off or documented exception), VC-5 (high-risk features disabled in Z2/Z3).

The PPAC **Environments → [env] → Settings → Product → Features** blade is the **per-environment override** surface for Copilot Studio. Per the §1 ceiling model, environment-level toggles can only **reduce** capability beneath the tenant ceiling — they cannot raise it.

### 3.1 Enumerate in-scope environments and zone tags

1. Sign in to PPAC as **Power Platform Admin**.
2. Click **Environments**.
3. In the column chooser, enable **Display name**, **Type**, **Region**, **State**, **Zone tag** (custom column or tag per Control 2.2), **Copilot Studio enabled**, and **Last modified**.
4. Export the grid to CSV — `pp-environments-<YYYY-MM-DD>.csv`.
5. Confirm every production environment has a zone tag. Untagged environments must be resolved via Control 2.2 **before** configuring features here — otherwise you cannot defensibly choose a posture.

*Screenshot anchor: `docs/images/2.24/EXPECTED.md#3-1-environments-grid` — PPAC Environments grid with zone-tag column populated.*

### 3.2 Configure Zone 3 environment features

Open each Zone 3 environment and apply the Z3 feature posture. Repeat the procedure below per environment:

1. Click the environment name → **Settings** (top ribbon).
2. Expand **Product → Features**.
3. Review and set the following toggles (note Microsoft names may shift — re-verify quarterly):
    - **Preview features** → **Off** (mandatory for Z3 unless a documented exception with expiration exists in the feature catalog)
    - **Generative actions (AI Builder)** → **Off** unless an explicit per-action allow-list is in place (enable individual actions in the AI Builder catalog)
    - **Copilot in canvas apps** → **Off** unless required
    - **Copilot in model-driven apps** → **Off** unless required
    - **Copilot for makers** → **On** (author experience only; does not affect runtime)
    - **Natural language to SQL** → **Off** for Z3
    - **External plugins / Custom connectors in Copilot Studio agents** → **Off**; use allow-list DLP per Control 1.4
4. Click **Save**. Capture the confirmation banner and the last-modified timestamp.
5. Record each change in the feature catalog (§5) with Zone `Z3-Enterprise`, approval ticket, expiration (if time-bound), and risk rating.

*Screenshot anchor: `docs/images/2.24/EXPECTED.md#3-2-z3-features` — Environment Settings → Product → Features pane for a Z3 environment with preview features Off.*

!!! warning "Some Features Cannot Be Disabled per Environment"
    Microsoft has historically released capabilities that are only globally toggleable (or not toggleable at all — on by default for all tenants). When you encounter one, document it as a **compensating-control gap** in the feature catalog with risk rating `High` and a quarterly re-check cadence. Do **not** silently accept the gap — surface it in the Control 2.12 supervisory register and, where material, escalate to Microsoft via a service request per §★ below.

### 3.3 Configure Zone 2 environment features

Open each Zone 2 environment:

1. Settings → Product → Features.
2. Recommended posture:
    - **Preview features** → **Off** by default; may be **On** for specific evaluation environments with an expiration date ≤ 90 days in the feature catalog
    - **Generative actions** → **On** with documented per-agent approval recorded in the feature catalog
    - **Copilot in canvas / model-driven apps** → **On** if required by business
    - **Natural language to SQL** → **On** with DLP constraints on target databases
    - **Custom connectors** → **On** with Control 1.4 DLP review completed
3. Save. Record every deviation from the Z3 baseline in the feature catalog.

### 3.4 Configure Zone 1 environment features

Open each Zone 1 environment:

1. Settings → Product → Features.
2. Recommended posture:
    - **Preview features** → **On** (Zone 1 is the testbed for preview evaluation — usage drives the next quarterly risk assessment under §10)
    - **Generative actions** → **On**
    - **All other features** → Microsoft default
3. Save. Record a single "Zone 1 default posture" entry in the feature catalog per environment; you do not need a per-toggle record in Z1.

### 3.5 Deprecation queue — preview features that graduate or withdraw

Microsoft regularly (a) graduates preview features to GA, (b) withdraws preview features, or (c) renames features mid-preview. Each transition triggers feature-catalog action:

| Microsoft action | Feature catalog action | Reverse-change action |
|---|---|---|
| Preview → GA | Re-evaluate under §10 quarterly risk assessment; promote to Z2/Z3 allow-list if approved | — |
| Preview withdrawn | Mark catalog entry `Retired` with reason `Microsoft withdrawn`; capture screenshot of Message Center notice | Disable in any environment where still present; open reverse CR (§6.4) |
| Feature rename | Update `FeatureName` field; preserve original as `PreviousFeatureName` for audit trail | — |
| Preview expires (time-bound Z1/Z2 exception) | Trigger reverse CR 7 days before expiration | Disable in environment and mark catalog entry `Expired` |

### 3.6 Verify and capture evidence

1. Re-export the environments CSV with current feature state.
2. Query Purview Audit workload `PowerPlatformAdmin` for `UpdateEnvironmentFeature` operations (name varies) in the change window. Export JSON.
3. Store under `Control-2.24/VC-1/environment-features/<YYYY-MM-DD>/<env-name>/`.

!!! example "Examiner Evidence Box — Environment Feature Posture"
    | Element | Value |
    |---|---|
    | Artifact produced | Per-environment feature-state CSVs + Purview audit JSON + feature-catalog rows referencing each change ticket |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervisory system change-control per environment), SOX §404 (IT general controls), SR 11-7 / OCC 2011-12 (material model change per capability), FFIEC IT Risk Management (environment segregation) |

!!! tip "Cross-Reference"
    The PowerShell loop that applies this posture across dozens of environments is at [`./powershell-setup.md`](./powershell-setup.md). For "feature toggle not visible in environment" symptoms, see [`./troubleshooting.md`](./troubleshooting.md).

---

## 4. Copilot Studio — Per-Agent Tool, Knowledge, Auth, and Publishing Configuration

**Verification Criteria evidenced:** VC-5 (high-risk features disabled in Z2/Z3 at the agent level), VC-8 (restricted features cannot be enabled by authors in their assigned environment).

Per-agent configuration is the **tertiary enforcement layer**. Everything configured here must be **within** the environment-level ceiling (§3) and the tenant-level ceiling (§1–§2). Authors cannot exceed upstream caps.

### 4.1 Open an agent in Copilot Studio

1. Sign in to [`https://copilotstudio.microsoft.com`](https://copilotstudio.microsoft.com) as **Copilot Studio Agent Author** (or Power Platform Admin for review).
2. In the top-right environment switcher, select the target environment.
3. Click **Agents** in the left navigation and open a representative agent.
4. Open the agent's **Settings** (top ribbon).

### 4.2 Configure the **Tools** tab

1. Click **Settings → Tools** (or the **Tools** tab within the agent authoring canvas, depending on UI version).
2. Review each tool and compare to the feature catalog entry for the agent's zone:
    - **Web search** — present only if §1.3 allows AND §3 environment allows AND feature catalog entry for this specific agent exists
    - **Code interpreter** — same chain; typically only present in dedicated Z1 sandbox agents
    - **Image generation** — same chain
    - **AI Builder prompts** — each prompt should be registered in the feature catalog with a prompt ID, and the prompt library should be scoped per environment
    - **Custom connectors** — must match Control 1.4 DLP allow-list
    - **MCP server connections** — see [§7](#7-mcp-connectors-and-agent-framework-feature-flags)
3. For each tool present that is **not** justified by an active feature catalog entry, **remove** the tool. Save the agent.
4. Capture a screenshot of the Tools tab showing final state.

*Screenshot anchor: `docs/images/2.24/EXPECTED.md#4-2-agent-tools` — Agent Settings → Tools with final post-remediation state.*

!!! warning "Author Removal Is Not a Block — Use DLP and Environment Controls for Hard Enforcement"
    Removing a tool from an agent is a **soft** control — the author can add it back unless environment-level and DLP controls prevent it. Always pair per-agent cleanup with the environment-level enforcement from §3 and the DLP enforcement from §7 / Control 1.4. Otherwise the next author "helpfully" re-adds the tool next week.

### 4.3 Configure the **Knowledge** tab

1. Click **Settings → Knowledge**.
2. Review each knowledge source (SharePoint sites, files, websites, Dataverse tables, external APIs).
3. For Z2/Z3 agents, every knowledge source must:
    - Carry a Purview sensitivity label compatible with the agent's zone (see Controls 2.4–2.10)
    - Be within the DLP allow-list for the environment
    - Have an entry in the agent registry (Control 1.2) cross-referencing this agent
4. Remove any knowledge source that fails the above. Save the agent.

### 4.4 Configure the **Authentication** tab

1. Click **Settings → Security → Authentication** (exact path varies).
2. Confirm authentication posture:
    - **Z1** — Microsoft identity or Teams authentication; user-level auth acceptable
    - **Z2/Z3** — **Microsoft Entra ID authentication with service-side** configuration; **no "No authentication"**; **no anonymous**; guest users excluded unless an explicit Control 2.1 Conditional Access policy allows
3. If an agent currently uses **No authentication** and is in Z2/Z3, change to Entra authentication **before** proceeding — and treat the pre-change state as an incident requiring Control 1.10 review.
4. Save and capture screenshot.

!!! danger "Anonymous Authentication in Z2/Z3 Is a Material Audit Finding"
    Any Zone 2 or Zone 3 agent operating with "No authentication" cannot satisfy FINRA 3110 supervisory identification, GLBA 501(b) access controls, or SR 11-7 model-owner identification. Fix immediately and backfill the incident retrospectively in the Control 1.10 monitoring scope.

### 4.5 Configure the **Publishing** tab

1. Click **Publish** (top ribbon) → **Channels** (or **Settings → Channels**).
2. Confirm only **approved channels** are enabled for this agent's zone:
    - **Microsoft Teams** — most common; gated by Control 1.1
    - **Microsoft 365 Copilot Chat** — gated by Control 1.1 and Control 2.25
    - **Web / Demo site** — Z1/Z2 only; never Z3
    - **WhatsApp / SMS / Facebook Messenger / consumer channels** — Off for FSI unless a FINRA 2210 review is on file
    - **Custom website** — requires Control 1.4 review
3. Any channel enabled on a Z3 agent must have a matching row in the feature catalog and a matching approval in the Control 1.1 publishing gate.
4. Save.

### 4.6 Verify and capture evidence

1. Use the **Export agent** (solution export) feature to capture the agent's full configuration as a ZIP.
2. Hash the ZIP (SHA-256) and record the hash alongside the feature catalog entry.
3. Store under `Control-2.24/VC-5/per-agent/<env>/<agent-id>/<YYYY-MM-DD>/`.

!!! example "Examiner Evidence Box — Per-Agent Configuration"
    | Element | Value |
    |---|---|
    | Artifact produced | Agent solution-export ZIP + SHA-256 hash + screenshots of Tools / Knowledge / Authentication / Channels tabs |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervised communication scope), SR 11-7 (model configuration baselining), GLBA 501(b) (access controls) |

!!! tip "Cross-Reference"
    The `pac copilot` CLI and Dataverse Web API scripts that automate agent-configuration audits are at [`./powershell-setup.md`](./powershell-setup.md). For "Channels pane greyed out" symptoms, see [`./troubleshooting.md`](./troubleshooting.md).

---

## 5. Feature Catalog Authoring (Dataverse or SharePoint)

**Verification Criteria evidenced:** VC-4 (feature catalog deployed and maintained with current status), VC-9 (catalog includes FeatureName, ZoneStatus, ApprovalDate, ChangeTicket, ExpirationDate).

The feature catalog is a **customer-built evidence register** (see the reframing admonition at the top of this playbook). Microsoft does not host it and does not enforce against it. Its purpose is to give examiners a single, queryable, authoritative list of "which capabilities are approved in which zones, by whom, with which expiration, and against which change ticket."

### 5.1 Decide between Dataverse and SharePoint

| Criterion | Dataverse | SharePoint List |
|---|---|---|
| Programmatic query (Power Automate, Graph, PowerShell) | ✅ First-class | ⚠️ Via Graph Sites API (slower) |
| Row-level security | ✅ Security roles | ⚠️ Item-level, error-prone |
| Version history per row | ✅ Audit + change tracking with delta | ⚠️ Built-in list versioning (lighter) |
| Operating cost | Requires governance environment + Dataverse DB | Requires SPO site only |
| Examiner readability | CSV export readable | SPO list view + CSV export readable |
| Recommended for | Z3-heavy tenants, >100 catalog rows | Z1/Z2-heavy tenants, <100 catalog rows |

Document the decision in the parent control's "Backing store selection" section of your governance package.

### 5.2 Author the Dataverse table (recommended path)

1. In the **governance environment**, open [`https://make.powerapps.com`](https://make.powerapps.com).
2. Click **Tables → + New table → Start from blank**.
3. Name: `fsi_featurecatalog` (Display: **FSI Feature Catalog**).
4. Enable **Audit changes** (Settings → More settings → Auditing → On).
5. Add the following columns (minimum schema — all required unless noted):
    - **fsi_featurename** (Single line of text, 200 char) — human-readable capability name
    - **fsi_featureid** (Single line of text, 100, unique key) — stable ID (e.g., `copilot.websearch`, `ppac.preview-features`, `mcp.external-server.<host>`)
    - **fsi_surface** (Choice) — `M365 Copilot Admin`, `PPAC Copilot Hub`, `PPAC Environment`, `Copilot Studio Agent`, `DLP`, `Purview`, `Other`
    - **fsi_cloudscope** (Choice) — `Commercial`, `GCC`, `GCC High`, `DoD` (one row per cloud — never shared)
    - **fsi_z1status** (Choice) — `Allowed`, `Restricted`, `Prohibited`, `Retired`
    - **fsi_z2status** (Choice) — same
    - **fsi_z3status** (Choice) — same
    - **fsi_approvaldate** (Date)
    - **fsi_approver** (Lookup → Systemuser, or text UPN if cross-tenant)
    - **fsi_changeticket** (Single line of text) — external ticket ID (ServiceNow, Jira, Azure DevOps)
    - **fsi_expirationdate** (Date, nullable) — for time-bound exceptions
    - **fsi_riskrating** (Choice) — `Low`, `Medium`, `High`, `Critical`
    - **fsi_justification** (Multi-line text) — business justification and compensating-control summary
    - **fsi_mrmticket** (Single line of text, nullable) — Control 2.6 MRM ticket reference for Z3 / capability-as-model-change entries
    - **fsi_supervisionticket** (Single line of text, nullable) — Control 2.12 supervision-procedures update reference
    - **fsi_rollbackplan** (Multi-line text) — the reverse-change procedure if this capability must be withdrawn
    - **fsi_lastreviewedon** (Date) — last quarterly risk assessment date
    - **fsi_lastreviewedby** (Lookup → Systemuser) — AI Governance Lead who signed off
6. Set **fsi_featureid** as the alternate key.
7. Create security roles: `Feature Catalog Owner` (AI Governance Lead — create/read/update), `Feature Catalog Contributor` (Change Management Team — read/update), `Feature Catalog Reader` (everyone else — read).
8. Publish the table.

### 5.3 Author the SharePoint list (alternate path)

1. In the governance SPO site, create a list named **FSI Feature Catalog**.
2. Add columns matching the Dataverse schema in §5.2. Use SharePoint column types: Single line, Choice, Date, Multi-line, Person.
3. Apply a **retention label** (Records Management — **6 years**, locked) to the list per SEC 17a-4 retention.
4. Configure list permissions mirroring §5.2 security roles.
5. Enable **Versioning** with at least **500 major versions** retained.

### 5.4 Seed the catalog with initial entries

Populate at minimum one row per capability you configured in §1–§4. Minimum initial corpus:

| fsi_featureid | Surface | Cloud | Z1 | Z2 | Z3 | Risk |
|---|---|---|---|---|---|---|
| `copilot.websearch` | M365 Copilot Admin | Commercial | Allowed | Restricted | Prohibited | Medium |
| `copilot.codeinterpreter` | M365 Copilot Admin | Commercial | Allowed | Prohibited | Prohibited | High |
| `copilot.imagegen` | M365 Copilot Admin | Commercial | Allowed | Restricted | Prohibited | Medium |
| `copilot.filesearch` | M365 Copilot Admin | Commercial | Allowed | Allowed | Allowed (label-gated) | Low |
| `copilot.actions.first-party` | M365 Copilot Admin | Commercial | Allowed | Restricted | Restricted | Medium |
| `copilot.mcp.external` | M365 Copilot Admin | Commercial | Restricted | Prohibited | Prohibited | High |
| `copilot.voice` | M365 Copilot Admin | Commercial | Restricted | Prohibited | Prohibited | High |
| `copilot.image-upload` | M365 Copilot Admin | Commercial | Allowed | Restricted | Prohibited | Medium |
| `ppac.tenant.preview-features` | PPAC Copilot Hub | Commercial | Allowed | Prohibited | Prohibited | High |
| `ppac.tenant.generative-actions` | PPAC Copilot Hub | Commercial | Allowed | Restricted | Prohibited | High |
| `ppac.tenant.multi-agent-orchestration` | PPAC Copilot Hub | Commercial | Allowed | Restricted | Prohibited | High |
| `ppac.env.preview-features` | PPAC Environment | Commercial | Allowed | Restricted | Prohibited | High |
| `ppac.env.custom-connectors` | PPAC Environment | Commercial | Allowed | Allowed (DLP-gated) | Restricted | Medium |
| `agent.auth.anonymous` | Copilot Studio Agent | Commercial | Restricted | Prohibited | Prohibited | Critical |

Replicate every row for each **sovereign cloud** you operate in (§9). **Never** share a row across clouds.

### 5.5 Wire the catalog to the change workflow

1. In the Dataverse table, add a **Power Automate flow** trigger on `Create` and `Update` that:
    - Validates that `fsi_changeticket` is non-null for any row where `fsi_z2status` or `fsi_z3status` is `Allowed` or `Restricted` (never Z2/Z3 without a ticket)
    - Validates that `fsi_mrmticket` is non-null for rows where `fsi_riskrating` is `High` or `Critical` AND `fsi_z2status`/`fsi_z3status` is `Allowed`
    - Writes an audit row to a secondary `fsi_featurecatalog_audit` table
2. Add a scheduled flow that runs daily and emails the AI Governance Lead + Change Management Team a list of catalog rows with `fsi_expirationdate` within 7 days.
3. Add a scheduled flow that runs weekly and compares catalog rows to actual PPAC / admin-center state via the PowerShell baseline at [`./powershell-setup.md`](./powershell-setup.md), opening a ticket for any drift.

!!! example "Examiner Evidence Box — Feature Catalog"
    | Element | Value |
    |---|---|
    | Artifact produced | Dataverse `fsi_featurecatalog` export CSV + audit-table export + drift-report email archive |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) — Dataverse audit auto-retained; SPO list via records label |
    | Regulatory mapping | FINRA 3110 (supervisory change inventory), SOX §404 (change-management evidence), SR 11-7 (model inventory), GLBA 501(b) (capability inventory) |

!!! tip "Cross-Reference"
    The PowerShell / Power Automate templates to provision the catalog and its triggers are at [`./powershell-setup.md`](./powershell-setup.md). For catalog-related errors (duplicate `fsi_featureid`, alt-key collisions), see [`./troubleshooting.md`](./troubleshooting.md).

---

## 6. Change-Management Workflow — Forward and Reverse

**Verification Criteria evidenced:** VC-7 (change management is operational with documented approvals for Z2/Z3 feature changes).

Every feature-posture change — **enable or disable** — goes through a change ticket. Examiners will ask for both directions: enablement **and** withdrawal. Many organisations document only the forward path and get findings on reverse changes (features turned off hastily after CVE / withdrawal / MRM failure without a ticketed trail).

### 6.1 Forward change template (feature enablement)

Create a change request template in your change-management system. Required fields:

- **Change type:** Copilot / Agent Feature Enablement
- **Feature ID** (matches `fsi_featureid` in the catalog)
- **Target zone(s):** Z1 / Z2 / Z3
- **Target environment(s) / tenant surface**
- **Cloud:** Commercial / GCC / GCC High / DoD
- **Requester** (agent author or business owner)
- **Business justification** (≥ 200 words for Z3)
- **Risk assessment** — security, regulatory, operational (reference Control 2.6 MRM ticket for High/Critical risk)
- **Supervision impact** — Control 2.12 register update required? Ticket?
- **Compensating controls**
- **Implementation window**
- **Expiration date** (time-bound exceptions only)
- **Rollback plan** (populates `fsi_rollbackplan` in the catalog)
- **Approvals required** (see §6.3)
- **Evidence attachments** — expected screenshots, audit logs, MRM memo

### 6.2 Reverse change template (feature withdrawal / deprecation)

Create a second template — **do not reuse the forward template**. Reverse changes have different triggers and different approvers:

- **Change type:** Copilot / Agent Feature Withdrawal
- **Feature ID**
- **Trigger** (choose one):
    - CVE or security advisory
    - Microsoft preview withdrawal (attach Message Center notice)
    - MRM re-validation failed (attach Control 2.6 memo)
    - Supervision review failed (attach Control 2.12 finding)
    - Expiration of time-bound exception
    - Quarterly risk-assessment re-rating (§10)
    - Customer complaint / regulatory enquiry
- **Affected agents / environments** (query via Control 1.2 agent registry)
- **Immediate vs scheduled withdrawal**
- **Communications plan** (who tells which users / authors)
- **Evidence for catalog update** (state change to `Retired` or `Prohibited`)

!!! warning "Emergency Reverse Changes Still Need Retroactive Tickets"
    If a CVE or regulatory enquiry forces a same-hour toggle flip, **file the reverse change ticket retroactively within 24 hours**. An untracked flip is itself a finding. The emergency-change process must document the break-glass actor, the timestamp, and the post-hoc approval.

### 6.3 Approval matrix

| Zone / Risk | Forward approvers | Reverse approvers |
|---|---|---|
| Z1, risk ≤ Medium | AI Governance Lead | AI Governance Lead |
| Z1, risk High/Critical | AI Governance Lead + Security Architect | AI Governance Lead |
| Z2, risk ≤ Medium | AI Governance Lead + Power Platform Admin | AI Governance Lead + Change Management Team |
| Z2, risk High | + Compliance Officer + MRM (2.6) | Compliance Officer + Change Management Team |
| Z2, risk Critical | + Compliance Officer + MRM + Security Architect | Compliance Officer + Security Architect |
| Z3, risk ≤ Medium | AI Governance Lead + Power Platform Admin + Compliance Officer + Supervision (2.12) | Compliance Officer + Supervision + Change Management Team |
| Z3, risk High | + MRM (2.6) + Security Architect | + MRM + Security Architect + Communications Lead |
| Z3, risk Critical | + CISO / executive sponsor | + CISO / executive sponsor |

### 6.4 Walk through a forward change

**Example scenario:** a Zone 2 agent author requests enabling **Web search** on a customer-service agent.

1. Author opens the Forward change template; fills Feature ID `copilot.websearch`, target zone `Z2`, target environment `ContosoCustomerSupport-Prod`, justification, compensating controls (query allow-list, Control 1.10 monitoring, human-review of outbound communications).
2. AI Governance Lead reviews the feature catalog row for `copilot.websearch` — Z2 status is `Restricted`, meaning approval required. Reviews justification and compensating controls.
3. Power Platform Admin confirms the environment-level ceiling allows web search and that the agent's Entra group is eligible.
4. Compliance Officer reviews Control 2.12 register; confirms supervisory procedures already cover web-search-augmented customer communications.
5. MRM ticket check — web search in Z2 with label-gated sources is **not** a material model change per the firm's MRM taxonomy; no MRM ticket required. (If it **were** High/Critical risk, 2.6 ticket would be mandatory.)
6. Approvers approve in change-management system.
7. Power Platform Admin performs the toggle in §1.3 (scope group add) + §3 environment confirm + §4.2 agent tool add.
8. Author captures screenshots and attaches to the change ticket.
9. AI Governance Lead updates the feature catalog row with new `fsi_approvaldate`, `fsi_changeticket`, and (if time-bound) `fsi_expirationdate`.
10. Change Management Team closes the ticket.

### 6.5 Walk through a reverse change (Microsoft preview withdrawal)

1. Microsoft publishes an MC1234567 Message Center notice: "Retirement of preview feature X on 2026-06-30."
2. Change Management Team opens a Reverse change ticket, Feature ID `ppac.env.preview.feature.x`, Trigger `Microsoft preview withdrawal`.
3. Query Control 1.2 agent registry for agents currently using feature X; list attached to ticket.
4. Communications Lead drafts notice to affected agent authors with 14-day notice.
5. AI Governance Lead approves.
6. On scheduled date, Power Platform Admin disables feature X per-environment in §3.
7. Feature catalog row updated: `fsi_z1status` / `fsi_z2status` / `fsi_z3status` → `Retired`, `fsi_lastreviewedon` = today.
8. Ticket closed; Message Center notice archived alongside.

!!! example "Examiner Evidence Box — Change Management"
    | Element | Value |
    |---|---|
    | Artifact produced | Forward + reverse change-ticket exports from change-management system + matching feature-catalog row history + Purview audit JSON |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervisory change-control), SOX §404 (change management), SR 11-7 / OCC 2011-12 (model change management, §V — both forward and retirement), FFIEC IT Risk Management |

!!! tip "Cross-Reference"
    The verification-testing playbook includes end-to-end test cases for both forward and reverse workflows — see [`./verification-testing.md`](./verification-testing.md). For "approval workflow stalls" symptoms, see [`./troubleshooting.md`](./troubleshooting.md).

---

## 7. MCP Connectors and Agent Framework Feature Flags

**Verification Criteria evidenced:** VC-6 (DLP policies enforce feature restrictions by blocking prohibited connectors and data sources), VC-8 (restricted features cannot be enabled by authors).

MCP (Model Context Protocol) connectors and Microsoft Agent Framework feature flags are the **external tool egress** surface. This is where an agent reaches **outside** Microsoft 365 — to customer APIs, SaaS services, and third-party AI tools. For FSI, this surface is the single highest-risk capability category: it combines model egress, third-party data sharing, and often non-Microsoft identity planes.

### 7.1 MCP connectors — tenant-level allow-list in the M365 admin center

1. Return to M365 admin center → **Copilot → Settings → Agents & connectors**.
2. Open the **MCP connectors** card → **Edit**.
3. Default posture: **State = Off** at the tenant ceiling unless at least one approved MCP server is in the feature catalog.
4. If On, configure **Allowed MCP servers** as an explicit allow-list of hostnames / URLs. **Never** use a wildcard.
5. For each allowed MCP server, the feature catalog must carry a row: Feature ID `mcp.external-server.<host>`, Surface `M365 Copilot Admin`, Z1/Z2/Z3 status per the zone matrix (typically Z1 `Restricted`, Z2 `Prohibited`, Z3 `Prohibited` unless compelling justification), Risk `High`, and **MRM ticket** populated.
6. Save.

!!! danger "MCP Connectors Are Third-Party Egress — Model Risk Management Applies Regardless of Zone"
    Any MCP connector reaches a **non-Microsoft model or tool endpoint**. Treat every MCP connector as requiring a Control 2.6 MRM review **even in Z1**, and a Control 1.4 DLP review for the data classes it can reach. "Tenant allow-list" is not a substitute for vendor due diligence under OCC 2013-29 (third-party risk).

### 7.2 MCP connectors — DLP environment enforcement

1. In PPAC → **Data policies**, open the policy that covers your Z3 environments.
2. Locate the **MCP** or **Custom connectors** classification (UI naming varies).
3. Ensure it is placed in the **Blocked** group for Z3 unless a specific allow-list entry exists.
4. For Z2, place in **Non-business** (preventing cross-use with Business data) and maintain a small allow-list.
5. For Z1, Microsoft default posture may be acceptable; document in the feature catalog.
6. Save.

Cross-reference [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) for the full DLP configuration procedure. This section captures only the 2.24-specific intersection.

### 7.3 Agent Framework feature flags

The Microsoft Agent Framework exposes feature flags via the `agent.yaml` manifest (or equivalent) and via PPAC environment-level toggles:

1. In PPAC → Environments → [env] → Settings → Product → Features, locate **Agent Framework features** (or **Microsoft Agent SDK features**).
2. Review each flag. Typical flags include:
    - **Autonomous task execution** — agent can take actions without per-turn user approval
    - **Background triggers** — agent can start a run without a user message
    - **Tool chaining depth** — how many tools can be chained in one turn (relates to Control 2.17)
    - **External model routing** — agent can route parts of a turn to a non-default model
3. For Z2/Z3: **Autonomous task execution Off** and **Background triggers Off** unless an MRM-approved exception exists. These flags convert an interactive agent into an **autonomous agent**, which has materially different regulatory implications under SR 11-7 and OCC 2013-29.
4. Record every flag state in the feature catalog (one row per flag) with Risk rating `High` when On.

*Screenshot anchor: `docs/images/2.24/EXPECTED.md#7-3-agent-framework-flags` — Environment Features pane with Agent Framework flags section and recommended off state for autonomous triggers.*

### 7.4 Verify and capture evidence

1. Export the MCP allow-list from the admin center (screenshot + CSV if available).
2. Export the DLP policy JSON via `Get-DlpPolicy` (see `./powershell-setup.md`).
3. Export the Agent Framework flag state per environment.
4. Store under `Control-2.24/VC-6/mcp-and-framework/<YYYY-MM-DD>/`.

!!! example "Examiner Evidence Box — MCP and Agent Framework"
    | Element | Value |
    |---|---|
    | Artifact produced | MCP allow-list export + DLP JSON + Agent Framework flag CSV + feature-catalog rows with MRM ticket references |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | SR 11-7 / OCC 2011-12 (model change + third-party model inventory), OCC 2013-29 (third-party risk management), FINRA 3110 (supervision of external tool use), GLBA 501(b) (third-party safeguards) |

!!! tip "Cross-Reference"
    The PowerShell loops that inventory MCP connectors and Agent Framework flags across all environments are at [`./powershell-setup.md`](./powershell-setup.md). For "MCP server allow-list greyed out" symptoms, see [`./troubleshooting.md`](./troubleshooting.md).

---

## 8. Voice and Image-Upload Toggles (Consent and DLP)

**Verification Criteria evidenced:** VC-5 (high-risk features disabled in Z2/Z3), VC-6 (DLP enforcement for capability outputs).

Voice and image-upload are covered separately because they carry **specific regulatory obligations** (call-recording consent for voice; data-classification and OCR-sensitivity for images) that other capabilities do not.

### 8.1 Voice capability and call-recording consent

1. M365 admin center → **Copilot → Settings → Agents & connectors** → **Voice** card → **Edit**.
2. Default Z3 posture: **State = Off**. Voice capability in financial services creates a recordable supervisory communication that is **rarely** justifiable in Z3 without a FINRA 3110-aligned supervisory voice-recording program.
3. If On for Z1/Z2:
    - **Consent banner** — set to **Required** (shown to caller before recording starts)
    - **Recording retention** — align to Control 2.9 / FINRA 4511 — minimum 3 years, typically 7 years for broker-dealers
    - **Transcription routing** — ensure transcripts are written to a Purview-labelled location covered by Control 1.10 Communication Compliance
    - **Cross-border** — if the tenant serves EU / UK / CA / AU residents, wire GDPR / PIPEDA / Privacy Act consent flows; disable voice for those locales if consent cannot be captured
4. Save. Record in feature catalog: Feature ID `copilot.voice`, Risk `High`.

!!! danger "Voice + Customer Communication = FINRA 2210 / 3110 Scope"
    If an agent with voice capability is used for **customer-facing communications**, the resulting audio and transcript are **communications with the public** under FINRA 2210 and **supervised communications** under FINRA 3110. The feature catalog entry must reference the Control 2.12 supervisory-procedures update and the records-retention schedule. Enabling voice without those tickets is an audit finding waiting to happen.

### 8.2 Image upload and Purview DLP for images

1. M365 admin center → **Copilot → Settings → Agents & connectors** → **Image upload** card → **Edit**.
2. Default Z3 posture: **State = Off**. Image uploads frequently contain PII (driver licence scans, cheque images, account statements) that may bypass text-based DLP classifiers.
3. If On for Z1/Z2:
    - **Purview DLP for images** — confirm **On**. Requires Purview Premium / Information Protection add-on in some tenancies.
    - **OCR classification** — confirm **On** so that Purview can scan image contents for sensitive-information types.
    - **Blocked classifiers** — add at minimum: `Credit Card Number`, `U.S. Social Security Number`, `U.S. Bank Account Number`, `ABA Routing Number`, `U.S. Driver's License Number`, `U.S. Passport Number`. Firm-specific classifiers (customer account numbers) should also be included.
    - **Action on match** — **Block** upload and notify Security Architect (not just warn).
4. Save. Record in feature catalog: Feature ID `copilot.image-upload`, Risk `Medium`–`High` depending on zone.
5. In Purview → **Data Loss Prevention → Policies**, confirm an image-classification policy covers the same sensitive-information types and is **scoped to Copilot workload** (if that scope is exposed in your tenant).

### 8.3 Verify and capture evidence

1. Test voice consent banner in a Z1 sandbox agent; screenshot the banner.
2. Test image upload with a synthetic test image containing an in-classifier string (e.g., a fake SSN `000-00-0000`); confirm upload is blocked; capture Purview DLP event.
3. Store under `Control-2.24/VC-5/voice-image/<YYYY-MM-DD>/`.

!!! example "Examiner Evidence Box — Voice and Image"
    | Element | Value |
    |---|---|
    | Artifact produced | Consent-banner screenshot + image-DLP block event export + feature-catalog rows with retention and Control 2.12 references |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511); voice recordings per FINRA 4511 retention schedule |
    | Regulatory mapping | FINRA 2210 (communications with the public), FINRA 3110 (supervision), FINRA 4511 / SEC 17a-4 (records retention), GLBA 501(b) (safeguards on sensitive images), GDPR / state privacy laws (consent) |

!!! tip "Cross-Reference"
    Communication Compliance scoping for voice transcripts is covered in [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md). For "Purview image DLP not triggering" symptoms, see [`./troubleshooting.md`](./troubleshooting.md).

---

## 9. Sovereign Cloud Compensating Control (GCC / GCC High / DoD)

**Audience:** operators in M365 GCC, GCC High, or DoD tenants. Skip this section if you are in M365 Commercial.

As of the verification date, many capabilities documented above (select MCP connectors, image generation, voice, and most Agent Framework features) are **not available** in US sovereign clouds. Microsoft has not committed to timelines for most of them. Until parity arrives, sovereign-cloud FSI organisations cannot rely on the admin-center surfaces described in §1, §7, and §8. Examiners (FFIEC IT Handbook, OCC Heightened Standards, DoD SRG) will still expect equivalent governance evidence. The substitute is a **dual-catalog + quarterly attestation** pattern.

### 9.1 Separate feature catalog per sovereign cloud

1. Provision a **separate Dataverse instance** (or separate SharePoint site) **in the sovereign tenant** — never in Commercial, never shared. The sovereign instance hosts its own `fsi_featurecatalog` with the same schema as §5.2 but with `fsi_cloudscope` set to the sovereign cloud.
2. **Do not copy rows from the Commercial catalog.** Each capability in sovereign requires an independent approval record, risk assessment, and (where applicable) MRM ticket. Inherited approvals are an audit finding under OCC 2013-29.
3. Seed the sovereign catalog with **only** the capabilities available in that cloud, per the cloud-specific service description. Mark unavailable capabilities as `Unavailable (product gap)` — not as `Prohibited`. This is a Microsoft product limitation, not an FSI policy decision, and belongs in examination briefing materials under that framing.

### 9.2 Manual quarterly attestation for sovereign feature inventory

1. Pull the sovereign feature-catalog CSV and the agent-registry CSV from [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md).
2. Distribute to AI Governance Lead, Compliance Officer, and each agent sponsor via a Purview-labelled attestation workbook.
3. Each sponsor attests in writing that:
    - They understand the capability posture currently allowed in the sovereign cloud.
    - They have not attempted to reach Commercial-only capabilities via unapproved channels (e.g., cross-cloud tenants, shadow IT).
    - Any capability gap vs Commercial is documented and accepted.
4. Archive attestations in a Purview-immutable location with 6-year retention (records-management label, locked policy).

### 9.3 Compensating-control mapping (Commercial capability → sovereign substitute)

| Commercial capability | Sovereign substitute | Residual risk |
|---|---|---|
| Tenant-level MCP connector allow-list | Hard prohibition in DLP (Control 1.4) + manual attestation that no out-of-band MCP channel exists | Shadow-IT circumvention risk |
| Voice capability with Purview-labelled transcripts | Third-party (e.g., Teams Phone recording with on-tenant retention) — document as Control 2.9 variant | Feature-parity lag |
| Image upload with Purview DLP classifiers | Block uploads at Copilot tenant level; manually review any approved use case via Control 1.10 | OCR-DLP not available in all sovereign tiers |
| Preview-feature exposure | Preview features are typically unavailable in sovereign; this is neutral — note in feature catalog | — |
| Agent Framework autonomous triggers | Not available; document product gap | Feature-parity lag |
| Message Center notices re: preview withdrawal | Sovereign Message Center lags; check Commercial Message Center for forward-looking visibility and plan ahead | Withdrawal-notice latency |

### 9.4 Cloud-parity cutover

When Microsoft announces a capability GA for your sovereign cloud, do **not** silently enable it. Treat cloud parity as a **controlled change**: open a forward change ticket per §6, dual-run Commercial + sovereign catalogs for one full quarter, obtain compliance sign-off, and only then retire the `Unavailable` marker in the sovereign catalog. Document the cutover in your change-management system per Control 2.16.

!!! example "Examiner Evidence Box — Sovereign Compensating Control"
    | Element | Value |
    |---|---|
    | Artifact produced | Sovereign feature-catalog export + quarterly attestation archive + compensating-control mapping memo + Microsoft service description citations |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511); longer where DoD contract schedules require |
    | Regulatory mapping | FFIEC IT Handbook, OCC 2013-29 (third-party / cloud risk), DoD SRG (sovereign cloud controls), FINRA 3110 (supervision — feature-parity gaps), SR 11-7 (model-inventory per cloud) |

---

## 10. Zone Cadence Checklists (Z1 / Z2 / Z3)

**Verification Criterion evidenced:** VC-10 (quarterly feature risk assessment with documented results).

Cadence is the discipline that keeps this control effective over time. Microsoft ships new capabilities roughly monthly; without a cadence the feature catalog decays into fiction.

### 10.1 Zone 1 cadence — Personal productivity

| Cadence | Activity | Owner | Evidence |
|---|---|---|---|
| Monthly | Scan Message Center for new previews; add to Z1 catalog rows | AI Governance Lead | Message Center archive + catalog row deltas |
| Monthly | Review preview-feature usage telemetry from PPAC analytics | AI Governance Lead | Telemetry export |
| Quarterly | Risk assessment of every Z1 capability currently in use; promote candidates to Z2/Z3 review | AI Governance Lead + Security Architect | Risk-assessment memo + catalog `fsi_lastreviewedon` update |
| On preview withdrawal | Reverse change per §6.5 | Change Management Team | Reverse change ticket |

### 10.2 Zone 2 cadence — Team collaboration

| Cadence | Activity | Owner | Evidence |
|---|---|---|---|
| Weekly | Drift-check — compare PPAC state to Z2 catalog rows (automated scheduled flow from §5.5) | AI Governance Lead | Drift-report email archive |
| Monthly | Capability usage report per environment (Control 1.10 supervisory digest input) | Power Platform Admin | Usage report |
| Quarterly | Risk re-rating of every Z2 capability; expiration review for time-bound exceptions | AI Governance Lead + Compliance Officer | Risk-assessment memo + expiration-remediation log |
| On expiration | Reverse change per §6.5 | Change Management Team | Reverse change ticket |
| On MRM trigger | Re-validation per Control 2.6 | MRM team | MRM memo referenced in `fsi_mrmticket` |

### 10.3 Zone 3 cadence — Enterprise / regulated

| Cadence | Activity | Owner | Evidence |
|---|---|---|---|
| Daily | Expiration-alert email (automated from §5.5) | AI Governance Lead | Email archive |
| Weekly | Drift-check + full capability baseline export | Power Platform Admin | CSV archive |
| Monthly | Supervisory digest (Control 2.12 register update) | Compliance Officer | Register update + sign-off |
| Monthly | Capability usage report + Communication Compliance sampling (Control 1.10) | Compliance Officer | CC digest |
| Quarterly | Formal feature risk assessment — attestation by AI Governance Lead + Compliance Officer + Security Architect; signed memo | AI Governance Lead | Signed quarterly memo |
| Annually | Independent-function review of feature catalog + change-workflow effectiveness | Internal Audit | Audit report |
| On MRM trigger | Re-validation per Control 2.6 | MRM team | MRM memo |
| On supervision trigger | Supervisory procedures update per Control 2.12 | Compliance Officer | Register update |
| On withdrawal | Reverse change per §6.5 within 48 hours of trigger | Change Management Team | Reverse change ticket + 1.2 registry update |

!!! example "Examiner Evidence Box — Quarterly Risk Assessment"
    | Element | Value |
    |---|---|
    | Artifact produced | Signed quarterly memo (AI Governance Lead + Compliance Officer + Security Architect) listing every capability reviewed, rating, status change, and change-ticket references |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (periodic supervisory review), SOX §404 (control-effectiveness attestation), SR 11-7 (ongoing model monitoring — capability scope), FFIEC IT Risk Management (periodic re-risk) |

---

## 11. Evidence Capture per Session

Every session in which you change capability posture — even a single toggle — should produce a named evidence bundle. This section prescribes the minimum bundle and folder convention so examiner walk-throughs do not require forensic reconstruction.

### 11.1 Folder convention

```
Control-2.24/
  <VC-N>/                          # Verification Criterion grouping
    <activity-name>/               # e.g., capability-toggles, environment-features, feature-catalog
      <YYYY-MM-DD>/                # Session date
        baseline/                  # Pre-change state
        screenshots/               # PNG, ordered by step number
        exports/                   # CSVs, JSON, solution ZIPs
        audit-logs/                # Purview Audit JSON exports
        change-tickets/            # PDF/JSON exports from change-management system
        signoff/                   # Approval emails, meeting notes
        README.md                  # Session narrative
```

### 11.2 Minimum bundle contents per session

- [ ] **README.md** with session narrative (who, when, why, what changed, which change ticket)
- [ ] **Baseline CSV / screenshots** captured **before** any change
- [ ] **Screenshot set** with at least one screenshot per toggle change, named `<step>.<capability>.<state>.png`
- [ ] **Export CSV / JSON** of post-change state
- [ ] **Purview Audit JSON** filtered to the session window (operator UPN + time range)
- [ ] **Feature-catalog row export** showing new or updated rows
- [ ] **Change-ticket PDF** with approval chain visible
- [ ] **Hash file** (SHA-256) of every binary artefact in the bundle

### 11.3 Session README template

```markdown
# Control 2.24 Session Evidence — <YYYY-MM-DD> — <activity>

**Operator:** <UPN>
**Role activated (PIM):** AI Administrator / Power Platform Admin
**Tenant:** <domain> (Tenant ID: <GUID>)
**Cloud:** Commercial / GCC / GCC High / DoD
**Change tickets:** CR-#####, CR-#####
**Verification Criteria addressed:** VC-1, VC-5

## Summary of changes
- Capability X enabled for group Y in scope Z1 (CR-12345)
- Capability W disabled in environment E3-Prod (reverse CR-12346, Microsoft preview withdrawal)

## Evidence artefacts
- `baseline/capability-baseline-pre.csv`
- `screenshots/01.websearch.off-to-on.png` ... `05.websearch.save-confirm.png`
- `exports/capability-baseline-post.csv`
- `audit-logs/purview-audit-<time-range>.json`
- `change-tickets/CR-12345.pdf`
- `signoff/aigov-lead-approval-<date>.eml`
- `hashes.txt` (SHA-256 of all binary artefacts)

## Feature-catalog delta
- `fsi_featurecatalog` row `copilot.websearch` updated: Z2 `Prohibited` → `Restricted`, approver, expiration 2026-10-31

## Follow-ups
- MRM ticket MRM-789 pending for Z3 consideration
- Control 2.12 register update filed under CR-12347
```

### 11.4 Retention

Bundle retention is **6 years** per SEC 17a-4 / FINRA 4511. For tenants that operate under DoD contract or additional state-level retention (NYDFS, MA 201 CMR 17), extend per the longer schedule. Store in an immutable (WORM) Purview records location or equivalent.

---

## 12. Cross-References and Sibling Routing

| If you need to … | Use this control / playbook |
|---|---|
| Restrict **who** can publish at all | [Control 1.1 — Restrict Agent Publishing by Authorization](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) |
| Inventory existing agents | [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |
| Classify connectors Business / Non-business / Blocked | [Control 1.4 — Advanced Connector Policies (ACP)](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) |
| Monitor agent output for supervisory review | [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) |
| Tier environments into zones | [Control 2.2 — Environment Groups and Tier Classification](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) |
| Re-validate a capability change as a model change | [Control 2.6 — Model Risk Management (OCC 2011-12 / SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) |
| Update supervisory procedures for a new capability | [Control 2.12 — Supervision and Oversight (FINRA 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |
| Limit multi-agent orchestration depth, hop count, token budget | [Control 2.17 — Multi-Agent Orchestration Limits](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) |
| Surface / block an individual agent through the Agent 365 console | [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) |
| Automate these same surfaces via PowerShell / Graph | [`./powershell-setup.md`](./powershell-setup.md) |
| Run test cases and evidence collection end-to-end | [`./verification-testing.md`](./verification-testing.md) |
| Diagnose missing blades, greyed toggles, propagation delays | [`./troubleshooting.md`](./troubleshooting.md) |
| Understand zone definitions | [Framework — Agent Zones](../../../framework/zones-and-tiers.md) |

---

## Closing Decision Matrix and Readiness Checklist

### Portal vs PowerShell vs Graph

This walkthrough used the portal end-to-end for clarity and screenshot evidence. In production, mix surfaces. Use this matrix to choose the right surface per task.

| Task | Portal | PowerShell | Graph REST | Recommended for FSI |
|---|---|---|---|---|
| Tenant capability baseline capture (first time) | ✅ | ✅ | ✅ | **Portal** for the initial baseline — examiner-readable screenshots; **PowerShell** thereafter for repeatability |
| Tenant capability toggle change (single) | ✅ | ✅ | ✅ | **Portal** — ceremonial, change-ticket visible in PIM activation |
| Bulk per-environment feature posture across >10 environments | ❌ Tedious | ✅ `Get-/Set-PowerAppEnvironmentFeature` | ✅ | **PowerShell** — portal does not scale |
| Feature-catalog CRUD | ✅ | ✅ Dataverse Web API | ✅ | **PowerShell / Power Automate** for drift detection; portal for ceremonial edits |
| Drift detection PPAC vs catalog | ❌ | ✅ Scheduled flow | ✅ | **PowerShell / Power Automate** — see [`./powershell-setup.md`](./powershell-setup.md) |
| MCP allow-list edit | ✅ | ⚠️ Limited Graph support | ⚠️ | **Portal** — MCP allow-list is low-volume, ceremonial |
| DLP policy change for connector / MCP enforcement | ✅ | ✅ `Get-/Set-DlpPolicy` | — | **PowerShell** for IaC parity; portal for initial design |
| Per-agent tool/knowledge/auth audit across >20 agents | ❌ | ✅ `pac copilot` + Dataverse Web API | ✅ | **PowerShell** |
| Change-ticket processing | ❌ | — | — | **Change-management system native** — integrate via webhook |
| Evidence capture per session | ✅ Screenshots | ✅ Scripted exports | ✅ | **Both** — screenshots for ceremony, scripts for completeness |

### When to escalate to Microsoft support

Open a Microsoft service request (M365 admin → Support → New service request) for:

- **Capability toggle greyed out or "save" button inactive** despite correct role (AI Administrator for Copilot, Power Platform Admin for PPAC). Category: Microsoft 365 → Copilot → Configuration.
- **Preview feature that cannot be disabled in PPAC** but is creating audit exposure. Category: Power Platform → Admin Center → Copilot.
- **MCP allow-list changes not propagating after 24 hours.** Category: Microsoft 365 → Copilot → Agents & connectors.
- **Purview image-DLP classifier not triggering despite On state and Premium licensing.** Category: Microsoft Purview → DLP.
- **Voice consent banner not rendering for specific locales.** Category: Microsoft 365 → Copilot → Voice.

Record support case numbers in the feature-catalog row for the affected capability under a new `fsi_supportcase` column if you operate with high support-ticket volume.

### Final readiness checklist

Before declaring Control 2.24 implemented, confirm:

- [ ] §0 pre-flight gates all pass; AI Administrator PIM-eligible not permanent.
- [ ] §1 M365 admin center capability toggles configured and baselined; evidence bundle archived.
- [ ] §2 PPAC tenant-wide Copilot hub toggles aligned to Z3-default posture; default-new-environment DLP exists.
- [ ] §3 per-environment feature flags configured per zone; preview features Off in Z3 or documented exception with expiration.
- [ ] §4 per-agent Tools, Knowledge, Authentication, Channels reviewed; no anonymous auth in Z2/Z3; solution-export hashes archived.
- [ ] §5 feature catalog provisioned (Dataverse preferred for Z3-heavy tenants); schema includes all required fields; drift-detection flow active.
- [ ] §6 forward AND reverse change templates exist in change-management system; approval matrix documented; walk-through of one forward change and one reverse change completed and archived.
- [ ] §7 MCP allow-list configured (or Off); Agent Framework autonomous/background flags Off in Z2/Z3; DLP enforcement aligned with Control 1.4.
- [ ] §8 voice posture aligned to FINRA 2210/3110; image-upload Purview DLP classifiers active and tested with synthetic content.
- [ ] §9 sovereign compensating control implemented (separate catalog, quarterly attestation) if operating in GCC / GCC High / DoD.
- [ ] §10 zone-cadence calendar entries created; quarterly risk-assessment memo template published.
- [ ] §11 evidence-bundle folder convention in use; at least one session archived to validate the process.
- [ ] §12 cross-references communicated to AI Governance Lead and Compliance Officer; sibling playbooks (`powershell-setup.md`, `verification-testing.md`, `troubleshooting.md`) reviewed.
- [ ] Control 1.1 publishing-authorisation, Control 2.6 MRM, and Control 2.12 supervisory register all updated to reflect current capability posture.

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
