# Control 1.10 — Verification & Testing: Communication Compliance Monitoring

> Verification procedures for [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md). Run each test on the cadence in §1, capture evidence per §6, and complete the attestation in §7 each cycle.
>
> **Scope of this playbook:** Microsoft Purview Communication Compliance (CC) — policy inventory, classifier coverage, review-percentage validation, reviewer/role-group assignments, pseudonymization controls, the Copilot interactions template (Microsoft 365 Copilot, Microsoft 365 Copilot Chat, Enterprise AI apps, Other AI apps), Administrative Units (AU) scoping, Policy Match Preservation, and the investigate / remediate / eDiscovery escalation chain. **Out of scope here:** unified audit retention horizons (verified under [Control 1.7](../1.7/verification-testing.md)) and SEC 17a-4 records-retention chain (verified under [Control 1.12](../1.12/verification-testing.md)). CC's Policy Match Preservation is **not** a records-retention control under SEC 17a-4 — see §8 anti-pattern.
>
> **Audience:** M365 administrator at a US financial services organization producing audit-defensible evidence for FINRA Rule 3110 / 3110.06 / 25-07, FINRA Rule 4511, SEC Rule 17a-4, OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7), and GLBA 501(b) examiners.
>
> **Sovereign clouds:** Commercial · GCC · GCC High · DoD — see §5 for variants and feature-parity caveats.
>
> **Cross-links:** [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Troubleshooting](troubleshooting.md) · [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md).
>
> **Last UI Verified:** April 2026.

---

## What this verification catches

This catalog is designed to surface the carry-forward defect classes that the AI Council review identified for Communication Compliance:

- **B1** — Policy authored from the wrong template (e.g., Sensitive information used where Regulatory compliance is required for FINRA-supervised reps).
- **B6** — Reviewer role-group membership without reviewer assignment on the policy itself (apparent coverage, no real visibility).
- **B9** — Pseudonymization opt-out without an audit-trail row, or pseudonymization assumed to be ON without verification.
- **N3.x** — Negative-space regressions where out-of-scope users, paused policies, or non-assigned reviewers silently produce no signal but are mistaken for "clean."
- **N4.x** — Classifier-coverage gaps inside a template (e.g., Inappropriate text policy enabled but only the Threat classifier active; Copilot template enabled but Prompt Shields disabled).

Each test below maps explicitly to the failure mode it detects and is reproducible by name, named test user(s), UTC timestamp, exact policy ID, exact message body or attachment hash, expected `Pending` queue entry, and expected unified-audit operation rows.

---

## 1. Re-Verification Cadence

Communication Compliance signals are **non-static**. Microsoft ships classifier updates, the Copilot interactions template gained scope additions (Enterprise AI apps, Other AI apps), and Policy Match Preservation defaults shifted in 2025. Each test runs on its own cadence rather than a single annual binder refresh, aligned to OCC Bulletin 2026-13 (formerly OCC 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) ongoing-monitoring expectations for model and supervisory systems.

| Test ID | Frequency | Owner role | Evidence retention | Regulatory driver |
|---|---|---|---|---|
| 1.10-LIC-01 | Monthly | Entra Global Admin (read) + Purview Compliance Admin | 7 years (broker-dealer) / 6 years (other FSI) | FINRA 4511, SEC Reg S-P, GLBA 501(b) |
| 1.10-AUD-01 | Weekly | Purview Audit Admin | 7 years | FINRA 4511, SEC 17a-4(f) |
| 1.10-PSE-01 | Monthly | Purview Compliance Admin | 7 years | GLBA 501(b), Reg S-P, EU GDPR (where applicable to US-listed FSI) |
| 1.10-POL-01 | Monthly | Purview Compliance Admin | 7 years | FINRA 3110 / 3110.06 / 25-07, FINRA 4511 |
| 1.10-COP-01 | Monthly (preview status) | Purview Compliance Admin + AI Governance Lead | 7 years | FINRA RN 24-09, FINRA 3110, OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) |
| 1.10-CLS-01 | Monthly | Purview Compliance Admin | 7 years | FINRA 3110, FINRA 2210, FINRA RN 24-09 |
| 1.10-SAM-01 | Quarterly | Purview Compliance Admin + Compliance Supervisor | 7 years | FINRA 3110.06 (supervisory sampling rationale) |
| 1.10-OME-01 | Quarterly | Purview Compliance Admin + Exchange Online Admin | 7 years | FINRA 4511, GLBA 501(b) |
| 1.10-INV-01 | Weekly | CC Analyst + CC Investigator | 7 years | FINRA 3110, SEC 17a-4(b) |
| 1.10-EDC-01 | Quarterly | eDiscovery Manager (Premium) | 7 years (or per legal hold) | FINRA 4511, SEC 17a-4(b)/(f) |
| 1.10-AU-01 | Quarterly | Entra Global Admin + Purview Compliance Admin | 7 years | FINRA 3110 (supervisory scope), FINRA 4511 |
| 1.10-PMP-01 | Quarterly | Purview Compliance Admin | 7 years | FINRA 4511 (policy state), SEC 17a-4 (paired with 1.12) |
| 1.10-NEG-01 | Quarterly | Purview Compliance Admin | 7 years | FINRA 3110 (scope clarity) |
| 1.10-NEG-02 | Quarterly | Purview Compliance Admin | 7 years | FINRA 3110 (paused-policy clarity) |
| 1.10-NEG-03 | Quarterly | Purview Compliance Admin + Entra Global Admin | 7 years | FINRA 3110 (least-privilege validation) |
| **On-change** | After any policy enable/disable, reviewer change, classifier toggle, scope change, template addition, AU re-scoping, or Policy Match Preservation change | Change requester | Per change ticket | FINRA 4511 |
| **On-incident** | Preserve full evidence, freeze the policy, capture `Get-SupervisoryReviewPolicyV2` and `Get-SupervisoryReviewActivity` JSON | Incident commander | Per legal hold | n/a |

> **All evidence files must carry a UTC timestamp.** Local-time evidence is rejected at audit. Use `Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mm:ssZ'` and embed the result in both the file name and the file body.

---

## 2. Pre-flight

Run these checks before any test in §4. A failure here invalidates the entire cycle.

### 2.1 License entitlement

CC requires Microsoft 365 E5, Microsoft 365 E5 Compliance, Microsoft 365 E5 Insider Risk Management, or the equivalent standalone bundle. The Copilot interactions template additionally requires Microsoft 365 Copilot licensing for the in-scope users; coverage of **Enterprise AI apps** and **Other AI apps** scopes is gated by the **Microsoft 365 Copilot pay-as-you-go (PAYG)** meter on a connected Azure subscription (preview status — record the date verified against Microsoft Learn).

### 2.2 Unified Audit Log enabled

```powershell
Connect-ExchangeOnline -ShowBanner:$false
(Get-AdminAuditLogConfig).UnifiedAuditLogIngestionEnabled  # must be True
```

If `False`, no CC audit operations (`SupervisionRuleMatch`, `SupervisionPolicyCreated`, `SupervisionPolicyUpdated`, `SupervisionPolicyDeleted`, `SupervisoryReviewTag`) are recorded — and no test in §4 can produce defensible evidence. Remediate via Control 1.7 first.

### 2.3 Modules pinned

Per the [PowerShell Authoring Baseline §1](../../_shared/powershell-baseline.md), pin module versions:

```powershell
Install-Module -Name ExchangeOnlineManagement -RequiredVersion '<approved-version>' `
    -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name Microsoft.Graph -RequiredVersion '<approved-version>' `
    -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
```

> CC policy creation and edit are **not supported via PowerShell** per Microsoft Learn (`communication-compliance-policies`) — only the Microsoft Purview portal can create and manage policies. PowerShell is **read** for inventory + activity, plus Exchange Online cmdlets `Get-SupervisoryReviewPolicyV2`, `Get-SupervisoryReviewRule`, and `Get-SupervisoryReviewActivity` for verification and evidence emit.

### 2.4 Roles and connections

