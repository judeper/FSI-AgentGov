# Verification Testing: Control 2.22 - Inactivity Timeout Enforcement

**Last Updated:** February 2026
**Test Environment:** Power Platform Admin Center, BAP Admin API, Dataverse
**Estimated Time:** 1-2 hours

## Prerequisites

- [ ] Control 2.22 implementation complete (portal walkthrough)
- [ ] `fsi_environmentpolicy` table populated with zone assignments
- [ ] Detect-InactivityTimeout-NonCompliance flow deployed
- [ ] Set-InactivityTimeout.ps1 script available
- [ ] Test environments available (at least one per zone)
- [ ] Power Platform Admin credentials

---

## Test Cases

### TC-2.22-01: Compliant Environment Detection

**Objective:** Verify the compliance flow correctly identifies a properly configured environment.

**Steps:**

1. Select a Zone 3 test environment
2. Configure inactivity timeout to 30 minutes (within the 60-minute Zone 3 maximum)
3. Ensure the environment has a corresponding `fsi_environmentpolicy` record with `fsi_requiredmaxduration` = 60
4. Run the Detect-InactivityTimeout-NonCompliance flow manually
5. Check the `fsi_inactivitytimeout_compliance` table for the scan result

**Expected Result:** Compliance record created with status = Compliant; timeout duration = 30; zone maximum = 60.

**Evidence:** Screenshot of compliance record showing Compliant status.

---

### TC-2.22-02: Non-Compliant Environment — Timeout Exceeds Zone Maximum

**Objective:** Verify the compliance flow detects when timeout duration exceeds the zone maximum.

**Steps:**

1. Select a Zone 2 test environment
2. Configure inactivity timeout to 180 minutes (exceeds the 120-minute Zone 2 maximum)
3. Ensure the environment has a corresponding `fsi_environmentpolicy` record with `fsi_requiredmaxduration` = 120
4. Run the Detect-InactivityTimeout-NonCompliance flow manually
5. Check the `fsi_inactivitytimeout_compliance` table for the scan result

**Expected Result:** Compliance record created with status = Non-Compliant; reason indicates duration exceeds zone maximum.

**Evidence:** Screenshot of compliance record showing Non-Compliant status with duration values.

---

### TC-2.22-03: Non-Compliant Environment — Timeout Disabled

**Objective:** Verify the compliance flow detects when inactivity timeout is disabled on a governed environment.

**Steps:**

1. Select a Zone 2 or Zone 3 test environment
2. Disable inactivity timeout in PPAC → Settings → Privacy + Security
3. Ensure the environment has a corresponding `fsi_environmentpolicy` record
4. Run the Detect-InactivityTimeout-NonCompliance flow manually
5. Check the `fsi_inactivitytimeout_compliance` table for the scan result

**Expected Result:** Compliance record created with status = Non-Compliant; reason indicates timeout is disabled.

**Evidence:** Screenshot of compliance record showing Non-Compliant status with "timeout disabled" reason.

---

### TC-2.22-04: Unknown Status — Missing Policy Record

**Objective:** Verify environments without a policy record receive Unknown compliance status.

**Steps:**

1. Select a test environment that does NOT have a record in the `fsi_environmentpolicy` table
2. Run the Detect-InactivityTimeout-NonCompliance flow manually
3. Check the `fsi_inactivitytimeout_errorlog` table for a MissingPolicy entry
4. Verify no false Compliant or Non-Compliant record is created

**Expected Result:** Error log entry with error type = MissingPolicy; compliance status = Unknown or no compliance record created.

**Evidence:** Screenshot of error log entry showing MissingPolicy error type.

---

### TC-2.22-05: Remediation Script — WhatIf Preview

**Objective:** Verify the PowerShell remediation script correctly previews changes without modifying the environment.

**Steps:**

1. Select a non-compliant test environment (e.g., Zone 3 with timeout at 120 minutes)
2. Run `Set-InactivityTimeout.ps1 -EnvironmentName <name> -TimeoutDuration 60 -WhatIf`
3. Verify the output shows current and proposed values
4. Verify no actual change was made by re-checking PPAC settings or re-running the compliance flow

**Expected Result:** Script outputs preview with current and proposed values; no actual configuration change applied.

**Evidence:** Screenshot of WhatIf output showing current vs. proposed values.

---

### TC-2.22-06: Remediation Script — Apply Fix

**Objective:** Verify the PowerShell remediation script successfully reconfigures an environment.

**Steps:**

1. Select a non-compliant test environment (e.g., Zone 3 with timeout at 120 minutes)
2. Run `Set-InactivityTimeout.ps1 -EnvironmentName <name> -TimeoutDuration 60`
3. Verify the script completes without errors
4. Navigate to PPAC → Environment → Settings → Privacy + Security
5. Confirm the timeout duration now shows 60 minutes
6. Run the compliance flow manually to generate a new compliance record
7. Verify the new compliance record shows status = Compliant

**Expected Result:** Environment timeout updated to 60 minutes; subsequent compliance scan shows Compliant.

**Evidence:** Screenshots of (a) successful script output, (b) PPAC showing updated timeout, (c) Compliant compliance record.

---

## Evidence Checklist

Collect the following evidence for audit documentation:

| # | Evidence Item | Format | Collected |
|---|--------------|--------|-----------|
| 1 | PPAC Privacy + Security settings for each governed environment | Screenshot | [ ] |
| 2 | `fsi_environmentpolicy` table export showing zone assignments | CSV/Screenshot | [ ] |
| 3 | Compliance scan results from `fsi_inactivitytimeout_compliance` table | CSV/Screenshot | [ ] |
| 4 | Flow run history showing successful daily execution | Screenshot | [ ] |
| 5 | Error log entries (if any) from `fsi_inactivitytimeout_errorlog` table | CSV/Screenshot | [ ] |
| 6 | Remediation script execution logs with before/after values | Text/Screenshot | [ ] |

---

## Attestation Template

```
I, [Name], [Title], confirm that:

1. Control 2.22 (Inactivity Timeout Enforcement) has been configured for all
   Zone 2 and Zone 3 Power Platform environments under governance.

2. All governed environments have inactivity timeout durations within
   zone-specific maximum limits (Zone 2: ≤120 min, Zone 3: ≤60 min).

3. The Detect-InactivityTimeout-NonCompliance flow is operational and
   producing daily compliance records in Dataverse.

4. Remediation procedures have been tested and documented.

Date: _______________
Signature: _______________
```

---

## Next Steps

- [Portal Walkthrough](portal-walkthrough.md) — Initial PPAC configuration
- [PowerShell Setup](powershell-setup.md) — Automated remediation
- [Troubleshooting](troubleshooting.md) — Common issues and resolutions

---

*Updated: February 2026 | Version: v1.3*
