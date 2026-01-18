# Verification & Testing: Control 1.15 - Encryption: Data in Transit and at Rest

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify TLS 1.2+ Enforcement

1. Navigate to [SSL Labs](https://www.ssllabs.com/ssltest/)
2. Enter tenant domain (e.g., tenant.sharepoint.com)
3. Review results:
   - Grade should be A or A+
   - TLS 1.0 and 1.1 should show "No"
   - TLS 1.2 or 1.3 should show "Yes"
4. **EXPECTED:** Grade A with TLS 1.2+ only

### Test 2: Verify Customer Key Status

1. Connect to Exchange Online PowerShell
2. Run: `Get-DataEncryptionPolicy | Format-List`
3. **EXPECTED:** DEP shows State = "PendingActivation" or "Active"

### Test 3: Verify Key Vault Configuration

1. Open Azure Portal > Key Vaults
2. Select Customer Key vault
3. Verify:
   - Soft delete: Enabled
   - Purge protection: Enabled
   - Keys exist with appropriate permissions
4. **EXPECTED:** Both protections enabled, keys present

### Test 4: Verify Power Platform CMK

1. Open Power Platform Admin Center
2. Navigate to Environment > Settings > Encryption
3. **EXPECTED:** Shows "Encryption key managed by customer"

### Test 5: Verify Key Rotation Schedule

1. Request key rotation documentation
2. Confirm schedule matches governance tier
3. Verify last rotation was within policy window
4. **EXPECTED:** Documented schedule with evidence of compliance

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.15-01 | SSL Labs test | Grade A, TLS 1.2+ only | |
| TC-1.15-02 | Customer Key DEP status | Active state | |
| TC-1.15-03 | Key Vault soft delete | Enabled | |
| TC-1.15-04 | Key Vault purge protection | Enabled | |
| TC-1.15-05 | Power Platform CMK | Customer-managed key shown | |
| TC-1.15-06 | Key rotation schedule | Within policy window | |
| TC-1.15-07 | Key Vault diagnostic logs | Flowing to SIEM | |

---

## Evidence Collection Checklist

### TLS Configuration

- [ ] Screenshot: SSL Labs test results
- [ ] Document: TLS configuration policy

### Customer Key

- [ ] Screenshot: DEP status in Purview
- [ ] Screenshot: Key Vault configuration (both vaults)
- [ ] Export: Key Vault diagnostic settings

### Key Management

- [ ] Document: Key rotation schedule
- [ ] Document: Last rotation date and evidence
- [ ] Screenshot: Key Vault access policies

### Power Platform

- [ ] Screenshot: Environment encryption settings
- [ ] Document: CMK configuration details

---

## Evidence Artifact Naming Convention

```
Control-1.15_[ArtifactType]_[YYYYMMDD].[ext]

Examples:
- Control-1.15_SSLLabsTest_20260115.png
- Control-1.15_DEPStatus_20260115.png
- Control-1.15_KeyVaultConfig_20260115.png
- Control-1.15_RotationSchedule_20260115.pdf
```

---

## Attestation Statement Template

```markdown
## Control 1.15 Attestation - Encryption

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. TLS 1.2+ is enforced for all agent communications
2. SSL Labs test confirms Grade A with no legacy TLS
3. Customer Key is configured (if applicable):
   - Primary Key Vault: [Name/Region]
   - Secondary Key Vault: [Name/Region]
   - DEP Status: [Active/Pending]
4. Key Vaults have soft delete and purge protection enabled
5. Power Platform CMK is enabled for production environments
6. Key rotation schedule is documented and followed:
   - Schedule: [Quarterly/Annual]
   - Last Rotation: [Date]
   - Next Rotation: [Date]

**Key Vault Diagnostic Logging:** [Enabled/Disabled]
**SIEM Integration:** [Yes/No]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
