# Troubleshooting: Control 2.1 — Managed Environments

**Companion to:** [Control 2.1 — Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md)
**Sibling playbooks:** [Portal Walkthrough](./portal-walkthrough.md) · [PowerShell Setup](./powershell-setup.md) · [Verification & Testing](./verification-testing.md)
**Audience:** Power Platform Admin, Power Platform Service Admin, M365 Admin, AI Governance Lead, Purview Compliance Admin, Entra Global Reader, makers and environment owners encountering production issues.
**Scope:** Symptom-first diagnostic and remediation runbook for Managed Environments configuration drift, license-enforcement events, sharing-limit gaps, IP firewall failures, Customer Managed Key (CMK) recovery, tenant isolation exceptions, weekly digest interruptions, environment routing failures, pipeline targeting, inactive-resource detection lag, and SOX 404 IT-general-controls audit findings traceable to Managed Environment state. Aligns with FINRA Rule 4511 books-and-records, FINRA RN 24-09 / Rule 3110 (generative-AI supervision expectations), SEC Rule 17a-3/17a-4 retention, SOX §302 / §404 ITGC, GLBA Safeguards Rule §501(b), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) model risk management, NYDFS 23 NYCRR 500.06 audit trail, CFTC Regulation 1.31, and FFIEC IT examination handbook expectations.

!!! danger "Non-Substitution"
    The procedures in this playbook **support compliance with** the cited regulations; they do **not** substitute for the regulated firm's supervisory, recordkeeping, or model-risk obligations. Managed Environments is a tenant configuration surface that **aids in** the enforcement of governance policy. It does not by itself satisfy FINRA Rule 3110 supervisory review, SEC Rule 17a-4(f) WORM retention, OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) model validation, or GLBA §501(b) safeguarding obligations. Each remediation that mutates a Zone 3 (Enterprise) production environment **requires** prior change-management approval per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) and post-change evidence preservation per [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md). Organizations should verify each procedure in a non-production tenant before production execution and engage Legal / Compliance before altering any setting that has produced examiner-reviewable evidence within an active examination window.

!!! warning "June 2026 License Enforcement Rollout"
    Microsoft has communicated that beginning **June 2026**, end-user license-compliance notifications will progressively roll out to environments where Managed Environments is enabled but per-user / per-app premium license coverage is incomplete. **Pay-As-You-Go (PAYG) meter attachment does NOT satisfy the Managed Environments licensing floor** for the purposes of these notifications — only Power Apps Premium (per-user or per-app), Power Automate Premium, or Microsoft 365 / Dynamics 365 plans that include the relevant entitlement count. Firms that rely on PAYG to cover maker workloads in Zone 3 environments should treat Scenarios 9, 10, and 14 as in-scope priority work between April and June 2026. Consult the [Power Platform licensing guide](https://go.microsoft.com/fwlink/?linkid=2085130) for current SKU mapping and verify with your Microsoft account team before relying on any specific SKU as the compliance basis.

!!! warning "Customer Managed Key Exclusion — Welcome Content"
    The maker welcome content (custom logo, custom welcome message, support links) configured on a Managed Environment is **excluded from CMK encryption**. This content is stored in the Power Platform service-fabric metadata layer encrypted with Microsoft-managed keys, even when the environment's Dataverse data is CMK-encrypted. Do **not** place sensitive content (customer names, PII, internal-only URLs that disclose strategy, regulator-confidential numbers) in the welcome message. See Scenario 7 for diagnostics and Scenario 11 for remediation when sensitive content is discovered in the welcome panel.

---

## §0 How to Use This Playbook

This troubleshooting playbook is **symptom-first**. Each scenario follows the same six-part structure so on-call responders can move quickly under time pressure:

1. **Symptom** — the observable behavior reported by a maker, examiner, monitoring alert, or change-control deviation report.
2. **Likely Cause** — ranked hypotheses, most-probable first.
3. **Diagnostic Steps (Portal)** — click-paths in PPAC, M365 Admin Center, Entra Admin Center, or Azure portal.
4. **Diagnostic Steps (PowerShell)** — read-only inventory cmdlets that produce evidence-quality output (CSV + SHA-256 sidecar per the [PowerShell baseline](../../_shared/powershell-baseline.md)).
5. **Resolution** — remediation steps, including any change-management dependencies.
6. **Prevention** — control hardening to reduce recurrence.
7. **Regulatory-Evidence Implications** — what to preserve, what to disclose, and which regulator-facing artifact this scenario typically lands in.

### §0.1 Triage Tree (Symptom Index)

| # | Symptom (one-line) | Severity baseline |
|---|---|---|
| 1 | Managed Environments toggle reverts to Off after enable | Sev2 |
| 2 | "You don't have permission" when toggling ME from PPAC | Sev3 |
| 3 | `protectionLevel` returns blank or `Unknown` from PowerShell | Sev3 |
| 4 | Sharing-limit policy ignored — flow shared with 50 users | Sev2 |
| 5 | Solution checker blocks valid solution import | Sev3 |
| 6 | IP firewall lockout — admins cannot reach Dataverse | **Sev1** |
| 7 | Sensitive PII discovered in maker welcome content | Sev2 |
| 8 | Weekly maker digest not arriving Mondays | Sev3 |
| 9 | License-compliance banner appears for premium-licensed maker | Sev2 |
| 10 | Mass license-enforcement event after June 2026 rollout | **Sev1** |
| 11 | CMK key rotation fails / environment shows "Encryption pending" | **Sev1** |
| 12 | Tenant Isolation blocks legitimate vendor connector | Sev2 |
| 13 | Cross-tenant data movement detected from Managed Environment | **Sev1** |
| 14 | Pipelines deploy to Unmanaged target despite policy | Sev2 |
| 15 | Environment Routing sends new makers to wrong default | Sev3 |
| 16 | Inactive-resource cleanup deleted business-critical app | **Sev1** |
| 17 | Customer Lockbox approval request not appearing | Sev2 |
| 18 | Maker cannot create flow despite Premium license | Sev3 |
| 19 | Solution checker results not exporting / report empty | Sev3 |
| 20 | DLP exception requested for Managed Environment connector | Sev3 |
| 21 | ME enabled but usage insights show no data | Sev3 |
| 22 | Audit log gap during Managed Environments configuration window | **Sev1** |
| 23 | Drift between IaC (Terraform/Bicep) state and tenant reality | Sev2 |
| 24 | Examiner production request — full Managed Environments evidence package | Sev2 |

### §0.2 Severity Matrix

| Severity | Trigger | Response SLA | Evidence floor |
|---|---|---|---|
| **Sev1** | Managed Environments disabled tenant-wide; CMK irrecoverable on Zone 3; sharing-limit bypass with confirmed sensitive-data exposure; cross-tenant data movement during examiner-active window | Engage on-call within 15 min; AI Governance Lead within 30 min; Compliance + Legal within 1 hour | Mandatory pre-remediation snapshot per §0.4 |
| **Sev2** | Single Zone 3 environment lost Managed status; solution checker bypassed for in-scope solution; license-loss caused enforcement to fall away; IP firewall AuditOnly drift > 4 weeks | 2 business hours | Snapshot per §0.4 |
| **Sev3** | Setting drift on Zone 1/2 (e.g., sharing limit relaxed without ticket); usage-insight gap > 14 days; weekly digest gap | Next business day | Optional; document in change log |
| **Sev4** | False-positive solution-checker block; transient propagation delay; welcome-content typo | Standard hygiene | Internal only |

### §0.3 Pre-Escalation Checklist

Before paging on-call, the reporting Power Platform Admin must complete:

1. ☐ Tenant ID captured.
2. ☐ Environment GUID + DisplayName captured (do not use display name alone — multiple environments can share a name across regions).
3. ☐ Current `protectionLevel` value captured via `Get-AdminPowerAppEnvironment` (Standard = Managed; Basic = Unmanaged).
4. ☐ Reporter's role captured (Power Platform Admin / Power Platform Service Admin / Dynamics 365 Admin / Environment Admin / Maker).
5. ☐ Affected zone(s) identified (Zone 1 Personal / Zone 2 Team / Zone 3 Enterprise per [Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md)).
6. ☐ Examiner-active status checked (FINRA / SEC / OCC / Fed / state-regulator examination in flight). If yes, escalate immediately and **do not** mutate state until Legal acknowledges.
7. ☐ Initial evidence floor captured (PPAC screenshot with timestamp, PowerShell read-only inventory, Purview audit log slice).

### §0.4 Evidence Preservation Floor (BEFORE Remediation)

Every Sev1 and every Zone-3 Sev2 incident must produce the following bundle **before** any mutation:

| Artifact | Description | Source | Retention target |
|---|---|---|---|
| **E-01** | PPAC screenshot of the current Managed Environments panel (full viewport, timestamp visible) | Browser | 7 yr (SEC 17a-4) |
| **E-02** | PowerShell read-only inventory CSV + SHA-256 sidecar | `Get-AdminPowerAppEnvironment` (verification-testing playbook §3) | 7 yr |
| **E-03** | Purview audit log export covering the suspected window | `Search-UnifiedAuditLog -RecordType PowerAppsAdmin,PowerPlatformAdministratorActivity,MicrosoftFlow` | 7 yr |
| **E-04** | User reports / ServiceNow tickets that surfaced the issue | ITSM | 7 yr |
| **E-05** | Tenant ID, environment GUID, exact UTC timestamps | Captured per §0.3 | 7 yr |
| **E-06** | PowerShell session transcript (`Start-Transcript`) | On-call workstation | 7 yr |
| **E-07** | Change-management ticket reference (if any prior change correlates) | ServiceNow / Jira | 7 yr |
| **E-08** | Microsoft service-health correlation export (if applicable) | M365 Admin Center → Health | 7 yr |
| **E-09** | Chain-of-custody record (acquirer, host, hash, second-person review) | Manual | 7 yr |

Store under `Control-2.1/incidents/{YYYYMMDD-incident-id}/pre-remediation/`. Hash all artifacts. Document the chain of custody.

> **Hedged language reminder.** Snapshots **support** the firm's ability to reconstruct the supervisory state at a point in time; they do not by themselves satisfy retention obligations. The retention SLA depends on the firm's configured Purview retention label and immutability policy. Verify with the Purview Compliance Admin before relying on the snapshot for examiner production.

---

## §1 Diagnostic Data Collection

### §1.1 PowerShell module pinning

All inventory commands in this playbook require **`Microsoft.PowerApps.Administration.PowerShell`** pinned to a known-good version. As of April 2026 the recommended minimum is **2.0.190**. The module supports **Windows PowerShell 5.1** for the admin scenarios used here; PowerShell 7+ is **not** supported for these admin scenarios. See the [PowerShell baseline](../../_shared/powershell-baseline.md).

```powershell
# Run from an elevated Windows PowerShell 5.1 session
$ModuleVersion = '2.0.190'
if (-not (Get-Module -ListAvailable -Name Microsoft.PowerApps.Administration.PowerShell |
          Where-Object { $_.Version -ge [version]$ModuleVersion })) {
    Install-Module Microsoft.PowerApps.Administration.PowerShell `
        -RequiredVersion $ModuleVersion -Scope CurrentUser -Force -AllowClobber
}
Import-Module Microsoft.PowerApps.Administration.PowerShell -RequiredVersion $ModuleVersion

