# Control 1.19 — Portal Walkthrough: eDiscovery for Agent Interactions

**Control:** [1.19 — eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md)<br>
**Pillar:** Security<br>
**Last UI Verified:** April 2026<br>
**Estimated time:** 8–14 hours initial setup across 6+ admin roles (multi-day calendar; per-matter time variable — see §10 SLAs)<br>
**Governance Levels:** Baseline / Recommended / Regulated<br>
**Audience:** Purview eDiscovery Manager, eDiscovery Administrator, Reviewer, Compliance Officer, Designated Supervisor / Registered Principal, General Counsel, Records Manager, AI Governance Lead, CISO

---

!!! danger "READ FIRST — what this walkthrough is and is NOT"
    This walkthrough configures the **case, custodian, location, search, hold, review-set, and export** surfaces of the **unified Microsoft Purview eDiscovery experience** at `purview.microsoft.com → Solutions → eDiscovery` for **Microsoft 365 Copilot and Copilot Studio agent interactions**.

    It is **NOT** a substitute for the following sibling controls. Each is a separate configuration surface with its own playbook:

    | If you need… | Use Control | Why this is not 1.19 |
    |---|---|---|
    | Configure Unified Audit Log retention and `CopilotInteraction` audit ingestion | **1.7** | 1.19 *consumes* `CopilotInteraction` for forensic correlation; 1.7 *configures* the audit pipeline |
    | DSPM-for-AI scoping intelligence (which agents touch what data) | **1.6** | 1.6 helps you scope a case before you create it; 1.19 runs the case |
    | Author retention policies, retention labels, and **Preservation Lock** for SEC 17a-4(f) format compliance | **1.9** | **An eDiscovery hold preserves availability — it does NOT make content WORM. Preservation Lock under 1.9 is the format-compliance control.** |
    | Author Communication Compliance policies (offensive language, regulatory, **Detect Microsoft Copilot Interactions** template) | **1.10** | Comm Compliance findings *feed* eDiscovery cases; 1.19 does not author Comm Compliance policies |
    | Author Sensitive Information Types used to cull review sets | **1.13** | SIT authoring is upstream; 1.19 *uses* the SITs in review-set culling and redaction |
    | Reduce the corpus an agent can ground on (data minimization, agent grounding scope, RCD/RSS/DAG posture) | **1.14**, **4.6** | 1.19 does not shrink the discoverable surface; 1.14 / 4.6 do |
    | Adversarial-input *detection* (Prompt Shields, Defender for Cloud TP for AI Workloads, Defender XDR Security for AI) | **1.21** | 1.21 *generates* attack evidence; 1.19 *holds and produces* it |
    | Incident reporting workflow / RCA / regulator notification mechanics (Form 8-K Item 1.05, Reg S-P 30-day, NYDFS 72-h, FINRA 4530) | **3.4** | 1.19 hands a confirmed incident to 3.4; 1.19 produces the evidence package |
    | Sentinel content-hub install, analytics rule tuning, hunting at scale | **3.9** | 1.19 references Sentinel only at the cross-plane correlation handoff |

!!! warning "Hedged-language reminder — supports, does not guarantee"
    Configuration of these surfaces **supports** firm compliance with **SEC 17a-4(b)(4)** and the **17a-4(f) audit-trail alternative (Oct 2022 amendment)**, **FINRA Rule 4511 / 8210 / 4530 / Notice 25-07**, **SOX Section 802 (18 USC §1519)**, **FRCP Rule 37(e)**, **GLBA Safeguards Rule (16 CFR Part 314)**, **Reg S-P (30-day customer notification, May 2024 amendment)**, **NYDFS 23 NYCRR Part 500 §500.17(a)**, **OCC Bulletin 2011-12 / Fed SR 11-7**, and **CFTC Rule 1.31**. It does **not** by itself satisfy any obligation.

    Specifically prohibited overclaims for this control: "ensures preservation", "guarantees defensible production", "complete capture of all AI interactions", "real-time discoverability", "instantaneous hold", "WORM-compliant by default". Designated Supervisors, the Compliance Officer, the Records Manager, and General Counsel must independently validate that the firm's WSP, retention schedule, hold-issuance procedure, production SLA, and incident-handling clocks reflect the **documented latencies and gaps** of the underlying Microsoft surfaces (see §0.2, §6.5, §10).

!!! info "What this walkthrough covers — surfaces & owners"
    | # | Surface | Portal | Owner role | Latency posture |
    |---|---|---|---|---|
    | 1 | Unified eDiscovery — Permissions and role groups | `purview.microsoft.com → Settings → Roles & scopes` | Purview Compliance Admin | Minutes (role propagation up to 1 h) |
    | 2 | Unified eDiscovery — Tenant settings (historical versions, OCR, deduplication, conversation reconstruction) | `purview.microsoft.com → Solutions → eDiscovery → Settings` | eDiscovery Administrator | Effective immediately for new searches |
    | 3 | Unified eDiscovery — Case lifecycle | `purview.microsoft.com → Solutions → eDiscovery → Cases` | eDiscovery Manager | Per case |
    | 4 | Custodians + non-custodial data sources (incl. **Microsoft 365 Copilot interactions** location) | `[case] → Data sources` | eDiscovery Manager | Index lag 4–24 h for new custodian |
    | 5 | Holds (case-scoped legal hold, including the **SubstrateHolds** preservation pattern) | `[case] → Holds` | eDiscovery Manager + second approver | Up to 24 h hold propagation |
    | 6 | Searches (KeyQL + condition cards incl. **Copilot activity**) | `[case] → Searches` | eDiscovery Manager | Index lag 4–24 h |
    | 7 | Review sets (conversation reconstruction, OCR, near-duplicate, themes, redaction, privilege) | `[case] → Review sets` | eDiscovery Manager / Reviewer | Per job |
    | 8 | Exports (load file + native + metadata + hash chain) | `[case] → Review sets → Action → Export` | eDiscovery Manager | Per export job (minutes–hours) |
    | 9 | Records Management — **Preservation Lock** (SEC 17a-4(f) handoff) | `purview.microsoft.com → Solutions → Records management` | Records Manager + Control 1.9 | Per label / per policy |
    | 10 | Power Platform — Dataverse audit and admin export (Copilot Studio transcript gap compensating control) | `admin.powerplatform.microsoft.com` | Power Platform Admin | Per environment |

!!! danger "Classic eDiscovery retired August 31, 2025 — except 21Vianet"
    Microsoft retired the classic eDiscovery (Standard) and eDiscovery (Premium) experiences on **August 31, 2025** in Commercial, GCC, GCC High, and DoD clouds. All commercial-cloud guidance below applies to the **unified eDiscovery experience** only.

    **Carve-out:** Microsoft 365 operated by **21Vianet (Gallatin / China)** continues to use the classic Standard / Premium eDiscovery surfaces. Firms with Gallatin tenants must continue using the legacy Microsoft Learn classic-eDiscovery documentation; the unified-eDiscovery procedures in this walkthrough do **not** apply to 21Vianet. Determine the cloud at the start of every matter — see §1.

---

## §0 Coverage boundary, discovery-plane inventory, and portal vs PowerShell matrix

### 0.1 Coverage boundary

In scope for this walkthrough:

- Unified eDiscovery cases scoped to Microsoft 365 Copilot prompts and responses preserved in the **SubstrateHolds** container of custodian Exchange Online mailboxes.
- Unified eDiscovery cases scoped to Copilot interactions surfaced through the dedicated **Microsoft 365 Copilot interactions** data-source location (Purview unified case wizard, GA in Commercial as of April 2026 — verify per cloud per §1).
- SharePoint sites and OneDrive accounts used as agent grounding sources (cross-link to Control 4.6 grounding-scope inventory).
- Teams 1:1 and group chats where Copilot operated (Exchange substrate dual-write).
- Copilot Studio agent transcripts that persist to mailbox; Copilot Studio transcripts that persist to **Dataverse** are documented as a coverage gap with compensating control in §6.5 and §14 anti-pattern AP-06.
- Hold issuance, search authoring (KeyQL + Copilot activity condition card), review-set culling and redaction, export with load file and hash chain, and the SEC 17a-4(f) handoff pathway to Records Management Preservation Lock under Control 1.9.

Out of scope (handled by sibling controls per the READ FIRST table above):

- Authoring of Unified Audit Log retention or the `CopilotInteraction` audit pipeline (Control 1.7).
- Authoring of retention policies, retention labels, and Preservation Lock (Control 1.9 — this is the WORM control, not 1.19).
- Authoring of Communication Compliance policies (Control 1.10 — Comm Compliance findings *feed* eDiscovery cases).
- Authoring of Sensitive Information Types (Control 1.13 — SITs are *consumed* in review-set culling).
- Reducing what an agent can ground on (Controls 1.14 and 4.6).
- Adversarial-input detection (Control 1.21 — its evidence is *preserved* via the §10.10 handoff into this control).
- Incident reporting workflow / regulator notification (Control 3.4 — receives the export package produced here).
- Sentinel-side cross-plane analytics tuning (Control 3.9).
- Azure AI Foundry / Azure OpenAI direct-call agent transcripts that live in resource diagnostic logs / Log Analytics — out of scope for unified eDiscovery; route to the Control 1.21 evidence pack and the Control 3.9 Sentinel pathway.

### 0.2 Six discovery planes plus latency reality

| # | Plane | Source surface | Content vs metadata | Typical latency | Sovereign-cloud parity (re-verify) |
|---|---|---|---|---|---|
| 1 | **Substrate plane** | SubstrateHolds container in user Exchange Online mailbox; Exchange mailbox proper; Teams chat (Exchange substrate) | **Content** — full prompt body, full response body, attachment payloads | Minutes to <1 h hot; up to 24 h full propagation | GA broadly |
| 2 | **Knowledge plane** | SharePoint sites, OneDrive accounts the agent grounded on | **Content** — source document, version history (subject to versioning policy under Control 1.9) | Indexing minutes–hours; 24 h after document mutation | GA broadly |
| 3 | **Audit plane** | Unified Audit Log `CopilotInteraction` records | **Metadata only** — user UPN, agent identifier, app context, timestamp, conversation thread ID, references-resource list, sensitive-info-type touch flags — **NO prompt body, NO response body** | Minutes to 24 h (Standard Audit) | GA broadly |
| 4 | **DSPM plane** | Purview DSPM for AI — Activity Explorer | Sampling + heuristic — scoping intelligence only, not full content | Hours to 24 h | Rolling per cloud (verify) |
| 5 | **Dataverse plane (out-of-band)** | Copilot Studio environment Dataverse `bot_transcript` (or env-specific) table | Content — but **not natively covered by unified eDiscovery as of April 2026** | Per Dataverse audit cadence | Limited preview / verify |
| 6 | **Foundry/diagnostic plane (out-of-scope)** | Azure AI Foundry / Azure OpenAI resource diagnostic logs to Log Analytics workspace | Content (where logging configured) | Per ingestion pipeline | Route to Control 1.21 / 3.9 |

