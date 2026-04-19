# Control 1.2 — Troubleshooting: Agent Registry & Integrated Apps Management

**Control:** 1.2 — Agent Registry and Integrated Apps Management
**Pillar:** Pillar 1 — Security
**Audience:** Entra Global Admin, Entra Application Admin, Power Platform Admin, M365 Copilot Admin, Defender for Cloud Apps Admin, Purview Compliance Admin, AI Governance Lead, Incident Response Lead, FSI Compliance Officer
**Companion playbooks:**
[Portal walkthrough](./portal-walkthrough.md) ·
[PowerShell setup](./powershell-setup.md) ·
[Verification & testing](./verification-testing.md) ·
[Sponsorship lifecycle workflows](./sponsorship-lifecycle-workflows.md)

> **Scope.** This troubleshooting playbook covers the seven registration surfaces governed by Control 1.2 — (1) Microsoft Entra App Registrations, (2) Integrated Apps blade in the Microsoft 365 admin center, (3) Power Platform Copilot Studio agents (Dataverse `bot` table), (4) Microsoft Graph `/applications` and `/servicePrincipals` (and the preview `/copilot/agents` and `/agents` endpoints), (5) Microsoft 365 Copilot declarative agent manifests, (6) Model Context Protocol (MCP) servers fronted by Entra app registrations, and (7) the Microsoft Agent 365 / Agent Registry preview admin centers. It also covers the cross-cutting OAuth-grant governance plane in Microsoft Defender for Cloud Apps and Conditional Access workload-identity policies.
>
> Use this document when a registration surface has produced a failure, a discrepancy, an orphaned object, an unauthorized grant, or an examiner inquiry. For day-2 operations, use [verification-testing.md](./verification-testing.md). For first-time setup, use [portal-walkthrough.md](./portal-walkthrough.md) and [powershell-setup.md](./powershell-setup.md).

---

## Table of Contents

