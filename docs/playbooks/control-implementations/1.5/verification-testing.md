# Control 1.5 — Verification & Testing: DLP and Sensitivity Labels

> Verification procedures for [Control 1.5 — Data Loss Prevention (DLP) and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md). Run each test on the cadence in §1, capture evidence per §3, and complete the attestation in §4 each cycle.
>
> **Scope of this playbook:** Microsoft Purview DLP enforcement on the **Microsoft 365 Copilot and Copilot Chat** location, sensitivity labels (file, email, container), service-side auto-labeling, Adaptive Protection, Endpoint DLP, and the **classification surface** of Power Platform data policies as it applies to Copilot Studio agents. Connector classification mechanics in depth (Business / Non-Business / Blocked taxonomy, HTTP endpoint filtering allow-list authoring) are verified under [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md). This playbook only re-verifies that the Power Platform data policy *exists, is in scope, and classifies the AI-related connectors as Control 1.5 expects*.

---

## 1. Re-Verification Cadence

DLP for the Copilot location, label propagation behavior, and Adaptive Protection signals are non-static — Microsoft ships connector and classifier additions, retention horizons drift with license changes, and rule shape can be silently broken by the **same-rule SIT+label restriction**. Each test runs on its own cadence rather than a single annual binder refresh.

| Test ID | Frequency | Owner role | Evidence retention | Regulatory driver |
|---|---|---|---|---|
| T-DLP-AI-Activation-01 | Weekly | Purview Compliance Admin | 7 years (broker-dealer) / 6 years (other FSI) | FINRA 4511, FINRA 3110, SEC Reg S-P §248.30 |
| T-License-Entitlement-02 | Monthly | Entra Global Admin (read) + Purview Compliance Admin | 7 years | SEC Reg S-P, GLBA 501(b) |
| T-Custom-Template-Inventory-03 | Monthly | Purview Compliance Admin | 7 years | FINRA 3110, SOX 404 |
| T-DLP-AI-Custom-SIT-04 | Monthly (preview status) | Purview Compliance Admin | 7 years | FINRA 4511, GLBA 501(b) |
| T-Label-Propagation-05 | Weekly | Purview Compliance Admin | 7 years | SEC Reg S-P, FINRA 4511 |
| T-AutoLabel-Scope-06 | Quarterly | Purview Compliance Admin | 7 years | SOX 404, FINRA 3110 |
| T-Container-Label-07 | Quarterly | Purview Compliance Admin | 7 years | GLBA 501(b), SEC Reg S-P |
| T-Adaptive-Protection-Threshold-08 | Quarterly (Commercial / GCC only) | Purview Compliance Admin + IRM Analyst | 7 years | FINRA 3110, OCC 2011-12 / Fed SR 11-7 |
| T-PPDLP-Connector-Class-09 | Monthly | Power Platform Admin | 7 years | FINRA 4511, SOX 404 |
| T-Endpoint-DLP-10 | Quarterly | Defender Endpoint Admin + Purview Compliance Admin | 7 years | GLBA 501(b), SEC Reg S-P |
| T-Audit-Pipeline-11 | Weekly | Purview Audit Admin | 7 years | FINRA 4511, SEC 17a-4(f) |
| T-Negative-NotInScope-12 | Quarterly | Purview Compliance Admin | 7 years | FINRA 3110 (scope clarity) |
| **On-change** | After any DLP rule change, label change, license SKU change, IRM tier change, or connector inventory delta — re-run any affected test within the propagation window plus 24h | Change requester | n/a | n/a |
| **On-incident** | Preserve full evidence per [troubleshooting playbook](troubleshooting.md); freeze the policy, capture `Get-DlpCompliancePolicy` and `Get-DlpComplianceRule` JSON | Incident commander | per legal hold | n/a |

> **All evidence files must carry a UTC timestamp.** Local-time evidence is rejected at audit.

---

## 2. Test Catalog

Each test is deterministic: a named test user, a known input, and an asserted output measured against a Microsoft-documented signal (cmdlet output, audit `RecordType`, label GUID). All tests assume a **non-production test boundary** (test tenant, test OU, or quarantined Zone 2 environment) and that the **≥ 4-hour propagation window** for the Microsoft 365 Copilot and Copilot Chat location has been observed since the last policy edit.

> **Wrong-shell trap (applies to every PowerShell step below).** DLP cmdlets live in **Security & Compliance PowerShell** (`Connect-IPPSSession`), not Exchange Online (`Connect-ExchangeOnline`). Exchange Online silently returns `False` / empty for `Get-DlpCompliancePolicy` and related cmdlets. Always start a transcript and confirm `(Get-ConnectionInformation).ConnectionUri` matches an `*.compliance.protection.outlook.(com|us)` host before running any test.

