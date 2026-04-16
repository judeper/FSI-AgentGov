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
   - Navigate to [Power Apps](https://make.powerapps.com) → select the governance environment
   - Open **Tables** → search for `fsi_environmentpolicy`
   - Click **+ New row** to create a new record with the canonical EnvironmentName
   - Set `fsi_zone` and `fsi_requiredmaxduration` per governance policy

3. **Re-run the compliance flow** to generate a fresh compliance record

**Root Cause:** Environment was provisioned but not registered in the governance policy table, or the EnvironmentName value contains the display name instead of the canonical GUID.

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

   # Obtain a fresh token for diagnostic API calls
   # Az.Accounts <4.x returns plain string; >=4.x returns SecureString
   $tokenResult = Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com"
   if ($tokenResult.Token -is [securestring]) {
       $token = $tokenResult.Token | ConvertFrom-SecureString -AsPlainText
   } else {
       $token = $tokenResult.Token
   }
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

---

### Issue 5: Compliance Flow Fails with HTTP 429 (Rate Limiting)

**Symptoms:**

- Error log shows HTTP 429 status code
- Compliance flow runs partially — some environments scanned, others skipped
- Errors occur when scanning many environments in rapid succession

**Resolution Steps:**

1. **Reduce concurrency:**
   - Open the compliance flow in Power Automate
   - Locate the Apply to Each action that iterates over environments
   - Reduce the degree of parallelism (default 5; try 2-3)

2. **Add retry logic:**
   - Configure the HTTP action with retry policy:
     - Count: 3
     - Interval: PT30S (30 seconds)
     - Type: Exponential
   - Honor the `Retry-After` response header — the BAP Admin API returns the recommended wait time in seconds. Ensure the retry interval is at least as long as the `Retry-After` value.

3. **Schedule off-peak execution:**
   - Move the daily scan trigger to off-peak hours (e.g., 02:00 UTC instead of business hours)

4. **Re-scan missed environments:**
   - After a rate-limited run, check the compliance records to identify which environments were not scanned
   - Re-run the flow manually during off-peak hours for any environments that were skipped

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

- Compliance flow runs without errors but no records appear in `fsi_inactivitytimeoutcompliance` table
- Flow run history shows Create Record action failed
- Error references missing table, column, or privilege

**Resolution Steps:**

1. **Verify Dataverse table exists:**
   - Navigate to Power Apps → Tables
   - Search for `fsi_inactivitytimeoutcompliance`
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

### Issue 9: Compliance Flow Fails Due to Missing or Incorrect Environment Variables

**Symptoms:**

- Compliance flow fails at the first or second action after trigger
- Flow run history shows "InvalidTemplate" or "ExpressionEvaluationFailed" errors
- Environment variables show empty or default values after solution import

**Resolution Steps:**

1. **Verify environment variables are configured:**
   - Navigate to Power Apps → Solutions → select the ITE solution
   - Open **Environment Variables** in the solution
   - Confirm these variables have correct values:
     - `fsi_ITE_ConcurrencyLimit`: Maximum parallel environment evaluations (default: 5)
     - `fsi_ITE_NotificationRecipients`: Email addresses for compliance alerts
     - `fsi_ITE_ScanFrequencyHours`: Scan interval in hours (default: 24)

2. **Set current values (not just default values):**
   - Environment variables have both a **Default Value** (defined in the solution) and a **Current Value** (tenant-specific)
   - After importing the solution, set the **Current Value** for each variable to override the defaults for your environment
   - `fsi_ITE_NotificationRecipients` has no default — this must be set before the notification action will work

3. **Verify connection references are authenticated:**
   - In the same solution, open **Connection References**
   - Confirm each connection reference shows an active, authenticated connection
   - Re-authenticate any connection references showing error or warning states

4. **Re-run the compliance flow** after updating environment variables and connection references

**Root Cause:** Solution import creates environment variable definitions with default values, but tenant-specific current values must be set manually. Connection references also require authentication after import.

---

### Issue 10: Agent Session Timeout Setting Not Available in Copilot Studio

**Symptoms:**

- Session timeout option not visible in Copilot Studio agent settings
- Setting appears grayed out or read-only
- No "Advanced" section under agent settings

**Resolution Steps:**

1. **Verify Copilot Studio version:**
   - Agent-level session timeout requires a current version of Copilot Studio
   - Check that your tenant has the latest Copilot Studio updates applied

2. **Verify license requirements:**
   - Agent-level session configuration requires a Copilot Studio license with the appropriate capabilities
   - Confirm the maker account has a valid Copilot Studio license assigned

3. **Check UI path changes:**
   - The session timeout setting location may vary by Copilot Studio version
   - Try: **Settings** → **Advanced** → **Session timeout**
   - Alternative path: **Settings** → **Generative AI** → **Session management**
   - Use the in-portal search to locate "session timeout" if neither path works

4. **For classic bots vs. modern agents:**
   - Classic Power Virtual Agents bots may have the setting under a different navigation path
   - Modern Copilot Studio agents use the updated settings structure

**Root Cause:** Copilot Studio UI evolves across releases; session timeout settings may appear under different navigation paths depending on the portal version and agent type.

---

### Issue 11: Session Expiration Not Applying as Expected

**Symptoms:**

- Session expiration (maximum session lifetime) configured in PPAC but sessions persist beyond the configured maximum duration
- Users report being able to work continuously beyond the session expiration limit
- Session expiration shows as enabled in PPAC but does not terminate active sessions at the expected time

**Resolution Steps:**

1. **Verify the setting is correctly configured:**
   - Navigate to PPAC → Environment → Settings → Privacy + Security → Session Expiration
   - Confirm **Set custom session timeout** is set to **On**
   - Confirm the **Maximum Session Length** value is within zone limits (Zone 2: ≤1440 min, Zone 3: ≤720 min)

2. **Understand session expiration behavior:**
   - Like inactivity timeout, session expiration applies to new sessions — existing sessions retain their original expiration from session creation
   - Users must sign out and sign back in for the new session expiration to apply

3. **Distinguish from inactivity timeout:**
   - Session expiration enforces an absolute maximum duration regardless of activity
   - Inactivity timeout terminates sessions after a period of no activity
   - Both settings operate independently; whichever threshold is reached first triggers session termination

4. **Verify via BAP Admin API:**
   - Query the environment's privacy settings using the diagnostic commands in the [Diagnostic Commands](#diagnostic-commands) section
   - Confirm the session expiration properties are present and correctly configured in the API response

**Root Cause:** Session expiration settings apply at session creation. Existing sessions are not retroactively updated when the setting changes.

---

### Issue 12: ISO 8601 Duration Parsing Error

**Symptoms:**

- Error log entry with error type = `ParseError`
- Compliance status shows **Unknown** for an environment that has a valid policy record
- Flow run history shows the `Parse_Duration_Minutes` compose action failed or produced an unexpected result
- `fsi_inactivitytimeouterrorlog` contains an entry for the environment with a non-null `fsi_errorraw` value

**Resolution Steps:**

1. **Identify the raw duration string:**
   - Open `fsi_inactivitytimeouterrorlog` in Power Apps → Tables
   - Find the error record for the affected environment
   - Check the `fsi_errorraw` column for the actual duration string returned by the BAP API

2. **Verify the format is unsupported:**
   - Supported formats: `PTnM` (e.g., `PT60M`), `PTnH` (e.g., `PT2H`), `PTnHnM` (e.g., `PT1H30M`)
   - Unsupported examples: `P1D` (days), `PT30S` (seconds only), `P1Y` (years)

3. **If the format is unsupported:**
   - This is a platform behavior from the BAP Admin API returning a non-standard duration format
   - Do not modify the flow's inline parsing expression
   - Open a Microsoft support ticket referencing the environment name and the raw duration value; include the BAP API endpoint `providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{name}/settings/privacy`

4. **If the format appears valid but still fails:**
   - Check for leading/trailing whitespace or null characters in `fsi_errorraw`
   - Verify the flow's `Parse_Duration_Minutes` compose expression matches the current supported formats in [SOLUTION-DOCUMENTATION.md Appendix: ISO 8601 Duration Parsing](https://github.com/judeper/FSI-AgentGov-Solutions/blob/main/inactivity-timeout-enforcement/SOLUTION-DOCUMENTATION.md)

**Root Cause:** The BAP Admin API returned an inactivity timeout duration in a format not handled by the flow's ISO 8601 parser (e.g., `P1D` for 1 day instead of `PT1440M`). This is a platform behavior — the flow cannot automatically handle all possible ISO 8601 variants.

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
| BAP Admin API rate limiting | Large tenant scans may be throttled | Reduce concurrency; schedule off-peak; implement exponential backoff; honor `Retry-After` header |
| No per-app timeout granularity | Timeout is environment-level, not per-application | Use separate environments for different timeout requirements |
| Developer/trial environments | May have restricted API access | Exclude from automated scanning or use manual verification |

---

## Diagnostic Commands

!!! note "Authentication Required"
    The diagnostic commands below require an authenticated session and a valid BAP API token. Obtain a token before running any commands:

    ```powershell
    Connect-AzAccount  # If not already authenticated
    # Az.Accounts <4.x returns plain string; >=4.x returns SecureString
    $tokenResult = Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com"
    if ($tokenResult.Token -is [securestring]) {
        $token = $tokenResult.Token | ConvertFrom-SecureString -AsPlainText
    } else {
        $token = $tokenResult.Token
    }
    ```

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

$results = foreach ($env in $envList.value) {
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
}
$results | Format-Table -AutoSize
```

---

## Next Steps

- [Portal Walkthrough](portal-walkthrough.md) — Manual PPAC configuration
- [PowerShell Setup](powershell-setup.md) — Automated remediation
- [Verification & Testing](verification-testing.md) — Compliance validation

---

*Updated: February 2026 | Version: v1.3*
