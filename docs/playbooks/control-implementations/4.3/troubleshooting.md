# Control 4.3: Site and Document Retention Management - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 4.3](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md).

---

## Common Issues and Solutions

| Issue | Possible Cause | Resolution |
|-------|---------------|------------|
| **Retention policy not applying to sites** | Policy scope misconfigured or sync delay | Verify SharePoint locations in policy; wait 24-48 hours for propagation; check policy is enabled |
| **Users can delete content under retention** | Retention label not set to "Record" | Enable record declaration on label or use preservation lock; users can delete but content is preserved |
| **Retention labels not visible to users** | Label policy not published to location | Publish label policy to SharePoint locations; wait up to 24 hours for sync |
| **Disposition review not triggering** | Review not configured or reviewers not assigned | Configure disposition review in label settings; assign reviewers with Disposition Management role |
| **Legal hold conflicts with retention** | Hold takes precedence over retention deletion | This is expected behavior; content under hold is never deleted regardless of retention policy |
| **Agent accessing stale content** | Content past freshness threshold | Implement content review workflow; use metadata to flag stale content; configure agent to filter by date |
| **Audit events missing for retention actions** | Unified audit log not enabled | Enable audit logging in Purview portal; retention events appear under "File and page activities" |

---

## Diagnostic Commands

### Check Retention Policy Status

```powershell
# Verify retention policy status and distribution
Get-RetentionCompliancePolicy -Identity "PolicyName" |
    Select-Object Name, Enabled, Mode, DistributionStatus, DistributionResults

# Check for any policy distribution errors
Get-RetentionCompliancePolicy | Where-Object { $_.DistributionStatus -ne "Success" } |
    Select-Object Name, DistributionStatus, DistributionResults
```

### Verify Label Application

```powershell
# Check retention rule configuration
Get-RetentionComplianceRule -Policy "PolicyName" |
    Select-Object Name, RetentionDuration, RetentionComplianceAction, ExpirationDateOption

# Verify label publication
Get-RetentionCompliancePolicy -Identity "LabelPolicyName" |
    Select-Object Name, Enabled, PublishComplianceTag
```

### Check Site Coverage

```powershell
# List all sites without retention policies
Connect-SPOService -Url https://tenant-admin.sharepoint.com

$RetentionPolicies = Get-RetentionCompliancePolicy | Where-Object { $_.SharePointLocation -ne $null }
$CoveredSites = $RetentionPolicies.SharePointLocation | Select-Object -Unique

$AllSites = Get-SPOSite -Limit All
$UncoveredSites = $AllSites | Where-Object { $_.Url -notin $CoveredSites }

Write-Host "Sites without retention coverage: $($UncoveredSites.Count)"
$UncoveredSites | Select-Object Url, Title | Format-Table
```

---

## Escalation Path

| Issue Severity | Escalation Path | SLA |
|---------------|-----------------|-----|
| Policy not applying after 48 hours | SharePoint Admin > Microsoft Support | 2 business days |
| Content deletion despite retention | Compliance Officer > Legal > Microsoft Support | Immediate |
| Audit logging gaps | Security Admin > Purview Support | 1 business day |
| Legal hold conflicts | Legal Department > Compliance | Same day |

---

## Prevention Best Practices

1. **Test policies in a pilot environment** before broad deployment
2. **Document all policy configurations** for audit purposes
3. **Monitor policy distribution status** weekly
4. **Establish regular review cadence** for retention settings
5. **Train site owners** on retention label application
6. **Coordinate with Legal** before making retention policy changes

---

## Related Resources

- [Site lifecycle management overview](https://learn.microsoft.com/en-us/sharepoint/site-lifecycle-management)
- [Retention policies for SharePoint and OneDrive](https://learn.microsoft.com/en-us/purview/retention-policies-sharepoint)
- [Use preservation lock for regulatory requirements](https://learn.microsoft.com/en-us/purview/retention-regulatory-requirements)
- [Disposition of content](https://learn.microsoft.com/en-us/purview/disposition)

---

*Updated: January 2026 | Version: v1.1*
