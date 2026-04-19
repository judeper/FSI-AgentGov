# Control 1.11 — Conditional Access and Phishing-Resistant MFA: Verification & Testing Playbook

**Control:** 1.11 — Entra Conditional Access + Phishing-Resistant MFA for AI Agents
**Pillar:** 1 — Security
**Audience:** Microsoft 365 administrator preparing evidence; auditor / compliance officer assembling examination binders for FINRA, SEC, NYDFS DFS-500, FFIEC, and OCC reviews.
**Sovereign-cloud scope:** Microsoft 365 Commercial, GCC, GCC High, DoD. 21Vianet (China) is treated as out-of-scope for this verification playbook because its Conditional Access (CA), Identity Protection, and Entra Agent ID feature surfaces materially diverge from Commercial parity and require an independent validator.
**Last UI verified:** April 2026
**Framework version:** v1.4

---

!!! warning "Scope Limit — What These Tests Confirm and Do Not Confirm"
    This verification playbook confirms the **access-control enforcement** layer of AI agent governance: that Conditional Access, phishing-resistant Authentication Strengths, Continuous Access Evaluation (CAE), Token Protection, and Privileged Identity Management (PIM) are configured, enforced, monitored, and evidenced for human makers, administrators, and (where supported) workload identities backing AI agents.

    These tests do **not** prove:

    - **Supervisory quality of agent output** — that registered-principal review under FINRA Rule 3110 is being performed at the cadence and depth the firm's written supervisory procedures require. See [Control 2.12 — Supervision and Oversight under FINRA Rule 3110](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).
    - **Model risk management effectiveness** — that the agent's grounding, prompts, retrieval, fine-tuning, and ongoing monitoring satisfy OCC Bulletin 2011-12 and Federal Reserve SR 11-7 expectations for material AI/ML systems. See [Control 2.6 — Model Risk Management Alignment with OCC 2011-12 / SR 11-7](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md).
    - **Books-and-records completeness** — that every conversational record, prompt, response, action, and decision was captured to immutable storage at the cadence FINRA Rule 4511 and SEC Rules 17a-3/17a-4 require, with WORM-equivalent retention. See [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

    All four control families — access control (1.11), supervisory review (2.12), model risk management (2.6), and books-and-records (1.7 / 1.9) — must operate **in combination** to support a defensible AI governance posture. A clean pass on this playbook is a necessary, but not sufficient, contribution to FINRA / SEC / NYDFS / FFIEC / OCC examination readiness.

!!! warning "Sovereign Cloud Availability"
    Conditional Access, Authentication Strengths, CAE, and PIM are generally available in Commercial, GCC, GCC High, and DoD. The following capabilities have **uneven sovereign-cloud parity** as of the verification date and must be re-confirmed against current Microsoft Learn release notes for the operating cloud at the start of every quarterly verification cycle:

    - **Conditional Access for Workload Identities** (TC-4) — generally available in Commercial; sovereign-cloud parity tracked per release wave. Where unavailable, the compensating control is a quarterly manual reconciliation worksheet (see §SOV, Control 3.6 §10 pattern).
    - **Token Protection (Preview)** (TC-6) — Windows-only preview surface; non-Windows endpoints have a **documented fallback**, not a silent bypass.
    - **Entra Agent ID** (referenced in TC-1, TC-4, TC-11) — Public Preview; surface and noun names continue to stabilise across 2026 release waves.
    - **Continuous Access Evaluation** (TC-5) — supported in Commercial, GCC, GCC High, DoD with per-app coverage that should be re-verified against the current Microsoft Learn CAE-supported-apps matrix each cycle.

    A `SKIPPED` evidence record with a pointer to the sovereign-cloud compensating-control worksheet is examiner-defensible; a silent omission is not.

---

## Document Conventions

This playbook is the **verification-and-testing** artifact for [Control 1.11 — Conditional Access and Phishing-Resistant MFA](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md). It is authored against framework version v1.4 and references Microsoft UI and API surfaces as last verified in April 2026.

- **Hedged regulatory language.** This playbook **supports compliance with** GLBA §501(b) and the FTC Safeguards Rule 16 CFR §314.4(c)(5) (MFA mandate, in force June 2023), SEC Regulation S-P (May 2024 amendments), SEC Rules 17a-3 and 17a-4 (records and retention), FINRA Rule 3110 (supervision), FINRA Rule 4511 (books and records), FINRA Regulatory Notice 21-18 (cybersecurity), FINRA Regulatory Notice 25-07 (generative-AI supervision), SOX Sections 302 and 404 (internal control over financial reporting), NYDFS 23 NYCRR Part 500 §500.12 (universal MFA, fully effective Nov 1, 2025), the FFIEC IT Examination Handbook (Information Security and Authentication booklets), NIST SP 800-63B (Authenticator Assurance Level 3), OCC Bulletin 2011-12 and Federal Reserve SR 11-7 (model risk management — applied to AI agent identities as model-bearing principals), CFTC Regulation 1.31 (recordkeeping), and CISA Zero Trust Maturity Model v2.0 (Identity pillar). A clean execution **does not guarantee** legal compliance, **does not replace** registered-principal supervisory review under FINRA Rule 3110 where that rule applies, and **does not substitute** for the firm's written supervisory procedures or its books-and-records program. Implementation requires organization-specific risk assessment and qualified-counsel review. Organizations should verify current Microsoft Learn documentation, sovereign-cloud feature parity, tenant entitlements, and per-app CAE coverage at every cycle.
- **Canonical role names.** This playbook uses the framework's canonical short-form role names: Entra Global Admin, Entra Security Admin, Authentication Policy Admin, Authentication Administrator, Entra Identity Governance Admin, Entra Agent ID Admin, AI Administrator, Power Platform Admin, Purview Compliance Admin, Exchange Online Admin, Sentinel Contributor, AI Governance Lead, Compliance Officer, CISO. No title substitution. (For example, "Global Administrator" is **not** a substitute for "Entra Global Admin"; "Compliance Administrator" is **not** a substitute for "Purview Compliance Admin"; "Power Apps Admin" is **not** a substitute for "Power Platform Admin".)
- **Surface terminology.** Sign-in evidence comes from two distinct Microsoft Sentinel / Microsoft Graph tables that are routinely conflated:
    - `SigninLogs` — interactive and non-interactive **human** sign-ins.
    - `AADServicePrincipalSignInLogs` — **service principal and workload identity** sign-ins (including AI agent backing identities). Agent sign-ins **do NOT appear in `SigninLogs`** — a frequent examiner finding. Every test case that touches an agent identity uses `AADServicePrincipalSignInLogs`.
    - `AuditLogs` — directory write operations (CA policy create/update/delete, role assignment changes, security-attribute changes).
    - `PowerPlatformAdminActivity` — Power Platform Admin Center change-log entries used to corroborate the report-only-to-enforce flip in TC-12.
- **Evidence retention.** Where evidence is **records-scope** under FINRA Rule 4511 or SEC Rule 17a-4, retention is **at least 7 years** with WORM-equivalent immutability via Microsoft Purview retention labels with deletion lock. Sentinel operational retention (typically 90 days hot, up to 2 years archived) is **not records-scope** and must not be relied upon as the system of record for audit-trail evidence.
- **No prohibited language.** This playbook does not use "ensures compliance", "guarantees", "will prevent", or "eliminates risk". Outcomes are stated as "supports", "helps meet", "is required for", "is recommended to", and "aids in", with implementation caveats.
- **PowerShell baseline.** PowerShell 7.4. Microsoft Graph PowerShell SDK ≥ 2.25.0 (`Microsoft.Graph.Identity.SignIns`, `Microsoft.Graph.Identity.DirectoryManagement`, `Microsoft.Graph.Identity.Governance`, `Microsoft.Graph.Beta.Identity.SignIns` for the workload-identity preview surfaces and Agent ID).
- **KQL baseline.** Microsoft Sentinel workspace with the `AzureActiveDirectory` data connector enabled and **all of** SignInLogs, NonInteractiveUserSignInLogs, ServicePrincipalSignInLogs, ManagedIdentitySignInLogs, AuditLogs, and (where the Power Platform connector is licensed) PowerPlatformAdminActivity selected.

---

## §0 Pre-Test Prerequisites

### 0.1 Operator role prerequisites

Verification reads from identity, sign-in, audit, Power Platform, and Sentinel surfaces. Read/write separation is enforced: every test case in TC-1 through TC-12 is **read-only** as far as the verifier is concerned. Any remediation derived from a FAIL routes to the sister [Portal Walkthrough](./portal-walkthrough.md), [PowerShell Setup](./powershell-setup.md), or [Conditional Access Agent Templates](./conditional-access-agent-templates.md) under its own change ticket and its own write scopes.

| Role (canonical) | Required for | PIM activation window |
|---|---|---|
| Entra Security Admin | Reads CA policy state, Authentication Strengths, named locations, sign-in logs | 4 hours, just-in-time |
| Authentication Policy Admin | Reads and (in remediation) writes Authentication Method policy, FIDO2 enablement, registration campaigns | 4 hours, just-in-time |
| Authentication Administrator | Reads per-user method registration; can reset methods only as part of an approved remediation | 4 hours, just-in-time |
| Entra Identity Governance Admin | Reads PIM eligible / active assignments, access reviews, lifecycle workflows | 4 hours, just-in-time |
| Entra Agent ID Admin | Reads Agent ID enrollment, sponsor assignments, agent custom security attributes | 4 hours, just-in-time |
| AI Administrator | Reads Agent 365 Admin Center, Copilot Studio environment posture, agent inventory | 4 hours, just-in-time |
| Power Platform Admin | Reads PPAC environment, maker, and DLP policy state; reads PPAC change-log for TC-12 | 4 hours, just-in-time |
| Purview Compliance Admin | Reads retention-label binding on evidence locations, UAL coverage | 4 hours, just-in-time |
| Sentinel Contributor / Reader | Runs KQL across `SigninLogs`, `AADServicePrincipalSignInLogs`, `AuditLogs`, `PowerPlatformAdminActivity`; reads CA Insights and Identity Protection workbooks | Standing read; contributor is JIT |
| AI Governance Lead | Owns the verification cycle; counter-signs the quarterly attestation in §13 | Standing with quarterly recertification (Control 2.8) |
| Compliance Officer | Counter-signs quarterly attestation; routes findings to Internal Audit | Standing |
| CISO (or CISO delegate) | Approves break-glass posture (TC-8) and the report-only-to-enforce change (TC-12) | Standing |

> **Least privilege.** No verifier holds **Entra Global Admin** persistently. Where Global Admin is required for a particular UI blade (rare in this control), activate through Entra PIM time-bound, never standing. Standing privileged-role overlap between Preparer / Validator / Compliance signatories on the §13 attestation is a cycle-stopping FAIL.

### 0.2 Module baseline (PowerShell 7.4)

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName='Microsoft.Graph.Authentication';                ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Identity.SignIns';              ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Identity.DirectoryManagement';  ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Identity.Governance';           ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Reports';                       ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Beta.Identity.SignIns';         ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.PowerApps.Administration.PowerShell'; ModuleVersion='2.0.200' }
#Requires -Modules @{ ModuleName='Az.SecurityInsights';                           ModuleVersion='3.1.0'  }

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'
```

Required Microsoft Graph delegated scopes for the verifier:

```text
Policy.Read.All
Policy.Read.ConditionalAccess
Directory.Read.All
User.Read.All
AuditLog.Read.All
Reports.Read.All
RoleManagement.Read.Directory
PrivilegedAccess.Read.AzureAD
UserAuthenticationMethod.Read.All
AgentGovernance.Read.All           # Entra Agent ID preview surface
```

### 0.3 Pre-flight gates

| Gate | ID | Purpose | Failure behavior |
|---|---|---|---|
| Tenant identity capture | PRE-01 | Captures `tenantId`, `displayName`, `verifiedDomains[0].name`, `cloud` for every evidence record | HALT |
| Cloud detection | PRE-02 | Resolves Commercial / GCC / GCCH / DoD; routes preview-only TCs (TC-4 WID, TC-6 Token Protection, Agent ID surfaces) to compensating-control branch where appropriate | Continue with route |
| License posture | PRE-03 | Confirms Entra ID P2 covers in-scope users; **Workload Identities Premium** covers every service principal and Agent ID in a workload-identity CA policy; Microsoft Authenticator FedRAMP authorization is current in sovereign clouds | HALT |
| Evidence root writeable | PRE-04 | Confirms `$env:CA111_EVIDENCE_ROOT` exists, is writeable, and resolves to WORM-eligible storage with a Purview retention label of ≥7 years and deletion lock | HALT |
| Clock skew gate | PRE-05 | Compares local UTC to Graph `Date` header; aborts on > 60 s drift (timestamp evidence under FINRA 4511 and SEC 17a-4 must be authoritative) | HALT |
| Sentinel reachability | PRE-06 | Confirms Log Analytics workspace is reachable, the `AzureActiveDirectory` connector is enabled, and the four required tables have entries in the last 24 hours | HALT |
| CAE baseline | PRE-07 | Records the per-tenant baseline CAE revocation latency for cycle-over-cycle comparison (no invented Microsoft SLA — see TC-5) | Continue |

### 0.4 Run identifier

```powershell
function New-Ca111RunId {
    $ts   = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
    $guid = ([guid]::NewGuid().ToString('N')).Substring(0,8)
    "CA111-$ts-$guid"
}