Add-PowerAppsAccount
```

### §1.2 Helper-cmdlet catalog (read-only)

| Helper | Purpose | Scenarios |
|---|---|---|
| `Get-Agt21Inventory` | Wraps `Get-AdminPowerAppEnvironment` and emits one row per environment with `protectionLevel`, region, Dataverse linkage, governance tags | All |
| `Get-Agt21SharingLimits` | Emits sharing-limit settings per environment (`SharingLimitPolicies`) | 4 |
| `Get-Agt21IpFirewall` | Emits IP firewall configuration + AuditOnly mode + rule count | 6 |
| `Get-Agt21CmkStatus` | Emits CMK key URI, Key Vault resource, last rotation, encryption status | 11 |
| `Get-Agt21TenantIsolation` | Emits inbound + outbound rules, default direction, exception list | 12, 13 |
| `Get-Agt21WeeklyDigest` | Emits last digest send timestamp + recipient count + bounce list | 8 |
| `Get-Agt21LicenseRollup` | Emits per-environment maker count + license SKU coverage matrix | 9, 10, 18 |
| `Get-Agt21SolutionChecker` | Emits solution-checker results for last 30 days | 5, 19 |
| `Get-Agt21AuditCorrelation` | Wraps Purview `Search-UnifiedAuditLog` with the standard ME RecordTypes | 22, 25 |
| `Get-Agt21Drift` | Diffs IaC desired state vs `Get-AdminPowerAppEnvironment` actual state | 24 |

The helper definitions are maintained in `scripts/control-2.1/Agt21-Helpers.ps1` and reviewed quarterly. All helpers are read-only by contract — they perform no `Set-*` or `New-*` calls.

```powershell
# Standard inventory call used at the top of nearly every scenario
$Inv = Get-Agt21Inventory -Cloud $Cloud |
        Sort-Object DisplayName
$Inv | Export-Csv ".\Agt21-Inv-$(Get-Date -Format yyyyMMddHHmm).csv" -NoTypeInformation
Get-FileHash ".\Agt21-Inv-$(Get-Date -Format yyyyMMddHHmm).csv" -Algorithm SHA256 |
    Out-File ".\Agt21-Inv-$(Get-Date -Format yyyyMMddHHmm).csv.sha256"
```

### §1.3 Microsoft Graph (read-only) reference queries

| ID | Purpose | Endpoint |
|---|---|---|
| **GQ-01** | Resolve Power Platform Admin role members | `GET /directoryRoles?$filter=displayName eq 'Power Platform Administrator'` then `/{id}/members` |
| **GQ-02** | Resolve Dynamics 365 Admin role members | `GET /directoryRoles?$filter=displayName eq 'Dynamics 365 Administrator'` then `/{id}/members` |
| **GQ-03** | Pull sign-in logs for a specific maker during incident window | `GET /auditLogs/signIns?$filter=userPrincipalName eq 'maker@contoso.com' and createdDateTime ge ...` |
| **GQ-04** | Service principals bound to Power Platform admin operations | `GET /servicePrincipals?$filter=appDisplayName eq 'Power Platform API'` |
| **GQ-05** | Conditional Access policies that scope `Power Platform` resource | `GET /identity/conditionalAccess/policies` (filter client-side on `conditions.applications.includeApplications`) |
| **GQ-06** | License assignments for a specific maker | `GET /users/{upn}/licenseDetails` |
| **GQ-07** | Group membership for environment-security-group enforcement | `GET /groups/{id}/members` |
| **GQ-08** | Privileged Identity Management (PIM) eligible vs active assignments | `GET /roleManagement/directory/roleAssignmentScheduleInstances` |

All Graph queries should be executed with a least-privilege app registration documented in the firm's Identity register, scoped to `Directory.Read.All`, `AuditLog.Read.All`, `Policy.Read.All`. Application secrets must be stored in Key Vault per [Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md).

### §1.4 KQL — Microsoft Sentinel / Purview Activity Explorer

```kql
// KQL-01 — Managed Environments setting changes (Purview audit log shipped to Sentinel)
OfficeActivity
| where TimeGenerated between (datetime(2026-04-01) .. datetime(2026-04-30))
| where RecordType in ("PowerAppsAdmin", "PowerPlatformAdministratorActivity")
| where Operation in ("UpdateEnvironment", "SetEnvironmentProtectionLevel",
                      "SetSharingLimits", "EnableTenantIsolation", "UpdateCmkKey")
| project TimeGenerated, UserId, Operation, ObjectId, ClientIP, RawJsonProperties=AdditionalDetails
| order by TimeGenerated desc
```

```kql
// KQL-02 — Sharing-limit bypass detection (admin sharing exceeds policy threshold)
OfficeActivity
| where RecordType == "MicrosoftFlow"
| where Operation == "ShareFlow"
| extend Recipients = todynamic(AdditionalDetails).recipientCount
| where Recipients > 50
| project TimeGenerated, UserId, ObjectId, Recipients, ClientIP
```

```kql
// KQL-03 — IP firewall rejection events
PowerPlatformAdminActivity
| where ActivityType == "DataverseConnectionRejected"
| where Reason has "IpFirewall"
| summarize Rejections=count() by SourceIp=ClientIp, EnvironmentId, bin(TimeGenerated, 1h)
| where Rejections > 5
```

```kql
// KQL-04 — Tenant Isolation cross-tenant attempts
PowerPlatformConnectorActivity
| where TenantIsolationDecision == "Blocked"
| project TimeGenerated, UserId, TargetTenant=PartnerTenantId,
          Connector=ConnectorName, EnvironmentId
| order by TimeGenerated desc
```

```kql
// KQL-05 — License compliance notification reception (post-June 2026)
EmailEvents
| where Subject has "Power Platform license"
| where RecipientEmailAddress endswith "@contoso.com"
| summarize Notifications=count() by RecipientEmailAddress, bin(TimeGenerated, 1d)
```

> **Caveat.** The KQL table names above assume Microsoft Sentinel ingestion of Office 365 Activity + Power Platform admin activity connectors. Firms using Purview Activity Explorer alone must use the equivalent Purview UI search expressions; firms using a third-party SIEM should map fields per their parser. Verify with the Sentinel admin before relying on these queries during examiner-active windows.

---

## §2 Scenarios

### Scenario 1 — Managed Environments toggle reverts to Off after enable

**Symptom.** A Power Platform Admin enables Managed Environments on a Zone 3 production environment from PPAC. The save action appears to succeed (toast confirmation visible). When the admin returns to the environment within 30–90 minutes, the panel shows Managed Environments **Off**. Other admins observing in parallel report the same regression.

**Likely Cause (ranked).**
1. A second tenant administrator (Power Platform Admin or Dynamics 365 Admin) reverted the change without coordinating — most common; check audit log first.
2. An Infrastructure-as-Code (IaC) reconciliation loop (Terraform, Bicep with `what-if` apply, GitHub Actions cron) is enforcing a desired-state of `protectionLevel = Basic`. The IaC pipeline has stale code that has not been updated to the new policy.
3. A Microsoft service-side propagation issue is rejecting the property write asynchronously — rare; correlate with M365 service health.
4. The environment lost its Dataverse linkage in the same window (Managed Environments requires Dataverse) — extremely rare absent an explicit delete.

**Diagnostic Steps (Portal).**
1. PPAC → **Environments** → select the affected environment → **Settings** → top-of-page chip should display "Managed Environment". Note the timestamp of the panel load.
2. PPAC → **Environments** → top toolbar → **Recent activity** (or **Audit history** under the environment's **History** blade if Dataverse-attached) → filter to the last 24 hours, Operation = `UpdateEnvironment` or `SetEnvironmentProtectionLevel`.
3. M365 Admin Center → **Health** → **Service health** → filter to **Power Platform** for the suspected window.
4. If IaC is suspected: check the source repository commit log for the `protectionLevel` declaration in the last 30 days.

**Diagnostic Steps (PowerShell).**
```powershell
$env = Get-AdminPowerAppEnvironment -EnvironmentName '<env-guid>'
$env.Properties.governanceConfiguration.protectionLevel    # Standard = ME enabled; Basic = disabled
$env.Properties.linkedEnvironmentMetadata.instanceUrl      # Dataverse linkage present?

# Pull recent admin events scoped to the environment
Search-UnifiedAuditLog -StartDate (Get-Date).AddHours(-48) -EndDate (Get-Date) `
    -RecordType PowerAppsAdmin,PowerPlatformAdministratorActivity `
    -ObjectIds '<env-guid>' |
    Select-Object CreationDate, UserIds, Operations, AuditData |
    Export-Csv ".\Agt21-Sc1-AuditTrail-$(Get-Date -Format yyyyMMddHHmm).csv" -NoTypeInformation
```

**Resolution.**
1. Capture E-01 through E-09 per §0.4 before any further action.
2. If a second admin reverted: contact that admin out-of-band; align on the policy intent; open a change-management ticket per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) before re-enabling.
3. If IaC is the cause: pause the IaC pipeline (disable scheduled trigger), update the desired state to `protectionLevel = Standard`, peer-review the PR, then re-run.
4. If Microsoft service-side: open a Pro Direct / Premier ticket citing the correlation IDs from Step 1; do not re-attempt the toggle until Microsoft confirms.
5. Re-enable Managed Environments via PPAC; re-validate after 30 minutes and again at the 24-hour mark.

**Prevention.**
- Configure a Sentinel alert on `KQL-01` for `Operation == 'SetEnvironmentProtectionLevel' and AdditionalDetails has 'Basic'` against any environment tagged `Zone3`.
- Require dual-control approval (two Power Platform Admins) for any Zone 3 ME state change via PIM-eligible role activation with approval workflow.
- Add a daily drift-detection job (`Get-Agt21Drift`) that compares IaC desired state to PPAC actual state and alerts on divergence.

**Regulatory-Evidence Implications.** A Zone 3 Managed Environment regression that goes undetected can invalidate the supervisory framing the firm relies on for FINRA Rule 3110 supervision evidence (because guardrails like sharing-limits and solution-checker only apply when ME is enabled). Capture E-01..E-09. Open a [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) incident if the regression coincided with maker activity that would otherwise have been blocked. Retain evidence 7 years per SEC Rule 17a-4. If the firm is in an active examination window, notify Legal before remediation.

**Cross-references.** [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) · [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)

---

### Scenario 2 — "You don't have permission" when toggling Managed Environments from PPAC

**Symptom.** An administrator opens PPAC → Environments → selects the environment → Edit Managed Environments and sees one of the following:
- The toggle is greyed out / read-only.
- A red banner reads "You don't have permission to perform this action."
- The Save button is disabled even after toggling.

**Likely Cause (ranked).**
1. The user holds **Environment Admin** or **Delegated Admin** but not a tenant-level role. Managed Environments enable/disable requires **Power Platform Admin** or **Dynamics 365 Admin** at the tenant level.
2. The user holds the role via **PIM Eligible** but has not activated the role for the current session.
3. The role assignment is scoped to an **Administrative Unit** that does not include the environment's owning Dataverse instance (rare but possible in segmented FSI tenants).

**Diagnostic Steps (Portal).**
1. Entra Admin Center → **Roles & admins** → search for the user → confirm `Power Platform Administrator` or `Dynamics 365 Administrator` is **Active** (not just Eligible).
2. PIM (Entra) → **My roles** → if eligible, activate the role for the next 1–4 hours with a justification reference (ServiceNow ticket).
3. PPAC → top-right user chip → confirm the cloud designation matches the target tenant.

**Diagnostic Steps (PowerShell).**
```powershell
# Confirm the signed-in identity actually holds the role at request time
Connect-MgGraph -Scopes 'Directory.Read.All','RoleManagement.Read.Directory'
$user = Get-MgUser -Filter "userPrincipalName eq '<upn>'"
Get-MgRoleManagementDirectoryRoleAssignment -Filter "principalId eq '$($user.Id)'" |
    ForEach-Object {
        $def = Get-MgRoleManagementDirectoryRoleDefinition -UnifiedRoleDefinitionId $_.RoleDefinitionId
        [pscustomobject]@{ Role = $def.DisplayName; Scope = $_.DirectoryScopeId }
    }
