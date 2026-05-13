# Control 1.5 — Verification & Testing Playbook (DLP and Sensitivity Labels)

| Field | Value |
|---|---|
| **Control** | 1.5 — Data Loss Prevention (DLP) and Sensitivity Labels |
| **Pillar** | Pillar 1 — Security |
| **Audience** | Purview Compliance Admin · Purview DLP Admin · Power Platform Admin · Defender Admin · Sentinel Engineer · FINRA-registered Supervisor · Internal Audit · External Examiner |
| **Sovereign-cloud scope** | Commercial · GCC · GCC High · DoD (parity gaps called out per surface) |
| **Last UI verified** | April 2026 |
| **Verifier output contract** | `[pscustomobject]` with `TestId`, `Status ∈ {Clean, Anomaly, Pending, NotApplicable, Error}`, `Evidence`, `Notes`, `TimestampUtc` |

---

## Regulatory Hedging Notice

This playbook describes verification procedures that **support compliance with** FINRA Rules 3110 / 4511 / 17a-4, SEC Reg S-P (2024 amendments), SEC Reg S-ID, GLBA Safeguards Rule, SOX §404, OCC Bulletin 2013-29 / 2021-39, Federal Reserve SR 11-7, and CFTC Regulation 1.31. Running these tests **does not guarantee** regulatory compliance, **does not prevent** every data-loss scenario, and **does not eliminate** customer-information risk. Implementation requires legal review against the firm's WSPs, examiner expectations, and the specific sovereign-cloud tenancy in scope. Organizations should verify control efficacy through independent audit and validate sovereign-cloud parity gaps with Microsoft account teams before treating any test result as evidence of a fully-mitigated risk.

---

## Why This Playbook Is Foundational

Control 1.5 governs the perimeter that decides whether non-public information (NPI), Material Non-Public Information (MNPI), customer PII, and other regulated data can be ingested by, surfaced through, or exfiltrated by Microsoft 365 Copilot, Copilot Studio agents, declarative agents, and connected Power Platform / Defender for Cloud Apps surfaces. Failures here cascade into Reg S-P incident-notification clocks (Control 3.4), supervisory review obligations (Control 2.12), audit-record fidelity (Control 1.7), and Sentinel detection coverage (Control 3.9). A single missed surface — for example, an unmanaged Edge for Business AI session, a Power Platform HTTP connector, or a Power BI workspace without label inheritance — can become the examiner finding that defines the firm's next cycle.

This playbook operationalizes the 13-surface DLP coverage matrix from the Control 1.5 specification, the Reg S-P 2024 dual-clock readiness drill, the override-telemetry chain, and the sovereign-cloud parity matrix. Each test produces machine-verifiable evidence consumable by the assessment manifest (`collectorField`) and the v1.4 evidence pack.

---

## Audience and How to Use This Playbook

| Role | Primary use |
|---|---|
| Purview Compliance Admin | Owns POLICY, LABEL, COPILOT, AUDIT namespaces. Runs weekly + monthly tests. |
| Purview DLP Admin | Owns SURFACE, SYNTH, OVERRIDE namespaces. Runs the 13-surface coverage drill monthly. |
| Power Platform Admin | Co-owns SURFACE (connector classification, HTTP endpoint filtering). Runs PP-specific subtests monthly. |
| Defender Admin | Co-owns SURFACE (Endpoint DLP, Defender for Cloud Apps file policy, unmanaged-AI). |
| Sentinel Engineer | Owns OVERRIDE telemetry pipeline verification (audit → Sentinel → supervisor queue). |
| FINRA-registered Supervisor | Consumes OVERRIDE evidence for 3110 supervisory queue review (cross-link Control 2.12). |
| Internal Audit | Runs quarterly examiner-style sampling (Section 9) and signs the attestation chain (Section 1). |
| External Examiner | Consumes the annual attestation pack (Section 10) and the 7-year evidence archive (Section 8). |

**How to use:** start at Section 5 (pre-flight gates). If any PRE gate returns `Error` or `Anomaly`, halt and remediate before running namespace tests. Run namespace tests on the cadence in Section 4. Assemble the evidence pack (Section 8) at every quarter close. Sign the attestation chain (Section 1) at every quarter close and on every material DLP rule change.

---

## Cross-Links

