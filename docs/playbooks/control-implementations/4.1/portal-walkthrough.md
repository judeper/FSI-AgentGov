# Portal Walkthrough: Control 4.1 - SharePoint Information Access Governance (IAG)

**Last Updated:** January 2026
**Portal:** SharePoint Admin Center
**Estimated Time:** 1-2 hours

## Prerequisites

- [ ] SharePoint Admin role assigned
- [ ] Access to [SharePoint Admin Center](https://admin.sharepoint.com)
- [ ] SharePoint Advanced Management Plan 1 license assigned to tenant
- [ ] Governance tier classification completed for all SharePoint sites
- [ ] Sensitive site inventory documented

---

## Step-by-Step Configuration

### Step 1: Inventory Sensitive Sites

Run Data access governance reports to identify sites requiring restriction:

1. Navigate to **SharePoint Admin Center** ([https://admin.sharepoint.com](https://admin.sharepoint.com))
2. Go to **Reports** > **Data access governance**
3. View "Site permissions across your organization" report
4. Identify sites with broad permissions (Everyone except external users)
5. Cross-reference with enterprise-managed agent knowledge sources

### Step 2: Enable Restricted Content Discovery (RCD) for Sensitive Sites

For each identified site:

1. Go to **Sites** > **Active sites**
2. Select the site containing sensitive content
3. Open **Settings** tab in the right panel
4. Locate "Restrict content from Microsoft 365 Copilot"
5. Set the toggle to **On**
6. Document the change in your governance records

**Repeat for all regulated/enterprise-managed sites.**

### Step 3: Configure Restricted SharePoint Search (RSS) - Allow-List Approach

For organizations preferring Zero Trust (allow-list approach):

1. Navigate to **SharePoint Admin Center** > **Settings** > **Restricted SharePoint Search**
2. Toggle **Restricted SharePoint Search** to **On**
3. Click **Add sites** to build your allow-list
4. Add up to 100 sites that Copilot may access
5. Save changes

**Key Constraints:**
- Maximum 100 sites in the allow-list
- Organization-wide setting (affects all Copilot users)
- Does not affect web search or Graph-connected content

### Step 4: Configure Restricted Access Control (RAC) for Ethical Walls

For sites requiring information barriers (M&A deal rooms, trading desks):

1. Navigate to **Sites** > **Active sites**
2. Select the site requiring ethical walls
3. Open **Settings** tab
4. Click **Restricted site access** > **Edit**
5. Enable restricted access
6. Add authorized security groups (up to 10 groups)
7. Save changes

**FSI Use Cases for RAC:**
- M&A Deal Rooms - Restrict to deal team members only
- Investment Banking / Research separation
- Trading Desk isolation
- Regulatory examination sites

### Step 5: Document Configuration

Record in your governance system:

- Site URL and name
- Restriction setting enabled date
- Reason for restriction
- Approving authority
- Review schedule

### Step 6: Establish Review Cycle

- **Quarterly:** Review restricted sites list
- **On agent deployment:** Verify knowledge sources are appropriately restricted
- **On regulatory change:** Assess new restriction requirements

---

## Configuration by Governance Level

| Setting | Baseline | Recommended | Regulated |
|---------|----------|-------------|-----------|
| **RCD for sensitive sites** | Case-by-case | Tier 2+ sites | All Tier 3 sites |
| **Restricted site access (RAC)** | Not required | Recommended | Required |
| **Review frequency** | Annual | Semi-annual | Quarterly |
| **Approval required** | No | Yes | Governance committee |

---

## RCD vs RSS: Choosing the Right Approach

| Approach | Use Case | When to Use |
|----------|----------|-------------|
| **Restricted Content Discovery (RCD)** | Block-list: exclude specific sites | Mature deployment, good hygiene |
| **Restricted SharePoint Search (RSS)** | Allow-list: include only approved sites | Initial Copilot deployment, Zero Trust |
| **Hybrid** | Start with RSS, transition to RCD | Phased rollout |

---

## Validation

After completing these steps, verify:

- [ ] RCD enabled for all regulated/enterprise-managed sites
- [ ] RSS configured (if using allow-list approach)
- [ ] RAC configured for information barrier sites
- [ ] Copilot does not return content from restricted sites (test with authorized user)
- [ ] Audit logs capture setting changes

---

[Back to Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