### T-DLP-AI-Activation-01 — Block-by-label deterministic activation in Test mode

**Objective.** Confirm that a published Custom-template DLP policy with the Microsoft 365 Copilot and Copilot Chat location, in **Test with notifications** mode, deterministically activates against a labeled grounding file for a named test user and writes one or more rows to the unified audit log.

**Preconditions.**
- Named test user `dlp-test-01@<tenant>` is M365 Copilot–licensed.
- Test SharePoint document `DLP-AI-Activation-Source.docx` carries the **Highly Confidential** sensitivity label (label GUID `<HCL-GUID>`).
- DLP policy `1.5-Copilot-Block-By-Label-TEST` exists, scoped to the Microsoft 365 Copilot and Copilot Chat location, in `Test with notifications` mode, with one rule referencing the `<HCL-GUID>` label and a Block action.
- Last edit to the policy was ≥ 4 hours ago (record the edit UTC timestamp in the tester log).

**Steps.**
1. Record `Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mm:ssZ'` as `T0`.
2. From Security & Compliance PowerShell:
   ```powershell
   Connect-IPPSSession -UserPrincipalName auditor@<tenant>
   Get-DlpCompliancePolicy -Identity '1.5-Copilot-Block-By-Label-TEST' | Format-List Name,Mode,Workload,Enabled
   Get-DlpComplianceRule -Policy '1.5-Copilot-Block-By-Label-TEST' | Format-List Name,Workload,Disabled,AdvancedRule
   ```
3. As `dlp-test-01`, in Microsoft 365 Copilot Chat, issue the prompt:
   `Summarize DLP-AI-Activation-Source.docx in three bullet points.`
