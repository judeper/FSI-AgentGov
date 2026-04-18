# Control 1.11 — Portal Walkthrough: Conditional Access and Phishing-Resistant MFA

**Control:** [1.11 — Conditional Access and Phishing-Resistant MFA](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md)<br>
**Pillar:** Security<br>
**Last UI Verified:** April 2026<br>
**Estimated time:** 12–20 hours initial setup across 7 admin roles (multi-day calendar; recurring weekly attestation 2–4 hours)<br>
**Governance Levels:** Baseline / Recommended / Regulated<br>
**Audience:** Conditional Access Administrator, Authentication Policy Administrator, Authentication Administrator, Entra Security Admin, Entra Identity Governance Admin, Entra Privileged Role Admin, AI Administrator / AI Governance Lead, Power Platform Admin, Compliance Officer, CISO

---

!!! danger "READ FIRST — what this walkthrough is and is NOT"
    This walkthrough configures the **Authentication Methods, Authentication Strengths, Named Locations, Conditional Access policy (human + workload identity), Microsoft Managed Policies, Continuous Access Evaluation, Token Protection, sign-in frequency, Privileged Identity Management, Identity Protection (incl. risky workload identities), Entra Agent ID registry / sponsors / custom security attributes / collections, and break-glass governance** surfaces of the **Microsoft Entra admin center** at `entra.microsoft.com` for **Microsoft 365 Copilot, Copilot Studio, Power Platform, and Entra Agent ID** identities.

    It is **NOT** a substitute for the following sibling controls. Each is a separate configuration surface with its own playbook:

    | If you need… | Use Control | Why this is not 1.11 |
    |---|---|---|
    | DLP policies, sensitivity labels, and Adaptive Protection signal feed | **1.5** | 1.5 governs data-at-rest classification; 1.11 governs the identity that touches it |
    | Unified Audit Log retention and `CopilotInteraction`, `Add member to role`, `Update conditional access policy`, PIM activation audit ingestion | **1.7** | 1.11 *generates* the audit events; 1.7 *configures* the audit pipeline that retains them |
    | Insider Risk Management workflow, response playbooks, alert triage for risky-user / risky-sign-in / risky-workload-identity escalations | **1.12** | 1.11 *emits* the Identity Protection risk signal; 1.12 *owns* the response workflow |
    | Data minimization and agent grounding scope (RCD/RSS, restricted SharePoint search, agent grounding sources) | **1.14** | 1.11 controls *who* can sign in; 1.14 controls *what* the agent can ground on |
    | eDiscovery of sign-in logs, PIM activation logs, CA-policy-change audit records for litigation / regulator response | **1.19** | 1.11 produces the evidence; 1.19 holds and produces it under FRCP / FINRA 8210 |
    | Adversarial input detection (Prompt Shields, Defender for Cloud TP for AI Workloads, Defender XDR Security for AI), risky-sign-in correlation | **1.21** | 1.21 correlates session evidence; 1.11 emits the sign-in events 1.21 joins to |
    | PIM lifecycle — provisioning, certification, deprovisioning, access reviews quarterly cadence | **2.5** | 1.11 configures the PIM *settings*; 2.5 owns the lifecycle |
    | Service principal / application consent governance, admin-consent workflow, consent-grant review | **2.8** | 1.11 *targets* SPs in CA workload-identity policies; 2.8 governs how those SPs are created |
    | Inactivity timeout enforcement in Power Platform Admin Center (PPAC) | **2.22** | 1.11 sets *sign-in frequency* (Entra layer); 2.22 sets *idle session timeout* (PPAC layer) |
    | Entra Agent ID identity lifecycle — registration, sponsor onboarding/offboarding, attribute schema governance | **2.26** | 1.11 *configures CA against* agent identities; 2.26 owns the lifecycle of those identities |
    | Agent inventory and metadata management — central inventory of agents and their owners | **3.1** | 1.11 references the inventory; 3.1 maintains it |
    | Copilot Hub and governance dashboard — operational metrics for the AI estate | **3.8** | 1.11 *feeds* sign-in / risk signals; 3.8 visualizes |
    | Incident reporting workflow / RCA / regulator notification mechanics (Form 8-K Item 1.05, Reg S-P 30-day, NYDFS 72-h, FINRA 4530) | **3.4 + AI Incident Response Playbook** | 1.11 *triggers* the incident pathway via §11 trigger table; 3.4 / the IR Playbook own the workflow |
    | Sentinel content-hub install, analytics rule tuning, hunting at scale | **3.9** | 1.11 references Sentinel only at the cross-plane analytics handoff |

!!! warning "Hedged-language reminder — supports, does not guarantee"
    Configuration of these surfaces **supports** firm compliance with **NYDFS 23 NYCRR Part 500 §500.7 (least privilege), §500.12 (universal MFA — fully effective Nov 1, 2025), §500.16 (BCDR), §500.17(a) (72-h cybersecurity event report)**, **FINRA Rules 3110 / 4511 / 4530 / Notice 25-07 (retired SMS/voice for FINRA Gateway access July 2025)**, **SEC Form 8-K Item 1.05 (4-business-day material-cyber-incident reporting)**, **Regulation S-P (30-day customer notification — May 2024 amendments)**, **SOX Section 404 (separation of duties for change management)**, **GLBA via FTC Safeguards Rule 16 CFR §314.4(c)(5) (in force June 2023 — strong authentication for systems holding customer information)**, **NIST SP 800-63B AAL3 (hardware-bound, verifier-impersonation-resistant)**, **CISA Phishing-Resistant Authenticator implementation guidance**, **OCC Bulletin 2011-12 / Federal Reserve SR 11-7**, **FFIEC SR 21-14 (risk-based MFA for employees, service accounts, and APIs)**, **CFTC Rule 1.31**. It does **not** by itself satisfy any obligation.

    Specifically prohibited overclaims for this control: "ensures phishing-resistant authentication", "guarantees no MFA bypass", "eliminates account-takeover risk", "prevents all credential theft", "real-time token revocation", "complete capture of all admin sign-ins", "guarantees compliance with NYDFS §500.12". Use the documented latencies (CAE near-real-time, typically <5 min, up to 1 h under degraded conditions; sign-in log hot-ingest 5–15 min, full ingest up to 6 h; PIM role activation ≤5 min; Authentication Methods policy propagation 1–24 h; CA policy propagation 5 min – 1 h; Identity Protection risk score 5–60 min; Agent ID registry near-real-time at preview). The Conditional Access Administrator, Entra Security Admin, Identity Governance Admin, and CISO must independently validate that the firm's WSP, exception process, break-glass governance, and incident-handling clocks reflect the **documented latencies and gaps** of the underlying Microsoft surfaces.

!!! info "What this walkthrough covers — surfaces & owners"
    | # | Surface | Portal path | Owner role | Latency posture |
    |---|---|---|---|---|
    | 1 | Authentication Methods — Policies | `entra.microsoft.com → Protection → Authentication methods → Policies` | Authentication Policy Administrator | 1–24 h propagation |
    | 2 | Authentication Methods — Registration Campaign | `entra.microsoft.com → Protection → Authentication methods → Registration campaign` | Authentication Policy Administrator | Effective at next sign-in |
    | 3 | Conditional Access — Authentication Strengths | `entra.microsoft.com → Protection → Conditional Access → Authentication strengths` | Conditional Access Administrator | Effective immediately on bound policy |
    | 4 | Conditional Access — Named Locations | `entra.microsoft.com → Protection → Conditional Access → Named locations` | Conditional Access Administrator | 5 min – 1 h |
    | 5 | Conditional Access — Policies (human users) | `entra.microsoft.com → Protection → Conditional Access → Policies` | Conditional Access Administrator | 5 min – 1 h |
    | 6 | Conditional Access — Workload Identities (Service Principals + Agent identities) | `entra.microsoft.com → Protection → Conditional Access → Policies → + New policy → Users and workload identities → Workload identities` | Conditional Access Administrator + AI Administrator | 5 min – 1 h |
    | 7 | Conditional Access — Microsoft Managed Policies | `entra.microsoft.com → Protection → Conditional Access → Policies` (filter `Source = Microsoft`) | Entra Security Admin | Per Microsoft cadence |
    | 8 | Continuous Access Evaluation + Token Protection (CA grant/session controls) | within each CA policy → Session controls | Conditional Access Administrator | CAE near-real-time, typically <5 min; up to 1 h degraded |
    | 9 | Identity Protection — risky users / risky sign-ins / risky workload identities | `entra.microsoft.com → Protection → Identity Protection` | Entra Security Admin | Risk score 5–60 min |
    | 10 | Privileged Identity Management — Microsoft Entra roles | `entra.microsoft.com → Identity governance → Privileged Identity Management → Microsoft Entra roles` | Entra Identity Governance Admin (PIM owner) + Entra Privileged Role Admin (assigner) | Activation ≤5 min |
    | 11 | Entra Agent ID — Registry / Sponsors / Custom Security Attributes / Collections | `entra.microsoft.com → Identity → Identity governance → Agent ID` (Public Preview, Frontier-gated) | AI Administrator + AI Governance Lead | Near-real-time at preview |
    | 12 | Sign-in logs filtered to ServicePrincipal + Agent | `entra.microsoft.com → Identity → Monitoring & health → Sign-in logs` | Entra Security Admin | Hot ingest 5–15 min; full ingest up to 6 h |

!!! danger "Entra Agent ID is Public Preview (Frontier-gated) — do not anchor WSP language to preview-only behavior"
    **Entra Agent ID** (the agent-identity registry, sponsor model, custom security attributes for agents, agent collections, and the ability to scope CA workload-identity policies to `AgentZone == 3`) is in **Public Preview** as of April 2026 under the Microsoft Frontier program. Configuration surfaces, schema, attribute names, and supported CA condition cards may change before general availability.

    By contrast, **Conditional Access for Workload Identities (CA WID)** — the underlying ability to scope CA policies to a Service Principal or managed identity — is **GA** (NOT preview). CA WID requires the **Microsoft Entra Workload Identities Premium SKU** licensed per service principal / managed identity / agent identity in the policy scope. Without the SKU the CA policy will **fail open** (will not enforce). Verify SKU before promoting any CA-WID policy from Report-only to Enabled (see §3 PRE-02 and §7).

    **Microsoft Managed Policies** (e.g., the `Block high-risk agents` baseline) appear in the standard `Conditional Access → Policies` blade with **`Source = Microsoft`** filter. There is **no** top-level "Microsoft Managed Policies" menu item in the Entra admin center — see anti-pattern AP-13.

---

## §0 Coverage boundary, identity-plane inventory, and portal vs PowerShell matrix

### 0.1 Coverage boundary

In scope for this walkthrough:

- Authentication Methods Policy configuration (FIDO2 with AAGUID restriction and attestation, Windows Hello for Business with cloud Kerberos trust, Certificate-Based Authentication, Microsoft Authenticator with passwordless + push number-matching, device-bound passkeys, registration campaign).
- Authentication Strengths — review of built-in strengths (`Phishing-resistant MFA`, `Passwordless MFA`, `MFA`) and creation of FSI-specific custom strengths (`FSI-Zone3-PhishingResistant`, `FSI-Zone2-Strong`, `FSI-BreakGlass-Hardware-Only`).
- Named Locations — trusted office IP ranges, allowed-countries / blocked-countries (FATF + OFAC overlap), retirement of legacy MFA Trusted IPs.
- Conditional Access policies for human users (CA-001 through CA-010), authored under the three-stage Report-only → Pilot → Broad lifecycle with two-admin author/approver separation.
- Conditional Access for Workload Identities (CA-WI-001 through CA-WI-003) — service principals, managed identities, and Entra Agent ID identities scoped via custom security attributes.
- Microsoft Managed Policies attestation and exception documentation.
- Continuous Access Evaluation enablement verification and revocation-trigger inventory; Token Protection grant configuration per resource; sign-in frequency and persistent browser session per zone.
- Privileged Identity Management for the seven AI-administration roles in §9 — eligible-only, MFA-on-activation through Authentication Strength binding, two-admin pattern for CA mutations, quarterly access reviews.
- Break-glass governance — minimum two cloud-only accounts, FIDO2-in-physical-safe, Sentinel sign-in alert, quarterly alternating activation test.
- Identity Protection — user-risk policy, sign-in-risk policy, risky-workload-identities review and auto-quarantine handoff.
- Entra Agent ID registry walkthrough, custom security attribute schema, sponsor assignment per zone, agent collection design, agent risk policies, and the linkage to §7 CA-WI policies.
- FSI incident-handling pathways from detected event → regulatory clock; 19-artifact SHA-256 evidence pack.

