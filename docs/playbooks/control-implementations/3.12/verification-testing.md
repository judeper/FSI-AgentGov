# Verification & Testing: Control 3.12 - Agent Governance Exception and Override Management

**Last Updated:** April 2026
**Test Duration:** 60-90 minutes
**Test Environments:** Dataverse test environment, Power Automate test flows

## Overview

This playbook provides comprehensive test cases to verify exception management system functionality including request submission, approval workflows, expiration monitoring, and audit trail integrity.

---

## Test Prerequisites

Before beginning verification testing:

- [ ] Dataverse Governance Exceptions table created with all required columns
- [ ] Power Apps exception request form deployed and shared
- [ ] Power Automate approval workflows configured for all three zones
- [ ] Power Automate expiration monitor flow configured
- [ ] Test user accounts available for requestor and approver roles
- [ ] Teams channel configured for governance alerts
- [ ] PowerShell scripts deployed and tested individually

---

## Test Case 1: Exception Request Submission

### Objective
Verify that users can submit exception requests via Power Apps form with proper validation.

### Test Steps

1. **Open Exception Request Form**
   - Navigate to Power Apps portal (make.powerapps.com)
   - Open "Agent Exception Request Form" app
   - Verify form loads without errors

2. **Test Field Auto-Population**
   - Verify **Requestor** field auto-populates with current user email
   - Verify **Exception Request Date** auto-populates with today's date
   - Verify both fields are read-only (cannot be edited)

3. **Test Form Validation**
   - Leave **Agent Name** blank and click Submit
   - Expected: Error message "Please complete all required fields"
   - Fill **Agent Name:** "TestAgent-3.12-Verification"

4. **Test Zone-Specific Duration Limits**
   - Select **Governance Zone:** Zone 3
   - Set **Expiration Date** to 45 days from today (exceeds 30-day limit)
   - Expected: Error message "Expiration date exceeds maximum duration for selected zone"
   - Adjust **Expiration Date** to 25 days from today
   - Expected: No error

5. **Test Minimum Character Requirements**
   - Enter **Business Justification:** "Test" (only 4 characters)
   - Expected: Warning showing "Characters: 4 / 100 minimum"
   - Expand justification to 100+ characters with valid business reason

6. **Submit Complete Request**
   - Fill all fields:
     - **Agent Name:** TestAgent-3.12-Verification
     - **Governance Zone:** Zone 3
     - **Exception Type:** Policy Override
     - **Business Justification:** [100+ character justification]
     - **Risk Assessment:** [100+ character risk analysis]
     - **Compensating Controls:** [50+ character description]
     - **Expiration Date:** [25 days from today]
   - Click **Submit Exception Request**
   - Expected: Success message "Exception request submitted successfully"

7. **Verify Dataverse Record Creation**
   - Navigate to Power Apps → Tables → Governance Exceptions → Data
   - Find newly created record with Agent Name "TestAgent-3.12-Verification"
   - Verify **Approval Status** = "Pending"
   - Verify **Renewal Count** = 0
   - Verify all submitted data matches form inputs

### Expected Results

✅ Form loads successfully
✅ Auto-population works for Requestor and Request Date
✅ Validation blocks submission with incomplete data
✅ Zone-specific duration validation enforces limits
✅ Character count validation requires minimum lengths
✅ Successful submission creates Dataverse record with status "Pending"

---

## Test Case 2: Zone 1 Approval Workflow (Single Approver)

### Objective
Verify single-level approval workflow for Zone 1 exceptions.

### Test Steps

1. **Submit Zone 1 Exception**
   - In exception request form, select **Governance Zone:** Zone 1
   - Set **Expiration Date:** 80 days from today (within 90-day limit)
   - Complete all required fields
   - Submit request

2. **Verify Approval Flow Trigger**
   - Navigate to Power Automate → My flows → Agent Exception Approval Workflow
   - Check run history for new execution triggered by submission
   - Expected: Flow status = "Running" or "Succeeded"

