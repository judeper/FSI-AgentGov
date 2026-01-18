# Verification & Testing: Control 1.20 - Network Isolation and Private Connectivity

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify IP Firewall Enforcement

1. Attempt access from non-allowlisted IP
2. **EXPECTED:** Access denied with firewall error

### Test 2: Verify VNet Connectivity

1. Check agent can reach private endpoint resources
2. **EXPECTED:** Resources accessible via private path

### Test 3: Verify Private DNS Resolution

1. Resolve private endpoint FQDN from within VNet
2. **EXPECTED:** Resolves to private IP (10.x.x.x)

### Test 4: Verify Key Vault Private Access

1. Check Key Vault access logs
2. **EXPECTED:** Access from private endpoint IP only

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.20-01 | IP Firewall blocks unauthorized | Access denied | |
| TC-1.20-02 | VNet connectivity works | Private path used | |
| TC-1.20-03 | Private DNS resolves | Private IP returned | |
| TC-1.20-04 | Key Vault private access | No public access | |

---

## Evidence Collection Checklist

- [ ] Screenshot: IP Firewall configuration
- [ ] Screenshot: VNet and subnet settings
- [ ] Screenshot: Private endpoint connections
- [ ] Document: Network architecture diagram

---

## Attestation Statement Template

```markdown
## Control 1.20 Attestation - Network Isolation

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. IP Firewall is configured with approved IP ranges
2. VNet support is enabled for Zone 3 environments
3. Private endpoints are configured for sensitive resources
4. Network flow logging is enabled

**IP Ranges Allowed:** [List]
**VNet Name:** [Name]
**Private Endpoints:** [Count]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 1.20](../../../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
