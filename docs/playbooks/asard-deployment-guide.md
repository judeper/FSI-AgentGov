# ASARD Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Agent Sharing Access Restriction Detector (ASARD) solution in a Power Platform tenant. ASARD helps organizations meet regulatory requirements related to agent access controls by detecting and remediating unauthorized agent sharing patterns.

**Scope:** This guide covers initial deployment, configuration, and verification. For ongoing operations, see [Exception Management](asard-exception-management.md). For issue resolution, see [Troubleshooting Guide](asard-troubleshooting-guide.md).

**Regulatory Context:** ASARD supports compliance with access control requirements in financial services regulations (GLBA, SOX, NYDFS 23 NYCRR 500) by providing technical controls that help identify and remediate unauthorized agent sharing patterns.

!!! warning "Implementation Caveat"
    ASARD is a technical control that supports regulatory compliance programs. It does not replace policy governance, security awareness training, or manual risk assessments. Organizations remain responsible for establishing and maintaining comprehensive access control policies.

## Prerequisites

Before deploying ASARD, ensure the following prerequisites are met:

### Microsoft Entra ID Requirements
- **Microsoft Entra ID app registration capability:** Ability to create and configure Microsoft Entra ID app registrations
- **API permissions:** Authority to grant admin consent for Microsoft Graph and BAP Admin API permissions
- **Security groups:** Access to Microsoft Entra ID security group management

### Power Platform Requirements
- **Power Platform admin role:** Global admin or Power Platform admin role required
- **Dataverse environment:** Production or dedicated governance environment with Dataverse database
- **Environment access:** Ability to query all environments in the tenant (for agent enumeration)

