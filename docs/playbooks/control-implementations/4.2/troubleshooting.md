# Troubleshooting: Control 4.2 - Site Access Reviews and Certification

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Data access governance reports not available | SharePoint Advanced Management not licensed | Verify SAM Plan 1 license is assigned; navigate to M365 Admin Center > Billing to confirm |
| Site attestation policy not sending notifications | Email settings misconfigured or owners not defined | Verify site owners are assigned; check notification settings in policy; review mail flow rules |
| Access review not starting automatically | Recurrence pattern misconfigured | Verify recurrence settings in review definition; check start date is not in the past |
| Decisions not being auto-applied | Auto-apply disabled or permissions insufficient | Enable autoApplyDecisionsEnabled in review settings; verify service principal has permissions |
| Export fails with permission error | Insufficient Graph API permissions | Ensure AccessReview.ReadWrite.All scope is consented; reconnect with appropriate scopes |
| Site owners not receiving attestation requests | Owner property not set on site | Use Get-SPOSite to verify owner; use Set-SPOSite -Owner to assign |

---

## Detailed Troubleshooting

### Issue: Data Access Governance Reports Not Available

**Symptoms:** Reports section shows error or "Get started" never completes.

**Diagnostic Steps:**

1. Verify SharePoint Advanced Management license:
   - Navigate to M365 Admin Center > Billing > Licenses
   - Confirm "SharePoint Advanced Management" is assigned

2. Check report generation status:
   - Reports can take several hours to generate on first run
   - Large tenants may take longer

3. Verify admin permissions:
   - Must have SharePoint Admin or Entra Global Admin role

**Resolution:**
- Confirm license assignment
- Wait up to 24 hours for initial report generation
- Contact Microsoft support if issue persists after 48 hours

---

### Issue: Site Attestation Policy Not Sending Notifications

**Symptoms:** Site owners not receiving attestation request emails.

**Diagnostic Steps:**

1. Verify site owners are assigned:
   ```powershell
   Get-SPOSite -Identity "https://tenant.sharepoint.com/sites/SiteName" |
       Select-Object Url, Owner, SecondaryContact
   ```

2. Check notification settings in policy:
   - Navigate to Policies > Site lifecycle management > Site attestation policies
   - Verify notification days are configured

3. Check email routing:
   - Verify owner email addresses are valid
   - Check spam/junk folders
   - Review Exchange mail flow rules

**Resolution:**
- Assign owners to all sites requiring attestation
- Verify notification settings in policy
- Check email delivery (may be blocked by mail rules)

---

### Issue: Access Review Not Starting Automatically

**Symptoms:** Scheduled access review shows "Not started" status.

**Diagnostic Steps:**

1. Verify recurrence pattern:
   ```powershell
   $review = Get-MgIdentityGovernanceAccessReviewDefinition -AccessReviewScheduleDefinitionId "review-id"
   $review.Settings.Recurrence | ConvertTo-Json
   ```

2. Check start date:
   - Start date must be in the past or present for review to begin
   - Future start dates will delay first instance

3. Verify review is enabled:
   ```powershell
   $review | Select-Object DisplayName, Status
   ```

**Resolution:**
- Update recurrence settings if misconfigured
- Adjust start date if needed
- Ensure review status is "InProgress" not "NotStarted"

---

### Issue: Decisions Not Being Auto-Applied

**Symptoms:** Access review completes but denied users still have access.

**Diagnostic Steps:**

1. Verify auto-apply setting:
   ```powershell
   $review = Get-MgIdentityGovernanceAccessReviewDefinition -AccessReviewScheduleDefinitionId "review-id"
   $review.Settings.AutoApplyDecisionsEnabled
   ```

