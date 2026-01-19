# Verification Testing: Control 2.21 - AI Marketing Claims and Substantiation

**Last Updated:** January 2026
**Test Environment:** SharePoint, Power Automate
**Estimated Time:** 1-2 hours

## Prerequisites

- [ ] Control 2.21 implementation complete (portal walkthrough)
- [ ] Test user accounts with appropriate permissions
- [ ] Sample claims for testing prepared
- [ ] Compliance Officer available for approval testing

---

## Manual Test Steps

### Test 1: Claims Inventory List Functionality

**Objective:** Verify the claims inventory list captures all required information.

**Steps:**

1. Navigate to AI Marketing Claims Inventory list
2. Click **+ New** to create a test claim
3. Complete all required fields:
   - Claim Text: "Test claim - AI processes 1000 documents per hour"
   - Claim Category: Performance
   - Agent/Product: Test Agent
   - Target Channel: Website
   - Governance Zone: Zone 3 - Enterprise
4. Save the item
5. Verify all fields saved correctly
6. Verify auto-generated fields populated (if configured)

**Expected Result:** Item created with all fields populated; no errors.

**Evidence:** Screenshot of completed list item.

---

### Test 2: Pre-Publication Workflow Execution

**Objective:** Verify the approval workflow triggers and routes correctly.

**Steps:**

1. Create a new claim in the inventory list (Status: Draft)
2. Update status to "Under Review" to trigger workflow
3. Verify Compliance Officer receives approval request
4. As Compliance Officer: Approve the request
5. Verify AI Governance Lead receives technical review request
6. As AI Governance Lead: Approve the request
7. For Zone 3 claims: Verify Legal receives review request
8. Complete final approval
9. Verify claim status updates to "Approved"
10. Verify Approval Date and Next Review Date populated

**Expected Result:** Workflow completes all approval stages; status updates correctly.

**Evidence:** Screenshots of each approval stage; workflow run history.

---

### Test 3: Substantiation File Linking

**Objective:** Verify substantiation evidence can be linked to claims.

**Steps:**

1. Upload a test document to AI Claims Substantiation library
2. Navigate to an existing claim in the inventory
3. Edit the claim and add Substantiation File URL
4. Save and verify link works correctly
5. Click the link to confirm document opens

**Expected Result:** Document link saves correctly and opens when clicked.

**Evidence:** Screenshot showing linked substantiation file.

---

### Test 4: Quarterly Review Reminder

**Objective:** Verify review reminders trigger for claims approaching review date.

**Steps:**

1. Create a test claim with Approval Date = Today - 80 days
2. Set Next Review Date = Today + 10 days
3. Manually trigger the quarterly review flow (or wait for scheduled run)
4. Verify reminder email sent to Compliance Reviewer

**Expected Result:** Reminder email received with claim details and review deadline.

**Evidence:** Screenshot of reminder email.

---

### Test 5: Rejection Workflow

**Objective:** Verify rejected claims are handled correctly.

**Steps:**

1. Submit a new claim for review
2. As Compliance Officer: Reject the claim with comments
3. Verify submitter receives rejection notification
4. Verify claim status updates to "Rejected"
5. Verify rejection comments are recorded

**Expected Result:** Rejection processed; submitter notified; status updated.

**Evidence:** Screenshot of rejected claim and notification email.

---

## Test Cases Table

| Test ID | Test Case | Zone | Expected Result | Status |
|---------|-----------|------|-----------------|--------|
| TC-2.21-001 | Create new claim with all fields | All | Item created successfully | ☐ Pass ☐ Fail |
| TC-2.21-002 | Submit claim for Zone 2 review | Zone 2 | Compliance approval only | ☐ Pass ☐ Fail |
| TC-2.21-003 | Submit claim for Zone 3 review | Zone 3 | Full review (Compliance + Legal) | ☐ Pass ☐ Fail |
| TC-2.21-004 | Approve claim through workflow | All | Status = Approved; dates set | ☐ Pass ☐ Fail |
| TC-2.21-005 | Reject claim at compliance stage | All | Status = Rejected; notified | ☐ Pass ☐ Fail |
| TC-2.21-006 | Link substantiation file | Zone 2/3 | URL saves and opens | ☐ Pass ☐ Fail |
| TC-2.21-007 | Quarterly review reminder | Zone 3 | Reminder email sent | ☐ Pass ☐ Fail |
| TC-2.21-008 | Export claims report | All | CSV generated with all claims | ☐ Pass ☐ Fail |
| TC-2.21-009 | Retire approved claim | All | Status = Retired; preserved | ☐ Pass ☐ Fail |
| TC-2.21-010 | Permission enforcement | All | Only authorized users can approve | ☐ Pass ☐ Fail |

---

## Evidence Checklist

For audit and compliance documentation, collect the following evidence:

- [ ] Screenshot: Claims inventory list with sample claims
- [ ] Screenshot: Substantiation library folder structure
- [ ] Screenshot: Power Automate workflow definition
- [ ] Screenshot: Successful workflow run history
- [ ] Screenshot: Approval email notification
- [ ] Screenshot: Quarterly review reminder email
- [ ] Document: Claims inventory export (CSV)
- [ ] Document: Test results summary with sign-off

---

## Attestation Template

```
AI MARKETING CLAIMS CONTROL ATTESTATION
Control 2.21 - AI Marketing Claims and Substantiation
Framework Version: 1.1

Organization: ____________________________________
Attestation Date: ____________________________________

I attest that:

1. [ ] AI Marketing Claims Inventory is established and operational
2. [ ] Pre-publication review workflow is configured and tested
3. [ ] Substantiation evidence library is configured with appropriate retention
4. [ ] Quarterly review process is documented and automated
5. [ ] All Zone 3 AI marketing claims have been reviewed by Compliance and Legal
6. [ ] Marketing team has completed training on AI claim requirements

Current Claims Status:
- Total Active Claims: ____
- Claims Approved (Zone 3): ____
- Claims Pending Review: ____
- Claims Due for Quarterly Review: ____

Exceptions/Findings:
_________________________________________________________________
_________________________________________________________________

Attested By: ____________________________________
Title: ____________________________________
Date: ____________________________________

Reviewed By: ____________________________________
Title: Compliance Officer
Date: ____________________________________
```

---

[Back to Control 2.21](../../../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