```

**Resolution.**
1. Activate the appropriate tenant-level role via PIM, with justification, for the minimum window required.
2. If the user genuinely needs persistent access: document a role-assignment change ticket and have the Entra Global Admin assign Power Platform Admin via PIM Eligible (never permanently active).
3. Re-attempt the PPAC operation in a new browser session (clear cached tokens) after activation.

**Prevention.**
- Maintain the canonical role catalog ([role-catalog.md](../../../reference/role-catalog.md)) and reconcile quarterly against actual PIM assignments.
- Forbid permanent (non-PIM) assignment of Power Platform Admin in Zone 3 tenants. Enforce via Entra Conditional Access requiring PIM activation for the role.
- Provide a short reference card to admins listing which roles can perform which Managed Environments operations.

**Regulatory-Evidence Implications.** Failure to enforce least privilege on the Power Platform Admin role is a SOX 404 ITGC finding ("inadequate segregation of duties / privileged access management"). NYDFS 23 NYCRR 500.07 (access privileges) requires periodic review of privileged access. Capture the Entra Audit Log entry for any role activation associated with a Managed Environments change; retain 7 years.

**Cross-references.** [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [role-catalog.md](../../../reference/role-catalog.md)

---

### Scenario 3 — `protectionLevel` returns blank or `Unknown` from PowerShell

**Symptom.** `Get-AdminPowerAppEnvironment` returns environments where `Properties.governanceConfiguration.protectionLevel` is `$null`, blank, or the property `governanceConfiguration` itself is missing — even though PPAC clearly shows the environment as Managed.

**Likely Cause (ranked).**
1. The `Microsoft.PowerApps.Administration.PowerShell` module is older than 2.0.190 and does not project the property in the response object.
2. The script is running under PowerShell 7+. The admin module emits warnings and may silently drop properties for some operations under PS 7+; certain admin scenarios are only fully supported on Windows PowerShell 5.1.
3. The session was authenticated against the wrong cloud and is enumerating an empty / partial result.
4. The environment is a **Default** environment in a tenant where Default has special-case property projection — confirm by GUID rather than display name.
5. Transient API throttling truncated the response — re-issue the call.

**Diagnostic Steps (Portal).** PPAC → Environments → confirm the chip displays "Managed Environment" — provides ground truth to compare against PowerShell.

**Diagnostic Steps (PowerShell).**
```powershell
# Verify module version and host
$PSVersionTable.PSVersion
Get-Module Microsoft.PowerApps.Administration.PowerShell | Select-Object Version, Path

# Re-pull a single environment with full property expansion
$env = Get-AdminPowerAppEnvironment -EnvironmentName '<env-guid>'
$env | ConvertTo-Json -Depth 12 | Out-File ".\Agt21-Sc3-Env.json"

# Cross-check against the BAP API directly
$Body = @{ '`$expand' = 'permissions,properties' } | ConvertTo-Json -Compress
Invoke-PowerAppsApi -Method GET -Route "providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/<env-guid>?api-version=2020-10-01" |
    ConvertTo-Json -Depth 12 | Out-File ".\Agt21-Sc3-Env-Bap.json"
```

**Resolution.**
1. Upgrade the module to ≥ 2.0.190: `Update-Module Microsoft.PowerApps.Administration.PowerShell`.
2. Re-run the inventory under Windows PowerShell 5.1 (`powershell.exe`, not `pwsh.exe`).
3. Re-authenticate with `Add-PowerAppsAccount` and re-issue the inventory; confirm `protectionLevel` is now populated.

**Prevention.**
- Pin the module version in the [PowerShell baseline](../../_shared/powershell-baseline.md) and enforce in CI/CD via `Required-Module` manifests.
- Run inventory jobs from a hardened Windows admin VM with PS 5.1 as the default shell for Power Platform admin work.
- Add a sanity check at the top of every inventory script that fails fast if `$PSVersionTable.PSVersion.Major -ne 5` or module version is below the floor.

**Regulatory-Evidence Implications.** An inventory CSV that silently records `protectionLevel = blank` for environments that are actually Managed produces **misleading evidence**. If submitted to an examiner without correction, this could be characterized as a books-and-records integrity issue under FINRA Rule 4511 / SEC Rule 17a-3. Always cross-validate inventory output against PPAC for at least one sentinel environment per run before submission.

**Cross-references.** [PowerShell baseline](../../_shared/powershell-baseline.md) · [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)

---

### Scenario 4 — Sharing-limit policy ignored: a flow is shared with 50 users despite a limit of 20

**Symptom.** A Managed Environment is configured with **Sharing limits → Share with a maximum of 20 people**. A maker shares a flow with 50 users via the Power Automate portal. The share succeeds. No banner, no block, no notification to admins.

**Likely Cause (ranked).**
1. **The sharing limit governs solution-aware canvas apps and (since 2024) solution-aware cloud flows; it does NOT govern standalone (non-solution) cloud flows or shared-via-group memberships exceeding the limit.** This is by design and is the most common cause.
2. The maker is a Power Platform Admin / Dynamics 365 Admin — admins **bypass** sharing limits by design.
3. The sharing limit was changed *after* the share occurred. **Sharing limits are NOT retroactive**; pre-existing shares persist.
4. The share targeted an Entra group whose membership exceeds 20 users; sharing-limit enforcement counts the group as one entity, not its expanded members.
5. The environment lost its Managed status briefly and the share occurred during the gap (correlate with Scenario 1).

**Diagnostic Steps (Portal).**
1. PPAC → Environments → select environment → **Settings** → **Product** → **Sharing** → confirm the configured limit and the **As of** timestamp.
2. Power Automate (maker portal) → the shared flow → **Owners** panel → enumerate explicit principals (users vs groups).
3. Determine whether the flow is **solution-aware** or **standalone**: Power Automate → flow → **Details** pane → "Solution" field.

**Diagnostic Steps (PowerShell).**
```powershell
# Pull sharing-limit policy
$lim = Get-Agt21SharingLimits -EnvironmentName '<env-guid>'
$lim | ConvertTo-Json -Depth 6

# Pull the actual share recipients on the flow
Get-AdminFlowOwnerRole -EnvironmentName '<env-guid>' -FlowName '<flow-guid>'

# Check audit log for the share event
Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-30) -EndDate (Get-Date) `
    -RecordType MicrosoftFlow `
    -Operations ShareFlow `
    -ObjectIds '<flow-guid>'
```

**Resolution.**
1. If standalone flow: document the gap in the Risk Register; require makers to convert business-critical flows to solution-aware. Communicate via the maker community channel.
2. If admin-bypass: review whether the admin had a valid business reason; if not, retroactively un-share and document in the change log.
3. If retroactive-gap: manually re-share to comply with the new limit. Communicate to affected users.
4. If group-expansion: replace the broad group with a narrower group whose membership is at or below the limit; or accept the risk and document.

**Prevention.**
- Require all production flows in Zone 3 to be solution-aware. Enforce via solution-checker rule (Scenario 5) and via Pipelines policy that rejects standalone-flow deployments to Zone 3 (see Scenario 14).
- Build a Sentinel detection on `KQL-02` to alert when ShareFlow recipientCount exceeds the configured limit, regardless of solution-awareness.
- Quarterly sharing-limit attestation: produce a per-environment report of all flows whose share count exceeds the limit; require maker certification.

**Regulatory-Evidence Implications.** Excessive sharing of a flow that processes customer NPI implicates GLBA §501(b) (administrative safeguards) and the firm's WISP. If the over-sharing led to a person without a business need accessing customer data, the firm should evaluate notification obligations under state breach laws (e.g., NYDFS 500.17(a)). FINRA Rule 3110 supervision: the firm should be able to demonstrate it knew about the over-share and either remediated or accepted with documented justification.

**Cross-references.** [Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) · [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) · [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)

---

### Scenario 5 — Solution checker blocks a valid solution import

**Symptom.** A Power Platform pipeline (or a maker performing a manual import) attempts to deploy a managed solution into a Zone 3 Managed Environment. Solution checker fails the import with a **High** severity finding (e.g., "use of unsupported API", "JavaScript web resource performs unmanaged DOM access"). The maker insists the solution worked previously and was certified by an internal review.

**Likely Cause (ranked).**
1. A genuinely unsafe pattern was introduced in a recent change and is correctly being blocked.
2. A solution-checker rule was updated by Microsoft (rules are versioned and updated periodically) and now flags a pattern that previously passed.
3. The environment's checker enforcement level was tightened from **Warn** to **Block** without notifying makers.
4. The solution contains a third-party (ISV) component whose code triggers the rule, but the ISV has a documented exception.
5. A genuinely false positive — rare but real; verifiable by re-running the same solution against a sandbox with the same checker version.

**Diagnostic Steps (Portal).**
1. PPAC → environment → **Solutions** → failed import → **View results** → expand the finding to see the file/line/rule reference.
2. PPAC → environment → **Settings** → **Product** → **Solution checker** → confirm enforcement mode (Warn vs Block) and the **As of** timestamp.
3. Microsoft Learn → look up the rule code (e.g., `web-use-relative-uri`) for the official remediation guidance.

**Diagnostic Steps (PowerShell).**
```powershell
$results = Get-Agt21SolutionChecker -EnvironmentName '<env-guid>' -SolutionName '<solution-name>' -DaysBack 30
$results | Where-Object { $_.Severity -eq 'High' } |
    Export-Csv ".\Agt21-Sc5-CheckerHigh.csv" -NoTypeInformation
```

**Resolution.**
1. **Default position: fix the finding**, do not bypass. Pair the maker with a developer to remediate the flagged code per Microsoft Learn guidance.
2. If the finding is genuinely a false positive: file a Microsoft support case with the rule ID and a minimal repro. Do not bypass production.
3. If the rule is new and the solution is business-critical: temporarily relax the environment to **Warn** mode under a change ticket with explicit time bound (e.g., 14 days), open a remediation epic, and revert to **Block** at the deadline.
4. If an ISV component: obtain the ISV's documented exception; record in the Risk Register with an expiration date.

**Prevention.**
- Run solution checker in **Warn** mode in non-production / Zone 2 environments and in **Block** mode in Zone 3, so issues are caught before they reach production.
- Subscribe to Microsoft Power Platform release notes and publish a quarterly maker briefing on new checker rules.
- Embed a solution checker step in the CI pipeline (Power Platform Build Tools / Azure DevOps) that runs against the source-controlled solution before any deployment attempt.

**Regulatory-Evidence Implications.** Solution checker results are part of the SDLC evidence trail expected under SOX §404 ITGC for change management. Capture the checker report (PDF or JSON export) and link it to the corresponding change ticket. For models embedded in solutions, the checker trail also informs OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) model validation evidence (model implementation review).

**Cross-references.** [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) · [Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md)

---

### Scenario 6 — IP firewall lockout: admins cannot reach Dataverse

**Symptom.** After enabling **IP firewall** on a Zone 3 Managed Environment in **Enforce** mode (not AuditOnly), administrators report that Dataverse is unreachable: model-driven apps fail to load; Power Automate flows referencing Dataverse fail with `403 Forbidden`; XrmToolBox / Dataverse REST clients fail to authenticate. PPAC environment view still works, but every data-plane action against Dataverse fails.

**Severity: Sev1.** This scenario triggers the Sev1 evidence floor.

**Likely Cause (ranked).**
1. The configured allow-list IP ranges do not include the actual egress IPs of the affected admins — most common when admins moved to a new VPN concentrator, when corporate egress NAT was renumbered, or when a remote admin is on a residential ISP not enumerated in the allow-list.
2. The IP firewall was flipped from **AuditOnly** directly to **Enforce** without analyzing the AuditOnly logs first; the allow-list is an estimate, not derived from observed traffic.
3. Connector-bound service principals (e.g., the Power Automate service backbone) are coming from Microsoft service IPs not enumerated in the allow-list. (Microsoft service IPs are auto-allowed by design but check this assumption.)
4. The trusted-service-tag exception (e.g., `PowerPlatformInfra`) was disabled.