$script:RunId        = New-Ca111RunId
$script:RunTimestamp = (Get-Date).ToUniversalTime().ToString('o')
$script:EvidenceRoot = Join-Path $env:CA111_EVIDENCE_ROOT $script:RunId
New-Item -Path $script:EvidenceRoot -ItemType Directory -Force | Out-Null
```

Every artifact emitted by TC-1 through TC-12 is stored under `$script:EvidenceRoot` and the `runId` is embedded in each filename assembled into the §13 quarterly attestation pack.

---
## §1 Test Cases

The 12 test cases below evidence the control's verification criteria. Each procedure follows a fixed structure: **Setup → Steps → Expected Result → Evidence Capture → Failure Remediation**. Test cases are independent — a FAIL in one does not preclude execution of the others — but the §13 quarterly attestation requires either a PASS or a signed compensating-control record for **every** test case before sign-off.

---

### TC-1 — Phishing-Resistant MFA Coverage for Privileged Roles

**Verifies:** Every member of the privileged roles enumerated below holds at least one phishing-resistant authentication method registered (FIDO2 security key, Windows Hello for Business, **device-bound** passkey in Microsoft Authenticator, or X.509 certificate-based authentication via PIV / CAC). Synced (cross-device) passkeys do **not** satisfy AAL3 and do **not** count toward this test.

**Privileged roles in scope:**

- Entra Global Admin
- Power Platform Admin
- Authentication Policy Admin
- Authentication Administrator
- Purview Compliance Admin
- AI Administrator
- Entra Agent ID Admin
- Entra Security Admin
- Entra Identity Governance Admin

**Regulatory tie:** NYDFS 23 NYCRR 500.12 (universal MFA, fully effective Nov 1, 2025); FFIEC Authentication and Access booklet (risk-based MFA for privileged users); GLBA / FTC Safeguards Rule 16 CFR §314.4(c)(5); NIST SP 800-63B AAL3 (phishing-resistant authenticators).

#### Setup

1. Verifier activates **Entra Identity Governance Admin** + **Authentication Administrator** through PIM for a 4-hour window with a written justification referencing the verification cycle's run-id.
2. Confirm Microsoft Graph PowerShell SDK is at the pinned version baseline (§0.2) and `Connect-MgGraph -Scopes "RoleManagement.Read.Directory","UserAuthenticationMethod.Read.All","User.Read.All","Reports.Read.All"` succeeds.
3. Confirm PRE-01 through PRE-04 PASSED for the run.

#### Steps

1. Enumerate the eligible-and-active membership of each in-scope role via `Get-MgRoleManagementDirectoryRoleAssignmentSchedule` and `Get-MgRoleManagementDirectoryRoleEligibilitySchedule`. Resolve to a deduplicated set of `userPrincipalName` values keyed by `userId`.
2. For each user, pull the registration detail report:

    ```powershell
    $roleNames = @(
        'Global Administrator','Power Platform Administrator','Authentication Policy Administrator',
        'Authentication Administrator','Compliance Administrator','AI Administrator',
        'Agent ID Administrator','Security Administrator','Identity Governance Administrator'
    )

    $privilegedUsers = foreach ($roleName in $roleNames) {
        $role = Get-MgDirectoryRole -Filter "displayName eq '$roleName'" -ErrorAction SilentlyContinue
        if (-not $role) { continue }
        $eligible = Get-MgRoleManagementDirectoryRoleEligibilitySchedule -Filter "roleDefinitionId eq '$($role.RoleTemplateId)'"
        $active   = Get-MgRoleManagementDirectoryRoleAssignmentSchedule  -Filter "roleDefinitionId eq '$($role.RoleTemplateId)'"
        ($eligible + $active) | Select-Object @{n='RoleName';e={$roleName}}, PrincipalId
    } | Sort-Object PrincipalId -Unique

    $registration = Get-MgReportAuthenticationMethodUserRegistrationDetail -All

    $report = foreach ($u in $privilegedUsers) {
        $reg = $registration | Where-Object { $_.Id -eq $u.PrincipalId }
        [pscustomobject]@{
            roleName                 = $u.RoleName
            userId                   = $u.PrincipalId
            userPrincipalName        = $reg.UserPrincipalName
            isMfaCapable             = $reg.IsMfaCapable
            isPasswordlessCapable    = $reg.IsPasswordlessCapable
            isSystemPreferredAuth    = $reg.IsSystemPreferredAuthenticationMethodEnabled
            phishResistantRegistered = ($reg.MethodsRegistered -match 'fido2|windowsHelloForBusiness|x509Certificate|passKeyDeviceBound').Count -gt 0
            methodsRegistered        = ($reg.MethodsRegistered -join ';')
        }
    }

    $report | Export-Csv -Path (Join-Path $script:EvidenceRoot 'TC-1-userRegistrationDetails.csv') -NoTypeInformation
    ```

3. Cross-validate against the Entra portal: **Microsoft Entra admin center → Protection → Authentication methods → User registration details**. Filter the blade by each privileged role and visually confirm the `phishResistantRegistered` count matches the CSV.
4. For any user whose `phishResistantRegistered` is `False`, capture the user's UPN, the role(s) they hold, and the registration detail row.

#### Expected Result

- For **every** user in **every** in-scope role, `phishResistantRegistered = True`.
- The CSV row count equals the deduplicated count from Step 1.
- The portal blade and the CSV agree on the count of non-compliant users (zero).

#### Evidence Capture

- `TC-1-userRegistrationDetails.csv` — full report; **digitally signed** by the verifier (X.509 code-signing certificate or Microsoft Purview sensitivity label with content marking + encryption).
- `TC-1-portal-screenshot-userRegistrationDetails.png` — timestamp-watermarked screenshot of the Entra portal blade.
- `TC-1-evidence.json` — canonical evidence record (status, observed_value, expected_value, regulator_mappings, operator UPN, run-id).
- **Retention:** ≥ 7 years; records-scope under FINRA 4511 and SEC 17a-4 because the artifact evidences access controls on principals who have authority over books-and-records systems.

#### Failure Remediation

1. If a privileged user lacks a phishing-resistant method, **immediately** open a high-severity ticket assigned to the user, copying the user's manager and the Authentication Policy Admin.
2. Route the user to the [Portal Walkthrough](./portal-walkthrough.md) §4 (Authentication Methods enrollment) and the firm's hardware-key issuance procedure. NYDFS 500.12 carries no grace period as of Nov 1, 2025; a non-compliant privileged user is a **finding** at examination, not a deferrable item.
3. Document the gap in the §13 attestation as an exception with a remediation deadline; if the deadline slips, escalate to the CISO and reduce the user's privileged role assignment until phishing-resistant enrollment is confirmed.
4. Re-run TC-1 within 5 business days of remediation and re-issue the signed CSV.

---

### TC-2 — Authentication Strengths Enforcement (Privileged User, Weak Method)

**Verifies:** A Conditional Access policy bound to a phishing-resistant Authentication Strength **blocks** an interactive sign-in attempt by a privileged user when the only registered second factor is a weak method (SMS or voice OTP) and prompts for a stronger method (or fails closed).

**Regulatory tie:** NYDFS 500.12; SEC 17a-4(b)(4) (sign-in records as evidence of access-control enforcement); FINRA 4511 evidenced via Purview retention; FINRA Notice 21-18 (cybersecurity).

#### Setup

1. Provision a **canary** privileged-role test account `ca111-canary-tc2@<tenant>` assigned the **AI Administrator** role through PIM eligibility only. The canary holds **only** SMS as a second factor (no FIDO2, no WHfB, no device-bound passkey, no certificate). The canary is documented in the firm's test-account register and excluded from production access reviews.
2. Confirm a Conditional Access policy `CA-Z3-Privileged-Roles-PhishResistant` is **Enabled** (not Report-only) targeting the privileged role set from TC-1, with grant control = **Require authentication strength = Phishing-resistant MFA**.
3. Note the policy's `id`, `state`, `displayName`, and the bound Authentication Strength `id` for evidence cross-reference.

#### Steps

1. From a clean browser session (incognito, no SSO state), navigate to the Agent 365 Admin Center sign-in URL and the Copilot Studio maker portal.
2. Sign in as the canary. Provide username + password.
3. Observe the second-factor challenge.
4. Attempt to complete the SMS challenge.
5. Capture the resulting screen text and the user-visible error code (e.g., `AADSTS500011` family or the "Your sign-in was successful but doesn't meet the criteria to access this resource" interrupt).
6. Within 10 minutes of the attempt, query Sentinel:

    ```kql
    SigninLogs
    | where TimeGenerated > ago(30m)
    | where UserPrincipalName == "ca111-canary-tc2@<tenant>"
    | where AppDisplayName in~ ("Microsoft 365 Agents Toolkit","Power Virtual Agents","Microsoft Copilot Studio")
    | extend caResult = tostring(ConditionalAccessPolicies)
    | project TimeGenerated, AppDisplayName, ResultType, ResultDescription, AuthenticationDetails, AuthenticationRequirement,
              AuthenticationStrengthDetails = tostring(AuthenticationContextClassReferences),
              CA = caResult, Status, ClientAppUsed, IPAddress
    | order by TimeGenerated desc
    ```

7. Confirm the row shows `ResultType != 0` (failure) **and** the matching CA policy entry with `result = "failure"` or `result = "notApplied"` with the reason indicating the Authentication Strength was not satisfied.

#### Expected Result

- The sign-in completes the password step, the MFA interrupt is presented, the SMS option is **not offered** (or, if offered, is rejected) because it does not satisfy the bound Authentication Strength.
- The user is presented with the standard Microsoft "stronger authentication required" interrupt and a list of qualifying methods.
- The Sentinel KQL returns at least one row for the attempt; the row's CA evaluation includes the `CA-Z3-Privileged-Roles-PhishResistant` policy with a non-success outcome and a reason that ties to Authentication Strength.

#### Evidence Capture

- `TC-2-signin-interrupt.png` — screenshot of the user-visible interrupt with timestamp watermark.
- `TC-2-signinLogs.csv` — KQL export of the matched sign-in row(s).
- `TC-2-ca-policy-snapshot.json` — `Get-MgIdentityConditionalAccessPolicy -ConditionalAccessPolicyId <id>` JSON snapshot of `CA-Z3-Privileged-Roles-PhishResistant` and the bound Authentication Strength definition.
- `TC-2-evidence.json` — canonical evidence record.
- **Retention:** ≥ 7 years (records-scope: the interrupt is the access-control evidence FINRA 4511 / SEC 17a-4 will examine).

#### Failure Remediation

1. **If the sign-in succeeded with SMS:** the policy is mis-bound or in Report-only. Pause Z3 maker enrollment for the affected role(s). Open a Sev-1 change ticket. Route to [Portal Walkthrough](./portal-walkthrough.md) §6 to re-bind the Authentication Strength and confirm `state = enabled`.
2. **If no Sentinel row appeared:** the sign-in did not reach the CA evaluator (federation issue, alternate IdP, or ingestion lag). Confirm with PRE-06 that the connector is healthy; if healthy, escalate to the federation owner.
3. **If the canary itself was already evicted by a separate baseline policy** (e.g., Microsoft-managed `Block legacy authentication` returned a misleading `notApplied`): re-run with a freshly provisioned canary and adjust the test scope to disambiguate which policy fired.
4. Re-run TC-2 within 2 business days of remediation. Append the failed and remediated runs to the §13 attestation as a paired record (both are evidence — the FAIL evidences detection, the PASS evidences correction).

---

### TC-3 — Conditional Access Policy for Agent Makers (Non-Compliant Device Block)

**Verifies:** A Conditional Access policy targeting Power Platform / Copilot Studio maker portals **blocks** access from a device that is not Intune-compliant, and presents the user with the Intune-compliance-required guidance message rather than failing silently or returning a generic error.

**Regulatory tie:** FFIEC Authentication and Access (device posture as a layered control); SEC 17a-3/17a-4 (records evidencing access-control enforcement on the maker plane); NYDFS 500.12; CISA Zero Trust Maturity Model v2.0 (Identity + Device pillars).

#### Setup

1. Identify a Windows endpoint that is **enrolled in Microsoft Intune but flagged non-compliant** (for example, a known canary device with an intentionally failing compliance policy such as expired BitLocker recovery escrow, missing required app, or stale OS patch level). The non-compliance state must be visible in the Intune blade **before** the test begins.
2. Provision a canary maker account `ca111-canary-tc3@<tenant>` assigned the Power Platform Maker role and licensed for Copilot Studio.
3. Confirm a CA policy `CA-Z2-Z3-Makers-RequireCompliantDevice` is **Enabled**, targeting the `Microsoft Copilot Studio` and `Power Apps` cloud apps (or the `Office 365` super-app where applicable), with grant control = **Require device to be marked as compliant**.

#### Steps

1. From the non-compliant device, in a clean browser session, navigate to `https://copilotstudio.microsoft.com`.
2. Sign in as the canary maker.
3. Observe the post-sign-in interrupt.
4. Capture the screen text, the user-visible reference code, and the Microsoft "You can't get there from here" / device-compliance interrupt.
5. Within 10 minutes, run the Sentinel KQL:

    ```kql
    SigninLogs
    | where TimeGenerated > ago(30m)
    | where UserPrincipalName == "ca111-canary-tc3@<tenant>"
    | where AppDisplayName in~ ("Microsoft Copilot Studio","Power Apps","Power Automate")
    | mv-expand CA = todynamic(ConditionalAccessPolicies)
    | where tostring(CA.displayName) == "CA-Z2-Z3-Makers-RequireCompliantDevice"
    | project TimeGenerated, UserPrincipalName, AppDisplayName, ResultType, ResultDescription,
              DeviceDetail, IsCompliant = tostring(DeviceDetail.isCompliant),
              CAResult = tostring(CA.result), CAReason = tostring(CA.conditionsNotSatisfied)
    | order by TimeGenerated desc
    ```

