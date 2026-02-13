# Control 2.24: Agent Feature Enablement and Restriction Governance - Screenshot Specifications

## Required Screenshots

### Screenshot 1: PPAC Copilot Governance Dashboard - Overview
**Portal Path:** Power Platform Admin Center → Copilot → Governance
**What to capture:**
- Copilot governance dashboard landing page
- Tenant-wide feature toggles section visible (top of page)
- Environment-specific feature controls section visible (middle of page)
- List of environments with feature status summary
- Tenant name visible in header
- Navigation breadcrumb showing: PPAC → Copilot → Governance

### Screenshot 2: PPAC Tenant-Wide Feature Toggles
**Portal Path:** Power Platform Admin Center → Copilot → Governance → Tenant settings
**What to capture:**
- Tenant settings or Global features section expanded
- Feature toggles visible:
  - Copilot Studio enabled (toggle state)
  - Generative AI features (toggle state)
  - Preview features (toggle state)
  - Agent sharing (toggle state)
  - Multi-agent orchestration (toggle state)
- Description text for each toggle (explaining what it controls)
- Save or Apply button visible

### Screenshot 3: PPAC Zone 3 Environment Feature Configuration (Restrictive)
**Portal Path:** PPAC → Copilot → Governance → Environment settings → [Zone 3 Environment]
**What to capture:**
- Environment details panel or modal
- Environment name clearly showing "Zone 3" or "Enterprise" or "PROD-Z3" classification
- Feature toggles set to restrictive settings:
  - Generative actions: Disabled or "Requires approval"
  - Preview features: Disabled
  - Web search tool: Disabled or "Explicit allowlist"
  - Code interpreter: Disabled
  - Custom plugins: "Approved list only"
  - Multi-agent orchestration: Disabled or "Requires approval"
- All toggles in restrictive/disabled state
- Save button visible
- Environment type visible (Production)

### Screenshot 4: PPAC Zone 2 Environment Feature Configuration (Moderate)
**Portal Path:** PPAC → Copilot → Governance → Environment settings → [Zone 2 Environment]
**What to capture:**
- Environment details panel for Zone 2 environment
- Environment name showing "Zone 2" or "Team" classification
- Feature toggles set to moderate settings:
  - Generative actions: Enabled (with note: "Requires documented approval")
  - Preview features: Disabled
  - Web search tool: Enabled (with note: "Approved agents only")
  - Code interpreter: Disabled
  - Custom plugins: Enabled (with note: "Approved plugins")
  - Multi-agent orchestration: Enabled (with note: "Max depth 2 levels")
- Mix of enabled and disabled toggles
- Save button visible
- Environment type visible (Production or Sandbox)

### Screenshot 5: PPAC Zone 1 Environment Feature Configuration (Permissive)
**Portal Path:** PPAC → Copilot → Governance → Environment settings → [Zone 1 Environment]
**What to capture:**
- Environment details panel for Zone 1 environment
- Environment name showing "Zone 1" or "Personal" classification
- Feature toggles set to permissive settings:
  - Generative actions: Enabled
  - Preview features: Enabled
  - Web search tool: Enabled
  - Code interpreter: Enabled
  - Custom plugins: Enabled
  - Multi-agent orchestration: Enabled
- All or most toggles in enabled state
- Save button visible
- Environment type visible (Sandbox or Development)

### Screenshot 6: PPAC DLP Policy - Zone 3 Connector Groups
**Portal Path:** PPAC → Data policies → [Zone 3 DLP Policy] → Connectors
**What to capture:**
- DLP policy editor showing connector classification groups
- Three groups visible: Business, Non-business, Blocked
- **Blocked group** contains high-risk connectors:
  - HTTP connector (shared_http)
  - Custom connectors
  - AI Builder connector (if generative actions prohibited)
- **Business group** contains only approved connectors:
  - SharePoint, Dataverse, Microsoft 365 Users (if approved)