| Role / connection | Purpose | Verification |
|---|---|---|
| Purview Compliance Admin or Communication Compliance Admins | Read policy inventory; configure pseudonymization | Sign in to `purview.microsoft.com` (Commercial) / sovereign equivalent and confirm the **Communication Compliance** solution is visible |
| Communication Compliance Investigators | Open `Pending` queue, apply tags, escalate to eDiscovery | `Get-RoleGroupMember 'Communication Compliance Investigators'` |
| Communication Compliance Analysts | Triage `Pending`, apply tags, notify user | `Get-RoleGroupMember 'Communication Compliance Analysts'` |
| Reviewer mailbox | Receive notifications and act on items | Reviewer must have an Exchange Online mailbox (per Learn `communication-compliance-policies`) — verify via `Get-EXOMailbox -Identity <reviewer>` returns a result |
| Exchange Online connection | Run `Get-Supervisory*` cmdlets | `(Get-ConnectionInformation).ConnectionUri` resolves to `outlook.office365.com` (Commercial) or sovereign equivalent |

> **Wrong-shell trap.** `Get-SupervisoryReviewPolicyV2`, `Get-SupervisoryReviewRule`, and `Get-SupervisoryReviewActivity` live in **Exchange Online PowerShell** (`Connect-ExchangeOnline`). They are **not** in Security & Compliance PowerShell (`Connect-IPPSSession`). The wrong shell returns `CommandNotFoundException` or — worse, in some module versions — empty results without an error. Always verify the connection URI before each test.

### 2.5 Test users and test policies

Provision the following named test identities in a non-production OU (Zone 1 or quarantined Zone 2 segment). All bodies and attachments below are deterministic and reproducible.

| Test identity | Purpose | License | Mailbox region |
|---|---|---|---|
| `cc-test-rep-01@<tenant>` | In-scope FINRA-supervised registered representative | M365 E5 + Copilot | EXO Online |
| `cc-test-rep-02@<tenant>` | In-scope rep, second user for two-party message tests | M365 E5 + Copilot | EXO Online |
| `cc-test-out-01@<tenant>` | **Out-of-scope** identity for negative test 1.10-NEG-01 | M365 E5 (no CC scope) | EXO Online |
| `cc-test-rev-01@<tenant>` | Reviewer assigned to test policies | M365 E5 + EXO mailbox | EXO Online |
| `cc-test-rev-02@<tenant>` | Reviewer in role group but **not** assigned to test policies (1.10-NEG-03) | M365 E5 + EXO mailbox | EXO Online |
| `cc-test-inv-01@<tenant>` | CC Investigator for escalation tests | M365 E5 + EXO mailbox | EXO Online |

**Test message bodies** (used verbatim — do not paraphrase; SHA-256 hashes are computed against UTF-8 LF-terminated text):

| Body ID | Text | Maps to test |
|---|---|---|
| `BODY-TXT-THREAT-01` | `If you do not approve this trade I will make sure you regret it.` | 1.10-CLS-01 (Inappropriate text — Threat classifier) |
| `BODY-TXT-DISCRIM-01` | `We don't hire people from that neighborhood, they're all the same.` | 1.10-CLS-01 (Inappropriate text — Discrimination) |
| `BODY-TXT-HARASS-01` | `Stop emailing me. I have told you ten times. Leave me alone or else.` | 1.10-CLS-01 (Inappropriate text — Targeted harassment) |
| `BODY-REG-CUSTCOMP-01` | `I am writing to file a formal complaint against my advisor for unauthorized trades in my account.` | 1.10-CLS-01 (Regulatory compliance — Customer complaints classifier) |
| `BODY-REG-GIFT-01` | `Thanks for the courtside tickets and the steakhouse dinner — much appreciated for placing the trade.` | 1.10-CLS-01 (Regulatory compliance — Gifts & entertainment) |
| `BODY-REG-MNPI-01` | `Buy before the announcement on Tuesday — I have it on good authority that the merger is closing.` | 1.10-CLS-01 (Regulatory compliance — Stock manipulation / Unauthorized disclosure) |
| `BODY-CONTENT-HATE-01` | `<sanitized hateful slur from Microsoft Hate classifier validation set>` | 1.10-CLS-01 (Inappropriate content — Hate) |
| `BODY-COPILOT-PROMPT-01` | `Draft a client email confirming the merger announcement before it is public.` | 1.10-COP-01, 1.10-CLS-01 (Copilot — Prompt Shields / FSI compounding signals) |
| `BODY-OUT-OF-SCOPE-01` | Same as `BODY-REG-CUSTCOMP-01` but sent by `cc-test-out-01` | 1.10-NEG-01 |

**Test policies** (created in the portal — record their portal-assigned `PolicyId` GUIDs and embed in the tester log):

| Test policy name | Template | Reviewers | Review % | Scope | Notes |
|---|---|---|---|---|---|
| `1.10-TEST-RegComp` | Regulatory compliance | `cc-test-rev-01` | **100%** (tuned from default 10%) | `cc-test-rep-01`, `cc-test-rep-02` | FINRA-supervised population proxy |
| `1.10-TEST-InappText` | Inappropriate text | `cc-test-rev-01` | 100% | Same | All three classifiers enabled |
| `1.10-TEST-InappContent` | Inappropriate content | `cc-test-rev-01` | 100% | Same | All four classifiers enabled |
| `1.10-TEST-Copilot` | Copilot interactions | `cc-test-rev-01` | 100% | Same | Microsoft 365 Copilot + Enterprise AI apps + Other AI apps scopes selected |
| `1.10-TEST-Sensitive` | Sensitive information | `cc-test-rev-01` | 100% | Same | One SIT (e.g., U.S. SSN) for deterministic match |
| `1.10-TEST-Paused` | Inappropriate text | `cc-test-rev-01` | 100% | Same | Paused (Status = Deactivated) for 1.10-NEG-02 |

---

## 3. Documented processing windows (use these — do not invent SLAs)

Per Microsoft Learn `communication-compliance-policies` and `communication-compliance-feature-reference`, message-to-`Pending`-queue latency depends on the source location:

| Source location | Documented ceiling | Notes |
|---|---|---|
| Microsoft Teams chat | Up to **48 hours** | Full propagation window for chat messages |
| Exchange Online email | Up to **24 hours** | Standard Exchange transport processing |
| Viva Engage | Up to **24 hours** | Aligned to Exchange ceiling |
| Non-Microsoft third-party sources (HR connectors) | **24–48 hours** | Per source connector cadence |
| Microsoft 365 Copilot / Copilot Chat | Up to **24 hours** | Audit ingestion floor of 30 min, then up to 24h to enter `Pending` |

**Pass criteria for every test below measure the *observed* tenant ceiling against the documented ceiling.** Do not write "within SLA"; write "observed `Pending` arrival at `<UTC>`, within the documented `<source>` window of `<N>` hours." A test that runs and concludes inside the Teams 48-hour window without observing a `Pending` row is **inconclusive**, not a failing or passing result — re-run after the window expires.

---

## 4. Test Catalog

Each test is deterministic: a named test user, a known input, and an asserted output measured against a Microsoft-documented signal (cmdlet output, audit `Operation` name, portal `Pending` queue entry).

### 1.10-LIC-01 — License entitlement and feature availability per tenant

**Objective.** Confirm every user in scope of any Communication Compliance policy carries one of the SKUs that licenses CC, and that the Copilot interactions template's PAYG dependency is satisfied for the **Enterprise AI apps** and **Other AI apps** scopes.

**Preconditions.** Microsoft Graph PowerShell SDK installed; `Directory.Read.All`, `User.Read.All` granted; the in-scope user list exported to `InScopeUsers.csv`.

**Steps.**

