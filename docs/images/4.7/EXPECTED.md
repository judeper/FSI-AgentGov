# Control 4.7: Microsoft 365 Copilot Data Governance - Screenshot Specifications

## Required Screenshots

### Screenshot 1: M365 Admin Center Copilot Settings
**Portal Path:** Microsoft 365 Admin Center → Copilot
**What to capture:**
- Copilot management dashboard
- Feature toggles and configuration options
- License assignment summary

### Screenshot 2: Copilot License Inventory
**Portal Path:** Microsoft 365 Admin Center → Billing → Licenses → Microsoft 365 Copilot
**What to capture:**
- Total Copilot licenses assigned vs. available
- Assigned user list or count
- License SKU details (SkuPartNumber)

### Screenshot 3: Restricted Content Discovery Configuration
**Portal Path:** SharePoint Admin Center → Settings → Restricted Content Discovery
**What to capture:**
- Sensitive sites excluded from Copilot (executive, legal, HR, M&A)
- Exclusion list with site URLs
- RCD toggle status

### Screenshot 4: Plugin Governance Settings
**Portal Path:** Microsoft 365 Admin Center → Copilot → Plugins
**What to capture:**
- Plugin approval workflow configuration
- Allowed vs. blocked third-party plugins
- Plugin governance policy settings

### Screenshot 5: Web Search Control
**Portal Path:** Microsoft 365 Admin Center → Copilot → Settings → Web search
**What to capture:**
- Web grounding enabled/disabled setting per governance level
- Web search policy configuration
- Scope of web search restriction

### Screenshot 6: Copilot Usage Analytics
**Portal Path:** Microsoft 365 Admin Center → Reports → Usage → Microsoft 365 Copilot
**What to capture:**
- Copilot adoption and usage metrics
- Feature utilization breakdown (Word, Excel, PowerPoint, Outlook, Teams)
- Active user trends over time

### Screenshot 7: PowerShell Verification Output
**What to capture:**
- `Get-MgSubscribedSku` output showing Copilot SKU (filtered by SkuPartNumber)
- `Get-MgUser` output showing Copilot license assignments
- EEEU report results (Content Shared with Everyone Except External Users)

---

## Notes for Verification
- Capture from pre-production environment when possible
- Ensure user names and site URLs are representative but not sensitive
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates
- EEEU remediation is a critical pre-deployment prerequisite