2. Check for pending decisions:
   ```powershell
   $instances = Get-MgIdentityGovernanceAccessReviewDefinitionInstance `
       -AccessReviewScheduleDefinitionId "review-id"
   $instances | Select-Object Status
   ```

3. Verify service principal permissions:
   - Auto-apply requires appropriate permissions to modify group membership

**Resolution:**
- Enable autoApplyDecisionsEnabled in review settings
- Verify all decisions are submitted (not NotReviewed)
- Check service principal has Directory.ReadWrite.All permission

---

### Issue: Site Owners Not Receiving Attestation Requests

**Symptoms:** Attestation policy is active but owners report no notifications.

**Diagnostic Steps:**

1. Verify Owner property is set:
   ```powershell
   Get-SPOSite -Limit All | Where-Object { [string]::IsNullOrEmpty($_.Owner) } |
       Select-Object Url, Title
   ```

2. Check policy scope:
   - Verify site matches policy criteria (sensitivity label, URL pattern)

3. Verify mail delivery:
   - Check owner's mailbox (including spam/junk)
   - Review Exchange message trace

**Resolution:**
- Assign owners: `Set-SPOSite -Identity $url -Owner "user@domain.com"`
- Verify site matches attestation policy scope
- Check email delivery via Exchange admin center

---

## Diagnostic Commands

```powershell
# Comprehensive access review health check
Write-Host "=== Access Review Diagnostic ===" -ForegroundColor Cyan

Connect-MgGraph -Scopes "AccessReview.Read.All"

# List all access reviews with status
Get-MgIdentityGovernanceAccessReviewDefinition |
    Select-Object DisplayName, Status, CreatedDateTime |
    Format-Table

# Check specific review details
$reviewId = "your-review-id"
$review = Get-MgIdentityGovernanceAccessReviewDefinition -AccessReviewScheduleDefinitionId $reviewId

Write-Host "`nReview: $($review.DisplayName)" -ForegroundColor Yellow
Write-Host "  Status: $($review.Status)"
Write-Host "  Auto-apply: $($review.Settings.AutoApplyDecisionsEnabled)"
Write-Host "  Default decision: $($review.Settings.DefaultDecision)"
Write-Host "  Duration: $($review.Settings.InstanceDurationInDays) days"

# Check instances
$instances = Get-MgIdentityGovernanceAccessReviewDefinitionInstance -AccessReviewScheduleDefinitionId $reviewId
Write-Host "`nInstances:" -ForegroundColor Yellow
$instances | ForEach-Object {
    Write-Host "  $($_.Id) - Status: $($_.Status), End: $($_.EndDateTime)"
}
```

---

## Escalation Path

1. **Level 1:** SharePoint Admin - Report generation and policy configuration
2. **Level 2:** Identity Governance Administrator - Access review workflows in Entra ID
3. **Level 3:** Microsoft Support - Product issues or feature limitations
4. **Level 4:** AI Governance Committee - Policy exceptions and review scope decisions

---

## How to Confirm Configuration is Active

### Via SharePoint Admin Portal

1. Navigate to **Reports** > **Data access governance**
2. Verify reports show recent data
3. Navigate to **Policies** > **Site lifecycle management**
4. Verify attestation policy shows "Active" status

### Via Entra Admin Portal

1. Navigate to **Identity governance** > **Access reviews**
2. Verify review shows "InProgress" or scheduled status
3. Check recent instances completed successfully

### Via PowerShell

```powershell
# Quick status check
Connect-MgGraph -Scopes "AccessReview.Read.All"
Connect-SPOService -Url "https://yourtenant-admin.sharepoint.com"

# Check access reviews
$reviews = Get-MgIdentityGovernanceAccessReviewDefinition
Write-Host "Access Reviews: $($reviews.Count)" -ForegroundColor Cyan

# Check site ownership
$sites = Get-SPOSite -Limit All | Where-Object { $_.Template -notlike "*SPSPERS*" }
$orphaned = ($sites | Where-Object { [string]::IsNullOrEmpty($_.Owner) }).Count
Write-Host "Sites without owners: $orphaned" -ForegroundColor $(if ($orphaned -gt 0) { "Yellow" } else { "Green" })
```

---

[Back to Control 4.2](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
