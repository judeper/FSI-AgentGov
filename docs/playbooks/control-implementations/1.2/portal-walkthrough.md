# Control 1.2 — Portal Walkthrough: Agent Registry & Integrated Apps Management

**Control ID:** 1.2 — Agent Registry and Integrated Apps Management
**Pillar:** 1 — Security & Identity
**Last UI Verified:** May 2026
**Estimated Time:** 6–10 hours initial buildout; 60–90 min per agent registration thereafter
**Audience:** Entra App Admin, AI Administrator, Power Platform Admin, Compliance Officer, Agent Sponsor
**Prerequisites:** Control 1.1 (Conditional Access for Agents) implemented; sponsor eligibility groups provisioned per `sponsorship-lifecycle-workflows.md`; Microsoft 365 E5 + Microsoft Entra ID P2 + Defender for Cloud Apps + Purview Audit (Premium) tenant licensing.

---

!!! danger "READ FIRST — Scope and Sibling Routing"
    This walkthrough operationalizes the **registration plane** of Control 1.2: the seven Microsoft administrative surfaces where an agent identity, integrated app, connector, or workload identity is created, sponsored, consented to, monitored, and ultimately retired. It is the entry door to every other Pillar 1 and Pillar 3 control.

    **This walkthrough IS:**

    - The canonical procedure for registering a new agent across all seven surfaces (Entra App Registrations, Entra Enterprise Apps / Agent ID, Microsoft 365 Integrated Apps, Microsoft 365 Agents blade / Agent 365 preview, Power Platform Admin Center Copilot Agents, Defender for Cloud Apps OAuth governance, and Connectors approval queue).
    - The portal-side implementation of the canonical metadata schema, the consent governance workflow, service principal & managed identity hygiene, and the quarterly three-signature attestation cycle.
    - The point-in-time evidence collection runbook examiners walk during FINRA, SEC, OCC, NYDFS, and Federal Reserve exams.

    **This walkthrough is NOT:**

    | Topic | Where it lives |
    |-------|----------------|
    | Sponsor eligibility group creation, Lifecycle Workflow JSON, sponsor-departure detection logic, Zone 3 24-hour suspension automation | `sponsorship-lifecycle-workflows.md` (sibling) |
    | Conditional Access policies for human users invoking agents | `../1.1-conditional-access-for-agents/portal-walkthrough.md` |
    | Connector classification (Business / Non-Business / Blocked) and DLP policy authoring | `../1.4-advanced-connector-policies-acp.md` portal walkthrough |
    | Audit log retention, eDiscovery hold, and 7-year WORM archive plumbing | `../1.7-comprehensive-audit-logging-and-compliance.md` |
    | Step-up authentication for high-risk agent operations | `../1.23-step-up-authentication-for-agent-operations.md` |
    | Defender XDR / AI-SPM posture findings triage | `../1.24-defender-ai-security-posture-management.md` |
    | The unified inventory database, reconciliation cadence, and orphaned-agent sweep | `../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md` and `../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md` |
    | Communication compliance supervision of agent outputs | `../1.10-communication-compliance-monitoring.md` |
    | Incident response when a registered agent is implicated | `../../incident-and-risk/ai-incident-response-playbook.md` |

    If your task maps to a row above, stop and route to the linked playbook. Continuing here will produce duplicate or conflicting evidence.

!!! warning "Hedged-Language Reminder (Mandatory)"
    Throughout this playbook — and in any derivative runbook, ticket template, attestation memo, or examiner-response narrative your team produces — the following overclaim phrases **must not appear**:

    - "ensures compliance with..." → use **"supports compliance with..."**
    - "guarantees..." → use **"is designed to..."** or **"helps the organization..."**
    - "will prevent..." → use **"is intended to reduce the likelihood of..."**
    - "eliminates the risk of..." → use **"helps mitigate..."**

    Microsoft 365, Power Platform, and Defender controls operate on tenant configuration, license entitlement, and operator discipline. They reduce risk surface; they do not — and cannot — produce a legal compliance guarantee. Examiners and outside counsel read every control narrative; an unhedged sentence in a registry attestation is the single fastest way to convert a routine inquiry into a finding. When in doubt, attach the qualifier "**Implementation requires sustained operator discipline; organizations should verify configuration against current regulatory expectations and their own legal counsel's interpretation.**"

!!! info "License Requirements"
    The registration surfaces and governance features used in this playbook depend on the following licensing baselines. Verify entitlement in the Microsoft 365 admin center → **Billing → Licenses** before beginning. Missing a single SKU below will cause one of the surfaces to silently degrade — most often Agent ID, Defender OAuth governance, or Identity Governance access reviews.

    | Capability used in this playbook | Required SKU(s) |
    |----------------------------------|-----------------|
    | Entra App Registrations, Enterprise Apps, owner enforcement | Microsoft Entra ID Free (included with M365) |
    | Conditional Access for workload identities (§12) | **Microsoft Entra Workload Identities Premium** (separate add-on; not part of Entra ID P2) |
    | Identity Governance access reviews on app assignments and owners | **Microsoft Entra ID Governance** (or Entra ID P2 for the basic access review feature) |
    | Lifecycle Workflows for sponsor-departure automation | Microsoft Entra ID Governance |
    | Agent ID surface in Enterprise Applications | Tenant must have **Microsoft 365 Copilot** licenses provisioned; surface enables only after first agent is created in Microsoft Copilot Studio or Agent Builder |
    | Microsoft 365 Integrated Apps blade (deploy / block / pending requests) | Microsoft 365 Apps for Enterprise or higher |
    | Microsoft 365 Agents blade and Agent 365 (preview) | **Microsoft 365 Copilot** + tenant opt-in to Agent 365 preview program |
    | Power Platform Admin Center → Copilot agents resource view | Power Platform admin center access (no additional SKU); managed environments features require **Power Platform Managed Environments** add-on |
    | Connectors approval workflow (custom and certified connector requests) | Power Platform Managed Environments recommended; basic queue available without |
    | Defender for Cloud Apps — Cloud Discovery and OAuth app governance | **Microsoft Defender for Cloud Apps** standalone or as part of Microsoft 365 E5 Security |
    | Purview Audit (Premium) — 1-year default + 10-year add-on retention used in §15 examiner audit-pull | **Microsoft Purview Audit (Premium)** + **10-Year Audit Log Retention** add-on |
    | Communication Compliance integration referenced in §16 | **Microsoft Purview Communication Compliance** (E5 Compliance) |
    | Step-up auth referenced in §16 | Entra ID P2 + Authentication Strengths feature |


---

## §0 — Coverage Boundary, Registration Surfaces, and Portal-vs-PowerShell Decision Matrix

### 0.1 What Control 1.2 Owns vs. What It Doesn't

Control 1.2 owns the **identity-of-record** for every AI agent, integrated app, connector-bound flow, and workload identity in the tenant. The "identity-of-record" is the canonical row that downstream controls (3.1 inventory, 3.6 orphan detection, 1.7 audit, 1.10 supervision, 1.23 step-up) join against. If a surface can mint a callable identity that touches Microsoft Graph, SharePoint, Exchange, or Dataverse, it is in scope here.

| In scope for 1.2 | Out of scope for 1.2 (linked control) |
|------------------|---------------------------------------|
| Creating an Entra app registration with sponsor metadata | Authoring the Conditional Access policy that scopes that app (1.1) |
| Registering a Copilot Studio agent in the M365 Agents blade | Reviewing what Graph data the agent retrieved (1.7, 1.10) |
| Approving a custom Power Platform connector | Classifying the connector Business / Non-Business (1.4) |
| Capturing the SP/MI hygiene snapshot quarterly | Remediating an orphaned SP found in the snapshot (3.6) |
| Documenting agent owner, sponsor, backup owner, business justification | Running the sponsor-departure Lifecycle Workflow (sibling playbook) |
| Three-signature attestation of the registry | Generating the management dashboard from registry data (3.5, 3.7) |

### 0.2 The Seven Registration Surfaces

A US financial services tenant typically exposes seven distinct surfaces where an agent identity can be born. Missing any one of them produces a registry blind spot — and a registry blind spot is, in practical terms, an unsupervised agent.

| # | Surface | Portal path | What gets registered here | Primary admin role |
|---|---------|-------------|---------------------------|-------------------|
| 1 | **Entra App Registrations** | `entra.microsoft.com` → Applications → App registrations | Custom-built apps and confidential clients with API permissions | Entra App Admin |
| 2 | **Entra Enterprise Applications** (incl. Agent ID surface) | `entra.microsoft.com` → Applications → Enterprise applications | Service principals (the tenant-side projection of every app), gallery apps, and the Agent ID surface for Copilot agents | Entra App Admin / Entra Agent ID Admin |
| 3 | **M365 Integrated Apps** | `admin.microsoft.com` → Settings → Integrated apps | Third-party Microsoft 365 add-ins, Teams apps, Outlook add-ins; Deploy / Block / Pending request queue | AI Administrator |
| 4 | **M365 Agents blade / Agent 365 (preview)** | `admin.microsoft.com` → Copilot → Agents | First-party Copilot agents, declarative agents, custom Copilot agents | AI Administrator |
| 5 | **Power Platform Admin Center → Copilot Agents** | `admin.powerplatform.microsoft.com` → Resources → Copilot agents | Copilot Studio agents per environment | Power Platform Admin |
| 6 | **Power Platform Connectors approval queue** | `admin.powerplatform.microsoft.com` → Data → Custom connectors / Connector requests | Custom connectors and certified-connector requests | Power Platform Admin |
| 7 | **Defender for Cloud Apps — OAuth App Governance** | `security.microsoft.com` → Cloud apps → OAuth apps | OAuth-consented third-party apps discovered post-consent | Entra Security Admin |