6. Confirm `IsCompliant == "false"`, `CAResult == "failure"`, and a non-empty `CAReason` referencing device compliance.

#### Expected Result

- The sign-in is blocked with the Intune-compliance-required interrupt; the user is directed to enroll or remediate via the Company Portal.
- The Sentinel row records the CA policy evaluation with a failure outcome and a device-compliance reason.
- No row evidences a `success` or `interrupted` outcome that would indicate the maker portal session was established.

#### Evidence Capture

- `TC-3-block-interrupt.png` — screenshot of the device-compliance interrupt.
- `TC-3-intune-device-status.png` — Intune device blade showing the non-compliant state at the time of the test.
- `TC-3-signinLogs.csv` — KQL export.
- `TC-3-ca-policy-snapshot.json` — `CA-Z2-Z3-Makers-RequireCompliantDevice` policy JSON.
- `TC-3-evidence.json` — canonical evidence record.
- **Retention:** ≥ 7 years (records-scope under FINRA 4511 and SEC 17a-4).

#### Failure Remediation

1. **If access was granted from the non-compliant device:** the policy is mis-targeted (wrong cloud app), in Report-only, or excludes the device's group. Pause Z2/Z3 maker enrollment for affected populations and open a Sev-1 change ticket.
2. **If the Sentinel row showed `notApplied` rather than `failure`:** confirm the canary user is in scope for the policy assignment and is not in any exclusion group. The exclusion register (Control 1.11 portal walkthrough §7) is the authoritative source — reconcile drift.
3. **If the Intune compliance signal did not propagate** (compliance evaluation lag): record the lag duration and compare to the per-tenant baseline; if lag exceeds the baseline +2σ, open a separate ticket against the Endpoint Admin to investigate compliance evaluation health (this is a Control 1.11 dependency, not a Control 1.11 failure per se, but must be tracked).
4. Re-run TC-3 within 5 business days of remediation.

---

### TC-4 — Conditional Access for Workload Identities (Agent / Service Principal)

**Verifies:** A Conditional Access for Workload Identities (CA WID) policy targeting AI agent backing identities (service principals, managed identities, or Entra Agent ID principals) **enforces the configured restriction** when an agent attempts a Microsoft Graph call from outside the named-location set, either by blocking the call (if the policy intent is "block from untrusted") or by requiring certificate-based authentication (if the policy intent is "require strong workload-identity auth"). The matching evidence row appears in `AADServicePrincipalSignInLogs` — **not** in `SigninLogs`.

> **Critical surface note.** Agent and service-principal sign-ins **do not appear in `SigninLogs`**. Verifiers and auditors who query `SigninLogs` for an agent UPN will find nothing and will incorrectly conclude there was no sign-in. The correct table is `AADServicePrincipalSignInLogs`. This is the most common examiner-finding pattern in early FSI agent-governance reviews.

**Regulatory tie:** OCC Bulletin 2011-12 / Federal Reserve SR 11-7 (model-serving endpoint authentication as an MRM control); FINRA Regulatory Notice 21-18; FINRA Notice 25-07 (AI-specific supervision); NYDFS 500.12 applied to non-human identities where the firm's risk assessment determines applicability.

> **Sovereign-cloud note.** Conditional Access for Workload Identities is GA in Commercial; sovereign-cloud parity (GCC, GCC High, DoD) tracked per release wave. Where unavailable, the compensating control is a quarterly manual reconciliation worksheet that proves equivalent restriction via tenant network egress controls + service-principal credential rotation evidence (see SOV namespace pattern in [Control 3.6 §10](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)).

#### Setup

1. Provision (or identify) a **canary agent** backing identity — a service principal `sp-ca111-canary-tc4` enrolled in the Workload Identities Premium SKU and bound to a CA WID policy `CA-WID-Agents-RestrictFromUntrustedLocations` whose intent is documented in the policy description (block, or require strong auth).
2. Provision a test execution environment **outside** every named location in the policy's "Trusted locations" set (for example, an Azure Cloud Shell session in a region intentionally excluded from the corporate egress range, or a developer workstation on a dedicated test ISP segment).
3. Ensure the canary SP holds the minimum Graph application permissions required for the test call (`User.Read.All`) and that the permission has admin consent.
4. Confirm `CA-WID-Agents-RestrictFromUntrustedLocations` is `state = enabled` (not Report-only).

#### Steps

1. From the out-of-location environment, acquire a token for the canary SP via the client credentials flow (certificate or secret as configured) and call `https://graph.microsoft.com/v1.0/users?$top=1`.
2. Capture the HTTP response — expected outcomes per policy intent:
    - **Block intent:** HTTP 403 with `AADSTS53003` (blocked by Conditional Access) or equivalent.
    - **Require certificate intent:** HTTP 401 with a challenge requiring certificate-based client credential, or HTTP 403 if the SP authenticated with a secret rather than the required certificate.
3. Within 10 minutes, query Sentinel against the **service principal** sign-in table:

    ```kql
    AADServicePrincipalSignInLogs
    | where TimeGenerated > ago(30m)
    | where ServicePrincipalName == "sp-ca111-canary-tc4"
    | mv-expand CA = todynamic(ConditionalAccessPolicies)
    | where tostring(CA.displayName) == "CA-WID-Agents-RestrictFromUntrustedLocations"
    | project TimeGenerated, ServicePrincipalId, ServicePrincipalName, AppId, ResourceDisplayName,
              IPAddress, Location = tostring(LocationDetails),
              ResultType, ResultDescription,
              CAResult = tostring(CA.result), CAReason = tostring(CA.conditionsNotSatisfied),
              CAPolicyId = tostring(CA.id)
    | order by TimeGenerated desc
    ```

4. Confirm the matched row and capture the `CAPolicyId`.
5. Cross-check that the **same** call from inside a trusted location succeeds (positive control, executed from the corporate network or Cloud Shell in an in-location region).

#### Expected Result

- The out-of-location call fails with the policy-intent-appropriate HTTP code.
- `AADServicePrincipalSignInLogs` records the failed sign-in with the bound CA policy's `result = failure` (or `notApplied` only with a documented reason that does not indicate a silent bypass).
- The same call from a trusted location succeeds, confirming the restriction is geographically scoped and not a credential failure.
- A `SigninLogs` query for the same SP UPN returns **zero rows** — this is the expected behavior and must be documented in the evidence record so future verifiers do not mis-interpret the empty result.

#### Evidence Capture

- `TC-4-graph-call-out-of-location.json` — raw HTTP request/response (with secrets redacted) of the failed call.
- `TC-4-graph-call-in-location.json` — raw HTTP request/response of the positive control success.
- `TC-4-aadServicePrincipalSignInLogs.csv` — KQL export from `AADServicePrincipalSignInLogs`.
- `TC-4-signinLogs-empty-confirmation.csv` — `SigninLogs` query for the SP returning zero rows, captured as the explicit "agent sign-ins do not appear here" evidence.
- `TC-4-ca-wid-policy-snapshot.json` — full policy JSON including `clientApplications`, `locations`, and `grantControls`.
- `TC-4-evidence.json` — canonical evidence record with `CAPolicyId` and the policy intent classification.
- **Retention:** ≥ 7 years (records-scope: agent identity is the model-serving principal under SR 11-7).

#### Failure Remediation