4. Wait 30 minutes (Copilot audit ingestion floor), then from Security & Compliance PowerShell:
   ```powershell
   Search-UnifiedAuditLog -StartDate $T0 -EndDate (Get-Date) `
     -UserIds 'dlp-test-01@<tenant>' `
     -RecordType 'ComplianceDLPSharePoint','ComplianceDLPExchange' `
     -ResultSize 50 | Export-Csv -NoTypeInformation .\T-DLP-AI-Activation-01-evidence.csv
   ```

**Expected result.**
- Step 2: `Workload` includes `Applications` (the API-name for the Copilot location); `Mode = TestWithNotifications`; rule's `AdvancedRule` JSON contains the `<HCL-GUID>` label reference.
- Step 3: Copilot returns either a policy-tip warning or a refusal consistent with Test-mode notifications.
- Step 4: CSV contains ≥ 1 row whose `AuditData` JSON includes `PolicyId` matching the test policy and a `SensitiveInfoTypeData`/`SensitivityLabelEventData` reference to `<HCL-GUID>`.

**Pass criteria (binary).** All three of: (a) cmdlet shape matches; (b) prompt produced documented Copilot behavior; (c) ≥ 1 audit row attributable to `dlp-test-01` within the window.

**Evidence collected.** PowerShell transcript (`.txt`), policy + rule JSON exports (`.json`), Copilot UI screenshot with UTC clock visible (`.png`), audit CSV (`.csv`), tester log (`.md`). One SHA-256 sidecar per file.

---

### T-License-Entitlement-02 — Microsoft 365 E5 / E5 Compliance license verification for in-scope users

**Objective.** Confirm every user in scope of the Copilot DLP policy carries Microsoft 365 E5, **or** Microsoft 365 E5 Compliance, **or** the equivalent standalone bundle that includes Purview DLP for Copilot.

**Preconditions.** Microsoft Graph PowerShell SDK installed; `Directory.Read.All` and `User.Read.All` granted; the policy's user/group scope exported to `InScopeUsers.csv`.

**Steps.**
1. Record `T0` UTC.
2. ```powershell
   Connect-MgGraph -Scopes 'Directory.Read.All','User.Read.All'
   $required = @('SPE_E5','M365_E5_COMPLIANCE','INFORMATION_PROTECTION_COMPLIANCE')  # accept any
   $inScope  = Import-Csv .\InScopeUsers.csv
   $gaps = foreach ($u in $inScope) {
     $skus = (Get-MgUserLicenseDetail -UserId $u.UserPrincipalName).SkuPartNumber
     if (-not ($skus | Where-Object { $required -contains $_ })) {
       [pscustomobject]@{ Upn=$u.UserPrincipalName; Skus=($skus -join ';') }
     }
   }
   $gaps | Export-Csv .\T-License-Entitlement-02-gaps.csv -NoTypeInformation
   ```

**Expected result.** `$gaps` is empty.

**Pass criteria.** `$gaps.Count -eq 0`. Any non-zero count is a fail because under-licensed users do not generate enforceable Copilot DLP signals — silent under-coverage.

**Evidence collected.** Gap CSV (even if empty, with header row), transcript, tester log. SHA-256 sidecars.

---

### T-Custom-Template-Inventory-03 — Custom-template policies with Copilot location and rule shape

**Objective.** Inventory every DLP policy that targets the Microsoft 365 Copilot and Copilot Chat location and confirm the **two-rule shape** (one rule for SIT-based blocking, one rule for label-based blocking) — a proxy for "policy was authored from the Custom template" because the Standard templates do not expose this location.

**Preconditions.** Security & Compliance PowerShell session; Purview Compliance Admin role.

**Steps.**
1. Record `T0` UTC.
2. ```powershell
   $copilotPolicies = Get-DlpCompliancePolicy |
     Where-Object { $_.Workload -match 'Applications' }
   $report = foreach ($p in $copilotPolicies) {
     $rules = Get-DlpComplianceRule -Policy $p.Name
     [pscustomobject]@{
       Policy        = $p.Name
       Mode          = $p.Mode
       Enabled       = $p.Enabled
       RuleCount     = $rules.Count
       SitRule       = ($rules | Where-Object { $_.AdvancedRule -match 'SensitiveType' }).Name
       LabelRule     = ($rules | Where-Object { $_.AdvancedRule -match 'SensitivityLabel' }).Name
       SameRuleViol  = [bool]($rules | Where-Object { $_.AdvancedRule -match 'SensitiveType' -and $_.AdvancedRule -match 'SensitivityLabel' })
     }
   }
   $report | Export-Csv .\T-Custom-Template-Inventory-03.csv -NoTypeInformation
   ```

**Expected result.** Each policy returns `RuleCount ≥ 1`. For policies that exercise both SIT and label conditions, `SitRule` and `LabelRule` are **different** rule names and `SameRuleViol = False`.

**Pass criteria.** No policy has `SameRuleViol = True`. Every policy intended for production has `Enabled = True` and `Mode` is either `TestWithNotifications` (during validation) or `Enable` (post-validation).

**Evidence collected.** Inventory CSV, full `Get-DlpCompliancePolicy | ConvertTo-Json -Depth 10` and `Get-DlpComplianceRule | ConvertTo-Json -Depth 10` exports, transcript. SHA-256 sidecars.

---

### T-DLP-AI-Custom-SIT-04 — SIT-based block in Copilot prompt (preview)

**Objective.** Confirm that when a SIT (e.g., **U.S. Bank Account Number**) appears inside a user prompt to Microsoft 365 Copilot Chat, the SIT-based rule activates the configured action.

> **Preview status.** SIT-on-prompt blocking for the Copilot location is documented by Microsoft Learn as **preview** as of this revision. Record the preview status in the tester log; do **not** treat this control as the sole Zone 3 safeguard for prompt-side data exfiltration. See the Copilot DLP capability matrix in Control 1.5 §Capability matrix.

**Preconditions.** Test policy `1.5-Copilot-Block-By-SIT-TEST` exists with a single rule referencing the U.S. Bank Account Number SIT (or organization-equivalent). Policy is in Test mode and ≥ 4h post-edit.

**Steps.**
1. Record `T0` UTC.
2. As `dlp-test-01`, paste a sanitized fake account number in the format the SIT recognizes into Copilot Chat with prompt: `Validate this account: <fake-acct>`.
3. Wait 30 minutes; run `Search-UnifiedAuditLog` as in T-DLP-AI-Activation-01 with `RecordType ComplianceDLPSharePoint`, `ComplianceDLPExchange`.

**Expected result.** Audit returns ≥ 1 row whose `AuditData` references the SIT name (`Sensitive Information Type`).

**Pass criteria.** ≥ 1 row, OR — if zero — a documented note in the tester log linking to the current Microsoft Learn preview status if the capability is not yet rolled out to the test tenant. Document, do not assume failure.

**Evidence collected.** Transcript, screenshot with UTC, audit CSV, preview-status note. SHA-256 sidecars.

---

### T-Label-Propagation-05 — Apply label to SPO doc, query Copilot, verify block + audit

**Objective.** Confirm end-to-end propagation: label applied to a SharePoint file → Copilot DLP rule activates on next prompt that grounds on that file → audit row written.

**Preconditions.** `T-DLP-AI-Activation-01` policy in place. Test file `Label-Propagation-Source.docx` initially **unlabeled**.

**Steps.**
1. Record `T0` UTC.
2. As `dlp-test-01`, prompt Copilot: `Summarize Label-Propagation-Source.docx.` Confirm normal (unblocked) response.
3. Apply Highly Confidential label to the file (Microsoft 365 web UI or `Set-Label` API).
4. Wait the propagation floor: ≥ 30 minutes for label, ≥ 4 hours since last DLP policy edit (already met in T0 baseline).
5. Repeat the prompt from step 2.
6. After 30 minutes, run the same `Search-UnifiedAuditLog` query.

**Expected result.** Step 2: response returned normally. Step 5: response blocked or warned per the rule's action. Step 6: ≥ 1 audit row referencing `<HCL-GUID>`.

**Pass criteria.** All three observations match.

**Evidence collected.** Two transcripts (pre-label and post-label Copilot UI screenshots, both with UTC clock), audit CSV, label history export from `Get-Label`. SHA-256 sidecars.

---

### T-AutoLabel-Scope-06 — Auto-labeling location restriction

**Objective.** Confirm that the only locations selectable when authoring an auto-labeling policy are **SharePoint Online**, **OneDrive for Business**, and **Exchange Online**. There is no "AI interactions" location and the absence is itself the asserted evidence.

**Preconditions.** Purview Compliance Admin in `purview.microsoft.com` (Commercial), `purview.microsoft.us` (GCC / GCC High), or `compliance.apps.mil` (DoD).

**Steps.**
1. Record `T0` UTC.
2. Navigate **Information protection → Auto-labeling policies → Create auto-labeling policy**.
3. Step through the wizard to **Choose locations**.
4. Capture a screenshot showing the selectable locations.
5. From Security & Compliance PowerShell:
   ```powershell
   Get-AutoSensitivityLabelPolicy | Select-Object Name,Workload | Format-Table
   ```

**Expected result.** Wizard exposes only SharePoint sites, OneDrive accounts, and Exchange Online. `Workload` values are constrained to `SharePoint`, `OneDrive`, and `Exchange`. **No** value of `Applications` (Copilot location) appears.

**Pass criteria.** Both conditions met.

**Evidence collected.** Wizard screenshot with UTC, cmdlet CSV. SHA-256 sidecars.

---

### T-Container-Label-07 — Container label does not label files inside

**Objective.** Confirm that a sensitivity label applied to a Microsoft 365 Group / Team / SharePoint site governs container-level settings only and does **not** label files inside.

**Preconditions.** Test SharePoint site `DLP-Container-Test` has the **Confidential** container label. A test file `Inside-Container.docx` was uploaded **without** explicit labeling.

**Steps.**
1. Record `T0` UTC.
2. Verify container label:
   ```powershell
   Get-SPOSite -Identity https://<tenant>.sharepoint.com/sites/DLP-Container-Test | Select-Object Url,SensitivityLabel
   ```
3. Inspect file label via Graph or via Microsoft 365 web UI **Sensitivity** indicator on the file card.
4. As `dlp-test-01`, prompt Copilot to ground on `Inside-Container.docx`.

**Expected result.** Step 2: site `SensitivityLabel` returns the Confidential GUID. Step 3: file `SensitivityLabel` is **null / unset**. Step 4: Copilot returns the file content (no label-based DLP block fires) — confirming inheritance does not occur.

**Pass criteria.** All three conditions met.

**Evidence collected.** Cmdlet output, file properties screenshot, Copilot transcript with UTC. SHA-256 sidecars.

---

### T-Adaptive-Protection-Threshold-08 — Deterministic IRM tier change → DLP rule activation

**Objective.** Confirm that an Adaptive Protection–enabled rule increases enforcement when a user is moved into the **Elevated** insider risk tier.

> **Sovereign N/A.** Adaptive Protection is **not at parity in GCC High and DoD** as of this revision. In those clouds, **skip** this test and record a documented exception. GCC tenants: verify parity in your tenant before treating as in-scope.

**Preconditions.** Insider Risk Management is enabled with a baseline window completed. A test policy contains a rule whose action escalates (e.g., from `Audit` to `Block`) when the user's tier is `Elevated`. Test user is `dlp-test-08@<tenant>`.

**Steps.**
1. Record `T0` UTC; capture `dlp-test-08`'s current IRM tier in Purview → Insider risk management → Users.
2. Trigger a tier change either by simulated activity per IRM playbook or via documented IRM admin override.
3. Wait the IRM-to-Adaptive-Protection propagation window documented by Microsoft Learn (record the wait).
4. As `dlp-test-08`, issue the test prompt that previously produced an `Audit` outcome at `Low` tier.
5. After 30 minutes, run `Search-UnifiedAuditLog` and capture the `AuditData` action.

**Expected result.** Pre-change action = `Audit`; post-change action = `Block` (or whichever escalation the rule defines).

**Pass criteria.** Post-change audit row carries the escalated action.

**Evidence collected.** IRM tier screenshots (pre + post, UTC visible), Copilot transcripts (pre + post), audit CSV, IRM event export. SHA-256 sidecars. **GCC High / DoD:** signed exception note in lieu of evidence.

---

### T-PPDLP-Connector-Class-09 — Power Platform data policy classification reflects expected groups

**Objective.** Confirm that a Power Platform data policy in scope of Copilot Studio agents classifies the AI-related connector inventory into the expected **Business / Non-Business / Blocked** groups for the target zone, and that the **API-returned values** match the **portal-displayed labels** after API↔UI normalization.

> **Scope boundary.** Connector classification *mechanics*, the full connector matrix, and HTTP endpoint filtering allow-list authoring are verified under [Control 1.4](../1.4/verification-testing.md). This test re-verifies only that, *for the AI-related connectors that Control 1.5 cares about*, classifications match the zone profile.

**Preconditions.** Power Platform Admin role; tenant's data policy ID known; expected classification map for the target zone exported to `ExpectedZone3.csv` (columns: `ConnectorName`, `ExpectedGroup`).

**Steps.**
1. Record `T0` UTC.
2. ```powershell
   Add-PowerAppsAccount -Endpoint prod    # or usgov | usgovhigh | dod
   $policy = Get-DlpPolicy -PolicyName <policyId>
   $live = $policy.connectorGroups | ForEach-Object {
     $group = $_.classification          # API: 'Confidential' | 'General' | 'Blocked'
     $_.connectors | ForEach-Object {
       [pscustomobject]@{
         ConnectorName = $_.name
         ApiGroup      = $group
         UiGroup       = switch ($group) {
           'Confidential' { 'Business' }
           'General'      { 'Non-Business' }
           'Blocked'      { 'Blocked' }
           default        { $group }
         }
       }
     }
   }
   $expected = Import-Csv .\ExpectedZone3.csv
   $diff = Compare-Object $live $expected -Property ConnectorName,UiGroup -IncludeEqual:$false
   $diff | Export-Csv .\T-PPDLP-Connector-Class-09-diff.csv -NoTypeInformation
   ```

**Expected result.** `$diff` is empty. (API `Confidential` ↔ portal **Business** is the documented normalization; treat any other unexpected value as a fail.)

**Pass criteria.** `$diff.Count -eq 0` for the AI-related connector subset (AI Builder GPT/Document Processing, Copilot Studio Topics/Skills/Knowledge, HTTP with Microsoft Entra ID, HTTP Webhook, Direct Line, Microsoft Teams Channel, SharePoint Channel, Custom Website Channel — verify the live catalog rather than relying on a closed list).

**Evidence collected.** Diff CSV (with header row even if empty), full policy JSON export, transcript. SHA-256 sidecars.

---

### T-Endpoint-DLP-10 — Onboarded device blocks copy of Highly Confidential file to USB

**Objective.** Confirm an Endpoint DLP rule blocks copy of a Highly Confidential–labeled file from a Defender-onboarded Windows device to removable USB.

> Endpoint DLP capability and rule shapes vary; some sub-features may be in preview. Record the preview status in the tester log.

**Preconditions.** Windows 11 test device onboarded to Microsoft Defender for Endpoint and visible in Endpoint DLP **Devices** inventory. Endpoint DLP policy includes a rule blocking copy-to-USB for the Highly Confidential label. Test file `Endpoint-USB-Source.docx` carries the Highly Confidential label.

**Steps.**
1. Record `T0` UTC.
2. On the test device, sign in as `dlp-test-10@<tenant>`; insert a USB drive.
3. Attempt to copy `Endpoint-USB-Source.docx` to the USB drive (File Explorer drag).
4. Capture the policy-tip / block dialog (UTC visible in screenshot).
5. After 30 minutes, run:
   ```powershell
   Search-UnifiedAuditLog -StartDate $T0 -EndDate (Get-Date) `
     -UserIds 'dlp-test-10@<tenant>' -RecordType 'DLPEndpoint' -ResultSize 50 |
     Export-Csv .\T-Endpoint-DLP-10.csv -NoTypeInformation
   ```

