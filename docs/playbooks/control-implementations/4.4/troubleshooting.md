# Control 4.4: Guest and External User Access Controls — Troubleshooting

> This playbook provides troubleshooting guidance for [Control 4.4](../../../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md). It assumes the configuration in the [Portal Walkthrough](portal-walkthrough.md) and [PowerShell Setup](powershell-setup.md) playbooks has been applied.

---

## Diagnostic Decision Tree

```
Sharing not behaving as expected?
├── Is the tenant SharingCapability the bottleneck?       → See "Tenant vs site hierarchy"
├── Is a sensitivity label overriding site sharing?       → See "Sensitivity labels override sharing"
├── Is Conditional Access blocking the guest sign-in?     → See "Conditional Access conflicts"
├── Is Entra cross-tenant access blocking before SP?      → See "Entra B2B / cross-tenant access"
├── Did the user previously have access that expired?     → See "Guest expiration vs revocation"
└── Is a recent admin change causing drift?               → See "Audit recent configuration changes"
```

---

## Common Issues

| Symptom | Likely Cause | Resolution |
|---------|--------------|------------|
| Cannot share a file externally from a site | Tenant `SharingCapability` is more restrictive than the site setting allows | Check `Get-SPOTenant` first; site sharing cannot exceed tenant. Tighten or relax tenant per policy |
| Sharing UI shows "Specific people" only, no external option | Site set to `ExistingExternalUserSharingOnly` but no existing guests have access | Inviter must add the recipient via a path that creates the guest first (e.g., Entra B2B invitation), or site must be temporarily set to `ExternalUserSharingOnly` per change control |
| Guest user receives invitation but sign-in fails | Conditional Access policy denies non-compliant device or non-MFA session | Review CA policies targeting "Guest or external users"; confirm guest's home tenant supports cross-tenant device compliance |
| Shared link returns "Access denied" after some weeks | `ExternalUserExpireInDays` reached its threshold | Re-invite the guest (creates a new grant + new expiration window). Document business justification if expiration must be relaxed |
| Sharing option grayed out in site UI | User lacks Site Owner / Member or `DisableSharingForNonOwnersStatus = True` | Verify role; if non-owner sharing is disabled (Zone 2 baseline), the site owner must initiate the share |
| External user blocked by domain policy | `SharingDomainRestrictionMode = AllowList` and the recipient's domain is not in the allow-list | Add domain to allow-list with documented business justification, or reject share per policy |
| `Get-SPOExternalUser` returns fewer users than the portal shows | Default `-PageSize` and missing `-Position` cause silent paging issues | Use the paged loop from the PowerShell Setup playbook to enumerate fully |
| `Remove-SPOExternalUser` returns "Cmdlet not recognized" | Cmdlet retired by Microsoft on **July 29, 2024** | Use `Remove-MgUser` from `Microsoft.Graph.Users`; see PowerShell Setup playbook |
| `Search-UnifiedAuditLog` returns suspiciously round number (5,000) | Result set was truncated at the per-call cap | Use session-paginated query (`SessionId` + `SessionCommand ReturnLargeSet`); see PowerShell Setup playbook |
| Site sharing change is "successful" but no effect visible | Propagation lag (typically 5–15 minutes for tenant; up to 60 minutes for some site settings) | Wait and re-verify; confirm propagation via `Get-SPOSite` rather than the portal cache |

---

## Detailed Diagnostics

### 1. Tenant vs site hierarchy

A site's `SharingCapability` is bounded by the tenant's. The effective sharing level is the **most restrictive** of the two.

```powershell
$tenant = Get-SPOTenant
$site   = Get-SPOSite -Identity 'https://contoso.sharepoint.com/sites/SiteName'
[pscustomobject]@{
    TenantSharing      = $tenant.SharingCapability
    SiteSharingRequest = $site.SharingCapability
    Note               = 'Effective sharing = most restrictive of these two'
}
```

If the tenant is `Disabled`, every site is `Disabled` regardless of per-site value.

### 2. Sensitivity labels override sharing

Container sensitivity labels (applied to a site or Microsoft 365 group) can enforce sharing settings that **override** SharePoint Admin Center settings.

```powershell
Get-SPOSite -Identity 'https://contoso.sharepoint.com/sites/SiteName' |
    Select-Object Url, SensitivityLabel, SharingCapability
```

If a label is applied, inspect the label's site & group settings in **Microsoft Purview** > **Information protection** > **Labels**. The label's external-sharing setting and the site's `SharingCapability` must be reconciled — see [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md).

### 3. Conditional Access conflicts

Symptoms: guest can be invited, but cannot sign in or is repeatedly prompted for MFA the home tenant cannot satisfy.

1. Open **Microsoft Entra admin center** > **Protection** > **Conditional Access** > **Sign-in logs**.
2. Filter on the guest's UPN (e.g., `user_partner.com#EXT#@contoso.onmicrosoft.com`).
3. Inspect the failed sign-in's **Conditional Access** tab for the policy that produced the block.
4. Cross-check whether **cross-tenant access settings** in **External Identities** trust the guest's home tenant for MFA / device claims; if not, the guest cannot satisfy the requirement no matter how they authenticate.

