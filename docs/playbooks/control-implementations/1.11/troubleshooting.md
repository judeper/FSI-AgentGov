# Control 1.11 — Conditional Access + Phishing-Resistant MFA for AI Agents: Troubleshooting Playbook

**Companion to:** [Control 1.11 — Entra Conditional Access and Phishing-Resistant MFA](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md)
**Sibling playbooks:** [Portal Walkthrough](./portal-walkthrough.md) · [PowerShell Setup](./powershell-setup.md) · [Verification & Testing](./verification-testing.md) · [CA Agent Templates](./conditional-access-agent-templates.md)
**Audience:** Authentication Policy Admin, Entra Security Admin, Entra Privileged Role Admin, Entra Global Admin (PIM-elevated, break-glass only), AI Administrator, Purview Compliance Admin, SOC analyst on call, Service Desk Tier 2/3.
**Scope:** Symptom-first diagnosis and remediation for Conditional Access (CA) policy enforcement, phishing-resistant authentication strengths, FIDO2 / Windows Hello for Business registration, Token Protection, Continuous Access Evaluation (CAE), CA for Workload Identities, Entra Agent ID preview targeting, break-glass discipline, and sovereign-cloud parity gaps as they affect Microsoft 365 AI agents (Copilot, Copilot Studio agents, Power Platform agents, custom Graph-calling apps).

> **Regulatory framing.** The procedures in this playbook **support compliance with** FFIEC Authentication Guidance, NYDFS 23 NYCRR Part 500 (notably §500.12 MFA — fully effective November 1, 2025 — and §500.17(a) 72-hour notification), FINRA Rule 3110 (supervision) and Rule 4511 (records), SEC Rule 17a-4(f) (WORM evidence retention), SOX §404 ITGC change-control and access-provisioning expectations, GLBA / FTC Safeguards Rule 16 CFR §314.4(c)(5) (MFA), OCC Heightened Standards / Bulletin 2011-12, Federal Reserve SR 11-7, and CFTC Regulation 1.31. They do **not** by themselves guarantee any regulatory outcome. Implementation requires the SKUs (Entra ID P2, Workload Identities Premium where applicable), role separations, change-control discipline, and annual exception approvals described below; organizations should verify each procedure end-to-end in a non-production tenant before production execution and engage Legal / Compliance before any tenant-wide CA mutation.

!!! warning "Scope Limit"
    This playbook covers **preventive identity and access** failures only — Conditional Access enforcement, phishing-resistant MFA registration, Token Protection, CAE, CA for Workload Identities, and Entra Agent ID targeting. It is **not** the triage path for:

    - **Supervisory review failures** of agent prompts, outputs, or content moderation — see [Control 2.12 — Agent Communication Supervision](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).
    - **Records-and-retention failures** affecting agent transcripts, audit immutability, or Purview retention labels — see [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).
    - **Token-theft / session-hijack incidents** with confirmed lateral movement — handle the access-side rollback here, then hand off to the firm-wide token-theft runbook (Control 1.21).
    - **Post-incident root-cause analysis and reporting** — feed findings into [Control 3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).

    If the presenting symptom does not appear in the §0 triage tree below, consult the supervisory or records playbook before mutating any CA or auth-method policy state.

!!! warning "Sovereign Cloud Availability"
    As of April 2026, the following Control 1.11 capabilities are **not at parity** in Microsoft Cloud for US Government (GCC), GCC High, or DoD:

    - **Conditional Access for Workload Identities** (general availability is commercial-cloud only; sovereign tenants must use the §15 compensating-control runbook).
    - **Entra Agent ID** preview targeting in CA policies (preview-flag controlled in commercial; not yet enabled in sovereign).
    - **Token Protection for sign-in tokens** (Edge-only enforcement available in commercial; sovereign Edge build parity verified per release).
    - **Authentication Strengths "Phishing-resistant MFA" built-in** (available in sovereign; FIDO2 attestation services for non-Microsoft AAGUIDs may have limited reachability — verify per release notes).

    Sovereign-tenant operators must document the parity gap in the tenant Risk Register, apply the compensating controls in §15, and re-verify at each Microsoft sovereign-cloud feature-availability publication.

!!! danger "Break-Glass Discipline"
    A break-glass (BG) account is invoked **only** when **all** of the following are true:

    1. The standard administrative path is fully blocked (e.g., every Authentication Policy Admin and Entra Security Admin is locked out by a CA misconfiguration, PIM activation is failing tenant-wide, or the Entra portal is returning a 5xx for every privileged sign-in).
    2. A SEV-1 incident has been declared and acknowledged by both the SOC duty manager and the on-call CISO delegate.
    3. **Two-person rule** is met: CISO (or named delegate) **and** Authentication Policy Admin (or Entra Privileged Role Admin) both attest in the incident record that no non-break-glass path exists.
    4. The BG account is signed in **only** with its registered phishing-resistant FIDO2 key from physical custody (the safe), and **only** to perform the minimum necessary remediation. SMS, voice, software OATH TOTP, email OTP, and synced passkeys are **never** acceptable BG factors.
    5. A Sentinel rule (`BreakGlassUsedOutsideTest`) will fire on the BG sign-in within minutes; the incident record must reference the alert ID and the alert must be acknowledged by the CISO within 30 minutes.

    **After any BG use:** the quarterly BG-test schedule restarts immediately; a full BG post-use review is convened within 5 business days; findings feed [Control 3.4 — Incident Reporting and RCA](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md). BG use **without** all five criteria met is itself a SOX deficiency.

---

## §0 Triage Tree (Symptom → Scenario)