1. **If the call succeeded from out-of-location:** the WID policy is mis-bound, in Report-only, or the SP is excluded. Pause new agent publishing under [Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) and open a Sev-1 change ticket. Re-target the policy and confirm `state = enabled`.
2. **If `AADServicePrincipalSignInLogs` returned no row:** confirm Workload Identities Premium SKU is **consumed** by the SP (entitlement without consumption is a silent fail-open — see Control 1.11 anti-pattern register). Confirm the connector for SP sign-ins is selected on the Sentinel `AzureActiveDirectory` connector blade.
3. **If the in-location positive control failed:** the test is invalid; the failure may be a credential or permission issue rather than a CA enforcement issue. Re-establish positive control before re-running.
4. **Sovereign-cloud unavailability:** if CA WID is not available in the operating cloud, mark the test `SKIPPED` with a pointer to the quarterly manual reconciliation worksheet. The skipped evidence record itself must be signed; a silent omission is examiner-non-defensible.

---

### TC-5 — Continuous Access Evaluation (CAE) Revocation Latency

**Verifies:** Continuous Access Evaluation propagates a session-revocation event (user disable) to a subsequent Microsoft Graph call within the per-tenant baseline established in PRE-07 (typically ~minutes, not hours), forcing a re-authentication on the next call rather than allowing the cached token to remain valid for its full lifetime.

**Regulatory tie:** FFIEC Authentication and Access booklet (continuous validation expectation); CISA Zero Trust Maturity Model v2.0 (continuous validation as Advanced/Optimal target); NYDFS 500.04 (CISO oversight of access-control effectiveness); FINRA Notice 21-18.

> **Hedging note.** Microsoft Learn explicitly states that CAE propagation is eventually consistent and that latency varies by client, app, signal type, and cloud. This test does **not** assert any single Microsoft SLA. The operative threshold is the per-tenant baseline measured in PRE-07 and compared cycle over cycle.

#### Setup

1. Provision a canary user `ca111-canary-tc5@<tenant>` with a CAE-supported client (Microsoft Graph PowerShell, Outlook desktop, or a Microsoft Graph SDK call from a long-lived session).
2. Confirm CAE is enabled at the tenant: `Get-MgIdentityConditionalAccessPolicy` and the tenant's CAE setting (continuous-access-evaluation in the CA blade) shows `Enabled` for the in-scope users.
3. Confirm PRE-07 captured a current baseline (e.g., previous quarter median + p95 revocation latency).

#### Steps

1. As the canary, sign in to a CAE-supported client and establish a long-lived session (e.g., `Connect-MgGraph` and run a `Get-MgUser -Top 1` to confirm the session works).
2. Record `T0` (UTC) — the moment of the disable action.
3. As Authentication Administrator, disable the canary account: `Update-MgUser -UserId <id> -AccountEnabled:$false`.
4. From the canary's still-running session, issue a Graph call every 30 seconds: `Get-MgUser -Top 1`.
5. Record `T1` (UTC) — the moment the call first fails with a CAE-driven re-authentication challenge (`AADSTS50173` family or equivalent claim-challenge response).
6. Compute `latency = T1 - T0`.
7. Pull the audit row:

    ```kql
    AuditLogs
    | where TimeGenerated > ago(1h)
    | where OperationName == "Update user"
    | where TargetResources has "ca111-canary-tc5"
    | project TimeGenerated, InitiatedBy, TargetResources, AdditionalDetails

    SigninLogs
    | where TimeGenerated > ago(1h)
    | where UserPrincipalName == "ca111-canary-tc5@<tenant>"
    | project TimeGenerated, ResultType, ResultDescription, IsContinuousAccessEvaluation,
              ConditionalAccessStatus, AuthenticationDetails
    | order by TimeGenerated desc
    ```

8. Confirm `IsContinuousAccessEvaluation == true` on the failing row.

#### Expected Result

- The disabled canary's next Graph call after `T0` fails within the per-tenant baseline window (recorded in PRE-07) with a CAE-driven re-authentication challenge.
- `latency` is recorded; a value within `baseline_median ± 2σ` is a PASS. A value beyond `baseline_p95 × 1.5` is a WARN that requires a documented investigation note in the §13 attestation. A value greater than 1 hour is a FAIL.
- The audit row evidences the disable; the sign-in row evidences the CAE-driven challenge.

#### Evidence Capture

- `TC-5-disable-action.json` — the audit-log row for the user disable, with `T0` highlighted.
- `TC-5-failed-graph-call.txt` — the Graph PowerShell error output with timestamp, evidencing the re-auth challenge at `T1`.
- `TC-5-signinLogs-cae.csv` — KQL export including `IsContinuousAccessEvaluation == true`.
- `TC-5-latency.json` — `{T0, T1, latency_seconds, baseline_median, baseline_p95, classification}`.
- `TC-5-evidence.json` — canonical evidence record.
- **Retention:** ≥ 7 years for the audit and sign-in evidence (records-scope); the latency JSON is operational evidence retained per the firm's operational retention policy (typically 2 years).

#### Failure Remediation

1. **If `IsContinuousAccessEvaluation` was false:** the session was not CAE-bound (the client may not be CAE-aware, or the resource may not be in the CAE-supported-apps matrix as of the verification date). Re-run with a confirmed CAE-supported client and resource pair.
2. **If `latency` exceeded 1 hour:** the disable propagated through standard token expiry rather than CAE. Open a ticket against the Entra Security Admin to validate CAE configuration; confirm the user was not in a CAE-excluded group; verify Microsoft Learn for any current advisories on CAE health in the operating cloud.
3. **If the canary's session never failed:** the test is invalid (likely a session-binding issue or the disable did not persist). Re-run after confirming the disable in the directory.
4. Cycle-over-cycle, if median latency drifts upward materially, raise a SOV concern (sovereign clouds historically have lagged Commercial on CAE evolution) and surface to the AI Governance Lead for trend tracking.

---

### TC-6 — Token Protection (Preview) Pilot Behavior

**Verifies:** Token Protection (also called token binding for sign-in sessions) is rolled out via Microsoft's recommended report-only / pilot / enforce ladder. On a supported pilot Windows endpoint with a supported browser, the access token is **bound to the device** and a stolen-token replay from another device fails. On a non-supported browser or non-Windows endpoint, the **documented fallback behavior** (typically a downgrade to standard MFA + sign-in frequency, or block, per policy intent) is observed and recorded — **not** a silent bypass.

**Regulatory tie:** FFIEC Authentication and Access (token theft and replay as a layered-control concern); CISA Zero Trust Maturity Model v2.0; FINRA Notice 21-18; NYDFS 500.12.

> **Preview-state hedge.** Token Protection is in Preview. Surface naming, supported app list, and supported browser list change between Microsoft release waves. Re-confirm the supported matrix on Microsoft Learn at the start of every cycle. The fallback behavior must be **explicitly documented in the policy description** so an examiner can distinguish "intended fallback" from "silent bypass".

#### Setup

1. Identify a pilot Windows 11 endpoint that meets the current Token Protection requirements (Hybrid Azure AD joined or Azure AD joined; supported OS build; supported browser as of the verification date).
2. Identify a non-supported endpoint (macOS, Linux, or Windows with an unsupported browser).
3. Confirm a CA policy `CA-Z3-TokenProtection-Pilot` is **Enabled** with **Session control = Require token protection for sign-in sessions** (preview), targeting the Z3 maker pilot population.
4. Confirm the policy description documents the **intended fallback** for non-supported clients (e.g., "On unsupported clients, the policy does not apply; access is governed by `CA-Z3-Makers-RequireCompliantDevice` and `CA-Z3-Makers-SignInFrequency-4h` as the residual baseline").

#### Steps

1. **Supported path:** From the pilot Windows 11 endpoint with the supported browser, sign in as a Z3 pilot maker. Confirm the session establishes.
2. Capture the bound-token claim by inspecting the token's `xms_cc` (client capabilities) or token-protection claim per the current Microsoft Learn schema (claim names should be re-verified each cycle).
3. **Replay test:** Export the cookie / token to an instrumented test harness running on a different device. Attempt to use the token from the second device.
4. Confirm the second device's request fails with a token-binding rejection (e.g., the resource server returns 401 with a claim challenge requiring re-auth on the original device).
5. **Non-supported path:** From the non-supported endpoint, sign in as the same pilot maker.
6. Confirm the documented fallback behavior is observed exactly: either (a) the policy is `notApplied` and access is gated by the residual policies named in the policy description, or (b) access is blocked with an explicit unsupported-client message — whichever the policy intent declares.
7. Pull both sign-in rows:

    ```kql
    SigninLogs
    | where TimeGenerated > ago(1h)
    | where UserPrincipalName == "<pilot-maker-upn>"
    | mv-expand CA = todynamic(ConditionalAccessPolicies)
    | where tostring(CA.displayName) == "CA-Z3-TokenProtection-Pilot"
    | project TimeGenerated, ClientAppUsed, DeviceDetail, UserAgent,
              CAResult = tostring(CA.result),
              SessionControls = tostring(CA.sessionControlsNotSatisfied),
              TokenProtectionStatus = tostring(TokenProtectionStatusDetails)
    | order by TimeGenerated desc
    ```

#### Expected Result

- Supported path: token-bound session establishes; replay from a second device fails with a token-binding rejection.
- Non-supported path: behavior matches the policy's documented fallback exactly.
- Sentinel rows distinguish the two paths via `DeviceDetail`, `UserAgent`, and `CAResult` / `SessionControls`.

#### Evidence Capture

- `TC-6-supported-session-token-claim.json` — redacted token-claim view confirming the binding claim is present.
- `TC-6-replay-rejection.txt` — the second device's failed-request output with timestamp.
- `TC-6-unsupported-fallback.png` — screenshot of the unsupported-client behavior matching the documented fallback.
- `TC-6-policy-description.md` — extract of the CA policy description documenting the intended fallback (this artifact is itself examiner-relevant: it proves the fallback was intentional, not silent).
- `TC-6-signinLogs.csv` — both sign-in rows with full CA evaluation details.
- `TC-6-evidence.json` — canonical evidence record.
- **Retention:** ≥ 7 years for sign-in rows and policy description (records-scope evidence of access-control policy intent and operation).

#### Failure Remediation

1. **If the replay succeeded:** Token Protection is not actually binding the token, or the policy is in Report-only. Pause the pilot, open a Sev-1 ticket, and re-confirm preview-availability against current Microsoft Learn. Do **not** broaden the pilot until a successful re-test.
2. **If the unsupported endpoint silently succeeded with no fallback evidence:** the policy description does not match enforced reality, or there is no residual baseline. Update the policy description and add the residual baseline policies; re-test.
3. **If the supported endpoint also failed (no session established):** the pilot is too aggressive for the current Microsoft Learn supported-matrix. Roll back to Report-only, re-verify the matrix, and re-pilot.
4. Track preview-state churn in the §13 attestation as a recurring SOV-class risk; quarterly re-verification is mandatory while the feature remains in Preview.

---

### TC-7 — Sign-in Frequency Enforcement (Zone 3)

**Verifies:** A 4-hour Sign-in Frequency (SIF) Conditional Access session control is **active** for Zone 3 environment access (Copilot Studio Z3 environments, Power Platform Z3 environments, the Agent 365 Admin Center). A user who has been signed in for more than 4 hours is forced to re-authenticate on the next access attempt; the sign-in log records the re-auth.

**Regulatory tie:** FFIEC Authentication and Access (session lifetime as a layered control on high-risk surfaces); SEC 17a-4 (session-boundary records as access-control evidence); NYDFS 500.12; FINRA Notice 21-18.

#### Setup

