# Troubleshooting: Control 1.20 - Network Isolation and Private Connectivity

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Access blocked unexpectedly | IP not in allowlist | Add IP to firewall rules |
| VNet connectivity failing | Subnet not delegated | Configure delegation |
| Private DNS not resolving | DNS zone not linked | Link private DNS zone to VNet |
| Key Vault access denied | Network rules blocking | Add private endpoint exception |

---

## Detailed Troubleshooting

### Issue: IP Firewall Blocking Legitimate Access

**Symptoms:** Users cannot access environment from corporate network

**Resolution:**

1. Verify corporate IP ranges in firewall rules
2. Check for NAT/proxy IP changes
3. Test in audit mode first
4. Add missing IP ranges

---

### Issue: VNet Connectivity Not Working

**Symptoms:** Agent cannot reach private resources

**Resolution:**

1. Verify subnet delegation to Microsoft.PowerPlatform
2. Check VNet is linked in PPAC environment settings
3. Verify NSG rules allow required traffic
4. Check private endpoint is healthy

---

## Escalation Path

1. **Power Platform Admin** - IP Firewall and VNet settings
2. **Azure Network Admin** - VNet and private endpoint configuration
3. **Security Admin** - Network architecture approval
4. **Microsoft Support** - Platform issues

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| VNet requires Managed Environment | Not available on standard | Upgrade to Managed |
| Regional availability | Not all regions supported | Check documentation |
| IP Firewall 200 rule limit | Large organizations may hit limit | Use CIDR aggregation |

---

[Back to Control 1.20](../../../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