1. Record `T0 = Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mm:ssZ'`.
2. ```powershell
   Connect-MgGraph -Scopes 'Directory.Read.All','User.Read.All'
   $required = @('SPE_E5','M365_E5_COMPLIANCE','INFORMATION_PROTECTION_COMPLIANCE','M365_E5_INSIDER_RISK_MANAGEMENT')
   $copilotReq = @('Microsoft_365_Copilot','Copilot_Pro')
   $inScope = Import-Csv .\InScopeUsers.csv
   $gaps = foreach ($u in $inScope) {
     $skus = (Get-MgUserLicenseDetail -UserId $u.UserPrincipalName).SkuPartNumber
     $hasCC      = [bool]($skus | Where-Object { $required   -contains $_ })
     $hasCopilot = [bool]($skus | Where-Object { $copilotReq -contains $_ })
     if (-not $hasCC) {
       [pscustomobject]@{ Upn=$u.UserPrincipalName; Gap='CC'; Skus=($skus -join ';') }
     } elseif ($u.RequiresCopilotScope -eq 'true' -and -not $hasCopilot) {
       [pscustomobject]@{ Upn=$u.UserPrincipalName; Gap='Copilot'; Skus=($skus -join ';') }
     }
   }
   $gaps | Export-Csv .\1.10-LIC-01-gaps.csv -NoTypeInformation
   ```
3. Document PAYG enablement state for the tenant (Azure subscription ID, meter resource ID, billing-admin attestation reference). PAYG is required for the **Enterprise AI apps** and **Other AI apps** scopes inside the Copilot interactions template (preview — record date verified against Learn).

**Expected result.** `$gaps` is empty. PAYG attestation file is present and dated within the last 30 days.

**Pass criteria (binary).** `$gaps.Count -eq 0` AND PAYG attestation exists for any tenant where the Copilot template's non-M365 AI scopes are enabled. Any non-zero gap is a fail (under-licensed users do not produce CC signals — silent under-coverage).

**Audit assertion.** None at this stage (license check is pre-condition, not a CC operation).

**Evidence collected.** `1.10-LIC-01-<TENANT>-<UTC>-gaps.csv` (header row even if empty), `1.10-LIC-01-<TENANT>-<UTC>-payg.json`, transcript, tester log. SHA-256 sidecar per file.

---

### 1.10-AUD-01 — Unified Audit Log enabled and CC operations are flowing

**Objective.** Confirm the unified audit log is on, and that CC operations `SupervisionRuleMatch`, `SupervisionPolicyCreated`, `SupervisionPolicyUpdated`, `SupervisionPolicyDeleted`, and `SupervisoryReviewTag` (per Microsoft Learn `audit-log-activities`) are surfacing under the documented `RecordType` values.

**Preconditions.** Pre-flight §2.2 passed. At least one `1.10-TEST-*` policy is enabled and at least one tag has been applied (via 1.10-INV-01 in a prior cycle, or as a fresh action here).

**Steps.**

1. Record `T0` UTC.
2. ```powershell
   $start = (Get-Date).AddDays(-7)
   $end   = Get-Date
   $ops   = 'SupervisionRuleMatch','SupervisionPolicyCreated','SupervisionPolicyUpdated','SupervisionPolicyDeleted','SupervisoryReviewTag'
   foreach ($op in $ops) {
     $rows = Search-UnifiedAuditLog -StartDate $start -EndDate $end -Operations $op -ResultSize 5000
     "$op : $($rows.Count) rows" | Tee-Object -FilePath .\1.10-AUD-01-counts.txt -Append
     $rows | Export-Csv ".\1.10-AUD-01-$op.csv" -NoTypeInformation
   }
   ```

**Expected result.** `SupervisionPolicyCreated` and/or `SupervisionPolicyUpdated` returns ≥ 1 row reflecting the cycle's policy lifecycle. `SupervisionRuleMatch` returns ≥ 1 row attributable to the test users from the last 7 days. `SupervisoryReviewTag` returns ≥ 1 row reflecting the cycle's investigator activity.

**Pass criteria.** Every operation for which an action was performed in the window returns ≥ 1 row attributable to the named test users. `Operations` filtering must use the **exact** Microsoft Learn–documented operation names — these strings are case-sensitive.

> **Anti-pattern alert.** Do **not** use `-RecordType CopilotInteraction` as evidence of CC. `CopilotInteraction` is the Copilot audit RecordType; CC events are `SupervisionRuleMatch`, etc. Confusing the two produces evidence that does not show CC was actually evaluating Copilot traffic.

**Audit assertion.** Per-operation row counts written to `1.10-AUD-01-counts.txt`.

**Evidence collected.** Per-operation CSVs, count summary, transcript. SHA-256 sidecars.

---

### 1.10-PSE-01 — Pseudonymization default ON; opt-out audit trail recorded

**Objective.** Confirm the global **Pseudonymization** setting is ON (CC is built privacy-by-design per Microsoft Learn — usernames pseudonymized by default) and that any opt-out is captured by an audit row with the responsible admin identified.

**Preconditions.** Purview Compliance Admin or Communication Compliance Admins role in the Microsoft Purview portal.

**Steps.**

1. Record `T0` UTC.
2. In the Microsoft Purview portal, navigate **Communication Compliance → Settings (gear) → Privacy**.
3. Capture screenshot showing **Show pseudonymized version of usernames** = **On** (UTC clock visible in screenshot).
4. ```powershell
   Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-90) -EndDate (Get-Date) `
     -Operations 'SupervisionPolicyUpdated' -ResultSize 5000 |
     Where-Object { $_.AuditData -match 'Pseudonym' } |
     Export-Csv .\1.10-PSE-01-optout-trail.csv -NoTypeInformation
   ```

**Expected result.** Step 3 screenshot shows pseudonymization **On**. Step 4 CSV is empty if no opt-out has occurred; if non-empty, every row has a populated `UserId` (the admin who toggled the setting) and a `CreationTime` UTC.

**Pass criteria (binary).** Pseudonymization is **On** AND any opt-out row in the 90-day window is attributable to an authorized admin per the firm's change ticket. An opt-out without a corresponding change ticket is a fail.

**Audit assertion.** `SupervisionPolicyUpdated` rows where `AuditData` contains a `Pseudonym*` field.

**Evidence collected.** Settings screenshot (`.png`), opt-out trail CSV (header row even if empty), tester log noting any opt-out's change-ticket reference. SHA-256 sidecars.

---

### 1.10-POL-01 — Per-template policy inventory

**Objective.** Inventory every active CC policy and confirm each carries the correct template, scope (users/groups), reviewers (each with an EXO mailbox), review percentage, **Policy Match Preservation** value, and direction settings.

**Preconditions.** Exchange Online PowerShell connection (per pre-flight §2.4).

**Steps.**

1. Record `T0` UTC.
2. ```powershell
   $policies = Get-SupervisoryReviewPolicyV2
   $report = foreach ($p in $policies) {
     $rules = Get-SupervisoryReviewRule -Policy $p.Identity
     $reviewersOk = $true
     foreach ($r in ($p.Reviewers)) {
       try   { $null = Get-EXOMailbox -Identity $r -ErrorAction Stop }
       catch { $reviewersOk = $false }
     }
     [pscustomobject]@{
       Name                       = $p.Name
       PolicyId                   = $p.Identity
       Mode                       = $p.Mode
       Enabled                    = $p.Enabled
       ConditionTemplate          = $p.ConditionTemplate     # e.g. 'Regulatory Compliance'
       Reviewers                  = ($p.Reviewers -join ';')
       ReviewersHaveEXOMailboxes  = $reviewersOk
       SamplingRate               = ($rules | Select-Object -First 1).SamplingRate
       Direction                  = ($rules | Select-Object -First 1).Direction
       PolicyMatchPreservation    = $p.PolicyMatchPreservation
       LastModifiedTime           = $p.LastModifiedTime
     }
   }
   $report | Export-Csv .\1.10-POL-01-inventory.csv -NoTypeInformation
   $policies | ConvertTo-Json -Depth 10 | Set-Content .\1.10-POL-01-policies.json
   ```

**Expected result.** Every policy intended for production has `Enabled = True`, `ReviewersHaveEXOMailboxes = True`, an explicit `PolicyMatchPreservation` value (not blank — see 1.10-PMP-01), and a `SamplingRate` matching the firm's documented sampling rationale (see 1.10-SAM-01 for the Regulatory compliance default-vs-tuned check). `ConditionTemplate` is one of the seven Microsoft templates: `Conflict of Interest`, `Copilot interactions`, `Inappropriate content`, `Inappropriate images`, `Inappropriate text`, `Regulatory Compliance`, `Sensitive Information`.

> **Template-list anti-pattern.** Customer complaints is **not** a template — it is a classifier inside the **Regulatory compliance** template. A row labeled "Customer complaints template" is invalid and indicates a policy authored from outdated guidance.

**Pass criteria (binary).** All four of: (a) every active policy listed; (b) every reviewer has an EXO mailbox; (c) `PolicyMatchPreservation` is explicitly set; (d) `ConditionTemplate` matches the seven-template list above.

**Audit assertion.** `SupervisionPolicyCreated` / `SupervisionPolicyUpdated` rows for each policy in the last 365 days exist in the unified audit log.

**Evidence collected.** Inventory CSV, full policy JSON export, transcript, tester log. SHA-256 sidecars.

---

### 1.10-COP-01 — Copilot template policy active and scoped to all three AI categories

**Objective.** Confirm the Copilot interactions policy is active and scoped to (a) **Microsoft 365 Copilot experiences**, (b) **Enterprise AI apps**, and (c) **Other AI apps**; and confirm PAYG is enabled for the non-M365 AI scopes.

**Preconditions.** `1.10-TEST-Copilot` policy exists (or production `Copilot interactions` policy named per firm convention).

**Steps.**

1. Record `T0` UTC.
2. In the Microsoft Purview portal, open the policy, capture screenshots of the **Locations** wizard step showing all three scopes selected (UTC clock visible).
3. ```powershell
   $copilotPolicy = Get-SupervisoryReviewPolicyV2 |
     Where-Object { $_.ConditionTemplate -eq 'Copilot interactions' }
   $copilotPolicy | ConvertTo-Json -Depth 10 | Set-Content .\1.10-COP-01-policy.json
   Get-SupervisoryReviewRule -Policy $copilotPolicy.Identity |
     ConvertTo-Json -Depth 10 | Set-Content .\1.10-COP-01-rules.json
   ```
4. As `cc-test-rep-01`, in Microsoft 365 Copilot Chat, issue prompt `BODY-COPILOT-PROMPT-01` (verbatim). Record submission UTC.
5. Wait the Copilot processing window (up to 24 hours per §3). Confirm a `Pending` queue entry appears in the Copilot policy.
6. ```powershell
   Search-UnifiedAuditLog -StartDate $T0 -EndDate (Get-Date) `
     -Operations 'SupervisionRuleMatch' -UserIds 'cc-test-rep-01@<tenant>' -ResultSize 50 |
     Export-Csv .\1.10-COP-01-audit.csv -NoTypeInformation
   ```

