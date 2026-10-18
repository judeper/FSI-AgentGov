# Control 1.5 — Verification & Testing Playbook (DLP and Sensitivity Labels)

| Field | Value |
|---|---|
| **Control** | 1.5 — Data Loss Prevention (DLP) and Sensitivity Labels |
| **Pillar** | Pillar 1 — Security |
| **Audience** | Purview Compliance Admin · Purview DLP Admin · Power Platform Admin · Defender Admin · Sentinel Engineer · FINRA-registered Supervisor · Internal Audit · External Examiner |
| **Cloud** | Commercial (Global) |
| **Last Verified:** | 2026-10-18 — Microsoft Learn documentation review; no tenant execution or UI/screenshot verification |
| **Last UI verified** | Historical April 2026 entry; not reverified in this review |
| **Verifier output contract** | `[pscustomobject]` with `TestId`, `Status ∈ {Clean, Anomaly, Pending, NotApplicable, Error}`, `Evidence`, `Notes`, `TimestampUtc` |

---

## Regulatory Hedging Notice

This playbook describes verification procedures that **support compliance with** FINRA Rules 3110 / 4511 / 17a-4, SEC Reg S-P (2024 amendments), SEC Reg S-ID, GLBA Safeguards Rule, SOX §404, OCC Bulletin 2013-29 / 2021-39, Federal Reserve SR 26-2 (formerly SR 11-7), and CFTC Regulation 1.31. Running these tests **does not guarantee** regulatory compliance, **does not prevent** every data-loss scenario, and **does not eliminate** customer-information risk. Implementation requires legal review against the firm's WSPs, examiner expectations, and the tenant environment in scope. Organizations should verify control efficacy through independent audit before treating any test result as evidence of a fully-mitigated risk.

---

## Why This Playbook Is Foundational

Control 1.5 governs the perimeter that decides whether non-public information (NPI), Material Non-Public Information (MNPI), customer PII, and other regulated data can be ingested by, surfaced through, or exfiltrated by Microsoft 365 Copilot, Microsoft Copilot Studio agents, declarative agents, and connected Power Platform / Defender for Cloud Apps surfaces. Failures here cascade into Reg S-P incident-notification clocks (Control 3.4), supervisory review obligations (Control 2.12), audit-record fidelity (Control 1.7), and Sentinel detection coverage (Control 3.9). A single missed surface — for example, an unmanaged Edge for Business AI session, a Power Platform HTTP connector, or a Power BI workspace without an applicable DLP policy — can become the examiner finding that defines the firm's next cycle.

This playbook operationalizes the 13-surface DLP coverage matrix from the Control 1.5 specification, the Reg S-P 2024 dual-clock readiness drill, the override-telemetry chain, and the evidence pack below. Tests are operator-run procedures, not supplied verifier implementations. The output contract is an organizational evidence format; it is not automatically collected or scored by the assessment engine.

