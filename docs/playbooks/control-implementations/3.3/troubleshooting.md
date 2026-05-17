# Troubleshooting: Control 3.3 - Compliance and Regulatory Reporting

**Last Updated:** April 2026

## Common Issues

| Issue | Likely Cause | Resolution |
|---|---|---|
| Premium AI templates not visible | Tenant lacks A5/E5/G5 entitlement or already consumed 3 free premium templates | Verify entitlement; purchase add-on or pick a different premium template |
| Compliance Manager scores stale | Improvement action evidence not refreshed; data connector paused | Refresh evidence on changed actions; check Settings > Connectors |
| Power Automate flow fails on Compliance Manager call | Graph compliance API not yet GA in your tenant or scope missing | Fall back to portal CSV export; request `ComplianceManager.Read.All` scope |
| Records library does not auto-apply retention label | Label not published, or scope excludes the site | Republish retention label policy with site in scope; wait 24 h |
| `Add-PnPFile` returns 403 | Service account lacks Contribute on the library, or library is on retention hold blocking writes | Grant least-privilege Contribute; check Preservation Hold settings |
| Sovereign tenant returns zero data | Graph or PnP connected to wrong cloud | Pass `-Environment USGov` / `USGovDoD` and verify with `Get-MgContext` |
| Approval emails not delivered | Mail flow rule blocks sender; recipient mailbox on litigation hold | Allow `noreply@microsoft.com`; verify recipient mailbox state |
| Power BI dashboard refresh fails | Dataverse / SharePoint connector credentials expired | Re-authenticate the dataset gateway; rotate service-account credential |

---

## Detailed Troubleshooting

### Issue: Compliance Manager Scores Not Updating

**Symptoms:** Assessment scores in Compliance Manager remain unchanged despite improvement-action evidence updates.

**Diagnostic Steps:**

1. Navigate to **Compliance Manager** > **Assessments** > select assessment > **Improvement actions**.
2. Open a recently updated action and confirm **Implementation status** and **Test status** were saved.
3. Check **Settings** > **Customer managed controls** for any unscored manual controls.
4. Review **Settings** > **Data connectors** for paused or errored connectors.

**Resolution:**

- Manually re-save the action's status fields to trigger rescoring.
- Resume any paused data connectors and wait up to 24 hours for sync.
- For premium AI assessments, confirm your tenant still holds entitlement — entitlement loss does not delete the assessment but freezes scoring.

---

### Issue: Records Retention Label Not Auto-Applied

**Symptoms:** New uploads to `AI-Compliance-Reports/Examination Packages/` do not show the `FSI-Reg-Records-7Year` label.

**Diagnostic Steps:**