- Policy name visible in header
- Environment scope section showing Zone 3 environments assigned
- Save button visible

### Screenshot 7: PPAC DLP Policy - Environment Scope Configuration
**Portal Path:** PPAC → Data policies → [Zone 3 DLP Policy] → Environments
**What to capture:**
- DLP policy environment scope configuration page
- Policy type selected: "Apply to specific environments" (not "All environments")
- List of environments included in policy scope:
  - Zone 3 Production environment(s) listed
  - Zone 1 and Zone 2 environments NOT listed (excluded)
- Environment selection interface (checkboxes or dropdown)
- "Add environments" button visible
- Save or Next button visible

### Screenshot 8: Copilot Studio - Zone 3 Agent with Generative Action Blocked
**Portal Path:** Copilot Studio (copilotstudio.microsoft.com) → [Zone 3 Environment] → [Agent] → Add action
**What to capture:**
- Copilot Studio agent authoring canvas
- Action menu opened (+ Add action or Actions panel)
- "Create generative action" option is either:
  - Not visible in the action menu (grayed out or missing), OR
  - Visible but clicking displays error message
- Error message (if displayed): "Generative actions are not enabled in this environment" or similar
- Environment name visible in header (showing Zone 3 environment)
- Agent name visible in header

### Screenshot 9: Copilot Studio - Zone 3 Agent Tools Settings (Code Interpreter Disabled)
**Portal Path:** Copilot Studio → [Zone 3 Agent] → Settings → Tools
**What to capture:**
- Agent settings panel showing Tools section
- Tool toggles visible:
  - Web Search: Off/Disabled (grayed out)
  - Code Interpreter: Off/Disabled (grayed out)
  - Other tools: Off/Disabled as appropriate
- Toggle controls are grayed out or show "Not available in this environment" tooltip
- Environment and agent name visible in header
- Save button visible (likely disabled if no changes can be made)

### Screenshot 10: Copilot Studio - Zone 2 Agent with Web Search Enabled (After Approval)
**Portal Path:** Copilot Studio → [Zone 2 Agent] → Settings → Tools
**What to capture:**
- Agent settings panel showing Tools section for Zone 2 approved agent
- Web Search toggle: On/Enabled (functional, not grayed out)
- Code Interpreter toggle: Off/Disabled (prohibited in Zone 2)
- Multi-agent orchestration: Enabled (if applicable)
- Environment name visible showing Zone 2 classification
- Agent name visible
- Demonstration that approved features work in Zone 2 after change approval

### Screenshot 11: Copilot Studio - Zone 1 Agent with All Features Enabled
**Portal Path:** Copilot Studio → [Zone 1 Agent] → Settings → Tools
**What to capture:**
- Agent settings panel showing Tools section for Zone 1 agent
- All tool toggles: On/Enabled
  - Web Search: On
  - Code Interpreter: On
  - Generative actions: Available
  - Custom plugins: Enabled
- No restrictions visible
- Environment name showing Zone 1 classification
- Demonstration of permissive feature access in Zone 1

### Screenshot 12: Copilot Studio - Preview Features Settings (Zone 1)
**Portal Path:** Copilot Studio → Settings → Preview features
**What to capture:**
- Preview features settings page
- List of preview/experimental features available for enablement
- Toggle controls for each preview feature
- Zone 1 environment: Toggles are functional and can be enabled
- Examples of preview features (as available in February 2026)
- Note or banner explaining these are preview features not recommended for production

### Screenshot 13: Copilot Studio - Preview Features Disabled (Zone 3)
**Portal Path:** Copilot Studio → Settings → Preview features (in Zone 3 environment)
**What to capture:**
- Same preview features settings page as Screenshot 12, but in Zone 3 environment
- All preview feature toggles: Off/Disabled and grayed out
- Tooltip or message explaining: "Preview features are not available in this environment"
- Comparison to Zone 1 showing enforcement of zone restrictions
- Environment name visible showing Zone 3 classification

