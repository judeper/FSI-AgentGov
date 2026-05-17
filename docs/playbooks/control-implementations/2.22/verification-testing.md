# Verification & Testing: Control 2.22 - Inactivity Timeout Enforcement

> **Parent Control:** [2.22 - Inactivity Timeout Enforcement](../../../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md)

**Last Updated:** April 2026
**Test Environment:** Power Platform Admin Center, BAP Admin API, Dataverse
**Estimated Time:** 1-2 hours

## Prerequisites

- [ ] Control 2.22 implementation complete (portal walkthrough)
- [ ] `fsi_environmentpolicy` table populated with zone assignments
- [ ] Detect-InactivityTimeout-NonCompliance flow deployed
- [ ] Set-InactivityTimeout.ps1 script available (located at `scripts/governance/Set-InactivityTimeout.ps1` in the FSI-AgentGov repository)
- [ ] Test environments available (at least one per zone)
- [ ] Power Platform Admin or Environment Admin credentials (Environment Admin is limited to assigned environments)
- [ ] Authenticated Azure session via `Connect-AzAccount` (required for PowerShell test cases TC-2.22-05 through TC-2.22-10)

---

## Test Cases

### TC-2.22-01: Compliant Environment Detection

**Objective:** Verify the compliance flow correctly identifies a properly configured environment.

**Steps:**

1. Select a Zone 3 test environment
2. Configure inactivity timeout to 30 minutes (within the 60-minute Zone 3 maximum)
3. Ensure the environment has a corresponding `fsi_environmentpolicy` record with `fsi_requiredmaxduration` = 60
4. Run the Detect-InactivityTimeout-NonCompliance flow manually
5. Check the `fsi_inactivitytimeoutcompliance` table for the scan result

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
5. Check the `fsi_inactivitytimeoutcompliance` table for the scan result

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
5. Check the `fsi_inactivitytimeoutcompliance` table for the scan result

**Expected Result:** Compliance record created with status = Non-Compliant; reason indicates timeout is disabled.

**Evidence:** Screenshot of compliance record showing Non-Compliant status with "timeout disabled" reason.

---

### TC-2.22-04: Unknown Status — Missing Policy Record

**Objective:** Verify environments without a policy record receive Unknown compliance status.

**Steps:**

1. Select a test environment that does NOT have a record in the `fsi_environmentpolicy` table
2. Run the Detect-InactivityTimeout-NonCompliance flow manually
3. Check the `fsi_inactivitytimeouterrorlog` table for a MissingPolicy entry
4. Query the `fsi_inactivitytimeoutcompliance` table, filtering by the test environment's EnvironmentName
5. Verify the compliance record shows compliance status = Unknown
6. Verify the error log contains an entry with error type = MissingPolicy for this environment

**Expected Result:** Compliance record created with status = Unknown; error log entry created with error type = MissingPolicy.

**Evidence:** Screenshot of error log entry showing MissingPolicy error type.

---

### TC-2.22-05: Remediation Script — WhatIf Preview

**Objective:** Verify the PowerShell remediation script correctly previews changes without modifying the environment.

**Steps:**

1. Select a non-compliant test environment (e.g., Zone 3 with timeout at 120 minutes)
2. Run `.\Set-InactivityTimeout.ps1 -EnvironmentName <name> -TimeoutDuration 60 -WhatIf -Verbose`
3. Verify the Verbose output shows current and proposed values (the `-Verbose` flag is required to see the comparison details)
4. Verify no actual change was made by re-checking PPAC settings or re-running the compliance flow

**Expected Result:** Script outputs preview with current and proposed values; no actual configuration change applied.

**Evidence:** Screenshot of WhatIf output showing current vs. proposed values.

---

### TC-2.22-06: Remediation Script — Apply Fix

**Objective:** Verify the PowerShell remediation script successfully reconfigures an environment.

**Steps:**

1. Select a non-compliant test environment (e.g., Zone 3 with timeout at 120 minutes)
2. Run `.\Set-InactivityTimeout.ps1 -EnvironmentName <name> -TimeoutDuration 60`
3. Verify the script completes without errors
4. Navigate to PPAC → Environment → Settings → Privacy + Security
5. Confirm the timeout duration now shows 60 minutes
6. Run the compliance flow manually to generate a new compliance record
7. Verify the new compliance record shows status = Compliant