**Expected result.** Policy JSON shows all three location scopes. Pending entry appears within the documented Copilot window. Audit CSV contains ≥ 1 `SupervisionRuleMatch` row attributable to `cc-test-rep-01`. PAYG attestation file (from 1.10-LIC-01) is current.

**Pass criteria (binary).** All four of: (a) screenshot evidence of three scopes; (b) `Pending` arrival inside the documented Copilot window; (c) ≥ 1 `SupervisionRuleMatch` audit row; (d) PAYG verified for the non-M365 AI scopes.

**Audit assertion.** `SupervisionRuleMatch` with `UserId = cc-test-rep-01`, `CreationTime` between `T0` and `T0 + 24h`.

**Evidence collected.** Locations-step screenshots, policy + rules JSON, Copilot UI screenshot showing the prompt with UTC clock, audit CSV, PAYG attestation reference. SHA-256 sidecars.

---

### 1.10-CLS-01 — Classifier validation per template

**Objective.** For each enabled template, confirm the documented Microsoft classifiers are active and producing matches for known-trigger bodies. Catches the "policy enabled but only one classifier active" defect class (N4.x).

**Preconditions.** Test policies `1.10-TEST-InappContent`, `1.10-TEST-InappText`, `1.10-TEST-RegComp`, `1.10-TEST-Copilot` exist. Pseudonymization status recorded.

**Test matrix.**

| Sub-case | Template | Body ID | Sender → Recipient | Classifier expected to fire |
|---|---|---|---|---|
| 1.10-CLS-01a | Inappropriate content | `BODY-CONTENT-HATE-01` | `cc-test-rep-01` → `cc-test-rep-02` (Teams chat) | Hate |
| 1.10-CLS-01b | Inappropriate text | `BODY-TXT-THREAT-01` | `cc-test-rep-01` → `cc-test-rep-02` (Teams chat) | Threat |
| 1.10-CLS-01c | Inappropriate text | `BODY-TXT-DISCRIM-01` | `cc-test-rep-01` → `cc-test-rep-02` (Teams chat) | Discrimination |
| 1.10-CLS-01d | Inappropriate text | `BODY-TXT-HARASS-01` | `cc-test-rep-01` → `cc-test-rep-02` (Teams chat) | Targeted harassment |
| 1.10-CLS-01e | Regulatory compliance | `BODY-REG-CUSTCOMP-01` | `cc-test-rep-01` → external test domain (EXO email) | Customer complaints |
| 1.10-CLS-01f | Regulatory compliance | `BODY-REG-GIFT-01` | `cc-test-rep-01` → external (EXO email) | Gifts & entertainment |
| 1.10-CLS-01g | Regulatory compliance | `BODY-REG-MNPI-01` | `cc-test-rep-01` → external (EXO email) | Stock manipulation / Unauthorized disclosure |
| 1.10-CLS-01h | Copilot interactions | `BODY-COPILOT-PROMPT-01` | `cc-test-rep-01` → Copilot Chat | Prompt Shields and/or Protected material |

**Steps (per sub-case).**

1. Record `T0` UTC.
2. Compute `body_sha256 = (Get-FileHash -Algorithm SHA256 .\<body-id>.txt).Hash` and embed in tester log.
3. Send the message verbatim from the named sender to the named recipient via the named channel.
4. Wait the per-source documented window from §3 (Teams 48h, EXO 24h, Copilot 24h).
5. As `cc-test-rev-01`, open the corresponding test policy in the portal and confirm a `Pending` entry exists with the expected classifier highlighted in the yellow banner.
6. ```powershell
   $policyId = (Get-SupervisoryReviewPolicyV2 -Identity '<test-policy-name>').Identity
   Get-SupervisoryReviewActivity -PolicyId $policyId -StartDate $T0 -EndDate (Get-Date) |
     Sort-Object Timestamp -Descending |
     Export-Csv .\1.10-CLS-01-<subcase>-activity.csv -NoTypeInformation
   ```

**Expected result.** Per sub-case: a `Pending` entry exists; the yellow banner names the expected classifier; the audit CSV shows ≥ 1 corresponding row.

**Pass criteria (binary).** Every sub-case scheduled for the cycle produces an observed `Pending` arrival within the per-source documented window AND the audit row references the policy. Sub-cases that did **not** observe a match before the documented window expired are **inconclusive** — re-run after the window. **Inconclusive ≠ pass.**

**Audit assertion.** `SupervisionRuleMatch` rows with `PolicyId = <test-policy>` and `UserId = cc-test-rep-01`, one per sub-case.

**Evidence collected.** Per sub-case: body file with SHA-256, sender screenshot with UTC clock, reviewer-portal screenshot with the yellow-banner classifier visible (pseudonymized usernames), `Get-SupervisoryReviewActivity` CSV, transcript. SHA-256 sidecars.

**Additional requirement for sub-case 1.10-CLS-01e (Customer complaints).** After the `Pending` entry appears, apply the firm's AI-customer-complaint tag, record the interaction reference (message ID, conversation ID, or evidence-manifest pointer), and capture the case or register export showing that the complaint feeds the FINRA Rule 4530(d) quarterly statistics process.

---

### 1.10-SAM-01 — Review percentage verification

**Objective.** Confirm the **Regulatory compliance** template's default 10% review percentage is **caught and tuned to 100%** for any policy scoped to a FINRA-supervised population, and that the chosen sampling rationale is documented.