**Diagnostic Steps (Portal).**
1. PPAC → environment → **Settings** → **Privacy + Security** → **IP firewall** → confirm **Enforce** mode and the configured allow-list. Note the **As of** timestamp and last editor.
2. PPAC → environment → **Audit history** (Dataverse) → filter to "IP firewall denied" events for the last 24 hours.
3. M365 Admin Center → **Health** → confirm no overlapping Microsoft incident.

**Diagnostic Steps (PowerShell).**
```powershell
$fw = Get-Agt21IpFirewall -EnvironmentName '<env-guid>'
$fw | ConvertTo-Json -Depth 6 | Out-File ".\Agt21-Sc6-Fw.json"

# Pull AuditOnly-style data even in Enforce mode using Sentinel KQL-03 equivalent
Search-UnifiedAuditLog -StartDate (Get-Date).AddHours(-24) -EndDate (Get-Date) `
    -RecordType PowerAppsAdmin -Operations 'DataverseAccessDenied' `
    -ObjectIds '<env-guid>' |
    Export-Csv ".\Agt21-Sc6-Denials.csv" -NoTypeInformation
```

**Resolution (recovery path).**
1. **Capture E-01..E-09 first.** Sev1 mandate.
2. Engage the Power Platform Service Admin via PIM activation. The Power Platform Service Admin role can edit the IP firewall configuration via PPAC even when Dataverse is data-plane-locked, because PPAC is a control-plane operation.
3. Switch the IP firewall to **AuditOnly** mode (do **not** disable the feature outright — that loses the configuration history).
4. Wait for propagation (typically 5–15 minutes).
5. Validate admin connectivity returns.
6. From the AuditOnly logs accumulated in the next 24–48 hours, derive the actual set of egress IPs in use and update the allow-list.
7. Re-enable **Enforce** mode only after a peer-reviewed allow-list is committed to IaC and a rollback ticket is staged.

**Prevention.**
- Never go directly from no-firewall to Enforce. Stage: Off → AuditOnly (≥ 4 weeks observation) → Enforce (with the peer-reviewed allow-list derived from AuditOnly logs).
- Maintain the allow-list in IaC; require dual approval for any change.
- Document the corporate egress IP map and the named residential exceptions for emergency-on-call admins (or require those admins to use a corporate VPN).
- Set a Sentinel alert on `KQL-03` for sudden spikes in DataverseConnectionRejected events.

**Regulatory-Evidence Implications.** A Sev1 IP firewall lockout produces an **availability incident** that may need disclosure to business stakeholders and (depending on customer impact) regulators. NYDFS 23 NYCRR 500.17(a) requires notice of cybersecurity events within 72 hours; an IP firewall misconfiguration is generally not a "cybersecurity event" but should be evaluated case-by-case. SOX 404 ITGC: capture the change ticket, the AuditOnly evidence basis for the allow-list, the dual-approval record, and the post-Enforce validation report. Retain 7 years.

**Cross-references.** [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) · [Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) · [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)

---

### Scenario 7 — Sensitive PII discovered in maker welcome content

**Symptom.** During a quarterly governance review, the AI Governance Lead notices the **maker welcome message** on a Zone 3 Managed Environment contains text such as "Contact John Smith (SSN xxx-xx-1234) for elevated access" or a link to an internal document with confidential customer names in the URL. The welcome panel is visible to every maker who lands in the environment.

**Likely Cause (ranked).**
1. A well-meaning admin pasted operational notes into the welcome panel without recognizing the audience — the welcome content is visible to **every maker** in the environment, not only admins.
2. A copy-paste error during environment provisioning brought template text from another system that contained PII.
3. Vendor / consultant contact information that was originally innocuous became sensitive after a reorganization or after the contact left the firm.

**Important.** **Maker welcome content is excluded from Customer Managed Key (CMK) encryption.** It is stored in Power Platform service-fabric metadata encrypted with Microsoft-managed keys. Even when the environment's Dataverse is CMK-encrypted, the welcome content is not. **Do not** assume CMK protects this surface.

**Diagnostic Steps (Portal).**
1. PPAC → environment → **Settings** → **Product** → **Welcome content** → review **all** four panels: welcome message, support contact, learning links, custom logo (alt-text).
2. Repeat for **every** Managed Environment in scope; do not limit to the reported one.

**Diagnostic Steps (PowerShell).**
```powershell
# Pull welcome content for all environments
Get-AdminPowerAppEnvironment |
    ForEach-Object {
        [pscustomobject]@{
            EnvironmentName = $_.EnvironmentName
            DisplayName = $_.DisplayName
            WelcomeMessage = $_.Properties.welcomeContent.welcomeMessage
            SupportContact = $_.Properties.welcomeContent.supportContact
            LearningLinks = ($_.Properties.welcomeContent.learningLinks | ConvertTo-Json -Compress)
        }
    } |
    Export-Csv ".\Agt21-Sc7-Welcome.csv" -NoTypeInformation
```

**Resolution.**
1. Capture the screenshot and CSV evidence (E-01, E-02) of the current welcome panel **before** editing.
2. Replace the offending content with sanitized text (e.g., "Contact the Power Platform Support team via ServiceNow ticket form 'PPLAT-ACCESS'").
3. If the leaked content included regulated PII (SSN, account number, customer name + financial detail) **or** confidential business information that could meet a state breach-notification threshold, treat as a potential incident: open [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) ticket, engage Privacy Office and Legal.
4. Pull the audit log for the welcome-content `UpdateEnvironment` events; identify when the content was added and (using sign-in logs) the population of makers who landed in the environment during the exposure window.

**Prevention.**
- Publish a welcome-content style guide that explicitly forbids PII, internal-only URLs, named individuals (use ticket queues / role mailboxes), and any text that would not be appropriate to read aloud in a public maker community call.
- Quarterly attestation: each environment owner reviews and re-attests welcome content.
- IaC the welcome content where possible so changes go through code review.

**Regulatory-Evidence Implications.** PII exposed in welcome content is a GLBA §501(b) administrative-safeguard issue and may trigger state breach notification (NYDFS 500.17(a) notice within 72 hours if the firm assesses material harm; CCPA/CPRA for California residents; HIPAA only if covered). Even where notification is not required, the firm should document the exposure, scope (number of makers exposed), duration (audit-log derived), remediation, and prevention. Retain 7 years per SEC Rule 17a-4 if any of the exposed content related to a customer transaction, supervisory record, or other §17a-3-covered item.

**Cross-references.** [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) · [Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) · [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)

---

### Scenario 8 — Weekly maker activity digest not arriving on Mondays

**Symptom.** The weekly Managed Environments maker activity digest, which by design fires Monday mornings (tenant timezone), did not arrive in the Power Platform Admin's inbox. Recipients also report the digest stopped appearing for the last 2–3 weeks.

**Likely Cause (ranked).**
1. The recipient mailbox / shared mailbox bounced or quarantined the digest (Exchange Online transport rule, Defender for Office 365 phishing classifier, or full mailbox).
2. The digest sender address is on the Exchange tenant block list (rare but seen after over-aggressive cleanup of safe-senders).
3. The environment was newly created and has not yet generated enough activity to produce a digest; or the environment was disabled / soft-deleted.
4. The recipient was removed from the digest distribution group; no one is now receiving it.

**Diagnostic Steps (Portal).**
1. PPAC → environment → **Settings** → **Audit and logs** → **Weekly digest** → confirm enablement, recipient list, last send timestamp.
2. Exchange Admin Center → message trace for the digest sender → search for the Monday window.
3. M365 Defender → Threats → Quarantine → search recipient inbox.

**Diagnostic Steps (PowerShell).**
```powershell
$dig = Get-Agt21WeeklyDigest -EnvironmentName '<env-guid>'
$dig | ConvertTo-Json -Depth 6

# Exchange message trace (requires Exchange Online Management module)
Get-MessageTrace -SenderAddress 'noreply@microsoft.com' `
    -RecipientAddress 'powerplatform-digest@contoso.com' `
    -StartDate (Get-Date).AddDays(-30) -EndDate (Get-Date) |
    Select-Object Received, Status, Subject |
    Export-Csv ".\Agt21-Sc8-Trace.csv" -NoTypeInformation
```

**Resolution.**
1. If quarantined: release the message and add the digest sender to the Allow list (Defender → Policies → Anti-phishing). Document in the change log.
2. If recipient removed: re-add the recipient and confirm with Exchange Online Admin that the distribution list has the correct nesting.
3. If new environment / soft-deleted: no remediation; document state.

**Prevention.**
- Monitor digest receipt as a heartbeat: if no digest received by Tuesday end-of-day, fire a Sentinel alert.
- Maintain the digest recipient list as a role-mailbox-backed distribution group (e.g., `pplat-digest@contoso.com`) so individual departures do not break delivery.

**Regulatory-Evidence Implications.** The weekly digest is a supervisory-attention artifact: it surfaces new makers, new flows, and orphaned artifacts. If the digest is missing, the firm's FINRA Rule 3110 supervision narrative loses one of its evidence sources. Document gaps explicitly. Capture screenshots of received digests and retain 7 years.

**Cross-references.** [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) · [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)

---

### Scenario 9 — License-compliance banner appears for a maker who is correctly Premium-licensed

**Symptom.** A maker reports a yellow banner in the Power Apps maker portal stating "Your environment requires Power Apps Premium license. Contact your administrator." The maker has been confirmed to hold a Power Apps Premium per-user license assigned via Entra group-based licensing.

**Likely Cause (ranked).**
1. License propagation lag — group-based licensing typically completes within 24 hours but can extend longer for nested groups or tenants under load.
2. The maker holds the license at the user level but is using a guest identity in the environment that does not carry the license.
3. The environment is enabled for **per-app** plan enforcement and the maker holds **per-user** premium — verify which plan is configured on the specific app.
4. The license is assigned but disabled (service-plan-level disablement on the SKU).
5. The environment requires a **specific** add-on (e.g., Power Apps Portals login capacity, AI Builder credits) that the user does not hold; the banner text is generic.

**Diagnostic Steps (Portal).**
1. M365 Admin Center → Users → search for the maker → Licenses → expand to confirm Power Apps Premium service plan is **Enabled** (not just assigned).
2. Entra Admin Center → Users → maker → Group memberships → confirm group-based licensing source.
3. PPAC → environment → **Settings** → **License** → review enforcement model.

**Diagnostic Steps (PowerShell).**
```powershell
$lic = Get-Agt21LicenseRollup -UserPrincipalName '<upn>'
$lic | ConvertTo-Json -Depth 6

# Direct Graph license check
Connect-MgGraph -Scopes 'User.Read.All','LicenseAssignment.Read.All'
Get-MgUserLicenseDetail -UserId '<upn>' |
    Select-Object SkuPartNumber, ServicePlans
```

**Resolution.**
1. If propagation lag: wait 24 hours; if still failing, force a license reconciliation by removing and re-adding the user to the licensing group.
2. If guest identity: the firm's policy should determine whether guests can be makers in Zone 3. If permitted, assign the license directly to the guest; if not, provision a member identity.
3. If per-app vs per-user mismatch: align the license SKU to the enforcement model.
4. If service-plan disabled: re-enable via M365 Admin Center.

**Prevention.**
- Standardize on group-based licensing with documented group → SKU mapping.
- Build a quarterly license-coverage attestation against `Get-Agt21LicenseRollup` showing every active maker is correctly licensed.
- Avoid mixing per-app and per-user enforcement within the same Zone 3 environment.

**Regulatory-Evidence Implications.** License posture is part of the SOX 404 ITGC change-management evidence (because licensing changes can change supervisory enforcement scope). Beginning June 2026, license-noncompliance notifications become a visible end-user signal — see Scenario 10.

**Cross-references.** [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)

---

### Scenario 10 — Mass license-enforcement event after the June 2026 rollout

**Symptom.** Beginning the week of June 1, 2026, the firm's helpdesk receives 50+ tickets in a single day from makers reporting the license-compliance banner. Apps continue to function (banner is informational in the first phase) but makers are alarmed and the AI Governance Lead is asked for an immediate posture statement.

