# Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources - Screenshot Specifications

## Required Screenshots

### Screenshot 1: Copilot Studio Agent Knowledge Sources
**Portal Path:** Microsoft Copilot Studio → Agents → [Agent Name] → Knowledge
**What to capture:**
- Agent knowledge source list showing connected SharePoint libraries
- SharePoint site URL and library/folder path for each knowledge source
- Knowledge source configuration panel

### Screenshot 2: SharePoint Library Permissions Overview
**Portal Path:** SharePoint Admin Center → Sites → Active sites → [Site Name] → Permissions
**What to capture:**
- Site-level permissions summary for an agent knowledge source site
- Site collection administrators list
- Permission groups and membership

### Screenshot 3: Item-Level Unique Permissions
**Portal Path:** SharePoint site → Knowledge source library → [Item] → Manage Access
**What to capture:**
- Item with broken permission inheritance (unique permissions indicator)
- Manage Access panel showing sharing scope (Anyone links, external users, EEEU)
- Sensitivity label applied to the item

### Screenshot 4: Scan Output CSV Review
**What to capture:**
- CSV output from `Get-KnowledgeSourceItemPermissions.ps1` opened in Excel or terminal
- Columns visible: SiteUrl, LibraryName, FileName, SensitivityLabel, SharingScopes, RiskLevel
- Risk distribution showing CRITICAL, HIGH, MEDIUM, LOW items

### Screenshot 5: Pre-Deployment Gate Status
**What to capture:**
- Compliance report showing BLOCKED or CLEARED gate status
- Risk summary table with counts per risk level
- Gate clearance documentation or sign-off

### Screenshot 6: Recurring Scan Schedule Configuration
**What to capture:**
- For Zone 1/2: Windows Task Scheduler showing monthly scan task (`AgentKnowledgeSourceScan-Monthly`)
- For Zone 3: Azure Automation runbook schedule configuration
- Schedule details (monthly cadence, execution time, target libraries)

### Screenshot 7: PowerShell Scan Execution Output
**What to capture:**
- Terminal output from `Get-KnowledgeSourceItemPermissions.ps1` execution
- Scan summary showing total items scanned, items with unique permissions
- Risk distribution (CRITICAL/HIGH/MEDIUM/LOW counts)
- Output file path confirmation

---

## Notes for Verification
- Capture from pre-production environment when possible
- Ensure user names and site URLs are representative but not sensitive
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates
- Pre-deployment gate screenshots should show both BLOCKED and CLEARED states if possible

---

## Screenshot Naming Convention

Save screenshots with the following naming format:
```
4.8_Screenshot-[Number]_[Description]_[YYYYMMDD].png
```

Examples:
- `4.8_Screenshot-01_Copilot-Studio-Knowledge-Sources_20260317.png`
- `4.8_Screenshot-03_Item-Level-Unique-Permissions_20260317.png`
- `4.8_Screenshot-05_Pre-Deployment-Gate-Status_20260317.png`

Store all screenshots in the `docs/images/4.8/` directory for easy reference and documentation embedding.

---

[Back to Control 4.8](../../controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md)
