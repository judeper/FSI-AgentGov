# Conditional Access Automation - Deployment Guide

**Status:** February 2026 - FSI-AgentGov v1.2.47
**Related Controls:** 1.11 (Conditional Access & MFA), 1.23 (Step-Up Authentication), 1.18 (Application-Level RBAC)

---

## Overview

This guide provides end-to-end deployment instructions for the Conditional Access Automation (CAA) solution. The deployment is organized into five phases, from prerequisites through validation.

**Estimated Time:** 2-4 hours (excluding Dataverse provisioning wait times)

---

## Phase 1: Prerequisites & App Registration

### Step 1: Create Entra ID App Registration

1. Navigate to [Microsoft Entra Admin Center](https://entra.microsoft.com)
2. Go to **Identity** > **Applications** > **App registrations**
3. Click **New registration**
4. Configure:
   - **Name:** `FSI-CAA-Automation`
   - **Supported account types:** Accounts in this organizational directory only
   - **Redirect URI:** Leave blank (no interactive sign-in needed)
5. Click **Register**
6. Record the **Application (client) ID** and **Directory (tenant) ID**

### Step 2: Configure API Permissions

1. In the app registration, go to **API permissions**
2. Click **Add a permission** > **Microsoft Graph** > **Application permissions**
3. Add the following permissions:
   - `Policy.Read.All` — Read all CA policies
   - `Application.Read.All` — Read app registrations (for service principal validation)
4. Click **Grant admin consent** (requires Global Admin or Privileged Role Administrator)
5. Verify both permissions show **Granted** status

### Step 3: Generate Certificate

Create a self-signed certificate for Azure Automation authentication:

```powershell
# Generate self-signed certificate (valid 2 years)
$cert = New-SelfSignedCertificate `
    -Subject "CN=FSI-CAA-Automation" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyAlgorithm RSA `
    -KeyLength 2048 `
    -NotAfter (Get-Date).AddYears(2) `
    -KeyExportPolicy Exportable

# Export PFX (for Azure Automation upload)
$pfxPassword = ConvertTo-SecureString -String "YourSecurePassword" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath ".\FSI-CAA-Automation.pfx" -Password $pfxPassword

# Export CER (for app registration upload)
Export-Certificate -Cert $cert -FilePath ".\FSI-CAA-Automation.cer"

# Record thumbprint
Write-Output "Certificate Thumbprint: $($cert.Thumbprint)"
```

### Step 4: Upload Certificate to App Registration

1. In the app registration, go to **Certificates & secrets**
2. Click **Upload certificate**
3. Upload `FSI-CAA-Automation.cer`
4. Click **Add**
5. Verify the certificate appears with the correct thumbprint

### Step 5: Upload Certificate to Azure Automation

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Go to your Azure Automation account
3. Under **Shared Resources**, click **Certificates**
4. Click **Add a certificate**
5. Upload `FSI-CAA-Automation.pfx` with the password
6. Click **Create**

---

## Phase 2: Dataverse Schema Deployment

### Step 1: Prepare Environment

The CAA solution requires Dataverse tables for persisting compliance results and baselines.

```bash
# Navigate to the repository root
cd /path/to/FSI-AgentGov

# Install Python dependencies
pip install -r scripts/requirements.txt
```

### Step 2: Configure Environment Variables

```bash
# Set required environment variables
export CAA_TENANT_ID="<your-tenant-id>"
export CAA_ENVIRONMENT_URL="https://<your-org>.crm.dynamics.com"
export CAA_CLIENT_ID="<your-app-client-id>"
export CAA_CLIENT_SECRET="<your-app-client-secret>"
```

### Step 3: Deploy Schema

```bash
# Deploy Dataverse tables (dry-run first)
python scripts/caa_client.py --dry-run

# Deploy Dataverse tables (production)
python scripts/caa_client.py
```

This creates the following Dataverse tables:

| Table | Purpose |
|-------|---------|
| `fsi_conditionalaccess_result` | Stores daily compliance validation results per policy |
| `fsi_policy_baseline` | Stores baseline snapshots for drift comparison |

### Step 4: Verify Schema Deployment

1. Navigate to [Power Apps](https://make.powerapps.com)
2. Select the target environment
3. Go to **Dataverse** > **Tables**
4. Verify both tables appear with expected columns
5. Confirm table permissions allow the CAA service principal to create and read records

---

## Phase 3: Module Installation

### Step 1: Install Graph Modules in Azure Automation

1. Navigate to your Azure Automation account in [Azure Portal](https://portal.azure.com)
2. Under **Shared Resources**, click **Modules**
3. Click **Add a module** > **Browse gallery**
4. Install the following modules (in order, as dependencies require):
   - `Microsoft.Graph.Authentication` (v2.0.0+)
   - `Microsoft.Graph.Identity.SignIns` (v2.0.0+)
   - `Microsoft.Graph.Applications` (v2.0.0+)
5. Wait for each module to reach **Available** status before installing the next

### Step 2: Upload CAA Private Modules

Upload the CAA helper scripts as custom modules:

1. In Azure Automation, go to **Modules** > **Add a module**
2. Upload `scripts/private/CAAClient.psm1` — Dataverse persistence module
3. Upload `scripts/private/Compare-PolicyBaseline.ps1` — Baseline drift comparison
4. Upload `scripts/private/Get-PolicyBaseline.ps1` — Baseline snapshot capture
5. Upload `scripts/private/Connect-GraphSession.ps1` — Graph authentication helper
6. Upload `scripts/private/Get-ZoneClassification.ps1` — Zone classification helper
7. Upload `scripts/private/Test-ParameterValidation.ps1` — Parameter validation helper

!!! note "Module Packaging"
    For Azure Automation, package the `private/` folder contents into a `.zip` alongside the module manifest (`conditional-access-automation.psd1`). Upload as a single custom module for cleaner dependency management.

### Step 3: Verify Module Availability

```powershell
# In Azure Automation test pane, verify modules load
Get-Module -ListAvailable | Where-Object { $_.Name -match 'Graph|CAAClient' }
```

---

## Phase 4: Runbook Configuration

### Step 1: Import Runbook

1. In Azure Automation, go to **Process Automation** > **Runbooks**
2. Click **Create a runbook**
3. Configure:
   - **Name:** `Start-CAAValidationRunbook`
   - **Runbook type:** PowerShell
   - **Runtime version:** 7.2 (or 7.4)
   - **Description:** Daily CA policy compliance validation for FSI governance
4. Click **Create**
5. Paste the contents of `scripts/Start-CAAValidationRunbook.ps1` into the editor
6. Click **Save** then **Publish**

### Step 2: Create Configuration File

Create a CA configuration JSON file and upload to Azure Automation:

```json
{
  "tenantSettings": {
    "tenantId": "<your-tenant-id>",
    "tenantName": "Contoso Financial"
  },
  "groupMappings": {
    "zone1SecurityGroup": "<zone-1-group-id>",
    "zone2SecurityGroup": "<zone-2-group-id>",
    "zone3SecurityGroup": "<zone-3-group-id>"
  },
  "breakGlassAccounts": [
    "<break-glass-account-1-object-id>",
    "<break-glass-account-2-object-id>"
  ],
  "applicationIds": {
    "copilotStudio": "96088433-f3d2-4e31-8e48-a07e8740e08d",
    "powerAutomate": "7df0a125-d3be-4c96-aa54-591f83ff541c"
  }
}
```

Upload this file to an Azure Storage account or Azure Automation variable (encrypted).

### Step 3: Configure Runbook Parameters

The runbook requires the following parameters:

| Parameter | Value | Source |
|-----------|-------|--------|
| `TenantId` | Your Entra ID tenant GUID | App registration |
| `ClientId` | FSI-CAA-Automation app client ID | App registration |
| `CertificateThumbprint` | Certificate thumbprint | Phase 1, Step 3 |
| `ConfigPath` | Path to configuration JSON | Phase 4, Step 2 |
| `DataverseUrl` | Dataverse environment URL | Phase 2, Step 2 |

Optional parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `Zone` | All zones | Filter to specific zone (1, 2, or 3) |
| `Scope` | `Full` | `Full` for daily scans, `Targeted` for provisioning-triggered scans |

### Step 4: Create Daily Schedule

1. In Azure Automation, go to the runbook > **Schedules**
2. Click **Add a schedule** > **Create a new schedule**
3. Configure:
   - **Name:** `CAA-Daily-Validation`
   - **Description:** Daily CA policy compliance check
   - **Starts:** Select next day at 02:00 UTC
   - **Recurrence:** Recurring every 1 day
   - **Set expiration:** No
4. Click **Create**
5. Link the schedule to the runbook with the configured parameters

---

## Phase 5: Validation

### Step 1: Manual Test Run

1. In Azure Automation, go to the runbook
2. Click **Start**
3. Enter the required parameters
4. Click **OK**
5. Monitor the job output in the **Output** tab

**Expected Output:** JSON object with compliance results:

```json
{
  "TenantId": "<tenant-id>",
  "ScanTimestamp": "2026-02-11T02:00:00Z",
  "OverallStatus": "Passed",
  "AlertRequired": false,
  "TotalChecks": 24,
  "PassedChecks": 24,
  "FailedChecks": 0,
  "Results": [...]
}
```

### Step 2: Verify Dataverse Records

1. Navigate to [Power Apps](https://make.powerapps.com)
2. Select the target environment
3. Open the `fsi_conditionalaccess_result` table
4. Verify new rows were created with the scan timestamp
5. Confirm violation details are populated for any failed checks

### Step 3: Verify Teams Notification (If Configured)

If a Power Automate flow is configured for alerting:

1. Check the Teams channel for compliance notification
2. Verify the notification contains:
   - Scan timestamp
   - Overall status
   - Count of findings by severity
   - Links to detailed results in Dataverse

### Step 4: Document Deployment

Record in your governance system:

- Deployment date and deploying administrator
- App registration details (client ID, permissions)
- Certificate thumbprint and expiration date
- Schedule configuration
- First successful validation run timestamp

---

## Troubleshooting

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| **Authentication failure** | Certificate not uploaded or expired | Re-upload PFX to Azure Automation; verify thumbprint matches app registration |
| **Graph permission denied** | Admin consent not granted | Navigate to app registration > API permissions > Grant admin consent |
| **Module not found** | Graph modules not installed | Install `Microsoft.Graph.Identity.SignIns` and `Microsoft.Graph.Applications` in Azure Automation modules |
| **Dataverse connection failed** | Incorrect URL or permissions | Verify `CAA_ENVIRONMENT_URL` format; confirm app registration has Dataverse permissions |
| **Runbook timeout** | Large number of CA policies | Increase runbook timeout setting; consider zone-scoped runs |
| **No baseline for drift analysis** | First run has no baseline | Run `Get-PolicyBaseline.ps1` to capture initial baseline before enabling drift detection |

### Diagnostic Steps

1. **Check job output:** Azure Automation > Runbook > Jobs > select job > Output
2. **Check job errors:** Same path > Errors tab
3. **Verify Graph connectivity:** Run `Connect-MgGraph -TenantId $tid -ClientId $cid -CertificateThumbprint $thumb` manually
4. **Verify Dataverse connectivity:** Run `Test-Connection` method on CAAClient

### Log Locations

| Log | Location |
|-----|----------|
| Azure Automation job logs | Azure Portal > Automation Account > Jobs |
| Dataverse validation results | Power Apps > `fsi_conditionalaccess_result` table |
| Dataverse baseline history | Power Apps > `fsi_policy_baseline` table |

---

*FSI Agent Governance Framework v1.2.47 - February 2026*
