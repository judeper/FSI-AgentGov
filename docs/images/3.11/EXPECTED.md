# Control 3.11: Centralized Agent Inventory Enforcement - Screenshot Specifications

## Required Screenshots

### Screenshot 1: PPAC Agent Inventory Dashboard - Overview
**Portal Path:** Power Platform Admin Center → Agents → Agent Inventory (or Analytics → Agent Inventory)
**What to capture:**
- Agent Inventory dashboard landing page showing centralized agent discovery interface
- Agent List table with all discovered agents
- Key columns visible: Agent Name, Owner, Environment, Creation Date, Last Modified Date, Sharing Status
- Filter and sort controls visible (filter by environment, owner, creation date, zone)
- Export button visible for CSV export
- Refresh button visible for manual discovery trigger
- Total agent count displayed
- Last refresh timestamp visible
- Tenant name visible in PPAC header
- Navigation breadcrumb showing: PPAC → Agent Inventory

> **Note:** As of February 2026, Agent Inventory feature is in Preview. If not visible in your tenant, capture Message Center announcement or use PowerShell-generated inventory export as alternative evidence.

---

### Screenshot 2: PPAC Agent Inventory Settings - Data Refresh Schedule
**Portal Path:** PPAC → Agent Inventory → Settings (gear icon)
**What to capture:**
- Agent Inventory configuration settings panel
- Data Refresh Schedule section with options:
  - Refresh frequency dropdown (Daily, Weekly, Manual)
  - Refresh time picker (e.g., 2:00 AM)
  - Automatic Refresh toggle (On/Off)
- Discovery scope settings (All environments, Specific environments, Zone-based)
- Real-time alerts toggle (if available in preview)
- Save button visible
- Current configuration showing Daily refresh at 2:00 AM for Zone 3 compliance

---

### Screenshot 3: PPAC Agent Inventory - Export to CSV
**Portal Path:** PPAC → Agent Inventory → Export button
**What to capture:**
- Agent Inventory page with Export button highlighted
- Export dialog showing:
  - Export format options (CSV, Excel)
  - Column selection (all columns vs. selected columns)
  - Filter options (export all agents vs. filtered view)
- "Download" or "Generate Export" button
- File naming format preview: "AgentInventory_YYYYMMDD.csv"
- Demonstrates baseline documentation capability

---

### Screenshot 4: Agent Inventory Report CSV - Sample Data (Excel View)
**What to capture:**
- Excel spreadsheet showing exported Agent Inventory CSV
- Columns visible:
  - AgentName
  - AgentId
  - Owner
  - OwnerStatus (Active, Departed, Invalid, Missing)
  - Environment
  - EnvironmentId
  - ZoneClassification (Zone 1, Zone 2, Zone 3, Unknown)
  - CreatedDate
  - LastModifiedDate
  - DaysSinceModified
  - State (Active, Decommissioned)
  - MetadataCompletenessPercent
  - MissingFields
- At least 10 sample agent records showing mix of compliant and non-compliant metadata
- Date/time stamp in filename showing when inventory was generated
- Professional Excel formatting with column headers bolded

---

### Screenshot 5: Agent with Complete Metadata (Zone 3 Compliant)
**Portal Path:** PPAC → Environments → [Zone 3 Environment] → Resources → Microsoft Copilot Studio agents → [Agent Details]
**What to capture:**
- Agent detail page showing fully populated metadata
- Fields visible:
  - Agent Name: "Z3-CustomerService-SupportAgent"
  - Owner: john.doe@contoso.com (Active)
  - Environment: PROD-Zone3-CustomerService
  - Zone Classification: Zone 3
  - Risk Rating: Medium
  - Description: Detailed description (>50 characters)
  - Creation Date: 2025-11-15
  - Last Modified Date: 2026-02-01
  - Approval Date: 2025-11-20
  - Approver: Jane Admin (AI Governance Lead)
  - Documentation Link: `https://sharepoint.contoso.com/agents/...`
  - Decommissioning Plan: Documented
  - Compliance Status: Compliant
- Metadata completeness: 100%
- Demonstrates gold standard for Zone 3 agent

---

