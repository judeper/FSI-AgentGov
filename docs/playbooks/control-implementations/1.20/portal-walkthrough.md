# Portal Walkthrough: Control 1.20 - Network Isolation and Private Connectivity

**Last Updated:** January 2026
**Portal:** Power Platform Admin Center, Azure Portal
**Estimated Time:** 6-8 hours for VNet setup

## Prerequisites

- [ ] Power Platform Admin role
- [ ] Azure Network Contributor role
- [ ] Managed Environment enabled
- [ ] Azure subscription for VNet resources

---

## Step-by-Step Configuration

### Step 1: Configure IP Firewall

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Select environment > **Settings** > **Security**
3. Enable **IP firewall**
4. Add approved IP ranges:
   - Corporate network CIDR (e.g., `10.0.0.0/8`)
   - VPN egress IPs
5. Set mode: Audit first, then Enforce

### Step 2: Enable VNet Support (Zone 3)

1. In Azure Portal, create VNet:
   - Name: `vnet-powerplatform-prod`
   - Address space: `10.100.0.0/16`
2. Create delegated subnet:
   - Name: `snet-powerplatform`
   - Delegation: `Microsoft.PowerPlatform/enterprisePolicies`
3. In PPAC, enable VNet support for environment
4. Select the delegated subnet

### Step 3: Configure Private Endpoints for Key Vault

1. In Azure Portal, navigate to Key Vault
2. Go to **Networking** > **Private endpoint connections**
3. Add private endpoint:
   - VNet: powerplatform VNet
   - Subnet: Private endpoint subnet
4. Create private DNS zone and link to VNet

### Step 4: Configure Private Link for Application Insights

1. Create Azure Monitor Private Link Scope (AMPLS)
2. Add Application Insights resources
3. Create private endpoint for AMPLS
4. Configure private DNS zones

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **IP Firewall** | Optional | Required | Required |
| **VNet Support** | Not required | Recommended | Mandatory |
| **Private Endpoints** | Not required | Sensitive data | All connections |
| **Network Logging** | Basic | Standard | Full flow logging |

---

## Validation

After completing these steps, verify:

- [ ] IP Firewall blocks non-allowlisted IPs
- [ ] Agent reaches resources via VNet path
- [ ] Private DNS resolves to private IPs
- [ ] Key Vault access uses private endpoint

---

[Back to Control 1.20](../../../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
