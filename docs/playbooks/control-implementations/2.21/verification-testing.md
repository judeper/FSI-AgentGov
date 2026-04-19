# Verification & Testing: Control 2.21 — AI Marketing Claims and Substantiation

**Last Updated:** April 2026
**Test Surfaces:** SharePoint list/library, Power Automate flows, Purview retention, attestation evidence
**Estimated Time:** 1–2 hours per test cycle
**Audience:** Compliance Officer, AI Governance Lead, SharePoint Admin, Power Platform Admin

---

## Prerequisites

- [ ] [Portal Walkthrough](portal-walkthrough.md) and [PowerShell Setup](powershell-setup.md) complete
- [ ] At least two non-production test user accounts (one submitter, one reviewer) in the test or staging tenant
- [ ] A sandbox or read-replica copy of the AI Governance site for negative testing — do **not** run rejection tests in the production claims list
- [ ] Sample claim text prepared for each category (Performance, Capability, Comparative, Predictive, Efficiency)
- [ ] Compliance Officer available to act as approver during the test window

!!! warning "Do not test in production claims data"
    All test claims must be flagged in the **Claim Text** with a clear `[TEST — DO NOT PUBLISH]` prefix and retired at the end of the cycle. Auditors should be able to filter test artifacts out of any production claims report.

---

## Manual test procedures

### Test 1 — Inventory captures required fields

**Objective:** Confirm every required field is present and saved correctly.

**Steps**

1. Open the **AI Marketing Claims Inventory** list.
2. Click **+ New** and complete:
    - **Claim Text:** `[TEST — DO NOT PUBLISH] Our AI agent processes ~1,000 client documents per business day in steady-state.`
    - **Claim Category:** Performance
    - **Agent / Product:** Onboarding Copilot (test)
    - **Target Channel:** Website
    - **Governance Zone:** Zone 3 — Enterprise
    - **FINRA 2210 Communication:** Retail Communication
3. Save and reopen the item.

**Expected:** All values persist; auto-fields (Submitted By, Submission Date) populate; `Status` defaults to Draft.

**Evidence:** Screenshot of the saved item view.

---

### Test 2 — Pre-publication workflow (Zone 2)

**Objective:** Confirm a Zone 2 claim routes Compliance → AI Governance Lead and skips Legal.

**Steps**

1. Create a `[TEST]` claim with **Governance Zone = Zone 2 — Team**.
2. Set `Status = Under Review` to trigger the flow.
3. Approve at the Compliance step.
4. Approve at the AI Governance Lead step.
5. Confirm no Legal approval is generated.
6. Confirm the item updates to `Status = Approved`, `Approval Date` populated, and `Next Review Date = Approval Date + 90 days`.

**Expected:** Two approval stages, final status Approved, dates correct.

**Evidence:** Power Automate run history; final list item screenshot.

---

### Test 3 — Pre-publication workflow (Zone 3)

**Objective:** Confirm a Zone 3 claim routes Compliance → AI Governance Lead → Legal.

**Steps**

1. Repeat Test 2 with **Governance Zone = Zone 3 — Enterprise**.
2. Confirm the third approval is generated and assigned to the Legal reviewer.
3. Approve all three stages.

**Expected:** Three approval stages, final status Approved.

**Evidence:** Run history showing all three approvals; screenshot of approved item.

---

### Test 4 — Rejection at Compliance

**Objective:** Confirm rejection terminates the flow, captures comments, and notifies the submitter.

**Steps**

1. Create a Zone 3 `[TEST]` claim with deliberately weak substantiation.
2. Set `Status = Under Review`.
3. As Compliance Officer, **Reject** with comment: `Insufficient backtest evidence — sample size below n=200`.
4. Confirm the item updates to `Status = Rejected`, comments are written to `Review Comments`, and the submitter receives a rejection email.
5. Confirm no downstream approvals are generated.

**Evidence:** Screenshot of rejected item with comments; rejection email.

---

### Test 5 — Substantiation file linking

**Objective:** Confirm the substantiation hyperlink resolves to the correct evidence document with appropriate permissions.

**Steps**

1. Upload a sample substantiation document (e.g., a backtest summary PDF) to the appropriate category folder in **AI Claims Substantiation**.
2. Copy the document URL.
3. Edit a claim and paste the URL into **Substantiation File**.
4. Sign in as a different user with Read access and click the link.

**Expected:** Document opens; permissions enforced as expected; URL persists across edits.

**Evidence:** Screenshot of the linked claim and the opened evidence document.

---

### Test 6 — Quarterly reminder

**Objective:** Confirm the scheduled reminder flow surfaces approved claims approaching the next review date.

**Steps**

1. Create an approved `[TEST]` claim and manually edit `Next Review Date` to today + 7 days.
2. Manually run the quarterly review reminder flow.
3. Confirm the named **Compliance Reviewer** receives an email referencing the claim text, original approval date, and substantiation link.

**Expected:** Reminder email delivered; flow run succeeds; the deep link opens the correct list item.

**Evidence:** Reminder email; flow run history.

---

### Test 7 — Approver permission enforcement

**Objective:** Confirm only members of the `AI Claims Approvers` group can approve.

**Steps**

1. As a non-approver test user, attempt to approve an in-flight approval request via Power Automate Approvals.
2. Confirm the request is not visible to the non-approver.
3. As an approver, confirm the request is visible and actionable.

**Expected:** Permissions enforce least-privilege approval. (Helps support FINRA Rule 3110 supervisory controls.)