### Screenshot 6: Agent with Incomplete Metadata (Non-Compliant)
**Portal Path:** PPAC → Environments → [Environment] → Resources → Copilot Studio agents → [Agent Details]
**What to capture:**
- Agent detail page showing partially populated metadata
- Missing or incomplete fields:
  - Owner: (blank or "Unknown")
  - Zone Classification: Unknown
  - Risk Rating: (blank)
  - Description: (blank or <50 characters)
  - Approval Date: (blank)
- Fields highlighted in red or with warning icons indicating missing data
- Metadata completeness: 45% (example)
- Demonstrates non-compliant agent requiring remediation

---

### Screenshot 7: Pre-Publication Checklist Document (SharePoint or Word)
**What to capture:**
- SharePoint page or Word document showing Agent Registration Pre-Publication Checklist
- Checklist items visible:
  - [ ] Agent Name follows naming convention
  - [ ] Owner Assigned (valid Entra ID user)
  - [ ] Environment matches zone classification
  - [ ] Zone Classification assigned (1, 2, or 3)
  - [ ] Risk Rating assigned (High/Medium/Low)
  - [ ] Description (minimum 50 characters)
  - [ ] Documentation Link provided
  - [ ] Approval Obtained (Zone 2/3)
  - [ ] Change Ticket created and approved
  - [ ] Metadata Complete (all mandatory fields)
  - [ ] Security Review completed (Zone 3)
  - [ ] Decommissioning Plan documented (Zone 3)
- Checklist includes zone-specific requirements table
- Version history or last updated date visible
- Demonstrates documented governance requirements

---

### Screenshot 8: Change Request - Agent Registration (ServiceNow/Jira)
**Portal Path:** Change management system → New Change Request → Agent Registration Template
**What to capture:**
- Change request form with Agent Registration template selected
- Form fields visible:
  - Agent Name: (text input)
  - Environment: (dropdown showing Zone 1/2/3 environments)
  - Governance Zone: (dropdown: Zone 1, Zone 2, Zone 3)
  - Requestor: (user lookup)
  - Business Justification: (multi-line text)
  - Risk Assessment: (multi-line text or dropdown)
  - Compensating Controls: (multi-line text)
  - Approval Required From: (checkboxes: Power Platform Admin, AI Governance Lead, Compliance Officer)
  - Implementation Date: (date picker)
  - Pre-Publication Checklist: (embedded checklist or attachment)
- Submit button visible
- Template name "Agent Registration - Pre-Publication" in header
- Change request number format visible (e.g., CHG0001234)

---

### Screenshot 9: Change Request - Approval Workflow (Zone 3)
**Portal Path:** Change management system → [Change Request CHG0001234] → Workflow / Approval history
**What to capture:**
- Change request detail page showing multi-stage approval workflow for Zone 3 agent
- Approval stages visible:
  1. Submitted (Requestor: Alice User, Date: 2026-02-01, Status: Submitted)
  2. Power Platform Admin Review (Approver: Bob Admin, Status: Approved, Date: 2026-02-02, Comments: "Metadata complete. Approved.")
  3. AI Governance Lead Review (Approver: Carol Governance, Status: Approved, Date: 2026-02-03, Comments: "Risk assessment acceptable. Approved.")
  4. Compliance Officer Review (Approver: Dave Compliance, Status: Approved, Date: 2026-02-04, Comments: "Regulatory requirements met. Approved.")
  5. Implementation (Status: Complete, Date: 2026-02-05)
- Each stage shows: Approver name, approval status, date/time, comments
- Change status: Approved and Implemented
- Demonstrates Zone 3 requires three-stage approval (vs. Zone 2: two-stage, Zone 1: one-stage)

---

### Screenshot 10: Power Automate Flow - Agent Inventory Completeness Monitor
**Portal Path:** Power Automate (make.powerautomate.com) → My flows → Agent Inventory Completeness Monitor
**What to capture:**
- Flow overview page showing scheduled flow
- Flow name: "Agent Inventory Completeness Monitor"
- Trigger: Recurrence (Daily at 3:00 AM)
- Flow steps visible:
  1. Recurrence trigger
  2. Get Agent Inventory Data (HTTP request or SharePoint Get file)
  3. Filter array (incomplete metadata)
  4. Condition (check if any agents have issues)
  5. Compose alert message
  6. Post adaptive card in Teams channel
  7. Add row to Dataverse (audit trail)
- Flow status: On (enabled)
- Last run: Success (green checkmark)
- Next run scheduled: 2026-02-13 03:00:00
- Demonstrates automated enforcement mechanism

