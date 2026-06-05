# Control 4.3: Site and Document Retention Management - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 4.3](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md).

---

## Common Issues and Solutions

| Issue | Likely Cause | Resolution |
|-------|--------------|------------|
| **Retention policy not applying to sites** | Policy scope misconfigured (URL typo, wildcard used), or normal propagation delay | Verify exact `SharePointLocation` URLs (no wildcards supported); confirm `Enabled = True` and `DistributionStatus = Success`; allow up to 24–48 hours for full propagation |
| **`DistributionStatus = Pending` for > 48 hours** | Backend deployment failure or invalid location | Run `Get-RetentionCompliancePolicy -Identity "<name>" \| Select-Object DistributionResults` to surface per-location errors; remove offending locations and re-add |
| **Users can permanently delete content under retention** | Label is not a Record / policy missing | Switch label to **Record** (`-IsRecordLabel $true`) or apply a retention policy that overrides user delete; for absolute immutability use **Regulatory Record** (irreversible — coordinate with Legal) |
| **Retention labels not visible to users** | Label-publishing policy not yet propagated, or location not included | Publish the label policy to the SharePoint/OneDrive locations; allow up to 24 hours; users may need to refresh sign-in |
| **Disposition review not triggering on expiry** | Review not configured, or no reviewers assigned | Configure disposition review on the label and assign reviewers with the **Disposition Management** role group in Purview |
| **Preservation Lock cannot be removed** | Working as designed — Preservation Lock is irreversible | The policy can be **extended** in scope or duration; it cannot be removed, disabled, or shortened — see SEC 17a-4(f) |
| **Legal hold prevents retention deletion** | Working as designed — holds always override retention | Confirm with eDiscovery owner; release the hold if no longer needed and disposition can resume |
| **Agent surfacing stale content** | Content past business freshness, but still within retention | Apply Restricted Content Discovery (Control 4.1) and metadata-based filtering on the agent's knowledge source; do **not** shorten retention to remove content from agent surface |
| **Audit events missing for retention actions** | Unified audit log disabled, or audit query scope wrong | Confirm audit logging is on (Control 1.7); search the Purview Audit log under **File and page activities** and **Compliance setting changes** |
| **Inactive site policy not detecting sites** | Site recently active, or policy scope filter excludes site template | Confirm inactivity threshold met (last access date), and that template/sensitivity filter does not exclude site; SAM evaluates daily but updates can lag 24 h |
| **`-SharePointLocation` rejects wildcard URL** | Wildcards not supported on this parameter | List explicit URLs, or use `-SharePointLocation All` to scope to every SPO site |

---

## Diagnostic Commands

### Check Retention Policy Status

```powershell
# Verify retention policy status, distribution, and lock state
Get-RetentionCompliancePolicy -Identity "PolicyName" |
    Select-Object Name, Enabled, Mode, DistributionStatus, DistributionResults, RestrictiveRetention

# Surface any policies that failed to deploy
Get-RetentionCompliancePolicy |
    Where-Object { $_.DistributionStatus -ne "Success" } |
    Select-Object Name, DistributionStatus, DistributionResults
```

### Verify Rules and Labels

```powershell
# Confirm rule attached to the policy
Get-RetentionComplianceRule -Policy "PolicyName" |
    Select-Object Name, RetentionDuration, RetentionComplianceAction, ExpirationDateOption

# Confirm published labels and their record status
Get-ComplianceTag |
    Select-Object Name, RetentionDuration, RetentionAction, IsRecordLabel, Regulatory
```

### Check Site Coverage Gaps

```powershell
Connect-SPOService -Url https://contoso-admin.sharepoint.com

$RetentionPolicies = Get-RetentionCompliancePolicy | Where-Object { $_.SharePointLocation }
$CoveredUrls       = $RetentionPolicies.SharePointLocation | Select-Object -Unique

$AllSites          = Get-SPOSite -Limit All
$UncoveredSites    = $AllSites | Where-Object { $_.Url -notin $CoveredUrls -and $CoveredUrls -notcontains 'All' }

Write-Host "Sites without retention coverage: $($UncoveredSites.Count)"
$UncoveredSites | Select-Object Url, Title, Template | Format-Table
```

### Check Audit Events for Retention Actions

```powershell
# Recent retention-related audit events (requires Purview Audit Admin/Reader)
Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) `
    -Operations FileDeletedFirstStageRecycleBin, FileDeletedSecondStageRecycleBin, ComplianceSettingChanged `
    -ResultSize 5000 |
    Select-Object CreationDate, UserIds, Operations, AuditData
```

---

## Escalation Path

| Issue Severity | Escalation Path | SLA |
|----------------|------------------|-----|
| Policy not applying after 48 hours | SharePoint Admin → Microsoft Support (Premier / Unified) | 2 business days |
| Content deletion despite active retention or legal hold | Compliance Officer → Legal → Microsoft Support | Immediate |
| Audit logging gaps for retention actions | Security Admin → Purview Support | 1 business day |
| Preservation Lock applied in error | Legal Department → Microsoft Support — note that Preservation Lock cannot be reversed; escalation focuses on impact mitigation | Same day |

---

## Prevention Best Practices

1. **Pilot every retention policy** in a non-production scope (single test site or OneDrive) before broad publication.
2. **Pin module versions** per the [PowerShell Authoring Baseline §1](../../_shared/powershell-baseline.md); record the pinned version in the change ticket.
3. **Use `-WhatIf`** on every mutating cmdlet before running for real; capture before/after snapshots per baseline §3.
4. **Apply Preservation Lock only after** at least one full review cycle has confirmed scope and duration are correct — it is irreversible.
5. **Coordinate with Legal and the eDiscovery owner** (Control 1.19) before publishing or modifying any policy that may interact with active holds.
6. **Train site owners** on retention label application and the meaning of Preservation Hold Library.
7. **Run the coverage report monthly**: every Copilot/agent knowledge source site without a retention policy is a finding.
8. **Land all evidence** in WORM-configured storage with SHA-256 hashes recorded in `manifest.json` per baseline §4.

---

## Related Resources

- [Site lifecycle management overview](https://learn.microsoft.com/en-us/sharepoint/site-lifecycle-management)
- [Retention policies for SharePoint and OneDrive](https://learn.microsoft.com/en-us/purview/retention-policies-sharepoint)
- [Use preservation lock for regulatory requirements](https://learn.microsoft.com/en-us/purview/retention-regulatory-requirements)
- [Disposition of content](https://learn.microsoft.com/en-us/purview/disposition)
- [Records Management in Microsoft Purview](https://learn.microsoft.com/en-us/purview/records-management)

---

[Back to Control 4.3](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
