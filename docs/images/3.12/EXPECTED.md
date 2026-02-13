# Control 3.12: Agent Governance Exception and Override Management - Screenshot Specifications

## Required Screenshots

### Screenshot 1: Dataverse - Governance Exceptions Table Schema
**Portal Path:** Power Apps → Tables → Governance Exceptions → Columns
**What to capture:**
- Dataverse table definition showing all custom columns for exception tracking
- Table name in header: "Governance Exceptions (fsi_governanceexception)"
- Columns visible with data types:
  - fsi_exceptionrequestdate (Date and time)
  - fsi_requestor (Lookup → User)
  - fsi_agentname (Text)
  - fsi_governancezone (Choice: Zone 1, Zone 2, Zone 3)
  - fsi_exceptiontype (Choice: Policy Override, Approval Bypass, etc.)
  - fsi_businessjustification (Text area)
  - fsi_riskassessment (Text area)
  - fsi_compensatingcontrols (Text area)
  - fsi_approvalstatus (Choice: Pending, Level 1 Approved, etc.)
  - fsi_approver1 (Lookup → User)
  - fsi_approvaldate1 (Date and time)
  - fsi_approver2 (Lookup → User)
  - fsi_approvaldate2 (Date and time)
  - fsi_approver3 (Lookup → User)
  - fsi_approvaldate3 (Date and time)
  - fsi_expirationdate (Date)
  - fsi_renewalcount (Whole number)
  - fsi_closuredate (Date and time)
  - fsi_closurereason (Text area)
- Column properties visible (data type, required status)
- Table settings showing "Audit changes to its data" enabled
- Demonstrates complete schema design for exception tracking

---

### Screenshot 2: Dataverse - Governance Exceptions Sample Data
**Portal Path:** Power Apps → Tables → Governance Exceptions → Data
**What to capture:**
- Grid view of exception records showing at least 10 sample exceptions
- Columns visible: Name, Agent Name, Governance Zone, Exception Type, Approval Status, Expiration Date, Renewal Count
- Mix of approval statuses:
  - Pending (2-3 records)
  - Fully Approved (5-6 records)
  - Expired (1-2 records)
  - Closed (1-2 records)
- Mix of zones: Zone 1, Zone 2, Zone 3
- Expiration dates showing some in past (expired), some within 7 days (expiring soon), some future
- Demonstrates active exception register with realistic data

---

### Screenshot 3: Power Apps - Exception Request Form Canvas
**Portal Path:** Power Apps → Apps → Agent Exception Request Form → Edit
**What to capture:**
- Canvas app editor showing complete exception request form
- Form fields visible in layout:
  - Header: "Agent Governance Exception Request"
  - Exception Request Date (read-only, auto-populated)
  - Requestor (read-only, auto-populated with User().Email)
  - Agent Name (text input)
  - Governance Zone (dropdown: Zone 1, Zone 2, Zone 3)
  - Exception Type (dropdown)
  - Business Justification (multiline text area with character count)
  - Risk Assessment (multiline text area)
  - Compensating Controls (multiline text area)
  - Expiration Date (date picker with zone-based duration guidance)
  - Submit button at bottom
- Professional form layout with clear labels and validation indicators
- Data source panel showing connection to Governance Exceptions table
- Demonstrates user-friendly request submission interface

---

### Screenshot 4: Power Apps - Form Validation Error
**Portal Path:** Power Apps → Agent Exception Request Form (Play mode)
**What to capture:**
- Exception request form in play mode showing validation errors
- Agent Name field: blank with red error indicator
- Business Justification: "Test" (insufficient characters) with error message "Characters: 4 / 100 minimum"
- Expiration Date: Set to 50 days from today for Zone 3 with error "Expiration date exceeds maximum duration for selected zone (30 days)"
- Submit button: Disabled or showing error message when clicked
- Error notification banner at top: "Please complete all required fields with sufficient detail"
- Demonstrates field-level validation enforcement

---