Out of scope (handled by sibling controls per the READ FIRST table above):

- DLP policy authoring and Adaptive Protection signal authoring (Control 1.5).
- Unified Audit Log retention and audit-pipeline ingestion (Control 1.7).
- Insider Risk Management workflow and response playbooks (Control 1.12).
- Data minimization, RCD/RSS, agent grounding scope (Controls 1.14 + 4.6).
- eDiscovery case management for sign-in evidence (Control 1.19).
- Adversarial-input detection authoring (Control 1.21).
- PIM lifecycle (Control 2.5 — provisioning, certification, deprovisioning); 1.11 configures the PIM *settings* layer only.
- Service principal consent governance (Control 2.8 — 1.11 *targets* SPs that are already consented).
- PPAC inactivity timeout (Control 2.22 — Entra-layer sign-in frequency belongs to 1.11; PPAC idle timeout belongs to 2.22).
- Entra Agent ID lifecycle / sponsor onboarding workflow (Control 2.26 — 1.11 reads the registry, 2.26 maintains it).
- Agent inventory metadata (Control 3.1).
- Incident reporting workflow / regulator notification mechanics (Control 3.4 + the [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md)).
- Sentinel content-hub install and analytics tuning (Control 3.9 — 1.11 emits sign-in / PIM / risk events; 3.9 ingests).

### 0.2 Five identity planes plus latency reality

Conditional Access in an FSI agent environment must be reasoned about across **five identity planes**, each with its own enrollment, session, and revocation surfaces. The single most common 1.11 deployment failure is configuring enrollment-strength only and leaving session-level controls (CAE, Token Protection, sign-in frequency) at their defaults.

| # | Plane | Enrollment surface | Session surface | Revocation surface | Typical latency |
|---|---|---|---|---|---|
| 1 | **Human user** | Authentication Methods Policy (FIDO2 / WHfB / CBA / device-bound passkey) bound to Authentication Strength | Sign-in frequency + persistent browser + CAE + Token Protection | CAE near-real-time on token revoke / disable / password change / risk detection / location change | CAE typically <5 min; sign-in frequency on schedule; Auth Methods policy 1–24 h |
| 2 | **Workload identity / Service Principal** | Service principal credential (cert preferred over secret) + Workload Identities Premium SKU | CA workload-identity policy → location + risk grant | CAE applies to workload identity tokens (subset); manual SP disable | SP disable propagation 5 min – 1 h |
| 3 | **Agent identity (Entra Agent ID, Public Preview)** | Agent registration in Agent ID registry + custom security attribute population (`AgentZone`, `DataClassification`, `RegulatoryScope`, `SponsorObjectId`) + sponsor assignment | CA-WI policy scoped to `AgentZone == 3` (or by collection); rides on top of CA WID | Auto-quarantine via Agent collection move on Identity Protection High risk | Risk score 5–60 min; collection-move near-real-time at preview |
| 4 | **Device** | Intune compliance + Hello for Business / TPM 2.0 attestation + device registration (Entra-joined / Hybrid Entra-joined / compliant) | CA grant `Require compliant device` or `Require Hybrid Entra joined device`; Token Protection requires Entra-joined or compliant Entra-joined Windows | Device wipe / disable through Intune | Compliance evaluation 5–60 min |
| 5 | **Session** | Token issuance at sign-in | CAE, Token Protection, sign-in frequency, persistent browser, resilience defaults | CAE event subscriptions | CAE typically <5 min, up to 1 h degraded |

!!! warning "Latency reality — do not write 'real-time' or 'instantaneous' into the WSP"
    **Continuous Access Evaluation** is **near-real-time, typically <5 min** after the revocation trigger. Under degraded conditions, Microsoft documents up to **1 h** propagation. WSP language that promises "real-time token revocation", "instantaneous account disable", or "complete capture of all admin sign-ins" overstates Microsoft surface capability and creates regulatory exposure under FINRA 25-07 (which calls for documented operational realism in AI WSPs). Use the documented latencies; build a **1 h revocation buffer** into NYDFS §500.17(a) 72-h cybersecurity-event-report procedures.

### 0.3 Plane separation — enrollment vs session vs revocation

Three traps to avoid:

1. **Enrollment-only trap.** Configuring FIDO2 + Authentication Strength `Phishing-resistant MFA` on a Zone 3 admin policy without setting sign-in frequency to 4 h leaves a long-lived session vulnerable to AiTM token replay even after credentials are rotated. Bind enrollment + session + revocation in the same policy review.
2. **Session-only trap.** Enabling Token Protection without verifying the device is Entra-joined / compliant Entra-joined silently fails open (Token Protection is a no-op on unmanaged devices). Pair Token Protection with `Require compliant device` for Zone 3 admin sessions.
3. **Revocation-only trap.** Relying on CAE for revocation without periodically re-attesting the eligible PIM assignment list lets stale eligibles persist. Quarterly Access Review per §9.5 closes this.

### 0.4 Portal vs PowerShell matrix

| Configuration step | Portal? | PowerShell / Graph? | Notes |
|---|---|---|---|
| CA policy CRUD | ✅ | ✅ Graph PowerShell `New-MgIdentityConditionalAccessPolicy` | Portal recommended for first-time + What-If; Graph for scale |
| Named Locations | ✅ | ✅ `New-MgIdentityConditionalAccessNamedLocation` | Either |
| Authentication Strengths | ✅ | ✅ `New-MgPolicyAuthenticationStrengthPolicy` | Portal recommended for visualization |
| Authentication Methods Policy | ✅ | ✅ `Update-MgPolicyAuthenticationMethodPolicyAuthenticationMethodConfiguration` | Portal recommended for AAGUID UI |
| Registration Campaign | ✅ | ✅ Graph beta | Portal recommended |
| CA Workload Identities policy | ✅ | ✅ Graph (workload identity selector) | Portal recommended for first-time |
| Microsoft Managed Policies (view + report-only/enabled toggle) | ✅ (filter `Source = Microsoft`) | Limited (read via Graph; toggle UI-first) | **Portal-only for toggle as of April 2026** |
| Entra Agent ID registry CRUD | ✅ (Preview UI) | Limited (Graph beta) | **Portal-first while preview** |
| Custom Security Attributes (define schema + assign per agent) | ✅ | ✅ Graph `directoryObjects/{id}/customSecurityAttributes` | Portal recommended for schema; Graph for bulk assign |
| Agent collections | ✅ | Limited | Portal-first |
| Sponsor assignment | ✅ | Limited | Portal-first |
| Agent risk policies | ✅ | ✅ Graph (Identity Protection beta) | Either |
| PIM role settings | ✅ | ✅ Graph `roleManagementPolicy` | Portal recommended for two-admin audit trail |
| PIM eligible/active assignments | ✅ | ✅ Graph `roleAssignmentSchedule*` | Either |
| PIM activation | ✅ | ✅ `New-MgRoleManagementDirectoryRoleAssignmentScheduleRequest` | Portal recommended; activations are auditable either way |
| PIM access reviews | ✅ | ✅ Graph `accessReviews` | Either |
| Identity Protection risk policies | ✅ | ✅ Graph beta | Portal recommended |
| Sign-in logs export (filtered to SP + Agent) | ✅ (CSV / JSON) | ✅ Graph `auditLogs/signIns` + Log Analytics | PowerShell required for chain-of-custody automation |
| Audit logs export (PIM, CA-policy mutation) | ✅ | ✅ Graph `auditLogs/directoryAudits` | Either |
| What-If tool | ✅ | Limited | **Portal-only** for the visualizer |
| CAE configuration verification | ✅ (per CA policy session controls) | ✅ Graph (read CA policy session controls) | Either |
| Token Protection grant | ✅ (CA session control) | ✅ Graph | Portal recommended |
| Two-admin change audit (Sentinel rule) | n/a | ✅ KQL in Sentinel against `MicrosoftGraphActivityLogs` + `AuditLogs` | Sentinel is the enforcement surface |

The companion [`powershell-setup.md`](powershell-setup.md) in this directory mirrors every PowerShell-eligible step; the present walkthrough is the portal path. The companion [`conditional-access-agent-templates.md`](conditional-access-agent-templates.md) holds the JSON policy templates referenced by §6 and §7 (do not duplicate them here — reference them by `CA-NNN` ID).

---

## §1 Surface inventory with latency posture

The 12-row inventory in the front-matter `What this walkthrough covers` admonition is reproduced and expanded here with explicit latency, throttle, and propagation notes used by §11 incident clocks and §13 evidence-pack timing.

| # | Surface | Hot-path latency | Full-propagation upper bound | Throttle / quota notes |
|---|---|---|---|---|
| 1 | Authentication Methods Policy | Effective at next user sign-in | 1–24 h | Tenant-wide policy mutation rate-limited; batch with care |
| 2 | Registration Campaign | Effective at next sign-in | 1–24 h | Coverage report exported via Authentication Methods activity report |
| 3 | Authentication Strengths | Immediate on bound policy | 5 min – 1 h | Strength definition mutation propagates with bound CA policy |
| 4 | Named Locations | 5 min | 1 h | IP-range payload size capped — split very large lists |
| 5 | CA Policies (human) | 5 min | 1 h | What-If results may lag policy state by up to 5 min |
| 6 | CA Policies (workload identity) | 5 min | 1 h | **Requires Workload Identities Premium SKU per SP/MI/agent in scope — fails open without** |
| 7 | Microsoft Managed Policies | Per Microsoft cadence | Per Microsoft cadence | Tenant cannot author; can only toggle Report-only / Enabled / Off and document exceptions |
| 8 | CAE / Token Protection / sign-in frequency / persistent browser | CAE typically <5 min; sign-in frequency on schedule | CAE up to 1 h degraded; token-protection enforcement immediate on policy save | Token Protection requires Entra-joined or compliant Entra-joined Windows + Edge / supported app |
| 9 | Identity Protection — risky users / sign-ins / workload identities | Risk score 5–60 min | 24 h for full risk-feed reconciliation | Workload identity risk requires Workload Identities Premium |
| 10 | PIM | Activation ≤5 min | Role propagation up to 1 h | Activation alert delivery dependent on Sentinel ingestion lag |
| 11 | Entra Agent ID registry | Near-real-time at preview | TBD at GA | **Public Preview; schema may change before GA** |
| 12 | Sign-in logs (SP + Agent filter) | Hot ingest 5–15 min | Full ingest up to 6 h | Log Analytics workspace export required for >30 d retention |

---

## §2 Sovereign cloud applicability matrix

