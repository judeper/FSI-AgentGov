<!-- TEMPLATE NOTE: EXPECTED.md files use two formats across this repository:
     - "Required Screenshots" (detailed per-screenshot subsections with Notes for Verification) — used for controls 1.21+, 2.16+, 3.10+, 4.6+
     - "Expected Screenshots" (table format with Verification Focus) — used for earlier controls
     Both formats are valid. The detailed format was adopted for later controls that require more verification guidance. -->
# Control 1.28: Policy-Based Agent Publishing Restrictions - Screenshot Specifications

## Required Screenshots

### Screenshot 1: DLP Policy Configuration - Zone 3 Strict Policy
**Portal Path:** Power Platform Admin Center → Policies → Data policies → [Zone 3 Policy]
**What to capture:**
- DLP policy name: "Zone 3 - Enterprise Customer-Facing DLP Policy"
- Connector classification table showing three categories:
  - **Business:** SharePoint, Dataverse, Office 365 Groups (minimal approved connectors)
  - **Non-Business:** (empty)
  - **Blocked:** HTTP, Telegram, Facebook, Public Website, Twitter, RSS (extensive block list)
- Policy scope showing Zone 3 environments assigned
- Save button and policy status (Active)

### Screenshot 2: Connector Classification Interface
**Portal Path:** Power Platform Admin Center → Policies → Data policies → [Policy] → Assign Connectors
**What to capture:**
- Three connector category columns: Business | Non-Business | Blocked
- Drag-and-drop interface showing connectors in each category
- Search bar for finding specific connectors
- Connector icons and names clearly visible
- Example of moving a connector between categories

### Screenshot 3: DLP Policy Environment Assignment
**Portal Path:** Power Platform Admin Center → Policies → Data policies → [Policy] → Define scope
**What to capture:**
- Environment selection interface with options:
  - "Add multiple environments"
  - "Add all environments"
  - "Exclude certain environments"
- List of environments with checkboxes
- Selected environments for Zone 3 policy (e.g., "Production", "Customer-Facing")
- Environment count and summary

### Screenshot 4: Security Scan - DLP Violation Detected
**Portal Path:** Copilot Studio → [Agent] → Publish → Security scan results
**What to capture:**
- Security scan panel with red error indicator
- Error message: "This agent cannot be published due to DLP policy violations"
- Details section showing:
  - Violating connector name (e.g., "HTTP connector")
  - Reason: "This connector is blocked by DLP policy"
  - Recommended action: "Remove connector or request DLP exception"
- Publish button grayed out/disabled
- Agent name visible in header

### Screenshot 5: Security Scan - Passed (Green Checkmark)
**Portal Path:** Copilot Studio → [Agent] → Publish → Security scan results
**What to capture:**
- Security scan panel with green checkmark indicator
- Success message: "No security issues detected"
- Summary showing:
  - DLP compliance: Passed
  - Channel restrictions: Passed
  - Configuration security: Passed
- Publish button enabled
- Agent name visible in header

### Screenshot 6: Security Scan - Warning (Yellow - Zone 1)
**Portal Path:** Copilot Studio → [Agent] → Publish → Security scan results
**What to capture:**
- Security scan panel with yellow warning indicator
- Warning message: "1 warning detected - review before publishing"
- Warning details:
  - Warning type: "Insecure connector configuration"
  - Description: "HTTP connector is used without certificate validation"
  - Impact: "Low risk for personal productivity agents"
- Acknowledge checkbox: "I understand the risk and want to proceed"
- Publish button enabled after acknowledgment
- Zone 1 environment indicator

### Screenshot 7: Blocked Channel Configuration
**Portal Path:** Copilot Studio → [Agent] → Settings → Channels
**What to capture:**
- Channels configuration page listing available channels
- Prohibited channels highlighted or marked as blocked:
  - Facebook (disabled/grayed out)
  - Telegram (disabled/grayed out)
  - Public Website (disabled/grayed out)
- Allowed channels available for selection:
  - Microsoft Teams (enabled/available)
  - Microsoft Teams (Internal) (enabled/available)
- Channel status: "Blocked by DLP policy"
- Save button

### Screenshot 8: Approval Workflow Configuration
**Portal Path:** Power Platform Admin Center → Environments → [Environment] → Settings → Features
**What to capture:**
- Features settings panel
- "Copilot and Power Apps" section expanded
- Approval settings:
  - "Require approval for new chatbots" toggle (enabled)
  - "Require approval for chatbot updates" toggle (enabled/optional)
- Environment name visible (Zone 2 or Zone 3)
- Save button

