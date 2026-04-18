# Control 1.11 — Troubleshooting & Incident Response Playbook

**Conditional Access and Phishing-Resistant MFA**

> **Scope.** This playbook is the canonical FSI troubleshooting and incident-response reference for Control 1.11. It covers identity-, Conditional Access (CA)-, MFA-, break-glass-, workload-identity-, and Entra Agent ID-related failure modes that affect Microsoft 365 AI agent operations (Copilot, Copilot Studio agents, Power Platform agent flows, custom Graph-calling apps). It is designed for use by Service Desk, SOC analysts, the Authentication Policy Administrator, the Entra Security Admin, the Entra Privileged Role Admin, the CISO, the Compliance Officer, and the FINRA Designated Supervisor.
>
> **Companion files.** [`portal-walkthrough.md`](portal-walkthrough.md) · [`powershell-setup.md`](powershell-setup.md) · [`verification-testing.md`](verification-testing.md) · [`conditional-access-agent-templates.md`](conditional-access-agent-templates.md). Parent control: [`1.11 Conditional Access and Phishing-Resistant MFA`](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md).
>
> **Authority.** Use this document together with the firm's enterprise incident-response runbook and with the related controls listed in §7. Where this playbook and the enterprise IR runbook differ procedurally, the enterprise IR runbook is authoritative for the overall lifecycle; this document is authoritative for identity- and CA-specific runbooks.
>
> **Hedged language.** Conditional Access, phishing-resistant MFA, break-glass discipline, and workload-identity controls **support compliance with**, **help meet**, and **are required for** the regulatory citations referenced. They do not by themselves guarantee any regulatory outcome. Implementation requires the SKUs, role separations, sponsor reviews, and annual exception approvals described below; organizations should verify each control end-to-end in their tenant before relying on it as evidence.

---

## 1. FSI Incident Handling

### 1.1 Severity Matrix

| Severity | Definition (identity / CA / MFA scope) | Auto-escalation triggers | Initial response SLA | Required notifications |
|----------|----------------------------------------|--------------------------|----------------------|------------------------|
| **SEV-1 — Critical** | Tenant-wide loss of authentication; mass CA lockout (>5% of workforce or any SOX in-scope app population); confirmed misuse of a break-glass (BG) account; service principal or workload identity confirmed bypassing CA in production; token-theft incident with confirmed lateral movement via stolen primary refresh token (PRT) or session cookie | Any of: BG sign-in outside of an authorized test window; >50 simultaneous CA-blocked sign-ins for SOX/FINRA-covered users in a 10-minute window; any SP sign-in to a Tier-0 resource without CA evaluation; Sentinel rule `BreakGlassUsedOutsideTest` fires; Agent ID risk = High on a Zone 3 production agent | **15 minutes** to acknowledge; **60 minutes** to first containment action | CISO, CCO, FINRA Designated Supervisor, SOC duty manager, Entra Global Admin on-call, Microsoft Premier/Unified TAM. Trigger Q1–Q7 reportability tree (§1.2) within 4 hours. |
| **SEV-2 — High** | Material degradation of identity controls; CA policy misconfiguration causing intermittent denial of service to a business-critical agent; phishing-resistant strength misapplied (e.g., synced passkey accepted in a Zone 3 grant control); PIM activation loop blocking privileged work; CAE not revoking sessions on a confirmed terminated user within 5 minutes | >100 unique users blocked from Copilot or a Zone 2/3 agent in a rolling hour; any auth-method policy change made outside the change window; Entra Agent ID workload identity sign-in failure rate >25% on a Zone 3 agent | **30 minutes** acknowledge; **4 hours** containment | Authentication Policy Administrator, Entra Security Admin, AI Governance Lead, app/agent owner, Service Desk lead |
| **SEV-3 — Moderate** | Single-user lockout that cannot be self-resolved; CA What-If shows unintended block on a non-critical app; one BG quarterly test failure (e.g., FIDO2 key not present in safe); Workload Identities Premium SKU shortfall discovered (CA WID author-time success but enforcement silently failing) | None automatic; routed via ticket | **4 business hours** acknowledge; **2 business days** resolution | Service Desk Tier 2, Authentication Policy Administrator |
| **SEV-4 — Low** | Cosmetic or single-user transient MFA prompt anomaly; Microsoft-managed CA policy informational notice (`Source = Microsoft`); user re-registration of a phishing-resistant credential after device replacement | None | **1 business day** acknowledge; **5 business days** resolution | Service Desk Tier 1 |

**Auto-escalation enforcement.** SEV-1 and SEV-2 triggers must be wired into Microsoft Sentinel analytic rules and a PagerDuty/ServiceNow on-call rotation; manual triage is not acceptable for these triggers under FFIEC and OCC Heightened Standards. See §6 for the Microsoft support pack.

### 1.2 Q1–Q7 Reportability Decision Tree

> **Apply this tree within 4 hours of any SEV-1 and within 24 hours of any SEV-2.** Document each answer in the incident record; the answers feed the regulator-notification clocks. This tree is verbatim from the FSI Agent Governance reportability standard and is identical across Controls 1.6, 1.11, 1.19, and 1.21.

**Q1 — Did the event involve unauthorized access to, or unauthorized acquisition of, customer information (NPI/PII) maintained by the firm or a third-party service provider acting on the firm's behalf?**
- **If YES:** Trigger **SEC Regulation S-P amended safeguards/disposal rule** customer-notification analysis. Notification of affected individuals required "as soon as practicable, but not later than 30 days" after the firm becomes aware that unauthorized access to or use of customer information has occurred or is reasonably likely to have occurred (effective compliance dates: large entities 12/3/2025; smaller entities 6/3/2026). Open the §1.6 customer-notification workstream.
- **If NO:** proceed to Q2.

**Q2 — Is the registrant a public company, and does the incident, including any series of related prior incidents, have a material impact (or reasonably likely material impact) on the registrant's financial condition or results of operations?**
- **If YES:** Trigger **SEC Form 8-K Item 1.05** materiality assessment. If material, file within **4 business days** of the materiality determination. Engage General Counsel and disclosure committee immediately; do not delay materiality determination unreasonably.
- **If NO or N/A:** proceed to Q3.

**Q3 — Does the firm operate in New York and is it a "Covered Entity" under 23 NYCRR Part 500 (NYDFS Cybersecurity Regulation)?**
- **If YES:** Apply **NYDFS §500.17(a)** notification — notify the Superintendent **as promptly as possible but in no event later than 72 hours** from the determination that a reportable cybersecurity event has occurred. Note that **§500.12 (multi-factor authentication for all individuals accessing any information system)** is fully effective **November 1, 2025**, and any §500.12 exception relied on in this incident must be documented in writing and approved annually by the CISO.
- **If NO:** proceed to Q4.

**Q4 — Is the firm a FINRA member, and does the event constitute a reportable matter under FINRA Rule 4530 (e.g., findings of violation, customer complaints meeting thresholds, or material associated-person events)?**
- **If YES:** File **FINRA Rule 4530** report within the applicable 30-day or quarterly statistical window; brief the **Designated Supervisor / Registered Principal**. Note that **SMS and voice OTP have been retired as acceptable MFA factors for FINRA-supervised authentication workflows since July 2025**; any SMS/voice fallback observed in the incident must be flagged as a control deficiency.
- **If NO or N/A:** proceed to Q5.

**Q5 — Does the firm hold customer information subject to GLBA, and does the event involve unauthorized access to "customer information" as defined under the FTC Safeguards Rule (16 CFR Part 314) or the equivalent rule of the firm's functional regulator?**
- **If YES:** Apply **FTC Safeguards Rule 16 CFR §314.4(j)** notification (notify FTC as soon as possible and no later than **30 days** after discovery of a notification event involving information of 500 or more consumers). Confirm the underlying MFA control (16 CFR §314.4(c)(5)) was in place; this is the operative MFA citation for non-banking financial institutions, **not** GLBA §501(b) directly. Engage Compliance Officer.
- **If NO:** proceed to Q6.

**Q6 — Was a model, AI agent, Copilot, or other automated decisioning system materially involved (as the affected resource, the propagation vector, or a decision-maker whose output was relied on)?**
- **If YES:** Apply **Federal Reserve SR 11-7 / OCC 2011-12 model risk management** — notify the model risk management (MRM) function, document the model/agent inventory entry, capture pre- and post-incident model behavior, and assess whether re-validation or decommissioning is required. For Entra Agent ID workload identities, capture the Agent ID risk snapshot at incident time.
- **If NO:** proceed to Q7.

