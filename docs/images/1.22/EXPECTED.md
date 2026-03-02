# Control 1.22: Information Barriers for AI Agents

## Expected Screenshots

### Screenshot 1: Purview Information Barrier Segments
**Portal Path:** Microsoft Purview Compliance Portal → Information Barriers → Segments
**What to capture:**
- List of defined segments (IB-Research, IB-Trading, IB-InvestmentBanking, IB-Sales, IB-Compliance)
- Segment filter attributes (Department-based Microsoft Entra ID attributes)
- Segment status (Active)

### Screenshot 2: Information Barrier Policies
**Portal Path:** Microsoft Purview Compliance Portal → Information Barriers → Policies
**What to capture:**
- Configured barrier policies showing blocked segment pairs (e.g., Research ↔ Trading)
- Policy status (Active)
- Policy application scope

### Screenshot 3: SharePoint Site Barrier Alignment
**Portal Path:** SharePoint Admin Center → Sites → Active Sites → [Site] → Permissions
**What to capture:**
- Site permissions showing alignment with barrier policies
- Information barrier mode setting for the site
- Segment association for the site

### Screenshot 4: Wall-Crossing Approval Workflow
**What to capture:**
- Wall-crossing request form or approval workflow (Power Automate or custom)
- Required approvers (Compliance + Legal + Business Unit head)
- Documentation requirements for wall-crossing exceptions

### Screenshot 5: PowerShell Verification Output
**What to capture:**
- `Get-InformationBarrierPolicy` output showing active barrier policies
- `Get-InformationBarrierSegment` output showing defined segments
- User segment assignment verification via `Get-InformationBarrierRecipientStatus`

---

## Verification Focus
- Capture from pre-production environment when possible
- Ensure segment names and user information are representative but not sensitive
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates
