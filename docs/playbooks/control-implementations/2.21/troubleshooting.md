# Troubleshooting: Control 2.21 - AI Marketing Claims and Substantiation

**Last Updated:** January 2026
**Support Contacts:** Compliance Officer, AI Governance Lead
**Escalation Path:** Legal → Chief Compliance Officer

---

## Common Issues and Resolutions

### Issue 1: Approval Workflow Not Triggering

**Symptoms:**

- Claim submitted but no approval request sent
- Workflow status shows "Not started"
- Approvers not receiving notifications

**Resolution Steps:**

1. **Verify workflow is enabled:**
   - Navigate to Power Automate > My flows
   - Locate the claims approval flow
   - Ensure status shows "On"

2. **Check trigger conditions:**
   - Verify the workflow trigger is set to "When an item is created" or status change
   - Confirm the list name matches exactly

3. **Verify connections:**
   - Open the flow in edit mode
   - Check all connection references show green checkmarks
   - Re-authenticate any connections showing errors

4. **Test with manual trigger:**
   - Run the flow manually with a test item
   - Review run history for specific error

**Root Cause:** Usually connection timeout or disabled flow.

---

### Issue 2: Substantiation Link Not Working

**Symptoms:**

- Hyperlink field shows URL but clicking returns 404
- "Access denied" error when clicking link
- Link opens but shows wrong document

**Resolution Steps:**

1. **Verify document exists:**
   - Navigate directly to the Substantiation library
   - Confirm the file is present at the expected location

2. **Check URL format:**
   - URL should be full path: `https://tenant.sharepoint.com/sites/Site/Library/File.docx`
   - Not relative path: `/sites/Site/Library/File.docx`

3. **Verify permissions:**
   - User viewing the claim must have Read access to Substantiation library
   - Check library permissions: Library settings > Permissions

4. **Re-link the document:**
   - Copy the correct URL from browser when viewing the document
   - Edit the claim and update the Substantiation File field

**Root Cause:** Permission mismatch or incorrect URL format.

---

### Issue 3: Quarterly Review Reminders Not Sending

**Symptoms:**

- Claims past review date but no reminders sent
- Scheduled flow shows no recent runs
- Compliance Reviewer not receiving emails

**Resolution Steps:**

1. **Check flow schedule:**
   - Open the quarterly review flow
   - Verify recurrence is set correctly (e.g., Weekly on Monday)
   - Check "Next run" date/time

2. **Verify filter conditions:**
   - Review the "Get items" action filter
   - Ensure it's checking `NextReviewDate <= Today + 14 days`
   - Ensure it's filtering for `Status = Approved` only

3. **Check email action:**
   - Verify the "Send email" action has valid recipients
   - Check if ComplianceReviewer field is populated on claims

4. **Run flow manually:**
   - Trigger the flow manually and review run history
   - Check for "No items found" vs actual errors

**Root Cause:** Filter conditions too restrictive or email recipient field empty.

---

### Issue 4: Claims Report Export Fails

**Symptoms:**

- PowerShell script returns errors
- Export file empty or incomplete
- Connection authentication errors

**Resolution Steps:**

1. **Re-authenticate PnP connection:**
   ```powershell
   Disconnect-PnPOnline
   Connect-PnPOnline -Url $SiteUrl -Interactive
   ```

2. **Verify list name:**
   - Ensure list name in script matches exactly: "AI Marketing Claims Inventory"
   - Check for extra spaces or typos

3. **Check permissions:**
   - User running script needs at minimum Read access
   - For full export, Site Member or higher recommended

4. **Handle large lists:**
   - If list has >5000 items, use `-PageSize 500` parameter
   - Consider filtering by date range

**Root Cause:** Authentication timeout or permission insufficient.

---

### Issue 5: Claim Stuck in "Under Review" Status

**Symptoms:**

- Claim shows "Under Review" for extended period
- No approval request visible to approvers
- Workflow shows "Running" indefinitely

**Resolution Steps:**

1. **Check workflow run history:**
   - Power Automate > Flow > Run history
   - Look for "Waiting for approval" status
   - Identify which approval stage is pending

2. **Check approver availability:**
   - Verify the assigned approver is active in the organization
   - Check if approver has access to approval requests

3. **Locate the approval:**
   - Approver: Check Power Automate > Approvals
   - Or Outlook: Search for approval email
   - Or Teams: Check Approvals app

4. **Cancel and restart if necessary:**
   - Cancel the stuck workflow run
   - Reset claim status to "Draft"
   - Resubmit for review

**Root Cause:** Approval request missed by approver or approver unavailable.

---

### Issue 6: Duplicate Claims Created

**Symptoms:**

- Same claim appears multiple times in inventory
- Workflow triggered multiple times
- Confusion about which version is authoritative

**Resolution Steps:**

1. **Identify duplicates:**
   - Sort list by Submission Date and Claim Text
   - Identify exact or near-duplicate entries

2. **Determine authoritative version:**
   - Keep the claim with most complete information
   - Keep the claim with most recent approval (if approved)

3. **Remove duplicates:**
   - Update duplicate status to "Retired"
   - Add note in comments: "Duplicate of Claim ID X"
   - Do not delete - retain for audit trail

4. **Prevent future duplicates:**
   - Add validation to submission form
   - Implement duplicate detection in workflow

**Root Cause:** Form submitted multiple times or workflow triggered twice.

---

## Escalation Matrix

| Issue Type | First Contact | Escalation 1 | Escalation 2 |
|------------|---------------|--------------|--------------|
| Workflow failure | Power Platform Admin | IT Support | Microsoft Support |
| Permission issues | SharePoint Admin | Security Admin | IT Director |
| Claim content dispute | Compliance Officer | Legal | Chief Compliance Officer |
| Regulatory interpretation | Legal | External Counsel | Regulatory Body |
| Urgent claim (blocking marketing) | Compliance Officer | Legal | CCO + General Counsel |

---

## Known Limitations

| Limitation | Workaround | Status |
|------------|------------|--------|
| Power Automate approval timeout (30 days) | Reminder flow sends weekly nudges | By Design |
| SharePoint column limit (500 columns) | Current implementation uses 15 columns | Acceptable |
| No mobile-optimized claim submission | Use SharePoint mobile app | Future Enhancement |
| Manual substantiation file linking | Copy URL from document library | Future Enhancement |

---

## Support Contacts

| Role | Responsibility | Contact |
|------|----------------|---------|
| Compliance Officer | Claim review, regulatory questions | compliance@company.com |
| AI Governance Lead | Technical accuracy validation | ai-governance@company.com |
| SharePoint Admin | List/library configuration | sharepoint-support@company.com |
| Power Platform Admin | Workflow troubleshooting | powerplatform@company.com |
| Legal | Regulatory interpretation, high-risk claims | legal@company.com |

---

[Back to Control 2.21](../../../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