3. **Verify Approval Email**
   - Log in as Power Platform Admin (Zone 1 approver)
   - Check email inbox for approval request
   - Expected: Email with subject "Agent Exception Request: [Agent Name]"
   - Verify email contains:
     - Requestor name
     - Agent name
     - Exception type
     - Justification
     - Risk assessment
     - Compensating controls
     - Expiration date
     - "Approve" and "Reject" buttons

4. **Test Approval Action**
   - Click **Approve** button in email
   - Add comment: "Approved for Zone 1 testing"
   - Submit approval

5. **Verify Dataverse Update**
   - Navigate to Governance Exceptions table → Data
   - Find the submitted record
   - Verify fields updated:
     - **Approval Status:** "Fully Approved" (Zone 1 requires only one approval)
     - **Approver 1:** [Power Platform Admin name]
     - **Approval Date 1:** [Today's date]

6. **Verify Teams Notification**
   - Open Microsoft Teams → Governance Team → Agent Governance Alerts channel
   - Expected: Adaptive card notification with:
     - Title: "✅ Exception Approved"
     - Agent Name
     - Requestor
     - Exception Type
     - Expiration Date
     - Approver name

### Expected Results

✅ Approval flow triggers automatically on request submission
✅ Single approval email sent to Power Platform Admin only
✅ Approving updates Dataverse with "Fully Approved" status
✅ Teams notification posted for transparency
✅ No second or third approval required for Zone 1

---

## Test Case 3: Zone 3 Approval Workflow (Three-Level Approval)

### Objective
Verify multi-level approval workflow for Zone 3 exceptions with escalating authority.

### Test Steps

1. **Submit Zone 3 Exception**
   - Submit exception request with **Governance Zone:** Zone 3
   - **Expiration Date:** 28 days from today (within 30-day limit)

2. **Level 1 Approval (Manager)**
   - Log in as manager (Level 1 approver)
   - Receive approval email
   - Click **Approve**
   - Add comment: "Level 1 approved - forwarding to Compliance"

3. **Verify Level 1 Update**
   - Check Dataverse record
   - Expected: **Approval Status** = "Level 1 Approved"
   - Expected: **Approver 1** and **Approval Date 1** populated

4. **Level 2 Approval (Compliance Officer)**
   - Log in as Compliance Officer (Level 2 approver)
   - Receive approval email with note "Level 1 approved by [Manager]"
   - Click **Approve**
   - Add comment: "Compliance reviewed - acceptable risk"

5. **Verify Level 2 Update**
   - Check Dataverse record
   - Expected: **Approval Status** = "Level 2 Approved"
   - Expected: **Approver 2** and **Approval Date 2** populated

6. **Level 3 Approval (CISO)**
   - Log in as CISO (Level 3 approver)
   - Receive approval email with notes from Level 1 and Level 2
   - Click **Approve**
   - Add comment: "CISO approval - risk accepted"

7. **Verify Final Approval**
   - Check Dataverse record
   - Expected: **Approval Status** = "Fully Approved"
   - Expected: **Approver 3** and **Approval Date 3** populated

8. **Verify Complete Audit Trail**
   - Review Dataverse record showing:
     - Three distinct approvers
     - Three distinct approval dates
     - Progression: Pending → Level 1 Approved → Level 2 Approved → Fully Approved

### Expected Results

✅ Three sequential approval stages execute in order
✅ Each approver receives email only after previous level approves
✅ Dataverse updates after each approval stage
✅ Final status = "Fully Approved" only after all three approvals
✅ Complete audit trail with all approver names and dates

---

## Test Case 4: Exception Denial

### Objective
Verify that denied exceptions update correctly and do not proceed to subsequent approval levels.

### Test Steps

1. **Submit Exception for Denial**
   - Submit Zone 2 exception request (requires 2 approvals)

2. **Level 1 Denial**
   - Log in as manager (Level 1 approver)
   - Click **Reject** in approval email
   - Add comment: "Insufficient justification - please resubmit with more detail"

3. **Verify Denial Status**
   - Check Dataverse record
   - Expected: **Approval Status** = "Denied"
   - Expected: No Level 2 approval email sent

4. **Verify Requestor Notification**
   - Log in as requestor
   - Expected: Email notification that exception was denied
   - Expected: Email includes denial reason/comment

### Expected Results

✅ Denial stops approval workflow immediately
✅ Status updates to "Denied" without progressing to next level
✅ Requestor receives notification with denial reason
✅ No subsequent approvers are contacted

---

## Test Case 5: Expiration Monitoring

### Objective
Verify that expiration monitor flow detects and alerts on exceptions nearing expiration.

### Test Steps

1. **Create Exception Expiring Soon**
   - Manually create Dataverse record:
     - **Agent Name:** TestAgent-Expiring
     - **Approval Status:** Fully Approved
     - **Expiration Date:** 5 days from today
     - **Requestor:** [Test user]
     - **Approver 1:** [Test approver]

2. **Manually Run Expiration Monitor**
   - Navigate to Power Automate → Exception Expiration Monitor
   - Click **Test** → **Manually** → **Run flow**

3. **Verify Flow Execution**
   - Expected: Flow runs successfully
   - Check flow run history for:
     - "List rows" action found 1 exception (the test record)
     - "Apply to each" loop executed once
     - "Send an email" action succeeded

4. **Verify Email Alert**
   - Check requestor's email inbox
   - Expected: Email with subject "URGENT: Agent Exception Expiring in 5 days"
   - Verify email contains:
     - Agent name
     - Exception type
     - Expiration date
     - Action required (renewal or closure instructions)
     - Current renewal count

5. **Verify CC to Approvers**
   - Check approver email inboxes
   - Expected: Same email CC'd to all approvers from original approval

6. **Verify Teams Alert**
   - Check Teams → Agent Governance Alerts channel
   - Expected: Adaptive card with warning icon and expiring exception details

### Expected Results

✅ Expiration monitor flow detects exceptions expiring within 7 days
✅ Email alerts sent to requestor and approvers
✅ Teams notification posted for governance team visibility
✅ Alert includes renewal instructions and limits

---

## Test Case 6: Expired Exception Detection

### Objective
Verify that already-expired exceptions are detected and flagged.

### Test Steps

1. **Create Already-Expired Exception**
   - Manually create Dataverse record:
     - **Agent Name:** TestAgent-Expired
     - **Approval Status:** Fully Approved
     - **Expiration Date:** Yesterday's date
     - **Requestor:** [Test user]

2. **Run PowerShell Expiration Script**
   ```powershell
   .\Find-ExpiringExceptions.ps1 `
       -EnvironmentUrl "https://contoso.crm.dynamics.com" `
       -OutputPath "C:\TestReports" `
       -ExpirationWindowDays 7
   ```

3. **Verify Script Output**
   - Expected: Console shows "Found 1 exceptions already expired" (red text)
   - Expected: CSV file created in C:\TestReports

4. **Review CSV Report**
   - Open CSV file in Excel
   - Find TestAgent-Expired record
   - Verify columns:
     - **DaysUntilExpiration:** Negative number (e.g., -1)
     - **Status:** "EXPIRED" (red flag)

### Expected Results

✅ Expired exceptions detected separately from expiring exceptions
✅ CSV report flags expired exceptions with "EXPIRED" status
✅ Negative DaysUntilExpiration clearly indicates overdue

---

## Test Case 7: Compliance Report Generation

### Objective
Verify compliance reporting identifies policy violations (excessive duration, renewal limits).

### Test Steps

1. **Create Non-Compliant Exceptions**
   - Create Zone 3 exception with:
     - **Expiration Date:** 90 days from request (exceeds 30-day limit)
     - **Approval Status:** Fully Approved
   - Create Zone 2 exception with:
     - **Renewal Count:** 3 (exceeds 2-renewal limit)
     - **Approval Status:** Fully Approved

2. **Run Compliance Report Script**
   ```powershell
   .\Get-ExceptionComplianceReport.ps1 `
       -EnvironmentUrl "https://contoso.crm.dynamics.com" `
       -OutputPath "C:\TestReports"
   ```

3. **Verify Script Output**
   - Expected: Console shows summary statistics
   - Expected: Non-compliant count > 0

4. **Review Compliance CSV**
   - Open CSV file
   - Find non-compliant records
   - Verify **ComplianceStatus:** "Non-Compliant"
   - Verify **Issues** column contains:
     - "Duration exceeds maximum" for Zone 3 exception
     - "Renewal count exceeds limit" for Zone 2 exception

5. **Verify Summary Statistics**
   - Console should display:
     - Total exceptions
     - Compliant count
     - Non-compliant count
     - Compliance rate percentage
     - Zone-specific breakdown

### Expected Results

✅ Compliance script detects duration violations
✅ Compliance script detects renewal limit violations
✅ Non-compliant exceptions clearly identified in report
✅ Issues column provides specific policy violation details

---

## Test Case 8: Exception Closure

### Objective
Verify proper closure process with documented reason and retention of audit trail.

### Test Steps

1. **Close Expired Exception**
   - Navigate to Dataverse → Governance Exceptions → Data
   - Find an expired or completed exception
   - Edit the record:
     - **Approval Status:** Closed
     - **Closure Date:** Today's date
     - **Closure Reason:** "Issue resolved - DLP policy updated to allow connector permanently"
   - Save record

2. **Verify Closed Exception Excluded from Active Reports**
   - Re-run Find-ExpiringExceptions.ps1
   - Expected: Closed exception does not appear in output (query filters for "Fully Approved" status only)

3. **Verify Audit Trail Preservation**
   - View closed exception record in Dataverse
   - Verify all original data preserved:
     - Request date
     - Requestor
     - Approvers and approval dates
     - Justification and risk assessment
     - Closure reason
   - Expected: No data deleted or overwritten

4. **Test Historical Reporting**
   - Run Get-ExceptionRegister.ps1 with no status filter
   - Expected: Closed exceptions included in full register export for compliance retention

### Expected Results

✅ Closed exceptions excluded from active monitoring
✅ Complete audit trail preserved after closure
✅ Closure reason documented
✅ Historical reporting includes closed exceptions

---

## Test Case 9: Renewal Request Validation

### Objective
Verify that renewal requests increment renewal count and enforce limits.

### Test Steps

1. **Create Exception with 2 Renewals**
   - Manually create Dataverse record:
     - **Renewal Count:** 2
     - **Expiration Date:** 3 days from today
     - **Approval Status:** Fully Approved

2. **Run Expiration Monitor**
   - Expected: Email alert includes warning "Maximum 2 renewals allowed. Current renewal count: 2"

3. **Attempt Third Renewal (Manual Process)**
   - Update record:
     - **Renewal Count:** 3
   - Run compliance report

4. **Verify Compliance Violation**
   - Expected: Compliance report flags as non-compliant with issue "Renewal count exceeds limit (3 > 2)"

### Expected Results

✅ Renewal count tracked accurately
✅ Expiration alerts warn when at renewal limit
✅ Compliance reports flag excessive renewals

---

## Test Case 10: Audit Evidence Export with Integrity Hash

### Objective
Verify evidence export generates SHA-256 hash for regulatory examination.

### Test Steps

1. **Run Audit Evidence Script**
   ```powershell
   .\Export-ExceptionAuditEvidence.ps1 `
       -EnvironmentUrl "https://contoso.crm.dynamics.com" `
       -OutputPath "C:\Evidence" `
       -ExaminerName "Test Auditor" `
       -ExaminationPurpose "Control 3.12 Verification"
   ```

2. **Verify Evidence Directory**
   - Navigate to C:\Evidence\ExceptionEvidence_[timestamp]
   - Expected files:
     - ExceptionRegister.csv
     - EVIDENCE_METADATA.txt
     - SHA256_HASH.txt

3. **Verify Hash File Format**
   - Open SHA256_HASH.txt
   - Expected format: `[64-character hex hash]  ExceptionRegister.csv`

4. **Verify Hash Integrity**
   - Run Windows certutil command:
     ```powershell
     certutil -hashfile C:\Evidence\ExceptionEvidence_[timestamp]\ExceptionRegister.csv SHA256
     ```
   - Compare output hash to SHA256_HASH.txt
   - Expected: Hashes match exactly

5. **Verify Metadata File**
   - Open EVIDENCE_METADATA.txt
   - Verify contains:
     - Export timestamp
     - Environment URL
     - Examiner name
     - Examination purpose
     - File hash
     - Exported by username

### Expected Results

✅ Evidence package created with all required files
✅ SHA-256 hash generated and verified
✅ Metadata includes chain of custody information
✅ Hash verification succeeds with certutil

---

## Integration Test: End-to-End Exception Lifecycle

### Objective
Verify complete exception lifecycle from request to closure.

### Test Steps

1. Submit exception request (Zone 2)
2. Verify Level 1 approval email received
3. Approve at Level 1
4. Verify Level 2 approval email received
5. Approve at Level 2
6. Verify status = "Fully Approved"
7. Verify Teams notification posted
8. Create test with expiration in 5 days
9. Run expiration monitor
10. Verify expiration alert sent
11. Close exception with documented reason
12. Verify excluded from future expiration alerts
13. Export audit evidence and verify hash

### Expected Results

✅ Complete lifecycle executes without errors
✅ All approval stages function correctly
✅ Monitoring detects approaching expiration
✅ Closure preserves audit trail
✅ Evidence export maintains integrity

---

## Performance Testing

### Test Case: High-Volume Exception Processing

**Objective:** Verify system handles multiple simultaneous exception requests.

**Steps:**

1. Submit 10 exception requests within 5 minutes (Zone 1, 2, and 3 mix)
2. Verify all approval flows trigger correctly
3. Monitor Dataverse for record creation
4. Check for any flow failures or timeouts

**Expected Results:**

✅ All requests create Dataverse records
✅ All approval flows trigger and execute
✅ No performance degradation or errors

---

## Security Testing

### Test Case: Unauthorized Access Prevention

**Objective:** Verify security roles prevent unauthorized modifications.

**Steps:**

1. Log in as standard user (non-admin)
2. Navigate to Dataverse → Governance Exceptions → Data
3. Attempt to directly edit an exception record (e.g., change Approval Status to "Fully Approved")
4. Expected: Permission denied error

**Expected Results:**

✅ Non-admin users cannot bypass approval workflow by direct record editing
✅ Security roles enforce read-only access for non-governance team members

---

## Test Summary Checklist

After completing all test cases, verify:

- [ ] Exception request form validates all required fields
- [ ] Zone 1 single-level approval works correctly
- [ ] Zone 3 three-level approval escalates properly
- [ ] Denials stop workflow and notify requestor
- [ ] Expiration monitor detects exceptions within 7 days
- [ ] Expired exceptions flagged separately
- [ ] Compliance report identifies policy violations
- [ ] Closed exceptions preserve audit trail
- [ ] Renewal limits enforced
- [ ] Audit evidence export generates valid SHA-256 hash
- [ ] End-to-end lifecycle completes successfully
- [ ] Security roles prevent unauthorized modifications

---

## Test Evidence Collection

For audit purposes, collect:

1. Screenshots of successful exception request submission
2. Screenshots of approval emails (all three zones)
3. Screenshots of Teams notifications
4. CSV exports from all PowerShell scripts
5. Dataverse record screenshots showing complete audit trail
6. SHA-256 hash verification output
7. Test execution log with timestamps

---

## Next Steps

- Review [Troubleshooting](troubleshooting.md) if any tests fail
- Document any customizations or deviations from standard configuration
- Schedule go-live date after successful verification
- Train governance team and exception requestors

---

[Back to Control 3.12](../../../controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md)

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
