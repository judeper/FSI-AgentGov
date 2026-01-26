# Portal Walkthrough: Control 4.2 - Site Access Reviews and Certification

**Last Updated:** January 2026
**Portal:** SharePoint Admin Center, Microsoft Entra Admin Center
**Estimated Time:** 1-2 hours

## Prerequisites

- [ ] SharePoint Admin role assigned
- [ ] Access to [SharePoint Admin Center](https://admin.sharepoint.com)
- [ ] Access to [Microsoft Entra Admin Center](https://entra.microsoft.com)
- [ ] SharePoint Advanced Management Plan 1 license assigned to tenant
- [ ] Entra ID Governance (P2) license for access review workflows
- [ ] Site owners identified and documented for each team/enterprise site

---

## Step-by-Step Configuration

### Step 1: Assess Current Permissions with Data Access Governance Reports

Generate baseline permissions report:

1. Navigate to [SharePoint Admin Center](https://admin.sharepoint.com)
2. Go to **Reports** > **Data access governance**
3. Click **Get started** to run initial assessment (if first use)
4. Click **View reports** under "Site permissions across your organization"
5. Export report for analysis
6. Identify sites with:
   - "Everyone except external users" access
   - Guest user access
   - Broad sharing links
7. Prioritize team/enterprise sites and agent knowledge sources

### Step 2: Configure Site Attestation Policies

Create attestation policy for regulated sites:

1. Navigate to **Policies** > **Site lifecycle management**
2. Click **Open** under "Site attestation policies"
3. Click **Create policy**
4. Configure scope:
   - **By sensitivity label:** Confidential, Highly Confidential
   - **By site URL pattern:** (optional)
   - **By site template:** (optional)
5. Set frequency:
   - **Quarterly:** For enterprise-managed sites
   - **Annual:** For team collaboration sites
6. Configure notifications:
   - Reminder before due date: 30, 14, 7 days
   - Escalation to admin if overdue
7. Set non-compliance action:
   - **Read-only:** Recommended for regulated sites
   - **Archive:** For long-term non-response
8. Click **Save** and enable the policy

### Step 3: Configure Access Reviews in Entra ID (for Groups)

Create access review schedule for M365 Groups/Teams:

1. Navigate to [Microsoft Entra Admin Center](https://entra.microsoft.com)
2. Go to **Identity governance** > **Access reviews**
3. Click **New access review**
4. Configure review:
   - **Review name:** "FSI SharePoint Site Access Review - Quarterly"
   - **Description:** Review and certify access to sensitive SharePoint sites
   - **Scope:** Groups and Teams
   - **Review scope:** Specific groups (select site-connected M365 groups)
5. Configure reviewers:
   - **Group owners:** Primary reviewer
   - **Fallback reviewers:** Compliance team
6. Configure settings:
   - **Duration:** 14 days
   - **Recurrence:** Quarterly
   - **Auto-apply results:** Yes
   - **Default decision if no response:** Deny
   - **Justification required:** Yes
7. Click **Create**

### Step 4: Establish Review Process for Agent Knowledge Sources

Document access review procedures:

1. Identify sites used as agent knowledge sources (from Agent Inventory)
2. Document review requirements per zone:
   - Zone 1: Annual review (site owner)
   - Zone 2: Semi-annual review (owner + manager)
   - Zone 3: Quarterly review (owner + compliance)
3. Create checklist for reviewers:
   - Is each user's access still needed?
   - Are permissions appropriate for role?
   - Are any external users present?
   - Is agent access documented and approved?

### Step 5: Monitor Compliance

Track attestation compliance:

1. Navigate to **Policies** > **Site lifecycle management**
2. Review "Site attestation policies" dashboard
3. Check attestation completion rates
4. Follow up on overdue attestations
5. Export reports for governance documentation

---

## Configuration by Governance Level

| Setting | Baseline | Recommended | Regulated |
|---------|----------|-------------|-----------|
| **Access review frequency** | Annual | Semi-annual | Quarterly |
| **Attestation policy** | None | Annual | Quarterly |
| **Reviewers** | Site owner | Owner + manager | Owner + compliance + legal |
| **Auto-remediation** | None | Archive if no response | Read-only + escalation |
| **Justification required** | No | Yes | Yes with documentation |

---

## Service Account Access Reviews for AI Agents

For AI agents using service accounts or service principals:

1. Identify agent service accounts from Agent Inventory
2. Review API permissions granted to each service principal
3. Validate least privilege:
   - Prefer Sites.Selected over Sites.Read.All
   - Document business justification for each permission
4. Include service accounts in quarterly access review cycle
5. Document findings using the Service Account Review Checklist

---

## Validation

After completing these steps, verify:

- [ ] Data access governance reports accessible and current
- [ ] Site attestation policy configured for regulated sites
- [ ] Access review schedules created in Entra ID
- [ ] Notification templates configured
- [ ] Non-compliance actions set appropriately
- [ ] Review process documented and communicated to site owners

---

[Back to Control 4.2](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