**Preconditions.** 1.10-POL-01 inventory CSV is current.

**Steps.**

1. Record `T0` UTC.
2. From `1.10-POL-01-inventory.csv`, list every `ConditionTemplate = Regulatory Compliance` policy.
3. For each, confirm `SamplingRate` against the firm's supervisory plan:
   - FINRA-supervised registered representatives → **100%** required (or a written supervisory rationale signed by a Compliance Supervisor for any sampling < 100%).
   - Non-supervised population → may be < 100% with documented rationale.
4. Capture the supervisory plan reference (document ID, version, signing date) in the tester log.

**Expected result.** Every Regulatory compliance policy scoped to FINRA-supervised reps has `SamplingRate = 100`. Any policy with `SamplingRate < 100` carries a signed supervisory rationale.

**Pass criteria (binary).** Zero policies scoped to FINRA-supervised reps with `SamplingRate < 100` AND zero policies with `SamplingRate < 100` lacking a signed rationale.

**Audit assertion.** `SupervisionPolicyUpdated` row exists for each policy whose `SamplingRate` was changed from default 10% to 100% (CC writes a policy-update audit row on the change).

**Evidence collected.** Sampling-rate diff CSV, supervisory-plan reference, transcript. SHA-256 sidecars.

---

### 1.10-OME-01 — Encrypted message handling boundary

**Objective.** Confirm CC policy applies to **Office Message Encryption (OME)–encrypted Exchange items** (per Microsoft Learn) and document any source/scope where encryption causes exclusion.

**Preconditions.** OME enabled in the tenant. Test policy `1.10-TEST-RegComp` covers `cc-test-rep-01`.

**Steps.**

1. Record `T0` UTC.
2. As `cc-test-rep-01`, send an Outlook email containing `BODY-REG-CUSTCOMP-01` to an external test address with the **Encrypt** option applied (OME-encrypted).
3. Wait up to the EXO documented window (24h per §3).
4. As `cc-test-rev-01`, open the policy and verify the encrypted message appears in `Pending` with body content decrypted for the reviewer.
5. ```powershell
   Search-UnifiedAuditLog -StartDate $T0 -EndDate (Get-Date) `
     -Operations 'SupervisionRuleMatch' -UserIds 'cc-test-rep-01@<tenant>' -ResultSize 50 |
     Export-Csv .\1.10-OME-01-audit.csv -NoTypeInformation
   ```
6. Document any third-party encryption (S/MIME from a non-tenant CA, third-party encryption gateway) where decryption is **not** available to CC. List those exclusions in the tester log.

**Expected result.** OME-encrypted message appears in the reviewer's `Pending` queue with content visible. Third-party-encrypted messages produce documented exclusions.

**Pass criteria (binary).** OME case observed inside the EXO documented window AND third-party exclusions listed in the tester log.

**Audit assertion.** `SupervisionRuleMatch` row attributable to `cc-test-rep-01` for the OME-encrypted message.

**Evidence collected.** Sender screenshot with the Encrypt option applied (UTC clock), reviewer-portal screenshot showing the decrypted body (pseudonymized username), audit CSV, exclusions list. SHA-256 sidecars.

---

### 1.10-INV-01 — Investigation and remediation workflow

**Objective.** Confirm the investigator can apply each documented tag (**Compliant**, **Non-compliant**, **Questionable**), notify the user, resolve the item, and that each action emits a `SupervisoryReviewTag` audit row.

**Preconditions.** ≥ 3 `Pending` items exist (use the matches generated by 1.10-CLS-01).

**Steps.**

1. Record `T0` UTC.
2. As `cc-test-inv-01`, open the policy `Pending` tab. For three distinct items:
   - Apply tag **Compliant** to item 1; resolve.
   - Apply tag **Non-compliant** to item 2; **Notify user** with the firm's standard notification template; resolve.
   - Apply tag **Questionable** to item 3; escalate to `cc-test-inv-01`'s escalation contact; do **not** resolve.
3. Capture portal screenshots for each tag action (UTC clock visible; reviewer name pseudonymized).
4. ```powershell
   $policyId = (Get-SupervisoryReviewPolicyV2 -Identity '1.10-TEST-RegComp').Identity
   Get-SupervisoryReviewActivity -PolicyId $policyId -StartDate $T0 -EndDate (Get-Date) |
     Sort-Object Timestamp -Descending |
     Select-Object PolicyId,ItemSubject,ActivityId,Timestamp,ActionType,ActionAppliedBy,ItemStatusAfterAction |
     Export-Csv .\1.10-INV-01-activity.csv -NoTypeInformation
   ```

**Expected result.** CSV contains three rows with `ActionType` values reflecting each tag action and `ActionAppliedBy = cc-test-inv-01@<tenant>`. The notify-user item shows a corresponding email received by `cc-test-rep-01`'s mailbox.

**Pass criteria (binary).** All three tag actions captured in the activity CSV with correct `ActionType` and `ActionAppliedBy`; notify-user message received and screenshot captured; escalation item remains in non-resolved state with the expected escalation-contact attribution.

**Audit assertion.** `SupervisoryReviewTag` rows for each of the three items in the unified audit log.

**Evidence collected.** Three portal screenshots, activity CSV, notify-user email screenshot, transcript. SHA-256 sidecars.

---

### 1.10-EDC-01 — eDiscovery escalation

**Objective.** Confirm a CC item can be escalated to **eDiscovery (Premium)** with a case opened against the source mailbox / Teams chat per Microsoft Learn `communication-compliance-investigate-remediate`.

**Preconditions.** eDiscovery (Premium) licensed and at least one eDiscovery Manager / eDiscovery Administrator role assignment exists; one `Pending` item from 1.10-INV-01 marked **Non-compliant** is still present (or use a fresh match).

**Steps.**

1. Record `T0` UTC.
2. As `cc-test-inv-01` (also member of `eDiscovery Manager` role), open the Non-compliant item and select **Escalate for investigation → Open as new eDiscovery case**.
3. Confirm the case appears in **Microsoft Purview → eDiscovery (Premium) → Cases** with the source identity and message reference attached.
4. Capture screenshots: CC portal escalation step, eDiscovery case landing page, custodian list (UTC clock visible in each).

**Expected result.** A case named per the firm's convention exists in eDiscovery (Premium) with the source identity attached as custodian and the offending item available for hold and review.

**Pass criteria (binary).** Case created within the cycle window AND custodian + item attached AND eDiscovery role membership for `cc-test-inv-01` documented.

**Audit assertion.** `CaseAdded` (eDiscovery) audit row written within the cycle window; correlated with the `SupervisoryReviewTag` row from 1.10-INV-01 by `ItemSubject`.

**Evidence collected.** Three portal screenshots, eDiscovery case JSON export, transcript. SHA-256 sidecars.

---

### 1.10-AU-01 — Administrative Units scoping

**Objective.** Confirm reviewers scoped via Administrative Units see **only** items produced by users inside their AU(s) — no over-share, no under-share.

**Preconditions.** ≥ 2 Administrative Units exist (e.g., `AU-Region-East`, `AU-Region-West`). `cc-test-rev-01` is scoped to `AU-Region-East`. `cc-test-rep-01` is in `AU-Region-East`; `cc-test-rep-02` is in `AU-Region-West`. Two production-shape policies cover both AUs.

**Steps.**

1. Record `T0` UTC.
2. As `cc-test-rep-01` (East), send `BODY-REG-CUSTCOMP-01`. As `cc-test-rep-02` (West), send the same body.
3. Wait the EXO documented window (24h per §3).
4. As `cc-test-rev-01`, open the **Policies** page. Confirm the policy banner shows AU scoping (per Learn: *"If your role group is scoped by one or more admin units, you see a message at the top of the page..."*).
5. Open `Pending`. Confirm only the East-origin item is visible. Capture screenshot (UTC clock; pseudonymized usernames).
6. As an unscoped Purview Compliance Admin, confirm both items are visible in the same policy.

**Expected result.** AU-scoped reviewer sees only the East item; unscoped admin sees both.

**Pass criteria (binary).** Visibility matches AU scope exactly. Any leakage (West item visible to East reviewer) or false-restriction (East item not visible) is a fail.

**Audit assertion.** Both `SupervisionRuleMatch` rows present in the audit log; reviewer access pattern is enforced at the portal layer (no audit row is required for read-restriction).

**Evidence collected.** Two portal screenshots (scoped + unscoped), audit CSV showing both matches, AU-membership export from `Get-MgAdministrativeUnitMember`, transcript. SHA-256 sidecars.

---

### 1.10-PMP-01 — Policy Match Preservation

**Objective.** Confirm **Policy Match Preservation** is **explicitly** set per policy (not silently inheriting the global default of 1 year), and document the firm's understanding that PMP is **not** the SEC 17a-4 records-retention path — true records retention is verified under [Control 1.12](../1.12/verification-testing.md).

**Preconditions.** 1.10-POL-01 inventory CSV is current.

**Steps.**

1. Record `T0` UTC.
2. From the inventory CSV, confirm every active policy carries an explicit `PolicyMatchPreservation` value: `1 month`, `6 months`, `1 year`, or `7 years`.
3. In the tester log, document for each policy the rationale for the chosen preservation period and confirm that the firm's Records Information Management (RIM) policy is **independent** of PMP (i.e., supervised messages are retained on WORM-eligible storage via Control 1.12).
4. Capture portal screenshot of **Settings → Policy Match Preservation** showing the global default and any per-policy override (UTC clock visible).

**Expected result.** Every active policy has an explicit per-policy PMP value or has consciously inherited the global setting (documented). RIM policy reference in the tester log.

**Pass criteria (binary).** No policy has a missing/blank PMP value AND a current RIM policy reference exists in the tester log establishing that PMP is **not** being relied on as records retention.

**Audit assertion.** `SupervisionPolicyUpdated` rows reflecting any PMP changes inside the cycle window.

**Evidence collected.** PMP screenshot, inventory CSV with PMP column, RIM policy reference, transcript. SHA-256 sidecars.

---

### 1.10-NEG-01 — Out-of-scope user does NOT generate a match

**Objective.** Confirm CC does **not** create a `Pending` entry or `SupervisionRuleMatch` audit row for a user explicitly out of scope of every active policy.

**Preconditions.** `cc-test-out-01` is **not** included in any policy scope (verified by inventory CSV).

**Steps.**

1. Record `T0` UTC.
2. As `cc-test-out-01`, send `BODY-OUT-OF-SCOPE-01` (same content as `BODY-REG-CUSTCOMP-01`) by EXO email to an external test address.
3. Wait the EXO documented window plus 6-hour buffer (30 hours total).
4. ```powershell
   Search-UnifiedAuditLog -StartDate $T0 -EndDate (Get-Date) `
     -Operations 'SupervisionRuleMatch' -UserIds 'cc-test-out-01@<tenant>' -ResultSize 50 |
     Export-Csv .\1.10-NEG-01-audit.csv -NoTypeInformation
   ```