1. Identify a Z3 maker account `ca111-canary-tc7@<tenant>` permitted to access a Z3 Copilot Studio environment.
2. Confirm a CA policy `CA-Z3-Makers-SignInFrequency-4h` is **Enabled** with **Session control = Sign-in frequency = 4 hours** targeting Z3 makers and the in-scope cloud apps.
3. Establish a long-lived session: sign in at `T0` and confirm Z3 access is established.

#### Steps

1. Wait at least 4 hours and 5 minutes after `T0` (allow for clock skew and propagation). For acceleration in a test cycle, set SIF to a short value in a **non-production test policy** scoped to the canary only, and document the acceleration in the test record.
2. From the same browser session, attempt to access the Z3 Copilot Studio environment.
3. Confirm the user is interrupted with a re-authentication prompt.
4. Complete the re-authentication.
5. Pull the sign-in row:

    ```kql
    SigninLogs
    | where TimeGenerated > ago(1h)
    | where UserPrincipalName == "ca111-canary-tc7@<tenant>"
    | mv-expand CA = todynamic(ConditionalAccessPolicies)
    | where tostring(CA.displayName) == "CA-Z3-Makers-SignInFrequency-4h"
    | project TimeGenerated, AppDisplayName, ResultType, ResultDescription,
              CAResult = tostring(CA.result),
              SessionControls = tostring(CA.enforcedSessionControls),
              AuthenticationRequirement, AuthenticationDetails
    | order by TimeGenerated desc
    ```

6. Confirm the row records the re-auth event and the SIF session control as enforced.

#### Expected Result

- The session is interrupted with a re-auth prompt at or shortly after the 4-hour boundary.
- The sign-in row records `enforcedSessionControls` containing the SIF control.
- The `AuthenticationRequirement` reflects the re-auth.

#### Evidence Capture

- `TC-7-reauth-interrupt.png` — screenshot of the re-auth prompt at the 4-hour boundary.
- `TC-7-signinLogs.csv` — KQL export of the re-auth row.
- `TC-7-ca-policy-snapshot.json` — `CA-Z3-Makers-SignInFrequency-4h` JSON.
- `TC-7-evidence.json` — canonical evidence record with `T0`, `T_reauth`, and the elapsed interval.
- **Retention:** ≥ 7 years (records-scope).

#### Failure Remediation

1. **If no re-auth was prompted:** SIF is not enforced; the policy may be in Report-only or excluded for the canary. Open a Sev-2 change ticket; re-target.
2. **If re-auth was prompted but the sign-in row is missing:** ingestion lag — re-query after 30 minutes; if still missing, escalate to PRE-06 connector health.
3. **If SIF is enforced at a different value than 4 hours:** policy drift; reconcile against the CA-as-code source of truth and remediate via [Portal Walkthrough](./portal-walkthrough.md) §8.

---

### TC-8 — Break-Glass Account Integrity

**Verifies:** Exactly **two** break-glass (emergency access) accounts exist; both are excluded from **every** Conditional Access policy; both are bound to hardware FIDO2 keys held in physical storage with no SMS / voice / OTP / Authenticator factors; credential custody is dual-controlled; and a Microsoft Sentinel analytics rule alerts on any sign-in by either account, integrated with the [Control 3.9 Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) incident workflow.

**Regulatory tie:** SOX 302/404 (break-glass test records are common SOX evidence); FFIEC Authentication and Access; NYDFS 500.04 (CISO oversight) and 500.12; FINRA 4511; OCC 2011-12 / SR 11-7 (controls around model-serving administrative access).

#### Setup

1. Confirm the firm's break-glass register lists exactly two accounts (e.g., `bg-01@<tenant>.onmicrosoft.com` and `bg-02@<tenant>.onmicrosoft.com`), both cloud-only (non-federated), neither dependent on on-premises identity infrastructure, neither dependent on the same hardware-key vendor (vendor diversity is recommended where feasible).
2. Confirm physical custody: each account's hardware FIDO2 key is in a tamper-evident envelope in a physical safe; safe access is dual-controlled (two custodians, separate combinations or keys).
3. Confirm a Sentinel analytics rule `BG-SignIn-Alert` is `Enabled` with severity High and an automated playbook routing to the on-call CISO delegate and the Compliance Officer.

#### Steps

1. **Exclusion enumeration.** Query every enabled CA policy and confirm both break-glass principal IDs appear in the exclusion list:

    ```powershell
    $bg = @('<bg-01-objectid>','<bg-02-objectid>')
    $policies = Get-MgIdentityConditionalAccessPolicy -All | Where-Object { $_.State -eq 'enabled' }
    $coverage = foreach ($p in $policies) {
        $excludedUsers  = @($p.Conditions.Users.ExcludeUsers)
        $excludedGroups = @($p.Conditions.Users.ExcludeGroups)
        # Resolve excluded groups to membership for transitive coverage
        $groupMembers = foreach ($g in $excludedGroups) {
            Get-MgGroupMemberAsUser -GroupId $g -All | Select-Object -ExpandProperty Id
        }
        $excludedSet = @($excludedUsers + $groupMembers) | Sort-Object -Unique
        [pscustomobject]@{
            policyId       = $p.Id
            policyName     = $p.DisplayName
            bg01_excluded  = $bg[0] -in $excludedSet
            bg02_excluded  = $bg[1] -in $excludedSet
        }
    }
    $coverage | Export-Csv (Join-Path $script:EvidenceRoot 'TC-8-bg-exclusion-coverage.csv') -NoTypeInformation
    $gaps = $coverage | Where-Object { -not $_.bg01_excluded -or -not $_.bg02_excluded }
    if ($gaps) { throw "BREAK-GLASS EXCLUSION GAP: $($gaps | ConvertTo-Json -Depth 5)" }
    ```

2. **Method enumeration.** For each break-glass UPN, confirm registered methods are exclusively FIDO2:

    ```powershell
    foreach ($upn in @('bg-01@<tenant>.onmicrosoft.com','bg-02@<tenant>.onmicrosoft.com')) {
        Get-MgUserAuthenticationMethod -UserId $upn |
            Select-Object @{n='upn';e={$upn}}, AdditionalProperties
    }
    ```

    Confirm only `#microsoft.graph.fido2AuthenticationMethod` entries appear; flag any `phoneAuthenticationMethod`, `softwareOathAuthenticationMethod`, or `microsoftAuthenticatorAuthenticationMethod` entries as a FAIL.

3. **Physical custody attestation.** Two custodians physically witness the safe contents and sign a dated attestation (`TC-8-physical-custody-attestation.pdf`).

4. **Sentinel rule confirmation.** Confirm `BG-SignIn-Alert` is enabled, has fired in test (a planned, signed test sign-in within the last 90 days), and is integrated into the Control 3.9 incident workflow:

    ```kql
    SigninLogs
    | where TimeGenerated > ago(90d)
    | where UserPrincipalName in~ ("bg-01@<tenant>.onmicrosoft.com","bg-02@<tenant>.onmicrosoft.com")
    | project TimeGenerated, UserPrincipalName, AppDisplayName, ResultType, IPAddress, ClientAppUsed
    | order by TimeGenerated desc
    ```

#### Expected Result

- Exactly two break-glass accounts exist; both are excluded from **every** enabled CA policy (transitive group resolution included).
- Each account has only FIDO2 methods registered; no SMS, voice, OTP, or Authenticator.
- Physical custody is dual-controlled and attested in writing for the cycle.
- The Sentinel alert rule is enabled and has fired on the planned test sign-in within the last 90 days.

#### Evidence Capture

- `TC-8-bg-exclusion-coverage.csv` — full per-policy coverage matrix.
- `TC-8-bg-method-registration.csv` — method registration per break-glass UPN.
- `TC-8-physical-custody-attestation.pdf` — signed by two custodians.
- `TC-8-sentinel-rule-config.json` — `BG-SignIn-Alert` rule definition export.
- `TC-8-sentinel-test-fire.csv` — KQL export evidencing the test fire and the 3.9 incident reference.
- `TC-8-evidence.json` — canonical evidence record.
- **Retention:** ≥ 7 years (records-scope; SOX-relevant).

#### Failure Remediation

1. **Coverage gap (one or more policies do not exclude one or both break-glass accounts):** treat as Sev-1; remediate within 24 hours via [Portal Walkthrough](./portal-walkthrough.md) §11. Re-run TC-8 to confirm closure.
2. **Method drift (an SMS or Authenticator method appears on a break-glass account):** treat as Sev-1; immediately remove the offending method via Authentication Administrator and re-run.
3. **Physical custody discrepancy:** treat as a SOX significant deficiency; route to the CISO and to Internal Audit; rotate the affected hardware key and re-attest.
4. **Sentinel rule disabled or never fired:** route to [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) for restoration; planned test fire required before the cycle's §13 sign-off.

---

### TC-9 — Legacy Authentication Blocked

