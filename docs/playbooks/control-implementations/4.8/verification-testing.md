# Control 4.8: Verification & Testing — Item-Level Permission Scanning for Agent Knowledge Sources

> **Parent Control:** [Control 4.8 — Item-Level Permission Scanning](../../../controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md)
>
> **Related Playbooks:** [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

## Overview

This playbook provides test procedures, expected results, and evidence collection guidance for verifying that Control 4.8 is operating effectively. Use these procedures for initial validation, ongoing compliance monitoring, and regulatory examination preparation.

---

## Test Procedures

### Test 1: Agent Knowledge Source Inventory Completeness

**Objective:** Verify all agent knowledge sources are identified and documented.

**Steps:**

1. Export the agent knowledge source inventory from the scanning tool or manual documentation
2. Cross-reference against the Copilot Studio agent list (all environments)
3. Verify each agent's knowledge sources are captured

**Expected Results:**

- [ ] Every deployed Copilot Studio agent with SharePoint knowledge sources is listed
- [ ] Each knowledge source entry includes: Agent Name, Environment, Site URL, Library Path, Files Count
- [ ] No agent knowledge sources are missing from the inventory
- [ ] Inventory is dated within the last 30 days

---

### Test 2: Item-Level Scan Execution

**Objective:** Verify item-level permission scan completes successfully on all knowledge source libraries.

**Steps:**

1. Run `Get-KnowledgeSourceItemPermissions.ps1` against each knowledge source library
2. Verify scan completes without errors
3. Review scan output CSV for completeness

**Expected Results:**

- [ ] Scan completes for every identified knowledge source library
- [ ] Output CSV contains all expected columns: SiteUrl, LibraryName, ItemId, FileName, FilePath, SensitivityLabel, SharingScopes, RiskLevel, HasUniquePerms, ScannedDate
- [ ] Total items scanned matches the known item count for each library (within tolerance)
- [ ] Risk classification is applied to all items with unique permissions
- [ ] Scan duration is within acceptable limits (varies by library size)

---

### Test 3: CRITICAL Item Identification

**Objective:** Verify CRITICAL items are correctly identified and flagged.

**Steps:**

1. In a dedicated **non-production** test SharePoint site connected to a test agent, create a test item:
   - Apply a "Confidential" or "Highly Confidential" sensitivity label
   - Share with "Everyone except external users" or create an "Anyone" link
2. Wait for label sync (up to 24 hours per Microsoft Learn) before scanning
3. Run the item-level scan against the test library
4. Verify the test item appears as CRITICAL in scan output

**Expected Results:**

- [ ] Test item with Confidential label + broad sharing is classified as CRITICAL
- [ ] CRITICAL items are listed first in scan output (sorted by risk)
- [ ] Sensitivity label and sharing scope details are accurately captured
- [ ] No false negatives — all items matching CRITICAL criteria are flagged

!!! warning "Test environment only"
    Use a dedicated test site and test agent for this test. Do not create overshared sensitive content in production libraries. Per Microsoft Learn, Copilot Studio does not index Confidential / Highly Confidential items as knowledge sources, so the test item should not actually be served by the agent — but the SharePoint-level oversharing must still be detected and remediated.

---

### Test 4: Pre-Deployment Gate Enforcement

**Objective:** Verify that agents cannot deploy to production when CRITICAL items exist.

**Steps:**

1. Run scan on a knowledge source library with known CRITICAL items
2. Verify the compliance report shows "BLOCKED" status
3. Remediate the CRITICAL items (remove sharing or restrict permissions)
4. Re-run scan and verify "CLEARED" status
5. Verify agent deployment documentation includes pre-deployment gate sign-off

**Expected Results:**

- [ ] Pre-deployment gate correctly blocks deployment when CRITICAL items exist
- [ ] Gate status changes to CLEARED after remediation
- [ ] Deployment documentation includes the scan report and gate clearance
- [ ] Gate enforcement is documented in the governance process

---

### Test 5: Remediation SLA Compliance

**Objective:** Verify remediation actions complete within defined SLAs.

**Steps:**

1. Review remediation log for the past 90 days
2. Compare remediation completion timestamps against detection timestamps
3. Calculate SLA compliance for each risk level

**Expected Results:**

- [ ] CRITICAL items: remediated within 4 hours of detection (100% compliance)
- [ ] HIGH items: remediated within 24 hours of detection (≥95% compliance)
- [ ] MEDIUM items: remediated within 5 business days (≥90% compliance)
- [ ] All remediation actions are documented with evidence

---

### Test 6: Recurring Scan Schedule

**Objective:** Verify monthly recurring scans are configured and executing.

**Steps:**

1. Check scan schedule configuration (Task Scheduler / Azure Automation / Power Automate)
2. Review scan execution history for the past 3 months
3. Verify scan output files exist for each scheduled execution

**Expected Results:**

- [ ] Monthly scan schedule is configured and active
- [ ] Scan has executed on schedule for each of the past 3 months
- [ ] Each execution produced a complete output CSV
- [ ] No missed scan cycles without documented exception

---

### Test 7: Evidence Retention Compliance

**Objective:** Verify scan output is retained for the required 7-year period.

**Steps:**

1. Review storage configuration for scan output files
2. Verify retention policy is applied (7 years / 2,555 days)
3. Confirm oldest available scan output
4. Check that scan outputs cannot be modified or deleted within retention period

**Expected Results:**

- [ ] Scan output storage has a 7-year retention policy applied
- [ ] Outputs are stored in an immutable or write-once-read-many (WORM) location
- [ ] Retention applies to all scan artifacts: CSV files, compliance reports, remediation logs
- [ ] Evidence chain is maintained from scan through remediation to sign-off

---

## Zone-Specific Verification

### Zone 1 — Personal Productivity

| Verification Item | Required | Method |
|-------------------|----------|--------|
| Knowledge source inventory | ✓ | Manual review |
| Item-level scan execution | Recommended | Script or manual |
| CRITICAL item remediation | ✓ | Review scan output |
| Recurring scan schedule | Quarterly | Check schedule |
| Evidence retention | 7 years | Check storage |

### Zone 2 — Team Collaboration

| Verification Item | Required | Method |
|-------------------|----------|--------|
| Knowledge source inventory | ✓ | Script export |
| Item-level scan execution | ✓ | Automated scan |
| CRITICAL item remediation | ✓ | Review + SLA check |
| HIGH item remediation | ✓ | Review + SLA check |
| Recurring scan schedule | Monthly | Check schedule |
| Pre-deployment gate | ✓ | Review deployment docs |
| Evidence retention | 7 years | Check storage + retention policy |

### Zone 3 — Enterprise Managed

| Verification Item | Required | Method |
|-------------------|----------|--------|
| Knowledge source inventory | ✓ | Automated inventory + manual validation |
| Item-level scan execution | ✓ | Automated scan with attestation |
| CRITICAL item remediation | ✓ | Review + SLA check (100% within 4 hours) |
| HIGH item remediation | ✓ | Review + SLA check (≥95% within 24 hours) |
| MEDIUM item remediation | ✓ | Review + SLA check (≥90% within 5 days) |
| Recurring scan schedule | Monthly + on-demand | Check schedule + alert triggers |
| Pre-deployment gate | ✓ (mandatory, no exceptions) | Review deployment docs + gate log |
| Compliance dashboard integration | ✓ | Verify dashboard displays 4.8 data |
| Evidence retention | 7 years (immutable) | Check WORM storage + retention policy |

---

## Evidence Types

| Evidence Type | Description | Retention | Format |
|---------------|-------------|-----------|--------|
| **Scan Output CSV** | Raw item-level permission scan results | 7 years | CSV |
| **Compliance Report** | Formatted risk summary with gate status | 7 years | Markdown/PDF |
| **Remediation Log** | Actions taken to resolve findings with timestamps | 7 years | CSV/Log |
| **Pre-Deployment Gate Sign-off** | Documented gate clearance with approver | 7 years | PDF/Email |
| **Scan Schedule Configuration** | Screenshot or export of recurring schedule | Current + 1 year | Screenshot/Export |
| **Audit Log Cross-Reference** | SharePoint unified audit log entries (`FileAccessed`, `FileDownloaded`) for agent-served libraries — used to support SEC 17a-4 record-keeping where Copilot Studio transcripts do not capture SharePoint-grounded responses | 7 years | CSV/JSON export |
| **Configuration File** | `item-scope-config.json` version in use | With each scan | JSON |

---

## Compliance Attestation Template

Use this template for quarterly governance attestation:

```
========================================
CONTROL 4.8 COMPLIANCE ATTESTATION
Item-Level Permission Scanning for Agent Knowledge Sources
========================================

Attestation Period: [Start Date] to [End Date]
Prepared By:        [Name / Role]
Reviewed By:        [Name / Role]
Date:               [YYYY-MM-DD]

CONFIGURATION STATUS
--------------------
[ ] All agent knowledge sources identified and inventoried
[ ] Item-level scan configured with current sensitivity labels
[ ] Pre-deployment gate enforced for all new agent deployments
[ ] Monthly recurring scan schedule active
[ ] Compliance dashboard integration operational

SCAN EXECUTION SUMMARY
-----------------------
Total scans executed this period:     ____
Total libraries scanned:               ____
Total items scanned:                   ____
CRITICAL findings detected:            ____
CRITICAL findings remediated:          ____ (within SLA: ____%)
HIGH findings detected:                ____
HIGH findings remediated:              ____ (within SLA: ____%)
MEDIUM findings detected:              ____
MEDIUM findings remediated:            ____ (within SLA: ____%)

PRE-DEPLOYMENT GATE
--------------------
Agents evaluated:                      ____
Agents cleared for deployment:         ____
Agents blocked (CRITICAL findings):    ____
Blocked agents remediated:             ____

EVIDENCE COLLECTION
-------------------
| Evidence Type        | Location           | Retention Verified |
|---------------------|--------------------|-------------------|
| Scan Output CSV     | [path/location]    | [ ] Yes  [ ] No   |
| Compliance Reports  | [path/location]    | [ ] Yes  [ ] No   |
| Remediation Logs    | [path/location]    | [ ] Yes  [ ] No   |
| Gate Sign-offs      | [path/location]    | [ ] Yes  [ ] No   |

FINDINGS & REMEDIATION
-----------------------
[Document any findings, exceptions, or remediation actions]

ATTESTATION
-----------
I attest that Control 4.8 has been operating effectively during the
attestation period and all scan evidence has been retained per policy.

AI Governance Lead:   ________________________  Date: ________
SharePoint Admin:     ________________________  Date: ________
Compliance Officer:   ________________________  Date: ________
```

---

## PowerShell Validation Scripts

### Quick Validation

```powershell
# Quick validation of Control 4.8 implementation
Write-Host "=== Control 4.8 Validation ===" -ForegroundColor Cyan

# Check 1: Scan output exists
$OutputPath = "./output"
$ScanFiles = Get-ChildItem -Path $OutputPath -Filter "item-permissions-scan-*.csv" -ErrorAction SilentlyContinue
Write-Host "Scan output files found: $($ScanFiles.Count)" -ForegroundColor $(if ($ScanFiles.Count -gt 0) { "Green" } else { "Red" })

# Check 2: Most recent scan is within 30 days
if ($ScanFiles) {
    $LatestScan = $ScanFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $DaysSinceLastScan = (New-TimeSpan -Start $LatestScan.LastWriteTime -End (Get-Date)).Days
    Write-Host "Days since last scan: $DaysSinceLastScan" -ForegroundColor $(if ($DaysSinceLastScan -le 30) { "Green" } else { "Red" })
}

# Check 3: No unresolved CRITICAL items
if ($ScanFiles) {
    $LatestResults = Import-Csv -Path $LatestScan.FullName
    $CriticalCount = ($LatestResults | Where-Object { $_.RiskLevel -eq "CRITICAL" }).Count
    Write-Host "Unresolved CRITICAL items: $CriticalCount" -ForegroundColor $(if ($CriticalCount -eq 0) { "Green" } else { "Red" })
}

# Check 4: Recurring schedule configured
$ScheduledTask = Get-ScheduledTask -TaskName "AgentKnowledgeSourceScan-Monthly" -ErrorAction SilentlyContinue
Write-Host "Monthly scan scheduled: $(if ($ScheduledTask) { 'Yes' } else { 'No' })" -ForegroundColor $(if ($ScheduledTask) { "Green" } else { "Yellow" })

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
