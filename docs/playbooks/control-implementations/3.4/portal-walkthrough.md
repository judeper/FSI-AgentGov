# Portal Walkthrough — Control 3.4: Incident Reporting and Root Cause Analysis

!!! danger "READ FIRST — Scope, Sibling Routing, and Non-Substitution"
    This walkthrough is the **portal-first operating manual** for Control 3.4 — the central regulator-notification clock orchestrator for AI-agent-related cyber and operational incidents in a US Financial Services Institution (FSI). It connects detection and triage in **Microsoft Defender XDR** and **Microsoft Sentinel** to investigation in **Microsoft Purview Insider Risk Management** and **eDiscovery (Premium)**, supervisory escalation in **Communication Compliance**, evidence and case management in **SharePoint**, time-bound notification choreography in **Power Automate**, and the firm's external regulator-notification matrix.

    **In scope (this file)**

    | Topic | Where it lives |
    |-------|----------------|
    | Defender XDR Unified Incidents queue, severity rubric, MITRE ATT&CK + ATLAS tagging | §2 |
    | Microsoft Sentinel Incidents and SOAR (Logic Apps) playbook wiring | §3 |
    | Purview Insider Risk Management — Cases (pseudonymized review, AI-agent-misuse templates) | §4 |
    | Purview eDiscovery (Premium) — legal holds, custodian notices, regulator-production export | §5 |
    | Purview Communication Compliance — Copilot-generated content supervisory escalation | §6 |
    | Microsoft 365 Service Health — Microsoft-side correlation **before** firm-side root-cause declaration | §7 |
    | SharePoint IR list — case fields, regulator notification matrix, legal-hold-aware site | §8 |
    | Power Automate notification flows — per-regulator timer countdowns, Teams adaptive cards | §9 |
    | Materiality determination workflow (SEC Form 8-K Item 1.05) | §10 |
    | OFAC sanctions screening for ransom payments | §11 |
    | Tabletop exercise harness (quarterly AI-specific scenarios) | §12 |
    | Regulator portal references (NYDFS, EDGAR, FINRA Firm Gateway, FTC, CISA, state AGs) | §13 |
    | Sovereign-cloud parity admonition and compensating manual register / matrix | §1, §14 |

    **Out of scope — routed to siblings**

    | Topic | Route to |
    |-------|----------|
    | PowerShell automation, KQL hunting bundles, Graph notification stubs | [powershell-setup.md](./powershell-setup.md) |
    | Verification queries, KPI definitions, examiner test scripts | [verification-testing.md](./verification-testing.md) |
    | UI anomalies, connector throttling, stale-state diagnostics | [troubleshooting.md](./troubleshooting.md) |
    | Sentinel data-connector configuration and ingestion baselining | [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) |
    | Insider risk policy authoring (upstream of cases) | [Control 1.12 — Insider Risk Detection and Response](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md) |
    | Supervisory review program (FINRA Rule 3110) | [Control 2.12 — Supervision and Oversight](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |
    | Audit-log retention and books-and-records | [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) |

    If the task at hand is **not** a portal-driven incident-management or regulator-notification action, stop and follow the routing above before continuing.

!!! warning "Non-Substitution"
    The Microsoft 365 tooling described in this walkthrough **supports** detection, triage, evidence preservation, and notification choreography. It does **not** replace any of the following firm-owned obligations:

    - The **written incident-response program** required by NYDFS 23 NYCRR 500.16, the SEC Reg S-P 2024 amendments at 17 CFR §248.30(a)(3), the FTC Safeguards Rule at 16 CFR 314.4(h), and the FFIEC IT Handbook (Information Security and Business Continuity Management booklets).
    - **Supervisory review** under FINRA Rule 3110 — see [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md). Defender / Sentinel alerts about Copilot-generated content do not substitute for registered-principal review by a Series 24 / 9 / 10 / 26 / 51 / 53 principal as applicable.
    - **Legal hold and litigation preservation** — issued and revoked by the General Counsel or designee through Purview eDiscovery (Premium); automated holds described in §5 are operational support, not legal sufficiency.
    - **Regulator notification filings** — NYDFS Cybersecurity Portal, SEC EDGAR Form 8-K, FINRA Firm Gateway 4530, FTC online breach form, CISA portal (when CIRCIA effective), and state-attorney-general portals are filed by **named human filers** in Compliance, Legal, or the Privacy Office. Power Automate countdown timers (§9) **inform** filers — they do not file.
    - **Books-and-records retention** required by SEC Rule 17a-3, 17a-4, and FINRA Rule 4511 — see [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

    Hedged language is used throughout this document — phrasing such as "supports", "helps meet", "aids in", and "required for" — to reinforce that final regulatory determinations rest with the firm's CCO, General Counsel, and named filers, not with Microsoft tooling.

!!! warning "Sovereign Cloud Availability (GCC / GCC High / DoD)"
    Several capabilities described in this walkthrough are **not at parity** in sovereign clouds at time of writing. Confirm against the Microsoft 365 sovereign roadmap and your tenant's release notes **before** each control execution.

    | Capability | Commercial | GCC | GCC High | DoD | Compensating control |
    |------------|------------|-----|----------|-----|----------------------|
    | Defender XDR Unified Incidents (cross-workload correlation) | GA | GA (parity may lag 30–90 days) | Limited | Limited | §1 manual incident register |
    | Microsoft Sentinel SOAR (Logic Apps) playbooks | GA | GA | GA (subset of connectors) | GA (subset of connectors) | §1 manual notification matrix |
    | Purview Insider Risk Management — Cases | GA | GA | Limited / staged | Not available | §1 manual case log |
    | Purview eDiscovery (Premium) | GA | GA | Available | Available | None — verify SKU |
    | Purview Communication Compliance (Copilot scope) | GA | GA | Limited | Not available | Manual supervisor sampling per Control 2.12 |
    | Power Automate premium connectors (Teams adaptive card, ServiceNow) | GA | GA | Subset | Subset | Email + manual ticket flow |

    Sovereign tenants execute the **Manual Incident Register and Manual Notification Matrix** in §1 as the **primary** evidence artifact for Control 3.4 until parity is confirmed. The portal sections below remain available to the extent the underlying capability is GA in your cloud.

!!! tip "Portal Navigation May Shift"
    Microsoft regularly updates portal blade names and navigation. Where this walkthrough cites a path such as **Defender XDR → Investigation & response → Incidents**, treat the path as descriptive, not authoritative. If a blade has moved, anchor on the **page title** and any documented telemetry node IDs rather than the breadcrumb. Capture the new path in [troubleshooting.md](./troubleshooting.md) so it can be promoted into the next revision.

## Document Map

| § | Section | Primary surface | Verification criterion |
|---|---------|-----------------|------------------------|
| 0 | Pre-flight prerequisites and triage | All portals | VC-1 (roles, licenses, scope) |
| 1 | Sovereign-cloud variant — manual incident register and notification matrix | Manual worksheet | VC-2 |
| 2 | Defender XDR Unified Incidents — triage, severity rubric, MITRE ATT&CK + ATLAS tagging | security.microsoft.com → Investigation & response → Incidents | VC-3 |
| 3 | Microsoft Sentinel — Incidents and SOAR (Logic Apps) playbooks | Azure portal → Sentinel workspace → Incidents | VC-4 |
| 4 | Purview Insider Risk Management — Cases | purview.microsoft.com → Insider risk management → Cases | VC-5 |
| 5 | Purview eDiscovery (Premium) — legal hold and regulator-production export | purview.microsoft.com → eDiscovery → Premium | VC-6 |
| 6 | Purview Communication Compliance — Copilot supervisory escalation | purview.microsoft.com → Communication compliance | VC-7 |
| 7 | Microsoft 365 Service Health — Microsoft-side correlation gate | admin.microsoft.com → Health → Service health | VC-8 |
| 8 | SharePoint IR list — case fields, notification matrix, legal-hold site | SharePoint admin center + IR site | VC-9 |
| 9 | Power Automate — notification flows, per-regulator timers, Teams adaptive cards | make.powerautomate.com | VC-10 |
| 10 | Materiality determination workflow (SEC 8-K Item 1.05) | Disclosure Committee — SharePoint + Teams | VC-11 |
| 11 | OFAC sanctions screening for extortion / ransom payment | GC + Treasury workflow | VC-12 |
| 12 | Tabletop exercise harness — quarterly AI-specific scenarios | Teams + SharePoint | VC-13 |
| 13 | Regulator portal references — NYDFS, EDGAR, FINRA, FTC, CISA, state AGs | External portals | VC-14 |
| 14 | Evidence capture, cadence, and examiner packet | All portals + Purview | VC-15 |

The numbering of regulator timers used throughout this walkthrough mirrors the **Regulator Notification Matrix** in [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md). Detection and triage signals upstream of §2 are owned by [Control 1.8](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) and [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md); supervisory escalation downstream of §6 is owned by [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).

## 0. Pre-flight Prerequisites and Triage

Before opening any portal blade or declaring an incident, complete the pre-flight checks below. A failed pre-flight gate is itself an auditable finding and must be logged in the incident worksheet that anchors every Control 3.4 case.

### 0.1 Role elevation via Entra PIM

Every role used in this walkthrough must be activated through **Microsoft Entra Privileged Identity Management (PIM)** with a justification reference and, where required, dual approver sign-off. Session maximums of 4–8 hours are recommended; do not leave incident-response roles permanently assigned. Permanent assignment is itself a Control 3.4 finding under the principle of least privilege required by GLBA Safeguards 16 CFR 314.4(c).

| Canonical role | Surfaces required for | Elevation recommendation |
|----------------|----------------------|--------------------------|
| **CISO** (or **Incident Commander** delegate) | Defender XDR Incidents, Sentinel Incidents, Disclosure Committee invocation | 8 h session, dual-approver for Sev-1 / Sev-2 |
| **Chief Compliance Officer (CCO)** | NYDFS / FINRA / SEC notification gating, regulator-portal access | 8 h session, justification = incident ID |
| **General Counsel** | Legal hold issuance, materiality determination, OFAC screening | 8 h session, dual-approver |
| **Privacy Officer** | Reg S-P / GLBA / state breach evaluation, customer notification authoring | 4 h session |
| **AI Governance Lead** | AI-agent-specific case ownership in Insider Risk Management, ATLAS tagging review | 4 h session |
| **Sentinel Admin** | Sentinel automation rules, playbook bind, SOAR | 4 h session, ticket justification |
| **SOC Analyst** | Defender XDR triage, Sentinel investigation graph, Cloud Apps drill-in | 4 h session |
| **Entra Security Admin** | Identity-side containment (revoke sessions, disable accounts) | 4 h session, dual-approver for tenant-admin scope |
| **Power Platform Admin** | Disable / quarantine compromised agents, environment isolation | 4 h session |
| **M365 Admin** | Service Health correlation, Exchange / Teams content actions | 4 h session |
| **Purview Compliance Admin** | IRM cases, eDiscovery (Premium) holds, Communication Compliance review | 4 h session |
| **Designated Series 24/66 Principal** | Supervisory close-out for customer-facing Copilot incidents | 4 h session |
| **Business Continuity Officer** | BCM invocation, FFIEC alignment | 4 h session |
| **Internal Audit** (read-only observer) | Evidence-trail walk-through, post-incident review attestation | 8 h session, read-only PIM role |

!!! example "Examiner Evidence Box — Role elevation"
    **Capture for every Control 3.4 incident:**

    1. PIM activation history export (CSV) filtered to the incident window from initial detection (T0) through post-incident review (T+30 days at minimum, longer if extended notification timers are still running).
    2. Ticket ID from the change / access-management system (ServiceNow, Jira, Azure DevOps).
    3. Screenshot of the PIM "My roles" blade for each elevated principal showing active assignments and expiration timestamps.
    4. Approver record where dual approval applied.

    Store in the Purview-backed evidence library tagged **Control=3.4, Incident=<INC-ID>**. Apply retention label `FSI-AgentGov-6yr-WORM` to help meet SEC 17a-4(f) recordkeeping expectations.

### 0.2 License and feature verification

1. In the **Microsoft 365 admin center** at [https://admin.microsoft.com](https://admin.microsoft.com), confirm the tenant has active **Microsoft 365 E5** (or **E5 Security + E5 Compliance**) and **Microsoft 365 Copilot** licensing across the in-scope user base. Open **Billing → Licenses** and screenshot the license inventory.
2. In **Microsoft Defender XDR** at [https://security.microsoft.com](https://security.microsoft.com), confirm **Settings → Microsoft Defender XDR → General → Account** shows the unified XDR experience enabled and onboarding status = **Complete**.
3. In **Microsoft Sentinel** (Azure portal → **Microsoft Sentinel** → select workspace), confirm at least the following data connectors are **Connected** (full configuration is owned by [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)):
    - Microsoft Defender XDR
    - Microsoft Entra ID (sign-in logs, audit logs, risky users)
    - Microsoft 365 (Unified Audit Log)
    - Microsoft Defender for Cloud Apps
    - Microsoft Purview Information Protection
    - Power Platform inventory connector (Copilot Studio / Power Apps activity)
4. In **Microsoft Purview** at [https://purview.microsoft.com](https://purview.microsoft.com), confirm:
    - **Insider risk management → Settings → Analytics** shows **Enabled** (or analytics-only mode for tenants in pilot).
    - **eDiscovery → Premium** is provisioned (E5 Compliance or eDiscovery & Audit add-on).
    - **Communication compliance** has at least one Copilot-scoped policy active (cross-ref [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)).
5. In **Power Platform admin center** at [https://admin.powerplatform.microsoft.com](https://admin.powerplatform.microsoft.com), confirm **Tenant → Analytics settings → Admin analytics** is **On**.
6. Record the **tenant region** and **sovereign-cloud flag** on the incident worksheet — this determines whether §1 compensating controls apply.

### 0.3 Authoritative-source readiness

Incident triage is only as reliable as the upstream signals that feed Defender XDR and Sentinel. Confirm the following **before** any Control 3.4 session:

| Source | Owner | Readiness check |
|--------|-------|-----------------|
| Unified Audit Log (UAL) | Purview Compliance Admin | Last ingestion timestamp ≤ 30 minutes; no ingestion-lag banner on **Purview → Audit** landing page |
| Entra sign-in logs | Entra Security Admin | Last record ≤ 5 minutes; risky-user list refreshed |
| Defender for Cloud Apps activity log | SOC Analyst | Connector status **Healthy**; activity count within ±10% of 7-day baseline |
| Power Platform admin analytics | Power Platform Admin | Last export ≤ 7 days; agent inventory matches Control 1.2 registry within ±2% |
| Agent registry (Control 1.2) | AI Governance Lead | Last attestation ≤ 30 days; owner field populated for 100% of registered agents |
| Sentinel data connectors | Sentinel Admin | All in-scope connectors **Connected**; ingestion delta ≤ 15 minutes |
| Service Health feed | M365 Admin | Health dashboard loads without error; advisory feed current |

A failure in any row **does not** block declaring an incident, but **must** be logged as an evidentiary caveat on the incident worksheet — examiners may ask why a particular signal was unavailable during the window of interest, and the firm must be able to explain.

### 0.4 Pre-flight gate checklist

- [ ] Required roles activated via PIM and evidence captured (§0.1)
- [ ] Licensing and feature flags confirmed (§0.2)
- [ ] Authoritative-source freshness confirmed or exceptions logged (§0.3)
- [ ] Sovereign-cloud flag recorded on the incident worksheet
- [ ] Incident severity (Sev-1 / 2 / 3) provisionally assigned per §2.3 rubric
- [ ] Evidence library path and incident tag prepared in Purview
- [ ] ITSM ticket opened, **incident commander named**, and linked to the worksheet
- [ ] CCO and General Counsel placed on **standby notice** for any Sev-1 / Sev-2 candidate

Only proceed to §1 (sovereign) or §2 (commercial / GCC) after every box is ticked or a documented exception is approved by the Incident Commander.

!!! tip "Cross-Reference"
    Pre-flight role and licensing checks overlap with [Control 2.25 §0 pre-flight](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md). Where the same evidence has been captured for an in-flight 2.25 session, link that artifact rather than re-capturing — but **do** re-confirm the freshness of authoritative sources at incident T0.

## 1. Sovereign Cloud Variant — Manual Incident Register and Manual Notification Matrix

GCC High and DoD tenants (and occasionally GCC during staged rollouts) lack full parity for Defender XDR cross-workload correlation, Purview Insider Risk Management cases, and the Communication Compliance Copilot scope. Until parity is confirmed, the **Manual Incident Register** and **Manual Notification Matrix** below become the **primary evidence artifacts** for Control 3.4 in those tenants.

### 1.1 Manual Incident Register inputs

The register is a SharePoint list (or, where SharePoint columns are insufficient, a controlled Excel workbook on the IR site documented in §8). Every row represents one incident and carries the following columns at minimum:

| Column | Type | Source / authority |
|--------|------|--------------------|
| `IncidentId` | Text (firm-prefixed, e.g., `INC-FSI-2026-0042`) | Incident Commander assigns at T0 |
| `DetectionTimeUtc` | DateTime | Earliest signal timestamp from Defender XDR / Sentinel / IRM / SOC analyst observation |
| `DetectionSource` | Choice (Defender XDR / Sentinel / IRM / Comm Compliance / Service Health / Tip / Other) | SOC Analyst |
| `Severity` | Choice (Sev-1 / Sev-2 / Sev-3 / Sev-4) | Incident Commander per §2.3 rubric |
| `MaterialityCandidate` | Yes/No | CISO + General Counsel; triggers §10 if Yes |
| `AgentInvolved` | Yes/No | AI Governance Lead |
| `AgentId` | Text (links to Control 1.2 registry) | AI Governance Lead |
| `Zone` | Choice (Z1 Personal / Z2 Team / Z3 Enterprise) | AI Governance Lead |
| `NPIRecordsAffected` | Number | Privacy Officer |
| `BooksAndRecordsImpact` | Yes/No | CCO |
| `SupervisorySystemFailure` | Yes/No | Designated Series 24/66 Principal |
| `PublicDisclosureThreshold` | Yes/No | CISO + General Counsel |
| `MITREATTACK` | Multi-choice | SOC Analyst (cross-ref §2.4) |
| `MITREATLAS` | Multi-choice | AI Governance Lead (cross-ref §2.4) |
| `RegulatorMatrixApplied` | Yes/No | CCO (links to §1.2) |
| `LegalHoldId` | Text | General Counsel (cross-ref §5) |
| `RootCauseStatement` | Long text | Incident Commander at close-out |
| `RootCauseTimestampUtc` | DateTime | Used to start regulator clocks (§9) |
| `EvidencePackUri` | URL | Purview-backed library |
| `CloseOutSignedBy` | Person | Incident Commander + CCO |

### 1.2 Manual Notification Matrix template

The matrix is a per-incident table that records, for **every** potentially applicable regulator clock, the determination, owner, and filing status. The matrix is updated at each materiality / scoping checkpoint and is the source of truth that the §9 Power Automate countdown timers mirror in commercial tenants.

| Regulator clock | Trigger event | Statutory window | Owner (firm role) | Filed Yes/No | Filing receipt |
|-----------------|---------------|------------------|-------------------|--------------|----------------|
| **NYDFS 23 NYCRR 500.17(a)** — cybersecurity event notice | Determination of "cybersecurity event" reportable to Superintendent | **72 hours** from determination | CCO + CISO | | |
| **NYDFS 23 NYCRR 500.17(c)** — extortion-payment notice | Extortion payment made (any amount) | **24 hours** from payment | CCO + General Counsel | | |
| **NYDFS 23 NYCRR 500.17(c)(2)** — extortion-payment written description | Extortion payment | **30 days** from payment | CCO | | |
| **Federal banking 36-hour rule** (12 CFR 53.3 OCC / 225.302 Fed / 304.23 FDIC) | "Notification incident" determined | **36 hours** from determination | CISO + CCO | | |
| **SEC Form 8-K Item 1.05** | Materiality determination of cybersecurity incident (public-company FSIs) | **4 business days** from materiality determination | General Counsel + Disclosure Committee | | EDGAR receipt |
| **SEC Reg S-P 17 CFR §248.30(a)(4)** customer notice | "Sensitive customer information" reasonably likely accessed/used | **As soon as practicable, not later than 30 days** after becoming aware | Privacy Officer + CCO | | |
| **SEC Reg S-P §248.30(a)(5)** service-provider notice | Service-provider unauthorized-access incident | **72 hours** from notice receipt | Privacy Officer | | |
| **FINRA Rule 4530(a)** | Reportable event under (a)(1)–(a)(7) | **30 calendar days** from knowledge | CCO via Firm Gateway | | |
| **FINRA Rule 4530(d)** quarterly statistical | Customer complaints quarterly aggregation | **15 calendar days** after end of calendar quarter | CCO | | |
| **FTC Safeguards Rule 16 CFR 314.4(j)** | Notification event ≥ 500 consumers | **As soon as possible, not later than 30 days** after discovery | Privacy Officer | | |
| **State breach notification** (NY GBL 899-aa, CA CCPA, MA 201 CMR 17, etc.) | State-specific trigger | Varies by state | Privacy Officer + General Counsel | | |
| **CISA CIRCIA** (when rule effective) | "Covered cyber incident" | **72 hours** (covered incident) / **24 hours** (ransom payment) | CISO + General Counsel | | |
| **NCUA 12 CFR 748.1(c)** (CU-affiliated) | Catastrophic act / cyber incident | Per Part 748 schedule | CCO | | |

### 1.3 Reconciliation logic and signing

For every open incident in sovereign tenants:

1. Update the register row at every state transition (detection → triage → containment → eradication → recovery → close-out).
2. Update the matrix at every checkpoint where a clock might start, advance, or close.
3. **Dual-sign** the closed register row and matrix (Incident Commander + CCO).
4. Render to PDF with the incident ID, tenant ID, sovereign-cloud flag, and signature block in the header.
5. Store in the Purview evidence library with **retention label = 6 years WORM** to help meet SEC 17a-4(f) recordkeeping expectations.

!!! example "Examiner Evidence Box — Sovereign manual artifacts"
    **Capture for every incident:**

    1. The dual-signed register row PDF (one PDF per incident).
    2. The dual-signed notification matrix PDF.
    3. CSV export of the register filtered to the calendar quarter.
    4. Hash (SHA-256) of every PDF and CSV with timestamps.
    5. Purview evidence-library URL and retention-label confirmation screenshot.
    6. ITSM ticket ID and linked change record.

### 1.4 Commercial / GCC tenants

Commercial and GCC tenants with full Defender XDR and IRM parity execute §1.1 / §1.2 as a **defense-in-depth quarterly reconciliation** rather than as the primary artifact — confirm that every Defender XDR Sev-1 / Sev-2 incident from the quarter has a matching register row and matrix. Discrepancies are findings against Control 3.4 effectiveness and must be documented with root cause.

!!! tip "Cross-Reference"
    Sovereign-cloud connector parity is owned by [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md). If a connector is unavailable in your sovereign cloud, route the corresponding manual reconciliation step here in §1; do not modify the §2–§9 procedures, which assume commercial / GCC parity.

## 2. Defender XDR — Unified Incidents Queue

The **Microsoft Defender XDR Unified Incidents queue** is the **primary triage surface** for Control 3.4 in commercial and GCC tenants. It correlates alerts across **Defender for Endpoint**, **Defender for Office 365**, **Defender for Identity**, **Defender for Cloud Apps**, **Defender for Cloud**, and (where ingested) **Microsoft Sentinel**. For AI-agent incidents, ATT&CK + ATLAS dual-tagging makes Defender XDR the canonical "single pane" the SOC works from.

### 2.1 Navigation

1. Sign in to the **Microsoft Defender portal** at [https://security.microsoft.com](https://security.microsoft.com) with a SOC role activated (SOC Analyst at minimum; Incident Commander for status changes).
2. In the left nav, expand **Investigation & response → Incidents & alerts → Incidents**.
3. The default view is **Open incidents — last 7 days**. Adjust the time window using the filter bar.

### 2.2 Triage UX — column set, filters, and row actions

Configure the incident queue once per analyst workstation; the column set and saved filter are evidence artifacts in their own right.

1. Click **Customize columns** (top-right). Required columns for FSI Control 3.4 use:
    - **Incident name**
    - **Tags** (must include `Copilot`, `AgentId:*`, `Zone:*`, `NPI`, `BooksAndRecords` where applicable)
    - **Severity**
    - **Investigation state**
    - **Status** (New / In progress / Resolved)
    - **Assigned to**
    - **Categories**
    - **Impacted assets** (devices, mailboxes, users, apps, **and AI agents** where the agent surface area is recognized)
    - **Active alerts**
    - **Service sources** (which Defender workloads contributed)
    - **Detection sources**
    - **Data sensitivity** (sensitivity-label coverage from Purview Information Protection — cross-ref [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md))
    - **First activity** / **Last activity**
    - **MITRE ATT&CK techniques**
2. Click **Filters → + Add filter** and create the saved filter **"FSI — Copilot / Agent Triage"** with:
    - Tags contains `Copilot` OR `AgentId:`
    - Severity in (High, Medium)
    - Status in (New, In progress)
3. Save the filter and pin it to the queue header.

### 2.3 FSI severity rubric — beyond the Defender default

Defender XDR's default Sev (Informational / Low / Medium / High) is necessary but **not sufficient** for FSI Control 3.4. Apply the following overlay during triage; the resulting severity is what enters the §1 register and drives the §9 timer flows.

| FSI Sev | Defender mapping | Triggers (any one is sufficient) | Clock-starting potential |
|---------|------------------|----------------------------------|--------------------------|
| **Sev-1 (Critical)** | High + escalation | NPI of ≥ 500 consumers reasonably likely accessed; supervisory-system failure for customer-facing Copilot; **public-disclosure threshold** met (8-K materiality candidate); active extortion demand; books-and-records integrity breached | All FSI clocks must be evaluated; CCO + GC + CISO immediate notify |
| **Sev-2 (High)** | High | NPI < 500 but > 0; Copilot agent acting on stale / poisoned context affecting external-facing communications; orphaned Z3 agent with active sessions; identity compromise of Sentinel / Defender / Power Platform Admin | NYDFS 500.17, Reg S-P, FINRA 4530(a) candidate; CCO notify within 4 h |
| **Sev-3 (Medium)** | Medium | Internal-only impact; Z2 agent misuse caught in IRM; supervisory escalation in Communication Compliance with no external send; failed but contained credential phishing | Internal SLA only; quarterly aggregation under 4530(d) candidate |
| **Sev-4 (Low / Informational)** | Low / Informational | Single-user Z1 incident; tabletop-style false positive; signal correlation only | Internal record; no regulator clock |

The rubric is **applied** by the Incident Commander, with input from the SOC Analyst (technical severity), AI Governance Lead (agent-specific severity), Privacy Officer (NPI count), and CCO (regulator-clock potential). Document the application in the incident worksheet — examiners frequently ask **why** a particular incident was assigned a particular severity.

!!! warning "Rubric overrides require documented justification"
    A mismatch between the Defender XDR default severity and the FSI Sev assigned by the Incident Commander is permissible but must be justified in writing. The justification is captured in the incident worksheet (§1.1 row), in the Defender XDR incident comment (§2.6), and in the Sentinel incident comment (§3.4).

### 2.4 MITRE ATT&CK + MITRE ATLAS dual tagging

Defender XDR auto-tags incidents with MITRE ATT&CK techniques where the underlying alert engine produced a mapping. **MITRE ATLAS** (Adversarial Threat Landscape for AI Systems) is **not** auto-tagged — Control 3.4 requires the AI Governance Lead to manually overlay ATLAS technique IDs for any incident involving a Copilot or Power Platform agent.

1. From the incident summary blade, scroll to the **Attack story** pane and click **MITRE techniques**.
2. Verify the auto-mapped ATT&CK techniques. Add or correct techniques via **+ Add technique** if the mapping is incomplete.
3. Open the **Comments and history** tab and add an ATLAS overlay comment in the structured form below:

    ```
    ATLAS-OVERLAY v1
    Incident: <INC-ID>
    Agent involved: <AgentId>
    Zone: <Z1|Z2|Z3>
    Techniques:
      - AML.T0051 (LLM Prompt Injection)
      - AML.T0048 (External Harms)
      - AML.T0057 (LLM Data Leakage)
    Justification: <free text — link to evidence>
    Reviewed by: <AI Governance Lead UPN>
    Reviewed at (UTC): <ISO timestamp>
    ```

4. Re-save the incident; the comment is immutable in the audit trail.

### 2.5 Multi-source correlation review

Before assigning the incident to an analyst, walk the **Attack story** and **Assets** tabs to confirm that all expected sources contributed:

| Expected source | What to verify |
|-----------------|----------------|
| **Defender for Endpoint** | Process tree for any device-side maker / agent-runtime activity; suspicious child processes of Office, browser, or Power Platform host |
| **Defender for Office 365** | Mail-flow telemetry for any Copilot-generated outbound email; URL detonation hits |
| **Defender for Identity** | Lateral movement, golden-ticket-style anomalies near service-principal accounts |
| **Defender for Cloud Apps** | Anomalous OAuth grant to a Copilot Studio agent; data-exfiltration signal to unsanctioned cloud apps |
| **Defender for Cloud** | Azure resource-side activity for any Sentinel / Logic App / Power Platform connector |
| **Microsoft Sentinel** (where bidirectionally synced) | Custom KQL detections, watchlist hits, threat-intel matches |
| **Microsoft Purview Information Protection** | Sensitivity-label drift, downgrade events, label-removal anomalies |

Any **missing** source (e.g., Defender for Cloud Apps shows no activity for an obviously cloud-active incident) is a **data-integrity finding** in its own right — open a sub-task to [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) and document on the worksheet. Do not silently proceed.

### 2.6 Assignment, status, and incident comments

1. Click **Manage incident** (top-right of the incident detail blade).
2. Set:
    - **Incident name** — prepend the firm incident ID (e.g., `INC-FSI-2026-0042 — Copilot prompt-injection — sales BU`).
    - **Tags** — confirm `Copilot`, `AgentId:<id>`, `Zone:<n>`, and any of `NPI`, `BooksAndRecords`, `Supervisory`, `8K-Candidate` as applicable.
    - **Assigned to** — name the SOC Analyst at L2 minimum; the Incident Commander remains accountable.
    - **Severity** — set to the **FSI Sev** per §2.3 (override the default if needed).
    - **Status** — `In progress` once triage starts; `Resolved` only at full close-out (do **not** resolve before the §1 register is closed and the §9 timers are stopped).
    - **Classification / Determination** — leave open until close-out; on close set to `True positive` with a determination matching the root cause.
3. Click **Save**.
4. Add an **opening comment** in the **Comments and history** tab using the structured template below:

    ```
    OPEN-COMMENT v1
    Incident: <INC-ID>
    Detection T0 (UTC): <ISO timestamp>
    Triage T1 (UTC): <ISO timestamp>
    FSI Sev: <Sev-1|Sev-2|Sev-3|Sev-4>
    Sev rubric trigger(s): <NPI|BooksAndRecords|Supervisory|PublicDisclosure|Other>
    Materiality candidate (8-K): <Yes|No|TBD>
    Regulator clocks placed on standby:
      - NYDFS 500.17(a) 72h: <Yes|No>
      - Banking 36h:         <Yes|No>
      - SEC 8-K 4bd:         <Yes|No>
      - Reg S-P 30d:         <Yes|No>
      - FTC 30d:             <Yes|No>
      - FINRA 4530(a) 30d:   <Yes|No>
      - State BNs:           <Yes|No>
    Assigned analyst: <UPN>
    Incident Commander: <UPN>
    CCO standby notified at (UTC): <ISO timestamp>
    GC standby notified at (UTC): <ISO timestamp>
    Linked SharePoint case: <URI>
    Linked legal hold (if any): <Hold ID>
    ```

5. Subsequent state changes (containment achieved, eradication confirmed, recovery validated) must each receive a `STATE-COMMENT` follow-up using the same structure.

### 2.7 Linking to Microsoft Sentinel

If Sentinel is bidirectionally synced (recommended; see [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)), Defender XDR incidents flow into Sentinel automatically with a back-link. Confirm the **Microsoft Sentinel incident** link appears in the Defender XDR incident summary header — clicking it opens the Sentinel incident in a new tab. If the link is **missing**, the bidirectional sync has degraded; open a Control 3.9 sub-task before continuing.

### 2.8 Bulk export for evidence

From the incidents queue:

1. Click **Export** (top-right) and choose **CSV**.
2. Rename to `defender-incidents_<tenantId>_<incidentId>_<ISO-date>.csv`.
3. Hash (SHA-256) and store both the CSV and the hash in the Purview evidence library tagged **Control=3.4, Incident=<INC-ID>**.
4. Capture full-page screenshots of the queue (with the FSI saved filter applied) and the incident detail blade.

!!! example "Examiner Evidence Box — Defender XDR triage"
    **Capture for every incident:**

    1. Queue-state screenshot at incident open with the FSI saved filter applied.
    2. Incident detail blade screenshot (Attack story, Assets, MITRE techniques tabs).
    3. ATLAS overlay comment text (copy-paste from the audit trail).
    4. Manage-incident screenshot showing FSI Sev, tags, and assignment.
    5. Open-comment text and every subsequent state-comment.
    6. CSV export hash and storage URI.

!!! tip "Cross-Reference"
    Detection content (analytic rules, hunting queries, custom Defender XDR detections) is configured under [Control 1.8](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) and [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md). Do not author new detections from this walkthrough — route detection-engineering changes through 3.9 and the firm's detection-as-code pipeline.

## 3. Microsoft Sentinel — Incidents and SOAR (Logic Apps) Playbooks

Microsoft Sentinel extends Defender XDR triage with **automation rules**, **Logic Apps playbooks** (SOAR), **investigation graph**, and **long-window hunting**. Control 3.4 uses Sentinel as the **orchestration spine** that fans incidents out to Power Automate notification flows (§9), Teams adaptive card escalations, SharePoint IR list updates (§8), and ITSM ticketing.

> Connector configuration, workspace sizing, and analytic-rule authoring are **out of scope** for this walkthrough — see [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md). The procedures below assume the workspace is healthy and bidirectional Defender XDR sync is on.

### 3.1 Navigation

1. Sign in to the **Azure portal** at [https://portal.azure.com](https://portal.azure.com) with **Sentinel Admin** activated (or **SOC Analyst** for read-only triage).
2. Search for **Microsoft Sentinel** and select the workspace named per the firm's naming convention (e.g., `sent-fsi-prod-eastus2`).
3. In the workspace blade, select **Threat management → Incidents**.

### 3.2 Reviewing the synced incident

For an incident that originated in Defender XDR (§2):

1. Locate the incident by Defender XDR incident ID or by the FSI tag set (`Copilot`, `AgentId:<id>`, `Zone:<n>`).
2. Click the incident to open the detail pane on the right.
3. Confirm the **Provider name = Microsoft 365 Defender** and the back-link to Defender XDR is present.
4. Click **View full details** to open the full incident page.

The Sentinel incident page exposes panes the Defender XDR view does not:

- **Investigation graph** — interactive graph of entities (users, hosts, IPs, files, **AI agents** via custom entity mapping) and their relationships.
- **Bookmarks** — analyst-flagged hunting query results pinned to the incident as evidence.
- **Workbook deep-links** — navigation to the workbook visualizations defined in [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).
- **Activity log** — every state and assignment change with timestamps, the audit-friendly view examiners look at.

### 3.3 Custom AI-agent entity in the investigation graph

Where the workspace has the optional **AI Agent custom entity** mapping configured (per [Control 3.9 §6](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)), the investigation graph displays the agent as a first-class node alongside users and devices. Confirm:

1. The agent node displays the canonical `AgentId` (matching the Control 1.2 registry).
2. Edges to user nodes represent identity relationships (owner, sponsor, maker, recent invokers).
3. Edges to data nodes represent connector-grounded data sources accessed in the incident window.
4. Hovering on the agent node reveals the **Zone**, **sensitivity-label coverage**, and **last attestation date**.

If any of those properties is **missing**, the agent inventory feed is stale — open a Control 3.9 sub-task.

### 3.4 Adding the incident comment with the Sentinel-side overlay

Sentinel comments are independent of Defender XDR comments and form a separate evidence trail. Add the following at incident open:

1. From the incident detail page, click **Comments → + New comment**.
2. Paste the structured template:

    ```
    SENTINEL-OPEN v1
    Incident (Sentinel): <Sentinel ID>
    Linked Defender XDR: <Defender XDR ID>
    Linked SharePoint case: <URI>
    Hunting bookmarks attached: <count>
    Workbook visualizations reviewed: <list>
    Custom AI Agent entity present: <Yes|No>
    Automation rules pending: <list of rule names>
    Playbook(s) pending invocation: <list>
    ```

3. Click **Comment** to save.

### 3.5 Automation rules — wiring incidents to playbooks

Sentinel **automation rules** are the trigger glue between incidents and Logic Apps playbooks. Control 3.4 expects the following rules to be **already configured** by the Sentinel Admin under [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md). The procedure below verifies they are present and triggers a manual playbook run if needed.

| Automation rule | Trigger | Action | Owner |
|-----------------|---------|--------|-------|
| `AR-FSI-OpenIncident-Notify` | When incident is created with tag `Copilot` or `AgentId:` | Run playbook `PB-Notify-CISO-CCO-GC-Standby` | Sentinel Admin |
| `AR-FSI-Sev1-Escalate` | When incident severity changes to High AND tag includes `8K-Candidate` | Run playbook `PB-Convene-Disclosure-Committee` | Sentinel Admin |
| `AR-FSI-NYDFS-72h-Standby` | When tag `NYDFS-Reportable` added | Run playbook `PB-Start-NYDFS-72h-Timer` | Sentinel Admin |
| `AR-FSI-Banking-36h-Standby` | When tag `Banking-Notification` added | Run playbook `PB-Start-Banking-36h-Timer` | Sentinel Admin |
| `AR-FSI-RegSP-30d-Standby` | When tag `RegSP-Customer-Notice` added | Run playbook `PB-Start-RegSP-30d-Timer` | Sentinel Admin |
| `AR-FSI-FINRA-4530a-Standby` | When tag `FINRA-4530a` added | Run playbook `PB-Start-FINRA-4530a-30d-Timer` | Sentinel Admin |
| `AR-FSI-FTC-30d-Standby` | When tag `FTC-Safeguards-Notice` added | Run playbook `PB-Start-FTC-30d-Timer` | Sentinel Admin |
| `AR-FSI-Containment-Verify` | When status changes to `In progress` AND tag `Containment-Achieved` added | Run playbook `PB-Update-SharePoint-IR-List` | Sentinel Admin |
| `AR-FSI-Close-Out` | When status changes to `Closed` AND tag `RootCause-Approved` added | Run playbook `PB-Close-Out-Notify` | Sentinel Admin |

Verify each rule is **Enabled** at **Sentinel → Configuration → Automation → Active rules**. A disabled rule is a finding; document on the worksheet and re-enable through the Control 3.9 change process.

### 3.6 Manually invoking a playbook

If a playbook needs to run **before** a tag-driven trigger fires (e.g., the analyst already knows the incident is NYDFS-reportable but the tag has not yet been applied):

1. From the incident detail page, click **Actions → Run playbook (Preview)**.
2. In the playbook picker, search by name (e.g., `PB-Start-NYDFS-72h-Timer`).
3. Confirm the playbook's **Permissions status = Permission granted** for this Sentinel workspace; if not, the workspace's managed identity lacks the run-playbook role and must be remediated by the Sentinel Admin.
4. Click **Run**.
5. Confirm the run appears under **Runs** for the playbook with status **Succeeded**.

### 3.7 Reviewing playbook run logs

For each playbook invoked during an incident, capture the run log as evidence:

1. Navigate to **Sentinel → Configuration → Automation → Active playbooks**.
2. Select the playbook by name.
3. Click **Open in Logic Apps** to open the underlying Logic App in the Azure portal.
4. In the Logic App blade, click **Runs history**.
5. Filter by the incident time window, identify the relevant run, and click into it to view the per-action log.
6. Export the run JSON via **... → Download run JSON** (or screenshot each action's input / output for evidence).
7. Store the JSON / screenshots in the Purview evidence library tagged **Control=3.4, Incident=<INC-ID>, Playbook=<name>**.

!!! warning "Logic App secrets in run logs"
    Playbook run logs may contain secrets in plain text (API keys, OAuth tokens, customer identifiers) if the Logic App was authored without secure inputs / outputs flags. Before exporting, confirm with the Sentinel Admin that the playbook's actions are configured with **Secure Inputs** and **Secure Outputs** turned on for any action that handles secrets. If a run log contains exposed secrets, the export itself becomes a data-handling event — route to General Counsel and consider an immediate secret-rotation action.

### 3.8 Hunting and bookmarks

For complex incidents, the SOC Analyst will run KQL hunting queries (defined in [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)). Pin notable results to the incident as **bookmarks**:

1. From **Threat management → Hunting**, run the relevant query.
2. In the results pane, select the rows of interest.
3. Click **Add bookmark**.
4. In the **Add bookmark** dialog, enter:
    - **Bookmark name** — descriptive (e.g., `INC-FSI-2026-0042 — Copilot prompt-injection — anomalous prompts`).
    - **Tags** — incident ID and tag set.
    - **Mapped entities** — confirm the auto-mapped entities (account, host, IP, agent) are correct.
    - **Incident** — select the open incident to attach the bookmark to.
5. Click **Save**.
6. Confirm the bookmark appears under the incident's **Bookmarks** pane.

### 3.9 Closing the Sentinel incident

Sentinel close-out lags Defender XDR close-out by design — close Sentinel **only after** the §9 timers have either reached their statutory determination point or been documented as not applicable, and the §1 register row is signed.

1. From the incident detail page, click **Manage → Status → Closed**.
2. Set **Classification → True Positive** (or the applicable determination).
3. Add a **closing comment** with the structured template:

    ```
    SENTINEL-CLOSE v1
    Incident (Sentinel): <Sentinel ID>
    Linked Defender XDR: <Defender XDR ID>
    Root cause statement: <free text — link to RCA document URI>
    Root cause timestamp (UTC): <ISO>
    Notification timers — closed status:
      - NYDFS 500.17(a) 72h: <Filed at UTC | Not applicable, justification>
      - Banking 36h:         <Filed at UTC | Not applicable, justification>
      - SEC 8-K 4bd:         <Filed at UTC | Not applicable, justification>
      - Reg S-P 30d:         <Filed at UTC | Not applicable, justification>
      - FTC 30d:             <Filed at UTC | Not applicable, justification>
      - FINRA 4530(a) 30d:   <Filed at UTC | Not applicable, justification>
      - State BNs:           <Per state — list>
    Legal hold status: <Open | Released at UTC>
    Insider Risk case status: <Open | Closed | N/A>
    Communication Compliance escalations: <count, dispositions>
    SharePoint case URI: <URI>
    Disclosure Committee memo URI (if 8-K): <URI>
    Tabletop scenario applicable for next quarter: <Yes|No>
    Signed off by Incident Commander (UPN): <UPN at UTC>
    Signed off by CCO (UPN): <UPN at UTC>
    Signed off by GC (UPN): <UPN at UTC>
    ```

4. Click **Apply**.

!!! example "Examiner Evidence Box — Sentinel orchestration"
    **Capture for every incident:**

    1. Sentinel incident screenshot at open (full details page).
    2. Investigation graph screenshot showing the AI agent custom entity (where present).
    3. Open-comment and close-comment text.
    4. List of automation rules that fired (with Logic App run IDs).
    5. Playbook run JSONs (or per-action screenshots) for every invocation.
    6. Bookmarks (if any) with their KQL query text and result snapshots.

!!! tip "Cross-Reference"
    Workspace health, ingestion baselines, KQL detection authoring, and playbook authoring are owned by [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md). If a playbook is missing or fails repeatedly, route through 3.9; do not modify Logic App definitions from this walkthrough.

## 4. Microsoft Purview Insider Risk Management — Cases

Where the incident involves **AI-agent misuse by an insider**, **anomalous prompt behavior** that suggests an authorized user is exfiltrating data via a Copilot agent, or **runaway agent** behavior on stale context, **Purview Insider Risk Management (IRM)** is the investigation surface. IRM enforces a pseudonymized review workflow (default-on for the analyst role) and provides clean escalation paths into eDiscovery (Premium) for legal hold and regulator-production export.

> Policy authoring (the upstream content for IRM alerts and cases) is owned by [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md). Control 3.4 consumes IRM cases at the case-management blade level only.

### 4.1 Navigation

1. Sign in to the **Microsoft Purview portal** at [https://purview.microsoft.com](https://purview.microsoft.com) with **Insider Risk Management Investigators** or **Insider Risk Management Analysts** activated (the role determines whether usernames are pseudonymized in the UI).
2. From the left nav, expand **Solutions → Insider risk management**.
3. Select **Cases** in the secondary nav.

### 4.2 Pseudonymization — confirm before you click

IRM defaults to **pseudonymized usernames** for analyst-role users; investigator-role users see real UPNs. Confirm before opening any case:

1. Click the user-account dropdown (top-right) and select **Account → Roles** to confirm your active IRM role.
2. If you see real UPNs in the case list and your role is **Analyst**, the tenant has likely been configured with **Privacy → Show usernames = On**, which is a **policy drift finding** under Control 1.12 — open a sub-task before continuing.
3. Pseudonymized cases display synthetic identifiers (e.g., `Anon_8a3f`); the investigator role can resolve to real identities through a documented unmask flow that itself produces an audit record.

!!! warning "Unmask events are auditable"
    Resolving a pseudonymized identifier to a real UPN creates an audit record in Purview (Activity = `IRMUnmask`). Examiners may sample these records to confirm unmask was justified; capture the case ID and justification at every unmask.

### 4.3 Opening a case from an alert

When a Defender XDR / Sentinel incident is correlated with an IRM alert (e.g., the same impacted user appears in a `Data leaks via Copilot` policy alert):

1. From **Insider risk management → Alerts**, locate the alert by user identifier, severity, and date.
2. Confirm the **Policy** that fired matches an AI-agent-misuse policy template — typical templates configured under [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md) include:
    - **Data exfiltration via agent** (Copilot Studio agent invoked unusual sensitive-content searches and exported)
    - **Anomalous prompt behavior** (sudden volume / pattern shift in Copilot prompts)
    - **Sensitive-data interaction by departing user via Copilot** (HR-leaver list correlated with Copilot activity in the 30-day window)
    - **Agent acting on stale / poisoned context** (anomalous grounding source diversity within an agent session)
3. Click **Actions → Confirm alert and create case**.
4. In the **Create case** dialog, enter:
    - **Case name** — prepend the firm incident ID (e.g., `INC-FSI-2026-0042 — IRM — anon_8a3f — Copilot exfiltration`).
    - **Case description** — link to the Defender XDR and Sentinel incident IDs and the SharePoint case URI.
    - **Assigned to** — name the **Insider Risk Investigator** (typically a CCO-designated investigator).
5. Click **Create case**.

### 4.4 Case workspace — Activity, Content explorer, User activity, Alerts

The case workspace exposes four primary tabs. Walk each in order:

1. **Case overview** — confirms severity, score, policy, and assignee. Add a structured comment via **Activity timeline → Add note**:

    ```
    IRM-OPEN v1
    Case: <Case ID>
    Linked incident: <INC-ID>
    Linked Defender XDR: <Defender XDR ID>
    Linked Sentinel: <Sentinel ID>
    Policy(ies) triggered: <list>
    Investigator: <UPN>
    Pseudonymization: <On|Off — investigator-role only>
    Linked legal hold (planned/issued): <Hold ID|Pending>
    ```

2. **Alerts** — every IRM alert correlated with this user / case. Cross-reference each alert against the §1 register row.
3. **User activity** — timeline of risk indicators (file downloads, label downgrades, USB use, Copilot prompt anomalies, etc.). Use the **Filter** pane to narrow to the incident window.
4. **Content explorer** — preview of the actual content involved (where the user role permits content view). Treat content view as a **legal-hold-relevant action** — confirm a hold is in place (see §5) **before** previewing sensitive content.

### 4.5 AI-agent-misuse case — required steps

For any case tagged as AI-agent-related, perform these additional steps:

1. From **User activity → Filters**, confirm the **Application** filter includes `Microsoft Copilot`, `Copilot Studio`, `Power Apps`, `Power Automate`, and `Microsoft 365 Apps with Copilot`. Without these filters, agent-specific signals will not surface.
2. Cross-reference the **AgentId** from the Defender XDR / Sentinel tags against the agent registry (Control 1.2) and confirm the registered owner / sponsor / maker UPNs map (after unmask) to the case subject. If they do **not** map, the case may be an **unauthorized invocation** rather than authorized-user misuse — escalate to the AI Governance Lead and consider a separate Defender XDR incident for the unauthorized-invocation thread.
3. Where **prompt content** is needed for the investigation, request it through eDiscovery (Premium) per §5; do **not** attempt to extract prompts from IRM Content explorer alone.

### 4.6 Escalation to eDiscovery (Premium)

When the case warrants legal hold and / or regulator-production export:

1. From the case workspace, click **Actions → Escalate for investigation → Create eDiscovery (Premium) case**.
2. In the **Escalate** dialog, enter:
    - **eDiscovery case name** — prepend the firm incident ID (e.g., `INC-FSI-2026-0042 — eDiscovery — Copilot exfiltration`).
    - **Custodians** — pre-populate from the IRM case subject (after unmask, via the documented unmask flow). Add the agent service principal as a custodian where the agent itself is a content source.
    - **Scope** — Exchange mailbox, OneDrive site, Teams chat, and SharePoint sites associated with the user; **and** Copilot interaction history (chat history container) for the in-scope user.
3. Confirm the **Notify** toggle is set to **On** so a hold notice is generated automatically — General Counsel reviews and releases the notice (§5.4) before it is sent.
4. Click **Escalate**.
5. Confirm the new eDiscovery (Premium) case appears with **Status = Active** and the IRM case shows the back-link.

### 4.7 Case close-out

1. From the case workspace, click **Actions → Resolve case**.
2. Enter the **Resolution** (e.g., `Substantiated — supervisory action taken`, `Substantiated — referred to HR`, `Unsubstantiated — false positive`, `Substantiated — referred to law enforcement`).
3. Add a **closing note** with the structured template:

    ```
    IRM-CLOSE v1
    Case: <Case ID>
    Linked incident: <INC-ID>
    Resolution: <enum from above>
    Resolution rationale: <free text — link to evidence>
    Linked eDiscovery case: <eDisco case ID|N/A>
    Linked legal hold: <Hold ID|Released at UTC|N/A>
    Supervisory escalation (Control 2.12): <Yes|No — if Yes, FINRA 3110 reviewer UPN and reviewed-at UTC>
    Closed by: <Investigator UPN at UTC>
    Reviewed by (CCO designee): <UPN at UTC>
    ```

4. Click **Resolve**.

!!! example "Examiner Evidence Box — IRM case"
    **Capture for every IRM-correlated incident:**

    1. Case overview screenshot at open and at close.
    2. Open-note and close-note text.
    3. Pseudonymization confirmation screenshot (analyst-role) or unmask audit record reference (investigator-role).
    4. List of policies triggered with template versions.
    5. eDiscovery (Premium) case ID and back-link confirmation (where escalated).
    6. Resolution rationale and reviewer record.

!!! tip "Cross-Reference"
    AI-agent-misuse policy templates and tuning (false-positive analysis, indicator weights) are owned by [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md). Recurring false positives observed in case work must be routed back to 1.12 for tuning; do not edit policy from this walkthrough.

## 5. Microsoft Purview eDiscovery (Premium) — Legal Hold and Regulator-Production Export

eDiscovery (Premium) is the surface where Control 3.4 issues **legal holds**, manages **custodian preservation**, captures **hold-notice acknowledgments**, and prepares **regulator-production exports**. The General Counsel (or designee) is the named owner of every hold; the Purview Compliance Admin executes the operational steps below.

### 5.1 Navigation

1. Sign in to the **Microsoft Purview portal** at [https://purview.microsoft.com](https://purview.microsoft.com) with **eDiscovery Manager** activated.
2. From the left nav, expand **Solutions → eDiscovery → Premium**.
3. Confirm the case from §4.6 (or create a new case if the hold is not IRM-originated — proceed to §5.2).

### 5.2 Creating an eDiscovery (Premium) case directly

For incidents that do **not** route through IRM (e.g., a Defender XDR-only correlated incident with an immediate hold need):

1. Click **+ Create a case**.
2. Enter:
    - **Case name** — prepend the firm incident ID.
    - **Case description** — link to the Defender XDR and Sentinel incident IDs.
    - **Case format** — **New case format** (recommended; legacy classic eDiscovery is being retired).
3. Click **Save**.
4. Confirm the case appears in the cases list with **Status = Active** and **Owner = <your UPN>**.

### 5.3 Adding custodians and creating a legal hold

1. Inside the case, navigate to **Data sources → + Add data sources → Add new custodians**.
2. For each custodian:
    - Enter the **UPN** (or pick from the directory).
    - Confirm the auto-included **data sources** — Exchange mailbox, OneDrive site, Teams chat (1:1 and group). Add **SharePoint sites** and **Teams team mailboxes** explicitly where relevant.
    - For AI-agent incidents, additionally include the **Copilot interaction history container** (where surfaced) and the agent's **Copilot Studio environment** as a SharePoint site reference.
3. Click **Next**, review the data sources summary, and click **Submit**.
4. Navigate to **Holds → + Create**.
5. In the **Create hold** wizard:
    - **Name and description** — prepend the firm incident ID; description must reference the legal-hold notice ID issued by General Counsel.
    - **Choose data sources** — select the custodian set added above.
    - **Conditions** — leave blank for an unconditional hold (default; recommended for active incidents). Add **date range** or **keyword** conditions only if explicitly directed by General Counsel.
    - **Review and create** — confirm and click **Submit**.
6. Confirm the hold appears with **Status = On** and **Hold start time** populated.

!!! warning "Hold scope vs. retention scope"
    A hold created here **preserves** content for the duration of the hold and overrides any retention-policy deletion within scope. It does **not** create new retention obligations on its own — books-and-records retention is owned by [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md). Confirm with General Counsel that the hold scope satisfies the litigation / regulator preservation expectation for this incident — examiners may probe scope choices.

### 5.4 Hold-notice acknowledgments

1. Navigate to **Communications → + Create communication**.
2. In the wizard:
    - **Name and description** — `<INC-ID> — Legal Hold Notice — <Date>`.
    - **Communication template** — select the firm-approved hold-notice template (configured in advance by General Counsel; if missing, route to General Counsel before proceeding).
    - **Recipients** — auto-populated from the custodian list.
    - **Issuance, re-issuance, release notices** — keep all three turned **On** so the system tracks acknowledgment, periodic re-issuance, and release.
    - **Acknowledgment required** — **On**. The custodian must acknowledge within the hold-notice deadline (typically 5 business days).
3. Click **Send**.
4. Track acknowledgment status under **Communications → <notice> → Recipients**. Non-acknowledgment after the deadline is a **finding**: route to General Counsel for follow-up; document the follow-up in the §1 register row.

### 5.5 Searches and review sets

For regulator-production preparation:

1. Navigate to **Searches → + New search**.
2. Configure the **search query** — KQL-style; typical queries:
    - For Reg S-P consumer notice: `(c:c)(date>=YYYY-MM-DD)(date<=YYYY-MM-DD)(participants:"<custodian>")`
    - For Copilot interaction history: include the Copilot interaction history scope and filter on the agent ID via metadata where supported.
3. Run the search; review **statistics** (item counts by location).
4. Click **Actions → Add to review set** → name the review set with the incident ID.
5. In the review set, apply **review-set queries** to triage to a producible set; tag responsive items with **Tag → Responsive** and privileged items with **Tag → Privileged — Withhold** (subject to General Counsel review).

### 5.6 Regulator-production export

1. From the review set, click **Action → Export**.
2. In the **Export** wizard:
    - **Export name** — `<INC-ID> — <Regulator> — <Date>`.
    - **Export options** — choose the production format the regulator requires (typically PDF + native + load file for SEC / FINRA productions; CSV summary for state AG productions).
    - **Include** — select **Tagged as Responsive**; **exclude** **Tagged as Privileged**.
    - **Conditional access** — leave defaults unless General Counsel directs otherwise.
3. Click **Export**.
4. Once the export job completes, download the export package via **Exports → <export name> → Download package**.
5. Hash the package (SHA-256), store the hash in the §1 register row, and transfer the package to the regulator-production secure-transfer location per the firm's regulator-production procedure (out of scope here).

### 5.7 Hold release

When the matter closes (incident closed AND no litigation pending AND General Counsel approves release):

1. Navigate to **Holds → <hold name> → Manage hold**.
2. Toggle **Status = Off**.
3. Confirm a **Release communication** is sent to custodians (auto-generated if §5.4 was configured with **Release notice = On**).
4. Document hold-release in the §1 register row with the release timestamp and General Counsel UPN.

!!! example "Examiner Evidence Box — eDiscovery (Premium)"
    **Capture for every incident with a hold:**

    1. Case-creation screenshot.
    2. Custodian list (CSV export from **Data sources**).
    3. Hold-creation screenshot with **Status = On** and start time.
    4. Hold-notice text and acknowledgment status export.
    5. Search query text and statistics screenshot.
    6. Review-set tag distribution screenshot.
    7. Export-package SHA-256 hash and transfer-receipt confirmation.
    8. Hold-release confirmation (where applicable) with General Counsel approval reference.

!!! tip "Cross-Reference"
    Audit-log retention sufficient to support eDiscovery searches is owned by [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md); retention labels on Copilot interaction history are owned by [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md). If a search returns zero results when results are expected, the issue is likely upstream in 1.7 / 1.9 rather than in eDiscovery.

## 6. Microsoft Purview Communication Compliance — Copilot Supervisory Escalation

**Communication Compliance** is the surface where Control 3.4 inherits supervisory escalations of **Copilot-generated content** that violates customer-communication policies. Examples include Copilot drafting an outbound email containing an unapproved performance projection, a non-compliant fee description, or a customer disclosure phrased outside the firm's compliance dictionary.

> Policy authoring (the Communication Compliance scopes that include Copilot-generated content) and supervisory program design are owned by [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md). Control 3.4 consumes Communication Compliance escalations at the alerts blade level only.

### 6.1 Navigation

1. Sign in to the **Microsoft Purview portal** at [https://purview.microsoft.com](https://purview.microsoft.com) with **Communication Compliance Investigators** activated.
2. From the left nav, expand **Solutions → Communication compliance**.
3. Select **Policies → <Copilot-scoped policy name>** to confirm the policy that fired (cross-ref Control 2.12 for the configuration).
4. Select **Alerts** to review.

### 6.2 Reviewing a Copilot-content alert

1. Filter alerts by **Policy = <Copilot policy>** and **Status = Pending**.
2. Click into an alert to open the alert detail blade.
3. Confirm the **Source** is identified as Copilot-generated (where the policy includes the `Copilot generated content` condition; if the source is not identified, the policy may need tuning under Control 2.12).
4. Review the **Message content** with the analyst's pseudonymization defaults applied (same model as IRM §4.2).
5. If the content was **sent externally** (email departed the tenant), this is a **higher-severity incident** that may trigger Reg S-P customer notice (if NPI was disclosed) and / or FINRA 4530(d) customer-complaint statistical aggregation (if a complaint follows). Cross-reference into the §1 register row.

### 6.3 Disposition and escalation

For each alert, choose one of:

| Disposition | Effect | Documentation requirement |
|-------------|--------|---------------------------|
| **Resolve** | Alert closed; no further action | Reviewer note required |
| **Notify the user** | Auto-notification sent to the user | Reviewer note + retained notice text |
| **Tag and notify** | Custom tag applied + notification sent | Reviewer note + tag rationale |
| **Escalate** | Alert escalated to a designated escalator (typically the Designated Series 24/66 Principal) | Reviewer note + escalation reason |
| **Escalate for investigation** | Creates an Advanced eDiscovery case (parallel to §5) | Reviewer note + IRM / eDiscovery linkage |
| **Remove message (where supported)** | Soft-delete from the recipient mailbox | Reviewer note + General Counsel concurrence |

For Control 3.4 active incidents, the typical disposition is **Escalate for investigation** with a back-link to the §1 register row.

### 6.4 Supervisory close-out by Designated Principal

Communication Compliance escalations involving registered persons require sign-off by the **Designated Series 24/66 Principal** (or applicable principal series for the line of business — Series 9/10, 26, 51, 53):

1. The escalator (typically the Communication Compliance Investigator) routes the escalation to the principal via Teams adaptive card (auto-generated by the §9 Power Automate flow `PB-Escalate-To-Series24`) or directly via the Purview UI.
2. The principal reviews the message, the user history, and the disposition options, then records the supervisory determination using a structured comment:

    ```
    SERIES24-REVIEW v1
    Alert: <Alert ID>
    Linked incident: <INC-ID>
    Reviewer (Series 24/66): <UPN>
    Determination: <Approved as sent | Required correction | Required clawback | Referred to HR | Referred to Compliance>
    Rationale: <free text>
    Linked supervisory file URI (Control 2.12): <URI>
    Reviewed at (UTC): <ISO timestamp>
    ```

3. The disposition is captured in the alert audit trail and mirrored into the firm's books-and-records system (Control 1.7 / 1.9).

!!! example "Examiner Evidence Box — Communication Compliance"
    **Capture for every incident with a Copilot-content escalation:**

    1. Alert-list screenshot filtered to the Copilot-scoped policy in the incident window.
    2. Alert-detail screenshot for each escalated alert.
    3. Disposition record with reviewer UPN.
    4. Series 24/66 principal review comment text.
    5. Cross-reference URI to the Control 2.12 supervisory file.

!!! tip "Cross-Reference"
    Communication Compliance policies are authored under [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md). DLP and sensitivity-label scopes that interact with Copilot content are owned by [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md). Recurring false positives must be routed to 2.12 for tuning.

## 7. Microsoft 365 Service Health — Microsoft-Side Correlation Gate

**Before** declaring a firm-side root cause for any Sev-1 / Sev-2 incident — and **especially** before initiating any regulator notification clock — the Incident Commander must check **Microsoft 365 Service Health** for any concurrent Microsoft-side advisory or incident that could explain the observed behavior. A regulator notification triggered by what turns out to be a Microsoft outage that the firm did not investigate is itself a finding under FFIEC Information Security and BCM expectations.

### 7.1 Navigation

1. Sign in to the **Microsoft 365 admin center** at [https://admin.microsoft.com](https://admin.microsoft.com) with **Service Support Administrator** or **M365 Admin** activated (read-only is sufficient for the check; status updates require Service Support Administrator).
2. From the left nav, expand **Health → Service health**.
3. The default view is **All services**.

### 7.2 Filtering for relevant services

For an AI-agent incident, the relevant service set is:

- **Microsoft 365 Apps** (Word, Excel, PowerPoint with Copilot)
- **Microsoft Copilot**
- **Microsoft Teams**
- **Microsoft Purview**
- **Microsoft Defender XDR**
- **Power Platform** (Copilot Studio, Power Apps, Power Automate)
- **Exchange Online**
- **SharePoint Online**
- **Microsoft Entra ID**

Click each service row to view active **Issues** and **Advisories**.

### 7.3 Recording the check as evidence

For each in-scope service:

1. Capture a screenshot of the service-detail blade showing the **"Issues" and "Advisories" count** (zero or non-zero) and the **last-updated timestamp**.
2. If the count is **non-zero**, click into each issue / advisory and:
    - Record the **issue ID** (e.g., `MO123456`).
    - Record the **title** and **summary**.
    - Record the **user impact** statement.
    - Record the **scope** (whether the firm's tenant is in the impacted set).
3. If a Microsoft-side issue plausibly correlates with the firm-side observed behavior, **pause** the clock-starting decision and document the correlation hypothesis in the §1 register row's `RootCauseStatement` field as **provisional**. Do **not** initiate regulator notifications based on a Microsoft-side issue without first ruling it out as the proximate cause.
4. If no Microsoft-side correlation is found, capture a screenshot showing **zero issues / advisories** for the in-scope services as the negative-evidence artifact.

### 7.4 Service Health history

For incidents whose detection T0 is more than 7 days in the past, also check the **Service Health → History** tab for the relevant period — Microsoft archives advisories after resolution and the firm needs the historical view for retrospective root-cause analysis.

!!! example "Examiner Evidence Box — Service Health correlation"
    **Capture for every Sev-1 / Sev-2 incident:**

    1. Service Health all-services screenshot at incident T0+1h, T0+24h, and at root-cause-determination.
    2. Per-service screenshots for each in-scope service.
    3. For any non-zero issue / advisory: issue ID, title, summary, user impact, scope, and the firm's correlation determination.
    4. Negative-evidence screenshot where applicable.

!!! warning "Do not skip the Service Health gate"
    A regulator notification filed for what turns out to be a Microsoft-side outage (without the firm having first investigated and ruled out the Microsoft-side cause) creates examiner risk under FFIEC IT Handbook expectations and may also create class-action plaintiff risk. The Service Health gate is a five-minute check — do not skip it.

## 8. SharePoint Incident Response List — Authoritative Firm Record

The **SharePoint IR list** is the firm's authoritative incident record outside the security tools. It is the reference of truth for the §1 manual register, the source for the §9 Power Automate notification flows, and the artifact most frequently requested by examiners as the single-pane view of an incident.

### 8.1 Site setup (one-time)

1. Sign in to the **SharePoint admin center** at `https://<tenant>-admin.sharepoint.com` with **SharePoint Administrator** activated.
2. Navigate to **Sites → Active sites → + Create → Team site (no group)** (or use a pre-provisioned IR site if the firm template exists).
3. Configure the site:
    - **Site name** — `IR — Incident Response Register` (use a stable, well-known name).
    - **Privacy** — Private.
    - **Sensitivity label** — apply the **Highly Confidential — Restricted** label (Control 1.5).
    - **Owners** — CISO, CCO, General Counsel (group), AI Governance Lead.
    - **Members** — Incident Commanders, SOC Analysts, Sentinel Admins, Privacy Officer, Disclosure Committee chair.
4. Mark the site as **legal-hold-aware** by:
    - Applying a **Purview retention label** to the site that requires retention for the books-and-records minimum (typically 6 years from item creation; confirm with General Counsel).
    - Adding the site to the standing **eDiscovery (Premium) preservation** maintained for IR records.
5. Confirm **versioning** is enabled at the list level (default: 500 major versions).

### 8.2 List creation

1. From the IR site home, click **+ New → List → Blank list**.
2. **Name** — `Incidents`.
3. Add columns per the schema below (use **+ Add column** for each; column types in parentheses):

| # | Column | Type | Required | Notes |
|---|--------|------|----------|-------|
| 1 | `IncidentID` | Single line of text | Yes | Format `INC-FSI-YYYY-NNNN`; see §1.2 |
| 2 | `Title` | Single line of text | Yes | Short, factual |
| 3 | `Severity` | Choice | Yes | Sev-1 / Sev-2 / Sev-3 / Sev-4 |
| 4 | `Status` | Choice | Yes | New / Triage / Investigating / Containing / Eradicating / Recovering / Closed |
| 5 | `DetectionUTC` | Date and time | Yes | T0 |
| 6 | `DeclarationUTC` | Date and time | No | Sev-elevation timestamp |
| 7 | `ContainmentUTC` | Date and time | No | |
| 8 | `EradicationUTC` | Date and time | No | |
| 9 | `RecoveryUTC` | Date and time | No | |
| 10 | `ClosureUTC` | Date and time | No | |
| 11 | `MaterialityDeterminationUTC` | Date and time | No | 8-K Item 1.05 trigger; see §10 |
| 12 | `MaterialityOutcome` | Choice | No | Material / Not Material / Not Yet Determined |
| 13 | `IncidentCommander` | Person | Yes | |
| 14 | `LegalLead` | Person | Yes | General Counsel designee |
| 15 | `ComplianceLead` | Person | Yes | CCO designee |
| 16 | `BCMLead` | Person | No | Business Continuity Officer |
| 17 | `DefenderXDRIncidentID` | Single line of text | No | |
| 18 | `SentinelIncidentID` | Single line of text | No | |
| 19 | `IRMCaseID` | Single line of text | No | |
| 20 | `eDiscoveryCaseID` | Single line of text | No | |
| 21 | `LegalHoldID` | Single line of text | No | |
| 22 | `AffectedAgentIDs` | Multiple lines of text | No | One agent per line |
| 23 | `AffectedUserCount` | Number | No | For Reg S-P scope sizing |
| 24 | `NPIDisclosed` | Choice | No | Yes / No / Unknown |
| 25 | `RootCauseStatement` | Multiple lines of text | No | Provisional → Final |
| 26 | `RegulatorNotificationsRequired` | Multiple lines of text | No | One per line; see §1.3 |
| 27 | `RegulatorNotificationsSent` | Multiple lines of text | No | One per line; ISO timestamp + filer UPN |
| 28 | `EvidencePackageURI` | Hyperlink | No | SharePoint folder URI |
| 29 | `EvidencePackageSHA256` | Single line of text | No | |
| 30 | `OFACScreeningOutcome` | Choice | No | Not Applicable / Cleared / Hit — Escalated |

4. Configure **views**:
    - **All Active** — filter `Status ≠ Closed`; sort by `Severity` ascending then `DetectionUTC` ascending.
    - **Reg-Notice Watchlist** — filter `RegulatorNotificationsRequired ≠ blank` AND `Status ≠ Closed`; sort by oldest `DetectionUTC` first.
    - **Disclosure-Committee Queue** — filter `MaterialityOutcome = Not Yet Determined`; ordered by oldest first.
    - **Closed Last 30 Days** — filter `Status = Closed` AND `ClosureUTC` within 30 days.

### 8.3 Per-incident folder convention

For each new IncidentID, create a sibling folder in the same site under **Documents → Incidents → <IncidentID>** with sub-folders:

```
<IncidentID>/
    01-defender-xdr/
    02-sentinel/
    03-irm/
    04-edisco/
    05-comm-compliance/
    06-service-health/
    07-materiality/
    08-ofac/
    09-regulator-notices/
    10-bcm-comms/
    11-tabletop-references/
    99-final-evidence-pack/
```

Each sub-folder receives the screenshots and exports captured per the section's Examiner Evidence Box. The `99-final-evidence-pack/` folder is the consolidated, hashed package referenced in §14.

### 8.4 Permissions and audit

1. Confirm **list-level permissions** restrict edit to the IR site members; restrict delete to site owners only (custom permission level: `IR-Contribute-NoDelete`).
2. Confirm **audit logging** at the site is captured under [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — every list edit must produce an audit record.
3. Confirm the site is included in the standing eDiscovery preservation per §8.1.

!!! example "Examiner Evidence Box — SharePoint IR list"
    **Capture annually plus per-incident:**

    1. Site permissions report (annual).
    2. Retention-label assignment confirmation (annual).
    3. List schema export (annual; CSV of column definitions).
    4. Per-incident: list-item version history export from open through close.

## 9. Power Automate — Notification Flows and Per-Regulator Timer Countdowns

Power Automate provides the **timer countdowns**, **internal SLA breach alerts**, and **Teams adaptive-card escalations** that drive incident-response cadence. Flows here do not file regulator notices automatically — every regulator notice is a **human-in-the-loop** action by General Counsel or designee — but flows surface the deadline and route the approval.

### 9.1 Navigation

1. Sign in to **Power Automate** at [https://make.powerautomate.com](https://make.powerautomate.com) with **Power Platform Admin** activated and the IR-flows environment selected.
2. From the left nav, expand **Solutions → IR Notification Flows** (the firm-managed solution housing the flows below).

### 9.2 Flow inventory

The following flows are in scope. Each flow is created from a SharePoint trigger on the §8 Incidents list and emits one or more Teams adaptive cards plus list-item updates.

| Flow name | Trigger | Action | Owner |
|-----------|---------|--------|-------|
| `IR-Timer-NYDFS-72h` | List item created where `RegulatorNotificationsRequired` contains `NYDFS-72h` | Countdown to T0+72h; alert at T0+24h, T0+48h, T0+60h, T0+71h; final alert at T0+72h to General Counsel | Power Platform Admin |
| `IR-Timer-NYDFS-24h-Ransom` | List item updated where `OFACScreeningOutcome = Cleared` AND ransom-payment context | Countdown to T0+24h from extortion-payment decision; per-hour alerts after T+12h | Power Platform Admin |
| `IR-Timer-Banking-36h` | List item created where `RegulatorNotificationsRequired` contains `Banking-36h` | Countdown to T0+36h from Notification Incident determination; alerts at T0+12h, T0+24h, T0+30h, T0+35h | Power Platform Admin |
| `IR-Timer-SEC-8K-4bd` | List item updated where `MaterialityOutcome = Material` | Countdown to material-determination + 4 business days; alerts at +1bd, +2bd, +3bd, +3.5bd | Power Platform Admin |
| `IR-Timer-RegSP-30d` | List item updated where `NPIDisclosed = Yes` | Countdown to T0+30 days; alerts at T0+15d, T0+25d, T0+29d | Power Platform Admin |
| `IR-Timer-RegSP-72h-FTC` | List item updated where `NPIDisclosed = Yes` AND FTC notification required | Countdown to T0+72h; alerts at T0+24h, T0+48h, T0+71h | Power Platform Admin |
| `IR-Timer-FINRA-4530a-30d` | List item updated where `RegulatorNotificationsRequired` contains `FINRA-4530a-30d` | Countdown to triggering-event + 30 days; alerts at +15d, +25d, +29d | Power Platform Admin |
| `IR-Timer-CISA-CIRCIA` | List item updated where `RegulatorNotificationsRequired` contains `CISA-CIRCIA` | Countdown applicable per final rule effective date; placeholder until final rule is in effect | Power Platform Admin |
| `IR-Card-Disclosure-Committee` | List item updated where `MaterialityDeterminationUTC` is not blank for the first time | Adaptive card to Disclosure Committee distribution list; sets `MaterialityOutcome = Not Yet Determined` if blank | Power Platform Admin |
| `IR-Card-Series24-Escalate` | List item updated where Communication Compliance escalation linked | Adaptive card to Designated Series 24/66 Principal | Power Platform Admin |
| `IR-Card-OFAC-Escalate` | List item updated where ransom-payment context tagged | Adaptive card to General Counsel + Treasury for OFAC pre-screen (see §11) | Power Platform Admin |

### 9.3 Walkthrough — `IR-Timer-NYDFS-72h` (representative pattern)

1. From the IR Notification Flows solution, click **+ New → Automated cloud flow**.
2. **Flow name** — `IR-Timer-NYDFS-72h`.
3. **Trigger** — `When an item is created (SharePoint)`.
    - **Site Address** — IR site URL.
    - **List Name** — `Incidents`.
4. Add a **Condition** — `triggerOutputs()?['body/RegulatorNotificationsRequired']` contains `NYDFS-72h`. **No** branch — terminate.
5. **Yes** branch — add a sequence of **Delay until** + **Send adaptive card to Teams chat** actions:
    - Delay until `addHours(triggerOutputs()?['body/DetectionUTC'], 24)` → card to General Counsel: "NYDFS 72h clock at +24h. <link to list item>. Recommended action: confirm Covered Entity determination."
    - Delay until `addHours(triggerOutputs()?['body/DetectionUTC'], 48)` → card to General Counsel + CISO: "NYDFS 72h clock at +48h. Confirm draft notification status."
    - Delay until `addHours(triggerOutputs()?['body/DetectionUTC'], 60)` → card to General Counsel + CISO + CCO: "NYDFS 72h clock at +60h. 12 hours remain."
    - Delay until `addHours(triggerOutputs()?['body/DetectionUTC'], 71)` → card to General Counsel + CISO + CCO + AI Governance Lead: "NYDFS 72h clock at +71h. **One hour remains.**"
    - Delay until `addHours(triggerOutputs()?['body/DetectionUTC'], 72)` → card to all-hands distribution: "**NYDFS 72h DEADLINE REACHED**. Capture filed-or-withheld determination in `RegulatorNotificationsSent`."
6. Add an **Update item** action (final) that appends an entry to `RegulatorNotificationsSent` capturing whether the 72h clock was met (manually filled by General Counsel; the flow simply marks the deadline-reached event).
7. **Save** and **Test** with a synthetic list item.

!!! warning "Flows do not file notices"
    The flows here are **deadline-surface** flows. They do **not** transmit anything to a regulator portal. Every regulator notice is filed by General Counsel (or designee) through the regulator's own portal (§13). Filing automation is explicitly out of scope and would create unacceptable legal exposure.

### 9.4 Run-history retention

1. From each flow's overview page, capture the **28-day run history** weekly to a CSV stored in the IR evidence folder (the §8.3 `08-ofac/` and `09-regulator-notices/` folders for the relevant flows).
2. Configure the host environment's **Activity logging** so flow runs land in Purview Audit (Control 1.7).

### 9.5 Secrets

Flows that send adaptive cards require no secrets. Any flow that integrates with external systems (e.g., a regulator-portal helper) **must** use Azure Key Vault references via the Power Platform connector — **never** inline secrets. See [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) for the platform identity model.

!!! example "Examiner Evidence Box — Power Automate"
    **Capture for every flow, monthly:**

    1. Flow definition export (zip from **Export → Package**).
    2. 28-day run history CSV.
    3. Last successful test-run record per flow.
    4. Owner attestation that no inline secrets are used.

## 10. Materiality Determination — SEC 8-K Item 1.05 Workflow

For SEC registrants, **Item 1.05 of Form 8-K** requires disclosure of a **material cybersecurity incident** within **four business days** of the **materiality determination** (the determination date, **not** the discovery date, starts the clock). Control 3.4 operationalizes the determination through the **Disclosure Committee**, with General Counsel sign-off and a written memo retained in the IR site.

### 10.1 Trigger criteria

Initiate the materiality workflow when **any** of the following is true for a Sev-1 / Sev-2 incident:

- Confirmed unauthorized access to systems containing material non-public information.
- Confirmed exfiltration of customer NPI affecting a material number of customers (per the firm's pre-defined materiality threshold; consult General Counsel).
- Operational disruption affecting a material business line for more than the firm's pre-defined disruption-materiality window.
- Confirmed integrity compromise of an AI agent that produces customer-facing output for a material business line.
- Any incident with reasonably foreseeable material impact on the firm's operations, financial condition, or reputation.

The materiality threshold is **firm-specific**; the Disclosure Committee owns the threshold and reviews it annually. Implementation requires the firm's Disclosure Committee to ratify a written materiality framework that this workflow operationalizes.

### 10.2 Disclosure Committee meeting

1. The Incident Commander emails the **Disclosure Committee chair** (typically the General Counsel or CFO) with the §1 register row link and a one-page incident summary.
2. The chair convenes the Disclosure Committee within the firm's pre-defined response SLA (recommended: within 24 hours of trigger criteria being met).
3. The meeting agenda is recorded using the structured template:

    ```
    DISCLOSURE-COMMITTEE-MEETING v1
    Incident: <INC-ID>
    Meeting at (UTC): <ISO timestamp>
    Chair: <UPN>
    Attendees: <UPNs — must include CISO, CCO, GC, CFO or designees>
    Outside counsel present: <Yes — Firm | No>
    Materiality framework version reviewed: <vN.N>
    Facts presented:
      - <bullet list — what is known with confidence>
    Facts unknown:
      - <bullet list — what is unknown / under investigation>
    Reasonably likely impact assessment (qualitative + quantitative where available):
      - <text>
    Materiality determination: <Material | Not Material | Defer — re-convene at <UTC>>
    Determination rationale: <free text — link to evidence>
    Determined at (UTC): <ISO timestamp — this starts the 4-bd clock if Material>
    Next review (if Defer): <UTC>
    ```

4. The chair records the outcome in the §8 list `MaterialityOutcome` and `MaterialityDeterminationUTC` columns.
5. If the determination is **Material**, the §9 `IR-Timer-SEC-8K-4bd` flow auto-engages.

### 10.3 Drafting the 8-K Item 1.05

The 8-K drafting itself is a **Legal / outside counsel / Investor Relations** workstream and is out of scope for this walkthrough. From the IR-process side:

1. The Incident Commander provides the **technical narrative** (what is known, what is unknown, scope, impact, remediation status) to General Counsel using the firm's 8-K technical-narrative template.
2. The narrative is updated as facts evolve and re-shared with General Counsel within 24 hours of any material change.
3. The Incident Commander does **not** review or edit the 8-K text itself.

### 10.4 Amended 8-K (Item 1.05(c))

When facts change after an initial 8-K is filed, **Item 1.05(c)** requires an **amended 8-K** within four business days of when the firm becomes aware of the new facts. The firm's standing materiality framework should specify the categories of change that trigger amendment (e.g., material change in scope of impacted customers, identification of additional impacted business lines, attribution of the threat actor with material implications).

!!! warning "8-K is the regulator-facing artifact, not a substitute for OCC / Fed / FDIC notice"
    For dual-regulated firms (e.g., a bank holding company that is also an SEC registrant), the **8-K does not satisfy** the **36-hour Notification Incident** requirement to the primary banking regulator (12 CFR Part 53 / 304 / 225). The two clocks run independently and require independent filings.

!!! example "Examiner Evidence Box — Materiality"
    **Capture for every Sev-1 / Sev-2 incident (whether or not Material):**

    1. Disclosure Committee meeting record (structured template above).
    2. Materiality framework version referenced.
    3. Determination outcome with rationale.
    4. Where Material: 4-bd clock-start UTC and confirmation of `IR-Timer-SEC-8K-4bd` engagement.
    5. Where Defer: re-convene UTC and the eventual final determination record.

!!! tip "Cross-Reference"
    Model-risk implications of a Material AI-agent incident (e.g., model retirement triggers under SR 11-7) are owned by [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md). A Material AI-agent integrity incident typically triggers MRM challenge re-validation in addition to disclosure obligations.

## 11. OFAC Sanctions Screening — Pre-Payment Gate for Extortion Demands

!!! danger "OFAC pre-payment screening is mandatory before any extortion / ransom payment"
    Making a ransom or extortion payment to a person, entity, or jurisdiction on the **OFAC Specially Designated Nationals (SDN) List**, in a **comprehensively sanctioned jurisdiction** (e.g., Iran, North Korea, Cuba, Syria, the Crimea / DNR / LNR regions of Ukraine), or otherwise blocked under an OFAC sanctions program, **is a strict-liability violation of US sanctions law** regardless of the payer's knowledge or intent. Penalties include civil penalties up to the greater of approximately **USD 368,136 per violation or twice the transaction value** (statutory amounts are inflation-adjusted; consult OFAC's current civil-penalty matrix), criminal penalties for willful violations, and reputational and licensing consequences. The OFAC 2020 advisory (updated September 2021) on **"Potential Sanctions Risks for Facilitating Ransomware Payments"** further articulates expected due diligence including timely reporting to OFAC, CISA, FBI, and Treasury FinCEN. **No payment may be authorized without documented OFAC pre-screening and General Counsel approval.** This walkthrough does not provide legal advice; consult sanctions counsel for every extortion-payment scenario.

### 11.1 Trigger

A pre-payment OFAC screening is initiated when **all** of the following are true:

1. The incident involves an extortion demand (e.g., ransomware encryption note, data-leak extortion, denial-of-service extortion).
2. The Incident Commander has documented the demand details (cryptocurrency address or payment instructions, demanded amount, deadline, communication channel, threat actor self-identification).
3. The CISO and General Counsel have begun considering payment as one option (which does **not** mean payment will be made).

The §9 `IR-Card-OFAC-Escalate` flow auto-fires the moment the §8 list item is tagged with the ransom-payment context.

### 11.2 Workflow

1. The General Counsel convenes the **Sanctions Review** with the following participants (recommended): General Counsel (chair), CCO, CISO, Treasurer, outside sanctions counsel, and the firm's third-party incident-response retainer (where one exists).
2. The Sanctions Review records the following using the structured template:

    ```
    OFAC-PRESCREEN v1
    Incident: <INC-ID>
    Convened at (UTC): <ISO timestamp>
    Chair (General Counsel): <UPN>
    Outside sanctions counsel: <Firm | None — explain>
    Demand details:
      - Cryptocurrency address(es): <list>
      - Demand amount: <amount + currency>
      - Demand deadline (UTC): <ISO>
      - Threat actor self-identification: <name / group / unknown>
    Attribution evidence reviewed: <bullet list>
    OFAC SDN List screening — addresses: <Cleared | Hit — details>
    OFAC SDN List screening — actor names / aliases: <Cleared | Hit — details>
    Comprehensively sanctioned jurisdiction nexus: <None | Possible — explain>
    OFAC Cyber-related sanctions program nexus (E.O. 13694 / 13757): <None | Possible — explain>
    Treasury FinCEN financial-institution-customer screening (where applicable): <Cleared | Hit>
    Determination: <Cleared to consider payment | Blocked — payment prohibited | Defer — additional inquiry needed>
    Determination rationale: <free text>
    Determined at (UTC): <ISO timestamp>
    Notifications planned (independent of payment decision): <OFAC | CISA | FBI | Treasury FinCEN | NYDFS-24h-Ransom | other>
    ```

3. The determination is recorded in the §8 list `OFACScreeningOutcome` column.
4. **If Blocked**, no payment may be authorized; the Incident Commander documents the decision and the firm's response continues without payment. Notifications proceed independent of the payment decision.
5. **If Cleared**, payment authorization remains a separate decision by the firm's executive leadership / board (per the firm's payment-authorization policy); a **Cleared** OFAC determination is necessary but not sufficient for payment.
6. **In all ransom-extortion scenarios** (regardless of payment), evaluate notifications to:
    - **OFAC** voluntary self-disclosure (where any sanctions-nexus risk is identified).
    - **CISA** under the firm's cyber-incident reporting practice (and CIRCIA when in effect).
    - **FBI** Internet Crime Complaint Center (IC3) and / or local field office.
    - **Treasury FinCEN** Suspicious Activity Report where the firm is a financial-institution covered person.
    - **NYDFS** within 24 hours of any extortion payment under 23 NYCRR 500.17(c) (separate from the 72-hour cybersecurity event notification).
    - State-level notifications per state-AG playbooks.

### 11.3 Sanctions screening tool

The screening itself is performed against the **OFAC Sanctions List Search** at [https://sanctionssearch.ofac.treas.gov](https://sanctionssearch.ofac.treas.gov) **and** any commercial sanctions-screening tool the firm maintains. Capture screenshots of every search performed (search term, date / time, result count, and full result text where any match is returned).

!!! warning "Screening is not legal advice"
    The OFAC Sanctions List Search produces **search results**; it does **not** produce a **determination**. The determination is a legal judgment by General Counsel and outside sanctions counsel based on the search results, the firm's broader knowledge, and the totality of available attribution evidence. Implementation requires an experienced sanctions-counsel relationship; firms without such a relationship should establish one before an incident occurs.

!!! example "Examiner Evidence Box — OFAC pre-screen"
    **Capture for every ransom-extortion incident:**

    1. Sanctions Review convening record with attendees.
    2. Structured `OFAC-PRESCREEN v1` template.
    3. Sanctions Search screenshots (all queries, with timestamps).
    4. Outside sanctions-counsel sign-off (email or memo).
    5. Final determination and rationale.
    6. Notifications planned and filed.

## 12. Tabletop Exercise Harness — Quarterly AI-Specific Scenarios

Tabletop exercises validate the IR plan against realistic scenarios, develop muscle memory across the cross-functional team, and produce examiner-evidence of program maturity. For Control 3.4, exercises are conducted **quarterly** with at least one AI-agent-specific scenario per quarter.

### 12.1 Cadence and ownership

| Cadence | Type | Owner | Approver |
|---------|------|-------|----------|
| Quarterly | Tabletop (2-3 hours, discussion-based) | AI Governance Lead | CISO + CCO + General Counsel |
| Annually | Functional exercise (4-6 hours, hands-on portal navigation) | CISO | Board Risk Committee |
| Biennially | Full-scale exercise (1-2 days, includes BCM activation) | Business Continuity Officer | Board Risk Committee |

### 12.2 AI-specific scenario library

Rotate across the following scenarios (minimum one per quarter):

| Scenario | Primary regulators in scope | Key controls exercised |
|----------|------------------------------|-----------------------|
| **Prompt-injection-driven exfiltration** — A threat actor seeds a SharePoint document with hidden instructions that cause a Copilot agent to summarize NPI from adjacent files into a draft email destined for an external recipient. | NYDFS, Reg S-P, FTC, state BNs, FINRA 4530 if registered persons involved | 1.5, 1.7, 1.8, 1.12, 2.12, 3.4 |
| **Hallucinated customer communication** — A Copilot-drafted client email cites a non-existent prospectus footnote and quotes an inaccurate yield. Email was sent before supervisory review. | FINRA 2210 / 3110, SEC Marketing Rule | 1.5, 2.12, 3.4 |
| **Runaway agent on stale context** — A scheduled agent continues to act on a stale grounding source after the source was revised; produces materially out-of-date risk reports for trading desks. | FINRA 3110 supervisory failure; potential Material 8-K depending on impact | 1.7, 1.9, 2.6, 2.12, 3.4 |
| **Orphaned-agent cascade** — A maker leaves the firm; their orphaned Copilot agents continue to run and accumulate signals an attacker exploits to pivot. Cross-references [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md). | NYDFS, Banking 36h, potential Material 8-K | 1.11, 2.25, 3.4, 3.6 |
| **Insider exfiltration via Copilot** — Departing financial advisor uses Copilot to collate client lists into a single export. | Reg S-P, state BNs, Protocol for Broker Recruiting if applicable | 1.5, 1.12, 2.12, 3.4 |
| **Ransomware with extortion of agent training data** — Threat actor encrypts and threatens to leak the firm's fine-tuning corpus (which contains NPI). | NYDFS-24h-Ransom, Reg S-P, FTC, OFAC pre-screen | 1.7, 1.8, 1.9, 3.4 (incl. §11) |
| **Third-party Copilot connector compromise** — An ISV-provided Copilot connector is compromised upstream; the firm's data accessed via the connector is potentially exfiltrated. | Reg S-P, NYDFS third-party-service-provider provisions, banking 36h | 1.5, 1.8, 2.6, 3.4 |
| **MRM-triggering integrity incident** — A Copilot agent used in a credit-decisioning workflow is shown to drift outside its validated boundaries. | OCC 2011-12 / SR 11-7 escalation, fair-lending considerations | 2.6, 3.4 |

### 12.3 Exercise structure

Each tabletop follows this structure:

1. **Pre-read distribution** (T-7 days) — scenario summary (1-2 pages), participant roles, expected duration, and the specific portal blades that will be referenced.
2. **Scenario setup** (15 min) — scenario lead reads the initial situation; clock T0 is established.
3. **Injects** (90-120 min) — scenario lead delivers 5-7 injects (new facts that change the picture) at intervals; participants respond by describing the actions they would take, the portal blades they would open, and the artifacts they would capture.
4. **Materiality and notification decisions** (20-30 min) — Disclosure Committee role-play; OFAC pre-screen role-play if scenario warrants.
5. **Hot wash** (20-30 min) — facilitated debrief; capture findings, follow-ups, and proposed plan changes.
6. **After-action report** (T+5 days) — written report with findings rated as Strength / Opportunity / Gap; Gap items become tracked work in the IR site.

### 12.4 After-action report template

```
TABLETOP-AAR v1
Exercise name: <name>
Date (UTC): <ISO>
Scenario: <library name + version>
Facilitator: <UPN>
Participants: <UPNs by role>
Duration (actual): <hh:mm>
Findings:
  - <ID>: <Strength|Opportunity|Gap> — <description>
    Owner: <UPN>
    Target close: <date>
    Linked control(s): <list>
Recommendations to plan:
  - <bullet list>
Approvals:
  - CISO sign-off: <UPN at UTC>
  - CCO sign-off: <UPN at UTC>
  - General Counsel sign-off: <UPN at UTC>
```

### 12.5 Evidence retention

Tabletop materials (pre-read, scenario script, inject log, AAR) are retained in the IR site under **Documents → Tabletops → <YYYY-QN — scenario>** and are part of the standard examiner packet (§14). Examiners frequently sample tabletop materials to assess program maturity.

!!! example "Examiner Evidence Box — Tabletops"
    **Capture per exercise plus annually:**

    1. Annual exercise calendar with planned scenarios.
    2. Per-exercise pre-read, attendance log, inject log, AAR.
    3. Gap-finding tracker showing close-out status.
    4. Board Risk Committee briefing materials referencing exercise outcomes (annual).

!!! tip "Cross-Reference"
    Tabletop scenarios that exercise orphaned-agent cascade should align with [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md). Scenarios that exercise MRM escalation should align with [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md). Scenarios that exercise supervisory escalation should align with [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).

## 13. Regulator Portal References

Filing notices is performed through regulator-operated portals. The portal references below are provided for orientation only; URLs and submission flows are subject to change without notice and the firm's General Counsel is responsible for confirming the current submission requirements at the time of filing.

| Regulator | Portal | Filing artifact | Owner |
|-----------|--------|-----------------|-------|
| **NYDFS** | DFS Cybersecurity Portal at [https://myportal.dfs.ny.gov](https://myportal.dfs.ny.gov) | 23 NYCRR 500.17(a) Cybersecurity Event Notification (72h); 500.17(c) Extortion Payment Notification (24h) and Written Statement (30d); annual 500.17(b) certification / acknowledgment of noncompliance | General Counsel |
| **SEC** | EDGAR at [https://www.sec.gov/edgar](https://www.sec.gov/edgar) | Form 8-K Item 1.05 (4 business days from materiality); amendment via Item 1.05(c) | General Counsel + Outside Counsel + IR |
| **SEC (Reg S-P)** | Filing model varies by registrant type; consult counsel | Customer notice of unauthorized access or use of customer information (30 days as amended); Federal law-enforcement notice (FBI / Secret Service) and to the SEC at [https://www.sec.gov](https://www.sec.gov) per program | General Counsel |
| **FINRA** | Firm Gateway at [https://firms.finra.org](https://firms.finra.org) | Rule 4530(a) and 4530(d) reporting; Rule 4530(f) quarterly statistical aggregation of customer complaints | CCO + Designated Series 24/66 Principal |
| **OCC** | BankNet at [https://www.banknet.gov](https://www.banknet.gov) | 12 CFR Part 53 Notification Incident (36h to primary federal regulator) | General Counsel + CCO |
| **Federal Reserve** | E-Apps at [https://www.federalreserve.gov](https://www.federalreserve.gov) and Reserve Bank contact | 12 CFR Part 225 Notification Incident (36h) | General Counsel + CCO |
| **FDIC** | FDICconnect at [https://www.fdicconnect.gov](https://www.fdicconnect.gov) | 12 CFR Part 304 Notification Incident (36h) | General Counsel + CCO |
| **NCUA** | NCUA Secure Mail and the Cyber Incident Notification page at [https://ncua.gov](https://ncua.gov) | 12 CFR Part 748 Cyber Incident Notification (72h, federally insured credit unions) | General Counsel + CCO (credit unions only) |
| **CFTC** | CFTC Portal at [https://portal.cftc.gov](https://portal.cftc.gov) | Notice obligations under Part 3, Part 23 (swap dealers), and the firm's specific registration program | General Counsel + CCO (for CFTC registrants) |
| **FTC** | Online complaint form at [https://www.ftc.gov](https://www.ftc.gov) | Safeguards Rule notification (16 CFR 314.5 — 30 days for incidents involving 500+ consumers) | General Counsel |
| **Treasury FinCEN** | BSA E-Filing at [https://bsaefiling.fincen.treas.gov](https://bsaefiling.fincen.treas.gov) | Suspicious Activity Report where applicable to financial-institution covered persons | BSA Officer |
| **OFAC** | OFAC Reporting at [https://ofac.treasury.gov](https://ofac.treasury.gov) | Voluntary self-disclosure where sanctions-nexus risk identified; blocked-property reports | General Counsel + Outside Sanctions Counsel |
| **CISA** | CISA Incident Reporting at [https://www.cisa.gov/report](https://www.cisa.gov/report) | Voluntary cyber-incident reporting today; CIRCIA reporting once final rule is in effect | CISO designee |
| **State AGs** | Each state operates its own portal or email channel | State breach-notification statutes (varies by state) — typically expedited for incidents involving state-resident NPI | General Counsel |
| **State financial regulators** | Each state operates its own portal | State-level licensing and consumer-protection notices (varies by state) | General Counsel + CCO |

!!! warning "Portal references are not legal advice"
    The portal table above is a navigation aid. The firm's General Counsel is responsible for confirming the current submission portal, the current submission format, and the current substantive requirements at the time of filing. Regulator portals and procedures change. Do not rely on this table as authoritative legal guidance.

## 14. Evidence Capture, Cadence, and Examiner Packet

### 14.1 Per-incident evidence pack

For every Sev-1 / Sev-2 incident, the **closure deliverable** is a consolidated, hashed evidence pack stored at `Documents → Incidents → <IncidentID> → 99-final-evidence-pack/` in the IR site. The pack consists of:

1. The §8 list-item version-history export (CSV).
2. All §1.3 register-row contents (PDF).
3. Defender XDR incident export (§2; structured comments included).
4. Sentinel incident export and automation-rule run logs (§3).
5. IRM case open / close exports (§4).
6. eDiscovery (Premium) case summary, hold list, hold-notice acknowledgments, search statistics, export-package SHA-256 hash (§5).
7. Communication Compliance disposition records (§6).
8. Service Health screenshots at T0+1h, T0+24h, root-cause-determination (§7).
9. Power Automate flow run-history CSVs spanning the incident window (§9).
10. Disclosure Committee meeting record (§10).
11. OFAC pre-screen record (§11) where applicable.
12. Regulator-notice copies and filing receipts (§13) where applicable.
13. Lessons-learned memo (signed by Incident Commander, CISO, CCO, General Counsel).

The pack is compressed to a single zip; SHA-256 is computed and recorded in the §8 list `EvidencePackageSHA256` column. The pack is retained per the firm's retention schedule (typically 7 years for SEC / FINRA registrants, 6 years for banking, longer where litigation hold applies).

### 14.2 Standing examiner packet

For ad-hoc examiner requests (e.g., NYDFS DFS examination, FINRA Rule 1017 examination, OCC continuous monitoring), maintain a **standing examiner packet** that is refreshed monthly at `Documents → Examiner-Packet/<YYYY-MM>/`:

| Artifact | Source section | Refresh cadence |
|----------|----------------|-----------------|
| IR plan (signed) | Out of scope here | Annually + on material change |
| IR site permissions report | §8.4 | Monthly |
| §1 register full export | §1 | Monthly |
| §8 schema export | §8.2 | Monthly + on change |
| Power Automate flow inventory | §9.2 | Monthly + on change |
| Flow run-history (28-day) for each flow | §9.4 | Monthly |
| Disclosure Committee charter and materiality framework | §10 | Annually + on change |
| OFAC sanctions-counsel relationship attestation | §11 | Annually |
| Tabletop calendar + last 12 months AARs | §12 | Quarterly |
| Regulator-portal access list (who has filer credentials) | §13 | Quarterly |
| Cross-reference matrix to Controls 1.5/1.7/1.8/1.9/1.11/1.12/2.6/2.12/2.25/3.6/3.9 | This file | Annually + on change |

### 14.3 Cadence summary

| Cadence | Activity |
|---------|----------|
| Continuous | §0 PIM activation per incident; §2 / §3 / §4 / §6 alert triage |
| Per incident | All sections relevant to the incident profile |
| Daily (during active incident) | §1 register update; §7 Service Health re-check; §9 flow-status review |
| Weekly | §9 flow run-history export |
| Monthly | §14.2 standing examiner packet refresh; §0 license-attestation refresh; §8.4 site permissions report |
| Quarterly | §12 tabletop exercise; §14.2 regulator-portal access review; §0 PIM eligibility review |
| Annually | §10 materiality framework review; §11 sanctions-counsel attestation; §12 annual functional exercise; full IR plan review and sign-off; §1 notification matrix review against current rules |

!!! example "Examiner Evidence Box — Annual program review"
    **Capture annually for board reporting:**

    1. Year-over-year incident-volume and severity-distribution charts.
    2. Mean time to detection / containment / closure per severity.
    3. Regulator-notification on-time rate (target: 100%).
    4. Tabletop completion rate and gap close-out rate.
    5. Cross-control finding rate (incidents that triggered tuning in 1.5/1.7/1.8/1.9/1.12/2.12/2.25).
    6. Board sign-off record on the annual IR program review.

## Closing Decision Matrix — Portal vs PowerShell vs Graph

For Control 3.4 operations, choose the surface based on the action profile below.

| Action profile | Surface | Why |
|----------------|---------|-----|
| Triage a live alert; make a containment / clock-start decision | **Portal** (this walkthrough) | Decisions require human judgment; portal provides full context (related entities, history, timeline) |
| Apply structured open / close comments on incidents and cases | **Portal** (this walkthrough) | Audit-trail attribution to the human reviewer is required |
| Author an IRM, eDiscovery, or Communication Compliance case | **Portal** (this walkthrough) | Wizard-driven flows enforce required fields |
| Review Service Health and capture screenshots | **Portal** (this walkthrough) | Microsoft does not expose a programmatic Service Health surface that meets evidence-capture requirements for Control 3.4 |
| Bulk export incident metadata for monthly examiner packet | **PowerShell** ([powershell-setup.md](./powershell-setup.md)) | Repeatable, scriptable, hash-stable |
| Bulk export Sentinel run-log evidence | **PowerShell** ([powershell-setup.md](./powershell-setup.md)) | Repeatable, scriptable |
| Programmatic enrichment / cross-tenant or cross-cloud queries | **Graph / REST APIs** | Not covered in this walkthrough |
| Provision the §8 SharePoint list schema across additional environments | **PowerShell** or **PnP PowerShell** ([powershell-setup.md](./powershell-setup.md)) | Repeatable, drift-detectable |
| Validation testing per release | **Verification testing** ([verification-testing.md](./verification-testing.md)) | Test cases and expected outcomes |
| Issue diagnosis | **Troubleshooting** ([troubleshooting.md](./troubleshooting.md)) | Common issues and resolutions |

## Final Readiness Checklist

Confirm every item before declaring Control 3.4 portal-side implementation **Ready**:

### Roles and access

- [ ] All §0.1 PIM-eligible roles assigned to named individuals; activation requires MFA + justification + ticket reference.
- [ ] Standing eligibility reviewed quarterly; results recorded in the §14.2 examiner packet.
- [ ] Regulator-portal filer credentials documented for NYDFS, EDGAR, FINRA Firm Gateway, OCC BankNet, FDICconnect, FederalReserve E-Apps, FTC, FinCEN, OFAC, CISA, and applicable state portals.

### Licensing

- [ ] §0.2 license matrix validated against current entitlements; gaps logged and tracked.

### Data sources

- [ ] §0.3 authoritative-source readiness confirmed for Defender XDR, Sentinel, Purview Audit, IRM, eDiscovery (Premium), Communication Compliance, Service Health, the §8 SharePoint list, and the §9 Power Automate solution.

### Configuration

- [ ] §1 manual register and notification matrix maintained as the sovereign-cloud / outage fallback.
- [ ] §2 Defender XDR custom view, FSI severity rubric, and structured-comment templates in place and known to SOC.
- [ ] §3 Sentinel automation rules deployed; run-history capture procedure documented.
- [ ] §4 IRM cases workspace permissioned; pseudonymization roles confirmed.
- [ ] §5 eDiscovery (Premium) standing case template configured; hold-notice template approved by General Counsel.
- [ ] §6 Communication Compliance Copilot-scoped policy fired test alert reviewed end-to-end with Series 24/66 disposition.
- [ ] §7 Service Health gate documented in IR plan as mandatory pre-clock-start step.
- [ ] §8 SharePoint IR list deployed with full schema; site is legal-hold-aware.
- [ ] §9 Power Automate flows deployed; 28-day run history exporting to the IR site.
- [ ] §10 Disclosure Committee charter and materiality framework approved; meeting template in use.
- [ ] §11 OFAC pre-screen workflow approved; sanctions-counsel relationship attested.
- [ ] §12 quarterly tabletop calendar published; AAR template in use.

### Evidence and reporting

- [ ] §13 regulator-portal reference reviewed by General Counsel within the last 12 months.
- [ ] §14 per-incident evidence-pack convention in place; standing examiner packet refreshed within the last 30 days.
- [ ] Annual board sign-off record on file.

### Cross-control alignment

- [ ] Recurring §2 / §3 false positives routed to [Control 1.8](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) for tuning.
- [ ] Recurring §4 false positives routed to [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md) for tuning.
- [ ] Recurring §6 false positives routed to [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) for tuning.
- [ ] DLP / sensitivity-label changes triggered by incident lessons-learned routed to [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md).
- [ ] Audit-log retention sufficiency validated against incident-investigation needs per [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).
- [ ] Retention-policy adequacy for Copilot interaction history validated per [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).
- [ ] Identity controls (PIM, phishing-resistant MFA) per [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md).
- [ ] Material AI-agent integrity incidents trigger MRM challenge re-validation per [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md).
- [ ] Agent-365 console used for cross-tenant agent inventory and ownership lookups per [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md).
- [ ] Orphaned-agent detection feed correlated into Sentinel per [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md).
- [ ] Sentinel integration architecture maintained per [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*