See [Microsoft Learn: Cross-tenant access overview](https://learn.microsoft.com/en-us/entra/external-id/cross-tenant-access-overview) for the authoritative trust-claim matrix.

### 4. Entra B2B / cross-tenant access

SharePoint sharing can succeed at the SharePoint layer but fail at the Entra B2B layer if cross-tenant access settings (inbound or outbound) restrict the guest's home tenant.

1. **Microsoft Entra admin center** > **External Identities** > **Cross-tenant access settings**.
2. Inspect both **Default settings** and **Organizational settings** for the guest's home tenant.
3. If the guest's tenant is blocked or restricted, sharing-link issuance may succeed silently while sign-in fails.

### 5. Guest expiration vs revocation

Expiration and revocation are different:

- **Expiration** (`ExternalUserExpireInDays`) revokes a guest's access at the **site** level after the configured days since first access.
- **Revocation** removes the guest **account** from Entra ID.

If a guest's access "stops working" after the expiration window, the guest account often still exists in Entra ID and can be re-invited via the same email. To fully remove, use `Remove-MgUser` (see PowerShell Setup).

### 6. Audit recent configuration changes

```powershell
Connect-IPPSSession
$sessionId = [guid]::NewGuid().ToString()
$events = @()
do {
    $batch = Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) `
        -RecordType SharePointSharingOperation `
        -SessionId $sessionId -SessionCommand ReturnLargeSet -ResultSize 5000
    $events += $batch
} while ($batch.Count -eq 5000)

# Focus on tenant- or site-level sharing setting changes
$events | Where-Object { $_.Operations -match 'Sharing|SiteCollection' } |
    Select-Object CreationDate, UserIds, Operations, AuditData |
    Format-List
```

Cross-reference any unexpected administrative actions against your change-ticket system. Unexplained changes are an incident — escalate per your security operations runbook.

### 7. Test with a different account

Confirm the issue is not user-specific (group membership, license assignment, or a stale Office client cache). Reproduce with:

- A different in-tenant user with equivalent role on the site.
- A clean browser session (private window, no extensions).
- The native Office desktop client, if the issue first appeared in the web client (or vice versa).

---

## Escalation Path

| Severity | Trigger | Owner | SLA |
|----------|---------|-------|-----|
| **P1 — Incident** | Unauthorized external access to regulated content discovered | Security Admin → Compliance Officer → Legal | Immediate (initiate incident response) |
| **P2 — Service-affecting** | Tenant-wide sharing change failed or partially applied | SharePoint Admin → Microsoft Support (Premier) | 1 business day |
| **P2 — Audit-blocking** | Evidence artifact missing, corrupt, or fails SHA-256 verification | SharePoint Admin → Compliance Officer | 1 business day |
| **P3 — Functional** | Conditional Access conflict for a single guest population | Entra Security Admin → Security Architect | 2 business days |
| **P3 — Functional** | Domain restriction blocking an approved partner | SharePoint Admin → Sponsoring business owner | Same day |
| **P4 — Hygiene** | Expired guest accounts requiring cleanup | SharePoint Admin (scheduled) | Quarterly access review |

---

## Prevention Practices

1. **Snapshot before mutating.** Every tenant or site change should produce a `before` JSON. The PowerShell Setup playbook codifies this.
2. **Run `-WhatIf` first.** This catches unexpected scope before production impact.
3. **Communicate change windows.** Site owners should know when tenant sharing posture changes; surprise lockouts are a frequent help-desk source.
4. **Quarterly guest access reviews** (see [Control 4.2](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md)).
5. **Annual cross-tenant access settings review** for partner trust drift.
6. **Coordinate with the DLP and sensitivity-label owners** ([Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)) so layered controls are reconciled — conflicts between label-enforced and site-enforced sharing are a common audit finding.
7. **Treat unexplained sharing-config changes as incidents** until proven otherwise.

---

## Related Resources

- [Microsoft Learn — Manage sharing settings in SharePoint](https://learn.microsoft.com/en-us/sharepoint/turn-external-sharing-on-or-off)
- [Microsoft Learn — External sharing overview](https://learn.microsoft.com/en-us/sharepoint/external-sharing-overview)
- [Microsoft Learn — Guest access expiration](https://learn.microsoft.com/en-us/sharepoint/turn-external-sharing-on-or-off#guest-access-to-a-site-or-onedrive-will-expire-automatically)
- [Microsoft Learn — Data access governance reports](https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports)
- [Microsoft Learn — Cross-tenant access overview](https://learn.microsoft.com/en-us/entra/external-id/cross-tenant-access-overview)
- [Microsoft Learn — Set-SPOTenant cmdlet reference](https://learn.microsoft.com/en-us/powershell/module/microsoft.online.sharepoint.powershell/set-spotenant)
- [Microsoft Learn — Remove-MgUser cmdlet reference](https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.users/remove-mguser)

---

[Back to Control 4.4](../../../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
