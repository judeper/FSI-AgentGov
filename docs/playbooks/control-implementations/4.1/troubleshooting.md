# Control 4.1: SharePoint Information Access Governance (IAG) — Troubleshooting

> Diagnostic and resolution guidance for [Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md). Organised by symptom.

---

## Quick-Reference Issue Matrix

| Symptom | Most likely cause | First action |
|---|---|---|
| RCD toggle missing or greyed out | No Copilot license assigned in tenant; insufficient role | Verify Copilot license + SharePoint Admin role |
| Copilot still surfaces restricted content | Reindex incomplete; user has recent-interaction history | Wait up to ~72h; isolate test user |
| RAC fails to block user | Wrong group GUID; user is site owner; group sync lag | Re-resolve group via Graph; check owners |
| Audit log empty | Unified Audit Log disabled; search-window too narrow | Enable UAL; widen the search range |
| RSS allow-list ineffective | URL mismatch (case/trailing slash); >100 sites | Re-add canonical URLs; trim list |
| PowerShell connect fails | Stale module; MFA / sovereign-cloud endpoint mismatch | Update module; pass `-Region` |

---

## Issue: Copilot Still Returns Content from a Restricted Site

### Symptoms

After enabling RCD, Microsoft 365 Copilot still surfaces documents or citations from the site for some users.

### Diagnostics

```powershell
Get-SPOSite -Identity 'https://contoso.sharepoint.com/sites/Restricted' |
    Select-Object Url, RestrictContentOrgWideSearch, LastContentModifiedDate
```

- Confirm `RestrictContentOrgWideSearch = True`.
- Note the time RCD was enabled — Semantic Index reindex can take several hours up to ~72 hours for large libraries.
- Check whether the test user has recently *viewed, edited, or shared* the document. RCD scopes org-wide discovery (SharePoint home, Office.com, Bing); it does not override an individual's interaction history.

### Resolution

- Wait for reindex to complete; re-test with a user who has **no** recent interaction with the document.
- Confirm the same content does not exist in another, non-restricted site (duplicate libraries are a common cause).
- If the issue persists past 72 hours with a clean test user, raise a Microsoft support case and supply the audit-log entry as evidence of RCD enablement.

---

## Issue: "Restrict content from Microsoft 365 Copilot" Toggle Is Missing or Greyed Out

### Symptoms

The toggle is not visible in **Site → Settings**, or is visible but disabled.

### Diagnostics

1. Confirm at least one Microsoft 365 Copilot license is assigned in the tenant — RCD is gated on this prerequisite as of the April 2026 Microsoft Learn update.
2. Confirm the signed-in user holds the **SharePoint Admin** role (or is a delegated site collection administrator with RCD delegation enabled).
3. Confirm you are using the modern SharePoint admin centre, not classic site settings.

### Resolution

- Assign a Copilot license to a pilot user, then refresh the admin centre.
- Re-check role assignment in Microsoft Entra; sign out / sign in to refresh tokens.
- If delegation is required, confirm the tenant setting via PowerShell (see [powershell-setup.md](powershell-setup.md)).

---

## Issue: Restricted Access Control (RAC) Is Not Blocking Users

### Symptoms

A user outside the configured Entra security groups can still open the RAC-protected site.

### Diagnostics

```powershell
Get-SPOSite -Identity $SiteUrl |
    Select-Object Url, RestrictedAccessControl, RestrictedAccessControlGroups

Connect-MgGraph -Scopes 'Group.Read.All','Directory.Read.All' -NoWelcome
Get-MgGroup -Filter "displayName eq 'MandA-DealTeam-Alpha'" |
    Select-Object Id, DisplayName
Get-MgGroupMember -GroupId <id> -All
```

- Verify the configured group GUIDs match the intended Entra groups.
- Verify the test user is **not** a site collection administrator — owners retain access regardless of RAC.
- Check whether group membership has propagated (Entra → SharePoint sync can take 15–60 minutes).

### Resolution

- Replace stale GUIDs; reapply RAC with the verified group list.
- Remove the test user from site owners if testing the deny path.
- Re-run the test after group sync completes.

---

## Issue: Audit Log Is Missing IAG Events

### Symptoms

Purview Audit search returns no results for `SiteRestrictedFromOrgSearch` or `RestrictedAccessControlPolicyUpdated` despite confirmed changes.