---

### Screenshot 11: Power Automate Flow - Run History (Successful Execution)
**Portal Path:** Power Automate → Agent Inventory Completeness Monitor → Run history → [Recent run]
**What to capture:**
- Flow run detail showing successful execution
- All steps completed with green checkmarks
- Step-by-step execution summary:
  - Recurrence: Triggered at 3:00 AM
  - Get Agent Inventory Data: Retrieved 87 agents
  - Filter array: Found 12 agents with incomplete metadata
  - Condition: True (agents have issues)
  - Compose alert message: Message formatted
  - Post to Teams: Notification sent successfully
  - Add row to Dataverse: Audit record created
- Execution duration: 45 seconds (reasonable performance)
- No errors or warnings
- Demonstrates operational flow

---

### Screenshot 12: Teams Notification - Incomplete Metadata Alert
**Portal Path:** Microsoft Teams → [Governance Team] → Agent Governance Alerts channel
**What to capture:**
- Teams channel showing adaptive card notification from Flow bot
- Notification content:
  - Title: "⚠️ Agent Inventory Completeness Alert"
  - Message: "The following agents have incomplete metadata and require remediation:"
  - List of agents with missing fields:
    1. Agent Name: TestAgent1
       - Environment: Zone2-Development
       - Missing Fields: Owner, Zone Classification
       - Action Required: Assign owner and classify zone within 7 days
    2. Agent Name: TestAgent2
       - Environment: Zone3-Production
       - Missing Fields: Risk Rating, Description
       - Action Required: Complete metadata within 7 days
  - Total agents with issues: 12
  - Links:
    - "View full inventory" (PPAC Agent Inventory link)
    - "Metadata requirements" (Governance document link)
  - SLA reminder: "Zone 1: 30 days, Zone 2: 14 days, Zone 3: 7 days"
- Notification timestamp visible
- Channel members can see notification
- Demonstrates real-time alerting

---

### Screenshot 13: Dataverse Table - fsi_inventoryalerts Schema
**Portal Path:** Power Apps (make.powerapps.com) → Tables → fsi_inventoryalerts → Columns
**What to capture:**
- Dataverse table definition for fsi_inventoryalerts showing audit trail schema
- Table columns visible:
  - fsi_alertdate (Date and Time) — When alert was generated
  - fsi_agentstaffected (Whole Number) — Count of agents with issues
  - fsi_agentlist (Multiple lines of text) — JSON or delimited list of affected agents
  - fsi_alerttype (Choice: Incomplete Metadata, Orphaned Agent, Unmanaged Agent, Other)
  - fsi_status (Choice: Open, In Progress, Resolved, Closed)
  - fsi_assignedto (Lookup to User) — Person responsible for remediation
  - fsi_resolutiondate (Date and Time) — When issue was resolved
  - fsi_resolutionnotes (Multiple lines of text) — Remediation actions taken
- Table name in header: fsi_inventoryalerts
- Column properties visible (data type, required, etc.)
- Demonstrates persistent audit trail for compliance

---

### Screenshot 14: Dataverse Table - fsi_inventoryalerts Sample Data
**Portal Path:** Power Apps → Tables → fsi_inventoryalerts → Data
**What to capture:**
- Dataverse table data view showing sample alert records
- At least 5-10 alert records visible in the grid:
  - Record 1: Alert Date: 2026-02-10, Type: Incomplete Metadata, Agents Affected: 12, Status: Open
  - Record 2: Alert Date: 2026-02-09, Type: Orphaned Agent, Agents Affected: 3, Status: In Progress, Assigned To: John Admin
  - Record 3: Alert Date: 2026-02-08, Type: Incomplete Metadata, Agents Affected: 8, Status: Resolved, Resolution Date: 2026-02-10
  - (Additional records...)
- Columns visible: Alert Date, Alert Type, Agents Affected, Status, Assigned To, Resolution Date
- Grid view with data clearly readable
- Demonstrates audit trail persistence

---