### Screenshot 14: Copilot Studio - Connector Search with Blocked Connector (Zone 3)
**Portal Path:** Copilot Studio → [Zone 3 Agent] → Add action → Call an action from a connector
**What to capture:**
- Connector selection interface
- Search box with "HTTP" searched
- Search results showing:
  - HTTP connector NOT in results (if completely blocked), OR
  - HTTP connector with "Blocked" badge or icon, OR
  - Error message when attempting to select HTTP connector
- Alternative: Show empty search results demonstrating connector is unavailable
- Environment name visible (Zone 3)

### Screenshot 15: Copilot Studio - Approved Connector Available (Zone 3)
**Portal Path:** Copilot Studio → [Zone 3 Agent] → Add action → Call an action from a connector
**What to capture:**
- Same connector selection interface as Screenshot 14
- Search box with "SharePoint" searched (or another approved connector)
- SharePoint connector visible in search results with no "Blocked" badge
- Connector is selectable and functional
- Demonstration that approved connectors work despite DLP restrictions
- Environment name visible (Zone 3)

### Screenshot 16: Power Apps - Feature Catalog Table Schema
**Portal Path:** Power Apps (make.powerapps.com) → Tables → fsi_featurecatalog → Columns
**What to capture:**
- Dataverse table definition for fsi_featurecatalog
- Table columns/fields list showing:
  - fsi_featurename (Single line of text)
  - fsi_featurecategory (Choice)
  - fsi_zone1status (Choice: Allowed/Restricted/Prohibited)
  - fsi_zone2status (Choice: Allowed/Restricted/Prohibited)
  - fsi_zone3status (Choice: Allowed/Restricted/Prohibited)
  - fsi_approvalrequired (Yes/No)
  - fsi_approvaldate (Date)
  - fsi_changeticket (Single line of text)
  - fsi_expirationdate (Date)
  - fsi_riskrating (Choice: High/Medium/Low)
  - fsi_justification (Multiple lines of text)
- Table name visible in header
- Column properties visible (data type, required, etc.)

### Screenshot 17: Power Apps - Feature Catalog Data (Sample Records)
**Portal Path:** Power Apps → Tables → fsi_featurecatalog → Data
**What to capture:**
- Dataverse table data view showing sample feature records
- At least 5-10 feature records visible in the grid:
  - Generative Actions (AI Builder) - Zone 1: Allowed, Zone 2: Restricted, Zone 3: Prohibited
  - Web Search Tool - Zone 1: Allowed, Zone 2: Restricted, Zone 3: Prohibited
  - Code Interpreter - Zone 1: Allowed, Zone 2: Prohibited, Zone 3: Prohibited
  - SharePoint Connector - Zone 1: Allowed, Zone 2: Allowed, Zone 3: Restricted
  - HTTP Connector - Zone 1: Allowed, Zone 2: Restricted, Zone 3: Prohibited
- Columns visible: Feature Name, Category, Zone 1/2/3 Status, Risk Rating, Approval Required
- Grid view showing multiple records for comprehensive feature inventory
- Add/Edit/Delete buttons visible in toolbar

### Screenshot 18: Power Apps - Feature Catalog Detail Record (Approved Feature)
**Portal Path:** Power Apps → Tables → fsi_featurecatalog → Data → [Select a feature record]
**What to capture:**
- Detail form for a single feature record (e.g., Web Search Tool)
- All fields populated:
  - Feature Name: Web Search Tool
  - Feature Category: Tool
  - Zone 1 Status: Allowed
  - Zone 2 Status: Restricted
  - Zone 3 Status: Prohibited
  - Approval Required: Yes
  - Approval Date: 2026-02-10 (or similar recent date)
  - Change Ticket: CHG0001234 (example ticket number)
  - Expiration Date: (empty or future date if time-bound)
  - Risk Rating: Medium
  - Justification: "Zone 2: Approved for customer support agents with domain restrictions and human review. Zone 3: Prohibited due to risk of inaccurate information retrieval."