**Expected Result:** Environment timeout updated to 60 minutes; subsequent compliance scan shows Compliant.

**Evidence:** Screenshots of (a) successful script output, (b) PPAC showing updated timeout, (c) Compliant compliance record.

---

### TC-2.22-07: Agent-Level Session Timeout Configuration (Zone 3)

**Objective:** Verify agent-level conversation session timeout is configured correctly for Zone 3 agents.

**Steps:**

1. Select a Zone 3 agent that processes customer data or PII
2. Navigate to Copilot Studio → select the agent → Settings → Advanced → Session timeout
3. Verify the conversation session timeout is set to ≤60 minutes
4. Verify the timeout setting is documented in the organization's agent inventory (Control 3.1)

**Expected Result:** Agent-level session timeout ≤60 minutes for Zone 3 agents; setting documented in agent inventory.

**Evidence:** Screenshot of agent session timeout configuration in Copilot Studio; agent inventory export showing the timeout setting.

---

### TC-2.22-08: Agent-Level Timeout Evidence for Audit

**Objective:** Verify agent owners can produce evidence of agent-level timeout configuration during audit reviews.

**Steps:**

1. Select a Zone 2 or Zone 3 agent
2. Request the agent owner to produce configuration evidence (screenshot or API response showing session timeout setting)
3. Verify the evidence includes: agent name, timeout duration, configuration date
4. Verify the evidence matches the agent inventory record

**Expected Result:** Agent owner produces timestamped evidence showing agent-level session timeout configuration matching inventory records.

**Evidence:** Agent configuration screenshot or API response with timestamp.

---

### TC-2.22-09: Remediation Script with Evidence Hash

**Objective:** Verify the PowerShell remediation script produces valid evidence with integrity hash.

**Steps:**

