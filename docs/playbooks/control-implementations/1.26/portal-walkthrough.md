# Portal Walkthrough: Control 1.26 - Agent File Upload and File Analysis Restrictions

**Last Updated:** February 2026
**Portal:** Copilot Studio, Power Platform Admin Center
**Estimated Time:** 20-30 minutes

## Prerequisites

- [ ] Power Platform Admin or Copilot Studio Agent Author role
- [ ] Access to Copilot Studio and Power Platform Admin Center
- [ ] Knowledge of agent governance zone classifications
- [ ] Approved file upload enablement request (Zone 2+)

---

## Step-by-Step Configuration

### Step 1: Navigate to Agent Settings in Copilot Studio

1. Open [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select the target agent from the agent list
3. Click **Settings** (gear icon) in the top navigation
4. Select **Security** from the settings menu

### Step 2: Configure File Upload Security Toggle

1. Locate the **File Upload** section under Security settings
2. Review the current toggle state (enabled or disabled)
3. Set the toggle based on the agent's governance zone:
   - **Zone 1 agents:** File upload may remain enabled (Microsoft defaults)
   - **Zone 2 agents:** Disable file upload unless an approved enablement request exists
   - **Zone 3 agents:** Disable file upload; enable only with formal risk assessment and approval documentation
4. Click **Save** to apply changes

> **Note:** When file upload is enabled, agents can accept up to 20 files as knowledge sources. Supported file types include docx, pptx, xlsx, pdf, txt, and csv.

### Step 3: Review File Size Limits

1. Within the File Upload security settings, review the applicable file size limits:
   - pptx, pdf, docx: up to 512MB per file
   - txt, csv, xls, xlsx, ppt, doc: up to 150MB per file
2. Document any environment-specific size restrictions that apply
3. For Zone 3 agents, verify whether reduced file size limits have been configured as part of the risk assessment

### Step 4: Verify Sensitivity Label Configuration

1. Navigate to the agent's **Knowledge** section
2. If file upload is enabled, upload a test file with a sensitivity label applied
3. Verify the agent displays the inherited sensitivity label
4. Confirm the agent inherits the most restrictive label when multiple files are uploaded

> **Important:** Sensitivity labels are auto-applied to uploaded files. The agent inherits the most restrictive label from its file knowledge sources, which may restrict the agent's ability to share responses with certain users.

### Step 5: Review SharePoint Embedded Container

1. Navigate to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Select **Environments** from the left navigation
3. Select the environment hosting the agent
4. Review the SharePoint Embedded (SPE) container configuration
5. Verify access controls and retention policies are applied to the SPE container
6. Document the container ID and associated environment for governance records

### Step 6: Verify DLP Policy Coverage (Zone 2+)

1. Navigate to [Microsoft Purview Compliance Portal](https://purview.microsoft.com)
2. Select **Data Loss Prevention** → **Policies**
3. Verify a DLP policy exists that covers Power Platform connectors in the agent's environment
4. Confirm the policy is in **Enforce** mode
5. For Zone 3 agents, verify content scanning rules are active and scoped to file upload data

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|---------------------|
| **File upload toggle default** | Allowed | Disabled until approved | Default deny |
| **Approval required** | No | Documented approval | Formal risk assessment |
| **Sensitivity labels** | Recommended | Required | Required with audit |
| **DLP policy coverage** | Not required | Required | Required with scanning |
| **SPE container review** | Quarterly | Monthly | Continuous |
| **Agent inventory tracking** | Recommended | Required | Required |
| **Review frequency** | Quarterly | Monthly | Weekly |
| **Exception process** | Informal | Documented | Documented with approval |

---

## Validation

After completing these steps, verify:

- [ ] File upload toggle is set to the correct state for the agent's governance zone
- [ ] Approval documentation exists for Zone 2 and Zone 3 agents with file upload enabled
- [ ] Sensitivity labels are being applied to uploaded files
- [ ] DLP policies cover agents with file upload enabled (Zone 2+)
- [ ] SPE container access controls and retention policies are configured
- [ ] Agent is recorded in the file upload inventory

---

[Back to Control 1.26](../../../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
