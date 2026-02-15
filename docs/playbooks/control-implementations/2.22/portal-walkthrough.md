# Portal Walkthrough: Control 2.22 - Inactivity Timeout Enforcement

> **Parent Control:** [2.22 - Inactivity Timeout Enforcement](../../../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md)

**Last Updated:** February 2026
**Portal:** Power Platform Admin Center (PPAC)
**Estimated Time:** 30-45 minutes per environment

## Prerequisites

- [ ] CAA Dataverse schema deployed (provides the `fsi_acv_zone` global option set required by the ITE policy table). If not already deployed, run `python scripts/create_dataverse_schema.py` from the Conditional Access Automation solution first.
- [ ] ITE solution imported into the target Dataverse environment (see [Solutions Index](../../../reference/solutions-index.md#inactivity-timeout-enforcement) for components and deployment scripts)
- [ ] ITE Dataverse schema deployed via Python scripts (see [Schema Deployment](#schema-deployment) below)
- [ ] Connection references authenticated and environment variable current values set (see [Post-Import Configuration](#post-import-configuration) below)
- [ ] Power Platform Admin or Environment Admin role assigned
- [ ] Access to Power Platform Admin Center ([admin.powerplatform.microsoft.com](https://admin.powerplatform.microsoft.com))
- [ ] Environment governance zone assignments documented (Zone 1/2/3) — see [Zones and Tiers](../../../framework/zones-and-tiers.md) for classification guidance
- [ ] Approved timeout duration values per zone policy
- [ ] `fsi_environmentpolicy` table populated with zone assignments and required maximum durations for all governed environments

---

## Schema Deployment

Before configuring environment settings, deploy the ITE Dataverse schema. This creates the tables, option sets, environment variables, and connection references the compliance flow and remediation script require.

### Python Environment Setup

The schema scripts require Python 3.8+ and the `caa_client` module (shared with other FSI-AgentGov-Solutions schema scripts).

```bash
# Install Python dependencies
pip install msal requests

# The caa_client module must be on the Python path.
# It is located in scripts/caa_client.py in the FSI-AgentGov repository.
# Run scripts from the repository root, or add the scripts directory to PYTHONPATH.
```

Set authentication environment variables (or pass via CLI arguments):

| Variable | Description |
|----------|-------------|
| `CAA_TENANT_ID` | Entra ID tenant GUID |
| `CAA_ENVIRONMENT_URL` | Dataverse environment URL (e.g., `https://org12345.crm.dynamics.com`) |
| `CAA_CLIENT_ID` | App registration client ID with Dataverse permissions |
| `CAA_CLIENT_SECRET` | App registration client secret |

### Script Execution Order

Run the scripts in this order from the repository root:

```bash
# 1. Create policy and compliance tables (+ 2 solution option sets)
python scripts/create_timeout_dataverse_schema.py

# 2. Create error log table
python scripts/create_timeout_errorlog_schema.py

# 3. Create 3 environment variables (concurrency, notifications, scan frequency)
python scripts/create_timeout_environment_variables.py

# 4. Create 2 connection references (Dataverse + Power Platform Admin)
python scripts/create_timeout_connection_references.py
```

All scripts are idempotent — safe to re-run if needed. Use `--dry-run` to preview changes without making API calls.

!!! warning "CAA Schema Prerequisite"
    The first script (`create_timeout_dataverse_schema.py`) requires the `fsi_acv_zone` global option set, which is created by the CAA (Conditional Access Automation) schema script. If you see an error referencing `fsi_acv_zone`, deploy the CAA schema first: `python scripts/create_dataverse_schema.py`.

---

## Post-Import Configuration

After importing the ITE solution and deploying the schema, complete these configuration steps before running the compliance flow.

### Authenticate Connection References

1. Navigate to [Power Apps](https://make.powerapps.com) → select the governance environment
2. Open **Solutions** → select the ITE solution
3. Open **Connection References**
4. For each connection reference (`fsi_cr_dataverse_inactivitytimeout` and `fsi_cr_powerplatformforadmins_inactivitytimeout`):
   - Click the connection reference → select or create an active connection
   - Authenticate with a service account that has the required permissions

### Set Environment Variable Current Values

1. In the same ITE solution, open **Environment Variables**
2. Set the **Current Value** for each variable (Current Value overrides the Default Value for your tenant):

| Variable | Default | Action Required |
|----------|---------|-----------------|
| `fsi_ITE_ConcurrencyLimit` | 5 | Adjust if your tenant has many environments (reduce for rate-limit avoidance) |
| `fsi_ITE_NotificationRecipients` | *(empty)* | **Must set** — enter email addresses for compliance alert recipients |
| `fsi_ITE_ScanFrequencyHours` | 24 | Adjust scan interval if needed |

!!! warning "Notification Recipients Required"
    The `fsi_ITE_NotificationRecipients` variable has no default value. Notifications will not be sent until you set a current value with valid email addresses.

### Populate Policy Table

1. Navigate to [Power Apps](https://make.powerapps.com) → select the governance environment
2. Open **Tables** → search for `fsi_environmentpolicy`
3. Create a record for each governed environment:

| Column | Description | Example |
|--------|-------------|---------|
| `fsi_name` | Descriptive name (required primary name) | "Production" |
| `fsi_environmentid` | Canonical EnvironmentName GUID from PPAC | "d1234567-abcd-ef01-2345-6789abcdef01" |
| `fsi_environmentdisplayname` | Human-readable name (optional) | "Production" |
| `fsi_zone` | Zone classification | Zone 2 or Zone 3 |
| `fsi_requiredmaxduration` | Maximum allowed timeout in minutes | 120 (Zone 2) or 60 (Zone 3) |

!!! tip "Finding the EnvironmentName GUID"
    Open PPAC → Environments → select the environment → the EnvironmentName GUID is visible in the browser URL bar. Do NOT use the display name.

---

## Step 1: Navigate to Environment Settings

1. Sign in to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Select **Environments** from the left navigation
3. Select the target environment from the list
4. Click **Settings** in the command bar

---

## Step 2: Open Privacy + Security Settings

1. Under **Product**, expand the settings categories
2. Select **Privacy + Security**
3. The Privacy + Security settings page opens with session timeout options

!!! note "Environment Admin Access"
    Environment Admins can access these settings for their assigned environments. Power Platform Admins have access across all environments.

---

## Step 3: Enable Inactivity Timeout

1. Locate the **Session Expiration** section
2. Set **Set inactivity timeout** to **On**
3. This enables the timeout duration and warning duration fields

---

## Step 4: Configure Timeout Duration

1. Set the **Duration of inactivity before timeout** value according to the environment's zone policy:

| Zone | Maximum Duration | Recommended Setting |
|------|-----------------|---------------------|
| Zone 1 (Personal) | Optional; ≤120 min if enabled | 120 minutes |
| Zone 2 (Team) | ≤120 minutes (required) | 90 minutes |
| Zone 3 (Enterprise) | ≤60 minutes (required) | 30 minutes |

2. Set the **Warning duration before timeout** to provide users advance notice (typically 5-10 minutes before timeout)

!!! warning "Zone Maximum Enforcement"
    The timeout duration value must not exceed the zone-specific maximum defined in your organization's `fsi_environmentpolicy` table. Exceeding the maximum results in a Non-Compliant status during automated scanning.

---

## Step 5: Save Configuration

1. Click **Save** to apply the settings
2. Verify the confirmation message appears
3. The setting takes effect for new sessions; existing sessions are governed by their original timeout at creation

---

## Step 6: Verify Configuration Applied

1. Return to **Settings** → **Privacy + Security**
2. Confirm the inactivity timeout toggle shows **On**
3. Confirm the duration value matches the intended setting
4. Document the environment name, timeout duration, and timestamp for audit evidence

---

## Step 7: Repeat for All Governed Environments

1. Return to the **Environments** list
2. Select the next environment requiring timeout configuration
3. Repeat Steps 2-6 for each environment
4. Use the governance settings tracker below to record progress

### Governance Settings Tracker

| Environment Name | Zone | Required Max (min) | Configured Duration (min) | Warning (min) | Date Configured | Configured By |
|-----------------|------|-------------------|--------------------------|--------------|----------------|---------------|
| *env-prod-01* | Zone 3 | 60 | *30* | *5* | *YYYY-MM-DD* | *Admin Name* |
| *env-team-collab* | Zone 2 | 120 | *90* | *10* | *YYYY-MM-DD* | *Admin Name* |
| *env-personal-dev* | Zone 1 | N/A | *120* | *10* | *YYYY-MM-DD* | *Admin Name* |

---

## Step 8: Configure Agent-Level Session Timeout

In addition to environment-level timeout settings, individual Copilot Studio agents have conversation session timeout configurations that control when agent conversation context expires. Configuring agent-level timeouts supports defense-in-depth session security across both platform and agent layers.

1. Navigate to [Copilot Studio](https://copilotstudio.microsoft.com) and sign in with your Power Platform Admin or Copilot Studio maker credentials
2. Select the target agent from the agent list
3. Go to **Settings** → **Advanced** → **Session timeout**
4. Set the conversation session timeout duration aligned with the agent's zone classification:

| Zone | Agent-Level Maximum | Recommended Setting | Rationale |
|------|---------------------|---------------------|-----------|
| Zone 3 (Enterprise) | ≤60 minutes (required) | 30 minutes | Helps protect high-sensitivity conversation data (customer data, PII, PHI) from extended exposure in abandoned sessions |
| Zone 2 (Team) | ≤120 minutes (required) | 90 minutes | Supports session security for team collaboration agents processing organizational data |
| Zone 1 (Personal) | Optional; ≤120 min if enabled | 120 minutes | Recommended if the agent processes any sensitive organizational data |

5. Click **Save** to apply the agent-level timeout setting
6. Document the agent name, configured timeout duration, and zone classification in your organization's agent inventory (Control 3.1) for audit trail purposes. If you have not yet implemented Control 3.1, record this information in a spreadsheet for later migration to the inventory system.
7. Repeat for each governed agent in the environment

!!! note "Quarterly Review Coordination"
    Agent-level timeout settings should be reviewed during quarterly agent configuration reviews, coordinated with the Control 1.27 review cadence. This periodic review aids in maintaining alignment between agent timeout policies and evolving zone requirements.

---

## Post-Configuration Validation

After configuring all environments:

1. Verify the `fsi_environmentpolicy` Dataverse table reflects current zone assignments and required maximum durations for all configured environments

!!! warning "Required Before Running Compliance Flow"
    The `fsi_environmentpolicy` table must be populated before running the compliance flow. Environments without policy records will receive MissingPolicy errors (see [Troubleshooting Issue 1](troubleshooting.md#issue-1-compliance-flow-shows-missingpolicy-for-known-environment)).

2. Run the Detect-InactivityTimeout-NonCompliance flow manually to validate initial compliance state
3. Review compliance records in the `fsi_inactivitytimeoutcompliance` table to confirm all environments show Compliant status
4. Address any Non-Compliant or Unknown results before enabling the daily schedule
5. Enable the daily schedule trigger on the compliance flow (default: 06:00 UTC)

---

## Next Steps

- [PowerShell Setup](powershell-setup.md) — Automated remediation with Set-InactivityTimeout.ps1
- [Verification & Testing](verification-testing.md) — Compliance validation and evidence collection
- [Troubleshooting](troubleshooting.md) — Common issues and resolutions

---

*Updated: February 2026 | Version: v1.3*