- Form layout showing all metadata fields
- Save button visible

### Screenshot 19: Power Apps - Feature Catalog Record with Expiration (Time-Bound Exception)
**Portal Path:** Power Apps → Tables → fsi_featurecatalog → Data → [Select a time-bound exception record]
**What to capture:**
- Detail form for a feature record with expiration date
- Example: Preview feature enabled in Zone 2 for 90-day evaluation
- Fields showing:
  - Feature Name: [Preview Feature X]
  - Zone 2 Status: Restricted (temporary exception)
  - Approval Required: Yes
  - Approval Date: 2026-02-01
  - Change Ticket: CHG0001235
  - **Expiration Date: 2026-05-01** (90 days from approval)
  - Justification: "Temporary 90-day evaluation period for [business justification]. Will be reviewed before expiration for renewal or revocation."
- Expiration Date field populated and visible
- Demonstration of time-bound exception tracking

### Screenshot 20: SharePoint - Feature Catalog List (Alternative to Dataverse)
**Portal Path:** SharePoint governance site → Feature Catalog list
**What to capture:**
- SharePoint list view showing feature catalog
- List columns matching Dataverse table schema:
  - Feature Name, Category, Zone 1/2/3 Status, Approval Required, Approval Date, Change Ticket, Risk Rating
- Sample data populated in list (same features as Dataverse example)
- List views and filtering options visible
- SharePoint list toolbar (New, Edit, Export to Excel)
- Governance site navigation showing this is part of Copilot governance documentation

### Screenshot 21: Change Management System - Feature Enablement Request Form (Template)
**Portal Path:** Change management system (ServiceNow, Jira, SharePoint, etc.) → New Change Request → Copilot Studio Feature Enablement
**What to capture:**
- Change request form with Copilot Studio Feature Enablement template
- Form fields visible:
  - Feature Name (dropdown or text)
  - Environment(s) (dropdown or multi-select)
  - Governance Zone (dropdown: Zone 1/2/3)
  - Requestor (user lookup or text)
  - Business Justification (multi-line text area)
  - Risk Assessment (multi-line text area or dropdown)
  - Compensating Controls (multi-line text area)
  - Approval Required From (multi-select: Power Platform Admin, AI Governance Lead, Compliance Officer)
  - Implementation Date (date picker)
  - Expiration Date (date picker, optional for time-bound exceptions)
  - Rollback Plan (multi-line text area)
- Submit or Create button visible
- Template name visible in header or title

### Screenshot 22: Change Management System - Feature Request Approval Workflow (Zone 2)
**Portal Path:** Change management system → [Specific change request] → Workflow or Approval history
**What to capture:**
- Change request detail page for a Zone 2 feature enablement request
- Approval workflow stages visible:
  1. Submitted (Requester: John Doe, Date: 2026-02-01)
  2. Power Platform Admin Review (Approver: Jane Admin, Status: Approved, Date: 2026-02-02)
  3. AI Governance Lead Review (Approver: Bob Governance, Status: Approved, Date: 2026-02-03)
  4. Implementation (Status: Complete, Date: 2026-02-04)
- Each approval stage shows: Approver name, approval status, date/time, comments
- Request status: Approved or Implemented
- Change ticket number visible (e.g., CHG0001234)

### Screenshot 23: Change Management System - Feature Request Approval Workflow (Zone 3)
**Portal Path:** Change management system → [Zone 3 change request] → Workflow or Approval history
**What to capture:**
- Similar to Screenshot 22, but for Zone 3 request
- Approval workflow stages showing additional Compliance Officer approval:
  1. Submitted (Requester: Alice User)
  2. Power Platform Admin Review (Approved)
  3. AI Governance Lead Review (Approved)
  4. **Compliance Officer Review** (Approver: Carol Compliance, Status: Approved, Date: 2026-02-06)
  5. Implementation (Complete)