### Screenshot 15: PowerShell Script - Get-AgentInventoryReport.ps1 Execution
**What to capture:**
- PowerShell console showing execution of Get-AgentInventoryReport.ps1
- Command line: `.\Get-AgentInventoryReport.ps1 -OutputPath "C:\Reports" -ZoneMappingFile "C:\Config\zone-mappings.csv"`
- Console output showing:
  - "Connecting to Power Platform..." (Cyan)
  - "Connecting to Microsoft Graph..." (Cyan)
  - "Loading zone mappings from C:\Config\zone-mappings.csv..." (Cyan)
  - "Retrieving all Power Platform environments..." (Cyan)
  - "[1/15] Processing environment: Default Environment" (Green)
  - "[2/15] Processing environment: Zone3-Production" (Green)
  - (Additional environments...)
  - "--- Agent Inventory Summary ---" (Cyan)
  - "Total Agents: 87" (White)
  - "Active Agents: 84" (White)
  - "Decommissioned Agents: 3" (White)
  - "Agents with Valid Owner: 79" (Green)
  - "Agents with Invalid/Missing Owner: 8" (Red)
  - "Agents with Unknown Zone: 5" (Yellow)
  - "Average Metadata Completeness: 78.45%" (White)
  - "✓ Inventory report saved to: C:\Reports\AgentInventoryReport_20260212-104530.csv" (Green)
  - "Script completed successfully." (Cyan)
- PowerShell version and window title visible
- Demonstrates successful automated inventory discovery

---

### Screenshot 16: PowerShell Script - Detect-OrphanedAgents.ps1 Execution
**What to capture:**
- PowerShell console showing execution of Detect-OrphanedAgents.ps1
- Command line: `.\Detect-OrphanedAgents.ps1 -InventoryReportPath "C:\Reports\AgentInventory.csv" -StalenessThresholdDays 365 -TeamsWebhookUrl "https://outlook.office.com/webhook/..."`
- Console output showing:
  - "Loading inventory report from C:\Reports\AgentInventory.csv..." (Cyan)
  - "Analyzing 87 agents for orphaned status..." (Cyan)
  - "--- Orphaned Agent Detection Summary ---" (Cyan)
  - "Total Orphaned Agents: 11" (White)
  - "  High Priority: 3" (Red) — Departed owners
  - "  Medium Priority: 6" (Yellow) — Stale agents
  - "  Low Priority: 2" (Green) — Missing metadata
  - "✓ Orphaned agents report saved to: C:\Reports\OrphanedAgentsReport_20260212-104600.csv" (Green)
  - "Sending Teams notification..." (Cyan)
  - "✓ Teams notification sent successfully." (Green)
  - "Script completed successfully." (Cyan)
- Demonstrates orphaned agent detection and alerting

---

### Screenshot 17: PowerShell Script - Test-InventoryCompleteness.ps1 Execution
**What to capture:**
- PowerShell console showing execution of Test-InventoryCompleteness.ps1
- Command line: `.\Test-InventoryCompleteness.ps1 -InventoryReportPath "C:\Reports\AgentInventory.csv" -OutputPath "C:\Reports"`
- Console output showing:
  - "Loading inventory report from C:\Reports\AgentInventory.csv..." (Cyan)
  - "Validating 87 agents against mandatory metadata requirements..." (Cyan)
  - "--- Inventory Completeness Summary ---" (Cyan)
  - "Total Agents: 87" (White)
  - "Compliant: 71" (Green)
  - "Non-Compliant: 16" (Red)
  - "Compliance Rate: 81.61%" (White)
  - "--- Compliance by Zone ---" (Cyan)
  - "Zone 1: 28 / 30 (93.33%)" (White)
  - "Zone 2: 35 / 40 (87.50%)" (White)
  - "Zone 3: 8 / 17 (47.06%)" (White) — Flagged for remediation
  - "✓ Compliance report saved to: C:\Reports\InventoryComplianceReport_20260212-104630.csv" (Green)
  - "⚠ WARNING: Compliance rate (81.61%) is below target (95%)!" (Red)
  - "Review non-compliant agents and initiate remediation." (Yellow)
  - "Script completed successfully." (Cyan)
- Demonstrates completeness validation and compliance gap identification

---

### Screenshot 18: CSV Report - OrphanedAgentsReport.csv Contents (Excel)
**What to capture:**
- Excel spreadsheet showing OrphanedAgentsReport.csv
- Columns visible:
  - AgentName
  - Owner
  - OwnerStatus (Departed, Invalid, Missing)
  - Environment
  - ZoneClassification
  - DaysSinceModified
  - OrphanReason (e.g., "Owner status: Departed; Stale (not modified in 450 days)")
  - Priority (High, Medium, Low)
  - RecommendedAction (Transfer ownership or decommission, Verify usage and decommission if unused)