**Severity: Sev1** (operationally; informational from Microsoft's perspective initially, but the firm's exposure if the rollout progresses to enforcement is material).

**Likely Cause (ranked).**
1. The firm has been relying on **Pay-As-You-Go (PAYG)** meters to cover maker workloads. PAYG does **not** satisfy the Managed Environments licensing floor for these notifications.
2. The firm has Power Apps Premium licenses pooled in a group whose membership has drifted; many makers are using premium connectors without holding the SKU.
3. The firm correctly licenses makers but has not licensed end users of model-driven apps; the per-app plan was undersized.
4. Microsoft's eligibility logic includes a SKU the firm did not realize counted (or excluded one it thought counted) — verify against current Microsoft licensing guide.

**Diagnostic Steps (Portal).**
1. PPAC → **Resources** → **Capacity** → **License consumption (preview)** → review per-environment premium-license requirement vs assigned coverage.
2. PPAC → environment → **Settings** → **License** → review reported gap.

**Diagnostic Steps (PowerShell).**
```powershell
# Tenant-wide rollup
$roll = Get-Agt21LicenseRollup -Tenant
$roll | Export-Csv ".\Agt21-Sc10-LicRollup.csv" -NoTypeInformation

# Identify environments above the gap threshold
$roll | Where-Object { $_.PremiumGapPercent -gt 5 } |
    Select-Object EnvironmentName, DisplayName, MakerCount, PremiumLicensed, PremiumGapPercent
```

**Resolution.**
1. Convene an urgent working session with Microsoft account team, Procurement, and AI Governance Lead.
2. For Zone 3 environments above threshold, immediately purchase Power Apps Premium per-user (or per-app, as fits the workload) to close the gap. Document procurement timeline.
3. For environments where the workload genuinely does not justify Premium, plan the migration of those makers to standard-licensed-only alternatives (e.g., remove premium connector dependencies) **before** the enforcement phase of the rollout.
4. Communicate to makers via the official maker community channel: include the firm's posture, the timeline, and the contact path for license requests.
5. Open a **Risk Acceptance** record in the Risk Register for any environment that will operate in noncompliance during the procurement window.

**Prevention.**
- Build the license-coverage dashboard well **before** June 2026 (target: Q1 2026 readiness).
- Embed license-coverage check as a gate in the [Control 2.15 environment routing](../../../controls/pillar-2-management/2.15-environment-routing.md) flow: if the requesting maker would push the target environment above the gap threshold, route to a different environment or trigger procurement.
- Treat PAYG as a development-stage tool, not a production licensing strategy for Zone 3.

**Regulatory-Evidence Implications.** A widespread license-noncompliance event during an active examiner window is awkward but not directly a books-and-records issue. However, the firm should be prepared to demonstrate it had a plan in place before the June 2026 rollout (procurement records, governance committee minutes referencing the rollout, internal communications). FINRA RN 24-09 / Rule 3110 framing (governance maturity for AI / agent platforms) makes license posture an indirect indicator of program maturity.

**Cross-references.** [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) · [Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md)

---

### Scenario 11 — CMK key rotation fails / environment shows "Encryption pending"

**Symptom.** A scheduled Customer Managed Key (CMK) rotation is initiated against a Zone 3 Managed Environment. PPAC → environment → Encryption shows status "Encryption pending" or "Encryption update failed" for hours or days. Dataverse may continue to function on the prior key but cannot complete migration to the new key.

**Severity: Sev1.** CMK irrecoverability is a worst-case scenario; treat all CMK incidents as Sev1 by default.

**Likely Cause (ranked).**
1. The Power Platform service principal lost **Get / Wrap Key / Unwrap Key** permission on the Key Vault (e.g., access policy or RBAC role assignment was removed by a different team during a Key Vault hardening exercise).
2. The Key Vault has **soft-delete** but not **purge protection** enabled. Microsoft now requires purge protection for CMK; rotation may refuse to proceed until purge protection is enabled.
3. The Key Vault firewall blocks the Power Platform service IPs (or the new key version is in a Key Vault in a region not co-located with the environment).
4. The new key version is disabled, expired, or has an `nbf` / `exp` time outside the operational window.
5. The environment is not in a state that allows rotation (e.g., a backup / restore is in flight; a copy / reset operation is queued).

**Reminder.** Maker welcome content is **excluded** from CMK encryption regardless of rotation success/failure (see Scenario 7).

**Diagnostic Steps (Portal).**
1. PPAC → environment → **Settings** → **Encryption** → review status, key URI, last rotation timestamp, error message (if any).
2. Azure Portal → Key Vault → **Access policies** OR **Access control (IAM)** → confirm the Power Platform service principal (App ID `7df0a125-d3be-4c96-aa54-591f83ff541c` for commercial; verify per cloud) holds Get/Wrap/Unwrap.
3. Azure Portal → Key Vault → **Properties** → confirm **Soft-delete enabled** and **Purge protection enabled**.
4. Azure Portal → Key Vault → **Networking** → confirm the firewall allows Power Platform service IPs or trusted Microsoft services.
5. Azure Portal → Key Vault → the specific key → **Versions** → confirm the new version is **Enabled** and within `nbf`/`exp`.

**Diagnostic Steps (PowerShell).**
```powershell
$cmk = Get-Agt21CmkStatus -EnvironmentName '<env-guid>'
$cmk | ConvertTo-Json -Depth 6 | Out-File ".\Agt21-Sc11-Cmk.json"

# Confirm Key Vault permissions
Connect-AzAccount
$kv = Get-AzKeyVault -VaultName '<kv-name>'
$kv.AccessPolicies | Where-Object { $_.ObjectId -eq '<powerplatform-sp-objectid>' }
$kv.EnableSoftDelete; $kv.EnablePurgeProtection
```

**Resolution.**
1. **Capture E-01..E-09 first.** Sev1 mandate. Engage Compliance + Legal if the environment holds in-scope customer data and the firm is in an examiner-active window.
2. Re-grant Get/Wrap/Unwrap to the Power Platform service principal.
3. Enable Purge Protection on the Key Vault (this is irreversible — confirm with the Key Vault owner before enabling).
4. If firewall: add the Power Platform service IP range or enable the "Allow trusted Microsoft services" toggle.
5. If key version is disabled / expired: enable a valid version; update the environment's CMK reference to the valid key version URI.
6. Re-initiate rotation from PPAC. Monitor every 30 minutes for 4 hours; expected completion within 24 hours.
7. If rotation still fails, open a Microsoft Pro Direct / Premier ticket immediately. **Do not delete the previous key version** under any circumstance until Microsoft confirms rotation is fully complete and the new key is in use; deleting the prior key during a partial rotation can render Dataverse data **permanently unrecoverable**.

