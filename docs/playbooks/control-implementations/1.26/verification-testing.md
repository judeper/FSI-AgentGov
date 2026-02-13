# Verification & Testing: Control 1.26 - Agent File Upload and File Analysis Restrictions

**Last Updated:** February 2026

## Manual Verification Steps

### Test 1: Verify File Upload Toggle State per Agent

1. Open Copilot Studio → Select target agent → Settings → Security
2. Locate the **File Upload** toggle
3. Verify the toggle state matches the agent's governance zone classification:
   - Zone 1: Enabled (acceptable) or Disabled
   - Zone 2: Disabled unless documented approval exists
   - Zone 3: Disabled unless formal risk assessment and approval on file
4. **EXPECTED:** File upload toggle aligns with zone governance requirements

### Test 2: Verify File Upload Blocked When Disabled

1. Open an agent with file upload disabled
2. Attempt to interact with the agent and upload a file
3. **EXPECTED:** The agent does not present a file upload option or rejects the upload attempt with an appropriate message

### Test 3: Verify File Upload Works When Enabled (Approved Agents)

1. Open an agent with file upload enabled and documented approval
2. Upload an approved file type (e.g., .pdf or .docx)
3. Verify the file is accepted and stored in the SPE container
4. Verify the agent can reference the file content in responses
5. **EXPECTED:** Approved file types are accepted; agent provides responses using file content

### Test 4: Verify Sensitivity Label Inheritance

1. Open an agent with file upload enabled
2. Upload a file with a sensitivity label applied (e.g., "Confidential")
3. Upload a second file with a more restrictive label (e.g., "Highly Confidential")
4. Verify the agent inherits the most restrictive label from its knowledge sources
5. **EXPECTED:** Agent displays the most restrictive sensitivity label from uploaded files

### Test 5: Verify DLP Policy Enforcement (Zone 2+)

1. Open an agent with file upload enabled in a Zone 2 or Zone 3 environment
2. Upload a file containing sensitive data patterns (e.g., test SSNs, account numbers)
3. Navigate to Microsoft Purview → Data Loss Prevention → Activity explorer
4. Verify a DLP policy match is logged for the upload
5. **EXPECTED:** DLP alerts are generated for uploads containing sensitive content

### Test 6: Verify Agent Inventory Accuracy

1. Run the `Get-AgentFileUploadStatus.ps1` script from the PowerShell Setup playbook
2. Compare the output against the documented file upload inventory
3. Verify all agents with file upload enabled are accounted for with appropriate approval documentation
4. **EXPECTED:** Inventory output matches documented records; no undocumented agents have file upload enabled

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.26-01 | File upload toggle matches zone | Toggle state aligns with governance zone | |
| TC-1.26-02 | Upload blocked when disabled | Agent rejects file upload attempts | |
| TC-1.26-03 | Upload works when enabled | Approved files accepted and processed | |
| TC-1.26-04 | Sensitivity label inherited | Agent inherits most restrictive label | |
| TC-1.26-05 | DLP policy triggered (Zone 2+) | DLP match logged in Activity explorer | |
| TC-1.26-06 | Agent inventory accurate | All upload-enabled agents documented | |
| TC-1.26-07 | Zone 3 default deny enforced | New agents default to file upload disabled | |
| TC-1.26-08 | File count limit enforced | Agent rejects uploads beyond 20-file limit | |

---

## Evidence Collection Checklist

- [ ] Screenshot: Copilot Studio agent settings showing File Upload toggle state
- [ ] Screenshot: File upload disabled agent rejecting upload attempt
- [ ] Screenshot: Sensitivity label displayed on agent with uploaded files
- [ ] Screenshot: DLP Activity explorer showing file upload policy match (Zone 2+)
- [ ] Export: Agent file upload inventory (Get-AgentFileUploadStatus output)
- [ ] Export: File upload compliance audit results per environment
- [ ] Document: Approval records for Zone 2/3 agents with file upload enabled
- [ ] Export: SPE container access control configuration

---

## Attestation Statement Template

```markdown
## Control 1.26 Attestation - Agent File Upload and File Analysis Restrictions

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. File upload governance is applied per governance zone:
   - Zone 1 agents: [Count] — file upload allowed with periodic review
   - Zone 2 agents: [Count] — file upload disabled unless approved ([Count] approved)
   - Zone 3 agents: [Count] — file upload default deny ([Count] exceptions with risk assessment)
2. Agent file upload inventory is current and accurate:
   - Total agents assessed: [Count]
   - Agents with file upload enabled: [Count]
   - Agents with file upload disabled: [Count]
3. DLP policies are active for agents with file upload enabled:
   - Zone 2 agents covered by DLP: [Yes/No]
   - Zone 3 agents covered by DLP with content scanning: [Yes/No]
4. Sensitivity label inheritance was verified:
   - Agents inheriting labels from uploaded files: [Yes/No]
5. Approval documentation exists for all Zone 2+ agents with file upload enabled: [Yes/No]
6. Exceptions documented and approved per governance process: [Count]

**Total Agents Assessed:** [Count]
**Compliant Agents:** [Count]
**Non-Compliant Agents:** [Count]

**Signature:** _______________________
**Date:** _______________________
```

---

## Zone-Specific Testing Requirements

| Zone | Test Frequency | Toggle State Review | DLP Validation | Sensitivity Labels | Inventory Check | SPE Container Review |
|------|----------------|---------------------|----------------|-------------------|-----------------|----------------------|
| Zone 1 | Quarterly | Quarterly | N/A | Quarterly | Quarterly | Quarterly |
| Zone 2 | Monthly | Monthly | Monthly | Monthly | Monthly | Monthly |
| Zone 3 | Weekly | Weekly | Weekly | Weekly | Weekly | Continuous |

---

## KQL Queries for Evidence

### Query Agent File Upload Activity (Sentinel)

```kql
PowerPlatformAdminActivity
| where TimeGenerated > ago(30d)
| where Operation contains "FileUpload" or Operation contains "ChatbotFileUpload"
| project
    TimeGenerated,
    EnvironmentName = tostring(AdditionalProperties.EnvironmentName),
    AgentName = tostring(AdditionalProperties.ChatbotName),
    UserPrincipalName = UserId,
    FileName = tostring(AdditionalProperties.FileName),
    FileSize = tostring(AdditionalProperties.FileSize),
    Operation
| order by TimeGenerated desc
```

### Query File Upload Toggle Changes (Sentinel)

```kql
PowerPlatformAdminActivity
| where TimeGenerated > ago(90d)
| where Operation contains "UpdateChatbot" or Operation contains "ChatbotSettings"
| where AdditionalProperties has "FileUpload"
| project
    TimeGenerated,
    EnvironmentName = tostring(AdditionalProperties.EnvironmentName),
    AgentName = tostring(AdditionalProperties.ChatbotName),
    ModifiedBy = UserId,
    SettingChanged = "FileUploadEnabled",
    NewValue = tostring(AdditionalProperties.FileUploadEnabled)
| order by TimeGenerated desc
```

### Query Agents with File Upload Enabled (Sentinel)

```kql
PowerPlatformAdminActivity
| where TimeGenerated > ago(7d)
| where Operation contains "ChatbotFileUpload" and Operation contains "Enabled"
| summarize
    LastUploadActivity = max(TimeGenerated),
    UploadCount = count()
    by
    EnvironmentName = tostring(AdditionalProperties.EnvironmentName),
    AgentName = tostring(AdditionalProperties.ChatbotName)
| order by UploadCount desc
```

---

[Back to Control 1.26](../../../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