!!! tip "The eighth-surface trap"
    Watch for **shadow surfaces** that look like registration but aren't governed: Teams app personal sideloads (governed via Teams Apps policies — outside 1.2), Power Automate cloud flows owned by individuals using only standard connectors (governed via 1.4 DLP policies), and SharePoint app-only tokens minted via legacy ACS (deprecated; flag for retirement in §10). These should **not** be added as a "surface 8" — they are eradication targets, not registration surfaces.

### 0.3 Portal-vs-PowerShell Decision Matrix

Every step in this playbook can be performed in the portal or in PowerShell. Use this matrix to decide:

| Activity | Portal | PowerShell | Recommendation |
|----------|:------:|:----------:|----------------|
| First-time registration of one agent | ✅ | ✅ | **Portal** — visual confirmation of metadata fields prevents typo errors that downstream reconciliation will surface as orphans |
| Bulk owner backfill across 50+ existing apps | ⚠️ Tedious | ✅ | **PowerShell** (see `powershell-setup.md`) |
| Quarterly SP/MI hygiene snapshot | ⚠️ Incomplete | ✅ | **PowerShell** — the portal cannot enumerate all credential expirations or last-sign-in dates in one view |
| Examiner audit-pull (point-in-time reconstruction) | ⚠️ Slow | ✅ | **PowerShell** for data extraction; portal screenshots for visual evidence |
| Three-signature attestation | ✅ | ❌ | **Portal** — the human signatures are the control |
| Sponsor metadata update on existing agent | ✅ | ✅ | Either; portal is auditable per-field |
| Consent grant approval | ✅ | ⚠️ Possible | **Portal** — admin consent grants must be reviewed visually in the consent request blade |
| Agent retirement and SP deletion | ✅ | ✅ | **PowerShell** for SP deletion; **portal** to verify the registry status field flips to `Retired` |

When you use PowerShell for any step, re-open the corresponding portal blade and screenshot the resulting state. The screenshot, with timestamp and admin upn visible, is the audit evidence — the script log is corroborating.

---

## §1 — The Canonical Registration Metadata Schema

Every row written to the agent registry — regardless of which of the seven surfaces it originates from — must carry the following 22 fields. This schema is the contract between Control 1.2 (registration) and Control 3.1 (inventory). Field names below are the canonical column names used by the reconciliation jobs in 3.1; if you rename any of them in your tenant, update the 3.1 mapping table in lockstep.

| # | Field | Source | Required for Zone | Notes |
|---|-------|--------|:-----------------:|-------|
| 1 | `agent_id` | Entra ObjectId or Power Platform agent GUID | 1, 2, 3 | Immutable; primary key |
| 2 | `display_name` | Surface display name | 1, 2, 3 | Must follow naming standard `<env>-<bu>-<purpose>-<seq>` |
| 3 | `surface_origin` | One of the 7 surfaces in §0.2 | 1, 2, 3 | |
| 4 | `agent_type` | Declarative / Custom-built / Connector-bound flow / Third-party add-in / Workload identity | 1, 2, 3 | |
| 5 | `zone` | 1 (Personal) / 2 (Team) / 3 (Enterprise) | 1, 2, 3 | Drives all downstream policy |
| 6 | `business_unit` | Free text, controlled vocabulary | 1, 2, 3 | Maps to cost center |
| 7 | `agent_owner_upn` | Entra UPN | 1, 2, 3 | Operationally responsible |
| 8 | `backup_owner_upn` | Entra UPN | 2, 3 | Required for Z2/Z3 to satisfy 3.6 orphan threshold |
| 9 | `agent_sponsor_upn` | Entra UPN | 1, 2, 3 | Must be member of `sg-agent-sponsors-zone<n>` per sibling playbook |
| 10 | `compliance_officer_upn` | Entra UPN | 3 | Required for Zone 3 attestation; recommended for Zone 2 |
| 11 | `business_justification` | Free text, ≥ 200 chars | 1, 2, 3 | Examiner artifact — write it as if FINRA will read it (they will) |
| 12 | `data_classification_max` | Public / Internal / Confidential / Restricted (NPI / MNPI) | 1, 2, 3 | Drives 1.4 connector and 1.10 supervision scope |
| 13 | `regulated_data_in_scope` | Bool array: NPI / MNPI / PCI / PHI / Customer-Identifiable / Trade-Surveillance | 1, 2, 3 | If any TRUE, automatic Zone 3 |
| 14 | `connectors_used` | Array of connector IDs from 1.4 catalog | 1, 2, 3 | Cross-checked against 1.4 DLP policy |
| 15 | `graph_permissions_granted` | Array of Graph scopes | 1, 2, 3 | Captured at consent time |
| 16 | `step_up_required` | Bool | 2, 3 | Triggers 1.23 enforcement; mandatory TRUE if Zone 3 |
| 17 | `creation_date` | Timestamp | 1, 2, 3 | Auto |
| 18 | `last_attestation_date` | Timestamp | 1, 2, 3 | Updated by §14 quarterly cycle |
| 19 | `attestation_status` | Current / Past-due / Suspended / Retired | 1, 2, 3 | |
| 20 | `compensating_controls` | Free text or N/A | 1, 2, 3 | Document any compensating controls for preview or unavailable capabilities |
| 21 | `retirement_date` | Timestamp or NULL | 1, 2, 3 | Set when retired; never reuse a retired `agent_id` |
| 22 | `evidence_pack_uri` | SharePoint URL to evidence folder | 1, 2, 3 | Folder must inherit retention label from §15 |

!!! note "Where the schema lives physically"
    The portal does not give you 22 free-form fields on any single blade. In practice the schema is materialized by:

    - **Entra App Registration / Enterprise App** — fields 1–4 native; fields 5–13, 16, 20 stored as **App-role custom security attributes** (Entra → Protection → Custom security attributes); fields 7, 8, 9 stored as **owners** (Entra App Admin → Owners blade) **and** mirrored into custom security attributes for query.
    - **M365 Integrated Apps / Agents blade** — limited custom-metadata support; mirror the schema into an external registry (SharePoint list, Dataverse table, or your GRC tool) keyed by `agent_id`.
    - **Power Platform Copilot Agents** — agent properties JSON supports tags; mirror the schema into Dataverse via the Power Platform CoE Starter Kit `cr_AgentRegistry` table.

    The reconciliation job in Control 3.1 walks all three stores nightly and flags any `agent_id` missing from any of them as a schema-integrity finding.

---

## §2 — Pre-Flight Gates (Run Before Any Registration)

Before you register a single agent, complete these gates. Each gate has a portal-side check and a PowerShell verification. Skipping a gate is the most common root cause of registry drift discovered during examiner pulls.

### 2.1 Gate A — Sponsor Eligibility Groups Exist and Are Populated

1. Open `entra.microsoft.com` → **Groups → All groups**.
2. Search for `sg-agent-sponsors-zone1`, `sg-agent-sponsors-zone2`, `sg-agent-sponsors-zone3`.
3. Confirm each group exists, is **Assigned** type (not Dynamic), and has **Privileged Access Group** management enabled.
4. Confirm membership is non-empty and is governed by an active **Identity Governance access package** (visible under Identity Governance → Access packages).

   *Screenshot description: Three group result rows showing names sg-agent-sponsors-zone1/2/3 with Type=Security and Membership type=Assigned. Privileged Access management toggle visible as Enabled in group properties pane.*

5. If any group is missing or empty, **stop** and complete the sibling playbook `sponsorship-lifecycle-workflows.md` §2 first.

### 2.2 Gate B — Custom Security Attributes Defined

1. Open `entra.microsoft.com` → **Protection → Custom security attributes**.
2. Confirm an attribute set named `AgentRegistry` exists, with at least these attributes defined: `Zone`, `BusinessUnit`, `AgentSponsor`, `BackupOwner`, `ComplianceOfficer`, `DataClassificationMax`, `RegulatedDataInScope`, `StepUpRequired`, `CompensatingControls`.
3. Confirm the **Attribute Assignment Reader** and **Attribute Assignment Administrator** roles are scoped to the App Admin team and the Compliance team respectively.
4. If the set or any attribute is missing, create per the schema in §1 before proceeding. (PowerShell automation in `powershell-setup.md` §3.)

### 2.3 Gate C — Audit Logging Active and Retention Confirmed

1. Open `purview.microsoft.com` → **Audit**.
2. Confirm the banner reads "Auditing is on" — not "Start recording user and admin activity".
3. Open `purview.microsoft.com` → **Data lifecycle management → Retention policies**.
4. Confirm a retention policy named `AgentRegistry-AuditEvidence-7yr` exists, scoped to the SharePoint site that holds evidence packs (field 22 in §1), with retention period `7 years` and disposition `Retain only — do not delete`.
5. If retention is shorter, **stop** and remediate per Control 1.7 portal walkthrough §4 — registry evidence collected before retention is right is not admissible as 17a-4 evidence.

### 2.4 Gate D — Defender for Cloud Apps Connected

1. Open `security.microsoft.com` → **Settings → Cloud apps → App connectors**.
2. Confirm connectors for **Microsoft 365** and **Microsoft Entra ID** are present and Status = **Connected**.
3. Open **Cloud apps → OAuth apps**. Confirm the page renders a list (it may be empty initially) — if it shows "Defender for Cloud Apps not licensed" you are blocked from §8 and must obtain licensing before continuing.

---
## §3 — Microsoft Entra Admin Center: App Registrations

This is the foundation surface. Every callable agent identity except first-party Copilot agents and Power Platform connector-bound flows is born here.

### 3.1 Create the App Registration

