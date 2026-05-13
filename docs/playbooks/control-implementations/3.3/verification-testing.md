# Verification & Testing: Control 3.3 - Compliance and Regulatory Reporting

**Last Updated:** April 2026

> Test cases and evidence collection for [Control 3.3](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md). Designed to support FINRA cycle exams, SEC OCIE/EXAMS reviews, OCC supervisory cycles, and SOX 404 IT general control testing.

---

## Manual Verification Steps

### Test 1: Compliance Manager Assessment Inventory

1. Sign in to [Microsoft Purview](https://purview.microsoft.com) as **Purview Compliance Admin**.
2. Open **Compliance Manager** > **Assessments**.
3. Filter by group `AI-Agent-Governance`.
4. **EXPECTED:** Assessments for FINRA Books & Records, SEC 17a-4, SOX 404, GLBA 501(b), NIST AI RMF, and ISO/IEC 42001 are all listed and show a non-zero score.

### Test 2: Improvement Action Mapping

1. Open one premium assessment (e.g., NIST AI RMF).
2. Click **Improvement actions** tab.
3. Open three random improvement actions.
4. **EXPECTED:** Each action's **Notes** field references at least one FSI-AgentGov control ID, and at least one action has an attached evidence file.

### Test 3: SharePoint Records Library Retention Behavior

1. Navigate to the `AI-Compliance-Reports` site as **SharePoint Site Owner**.
2. Open `Examination Packages/FINRA/`.
3. Upload a test file `retention-test.txt` and view its properties.
4. **EXPECTED:** The default retention label `FSI-Reg-Records-7Year` is applied automatically; the file shows as a regulatory record (immutable).
5. Attempt to delete the test file.
6. **EXPECTED:** Deletion is blocked with a retention-policy message (or, if allowed, the file is preserved in the Preservation Hold Library).

### Test 4: Weekly Control Status Flow

1. Open [Power Automate](https://make.powerautomate.com) as **Power Platform Admin**.
2. Open the **Weekly Control Status** flow.
3. Click **Run** to trigger manually.
4. Wait for completion; open run history.
5. **EXPECTED:** Flow shows **Succeeded**, output report is in `Weekly Reports/`, and an evidence row was appended to the SHA-256 evidence log.

### Test 5: Monthly Approval Workflow

1. Trigger the **Monthly Regulatory Alignment** flow.
2. As CCO (or test approver), open the email or Approvals app.
3. Approve the request and add a comment.
4. **EXPECTED:** Report is released to the distribution list, approval comment is stored, and the SharePoint metadata column `ApprovedBy` is populated.

### Test 6: Examination Package Manifest

1. From a controlled workstation, run:
   ```powershell
   New-ExaminationManifest -Regulator FINRA -OutputFolder '.\test-finra' -WhatIf
   ```
2. Run again without `-WhatIf` and inspect `.\test-finra\MANIFEST.json`.
3. **EXPECTED:** Manifest contains all 9 FINRA package items with descriptions and includes operator/tenant/cloud metadata.

### Test 7: Power BI Dashboard Refresh

1. Open the **AI Compliance Dashboard** in [Power BI](https://app.powerbi.com).
2. Verify each page renders without "Couldn't load data" errors.
3. Click **Refresh** in the workspace and confirm scheduled refresh history shows successful runs in the last 24 hours.
4. **EXPECTED:** All five pages render with current data; no refresh failures in the last 7 days.

### Test 8: Regulation S-P Notification Drill (Quarterly)

1. From the **Examination Readiness** page, identify the most recent simulated Reg S-P incident drill.
2. Confirm the drill artifact includes: incident timeline, customer determination logic, sample notification letter, 30-day countdown evidence.
3. **EXPECTED:** Drill artifact exists for the current quarter and is signed off by CCO and CISO.

---

## Test Case Matrix

| Test ID | Scenario | Expected Result | Pass/Fail |
|---|---|---|---|
| TC-3.3-01 | Assessment inventory present | All six assessments listed | |
| TC-3.3-02 | Improvement actions mapped to FSI controls | Notes reference control IDs | |
| TC-3.3-03 | Records library default label applies | Label appears on upload | |
| TC-3.3-04 | Records library deletion blocked | Retention enforces immutability | |
| TC-3.3-05 | Weekly flow runs successfully | Status: Succeeded | |
| TC-3.3-06 | Weekly flow emits evidence row | SHA-256 row appended | |
| TC-3.3-07 | Monthly flow triggers approval | CCO receives approval request | |
| TC-3.3-08 | Approved monthly report distributes | Recipients receive email | |
| TC-3.3-09 | FINRA exam manifest builds | MANIFEST.json contains 9 items | |
| TC-3.3-10 | SEC exam manifest contains Reg S-P artifact | Item 06 present | |
| TC-3.3-11 | Power BI dashboard renders all pages | No errors on five pages | |
| TC-3.3-12 | Power BI scheduled refresh succeeds | History clean for 7 days | |
| TC-3.3-13 | Reg S-P quarterly drill artifact exists | Current quarter signed off | |
| TC-3.3-14 | Sovereign cloud parameter respected | `Get-MgContext` shows correct env | |
| TC-3.3-15 | Mutation cmdlets honor `-WhatIf` | No upload occurs in WhatIf mode | |

---

## Evidence to Retain

### Configuration Evidence

- [ ] Screenshot: Compliance Manager > Assessments page filtered by `AI-Agent-Governance` group
- [ ] Export: Compliance Manager improvement actions CSV
- [ ] Screenshot: SharePoint records library default retention label assignment
- [ ] Export: Retention label policy definition (Purview > Records management)

### Operational Evidence

- [ ] Power Automate flow run history (export from each flow, last 90 days)
- [ ] SHA-256 evidence log (`evidence.csv`) covering all snapshot runs in the period
- [ ] Power BI refresh history export
- [ ] Approval workflow records (CCO/CAO sign-offs with comments)

### Examination-Ready Evidence

- [ ] Most recent FINRA, SEC, OCC examination manifests
- [ ] Quarterly Regulation S-P notification drill artifact (most recent)
- [ ] Annual GLBA 501(b) safeguards review document
- [ ] Annual SOX 404 IT general controls attestation referencing this control

### Attestation Statement

- [ ] Signed statement from the **Purview Compliance Admin** (control owner) confirming:
    - Assessments are configured and scored monthly
    - Reports generate on schedule with documented approvals
    - Evidence is retained under records-management retention labels
    - Sovereign cloud parameters are correctly configured (where applicable)
    - Operator runs use the canonical install pattern from the [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md)

---

## Automated Validation Script

```powershell
# Read-only validation for Control 3.3
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$SharePointSiteUrl,
    [string]$EvidenceLogPath = '.\evidence.csv'
)

Write-Host "=== Control 3.3 Validation ===" -ForegroundColor Cyan

# Check 1: Graph context (sovereign-aware)
$ctx = Get-MgContext
if ($ctx) {
    Write-Host "[PASS] Graph connected — Tenant: $($ctx.TenantId), Env: $($ctx.Environment)" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Not connected to Microsoft Graph" -ForegroundColor Red
}

# Check 2: PnP connection
try {
    $web = Get-PnPWeb -ErrorAction Stop
    Write-Host "[PASS] PnP connected to $($web.Url)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] PnP connection failed: $_" -ForegroundColor Red
}

# Check 3: Records library exists
$libs = @('Weekly Reports','Monthly Reports','Quarterly Reports','Annual Reports','Examination Packages')
foreach ($l in $libs) {
    try {
        Get-PnPList -Identity $l -ErrorAction Stop | Out-Null
        Write-Host "[PASS] Library present: $l" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Missing library: $l" -ForegroundColor Red
    }
}

# Check 4: Recent evidence rows
if (Test-Path $EvidenceLogPath) {
    $recent = Import-Csv $EvidenceLogPath |
        Where-Object { [datetime]$_.Timestamp -gt (Get-Date).AddDays(-7) -and $_.ControlId -eq '3.3' }
    if ($recent.Count -gt 0) {
        Write-Host "[PASS] Evidence rows in last 7 days: $($recent.Count)" -ForegroundColor Green
    } else {
        Write-Host "[WARN] No evidence rows for control 3.3 in last 7 days" -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARN] Evidence log not found at $EvidenceLogPath" -ForegroundColor Yellow
}

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

## Governance Tier-Specific Testing

### Baseline (Zone 1 — Personal Productivity)

- [ ] Weekly summary report archives to SharePoint
- [ ] Manager-level acknowledgment of monthly summary

### Recommended (Zone 2 — Team Collaboration)

- [ ] All weekly + monthly flows succeed
- [ ] Department Head approval recorded for monthly report
- [ ] Quarterly evidence bundle compiled
- [ ] Power BI dashboard refresh runs cleanly

### Regulated (Zone 3 — Enterprise Managed)

- [ ] All flows (weekly through annual) succeed
- [ ] CCO/CAO approval recorded with comments
- [ ] Examination manifests generated for FINRA, SEC, OCC on demand within 24 hours
- [ ] SHA-256 evidence emission for every snapshot run
- [ ] Reg S-P notification readiness drill completed in current quarter
- [ ] Records-management retention labels enforce immutability for examination packages

---

## KPI Verification

| KPI | Zone 1 Target | Zone 2 Target | Zone 3 Target | Actual | Status |
|---|---|---|---|---|---|
| Weekly report success rate | ≥ 90% | ≥ 95% | ≥ 99% | | |
| Monthly approval cycle time | ≤ 10 days | ≤ 7 days | ≤ 5 days | | |
| Examination manifest build time | n/a | ≤ 48 h | ≤ 24 h | | |
| Power BI refresh success rate (30 d) | ≥ 90% | ≥ 95% | ≥ 99% | | |
| Reg S-P drill cadence | n/a | Annual | Quarterly | | |

---

[Back to Control 3.3](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.6.2*