**Q7 — Did the incident involve any step-down from NIST SP 800-63B Authentication Assurance Level 3 (AAL3) for a privileged action, a Tier-0 resource, or a SOX/FINRA in-scope workflow (for example, acceptance of a synced/cloud-backed passkey, fallback to SMS/voice, or temporary access pass used outside its approved window)?**
- **If YES:** Document the AAL3 step-down as a **control deficiency** in the SOX ITGC log and in the AI Risk Register; require CISO sign-off on the compensating control and a remediation deadline. Synced passkeys do **not** meet AAL3 (verifier-impersonation resistance + single-factor cryptographic device requirements); only device-bound FIDO2 authenticators and Windows Hello for Business with TPM-bound keys satisfy AAL3 in the Microsoft stack.
- **If NO:** Close the reportability tree with "no external notification triggered" and retain documentation per §1.3.

> **All seven answers**, the supporting evidence references, and the named decision-maker for each "YES" must be entered into the incident record within the SLA. The Q1–Q7 record is itself an SOX-evidence artifact and must be retained per §1.3.

### 1.3 Evidence Floor (13 mandatory artifacts)

All SEV-1 and SEV-2 incidents under Control 1.11 must capture **all 13** artifacts; SEV-3 must capture artifacts 1, 2, 3, 8, 13. Evidence is preserved under the firm's WORM (write-once-read-many) retention store with SHA-256 hash manifest; chain of custody is logged in the incident record.

| # | Artifact | Source | Retention | Notes |
|---|----------|--------|-----------|-------|
| 1 | **Incident clock** (UTC) — first detection, first containment, first eradication, recovery, closure | Incident record | 7 years (SOX) / 6 years (FINRA 4511) | Used for regulator notification clocks |
| 2 | **Sign-in logs (interactive + non-interactive + service-principal + managed-identity)** for affected users/SPs, JSON export | Entra ID → Sign-in logs; Graph `auditLogs/signIns` | 2 years live, 7 years archive (Storage/Sentinel) | Pull ±24h around incident; include `riskState`, `riskLevelAggregated`, `authenticationDetails`, `authenticationRequirementPolicies` |
| 3 | **Conditional Access policy export** (all policies, JSON) at incident time and pre-incident | Graph `identity/conditionalAccess/policies`; Microsoft-managed policies surface via filter `Source = Microsoft` (no top-level menu) | 7 years | Capture both production and report-only |
| 4 | **What-If analysis output** for the failing user/app/conditions | Entra portal → Conditional Access → What-If; or Graph `evaluate` API | 7 years | Run pre- and post-remediation |
| 5 | **User risk detail** and **sign-in risk detail** | Entra ID Protection → Risk detections | 90 days live (extend via Sentinel/Storage for 7 years) | Include `riskEventType`, `tokenIssuerType` |
| 6 | **Authentication-methods policy export** | Graph `policies/authenticationMethodsPolicy` | 7 years | Confirms which methods are enabled per group/zone |
| 7 | **FIDO2 / Windows Hello for Business registration state** for affected users | Graph `users/{id}/authentication/methods` | 7 years | Captures whether AAL3-eligible credentials were present |
| 8 | **PIM activation log** for the incident window | Entra → PIM → Audit history; Graph `roleManagement/directory/roleAssignmentScheduleRequests` | 7 years | Confirms admin role activations were JIT and approved |
| 9 | **Token / session revocation timestamps** (`revokeSignInSessions`, `invalidateAllRefreshTokens`) | Graph audit; PowerShell transcripts | 7 years | Required for token-theft incidents (cross-ref Control 1.21) |
| 10 | **Workload identity sign-in data** (Entra Workload ID Premium) | Workload Identities → Risky workload identities; Graph `identity/conditionalAccess/policies` filtered to SP/MI scope | 7 years | If Workload Identities Premium SKU is missing, record this as the evidence gap and a SEV-2 finding (CA for workload identities authors successfully but enforces silently / fails open without the SKU) |
| 11 | **Entra Agent ID risk snapshot** for any AI agent identity touched by the incident | Entra Agent ID portal; Graph (preview) | 7 years | Note: Entra Agent ID is staged across clouds (see §4) and is not yet at parity in GCC High / DoD |
| 12 | **Microsoft Sentinel incident export** (full incident JSON, all alerts, hunting queries used) | Sentinel → Incidents → Export | 7 years | Include the `BreakGlassUsedOutsideTest` rule output if applicable |
| 13 | **SHA-256 hash manifest** of all evidence files + WORM storage reference (Immutable Blob policy ID, retention lock expiry) | Storage account / Purview eDiscovery | 7 years | Chain-of-custody anchor |

> **Evidence-gap rule.** If any of the 13 artifacts cannot be produced, the incident record must explicitly name the missing artifact, the reason, and the CISO-approved compensating control. Missing artifacts 3, 4, 8, or 13 require a SOX deficiency entry.

### 1.4 Compensating Controls During Incident

If a CA policy or auth-method policy must be temporarily relaxed to restore service, the following compensating controls are mandatory:

- **Time-boxed exception.** Maximum 24 hours, single renewal up to 72 hours with CISO sign-off. Exception ID must be referenced in every related Graph audit log.
- **Scoped exception.** Use a CA policy *exclusion group* with named members only; never disable the policy globally. The exclusion group must be monitored by Sentinel rule `CA_Exclusion_Group_Membership_Change`.
- **Elevated logging.** Enable Entra ID diagnostic settings stream to Sentinel at `1m` interval; set Risky Sign-Ins workbook to alert on every event for the exception scope.
- **Phishing-resistant fallback.** Even during exception, the user must authenticate with a device-bound FIDO2 key or WHfB-TPM credential. Synced passkeys, SMS, voice, and email OTP are not acceptable fallbacks for Zone 3 or Tier-0 work.
- **Two-admin pattern.** Any CA, auth-method, or PIM-role configuration change made during the incident requires a second Entra Security Admin or CISO to co-sign in the change record. Single-admin changes during an active incident are themselves a SOX deficiency.
- **Break-glass discipline.** Do not use a BG account to "fix" a CA misconfiguration unless the standard admin path is fully blocked; if a BG is used, the quarterly test schedule restarts and a full BG post-use review (§2.3) is required.

### 1.5 Pre-Escalation Checklist

Before paging the CISO or filing a SEV-1, the on-call Authentication Policy Administrator must complete:

1. Confirm the incident is **reproducible** (not a single transient prompt) by re-running the user's sign-in scenario or executing a What-If with identical conditions.
2. Capture artifacts 1, 2, 3, 4, 8, 13 from §1.3 *before* making any remediation change.
3. Run the **two-admin verification**: a second admin independently confirms the diagnostic finding via Graph or portal.
4. Check the **Microsoft Service Health dashboard** and the Entra status page; if the symptom matches an active Microsoft incident, attach the tracking ID to the incident record and switch to "Microsoft-side incident" workflow (§6).
5. Run the **What-If analysis** for the affected user/app/conditions and attach the output (artifact 4); a CA change made without a What-If output attached is a documented anti-pattern (§3, AP-15).
6. Confirm whether the affected identity is a **human user, service principal, managed identity, or Entra Agent ID**; the runbook path differs (see §2).
7. Confirm whether **Workload Identities Premium** is licensed in the tenant (Entra → Licenses; or Graph `subscribedSkus` for `WORKLOAD_IDENTITIES_PREMIUM`). If absent and the incident involves an SP/MI/Agent identity, escalate immediately — CA workload-identity policies authored without the SKU enforce silently and a "configured" policy is not actually evaluated.
8. Confirm the **break-glass posture** before any CA tenant-wide change: both BG accounts present, both excluded from the policy being changed, both with FIDO2 key in the safe, last quarterly test ≤90 days old.

### 1.6 Communication & Escalation Tree

| Channel | Audience | Trigger | Owner | Cadence |
|---------|----------|---------|-------|---------|
| **Primary IR bridge** (Teams call + ServiceNow incident) | SOC, Authentication Policy Admin, Entra Security Admin, Service Desk lead | SEV-1 / SEV-2 declared | SOC duty manager | Continuous until containment |
| **Executive brief** (email + Teams) | CISO, CCO, CIO, General Counsel | SEV-1 declared; SEV-2 if customer-facing | CISO chief of staff | T+15min, T+1h, T+4h, then every 4h |
| **FINRA Designated Supervisor brief** | Designated Supervisor / Registered Principal | Any incident touching a FINRA-supervised workflow or supervised user | Compliance Officer | T+1h and at every state change |
| **Customer / employee comms hold** | Comms / IR comms lead | Any SEV-1 | General Counsel | Hold until materiality determination (Q2) and Reg S-P determination (Q1) complete |
| **Microsoft TAM / DSE** | Microsoft Premier/Unified TAM, Designated Support Engineer | SEV-1 always; SEV-2 if Microsoft-side suspected | Entra Global Admin on-call | Within 1h of SEV-1 declaration; see §6 |
| **Regulator clocks** | NYDFS Superintendent (72h), SEC (4 business days post-materiality), FINRA (30d / quarterly), FTC (30d), Reg S-P (30d) | Q1–Q7 outcomes | General Counsel / Compliance Officer | Per Q1–Q7 |
| **AI Governance Lead brief** | AI Governance Lead, agent owner | Any incident touching a Zone 2 or Zone 3 agent or Entra Agent ID | AI Governance Lead | T+1h |
| **Post-incident comms** | All staff (if applicable) | Per General Counsel | Comms lead | After containment + materiality determination |

