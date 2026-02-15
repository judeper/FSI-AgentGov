# Troubleshooting: Control 2.22 - Inactivity Timeout Enforcement

> **Parent Control:** [2.22 - Inactivity Timeout Enforcement](../../../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md)

**Last Updated:** February 2026
**Support Contacts:** Power Platform Admin, AI Governance Lead
**Escalation Path:** L1 (IT Help Desk) → L2 (Power Platform Admin) → L3 (AI Governance Lead) → L4 (Microsoft Support)

---

## Common Issues and Resolutions

### Issue 1: Compliance Flow Shows "MissingPolicy" for Known Environment

**Symptoms:**

- Error log entry with error type = MissingPolicy
- Compliance status shows Unknown for an environment that should be governed
- Environment exists in PPAC but has no policy record

**Resolution Steps:**

1. **Verify the EnvironmentName used in the policy table:**
   - Open PPAC → Environments → select the environment → click **Environment URL** or check the URL bar
   - The EnvironmentName is the GUID in the URL (e.g., `d1234567-abcd-ef01-2345-6789abcdef01`)
   - Do NOT use the environment display name

2. **Add the policy record:**
   - Open the `fsi_environmentpolicy` table in Dataverse
   - Create a new record with the canonical EnvironmentName
   - Set `fsi_zone` and `fsi_requiredmaxduration` per governance policy

3. **Re-run the compliance flow** to generate a fresh compliance record

**Root Cause:** Environment was provisioned but not registered in the governance policy table, or the EnvironmentName value contains the display name instead of the canonical GUID.

!!! tip "Remediation Script"
    After adding the policy record and confirming the environment is non-compliant, use `Set-InactivityTimeout.ps1` to apply the correct timeout value via the BAP Admin API. See [PowerShell Setup](powershell-setup.md) for script parameters and usage.

---

### Issue 2: BAP Admin API Returns 401 Unauthorized

**Symptoms:**

- Compliance flow fails with HTTP 401 status
- Error log shows "Unauthorized" for environment API calls
- PowerShell script fails with authentication error

**Resolution Steps:**

1. **Verify token scope:**
   - The access token must be obtained with resource URL `https://api.bap.microsoft.com/.default`
   - Tokens scoped to `https://graph.microsoft.com` or other resources are not valid

2. **Check service principal permissions:**
   - Verify the app registration has the Power Platform Admin role, or per-environment admin role
   - Admin consent must be granted for the API permission

3. **Verify token expiration:**
   - Access tokens expire after 60-75 minutes
   - For long-running batch operations, implement token refresh logic

