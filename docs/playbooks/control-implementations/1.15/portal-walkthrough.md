# Portal Walkthrough: Control 1.15 — Encryption: Data in Transit and at Rest

**Last Updated:** May 2026
**Portals:** Microsoft Purview portal, Azure portal, Power Platform admin center (PPAC), Microsoft 365 admin center
**Estimated Time:** 6–10 hours initial setup (Customer Key activation alone takes 1–24 hours of Microsoft-side processing per DEP)

!!! danger "Customer Key and DKE actions can permanently destroy data"
    Several steps in this walkthrough — Customer Key revocation, deletion of an active Key Vault key, deletion of a DKE key — trigger **irreversible data-purge paths** by design. Run all initial setup against a non-production tenant first. Restrict revocation rights to a small named group with break-glass approval. See [Troubleshooting › Customer Key revocation safety](troubleshooting.md#customer-key-revocation-and-data-purge-safety).

---

## Prerequisites

- [ ] Microsoft 365 E5 (or Office 365 E5 + Customer Key add-on) for Customer Key and DKE
- [ ] Azure subscription in the same Microsoft Entra tenant as Microsoft 365
- [ ] Roles (least-privilege; canonical names per the role catalog):
    - **Entra Security Admin** — Customer Key activation, DKE label-encryption configuration
    - **Purview Info Protection Admin** — DEP and sensitivity-label authoring
    - **SharePoint Admin** — register SPO/OneDrive DEP
    - **Exchange Online Admin** — assign Exchange DEPs to mailboxes
    - **Power Platform Admin** — PPAC CMK on Managed Environments
    - Azure RBAC: **Key Vault Contributor** to provision vaults; **Key Vault Crypto Officer** to create keys
- [ ] Two Azure regions identified for paired Key Vaults (use Azure paired regions where possible)
- [ ] Approved naming convention and tagging for Key Vaults and keys
- [ ] CAB / change ticket for production activation

---

## Phase 1 — Verify Microsoft Defaults (All Zones)

These steps require no configuration — they verify the encryption baseline is intact.

### Step 1.1: Verify TLS posture against tenant endpoints

1. Open [Qualys SSL Labs](https://www.ssllabs.com/ssltest/).
2. Test each public tenant endpoint:
    - `<tenant>.sharepoint.com`
    - `<tenant>-my.sharepoint.com`
    - `outlook.office.com` (Microsoft-managed; informational)
    - Any custom domain bound to Exchange / SharePoint / a Microsoft Copilot Studio agent direct-line endpoint
3. **Expected:** Grade A or A+; TLS 1.2 and TLS 1.3 supported; TLS 1.0 / 1.1 / SSL 3.0 = No; no RC4, no 3DES, no export-grade ciphers; valid certificate chain ≥ 60 days from expiry.
4. Save the SSL Labs PDF/PNG result to your evidence store with the date.

### Step 1.2: Confirm Microsoft 365 service-encryption baseline

1. Open the [Microsoft Purview portal](https://purview.microsoft.com).
2. Navigate to **Settings** → **Customer Key**.
3. The intro panel confirms the workloads currently protected by Microsoft service encryption with Microsoft-managed keys (Exchange Online, SharePoint Online, OneDrive, Teams). Capture a screenshot for evidence.
4. Even with no Customer Key activated, **all** of these workloads are encrypted at rest by default — this is the Zone 1 baseline.

---

## Phase 2 — Microsoft Purview Customer Key (Zone 2 / Zone 3)

### Step 2.1: Provision the two Azure Key Vaults

1. Open the [Azure portal](https://portal.azure.com) → **Key vaults** → **Create**.
2. Primary vault:
    - Name: `kv-fsi-ck-eo-pri-<region>` (Customer Key, Exchange Online, primary; analogous naming for SPO)
    - Region: primary Azure region
    - Pricing tier: **Premium** (HSM-backed) for Zone 3; **Standard** acceptable for Zone 2
    - **Soft-delete retention period: 90 days** (90 is the Customer Key minimum)
    - **Enable purge protection: Yes** ← required for Customer Key; this setting cannot be disabled later
3. Repeat for the secondary vault in a paired region (e.g., East US ↔ West US): `kv-fsi-ck-eo-sec-<region>`.
4. For SharePoint/OneDrive Customer Key, create a **separate** pair of vaults — Microsoft requires DEP-per-workload separation for Exchange vs. SPO/OneDrive.

!!! warning "Purge protection is irreversible"
    Once enabled, purge protection cannot be turned off for the lifetime of the vault. This is intentional — Customer Key requires it so an attacker (or admin error) cannot bypass the soft-delete window.

### Step 2.2: Create the wrapping keys

1. Open each vault → **Keys** → **Generate/Import**.
2. Settings:
    - Name: `m365-ck-key`
    - Key type: **RSA-HSM** (Premium vault) or **RSA** (Standard vault)
    - Key size: **3072** (Microsoft minimum is 2048; 3072+ recommended for Zone 2/3)
    - Activation date / expiration date: leave unset (Customer Key manages versioning via rotation, not expiry)
3. After creation, click the key → **Current Version** → copy the full key URI (`https://<vault>.vault.azure.net/keys/m365-ck-key/<version>`). You will need this for the DEP cmdlets.

### Step 2.3: Grant the Microsoft 365 DEP service principal access

1. Open each vault → **Access policies** (or **Access control (IAM)** if using Azure RBAC).
2. **Access policy mode:**
    - **Add Access Policy** → choose the principal:
        - For Exchange Online vaults: **Office 365 Exchange Online**
        - For SharePoint/OneDrive vaults: **Office 365 SharePoint Online**
    - Permissions: **Get**, **Wrap Key**, **Unwrap Key** only (no other key, secret, or certificate permissions).
    - Save.
3. **Azure RBAC mode (recommended for Zone 3):**
    - Assign the workload service principal the **Key Vault Crypto Service Encryption User** role at the key scope (not subscription scope — least privilege).
4. Verify your own admin account has **only** the management permissions you need for activation; remove broad Crypto Officer / Administrator rights from human accounts after activation completes.

### Step 2.4: Activate Customer Key for Exchange Online

1. Connect via PowerShell (`Connect-ExchangeOnline`) — see [PowerShell setup](powershell-setup.md#2-exchange-online-customer-key-activation) for the full scripted flow with `-WhatIf` safety.
2. Create the multi-workload root DEP:
    ```powershell
    New-M365DataAtRestEncryptionPolicy `
        -Name "FSI-EO-Root-DEP" `
        -AzureKeyIDs @(
            "https://kv-fsi-ck-eo-pri-eastus.vault.azure.net/keys/m365-ck-key/<ver>",
            "https://kv-fsi-ck-eo-sec-westus.vault.azure.net/keys/m365-ck-key/<ver>"
        ) `
        -Description "Customer Key DEP for Exchange Online — agent-bearing mailboxes"
    ```
3. Assign to the tenant: `Set-M365DataAtRestEncryptionPolicyAssignment -DataEncryptionPolicy "FSI-EO-Root-DEP"`.
4. **Activation is asynchronous.** Microsoft validates both keys, wraps the workload root key, and transitions state from `PendingActivation` → `Active`. This typically completes within minutes to a few hours; in some tenants the multi-workload DEP can take up to 24 hours.

### Step 2.5: Activate Customer Key for SharePoint Online / OneDrive

1. From a Windows PowerShell 5.1 session with `Microsoft.Online.SharePoint.PowerShell`:
    ```powershell
    Connect-SPOService -Url "https://<tenant>-admin.sharepoint.com"
    Register-SPODataEncryptionPolicy `
        -PrimaryKeyVaultName "kv-fsi-ck-spo-pri-eastus" `
        -PrimaryKeyName "m365-ck-key" `
        -PrimaryKeyVersion "<version>" `
        -SecondaryKeyVaultName "kv-fsi-ck-spo-sec-westus" `
        -SecondaryKeyName "m365-ck-key" `
        -SecondaryKeyVersion "<version>"
    ```
2. SharePoint Customer Key registration is **tenant-wide** (it does not target individual sites — every SPO/OneDrive site comes under the same DEP).
3. Confirm with `Get-SPODataEncryptionPolicy`. Activation can take several hours; the cmdlet is one-shot — re-running it fails until the previous activation completes.

### Step 2.6: Verify activation in the Purview portal

1. Purview portal → **Settings** → **Customer Key**.
2. The Exchange Online and SharePoint cards should show:
    - State: **Active**
    - Both Primary and Secondary key URIs displayed
    - "Last validated" timestamp within the last 24 hours
3. Save a screenshot for evidence.

---

## Phase 3 — Double Key Encryption (Zone 3 only)

DKE is a **separate** technology from Customer Key. It encrypts files with a label such that **two** keys are required to decrypt: a Microsoft-held key **and** a key held by your customer-hosted DKE service. Microsoft cannot decrypt DKE-protected content. Use DKE for MNPI, M&A working files, deal-team material, and any holding that must be cryptographically isolated from Microsoft cloud services.

### Step 3.1: Deploy the DKE key service

1. The DKE key service is a customer-operated REST endpoint. Microsoft publishes a reference .NET implementation: <https://github.com/Azure-Samples/DoubleKeyEncryptionService>.
2. Deploy the service in your environment:
    - Azure App Service, AKS, or on-premises — your choice
    - Front it with a publicly trusted TLS certificate (the service URL must be reachable from any Office client that needs to apply or read the label)
    - Configure two test keys: e.g., `Confidential-MNPI`, `Confidential-DealRoom`
    - Restrict access via Microsoft Entra app registration with explicit user/group assignment
3. Operationalize: HA / DR pair (loss of the service = loss of access to all DKE-labelled data), backup the key material into your HSM, document recovery RTO.

!!! danger "Loss of the DKE key = permanent loss of all DKE-protected files"
    The customer DKE key never leaves your environment. If you lose the key (misconfigured backup, accidental delete, vendor exit), no recovery is possible. Treat the DKE key custody process with the same rigor as a root signing CA.

### Step 3.2: Create a DKE-enabled sensitivity label

1. Purview portal → **Information Protection** → **Labels** → **Create a label**.
2. Name it (e.g., `Highly Confidential / MNPI (DKE)`); set scope to **Files & emails**.
3. **Encryption:** Configure → **Configure encryption settings**.
4. Under **Configure encryption**, set encryption type to **Double Key Encryption** and supply your DKE service endpoint URL (for example, `https://dke.fsi-corp.example/<keyname>`; placeholder — replace with your tenant).
5. Configure user/group rights as for any sensitivity label (Co-author / Reviewer / etc.).
6. **Publish** the label via a label policy targeting the MNPI-handling user scope.

### Step 3.3: Validate DKE end to end

1. From a workstation that **can** reach the DKE service, open Word, apply the label, save the file. Re-open — it should open transparently.
2. From a workstation or service account that **cannot** reach the DKE service, attempt to open the same file. It must fail with "Access required from the customer key service" — this is the expected proof of cryptographic isolation.
3. Capture both results as evidence.

---

## Phase 4 — Power Platform Customer-Managed Key (Zone 2 / Zone 3)

### Step 4.1: Convert the target environment to a Managed Environment

1. PPAC → **Environments** → select the Dataverse environment hosting your Copilot Studio agents.
2. **Edit Managed Environment** → enable. Configure usage insights / weekly digest as your standard requires.

### Step 4.2: Provision a Key Vault for Power Platform CMK

1. Create a **separate** Key Vault dedicated to Power Platform — co-located in the **same Azure region** as the Dataverse environment.
2. Soft delete and purge protection: **Enabled** (same rule as Customer Key).
3. Generate an RSA 2048+ HSM key.

### Step 4.3: Register the encryption key in PPAC

1. PPAC → **Policies** → **Customer-managed keys** → **+ New key**.
2. Provide the Key Vault key URI; PPAC will display the Dataverse service principal that needs Wrap/Unwrap/Get on the key.
3. In the Azure portal, grant that service principal access to the key (access policy or RBAC `Key Vault Crypto Service Encryption User` role on the key scope).
4. Return to PPAC and complete the registration.

### Step 4.4: Apply the CMK to the environment

1. PPAC → **Environments** → select the Managed Environment → **Manage encryption key**.
2. Select the registered CMK → **Confirm**.
3. PPAC initiates the Dataverse re-encryption operation. **The environment may be unavailable for the duration; size and storage volume drive runtime.** Plan to do this in a maintenance window.
4. After completion, the environment detail page shows **Encryption key managed by customer** with the linked vault key URI.

---

## Phase 5 — Map Copilot Grounding Sources to DEP Coverage

Microsoft 365 Copilot does not have a separate "Copilot DEP". Copilot prompts and responses inherit the encryption posture of the underlying workload (Exchange mailbox / SPO site / OneDrive / Teams chat).

1. Build an inventory of every Copilot grounding source per agent:
    - SharePoint sites used as knowledge sources
    - Exchange mailboxes used by agent flows
    - OneDrive accounts that host agent files
    - Teams channels surfaced to Copilot
2. For each source, record the DEP that covers it (or note "Microsoft-managed key" for Zone 1).
3. Store the inventory next to your encryption attestation; refresh quarterly.

---

## Configuration by Governance Level

| Setting | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|---------|-------------------|---------------|---------------------|
| Transit | TLS 1.2+ (Microsoft default) | TLS 1.2+ verified for custom surfaces | TLS 1.3 preferred end-to-end; mTLS on integrations |
| At-rest baseline | Microsoft-managed keys (BitLocker + service encryption) | Same as Zone 1 | Same as Zone 1 |
| Customer Key | Not required | **Required** for EO + SPO/OneDrive | **Required** with Premium HSM-backed keys |
| Key Vault SKU | n/a | Standard (Premium for sensitive subsets) | **Premium**; Managed HSM for highest assurance |
| DKE | Not required | Optional | **Required** for MNPI / deal-team / privileged content |
| Power Platform CMK | Not required | Required on team-tier Managed Environments | Required on all Managed Environments |
| Key rotation cadence | Microsoft-managed | Annual, dual-control | Quarterly, dual-control + CISO + Records Officer |
| Diagnostic logging | Service defaults | Key Vault audit → SIEM | Key Vault audit → Sentinel with alerting |
| Revocation runbook | n/a | Documented | Documented **and rehearsed** in non-prod |

---

## Validation

After completing the relevant phases, verify:

- [ ] SSL Labs: Grade A/A+, TLS 1.2+ only, no weak ciphers
- [ ] Purview → Customer Key: state **Active** for all configured DEPs
- [ ] Azure Key Vault: soft delete **enabled**, purge protection **enabled**, access scoped to the correct service principal with `Get/WrapKey/UnwrapKey` only
- [ ] DKE label visible and applicable; DKE-protected file unreadable from a non-authorized client
- [ ] PPAC environment: "Encryption key managed by customer" displayed with linked vault key URI
- [ ] Encryption inventory maps every Copilot grounding source to a DEP or to Microsoft-managed-key baseline
- [ ] Key Vault diagnostic logs flowing to SIEM; recent events present

Cross-reference with [Verification & Testing](verification-testing.md) for the auditor-evidence checklist.

---

[Back to Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
