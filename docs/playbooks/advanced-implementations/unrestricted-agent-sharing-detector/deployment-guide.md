# Unrestricted Agent Sharing Detector - Deployment Guide

**Status:** February 2026 - FSI-AgentGov v1.2.43
**Related Controls:** 1.1 (Restrict Agent Publishing by Authorization), 3.8 (Copilot Hub & Governance Dashboard)

---

## Overview

The Unrestricted Agent Sharing Detector (UASD) is a governance solution that scans Copilot Studio agents for sharing configurations that violate organizational policy. It detects five violation types — organization-wide sharing, public internet links, unapproved security groups, excessive individual shares, and cross-tenant access — and supports automated remediation with exception management workflows.

This guide walks through end-to-end deployment of the UASD solution, from Dataverse schema provisioning through operational validation.

**Estimated Time:** 2-3 hours (excluding Dataverse provisioning wait times)

**What you get when done:**

- Automated detection of agent sharing violations across all Power Platform environments
- Configurable remediation flows with auto-remediation options for critical violations
- Exception management application for approved deviations with audit trail
- Compliance reporting with SHA-256 evidence hashing for regulatory audit packages

!!! warning "Implementation Caveat"
    This solution supports compliance with FINRA 4511 and SEC 17a-4 recordkeeping requirements but does not by itself satisfy all regulatory obligations. Organizations should validate the deployment against their specific compliance program requirements.

---

## Prerequisites

### Required Licenses

| License | Purpose |
|---------|---------|
| Power Platform environment with Dataverse | Data storage for violations, exceptions, and policies |
| Power Automate Premium | Cloud flows for detection and remediation |
| Copilot Studio | Agent governance scope |
| Azure subscription | Az.Accounts authentication for PowerShell scripts |

### Required Roles

| Role | Purpose |
|------|---------|
| Power Platform Admin | Environment and flow management |
| Dataverse System Administrator | Table creation and security role assignment |
| Microsoft Entra ID Global Reader (or equivalent) | Az.Accounts sign-in for Dataverse API access |

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.9+ | Schema and configuration deployment scripts |
| PowerShell | 7.0+ | Governance scripts (audit, export, import) |
| Az.Accounts module | Latest | Dataverse OAuth authentication |
| Microsoft.PowerApps.Administration.PowerShell | 2.0.0+ | On-demand sharing audit |

```powershell
# Verify PowerShell version
$PSVersionTable.PSVersion

# Install required modules
Install-Module -Name Az.Accounts -Scope CurrentUser -Force
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser -Force

# Install Python dependencies
pip install -r scripts/requirements.txt
```

---

## Phase 1: Infrastructure Deployment

### Step 1: Deploy Dataverse Schema

The schema deployment script creates five Dataverse tables with the `fsi_` publisher prefix.

```bash
# Set environment variables
export DATAVERSE_URL="https://<your-org>.crm.dynamics.com"
export DATAVERSE_CLIENT_ID="<your-app-client-id>"
export DATAVERSE_CLIENT_SECRET="<your-app-client-secret>"
export DATAVERSE_TENANT_ID="<your-tenant-id>"

# Deploy schema (dry-run first)
python scripts/create_uasd_dataverse_schema.py --dry-run

# Deploy schema (production)
python scripts/create_uasd_dataverse_schema.py
```

This creates the following tables:

| Table | Purpose |
|-------|---------|
| `fsi_SharingViolation` | Detected sharing policy violations |
| `fsi_SharingException` | Approved exception records with expiration |
| `fsi_SharingPolicy` | Policy configuration per zone |
| `fsi_SharingAgentSetting` | Per-agent sharing configuration snapshots |
| `fsi_ApprovedSecurityGroup` | Approved security groups for sharing validation |

### Step 2: Deploy Environment Variables

```bash
# Deploy environment variables for flow configuration
python scripts/create_uasd_environment_variables.py
```

Key environment variables created:

| Variable | Description |
|----------|-------------|
| `fsi_UASD_ScanFrequencyHours` | Detection scan interval (default: 24) |
| `fsi_UASD_AutoRemediatePublicLink` | Auto-remediate public links (default: false) |
| `fsi_UASD_MaxIndividualShares` | Threshold for excessive individual sharing (default: 100) |
| `fsi_UASD_AlertTeamsChannelId` | Teams channel for violation alerts |

### Step 3: Deploy Connection References

```bash
# Deploy connection references
python scripts/create_uasd_connection_references.py
```

### Step 4: Verify Infrastructure

1. Navigate to [Power Apps](https://make.powerapps.com)
2. Select the target environment
3. Go to **Dataverse** > **Tables**
4. Verify all five tables appear with the `fsi_` prefix
5. Confirm environment variables are listed under **Solutions** > **UASD** > **Environment variables**
6. Confirm connection references are listed under **Solutions** > **UASD** > **Connection references**

!!! tip "Quick Verification"
    ```powershell
    # Verify Dataverse connectivity
    Connect-AzAccount
    $token = Get-AzAccessToken -ResourceUrl "https://<your-org>.crm.dynamics.com"
    # If this returns without error, authentication is configured correctly
    ```

---

## Phase 2: Detection Flow Deployment

### Step 1: Import Detection Flow

Deploy the detection flow using the governance script:

```powershell
.\scripts\governance\Deploy-DetectionFlow.ps1 `
    -DataverseUrl "https://<your-org>.crm.dynamics.com" `
    -SolutionPath "unrestricted-agent-sharing-detector/src/uasd-detector-scan-agents.json" `
    -WhatIf

# After verifying, run without -WhatIf
.\scripts\governance\Deploy-DetectionFlow.ps1 `
    -DataverseUrl "https://<your-org>.crm.dynamics.com" `
    -SolutionPath "unrestricted-agent-sharing-detector/src/uasd-detector-scan-agents.json"
```

### Step 2: Bind Connection References

After import, bind the connection references to active connections:

1. Navigate to [Power Automate](https://make.powerautomate.com)
2. Go to **Solutions** > **UASD**
3. Open each connection reference and click **Edit**
4. Select or create a connection for each reference:
   - **Dataverse** — use the service account with System Administrator role
   - **Microsoft Teams** — use the service account for alert notifications

!!! note "Service Account Best Practice"
    Use a dedicated service account for flow connections rather than personal accounts. This helps meet separation-of-duties requirements and avoids flow disruption when personnel changes occur.

### Step 3: Configure Scan Schedule

The detection flow runs on a configurable schedule controlled by the `fsi_UASD_ScanFrequencyHours` environment variable.

- **Default:** 24 hours (daily scan)
- **Recommended for FSI:** 24 hours for production, 4 hours during initial rollout

To adjust the schedule:

1. Navigate to **Solutions** > **UASD** > **Environment variables**
2. Edit `fsi_UASD_ScanFrequencyHours`
3. Set the desired interval in hours

### Step 4: Validate Detection Flow

Run an on-demand sharing audit to verify detection works before enabling the scheduled flow:

```powershell
# Run on-demand audit (does not write to Dataverse)
.\scripts\governance\Invoke-SharingAudit.ps1 `
    -OutputFormat JSON `
    -OutputPath .\evidence\initial-audit.json `
    -IncludeEvidence
```

Review the output for any sharing violations detected across environments. If violations are found, they confirm the detection logic is working correctly.

---

## Phase 3: Remediation & Exception Setup

### Step 1: Deploy Remediation Flows

```powershell
.\scripts\governance\Deploy-RemediationFlow.ps1 `
    -DataverseUrl "https://<your-org>.crm.dynamics.com" `
    -SolutionPath "unrestricted-agent-sharing-detector/src/uasd-remediation-apply-sharing-policy.json" `
    -WhatIf

# After verifying, run without -WhatIf
.\scripts\governance\Deploy-RemediationFlow.ps1 `
    -DataverseUrl "https://<your-org>.crm.dynamics.com" `
    -SolutionPath "unrestricted-agent-sharing-detector/src/uasd-remediation-apply-sharing-policy.json"
```

### Step 2: Import Exception Approval Flow

Import the exception approval workflow:

1. Navigate to [Power Automate](https://make.powerautomate.com)
2. Go to **Solutions** > **UASD**
3. Import `unrestricted-agent-sharing-detector/src/uasd-exception-approval-workflow.json` from FSI-AgentGov-Solutions
4. Bind connection references as in Phase 2, Step 2

### Step 3: Configure Auto-Remediation

The `fsi_UASD_AutoRemediatePublicLink` environment variable controls whether public internet link violations are automatically remediated.

!!! warning "FSI Default: Auto-Remediation Disabled"
    For financial services organizations, auto-remediation is **disabled by default** (`false`). This is recommended to allow compliance review before remediation actions. Enable only after establishing a documented review process and obtaining compliance officer approval.

To enable auto-remediation (after compliance review):

1. Navigate to **Solutions** > **UASD** > **Environment variables**
2. Edit `fsi_UASD_AutoRemediatePublicLink`
3. Set to `true`

### Step 4: Import Approved Security Groups

Load pre-approved security groups for the UNAPPROVED_GROUP violation rule:

```powershell
.\scripts\governance\Import-ApprovedSecurityGroups.ps1 `
    -DataverseUrl "https://<your-org>.crm.dynamics.com" `
    -InputPath .\config\approved-groups.csv
```

The CSV file should contain columns: `GroupId`, `GroupName`, `Zone`, `ApprovedBy`.

### Step 5: Import Exception Manager App

Import the model-driven app for managing exceptions:

1. Navigate to [Power Apps](https://make.powerapps.com)
2. Go to **Solutions** > **Import solution**
3. Select `unrestricted-agent-sharing-detector/src/uasd-exception-manager-app.json` from FSI-AgentGov-Solutions
4. Complete the import wizard and bind connection references
5. Share the app with compliance officers who will manage exceptions

---

## Phase 4: Operational Validation

### Step 1: Run Initial Sharing Audit

Execute a full sharing audit to establish the baseline:

```powershell
.\scripts\governance\Invoke-SharingAudit.ps1 `
    -HomeTenantId "<your-tenant-id>" `
    -OutputFormat JSON `
    -OutputPath .\evidence\baseline-audit.json `
    -IncludeEvidence
```

### Step 2: Verify End-to-End Flow

Validate the complete detection-to-reporting pipeline:

1. **Trigger:** Manually run the detection flow or wait for scheduled execution
2. **Detect:** Verify violation records appear in the `fsi_SharingViolation` table
3. **Alert:** Confirm Teams notification is delivered to the configured channel
4. **Review:** Open the Exception Manager app and verify violations are visible
5. **Remediate:** If auto-remediation is enabled, confirm the remediation flow processes a test violation
6. **Export:** Generate a compliance report (see Step 3)

### Step 3: Export Compliance Report

Generate the first violation report to validate export functionality:

```powershell
# Export all violations to CSV
.\scripts\governance\Export-ViolationReport.ps1 `
    -DataverseUrl "https://<your-org>.crm.dynamics.com" `
    -OutputPath .\evidence\violations-report.csv

# Export with evidence hash for audit packaging
.\scripts\governance\Export-ViolationReport.ps1 `
    -DataverseUrl "https://<your-org>.crm.dynamics.com" `
    -OutputFormat JSON `
    -OutputPath .\evidence\violations-evidence.json `
    -IncludeEvidence `
    -IncludeExceptions
```

---

## Validation Checklist

| # | Item | Expected Result | Verified |
|---|------|----------------|----------|
| 1 | Dataverse tables deployed | 5 tables with `fsi_` prefix visible in Power Apps | [ ] |
| 2 | Environment variables created | 4+ variables under UASD solution | [ ] |
| 3 | Connection references created | Dataverse and Teams connection references listed | [ ] |
| 4 | Detection flow imported | Flow visible in Power Automate solutions | [ ] |
| 5 | Detection flow connections bound | All connection references linked to active connections | [ ] |
| 6 | Scan schedule configured | `fsi_UASD_ScanFrequencyHours` set to desired interval | [ ] |
| 7 | On-demand audit completes | `Invoke-SharingAudit.ps1` returns results without errors | [ ] |
| 8 | Remediation flow imported | Remediation flow visible in Power Automate solutions | [ ] |
| 9 | Exception approval flow imported | Exception workflow visible and connections bound | [ ] |
| 10 | Auto-remediation configured | `fsi_UASD_AutoRemediatePublicLink` set appropriately (default: false) | [ ] |
| 11 | Approved security groups loaded | Groups visible in `fsi_ApprovedSecurityGroup` table | [ ] |
| 12 | Exception Manager app imported | Model-driven app accessible and shared with compliance team | [ ] |
| 13 | Violation report exports | `Export-ViolationReport.ps1` produces CSV/JSON output | [ ] |
| 14 | Evidence hash computed | `-IncludeEvidence` flag produces SHA-256 hash | [ ] |
| 15 | Teams alerts delivered | Violation alerts appear in configured Teams channel | [ ] |

---

## Troubleshooting

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| **Az.Accounts token failure** | Not signed in or expired session | Run `Connect-AzAccount` and verify the account has Dataverse access |
| **Dataverse 403 Forbidden** | Insufficient Dataverse permissions | Assign System Administrator or System Customizer security role to the service account |
| **Schema deployment fails** | Missing Python dependencies or incorrect environment URL | Run `pip install -r scripts/requirements.txt`; verify `DATAVERSE_URL` format includes `https://` |
| **Detection flow import error** | Solution version conflict or missing dependencies | Check that Dataverse schema was deployed first; verify no existing UASD solution with higher version |
| **Connection reference unbound** | Connection not created or expired | Create a new connection for each required connector; verify service account credentials |
| **No violations detected** | No agents with sharing violations in scope | Run `Invoke-SharingAudit.ps1` directly to verify BAP API connectivity and agent enumeration |
| **Remediation flow inactive** | Flow imported but not activated | Navigate to the flow in Power Automate and click **Turn on** |
| **Export returns empty results** | Filter parameters too restrictive or no violations in Dataverse | Try without filters first; verify violations exist in `fsi_SharingViolation` table |
| **Teams notification not received** | Channel ID incorrect or connector permissions missing | Verify `fsi_UASD_AlertTeamsChannelId` value; check Teams connector permissions |

### Diagnostic Steps

1. **Verify Dataverse access:** Run a simple OData query against the environment URL
2. **Check flow run history:** Power Automate > Solutions > UASD > select flow > Run history
3. **Inspect violation records:** Power Apps > Dataverse > Tables > `fsi_SharingViolation` > Data
4. **Review script output:** Run governance scripts with `-Verbose` flag for detailed logging
5. **Validate connections:** Power Automate > Connections > verify status is **Connected**

### Log Locations

| Log | Location |
|-----|----------|
| Power Automate flow run history | Power Automate portal > Solutions > UASD > Flow > Run history |
| Dataverse violation records | Power Apps > Dataverse > `fsi_SharingViolation` table |
| PowerShell script output | Console output or `-OutputPath` file |
| Evidence audit packages | `.\evidence\` directory (local) |

---

## Next Steps

After successful deployment:

1. **Establish monitoring cadence** — Schedule weekly review of violation reports with the compliance team
2. **Configure alert thresholds** — Adjust `fsi_UASD_MaxIndividualShares` based on organizational policy
3. **Document exception process** — Create an internal SOP for the exception approval workflow
4. **Plan periodic audits** — Run `Invoke-SharingAudit.ps1` quarterly for independent validation outside the automated flow
5. **Review auto-remediation policy** — After 30 days of operation, evaluate whether to enable auto-remediation for specific violation types

!!! note "Ongoing Operations"
    Review the [Configuration Hardening Baseline](../configuration-hardening-baseline/index.md) for additional governance checks that complement UASD detection capabilities.

---

*FSI Agent Governance Framework v1.2.43 - February 2026*
