# Troubleshooting: Control 1.3 - SharePoint Content Governance and Permissions

**Last Updated:** May 2026
**Audience:** SharePoint Admin, AI Governance Lead, Service Desk Tier 2/3

---

## Quick reference

| Issue | Likely cause | Fix |
|---|---|---|
| Agent or Copilot returns content the user shouldn't see | `Everyone` / `Everyone except external users` claim still on site; site is in Restricted SharePoint Search allow-list; container label not applied | Remove broad claims (PowerShell §3); review allow-list; apply container label |
| Authorized user gets "no information found" from agent | Service / user account not in RAC group; site under RCD with no direct grant; sensitivity label blocks unmanaged-device access | Add user to RAC group; grant direct access; verify device compliance |
| Container label not appearing on site | Label policy not published to user's audience; site is non-group-connected; group already has a different assigned label | Publish policy to label-creator audience; convert site to group-connected or apply via UI; clear existing assigned label |
| External sharing still possible despite tenant `Disabled` | Site-level setting more permissive (sites can be more restrictive than tenant, never more permissive — check for older site that retained value before tenant tightened) | Re-apply `Set-SPOSite -SharingCapability Disabled`; verify no scripts reset values |
| RAC blocks legitimate Power Automate / agent service flows | Service account / managed identity not in RAC group | Add the service identity to the bound RAC group; never disable RAC as a workaround |
| RCD not suppressing content from Copilot | Propagation delay; user has direct access via another path; RCD applied to wrong site | Wait up to 24h; confirm via `Get-SPOSite -Detailed`; check user's effective permissions |
| `Set-SPOSite -RestrictedAccessControl` parameter not found | Module version too old or cmdlet not yet available | Pin newer SPO Management Shell; use the SharePoint admin center flyout as fallback |
| Access review not sending notifications | Reviewers have no mailbox / are guest accounts; mail-flow restricted; review still queued | Confirm reviewers are licensed; check Exchange Online flow; wait for cycle start |
| DAG report shows broad sharing on a site you remediated | Report is cached/scheduled, not real-time | Force re-run from the report page; expect 24–48h refresh |
| Restricted SharePoint Search blocks Copilot for sanctioned sites | Site missing from the allow-list (max 100) | Add site or, better, complete RAC/RCD remediation and disable Restricted SharePoint Search |
| `Remove-SPOUser` fails with "user does not exist" for `Everyone except external users` | LoginName claim format is tenant-specific (`spo-grid-all-users/<tenant>`) | Use `Get-SPOUser -Site $url \| Where-Object LoginName -like '*spo-grid-all-users*'` to discover the exact claim |

---

## Issue: Microsoft 365 Copilot or a Copilot Studio agent returns content the user should not see

### Symptoms
- A user prompts Copilot or an agent and receives text quoting documents from a site that should be invisible to that user.
- DAG report or audit log shows the site as broadly shared.

### Likely causes
1. The site still has `Everyone except external users` (`spo-grid-all-users`) on a SharePoint group.
2. Microsoft 365 Copilot grounding pulled the content via the user's existing direct or transitive permissions (Copilot does not bypass permissions, but it surfaces anything the user already has rights to).
3. The site is in the Restricted SharePoint Search allow-list inadvertently.
4. RCD was expected but never enabled on the site.

### Diagnostic steps
1. Identify the source URL of the surfaced content — Copilot citations include the file path. Open the site in an InPrivate session as the test user.
2. Inventory the user's effective permission to that site:
    ```powershell
    Get-SPOUser -Site $SiteUrl -Limit All | Where-Object LoginName -match $UserUpn
    Get-SPOUser -Site $SiteUrl -Limit All | Where-Object LoginName -match 'spo-grid-all-users|^c:0\(\.s\|true$'
    ```
3. Check RCD and RAC state:
    ```powershell
    Get-SPOSite -Identity $SiteUrl -Detailed | Select-Object Url, SharingCapability, SensitivityLabel, RestrictedAccessControl, RestrictContentOrgWideSearch
    ```