**Expected result.** Step 3: copy blocked. Step 5: ≥ 1 audit row with `RecordType = DLPEndpoint`.

**Pass criteria.** Both observations met.

**Evidence collected.** Block dialog screenshot, audit CSV, device onboarding state export, transcript. SHA-256 sidecars.

---

### T-Audit-Pipeline-11 — Search-UnifiedAuditLog returns DLP events using correct RecordTypes

**Objective.** Confirm the audit pipeline surfaces DLP events under the documented `RecordType` values and that nothing is silently dropped.

**Preconditions.** Audit ingestion enabled (verify via Control 1.7 T1). Tests T-DLP-AI-Activation-01, T-Label-Propagation-05, and T-Endpoint-DLP-10 have run within the last 7 days.

**Steps.**
1. Record `T0` UTC.
2. ```powershell
   $start = (Get-Date).AddDays(-7)
   $end   = Get-Date
   foreach ($rt in 'ComplianceDLPSharePoint','ComplianceDLPExchange','DLPEndpoint') {
     $rows = Search-UnifiedAuditLog -StartDate $start -EndDate $end -RecordType $rt -ResultSize 5000
     "$rt : $($rows.Count) rows" | Tee-Object -FilePath .\T-Audit-Pipeline-11-counts.txt -Append
     $rows | Export-Csv ".\T-Audit-Pipeline-11-$rt.csv" -NoTypeInformation
   }
   ```

