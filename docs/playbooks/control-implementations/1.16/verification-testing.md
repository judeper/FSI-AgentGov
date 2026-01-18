# Verification & Testing: Control 1.16 - Information Rights Management (IRM)

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Azure RMS Activation

1. Open Microsoft 365 Admin Center
2. Navigate to Settings > Org settings > Microsoft Azure Information Protection
3. **EXPECTED:** Status shows "Protection is activated"

### Test 2: Verify IRM-Enabled Sensitivity Labels

1. Open Microsoft Purview > Information protection > Labels
2. Select sensitivity label used for agent content
3. Verify encryption settings are configured
4. **EXPECTED:** Label has encryption with permissions defined

### Test 3: Test SharePoint Library IRM

1. Navigate to SharePoint library with IRM enabled
2. Upload a test document
3. Download the document
4. **EXPECTED:** Document downloads with IRM protection applied

### Test 4: Test Agent IRM Access

1. Trigger agent to retrieve IRM-protected content
2. Verify agent can read content
3. Verify agent cannot bypass restrictions (copy, print)
4. **EXPECTED:** Agent reads content within IRM constraints

### Test 5: Verify Document Tracking

1. Access an IRM-protected document
2. Check Purview > Track usage
3. **EXPECTED:** Access event logged with user details

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.16-01 | Azure RMS status | Shows activated | |
| TC-1.16-02 | Sensitivity label encryption | Configured correctly | |
| TC-1.16-03 | Library IRM enabled | Downloads protected | |
| TC-1.16-04 | Agent reads IRM content | Content accessible | |
| TC-1.16-05 | Agent cannot bypass IRM | Restrictions enforced | |
| TC-1.16-06 | Document tracking active | Access logged | |
| TC-1.16-07 | Content expiration | Expires per policy | |

---

## Evidence Collection Checklist

### Azure RMS

- [ ] Screenshot: Azure RMS activation status
- [ ] Document: RMS configuration settings

### Sensitivity Labels

- [ ] Screenshot: Label configuration with encryption
- [ ] Screenshot: Label permissions assignments
- [ ] Document: Label policy assignments

### SharePoint IRM

- [ ] Screenshot: Library IRM settings
- [ ] Screenshot: IRM configuration options
- [ ] Document: Libraries with IRM enabled

### Document Tracking

- [ ] Screenshot: Track usage dashboard
- [ ] Export: Sample access log entries

---

## Evidence Artifact Naming Convention

```
Control-1.16_[ArtifactType]_[YYYYMMDD].[ext]

Examples:
- Control-1.16_AzureRMSStatus_20260115.png
- Control-1.16_SensitivityLabel_20260115.png
- Control-1.16_LibraryIRM_20260115.png
- Control-1.16_DocumentTracking_20260115.csv
```

---

## Attestation Statement Template

```markdown
## Control 1.16 Attestation - Information Rights Management

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Azure Rights Management Service is activated
2. Sensitivity labels with IRM encryption are published
3. SharePoint libraries containing agent knowledge sources have IRM enabled:
   - [Site 1]: [X] libraries protected
   - [Site 2]: [X] libraries protected
4. Agent service accounts have appropriate permissions (Viewer)
5. Document tracking is enabled and monitored
6. IRM settings by zone:
   - Zone 1: [IRM optional/not required]
   - Zone 2: [IRM required, settings...]
   - Zone 3: [IRM mandatory, settings...]

**Last Configuration Review:** [Date]
**Document Tracking Active:** [Yes/No]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 1.16](../../../controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