### 1.7 SEV-1 Worked Example: Mass CA Lockout with Token-Theft Indicators

> **Scenario.** At 03:14 UTC, the Sentinel rule `MassCABlockedSignIns` fires: 312 unique users in the FINRA-supervised population are receiving CA block decisions on Microsoft 365 and Copilot in a 6-minute window. Concurrently, the `RiskySignIn_TokenIssuerAnomaly` rule fires for 7 of those users, indicating possible PRT replay from non-compliant devices. An overnight CA policy change ("Require compliant device for Office 365") was promoted to production at 03:09 UTC by a single admin without a documented What-If output and without a paired co-signer.

**T+0 (03:14 UTC) — Detection.** SOC analyst acknowledges the Sentinel incident. Severity auto-escalated to SEV-1 (>50 simultaneous CA-blocked sign-ins for FINRA-covered users in a 10-minute window per §1.1).

**T+5 (03:19 UTC) — Pre-escalation.** SOC pulls artifacts 1, 2, 3, 8 (§1.3). Confirms (a) the 03:09 CA policy change is the proximate cause; (b) the token-issuer anomalies are a separate concern requiring Control 1.21 token-theft runbook in parallel; (c) the change was single-admin (anti-pattern AP-13) with no What-If output (AP-15).

**T+15 (03:29 UTC) — Notifications.** CISO, CCO, FINRA Designated Supervisor, Microsoft Premier TAM paged. Executive brief #1 sent. IR bridge open. AI Governance Lead briefed because Copilot is in scope.

**T+30 (03:44 UTC) — Containment.** Two-admin pattern enforced: Entra Security Admin and on-call Entra Privileged Role Admin co-sign a rollback of the 03:09 policy via Graph `PATCH identity/conditionalAccess/policies/{id}` setting `state = "disabled"`. They do **not** delete the policy (forensic preservation). Mass sign-ins begin restoring at 03:46 UTC. The 7 token-anomaly users have their refresh tokens revoked (`revokeSignInSessions`) and are routed into the 1.21 runbook; their devices are quarantined via Intune.

**T+60 (04:14 UTC) — Eradication & Q1–Q7.** Authentication Policy Administrator opens Q1–Q7. Q1: under investigation pending forensic confirmation that no NPI was accessed by the 7 token-anomaly users — precautionary 30-day Reg S-P clock started. Q2: SEC 8-K materiality assessment opened with disclosure committee. Q3: NYDFS 72h clock started (firm is a Covered Entity). Q4: FINRA Designated Supervisor confirms no Rule 4530 trigger yet. Q5: GLBA/Safeguards clock started precautionary. Q6: Copilot was an affected resource — MRM notified, model behavior captured. Q7: AAL3 step-down — none observed (phishing-resistant strength held).

**T+4h (07:14 UTC) — Recovery.** Replacement CA policy authored with What-If attached, report-only mode for 24h, paired co-signer, BG accounts re-verified excluded, exclusion-group compensating control documented. Sentinel monitoring elevated.

**T+72h — Post-Incident Review.** PIR convened per §8. Findings: AP-13 (single-admin change), AP-15 (no What-If), AP-11 (no token-theft CA policy in place that would have detected the anomaly earlier). Remediations: enforce two-admin via PIM-approval workflow on all CA policy writes; require What-If output as a mandatory ServiceNow change-record attachment; deploy the token-theft CA policy from Control 1.21.

---

## 2. Failure-Mode Runbooks

Each runbook below uses the same six-block structure: **Symptoms · Likely Root Causes · Diagnostic Queries · Remediation · Validation · Evidence to Capture**. KQL queries assume Entra sign-in/audit logs are streamed to a Log Analytics workspace named `SecurityLogs`; substitute as needed. Graph queries use beta endpoints where preview features are required and are noted. PowerShell uses Microsoft Graph PowerShell SDK v2+.

### 2.1 User Lockout After CA Policy Promotion

**Symptoms.**

- One or more users receive `AADSTS53003` ("Access has been blocked by Conditional Access policies") after a recent CA policy promotion.
- Self-service password reset (SSPR) does not resolve the issue.
- Mobile and desktop Office clients show repeated CA prompts that loop without success.
- The user's last successful sign-in pre-dates the policy promotion timestamp.

**Likely root causes.**

1. The promoted policy targets `All users` without an `Exclude` clause for the BG accounts, an emergency-access exclusion group, or service accounts.
2. The policy requires a control the user cannot satisfy from the device they are using (e.g., compliant device on a personal device; phishing-resistant strength on a user without a registered FIDO2 key).
3. A grant control was set to `Require all the selected controls` when the intent was `Require one of the selected controls`.
4. The policy was authored against the wrong app (e.g., `Office 365` includes Copilot but excludes a custom Graph-calling agent that the user actually needs).
5. A named-location condition references an outdated IP range after a network change.

**Diagnostic queries.**

```kusto
// KQL — Identify CA-blocked sign-ins for a user in the last 2h
SigninLogs
| where TimeGenerated > ago(2h)
| where UserPrincipalName == "user@contoso.com"
| where ResultType in ("53003", "50158", "50097", "53000", "53002")
| project TimeGenerated, AppDisplayName, ConditionalAccessStatus, ConditionalAccessPolicies, AuthenticationRequirementPolicies, DeviceDetail, IPAddress, ResultType, ResultDescription
| order by TimeGenerated desc
```

```powershell
# Graph PowerShell — Pull the policies that fired and their failure reason
Connect-MgGraph -Scopes "AuditLog.Read.All","Policy.Read.All"
$signIns = Get-MgAuditLogSignIn -Filter "userPrincipalName eq 'user@contoso.com' and createdDateTime ge 2026-04-18T00:00:00Z" -Top 200
$signIns | Select-Object createdDateTime, appDisplayName, conditionalAccessStatus -ExpandProperty appliedConditionalAccessPolicies |
    Where-Object { $_.result -in @('failure','notApplied') } |
    Format-Table createdDateTime, displayName, result, conditionsSatisfied, conditionsNotSatisfied
```

> **Anti-pattern caution.** Do not use `-Top 100` and assume completeness. Sign-in volume routinely exceeds 100 events per user per hour; truncated audit pulls are documented anti-pattern AP-9 and have produced multiple false "no evidence" findings. Page through all results, or use the Graph batch endpoint with `$top=999` and follow `@odata.nextLink`.

```powershell
# What-If — Reproduce the block
# In portal: Entra → Security → Conditional Access → What-If
# Or via Graph beta evaluate API:
$body = @{
    signInIdentifier = "user@contoso.com"
    appId            = "<copilot-or-target-app-id>"
    clientAppType    = "browser"
    deviceInfo       = @{ isCompliant = $false; trustType = "AzureAD" }
    countryCode      = "US"
} | ConvertTo-Json -Depth 10
Invoke-MgGraphRequest -Method POST -Uri "https://graph.microsoft.com/beta/identity/conditionalAccess/evaluate" -Body $body
```

**Remediation.**

1. Two-admin pattern: a second Entra Security Admin or the Authentication Policy Administrator co-signs the change record.
2. If the policy is the proximate cause and rollback is appropriate, set `state = enabledForReportingButNotEnforced` (report-only) rather than `disabled`, so evidence collection continues.
3. If the user genuinely should be allowed, remediate the user-side gap (register a FIDO2 key; enroll the device in Intune; correct the named location). Do not add the user to a permanent exclusion group as a workaround — temporary exclusion groups are time-boxed per §1.4.
4. Re-promote the policy in **report-only** for 24–72 hours, attach the What-If output to the change record, then promote to enforce.

**Validation.**

1. Re-run the user's failing sign-in scenario; confirm `ConditionalAccessStatus = success`.
2. Run a fresh What-If against the same user/app/conditions; confirm `result = success` for the corrected configuration.
3. Confirm the policy now appears in the user's `appliedConditionalAccessPolicies` with `result = success`.
4. Confirm BG accounts remain excluded (run §2.9 BG verification subset).
5. Run the Sentinel hunting query `CA_Policy_Promotion_Lookback` for 24h; confirm no other users were collaterally affected.

**Evidence to capture.** Artifacts 1, 2, 3, 4 from §1.3, plus the change record, the paired-co-signer attestation, and the report-only evidence run.

### 2.2 Phishing-Resistant Strength Misconfigured (Synced Passkey Accepted in Zone 3)

**Symptoms.**

- A Zone 3 (Enterprise) agent or Tier-0 admin action is accessible after the user authenticated with a synced (cloud-backed) passkey on iCloud Keychain or Google Password Manager.
- The Authentication-Methods activity report shows `passkey (FIDO2)` for sign-ins that were expected to be device-bound only.
- Internal AAL3 attestation shows passing, but a SOX walkthrough auditor flags the synced credential.