!!! danger "Cross-cloud parity is not symmetric — verify at deploy time"
    The matrix below reflects publicly documented availability as of **April 2026**. Microsoft adds and removes sovereign-cloud parity on a per-feature, per-region cadence. Re-verify against the [Microsoft 365 Government service description](https://learn.microsoft.com/en-us/office365/servicedescriptions/office-365-platform-service-description/office-365-us-government/office-365-us-government), the [Conditional Access overview](https://learn.microsoft.com/en-us/entra/identity/conditional-access/overview), and the [Microsoft Entra Agent ID documentation](https://learn.microsoft.com/en-us/entra/architecture/secure-resource-management) **before** treating any item below as a primary control in GCC / GCC High / DoD.

| Capability | Commercial | GCC | GCC High | DoD |
|---|---|---|---|---|
| Conditional Access (human users) | GA | GA | GA | GA |
| Conditional Access for Workload Identities (CA WID) — **GA** | GA | GA | GA | GA |
| Workload Identities Premium SKU | GA | GA | Verify | Verify |
| Microsoft Entra Agent ID (Public Preview, Frontier) | **Public Preview** | **Verify — staged rollout** | **Likely unavailable — verify** | **Likely unavailable — verify** |
| Microsoft Managed Policies (`Block high-risk agents` baseline) | GA | **Verify — rolling** | **Verify — rolling** | **Verify — rolling** |
| FIDO2 security keys (Authentication Methods) | GA | GA | GA | GA |
| Windows Hello for Business — cloud Kerberos trust | GA | GA | GA | GA |
| Windows Hello for Business — **key trust (legacy, deprecation path)** | GA — migrate off | GA — migrate off | GA — migrate off | GA — migrate off |
| Windows Hello for Business — certificate trust | GA | GA | GA | GA |
| Certificate-Based Authentication (CBA) | GA | GA | GA | GA |
| Device-bound passkey in Microsoft Authenticator | GA | GA (Verify) | **Verify — FedRAMP-High Authenticator build required** | **Verify — additional restrictions** |
| **Synced (cross-device) passkey** (iCloud Keychain / Google Password Manager) | Available — **NOT AAL3** | Available — NOT AAL3 | Restricted | Restricted |
| Microsoft Authenticator — passwordless + push w/ number-matching | GA | GA | **GCC-H requires the FedRAMP-High Authenticator build; consumer Authenticator NOT approved** | **Additional restrictions; CBA + FIDO2 are the safer Zone 3 posture** |
| Continuous Access Evaluation (CAE) — **GA, default On for new tenants** | GA | GA | GA | GA |
| Token Protection for sign-in sessions — **Public Preview (early 2026)** | Public Preview | Public Preview / Verify | Likely unavailable — verify | Likely unavailable — verify |
| Sign-in frequency + persistent browser (CA session control) | GA | GA | GA | GA |
| Privileged Identity Management for Microsoft Entra roles | GA | GA | GA | GA |
| Identity Protection — risky users / sign-ins | GA | GA | GA | GA |
| Identity Protection — risky **workload identities** | GA | GA | Verify | Verify |
| Sign-in logs filtered to ServicePrincipal + Agent | GA | GA | GA | GA |
| Sentinel ingestion of CA + PIM + sign-in events | GA | GA | GA Az Gov | GA Az Gov |

### 2.1 Per-cloud caveats

**Commercial.** Reference posture for this walkthrough. All capabilities GA except Entra Agent ID (Public Preview, Frontier) and Token Protection (Public Preview, early 2026).

**GCC.** Treat as Commercial-minus-30-days. Entra Agent ID staged rollout — re-verify at deploy time. Microsoft Authenticator FedRAMP build availability — confirm with the GCC service description.

**GCC High.** Microsoft Entra Agent ID and Microsoft Managed Policies are typically lagging or unavailable. The consumer Microsoft Authenticator is **not** approved; only the **FedRAMP-High Authenticator** build is approved, and even then CBA + FIDO2 are the safer Zone 3 posture for phishing-resistant MFA. If Agent ID is unavailable in GCC High, **Zone 3 agent CA must be enforced via service-principal CA-WID policies (CA-WI-001 / CA-WI-002) without `AgentZone == 3` attribute scoping**; document the gap to the AI Governance Lead and Compliance Officer.

**DoD.** As GCC High with greater lag. If Entra Agent ID is not deployed, agent CA reduces to standard CA-WID against Service Principals; document the reduced surface to the Designated Supervisor and CISO.

### 2.2 Compensating controls when a capability is unavailable

| Unavailable capability | Compensating control | Risk-register entry (Control 1.2) |
|---|---|---|
| Entra Agent ID registry / custom security attribute scoping | CA-WID against named SP IDs from the agent inventory (Control 3.1); attribute-based scoping replaced with explicit SP allow-list per zone | Yes — recall-completeness assumption documented |
| Token Protection on a given resource | Tighter sign-in frequency (4 h Zone 3) + Require compliant device + Require phishing-resistant MFA strength | Yes — note replay-risk window |
| FedRAMP-High Authenticator availability | Hard requirement for FIDO2 + CBA only on Zone 3 in GCC-H/DoD; SMS / voice / email OTP / consumer Authenticator disabled | Yes — note method-coverage delta |
| Microsoft Managed Policies in sovereign cloud | Author equivalent customer-managed CA policy mirroring the `Block high-risk agents` baseline; document divergence at each Microsoft update | Yes |

---

## §3 Pre-flight gates (PRE-01 … PRE-18)

Before configuring any surface in this walkthrough, complete the following gates. Each gate has a documented owner, an evidence artifact, and a rollback path. Do **not** skip a gate by attestation only — every gate produces a tangible artifact for the §14 evidence pack.

| # | Gate | Owner | Evidence | Rollback path |
|---|---|---|---|---|
| **PRE-01** | Tenant licensing confirmed: Entra ID P2 (PIM, Identity Protection, Access Reviews) for all in-scope admins | Entra Global Admin | License report (`Get-MgSubscribedSku` CSV) | N/A — gate; cannot proceed without P2 |
| **PRE-02** | **Microsoft Entra Workload Identities Premium SKU** licensed per SP / managed identity / agent that will appear in any CA-WI policy in §7 | Entra Global Admin | SKU assignment export | Without SKU, CA-WI policies fail open — do not enable |
| **PRE-03** | Entra Agent ID Frontier-program enrollment confirmed (if scoping CA against `AgentZone == 3` in §7 / §8) | AI Administrator | Frontier program enrollment confirmation | If denied, document the gap and use named-SP allow-list per §2.2 |
| **PRE-04** | Two break-glass cloud-only accounts created, FIDO2 keys provisioned to each, keys stored in two physically separate safes with split combination knowledge | CISO + Compliance Officer | Break-glass governance record (account UPN, FIDO2 AAGUID, safe location, last-tested date) | If safe access broken, reissue FIDO2 keys before any CA policy that targets All Users |
| **PRE-05** | Sentinel rule active: alert on any sign-in by either break-glass UPN to **CISO + on-call SOC + Compliance Officer**; alert tested within last 90 d | Sentinel Engineer + CISO | Rule definition + test alert evidence | Disable Sentinel rule update window per change-management |
| **PRE-06** | Quarterly alternating break-glass activation test complete and signed off | CISO | Test record (UTC timestamp, key ID, validator UPN) | N/A — overdue test triggers Compliance Committee escalation |
| **PRE-07** | Inventory of all Service Principals (Control 2.8) + agents (Control 3.1) reconciled to Entra `Enterprise applications` and Agent ID registry | AI Administrator + AI Governance Lead | Reconciled CSV with SP `objectId`, agent `objectId`, owner UPN, sponsor UPN, zone | Discrepancy → block CA-WI policy promotion until resolved |
| **PRE-08** | All in-scope admins have FIDO2 security keys (or device-bound passkeys) registered and **tested** through `https://aka.ms/mysecurityinfo` — minimum two methods per admin | Authentication Administrator + each admin | `UserRegistrationDetails` Graph export | If admin missing methods, exclude from Zone 3 policies until provisioned |
| **PRE-09** | `Conditional Access — What-If` tool walkthrough complete for each authored policy against (a) typical user, (b) break-glass account, (c) external guest if applicable | Conditional Access Administrator | What-If screenshots (PNG with policy ID + UTC timestamp) | Discrepancy → revise policy before promotion to Report-only |
| **PRE-10** | Authentication Methods migration from legacy "MFA portal" / per-user MFA / Security Defaults complete; legacy controls disabled | Authentication Policy Administrator | Authentication Methods activity report showing 0 sign-ins via legacy methods over 30 d | Roll back legacy disablement if evidence shows residual dependencies |
| **PRE-11** | Communication plan published to all in-scope users 7+ days before any policy promotion to Pilot, 14+ days before Broad rollout | Change Manager + Communications | Email / Teams post / intranet artifact | Pause rollout if comms gap detected |
| **PRE-12** | Service desk runbook updated with: (a) FIDO2 reset path, (b) lost-passkey path, (c) WHfB re-enrollment path, (d) device-bound passkey reset path, (e) self-service password reset (SSPR) integration | Service Desk Lead + Authentication Administrator | Runbook URL + version | Block policy promotion if runbook out of date |
| **PRE-13** | Two-admin author/approver assignments confirmed for all 10 CA policies in §6 and 3 in §7 (author UPN ≠ approver UPN; both must hold Conditional Access Administrator at activation time) | Conditional Access Administrator + Entra Privileged Role Admin | Two-admin assignment matrix | Cancel policy authorship if same-admin pattern detected |
| **PRE-14** | Sentinel KQL detection live for unauthorized CA policy mutation (compares `AuditLogs` `Update conditional access policy` against the two-admin assignment matrix from PRE-13); tested in last 90 d | Sentinel Engineer | KQL rule + test evidence | Escalate to Insider Risk (Control 1.12) if detection silent |
| **PRE-15** | Audit log retention confirmed minimum 1 year (Audit Premium) with Sentinel ingestion of `AuditLogs`, `SignInLogs`, `MicrosoftGraphActivityLogs`, `AADRiskyUsers`, `AADRiskyServicePrincipals`, `AADUserRiskEvents` | Compliance Officer + Sentinel Engineer | Workspace export evidence + retention setting screenshot | Block §6/§7 promotion if retention <1 y |
| **PRE-16** | Custom Security Attribute schema for `AgentZone`, `DataClassification`, `RegulatoryScope`, `SponsorObjectId` defined and access-scoped (Attribute Definition Reader / Attribute Assignment Administrator) | AI Governance Lead + Entra Identity Governance Admin | Schema export + role assignment matrix | Schema may not be edited after CA-WI policies bind to it without exception process |
| **PRE-17** | Power Platform Admin Center / Microsoft 365 admin center cross-reference: PPAC inactivity timeout (Control 2.22) configured before Entra-layer sign-in frequency (§10), to avoid double-counting session-expiry confusion in user comms | Power Platform Admin + Conditional Access Administrator | PPAC config screenshot | If misordered, re-issue user comms before §10 promotion |
| **PRE-18** | Sovereign-cloud confirmation per §2 — capability matrix re-verified for the deploy environment (Commercial / GCC / GCC-H / DoD); compensating controls per §2.2 documented for any unavailable capability | CISO + Compliance Officer | Signed sovereign-cloud applicability matrix | If matrix incomplete, defer Zone 3 promotion |

!!! danger "Two break-glass accounts are non-negotiable"
    NIST SP 800-63B §5.2.10, FFIEC Information Security Handbook, NYDFS §500.16, and FINRA Rule 4370 (BCDR) all expect **resilient privileged access** independent of any single MFA factor failure. The pattern is: (a) two cloud-only accounts with ultra-strong randomly-generated passwords stored in a sealed envelope in two physically separate safes; (b) two FIDO2 hardware keys per account, each in its own safe; (c) all CA policies in §6 / §7 explicitly **exclude** these two accounts; (d) Sentinel rule per PRE-05 alerts CISO + SOC + Compliance Officer on any sign-in; (e) quarterly alternating activation test per PRE-06 to confirm both are usable. Do **not** automate break-glass account creation through Graph PowerShell — manual portal creation with two-admin witness is required for evidentiary integrity.

---

## §4 Authentication Methods Policy — passwordless-first baseline

**Portal path:** `entra.microsoft.com → Protection → Authentication methods → Policies`<br>
**Owner role:** Authentication Policy Administrator (canonical short-name: *Authentication Administrator* per `docs/reference/role-catalog.md`; Microsoft built-in display name *Authentication Policy Administrator*)<br>
**Propagation:** 1–24 hours after save; effective at next user sign-in<br>
**Reference:** [Microsoft Entra authentication methods policy](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-methods)

### 4.1 Method-by-method enablement table

| Method | Action | Target group(s) | Why for FSI |
|---|---|---|---|
| **FIDO2 security key** | **Enable** | All Users + dedicated `BreakGlass-Users` group | NIST SP 800-63B AAL3-eligible when paired with attested AAGUID; phishing-resistant per CISA fact sheet |
| **Microsoft Authenticator (passwordless + push, number-matching ON)** | **Enable** | All Users (Zone 1/2); for Zone 3 use **device-bound passkey** mode only | Passwordless Authenticator without device-bound passkey is **NOT AAL3** — Zone 3 admins must use device-bound passkey, FIDO2, or CBA |
| **Windows Hello for Business** | **Enable** + select **Cloud Kerberos trust** as deployment model | All Entra-joined Windows | Cloud Kerberos trust supersedes key trust (deprecation path); cert trust still supported. Phishing-resistant per CISA |
| **Certificate-based authentication (CBA)** | **Enable** + bind to PKI per Microsoft CBA configuration guide | Admins + smartcard-issued staff | NIST SP 800-63B AAL3 with hardware-backed certificate; required for many federal-adjacent FSI roles |
| **Passkey (FIDO2) — synced cross-device** | **Disable** for Zone 3 admins (via authentication strength, see §5); allow for Zone 1/2 only | Zone 1/2 only | Synced passkeys (iCloud Keychain / Google Password Manager) are **not** AAL3 — explicitly excluded from Zone 3 admin authentication strength |
| **Temporary Access Pass (TAP)** | **Enable** with single-use, ≤8 h lifetime | Onboarding admins, FIDO2-reset path | Required for the lost-key recovery path; must NOT be a permanent factor |
| **SMS** | **Disable** for Zone 2/3; allow Zone 1 only with documented compensating control | Zone 1 only (with attestation) | NIST SP 800-63B deprecated for AAL2/3; FINRA Notice 25-07 retired for FINRA Gateway access (July 2025); NYDFS §500.12 effectively disallows for privileged use |
| **Voice call** | **Disable** | None | Same as SMS — phishable; not AAL2/3 eligible |
| **Email OTP** | **Disable** for internal users; allow for B2B guest sign-in only with risk acceptance | B2B guests only | Email OTP is not phishing-resistant; documented compensating control (Conditional Access for guests) required |
| **Hardware OTP token** | **Enable** as secondary fallback only; not primary | Admins as fallback | OATH hardware tokens AAL2 — useful as break-glass fallback but FIDO2 / CBA preferred for Zone 3 primary |
| **Third-party software OATH** | **Disable** | None | Cannot enforce verifier-impersonation-resistance |
| **Software OATH (Authenticator app TOTP code)** | **Disable** for Zone 3; allowed for Zone 1/2 fallback | Zone 1/2 fallback | Not phishing-resistant by itself |

!!! warning "FIDO2 AAGUID restriction is the single highest-leverage Zone 3 control"
    Without **AAGUID restriction with attestation enforcement**, an attacker who phishes a Zone 3 admin into provisioning a non-attested or non-FIPS-validated FIDO2 key can present credentials that satisfy `Phishing-resistant MFA` strength but bypass the firm's hardware-vetting policy. Configure the **FIDO2 settings**:
    
    1. Navigate `Protection → Authentication methods → Policies → FIDO2 security key → Configure`.
    2. **Enforce attestation:** ON.
    3. **Enforce key restrictions:** ON; **Restrict specific keys:** **Allow** (allow-list, not block-list).
    4. Add the **AAGUIDs** of FIPS 140-3 validated keys approved by your CISO + Compliance Officer (typical FSI baseline: YubiKey 5 series FIPS, Feitian FIPS, Google Titan, AuthenTrend).
    5. Document the AAGUID allow-list version + signature in your evidence pack (artifact EP-04).

### 4.2 FIDO2 attestation + AAGUID allow-list portal steps

1. Sign in as **Authentication Policy Administrator** to `entra.microsoft.com`.
2. Browse `Protection → Authentication methods → Policies`.
3. Select **FIDO2 security key** → **Configure**.
4. **Allow self-service set up:** ON.
5. **Enforce attestation:** ON.
6. **Enforce key restrictions:** ON; **Restrict specific keys:** **Allow**.
7. Paste the AAGUID list from the firm's approved-keys document. Each AAGUID is on its own line, lowercase GUID format.
8. Click **Save**.
9. Capture screenshot with policy ID + UTC timestamp → save as artifact `EP-04-FIDO2-AAGUID-Allowlist-{YYYYMMDD}.png` in the evidence repository.
10. Wait minimum 1 hour, maximum 24 hours, then run `Get-MgPolicyAuthenticationMethodPolicyAuthenticationMethodConfiguration -AuthenticationMethodConfigurationId fido2` to confirm propagation; export JSON → `EP-04-FIDO2-Policy-State-{YYYYMMDD}.json`.

### 4.3 Windows Hello for Business — cloud Kerberos trust

WHfB has three deployment models: **key trust** (legacy, deprecation path — do not deploy new), **certificate trust** (still supported), and **cloud Kerberos trust** (recommended, simpler, GA). Choose **cloud Kerberos trust** for any new deployment unless there is a documented CBA dependency that requires certificate trust.

Portal steps:

1. `Protection → Authentication methods → Policies → Windows Hello for Business → Configure`.
2. **Enable** for **All users** (or scoped group during pilot).
3. **Authentication type:** Cloud Kerberos trust.
4. Combine with Intune **Account Protection → Windows Hello for Business** profile to enforce TPM 2.0 + 8-digit PIN minimum + biometric where supported.
5. Save → screenshot → artifact `EP-05-WHfB-CloudKerberos-{YYYYMMDD}.png`.

### 4.4 Certificate-Based Authentication (CBA)

For FSI environments with existing PKI (common for institutional brokerage and bank-holding companies), CBA provides AAL3 authentication using hardware-bound smartcards. Configure per [Microsoft Entra CBA configuration](https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-certificate-based-authentication):

1. Upload trusted CA cert chain to Entra (`Protection → Show more → Security center / Identity Secure Score → Certificate authorities` — exact path varies; reference Microsoft Learn).
2. Enable CBA in Authentication Methods Policy.
3. Configure **Authentication binding** rules — map cert OID / issuer / policy OID to single-factor or multi-factor based on hardware-binding evidence.
4. Configure **Username binding** — Principal Name is preferred for FSI to avoid cert-rotation outages.
5. Save → `EP-06-CBA-Configuration-{YYYYMMDD}.png` + `EP-06-CBA-Policy-{YYYYMMDD}.json`.

### 4.5 Device-bound passkey in Microsoft Authenticator (Zone 3 only)

The **device-bound passkey** mode of Microsoft Authenticator is AAL3-eligible because the private key is bound to the device's hardware-backed keystore (iOS Secure Enclave / Android StrongBox) and never syncs to iCloud Keychain or Google Password Manager. The **synced passkey** mode is **NOT** AAL3 and must be excluded from Zone 3 authentication strengths (see §5).

Portal steps:

1. `Protection → Authentication methods → Policies → Microsoft Authenticator → Configure`.
2. **Allow use of Microsoft Authenticator OTP:** OFF for Zone 3 (force passwordless or passkey).
3. Under **Passkey (Preview where applicable)** settings: enable for the Zone 3 admin group; **disable cross-device sync**.
4. Pair with FIDO2 attestation requirements via the `FSI-Zone3-PhishingResistant` authentication strength (§5).
5. `EP-07-Authenticator-PasskeyMode-{YYYYMMDD}.png`.

### 4.6 Registration campaign

Force users without a phishing-resistant method to register one at next interactive sign-in:

1. `Protection → Authentication methods → Registration campaign`.
2. **State:** Enabled.
3. **Days allowed to snooze:** 0 (Zone 3 admins) / 7 (Zone 2) / 14 (Zone 1).
4. **Methods:** Microsoft Authenticator (push) + FIDO2 security key — recommended order Authenticator first for end-user friendliness, FIDO2 first for admins.
5. Include groups: All licensed users **except** `BreakGlass-Users`.
6. Exclude: `BreakGlass-Users`, service-account UPNs (no interactive sign-in).
7. Save → `EP-08-RegistrationCampaign-{YYYYMMDD}.png`.

### 4.7 Suppressing legacy authentication endpoints

Authentication Methods Policy alone does not block legacy authentication (POP3/IMAP/SMTP basic, MAPI/CDO, Older Office). The block is enforced via CA policy `CA-001 Block legacy authentication` in §6. Confirm here that **Security Defaults** is **OFF** (`Properties → Manage Security defaults → Disabled`); otherwise CA policies are ignored.

---

## §5 Authentication Strengths — built-in plus three FSI custom strengths

**Portal path:** `entra.microsoft.com → Protection → Conditional Access → Authentication strengths`<br>
**Owner role:** Conditional Access Administrator<br>
**Reference:** [Microsoft Entra Conditional Access authentication strength](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths)

### 5.1 Built-in strengths — review only

Microsoft ships three built-in strengths. Do not delete or modify them; reference them where appropriate.

| Built-in strength | Allowed methods | Use in this walkthrough |
|---|---|---|
| **Phishing-resistant MFA** | Windows Hello for Business, FIDO2 security key, certificate-based authentication (multi-factor) | Reference baseline for Zone 3 admins; supplemented by `FSI-Zone3-PhishingResistant` to add device-bound passkey + AAGUID enforcement |
| **Passwordless MFA** | WHfB, FIDO2, Microsoft Authenticator (passwordless) | Used by `FSI-Zone2-Strong` |
| **MFA** | Any combination of password + second factor (incl. SMS/voice) | **Do not use for Zone 2 or Zone 3** — too permissive |

### 5.2 Custom strength: `FSI-Zone3-PhishingResistant`

Goal: enforce hardware-backed phishing-resistant MFA on Zone 3 admin sign-ins; explicitly exclude synced passkeys.

1. `Protection → Conditional Access → Authentication strengths → + New authentication strength`.
2. **Name:** `FSI-Zone3-PhishingResistant`.
3. **Description:** `Zone 3 admin baseline — FIDO2 attested keys (AAGUID allow-list per Authentication Methods Policy), WHfB cloud Kerberos trust, CBA hardware-bound, device-bound passkey in Microsoft Authenticator. Synced passkeys explicitly excluded. Aligned to NIST SP 800-63B AAL3.`
4. **Methods:**
    - ✅ FIDO2 security key
    - ✅ Windows Hello for Business
    - ✅ Certificate-based authentication (multi-factor)
    - ✅ Passkeys (Microsoft Authenticator) — **device-bound only** (filter via FIDO2 settings — see step 6)
5. **Save**.
6. **FIDO2 advanced settings within the strength:** ensure **Enforce attestation** ON and the AAGUID allow-list inherited from §4.2 applies. Synced passkey AAGUIDs are not on the allow-list, so they are implicitly excluded.
7. Screenshot → `EP-09-AuthStrength-Zone3-{YYYYMMDD}.png`.
8. Reference this strength from CA-002, CA-003, CA-006, CA-007, CA-WI-001 (where applicable).

### 5.3 Custom strength: `FSI-Zone2-Strong`

Goal: passwordless or strong MFA for Zone 2 (team-shared agents, business-team self-service, Copilot Studio non-DLP-edge work).

1. **+ New authentication strength**.
2. **Name:** `FSI-Zone2-Strong`.
3. **Description:** `Zone 2 baseline — passwordless preferred, push w/ number-matching acceptable, no SMS / voice / email OTP`.
4. **Methods:**
    - ✅ FIDO2 security key
    - ✅ Windows Hello for Business
    - ✅ Microsoft Authenticator (passwordless)
    - ✅ Microsoft Authenticator (push notification with number-matching)
    - ✅ Certificate-based authentication (multi-factor)
    - ❌ SMS, voice call, email OTP, third-party software OATH
5. Save → `EP-10-AuthStrength-Zone2-{YYYYMMDD}.png`.

### 5.4 Custom strength: `FSI-BreakGlass-Hardware-Only`

Goal: ensure break-glass accounts can sign in **only** with the FIDO2 keys provisioned to them per PRE-04.

1. **+ New authentication strength**.
2. **Name:** `FSI-BreakGlass-Hardware-Only`.
3. **Description:** `Break-glass accounts — FIDO2 attested key from approved AAGUID list ONLY. No fallback. Aligned to NYDFS §500.16, FFIEC BCDR.`
4. **Methods:**
    - ✅ FIDO2 security key (only)
5. Save → `EP-11-AuthStrength-BreakGlass-{YYYYMMDD}.png`.
6. This strength is referenced **only** by `CA-009 Break-glass account governance` in §6.

---

## §6 Named Locations

**Portal path:** `entra.microsoft.com → Protection → Conditional Access → Named locations`<br>
**Owner role:** Conditional Access Administrator<br>
**Reference:** [Using the location condition in a Conditional Access policy](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-assignment-network)

!!! warning "Legacy MFA Trusted IPs is deprecated"
    The old `Multi-Factor Authentication → Service settings → Trusted IPs` blade in the legacy MFA portal is **deprecated**. Migrate any trusted IP ranges to **Conditional Access → Named locations → Mark as trusted location**. Failing to migrate leaves trusted-IP behavior in an undefined state when CA evaluates a policy.

### 6.1 Trusted office IPs

1. `+ Countries location` is below; first create **+ IP ranges location**.
2. **Name:** `FSI-TrustedOffices-{Region}` (one per regional office, or one consolidated if firm-policy allows).
3. **Mark as trusted location:** ON (this elevates these IPs to a separate trust tier; CA conditions can reference `MFA Trusted IPs` deprecated state vs. `Trusted Named Locations`).
4. Paste each office's egress IP range in CIDR notation (`/24`, `/29`, etc.).
5. Save → `EP-12-NamedLocation-Offices-{YYYYMMDD}.json` (export via Graph for chain-of-custody).

### 6.2 Allowed countries (geofence)

1. `+ Countries location`.
2. **Name:** `FSI-AllowedCountries`.
3. **Country lookup method:** GPS coordinate (preferred) or IP address.
4. Select the countries from which the firm permits sign-in (typically: US, Canada, UK, EU member states, Israel, Australia, Singapore, Hong Kong, Japan).
5. **Include unknown countries/regions:** OFF.
6. Save → `EP-13-NamedLocation-AllowedCountries-{YYYYMMDD}.json`.

### 6.3 Blocked countries (FATF + OFAC overlap)

1. `+ Countries location`.
2. **Name:** `FSI-BlockedCountries-FATF-OFAC`.
3. Select all countries appearing on either: (a) FATF black-list / grey-list; (b) OFAC comprehensive sanctions list (Cuba, Iran, North Korea, Syria, Russia where applicable, Belarus where applicable, Crimea / DNR / LNR regions). Re-verify quarterly.
4. **Include unknown countries/regions:** ON (treat geo-IP unknown as untrusted).
5. Save → `EP-14-NamedLocation-BlockedCountries-{YYYYMMDD}.json`.
6. Reference from `CA-005 Block sign-in from blocked countries` in §7.

### 6.4 Maintenance cadence

| Cadence | Owner | Action |
|---|---|---|
| Weekly | Entra Security Admin | Review sign-in logs for `Risky IP` flags from outside `FSI-AllowedCountries` |
| Monthly | Network Engineering + Conditional Access Administrator | Reconcile office-egress CIDR drift |
| Quarterly | Compliance Officer | Re-verify blocked-country list against current FATF + OFAC |
| Ad-hoc | CISO | Add country to blocked list within 24 h of any new OFAC designation |

---

## §7 Conditional Access policies for human users (CA-001 … CA-010)

**Portal path:** `entra.microsoft.com → Protection → Conditional Access → Policies`<br>
**Owner role:** Conditional Access Administrator (with two-admin pattern per PRE-13)<br>
**Reference:** [Plan a Conditional Access deployment](https://learn.microsoft.com/en-us/entra/identity/conditional-access/plan-conditional-access)

### 7.1 Three-stage rollout per policy

Every policy in §7 and §8 follows the same lifecycle:

| Stage | Duration | Acceptance signal | Two-admin approval |
|---|---|---|---|
| **Report-only** | 7–14 days | What-If matches actual sign-in evaluations in `Sign-in logs → Conditional Access` tab; no unexpected `Failure` results | Author admin proposes; second admin reviews What-If + sign-in log evidence |
| **Pilot (Enabled, scoped to pilot group)** | 7–14 days | Pilot group (10–50 users including 1 admin, 1 power user, 1 guest if applicable) reports no friction; service desk no incidents | Author admin promotes; second admin reviews pilot evidence and signs off in change ticket |
| **Broad (Enabled, scoped to All Users with required exclusions)** | Steady state | Sign-in logs show enforcement; Sentinel detection per PRE-14 silent (no unauthorized mutations); quarterly review per Control 2.5 | Promotion approved by Conditional Access Administrator + Entra Security Admin in change ticket |

!!! danger "Two-admin pattern — SOX 404 separation of duties"
    Every CA policy mutation (create, modify, enable, disable, scope-change) requires:
    
    1. **Author** (holds Conditional Access Administrator) drafts the change in a documented change ticket.
    2. **Approver** (different UPN, also holds Conditional Access Administrator or Entra Security Admin) reviews What-If + change-ticket rationale + intended exclusions, then approves activation in the ticket.
    3. **Activator** (may be either; recorded in change ticket) makes the portal save.
    4. **Sentinel detection** per PRE-14 alerts on any `AuditLogs` `Update conditional access policy` event whose `InitiatedBy` UPN does not match the Author or Activator UPN in the corresponding change ticket within ±15 min — flags as unauthorized mutation.

### 7.2 The 10 human-user policies — summary

| ID | Name | Target | Grant / session | Reference template in `conditional-access-agent-templates.md` |
|---|---|---|---|---|
| **CA-001** | Block legacy authentication | All Users (excl. BreakGlass) | Block | T-CA-001 |
| **CA-002** | Require Zone 3 strength for privileged role activation | PIM-eligible admins | `FSI-Zone3-PhishingResistant` + Require compliant device + Sign-in frequency 4 h + No persistent browser + Token Protection | T-CA-002 |
| **CA-003** | Require Zone 3 strength for AI Administrator portal access | AI Administrator role + Power Platform Admin role | `FSI-Zone3-PhishingResistant` + Require compliant device + SIF 4 h | T-CA-003 |
| **CA-004** | Require Zone 2 strength for Copilot / Copilot Studio | All licensed Copilot users (excl. BreakGlass) | `FSI-Zone2-Strong` + SIF 8 h + No persistent browser | T-CA-004 |
| **CA-005** | Block sign-in from blocked countries | All Users (excl. BreakGlass) | Block | T-CA-005 |
| **CA-006** | Require Zone 3 strength + compliant device for Microsoft 365 admin centers | Anyone signing in to `Microsoft Admin Portals` cloud app | `FSI-Zone3-PhishingResistant` + Require compliant device + SIF 4 h | T-CA-006 |
| **CA-007** | Require Zone 3 + compliant device for Azure management | Azure management cloud app | `FSI-Zone3-PhishingResistant` + Require compliant device + SIF 4 h | T-CA-007 |
| **CA-008** | High user risk → require password change + Zone 2 strength | All Users (excl. BreakGlass) | Require password change + `FSI-Zone2-Strong` (when User risk = High) | T-CA-008 |
| **CA-009** | Break-glass account governance | BreakGlass-Users (only) | `FSI-BreakGlass-Hardware-Only` + No SIF + Sentinel alert per PRE-05 | T-CA-009 |
| **CA-010** | Guest user baseline | Guests/external users | `FSI-Zone2-Strong` + Block downloads on unmanaged device + SIF 4 h | T-CA-010 |

The full JSON for each policy is in [`conditional-access-agent-templates.md`](conditional-access-agent-templates.md). The portal-side authoring steps for the most consequential three follow.

### 7.3 CA-001 — Block legacy authentication (worked example)

1. `Conditional Access → Policies → + New policy`.
2. **Name:** `CA-001 Block legacy authentication`.
3. **Users:**
    - Include: All users.
    - Exclude: `BreakGlass-Users` group; emergency-access service accounts if any (with documented compensating controls).
4. **Target resources:** All cloud apps.
5. **Conditions → Client apps:** select **Exchange ActiveSync clients** + **Other clients** (these are the legacy-auth client app categories).
6. **Grant:** **Block access**.
7. **Enable policy:** **Report-only**.
8. **Create**.
9. Two-admin approval per PRE-13 → 7-day Report-only observation → review `Sign-in logs → Conditional Access` tab → if no false-positive blocks expected, second admin promotes to Pilot (target a 25-user pilot group) → 7 days → Broad (`Enable policy → On`).
10. Evidence: `EP-15-CA001-ReportOnly-{YYYYMMDD}.png`, `EP-15-CA001-Pilot-{YYYYMMDD}.png`, `EP-15-CA001-Enabled-{YYYYMMDD}.png` + Graph export of policy state at each transition.

### 7.4 CA-002 — Require Zone 3 strength for privileged role activation (worked example)

This policy binds Authentication Strength `FSI-Zone3-PhishingResistant` to **Authentication Context** `c1: Privileged role activation`, which PIM consumes at activation time (§9).

1. **Configure Authentication Context first:** `Conditional Access → Authentication context → + New authentication context`. ID `c1`, Name `Privileged role activation`, Publish to apps **ON**.
2. **+ New policy** named `CA-002 Require Zone 3 strength for privileged role activation`.
3. **Users:** Include `PIM-Eligible-Admins` group; Exclude `BreakGlass-Users`.
4. **Target resources → Authentication context:** select `c1: Privileged role activation`.
5. **Conditions → Device platforms:** any.
6. **Grant:**
    - Require authentication strength: `FSI-Zone3-PhishingResistant`.
    - Require device to be marked as compliant: ON.
7. **Session:**
    - Sign-in frequency: 4 hours, periodic reauthentication.
    - Persistent browser session: Never persistent.
    - Customize continuous access evaluation: Default (ON for new tenants per §10).
    - Require token protection for sign-in sessions: ON (Public Preview — verify availability).
8. **Enable policy:** Report-only → Pilot → Broad per §7.1.
9. In **PIM → Roles → {role} → Settings → Activation → On activation, require Conditional Access authentication context** → select `c1`. PIM will now demand Zone 3 strength + compliant device on every activation. (This step crosses §9 — record both portal screenshots together for traceability.)
10. Evidence: `EP-16-CA002-AuthContext-{YYYYMMDD}.png`, `EP-16-CA002-Policy-{YYYYMMDD}.png`, `EP-16-CA002-PIMBinding-{YYYYMMDD}.png`.

### 7.5 CA-009 — Break-glass account governance (worked example)

1. **+ New policy** named `CA-009 Break-glass account governance`.
2. **Users:** Include `BreakGlass-Users` only.
3. **Target resources:** All cloud apps.
4. **Grant:** Require authentication strength `FSI-BreakGlass-Hardware-Only`.
5. **Session:** Sign-in frequency: **Do not configure** (let break-glass keep session for the duration of the emergency); Persistent browser: Never persistent.
6. **Enable policy:** Enabled (skip Report-only — break-glass accounts must be policy-protected from inception).
7. Confirm **all other CA policies (CA-001 .. CA-010 except CA-009)** include `BreakGlass-Users` in their **Exclude** list. This is the single most often-broken CA invariant — re-verify on every CA mutation.
8. Confirm Sentinel rule per PRE-05 fires on any sign-in by either break-glass UPN.
9. Evidence: `EP-17-CA009-Policy-{YYYYMMDD}.png`, `EP-17-CA009-Exclusions-Audit-{YYYYMMDD}.csv` (cross-policy exclusion audit).

### 7.6 The remaining seven policies

For CA-003, CA-004, CA-005, CA-006, CA-007, CA-008, CA-010, follow the same authoring pattern as CA-001 / CA-002 but with the targeting / grant / session controls in the §7.2 summary table. The full JSON is in [`conditional-access-agent-templates.md`](conditional-access-agent-templates.md). Apply the same two-admin pattern, three-stage rollout, and per-policy evidence capture.

### 7.7 What-If walkthrough — required for every policy

For each policy, before promoting from Report-only to Pilot:

1. `Conditional Access → What If`.
2. **User:** representative target user for the policy.
3. **Cloud app / actions:** the targeted resource.
4. **IP address:** simulate trusted IP, allowed-country IP, blocked-country IP.
5. **Device platform / Client app / Sign-in risk / User risk:** vary across realistic scenarios.
6. **Run** → review **Policies that will apply** vs **Policies that will not apply** with the explanatory text.
7. Repeat with break-glass UPN — must show `CA-009` apply and **all other policies excluded**.
8. Repeat with guest UPN if applicable.
9. Capture screenshots → `EP-18-WhatIf-{policyID}-{scenario}-{YYYYMMDD}.png`.

---

## §8 Conditional Access for Workload Identities (CA WID)

**Portal path:** `entra.microsoft.com → Protection → Conditional Access → Policies → + New policy → Users and workload identities → Workload identities`<br>
**Owner role:** Conditional Access Administrator + AI Administrator<br>
**SKU:** **Microsoft Entra Workload Identities Premium** required per SP / managed identity / agent identity in scope. Without the SKU the policy fails open.<br>
**Status:** **GA** (not preview)<br>
**Reference:** [Conditional Access for workload identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity)

!!! warning "CA WID is GA; Entra Agent ID is Public Preview — they are different layers"
    Conditional Access for Workload Identities (CA WID) is **GA** and applies to any Service Principal or managed identity that has the Workload Identities Premium license assigned. **Entra Agent ID** (§9 below) is the Public Preview registry for AI agent identities; it rides on top of CA WID by adding `AgentZone` / `DataClassification` / `RegulatoryScope` / `SponsorObjectId` custom security attributes that CA-WI policies can scope on. If Agent ID is unavailable in your sovereign cloud (§2), use named-SP allow-lists in CA-WI policies instead.

### 8.1 Microsoft Managed Policies — view, attest, and document exceptions

Microsoft now ships baseline workload-identity protections via the **Microsoft Managed Policies** feature. These appear in the standard CA Policies blade and are **not** at a separate top-level menu (anti-pattern AP-13).

1. `Conditional Access → Policies`.
2. **Filter:** `Source = Microsoft`.
3. Review each Microsoft Managed Policy currently visible (the set evolves; representative examples include `Block high-risk service principals`, `Block high-risk agents`).
4. For each, decide one of: **Enabled** (recommended baseline), **Report-only** (during evaluation), or **Off** with documented exception in the firm's risk register (Control 1.2).
5. The tenant **cannot author or edit** Microsoft Managed Policies — only the on/off toggle and exception documentation are tenant-side.
6. Evidence: `EP-19-MicrosoftManagedPolicies-State-{YYYYMMDD}.json` (Graph export of all `source = Microsoft` policies and their state).

### 8.2 CA-WI-001 — Block workload identity sign-in from blocked countries

1. **+ New policy** named `CA-WI-001 Block workload identity sign-in from blocked countries`.
2. **Users and workload identities:** select **Workload identities**.
3. **Include:** select all targeted SPs (or a workload-identity group if firm uses the Preview group support).
4. **Exclude:** any SP with documented multi-region operational requirement (with Control 1.2 risk-register entry).
5. **Target resources:** All cloud apps.
6. **Conditions → Locations:** Include `FSI-BlockedCountries-FATF-OFAC`.
7. **Grant:** Block access.
8. **Enable policy:** Report-only → Pilot (single non-production SP) → Broad per §7.1.
9. Evidence: `EP-20-CAWI001-State-{YYYYMMDD}.json`.

### 8.3 CA-WI-002 — Require Zone 3 service principals to sign in from trusted IPs only

1. **+ New policy** named `CA-WI-002 Zone 3 SP trusted-IP enforcement`.
2. **Users and workload identities → Workload identities:** Include all SPs and Agent identities marked `AgentZone == 3` (via custom security attribute filter — see §9.4) **OR** (when Agent ID unavailable) the named Zone 3 SP allow-list.
3. **Conditions → Locations:** Exclude `FSI-TrustedOffices-{Region}` ranges; Include any location.
4. **Grant:** Block access (i.e., block sign-in from anywhere except trusted office IPs).
5. **Enable policy:** Report-only minimum 14 days (workload identity sign-in patterns are bursty; observe a full operational cycle) → Pilot → Broad.
6. Evidence: `EP-21-CAWI002-State-{YYYYMMDD}.json`.

### 8.4 CA-WI-003 — Block service principals on Identity Protection High risk

1. **+ New policy** named `CA-WI-003 Block high-risk workload identities`.
2. **Users and workload identities → Workload identities:** Include all SPs + agents.
3. **Conditions → Service principal risk:** High.
4. **Grant:** Block access.
5. **Enable policy:** Report-only → Pilot → Broad.
6. This complements (does not replace) the Microsoft Managed Policy `Block high-risk service principals`. If the Microsoft Managed Policy is Enabled in §8.1, CA-WI-003 may be set to Off but documented as customer-authored fallback should the Microsoft Managed Policy be paused or removed.
7. Evidence: `EP-22-CAWI003-State-{YYYYMMDD}.json`.

---

## §9 Entra Agent ID — registry, custom security attributes, sponsors, collections, risk policies

**Portal path:** `entra.microsoft.com → Identity → Identity governance → Agent ID` (Public Preview, Frontier-gated)<br>
**Owner role:** AI Administrator + AI Governance Lead<br>
**Status:** **Public Preview** under Microsoft Frontier program — schema and UI may change<br>
**Reference:** [Microsoft Entra Agent ID for AI agents](https://learn.microsoft.com/en-us/entra/architecture/secure-resource-management) (re-verify the canonical Agent ID landing page at deploy time)

!!! danger "Agent Sponsor is NOT a built-in Entra directory role"
    The "Agent Sponsor" concept is implemented via **Microsoft Entra ID Governance access packages** (Identity Governance → Entitlement management → Access packages), not as a built-in directory role. Onboard sponsors per Control 2.26 by:
    
    1. Defining an `AI-Agent-Sponsor-Zone3` access package whose policies require: manager approval + quarterly recertification + Conditional Access requirement (`FSI-Zone3-PhishingResistant`).
    2. Granting that access package to nominated sponsor candidates.
    3. Recording the sponsor's `objectId` in the agent's `SponsorObjectId` custom security attribute (§9.4).
    
    Do **not** delegate sponsor authority by adding the user to a built-in role — there is no "Agent Sponsor" built-in role.

### 9.1 Agent registry walkthrough

1. Sign in as **AI Administrator** to `entra.microsoft.com`.
2. Browse `Identity → Identity governance → Agent ID` (Public Preview surface — exact navigation may shift).
3. **All agents** view shows registered agents from Copilot Studio, Microsoft 365 Copilot custom agents, and Azure AI Foundry agents.
4. For each agent, the registry shows: `objectId`, `displayName`, `appId` (origin), `createdDateTime`, owner UPN, sponsor UPN (if `SponsorObjectId` populated), `AgentZone`, `DataClassification`, `RegulatoryScope`.
5. **Reconcile to Control 3.1 inventory:** export the registry view → match against the agent inventory in Control 3.1 → flag discrepancies for AI Governance Lead.
6. Evidence: `EP-23-AgentRegistry-Export-{YYYYMMDD}.csv`.

### 9.2 Custom Security Attributes — schema definition (PRE-16 prerequisite)

1. `Protection → Custom security attributes` (or `Identity → Custom security attributes` depending on tenant).
2. **+ Add attribute set:** `AgentGovernance`.
3. Within `AgentGovernance`, add four attributes:
    - `AgentZone` — String, predefined values: `Zone1`, `Zone2`, `Zone3`. Allow multiple values: No. Allow only predefined values: Yes.
    - `DataClassification` — String, predefined values: `Public`, `Internal`, `Confidential`, `Restricted`, `MNPI`. Allow only predefined: Yes.
    - `RegulatoryScope` — String, predefined values: `FINRA`, `SEC`, `NYDFS`, `OCC`, `FFIEC`, `CFTC`, `GLBA-Customer`, `None`. Allow multiple: Yes.
    - `SponsorObjectId` — String, free-form (Entra `objectId` of the access-package-granted sponsor).
4. **Role separation:**
    - **Attribute Definition Administrator** — defines schema; should be a small group (Compliance Officer + Entra Identity Governance Admin).
    - **Attribute Assignment Administrator** — assigns values to objects; AI Administrator + AI Governance Lead.
    - **Attribute Definition Reader / Attribute Assignment Reader** — read-only roles for SOC, audit, and Sentinel ingestion service principals.
5. Evidence: `EP-24-CSA-Schema-{YYYYMMDD}.json`, `EP-24-CSA-RoleAssignments-{YYYYMMDD}.csv`.

### 9.3 Sponsor assignment via access package

Per the warning above, sponsor authority is granted via Identity Governance access package. To onboard a sponsor:

1. `Identity governance → Entitlement management → Access packages → + New access package` named `AI-Agent-Sponsor-Zone3`.
2. **Resource roles:** none (the access package is a governance wrapper, not a resource grant).
3. **Requests:** Restricted requesters → AI Administrator group only. Approval: AI Governance Lead + Compliance Officer (two-step).
4. **Lifecycle:** Expiration after 365 days; recertification quarterly.
5. **Custom extensions:** none required for the basic flow.
6. Grant the access package to sponsor candidates.
7. For each agent, record the sponsor's `objectId` into the agent's `SponsorObjectId` custom security attribute (§9.4 below).
8. Evidence: `EP-25-AccessPackage-Sponsor-{YYYYMMDD}.json`.

### 9.4 Assigning custom security attributes to an agent

1. `Identity → Identity governance → Agent ID → All agents → {agent display name}`.
2. **Custom security attributes → + Add assignment**.
3. Set `AgentZone`, `DataClassification`, `RegulatoryScope`, `SponsorObjectId` per the agent's documented governance record.
4. Save.
5. Evidence: `EP-26-Agent-{agentObjectId}-CSA-{YYYYMMDD}.json` (Graph export of the agent's `customSecurityAttributes` payload).

### 9.5 Agent collections

Agent collections group agents for bulk policy targeting. The two operationally important collections are:

| Collection | Purpose | Membership rule |
|---|---|---|
| `Quarantine-Agents` | Agents auto-moved here on Identity Protection High risk; CA-WI policy `Block all access` targets this collection | Manual move on Identity Protection High risk OR scripted move via Logic App |
| `Zone3-Agents` | Convenience grouping mirroring `AgentZone == 3` for CA-WI scoping where the attribute filter UI is not yet exposed | Manual / scripted by AI Administrator |

1. `Identity → Identity governance → Agent ID → Collections → + New collection`.
2. Create `Quarantine-Agents` and `Zone3-Agents`.
3. Bind to CA-WI policies as appropriate.
4. Evidence: `EP-27-AgentCollections-{YYYYMMDD}.json`.

### 9.6 Agent risk policies (Identity Protection)

1. `Protection → Identity Protection → Workload identity risk policy` (the same blade now shows agent identity risk where the registry is enabled).
2. Confirm **Workload identity risk policy** is configured: Service principal risk **High** → Block. Apply to all SPs + agents (excl. break-glass-equivalent service identities if any with documented compensation).
3. Identity Protection emits risk on workload identity sign-ins; the response is twofold: (a) CA-WI-003 + Microsoft Managed Policy block at sign-in; (b) Logic App (out of scope for this walkthrough — see Control 1.12) auto-moves the agent to `Quarantine-Agents` collection.
4. Evidence: `EP-28-WorkloadIdentityRiskPolicy-{YYYYMMDD}.png`.

### 9.7 Cross-reference to Control 2.26

Lifecycle of agent identities — registration, sponsor onboarding workflow, attribute schema versioning, deprovisioning on agent retirement — is owned by **Control 2.26 (Entra Agent ID Identity Governance)**. This walkthrough configures the §9 surfaces only as they are referenced by §8 CA-WI policies. Do not extend §9 to cover lifecycle steps; route lifecycle requests to the [2.26 portal walkthrough](../2.26/portal-walkthrough.md).

---

## §10 Privileged Identity Management — eligible-only with two-admin CA mutation pattern

**Portal path:** `entra.microsoft.com → Identity governance → Privileged Identity Management → Microsoft Entra roles`<br>
**Owner role:** Entra Identity Governance Admin (PIM owner) + Entra Privileged Role Admin (assigner)<br>
**Reference:** [Configure Microsoft Entra role settings in Privileged Identity Management](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-how-to-change-default-settings)

### 10.1 Roles in scope for this walkthrough

The seven roles below directly govern the AI estate. Apply the §10.2 settings to each.

| # | Role (Microsoft display name) | Canonical short-name | Why eligible-only |
|---|---|---|---|
| 1 | Conditional Access Administrator | Entra Conditional Access Admin | Authors the policies in §7 / §8 — must be eligible + two-admin gated |
| 2 | Authentication Policy Administrator | Authentication Administrator (canonical) | Authors §4 Authentication Methods Policy |
| 3 | Privileged Role Administrator | Entra Privileged Role Admin | Assigns PIM roles — itself privileged |
| 4 | Identity Governance Administrator | Entra Identity Governance Admin | Configures PIM, access packages, access reviews |
| 5 | Security Administrator | Entra Security Admin | Identity Protection, Microsoft Managed Policies, sign-in log review |
| 6 | Global Administrator | Entra Global Admin | Tenant-wide; minimum two eligible per FFIEC + NIST 800-63B BCDR; no permanent assignments |
| 7 | Application Administrator + Cloud Application Administrator | Entra Application Admin | Service principal management — required for §8 CA-WI scoping; eligible-only |

The two AI-specific roles — **AI Administrator** and **AI Governance Lead** — are configured similarly per Control 2.5; they are not in this list because their PIM settings are owned by 2.5.

### 10.2 PIM role settings — uniform baseline

For each role above:

1. `Privileged Identity Management → Microsoft Entra roles → Roles → {role} → Settings`.
2. **Activation:**
    - Maximum activation duration: **4 hours** (Zone 3 admin roles); 8 hours (operational roles).
    - On activation, require: **Microsoft Entra Multi-Factor Authentication** + **Conditional Access authentication context** = `c1: Privileged role activation` (binds CA-002 / Zone 3 strength + compliant device).
    - Require justification on activation: ON.
    - Require ticket information on activation: ON (integrate with firm's change management — record ticket ID).
    - Require approval to activate: ON for Global Admin, Conditional Access Admin, Privileged Role Admin (two-step approval — see §10.3); optional for others per risk appetite.
3. **Assignment:**
    - Allow permanent eligible assignment: **OFF** (eligibility expires; recertify per quarterly access review).
    - Expire eligible assignments after: **365 days**.
    - Allow permanent active assignment: **OFF** (no permanent active — break-glass uses non-PIM permanent assignment to a different account).
    - Expire active assignments after: **6 months** (rare; emergency only).
    - Require Microsoft Entra Multi-Factor Authentication on active assignment: ON.
    - Require justification on active assignment: ON.
4. **Notifications:** alert role member, role assignees, and **CISO + on-call SOC** on assignment, eligible-assignment change, and activation.
5. Save → `EP-29-PIM-{role}-Settings-{YYYYMMDD}.json` per role.

### 10.3 Two-admin pattern for CA mutations

Conditional Access Administrator role has elevated mutation power; combine PIM + the two-admin pattern from §7.1:

1. PIM activation requires approval by a **second** Conditional Access Administrator (not the requester).
2. The requesting admin documents the change ticket, links the What-If evidence, and identifies the second admin for approval.
3. After activation, the change is made; activation logs (`AuditLogs` `Add eligible member to role` / `Add member to role` / `Activate role assignment`) are joined in Sentinel against the change ticket per PRE-14.
4. Mutations whose `InitiatedBy` UPN does not match the change ticket fire as unauthorized mutation.

### 10.4 Quarterly access reviews

1. `Identity governance → Access reviews → + New access review`.
2. **Review type:** Microsoft Entra role; select all 7 roles in §10.1.
3. **Reviewers:** Manager of each assignee + CISO secondary review.
4. **Frequency:** Quarterly; auto-apply results.
5. **Inactive eligibility removal:** auto-remove eligible assignments unused in last 90 days.
6. Evidence: `EP-30-AccessReview-{quarter}-{YYYYMMDD}.csv`.

### 10.5 Break-glass — the non-PIM exception

Per PRE-04, break-glass accounts are **permanently active Global Administrators** (NOT in PIM). Document explicitly in the firm's WSP:

- BreakGlass-01 and BreakGlass-02: permanently active Global Administrator.
- Sentinel rule per PRE-05 alerts on any sign-in.
- Excluded from CA-001..CA-008, CA-010, CA-WI-001..CA-WI-003. Subject only to CA-009.
- Quarterly alternating activation test per PRE-06.

---

## §11 CAE / Token Protection / Sign-in Frequency / Persistent Browser

**Owner role:** Conditional Access Administrator<br>
**References:**
- [Continuous access evaluation](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation)
- [Token protection (sign-in session) in Conditional Access (Public Preview)](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-token-protection)
- [Configure adaptive session lifetime policies](https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-session-lifetime)

### 11.1 Continuous Access Evaluation — verification

CAE is **GA** and **default On for new tenants** as of April 2026. For existing tenants:

1. `Conditional Access → Policies → {any policy} → Session → Customize continuous access evaluation`.
2. Default: not configured (CAE enabled tenant-wide). For Zone 3 admin policies, explicitly set **CAE: Default (enabled)** to record the choice in the policy state for audit.
3. Validate revocation triggers fire by:
    - In a test tenant (do **not** run in production), disable a test user → confirm the user's existing token in Outlook Web is revoked within 5 minutes (typical) — up to 1 hour in degraded conditions.
    - Capture the revocation event in `Sign-in logs → Continuous access evaluation` filter.
4. Evidence: `EP-31-CAE-RevocationTest-{YYYYMMDD}.png` (test tenant) + `EP-31-CAE-Triggers-Inventory.md` (the firm's documented list of in-scope revocation triggers).

The documented in-scope CAE revocation triggers (Microsoft current list):
- User account deletion / disable.
- User password change / reset.
- MFA registration changes.
- Token revoked by admin (`Revoke-MgUserSignInSession`).
- High user risk detection in Identity Protection.
- Outside trusted IP / Named Location change (with policy bind).

!!! warning "CAE is near-real-time, not real-time"
    Document expected propagation as **typically <5 minutes; up to 1 hour under degraded conditions**. Build a **1-hour revocation buffer** into NYDFS §500.17(a) 72-hour cybersecurity-event-report procedures.

### 11.2 Token Protection (Public Preview, early 2026)

Token Protection cryptographically binds the issued token to the device's hardware-backed key. A stolen token replayed from a different device fails Token Protection and is rejected.

1. Within a Zone 3 CA policy (CA-002, CA-006, CA-007), `Session → Require token protection for sign-in sessions` → ON.
2. **Pre-requisite (very important):** the targeted user must be on an **Entra-joined or compliant Entra-joined Windows device** with a supported app (Edge, Outlook desktop, Teams desktop). On unmanaged devices, Token Protection is a **silent no-op** — pair with `Require compliant device` to enforce.
3. Pilot with a small admin group on managed Windows for 14 days; review `Sign-in logs → Token Protection` filter for unexpected failures.
4. Evidence: `EP-32-TokenProtection-Policy-{YYYYMMDD}.png` + `EP-32-TokenProtection-PilotResults-{YYYYMMDD}.csv`.

### 11.3 Sign-in frequency per zone

| Zone | SIF | Persistent browser |
|---|---|---|
| **Zone 3** (admin / privileged role activation / admin portals) | **4 hours**, periodic reauthentication | Never persistent |
| **Zone 2** (Copilot, Copilot Studio, business team agents) | **8 hours** | Never persistent |
| **Zone 1** (general user productivity, low-risk Copilot) | **24 hours** (or do not configure if firm default is acceptable) | Allowed (firm default) |

Configure within each CA policy `Session → Sign-in frequency` and `Session → Persistent browser session`. Capture evidence within each policy's screenshot bundle (already captured under EP-15 .. EP-22).

### 11.4 Cross-control reminder — PPAC inactivity vs Entra SIF

The Power Platform Admin Center has a separate **inactivity timeout** governed by Control 2.22. Entra SIF (this section) governs how often the user must re-authenticate; PPAC inactivity timeout governs how long an idle session persists before the application terminates it. The two are independent and both must be configured. Coordinate user comms to avoid confusion. Reference: [Control 2.22 portal walkthrough](../2.22/portal-walkthrough.md).

---

## §12 Identity Protection — risky users, sign-ins, workload identities

**Portal path:** `entra.microsoft.com → Protection → Identity Protection`<br>
**Owner role:** Entra Security Admin<br>
**Reference:** [What is Microsoft Entra ID Protection?](https://learn.microsoft.com/en-us/entra/id-protection/overview-identity-protection)

### 12.1 User risk policy

1. `Protection → Identity Protection → User risk policy`.
2. **Assignments:** All users **except** `BreakGlass-Users`.
3. **Conditions → User risk:** High.
4. **Controls → Access:** Allow access; **Require password change**.
5. **Enforce policy:** Report-only → Pilot → On.
6. Evidence: `EP-33-UserRiskPolicy-{YYYYMMDD}.png`.

Note: this overlaps CA-008 conceptually. The recommended pattern is to use the standalone Identity Protection user risk policy for the password-change action and CA-008 (built as a CA policy) for the strength-upgrade action. They run side-by-side.

### 12.2 Sign-in risk policy

1. `Sign-in risk policy`.
2. **Assignments:** All users **except** `BreakGlass-Users`.
3. **Conditions → Sign-in risk:** Medium and above.
4. **Controls → Access:** Allow access; **Require multi-factor authentication**.
5. **Enforce policy:** Report-only → Pilot → On.
6. Evidence: `EP-34-SignInRiskPolicy-{YYYYMMDD}.png`.

### 12.3 Risky workload identities

1. `Risky workload identities` (requires Workload Identities Premium).
2. Review the queue weekly. Investigate each `High` flagged SP / agent — identify the trigger (anomalous IP, anomalous app permission grant, leaked credential).
3. For confirmed-malicious workload identities, **disable** the SP (`Enterprise applications → {SP} → Properties → Enabled for users to sign in: No`) and rotate any credentials.
4. CA-WI-003 + Microsoft Managed Policy `Block high-risk service principals` provide automated containment; manual review provides triage and root-cause.
5. Evidence: weekly export to `EP-35-RiskyWorkloadIdentities-{YYYYMMDD}.csv`.

### 12.4 Cross-reference to Control 1.12

Identity Protection emits the risk signal; **Control 1.12 (Insider Risk Detection and Response)** owns the response workflow, alert routing, case management, and escalation to legal/compliance. Do not extend §12 to the workflow layer; route to the [1.12 portal walkthrough](../1.12/portal-walkthrough.md).

---

## §13 Sign-in log review and FSI incident clocks

**Portal path:** `entra.microsoft.com → Identity → Monitoring & health → Sign-in logs`<br>
**Owner role:** Entra Security Admin (daily review) + CISO + Compliance Officer (incident pathway)<br>
**Reference:** [Sign-in logs in Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-sign-ins)

### 13.1 Daily SP + Agent sign-in review

1. `Sign-in logs → User sign-ins (interactive) | (non-interactive) | Service principal sign-ins | Managed identities sign-ins`.
2. Filter to **Service principal sign-ins** + add column **Workload identity risk** + **Conditional Access** (status of CA evaluation per sign-in).
3. Review for:
    - Failures with `Conditional Access status = Failure` against expected CA-WI policies (silent CA mutation indicator).
    - High workload-identity risk events.
    - Sign-ins from unexpected geographies.
4. Latency reminder: hot ingest 5–15 min, full ingest up to 6 hours. For backfill investigations, query Log Analytics workspace via Sentinel rather than the portal.
5. Evidence: weekly export `EP-36-SP-Agent-Signins-{YYYYMMDD}.csv`.

### 13.2 FSI regulatory incident clocks

When a 1.11-detected event indicates a reportable cybersecurity event, the following clocks start. Coordinate with Control 3.4 / the [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) for end-to-end workflow.

| Trigger detected via | Regulatory clock | Authority | Notes |
|---|---|---|---|
| Confirmed unauthorized access to systems holding customer information | **NYDFS §500.17(a) — 72 hours** to report cybersecurity event to DFS Superintendent | NYDFS 23 NYCRR Part 500 | Build 1-h CAE revocation buffer into the 72-h clock |
| Material cybersecurity incident at a US-listed firm | **SEC Form 8-K Item 1.05 — 4 business days** post materiality determination | SEC | Materiality determination clock starts at IR triage; document determination evidence |
| Customer-information unauthorized access (broker-dealer / investment adviser) | **Reg S-P — 30 days** customer notification (May 2024 amendment) | SEC Regulation S-P | Begin the 30-day clock at confirmed unauthorized access |
| Required FINRA disclosure of compromise affecting member-firm operations | **FINRA Rule 4530 — 30 days** | FINRA | FINRA Notice 25-07 reaffirmed phishing-resistant MFA expectation |
| Significant operational disruption for a federally insured bank | **Federal banking computer-security incident notification — 36 hours** | OCC, FRB, FDIC (12 CFR §53 / §225 / §304) | Banks only |
| FFIEC SR 21-14 risk-based MFA — exam evidence on demand | n/a (exam cycle) | FFIEC | This walkthrough's evidence pack supports the exam package |
| GLBA Customer-information access | **FTC Safeguards Rule 16 CFR §314.4(c)(5)** (in force June 2023 — strong authentication for systems holding customer information); not a notification clock but an exam expectation | FTC | Reference 16 CFR §314, not GLBA §501(b) directly |
| CFTC-registered FCM / DCM | **CFTC Rule 1.31** record-retention; cybersecurity-event reporting via System Safeguards Testing | CFTC | Coordinate with the firm's CFTC compliance lead |

### 13.3 Verification handoff

This portal walkthrough handles **configuration**. Test execution and evidence collection are in the companion [`verification-testing.md`](verification-testing.md). Common failures and remediation are in [`troubleshooting.md`](troubleshooting.md). PowerShell automation of every step above is in [`powershell-setup.md`](powershell-setup.md). The CA policy JSON templates referenced by §7 / §8 are in [`conditional-access-agent-templates.md`](conditional-access-agent-templates.md).

---

## §14 Evidence pack, anti-pattern catalog, and cross-references

### 14.1 19-artifact evidence pack (SHA-256 hashed; chain-of-custody)

For every promotion (Report-only → Pilot → Broad), capture and hash the following. Store in a WORM-eligible repository (SharePoint with retention label per Control 1.7, or Azure immutable blob storage). Each artifact should be hashed (`Get-FileHash -Algorithm SHA256`) and the hash recorded in the firm's evidence index.

| EP-# | Artifact | Source | Format | Owner |
|---|---|---|---|---|
| EP-01 | License inventory (P2 + Workload Identities Premium) | `Get-MgSubscribedSku` | CSV | Entra Global Admin |
| EP-02 | SP + Agent inventory reconciled to Control 3.1 | Graph + Agent ID registry | CSV | AI Administrator |
| EP-03 | Break-glass governance record | Portal + safe-records | PDF + signed attestation | CISO |
| EP-04 | FIDO2 AAGUID allow-list configuration | Portal screenshot + Graph JSON | PNG + JSON | Authentication Policy Administrator |
| EP-05 | WHfB cloud Kerberos trust configuration | Portal screenshot | PNG | Authentication Policy Administrator |
| EP-06 | CBA configuration + bound CA cert chain | Portal screenshot + Graph JSON | PNG + JSON | Authentication Policy Administrator |
| EP-07 | Microsoft Authenticator passkey-mode (device-bound) | Portal screenshot | PNG | Authentication Policy Administrator |
| EP-08 | Registration campaign configuration | Portal screenshot | PNG | Authentication Policy Administrator |
| EP-09 | Authentication strength `FSI-Zone3-PhishingResistant` | Portal screenshot + Graph JSON | PNG + JSON | Conditional Access Administrator |
| EP-10 | Authentication strength `FSI-Zone2-Strong` | Portal screenshot + Graph JSON | PNG + JSON | Conditional Access Administrator |
| EP-11 | Authentication strength `FSI-BreakGlass-Hardware-Only` | Portal screenshot + Graph JSON | PNG + JSON | Conditional Access Administrator |
| EP-12 | Named Location: trusted offices | Graph JSON | JSON | Conditional Access Administrator |
| EP-13 | Named Location: allowed countries | Graph JSON | JSON | Conditional Access Administrator |
| EP-14 | Named Location: blocked countries (FATF + OFAC) | Graph JSON | JSON | Conditional Access Administrator |
| EP-15 | CA-001 state at each rollout stage | Portal screenshot + Graph JSON | PNG + JSON | Conditional Access Administrator |
| EP-16 | CA-002 + Authentication Context + PIM binding | Portal screenshots + Graph JSON | PNG + JSON | Conditional Access Administrator |
| EP-17 | CA-009 break-glass policy + cross-policy exclusion audit | Portal screenshot + cross-policy CSV | PNG + CSV | Conditional Access Administrator |
| EP-18 | What-If results for each policy / scenario | Portal screenshots | PNG | Conditional Access Administrator |
| EP-19 | Microsoft Managed Policies state | Graph JSON | JSON | Entra Security Admin |

(EP-20 .. EP-36 follow the inline numbering in §8 .. §13 above; the full list is the canonical 19+ artifact baseline plus per-policy / per-quarter additions.)

### 14.2 Anti-pattern catalog — 15 entries

| # | Anti-pattern | Why it fails | Detection | Correction |
|---|---|---|---|---|
| **AP-01** | Configuring FIDO2 attestation OFF "to onboard faster" | Allows non-FIPS keys onto Zone 3; bypasses AAL3 hardware-binding | Quarterly review of FIDO2 method config | Set attestation ON; revoke any non-attested registrations |
| **AP-02** | Allowing **synced** passkeys (iCloud / Google Password Manager) on Zone 3 admins | Synced passkeys are not AAL3; private key leaves hardware | Sign-in log filter on `authenticationDetails` | Exclude sync-AAGUIDs from `FSI-Zone3-PhishingResistant` |
| **AP-03** | Using built-in `MFA` strength on Zone 3 (not `Phishing-resistant MFA`) | Allows SMS/voice/OTP — fails NYDFS §500.12 phishing-resistance posture for privileged | What-If shows non-phishing-resistant methods accepted | Migrate to `FSI-Zone3-PhishingResistant` |
| **AP-04** | Single break-glass account, or both keys in same safe | Single point of failure violates NYDFS §500.16, FFIEC BCDR | PRE-04 attestation review | Provision second account + second safe; quarterly test |
| **AP-05** | Forgetting to exclude break-glass from new CA policies | Lockout on policy mistake; full tenant inaccessible | EP-17 cross-policy exclusion audit | Add exclusion before promotion; What-If with break-glass UPN |
| **AP-06** | Using **per-user MFA** in legacy MFA portal alongside CA | Conflicting evaluation; CA may be ignored or override unpredictably | PRE-10 legacy MFA migration | Disable per-user MFA; migrate fully to CA |
| **AP-07** | Leaving Security Defaults ON while configuring CA | Security Defaults overrides CA; CA policies ignored | `entra.microsoft.com → Properties → Manage Security defaults` | Disable Security Defaults |
| **AP-08** | Trusted IPs configured in legacy MFA portal but not in Named Locations | Trusted-IP behavior undefined for CA evaluation | Audit Named Locations for trusted office ranges | Migrate to Named Locations + Mark as trusted location |
| **AP-09** | Token Protection ON without `Require compliant device` | Silent no-op on unmanaged devices | Sign-in log Token Protection filter shows mostly `Not Applied` | Pair Token Protection with compliant-device grant |
| **AP-10** | Sign-in frequency configured but persistent browser left allowed | Long-lived session persists across browser restart, defeats SIF | Per-policy session control review | Set persistent browser to Never persistent for Zone 2/3 |
| **AP-11** | CA-WI policy without Workload Identities Premium SKU | Policy fails open; no enforcement | License audit per PRE-02 | Assign SKU before promotion; verify in policy state |
| **AP-12** | Treating Entra Agent ID Public Preview as GA in WSP language | Schema may change; WSP becomes inaccurate | WSP language review | Mark Agent ID surfaces as Public Preview; document in risk register |
| **AP-13** | Looking for a top-level "Microsoft Managed Policies" menu | Does not exist; managed policies appear via `Source = Microsoft` filter in standard CA Policies blade | Path verification | Use `Conditional Access → Policies` with filter |
| **AP-14** | Adding a user to a built-in role for "Agent Sponsor" duty | No such built-in role exists; sponsorship is via access package | Role audit shows no Agent Sponsor role | Implement via Identity Governance access package per §9.3 |
| **AP-15** | Same-admin authoring + activating CA policy mutation (no two-admin approval) | Violates SOX 404 separation of duties; PRE-13 + PRE-14 detection silent if no approval ticket | Sentinel rule per PRE-14 | Enforce two-admin pattern; reject mutations without ticket trail |

### 14.3 Cross-references

**Sibling controls (Pillar 1):**
- [1.5 — Data Loss Prevention and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)
- [1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [1.12 — Insider Risk Detection and Response](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md)
- [1.14 — Data Minimization and Agent Scope Control](../../../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md)
- [1.19 — eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md)
- [1.21 — Adversarial Input Logging](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md)

**Sibling controls (Pillar 2 — Management):**
- [2.5 — Testing, Validation, and Quality Assurance](../../../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) (PIM lifecycle handoff)
- [2.8 — Access Control and Segregation of Duties](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md)
- [2.22 — Inactivity Timeout Enforcement](../../../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md)
- [2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)

**Sibling controls (Pillar 3 — Governance):**
- [3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
- [3.8 — Copilot Hub and Governance Dashboard](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md)

**Companion playbook artifacts in this directory:**
- [`powershell-setup.md`](powershell-setup.md) — PowerShell automation for every step
- [`verification-testing.md`](verification-testing.md) — test cases + evidence collection
- [`troubleshooting.md`](troubleshooting.md) — common failures + remediation
- [`conditional-access-agent-templates.md`](conditional-access-agent-templates.md) — CA + CA-WI JSON policy templates referenced by §7 / §8

**Incident pathway:**
- [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md)

**External references:**
- [CISA — Implementing Phishing-Resistant MFA fact sheet](https://www.cisa.gov/sites/default/files/publications/fact-sheet-implementing-phishing-resistant-mfa-508c.pdf)
- [NIST SP 800-63B — Digital Identity Guidelines: Authentication and Lifecycle Management](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [Microsoft Entra Conditional Access overview](https://learn.microsoft.com/en-us/entra/identity/conditional-access/overview)
- [Plan a Conditional Access deployment](https://learn.microsoft.com/en-us/entra/identity/conditional-access/plan-conditional-access)
- [Conditional Access for workload identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity)
- [Microsoft Entra authentication methods](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-methods)
- [Conditional Access authentication strength](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths)
- [Continuous access evaluation](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation)
- [Token protection in Conditional Access (Public Preview)](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-token-protection)
- [Configure adaptive session lifetime policies](https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-session-lifetime)
- [Microsoft Entra ID Protection overview](https://learn.microsoft.com/en-us/entra/id-protection/overview-identity-protection)
- [PIM — Configure Microsoft Entra role settings](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-how-to-change-default-settings)
- [PIM — Approve or deny requests for Microsoft Entra roles](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-approval-workflow)
- [Identity Governance — entitlement management access packages](https://learn.microsoft.com/en-us/entra/id-governance/entitlement-management-overview)
- [Custom security attributes in Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/fundamentals/custom-security-attributes-overview)
- [Microsoft Entra Workload Identities licensing](https://learn.microsoft.com/en-us/entra/workload-id/workload-identities-overview)
- [Sign-in logs in Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-sign-ins)
- [Microsoft 365 Government service description](https://learn.microsoft.com/en-us/office365/servicedescriptions/office-365-platform-service-description/office-365-us-government/office-365-us-government)
- [NYDFS 23 NYCRR Part 500 — Cybersecurity Requirements for Financial Services Companies](https://www.dfs.ny.gov/industry_guidance/cybersecurity)
- [FINRA — Notice 25-07 Cybersecurity Authentication](https://www.finra.org/rules-guidance/notices)
- [FTC Safeguards Rule — 16 CFR Part 314](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314)
- [SEC — Form 8-K Item 1.05 cybersecurity disclosure](https://www.sec.gov/files/rules/final/2023/33-11216.pdf)
- [SEC — Regulation S-P amendments (May 2024)](https://www.sec.gov/files/rules/final/2024/34-100155.pdf)
- [FFIEC SR 21-14 — Authentication and Access to Financial Institution Services and Systems](https://www.federalreserve.gov/supervisionreg/srletters/sr2114.htm)
- [OCC Bulletin 2011-12 — Sound Practices for Model Risk Management](https://www.occ.gov/news-issuances/bulletins/2011/bulletin-2011-12.html)
- [Federal Reserve SR 11-7 — Guidance on Model Risk Management](https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm)
- [CFTC Rule 1.31 — Books and records](https://www.ecfr.gov/current/title-17/chapter-I/part-1/subpart-A/section-1.31)
- [Microsoft Entra Workload Identities Premium](https://learn.microsoft.com/en-us/entra/workload-id/workload-identities-faqs)
- [Microsoft Entra agent identity for AI agents (Public Preview)](https://learn.microsoft.com/en-us/entra/architecture/secure-resource-management)

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