**Verifies:** A Conditional Access policy `CA-All-BlockLegacyAuth` is **Enabled**, targets all users (including, where applicable to the tenant's risk model, workload identities), and blocks legacy authentication protocols including ROPC (Resource Owner Password Credentials), basic auth, IMAP, POP, SMTP AUTH, and EWS basic.

**Regulatory tie:** FFIEC Authentication and Access; CISA Zero Trust Maturity Model v2.0; NYDFS 500.12; FINRA Notice 21-18; SEC Reg S-P (May 2024 amendments — incident response on auth-protocol weaknesses).

#### Setup

1. Confirm `CA-All-BlockLegacyAuth` exists and `state = enabled` (not Report-only). Conditions: `clientAppTypes = exchangeActiveSync, other` (the canonical legacy-auth selectors). Grant: `block`.
2. Confirm the exclusion register documents any per-app exclusions with named-business justifications, expiry dates, and compensating controls.
3. Provision (or reuse) a canary account `ca111-canary-tc9@<tenant>` and a test client capable of issuing a basic-auth IMAP / SMTP request, or a ROPC token request.

#### Steps

1. From a test workstation, attempt a basic-auth IMAP request against `outlook.office365.com:993` using the canary credentials.
2. Confirm the request fails with an authentication error.
3. Attempt a ROPC token request:

    ```text
    POST https://login.microsoftonline.com/<tenant>/oauth2/v2.0/token
    Content-Type: application/x-www-form-urlencoded

    client_id=<test-public-client-id>
    &grant_type=password
    &username=ca111-canary-tc9@<tenant>
    &password=<password>
    &scope=https://graph.microsoft.com/.default
    ```

4. Confirm the response includes a Conditional Access block (e.g., `AADSTS50158` for required additional auth, or `AADSTS53003` for the CA block — exact code depends on the resource and current Microsoft surface).
5. Pull the Sentinel rows:

    ```kql
    SigninLogs
    | where TimeGenerated > ago(1h)
    | where UserPrincipalName == "ca111-canary-tc9@<tenant>"
    | where ClientAppUsed in ("IMAP4","POP3","Authenticated SMTP","Other clients","Exchange ActiveSync","Exchange Web Services")
        or AuthenticationProtocol == "ropc"
    | mv-expand CA = todynamic(ConditionalAccessPolicies)
    | where tostring(CA.displayName) == "CA-All-BlockLegacyAuth"
    | project TimeGenerated, UserPrincipalName, ClientAppUsed, AuthenticationProtocol,
              ResultType, ResultDescription, CAResult = tostring(CA.result)
    | order by TimeGenerated desc
    ```

6. For workload-identity coverage (where the firm's risk model requires it), confirm an equivalent block via `AADServicePrincipalSignInLogs` against a test SP attempting an unsupported flow.

#### Expected Result

- Both the IMAP basic-auth attempt and the ROPC attempt fail with CA-driven block outcomes.
- `SigninLogs` shows the blocked rows with `CA-All-BlockLegacyAuth` in the evaluated policies and `result = failure`.
- Where workload-identity scope applies, `AADServicePrincipalSignInLogs` shows the equivalent block.

#### Evidence Capture

- `TC-9-imap-attempt.txt` — raw IMAP attempt and failure response.
- `TC-9-ropc-attempt.json` — raw HTTP request/response (secrets redacted).
- `TC-9-signinLogs.csv` — KQL export.
- `TC-9-aadServicePrincipalSignInLogs.csv` — workload-identity equivalent (where scoped).
- `TC-9-ca-policy-snapshot.json` — full `CA-All-BlockLegacyAuth` JSON.
- `TC-9-exclusion-register.csv` — current legacy-auth exclusions with justifications and expiries.
- `TC-9-evidence.json` — canonical evidence record.
- **Retention:** ≥ 7 years (records-scope).

#### Failure Remediation

1. **If legacy auth succeeded:** Sev-1; the policy is mis-configured or the canary is in an exclusion group. Pause any DLP / supervisory control that depends on modern-auth-only assumptions. Remediate and re-test.
2. **If exclusions exist without justifications or with expired justifications:** treat as a finding; require the exclusion owner to either close the exclusion (preferred) or refresh the justification with CISO approval (compensating-control path).
3. **If workload-identity legacy-auth coverage is unscoped despite a documented risk:** raise as a control-design gap to AI Governance Lead; coordinate with [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for full audit-trail coverage.

---

### TC-10 — PIM Activation-Time Phishing-Resistant MFA

**Verifies:** Activating a PIM-eligible privileged role (Entra Global Admin, AI Administrator, Authentication Policy Admin, Power Platform Admin, Purview Compliance Admin) requires **phishing-resistant MFA at the moment of activation**, satisfied by a CA Authentication Context bound to the PIM role activation flow — **not** session-token reuse from a prior weaker MFA event.

**Regulatory tie:** SOX 302/404 (PIM activation logs are common SOX evidence); FFIEC Authentication and Access; NYDFS 500.12 and 500.04; FINRA 4511; OCC 2011-12 / SR 11-7 (administrative access to model-serving environments).

#### Setup

1. Confirm a CA policy `CA-AuthContext-PIM-Activation-PhishResistant` is **Enabled** binding **Authentication Context = c1** (or the firm's chosen context value) to the **Phishing-resistant MFA** Authentication Strength.
2. Confirm each in-scope PIM-eligible role's activation settings reference the same Authentication Context value (Entra Identity Governance → PIM → Microsoft Entra roles → Settings → activation requires authentication context `c1`).
3. Provision a canary user `ca111-canary-tc10@<tenant>` PIM-eligible for AI Administrator. The canary holds **both** SMS and a hardware FIDO2 key registered (the test depends on the canary having a weaker option to attempt).

#### Steps

1. Sign the canary in to Microsoft Entra admin center using a **non-phishing-resistant** method (SMS) to establish a session; confirm the session tokens are not phishing-resistant-class.
2. Navigate to PIM and request activation of the AI Administrator role.
3. Observe whether the activation prompts for a step-up to phishing-resistant MFA at the moment of activation.
4. Complete the step-up using the FIDO2 key.
5. Pull the audit + sign-in evidence:

    ```kql
    AuditLogs
    | where TimeGenerated > ago(1h)
    | where Category == "RoleManagement"
    | where OperationName has "Add member to role" and TargetResources has "AI Administrator"
    | where InitiatedBy.user.userPrincipalName == "ca111-canary-tc10@<tenant>"
    | project TimeGenerated, OperationName, TargetResources, AdditionalDetails

    SigninLogs
    | where TimeGenerated > ago(1h)
    | where UserPrincipalName == "ca111-canary-tc10@<tenant>"
    | where AuthenticationContextClassReferences contains "c1"
    | project TimeGenerated, AppDisplayName, AuthenticationDetails,
              AuthenticationContextClassReferences,
              ConditionalAccessStatus, ResultType
    | order by TimeGenerated desc
    ```

6. Confirm the activation event is preceded by a sign-in row whose `AuthenticationDetails` shows a phishing-resistant method used in the immediate timeframe — not session-token reuse from the original SMS sign-in.

#### Expected Result

- The PIM activation triggers a step-up; the activation does **not** proceed on the SMS-only session.
- The audit row evidences the activation; the sign-in row evidences the phishing-resistant step-up at activation time.

#### Evidence Capture

- `TC-10-pim-stepup-prompt.png` — screenshot of the step-up prompt at activation.
- `TC-10-auditLogs.csv` — the role-activation audit row.
- `TC-10-signinLogs.csv` — the step-up sign-in row with `AuthenticationContextClassReferences` containing `c1`.
- `TC-10-ca-authcontext-policy.json` — `CA-AuthContext-PIM-Activation-PhishResistant` JSON.
- `TC-10-pim-role-settings.json` — the role's PIM settings export confirming the bound auth context.
- `TC-10-evidence.json` — canonical evidence record.
- **Retention:** ≥ 7 years (records-scope; SOX-relevant; NYDFS-relevant).

#### Failure Remediation

1. **If the activation succeeded without a step-up:** the auth context is not bound, the CA policy is mis-configured, or PIM role settings do not reference the context. Sev-1; remediate via [Portal Walkthrough](./portal-walkthrough.md) §10.
2. **If the step-up prompted but session-token reuse satisfied it:** examine the CA policy's grant control — Authentication Strength is the correct grant; "Require MFA" alone allows session-token reuse and does **not** satisfy this test.
3. **If the activation failed entirely** (the canary could not activate even with FIDO2): the role settings or auth-context mapping are misconfigured against the policy; reconcile and re-test.

---

### TC-11 — Sentinel Conditional Access Insights Workbook

**Verifies:** The Microsoft Sentinel **Conditional Access Insights and Reporting** workbook is configured, accessible to the CA Insights reviewer role, and shows data flowing from **both** `SigninLogs` and `AADServicePrincipalSignInLogs` in the last 24 hours; the workbook's findings cross-reference the [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) incident workflow for any flagged anomaly.

**Regulatory tie:** SEC Reg S-P (May 2024 amendments — incident detection); FINRA Notice 21-18; FFIEC Information Security booklet; NYDFS 500.16 (incident response).

#### Setup

1. Confirm the Sentinel workspace has the **Conditional Access Insights and Reporting** workbook deployed (Sentinel → Workbooks → Templates → Conditional Access Insights → Save).
2. Confirm the verifier holds **Sentinel Reader** plus **Log Analytics Reader** on the workspace.

#### Steps

1. Open the workbook. Set the time range to **Last 24 hours**.
2. Confirm the workbook tiles populate from both tables:

    ```kql
    SigninLogs
    | where TimeGenerated > ago(24h)
    | summarize human_signins = count()

    AADServicePrincipalSignInLogs
    | where TimeGenerated > ago(24h)
    | summarize agent_signins = count()
    ```

    Both counts must be > 0 in an active tenant. A `human_signins = 0` is itself a finding (likely connector outage). An `agent_signins = 0` in a tenant that has provisioned AI agents is a finding (likely SP sign-in connector not selected — see PRE-06).
3. Cross-reference any high-severity finding (e.g., a CA policy with > 5% failure rate, a sudden spike in `notApplied` outcomes, or an unexpected service-principal sign-in pattern) to the Control 3.9 incident-workflow ticket queue. Each flagged anomaly must have either an open ticket or a signed false-positive disposition within the cycle's grace window.
4. Capture screenshots of the workbook tiles for both tables and the anomaly cross-reference panel.

#### Expected Result

- The workbook displays non-zero counts for both `SigninLogs` and `AADServicePrincipalSignInLogs` in the last 24 hours.
- Each workbook-flagged anomaly maps to a Control 3.9 incident-workflow item.
- The verifier can demonstrate the path from workbook → KQL → Sentinel incident → ITSM ticket without manual interpretation gaps.

#### Evidence Capture

- `TC-11-workbook-overview.png` — workbook landing page with 24-hour tiles.
- `TC-11-signinLogs-count.csv` — `human_signins` count.
- `TC-11-aadServicePrincipalSignInLogs-count.csv` — `agent_signins` count.
- `TC-11-anomaly-crossref.csv` — anomaly → Control 3.9 incident → ITSM ticket mapping.
- `TC-11-evidence.json` — canonical evidence record.
- **Retention:** ≥ 7 years for the cross-reference CSV (records-scope when it documents an actual incident); workbook screenshots retained per operational policy (typically 2 years).

#### Failure Remediation

1. **If `agent_signins = 0`:** the Service Principal Sign-In Logs option on the `AzureActiveDirectory` connector is not selected. Open a Sev-2 ticket against the Sentinel Contributor; re-test after a 4-hour ingestion window.
2. **If the workbook is missing tiles or shows errors:** re-deploy from the current Microsoft template; verify the workspace permissions.
3. **If anomalies lack 3.9 cross-reference:** route to the AI Governance Lead; the linkage is required for examiner-defensible incident-traceability.

---

### TC-12 — Report-Only → Enforce Change Record

**Verifies:** Every CA policy that has been promoted from **Report-only** to **Enforce** in the cycle window has a corresponding change-management ticket, a Power Platform Admin Center (PPAC) change-log reference where the policy affects Power Platform / Copilot Studio surfaces, and approval signatures from **both** the Authentication Policy Admin and the CISO (or CISO delegate).

**Regulatory tie:** SOX 302/404 (change-management evidence on access controls); FFIEC Information Security booklet (change management); NYDFS 500.04 (CISO oversight); FINRA 4511 / SEC 17a-4 (records of access-control changes).

#### Setup

1. Identify all CA policies whose `state` transitioned from `enabledForReportingButNotEnforced` to `enabled` in the cycle window:

    ```kql
    AuditLogs
    | where TimeGenerated > ago(100d)   // adjust to the cycle window
    | where Category == "Policy" and OperationName == "Update conditional access policy"
    | extend modProps = tostring(TargetResources[0].modifiedProperties)
    | where modProps has "state" and modProps has "enabledForReportingButNotEnforced" and modProps has "enabled"
    | project TimeGenerated, InitiatedByUpn = tostring(InitiatedBy.user.userPrincipalName),
              policyId = tostring(TargetResources[0].id),
              policyName = tostring(TargetResources[0].displayName),
              modProps
    | order by TimeGenerated desc
    ```

2. For each transition, locate the change ticket, approval emails / digital signatures, and (where applicable) the PPAC change-log entry.

#### Steps

1. For every transition row, assemble:
    - The change ticket number (ServiceNow / Jira / equivalent).
    - The Authentication Policy Admin's approval signature (digital or hand-signed scan).
    - The CISO (or CISO delegate) approval signature.
    - The PPAC change-log reference where the policy affects `Power Apps`, `Power Automate`, `Microsoft Copilot Studio`, or the Agent 365 Admin Center:

        ```kql
        PowerPlatformAdminActivity
        | where TimeGenerated > ago(100d)
        | where OperationName has_any ("Conditional Access","CA Policy","SecurityPolicyUpdated")
        | project TimeGenerated, OperationName, ActorUpn, EnvironmentName, TenantId, AdditionalProperties
        | order by TimeGenerated desc
        ```

    - The pre-flip Report-only sign-in evidence (the impact-analysis artifact that justified flipping to Enforce).
2. Build the per-transition evidence package as a single PDF or evidence subfolder.
3. For transitions that lack a complete package, list them in the §13 attestation as findings with remediation deadlines.

#### Expected Result

- Every Report-only → Enforce transition in the cycle window has: change ticket + dual approval + (where applicable) PPAC change-log reference + pre-flip impact-analysis artifact.
- No transition lacks a documented signoff.

#### Evidence Capture

- `TC-12-transitions.csv` — full list of transitions in the cycle window.
- `TC-12-package-<policyId>.pdf` — one per transition; assembled change-management package.
- `TC-12-ppac-changelog.csv` — KQL export from `PowerPlatformAdminActivity`.
- `TC-12-evidence.json` — canonical evidence record listing per-transition completeness.
- **Retention:** ≥ 7 years (records-scope; SOX-relevant; FINRA 4511 evidence of access-control change).

#### Failure Remediation

1. **If a transition lacks a change ticket:** treat as a SOX significant-deficiency candidate; route to Internal Audit and the CISO. The transition itself is not reversed (the policy is now Enforce and may be load-bearing), but the missing ticket must be reconstructed from contemporaneous evidence (email, PPAC log, audit log) and counter-signed.
2. **If a transition lacks dual approval:** capture the missing signature retroactively only with explicit annotation that it was post-hoc; never backdate. Open a process gap and close via the firm's change-management remediation track.
3. **If PPAC change-log evidence is missing for a Power Platform-affecting policy:** confirm the PowerPlatformAdminActivity connector is healthy in PRE-06; reconcile with PPAC blade exports.

---

## §2 Evidence Capture Summary Table

The table below consolidates the per-test evidence artifacts, retention durations, and primary regulation ties. Every row in the table maps to artifacts assembled into the §13 quarterly attestation pack. Where retention is recorded as ≥ 7 years, the artifact is **records-scope** under FINRA Rule 4511 and SEC Rule 17a-4 and must be filed via Microsoft Purview retention labels with deletion lock; **Sentinel operational retention is not a substitute** because Sentinel hot/archive retention is not records-scope.

| Test | Evidence Artifact(s) | Retention | Primary Regulation Tie |
|------|----------------------|-----------|------------------------|
| TC-1 | `TC-1-userRegistrationDetails.csv` (signed); `TC-1-portal-screenshot-userRegistrationDetails.png`; `TC-1-evidence.json` | ≥ 7 years (records-scope) | NYDFS 23 NYCRR 500.12; FFIEC Authentication and Access; NIST SP 800-63B AAL3; GLBA / FTC Safeguards 16 CFR §314.4(c)(5) |
| TC-2 | `TC-2-signin-interrupt.png`; `TC-2-signinLogs.csv` (CA "Not Applied / Failure" sign-in row); `TC-2-ca-policy-snapshot.json`; `TC-2-evidence.json` | ≥ 7 years (records-scope) | SEC Rule 17a-4; FINRA Rule 4511 (via Purview retention); NYDFS 500.12 |
| TC-3 | `TC-3-block-interrupt.png`; `TC-3-intune-device-status.png`; `TC-3-signinLogs.csv` (CA "Not Applied / Failure" sign-in row); `TC-3-ca-policy-snapshot.json`; `TC-3-evidence.json` | ≥ 7 years (records-scope) | SEC Rule 17a-4; FINRA Rule 4511 (via Purview retention); FFIEC Authentication and Access; CISA ZTMM v2.0 |
| TC-4 | `TC-4-graph-call-out-of-location.json`; `TC-4-graph-call-in-location.json`; `TC-4-aadServicePrincipalSignInLogs.csv` (KQL result); `TC-4-signinLogs-empty-confirmation.csv`; `TC-4-ca-wid-policy-snapshot.json` (with `CAPolicyId`); `TC-4-evidence.json` | ≥ 7 years (records-scope) | OCC Bulletin 2011-12; Federal Reserve SR 11-7; FINRA Notice 21-18; FINRA Notice 25-07 |
| TC-5 | `TC-5-disable-action.json` (audit row); `TC-5-failed-graph-call.txt`; `TC-5-signinLogs-cae.csv`; `TC-5-latency.json`; `TC-5-evidence.json` | ≥ 7 years for audit + sign-in evidence (records-scope); 2 years for latency JSON (operational) | FFIEC Authentication and Access; CISA ZTMM v2.0; NYDFS 500.04 |
| TC-6 | `TC-6-supported-session-token-claim.json`; `TC-6-replay-rejection.txt`; `TC-6-unsupported-fallback.png`; `TC-6-policy-description.md` (intended fallback); `TC-6-signinLogs.csv`; `TC-6-evidence.json` | ≥ 7 years (records-scope) | FFIEC Authentication and Access; CISA ZTMM v2.0; FINRA Notice 21-18 |
| TC-7 | `TC-7-reauth-interrupt.png`; `TC-7-signinLogs.csv` (re-auth row with `enforcedSessionControls`); `TC-7-ca-policy-snapshot.json`; `TC-7-evidence.json` | ≥ 7 years (records-scope) | FFIEC Authentication and Access; SEC Rule 17a-4; NYDFS 500.12 |
| TC-8 | `TC-8-bg-exclusion-coverage.csv`; `TC-8-bg-method-registration.csv`; `TC-8-physical-custody-attestation.pdf` (dual-signed); `TC-8-sentinel-rule-config.json`; `TC-8-sentinel-test-fire.csv` (3.9 incident reference); `TC-8-evidence.json` | ≥ 7 years (records-scope; SOX-relevant) | SOX 302/404; FFIEC Authentication and Access; NYDFS 500.04 / 500.12; OCC 2011-12 / SR 11-7 |
| TC-9 | `TC-9-imap-attempt.txt`; `TC-9-ropc-attempt.json`; `TC-9-signinLogs.csv`; `TC-9-aadServicePrincipalSignInLogs.csv` (where scoped); `TC-9-ca-policy-snapshot.json`; `TC-9-exclusion-register.csv`; `TC-9-evidence.json` | ≥ 7 years (records-scope) | FFIEC Authentication and Access; CISA ZTMM v2.0; SEC Reg S-P (May 2024); NYDFS 500.12 |
| TC-10 | `TC-10-pim-stepup-prompt.png`; `TC-10-auditLogs.csv` (role activation); `TC-10-signinLogs.csv` (auth context `c1`); `TC-10-ca-authcontext-policy.json`; `TC-10-pim-role-settings.json`; `TC-10-evidence.json` | ≥ 7 years (records-scope; SOX-relevant) | SOX 302/404; FFIEC Authentication and Access; NYDFS 500.04 / 500.12; FINRA 4511; OCC 2011-12 / SR 11-7 |
| TC-11 | `TC-11-workbook-overview.png`; `TC-11-signinLogs-count.csv`; `TC-11-aadServicePrincipalSignInLogs-count.csv`; `TC-11-anomaly-crossref.csv` (3.9 incident mapping); `TC-11-evidence.json` | ≥ 7 years for cross-reference CSV when an incident is recorded (records-scope); 2 years for workbook screenshots (operational) | SEC Reg S-P (May 2024); FINRA Notice 21-18; FFIEC Information Security; NYDFS 500.16 |
| TC-12 | `TC-12-transitions.csv`; `TC-12-package-<policyId>.pdf` (per transition; change ticket + dual approval + PPAC change-log + pre-flip impact analysis); `TC-12-ppac-changelog.csv`; `TC-12-evidence.json` | ≥ 7 years (records-scope; SOX-relevant; FINRA 4511) | SOX 302/404; FFIEC Information Security (change management); NYDFS 500.04; FINRA 4511 / SEC 17a-4 |

---

## §3 Quarterly Attestation

The quarterly attestation is the consolidated examiner-facing artifact. It compiles each test case's evidence record, captures the cycle's findings and exceptions, and is signed by the named approvers. Filing of the attestation pack is via the [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) workbook export to a Microsoft Purview retention-labelled location. **Sentinel operational retention is not records-scope** and must not be relied upon as the system of record.

### 3.1 Attestation contents

A complete attestation pack contains:

1. **Cycle metadata** — `runId`, `cycleStartUtc`, `cycleEndUtc`, `cloud`, `tenantId`, `tenantDisplayName`, framework version, prior-cycle reference.
2. **Test results matrix** — one row per TC-1 through TC-12: `status` (PASS / FAIL / WARN / SKIPPED-with-compensating-control), evidence-artifact references, observed values, expected values, and any deviations.
3. **Findings register** — every FAIL or WARN with: severity, owner, remediation deadline, and (where the remediation deadline falls outside the cycle) the signed risk-acceptance with `acceptedRiskUntilUtc`.
4. **Exception register** — all CA-policy exclusions in force at cycle close, each with named-business justification, expiry date, compensating control, and current owner.
5. **Sovereign-cloud reconciliation** — for tenants in GCC, GCC High, or DoD, the per-feature parity statement and any compensating-control worksheets (TC-4 WID, TC-6 Token Protection, Agent ID surfaces).
6. **Cross-control linkage** — explicit pointers to the corresponding cycles for [Control 2.12 — Supervision](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [Control 2.6 — MRM](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md), [Control 1.7 — Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [Control 1.9 — Retention and Deletion](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md), [Control 1.1 — Restrict Agent Publishing](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md), [Control 2.14 — Training and Awareness](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md), [Control 2.25 — Agent 365 Admin Center](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md), [Control 3.6 — Orphaned Agent Detection](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md), and [Control 3.9 — Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).
7. **Approver signatures** — see §3.2.

### 3.2 Signatories

The quarterly attestation is signed by **all five** of the following roles. Signatures are digital (X.509 code-signing or qualified e-signature) and timestamped. Standing privileged-role overlap between Preparer / Validator / Compliance signatories is a cycle-stopping FAIL — the signatories must represent independent control points.

| Signatory (canonical role) | Attestation responsibility |
|---|---|
| **Authentication Policy Admin** | Attests to TC-1 through TC-7, TC-9, TC-10 — the Authentication Method and CA Authentication Strength configuration is current, drift-checked, and consistent with the firm's authentication-policy standard. |
| **Entra Global Admin** | Attests to TC-8 (break-glass integrity), TC-12 (Report-only → Enforce change records), and the overall directory-tier integrity of the cycle. (Activation through PIM, time-bound; no standing Global Admin.) |
| **AI Administrator** | Attests to TC-1 (AI Administrator role coverage), TC-3 (maker portal protections), TC-4 (workload-identity / Agent ID coverage), TC-11 (workbook usability for AI-governance reviewers). |
| **Compliance Officer** | Attests to the records-scope retention posture across the evidence pack, the cross-control linkage to 2.12 / 2.6 / 1.7 / 1.9, and the findings register's remediation tracking. |
| **CISO (or CISO delegate)** | Attests to TC-8 break-glass posture, TC-12 dual-approval evidence, the sovereign-cloud reconciliation, and the overall risk acceptance for any open exceptions or accepted-risk items. |

### 3.3 Retention and filing

- **Records-scope artifacts** (those marked ≥ 7 years in §2) are filed to a Microsoft Purview retention-labelled location with `≥7-year retention` and `deletionLocked = true`. The retention label is bound under [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).
- **The attestation pack itself** is filed via the [Control 3.9 Sentinel workbook export → Purview-labelled SharePoint or Azure Blob WORM container](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md). The export step records a SHA-256 digest of the pack; the digest is itself a records-scope artifact.
- **Sentinel operational retention is not records-scope.** Sentinel hot retention (default 90 days) and archive retention (up to 2 years on standard pricing tiers) are **operational** and must not be relied upon as the system of record for FINRA 4511 / SEC 17a-4 evidence. The Purview-labelled filing location is the system of record.
- **Where records-scope under FINRA 4511 / SEC 17a-4 applies** (which is the case for all TC-1 through TC-12 records-scope artifacts in this control), retention is **at least 7 years** from the date of cycle close. Some firms apply longer retention by policy (e.g., 10 years for SOX-significant artifacts); the longer of the firm's policy and the regulatory minimum applies.

### 3.4 Attestation template (canonical JSON)

```json
{
  "control_id": "1.11",
  "framework_version": "v1.4",
  "cycle": {
    "run_id": "CA111-20260415-093012-a1b2c3d4",
    "cycle_start_utc": "2026-01-15T00:00:00Z",
    "cycle_end_utc":   "2026-04-15T00:00:00Z",
    "cloud": "Commercial",
    "tenant_id": "11111111-2222-3333-4444-555555555555",
    "tenant_display_name": "Contoso Bank, N.A."
  },
  "test_results": [
    { "test": "TC-1",  "status": "PASS",     "evidence_refs": ["TC-1-userRegistrationDetails.csv","TC-1-evidence.json"] },
    { "test": "TC-2",  "status": "PASS",     "evidence_refs": ["TC-2-signinLogs.csv","TC-2-evidence.json"] },
    { "test": "TC-3",  "status": "PASS",     "evidence_refs": ["TC-3-signinLogs.csv","TC-3-evidence.json"] },
    { "test": "TC-4",  "status": "SKIPPED",  "evidence_refs": ["TC-4-sov-compensating-worksheet.pdf"], "skip_reason": "CA WID not GA in operating cloud; compensating worksheet attached." },
    { "test": "TC-5",  "status": "PASS",     "evidence_refs": ["TC-5-latency.json","TC-5-evidence.json"] },
    { "test": "TC-6",  "status": "PASS",     "evidence_refs": ["TC-6-evidence.json"] },
    { "test": "TC-7",  "status": "PASS",     "evidence_refs": ["TC-7-evidence.json"] },
    { "test": "TC-8",  "status": "PASS",     "evidence_refs": ["TC-8-physical-custody-attestation.pdf","TC-8-evidence.json"] },
    { "test": "TC-9",  "status": "PASS",     "evidence_refs": ["TC-9-evidence.json"] },
    { "test": "TC-10", "status": "PASS",     "evidence_refs": ["TC-10-evidence.json"] },
    { "test": "TC-11", "status": "PASS",     "evidence_refs": ["TC-11-evidence.json"] },
    { "test": "TC-12", "status": "WARN",     "evidence_refs": ["TC-12-transitions.csv"], "finding": "1 transition lacks PPAC change-log reference; remediation deadline 2026-04-30." }
  ],
  "findings": [
    {
      "finding_id": "F-2026Q1-001",
      "severity": "Medium",
      "test": "TC-12",
      "owner": "authentication.policy.admin@contoso.com",
      "remediation_deadline_utc": "2026-04-30T17:00:00Z",
      "accepted_risk_until_utc": null
    }
  ],
  "exceptions": [],
  "sovereign_reconciliation": {
    "ca_workload_identities": "GA in Commercial; SKIPPED with compensating worksheet in this run.",
    "token_protection": "Pilot in progress on supported Windows 11 endpoints.",
    "agent_id": "Public Preview; cycle-over-cycle re-confirmation required."
  },
  "cross_control_linkage": {
    "control_2_12_supervision": "cycle 2026-Q1 PASS",
    "control_2_6_mrm": "cycle 2026-Q1 PASS",
    "control_1_7_audit_logging": "cycle 2026-Q1 PASS",
    "control_1_9_retention": "cycle 2026-Q1 PASS",
    "control_3_9_sentinel": "workbook export filed; SHA-256 recorded"
  },
  "signatories": [
    { "role": "Authentication Policy Admin", "upn": "auth.policy.admin@contoso.com",  "signed_utc": "2026-04-15T18:12:00Z", "signature_method": "X.509" },
    { "role": "Entra Global Admin",          "upn": "global.admin@contoso.com",      "signed_utc": "2026-04-15T18:14:00Z", "signature_method": "X.509", "pim_activation_ref": "pim-act-2026-04-15-0001" },
    { "role": "AI Administrator",            "upn": "ai.administrator@contoso.com",  "signed_utc": "2026-04-15T18:16:00Z", "signature_method": "X.509" },
    { "role": "Compliance Officer",          "upn": "compliance.officer@contoso.com","signed_utc": "2026-04-15T18:18:00Z", "signature_method": "X.509" },
    { "role": "CISO",                         "upn": "ciso@contoso.com",              "signed_utc": "2026-04-15T18:20:00Z", "signature_method": "X.509" }
  ],
  "filing": {
    "purview_label": "FSI-Records-7yr-DeletionLocked",
    "filing_location_uri": "https://contoso.sharepoint.com/sites/governance/records/CA111-2026Q1/",
    "pack_sha256": "f3a1...",
    "filing_method": "Control 3.9 Sentinel workbook export → Purview-labelled SharePoint"
  }
}
```

### 3.5 Cycle-stopping conditions

The following conditions stop a cycle from being signed off and require remediation before the attestation can be filed:

1. **TC-1 fail** — any privileged-role member without a phishing-resistant method registered.
2. **TC-8 fail** — any break-glass coverage gap, method drift, or physical custody discrepancy.
3. **TC-12 fail with no compensating evidence** — a Report-only → Enforce transition with no recoverable change-management trail.
4. **Standing privileged-role overlap** between Preparer / Validator / Compliance signatories.
5. **Pre-flight FAIL** — any HALT on PRE-01 through PRE-06.

A cycle that stops on any of the above is reported to FSI Internal Audit as a control deficiency and the assessment engine downgrades the control's confidence rating from `high` to `medium` until the next clean cycle is signed.

---

## §4 Cross-Control Dependencies

This control does not stand alone. The following cross-references connect Control 1.11 to its sibling controls. **Examination evidence is strongest when these controls' evidence packs are presented together, in cycle alignment**, because access-control enforcement (1.11) is one of four required layers — alongside supervisory review (2.12), model risk management (2.6), and books-and-records (1.7 / 1.9) — for a defensible AI-agent governance posture.

- [**Control 1.1 — Restrict Agent Publishing by Authorization**](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) — the authorization model that this control's CA policies enforce identity context against. A 1.11 cycle that does not reference the 1.1 authorization register has an unbounded scope.
- [**Control 1.7 — Comprehensive Audit Logging and Compliance**](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — the books-and-records completeness layer. 1.11 evidences access; 1.7 evidences the trail. Both are required.
- [**Control 1.9 — Data Retention and Deletion Policies**](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) — the Purview retention-labelling that makes 1.11's evidence records-scope under FINRA 4511 / SEC 17a-4.
- [**Control 2.6 — Model Risk Management Alignment with OCC 2011-12 / SR 11-7**](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) — the MRM effectiveness layer. 1.11 enforces identity controls on model-serving endpoints; 2.6 validates the model itself.
- [**Control 2.12 — Supervision and Oversight under FINRA Rule 3110**](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) — the registered-principal supervisory review layer. 1.11 does not satisfy supervision; only 2.12 does.
- [**Control 2.14 — Training and Awareness Program**](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) — operator competence on Authentication Strength, FIDO2 enrollment, and break-glass procedures. The 2.14 cycle's training-completion evidence is referenced by the 1.11 attestation for signatory eligibility.
- [**Control 2.25 — Agent 365 Admin Center Governance Console**](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — the operator surface where many of the 1.11 enforcement signals are first surfaced; TC-2 and TC-3 explicitly target Agent 365 / Copilot Studio access paths.
- [**Control 3.6 — Orphaned Agent Detection and Remediation**](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — the lifecycle layer that pairs with TC-4 (workload-identity coverage) and the sovereign-cloud compensating-control pattern.
- [**Control 3.9 — Microsoft Sentinel Integration**](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) — the SIEM / incident-workflow layer that ingests 1.11's sign-in and audit signals; TC-8 and TC-11 cross-link explicitly.

---

## §5 Glossary (Verifier-Facing)

- **AAL3** — Authenticator Assurance Level 3 (NIST SP 800-63B). Phishing-resistant, hardware-bound or device-bound credential. Synced (cross-device) passkeys do **not** meet AAL3.
- **CA** — Conditional Access (Microsoft Entra).
- **CA WID** — Conditional Access for Workload Identities. Targets service principals, managed identities, and (preview) Entra Agent ID principals.
- **CAE** — Continuous Access Evaluation. Eventually-consistent revocation/claim propagation; per-tenant baseline measured in PRE-07.
- **Authentication Strength** — A named, configurable combination of authentication methods that a CA grant control can require. The framework's Z3 phishing-resistant strength includes FIDO2, WHfB, device-bound passkey, and X.509 CBA — not SMS, voice, or OTP.
- **Authentication Context** — A named claim (e.g., `c1`) bound to a CA policy and consumed by downstream resources (PIM activation, sensitive SharePoint sites) to require step-up MFA at the moment of access, not session-token reuse.
- **Break-glass** — Cloud-only emergency-access account, hardware-FIDO2-only, excluded from every CA policy, dual-custody physical key storage, Sentinel-alerted on any sign-in.
- **Records-scope** — Records subject to FINRA Rule 4511 / SEC Rule 17a-4 retention-and-immutability requirements. Filed via Purview retention labels with deletion lock. **Not** Sentinel operational retention.
- **`SigninLogs`** — Sentinel/Graph table for **human** sign-ins.
- **`AADServicePrincipalSignInLogs`** — Sentinel/Graph table for **service principal / workload identity** sign-ins. Agent sign-ins appear here, **not** in `SigninLogs`.
- **`AuditLogs`** — directory write operations (CA, role, attribute changes).
- **`PowerPlatformAdminActivity`** — PPAC change-log table; corroborates TC-12 transitions affecting Power Platform / Copilot Studio surfaces.
- **PPAC** — Power Platform Admin Center.
- **PIM** — Privileged Identity Management (Microsoft Entra). JIT activation of eligible role assignments.
- **Report-only / Enforce** — CA policy `state` values. `enabledForReportingButNotEnforced` evaluates and logs but does not deny; `enabled` evaluates, logs, and denies. The Report-only → Enforce transition is the change-management gate evidenced by TC-12.
- **SOV** — Sovereign-cloud namespace; compensating-control pattern when a feature is unavailable in GCC, GCC High, or DoD.
- **Token Protection** — Preview CA session control that binds the access token to the device. Windows-only at the verification date; documented fallback for non-supported clients.

---

## §6 Change Log for This Playbook

| Date | Version | Change | Author |
|---|---|---|---|
| 2026-04-18 | v1.4 | End-to-end rewrite to the 12-test-case structure; added explicit scope-limit and sovereign-cloud admonitions; corrected `SigninLogs` vs `AADServicePrincipalSignInLogs` table guidance throughout (TC-4); added quarterly attestation JSON template; aligned canonical role names; added cross-references to Controls 1.1, 1.7, 1.9, 2.6, 2.12, 2.14, 2.25, 3.6, 3.9. | Doc Writer Agent |
| 2026-01-12 | v1.3 | Added CAE per-tenant baseline (PRE-07); removed invented Microsoft SLA assertions on CAE latency. | Doc Writer Agent |
| 2025-10-04 | v1.2 | Added Token Protection (Preview) test case with documented fallback. | Doc Writer Agent |
| 2025-07-15 | v1.1 | Added break-glass dual-custody attestation. | Doc Writer Agent |
| 2025-04-08 | v1.0 | Initial publication. | Doc Writer Agent |

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*



