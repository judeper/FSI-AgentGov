# SharePoint Advanced Management Licensing Guide

This guide clarifies SharePoint Advanced Management (SAM) licensing requirements and the features included with Microsoft 365 Copilot licenses.

---

## Licensing Overview

SharePoint Advanced Management features are available through two licensing paths:

| License Path | Cost | Scope |
|--------------|------|-------|
| **Microsoft 365 Copilot** | Included (most features) | One Copilot license assigned activates SAM for entire tenant |
| **Standalone SAM** | $3 per user per month | Required only if no Copilot licenses assigned |

---

## Features Included with Microsoft 365 Copilot License

Organizations with at least one Microsoft 365 Copilot license assigned receive access to most SharePoint Advanced Management features at no additional cost. The list below reflects features available as of this writing; Microsoft may add features over time — check the [SAM documentation](https://learn.microsoft.com/en-us/sharepoint/advanced-management) for the current list:

| Feature | Description | Related Control |
|---------|-------------|-----------------|
| **Restricted Content Discovery (RCD)** | Exclude sites from Copilot discovery | [4.1](../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) |
| **Restricted SharePoint Search (RSS)** | Allow-list of sites accessible to Copilot | [4.1](../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) |
| **Restricted Access Control (RAC)** | Information barriers based on sensitivity labels | [4.1](../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) |
| **Data Access Governance Reports** | Permission and sharing analysis | [4.2](../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md), [4.5](../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md) |
| **Site Access Reviews** | Owner attestation workflows | [4.2](../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) |
| **Site Lifecycle Management** | Inactive site detection and remediation | [4.3](../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md) |
| **Site Ownership Policies** | Orphaned site remediation | [4.3](../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md) |
| **Agent Insights** | AI agent activity monitoring | [4.5](../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md) |
| **Change History** | Administrative action tracking | [4.5](../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md) |
| **Block Download Policy** | Prevent downloads based on conditions | [4.4](../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md) |
| **Conditional Access for SharePoint Sites** | Site-level Conditional Access policies | [4.4](../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md) |

---

## Feature NOT Included with Copilot License

**Restricted Site Creation** requires a standalone SharePoint Advanced Management license. This feature restricts which users can create new SharePoint sites based on group membership.

If your organization requires Restricted Site Creation, you must purchase standalone SAM licenses regardless of Copilot licensing.

---

## Activation Requirements

### Microsoft 365 Copilot Path

1. Assign at least one Microsoft 365 Copilot license to any user in the tenant
2. SAM features activate automatically for the entire tenant within 24 hours
3. No additional configuration required beyond license assignment

### Standalone SAM Path

1. Purchase SAM licenses through Microsoft 365 Admin Center or volume licensing
2. Assign licenses to users who will administer SAM features
3. SAM features activate for the tenant upon first license assignment

---

## Licensing Verification

Verify SAM licensing status:

**SharePoint Admin Center:**

1. Navigate to SharePoint Admin Center
2. Select **Advanced** in the left navigation
3. If features are accessible, SAM is licensed

**PowerShell:**

```powershell
# Check if SAM features are enabled
Get-SPOTenant | Select-Object -Property *AdvancedManagement*
```

---

## Cost Comparison for FSI Organizations

| Scenario | Copilot Path | Standalone SAM Path |
|----------|--------------|---------------------|
| 1,000 users, 100 Copilot licenses | $3,000/month (Copilot only) | +$3,000/month (all users) |
| 5,000 users, 500 Copilot licenses | $15,000/month (Copilot only) | +$15,000/month (all users) |
| 10,000 users, 1,000 Copilot licenses | $30,000/month (Copilot only) | +$30,000/month (all users) |

**Recommendation:** Organizations planning Microsoft 365 Copilot deployment receive significant value from included SAM features. Prioritize SAM governance features in Copilot deployment planning.

---

## Additional Resources

- [SharePoint Advanced Management overview](https://learn.microsoft.com/en-us/sharepoint/advanced-management)
- [Microsoft 365 Copilot licensing](https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-licensing)
- [SharePoint Advanced Management licensing FAQ](https://learn.microsoft.com/en-us/sharepoint/advanced-management#licensing)

---

*Updated: February 2026 | Framework Version: v1.2.45*