### Screenshot 9: Submit Agent for Approval (Agent Author View)
**Portal Path:** Copilot Studio → [Agent] → Publish → Submit for approval
**What to capture:**
- Publish agent dialog with approval submission form
- Form fields:
  - **Publishing justification:** Text field with sample text (e.g., "Customer support agent for Q1 launch")
  - **Expected impact:** Text field describing usage (e.g., "100 customer service reps")
  - **Testing evidence:** Reference to test results
- Security scan status: Passed (green checkmark)
- "Submit for approval" button (primary action)
- "Cancel" button

### Screenshot 10: Pending Approval Request (Admin View)
**Portal Path:** Power Platform Admin Center → Pending approvals (or email notification)
**What to capture:**
- Pending approval notification showing:
  - Agent name: "Customer Support Agent - Zone 2"
  - Requested by: Agent author name
  - Environment: Zone 2 environment name
  - Publishing justification text
  - Security scan results: Passed
  - DLP compliance status: Compliant
- Action buttons:
  - "Approve" (primary)
  - "Reject" (secondary)
- Comment field for approval/rejection notes
- Timestamp of request

### Screenshot 11: Approved Publishing Request
**Portal Path:** Power Platform Admin Center → Completed approvals
**What to capture:**
- Approval record showing:
  - Agent name
  - Approved by: Power Platform Admin name
  - Approval timestamp
  - Admin comments: "Approved - Security review completed"
  - Status: "Approved"
- Approval history timeline
- Link to view agent details

### Screenshot 12: Rejected Publishing Request
**Portal Path:** Power Platform Admin Center → Completed approvals (or Copilot Studio notification)
**What to capture:**
- Rejection record showing:
  - Agent name
  - Rejected by: Power Platform Admin name
  - Rejection timestamp
  - Admin comments: "Insufficient testing evidence - please provide test results"
  - Status: "Rejected"
- Agent author notification display
- Option to re-submit request

### Screenshot 13: Published Agent with DLP Violation (Blocked Update)
**Portal Path:** Copilot Studio → [Agent] → Publish (for update)
**What to capture:**
- Published agent details showing:
  - Agent status: "Published (Non-Compliant)"
  - Last published date
  - Current version number
- Attempt to publish update:
  - Security scan showing DLP violation
  - Error message: "This published agent has DLP violations and cannot be updated"
  - Details: "SharePoint connector is now blocked by DLP policy"
- Update button grayed out/disabled
- Warning banner: "This agent requires remediation before updates can be published"

### Screenshot 14: Environment Promotion Pipeline
**Portal Path:** Power Platform Admin Center → Environment groups
**What to capture:**
- Environment group configuration showing:
  - Group name: "Zone 3 Production Pipeline"
  - Linked environments:
    - Development (Dev-Zone3)
    - Test (UAT-Zone3)
    - Production (Prod-Zone3)
  - Promotion pipeline diagram or flow
- Environment metadata:
  - Environment type (Sandbox/Production)
  - DLP policy assigned
  - Approval workflow status

### Screenshot 15: Purview Audit Log - Agent Publishing Event
**Portal Path:** Microsoft Purview Compliance Portal → Audit → Search results
**What to capture:**
- Audit log entry for agent publishing showing:
  - **Activity:** "Publish chatbot" or "Create chatbot"
  - **User:** Agent author name
  - **Date/Time:** Timestamp
  - **Item:** Agent name
  - **Details:** Environment, DLP status, approval status
- Expanded details panel showing:
  - Agent ID
  - Environment ID
  - Connector usage details
  - Security scan results
- Export button for compliance records

### Screenshot 16: Purview Audit Log - DLP Violation Event
**Portal Path:** Microsoft Purview Compliance Portal → Audit → Search results
**What to capture:**
- Audit log entry for DLP violation showing:
  - **Activity:** "DLP policy violation detected"
  - **User:** Agent author name
  - **Date/Time:** Timestamp
  - **Item:** Agent name
  - **Details:** Violating connector, DLP policy name
- Expanded details showing:
  - Blocked connector name (e.g., "HTTP")
  - DLP policy enforcing the block
  - Environment name
  - Publishing attempt result: "Blocked"

### Screenshot 17: Purview Audit Log - Approval Event
**Portal Path:** Microsoft Purview Compliance Portal → Audit → Search results
**What to capture:**
- Audit log entry for approval showing:
  - **Activity:** "Approve chatbot publishing request"
  - **User:** Power Platform Admin name
  - **Date/Time:** Timestamp
  - **Item:** Agent name
  - **Details:** Approval comments, agent author
- Expanded details showing:
  - Request submission timestamp
  - Approval timestamp
  - Approver comments
  - Agent details (name, environment, purpose)