5. As `cc-test-rev-01`, confirm no `Pending` item attributable to `cc-test-out-01` appears in any policy.

**Expected result.** Zero `SupervisionRuleMatch` rows for `cc-test-out-01`. Zero `Pending` entries.

**Pass criteria (binary).** Both observations match. A non-zero result indicates scope leakage and is a fail.

**Audit assertion.** `SupervisionRuleMatch` row count for `UserId = cc-test-out-01` is exactly 0.

**Evidence collected.** Audit CSV (header row + zero data rows), reviewer-portal screenshot showing absence of `cc-test-out-01` items, transcript. SHA-256 sidecars.

---

### 1.10-NEG-02 — Paused policy does NOT generate matches

**Objective.** Confirm a policy in **Deactivated** status produces zero matches even when an in-scope user sends a known-trigger body.

**Preconditions.** `1.10-TEST-Paused` is `Enabled = False` (Status = Deactivated).

**Steps.**

1. Record `T0` UTC. Confirm `(Get-SupervisoryReviewPolicyV2 -Identity '1.10-TEST-Paused').Enabled -eq $false`.
2. As `cc-test-rep-01`, send `BODY-TXT-THREAT-01` via Teams chat to `cc-test-rep-02`.
3. Wait the Teams documented window plus 6-hour buffer (54 hours total).
4. ```powershell
   $policyId = (Get-SupervisoryReviewPolicyV2 -Identity '1.10-TEST-Paused').Identity
   Get-SupervisoryReviewActivity -PolicyId $policyId -StartDate $T0 -EndDate (Get-Date) |
     Export-Csv .\1.10-NEG-02-activity.csv -NoTypeInformation
   Search-UnifiedAuditLog -StartDate $T0 -EndDate (Get-Date) `
     -Operations 'SupervisionRuleMatch' -UserIds 'cc-test-rep-01@<tenant>' -ResultSize 50 |
     Where-Object { $_.AuditData -match $policyId } |
     Export-Csv .\1.10-NEG-02-audit.csv -NoTypeInformation
   ```

**Expected result.** Both CSVs contain zero data rows for the paused policy.

**Pass criteria (binary).** Zero matches attributable to the paused policy. A non-zero result indicates the policy is silently active and is a fail.

**Audit assertion.** `SupervisionRuleMatch` rows referencing `1.10-TEST-Paused`'s `PolicyId` is exactly 0.

**Evidence collected.** Two CSVs (header rows + zero data), policy-status screenshot, transcript. SHA-256 sidecars.

---

### 1.10-NEG-03 — Reviewer in role group but NOT assigned to policy cannot view matches

**Objective.** Confirm role-group membership alone does not grant policy visibility — explicit assignment as a reviewer on the policy is required (per Learn: *"Reviewer in the policy that is associated with the alert"*).

**Preconditions.** `cc-test-rev-02` is a member of `Communication Compliance Analysts` role group but is **not** assigned as a reviewer on `1.10-TEST-RegComp`. ≥ 1 Pending item exists in `1.10-TEST-RegComp`.

**Steps.**

1. Record `T0` UTC.
2. ```powershell
   (Get-RoleGroupMember 'Communication Compliance Analysts').Name -contains 'cc-test-rev-02'   # expect True
   (Get-SupervisoryReviewPolicyV2 -Identity '1.10-TEST-RegComp').Reviewers -contains 'cc-test-rev-02@<tenant>'  # expect False
   ```
3. As `cc-test-rev-02`, sign in to the Microsoft Purview portal and open **Communication Compliance → Policies**.
4. Confirm `1.10-TEST-RegComp` is **not** visible OR is visible with zero `Pending` items accessible.
5. Capture screenshot (UTC clock visible).
6. As `cc-test-rev-01` (assigned reviewer), confirm the same items are visible. Capture comparison screenshot.

**Expected result.** `cc-test-rev-02` cannot see the items; `cc-test-rev-01` can.

**Pass criteria (binary).** Negative-visibility for the unassigned reviewer AND positive-visibility for the assigned reviewer. Any leakage is a fail and indicates a misconfiguration of role group vs. per-policy reviewer assignment (defect class B6).

**Audit assertion.** No CC-specific audit row is required; the test is a portal-layer access-control validation.

**Evidence collected.** Two portal screenshots (unassigned vs. assigned), role-group membership export, policy-reviewer JSON, transcript. SHA-256 sidecars.

---

## 5. Sovereign Cloud Variant

For each test in §4, substitute the cloud-specific endpoints and record the cloud in the tester log header. **Feature parity caveats apply** — verify each preview feature against current Microsoft Learn for the target cloud before claiming pass/fail.

| Step type | Commercial | GCC | GCC High | DoD |
|---|---|---|---|---|
| Microsoft Purview portal | `purview.microsoft.com` | `purview.microsoft.com` (verify) | `purview.microsoft.us` | `compliance.apps.mil` |
| Exchange Online PowerShell | `Connect-ExchangeOnline` | `Connect-ExchangeOnline` (default) | `Connect-ExchangeOnline -ExchangeEnvironmentName O365USGovGCCHigh` | `Connect-ExchangeOnline -ExchangeEnvironmentName O365USGovDoD` |
| Microsoft Graph (`Connect-MgGraph`) | default | `-Environment USGov` | `-Environment USGov` (verify) | `-Environment USGovDoD` |
| Copilot interactions template scope | M365 Copilot + Enterprise AI apps + Other AI apps | Verify per Learn (rollout dates differ) | **Verify parity** — non-M365 AI scopes may trail Commercial; record exception if N/A | **Verify parity** — non-M365 AI scopes may not be available; record exception |
| PAYG meter (1.10-LIC-01, 1.10-COP-01) | Available | Available (verify) | **Verify parity**; document exception if unavailable | **Verify parity**; document exception if unavailable |
| Administrative Units scoping (1.10-AU-01) | GA | GA (verify) | Verify | Verify |
| eDiscovery (Premium) escalation (1.10-EDC-01) | Available | Available | Available (verify) | Available (verify) |
| User-reported messages (Teams / Viva Engage) | GA | GA | Verify | Verify |

> **Sovereign anti-pattern.** Do **not** synthesize evidence in a sovereign cloud where a feature is documented as N/A. Record a **signed exception** referencing the current Microsoft Learn URL and the date of verification. See `docs/playbooks/_shared/powershell-baseline.md` §3 for the canonical sovereign-endpoint reference.

---

## 6. Evidence Pack

Every cycle, produce and archive the artifacts below. **File naming convention:**

```
1.10-<TestID>-<TENANT>-<UTC-yyyyMMddTHHmmssZ>-evidence.<json|csv|png|md|txt>
e.g., 1.10-COP-01-CONTOSO-20260415T141207Z-evidence.csv
      1.10-COP-01-CONTOSO-20260415T141207Z-evidence.csv.sha256