**Likely root causes.**

1. The CA grant control specifies "Require authentication strength: Phishing-resistant MFA" but does **not** further constrain the allowed authenticators. Microsoft's built-in "Phishing-resistant MFA" strength accepts WHfB, FIDO2 security key, and certificate-based authentication — it does not by itself distinguish device-bound from synced passkeys.
2. The Authentication Methods Policy permits FIDO2 with `restrictForUsersFeatureSettings` not configured to enforce attestation or AAGUID allow-listing, so synced/cross-platform passkeys with provider AAGUIDs not on the firm's allow list are accepted.
3. WHfB key trust deployment (deprecating; Microsoft is transitioning to cloud Kerberos trust) has been carried forward and now coexists with synced passkeys without disambiguation.

**Diagnostic queries.**

```kusto
// KQL — Identify sign-ins that used a passkey credential to access a Zone 3 app
SigninLogs
| where TimeGenerated > ago(7d)
| where AppDisplayName in ("ContosoZone3Agent","Microsoft Graph PowerShell","Azure Portal")
| extend authMethods = tostring(AuthenticationDetails)
| where authMethods has "passkey" or authMethods has "FIDO"
| project TimeGenerated, UserPrincipalName, AppDisplayName, AuthenticationDetails, AuthenticationRequirementPolicies, DeviceDetail
```

```powershell
# Graph — Pull the authentication-methods policy and confirm FIDO2 attestation enforcement
$amp = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/beta/policies/authenticationMethodsPolicy/authenticationMethodConfigurations/Fido2"
$amp | ConvertTo-Json -Depth 10
# Look for: isAttestationEnforced = true; keyRestrictions.aaGuids includes only device-bound authenticator AAGUIDs; keyRestrictions.enforcementType = "allow"
```

```powershell
# Graph — Pull authentication-strength policies in use
Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/beta/policies/authenticationStrengthPolicies" |
    Select-Object -ExpandProperty value |
    Format-Table displayName, policyType, allowedCombinations
```

**Remediation.**

1. Author a **custom authentication strength** that lists only device-bound combinations (e.g., `fido2,windowsHelloForBusiness`) and, in the FIDO2 configuration, restrict `keyRestrictions.aaGuids` to a CISO-approved allow-list of device-bound authenticator AAGUIDs.
2. Update the relevant CA policy grant control to require the new custom strength rather than the built-in "Phishing-resistant MFA".
3. Set `Fido2.isAttestationEnforced = true`. Note: this requires authenticators that ship attestation; non-attesting passkey providers will be blocked.
4. Document the AAGUID allow-list in the AI Risk Register and re-review at least annually (or at any change in approved hardware).
5. For users who only have a synced passkey registered, drive a re-registration campaign to issue a device-bound credential before enforcement.

**Validation.**

1. Run a sign-in test using a synced passkey to a Zone 3 app — must be **denied** with `AADSTS53003` and a detail indicating the authenticator did not satisfy the required strength.
2. Run a sign-in test using a device-bound FIDO2 key — must succeed.
3. Confirm via the §1.3 artifact 6 export that the new strength is referenced in the relevant CA policies.
4. Document AAL3 conformance: only device-bound FIDO2 and WHfB-TPM credentials satisfy NIST 800-63B AAL3; synced passkeys do not. Update the SOX ITGC narrative.

**Evidence to capture.** Artifacts 2, 3, 4, 6, 7 from §1.3; AAGUID allow-list document; CISO sign-off on the custom strength.

### 2.3 Break-Glass Sign-In Alert (Genuine Use vs. False Positive)

**Symptoms.**

- Sentinel rule `BreakGlassUsedOutsideTest` fires.
- A sign-in event is observed for `breakglass1@contoso.onmicrosoft.com` or `breakglass2@contoso.onmicrosoft.com`.

**Likely root causes / decision tree.**

1. **Authorized quarterly test in progress** (most common) — confirm against the change calendar and the BG test runbook ticket.
2. **Genuine emergency use** — confirm the standard admin path was unavailable (e.g., Microsoft outage, mass admin lockout).
3. **Unauthorized use / credential compromise** — treat as SEV-1 immediately; the BG cleartext password and FIDO2 key are tightly held, so any unexpected use indicates either a process breakdown or a serious compromise.
4. **False positive** — the alert rule is keyed on UPN; confirm the sign-in is not a directory-read against the BG object by another service.

**Diagnostic queries.**

```kusto
SigninLogs
| where TimeGenerated > ago(24h)
| where UserPrincipalName in~ ("breakglass1@contoso.onmicrosoft.com","breakglass2@contoso.onmicrosoft.com")
| project TimeGenerated, UserPrincipalName, AppDisplayName, IPAddress, DeviceDetail, AuthenticationDetails, ResultType, ConditionalAccessStatus, CorrelationId
| order by TimeGenerated desc
```

```kusto
// Confirm the sign-in correlates to a directory-write or RBAC change
AuditLogs
| where TimeGenerated > ago(24h)
| where InitiatedBy.user.userPrincipalName in~ ("breakglass1@contoso.onmicrosoft.com","breakglass2@contoso.onmicrosoft.com")
| project TimeGenerated, OperationName, Category, TargetResources, Result, CorrelationId
```

**Remediation.**

- **If authorized test:** mark the Sentinel incident as confirmed-true-positive-test, attach the BG test runbook ticket, and close. Reset the 90-day quarterly clock from the test date. Confirm the alternating-quarterly pattern is honored (BG1 this quarter, BG2 next quarter). The two-BG-account pattern is mandatory; a single BG account is anti-pattern AP-5.
- **If genuine emergency:** allow the BG to perform the minimum necessary action under a recorded session (Teams meeting with screen recording, witnessed by a second admin). On completion: rotate the BG password, re-issue and re-store the FIDO2 key, restart the quarterly cadence, file a SEV-1 PIR per §8, and verify the BG remained excluded only from the policies it must be excluded from.
- **If unauthorized use:** declare SEV-1; treat as confirmed credential compromise. Immediately disable the BG account (yes, even though it is the BG — the second BG covers continuity), revoke all sessions, force credential rotation, engage forensic services, run Q1–Q7. Microsoft Premier/Unified TAM engaged within 1h.
- **If false positive (directory-read only):** tighten the Sentinel rule to filter on `AppDisplayName` or `Category` to exclude background reads.

**Validation.**

1. The other BG account remains usable (test it, in a witnessed session, immediately).
2. Both BG accounts remain excluded from the standard CA "block legacy auth" policy and from any "require compliant device" policies, but are **subject** to a dedicated CA policy that requires phishing-resistant MFA. (Excluding BGs from phishing-resistant strength is anti-pattern AP-6.)
3. FIDO2 keys for both BGs verified physically present in the safes.
4. Sentinel rule re-tested.

**Evidence to capture.** Artifacts 1, 2, 3, 6, 7, 8, 12, 13 from §1.3; safe-access log; witness attestation.

### 2.4 CA Policy Blocking a Critical Copilot or Agent App

**Symptoms.**

- Copilot for Microsoft 365 or a named Copilot Studio agent returns "Access blocked" or fails to load for a population of users.
- The affected app's service-principal sign-ins or the user-delegated sign-ins to the app show CA `failure`.

**Likely root causes.**

1. The CA policy targets `All cloud apps` with insufficient exclusions; the Copilot or agent app's resource ID was not excluded when an exception was needed.
2. The policy requires a control the agent context cannot satisfy (e.g., "Require app protection policy" applied to a desktop client that does not implement App Protection).
3. The policy uses a "client app" filter that excludes the agent's actual client app type (e.g., excludes "browser" while the agent is in fact accessed via browser).
4. A workload-identity (service principal) CA policy is incorrectly scoping the agent's underlying SP and Workload Identities Premium is licensed (so it actually enforces).

**Diagnostic queries.**

```kusto
SigninLogs
| where TimeGenerated > ago(4h)
| where AppDisplayName has "Copilot" or AppId == "<agent-app-id>"
| where ConditionalAccessStatus == "failure"
| summarize count() by tostring(ConditionalAccessPolicies), ResultType
```

```powershell
# Pull all CA policies that name this app or that target "all"
$policies = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies"
$policies.value | Where-Object {
    $_.conditions.applications.includeApplications -contains "<app-id>" -or
    $_.conditions.applications.includeApplications -contains "All"
} | Select-Object displayName, state, id
```

**Remediation.**

1. Run What-If for the affected user → app combination; confirm which policy is denying.
2. If the agent legitimately needs a relaxed control, author a **scoped** policy with the agent excluded from the broad policy, and a **dedicated** policy applying tightened controls suited to the agent (for example, require Sign-in risk = none and a compliant device, which most agents can satisfy).
3. Validate that the agent's Entra Agent ID identity is included in workload-identity policies if applicable.
4. Co-signed change; report-only for 24h; promote.