### Screenshot 5: Power Automate - Exception Approval Workflow Overview
**Portal Path:** Power Automate → My flows → Agent Exception Approval Workflow
**What to capture:**
- Flow overview page showing complete approval workflow structure
- Flow name: "Agent Exception Approval Workflow"
- Trigger: When a row is added (Dataverse) - Governance Exceptions table
- Flow steps visible in collapsed view:
  1. When a row is added (trigger)
  2. Condition (Check if status = Pending)
  3. Switch (Zone-based routing)
     - Case 1: Zone 1 (1 approval stage)
     - Case 2: Zone 2 (2 approval stages)
     - Case 3: Zone 3 (3 approval stages)
  4. Post adaptive card in Teams
- Flow status: On (enabled)
- Last run: Success (green checkmark)
- Run history showing recent executions
- Demonstrates multi-zone approval orchestration

---

### Screenshot 6: Power Automate - Zone 3 Approval Branch Detail
**Portal Path:** Power Automate → Agent Exception Approval Workflow → Edit (Zone 3 branch expanded)
**What to capture:**
- Detailed view of Zone 3 approval branch showing three sequential approval stages
- **Level 1 Approval:**
  - Start and wait for an approval (Approve/Reject)
  - Assigned to: Manager email
  - Title: "Agent Exception Request: [Agent Name]"
  - Details: Full exception information
- **Condition:** Check if Level 1 approved
  - Yes branch → Update row (Status = "Level 1 Approved")
  - No branch → Update row (Status = "Denied")
- **Level 2 Approval:**
  - Start and wait for an approval
  - Assigned to: Compliance Officer email
  - Includes note "Level 1 approved by [Manager]"
- **Condition:** Check if Level 2 approved
  - Yes branch → Update row (Status = "Level 2 Approved")
- **Level 3 Approval:**
  - Start and wait for an approval
  - Assigned to: CISO email
  - Includes notes from Level 1 and Level 2
- **Final Condition:** Check if Level 3 approved
  - Yes branch → Update row (Status = "Fully Approved")
- Demonstrates three-level escalation for Zone 3 exceptions

---

