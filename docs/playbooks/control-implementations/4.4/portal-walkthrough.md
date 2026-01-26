# Control 4.4: Guest and External User Access Controls - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 4.4](../../../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md).

---

## Prerequisites

Before starting, ensure you have:

- SharePoint Admin role assigned
- Microsoft 365 E3/E5 license
- Current sharing settings documented
- Site inventory with governance classifications available

---

## Step 1: Inventory Current Sharing State

Assess current external sharing:

1. Navigate to [SharePoint Admin Center](https://admin.sharepoint.com)
2. Go to **Reports** > **Data access governance**
3. View "Site permissions across your organization" report
4. Identify sites with guest access enabled
5. Export report for analysis
6. Cross-reference with governance classification

---

## Step 2: Configure Site-Level Restrictions

### For Regulated/Sensitive Sites (Zone 3)

1. Navigate to **Sites** > **Active sites**
2. Select the site
3. Open **Settings** tab
4. Set "External file sharing" to **Only people in your organization**
5. Repeat for all regulated/sensitive sites

### For Collaborative Sites (Zone 2)

1. Set "External file sharing" to **Existing guests** at most
2. Document any approved guest access with business justification

---

## Step 3: Configure Organization Policies

Set organization defaults:

1. Navigate to **Policies** > **Sharing**
2. Configure external sharing level:
   - **Baseline:** "Existing guests" or more restrictive
   - **Regulated:** "Only people in your organization"
3. Enable guest access expiration (30 days recommended)
4. Set default link type to **Internal**
5. Enable link expiration requirements (30 days maximum)

---

## Step 4: Configure Guest Access Expiration

1. Navigate to **Policies** > **Sharing**
2. Enable "Guest access to a site or OneDrive will expire automatically"
3. Set expiration period:
   - Zone 1: 90 days
   - Zone 2: 30 days
   - Zone 3: Not permitted (external sharing disabled)

---

## Step 5: Configure Domain Restrictions (Optional)

For approved partner collaboration:

1. Navigate to **Policies** > **Sharing**
2. Under "Advanced settings for external sharing"
3. Select "Limit external sharing by domain"
4. Choose "Allow only specific domains"
5. Add approved partner domains

---

## Step 6: Implement Monitoring

Establish ongoing monitoring:

1. Schedule weekly review of sharing reports
2. Navigate to **Reports** > **Data access governance**
3. Review "Sharing links" report
4. Review "Site permissions across your organization"
5. Document all guest access approvals

---

## Governance Level Configurations

### Baseline (Level 1)

| Setting | Value |
|---------|-------|
| Organization sharing | Existing guests or more restrictive |
| Sensitive sites | External sharing disabled |
| Monitoring | Monthly sharing report review |

### Recommended (Level 2-3)

| Setting | Value |
|---------|-------|
| Guest expiration | 30 days |
| Link expiration | 30 days maximum |
| Default link type | Internal |
| Monitoring | Weekly sharing report review |

### Regulated (Level 4)

| Setting | Value |
|---------|-------|
| Organization sharing | Existing guests only |
| Regulated sites | External sharing disabled |
| Conditional Access | MFA required for guests |
| Guest access reviews | Quarterly certification |

---

## Validation

After completing the configuration, verify:

1. [ ] Organization-level sharing settings configured appropriately
2. [ ] Zone 3 sites have external sharing disabled
3. [ ] Guest access expiration enabled with appropriate timeframes
4. [ ] Default link type set to Internal
5. [ ] Domain restrictions configured (if applicable)
6. [ ] Sharing reports accessible and showing expected data
7. [ ] Test external sharing attempt blocked on regulated site

**Expected Result:** External sharing is appropriately restricted based on site classification, guest access expires automatically, and sharing activity is visible in governance reports.

---

[Back to Control 4.4](../../../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