- Sample rows showing orphaned agents:
  - Agent1: Owner Departed, High Priority
  - Agent2: Stale (500 days), Medium Priority
  - Agent3: Missing Zone Classification, Low Priority
- Sorted by Priority (High → Medium → Low)
- Professional formatting with color-coding by priority (red for High, yellow for Medium, green for Low)

---

### Screenshot 19: CSV Report - InventoryComplianceReport.csv Contents (Excel)
**What to capture:**
- Excel spreadsheet showing InventoryComplianceReport.csv
- Columns visible:
  - AgentName
  - Environment
  - ZoneClassification
  - ComplianceStatus (Compliant, Non-Compliant)
  - MissingFields (e.g., "Owner; Risk Rating; Description")
  - MetadataCompletenessPercent
- Sample rows showing mix of compliant and non-compliant agents
- Filter applied to show only Non-Compliant agents for remediation prioritization
- Summary row at bottom showing totals and compliance rate

---

### Screenshot 20: Ownership Validation - Valid Owner (Active Entra ID User)
**Portal Path:** Entra ID → Users → john.doe@contoso.com
**What to capture:**
- Entra ID user profile page
- User details visible:
  - Display Name: John Doe
  - User Principal Name: john.doe@contoso.com
  - Account Status: Enabled (Active)
  - Department: Customer Service
  - Job Title: Support Manager
- User is active and can be assigned as agent owner
- Demonstrates valid ownership

---

### Screenshot 21: Ownership Validation - Departed Owner (Deleted Entra ID User)
**Portal Path:** Entra ID → Deleted users → jane.smith@contoso.com (or User not found)
**What to capture:**
- Entra ID search showing user not found or deleted user
- Search query: "jane.smith@contoso.com"
- Result: "No results found" or "User has been deleted"
- Deleted users list showing jane.smith@contoso.com with deletion date
- Demonstrates departed owner requiring remediation

---

### Screenshot 22: Ownership Transfer - PPAC Agent Sharing Settings
**Portal Path:** PPAC → Environments → [Environment] → Resources → Copilot Studio agents → [Agent] → Manage sharing
**What to capture:**
- Agent sharing settings panel
- Current owner: jane.smith@contoso.com (Departed)
- "Transfer ownership" button visible
- Transfer ownership dialog:
  - New Owner: (user lookup field)
  - Search and select: john.doe@contoso.com
  - Reason for transfer: "Original owner departed. Transferring to team lead."
  - Confirm transfer button
- Demonstrates remediation action for orphaned agent

---

### Screenshot 23: Agent Decommissioning - Metadata Archive in SharePoint
**Portal Path:** SharePoint → Governance Site → Decommissioned Agents Archive → 2026 → 02 → TestAgent_Decommissioned20260212
**What to capture:**
- SharePoint folder showing decommissioned agent metadata archive
- Folder structure: Governance Site → Decommissioned Agents Archive → Year (2026) → Month (02) → Agent-specific folder
- Archived files visible:
  - AgentMetadata_Export.csv (metadata from Agent Inventory)
  - AgentConfiguration.json (exported configuration from Copilot Studio)
  - ChangeRequest_CHG0001245.pdf (approved decommissioning change request)
  - DecommissioningNotes.txt (reason for decommissioning, usage analytics, approvals)
- File retention policy visible: "Retain for 7 years (Regulatory requirement)"
- Demonstrates compliant metadata archival before deletion

---

### Screenshot 24: Agent Decommissioning - Status Update in Inventory
**Portal Path:** PPAC → Agent Inventory → [Filter: State = Decommissioned]
**What to capture:**
- Agent Inventory filtered to show only decommissioned agents
- Sample decommissioned agent record:
  - Agent Name: TestAgent
  - Owner: john.doe@contoso.com (Original)
  - Environment: Zone2-Development
  - State: Decommissioned
  - Decommissioning Date: 2026-02-12
  - Decommissioning Reason: "Agent no longer in use. Zero usage for 90 days. Business owner approval obtained."
  - Metadata Archived: Yes
  - Archive Location: `https://sharepoint.contoso.com/governance/decommissioned/...`
- Demonstrates decommissioned agents remain in inventory for audit trail (not deleted)

---