4. Confirm whether the site is in the Restricted SharePoint Search allow-list (note: RSS is retiring — new enablement blocked from July 31, 2026; prefer RCD):
    ```powershell
    Get-SPOTenantRestrictedSearchMode
    Get-SPOTenantRestrictedSearchAllowedList
    ```

### Fix
1. Remove the broad claim using the `Remove-BroadClaim` function in `powershell-setup.md` §3.
2. If the site is Zone 3, enable RAC (binding to a named group) and RCD.
3. Remove the site from Restricted SharePoint Search if it was added in error.
4. After remediation, re-run Test 6 in `verification-testing.md` with the same prompt and capture evidence of the corrected behavior.

---

## Issue: Authorized user / agent service account cannot retrieve content

### Symptoms
- A user who legitimately needs access reports "I don't have access" or the agent returns "no information found" for valid content.
- A Power Automate flow / agent service identity returns 401/403 against a site.

### Likely causes
1. Restricted Access Control is enabled on the site and the user / service identity is not in the bound group.
2. Restricted Content Discovery is enabled and the user has no direct grant (RCD doesn't block access, but if there was no direct grant the user never had access in the first place).
3. The container sensitivity label has **Block access from unmanaged devices** enabled and the device is not Intune-compliant.
4. A Conditional Access policy is blocking the service principal.

### Diagnostic steps
1. Confirm RAC binding:
    ```powershell
    Get-SPOSite -Identity $SiteUrl | Select-Object RestrictedAccessControl, RestrictedAccessControlGroups
    # Then inspect the bound group membership in Entra
    Get-MgGroupMember -GroupId <bound-group-id>
    ```
2. Check the user's effective permissions:
    - SharePoint admin center → site → **Site permissions** → **Check permissions** for the user.
3. Check the container label's protection settings in Purview → **Information protection** → **Labels** → select label → **Edit** → Site & group settings.
4. Check Entra sign-in logs for the user / service principal to identify any Conditional Access block.

### Fix
1. Add the user (or service identity) to the RAC-bound group.
2. If the device-compliance label setting is the cause, either issue a managed device or relax the label to `Allow limited, web-only access` for Zone 2 use cases.
3. For service principals, use a Conditional Access exclusion specifically scoped to that workload identity (do not exclude the entire app).

---

## Issue: Container sensitivity label not appearing on a site

### Symptoms
- The sensitivity dropdown in the SharePoint admin center → site **Settings** flyout doesn't show the desired label.
- `Get-SPOSite -Detailed` returns a blank `SensitivityLabel`.
- A Graph `PATCH /groups/{id}` with `assignedLabels` returns 400 or 403.

### Likely causes
1. The label policy is not published to an audience that includes the user attempting to apply it.
2. The site is not group-connected (classic site, communication site without group). Container labels require an associated Microsoft 365 group or Entra security identity.
3. The group already has an `assignedLabels` value and the new value conflicts with policy assignment rules.
4. The label is not configured for **Groups & sites** scope.

### Diagnostic steps
1. In Purview → **Information protection** → **Label policies**, confirm the policy that publishes the label includes the admin user's account in its scope.
2. Check the label scope in Purview → **Labels** → open label → confirm `Groups & sites` is enabled.
3. Inspect the site:
    ```powershell
    $site = Get-SPOSite -Identity $url -Detailed
    $site.GroupId    # 00000000-0000-0000-0000-000000000000 means non-group
    Get-MgGroup -GroupId $site.GroupId -Property assignedLabels | Select -ExpandProperty assignedLabels
    ```

### Fix
1. Re-publish the label policy with the correct audience; allow up to 24 hours for propagation.
2. For non-group sites, either convert to a group-connected site (preferred for Zone 3) or apply the label exclusively at the file/library level via DLP / default library label.
3. Clear existing `assignedLabels` via Graph before applying a new one if a conflict exists.

---

## Issue: External sharing still works despite tenant settings

### Symptoms
- A user successfully shares a document externally even though tenant `SharingCapability = Disabled`.

### Likely causes
1. The site-level `SharingCapability` was set to a more permissive value before the tenant was tightened, and SharePoint preserves the **lesser** of the two — but only when the tenant value is **more** permissive than the site. If a site shows `SharingCapability=Disabled` after tightening, it is correctly blocked. If it still shows a more permissive value, the tenant change did not propagate or the site was excluded.
2. The user is a Site Collection Admin and bypassed standard sharing UI via API.
3. A tenant-level B2B Direct Connect policy or cross-tenant access policy is permitting the share through Teams shared channels rather than SharePoint sharing.

### Diagnostic steps
```powershell
$tenant = Get-SPOTenant
$site   = Get-SPOSite -Identity $SiteUrl -Detailed
"Tenant: $($tenant.SharingCapability) | Site: $($site.SharingCapability)"
Get-SPOSite -Identity $SiteUrl -Detailed | Select Url, AllowDownloadingNonWebViewableFiles, ConditionalAccessPolicy
```
Check the SharePoint audit log for `SharingInvitationCreated` and `SharingSet` operations on the document to identify the actual sharing path.

### Fix
1. Re-apply the desired site-level `SharingCapability`:
    ```powershell
    Set-SPOSite -Identity $SiteUrl -SharingCapability Disabled
    ```
2. Audit Site Collection Admins; remove non-admin users from that role.
3. If sharing is occurring via Teams shared channels, address at the Entra cross-tenant access policy level; SharePoint sharing controls do not govern Teams shared channels.

---

## Issue: `Set-SPOSite -RestrictedAccessControl` or RAC cmdlet not available

### Symptoms
- PowerShell error: `A parameter cannot be found that matches parameter name 'RestrictedAccessControl'`.

### Likely causes
1. The pinned `Microsoft.Online.SharePoint.PowerShell` version predates the RAC GA cmdlet surface.
2. SharePoint Advanced Management is not licensed in the tenant.
3. The site is not eligible for RAC (must be group-connected with stable membership).

### Fix
1. Upgrade to a CAB-approved version of SPO Management Shell that exposes the RAC parameters:
    ```powershell
    Get-Module Microsoft.Online.SharePoint.PowerShell -ListAvailable
    Get-Help Set-SPOSite -Parameter RestrictedAccessControl -ErrorAction SilentlyContinue
    Get-Help Set-SPOSite -Parameter AddRestrictedAccessControlGroups -ErrorAction SilentlyContinue
    ```
    Enable and bind with `Set-SPOSite -Identity $SiteUrl -RestrictedAccessControl $true` followed by `Set-SPOSite -Identity $SiteUrl -AddRestrictedAccessControlGroups <GUIDs>` (up to 10 groups). The legacy `Set-SPOSiteGroup -Identity 'RestrictedAccessControlGroups'` approach is **not** the supported surface — use the `-AddRestrictedAccessControlGroups` / `-RestrictedAccessControlGroups` / `-RemoveRestrictedAccessControlGroups` parameters.
2. Verify SAM licensing in the Microsoft 365 admin center → **Billing** → **Licenses**. SAM ships with Microsoft 365 Copilot or as a standalone SKU.
3. If the site is non-group-connected, fall back to the SharePoint admin center flyout UI (which uses the same back-end API but accepts a wider input set) or convert the site to a group-connected site.

---

## Issue: Restricted Content Discovery does not suppress content from Copilot

### Symptoms
- After enabling RCD, Microsoft 365 Copilot still returns content from the site for users who have direct access.

### Cause
RCD suppresses sites from **organization-wide** search and Copilot grounding for users who do **not** have direct permission. Users with direct site permission can still ground Copilot against that site — that is by design. RCD is the wrong control for "I want to hide this site from its own members". For that scenario, use RAC or remove user permissions.

### Fix
1. Inventory who has direct access to the site:
    ```powershell
    Get-SPOUser -Site $SiteUrl -Limit All | Format-Table LoginName, IsSiteAdmin, Groups
    ```
2. If the goal is to remove the site from Copilot grounding for everyone, also enable RAC bound to a small named group and remove the broader grants.
3. Allow up to 24 hours for search-index changes to propagate after permission changes.

---

## Issue: Access review not sending notifications or never completing

### Symptoms
- Reviewers report no email; review status remains `In progress` after the duration window.

### Likely causes
1. Reviewer is a guest or service account without a mailbox.
2. Reviewer mailbox is on litigation hold but unlicensed for Exchange Online.
3. The review was created against a dynamic group that has no current members.
4. Mail-flow rules (Exchange Online transport rules) are quarantining `noreply@accesscontrol.windows.net` notifications.

### Diagnostic steps
1. Entra admin center → **Identity Governance** → **Access reviews** → **Reviews** → open the instance → **History** tab — review the per-user notification status.
2. Confirm reviewer licensing:
    ```powershell
    Get-MgUser -UserId $ReviewerUpn -Property AssignedLicenses, MailEnabled, UserType
    ```
3. Run an Exchange Online message trace for the reviewer.

### Fix
1. Replace mailbox-less reviewers with a governance group whose members are all licensed users.
2. Adjust transport rules to allow Microsoft notification senders.
3. Add a backup reviewer (typically the AI Governance Lead) on the access review definition.

---

## How to confirm the configuration is active end-to-end

### Via portal
1. SharePoint admin center → **Policies** → **Sharing** — verify tenant baseline.
2. SharePoint admin center → **Active sites** → select site → **Settings** flyout — verify Sensitivity, RAC, RCD.
3. Microsoft Purview → **Data Loss Prevention** → confirm `FSI-DLP-SharePoint-AgentGrounding` is in `Enforce`.
4. Microsoft Entra → **Identity Governance** → **Access reviews** — confirm cycle status.

### Via PowerShell
```powershell
$Url = 'https://contoso.sharepoint.com/sites/Agent-CustomerService'
$tenant = Get-SPOTenant
$site   = Get-SPOSite -Identity $Url -Detailed
$broad  = Get-SPOUser -Site $Url -Limit All | Where-Object LoginName -match 'spo-grid-all-users|^c:0\(\.s\|true$'

[PSCustomObject]@{
    Url                          = $Url
    TenantSharingCapability      = $tenant.SharingCapability
    SiteSharingCapability        = $site.SharingCapability
    SiteSensitivityLabel         = $site.SensitivityLabel
    RestrictedAccessControl      = $site.RestrictedAccessControl
    RestrictedAccessControlGroups = ($site.RestrictedAccessControlGroups -join ', ')
    RestrictContentOrgWideSearch = $site.RestrictContentOrgWideSearch
    BroadClaimCount              = ($broad | Measure-Object).Count
} | Format-List
```

A healthy Zone 3 site returns: tenant `Disabled`, site `Disabled`, label set, `RestrictedAccessControl=$true` with at least one bound group in `RestrictedAccessControlGroups`, `RestrictContentOrgWideSearch=$true`, `BroadClaimCount=0`.

---

## Escalation path

1. **SharePoint Admin** — site configuration, sharing, RAC/RCD, DAG reports.
2. **Purview Info Protection Admin** — sensitivity label authoring and policy publication.
3. **Purview Compliance Admin** — DLP policy authoring and incident triage.
4. **Entra Identity Governance Admin** — access review configuration and notification flow.
5. **AI Governance Lead** — agent grounding inventory disputes; sanctioned-source decisions.
6. **Compliance Officer** — regulatory interpretation, evidence sufficiency for FINRA / SEC examinations.
7. **Microsoft Support** — platform bugs, RAC API regressions, SAM licensing issues.

---

[Back to Control 1.3](../../../controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