**Validation.** Re-run the failing scenario; the agent loads and operates normally; CA logs show `success` with the dedicated policy applied.

**Evidence to capture.** Artifacts 1, 2, 3, 4, 11 from §1.3.

### 2.5 Service Principal CA Bypass Discovered

**Symptoms.**

- A service principal or managed identity is observed accessing a Tier-0 resource without any CA policy listed in `appliedConditionalAccessPolicies`.
- Workload-identity policy authoring shows the policy as `enabled`, but the SP sign-ins do not reflect evaluation.
- A red-team exercise or external auditor flags an SP that should be subject to CA but is not.

**Likely root causes.**

1. **Workload Identities Premium SKU is not licensed in the tenant.** This is the single most common cause. The CA blade allows authoring of a workload-identity policy without the SKU; the policy saves and shows as enabled; but enforcement requires the SKU and **silently fails open** without it. Confirm via Graph `subscribedSkus`. (Anti-pattern AP-2.)
2. The SP is excluded from the policy via a stale exclusion left over from a migration.
3. The SP is a managed identity that the policy did not explicitly include (workload-identity policies require explicit inclusion of MIs in some scenarios).
4. The SP is a federated identity (workload identity federation) whose token issuer is not subject to the policy as authored.

**Diagnostic queries.**

```powershell
# Confirm Workload Identities Premium SKU
Connect-MgGraph -Scopes "Organization.Read.All"
Get-MgSubscribedSku | Where-Object { $_.SkuPartNumber -like "*WORKLOAD*" } |
    Select-Object SkuPartNumber, ConsumedUnits, @{n='Enabled';e={$_.PrepaidUnits.Enabled}}
# If no rows or zero enabled units: SKU absent. CA workload-identity policies are not enforcing.
```

```kusto
SigninLogs
| where TimeGenerated > ago(7d)
| where ServicePrincipalName == "<sp-name>" or ServicePrincipalId == "<sp-id>"
| project TimeGenerated, AppDisplayName, ResourceDisplayName, ConditionalAccessStatus, AuthenticationProtocol, IPAddress, ServicePrincipalCredentialKeyId
```

```powershell
# List workload-identity CA policies
$policies = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies"
$policies.value | Where-Object { $_.conditions.clientApplications -ne $null } |
    Select-Object displayName, state, @{n='Includes';e={$_.conditions.clientApplications.includeServicePrincipals}}, @{n='Excludes';e={$_.conditions.clientApplications.excludeServicePrincipals}}
```

**Remediation.**

1. **If SKU is missing:** declare a SEV-2 control deficiency. Procure Workload Identities Premium for the tenant (per-workload-identity SKU). Until SKU is in place, the documented workload-identity policies do not provide the assurance their authoring suggests; record this as a SOX deficiency and use compensating controls (network restrictions, certificate-based auth with short rotation, IP allow-listing).
2. **If exclusion is stale:** remove via two-admin co-signed change; report-only for 24h; promote.
3. **If MI not included:** explicitly add the MI's object ID to the policy `includeServicePrincipals`.
4. **If federated identity:** ensure the policy targets the correct workload-identity scope and that the federated credential's `subject` and `issuer` are accounted for.

**Validation.**

1. Re-run a representative SP sign-in; confirm `appliedConditionalAccessPolicies` now lists the policy.
2. Pull a 7-day backfill of SP sign-ins to confirm consistent enforcement.
3. Confirm the Workload Identities Premium consumed-unit count covers all in-scope SPs.

**Evidence to capture.** Artifacts 1, 2, 3, 10, 13 from §1.3; SKU procurement record; SOX deficiency log entry if applicable.

### 2.6 Entra Agent ID Risk Event = High

**Symptoms.**

- Entra Agent ID portal shows a Zone 3 production agent identity with `riskLevel = high`.
- The associated workload identity has anomalous sign-in patterns (e.g., new IP geolocation, atypical resource access pattern, or anomalous credential use).
- A Sentinel rule keyed to Entra Agent ID risk fires.

**Likely root causes.**

1. The agent's secret/credential has been exfiltrated (most serious).
2. The agent's calling pattern has legitimately changed (e.g., new tenant, new region) but the change was not pre-registered.
3. A misconfigured retry storm is producing anomalous sign-in volume.
4. An infrastructure change (new outbound proxy IP) is causing legitimate traffic to look anomalous.

**Diagnostic queries.**

```powershell
# Pull Entra Agent ID risky workload identity detail (preview Graph endpoint)
Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/beta/identityProtection/riskyServicePrincipals?`$filter=riskLevel eq 'high'" |
    Select-Object -ExpandProperty value |
    Format-Table id, displayName, riskLevel, riskState, riskLastUpdatedDateTime
