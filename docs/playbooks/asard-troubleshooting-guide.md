# ASARD Troubleshooting Guide

!!! info "Related solution: UASD"
    This is the troubleshooting guide for **ASARD (Agent Sharing Access Restriction Detector)** (Python-based). If you are using **UASD (Unrestricted Agent Sharing Detector)** (Power Automate + Dataverse), see [UASD index](advanced-implementations/unrestricted-agent-sharing-detector/index.md). For the comparison between the two solutions and deployment guidance, see [ASARD Deployment Guide](asard-deployment-guide.md).

## Overview

This guide provides diagnostic procedures and resolutions for common issues encountered when operating the Agent Sharing Access Restriction Detector (ASARD) solution.

**Scope:** This guide covers operational issues, error diagnostics, and resolution procedures. For deployment instructions, see [Deployment Guide](asard-deployment-guide.md). For exception management procedures, see [Exception Management Guide](asard-exception-management.md).

**Escalation:** If issues persist after following resolution procedures, escalate to:
- **Platform issues:** Power Platform support or tenant admin team
- **Script issues:** Development team or governance automation owner
- **Policy questions:** Information security or compliance team

!!! tip "Diagnostic Approach"
    When troubleshooting, start with the most recent logs and error messages. Most issues can be diagnosed from script output, API responses, or Power Automate run history.

## BAP API Authentication Issues

### Symptom
- Detection script fails with `401 Unauthorized` errors
- Error message: `"error": {"code": "Unauthorized", "message": "Unauthorized"}`
- Script output shows authentication failures when enumerating environments or agents

### Causes
1. **Expired access token:** Access tokens expire after 1 hour
2. **Insufficient API permissions:** App registration missing required permissions
3. **Wrong tenant ID:** Script configured with incorrect tenant
4. **Missing admin consent:** API permissions not granted admin consent
5. **Disabled or deleted app registration:** Service principal no longer exists

### Diagnostic Steps

**1. Verify token acquisition:**

