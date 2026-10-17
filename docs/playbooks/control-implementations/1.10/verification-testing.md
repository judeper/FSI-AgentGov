# Control 1.10 — Verification & Testing: Communication Compliance Monitoring

> Verification procedures for [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md). Run each test on the cadence in §1, capture evidence per §5, and complete the attestation in §6 each cycle.
>
> **Scope of this playbook:** Microsoft Purview Communication Compliance (CC) — policy inventory, classifier coverage, review-percentage validation, reviewer/role-group assignments, pseudonymization controls, the Copilot interactions template (Microsoft 365 Copilot, Microsoft 365 Copilot Chat, Enterprise AI apps, Other AI apps), Administrative Units (AU) scoping, Policy Match Preservation, and the investigate / remediate / eDiscovery escalation chain. **Out of scope here:** unified audit retention horizons (verified under [Control 1.7](../1.7/verification-testing.md)) and SEC 17a-4 records-retention chain (verified under [Control 1.9](../1.9/verification-testing.md)). CC's Policy Match Preservation is **not** a records-retention control under SEC 17a-4 — see §7 anti-pattern.
>
> **Audience:** M365 administrator at a US financial services organization producing audit-defensible evidence for FINRA Rule 3110 / 3110.06 (with RN 24-09 for AI supervisory guidance), FINRA Rule 4511, SEC Rule 17a-4, OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7), and GLBA 501(b) examiners.
>
> **Scope:** Microsoft 365 Commercial (Global) cloud — the deployment surface for US financial-services customers.
>
> **Cross-links:** [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Troubleshooting](troubleshooting.md) · [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md).
>
> **Last UI Verified:** April 2026.
>
> **Last Verified:** 2026-10-16 — live Microsoft Learn documentation review only. No tenant, portal UI, licensing, PowerShell connection, classifier, or message-processing test was executed. The earlier UI-verification date is historical, not renewed by this review.

---

## What this verification catches

This catalog is designed to surface the carry-forward defect classes that the AI Council review identified for Communication Compliance:

- **B1** — Policy authored from the wrong template (e.g., Sensitive information used where Regulatory compliance is required for FINRA-supervised reps).
- **B6** — Reviewer role-group membership without reviewer assignment on the policy itself (apparent coverage, no real visibility).
- **B9** — Pseudonymization opt-out without an audit-trail row, or pseudonymization assumed to be ON without verification.
- **N3.x** — Negative-space regressions where out-of-scope users, paused policies, or non-assigned reviewers silently produce no signal but are mistaken for "clean."
- **N4.x** — Classifier-coverage gaps inside a template (e.g., Inappropriate text policy enabled but only the Threat classifier active; Copilot template enabled but Prompt Shields disabled).

Each test below maps explicitly to the failure mode it detects and records the named test user(s), UTC timestamp, exact policy ID, exact message body or attachment hash, observed `Pending` queue entry, and applicable unified-audit operation rows. Classifier outcomes are probabilistic; the example bodies are not Microsoft-certified trigger strings.

---

## 1. Re-Verification Cadence

Communication Compliance signals are **non-static**. Microsoft ships classifier updates, the Copilot interactions template gained scope additions (Enterprise AI apps, Other AI apps), and Policy Match Preservation defaults shifted in 2025. Each test runs on its own cadence rather than a single annual binder refresh, aligned to OCC Bulletin 2026-13 (formerly OCC 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) ongoing-monitoring expectations for model and supervisory systems.

| Test ID | Frequency | Owner role | Evidence retention | Regulatory driver |
|---|---|---|---|---|
| 1.10-LIC-01 | Monthly | Entra Global Admin (read) + Purview Compliance Admin | 7 years (broker-dealer) / 6 years (other FSI) | FINRA 4511, SEC Reg S-P, GLBA 501(b) |
| 1.10-AUD-01 | Weekly | Purview Audit Admin | 7 years | FINRA 4511, SEC 17a-4(f) |
| 1.10-PSE-01 | Monthly | Purview Compliance Admin | 7 years | GLBA 501(b), Reg S-P, EU GDPR (where applicable to US-listed FSI) |
| 1.10-POL-01 | Monthly | Purview Compliance Admin | 7 years | FINRA 3110 / 3110.06 / RN 24-09, FINRA 4511 |
| 1.10-COP-01 | Monthly (feature and scope changes) | Purview Compliance Admin + AI Governance Lead | 7 years | FINRA RN 24-09, FINRA 3110, OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) |
| 1.10-CLS-01 | Monthly | Purview Compliance Admin | 7 years | FINRA 3110, FINRA 2210, FINRA RN 24-09 |
| 1.10-SAM-01 | Quarterly | Purview Compliance Admin + Compliance Supervisor | 7 years | FINRA 3110.06 (supervisory sampling rationale) |
| 1.10-OME-01 | Quarterly | Purview Compliance Admin + Exchange Online Admin | 7 years | FINRA 4511, GLBA 501(b) |
| 1.10-INV-01 | Weekly | CC Analyst + CC Investigator | 7 years | FINRA 3110, SEC 17a-4(b) |
| 1.10-EDC-01 | Quarterly | Authorized CC Investigator / policy reviewer; coordinate with eDiscovery owner | 7 years (or per legal hold) | FINRA 4511, SEC 17a-4(b)/(f) |
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

The [Microsoft Purview service description](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description) lists base CC rights for Microsoft 365 E5, Microsoft Purview Suite, the qualifying Insider Risk Management add-on, and Office 365 E5. Its **Microsoft Copilot for Microsoft 365 prompt and response analysis** row lists Microsoft 365 E5 + Microsoft Copilot or Microsoft Purview Suite + Microsoft Copilot; base CC rights alone are not sufficient for that feature. Verify the exact purchased plans, prerequisites, assigned service plans, and the source experience rather than inferring entitlement from a policy's template name.