```

```kusto
SigninLogs
| where TimeGenerated > ago(48h)
| where ServicePrincipalId == "<agent-sp-id>"
| summarize signIns = count(), countries = make_set(LocationDetails.countryOrRegion), ips = dcount(IPAddress) by bin(TimeGenerated, 1h)
| order by TimeGenerated desc
```

**Remediation.**

1. Immediately revoke the agent's current credentials (rotate client secret or roll federated credential); two-admin co-signed.
2. Engage the **Agent Sponsor** named on the agent's Entra ID Governance access package. Note: "Agent Sponsor" is the access-package owner role assigned via Entra ID Governance — it is **not** an Entra directory role and does not appear in the directory roles UI. Confirm the sponsor via Entra ID Governance → Access packages → Agent's package → Resource roles.
3. Quarantine the agent (set `accountEnabled = false` on the SP) until cause is established.
4. If cause is benign infrastructure change, register the new outbound IP range as a named location and retire the risk event with documented justification.
5. If cause is credential exfiltration, run Q1–Q7; this likely triggers Q6 (model/agent involvement) and possibly Q1 (NPI exposure depending on what the agent had access to).

**Validation.** Risk state returns to `confirmedSafe`; sign-in pattern normalizes; access-package recertification triggered.

**Evidence to capture.** Artifacts 1, 2, 3, 9, 10, 11, 12, 13 from §1.3; Agent Sponsor attestation; access package recertification record.

### 2.7 PIM Activation MFA Loop

**Symptoms.**

- Privileged user attempting to activate a PIM-eligible role is repeatedly prompted for MFA and the activation never completes.
- `AADSTS50076` or `AADSTS50079` codes appear in sign-in logs.
- The user can sign in to other apps successfully but cannot satisfy the PIM activation MFA challenge.

**Likely root causes.**

1. The PIM role activation requires phishing-resistant MFA (per Control 1.11 baseline), but the user has only registered an authenticator app or a synced passkey.
2. CAE has invalidated the user's session mid-activation, causing a re-prompt loop.
3. The user's device is non-compliant and a CA policy is gating the underlying admin app.
4. A WHfB key trust deployment is mid-migration and the user's credential is not currently usable for the PIM resource.
5. Permanent admin assignments exist in parallel and are masking the PIM workflow (anti-pattern AP-3 — permanent CA admin assignments).

**Diagnostic queries.**

```kusto
SigninLogs
| where TimeGenerated > ago(1h)
| where UserPrincipalName == "admin@contoso.com"
| where AppDisplayName has "Privileged Identity Management" or AppDisplayName has "Azure Portal"
| project TimeGenerated, AppDisplayName, ResultType, ResultDescription, AuthenticationDetails, ConditionalAccessStatus, AuthenticationRequirementPolicies
```

```powershell
# Pull the user's registered methods
Get-MgUserAuthenticationMethod -UserId "admin@contoso.com" | Format-Table AdditionalProperties
```

**Remediation.**

1. If the user lacks a device-bound FIDO2 key, drive immediate re-registration through a witnessed in-person process (or temporary access pass with strict TTL — and document AAL3 step-down per Q7).
2. If CAE is the cause, allow CAE to complete the revoke/re-issue cycle; the loop is normally self-resolving within 5 minutes. If not self-resolving, capture artifacts 2 and 9 and engage Microsoft.
3. Confirm there is no permanent admin assignment paralleling the PIM-eligible assignment; remove permanent assignments per Control 1.11 / 1.12 baseline.
4. If WHfB key trust migration is mid-flight, complete the cloud Kerberos trust migration; key trust is deprecating.

**Validation.** PIM activation completes within 60 seconds; the activation appears in PIM audit history with a successful MFA detail.

**Evidence to capture.** Artifacts 2, 6, 7, 8 from §1.3.

### 2.8 CAE Not Revoking Sessions on Terminated User

**Symptoms.**

- A user terminated in HR/Workday and disabled in Entra continues to access Microsoft 365 and a Zone 3 agent for >5 minutes after `accountEnabled = false`.
- Token revocation runs (`revokeSignInSessions`) but the user's existing session continues.

**Likely root causes.**

1. The accessed app is **not CAE-aware**, so session-state propagation depends on token expiry rather than near-real-time revocation. CAE coverage is not universal — Exchange, SharePoint, Teams, and Graph are CAE-aware; many third-party and custom apps are not.
2. CAE is enabled but the session is bound to a long-lived refresh token issued before account disablement.
3. The user is using a stale local cookie that the app does not validate against Entra on each call.
4. The signal (`accountEnabled = false`) was issued but `revokeSignInSessions` was not called explicitly.

**Diagnostic queries.**

```powershell
# Confirm revoke was issued
Invoke-MgGraphRequest -Method POST -Uri "https://graph.microsoft.com/v1.0/users/<id>/revokeSignInSessions"
# Confirm in audit
```

```kusto
AuditLogs
| where TimeGenerated > ago(2h)
| where TargetResources has "<user-id>"
| where OperationName in ("Update user","Disable account","Invalidate all refresh tokens of user","Revoke user sign-in sessions")
| project TimeGenerated, OperationName, InitiatedBy, Result, CorrelationId
```

```kusto
SigninLogs
| where TimeGenerated > ago(2h)
| where UserId == "<user-id>"
| project TimeGenerated, AppDisplayName, ResourceDisplayName, ResultType, ConditionalAccessStatus, IsContinuousAccessEvaluationCapable
```

**Remediation.**

1. Issue `revokeSignInSessions` and `invalidateAllRefreshTokens` explicitly on termination; do not rely on `accountEnabled = false` alone. Document this in the joiner-mover-leaver runbook (cross-ref Control 2.26).
2. For non-CAE-aware apps, layer a CA policy that requires a fresh sign-in frequency (e.g., 1 hour) for that app and accept the user-experience impact.
3. For Zone 3 agents, require CAE-aware app architecture as a Zone 3 onboarding gate (cross-ref Control 2.26 agent intake).
4. If a specific app is silently failing CAE despite advertised support, capture artifact 2 with `IsContinuousAccessEvaluationCapable` and open a Microsoft case (§6).

**Validation.** Re-test termination scenario end to end against the affected app; session terminates within 5 minutes.

**Evidence to capture.** Artifacts 1, 2, 9, 13 from §1.3; cross-link to the firm's token-theft / session-protection runbook for the CAE component.

### 2.9 Break-Glass Recovery from Total Tenant Lockout

**Symptoms.**

- All standard admin accounts are blocked from sign-in (typical cause: a CA policy promotion that inadvertently blocked admins).
- The Entra portal is accessible only via the BG account.

**Pre-conditions confirmed before BG use.**

1. Two BG accounts exist (`breakglass1`, `breakglass2`) — anti-pattern AP-5 if only one.
2. Both BGs are excluded from the policy that caused the lockout, but both are subject to a dedicated CA policy requiring phishing-resistant MFA — anti-pattern AP-6 if BG is excluded from phishing-resistant MFA entirely.
3. FIDO2 keys for both BGs are in their respective safes.
4. The standard admin path is genuinely unrecoverable (confirm with two admins).
5. Microsoft Premier/Unified TAM has been notified.

**Recovery procedure (witnessed, recorded).**

1. Open a Teams meeting with screen recording; minimum two admins present (one as "driver", one as "witness"). Compliance Officer joins for SOX evidence.
2. Retrieve `breakglass1` credentials and FIDO2 key from the safe; record safe-access in safe log; record retrieval timestamp in incident record.
3. Sign in as `breakglass1` to the Entra portal.
4. Identify the offending CA policy (use Sign-in logs and What-If as available).
5. Set the offending policy to `state = enabledForReportingButNotEnforced` (preserves forensics) — do not delete.
6. Re-test standard admin sign-in. Confirm restoration.
7. Sign out the BG account. **Immediately**: rotate the BG password; re-issue the FIDO2 key; return both to the safe under a new tamper-evident seal.
8. Restart the BG quarterly test cadence from today's date. Confirm `breakglass2` remains untouched and tested separately at the next quarterly window (alternating cadence).
9. File a SEV-1 PIR per §8.

**Validation.**

1. Standard admin path restored.
2. BG sign-in event correctly captured by Sentinel `BreakGlassUsedOutsideTest` (true positive).
3. Both BGs re-verified excluded only from policies they should be excluded from; both BGs subject to phishing-resistant MFA CA policy.
4. Both BGs tested for sign-in within 7 days post-incident (witnessed, recorded).
5. Quarterly cadence reset and on calendar.

**Evidence to capture.** All 13 artifacts from §1.3; safe-access log; meeting recording; witness attestations; password-rotation evidence; FIDO2 key serial-number change record.

---

## 3. Anti-Patterns

The following 18 anti-patterns are documented findings observed in FSI tenants and FSI auditor walkthroughs. Each anti-pattern is a SEV-2 or SEV-3 control deficiency unless otherwise noted.

| # | Anti-pattern | Why it fails | Correct pattern |
|---|--------------|--------------|-----------------|
| AP-1 | Relying on **SMS or voice OTP** as MFA for FINRA-supervised authentication | SMS/voice retired as acceptable MFA factors for FINRA-supervised authentication workflows since **July 2025**; insufficient under FTC Safeguards 16 CFR §314.4(c)(5) phishing-resistant guidance for sensitive systems | Device-bound FIDO2 / WHfB-TPM; Authenticator number-matching only as a transitional measure outside FINRA scope |
| AP-2 | Authoring **CA workload-identity policies without Workload Identities Premium SKU** | Author succeeds; the policy shows enabled; enforcement silently fails open. SP / MI traffic is not evaluated. | Confirm `WORKLOAD_IDENTITIES_PREMIUM` in `subscribedSkus` *before* authoring; treat absent SKU as a SEV-2 deficiency |
| AP-3 | **Permanent CA / Entra Security Admin assignments** | Eliminates JIT controls; expands blast radius of a compromised admin; violates Control 1.11 baseline | All admin assignments PIM-eligible; activation requires phishing-resistant MFA + approver |
| AP-4 | Accepting a **synced (cloud-backed) passkey** in Zone 3 grant controls | Synced passkeys do not satisfy NIST 800-63B AAL3 (verifier-impersonation resistance / single-factor cryptographic device). Built-in "Phishing-resistant MFA" strength accepts them. | Custom authentication strength with AAGUID allow-list of device-bound authenticators; `isAttestationEnforced = true` |
| AP-5 | **Single break-glass account** | Loss of the single BG (forgotten password, lost FIDO2 key) leaves the tenant unrecoverable; violates Microsoft and FSI guidance | Two BG accounts, alternating quarterly test cadence |
| AP-6 | **BG accounts excluded from phishing-resistant MFA entirely** | A BG with no MFA is a credential-theft trophy; the firm's strongest credential is reduced to a password | BGs excluded from policies that would block emergency use, but **subject** to a dedicated CA policy requiring phishing-resistant MFA |
| AP-7 | **No quarterly BG test** (or untested for >90 days) | The BG is the firm's continuity backstop; an untested BG is a presumption, not a control | Documented quarterly test, witnessed, alternating between BG1 and BG2; FIDO2 key physically verified each test |
| AP-8 | Treating **"Agent Sponsor" as an Entra directory role** | "Agent Sponsor" is an access-package owner role assigned via Entra ID Governance — it does not exist as a directory role. Searching for it in directory roles yields nothing and creates a false negative for governance audits. | Confirm Agent Sponsors via Entra ID Governance → Access packages → Resource roles |
| AP-9 | Truncated **`-Top 100`** audit query relied on for "no evidence" findings | Sign-in volume routinely exceeds 100 events per user per hour; the query truncates and returns false negatives | Page through with `@odata.nextLink`; use `$top=999`; for compliance pulls, export full window to Storage |
| AP-10 | Assuming **Microsoft-managed CA policies** appear in a top-level menu | They do not. They surface only via the filter `Source = Microsoft` on the Conditional Access policies blade | Always filter `Source = Microsoft` when reconciling the policy inventory |
| AP-11 | **No token-theft CA policy** in place | Token-theft attacks (PRT replay, session-cookie theft) bypass standard CA grant controls. Without a Risky Sign-In + token-protection CA policy, the firm has no defense in depth. | Deploy the token-theft policy from Control 1.21 (Risky Sign-In + sign-in frequency + compliant device + token protection) |
| AP-12 | Assumption that **CAE is operating** without verification | CAE coverage is not universal; many apps are not CAE-aware. Termination-revoke flows can take >1h on non-CAE-aware apps. | Verify per-app via `IsContinuousAccessEvaluationCapable` in sign-in logs; layer fresh sign-in frequency for non-CAE apps |
| AP-13 | **Single-admin CA / auth-method policy change** | No second pair of eyes; documented cause of multiple mass-lockout incidents; SOX deficiency | Two-admin pattern enforced via PIM approval workflow on every CA policy write |
| AP-14 | Continuing to deploy **WHfB key trust** after Microsoft deprecation announcement | Key trust is deprecating; new deployments accumulate technical debt and may break in future releases | Use cloud Kerberos trust for new WHfB deployments; plan migration off key trust |
| AP-15 | CA policy promoted to enforce **without a What-If output attached to the change record** | Author cannot demonstrate the change was modeled; collateral lockouts are common | Attach What-If output to every CA change record; report-only for 24–72h before enforce |
| AP-16 | **TPM-bound key not required** for FedRAMP-High tenants (GCC High / DoD) | FedRAMP-High requires hardware-bound credentials for privileged authentication; software-only or non-TPM-bound credentials fail the assessment | WHfB with TPM-bound key required; FIDO2 with attestation; verify via Graph `Fido2.keyRestrictions` and WHfB policy |
| AP-17 | **No Sentinel BG alert rule** | The firm has no automated detection of BG misuse; reliance on manual log review is not acceptable for SOX or NYDFS | Sentinel rule `BreakGlassUsedOutsideTest` deployed and tested |
| AP-18 | **NYDFS §500.12 exception relied on without annual CISO approval** | §500.12 requires written CISO approval annually for any MFA exception; relying on an exception without the documented approval is a §500.12 violation as of November 1, 2025 | Annual CISO-signed exception register; reviewed quarterly; flagged in Q3 of the reportability tree |

---

## 4. Sovereign Cloud & Entra Agent ID Matrix

| Capability | Commercial | GCC | GCC High | DoD |
|------------|-----------|-----|---------|-----|
| Conditional Access (user) | GA | GA | GA | GA |
| Conditional Access for workload identities | GA (requires Workload Identities Premium) | GA (requires SKU) | GA (requires SKU; verify SKU availability with TAM) | Verify with TAM; staged availability |
| Phishing-resistant MFA / authentication strengths | GA | GA | GA | GA |
| Custom authentication strengths | GA | GA | GA | GA |
| FIDO2 (device-bound, attested) | GA | GA | GA | GA |
| WHfB with cloud Kerberos trust | GA | GA | GA | GA |
| WHfB key trust | Deprecating | Deprecating | Deprecating | Deprecating |
| Continuous Access Evaluation (CAE) | GA across major M365 apps | GA | GA (parity lag may apply to specific apps; verify in tenant) | GA (parity lag may apply; verify) |
| PIM (Entra roles) | GA | GA | GA | GA |
| **Entra Agent ID** | GA / staged feature rollout | Staged | **Not at parity** — verify availability with Microsoft TAM | **Not at parity** — verify availability with Microsoft TAM |
| Microsoft-managed CA policies | GA (filter `Source = Microsoft`) | GA | Verify | Verify |
| Sentinel analytic rule templates for BG / token-theft | GA | GA | GA | GA |

> **GCC High / DoD note.** Entra Agent ID is staged across sovereign clouds and is not yet at parity in GCC High / DoD as of the Last UI Verified date on the parent control. Tenants in these clouds must use compensating workload-identity governance (per Control 1.10 and 2.8) until parity is achieved. Confirm current parity with the Microsoft TAM at incident time and record the answer in the incident evidence.

---

## 5. Escalation Path (L1 → L4)

| Level | Role(s) | Scope of authority | Engages when | Hand-off criteria |
|-------|---------|--------------------|--------------|-------------------|
| **L1 — Service Desk** | Service Desk Tier 1 / Tier 2 | Single-user MFA reset (within self-service guardrails); FIDO2 re-registration with witnessed identity proofing; documented FAQ resolutions | Single-user lockout; routine MFA prompt issue; credential reset request that does not touch CA policy or auth-method policy | Cannot resolve within 1 business hour; involves >1 user; touches a Zone 2/3 agent; touches a privileged user |
| **L2 — Authentication Policy Administrator** | Authentication Policy Administrator + a paired Entra Security Admin for any policy write | Authentication-methods policy reads/writes; CA policy reads; CA policy writes only with two-admin and What-If; user-side remediation for AAL3 alignment | Multi-user CA-related incident; auth-method policy questions; phishing-resistant strength misconfiguration; PIM activation MFA loop | SEV-1 declared; suspected workload-identity bypass; suspected token-theft; BG account event; need to change CA policy targeting >100 users |
| **L3 — Entra Security Admin / CISO** | Entra Security Admin, Entra Privileged Role Admin, CISO (or delegate) | All CA policy writes; workload-identity CA writes; BG account use approval; exception approvals (time-boxed); cross-control coordination with 1.6, 1.21 | SEV-1 declared; BG use; SP CA bypass discovered; mass-lockout in progress; Q1–Q7 reportability triggered | Materiality possibly triggered (Q2); regulator-notification clock starts; legal hold required |
| **L4 — General Counsel + CISO + CCO** | General Counsel, CISO, Chief Compliance Officer, FINRA Designated Supervisor (for FINRA-supervised matters) | Regulator notification decisions (NYDFS, SEC, FINRA, FTC, Reg S-P); customer-notification decisions; public disclosure (8-K); board notification | Q1–Q7 outcomes indicate any external notification or any material financial impact assessment | Closure or formal regulator submission |

> **Standing rule.** No L2/L3/L4 action that writes to CA, auth-method policy, BG configuration, or PIM role assignments may be performed by a single admin during an active incident. The two-admin pattern (AP-13 prevention) is enforced via PIM approval workflow on every write and recorded in the Graph audit log. Single-admin writes during an active incident are themselves a SOX deficiency.

---

## 6. Microsoft Support Pack

### 6.1 When to open a Microsoft case

| Trigger | Severity to request | Channel |
|---------|---------------------|---------|
| SEV-1 mass CA lockout suspected to be Microsoft-side | Sev A | Premier/Unified TAM phone + portal Sev A |
| BG misuse with confirmed compromise | Sev A | Premier/Unified TAM + Microsoft DART (Detection and Response Team) engagement |
| CA workload-identity policy authored but not enforcing despite SKU | Sev B | Portal Sev B + TAM follow-up |
| CAE not revoking on a CAE-advertised app | Sev B | Portal Sev B |
| Entra Agent ID risk event with insufficient detail | Sev B | TAM + Designated Support Engineer (DSE) if engaged |
| Microsoft-managed CA policy behavior question | Sev C | Portal Sev C |

### 6.2 Case template

```
Subject: [SEV-1] Mass Conditional Access denial — tenant <tenant-id> — incident <ID>

