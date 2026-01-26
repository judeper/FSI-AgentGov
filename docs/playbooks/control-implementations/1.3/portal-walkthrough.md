# Portal Walkthrough: Control 1.3 - SharePoint Content Governance and Permissions

**Last Updated:** January 2026
**Portal:** SharePoint Admin Center, Microsoft Purview, Entra Admin Center
**Estimated Time:** 2-4 hours (initial configuration)

## Prerequisites

- [ ] SharePoint Admin role assigned
- [ ] Access to [SharePoint Admin Center](https://admin.microsoft.com/sharepoint)
- [ ] Access to [Microsoft Purview](https://purview.microsoft.com)
- [ ] Purview Compliance Admin role (for sensitivity labels)
- [ ] [Control 1.5: DLP & Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) configured
- [ ] Audit of existing SharePoint sites with sensitive data completed

---

## Step-by-Step Configuration

### Step 1: Configure Tenant-Level Sharing Settings

**Portal Path:** [SharePoint Admin Center](https://admin.microsoft.com/sharepoint) > **Policies** > **Sharing**

1. Navigate to SharePoint Admin Center
2. Go to **Policies** > **Sharing**
3. Configure organization-level settings:

**FSI Recommended Settings:**

| Setting | Recommended Value | Rationale |
|---------|-------------------|-----------|
| External sharing level | **Only people in your organization** | Prevent accidental customer data exposure |
| File and folder links | **Only people in your organization** | No anonymous links |
| Allow or block sharing with specific domains | Block consumer domains (gmail.com, yahoo.com) | Prevent consumer email sharing |
| Guests must sign in using the same account | **Enabled** | Ensure accountability |
| Allow guests to share items they don't own | **Disabled** | Prevent chain sharing |
| Guest access expires automatically | **30-90 days** | Limit persistent guest access |

4. Click **Save**

### Step 2: Configure Site-Level Settings for Agent Knowledge Sources

**Portal Path:** SharePoint Admin Center > **Sites** > **Active sites** > [Select site]

For each SharePoint site that agents will use as a knowledge source:

1. Select the site > Click **Sharing**
2. Set sharing level:
   - Enterprise-managed agents: **Only people in your organization**
   - Team collaboration agents: **New and existing guests** (with approval)
   - Personal productivity agents: Site owner discretion
3. Click **Permissions** > **Advanced permissions settings**
4. Review and configure:
   - Remove **Everyone** and **Everyone except external users** groups
   - Add specific security groups with appropriate roles
   - Document all permission grants

### Step 3: Apply Sensitivity Labels to Sites and Libraries

**Portal Path:** Microsoft Purview > **Information protection** > **Labels**

#### Apply Label at Site Level

1. In SharePoint Admin Center > **Sites** > **Active sites**
2. Select the site > **Policies** tab
3. Under **Sensitivity**, click **Edit**
4. Select appropriate label:
   - `Confidential-FSI` for customer data
   - `Highly Confidential` for trading/material non-public information
   - `Internal` for general business content
5. Click **Save**

#### Apply Label at Library Level

1. Navigate to the document library in SharePoint
2. Click **Settings** (gear) > **Library settings**
3. Under **Permissions and Management**:
   - Click **Apply sensitivity label to items in this list or library**
4. Select the appropriate default label
5. Choose whether to:
   - **Apply label to existing items**: Recommended for initial deployment
   - **Apply label only to new items**: For ongoing governance

### Step 4: Create Restricted Sites for Sensitive Agent Knowledge

**Portal Path:** SharePoint Admin Center > **Sites** > **Create**

1. Click **Create** > Choose **Team site** or **Communication site**
2. Configure site settings:
   - **Site name**: `Agent-Knowledge-[AgentName]` or `FSI-AgentData-[Zone]`
   - **Privacy settings**: Private
   - **Language**: English
3. After creation, configure:
   - External sharing: **Only people in your organization**
   - Apply sensitivity label: Appropriate FSI label
   - Site permissions: Only agent service accounts + content owners

### Step 5: Configure Information Access Governance (IAG)

**Portal Path:** SharePoint Admin Center > **Sites** > **Active sites** > **Restricted access control**

For enterprise-managed agent knowledge sources:

1. Select the site containing sensitive data
2. Click **Policies** > **Restricted access control**
3. Enable **Restrict access to this site**
4. Add specific users or groups who can access
5. This creates an additional layer beyond standard permissions

### Step 6: Configure Access Reviews for Agent Knowledge Sites

**Portal Path:** Microsoft Entra > **Identity Governance** > **Access Reviews**

1. Navigate to Entra Admin Center > **Identity Governance** > **Access Reviews**
2. Click **+ New access review**
3. Configure:
   - **Name**: `Agent-Knowledge-Sites-Quarterly-Review`
   - **Scope**: SharePoint site(s) used by agents
   - **Reviewers**: Site owners or designated governance team
   - **Frequency**: Quarterly (for enterprise-managed) or Semi-annually (team collaboration)
   - **Duration**: 14 days
4. Under **Upon completion settings**:
   - Auto-apply results: Consider for personal productivity / team collaboration
   - If reviewers don't respond: Remove access (for enterprise-managed)
5. Create the access review

---

## Configuration by Governance Level

| Setting | Baseline (Personal) | Recommended (Team) | Regulated (Enterprise) |
|---------|-------------------|----------------------|--------------------|
| **Site Sharing** | Site owner discretion | Existing guests only | Organization only |
| **External Sharing** | Organization-wide setting | Partner domains only | Disabled |
| **Sensitivity Labels** | Recommended | Required (Internal+) | Required (Confidential+) |
| **Access Reviews** | Annual | Semi-annual | Quarterly |
| **Permissions** | Standard groups | Named security groups | Named individuals only |
| **IAG** | Not required | Recommended | Required |

---

## Validation

After completing these steps, verify:

- [ ] Tenant-level sharing restricted per FSI requirements
- [ ] Agent knowledge sites have appropriate sharing settings
- [ ] Sensitivity labels applied to sites and libraries
- [ ] "Everyone" groups removed from agent data sources
- [ ] Access reviews scheduled and notifications working
- [ ] IAG configured for enterprise-managed sites

---

[Back to Control 1.3](../../../controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
