# Control 1.12 — Verification & Testing: Insider Risk Management

> Verification procedures for [Control 1.12 — Insider Risk Detection and Response](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md). Run each test on the cadence in §1, capture evidence per §6, and complete the attestation in §7 each cycle.
>
> **Scope of this playbook:** Microsoft Purview Insider Risk Management (IRM) — the six IRM role groups (Admins, Analysts, Investigators, Auditors, Approvers, and the catch-all Insider Risk Management group), Risky Agents (default-applied policy targeting Microsoft 365 Copilot agents, Copilot Studio agents, and Microsoft Foundry agents), Risky AI usage and Risky browser usage (browser-extension-dependent), Adaptive Protection, Forensic Evidence (opt-in, dual-authorization, 120-day clip auto-delete, PAYG-billed), HR / Microsoft Defender for Endpoint / Microsoft Defender for Cloud Apps connectors, pseudonymization, priority user groups, the analytics scan, the case escalation path to eDiscovery (Premium), and the unified audit footprint of IRM admin and investigator actions. **Out of scope here:** SEC 17a-4 / FINRA 4511 records retention of source artifacts (verified under [Control 1.9](../1.9/verification-testing.md)) and unified audit retention horizons (verified under [Control 1.7](../1.7/verification-testing.md)). IRM is a **detection and investigation surface, not a books-and-records retention plane** — see §8 anti-pattern.
>
> **Audience:** M365 administrator at a US financial services organization producing audit-defensible evidence for FINRA Rule 3110 / 25-07, FINRA Rule 4511, SEC Rule 17a-4, GLBA 501(b), SOX 404, OCC 2011-12 / Fed SR 11-7, and NYDFS 23 NYCRR 500 examiners.
>
> **Sovereign clouds:** Commercial · GCC · GCC High · DoD — see §5 for variants. **Important:** Insider Risk Management — and in particular Adaptive Protection, Risky AI usage, Risky Agents, and Forensic Evidence — has limited or non-parity availability in US Government cloud programs per Microsoft Learn. Verify each capability before claiming pass/fail on a sovereign tenant; record signed exceptions where N/A.
>
> **Cross-links:** [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Troubleshooting](troubleshooting.md) · [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md).
>
> **Last UI Verified:** April 2026.

---

## What this verification catches

This catalog is designed to surface the carry-forward defect classes that the AI Council review identified for Insider Risk Management:

- **Silent-failure if Unified Audit Log is off.** IRM policies and analytics scans depend on UAL ingestion. With UAL disabled, every IRM policy (including the default-applied Risky Agents) produces zero signal and zero `InsiderRiskMgmt*` audit rows — and the dashboard appears "clean."
- **Test-mode trap.** Policies created in **Test mode** (per Microsoft Learn: *"policy will be created in test mode and not generate alerts"*) generate **no alerts** by design. A test policy left in Test mode after go-live is the most common silent regression in IRM.
- **Missing browser extension producing zero Risky AI signal.** Risky AI usage and Risky browser usage require the Microsoft Insider risk extension (Edge) or Microsoft Purview extension (Chrome) on a Windows-onboarded device. Without it, the policy is enabled-but-silent for browser-derived signals.
- **Approver = Investigator separation-of-duties violation.** The Forensic Evidence dual-authorization model collapses when the same identity is in both the Investigators and Approvers role groups.
- **HR connector field-mapping gap.** Departing-user, priority-user, and risky-user variants depend on the HR connector mapping `EmployeeID`, `ResignationDate`, and `LastWorkingDate`. A missing or misnamed field silently disables the departing-user signal.
- **Forensic Evidence 120-day clip expiry data loss.** Captured clips auto-delete 120 days after capture. Treating IRM as records retention causes loss of evidence required by an active investigation, eDiscovery hold, or examiner request.
- **Adaptive Protection in a US Government cloud mistakenly attested.** Adaptive Protection is documented as having limited availability in GCC / GCC High / DoD. Sampling a "pass" without reading the current Learn caveat creates an examiner-facing misstatement.
- **Pseudonymization unmask without role + reason audit trail.** Re-identifying a user inside IRM is an Investigator-only action that must produce an audit row; an unmask outside the role-and-reason flow is a privacy and compliance defect.
- **Confusing Risky Agents (default-applied) with Risky AI usage (template-created).** They are different policies with different prerequisites and different audit footprints. Treating one as evidence of the other produces a coverage gap.
- **Mistaking Triage Agent recommendations for human supervision under FINRA 25-07.** The Triage Agent is decision support; FINRA 25-07 expects supervision of the AI agent itself. Attesting Triage Agent prioritization as the supervisory act conflates the model with the supervisor.

Each test below maps explicitly to the failure mode it detects and is reproducible by named test user(s), UTC timestamp, exact policy name and (where assigned) `PolicyId`, and expected unified-audit `InsiderRiskMgmt*` operation rows.

---

## 1. Re-Verification Cadence

IRM signals are **non-static**. Microsoft ships analytics-model updates, policy templates evolve (Risky Agents was added by-default; Risky browser usage is in preview at multiple points in 2025–2026), Adaptive Protection thresholds are tunable, and Forensic Evidence's 120-day auto-delete creates a ticking-clock evidence horizon. Each test runs on its own cadence rather than a single annual binder refresh, aligned to OCC 2011-12 / Federal Reserve SR 11-7 ongoing-monitoring expectations for model-driven supervisory systems.