### Diagnostics

```powershell
Connect-IPPSSession
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled
```

- Confirm `UnifiedAuditLogIngestionEnabled = True`.
- Confirm the search date range is wide enough — events typically appear within minutes but can be delayed up to 24 hours.
- Confirm the operator running the search holds **Purview Compliance Admin** (or equivalent audit-search role).

### Resolution

- Enable the Unified Audit Log if disabled.
- Widen the search window and re-run.
- For sustained delays beyond 24 hours, raise a Microsoft support case.

---

## Issue: Restricted SharePoint Search (RSS) Allow-List Is Not Behaving Correctly

### Symptoms

Copilot accesses content from non-allow-listed sites, or fails to access listed sites.

### Diagnostics

```powershell
Get-SPOTenant | Select-Object EnableRestrictedSearchAllList
Get-SPOTenantRestrictedSearchAllowedList
```

- Confirm RSS is enabled at the tenant.
- Confirm site URLs are **canonical** (no trailing slash; correct case) and unique.
- Confirm the allow-list has not exceeded the documented site cap (current Microsoft Learn value: 100; verify before relying on it).

### Resolution

- Remove and re-add any URLs that do not match the canonical form returned by `Get-SPOSite`.
- Trim the list to the supported maximum.
- Allow up to 24 hours for propagation.

---

## Issue: PowerShell Connection or Cmdlet Failures

### Symptoms

`Connect-SPOService` fails; `Set-SPOSite` returns access-denied or "parameter not found".

### Diagnostics

```powershell
Get-Module Microsoft.Online.SharePoint.PowerShell -ListAvailable |
    Select-Object Name, Version
```

- Confirm the module version meets the baseline minimum.
- Confirm the `-Url` value matches your sovereign cloud (`*.sharepoint.com`, `*.sharepoint.us`, etc.).
- Confirm the operator's account is not blocked by Conditional Access (named-location, device-compliance).

### Resolution

- Update to the pinned module version per [powershell-setup.md](powershell-setup.md).
- For sovereign clouds, pass `-Region ITAR` (GCC High) or `-Region USGovDoD` (DoD) on `Connect-SPOService`.
- Use a workstation that satisfies your Conditional Access posture (PAW / compliant device).

---

## Issue: Bulk RCD Apply Reports Throttling (HTTP 429)

### Symptoms

Repeated `Set-SPOSite` calls fail intermittently with throttling errors.

### Resolution

- Add exponential backoff (per the PowerShell baseline) — start at 5s, double up to a cap of 5 minutes.
- Reduce parallelism to a single thread for mutating cmdlets.
- Stage rollouts in tranches of 50 sites per hour for very large tenants.

---

## Diagnostic Bundle

```powershell
$SiteUrl = 'https://contoso.sharepoint.com/sites/TestSite'

Write-Host '=== IAG Diagnostic Report ===' -ForegroundColor Cyan
$site = Get-SPOSite -Identity $SiteUrl
[pscustomobject]@{
    Url                         = $site.Url
    RCD                         = $site.RestrictContentOrgWideSearch
    RAC                         = $site.RestrictedAccessControl
    RACGroups                   = $site.RestrictedAccessControlGroups
    SensitivityLabel            = $site.SensitivityLabel
    SharingCapability           = $site.SharingCapability
    LastContentModifiedDate     = $site.LastContentModifiedDate
} | Format-List

$tenant = Get-SPOTenant
[pscustomobject]@{
    EnableRestrictedSearchAllList         = $tenant.EnableRestrictedSearchAllList
    DelegateRestrictedAccessControlMgmt   = $tenant.DelegateRestrictedAccessControlManagement
} | Format-List

Get-SPOTenantRestrictedSearchAllowedList | Format-Table -AutoSize
```

---

## Escalation Path

1. **Site owner / SharePoint Admin** — Per-site configuration and reindex questions.
2. **Microsoft 365 Admin / Tenant Admin** — Licensing, tenant-level RSS and delegation settings.
3. **Microsoft Support** — Reindex stalls beyond 72 hours, audit-log gaps beyond 24 hours, suspected service regression.
4. **AI Governance Committee** — Policy exceptions (e.g., temporary RCD disable for an investigation) and Zone 3 attestation issues.

---

[Back to Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
