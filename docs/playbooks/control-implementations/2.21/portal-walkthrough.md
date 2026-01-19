# Portal Walkthrough: Control 2.21 - AI Marketing Claims and Substantiation

**Last Updated:** January 2026
**Portal:** SharePoint, Microsoft Compliance Center
**Estimated Time:** 2-3 hours initial setup

## Prerequisites

- [ ] SharePoint Admin or Site Owner permissions
- [ ] Access to Microsoft Compliance Center
- [ ] Compliance Officer approval for workflow design
- [ ] Legal review of claim categories completed
- [ ] Marketing team stakeholders identified

---

## Step-by-Step Configuration

### Step 1: Create AI Claims Inventory List in SharePoint

1. Navigate to your Governance SharePoint site
2. Create a new List named "AI Marketing Claims Inventory"
3. Add the following columns:

| Column Name | Type | Options/Format |
|-------------|------|----------------|
| Claim ID | Auto-number | AI-CLAIM-#### |
| Claim Text | Multiple lines | Plain text |
| Claim Category | Choice | Performance, Capability, Comparative, Predictive, Efficiency |
| Agent/Product | Single line | Text |
| Target Channel | Choice | Website, Email, Social Media, Sales Collateral, Press Release |
| Substantiation File | Hyperlink | Link to evidence document |
| Status | Choice | Draft, Under Review, Approved, Rejected, Retired |
| Submitted By | Person | |
| Submission Date | Date | |
| Compliance Reviewer | Person | |
| Review Date | Date | |
| Approval Date | Date | |
| Next Review Date | Date | Auto-calculate: Approval Date + 90 days |
| Comments | Multiple lines | |

### Step 2: Create Substantiation Evidence Library

1. In the same SharePoint site, create a Document Library: "AI Claims Substantiation"
2. Create folders for each claim category:
   - Performance Claims
   - Capability Claims
   - Comparative Claims
   - Predictive Claims
   - Efficiency Claims
3. Set retention: 7 years (FINRA 4511 alignment)
4. Configure versioning: Major versions only, require check-out

### Step 3: Configure Pre-Publication Review Workflow

Using Power Automate, create an approval workflow:

**Trigger:** When an item is created in "AI Marketing Claims Inventory"

**Flow Steps:**

1. **Notify Submitter:** Send confirmation email
2. **Initial Review:** Start approval with Compliance Officer
   - If Rejected: Update status, notify submitter, end flow
   - If Approved: Continue to Step 3
3. **Technical Review:** Start approval with AI Governance Lead
   - If Rejected: Update status, notify submitter, end flow
   - If Approved: Continue to Step 4
4. **Legal Review (Zone 3 only):** If Zone = 3, start approval with Legal
   - If Rejected: Update status, notify submitter, end flow
   - If Approved: Continue to Step 5
5. **Final Approval:** Update status to "Approved", set Approval Date and Next Review Date
6. **Notification:** Send approval confirmation to submitter and reviewers

### Step 4: Set Up Quarterly Review Reminder

Create a scheduled Power Automate flow:

**Trigger:** Recurrence - Weekly on Mondays

**Flow Steps:**

1. Get items from AI Marketing Claims Inventory where:
   - Status = "Approved"
   - Next Review Date <= Today + 14 days
2. For each item:
   - Send reminder email to Compliance Reviewer
   - Include claim text, original approval date, substantiation file link

### Step 5: Configure Compliance Center Integration

1. Navigate to Microsoft Compliance Center
2. Under **Information governance** > **Labels**, create retention label:
   - Name: "AI Marketing Claim - 7 Year Retention"
   - Retention period: 7 years from creation
   - Apply to: AI Claims Substantiation library

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|--------------------|
| **Claims Inventory** | Not required | Recommended | **Required** |
| **Pre-Publication Review** | Not required | Compliance review | Full review (Compliance + Legal) |
| **Substantiation File** | Not required | Recommended | **Mandatory** |
| **Quarterly Review** | Not required | Optional | **Mandatory** |
| **Retention** | N/A | 3 years | **7 years** |

---

## FSI Example Configuration

```yaml
Organization: Regional Investment Advisory Firm
Claims Inventory Site: https://contoso.sharepoint.com/sites/AIGovernance

Active Claims:
  - Claim ID: AI-CLAIM-0001
    Text: "Our AI-powered portfolio analysis reviews 10,000+ securities daily"
    Category: Capability
    Status: Approved
    Substantiation: Link to technical documentation + usage logs
    Next Review: April 15, 2026

  - Claim ID: AI-CLAIM-0002
    Text: "AI assistant reduces client onboarding time by 60%"
    Category: Efficiency
    Status: Approved
    Substantiation: Link to benchmark study (n=500 onboardings)
    Next Review: May 1, 2026

Review Workflow:
  Zone 3 Claims: Marketing → Compliance → AI Governance → Legal → Publication
  Zone 2 Claims: Marketing → Compliance → Publication
```

---

## Validation

After completing these steps, verify:

- [ ] AI Marketing Claims Inventory list created with all required columns
- [ ] Substantiation Evidence library created with folder structure
- [ ] Pre-publication approval workflow triggers on new item creation
- [ ] Quarterly review reminders are being sent
- [ ] Retention label applied to substantiation library
- [ ] Test claim submission completes full workflow

---

[Back to Control 2.21](../../../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