**Prevention.**
- Document the Key Vault dependency in the firm's CMDB. Tag the Key Vault as `Power-Platform-CMK` so cross-team hardening exercises do not strip its access policies.
- Require a 90-day notice and dual approval before any change to the Power Platform CMK Key Vault.
- Schedule rotation during a non-examiner window with on-call coverage.
- Maintain a runbook for the unrecoverable-key scenario (see Scenario 11b in the firm's internal CMK incident playbook).

**Regulatory-Evidence Implications.** CMK is part of the GLBA §501(b) Safeguards Rule technical safeguards posture. A failed rotation that resulted in unauthorized access (e.g., a stale, compromised key remained in use) could trigger NYDFS 500.17(a) 72-hour notice. SOX 404 ITGC: capture the rotation ticket, the Key Vault audit log, the PPAC rotation event log, and the post-rotation validation report. Retain 7 years.

**Cross-references.** [Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) · [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)

---

### Scenario 12 — Tenant Isolation blocks a legitimate vendor connector

**Symptom.** A maker reports that a flow which previously worked has begun failing with "Cross-tenant access blocked by Tenant Isolation policy." The flow uses a connector that authenticates the firm's vendor tenant (e.g., a partner accounting platform that uses a B2B Entra app).

**Likely Cause (ranked).**
1. Tenant Isolation was recently changed from **Allow all** to **Block all with exceptions** and the vendor tenant is not on the exception list.
2. The vendor's Entra tenant ID changed (e.g., merger, restructure) and the old tenant ID on the exception list no longer matches.
3. The connector is mis-classified — it uses a multi-tenant Entra app whose `home tenant` is the vendor, but the connector is configured to authenticate as the vendor's tenant rather than the firm's tenant.
4. The Tenant Isolation rule is configured for **outbound** but the connector requires inbound delegated access; or vice versa.

**Diagnostic Steps (Portal).**
1. PPAC → **Policies** → **Tenant isolation** → review default direction and exception list.
2. Power Automate (maker portal) → flow → run history → expand the failed run → review the `403 / TenantIsolationBlocked` error and capture the partner tenant ID from the error JSON.
3. Entra Admin Center → confirm the partner tenant ID against the firm's vendor inventory.

**Diagnostic Steps (PowerShell).**
```powershell
$ti = Get-Agt21TenantIsolation
$ti | ConvertTo-Json -Depth 6 | Out-File ".\Agt21-Sc12-TI.json"

# Pull recent block events
Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) `
    -RecordType PowerPlatformAdministratorActivity `
    -Operations 'TenantIsolationBlocked' |
    Export-Csv ".\Agt21-Sc12-Blocks.csv" -NoTypeInformation
```

**Resolution.**
1. Validate the vendor relationship is current (Procurement / Vendor Risk Management). Do not add an exception for an out-of-contract vendor.
2. Open a change ticket per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md). Include vendor name, tenant ID, business justification, expiration date.
3. After approval, add the partner tenant ID to the Tenant Isolation **outbound** exception list (and **inbound** if the vendor needs to push to the firm's environment).
4. Notify the maker; have them re-run the flow.

**Prevention.**
- Maintain the Tenant Isolation exception list in IaC; review quarterly against the Vendor Risk Management vendor list.
- All exceptions carry an explicit expiration date; expired exceptions auto-remove via the IaC pipeline.
- Map every approved vendor connector to its required Tenant Isolation exception in the connector inventory.

**Regulatory-Evidence Implications.** Vendor connector decisions implicate third-party risk management programs (FFIEC TPRM guidance; OCC Bulletin 2013-29 third-party relationships; SR 23-4). Capture the change ticket, the vendor due-diligence reference, and the exception expiration date. Retain 7 years.

**Cross-references.** [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) · [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)

---

### Scenario 13 — Cross-tenant data movement detected from a Managed Environment

**Symptom.** Sentinel `KQL-04` (or a Defender for Cloud Apps alert) fires showing that a flow in a Managed Environment is sending data to a tenant that is **not** on the Tenant Isolation exception list — yet the flow runs are succeeding (not blocked). The destination tenant is unfamiliar.

**Severity: Sev1.** Treat as a potential exfiltration incident.

**Likely Cause (ranked).**
1. The connector in question is **not Entra-authenticated**. **Tenant Isolation only governs Entra-authenticated cross-tenant connectors.** A connector that uses an API key, basic auth, OAuth to a non-Entra IdP, or a webhook target by raw URL is **not** subject to Tenant Isolation.
2. The destination is a multi-tenant Entra app whose target tenant is determined dynamically per call — the policy is evaluated on the connector's app registration, not the call's runtime tenant target.
3. The flow uses HTTP / Custom Connector to reach an arbitrary endpoint outside the Tenant Isolation enforcement plane.
4. The flow runs as a service principal whose permissions exceed the maker's; the maker cannot see what the flow is doing.

**Diagnostic Steps (Portal).**
1. Power Automate (maker portal, in admin mode) → environment → all flows → identify the flow → review actions.
2. Defender for Cloud Apps → activity log → filter to the flow's service principal and the destination domain.
3. Sentinel → run `KQL-04` and supplemental queries on egress connector activity.

**Diagnostic Steps (PowerShell).**
```powershell
# Inventory all flows in the environment with their actions
Get-AdminFlow -EnvironmentName '<env-guid>' |
    ForEach-Object {
        $f = Get-AdminFlow -EnvironmentName '<env-guid>' -FlowName $_.FlowName
        [pscustomobject]@{
            FlowName = $f.FlowName
            DisplayName = $f.DisplayName
            CreatedBy = $f.CreatedBy.userPrincipalName
            Connectors = ($f.Internal.properties.definitionSummary.actions | ConvertTo-Json -Compress)
        }
    } |
    Export-Csv ".\Agt21-Sc13-FlowInventory.csv" -NoTypeInformation
```

**Resolution (incident path).**
1. **Capture E-01..E-09 immediately.** Engage Incident Response, Privacy Office, Legal.
2. Identify the maker, the flow, the destination, the data volume (where possible), and the time window. Do **not** disable the flow before snapshotting evidence — disabling can lose run history detail.
3. After snapshot, **disable** the flow (PPAC / Power Automate admin: turn off, do not delete).
4. Determine whether the data movement was authorized (e.g., a known vendor integration that bypasses Tenant Isolation by design, or unauthorized exfiltration). Engage the maker's manager.
5. If unauthorized: open a [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) incident; coordinate with HR / Legal on user actions; follow breach-assessment workflow.
6. If authorized but undocumented: backfill the documentation, add to the connector inventory, and either bring the connector under Tenant Isolation (Entra-authenticated alternative) or implement a compensating control.

**Prevention.**
- Combine Tenant Isolation with a **Connector Allow-list** ([Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md)) that blocks HTTP / Custom Connector / non-Entra-authenticated connectors in Zone 3 by default; require business-justified exceptions.
- Implement DLP policies ([Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)) that block business-data flow into the Non-Business connector group.
- Monitor egress at the connector layer with a Sentinel rule on `KQL-04` and analogous queries for HTTP egress.

**Regulatory-Evidence Implications.** This is a potential GLBA §501(b) and state-breach-law trigger. NYDFS 500.17(a) requires 72-hour notice for material cybersecurity events. SEC Reg S-P (amended 2024) requires customer notification within 30 days for incidents involving customer information. FINRA Rule 4530 requires reporting to FINRA within 30 days for certain incidents. Engage Legal immediately; do not make external statements without coordination. Capture all evidence; retain 7 years.

**Cross-references.** [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) · [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) · [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)

---

### Scenario 14 — Pipelines (Power Platform) deploys to an Unmanaged target despite policy

**Symptom.** A Power Platform Pipeline run successfully deploys a solution from Dev → Test → Prod. The "Prod" target environment is intended to be a Managed Environment; however, the deployment lands in an Unmanaged environment that happens to also be named "Prod" or that was substituted recently.

**Likely Cause (ranked).**
1. The Pipelines configuration references the target by **DisplayName** rather than by **environment GUID**. A new environment with the same DisplayName was created and is being resolved instead.
2. The intended Managed target was reverted to Unmanaged (correlate with Scenario 1) and the pipeline ran during the gap.
3. The Pipelines host environment's deployment-stage configuration was edited by a maker without change control.

**Diagnostic Steps (Portal).**
1. Power Apps maker portal → **Pipelines** → the pipeline definition → review each deployment stage's target environment GUID (not just name).
2. PPAC → Environments → the target environment → confirm Managed Environments status at the time of deployment by cross-referencing audit log.

**Diagnostic Steps (PowerShell).**
```powershell
# Inventory pipelines (Pipelines is a Dataverse-resident model; query the host environment)
$pipeHost = '<pipelines-host-env-guid>'
Get-CrmRecords -conn $conn -EntityLogicalName deploymentpipeline -Fields name,statecode |
    Format-Table

# For each pipeline, list stages and target environments
Get-CrmRecords -conn $conn -EntityLogicalName deploymentstage -Fields name,targetenvironmentid
```

**Resolution.**
1. Pause the pipeline.
2. Update each stage to reference the target by **environment GUID** explicitly.
3. Add a pre-deployment guardrail: a custom action / Azure DevOps task that calls `Get-AdminPowerAppEnvironment` and verifies the target's `protectionLevel == 'Standard'` before allowing the deployment to proceed.
4. Roll back the misdeployment if it created drift in the wrong environment; coordinate with the solution owner.
5. Document in [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).

**Prevention.**
- Always reference environments by GUID in pipeline definitions, IaC, and runbooks. DisplayName is for humans; GUID is for machines.
- Add a CI gate that validates target environments are Managed before any Zone 3 deployment.
- Forbid maker self-service edits to pipeline stage configuration; require Power Platform Admin approval.

**Regulatory-Evidence Implications.** Misdeployment to an environment with the wrong governance posture (e.g., Unmanaged when policy requires Managed) is a SOX 404 ITGC change-management failure. Capture the pipeline run log, the stage configuration as it was at run time, and the environment state evidence. Retain 7 years.

**Cross-references.** [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) · [Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md)

---

### Scenario 15 — Environment Routing sends a new maker to the wrong default environment

**Symptom.** A new maker creates their first canvas app. Per the firm's Environment Routing policy ([Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md)), the maker should be routed to a personal Zone 1 environment (per-user developer environment). Instead, the maker is dropped into the tenant **Default** environment, which the firm has classified as legacy and is in the process of decommissioning.

**Likely Cause (ranked).**
1. Environment Routing was not enabled tenant-wide. Routing requires explicit opt-in.
2. Environment Routing is enabled but the routing rules do not match this maker's persona (e.g., the rules require the maker to be in a specific Entra group; the maker is not yet a member).
3. The maker's first action was not eligible for routing (e.g., they opened a shared app rather than creating a new one). Routing fires only on certain "first-touch" actions.
4. Provisioning of the per-user developer environment failed (capacity exhausted); routing fell back to Default.

**Diagnostic Steps (Portal).**
1. PPAC → **Environments** → tenant-level **Settings** → **Environment Routing** → confirm enablement, rules, and target group.
2. Entra → confirm the maker is in the correct routing-eligible group.
3. PPAC → **Environments** → check developer environment capacity (`Microsoft.PowerApps/environments` of `kind == Developer`).

**Diagnostic Steps (PowerShell).**
```powershell
# Confirm Environment Routing settings (Power Platform CLI / PAC)
pac admin tenant-settings list --json |
    ConvertFrom-Json |
    Select-Object -ExpandProperty environmentRouting

# Confirm developer environment capacity
Get-AdminPowerAppEnvironment | Where-Object { $_.EnvironmentType -eq 'Developer' } |
    Group-Object CreatedBy.userPrincipalName |
    Select-Object Name, Count |
    Sort-Object Count -Descending
```

**Resolution.**
1. If Routing is disabled: open a change ticket; enable Routing under [Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md).
2. If maker not in eligible group: add via the standard provisioning workflow.
3. If capacity exhausted: provision additional developer environment quota (Microsoft Power Platform admin → Resources → Capacity); document.
4. Migrate the maker's existing work from Default to the correct environment; archive the artifacts in Default per the decommission plan.

**Prevention.**
- Enable Environment Routing tenant-wide before disabling Default for maker creation.
- Build automation that auto-adds new hires (Entra dynamic group) to the routing-eligible group on Day 1.
- Monitor developer environment capacity weekly; alert at 80%.

**Regulatory-Evidence Implications.** Routing is a maker-experience and governance hygiene control; failures generally do not have direct regulatory implications. However, if work created in the wrong environment includes regulated data and falls outside the supervisory scope, the firm should re-evaluate. Capture the routing-rule configuration history; retain per the firm's standard configuration-change retention.

**Cross-references.** [Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md) · [Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md)

---

### Scenario 16 — Inactive-resource cleanup deleted a business-critical app

**Symptom.** Managed Environments inactive-resource cleanup runs as scheduled. A maker reports that a business-critical canvas app has disappeared from the maker portal. Audit log shows the app was deleted by the system service principal as part of inactive-resource cleanup, with the reason "Last accessed > 90 days."

**Severity: Sev1** if the app is truly business-critical and recovery is non-trivial.

**Likely Cause (ranked).**
1. The app was genuinely unused (correctly identified as inactive) but a quarterly user did not interact with it in the 90-day window — the cleanup correctly flagged it but the policy is wrong for this app.
2. The app was wrapped behind a Power Automate trigger that did not register as "user access," so the activity counter did not increment despite the app being in use.
3. The app's owner left the firm and ownership reassignment did not happen; the app accumulated inactivity flags despite continued downstream consumption.
4. The cleanup policy was misconfigured (window too short, scope too broad).
5. The app was excluded from cleanup via tag or exception, but the exception expired.

**Diagnostic Steps (Portal).**
1. PPAC → environment → **Resources** → **Apps** → Recycle Bin / Soft-deleted apps → confirm presence and soft-delete timestamp (apps are typically soft-deleted for 28 days before permanent deletion).
2. PPAC → environment → **Settings** → **Resource cleanup** → review policy, exception list, and cleanup history.
3. Audit log → identify the deletion event and the policy version that triggered it.

**Diagnostic Steps (PowerShell).**
```powershell
# Soft-deleted apps
Get-AdminDeletedPowerAppsList -EnvironmentName '<env-guid>' |
    Where-Object { $_.AppName -eq '<app-guid>' }

# Cleanup policy
Get-AdminPowerAppEnvironment -EnvironmentName '<env-guid>' |
    Select-Object -ExpandProperty Properties |
    Select-Object -ExpandProperty governanceConfiguration |
    Select-Object -ExpandProperty settings |
    ConvertTo-Json -Depth 6
```

**Resolution.**
1. **Capture E-01..E-09 first.**
2. If within the soft-delete window (typically 28 days): restore via `Restore-AdminDeletedPowerApp -EnvironmentName <env> -AppName <app>`.
3. If past the soft-delete window: engage the maker community for the latest local export; check source control. If neither, recovery is not possible — escalate to the business owner.
4. Add the app (or the maker's app inventory) to the cleanup exception list.
5. Open a [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) incident and conduct a root-cause review of the cleanup policy.

**Prevention.**
- Require all Zone 3 apps to be source-controlled (export-as-msapp committed to a Git repo) per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).
- Maintain an explicit "do not cleanup" tag for business-critical apps; expire tags annually with re-attestation.
- Configure the cleanup policy in **Notify-only** mode for the first 60 days of operation to surface candidates for review before any deletion occurs.
- Ensure ownership reassignment is part of the offboarding workflow ([Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)).

**Regulatory-Evidence Implications.** Loss of a business-critical app that was relied upon for a regulated workflow (e.g., trade reconciliation, KYC review) is a books-and-records continuity issue. FINRA Rule 4511 / SEC Rule 17a-3 require records to be preserved; if the app was the system of record for any record, the firm must reconstruct from the underlying data store and document the gap. SOX 404 ITGC: capture the deletion event, the cleanup policy version, the restore evidence (or recovery-failed evidence), and the policy update. Retain 7 years.

**Cross-references.** [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) · [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) · [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)

---

### Scenario 17 — Customer Lockbox approval request not appearing

**Symptom.** Microsoft engineering has indicated (via support ticket or service health) that they need to access tenant data to investigate an issue. Customer Lockbox is enabled. The Power Platform Admin expects to receive an approval request in M365 Admin Center but no request appears, blocking Microsoft's investigation.

**Likely Cause (ranked).**
1. Customer Lockbox is enabled at the M365 tenant level but not enabled for Power Platform specifically; verify both surfaces.
2. The approver group is misconfigured (empty, or pointing to a deactivated mailbox).
3. The request is awaiting Microsoft-side initiation; the Microsoft engineer has not yet triggered it.
4. The notification is being filtered by Defender for Office 365 (rare; Microsoft sender should be on the safe-senders list).

**Diagnostic Steps (Portal).**
1. M365 Admin Center → **Settings** → **Org settings** → **Security & privacy** → **Customer Lockbox** → confirm enabled and approvers.
2. PPAC → tenant settings → confirm Customer Lockbox enabled for Power Platform.
3. Exchange message trace → search for Microsoft Customer Lockbox sender to the approver mailbox.

**Diagnostic Steps (PowerShell).**
```powershell
# M365 setting
Connect-IPPSSession
Get-OrganizationConfig | Select-Object CustomerLockBoxEnabled

# Power Platform tenant setting
pac admin tenant-settings list --json | ConvertFrom-Json |
    Select-Object -ExpandProperty disableCustomerLockbox
```

**Resolution.**
1. If not enabled for Power Platform: open a change ticket and enable. Document policy.
2. If approver group misconfigured: re-point to a monitored role mailbox (e.g., `lockbox-approvers@contoso.com`); ensure the mailbox has multiple human approvers.
3. If Microsoft has not yet initiated: contact the Microsoft case owner.
4. If quarantined: release; whitelist the Customer Lockbox sender.

**Prevention.**
- Backstop the approver mailbox with at least two named individuals plus one role mailbox.
- Quarterly test: have a Microsoft FastTrack contact initiate a Lockbox test request to confirm the path works.
- Document Customer Lockbox approval as part of the firm's privileged-access governance documentation.

**Regulatory-Evidence Implications.** Customer Lockbox is part of demonstrating control over third-party access to tenant data — a key element of GLBA §501(b) administrative safeguards and OCC 2013-29 third-party-relationship management as applied to the cloud provider. Capture every Lockbox request, approval/denial, justification, and access log. Retain 7 years.

**Cross-references.** [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md)

---

### Scenario 18 — Maker cannot create a flow despite holding Power Automate Premium

**Symptom.** A maker holding Power Automate Premium per-user license attempts to create a new cloud flow in a Zone 3 Managed Environment and receives "You don't have permission to create flows in this environment" or "This environment doesn't accept new makers."

**Likely Cause (ranked).**
1. The environment's **Maker** security group restricts creation to a specific Entra group; the maker is not a member.
2. The environment is at its maker quota or solution quota.
3. The environment's Dataverse security role for makers (e.g., Environment Maker) was not granted to the user.
4. The maker is attempting to create a standalone flow but the environment requires solution-aware flows; the maker portal is presenting a confusing error.
5. The license is held but the service plan is disabled (see Scenario 9).

**Diagnostic Steps (Portal).**
1. PPAC → environment → **Settings** → **Users + permissions** → **Security groups** → confirm the maker is in the Maker group (or no group is set).
2. PPAC → environment → **Settings** → **Users + permissions** → **Users** → confirm the user is added with the **Environment Maker** Dataverse role.
3. Power Apps maker portal as the affected user → attempt creation; capture the error and any correlation ID.

**Diagnostic Steps (PowerShell).**
```powershell
# Confirm maker is in the environment as a Dataverse user with Environment Maker role
$conn = Get-CrmConnection -InteractiveMode -ServerUrl '<dataverse-url>'
Get-CrmRecords -conn $conn -EntityLogicalName systemuser `
    -FilterAttribute domainname -FilterOperator eq -FilterValue '<upn>' |
    Select-Object -ExpandProperty CrmRecords

# License + group membership cross-check
Get-Agt21LicenseRollup -UserPrincipalName '<upn>'
```

**Resolution.**
1. Add the maker to the appropriate Maker group via the firm's standard maker-onboarding workflow.
2. Assign the Environment Maker security role in Dataverse if missing.
3. If quota: review whether the maker should be in this environment or in a different one (Environment Routing).
4. If standalone-vs-solution confusion: provide the maker with a solution template; confirm via training material.

**Prevention.**
- Standardize maker onboarding via Environment Routing ([Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md)) and dynamic Entra groups.
- Monitor environment quotas; alert at 80%.
- Provide a maker self-service "why can't I create" diagnostic page that walks them through the most common causes.

**Regulatory-Evidence Implications.** Maker access denials are not directly a regulatory issue but cumulative friction can drive shadow-IT (e.g., makers using personal accounts or Excel-based workflows outside the platform). The firm should track these denials as a leading indicator of governance friction. No specific evidence retention requirement.

**Cross-references.** [Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md) · [role-catalog.md](../../../reference/role-catalog.md)

---

### Scenario 19 — Solution checker results not exporting; report shows empty

**Symptom.** A Power Platform Admin attempts to export the last 30 days of solution checker results for an upcoming SOX 404 ITGC walkthrough. The export completes but the resulting file is empty or contains only headers.

**Likely Cause (ranked).**
1. No solution checker runs occurred in the window (the environment had no imports).
2. The export filter was too narrow (e.g., date range off-by-one, severity filter excludes everything).
3. The PowerShell module version is below the floor and the export call returns an empty result silently.
4. The user lacks permission to read solution checker results (rare; usually inherited with Power Platform Admin).
5. The export job timed out and produced a partial file.

**Diagnostic Steps (Portal).**
1. PPAC → environment → **Solutions** → **Solution checker** → review the runs list for the window; confirm at least one run is present.
2. Re-run the export with broader filters (full month, all severities).

**Diagnostic Steps (PowerShell).**
```powershell
$results = Get-Agt21SolutionChecker -EnvironmentName '<env-guid>' -DaysBack 30
$results | Measure-Object | Select-Object Count

# If count is 0, expand to 90 days as a sanity check
$results90 = Get-Agt21SolutionChecker -EnvironmentName '<env-guid>' -DaysBack 90
$results90 | Group-Object Severity | Select-Object Name, Count
```

**Resolution.**
1. If genuinely no runs: document for the examiner. Explain that solution checker only runs on solution imports; if no solutions were imported, no results exist. Provide the import history as supporting evidence.
2. If filter issue: re-export with corrected filters.
3. If module version: upgrade per Scenario 3.
4. If permission: assign Power Platform Admin via PIM.
5. If timeout: split the export into smaller windows and concatenate.

**Prevention.**
- Schedule a monthly export job that pulls the prior month's checker results and stores in an immutable archive (per [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)). Then ad-hoc examiner requests are served from the archive without depending on the API.
- Embed checker reports in the change-management ticket workflow so each solution deployment carries its checker evidence.

**Regulatory-Evidence Implications.** Solution checker reports are SOX 404 ITGC evidence (change management). Empty export with no documentation invites a finding. Always include narrative explaining what the export shows (or doesn't show) and why. Retain 7 years.

**Cross-references.** [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)

---

### Scenario 20 — DLP exception requested for a Managed Environment connector

**Symptom.** A maker requests a DLP exception in a Zone 3 Managed Environment to enable a connector currently classified as **Blocked** (e.g., a specific social-media connector, an external storage provider, or a third-party AI service). The maker provides a business-justified use case.

**Likely Cause / Context.** This is not a malfunction — it is a routine governance request that arrives via the Managed Environments surface. The scenario is included because Managed Environments and DLP interact: the Tenant Isolation policy and the Connector Allow-list both layer on top of DLP, and a malformed exception can punch a hole through Managed Environments' otherwise tight posture.

**Diagnostic Steps (Portal).**
1. PPAC → **Policies** → **Data policies** → identify the policy that applies to the target environment; confirm current connector classification.
2. Confirm whether the requested connector is Entra-authenticated (relevant for Tenant Isolation, see Scenario 13).

**Diagnostic Steps (PowerShell).**
```powershell
# Pull DLP policies that scope this environment
Get-DlpPolicy | Where-Object { $_.environments.name -contains '<env-guid>' -or $_.environmentType -eq 'AllEnvironments' }
```

**Resolution.**
1. Open a change ticket per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md). The ticket must include: maker identity, business justification, data classification flowing through the connector, vendor due-diligence reference (if external), expiration date.
2. Cross-reference [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) (Advanced Connector Policies) for any per-action restrictions.
3. Cross-reference [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) for DLP and sensitivity-label interactions.
4. After review by AI Governance Lead and Data Risk Officer, modify the policy via PPAC or PowerShell. Capture before/after policy export.
5. Validate via a test run as the requesting maker.

**Prevention.**
- Maintain a published catalog of approved / pending / denied connectors with rationales.
- Require all exceptions to carry an expiration date; expire automatically via IaC pipeline.
- Quarterly review: every active exception is re-attested or rolled back.

**Regulatory-Evidence Implications.** DLP exceptions are part of the firm's data-governance posture. GLBA §501(b), NYDFS 500.07, FINRA 4530 (in the case of incidents). Capture the change ticket, the policy export before/after, the maker's business-justification statement, and the expiration date. Retain 7 years.

**Cross-references.** [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) · [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) · [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)

---

### Scenario 21 — Managed Environments enabled but usage insights show no data

**Symptom.** A Power Platform Admin enables Managed Environments on a Zone 2 environment and waits for usage-insights dashboards (PPAC → Analytics → environment) to populate. After 14 days, the dashboards remain empty: zero apps, zero flows, zero makers reported even though the environment is in active use.

**Likely Cause (ranked).**
1. The environment lacks the **Dataverse** that usage insights depend on. Even when ME does not strictly require Dataverse for all features, certain analytics surfaces require it.
2. Telemetry ingestion is throttled tenant-wide (rare, transient).
3. The environment is in a region whose analytics pipeline has a known delay (verify Microsoft Learn).
4. Usage insights respect the environment's **data residency** — if cross-region replication is partly disabled, the dashboard host may not see the source data.
5. The maker portal cache is stale; sign out / sign in or use a private browsing session.

**Diagnostic Steps (Portal).**
1. PPAC → environment → confirm Dataverse linkage (Settings → Resources → Dataverse).
2. PPAC → **Analytics** → environment → expand "Last refreshed" timestamp.
3. M365 Admin Center → Health → search for analytics pipeline incidents.

**Diagnostic Steps (PowerShell).**
```powershell
$env = Get-AdminPowerAppEnvironment -EnvironmentName '<env-guid>'
$env.Properties.linkedEnvironmentMetadata
$env.Properties.azureRegion
$env.Properties.governanceConfiguration.protectionLevel
```

**Resolution.**
1. If no Dataverse: provision Dataverse for the environment via PPAC. Note: this is irreversible without recreating the environment; obtain change approval per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).
2. If throttled / regional delay: wait an additional 7 days; if still empty, open a Microsoft support case.
3. If cache: clear browser cache or test in private browsing.
4. While the dashboards are unavailable, derive equivalent usage statistics via PowerShell inventory (`Get-AdminFlow`, `Get-AdminPowerApp`, `Get-AdminFlowRun`) and produce a custom report.

**Prevention.**
- Provision Dataverse for every Zone 2 / Zone 3 environment at creation time, not retroactively.
- Schedule a monthly inventory job that produces the same fields the PPAC analytics page would, regardless of whether the dashboard is populated; serve audit requests from this archive.

**Regulatory-Evidence Implications.** Usage insights are an evidence source for FINRA Rule 3110 supervision (who is doing what in the environment). If the dashboards are empty, the firm should not assume "no activity" — they should derive activity from PowerShell inventory and document the data source. Retain inventory exports per the firm's standard 7-year retention.

**Cross-references.** [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) · [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)

---

### Scenario 22 — Audit log gap during the Managed Environments configuration window

**Symptom.** During an examiner walkthrough, the firm produces the Purview audit log slice for a Managed Environments configuration change. The examiner notices a multi-hour gap in the audit log corresponding to the change window. No `UpdateEnvironment` or `SetEnvironmentProtectionLevel` events are present where they should be.

**Severity: Sev1.** Audit-log gaps during regulator-relevant windows are escalated immediately.

**Likely Cause (ranked).**
1. Purview audit log ingestion was delayed; the events exist but landed late. The Microsoft documented ingestion SLO is hours; verify against the underlying admin activity log.
2. The query was constructed incorrectly (wrong RecordType, wrong UTC offset, wrong ObjectId).
3. The unified audit log was not enabled at the time of the change (rare in mature FSI tenants but seen in newly-acquired subsidiaries).
4. The Purview retention label assigned to audit data was below the firm's policy and events have aged out.
5. A search-result truncation occurred; only the first N rows were returned and the relevant rows are below the cut-off.

**Diagnostic Steps (Portal).**
1. Purview portal → **Audit** → re-run the search with broader filters: full UTC day, no RecordType filter, all users.
2. Cross-check against the Power Platform Admin Activity log directly via the BAP API.
3. M365 Admin Center → Audit settings → confirm unified audit log was enabled at the relevant time (history view).

**Diagnostic Steps (PowerShell).**
```powershell
# Broaden the search aggressively
Search-UnifiedAuditLog -StartDate '2026-04-01T00:00:00Z' -EndDate '2026-04-02T00:00:00Z' `
    -ResultSize 5000 -Formatted |
    Where-Object { $_.AuditData -match '<env-guid>' } |
    Export-Csv ".\Agt21-Sc22-AuditBroad.csv" -NoTypeInformation

# Pull from BAP directly as a second source
Invoke-PowerAppsApi -Method GET -Route "providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/<env-guid>/eventLogs?api-version=2020-10-01"
```

**Resolution.**
1. **Capture E-01..E-09.** The "missing event" itself is part of the evidence package.
2. If the events surface in the broader query: produce the corrected slice to the examiner with a written explanation of the search refinement (filter was too narrow).
3. If the events are confirmed missing: pull from the secondary source (BAP eventLogs API). Most Power Platform admin events are recorded in two places.
4. If both sources confirm absence: open a Microsoft support case with the time window and tenant ID. Engage the Purview Compliance Admin and Legal. Provide the examiner with a transparent narrative — do not speculate.
5. Document the gap in the Risk Register and the examiner's response file.

**Prevention.**
- Enable unified audit log by default at tenant creation (and verify at every onboarding of an acquired subsidiary).
- Apply a Purview retention label to audit data that meets or exceeds the firm's longest applicable retention (typically 7 years).
- Maintain a secondary archive: ship audit data to Sentinel / a SIEM with a longer retention than Purview default.
- Run a quarterly audit-log completeness test: pick a known event (e.g., a deliberate test config change) and confirm it appears in both Purview and the secondary archive within SLO.

**Regulatory-Evidence Implications.** This is a **direct** books-and-records issue. SEC Rule 17a-4(f) requires WORM-quality preservation of supervisory records. FINRA Rule 4511. SOX 404 ITGC. CFTC Reg 1.31. NYDFS 500.06 audit trail. A confirmed audit-log gap should be reported to Compliance immediately; depending on the underlying transaction, regulator notification may follow. Retain all evidence (including the gap evidence) for 7 years minimum, and longer if subject to a litigation hold.

**Cross-references.** [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)

---

### Scenario 23 — Drift between IaC desired state and tenant reality

**Symptom.** The firm uses Terraform / Bicep / a custom IaC pipeline to manage Managed Environments configuration. A scheduled drift-detection job (`Get-Agt21Drift`) reports that for one or more Zone 3 environments, the actual `protectionLevel`, sharing-limit threshold, IP firewall rule set, or CMK key URI does not match the IaC desired state.

**Likely Cause (ranked).**
1. An admin made a manual change in PPAC outside the IaC workflow (most common; usually emergency response that was not back-ported into IaC).
2. A Microsoft platform change altered the property representation (e.g., a new sub-property defaulted to a new value); the IaC code is out of date with the latest property schema.
3. The IaC pipeline failed silently on a recent run; the desired state was never applied.
4. Two IaC pipelines (e.g., one Terraform, one Bicep) are competing on the same resource.
5. The drift detector itself is buggy and reporting false positives.

**Diagnostic Steps (Portal).**
1. PPAC → environment → review the property in question; capture the **As of** timestamp.
2. IaC repository → blame on the property declaration; identify last commit, last apply.

**Diagnostic Steps (PowerShell).**
```powershell
$drift = Get-Agt21Drift -DesiredStateFile '.\desired-state.json' -EnvironmentName '<env-guid>'
$drift | Format-List

# Verify IaC pipeline run history
# (call your CI provider's API; Azure DevOps example)
Invoke-RestMethod -Uri "https://dev.azure.com/<org>/<proj>/_apis/build/builds?definitions=<defid>&api-version=7.1" `
    -Headers @{ Authorization = "Bearer $env:ADO_TOKEN" } |
    Select-Object -ExpandProperty value | Select-Object id, result, finishTime
```

**Resolution.**
1. **Determine the canonical source of truth** before mutating either side. If the manual PPAC change was a deliberate emergency response that should persist, **back-port to IaC** before re-applying.
2. If the manual change was inadvertent, run the IaC pipeline to restore desired state. Capture before/after.
3. If two pipelines are competing: disable one; reconcile.
4. If the property schema changed: update the IaC code to handle the new schema; pin to a known module/provider version.
5. Open a [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) ticket and a [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) RCA if the drift was material (Zone 3, security-relevant property).

**Prevention.**
- Run drift detection daily; alert on any divergence in Zone 3.
- Lock down direct PPAC mutation in Zone 3 via PIM with approval; force change to flow through IaC.
- Maintain a single canonical IaC pipeline per resource type; avoid overlap.
- Pin all provider / module versions; subscribe to release notes for breaking changes.

**Regulatory-Evidence Implications.** SOX 404 ITGC change-management evidence is strongest when IaC desired state, applied state, and runtime state can all be reconciled at any moment. Drift breaks this narrative. Capture the drift report, the reconciliation ticket, the back-port commit (if any), and the post-reconciliation drift report. Retain 7 years.

**Cross-references.** [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) · [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)

---

### Scenario 24 — Examiner production request for a full Managed Environments evidence package

**Symptom.** A FINRA, SEC, OCC, Federal Reserve, NYDFS, or state-regulator examiner issues a written request for "the firm's complete Managed Environments configuration, change history, and supervisory artifacts for the period [start] to [end] for the following environments: [list]."

**Severity: Sev2** (operational urgency); **must be handled with Legal and Compliance leadership from the first hour.**

**Likely Cause / Context.** This is not a malfunction. It is the moment every prior scenario was preparing for. The request will typically arrive with a deadline (10–30 business days). The firm's response quality directly reflects the maturity of its Managed Environments program.

**Engagement protocol.**
1. **Do not respond directly to the examiner without Legal and Compliance review.** Acknowledge receipt only; defer substantive response until reviewed.
2. Open a confidential incident record. Restrict access to a need-to-know list.
3. Stand up a daily standup with Legal, Compliance, AI Governance Lead, and the Power Platform Admin. Track production milestones.
4. Apply a **legal hold** to all evidence sources within scope (Purview retention, Sentinel data, IaC repos, ServiceNow tickets). This may temporarily extend retention beyond the firm's normal cycle.

**Evidence package contents (minimum).**
| # | Artifact | Source | Owner |
|---|---|---|---|
| 1 | Per-environment configuration snapshot at the start and end of the request window | `Get-AdminPowerAppEnvironment` against historical data; cross-check IaC commit history | Power Platform Admin |
| 2 | Full change history for each environment in scope | Purview audit log + Sentinel + Power Platform admin activity log + ServiceNow change-ticket export | Purview Compliance Admin |
| 3 | Sharing-limit configuration history | `Get-Agt21SharingLimits` + audit | Power Platform Admin |
| 4 | Solution checker results for the window | Per Scenario 5 / 19 export | Power Platform Admin |
| 5 | IP firewall configuration + rejection logs | `Get-Agt21IpFirewall` + KQL-03 + audit | Power Platform Admin |
| 6 | CMK key history including rotations | `Get-Agt21CmkStatus` + Azure Key Vault audit | Power Platform Admin + Azure Admin |
| 7 | Tenant Isolation policy + exception inventory | `Get-Agt21TenantIsolation` + change tickets | Power Platform Admin |
| 8 | Customer Lockbox approvals for the window | M365 Admin Center → Lockbox history | Entra Global Admin |
| 9 | License coverage rollup | `Get-Agt21LicenseRollup` snapshots | M365 Admin |
| 10 | Weekly digest receipt evidence | Mailbox archive | Power Platform Admin |
| 11 | Pipelines deployment history | Pipelines audit + ADO/GitHub Actions run logs | Power Platform Admin |
| 12 | Environment Routing configuration history | Tenant settings audit | Power Platform Admin |
| 13 | Inactive-resource cleanup history | Cleanup policy audit + restore events | Power Platform Admin |
| 14 | Drift detection reports for the window | `Get-Agt21Drift` archive | Power Platform Admin |
| 15 | AI Governance Committee minutes covering Managed Environments decisions | Governance archive | AI Governance Lead |
| 16 | Role assignment + PIM activation history for Power Platform Admin / Dynamics 365 Admin | Entra audit + PIM logs | Entra Global Admin |
| 17 | Maker community communications regarding governance changes | Comms archive | AI Governance Lead |
| 18 | Hash manifest + chain-of-custody record for the entire production package | Manual | Power Platform Admin (countersigned) |
| 19 | Cover narrative explaining the package, methodology, scope limitations, and any known gaps (per Scenario 22) | Manual | AI Governance Lead + Legal review |

**Production hygiene.**
- Every artifact is hashed (SHA-256) and the hash is recorded on an index.
- A second person verifies each hash on production day (chain of custody).
- The package is delivered via the channel specified by the examiner (regulator portal, encrypted USB, secure file transfer). Do not email.
- A copy of the production package is retained by the firm for at least 7 years (longer if litigation hold).

**Cross-validation steps before submission.**
1. Re-run the inventory against the live tenant; spot-check that historical snapshots reconcile to the live state with documented intervening changes.
2. Reconcile audit log timestamps against ServiceNow tickets; explain any unmatched events.
3. Where evidence is incomplete (e.g., the `Last UI Verified` date precedes a Microsoft change and the screenshot may not reflect current UI), state this in the cover narrative.
4. Where compensating controls were used (e.g., audit log gap), describe each.

**Regulatory-Evidence Implications.** This scenario *is* the regulatory-evidence implication. The cumulative quality of every prior playbook scenario is materialized in this single deliverable. FINRA 4511, FINRA RN 24-09 / Rule 3110, SEC Rule 17a-3 / 17a-4, SOX §302 / §404, GLBA §501(b), OCC Bulletin 2026-13 (formerly OCC 2011-12), Fed SR 26-2 (formerly SR 11-7), NYDFS 500.06, CFTC 1.31, FFIEC IT examination handbook — all of these regulatory frames may inform what the examiner expects to see. The firm's posture should be: comprehensive, transparent about limits, evidence-rich, and humble about anything it cannot demonstrate.

**Cross-references.** All controls referenced in this playbook · [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) · [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)

---

## §3 Closing Notes

This playbook is a living document. Quarterly review by the Power Platform Admin team and the AI Governance Lead is required. Update triggers include:
- New Microsoft platform features or deprecations affecting Managed Environments
- New regulatory guidance (e.g., new FINRA notices, SEC rule amendments, NYDFS revisions)
- Any Sev1 incident — append the lessons-learned to the relevant scenario and tag the change in the version history
- Feedback from examiner walkthroughs

Pair this playbook with:
- [Portal Walkthrough](./portal-walkthrough.md) — for click-by-click setup
- [PowerShell Setup](./powershell-setup.md) — for automation baseline
- [Verification & Testing](./verification-testing.md) — for evidence-quality test cases
- [Control 2.1 — Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md) — for normative requirements

> **Final reminder.** Nothing in this playbook substitutes for the firm's supervisory, recordkeeping, or model-risk obligations. The procedures **support compliance with** the cited regulations and **aid in** the firm's governance posture. Each remediation should be performed under the firm's change-management discipline, with appropriate Legal / Compliance engagement when the configuration intersects examiner-relevant evidence.

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
