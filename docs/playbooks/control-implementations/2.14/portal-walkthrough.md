# Portal Walkthrough: Control 2.14 - Training and Awareness Program

**Last Updated:** January 2026
**Portals:** Microsoft 365 Admin Center, Microsoft Viva Learning
**Estimated Time:** 2-4 hours initial setup, ongoing management

## Prerequisites

- [ ] Microsoft 365 Admin role or Learning Administrator role
- [ ] Training content developed and approved
- [ ] Role-based training requirements defined
- [ ] LMS integration configured (if applicable)

---

## Step-by-Step Configuration

### Step 1: Define Training Requirements by Role

1. Identify roles that interact with AI agents:
   - **Makers:** Users who create/modify agents
   - **Users:** Users who interact with agents
   - **Administrators:** Users who manage agent governance
   - **Compliance:** Users who review agent outputs

2. Map training modules to each role:

| Role | Required Training | Frequency |
|------|------------------|-----------|
| Maker | Agent Development, Data Governance, Security | Annual + on new features |
| User | Agent Usage Policy, Data Handling | Annual |
| Administrator | Full governance framework | Annual + quarterly updates |
| Compliance | Audit procedures, Evidence collection | Annual |

### Step 2: Configure Viva Learning (If Using)

1. Open [Microsoft 365 Admin Center](https://admin.microsoft.com)
2. Navigate to **Settings** > **Org settings** > **Viva Learning**
3. Enable Viva Learning for the organization
4. Configure learning content sources:
   - Microsoft Learn (built-in)
   - Custom content (SharePoint)
   - Third-party LMS integration

### Step 3: Create Custom Learning Content

1. Create a SharePoint site for AI Governance Training
2. Upload training materials:
   - Governance framework overview
   - Role-specific guides
   - Policy documents
   - Video walkthroughs

3. Configure Viva Learning to pull from SharePoint:
   - Admin Center > Viva Learning > Content sources
   - Add SharePoint site URL
   - Map content to learning paths

### Step 4: Establish Training Completion Tracking

1. Configure completion tracking in your LMS or Viva Learning
2. Set up automated reminders for:
   - Initial training (within 30 days of role assignment)
   - Annual refresher training
   - Policy update acknowledgments

3. Create compliance reports for:
   - Training completion rates by role
   - Overdue training notifications
   - Training effectiveness metrics

### Step 5: Integrate with Agent Publishing Workflow

1. Configure pre-publishing checks in Copilot Studio:
   - Verify maker has completed required training
   - Block publishing if training is incomplete (Zone 3)
   - Warn if training is incomplete (Zone 2)

2. Document training requirements in Maker Welcome Content (Control 2.1)

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|--------------------|
| **Training Required** | Recommended | Required for makers | **Mandatory for all** |
| **Completion Tracking** | Optional | Enabled | **Enforced with blocking** |
| **Refresh Frequency** | Annual | Annual | **Semi-annual** |
| **Policy Acknowledgment** | Optional | Annual | **Per policy update** |
| **Evidence Retention** | 1 year | 3 years | **7 years** |

---

## Validation

After completing these steps, verify:

- [ ] Training content is accessible in configured LMS
- [ ] Completion tracking is functioning
- [ ] Role-based assignments are correct
- [ ] Automated reminders are sending
- [ ] Reports show accurate completion data

---

[Back to Control 2.14](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