1. Run `.\Set-InactivityTimeout.ps1 -EnvironmentName <name> -TimeoutDuration 60 -IncludeEvidence -OutputFormat JSON -OutputPath .\evidence\test-hash.json`
2. Verify the output JSON file contains a non-null `Metadata.IntegrityHash` field
3. Run the [evidence hash verification procedure](powershell-setup.md#evidence-hash-verification) from the PowerShell Setup playbook
4. Verify the computed hash matches the recorded hash

**Expected Result:** Evidence file produced with SHA-256 integrity hash; verification procedure confirms hash match.

**Evidence:** JSON evidence file with integrity hash; verification script output showing "Evidence integrity verified".

---

### TC-2.22-10: Bulk Remediation from CSV

**Objective:** Verify bulk remediation via CSV import works correctly across multiple environments.

**Steps:**

1. Create a CSV file with columns `EnvironmentName,TimeoutDuration` containing at least 2 test environments
2. Run `Import-Csv .\test-environments.csv | ForEach-Object { .\Set-InactivityTimeout.ps1 -EnvironmentName $_.EnvironmentName -TimeoutDuration ([int]$_.TimeoutDuration) -WhatIf }`
3. Verify WhatIf output shows preview for each environment
4. Run without -WhatIf to apply changes
5. Run the compliance flow manually to verify all environments show Compliant

**Expected Result:** All environments remediated successfully; subsequent compliance scan confirms Compliant status for each.

**Evidence:** Bulk remediation output logs; compliance scan results.

---

### TC-2.22-11: Session Expiration Configuration Verification

**Objective:** Verify session expiration (maximum session lifetime) is configured correctly for the environment's zone classification.

**Steps:**

1. Select a Zone 3 test environment
2. Navigate to PPAC → Environment → Settings → Privacy + Security → Session Expiration
3. Verify **Set custom session timeout** is set to **On**
4. Verify the **Maximum Session Length** is set to ≤720 minutes for Zone 3 (or ≤1440 minutes for Zone 2)
5. Repeat for a Zone 2 environment and confirm the maximum session lifetime is ≤1440 minutes

**Expected Result:** Session expiration enabled with maximum lifetime within zone-specific limits (Zone 2: ≤1440 minutes, Zone 3: ≤720 minutes).

**Evidence:** Screenshot of PPAC Privacy + Security settings showing session expiration configuration for each governed environment.

---

## Evidence Checklist

Collect the following evidence for audit documentation:

| # | Evidence Item | Format | Collected |
|---|--------------|--------|-----------|
| 1 | PPAC Privacy + Security settings for each governed environment | Screenshot | [ ] |
| 2 | `fsi_environmentpolicy` table export showing zone assignments | CSV/Screenshot | [ ] |
| 3 | Compliance scan results from `fsi_inactivitytimeoutcompliance` table | CSV/Screenshot | [ ] |
| 4 | Flow run history showing successful daily execution | Screenshot | [ ] |
| 5 | Error log entries (if any) from `fsi_inactivitytimeouterrorlog` table | CSV/Screenshot | [ ] |
| 6 | Remediation script execution logs with before/after values | Text/Screenshot | [ ] |
| 7 | Evidence hash verification output for remediation records | JSON + Console | [ ] |
| 8 | Agent-level session timeout configuration screenshots from Copilot Studio | Screenshot | [ ] |
| 9 | Agent inventory export showing agent-level timeout settings for Zone 2/3 agents | CSV/Screenshot | [ ] |
| 10 | Session expiration (maximum session lifetime) configuration for each governed environment | Screenshot | [ ] |
| 11 | Evidence export to retention-managed location (e.g., Purview-protected SharePoint, immutable Azure Storage) for SEC 17a-4(f) six-year retention | Export log / storage policy screenshot | [ ] |

---

## Evidence Retention (SEC 17a-4(f))

For broker-dealer organizations subject to SEC 17a-4 record-keeping rules, compliance scan results, error logs, and remediation evidence collected for Control 2.22 should be treated as books and records when they are used to demonstrate supervisory or system-access controls. Key retention expectations:

| Requirement | Expectation | Implementation Option |
|-------------|-------------|----------------------|
| Retention period | At least six years from creation; first two years readily accessible | Schedule periodic exports of `fsi_inactivitytimeoutcompliance` and `fsi_inactivitytimeouterrorlog` to a retention-managed store |
| Storage format | Non-rewriteable, non-erasable (WORM) for affected broker-dealer evidence | Purview retention labels with record-locking; Azure Storage immutable blob policies; SharePoint libraries with retention-lock policies |
| Integrity | Tamper-evident records | SHA-256 hashes from `Set-InactivityTimeout.ps1 -IncludeEvidence`; combine with WORM storage |
| Indexing / retrievability | Records must be locatable on request | Maintain an index by environment name, scan date, and remediation date |

!!! warning "Scope and Counsel Review"
    Whether Control 2.22 evidence falls within SEC 17a-4(f) scope depends on each organization's books-and-records determinations. Coordinate with the Compliance Officer and counsel to confirm classification before designing the retention pipeline. The patterns above are common implementations and do not constitute legal advice.

---

## Attestation Template

!!! note "Scope"
    This attestation covers key operational criteria. For comprehensive verification, confirm all 10 criteria from the [Control 2.22 Verification Criteria](../../../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md#verification-criteria) section.

```
I, [Name], [Title], confirm that:

1. Control 2.22 (Inactivity Timeout Enforcement) has been configured for all
   Zone 2 and Zone 3 Power Platform environments under governance.

2. All governed environments have inactivity timeout durations within
   zone-specific maximum limits (Zone 2: ≤120 min, Zone 3: ≤60 min).

3. The Detect-InactivityTimeout-NonCompliance flow is operational and
   producing daily compliance records in Dataverse.

4. Remediation procedures have been tested and documented.

5. Agent-level conversation session timeout settings are documented in
   the agent inventory (Control 3.1) for all Zone 2 and Zone 3 agents.

6. Zone 3 agents processing customer data, PII, or PHI have conversation
   session timeout configured at ≤60 minutes.

7. The compliance flow runs on a daily schedule and produces immutable
   (append-only) compliance records in Dataverse.

8. No governed environments have remained in Unknown compliance status
   for more than one review cycle without investigation.

9. All remediation actions are documented with before/after configuration
   values and SHA-256 evidence hashes where applicable.

10. Compliance records, error logs, and remediation evidence are exported to
    a retention-managed location aligned with the organization's books-and-
    records determinations under SEC 17a-4(f) (six-year retention; first two
    years readily accessible) where applicable to broker-dealer scope.

Date: _______________
Signature: _______________
```

---

## Next Steps

- [Portal Walkthrough](portal-walkthrough.md) — Initial PPAC configuration
- [PowerShell Setup](powershell-setup.md) — Automated remediation
- [Troubleshooting](troubleshooting.md) — Common issues and resolutions

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