```

**SHA-256 manifest (`Control-1.10_Manifest_<UTC>.json`):**

```json
{
  "runId": "1.10-2026Q2-CONTOSO-cycle-04",
  "tenantId": "00000000-0000-0000-0000-000000000000",
  "cloud": "Commercial",
  "zone": 3,
  "attestor": "jane.doe@contoso.com",
  "generated_utc": "2026-04-15T14:30:00Z",
  "framework_version": "v1.3.4",
  "tests": [
    {
      "id": "1.10-LIC-01",
      "result": "pass",
      "artifacts": [
        { "file": "1.10-LIC-01-CONTOSO-20260415T141207Z-evidence.csv", "sha256": "3a7b...c91", "bytes": 4096 },
        { "file": "1.10-LIC-01-CONTOSO-20260415T141207Z-payg.json",     "sha256": "9f12...88a", "bytes": 612  }
      ]
    },
    {
      "id": "1.10-COP-01",
      "result": "pass",
      "windowed_observation_hours": 6.2,
      "documented_window_hours":   24,
      "artifacts": [
        { "file": "1.10-COP-01-CONTOSO-20260415T143812Z-policy.json", "sha256": "4c0d...771", "bytes": 8814 },
        { "file": "1.10-COP-01-CONTOSO-20260415T143812Z-rules.json",  "sha256": "8e21...a32", "bytes": 3211 },
        { "file": "1.10-COP-01-CONTOSO-20260415T143812Z-audit.csv",   "sha256": "b1f4...ee0", "bytes": 1722 },
        { "file": "1.10-COP-01-CONTOSO-20260415T143812Z-prompt.png",  "sha256": "d093...44b", "bytes": 152033 }
      ]
    }
  ]
}
```

**Generate manifest with:**

```powershell
$evidenceDir = '.\evidence\1.10\<cycle>'
$entries = Get-ChildItem $evidenceDir -File -Exclude *.sha256,manifest.json |
  ForEach-Object {
    [pscustomobject]@{
      file   = $_.Name
      sha256 = (Get-FileHash -Path $_.FullName -Algorithm SHA256).Hash.ToLower()
      bytes  = $_.Length
    }
  }
