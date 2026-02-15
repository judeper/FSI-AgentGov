# Portal Walkthrough: Control 2.22 - Inactivity Timeout Enforcement

> **Parent Control:** [2.22 - Inactivity Timeout Enforcement](../../../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md)

**Last Updated:** February 2026
**Portal:** Power Platform Admin Center (PPAC)
**Estimated Time:** 30-45 minutes per environment

## Prerequisites

- [ ] Power Platform Admin or Environment Admin role assigned
- [ ] Access to Power Platform Admin Center ([admin.powerplatform.microsoft.com](https://admin.powerplatform.microsoft.com))
- [ ] Environment governance zone assignments documented (Zone 1/2/3)
- [ ] Approved timeout duration values per zone policy

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

## Post-Configuration

After configuring all environments:

1. Update the `fsi_environmentpolicy` Dataverse table to reflect current zone assignments and required maximum durations
2. Run the Detect-InactivityTimeout-NonCompliance flow manually to validate initial compliance state
3. Review compliance records in the `fsi_inactivitytimeout_compliance` table to confirm all environments show Compliant status
4. Address any Non-Compliant or Unknown results before enabling the daily schedule
5. Verify the following environment variables are configured in the governance Dataverse environment:

| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `fsi_ITE_ConcurrencyLimit` | Decimal | 5 | Max parallel environment evaluations in the compliance flow |
| `fsi_ITE_NotificationRecipients` | String | (empty) | Email addresses for non-compliance alerts — must be set for notifications to send |
| `fsi_ITE_ScanFrequencyHours` | Decimal | 24 | Scan interval in hours for the daily compliance schedule |

!!! warning "Notification Recipients Required"
    The `fsi_ITE_NotificationRecipients` variable defaults to empty. Set this value before enabling the daily schedule or non-compliance alerts will not be delivered.

---

## Next Steps

- [PowerShell Setup](powershell-setup.md) — Automated remediation with Set-InactivityTimeout.ps1
- [Verification & Testing](verification-testing.md) — Compliance validation and evidence collection
- [Troubleshooting](troubleshooting.md) — Common issues and resolutions

---

*Updated: February 2026 | Version: v1.3*