**Expected result.** Each in-scope `RecordType` returns ≥ 1 row corresponding to the recent test activity. (`DLPEndpoint` count may be 0 if no Endpoint DLP tests have run in window — document the absence.)

**Pass criteria.** Every `RecordType` for which a test was executed in window returns ≥ 1 row attributable to the test user.

**Evidence collected.** Three CSVs, count summary, transcript. SHA-256 sidecars.

---

### T-Negative-NotInScope-12 — Confirm DLP does not fire outside documented scope

**Objective.** Document the **negative space** of the Copilot DLP location so that admins do not chase phantom failures or assume coverage that Microsoft does not provide.

**Preconditions.** Standard test policy from T-DLP-AI-Activation-01 in place.

**Cases.**

| Sub-case | Scenario | Expected outcome |
|---|---|---|
| 12a | User uploads a Highly Confidential file *directly into a Copilot prompt* (rather than grounding via SharePoint reference) | Behavior follows documented Copilot upload handling; the SPO/EXO label-based DLP rule may **not** fire because the source is not SharePoint or Exchange. Document the observed behavior; do not assert as a control failure. |
| 12b | Calendar invites carrying labeled attachments are referenced from Copilot | Calendar invites are not in scope of the EXO DLP location for Copilot rules; no rule fires. Documented as scope limit. |
| 12c | Audit search for DLP events with `EndDate` before **2025-01-01** | Returns zero rows attributable to the Copilot location for periods predating GA of that location in the tenant. Documented as expected. |
| 12d | An auto-labeling policy authored to target "AI interactions" | **Not creatable** — the location does not exist. Screenshot of wizard with no such option (cross-reference to T-AutoLabel-Scope-06). |