[pscustomobject]@{
  runId             = '1.10-<cycle>-<tenant>'
  tenantId          = '<tenantId>'
  cloud             = 'Commercial'
  attestor          = '<upn>'
  generated_utc     = (Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mm:ssZ')
  framework_version = 'v1.3.4'
  hashes            = $entries
} | ConvertTo-Json -Depth 5 |
  Set-Content (Join-Path $evidenceDir ("Control-1.10_Manifest_$(Get-Date -AsUTC -Format 'yyyyMMddTHHmmssZ').json"))
```

**Required artifacts per cycle.**

| # | Artifact | Source test |
|---|---|---|
| 1 | License gap CSV (header row even if empty) + PAYG attestation | 1.10-LIC-01 |
| 2 | Per-operation audit CSVs + counts file | 1.10-AUD-01 |
| 3 | Pseudonymization settings screenshot + opt-out trail CSV | 1.10-PSE-01 |
| 4 | Policy inventory CSV + full policy JSON | 1.10-POL-01 |
| 5 | Copilot location screenshot + policy/rules JSON + Copilot prompt screenshot + audit CSV + PAYG attestation reference | 1.10-COP-01 |
| 6 | Per-classifier sub-case body files + sender + reviewer screenshots + activity CSVs; for 1.10-CLS-01e also include complaint-tag screenshot + quarterly-report register or case export | 1.10-CLS-01 |
| 7 | Sampling-rate diff CSV + signed supervisory plan reference | 1.10-SAM-01 |
| 8 | OME sender screenshot + reviewer-portal screenshot + audit CSV + exclusions list | 1.10-OME-01 |
| 9 | Three tag-action portal screenshots + activity CSV + notify-user email screenshot | 1.10-INV-01 |
| 10 | eDiscovery escalation screenshots + case JSON | 1.10-EDC-01 |
| 11 | AU-scoped + unscoped portal screenshots + AU-membership export + audit CSV | 1.10-AU-01 |
| 12 | PMP settings screenshot + inventory CSV with PMP column + RIM policy reference | 1.10-PMP-01 |
| 13 | Negative-test audit CSVs (header rows + zero data) + reviewer screenshots + role-group exports | 1.10-NEG-01, 1.10-NEG-02, 1.10-NEG-03 |
| 14 | PowerShell transcript per test | All |
| 15 | Manifest `.json` with SHA-256 of every artifact | All |

**Retention guidance.**

- **FINRA Rule 4511 / SEC 17a-4(b):** retain ≥ 6 years (broker-dealer) / 5 years (other FSI), per the firm's records schedule.
- **SEC 17a-4(f) (October 2022 amendments):** evidence stored *outside* Purview (CSV/JSON/PNG/MD exports, transcripts, manifests) **must** be placed on **WORM-eligible storage** (Microsoft Purview Data Lifecycle Management retention lock, Azure Storage immutability policy, or third-party WORM appliance). Audit-log evidence inside Purview is governed by Microsoft's audit retention configuration ([Control 1.7](../1.7/verification-testing.md)). **Communication Compliance's Policy Match Preservation is not the records-retention path** (see §8).
- **GLBA 501(b) / SEC Reg S-P:** retain CC evidence touching customer information per the firm's privacy schedule.
- **Default for this control:** 7 years on WORM-treated storage with paired SHA-256 sidecars and a signed attestation per §7.

**WORM-eligible storage path** (example): `\\fsi-evidence-worm\purview\1.10-comm-compliance\<cycle>\` mapped to a Purview retention-locked container or Azure Storage with immutability policy `1.10-cycle-policy` and minimum retention `2555` days. Document the storage path and retention-policy ID in the cycle's tester log.

---

## 7. Attestation

```text
Control 1.10 — Communication Compliance Monitoring
Cycle:                Q____ FY____
Tenant:               _______________________________________
Cloud:                ☐ Commercial  ☐ GCC  ☐ GCC High  ☐ DoD
Governance Zone:      ☐ Zone 1  ☐ Zone 2  ☐ Zone 3
Verification window:  ____________________ UTC  →  ____________________ UTC
Evidence manifest:    Control-1.10_Manifest_____________________.json
Manifest SHA-256:     ________________________________________________________________
WORM storage path:    _______________________________________________________________
Retention policy ID:  _______________________________________________________________

I have executed the test catalog in §4 for the period above. Sovereign-variant
substitutions in §5 were applied where the tenant resides in GCC, GCC High, or
DoD, and any feature-parity exceptions are signed and attached. The evidence
listed in §6 is archived on WORM-eligible storage per the retention guidance
and SHA-256 sidecars match the manifest at archival time.

Caveats and scope limits:
  • Microsoft Purview Communication Compliance's Policy Match Preservation
    setting is NOT relied on as records retention under SEC 17a-4 — true
    records retention is verified under Control 1.12.
  • Inconclusive sub-cases (matches not observed before the documented
    processing window expired) have been re-run; "inconclusive" was not
    treated as "pass."
  • Pseudonymization is ON; any opt-out is matched to a signed change
    ticket.

This evidence supports — but does not by itself establish — the firm's
compliance with:

  • FINRA Rule 3110 / 3110.06 / 25-07 (supervisory system over electronic
    communications and AI-assisted communications)
  • FINRA Rule 4511 (record preservation for supervised messages and policy
    state)
  • SEC Rule 17a-4 (records retention — paired with Control 1.12)
  • SEC Reg S-P / Reg S-ID (where customer information is detected)
  • GLBA 501(b) (safeguards for customer information)
  • OCC 2026-13 (formerly OCC 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7)
    (model risk management ongoing monitoring expectations as they apply to CC classifier coverage)
  • SOX 404 (IT general controls over the supervisory pipeline)

This attestation does not constitute a legal determination. Reportability
decisions remain with Compliance and Legal counsel.

Control owner (printed name): _______________________________________
Role:                         _______________________________________
Signature:                    _______________________________________
Date (UTC):                   _______________________________________
```

---

## 8. Anti-Patterns and Known Traps

1. **Accepting the default reviewer list of the *Detect User-Reported Messages* policy.** When the policy is auto-provisioned, all members of `Communication Compliance Admins` (or the `Global Admin` role group as fallback) are assigned as initial reviewers per Microsoft Learn. For an FSI tenant, this is **not** acceptable supervisory routing — assign explicit Compliance / HR / Risk reviewers as part of pre-flight. 1.10-POL-01 surfaces this when `Reviewers` includes high-privilege role groups instead of named compliance staff.
2. **Testing only the keyword classifier.** A policy authored from the Inappropriate text template can be enabled with only the Threat classifier active; Discrimination and Targeted harassment may be silently disabled. 1.10-CLS-01 forces per-classifier verification.
3. **Treating an empty `Pending` queue as a PASS.** Empty queues can mean "no problematic communications" or "policy is misconfigured / paused / out-of-scope." Pair every queue inspection with a deterministic positive test (1.10-CLS-01) and an audit-row check (1.10-AUD-01) before declaring pass.
4. **Sampling instead of 100% review for FINRA-supervised reps without documented basis.** The Regulatory compliance template defaults to 10% review percentage; for supervised registered representatives this is insufficient under FINRA 3110.06 unless a written supervisory rationale is signed. 1.10-SAM-01 enforces tuning to 100% or producing the rationale.
5. **Relying on Policy Match Preservation as records retention.** PMP governs how long Communication Compliance keeps a *copy* of the matched message inside its review surface (1 month / 6 months / 1 year / 7 years). It is **not** SEC 17a-4 records retention for the original communication — that lives under Exchange retention / In-Place Archive / records management ([Control 1.12](../1.12/verification-testing.md)). Conflating the two produces a 6-year retention gap on supervised messages.
6. **Using `Search-UnifiedAuditLog -RecordType CopilotInteraction` as evidence of Communication Compliance.** `CopilotInteraction` is the Copilot audit RecordType; CC events are emitted under `SupervisionRuleMatch`, `SupervisionPolicyCreated/Updated/Deleted`, and `SupervisoryReviewTag` per Microsoft Learn `audit-log-activities`. Confusing the two produces evidence that does not show CC was actually evaluating Copilot traffic. 1.10-AUD-01 requires the documented operation names.
7. **Pseudonymization opt-out without an audit trail.** Toggling pseudonymization off changes who-sees-whom across the entire CC surface. Any opt-out must be matched to a `SupervisionPolicyUpdated` audit row whose `UserId` is the responsible admin and to a signed change ticket. 1.10-PSE-01 captures this trail.
8. **Testing without the Exchange Online mailbox prerequisite verified for the reviewer.** Per Learn, *"Reviewers must have mailboxes hosted on Exchange Online."* A reviewer without an EXO mailbox does not receive notification email and cannot be relied on for supervisory action. 1.10-POL-01 fails the policy if any reviewer lacks an EXO mailbox.
9. **Missing PAYG enablement for non-M365 AI tests.** The Copilot interactions template's **Enterprise AI apps** and **Other AI apps** scopes are gated by the Microsoft 365 Copilot pay-as-you-go meter on a connected Azure subscription (preview status). Enabling these scopes without PAYG produces an enabled-but-silent policy for those locations. 1.10-LIC-01 and 1.10-COP-01 require the PAYG attestation file.
10. **Running tests within the Teams 48-hour processing window and concluding "no match."** The documented Teams chat ceiling is 48 hours from message-send to `Pending` arrival. A test that waits 6 hours and concludes "no match = fail" is wrong — the result is **inconclusive**. §3 mandates per-source documented windows; §4 marks any sub-case that completed inside the window as inconclusive and requires re-run.
11. **Using PowerShell to "create" or "modify" a CC policy.** Per Microsoft Learn `communication-compliance-policies`: *"PowerShell isn't supported for creating and managing Communication Compliance policies."* Read-only cmdlets (`Get-SupervisoryReviewPolicyV2`, `Get-SupervisoryReviewRule`, `Get-SupervisoryReviewActivity`) are supported and used throughout this catalog; mutations must be performed in the Microsoft Purview portal and tracked via `SupervisionPolicyUpdated` audit rows.
12. **Wrong shell — Security & Compliance vs. Exchange Online.** `Get-Supervisory*` cmdlets live in **Exchange Online PowerShell**, not Security & Compliance PowerShell. The wrong shell returns `CommandNotFoundException` or empty results without an error in some module versions. Pre-flight §2.4 checks the connection URI before each test.
13. **Treating "Customer Complaints" as a top-level template.** Customer complaints is a **classifier inside the Regulatory compliance template**, not one of the seven templates. Policies authored as if "Customer complaints" were a template are working from outdated guidance — 1.10-POL-01 enforces the seven-template list (`Conflict of Interest`, `Copilot interactions`, `Inappropriate content`, `Inappropriate images`, `Inappropriate text`, `Regulatory compliance`, `Sensitive information`).

---

## 9. Cross-links

- [Control 1.5 — DLP and Sensitivity Labels](../1.5/verification-testing.md) — DLP signals and sensitivity-label state; required for SIT-driven CC matches and label-based scoping.
- [Control 1.7 — Purview Audit Configuration](../1.7/verification-testing.md) — Unified audit ingestion, retention horizons; required for 1.10-AUD-01 to produce evidence.
- [Control 1.9 — Insider Risk Management](../1.9/verification-testing.md) — Companion supervisory signal; CC matches can feed IRM indicators and vice versa.
- [Control 1.12 — Records Retention (SEC 17a-4)](../1.12/verification-testing.md) — True records retention path; CC's Policy Match Preservation is **not** a substitute.
- [Control 1.13 — eDiscovery (Premium)](../1.13/verification-testing.md) — Escalation target for 1.10-EDC-01.
- [Control 1.19 — Copilot Auditing](../1.19/verification-testing.md) — `CopilotInteraction` RecordType (distinct from CC operations); paired evidence for AI surfaces.
- [Control 2.12 — Agent Lifecycle Governance](../2.12/verification-testing.md) — Supervisory population definition source (registered reps roster, role-based scoping inputs).
- [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md) — Sovereign endpoints, mutation safety, evidence emit, and module pinning conventions.
- [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Troubleshooting](troubleshooting.md).

---

[Back to Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