4. **Re-authenticate:**
   ```powershell
   Connect-AzAccount -ServicePrincipal `
       -ApplicationId $clientId `
       -CertificateThumbprint $thumbprint `
       -TenantId $tenantId
   $tokenResult = Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com"
   $token = if ($tokenResult.Token -is [securestring]) { $tokenResult.Token | ConvertFrom-SecureString -AsPlainText } else { $tokenResult.Token }
   ```

**Root Cause:** Token scope mismatch or expired credentials.

---

### Issue 3: BAP Admin API Returns 403 Forbidden

**Symptoms:**

- API call returns HTTP 403
- Service principal can authenticate but cannot access environment settings
- Error message references insufficient permissions

**Resolution Steps:**

1. **Verify role assignment:**
   - Navigate to PPAC → Settings → Admin roles
   - Confirm the service principal has the Power Platform Admin role
   - Alternatively, confirm Environment Admin role for the specific environment

2. **Check Conditional Access policies:**
   - CA policies may block service principal access from certain locations
   - Verify the service principal is not blocked by IP-based restrictions

3. **Verify environment type:**
   - Some environment types (e.g., developer, trial) may have restricted API access
   - Managed Environments (Control 2.1) typically have full API accessibility

**Root Cause:** Service principal lacks required admin role or is blocked by Conditional Access.

---

### Issue 4: Timeout Setting Not Taking Effect for Existing Sessions

**Symptoms:**

- Timeout configured in PPAC but users report sessions not expiring
- New configuration saved but no change in user experience
- Timeout works for new sessions but existing sessions use old values

**Resolution Steps:**

1. **Understand session behavior:**
   - Inactivity timeout settings apply to NEW sessions only
   - Users with existing sessions retain the timeout value from session creation
   - Users must sign out and sign back in for the new timeout to apply

2. **Force session refresh (if urgent):**
   - Revoke user sessions via Entra ID (Microsoft Graph API)
   - This forces all users to re-authenticate and pick up the new timeout setting

3. **Communicate the change:**
   - Notify users that they need to sign out and sign back in
   - Plan changes during maintenance windows to minimize disruption

**Root Cause:** Expected behavior — timeout settings are applied at session creation, not retroactively.

!!! tip "Automated Remediation"
    For environments requiring timeout changes, `Set-InactivityTimeout.ps1` supports `-WhatIf` preview and bulk remediation via CSV input. See [PowerShell Setup](powershell-setup.md) for details.

---

### Issue 5: Compliance Flow Fails with HTTP 429 (Rate Limiting)

**Symptoms:**

- Error log shows HTTP 429 status code
- Compliance flow runs partially — some environments scanned, others skipped
- Errors occur when scanning many environments in rapid succession

**Resolution Steps:**

1. **Reduce concurrency in the flow:**
   - Open the compliance flow in Power Automate → Edit
   - Locate the **Apply to Each** action that iterates over environments
   - Click the **⋯** (three dots) menu on the Apply to Each action → **Settings**
   - Under **Concurrency Control**, toggle it to **On** if not already enabled
   - Set the **Degree of Parallelism** slider to 2-3 (default is 5)
   - Click **Done**, then **Save** the flow

2. **Alternative — adjust via environment variable:**
   - Open Power Apps → Tables → search for `environmentvariabledefinitions`
   - Locate the `fsi_ITE_ConcurrencyLimit` environment variable
   - Update the current value from `5` to `2` or `3`
   - The compliance flow reads this variable at runtime to set its concurrency limit

3. **Add retry logic:**
   - Configure the HTTP action with retry policy:
     - Count: 3
     - Interval: PT30S (30 seconds)
     - Type: Exponential

4. **Schedule off-peak execution:**
   - Move the daily scan trigger to off-peak hours (e.g., 02:00 UTC instead of business hours)

**Root Cause:** BAP Admin API rate limits exceeded when scanning many environments concurrently.

---

### Issue 6: Non-Compliant Notification Email Not Received

**Symptoms:**

- Compliance flow runs successfully and creates compliance records
- Non-compliant environments detected but no notification sent
- Flow run history shows notification action skipped or failed

**Resolution Steps:**

1. **Verify notification recipients:**
   - Check the flow configuration for the notification action
   - Confirm recipient email addresses are correct and active
   - Verify recipients are not blocking Power Automate notifications

2. **Check the Office 365 Outlook connection:**
   - Open the flow in edit mode
   - Verify the Office 365 Outlook connection reference is authenticated
   - Re-authenticate if the connection shows an error state

3. **Verify notification trigger condition:**
   - The notification should trigger when at least one environment is Non-Compliant
   - Check the condition expression in the flow for correctness

**Root Cause:** Connection reference expired or notification recipients misconfigured.

---

### Issue 7: Environment Not Appearing in Compliance Scan Results

**Symptoms:**

- Environment exists in PPAC but no compliance record is created
- No error log entry for the environment either
- Environment is simply missing from scan results

**Resolution Steps:**

1. **Verify environment is in scope:**
   - The compliance flow retrieves environments from a configured source (API list or Dataverse query)
   - Confirm the environment is not filtered out by environment type or status

2. **Check environment status:**
   - Navigate to PPAC → Environments
   - Verify the environment state is "Ready" (not "Provisioning", "Deleting", or "Failed")

3. **Review flow run history:**
   - Open the compliance flow run history
   - Examine the "List Environments" action output
   - Confirm the target environment appears in the retrieved list

**Root Cause:** Environment filtered out by type/status criteria or not in "Ready" state.

---

### Issue 8: Dataverse Compliance Records Not Writing

**Symptoms:**

- Compliance flow runs without errors but no records appear in `fsi_inactivitytimeout_compliance` table
- Flow run history shows Create Record action failed
- Error references missing table, column, or privilege

**Resolution Steps:**

1. **Verify Dataverse table exists:**
   - Navigate to Power Apps → Tables
   - Search for `fsi_inactivitytimeout_compliance`
   - Verify the table schema matches expected columns

2. **Check service account permissions:**
   - The flow's connection reference user must have Create privilege on the compliance table
   - Assign the appropriate Dataverse security role

3. **Verify column names:**
   - Dataverse column logical names must match exactly (case-sensitive in API calls)
   - Common issue: using display names instead of logical names in flow expressions

4. **Check solution import:**
   - If the table was deployed as part of a solution, verify the solution imported successfully
   - Navigate to Power Apps → Solutions → check import status

**Root Cause:** Missing table, insufficient Dataverse privileges, or column name mismatch.

---

### Issue 9: Environment Variables Not Configured

**Symptoms:**

- Compliance flow uses unexpected default values (e.g., wrong concurrency, no notifications)
- Flow runs but notification emails are never sent despite non-compliant environments
- Concurrency limit does not match organizational expectations

**Resolution Steps:**

1. **Verify environment variables exist:**
   - Open Power Apps → select the governance environment → Tables
   - Search for `environmentvariabledefinitions`
   - Confirm these 3 variables are present:

   | Variable | Type | Default | Purpose |
   |----------|------|---------|---------|
   | `fsi_ITE_ConcurrencyLimit` | Decimal | 5 | Max parallel environment evaluations |
   | `fsi_ITE_NotificationRecipients` | String | (empty) | Email addresses for compliance alerts |
   | `fsi_ITE_ScanFrequencyHours` | Decimal | 24 | Scan interval in hours |

2. **Set current values:**
   - For each variable, click to open and set the **Current Value** appropriate for your organization
   - `fsi_ITE_NotificationRecipients` must be populated for notification emails to send (semicolon-separated for multiple addresses)

3. **If variables are missing, re-run the deployment script:**
   ```bash
   python scripts/create_timeout_environment_variables.py --verbose
   ```

4. **Verify after configuration:**
   - Run the compliance flow manually
   - Confirm it uses the updated concurrency limit and sends notifications to the configured recipients

**Root Cause:** Environment variables not deployed or current values not set after initial deployment (defaults may not match organizational requirements).

---

## Escalation Path

| Level | Contact | When to Escalate |
|-------|---------|-----------------|
| L1 — IT Help Desk | IT Support Team | User reports session not timing out; basic PPAC navigation issues |
| L2 — Power Platform Admin | Platform Admin Team | API authentication failures; flow configuration issues; environment settings not saving |
| L3 — AI Governance Lead | Governance Team | Policy definition questions; zone assignment disputes; compliance exceptions |
| L4 — Microsoft Support | Microsoft Premier/Unified | BAP Admin API behavior changes; environment-level bugs; Dataverse platform issues |

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Timeout applies to new sessions only | Existing sessions retain old timeout until re-authentication | Force session refresh via Entra ID session revocation for urgent changes |
| BAP Admin API rate limiting | Large tenant scans may be throttled | Reduce concurrency; schedule off-peak; implement exponential backoff |
| No per-app timeout granularity | Timeout is environment-level, not per-application | Use separate environments for different timeout requirements |
| Developer/trial environments | May have restricted API access | Exclude from automated scanning or use manual verification |

---

## Diagnostic Commands

### Verify timeout setting via API

```powershell
$envName = "d1234567-abcd-ef01-2345-6789abcdef01"
$uri = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/$envName/settings/privacy?api-version=2021-04-01"

