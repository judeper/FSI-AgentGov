# Portal Walkthrough: Control 1.15 - Encryption: Data in Transit and at Rest

**Last Updated:** January 2026
**Portal:** Microsoft 365 Admin Center, Azure Portal, Power Platform Admin Center
**Estimated Time:** 4-8 hours for Customer Key setup

## Prerequisites

- [ ] Entra Global Admin or Security Admin role
- [ ] Azure Key Vault Contributor access
- [ ] Power Platform Admin role
- [ ] Microsoft 365 E5 or equivalent license (for Customer Key)

---

## Step-by-Step Configuration

### Step 1: Verify TLS 1.2+ Enforcement

1. Open [Microsoft 365 Admin Center](https://admin.microsoft.com)
2. Navigate to **Settings** > **Org settings** > **Security & privacy**
3. Verify TLS 1.2 is enforced for all services
4. Test with [SSL Labs](https://www.ssllabs.com/ssltest/):
   - Enter your tenant domain
   - Verify Grade A or better
   - Confirm no TLS 1.0/1.1 support

### Step 2: Verify Microsoft Service Encryption

1. Navigate to [Microsoft Purview](https://compliance.microsoft.com)
2. Go to **Data classification** > **Content explorer**
3. Confirm encryption is active for:
   - Exchange Online
   - SharePoint Online
   - OneDrive for Business
   - Microsoft Teams

### Step 3: Configure Customer Key (Optional - Tier 2/3)

#### 3a: Create Azure Key Vaults

1. Open [Azure Portal](https://portal.azure.com)
2. Create first Key Vault:
   - Name: `kv-m365-cmk-primary`
   - Region: Primary region
   - SKU: Premium (HSM-backed for Tier 3)
   - Enable soft delete and purge protection

3. Create second Key Vault in different region:
   - Name: `kv-m365-cmk-secondary`
   - Region: Secondary region
   - Same settings as primary

#### 3b: Generate Keys

1. In each Key Vault, create key:
   - Name: `m365-customer-key`
   - Type: RSA-HSM (Premium) or RSA (Standard)
   - Size: 2048 or 4096 bits
   - Enable: Wrap/Unwrap permissions

#### 3c: Configure Customer Key in Microsoft 365

1. Open [Microsoft Purview](https://compliance.microsoft.com)
2. Navigate to **Information protection** > **Customer Key**
3. Follow the guided setup:
   - Connect primary Key Vault
   - Connect secondary Key Vault
   - Verify key access

### Step 4: Create Data Encryption Policy (DEP)

1. In Microsoft Purview > Customer Key:
2. Create new DEP:
   - Name: `DEP-AgentData`
   - Scope: SharePoint, Exchange (as needed)
   - Key Vault 1: Primary vault and key
   - Key Vault 2: Secondary vault and key

3. Assign DEP to locations:
   - SharePoint sites used as agent knowledge sources
   - Exchange mailboxes for agent communications

### Step 5: Configure Power Platform CMK

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Environments** > Select environment
3. Go to **Settings** > **Encryption**
4. Enable customer-managed key:
   - Select Azure Key Vault
   - Select encryption key
   - Confirm activation

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **Transit Encryption** | TLS 1.2 | TLS 1.2+ | TLS 1.3 + mTLS |
| **At-Rest Encryption** | Microsoft-managed | Customer Key (Standard) | Customer Key (HSM) |
| **Key Rotation** | Microsoft-managed | Annual | Quarterly |
| **Key Vault SKU** | N/A | Standard | Premium (HSM) |
| **Double Encryption** | No | No | Yes (for MNPI) |

---

## FSI Example Configuration

```yaml
Encryption Configuration: Investment Advisory Bot

Transit:
  Protocol: TLS 1.3
  Certificate: DigiCert EV
  mTLS: Enabled for Zone 3

At Rest:
  Provider: Customer Key
  Primary Vault: kv-fsi-cmk-eastus
  Secondary Vault: kv-fsi-cmk-westus
  Key Type: RSA-HSM 4096

Key Rotation:
  Schedule: Quarterly (January, April, July, October)
  Owner: Security Operations
  Approval: CISO

Data Encryption Policies:
  - DEP-CustomerData: SharePoint sites with customer documents
  - DEP-AgentLogs: Exchange audit mailbox
  - DEP-TradeRecords: Dataverse trade tables
```

---

## Validation

After completing these steps, verify:

- [ ] SSL Labs test shows Grade A with TLS 1.2+ only
- [ ] Customer Key shows "Active" status (if configured)
- [ ] DEP applied to agent data locations
- [ ] Power Platform environment shows CMK enabled
- [ ] Key rotation schedule documented

---

[Back to Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