| Test ID | Frequency | Owner role | Evidence retention | Regulatory driver |
|---|---|---|---|---|
| 1.12-LIC-01 | Monthly | Entra Global Admin (read) + Purview Compliance Admin | 7 years (broker-dealer) / 6 years (other FSI) | FINRA 4511, GLBA 501(b) |
| 1.12-UAL-01 | Weekly | Purview Audit Admin | 7 years | FINRA 4511, SEC 17a-4(f) |
| 1.12-ROLE-01 | Quarterly | Entra Global Admin + Purview Compliance Admin | 7 years | FINRA 3110 (separation of duties), SOX 404 |
| 1.12-PSEUD-01 | Quarterly | Purview Compliance Admin + Privacy Officer | 7 years | GLBA 501(b), SEC Reg S-P |
| 1.12-AU-01 | Quarterly | Entra Global Admin + Purview Compliance Admin | 7 years | FINRA 3110 (supervisory scope) |
| 1.12-HR-01 | Monthly | HR Connector owner + Purview Compliance Admin | 7 years | FINRA 3110 (departing-user supervision) |
| 1.12-HR-02 | Quarterly | HR Connector owner | 7 years | FINRA 3110, GLBA 501(b) |
| 1.12-DLP-01 | Monthly | Purview Compliance Admin (DLP) | 7 years | GLBA 501(b), SEC Reg S-P |
| 1.12-MDE-01 | Monthly | MDE Admin + Purview Compliance Admin | 7 years | FFIEC, OCC 2013-29 (third-party / endpoint risk) |
| 1.12-DCA-01 | Quarterly | MDA Admin + Purview Compliance Admin | 7 years | FINRA 4511, GLBA 501(b) |
| 1.12-RAI-01 | Monthly (preview-status review) | Purview Compliance Admin + AI Governance Lead | 7 years | FINRA 25-07, OCC 2011-12 / Fed SR 11-7 |
| 1.12-RAG-01 | Monthly | Purview Compliance Admin + AI Governance Lead | 7 years | FINRA 25-07, OCC 2011-12 / Fed SR 11-7 |
| 1.12-RBR-01 | Monthly (preview — verify lifecycle on Learn) | Purview Compliance Admin | 7 years | FINRA 3110 |
| 1.12-FE-01 | Quarterly | IRM Investigator + IRM Approver + Privacy Officer | 7 years (or per legal hold) | FINRA 4511, SEC 17a-4(b) |
| 1.12-FE-02 | Quarterly (clock-driven; track every capture's day-90 / day-110) | IRM Investigator + eDiscovery Manager (Premium) | Per legal hold | SEC 17a-4(b), FINRA 4511 |
| 1.12-AP-01 | Quarterly (Commercial); **N/A in US Gov clouds — record exception** | Purview Compliance Admin + DLP Admin + Conditional Access Admin | 7 years | OCC 2011-12, GLBA 501(b) |
| 1.12-CASE-01 | Quarterly | IRM Analyst + IRM Investigator | 7 years | FINRA 3110, SEC 17a-4(b) |
| 1.12-EDISC-01 | Quarterly | eDiscovery Manager (Premium) | 7 years (or per legal hold) | FINRA 4511, SEC 17a-4(b)/(f) |
| 1.12-AUDIT-01 | Weekly | Purview Audit Admin + IRM Auditor | 7 years | FINRA 4511, SEC 17a-4(f) |
| 1.12-NEG-01 | Quarterly | Purview Compliance Admin | 7 years | FINRA 3110 (scope clarity) |
| 1.12-NEG-02 | Quarterly | Purview Compliance Admin | 7 years | FINRA 3110 (test-mode trap) |
| 1.12-NEG-03 | Quarterly | IRM Auditor + Privacy Officer | 7 years | GLBA 501(b), SEC Reg S-P |
| **On-change** | After any policy create / enable / disable / scope change, role-group change, indicator toggle, AU re-scoping, Adaptive Protection threshold change, HR / MDE / MDA connector schema change, or browser-extension policy change | Change requester | Per change ticket | FINRA 4511 |
| **On-incident** | Preserve full evidence, freeze the policy, capture role-group exports, capture the relevant `InsiderRiskMgmt*` audit slice, and **for Forensic Evidence: export any captured clip well before the 120-day auto-delete** | Incident commander | Per legal hold | NYDFS 500.17 (72-hour clock — see FSI Incident Handling) |

> **All evidence files must carry a UTC timestamp.** Local-time evidence is rejected at audit. Use `Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mm:ssZ'` and embed the result in both the file name and the file body.

> **Firm-defined cadences only.** Microsoft Learn does not publish IRM investigation, alert-response, or triage SLAs. Where this catalog references review or response targets, those are firm-defined supervisory commitments per the firm's Written Supervisory Procedures (WSP) — they are **not** Microsoft-stated ceilings. The only Microsoft-published processing window cited in §3 is the **analytics scan up to 48 hours**.

---

## 2. Pre-flight

Run these checks before any test in §4. A failure here invalidates the entire cycle.

### 2.1 License entitlement and PAYG

IRM core requires Microsoft 365 E5, Microsoft 365 E5 Compliance, Microsoft 365 E5 Insider Risk Management, or the Microsoft Purview Suite per-user SKU for every in-scope identity. **Forensic Evidence** additionally requires **pay-as-you-go (PAYG)** billing on a connected Azure subscription with a Microsoft-specified storage trial allowance (verify the current trial size on Microsoft Learn `insider-risk-management-forensic-evidence` at deployment time). The **Risky AI usage** template's coverage of non-M365 AI surfaces depends on Microsoft 365 Copilot pay-as-you-go meter parity — verify the same way for the surfaces you intend to monitor. Capture a tenant-level entitlement snapshot:

```powershell
Connect-MgGraph -Scopes 'Directory.Read.All','User.Read.All'
$irmSkus = @('SPE_E5','M365_E5_COMPLIANCE','M365_E5_INSIDER_RISK_MANAGEMENT','INFORMATION_PROTECTION_COMPLIANCE')
$inScope = Import-Csv .\InScopeUsers.csv
$gaps = foreach ($u in $inScope) {
  $skus = (Get-MgUserLicenseDetail -UserId $u.UserPrincipalName).SkuPartNumber
  if (-not ($skus | Where-Object { $irmSkus -contains $_ })) {
    [pscustomobject]@{ Upn=$u.UserPrincipalName; Skus=($skus -join ';') }
  }
}
$gaps | Export-Csv .\1.12-LIC-pre.csv -NoTypeInformation
```

The PAYG attestation is a tenant-level artifact (Azure subscription ID, meter resource ID, billing-admin attestation reference, date verified against Learn). It is required if any of the following are in scope this cycle: `1.12-FE-01`, `1.12-FE-02`, `1.12-RAI-01` (where non-M365 AI surfaces are enabled).

### 2.2 Unified Audit Log enabled

```powershell
Connect-ExchangeOnline -ShowBanner:$false
(Get-AdminAuditLogConfig).UnifiedAuditLogIngestionEnabled  # must be True
```

If `False`, no `InsiderRiskMgmt*` audit operations are recorded — every IRM policy (including the default-applied **Risky Agents**) is silently signal-less, no admin / investigator action is visible in audit, and no test in §4 can produce defensible evidence. Remediate via [Control 1.7](../1.7/verification-testing.md) first. This is the single most common silent-failure mode in IRM.

### 2.3 Modules pinned

Per the [PowerShell Authoring Baseline §1](../../_shared/powershell-baseline.md), pin module versions and record them in the cycle's tester log:

```powershell
Install-Module -Name ExchangeOnlineManagement -RequiredVersion '<approved-version>' `
    -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name Microsoft.Graph -RequiredVersion '<approved-version>' `
    -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
```

> **Mutation surface.** Microsoft Learn does not publish a complete PowerShell surface for IRM policy authoring; primary policy create / edit operations are performed in the Microsoft Purview portal. PowerShell is used in this catalog for read-side inventory (role-group membership, audit search, license entitlement, eDiscovery case creation via `New-ComplianceCase -CaseType InsiderRisk`). Where a step is portal-only, the test specifies the exact portal navigation and screenshot evidence.

### 2.4 Six IRM role groups assigned with separation of duties

IRM defines **six** role groups in Microsoft Purview (per Learn `insider-risk-management-permissions`). Verify membership and separation of duties before the cycle:

| Role group | Purpose | Separation-of-duties rule |
|---|---|---|
| `Insider Risk Management` | Catch-all (all IRM permissions) | **Avoid in regulated FSI tenants.** Empty-or-near-empty preferred; prefer the segmented groups below. Any membership requires an exception ticket. |
| `Insider Risk Management Admins` | Configure policies, settings, role groups, priority user groups, priority content | Compliance / IRM admin function. **Must not** be in `Auditors`. |
| `Insider Risk Management Analysts` | Triage and review alerts (no file/email content visibility) | Tier-1 supervisory analyst. |
| `Insider Risk Management Investigators` | Investigate cases, view content (subject to pseudonymization), submit Forensic Evidence capture requests | Tier-2 investigator. **Must not** be in `Approvers` (dual-auth). **Must not** be in `Auditors`. |
| `Insider Risk Management Auditors` | View IRM audit logs (admin actions, settings changes, unmask events) | Independent assurance / Internal Audit. **Must not** be in `Admins` or `Investigators`. |
| `Insider Risk Management Approvers` | Approve Forensic Evidence capture requests (dual-authorization) | **Must be distinct** from `Investigators`. Assign to a separate Compliance / Privacy approver function. |

Verify with:

```powershell
$groups = @(
  'Insider Risk Management',
  'Insider Risk Management Admins',
  'Insider Risk Management Analysts',
  'Insider Risk Management Investigators',
  'Insider Risk Management Auditors',
  'Insider Risk Management Approvers'
)
$members = foreach ($g in $groups) {
  Get-RoleGroupMember -Identity $g | Select-Object @{n='RoleGroup';e={$g}}, Name, RecipientType
}
$members | Export-Csv .\1.12-ROLE-pre.csv -NoTypeInformation
```

Separation-of-duties violation report (must be empty):

```powershell
$inv = (Get-RoleGroupMember 'Insider Risk Management Investigators').Name
$apr = (Get-RoleGroupMember 'Insider Risk Management Approvers').Name
$adm = (Get-RoleGroupMember 'Insider Risk Management Admins').Name
$aud = (Get-RoleGroupMember 'Insider Risk Management Auditors').Name
$violations = @()
$violations += $inv | Where-Object { $apr -contains $_ } | ForEach-Object { "INV+APR: $_" }
$violations += $adm | Where-Object { $aud -contains $_ } | ForEach-Object { "ADM+AUD: $_" }
$violations += $inv | Where-Object { $aud -contains $_ } | ForEach-Object { "INV+AUD: $_" }
$violations | Set-Content .\1.12-ROLE-violations.txt
```

### 2.5 Connectors and signal sources

| Source | Purpose | Verification |
|---|---|---|
| Microsoft 365 HR connector | Departing-user / priority-user / risky-user variants | Last successful ingestion within firm-defined window; required fields populated: `UserPrincipalName`, `EmployeeID`, `ResignationDate`, `LastWorkingDate` |
| Microsoft Defender for Endpoint integration | Security-policy-violations templates | MDE → Microsoft Purview integration toggle ON; in-scope devices onboarded; sample MDE alert visible to IRM |
| Microsoft Defender for Cloud Apps connectors | Cloud-app coverage in *Data theft by departing users* | Connectors configured for the platforms in scope (Box, Dropbox, Google Drive, Amazon S3, Azure as applicable); status `Connected` |
| Browser extension (Edge / Chrome) | Risky AI usage, Risky browser usage, browser-derived indicators | **Edge:** Microsoft Insider risk extension or Microsoft Purview extension (per current Learn for the scenario). **Chrome:** Microsoft Purview extension. **Windows-only.** Deployed via Intune to in-scope devices; deployment report exported. Browsing indicators enabled in **Settings → Policy indicators → Browsing indicators** |
| Devices onboarded to Microsoft Purview | Required for Forensic Evidence and most browser/endpoint signals | Onboarding state visible in Microsoft Purview; sampled device returns activity within the analytics scan |
| DLP (high-severity incident reports) | Required when DLP is the trigger source for *Data leaks* templates | DLP policies configured per [Control 1.5](../1.5/verification-testing.md); incident-report severity mapping documented |

### 2.6 Sovereign-cloud parity check

Before any test, verify the target cloud's current parity for IRM, Adaptive Protection, Risky AI usage, Risky Agents, Risky browser usage, Forensic Evidence, and Triage Agent against current Microsoft Learn (`insider-risk-management`, `insider-risk-management-adaptive-protection`, `insider-risk-management-forensic-evidence`). Record:

- **Cloud** (Commercial / GCC / GCC High / DoD)
- **Per-capability availability** (GA / Preview / N/A) with the Learn URL and date verified
- **Signed exception** for any capability marked N/A in the target cloud — the corresponding test in §4 is then marked **N/A — Exception #_____** and not run

`1.12-AP-01` is **N/A in US Government clouds at parity** per Learn — record an exception and apply compensating controls (Communication Compliance, Audit, DLP, Defender for Cloud Apps, Sentinel UEBA).

### 2.7 Test users, test policies, and seed activities

Provision the following named test identities in a non-production OU (Zone 1 or quarantined Zone 2 segment). All seed activities are deterministic and reproducible.

| Test identity | Purpose | License | Notes |
|---|---|---|---|
| `irm-test-rep-01@<tenant>` | In-scope FINRA-supervised registered representative | M365 E5 + Copilot | Used for Risky AI usage, Data leaks, Risky Agents seed |
| `irm-test-rep-02@<tenant>` | Second user for two-party tests; toggled "departing" via HR connector | M365 E5 | Used for HR / Departing-user seed |
| `irm-test-out-01@<tenant>` | **Out-of-scope** identity for negative test 1.12-NEG-01 | M365 E5 (no IRM scope) | |
| `irm-test-inv-01@<tenant>` | IRM Investigator (Tier-2) | M365 E5 | Member of Investigators only |
| `irm-test-apr-01@<tenant>` | IRM Approver (Forensic Evidence dual-auth) | M365 E5 | Member of Approvers only — **distinct from Investigators** |
| `irm-test-aud-01@<tenant>` | IRM Auditor (independent assurance) | M365 E5 | Member of Auditors only |

| Test policy / artifact | Template | Status | In-scope users | Notes |
|---|---|---|---|---|
| `1.12-TEST-Departing` | Data theft by departing users | Active | `irm-test-rep-02` | Requires HR connector with `ResignationDate` set in past 30 days |
| `1.12-TEST-Leaks` | Data leaks | Active | `irm-test-rep-01` | DLP-trigger variant; high-severity incident report mapping |
| `1.12-TEST-RiskyAI` | Risky AI usage | Active | `irm-test-rep-01` | Browser extension on Windows test device; browsing indicators ON |
| `1.12-TEST-FE` | Forensic Evidence (paired) | Active | `irm-test-rep-01` | Pairs with the Risky AI usage policy; dual-auth required |
| `1.12-TEST-Mode` | Data leaks | **Test mode** | `irm-test-rep-01` | Negative test 1.12-NEG-02 (must produce ZERO alerts) |
| Risky Agents (default) | Risky Agents | Default-applied (not created via wizard) | Tenant-wide | Verify default policy exists; do not attempt to delete |

> **Seed activity inventory.** Each test below names the deterministic seed (e.g., a download to USB, a Copilot prompt with a flagged pattern, a SharePoint external share). Bodies and file payloads are SHA-256-hashed; embed the hash in the tester log so the seed itself is reproducible.

---

## 3. Documented processing windows

Per Microsoft Learn (`insider-risk-management-settings`, `insider-risk-management-policies`):

| Pipeline stage | Documented ceiling | Notes |
|---|---|---|
| Initial analytics scan | Up to **48 hours** | De-identified scan of activity to surface tenant-wide insights; required before some templates produce signal |
| Policy ingestion / activity-to-alert | **Not published as an SLA** | Microsoft Learn does not publish a single end-to-end alert latency. Latency depends on signal source (HR connector cadence, MDE alert pipeline, MDA connector cadence, browser extension reporting, Defender for Cloud Apps polling) |
| HR connector ingestion | Per scheduled job (firm-defined) | Connector job cadence is configured by the customer |
| Forensic Evidence clip retention | **120 days** auto-delete from capture date | Hard ceiling; export to long-term store before expiry |
| Role-group membership propagation | Approximately **30 minutes** (per Learn) | Affects all tests that depend on a fresh role-group change |

**Pass criteria for every test below measure the *observed* tenant behavior against the ceilings above where one is published, and against a firm-defined supervisory window otherwise.** Do not write "within SLA" against a Microsoft window that does not exist. Do write: "observed alert at `<UTC>`, within firm-defined supervisory window of `<N>` hours per WSP §___." A test that runs and concludes inside a documented window without observing the asserted signal is **inconclusive**, not a failing or passing result — re-run after the window expires.

---

## 4. Test Catalog

Each test is deterministic: a named test user, a known input, and an asserted output measured against a Microsoft-documented signal (cmdlet output, audit `Operation` name under the `InsiderRiskMgmt*` prefix, portal alert / case entry).

> **Audit-operation naming.** Microsoft Learn `audit-log-activities` documents IRM operations under the `InsiderRiskMgmt*` prefix (examples include `InsiderRiskMgmtAlertUpdated`, `InsiderRiskMgmtCaseCreated`, `InsiderRiskMgmtPolicyCreated`, `InsiderRiskMgmtPolicyUpdated`, `InsiderRiskMgmtPolicyDeleted`). **Verify the exact spelling and current set of operations on Microsoft Learn at write time** — Microsoft adds and renames operations periodically. The operations cited in each test are illustrative of the prefix and the audit assertion shape, not a closed list.

### 1.12-LIC-01 — License entitlement and PAYG attestation per tenant

**Objective.** Confirm every user in scope of any IRM policy carries an SKU that licenses IRM, and that the Forensic Evidence PAYG meter is enabled where Forensic Evidence is in scope this cycle.

**Preconditions.** Microsoft Graph PowerShell SDK installed; `Directory.Read.All`, `User.Read.All` granted; the in-scope user list exported to `InScopeUsers.csv`. Forensic Evidence in-scope flag and any Risky AI usage non-M365 surface flag recorded for the cycle.

**Steps.**

1. Record `T0 = Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mm:ssZ'`.
2. Run the entitlement snapshot script in §2.1.
3. If Forensic Evidence is in scope: capture the PAYG attestation file (Azure subscription ID, meter resource ID, billing-admin attestation reference, Learn URL, date verified).
4. If Risky AI usage non-M365 surfaces are in scope: capture the corresponding Copilot PAYG attestation reference (paired with [Control 1.10](../1.10/verification-testing.md) §2.1 if already produced this cycle).

**Expected result.** `1.12-LIC-pre.csv` contains zero rows. PAYG attestation files exist where required and are dated within the firm-defined attestation refresh window (typically 30 days).

**Pass criteria (binary).** Zero entitlement gaps AND PAYG attestations present where required. Any non-zero gap is a fail (under-licensed users do not produce IRM signal — silent under-coverage).

**Audit assertion.** None at this stage (license check is a pre-condition, not an IRM operation).

**Evidence collected.** `1.12-LIC-01-<TENANT>-<UTC>-gaps.csv` (header row even if empty), `1.12-LIC-01-<TENANT>-<UTC>-payg.json` (where applicable), transcript, tester log. SHA-256 sidecar per file.

---

### 1.12-UAL-01 — Unified Audit Log enabled and InsiderRiskMgmt operations are flowing

**Objective.** Confirm UAL ingestion is enabled and that recent IRM admin or policy activity has produced `InsiderRiskMgmt*` audit rows.

**Preconditions.** Exchange Online connection; Purview Audit Admin role; at least one IRM admin action (e.g., a policy edit or role-group membership change) performed by a known admin in the last 7 days, OR a deterministic seed action performed during this test.

**Steps.**

1. Record `T0` UTC.
2. ```powershell
   (Get-AdminAuditLogConfig).UnifiedAuditLogIngestionEnabled  # must be True
   ```
3. Trigger a deterministic seed: as `irm-test-aud-01` (or a designated change requester), make a no-op edit to `1.12-TEST-Leaks` in the Purview portal (e.g., toggle a comment field) — this should emit an `InsiderRiskMgmtPolicyUpdated`-class event. Record `T1` UTC.
4. Wait for the documented audit ingestion floor (30 minutes) before searching.
5. Use a paged audit search to retrieve all IRM-prefixed operations in the window:
   ```powershell
   $sid = "1.12-UAL-01-$([guid]::NewGuid().ToString('N'))"
   $start = (Get-Date).AddHours(-24).ToUniversalTime()
   $end   = (Get-Date).ToUniversalTime()
   $rows = @()
   do {
     $page = Search-UnifiedAuditLog -StartDate $start -EndDate $end `
       -SessionId $sid -SessionCommand ReturnLargeSet -ResultSize 5000 `
       -Operations 'InsiderRiskMgmtPolicyUpdated','InsiderRiskMgmtPolicyCreated','InsiderRiskMgmtPolicyDeleted','InsiderRiskMgmtAlertUpdated','InsiderRiskMgmtCaseCreated'
     $rows += $page
   } while ($page.Count -gt 0)
   $rows | Export-Csv .\1.12-UAL-01-rows.csv -NoTypeInformation
   ```
6. Confirm at least one row corresponds to the seed in step 3.

**Expected result.** UAL is enabled. The seed action appears as an `InsiderRiskMgmtPolicyUpdated`-class row within the documented 30-minute audit ingestion floor (allow firm-defined buffer). Other IRM operations from the trailing 24 hours are present and consistent with known activity.

**Pass criteria (binary).** UAL enabled = True AND seed event observed in audit AND row counts match the change-ticket / activity log for the trailing 24-hour window.

**Audit assertion.** ≥ 1 row with `Operations` in the `InsiderRiskMgmt*` prefix and `UserIds` matching the seed actor.

**Evidence collected.** `1.12-UAL-01-<TENANT>-<UTC>-config.txt` (UAL state), `1.12-UAL-01-<TENANT>-<UTC>-rows.csv` (paged audit export), `1.12-UAL-01-<TENANT>-<UTC>-seed.json` (T1 + actor + change-ticket reference), transcript. SHA-256 sidecars.

---

### 1.12-ROLE-01 — Six IRM role groups assigned with separation of duties

**Objective.** Confirm all six IRM role groups exist, are populated to the firm's standard, and that no identity violates the separation-of-duties matrix in §2.4.

**Preconditions.** Exchange Online connection (Security & Compliance role-group cmdlets); Entra Global Admin (read) for cross-validation of nested groups.

**Steps.**

1. Record `T0` UTC.
2. Run the membership export script in §2.4.
3. Run the violation report script in §2.4.
4. For each role group, capture the assignment policy / approver flow (PIM eligibility, JIT activation duration, approval requirement) from the Microsoft Entra portal — screenshot with UTC clock visible.
5. Verify role-group propagation freshness: any membership change in the past 30 minutes should be flagged for re-test (per Learn ~30-min propagation).

**Expected result.** All six groups exist; `1.12-ROLE-violations.txt` is empty; `Insider Risk Management` (catch-all) has either zero members or only documented exception accounts; `Approvers` and `Investigators` share zero identities.

**Pass criteria (binary).** Six groups present AND violations file empty AND catch-all group within firm-defined limit AND PIM/approval evidence captured for each group.

**Audit assertion.** Any membership change in the prior 24 hours appears in audit under the `Add member to role` / `Remove member from role` operations (Entra) — not under `InsiderRiskMgmt*` (membership audit is in the directory, not in the IRM operation set).

**Evidence collected.** `1.12-ROLE-01-<TENANT>-<UTC>-members.csv`, `1.12-ROLE-01-<TENANT>-<UTC>-violations.txt`, six PIM screenshots, transcript. SHA-256 sidecars.

---

### 1.12-PSEUD-01 — Pseudonymization default-on; re-identification audit trail tested

**Objective.** Confirm that IRM displays usernames in pseudonymized form by default and that any re-identification ("show real name") is gated by Investigator role and produces an audit row.

**Preconditions.** `irm-test-inv-01` is in `Insider Risk Management Investigators` only. At least one alert exists for `irm-test-rep-01` in the IRM dashboard (e.g., from `1.12-RAI-01`).

**Steps.**

1. Record `T0` UTC.
2. As `irm-test-aud-01` (Auditor only — no Investigator role), open Microsoft Purview → Insider Risk Management → Alerts. Capture screenshot — names must be pseudonymized.
3. As `irm-test-inv-01`, open the same alert. Confirm pseudonymized display by default.
4. As `irm-test-inv-01`, perform the re-identification action (Show real name) on the alert. Record `T1` UTC and the documented business reason.
5. Wait for audit ingestion floor (30 minutes), then search for the unmask row:
   ```powershell
   Search-UnifiedAuditLog -StartDate $T1.AddMinutes(-5) -EndDate $T1.AddHours(2) `
     -UserIds 'irm-test-inv-01@<tenant>' `
     -Operations 'InsiderRiskMgmtAlertUpdated' | Export-Csv .\1.12-PSEUD-01-unmask.csv -NoTypeInformation
   ```
   Verify at least one row whose payload reflects the unmask action (verify the exact property name on Learn — Microsoft documents the unmask as an Investigator activity under the alert-update operation set; confirm the spelling at write time).
6. Verify the pseudonymization tenant setting in **Insider Risk Management → Settings → Privacy** is **Show anonymized versions of usernames** (the default).

**Expected result.** Both Auditor and Investigator default views are pseudonymized; the unmask attempt by the Auditor (step 2) is not possible (or returns no real-name display); the Investigator unmask in step 4 succeeds and emits an audit row tied to the Investigator's UPN with a documented reason.

**Pass criteria (binary).** Default = anonymized AND Auditor cannot unmask AND Investigator unmask emits at least one audit row referencing the alert and Investigator UPN AND the Settings → Privacy state is "anonymized."

**Audit assertion.** ≥ 1 `InsiderRiskMgmtAlertUpdated`-class row with `UserIds = irm-test-inv-01@<tenant>` and a payload field indicating the unmask. Cross-reference the change ticket / business-reason field.

**Evidence collected.** Two portal screenshots (Auditor view, Investigator view), Settings → Privacy screenshot, `1.12-PSEUD-01-<TENANT>-<UTC>-unmask.csv`, signed business-reason record, transcript. SHA-256 sidecars.

---

### 1.12-AU-01 — Administrative-unit scoping for IRM admin / analyst / investigator

**Objective.** Confirm AU scoping (where supported on Learn for IRM at write time) limits the visibility of IRM admins / analysts / investigators to their assigned business unit (e.g., broker-dealer vs. RIA vs. bank).

**Preconditions.** At least two AUs configured (e.g., `AU-BD`, `AU-RIA`). Test users assigned to each AU. Verify on Learn at write time whether IRM honors AU scoping for the specific role groups in your cloud — record the verification date.

**Steps.**

1. Record `T0` UTC.
2. Capture AU membership: `Get-MgDirectoryAdministrativeUnitMember -AdministrativeUnitId <id>` for each AU, exported to CSV.
3. Configure (or verify) IRM admin/analyst/investigator role-group assignments scoped to each AU per the firm's design.
4. As an `AU-BD`-scoped Analyst, open IRM → Alerts. Capture screenshot — only `AU-BD` user alerts visible.
5. As an `AU-RIA`-scoped Analyst, open the same view. Capture screenshot — only `AU-RIA` user alerts visible.
6. As a tenant-wide Admin (no AU scoping), confirm both AUs are visible.

**Expected result.** Each AU-scoped role sees only its AU; tenant-wide role sees all.

**Pass criteria (binary).** AU scoping behaves per the firm's design AND no cross-AU leakage observed AND AU membership exports match the scoping intent.

**Audit assertion.** AU membership changes in the prior 24 hours appear in directory audit (`Add member to administrative unit` / `Remove member from administrative unit`).

**Evidence collected.** Three portal screenshots (per-AU + tenant-wide), AU membership CSV per AU, role-group export filtered to AU-scoped roles, transcript. SHA-256 sidecars.

---

### 1.12-HR-01 — HR connector ingestion + departing-user signal end-to-end

**Objective.** Confirm the Microsoft 365 HR connector is ingesting on schedule with the required field set and that a deterministic departing-user record produces a `Data theft by departing users` signal.

**Preconditions.** HR connector configured; `1.12-TEST-Departing` policy active; `irm-test-rep-02` flagged as departing in the most recent HR CSV with `ResignationDate = T0 - 7d` and `LastWorkingDate = T0 + 14d`.

**Steps.**

1. Record `T0` UTC.
2. Open Microsoft Purview → Data connectors → HR. Capture the last successful ingestion timestamp (must be within firm-defined cadence). Screenshot with UTC clock visible.
3. Verify required fields populated for `irm-test-rep-02`: `UserPrincipalName`, `EmployeeID`, `ResignationDate`, `LastWorkingDate`. Export the HR-connector status JSON / CSV from the portal.
4. As `irm-test-rep-02`, perform a deterministic seed: download a SharePoint file (file SHA-256 recorded) and copy to USB on a Windows-onboarded device (per Learn, USB copy is a Microsoft-defined indicator for this template).
5. Wait for the firm-defined supervisory observation window (recorded in WSP — Microsoft does not publish this latency).
6. As `irm-test-inv-01`, confirm an alert appears in IRM → Alerts referencing `irm-test-rep-02` and the seed activity. Capture screenshot.

**Expected result.** HR connector last-success within window; required fields populated; seed activity surfaces as an alert under the departing-users policy within the firm-defined window.

**Pass criteria (binary).** Connector status = healthy AND required fields populated AND alert observed (or marked **inconclusive** if the firm-defined window has not elapsed — re-run; do not pass).

**Audit assertion.** ≥ 1 `InsiderRiskMgmtAlertUpdated`-class row referencing the alert opened in step 6.

**Evidence collected.** HR connector status screenshot + JSON, HR CSV row for `irm-test-rep-02` (PII-redacted; hashed), alert screenshot, USB-event evidence (MDE timeline export), transcript. SHA-256 sidecars.

---

### 1.12-HR-02 — HR connector schema integrity (field mapping)

**Objective.** Confirm the HR connector CSV schema matches the IRM-required field set and that no field rename, blank value, or upstream HRIS schema drift has silently broken the departing-/priority-/risky-user signal.

**Preconditions.** Access to the most recent HR CSV uploaded to the connector and to the connector configuration.

**Steps.**

1. Record `T0` UTC.
2. Export the connector's expected schema from the portal (Microsoft Purview → Data connectors → HR → connector → Schema). Screenshot.
3. Compare against the most recent uploaded CSV header row:
   ```powershell
   $required = 'UserPrincipalName','EmployeeID','ResignationDate','LastWorkingDate'
   $hdr = (Get-Content .\hr-latest.csv -TotalCount 1).Split(',')
   $missing = $required | Where-Object { $_ -notin $hdr }
   $missing | Set-Content .\1.12-HR-02-missing.txt
   ```
4. Sample 25 random rows; count blanks in each required field:
   ```powershell
   Import-Csv .\hr-latest.csv |
     Get-Random -Count 25 |
     ForEach-Object {
       foreach ($f in $required) { if (-not $_.$f) { "$($_.UserPrincipalName) :: $f BLANK" } }
     } | Set-Content .\1.12-HR-02-blanks.txt
   ```

**Expected result.** Zero missing fields; blank-rate within firm-defined tolerance (typically zero blanks for `UserPrincipalName` and `EmployeeID`; `ResignationDate` / `LastWorkingDate` legitimately blank for non-departing users).

**Pass criteria (binary).** Missing-fields file empty AND `UserPrincipalName` / `EmployeeID` blank-count = 0 AND any blank in `ResignationDate` / `LastWorkingDate` corresponds to a non-departing user (verified against HRIS extract reference).

**Audit assertion.** None at this stage (schema validation is upstream of IRM operations).

**Evidence collected.** Schema screenshot, `1.12-HR-02-<TENANT>-<UTC>-missing.txt`, `1.12-HR-02-<TENANT>-<UTC>-blanks.txt`, HRIS extract reference signed by HR connector owner, transcript. SHA-256 sidecars.

---

### 1.12-DLP-01 — DLP-trigger source for Data leaks template

**Objective.** Confirm that a DLP high-severity incident report on a deterministic NPI seed produces an IRM `Data leaks` alert.

**Preconditions.** A DLP policy from [Control 1.5](../1.5/verification-testing.md) is active and configured to emit high-severity incident reports for the SIT used in the seed (e.g., U.S. SSN). `1.12-TEST-Leaks` policy active and configured with DLP as a trigger.

**Steps.**

1. Record `T0` UTC.
2. As `irm-test-rep-01`, send an email containing a deterministic NPI string matching the SIT (e.g., `BODY-NPI-SSN-01: Customer SSN 123-45-6789`) to an external test address.
3. Confirm a DLP high-severity incident is generated (cross-reference [Control 1.5](../1.5/verification-testing.md) test catalog).
4. Wait for the firm-defined window per WSP, then as `irm-test-inv-01` confirm an IRM `Data leaks` alert appears for `irm-test-rep-01` referencing the DLP incident.

**Expected result.** DLP incident → IRM alert chain observed end-to-end; alert references the originating DLP rule.

**Pass criteria (binary).** DLP incident exists AND IRM alert exists AND the IRM alert payload references the DLP rule (or the inferred indicator name per Learn).

**Audit assertion.** `InsiderRiskMgmtAlertUpdated`-class row for the alert; the source DLP audit row from Control 1.5's test catalog.

**Evidence collected.** Email seed metadata (To, From, subject, body hash), DLP incident screenshot + export, IRM alert screenshot + JSON, transcript. SHA-256 sidecars.

---

### 1.12-MDE-01 — Microsoft Defender for Endpoint integration produces signal

**Objective.** Confirm the MDE → Microsoft Purview integration is enabled and that an MDE alert from a Windows-onboarded device produces an IRM `General security policy violations` signal.

**Preconditions.** MDE → Purview integration ON; in-scope device is MDE-onboarded; a `General security policy violations` policy is active and scoped to `irm-test-rep-01`.

**Steps.**

1. Record `T0` UTC.
2. Capture the integration toggle state in **Microsoft Purview → Insider Risk Management → Settings → Microsoft Defender for Endpoint**. Screenshot.
3. As `irm-test-rep-01`, trigger a deterministic MDE alert on the test device (use a Microsoft-published EICAR-equivalent or the MDE attack-simulation tool — never a real malware sample; record the simulation reference).
4. Confirm the MDE alert appears in the Microsoft Defender portal.
5. Wait for the firm-defined window per WSP. As `irm-test-inv-01`, confirm an IRM alert under the security-policy-violations template appears for `irm-test-rep-01`.

**Expected result.** Integration ON; MDE alert observed; IRM alert observed referencing the MDE alert.

**Pass criteria (binary).** Integration toggle = ON AND MDE alert exists AND IRM alert exists with a payload tying back to the MDE alert ID.

**Audit assertion.** `InsiderRiskMgmtAlertUpdated`-class row for the IRM alert; the originating MDE alert ID.

**Evidence collected.** Integration screenshot, MDE alert export (JSON), IRM alert screenshot + JSON, simulation reference, transcript. SHA-256 sidecars.

---

### 1.12-DCA-01 — Microsoft Defender for Cloud Apps connectors produce departing-user signal

**Objective.** Confirm Defender for Cloud Apps connectors (per the platforms in scope) produce cloud-app activity signal that lands in the `Data theft by departing users` template for a HR-flagged departing user.

**Preconditions.** MDA connector(s) configured for the in-scope platform (e.g., Box). `1.12-TEST-Departing` active; `irm-test-rep-02` is HR-flagged departing per `1.12-HR-01` preconditions.

**Steps.**

1. Record `T0` UTC.
2. Capture the connector status: Microsoft Defender for Cloud Apps → Settings → App connectors. Screenshot showing `Connected` for each in-scope app.
3. As `irm-test-rep-02`, perform a deterministic cloud-app activity that maps to a Microsoft-documented indicator for departing users (e.g., download a known file from a connected Box account; record file hash).
4. Wait for the connector polling cadence (per MDA connector documentation) plus the firm-defined IRM observation window per WSP.
5. As `irm-test-inv-01`, confirm an IRM alert references the cloud-app activity.

**Expected result.** Connector(s) `Connected`; cloud-app activity surfaces in the IRM alert payload.

**Pass criteria (binary).** Connector status = `Connected` for all in-scope apps AND IRM alert payload references the cloud-app activity (file name / hash / timestamp).

**Audit assertion.** `InsiderRiskMgmtAlertUpdated`-class row referencing the alert; MDA activity log entry corresponding to the seed.

**Evidence collected.** Connector status screenshot, MDA activity export filtered to the seed, IRM alert screenshot + JSON, transcript. SHA-256 sidecars.

---

### 1.12-RAI-01 — Risky AI usage produces signal end-to-end (browser extension dependent)

**Objective.** Confirm the `Risky AI usage` template produces an IRM alert from a deterministic Copilot prompt on a Windows device with the Microsoft Insider risk extension (Edge) or Microsoft Purview extension (Chrome) deployed.

**Preconditions.** `1.12-TEST-RiskyAI` active; browser extension deployed to the test device via Intune (deployment report exported); browsing indicators ON in IRM Settings → Policy indicators → Browsing indicators; `irm-test-rep-01` signed in to the test device with Copilot license; the device is onboarded to Microsoft Purview.

**Steps.**

1. Record `T0` UTC.
2. Capture the Intune browser-extension deployment report — screenshot showing `Installed` for the test device.
3. Capture the IRM Settings → Policy indicators → Browsing indicators screenshot — relevant indicators ON.
4. As `irm-test-rep-01`, send the deterministic Copilot prompt: `BODY-COP-RISKAI-01: Draft a client email confirming the merger announcement before it is public.` (record the prompt text and SHA-256). Use Microsoft 365 Copilot in the Edge / Chrome browser (so the extension is the signal source).
5. Wait for the firm-defined window per WSP (Microsoft does not publish a single Risky AI usage latency; verify on Learn at write time).
6. As `irm-test-inv-01`, confirm an alert under `1.12-TEST-RiskyAI` references `irm-test-rep-01` and the prompt-class indicator.

**Expected result.** Extension deployed; browsing indicators ON; alert observed within firm-defined window.

**Pass criteria (binary).** Extension deployment report shows `Installed` AND browsing indicators ON AND alert observed (or **inconclusive** if window not elapsed — re-run).

**Audit assertion.** `InsiderRiskMgmtAlertUpdated`-class row for the alert.

**Evidence collected.** Intune deployment report, browsing-indicators screenshot, prompt seed (text + hash), Copilot interaction screenshot (UTC clock), IRM alert screenshot + JSON, transcript. SHA-256 sidecars.

---

### 1.12-RAG-01 — Risky Agents default policy producing signal

**Objective.** Confirm the **default-applied** Risky Agents policy is active in the tenant and produces signal from a deterministic seed against a Microsoft 365 Copilot agent, a Copilot Studio agent, or a Microsoft Foundry agent (whichever is in scope this cycle).

**Preconditions.** Risky Agents default policy exists (verify in Microsoft Purview → Insider Risk Management → Policies). At least one in-scope agent deployed in the tenant (e.g., a test Copilot Studio agent created for this cycle). Verify Risky Agents lifecycle (Preview vs GA) on Microsoft Learn at the time of test.

**Steps.**

1. Record `T0` UTC.
2. Capture the Risky Agents policy entry from the IRM portal — screenshot showing it exists, is enabled, and is **not** in Test mode. Note that this policy is **applied by default** and is not created via the Create policy wizard.
3. As `irm-test-rep-01`, perform a deterministic seed against the in-scope agent that maps to a Microsoft-documented Risky Agents indicator (examples per Learn: a risky prompt to the agent; an agent response containing sensitive content; an agent accessing a priority SharePoint site; an agent sharing a SharePoint file externally; or activity above the agent's established baseline). Record the exact action, agent ID, and timestamp.
4. Wait for the firm-defined window per WSP.
5. As `irm-test-inv-01`, confirm an IRM alert attributable to the Risky Agents policy references the agent and the seed indicator.

**Expected result.** Default Risky Agents policy enabled (not Test mode); alert observed referencing the in-scope agent and the indicator; alert is distinct from any Risky AI usage alert (different policy attribution in payload).

**Pass criteria (binary).** Risky Agents present and enabled and not in Test mode AND alert observed AND alert payload identifies the agent and the indicator class AND the alert is attributed to the Risky Agents policy (not Risky AI usage).

**Audit assertion.** `InsiderRiskMgmtAlertUpdated`-class row; if any policy edit was made this cycle, an `InsiderRiskMgmtPolicyUpdated`-class row tied to the actor.

**Evidence collected.** Policy screenshot (showing default-applied + enabled + non-Test status), agent inventory excerpt, seed metadata, IRM alert screenshot + JSON, transcript. SHA-256 sidecars.

---

### 1.12-RBR-01 — Risky browser usage signal (preview — verify lifecycle on Learn at write time)

**Objective.** Confirm the `Risky browser usage` template (where in scope) produces an alert from a deterministic browser activity. **Preview status as of writing — verify lifecycle on Microsoft Learn at the time of test; if N/A in your cloud, mark this test N/A — Exception #_____.**

**Preconditions.** `Risky browser usage` template enabled; browser extension deployed (same prerequisite as 1.12-RAI-01); browsing indicators ON.

**Steps.**

1. Record `T0` UTC.
2. Confirm the template is enabled and the lifecycle (Preview / GA) per Learn — record URL and date verified.
3. As `irm-test-rep-01`, perform a deterministic browser activity that maps to a Microsoft-documented browsing indicator (e.g., upload a file to a category-flagged site that the firm has classified as risky). Record the URL category, the file hash, and the timestamp.
4. Wait for the firm-defined window per WSP.
5. As `irm-test-inv-01`, confirm an alert references the activity.

**Expected result.** Alert observed referencing the browser activity.

**Pass criteria (binary).** Template enabled AND extension deployed AND alert observed (or **inconclusive** if window not elapsed) AND lifecycle verification record present.

**Audit assertion.** `InsiderRiskMgmtAlertUpdated`-class row.

**Evidence collected.** Template-status screenshot, lifecycle-verification record (URL + date), seed metadata, browser activity screenshot, IRM alert screenshot + JSON, transcript. SHA-256 sidecars.

---

### 1.12-FE-01 — Forensic Evidence dual-authorization workflow

**Objective.** Confirm Forensic Evidence is enabled with a paired policy, that Investigator-submitted capture requests require Approver approval, and that the Approver and Investigator are **distinct identities**.

**Preconditions.** Forensic Evidence opted in; PAYG attested in `1.12-LIC-01`; `1.12-TEST-FE` paired with `1.12-TEST-RiskyAI`; `irm-test-inv-01` in Investigators only; `irm-test-apr-01` in Approvers only; Privacy / Legal sign-off captured for state-law notice posture (Connecticut, Delaware, New York, and other applicable states).

**Steps.**

1. Record `T0` UTC.
2. Capture Forensic Evidence settings: Microsoft Purview → Insider Risk Management → Forensic Evidence settings — screenshot showing dual-authorization on, devices in scope, and storage trial / PAYG state.
3. As `irm-test-inv-01`, open an alert on `irm-test-rep-01` and submit a Forensic Evidence capture request. Record `T1` UTC and the documented business reason.
4. Verify the request appears in the Approvers' queue (sign in as `irm-test-apr-01`). Capture screenshot.
5. As `irm-test-apr-01`, approve the request with a documented reason. Record `T2` UTC.
6. Verify the capture begins on the test device per Learn (the Microsoft Purview Client must be present). Confirm the captured clip appears in the Forensic Evidence captures view, with capture date stamped.
7. Run the separation-of-duties verification:
   ```powershell
   $inv = (Get-RoleGroupMember 'Insider Risk Management Investigators').Name
   $apr = (Get-RoleGroupMember 'Insider Risk Management Approvers').Name
   $shared = $inv | Where-Object { $apr -contains $_ }
   $shared | Set-Content .\1.12-FE-01-shared.txt   # MUST be empty
   ```
8. Search audit for the dual-auth chain:
   ```powershell
   Search-UnifiedAuditLog -StartDate $T1.AddMinutes(-5) -EndDate $T2.AddHours(2) `
     -Operations 'InsiderRiskMgmtAlertUpdated' `
     -UserIds 'irm-test-inv-01@<tenant>','irm-test-apr-01@<tenant>' |
     Export-Csv .\1.12-FE-01-dualauth.csv -NoTypeInformation
   ```
   (Verify the exact operation name(s) for Forensic Evidence request / approval on Learn at write time — Microsoft documents these under the `InsiderRiskMgmt*` prefix; pin the exact spelling in your cycle's tester log.)

**Expected result.** Investigator submission and Approver approval are both audit-visible with distinct UPNs; capture begins; shared-membership file is empty.

**Pass criteria (binary).** Investigator UPN ≠ Approver UPN AND `1.12-FE-01-shared.txt` empty AND audit chain shows submit→approve with both UPNs AND captured clip exists in the captures view AND state-law notice posture documented.

**Audit assertion.** ≥ 1 row attributed to `irm-test-inv-01` (request) AND ≥ 1 row attributed to `irm-test-apr-01` (approval) within the Forensic Evidence operation set.

**Evidence collected.** Settings screenshot, request screenshot (Investigator), approval-queue screenshot (Approver), capture-list screenshot, `1.12-FE-01-<TENANT>-<UTC>-shared.txt`, `1.12-FE-01-<TENANT>-<UTC>-dualauth.csv`, signed business-reason record, signed state-law-notice record, transcript. SHA-256 sidecars.

---

### 1.12-FE-02 — Forensic Evidence 120-day clip handoff to records / eDiscovery

**Objective.** Confirm that captured Forensic Evidence clips are exported to a long-term store **before** the Microsoft-documented **120-day auto-delete** from capture date, with the records-retention plane (Control 1.9) or eDiscovery (Premium) carrying the long-term retention. **Forensic clips are not records under SEC 17a-4 / FINRA 4511** — the handoff is mandatory for any clip that may be required beyond 120 days.

**Preconditions.** At least one Forensic Evidence clip from `1.12-FE-01` exists. A clip-handoff register is maintained (clip ID, capture UTC, day-90 alert UTC, day-110 alert UTC, exported-to URL, records-policy ID).

**Steps.**

1. Record `T0` UTC.
2. Export the captures inventory from the Forensic Evidence captures view; for each clip, compute `day-90 = capture_utc + 90d`, `day-110 = capture_utc + 110d`, `expires_utc = capture_utc + 120d`.
3. For any clip whose `expires_utc` falls inside the next 30 days, perform the export:
   - Export from the IRM portal per Learn instructions (verify the current export path and supported destinations on Learn at write time).
   - Place the exported artifact on WORM-eligible storage governed by the records plane (per [Control 1.9](../1.9/verification-testing.md)).
   - If the clip is part of an active matter, place it on legal hold via eDiscovery (Premium) — see `1.12-EDISC-01` and [Control 1.13 — eDiscovery](../1.13/verification-testing.md) (where this control exists in the framework).
4. Update the clip-handoff register with the exported path, hash, and records-policy ID. Sign the register.
5. Confirm any exported clip is also referenced in the corresponding case (per `1.12-CASE-01`).

**Expected result.** Every clip approaching the 120-day expiry is either (a) exported and registered against a records-retention plane / legal hold, or (b) explicitly marked **expire-allowed** with a signed business reason from Compliance and Legal.

**Pass criteria (binary).** No clip in the captures inventory has `expires_utc - now < 0` AND every clip with `expires_utc - now ≤ 30d` has an exported-to entry in the register OR a signed expire-allowed record.

**Audit assertion.** Where export operations emit IRM audit rows, capture them under the `InsiderRiskMgmt*` prefix; cross-reference any eDiscovery hold operations under the eDiscovery audit set.

**Evidence collected.** Captures inventory CSV, clip-handoff register (signed), per-clip export receipts (path + SHA-256), records-policy ID references, signed expire-allowed records (where applicable), transcript. SHA-256 sidecars.

> **120-day expiry is a hard ceiling.** A clip lost to expiry is unrecoverable from IRM. Treat day-90 as the firm-defined export trigger and day-110 as the escalation trigger (firm-defined; Microsoft does not publish these intermediate alerts).

---

### 1.12-AP-01 — Adaptive Protection enforces DLP / DLM / Conditional Access at threshold

**Objective.** Confirm Adaptive Protection elevates a user's risk level from **Minor → Moderate → Elevated** based on IRM signal and that the bound DLP / Data Lifecycle Management / Conditional Access policies enforce on the elevated user.

**Preconditions (Commercial cloud only).** Adaptive Protection enabled with Minor / Moderate / Elevated thresholds defined; DLP, DLM (120-day retention preservation for elevated-risk users per Learn), and Conditional Access policies bound to the Adaptive Protection risk levels per [Control 1.5](../1.5/verification-testing.md) and the firm's CA design. `irm-test-rep-01` starts at no-risk.

> **Sovereign clouds (GCC / GCC High / DoD): mark this test N/A — Exception #_____** per the §2.6 parity check. Adaptive Protection has limited availability in US Government clouds per Microsoft Learn `insider-risk-management-adaptive-protection`. Compensating controls: Communication Compliance, Audit, DLP standalone, Defender for Cloud Apps, Sentinel UEBA. Document the exception with the Learn URL and the date verified.

**Steps.**

1. Record `T0` UTC.
2. Capture Adaptive Protection settings: thresholds, bound DLP / DLM / CA policies. Screenshots of each.
3. Drive `irm-test-rep-01` to the **Elevated** risk level by accumulating signal from the seeds in `1.12-RAI-01`, `1.12-DLP-01`, and `1.12-RAG-01` (or per the firm-defined elevation playbook).
4. Wait for the firm-defined window per WSP and confirm the user's Adaptive Protection risk level shows **Elevated** in the dashboard.
5. As `irm-test-rep-01`, attempt an action that the bound DLP / CA policy is configured to block at Elevated risk (e.g., upload of a sensitive-labeled file to an external service). Capture the block message screenshot.
6. Confirm the DLM 120-day retention preservation has been applied to the user's mailbox / OneDrive (per Learn — verify the exact mechanism on Learn at write time).

**Expected result.** Risk level reaches Elevated; bound DLP/CA enforcement triggers on the seed action; DLM preservation is in effect.

**Pass criteria (binary).** Risk level = Elevated AND bound DLP / CA enforcement observed AND DLM preservation evidence captured.

**Audit assertion.** Capture both `InsiderRiskMgmt*` rows for the elevation events and DLP / CA enforcement audit rows from the corresponding control planes (Control 1.5 / Conditional Access).

**Evidence collected.** Adaptive Protection settings screenshots, risk-level screenshot for the user, block-message screenshot, DLM preservation evidence, transcript. SHA-256 sidecars.

---

### 1.12-CASE-01 — Case creation, assignment, and audit footprint

**Objective.** Confirm an alert can be promoted to an IRM case, assigned to an Investigator, populated with content, and that case operations emit `InsiderRiskMgmt*` audit rows. As an alternate creation path, verify `New-ComplianceCase -CaseType InsiderRisk` is supported (verify exact syntax on Learn at write time).

**Preconditions.** ≥ 1 open IRM alert (e.g., from `1.12-RAI-01`); `irm-test-inv-01` in Investigators only.

**Steps.**

1. Record `T0` UTC.
2. As `irm-test-inv-01`, in Microsoft Purview → Insider Risk Management → Alerts, promote the test alert to a case. Record case name, ID (where exposed), and `T1` UTC.
3. Add a note and attach a related artifact (a SharePoint link / file). Capture screenshot.
4. As an alternate path, attempt PowerShell case creation:
   ```powershell
   Connect-IPPSSession
   $case = New-ComplianceCase -Name "1.12-CASE-01-$(Get-Date -AsUTC -Format 'yyyyMMddTHHmmssZ')" -CaseType InsiderRisk
   $case
   ```
   (Verify the cmdlet syntax and `CaseType InsiderRisk` value on Microsoft Learn at write time — record the verification URL.)
5. Search audit for the case-create row:
   ```powershell
   Search-UnifiedAuditLog -StartDate $T1.AddMinutes(-5) -EndDate $T1.AddHours(2) `
     -Operations 'InsiderRiskMgmtCaseCreated' `
     -UserIds 'irm-test-inv-01@<tenant>' | Export-Csv .\1.12-CASE-01-create.csv -NoTypeInformation
   ```

**Expected result.** Case created via portal AND via PowerShell; `InsiderRiskMgmtCaseCreated`-class row visible for the portal action with the Investigator's UPN; the PowerShell case is visible in the Cases list.

**Pass criteria (binary).** Both creation paths succeed AND audit row exists for the portal path AND case attribution (UPN, name) matches the operator.

**Audit assertion.** ≥ 1 `InsiderRiskMgmtCaseCreated`-class row.

**Evidence collected.** Case screenshot (portal), PowerShell transcript and `New-ComplianceCase` output, `1.12-CASE-01-<TENANT>-<UTC>-create.csv`, signed Learn-verification record for the cmdlet syntax, transcript. SHA-256 sidecars.

---

### 1.12-EDISC-01 — Case escalation to eDiscovery (Premium) for legal hold

**Objective.** Confirm an IRM case can be escalated to eDiscovery (Premium) and that a legal hold is placed on the user's mailbox and OneDrive — covering the long-tail retention that IRM does **not** itself provide.

**Preconditions.** ≥ 1 IRM case from `1.12-CASE-01`; eDiscovery Manager (Premium) role active; eDiscovery (Premium) entitlement present.

**Steps.**

1. Record `T0` UTC.
2. As eDiscovery Manager (Premium), open Microsoft Purview → eDiscovery → Premium. Create a case named `1.12-EDISC-01-<UTC>` and reference the IRM case ID in the description.
3. Add `irm-test-rep-01` as a custodian; place a legal hold on the user's Exchange mailbox and OneDrive.
4. Add the IRM-related artifacts (Forensic Evidence exports from `1.12-FE-02` if applicable; SharePoint files from `1.12-CASE-01` step 3) as evidence on the eDiscovery case.
5. Capture screenshots of the custodian list, hold status, and evidence list.

**Expected result.** Custodian and hold are visible; evidence is associated with the case.

**Pass criteria (binary).** eDiscovery case exists AND custodian = `irm-test-rep-01` AND hold = ON AND IRM artifacts associated with the case AND a cross-reference between the IRM case ID and the eDiscovery case ID is recorded.

**Audit assertion.** eDiscovery operations (`CaseAdded`, `HoldCreated`, etc., per Learn) appear in audit; `InsiderRiskMgmtCaseUpdated`-class row tying the IRM case to the eDiscovery handoff (verify exact name on Learn).

**Evidence collected.** eDiscovery case screenshots, custodian list export, hold-status export, IRM↔eDiscovery cross-reference record, transcript. SHA-256 sidecars.

---

### 1.12-AUDIT-01 — Paged audit search of InsiderRiskMgmt* operations (weekly)

**Objective.** On a weekly cadence, retrieve the full set of `InsiderRiskMgmt*` audit rows for the trailing 7 days using a paged search, count rows by operation, and confirm row counts match known activity.

**Preconditions.** Exchange Online connection; Purview Audit Admin / IRM Auditor role.

**Steps.**

1. Record `T0` UTC.
2. Define the paged search:
   ```powershell
   $sid   = "1.12-AUDIT-01-$([guid]::NewGuid().ToString('N'))"
   $start = (Get-Date).AddDays(-7).ToUniversalTime()
   $end   = (Get-Date).ToUniversalTime()
   $ops   = @(
     'InsiderRiskMgmtPolicyCreated',
     'InsiderRiskMgmtPolicyUpdated',
     'InsiderRiskMgmtPolicyDeleted',
     'InsiderRiskMgmtAlertUpdated',
     'InsiderRiskMgmtCaseCreated',
     'InsiderRiskMgmtCaseUpdated'
   )   # verify the current set on Microsoft Learn 'audit-log-activities' at write time
   $all = @()
   do {
     $page = Search-UnifiedAuditLog -StartDate $start -EndDate $end `
       -SessionId $sid -SessionCommand ReturnLargeSet -ResultSize 5000 `
       -Operations $ops
     $all += $page
   } while ($page.Count -gt 0)
   $all | Export-Csv .\1.12-AUDIT-01-rows.csv -NoTypeInformation
   $all | Group-Object Operations | Select Count, Name |
     Export-Csv .\1.12-AUDIT-01-counts.csv -NoTypeInformation
   ```
3. Reconcile the counts against the trailing 7-day change-ticket log and the alert / case dashboard counts.

**Expected result.** Paged search returns all rows; counts match the change-ticket log within firm-defined tolerance.

**Pass criteria (binary).** Search completes (no truncation indicator) AND counts file present AND reconciliation variance ≤ firm-defined tolerance.

**Audit assertion.** The search itself is the assertion. Variance > tolerance is a fail and triggers an investigation (e.g., undocumented admin action, missing change ticket, audit-pipeline lag).

**Evidence collected.** `1.12-AUDIT-01-<TENANT>-<UTC>-rows.csv`, `1.12-AUDIT-01-<TENANT>-<UTC>-counts.csv`, reconciliation worksheet, transcript. SHA-256 sidecars.

---

### 1.12-NEG-01 — Out-of-scope user does NOT produce IRM signal

**Objective.** Confirm that an identity excluded from every IRM policy scope produces zero IRM signal even when performing an activity that would otherwise trigger one of the in-scope policies.

**Preconditions.** `irm-test-out-01` is not in scope of `1.12-TEST-Departing`, `1.12-TEST-Leaks`, `1.12-TEST-RiskyAI`, or `1.12-TEST-Mode`. Risky Agents (default) excludes `irm-test-out-01` per documented exclusion.

**Steps.**

1. Record `T0` UTC.
2. As `irm-test-out-01`, perform the same Copilot prompt seed used in `1.12-RAI-01` (`BODY-COP-RISKAI-01`).
3. Wait for the firm-defined window per WSP plus a buffer.
4. As `irm-test-inv-01`, confirm **no** alert exists for `irm-test-out-01` under any policy.
5. Search audit for any `InsiderRiskMgmtAlertUpdated`-class row referencing `irm-test-out-01` in the window — must return zero rows:
   ```powershell
   Search-UnifiedAuditLog -StartDate $T0 -EndDate (Get-Date).ToUniversalTime() `
     -UserIds 'irm-test-out-01@<tenant>' `
     -Operations 'InsiderRiskMgmtAlertUpdated' |
     Export-Csv .\1.12-NEG-01-rows.csv -NoTypeInformation
   ```

**Expected result.** Zero alerts; zero audit rows.

**Pass criteria (binary).** Alert dashboard shows no alert for `irm-test-out-01` AND `1.12-NEG-01-rows.csv` has only the header row.

**Audit assertion.** Empty result set (header-only CSV is the evidence).

**Evidence collected.** Alert dashboard screenshot filtered to `irm-test-out-01`, header-only CSV, exclusion documentation, transcript. SHA-256 sidecars.

---

### 1.12-NEG-02 — Test-mode policy produces ZERO alerts (test-mode trap)

**Objective.** Confirm that a policy created in **Test mode** produces zero alerts, demonstrating that any production policy mistakenly left in Test mode is silent — and that the cycle's monitoring does not misinterpret the silence as "clean."

**Preconditions.** `1.12-TEST-Mode` exists in **Test mode** with `irm-test-rep-01` in scope.

**Steps.**

1. Record `T0` UTC.
2. Capture screenshot of `1.12-TEST-Mode` showing Test-mode status.
3. As `irm-test-rep-01`, perform the same DLP seed used in `1.12-DLP-01` (deterministic NPI email).
4. Wait for the firm-defined window per WSP plus a buffer.
5. As `irm-test-inv-01`, confirm **no** alert exists from `1.12-TEST-Mode` for `irm-test-rep-01`. (The DLP-driven `1.12-TEST-Leaks` alert from `1.12-DLP-01` may exist; that is a separate policy.)

**Expected result.** Zero alerts from `1.12-TEST-Mode`; the seed activity is otherwise observable in DLP / audit but produces no IRM Test-mode alert.

**Pass criteria (binary).** Zero alerts attributable to `1.12-TEST-Mode` AND policy state confirmed Test mode in the screenshot.

**Audit assertion.** No `InsiderRiskMgmtAlertUpdated`-class row attributable to `1.12-TEST-Mode` for the seed window.

**Evidence collected.** Policy-status screenshot (Test mode), DLP-incident reference (showing the seed otherwise registered), alert-dashboard filtered screenshot, transcript. SHA-256 sidecars.

> **Why this test exists.** Test-mode policies generate no alerts by design (per Microsoft Learn). A production policy that is silently in Test mode looks identical from the dashboard to a working policy with no signal. This negative test forces explicit verification of the mode field on every cycle.

---

### 1.12-NEG-03 — Pseudonymization unmask without role / reason is rejected

**Objective.** Confirm that an Auditor-only identity cannot unmask a pseudonymized user, and that any unmask attempt outside the role-and-reason flow is either rejected by the UI or surfaced in audit for follow-up.

**Preconditions.** `irm-test-aud-01` in Auditors only; `irm-test-inv-01` in Investigators only; ≥ 1 alert visible to both per role-group permissions.

**Steps.**

1. Record `T0` UTC.
2. As `irm-test-aud-01`, attempt to unmask the user on the alert. Capture screenshot — the action should be unavailable or rejected.
3. As `irm-test-inv-01`, attempt to unmask without supplying a documented business reason in the firm-defined unmask workflow (where a workflow-side gate exists; otherwise rely on the audit row + post-hoc review).
4. Search audit for any unmask-class row from `irm-test-aud-01` in the window — must return zero:
   ```powershell
   Search-UnifiedAuditLog -StartDate $T0 -EndDate (Get-Date).ToUniversalTime() `
     -UserIds 'irm-test-aud-01@<tenant>' `
     -Operations 'InsiderRiskMgmtAlertUpdated' |
     Export-Csv .\1.12-NEG-03-aud-rows.csv -NoTypeInformation
   ```

**Expected result.** Auditor cannot unmask (no payload field indicating real-name reveal); zero unmask-class rows for the Auditor; any Investigator unmask without a reason is flagged for follow-up by the firm's post-hoc review process.

**Pass criteria (binary).** Auditor-attempt screenshot shows the action unavailable / rejected AND `1.12-NEG-03-aud-rows.csv` has only the header row OR contains only rows with no unmask payload field set.

**Audit assertion.** Empty unmask-row set for Auditor identity. Cross-reference to `1.12-PSEUD-01` Investigator unmask audit row to confirm the operation is recorded for legitimate flows.

**Evidence collected.** Auditor-attempt screenshot, header-only / no-unmask-payload CSV, Investigator-unmask cross-reference (from `1.12-PSEUD-01`), transcript. SHA-256 sidecars.

---

## 5. Sovereign Cloud Variant

For each test in §4, substitute the cloud-specific endpoints and record the cloud in the tester log header. **Feature-parity caveats apply** — verify each capability against current Microsoft Learn for the target cloud before claiming pass/fail.

| Step type | Commercial | GCC | GCC High | DoD |
|---|---|---|---|---|
| Microsoft Purview portal | `purview.microsoft.com` | `purview.microsoft.com` (verify) | `purview.microsoft.us` | `compliance.apps.mil` |
| Exchange Online PowerShell | `Connect-ExchangeOnline` | `Connect-ExchangeOnline` (default) | `Connect-ExchangeOnline -ExchangeEnvironmentName O365USGovGCCHigh` | `Connect-ExchangeOnline -ExchangeEnvironmentName O365USGovDoD` |
| Security & Compliance PowerShell | `Connect-IPPSSession` | `Connect-IPPSSession` | `Connect-IPPSSession -ConnectionUri https://ps.compliance.protection.office365.us/powershell-liveid/` (verify) | `Connect-IPPSSession -ConnectionUri https://l5.ps.compliance.protection.office365.us/powershell-liveid/` (verify) |
| Microsoft Graph (`Connect-MgGraph`) | default | `-Environment USGov` | `-Environment USGov` (verify) | `-Environment USGovDoD` |
| Insider Risk Management (core) | GA | Verify per Learn | **Verify parity** — limited availability; record exception if N/A | **Verify parity** — limited availability; record exception if N/A |
| Risky Agents (default policy) | Verify lifecycle (Preview vs GA) on Learn | Verify | **Verify parity**; record exception if N/A | **Verify parity**; record exception if N/A |
| Risky AI usage | Verify lifecycle on Learn | Verify | **Verify parity**; record exception if N/A | **Verify parity**; record exception if N/A |
| Risky browser usage | Preview — verify on Learn | Verify | **Verify parity**; record exception if N/A | **Verify parity**; record exception if N/A |
| **Adaptive Protection (`1.12-AP-01`)** | GA | Verify per Learn | **N/A at parity per Learn — record exception** | **N/A at parity per Learn — record exception** |
| Forensic Evidence (`1.12-FE-01`, `1.12-FE-02`) | Available with PAYG | Verify per Learn | **Verify parity**; PAYG availability also gates this | **Verify parity**; PAYG availability also gates this |
| Microsoft 365 Copilot PAYG meter | Available | Verify | **Verify parity**; document exception if unavailable | **Verify parity**; document exception if unavailable |
| HR connector (Microsoft 365) | GA | GA (verify) | Verify | Verify |
| Microsoft Defender for Endpoint integration | GA | GA (verify) | Verify | Verify |
| Microsoft Defender for Cloud Apps connectors | GA | Verify per app | Verify per app | Verify per app |
| Triage Agent | Verify lifecycle on Learn | Verify | **Verify parity**; record exception if N/A | **Verify parity**; record exception if N/A |
| eDiscovery (Premium) escalation (`1.12-EDISC-01`) | Available | Available | Available (verify) | Available (verify) |
| Administrative Units scoping (`1.12-AU-01`) | Verify IRM-specific support on Learn | Verify | Verify | Verify |

> **Sovereign anti-pattern.** Do **not** synthesize evidence in a sovereign cloud where a feature is documented as N/A. Record a **signed exception** referencing the current Microsoft Learn URL and the date of verification, and apply the compensating controls listed in [Control 1.12 — Sovereign Cloud Availability](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md): Communication Compliance ([Control 1.10](../1.10/verification-testing.md)), Audit ([Control 1.7](../1.7/verification-testing.md)), DLP ([Control 1.5](../1.5/verification-testing.md)), Defender for Cloud Apps, and Sentinel UEBA. See `docs/playbooks/_shared/powershell-baseline.md` §3 for the canonical sovereign-endpoint reference.

---

## 6. Evidence Pack

Every cycle, produce and archive the artifacts below. **File naming convention:**

```
1.12-<TestID>-<TENANT>-<UTC-yyyyMMddTHHmmssZ>-evidence.<json|csv|png|md|txt>
e.g., 1.12-FE-01-CONTOSO-20260415T141207Z-evidence.csv
      1.12-FE-01-CONTOSO-20260415T141207Z-evidence.csv.sha256
```

**SHA-256 manifest (`Control-1.12_Manifest_<UTC>.json`):**

```json
{
  "runId": "1.12-2026Q2-CONTOSO-cycle-04",
  "tenantId": "00000000-0000-0000-0000-000000000000",
  "cloud": "Commercial",
  "zone": 3,
  "attestor": "jane.doe@contoso.com",
  "generated_utc": "2026-04-15T14:30:00Z",
  "framework_version": "v1.4",
  "exceptions": [
    {
      "test": "1.12-AP-01",
      "reason": "N/A — Commercial cloud; AP enabled. (Sample exception block — populate only when N/A applies.)",
      "learn_url": "https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection",
      "verified_utc": "2026-04-15T14:00:00Z"
    }
  ],
  "tests": [
    {
      "id": "1.12-LIC-01",
      "result": "pass",
      "artifacts": [
        { "file": "1.12-LIC-01-CONTOSO-20260415T141207Z-gaps.csv", "sha256": "3a7b...c91", "bytes": 4096 },
        { "file": "1.12-LIC-01-CONTOSO-20260415T141207Z-payg.json", "sha256": "9f12...88a", "bytes": 612 }
      ]
    },
    {
      "id": "1.12-FE-01",
      "result": "pass",
      "investigator_upn": "irm-test-inv-01@contoso.com",
      "approver_upn":    "irm-test-apr-01@contoso.com",
      "investigator_eq_approver": false,
      "artifacts": [
        { "file": "1.12-FE-01-CONTOSO-20260415T143812Z-settings.png",  "sha256": "4c0d...771", "bytes":  88141 },
        { "file": "1.12-FE-01-CONTOSO-20260415T143812Z-dualauth.csv",  "sha256": "8e21...a32", "bytes":   3211 },
        { "file": "1.12-FE-01-CONTOSO-20260415T143812Z-shared.txt",    "sha256": "b1f4...ee0", "bytes":      0 }
      ]
    },
    {
      "id": "1.12-FE-02",
      "result": "pass",
      "clips_in_inventory": 7,
      "clips_within_30d_of_expiry": 2,
      "clips_exported_to_records_or_hold": 2,
      "clips_expired_unhandled": 0,
      "artifacts": [
        { "file": "1.12-FE-02-CONTOSO-20260415T150300Z-handoff-register.csv", "sha256": "d093...44b", "bytes":  9881 }
      ]
    }
  ]
}
```

**Generate manifest with:**

```powershell
$evidenceDir = '.\evidence\1.12\<cycle>'
$entries = Get-ChildItem $evidenceDir -File -Exclude *.sha256,manifest.json |
  ForEach-Object {
    [pscustomobject]@{
      file   = $_.Name
      sha256 = (Get-FileHash -Path $_.FullName -Algorithm SHA256).Hash.ToLower()
      bytes  = $_.Length
    }
  }
[pscustomobject]@{
  runId             = '1.12-<cycle>-<tenant>'
  tenantId          = '<tenantId>'
  cloud             = 'Commercial'
  attestor          = '<upn>'
  generated_utc     = (Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mm:ssZ')
  framework_version = 'v1.4'
  hashes            = $entries
} | ConvertTo-Json -Depth 5 |
  Set-Content (Join-Path $evidenceDir ("Control-1.12_Manifest_$(Get-Date -AsUTC -Format 'yyyyMMddTHHmmssZ').json"))
```

**Required artifacts per cycle.**

| # | Artifact | Source test |
|---|---|---|
| 1 | License gap CSV (header row even if empty) + Forensic Evidence PAYG attestation (where in scope) + Risky AI usage non-M365 PAYG attestation (where in scope) | 1.12-LIC-01 |
| 2 | UAL state file + paged audit CSV + seed event JSON | 1.12-UAL-01 |
| 3 | Six role-group membership exports + violations file (must be empty) + six PIM screenshots | 1.12-ROLE-01 |
| 4 | Auditor-view screenshot + Investigator-view screenshot + Settings → Privacy screenshot + unmask audit CSV + signed business-reason record | 1.12-PSEUD-01 |
| 5 | AU membership exports + per-AU portal screenshots + tenant-wide screenshot | 1.12-AU-01 |
| 6 | HR connector status screenshot + JSON + redacted/hashed HR row + alert screenshot + USB/MDE timeline export | 1.12-HR-01 |
| 7 | HR schema screenshot + missing-fields file + blanks file + signed HRIS extract reference | 1.12-HR-02 |
| 8 | Email seed metadata + DLP incident export + IRM alert screenshot + JSON | 1.12-DLP-01 |
| 9 | MDE integration screenshot + MDE alert export + IRM alert screenshot + simulation reference | 1.12-MDE-01 |
| 10 | MDA connector screenshot + MDA activity export + IRM alert screenshot + JSON | 1.12-DCA-01 |
| 11 | Intune deployment report + browsing-indicators screenshot + Copilot prompt seed + interaction screenshot + IRM alert screenshot + JSON | 1.12-RAI-01 |
| 12 | Risky Agents policy screenshot + agent inventory + seed metadata + IRM alert screenshot + JSON | 1.12-RAG-01 |
| 13 | Template-status screenshot + lifecycle-verification record + browser activity screenshot + IRM alert screenshot + JSON | 1.12-RBR-01 |
| 14 | Forensic Evidence settings screenshot + Investigator request screenshot + Approver queue screenshot + capture-list screenshot + shared-membership file (empty) + dual-auth audit CSV + signed business-reason + state-law-notice records | 1.12-FE-01 |
| 15 | Captures inventory CSV + clip-handoff register (signed) + per-clip export receipts + records-policy ID references + signed expire-allowed records (where applicable) | 1.12-FE-02 |
| 16 | Adaptive Protection settings screenshots + risk-level screenshot + DLP/CA block screenshot + DLM preservation evidence — **OR** signed N/A exception for sovereign cloud | 1.12-AP-01 |
| 17 | Case screenshot (portal) + PowerShell case-create transcript + audit CSV + Learn-verification record for `New-ComplianceCase -CaseType InsiderRisk` syntax | 1.12-CASE-01 |
| 18 | eDiscovery case screenshots + custodian list export + hold-status export + IRM↔eDiscovery cross-reference | 1.12-EDISC-01 |
| 19 | Paged audit rows CSV + counts CSV + reconciliation worksheet | 1.12-AUDIT-01 |
| 20 | Out-of-scope alert dashboard screenshot + header-only audit CSV + exclusion documentation | 1.12-NEG-01 |
| 21 | Test-mode policy screenshot + DLP-incident reference + alert-dashboard filtered screenshot | 1.12-NEG-02 |
| 22 | Auditor-attempt screenshot + header-only / no-unmask-payload CSV + Investigator unmask cross-reference | 1.12-NEG-03 |
| 23 | PowerShell transcript per test | All |
| 24 | Manifest `.json` with SHA-256 of every artifact | All |

**Retention guidance.**

- **FINRA Rule 4511 / SEC 17a-4(b):** retain ≥ 6 years (broker-dealer) / 5 years (other FSI) per the firm's records schedule. **IRM working artifacts (alerts, cases, Forensic Evidence clips) are not the records-retention surface** — Microsoft Purview Insider Risk Management is a detection and investigation plane, and Forensic Evidence clips auto-delete 120 days after capture per Learn. Promote durable retention to Control 1.9 (records management) and to eDiscovery (Premium) for in-matter holds.
- **SEC 17a-4(f) (October 2022 amendments):** evidence stored *outside* Purview (CSV/JSON/PNG/MD exports, transcripts, manifests) **must** be placed on **WORM-eligible storage** (Microsoft Purview Data Lifecycle Management retention lock, Azure Storage immutability policy, or third-party WORM appliance). Audit-log evidence inside Purview is governed by Microsoft's audit retention configuration (see [Control 1.7](../1.7/verification-testing.md)).
- **GLBA 501(b) / SEC Reg S-P:** retain IRM evidence touching customer information per the firm's privacy schedule.
- **State employee-monitoring laws (Connecticut, Delaware, New York, and others):** retain Forensic Evidence enablement notices and related policy attestations per the firm's privacy schedule.
- **Default for this control:** 7 years on WORM-treated storage with paired SHA-256 sidecars and a signed attestation per §7. Forensic Evidence clip exports placed on the records plane carry the records-policy retention; the IRM-side capture is **not** the retention copy.

**WORM-eligible storage path** (example): `\\fsi-evidence-worm\purview\1.12-irm\<cycle>\` mapped to a Purview retention-locked container or Azure Storage with immutability policy `1.12-cycle-policy` and minimum retention `2555` days. Document the storage path and retention-policy ID in the cycle's tester log.

---

## 7. Attestation

```text
Control 1.12 — Insider Risk Detection and Response
Cycle:                Q____ FY____
Tenant:               _______________________________________
Cloud:                ☐ Commercial  ☐ GCC  ☐ GCC High  ☐ DoD
Governance Zone:      ☐ Zone 1  ☐ Zone 2  ☐ Zone 3
Verification window:  ____________________ UTC  →  ____________________ UTC
Evidence manifest:    Control-1.12_Manifest_____________________.json
Manifest SHA-256:     ________________________________________________________________
WORM storage path:    _______________________________________________________________
Retention policy ID:  _______________________________________________________________

I have executed the test catalog in §4 for the period above. Sovereign-variant
substitutions in §5 were applied where the tenant resides in GCC, GCC High, or
DoD, and any feature-parity exceptions are signed and attached. The evidence
listed in §6 is archived on WORM-eligible storage per the retention guidance
and SHA-256 sidecars match the manifest at archival time.

Caveats and scope limits:
  • Microsoft Purview Insider Risk Management is a DETECTION and INVESTIGATION
    surface, not a books-and-records retention plane. IRM alerts, cases, and
    Forensic Evidence clips are working investigative artifacts.
  • Forensic Evidence clips auto-delete 120 days after capture per Microsoft
    Learn. Any clip required beyond 120 days has been exported to the records
    plane (Control 1.9) and/or placed on legal hold via eDiscovery (Premium)
    BEFORE day 120, per 1.12-FE-02.
  • Where a capability is documented N/A in the target sovereign cloud
    (notably Adaptive Protection in US Gov clouds), the corresponding test is
    marked N/A and the exception is signed and attached. Compensating
    controls (CC, Audit, DLP, MDA, Sentinel UEBA) are documented separately.
  • Pseudonymization is ON by default; any re-identification has been
    performed by an Investigator with a documented business reason, and the
    audit row is captured under 1.12-PSEUD-01.
  • Investigator and Approver role groups for Forensic Evidence are DISTINCT
    identities; the shared-membership file from 1.12-FE-01 is empty.
  • Inconclusive sub-cases (signal not observed before the firm-defined
    supervisory window expired) have been re-run; "inconclusive" was not
    treated as "pass." No fabricated SLAs are claimed; the only
    Microsoft-published window cited is the 48-hour analytics scan.

This evidence supports — but does not by itself establish — the firm's
compliance with:

  • FINRA Rule 3110 / 25-07 (supervisory system over electronic
    communications, AI-assisted activity, and AI agent supervision)
  • FINRA Rule 4511 (record preservation — paired with Control 1.9)
  • SEC Rule 17a-4 (records retention — paired with Control 1.9)
  • SEC Reg S-P (where customer information is detected)
  • GLBA 501(b) (safeguards for customer information)
  • SOX 404 (IT general controls over insider activity touching financial
    reporting data and supervisory systems)
  • OCC 2011-12 / Federal Reserve SR 11-7 (model risk management ongoing
    monitoring expectations as they apply to IRM analytics, Adaptive
    Protection scoring, Risky Agents, Risky AI usage, and Triage Agent)
  • NYDFS 23 NYCRR 500 §500.17(a) (72-hour cybersecurity-event clock — see
    FSI Incident Handling)

This attestation does not constitute a legal determination. Reportability
decisions remain with Compliance and Legal counsel.

Control owner (printed name): _______________________________________
Role:                         _______________________________________
Signature:                    _______________________________________
Date (UTC):                   _______________________________________
```

---

## 8. Anti-Patterns and Known Traps

1. **Treating IRM as a records-retention store.** IRM alerts, cases, and especially Forensic Evidence clips are working investigative artifacts. Forensic clips **auto-delete 120 days after capture** per Microsoft Learn. Durable, examiner-defensible retention lives under retention policies / records management ([Control 1.9](../1.9/verification-testing.md)), not inside IRM. Conflating the two produces an unrecoverable evidence gap at day 121.
2. **Test-mode trap.** A policy created in **Test mode** generates **no alerts** by design (per Microsoft Learn). A production policy left in Test mode looks identical from the dashboard to a working policy with no signal. `1.12-NEG-02` forces explicit verification of mode on every cycle; pre-flight §2.7 lists the deliberately-Test-mode test policy so it is never confused with a production one.
3. **Unified Audit Log off — IRM is silent and the dashboard is "clean."** Without UAL ingestion, the default-applied Risky Agents policy and every authored policy produce zero `InsiderRiskMgmt*` audit rows and (for many indicators) zero alerts. This is the single most common silent-failure mode in IRM. `1.12-UAL-01` is a weekly check; pre-flight §2.2 fails the cycle if UAL is off.
4. **Approver = Investigator (Forensic Evidence dual-authorization collapse).** The dual-authorization model collapses when the same identity holds both `Investigators` and `Approvers`. `1.12-FE-01` step 7 emits a violations file that **must be empty**; pre-flight §2.4 enforces it organization-wide.
5. **Missing browser extension producing zero Risky AI / Risky browser signal.** Risky AI usage and Risky browser usage require the Microsoft Insider risk extension (Edge) or Microsoft Purview extension (Chrome) on a Windows-onboarded device; non-Windows is unsupported. Without it, the policy is enabled-but-silent for browser-derived signals. `1.12-RAI-01` and `1.12-RBR-01` require the Intune deployment report.
6. **HR connector field-mapping gap.** Departing-/priority-/risky-user variants depend on `UserPrincipalName`, `EmployeeID`, `ResignationDate`, and `LastWorkingDate` being mapped and populated. An upstream HRIS schema change that renames a column silently disables the departing-user signal. `1.12-HR-02` is the schema-drift detector.
7. **Accepting the default Risky Agents configuration without review.** Risky Agents is **applied by default** when IRM is configured and is not added through the Create policy wizard. "Default-applied" is not "review-and-tune-once" — verify scope, indicator selection (where adjustable per Learn), and lifecycle (Preview vs GA) at every cycle. `1.12-RAG-01` requires an explicit screenshot showing the policy is enabled and not in Test mode.
8. **Sampling Adaptive Protection in a US Government cloud.** Adaptive Protection has **limited availability** in GCC / GCC High / DoD per Microsoft Learn `insider-risk-management-adaptive-protection`. Synthesizing a "pass" without reading the current Learn caveat is an examiner-facing misstatement. `1.12-AP-01` is **N/A in US Gov clouds** with a signed exception and a documented compensating-controls posture (CC, Audit, DLP, MDA, Sentinel UEBA).
9. **Forensic Evidence 120-day data loss.** A clip captured today is **gone in 120 days** unless exported. There is no Microsoft-published intermediate alert at day 90 or day 110; firm-defined alerting at those marks is required. `1.12-FE-02` is a quarterly check but is **clock-driven** (track every capture's day-90 / day-110 in the clip-handoff register).
10. **Pseudonymization unmask without role + reason audit trail.** Re-identification is an Investigator action that must produce an `InsiderRiskMgmtAlertUpdated`-class row tied to the Investigator's UPN, with a documented business reason. An Auditor cannot unmask. `1.12-PSEUD-01` and `1.12-NEG-03` together establish the positive and negative tests.
11. **Mistaking Triage Agent recommendations for human supervision under FINRA 25-07.** The Triage Agent (Security Copilot–powered, lifecycle Preview/GA-on-Learn-at-write-time) is decision support — it prioritizes alerts but does not substitute for the Tier-1 / Tier-2 supervisory decision required by FINRA 25-07 (which expects supervision of the AI agent itself at parity with employees). Attesting Triage Agent prioritization as the supervisory act conflates the model with the supervisor.
12. **Confusing Risky Agents (default-applied) with Risky AI usage (template-created).** They are different policies with different prerequisites: Risky Agents targets agents (Microsoft 365 Copilot agents, Copilot Studio agents, Microsoft Foundry agents) and is applied by default; Risky AI usage targets human prompts on Copilot / Microsoft Copilot / other AI surfaces and requires the browser extension. Treating one as evidence of the other produces a coverage gap. `1.12-RAI-01` and `1.12-RAG-01` require distinct alert attribution in the payload.
13. **Using PowerShell to author or mutate IRM policies where Learn does not document a supported surface.** The primary policy create / edit operations are performed in the Microsoft Purview portal; PowerShell is used for read-side inventory, role-group enumeration, audit search, and `New-ComplianceCase -CaseType InsiderRisk` (verify cmdlet syntax on Learn at write time). Attempting unsupported PowerShell mutations either fails silently or produces an inconsistent state with no audit row tied to the actor.
14. **Wrong-shell trap for compliance-case cmdlets.** `New-ComplianceCase` lives in **Security & Compliance PowerShell** (`Connect-IPPSSession`), not Exchange Online PowerShell. The wrong shell returns `CommandNotFoundException`. Pre-flight §2.3 records the connection URI of every shell used in the cycle.
15. **Skipping state-law notice posture for Forensic Evidence.** Connecticut, Delaware, New York, and several other states impose employee-monitoring notice requirements that are triggered by visual activity capture. Enabling Forensic Evidence without Privacy / Legal sign-off is a compliance defect independent of any FINRA / SEC consideration. `1.12-FE-01` requires the signed state-law-notice record as evidence.

---

## 9. Cross-links

- [Control 1.5 — DLP and Sensitivity Labels](../1.5/verification-testing.md) — DLP signals feeding `Data leaks` template; sensitivity-label state for priority content.
- [Control 1.6 — Grounding Data Protection / DSPM for AI](../1.6/verification-testing.md) — DSPM-for-AI signals feed Risky AI usage and Risky Agents.
- [Control 1.7 — Purview Audit Configuration](../1.7/verification-testing.md) — Unified audit ingestion and retention horizons; required for `1.12-UAL-01` and `1.12-AUDIT-01` to produce evidence.
- [Control 1.9 — Records Retention and Immutability](../1.9/verification-testing.md) — **The records-retention plane.** IRM is **not** the records store; Forensic Evidence clips and other IRM artifacts that must be retained beyond their working lifespan are handed off to Control 1.9 (or to eDiscovery (Premium) for in-matter holds).
- [Control 1.10 — Communication Compliance Monitoring](../1.10/verification-testing.md) — Companion supervisory signal; CC matches feed IRM risky-user indicators and IRM cases can reference CC `Pending` items.
- [Control 2.6 — Model Risk Management (OCC 2011-12 / SR 11-7)](../2.6/verification-testing.md) — IRM analytics scoring, Adaptive Protection scoring, and the Triage Agent are model-driven; bring them into the firm's model inventory, validation, and ongoing-monitoring program.
- [Control 2.12 — Supervision and Oversight (FINRA 3110 / 25-07)](../2.12/verification-testing.md) — Supervisory population definition source and AI-agent supervision linkage.
- [Control 3.1 — Identity and Access Foundations](../3.1/verification-testing.md) — Source of truth for the six IRM role groups' membership, PIM activation, and AU scoping.
- **FSI Incident Handling** — NYDFS 23 NYCRR 500 §500.17(a) 72-hour cybersecurity-event clock; IRM-derived determinations may trigger this clock (cross-link from the troubleshooting playbook to the firm's Incident Handling plan).
- [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md) — Sovereign endpoints, mutation safety, evidence emit, and module pinning conventions (cited in §2.3 and §5).
- [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Troubleshooting](troubleshooting.md).

---

[Back to Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md)

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