**Pass criteria.** Each sub-case behaves as documented and is recorded in the tester log with a short explanation. Failure = an unexpected DLP activation, which would indicate scope drift and warrants investigation.

**Evidence collected.** Tester log entries with screenshots and audit search outputs per sub-case. SHA-256 sidecars.

---

## 2A. Copilot Studio agent — connector use (limited scope)

The narrow Copilot-Studio-agent–specific assertions retained here cover *agent-time* connector behavior that is observable through Control 1.5's signal surface (Purview audit). Full connector-classification verification lives in [Control 1.4](../1.4/verification-testing.md).

| Mini-test | Assertion | Signal |
|---|---|---|
| 1.5-AGENT-A | A Copilot Studio agent attempting to use a `Blocked` connector at runtime fails fast | PPAC analytics show a connector-blocked event for the agent run; correlated Purview audit row attributable to the agent's service principal |
| 1.5-AGENT-B | A Copilot Studio agent using an `HTTP with Microsoft Entra ID` connector pointed at a non-allowlisted endpoint fails | PPAC runtime error; agent run telemetry shows endpoint-filtering denial (preview status — record) |

These two mini-assertions are **observational** — they do not replace the connector-classification deterministic suite under Control 1.4.

---

## 3. Sovereign Cloud Variant

For each test above, substitute the cloud-specific endpoints and record the cloud in the tester log header. **Adaptive Protection (T-Adaptive-Protection-Threshold-08) is N/A in GCC High and DoD** as of this revision — capture a signed exception in lieu of evidence.