- [§1. FSI Incident Handling Framework (Registration-Plane Specific)](#1-fsi-incident-handling-framework-registration-plane-specific)
  - [1.1 Severity Classification Matrix](#11-severity-classification-matrix)
  - [1.2 Aggravating-Factor Severity Bumps](#12-aggravating-factor-severity-bumps)
  - [1.3 Reportability Decision Tree (Q1–Q10)](#13-reportability-decision-tree-q1q10)
  - [1.4 Evidence Floor (E-01 … E-15)](#14-evidence-floor-e-01-e-15)
  - [1.5 Compensating Controls Matrix](#15-compensating-controls-matrix)
  - [1.6 Pre-Escalation Checklist (≥15 items)](#16-pre-escalation-checklist-15-items)
  - [1.7 Communication Ladder (L1–L5)](#17-communication-ladder-l1l5)
  - [1.8 Worked Example — SEV-1 Shadow Agent with Mail.ReadWrite](#18-worked-example-sev-1-shadow-agent-with-mailreadwrite)
  - [1.9 Diagnostic Query Reference (DQ-1 … DQ-8)](#19-diagnostic-query-reference-dq-1-dq-8)
- [§2. Eight Troubleshooting Pillars](#2-eight-troubleshooting-pillars)
  - [Pillar A — Entra App Registration Failures](#pillar-a-entra-app-registration-failures)
  - [Pillar B — Integrated Apps (M365 Admin) Failures](#pillar-b-integrated-apps-m365-admin-failures)
  - [Pillar C — Power Platform / Copilot Studio Registration Failures](#pillar-c-power-platform-copilot-studio-registration-failures)
  - [Pillar D — Microsoft Graph Application API Failures](#pillar-d-microsoft-graph-application-api-failures)
  - [Pillar E — Agent 365 / Agent Registry Preview Gaps](#pillar-e-agent-365-agent-registry-preview-gaps)
  - [Pillar F — Defender for Cloud Apps OAuth Governance Failures](#pillar-f-defender-for-cloud-apps-oauth-governance-failures)
  - [Pillar G — Conditional Access Workload-Identity Policy Failures](#pillar-g-conditional-access-workload-identity-policy-failures)
  - [Pillar H — Sovereign-Cloud / Per-Tenant Feature Gaps](#pillar-h-sovereign-cloud-per-tenant-feature-gaps)
- [§3. Failure-Mode Runbooks (Detailed)](#3-failure-mode-runbooks-detailed)
  - [Runbook 1 — Shadow Agent Discovered (Unregistered Production Agent)](#runbook-1-shadow-agent-discovered-unregistered-production-agent)
  - [Runbook 2 — Mass Departed-Owner Cascade (>50 Apps)](#runbook-2-mass-departed-owner-cascade-50-apps)
  - [Runbook 3 — Over-Permissioned Grant Exploited](#runbook-3-over-permissioned-grant-exploited)
  - [Runbook 4 — Expired Secret Used in Production](#runbook-4-expired-secret-used-in-production)
  - [Runbook 5 — Admin Consent Workflow Tampering](#runbook-5-admin-consent-workflow-tampering)
  - [Runbook 6 — CA Workload-Identity Policy Misfire](#runbook-6-ca-workload-identity-policy-misfire)
  - [Runbook 7 — Sponsor / Owner Attestation Lapse](#runbook-7-sponsor-owner-attestation-lapse)
  - [Runbook 8 — Cross-Cloud Sovereign Boundary Breach](#runbook-8-cross-cloud-sovereign-boundary-breach)
  - [Runbook 9 — Examiner Audit Pull (FINRA / OCC / Fed Snapshot)](#runbook-9-examiner-audit-pull-finra-occ-fed-snapshot)
- [§4. Common Symptom → Cause → Resolution Index](#4-common-symptom-cause-resolution-index)
- [§5. Tooling, Endpoints, and Module Versions](#5-tooling-endpoints-and-module-versions)
- [§6. Known Issues, Preview Caveats, and Documented Gaps](#6-known-issues-preview-caveats-and-documented-gaps)
- [§7. Escalation Contacts and Vendor Support](#7-escalation-contacts-and-vendor-support)
- [§8. Cross-References](#8-cross-references)

---

## §1. FSI Incident Handling Framework (Registration-Plane Specific)

This framework adapts the canonical FSI Incident Handling pattern (originally documented for Control 3.1 inventory-plane incidents and Control 1.6 broader incident response) to the **registration plane** specifically — the moment an agent identity is created, modified, granted, or deleted across any of the seven Control 1.2 surfaces. Registration-plane incidents differ from runtime incidents because the **identity itself** (the principal, the consent grant, the credential) is the failure object, not the data the agent processes. That distinction changes the evidence you collect, the controls you compensate with, and the regulators you notify.

> **Hedging note.** This framework helps meet, and is recommended to support compliance with, the regulations cited below. It does not by itself satisfy any reporting obligation. Implementation requires legal review and organizations should verify each obligation against current rule text and the firm's written supervisory procedures (WSPs) before relying on the timing or scope guidance here.

### 1.1 Severity Classification Matrix

The matrix below provides an **initial** severity classification for registration-plane incidents. All severities are subject to upward adjustment under the aggravating-factor rules in §1.2. The Incident Commander has the authority — and the documented obligation — to bump severity at any time during the response based on new facts.

| Severity | Definition (registration plane) | Examples | Initial response time | Decision authority |
|----------|---------------------------------|----------|----------------------|--------------------|
| **SEV-1** | An unregistered or improperly registered agent is operating in production with a high-privilege grant (Mail.ReadWrite, Files.ReadWrite.All, Sites.FullControl.All, Directory.ReadWrite.All, application-permission Graph scope) **and** has touched, or could touch, regulated data (NPI, MNPI, customer transaction data, books-and-records). Includes confirmed unauthorized OAuth grant exploitation; tampering with the admin consent workflow; or any registration-plane event currently under active regulator examination. | Shadow Copilot Studio bot with Mail.ReadWrite consented by a non-admin via user-consent workflow; tenant-wide application permission granted without admin approval; service principal credential exfiltrated and used. | **15 minutes** to assemble bridge; **1 hour** to first containment action. | CISO + AI Governance Lead jointly; legal must be on the bridge within 30 minutes. |
| **SEV-2** | A registered agent has a material registration defect (missing sponsor, expired owner, expired secret in active use, missing required attestation, scope drift beyond approved minimum-necessary set) **or** an orphaned high-privilege application principal exists with no current owner. Regulated data may be exposed but no confirmed exfiltration. | Critical-tier agent owner departed >30 days ago and Sponsor has not re-attested; application secret expired and the agent is failing closed but with regulated traffic queued; >10 apps with no owner discovered in monthly attestation. | **1 hour** to triage; **4 hours** to first containment action. | AI Governance Lead; CISO informed; Compliance informed within 4 hours. |
| **SEV-3** | A registration hygiene defect with low immediate risk — for example, low-privilege agent with stale metadata, manifest version mismatch, ownership recorded only in one of the two required attestation records, or a documented preview-API gap that requires manual reconciliation. | Reply-domain mismatch on a low-privilege agent; declarative manifest version drift; PPAC vs. Dataverse `bot` count mismatch attributable to known propagation lag. | **1 business day** to triage. | Control owner (delegated). |
| **SEV-4** | Cosmetic, documentation, or process-improvement issue with no production impact. | Display-name typo; missing optional tag; description field below preferred length. | **5 business days**. | Control owner (delegated). |

### 1.2 Aggravating-Factor Severity Bumps

If **any** of the following factors applies, bump the initial severity by **one full level** (SEV-3 → SEV-2, SEV-2 → SEV-1). If **two or more** factors apply, bump by two levels and treat as SEV-1 by default. Document each factor explicitly in the incident record (E-11 operator-context manifest, see §1.4).

1. **NPI involvement** — the agent has, or had within the look-back window, access to nonpublic personal information as defined under GLBA §6809(4) and the FTC Safeguards Rule (16 CFR 314.2). Triggers GLBA notification analysis.
2. **MNPI involvement** — the agent has, or had access to, material nonpublic information (insider lists, deal rooms, earnings drafts, research-under-embargo). Triggers Reg FD, Rule 10b5-1, and information-barrier review.
3. **MRM scope** — the agent meets the firm's definition of a "model" under SR 11-7 / OCC 2011-12 (i.e., applies statistical, economic, financial, or mathematical theories to produce quantitative estimates that drive a business decision). Triggers MRM independent validation review.
4. **Active regulator examination** — FINRA, SEC, OCC, Fed, NYDFS, or state regulator has an open exam, sweep, or inquiry that touches the agent, its owner, its sponsoring business unit, or the data domain. **Document preservation hold attaches automatically.**
5. **Sovereign cloud** — the agent is registered in GCC, GCC High, or DoD; cross-tenant or cross-cloud blast radius is presumed unless proven otherwise.
6. **Personnel change in the look-back window** — owner, sponsor, or backup owner departed, transferred, or had role changes within the prior 90 days. Increases insider-threat probability.
7. **High-privilege grant** — any application-permission scope, any `*.ReadWrite.All` scope, any `Directory.*` scope, or any scope explicitly listed on the firm's high-privilege register.
8. **Customer-facing surface** — agent is exposed to retail clients, intermediaries, or external counterparties (vs. internal-only).
9. **Books-and-records touch** — the agent reads, writes, or could write to any system that produces SEC 17a-4 or FINRA 4511 books-and-records artifacts.
10. **Cross-border data flow** — the agent processes data subject to a non-US data-protection regime (UK, EU, APAC) that could trigger parallel notification clocks.

### 1.3 Reportability Decision Tree (Q1–Q10)

Walk these questions in order. Each "yes" creates a **distinct** notification clock that runs independently. Multiple clocks routinely run in parallel — do not assume that satisfying one obligation discharges another. **Confirm every answer with Legal and Compliance before relying on it.**

| # | Question | If "Yes," consider | Typical clock |
|---|----------|---------------------|---------------|
| **Q1** | Is the agent or its owner subject to FINRA membership, and could the registration defect have allowed a communication with the public, with a customer, or among associated persons that lacks required supervision? | **FINRA Rule 3110** (supervision) and **FINRA Rule 3110.18** (communications). Consider whether the firm's WSPs covered the agent's communications channel. | Internal — feeds annual 3120 report and may surface in cycle exam. |
| **Q2** | Did the registration defect cause a books-and-records writing to be created, modified, or deleted outside a WORM-compliant store? | **SEC Rule 17a-4** (broker-dealers), **SEC Rule 204-2** (advisers), **FINRA Rule 4511**, **CFTC Rule 1.31** (FCMs/swap dealers). Books-and-records integrity issues frequently require **immediate self-report** under firm WSPs. | Self-report typically same business day per WSP; no statutory clock but examiners expect prompt disclosure. |
| **Q3** | Does the incident involve associated-person conduct, customer complaints, or compliance violations that meet a **FINRA Rule 4530** reportable event category (statutory disqualification, customer complaint involving compensatory damages ≥$15K, internal review of associated person, etc.)? | **FINRA Rule 4530(a)/(b)/(d)** filings via the Firm Gateway. | **30 calendar days** from when the firm knew or should have known. |
| **Q4** | Was a customer-facing AI agent involved, and could its registration defect have caused a misrepresentation, an unsuitable recommendation, an unauthorized communication, or a privacy breach to a retail customer? | **FINRA Regulatory Notice 25-07** (AI-related supervisory and disclosure expectations). Document the supervisory failure analysis even if no other rule is implicated. | Internal documentation immediate; customer remediation per Reg BI / firm policy. |
| **Q5** | Did NPI of a customer become accessible to an unauthorized person, system, or service principal as a result of the registration defect? | **SEC Regulation S-P §248.30(a)(3)–(4)** customer-notification rule (as amended 2024, effective for larger entities Dec 2025 / smaller entities Jun 2026). **GLBA §501(b)** and the **FTC Safeguards Rule** (16 CFR 314.4(j)) notification requirements. | **30 days** under amended Reg S-P (from determination of unauthorized access). FTC Safeguards: notify FTC of incidents affecting ≥500 consumers **as soon as possible and no later than 30 days**. |
| **Q6** | Is the registrant or its parent an **SEC registrant** and does the incident meet the materiality threshold for **Form 8-K Item 1.05** (material cybersecurity incident)? | **SEC Form 8-K Item 1.05**. Materiality determination is itself a reportable event — document the determination meeting and conclusion. | **4 business days** from the date the registrant determines the incident is material. |
| **Q7** | Is the firm a **NYDFS Part 500 covered entity**, and does the incident meet the **§500.1(g) cybersecurity event** definition (a cybersecurity event affecting the covered entity that has a reasonable likelihood of materially harming any material part of normal operations, **or** notice was provided to any government body, self-regulatory agency, or supervisory body)? | **23 NYCRR §500.17(a)** notification to the Superintendent. | **72 hours** from determination. |
| **Q8** | Does the agent meet the firm's **model** definition under SR 11-7 / OCC Bulletin 2011-12, and did the registration defect bypass MRM independent validation? | **SR 11-7 / OCC 2011-12** model risk management findings. Likely an MRA (matter requiring attention) at next exam if uncorrected. | Internal MRM tracking; surfaces at next safety-and-soundness or BSA exam. |
| **Q9** | Did the incident involve a third-party / vendor / ISV agent (e.g., publisher-side declarative agent, third-party MCP server, marketplace OAuth app) and could it implicate **third-party risk management** obligations? | **OCC Bulletin 2013-29** (and 2020-10), **Federal Reserve SR 23-4** / **FDIC FIL-29-2023** (Interagency TPRM Guidance, June 2023). Update vendor risk register; consider re-scoring the vendor. | Internal; surfaces at next TPRM and IT exams. |
| **Q10** | Is the agent registered in a CFTC-jurisdictional entity (FCM, swap dealer, CTA/CPO) and does the defect implicate recordkeeping under **CFTC Rule 1.31**, position-limit aggregation under Part 150, or risk-management programs under Reg 1.11 / 23.600? | **CFTC Rule 1.31, Part 150, Reg 1.11/23.600**. NFA Compliance Rule 2-9 supervisory obligations. | Internal; reportable to CFTC/NFA per applicable rule and firm WSPs. |

> **Process rule.** All "yes" answers must be documented in the incident record with: (i) the rule citation, (ii) the clock start time and basis, (iii) the responsible Compliance reviewer, (iv) the legal-privilege designation, and (v) the planned filing date. Use the firm's GRC tool of record.

### 1.4 Evidence Floor (E-01 … E-15)

The evidence floor is the **minimum** set of artifacts that must be captured for any registration-plane incident at SEV-2 or above. SEV-1 incidents require all 15. SEV-3 incidents require E-01 through E-07 at minimum. Capture **before** containment actions destroy state.

| # | Artifact | Source | Capture method | Retention |
|---|----------|--------|----------------|-----------|
| **E-01** | Surface screenshot — Entra App Registration blade | Entra admin center → Identity → Applications → App registrations → *(app)* → Overview | Full-page screenshot (timestamp visible) + `Get-MgApplication -ApplicationId <id> \| ConvertTo-Json -Depth 10` | 7 years (books-and-records aligned) |
| **E-02** | Surface screenshot — Service Principal blade | Entra admin center → Enterprise applications → *(app)* → Permissions, Properties, Sign-in logs | Full-page screenshots + `Get-MgServicePrincipal -ServicePrincipalId <id> \| ConvertTo-Json -Depth 10` | 7 years |
| **E-03** | Integrated Apps blade snapshot | M365 admin center → Settings → Integrated apps → *(app)* | Full-page screenshot of overview, users, permissions, deployment tabs | 7 years |
| **E-04** | PPAC + Dataverse `bot` table snapshot | Power Platform admin center → Environments → *(env)* → Copilots; **and** Dataverse `bot` and `botcomponent` tables via `Invoke-DataverseRequest` | PPAC screenshot + Dataverse `SELECT botid, name, ownerid, statecode, statuscode, createdon, modifiedon, schemaname, configuration FROM bot` export to JSON | 7 years |
| **E-05** | Microsoft Graph snapshot of `/applications/{id}` and `/servicePrincipals/{id}` | `https://graph.microsoft.com/v1.0/applications/{id}`, `https://graph.microsoft.com/v1.0/servicePrincipals/{id}`, `…/oauth2PermissionGrants`, `…/appRoleAssignments` | `Invoke-MgGraphRequest` to JSON files; capture `@odata.context` and ETag headers | 7 years |
| **E-06** | Agent Register state (firm system of record) | Internal GRC / agent register | Export current row + full version history (createdBy, modifiedBy, modifiedOn, prior values) | 7 years |
| **E-07** | Purview Unified Audit Log query result | Purview portal → Audit (or `Search-UnifiedAuditLog`) | Capture all events for the affected app/principal for the look-back window (default 30 days; 90 for SEV-1) using `RecordType` filters: AzureActiveDirectory, AzureActiveDirectoryStsLogon, ApplicationAudit, MicrosoftGraphActivityLogs, PowerPlatformAdminActivity, MicrosoftTeams, OneDrive, SharePointFileOperation, MicrosoftFlow, MicrosoftPowerBI, CopilotInteraction | 7 years |
| **E-08** | Purview DSPM for AI — Activity Explorer export | Purview portal → DSPM for AI → Activity Explorer | Filter by app/principal; export to CSV; capture sensitivity-label hits and SIT (sensitive information type) hits | 7 years |
| **E-09** | DLP / Retention / Sensitivity-Label inventory applicable to the agent's scope | Purview policies for the affected workloads (Exchange, SPO/ODB, Teams, Endpoint, Power Platform, Fabric) | Export policy configurations and the policy-to-app applicability matrix | 7 years |
| **E-10** | Entra owner state (current + historical) | `Get-MgApplicationOwner`, `Get-MgServicePrincipalOwner`; HR system of record for personnel status | Export owner list with `signInActivity`, `accountEnabled`, `employeeHireDate`, `employeeLeaveDateTime` | 7 years |
| **E-11** | PIM activation log | Entra admin center → PIM → My audit history (and tenant audit) | Export all PIM activations within the look-back window for any role that could have modified the app or its grants (Application Admin, Cloud Application Admin, Privileged Role Admin, Global Admin) | 7 years |
| **E-12** | Sign-in logs (interactive + non-interactive + service-principal sign-ins) | Entra admin center → Monitoring → Sign-in logs (or `Get-MgAuditLogSignIn`) | Filter by `appId`, `servicePrincipalId`, and `resourceId`; export all four sign-in tabs | 7 years |
| **E-13** | Operator-context manifest | Compiled by Incident Commander | Document: who is on the bridge, with what role, under what privilege (legal hold, attorney-client, work product), with what authority to act, and the known/unknown state at each decision point | 7 years |
| **E-14** | SDK / module / API version manifest | Capture: `Get-Module Microsoft.Graph -ListAvailable`; `Get-Module Microsoft.PowerApps.Administration.PowerShell -ListAvailable`; `Get-Module Microsoft.Online.SharePoint.PowerShell -ListAvailable`; `az version`; the Graph API versions used (`v1.0` vs `beta`); the PPAC `-Endpoint` flag value used | Save as `versions.json` alongside other artifacts | 7 years |
| **E-15** | SHA-256 manifest of all collected artifacts | `Get-FileHash -Algorithm SHA256 *` over the evidence directory; sign the manifest with the IR team's PGP key or the firm's evidence-signing certificate | Store hash manifest separately from artifacts; commit to evidence-management system | 7 years |

> **Chain of custody.** Every artifact must include capture timestamp (UTC), capture operator, source URL/cmdlet, and the SHA-256 from E-15. Where artifacts contain customer NPI or MNPI, follow the firm's privileged-data handling SOP — do **not** stage them in general-purpose ticketing systems.

### 1.5 Compensating Controls Matrix

When a registration-plane defect is detected but immediate remediation is not yet possible, deploy the following compensating controls. Document the compensating control in the incident record with a defined sunset date.

| Defect | Compensating control | Implementation surface | Sunset condition |
|--------|----------------------|------------------------|-------------------|
| Unverified or shadow registration | Block sign-in on the service principal (`Update-MgServicePrincipal -AccountEnabled:$false`); add the appId to a **CA workload-identity policy** that blocks all sign-ins | Entra ID + Conditional Access | Registration verified, sponsor & owner re-attested, scope re-approved |
| Over-permissioned grant | Revoke the specific oauth2PermissionGrant or appRoleAssignment; if revocation breaks the agent, scope-down via a **least-privilege replacement grant** under temporary admin consent with 30-day expiry | Entra ID `/oauth2PermissionGrants` and `/appRoleAssignments` | Long-term grant request submitted, MRM (if applicable) re-validation complete |
| Expired secret in active use | Issue **short-lived (24-72h) replacement credential**; require migration to **federated credential** or **managed identity** before sunset; log all uses against the temporary credential | Entra ID app credential | Federated credential or managed identity in place; legacy secret removed |
| Owner departed >30 days | Assign **Sponsor as temporary owner** (not a non-human shared mailbox); record the temporary assignment in the agent register; require backup-owner identification within 14 days | Entra ID app owner + Sponsorship register | New permanent owner attested by Sponsor; backup owner attested |
| Sponsor attestation lapse | **Freeze** the agent (block sign-in or pause Copilot Studio bot via `statecode = 1` in Dataverse); notify business unit head; require Sponsor re-attestation or Sponsor reassignment | Entra ID + Dataverse `bot` | Sponsor re-attests or new Sponsor designated |
| Manifest version drift / declarative-agent mismatch | Restrict the agent to **Zone 1** until manifest reconciliation; suppress promotion to Zone 2/3 in the agent register | Microsoft 365 admin center deployment policies; agent register | Manifest reconciled, version pinned, change ticket closed |
| Preview-API gap (Agent 365 / `/copilot/agents`) | **Manual reconciliation** — capture both the preview-API state and the underlying primary surface (Entra app reg, Dataverse `bot`, Integrated Apps) state; document the discrepancy in the agent register's "known gaps" field | Manual; documented in [verification-testing.md](./verification-testing.md) | Microsoft GA of the preview API; or vendor-confirmed reconciliation |
| Cross-cloud capability gap (GCC High lacks a feature) | Implement the **commercial-equivalent compensating control** (e.g., if a Defender for Cloud Apps OAuth app policy is GA in commercial but preview/absent in GCC High, substitute a Conditional Access workload-identity policy plus a daily Graph-based detection report) | CA + custom Graph queries + Sentinel | Microsoft adds feature parity; or compensating control approved as permanent |

### 1.6 Pre-Escalation Checklist (≥15 items)

Before escalating to Legal, Compliance, or executive leadership, the Incident Commander **should** complete the following 17-item checklist. Items that cannot be completed must be explicitly noted as "unable to complete — reason: …" rather than skipped silently.

1. **Severity classified** per §1.1 and aggravating-factor analysis per §1.2 documented in the incident record.
2. **Scope defined** — list of affected appIds, servicePrincipalIds, Copilot Studio botIds, declarative-agent manifest IDs, and any user accounts that consented to the affected app.
3. **Reportability tree (§1.3) walked** with Compliance reviewer named for each "yes" answer.
4. **Evidence floor (§1.4) capture initiated** — at least E-01 through E-07 captured before any containment action that mutates state.
5. **Containment options identified** — for each containment action, document: (a) action, (b) blast radius, (c) reversibility, (d) decision authority, (e) required approver.
6. **Compensating controls (§1.5) selected** with sunset dates assigned.
7. **Document preservation hold** issued or confirmed (especially if Q4 active examination = yes).
8. **Privilege analysis** — Incident Commander confirms with Legal whether the response is conducted under attorney-client privilege / attorney work product, and labels artifacts accordingly.
9. **Communications plan** drafted per §1.7 ladder; talking points reviewed by Legal **before** any external statement.
10. **Customer-impact assessment** initiated — at minimum: are any customer-facing surfaces involved? Any NPI? Any retail clients?
11. **Vendor / third-party assessment** — was any third-party agent, MCP server, ISV connector, or marketplace OAuth app involved? If yes, vendor incident-response contact engaged.
12. **HR coordination** — if owner, sponsor, or any insider is implicated, HR engaged before any access changes that could be construed as adverse employment action.
13. **Forensics readiness** — if the response may require external forensics counsel or vendor (Mandiant, CrowdStrike, etc.), retainer status confirmed.
14. **Regulator preservation triggers** — if any active examination touches the affected agent/owner/BU, document-preservation scope formally extended; counsel notified.
15. **Sovereign-cloud boundary** — confirm whether the incident is contained to commercial / GCC / GCC High / DoD; if cross-cloud, immediately escalate to SEV-1 and notify the cleared personnel pool.
16. **Insurance notification trigger evaluated** — does the firm's cyber insurance policy require notice within a specific window (often 72 hours)? Document the notification decision.
17. **Lessons-learned tracker** opened in the post-incident review tool (do not wait until the end — capture observations during the response).

### 1.7 Communication Ladder (L1–L5)

Communications cascade upward and outward. Each level has defined triggers, recipients, channels, message owners, and Legal review requirements. **No external communication leaves the firm without Legal sign-off.**

| Level | Trigger | Recipients | Channel | Message owner | Legal review |
|-------|---------|------------|---------|---------------|--------------|
| **L1 — Operator** | Any SEV-3/4 detected, or SEV-1/2 in first 15 minutes | IR on-call, control owner, IT operations duty manager | Bridge call + ticket | Incident Commander | Not required (internal operational) |
| **L2 — Functional leadership** | SEV-2 confirmed or SEV-1 at any point | CISO, AI Governance Lead, Compliance lead, Privacy lead | Email + bridge | Incident Commander | Required for any written summary that may be retained |
| **L3 — Executive** | SEV-1, or SEV-2 with regulatory-notification clock running | CEO, COO, CFO, CRO, GC, CISO | Executive briefing memo + verbal | GC + CISO | Required |
| **L4 — Board / Audit Committee** | SEV-1 with material-incident determination, or any incident requiring SEC 8-K Item 1.05 disclosure, or any incident triggering NYDFS §500.17 notification | Board (or Audit / Risk Committee) | Formal board memo | GC | Required |
| **L5 — External** | Any required regulator notification, customer notification under Reg S-P / GLBA / state law, public disclosure under 8-K Item 1.05, vendor notifications | Regulators (FINRA, SEC, OCC, Fed, NYDFS, FTC, state AGs, CFTC/NFA), customers, vendors, media (only via Communications) | Per regulator / per WSP; never via direct executive email | GC + Compliance | **Required and dispositive** |

> **Channel rule.** Bridge audio, chat transcripts, and any chat-based decisions are **discoverable and retained per WSP**. Do not use ephemeral channels (auto-delete chat, disappearing messages) for incident communications.

### 1.8 Worked Example — SEV-1 Shadow Agent with Mail.ReadWrite

**Scenario.** At 09:14 ET on a Tuesday, the daily Defender for Cloud Apps OAuth app discovery report flags a service principal named `WealthMgmt-ClientPrep-AI` with **Mail.ReadWrite** (delegated) consented to it by 47 financial advisors over the prior 9 days. The app does not appear in the firm's agent register. The advisors are wealth-management associated persons (FINRA-registered) handling retail-customer correspondence.

**Minute-by-minute response (first 4 hours).**

- **T+0 (09:14)** — Detection alert fires in Sentinel (sourced from Defender for Cloud Apps OAuth app discovery). On-call IR analyst acknowledges within 4 minutes. Initial classification: SEV-2 (registered defect, high-privilege scope, no confirmed exfiltration).
- **T+9 (09:23)** — On-call analyst applies §1.2 aggravating-factor analysis: NPI involvement = **yes** (customer correspondence accessed); customer-facing = **yes** (advisors interact with retail clients); books-and-records touch = **yes** (FINRA 4511 / SEC 17a-4 communications). Three factors → bump to **SEV-1**.
- **T+12 (09:26)** — Bridge opens. Incident Commander designated (AI Governance Lead deputy, since lead is in a meeting that GC pulls them out of by T+18). CISO, GC, Compliance, Privacy, and the wealth-management business-unit COO join by T+25.
- **T+15 (09:29)** — Evidence capture begins. E-01, E-02, E-03, E-04, E-05 captured **before** any containment action. E-07 (Purview audit log) initiated for a 30-day look-back. E-12 (sign-in logs) shows the app authenticated 1,247 times in 9 days.
- **T+45 (09:59)** — First containment decision. Options:
  - Disable the service principal (`Update-MgServicePrincipal -AccountEnabled:$false`) — fast, reversible, but advisors lose the tool mid-day.
  - Revoke just the Mail.ReadWrite grant (`Remove-MgOauth2PermissionGrant`) — surgical, preserves any non-mail functionality.
  - Add the appId to a CA workload-identity block policy — defense-in-depth.
  IC selects **all three** to be applied simultaneously at T+60. Business-unit COO accepts the productivity impact in writing (chat log captured to E-13).
- **T+60 (10:14)** — Containment applied. CA policy hits within 90 seconds. `Get-MgServicePrincipalSignInActivity` confirms no successful sign-ins after T+62.
- **T+90 (10:44)** — Reportability tree (§1.3) walked with Compliance. Yes answers: Q1 (3110 supervision — advisors used an unsupervised tool for customer comms), Q2 (4511 / 17a-4 — communications outside WORM store, since the app accessed mailbox content but the firm cannot yet confirm what was read or written back), Q4 (Notice 25-07), Q5 (Reg S-P NPI — clock starts at T+0 per Compliance guidance).
- **T+120 (11:14)** — L3 executive briefing memo drafted by IC, reviewed by GC, delivered to CEO/CRO/CFO at T+150.
- **T+180 (12:14)** — Materiality assessment for SEC 8-K Item 1.05 begins (registrant is the parent holding company). GC chairs; CFO, Investor Relations, External Counsel, CISO participate. Determination by T+240: **not yet material** pending forensics on what data the app actually accessed; re-evaluate at 24h, 48h, 72h.
- **T+240 (13:14)** — Forensics handoff. External counsel engages forensics vendor under privilege. Scope: reconstruct, per session, what mail items the app `read` and `wrote`; identify whether any customer NPI was transmitted off-tenant via the app's reply URL.

**Reporting clocks running at T+240:**

- Reg S-P §248.30(a)(3)–(4) — 30-day customer notification clock running from T+0; preliminary determination expected by T+72h.
- NYDFS §500.17 — 72-hour clock running from "determination of cybersecurity event"; Compliance + GC have set determination at T+90 minutes; notification due by **T+90min + 72h**.
- FINRA 4530 — only triggered if the post-mortem reveals associated-person conduct meeting (b)(1) — under review.
- SEC 8-K 1.05 — re-evaluated at 24h.

**Lessons learned (subset, captured as observations during the response, finalized in post-mortem at T+30 days):** (i) user-consent for application permissions on Microsoft Graph was not blocked at the tenant level for **non-verified-publisher apps** with Mail.* scopes — closed within 24 hours; (ii) Defender for Cloud Apps OAuth app policy did not auto-revoke for Mail.ReadWrite even though firm policy required it — policy reconfigured; (iii) the agent register's discovery feed from Defender for Cloud Apps was running daily; cadence increased to hourly for Mail.* / Files.* / Sites.* scopes; (iv) the wealth-management business unit had no Sponsor designated for AI tools — Sponsor designated as a Control 1.2 prerequisite for the BU.

### 1.9 Diagnostic Query Reference (DQ-1 … DQ-8)

These eight queries form the standard diagnostic library for Control 1.2 incidents. Run them as a kit early in any SEV-1/2 response. Versions for commercial, GCC, and GCC High are noted where they differ.

**DQ-1 — Inventory all application registrations created or modified in the last N days.**

```powershell
Connect-MgGraph -Scopes Application.Read.All, AuditLog.Read.All
$since = (Get-Date).AddDays(-30).ToString('o')
Get-MgApplication -All -Filter "createdDateTime ge $since or" `
  | Select-Object Id, AppId, DisplayName, CreatedDateTime, PublisherDomain, SignInAudience, `
                  @{n='Owners';e={(Get-MgApplicationOwner -ApplicationId $_.Id).AdditionalProperties.userPrincipalName -join ';'}} `
  | Export-Csv -NoTypeInformation .\dq1-apps.csv
```

For GCC High, set `Connect-MgGraph -Environment USGovHigh`. For DoD, `-Environment USGovDoD`.

**DQ-2 — Identify all service principals with high-privilege application-permission grants.**

```powershell
$highPriv = @('Mail.ReadWrite','Mail.Send','Files.ReadWrite.All','Sites.FullControl.All',
              'Directory.ReadWrite.All','User.ReadWrite.All','Application.ReadWrite.All',
              'AppRoleAssignment.ReadWrite.All','RoleManagement.ReadWrite.Directory')
Get-MgServicePrincipal -All -Filter "servicePrincipalType eq 'Application'" |
  ForEach-Object {
    $sp = $_
    Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $sp.Id |
      Where-Object { $_.AppRoleId -ne [guid]::Empty } |
      ForEach-Object {
        $resource = Get-MgServicePrincipal -ServicePrincipalId $_.ResourceId
        $role = $resource.AppRoles | Where-Object Id -eq $_.AppRoleId
        if ($role.Value -in $highPriv) {
          [pscustomobject]@{
            AppDisplayName = $sp.DisplayName
            AppId          = $sp.AppId
            Resource       = $resource.DisplayName
            Permission     = $role.Value
            GrantedOn      = $_.CreatedDateTime
          }
        }
      }
  } | Export-Csv -NoTypeInformation .\dq2-highpriv-grants.csv
```

**DQ-3 — Power Platform Copilot Studio bots not present in the agent register.**

```powershell
Add-PowerAppsAccount -Endpoint prod   # use 'usgovhigh' for GCC High
$envs = Get-AdminPowerAppEnvironment
$bots = foreach ($e in $envs) {
  Invoke-DataverseRequest -EnvironmentName $e.EnvironmentName -Method GET `
    -Url "/api/data/v9.2/bots?`$select=botid,name,ownerid,statecode,createdon,modifiedon,schemaname"
}
# Compare against agent register export (assumes register exported as register.csv with column 'BotId')
$register = Import-Csv .\register.csv
$bots | Where-Object { $_.botid -notin $register.BotId } | Export-Csv -NoTypeInformation .\dq3-shadow-bots.csv
```

> **Gotcha.** `Get-AdminPowerApp` returns only canvas/model-driven Power Apps and **does not** list Copilot Studio bots. The Dataverse `bot` table query above is the authoritative source.

**DQ-4 — Orphaned applications (no owner, or all owners disabled / departed).**

```powershell
$apps = Get-MgApplication -All
$apps | ForEach-Object {
  $owners = Get-MgApplicationOwner -ApplicationId $_.Id
  $live = $owners | Where-Object { $_.AdditionalProperties.accountEnabled -eq $true }
  if (-not $owners -or -not $live) {
    [pscustomobject]@{
      AppId = $_.AppId; DisplayName = $_.DisplayName
      OwnerCount = $owners.Count; LiveOwnerCount = $live.Count
      OldestOwnerSignIn = ($owners.AdditionalProperties.signInActivity.lastSignInDateTime | Sort-Object | Select-Object -First 1)
    }
  }
} | Export-Csv -NoTypeInformation .\dq4-orphaned.csv
```

**DQ-5 — Application credentials (secrets/certs) expiring in next 30 days, or already expired and still active.**

```powershell
Get-MgApplication -All | ForEach-Object {
  $a = $_
  $a.PasswordCredentials + $a.KeyCredentials | ForEach-Object {
    [pscustomobject]@{
      AppId = $a.AppId; DisplayName = $a.DisplayName
      CredType = if ($_.Type) { $_.Type } else { 'Secret' }
      KeyId = $_.KeyId; StartDateTime = $_.StartDateTime; EndDateTime = $_.EndDateTime
      DaysToExpiry = (New-TimeSpan -Start (Get-Date) -End $_.EndDateTime).Days
    }
  }
} | Where-Object { $_.DaysToExpiry -le 30 } | Sort-Object DaysToExpiry |
    Export-Csv -NoTypeInformation .\dq5-expiring-creds.csv
```

**DQ-6 — All consent grants (delegated + application) for a target appId.**

```powershell
param($AppId)
$sp = Get-MgServicePrincipal -Filter "appId eq '$AppId'"
"=== Delegated (oauth2PermissionGrants) ==="
Get-MgOauth2PermissionGrant -Filter "clientId eq '$($sp.Id)'" |
  Select-Object Id, ConsentType, PrincipalId, ResourceId, Scope
"=== Application (appRoleAssignments) ==="
Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $sp.Id |
  Select-Object Id, ResourceId, AppRoleId, CreatedDateTime
```

**DQ-7 — Purview Unified Audit Log query for application-related events for a target appId.**

```powershell
$start = (Get-Date).AddDays(-30); $end = Get-Date
Search-UnifiedAuditLog -StartDate $start -EndDate $end -ResultSize 5000 `
  -Operations 'Add application.','Update application.','Delete application.', `
              'Add service principal.','Update service principal.','Remove service principal.', `
              'Add app role assignment to service principal.','Remove app role assignment from service principal.', `
              'Add OAuth2PermissionGrant.','Update OAuth2PermissionGrant.','Remove OAuth2PermissionGrant.', `
              'Consent to application.','Add owner to application.','Remove owner from application.', `
              'Add owner to service principal.','Remove owner from service principal.' `
  -FreeText $AppId | Export-Csv -NoTypeInformation .\dq7-ual.csv
```

> **Latency note.** Purview Unified Audit Log surfaces application-plane events at typical latency of 60–90 minutes; allow up to 24 hours for full coverage in high-volume tenants.

**DQ-8 — Cross-surface reconciliation matrix (Entra ↔ Integrated Apps ↔ Dataverse `bot` ↔ Agent Register).**

```powershell
# Pseudocode — see verification-testing.md for the full implementation.
$entraApps = Get-MgApplication -All
$intApps   = Invoke-MgGraphRequest -Method GET -Uri 'https://graph.microsoft.com/v1.0/servicePrincipals?$filter=tags/any(t:t eq ''WindowsAzureActiveDirectoryIntegratedApp'')'
$bots      = <Dataverse bot rows from DQ-3>
$register  = Import-Csv .\register.csv
# Outer-join across the four sources by the canonical key (AppId where available, BotId for bot-only entries).
# Output: rows present in some sources but missing in others — these are the reconciliation backlog.
```



---

## §2. Eight Troubleshooting Pillars

Each pillar covers one registration surface (or cross-cutting governance plane). Pillars share a common structure: **What can fail · How it surfaces · Diagnostic steps · Resolution patterns · Watch-outs**. Pillar-specific failures escalate via the §1 framework if they meet a severity threshold.

### Pillar A — Entra App Registration Failures

**Scope.** All failures involving `/applications` and `/servicePrincipals` objects in Microsoft Entra ID, including credential lifecycle, owner lifecycle, redirect-URI / reply-URL configuration, certificate trust, app-manifest validation, and tenant-restriction policy interaction.

**What can fail.**

- App registration cannot be created — typically caused by Application Admin role not in PIM-active state; or the user is in a directory role group that excludes Application.ReadWrite.OwnedBy due to a custom RBAC policy.
- App is created but owner cannot be assigned — frequent with B2B guests or with on-prem-synced users that lack `User.Read` consent for the tenant.
- Federated credential cannot be added — typically a tenant policy that restricts subject identifiers, or the external IdP issuer is not on the allowlist.
- Reply URL rejected — wildcard redirects are blocked tenant-wide; HTTP (non-HTTPS) reply URLs are rejected outside `localhost`; reply URL exceeds 256 characters; the publisher domain is unverified and the app is multi-tenant.
- Application cannot sign in — the principal is disabled (`accountEnabled = false`); the secret has expired; the app is blocked by a CA workload-identity policy; the home-tenant restriction excludes the requesting tenant; the resource SP does not have a corresponding service principal in the home tenant.
- "Need admin approval" loop — admin consent workflow is misconfigured, or the requested scope is on the firm's permanent-deny list.

**How it surfaces.** Entra portal "AADSTS…" error codes; failed sign-ins in `Get-MgAuditLogSignIn`; "Insufficient privileges to complete the operation" from PowerShell; orphaned `applications/{id}` with no matching `servicePrincipals/{appId}` (or vice versa); "publisher domain unverified" warning in admin consent prompt.

**Diagnostic steps.**

1. Confirm the role context: `Get-MgContext` then `Get-MgUserMemberOf -UserId <UPN>` — verify Application Administrator or Cloud Application Administrator is **active** (not just eligible).
2. For sign-in failures, pull the full sign-in log with the correlation ID from the user's error: `Get-MgAuditLogSignIn -Filter "correlationId eq '<guid>'"`. Inspect `errorCode`, `failureReason`, `additionalDetails`.
3. For consent loops, examine `https://entra.microsoft.com/#view/Microsoft_AAD_IAM/ConsentPoliciesMenuBlade` — is the app requesting a permission on the deny list?
4. For credential issues, dump the full credential set with DQ-5; cross-check against the agent register's recorded credential rotation schedule.
5. For owner-assignment failures, confirm the proposed owner is a member (not external guest) unless the tenant explicitly allows guest owners on app registrations.

**Resolution patterns.**

- Activate the required role through PIM with a justification; record the activation in E-11.
- For reply-URL rejections, restructure to a fixed HTTPS URL on a verified publisher domain; for SPAs use the SPA platform with `responseType=code`+PKCE rather than implicit.
- For consent loops, route through the **admin consent workflow** (Entra → Enterprise applications → Consent and permissions → Admin consent settings) — not by direct grant. The reviewer chain (Cloud App Admin → Compliance reviewer → AI Governance Lead) is documented in [sponsorship-lifecycle-workflows.md](./sponsorship-lifecycle-workflows.md).
- For credential rotation, prefer **federated credentials** (workload identity federation) for any agent that runs in a workload supporting OIDC (GitHub Actions, Azure DevOps, AKS, Kubernetes, GCP). Prefer **managed identity** for any agent that runs in Azure. Reserve client secrets for the cases where neither is possible, and require automated rotation with maximum 90-day lifetime per the firm's secret-management policy.

**Watch-outs.**

- The `applications` object lives in the **home tenant**; the `servicePrincipals` object lives in **every tenant where the app has been consented**. Deleting the app registration in the home tenant does **not** automatically remove every downstream service principal — clean those up via Graph in each affected tenant.
- A **soft-deleted** application (Entra → Identity → Applications → Deleted applications) is recoverable for 30 days. Examiners may request the soft-deleted state during audit; DO NOT hard-delete during an active examination.
- "Verified publisher" status is **per Microsoft Partner Center MPN**, not per tenant. A verified-publisher app is treated more leniently by the user-consent workflow — verify your tenant's consent policy reflects this intentionally.

### Pillar B — Integrated Apps (M365 Admin) Failures

**Scope.** The Microsoft 365 admin center → Settings → Integrated apps blade, which governs apps deployed to Microsoft 365 surfaces (Outlook add-ins, Teams apps, Office add-ins, declarative agents for M365 Copilot). This blade is **distinct from** Entra Enterprise applications even though it uses the same underlying service principal.

**What can fail.**

- App deployment via Integrated Apps fails with no error in UI — typically caused by missing role (M365 Apps Admin or Teams Admin); or app is not eligible for centralized deployment (legacy COM add-ins, certain VBA-based add-ins).
- App appears deployed but does not load for users — the deployment scope (specific group) does not include the user; the user has the Office build that pre-dates centralized-deployment support; the user's Outlook is in cached mode without enough cache refreshes.
- "Get apps" search does not return the app — the publisher's listing is geo-restricted; the firm's tenant is enrolled in a delayed channel; the app is in a private store that the user has not been added to.
- Permissions consent "Accept" button is greyed out — the user is not an Entra Application Admin or Cloud Application Admin **and** the integrated app is requesting a permission that requires admin consent.
- App is deployed but the Service Principal is in a different state (disabled, hidden, wrong tags) — most often caused by the IT operator deploying via Integrated Apps **after** the SP was already created/modified directly in Entra.

**How it surfaces.** Empty deployment log; users complain the add-in does not appear in their ribbon; M365 admin center shows "Deployment in progress" indefinitely; SP appears in Enterprise Applications but with `tags` that do not include `WindowsAzureActiveDirectoryIntegratedApp`.

**Diagnostic steps.**

1. Verify the deployment in the M365 admin center → Settings → Integrated apps → *(app)* → Deployment status.
2. Cross-check the SP in Entra: `Get-MgServicePrincipal -Filter "appId eq '<appId>'"` and inspect `tags` — should include `WindowsAzureActiveDirectoryIntegratedApp` and `M365Enabled`.
3. For Teams apps, additionally check the Teams admin center → Teams apps → Manage apps.
4. For declarative agents for M365 Copilot, confirm the manifest is published to the org catalog and the assignment policy includes the user.
5. For Outlook add-ins, examine the user's `OWAMailboxPolicy` and confirm `AllowedAddinList` does not exclude the app.

**Resolution patterns.**

- Re-deploy via Integrated Apps after correcting the underlying SP state. Ordering matters: prefer Integrated Apps as the primary, and only modify the SP in Entra to add governance metadata (owner, tags, notes) — never to mutate scope or permissions.
- For unending "deployment in progress," check the **deployment job** record via Graph: `GET /admin/microsoft365Apps/installationOptions` and the related deployment beta endpoints.
- For greyed-out consent, route the user to request admin consent via the admin consent workflow.

**Watch-outs.**

- Integrated Apps deployments may take **6–24 hours** to fully propagate to all users, especially in cached-mode Outlook clients. Do **not** treat absence-after-1-hour as a failure.
- Integrated Apps records ownership at the *deployment* level, but Entra records ownership at the *service principal* level. The two ownership records can drift. The agent register must reconcile both.

### Pillar C — Power Platform / Copilot Studio Registration Failures

**Scope.** Copilot Studio agents (formerly Power Virtual Agents bots) registered in Dataverse-backed Power Platform environments, including their Entra app registrations (when published to channels other than Teams), their Dataverse `bot` and `botcomponent` rows, their connection references, and their PPAC (Power Platform Admin Center) governance metadata.

**What can fail.**

- Bot is created but does not appear in PPAC → Environments → *(env)* → Copilots — typically a PPAC propagation delay (steady-state ~15 minutes, but observed up to 60 minutes in high-tenancy regions).
- `Get-AdminPowerApp` returns canvas/model-driven apps but the Copilot Studio bot is missing — **expected**: the cmdlet does not enumerate bots. Use the Dataverse `bot` table query (DQ-3).
- `Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName <env>` returns an empty array with **no error** — this happens for Dataverse-backed environments; use the Dataverse `systemuser` and `systemuserroles_association` tables instead.
- Bot is enabled but channel publishing fails — most common with Microsoft Teams channel: missing Teams channel app registration, or the Teams admin policy blocks custom apps.
- Bot's connection reference points to a connection owned by a departed user — bot fails at runtime with "connection invalid" but the bot itself appears healthy in PPAC.
- DLP policy blocks the bot from using a connector — surfaces as "policy violation" at design time when the user adds the connector to a topic.

**How it surfaces.** PPAC shows a different bot count than Dataverse; Sentinel detection rule "shadow-bot" fires when DQ-3 finds a `bot` row not in the agent register; users report bot answers stop matching the latest published version (typically a publish job that completed in Dataverse but did not propagate to the channel).

**Diagnostic steps.**

1. Run DQ-3 to list Dataverse `bot` rows; cross-check with PPAC and the agent register.
2. For a specific bot, query: `GET /api/data/v9.2/bots({botid})?$expand=ownerid,bot_botcomponent` to capture full state including components.
3. For channel-publishing failures, examine the bot's `runtimeprovider` and `channelregistrationid` columns; pull the channel's Teams admin policy.
4. For connection-reference failures, query `connectionreference` rows and check `connectionreferencelogicalname` against the connector inventory.
5. For DLP misfires, check the environment's DLP policies and the connector's classification (Business / Non-Business / Blocked).

**Resolution patterns.**

- Wait the propagation window (15-60 min) before treating a "missing bot" as a registration failure. Do not auto-remediate during the window — that creates duplicate bots.
- For channel-publishing failures with Teams, use the Power Platform/Teams integration wizard rather than manual app-package upload, which bypasses the governance metadata recorded by the wizard.
- For connection-reference orphaning, transfer the connection ownership to the new bot owner via PPAC → Resources → Connections; record the transfer in the agent register.

**Watch-outs.**

- Copilot Studio agents do **not** always create a corresponding Entra app registration. Teams-channel-only bots use a tenant-level shared SP. Do not treat absence of a dedicated Entra app reg as a registration defect for Teams-only bots.
- The PPAC **`-Endpoint`** flag must match the cloud: `prod` (commercial), `usgov` (GCC), `usgovhigh` (GCC High), `dod` (DoD). Cross-cloud queries silently return empty results — record the endpoint used in E-14.

### Pillar D — Microsoft Graph Application API Failures

**Scope.** Programmatic interactions with the Graph `/applications`, `/servicePrincipals`, `/oauth2PermissionGrants`, `/appRoleAssignments` endpoints, plus the preview `/copilot/agents` and `/agents` endpoints.

**What can fail.**

- 403 Authorization_RequestDenied — caller lacks the required scope (Application.Read.All vs. Application.ReadWrite.All vs. Application.ReadWrite.OwnedBy).
- 404 Request_ResourceNotFound — querying `applications/{id}` with the **appId** (a GUID) instead of the **object id** (a different GUID). The two are distinct.
- Inconsistent results between v1.0 and beta — the beta surface includes properties (e.g., `requestedAccessTokenVersion`, `samlMetadataUrl` for some resource SPs) not in v1.0. Pinning the API version is mandatory; record in E-14.
- `/copilot/agents` returns 200 with empty `value` array even when bots exist — preview API gap; not all bot types are surfaced; must reconcile against Dataverse `bot`.
- Throttling (429) — large-tenant inventory queries hit Graph throttling; prefer `$select` to minimize payload, page with `$top=999`, and respect `Retry-After`.

**How it surfaces.** Inventory jobs fail; Sentinel "agent count drift" alert fires comparing two consecutive snapshots.

**Diagnostic steps.**

1. Capture the full Graph response including headers (especially `request-id`, `client-request-id`, `x-ms-ags-diagnostic`). Submit `request-id` to Microsoft Support if escalating.
2. Check Graph service health: `https://status.cloud.microsoft` for any active advisory.
3. Compare v1.0 and beta side-by-side for the same object to identify schema drift.
4. For preview endpoints, capture the API version in the URL path and confirm against the Microsoft Learn doc set as of the date the query was run.

**Resolution patterns.**

- Retry with exponential backoff on 429s; honor `Retry-After`.
- For preview endpoint gaps, do **not** rely on the preview API as the system of record. Use it as a discovery hint and reconcile against the primary surface (Entra app reg, Dataverse `bot`, Integrated Apps).

**Watch-outs.**

- Graph **delta queries** (`$delta`) for `/applications` and `/servicePrincipals` are powerful for inventory reconciliation but have a max state-token lifetime of 30 days. Schedule full reconciliations at least monthly.

### Pillar E — Agent 365 / Agent Registry Preview Gaps

**Scope.** The Microsoft Agent 365 admin center and the Agent Registry preview surfaces. Both are in active preview as of the document's "Last UI Verified" date — features, endpoints, and UI surfaces are subject to change.

**What can fail.**

- Agent appears in one preview surface but not another — surfaces sync at different cadences and from different upstream stores.
- Counts shown in the preview admin center diverge from Entra + Dataverse + Integrated Apps reconciliation by a small percentage — under investigation with Microsoft as of writing.
- Preview UI does not yet expose Sponsor / Backup-Owner / Operator-Context fields — must capture these in the firm agent register; do not rely on the preview UI alone.

**How it surfaces.** Manual reconciliation flag in monthly attestation.

**Diagnostic steps.** Document divergence with screenshot + timestamp; raise a Microsoft Support case referencing the preview SKU.

**Resolution patterns.** Use the firm's agent register as the **system of record** during preview. Treat preview surfaces as **decoration** until GA.

**Watch-outs.** Preview surfaces may be deprecated or rebranded with little notice. Pin the date and version of any screenshot.

### Pillar F — Defender for Cloud Apps OAuth Governance Failures

**Scope.** Defender for Cloud Apps OAuth app discovery, OAuth app policies, and the OAuth app investigation experience.

**What can fail.**

- OAuth app discovery feed has gaps — typically caused by an IdP-side connector (e.g., between Defender for Cloud Apps and Entra) being misconfigured or in degraded state.
- OAuth app policy fails to auto-revoke a flagged grant — common cause is the policy's `Action` set to `Notify` only; or the SP has been excluded by a stale exclusion rule.
- A new high-risk OAuth app is consented but does not appear in the OAuth apps list for several hours — known indexing latency; document in E-13.

**How it surfaces.** Defender alerts for "unusual OAuth app behavior" with no preceding discovery; OAuth app stays in "Allowed" state after policy should have revoked.

**Diagnostic steps.**

1. Confirm the Defender for Cloud Apps connector to Entra ID is healthy: portal → Settings → Cloud apps → App connectors → Microsoft 365 → Status = Connected, last sync recent.
2. Inspect the OAuth app policy's run history: portal → Cloud apps → OAuth apps → Policies → *(policy)* → Reports.
3. For revocation failures, check whether the SP is on a tenant-level exclusion or a CA workload-identity exclusion.

**Resolution patterns.** Move policy `Action` to `Revoke app` for any matching high-risk scope set; review and prune exclusion lists quarterly; pair Defender for Cloud Apps OAuth governance with a CA workload-identity policy as defense-in-depth.

**Watch-outs.** Defender for Cloud Apps OAuth governance is most effective when **paired** with the Entra admin-consent workflow and CA workload-identity policies. Single-control reliance creates gaps.

### Pillar G — Conditional Access Workload-Identity Policy Failures

**Scope.** CA policies targeting **workload identities** (service principals and managed identities) — distinct from CA policies targeting users.

**What can fail.**

- Policy does not apply — workload-identity CA requires Workload Identities Premium licensing; policy silently does nothing if licensing is missing.
- Policy applies but blocks a legitimate first-party Microsoft service principal — typically because the policy targets "All workload identities" and excludes the wrong assignment.
- Policy in report-only mode forever — common operational issue, with the team forgetting to flip to enforced mode.
- Service principal sign-in succeeds despite policy — policy may be evaluated only on certain authentication flows (typically client-credentials and federated identity); user-impersonation flows are evaluated under user-targeted CA.

**How it surfaces.** Sign-in failures for legitimate workloads; or, conversely, expected blocks not occurring.

**Diagnostic steps.**

1. Confirm Workload Identities Premium SKU in Entra → Identity → Licenses.
2. Inspect the sign-in log for the SP: `Get-MgAuditLogSignIn -Filter "appId eq '<appId>' and signInEventTypes/any(t:t eq 'servicePrincipal')"`. Look at `appliedConditionalAccessPolicies`.
3. For "policy did not apply," check the policy's assignments — the SP must be in the included set and not in the excluded set.

**Resolution patterns.** Use the **What If** tool in Entra → Conditional Access → What If, in Workload Identity mode. Pilot with a small set of low-risk SPs in report-only before enforced.

**Watch-outs.** Workload-identity CA policies cannot evaluate device, location for some legacy authentication flows, or MFA — they evaluate **named locations**, **risk**, and **filter for applications**. Plan policy logic accordingly.

### Pillar H — Sovereign-Cloud / Per-Tenant Feature Gaps

**Scope.** Feature parity gaps between commercial, GCC, GCC High, and DoD; tenant-specific opt-in features; preview features that are GA in commercial but absent or preview in sovereign clouds.

**What can fail.**

- A control documented for commercial does not exist in GCC High (e.g., a specific Defender for Cloud Apps OAuth-app policy template).
- Endpoint URL differs — commercial `graph.microsoft.com`, GCC High `graph.microsoft.us`, DoD `dod-graph.microsoft.us`. PowerShell scripts that hardcode `graph.microsoft.com` fail silently in sovereign tenants.
- A feature is enabled by tenant flag in commercial but requires Microsoft Support ticket in sovereign clouds.

**How it surfaces.** Cross-cloud reconciliation fails; PowerShell scripts return empty results; Microsoft Learn documentation page warns of sovereign-cloud differences in a callout.

**Diagnostic steps.**

1. Confirm the cloud: Entra → Properties → "Tenant ID" page shows tenant region and cloud.
2. Pin endpoints in scripts via `Connect-MgGraph -Environment USGovHigh` / `-Environment USGovDoD`; for PPAC, use `Add-PowerAppsAccount -Endpoint usgovhigh` / `dod`.
3. For each control in GCC High / DoD, check the Microsoft Learn "Service description for US Government" or equivalent page.

**Resolution patterns.** Maintain a per-cloud control matrix in the agent register; deploy compensating controls (per §1.5) where features lag.

**Watch-outs.** GCC High and DoD have **separate tenant boundaries**; cross-cloud sign-in is not possible. A user in DoD cannot administer a commercial-tenant agent. Plan for cleared-personnel staffing in advance of any cross-cloud incident.

---

## §3. Failure-Mode Runbooks (Detailed)

Each runbook follows the same eight-section structure: **Severity classification · Triggers and detection · Immediate actions (first 60 minutes) · Investigation · Containment · Eradication · Recovery · Lessons-learned & reporting decision tree**. Severities default per §1.1 and may be bumped per §1.2.

### Runbook 1 — Shadow Agent Discovered (Unregistered Production Agent)

**Severity classification.** Default **SEV-2**; bump to **SEV-1** if any of: high-privilege grant (any application-permission scope, `*.ReadWrite.All`, `Directory.*`, Mail.* with read or write), customer-facing surface, NPI/MNPI access, books-and-records touch, or active examination.

**Triggers and detection.**
- DQ-3 (Dataverse `bot` rows) returns a botid not present in the agent register.
- DQ-1 (recent app registrations) shows an appId without a register entry within 7 days of `createdDateTime`.
- Defender for Cloud Apps OAuth app discovery flags an app with consents from ≥5 users and the app is not in the register.
- Purview DSPM for AI Activity Explorer surfaces traffic from an unknown principal.

**Immediate actions (first 60 minutes).**
1. Open incident record; classify per §1.1; apply §1.2 bumps; document operator-context (E-13).
2. Capture E-01, E-02, E-03 (if applicable), E-04 (if Copilot Studio bot), E-05, E-12 — **before** any state change. Reconstruction without evidence is not possible.
3. Identify the de-facto operator (the user(s) who consented or who is invoking the agent). Do **not** suspend their accounts unilaterally — engage HR partner before any user-facing action.
4. Identify any second-party (the publisher / developer / vendor). If third-party, engage TPRM lead immediately.
5. Notify L1 then L2 per §1.7 within 15 minutes.

**Investigation.**
- Reconstruct the consent chain: who clicked "Accept," when, from what device, and via what consent surface (admin consent workflow vs. user consent vs. on-behalf-of). DQ-7 isolates the relevant Purview audit events.
- Quantify blast radius: distinct users who consented, distinct mailboxes / sites / drives / Teams accessed, distinct messages sent. Use DQ-6 to enumerate grants and DQ-2 to characterize their privilege level.
- Determine business need: is this a sanctioned-but-unregistered tool (process gap), a developer experiment, or a malicious / misconfigured app?

**Containment.**
- Disable the SP (`Update-MgServicePrincipal -AccountEnabled:$false`) — fastest blunt instrument.
- Or revoke specific high-risk grants (DQ-6 → `Remove-MgOauth2PermissionGrant` / `Remove-MgServicePrincipalAppRoleAssignment`).
- Or add the appId to a CA workload-identity block policy — preferred when the SP must remain enabled for a legitimate sub-function while the high-risk surface is blocked.
- For Copilot Studio bots, set `statecode = 1` (Disabled) on the `bot` row via `Invoke-DataverseRequest`.

**Eradication.** If unsanctioned: revoke all grants; delete the SP and the application object (after preservation hold consideration); remove Integrated Apps deployment; delete Dataverse `bot` and orphaned `botcomponent` rows. If sanctioned-but-unregistered: register through the standard sponsorship workflow; do **not** simply "back-fill" the register without Sponsor sign-off and scope re-approval.

**Recovery.** Restore advisor / user productivity by deploying the sanctioned replacement (or by re-enabling the now-registered original under properly scoped grants). Document a 30-day heightened-monitoring period via Sentinel.

**Lessons-learned & reporting decision tree.** Walk Q1–Q10. Common "yes" answers for shadow-agent incidents: Q1 (3110 supervision), Q4 (Notice 25-07), Q5 (Reg S-P) if NPI accessed. Hold post-mortem within 14 days; root-cause typically lands on (a) user-consent permitted for a scope class that should require admin consent, (b) discovery cadence too slow, (c) agent-register intake friction encouraging shadow IT.

### Runbook 2 — Mass Departed-Owner Cascade (>50 Apps)

**Severity classification.** Default **SEV-2**; bump to **SEV-1** if the cascade includes any high-privilege apps with NPI/MNPI scope or a critical-tier agent.

**Triggers and detection.** Quarterly attestation discovers ≥50 apps where all owners are `accountEnabled = false` or have `employeeLeaveDateTime` in the past. Often correlated with a business reorganization, a divestiture, or an RIF.

**Immediate actions.**
1. Capture DQ-4 (orphaned applications) results as E-06 and E-10 baseline.
2. Bucket the orphaned apps by criticality tier (critical / high / medium / low) per the agent register.
3. Notify L2 immediately; this is rarely a security event by itself but creates large attack surface.
4. Engage HR for the master leaver list and any pending-leaver list.

**Investigation.** Determine cause: divestiture (some apps may belong to the divested entity and should be transferred, not re-owned), mass departure (RIF), or accumulated drift. Determine which sponsors are also affected (sponsor cascade compounds the issue).

**Containment.**
- For critical-tier orphans with high-privilege scopes: assign the **Sponsor** as temporary owner (or, if Sponsor is also gone, the BU's COO / equivalent). Do **not** assign a shared mailbox or non-human identity as owner — that defeats accountability.
- Apply a CA workload-identity policy that requires the SP's sign-ins to come only from approved network locations until permanent ownership is restored.

**Eradication.** Re-attest each app: identify new permanent owner + backup owner per the firm's two-deep ownership rule; route through the Sponsor for re-attestation; record both owners in the agent register and the Entra app owner list (`Add-MgApplicationOwner` and `Add-MgServicePrincipalOwner` — both are required). Delete apps that are no longer needed per business-unit confirmation.

**Recovery.** Update the agent register with all new ownership; set the next attestation date; instrument a Sentinel rule that fires when any app's owner-set drops to zero live owners.

**Lessons-learned & reporting decision tree.** Q8 (SR 11-7) often "yes" if any of the orphaned apps are MRM-scope models that lapsed governance. Q9 (TPRM) if any divested entity's apps remain co-mingled. Q4 (Notice 25-07) if customer-facing apps are involved. Add a leaver-process control: HR's leaver workflow should fire a Graph webhook into the agent register to trigger pre-departure ownership transfer.

### Runbook 3 — Over-Permissioned Grant Exploited

**Severity classification.** **SEV-1** by default. Exploitation of an over-permissioned grant means an actor used scope that exceeds the agent's minimum-necessary permission set, by definition affecting confidentiality and likely integrity.

**Triggers and detection.** Defender for Cloud Apps anomaly alert ("unusual data download by application," "mass mailbox access by app"); Purview DSPM for AI flags an unusual sensitivity-label distribution from an application principal; Sentinel detection on Graph `applicationActivity` showing access patterns inconsistent with the agent's stated function.

**Immediate actions.**
1. Bridge open within 15 minutes; CISO + GC + Compliance on bridge within 30.
2. Capture E-01..E-15. Pay particular attention to E-07 (Purview audit) and E-12 (sign-in logs) — these are the primary forensic anchors.
3. Containment by **revoking the specific grant**, not by disabling the SP wholesale (preserves forensic state on the SP and avoids tipping off in an internal-actor scenario).

**Investigation.** Reconstruct: (a) when the grant was added (DQ-7 will surface "Add app role assignment to service principal." or "Add OAuth2PermissionGrant."); (b) by whom (the `UserId` field in the audit event); (c) under what privilege state (E-11 PIM activations); (d) what data the grant was used to access (Purview DSPM, Defender for Cloud Apps); (e) whether the grant was used outside business hours, from anomalous geographies, or from anomalous client apps.

**Containment.** Revoke grant; rotate any credentials the SP holds; add the SP to a CA workload-identity policy enforcing strict named-location and risk-based gating.

**Eradication.** Replace over-permissioned grant with a least-privilege equivalent (often achievable by switching from application permission to delegated permission, or by switching from `*.ReadWrite.All` to a resource-specific consent scope). Where the over-grant came from a developer mistake, add a CI/CD scan for permission-set deltas.

**Recovery.** Heightened monitoring 90 days; review all other apps owned by the same owner / sponsored by the same sponsor for similar over-grants.

**Lessons-learned & reporting decision tree.** Almost always Q5 (Reg S-P, GLBA) if NPI; Q6 (8-K Item 1.05 materiality assessment) for SEC registrants; Q7 (NYDFS 72-hour) for covered entities; Q4 (Notice 25-07). Insurance notification typically required.

### Runbook 4 — Expired Secret Used in Production

**Severity classification.** **SEV-2** if the agent has failed-closed and queued workload exists; **SEV-3** if no production impact; **SEV-1** if the expired secret was somehow accepted (which would indicate a serious Entra-side bug — escalate to Microsoft).

**Triggers and detection.** DQ-5 returns secrets with `EndDateTime < now`; agent-side error logs show 401 invalid_client; ticket from the agent's owner.

**Immediate actions.** Capture the expired secret's full lifecycle from E-01 + E-07 (creation event, any rotations, the use that failed). Confirm with the owner whether the secret was migrated to a federated credential or managed identity (often the rotation was done but the agent code was not updated).

**Investigation.** Determine why the rotation did not occur: was the secret in the rotation-tracking system? Did notifications fire? Was there an owner-change that lost continuity?

**Containment.** Issue a short-lived (24-72h) replacement; commit to migration to federated credential or managed identity within 30 days.

**Eradication.** Migrate; remove all legacy secrets; instrument the agent register's secret-tracker to fire 60/30/14/7-day expiry warnings.

**Recovery.** Heightened secret-rotation monitoring for the affected BU for 6 months.

**Lessons-learned & reporting decision tree.** Usually internal only. Rare regulator implications unless the failure cascaded into a books-and-records gap (Q2) or a customer impact (Q4, Q5).

### Runbook 5 — Admin Consent Workflow Tampering

**Severity classification.** **SEV-1** by default. Tampering with the admin consent workflow undermines the firm's primary control against shadow consent and over-permissioning.

**Triggers and detection.** Audit log shows "Update consent settings" or "Update admin consent request policy" by an unexpected actor; the reviewer pool was modified to include / exclude users without an approved change ticket; the workflow was disabled.

**Immediate actions.** Bridge with CISO + GC + Compliance immediately. Treat as potential insider-threat case — engage HR and Insider Threat program lead.

**Investigation.** DQ-7 with the specific operations above; PIM activation log (E-11) for any role that could have made the change (Cloud App Admin, Privileged Role Admin, Global Admin); user behavior analytics for the actor.

**Containment.** Restore the prior workflow configuration; place the actor's account under heightened monitoring (do **not** suspend without HR coordination unless physical/cyber emergency); review any consents granted during the tampering window.

**Eradication.** Re-validate every consent granted during the tampering window; revoke any consents that would not have been approved under the proper workflow.

**Recovery.** Add a Conditional Access break-glass alert specifically for changes to the admin-consent-workflow configuration; require step-up authentication (Control 1.23) for all changes to consent-related settings.

**Lessons-learned & reporting decision tree.** Q1, Q4, Q7 (NYDFS — tampering is itself a cybersecurity event); Q5 if downstream consents accessed NPI; Q6 materiality assessment for SEC registrants.

### Runbook 6 — CA Workload-Identity Policy Misfire

**Severity classification.** **SEV-2** for over-blocking (productivity impact); **SEV-1** for under-blocking that allowed a high-risk sign-in.

**Triggers and detection.** Sudden spike in 530001 / 530002 sign-in errors for service principals; conversely, an SP that should be blocked is signing in successfully.

**Immediate actions.** Identify the policy(ies) involved via the sign-in log's `appliedConditionalAccessPolicies`. Capture the policy state (export JSON via Graph). Use the **What If** tool to model expected vs. observed.

**Investigation.** Was the policy changed recently? By whom (E-11)? Was the licensing for Workload Identities Premium intact? Did an exclusion list grow improperly?

**Containment.** For over-blocking, place the policy in report-only mode while the affected SPs are properly excluded or the policy logic is corrected. For under-blocking, immediately add a temporary deny policy targeting the specific appId(s).

**Eradication.** Restore correct policy state; add automated tests (PowerShell + What If) to the change-management pipeline for CA policies.

**Recovery.** Re-enable enforcement; communicate to affected app owners.

**Lessons-learned & reporting decision tree.** Internal usually; if under-blocking allowed a successful unauthorized sign-in to NPI/MNPI scope, walk Q5/Q6/Q7.

### Runbook 7 — Sponsor / Owner Attestation Lapse

**Severity classification.** **SEV-3** for first-time minor lapse; **SEV-2** if recurring or covering critical-tier agents; **SEV-1** if combined with another defect (e.g., over-grant + lapsed attestation).

**Triggers and detection.** Quarterly attestation report identifies agents with attestation overdue >30 days.

**Immediate actions.** Notify Sponsor with a 14-day cure window; freeze any in-flight scope changes for the affected agents; record the lapse in the agent register.

**Investigation.** Why did the lapse occur? Sponsor on extended leave? Sponsor departed? Process not surfacing in Sponsor's queue?

**Containment.** If cure window expires, **freeze** the agent (block sign-in / set bot statecode = 1) until attestation is completed.

**Eradication.** Complete the attestation; if Sponsor unable, designate replacement Sponsor.

**Recovery.** Add the lapse to the BU's quarterly governance scorecard.

**Lessons-learned & reporting decision tree.** Internal; Q8 if the lapsed agent is an MRM-scope model.

### Runbook 8 — Cross-Cloud Sovereign Boundary Breach

**Severity classification.** **SEV-1** always.

**Triggers and detection.** A registration object, credential, or grant from one sovereign cloud appears in or affects another (e.g., a GCC High service principal somehow granted access to a commercial-tenant resource). Almost always indicates a misconfiguration of multi-tenant app, a federated credential pointing across clouds, or — most seriously — a credential exfiltration with cross-cloud reuse.

**Immediate actions.** Engage cleared personnel pool (the responders authorized to act in the affected sovereign cloud). Capture evidence in **both** clouds — and remember E-15 hashes must be generated from the cleared workstation for the cleared cloud's evidence.

**Investigation.** Reconstruct the cross-cloud path. Determine whether sovereign data left the sovereign boundary (this is the dispositive question). Engage Microsoft Support FastTrack / sovereign-cloud support immediately.

**Containment.** Block the offending principal at both ends (CA workload-identity policies in both clouds); revoke all credentials; preserve in-place — do not delete during the investigation.

**Eradication.** Remove the cross-cloud configuration; re-architect to avoid cross-cloud trust.

**Recovery.** Independent third-party assessment; report to ATO authority for the sovereign environment.

**Lessons-learned & reporting decision tree.** Q5, Q6, Q7 always to be assessed; agency-specific reporting per the sovereign environment's authorization (e.g., FedRAMP incident reporting to the Joint Authorization Board / Agency PMO).

### Runbook 9 — Examiner Audit Pull (FINRA / OCC / Fed Snapshot)

**Severity classification.** Not a security incident; treated as a **regulatory operations** workflow with a strict deadline (typically 5–10 business days for the initial production).

**Triggers and detection.** Examiner request letter (FINRA, SEC, OCC, Fed, NYDFS, CFTC/NFA, state regulator) includes language such as "all AI agents," "all bots," "all Copilot agents," "all OAuth applications," or specific named agents. Often paired with a request for the firm's WSPs governing AI.

**Immediate actions (driven by the request deadline, not minutes-to-incident).**
1. Engage Legal, Compliance, and Regulatory Reporting; confirm document-preservation hold scope is sufficient.
2. Confirm whether the request is **production** (full document delivery) vs. **interview / walkthrough** (demonstration with screen-share and narration).
3. Capture the **as-of date** for the snapshot — the examiner expects a frozen-in-time view, not a live system.

**Investigation / preparation.**
- Run DQ-1 through DQ-8 with the as-of date; commit each output to the evidence store with E-15 hashes.
- Generate the agent register snapshot, the cross-surface reconciliation, and the attestation history for each agent in scope.
- Prepare the WSPs and the change-management history for the WSPs themselves.

**"Containment" (production hygiene).** No system changes during the production window other than those required by ongoing operations; document any changes.

**Eradication / recovery.** Not applicable — this is not an incident.

**Lessons-learned & reporting decision tree.** Walk every Q1–Q10 question with Compliance for each agent in scope. Use the examiner pull as a test of the controls' production-readiness; record gaps for remediation.

---

## §4. Common Symptom → Cause → Resolution Index

| Symptom | Likely cause(s) | First-line resolution | Pillar / Runbook |
|---------|-----------------|----------------------|------------------|
| Bot exists in Dataverse but not in PPAC | Propagation lag (15-60 min) | Wait window; do not auto-remediate | Pillar C |
| `Get-AdminPowerApp` empty for a Copilot Studio bot | Cmdlet does not enumerate bots | Use Dataverse `bot` table query (DQ-3) | Pillar C |
| `Get-AdminPowerAppEnvironmentRoleAssignment` returns empty array | Dataverse-backed environments do not return via this cmdlet | Query Dataverse `systemuserroles_association` | Pillar C |
| AADSTS50034 / 700016 on consent | Wrong tenant; multi-tenant app misconfigured | Verify `signInAudience` and tenant id | Pillar A |
| AADSTS7000215 invalid client secret | Expired or rotated secret | DQ-5; rotate or migrate to federated credential | Pillar A / Runbook 4 |
| AADSTS650056 misconfigured app | Reply URL mismatch or platform misconfigured | Re-register reply URLs; verify platform type | Pillar A |
| AADSTS530001 / 530002 (CA block) | CA workload-identity policy denies sign-in | Use What If; review excludes; report-only test | Pillar G / Runbook 6 |
| App appears in Enterprise Apps without `WindowsAzureActiveDirectoryIntegratedApp` tag | Created directly in Entra; not via Integrated Apps | Re-deploy via Integrated Apps; reconcile metadata | Pillar B |
| Defender for Cloud Apps OAuth policy did not auto-revoke | Action set to Notify; or exclusion in place | Switch action to Revoke; prune exclusions | Pillar F |
| Graph 403 Authorization_RequestDenied | Missing scope or non-active role | Re-consent scope; activate role via PIM | Pillar D |
| Graph 404 on `applications/{id}` | Used `appId` instead of object id | Use `Get-MgApplication -Filter "appId eq '<guid>'"` | Pillar D |
| Inventory query returns different counts on consecutive runs | Throttling, paging mid-mutation, or preview-API gap | Use stable inventory window; reconcile against Dataverse | Pillar D / E |
| Cross-cloud query silently returns empty | Wrong `-Endpoint` or `-Environment` flag | Pin endpoint per cloud; record in E-14 | Pillar H / Runbook 8 |
| Agent register and Entra disagree on owner | Owner change in one surface not propagated to the other | Manual reconciliation; add to attestation checklist | Pillar A / Runbook 2 |
| User cannot accept consent prompt (greyed out) | Admin-consent-required scope | Route via admin consent workflow | Pillar A |

## §5. Tooling, Endpoints, and Module Versions

Pin and record every tool version in E-14. Versions current as of the document's "Last UI Verified" date — update when verifying.

| Tool / Module | Minimum version | Notes |
|---------------|-----------------|-------|
| `Microsoft.Graph` PowerShell SDK | 2.20.0+ | Use `-Environment USGov` / `USGovHigh` / `USGovDoD` for sovereign clouds. |
| `Microsoft.PowerApps.Administration.PowerShell` | 2.0.180+ | Use `Add-PowerAppsAccount -Endpoint prod\|usgov\|usgovhigh\|dod`. |
| `ExchangeOnlineManagement` | 3.4.0+ | Required for `Search-UnifiedAuditLog`. |
| Azure CLI | 2.55.0+ | For workload identity federation administration. |
| Microsoft Graph endpoints | `graph.microsoft.com` (commercial); `graph.microsoft.us` (GCC + GCC High); `dod-graph.microsoft.us` (DoD) | Hardcoded URLs in scripts must be cloud-aware. |
| Defender for Cloud Apps portal | `https://security.microsoft.com/cloudapps` (commercial) | Sovereign cloud equivalents differ; verify per tenant. |
| Purview portal | `https://purview.microsoft.com` (commercial); `purview.microsoft.us` (GCC High) | DSPM for AI availability varies. |

## §6. Known Issues, Preview Caveats, and Documented Gaps

- **Agent 365 admin center** is in preview; counts and surfaces may diverge from Entra + Dataverse + Integrated Apps reconciliation. Use the firm's agent register as the system of record.
- **`/copilot/agents` and `/agents` Graph endpoints** are preview; not all bot types are surfaced. Reconcile against Dataverse `bot`.
- **PPAC propagation** for Copilot Studio bots is steady-state ~15 minutes; observed up to 60 minutes in high-tenancy regions. Do not auto-remediate within this window.
- **Purview Unified Audit Log** application-plane events surface at 60–90 minutes typical latency; allow 24 hours for full coverage.
- **Defender for Cloud Apps OAuth app** indexing latency for new high-risk apps can be several hours. Pair with Entra admin consent workflow for primary control.
- **Workload Identities Premium** licensing is required for workload-identity CA policies; without it, policies silently do nothing.
- **Sovereign-cloud feature parity**: GCC High and DoD lag commercial in Defender for Cloud Apps OAuth-app templates, some Purview DSPM for AI features, and several preview Graph endpoints. Maintain a per-cloud control matrix.
- **`signInActivity` on application objects** is populated only for service principals that have signed in within the last 30 days; a `null` value is not proof of inactivity.

## §7. Escalation Contacts and Vendor Support

- **Microsoft Support** — open premier / unified support case via the Microsoft 365 admin center for tenant-affecting issues; for sovereign clouds, use the cleared-personnel support channel.
- **Microsoft Defender for Cloud Apps** — for OAuth governance failures, capture the OAuth app's `oauthAppId` and the policy's `policyId` and submit via the Defender portal "Need help" link.
- **FastTrack** — for sovereign-cloud feature gaps with documented commercial parity, FastTrack engagement may surface the timeline for parity.
- **Internal contacts** — populate per firm: AI Governance Lead, CISO duty officer, Compliance duty officer, GC duty officer, HR partner, TPRM lead, External Counsel, Cyber Insurance broker, Forensics retainer firm.

## §8. Cross-References

- [`./portal-walkthrough.md`](./portal-walkthrough.md) — first-time portal configuration for the seven Control 1.2 registration surfaces.
- [`./powershell-setup.md`](./powershell-setup.md) — automation scripts for registration, attestation, and reconciliation.
- [`./verification-testing.md`](./verification-testing.md) — test cases, evidence collection scripts, and the cross-surface reconciliation matrix referenced in DQ-8.
- [`./sponsorship-lifecycle-workflows.md`](./sponsorship-lifecycle-workflows.md) — the Sponsor / Owner / Backup Owner attestation workflow referenced in §1.5, Runbook 2, Runbook 7.
- [`../../incident-and-risk/ai-incident-response-playbook.md`](../../incident-and-risk/ai-incident-response-playbook.md) — overarching AI incident response playbook; the §1 framework here is the registration-plane specialization.
- [`../1.6/troubleshooting.md`](../1.6/troubleshooting.md) — Control 1.6 (Purview DSPM for AI) playbook; canonical FSI Incident Handling framing source.
- [`../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — Control 1.7 audit logging; the source of E-07 Purview audit evidence.
- [`../1.19/`](../1.19/) — Control 1.19 (managed identity / federated credential lifecycle); referenced in Runbook 4.
- [`../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md`](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) — step-up auth required for high-risk consent-workflow changes (Runbook 5).
- [`../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md`](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) — AI-SPM detection signals that feed Pillar F and Runbook 3.
- [`../2.1/`](../2.1/) — Control 2.1 (data classification & sensitivity labels); the source of the sensitivity-label inventory in E-09.
- [`../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — Control 3.1 inventory plane; gold-standard structural reference for this troubleshooting playbook.
- [`../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md`](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — Control 3.4 incident reporting & RCA; downstream consumer of the post-mortem outputs from §3 runbooks.
- [`../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — Control 3.6 orphaned-agent detection; downstream consumer of DQ-4.

---
*Updated: April 2026 | Version: v1.4.0 | Maintained by: AI Governance Team*