| Related control | Why it matters here |
|---|---|
| [Control 1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | DSPM surfaces Copilot interaction telemetry that complements DLP block events. |
| [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | DLP RecordTypes (`ComplianceDLPSharePoint`, `ComplianceDLPExchange`, `DLPEndpoint`) flow through the unified audit pipeline. |
| [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | Comm Compliance policies consume DLP-tagged events for supervisory review queues. |
| [Control 1.13 — Sensitive Information Types and Pattern Recognition](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) | SITs and EDM classifiers are the primary detection primitives invoked by 1.5 rules. |
| [Control 1.15 — Encryption (Data in Transit and at Rest)](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | Sensitivity labels with encryption invoke Azure Information Protection / Rights Management. |
| [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Override events with justifications must reach the supervisory queue for 3110 review. |
| [Control 3.4 — Incident Reporting and Root-Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Reg S-P 2024 30-day affected-individual / 72-hour service-provider clocks fire from confirmed DLP incidents. |
| [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Override telemetry, block events, and policy-change audit records hydrate Sentinel detections. |

---

## What This Playbook Catches

- Missing or misconfigured DLP surfaces across the 13-surface matrix (SharePoint, OneDrive, Exchange, Teams, Endpoint, Copilot block-by-label, Copilot block-by-SIT-prompt, PP connector classification, PP HTTP filtering, Edge unmanaged-AI, Network DLP unmanaged-AI, Defender for Cloud Apps file policy, Power BI / Fabric).
- DLP rule shape errors (e.g., illegal same-rule SIT+label combination on Copilot location).
- Sensitivity label taxonomy drift, missing label publication, container-vs-file boundary errors, missing Copilot grounding labels.
- Synthetic-leak failures per surface using fake CC numbers (Luhn-valid 4xxx test IINs), synthetic SSNs, and test account numbers.
- Override events that never reach the supervisor queue (broken telemetry chain).
- Audit pipeline gaps — RecordType counts diverging from policy hit counts.
- Reg S-P 2024 dual-clock readiness gaps (incident playbook missing, RACI undefined, escalation untested).
- Sovereign-cloud parity gaps where IRM or Adaptive Protection are silently assumed in GCC / GCC High / DoD.

## What This Playbook Does NOT Claim

- It does not certify the firm's WSPs are sufficient — that is a legal-and-compliance determination.
- It does not validate that every regulated data element in the firm has a corresponding SIT or EDM classifier — that is the scope of Control 1.13.
- It does not prove customer notifications were timely under Reg S-P — only that the technical signal and the documented playbook exist; the determination lives in Control 3.4.
- It does not test third-party agents outside the M365 / Power Platform / Defender perimeter.
- It does not evaluate label-inheritance correctness in third-party productivity surfaces (Box, Slack, Google Workspace) beyond what Defender for Cloud Apps covers.
- A `Clean` result on any test means "no anomaly observed within the documented processing window" — not "no risk exists."

---


## Section 1 — Three-Signature Attestation Chain

Every quarter close and every material DLP rule, label policy, or PP connector classification change requires three signatures captured against a SHA-256 hash chain over the evidence pack (Section 8).

| Signer | Role | What they attest |
|---|---|---|
| **Sponsor** | Business unit head (e.g., Wealth Management COO) | The 13-surface coverage gaps documented in this cycle are accepted business risk OR have funded remediation tickets. |
| **Owner** | Purview Compliance Admin | The technical controls described in the evidence pack are the controls actually in production at the timestamp of the manifest. |
| **Compliance** | Chief Compliance Officer or designee | The override telemetry, supervisor-queue evidence, and Reg S-P drill outcomes meet the firm's WSPs. |

### Hash Chain

```
manifest.sha256        = SHA256(evidence-pack/*)
attestation.sponsor    = Sign(manifest.sha256, sponsor-key)
attestation.owner      = Sign(manifest.sha256 || attestation.sponsor, owner-key)
attestation.compliance = Sign(manifest.sha256 || attestation.sponsor || attestation.owner, compliance-key)
```

### Signature Methods by Zone

| Zone | Acceptable signature method |
|---|---|
| **Zone 1 — Personal productivity** | DocuSign or Adobe Sign with audit trail; signer identity bound to Entra UPN. |
| **Zone 2 — Team / departmental** | Hardware-backed Entra ID Verifiable Credential OR FIDO2 security key signing the manifest hash. |
| **Zone 3 — Enterprise / regulated** | HSM-backed signing key (Azure Key Vault Premium, FIPS 140-2 Level 3 in commercial; FIPS 140-3 in GCC High / DoD); signer requires PIM-elevated role with break-glass logging. |

Signatures are stored alongside the manifest in the WORM-treated evidence archive (Section 8).

---

## Section 2 — Sovereign Cloud Parity Matrix per Surface

| Surface | Commercial | GCC | GCC High | DoD | Notes |
|---|---|---|---|---|---|
| SharePoint Online DLP | ✅ | ✅ | ✅ | ✅ | Full parity. |
| OneDrive for Business DLP | ✅ | ✅ | ✅ | ✅ | Full parity. |
| Exchange Online DLP | ✅ | ✅ | ✅ | ✅ | Full parity. |
| Teams chat & channel DLP | ✅ | ✅ | ✅ | ✅ | Private-channel coverage requires same-tenant policy scope. |
| Endpoint DLP (Devices) | ✅ | ✅ | ✅ | ✅ | macOS support: last 3 versions only. |
| Copilot block-by-label (GA) | ✅ | ⚠️ | ⚠️ | ⚠️ | GA in commercial; verify GCC roadmap with account team — sovereign tenancies may lag. |
| Copilot block-by-SIT-prompt (preview) | ⚠️ Preview | ❌ | ❌ | ❌ | Preview feature; sovereign clouds: not available — document compensating control in WSPs. |
| PP connector classification (PPAC) | ✅ | ✅ | ✅ | ✅ | Full parity. API↔portal label mapping: `Confidential`→`Business`, `General`→`Non-Business`, `Blocked`→`Blocked`. |
| PP HTTP endpoint filtering (preview) | ⚠️ Preview | ⚠️ Preview | ❌ | ❌ | Preview status; verify with account team. |
| Edge for Business unmanaged AI (preview) | ⚠️ Preview | ❌ | ❌ | ❌ | ChatGPT / Gemini / DeepSeek targeting — preview only. |
| Network DLP for unmanaged AI (preview) | ⚠️ Preview | ❌ | ❌ | ❌ | Preview only; sovereign clouds: not available. |
| Defender for Cloud Apps file policy | ✅ | ✅ | ⚠️ | ⚠️ | GCC High / DoD: reduced connector catalog — confirm covered SaaS list. |
| Power BI / Fabric workspace label inheritance | ✅ | ✅ | ⚠️ | ⚠️ | Fabric availability varies; confirm with account team. |
| **IRM (Information Rights Management)** | ✅ | ❌ | ❌ | ❌ | **Not available in GCC / GCC High / DoD.** Document static role-based DLP rules as compensating control in WSPs. |
| **Adaptive Protection** | ✅ | ❌ | ❌ | ❌ | **Not available in GCC / GCC High / DoD.** Document static-threshold DLP rules as compensating control in WSPs. |
| Purview IP scanner (on-prem repositories) | ✅ | ✅ | ✅ | ✅ | Required for on-prem file shares feeding M365 Search / Copilot grounding. |

**Compensating-control guidance:** for any ❌ in Zone 3 sovereign deployments, the firm's WSPs must explicitly name (a) the surface, (b) the unavailable Microsoft control, (c) the static-rule or process compensating control, (d) the residual risk, and (e) the Sponsor sign-off (Section 1).

---


## Section 3 — Prerequisites

### Licensing

| Surface | Required SKU |
|---|---|
| SharePoint / OneDrive / Exchange / Teams DLP | Microsoft 365 E3 (DLP for Exchange/SharePoint/OneDrive) + E5 / E5 Compliance for Teams DLP at scale and advanced classifiers. |
| Endpoint DLP | Microsoft 365 E5 / E5 Compliance / Defender for Endpoint Plan 2. |
| Copilot block-by-label | Microsoft 365 Copilot license + E5 Compliance (Sensitivity Labels publishing). |
| Copilot block-by-SIT-prompt (preview) | Microsoft 365 Copilot + E5 Compliance + preview enrolment. |
| Power Platform DLP | Power Platform per-user / per-app license; PPAC access. |
| Defender for Cloud Apps file policy | Microsoft 365 E5 / Defender for Cloud Apps standalone. |
| Adaptive Protection | E5 Compliance + Insider Risk Management (commercial only). |

### Role Assignments (Canonical)

| Role | Scope used in this playbook |
|---|---|
| Purview Compliance Admin | DLP policy and rule read/write; sensitivity label publishing; audit search. |
| Purview DLP Admin | DLP policy and rule read/write only. |
| Power Platform Admin | PPAC environment and tenant DLP policies; connector classification. |
| Defender Admin | Endpoint DLP, Defender for Cloud Apps file policies. |
| Sentinel Engineer | Workspace Reader + analytics rule editor for the Sentinel workspace consuming UAL. |
| Entra Global Admin | Required only for break-glass and PIM activation; never used for routine verification. |

### Microsoft Graph and PowerShell Module Permissions

| Module / API | Permission | Used by |
|---|---|---|
| `ExchangeOnlineManagement` | `Connect-IPPSSession` (Security & Compliance PowerShell) — Compliance Admin role group | DLP cmdlets, label cmdlets, audit search |
| `Microsoft.PowerApps.Administration.PowerShell` (PS 5.1) | `Add-PowerAppsAccount` — Power Platform Admin | `Get-DlpPolicy`, connector classification |
| `Microsoft.Graph.Security` | `SecurityEvents.Read.All`, `InformationProtectionPolicy.Read.All` | Label policy export |
| Exchange Online (`Connect-ExchangeOnline`) | View-Only Audit Logs role | UAL search for RecordType counts |
| Defender for Cloud Apps API | Tenant-level file policy read | File policy export |

### Wrong-Shell Trap (Critical)

| Cmdlet family | Required session | Wrong-session symptom |
|---|---|---|
| `Get-DlpCompliancePolicy`, `Get-DlpComplianceRule`, `Get-Label`, `Get-LabelPolicy` | `Connect-IPPSSession` (Security & Compliance PowerShell) | Cmdlet not recognized OR silent zero rows from a Connect-ExchangeOnline session — false-pass risk. |
| `Get-DlpPolicy` (Power Platform) | `Add-PowerAppsAccount` from Windows PowerShell 5.1 | Cmdlet not recognized in PS 7; silent zero in unauthenticated session. |
| `Search-UnifiedAuditLog` | `Connect-ExchangeOnline` | Returns zero from S&C session. |
| Defender for Cloud Apps file policies | Defender XDR portal or MDA REST API | No cmdlet equivalent — REST only. |

All verifier scripts in this playbook invoke `Test-PreFlight` (defined in [`powershell-setup.md`](./powershell-setup.md)) which validates the active session matches the required cmdlet family and returns `Status = Error` on mismatch.

---

## Section 4 — Required Namespace × Zone Cadence Matrix

| Namespace | Zone 1 | Zone 2 | Zone 3 | Notes |
|---|---|---|---|---|
| SURFACE | Quarterly | Monthly | Weekly | 13-surface coverage drill. |
| POLICY | Monthly | Monthly | Weekly | Includes same-rule SIT+label restriction check. |
| LABEL | Quarterly | Monthly | Monthly | Container-vs-file boundary, Copilot grounding labels. |
| SYNTH | Quarterly | Monthly | Monthly | Synthetic-leak per surface; **never use real customer NPI**. |
| COPILOT | Monthly | Monthly | Weekly | Block-by-label, block-by-SIT-prompt, Copilot Studio agent grounding. |
| OVERRIDE | Weekly | Weekly | Daily | Telemetry sweep: audit → Sentinel → supervisor queue. |
| AUDIT | Weekly | Weekly | Daily | RecordType integrity. |
| INCIDENT | Annually | Semi-annually | Quarterly | Reg S-P 2024 dual-clock drill. |
| SOV | Per-tenancy quarterly | Per-tenancy quarterly | Per-tenancy quarterly | Sovereign-cloud parity confirmation. |
| **Per-change** | Within propagation window + 24h | Within propagation window + 24h | Within propagation window + 24h | Re-run affected namespace after any DLP rule, label, license, IRM tier, or connector inventory change. |

**Evidence retention:** 7 years on WORM-treated storage with SHA-256 sidecars (SEC Rule 17a-4 broker-dealer requirement). Ties to FINRA 3110 supervision evidence and SOX §404 IT control testing.

---

## Section 5 — Pre-Flight Gates

All seven gates must return `Status ∈ {Clean, NotApplicable}` before any namespace test runs. Any `Anomaly`, `Pending`, or `Error` halts the cycle and routes to the escalation matrix (Section 11).

| Gate | Check | Pass criterion |
|---|---|---|
| **PRE-01** | Correct PowerShell session for the cmdlet family in scope | `Test-PreFlight -CmdletFamily <name>` returns `Clean`. |
| **PRE-02** | Tenant region and sovereign cloud match the playbook scope | `Get-OrganizationConfig` `.Identity` resolves to expected tenancy; cloud parameter matches expected (`AzureCloud`, `AzureUSGovernment`, `AzureUSGovernment2`, `AzureUSGovernment3`). |
| **PRE-03** | Required licenses present and assigned | License inventory snapshot ≥ required SKU count for in-scope users. |
| **PRE-04** | Operator role membership at minimum required scope (least privilege) | PIM-elevated only for the duration of the test window; activation event captured. |
| **PRE-05** | Audit pipeline healthy (UAL ingestion lag < 30 minutes) | Last DLP RecordType timestamp within 30 minutes of NOW. |
| **PRE-06** | Copilot DLP propagation window not active for any in-scope rule modified within the last 4 hours | If active, mark affected COPILOT tests `Pending` (not `Anomaly`). |
| **PRE-07** | Evidence pack target storage is WORM-treated and writable | Test-write to evidence path; verify immutability flag. |

PRE-gate verifier output is the first artifact in every evidence pack.

---

## Section 6 — Documented Processing Windows

| Window | Duration | Effect on test results |
|---|---|---|
| Copilot DLP rule propagation | Up to 4 hours after any DLP rule edit affecting the Copilot location | COPILOT-namespace tests within window: `Status = Pending`. Do not escalate as `Anomaly` until window elapses + 30 minutes buffer. |
| Sensitivity label policy publication | Up to 24 hours for client refresh on Office desktop apps | LABEL-namespace tests against newly-published labels: `Status = Pending` for first 24h. |
| Endpoint DLP policy push | Up to 1 hour after policy save | Endpoint synthetic-leak tests within window: `Status = Pending`. |
| PP DLP policy propagation | Up to 30 minutes for tenant policies; longer for environment-scoped | PP SURFACE tests within window: `Status = Pending`. |
| UAL ingestion lag | Up to 30 minutes typical; up to 24 hours documented worst case | AUDIT RecordType counts within window: `Status = Pending`. |
| Defender for Cloud Apps file scan | Up to 24 hours for new file ingestion | MDA file-policy SYNTH tests within window: `Status = Pending`. |

`Pending` results carry forward to the next scheduled run; if `Pending` persists across two consecutive runs, escalate as `Anomaly`.

---


## Section 7 — Test Catalog

Each test returns `[pscustomobject]@{ TestId; Status; Evidence; Notes; TimestampUtc }` where `Status ∈ {Clean, Anomaly, Pending, NotApplicable, Error}`. Evidence files are written via `Write-FsiEvidence` (see [`powershell-setup.md`](./powershell-setup.md)) and rolled up into the evidence pack (Section 8).

> **⚠ Synthetic-data discipline:** SYNTH tests use **fake data only** — Luhn-valid 4xxx test IINs, synthetic SSNs from the IRS test-data ranges (e.g., `9xx-xx-xxxx`), and test account numbers prefixed `TEST-`. **Never use real customer NPI** in any verification test — doing so creates a real Reg S-P incident.

### Namespace: SURFACE — 13-surface coverage

#### T-SURFACE-01 — 13-surface enumeration

**Purpose.** Confirm the firm has at least one DLP enforcement rule (or documented compensating control) covering each of the 13 surfaces in the Control 1.5 specification.

**Procedure.**

1. Run `Test-PreFlight -CmdletFamily Purview, PowerPlatform, Defender`.
2. For each surface in the matrix below, query the appropriate API and record `Present | Missing | NotApplicable`.
3. For any `Missing` in Zone 3, the surface must have a documented compensating control referenced in WSPs; otherwise `Status = Anomaly`.

| # | Surface | Query |
|---|---|---|
| 1 | SharePoint Online | `Get-DlpComplianceRule \| Where { $_.SharePointLocation }` |
| 2 | OneDrive for Business | `Get-DlpComplianceRule \| Where { $_.OneDriveLocation }` |
| 3 | Exchange Online | `Get-DlpComplianceRule \| Where { $_.ExchangeLocation }` |
| 4 | Teams chat & channel | `Get-DlpComplianceRule \| Where { $_.TeamsLocation }` |
| 5 | Endpoint DLP (Devices) | `Get-DlpComplianceRule \| Where { $_.EndpointDlpLocation }` |
| 6 | Copilot block-by-label (GA) | `Get-DlpComplianceRule \| Where { $_.CopilotLocation -and $_.ContentContainsSensitiveLabel }` |
| 7 | Copilot block-by-SIT-prompt (preview) | `Get-DlpComplianceRule \| Where { $_.CopilotLocation -and $_.ContentContainsSensitiveInformation }` |
| 8 | PP connector classification (PPAC) | `Get-DlpPolicy` (PP module) |
| 9 | PP HTTP endpoint filtering (preview) | PPAC REST: `/providers/PowerPlatform.Governance/policies` |
| 10 | Edge for Business unmanaged-AI (preview) | Defender XDR Cloud Apps → Conditional Access App Control policies |
| 11 | Network DLP for unmanaged-AI (preview) | Defender XDR → Network Protection policies |
| 12 | Defender for Cloud Apps file policy | MDA REST: `/api/v1/file_policies/` |
| 13 | Power BI / Fabric workspace label inheritance | Fabric admin API: `admin/workspaces/scanResult` |

**Status mapping.**
- All 13 `Present` (or `NotApplicable` per sovereign matrix with documented compensating control) → `Clean`.
- Any `Missing` without a referenced compensating control → `Anomaly`.
- Any preview surface in a sovereign cloud where preview is unavailable → `NotApplicable`.

**Evidence.** `surface-coverage-<UTC>.json` listing all 13 surfaces with `Status`, `RuleCount`, `WspReference`.

#### T-SURFACE-02 — On-prem repository IP scanner coverage

Verify Purview Information Protection scanner is deployed against every on-prem file share that feeds M365 Search or Copilot grounding. `Status = Clean` only when scanner inventory matches WSP-listed in-scope shares.

---

### Namespace: POLICY — DLP policy shape

#### T-POLICY-01 — Same-rule SIT+label restriction

**Purpose.** Confirm no DLP rule scoped to the Copilot location combines `Content contains sensitive information types` AND `Content contains sensitivity labels` in a single rule (Microsoft restriction — must be two rules in the same policy).

**Procedure.**
1. `Connect-IPPSSession`.
2. `$rules = Get-DlpComplianceRule | Where { $_.CopilotLocation }`.
3. For each rule, parse `AdvancedRule` JSON and assert that `Condition.SubConditions` does NOT contain both `ContentContainsSensitiveInformation` and `ContentContainsSensitivityLabel`.

**Status.** Any violating rule → `Anomaly`.

#### T-POLICY-02 — Custom-template inventory

Confirm Copilot block-by-label rules use the GA "Custom" template (not legacy templates that lack Copilot location support). Inventory all DLP policy templates and flag any policy targeting Copilot that uses a non-Custom template.

#### T-POLICY-03 — License entitlement coverage

For every DLP policy, confirm the user/group scope is fully covered by required SKUs (E5 / E5 Compliance / Defender plans). Users in scope without entitlement produce silent non-enforcement → `Anomaly`.

---

### Namespace: LABEL — Sensitivity label taxonomy

#### T-LABEL-01 — Label publication and assignment

Confirm the published label policy reaches all users in scope. `Get-LabelPolicy | Format-List Name, Labels, ScopedLabels, Settings, ModernGroupLocation`. Cross-check `ScopedLabels` against expected taxonomy.

#### T-LABEL-02 — Container-vs-file boundary

Confirm container labels (Teams, M365 Groups, SharePoint sites) and file labels are distinct and correctly scoped. A single label scoped to both can produce inheritance surprises that misclassify Copilot grounding context.

#### T-LABEL-03 — Copilot grounding label presence

Confirm at least one label in the published policy carries the `EncryptionRightsDefinitions` property required to block Copilot from grounding on encrypted content for users without `EXTRACT` rights. `Status = Anomaly` if no encryption-bearing label is published in Zone 3.

#### T-LABEL-04 — API↔portal label normalization (Power Platform)

Confirm `Get-DlpPolicy` returned labels match portal display: `Confidential`→`Business`, `General`→`Non-Business`, `Blocked`→`Blocked`. Use `ConvertTo-FsiUiLabel` from [`powershell-setup.md`](./powershell-setup.md). Mismatch → `Error` (telemetry correctness issue, not a policy issue).

---


### Namespace: SYNTH — Synthetic-leak tests per surface

> **Reminder:** synthetic data only. Use Luhn-valid 4xxx test card numbers (e.g., `4111 1111 1111 1111`), synthetic SSNs (`9xx-xx-xxxx` test ranges), test account numbers prefixed `TEST-`. Do not pull from production data sources.

#### T-SYNTH-01 — SharePoint upload synthetic CC

Upload a `.docx` containing five Luhn-valid synthetic CC numbers to a SharePoint library in scope. Expected: DLP policy match within propagation window; UAL `RecordType = ComplianceDLPSharePoint` written. Verify policy-tip presented to test user.

#### T-SYNTH-02 — Exchange outbound synthetic SSN

Send a test email from a scoped mailbox to an external recipient with five synthetic SSNs in body. Expected: rule match, UAL `RecordType = ComplianceDLPExchange`, message blocked or quarantined per rule action.

#### T-SYNTH-03 — Endpoint clipboard synthetic data

On a managed endpoint in scope, copy synthetic CC content from a test file to clipboard and attempt paste to a non-allowed application. Expected: Endpoint DLP block; UAL `RecordType = DLPEndpoint`.

#### T-SYNTH-04 — Teams chat synthetic data

Post a Teams chat (in a non-private test channel) containing synthetic CC numbers. Expected: rule match; recipient sees policy-tip; UAL records the event.

#### T-SYNTH-05 — Copilot prompt synthetic SIT (block-by-SIT-prompt, preview)

In Copilot Chat, submit a prompt containing synthetic CC content. Expected (preview): block by SIT-prompt rule. `Status = NotApplicable` in sovereign clouds where preview is unavailable. `Status = Pending` within 4-hour propagation window.

#### T-SYNTH-06 — Copilot grounding on labelled file (block-by-label, GA)

Confirm a labelled file with `EncryptionRightsDefinitions` blocking `EXTRACT` does not appear in Copilot grounding citations for an unauthorized test user. Expected: file does not appear in citations; UAL records suppression.

#### T-SYNTH-07 — Power Platform connector synthetic data flow

Build a test flow that crosses the Business / Non-Business connector boundary with synthetic data. Expected: flow blocked at design-time per `Get-DlpPolicy` configuration.

#### T-SYNTH-08 — Defender for Cloud Apps synthetic file

Upload a synthetic-CC file to a non-MS SaaS surface covered by an MDA file policy. Expected: file policy match within 24h scan window.

> **Important:** SYNTH tests do not exhaustively prove DLP catches all NPI variants. They prove that the configured rule path produces the expected enforcement and audit signal for a known-good positive sample.

---

### Namespace: COPILOT — Copilot-specific tests

#### T-COPILOT-01 — Block-by-label (GA) end-to-end

Authorized user requests Copilot summary of a folder containing a labelled-and-encrypted file they cannot `EXTRACT`. Expected: Copilot returns content from accessible files only; cites no encrypted content; UAL `RecordType = ComplianceDLPSharePoint` records the suppression.

#### T-COPILOT-02 — Block-by-SIT-prompt (preview) end-to-end

User submits a prompt containing synthetic CC data. Expected (preview, commercial only): prompt blocked with policy-tip; UAL records the prompt-block event. `NotApplicable` in sovereign clouds.

#### T-COPILOT-03 — Copilot Studio agent grounding source DLP coverage

For each published Copilot Studio agent, enumerate grounding sources (SharePoint sites, Dataverse tables, web sources). Confirm each source has DLP coverage from T-SURFACE-01 results. Any source on a `Missing` surface → `Anomaly`.

#### T-COPILOT-04 — Calendar invite and direct-prompt-upload exclusions

Document (do not test) the known unsupported scenarios per the Control 1.5 spec: Copilot DLP location does NOT scan calendar invites, and files uploaded directly into a prompt are NOT scanned. `Status = NotApplicable` with a Notes pointer to the WSP compensating control.

---

### Namespace: OVERRIDE — Override telemetry chain

#### T-OVERRIDE-01 — End-to-end override chain

**Purpose.** Confirm a user-initiated DLP override with required justification produces audit (Control 1.7) → Sentinel (Control 3.9) → supervisor queue (Control 2.12).

**Procedure.**
1. Configure a low-risk test rule with policy-tip override allowed and required justification.
2. Test user triggers a synthetic match (T-SYNTH-01 variant) and overrides with justification text.
3. Within 30 minutes (UAL ingestion lag), verify:
   - UAL has the override event with `UserJustification` populated.
   - Sentinel `OfficeActivity` table contains the event.
   - The Comm Compliance / supervisor queue (per Control 2.12) shows a queued review item linking to the event.
4. Capture screenshots / API responses as evidence.

**Status.** Any broken link in the chain → `Anomaly`. `Pending` if within UAL ingestion lag.

#### T-OVERRIDE-02 — Override telemetry sweep

Daily query: `Search-UnifiedAuditLog -RecordType ComplianceDLPSharePoint,ComplianceDLPExchange,DLPEndpoint -Operations DLPRuleMatch -ResultSize 5000 | Where { $_.AuditData -match 'UserOverride' }`. Spot-check 5 randomly-sampled override events for justification text quality. Empty / boilerplate justifications → `Anomaly` and route to supervisor.

---

### Namespace: AUDIT — Audit pipeline integrity

#### T-AUDIT-01 — RecordType counts

Compare DLP rule-hit counts (from Purview Activity Explorer) against UAL RecordType counts for the same window. Divergence > 5% → `Anomaly` (audit pipeline gap → cross-link Control 1.7).

| Surface | RecordType |
|---|---|
| SharePoint / OneDrive | `ComplianceDLPSharePoint` |
| Exchange | `ComplianceDLPExchange` |
| Endpoint | `DLPEndpoint` |
| Teams | `ComplianceDLPSharePoint` (Teams chat files) / `ComplianceDLPExchange` (chat messages) |

#### T-AUDIT-02 — UAL ingestion lag

Sample most-recent DLP RecordType entry; compare to NOW. Lag > 30 minutes → `Pending`. Lag > 24 hours → `Anomaly`.

---

### Namespace: INCIDENT — Reg S-P 2024 dual-clock readiness

#### T-INCIDENT-01 — Reg S-P dual-clock drill

**Purpose.** Confirm the firm can determine and execute Reg S-P 2024 notification within 30 days (affected individuals) and 72 hours (covered service provider → covered institution) from a confirmed DLP incident.

**Procedure.** Tabletop drill annually (Z1) / semi-annually (Z2) / quarterly (Z3):
1. Stage a synthetic incident: T-SYNTH-02 escalated as a "real" event.
2. Walk the Control 3.4 incident playbook end-to-end.
3. Capture: time to detection, time to determination, time to notification draft, RACI execution, legal sign-off path.
4. Confirm the playbook references both the 30-day and 72-hour clocks and the trigger conditions for each.

**Status.** Drill completes within target windows → `Clean`. Any clock missed in drill → `Anomaly`. Playbook absent or not signed → `Anomaly`.

> DLP telemetry feeds the **determination** but does not satisfy the **written program** requirement, which lives in Control 3.4.

---

### Namespace: SOV — Sovereign-cloud parity

#### T-SOV-01 — IRM and Adaptive Protection N/A documentation

In any GCC / GCC High / DoD tenancy, confirm:
1. IRM is not enabled (it cannot be); WSPs reference the static role-based DLP rules acting as compensating control.
2. Adaptive Protection is not enabled (it cannot be); WSPs reference static-threshold DLP rules as compensating control.
3. Sponsor sign-off (Section 1) explicitly accepts the residual risk for the cycle.

`Status = Clean` only when all three artifacts exist with current-cycle signatures.

#### T-SOV-02 — Preview feature exclusion confirmation

For each preview-only surface (Copilot block-by-SIT-prompt, PP HTTP filtering, Edge unmanaged-AI, Network DLP unmanaged-AI), confirm the surface is documented as `NotApplicable` in the active sovereign tenancy with a compensating-control reference.

---


## Section 8 — Reconciliation Evidence Pack

At every quarter close, assemble the evidence pack:

```
evidence-pack/<YYYY-QN>/
  manifest.sha256                    # SHA-256 of every file below
  preflight/
    pre-01..pre-07-<UTC>.json
  surface/
    surface-coverage-<UTC>.json      # T-SURFACE-01 output
    onprem-scanner-<UTC>.json        # T-SURFACE-02
  policy/
    rule-shape-<UTC>.json            # T-POLICY-01..03
  label/
    label-policy-<UTC>.json          # T-LABEL-01..04
  synth/
    synth-<surface>-<UTC>.json       # T-SYNTH-01..08
  copilot/
    copilot-<UTC>.json               # T-COPILOT-01..04
  override/
    override-chain-<UTC>.json        # T-OVERRIDE-01
    override-sweep-<UTC>.json        # T-OVERRIDE-02
  audit/
    recordtype-counts-<UTC>.json     # T-AUDIT-01
    ual-lag-<UTC>.json               # T-AUDIT-02
  incident/
    regsp-drill-<UTC>.json           # T-INCIDENT-01
  sov/
    sovereign-parity-<UTC>.json      # T-SOV-01..02
  rollup/
    summary-<UTC>.json               # Get-FsiVerifierRollup output for collectorField
  attestation/
    attestation.sponsor.json
    attestation.owner.json
    attestation.compliance.json
```

`manifest.sha256` is computed last; the three attestation signatures sign the chain per Section 1. The whole directory is sealed to WORM storage (Azure Blob Immutable Storage with legal hold OR Azure Blob Versioning with time-based retention) for **7 years** (SEC Rule 17a-4).

---

## Section 9 — Quarterly Examiner-Style Audit

Internal Audit performs a seeded sampling pass each quarter:

1. Random sample 10 DLP rules across SharePoint, Exchange, Teams, Endpoint, Copilot.
2. Walk each rule from portal definition → PowerShell export → UAL hit history → supervisor queue (where overrides exist).
3. Sample 5 override events from the cycle; confirm justification adequacy and supervisor closure.
4. Sample 3 preview-feature surfaces; confirm sovereign-cloud `NotApplicable` documentation.
5. Re-execute T-INCIDENT-01 with a different synthetic scenario.
6. Issue findings; route any `Anomaly` to the escalation matrix (Section 11).

Sampling seed and methodology are recorded in the evidence pack so external examiners can reproduce.

---

## Section 10 — Annual External Attestation Pack

Once per fiscal year, compile:

- Four quarterly evidence packs.
- The 13-surface coverage trend across all four quarters (gaps opened, gaps closed).
- Override telemetry trend (volume, justification quality, supervisor closure SLA).
- Reg S-P drill outcomes for the year.
- Sovereign-cloud parity confirmations for each tenancy.
- All attestation signatures and the SHA-256 chain across the four quarters.
- WSP excerpts referencing the compensating controls invoked per surface.
- Microsoft roadmap delta (preview → GA transitions affecting the firm during the year).

Provide to external auditor / examiner under the firm's standard records-request handling.

---

## Section 11 — Failure Escalation Matrix

| Severity | Trigger | Owner SLA | Routing |
|---|---|---|---|
| **Critical** | T-OVERRIDE-01 chain broken (overrides not reaching supervisor); T-INCIDENT-01 drill fails clock; any production NPI confirmed in a non-DLP-covered surface; PRE-05 audit pipeline outage > 4 hours. | 1 hour to acknowledge; 4 hours to remediate or compensating control. | CISO + CCO + CRO; open Sev-1 ticket; consider Reg S-P 72-hour clock. |
| **High** | T-SURFACE-01 missing surface in Zone 3 without compensating control; T-POLICY-01 same-rule SIT+label violation; T-AUDIT-01 divergence > 5%. | 24 hours to remediate or open exception. | Purview Compliance Admin + Internal Audit; Sponsor notified. |
| **Medium** | T-LABEL boundary anomaly; T-SYNTH single-surface failure; T-OVERRIDE-02 boilerplate justifications above threshold. | 5 business days. | Owner remediates; tracked in next quarterly attestation. |
| **Low** | `Pending` results within documented processing windows; preview-feature drift in commercial. | Carry to next scheduled run; escalate to Medium if persists across two cycles. | Owner monitors. |

---

## Section 12 — Continuous Improvement

- Track each `Anomaly` to a remediation ticket and a root cause (cross-link Control 3.4).
- Review Microsoft roadmap monthly for preview → GA transitions; reclassify `NotApplicable` results once a feature reaches GA in the firm's tenancy.
- Re-run the SURFACE namespace within the propagation window + 24 hours after every license, role, or sovereign-cloud change.
- Feed override-telemetry trend into supervisor training (Control 2.12).
- Update the synthetic-data corpus annually to track new SIT and EDM coverage.

---

## Section 13 — References

- [Control 1.5 — Data Loss Prevention (DLP) and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)
- [Control 1.5 — Portal Walkthrough](./portal-walkthrough.md)
- [Control 1.5 — PowerShell Setup](./powershell-setup.md)
- [Control 1.5 — Troubleshooting](./troubleshooting.md)
- [Shared PowerShell Baseline](../../_shared/powershell-baseline.md)
- [Control 1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)
- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)
- [Control 1.13 — Sensitive Information Types and Pattern Recognition](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md)
- [Control 1.15 — Encryption (Data in Transit and at Rest)](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md)
- [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)
- [Control 3.4 — Incident Reporting and Root-Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)
- [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)
- Microsoft Learn — [Data Loss Prevention reference](https://learn.microsoft.com/purview/dlp-learn-about-dlp)
- Microsoft Learn — [DLP policy locations](https://learn.microsoft.com/purview/dlp-policy-reference)
- Microsoft Learn — [DLP for Microsoft 365 Copilot](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about)
- Microsoft Learn — [Sensitivity labels](https://learn.microsoft.com/purview/sensitivity-labels)
- Microsoft Learn — [Power Platform DLP policies](https://learn.microsoft.com/power-platform/admin/wp-data-loss-prevention)
- Microsoft Learn — [Adaptive Protection](https://learn.microsoft.com/purview/insider-risk-management-adaptive-protection)
- SEC — [Reg S-P 2024 amendments](https://www.sec.gov/files/rules/final/2024/34-100155.pdf)
- FINRA — [Rule 3110 Supervision](https://www.finra.org/rules-guidance/rulebooks/finra-rules/3110)
- SEC — [Rule 17a-4 Records to Be Preserved](https://www.ecfr.gov/current/title-17/chapter-II/part-240/section-240.17a-4)

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*