| Step type | Commercial | GCC | GCC High | DoD |
|---|---|---|---|---|
| Purview portal | `purview.microsoft.com` | `purview.microsoft.com` (verify) | `purview.microsoft.us` | `compliance.apps.mil` |
| Exchange Online PowerShell | `Connect-ExchangeOnline` | `Connect-ExchangeOnline -ExchangeEnvironmentName O365USGovGCCHigh` (GCC: default + tenant verification) | `Connect-ExchangeOnline -ExchangeEnvironmentName O365USGovGCCHigh` | `Connect-ExchangeOnline -ExchangeEnvironmentName O365USGovDoD` |
| Security & Compliance PowerShell | `Connect-IPPSSession` | `Connect-IPPSSession` (default) | `Connect-IPPSSession -ConnectionUri https://ps.compliance.protection.outlook.us/powershell-liveid -AzureADAuthorizationEndpointUri https://login.microsoftonline.us/common` | `Connect-IPPSSession -ConnectionUri https://l5.ps.compliance.protection.office365.us/powershell-liveid -AzureADAuthorizationEndpointUri https://login.microsoftonline.us/common` |
| Power Platform (`Add-PowerAppsAccount`) | `-Endpoint prod` | `-Endpoint usgov` | `-Endpoint usgovhigh` | `-Endpoint dod` |
| Microsoft Graph (`Connect-MgGraph`) | default | `-Environment USGov` | `-Environment USGov` (verify) | `-Environment USGovDoD` |
| Adaptive Protection (T-08) | In scope | In scope (verify parity) | **N/A — record exception** | **N/A — record exception** |

> See `docs/playbooks/_shared/powershell-baseline.md` for the canonical sovereign-cloud parameter reference.

---

## 4. Evidence Pack

Every cycle, produce and archive the artifacts below. **File naming convention:**

```
<TestID>-<UTC-yyyyMMddTHHmmssZ>-<artifact>.<ext>
e.g., T-DLP-AI-Activation-01-20260415T141207Z-audit.csv
      T-DLP-AI-Activation-01-20260415T141207Z-audit.csv.sha256
```

**SHA-256 manifest example (`Control-1.5_Manifest_<UTC>.txt`):**

```text
# Control 1.5 — Evidence Manifest
# Generated: 2026-04-15T14:30:00Z
# Tenant:   <tenantId>     Cloud: Commercial     Zone: 3
#
3a7b...c91   T-DLP-AI-Activation-01-20260415T141207Z-audit.csv
9f12...88a   T-DLP-AI-Activation-01-20260415T141207Z-policy.json
4c0d...771   T-DLP-AI-Activation-01-20260415T141207Z-rule.json
...
```

Generate with:

```powershell
Get-ChildItem .\evidence\1.5\<cycle>\ -File -Exclude *.sha256 |
  Get-FileHash -Algorithm SHA256 |
  ForEach-Object { "$($_.Hash.ToLower())   $((Split-Path $_.Path -Leaf))" } |
  Set-Content ".\evidence\1.5\<cycle>\Control-1.5_Manifest_$(Get-Date -AsUTC -Format 'yyyyMMddTHHmmssZ').txt"
```

**Required artifacts per cycle.**

| # | Artifact | Source test |
|---|---|---|
| 1 | `policy.json` + `rule.json` exports | T-01, T-03 |
| 2 | Activation audit CSV (`ComplianceDLPSharePoint`, `ComplianceDLPExchange`) | T-01, T-04, T-05 |
| 3 | Copilot UI screenshot with UTC clock | T-01, T-04, T-05, T-07 |
| 4 | License gap CSV (header row even if empty) | T-02 |
| 5 | Custom-template inventory CSV | T-03 |
| 6 | Auto-label policy wizard screenshot + `Get-AutoSensitivityLabelPolicy` CSV | T-06 |
| 7 | Container vs file label evidence (cmdlet output + UI screenshot) | T-07 |
| 8 | Adaptive Protection pre/post screenshots + audit CSV — **or** signed sovereign exception | T-08 |
| 9 | Power Platform classification diff CSV + full policy JSON | T-09 |
| 10 | Endpoint DLP block dialog screenshot + `DLPEndpoint` audit CSV | T-10 |
| 11 | Per-`RecordType` audit pipeline CSVs + counts file | T-11 |
| 12 | Negative-test tester log with sub-case evidence | T-12 |
| 13 | PowerShell transcript per test | All |
| 14 | Manifest `.txt` with SHA-256 of every artifact | All |

**Retention guidance.**

- **FINRA Rule 4511 / SEC 17a-4(b):** retain for ≥ 6 years.
- **SEC 17a-4(f) (October 2022 amendments):** for broker-dealer evidence, retain via the audit-trail alternative (paired electronic record + serial-number index + digital signature) **or** WORM media. **Audit log evidence held inside Purview** is governed by Microsoft's audit retention configuration (Control 1.7) — supplemental evidence stored *outside* Purview (CSV/JSON/PNG/MD exports, transcripts, manifests) **must** be placed on WORM-treated storage per the firm's retention policy.
- **GLBA 501(b) / SEC Reg S-P:** retain customer-information related DLP evidence aligned to the firm's privacy retention schedule.
- **Default for this control:** 7 years on WORM-treated storage with paired SHA-256 sidecars and a signed attestation per §5.