Tenant: <name> / <tenant-id>
Cloud: Commercial | GCC | GCC High | DoD
Incident clock (UTC): detection <ts>; first containment <ts>
Affected scope: <count> users; apps <list>; SP/MIs <list>
Suspected Microsoft component: Entra ID / Conditional Access / CAE / Entra Agent ID
Recent changes (last 7d): <list of CA, auth-method, PIM changes with timestamps and admins>
What-If output attached: yes/no (if no, explain)
Workload Identities Premium SKU present: yes/no (Get-MgSubscribedSku output attached)
BG posture: BG1/BG2 status, last quarterly test date
Sentinel incident: <link>
Evidence attached: artifacts <list> from §1.3
Contact: on-call Entra Global Admin <name> +1-555-…
Premier/Unified TAM informed: yes <name> at <ts>
```

### 6.3 What Microsoft Support can / cannot do

| Microsoft can | Microsoft cannot |
|---------------|------------------|
| Confirm Entra service health and active incidents | Diagnose your custom CA policy logic for you |
| Provide raw service-side telemetry under DSE arrangement | Modify your tenant's policies on your behalf |
| Assist with workload-identity SKU questions and licensing | Validate your AAL3 conformance — that is the firm's compliance responsibility |
| Engage DART for confirmed compromise with regulator implications | Make the regulator-notification determination (Q1–Q7) — that is the firm's General Counsel / Compliance Officer responsibility |
| Provide RCA for Microsoft-side incidents | Provide RCA for customer-side misconfiguration; they will document your config without remediating it |

### 6.4 Premier / Unified / DSE / CSAM contact paths

- **Premier/Unified TAM** — first call for any SEV-1; phone path is the documented escalation, not the portal
- **Designated Support Engineer (DSE)** — if engaged, looped in via TAM; provides deeper service-side telemetry
- **CSAM (Customer Success Account Manager)** — for licensing / SKU / Entra Agent ID parity questions, not for incident response
- **DART** — engaged via TAM for confirmed compromise with regulator implications (FINRA, SEC, NYDFS, FTC)

---

## 7. Cross-References

### 7.1 Related controls

- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — sign-in / audit log retention and Sentinel streaming relied on throughout this playbook
- [Control 1.18 — Application-Level Authorization and RBAC](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) — RBAC layer that complements CA grant controls
- [Control 1.23 — Step-Up Authentication for Agent Operations](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) — companion authentication-strength control for sensitive agent actions
- [Control 1.24 — Defender AI Security Posture Management](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) — posture and detections that surface CA / identity drift
- [Control 1.29 — Global Secure Access Network Controls](../../../controls/pillar-1-security/1.29-global-secure-access-network-controls.md) — network conditions referenced by named-location CA conditions
- [Control 2.5 — Testing, Validation, and Quality Assurance](../../../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) — pre-promotion validation discipline (mirrors the What-If / report-only requirement on every CA change)
- [Control 2.8 — Access Control and Segregation of Duties](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) — SoD requirement enforced via the two-admin pattern (AP-13) on every CA / auth-method / PIM write
- [Control 2.22 — Inactivity Timeout Enforcement](../../../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md) — application-level inactivity that complements CA session frequency
- [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) — agent provisioning, sponsorship (Agent Sponsor access package), and deprovisioning that underpins CA targeting and the Agent ID risk runbook (§2.6)
- [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — source of the `AgentZone` custom security attribute used by attribute-scoped agent CA policies
- [Control 3.8 — Copilot Hub and Governance Dashboard](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) — cross-platform CA enforcement visibility

### 7.2 Microsoft Learn anchors

- Entra Conditional Access overview and What-If — `learn.microsoft.com/entra/identity/conditional-access/overview` and `…/what-if-tool`
- Authentication strengths — `learn.microsoft.com/entra/identity/authentication/concept-authentication-strengths`
- FIDO2 authentication method and AAGUID restrictions — `learn.microsoft.com/entra/identity/authentication/concept-authentication-passwordless`
- Continuous Access Evaluation — `learn.microsoft.com/entra/identity/conditional-access/concept-continuous-access-evaluation`
- Workload identities and Conditional Access — `learn.microsoft.com/entra/workload-identities/workload-identities-overview`
- Entra Agent ID — `learn.microsoft.com/entra/architecture/agent-id` (preview surface; verify URL at incident time)
- Privileged Identity Management — `learn.microsoft.com/entra/id-governance/privileged-identity-management/pim-configure`
- Microsoft-managed Conditional Access policies — `learn.microsoft.com/entra/identity/conditional-access/managed-policies`

### 7.3 Regulatory anchors

- **SEC Regulation S-P** amended safeguards/disposal rule (customer notification — 30 days)
- **SEC Form 8-K Item 1.05** (cybersecurity incident disclosure — 4 business days post-materiality)
- **NYDFS 23 NYCRR Part 500** — §500.17 (72-hour notification); §500.12 (MFA, fully effective November 1, 2025)
- **FINRA Rule 4530** (reporting requirements); **FINRA Rule 4511** (record retention, 6 years)
- **FTC Safeguards Rule 16 CFR Part 314** — §314.4(c)(5) (MFA requirement, the operative MFA citation for non-banking financial institutions); §314.4(j) (notification — 30 days, 500+ consumers)
- **GLBA** — financial-privacy framework; the Safeguards Rule is the operative MFA citation, not §501(b) directly
- **Federal Reserve SR 11-7 / OCC 2011-12** — model risk management (apply to AI agents and Copilot when materially involved)
- **FFIEC IT Examination Handbook** — Information Security and Authentication / Access guidance
- **OCC Heightened Standards** (12 CFR Part 30 Appendix D) — risk governance and three-lines model
- **CFTC** — Regulation 1.31 (recordkeeping) and System Safeguards rules where applicable to swap dealers / FCMs
- **NIST SP 800-63B** — Authentication Assurance Level 3 (AAL3) — verifier-impersonation resistance, single-factor cryptographic device

### 7.4 Companion solutions

- `conditional-access-automation` — IaC templates and approval workflow for two-admin CA policy writes (`FSI-AgentGov-Solutions/identity/conditional-access-automation/`)
- `session-security-configurator` — Token-theft and CAE configuration solution (`FSI-AgentGov-Solutions/identity/session-security-configurator/`)
- `agent-365-lifecycle-governance` — End-to-end Entra Agent ID lifecycle including Agent Sponsor access-package wiring (`FSI-AgentGov-Solutions/agents/agent-365-lifecycle-governance/`)

See `docs/reference/solutions-index.md` for current versions and deployment notes.

---

## 8. Post-Incident Review (PIR) Template

Convene the PIR within **5 business days** of incident closure for SEV-1, **10 business days** for SEV-2. Attendees: incident commander, Authentication Policy Administrator, Entra Security Admin, CISO (or delegate), Compliance Officer, FINRA Designated Supervisor (if applicable), AI Governance Lead (if a Zone 2/3 agent was touched), General Counsel (if Q1–Q7 triggered any external notification).

### 8.1 PIR sections

1. **Incident summary** — one paragraph; what, when, scope, severity, regulator clocks triggered.
2. **Timeline** — UTC, every state change, with named decision-makers.
3. **Root-cause analysis (RCA)** — proximate cause, contributing causes, latent causes; map each to anti-patterns from §3.
4. **Detection effectiveness** — was the incident detected by automation, manual review, or external party? Time-to-detect.
5. **Response effectiveness** — time-to-acknowledge, time-to-contain, time-to-eradicate, time-to-recover; deviations from SLA.
6. **Evidence completeness** — were all 13 §1.3 artifacts captured? Document any gaps and the compensating attestation.
7. **Q1–Q7 reportability outcome** — each answer with named decision-maker; regulator-notification status.
8. **Anti-pattern findings** — list each AP from §3 that materialized; proposed remediation with owner and due date.
9. **Cross-control implications** — were Controls 1.7, 1.18, 1.23, 1.24, 2.5, 2.8, 2.22, 2.26, 3.1, 3.8 affected? File cross-control deficiencies.
10. **Sovereign-cloud notes** — if GCC/GCC High/DoD, did parity gaps contribute? Engage TAM for follow-up.
11. **Microsoft support outcome** — case IDs, RCA from Microsoft if applicable, DSE/DART involvement.
12. **Lessons learned and action items** — RACI, due dates, tracking ticket IDs; CISO sign-off.

### 8.2 Standing PIR questions (16)

1. Was the two-admin pattern enforced on every CA / auth-method / PIM write during the incident?
2. Was a What-If output attached to every CA change record?
3. Were both BG accounts confirmed present, tested ≤90 days, and excluded only from the policies they should be excluded from (and subject to phishing-resistant MFA)?
4. Was Workload Identities Premium SKU verified before relying on any workload-identity CA policy?
5. Did any sign-in accept a synced passkey for a Zone 3 or Tier-0 action? If yes, this is an AAL3 step-down (Q7).
6. Did any sign-in fall back to SMS or voice OTP? If yes for a FINRA-supervised user, this is an AP-1 finding.
7. Were Microsoft-managed CA policies reconciled via `Source = Microsoft`?
8. Was the audit-log pull paged through completely (no `-Top 100` truncation)?
9. Was CAE verified per affected app (not assumed)?
10. Was the token-theft CA policy in place? If not, file an AP-11 deficiency.
11. Were any permanent admin assignments observed parallel to PIM-eligible assignments? If yes, AP-3.
12. Was the "Agent Sponsor" relationship confirmed via Entra ID Governance access packages, not via directory roles?
13. Was a NYDFS §500.12 exception relied on? If yes, was the annual CISO approval current?
14. For GCC High / DoD, did Entra Agent ID parity gaps require compensating controls?
15. Was the Sentinel `BreakGlassUsedOutsideTest` rule deployed and did it fire correctly?
16. Was every Q1–Q7 answer recorded with a named decision-maker and supporting evidence reference?

### 8.3 12-month trend watch

After PIR closure, the AI Governance Lead and CISO maintain a 12-month rolling watch on:

- Volume and trend of CA-blocked sign-ins per week, by app and by user population.
- BG quarterly-test pass rate (target: 100%).
- Workload Identities Premium consumed-units coverage of in-scope SPs (target: 100%).
- AAL3-eligible credential coverage of the privileged user population (target: 100%).
- PIM activation success rate and median activation time.
- CAE revocation latency on terminated users (target: <5 minutes for CAE-aware apps).
- Synced-passkey acceptance rate in Zone 3 (target: 0).
- SMS/voice OTP acceptance for FINRA-supervised users (target: 0).
- Single-admin CA writes (target: 0).
- What-If attachment rate on CA change records (target: 100%).
- §500.12 exception count and annual-approval freshness (target: all current).
- Entra Agent ID risk events per quarter, by zone.

### 8.4 Annual control-effectiveness statement

The CISO issues an annual statement of effectiveness for Control 1.11 to the AI Governance Council and the Audit Committee. The statement covers: control objective status; the trend metrics in §8.3; material incidents and their root causes; anti-pattern recurrence; sovereign-cloud parity status (Entra Agent ID in particular); and any compensating controls relied on during the year. The statement supports — but does not by itself constitute — SOX management's assertion on ITGC effectiveness; SOX-specific evidence flows through Control 3.8.

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