!!! warning "Latency reality — do not write 'real-time' or 'instantaneous' into the WSP"
    Hold propagation can take **up to 24 hours**. SubstrateHolds population for a freshly issued Copilot prompt typically lags **minutes to hours**. Search indexing for a newly added custodian is **typically 4 hours, up to 24 hours**. WSP language that promises "immediate preservation", "real-time discoverability", "instantaneous hold activation", or "complete capture of all AI interactions" overstates Microsoft surface capability and creates regulatory exposure under FINRA 25-07 (which calls for documented operational realism in AI WSPs). Use the documented latencies; build a **24-hour buffer** into FRCP 37(e) hold-issuance procedures and FINRA 8210 production timelines.

### 0.3 Plane separation — content vs activity

The single most common 1.19 evidence-pipeline failure is conflating **eDiscovery content retrieval** with **`CopilotInteraction` audit metadata retrieval**. They are different planes producing different evidence types:

- **eDiscovery (Plane 1 + 2)** returns the **content** — the actual prompt text, the actual response text, the actual attachment payload, the actual SharePoint grounding document. This is what regulators and litigation counsel need to read.
- **Unified Audit Log `CopilotInteraction` (Plane 3)** returns **activity metadata** — who, when, which agent, which thread, which references — but **not the prompt body or response body**. This is what investigators need to build a forensic timeline and to scope a case.

Build evidence packages by **joining both**: eDiscovery for the content, `CopilotInteraction` for the activity context. Do not attempt content production from the audit plane alone (anti-pattern AP-02). Do not attempt forensic timeline reconstruction from the content plane alone — the SubstrateHolds container is not natively timeline-indexed for cross-custodian correlation.

### 0.4 Portal vs PowerShell matrix

| Configuration step | Portal? | PowerShell / CLI? | Notes |
|---|---|---|---|
| Assign eDiscovery role-group membership | ✅ Purview Settings | ✅ `Add-RoleGroupMember` (Security & Compliance PowerShell) | Portal recommended for first-time assignment + audit trail |
| Configure tenant-level eDiscovery settings (OCR, conversation reconstruction, deduplication) | ✅ | Limited — most settings UI-only | Portal recommended |
| Create eDiscovery case | ✅ | ✅ `New-ComplianceCase` | Either; portal recommended for case metadata |
| Add custodians | ✅ | ✅ `Add-eDiscoveryCaseMember` / case-scoped cmdlets (verify slug at deploy time) | Portal recommended for custodian-communication workflow |
| Add non-custodial data source (incl. **Microsoft 365 Copilot interactions** location) | ✅ | Limited — Copilot interactions location is portal-first as of April 2026 | **Portal-only for the Copilot interactions location** |
| Create hold (case-scoped) | ✅ | ✅ `New-CaseHoldPolicy` + `New-CaseHoldRule` | Both supported; portal recommended for two-admin pattern audit trail |
| Create collection / search | ✅ | ✅ `New-ComplianceSearch` | Both supported |
| Run search action (export, purge — purge is destructive, see anti-pattern AP-15) | ✅ | ✅ `New-ComplianceSearchAction` | Both supported; export from review set is portal-first for load-file generation |
| Review-set workflow (tag, redact, code) | ✅ | ❌ (no PowerShell authoring path) | Portal-only |
| Export from review set with load file | ✅ | Limited (export job triggerable; load-file generation is portal-managed) | Portal recommended |
| Verify export hash chain | ❌ (manifest visible in portal) | ✅ `Get-FileHash -Algorithm SHA256` | PowerShell required for end-to-end verification — see §8.5 |
| Records Management Preservation Lock (SEC 17a-4(f) handoff) | See **Control 1.9** | See **Control 1.9** | Out of scope here |
| Power Platform Dataverse audit + admin export (Copilot Studio gap compensating control) | ✅ Power Platform admin center | ✅ Power Platform admin PowerShell module | See §6.5 |

The companion `powershell-setup.md` in this directory mirrors every PowerShell-eligible step; the present walkthrough is the portal path.

---

## §1 Sovereign cloud applicability matrix

