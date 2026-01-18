# Troubleshooting: Control 1.15 - Encryption: Data in Transit and at Rest

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| SSL Labs shows TLS 1.0/1.1 | Legacy protocol enabled | Disable legacy TLS in admin settings |
| Customer Key activation failed | Key Vault permissions | Grant M365 service required permissions |
| DEP stuck in pending | Key access issue | Verify key wrap/unwrap permissions |
| Key rotation failed | Key not available | Check key vault access and key status |
| CMK not available | License or feature flag | Verify E5 license and feature enablement |

---

## Detailed Troubleshooting

### Issue: SSL Labs Shows Legacy TLS Support

**Symptoms:** SSL Labs test shows TLS 1.0 or 1.1 enabled

**Diagnostic Steps:**

1. Verify organization-wide TLS settings:
   ```
   Microsoft 365 Admin > Settings > Org settings > Security & privacy
   ```

2. Check for legacy client requirements
3. Review any custom configurations

**Resolution:**

- Disable TLS 1.0/1.1 in organization settings
- Communicate to users about legacy client impacts
- Update legacy clients before enforcement
- Re-test with SSL Labs after 24 hours

---

### Issue: Customer Key Activation Failed

**Symptoms:** DEP creation fails or stays in error state

**Diagnostic Steps:**

1. Verify Key Vault permissions:
   - M365 DataAtRestEncryption app must have permissions
   - Required: Get, Wrap Key, Unwrap Key

2. Check Key Vault network access:
   - Firewall may be blocking M365 services
   - Public access or service endpoints required

3. Verify key is enabled and not expired

**Resolution:**

- Add M365 DataAtRestEncryption service principal to Key Vault access policies
- Grant Wrap Key and Unwrap Key permissions
- Allow trusted Microsoft services if using firewall
- Enable key if disabled

---

### Issue: DEP Stuck in Pending State

**Symptoms:** Data Encryption Policy shows "PendingActivation" indefinitely

**Diagnostic Steps:**

1. Check both Key Vaults are accessible
2. Verify keys in both vaults are enabled
3. Review DEP configuration for errors

**Resolution:**

- Ensure both primary and secondary keys are accessible
- Wait up to 24 hours for initial activation
- Contact Microsoft Support if pending > 48 hours
- Recreate DEP if configuration error

---

### Issue: Key Rotation Failed

**Symptoms:** Key rotation process fails or doesn't complete

**Diagnostic Steps:**

1. Verify new key is created in Key Vault
2. Check access to new key
3. Review rotation process for errors

**Resolution:**

- Create new key version (not new key)
- Verify permissions on new key version
- Follow Microsoft key rotation procedure
- Test key access before rotation

---

### Issue: Power Platform CMK Not Available

**Symptoms:** CMK option not visible in environment settings

**Diagnostic Steps:**

1. Verify license includes CMK feature:
   - Requires Premium or specific add-on

2. Check environment type:
   - Must be Managed Environment
   - Production environments only

3. Verify regional availability

**Resolution:**

- Upgrade to required license tier
- Convert to Managed Environment
- Check Microsoft documentation for regional availability
- Contact Microsoft Support for feature enablement

---

## How to Confirm Configuration is Active

### TLS Verification

1. Run SSL Labs test on tenant domain
2. Verify Grade A or better
3. Confirm no TLS 1.0/1.1 in results

### Customer Key Verification

1. Run: `Get-DataEncryptionPolicy | Select Name, State`
2. Verify State = "Active"
3. Check Key Vault diagnostic logs for access events

### Power Platform CMK Verification

1. Navigate to PPAC > Environment > Settings > Encryption
2. Confirm "Customer-managed key" displayed
3. Check linked Key Vault is accessible

---

## Escalation Path

If issues persist after troubleshooting:

1. **Security Operations** - Key Vault and access issues
2. **Microsoft 365 Admin** - Customer Key configuration
3. **Power Platform Admin** - Environment CMK issues
4. **Microsoft Support** - Platform-level issues

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Customer Key requires E5 | Not available on lower licenses | Use Microsoft-managed encryption |
| DEP activation delay | Up to 24 hours | Plan ahead for new deployments |
| CMK not available all regions | Regional limitations | Check documentation for availability |
| Key rotation requires planning | Service interruption risk | Follow documented procedure |
| HSM keys require Premium vault | Additional cost | Use Standard for non-regulated |

---

[Back to Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
