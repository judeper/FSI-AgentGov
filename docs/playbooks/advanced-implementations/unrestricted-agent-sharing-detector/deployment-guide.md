# Unrestricted Agent Sharing Detector - Deployment Guide

**Status:** May 2026 - FSI-AgentGov v1.6.2
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
| Microsoft.PowerApps.Administration.PowerShell module | Latest | On-demand sharing audit (Invoke-SharingAudit) |

```powershell
# Verify PowerShell version
$PSVersionTable.PSVersion

# Install required modules
Install-Module -Name Az.Accounts -Scope CurrentUser -Force
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser -Force

# Install Python dependencies
pip install -r scripts/requirements.txt
```

### Required Repositories

| Repository | Purpose |
|------------|---------|
| **FSI-AgentGov** (this repo) | Documentation and deployment guide |
| **FSI-AgentGov-Solutions** (companion) | Python deployment scripts, PowerShell governance scripts, Power Automate flow definitions, canvas app package |

!!! warning "Companion Repository Required"
    The flow JSON files and canvas app package used in Phases 2–3 are located in the **FSI-AgentGov-Solutions** companion repository. Clone it alongside this repository before proceeding:

    ```bash
    git clone https://github.com/<your-org>/FSI-AgentGov-Solutions.git
    ```

### Prerequisite Deployments

The UASD Dataverse schema depends on the shared `fsi_acv_zone` global option set created by the CAA (Conditional Access Automation) schema. Deploy the CAA schema first if it has not already been provisioned in your environment:

```powershell
cd scripts
python create_dataverse_schema.py --dry-run `
    --environment-url "https://<your-org>.crm.dynamics.com" `
    --tenant-id "<your-tenant-id>" `
    --client-id "<your-app-client-id>" `
    --client-secret "<your-app-client-secret>"

# After verifying, deploy without --dry-run
python create_dataverse_schema.py `
    --environment-url "https://<your-org>.crm.dynamics.com" `
    --tenant-id "<your-tenant-id>" `
    --client-id "<your-app-client-id>" `
    --client-secret "<your-app-client-secret>"
```

---

## Phase 1: Infrastructure Deployment

### Step 1: Deploy Dataverse Schema

The schema deployment script creates five Dataverse tables with the `fsi_` publisher prefix.

!!! note "Working Directory"
    All Python scripts must be run from the `scripts/` directory so that the `caa_client` module can be found. Use `cd scripts` before running the commands below.

```powershell
cd scripts

# Option A: Use CLI arguments (recommended)
python create_uasd_dataverse_schema.py --dry-run `
    --environment-url "https://<your-org>.crm.dynamics.com" `
    --tenant-id "<your-tenant-id>" `
    --client-id "<your-app-client-id>" `
    --client-secret "<your-app-client-secret>"

# Option B: Use environment variables (PowerShell)
$env:CAA_ENVIRONMENT_URL = "https://<your-org>.crm.dynamics.com"
$env:CAA_CLIENT_ID = "<your-app-client-id>"
$env:CAA_CLIENT_SECRET = "<your-app-client-secret>"
$env:CAA_TENANT_ID = "<your-tenant-id>"

# Deploy schema (dry-run first)
python create_uasd_dataverse_schema.py --dry-run

# Deploy schema (production)
python create_uasd_dataverse_schema.py
```

This creates the following tables:

| Table | Purpose |
|-------|---------|
| `fsi_AgentSharingSetting` | Per-agent sharing configuration snapshots |
| `fsi_SharingViolation` | Detected sharing policy violations |
| `fsi_SharingException` | Approved exception records with expiration |
| `fsi_ApprovedSecurityGroup` | Approved security groups for sharing validation |
| `fsi_SharingPolicy` | Policy configuration per zone |

### Step 2: Deploy Environment Variables