!!! danger "Cross-cloud parity is not symmetric — verify at deploy time"
    The matrix below reflects publicly documented availability as of **April 2026**. Microsoft adds and removes sovereign-cloud parity on a per-feature, per-region cadence. Re-verify against the [Microsoft 365 Government service description](https://learn.microsoft.com/en-us/office365/servicedescriptions/office-365-platform-service-description/office-365-us-government/office-365-us-government) and the [Purview eDiscovery overview](https://learn.microsoft.com/en-us/purview/ediscovery) **before** treating any item below as a primary control in GCC / GCC High / DoD / 21Vianet.

| Capability | Commercial | GCC | GCC High | DoD | 21Vianet (Gallatin) |
|---|---|---|---|---|---|
| Unified eDiscovery (case dashboard) | GA | GA | GA | GA | **N/A — classic eDiscovery only** |
| **Microsoft 365 Copilot interactions** data-source location in case wizard | GA | GA (verify) | **Lagging — verify per release** | **Lagging — verify per release** | N/A |
| `CopilotInteraction` audit record collection (consumed via Plane 3) | GA | GA | Verify per release | Verify per release | N/A |
| **SubstrateHolds** container preservation | GA | GA | GA | GA | N/A |
| Hold notification workflow (custodian acknowledgment) | GA | GA | GA | GA | N/A |
| Review set — conversation reconstruction (Teams Copilot threading) | GA | Rolling | Verify per release | Verify per release | N/A |
| Review set — themes, near-duplicate, email threading | GA | GA | Verify per release | Verify per release | N/A |
| Review set — OCR / transcription | GA | Rolling | Verify per release | Verify per release | N/A |
| Export with load file (Relativity / Concordance / generic) | GA | GA | GA | GA | N/A |
| Microsoft 365 Copilot (custodian-side prerequisite) | GA | GA | **Limited preview as of early 2026 — verify** | **Limited / verify** | N/A |
| Copilot Studio Dataverse via Purview (native integration) | **Limited preview / verify** | Verify | Likely unavailable — verify | Likely unavailable — verify | N/A |
| Purview Records Management — **Preservation Lock** (SEC 17a-4(f) handoff under Control 1.9) | GA | GA | GA | GA | Verify |
| Purview Audit (Advanced) for `eDiscoveryAdminOperation` long-term retention | GA | GA | GA | GA | N/A |

### 1.1 Per-cloud caveats

**Commercial.** Reference posture for this walkthrough. All capabilities GA except Copilot Studio Dataverse-via-Purview (limited preview).

**GCC.** Treat as Commercial-minus-30-days. Re-verify the Copilot interactions data-source location and review-set conversation reconstruction at deploy time.

**GCC High.** The Copilot interactions data-source location and conversation reconstruction are typically lagging in GCC High. As of April 2026, **Microsoft 365 Copilot itself is in limited preview in GCC High** — meaning the upstream prerequisite for any Copilot-content eDiscovery may not be deployable. Document the gap to the AI Governance Lead and Compliance Officer; substitute with custodian-mailbox-scoped searches (no Copilot interactions toggle) and accept that Copilot-content recall may be incomplete until parity arrives.

**DoD.** As GCC High, with greater lag. If Microsoft 365 Copilot is not deployed at all in the tenant, planes 1 and 5 (Copilot-specific) are not in scope; the eDiscovery posture reduces to standard Exchange / SharePoint / OneDrive / Teams discovery against custodian content (which remains GA). Document the reduced surface to the Designated Supervisor and CISO.

**21Vianet (Gallatin).** Unified eDiscovery is **not available**. Continue using classic eDiscovery (Standard / Premium) per the legacy Microsoft Learn classic-eDiscovery documentation. Determine the cloud at the start of every matter; if the firm operates a Gallatin tenant, route to the classic procedure and document the cloud determination in the case metadata. See anti-pattern AP-10.

### 1.2 Compensating controls when a capability is unavailable

| Unavailable capability | Compensating control | Risk-register entry (Control 1.2) |
|---|---|---|
| Copilot interactions data-source location | Custodian-scoped mailbox search with `itemclass:IPM.SkypeTeams.Message.Copilot.*` filter (verify exact item-class string at deploy time) plus explicit SubstrateHolds inclusion | Yes — document recall-completeness assumption |
| Conversation reconstruction | Manual reviewer methodology to reconstruct multi-turn threads from individual items; document methodology in privilege log | Yes — note manual-method risk to FINRA 8210 production |
| OCR in review set | Force OCR pre-export via third-party tool against the native files; document toolchain and hash | Yes — note tooling dependency |
| Copilot Studio Dataverse-via-Purview | Power Platform Dataverse audit + admin export per §6.5 | **Always required** — Dataverse gap is the largest 1.19 limitation |
| Microsoft 365 Copilot in GCC High / DoD | Restrict Zone 3 agents to Foundry-backed surfaces; route evidence via Control 1.21 + Control 3.9 (Sentinel) | Yes — document reduced unified-eDiscovery surface |

---

## §2 Pre-flight gates

Complete every gate below **before** opening the eDiscovery surface. Most failures during case execution trace back to a missed gate.

### 2.1 License gate

Re-verify SKU eligibility at deploy time against the [Microsoft 365 security & compliance licensing guidance](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-365-security-compliance-licensing-guidance):

- [ ] **eDiscovery (Standard scope):** Microsoft 365 / Office 365 **E3** — covers case creation, content search, basic legal hold, basic export.
- [ ] **eDiscovery (Premium scope):** Microsoft 365 **E5**, **E5 Compliance**, or the **eDiscovery Premium add-on** — required for custodian management with hold-notice workflow, review sets, conversation reconstruction (Teams / Copilot), transcription, predictive coding, and advanced indexing. **Required for Zone 2 review-set workflows and all Zone 3 features.**
- [ ] **Microsoft 365 Copilot license** assigned to every in-scope custodian — required for Copilot prompts and responses to be in scope of eDiscovery via the Copilot interactions location/condition. Loss of license can affect retrievability — pair with a Purview retention policy scoped to Copilot interactions under Control 1.9.
- [ ] **Microsoft Purview Audit (Advanced)** — required for long-term retention of `eDiscoveryAdminOperation`, `ComplianceSearch*`, `CaseHold*` operations beyond Standard Audit retention. E5 / E5 Compliance.
- [ ] **Purview Records Management** — required for the Preservation Lock pathway under Control 1.9 (the SEC 17a-4(f) format-compliance control).
- [ ] **Copilot Studio license** for the environments hosting Copilot Studio agents — relevant for the §6.5 Dataverse compensating control.
- [ ] **Power Platform per-app or per-user license** in environments hosting Copilot Studio agents — relevant for §6.5.
- [ ] **Immutable export storage (third-party)** — required only when relying on the SEC 17a-4(f) audit-trail alternative; the eDiscovery export itself is not WORM, the storage layer must be.

### 2.2 Role gate

Per Control 1.19 §Roles & Responsibilities and `docs/reference/role-catalog.md`. Configure all of these **before** any case is created.

| Role | Tenant scope | Case scope | Typical FSI assignee | Provisioning notes |
|---|---|---|---|---|
| **eDiscovery Administrator** (Purview eDiscovery role group) | Full tenant — can see and manage **all** cases, including those they are not a member of; can recover orphaned cases; manages tenant-level eDiscovery settings | Implicit access to all | Typically 1–2 named individuals (e.g., Head of Litigation Support) | **PIM-elevation only** in Zone 3 — eligible-only assignment; just-in-time activation with mandatory ticket reference; max 4–8 hour activation window. See anti-pattern AP-09. |
| **eDiscovery Manager** (Purview eDiscovery role group) | Can create cases; can only see and manage **cases they are a member of**; can add/remove case members within their own cases | Member of specific cases | Litigation / regulatory case managers (one per matter family) | Standing assignment acceptable; review membership quarterly |
| **Reviewer** (Purview eDiscovery role group) | No case-creation rights; can only access **review sets** within cases they are added to as Reviewer; can tag, redact, code documents but **cannot export** | Case-scoped, review-set-scoped | Outside counsel, internal investigators, privilege reviewers | Standing assignment acceptable; **separation of duties from Manager and Administrator is mandatory in Zone 3** — see anti-pattern AP-08 |
| **Purview Compliance Admin** | Tenant-level Purview portal RBAC | n/a | Platform admin team | **Does not implicitly grant eDiscovery role membership** — assignment must be explicit |
| **Records Manager** (Purview Records Manager role) | Records Management surface in Purview | n/a | Records / Information Governance lead | Required for the §10.1 SEC 17a-4(f) Preservation Lock handoff into Control 1.9 |
| **Designated Supervisor / Registered Principal** | Reviews production packages for FINRA 3110 supervisory sign-off | Per matter | Named per WSP | Must be human-named (not group); see anti-pattern AP-13 |
| **Compliance Officer** | Approves legal holds; signs off on production packages | Per matter | Named per WSP | Approves the two-admin pattern in §6.4 |
| **General Counsel** | Final sign-off on production package; privileged-review owner | Per matter | Named per WSP | Owns privilege determinations |
| **AI Governance Lead** | Maintains agent ↔ content-location map (Control 1.2 cross-reference); convenes Zone 3 quarterly drill (§11) | n/a | Named per WSP | Owns Dataverse compensating control coordination per §6.5 |
| **Power Platform Admin** | Power Platform admin center; Dataverse environment configuration | Per environment | Power Platform team | Required for §6.5 Copilot Studio compensating control |
| **CISO** | Sovereign-cloud determination; export-storage immutability sign-off | Tenant-wide | Named per WSP | Signs off on §10 incident pathways |

**Two-admin pattern for legal hold issuance (Zone 3 mandatory):** No single human should both author and activate a hold for a Zone 3 customer-facing or recordkeeping-scope agent matter. One eDiscovery Manager authors; a second eDiscovery Manager (or eDiscovery Administrator under PIM elevation) approves and activates. This is **not a Microsoft-enforced workflow** — it is a procedural control surfaced through the Purview Audit log (`HoldCreated` / `HoldUpdated` operations on different `UserId`). See §6.4 for the operational pattern and anti-pattern AP-12.

**Reviewer / Manager separation:** A single human should not hold both Reviewer and Manager rights on the same case. Reviewer-only cannot export; Manager can. Combining them collapses the separation-of-duties posture required for FINRA 8210 productions, SOX 802 anti-spoliation, and Reg S-P privileged-review handling. See anti-pattern AP-08.

**Comm Compliance / eDiscovery role separation:** A single human should not hold both Communication Compliance Investigator (Control 1.10) and eDiscovery Manager on the same case — combining them collapses the supervisory independence required by FINRA 3110.

### 2.3 Tenant settings gate

Verify these dependencies **before** the first case:

- [ ] **Unified Audit Log enabled** (Control 1.7) — required for `CaseHoldCreated`, `ComplianceSearchCreated`, `eDiscoveryAdminOperation` recording.
- [ ] **Advanced Audit retention enabled** for Zone 3 — long-term retention of eDiscovery operations is required to defend the chain of custody at the SEC 17a-4(b)(4) 6-year horizon.
- [ ] **Sensitivity labels published** (Control 1.10) — drives review-set culling by `Sensitivity` field.
- [ ] **Retention policies authored** (Control 1.9) — coordinate with hold posture so a label-driven deletion does not prematurely purge held content; Records Manager has signed off on the reconciliation matrix.
- [ ] **DSPM for AI active** (Control 1.6) — provides scoping intelligence (which agents touched what data) to inform case scope.
- [ ] **Microsoft 365 Copilot deployed** to in-scope custodians — without the license assignment, the Copilot interactions location returns nothing for that custodian.
- [ ] **Copilot Studio agent inventory** maintained in Control 1.2 agent registry, with environment ↔ Dataverse-table mapping for the §6.5 compensating control.
- [ ] **SharePoint grounding-source inventory** maintained in Control 4.6, with site URLs ready to add as non-custodial data sources.

### 2.4 WSP / change-control gate

- [ ] Written Supervisory Procedure references **unified eDiscovery** (not Standard/Premium) and acknowledges the August 31, 2025 retirement.
- [ ] Legal-hold approval workflow documented, including the two-admin pattern for Zone 3.
- [ ] FINRA 8210 production SLA documented (target ~30 days; 24-hour latency buffer per §0.2).
- [ ] FRCP 37(e) "litigation reasonably anticipated" trigger documented with hold-issuance procedure.
- [ ] SEC 17a-4(b)(4) recordkeeping retention floor documented (6 years total, first 2 years easily accessible) and tied to the agent registry under Control 1.2.
- [ ] SEC 17a-4(f) format-compliance pathway documented — eDiscovery hold preserves availability; **Records Management Preservation Lock under Control 1.9 provides format compliance**.
- [ ] Reg S-P 30-day customer-notification clock documented for matters that may surface NPI exposure.
- [ ] SEC Form 8-K Item 1.05 4-business-day clock documented for matters where the discovery effort itself is material.
- [ ] NYDFS 23 NYCRR Part 500 §500.17(a) 72-hour clock documented if the firm is NY-DFS-regulated.
- [ ] FINRA 4530 30-day clock documented for customer-complaint-related discovery.
- [ ] Copilot Studio Dataverse coverage gap disclosed in the WSP per §6.5 and AP-06.
- [ ] Sovereign-cloud determination procedure documented (Commercial / GCC / GCC High / DoD / 21Vianet) — see §1.

### 2.5 Test fixtures gate

- [ ] **Sandbox / test tenant** available where possible (verification cases against production carry collateral risk).
- [ ] **Test custodian** — a non-NPI test user with Microsoft 365 Copilot license and at least one week of synthetic Copilot prompt history.
- [ ] **Test SharePoint site** with grounding documents (mirrors a Zone 3 agent grounding surface; cross-reference Control 4.6).
- [ ] **Canary string** — a unique, traceable token (e.g., `FSI-CANARY-1.19-2026-04-XXXX`) embedded in a synthetic Copilot prompt. Used in §11 quarterly drill end-to-end verification.
- [ ] **PyRIT-derived adversarial fixture** coordinated with Control 1.21 — required for the §10.10 adversarial-evidence preservation handoff verification.
- [ ] **Test export landing zone** — a non-production immutable storage account or tenant-isolated SharePoint library, used for §8 dry runs without committing to long-term retention.

---


## §3 Create the case and add the custodian

### 3.1 Open the case dashboard

1. Navigate to `https://purview.microsoft.com`.
2. From the left navigation, choose **Solutions → eDiscovery**. The unified case dashboard opens.
3. Confirm the page header reads **eDiscovery** (not "eDiscovery (Standard)" or "eDiscovery (Premium)" — those legacy entry points were retired August 31, 2025 in Commercial / GCC / GCC High / DoD; if you see them, you are in the 21Vianet cloud — stop and route to classic eDiscovery per §1).

### 3.2 Verify your role

In the upper-right of the case dashboard, click your profile → **My permissions** (or run `Get-RoleGroupMember -Identity "eDiscovery Manager"` from Security & Compliance PowerShell):

- For Zone 1 / Zone 2 cases: confirm **eDiscovery Manager** membership.
- For Zone 3 customer-facing or recordkeeping-scope cases: confirm **eDiscovery Administrator** elevation has been activated through PIM with a ticket reference; capture the activation timestamp and the justification text into the case notes per §2.2.

### 3.3 Create the case

1. Click **Create case**.
2. **Name** the case using the firm's case-naming convention (recommended pattern: `{matter-id}-{matter-type}-{custodian-count}-{YYYYMMDD}`, e.g., `FSI-2026-0417-FINRA8210-CUST3-20260417`). Naming convention drives the §14 evidence pack indexing — see anti-pattern AP-15.
3. **Description** must include: matter type, regulatory citation (e.g., "FINRA Rule 8210 production response"), litigation-hold trigger date, requesting authority, and named Compliance Officer + General Counsel approvers.
4. **Case number** — the firm-internal matter ID, mirrored from the legal matter management system.
5. Set **Case format = Premium** (this is the unified format that replaced the legacy Standard / Premium split). For Standard-scope-licensed tenants, the option will be locked to Standard; document the reduced feature surface (no review sets, no conversation reconstruction) to the Compliance Officer.
6. Click **Save**. The case opens to the **Overview** tab.

### 3.4 Capture pre-flight evidence

Before adding any custodian or location, capture:

- [ ] Screenshot of the case **Overview** tab showing case ID, creator UPN, creation timestamp.
- [ ] Export the corresponding `CaseAdded` Unified Audit Log entry (Control 1.7) — `Search-UnifiedAuditLog -Operations CaseAdded -StartDate ... -EndDate ...`.
- [ ] Record the case ID into the §14 evidence-pack manifest under artifact #1.

### 3.5 Add custodians

1. Open the **Data sources** tab → **Add data source** → **Add new custodians**.
2. Enter the custodian UPN(s). The custodian-management workflow attaches:
   - The custodian's Exchange Online mailbox (including SubstrateHolds container).
   - The custodian's OneDrive for Business.
   - The custodian's Teams 1:1 and group chat content (substrate dual-write into mailbox).
3. **Microsoft 365 Copilot interactions toggle** — in the custodian wizard, confirm the **Microsoft 365 Copilot interactions** location is enabled for each custodian. If the toggle is absent in your cloud, document the gap per §1.1 and substitute the SubstrateHolds-direct compensating pattern in §6.3.
4. **Hold-notice (custodian acknowledgment) workflow** — for FRCP 37(e) and FINRA 8210 matters, configure the hold-notice template under **Custodians → Communications**. Acknowledgment metadata feeds the §14 evidence pack (artifact #4).
5. **Do not** add a custodian as a "non-custodial" location to bypass the acknowledgment workflow — this defeats the FRCP 37(e) defensibility pathway. See anti-pattern AP-11.
6. Click **Next** through the wizard, leaving the hold creation step **unchecked at this stage** (we author the hold separately in §6 to enforce the two-admin pattern).
7. Click **Submit**. The custodian appears in the Data sources list with status **Indexing** (typically 4–24 h to complete).

### 3.6 Add non-custodial data sources (agent grounding surfaces)

For SharePoint sites, OneDrive accounts, and Teams channels that the in-scope agent grounded on (cross-reference the Control 4.6 grounding-source inventory):

1. **Data sources → Add data source → Add non-custodial data sources**.
2. Choose **SharePoint sites** / **Mailboxes** / **Teams** as appropriate.
3. Enter the location URL or UPN.
4. **Mark each non-custodial source with a clear label** linking it to the agent registry entry under Control 1.2 (e.g., `grounding-source:Agent-WealthAdvisor-Prod-SP01`). This labelling is the audit trail that the case scope reflects the actual agent reach — required for FINRA 25-07 documented operational realism.
5. Click **Submit**.

### 3.7 Capture custodian + non-custodial evidence

- [ ] Screenshot of the **Data sources** tab showing all custodians + non-custodial sources with location URLs / UPNs.
- [ ] Export the `CustodianAddedToCase` UAL records.
- [ ] Map each non-custodial source to the Control 4.6 grounding-source inventory and the Control 1.2 agent registry; capture the mapping spreadsheet as evidence artifact #5.

---

## §4 Location selection — the five surfaces that hold agent interactions

Custodian addition (§3.5) attaches the standard four locations (mailbox, OneDrive, Teams, SharePoint personal). Agent-interaction discovery requires explicit attention to **five surfaces**, only some of which are toggled by the custodian wizard.

### 4.1 Microsoft 365 Copilot interactions location

Where Copilot prompts and responses surface in the unified case wizard.

1. **Data sources → Add data source → Add locations** → **Microsoft 365 Copilot interactions**.
2. Select the in-scope custodians (must already be added per §3.5).
3. The location attaches the **SubstrateHolds container** of each custodian's mailbox to the case scope.
4. Click **Submit**.

If the **Microsoft 365 Copilot interactions** location is not visible in your cloud (typical in GCC High / DoD as of April 2026 — re-verify per §1), use the SubstrateHolds-direct compensating pattern in §6.3 — add the custodian mailbox with an explicit search scope that includes the SubstrateHolds folder by `itemclass` filter.

### 4.2 Custodian Exchange Online mailbox (including SubstrateHolds)

Already attached by §3.5. Confirm:

- [ ] The mailbox shows **status: Indexed** (or **Indexing** if recent).
- [ ] The mailbox properties (click the custodian name → **Locations**) confirm the SubstrateHolds container is in scope. The SubstrateHolds container is a hidden folder; portal does not show its child items in the location browser, but searches and holds against the mailbox include it by default.

**Plain-language warning to the Compliance Officer:** Copilot prompts and responses are **not stored in Teams chat threads**. They are dual-written into the user's Exchange mailbox SubstrateHolds container. A custodian who deletes a Teams chat does not delete the Copilot prompt/response — the substrate copy persists subject to retention policy under Control 1.9. Conversely, a search scoped only to "Teams" without including the custodian mailbox will miss Copilot content. See anti-pattern AP-05.

### 4.3 SharePoint sites and OneDrive accounts (grounding surfaces)

1. Confirm the §3.6 non-custodial sources include every SharePoint site and OneDrive account the in-scope agent could ground on.
2. For Zone 3 agents, cross-check against Control 4.6 grounding-source inventory; document any divergence to the AI Governance Lead.
3. **Versioning:** confirm with Records Manager that SharePoint version history is preserved per the retention policy under Control 1.9 — eDiscovery returns the current version plus held prior versions.

### 4.4 Teams channels and chats

1. For 1:1 and group chat content, the custodian mailbox attachment (§4.2) is the substrate path.
2. For Teams **channel** content (standard, private, shared), add the parent Teams **SharePoint site** as a non-custodial source (private/shared channels each have their own site).
3. Confirm with the Teams admin (Control 4.x) that the channel inventory matches the agent grounding inventory.

### 4.5 Copilot Studio Dataverse (coverage gap)

The unified eDiscovery case wizard does **not** natively attach Dataverse `bot_transcript` (or environment-specific transcript) tables as of April 2026 — Microsoft has signaled future Purview integration for Copilot Studio in some cloud regions but the integration is in limited preview at best. Treat this as a known coverage gap.

**Compensating control (operationalized in §6.5):** Power Platform Admin runs Dataverse audit export per environment per matter; the export is hashed (SHA-256) and added to the §14 evidence pack as artifact #18. Document the gap to General Counsel **at hold issuance**, not at production. See anti-pattern AP-06.

### 4.6 Capture location evidence

- [ ] Screenshot of the **Data sources → Locations** tab confirming Copilot interactions location attached.
- [ ] Mapping spreadsheet (Control 4.6 grounding sources ↔ case non-custodial sources) signed by AI Governance Lead.
- [ ] Dataverse compensating-control disclosure memo signed by Power Platform Admin + General Counsel.

---

## §5 Author the search — KeyQL plus the Copilot activity condition card

### 5.1 Open the search authoring pane

1. From the case, open **Searches** tab → **New search**.
2. **Name** the search using the convention `{case-id}-search-{n}-{purpose}` (e.g., `FSI-2026-0417-FINRA8210-CUST3-20260417-search-01-initial-scope`).
3. **Description** must record the requesting authority, the date-range scope, and the keyword strategy rationale.

### 5.2 Choose locations

1. Select the custodians, non-custodial sources, and the Microsoft 365 Copilot interactions location attached in §3 / §4.
2. **Do not** use "All locations" for Zone 3 matters — over-collection inflates review cost and increases inadvertent privilege production risk.

### 5.3 KeyQL keyword strategy

KeyQL (Keyword Query Language) is the property-based query language for Purview searches. For agent-interaction matters:

#### 5.3.1 Date range

Always scope by date. Example:

```keyql
(received>=2025-10-01) AND (received<=2026-04-17)
```

For Copilot interactions, the `received` property maps to the substrate timestamp of the prompt/response item. Document the timezone assumption (UTC by default) in the case notes.

#### 5.3.2 Topical keywords

Use property-scoped terms where possible to reduce false positives:

```keyql
(subject:"Q4 forecast" OR body:"Q4 forecast") AND (participants:custodian@firm.com)
```

#### 5.3.3 The `from:"Copilot"` anti-pattern

**Do not** write a KeyQL filter such as `from:"Copilot"` or `sender:Copilot` to "find Copilot messages". Copilot prompts and responses **do not have a sender of "Copilot"** in the substrate item — they are stored in the SubstrateHolds container with the custodian as the participant and an item class such as `IPM.SkypeTeams.Message.Copilot.*` (verify exact strings at deploy time). A `from:"Copilot"` filter returns zero results and creates a defensibility gap if relied upon. See anti-pattern AP-01.

**Correct approach:** rely on the **Microsoft 365 Copilot interactions** location (§4.1) plus the **Copilot activity** condition card (§5.4) to scope. Use KeyQL only for date, topical keywords, sensitivity labels, and SIT references — not as the primary "is this a Copilot item" filter.

#### 5.3.4 SIT and label scoping

```keyql
(SensitiveType:"U.S. Social Security Number (SSN)") OR (SensitivityLabel:"Confidential\Customer NPI")
```

Cross-reference Control 1.13 (SIT authoring) and Control 1.10 (label authoring).

### 5.4 The Copilot activity condition card

The **Copilot activity** condition card (in the search authoring UI under **Add condition → Copilot activity**, where available — re-verify exact UI label per §1) lets you scope by:

- Conversation thread ID (for reconstructing a multi-turn interaction).
- Agent identifier (to scope to a specific Copilot or Copilot Studio agent — cross-reference the Control 1.2 agent registry).
- Reference resource flag (was the response grounded on a specific document?).
- Sensitive-info-type touch flag.

Use this card as the **primary** "is this a Copilot item and which agent" filter — in combination with the location selection in §4.1, not in lieu of it.

### 5.5 The CopilotInteraction-content anti-pattern

**Do not** assume that the Unified Audit Log `CopilotInteraction` operation contains the prompt body or the response body — it does **not**. `CopilotInteraction` is **metadata only**: who, when, which agent, which conversation thread, references-resource list, sensitive-info-type touch flags. The content itself is in the substrate (SubstrateHolds container) and is retrieved through eDiscovery — not through audit. See §0.3 plane separation and anti-pattern AP-02.

**Correct evidence-pipeline pattern:**
1. Use `CopilotInteraction` audit metadata (Plane 3) to scope the timeline and identify the conversation thread IDs of interest.
2. Use eDiscovery search with the Copilot activity condition card filtered by those thread IDs (Plane 1) to retrieve the actual prompt/response content.
3. Join both in the §14 evidence pack — neither alone is sufficient.

### 5.6 Run the search and review statistics

1. Click **Save and run**. Status moves to **Estimating**, then **Estimated**.
2. Review the **Statistics** tab:
   - **Items found** (count of substrate items matching the query).
   - **Locations searched** (custodian count, non-custodial count).
   - **Top locations by item count** — sanity-check that the SubstrateHolds container (or the custodian mailbox proxy) appears for any custodian with Copilot license.
   - **Unindexed items** count — non-zero counts must be triaged; for Zone 3, the Compliance Officer signs off on the disposition of unindexed items per §10.4.

### 5.7 Common search-statistics signals

| Signal | Likely cause | Action |
|---|---|---|
| Zero items from any custodian who is licensed for Copilot and has a week of activity | `from:"Copilot"` anti-pattern; or Copilot interactions location not attached; or wrong cloud (21Vianet) | Review §5.3.3, §4.1, §1 |
| Custodian shows zero items but other custodians return content | Indexing not complete (status "Indexing" still); or license assignment recent | Wait 24 h; verify license per §2.1 |
| High unindexed count concentrated in one custodian | Mailbox-corruption or item-class-not-recognized condition | Triage with Exchange Admin; document in §10.4 |
| SharePoint grounding source returns zero | Site URL incorrect; or site permissions exclude search service | Verify with Control 4.6 inventory |

### 5.8 Capture search evidence

- [ ] Screenshot of the **Statistics** tab.
- [ ] Export the search definition (KeyQL + condition cards) — captured as evidence artifact #8.
- [ ] Export the `ComplianceSearchCreated` and `ComplianceSearchStarted` UAL entries.

---

## §6 Issue the legal hold (case-scoped) — two-admin pattern

### 6.1 Conceptual model — hold preserves availability, not format

A case-scoped legal hold in unified eDiscovery places held items into a preservation state that **prevents purging by retention policy or user deletion** and routes deletions into the SubstrateHolds container (mailbox) or preservation hold library (SharePoint). The held items remain available for search, review-set ingestion, and export for as long as the hold is active.

A legal hold **does not** make the storage layer immutable in the SEC 17a-4(f) sense. Format compliance with 17a-4(f) — the WORM/immutable-storage requirement — is satisfied through the **Records Management Preservation Lock pathway under Control 1.9**, not through the eDiscovery hold. Pair the two; do not substitute one for the other. See anti-pattern AP-07.

### 6.2 Open the hold authoring pane

1. From the case, open **Holds** tab → **Create hold**.
2. **Name** using `{case-id}-hold-{n}-{scope}` (e.g., `FSI-2026-0417-FINRA8210-CUST3-20260417-hold-01-broad`).
3. **Description** must include the FRCP 37(e) reasonable-anticipation trigger date, the FINRA 8210 letter date (if applicable), the hold-author UPN, and the named hold-approver UPN (the second admin per §6.4).

### 6.3 Choose locations

1. Select the same custodians, non-custodial sources, and Copilot interactions location used in the §5 search.
2. **Explicitly include the SubstrateHolds preservation pattern** — when the Copilot interactions location is attached, SubstrateHolds is implicit; document the implicit inclusion in the hold notes for Compliance Officer sign-off.
3. For Zone 3 matters, **broaden** the hold scope to the custodian's full mailbox + OneDrive + Teams chat substrate — not just the Copilot interactions slice — to defend against future scope expansion. The cost of over-preserving is far lower than the cost of spoliation.

### 6.4 The two-admin pattern (Zone 3 mandatory)

The unified eDiscovery surface does **not** enforce a four-eyes hold-issuance workflow. The two-admin pattern is procedural:

1. **Author** (eDiscovery Manager A): completes the hold authoring pane, sets the query (if any), and clicks **Save** but **not Activate**. The hold is in **Inactive** state.
2. **Approver** (eDiscovery Manager B, or eDiscovery Administrator under PIM elevation): independently reviews the hold definition, captures a screenshot of the inactive-state hold, and clicks **Activate**. The hold transitions to **Active**.
3. **Audit trail:** the `HoldCreated` and `HoldUpdated` (status → Active) UAL operations record different `UserId` values — this is the evidence of the two-admin pattern. Capture both records as evidence artifact #11.
4. **WSP entry:** the firm's WSP must name the two-admin pattern as the Zone 3 standard and identify the named role-holders.

A single human authoring and activating in one session collapses the separation of duties and creates SOX 802 / FINRA 8210 defensibility exposure. See anti-pattern AP-12.

### 6.5 Copilot Studio Dataverse compensating control (issued in parallel with the hold)

Because the unified eDiscovery hold does not natively reach Copilot Studio Dataverse `bot_transcript` content, the Power Platform Admin executes the following compensating procedure **in parallel** with hold activation:

1. **Inventory:** identify every Copilot Studio environment hosting an in-scope agent (cross-reference Control 1.2 agent registry).
2. **Audit enable:** confirm Dataverse audit is enabled on the transcript table(s) for each environment (`admin.powerplatform.microsoft.com → Environments → [env] → Settings → Auditing`).
3. **Export:** trigger an admin-scoped Dataverse export of the transcript table(s) filtered by the custodian and date range matching the §5 search; the export is JSONL or CSV per the firm's standard.
4. **Hash:** Power Platform Admin computes SHA-256 of the export file.
5. **Lock:** the export is placed in immutable storage (matching the §10.1 SEC 17a-4(f) pathway under Control 1.9).
6. **Memo:** Power Platform Admin signs a memo to General Counsel disclosing the compensating control, the export hash, the immutable-storage location, and the timestamp.
7. **Repeat:** the export is re-run weekly until the hold is released (Dataverse audit retention is environment-dependent; weekly snapshots prevent loss).

The output of this procedure is evidence pack artifact #18. See anti-pattern AP-06.

### 6.6 Activate, propagate, verify

1. Approver clicks **Activate**. Status moves to **On (pending sync)** then **On**.
2. **Hold propagation can take up to 24 hours** to reach all locations — document this latency in the case notes and in any litigation-hold confirmation to opposing counsel.
3. **Verify propagation:** for each custodian mailbox, run `Get-Mailbox <upn> | FL *Hold*` (Exchange Online PowerShell) and confirm the case-scoped hold GUID appears in `InPlaceHolds`. For SharePoint sites, verify via SharePoint admin center site properties.

### 6.7 Capture hold evidence

- [ ] Screenshot of the hold definition (locations, query if any).
- [ ] Screenshot of the inactive-state hold (captured by approver before activation).
- [ ] Screenshot of the active-state hold with timestamp.
- [ ] UAL export of `HoldCreated` and `HoldUpdated` operations showing distinct author and approver UPNs.
- [ ] Mailbox `InPlaceHolds` verification output (PowerShell).
- [ ] Dataverse compensating-control memo (artifact #18).

---

## §7 Review set — culling, redaction, conversation reconstruction

### 7.1 Add search results to a review set

Review sets are an eDiscovery (Premium) feature; not available in Standard-licensed tenants.

1. From the search **Statistics** view, click **Action → Add to review set**.
2. Choose **Add results to a new review set** (or an existing review set if scope is appended).
3. Configure:
   - **Conversation reconstruction** — **on** for any matter touching Teams chat or Copilot interactions. This re-stitches multi-turn threads into a reviewer-friendly conversation view. Without it, reviewers see individual prompt/response items in isolation, which obscures context and inflates privilege-call risk. See anti-pattern AP-11.
   - **OCR** — **on** for any matter where attachments may contain image-based text (PDFs, screenshots). OCR adds to ingestion latency but is required to defend completeness of review. See anti-pattern AP-13.
   - **Inclusive deduplication** — **on** to suppress exact duplicates while preserving distinct custodian copies.
   - **Process modern attachments / cloud attachments** — **on** to follow links to cloud-hosted attachments (SharePoint / OneDrive) and ingest the linked file.
4. Click **Add**. The job moves to **Processing**; latency depends on volume (minutes for hundreds, hours for tens of thousands).

### 7.2 Verify review-set ingestion

1. Open **Review sets → [name]**.
2. Confirm **Total items** matches the search-stats count (after deduplication).
3. Sample three Copilot interactions:
   - Confirm the prompt body and the response body are both visible.
   - Confirm the **References** panel (where available) lists the SharePoint/OneDrive grounding documents.
   - Confirm the **Conversation** view threads multi-turn prompts together.

### 7.3 Cull and tag

1. Use **Filters** to cull by Sensitivity label, SIT match, custodian, date, or Copilot activity attribute (where the filter set surfaces it).
2. Apply **Tags** for: Responsive, Non-Responsive, Privileged, Confidential-Customer, Needs-Redaction.
3. The Reviewer role (separate human per §2.2) performs the substantive review and tagging.

### 7.4 Redact for privilege and NPI

1. Open a document → **Annotate** → draw redaction boxes over privileged or NPI passages.
2. Apply a **Reason** code per the firm's privilege log template.
3. The redacted view becomes the **production version** at export; the native is preserved separately for the privilege log.

### 7.5 Themes, near-duplicate, predictive coding (E5 only)

Where licensed, run:

- **Themes** — surfaces topic clusters; useful for early case assessment.
- **Near-duplicate detection** — groups items by lexical similarity; useful for batch tagging.
- **Predictive coding (TAR / continuous active learning)** — train on a seed set of Reviewer tags; surface likely-responsive items.

Document any predictive-coding model parameters and the seed-set composition in the case notes — required for FINRA 8210 defensibility if an opposing party challenges the production methodology.

### 7.6 Capture review-set evidence

- [ ] Screenshot of the review-set ingestion configuration (conversation reconstruction, OCR, deduplication settings).
- [ ] Tagging summary report (export from review set).
- [ ] Privilege log (export of all items tagged Privileged with redaction reason codes).
- [ ] Predictive-coding model summary (if used).

---

## §8 Export the production package — load file + native + metadata + hash chain

### 8.1 Open the export pane

1. From the review set, filter to items tagged **Responsive** AND NOT **Privileged**.
2. Click **Action → Export**.
3. Configure the export job:
   - **Output options** → include **Native files**, **Text files (extracted)**, **Tags**, **Metadata** (CSV).
   - **Load file format** → choose the format requested by the receiving party (Relativity, Concordance/DAT, or generic).
   - **Include conversations** → on (preserves the conversation reconstruction context).
   - **Include redactions** → on (so redactions are baked into the produced renditions).
   - **Apply password** → optional; coordinate with receiving party.

### 8.2 Run the export and download

1. Click **Export**. The job appears under **Exports** with status **In progress**.
2. When status moves to **Complete**, click the export job → **Download export**.
3. The download is a single ZIP containing folders: `NativeFiles/`, `ExtractedText/`, `Metadata.csv`, `Summary.csv`, the load file, and a Microsoft-generated manifest.

### 8.3 Verify the Microsoft-generated manifest

1. Open `Summary.csv` and confirm the item count matches the review-set responsive-tagged count.
2. Open the export-job summary in the portal and capture the Microsoft-reported export hash (where surfaced in the UI).

### 8.4 Build the chain-of-custody record

The chain of custody is the auditable narrative of who handled the production package, when, and what cryptographic checksum was observed at each handoff. Required for FINRA 8210 defensibility, FRCP 37(e) anti-spoliation defense, and SEC 17a-4(b)(4) recordkeeping integrity.

Capture, at minimum:

| Field | Source |
|---|---|
| Export job ID | Portal → Exports |
| Export creator UPN + timestamp | Portal → Exports → Job details |
| Microsoft-reported manifest hash | Portal (where available) + manifest file inside the ZIP |
| Independent SHA-256 of the downloaded ZIP | PowerShell (next subsection) |
| Receiving party UPN/email | Out-of-band record |
| Transmission mechanism | Out-of-band record (SFTP, secure file share, etc.) |
| Receiving-party acknowledgment SHA-256 | Receiving-party countersignature |

### 8.5 PowerShell — independent SHA-256 verification

Run from the workstation that downloaded the ZIP:

```powershell
$exportPath = "C:\eDiscovery\Exports\FSI-2026-0417-FINRA8210-CUST3-20260417-export-01.zip"
$hash = Get-FileHash -Path $exportPath -Algorithm SHA256
$hash | Format-List Algorithm, Hash, Path
```

Capture the output into the §14 evidence pack as artifact #21. The PowerShell-computed hash must match the manifest hash; any divergence is a chain-of-custody break and must be triaged before transmission. See anti-pattern AP-14.

### 8.6 Hand off to Records Management Preservation Lock (Control 1.9)

The exported ZIP is **not** WORM. To satisfy the SEC 17a-4(f) format-compliance pathway:

1. Transfer the ZIP to immutable storage governed by a Purview Records Management retention label with **Preservation Lock** applied (per Control 1.9 portal walkthrough).
2. Capture the Records Management label assignment and the preservation-lock confirmation.
3. The Records Manager signs the §14 artifact #22 (Preservation Lock confirmation memo).

### 8.7 Designated Supervisor sign-off

Per FINRA Rule 3110, a Designated Supervisor / Registered Principal must review the production package before transmission to the regulator. The supervisor:

1. Reviews the responsive-tagged item sample.
2. Reviews the privilege log.
3. Reviews the chain-of-custody record.
4. Signs the §14 artifact #23 (supervisory sign-off memo) with name, CRD number, date, and timestamp. **Group sign-off is not acceptable** — the human supervisor must be named. See anti-pattern AP-13.

### 8.8 Capture export evidence

- [ ] Export job summary (portal screenshot + downloaded `Summary.csv`).
- [ ] Microsoft-generated manifest.
- [ ] Independent PowerShell SHA-256 output.
- [ ] Chain-of-custody record (filled-in template).
- [ ] Records Management Preservation Lock confirmation.
- [ ] Designated Supervisor sign-off memo.

---

## §9 Zone-aware response matrix

The case-handling intensity scales with the agent zone. Determine the in-scope agent's zone (Control 1.2 agent registry) **before** opening the case; the zone drives the role assignments, hold scope, review-set features, supervisory sign-off, and incident clocks.

| Dimension | Zone 1 — Personal productivity | Zone 2 — Team / departmental | Zone 3 — Enterprise / customer-facing / recordkeeping-scope |
|---|---|---|---|
| Case-creation trigger | Ad-hoc (HR / internal investigation / individual complaint) | Internal investigation; Comm Compliance escalation; manager request | Regulator letter (FINRA 8210, SEC subpoena, OCC request); customer complaint; litigation hold; AI-incident escalation per Control 3.4 |
| eDiscovery role posture | Manager standing assignment OK; Reviewer optional | Manager standing OK; Reviewer mandatory; Comm Compliance separation enforced | **Two-admin pattern mandatory** (§6.4); eDiscovery Administrator PIM-only; Manager / Reviewer separation enforced (AP-08) |
| License floor | E3 + Copilot (where licensed) | E5 or eDiscovery Premium add-on | E5 + Advanced Audit + Records Management |
| Hold scope | Custodian mailbox + Copilot interactions location | Custodian mailbox + Copilot interactions + grounding non-custodial sources | Custodian mailbox + Copilot interactions + grounding non-custodial sources + Dataverse compensating control + parallel Records Management Preservation Lock |
| Hold-issuance pattern | Single Manager OK | Single Manager OK; Compliance Officer notified | **Two-admin pattern mandatory** (author + approver, distinct UPNs) |
| Review-set features | Optional | Conversation reconstruction + OCR mandatory | Conversation reconstruction + OCR + near-duplicate + (where used) predictive coding with documented seed set |
| Privilege log | Optional | Required | Required + General Counsel sign-off |
| Designated Supervisor sign-off | Not required | Recommended | **Mandatory, named human, with CRD number** |
| Production-package immutability | Standard storage OK | Standard storage OK | **Preservation Lock under Control 1.9 mandatory** for SEC 17a-4(f) pathway |
| Quarterly drill participation | Optional | Recommended | **Mandatory** — see §11 |
| Evidence-pack completeness | Subset of §14 (artifacts #1, #2, #4, #8, #11, #14, #17, #20, #21) acceptable | Most of §14 (omit #18 if no Copilot Studio in scope) | **All 25 artifacts** of §14 |
| Cross-plane audit join (Sentinel correlation under Control 3.9) | Optional | Recommended | **Mandatory** |
| Latency posture in WSP | "Best effort within Microsoft latency" | Documented latency, FRCP 37(e) hold within 24 h | Documented latency + 24 h buffer; FINRA 8210 production within ~30 days; SEC 17a-4(f) Preservation Lock within 24 h of hold |

---

## §10 FSI incident-handling pathways

Each pathway below is a regulator-facing scenario keyed to a specific clock and a specific evidence-package shape. The case-handling steps in §3–§8 produce the evidence; this section governs **timing, supervisory sign-off, and notification orchestration**.

### 10.1 SEC 17a-4(b)(4) recordkeeping retention floor + 17a-4(f) format compliance

**Trigger:** routine recordkeeping audit; SEC examination; firm-internal records-completeness review.

**Clock:** 17a-4(b)(4) requires 6-year retention (first 2 years easily accessible) for communications relating to the broker-dealer's business — **including** AI-mediated communications that constitute business communications under FINRA Notice 25-07 interpretive guidance.

**Pathway:**
1. eDiscovery hold preserves availability (this control, §6).
2. **Records Management Preservation Lock under Control 1.9** provides format compliance — without it, the firm relies on the eDiscovery hold alone, which is **not** WORM and does not satisfy 17a-4(f). See AP-07.
3. Document the dual-pathway (hold + lock) in the WSP.
4. Re-verify lock posture quarterly per §11.

### 10.2 SEC 17a-4(f) October 2022 audit-trail alternative

**Trigger:** firm elects to use the audit-trail alternative (rather than WORM media) for electronic records compliance.

**Clock:** continuous — the audit-trail alternative is a posture, not a one-time event.

**Pathway:**
1. The audit-trail alternative requires that the firm preserve original-and-modified records, preserve the audit trail of modifications, and verify integrity through cryptographic checksums.
2. eDiscovery export with SHA-256 verification (§8.5) provides the cryptographic checksum.
3. Records Management Preservation Lock (Control 1.9) provides the original-record preservation.
4. Unified Audit Log retention (Control 1.7, Advanced Audit) provides the modification audit trail.
5. The firm's Designated Third Party (D3P) attestation under 17a-4(f) must reference the Microsoft surface architecture; coordinate with the D3P annually.

### 10.3 FINRA Rule 8210 production response

**Trigger:** FINRA letter requesting documents and information.

**Clock:** typically ~30 days from letter date; firm-specific extensions negotiated case-by-case.

**Pathway:**
1. **Day 0 (letter received):** General Counsel logs the matter; Compliance Officer convenes the case team; eDiscovery Manager opens the case per §3.
2. **Day 0 + 24 h:** hold issued under the two-admin pattern per §6.4.
3. **Day 0 + 48 h:** custodians and non-custodial sources confirmed; Copilot interactions location attached; SharePoint grounding sources cross-checked with Control 4.6 inventory.
4. **Day 1–7:** search authoring and statistics review (§5); Compliance Officer reviews scope.
5. **Day 7–21:** review-set ingestion, culling, tagging, redaction (§7); General Counsel reviews privilege calls.
6. **Day 21–28:** export (§8); independent SHA-256 verification; chain-of-custody assembly; Designated Supervisor sign-off.
7. **Day 28–30:** transmission to FINRA; receiving-party acknowledgment captured.
8. **Build a 24-hour buffer** at every step to absorb the documented Microsoft surface latencies (§0.2). Do not promise FINRA a turn-around shorter than the Microsoft-surface latency floor; document any latency-driven extension request in the production cover letter.

### 10.4 FRCP Rule 37(e) anti-spoliation defense

**Trigger:** "litigation reasonably anticipated" — typically a demand letter, regulator inquiry, or internal counsel determination.

**Clock:** continuous from the trigger; the hold must be issued and propagated **promptly** to defend against a 37(e) sanctions motion.

**Pathway:**
1. **Hold issuance within 24 h of trigger** per §6 two-admin pattern.
2. **Hold notice to custodians** per §3.5 with acknowledgment workflow — the acknowledgment metadata is the affirmative-defense evidence at any future 37(e) hearing.
3. **Hold scope broadened** per §6.3 — over-preserve at the substrate level rather than rely on a narrow Copilot-only slice that may need to widen later.
4. **Latency disclosure:** any future 37(e) declaration must accurately characterize the Microsoft surface latencies (§0.2) — do not declare "instantaneous" or "real-time" hold under penalty of perjury when the documented surface behavior is "up to 24 hours". See AP-04.
5. **Triage unindexed items** per §5.7; Compliance Officer signs off on any non-zero unindexed disposition.

### 10.5 SOX Section 802 (18 USC §1519) anti-spoliation

**Trigger:** internal-controls audit, SEC investigation of financial reporting, internal whistleblower allegation touching books-and-records.

**Clock:** continuous; the criminal exposure of §1519 attaches to any knowing destruction or alteration of records "in relation to or contemplation of" a federal investigation.

**Pathway:**
1. Hold issuance under the two-admin pattern (§6.4) provides the procedural integrity.
2. Manager / Reviewer separation (§2.2) provides the role-segregation defense.
3. PIM elevation of eDiscovery Administrator (§2.2) prevents the standing-superuser anti-pattern (AP-09).
4. Records Management Preservation Lock (Control 1.9) provides format-immutability.
5. Designated Supervisor sign-off (§8.7) provides the named-human accountability.

### 10.6 GLBA Safeguards Rule (16 CFR Part 314) and Reg S-P 30-day customer notification (May 2024 amendment)

**Trigger:** unauthorized access to customer NPI suspected — including NPI surfaced through agent grounding (Copilot returning customer NPI to a user who should not have access — typically a Control 1.13 oversharing finding feeding into a 1.19 case).

**Clock:** Reg S-P amended (May 2024) requires customer notification "as soon as practicable but not later than 30 days" after determination that customer NPI has been or is reasonably likely to have been accessed without authorization.

**Pathway:**
1. eDiscovery case scoped to identify the affected customer set: search by SIT (`SensitiveType:"U.S. Social Security Number (SSN)"`, etc.) per §5.3.4.
2. Review-set culling (§7.3) confirms the identification of affected customers.
3. **Privacy office** (cross-reference Control 1.10 / Reg S-P workstream) initiates the 30-day notification clock from determination, not from discovery start.
4. Production package (§8) supports the notification narrative and any subsequent regulator inquiry.
5. **Do not** equate "eDiscovery hold issued" with "Reg S-P clock started" — the clock starts at determination of unauthorized access, which may precede or follow hold issuance.

### 10.7 NYDFS 23 NYCRR Part 500 §500.17(a) 72-hour notification

**Trigger:** cybersecurity event impacting NY-DFS-regulated entity; including AI-mediated incidents with NPI exposure.

**Clock:** 72 hours from determination of cybersecurity event.

**Pathway:**
1. Hold issuance per §6 within 24 h of trigger to preserve evidence ahead of the 72-h notification.
2. Coordinate with Control 3.4 incident-reporting workflow for the NYDFS notification proper.
3. The eDiscovery evidence package may not be production-ready within 72 h — that is acceptable; the notification is the trigger, not the production deadline.

### 10.8 SEC Form 8-K Item 1.05 (cybersecurity incident materiality) 4-business-day clock

**Trigger:** registrant determines a cybersecurity incident is material — including AI-incident matters where the discovery effort itself is material.

**Clock:** 4 business days from materiality determination.

**Pathway:**
1. Materiality determination is a Disclosure Committee call, not an eDiscovery call.
2. eDiscovery supports the materiality determination by surfacing the scope of affected systems / customers / data.
3. Coordinate hold issuance with disclosure preparation; do not let the hold-issuance latency push past the 4-business-day clock.

### 10.9 FINRA Rule 4530 customer-complaint reporting

**Trigger:** customer complaint touching AI-mediated interaction (e.g., Copilot-surfaced advice the customer disputes).

**Clock:** 30 days from receipt for written complaints; quarterly statistical reporting.

**Pathway:**
1. Hold issuance per §6 within 24 h of complaint receipt.
2. eDiscovery scope: the specific Copilot interactions plus any grounding sources; Conversation reconstruction (§7.1) is mandatory to reconstruct the multi-turn context the customer experienced.
3. Production package supports any subsequent FINRA arbitration or 8210 escalation.

### 10.10 Adversarial-input incident handoff from Control 1.21

**Trigger:** Defender for Cloud TP for AI Workloads alert; Defender XDR Security for AI alert; Prompt Shields detection feeding a confirmed prompt-injection or jailbreak incident under Control 1.21.

**Clock:** per Control 3.4 incident-response SLA (typically Sev-1 = 1 h to triage, 24 h to contain, 72 h to scope).

**Pathway:**
1. Control 1.21 generates the adversarial-input alert and the initial evidence (PyRIT-style attack trace, Defender alert artifact).
2. Control 1.19 case opened to **preserve and produce** the surrounding agent interactions: the prompts that triggered the detection, the agent's responses, the conversation thread, the grounding sources.
3. Use the Copilot activity condition card (§5.4) to scope by conversation thread ID matching the Defender alert.
4. Cross-plane join under Control 3.9 (Sentinel) correlates the Defender alert, the `CopilotInteraction` audit metadata, and the eDiscovery content.
5. Evidence package supports any subsequent regulator notification (NYDFS 72-h, SEC 8-K Item 1.05, Reg S-P 30-day) routed through Control 3.4.

### 10.11 Communication Compliance escalation (from Control 1.10)

**Trigger:** Comm Compliance "Detect Microsoft Copilot Interactions" template policy hits a Sev-1 threshold (e.g., regulated-conduct keyword in a Copilot prompt or response).

**Pathway:**
1. Comm Compliance Investigator (separate human from any case Manager / Reviewer per §2.2) escalates to Compliance Officer.
2. Compliance Officer convenes the case team; eDiscovery Manager opens the 1.19 case per §3.
3. The Comm Compliance evidence (the alert, the conversation excerpt) is **input** to the case; the eDiscovery production is the regulator-facing **output**.
4. Maintain Comm Compliance / eDiscovery role separation (§2.2) for the FINRA 3110 supervisory-independence defense.

---

## §11 Quarterly Zone 3 drill

A documented quarterly end-to-end exercise is the operational evidence that the Zone 3 eDiscovery posture works under timing pressure. Required for FINRA 25-07 documented operational realism and for SOX 802 anti-spoliation defensibility.

### 11.1 Drill scope

- One Zone 3 customer-facing or recordkeeping-scope agent (rotated quarterly across the agent registry per Control 1.2).
- One named test custodian (per §2.5).
- One canary string embedded in a synthetic Copilot prompt at least 7 days before the drill (so it has propagated through audit, DSPM, and SubstrateHolds).
- One PyRIT-derived adversarial fixture per §10.10 (rotated each quarter).

### 11.2 Drill scenario

Choose one of the §10 scenarios per quarter; rotate annually:

- Q1: FINRA 8210 (~30-day production)
- Q2: FRCP 37(e) (24-h hold issuance)
- Q3: Reg S-P 30-day customer notification
- Q4: §10.10 adversarial-input handoff from Control 1.21

### 11.3 Drill execution

1. **Convener:** AI Governance Lead.
2. **Participants:** eDiscovery Manager (author), eDiscovery Manager or Administrator (approver), Reviewer, Compliance Officer, General Counsel, Designated Supervisor, Records Manager, Power Platform Admin, CISO observer.
3. **Wall clock:** start clock at scenario trigger; record every step's wall-clock duration.
4. **Steps:** execute §3 → §8 end-to-end against the test custodian + canary; produce a synthetic export.
5. **Validate canary recovery:** the canary string must surface in the §7 review set and the §8 export. If it does not, root-cause the gap (license, location, KeyQL, hold propagation, indexing) and remediate before drill closeout.
6. **Validate Dataverse compensating control:** the Power Platform Admin runs §6.5 against the test environment; the Dataverse export hash is recorded.
7. **Validate hash chain:** §8.5 PowerShell SHA-256 matches Microsoft manifest.
8. **Validate Preservation Lock handoff:** Records Manager applies the lock per Control 1.9 and confirms.
9. **Validate Supervisor sign-off:** Designated Supervisor signs the synthetic production memo with name + CRD + timestamp.

### 11.4 Drill report

The AI Governance Lead produces a drill report containing:

- Wall-clock latency of each step against §0.2 expected ranges.
- Any latency excursion, with root-cause and remediation owner.
- Canary recovery confirmation.
- Hash-chain verification confirmation.
- Compensating-control verification confirmation.
- Preservation Lock confirmation.
- Designated Supervisor sign-off memo.
- Sign-off by Compliance Officer + General Counsel + CISO.

The report is filed to the §14 evidence pack as artifact #25 and feeds the Control 1.2 risk register update.

### 11.5 Drill cadence enforcement

Missed quarterly drills are a Sev-2 governance finding under the Control 1.2 risk-register taxonomy and must be raised at the next AI Governance Council meeting.

---

## §12 Verification handoff

Detailed verification procedures, test cases, and the canary-string playbook live in `verification-testing.md` in this directory. The portal walkthrough hands off to verification at the following checkpoints:

| §-checkpoint | Verification artifact | Owner |
|---|---|---|
| §2 pre-flight gates | Pre-flight checklist signed by Purview Compliance Admin + Compliance Officer | Compliance Officer |
| §3 case + custodians | `CaseAdded` and `CustodianAddedToCase` UAL evidence | eDiscovery Manager |
| §4 Copilot interactions location | Location screenshot + Control 4.6 mapping spreadsheet | AI Governance Lead |
| §5 search | Search definition export + statistics screenshot + canary-recovery confirmation | eDiscovery Manager |
| §6 hold | Two-admin UAL evidence + `Get-Mailbox` `InPlaceHolds` output + Dataverse compensating-control memo | eDiscovery Manager + Power Platform Admin |
| §7 review set | Ingestion configuration + tagging summary + privilege log | Reviewer + General Counsel |
| §8 export | Microsoft manifest + PowerShell SHA-256 + chain-of-custody record + Preservation Lock + Designated Supervisor sign-off | eDiscovery Manager + Records Manager + Designated Supervisor |
| §10 incident scenarios | Per-scenario clock-compliance evidence | Compliance Officer + General Counsel |
| §11 quarterly drill | Drill report (artifact #25) | AI Governance Lead |

For end-to-end verification (canary string round-trip, sovereign-cloud parity verification, hash-chain integrity), see `verification-testing.md`.

---

## §13 Troubleshooting handoff

Detailed symptom → root-cause → resolution tables live in `troubleshooting.md` in this directory. Common high-impact issues:

| Symptom | Likely root cause | Resolution location |
|---|---|---|
| Copilot interactions location absent in case wizard | Sovereign-cloud parity gap (GCC High / DoD); or 21Vianet (use classic) | §1.1; troubleshooting.md §"Sovereign-cloud parity" |
| `from:"Copilot"` returns zero items | Anti-pattern AP-01 | §5.3.3; troubleshooting.md §"Common KeyQL errors" |
| Custodian shows zero items despite Copilot license + activity | License recently assigned; or indexing not complete; or wrong cloud | §5.7; troubleshooting.md §"Indexing latency" |
| Hold shows "On" but `Get-Mailbox` does not list the hold GUID | Hold propagation lag (up to 24 h); or mailbox in litigation hold conflict state | §6.6; troubleshooting.md §"Hold propagation" |
| Review-set ingestion stuck in "Processing" > 24 h | OCR backlog; or large attachment volume; or service-side throttling | §7; troubleshooting.md §"Review-set processing" |
| PowerShell SHA-256 disagrees with Microsoft manifest hash | Download corruption; or manifest references pre-zip checksum, not zip checksum | §8.5; troubleshooting.md §"Hash-chain divergence" |
| Dataverse audit table empty for a Copilot Studio environment | Audit not enabled at environment creation; or transcript-table audit toggle off | §6.5; troubleshooting.md §"Dataverse compensating control" |
| Designated Supervisor balks at signing without supervisor-in-the-portal evidence | Group sign-off attempted (AP-13); or sign-off requested without privilege-log review | §8.7; troubleshooting.md §"Supervisory sign-off" |

---

## §14 Evidence pack — 25 artifacts with SHA-256 manifest

The evidence pack is the auditable bundle that survives the matter. Build it during the case, not after; the §11 quarterly drill validates that the build process is operational.

### 14.1 Artifact inventory

| # | Artifact | Section | Format | Owner |
|---|---|---|---|---|
| 1 | Case overview screenshot + `CaseAdded` UAL record | §3.4 | PNG + CSV | eDiscovery Manager |
| 2 | Pre-flight checklist signed by Compliance Officer | §2 | PDF | Compliance Officer |
| 3 | Sovereign-cloud determination memo | §1 | PDF | CISO |
| 4 | Custodian list + hold-notice acknowledgments | §3.5 | CSV + PDF | eDiscovery Manager |
| 5 | Non-custodial source ↔ Control 4.6 grounding inventory mapping | §3.6 | XLSX | AI Governance Lead |
| 6 | Copilot interactions location screenshot | §4.1 | PNG | eDiscovery Manager |
| 7 | Mailbox / SharePoint location verification | §4.2–4.4 | PNG + CSV | eDiscovery Manager |
| 8 | Search definition export (KeyQL + condition cards) | §5.6 | JSON + PNG | eDiscovery Manager |
| 9 | Search statistics screenshot | §5.6 | PNG | eDiscovery Manager |
| 10 | `ComplianceSearchCreated` / `Started` UAL records | §5.8 | CSV | eDiscovery Manager |
| 11 | Hold definition + inactive-state screenshot + active-state screenshot + two-admin UAL evidence | §6.7 | PNG + CSV | eDiscovery Manager (author) + approver |
| 12 | `Get-Mailbox InPlaceHolds` PowerShell output | §6.6 | TXT | eDiscovery Manager |
| 13 | Review-set ingestion configuration screenshot | §7.6 | PNG | eDiscovery Manager |
| 14 | Tagging summary report | §7.6 | CSV | Reviewer |
| 15 | Privilege log with redaction reason codes | §7.6 | XLSX + PDF | General Counsel |
| 16 | Predictive-coding model summary (if used) | §7.5 | PDF | eDiscovery Manager |
| 17 | Export job summary + Microsoft `Summary.csv` | §8.8 | PNG + CSV | eDiscovery Manager |
| 18 | Copilot Studio Dataverse compensating-control memo + export hash | §6.5 | PDF + TXT | Power Platform Admin |
| 19 | Microsoft-generated export manifest | §8.3 | TXT/JSON | eDiscovery Manager |
| 20 | Export ZIP (native + extracted text + metadata + load file) | §8.2 | ZIP | eDiscovery Manager |
| 21 | Independent PowerShell SHA-256 of export ZIP | §8.5 | TXT | eDiscovery Manager |
| 22 | Records Management Preservation Lock confirmation (Control 1.9 handoff) | §8.6 | PDF | Records Manager |
| 23 | Designated Supervisor sign-off memo (named human + CRD + timestamp) | §8.7 | PDF | Designated Supervisor |
| 24 | Chain-of-custody record (transmission to receiving party + acknowledgment) | §8.4 | PDF | eDiscovery Manager + General Counsel |
| 25 | Quarterly drill report (most recent applicable) | §11.4 | PDF | AI Governance Lead |

Zone 1 evidence packs may omit artifacts marked optional in §9. Zone 2 packs may omit artifact #18 if no Copilot Studio agent is in scope. Zone 3 packs **must** contain all 25 artifacts.

### 14.2 SHA-256 manifest — PowerShell

The evidence pack itself is hashed at packaging time. The hashes are recorded in a manifest that is countersigned by the Compliance Officer and the General Counsel and stored alongside the evidence pack in the immutable storage layer (Control 1.9 Preservation Lock).

```powershell
# Build the evidence pack manifest
$evidenceRoot = "C:\eDiscovery\EvidencePacks\FSI-2026-0417-FINRA8210-CUST3-20260417"
$manifestPath = Join-Path $evidenceRoot "manifest.sha256.txt"

$artifacts = Get-ChildItem -Path $evidenceRoot -Recurse -File |
    Where-Object { $_.Name -ne "manifest.sha256.txt" }

$manifestEntries = foreach ($artifact in $artifacts) {
    $hash = Get-FileHash -Path $artifact.FullName -Algorithm SHA256
    [PSCustomObject]@{
        RelativePath = $artifact.FullName.Substring($evidenceRoot.Length + 1)
        SizeBytes    = $artifact.Length
        SHA256       = $hash.Hash
        LastWriteUtc = $artifact.LastWriteTimeUtc.ToString("o")
    }
}

$manifestEntries |
    Sort-Object RelativePath |
    ForEach-Object { "{0}  {1}  {2}  {3}" -f $_.SHA256, $_.SizeBytes, $_.LastWriteUtc, $_.RelativePath } |
    Set-Content -Path $manifestPath -Encoding UTF8

# Hash the manifest itself (the meta-hash)
$manifestHash = Get-FileHash -Path $manifestPath -Algorithm SHA256
$manifestHash | Format-List Algorithm, Hash, Path
```

The output of the meta-hash is the single value the Compliance Officer + General Counsel countersign. Any subsequent integrity verification recomputes the per-artifact hashes, the manifest, and the meta-hash, and compares.

### 14.3 Anti-pattern catalog (must-not-do — 15 entries)

Each anti-pattern below has been observed in real FSI matters and has documented regulatory or defensibility consequences. Train every Zone 3 case team member on this catalog at onboarding and at the §11 quarterly drill.

| # | Anti-pattern | Why it fails | Correct pattern |
|---|---|---|---|
| **AP-01** | Writing `from:"Copilot"` or `sender:Copilot` in KeyQL to "find Copilot messages" | Copilot prompts/responses do not have a sender of "Copilot" in the substrate; the filter returns zero | §5.3.3 — use the Copilot interactions location (§4.1) plus the Copilot activity condition card (§5.4) |
| **AP-02** | Treating `CopilotInteraction` Unified Audit Log records as content evidence | The audit record is metadata only — no prompt body, no response body | §0.3 + §5.5 — join Plane 3 metadata with Plane 1 eDiscovery content |
| **AP-03** | Substituting Content Search for a case-scoped legal hold | Content Search does not preserve — items remain subject to deletion / retention purge | §6 — always issue a case-scoped hold via the Holds tab; the two-admin pattern under §6.4 in Zone 3 |
| **AP-04** | Declaring "real-time" or "instantaneous" hold / preservation in WSP, declarations, or production cover letters | Microsoft surface latency is up to 24 h; the overclaim creates 37(e) and SOX 802 exposure | §0.2 — use documented latencies; build a 24-h buffer |
| **AP-05** | Searching only "Teams" without including custodian mailbox to find Copilot interactions | Copilot prompts/responses live in mailbox SubstrateHolds, not in Teams chat threads | §4.2 — always attach the custodian mailbox; use the Copilot interactions location for clarity |
| **AP-06** | Treating Copilot Studio Dataverse `bot_transcript` content as covered by unified eDiscovery | Native unified-eDiscovery integration is in limited preview; Dataverse content is a known coverage gap | §6.5 — Power Platform Admin compensating control with weekly hashed exports |
| **AP-07** | Treating an eDiscovery hold as WORM / SEC 17a-4(f)-compliant | Hold preserves availability; format compliance requires Records Management Preservation Lock under Control 1.9 | §10.1 + §10.2 — pair the hold with the Preservation Lock, do not substitute |
| **AP-08** | Granting a single human both Reviewer and Manager rights on the same case | Collapses separation of duties; Reviewer cannot export, Manager can — combining defeats the FINRA 8210 / Reg S-P privileged-handling defense | §2.2 — strict role separation in Zone 3 |
| **AP-09** | Standing eDiscovery Administrator assignment without PIM elevation | Administrator can see and manage all cases tenant-wide; standing assignment is a privileged-access control failure under SOX 802 and OCC 2011-12 | §2.2 — eligible-only PIM with mandatory ticket reference and short activation window |
| **AP-10** | Applying the unified-eDiscovery procedure to a 21Vianet (Gallatin) tenant | 21Vianet remains on classic eDiscovery; unified surface is not available | §1 — determine the cloud at matter open; route Gallatin to classic procedure |
| **AP-11** | Skipping conversation reconstruction in review-set ingestion for Teams / Copilot matters | Reviewers see individual prompt/response items in isolation; loses multi-turn context; inflates privilege-call risk | §7.1 — conversation reconstruction on for any Teams / Copilot matter |
| **AP-12** | Single-human authoring + activating a Zone 3 hold in one session | Collapses the two-admin pattern; UAL shows single `UserId` for both `HoldCreated` and the activation `HoldUpdated` | §6.4 — distinct author UPN and approver UPN; capture both UAL records |
| **AP-13** | Group sign-off (e.g., "Compliance team approved") in lieu of a named Designated Supervisor with CRD number | FINRA 3110 requires named supervisor accountability; group sign-off is not defensible | §8.7 — named human, CRD, timestamp |
| **AP-14** | Skipping the independent PowerShell SHA-256 verification of the export ZIP and relying solely on the Microsoft-reported manifest hash | The Microsoft manifest reports the pre-zip checksum in some configurations; independent post-zip hash is the chain-of-custody anchor | §8.5 — always run `Get-FileHash -Algorithm SHA256` against the downloaded ZIP |
| **AP-15** | Ad-hoc case / search / hold / export naming that does not encode matter ID + custodian count + date | Defeats indexing of the §14 evidence pack; complicates supervisory review and any subsequent regulator inquiry | §3.3 + §5.1 + §6.2 + §8 — use the documented naming convention |

### 14.4 Cross-references

This control coordinates with:

- **Control 1.5 — Identity and access for AI** (custodian identity and Conditional Access posture for the case team)
- **Control 1.6 — DSPM for AI** (scoping intelligence — which agents touched what data)
- **Control 1.7 — Audit logging for AI agents** (the `CopilotInteraction` audit-plane source for Plane 3 in §0.2)
- **Control 1.9 — Records management and retention for AI content** (the SEC 17a-4(f) Preservation Lock pathway — pair, do not substitute)
- **Control 1.10 — Communication compliance for AI** (Comm Compliance escalations feeding eDiscovery cases per §10.11)
- **Control 1.13 — Sensitive Information Types for AI** (SITs consumed in review-set culling per §5.3.4 and §7.3)
- **Control 1.14 — Data minimization for AI grounding** (reducing the discoverable surface upstream)
- **Control 1.21 — Adversarial input detection for AI agents** (the upstream evidence source for §10.10)
- **Control 1.24 — AI incident response** (the §10 scenario clocks and notification workflow handoff)
- **Control 4.6 — Agent grounding scope** (the non-custodial source inventory per §3.6 and §4.3)
- **AI Incident Response Playbook** (the master orchestration doc for cross-control incident handling)

### 14.5 Closeout

When the matter closes:

1. **Preserve the hold** until General Counsel formally releases it. Premature hold release is a 37(e) / SOX 802 exposure.
2. **Close the case** in the portal only after evidence-pack countersignatures are filed (Compliance Officer + General Counsel + Records Manager + Designated Supervisor).
3. **Archive the evidence pack** to immutable storage governed by Records Management Preservation Lock under Control 1.9.
4. **Update the Control 1.2 risk register** with any latency excursion, gap discovered, or compensating-control invocation observed during the matter.
5. **Feed lessons learned** into the next §11 quarterly drill agenda.

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