The [generative AI guidance](https://learn.microsoft.com/en-us/purview/communication-compliance-copilot) requires **Microsoft Purview pay-as-you-go billing** for **all non-Microsoft 365 AI data**, including Copilot Studio, Security Copilot, and Copilot in Fabric within **Microsoft Copilot experiences**, as well as **Enterprise AI apps** and **Other AI apps**. Microsoft 365 Copilot data has no PAYG requirement or charge for this detection. Record the date and source used for each entitlement decision.

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

> CC policy creation and edit are **not supported via PowerShell** per [Microsoft Learn](https://learn.microsoft.com/en-us/purview/communication-compliance-policies) — use the Microsoft Purview portal. `Get-SupervisoryReviewPolicyV2` and `Get-SupervisoryReviewRule` require Security & Compliance PowerShell (IPPS). `Get-SupervisoryReviewActivity` returns **reviewer actions**, not newly detected matches. Preserve raw output and reconcile it to the portal; the cmdlet references do not document a stable output contract for every modern CC setting.

### 2.4 Roles and connections

| Role / connection | Purpose | Verification |
|---|---|---|
| Purview Compliance Admin or Communication Compliance Admins | Read policy inventory; configure pseudonymization | Sign in to `purview.microsoft.com` and confirm the **Communication Compliance** solution is visible |
| Communication Compliance Investigators | Open `Pending` queue, apply tags, escalate to eDiscovery | `Get-RoleGroupMember 'Communication Compliance Investigators'` |
| Communication Compliance Analysts | Triage `Pending`, apply tags, notify user | `Get-RoleGroupMember 'Communication Compliance Analysts'` |
| Reviewer mailbox | Receive notifications and act on items | Reviewer must have an Exchange Online mailbox (per Learn `communication-compliance-policies`) — verify via `Get-EXOMailbox -Identity <reviewer>` returns a result |
| Security & Compliance (IPPS) connection | Read supervisory review policies and rules | Run `Connect-IPPSSession`; inspect `Get-ConnectionInformation` for the intended tenant and `https://ps.compliance.protection.outlook.com/powershell-liveid/`, and confirm required commands are available |

> **Wrong-shell trap.** The policy and rule references explicitly require **Security & Compliance PowerShell** (`Connect-IPPSSession`). The activity reference describes a cloud-service cmdlet; the reports guidance also uses Exchange Online PowerShell for mailbox statistics. Do not infer undocumented silent-zero behavior from a connection type. Verify command availability, tenant, permissions, and a positive control. Use `Connect-ExchangeOnline` separately for `Get-AdminAuditLogConfig` and `Get-EXOMailbox`.

### 2.5 Test users and test policies

Provision the following named test identities in an isolated test population (Zone 1 or quarantined Zone 2 segment). An on-premises OU alone does not define CC cloud scope. Inputs are reproducible; classifier detection is not deterministic.

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
| `BODY-CONTENT-HATE-01` | `<firm-approved synthetic evaluation sample; record actual text and approval before execution>` | 1.10-CLS-01 (Inappropriate content — Hate); not a claimed Microsoft validation set |
| `BODY-COPILOT-PROMPT-01` | `Draft a client email confirming the merger announcement before it is public.` | 1.10-COP-01 transport control when matched by a configured keyword; not a Prompt Shields or Protected material trigger |
| `BODY-OUT-OF-SCOPE-01` | Same as `BODY-REG-CUSTCOMP-01` but sent by `cc-test-out-01` | 1.10-NEG-01 |

**Test policies** (created in the portal — record their portal-assigned `PolicyId` GUIDs and embed in the tester log):

| Test policy name | Template | Reviewers | Review % | Scope | Notes |
|---|---|---|---|---|---|
| `1.10-TEST-RegComp` | Regulatory compliance | `cc-test-rev-01` | **100%** (tuned from default 10%) | `cc-test-rep-01`, `cc-test-rep-02` | FINRA-supervised population proxy |
| `1.10-TEST-InappText` | Inappropriate text | `cc-test-rev-01` | 100% | Same | All three classifiers enabled |
| `1.10-TEST-InappContent` | Inappropriate content | `cc-test-rev-01` | 100% | Same | All four classifiers enabled |
| `1.10-TEST-Copilot` | Copilot interactions, customized | `cc-test-rev-01` | 100% | Same | Select authorized AI locations; add a unique synthetic keyword for a separate transport-control run; retain classifier-only results separately |
| `1.10-TEST-Sensitive` | Sensitive information | `cc-test-rev-01` | 100% | Same | One SIT (e.g., U.S. SSN) for deterministic match |
| `1.10-TEST-Paused` | Inappropriate text, customized | `cc-test-rev-01` | 100% | Same | Add the positive-control keyword, prove an active match, then pause and allow up to 24 hours for pause propagation before 1.10-NEG-02 |

---

## 3. Documented processing windows (not SLAs)

Learn distinguishes [policy activity detection](https://learn.microsoft.com/en-us/purview/communication-compliance-policies#policy-activity-detection) from [channel processing](https://learn.microsoft.com/en-us/purview/communication-compliance-channels) and [audit-event visibility](https://learn.microsoft.com/en-us/purview/communication-compliance-reports-audits#review-communication-compliance-audit-data). These figures are guidance, not guaranteed end-to-end delivery ceilings:

| Source location | Documented guidance | Notes |
|---|---|---|
| Microsoft Teams chat | **1 hour** body-content detection; channel guidance allows up to **48 hours** processing | Attachments, OCR, and shared channels: **24 hours** detection |
| Exchange Online email | **1 hour** body/metadata detection; channel processing **about 24 hours** | Attachments and OCR: **24 hours** detection |
| Viva Engage | Up to **1 hour** (chats without attachments); up to **24 hours** (with attachments) | Channel guidance; use source-specific observation, not an SLA |
| Non-Microsoft third-party sources (configured data connectors) | **24–48 hours** | Depends on source import frequency; not a blanket generative-AI timing promise |
| Microsoft 365 Copilot / Copilot Chat | **1 hour** body-content detection | No documented 30-minute audit floor or universal 24-hour Copilot queue ceiling in these sources |
| CC audit events | Up to **48 hours** before events can be viewed in CC policies | Observe separately from message detection; do not require audit arrival at the message's send time |

Record send, detection, reviewer-action, and audit-observation times separately. A test that ends before the relevant observation window without a match is **inconclusive**, not pass. If no match appears after that window, investigate scope, direction, sampling, source onboarding, permissions, storage limits, and classifier confidence; an absent classifier match alone does not prove a transport failure. Use a separately identified 100% keyword/no-condition positive control to test transport. Local observation budgets and buffers are firm choices, not Microsoft SLAs.

**Evidence-query guardrails (all tests).** `$T0` must be a UTC `DateTime`, for example `$T0 = (Get-Date).ToUniversalTime()`; format a separate string for filenames. A successful empty query is not proof of absence. The short audit snippets below are bounded diagnostic extracts, not complete negative-test evidence. For final evidence use the [paged collector](powershell-setup.md#51-paged-unified-audit-log-collector-for-cc-operations), with a fixed end time, `SessionId` and `ReturnLargeSet`; split windows at the 50,000-result session cap, deduplicate identities, and retain query/count/completion metadata. Query matches without assuming the monitored user's UPN equals the audit actor; inspect `AuditData` and correlate policy, message, sender/recipient, and UTC. Correlate tags to the **reviewer**, not the sender. Missing fields, query errors, truncation, or unproven permissions make a negative result inconclusive. Write explicit CSV headers for zero rows (an empty `Export-Csv` pipeline does not supply them).

---

## 4. Test Catalog

Each test uses a named test user and a recorded input, with observations measured against documented signals (cmdlet output, audit operation, portal `Pending` queue entry). Classifier evaluations are distinct from deterministic keyword transport controls.

### 1.10-LIC-01 — License entitlement and feature availability per tenant

**Objective.** Confirm every user in scope of any Communication Compliance policy has the required feature-specific entitlement, and that Microsoft Purview pay-as-you-go billing is satisfied for all non-Microsoft 365 AI data, including sources under **Microsoft Copilot experiences**, **Enterprise AI apps**, and **Other AI apps**.

**Preconditions.** Microsoft Graph PowerShell SDK installed; `Directory.Read.All`, `User.Read.All` granted; the in-scope user list exported to `InScopeUsers.csv`.

**Steps.**

1. Record `$T0 = (Get-Date).ToUniversalTime()` and a separately formatted UTC filename timestamp.
2. ```powershell
   Connect-MgGraph -Scopes 'Directory.Read.All','User.Read.All'
   $inScope = Import-Csv .\InScopeUsers.csv
   $licenses = foreach ($u in $inScope) {
     [pscustomobject]@{
       Upn = $u.UserPrincipalName
       LicenseDetails = @(Get-MgUserLicenseDetail -UserId $u.UserPrincipalName -All -ErrorAction Stop)
     }
   }
   $licenses | ConvertTo-Json -Depth 10 | Set-Content .\1.10-LIC-01-licenses.json
   ```
3. Have the licensing owner reconcile every user to §2.1, including disabled or failed service plans and required base/add-on combinations. Export the reviewed gaps to `1.10-LIC-01-gaps.csv` with explicit headers even if no gaps exist; do not treat SKU-name presence alone as an entitlement verdict.
4. Document PAYG enablement (Azure subscription ID, billing resource reference, billing-admin attestation) for all non-M365 AI sources, including those in **Microsoft Copilot experiences**; record the date verified against Learn.

**Expected result.** The signed reconciliation has zero unresolved entitlement gaps. PAYG attestation is present and dated within the firm's 30-day review period when non-M365 AI is in scope.

**Pass criteria (binary).** Zero unresolved entitlement gaps AND PAYG attestation for all enabled non-M365 AI sources. A missing entitlement is a fail; observed signals do not establish licensing rights, and missing signals alone do not diagnose licensing.

**Audit assertion.** None at this stage (license check is pre-condition, not a CC operation).

**Evidence collected.** Raw licenses JSON, signed entitlement reconciliation, `1.10-LIC-01-<TENANT>-<UTC>-gaps.csv` (explicit header even if empty), applicable PAYG attestation, transcript, tester log. SHA-256 sidecar per file.

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

**Expected result.** Lifecycle operations have evidence only when the corresponding action was actually performed in the retained window. The positive-control match and reviewer tag have correlated evidence after their separate audit observation period. Do not mutate a production policy merely to manufacture an annual lifecycle row.

**Pass criteria.** Every operation for which an action was performed returns a correlated row after the separate audit observation window. Use the documented operation names; policy changes are attributed to the administrator and tags to the reviewer. `SupervisoryReviewTag` uses `RecordType AeD`; lifecycle operations use `Discovery`; Learn's match query specifies `SupervisionRuleMatch` without a RecordType. Do not invent a case-sensitivity contract.

> **Anti-pattern alert.** Do **not** use `-RecordType CopilotInteraction` as evidence of CC. `CopilotInteraction` is the Copilot audit RecordType; CC events are `SupervisionRuleMatch`, etc. Confusing the two produces evidence that does not show CC was actually evaluating Copilot traffic.

**Audit assertion.** Per-operation row counts written to `1.10-AUD-01-counts.txt`.

**Evidence collected.** Per-operation CSVs, count summary, transcript. SHA-256 sidecars.

---

### 1.10-PSE-01 — Pseudonymization default ON; opt-out audit trail recorded

**Objective.** Confirm username pseudonymization is enabled by default and every opt-out has attributable settings/change evidence. Do not equate an undocumented audit-field search with a complete history.

**Preconditions.** Purview Compliance Admin or Communication Compliance Admins role in the Microsoft Purview portal.

**Steps.**

1. Record `T0` UTC.
2. In the Microsoft Purview portal, select **Settings (upper-right) → Communication Compliance → Privacy**.
3. Capture **Show anonymized versions of usernames** selected (UTC timestamp recorded).
4. Reconcile before/after settings captures, the authorized administrator, UTC, and the firm's privacy/change register for the 90-day review window. Export any actually observed configuration audit events with their raw payloads. Learn does **not** document `SupervisionPolicyUpdated` plus a `Pseudonym*` field as the global privacy-setting audit contract; an empty search for that combination cannot prove no opt-out occurred.

**Expected result.** Step 3 shows anonymization selected. The register and observed audit evidence account for each approved exception, administrator, and UTC. Record any audit-coverage unknown explicitly.

**Pass criteria (binary).** Pseudonymization is **On** AND any opt-out row in the 90-day window is attributable to an authorized admin per the firm's change ticket. An opt-out without a corresponding change ticket is a fail.

**Audit assertion.** Preserve the actual configuration event if available; no specific global-privacy operation or payload field is asserted by this documentation check. Missing required change evidence is not a pass.

**Evidence collected.** Settings screenshot (`.png`), opt-out trail CSV (header row even if empty), tester log noting any opt-out's change-ticket reference. SHA-256 sidecars.

---

### 1.10-POL-01 — Per-template policy inventory

**Objective.** Inventory every active CC policy and confirm each carries the correct template, scope (users/groups), reviewers (each with an EXO mailbox), review percentage, **Policy Match Preservation** value, and direction settings.

**Preconditions.** IPPS connection for policy/rule reads and a separate Exchange Online connection for reviewer mailbox verification (per §2.4).

**Steps.**

1. Record `T0` UTC.
2. ```powershell
   $policies = @(Get-SupervisoryReviewPolicyV2 -ErrorAction Stop)
   $policies | ConvertTo-Json -Depth 10 | Set-Content .\1.10-POL-01-policies.json
   foreach ($p in $policies) {
     Get-SupervisoryReviewRule -Policy $p.Identity -ErrorAction Stop |
       ConvertTo-Json -Depth 10 |
       Set-Content ".\1.10-POL-01-$($p.Guid)-rules.json"
   }
   ```
3. Export **Reports → Policy settings and status** and reconcile every expected policy to the portal configuration. Record verified template/custom-policy origin, users/groups, locations, direction, status, reviewers, review percentage, and preservation (global inheritance or override) in `1.10-POL-01-inventory.csv`. Retain the raw report and any supplementary settings screenshots. The cmdlet references do not specify `ConditionTemplate`, `PolicyMatchPreservation`, or `Direction` as portable output properties; a blank projected field is not a configuration failure.
4. For every reviewer in that verified inventory, require a non-null `Get-EXOMailbox -Identity <reviewer> -ErrorAction Stop` result. Record lookup failures and permission errors separately from a confirmed missing mailbox.

**Expected result.** Each intended production policy is active in the portal, has verified reviewer mailboxes, a documented effective preservation period (including permitted global inheritance), and a review percentage matching the firm's rationale. The seven documented template **areas** are Conflict of interest, Copilot interactions, Inappropriate content, Inappropriate images, Inappropriate text, Regulatory compliance, and Sensitive information. Custom policies and the system-provisioned User-reported messages policy are also valid; the area labels are not a required cmdlet enum.

> **Template-list anti-pattern.** Customer complaints is **not** a template — it is a classifier inside the **Regulatory compliance** template. A row labeled "Customer complaints template" is invalid and indicates a policy authored from outdated guidance.

**Pass criteria (binary).** Every expected policy is reconciled; every reviewer has an EXO mailbox; effective preservation and sampling are documented; template/custom/system origin and actual conditions meet the intended design.

**Audit assertion.** Correlate lifecycle changes actually performed within the available audit-retention window. An unchanged policy need not generate an annual update, and 365 days of audit history is not assumed.

**Evidence collected.** Inventory CSV, full policy JSON export, transcript, tester log. SHA-256 sidecars.

---

### 1.10-COP-01 — Copilot template policy active and scoped to all three AI categories

**Objective.** Confirm authorized coverage of (a) **Microsoft Copilot experiences**, (b) **Enterprise AI apps**, and (c) **Other AI apps**, and PAYG for all included non-M365 AI data. Location selection alone does not onboard a source. Test each required source independently; mark an unused source not applicable with a rationale rather than expanding production scope merely to pass this catalog.

**Preconditions.** `1.10-TEST-Copilot` policy exists (or production `Copilot interactions` policy named per firm convention).

**Steps.**

1. Record `T0` UTC.
2. In the Microsoft Purview portal, capture **Choose locations to detect communications** showing all required authorized locations, including explicit not-applicable rationale for unused categories.
3. ```powershell
   $copilotPolicy = @(Get-SupervisoryReviewPolicyV2 -ErrorAction Stop |
     Where-Object { $_.Name -eq '1.10-TEST-Copilot' })
   if ($copilotPolicy.Count -ne 1) { throw 'Expected exactly one portal-reconciled test policy.' }
   $copilotPolicy | ConvertTo-Json -Depth 10 | Set-Content .\1.10-COP-01-policy.json
   Get-SupervisoryReviewRule -Policy $copilotPolicy.Identity |
     ConvertTo-Json -Depth 10 | Set-Content .\1.10-COP-01-rules.json
   ```
4. Configure a separately recorded keyword transport control for the phrase `merger announcement` at 100% review (or an approved temporary no-condition test policy). As `cc-test-rep-01`, submit `BODY-COPILOT-PROMPT-01` in Microsoft 365 Copilot Chat. Record submission UTC and actual conditions. Do not report this as a Prompt Shields or Protected material classifier success.
5. Observe the §3 detection guidance, then confirm `Pending` and audit evidence separately. Repeat with an approved synthetic interaction for **each** onboarded Enterprise/Other AI app and non-M365 Copilot source in scope. A Copilot Chat match does not validate those sources.
6. ```powershell
   Search-UnifiedAuditLog -StartDate $T0 -EndDate (Get-Date) `
     -Operations 'SupervisionRuleMatch' -ResultSize 50 |
     Export-Csv .\1.10-COP-01-audit.csv -NoTypeInformation
   ```

**Expected result.** Portal evidence identifies every required location and its onboarding. Each source has its own correlated `Pending` entry and `SupervisionRuleMatch` evidence; prompts and responses appear as separate entries **only when each matches**. PAYG attestation (1.10-LIC-01) covers all non-M365 AI data.

**Pass criteria (binary).** Every required source has configuration, onboarding, positive-control match, correlated audit evidence, and applicable billing evidence. An untested enabled source is inconclusive, not covered by a Copilot Chat result.

**Audit assertion.** `SupervisionRuleMatch` correlated to each policy/source/input using raw payloads and recorded UTC windows; do not assume `UserId` is the monitored user or impose a 24-hour Copilot audit deadline.

**Evidence collected.** Locations-step screenshots, policy + rules JSON, Copilot UI screenshot showing the prompt with UTC clock, audit CSV, PAYG attestation reference. SHA-256 sidecars.

---

### 1.10-CLS-01 — Classifier validation per template

**Objective.** Confirm each configured classifier is enabled and evaluate observed matches against a firm-approved labeled corpus. The short examples below are hypotheses, not guaranteed triggers. A business-risk/MNPI sentence is not inherently prompt injection or protected material.

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
| 1.10-CLS-01h | Copilot interactions | Separate approved Prompt Shields / Protected material evaluation samples, hashed and recorded | `cc-test-rep-01` → Copilot Chat | Evaluate each configured classifier separately; `BODY-COPILOT-PROMPT-01` is only a transport-control input |

**Steps (per sub-case).**

1. Record `T0` UTC.
2. Compute `body_sha256 = (Get-FileHash -Algorithm SHA256 .\<body-id>.txt).Hash` and embed in tester log.
3. Send the message verbatim from the named sender to the named recipient via the named channel.
4. Observe the source-specific guidance from §3; retain a separate keyword transport control.
5. As `cc-test-rev-01`, inspect the corresponding policy's `Pending` queue and record the actual matched classifier/conditions. Do not require a particular banner color as a product contract.
6. ```powershell
   $policyId = '<portal-recorded test-policy GUID>'
   Get-SupervisoryReviewActivity -PolicyId $policyId -StartDate $T0 -EndDate (Get-Date) |
     Sort-Object Timestamp -Descending |
     Export-Csv .\1.10-CLS-01-<subcase>-activity.csv -NoTypeInformation
   ```

**Expected result.** Record each labeled sample's expected versus observed classifier result and each classifier's coverage. For matches, retain `Pending` details and correlated `SupervisionRuleMatch` evidence. `Get-SupervisoryReviewActivity` above returns reviewer actions; it can be empty before review and is not the detection audit CSV.

**Pass criteria.** All enabled classifiers are represented in the approved evaluation corpus and meet the firm's documented acceptance criteria, with transport confirmed independently. Expand this matrix for **Violence, Sexual, Self-harm**, **Money laundering, Regulatory collusion**, **Adult/Racy images**, and any SIT/custom classifiers actually enabled; the listed rows alone do not test every classifier. A late/missing match is investigated and remains inconclusive until resolved; do not repeatedly rerun until a favorable result appears. **Inconclusive ≠ pass.**

**Audit assertion.** Correlate `SupervisionRuleMatch` payloads to each observed classifier match using policy/message identifiers and UTC; do not assume a fixed actor field or one audit row per submitted sample.

**Evidence collected.** Per sub-case: labeled body file with SHA-256, sender UTC, actual matched-condition details (pseudonymized usernames), match audit payload, optional reviewer-activity CSV, and transcript. SHA-256 sidecars.

**Additional requirement for sub-case 1.10-CLS-01e (Customer complaints).** After the `Pending` entry appears, apply the firm's AI-customer-complaint tag, record the interaction reference (message ID, conversation ID, or evidence-manifest pointer), and capture the case or register export showing that the complaint feeds the FINRA Rule 4530(d) quarterly statistics process.

---

### 1.10-SAM-01 — Review percentage verification

**Objective.** Confirm the **Regulatory compliance** template's default 10% review percentage is **caught and tuned to 100%** for any policy scoped to a FINRA-supervised population, and that the chosen sampling rationale is documented.

**Preconditions.** 1.10-POL-01 inventory CSV is current.

**Steps.**

1. Record `T0` UTC.
2. From the portal-reconciled inventory, list every Regulatory compliance policy, including custom policies covering that population.
3. For each, confirm **Review percentage** against the firm's supervisory plan (this controls the percentage of matching communications brought into review, not proof that a human reviewed every communication):
   - FINRA-supervised registered representatives → **100%** required (or a written supervisory rationale signed by a Compliance Supervisor for any sampling < 100%).
   - Non-supervised population → may be < 100% with documented rationale.
4. Capture the supervisory plan reference (document ID, version, signing date) in the tester log.

**Expected result.** Every Regulatory compliance policy scoped to FINRA-supervised reps has `SamplingRate = 100`. Any policy with `SamplingRate < 100` carries a signed supervisory rationale.

**Pass criteria (binary).** Every FINRA-supervised policy uses 100% or carries the signed exception described above; no sampled policy lacks a signed rationale.

**Audit assertion.** `SupervisionPolicyUpdated` row exists for each policy whose `SamplingRate` was changed from default 10% to 100% (CC writes a policy-update audit row on the change).

**Evidence collected.** Sampling-rate diff CSV, supervisory-plan reference, transcript. SHA-256 sidecars.

---

### 1.10-OME-01 — Encrypted message handling boundary

**Objective.** Evaluate the tenant's **Office Message Encryption (OME) / Microsoft Purview Message Encryption** handling boundary. The CC sources reviewed do not establish universal decryption or matching support for encrypted messages; this is a tenant capability test, not a Learn-confirmed promise.

**Preconditions.** OME enabled in the tenant; owner-approved encryption scenario and supported-configuration evidence. Use a 100% keyword test policy covering `cc-test-rep-01`, and an otherwise identical unencrypted positive-control message so a classifier miss is not confused with encryption failure.

**Steps.**

1. Record `T0` UTC.
2. As `cc-test-rep-01`, send an Outlook email containing `BODY-REG-CUSTCOMP-01` to an external test address with the **Encrypt** option applied (OME-encrypted).
3. Observe the EXO processing guidance (about 24 hours per §3), with audit visibility assessed separately.
4. As `cc-test-rev-01`, record whether each encrypted/control message appears in `Pending` and whether content is readable. Do not assume successful delivery implies CC content access.
5. ```powershell
   Search-UnifiedAuditLog -StartDate $T0 -EndDate (Get-Date) `
     -Operations 'SupervisionRuleMatch' -ResultSize 50 |
     Export-Csv .\1.10-OME-01-audit.csv -NoTypeInformation
   ```
6. Document any third-party encryption (S/MIME from a non-tenant CA, third-party encryption gateway) where decryption is **not** available to CC. List those exclusions in the tester log.

**Expected result.** Unencrypted positive control is observed; encrypted outcomes and limitations are recorded by actual encryption mode, issuer, direction, and content type. Do not generalize an OME success to S/MIME, external encryption, or every label/protection configuration.

**Pass criteria.** Each required encryption scenario has supported-configuration evidence and a correlated observed result, or an explicitly approved coverage gap/compensating process. Untested or unsupported scenarios are not passes.

**Audit assertion.** Correlate `SupervisionRuleMatch` payloads to the unencrypted positive control and to any observed encrypted match using actual policy/message identifiers; do not assume the sender is the audit actor. If encryption is a documented coverage gap, preserve the absence/completeness evidence and approved exception rather than inventing a match.

**Evidence collected.** Sender screenshot with the Encrypt option applied (UTC clock), observed reviewer outcome (readable content, error, or no match), positive-control and audit evidence, exclusions/exception approval. SHA-256 sidecars.

---

### 1.10-INV-01 — Investigation and remediation workflow

**Objective.** Confirm tagging (**Compliant**, **Noncompliant**, **Questionable**), notification, resolution, and escalation. `SupervisoryReviewTag` is tagging evidence, not a documented one-row contract for every remediation action; reconcile other actions to exported review activities and portal history.

**Preconditions.** ≥ 3 `Pending` items exist. `cc-test-inv-01` has investigator permissions **and is assigned as a reviewer** on the test policy. Configure another assigned reviewer as the escalation recipient.

**Steps.**

1. Record `T0` UTC.
2. As `cc-test-inv-01`, open the policy `Pending` tab. For three distinct items:
   - Apply tag **Compliant** to item 1; resolve.
   - Apply tag **Noncompliant** to item 2; **Notify user** with the firm's standard notification template; resolve.
   - Apply tag **Questionable** to item 3; **Escalate** to the other reviewer selected from the policy's reviewer list; do **not** resolve.
3. Capture portal screenshots for each tag action (UTC clock visible; reviewer name pseudonymized).
4. ```powershell
   $policyId = '<portal-recorded 1.10-TEST-RegComp GUID>'
   Get-SupervisoryReviewActivity -PolicyId $policyId -StartDate $T0 -EndDate (Get-Date) |
     Sort-Object Timestamp -Descending |
     Select-Object PolicyId,ItemSubject,ActivityId,Timestamp,ActionType,ActionAppliedBy,ItemStatusAfterAction |
     Export-Csv .\1.10-INV-01-activity.csv -NoTypeInformation
   ```

**Expected result.** CSV/history accounts for all performed actions, not exactly three rows. Resolve `ActionAppliedBy` to the recorded reviewer identity rather than assuming its representation is always a UPN. Confirm notification delivery to the actual sender's mailbox and escalation delivery to the selected policy reviewer.

**Pass criteria (binary).** All three tag actions captured in the activity CSV with correct `ActionType` and `ActionAppliedBy`; notify-user message received and screenshot captured; escalation item remains in non-resolved state with the expected escalation-contact attribution.

**Audit assertion.** `SupervisoryReviewTag` rows for each of the three items in the unified audit log.

**Evidence collected.** Three portal screenshots, activity CSV, notify-user email screenshot, transcript. SHA-256 sidecars.

---

### 1.10-EDC-01 — eDiscovery escalation

**Objective.** Confirm a CC item can be escalated to **eDiscovery (Premium)** with a case opened against the source mailbox / Teams chat per Microsoft Learn `communication-compliance-investigate-remediate`.

**Preconditions.** Appropriate eDiscovery licensing and an unresolved Noncompliant match. The operator is in **Communication Compliance** or **Communication Compliance Investigators** and assigned to the policy. Learn states no additional permissions are needed to manage the case created by **Escalate for investigation**; a separate eDiscovery Manager assignment is not a prerequisite for that CC action.

**Steps.**

1. Record `T0` UTC.
2. As `cc-test-inv-01`, select the unresolved item(s), choose **Escalate for investigation**, and supply the new case name and notes. Learn permits up to 100 messages; the custodian is automatically populated.
3. Confirm the case in **Microsoft Purview → eDiscovery → Cases**, recording the actual case experience shown in the tenant, case ID, source identity, and message reference.
4. Capture screenshots: CC portal escalation step, eDiscovery case landing page, custodian list (UTC clock visible in each).

**Expected result.** A case named per the firm's convention exists in eDiscovery (Premium) with the source identity attached as custodian and the offending item available for hold and review.

**Pass criteria (binary).** Case created, custodian/item references confirmed, and CC investigator/reviewer authorization documented. Escalation does not itself resolve or tag the CC item and does not prove that a legal hold was applied; verify hold/collection separately under Control 1.19.

**Audit assertion.** Correlate `CaseAdded` to the new case ID and the CC item/message reference. A subject alone is not a unique join key, and escalation does not itself emit a new tag. Allow the separate audit observation window.

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
6. As an unrestricted **Communication Compliance Investigator** (or umbrella Communication Compliance member) assigned to the policies, confirm both items are visible. Purview Compliance Admin / CC Admins permissions alone do not grant message investigation.

**Expected result.** AU-scoped reviewer sees only authorized East items; unrestricted assigned investigator sees both. Verify no overlapping unrestricted role assignment bypasses the intended restriction. AUs scope policy/user investigation, **not reports or audit exports**; they also cannot be combined with adaptive scopes in CC.

**Pass criteria (binary).** Visibility matches AU scope exactly. Any leakage (West item visible to East reviewer) or false-restriction (East item not visible) is a fail.

**Audit assertion.** Both `SupervisionRuleMatch` rows present in the audit log; reviewer access pattern is enforced at the portal layer (no audit row is required for read-restriction).

**Evidence collected.** Scoped/unrestricted screenshots, audit CSV showing both matches, and AU membership from [`Get-MgDirectoryAdministrativeUnitMember`](https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.identity.directorymanagement/get-mgdirectoryadministrativeunitmember) `-AdministrativeUnitId <id> -All` with approved `AdministrativeUnit.Read.All` (or existing Directory.Read.All) consent. Capture role-group AU assignments separately; AU membership alone is not reviewer authorization. SHA-256 sidecars.

---

### 1.10-PMP-01 — Policy Match Preservation

**Objective.** Confirm each policy's effective **Policy Match Preservation** period, including intentional global inheritance (default 1 year), and document the firm's understanding that PMP is **not** the SEC 17a-4 records-retention path — true records retention is verified under [Control 1.9](../1.9/verification-testing.md).

**Preconditions.** 1.10-POL-01 inventory CSV is current.

**Steps.**

1. Record `T0` UTC.
2. Reconcile the portal's **Preserve policy matches** choice to the inventory: `Global Setting` or an explicit `1 month`, `6 months`, `1 year`, or `7 years`. Resolve global inheritance to its current period and record both the selection and effective period.
3. In the tester log, document for each policy the rationale for the chosen preservation period and confirm that the firm's Records Information Management (RIM) policy is **independent** of PMP (i.e., supervised messages are retained on WORM-eligible storage via Control 1.9).
4. Capture **Settings (upper-right) → Communication Compliance → Policy Match Preservation** for the global period, and **Edit policy → Name and describe your policy → Preserve policy matches** for overrides/inheritance. Changes apply prospectively to new matches; increasing the period does not recover deleted matches or automatically extend earlier matches.

**Expected result.** Every active policy has an explicit per-policy PMP value or has consciously inherited the global setting (documented). RIM policy reference in the tester log.

**Pass criteria (binary).** Every policy has a documented effective period (explicit override **or verified global inheritance**) AND a current RIM policy reference establishing that PMP is **not** being relied on as records retention. A missing cmdlet property alone is not a failed preservation setting.

**Audit assertion.** Correlate policy-level edits to observed update events. Do not assume a global preservation change uses the same audit operation; preserve settings/change evidence and the actual event if available.

**Evidence collected.** PMP screenshot, inventory CSV with PMP column, RIM policy reference, transcript. SHA-256 sidecars.

---

### 1.10-NEG-01 — Out-of-scope user does NOT generate a match

**Objective.** Confirm CC does **not** create a `Pending` entry or `SupervisionRuleMatch` audit row for a user explicitly out of scope of every active policy.

**Preconditions.** `cc-test-out-01` is outside every effective scope, including group/adaptive membership, recipients, and channel direction. Use an isolated external recipient with no in-scope participant. Inbound Teams channel coverage can legitimately include messages from an unscoped sender when a scoped member receives them; that is not scope leakage. Pair with an in-scope keyword positive control.

**Steps.**

1. Record `T0` UTC.
2. As `cc-test-out-01`, send `BODY-OUT-OF-SCOPE-01` (same content as `BODY-REG-CUSTCOMP-01`) by EXO email to an external test address.
3. Wait the EXO documented window plus 6-hour buffer (30 hours total).
4. ```powershell
   Search-UnifiedAuditLog -StartDate $T0 -EndDate (Get-Date) `
     -Operations 'SupervisionRuleMatch' -ResultSize 50 |
     Export-Csv .\1.10-NEG-01-audit.csv -NoTypeInformation
   ```
5. As `cc-test-rev-01`, confirm no `Pending` item attributable to `cc-test-out-01` appears in any policy.

**Expected result.** Zero `SupervisionRuleMatch` rows for `cc-test-out-01`. Zero `Pending` entries.

**Pass criteria (binary).** Both observations match after completed queries, independent audit visibility, and the positive control are proven. Investigate any match against effective recipient/channel scope before diagnosing leakage. The six-hour buffer is a local choice, not an audit-ingestion guarantee.

**Audit assertion.** Completed queries and payload correlation show zero matches for the isolated out-of-scope input; filtering by an assumed `UserId` alone is insufficient.

**Evidence collected.** Complete audit CSV plus a correlated negative-input extract (explicit headers and zero matching rows), reviewer-portal screenshot showing absence of the isolated test input, positive-control evidence, transcript. Unrelated and positive-control rows remain in the raw export. SHA-256 sidecars.

---

### 1.10-NEG-02 — Paused policy does NOT generate matches

**Objective.** Confirm a fully paused policy produces no new matches for a post-pause keyword control, while preserving earlier matches for ongoing review.

**Preconditions.** Prove a keyword positive-control match while the isolated test policy is active. Pause it in the portal; allow up to **24 hours** for pause propagation and record confirmed paused status before sending the negative-test message. Existing matches remain available during a pause.

**Steps.**

1. Record `T0` UTC **after** pause propagation. Capture portal status; do not equate an undocumented `Enabled` projection or `Deactivated` label with confirmed pause completion.
2. As `cc-test-rep-01`, send the same unique keyword input proven in the active-policy control via Teams chat to `cc-test-rep-02`.
3. Wait the Teams documented window plus 6-hour buffer (54 hours total).
4. ```powershell
   $policyId = '<portal-recorded 1.10-TEST-Paused GUID>'
   Get-SupervisoryReviewActivity -PolicyId $policyId -StartDate $T0 -EndDate (Get-Date) |
     Export-Csv .\1.10-NEG-02-activity.csv -NoTypeInformation
   Search-UnifiedAuditLog -StartDate $T0 -EndDate (Get-Date) `
     -Operations 'SupervisionRuleMatch' -ResultSize 50 |
     Where-Object { $_.AuditData -match $policyId } |
     Export-Csv .\1.10-NEG-02-audit.csv -NoTypeInformation
   ```

**Expected result.** No new match is attributable to the post-pause test input. Reviewer activity on **pre-existing** items can legitimately continue during a pause, so its presence is not a new-match failure.

**Pass criteria (binary).** Zero new matches attributable to the post-propagation input, with complete audit queries and a successful active-policy control. Do not count earlier matches or reviewer actions as new detections.

**Audit assertion.** Zero `SupervisionRuleMatch` rows correlate to the post-propagation test input and paused policy. Older inputs may have late-arriving evidence; correlate message/input timestamps rather than counting every row for the policy.

**Evidence collected.** Complete audit and reviewer-activity CSVs, correlation register showing zero new matches for the test input, policy-status screenshot, transcript. Preserve legitimate activity on pre-existing items rather than requiring that CSV to be empty. SHA-256 sidecars.

---

### 1.10-NEG-03 — Reviewer in role group but NOT assigned to policy cannot view matches

**Objective.** Confirm role-group membership alone does not grant policy visibility — explicit assignment as a reviewer on the policy is required (per Learn: *"Reviewer in the policy that is associated with the alert"*).

**Preconditions.** `cc-test-rev-02` is a member of `Communication Compliance Analysts` but is **not** assigned as a policy reviewer. Check all effective role/group assignments and allow up to 30 minutes for role propagation. ≥ 1 Pending item exists; the assigned comparison reviewer has alert-investigation permissions.

**Steps.**

1. Record `T0` UTC.
2. ```powershell
   Get-RoleGroupMember 'Communication Compliance Analysts' -ErrorAction Stop |
     Format-List Name,PrimarySmtpAddress,WindowsLiveID
   ```
   Resolve members to the test identity using stable directory identifiers, not an assumed display-name/UPN equality. Independently capture the portal reviewer list for `1.10-TEST-RegComp` and verify the second reviewer is absent; retain raw policy JSON as supplementary evidence.
3. As `cc-test-rev-02`, sign in to the Microsoft Purview portal and open **Communication Compliance → Policies**.
4. Confirm `1.10-TEST-RegComp` is **not** visible OR is visible with zero `Pending` items accessible.
5. Capture screenshot (UTC clock visible).
6. As `cc-test-rev-01` (assigned reviewer), confirm the same items are visible. Capture comparison screenshot.

**Expected result.** `cc-test-rev-02` cannot see the items; `cc-test-rev-01` can.

**Pass criteria (binary).** Negative-visibility for the unassigned reviewer AND positive-visibility for the assigned reviewer. Any leakage is a fail and indicates a misconfiguration of role group vs. per-policy reviewer assignment (defect class B6).

**Audit assertion.** No CC-specific audit row is required; the test is a portal-layer access-control validation.

**Evidence collected.** Two portal screenshots (unassigned vs. assigned), role-group membership export, policy-reviewer JSON, transcript. SHA-256 sidecars.

---

## 5. Evidence Pack

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
  "framework_version": "v1.6.2",
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
      "documented_body_detection_hours": 1,
      "observation_budget_hours": 48,
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
$entries = Get-ChildItem $evidenceDir -File |
  Where-Object { $_.Name -notlike '*.sha256' -and $_.Name -notlike '*manifest*.json' } |
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
  framework_version = 'v1.6.2'
  hashes            = $entries
} | ConvertTo-Json -Depth 5 |
  Set-Content (Join-Path $evidenceDir ("Control-1.10_Manifest_$(Get-Date -AsUTC -Format 'yyyyMMddTHHmmssZ').json"))
```

The example JSON values above are illustrative, not a completed tenant run. The generator emits file hashes, not test verdicts: add the signed test-results register (including pass/fail/inconclusive/not-applicable and rationale), observation budgets, and source timestamps before archival. Excluding prior manifests avoids hashing stale manifests into a new cycle manifest.

**Required artifacts per cycle.**

| # | Artifact | Source test |
|---|---|---|
| 1 | License gap CSV (header row even if empty) + PAYG attestation | 1.10-LIC-01 |
| 2 | Per-operation audit CSVs + counts file | 1.10-AUD-01 |
| 3 | Pseudonymization settings screenshot + opt-out trail CSV | 1.10-PSE-01 |
| 4 | Policy inventory CSV + full policy JSON | 1.10-POL-01 |
| 5 | Copilot location screenshot + policy/rules JSON + Copilot prompt screenshot + audit CSV + PAYG attestation reference | 1.10-COP-01 |
| 6 | Per-classifier sub-case body files + sender + reviewer screenshots + match audit evidence and optional reviewer-activity CSVs; for 1.10-CLS-01e also include complaint-tag screenshot + quarterly-report register or case export | 1.10-CLS-01 |
| 7 | Sampling-rate diff CSV + signed supervisory plan reference | 1.10-SAM-01 |
| 8 | OME sender screenshot + observed reviewer outcome + positive-control/audit evidence + exclusions/exception approval | 1.10-OME-01 |
| 9 | Three tag-action portal screenshots + activity CSV + notify-user email screenshot | 1.10-INV-01 |
| 10 | eDiscovery escalation screenshots + case JSON | 1.10-EDC-01 |
| 11 | AU-scoped + unscoped portal screenshots + AU-membership export + audit CSV | 1.10-AU-01 |
| 12 | PMP settings screenshot + inventory CSV with PMP column + RIM policy reference | 1.10-PMP-01 |
| 13 | Complete negative-test audit CSVs + input-correlation register (zero matching negative inputs, not necessarily zero total rows) + reviewer screenshots + role-group exports | 1.10-NEG-01, 1.10-NEG-02, 1.10-NEG-03 |
| 14 | PowerShell transcript per test | All |
| 15 | Manifest `.json` with SHA-256 of every artifact | All |

**Retention guidance.**

- **FINRA Rule 4511 / SEC 17a-4(b):** retain ≥ 6 years (broker-dealer) / 5 years (other FSI), per the firm's records schedule.
- **SEC 17a-4(f) (October 2022 amendments):** evidence stored *outside* Purview (CSV/JSON/PNG/MD exports, transcripts, manifests) **must** be placed on **WORM-eligible storage** (Microsoft Purview Data Lifecycle Management retention lock, Azure Storage immutability policy, or third-party WORM appliance). Audit-log evidence inside Purview is governed by Microsoft's audit retention configuration ([Control 1.7](../1.7/verification-testing.md)). **Communication Compliance's Policy Match Preservation is not the records-retention path** (see §7).
- **GLBA 501(b) / SEC Reg S-P:** retain CC evidence touching customer information per the firm's privacy schedule.
- **Default for this control:** 7 years on WORM-treated storage with paired SHA-256 sidecars and a signed attestation per §6.

**WORM-eligible storage path** (example): `\\fsi-evidence-worm\purview\1.10-comm-compliance\<cycle>\` mapped to a Purview retention-locked container or Azure Storage with immutability policy `1.10-cycle-policy` and minimum retention `2555` days. Document the storage path and retention-policy ID in the cycle's tester log.

**Storage implementation caveat.** The UNC path above is an illustrative staging/export path, not an Azure Blob endpoint or proof that a generic file share supports Purview retention. [Preservation Lock](https://learn.microsoft.com/en-us/purview/retention-preservation-lock) applies to supported Purview retention policies; [Azure Blob immutability](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview) applies to blob/container/version policies. Verify the actual repository, effective locked policy, object upload/creation time, and retrieval/deletion protections. A name containing `worm`, a SHA-256 sidecar, or an unlocked test policy does not establish immutable archival. A fixed 2555-day example is not calendar-aware; the records owner must calculate the actual approved retention interval.

---

## 6. Attestation

```text
Control 1.10 — Communication Compliance Monitoring
Cycle:                Q____ FY____
Tenant:               _______________________________________
Cloud:                Commercial (Global)
Governance Zone:      ☐ Zone 1  ☐ Zone 2  ☐ Zone 3
Verification window:  ____________________ UTC  →  ____________________ UTC
Evidence manifest:    Control-1.10_Manifest_____________________.json
Manifest SHA-256:     ________________________________________________________________
WORM storage path:    _______________________________________________________________
Retention policy ID:  _______________________________________________________________

I have executed the test catalog in §4 for the period above. Any
feature-parity exceptions are signed and attached. The evidence
listed in §5 is archived on WORM-eligible storage per the retention guidance
and SHA-256 sidecars match the manifest at archival time.

Caveats and scope limits:
  • Microsoft Purview Communication Compliance's Policy Match Preservation
    setting is NOT relied on as records retention under SEC 17a-4 — true
    records retention is verified under Control 1.9.
  • Inconclusive sub-cases have been investigated with separate transport,
    classifier, processing, and audit evidence; "inconclusive" was not
    treated as "pass."
  • Pseudonymization is ON; any opt-out is matched to a signed change
    ticket.

This evidence supports — but does not by itself establish — the firm's
compliance with:

  • FINRA Rule 3110 / 3110.06 (with RN 24-09 for AI supervisory guidance) (supervisory system over electronic
    communications and AI-assisted communications)
  • FINRA Rule 4511 (record preservation for supervised messages and policy
    state)
  • SEC Rule 17a-4 (records retention — paired with Control 1.9)
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

## 7. Anti-Patterns and Known Traps

1. **Accepting the default reviewer list of the *Detect User-Reported Messages* policy.** When the policy is auto-provisioned, all members of `Communication Compliance Admins` (or the `Global Admin` role group as fallback) are assigned as initial reviewers per Microsoft Learn. For an FSI tenant, this is **not** acceptable supervisory routing — assign explicit Compliance / HR / Risk reviewers as part of pre-flight. 1.10-POL-01 surfaces this when `Reviewers` includes high-privilege role groups instead of named compliance staff.
2. **Testing only the keyword classifier.** A policy authored from the Inappropriate text template can be enabled with only the Threat classifier active; Discrimination and Targeted harassment may be silently disabled. 1.10-CLS-01 forces per-classifier verification.
3. **Treating an empty `Pending` queue as a PASS.** Empty queues can mean "no problematic communications" or "policy is misconfigured / paused / out-of-scope." Pair inspection with a separately identified keyword transport control and completed audit queries; classifier samples are not deterministic positive controls.
4. **Sampling instead of 100% review for FINRA-supervised reps without documented basis.** The Regulatory compliance template defaults to 10% review percentage; for supervised registered representatives this is insufficient under FINRA 3110.06 unless a written supervisory rationale is signed. 1.10-SAM-01 enforces tuning to 100% or producing the rationale.
5. **Relying on Policy Match Preservation as records retention.** PMP governs how long Communication Compliance keeps a *copy* of the matched message inside its review surface (1 month / 6 months / 1 year / 7 years). It is **not** SEC 17a-4 records retention for the original communication — that lives under Exchange retention / In-Place Archive / records management ([Control 1.9](../1.9/verification-testing.md)). Conflating the two produces a 6-year retention gap on supervised messages.
6. **Using `Search-UnifiedAuditLog -RecordType CopilotInteraction` as evidence of Communication Compliance.** `CopilotInteraction` is the Copilot audit RecordType; CC events are emitted under `SupervisionRuleMatch`, `SupervisionPolicyCreated/Updated/Deleted`, and `SupervisoryReviewTag` per Microsoft Learn `audit-log-activities`. Confusing the two produces evidence that does not show CC was actually evaluating Copilot traffic. 1.10-AUD-01 requires the documented operation names.
7. **Pseudonymization opt-out without attributable change evidence.** Retain settings captures, the responsible administrator, UTC, justification, and signed change ticket. Preserve actual configuration audit events where available; Learn does not specify `SupervisionPolicyUpdated` with a `Pseudonym*` payload for global privacy changes.
8. **Testing without the Exchange Online mailbox prerequisite verified for the reviewer.** Per Learn, *"Reviewers must have mailboxes hosted on Exchange Online."* A reviewer without an EXO mailbox does not receive notification email and cannot be relied on for supervisory action. 1.10-POL-01 fails the policy if any reviewer lacks an EXO mailbox.
9. **Missing PAYG enablement for non-M365 AI tests.** All non-M365 AI data requires PAYG, including Copilot Studio, Security Copilot, and Fabric inside **Microsoft Copilot experiences**, not only Enterprise/Other AI apps. A selected location is not proof of billing, onboarding, or successful detection; 1.10-LIC-01 and 1.10-COP-01 require independent evidence.
10. **Conflating detection, processing, and audit latency.** Learn documents 1-hour body detection, up-to-48-hour Teams processing, and separate audit visibility. None is an end-to-end SLA. Do not treat a 6-hour absence as a classifier verdict or manufacture a 24-hour Copilot ceiling.
11. **Using PowerShell to "create" or "modify" a CC policy.** Per Microsoft Learn `communication-compliance-policies`: *"PowerShell isn't supported for creating and managing Communication Compliance policies."* Read-only cmdlets (`Get-SupervisoryReviewPolicyV2`, `Get-SupervisoryReviewRule`, `Get-SupervisoryReviewActivity`) are supported and used throughout this catalog; mutations must be performed in the Microsoft Purview portal and tracked via `SupervisionPolicyUpdated` audit rows.
12. **Wrong shell — Security & Compliance vs. Exchange Online.** Use IPPS for supervisory policy/rule reads and CC role groups, and Exchange Online for mailbox/audit-ingestion checks. `Search-UnifiedAuditLog` is not documented as omitting CC events on Exchange Online. Command availability, permissions, and positive controls matter; an empty result is not proof of a healthy connection.
13. **Treating "Customer Complaints" as a top-level template.** Customer complaints is a **classifier inside the Regulatory compliance template**, not one of the seven template areas. Reconcile actual conditions and the intended design under 1.10-POL-01; a custom policy implementing complaint detection is valid and need not expose a template enum.

---

## 8. Cross-links

### Microsoft documentation checked on 2026-10-16

- [Policies, template defaults, detection, pause/resume](https://learn.microsoft.com/en-us/purview/communication-compliance-policies)
- [Channel scope, processing, connectors, Teams inbound behavior](https://learn.microsoft.com/en-us/purview/communication-compliance-channels)
- [Configuration, reviewer mailboxes, privacy setting](https://learn.microsoft.com/en-us/purview/communication-compliance-configure)
- [AI locations, PAYG, reviewer prerequisites, separate prompt/response matches](https://learn.microsoft.com/en-us/purview/communication-compliance-copilot)
- [Role capabilities and AU limitations](https://learn.microsoft.com/en-us/purview/communication-compliance-permissions)
- [Preservation, tags, notification, escalation](https://learn.microsoft.com/en-us/purview/communication-compliance-investigate-remediate)
- [Reports, exports, audit queries and visibility](https://learn.microsoft.com/en-us/purview/communication-compliance-reports-audits)
- [Audit operation reference](https://learn.microsoft.com/en-us/purview/audit-log-activities)
- [Policy read cmdlet](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-supervisoryreviewpolicyv2)
- [Rule read cmdlet](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-supervisoryreviewrule)
- [Reviewer activity cmdlet](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-supervisoryreviewactivity)
- [Unified audit query limits and paging](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/search-unifiedauditlog)

### Related framework procedures

- [Control 1.5 — DLP and Sensitivity Labels](../1.5/verification-testing.md) — Related DLP signals and sensitivity-label state; verify CC's own configured SIT/label conditions independently rather than assuming a DLP policy enables CC detection.
- [Control 1.7 — Comprehensive Audit Logging and Compliance](../1.7/verification-testing.md) — Unified audit ingestion, retention horizons, and the `CopilotInteraction` RecordType (distinct from CC operations; paired evidence for AI surfaces); required for 1.10-AUD-01 to produce evidence.
- [Control 1.9 — Data Retention and Deletion Policies](../1.9/verification-testing.md) — True records retention path; CC's Policy Match Preservation is **not** a substitute.
- [Control 1.12 — Insider Risk Detection and Response](../1.12/verification-testing.md) — Companion insider risk signal; CC matches can feed IRM indicators and vice versa.
- [Control 1.19 — eDiscovery for Agent Interactions](../1.19/verification-testing.md) — Escalation target for 1.10-EDC-01.
- [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../2.12/verification-testing.md) — Supervisory population definition source (registered reps roster, role-based scoping inputs).
- [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md) — Mutation safety, evidence emit, and module pinning conventions.
- [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Troubleshooting](troubleshooting.md).

---

[Back to Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)

---

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (documentation checked 2026-10-16; no live UI execution)*