```powershell
# Deploy environment variables for flow configuration
# If you used Option A (CLI args) in Step 1, pass the same arguments again.
# If you used Option B (env vars), they are already set in your session.
python create_uasd_environment_variables.py `
    --environment-url "https://<your-org>.crm.dynamics.com" `
    --tenant-id "<your-tenant-id>" `
    --client-id "<your-app-client-id>" `
    --client-secret "<your-app-client-secret>"
```

Key environment variables created:

| Variable | Description |
|----------|-------------|
| `fsi_UASD_ScanFrequencyHours` | Detection scan interval (default: 24) |
| `fsi_UASD_AutoRemediatePublicLink` | Auto-remediate public links (default: false) |
| `fsi_UASD_MaxIndividualShares` | Threshold for excessive individual sharing (default: 5) |
| `fsi_UASD_HomeTenantId` | Home tenant GUID for cross-tenant detection |
| `fsi_UASD_DefaultExceptionDays` | Default exception duration in days (default: 90) |
| `fsi_UASD_SecurityApproverEmail` | Security team approver email for dual-approval workflow |
| `fsi_UASD_DataOwnerApproverEmail` | Data owner approver email for dual-approval workflow |
| `fsi_UASD_RemediationDryRun` | Dry-run mode — prevents remediation changes (default: true) |
| `fsi_UASD_TeamsGroupId` | Teams group/team ID for violation alert notifications |
| `fsi_UASD_TeamsChannelId` | Teams channel ID for violation alert notifications |
| `fsi_UASD_DataverseUrl` | Dataverse environment URL |

!!! info "Variables Requiring Manual Configuration"
    The deployment script creates all 11 variables with default or empty values. Several must be configured manually before the flows will function correctly: `fsi_UASD_DataverseUrl` (configured in Phase 1, Step 4), `fsi_UASD_SecurityApproverEmail`, `fsi_UASD_DataOwnerApproverEmail`, `fsi_UASD_HomeTenantId`, `fsi_UASD_TeamsGroupId`, and `fsi_UASD_TeamsChannelId` (covered in Phase 3, Steps 4–6).

### Step 3: Deploy Connection References

```powershell
# Deploy connection references
# Pass the same authentication arguments (or use env vars set in Step 1)
python create_uasd_connection_references.py `
    --environment-url "https://<your-org>.crm.dynamics.com" `
    --tenant-id "<your-tenant-id>" `
    --client-id "<your-app-client-id>" `
    --client-secret "<your-app-client-secret>"
```

### Step 4: Configure Dataverse URL Variable

Set the `fsi_UASD_DataverseUrl` environment variable so the detection flow can locate your Dataverse environment:

1. Navigate to [Power Apps](https://make.powerapps.com)
2. Go to **Solutions** > **UASD** > **Environment variables**
3. Edit `fsi_UASD_DataverseUrl`
4. Set the value to your environment URL (e.g., `https://<your-org>.crm.dynamics.com`)

### Step 5: Verify Infrastructure

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

!!! note "Flow Definition Source"
    The flow JSON files are located in the **FSI-AgentGov-Solutions** companion repository under `unrestricted-agent-sharing-detector/src/`. The `-FlowDefinitionPath` values below assume you are running from the FSI-AgentGov-Solutions repo root. If you cloned both repositories side-by-side, adjust the path accordingly.

```powershell
.\scripts\governance\Deploy-DetectionFlow.ps1 `
    -EnvironmentId "<your-environment-guid>" `
    -DataverseUrl "https://<your-org>.crm.dynamics.com" `
    -FlowDefinitionPath "unrestricted-agent-sharing-detector\src\uasd-detector-scan-agents.json" `
    -WhatIf

# After verifying, run without -WhatIf
.\scripts\governance\Deploy-DetectionFlow.ps1 `
    -EnvironmentId "<your-environment-guid>" `
    -DataverseUrl "https://<your-org>.crm.dynamics.com" `
    -FlowDefinitionPath "unrestricted-agent-sharing-detector\src\uasd-detector-scan-agents.json"
```

### Step 2: Bind Connection References

After import, bind the connection references to active connections:

1. Navigate to [Power Automate](https://make.powerautomate.com)
2. Go to **Solutions** > **UASD**
3. Open each connection reference and click **Edit**
4. Select or create a connection for each reference:
   - **Dataverse** — use the service account with System Administrator role
   - **Microsoft Teams** — use the service account for alert notifications

!!! note "Connection References"
    The connection reference deployment (Phase 1, Step 3) creates three connection references (Dataverse, Teams, and Approvals). All three are used across the detection, remediation, and exception flows.

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

**Recommended zone-based scheduling model:**

| Zone | Recommended Frequency | Rationale |
|------|----------------------|-----------|
| Zone 3 (Enterprise Managed) | 4 hours | High-sensitivity agents require near-real-time violation detection |
| Zone 2 (Team Collaboration) | 8–12 hours | Moderate sensitivity with same-day detection |
| Zone 1 (Personal Productivity) | 24 hours (daily) | Lower sensitivity, daily scans sufficient |

!!! note "Per-Zone Frequency Limitation"
    The current implementation uses a single `fsi_UASD_ScanFrequencyHours` variable for all zones. Organizations needing per-zone scan frequencies should deploy separate detection flow instances per zone, each configured with a zone-scoped filter and its own recurrence interval.

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

The flow definition paths below assume you are running from the FSI-AgentGov-Solutions repo root. Both the remediation flow and exception approval workflow are deployed in a single script invocation.

```powershell
# Preview deployment (WhatIf)
.\scripts\governance\Deploy-RemediationFlow.ps1 `
    -EnvironmentId "<your-environment-guid>" `
    -DataverseUrl "https://<your-org>.crm.dynamics.com" `
    -RemediationFlowPath "unrestricted-agent-sharing-detector\src\uasd-remediation-apply-sharing-policy.json" `
    -ExceptionFlowPath "unrestricted-agent-sharing-detector\src\uasd-exception-approval-workflow.json" `
    -WhatIf

# Deploy (production)
.\scripts\governance\Deploy-RemediationFlow.ps1 `
    -EnvironmentId "<your-environment-guid>" `
    -DataverseUrl "https://<your-org>.crm.dynamics.com" `
    -RemediationFlowPath "unrestricted-agent-sharing-detector\src\uasd-remediation-apply-sharing-policy.json" `
    -ExceptionFlowPath "unrestricted-agent-sharing-detector\src\uasd-exception-approval-workflow.json"
```

### Step 2: Bind Remediation Connection References

After import, bind the connection references for the remediation and exception flows. These flows require an additional Approvals connector beyond the Dataverse and Teams connectors used by the detection flow:

1. Navigate to [Power Automate](https://make.powerautomate.com)
2. Go to **Solutions** > **UASD**
3. Open each connection reference and click **Edit**
4. Select or create a connection for each reference:
   - **Dataverse** (`fsi_cr_dataverse_sharingdetector`) — use the service account with System Administrator role
   - **Microsoft Teams** (`fsi_cr_teams_sharingdetector`) — use the service account for alert notifications
   - **Microsoft Approvals** (`fsi_cr_approvals_sharingdetector`) — use the service account for exception approval workflows

### Step 3: Configure Auto-Remediation

The `fsi_UASD_AutoRemediatePublicLink` environment variable controls whether public internet link violations are automatically remediated.

!!! warning "FSI Default: Auto-Remediation Disabled"
    For financial services organizations, auto-remediation is **disabled by default** (`false`). This is recommended to allow compliance review before remediation actions. Enable only after establishing a documented review process and obtaining compliance officer approval.

!!! info "Auto-Remediation Scope"
    Per the solution design, the default remediation mode is **approval-required for all zones**. Fully automatic remediation is allowed **only** for `PUBLIC_INTERNET_LINK` violations when `fsi_UASD_AutoRemediatePublicLink` is explicitly set to `true`. All other violation types (`ORG_WIDE_SHARING`, `UNAPPROVED_GROUP`, `EXCESSIVE_INDIVIDUAL`, `CROSS_TENANT_ACCESS`) always require approval regardless of this setting.

To enable auto-remediation (after compliance review):

1. Navigate to **Solutions** > **UASD** > **Environment variables**
2. Edit `fsi_UASD_AutoRemediatePublicLink`
3. Set to `true`

### Step 4: Configure Approver Emails

Set the approver email addresses for the dual-approval exception workflow:

1. Navigate to **Solutions** > **UASD** > **Environment variables**
2. Edit `fsi_UASD_SecurityApproverEmail` — enter the security team approver email address
3. Edit `fsi_UASD_DataOwnerApproverEmail` — enter the data owner approver email address

!!! warning "Required Before Enabling Exception Workflow"
    The exception approval workflow cannot function without configured approver emails. Both fields must be set before the workflow will process exception requests.

!!! note "Exception Governance Is Not Optional"
    Organizations that intentionally maintain broad-access agents must not silently tolerate those configurations. The solution requires such agents to be tracked through the exception workflow with documented approvals and time-bound expirations (`fsi_UASD_DefaultExceptionDays`). Unmanaged exceptions represent audit findings under FINRA 4511 and SEC 17a-4 recordkeeping requirements.

### Step 5: Configure Home Tenant ID

Set the home tenant GUID for cross-tenant access detection (Rule 5):

1. Navigate to **Solutions** > **UASD** > **Environment variables**
2. Edit `fsi_UASD_HomeTenantId` — enter your organization's Entra ID tenant GUID

!!! warning "Required for Cross-Tenant Detection"
    Without `fsi_UASD_HomeTenantId` configured, the CROSS_TENANT_ACCESS violation rule (Critical severity) cannot evaluate agent sharing. The variable is created with an empty default value and must be set explicitly.

### Step 6: Configure Teams Alert Channel

Set the Teams group/team ID and channel ID for violation alert notifications:

1. Navigate to **Solutions** > **UASD** > **Environment variables**
2. Edit `fsi_UASD_TeamsGroupId` — enter the Microsoft Teams team/group ID where violation alerts should be posted
3. Edit `fsi_UASD_TeamsChannelId` — enter the Teams channel ID within that team where alerts should be posted

!!! tip "Finding Your Teams Group ID"
    In Microsoft Teams, right-click the team name > **Get link to team**. The group ID is the GUID in the link URL. Alternatively, use the Microsoft Graph Explorer or Entra admin center to find the group ID.

### Step 7: Configure Dry-Run Mode

The `fsi_UASD_RemediationDryRun` environment variable controls whether remediation actions are applied to agents. Dry-run mode defaults to `true` for safe initial deployment.

**Recommended deployment sequence:**

1. Deploy with `fsi_UASD_RemediationDryRun` = `true` (default)
2. Run the detection flow and verify violations are identified correctly
3. Review dry-run notifications in Teams — confirm the remediation actions that would have been applied
4. After validation, set `fsi_UASD_RemediationDryRun` to `false` to enable production remediation

!!! tip "Safe Rollout"
    Keep dry-run mode enabled for at least one full scan cycle (24 hours) before enabling production remediation. This allows the governance team to review the scope of changes before they take effect.

### Step 8: Configure Break-Glass Exclusions

Critical agents that must never be automatically remediated can be excluded using the `fsi_break_glass_exclude` tag:

1. Navigate to **Power Apps** > **Dataverse** > **Tables** > **fsi_AgentSharingSetting**
2. Locate the agent record to exclude
3. Set `fsi_break_glass_exclude` to `true`

Break-glass agents are still detected and violations are recorded, but remediation is skipped. The violation remains open for manual review by the governance team.

!!! note "Audit Trail"
    Break-glass exclusions are logged in the violation description field and generate a Teams notification. This supports audit trail requirements for agents that deviate from standard remediation policy.

### Step 9: Import Approved Security Groups

Load pre-approved security groups for the UNAPPROVED_GROUP violation rule:

```powershell
.\scripts\governance\Import-ApprovedSecurityGroups.ps1 `
    -DataverseUrl "https://<your-org>.crm.dynamics.com" `
    -InputPath .\config\approved-groups.csv
```

The CSV file requires two columns: `GroupId` and `DisplayName`. Optional columns: `Zone` (defaults to the `-DefaultZone` parameter value, which defaults to `All`) and `IsActive` (defaults to `true`). The script auto-populates `fsi_added_by` from the current user identity.

!!! tip "JSON Format Supported"
    The script auto-detects the input format from the file extension. JSON files (`.json`) containing an array of objects with `GroupId` and `DisplayName` properties are also accepted.

Example CSV format:

```csv
GroupId,DisplayName,Zone,IsActive
00000000-0000-0000-0000-000000000001,Finance Team,Zone3,true
00000000-0000-0000-0000-000000000002,Compliance Officers,Zone2,true
00000000-0000-0000-0000-000000000003,Executive Assistants,Zone2,true
```

### Step 10: Configure Sharing Policy Thresholds

The `fsi_SharingPolicy` table stores zone-specific policy definitions including the `MaxIndividualSharesPerAgent` threshold used by the `EXCESSIVE_INDIVIDUAL` detection rule. Populate this table with organization-specific thresholds per zone:

1. Navigate to **Power Apps** > **Dataverse** > **Tables** > **fsi_SharingPolicy**
2. Create a record for each governance zone with appropriate thresholds:

| Zone | Recommended `MaxIndividualSharesPerAgent` | Rationale |
|------|-------------------------------------------|-----------|
| Zone 1 (Personal Productivity) | 10 | Lower sensitivity, broader personal use |
| Zone 2 (Team Collaboration) | 25 | Team-scoped sharing with moderate controls |
| Zone 3 (Enterprise Managed) | 5 | Strictest controls for enterprise-critical agents |

!!! warning "Required for Excessive Sharing Detection"
    Without populating the `fsi_SharingPolicy` table, the `EXCESSIVE_INDIVIDUAL` rule may not function as designed. The `fsi_UASD_MaxIndividualShares` environment variable provides a global default fallback, but the table enables zone-specific overrides that align with the three-zone governance model.

### Step 11: Import Exception Manager App

Import the canvas app solution package for managing exceptions:

1. Navigate to [Power Apps](https://make.powerapps.com)
2. Go to **Solutions** > **Import solution**
3. Select the UASD exception manager solution package (`.zip` file) from the FSI-AgentGov-Solutions companion repository under `unrestricted-agent-sharing-detector/src/`
4. Complete the import wizard and bind connection references
5. Share the app with compliance officers who will manage exceptions

---

## Phase 4: Operational Validation

### Step 1: Run Initial Sharing Audit

Execute a full sharing audit to establish the baseline. This initial report serves as the first proof point that identity permissions, BAP API calls, and Dataverse connectivity are working correctly — a successfully populated report confirms the detector can enumerate agents and interpret sharing state as designed.

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
| 2 | Environment variables created | 11 variables under UASD solution | [ ] |
| 3 | Connection references created | Dataverse and Teams connection references listed | [ ] |
| 4 | Detection flow imported | Flow visible in Power Automate solutions | [ ] |
| 5 | Detection flow connections bound | All connection references linked to active connections | [ ] |
| 6 | Scan schedule configured | `fsi_UASD_ScanFrequencyHours` set to desired interval | [ ] |
| 7 | On-demand audit completes | `Invoke-SharingAudit.ps1` returns results without errors | [ ] |
| 8 | Remediation flow imported | Remediation flow visible in Power Automate solutions | [ ] |
| 9 | Exception approval flow imported | Exception workflow visible and connections bound | [ ] |
| 10 | Auto-remediation configured | `fsi_UASD_AutoRemediatePublicLink` set appropriately (default: false) | [ ] |
| 11 | Approved security groups loaded | Groups visible in `fsi_ApprovedSecurityGroup` table | [ ] |
| 12 | Exception Manager app imported | Canvas app accessible and shared with compliance team | [ ] |
| 13 | Violation report exports | `Export-ViolationReport.ps1` produces CSV/JSON output | [ ] |
| 14 | Evidence hash computed | `-IncludeEvidence` flag produces SHA-256 hash | [ ] |
| 15 | Teams alerts delivered | Violation alerts appear in configured Teams channel | [ ] |
| 16 | Teams group ID configured | `fsi_UASD_TeamsGroupId` set to the target team/group GUID | [ ] |
| 17 | Teams channel ID configured | `fsi_UASD_TeamsChannelId` set to the target channel ID | [ ] |
| 18 | Approver emails configured | `fsi_UASD_SecurityApproverEmail` and `fsi_UASD_DataOwnerApproverEmail` set | [ ] |
| 19 | Home tenant ID configured | `fsi_UASD_HomeTenantId` set to your tenant GUID (required for cross-tenant detection) | [ ] |
| 20 | Dry-run mode tested | Remediation flow produces dry-run notifications without applying changes | [ ] |
| 21 | Break-glass exclusions documented | Critical agents identified and tagged with `fsi_break_glass_exclude` | [ ] |

!!! note "Adaptive Card Template"
    The Teams alert notification uses the `adaptive-card-uasd-alert.json` template from the FSI-AgentGov-Solutions repository. This template is referenced by the detection flow and does not require a separate deployment step — it is embedded in the flow definition at import time.

---

## Troubleshooting

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| **Python `ModuleNotFoundError: No module named 'caa_client'`** | Script run from wrong directory | Run Python scripts from the `scripts/` directory: `cd scripts` then `python create_uasd_dataverse_schema.py ...`. Verify the `caa_client` package is installed via `pip install -r scripts/requirements.txt`. |
| **Schema deployment: `fsi_acv_zone not found`** | CAA schema not deployed | Run `python create_dataverse_schema.py` first to create shared option sets before the UASD schema |
| **Az.Accounts token failure** | Not signed in or expired session | Run `Connect-AzAccount` and verify the account has Dataverse access |
| **Dataverse 403 Forbidden** | Insufficient Dataverse permissions | Assign System Administrator or System Customizer security role to the service account |
| **Schema deployment fails** | Missing Python dependencies or incorrect environment URL | Run `pip install -r scripts/requirements.txt`; verify `UASD_ENVIRONMENT_URL` format includes `https://` |
| **Detection flow import error** | Solution version conflict or missing dependencies | Check that Dataverse schema was deployed first; verify no existing UASD solution with higher version |
| **Connection reference unbound** | Connection not created or expired | Create a new connection for each required connector; verify service account credentials |
| **No violations detected** | No agents with sharing violations in scope | Run `Invoke-SharingAudit.ps1` directly to verify BAP API connectivity and agent enumeration |
| **Remediation flow inactive** | Flow imported but not activated | Navigate to the flow in Power Automate and click **Turn on** |
| **Export returns empty results** | Filter parameters too restrictive or no violations in Dataverse | Try without filters first; verify violations exist in `fsi_SharingViolation` table |
| **Teams notification not received** | Channel ID incorrect or connector permissions missing | Verify `fsi_UASD_TeamsGroupId` and `fsi_UASD_TeamsChannelId` values; check Teams connector permissions |

### Deployment & Operational Issues

| Issue | Severity | Cause | Resolution |
|-------|----------|-------|------------|
| **Unedited approved groups (placeholder GUIDs)** | High | The example CSV/JSON contains placeholder GUIDs that don't match real Entra group IDs | Replace all placeholder `GroupId` values with actual Entra group object IDs from your tenant before importing. Placeholder IDs cause universal `UNAPPROVED_GROUP` violations. |
| **Automation identity running as personal account** | High | Detection or remediation flows running under a user account instead of a dedicated service principal | Configure flows to run under a dedicated Entra service principal or managed identity with minimum required scopes for BAP, Dataverse, and optionally Graph directory resolution. |
| **Approved group still flagged as violation** | Medium | The `fsi_ApprovedSecurityGroup` record uses an incorrect Entra object ID, is marked inactive, or has a zone mismatch | Verify the record in Dataverse: confirm `fsi_entraid_group_id` matches the exact Entra object ID, `fsi_is_active` is `true`, and `fsi_zone` matches the agent's governance zone. |
| **Exceptions stuck in Pending** | Medium | Approver email addresses not configured or exception approval flow is inactive | Verify `fsi_UASD_SecurityApproverEmail` and `fsi_UASD_DataOwnerApproverEmail` are set to valid email addresses. Check that the exception approval flow is turned on in Power Automate. Ensure exception approvals create active, non-expired records so the detector can suppress violations until expiration. |
| **Policy threshold not configured** | Low | `fsi_SharingPolicy` table not seeded with zone-specific thresholds | Populate `fsi_SharingPolicy` with `MaxIndividualSharesPerAgent` values per zone. Without this configuration, the `EXCESSIVE_INDIVIDUAL` rule may use only the global `fsi_UASD_MaxIndividualShares` environment variable default. |
| **Remediation returns 403/Forbidden** | High | Execution identity lacks write permissions for BAP remediation APIs or DLP policy blocks the connector | Validate that the service principal has permissions to call BAP bot permissions endpoints. Check that DLP policies in the target environment allow the Power Platform connector used by the remediation flow. |

### Audit Evidence Production

The UASD solution maintains a complete audit trail in Dataverse for regulatory compliance evidence:

- **Violation records** (`fsi_SharingViolation`) — timestamped detection events with agent identity, violation type, severity, and sharing state snapshot
- **Remediation records** — before/after governance state with remediation timestamp and operator identity
- **Exception records** (`fsi_SharingException`) — dual-approval audit trail with business justification, expiration tracking, and approval timestamps

To export evidence for compliance review:

```powershell
# Export violations with SHA-256 integrity hash
.\scripts\governance\Export-ViolationReport.ps1 `
    -DataverseUrl "https://<your-org>.crm.dynamics.com" `
    -OutputFormat JSON `
    -OutputPath .\evidence\violations-evidence.json `
    -IncludeEvidence `
    -IncludeExceptions
```

Dataverse records support evidence requirements for FINRA 4511 (books and records), GLBA 501(b) (safeguards through least privilege), and SOX 302/404 (internal controls and access governance). Organizations should validate that exported evidence meets their specific compliance program requirements.

!!! tip "Alternative Environment Variable for Remediation Script"
    The `remediate_agent_sharing.py` script accepts `DATAVERSE_ORG_URL` as an alternative to `CAA_ENVIRONMENT_URL` for specifying the Dataverse endpoint. If using environment variables for authentication, either variable name is accepted.

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
2. **Transition from dry-run to production** — After validating dry-run results for at least one scan cycle, set `fsi_UASD_RemediationDryRun` to `false` to enable production remediation
3. **Configure alert thresholds** — Adjust `fsi_UASD_MaxIndividualShares` based on organizational policy
4. **Document exception process** — Create an internal SOP for the exception approval workflow
5. **Plan periodic audits** — Run `Invoke-SharingAudit.ps1` quarterly for independent validation outside the automated flow
6. **Review auto-remediation policy** — After 30 days of operation, evaluate whether to enable auto-remediation for specific violation types

!!! note "Ongoing Operations"
    Review the [Configuration Hardening Baseline](../configuration-hardening-baseline/index.md) for additional governance checks that complement UASD detection capabilities.

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
