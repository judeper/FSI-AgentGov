# Control 4.5: SharePoint Security and Compliance Monitoring - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 4.5](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md).

---

## Prerequisites

Before starting, ensure you have:

- SharePoint Admin role assigned
- SharePoint Advanced Management license (for Agent insights)
- Unified audit logging enabled in Microsoft Purview

---

## Step 1: Enable Reporting Access

Ensure appropriate access for monitoring personnel:

1. Assign **SharePoint Admin** role for full admin center access
2. For read-only access: Assign **Reports Reader** role
3. Verify access to SharePoint Admin Center at [admin.sharepoint.com](https://admin.sharepoint.com)

---

## Step 2: Configure Agent Insights Monitoring

Establish agent monitoring:

1. Navigate to [SharePoint Admin Center](https://admin.sharepoint.com)
2. Go to **Reports** > **Agent insights**
3. Click **View reports** under "SharePoint agents"
4. Review agent list and document findings
5. Click **View reports** under "Agent access"
6. Identify agents accessing sensitive sites
7. Cross-reference with governance approval records

---

## Step 3: Establish Data Access Governance Baseline

Create baseline reports:

1. Navigate to **Reports** > **Data access governance**
2. Click **Get started** to run initial assessment
3. Generate all snapshot reports:
   - Site permissions across your organization
   - User permissions
   - Sensitivity labels
4. Export reports for baseline documentation
5. Identify immediate remediation items

---

## Step 4: Configure Advanced Management Assessments

Run Copilot readiness assessment:

1. Navigate to **Advanced management** > **Overview**
2. Click **Start assessment**
3. Review Site lifecycle results:
   - Site inactivity
   - Missing site ownership
4. Review Oversharing results:
   - Broken permission inheritance
   - Org-wide site permissions
   - Organization and anyone sharing links
5. Click **View recommendations** for remediation guidance

---

## Step 5: Review Home Dashboard

The SharePoint Admin Center home dashboard provides at-a-glance metrics:

1. Navigate to **Home** in SharePoint Admin Center
2. Review dashboard cards:
   - Sensitivity labels across sites (labeled vs. unlabeled)
   - Information barriers status
   - OneDrive file activity
   - Message center announcements
3. Subscribe to relevant message center notifications

---

## Step 6: Establish Monitoring Cadence

Create monitoring schedule:

| Activity | Frequency | Responsible Role |
|----------|-----------|------------------|
| Dashboard review | Daily | SharePoint Admin |
| Agent insights review | Weekly | AI Governance Lead |
| Data access reports | Monthly | Compliance |
| Advanced assessments | Quarterly | Governance Committee |
| Comprehensive audit | Annually | Internal Audit |

---

## Governance Level Configurations

### Baseline (Level 1)

| Setting | Value |
|---------|-------|
| Agent activity monitoring | Monthly review of Agent insights |
| Dashboard review | Weekly review of Home dashboard |
| Security event awareness | Subscribe to Message center |

### Recommended (Level 2-3)

| Setting | Value |
|---------|-------|
| Agent access review | Weekly Agent access report |
| Data access governance | Monthly permissions/sharing review |
| Oversharing assessments | Quarterly |
| Compliance dashboard | Custom monitoring dashboard |

### Regulated (Level 4)

| Setting | Value |
|---------|-------|
| Real-time threat monitoring | Microsoft Sentinel integration |
| SOC integration | Alert SOC on security events |
| Automated response | Containment actions configured |
| Audit trail | Per-regulation retention |

---

## Validation

After completing the configuration, verify:

1. [ ] SharePoint Admin and Reports Reader roles assigned to monitoring personnel
2. [ ] Agent insights reports accessible in SharePoint Admin Center > Reports
3. [ ] Data Access Governance baseline reports generated and exported
4. [ ] Monitoring cadence documented with responsible roles assigned

**Expected Result:** SharePoint monitoring dashboards provide visibility into agent access patterns, oversharing risks, and security posture.

---

[Back to Control 4.5](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