### Screenshot 7: Power Automate - Approval Email Received
**Portal Path:** Outlook → Inbox (Approver's view)
**What to capture:**
- Email from "Microsoft Power Automate" or flow owner
- Subject: "Agent Exception Request: TestAgent-3.12"
- Email body showing:
  - Approval request header
  - Exception details:
    - Requestor: john.doe@contoso.com
    - Agent Name: TestAgent-3.12
    - Exception Type: Policy Override
    - Governance Zone: Zone 3
    - Justification: [Full justification text]
    - Risk Assessment: [Full risk text]
    - Compensating Controls: [Control description]
    - Expiration Date: 2026-03-15
  - Action buttons: **Approve** and **Reject** (prominent blue and red buttons)
  - "View approval" link to Power Automate approval center
- Email received timestamp
- Demonstrates professional approval request format

---

### Screenshot 8: Power Automate - Approval Action Response
**Portal Path:** Outlook → Approval email → Click Approve → Add comments → Submit
**What to capture:**
- Approval response dialog within email
- Comment box with text: "Level 1 approved - risk is acceptable with documented compensating controls"
- Submit button highlighted
- OR: Screenshot of Actionable Message Success notification: "Your response has been submitted"
- Demonstrates inline approval action from email

---

### Screenshot 9: Power Automate - Flow Run History (Successful)
**Portal Path:** Power Automate → Agent Exception Approval Workflow → Run history → [Recent successful run]
**What to capture:**
- Flow run detail showing all steps executed successfully
- All actions with green checkmarks:
  - When a row is added (trigger) - Duration: <1 sec
  - Condition (Check Pending) - Yes branch taken
  - Switch (Zone routing) - Zone 3 case matched
  - Start and wait for approval (Level 1) - Duration: 2m 15s (time until approver responded)
  - Update a row (Level 1 Approved)
  - Start and wait for approval (Level 2) - Duration: 5m 32s
  - Update a row (Level 2 Approved)
  - Start and wait for approval (Level 3) - Duration: 1m 48s
  - Update a row (Fully Approved)
  - Post adaptive card in Teams - Success
- Total flow duration: 9m 45s
- No errors or warnings
- Demonstrates successful multi-stage approval execution

---

### Screenshot 10: Dataverse - Exception Record with Complete Approval Trail
**Portal Path:** Power Apps → Tables → Governance Exceptions → Data → [Open specific record]
**What to capture:**
- Detail view of exception record showing complete audit trail
- Fields populated:
  - Exception Name: EXC-2026-001
  - Exception Request Date: 2026-02-10
  - Requestor: john.doe@contoso.com
  - Agent Name: TestAgent-3.12
  - Governance Zone: Zone 3 - Enterprise
  - Exception Type: Policy Override
  - Business Justification: [Full text visible]
  - Risk Assessment: [Full text visible]
  - Compensating Controls: [Full text visible]
  - Approval Status: Fully Approved
  - Approver 1: Jane Manager (john.manager@contoso.com)
  - Approval Date 1: 2026-02-10 10:15 AM
  - Approver 2: Bob Compliance (bob.compliance@contoso.com)
  - Approval Date 2: 2026-02-10 10:20 AM
  - Approver 3: Carol CISO (carol.ciso@contoso.com)
  - Approval Date 3: 2026-02-10 10:22 AM
  - Expiration Date: 2026-03-12
  - Renewal Count: 0
  - Closure Date: (blank - still active)
  - Closure Reason: (blank)
- Created On, Modified On timestamps visible
- Demonstrates complete approval audit trail

---

### Screenshot 11: Teams - Exception Approved Notification
**Portal Path:** Microsoft Teams → Governance Team → Agent Governance Alerts channel
**What to capture:**
- Teams channel showing adaptive card notification from Flow bot
- Notification card:
  - Title: "✅ Exception Approved" (green checkmark, large bold text)
  - Card body with fact set:
    - Agent Name: TestAgent-3.12
    - Requestor: john.doe@contoso.com
    - Exception Type: Policy Override
    - Governance Zone: Zone 3 - Enterprise
    - Expiration Date: 2026-03-12 (30 days)
    - Approvers: Jane Manager, Bob Compliance, Carol CISO
  - Card footer: Posted timestamp
- Previous messages in channel showing historical notifications
- Demonstrates real-time governance transparency

---

### Screenshot 12: Power Automate - Exception Expiration Monitor Flow
**Portal Path:** Power Automate → My flows → Exception Expiration Monitor
**What to capture:**
- Flow overview showing scheduled expiration monitoring
- Flow name: "Exception Expiration Monitor"
- Trigger: Recurrence (Daily at 8:00 AM)
- Flow steps:
  1. Recurrence trigger
  2. List rows (Dataverse) - Filter: Approved exceptions expiring within 7 days
  3. Apply to each (loop through expiring exceptions)
     - Send an email (to requestor)
     - Post adaptive card in Teams
- Flow status: On (enabled)
- Next run scheduled: Tomorrow at 8:00 AM
- Last run: Success (today at 8:00 AM)
- Demonstrates automated expiration alerting

---

### Screenshot 13: Outlook - Expiration Warning Email
**Portal Path:** Outlook → Inbox (Requestor's view)
**What to capture:**
- Email from automated expiration monitor
- Subject: "URGENT: Agent Exception Expiring in 5 days"
- Email body:
  - Warning header with icon
  - Exception details:
    - Agent Name: TestAgent-OldException
    - Exception Type: Risk Acceptance
    - Original Request Date: 2026-01-10
    - Expiration Date: 2026-02-17 (5 days from now)
    - Current Renewal Count: 1
  - Action required section:
    - "If the underlying issue has been remediated, close the exception in Dataverse."
    - "If additional time is needed, submit a renewal request with updated justification."
  - Renewal limit warning: "Maximum 2 renewals allowed. Current count: 1. One renewal remaining."
  - Links:
    - "Close Exception" (link to Dataverse record)
    - "Submit Renewal Request" (link to Power Apps form)
- Email CC'd to original approvers
- Demonstrates proactive expiration management

---

### Screenshot 14: Teams - Expiration Warning Adaptive Card
**Portal Path:** Microsoft Teams → Governance Team → Agent Governance Alerts channel
**What to capture:**
- Adaptive card with warning styling (orange/yellow accent)
- Title: "⚠️ Exception Expiring Soon"
- Card body:
  - Agent Name: TestAgent-OldException
  - Requestor: john.doe@contoso.com
  - Exception Type: Risk Acceptance
  - Expiration Date: 2026-02-17 (5 days)
  - Days Until Expiration: 5
  - Status: WARNING
  - Renewal Count: 1 / 2
- Action buttons (if using button-enabled cards):
  - "View Exception"
  - "Request Renewal"
- Posted timestamp
- Demonstrates governance team alerting for oversight

---

### Screenshot 15: PowerShell Console - Get-ExceptionRegister.ps1 Execution
**What to capture:**
- PowerShell console showing execution of exception register export script
- Command line: `.\Get-ExceptionRegister.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -OutputPath "C:\Reports"`
- Console output:
  - "======================================" (Cyan)
  - "Exception Register Export" (Cyan)
  - "======================================" (Cyan)
  - "Connecting to Dataverse environment: https://contoso.crm.dynamics.com..." (Cyan)
  - "✓ Connected successfully" (Green)
  - "Querying Governance Exceptions table..." (Cyan)
  - "Found 42 exception records" (White)
  - "✓ Exception register exported to: C:\Reports\ExceptionRegister_20260212-145030.csv" (Green)
  - "--- Exception Register Summary ---" (Cyan)
  - "Total Exceptions: 42" (White)
  - "  Pending: 5" (Yellow)
  - "  Fully Approved: 28" (Green)
  - "  Expired: 3" (Red)
  - "  Closed: 4" (Gray)
  - "  Denied: 2" (Red)
  - "Script completed successfully." (Cyan)
- PowerShell version visible in window title
- Demonstrates successful exception register export

---

### Screenshot 16: Excel - Exception Register CSV Export
**What to capture:**
- Excel spreadsheet showing exported exception register data
- File name in Excel title bar: "ExceptionRegister_20260212-145030.csv"
- Columns visible:
  - ExceptionID (GUID)
  - ExceptionName (EXC-2026-001, etc.)
  - RequestDate (2026-01-15)
  - Requestor (john.doe@contoso.com)
  - AgentName (TestAgent-1)
  - GovernanceZone (Zone 3 - Enterprise)
  - ExceptionType (Policy Override)
  - BusinessJustification (truncated in cell, full text in formula bar when selected)
  - RiskAssessment (text)
  - CompensatingControls (text)
  - ApprovalStatus (Fully Approved)
  - Approver1 (Jane Manager)
  - ApprovalDate1 (2026-01-15)
  - Approver2 (Bob Compliance)
  - ApprovalDate2 (2026-01-15)
  - Approver3 (Carol CISO)
  - ApprovalDate3 (2026-01-15)
  - ExpirationDate (2026-02-15)
  - RenewalCount (0)
  - ClosureDate (blank for active)
  - ClosureReason (blank)
  - CreatedOn (2026-01-15 09:30:00)
  - ModifiedOn (2026-01-15 10:45:00)
- At least 15-20 sample rows visible
- Professional Excel formatting (column headers bold, dates formatted)
- Demonstrates comprehensive exception data export for audits

---

### Screenshot 17: PowerShell Console - Find-ExpiringExceptions.ps1 Execution
**What to capture:**
- PowerShell console showing expiration detection script
- Command line: `.\Find-ExpiringExceptions.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -OutputPath "C:\Reports" -ExpirationWindowDays 7`
- Console output:
  - "======================================" (Cyan)
  - "Exception Expiration Monitor" (Cyan)
  - "Connecting to Dataverse environment..." (Cyan)
  - "✓ Connected successfully" (Green)
  - "Searching for exceptions expiring between 2026-02-12 and 2026-02-19..." (Cyan)
  - "Found 8 exceptions expiring within 7 days" (Yellow)
  - "Found 3 exceptions already expired" (Red)
  - "✓ Expiring exceptions report saved to: C:\Reports\ExpiringExceptions_20260212-150000.csv" (Green)
  - "--- Expiration Summary ---" (Cyan)
  - "Total Expiring/Expired: 11" (White)
  - "  EXPIRED: 3" (Red)
  - "  CRITICAL (<=3 days): 2" (Red)
  - "  WARNING (<=7 days): 6" (Yellow)
  - "  Max Renewals Reached: 1" (Red)
  - "Script completed successfully." (Cyan)
- Demonstrates expiration detection and severity classification

---

### Screenshot 18: Excel - Expiring Exceptions Report
**What to capture:**
- Excel spreadsheet showing expiring exceptions report
- File name: "ExpiringExceptions_20260212-150000.csv"
- Columns visible:
  - ExceptionID
  - AgentName
  - Requestor
  - GovernanceZone
  - ExceptionType
  - ExpirationDate
  - DaysUntilExpiration (-2, 1, 3, 5, 6, etc.)
  - Status (EXPIRED, CRITICAL (<=3 days), WARNING (<=7 days))
  - RenewalCount (0, 1, 2, 3)
  - MaxRenewalsReached (YES, NO)
  - Approver1, Approver2, Approver3
- Rows sorted by DaysUntilExpiration (ascending, showing expired first)
- Conditional formatting or color-coding:
  - Red highlighting for EXPIRED and CRITICAL rows
  - Yellow highlighting for WARNING rows
  - Red highlighting for MaxRenewalsReached = YES
- Demonstrates actionable remediation report

---

### Screenshot 19: PowerShell Console - Get-ExceptionComplianceReport.ps1 Execution
**What to capture:**
- PowerShell console showing compliance analysis script
- Command line: `.\Get-ExceptionComplianceReport.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -OutputPath "C:\Reports"`
- Console output:
  - "======================================" (Cyan)
  - "Exception Compliance Report" (Cyan)
  - "Connecting to Dataverse environment..." (Cyan)
  - "✓ Connected successfully" (Green)
  - "Querying all active exceptions..." (Cyan)
  - "Analyzing 28 active exceptions for compliance..." (Cyan)
  - "✓ Compliance report saved to: C:\Reports\ExceptionComplianceReport_20260212-151500.csv" (Green)
  - "--- Compliance Summary ---" (Cyan)
  - "Total Active Exceptions: 28" (White)
  - "  Compliant: 22" (Green)
  - "  Non-Compliant: 6" (Red)
  - "Compliance Rate: 78.57%" (White)
  - "--- Compliance by Zone ---" (Cyan)
  - "Zone 1 - Personal: 10 / 10 (100.00%)" (White)
  - "Zone 2 - Team: 11 / 12 (91.67%)" (White)
  - "Zone 3 - Enterprise: 1 / 6 (16.67%)" (White) - Flagged concern
  - "⚠ WARNING: 6 non-compliant exceptions require immediate review" (Yellow)
  - "Script completed successfully." (Cyan)
- Demonstrates zone-specific compliance monitoring

---

### Screenshot 20: Excel - Exception Compliance Report
**What to capture:**
- Excel spreadsheet showing compliance analysis
- File name: "ExceptionComplianceReport_20260212-151500.csv"
- Columns visible:
  - ExceptionID
  - AgentName
  - GovernanceZone
  - ExceptionType
  - DurationDays (15, 45, 95, etc.)
  - MaxAllowedDays (30 for Zone 3, 60 for Zone 2, 90 for Zone 1)
  - RenewalCount (0, 1, 2, 3)
  - ComplianceStatus (Compliant, Non-Compliant)
  - Issues (e.g., "Duration exceeds maximum (95 days > 30 days); Renewal count exceeds limit (3 > 2)")
- Rows with ComplianceStatus = "Non-Compliant" highlighted in red
- Filter showing only non-compliant exceptions for remediation focus
- Demonstrates policy violation detection

---

### Screenshot 21: PowerShell Console - Export-ExceptionAuditEvidence.ps1 Execution
**What to capture:**
- PowerShell console showing audit evidence export
- Command line: `.\Export-ExceptionAuditEvidence.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -OutputPath "C:\Evidence" -ExaminerName "SEC Examiner" -ExaminationPurpose "Cybersecurity Rule Examination"`
- Console output:
  - "======================================" (Cyan)
  - "Exception Audit Evidence Export" (Cyan)
  - "Evidence directory: C:\Evidence\ExceptionEvidence_20260212-153000" (Cyan)
  - "Connecting to Dataverse environment..." (Cyan)
  - "✓ Connected successfully" (Green)
  - "Exporting exception register..." (Cyan)
  - "✓ Exception register exported" (Green)
  - "Calculating SHA-256 integrity hash..." (Cyan)
  - "✓ SHA-256 hash: a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456" (Green)
  - "✓ Evidence metadata created" (Green)
  - "✓ Hash verification file created" (Green)
  - "======================================" (Cyan)
  - "Evidence Package Complete" (Cyan)
  - "Location: C:\Evidence\ExceptionEvidence_20260212-153000" (White)
  - "Files included:" (Cyan)
  - "  - ExceptionRegister.csv (exception data)" (White)
  - "  - EVIDENCE_METADATA.txt (chain of custody)" (White)
  - "  - SHA256_HASH.txt (integrity verification)" (White)
  - "To verify file integrity later, run:" (Cyan)
  - "  certutil -hashfile ExceptionRegister.csv SHA256" (Yellow)
  - "Script completed successfully." (Cyan)
- Demonstrates regulatory examination evidence preparation

---

### Screenshot 22: File Explorer - Evidence Package Directory
**What to capture:**
- Windows File Explorer showing evidence package directory
- Path: C:\Evidence\ExceptionEvidence_20260212-153000
- Three files visible:
  - ExceptionRegister.csv (Size: 45 KB, Date: 2026-02-12 3:30 PM)
  - EVIDENCE_METADATA.txt (Size: 2 KB, Date: 2026-02-12 3:30 PM)
  - SHA256_HASH.txt (Size: 1 KB, Date: 2026-02-12 3:30 PM)
- File properties showing Date Created and Date Modified match
- Demonstrates complete evidence package

---

### Screenshot 23: Notepad - EVIDENCE_METADATA.txt Contents
**What to capture:**
- Notepad showing evidence metadata file contents
- File content:
```
===========================================
EXCEPTION REGISTER AUDIT EVIDENCE
===========================================

Export Timestamp: 2026-02-12 15:30:00 UTC
Environment URL: https://contoso.crm.dynamics.com
Examiner Name: SEC Examiner
Examination Purpose: Cybersecurity Rule Examination
Exported By: jdoe
Export Host: ADMINPC01

--- FILE INTEGRITY ---
File Name: ExceptionRegister.csv
File Size: 46080 bytes
SHA-256 Hash: a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456

--- DATA SUMMARY ---
Total Records: 42
Date Range: 2025-11-01 to 2026-02-12

===========================================
```
- Demonstrates chain of custody documentation

---

### Screenshot 24: Notepad - SHA256_HASH.txt Contents
**What to capture:**
- Notepad showing hash verification file
- File content:
```
a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456  ExceptionRegister.csv
```
- Simple format matching standard hash file conventions
- Demonstrates integrity verification mechanism

---

### Screenshot 25: PowerShell Console - certutil Hash Verification
**What to capture:**
- PowerShell console showing hash verification command and output
- Command line: `certutil -hashfile C:\Evidence\ExceptionEvidence_20260212-153000\ExceptionRegister.csv SHA256`
- Output:
```
SHA256 hash of ExceptionRegister.csv:
a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
CertUtil: -hashfile command completed successfully.
```
- Manual comparison: Hash from certutil matches SHA256_HASH.txt
- Demonstrates successful integrity verification

---

### Screenshot 26: Power BI Desktop - Exception Dashboard Design
**What to capture:**
- Power BI Desktop showing exception management dashboard
- Dashboard title: "Agent Governance Exception Dashboard"
- Visuals:
  1. **Active Exceptions by Zone** (Clustered column chart):
     - X-axis: Zone 1 (10), Zone 2 (12), Zone 3 (6)
     - Legend: Approval Status (Fully Approved, Pending)
  2. **Exceptions by Type** (Pie chart):
     - Policy Override: 45%
     - Approval Bypass: 25%
     - Risk Acceptance: 20%
     - Inventory Grace Period: 10%
  3. **Expiring Exceptions (Next 30 Days)** (Table):
     - Columns: Agent Name, Requestor, Type, Expiration Date, Days Until Exp
     - 8 rows showing sorted by Days Until Exp (ascending)
  4. **Renewal Count Distribution** (Bar chart):
     - 0 renewals: 20 exceptions
     - 1 renewal: 5 exceptions
     - 2 renewals: 3 exceptions
     - 3+ renewals: 1 exception (flagged)
  5. **Compliance Rate** (Card visual):
     - Large number: 78.57%
     - Subtitle: "28 Active Exceptions, 22 Compliant"
- Professional color scheme and formatting
- Demonstrates executive-level exception visibility

---

### Screenshot 27: Power BI Service - Published Dashboard
**Portal Path:** Power BI Service (app.powerbi.com) → Workspace → Agent Governance Dashboard
**What to capture:**
- Published dashboard in Power BI Service
- Workspace name: "Agent Governance Workspace"
- Dashboard showing same visuals as Screenshot 26
- Last refresh timestamp visible: "Data refreshed at 2026-02-12 6:00 AM"
- Share button visible in toolbar
- Scheduled refresh configured (visible in dataset settings)
- Demonstrates operational dashboard for governance team

---

### Screenshot 28: Dataverse - Closed Exception with Audit Trail
**Portal Path:** Power Apps → Tables → Governance Exceptions → Data → [Closed exception record]
**What to capture:**
- Exception record with status "Closed"
- All original fields preserved:
  - Request date, requestor, agent name, zone, type, justifications
  - All three approvers and approval dates
  - Original expiration date
- Closure fields populated:
  - Approval Status: Closed
  - Closure Date: 2026-02-05
  - Closure Reason: "Issue resolved - DLP policy updated permanently to allow connector. Exception no longer required. Documented in change request CHG0012345."
- Audit trail section showing:
  - Created On: 2026-01-10 09:15:00 by john.doe@contoso.com
  - Modified On: 2026-02-05 14:30:00 by governance.admin@contoso.com
  - Version history available
- Demonstrates complete lifecycle preservation for compliance

---

### Screenshot 29: Exception Request Denied - Email Notification
**Portal Path:** Outlook → Inbox (Requestor's view)
**What to capture:**
- Email notification of denied exception request
- Subject: "Agent Exception Request Denied: TestAgent-Denied"
- Email body:
  - "Your exception request has been denied."
  - Exception details (agent name, type, requested expiration)
  - Denial reason/comments from approver: "Insufficient business justification. The risk assessment does not demonstrate adequate necessity for this policy override. Please resubmit with more detailed justification and explore alternative solutions before requesting exception."
  - Denied by: Jane Manager (Manager - Level 1 Approver)
  - Denial date: 2026-02-12 11:45 AM
  - Next steps: "If you have additional information or the situation has changed, you may submit a new exception request via the Power Apps form."
- Demonstrates transparency in denial process

---

### Screenshot 30: Windows Task Scheduler - Scheduled Exception Monitoring
**Portal Path:** Windows → Task Scheduler → Task Scheduler Library → Agent Exception Monitoring
**What to capture:**
- Task Scheduler showing scheduled PowerShell script execution
- Task name: "Daily Exception Expiration Monitor"
- Trigger: Daily at 8:00 AM
- Actions:
  - Program: PowerShell.exe
  - Arguments: `-File "C:\Scripts\Find-ExpiringExceptions.ps1" -EnvironmentUrl "https://contoso.crm.dynamics.com" -OutputPath "C:\Reports\Exceptions"`
- Status: Ready (Enabled)
- Last Run Time: 2026-02-12 8:00:00 AM (Success)
- Next Run Time: 2026-02-13 8:00:00 AM
- Run with highest privileges: Yes
- History tab showing successful execution logs
- Demonstrates automated daily monitoring

---

## Screenshot Naming Convention

Save screenshots with the following naming format:
```
3.12_Screenshot-[Number]_[Description]_[YYYYMMDD].png
```

Examples:
- `3.12_Screenshot-01_Dataverse-Governance-Exceptions-Table-Schema_20260212.png`
- `3.12_Screenshot-05_Power-Automate-Exception-Approval-Workflow-Overview_20260212.png`
- `3.12_Screenshot-15_PowerShell-Get-ExceptionRegister-Execution_20260212.png`
- `3.12_Screenshot-26_Power-BI-Desktop-Exception-Dashboard-Design_20260212.png`

Store all screenshots in the `docs/images/3.12/` directory for easy reference and documentation embedding.

---

## Screenshot Quality Guidelines

- **Resolution:** Minimum 1920x1080 for desktop portal screenshots; full browser window
- **Format:** PNG for static images (best quality for UI screenshots)
- **Content:** Ensure all text is readable; no excessive whitespace; crop appropriately
- **Annotations:** Add red boxes, arrows, or highlights to emphasize important elements (optional but helpful)
- **Privacy:** Redact sensitive data (real user emails, organization names, customer data) — use "contoso.com" or fictional names
- **Consistency:** Use the same browser, zoom level, and theme across all screenshots for professional appearance
- **Context:** Include navigation breadcrumbs, environment names, timestamps to demonstrate currency

---

## Priority Screenshots (Minimum Viable Documentation)

If time is limited, capture these minimum priority screenshots first:

1. **Screenshot 2:** Dataverse exception register sample data (demonstrates working system)
2. **Screenshot 3:** Power Apps exception request form (demonstrates user interface)
3. **Screenshot 5:** Power Automate approval workflow overview (demonstrates automation)
4. **Screenshot 10:** Dataverse record with complete approval trail (demonstrates audit capability)
5. **Screenshot 13:** Outlook expiration warning email (demonstrates monitoring)
6. **Screenshot 15:** PowerShell exception register export (demonstrates reporting)
7. **Screenshot 20:** Excel compliance report (demonstrates policy enforcement)
8. **Screenshot 21:** PowerShell audit evidence export (demonstrates regulatory readiness)

These 8 screenshots cover the core aspects of Control 3.12 and can serve as baseline documentation until full screenshot set is completed.

---

## Feature Availability Note

This control is a **process-based control** using standard Power Platform capabilities (Dataverse, Power Automate, Power Apps). All features documented are generally available as of February 2026. No preview features are required.

Organizations can implement this control immediately with:
- Power Automate Premium license (for Dataverse and approval flows)
- Power Apps per-user or per-app license (for request form)
- Basic PowerShell knowledge for reporting scripts

---

## Additional Guidance

**For Dataverse screenshots:**
- Capture full schema definition showing all required columns
- Show sample data with realistic values (not just "Test 1", "Test 2")
- Demonstrate mix of approval statuses and zones

**For Power Automate screenshots:**
- Show both collapsed overview (full workflow) and expanded detail (specific branches)
- Include run history demonstrating successful execution
- Capture approval emails showing requestor perspective

**For PowerShell screenshots:**
- Capture full console output including colored text (success in green, warnings in yellow, errors in red)
- Show file paths and timestamps
- Include summary statistics demonstrating script value

**For Excel/CSV screenshots:**
- Professional formatting with column headers bold and wrapped text
- Sufficient sample rows (10-20) to demonstrate realistic scale
- Use conditional formatting to highlight non-compliant items

---

[Back to Control 3.12](../../controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md)