### Screenshot 18: PowerShell Compliance Report Output
**What to capture:**
- Terminal/PowerShell window showing output from compliance audit script
- Report sections:
  - **Summary:**
    - Total Agents: 15
    - Compliant Agents: 12
    - Non-Compliant Agents: 3
  - **Non-Compliant Agents Table:**
    - Environment | Agent Name | DLP Violations | Blocked Channels
    - Production | "Legacy Support Agent" | "HTTP connector" | "Facebook"
    - UAT | "Test Agent 1" | "Twitter connector" | ""
- Export confirmation: "Report exported to: agent-publishing-compliance-report-20260212.csv"

### Screenshot 19: PowerShell DLP Policy Creation
**What to capture:**
- Terminal/PowerShell window showing DLP policy creation script execution
- Script output:
  - "Creating Zone 1 DLP policy..."
  - "✓ Zone 1 DLP policy created: Zone 1 - Personal Productivity DLP Policy"
  - "Adding connectors to Business group..."
  - "✓ SharePoint added to Business group"
  - "✓ Dataverse added to Business group"
  - "Adding connectors to Blocked group..."
  - "✓ Telegram added to Blocked group"
  - "✓ Facebook added to Blocked group"
  - "DLP policies created successfully. Next: Assign policies to environments."
- Success indicators (green checkmarks or "✓")

### Screenshot 20: Custom Connector Pattern Configuration
**Portal Path:** Power Platform Admin Center → Policies → Data policies → [Policy] → Custom connector patterns
**What to capture:**
- Custom connector patterns configuration page
- URL pattern rules:
  - **Allowed domain patterns:**
    - `*.yourcompany.com`
    - `*.microsoft.com`
  - **Blocked domain patterns:**
    - `*` (block all others)
- HTTP connector restriction settings
- Pattern matching preview showing examples
- Save button

---

## Notes for Verification

- Capture from pre-production or test environment when possible
- Use non-sensitive agent names and data for screenshots
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates (last verified: February 2026)
- DLP enforcement change (removal of "Soft-Enabled" exemption) effective February 2025
<!-- NEEDS_HUMAN_REVIEW: MC1217615 is also referenced in 1.27/EXPECTED.md for content moderation GA.
     Verify this single MC post covers both security scan GA and content moderation GA features. -->
- Security scan feature became GA January 31, 2026 (MC1217615)
- Approval workflow settings may vary by tenant rollout schedule
- For Zone 3 documentation, capture multi-level approval if configured

---

## Feature Availability Note

Policy-based agent publishing restrictions with DLP enforcement became mandatory in February 2025 (removal of "Soft-Enabled" exemption). Security scans with UI integration became GA on January 31, 2026 (MC1217615 — see review comment above). If your tenant has not yet received these updates:

- DLP violations may not block publishing (old behavior - "Soft-Enabled")
- Security scan UI may appear in a different location or under preview flag
- Approval workflow settings may be under different menu path
- Contact Microsoft support to confirm rollout status for your tenant region
- Screenshots should be updated once features are available in your environment

---

## Screenshot Organization

Organize screenshots in this directory as:
- `1.28-01-dlp-policy-zone3.png` — DLP policy configuration
- `1.28-02-connector-classification.png` — Connector drag-and-drop interface
- `1.28-03-environment-assignment.png` — Environment scope selection
- `1.28-04-security-scan-violation.png` — DLP violation detected
- `1.28-05-security-scan-passed.png` — Security scan passed
- `1.28-06-security-scan-warning.png` — Warning in Zone 1
- `1.28-07-blocked-channels.png` — Blocked channel configuration
- `1.28-08-approval-workflow-settings.png` — Environment approval settings
- `1.28-09-submit-for-approval.png` — Agent author submission form
- `1.28-10-pending-approval.png` — Admin approval request view
- `1.28-11-approved-request.png` — Approved publishing record
- `1.28-12-rejected-request.png` — Rejected publishing record
- `1.28-13-blocked-update.png` — Published agent with DLP violation
- `1.28-14-environment-promotion.png` — Environment group pipeline
- `1.28-15-audit-log-publishing.png` — Purview audit log entry (publishing)
- `1.28-16-audit-log-dlp-violation.png` — Purview audit log entry (DLP)
- `1.28-17-audit-log-approval.png` — Purview audit log entry (approval)
- `1.28-18-powershell-compliance-report.png` — PowerShell report output
- `1.28-19-powershell-dlp-creation.png` — PowerShell DLP policy creation
- `1.28-20-custom-connector-patterns.png` — Custom connector URL patterns