1. Sign in to `entra.microsoft.com` as **Entra App Admin** (least-privilege; do not use Global Admin).
2. Navigate **Applications → App registrations → + New registration**.
3. Populate:
   - **Name**: `<env>-<bu>-<purpose>-<seq>` per §1 field 2 (e.g., `prod-wealth-clientonboarding-001`).
   - **Supported account types**: Always **Accounts in this organizational directory only (Single tenant)** for FSI workloads. Multi-tenant should be rejected at this gate unless the Compliance Officer has signed an exception memo (rare — applies only to vendor-hosted SaaS that genuinely requires it).
   - **Redirect URI**: Leave blank for daemon / confidential clients; set Web URI for interactive flows. **Never** set redirect to `localhost` or `urn:ietf:wg:oauth:2.0:oob` outside development tenants.
4. Click **Register**.

   *Screenshot description: New app registration form with Name field populated, Single tenant radio selected, Redirect URI blank. Top breadcrumb shows Microsoft Entra admin center › Identity › Applications › App registrations › Register an application.*

### 3.2 Assign Owners (Field 7, 8 of Schema)

1. From the new app registration → **Owners → + Add owners**.
2. Add the **Agent Owner** UPN.
3. Add the **Backup Owner** UPN (required for Zone 2 and Zone 3; recommended for Zone 1 to satisfy 3.6 orphan-prevention threshold).
4. **Do not** add a security group as owner — owners must be individually-named humans for examiner traceability. The exception is sponsor visibility, which is achieved via custom security attributes (next step), not ownership.

!!! warning "Single-owner apps are 3.6 findings"
    Control 3.6 (Orphaned Agent Detection) treats any app registration with fewer than two named human owners as an orphan-risk finding. The Backup Owner is **not** a courtesy field — it is the survivability control that lets your tenant absorb a single owner departure without triggering Zone 3 24-hour suspension. Backfill backup owners on every existing registration before registering anything new.

### 3.3 Apply Custom Security Attributes (Schema Fields 5, 6, 9, 10, 12, 13, 16, 20)

1. From the app registration overview → **Custom security attributes → + Add assignment**.
2. Select attribute set `AgentRegistry`.
3. Populate every required attribute per §1. The portal will validate against the predefined values for `Zone`, `DataClassificationMax`, and the boolean array fields.
4. Save.

   *Screenshot description: Custom security attributes blade with AgentRegistry attribute set expanded, showing Zone=3, BusinessUnit=Wealth, AgentSponsor=jdoe@contoso.com, ComplianceOfficer=cofficer@contoso.com, DataClassificationMax=Restricted, RegulatedDataInScope=[NPI; Customer-Identifiable], StepUpRequired=true.*

5. **Verification**: Open Entra → Protection → Custom security attributes → AgentRegistry → click the attribute name → confirm the new app registration appears in the assignment list.

### 3.4 Configure API Permissions (Schema Field 15)

1. App registration → **API permissions → + Add a permission**.
2. Select Microsoft Graph (most common) or the target API.
3. Choose **Application permissions** for daemon agents, **Delegated permissions** for user-context agents.
4. Select the **least-privilege** scopes that match the documented business justification. Examples for FSI:
   - Read-only research agent: `Sites.Selected` (then grant per-site permission via Graph) + `Files.Read.All` is **wrong**; use `Sites.Selected` only and grant explicit site permissions via PowerShell to constrain blast radius.
   - Email-summarization agent: `Mail.Read` for the specific mailbox(es) via Application Access Policy in Exchange Online (Control 1.20).
   - Trade-surveillance agent: `eDiscovery.Read.All` only after Compliance Officer sign-off.
5. **Do not** click "Grant admin consent" yet — consent flows through the governance workflow in §9.

!!! danger "The .Default scope is a registry red flag"
    If you see `Mail.ReadWrite`, `Sites.ReadWrite.All`, `Files.ReadWrite.All`, `Directory.ReadWrite.All`, or any `*.Default` resource scope on a Zone 2 or Zone 3 registration, treat it as an immediate finding and route to the AI Administrator for justification. Broad scopes are appropriate for a vanishingly small number of agents (typically only the audit-extraction service principal and the lifecycle-cleanup service principal). For everything else, document the least-privilege scope set in the business justification and refuse the registration if the requestor cannot articulate why narrower scopes do not work.

### 3.5 Credential Configuration

1. App registration → **Certificates & secrets**.
2. Choose credential type:
   - **Certificate** — preferred for daemon agents. Upload the public key only; the private key stays in the agent runtime's key vault.
   - **Federated credential** — preferred when the agent runs in Azure (use Managed Identity federation) or in GitHub Actions / GitLab CI (use OIDC federation). **No secret to rotate** — strongly preferred for FSI.
   - **Client secret** — last resort. Maximum lifetime 6 months. Document the rotation owner in the schema's `business_justification` field. Set a calendar reminder for 14 days before expiry.
3. **Do not** create credentials with the maximum 24-month lifetime. Microsoft allows it; FSI registry policy disallows it. Override the default to ≤ 6 months.
4. Record the credential thumbprint or KID in the evidence pack folder (field 22).

   *Screenshot description: Certificates & secrets blade showing one Federated credential of type GitHub Actions and zero client secrets. Expires column shows N/A for federated. Banner reminder reads "Client secrets should be replaced with certificates or federated credentials whenever possible."*

### 3.6 Token Configuration and Optional Claims

1. App registration → **Token configuration**.
2. Add optional claims as required by the agent's downstream resource. Common FSI additions: `acrs` (for step-up), `amr`, `groups` (only when the resource needs group membership; otherwise prefer Application permissions to avoid token bloat).
3. **Do not** add `aud`, `iss`, `iat`, `exp`, `nbf`, or `sub` — these are mandatory base claims and re-adding them produces malformed tokens.

### 3.7 Authentication Settings

1. App registration → **Authentication**.
2. Set **Allow public client flows** to **No** unless the agent specifically uses device-code or ROPC flows (rare; ROPC is deprecated for FSI and should be denied at consent).
3. Set **Front-channel logout URL** if the agent is a web app and has a sign-out endpoint.
4. **Advanced settings**: Set **Treat application as a public client** to **No** (default).

### 3.8 Capture Evidence

1. Take screenshots of:
   - Overview blade (Application ID, Object ID, Tenant ID visible)
   - Owners blade (both owners visible)
   - Custom security attributes blade (full schema visible)
   - API permissions blade (least-privilege scopes visible, no admin consent yet)
   - Certificates & secrets blade (credential type and expiry visible)
2. Upload screenshots to the evidence pack folder (schema field 22).
3. Update the registry row's `creation_date`, `attestation_status` (set to `Pending-Sponsor-Review`), and `evidence_pack_uri`.

---

## §4 — Microsoft Entra Admin Center: Enterprise Applications and the Agent ID Surface

Every app registration created in §3 produces a tenant-side **service principal** under Enterprise Applications. The Agent ID surface is a specialized projection of Enterprise Applications that surfaces Copilot agents created in Copilot Studio, Agent Builder, or via the Microsoft 365 Agents blade.

### 4.1 Verify the Service Principal Was Created

1. Navigate `entra.microsoft.com` → **Applications → Enterprise applications → All applications**.
2. Filter **Application type = All applications**, **Application visibility = All**, search by display name.
3. Confirm the SP exists with status **Enabled**.
4. Click the SP → **Properties**.
5. Set **Assignment required?** to **Yes** (this enforces explicit user/group assignment for delegated flows; it has no effect on application-permission daemon flows but does no harm).
6. Set **Visible to users?** to **No** unless the agent is a launchable user-facing app (rare for backend agents).

   *Screenshot description: Enterprise application Properties blade showing Assignment required = Yes, Visible to users = No, and the Service Principal Object ID highlighted.*

### 4.2 Confirm SP-Side Owners Match App-Registration-Side Owners

1. SP → **Owners**. Confirm the same two named humans from §3.2 appear here. (Microsoft Entra automatically syncs the first owner; the **backup owner is not auto-synced** — you must add it explicitly on the SP side. This is a frequent registry-drift root cause.)
2. If the SP shows only one owner, add the backup owner now and screenshot.

### 4.3 Apply Custom Security Attributes on the SP (Required — Distinct from §3.3)

The custom security attributes from §3.3 attach to the **app registration object** in the home tenant. The **service principal object** is a distinct object and **does not inherit** them. You must re-apply the attributes on the SP for downstream queries (3.1 reconciliation, 1.7 audit-correlation, 3.6 orphan detection) to find them.

1. SP → **Custom security attributes → + Add assignment**.
2. Re-apply the same `AgentRegistry` attribute set with the same values as §3.3.
3. Save and screenshot.

!!! tip "Why the dual-attribute design"
    The app registration is the developer-facing object; the SP is the runtime-facing object. Examiners pulling a runtime audit will pivot from the audit log's `appId` value to the SP, not to the app registration. Sponsor metadata on the SP is what closes the audit-trail loop. Until Microsoft unifies the two object models, dual-attribution is the only correct pattern.

### 4.4 The Agent ID Surface (Copilot Agents Projection)

For tenants on the GA Agent ID surface (Commercial):

1. Navigate `entra.microsoft.com` → **Applications → Enterprise applications**.
2. Filter **Application type = Microsoft Copilot agents** (or in some tenant builds: **Agent ID**).
3. The list shows every Copilot Studio agent, declarative agent, and custom Copilot agent that has been created in the tenant — each materialized as an Entra Agent ID with its own Object ID.
4. Click any agent → **Overview**. Note the **Agent type**, **Created by**, **Created date**, and (if surfaced in your tenant build) the **Sponsor** and **Owner** fields.
5. Apply the `AgentRegistry` custom security attributes per §4.3 — Agent IDs participate in custom-security-attribute query the same way SPs do.

   *Screenshot description: Enterprise applications list filtered to Application type=Microsoft Copilot agents showing five agents with App ID values starting with the Copilot-agent prefix and Owner column populated.*

