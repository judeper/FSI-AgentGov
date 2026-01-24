# Portal Walkthrough: Control 2.13 - Documentation and Record Keeping

**Last Updated:** January 2026
**Portal:** SharePoint, Microsoft Purview
**Estimated Time:** 4-6 hours

## Prerequisites

- [ ] SharePoint Admin role
- [ ] Purview Records Manager role
- [ ] Retention requirements documented per FINRA 4511
- [ ] Document taxonomy defined

---

## Step-by-Step Configuration

### Step 1: Create SharePoint Site Hierarchy

1. Open [SharePoint Admin Center](https://admin.microsoft.com/sharepoint)
2. Create AI Governance hub site:
   - Name: `AI-Governance`
   - Template: Team site
3. Create document libraries:
   - Agent Configurations
   - Interaction Logs
   - Approval Records
   - Incident Reports
   - Governance Decisions

### Step 2: Configure Document Metadata

1. Create site columns:
   - Agent ID (text)
   - Document Category (choice: Configuration, Log, Approval, Incident, Decision)
   - Regulatory Reference (choice: FINRA 4511, SEC 17a-4, SOX 404, GLBA)
   - Retention Period (choice: 3 years, 6 years, 7 years, Permanent)
   - Classification Date (date)
2. Create content types using site columns
3. Apply content types to libraries

### Step 3: Configure Retention Labels

1. Open [Microsoft Purview](https://compliance.microsoft.com)
2. Navigate to **Records management** > **File plan**
3. Create retention labels:

| Label | Retention | Action | Apply To |
|-------|-----------|--------|----------|
| FSI-Agent-6Year | 6 years | Delete | Agent records |
| FSI-Agent-7Year | 7 years | Delete | Regulatory records |
| FSI-Agent-Permanent | Permanent | None | Critical governance |

4. Publish labels to AI Governance site

### Step 4: Configure SEC 17a-4 Compliant Storage (Zone 3)

Per the October 2022 SEC amendments (effective May 2023), broker-dealers can choose either WORM storage or an audit-trail alternative.

**Option A: WORM Storage (Azure Immutable Blob)**

1. Open [Azure Portal](https://portal.azure.com)
2. Create storage account with immutability:
   - Enable blob versioning
   - Configure immutability policy (time-based)
   - Set retention period: 6+ years
3. Configure Purview to use immutable storage

**Option B: Audit-Trail Alternative**

1. Ensure complete audit trail of all record access and modifications
2. Implement integrity verification mechanisms
3. Document procedures demonstrating modification detection capability
4. Consult compliance/legal for specific implementation requirements

### Step 5: Configure Auto-Labeling

1. In Purview > Auto-labeling:
2. Create policy for agent interaction logs:
   - Condition: Location = AI Governance site
   - Condition: Content type = Interaction Log
   - Action: Apply FSI-Agent-6Year label
3. Enable policy

### Step 6: Create Examination Response Procedures

Document procedures for regulatory examination:
1. Designated custodians and contact info
2. Search procedures for agent records
3. Export and production process
4. Chain of custody documentation

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **Retention** | 3 years | 6 years | 6-7 years |
| **Metadata** | Basic | Comprehensive | Full taxonomy |
| **Auto-Labeling** | None | Recommended | Required |
| **SEC 17a-4** | N/A | N/A | WORM or audit-trail |
| **Audit** | Annual | Quarterly | Monthly |

---

## FSI Example Configuration

```yaml
Document Management: AI Governance Records

SharePoint Site: https://tenant.sharepoint.com/sites/AI-Governance

Libraries:
  - AgentConfigurations: Manifest exports, prompt versions
  - InteractionLogs: Conversation transcripts
  - ApprovalRecords: Deployment approvals, change requests
  - IncidentReports: Security incidents, compliance issues
  - GovernanceDecisions: Policy decisions, risk acceptances

Retention:
  Default: 6 years
  SEC 17a-4 content: 7 years (WORM or audit-trail alternative)
  Permanent: Board approvals, critical decisions

Auto-Labeling:
  Enabled: Yes
  Scope: All libraries
  Default Label: FSI-Agent-6Year

Examination Readiness:
  Custodian: [Name]
  Backup: [Name]
  Response SLA: 48 hours
```

---

## Validation

After completing these steps, verify:

- [ ] SharePoint site hierarchy created
- [ ] Metadata columns and content types configured
- [ ] Retention labels published and applied
- [ ] SEC 17a-4 compliant storage configured (WORM or audit-trail, Zone 3)
- [ ] Examination procedures documented

---

[Back to Control 2.13](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