---

## 5. Attestation

```text
Control 1.5 — Data Loss Prevention (DLP) and Sensitivity Labels
Cycle:                Q____ FY____
Tenant:               _______________________________________
Cloud:                ☐ Commercial  ☐ GCC  ☐ GCC High  ☐ DoD
Governance Zone:      ☐ Zone 1  ☐ Zone 2  ☐ Zone 3
Verification window:  ____________________ UTC  →  ____________________ UTC
Evidence manifest:    Control-1.5_Manifest_____________________.txt
Manifest SHA-256:     ________________________________________________________________

I have executed the test catalog in §2 (and §2A where Copilot Studio agent
connectors are in scope) for the period above. Sovereign-variant substitutions
in §3 were applied where the tenant resides in GCC, GCC High, or DoD. The
evidence listed in §4 is archived per the retention guidance and SHA-256
sidecars match the manifest at archival time.

This evidence supports — but does not by itself establish — the firm's
compliance with:

  • FINRA Rule 4511 (record preservation for DLP enforcement and label state)
  • FINRA Rule 3110 / 25-07 (supervisory system over AI-surfaces)
  • SEC Reg S-P §248.30 (privacy and detection support for events that may
    trigger customer notification)
  • SEC 17a-4(f) (record-format / WORM expectations, paired with Control 1.7)
  • GLBA 501(b) (safeguards for customer information processed by AI)
  • SOX 404 (IT general controls over AI data flows)
  • OCC 2011-12 / Federal Reserve SR 11-7 (model risk management ongoing
    monitoring expectations as they apply to Copilot enforcement signals)

This attestation does not constitute a legal determination. Reportability
decisions remain with Compliance and Legal counsel.

Control owner (printed name): _______________________________________
Role:                         _______________________________________
Signature:                    _______________________________________
Date (UTC):                   _______________________________________
```

---

## 6. Anti-Patterns and Known Traps

- **Standard-vs-Custom template trap.** The Microsoft 365 Copilot and Copilot Chat location is exposed **only** when authoring from the **Custom** template. Standard templates (Financial, Privacy, etc.) silently omit this location. T-Custom-Template-Inventory-03 is the early-warning signal.
- **Same-rule SIT + label rejection.** A single rule cannot combine SIT conditions and sensitivity label conditions for the Copilot location. Author **two separate rules** in the same policy. T-Custom-Template-Inventory-03 flags `SameRuleViol = True`.
- **"AI interactions" is not an auto-labeling location.** Service-side auto-labeling targets only SharePoint Online, OneDrive for Business, and Exchange Online. Anyone proposing an "AI interactions" auto-label scope is working from outdated or fabricated guidance — see T-AutoLabel-Scope-06.
- **The 4-hour propagation window is real and must be observed.** Validation runs inside the window produce inconclusive (not failing) results. Record the policy edit timestamp in `T0` for every test and abort if `now − last_edit < 4h`.
- **Restricted Administrative Unit limitation.** The Copilot DLP location does **not** support administrative units. An admin scoped to a Restricted AU cannot create or edit a policy that targets the Copilot location — use a tenant-scoped Purview Compliance Admin role for these tests, and document the role used in the tester log.
- **Wrong shell — Exchange Online vs. Security & Compliance.** `Get-DlpCompliancePolicy`, `Get-DlpComplianceRule`, `Search-UnifiedAuditLog`, `Get-AutoSensitivityLabelPolicy`, and `Get-Label` live in Security & Compliance PowerShell (`Connect-IPPSSession`), not Exchange Online. The wrong shell returns silent zero / `False` results — a leading cause of false-pass attestations. Confirm `(Get-ConnectionInformation).ConnectionUri` before every test.
- **Container label ≠ file label.** A container label on a Team / Group / SharePoint site does not propagate to files inside. Plan label-based DLP rules around the file/email label, not the container label. T-Container-Label-07 makes this explicit.
- **Power Platform API ↔ portal label normalization.** API `Confidential` displays as **Business** in the portal, `General` displays as **Non-Business**, `Blocked` displays as **Blocked**. Compare apples to apples in T-PPDLP-Connector-Class-09.
- **Adaptive Protection sovereign gap.** GCC High and DoD do not have Adaptive Protection at parity with Commercial as of this revision. Treat T-Adaptive-Protection-Threshold-08 as N/A in those clouds and retain a signed exception, not synthetic evidence.

---

[Back to Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md) | [Control 1.4 Verification](../1.4/verification-testing.md) | [Control 1.7 Verification](../1.7/verification-testing.md)

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