- Demonstrates Zone 3 requires additional approval stage
- Risk assessment document attached (if attachment section is visible)
- Change ticket number visible

### Screenshot 24: PowerShell - Deploy-FeatureCatalog.ps1 Execution
**What to capture:**
- PowerShell console window showing execution of Deploy-FeatureCatalog.ps1 script
- Command line: `.\Deploy-FeatureCatalog.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com"`
- Console output showing:
  - "Connecting to Dataverse environment: https://contoso.crm.dynamics.com"
  - "Connected successfully to [Org Name]"
  - "Creating table: FSI Feature Catalog"
  - "Table definition prepared. Columns to create:"
  - List of columns (Feature Name, Category, Zone Status fields, etc.)
  - Note about using Power Platform CLI commands
  - "Script completed. Table schema defined."
- Successful execution with green success messages
- PowerShell version and window title visible

### Screenshot 25: PowerShell - Populate-FeatureCatalog.ps1 Execution
**What to capture:**
- PowerShell console showing execution of Populate-FeatureCatalog.ps1 script
- Command line: `.\Populate-FeatureCatalog.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com"`
- Console output showing:
  - "Connected to Dataverse. Populating feature catalog..."
  - "✓ Created: Generative Actions (AI Builder)"
  - "✓ Created: Web Search Tool"
  - "✓ Created: Code Interpreter"
  - (Additional features...)
  - "Feature Catalog Population Summary:"
  - "  Success: 9"
  - "  Errors: 0"
  - "All features populated successfully!"
- Green checkmarks for successful records
- Summary statistics visible

### Screenshot 26: PowerShell - Get-FeatureComplianceReport.ps1 Output
**What to capture:**
- PowerShell console showing execution and output of Get-FeatureComplianceReport.ps1
- Command line: `.\Get-FeatureComplianceReport.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -OutputPath "C:\Reports"`
- Console output showing:
  - "Connected to Dataverse. Retrieving feature catalog..."
  - "Retrieved 9 feature records"
  - "Full report saved to: C:\Reports\FeatureComplianceReport_20260212-103045.csv"
  - "--- Feature Compliance Summary ---"
  - "Total Features: 9"
  - "High Risk: 3"
  - "Medium Risk: 4"
  - "Low Risk: 2"
  - "Zone 3 Prohibited Features: 5"
  - "Zone 3 Restricted (Exceptions): 1"
  - "✓ All time-bound exceptions are current (no expirations within 30 days)"
- Summary statistics and file paths visible
- Green success messages

### Screenshot 27: PowerShell - Get-FeatureComplianceReport.ps1 with Expiration Alerts
**What to capture:**
- Similar to Screenshot 26, but with expiration alerts triggered
- Console output showing:
  - "Retrieved 9 feature records"
  - "Full report saved to: C:\Reports\FeatureComplianceReport_20260212-103045.csv"
  - "Expiration alerts saved to: C:\Reports\FeatureExpirationAlerts_20260212-103045.csv"
  - "  - Features expiring or expired: 2"
  - "--- Feature Compliance Summary ---"
  - (Summary statistics...)
  - "⚠ WARNING: 2 feature(s) have expired or expiring exceptions!"
  - "Review expiration alerts report and renew or revoke access."
- Red warning messages for expiration alerts
- Two CSV files generated (full report + alerts)

### Screenshot 28: PowerShell - Test-DLPEnforcement.ps1 Output (Compliant)
**What to capture:**
- PowerShell console showing execution of Test-DLPEnforcement.ps1
- Command line: `.\Test-DLPEnforcement.ps1`
- Console output showing:
  - "Retrieving DLP policies..."
  - "Found 3 DLP policies"
  - "Analyzing Policy: Zone 3 Enterprise DLP"
  - "  ✓ shared_http is blocked"
  - "  ✓ shared_custom is blocked"
  - (Additional policies analyzed...)
  - "Validation results saved to: DLPValidation_20260212-103500.csv"
  - "✓ All high-risk connectors are properly blocked"