$response = Invoke-RestMethod -Uri $uri -Headers @{
    Authorization = "Bearer $token"
} -Method Get

$response.properties | Format-List
```

### List all environments and their timeout status

```powershell
$envList = Invoke-RestMethod -Uri "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments?api-version=2021-04-01" `
    -Headers @{ Authorization = "Bearer $token" } -Method Get

foreach ($env in $envList.value) {
    $privacyUri = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/$($env.name)/settings/privacy?api-version=2021-04-01"
    try {
        $privacy = Invoke-RestMethod -Uri $privacyUri -Headers @{ Authorization = "Bearer $token" } -Method Get
        [PSCustomObject]@{
            EnvironmentName = $env.name
            DisplayName     = $env.properties.displayName
            TimeoutEnabled  = $privacy.properties.InactivityTimeoutEnabled
            TimeoutMinutes  = $privacy.properties.InactivityTimeoutInMinutes
        }
    } catch {
        [PSCustomObject]@{
            EnvironmentName = $env.name
            DisplayName     = $env.properties.displayName
            TimeoutEnabled  = "ERROR"
            TimeoutMinutes  = $_.Exception.Message
        }
    }
} | Format-Table -AutoSize
```

---

## Next Steps

- [Portal Walkthrough](portal-walkthrough.md) — Manual PPAC configuration
- [PowerShell Setup](powershell-setup.md) — Automated remediation
- [Verification & Testing](verification-testing.md) — Compliance validation

---

*Updated: February 2026 | Version: v1.3*