**Coverage accounting:** rows 6 and 7 are separate Copilot behaviors, not separate policy locations. The on-premises scanner is an additional repository check (T-SURFACE-02), as in the control specification. A label-inheritance setting alone does not establish Fabric DLP coverage.

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
| [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | Communication Compliance evaluates scoped communications; a DLP override does not automatically create a review item. Verify the firm's separate routing integration. |
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
- Synthetic-leak failures per surface using classifier-validated fake CC numbers, synthetic SSNs, and test account numbers.
- Override events that never reach the supervisor queue (broken telemetry chain).
- Audit pipeline gaps — RecordType counts diverging from policy hit counts.
- Reg S-P 2024 dual-clock readiness gaps (incident playbook missing, RACI undefined, escalation untested).

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
| **Zone 1 — Personal productivity** | Organization-approved signature workflow with signer identity and verification evidence. |
| **Zone 2 — Team / departmental** | Organization-approved signing key and independently verifiable signature over the manifest; authentication alone is not an arbitrary-file signing mechanism. |
| **Zone 3 — Enterprise / regulated** | HSM-backed signing key; verify the deployed HSM version and validation against [Azure Key Vault documentation](https://learn.microsoft.com/en-us/azure/key-vault/general/overview). Capture signer authorization and any PIM activation separately. |

Signatures are stored alongside the manifest in the WORM-treated evidence archive (Section 8).

---

## Section 3 — Prerequisites

### Licensing

| Surface | Required SKU |
|---|---|
| SharePoint / OneDrive / Exchange DLP | Office 365 or Microsoft 365 E3 includes baseline DLP; advanced capabilities require the appropriate additional entitlement. |
| Teams message DLP | E5-level DLP entitlement (for example Microsoft 365 E5 or Microsoft Purview Suite); not an E3 capability at any scale. |
| Endpoint DLP | Microsoft 365 E5, Microsoft Purview Suite, or another listed Information Protection and Governance entitlement. Defender for Endpoint Plan 2 alone is not an Endpoint DLP license. |
| Copilot block-by-label | E5 / Microsoft Purview Suite or another eligible file/email-processing entitlement; verify access to the Copilot experience being tested separately. |
| Copilot block-by-SIT-prompt (preview) | Available to users of Microsoft Copilot and Copilot Chat; no additional E5 requirement for prompt DLP. Verify tenant rollout, not assumed preview enrollment. |
| Power Platform DLP | PPAC permissions and licenses for the apps, flows, and agents being exercised; do not infer a per-app/per-user DLP add-on requirement. |
| Edge for Business unmanaged-app DLP | Purview pay-as-you-go; Intune-managed Windows 10/11 and supported Edge versions. This is separate from Endpoint DLP. |
| Network data security | Integration-specific entitlement: Entra Global Secure Access requires eligible Purview plus Entra Internet Access (or the documented bundle); non-Microsoft SASE/secure-browser integrations require eligible Purview plus pay-as-you-go. |
| Defender for Cloud Apps file policy | Microsoft 365 E5 / Defender for Cloud Apps standalone. |
| Adaptive Protection | E5 Compliance + Insider Risk Management (commercial only). |

Check the current [Purview service description](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description), [browser DLP prerequisites](https://learn.microsoft.com/en-us/purview/dlp-browser-dlp-learn), and [network data security prerequisites](https://learn.microsoft.com/en-us/purview/dlp-network-data-security-learn) for every benefiting user and integration. The table is not a complete purchasing guide.

### Role Assignments (Canonical)

| Role | Scope used in this playbook |
|---|---|
| Purview Compliance Admin | DLP policy and rule read/write; sensitivity label publishing; audit search. |
| Purview DLP Admin | DLP policy and rule read/write only. |
| Power Platform Admin | PPAC environment and tenant DLP policies; connector classification. |
| Defender Admin | Defender device/app onboarding and legacy file policies; Purview DLP permissions are separately required for Purview rules. |
| Sentinel Engineer | Workspace read access and Microsoft Sentinel Contributor when editing analytics rules; ingestion setup may require additional resource permissions. |
| Entra Global Admin | Not required for routine verification or for activating an already eligible workload role in PIM. |

### Microsoft Graph and PowerShell Module Permissions

| Module / API | Permission | Used by |
|---|---|---|
| `ExchangeOnlineManagement` | `Connect-IPPSSession` (Security & Compliance PowerShell) — appropriate Purview role group | DLP and label cmdlets; connect Exchange Online separately for audit search |
| `Microsoft.PowerApps.Administration.PowerShell` (PS 5.1) | `Add-PowerAppsAccount` — Power Platform Admin | `Get-DlpPolicy`, connector classification |
| Microsoft Graph (optional) | `InformationProtectionPolicy.Read` for delegated user labels; `InformationProtectionPolicy.Read.All` application permission for organization inventory | Label inventory only, not label-policy export; see [List sensitivityLabels](https://learn.microsoft.com/en-us/graph/api/security-informationprotection-list-sensitivitylabels?view=graph-rest-beta). Use `Get-LabelPolicy` for policies. |
| Exchange Online (`Connect-ExchangeOnline`) | View-Only Audit Logs role | UAL search for RecordType counts |
| Defender for Cloud Apps | Appropriate portal policy permissions | Inspect legacy file policies in the portal; do not assume an undocumented file-policy REST endpoint. |

### Wrong-Shell Trap (Critical)

| Cmdlet family | Required session | Wrong-session symptom |
|---|---|---|
| `Get-DlpCompliancePolicy`, `Get-DlpComplianceRule`, `Get-Label`, `Get-LabelPolicy` | `Connect-IPPSSession` (Security & Compliance PowerShell) | Missing cmdlet, authorization failure, or unavailable session; treat errors as `Error`, not empty evidence. |
| `Get-DlpPolicy` (Power Platform) | `Add-PowerAppsAccount` in the supported Windows PowerShell host | Missing cmdlet or failed authentication is `Error`, not proof that no policies exist. |
| `Search-UnifiedAuditLog` | `Connect-ExchangeOnline` | Verify Audit Logs or View-Only Audit Logs access; a zero-result search is not a session-health test. |
| Defender for Cloud Apps file policies | Defender XDR portal | Review connected-app support and policy state; do not substitute a guessed API. |

Perform PRE-01 through PRE-07 explicitly. Neither `Test-PreFlight` nor `Get-FsiVerifierRollup` is supplied by the companion playbook. Any local verifier must implement and test the output contract before use. `Write-FsiEvidence` is a shared-baseline helper, not a Microsoft cmdlet; load it from the [shared baseline](../../_shared/powershell-baseline.md) and follow its actual parameters. Connection references: [Purview policy cmdlet](https://learn.microsoft.com/en-us/powershell/module/exchange/get-dlpcompliancepolicy), [Power Platform PowerShell](https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell), and [audit search](https://learn.microsoft.com/en-us/purview/audit-log-search).

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
| **Per-change** | Within propagation window + 24h | Within propagation window + 24h | Within propagation window + 24h | Re-run affected namespace after any DLP rule, label, license, IRM tier, or connector inventory change. |

**Evidence retention:** 7 years on WORM-treated storage with SHA-256 sidecars (SEC Rule 17a-4 broker-dealer requirement). Ties to FINRA 3110 supervision evidence and SOX §404 IT control testing.

---

## Section 5 — Pre-Flight Gates

All seven gates must return `Status ∈ {Clean, NotApplicable}` before any namespace test runs. Any `Anomaly`, `Pending`, or `Error` halts the cycle and routes to the escalation matrix (Section 11).

| Gate | Check | Pass criterion |
|---|---|---|
| **PRE-01** | Correct PowerShell session for the cmdlet family in scope | Confirm command availability, successful authenticated read, and required permissions separately in each control plane. |
| **PRE-02** | Tenant identity confirmed | Compare the tenant identifier in each authenticated connection with the approved test tenant; an organization display name alone is insufficient. |
| **PRE-03** | Required licenses present and assigned | License inventory snapshot ≥ required SKU count for in-scope users. |
| **PRE-04** | Operator role membership at minimum required scope (least privilege) | PIM-elevated only for the duration of the test window; activation event captured. |
| **PRE-05** | Audit pipeline healthy | Verify ingestion enabled from Exchange Online and search for a known positive test event; core-service records typically take 60–90 minutes, with no guaranteed maximum. An idle tenant need not have recent DLP events. |
| **PRE-06** | Copilot DLP propagation window not active for any in-scope rule modified within the last 4 hours | If active, mark affected COPILOT tests `Pending` (not `Anomaly`). |
| **PRE-07** | Evidence pack target storage is WORM-treated and writable | Test-write to evidence path; verify immutability flag. |

PRE-gate verifier output is the first artifact in every evidence pack.

---

## Section 6 — Documented Processing Windows

| Window | Duration | Effect on test results |
|---|---|---|
| Copilot DLP rule propagation | Up to 4 hours after any DLP rule edit affecting the Copilot location | COPILOT-namespace tests within window: `Status = Pending`. Do not escalate as `Anomaly` until window elapses + 30 minutes buffer. |
| Sensitivity label policy publication | Allow up to 24 hours for changes to replicate; client refresh can require additional time | Record publication and client observation separately; use `Pending` while replication/refresh is unconfirmed. |
| Endpoint DLP policy push | Verify device policy synchronization and connectivity; no universal one-hour completion bound is asserted here | Endpoint tests remain `Pending` until the device has received the intended policy. |
| PP DLP policy propagation | Within an hour in most cases; up to 24 hours per Microsoft Learn (tenant- and environment-scoped) | PP SURFACE tests within window: `Status = Pending`. |
| UAL ingestion lag | Core services typically 60–90 minutes; Microsoft commits to no fixed maximum | Missing known events remain `Pending` during investigation; firm escalation thresholds are not Microsoft SLAs. |
| Browser / network DLP activation | Network integration: allow up to 24 hours initially, then up to 30 minutes for request data; browser activation errors must be resolved | Validate the specific enforcement plane; these are not Endpoint DLP policy-push timings. |
| Defender for Cloud Apps file scan | App/API and inventory dependent; no universal 24-hour scan bound | Record connected-app health and scan status before interpreting missing matches. |

`Pending` results carry forward to the next scheduled run; if `Pending` persists across two consecutive runs, escalate as `Anomaly`.

---


## Section 7 — Test Catalog

Record each test as an object with `TestId`, `Status`, `Evidence`, `Notes`, and `TimestampUtc`, where `Status ∈ {Clean, Anomaly, Pending, NotApplicable, Error}`. This describes a result schema, not executable PowerShell. Save raw exports before hashing and assembling the evidence pack (Section 8).

> **⚠ Synthetic-data discipline:** SYNTH tests use **fake data only**, with each positive sample first validated against the exact SIT, confidence, proximity, and count. The built-in [credit-card SIT](https://learn.microsoft.com/en-us/purview/sit-defn-credit-card-number) excludes reserved test numbers; Luhn validity alone is insufficient. Do not assume `9xx-xx-xxxx` matches the [U.S. SSN SIT](https://learn.microsoft.com/en-us/purview/sit-defn-us-social-security-number). A custom `TEST-` account pattern tests only the custom SIT configured for it. **Never use real customer NPI** in any verification test — doing so creates a real Reg S-P incident.

### Namespace: SURFACE — 13-surface coverage

#### T-SURFACE-01 — 13-surface enumeration

**Purpose.** Confirm the firm has at least one DLP enforcement rule (or documented compensating control) covering each of the 13 surfaces in the Control 1.5 specification.

**Procedure.**

1. Complete the pre-flight gates for Purview, Power Platform, and any in-scope browser, network, or connected-app integration.
2. For each surface in the matrix below, inspect its control plane or supported API and record `Present | Missing | NotApplicable`.
3. For any `Missing` in Zone 3, the surface must have a documented compensating control referenced in WSPs; otherwise `Status = Anomaly`.

| # | Surface | Query |
|---|---|---|
| 1 | SharePoint Online | Policy `.SharePointLocation`, then rules for each policy |
| 2 | OneDrive for Business | Policy `.OneDriveLocation`, then rules for each policy |
| 3 | Exchange Online | Policy `.ExchangeLocation`, then rules for each policy |
| 4 | Teams chat & channel | Policy `.TeamsLocation`, then rules and user/group scope |
| 5 | Endpoint DLP (Devices) | Policy `.EndpointDlpLocation`, then rules and device onboarding |
| 6 | Copilot block-by-label (GA) | Policy `Locations` and `EnforcementPlanes = CopilotExperiences`, then label condition and processing action |
| 7 | Copilot block-by-SIT-prompt (preview) | Same policy location, then SIT condition and **Processing prompts** action; web-search restriction alone does not block the prompt |
| 8 | PP connector classification (PPAC) | `Get-DlpPolicy` (PP module) |
| 9 | PP HTTP endpoint filtering (preview) | `Get-PowerAppDlpPolicyConnectorConfigurations -TenantId <tenant-guid> -PolicyName <policy-guid>`; inspect ordered endpoint rules |
| 10 | Edge for Business unmanaged-AI | Purview **Data Loss Prevention → Policies → Inline web traffic**; verify **Edge for Business** enforcement and automatic activation |
| 11 | Network data security | Purview **Data Loss Prevention → Security Store** integration plus **Inline web traffic → Network and non-Microsoft secure browsers** policy |
| 12 | Defender for Cloud Apps legacy file policy | Defender **Cloud Apps → Policies → Policy management**; record migration plan before file policies retire January 6, 2027 |
| 13 | Power BI / Fabric DLP | Purview **Fabric and Power BI workspaces** location, supported capacity/item/condition, and positive match evidence; label inheritance alone is insufficient |

For rows 1–7, start with `Get-DlpCompliancePolicy`, inspect policy mode and scope, then use `Get-DlpComplianceRule -Policy <policy-name>`. Current Copilot policy authoring uses `-Locations` with application location ID `470f2276-e011-4e9d-a6ec-20768be3a4b0` and policy-level `-EnforcementPlanes @('CopilotExperiences')`; do not assume the older `MicrosoftCopilotEnabledLocation` parameter is available. Location presence is configuration evidence, not enforcement proof: simulation, disabled rules, exclusions, and unsupported actions can all produce false coverage. Inspect returned rule conditions/actions in full rather than assuming a fixed `AdvancedRule` JSON layout. References: [policy parameters](https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancepolicy), [rule parameters](https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancerule), [endpoint filtering](https://learn.microsoft.com/en-us/power-platform/admin/connector-endpoint-filtering), [browser DLP](https://learn.microsoft.com/en-us/purview/dlp-browser-dlp-learn), [network DLP](https://learn.microsoft.com/en-us/purview/dlp-network-data-security-learn), [legacy file policies](https://learn.microsoft.com/en-us/defender-cloud-apps/data-protection-policies), and [Fabric DLP](https://learn.microsoft.com/en-us/purview/dlp-powerbi-get-started).

**Status mapping.**
- All applicable surfaces have enabled enforcement, verified scope, and a successful positive test → `Clean`; configuration inventory alone is not sufficient.
- Any `Missing` without a referenced compensating control → `Anomaly`.

**Evidence.** `surface-coverage-<UTC>.json` listing all 13 surfaces with `Status`, `RuleCount`, `WspReference`.

#### T-SURFACE-02 — On-prem repository IP scanner coverage

Verify Purview Information Protection scanner is deployed against every on-prem file share that feeds M365 Search or Copilot grounding. `Status = Clean` only when scanner inventory matches WSP-listed in-scope shares. Inspect scanner content-scan jobs/repositories and published labels with automatic classification conditions; service-side auto-labeling policies are not scanner configuration. See [Deploy the scanner](https://learn.microsoft.com/en-us/purview/deploy-scanner).

---

### Namespace: POLICY — DLP policy shape

#### T-POLICY-01 — Same-rule SIT+label restriction

**Purpose.** Confirm no DLP rule scoped to the Copilot location combines `Content contains sensitive information types` AND `Content contains sensitivity labels` in a single rule (Microsoft restriction — must be two rules in the same policy).

**Procedure.**
1. `Connect-IPPSSession`.
2. Enumerate policies with `Get-DlpCompliancePolicy`; inspect `Locations` and policy-level `EnforcementPlanes` for Copilot scope.
3. Retrieve each policy's rules with `Get-DlpComplianceRule -Policy <policy-name>`. Inspect the complete exported conditions and the portal editor for both SIT and sensitivity-label conditions in one rule. A label can appear inside an `AdvancedRule` sensitive-information group with `type = Sensitivity`; do not infer condition types solely from top-level property names. Do not filter rules on a nonexistent `CopilotLocation` property or assume one JSON nesting layout.

**Status.** Any violating rule → `Anomaly`.

#### T-POLICY-02 — Custom-template inventory

Confirm Copilot block-by-label rules use the GA "Custom" template (not legacy templates that lack Copilot location support). Inventory all DLP policy templates and flag any policy targeting Copilot that uses a non-Custom template.

#### T-POLICY-03 — License entitlement coverage

For every DLP policy, confirm the benefiting users have the entitlement for that capability. Missing entitlement → `Anomaly`; do not infer either enforcement or non-enforcement solely from licensing state.

---

### Namespace: LABEL — Sensitivity label taxonomy

#### T-LABEL-01 — Label publication and assignment

Confirm the published label policy reaches all users in scope. Export `Get-Label` and `Get-LabelPolicy` in full; inspect label IDs, policy settings, user/group scope, and a target user's client. Policy existence alone does not prove publication has reached that user.

#### T-LABEL-02 — Container-vs-file boundary

Confirm the intended container and item scopes. One sensitivity label can legitimately cover both files and containers, but items do not inherit the container label. Verify the label on the file itself. See [container label boundaries](https://learn.microsoft.com/en-us/purview/sensitivity-labels-teams-groups-sites).

#### T-LABEL-03 — Copilot grounding label presence

Confirm the source item carries a label selected by an enabled Copilot-location DLP rule with **Prevent Copilot from processing content**. Encryption is not required for this label-based DLP action. Separately test encrypted-content access: Copilot requires both `VIEW` and `EXTRACT` usage rights. Do not treat an encryption configuration property as proof of a DLP match. See [Copilot DLP](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about) and [AI information protection](https://learn.microsoft.com/en-us/purview/ai-microsoft-purview).

#### T-LABEL-04 — API↔portal label normalization (Power Platform)

Confirm `Get-DlpPolicy` returned labels match portal display: `Confidential`→`Business`, `General`→`Non-Business`, `Blocked`→`Blocked`. Use `ConvertTo-FsiUiLabel` from [`powershell-setup.md`](./powershell-setup.md). Mismatch → `Error` (telemetry correctness issue, not a policy issue).

For connector endpoint filtering, export the separate connector configurations and test a static allowed and denied URL. Record environment-variable/custom-input/dynamically bound endpoints as a documented limitation, not as protected runtime paths. The **Get web resource** action of HTTP with Microsoft Entra ID is also outside this filter's scope. See [endpoint filtering limitations](https://learn.microsoft.com/en-us/power-platform/admin/connector-endpoint-filtering).

---


### Namespace: SYNTH — Synthetic-leak tests per surface

> **Reminder:** synthetic data only. Keep classifier-test evidence for each positive sample and a negative control. Reserved card numbers can be intentionally excluded by the built-in SIT. If only a custom canary SIT can be tested safely, record that this validates routing/enforcement, not the built-in classifier. Do not pull from production data sources.

#### T-SYNTH-01 — SharePoint upload synthetic CC

Upload a `.docx` containing a classifier-validated synthetic sample meeting the configured count/confidence to a SharePoint library in scope. Expected: configured DLP action and, where enabled, policy tip/alert and a corresponding `ComplianceDLPSharePoint` event. Retain the unchanged sample and a negative control.

#### T-SYNTH-02 — Exchange outbound synthetic SSN

Send a classifier-validated synthetic sample from a scoped mailbox to a firm-controlled external test mailbox. Expected: `ComplianceDLPExchange` match and the configured DLP restriction; do not assume quarantine is the generic DLP action. Confirm both sender and recipient outcomes.

#### T-SYNTH-03 — Endpoint clipboard synthetic data

On a supported, onboarded endpoint, use a classifier-validated synthetic file and the actual configured activity. Test **Copy to clipboard** and **Access by restricted apps** separately; do not assume a generic paste-to-any-app action. Confirm the expected block and corresponding `DLPEndpoint` activity for the supported OS/app. See [Endpoint DLP](https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about) and [device activity examples](https://learn.microsoft.com/en-us/purview/dlp-adaptive-protection-learn).

#### T-SYNTH-04 — Teams chat synthetic data

Test chat and channel messages separately with a classifier-validated synthetic sample. Include private channels where in scope and verify the policy's supported group scope. Expected: sender policy tip/blocked-message notification and recipient blocked-message placeholder for a block rule. Shared-channel evaluation follows each sender's home tenant; external-access chat has different hosting-tenant rules. See [Teams DLP](https://learn.microsoft.com/en-us/purview/dlp-microsoft-teams).

#### T-SYNTH-05 — Copilot prompt synthetic SIT (block-by-SIT-prompt, preview)

In Copilot Chat, submit a prompt containing synthetic CC content. Expected (preview): block by SIT-prompt rule. `Status = Pending` within 4-hour propagation window.

#### T-SYNTH-06 — Copilot grounding on labelled file (block-by-label, GA)

Use a labeled test file that the user can normally access and that matches an enforced Copilot DLP label rule. Verify its unique canary content is not used in the response; the item may still appear in citations. Repeat with the label/rule condition absent in an isolated test scope as a positive grounding control. Test missing `VIEW`/`EXTRACT` separately as an authorization control, not as proof of DLP suppression. Correlate DLP activity with the test; do not require a SharePoint audit record for Copilot suppression.

#### T-SYNTH-07 — Power Platform connector synthetic data flow

Build a test flow that crosses the Business / Non-Business connector boundary with synthetic data. Expected: flow blocked at design-time per `Get-DlpPolicy` configuration.

#### T-SYNTH-08 — Defender for Cloud Apps synthetic file

Upload a classifier-validated synthetic file to a supported connected app covered by a legacy file policy. Verify scan/match and configured governance action without assuming a 24-hour completion bound. Record migration to Purview before the [January 6, 2027 retirement](https://learn.microsoft.com/en-us/defender-cloud-apps/data-protection-policies).

> **Important:** SYNTH tests do not exhaustively prove DLP catches all NPI variants. They prove that the configured rule path produces the expected enforcement and audit signal for a known-good positive sample.

---

### Namespace: COPILOT — Copilot-specific tests

#### T-COPILOT-01 — Block-by-label (GA) end-to-end

An authorized user requests content from a labeled file selected by the enforced DLP rule. Verify content exclusion even though direct file access is allowed; citations may remain. Do not require encryption or missing `EXTRACT` rights, which would test a different control. For Word/Excel/PowerPoint, reopen the file after changing its label because policy evaluation occurs at file open. Correlate the test with DLP activity/alerts rather than asserting `ComplianceDLPSharePoint` records Copilot suppression.

#### T-COPILOT-02 — Block-by-SIT-prompt (preview) end-to-end

User submits classifier-validated synthetic SIT text. With **Processing prompts**, expect no answer and no internal/web search for that prompt. Test **Performing Web Searches** independently: web search is restricted but an internally grounded answer remains possible. Record tenant rollout and client messaging; preview block messaging in Word/Excel/PowerPoint can be unclear. Where configured, test the compliance URL; it changes only the help link, not the standard block message. See [Copilot DLP behavior](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about).

#### T-COPILOT-03 — Copilot Studio agent grounding source DLP coverage

For each published Copilot Studio agent, enumerate knowledge sources and connectors. Verify the applicable Power Platform data policy and resource exemptions, plus source permissions. Purview file DLP and Power Platform connector governance are not interchangeable; connector classification does not inspect every returned value for SITs. Test prohibited connector combinations and a permitted control path. See [Copilot Studio data policies](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention).

#### T-COPILOT-04 — Calendar invite and direct-prompt-upload exclusions

Document (do not test) the known unsupported scenarios per the Control 1.5 spec: Copilot DLP location does NOT scan calendar invites, and files uploaded directly into a prompt are NOT scanned. `Status = NotApplicable` with a Notes pointer to the WSP compensating control.

---

### Namespace: OVERRIDE — Override telemetry chain

#### T-OVERRIDE-01 — End-to-end override chain

**Purpose.** Confirm a user-initiated DLP override with required justification produces audit (Control 1.7) → Sentinel (Control 3.9) → supervisor queue (Control 2.12).

**Procedure.**
1. Configure a low-risk test rule with policy-tip override allowed and required justification.
2. Test user triggers a synthetic match (T-SYNTH-01 variant) and overrides with a unique justification marker. Retain the confirmed trigger UTC, marker, user/file/policy identifiers, and firm-approved observation deadline unchanged across reruns; see [Control 1.7 CAP-06](../1.7/verification-testing.md#cap-06-dlp-override-justification-reaches-audit-control-15-cross-link).
3. After allowing for audit ingestion and the firm's integration latency, verify:
   - For SharePoint/OneDrive overrides, UAL has a `DlpRuleUndo` event with `ExceptionInfo.Reason = Override` and the retained marker in `ExceptionInfo.Justification`. Decode `AuditData`, then deserialize `ExceptionInfo` when it is a JSON string; do not assume it is already a nested object.
   - The configured Sentinel ingestion path contains that same event. Do not assume the Office 365 connector imports the separate `DLP.All` feed into `OfficeActivity`.
   - The firm's explicitly configured supervisor workflow (per Control 2.12) shows a queued review item linking to the event; Communication Compliance is not an automatic DLP override queue.
4. Capture screenshots / API responses as evidence.

**Status.** Any broken link in the chain → `Anomaly`. Absence before the retained observation deadline is `Pending`; at/after that deadline it is `Anomaly`, not perpetually `Pending`. Also apply the two-consecutive-run escalation in Section 6. A failed query, incomplete query window, malformed payload, or unconfirmed trigger is `Error` requiring investigation, not evidence that a known emitted event was lost. These are local escalation rules, not a Microsoft ingestion SLA.

#### T-OVERRIDE-02 — Override telemetry sweep

For a SharePoint/OneDrive override, use `Search-UnifiedAuditLog -StartDate <start-utc> -EndDate <end-utc> -RecordType ComplianceDLPSharePoint -Operations DlpRuleUndo -ResultSize 5000`, parse `AuditData`, deserialize `ExceptionInfo` if it is a JSON string, and inspect its reason/justification. `-RecordType` accepts one value, not a comma-separated list. Search other workload-specific override schemas separately; use paging/time slices for result completeness, not a single 5,000-row count. See [cmdlet reference](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog) and [DLP schema](https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema). Spot-check 5 randomly-sampled override events for justification text quality. Empty / boilerplate justifications → `Anomaly` and route to supervisor.

---

### Namespace: AUDIT — Audit pipeline integrity

#### T-AUDIT-01 — RecordType counts

Compare a fixed set of known test event IDs, policy/rule IDs, users, workloads, and UTC windows between Activity Explorer and the configured audit export. Allow ingestion delay, deduplicate, and account for distinct event semantics before comparing counts. A raw count difference does not prove event loss. Divergence > 5% after reconciliation → `Anomaly` (audit pipeline gap → cross-link Control 1.7).

| Surface | RecordType |
|---|---|
| SharePoint / OneDrive | `ComplianceDLPSharePoint` |
| Exchange | `ComplianceDLPExchange` |
| Endpoint | `DLPEndpoint` |
| Teams | Files use their SharePoint/OneDrive storage workload; identify message DLP events by their actual exported workload/schema, not an assumed Exchange record type |
| Copilot | Correlate DLP policy-match activity separately from `CopilotInteraction`; neither an interaction record nor a SharePoint file event alone proves a Copilot DLP block |

#### T-AUDIT-02 — UAL ingestion lag

Generate and timestamp a known test event, then measure time until it becomes searchable. Core-service audit records typically appear in 60–90 minutes, but there is no Microsoft maximum-latency commitment. The firm may investigate after 24 hours as an operational threshold; absence of unrelated recent DLP activity is not proof of an outage.

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
  rollup/
    summary-<UTC>.json               # operator-generated rollup; not a supplied collector
  attestation/
    attestation.sponsor.json
    attestation.owner.json
    attestation.compliance.json
```

`manifest.sha256` covers the evidence files, excluding itself and later signatures; record file paths and digests in a deterministic order. The three attestation signatures sign the chain per Section 1 and are stored alongside it. The whole directory is sealed to WORM storage (Azure Blob immutable storage with a legal hold or a locked time-based immutability policy; versioning alone is not WORM) for **7 years** (SEC Rule 17a-4).

Verify the actual container/version immutability policy and retain its configuration export. See [Azure Blob immutable storage](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview). This documentation review does not validate any evidence archive, signature, or retention deployment.

---

## Section 9 — Quarterly Examiner-Style Audit

Internal Audit performs a seeded sampling pass each quarter:

1. Random sample 10 DLP rules across SharePoint, Exchange, Teams, Endpoint, Copilot.
2. Walk each rule from portal definition → PowerShell export → UAL hit history → supervisor queue (where overrides exist).
3. Sample 5 override events from the cycle; confirm justification adequacy and supervisor closure.
4. Sample 3 preview-feature surfaces; confirm documented compensating controls where features are unavailable.
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
- Re-run the SURFACE namespace within the propagation window + 24 hours after every license or role change.
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

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (Microsoft Learn verified 2026-10-16; tenant UI and screenshots not tested)*