- Green checkmarks showing compliant configuration
- CSV file path visible

### Screenshot 29: PowerShell - Test-DLPEnforcement.ps1 Output (Non-Compliant)
**What to capture:**
- Similar to Screenshot 28, but showing non-compliant configuration
- Console output showing:
  - "Analyzing Policy: Zone 3 Enterprise DLP"
  - "  ✗ shared_http is NOT blocked (should be blocked for high-risk environments)"
  - "  ✓ shared_custom is blocked"
  - "Validation results saved to: DLPValidation_20260212-103500.csv"
  - "⚠ WARNING: 1 non-compliant connector(s) found!"
  - "Review DLP policies and move high-risk connectors to Blocked group."
- Red X showing non-compliant connector
- Red warning messages
- Demonstration of issue detection

### Screenshot 30: CSV Report - FeatureComplianceReport.csv Contents
**What to capture:**
- Excel or text editor showing contents of FeatureComplianceReport.csv
- CSV columns visible:
  - FeatureName, Category, Zone1Status, Zone2Status, Zone3Status, ApprovalRequired, ApprovalDate, ChangeTicket, ExpirationDate, DaysToExpiration, ExpirationAlert, RiskRating, Justification
- Sample rows showing multiple features with complete data
- Proper CSV formatting (comma-separated, quoted strings)
- At least 5-10 rows visible for comprehensive view
- Excel grid view or Notepad++ with data clearly readable

### Screenshot 31: CSV Report - FeatureExpirationAlerts.csv Contents
**What to capture:**
- Excel or text editor showing contents of FeatureExpirationAlerts.csv
- Same columns as full report, but filtered to only expired or expiring features
- Sample rows showing:
  - Feature with DaysToExpiration = 15 (EXPIRES SOON)
  - Feature with DaysToExpiration = -5 (EXPIRED)
- ExpirationAlert column showing alert text
- Demonstrates filtered report for governance team review

### Screenshot 32: Error Message - Generative Action Blocked in Zone 3
**Portal Path:** Copilot Studio → [Zone 3 Agent] → Attempt to add generative action
**What to capture:**
- Copilot Studio interface showing error message when attempting to use generative actions
- Error message text: "Generative actions are not enabled in this environment" or similar
- Optional guidance: "Contact your Power Platform Administrator or AI Governance Team for approval"
- Error icon or modal dialog
- Environment name visible (Zone 3)
- Clear, user-friendly error messaging

### Screenshot 33: Error Message - Code Interpreter Disabled in Zone 3
**Portal Path:** Copilot Studio → [Zone 3 Agent] → Settings → Tools → Attempt to enable Code Interpreter
**What to capture:**
- Agent settings panel with Code Interpreter toggle
- Tooltip or error message when hovering over or clicking disabled toggle
- Message text: "Code Interpreter is not available in this environment" or "This tool is restricted in Zone 3 environments"
- Optional: Contact information for requesting feature enablement
- Disabled/grayed-out toggle UI state

### Screenshot 34: Error Message - DLP Connector Blocked
**Portal Path:** Copilot Studio → [Zone 3 Agent] → Attempt to save agent with blocked connector
**What to capture:**
- Copilot Studio save error dialog or banner
- Error message text: "This agent uses connectors that are blocked by your organization's data policy and cannot be saved. Remove the [HTTP] action to continue."
- List of blocked connectors preventing save (if visible)
- Agent authoring canvas in background showing agent with prohibited connector
- Save button visible but disabled, or error modal blocking save action

### Screenshot 35: Monthly Feature Usage Report (Example)
**What to capture:**
- Excel spreadsheet or Power BI dashboard showing monthly feature usage report
- Report sections:
  - **Agents by Zone:** Bar chart or table showing count of agents in Zone 1/2/3
  - **Feature Adoption:** List of features and usage count in each zone
  - **Exception Tracking:** Table showing time-bound exceptions with expiration dates
  - **Compliance Status:** Percentage or count of agents compliant with zone restrictions
  - **Incidents:** Log of unauthorized feature usage attempts (if any)