| # | Presenting symptom (what the user or admin actually sees) | Go to |
|---|-----------------------------------------------------------|-------|
| 1 | "Your security key is not supported" or "We cannot register this key" during FIDO2 registration on aka.ms/mysecurityinfo | [§1](#1-fido2-key-registration-rejected-key-is-not-supported) |
| 2 | CA policy in report-only is generating a high count of "Would have blocked" decisions for the agent maker / Copilot Studio author group | [§2](#2-report-only-ca-policy-shows-high-would-have-blocked-for-agent-maker-group) |
| 3 | Token Protection pilot is blocking legitimate sign-ins from Firefox / Chrome / Safari users, Edge users unaffected | [§3](#3-token-protection-pilot-blocking-legitimate-non-edge-browser-access) |
| 4 | A scheduled Graph job, Logic App, or unattended agent service principal is suddenly failing with `AADSTS53003` after a CA Workload Identities policy was promoted | [§4](#4-service-principal-blocked-by-ca-workload-identities-policy-on-scheduled-job) |
| 5 | A break-glass account is reporting "locked", "MFA required", or "key not present" during a quarterly test or live invocation | [§5](#5-break-glass-account-lockout-or-failed-quarterly-test) |
| 6 | PIM role activation for an Authentication Policy Admin or Entra Global Admin returns "phishing-resistant authentication required" but the admin only has SMS / Authenticator-push registered | [§6](#6-pim-activation-fails-with-phishing-resistant-required-on-sms-registered-admin) |
| 7 | A privileged user's count of registered phishing-resistant authentication methods has dropped to 0 (device loss, key returned, employment change) and they retain admin-eligible PIM assignments | [§7](#7-privileged-user-phishing-resistant-method-count-drops-to-zero) |
| 8 | The Sentinel "Conditional Access Insights and Reporting" workbook (or the FSI-AgentGov CA Insights workbook) is empty, partial, or stuck on "Loading" | [§8](#8-sentinel-conditional-access-insights-workbook-empty-or-stale) |
| 9 | An AI Administrator who can sign in to the Entra portal is denied at the Microsoft Agent 365 Admin Center (`Sorry, access denied. Conditional Access policy required.`) after a CA tenant flip | [§9](#9-microsoft-agent-365-admin-center-access-denied-after-ca-policy-flip) |
| 10 | A user was disabled or had their refresh tokens revoked, but is still seen accessing Copilot, SharePoint, or a Zone 3 agent for >30 minutes after revocation | [§10](#10-continuous-access-evaluation-not-propagating-revocations) |
| 11 | A user's sign-in shows `ConditionalAccessStatus = notApplied` or two CA policies producing contradictory results; the audit shows multiple `Source = Microsoft` policies overlapping a custom policy | [§11](#11-conflicting-conditional-access-policies-producing-inconclusive-or-contradictory-results) |
| 12 | A GCC High or DoD tenant cannot find the **Conditional Access > Workload Identities** blade or the policy author returns `featureNotAvailable` | [§12](#12-sovereign-cloud-gcc-high-dod-conditional-access-for-workload-identities-unavailable) |
| 13 | Authentication Strengths blade is not visible under **Entra → Protection → Authentication methods**, or "Phishing-resistant MFA" cannot be selected as a grant control | [§13](#13-authentication-strengths-ui-not-visible) |
| 14 | A managed identity attached to a Logic App or Function App is being denied by a CA Workload Identities policy that was meant to target only third-party SaaS service principals | [§14](#14-managed-identity-blocked-by-over-broad-ca-workload-identity-policy) |
| 15 | Copilot Studio publish action returns `conditional access required` even though the maker has registered a passkey and signed in successfully ten minutes earlier | [§15](#15-copilot-studio-publish-fails-with-conditional-access-required-despite-registered-passkey) |
| 16 | An Entra Agent ID preview workload identity for a newly-deployed Copilot Studio agent does not appear in CA Workload Identities policy targeting pickers | [§16](#16-entra-agent-id-preview-service-principals-not-appearing-in-conditional-access-targeting) |

> **How to use this tree.** Identify the presenting symptom first. Each scenario below is structured: **Symptom → Likely Cause (frequency-ordered) → Diagnostic Steps → Resolution → Prevention → Regulatory / Evidence Implications**. Do not skip the diagnostic steps — every resolution that mutates a CA policy or an auth-method policy is gated on the diagnostic evidence captured first.

---

## §1 FIDO2 Key Registration Rejected ("Key Is Not Supported")

### Symptom

A user attempting first-time FIDO2 registration at **https://aka.ms/mysecurityinfo** → **Add sign-in method → Security key** sees one of:

- "Your security key is not supported. Please contact your administrator." (most common)
- "We can't register this key with this account."
- The browser silently aborts the WebAuthn ceremony with no Entra-side audit event.
- The Authenticator-app passkey path completes, but the physical security key path does not.

The user reports the same key worked on a personal account or in a different tenant.

### Likely Cause (frequency-ordered)

1. **Authentication Methods Policy does not enable FIDO2 for the user's group.** Most common in tenants that migrated from the legacy "MFA service settings" page to the modern Authentication Methods Policy without explicitly enabling FIDO2 for the workforce groups. The legacy page may show FIDO2 as enabled while the modern policy enforces a `state = "disabled"` for the user's effective scope.
2. **AAGUID is not on the FIDO2 key restrictions allow-list.** The Authentication Methods Policy can be configured with `keyRestrictions.enforcementType = "allow"` and an explicit AAGUID allow-list. Any AAGUID not on the list is rejected with the generic "not supported" error. FSI tenants commonly allow only FIDO2 L2-certified, attestation-verifiable AAGUIDs (e.g., specific YubiKey 5 series, Feitian, Token2 firmware-locked variants).
3. **Attestation enforcement (`isAttestationEnforced = true`) blocks keys that cannot present an FIDO MDS-resolvable attestation statement.** Some keys ship with self-attestation only or with attestation roots not present in the Microsoft attestation cache.
4. **Browser unsupported or out-of-date.** WebAuthn requires modern Edge / Chrome / Firefox / Safari with platform-authenticator and roaming-authenticator support. Tenants that pin Internet Explorer mode or legacy Edge for legacy line-of-business apps see this on the same machine that registers fine in modern Edge.
5. **Cross-tenant access settings or device compliance** is interfering. Less common, but a B2B guest registering a key in the resource tenant may hit a cross-tenant access policy that blocks the registration ceremony.
6. **TPM / Windows Hello for Business pre-emption.** On Windows 11 with WHfB enrolled, the platform authenticator may take precedence and the roaming key path may not surface; the user perceives this as "the key did nothing."

### Diagnostic Steps

**Portal path.**

1. **Entra admin center → Protection → Authentication methods → Policies → FIDO2 security key**. Confirm `Enable` is on, the user is in the **Include** scope (directly or via group), and not in the **Exclude** scope.
2. Open the **Configure** tab. Note `Allow self-service set up` (must be **Yes** for end-user registration), `Enforce attestation`, `Enforce key restrictions`, `Restrict specific keys` (Allow / Block), and the AAGUID list.
3. **Entra admin center → Users → {user} → Authentication methods**. Confirm no existing FIDO2 entry from a previous registration attempt that is now stuck.
4. **Entra admin center → Monitoring → Audit logs**. Filter `Service = Authentication Methods`, `Activity = User registered security info` and `Activity = Update authentication method`. The audit log surfaces the AAGUID and the failure reason.

**Microsoft Graph (PowerShell SDK v2+).**

```powershell
# Confirm the effective FIDO2 policy
Connect-MgGraph -Scopes "Policy.Read.All","UserAuthenticationMethod.Read.All"

$fido2Policy = Invoke-MgGraphRequest -Method GET `
    -Uri "https://graph.microsoft.com/v1.0/policies/authenticationMethodsPolicy/authenticationMethodConfigurations/Fido2"
$fido2Policy | ConvertTo-Json -Depth 10

# Pull the user's currently registered methods
$upn = "alex.maker@contoso.com"
$user = Get-MgUser -Filter "userPrincipalName eq '$upn'"
Invoke-MgGraphRequest -Method GET `
    -Uri "https://graph.microsoft.com/v1.0/users/$($user.Id)/authentication/methods"
```

**KQL (sign-in / audit logs in Log Analytics workspace `SecurityLogs`).**

```kusto
// Failed FIDO2 registration audit events for a user, last 24h
AuditLogs
| where TimeGenerated > ago(24h)
| where LoggedByService == "Authentication Methods"
| where TargetResources has "alex.maker@contoso.com"
| where Result != "success"
| extend method = tostring(parse_json(tostring(AdditionalDetails))[0].value)
| project TimeGenerated, ActivityDisplayName, Result, ResultReason, method, AdditionalDetails
| order by TimeGenerated desc
```

```kusto
// Tenant-wide FIDO2 registration failure rate, last 7d (used to confirm scope vs single-user)
AuditLogs
| where TimeGenerated > ago(7d)
| where ActivityDisplayName == "User registered security info"
| where AdditionalDetails has "Fido2"
| summarize total = count(), failures = countif(Result != "success") by bin(TimeGenerated, 1d)
| extend failureRate = round(100.0 * failures / total, 2)
```

### Resolution

> **Change-control gate.** Any modification to the Authentication Methods Policy is a tenant-wide change governed by the firm's standard change ticket (ServiceNow CHG template `IDM-AUTHMETHOD`). A second Authentication Policy Admin must co-sign per the two-admin pattern; the change cannot proceed without an attached `-WhatIf` PowerShell stub demonstrating the diff.

1. **If FIDO2 is disabled for the user's effective scope**: add the user's intended group to the FIDO2 policy `Include` scope. Use the change template; do **not** set Include to "All users" without a documented Risk Register entry.

   ```powershell
   # -WhatIf stub: pull current policy, compute diff, write change record
   $current = Invoke-MgGraphRequest -Method GET `
       -Uri "https://graph.microsoft.com/v1.0/policies/authenticationMethodsPolicy/authenticationMethodConfigurations/Fido2"
   $proposed = $current.Clone()
   $proposed.includeTargets += @{ targetType = "group"; id = "<group-object-id>"; isRegistrationRequired = $false }
   Write-Host "WhatIf: would add group <group-object-id> to FIDO2 includeTargets"
   Write-Host "Diff:" ; Compare-Object ($current.includeTargets | ConvertTo-Json) ($proposed.includeTargets | ConvertTo-Json)
   # Apply only after change-record approval and second-admin co-sign:
   # Invoke-MgGraphRequest -Method PATCH -Uri "https://graph.microsoft.com/v1.0/policies/authenticationMethodsPolicy/authenticationMethodConfigurations/Fido2" -Body ($proposed | ConvertTo-Json -Depth 10)
   ```

2. **If the AAGUID is not on the allow-list**: confirm the key model is on the firm's approved-authenticator list (curated by the Authentication Policy Admin in coordination with the CISO). If approved, add the AAGUID to `keyRestrictions.aaGuids`. If not approved, supply the user with a model from the issued inventory and recover any unsanctioned key per asset-handling policy.
3. **If attestation enforcement is the cause**: do **not** disable attestation enforcement to "fix" a single user; this weakens the AAL3 posture for the tenant. Replace the key with one whose attestation root is resolvable via FIDO MDS (the firm's approved-authenticator list should already filter for this).
4. **If the browser is unsupported**: have the user retry in Microsoft Edge (current channel) or Chrome (current channel). Document the browser version in the ticket. If the user is forced into IE Mode by an enterprise site list, register from a different browser session.
5. **If WHfB is pre-empting the roaming key**: in modern Edge, the registration UI now surfaces a "Use a different device" branch — guide the user explicitly to the security-key option, not "this device".

### Prevention

- **Authentication Methods Policy hardening baseline** — codified in [`powershell-setup.md`](./powershell-setup.md) and exercised quarterly. The baseline pins FIDO2 enabled for the workforce, attestation enforced, AAGUID allow-list in place, and the policy state version-controlled.
- **Approved-authenticator list** — published in the Identity Standards SharePoint site, reviewed annually by the Authentication Policy Admin and the CISO, and referenced from the user-facing registration runbook.
- **Pre-issuance ceremony** — for privileged users (Authentication Policy Admin, Entra Global Admin, Purview Compliance Admin), keys are pre-registered in the Service Desk before issuance; the registration is verified before the key leaves the desk.
- **Self-service registration health KPI** — surfaced by the Sentinel CA Insights workbook (see §8); a sustained tenant-wide FIDO2 registration failure rate >5% triggers a SEV-3 ticket to the Authentication Policy Admin.
- See [Control 2.6 — Identity Lifecycle Management](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) for joiner/mover/leaver registration timing and [Control 2.14 — Privileged Identity Management](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) for privileged-user registration prerequisites.

### Regulatory / Evidence Implications

A single-user FIDO2 registration failure is not by itself a regulator-notifiable event. **However**:

- If the user is an **Authentication Policy Admin, Entra Global Admin, or other Tier-0 role holder** and the failure leaves them **without any registered phishing-resistant method**, treat the situation per §7 (privileged user method-count drop to zero). NYDFS §500.12 (effective November 1, 2025) requires MFA for all individuals accessing any information system; a privileged user with **no** AAL3-eligible method is a §500.12 control gap to be documented.
- If the failure is **tenant-wide** (failure rate >25% sustained for >1 hour), escalate to SEV-2 and treat as a control degradation feeding [Control 3.4 — Incident Reporting and RCA](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md). Capture the audit-log export, the Authentication Methods Policy snapshot, and the change-record history per the §17 evidence floor.
- For FINRA-supervised users, document the registration ticket and resolution in the user's identity record per FINRA Rule 4511; SMS / voice / email OTP **must not** be used as a workaround pending FIDO2 re-registration.

---

## §2 Report-Only CA Policy Shows High "Would Have Blocked" for Agent Maker Group

### Symptom

A CA policy authored in **report-only** mode (`enabledForReportingButNotEnforced`) and targeted at the Copilot Studio / Power Platform maker population shows, in the Conditional Access Insights and Reporting workbook (or the Sign-in logs `Conditional Access > Report-only` filter), a high count of **"Would have blocked"** outcomes. Common framing in stakeholder reports: "If we promote this policy, we will block 38% of our makers from publishing tomorrow."

### Likely Cause (frequency-ordered)

1. **Group membership drift.** The CA policy targets `Copilot-Makers-All` but that group is auto-populated from a license SKU or from a dynamic membership rule that has expanded beyond the originally scoped maker community (e.g., now includes contractors, B2B guests, or service accounts that were never intended to be makers).
2. **Named-locations scope is wrong.** The "Would have blocked" reason resolves to `Location not in trusted IPs` because the named-locations object was built from a pre-VPN-migration IP table. Remote and split-tunnel users now egress from public ISPs, not the corporate edge.
3. **Device compliance posture gap.** The grant control requires `Compliant device`, but a non-trivial portion of the maker group is using BYOD / unenrolled devices, MAM-only devices, or devices stuck in a stale Intune compliance state.
4. **Exclusion-group lapse.** A previously-maintained exclusion group (e.g., the Copilot Studio maker pilot, certain executive assistants who use a kiosk pattern) has expired its access-review cycle and the membership has dropped to zero, so users who used to be excluded are now included.
5. **Authentication strength mismatch.** The policy requires "Phishing-resistant MFA" but a portion of the maker group has only Authenticator-push or Authenticator-passkey-synced registered.
6. **App scope wider than intended.** The policy targets "Office 365" (which is a large cloud-app group including Copilot, SharePoint, Exchange, Teams) rather than the specific app object IDs for Copilot Studio and the Power Platform maker portal.

### Diagnostic Steps

**Portal path.**

1. **Entra → Protection → Conditional Access → Insights and reporting**. Filter to the policy ID, time range = last 7 days. Note the top three failure reasons in the **"Would have blocked" by reason** breakdown.
2. **Entra → Protection → Conditional Access → Policies → {policy} → View policy impact**. Cross-check the user-count per Include/Exclude resolution against the expected maker population.
3. **Entra → Sign-in logs → Conditional Access tab**. Filter `ConditionalAccessStatus = reportOnlyFailure` and the policy id. Inspect a representative sample of 10–20 events for `conditionsNotSatisfied`.

**KQL.**

```kusto
// Top reasons a report-only policy "would have blocked" — last 7 days
SigninLogs
| where TimeGenerated > ago(7d)
| mv-expand policy = todynamic(ConditionalAccessPolicies)
| where tostring(policy.id) == "{policy-guid}"
| where tostring(policy.result) in ("reportOnlyFailure","reportOnlyInterrupted")
| extend reason = tostring(policy.conditionsNotSatisfied)
| summarize wouldBlockCount = count() by reason, AppDisplayName
| order by wouldBlockCount desc
```

```kusto
// Distribution of wouldBlock outcomes by user — identify whether 80% of pain is concentrated in 5% of users
SigninLogs
| where TimeGenerated > ago(7d)
| mv-expand policy = todynamic(ConditionalAccessPolicies)
| where tostring(policy.id) == "{policy-guid}" and tostring(policy.result) startswith "reportOnly"
| summarize blocks = count() by UserPrincipalName
| order by blocks desc
| take 50
```

**Microsoft Graph (PowerShell).**

```powershell
# Snapshot the current group membership to confirm scope expansion
$grp = Get-MgGroup -Filter "displayName eq 'Copilot-Makers-All'"
$members = Get-MgGroupMember -GroupId $grp.Id -All
$members | Measure-Object   # baseline count
$members | Where-Object { $_.AdditionalProperties.userType -eq 'Guest' } | Measure-Object   # guest count

# Pull named-locations referenced by the policy
$pol = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policy-guid}"
$pol.conditions.locations | ConvertTo-Json -Depth 10
```

### Resolution

> **Change-control gate.** Promoting any policy from report-only to `enabled` requires a change record with attached What-If output, the Insights workbook 7-day snapshot, the maker-group membership snapshot, and the named-locations export. Two-admin co-sign is mandatory.

1. **Tighten the included population.** If group membership has drifted, re-scope the policy to a curated `Copilot-Makers-Approved` group sourced from the Agent Registry (Control 1.2) rather than from a license SKU. Run an access review (Entra → Identity Governance → Access reviews) before promotion.
2. **Refresh named locations.** Pull current corporate egress IP ranges from Networking; rebuild the `Trusted-Egress-Corp` named location object. Verify split-tunnel and VPN populations either egress through the trusted ranges or are explicitly excluded with a documented compensating control (e.g., compliant-device requirement plus risk-based sign-in policy).
3. **Pre-remediate device compliance.** Run an Intune compliance dashboard report for the maker group; for the unenrolled / non-compliant subset, run an enrollment campaign **before** promoting the CA policy. Do not promote a compliant-device policy when >5% of the included scope cannot satisfy it within 24 hours.
4. **Restore exclusion groups.** Re-establish the exclusion group (e.g., `CA-Exclude-Maker-Pilot`) with an active access review; re-add the documented exception members. Each exclusion must have a Risk Register entry and an annual CISO sign-off.
5. **Pre-register phishing-resistant methods.** Run a registration campaign for any maker without a FIDO2 / WHfB credential. Use the Authentication Methods Activity report to confirm the population is at 100% before promotion.
6. **Tighten the app scope.** Replace "Office 365" with the explicit Copilot Studio and Power Platform app object IDs if the intent is to govern only the maker surfaces.

```powershell
# -WhatIf stub — promote from report-only to enabled
$polId = "{policy-guid}"
$current = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/$polId"
Write-Host "Current state: $($current.state)"
Write-Host "WhatIf: would PATCH state -> 'enabled'. Required attachments: change record, Insights 7d snapshot, group snapshot, named-locations export."
# Apply only after change-record approval and second-admin co-sign:
# Invoke-MgGraphRequest -Method PATCH -Uri "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/$polId" -Body (@{ state = "enabled" } | ConvertTo-Json)
```

After promotion, keep the policy under elevated monitoring for 72 hours; the on-call Authentication Policy Admin reviews the Insights workbook every 4 hours during business and at start-of-day for two weekend days.

### Prevention

- **Report-only-then-enforce discipline** — every new CA policy ships in report-only for a minimum of 7 calendar days (14 for any policy targeting >1,000 users or any Zone 3 surface).
- **Group-source-of-truth** — CA policies targeting the maker population MUST source from the Agent Registry, not from a license SKU.
- **Named-location lifecycle** — the Networking team owns the named-location refresh quarterly; the Authentication Policy Admin verifies the refresh against the firm's egress posture.
- **Pre-flight device-compliance and method-registration campaigns** — codified in [`portal-walkthrough.md`](./portal-walkthrough.md) §3.2.
- See [Control 1.1 — Restrict Agent Publishing by Authorization](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) for the maker-population governance, [Control 2.6 — Identity Lifecycle Management](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) for joiner/leaver group hygiene, and [Control 2.26 — Power Platform Environment Strategy](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) for environment-to-policy alignment.

### Regulatory / Evidence Implications

A high "Would have blocked" rate in report-only is **not** by itself a regulator-notifiable event — the policy is, by definition, not enforcing — but the workflow around it has SOX and FINRA implications:

- **SOX ITGC** — Promoting a CA policy that demonstrably blocks legitimate users without remediation is a change-control deficiency. The change record must show the Insights snapshot, the remediation plan, and the residual-risk acceptance.
- **FINRA supervision** — If the policy materially affects the supervised population's ability to perform supervised activities (e.g., publishing a customer-facing Copilot Studio agent), the change must be reviewed with the FINRA Designated Supervisor before promotion.
- **NYDFS §500.12** — A policy that improves the MFA posture of the maker community supports §500.12 compliance, but a botched promotion that locks out the population creates an availability incident; if it crosses the firm's materiality threshold (e.g., affects customer-facing services), assess against the §500.17(a) 72-hour notification clock.

---

## §3 Token Protection Pilot Blocking Legitimate Non-Edge Browser Access

### Symptom

A Token Protection (sign-in token binding) CA policy promoted from preview to a pilot population is now generating sign-in failures (`AADSTS530034` / "sign-in failed due to token protection policy") for legitimate users on Firefox, Chrome, Safari, or older Edge channels. Edge (Stable, Beta, Canary, current channel) users on Windows 11 are unaffected. Users perceive intermittent or persistent sign-in failures to Microsoft 365 desktop and web apps.

### Likely Cause (frequency-ordered)

1. **Browser support matrix gap.** Sign-in token protection currently requires platform support for the binding cryptography. As of the April 2026 rollout, Microsoft Edge on Windows 11 with TPM is the supported browser; other browsers and other OSes have variable / no support, depending on Microsoft's published matrix.
2. **OS / TPM gap.** Even on Edge, the device must have a TPM 2.0 and meet the platform-bound key requirements; older Windows 10 devices and Mac devices may not be in scope.
3. **Policy scope too broad.** The pilot policy was scoped to "All cloud apps" and "All users in pilot group" without an Edge-only client-app filter, so non-Edge sessions hit the policy unintentionally.
4. **Mobile clients out of scope.** Outlook mobile, Teams mobile, and other native mobile clients are not in the Token Protection scope; if the CA policy was authored against `clientAppType = all`, these mobile clients fail.
5. **Browser version regression.** A Chrome or Edge update reverted a WebAuthn / token-binding capability; verify against Microsoft's known-issues feed.

### Diagnostic Steps

**Portal path.**

1. **Entra → Sign-in logs**. Filter `Status = Failure` and `Conditional Access = Failure` for the affected user; expand the failure detail to confirm the failing policy is the Token Protection policy and the `clientAppUsed` / `browser` field.
2. **Entra → Protection → Conditional Access → Policies → {Token Protection policy}**. Verify Session control "Require token protection for sign-in sessions" is on; verify Conditions → Client apps; verify Conditions → Device platforms.
3. Compare against Microsoft's published support matrix for Token Protection (linked from the policy authoring blade as "Learn more").

**KQL.**

```kusto
// Token Protection failures broken down by browser / OS — last 24h
SigninLogs
| where TimeGenerated > ago(24h)
| where ResultType in ("530034","53003")
| mv-expand policy = todynamic(ConditionalAccessPolicies)
| where tostring(policy.displayName) has "Token Protection"
| extend browser = tostring(DeviceDetail.browser), os = tostring(DeviceDetail.operatingSystem)
| summarize failures = count() by browser, os, AppDisplayName
| order by failures desc
```

```kusto
// Confirm Edge users on Windows 11 are NOT failing — sanity check
SigninLogs
| where TimeGenerated > ago(24h)
| where DeviceDetail.browser startswith "Edge" and DeviceDetail.operatingSystem startswith "Windows 11"
| where ResultType in ("530034")
| count
```

### Resolution

> **Change-control gate.** Narrowing or rolling back a Token Protection policy is a SOX-relevant change. A second Authentication Policy Admin must co-sign; the change record must reference the Microsoft published support matrix version-of-record at the time of decision.

1. **Scope to Edge on Windows 11 (the supported matrix).** Re-author the CA policy with Conditions → Device platforms = `Windows`, Conditions → Client apps = `Browser`, and use a custom **Filter for devices** rule that constrains to Edge — e.g., a managed-device attribute populated by Intune for the Edge-on-Windows-11 fleet. Until first-party "browser = Edge" condition is GA, the device-filter approach is the documented pattern.
2. **Document product unavailability** for non-Edge browsers in the tenant Risk Register and in the Identity Standards SharePoint site as "Token Protection is browser-dependent; non-Edge browsers continue to rely on the standard CA + phishing-resistant MFA stack until parity is reached."
3. **Hold the policy in report-only** while remediating. Do not enforce against an unsupported browser fleet.
4. **Plan parity.** Track Microsoft's roadmap for non-Edge browser support; the AI Governance Lead reviews the support matrix at each quarterly Operating Model meeting (Control 3.4 cadence applies for any open product unavailability).

```powershell
# -WhatIf stub — narrow Token Protection policy to Edge-on-Windows-11 only
$polId = "{token-protection-policy-guid}"
$current = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/$polId"
$proposed = $current
$proposed.conditions.platforms = @{ includePlatforms = @("windows") }
$proposed.conditions.clientAppTypes = @("browser")
# Add device filter for Edge — requires Intune-populated extension attribute
$proposed.conditions.devices = @{ deviceFilter = @{ mode = "include"; rule = 'device.extensionAttribute1 -eq "Edge-Win11"' } }
Write-Host "WhatIf: would narrow policy '$($current.displayName)' to Edge-on-Windows-11. Diff captured."
# Apply only after change-record approval and second-admin co-sign.
```

### Prevention

- **Pilot ring discipline** — Token Protection (and any session-control policy in preview) ships only to a curated Edge-on-Windows-11 pilot ring (the Copilot Studio maker group on managed Windows 11 devices is a typical first ring).
- **Browser support matrix review** — added to the standing agenda of the monthly Authentication Policy Admin operations review.
- **Risk Register entry** — every preview-or-pilot CA control has a Risk Register entry that is closed only when the control is GA across the Microsoft-supported matrix and the firm's full population.
- See [Control 1.21 — Token Theft Detection](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) for the broader token-binding strategy and [Control 2.25 — Microsoft Agent 365 Admin Center](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) for the agent-management surfaces that benefit from Token Protection once the matrix is sufficient.

### Regulatory / Evidence Implications

- **No notification trigger** for a routine pilot rollback as long as the population can fall back to the standard CA + phishing-resistant MFA stack.
- **SOX evidence** — the change record (with rationale, support-matrix version, two-admin attestation) is a control-tuning artifact; preserve it per [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).
- If users were materially blocked from supervised customer-facing work for a meaningful duration, brief the FINRA Designated Supervisor; assess against §500.17(a) only if the firm's materiality threshold is crossed.

---

## §4 Service Principal Blocked by CA Workload Identities Policy on Scheduled Job

### Symptom

A scheduled batch — Logic App, Function App, Azure Automation runbook, custom Graph-calling agent, or third-party SaaS connector represented by a service principal (SP) — that ran successfully yesterday is now failing with `AADSTS53003` ("Access has been blocked by Conditional Access policies"). The SP owner reports the failure showed up immediately after a CA Workload Identities policy was promoted last night. **Critical detail:** the SP sign-in does **not** appear in `SigninLogs` — it appears in `AADServicePrincipalSignInLogs`.

### Likely Cause (frequency-ordered)

1. **CA Workload Identities policy now requires a named-location IP** for non-interactive SP sign-ins, and the SP egresses from an IP not yet on the allow-list (newly provisioned Function App, regional failover, partner SaaS IP rotation).
2. **The policy targets `All workload identities`** rather than a `Selected` set — see §14 for the related root cause.
3. **The SP authenticates with a client secret**, and the policy's grant control is now "Block" for client-secret SPs as part of a phishing-resistant migration to certificate-based or federated credentials.
4. **The SP is missing from the included scope** because the CA Workload Identities policy targets a curated `Approved-WorkloadIdentities` group and the SP was never added (governance gap).
5. **Workload Identities Premium SKU is not assigned**, so the policy authored successfully but is enforcing inconsistently — see §1.5 of the Pre-Escalation Checklist in the parent control documentation.

### Diagnostic Steps

**Portal path.**

1. **Entra → Monitoring → Sign-in logs → Service principal sign-ins** tab (NOT the Users tab). Filter to the SP `appId` and the failure window.
2. **Entra → Protection → Conditional Access → Policies**. Filter `Workload identities`. Inspect the policies that target the SP's `appId` directly or via group.
3. **Entra → Identity → Applications → Enterprise applications → {SP}**. Confirm the SP's `appId`, owner, and credentials (client secret vs certificate vs federated credential).

**KQL — use the correct table.**

```kusto
// Service principal sign-in failures — last 24h
AADServicePrincipalSignInLogs
| where TimeGenerated > ago(24h)
| where ServicePrincipalName == "<sp-display-name>" or ServicePrincipalId == "<sp-object-id>"
| where ResultType != 0
| project TimeGenerated, ServicePrincipalName, AppId, ResultType, ResultDescription, IPAddress, ConditionalAccessPolicies, ConditionalAccessStatus
| order by TimeGenerated desc
```

```kusto
// Which CA workload-identity policy fired? — last 24h
AADServicePrincipalSignInLogs
| where TimeGenerated > ago(24h) and ResultType != 0
| mv-expand policy = todynamic(ConditionalAccessPolicies)
| where tostring(policy.result) == "failure"
| summarize failures = count() by tostring(policy.displayName), ServicePrincipalName, IPAddress
| order by failures desc
```

```kusto
// Confirm Workload Identities Premium is enforcing — sample of "success" outcomes attributable to a workload-identity policy
AADServicePrincipalSignInLogs
| where TimeGenerated > ago(24h)
| mv-expand policy = todynamic(ConditionalAccessPolicies)
| where tostring(policy.displayName) startswith "WID-" and tostring(policy.result) == "success"
| summarize count() by tostring(policy.displayName)
```

> **Diagnostic anti-pattern.** Querying `SigninLogs` for an SP failure returns zero rows and creates the false impression "no event occurred". The `SigninLogs` table holds **user** interactive and non-interactive sign-ins; SP and managed-identity sign-ins are in `AADServicePrincipalSignInLogs` and `AADManagedIdentitySignInLogs`. Always check both when triaging a workload-identity issue.

### Resolution

> **Change-control gate.** Modifying a CA Workload Identities policy is a tenant-wide change. Two-admin co-sign required. The change record must include the SP inventory snapshot, the named-locations diff, and the Workload Identities Premium SKU verification.

1. **If the named-location is the cause**: add the SP's egress IP to the `Trusted-WorkloadEgress` named location after Networking confirms the IP is genuinely owned by the workload (not a shared NAT pool with end-user traffic). Re-test.
2. **If the SP is missing from the included scope**: add the SP to the `Approved-WorkloadIdentities` group via change record; the SP's owner must attest in writing to the SP's purpose, scope, and review cadence (Control 1.1 maker-attestation pattern adapted for SPs).
3. **If the cause is client-secret use under a "Block client-secret" policy**: migrate the SP to **certificate-based** or **federated** credentials. **Do not** add an MFA grant control to a workload identity — workload identities cannot perform interactive MFA. The correct remediation is credential migration, not MFA fallback.

   ```powershell
   # -WhatIf stub — migrate SP from secret to certificate auth
   $spId = "<sp-object-id>"
   Write-Host "WhatIf: would generate a new self-signed certificate, upload public key as a keyCredential on SP $spId, store private key in the workload's Key Vault, and remove the existing passwordCredential after successful test."
   # Implementation: New-MgServicePrincipalKey ... ; followed by Remove-MgServicePrincipalPassword after cutover validation.
   ```

4. **If Workload Identities Premium is not assigned**: open a license ticket; until the SKU is assigned, document the SP-side risk in the Risk Register and constrain the SP via narrow Graph permissions and a Sentinel detection rule (see §15 compensating controls).

### Prevention

- **Workload Identities Premium SKU** in place tenant-wide before any CA Workload Identities policy is authored.
- **Selected-not-All targeting** — every CA Workload Identities policy targets `Selected service principals` from a curated approved-list group, never `All workload identities` (see §14).
- **Credential standards** — the firm's identity standards prohibit new SPs with client-secret auth in production; certificate or federated credentials are the standard. Existing client-secret SPs are tracked in the Risk Register with a remediation deadline.
- **Named-location lifecycle for workload egress** — Networking owns a separate `Trusted-WorkloadEgress` named location distinct from end-user egress; refresh quarterly.
- See [Control 2.6 — Identity Lifecycle Management](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) for the SP / workload-identity inventory and [Control 2.14 — Privileged Identity Management](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) for the privileged SP review cadence.

### Regulatory / Evidence Implications

- **SOX ITGC** — A scheduled job that fails because of a CA change is a change-control evidence trail. Preserve the change record, the SP sign-in audit, and the remediation diff.
- **NYDFS §500.17(a)** — A scheduled job failure does **not** by itself constitute a §500.17(a) reportable event. **However**, if the SP is part of a SOX-significant or customer-facing workflow and the outage crosses the firm's materiality threshold, run the Q1–Q7 reportability tree (parent control documentation §1.2). The 72-hour clock starts at the determination of reportability, not at first detection.
- **GLBA Safeguards** — If the SP accesses customer NPI on the firm's behalf (e.g., a Logic App that processes account statements), an unplanned outage is an availability incident; document and brief Compliance.

---

## §5 Break-Glass Account Lockout or Failed Quarterly Test

### Symptom

A scheduled quarterly break-glass (BG) test fails with one of:

- "Sign-in blocked by Conditional Access policy" (the BG account was inadvertently included in a tenant-wide CA policy by a recent group change).
- "Phishing-resistant authentication required, no methods registered" (a registered FIDO2 key has been lost, never registered, or removed by a policy change).
- "Account locked" (Smart Lockout fired after a failed-attempt sequence by the test runner).
- The BG account simply does not appear in the directory (deleted or moved).

Or — worse — a live SEV-1 is in flight and the BG account cannot be invoked to recover the tenant.

### Likely Cause (frequency-ordered)

1. **Group-membership drift** added the BG account to an `All Users` dynamic group, and a tenant-wide CA policy now applies to it.
2. **Authentication Methods Policy change** removed FIDO2 from the BG account's effective scope (e.g., a group-targeted FIDO2-only policy excluded the BG group).
3. **Smart Lockout** triggered by a failed sign-in sequence (the test runner mistyped the password or used the wrong key).
4. **The FIDO2 key is not in the safe** (chain-of-custody breach, key returned for re-issuance and not yet replaced).
5. **The BG account's credentials have aged out** beyond the firm's password rotation policy and the planned rotation was missed.

### Diagnostic Steps

**Portal path.**

1. **Entra → Users → {BG account}** — confirm it exists, is enabled, and has a registered FIDO2 method (Authentication methods tab).
2. **Entra → Sign-in logs** — pull the BG account's sign-in attempts for the test window; confirm `ResultType` and `ConditionalAccessStatus`.
3. **Entra → Protection → Conditional Access → Policies** — for each policy, confirm the BG account (and its containing exclusion group) is in the Exclude scope.
4. Physical safe inspection — the FIDO2 key is in the safe; the safe access log shows the expected custodians.

**KQL.**

```kusto
// Break-glass account sign-in attempts — last 90d (covers quarterly test windows)
SigninLogs
| where TimeGenerated > ago(90d)
| where UserPrincipalName in ("breakglass-1@contoso.onmicrosoft.com","breakglass-2@contoso.onmicrosoft.com")
| project TimeGenerated, UserPrincipalName, ResultType, ResultDescription, ConditionalAccessStatus, IPAddress, AppDisplayName, AuthenticationDetails
| order by TimeGenerated desc
```

```kusto
// Which CA policies currently include OR fail to exclude the BG account?
// Run as a Graph script and join with policy export — see PowerShell Setup §6.4
```

### Resolution

> **!!! danger Break-Glass Discipline applies.** Read the §0 admonition before invoking a BG account. Two-person rule (CISO delegate + Authentication Policy Admin) is mandatory.

1. **Quarterly test failure (no live incident).** Diagnose the cause from the diagnostic steps; fix the underlying drift (remove BG from the offending group; restore Exclude membership; re-register FIDO2 if the key is verifiably present). Restart the quarterly test schedule.
2. **Smart Lockout.** Wait the lockout window (default 60 seconds escalating); do not brute-force-clear via password reset, which itself is a CA-evaluated event. Document the lockout cause; if test-runner error, retrain.
3. **Key not in safe.** Treat as a chain-of-custody incident: open a SEV-2 to the CISO; do not attempt to provision a replacement key without CISO and Authentication Policy Admin co-sign. Replace BG account if necessary (parent control §2.3 BG replacement runbook).
4. **Live SEV-1 BG invocation.** Sign in only with the registered FIDO2 key from the safe; perform the **minimum** necessary remediation (typically: PATCH a single CA policy to `disabled` or restore an exclusion-group membership). Do not browse, do not change unrelated state. Sign out. The Sentinel rule `BreakGlassUsedOutsideTest` will fire; the CISO must acknowledge within 30 minutes.

```powershell
# -WhatIf stub — minimum-necessary remediation pattern (BG context)
$polId = "{offending-policy-guid}"
$current = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/$polId"
Write-Host "WhatIf: would PATCH policy '$($current.displayName)' state to 'disabled'. BG context: minimum-necessary, two-person attestation required, SHA-256 hash of pre-change policy state captured."
# Apply only with both CISO delegate and Authentication Policy Admin attestation in the incident record.
```

### Prevention

- **BG-exclusion group** named `CA-Exclude-BreakGlass` containing both BG accounts; **every** CA policy in the tenant references this group in Exclude. Sentinel rule alerts on any change to the group.
- **Dynamic-group rule lint** — the Authentication Policy Admin reviews every dynamic-membership rule monthly to ensure no rule resolves to include a BG account.
- **Quarterly test calendar** — calendared and owned by the CISO chief of staff; test failure is itself a SEV-3 ticket.
- **Safe access log** reviewed monthly by Internal Audit (independent of IT).
- **Two BG accounts** minimum, geographically separated keys.
- See [Control 2.14 — Privileged Identity Management](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) for the broader privileged-account hygiene and [Control 3.4 — Incident Reporting and RCA](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) for the post-use review pipeline.

### Regulatory / Evidence Implications

- **NYDFS §500.12 / §500.17** — BG accounts are an MFA-control architecture component; failure of the quarterly test is a §500.12 control deficiency to be documented in the Risk Register and the annual NYDFS Certificate of Compliance package. A live BG invocation may itself be reportable under §500.17(a) depending on the underlying incident; the 72-hour clock starts at the reportability determination.
- **FFIEC Authentication Guidance** — BG discipline is a long-standing FFIEC expectation; document the test history in the firm's authentication-control evidence binder.
- **SOX ITGC** — BG access is a high-risk privileged path; every BG use produces an evidence package per [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and feeds the post-incident review per [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).
- **FINRA Rule 3110 supervision** — if the BG was used to alter a policy affecting a supervised population, the FINRA Designated Supervisor must be briefed in the post-use review.

---

## §6 PIM Activation Fails with "Phishing-Resistant Required" on SMS-Registered Admin

### Symptom

A privileged user attempts to activate an eligible PIM role (e.g., Privileged Role Admin, Application Admin, Power Platform Admin) and is blocked at the activation MFA prompt with "Your sign-in was successful but does not meet the criteria to access this resource. Please use a phishing-resistant authentication method." The user has only SMS or Authenticator app push registered — no FIDO2 key, no Windows Hello for Business credential, no certificate.

### Likely Cause (frequency-ordered)

1. **Onboarding gap** — the user was made PIM-eligible before completing the firm's phishing-resistant registration ceremony (joiner workflow defect).
2. **Authentication-method drift** — the user's FIDO2 key was unenrolled (lost, returned for re-issue, or removed by an Authentication Methods Policy change) and the user is unaware.
3. **Authentication Strength binding** on the PIM-activation CA policy was tightened from "MFA" to "Phishing-resistant MFA" without coordinated re-registration of the affected population.
4. **Conditional Access policy targeting** changed — the user is newly in scope of a tighter policy because of a group-membership change.

### Diagnostic Steps

**Portal path.**

1. **Entra → Users → {user} → Authentication methods.** Confirm registered methods. Phishing-resistant = FIDO2 security key, Windows Hello for Business, or certificate-based authentication.
2. **Entra → Protection → Authentication methods → Policies.** Confirm the user is in scope of a policy that **enables** FIDO2 (or WHfB / CBA) for them.
3. **Entra → Identity Governance → PIM → {role} → Settings.** Confirm the activation requires "Authentication context" `c1` (or whichever AC binds to phishing-resistant in your tenant).
4. **Entra → Protection → Conditional Access → Authentication contexts → c1 → bound policy.** Confirm the grant control is the named Authentication Strength `Phishing-resistant MFA`.

**KQL.**

```kusto
// Recent registration / unenrollment audit for this user
AuditLogs
| where TimeGenerated > ago(30d)
| where TargetResources has "<user-upn>"
| where Category == "UserManagement" or OperationName has "authentication method"
| project TimeGenerated, OperationName, InitiatedBy, TargetResources, Result, ResultReason
| order by TimeGenerated desc
```

```kusto
// PIM activation failures for this user
SigninLogs
| where TimeGenerated > ago(7d)
| where UserPrincipalName == "<user-upn>"
| where AppDisplayName == "Azure AD PIM" or ResourceDisplayName has "Privileged Identity"
| project TimeGenerated, ResultType, ResultDescription, AuthenticationRequirement, AuthenticationDetails, ConditionalAccessStatus
```

### Resolution

> **Do not** loosen the activation policy to "MFA" as a workaround. Loosening a phishing-resistant control to accommodate an under-registered user is a regression that produces an audit finding ([Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)) and may breach NYDFS §500.12 expectations. Resolve at the user's registration, not at the policy.

1. **Pre-elevation registration ceremony.** The user attends a witnessed FIDO2 registration session (in-person or attested video) per the parent control onboarding playbook (`portal-walkthrough.md` §4.5). Witness records the key serial number in the privileged-credential register.
2. **Suspend PIM eligibility** on any role the user holds until the registration is complete (preserves least-privilege posture). Re-enable post-registration via change record.
3. **If the cause was unintended Authentication Methods Policy drift**, restore the FIDO2 group-targeting and re-attest the user's registration. Sentinel rule should alert on Authentication Methods Policy changes (Control 3.9 detection bundle).

```powershell
# -WhatIf stub — suspend PIM eligibility pending re-registration
$userId = "<user-object-id>"; $roleDefId = "<role-template-id>"
Write-Host "WhatIf: would PATCH eligibilitySchedule for user $userId on role $roleDefId to set status='Removed', reason='Pending phishing-resistant re-registration', expiry=now+72h. Apply only after CISO delegate co-sign."
```

### Prevention

- **Joiner workflow gate.** No PIM eligibility is granted until the user's `strongAuthenticationMethodCount` (phishing-resistant) ≥ 1. Helper: `Test-Fsi-PhishingResistantCoverage` (PowerShell Setup §3.2) runs nightly against the privileged population.
- **Mover/leaver alignment.** Role-bearing internal transfers re-attest registration; offboarded users have FIDO2 keys collected and zeroed.
- **Quarterly registration audit** by Internal Audit covering 100% of privileged users.
- See [Control 2.14 — Privileged Identity Management](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) and [Control 2.6 — Identity Lifecycle Management](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md).

### Regulatory / Evidence Implications

- **NYDFS §500.12** — phishing-resistant MFA on privileged access is the post-2023-amendment expectation; under-registered privileged users are a control deficiency.
- **SOX ITGC** — PIM activation evidence is a quarterly control sample; preserve the activation log, the registration record, and the witness attestation.
- **FFIEC Authentication Guidance** — supports the elevated-risk-transactions assurance level requirement.

---

## §7 Privileged User Phishing-Resistant Method Count Drops to Zero

### Symptom

The nightly `Test-Fsi-PhishingResistantCoverage` helper (PowerShell Setup §3.2) reports a privileged user (PIM-eligible or PIM-active) whose count of registered phishing-resistant methods is zero. The user may not yet have attempted a sign-in that fails — this is a leading indicator caught by inventory, not a user-reported incident.

### Likely Cause (frequency-ordered)

1. **FIDO2 key removed by helpdesk** in response to a user "lost key" ticket, without provisioning a replacement first.
2. **Authentication Methods Policy change** group-excluded the user from FIDO2 (e.g., a remediation script ran with broad scope).
3. **WHfB credential invalidated** (TPM reset, device wipe, hardware replacement).
4. **Certificate expired** (CBA-registered users) and not yet renewed.

### Diagnostic Steps

```powershell
# Helper invocation — see PowerShell Setup §3.2 for full source
Test-Fsi-PhishingResistantCoverage -Scope PrivilegedOnly -OutputFormat Table |
  Where-Object { $_.PhishingResistantMethodCount -eq 0 }
```

```kusto
// What removed the method? — last 14d
AuditLogs
| where TimeGenerated > ago(14d)
| where TargetResources has "<user-upn>"
| where OperationName in ("Delete authentication method","Update authentication method","User registered security info")
| project TimeGenerated, OperationName, InitiatedBy.user.userPrincipalName, TargetResources, Result
| order by TimeGenerated desc
```

### Resolution

1. **Immediately suspend PIM eligibility** on the user's privileged roles (see §6 `-WhatIf` stub). Do not wait for the user to attempt activation and fail at the gate — suspend proactively.
2. **Schedule re-registration** within 72 hours; the user's privileged work is paused until completion. If business-critical, a peer with a registered key acts as the deputy via existing PIM eligibility (no role expansion).
3. **Root-cause the removal.** If a helpdesk script or an Authentication Methods Policy change caused mass removal, treat as a SEV-2 incident and brief the CISO; the change must be reviewed and the affected population re-attested.

### Prevention

- **Helpdesk runbook gate.** The "lost key" ticket cannot close until a replacement key is provisioned and the original is invalidated; the runbook enforces "provision before remove" sequencing.
- **Sentinel detection rule** `PrivilegedUserPhishingResistantCountZero` fires within 60 minutes of a method removal that drops a privileged user to zero (cross-ref [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)).
- **Monthly Internal Audit reconciliation** of the privileged-credential register against the live `Test-Fsi-PhishingResistantCoverage` output.

### Regulatory / Evidence Implications

- **NYDFS §500.12** — a privileged user without phishing-resistant credentials is a live control deficiency; document and remediate in the next reporting window.
- **SOX ITGC** — privileged-access evidence requires that every privileged user has a continuously-satisfied phishing-resistant credential; gaps must be remediated before the SOX testing window or noted as exceptions.
- **FINRA Rule 4511 (recordkeeping)** — preserve the helper's nightly output as evidence of monitoring.

---

## §8 Sentinel Conditional Access Insights Workbook Empty or Stale

### Symptom

The Sentinel **Conditional Access Insights and Reporting** workbook (or the firm's custom CA detection workbook) renders empty tiles, blank time-charts, or "no data" placeholders. Detection rules dependent on `SigninLogs` / `AADServicePrincipalSignInLogs` are not firing despite known sign-in failures observable in the Entra portal.

### Likely Cause (frequency-ordered)

1. **Diagnostic settings missing or partial** — the Entra tenant is not exporting `SignInLogs`, `NonInteractiveUserSignInLogs`, `ServicePrincipalSignInLogs`, `ManagedIdentitySignInLogs`, and `AuditLogs` to the workspace bound to the workbook.
2. **Workspace mismatch** — the workbook was authored against a Sentinel workspace different from the one currently receiving the diagnostic stream (common after a workspace migration).
3. **Ingestion lag** beyond the workbook's default time window (typically 5-15 minutes; sustained lag > 60 minutes indicates a connector health issue).
4. **Log Analytics retention dropped** below the workbook's default lookback (e.g., workbook queries 30 days, retention is 14).
5. **Workspace RBAC** — the user viewing the workbook lacks `Log Analytics Reader` on the workspace.

### Diagnostic Steps

**Portal path.**

1. **Entra → Monitoring → Diagnostic settings.** Confirm a setting exists exporting all five log categories above to the target workspace.
2. **Sentinel → Data connectors → Microsoft Entra ID.** Confirm "Connected" status and the last data received timestamp.
3. **Log Analytics workspace → Usage and estimated costs → Data retention.** Confirm retention ≥ workbook lookback.
4. **Workbook → Edit → check the workspace parameter** at the top of the workbook.

**KQL.**

```kusto
// Are sign-ins being ingested at all?
union SigninLogs, AADServicePrincipalSignInLogs, AADNonInteractiveUserSignInLogs, AADManagedIdentitySignInLogs
| where TimeGenerated > ago(2h)
| summarize Count = count(), LatestEvent = max(TimeGenerated) by Type
```

```kusto
// Lag check
SigninLogs
| where TimeGenerated > ago(1h)
| summarize MaxLag = max(ingestion_time() - TimeGenerated)
```

### Resolution

1. **Add the missing diagnostic setting** if absent. Export all five categories to the Sentinel-bound workspace.
2. **Re-bind the workbook** to the correct workspace via the workspace parameter.
3. **Increase retention** if the lookback exceeds retention.
4. **Grant `Log Analytics Reader`** to the consuming SOC analyst group.

> **Change-control gate.** Diagnostic-setting changes are tenant-wide; record under standard change control. No `-WhatIf` mutation here, but document the pre/post diagnostic-setting JSON in the change record.

### Prevention

- **Sentinel data-source health rule** — analytics rule `EntraDiagnosticIngestionGap` alerts when any of the five categories shows zero events in any 30-minute window.
- **Workspace-binding lint** — quarterly Internal Audit review confirms every CA-related workbook is bound to the production Sentinel workspace.
- See [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) and [Control 3.6 — Telemetry and Monitoring](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md).

### Regulatory / Evidence Implications

- **SEC Rule 17a-4(f) / FINRA 4511** — telemetry retention supports the recordkeeping floor; an ingestion gap that crosses a regulatory retention boundary is itself a finding.
- **NYDFS §500.06** — audit-trail completeness; document and remediate gaps.
- **SOX ITGC** — monitoring-control deficiencies require disclosure in the SOX 404 attestation.

---

## §9 Microsoft Agent 365 Admin Center Access Denied After CA Policy Flip

### Symptom

After promoting a CA policy that targets the `Microsoft Agent 365 Admin Center` (or a related agent-management surface) from report-only to enabled, the AI Administrator and AI Governance Lead receive "Access denied — your sign-in does not satisfy the conditional access policy" when attempting to open the admin center. Agent inventory and approval workflows are blocked.

### Likely Cause (frequency-ordered)

1. **Authentication context mismatch** — the new policy requires authentication context `c2` (or whichever AC binds agent-admin operations), but the AI Admin's sign-in did not surface the AC step-up because the Agent 365 admin-center app does not yet request the AC token.
2. **Group-scope error** — the policy targets `All users` or a group that excludes the AI Admin role assignees.
3. **Trusted-location requirement** added to the policy that the AI Admin's egress IP does not satisfy.
4. **Authentication Strength binding** is `Phishing-resistant MFA` and the AI Admin only has Authenticator-app push registered (parallel to §6 for PIM).

### Diagnostic Steps

1. **Entra → Sign-in logs → User sign-ins** filtered to the AI Admin and the agent-admin app. Inspect `AuthenticationContextClassReferences`, `ConditionalAccessStatus`, and the failing policy name.
2. **Entra → Conditional Access → Policies → {policy} → Insights and reporting.** Confirm the policy fired and the grant control denied.
3. **Cross-ref [Control 2.25 — Microsoft Agent 365 Admin Center](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)** for the supported sign-in flows of the admin center app and known limitations.

### Resolution

1. **If the AC is not surfaced by the app**, do not bind agent-admin to that AC; instead bind the policy directly to the app and require the Authentication Strength `Phishing-resistant MFA` as the grant control.
2. **If group-scope error**, expand the included group to cover the AI Admin role assignees, document under change control.
3. **If trusted-location**, add the AI Admin's known egress to the named-locations allow-list.
4. **If under-registered**, follow §6 pre-elevation registration ceremony.

```powershell
# -WhatIf — re-target the policy from AC to direct app binding
$polId = "<policy-guid>"
Write-Host "WhatIf: would PATCH policy $polId conditions.applications.includeApplications to ['<agent-admin-app-id>'] and remove conditions.applications.includeAuthenticationContextClassReferences. Two-admin co-sign required."
```

### Prevention

- **Stage every CA policy through report-only for ≥ 14 days** with the AI Admin role population in scope; review the "Would have blocked" tile before flipping (see §2).
- **Maintain a `CA-Stakeholder-AIAdmin` exclusion-aware test group** to validate every policy that touches agent-admin surfaces.
- See [Control 2.25 — Microsoft Agent 365 Admin Center](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) and [Control 2.26 — Agent Lifecycle Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md).

### Regulatory / Evidence Implications

- **FINRA Rule 3110** — agent supervision requires the AI Governance Lead and the FINRA Designated Supervisor to maintain admin access; an outage of this surface is a supervisory-control deficiency to be documented and remediated.
- **SOX ITGC** — agent-admin access controls are a SOX-significant change; preserve the change record and post-flip access verification.

---

## §10 Continuous Access Evaluation Not Propagating Revocations

### Symptom

A user is disabled (or a session is revoked, or a risky-user is detected and remediated) in Entra, but the user retains active sessions to Exchange Online, SharePoint Online, or Teams for minutes to hours after the revocation event. The expected near-real-time CAE behavior is not observed.

### Likely Cause (frequency-ordered)

1. **Client app is not CAE-aware** (older client version, third-party app using a non-CAE-compatible MSAL build).
2. **CAE is disabled** at the tenant or policy level (Entra → Security → Conditional Access → CAE settings).
3. **Network condition mismatch** — CAE relies on the resource provider being able to challenge the client; if the client is on a network the provider cannot reach back through, the revocation cannot be evaluated until token expiry.
4. **Known-issue window** — Microsoft has periodically published transient CAE propagation issues; check the Microsoft 365 admin center service health.

### Diagnostic Steps

1. **Entra → Sign-in logs → {user}** — inspect the `IsCaeToken` field on recent token issuance; confirm the resource accepted a CAE token.
2. **Entra → Security → Conditional Access → CAE settings.** Confirm enabled and scope.
3. **Microsoft 365 admin center → Service health.** Check for active CAE incidents.

### Resolution

1. **If client-app version**, mandate upgrade through Intune app-version compliance policies; track non-compliant device count.
2. **If CAE disabled**, enable per the tenant standard; record under change control.
3. **If known issue**, apply Microsoft's published mitigation; document the window.
4. **Hard fallback** for true emergencies: revoke the user's refresh tokens via `Revoke-MgUserSignInSession` and force a tenant-wide token-version rotation only with CISO co-sign.

### Prevention

- **CAE-readiness audit** quarterly across the top-20 client apps in the tenant.
- **Sentinel rule** `RevocationLagExceeded` alerts when a disabled user's last sign-in to a resource exceeds 15 minutes after the disable event.

### Regulatory / Evidence Implications

- **NYDFS §500.07 (access privileges)** — revocation latency is a known control characteristic; document the firm's tolerance and the compensating controls (token TTL, hard-revoke runbook).
- **SOX ITGC** — termination access removal evidence must show revocation within the firm's SLA; CAE lag that exceeds the SLA is a finding.

---

## §11 Conflicting Conditional Access Policies Producing Inconclusive or Contradictory Results

### Symptom

The CA What-If tool returns "Inconclusive" for a representative user/app/condition combination, or a user observes that two sign-ins under apparently identical conditions produce different outcomes (one allowed, one blocked). The Sign-in log shows multiple policies evaluating with mixed `success` / `failure` / `notApplied` results, and the effective grant control is unclear to the operator.

### Likely Cause (frequency-ordered)

1. **Policy proliferation** — the tenant holds dozens of CA policies authored over time, with overlapping include/exclude scopes; the cumulative grant evaluation is non-obvious.
2. **Both "Block" and "Grant" policies fire** — by Microsoft documented precedence, Block wins, but operator expectation differs.
3. **Authentication Strength conflict** — two policies require different Authentication Strengths; the user's available methods satisfy one but not the other.
4. **Session controls overlap** — sign-in frequency, persistent browser, and CAE settings differ across applicable policies.
5. **Group-membership churn** mid-evaluation (rare, but possible if a dynamic-group transition occurs between sign-in events).

### Diagnostic Steps

**Portal path.**

1. **Entra → Conditional Access → What-If.** Reproduce the exact user / app / IP / device / risk combination. Capture the JSON output.
2. **Entra → Sign-in logs → {event} → Conditional Access tab.** Enumerate every policy that evaluated and its result.
3. **Export all CA policies as JSON** via Graph and run the firm's CA-merge linter to identify overlap (PowerShell Setup §7).

**KQL.**

```kusto
SigninLogs
| where TimeGenerated > ago(7d)
| where UserPrincipalName == "<upn>" and AppDisplayName == "<app>"
| mv-expand pol = todynamic(ConditionalAccessPolicies)
| project TimeGenerated, ResultType, PolicyName = tostring(pol.displayName), PolicyResult = tostring(pol.result), GrantControls = tostring(pol.enforcedGrantControls)
| order by TimeGenerated desc
```

### Resolution

1. **Consolidate.** Merge overlapping policies into a single named policy per intent (one policy per business outcome). Decommission redundant policies under change control.
2. **Adopt named-policy taxonomy** — `BLOCK-*`, `GRANT-MFA-*`, `GRANT-PR-*` (phishing-resistant), `WID-*` (workload identities), `SESSION-*`. The taxonomy makes effective-control attribution self-documenting.
3. **Document precedence** in the firm's CA-policy register: Block always wins; among grants, the most restrictive Authentication Strength wins; session controls compound.

> **Change-control gate.** Policy merge / decommission is high-risk. Stage every consolidated policy through report-only ≥ 14 days before flipping (see §2). Two-admin co-sign required.

### Prevention

- **CA-policy register** maintained by the Authentication Policy Admin; every policy has an owner, intent statement, and review date.
- **Quarterly merge review** chaired by the AI Governance Lead with Internal Audit observation.
- **What-If smoke tests** automated in the CI pipeline for the firm's top-20 user/app combinations.

### Regulatory / Evidence Implications

- **SOX ITGC** — control documentation must be unambiguous; an inconclusive What-If result on a SOX-significant population is a documentation deficiency.
- **NYDFS §500.03** — written policy and procedure must reflect the actual control state; the CA-policy register is the evidentiary artifact.

---

## §12 Sovereign Cloud (GCC High / DoD) — Conditional Access for Workload Identities Unavailable

### Symptom

The firm operates in GCC High or DoD and attempts to author a CA Workload Identities policy to constrain agent service principals. The policy blade is unavailable, the Workload Identities Premium SKU does not appear in the license catalog, or the policy authors but does not enforce. Microsoft documentation indicates feature parity gaps for sovereign clouds.

### Likely Cause

1. **Product unavailability** — CA for Workload Identities (Workload Identities Premium) has historically had delayed or limited availability in GCC High and DoD. Verify current state in Microsoft sovereign-cloud feature parity documentation before designing the control.
2. **Tenant SKU mismatch** — even where the SKU exists, it may not be assigned to the sovereign tenant.

> **!!! warning Sovereign Cloud Availability.** As re-emphasized in §0, this playbook describes the commercial-cloud feature surface. Sovereign-cloud feature parity changes; verify against Microsoft's current GCC High / DoD parity matrix before designing or operating this control. The compensating controls below describe a defensible control posture where the native CA Workload Identities surface is unavailable.

### Diagnostic Steps

1. **Microsoft Learn** — sovereign-cloud feature parity documentation for Conditional Access and Workload Identities Premium.
2. **Entra (sovereign tenant) → Protection → Conditional Access → Policies → New policy → Workload identities** — confirm the option is or is not present.
3. **Microsoft 365 admin center → Billing → Licenses** — confirm SKU availability.

### Resolution / Compensating Controls

Where CA for Workload Identities is unavailable in the sovereign tenant, document the gap in the Risk Register and apply the following compensating controls:

1. **Stricter credential standards** — workload identities use certificate-based or federated credentials only; no client secrets in production.
2. **Narrowed Graph permissions** — every SP holds the minimum API permissions required; quarterly attestation by the SP owner.
3. **Sentinel detection coverage** — `AADServicePrincipalSignInLogs` analytics rules detect SP sign-ins from unexpected IPs, unusual API surfaces, or anomalous volumes (cross-ref [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)).
4. **Network egress constraint** — SPs running in the firm's Azure environment egress through a known IP range; partner SPs are constrained by an upstream firewall rule where feasible.
5. **Quarterly SP review** by the Authentication Policy Admin and AI Governance Lead per [Control 1.21 — Service Principal Management](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md).

### Prevention

- **Sovereign-cloud parity tracking** — the firm maintains a quarterly tracker of Microsoft sovereign-cloud feature parity for the controls in this framework; the AI Governance Lead reviews and updates the Risk Register accordingly.
- **No silent control assumption** — control narrative explicitly states which compensating controls substitute for the native control where parity is incomplete.

### Regulatory / Evidence Implications

- **NYDFS §500.03 / FFIEC** — control documentation must reflect actual implementation; do not document "CA for Workload Identities" as in place where the sovereign tenant lacks the feature. Document compensating controls explicitly.
- **DFARS / CMMC (DoD context)** — workload-identity governance is part of the access-control family; compensating-control evidence is mandatory.

---

## §13 Authentication Strengths UI Not Visible

### Symptom

The Authentication Policy Admin opens **Entra → Protection → Authentication methods → Authentication strengths** and the blade is missing, the "Phishing-resistant MFA" built-in strength is not visible, or attempts to bind a strength to a CA grant control fail with "feature not available".

### Likely Cause (frequency-ordered)

1. **License tier** — Authentication Strengths is an Entra ID Premium **P1** feature, but Workload Identities and some advanced bindings require **P2**. Verify the directory's license inventory.
2. **Directory role** — the user must hold `Authentication Policy Administrator` or higher; `Authentication Administrator` does not surface the strength-authoring UI.
3. **Tenant region / sovereign cloud** — see §12 for sovereign parity caveats.
4. **Browser cache / preview-feature flag** — clear cache; toggle the preview-features banner in the Entra portal.

### Diagnostic Steps

1. **Microsoft 365 admin center → Billing → Licenses** — confirm Entra ID P1 (and P2 for privileged scenarios) is assigned to the directory and to the admin attempting the operation.
2. **Entra → Roles and administrators → {admin user}** — confirm role assignment.
3. **Microsoft Learn** — current Authentication Strengths licensing and feature documentation.

### Resolution

1. **Assign appropriate license** to the directory and to the admin.
2. **Assign Authentication Policy Admin** role via PIM eligible assignment (not active) per [Control 2.14](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md).
3. **If sovereign-cloud limitation**, document under §12 compensating controls.

### Prevention

- **License-tier readiness check** in the firm's pre-deployment runbook for any control that depends on Authentication Strengths.
- **Role assignment via PIM only** — no permanent Authentication Policy Admin assignments.

### Regulatory / Evidence Implications

- **NYDFS §500.12** — phishing-resistant MFA expectation drives the Authentication Strengths feature dependency; license-tier gaps that prevent control implementation must be remediated and documented.

---

## §14 Managed Identity Blocked by Over-Broad CA Workload Identity Policy

### Symptom

A system-assigned or user-assigned managed identity (MI) attached to an Azure resource (App Service, Function App, VM, AKS pod with workload identity federation) fails to acquire a Graph or Azure ARM token after a CA Workload Identities policy is enabled. Logs in `AADManagedIdentitySignInLogs` show `ConditionalAccessStatus = failure`.

### Likely Cause

1. **Policy scope set to "All workload identities"** rather than "Selected service principals". Managed identities are workload identities; an `All` scope sweeps them in.
2. **No exclusion group for managed identities** — even with `Selected` scope, MIs may be included if the targeted group dynamically resolves to include them.
3. **Named-location requirement** — the MI's egress IP (Azure datacenter range) is not on the allow-list.

### Diagnostic Steps

```kusto
AADManagedIdentitySignInLogs
| where TimeGenerated > ago(24h)
| where ResultType != 0
| mv-expand pol = todynamic(ConditionalAccessPolicies)
| where tostring(pol.result) == "failure"
| project TimeGenerated, ServicePrincipalId, ServicePrincipalName, ResourceDisplayName, IPAddress, PolicyName = tostring(pol.displayName)
| order by TimeGenerated desc
```

Portal: **Entra → Conditional Access → {policy} → Conditions → Workload identities** — confirm scope.

### Resolution

1. **Re-scope the policy** from `All workload identities` to `Selected service principals` targeting only the curated `Approved-WorkloadIdentities` group. Add a documented exclusion for the `MI-Excluded` group containing managed identities not appropriate to govern via this control.

```powershell
# -WhatIf — re-scope policy to Selected with exclusion
$polId = "<policy-guid>"
Write-Host "WhatIf: would PATCH policy $polId conditions.clientApplications.includeServicePrincipals to ['<approved-wid-group-guid>'] and excludeServicePrincipals to ['<mi-excluded-group-guid>']. Two-admin co-sign required."
```

2. **For MIs that should be governed**, add to the included group with the SP-owner attestation pattern from §4.

### Prevention

- **Standing rule**: no CA Workload Identities policy uses `All workload identities` scope. The CA-policy register lints for this.
- **MI inventory** maintained as a tag-driven Azure Resource Graph query; reviewed quarterly with [Control 1.21](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md).

### Regulatory / Evidence Implications

- **SOX ITGC** — over-broad scope causing production outage is a change-control finding. Preserve the policy-state diff and the post-incident review.
- **NYDFS §500.07** — least-privilege scoping of access controls; an over-broad CA policy is the inverse of the least-privilege expectation.

---

## §15 Copilot Studio Publish Fails with "Conditional Access Required" Despite Registered Passkey

### Symptom

A maker registered with a FIDO2 passkey attempts to publish a Copilot Studio agent and receives a "conditional access required" or "session does not meet the criteria" error at the publish step, despite a successful interactive sign-in earlier in the session.

### Likely Cause (frequency-ordered)

1. **Sign-in frequency session control** on a CA policy targeting Copilot Studio has expired since the initial sign-in; the publish operation requires re-authentication.
2. **Token state stale** — browser cookie holds a non-CAE token; the publish API requires CAE-aware token issuance.
3. **Tenant Restrictions V2** is enforcing on the user's network egress and the Copilot Studio publish endpoint resolves through a path TR v2 does not allow.
4. **Authentication context** required for publish (e.g., `c3` for elevated-publish) is not surfaced by the Copilot Studio UI; the user signed in without satisfying the AC.
5. **Cross-ref [Control 1.1 — Tenant-Wide Foundation](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md)** for tenant-level authentication baselines that interact with this scenario.

### Diagnostic Steps

1. **Entra → Sign-in logs → {maker user} → filter by app `Power Virtual Agents` / `Copilot Studio`.** Inspect `AuthenticationContextClassReferences`, session-control evaluation, and the failing policy.
2. **Browser DevTools → Application → Cookies / Storage** — clear and re-sign-in to rule out stale token state.
3. **CA What-If** for the user / publish operation / current network conditions.

### Resolution

1. **If sign-in frequency expired**, prompt the user to re-authenticate; consider lengthening the frequency for the Copilot Studio app population if business-justified, with risk acceptance from the AI Governance Lead.
2. **If TR v2 interfering**, coordinate with Network to confirm the publish endpoint is allowlisted.
3. **If AC not surfaced**, do not bind publish to an AC the app does not request; bind directly to the app with an Authentication Strength grant control instead.

### Prevention

- **Document the publish-session profile** in the firm's Copilot Studio operations runbook (cross-ref `portal-walkthrough.md` §6).
- **Pre-publish session-state check** in the maker training material.

### Regulatory / Evidence Implications

- **FINRA Rule 3110** — agent publish is a supervised maker action; preserve the publish-attempt sign-in record alongside the publish approval ([Control 2.26 — Agent Lifecycle Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)).

---

## §16 Entra Agent ID Preview Service Principals Not Appearing in Conditional Access Targeting

### Symptom

An AI agent provisioned through the **Entra Agent ID** preview surface does not appear in the CA Workload Identities policy targeting picker. The Authentication Policy Admin cannot include the agent's identity in a CA policy and therefore cannot enforce phishing-resistant constraints (or any CA constraint) on the agent's runtime sign-ins.

> **!!! warning Scope Limit.** Entra Agent ID is a Microsoft preview surface. Feature behavior, naming, and CA integration are subject to change. Verify against current Microsoft Learn documentation before designing dependent controls. The guidance below describes a defensible interim posture; it does not constitute a permanent control architecture.

### Likely Cause

1. **Tenant opt-in not enabled** for the Entra Agent ID preview.
2. **Preview feature flag** off in the Entra portal preview-features pane.
3. **Identity surfaced as a non-SP object type** — preview Agent ID identities may be represented in a manner that is not yet a standard service-principal object the CA picker recognizes.
4. **Documentation lag** — the firm's runbooks were authored before a preview update changed the targeting model.

### Diagnostic Steps

1. **Microsoft Learn → Entra Agent ID** — confirm current preview state and CA integration documentation.
2. **Entra portal → preview features** — confirm tenant opt-in.
3. **Graph query** for the agent's directory object: confirm object type and `appId`.

### Resolution / Compensating Controls

1. **Engage Microsoft preview support** to confirm the current targeting model.
2. **Compensating controls** until native CA targeting is available:
   - Constrain the agent's Graph permissions to the minimum.
   - Apply a Sentinel detection rule on the agent's `appId` for anomalous sign-in volume / geography.
   - Document the gap in the Risk Register with a reassessment date tied to GA of the preview.
   - Defer onboarding any high-risk agent (Zone 3 Enterprise, Restricted data class) onto Entra Agent ID until CA integration is GA.
3. **Cross-ref [Control 1.9 — Agent Identity and Lifecycle](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)** and [Control 2.26 — Agent Lifecycle Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) for the broader agent-identity governance posture.

### Prevention

- **Preview-feature governance** — every preview feature adopted by the firm carries an entry in the preview-feature register with a re-evaluation date and compensating-controls statement.
- **Zone-gating** — preview identities are restricted to Zone 1 (Personal) and Zone 2 (Team) until native governance integration is GA.

### Regulatory / Evidence Implications

- **NYDFS §500.03** — written policy reflecting preview-feature limitations and compensating controls.
- **FINRA Rule 3110** — preview-feature governance and supervisor awareness; the FINRA Designated Supervisor must be briefed on any preview adoption that touches supervised functions.
- **SOX ITGC** — preview features in scope of SOX-significant workflows require an explicit risk acceptance and compensating-control documentation; the firm's external auditor should be apprised.

---

## Cross-References

This troubleshooting playbook intersects the following controls. Consult their dedicated playbooks when diagnosis indicates the root cause lies outside Control 1.11's scope.

- [Control 1.1 — Tenant-Wide Foundation and Zone Architecture](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md)
- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Control 1.9 — Agent Identity and Lifecycle](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)
- [Control 1.21 — Service Principal Management](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md)
- [Control 2.6 — Identity Lifecycle Management](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md)
- [Control 2.12 — Data Loss Prevention for Agents](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)
- [Control 2.14 — Privileged Identity Management](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md)
- [Control 2.25 — Microsoft Agent 365 Admin Center](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)
- [Control 2.26 — Agent Lifecycle Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)
- [Control 3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)
- [Control 3.6 — Agent Telemetry and Monitoring](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
- [Control 3.9 — Microsoft Sentinel Integration and SIEM](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