Enable Azure SDK logging using the documented Python pattern (the `azure-identity` library does not consume an `AZURE_IDENTITY_LOGGING` environment variable — see [Configure logging in the Azure libraries for Python](https://learn.microsoft.com/en-us/azure/developer/python/sdk/azure-sdk-logging)):

```python
import logging
import sys
from azure.identity import ClientSecretCredential

logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

credential = ClientSecretCredential(
    tenant_id=os.environ["AZURE_TENANT_ID"],
    client_id=os.environ["AZURE_CLIENT_ID"],
    client_secret=os.environ["AZURE_CLIENT_SECRET"],
    logging_enable=True,
)
```

Then re-run the detection script:

```bash
python detect_agent_sharing_violations.py --dry-run
```

- Check if token is successfully acquired from Microsoft Entra ID
- Verify token contains expected audience (Power Platform API)

**2. Check API permissions:**
- Navigate to Azure Portal > App registrations > Your app
- Go to **API permissions**
- Verify the following permissions exist and are granted:
  - **Power Platform API (Delegated)**: minimum `EnvironmentManagement.Environments.Read` plus the optional scopes documented in the deployment guide (e.g., `EnvironmentManagement.Groups.Read`, `AiFlows.Workflows.Read`, `CopilotGovernance.Features.Read`, `CopilotGovernance.Settings.Read`, `Analytics.AdvisorRecommendations.Read`). PPAPI is delegated-only as of May 2026 — for unattended SPN runs use the admin management application registration (`PUT api.bap.microsoft.com/.../adminApplications/{clientId}`) or a Power Platform RBAC role assignment instead. Register the PPAPI resource SP via `Connect-MgGraph -Scopes "Application.ReadWrite.All"; New-MgServicePrincipal -AppId 8578e004-a5c6-46e7-913e-12f58912df43 -DisplayName "Power Platform API"` if it does not appear in the picker. See the deployment guide and the canonical references: [Power Platform API permission reference](https://learn.microsoft.com/en-us/power-platform/admin/programmability-permission-reference), [Authenticate to Power Platform — v2](https://learn.microsoft.com/en-us/power-platform/admin/programmability-authentication-v2).
  - `Microsoft Graph / Group.Read.All`
- Check **Status** column shows "Granted for [tenant]"

**3. Validate configuration:**
```bash
# Verify environment variables
echo $AZURE_CLIENT_ID
echo $AZURE_TENANT_ID
# Do NOT echo client secret for security reasons
```
- Confirm values match Microsoft Entra ID app registration
- Tenant ID should match your organization's tenant

**4. Test token manually:**
```python
from azure.identity import ClientSecretCredential
import os

credential = ClientSecretCredential(
    tenant_id=os.environ["AZURE_TENANT_ID"],
    client_id=os.environ["AZURE_CLIENT_ID"],
    client_secret=os.environ["AZURE_CLIENT_SECRET"]
)

token = credential.get_token("https://api.powerplatform.com/.default")
print(f"Token acquired: {token.token[:20]}...")
print(f"Expires on: {token.expires_on}")
```

!!! note "Resource scope selection"
    Use `https://api.powerplatform.com/.default` for the modern Power Platform API (PPAPI) — see [Authenticate to Power Platform — v2](https://learn.microsoft.com/en-us/power-platform/admin/programmability-authentication-v2). Legacy BAP admin endpoints invoked via the `Microsoft.PowerApps.Administration.PowerShell` module use `https://service.powerapps.com/.default` instead. Avoid the undocumented `https://api.bap.microsoft.com/.default` scope.

### Resolution

**For expired tokens:**
- Tokens are automatically refreshed by the MSAL library
- If script runs longer than 1 hour, ensure refresh logic is enabled
- No manual action required in most cases

**For insufficient permissions:**
1. Add missing API permissions in Azure Portal
2. Click **Grant admin consent** for your tenant
3. Wait 5-10 minutes for permission propagation
4. Retry detection script

**For wrong tenant ID:**
1. Obtain correct tenant ID from Azure Portal > Microsoft Entra ID > Overview
2. Update `AZURE_TENANT_ID` environment variable or configuration
3. Retry

**For missing admin consent:**
1. Navigate to App registrations > Your app > API permissions
2. Click **Grant admin consent for [tenant]**
3. Confirm the action
4. Verify **Status** column updates to "Granted"

**For disabled app registration:**
1. Check app registration status in Azure Portal
2. If deleted, recreate following [Deployment Guide Step 1](asard-deployment-guide.md#step-1-create-microsoft-entra-id-app-registration)
3. Update configuration with new client ID and secret

## Security Group Resolution Failures

### Symptom
- Agents marked as violations despite being shared with approved groups
- Warning: `Unable to resolve security group: <group-id>`
- Console output shows group resolution failures
- False positive violations for agents with approved sharing

### Causes
1. **Group not found:** Group ID does not exist in Microsoft Entra ID
2. **Deleted security groups:** Group was deleted after agent sharing configured
3. **Nested groups not supported:** Sharing principal is member of approved group (indirectly)
4. **Incorrect group ID format:** Group object ID vs. group name vs. group email
5. **Insufficient Graph API permissions:** Cannot read group membership

### Diagnostic Steps

**1. Verify group exists in Microsoft Entra ID:**
```powershell
# Using Microsoft Graph PowerShell
Connect-MgGraph -Scopes "Group.Read.All"
Get-MgGroup -GroupId "<group-id>"
```
- If group not found, it may have been deleted
- Verify group ID matches Microsoft Entra ID object ID (GUID format)

**2. Check group ID format:**
- Group object ID: `12345678-1234-1234-1234-123456789abc` (GUID)
- Group name: `Finance-Agents-Prod` (display name)
- Group email: `finance-agents@contoso.com` (mail attribute)
- **Script expects object ID** (GUID format)

**3. Test group resolution:**
```python
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
import os

credential = ClientSecretCredential(
    tenant_id=os.environ["AZURE_TENANT_ID"],
    client_id=os.environ["AZURE_CLIENT_ID"],
    client_secret=os.environ["AZURE_CLIENT_SECRET"]
)

client = GraphServiceClient(credential)
group = await client.groups.by_group_id("<group-id>").get()
print(f"Group: {group.display_name}")
```

**4. Review approved group policy table:**
- Navigate to Dataverse > `gov_asardsecuritygrouppolicy`
- Verify group IDs are in object ID (GUID) format
- Check `isactive` field is set to Yes
- Confirm `zone` matches environment classification

### Resolution

**For deleted groups:**
1. Identify replacement group or create new approved group
2. Update `gov_asardsecuritygrouppolicy` table with new group ID
3. Update agent sharing to use new group (if remediation needed)
4. Re-run detection scan

**For incorrect group ID format:**
1. Obtain correct object ID from Microsoft Entra ID:
   ```powershell
   Get-MgGroup -Filter "displayName eq 'Finance-Agents-Prod'" | Select-Object Id, DisplayName
   ```
2. Update `gov_asardsecuritygrouppolicy` table with correct object ID
3. Re-run detection scan

**For nested groups (design limitation):**
- **Current behavior:** Script does NOT resolve nested group membership
- **Workaround options:**
  1. **Flatten sharing:** Share agent directly with approved group (not nested)
  2. **Create exception:** Add exception record for legitimate nested group sharing
  3. **Enhance script:** Modify `bap_admin_client.py` to recursively resolve groups using the Microsoft Graph `GET /groups/{id}/transitiveMembers` endpoint. Calls that use advanced query parameters (`$count`, `$search`, or advanced `$filter`) require the `ConsistencyLevel: eventual` header and `$count=true` — see [List group transitive members](https://learn.microsoft.com/en-us/graph/api/group-list-transitivemembers) and [Advanced query capabilities on directory objects](https://learn.microsoft.com/en-us/graph/aad-advanced-queries). Grant both `Group.Read.All` **and** `GroupMember.Read.All` to the app registration for this code path.

**For insufficient permissions:**
1. Verify `Group.Read.All` (and `GroupMember.Read.All` if the nested-group resolution path is enabled) permissions are granted to the app registration
2. Grant admin consent if missing
3. Retry detection script

**For stale group policy:**
1. Review all records in `gov_asardsecuritygrouppolicy`
2. Set `isactive = false` for groups that no longer exist
3. Add new approved groups as needed
4. Document group lifecycle process to prevent future staleness

## Agent Enumeration Failures

### Symptom
- Detection script reports fewer agents than expected
- Warning: `Failed to enumerate agents in environment: <env-name>`
- Incomplete agent inventory in violation reports
- Script completes but misses environments or agents

### Causes
1. **API throttling:** Too many requests to BAP Admin API
2. **Environment access denied:** Service principal lacks permissions for environment
3. **Deleted agents:** Agent was deleted after enumeration started
4. **API timeout:** Request took too long and timed out
5. **Transient API failures:** Temporary service issues

### Diagnostic Steps

**1. Check API throttling headers:**
```python
# Add logging in bap_admin_client.py
response = requests.get(url, headers=headers)
if response.status_code in (429, 503):
    retry_after = int(response.headers.get('Retry-After', '0'))
    print(f'Throttled, retry after {retry_after}s')
    # Dataverse-specific (when calling api.crm.dynamics.com):
    burst_remaining = response.headers.get('x-ms-ratelimit-burst-remaining-xrm-requests')
    time_remaining = response.headers.get('x-ms-ratelimit-time-remaining-xrm-requests')
    exec_time_remaining = response.headers.get('x-ms-ratelimit-time-remaining-xrm-executiontime')
    print(f'Dataverse rate-limit remaining: burst={burst_remaining} time={time_remaining} exec={exec_time_remaining}')
```
- Honor the standard `Retry-After` header on any `429` or `503` response (this is the documented Microsoft pattern across Dataverse, Microsoft Graph, and Power Platform APIs)
- For Dataverse calls specifically, the `x-ms-ratelimit-burst-remaining-xrm-requests`, `x-ms-ratelimit-time-remaining-xrm-requests`, and `x-ms-ratelimit-time-remaining-xrm-executiontime` headers indicate how close the caller is to the per-user service-protection limits — see [Service Protection API Limits](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/api-limits) and [Microsoft Graph throttling guidance](https://learn.microsoft.com/en-us/graph/throttling) (note: legacy `x-ratelimit-remaining` / `x-ratelimit-reset` header names are **not** Microsoft conventions and will always be `None`)

**2. Verify environment permissions:**
```powershell
# Enumerate service principals with access to the target environment
pac admin list-service-principal --environment <env-id>
```
- Service principal should appear in environment security group or have system admin role

**3. Test agent enumeration for specific environment:**
```python
from bap_admin_client import BAPAdminClient
client = BAPAdminClient()
agents = client.get_agents(environment_id="<env-id>")
print(f"Found {len(agents)} agents")
```

**4. Review script logs:**
```bash
python detect_agent_sharing_violations.py --dry-run 2>&1 | tee detection.log
```
- Search for "Failed to enumerate" or exception stack traces
- Check for timeout errors or connection issues

### Resolution

**For API throttling:**
1. **Implement exponential backoff:** Modify `bap_admin_client.py`:
   ```python
   import time
   
   def get_agents_with_retry(env_id, max_retries=3):
       for attempt in range(max_retries):
           try:
               return get_agents(env_id)
           except ThrottlingException:
               wait_time = 2 ** attempt  # Exponential backoff
               print(f"Throttled, waiting {wait_time}s...")
               time.sleep(wait_time)
   ```

2. **Reduce request rate:** Add delay between environment enumerations:
   ```python
   for env in environments:
       agents = get_agents(env.id)
       time.sleep(1)  # 1 second delay between requests
   ```

**For environment access denied:**
1. **Grant system admin role to service principal:**
   - Navigate to Power Platform Admin Center
   - Select environment > Settings > Users + permissions > Security roles
   - Assign **System Administrator** role to app registration user

2. **Use delegated authentication:** Switch from application permissions to delegated permissions with user context

**For deleted agents:**
- Expected behavior: Agent deleted between enumeration and evaluation
- Script should handle gracefully with try-catch
- No action required if script continues

**For API timeouts:**
1. Increase timeout in requests:
   ```python
   response = requests.get(url, headers=headers, timeout=60)  # 60 seconds
   ```
2. Implement pagination for large result sets

**For transient failures:**
1. Retry detection script
2. If persistent, check [Microsoft 365 Service Health](https://admin.microsoft.com/Adminportal/Home#/servicehealth) for platform issues
3. Implement retry logic with exponential backoff

## Dataverse Write Errors

### Symptom
- Detection script completes but no violations written to Dataverse
- Error: `"error": {"code": "0x80040237", "message": "Duplicate key detected"}`
- Error: `"error": {"code": "0x80048306", "message": "Request throttled"}`
- Violation records missing or incomplete in `gov_asardsharingviolation` table

### Causes
1. **Schema mismatch:** Dataverse table schema does not match script expectations
2. **Alternate key conflicts:** Attempting to create record with duplicate key
3. **API throttling:** Too many Dataverse write operations
4. **Field validation errors:** Data violates field constraints (length, format)
5. **Missing required fields:** Script not providing all required attributes

### Diagnostic Steps

**1. Verify schema version:**
```python
# Check table definition
import requests
response = requests.get(
    f"{dataverse_url}/api/data/v9.2/EntityDefinitions(LogicalName='gov_asardsharingviolation')",
    headers={"Authorization": f"Bearer {token}"}
)
print(response.json())
```
- Compare attributes with script's expected schema
- Check for missing fields or data type mismatches

**2. Test single record write:**
```python
violation_record = {
    "gov_agentid": "test-agent-123",
    "gov_environmentid": "test-env-456",
    "gov_sharingprincipalid": "test-group-789",
    "gov_zone": "production",
    "gov_detectiondate": "2026-02-13T19:00:00Z",
    "gov_status": "active"
}

response = requests.post(
    f"{dataverse_url}/api/data/v9.2/gov_asardsharingviolations",
    headers={"Authorization": f"Bearer {token}"},
    json=violation_record
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

**3. Check for duplicate keys:**
- Review alternate key definition on `gov_asardsharingviolation` table
- Typical alternate key: `gov_agentid` + `gov_sharingprincipalid` + `gov_detectiondate`
- Query existing records to find conflicts:
  ```
  GET /api/data/v9.2/gov_asardsharingviolations?$filter=gov_agentid eq 'test-agent-123'
  ```

**4. Monitor API throttling:**
```bash
# Enable Dataverse API throttling logging
export DATAVERSE_DEBUG=1
python detect_agent_sharing_violations.py
```

### Resolution

**For schema mismatch:**
1. Re-run schema creation script:
   ```bash
   python create_asard_dataverse_schema.py --update
   ```
2. If script does not support updates, manually add missing fields via Power Apps UI
3. Update script to match current schema

**For alternate key conflicts:**
1. **Identify conflict:** Determine which record has duplicate key
2. **Update instead of insert:** Modify script to use PATCH for existing records:
   ```python
   # Check if record exists
   filter_query = f"gov_agentid eq '{agent_id}' and gov_sharingprincipalid eq '{group_id}'"
   existing = requests.get(
       f"{dataverse_url}/api/data/v9.2/gov_asardsharingviolations?$filter={filter_query}",
       headers={"Authorization": f"Bearer {token}"}
   )
   
   if existing.json()['value']:
       # Update existing record
       record_id = existing.json()['value'][0]['gov_asardsharingviolationid']
       requests.patch(f"{dataverse_url}/api/data/v9.2/gov_asardsharingviolations({record_id})", ...)
   else:
       # Create new record
       requests.post(f"{dataverse_url}/api/data/v9.2/gov_asardsharingviolations", ...)
   ```

**For API throttling:**
1. **Batch write operations:** Use `$batch` endpoint to reduce request count
2. **Implement backoff:** Catch throttling errors (429 status code) and retry:
   ```python
   if response.status_code == 429:
       retry_after = int(response.headers.get('Retry-After', 60))
       time.sleep(retry_after)
   ```
3. **Reduce write frequency:** Batch violations in memory and write in chunks

**For field validation errors:**
1. Review error message for specific field causing validation failure
2. Common issues:
   - **String too long:** Trim or truncate values to field max length
   - **Invalid date format:** Use ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`
   - **Invalid choice value:** Ensure choice field values match defined options
3. Update script to validate data before write

**For missing required fields:**
1. Review table definition to identify required fields
2. Update script to provide all required attributes
3. Set default values for optional fields

## Detection False Positives/Negatives

### Symptom
- **False positives:** Agents marked as violations despite compliant sharing
- **False negatives:** Non-compliant agents not detected as violations
- Zone classification incorrect for environments
- Approved groups not recognized

### Causes
1. **Zone classification errors:** Environment names do not match classification rules
2. **Sharing principal parsing issues:** Script cannot parse sharing configuration format
3. **Approved group policy gaps:** Missing entries in policy table
4. **Zone-specific policy not applied:** Group approved for one zone but agent in different zone
5. **Wildcard policy misconfigured:** Zone-wide approval not working as expected

### Diagnostic Steps

**1. Test zone classification:**
```python
from asard_zone_rules import classify_environment_zone

test_envs = [
    "Finance-Production-01",
    "HR-Development-Sandbox",
    "Test-Environment-QA",
    "MyApp-Prod"
]

for env_name in test_envs:
    zone = classify_environment_zone(env_name)
    print(f"{env_name} -> {zone}")
```
- Verify zones match expectations
- Check for `unknown` zone assignments

**2. Review sharing principal structure:**
```python
# Log sharing principals during detection
agent = get_agent(agent_id)
print(f"Sharing principals: {agent.get('sharingPrincipals', [])}")
```
- Verify structure matches script parsing logic
- Check for unexpected formats (e.g., nested arrays, null values)

**3. Audit approved group policy:**
```http
GET /api/data/v9.2/gov_asardsecuritygrouppolicies?$select=gov_groupobjectid,gov_groupname,gov_zone,gov_isactive&$filter=gov_isactive eq true
```
- Confirm all approved groups are listed
- Verify zone assignments match actual usage
- Dataverse does not support direct SQL `SELECT` against the primary store. If the read-only TDS endpoint is enabled on the environment, you can query the same data via SQL Server Management Studio, Power BI, or Tabular Editor at `<org>.crm.dynamics.com,5558` — see [Use SQL to query data — Dataverse TDS endpoint](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/dataverse-sql-query). TDS is read-only and is not enabled by default.

**4. Trace specific violation:**
```bash
python detect_agent_sharing_violations.py --dry-run --agent-id "<agent-id>"
```
- Add `--agent-id` flag to debug specific agent
- Review console output for evaluation logic

### Resolution

**For zone classification errors:**
1. **Update classification rules:** Edit `asard_zone_rules.py`:
   ```python
   def classify_environment_zone(env_name: str) -> str:
       env_lower = env_name.lower()
       # Add your custom keywords
       if 'prod' in env_lower or 'prd' in env_lower:
           return 'production'
       # ... add more patterns
   ```
2. **Document naming conventions:** Ensure environment names follow consistent patterns
3. Re-run detection after rule updates

**For sharing principal parsing issues:**
1. **Review API response structure:** Examine raw BAP Admin API response
2. **Update parsing logic:** Modify `detect_agent_sharing_violations.py`:
   ```python
   def parse_sharing_principals(agent_data):
       principals = agent_data.get('sharingPrincipals', [])
       # Add error handling and logging
       for principal in principals:
           if not isinstance(principal, dict):
               print(f"Unexpected principal format: {principal}")
               continue
           # Extract group ID with fallback logic
           group_id = principal.get('id') or principal.get('principalId')
   ```

**For approved group policy gaps:**
1. Identify missing groups from false positive violations
2. Validate with security team that groups should be approved
3. Add missing groups to `gov_asardsecuritygrouppolicy` table
4. Re-run detection scan

**For zone-specific policy issues:**
1. **Verify zone matching:** Ensure agent's environment zone matches policy zone
2. **Add cross-zone policies:** If group should be approved in multiple zones:
   - Create separate policy records for each zone
   - Or use wildcard zone (`*`) if appropriate
3. **Review zone hierarchy:** Some organizations need parent/child zone logic

**For wildcard policy misconfigured:**
1. **Verify wildcard format:** Policy record should have:
   - `gov_groupobjectid = "*"`
   - `gov_zone = "<target-zone>"`
   - `gov_isactive = true`
2. **Check script logic:** Ensure detection script recognizes wildcard:
   ```python
   if group_id in approved_groups or "*" in approved_groups:
       return True  # Approved
   ```

## Remediation Failures

### Symptom
- `remediate_agent_sharing.py` script fails during execution
- Error: `"error": {"code": "BadRequest", "message": "Invalid PATCH operation"}`
- Agent sharing not removed after remediation runs
- Script reports success but sharing still present

### Causes
1. **PATCH operation errors:** API rejects sharing removal request
2. **Validation failures:** Sharing configuration cannot be modified (e.g., owner sharing)
3. **Concurrent modifications:** Another process modified agent during remediation
4. **Insufficient permissions:** Service principal cannot modify agent sharing
5. **Agent state issues:** Agent in draft mode or being published

### Diagnostic Steps

**1. Test remediation in WhatIf mode:**
```bash
python remediate_agent_sharing.py --whatif
```
- Review proposed changes without applying
- Identify which agents/groups would be modified

**2. Test single agent remediation:**
```bash
python remediate_agent_sharing.py --agent-id "<agent-id>" --dry-run
```
- Isolate to single agent to debug
- Review API request/response details

**3. Check agent state:**
```python
agent = bap_client.get_agent(agent_id)
print(f"State: {agent.get('state')}")
print(f"Owner: {agent.get('owner')}")
print(f"Sharing: {agent.get('sharingPrincipals')}")
```
- Verify agent is published (not draft)
- Confirm sharing principals are modifiable

**4. Verify permissions:**
```powershell
# Enumerate service principal role assignments in the target environment
pac admin list-service-principal --environment <env-id>
```
- Service principal needs **System Administrator** or **Environment Admin** role

### Resolution

**For PATCH operation errors:**
1. **Review API error details:** Check full error response for specific issue
2. **Validate PATCH payload:** Ensure request body format matches API requirements:
   ```json
   {
     "sharingPrincipals": [
       {"id": "keep-this-group-id"},
       // Removed group omitted from array
     ]
   }
   ```
3. **Test sharing changes outside the script:** Power Platform CLI does not expose an agent-sharing command as of 2026. Test sharing changes via the Copilot Studio web UI (`make.copilotstudio.microsoft.com` → agent → **Share** → remove principal) OR by patching the Dataverse `principalobjectaccess` rows directly via the Web API.

**For validation failures (owner sharing):**
- **Limitation:** Agent owners cannot be removed via sharing API
- **Workaround:** Change agent owner first, then remove old owner from sharing
- **Exception:** Create exception for owner sharing if legitimate

**For concurrent modifications:**
1. **Implement optimistic concurrency:** Use ETag headers:
   ```python
   # Get current ETag
   response = requests.get(agent_url, headers=headers)
   etag = response.headers.get('ETag')
   
   # Include in PATCH request
   patch_headers = {**headers, 'If-Match': etag}
   requests.patch(agent_url, headers=patch_headers, json=data)
   ```
2. **Retry logic:** Catch concurrency errors and retry after delay

**For insufficient permissions:**
1. Grant **System Administrator** role to service principal in target environment
2. Or use delegated authentication with user account that has appropriate permissions

**For agent state issues:**
1. **Wait for publishing:** If agent is being published, retry after completion
2. **Handle draft agents:** Skip remediation for draft agents or wait until published
3. **Add state check:**
   ```python
   if agent.get('state') != 'Published':
       print(f"Skipping agent in {agent.get('state')} state")
       return
   ```

**Post-validation required:**
- After successful remediation, always re-run detection scan
- Verify sharing actually removed (not just API success)
- Update violation status in Dataverse

## Exception Workflow Issues

### Symptom
- Expired exceptions not reset to active violations
- Exception expiration notifications not sent
- Exception review workflow does not trigger
- Exception records not created properly

### Causes
1. **Flow misconfiguration:** Triggers or conditions not set correctly
2. **Webhook failures:** Teams webhook URL invalid or channel deleted
3. **Trigger conditions:** Recurrence schedule or data trigger not working
4. **Dataverse connection issues:** Flow cannot read/write exception records
5. **Adaptive card errors:** Card payload invalid or missing required fields

### Diagnostic Steps

**1. Check flow run history:**
- Navigate to Power Automate > My flows > Exception Review Workflow
- Click **Run history**
- Review failed runs for error details

**2. Test webhook manually:**

Teams Workflows webhooks (the supported replacement for retired Office 365 Connectors) reject the legacy `MessageCard` `{"text":"..."}` payload with HTTP 400. The supported payload is an Adaptive Card v1.5 wrapped in the Workflows `attachments` shape — see [Post a workflow when a webhook request is received in Microsoft Teams](https://support.microsoft.com/en-us/office/post-a-workflow-when-a-webhook-request-is-received-in-microsoft-teams-8ae491c7-0394-4861-ba59-055e33f75498):

```bash
curl -X POST "$WEBHOOK_URL" -H 'Content-Type: application/json' -d '{
  "type":"message",
  "attachments":[{
    "contentType":"application/vnd.microsoft.card.adaptive",
    "content":{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Test from ASARD"}]}
  }]
}'
```
- Verify notification appears in Teams channel

**3. Query exception records:**
```sql
SELECT gov_asardexceptionid, gov_expirationdate, gov_status
FROM gov_asardexception
WHERE gov_expirationdate < GETDATE() AND gov_status = 'active'
```
- Check if expired exceptions exist
- Verify status field values

**4. Test flow manually:**
- Open flow in Power Automate
- Click **Test** > **Manually**
- Provide test data and observe execution

### Resolution

**For flow misconfiguration:**
1. **Verify recurrence trigger:**
   - Open flow > Edit trigger
   - Confirm schedule is correct (e.g., Daily at 8 AM)
   - Check time zone settings

2. **Update filter conditions:**
   - In "Get expired exceptions" action
   - Filter query should be:
     ```
     gov_expirationdate lt '@{utcNow()}' and gov_status eq 'active'
     ```

**For webhook failures:**
1. **Regenerate webhook:**
   - Remove old webhook from Teams channel
   - Create new webhook
   - Update flow with new URL

2. **Test webhook connectivity:**
   - Use curl or Postman to send test message
   - Check Teams channel for delivery

**For trigger conditions:**
1. **Review trigger settings:**
   - Recurrence: Verify interval and frequency
   - Dataverse trigger: Check table and filter conditions

2. **Enable flow:**
   - Ensure flow is turned on (not disabled)
   - Check if any connections need reauthentication

**For Dataverse connection issues:**
1. **Reauthenticate connection:**
   - Flow > Edit > Connections
   - Remove and re-add Dataverse connection
   - Use account with appropriate permissions

2. **Check table permissions:**
   - Verify flow's connection has read/write access to exception table

**For adaptive card errors:**
1. **Validate card payload:**
   - Copy adaptive card JSON from flow action
   - Test in [Adaptive Cards Designer](https://adaptivecards.io/designer/)
   - Fix any schema errors

2. **Check dynamic content:**
   - Ensure all dynamic fields (e.g., `@{items('Apply_to_each')?['gov_agentid']}`) have fallback values
   - Add null checks: `@{coalesce(items('Apply_to_each')?['gov_agentid'], 'N/A')}`

**Monitoring exceptions workflow health:**
- Set up flow analytics in Power Automate
- Configure failure notifications to governance team
- Review run history weekly for patterns

## Related Documentation

- [ASARD Deployment Guide](asard-deployment-guide.md)
- [ASARD Exception Management Guide](asard-exception-management.md)
- [Power Platform Admin API Documentation](https://learn.microsoft.com/en-us/power-platform/admin/powerplatform-api-getting-started)
- [Dataverse Web API Documentation](https://learn.microsoft.com/power-apps/developer/data-platform/webapi/overview)
- [Power Automate Troubleshooting](https://learn.microsoft.com/en-us/troubleshoot/power-platform/power-automate/welcome-power-automate)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
