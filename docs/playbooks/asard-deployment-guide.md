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
- **Python 3.9 or later:** Verified with Python 3.9, 3.10, 3.11
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
   - Search for `PowerApps-Advisor` and select it
   - Select **Delegated permissions** or **Application permissions** (depending on authentication mode)
   - Add the following permissions:
     - `Analysis.Read.All` (BAP Admin API access)
   - Click **Add a permission** again > **Microsoft Graph**
   - Add the following permissions:
     - `Group.Read.All` (to resolve security groups)
   - Click **Grant admin consent** for your tenant

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
     
     response = requests.post(
         f"{dataverse_url}/gov_asardsecuritygrouppolicies",
         headers={"Authorization": f"Bearer {token}"},
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

### Step 7: Configure Teams Notifications

Set up Microsoft Teams webhook for violation alerts and remediation results.

1. **Create Teams webhook:**
   - Open Microsoft Teams
   - Navigate to target channel (e.g., `#power-platform-governance`)
   - Click **···** (More options) > **Connectors**
   - Search for **Incoming Webhook** and click **Configure**
   - **Name:** `ASARD Notifications`
   - **Upload image:** (optional)
   - Click **Create**
   - **Copy the webhook URL** (format: `https://outlook.office.com/webhook/...`)

2. **Configure webhook in detection script:**
   - Open `scripts/detect_agent_sharing_violations.py`
   - Locate the `TEAMS_WEBHOOK_URL` configuration variable
   - Set it to your webhook URL:
     ```python
     TEAMS_WEBHOOK_URL = "https://outlook.office.com/webhook/..."
     ```
   - Alternatively, set environment variable:
     ```bash
     export TEAMS_WEBHOOK_URL="https://outlook.office.com/webhook/..."
     ```

3. **Test notification:**
   - Run detection scan with `--notify` flag:
     ```bash
     python detect_agent_sharing_violations.py --notify
     ```
   - Verify notification received in Teams channel
   - Check that adaptive card renders correctly

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
     - Program: `C:\Python39\python.exe`
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
       versionSpec: '3.9'
   
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
# Power Platform CLI
pac org list
pac org select --environment <env-id>
pac data list-tables --filter "gov_asard"
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
