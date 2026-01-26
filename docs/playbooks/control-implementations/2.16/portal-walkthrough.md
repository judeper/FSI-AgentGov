# Portal Walkthrough: Control 2.16 - RAG Source Integrity Validation

**Last Updated:** January 2026
**Portals:** Copilot Studio, SharePoint Admin Center
**Estimated Time:** 1-2 hours initial setup, ongoing monitoring

## Prerequisites

- [ ] Copilot Studio Environment Admin or Maker role
- [ ] SharePoint Admin role (for site-based knowledge sources)
- [ ] Knowledge source inventory documented
- [ ] Approval workflow defined for new knowledge sources
- [ ] Content versioning strategy established

---

## Step-by-Step Configuration

### Step 1: Inventory Existing Knowledge Sources

1. Open [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select the target environment
3. Open each agent and review **Knowledge** settings
4. Document all knowledge sources:
   - SharePoint sites
   - Dataverse tables
   - External websites (if allowed)
   - Uploaded files

### Step 2: Configure SharePoint Knowledge Source

1. In Copilot Studio, open the agent
2. Navigate to **Knowledge** > **+ Add knowledge**
3. Select **SharePoint**
4. Configure the connection:
   - Enter SharePoint site URL
   - Select specific libraries/folders (avoid entire site if possible)
   - Review indexing scope

**FSI Best Practice:** Limit knowledge sources to specific document libraries rather than entire sites to reduce scope and improve accuracy.

### Step 3: Establish Content Approval Workflow

1. In SharePoint Admin Center, configure content approval:
   - Navigate to target site > **Site settings** > **Site content types**
   - Enable content approval for document libraries
2. Or use Power Automate approval flow:
   - Create flow triggered on new document upload
   - Route to content owner for approval
   - Only approved content is indexed

### Step 4: Configure Knowledge Source Versioning

1. Enable versioning on SharePoint document libraries:
   - Library settings > **Versioning settings**
   - Enable **Create major versions**
   - Set version history limits (e.g., 50 versions)
2. Document version control requirements:
   - Major version = approved for agent use
   - Minor version = draft, not indexed

### Step 5: Set Up Staleness Detection

1. Create a monitoring process for content freshness:
   - Define maximum age thresholds (e.g., 365 days)
   - Create Power Automate flow or scheduled report
   - Alert content owners of stale documents

2. Configure Copilot Studio refresh settings:
   - Knowledge sources sync periodically
   - Document expected refresh frequency

### Step 6: Enable Citation Logging

1. Verify agent includes citations in responses:
   - Test agent and confirm source citations appear
   - Document citation format for audit

2. Configure audit logging (via Control 1.7):
   - Ensure Copilot Studio audit events capture knowledge queries
   - Retain logs per regulatory requirements

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|--------------------|
| **Knowledge Source Approval** | Informal | Documented approval | **Formal workflow** |
| **Content Versioning** | Optional | Enabled | **Required with audit** |
| **Staleness Threshold** | None | 365 days | **90 days** |
| **Citation Display** | Optional | Enabled | **Required** |
| **Source Inventory** | Informal | Documented | **Audited quarterly** |
| **External Sources** | Allowed | Restricted | **Prohibited** |

---

## FSI Example Configuration

```yaml
Agent: Client Portfolio Advisor
Environment: FSI-Wealth-Prod

Knowledge Sources:
  1. Source: SharePoint - Investment Research Library
     URL: https://company.sharepoint.com/sites/research/library
     Scope: "Published Research" folder only
     Approval: Content approval workflow enabled
     Owner: Research Team Lead
     Review Frequency: Monthly

  2. Source: SharePoint - Product Documentation
     URL: https://company.sharepoint.com/sites/products/docs
     Scope: "Approved Documents" library
     Approval: Major versions only (minor = draft)
     Owner: Product Management
     Review Frequency: Quarterly

  3. Source: Dataverse - Client FAQs
     Table: fsi_clientfaqs
     Scope: Status = "Published"
     Approval: Via Dataverse workflow
     Owner: Client Services Lead
     Review Frequency: Monthly

Prohibited Sources:
  - External websites
  - Personal OneDrive
  - Unapproved SharePoint sites
  - Third-party knowledge bases

Staleness Policy:
  - Alert at 90 days without update
  - Review required at 180 days
  - Removal consideration at 365 days
```

---

## Validation

After completing these steps, verify:

- [ ] All knowledge sources are inventoried and documented
- [ ] Approval workflow is functioning for new content
- [ ] Versioning is enabled on SharePoint sources
- [ ] Staleness monitoring is active
- [ ] Citations appear in agent responses
- [ ] Audit logging captures knowledge queries

---

[Back to Control 2.16](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
