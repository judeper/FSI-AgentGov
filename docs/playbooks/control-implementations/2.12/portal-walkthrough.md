# Portal Walkthrough — Control 2.12: Supervision and Oversight (FINRA Rule 3110)

!!! danger "READ FIRST — Scope and Sibling Routing"
    **This playbook configures the supervisory control surfaces that FINRA Rule 3110 requires a firm to operate on top of AI agents** — Written Supervisory Procedures (WSP) addendum authoring, designated-principal designation and CRD verification, Copilot Studio supervisory patterns (human-agent handoff, approval actions, generative-answers guardrails), Microsoft Agent Framework human-in-the-loop (HITL) using `RequestPort` / `request_info()` / checkpointed pending requests, Power Automate supervisory review queues, Entra ID Governance sponsor attestation, Rule 2210 communication classification, Rule 3120 annual testing, and the sovereign-cloud compensating control.

    **Control 2.12 is the FINRA Rule 3110 non-substitution anchor for the framework.** Controls [2.25 (Agent 365 admin center)](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md), [2.26 (Entra Agent ID)](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md), and [3.6 (orphaned-agent detection)](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) provide tooling that **supports** supervision; they do **not substitute for** the principal-led supervisory review configured here.

    **This walkthrough IS for:**

    | In Scope | Surface | Outcome |
    |---|---|---|
    | Authoring and versioning the firm's AI-specific WSP addendum | SharePoint / document library + principal signature workflow | Addendum signed by a registered principal, retained under SEC 17a-4(f) |
    | Verifying principal registration (Series 24 for BD; Series 66 / 65 for RIA) against CRD | FINRA Gateway + firm CRD evidence repository | Quarterly-refreshed principal roster |
    | Configuring **human-agent handoff** in Copilot Studio (escalation to a live reviewer) | Copilot Studio → Agent → Topics / Settings → Escalation | Deterministic escalation for defined high-risk triggers |
    | Configuring **approval actions** in Copilot Studio (pre-send principal approval via Power Automate) | Copilot Studio → Agent → Actions + Power Automate | Zero Retail Communications delivered without documented pre-use approval |
    | Configuring **generative-answers guardrails** (content sources, moderation, citation enforcement) | Copilot Studio → Generative AI → Knowledge + Moderation | Grounded outputs with enforced citation and topic boundaries |
    | Wiring **Microsoft Agent Framework HITL** (`RequestPort`, `request_info()`, checkpoints with pending requests) | Agent Framework SDK + application-surface integration | Auditable pause / resume with reviewer-attributed decisions |
    | Building the **Power Automate supervisory review queue** (SLA, risk-based routing, reviewer identity) | Power Automate → Cloud flows → Approvals | Examiner-ready queue with per-item audit trail |
    | Configuring **Entra ID Governance sponsor attestation** (quarterly access review for Z3 agents) | Entra → Identity Governance → Access reviews | Quarterly sponsor attestation evidence |
    | Operating the **Rule 2210 classification** workflow (Correspondence / Retail / Institutional) | Copilot Studio metadata + approval flow | Per-template classification with principal pre-use approval where required |
    | Operating the **Rule 3120 annual testing** workflow (design, operating, exception) | Purview + firm test repository | Signed annual testing report |
    | Operating the **sovereign-cloud compensating control** (principal-led manual review) | Firm supervision register + Control 1.2 registry | Documented manual sampling where tooling parity is absent |
    | Capturing per-session evidence (screenshots, exports, reviewer-decision audit trail) | SharePoint retention labels / Purview / WORM archive | 6-year retention aligned to SEC 17a-4 |

    **This walkthrough is NOT for:**

    | Out of Scope | Use Instead |
    |---|---|
    | Discovery and first-time inventory of agents at the tenant level | [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |
    | Authoring the master agent registry metadata schema | [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) |
    | Agent-identity lifecycle governance (sponsor assignment, access packages, lifecycle workflows for leaver cascades) | [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) |
    | Agent 365 admin center publishing / activation approval (admin approval is **not** principal supervision) | [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) |
    | Orphaned-agent detection and remediation | [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |
    | Audit-log retention plumbing (WORM, 17a-4(f) alternative, Purview retention lock) | [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) |
    | Model risk management (validation, challenger models, inventory under OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)) | [Control 2.6 — Model Risk Management Alignment with OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) |
    | Document and records retention beyond supervision records | [Control 2.13 — Documentation and Record-Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) |
    | Incident reporting and RCA following a supervisory failure | [Control 3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) |
    | PowerShell / Microsoft Graph automation for the same surfaces | [`./powershell-setup.md`](./powershell-setup.md) |
    | Test cases and sample queries for verification | [`./verification-testing.md`](./verification-testing.md) |
    | Error remediation, missing blades, feature-flag anomalies | [`./troubleshooting.md`](./troubleshooting.md) |

!!! warning "Hedged-Language Reminder"
    This playbook helps your organization **support compliance with** FINRA Rule 3110 (Supervision), FINRA Rule 3120 (Supervisory Control System), FINRA Rule 2210 (Communications with the Public), FINRA Rule 4511 (Books and Records), FINRA Regulatory Notice 24-09 (Gen AI / LLM guidance), SEC Rules 17a-3 / 17a-4 (Recordkeeping and WORM retention), SOX Sections 302 / 404 (Internal Controls), and NYDFS 23 NYCRR 500 (Supervisory Review Analogue). It does **not** by itself guarantee any regulatory outcome. It **does not replace** a firm's written supervisory procedures, the designation of an appropriately registered principal (Series 24 for broker-dealers, Series 66 / 65 for investment advisers), or the registered-principal supervisory review required by FINRA Rule 3110 for the business activities involved. Implementation requires firm-specific WSP authoring, validated change control, and independent testing by the compliance function. Organizations should verify all configurations against their examination workpapers and legal counsel before treating these procedures as adequate evidence.

!!! info "License and Program Requirements"
    | Requirement | Why | Where to verify |
    |---|---|---|
    | Microsoft 365 Copilot / Copilot Studio license | Required for authoring supervisory patterns in Copilot Studio | M365 admin center → Billing → Licenses |
    | Power Automate per-flow or per-user plan | Approval actions and the review queue run as cloud flows | Power Platform admin center → Licensing |
    | Microsoft Entra ID P2 (Identity Governance) | Required for Access Reviews that underpin sponsor attestation | Entra → Identity → Overview → License |
    | Microsoft Purview Audit (Standard or Premium) | Required to retain supervision events for the 6-year SEC 17a-4 horizon | Purview → Audit → Audit retention policies |
    | SharePoint Online with retention labels (or equivalent 17a-4(f) WORM archive) | Required to preserve signed WSP, reviewer decisions, and Rule 3120 evidence | SharePoint admin → Content services → Retention labels |
    | FINRA Gateway access (or firm CRD-evidence repository) | Required to verify principal registration | <https://www.finra.org/filing-reporting/finra-gateway> |
    | Microsoft Agent Framework SDK (optional) | Required for HITL patterns using `RequestPort` / `request_info()` / checkpoints when building code-first agents | Developer workstation with the Agent Framework runtime |

!!! warning "Sovereign Cloud Availability — GCC, GCC High, DoD"
    Supervisory obligations under FINRA Rule 3110 apply equally to agents deployed in commercial, GCC, GCC High, and DoD tenants. Several of the Microsoft tools referenced here have parity gaps in sovereign clouds as of April 2026:

    | Capability | Commercial | GCC | GCC High | DoD |
    |---|---|---|---|---|
    | Copilot Studio human-agent handoff | ✅ GA | ⚠️ verify | ⚠️ verify | ⚠️ verify |
    | Copilot Studio approval actions (Power Automate) | ✅ GA | ✅ GA | ⚠️ verify | ⚠️ verify |
    | Agent Framework HITL (`RequestPort`, `request_info()`) | ✅ GA (runtime) | ⚠️ evidence-export may lag | ⚠️ evidence-export may lag | ⚠️ evidence-export may lag |
    | Entra Agent ID sponsorship attestation | ✅ Preview | ❌ not announced | ❌ not announced | ❌ not announced |
    | Agent 365 admin center | ✅ GA May 1, 2026 | ❌ not announced | ❌ not announced | ❌ not announced |

    **If your tenant URL ends in `admin.microsoft.us` or you authenticate against `login.microsoftonline.us`, jump to [§10 — Sovereign Cloud Compensating Control](#10-sovereign-cloud-compensating-control-gcc-gcc-high-dod) before configuring anything else.** FSI firms operating sovereign tenants must maintain a **documented compensating supervisory control** — principal-led manual review at the zone-appropriate sampling rate, reconciled against the Control 1.2 / 3.1 agent registry — and must not claim technical enforcement of Zone 3 HITL in sovereign clouds unless Microsoft has published parity for the specific feature being claimed.

!!! tip "Portal Navigation May Shift"
    Microsoft refines Copilot Studio, Power Automate, and Entra navigation regularly. If a blade name does not match what you see, anchor on the underlying noun ("Topics", "Actions", "Moderation", "Approvals", "Access reviews") and consult Microsoft Learn. Screenshot anchors in this playbook record the navigation that was verified at the **Last UI Verified** date in the [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) header (April 2026).

---

## Document Map

| § | Section | Verification Criterion Evidenced |
|---|---|---|
| 0 | [Pre-flight Prerequisites and Triage](#0-pre-flight-prerequisites-and-triage) | All — gating checks |
| 1 | [WSP Addendum Authoring Workflow](#1-wsp-addendum-authoring-workflow) | VC-1, VC-2 |
| 2 | [Principal Designation and CRD Verification](#2-principal-designation-and-crd-verification) | VC-3 |
| 3 | [Copilot Studio Supervisory Patterns](#3-copilot-studio-supervisory-patterns) | VC-4 |
| 3a | [Pattern A — Human-Agent Handoff](#3a-pattern-a-human-agent-handoff) | VC-4 |
| 3b | [Pattern B — Approval Actions](#3b-pattern-b-approval-actions) | VC-4, VC-5 |
| 3c | [Pattern C — Generative-Answers Guardrails](#3c-pattern-c-generative-answers-guardrails) | VC-4 |
| 4 | [Microsoft Agent Framework HITL Configuration](#4-microsoft-agent-framework-hitl-configuration) | VC-4 |
| 5 | [Power Automate Supervisory Review Queue](#5-power-automate-supervisory-review-queue) | VC-5, VC-6 |
| 6 | [Entra ID Governance Sponsor Attestation](#6-entra-id-governance-sponsor-attestation) | VC-7 |
| 7 | [Rule 2210 Classification Workflow](#7-rule-2210-classification-workflow) | VC-8 |
| 8 | [Rule 3120 Annual Testing Workflow](#8-rule-3120-annual-testing-workflow) | VC-9 |
| 9 | [Evidence Capture Per Session](#9-evidence-capture-per-session) | VC-10 |
| 10 | [Sovereign Cloud Compensating Control — GCC, GCC High, DoD](#10-sovereign-cloud-compensating-control-gcc-gcc-high-dod) | VC-1 through VC-10 (substitute path) |
| 11 | [Zone Cadence Checklists](#11-zone-cadence-checklists) | Operational rhythm |
| 12 | [Cross-References and Sibling Routing](#12-cross-references-and-sibling-routing) | Navigation |

---

## 0. Pre-flight Prerequisites and Triage

Before opening any portal blade, walk through this gate. A failed gate is itself an auditable finding and must be logged in the control session worksheet. Skipping a gate produces silent failures later — for example, Copilot Studio approval actions will not run if the Power Automate connector is not licensed to the agent's publishing environment.

### 0.1 Confirm tenant cloud and in-scope entity

1. Sign in to [`https://admin.microsoft.com`](https://admin.microsoft.com) as a user holding **Global Reader** (or higher).
2. In the upper-right profile menu, confirm the tenant name matches the **regulated legal entity** (broker-dealer, registered investment adviser, bank holding company, or affiliate) whose WSP you are amending. Firms with multiple regulated entities under one tenant must produce a separate WSP addendum per entity and keep the cross-tenant registry aligned with [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md).
3. Record the **Tenant ID** (GUID) and the **Primary domain** in the control session worksheet.
4. Identify the cloud:
    - Commercial → continue with §1 onward.
    - GCC → continue with §1 onward, but verify each feature against the Sovereign Cloud table before relying on it.
    - **GCC High / DoD → stop here and jump to [§10](#10-sovereign-cloud-compensating-control-gcc-gcc-high-dod).**

!!! warning "Tenant Cloud Detection"
    If the URL bar shows `admin.microsoft.us`, `entra.microsoft.us`, or you authenticate against `login.microsoftonline.us`, treat the tenant as GCC High or DoD and operate the compensating control in §10. Do not silently fall through; examiners will ask which variant was used.

### 0.2 Confirm role assignments

Every section below assumes **two named humans hold each role** per FINRA dual-control expectations. Single-person admin coverage on supervisory surfaces is itself an audit finding.

| Role (canonical — see `docs/reference/role-catalog.md`) | Required for | Where to assign |
|---|---|---|
| **Compliance Officer** | WSP addendum ownership, Rule 3120 annual testing sign-off, regulatory-alignment review | Firm compliance org chart (governance artifact, not an Entra role) |
| **Designated Principal / Qualified Supervisor** (Series 24 for BD; Series 66 / 65 for RIA) | Principal review / approval of flagged outputs, Rule 2210 pre-use approvals, Rule 3120 evidence signature | Firm registered-principal roster; verified against FINRA CRD quarterly (§2) |
| **AI Governance Lead** | Framework-level supervision design, sampling protocols, sovereign compensating-control operation, internal-audit liaison | Firm governance committee charter |
| **AI Administrator** | Copilot Studio HITL / handoff / approval configuration; Agent Framework HITL evidence export; maintains admin-configured SoD boundaries | Power Platform Admin + Copilot Studio Admin in M365 admin center |
| **Agent Owner** | Ensures each assigned agent is registered in Control 1.2 / 3.1, zone-classified, and operating within approved scope | Agent's sponsor record (see [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)) |
| **Entra Global Admin** | One-time Access Review scope creation for sponsor attestation (§6) | Entra → Roles & admins |
| **Entra Identity Governance Admin** | Access Reviews authoring and execution (§6) | Entra → Roles & admins |
| **Power Platform Admin** | Approval-flow publishing, environment-scoped DLP for the approval connector (§3b, §5) | Power Platform admin center → Admins |
| **Purview Compliance Admin** | Retention label creation, audit retention policies (§9) | Purview → Roles & scopes |
| **Exchange Online Admin** | Approval-email channel configuration where approvals run over Outlook actionable messages | Exchange admin center → Roles |

!!! example "Examiner Evidence Box — Role Coverage"
    | Element | Value |
    |---|---|
    | Screenshot (Entra Roles & admins filtered to `Identity Governance`) | `docs/images/2.12/EXPECTED.md#0-2-role-coverage` |
    | Firm principal roster PDF | Stored in `SharePoint/Compliance/Supervision/2.12/principals-{YYYY-Q#}.pdf` |
    | Retention path | 6 years under SEC 17a-4(b)(4) |

### 0.3 Confirm licensing and program entitlements

1. M365 admin center → **Billing → Licenses** — confirm Microsoft 365 Copilot / Copilot Studio seats for every Agent Owner and Principal who will review outputs.
2. Power Platform admin center → **Licensing** — confirm a Power Automate per-flow or per-user plan attached to the environment where the approval flow will run.
3. Entra admin center → **Identity → Overview** — confirm Entra ID P2 is active (Access Reviews require P2).
4. Purview portal → **Audit → Audit retention policies** — confirm an agent-scoped retention policy exists with a retention duration of **10 years** (preferred, matches NYDFS record-keeping guidance) or **6 years minimum** (SEC 17a-4 floor).

*Screenshot anchor: `docs/images/2.12/EXPECTED.md#0-3-licenses` — M365 admin center billing view filtered to Copilot licenses.*

### 0.4 Confirm the authoritative agent registry is current

1. Open the Control 1.2 / 3.1 agent registry (typically a Dataverse table or SharePoint list; path is documented in your firm's Control 1.2 runbook).
2. Filter to the regulated entity identified in §0.1 and to agents with zone classification `Zone 2` or `Zone 3`.
3. Confirm every in-scope agent has:
    - An identified **Agent Owner** (human user principal name).
    - An assigned **Sponsor** (see [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)).
    - A **zone classification** (Z1 / Z2 / Z3).
    - An **autonomy level** (Recommend-Only / Semi-Autonomous / Fully Autonomous — note that Fully Autonomous is out of scope at Agent 365 GA per Control 2.12).
    - A **Rule 2210 classification** (Correspondence / Retail / Institutional / Internal-only) if the agent produces customer-facing output.
4. Flag every row with a null in any of the above columns and resolve before proceeding. Unregistered or incompletely classified agents cannot be supervised and must be remediated under [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) or [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) before they appear in this walkthrough.

!!! warning "Scope gate — no registry, no supervision"
    If the registry is unavailable, out of date, or incomplete, **stop this walkthrough**. Supervision scope is bounded by the authoritative registry; untracked agents cannot be supervised and must not be deployed into Zone 2 or Zone 3. Re-enter this playbook only after the registry is reconciled.

### 0.5 PIM activation window

For every role listed in §0.2 that is governed by Privileged Identity Management (PIM), activate the role for **the minimum session duration** needed (typically 2–4 hours for a single configuration pass). Record the activation justification as `Control 2.12 configuration session — {YYYY-MM-DD} — {operator UPN}`. At the end of the session, deactivate.

---

## 1. WSP Addendum Authoring Workflow

The firm's Written Supervisory Procedures are the centerpiece of Rule 3110. The AI-specific addendum documents how the firm supervises AI agent outputs and references this playbook as the operational procedure. It must be authored, reviewed, approved, versioned, and retained — and must be re-reviewed annually or on material change.

### 1.1 Create the addendum document

1. Open the firm's compliance document library in SharePoint Online — typically `SharePoint/Compliance/WSP/`. If your firm operates a compliance DMS (e.g., NICE Actimize, Smarsh) instead, use that system and treat the paragraphs below as structural guidance.
2. Create a new document named `WSP-Addendum-AI-Supervision-{YYYY}-v{N}.docx` (e.g., `WSP-Addendum-AI-Supervision-2026-v1.docx`).
3. Apply the **Content Type** `Supervisory Procedure — AI Agents` (create if not present; must inherit from the firm's standard WSP content type).
4. Apply a **retention label** of `WSP — 10 years` (or the firm's equivalent 17a-4(f)-compliant label). Once applied, the label must be immutable (no user-initiated deletion).

*Screenshot anchor: `docs/images/2.12/EXPECTED.md#1-1-wsp-library` — SharePoint library view showing the retention label applied.*

### 1.2 Required sections in the addendum

At minimum, the addendum must contain the sections listed below. Each section has a suggested opening sentence that uses the framework's hedged-language conventions; adapt to firm style but preserve the hedging.

| # | Section | Minimum content | Hedged-language opening |
|---|---|---|---|
| 1 | Scope and applicability | In-scope agents by zone, business unit, and regulated entity | "These procedures apply to AI agents registered under Control 1.2 / 3.1 and supports compliance with FINRA Rule 3110." |
| 2 | Definitions | AI agent, HITL, autonomy level, Zone 1/2/3, Rule 2210 classes | — |
| 3 | Designated principals | Named principals, registrations (Series 24 / 66 / 65), CRD numbers, scope | "The firm designates the following registered principals as the responsible supervisors for AI agent supervisory review; this designation does not substitute for the registered-principal review obligations of any individual business activity." |
| 4 | Supervisory patterns | Human-agent handoff, approval actions, generative-answers guardrails, Agent Framework HITL — how each is used | — |
| 5 | Sampling protocols | Z1 / Z2 / Z3 sampling rates; high-risk 100% rule | — |
| 6 | Rule 2210 classification procedure | Decision tree, per-template approval, exclusion reliance | — |
| 7 | Rule 3120 annual testing | Test design, operating effectiveness, exception handling | — |
| 8 | Exception escalation | Triggers, routing, SLAs, incident-reporting interface to Control 3.4 | — |
| 9 | Record-keeping | Retention paths, retention duration, 17a-4(f) attestation | — |
| 10 | Sovereign-cloud compensating control | Description of manual principal-led review when tooling parity is absent | "Where Microsoft has not published parity for a referenced supervisory tool in the firm's sovereign tenant, the firm operates a compensating manual principal-led review that supports — and does not substitute for — the supervisory obligations of FINRA Rule 3110." |
| 11 | Review and amendment | Annual review cadence; material-change trigger list | — |
| 12 | Approval | Registered-principal signature, effective date, version history | — |

### 1.3 Principal review and signature

1. Save the draft and set permissions to the designated principal (read/write) and Compliance Officer (read/write). Remove all other contributors to prevent tampering during the approval window.
2. Trigger a SharePoint approval flow (Power Automate template: **Request sign-off**) targeting the principal's mailbox. The flow must:
    - Record the **approver UPN** and **approval timestamp**.
    - Write the decision (`Approved` / `Rejected` / `Returned for revision`) back to a metadata column on the document.
    - On approval, set the document status to `Effective — {date}`.
3. The principal reviews the draft, signs (digital signature or sign-off action), and on approval the flow publishes the document to a read-only library view.
4. Capture the approval history (Power Automate run → Approvals tab → export JSON) and store alongside the signed PDF.

*Screenshot anchor: `docs/images/2.12/EXPECTED.md#1-3-approval-flow` — Power Automate approval run history showing approver identity and timestamp.*

!!! example "Examiner Evidence Box — Signed WSP Addendum"
    | Element | Value |
    |---|---|
    | Signed PDF | `SharePoint/Compliance/WSP/WSP-Addendum-AI-Supervision-2026-v1.pdf` |
    | Approval flow run history | Exported to `SharePoint/Compliance/WSP/approval-history/WSP-Addendum-AI-Supervision-2026-v1.json` |
    | Retention label | `WSP — 10 years` (immutable) |
    | Hash / version | Document version + SHA-256 captured in firm DMS |

### 1.4 Versioning and amendment triggers

Re-version (v2, v3, …) and re-sign the addendum whenever any of the following occur:

- Annual review date arrives (minimum once per calendar year).
- A new AI agent deploys into Zone 3 for a business activity not previously covered.
- A material change occurs in a referenced Microsoft feature (e.g., Copilot Studio approval-action semantics change; Agent Framework `RequestPort` API is superseded).
- FINRA, SEC, OCC, Fed, or NYDFS publishes AI-specific guidance that changes the expectation (e.g., a successor to FINRA Regulatory Notice 24-09).
- A Rule 3120 annual test identifies a design- or operating-effectiveness gap that requires procedural amendment.
- A supervisory failure is reported through [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) and root-cause analysis identifies a WSP gap.

---

## 2. Principal Designation and CRD Verification

FINRA Rule 3110 requires the firm to designate an **appropriately registered principal** as the responsible supervisor. For the AI-supervision scope, this is typically a Series 24 principal (general securities) or Series 66 / 65 principal (investment adviser). Designation without current registration is a finding; this playbook requires quarterly CRD verification.

### 2.1 Identify candidate principals

1. Open the firm's registered-principal roster (HR or compliance system).
2. Filter to principals whose **Rule 3110 scope** encompasses the business activity of the AI agents in scope (e.g., retail brokerage supervision, investment-adviser communication supervision, research review, trade surveillance).
3. For each candidate, record:
    - Full name, UPN, CRD number.
    - Registrations held, with effective and expiration dates.
    - Scope of supervisory authority (documented in the firm's supervisory structure).
    - Deputy / backup principal (single-person coverage is a finding).

### 2.2 Verify registration via FINRA Gateway / CRD

1. Open [`https://www.finra.org/filing-reporting/finra-gateway`](https://www.finra.org/filing-reporting/finra-gateway) and sign in with the firm's Gateway account.
2. Navigate to **Registration → View Registrations** (the exact path may vary; anchor on the noun "Registrations").
3. For each candidate principal, look up the CRD record and confirm:
    - Registration status is `Active`.
    - The Series 24 (or 66 / 65) registration is listed and not flagged `Expired`, `Suspended`, or `Pending withdrawal`.
    - No open disclosures that would affect supervisory fitness (firm compliance counsel determines materiality).
4. Export the registration confirmation to PDF (Gateway → Export) and save to `SharePoint/Compliance/Supervision/2.12/principals-{YYYY-Q#}/{CRD}.pdf`.
5. If the firm does not operate FINRA Gateway directly (e.g., RIA-only firm), use BrokerCheck or the firm's Form ADV / IARD evidence and document the alternative source in the principal roster.

*Screenshot anchor: `docs/images/2.12/EXPECTED.md#2-2-crd-verification` — FINRA Gateway registration detail (redacted) showing active status.*

### 2.3 Assign principals to agent scopes

1. In the agent registry (Control 1.2 / 3.1), for each Z2 / Z3 agent, populate the `Designated Principal UPN` and `Designated Principal CRD` columns.
2. For Z3 agents producing Rule 2210 Retail Communication, populate a separate `Rule 2210 Pre-Use Approver UPN` column (may be the same principal or a different one per firm structure).
3. Commit the change through the registry's change-control process (audit-logged; see Control 1.2).

### 2.4 Quarterly refresh cadence

1. On the first business day of each calendar quarter, the Compliance Officer re-runs §2.2 for every designated principal.
2. If a registration has lapsed, been suspended, or is about to expire (<60 days), the principal is temporarily removed from the scope and a backup is promoted until CRD status is restored.
3. The Compliance Officer signs the quarterly principal-roster attestation and stores it at `SharePoint/Compliance/Supervision/2.12/principals-{YYYY-Q#}.pdf`.

!!! example "Examiner Evidence Box — Principal Roster"
    | Element | Value |
    |---|---|
    | Quarterly signed roster | `SharePoint/Compliance/Supervision/2.12/principals-{YYYY-Q#}.pdf` |
    | Per-principal CRD export | `SharePoint/Compliance/Supervision/2.12/principals-{YYYY-Q#}/{CRD}.pdf` |
    | Registry column populated | `Designated Principal UPN`, `Designated Principal CRD`, `Rule 2210 Pre-Use Approver UPN` |
    | Retention | 6 years under SEC 17a-4(b)(4) |

---

## 3. Copilot Studio Supervisory Patterns

Copilot Studio exposes three supervisory patterns that map directly to the high-risk-criteria obligations of the firm's WSP: **human-agent handoff** (escalate a live conversation to a human), **approval actions** (pre-send principal approval of a specific generated output), and **generative-answers guardrails** (constrain content sources and moderation). Pattern selection must match the WSP's firm-defined high-risk criteria and must be verifiable by configuration export.

!!! info "Which pattern for which trigger?"
    | Trigger example | Recommended pattern | Rationale |
    |---|---|---|
    | Customer asks for an investment recommendation | Pattern A (handoff) — transfer to a licensed representative | Recommendations to retail customers require a licensed human; no generative path is acceptable |
    | Agent drafts an email that will be sent to >25 retail investors | Pattern B (approval) — principal pre-use approval per Rule 2210 | Retail Communication requires pre-use principal approval |
    | Agent answers routine product questions from grounded knowledge | Pattern C (guardrails) — restrict sources + moderation + citation enforcement | Information-retrieval only; no recommendation; sampling applies |
    | Agent executes an action (account open, trade entry) | Pattern B (approval) or explicit block | High-impact action; firms should typically block agents from autonomous execution in Zone 3 |

### 3a. Pattern A — Human-Agent Handoff

Human-agent handoff transfers a live Copilot Studio conversation to a human reviewer, preserving conversational context. It is the right pattern for **interactive** high-risk turns that warrant a licensed person, not a pre-send approval.

#### 3a.1 Open the agent in Copilot Studio

1. Open [`https://copilotstudio.microsoft.com`](https://copilotstudio.microsoft.com).
2. Select the target environment (match the agent's registered environment in Control 1.2). If you see the wrong environment, switch via the environment picker in the upper right.
3. Open the target agent. Confirm the agent's **Zone** metadata matches the WSP in-scope zones. Agents outside scope must not be modified here.

*Screenshot anchor: `docs/images/2.12/EXPECTED.md#3a-1-agent-open` — Copilot Studio agent overview page with environment indicator and zone metadata visible.*

#### 3a.2 Create or open the escalation topic

1. In the left nav, click **Topics**.
2. Create a new topic named `Escalate to Human — {scope}` (e.g., `Escalate to Human — Investment Advice`) or open an existing escalation topic.
3. Configure trigger phrases for interactive handoff triggers (e.g., `talk to an advisor`, `speak to a human`, `I need a recommendation`).
4. In the authoring canvas, add a node **Transfer conversation → Transfer to agent** (exact label varies with Copilot Studio release; anchor on "Transfer"). Configure:
    - **Target agent / queue** — the Omnichannel / Customer Service queue staffed by licensed representatives. The queue must be monitored during business hours and must have a documented SLA (typically ≤5 minutes initial response for Zone 3).
    - **Context to pass** — include conversation history, agent ID, triggering phrase, and the registered user's identifier (do not pass PII not needed for routing).
    - **Fallback** — if no agent is available, route to a `Take a message` topic that collects callback details and creates a review queue item (see §5).

*Screenshot anchor: `docs/images/2.12/EXPECTED.md#3a-2-transfer-node` — Transfer-conversation node configuration.*

#### 3a.3 Configure system-wide escalation triggers

1. In the left nav, click **Settings → Escalation** (or **Topics → System → Escalate**).
2. Confirm the default escalation topic routes to the topic created in §3a.2.
3. Add firm-specific high-risk keyword triggers from the WSP (e.g., `margin`, `options`, `short sale`, `annuity`, `401(k) rollover`) — each adds a guaranteed escalation path independent of authored topics.

#### 3a.4 Test the handoff

1. Open the **Test agent** pane (right side).
2. Trigger each escalation path in turn. Verify:
    - The transfer node fires.
    - The target queue receives the conversation with context.
    - The reviewer's UPN is recorded in the transcript.
3. Capture a screenshot of one successful handoff and attach to the control session worksheet.

#### 3a.5 Publish and record

1. Click **Publish**. Copilot Studio surfaces a publishing approval flow if Agent 365 admin-gated publishing is configured (see [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)).
2. Record the **publish version**, **publisher UPN**, and **publish timestamp** in the agent's registry row.
3. Export the topic definition as YAML (Copilot Studio → Topic → ⋯ → **Copy topic** → paste into a file) and commit to `SharePoint/Compliance/Supervision/2.12/copilot-studio/{agent}/handoff-v{N}.yaml`. The YAML is the audit artifact.

### 3b. Pattern B — Approval Actions

Approval actions pause a Copilot Studio turn, invoke a Power Automate approval flow, and resume only after the designated approver records a decision. This is the right pattern for **pre-send** principal approval (Rule 2210) and for high-impact actions (e.g., drafting an outbound email to retail customers).

#### 3b.1 Create the approval cloud flow

1. Open [`https://make.powerautomate.com`](https://make.powerautomate.com) in the same environment as the agent.
2. Create a new **Instant cloud flow** with trigger **When Copilot Studio calls a flow** (or **PVA Connector** / **Copilot Studio connector** — the trigger name has changed twice in the last 12 months; anchor on the "called from Copilot Studio" description).
3. Define inputs:
    - `agentId` (string)
    - `conversationId` (string)
    - `generatedOutput` (string)
    - `rule2210Classification` (string; values: `Correspondence`, `Retail`, `Institutional`, `NotApplicable`)
    - `riskTier` (string; values: `High`, `Medium`, `Low`)
    - `requesterUpn` (string)
4. Add an action **Start and wait for an approval** (Approvals connector). Configure:
    - **Approval type**: `Approve / Reject — First to respond`.
    - **Title**: `Supervisory review — {agentId} — {riskTier}`.
    - **Assigned to**: dynamic — look up the agent's `Designated Principal UPN` (and `Rule 2210 Pre-Use Approver UPN` for Retail Communications) from the registry. Do **not** hardcode approver UPNs; hardcoding bypasses §2's quarterly refresh.
    - **Details**: include the full `generatedOutput`, the `rule2210Classification`, the `riskTier`, and a link to the WSP addendum.
    - **Item link**: the conversation transcript URL if available.
5. After the approval action, add a **Compose** step that captures:
    - `outcome` (Approve / Reject / Returned)
    - `approverUpn` (from approval output)
    - `approvalTimestampUtc` (UTC ISO-8601)
    - `approverComments`
6. Write the decision to the supervision review register (SharePoint list; see §5) and to the agent's audit trail.
7. Return the `outcome` to Copilot Studio as the flow output.

*Screenshot anchor: `docs/images/2.12/EXPECTED.md#3b-1-approval-flow` — Power Automate canvas showing the Approvals action with dynamic `Assigned to`.*

#### 3b.2 SLA and escalation

1. In the approval action, set the **Reassignment** option so that unresponded approvals after a firm-defined SLA (typically 60 minutes for Retail Communication, 15 minutes for high-risk real-time) reassign to the backup principal.
2. Add a **parallel branch** with a `Delay until` timer equal to the SLA. On timeout, post to a Teams supervision channel monitored by the Compliance Officer and create an incident item under [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).
3. Save the flow and test it end-to-end with a dummy agent output.

#### 3b.3 Attach the flow to the agent

1. Return to Copilot Studio → target agent → **Actions → + Add an action**.
2. Choose **Create a new action → Use a pre-built flow** and select the flow authored in §3b.1.
3. In the action's **Inputs**, map `generatedOutput` to the agent's generated response, `rule2210Classification` to the agent-level metadata (see §7), and `riskTier` to the firm's risk-tier classifier (topic-level metadata or a policy module).
4. Configure the **topics that must invoke the action before sending**. For every topic that could produce customer-facing Retail Communication, insert a **Call an action** node with the approval action and add a **Condition** node that gates the send on `outcome == 'Approve'`.
5. For a rejection, route to a `Supervisor rejected — revise or escalate` topic that preserves context, informs the user politely, and creates a training-signal entry for the Agent Owner.

*Screenshot anchor: `docs/images/2.12/EXPECTED.md#3b-3-agent-action-bind` — Copilot Studio actions pane with the approval flow attached.*

#### 3b.4 Test the approval path

1. In the **Test agent** pane, force a trigger that invokes the approval action.
2. Confirm the approval is delivered to the designated principal (Outlook / Teams / Approvals app).
3. Record a successful approval and a successful rejection. Verify the rejection branch delivers the expected `Supervisor rejected` response and logs the event.
4. Export the flow-run history for both paths and attach to the control session worksheet.

#### 3b.5 Environment DLP and connector scoping

1. Open Power Platform admin center → **Policies → Data policies**.
2. Confirm the environment hosting the approval flow has a DLP policy that:
    - Classifies the **Approvals** connector as `Business`.
    - Classifies any external / unsanctioned connectors as `Blocked` (e.g., personal cloud storage, unapproved messaging platforms).
3. Scope the DLP policy to the environment, not tenant-wide, to avoid breaking other supervisory flows.

!!! example "Examiner Evidence Box — Approval Action"
    | Element | Value |
    |---|---|
    | Flow definition export (JSON) | `SharePoint/Compliance/Supervision/2.12/power-automate/{flowName}-v{N}.json` |
    | Flow-run history (approve path) | Exported to `SharePoint/Compliance/Supervision/2.12/runs/{flowName}/approve-{yyyyMMddTHHmmssZ}.json` |
    | Flow-run history (reject path) | Same, with `reject` suffix |
    | DLP policy screenshot | `docs/images/2.12/EXPECTED.md#3b-5-dlp` |
    | Retention | 6 years WORM |

### 3c. Pattern C — Generative-Answers Guardrails

Guardrails constrain what the agent can cite and say. For Zone 2 agents operating on grounded knowledge and for Zone 3 information-only agents, guardrails plus sampling may be sufficient supervision. For Zone 3 agents that produce recommendations, guardrails **must** be combined with Pattern A or Pattern B.

#### 3c.1 Restrict content sources

1. In Copilot Studio → target agent → **Knowledge**.
2. Remove any source marked **Public websites (open web)** for Zone 3 agents unless the firm's WSP explicitly approves the source list and the source set is monitored by the model-risk function under [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md).
3. Add only firm-approved SharePoint sites, Dataverse tables, or APIs that have been classified and registered in Control 1.2.
4. Record the source inventory (Knowledge → ⋯ → Export) and commit to `SharePoint/Compliance/Supervision/2.12/copilot-studio/{agent}/knowledge-v{N}.json`.

*Screenshot anchor: `docs/images/2.12/EXPECTED.md#3c-1-knowledge-sources` — Knowledge pane showing approved sources only.*

#### 3c.2 Configure moderation and response guidance

1. Open **Settings → Generative AI** (or **Generative answers** — blade name varies).
2. Set **Content moderation** to `High` for Zone 3 agents. This level increases the likelihood the service will decline to produce risky output; it does not guarantee refusal. Moderation is a supplement to — not a substitute for — HITL.
3. In **Instructions** (system prompt / response guidance), add the firm's supervisory boilerplate:
    - "You must not provide investment recommendations. If the user asks for one, escalate using the `Escalate to Human — Investment Advice` topic."
    - "You must cite every factual claim using the provided knowledge sources. If a claim cannot be cited, say you do not know."
    - "You must not collect account numbers, Social Security numbers, or other PII outside the authorized intake forms."
4. Enable **Require citations** where the Copilot Studio release exposes the setting.

#### 3c.3 Configure topic-level boundaries

1. Review every authored topic and classify:
    - **Safe** — information-only; guardrails sufficient.
    - **Sensitive** — requires Pattern B approval before send.
    - **Blocked** — must always escalate via Pattern A.
2. Implement the classification by inserting `Call an action` or `Transfer` nodes in the Sensitive and Blocked topics.

#### 3c.4 Sample the output

1. Configure the **Analytics** or **Insights** pane to export conversations to a SharePoint list monitored by the designated principal.
2. Apply the firm's sampling protocol (§11) to draw the per-period sample.
3. Have the principal complete a documented review (approve / reject / coach) and write the decision to the supervision review register.

#### 3c.5 Publish and record

Follow §3a.5 for publishing, version recording, and YAML export. The combined evidence for Pattern C consists of the knowledge-source export, the generative-AI settings screenshot, and the topic classification table.

---

## 4. Microsoft Agent Framework HITL Configuration

For code-first agents built with the **Microsoft Agent Framework** (the open-source framework that supersedes Semantic Kernel / AutoGen orchestration patterns for enterprise agents), HITL is implemented programmatically rather than through Copilot Studio topics. The Agent Framework exposes a **`RequestPort`** abstraction, a **`request_info()`** call (Python SDK) / equivalent in .NET, and **checkpoints with pending requests** that let the runtime pause, persist state, wait for a human decision via an external surface, and resume.

!!! info "When to use Agent Framework HITL vs Copilot Studio patterns"
    Use Copilot Studio patterns (§3) when the agent is authored in Copilot Studio or Microsoft 365 Copilot declarative-agent form. Use Agent Framework HITL when the agent is a code-first .NET or Python application that the firm builds and deploys (typically Zone 3 back-office agents — surveillance assistants, exception-investigation agents, document-review agents). Both can co-exist in a firm; both must be documented in the WSP (§1.2 row 4).

### 4.1 Prerequisites

1. Agent Framework SDK installed on developer workstations (`pip install agent-framework` for Python, or the .NET package; exact package name and version pinned in the firm's `requirements.txt` / `Directory.Packages.props`).
2. Persistent checkpoint store configured — Azure Storage (Blob + Table), Azure Cosmos DB, or Dataverse. The store must be in a region consistent with the firm's data-residency posture and must have soft-delete and retention-lock enabled to protect supervision state.
3. A reviewer-facing application surface — Teams adaptive card, Power Automate approval, a firm-built web app, or an Outlook actionable message. The surface authenticates the reviewer and writes the decision back to the pending-request store.
4. Application Insights / Azure Monitor configured to capture HITL telemetry to the firm's SIEM per [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

### 4.2 Design the pending-request contract

1. Decide the **schema** of the pending request. Minimum fields:
    - `requestId` (UUID)
    - `agentId`
    - `conversationId`
    - `generatedOutput`
    - `rule2210Classification`
    - `riskTier`
    - `requesterUpn`
    - `approverUpn` (populated from the registry at the time of the request)
    - `createdUtc`, `slaDeadlineUtc`
    - `decisionOutcome` (null until resolved)
    - `decisionApproverUpn`, `decisionUtc`, `decisionComments`
2. Commit the schema as JSON Schema to `SharePoint/Compliance/Supervision/2.12/agent-framework/pending-request.schema.json`. The schema is an audit artifact and must version with the addendum.

### 4.3 Wire `RequestPort` and `request_info()` (Python example)

The snippet below is illustrative — exact class and method names track the Agent Framework release the firm is pinned to. The WSP addendum (§1.2 row 4) documents the firm's pinned version and the surface used to render pending requests.

```python
from agent_framework import Agent, RequestPort, Checkpoint
from firm.supervision import build_pending_request, wait_for_decision

class SupervisedAgent(Agent):
    async def handle(self, turn):
        draft = await self.generate(turn)

        if self.classify_risk(draft) != "Low":
            # Persist a checkpoint with a pending request
            req = build_pending_request(
                agent_id=self.id,
                conversation_id=turn.conversation_id,
                generated_output=draft,
                rule_2210_classification=self.classify_rule_2210(draft),
                risk_tier=self.classify_risk(draft),
                requester_upn=turn.user.upn,
                approver_upn=self.registry.lookup_principal(self.id),
            )
            await self.request_port.submit(req)                      # RequestPort.submit
            decision = await wait_for_decision(req.request_id)       # resolves via request_info()
            if decision.outcome != "Approve":
                return self.rejection_template(decision)

        return draft
```

1. `RequestPort.submit(req)` writes the pending request to the checkpoint store and signals the reviewer-facing surface.
2. The reviewer opens the surface, reviews the `generatedOutput`, records a decision, and writes back to the store.
3. `wait_for_decision(request_id)` (backed by `request_info()` in the framework) resumes the agent turn when the decision arrives.
4. All state is durable: if the runtime restarts during the wait, the agent resumes from the checkpoint on the decision event.

### 4.4 Response handler (reviewer-facing surface)

Typical implementations:

| Surface | How the reviewer acts | How the decision is written back |
|---|---|---|
| Teams adaptive card (recommended) | Card posted in a private 1:1 with the principal; buttons: Approve / Reject | Bot Framework callback writes to the checkpoint store |
| Power Automate approval | Approval delivered via Approvals app / email | Power Automate HTTP action posts decision back to the HITL endpoint |
| Firm-built web app | Reviewer logs in with SSO, sees the queue | Web app writes to the store with the authenticated user's UPN |
| Outlook actionable message | Approve / Reject buttons rendered in email | Requires the firm's Exchange / Graph registration for actionable messages |

In every surface, the decision record **must** capture the authenticated reviewer's UPN from the identity context — never from a form field. Hand-typed approver names are not acceptable supervisory evidence.

### 4.5 Evidence export

1. Configure Application Insights / Azure Monitor to emit a custom event `supervision.decision` on every resolved pending request with properties:
    - `requestId`, `agentId`, `conversationId`, `outcome`, `approverUpn`, `decisionUtc`, `rule2210Classification`, `riskTier`.
2. Forward the events to the firm's SIEM and to a WORM archive under [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).
3. Build a weekly Logic App / Data Factory pipeline that exports the week's supervision decisions to a signed CSV and stores at `SharePoint/Compliance/Supervision/2.12/agent-framework/weekly/{yyyy}-W{ww}.csv`.

!!! warning "Sovereign-cloud evidence-export caveat"
    In GCC High / DoD, some Agent Framework evidence-export integrations (e.g., specific Azure Monitor sinks, Application Insights connectors) may lag commercial. If your firm deploys Agent Framework HITL in sovereign clouds, verify that every component of the evidence pipeline is available in the sovereign cloud before relying on it. Where a sink is unavailable, operate the §10 compensating control on top of the Agent Framework HITL until parity lands.

### 4.6 Test and document

1. Run an end-to-end test: agent generates → pending request created → reviewer approves → agent resumes and delivers output → telemetry event written.
2. Run a rejection test and a timeout test. In the timeout test, verify the pending request is routed to the backup principal per §3b.2.
3. Export the test transcripts, screenshots, and telemetry records. Sign off with the Compliance Officer and AI Governance Lead. Store under `SharePoint/Compliance/Supervision/2.12/agent-framework/tests/`.

---

## 5. Power Automate Supervisory Review Queue

The supervisory review queue is the persistent record of every HITL decision — the queue that an examiner will inspect. Pattern B (§3b) and Agent Framework HITL (§4) both write to this queue. The queue is typically a SharePoint list with a retention label, because SharePoint retention labels provide 17a-4(f)-aligned immutability.

### 5.1 Create the review queue list

1. Open `SharePoint/Compliance/Supervision/2.12/` as a Compliance Officer.
2. Create a new list named `Supervision Review Queue — {YYYY}`.
3. Add columns:
    - `RequestId` (single line, indexed)
    - `AgentId` (single line, indexed)
    - `ConversationId` (single line)
    - `GeneratedOutput` (multiple lines)
    - `Rule2210Classification` (choice: Correspondence / Retail / Institutional / NotApplicable)
    - `RiskTier` (choice: High / Medium / Low)
    - `RequesterUpn` (person)
    - `AssignedPrincipalUpn` (person)
    - `CreatedUtc` (date/time)
    - `SlaDeadlineUtc` (date/time)
    - `Outcome` (choice: Pending / Approve / Reject / Returned / Escalated / TimedOut)
    - `DecisionApproverUpn` (person)
    - `DecisionUtc` (date/time)
    - `DecisionComments` (multiple lines)
    - `EvidenceLink` (hyperlink — back to the Copilot Studio conversation or Agent Framework request record)
4. Apply retention label `Supervision — 10 years` (or firm-equivalent 17a-4(f) label). The label must be immutable.

*Screenshot anchor: `docs/images/2.12/EXPECTED.md#5-1-review-queue` — SharePoint list view with retention label and column schema.*

### 5.2 Risk-based routing

1. In the approval flow (§3b) and the Agent Framework write-back, before creating the list item, compute the routing target:
    - `RiskTier == 'High'` **or** `Rule2210Classification == 'Retail'` → `AssignedPrincipalUpn = Rule 2210 Pre-Use Approver UPN` (from registry).
    - Otherwise → `AssignedPrincipalUpn = Designated Principal UPN`.
2. Compute `SlaDeadlineUtc`:
    - High: 15 minutes from `CreatedUtc`.
    - Medium: 60 minutes.
    - Low: 4 business hours.
3. These values are illustrative defaults; the firm's WSP (§1.2 row 5) is the authoritative source and may tighten or relax them per business line.

### 5.3 SLA monitor flow

1. Create a second Power Automate scheduled flow that runs every 5 minutes.
2. Query the queue for items where `Outcome == 'Pending'` **and** `SlaDeadlineUtc < utcNow()`.
3. For each, set `Outcome = 'TimedOut'`, reassign to the backup principal, and post to the supervision Teams channel.
4. Create an incident under [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) for every timeout where the original `RiskTier == 'High'` or `Rule2210Classification == 'Retail'`.

*Screenshot anchor: `docs/images/2.12/EXPECTED.md#5-3-sla-monitor` — Power Automate run history showing SLA-monitor execution.*

### 5.4 Reviewer identity integrity

The reviewer's UPN **must** come from an authenticated context — the approval action's outputs (`responses[0].responder.userPrincipalName`) or the Agent Framework surface's identity claim — and must be written to `DecisionApproverUpn` by the flow, not by the user. Do not expose `DecisionApproverUpn` as an editable field on the SharePoint form.

### 5.5 Queue views and examiner exports

1. Build SharePoint views:
    - `Pending — High Risk` (all `Pending`, `RiskTier == High`, sorted by `SlaDeadlineUtc` asc).
    - `Decisions — This Week` (all decisions in the current ISO week).
    - `Timeouts` (all `TimedOut` items, grouped by agent).
    - `Retail Communication — Rule 2210` (all items where `Rule2210Classification == 'Retail'`).
2. Weekly, the Compliance Officer exports the `Decisions — This Week` view to CSV and archives at `SharePoint/Compliance/Supervision/2.12/weekly-exports/{yyyy}-W{ww}.csv`.
3. For an examination, the Compliance Officer produces a filtered CSV per examiner request and signs the export manifest.

!!! example "Examiner Evidence Box — Review Queue"
    | Element | Value |
    |---|---|
    | SharePoint list | `Supervision Review Queue — {YYYY}` |
    | Retention label | `Supervision — 10 years` (immutable) |
    | Weekly CSV exports | `SharePoint/Compliance/Supervision/2.12/weekly-exports/` |
    | SLA monitor run history | Power Automate run history, retained 28 days in-portal and mirrored to Azure Monitor for 6 years |

---

## 6. Entra ID Governance Sponsor Attestation

Quarterly sponsor attestation for Zone 3 agents is required by the FINRA 2026 oversight emphasis on designated-supervisor currency and by this control's Zone 3 requirements. The attestation runs as an Entra Access Review. See [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) for the primary walkthrough of Entra Agent ID sponsorship; this section narrows to the **supervisory** attestation required by Rule 3110.

### 6.1 Scope the attestation

1. Open [`https://entra.microsoft.com`](https://entra.microsoft.com) as an **Entra Identity Governance Admin**.
2. Navigate to **Identity Governance → Access reviews → + New access review**.
3. Configure:
    - **Review type**: `Teams + Groups` (if agents are modeled as groups) or `Applications` if agents are modeled as enterprise applications. Use the pattern established by Control 2.26.
    - **Scope**: the security group or access package that contains the Zone 3 agent identities for the regulated entity.
    - **Reviewers**: **Manager of the user** (the sponsor) — this enforces that the sponsor performs the attestation, not an admin. Add a fallback reviewer (Compliance Officer) for any user with a null manager.
    - **Frequency**: quarterly.
    - **Duration**: 14 days.
    - **Upon completion**: `Remove access` for denied sponsors (removes the sponsor's supervisory binding; the Compliance Officer must reassign manually). Do **not** auto-apply; firms operating under Rule 3110 should require a human reassignment decision.
    - **Advanced settings**: require the reviewer to provide a reason for each approval and each denial.

*Screenshot anchor: `docs/images/2.12/EXPECTED.md#6-1-access-review` — Access review configuration page with quarterly frequency and sponsor-as-reviewer.*

### 6.2 Tie the attestation to this control

1. In the access review description, paste the following hedged language (verbatim): "This attestation supports compliance with FINRA Rule 3110's periodic supervisory review obligation and with the Zone 3 requirement of Control 2.12. It does not replace registered-principal supervisory review of agent outputs."
2. Store the description so it appears in every reviewer's attestation email; this documents the supervisory nexus in the audit record.

### 6.3 Monitor and evidence the campaign

1. After 14 days, the campaign completes. Navigate to the completed review and download the results (Access review → Results → Export).
2. Store the CSV at `SharePoint/Compliance/Supervision/2.12/attestations/{YYYY-Q#}-sponsor-attestation.csv`.
3. The Compliance Officer reviews the results:
    - For any `Denied` row, confirm the sponsor has been removed and a replacement has been assigned per Control 2.26's reassignment playbook.
    - For any `Not reviewed` row, escalate to the AI Governance Lead; failure to attest is a finding.
4. Sign the quarterly attestation report and store alongside the CSV.

!!! example "Examiner Evidence Box — Sponsor Attestation"
    | Element | Value |
    |---|---|
    | Access review definition | Entra → Identity Governance → Access reviews → `Z3 Agent Sponsor Attestation — {YYYY-Q#}` |
    | Results CSV | `SharePoint/Compliance/Supervision/2.12/attestations/{YYYY-Q#}-sponsor-attestation.csv` |
    | Signed quarterly report | `SharePoint/Compliance/Supervision/2.12/attestations/{YYYY-Q#}-sponsor-attestation-report.pdf` |
    | Retention | 6 years (SEC 17a-4) |

---

## 7. Rule 2210 Classification Workflow

FINRA Rule 2210 classifies communications as **Correspondence**, **Retail Communication**, or **Institutional Communication**. Each class has different supervision obligations; misclassification is a recurring FINRA examination finding. This section operationalizes classification as a per-template workflow.

### 7.1 Classify every customer-facing agent output template

1. In the agent registry, for every Zone 2 / Zone 3 agent whose outputs can reach customers, enumerate the **output templates** (topics, response templates, email templates) the agent can emit.
2. For each template, apply the classification decision tree from Control 2.12:
    - Audience institutional only → `Institutional`.
    - Audience includes retail, ≤25 retail investors / 30 days → `Correspondence`.
    - Audience includes retail, >25 retail investors / 30 days → `Retail`.
    - Internal-only (no customer delivery) → `NotApplicable`.
3. Record the classification in a metadata column on the template (Copilot Studio topic tag, or a separate Dataverse table keyed to `(agentId, templateId)`).

### 7.2 Document Rule 2210 exclusion reliance (if any)

Rule 2210(b)(1) enumerates exclusions under which a Retail Communication does not require pre-use principal approval (e.g., certain previously-approved templated content, certain filed / reused institutional material). **If the firm relies on an exclusion, it must document which exclusion and the evidence supporting the reliance.**

1. Add a column `Rule2210ExclusionRelied` to the template metadata (values: `None`, `Filed`, `PreviouslyApproved`, `Other — see note`).
2. For every template using an exclusion, attach the supporting evidence (prior approval memo, filing receipt, firm legal memo) to the template record.
3. The Compliance Officer reviews exclusion reliance **annually** and signs an attestation that the exclusions remain valid.

!!! warning "Default to the stricter classification"
    If an AI agent's output could reach more than 25 retail investors within any 30-day period, it likely qualifies as a **Retail Communication** requiring pre-use principal approval. Err on the side of stricter classification; examiners rarely penalize over-classification but routinely cite under-classification.

### 7.3 Pre-use approval for Retail Communications

1. For every template classified `Retail` with no exclusion relied upon, configure Pattern B (§3b) so that every turn emitting the template invokes the approval action.
2. Route the approval to the `Rule 2210 Pre-Use Approver UPN` from the registry (not the general `Designated Principal UPN` unless they are the same person).
3. Retain the approval record for **3 years** (FINRA Rule 2210 record-keeping minimum) under WORM — but the firm's existing 6-year SEC 17a-4 retention subsumes this.

### 7.4 Quarterly re-classification

1. Each quarter, the AI Governance Lead and Compliance Officer re-review the classification of every template where the audience size, distribution channel, or content has changed.
2. Changes to classification require re-approval by the designated principal (Pattern B flow re-triggers once the template's metadata is updated).

!!! example "Examiner Evidence Box — Rule 2210 Classification"
    | Element | Value |
    |---|---|
    | Template classification table | Dataverse table `Rule2210TemplateClassification` or SharePoint list |
    | Exclusion-reliance register | Column `Rule2210ExclusionRelied` + attached evidence |
    | Annual exclusion-reliance attestation | `SharePoint/Compliance/Supervision/2.12/rule-2210/{YYYY}-exclusion-attestation.pdf` |
    | Retail pre-use approval records | Supervision Review Queue filtered to `Rule2210Classification == Retail` |

---

## 8. Rule 3120 Annual Testing Workflow

FINRA Rule 3120 requires firms to test their supervisory control systems annually. For AI supervision this means testing that every control configured above — WSP adherence, HITL functionality, escalation procedures, review queue performance, sampling execution, and supervisor qualifications — actually works.

### 8.1 Scope and plan the test

1. Each January, the Compliance Officer and AI Governance Lead jointly produce the **Rule 3120 AI-Supervision Test Plan** for the year. The plan must cover:
    - **Design effectiveness** — Do the WSPs adequately address AI agent supervision risks? Are they current with Microsoft feature changes, regulatory guidance, and business activities?
    - **Operating effectiveness** — Do the configured controls operate as designed throughout the year? Sample real supervision decisions; confirm the approver UPN matches the registry; confirm the retention label is applied.
    - **Exception handling** — Are exceptions identified, escalated, and resolved? Examine Control 3.4 incident records to confirm supervisory gaps were captured.
2. Store the plan at `SharePoint/Compliance/Supervision/2.12/rule-3120/{YYYY}-test-plan.pdf`.

### 8.2 Execute the test (design effectiveness)

1. Review the WSP addendum (§1) for completeness against the `Required sections` table in §1.2.
2. Walk through each supervisory pattern (§3, §4) and confirm the WSP references the pattern and specifies the firm-defined high-risk criteria it addresses.
3. Sample 5 Rule 2210 Retail Communication templates and confirm each has a documented classification, principal pre-use approval (or documented exclusion reliance), and a current approval evidence record.
4. Capture findings in `{YYYY}-test-design.md`.

### 8.3 Execute the test (operating effectiveness)

1. Draw a statistical sample from the Supervision Review Queue for the test period. Suggested sample sizes per FINRA examination practice:
    - High-risk items: 100% review (no sampling — examine every item).
    - Medium-risk items: 25 items per quarter per business unit.
    - Low-risk items: 25 items per quarter per business unit.
2. For each sampled item, verify:
    - The approver UPN matches the current designated principal for the agent (per §2).
    - The `DecisionUtc` is within the SLA.
    - The `EvidenceLink` resolves to the underlying conversation / pending request.
    - The retention label is applied.
3. Run a **fire drill**: simulate a high-risk output that should trigger handoff or approval. Verify the pattern fires, the correct principal is notified, and the decision is recorded.
4. Run a **timeout drill**: submit a pending request, do not respond, and confirm the SLA monitor (§5.3) reassigns and creates a Control 3.4 incident.
5. Capture findings in `{YYYY}-test-operating.md`.

### 8.4 Execute the test (exception handling)

1. Pull Control 3.4 incident records where the RCA identified a 2.12 gap.
2. Confirm each was remediated and the remediation is reflected in WSP, registry, or configuration.
3. Capture findings in `{YYYY}-test-exceptions.md`.

### 8.5 Report and sign

1. Consolidate design / operating / exception findings into the **{YYYY} Rule 3120 AI-Supervision Test Report**.
2. The report is signed by the Compliance Officer and the Designated Principal.
3. Store at `SharePoint/Compliance/Supervision/2.12/rule-3120/{YYYY}-test-report.pdf` with retention label `Supervision — 10 years`.
4. Surface findings to the firm's risk committee and incorporate into the next WSP version (§1.4 amendment trigger).

!!! example "Examiner Evidence Box — Rule 3120 Annual Test"
    | Element | Value |
    |---|---|
    | Annual test plan | `SharePoint/Compliance/Supervision/2.12/rule-3120/{YYYY}-test-plan.pdf` |
    | Test working papers | `{YYYY}-test-design.md`, `{YYYY}-test-operating.md`, `{YYYY}-test-exceptions.md` |
    | Signed test report | `{YYYY}-test-report.pdf` |
    | Retention | 6 years (SEC 17a-4(b)(4)) — firm retains 10 for conservatism |

!!! warning "Undocumented testing is treated as no testing"
    The FINRA 2026 Annual Regulatory Oversight Report emphasizes that examiners will treat undocumented Rule 3120 testing as if no testing occurred. Working papers, samples drawn, and signed reports are not optional.

---

## 9. Evidence Capture Per Session

Every configuration session under this control produces evidence. The control-session worksheet binds the evidence together. Operators complete the worksheet each session.

### 9.1 Control-session worksheet structure

At the top of each session, the operator (typically the AI Administrator or AI Governance Lead) creates a new row in `SharePoint/Compliance/Supervision/2.12/session-log.xlsx` (or equivalent):

| Column | Value |
|---|---|
| `SessionId` | GUID |
| `SessionDateUtc` | ISO-8601 |
| `OperatorUpn` | Human UPN of the operator |
| `PimActivationWindow` | Start / end of the PIM activation |
| `Scope` | Agent IDs, zone, regulated entity |
| `SectionsExecuted` | List of § numbers completed |
| `EvidenceLinks` | Links to screenshots, exports, and flow-run histories |
| `Approver` | Compliance Officer sign-off (UPN + timestamp) |

### 9.2 Per-section evidence checklist

| § | Evidence item | Path |
|---|---|---|
| 1 | Signed WSP addendum PDF | `SharePoint/Compliance/WSP/WSP-Addendum-AI-Supervision-{YYYY}-v{N}.pdf` |
| 1 | Approval flow run history | `SharePoint/Compliance/WSP/approval-history/` |
| 2 | Quarterly principal roster | `SharePoint/Compliance/Supervision/2.12/principals-{YYYY-Q#}.pdf` |
| 2 | Per-principal CRD export | `SharePoint/Compliance/Supervision/2.12/principals-{YYYY-Q#}/{CRD}.pdf` |
| 3a | Handoff topic YAML | `SharePoint/Compliance/Supervision/2.12/copilot-studio/{agent}/handoff-v{N}.yaml` |
| 3b | Approval flow definition | `SharePoint/Compliance/Supervision/2.12/power-automate/{flowName}-v{N}.json` |
| 3b | Approval flow run history (approve + reject paths) | `SharePoint/Compliance/Supervision/2.12/runs/{flowName}/` |
| 3c | Knowledge source export | `SharePoint/Compliance/Supervision/2.12/copilot-studio/{agent}/knowledge-v{N}.json` |
| 3c | Generative-AI settings screenshot | `docs/images/2.12/EXPECTED.md#3c-2-generative-settings` |
| 4 | Pending-request schema | `SharePoint/Compliance/Supervision/2.12/agent-framework/pending-request.schema.json` |
| 4 | Weekly telemetry export | `SharePoint/Compliance/Supervision/2.12/agent-framework/weekly/{yyyy}-W{ww}.csv` |
| 5 | Supervision Review Queue list | SharePoint list with retention label |
| 5 | Weekly decision CSV | `SharePoint/Compliance/Supervision/2.12/weekly-exports/{yyyy}-W{ww}.csv` |
| 6 | Quarterly sponsor attestation results | `SharePoint/Compliance/Supervision/2.12/attestations/{YYYY-Q#}-sponsor-attestation.csv` |
| 7 | Rule 2210 classification table | Dataverse / SharePoint |
| 7 | Annual exclusion-reliance attestation | `SharePoint/Compliance/Supervision/2.12/rule-2210/{YYYY}-exclusion-attestation.pdf` |
| 8 | Annual Rule 3120 test report | `SharePoint/Compliance/Supervision/2.12/rule-3120/{YYYY}-test-report.pdf` |
| 10 | Sovereign compensating-control register | `SharePoint/Compliance/Supervision/2.12/sovereign/{YYYY-Q#}-register.xlsx` |

### 9.3 Retention

All evidence in §9.2 must be retained for **6 years** under SEC 17a-4(b)(4) on WORM-backed storage or an approved 17a-4(f) audit-trail alternative (firms commonly retain 10 years for headroom). SharePoint retention labels marked immutable satisfy 17a-4(f) when the firm has filed the appropriate notice; consult firm counsel.

### 9.4 Purview audit pipeline

1. Ensure Purview Audit captures the following events and exports them to the firm's SIEM:
    - SharePoint list item creation and modification on the Supervision Review Queue.
    - Power Automate flow runs on the approval flow and the SLA monitor flow.
    - Copilot Studio publish events.
    - Entra Access Review results.
2. See [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for the authoritative audit plumbing.

---

## 10. Sovereign Cloud Compensating Control — GCC, GCC High, DoD

Firms operating in GCC High / DoD (and some GCC tenants where a specific feature has not landed) must operate a **documented compensating supervisory control**: principal-led manual review at the zone-appropriate sampling rate, evidenced in the supervision register, and reconciled against the Control 1.2 / 3.1 agent registry.

!!! warning "Scope — do not claim what you have not configured"
    The firm's WSP must **not** claim technical enforcement of Zone 3 HITL in sovereign clouds for any feature Microsoft has not published parity for. Disclose the absence of native technical enforcement so FINRA / OCC / SEC / NYDFS examiners are not surprised.

### 10.1 Identify the parity gap

1. On the first business day of each quarter, re-read the Microsoft 365 roadmap and the Agent 365 / Copilot Studio / Entra release notes for sovereign clouds.
2. Populate the **sovereign parity register** at `SharePoint/Compliance/Supervision/2.12/sovereign/{YYYY-Q#}-register.xlsx` with columns:
    - `Feature` (e.g., Copilot Studio approval actions, Entra Agent ID sponsorship)
    - `Commercial Status`, `GCC Status`, `GCC High Status`, `DoD Status`
    - `CompensatingControlApplied` (Y/N)
    - `CompensatingControlDescription`
    - `ReconciledToRegistry` (Y/N + date)
3. The AI Governance Lead signs the quarterly register.

### 10.2 Operate the manual principal-led review

For every Zone 3 agent whose native supervisory feature is unavailable:

1. The Agent Owner assembles a weekly sample of the agent's customer-facing outputs (the sampling rate follows §11's Z3 table — 100% for high-risk, statistical for routine).
2. The sample is delivered to the designated principal via a monitored SharePoint folder or secure file share.
3. The designated principal reviews each output and records a decision (Approve / Flag / Escalate) in a manual-review worksheet at `SharePoint/Compliance/Supervision/2.12/sovereign/manual-reviews/{agent}/{yyyy-Www}.xlsx`.
4. Flagged outputs generate incident records under [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).
5. The Compliance Officer reconciles weekly samples against the Control 1.2 / 3.1 registry to confirm no in-scope agent was omitted.

### 10.3 Document the compensating control in the WSP

Section §1.2 row 10 of the WSP addendum must describe the compensating control in concrete terms — which feature is absent, which manual procedure substitutes, who operates it, what the sampling rate is, and how reconciliation against the registry works. Re-sign the WSP when the parity gap closes (if a feature lands in sovereign) and adjust the control.

### 10.4 Examiner-ready story

When an examiner asks how the firm supervises AI agents in the sovereign tenant, the Compliance Officer produces:

1. The quarterly sovereign parity register.
2. The manual-review worksheets for the examination period.
3. The reconciliation log against the Control 1.2 / 3.1 registry.
4. The WSP addendum section describing the compensating control.
5. The Rule 3120 annual test report, which must include a dedicated subsection on compensating-control operating effectiveness.

!!! example "Examiner Evidence Box — Sovereign Compensating Control"
    | Element | Value |
    |---|---|
    | Quarterly parity register | `SharePoint/Compliance/Supervision/2.12/sovereign/{YYYY-Q#}-register.xlsx` |
    | Weekly manual-review worksheets | `SharePoint/Compliance/Supervision/2.12/sovereign/manual-reviews/{agent}/{yyyy-Www}.xlsx` |
    | Reconciliation log | `SharePoint/Compliance/Supervision/2.12/sovereign/reconciliation-{YYYY-Q#}.xlsx` |
    | WSP addendum section | §1.2 row 10 of the current WSP version |

---

## 11. Zone Cadence Checklists

The zone cadence integrates this control's obligations with the broader supervisory rhythm. Cadence is authoritative; frequency deviations require a WSP amendment.

### 11.1 Zone 1 (Personal) cadence

| Cadence | Activity | Owner | Evidence |
|---|---|---|---|
| Annual | WSP acknowledgment by Agent Owner | Agent Owner | Signed acknowledgment in HR / LMS |
| Monthly | 1% spot-check of outputs (or any output that triggers an exception) | Agent Owner | Spot-check worksheet |
| On change | Re-register in Control 1.2 / 3.1 if scope changes | Agent Owner | Registry audit trail |

### 11.2 Zone 2 (Team) cadence

| Cadence | Activity | Owner | Evidence |
|---|---|---|---|
| Weekly | 10% sampling of outputs; documented review | Agent Owner + team lead | Review queue entries |
| Weekly | Review exceptions in the supervision queue | Agent Owner | Queue decisions |
| Quarterly | Sponsor attestation (if Z2 agent has an Entra Agent ID with sponsor) | Sponsor | Access review result |
| Annual | Rule 3120 operating-effectiveness test subset for Z2 | Compliance Officer | Test working papers |
| On change | WSP re-review if the agent's scope changes materially | Compliance Officer | WSP version bump |

### 11.3 Zone 3 (Enterprise) cadence

| Cadence | Activity | Owner | Evidence |
|---|---|---|---|
| Real-time | HITL on every high-risk output (Pattern A / B / Agent Framework) | Designated Principal | Supervision Review Queue |
| Daily | Queue inspection and SLA monitoring | Compliance Officer | SLA monitor run history |
| Daily | Reconcile against Control 3.6 orphaned-agent detection | Compliance Officer | Control 3.6 daily report |
| Weekly | Review of Decisions — This Week export | Compliance Officer | Signed weekly export |
| Weekly | 100% review of high-risk items + 10% statistical sampling of routine | Designated Principal | Queue decisions |
| Monthly | Agent 365 governance card rhythm (Pending Requests, Ownerless) | AI Administrator | Control 2.25 evidence |
| Quarterly | Sponsor attestation access review | Sponsor + Compliance Officer | Access review result |
| Quarterly | Principal CRD verification refresh | Compliance Officer | CRD evidence PDFs |
| Quarterly | Rule 2210 template re-classification | AI Governance Lead + Compliance Officer | Classification table |
| Quarterly | Sovereign parity register (sovereign tenants only) | AI Governance Lead | Parity register |
| Annual | Rule 3120 test (design + operating + exception) | Compliance Officer | Test report |
| Annual | Rule 2210 exclusion-reliance attestation | Compliance Officer | Signed attestation |
| Annual | WSP addendum re-review and re-signature | Compliance Officer + Designated Principal | New WSP version |
| On change | Re-publish Copilot Studio agent on approval / guardrail change | AI Administrator | Publish record |
| On incident | Control 3.4 incident process | Compliance Officer | Incident record |

---

## 12. Cross-References and Sibling Routing

### 12.1 Sibling playbooks (same control)

- [PowerShell Setup](./powershell-setup.md) — automation scripts for the supervisory surfaces
- [Verification Testing](./verification-testing.md) — test cases, sample queries, evidence collection
- [Troubleshooting](./troubleshooting.md) — common errors, missing blades, remediation

### 12.2 Related controls

- [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) — authoritative registry; supervision scope is bounded here.
- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — supervision events feed the immutable audit log.
- [Control 2.6 — Model Risk Management (OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7))](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) — MRM is the model-level complement to this control's human-oversight layer.
- [Control 2.13 — Documentation and Record-Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) — WSPs and supervision registers are records under this control.
- [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — admin-gated publish / activate is **not** principal supervision; this control is the non-substitution anchor for 2.25.
- [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) — sponsorship provides lifecycle accountability; this control provides business-activity supervision. Non-substitution anchor for 2.26.
- [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — metadata schema that supervision relies on.
- [Control 3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — supervisory failures and timeouts escalate here.
- [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — orphaned agents re-enter this control's supervisory scope until reassignment. Non-substitution anchor for 3.6.

### 12.3 Control source

- [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)

### 12.4 External references

- [FINRA Rule 3110 — Supervision](https://www.finra.org/rules-guidance/rulebooks/finra-rules/3110)
- [FINRA Rule 3120 — Supervisory Control System](https://www.finra.org/rules-guidance/rulebooks/finra-rules/3120)
- [FINRA Rule 2210 — Communications with the Public](https://www.finra.org/rules-guidance/rulebooks/finra-rules/2210)
- [FINRA Rule 4511 — Books and Records](https://www.finra.org/rules-guidance/rulebooks/finra-rules/4511)
- [FINRA Regulatory Notice 24-09 — Gen AI / LLM Guidance](https://www.finra.org/rules-guidance/notices/24-09)
- [FINRA 2026 Annual Regulatory Oversight Report](https://www.finra.org/rules-guidance/guidance/reports)
- [SEC Rule 17a-4 — Records To Be Preserved by Certain Exchange Members, Brokers and Dealers](https://www.ecfr.gov/current/title-17/chapter-II/part-240/section-240.17a-4)
- [Microsoft Copilot Studio — Human-agent handoff](https://learn.microsoft.com/en-us/microsoft-copilot-studio/)
- [Microsoft Power Automate — Approvals](https://learn.microsoft.com/en-us/power-automate/get-started-approvals)
- [Microsoft Entra ID Governance — Access reviews](https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview)
- [Microsoft Agent Framework — overview](https://learn.microsoft.com/en-us/agent-framework/)

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*
