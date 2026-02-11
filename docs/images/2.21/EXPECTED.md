# Control 2.21: AI Marketing Claims and Substantiation - Screenshot Specifications

## Required Screenshots

### Screenshot 1: Claims Inventory Registry
**Portal Path:** SharePoint → [Claims Governance Site] → Claims Inventory List (or Dataverse table)
**What to capture:**
- Central registry of AI marketing claims with metadata columns
- Claim type categorization (performance, capability, comparative, predictive, efficiency)
- Claim status (draft, under review, approved, published, retired)

### Screenshot 2: Pre-Publication Review Workflow
**Portal Path:** Power Automate → Flows → AI Claims Approval Flow
**What to capture:**
- Approval workflow stages (Compliance review → Technical validation → Legal review → Approval)
- Approver configuration (Compliance Officer, AI Governance Lead, Legal Counsel)
- Approval/rejection notification settings

### Screenshot 3: Substantiation Document Library
**Portal Path:** SharePoint → [Claims Governance Site] → Substantiation Documents
**What to capture:**
- Document library with substantiation evidence organized by claim
- Metadata schema (claim ID, evidence type, validation date, reviewer)
- Folder or tag structure linking evidence to specific claims

### Screenshot 4: Quarterly Review Schedule
**What to capture:**
- Calendar-based review process for published claims accuracy
- Review reminder automation (Power Automate scheduled flow)
- Review completion tracking with sign-off records

### Screenshot 5: FINRA 2210 Communication Classification
**What to capture:**
- Communication classification workflow (Correspondence vs. Retail Communication vs. Institutional)
- Pre-use principal approval documentation for Retail Communications
- Classification determination records

---

## Notes for Verification
- This control uses general-purpose SharePoint, Power Automate, and Purview capabilities
- No specialized FINRA/SEC compliance tools exist in Microsoft 365 for this purpose
- Capture from pre-production environment when possible
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates
