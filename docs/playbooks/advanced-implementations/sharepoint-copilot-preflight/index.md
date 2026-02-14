# SharePoint Governance Pre-Flight Checklist for Microsoft 365 Copilot

This playbook provides a comprehensive pre-deployment checklist for FSI organizations preparing SharePoint environments for Microsoft 365 Copilot deployment.

---

## Overview

Microsoft 365 Copilot inherits user permissions when accessing SharePoint content. This means existing permission gaps become material risks when Copilot makes content more discoverable. Complete this checklist before assigning Copilot licenses to production users.

**Estimated Effort:** 2-4 weeks for initial assessment, ongoing for remediation
**Required Roles:** SharePoint Admin, Purview Compliance Admin, Security Admin

---

## Phase 1: Pre-Deployment Permission Audit

### 1.1 Content Shared with EEEU

**Priority: CRITICAL**

Content shared with "Everyone Except External Users" (EEEU) is accessible to all internal users and represents the highest-risk oversharing scenario.

- [ ] Run DAG "Content Shared with EEEU" report in SharePoint Admin Center
- [ ] Export findings to Excel for tracking
- [ ] Categorize sites by data sensitivity (PII, financial, regulated)
- [ ] Create remediation plan with target dates
- [ ] Remove EEEU permissions or apply RCD to sensitive sites
- [ ] Re-run report to verify remediation

**Location:** SharePoint Admin Center > Reports > Data access governance > Content shared with "Everyone except external users"

### 1.2 Site Permissions Analysis

- [ ] Run Site Permissions report identifying sites with >1,000 users
- [ ] Run Site Permissions report identifying sites with broken inheritance
- [ ] Review sites with numerous permission levels (>10)
- [ ] Document business justification for broadly-shared sites
- [ ] Remediate unnecessary broad permissions

**Location:** SharePoint Admin Center > Reports > Data access governance > Site permissions

### 1.3 Site Permissions for Users (Pilot Users)

For each pilot user receiving Copilot:

- [ ] Run Site Permissions for Users report
- [ ] Review all accessible sites for appropriateness
- [ ] Identify unexpected access (legacy permissions, group memberships)
- [ ] Remediate inappropriate access before Copilot assignment

**Location:** SharePoint Admin Center > Reports > Data access governance > Site permissions for users

### 1.4 Sharing Links Audit

- [ ] Run Sharing Links report in SharePoint Admin Center
- [ ] Identify "Anyone" (anonymous) links on regulated content
- [ ] Identify expired or unused sharing links
- [ ] Bulk disable risky sharing links
- [ ] Configure link expiration policies (30 days maximum)

**Location:** SharePoint Admin Center > Reports > Data access governance > Sharing links

---

## Phase 2: Grounding Scope Configuration

### 2.1 Restricted Content Discovery (RCD)

Enable RCD for sites that should not appear in Copilot responses:

- [ ] Executive leadership sites
- [ ] Legal and compliance repositories
- [ ] Human Resources (personnel files, compensation)
- [ ] M&A deal rooms and confidential projects
- [ ] Board of Directors materials
- [ ] Regulatory examination workspaces

**Configuration:**

```powershell
# Enable RCD for a site
Set-SPOSite -Identity "https://contoso.sharepoint.com/sites/hr-personnel" -RestrictContentOrgWideSearch $true

# Verify RCD status
Get-SPOSite -Identity "https://contoso.sharepoint.com/sites/hr-personnel" | Select RestrictContentOrgWideSearch
```

### 2.2 DLP Policies for Copilot Studio Knowledge Sources

- [ ] Create DLP policy in Power Platform Admin Center
- [ ] Add "Knowledge source with SharePoint and OneDrive in Copilot Studio" connector
- [ ] Configure endpoint filtering (allowlist or blocklist approach)
- [ ] Apply policy to production environments
- [ ] Test policy enforcement with sample agent

### 2.3 Retention Policies for Stale Content

- [ ] Review existing retention policies for SharePoint
- [ ] Implement 2-year retention-then-delete for non-regulated content
- [ ] Configure Site Lifecycle Policy for inactive sites (90-day threshold)
- [ ] Review disposition workflows for regulated content

---

## Phase 3: External Access Controls

### 3.1 Guest Access Configuration

- [ ] Verify organization-level sharing is "Existing guests" or more restrictive
- [ ] Disable external sharing for Zone 3 (Enterprise Managed) sites
- [ ] Configure guest access expiration (30 days for Zone 2, 90 days for Zone 1)
- [ ] Review domain allowlist for approved external partners
- [ ] Audit existing guest accounts for appropriateness

### 3.2 Sharing Defaults

- [ ] Set default link type to "People in your organization" or "Specific people"
- [ ] Enable link expiration requirement (30 days maximum)
- [ ] Disable "Anyone" links for regulated content libraries

---

## Phase 4: Security and Monitoring

### 4.1 Conditional Access

- [ ] Verify Conditional Access policies apply to SharePoint access
- [ ] Configure MFA requirements for Copilot-licensed users
- [ ] Review device compliance requirements
- [ ] Test Conditional Access with sample Copilot queries

### 4.2 Sensitivity Labels

- [ ] Verify sensitivity label taxonomy is deployed
- [ ] Configure auto-labeling policies for regulated content
- [ ] Test that Copilot respects label access restrictions
- [ ] Verify labels appear in Copilot response citations

### 4.3 Monitoring Configuration

- [ ] Enable Agent Insights in SharePoint Admin Center
- [ ] Configure SIEM integration for Zone 3 sites
- [ ] Establish monitoring cadence (daily for Zone 3, weekly for Zone 2)
- [ ] Define alert thresholds and escalation procedures

---

## Phase 5: Access Review Cadence

### 5.1 Establish Review Schedule

- [ ] Configure quarterly Site Access Reviews for Zone 3 sites
- [ ] Configure semi-annual reviews for Zone 2 sites
- [ ] Include AI agent service accounts in review scope
- [ ] Configure auto-remediation for non-compliant sites

### 5.2 Documentation

- [ ] Document all RCD-protected sites with business justification
- [ ] Archive permission audit results for compliance
- [ ] Create runbook for ongoing permission hygiene

---

## Verification Checklist

Before assigning Copilot licenses:

- [ ] All EEEU content remediated or RCD-protected
- [ ] Site permissions appropriate for all pilot users
- [ ] RCD enabled on sensitive sites (HR, Legal, M&A, Executive)
- [ ] DLP policies configured for Copilot Studio knowledge sources
- [ ] Guest access controls verified
- [ ] Conditional Access policies applied
- [ ] Monitoring configured and operational
- [ ] Access review schedule established

---

## Related Controls

| Control | Checklist Section |
|---------|------------------|
| [4.1 - Information Access Governance](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | Phase 2 |
| [4.2 - Site Access Reviews](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | Phase 1, Phase 5 |
| [4.3 - Retention Management](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md) | Phase 2 |
| [4.4 - Guest Access Controls](../../../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md) | Phase 3 |
| [4.5 - Security Monitoring](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md) | Phase 4 |
| [4.6 - Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Phase 2 |
| [4.7 - Copilot Data Governance](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | All Phases |

---

## Additional Resources

- [SharePoint Advanced Management Licensing Guide](../../../reference/sharepoint-advanced-management-licensing.md)
- [Data access governance reports](https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports)
- [Microsoft 365 Copilot data, privacy, and security](https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-privacy)
- [Preparing for Microsoft 365 Copilot](https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-setup)

---

*Updated: February 2026 | Framework Version: v1.2.43*