1. Open [Microsoft Purview](https://purview.microsoft.com) > **Records management** > **Label policies**.
2. Confirm the policy applying `FSI-Reg-Records-7Year` is **Published** and includes the site URL in scope.
3. Open the SharePoint library > **Library settings** > **Apply label to items in this library** — confirm default label is set.
4. Test by uploading a small file and waiting 5 minutes (label application is asynchronous).

**Resolution:**

- Republish the label policy if scope was edited (changes take up to 24 hours).
- If the default label was missing on the library, set it explicitly — policy-level publishing alone does not always set the library default.
- Confirm the user uploading is **not** an external guest with restricted permissions that block label application.

---

### Issue: Power Automate Flow Fails on Compliance Manager API Call

**Symptoms:** Flow run shows error like `Forbidden` or `BadRequest` when calling Microsoft Graph compliance endpoints.

**Diagnostic Steps:**

1. Open the failed run > expand the failing action > review HTTP response.
2. Check the connection used for the action — it must use a service principal or user with `ComplianceManager.Read.All`.
3. In [Entra Admin Center](https://entra.microsoft.com) > **Enterprise applications**, confirm the connector app has admin consent for the scope.
4. Check whether the API endpoint is GA in your tenant (compliance Graph surface evolves frequently).

**Resolution:**

- Grant the missing Graph scope and re-consent.
- If the endpoint is not yet available in your tenant, switch the flow to use the portal CSV export staged to SharePoint as the data source (documented fallback).
- Pin connector versions in your environment to avoid silent breaking changes.

---

### Issue: SharePoint Archive Upload Returns 403 Forbidden

**Symptoms:** `Add-PnPFile` or Power Automate **Create file** fails with HTTP 403.

**Diagnostic Steps:**

1. Verify the connection account (service account or flow connection) holds **Contribute** or higher on the target library.
2. Check whether the library is in **read-only** mode due to a tenant-level hold or preservation policy.
3. Confirm the file path does not exceed SharePoint URL length limits (400 characters).
4. Check for blocked file types in the tenant blocked-file-types list.

**Resolution:**

- Use a least-privilege service account with **Contribute** on the specific library only — do **not** grant tenant-wide SharePoint Admin to flow connections.
- If a preservation hold blocks new content, work with the eDiscovery team to scope the hold off the report library.
- Shorten file/folder names if URL length is the cause.

---

### Issue: Sovereign Cloud Tenant Returns Zero Data

**Symptoms:** Scripts complete successfully but return empty results in a GCC, GCC High, or DoD tenant.

**Diagnostic Steps:**

1. Run `Get-MgContext` and confirm `Environment` matches your tenant's cloud (`USGov`, `USGovDoD`).
2. For PnP, confirm `Connect-PnPOnline` was called against the correct sovereign URL (e.g., `*.sharepoint.us`).
3. Check the SHA-256 evidence row — it records the resolved environment and operator.

**Resolution:**

- Reconnect with the correct `-Environment` parameter per the [PowerShell Authoring Baseline §3](../../_shared/powershell-baseline.md).
- Add an environment guard at the top of every script that throws when `Get-MgContext` returns the wrong cloud.
- **Do not treat empty results as "all clean"** — empty often means misconnected. This is the single most common false-clean pattern in regulated tenants.

---

### Issue: Approval Emails Not Delivered to CCO

**Symptoms:** Monthly/quarterly approval requests do not arrive at the approver's inbox.

**Diagnostic Steps:**

1. Open the flow run > expand the **Start and wait for an approval** action > confirm approver email address.
2. Check Exchange Online message trace for the approval email.
3. Check the approver's [Approvals app](https://approvals.microsoft.com) — emails sometimes filter out, but the in-app entry remains.

**Resolution:**

- Add `noreply@microsoft.com` and Power Automate sender domains to the safe-senders list.
- Train approvers to use the Approvals app or Teams Approvals channel as the canonical interface — email is a notification, not the source of truth.

---

### Issue: Power BI Dashboard Refresh Fails

**Symptoms:** Scheduled refresh shows **Failed** with credential or gateway errors.

**Diagnostic Steps:**

1. Open the dataset > **Settings** > **Data source credentials** — confirm credentials are valid for each connector.
2. Check the on-premises data gateway status if the dataset uses one.
3. Review refresh history error messages for specific connector failures.

**Resolution:**

- Re-authenticate expired connector credentials (especially OAuth tokens that expire after 90 days for some connectors).
- Use a service-account credential rather than an individual user account so refreshes do not break when a user is deprovisioned.
- Move large datasets to **Premium Per User** or a Premium capacity to lift refresh quota and time limits.

---

## How to Confirm Configuration is Active

### Via Portal (Compliance Manager)

1. [Microsoft Purview](https://purview.microsoft.com) > **Compliance Manager** > **Assessments**.
2. Verify the AI-Agent-Governance assessment group exists with all expected assessments.
3. Confirm at least one improvement action per assessment shows recent evidence attachment.

### Via Portal (SharePoint)

1. Open `AI-Compliance-Reports`.
2. Verify each top-level library exists and contains at least one report from the last 7 days.
3. Open a Weekly report file properties — confirm the retention label is applied.

### Via PowerShell (read-only)

```powershell
# Quick validation
Write-Host "Checking Control 3.3 configuration..." -ForegroundColor Cyan

$ctx = Get-MgContext
Write-Host "Graph: $(if ($ctx) { "$($ctx.TenantId) [$($ctx.Environment)]" } else { 'NOT CONNECTED' })"

try {
    $web = Get-PnPWeb -ErrorAction Stop
    Write-Host "PnP : $($web.Url)"
} catch {
    Write-Host "PnP : NOT CONNECTED"
}

# Recent files in Weekly Reports library
try {
    $items = Get-PnPListItem -List 'Weekly Reports' -PageSize 100 |
        Where-Object { $_.FieldValues.Modified -gt (Get-Date).AddDays(-14) }
    Write-Host "Weekly reports in last 14 days: $($items.Count)"
} catch {
    Write-Host "Weekly Reports library not accessible: $_" -ForegroundColor Yellow
}
```

---

## Escalation Path

| Issue | Escalate To | Response Target |
|---|---|---|
| Report generation failure (single flow) | IT Operations / Power Platform Admin | 4 business hours |
| Compliance Manager score discrepancy | Purview Compliance Admin | 1 business day |
| Records library retention misconfiguration | Purview Records Manager + SharePoint Admin | 1 business day |
| Sovereign cloud misconnection (false-clean risk) | CISO + Compliance Officer | Immediate |
| Examination deadline at risk | CCO + Outside Counsel | Immediate |
| Reg S-P 30-day notification timer concern | CCO + CISO + General Counsel | Immediate |
| Microsoft platform bug or outage | Microsoft Support (premium / unified) | Per support SLA |

> **FSI escalation note:** Any issue that could result in a missed regulatory filing, examination response, or customer notification deadline must be escalated immediately and logged as a control deficiency, regardless of root cause.

---

[Back to Control 3.3](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
