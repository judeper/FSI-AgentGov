# Control 4.6: Grounding Scope Governance - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md).

---

## Prerequisites

Before starting, ensure you have:

- SharePoint Admin role assigned
- SharePoint Advanced Management license
- Site inventory completed with content classification
- Sensitivity labels deployed (if using label-based exclusion)

---

## Step 1: Inventory Current Grounding Scope

### Categorize Sites by Content Type

| Category | Description | Default Index Status | Recommendation |
|----------|-------------|---------------------|----------------|
| **Production Knowledge** | Finalized, approved content | Include | Keep indexed |
| **Draft/WIP** | Work in progress documents | Include (by default) | Exclude |
| **Archive** | Historical, outdated content | Include (by default) | Exclude |
| **Personal** | Individual user files | Include (by default) | Exclude |
| **Regulatory Hold** | Content under legal hold | Include (by default) | Review |
| **Highly Confidential** | Top-secret business data | Include (by default) | Exclude or restrict |

---

## Step 2: Configure Site Exclusion from Semantic Index

### Option A: Restricted Content Discovery (RCD) via Portal

1. Navigate to [SharePoint Admin Center](https://admin.sharepoint.com)
2. Go to **Sites** > **Active sites**
3. Select the site to restrict
4. Click the **Settings** tab
5. Under **Microsoft 365 Copilot**, locate **Restrict content from Microsoft 365 Copilot**
6. Toggle the setting to **On** to exclude the site from Copilot results
7. Click **Save**

!!! note "Toggle UI"
    The Restricted Content Discovery setting uses an **On/Off toggle**, not a dropdown. When toggled **On**, the site's content is excluded from Microsoft 365 Copilot (Business Chat) results. When **Off** (default), content is available to Copilot based on user permissions.

!!! warning "Reindexing After Scope Changes"
    Changes to Copilot grounding scope (adding or removing sites, libraries)
    may trigger partial reindexing. Updated semantic index boundaries become
    effective only after reindex completion. Allow **24-48 hours** before
    validating scope changes via test queries.

### Sites to Exclude

Apply Restricted Content Discovery to:

- All sites with "Draft" in the name
- Archive sites
- Legal hold sites
- Executive communications
- HR confidential sites
- M&A / deal rooms

---

## Step 3: Implement CopilotReady Metadata Approach

For positive governance (explicit approval for indexing):

1. Create a governance register of approved sites
2. Document each site with:
   - Site URL
   - CopilotReady status (Yes/No)
   - Approved by
   - Approval date
   - Review due date
3. Use site property bags or a SharePoint list to track approvals

---

## Step 4: Establish Monitoring

### Monitoring Cadence

| Activity | Frequency | Responsible Role |
|----------|-----------|------------------|
| Review new sites for grounding scope | Weekly | SharePoint Admin |
| Audit excluded sites | Monthly | AI Governance Lead |
| CopilotReady certification | Quarterly | Content Owners |
| Comprehensive scope review | Annually | Governance Committee |

---

## Step 5: Configure SharePoint Restricted Search

!!! info "GA Feature"
    SharePoint Restricted Search is generally available for Microsoft 365 Copilot customers. This feature provides positive governance with an allowed list of up to 100 SharePoint sites for AI agent grounding.

### Overview

SharePoint Restricted Search implements a **positive governance model** where only explicitly approved sites are accessible to Microsoft 365 Copilot and AI agents for grounding. This is recommended for Zone 3 environments requiring strict content governance.

### Configuration Steps

**Note:** As of January 2026, SharePoint Restricted Search is primarily configured via PowerShell. Check the SharePoint Admin Center Search settings for potential UI configuration options in newer releases.

1. **Enable Restricted Search Mode** (PowerShell):
   ```powershell
   # Connect to SharePoint Online
   Connect-SPOService -Url "https://contoso-admin.sharepoint.com"

   # Enable Restricted Search
   Set-SPOTenant -EnableRestrictedSearchAllList $true
   ```

2. **Add Sites to Allowed List**:
   ```powershell
   # Add individual site to allowed list
   Add-SPOTenantRestrictedSearchAllowedList -SiteUrl "https://contoso.sharepoint.com/sites/ApprovedKnowledge"

   # Verify addition
   Get-SPOTenantRestrictedSearchAllowedList
   ```

3. **Document Governance Process**:
   - Create a governance register tracking all 100 allowed sites
   - Document business justification for each site
   - Record approval date and approving officer
   - Schedule quarterly review dates

4. **Monitor Propagation** (24-48 hours):
   - Configuration changes may take 24-48 hours to affect Copilot grounding behavior
   - Test Copilot queries against allowed and non-allowed sites after propagation period
   - Verify users can only get grounded responses from allowed sites

### Zone-Specific Configuration

| Zone | Restricted Search Configuration | Rationale |
|------|--------------------------------|-----------|
| **Zone 1** (Personal) | Not typically used; document policy | Personal agents access individual OneDrive content |
| **Zone 2** (Team) | Optional; use for high-value team agents | Balances governance with flexibility |
| **Zone 3** (Enterprise) | **Mandatory**; enable Restricted Search and limit to pre-approved sites only | Strictest content governance for regulated environments |

### Governance Process for Site Additions

1. **Content owner nominates site** with business justification
2. **Security team verifies** sensitivity labeling and access controls
3. **Compliance officer approves** site for AI grounding
4. **SharePoint admin adds** site to allowed list via PowerShell
5. **Document decision** in governance register

### 100-Site Limit Management

When approaching the 100-site limit:

- **Prioritize authoritative sources** (product documentation, compliance manuals, approved knowledge bases)
- **Remove low-usage sites** based on quarterly usage metrics
- **Consolidate content** where possible to reduce site count
- **Use RCD complementarily** to exclude specific content within allowed sites

---

## Governance Level Configurations

### Baseline (Level 1)

| Setting | Value |
|---------|-------|
| Site awareness | Document which sites agents access |
| Manual exclusion | Exclude known sensitive sites |
| Monitoring | Quarterly review of indexed content |

### Recommended (Level 2-3)

| Setting | Value |
|---------|-------|
| Systematic exclusion | Policy-based site exclusion |
| Content type filtering | Exclude Draft, Archived, Personal |
| Metadata approach | CopilotReady tag for approved content |
| Review frequency | Monthly |

### Regulated (Level 4)

| Setting | Value |
|---------|-------|
| Comprehensive governance | All content explicitly approved for indexing |
| Label integration | Sensitivity labels control index inclusion |
| Real-time monitoring | Continuous audit of indexed content |
| Change control | Formal approval for grounding scope changes |

---

[Back to Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: February 2026 | Version: v1.2*