!!! warning "Agent ID without sponsor metadata is a Zone 2/3 finding"
    Copilot Studio and Agent Builder allow an end user to create an agent and immediately project it as an Agent ID without a sponsor field. For Zone 2 and Zone 3 agents this is unacceptable. Configure the **Power Platform DLP policy** (1.4) and **Copilot Studio admin settings** (this control's PowerShell setup §5) to block agent publish unless a sponsor attribute can be applied at creation time. For tenants where this gate is not yet available, run the `powershell-setup.md` daily sweep job to detect and quarantine sponsor-less Agent IDs.

### 4.5 Conditional Access for the Service Principal

This is a sister activity to §12; capture it now while you have the SP open.

1. Open `entra.microsoft.com` → **Protection → Conditional Access → Policies**.
2. Confirm a policy named `CAP-AGENTS-Workload-Identities-AllAgents` (or your tenant's equivalent) is active and includes the new SP in scope.
3. If the SP is not yet in scope, do **not** edit the global policy — instead add the SP to the security group `sg-workload-identities-governed` which is the policy's assignment target. (Group-based CA assignment is auditable; per-SP assignment is not.)
4. Verify in Conditional Access → **What If** by entering the SP's Object ID.

### 4.6 Capture Evidence

Add to the evidence pack:

- Enterprise app Properties blade (Assignment required = Yes)
- SP Owners blade (both humans visible)
- SP Custom security attributes blade
- (If applicable) Agent ID Overview blade
- CA What-If result showing the policy applies

---

## §5 — Microsoft 365 Admin Center: Integrated Apps

This surface governs **third-party Microsoft 365 add-ins, Teams apps, and Outlook add-ins** at the tenant level. It is the front door that vendors knock on to put an agent in front of your users.

### 5.1 Open the Integrated Apps Blade

1. Sign in to `admin.microsoft.com` as **AI Administrator**.
2. Navigate **Settings → Integrated apps**.
3. The page shows three tabs: **Available apps** (catalog), **Deployed apps** (active), **Pending requests** (user-initiated requests awaiting admin action).

### 5.2 Lock Down User Consent Defaults

Before processing any app, set the tenant-level consent posture.

1. Open `entra.microsoft.com` → **Identity → Applications → Enterprise applications → Consent and permissions → User consent settings**.
2. Set **User consent for applications** to **Do not allow user consent** (preferred for FSI) or **Allow user consent for apps from verified publishers, for selected permissions** (acceptable for tenants with mature low-risk-scope catalog).
3. Set **Group owner consent for apps accessing data** to **Do not allow group owner consent**.
4. Save.

   *Screenshot description: User consent settings blade with "Do not allow user consent" radio selected and a yellow info banner explaining the impact on end-user experience.*

5. Open **Admin consent settings**. Set **Users can request admin consent to apps they are unable to consent to** to **Yes** and configure:
   - **Reviewers**: security group `sg-app-consent-reviewers` (members: AI Administrator, Entra App Admin, Compliance Officer rotating).
   - **Selected users will receive email notifications for requests**: Yes.
   - **Selected users will receive request expiration reminders**: Yes.
   - **Consent request expires after (days)**: 30 (FSI standard; some tenants prefer 14).
6. Save and screenshot.

### 5.3 Process the Pending Requests Queue

1. Back to `admin.microsoft.com` → **Settings → Integrated apps → Pending requests**.
2. For each request:
   - **Open** the request and review: requesting user, app publisher, requested permissions, justification text.
   - Click **Microsoft AppSource compliance** to view the app's published Microsoft 365 Certification and SOC 2 / ISO 27001 attestations. **No certification = automatic decline** for Zone 3 data scopes.
   - Cross-check the publisher domain against your vendor risk catalog. Reject any publisher not in the catalog.
   - If approving: click **Deploy** → choose **Specific users / groups** (never "Entire organization" on first deployment) → assign to a pilot security group → set the rollout cadence.
   - If rejecting: click **Reject** → paste the rejection rationale (this becomes audit evidence) → notify the requesting user via the templated email in your evidence pack folder.
3. **Document every approval** in the registry with `surface_origin = M365 Integrated Apps`, sponsor metadata, and a link to the request approval evidence.

!!! warning "Microsoft 365 Certification is necessary, not sufficient"
    Microsoft 365 Certification confirms the publisher has attested to security and privacy practices; it does **not** verify those practices, and it **does not** evaluate the app under FINRA, SEC, or NYDFS-specific obligations. Treat the Microsoft certification as a baseline gate and apply your own vendor risk management procedure (typically driven by your TPRM team) on top of it. Document the dual-gate decision in the business justification field.

### 5.4 Block Apps That Should Never Reach Users

1. **Settings → Integrated apps → Available apps**.
2. For each app you do not want users to install (consumer-grade AI assistants, unsanctioned chat tools, free OCR add-ins commonly used to exfiltrate via screen capture):
   - Click the app → **Block app**.
   - Document the block rationale.
3. The blocked-apps list is itself an audit artifact — export it monthly to your evidence pack.

### 5.5 Review Deployed Apps Inventory

1. **Settings → Integrated apps → Deployed apps**.
2. Confirm every deployed app appears in your registry with matching sponsor metadata. Any deployed app **not** in the registry is a finding — register it now or initiate retirement.
3. Capture evidence: full export of the deployed apps list (Export button → CSV) saved to the evidence pack with timestamp.

---
## §6 — Microsoft 365 Admin Center: Agents Blade and Agent 365 (Preview)

This surface registers **first-party Copilot agents** — declarative agents authored in Copilot Studio, custom agents from Agent Builder, and agents distributed through the M365 admin center's Agents catalog.

### 6.1 Open the Agents Blade

1. Sign in to `admin.microsoft.com` as **AI Administrator**.
2. Navigate **Copilot → Agents**. (In some tenant builds the path is **Copilot → Settings → Agents**.)
3. The page lists every agent the tenant has surfaced, with columns for Name, Type, Owner, Created, Status.

### 6.2 Configure Tenant-Level Agent Defaults

1. Click **Settings** (gear) on the Agents page.
2. Set **Who can create agents** to one of:
   - **Specific users / groups** — strongly preferred. Scope to `sg-agent-builders-zone1`, `sg-agent-builders-zone2`, `sg-agent-builders-zone3` (managed via Identity Governance access packages with sponsor approval).
   - **Everyone** — appropriate only for tenants in the very early Copilot pilot phase and only when paired with a Power Platform DLP policy that blocks all data-touching connectors.
3. Set **Default sharing scope for new agents** to **Just me** (Zone 1 default). Tenant-wide sharing must require a sponsor sign-off step.
4. Set **Allow publishing to organization catalog** to **Specific approvers** and configure the approver group to `sg-agent-publish-approvers`.
5. Save and screenshot.

### 6.3 Walk the Agent Inventory

1. From the Agents page, sort by **Created date descending**.
2. For each agent created since your last walk:
   - Click the agent → **Properties**.
   - Confirm **Owner** is populated and is a named human (not a service account).
   - Confirm **Sharing scope** matches the registered Zone (Zone 1 → Just me; Zone 2 → security group; Zone 3 → security group + Compliance Officer co-owner).
   - Confirm the agent's **Connected data sources** column matches the connectors approved in the registry's `connectors_used` field.
   - If any field drifts from the registry, flag for sponsor re-attestation per §14.

   *Screenshot description: Agents blade list with five agents, columns Name / Type / Owner / Created / Status / Sharing scope visible. One row highlighted showing Type = Declarative agent, Owner = jdoe@contoso.com, Sharing scope = Specific people (sg-z2-wealth-research).*

### 6.4 Agent 365 (Preview) — Tenant Opt-In and Special Handling

If your tenant has opted in to the Agent 365 preview:

1. **Settings (gear) → Agent 365** confirms opt-in status.
2. Agent 365 agents appear with an **"Agent 365"** badge in the agents list.
3. **Treat Agent 365 agents as Zone 3 by default** until the preview reaches GA and your control catalog is updated to reflect any new isolation, supervision, or audit-export capabilities. The preview-period default-Zone-3 posture is a hedge against capability changes; revisit at GA.
4. Document Agent 365 enrollment in the evidence pack with the opt-in date and the Compliance Officer's sign-off on the preview risk acceptance.

### 6.5 Agents-Blade-to-Registry Reconciliation

The Agents blade does not natively support custom security attributes. Mirror each agent into the external registry (SharePoint list / Dataverse table / GRC tool) at registration time. The Control 3.1 reconciliation job will alert on any agent present in the blade but absent from the external registry within 24 hours.

---

## §7 — Power Platform Admin Center: Copilot Agents and Connectors

This surface registers **Copilot Studio agents per environment** and the **custom and certified connectors** they invoke. Power Platform is the single largest agent-creation surface in most FSI tenants and the most common source of registry drift.

### 7.1 Open the Power Platform Admin Center

1. Sign in to `admin.powerplatform.microsoft.com` as **Power Platform Admin**.
2. Confirm the tenant home page renders the environment list. If you see only a single Default environment, your environment topology is the largest single risk in your Power Platform footprint — see Control 1.4 portal walkthrough §2 to remediate before continuing.

### 7.2 Resources → Copilot Agents View

1. Navigate **Resources → Copilot agents**.
2. Use environment filter to walk each environment in turn (Default, Production-Wealth, Production-Capital-Markets, etc.).
3. For each environment:
   - Sort by **Modified date descending**.
   - For each agent: click → confirm **Created by**, **Modified by**, **Published** status, **Authentication** mode (preferred: **Authenticate manually** with explicit Entra app, never **No authentication** for Zone 2/3).
   - Confirm the agent's **Topics → Generative actions** list matches what's documented in the registry. Generative actions are the highest-risk Copilot Studio feature — they invoke connectors with model-decided arguments and are an out-of-band path that bypasses topic-level supervision.

   *Screenshot description: Power Platform admin center → Resources → Copilot agents view filtered to Production-Wealth environment showing seven agents with Owner column populated and three rows highlighted as Published.*

### 7.3 Environments → Settings → Generative AI Settings (Per Environment)

For each environment hosting Zone 2 or Zone 3 agents:

1. **Environments → [environment] → Settings → Product → Generative AI**.
2. Confirm:
   - **Enable Copilot for makers**: Yes (or No based on your maker enablement decision)
   - **Enable users to create agents**: scoped per Zone
   - **Enable Generative answers**: scoped per Zone — **disable for Zone 3** unless data sources have been individually whitelisted
   - **Allow agents to use the public web**: **No for all Zones** in FSI baseline (web grounding is a model-controlled outbound channel; treat as exfiltration risk until you have a content-filtering proxy in front of it)
3. Save and screenshot per environment.

### 7.4 Connectors Approval Workflow

1. **Data → Custom connectors** (per environment) and **Data → Connector requests** (tenant-wide queue).
2. For each pending custom connector:
   - Open the connector definition. Walk the **Definition** tab and confirm every operation maps to a documented business need.
   - Confirm authentication is **OAuth 2.0** or **API Key in Key Vault**, never **No authentication** or **Basic** with hard-coded credentials.
   - If the connector targets a regulated downstream system (CRM with NPI, trading system, surveillance feed): require Compliance Officer co-approval before publishing.
   - Approve → set **Sharing** to specific environments, never tenant-wide on first publish.
3. **Connector requests** queue: process per request, mirroring the M365 Integrated Apps consent workflow (§5.3).

### 7.5 Capture Evidence

For each environment:

- Copilot agents list export (CSV)
- Generative AI settings screenshot
- Custom connectors list export
- Connector requests log (approvals and rejections with timestamps and approver UPN)

Mirror every Power Platform agent into the external registry the same day it is published. Power Platform agents that don't reach the registry within 24 hours are surfaced by Control 3.6 as orphan-risk findings.

---

## §8 — Microsoft Defender for Cloud Apps: Cloud Discovery and OAuth App Governance

This surface is the **post-consent visibility plane** — it is where you discover the OAuth apps that already received consent before your governance was tight enough to catch them, and where you continuously monitor for new ones.

### 8.1 Cloud Discovery — Establish Baseline

1. Sign in to `security.microsoft.com` as **Entra Security Admin**.
2. Navigate **Cloud apps → Cloud discovery → Dashboard**.
3. Confirm the dashboard shows non-zero discovered apps. If it is empty, configure a continuous data feed from your firewall / proxy (Zscaler, Netskope, Palo Alto, etc.) per the Defender for Cloud Apps documentation.
4. Set **Risk score threshold** for automatic flagging:
   - Score ≤ 3 → automatic alert
   - Score 4–6 → manual review queue
   - Score ≥ 7 → permitted with no flag (informational only)
5. Configure the **App tagging** taxonomy: `Sanctioned-Registered`, `Sanctioned-Personal`, `Unsanctioned`, `Under-Review`, `Blocked`. Every discovered app must carry exactly one tag.

### 8.2 OAuth App Governance

1. **Cloud apps → OAuth apps**.
2. Filter **App state = Approved** and review every approved OAuth app:
   - Confirm the app appears in the registry with matching sponsor metadata.
   - Confirm the granted permissions match the registry's `graph_permissions_granted` field.
   - Confirm the consent type (User vs. Admin) matches the consent governance workflow's expected outcome (§9).
3. For any approved app **not** in the registry: investigate the consent event in Purview Audit (filter by `Operation = Consent to application`), identify the consenting user, and either retroactively register or revoke consent.
4. Filter **App state = Pending review** and process per §9 reviewer queue.

### 8.3 OAuth App Policies

1. **Cloud apps → Policies → Policy management → OAuth app policies**.
2. Confirm the following policies are active (create if missing):
   - **High-permission OAuth app from new publisher** — Severity High, action: Revoke app and notify reviewers.
   - **OAuth app with low community use granting high permissions** — Severity High, action: Notify reviewers.
   - **Misleading OAuth app name / publisher name** — Severity High, action: Revoke app.
   - **OAuth app from non-verified publisher requesting Mail.Read or Mail.ReadWrite** — Severity High, action: Notify and revoke.
3. Tune severity thresholds per your tenant's noise level over the first 30 days; document the final thresholds in the evidence pack.

### 8.4 OAuth App Anomaly Detection

1. **Cloud apps → Policies → Anomaly detection** confirms the built-in policies for unusual OAuth app activity are enabled.
2. Forward all OAuth-related alerts to the SOC ticketing queue (see Control 1.24 portal walkthrough §6 for the integration steps).

### 8.5 Capture Evidence

- Cloud Discovery dashboard screenshot (top apps, risk distribution)
- OAuth app full export (CSV) with state, permissions, last activity per app
- Active OAuth policies list
- 30-day OAuth alert summary

---

## §9 — App Consent Governance Workflow

This section ties §3, §4, §5, §7, and §8 together with the **end-to-end consent decision flow**. Every consent grant in the tenant must traverse this workflow.

### 9.1 The Workflow at a Glance

```
[1] User or developer initiates consent
     │
     ▼
[2] Tenant consent setting blocks self-service (per §5.2)
     │
     ▼
[3] User submits Admin consent request
     │
     ▼
[4] Reviewer queue (sg-app-consent-reviewers) receives notification
     │
     ▼
[5] Reviewer evaluates: Microsoft 365 Cert? Vendor in catalog?
    Permissions least-privilege? Sponsor identified? Zone determined?
     │
     ├──► Reject → email rationale → log in evidence pack
     │
     ▼
[6] Reviewer approves with scoped consent (specific users / groups, not all)
     │
     ▼
[7] App Admin populates registry row with sponsor metadata,
    Zone, business justification, evidence pack URI
     │
     ▼
[8] Custom security attributes applied to app registration AND SP
     │
     ▼
[9] Defender for Cloud Apps tags the app Sanctioned-Registered
     │
     ▼
[10] First sign-in observed → Conditional Access for workload identity
     applies (per §12) → audit event logged → 3.1 reconciliation closes the loop
```

### 9.2 Reviewer Triage Checklist

Every reviewer in `sg-app-consent-reviewers` works from this checklist. Save as a Microsoft Form or as a SharePoint list for queryable evidence.

| # | Question | Source of answer | Pass criterion |
|---|----------|------------------|----------------|
| 1 | Is the app from a verified publisher? | App detail blade in admin consent request | Yes |
| 2 | Does the publisher hold Microsoft 365 Certification? | Microsoft AppSource link in request | Yes for Zone 2/3; advisory for Zone 1 |
| 3 | Is the publisher in the tenant's vendor risk catalog? | TPRM portal | Yes for Zone 2/3 |
| 4 | Are the requested permissions least-privilege? | Permissions list in request | No `*.Default` or `*.All` unless justified |
| 5 | Is a named Agent Sponsor identified? | Request justification text | Yes; sponsor must be member of `sg-agent-sponsors-zone<n>` |
| 6 | Has the data classification been determined? | Sponsor confirmation | Yes |
| 7 | Will the app touch NPI, MNPI, PCI, PHI, or trade-surveillance data? | Sponsor confirmation | If yes, reviewer escalates to Compliance Officer for Zone 3 path |
| 8 | Is the consent scope `Specific users / groups`, never tenant-wide? | Reviewer choice | Yes for first deployment |
| 9 | Has the registry row been pre-staged? | Reviewer verifies in registry | Yes |
| 10 | Has the evidence pack folder been created? | Reviewer verifies in SharePoint | Yes |

If any answer fails, reject the request with the specific reason. Do **not** approve and "fix later" — the post-approval revoke creates a permission window in the audit trail that examiners will ask about.

### 9.3 Scope-Based Decision Rules (FSI Baseline)

| Permission scope | Auto-decision | Rationale |
|------------------|---------------|-----------|
| `User.Read`, `openid`, `profile`, `offline_access` | Auto-approve (only these) | Sign-in scopes, no data access |
| `Files.Read`, `Files.ReadWrite` (delegated) | Reviewer approval | Data access — sponsor required |
| `Files.Read.All`, `Files.ReadWrite.All` (application) | Compliance Officer approval | Tenant-wide blast radius |
| `Sites.Selected` (application) | Reviewer approval + per-site grant via PowerShell | Preferred pattern for site-scoped access |
| `Mail.Read`, `Mail.ReadWrite` (application) | Compliance Officer approval + Application Access Policy in EXO | Mailbox content; high regulator interest |
| `Directory.Read.All`, `Directory.ReadWrite.All` | Entra Global Admin + Compliance Officer | Identity blast radius |
| `eDiscovery.*` | Compliance Officer + Legal sign-off | Regulator-sensitive |
| `RoleManagement.*` | Reject by default | Privilege escalation surface |

### 9.4 Quarterly Consent Sweep

1. Once per quarter, the Reviewer team runs a sweep of all granted consents using the PowerShell script in `powershell-setup.md` §6.
2. Output is a CSV of every consent grant with sponsor metadata join.
3. Any grant without a sponsor or with a stale sponsor (sponsor no longer in `sg-agent-sponsors-zone<n>`) is escalated to the Compliance Officer for re-attestation or revocation.
4. Sweep output is filed in the evidence pack with the quarterly attestation memo (§14).

---

## §10 — Service Principal and Managed Identity Hygiene

The accumulation of stale service principals, expired credentials, and orphaned managed identities is the single most common 1.2 finding in FSI tenant audits. This section is the routine sanitation drill.

### 10.1 Quarterly SP Inventory and Triage

1. From the Entra portal: **Applications → Enterprise applications → All applications**.
2. Add columns: **Application ID**, **Object ID**, **Created on**, **Sign-in Activity (preview)**, **Owner count**.
3. Export the full list (Download button).
4. Open in Excel / Power Query. Triage rows:
   - **Sign-in Activity > 90 days ago** AND **non-Microsoft publisher** → candidate for retirement.
   - **Owner count = 0** → orphan; route to 3.6 remediation immediately (do not auto-delete; ownership backfill or sponsor-owned retirement memo required).
   - **Created > 2 years ago** AND **never signed in** → almost certainly a leftover from a vendor PoC; retirement candidate.
5. For each retirement candidate, follow §10.4.

### 10.2 Credential Expiration Triage

1. Cannot be done in portal at scale. Use the PowerShell script in `powershell-setup.md` §7 (`Get-MgApplication -All` + `$_.PasswordCredentials` enumeration).
2. Output CSV with columns: AppId, DisplayName, CredentialType (Password/Certificate/Federated), EndDate, DaysUntilExpiry, Owner.
3. Triage:
   - **DaysUntilExpiry ≤ 14**: notify Owner and Backup Owner; track to rotation in evidence pack.
   - **DaysUntilExpiry ≤ 0** (already expired): app may already be broken in production — investigate before rotating.
   - **CredentialType = Password AND lifetime > 6 months** at issuance: policy violation; rotate to Certificate or Federated and shorten.
4. Repeat monthly for Zone 2/3 apps; quarterly for Zone 1.

### 10.3 Managed Identity Hygiene

1. Managed Identities are minted from Azure subscriptions and projected as service principals into the home tenant.
2. **Applications → Enterprise applications → All applications → Filter Application type = Managed Identities**.
3. For each MI:
   - Confirm the source Azure resource still exists. Use the MI Object ID to query `Get-AzResource` (PowerShell) — if the source resource is gone, the MI is orphaned and must be deleted.
   - Confirm the MI's Graph permissions match the registered scope. MIs frequently accumulate permissions during incident response and never have them removed.
   - Confirm the MI has Owner metadata via custom security attributes (MIs don't natively support owners; the workaround is custom security attributes carrying owner UPN).
4. Document MIs in the registry with `agent_type = Workload identity`.

### 10.4 Retirement Procedure

A retirement is **not** a delete. It is a controlled state transition with audit evidence.

1. Sponsor and Compliance Officer co-sign a retirement memo (template in evidence pack folder `templates/agent-retirement-memo.docx`).
2. Disable the SP: **Enterprise applications → [app] → Properties → Enabled for users to sign in = No**. Wait 30 days as the **deprecation window** to surface any unanticipated dependencies.
3. After 30 days with no sign-in attempts (verify via Sign-ins log), revoke all credentials and delete the SP and the app registration.
4. Update registry: `attestation_status = Retired`, `retirement_date = <date>`. **Do not delete the registry row** — examiners can pull retired-agent histories years later.
5. File the retirement memo, the deprecation-window sign-in log, and the deletion confirmation in the evidence pack.

!!! danger "Never reuse a retired agent_id"
    Tempting as it is to "recreate" an agent under the same display name and pretend the historical audit trail belongs to the new agent, this is an evidence-integrity violation. The new agent gets a new `agent_id`, a new evidence pack folder, and a new registration history. The old `agent_id` row stays in the registry forever with `attestation_status = Retired`.

---
## §11 — Sponsorship Portal Touchpoints

The end-to-end sponsorship lifecycle (eligibility, attestation, departure detection, reassignment, Zone 3 24-hour suspension, Lifecycle Workflow JSON) lives in the sibling playbook `sponsorship-lifecycle-workflows.md`. **Do not duplicate that material here.** This section catalogs only the portal locations where the sponsor metadata field surfaces, so you know where to look during incident response, examiner pulls, or routine reconciliation.

### 11.1 Where Sponsor Metadata Appears (Per Surface)

| Surface | Where to find sponsor field | Editable in portal? |
|---------|-----------------------------|--------------------|
| Entra App Registration | Custom security attributes blade → `AgentRegistry → AgentSponsor` | Yes (Attribute Assignment Administrator role) |
| Entra Enterprise Application (SP) | Custom security attributes blade → `AgentRegistry → AgentSponsor` (must be re-applied — see §4.3) | Yes |
| Entra Agent ID | Custom security attributes blade on the Agent ID object → `AgentRegistry → AgentSponsor` | Yes |
| M365 Integrated Apps | Not native; mirror to external registry keyed by `agent_id` | No (external store only) |
| M365 Agents blade | Not native; mirror to external registry | No |
| Power Platform Copilot agent | Tags property on the agent JSON OR Dataverse `cr_AgentRegistry` row | Editable via Dataverse (Power Platform Admin), not via the agent properties pane |
| Defender for Cloud Apps OAuth app | App tag → `Sanctioned-Registered:<sponsor-upn>` (use the tagging convention to encode sponsor) | Yes |

### 11.2 Sponsor-Lookup Quick Procedure (For Incident Response)

When an incident references an audit event with `appId = <guid>` and you need to identify the sponsor in under five minutes:

1. Open `entra.microsoft.com` → **Applications → Enterprise applications → All applications**.
2. Search by Application ID.
3. Click the SP → **Custom security attributes**.
4. Read the `AgentSponsor` value.
5. If the attribute is missing, the agent is unregistered — escalate to the AI Administrator and Compliance Officer immediately, then walk through Defender → Cloud apps → OAuth apps to look for the app under any consent record.

### 11.3 Sponsor Visibility for Read-Only Roles

Reviewers, auditors, and SOC analysts often need to see sponsor metadata without write access.

1. Assign **Attribute Assignment Reader** (Entra directory role) to the security group `sg-registry-readers`.
2. Add SOC analysts, internal auditors, and Compliance read-only roles to that group.
3. Confirm read access by signing in as a test user from that group and confirming the `AgentRegistry` attribute set is visible (read-only) on a sample app registration.

### 11.4 Cross-Reference to Sponsorship Lifecycle Playbook

For the following procedures, route to `./sponsorship-lifecycle-workflows.md`:

- §2 — Sponsor eligibility group provisioning and access-package configuration
- §3 — Sponsor attestation cadence (paired with the §14 quarterly attestation here)
- §4 — Sponsor departure detection via Entra Lifecycle Workflows
- §5 — Sponsor reassignment workflow
- §6 — Zone 3 24-hour suspension automation when a sponsor cannot be reassigned
- §7 — Evidence collection schema for sponsor lifecycle events
- §8 — Integration with Control 3.6 orphan detection

---

## §12 — Conditional Access for Workload Identities

This is the runtime gate that prevents a stolen credential from being usable outside the sanctioned context. Workload Identities Premium licensing is required.

### 12.1 Confirm Licensing

1. `entra.microsoft.com` → **Identity → Overview → Licenses**.
2. Confirm **Microsoft Entra Workload Identities Premium** appears with non-zero assigned units.
3. If absent, you cannot proceed — engage procurement before relying on §12 for any control narrative.

### 12.2 Create the Baseline Workload Identity Policy

1. **Protection → Conditional Access → Policies → + New policy**.
2. Name: `CAP-AGENTS-Workload-Identities-Baseline`.
3. **Assignments → Workload identities → Single identities or all service principals**: Select **Service principals → Include security group `sg-workload-identities-governed`**.
4. **Cloud apps or actions → Cloud apps → Include All cloud apps**.
5. **Conditions → Locations → Include Any location, Exclude Named location `corporate-egress-ranges`** (your egress ranges).
6. **Conditions → Sign-in risk → High and Medium**.
7. **Grant → Block access**.
8. **Enable policy → Report-only** for the first 7 days; then **On**.
9. Save.

   *Screenshot description: Conditional Access policy summary card showing CAP-AGENTS-Workload-Identities-Baseline, Target = service principals in sg-workload-identities-governed, Conditions include Sign-in risk High|Medium and Locations exclude corporate-egress-ranges, Control = Block, State = On.*

### 12.3 Create the Step-Up Companion Policy

For workload identities that perform high-risk operations (HVT actions in 1.23 scope), pair the baseline with a step-up trigger.

1. **+ New policy** → name `CAP-AGENTS-Workload-Identities-StepUp-Trigger`.
2. Same scope as 12.2.
3. **Cloud apps → Include**: high-value resources only (specific Graph API scopes, specific SharePoint sites, specific Exchange mailboxes — see Control 1.23 portal walkthrough §3 for the canonical list).
4. **Grant → Require authentication strength → Phishing-resistant MFA** (the step-up authentication strength).
5. Note: workload identities cannot perform interactive MFA; this policy works because the step-up requirement passes through to the **invoking user** when the workload identity acts on a delegated token. For application-permission daemon flows the policy effectively becomes a block — which is the intended outcome for HVT actions on daemon flows in FSI baseline.

### 12.4 Verify Coverage Using What If

1. **Conditional Access → What If**.
2. Enter the SP's Object ID (toggle the "Workload identity" tab).
3. Test scenarios: from a corporate egress IP (expect: allow), from a non-corporate IP (expect: block), high sign-in risk (expect: block).
4. Screenshot all three What If results to the evidence pack.

### 12.5 Operate the Policy

1. Add new agent SPs to `sg-workload-identities-governed` at registration time (§4.5). Group-based assignment is the audit-friendly pattern; per-SP assignment in CA is not.
2. Review CA workload identity sign-in failures weekly via **Monitoring → Sign-in logs → Service principal sign-ins → Status = Failure**. Failures here often indicate either a misregistered agent or an attempted credential abuse — both warrant investigation.

---

## §13 — Zone-Specific Portal Workflows

The seven surfaces above are common to all zones; the **operating procedure** differs by zone. This section is the per-zone delta.

### 13.1 Zone 1 (Personal / Productivity)

Characteristics: single user audience, Public or Internal data only, no NPI / MNPI / PCI / PHI.

Portal workflow deltas:

- **§3 owners**: Single Agent Owner acceptable; Backup Owner recommended but not blocking.
- **§4 SP**: Custom security attributes still required. Conditional Access via `sg-workload-identities-governed` still required.
- **§5 Integrated Apps**: User self-consent is permissible only for the verified-publisher + low-risk-scope subset configured in §5.2.
- **§6 Agents blade**: Default sharing scope **Just me**.
- **§7 Power Platform**: Permitted in the Default environment only if a Default-environment DLP policy from 1.4 blocks Business connectors entirely.
- **§14 attestation**: Annual cadence acceptable (Zone 2/3 are quarterly).

### 13.2 Zone 2 (Team / Departmental)

Characteristics: scoped to a department or team, may touch Internal or Confidential data, non-regulated workloads.

Portal workflow deltas:

- **§3 owners**: Two named humans required (Owner + Backup Owner). No exceptions.
- **§4 SP**: Custom security attributes required. CA via `sg-workload-identities-governed` required. Sign-in risk Medium triggers block (vs. High-only for Zone 1).
- **§5 Integrated Apps**: All consents flow through admin consent reviewer queue; no user self-consent.
- **§7 Power Platform**: Must run in a non-Default Production environment with an environment-scoped DLP policy. Custom connectors require Compliance Officer review.
- **§9 consent governance**: Reviewer + Sponsor sign-off required.
- **§14 attestation**: Quarterly.

### 13.3 Zone 3 (Enterprise / Regulated)

Characteristics: enterprise-wide audience or regulated data scope (NPI, MNPI, PCI, PHI, customer-identifiable, trade-surveillance).

Portal workflow deltas:

- **§3 owners**: Two named humans + named Compliance Officer co-owner (via custom security attribute, not portal owner role — the Compliance Officer's role is attestation, not operations).
- **§4 SP**: Custom security attributes required. CA via `sg-workload-identities-governed` required + step-up policy (§12.3) required for any HVT operation.
- **§5 Integrated Apps**: All consents require Compliance Officer co-approval beyond the standard reviewer queue.
- **§6 Agents blade / Agent 365**: Sharing scope must be a security group governed by an Identity Governance access package with sponsor + Compliance Officer co-approval; default-Zone-3 posture for all Agent 365 preview agents.
- **§7 Power Platform**: Must run in a Production environment with an environment-scoped DLP policy that excludes all non-allowlisted connectors. Generative answers disabled by default. No public web grounding.
- **§9 consent governance**: Reviewer + Sponsor + Compliance Officer + (for `Mail.*`, `Directory.*`, `eDiscovery.*`) Legal sign-off.
- **§10 SP hygiene**: Monthly credential expiration sweep; quarterly full SP triage.
- **§14 attestation**: Quarterly + ad-hoc on any sponsor change, scope change, or material incident.
- **§15 examiner audit-pull**: Pre-staged evidence pack maintained continuously, not built reactively.

---

## §14 — Quarterly Attestation (Three-Signature)

The attestation is the human control that closes the registry loop. Three signatures are required: **Agent Sponsor → Agent Owner → Compliance Officer**. Without all three, the registry row's `attestation_status` cannot move to `Current`.

### 14.1 Cadence and Scope

- Zone 1: Annual.
- Zone 2: Quarterly (Jan/Apr/Jul/Oct or fiscal-quarter-aligned).
- Zone 3: Quarterly + ad-hoc on sponsor change, material scope change, or post-incident.

### 14.2 The Attestation Memo Template

Every attestation produces a Word memo (template `templates/agent-attestation-memo-vYYYYQ#.docx` in the evidence pack folder). The memo carries:

1. Agent identification: `agent_id`, `display_name`, `surface_origin`, current `zone`.
2. Schema review: every field in §1 reviewed; changes since last attestation listed.
3. Sponsor attestation: "I, <sponsor>, confirm I am familiar with this agent's purpose, the data it accesses, and the business justification on file. I have reviewed the audit logs for the attestation period and am not aware of misuse. I remain in `sg-agent-sponsors-zone<n>` and accept continued sponsorship for the next quarter." — sponsor signature + date.
4. Owner attestation: "I, <owner>, confirm I am the operationally responsible owner. I have rotated credentials within policy windows, applied any required configuration changes, and resolved any 1.24 / 1.10 / 3.6 findings flagged this quarter. The Backup Owner is current and reachable." — owner signature + date.
5. Compliance Officer attestation (Zone 3 + Zone 2 by policy): "I, <compliance officer>, have reviewed the sponsor and owner attestations, the audit log summary, and any open findings. I find the agent's operation supports compliance with the regulatory references on file and approve continued operation for the next quarter." — Compliance Officer signature + date.
6. Hedged caveat (mandatory): "**Implementation requires sustained operator discipline; this attestation supports compliance with the cited regulations and does not constitute a legal determination of compliance. Organizations should verify configuration against current regulatory expectations and their own legal counsel's interpretation.**"

### 14.3 Portal Procedure

1. Compliance Officer launches the **Attestation Tracker** (SharePoint list `AgentAttestationTracker`) at the start of each quarter.
2. The list auto-populates rows from the registry filtered to `attestation_status IN (Current, Past-due)` with `last_attestation_date < quarterly threshold`.
3. For each row:
   - Sponsor receives an automated Microsoft Forms attestation request linked to the memo template.
   - Sponsor completes form → memo PDF auto-generated → routed to Owner.
   - Owner completes attestation → memo updated → routed to Compliance Officer.
   - Compliance Officer reviews and signs → memo finalized → uploaded to evidence pack folder → registry `last_attestation_date` and `attestation_status` updated by Power Automate flow.
4. Any row not completed by the quarterly deadline flips to `attestation_status = Past-due` and triggers escalation:
   - Day 1 past-due: notification to sponsor, owner, Compliance Officer.
   - Day 7 past-due: notification to sponsor's manager.
   - Day 14 past-due: agent SP **disabled** in Enterprise Applications (Properties → Enabled = No) until attestation completes.
   - Day 30 past-due: registry row flipped to `Suspended`; downstream controls (3.6, 1.7) flag for retirement evaluation.

### 14.4 Sample Attestation Walk

Walk one Zone 3 attestation end-to-end at the start of every quarter as a **control rehearsal**, even if no findings emerge. The rehearsal evidence (a successful attestation cycle on a known-good agent) is the demonstration evidence examiners expect when they ask "show me how a sponsor attestation works."

---

## §15 — Examiner Audit-Pull (Point-in-Time Reconstruction)

When FINRA, SEC, OCC, NYDFS, or the Federal Reserve issues a request for production touching an agent, you have a fixed window (typically 10 business days) to assemble a defensible evidence package. This section is the runbook.

### 15.1 What Examiners Typically Request

- **Agent inventory as of <date>** with sponsor, owner, data classification, and consent grants.
- **Sign-in activity** for a specific agent over a defined window.
- **Configuration history** showing the agent's permissions and policy posture at a specific moment.
- **Attestation history** showing who signed off on the agent and when.
- **Any incidents** involving the agent and the response.
- **Retirement memo** (if applicable) and the deprecation-window evidence.

### 15.2 Pre-Staged Evidence (Maintained Continuously, Not Reactively)

For every Zone 3 agent (and every Zone 2 agent in regulated business units), the evidence pack folder must already contain:

1. Registration evidence (§3.8, §4.6, §5.5, §6.5, §7.5 outputs).
2. Quarterly attestation memos (§14.2).
3. Quarterly SP/MI hygiene snapshots (§10).
4. Annual configuration baseline export (Conditional Access policies in scope, custom security attributes, group memberships, Power Platform DLP policies in scope).
5. Audit log extracts (1.7) for the agent's last 12 months — pre-extracted monthly to a sealed SharePoint folder with retention label.
6. Any incident reports (1.10, 1.24).

### 15.3 Reactive Pull Procedure (10-Business-Day SLA)

| Day | Action | Owner |
|-----|--------|-------|
| 1 | Receive request. Compliance Officer opens evidence pack folder, confirms pre-staged completeness, identifies any gaps. | Compliance Officer |
| 1–2 | Run point-in-time reconstruction PowerShell (`powershell-setup.md` §10) for the requested date range. Output: registry snapshot, audit log extracts, configuration export. | Entra App Admin |
| 2–3 | Validate reconstruction against pre-staged evidence; resolve discrepancies. | Compliance Officer + App Admin |
| 3–5 | Compose narrative memo with hedged language; cite each evidence artifact by filename and SHA-256 hash. | Compliance Officer |
| 5–7 | Legal review of narrative memo. | Legal |
| 7–9 | Final assembly: numbered exhibit list, hash manifest, narrative memo, raw evidence files. | Compliance Officer |
| 9–10 | Production. Maintain a production log (what was sent, to whom, when, with hash manifest) — this log itself becomes evidence. | Compliance Officer |

### 15.4 Hedged-Language Discipline in Examiner Production

Every narrative memo provided to an examiner repeats the hedged-language discipline from the top of this playbook. Specifically: never assert that a configuration "ensured", "guaranteed", or "prevented" anything. Examiners read every word; the memo's job is to demonstrate **rigor of process**, not to claim outcomes that no system can guarantee.

---

## §16 — Downstream Control Linkage

Control 1.2 is upstream of nearly every other Pillar 1 and Pillar 3 control. Each registered agent inherits a set of obligations enforced by other controls; the registry row is the join key.

| Downstream control | What it consumes from 1.2 | When it fires |
|--------------------|---------------------------|--------------|
| **1.1 Conditional Access for Agents** | `agent_id` membership in `sg-workload-identities-governed`; sponsor + zone metadata for risk-tiered policies | Every sign-in by the agent's SP |
| **1.4 Advanced Connector Policies (ACP)** | `connectors_used` field; environment placement from §7 | Every connector add to a flow / agent |
| **1.7 Comprehensive Audit Logging** | `agent_id` and `appId` for audit query; sponsor metadata for examiner pivot | Continuously |
| **1.10 Communication Compliance** | `data_classification_max`, `regulated_data_in_scope`, sponsor for supervisor routing | Every agent-emitted communication |
| **1.19 Sensitivity Labels for Agent Outputs** | `data_classification_max` for label-default selection | Every agent output write |
| **1.21 Data Loss Prevention for Agent Channels** | `regulated_data_in_scope` for policy scope | Every agent egress |
| **1.23 Step-Up Authentication for Agent Operations** | `step_up_required` flag; CA policy in §12.3 | Every HVT operation |
| **1.24 Defender AI-SPM** | All registry metadata for posture join | Continuously; alerts join on `appId` |
| **2.1 Lifecycle States** | `attestation_status`, `creation_date`, `retirement_date` | At every state transition |
| **2.5 Change Management** | Schema fields 5, 12, 13, 16 (changes trigger re-attestation) | At every material change |
| **3.1 Agent Inventory** | The full registry; the canonical source of truth | Nightly reconciliation |
| **3.6 Orphan Detection** | `agent_owner_upn`, `backup_owner_upn`, sponsor membership | Daily sweep |
| **3.11 Agent Risk Scoring** | All schema fields for risk-score input | Continuously |

When you change a registry field, you implicitly change the inputs to every control above. Treat schema changes as **change-managed events** under Control 2.5; re-attestation under §14 is the natural hook.

---

## §17 — Anti-Pattern Catalog

Things that look reasonable in isolation and produce findings at scale. Each anti-pattern below has been observed in FSI tenants; each carries a remediation reference.

| # | Anti-pattern | Why it fails | Remediation |
|---|--------------|--------------|-------------|
| 1 | Service-account UPN as Agent Owner | Service accounts cannot attest; produces orphan findings on every quarterly cycle | Replace with named human; add Backup Owner |
| 2 | Single-owner app registration | First owner departure orphans the agent and triggers Zone 3 24-hour suspension | Always set Backup Owner at registration |
| 3 | Custom security attributes applied only to app registration, not SP | Audit pivots from `appId` to SP and finds no sponsor metadata | Apply attributes on SP per §4.3 |
| 4 | "Grant admin consent" clicked at app-registration time | Consent grant precedes governance workflow; reviewer never sees the request | Block with §5.2 user consent setting; route through admin consent request |
| 5 | Tenant-wide sharing on first deployment | No pilot validation; failure modes hit all users at once | Always start with security-group-scoped sharing |
| 6 | Client secret with 24-month lifetime | Rotation discipline collapses; secret leaks have year-plus exposure | Cap lifetime at 6 months; prefer Federated credential |
| 7 | Reusing a retired `agent_id` | Audit trails of two distinct agents merge; evidence integrity destroyed | Always mint a new `agent_id`; retired rows live forever in `Retired` state |
| 8 | "We'll register it after deployment" | Registration and deployment must be atomic; post-hoc registration produces a window of unsupervised operation | Hard gate: no deployment without a registry row in `Pending-Sponsor-Review` |
| 9 | Sponsor metadata only in external registry, not on Entra objects | Defender alert workflows can't pivot to sponsor; SOC routes to wrong human | Mirror sponsor to Entra custom security attributes (§3.3, §4.3) |
| 10 | Generative answers enabled on Power Platform agents touching NPI | Model-decided outputs over regulated data with no per-output supervision hook | Disable per §7.3; revisit only when 1.10 supervision can hook generative-answer outputs |
| 11 | Allowing public-web grounding in Copilot Studio for FSI agents | Outbound channel to model-controlled URLs; effectively exfiltration risk | Disable per §7.3 |
| 12 | "Just me" sharing on a Zone 3 agent | Sponsor can't observe; Compliance Officer can't attest | Zone 3 requires security-group sharing with attestation chain |
| 13 | OAuth app approved by reviewer without registry row | Defender finds the app `Sanctioned-Registered` but reconciliation fails | Reviewer must pre-stage registry row before approval (§9.2 Q9) |
| 14 | Quarterly attestation done by sending the same template to all sponsors via email | No tracker, no audit evidence of completion, no past-due escalation | Use SharePoint AgentAttestationTracker with auto-escalation per §14.3 |
| 15 | Compensating controls for preview features not reviewed quarterly | Feature goes GA, manual workaround continues, double-track creates drift | Quarterly re-verification of compensating controls |
| 16 | Service principals enabled with `Assignment required = No` for daemon flows | Doesn't break daemon flows, but obscures intent and surfaces apps to interactive users | Set `Assignment required = Yes` per §4.1 even for daemon SPs |
| 17 | Power Platform Default environment used for any Zone 2/3 agent | Default environment lacks DLP scoping; users can mint connectors freely | Force into Production environment; lock down Default per Control 1.4 |
| 18 | Ignoring the `Pending requests` queue in M365 Integrated Apps | Requests expire silently; users assume they were rejected and move to shadow IT | Reviewer SLA: process every request within 5 business days |
| 19 | Naming standard not enforced; `display_name` is free text | Examiner pulls return ambiguous results; reconciliation fails join | Enforce `<env>-<bu>-<purpose>-<seq>` per §3.1 |
| 20 | Treating Microsoft 365 Certification as sufficient vendor risk diligence | Cert attests to publisher self-assertion; doesn't substitute for TPRM | §5.3 dual-gate explicitly required |

---

## §18 — Verification Handoff

After completing this walkthrough, the Verification & Testing playbook (`./verification-testing.md`) is the next stop. Confirm at minimum:

1. Every of the seven surfaces in §0.2 is reachable in your tenant, or has a documented compensating control for any unavailable preview surfaces.
2. The 22-field schema in §1 is implemented and queryable.
3. Pre-flight gates A–E in §2 all pass.
4. At least one Zone 1, one Zone 2, and one Zone 3 agent are registered end-to-end through every relevant section of this playbook.
5. The §9 consent workflow has processed at least one approval and one rejection with evidence captured.
6. The §10 SP/MI hygiene snapshot has been run at least once and triaged.
7. The §12 Conditional Access policies are On (not Report-only).
8. The §14 attestation tracker is populated and at least one full attestation cycle has been completed end-to-end as a control rehearsal.
9. The §15 examiner audit-pull procedure has been rehearsed with a synthetic request and the production log captured.

The Verification playbook walks each item with explicit pass/fail criteria and evidence requirements.

---

## §19 — Troubleshooting Handoff

When portal steps in this playbook fail or surface unexpected state, route to `./troubleshooting.md` for the remediation matrix. The most common 1.2 troubleshooting topics covered there:

- Custom security attributes blade is empty / inaccessible (Entra role and license issues).
- Service principal Owner blade shows `Application` instead of a human (legacy ACS or app-only token issuance).
- Agent ID surface absent in Enterprise Applications (Copilot license / preview enrollment).
- Power Platform Copilot agent created but not visible in admin center (environment indexing delay or DLP block during publish).
- M365 Integrated Apps Pending requests queue empty when users report submitting requests (admin consent settings misconfiguration in §5.2).
- Defender for Cloud Apps OAuth apps view shows "Not licensed" (license / connector setup gap).
- Conditional Access for workload identity policy not applying to a specific SP (group membership lag or `Assignment required` interaction).
- Quarterly attestation Power Automate flow stuck in "Failed" state (SharePoint list schema drift or Forms permission revoked).

---

## §20 — Cross-References and Closing Reminders

### 20.1 Sibling Playbooks

- `./powershell-setup.md` — every PowerShell automation referenced in this walkthrough (registration capture, SP/MI hygiene sweeps, examiner point-in-time reconstruction, attestation tracker population).
- `./verification-testing.md` — pass/fail criteria for every step here.
- `./troubleshooting.md` — remediation matrix.
- `./sponsorship-lifecycle-workflows.md` — the sponsorship lifecycle plumbing referenced throughout §11 and §14.

### 20.2 Related Pillar 1 Controls

- `../1.1-conditional-access-for-agents/portal-walkthrough.md`
- `../1.4-advanced-connector-policies-acp.md`
- `../1.7-comprehensive-audit-logging-and-compliance.md`
- `../1.10-communication-compliance-monitoring.md`
- `../1.19/portal-walkthrough.md`
- `../1.21/portal-walkthrough.md`
- `../1.23-step-up-authentication-for-agent-operations.md`
- `../1.24-defender-ai-security-posture-management.md`

### 20.3 Related Pillar 2 / 3 Controls

- `../2.1/portal-walkthrough.md`
- `../2.5/portal-walkthrough.md`
- `../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- `../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`

### 20.4 Incident Response Tie-In

- `../../incident-and-risk/ai-incident-response-playbook.md` — when an incident references a registered agent, the sponsor, owner, and Compliance Officer surfaced from the registry per §11.2 are the first three notifications.

### 20.5 Closing Hedged-Language Reminder

This playbook describes a configuration and operating discipline that **supports compliance with** FINRA Rule 4511, FINRA RN 24-09 / Rule 3110, SEC Rule 17a-4(b)(4) and 17a-4(g), SOX Sections 302 and 404, GLBA Section 501(b), NYDFS 23 NYCRR 500.07 / 500.16 / 500.17, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Federal Reserve SR 26-2 (formerly SR 11-7), NIST AI RMF GOVERN 1.4 and 1.6, FTC Safeguards Rule 16 CFR §314.4(c), and CFTC Rule 1.31. **Implementation requires sustained operator discipline; organizations should verify configuration against current regulatory expectations and their own legal counsel's interpretation. The procedures in this playbook do not constitute legal advice and do not, by themselves, demonstrate regulatory compliance.**

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