### Development Environment
- **Python 3.11 or later:** Verified with Python 3.11, 3.12, 3.13. Python 3.9 reached end-of-life on **2025-10-31** ([Status of Python versions](https://devguide.python.org/versions/), [endoflife.date/python](https://endoflife.date/python)) and is no longer supported for new deployments.
- **Python packages:** Install required dependencies:
  ```bash
  pip install msal requests azure-identity
  ```

### Access and Permissions
- **BAP Admin API access:** Required to enumerate agents and manage sharing settings
- **Microsoft Graph API access:** Required to resolve Microsoft Entra ID security groups
- **Teams webhook:** Microsoft Teams channel webhook URL for notifications (optional but recommended)

## Deployment Steps

### Step 1: Create Microsoft Entra ID App Registration

1. **Navigate to Azure Portal:**
   - Go to [Azure Portal](https://portal.azure.com) > Microsoft Entra ID > App registrations
   - Click **New registration**

2. **Configure app registration:**
   - **Name:** `ASARD-Service-Principal`
   - **Supported account types:** Single tenant (your organization only)
   - **Redirect URI:** Leave blank (not required for service principal)
   - Click **Register**

3. **Create client secret:**
   - In the app registration, go to **Certificates & secrets**
   - Click **New client secret**
   - **Description:** `ASARD Detection Service`
   - **Expires:** Select appropriate duration (recommend 12-24 months)
   - Click **Add**
   - **Copy the secret value immediately** (it will not be shown again)

4. **Configure API permissions:**
   - Go to **API permissions**
   - Click **Add a permission** > **APIs my organization uses**
   - Add a permission for **Power Platform API**. The minimum scopes for tenant-wide environment + governance posture enumeration are:
     - `EnvironmentManagement.Environments.Read` — list environments tenant-wide
     - `EnvironmentManagement.Groups.Read` — list environment groups (if used by your governance posture)
     - `AiFlows.Workflows.Read` — list AI flows / agent workflows
     - `CopilotGovernance.Features.Read` and `CopilotGovernance.Settings.Read` — read Copilot governance posture
     - `Analytics.AdvisorRecommendations.Read` — read advisor recommendations (closest published Analytics-tier permission; raw agent telemetry is not exposed as a PPAPI scope as of May 2026)
   - If the **Power Platform API** does not appear in the picker, first instantiate the **PPAPI resource service principal** in the tenant so the picker can find it:
     ```powershell
     # Microsoft.Graph PowerShell SDK; install once with:
     # Install-Module Microsoft.Graph -Scope CurrentUser -Repository PSGallery -Force
     Connect-MgGraph -Scopes "Application.ReadWrite.All"
     New-MgServicePrincipal -AppId 8578e004-a5c6-46e7-913e-12f58912df43 -DisplayName "Power Platform API"
     ```
     The legacy `New-AzureADServicePrincipal` cmdlet (AzureAD module) reached end-of-support **2024-03-30** and should not be used; the Microsoft Graph PowerShell SDK is Microsoft's supported replacement ([Azure AD / MSOnline deprecation](https://learn.microsoft.com/en-us/powershell/azure/active-directory/overview)).
   - For tenant-wide BAP-side enumeration via service-principal (S2S), additionally register the app as an admin management application:
     ```http
     PUT https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/adminApplications/{clientId}?api-version=2020-10-01
     ```

   !!! warning "PPAPI delegated-only design caveat"
       Microsoft Learn states verbatim: *"Power Platform API uses delegated permissions only at this time… For service principal identities, don't use application permissions. Instead, after you create your app registration, assign it an RBAC role to grant scoped permissions (such as Contributor or Reader)."* ([Authenticate to Power Platform — v2](https://learn.microsoft.com/en-us/power-platform/admin/programmability-authentication-v2))

       If ASARD detection runs as a **headless service principal** (the canonical pattern), the supported tenant-wide enumeration path is one of:
       (a) the **admin management application** registration via the `PUT api.bap.microsoft.com/.../adminApplications/{clientId}` call above (used for legacy BAP admin endpoints), or
       (b) a **Power Platform RBAC role assignment** (e.g., Power Platform Reader) on the app's service principal — see [Tutorial — assign RBAC role to a service principal](https://learn.microsoft.com/en-us/power-platform/admin/programmability-tutorial-rbac-role-assignment).

       The PPAPI delegated scopes listed above are appropriate when ASARD runs in **delegated user context** (e.g., interactive admin-initiated detection). Do not rely on PPAPI delegated scopes as the sole tenant-wide enumeration path for an unattended SPN workload.

   - Select **Delegated permissions** (PPAPI exposes Delegated only as of May 2026).
   - Click **Add a permission** again > **Microsoft Graph**
   - Add the following permissions:
     - `Group.Read.All` (to resolve security groups)
     - `GroupMember.Read.All` — required for nested-group / transitive membership queries via [`/groups/{id}/transitiveMembers`](https://learn.microsoft.com/en-us/graph/api/group-list-transitivemembers). Advanced query options on this endpoint (`$count`, `$search`, advanced `$filter`) also require the `ConsistencyLevel: eventual` request header — see [advanced query capabilities](https://learn.microsoft.com/en-us/graph/aad-advanced-queries).
   - Click **Grant admin consent** for your tenant.
   - References:
     - [Power Platform API permission reference](https://learn.microsoft.com/en-us/power-platform/admin/programmability-permission-reference)
     - [Authenticate to Power Platform — v2](https://learn.microsoft.com/en-us/power-platform/admin/programmability-authentication-v2)
     - [Authenticate to Power Platform with service principal](https://learn.microsoft.com/en-us/power-platform/admin/powerplatform-api-create-service-principal) (BAP admin endpoint registration)

5. **Record configuration values:**
   - **Application (client) ID:** Copy from Overview page
   - **Directory (tenant) ID:** Copy from Overview page
   - **Client secret:** Previously copied value
   - Store these values securely (e.g., Azure Key Vault, password manager)

### Step 2: Create Dataverse Schema

Run the schema creation script to create the required Dataverse tables for ASARD.

1. **Configure environment variables:**
   ```bash
   export AZURE_CLIENT_ID="<application-id>"
   export AZURE_CLIENT_SECRET="<client-secret>"
   export AZURE_TENANT_ID="<tenant-id>"
   export DATAVERSE_ENVIRONMENT_URL="https://<org>.crm.dynamics.com"
   ```

   !!! note "Geography-specific Dataverse host suffix"
       Set `DATAVERSE_ENVIRONMENT_URL` to the environment's actual URL retrieved from the Power Platform admin center or the [discovery service](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/discover-url-organization-web-api). The host suffix varies by region (for example `crm.dynamics.com`, `crm2.dynamics.com`, `crm3.dynamics.com`, `crm4.dynamics.com` — region-dependent).

2. **Run schema creation script:**
   ```bash
   cd scripts
   python create_asard_dataverse_schema.py
   ```

3. **Verify schema creation:**
   - Log in to [Power Apps](https://make.powerapps.com)
   - Navigate to your Dataverse environment > Tables
   - Verify the following tables exist:
     - `gov_asardsharingviolation` — Agent sharing violation records
     - `gov_asardsecuritygrouppolicy` — Approved security group policy
     - `gov_asardexception` — Exception records
     - `gov_asardremediationlog` — Remediation history

**Expected Output:**
```
Creating ASARD Dataverse schema...
[INFO] Creating gov_asardsharingviolation table...
[INFO] Creating gov_asardsecuritygrouppolicy table...
[INFO] Creating gov_asardexception table...
[INFO] Creating gov_asardremediationlog table...
[SUCCESS] Schema created successfully.
```

### Step 3: Populate Approved Security Group Policy

Configure which Microsoft Entra ID security groups are approved for agent sharing.

1. **Identify approved security groups:**
   - Work with your security team to identify Microsoft Entra ID security groups that are approved for agent sharing
   - For each group, obtain:
     - **Group Object ID:** From Microsoft Entra ID
     - **Group Display Name:** For reference
     - **Zone:** Environment zone this approval applies to (e.g., `production`, `development`, `sandbox`)

2. **Add policy records:**
   - Option A: Use Power Apps UI
     - Navigate to [Power Apps](https://make.powerapps.com) > Tables > `gov_asardsecuritygrouppolicy`
     - Click **New record**
     - Fill in: `groupobjectid`, `groupname`, `zone`, `isactive` (set to Yes)
     - Save

   - Option B: Use script (if bulk import needed)
     ```python
     # Example: Add approved group via API
     import requests

     dataverse_url = "https://<org>.crm.dynamics.com/api/data/v9.2"
     group_policy = {
         "gov_groupobjectid": "12345678-1234-1234-1234-123456789abc",
         "gov_groupname": "Finance-Agents-Prod",
         "gov_zone": "production",
         "gov_isactive": True
     }

     # Dataverse Web API required headers — see
     # https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/compose-http-requests-handle-errors#http-headers
     # Prefer: return=representation is needed only if you want the created record echoed back
     # in the response body (otherwise Dataverse returns 204 No Content + the entity URI in OData-EntityId).
     headers = {
         "Authorization": f"Bearer {token}",
         "OData-MaxVersion": "4.0",
         "OData-Version": "4.0",
         "Accept": "application/json",
         "Content-Type": "application/json; charset=utf-8",
         "Prefer": "return=representation"
     }

     response = requests.post(
         f"{dataverse_url}/gov_asardsecuritygrouppolicies",
         headers=headers,
         json=group_policy
     )
     ```

3. **Configure zone-wide approval (optional):**
   - If all agent sharing in certain zones (e.g., `sandbox`) is permitted:
     - Create a policy record with `groupobjectid` = `*` (wildcard)
     - Set `zone` to the target zone
     - Set `isactive` to Yes
   - This allows any sharing in that zone to be considered compliant

### Step 4: Configure Zone Classification

Define how environments are classified into zones based on naming conventions.

1. **Edit zone rules:**
   - Open `scripts/asard_zone_rules.py`
   - Review the `classify_environment_zone()` function
   - Default logic:
     ```python
     def classify_environment_zone(env_name: str) -> str:
         env_lower = env_name.lower()
         if any(x in env_lower for x in ['prod', 'production']):
             return 'production'
         elif any(x in env_lower for x in ['dev', 'development']):
             return 'development'
         elif any(x in env_lower for x in ['test', 'testing', 'qa']):
             return 'testing'
         elif any(x in env_lower for x in ['sandbox', 'sbx']):
             return 'sandbox'
         else:
             return 'unknown'
     ```

2. **Customize for your tenant:**
   - Modify the keyword lists to match your environment naming conventions
   - Add additional zones if needed (e.g., `uat`, `staging`)
   - Ensure zone names match those used in approved security group policies

3. **Test classification:**
   ```bash
   python -c "from asard_zone_rules import classify_environment_zone; \
   print(classify_environment_zone('Finance-Production-01'))"
   ```

### Step 5: Run Detection Scan

Execute the detection engine to identify agent sharing violations.

1. **First run — dry run mode (recommended):**
   ```bash
   python detect_agent_sharing_violations.py --dry-run
   ```
   - This mode performs detection but does NOT write to Dataverse
   - Review console output to validate zone classification and violation detection
   - Verify that approved groups are correctly recognized

2. **Full scan with Dataverse persistence:**
   ```bash
   python detect_agent_sharing_violations.py
   ```
   - Enumerates all agents across all environments
   - Evaluates sharing configurations against approved group policies
   - Writes violation records to `gov_asardsharingviolation` table
   - Exports CSV report to `reports/asard-violations-<timestamp>.csv`

3. **Review detection results:**
   - Check Dataverse table `gov_asardsharingviolation` for violation records
   - Review CSV export in `reports/` directory
   - Validate that violations are correctly identified (no false positives)

**Expected Output (example):**
```
[INFO] Enumerating environments...
[INFO] Found 47 environments
[INFO] Enumerating agents in environment 'Finance-Production-01'...
[INFO] Found 23 agents
[INFO] Evaluating agent 'Invoice Processing Bot' (shared with group 12345678...)
[WARN] Violation detected: Group not in approved list for zone 'production'
[INFO] Writing violation to Dataverse...
[SUCCESS] Detection complete. 5 violations detected.
[INFO] CSV report: reports/asard-violations-2026-02-13T191500Z.csv
```

### Step 6: Import Power Automate Flows

Deploy the approval and exception review workflows.

1. **Import remediation approval workflow:**
   - Open [Power Automate](https://make.powerautomate.com)
   - Navigate to **My flows** > **Import** > **Import Package (Legacy)**
   - Select `agent-sharing-access-restriction-detector/src/asard-remediation-approval-workflow.json` from [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions)
   - Configure connections (Dataverse, Office 365 Users)
   - Click **Import**

2. **Import exception review workflow:**
   - Repeat import process for `agent-sharing-access-restriction-detector/src/asard-exception-review-workflow.json` from FSI-AgentGov-Solutions
   - Configure connections
   - Set recurrence trigger (recommend daily at 8 AM)

3. **Configure approval recipients:**
   - Edit the remediation approval workflow
   - Update the **Start and wait for an approval** action
   - Set **Assigned to:** to the email addresses of governance team members

4. **Enable flows:**
   - Turn on both flows after import and configuration

### Step 7: Teams Notification Setup (Workflows webhook)

Office 365 Connectors (Teams Incoming Webhook) were retired on **December 31, 2025**. Configure a Microsoft Teams **Workflows** webhook instead:

1. **Create the Workflows webhook:**
   - In the target Teams channel (e.g., `#power-platform-governance`), click **···** (More options) > **Workflows**.
   - Choose the template **"Post to a channel when a webhook request is received"** and follow the wizard.
   - Required permissions: the workflow runs in the maker's account context; for governance scenarios, run it from a service account.
   - After the workflow is created, copy the issued **HTTPS URL** (format: `https://prod-NN.<region>.logic.azure.com:443/workflows/<workflow-id>/triggers/manual/paths/invoke?...`).

2. **Configure webhook in detection script:**
   - Open `scripts/detect_agent_sharing_violations.py`
   - Locate the `TEAMS_WEBHOOK_URL` configuration variable
   - Set it to your Workflows URL:
     ```python
     TEAMS_WEBHOOK_URL = "https://prod-NN.westus.logic.azure.com:443/workflows/<workflow-id>/triggers/manual/paths/invoke?..."
     ```
   - Alternatively, set environment variable:
     ```bash
     export TEAMS_WEBHOOK_URL="https://prod-NN.westus.logic.azure.com:443/workflows/<workflow-id>/triggers/manual/paths/invoke?..."
     ```
   - Payload shape is **Adaptive Card v1.5** wrapped in a Workflows `attachments` array (see Step 8 for an example). The legacy `MessageCard` schema used by Office 365 Connectors is NOT compatible.

   References: [Retirement of Office 365 connectors within Microsoft Teams](https://devblogs.microsoft.com/microsoft365dev/retirement-of-office-365-connectors-within-microsoft-teams/); [Post a workflow when a webhook request is received in Microsoft Teams](https://support.microsoft.com/en-us/office/post-a-workflow-when-a-webhook-request-is-received-in-microsoft-teams-8ae491c7-0394-4861-ba59-055e33f75498); [Adaptive Cards for Microsoft Teams](https://learn.microsoft.com/en-us/adaptive-cards/authoring-cards/getting-started).

3. **Test notification:**
   - Run detection scan with `--notify` flag:
     ```bash
     python detect_agent_sharing_violations.py --notify
     ```
   - Verify notification received in Teams channel
   - Check that adaptive card renders correctly

4. **Paste-ready curl test (Adaptive Card v1.5 payload):**
   The Workflows webhook expects a `message` envelope with an `attachments` array containing an Adaptive Card v1.5 payload. The legacy `MessageCard` schema used by Office 365 Connectors is NOT compatible. References: [Post a workflow when a webhook request is received](https://support.microsoft.com/en-us/office/post-a-workflow-when-a-webhook-request-is-received-in-microsoft-teams-8ae491c7-0394-4861-ba59-055e33f75498); [Adaptive Cards for Microsoft Teams](https://learn.microsoft.com/en-us/adaptive-cards/authoring-cards/getting-started).

   ```bash
   curl -X POST "$WEBHOOK_URL" -H 'Content-Type: application/json' -d '{
     "type": "message",
     "attachments": [{
       "contentType": "application/vnd.microsoft.card.adaptive",
       "content": {
         "type": "AdaptiveCard",
         "version": "1.5",
         "body": [{
           "type": "TextBlock",
           "text": "ASARD detection: <agent-name> shared with unapproved principal"
         }]
       }
     }]
   }'
   ```

   A successful test returns HTTP 200/202 and the card appears in the target channel within a few seconds.

### Step 8: Schedule Recurring Scans

Automate regular detection scans to continuously monitor agent sharing compliance.

**Option A: Windows Task Scheduler**

1. **Create scheduled task:**
   - Open Task Scheduler > **Create Task**
   - **General:**
     - Name: `ASARD Detection Scan`
     - Run whether user is logged on or not
     - Run with highest privileges
   - **Triggers:**
     - New trigger > Daily at 2:00 AM
     - Recur every 1 day
   - **Actions:**
     - New action > Start a program
     - Program: `C:\Python313\python.exe` (or your installed Python 3.11+ path; Python 3.9 reached end-of-life 2025-10-31 and should not be used for new deployments)
     - Arguments: `C:\dev\scripts\detect_agent_sharing_violations.py --notify`
     - Start in: `C:\dev\scripts`
   - **Conditions:** Adjust power and network settings as needed

**Option B: Azure DevOps Pipeline**

1. **Create YAML pipeline:**
   ```yaml
   trigger: none  # Manual or scheduled only
   
   schedules:
   - cron: "0 2 * * *"  # Daily at 2:00 AM UTC
     displayName: Daily ASARD scan
     branches:
       include:
       - main
     always: true
   
   pool:
     vmImage: 'ubuntu-latest'
   
   steps:
   - task: UsePythonVersion@0
     inputs:
       versionSpec: '3.13'  # Python 3.11+ required; 3.9 reached EOL 2025-10-31
   
   - script: |
       pip install msal requests azure-identity
     displayName: 'Install dependencies'
   
   - script: |
       python scripts/detect_agent_sharing_violations.py --notify
     displayName: 'Run ASARD detection'
     env:
       AZURE_CLIENT_ID: $(AZURE_CLIENT_ID)
       AZURE_CLIENT_SECRET: $(AZURE_CLIENT_SECRET)
       AZURE_TENANT_ID: $(AZURE_TENANT_ID)
       DATAVERSE_ENVIRONMENT_URL: $(DATAVERSE_ENVIRONMENT_URL)
       TEAMS_WEBHOOK_URL: $(TEAMS_WEBHOOK_URL)
   ```

**Option C: Power Automate Scheduled Flow**

1. **Create scheduled flow:**
   - Flow name: `ASARD Scheduled Detection`
   - Trigger: **Recurrence** (Daily at 2:00 AM)
   - Action: **HTTP** request to Azure Function or Logic App that runs detection script
   - (Requires hosting the Python script as an Azure Function)

## Verification

After deployment, verify that all components are functioning correctly.

### 1. Verify Dataverse Schema

**Check tables exist:**
```powershell
# Power Platform CLI selects the org; metadata enumeration uses the Dataverse Web API
pac org list
pac org select --environment <env-id>

# Enumerate ASARD tables via the documented EntityDefinitions endpoint.
# Az.Accounts 2.13+ supports -AsSecureString (recommended for modern modules); SecureString-by-default
# landed in a much later major (~4.0). Interpolating a [SecureString] directly into "Bearer $token"
# produces the literal string "Bearer System.Security.SecureString", so convert to plain text first.
# See https://learn.microsoft.com/en-us/powershell/module/az.accounts/get-azaccesstoken
$secure = (Get-AzAccessToken -ResourceUrl 'https://<org>.crm.dynamics.com' -AsSecureString).Token
$token  = ConvertFrom-SecureString -SecureString $secure -AsPlainText
Invoke-RestMethod -Uri "https://<org>.crm.dynamics.com/api/data/v9.2/EntityDefinitions?`$select=LogicalName&`$filter=startswith(LogicalName,'gov_asard')" -Headers @{ Authorization = "Bearer $token"; Accept = 'application/json' }

# Note: PowerShell 7+ is required for ConvertFrom-SecureString -AsPlainText.
# Older Az.Accounts (< 2.13) returned a plain-text [string] in .Token; if you must
# support that path, use: $token = (Get-AzAccessToken -ResourceUrl '...').Token
```

**Expected output:**
- `gov_asardsharingviolation`
- `gov_asardsecuritygrouppolicy`
- `gov_asardexception`
- `gov_asardremediationlog`

### 2. Run Test Detection Scan

**Execute detection with known test case:**
```bash
python detect_agent_sharing_violations.py --dry-run
```

**Verify:**
- Script completes without errors
- Zone classification produces expected zones
- Approved groups are correctly recognized
- Test violations (if any) are detected

### 3. Check Dataverse Records

**Verify violation records written:**
- Navigate to [Power Apps](https://make.powerapps.com) > Tables > `gov_asardsharingviolation`
- Confirm records exist with correct fields populated:
  - `gov_agentid`
  - `gov_environmentid`
  - `gov_sharingprincipalid`
  - `gov_zone`
  - `gov_detectiondate`
  - `gov_status` (should be `active`)

### 4. Verify Teams Notifications

**Test notification delivery:**
```bash
python detect_agent_sharing_violations.py --notify
```

**Check Teams channel:**
- Notification card received
- Adaptive card renders correctly
- Summary shows correct violation count
- Links to Dataverse records work (if configured)

### 5. Test Approval Workflow

**Trigger approval flow:**
- Manually trigger the approval workflow from Power Automate
- Or wait for automated trigger based on new violation

**Verify:**
- Approval request sent to configured recipients
- Adaptive card displays violation details
- Approve/Reject actions work
- Flow completes successfully

## Post-Deployment

### Establish Baseline

After initial deployment, establish a compliance baseline:

1. **Review initial violations:**
   - Analyze all violations detected in first scan
   - Classify as true positives vs. false positives
   - Document rationale for each classification

2. **Create exceptions for legitimate sharing:**
   - For violations that represent approved sharing patterns not covered by security groups:
     - Create exception records in `gov_asardexception` table
     - Set expiration dates and require business justification
     - See [Exception Management](asard-exception-management.md) for procedures

3. **Refine zone classification:**
   - If false positives occur due to incorrect zone assignment:
     - Update `asard_zone_rules.py` to improve classification logic
     - Re-run detection scan to validate

4. **Update approved group policies:**
   - Add any missing approved security groups to `gov_asardsecuritygrouppolicy` table

### Monitoring Recommendations

**Daily:**
- Review Teams notifications for new violations
- Triage new violations within 24 hours

**Weekly:**
- Review exception status (expiring/expired)
- Generate trend report (violation count over time)

**Monthly:**
- Audit approved security group list for accuracy
- Review remediation log for patterns
- Update zone classification rules if needed

### Exception Backlog Management

If initial scan reveals a large number of violations:

1. **Prioritize by risk:**
   - Production zones first
   - High-value agents (connected to sensitive data)
   - Agents shared with external users

2. **Batch remediation:**
   - Group violations by environment or agent owner
   - Coordinate with business units for remediation windows
   - Use `remediate_agent_sharing.py --whatif` to preview changes

3. **Create time-bound exceptions:**
   - For violations requiring extended remediation time:
     - Create exceptions with 30-90 day expiration
     - Assign to agent owners for resolution
     - Track progress via exception review workflow

## Next Steps

- **Exception Management:** See [Exception Management Guide](asard-exception-management.md) for ongoing exception workflows
- **Troubleshooting:** See [Troubleshooting Guide](asard-troubleshooting-guide.md) for common issues and resolutions
- **Remediation:** Use `remediate_agent_sharing.py` for automated sharing removal (see script documentation)

## Related Documentation

- [ASARD Exception Management Guide](asard-exception-management.md)
- [ASARD Troubleshooting Guide](asard-troubleshooting-guide.md)
- [Power Platform Admin API Documentation](https://learn.microsoft.com/en-us/power-platform/admin/powerplatform-api-getting-started)
- [Dataverse Security Concepts](https://learn.microsoft.com/power-apps/developer/data-platform/security-concepts)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