### Screenshot 25: Zone Mapping CSV - Sample Zone-to-Environment Mappings
**What to capture:**
- Notepad++ or Excel showing zone-mappings.csv file
- CSV structure:
  ```csv
  EnvironmentId,ZoneName
  00000000-0000-0000-0000-000000000001,Zone 1
  00000000-0000-0000-0000-000000000002,Zone 1
  00000000-0000-0000-0000-000000000003,Zone 2
  00000000-0000-0000-0000-000000000004,Zone 2
  00000000-0000-0000-0000-000000000005,Zone 3
  00000000-0000-0000-0000-000000000006,Zone 3
  ```
- At least 10-15 environment mappings visible
- Clear column headers
- Properly formatted CSV (comma-separated, no extra spaces)
- Demonstrates zone classification input for scripts

---

### Screenshot 26: Quarterly Inventory Audit Report (Word Document)
**What to capture:**
- Word document showing formal quarterly inventory audit report
- Report sections visible:
  - **Executive Summary:** Compliance rate, improvement trend, key findings
  - **Scope:** Audit period (Q1 2026), environments audited, agent count
  - **Completeness Metrics:** Table showing compliance by zone (Zone 1: 93%, Zone 2: 88%, Zone 3: 47%)
  - **Non-Compliant Agents:** List of agents requiring remediation with SLA status
  - **Remediation Progress:** Count of agents remediated since last audit (15 resolved, 16 outstanding)
  - **Trends:** Chart showing compliance rate improvement from 65% (Q4 2025) to 82% (Q1 2026)
  - **Recommendations:** Improve Zone 3 compliance through enhanced training and automated enforcement
  - **Approvals:** Reviewed by AI Governance Lead (signature), Approved by Compliance Officer (signature)
- Professional formatting with company logo, date, version
- Demonstrates formal audit process for regulatory examination

---

### Screenshot 27: Master Orchestration Script - Invoke-InventoryEnforcementSuite.ps1 Execution
**What to capture:**
- PowerShell console showing execution of master orchestration script
- Command line: `.\Invoke-InventoryEnforcementSuite.ps1 -OutputPath "C:\Reports" -ZoneMappingFile "C:\Config\zone-mappings.csv" -TeamsWebhookUrl "https://outlook.office.com/webhook/..."`
- Console output showing:
  - "========================================"
  - "Agent Inventory Enforcement Suite"
  - "========================================"
  - "[1/3] Generating agent inventory report..." (Green)
  - (Output from Get-AgentInventoryReport.ps1...)
  - "✓ Inventory report generated: C:\Reports\AgentInventoryReport_20260212-105000.csv"
  - "[2/3] Detecting orphaned agents..." (Green)
  - (Output from Detect-OrphanedAgents.ps1...)
  - "✓ Orphaned agent detection completed"
  - "[3/3] Validating inventory completeness..." (Green)
  - (Output from Test-InventoryCompleteness.ps1...)
  - "✓ Completeness validation completed"
  - "========================================"
  - "Enforcement Suite Completed"
  - "========================================"
  - "All reports saved to: C:\Reports"
  - "Next Steps:" (Yellow)
  - "1. Review orphaned agent report and initiate remediation"
  - "2. Review completeness report and contact agent authors for metadata updates"
  - "3. Update zone mappings if any agents have 'Unknown' classification"
  - "4. Schedule this suite to run daily for Zone 2/3 environments"
- Demonstrates end-to-end automated enforcement

---

### Screenshot 28: Windows Task Scheduler - Scheduled Enforcement Suite Execution
**Portal Path:** Windows Task Scheduler → Task Scheduler Library → Agent Inventory Enforcement Suite
**What to capture:**
- Task Scheduler window showing scheduled task
- Task Name: "Agent Inventory Enforcement Suite"
- Status: Ready (Enabled)
- Trigger: Daily at 4:00 AM
- Action: Start a program → PowerShell.exe with arguments:
  - `-File C:\Scripts\Invoke-InventoryEnforcementSuite.ps1 -OutputPath C:\Reports -ZoneMappingFile C:\Config\zone-mappings.csv -TeamsWebhookUrl 'https://outlook.office.com/webhook/...'`
- Run with highest privileges: Yes
- Last Run Time: 2026-02-12 04:00:00 (Success)
- Next Run Time: 2026-02-13 04:00:00
- History tab showing successful execution logs
- Demonstrates continuous automated enforcement