**Evidence:** Screenshots from both accounts.

---

### Test 8 — Retention label coverage

**Objective:** Confirm new uploads to the substantiation library inherit the firm's records label and that list items are in scope of the published retention policy.

**Steps**

1. Upload a new test document to **AI Claims Substantiation**.
2. In the document's **Details** pane, verify **Retention label** matches the firm's marketing-records label.
3. In Purview, open **Records management → Label policies** and confirm the policy targets both the list and the library.

**Expected:** Label applied automatically; policy scoped correctly. Helps meet books-and-records obligations under FINRA 4511 / SEC 17a-4.

**Evidence:** Screenshot of file details pane; screenshot of Purview policy locations.

---

## Test case matrix

| Test ID | Scenario | Zone | Expected Result | Status |
|---|---|---|---|---|
| TC-2.21-001 | Create new claim with all fields | All | Item saved, Status=Draft | ☐ Pass ☐ Fail |
| TC-2.21-002 | Zone 2 approval flow | Zone 2 | Compliance → AI Governance only | ☐ Pass ☐ Fail |
| TC-2.21-003 | Zone 3 approval flow | Zone 3 | Compliance → AI Governance → Legal | ☐ Pass ☐ Fail |
| TC-2.21-004 | Approve to completion | All | Status=Approved; Next Review = +90d | ☐ Pass ☐ Fail |
| TC-2.21-005 | Reject at Compliance | All | Status=Rejected; submitter notified | ☐ Pass ☐ Fail |
| TC-2.21-006 | Substantiation link | Zone 2/3 | URL resolves with correct permissions | ☐ Pass ☐ Fail |
| TC-2.21-007 | Quarterly reminder | Zone 3 | Reminder delivered to reviewer | ☐ Pass ☐ Fail |
| TC-2.21-008 | Inventory CSV export | All | CSV + SHA-256 sidecar generated | ☐ Pass ☐ Fail |
| TC-2.21-009 | Retire approved claim | All | Status=Retired; record preserved | ☐ Pass ☐ Fail |
| TC-2.21-010 | Approver permission enforcement | All | Only approvers can act | ☐ Pass ☐ Fail |
| TC-2.21-011 | Retention label coverage | Zone 2/3 | Label applied; policy targets list and library | ☐ Pass ☐ Fail |
| TC-2.21-012 | FINRA 2210 classification recorded | Zone 3 | Field populated and visible in export | ☐ Pass ☐ Fail |

---

## Evidence checklist

For audit and compliance reviews, retain the following:

- [ ] Screenshot: Claims Inventory list with sample (test) claims clearly tagged
- [ ] Screenshot: Substantiation library folder structure and an example evidence document with retention label visible
- [ ] Screenshot: Power Automate flow definition (pre-publication and reminder)
- [ ] Screenshot: Successful approval run history (Zone 2 and Zone 3)
- [ ] Screenshot: Rejection email received by submitter
- [ ] Screenshot: Quarterly reminder email
- [ ] Document: Inventory export CSV plus its SHA-256 sidecar (from PowerShell Script 3)
- [ ] Document: Test results matrix above with reviewer sign-off
- [ ] Document: Reference to the WSP section that incorporates this workflow

---

## Attestation template

The wording below is intended as a starting point. Compliance and Legal should adapt it to the firm's own attestation standard before use.

```
AI MARKETING CLAIMS CONTROL — ATTESTATION
Control 2.21 — AI Marketing Claims and Substantiation
Framework Version: 1.3.3

Organization: ____________________________________
Attestation Period: ______________________________
Attestation Date: ________________________________

Based on the evidence collected for the period above, I attest that:

  1. [ ] An AI Marketing Claims Inventory is operational as the system of
         record for AI-related marketing claims.
  2. [ ] A documented pre-publication review workflow is configured, was
         tested during the period, and is followed for Zone 2 and Zone 3
         claims as defined in Control 2.21.
  3. [ ] A substantiation evidence library is configured and is in scope of
         the firm's retention label policy aligned with applicable
         books-and-records obligations (e.g., FINRA Rule 4511, SEC Rule
         17a-4) as confirmed by Compliance.
  4. [ ] A quarterly review process is documented and was executed during
         the period; reminders were generated for claims approaching their
         Next Review Date.
  5. [ ] All Zone 3 AI marketing claims active during the period received
         pre-publication review by Compliance, AI Governance, and Legal.
  6. [ ] A documented process exists to identify, withdraw, and correct
         AI marketing claims subsequently determined to be materially
         misleading. Remediation events during the period are summarized
         below (or "none identified").
  7. [ ] Marketing, sales, and other content-producing staff have completed
         AI claims training within the firm's recertification window.

Period Summary:
  - Total active claims:                     ____
  - New claims approved (Zone 3):            ____
  - Claims pending review at period end:     ____
  - Claims due for quarterly re-review next  ____
    30 days:
  - Claims withdrawn or corrected during     ____
    the period (with reference IDs):

Exceptions / Findings:
__________________________________________________________________
__________________________________________________________________

Attested By: ______________________________________
Title:        ______________________________________
Date:         ______________________________________

Reviewed By:  ______________________________________
Title:        Compliance Officer
Date:         ______________________________________
```

!!! tip "Attestation language hedging"
    The wording above intentionally avoids "ensures compliance" or "guarantees." Attestations describe the operation of the control during a defined period; they do not warrant the firm's regulatory status as a whole.

---

[Back to Control 2.21](../../../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