- Date visible showing reporting period (e.g., "February 2026")
- Summary statistics and visualizations
- Professional report formatting for presentation to leadership

---

## Notes for Verification

- Capture screenshots from a pre-production or test environment when possible
- Use non-sensitive environment names, user accounts, and organization names (e.g., "Contoso" instead of real org)
- Include timestamps to demonstrate currency of configurations
- Verify UI matches documentation after Microsoft portal updates (features rolling out Q1-Q2 2026)
- PPAC Copilot governance page may not be available in all tenants yet; document feature availability status
- If specific feature toggles are not available, document as compensating control and show alternative enforcement (DLP policies)
- Capture both compliant and non-compliant scenarios to demonstrate validation and issue detection
- PowerShell screenshots should show successful execution with realistic data
- CSV reports should show properly formatted data with multiple records for realism
- Error messages should be clear and helpful, demonstrating good user experience even when features are restricted

---

## Feature Availability Note

The PPAC Copilot governance page and environment-specific feature toggles are rolling out to Power Platform tenants throughout Q1-Q2 2026. If your tenant has not yet received this update:

- The Copilot governance page may not appear in PPAC navigation
- Feature toggles may be controlled through Settings → Features instead
- Some features may only be disableable via Microsoft Support ticket
- Document feature availability status and use alternative enforcement methods (DLP, security roles) as compensating controls
- Check Microsoft 365 Message Center for announcements regarding Copilot governance feature availability
- Screenshots should be updated once features become available in your environment

---

## Screenshot Naming Convention

Save screenshots with the following naming format:
```
2.24_Screenshot-[Number]_[Description]_[YYYYMMDD].png
```

Examples:
- `2.24_Screenshot-01_PPAC-Copilot-Governance-Dashboard_20260212.png`
- `2.24_Screenshot-03_Zone3-Environment-Feature-Config_20260212.png`
- `2.24_Screenshot-17_Feature-Catalog-Data-Records_20260212.png`
- `2.24_Screenshot-26_PowerShell-Compliance-Report-Output_20260212.png`
- `2.24_Screenshot-32_Error-Generative-Action-Blocked_20260212.png`

Store all screenshots in the `docs/images/2.24/` directory for easy reference and documentation embedding.

---

## Screenshot Quality Guidelines

- **Resolution:** Minimum 1920x1080 for desktop portal screenshots; capture full browser window
- **Format:** PNG for static images (best quality for UI screenshots)
- **Content:** Ensure all text is readable; no excessive whitespace; crop appropriately
- **Annotations:** Add red boxes or arrows to highlight important elements (optional but helpful)
- **Privacy:** Redact any sensitive data (user emails, real organization names, customer data)
- **Consistency:** Use the same browser, zoom level, and theme across all screenshots for professional appearance
- **Context:** Include enough context (navigation, environment name, user role) to understand the screenshot location and purpose

---

## Priority Screenshots (Minimum Viable Documentation)

If time is limited, capture these minimum priority screenshots first:

1. **Screenshot 3:** Zone 3 environment with restrictive features (demonstrates control enforcement)
2. **Screenshot 8:** Generative action blocked in Zone 3 (demonstrates runtime restriction)
3. **Screenshot 17:** Feature catalog data with sample records (demonstrates governance tracking)
4. **Screenshot 22:** Change request approval workflow (demonstrates process integration)
5. **Screenshot 26:** Feature compliance report output (demonstrates reporting capability)
6. **Screenshot 6:** DLP policy with blocked connectors (demonstrates enforcement mechanism)

These 6 screenshots cover the core aspects of Control 2.24 and can serve as baseline documentation until full screenshot set is completed.