---

### Screenshot 29: Error Message - Agent Inventory Not Available (Preview Status)
**Portal Path:** PPAC → Agents (or attempt to access Agent Inventory)
**What to capture:**
- PPAC interface showing Agent Inventory feature not available message
- Error or info message: "Agent Inventory is currently in Preview and not yet available in your tenant. Check Message Center for rollout updates or contact Microsoft Support to enable the preview."
- Alternative message: "This feature is not available in your region. Expected availability: Q2 2026."
- PPAC navigation showing no "Agent Inventory" menu item
- Demonstrates preview status and compensating control need

---

### Screenshot 30: Message Center - Agent Inventory GA Announcement (Future)
**Portal Path:** Microsoft 365 Admin Center → Health → Message Center → [Search: Agent Inventory]
**What to capture:**
- Message Center showing announcement of Agent Inventory GA
- Message details:
  - Message ID: MC123456
  - Title: "Agent Inventory in Power Platform Admin Center reaches General Availability"
  - Description: "The Agent Inventory feature is now generally available for all tenants. This feature provides centralized discovery and management of Copilot Studio agents, Microsoft 365 Copilot agents, and declarative agents across your organization."
  - Affected services: Power Platform, Copilot Studio
  - Status: General Availability
  - Rollout timeline: Completed
  - Action required: None (automatically enabled)
  - Learn more link
- Demonstrates feature availability tracking

---

## Screenshot Naming Convention

Save screenshots with the following naming format:
```
3.11_Screenshot-[Number]_[Description]_[YYYYMMDD].png
```

Examples:
- `3.11_Screenshot-01_PPAC-Agent-Inventory-Dashboard_20260212.png`
- `3.11_Screenshot-04_Agent-Inventory-Report-CSV-Excel-View_20260212.png`
- `3.11_Screenshot-15_PowerShell-Get-AgentInventoryReport-Execution_20260212.png`
- `3.11_Screenshot-26_Quarterly-Inventory-Audit-Report_20260212.png`

Store all screenshots in the `docs/images/3.11/` directory for easy reference and documentation embedding.

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

1. **Screenshot 1:** PPAC Agent Inventory Dashboard (demonstrates core capability)
2. **Screenshot 5:** Agent with Complete Metadata Zone 3 (gold standard)
3. **Screenshot 6:** Agent with Incomplete Metadata (demonstrates gap)
4. **Screenshot 12:** Teams Notification Incomplete Metadata Alert (demonstrates alerting)
5. **Screenshot 15:** PowerShell Get-AgentInventoryReport Execution (demonstrates automation)
6. **Screenshot 18:** CSV Report OrphanedAgentsReport (demonstrates remediation tracking)
7. **Screenshot 23:** Agent Decommissioning Metadata Archive SharePoint (demonstrates retention)
8. **Screenshot 26:** Quarterly Inventory Audit Report (demonstrates compliance process)

These 8 screenshots cover the core aspects of Control 3.11 and can serve as baseline documentation until full screenshot set is completed.

---

## Feature Availability Note

The Agent Inventory feature in PPAC is in Preview as of February 2026. Portal location, UI, and feature names may change before General Availability. Monitor Microsoft 365 Message Center and Roadmap for GA announcements.

If Agent Inventory is not visible in your tenant:
- Capture Message Center announcement or roadmap entry as evidence of preview status
- Use PowerShell-generated inventory reports as alternative evidence
- Document compensating controls (manual inventory tracking, PowerShell automation) until feature is available
- Screenshots should be updated once features become available in your environment

---

## Additional Guidance

**For PowerShell screenshots:**
- Capture full console window including command prompt path
- Show successful execution with green success messages and summary statistics
- Include error handling examples (e.g., connection failures, permission issues) for troubleshooting reference

**For CSV reports:**
- Open in Excel for professional formatting and readability
- Include column headers and at least 10 sample rows
- Use conditional formatting or color-coding to highlight priorities (red for high, yellow for medium)
- Demonstrate realistic data (not just test data)

**For change management screenshots:**
- Use actual change management system (ServiceNow, Jira, or equivalent)
- Show complete approval workflow with multiple approvers and approval chain
- Include timestamps and approval comments to demonstrate audit trail
- Redact sensitive information but maintain realistic organizational context

---

[Back to Control 3.11](../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md)
