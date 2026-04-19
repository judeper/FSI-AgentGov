# Control 4.5: SharePoint Security and Compliance Monitoring - Verification & Testing

> This playbook provides verification and testing guidance for [Control 4.5](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md).

!!! info "Read-only verification"
    All steps here are evidence collection only. They do not change tenant state. Run quarterly at minimum (Zone 2/3) and after any change to SharePoint sharing, agent licensing, or audit retention configuration.

---

## Test Procedure

### Step 1: Verify Foundational Audit Ingestion

1. In Purview, navigate to **Audit** > **Search**.
2. Search for `FileAccessed` over the last 24 hours, scoped to a high-traffic site.
3. Confirm non-zero results.
4. Capture a screenshot showing date/time, scope, and result count.

**Why this is Step 1:** Every other check below assumes the audit pipeline is live. If audit ingestion is broken, the rest of the evidence in this run will be misleading.

### Step 2: Verify SharePoint Admin Center Dashboard

1. Navigate to [SharePoint Admin Center](https://admin.sharepoint.com) > **Home**.
2. Confirm dashboard cards render with current data (no "Data unavailable" or stale timestamps).
3. Capture a screenshot of the dashboard.

### Step 3: Verify Agent Insights

1. Navigate to **Reports** > **Agent insights**.
2. Open both **SharePoint agents** and **Agent access** report cards.
3. Confirm agent inventory and access pattern data are populated (or that the page accurately reflects "no agents in tenant").
4. Export each report to CSV and store under your evidence root.

### Step 4: Verify Data Access Governance

1. Navigate to **Reports** > **Data access governance**.
2. Run **Site permissions across your organization** and **Sharing links**.
3. Confirm reports complete without error and produce CSV export.
4. Spot-check three sites against expected sharing posture.

### Step 5: Verify Advanced Management Assessments

1. Navigate to **Advanced management** > **Overview**.
2. Confirm the most recent **Microsoft 365 Copilot readiness** assessment completed within the cadence required for the tenant's zone.
3. Confirm at least one finding has an assigned owner (or attest "no findings" if applicable).

### Step 6: Verify Alert Policy Coverage

1. Navigate to Purview > **Audit** > **Alert policies**.
2. Confirm alert policies exist for the events listed in Step 5 of the [Portal Walkthrough](portal-walkthrough.md).
3. Confirm recipients route to a monitored shared mailbox.
4. (Zone 3) Confirm Sentinel forwarding shows recent SharePoint events in the last 24 hours.

### Step 7: Verify Audit Retention Sufficiency

1. Navigate to Purview > **Audit** > **Audit retention policies**.
2. Confirm a policy exists that retains SharePoint audit records for the full regulatory window (typically 6 years for SEC 17a-4 broker-dealers, 7 years for some advisor obligations — confirm with Compliance).
3. If only the default Standard (180 days) or Premium (1 year) retention is in place, **fail this check** and open a remediation ticket.

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass / Fail |
|---|---|---|---|
| TC-4.5-01 | Audit ingestion live | `FileAccessed` search over last 24h returns non-zero results in an active tenant | |
| TC-4.5-02 | Dashboard accessible | SharePoint Admin Center Home renders all cards with current data | |
| TC-4.5-03 | Agent insights populated | Both Agent insights reports return data (or accurately show empty for tenants with no agents) | |
| TC-4.5-04 | DAG report exports cleanly | Site permissions report generates CSV without error | |
| TC-4.5-05 | Advanced Management current | Most recent Copilot readiness assessment is within cadence for zone | |
| TC-4.5-06 | Alert policies present | At least five SharePoint / agent / sharing alert policies configured with monitored recipients | |
| TC-4.5-07 | Audit retention sufficient | Purview audit retention policy retains SharePoint records for full regulatory window | |
| TC-4.5-08 | Paginated search returns more than 5,000 | Test pagination by querying a high-volume window; confirm result count exceeds 5,000 in tenants with that level of activity | |
| TC-4.5-09 | Evidence manifest hashed | Every export in the evidence directory has a SHA-256 entry in `EVIDENCE-MANIFEST.csv` | |
| TC-4.5-10 | Zone 3 SIEM forwarding | Sentinel `OfficeActivity` table shows SharePoint events in the last 24 hours (Zone 3 only) | |

---

## Zone-Specific Verification

### Zone 1 (Personal Productivity)

- [ ] Tenant-wide audit ingestion confirmed (TC-4.5-01)
- [ ] Monthly Agent insights review completed and exported
- [ ] Weekly dashboard review captured (screenshot or log)

### Zone 2 (Team Collaboration)

- [ ] Weekly Agent access report review completed
- [ ] Monthly DAG reports run, exported, and hashed
- [ ] Alert policies for high-severity events configured (TC-4.5-06)
- [ ] Evidence retained per regulatory retention window

### Zone 3 (Enterprise Managed)

- [ ] Daily agent access monitoring evidence available
- [ ] Continuous dashboard / SIEM coverage in place
- [ ] Sentinel SharePoint forwarding healthy (TC-4.5-10)
- [ ] Containment playbook tested at least quarterly (tabletop or live)

---

## PowerShell Validation Snippets

These snippets are spot-checks. The full evidence collection lives in [PowerShell Setup](powershell-setup.md).

```powershell
# 1) SAM / Copilot licensing presence (SAM is bundled with Copilot since Jan 2025)
Get-MgSubscribedSku | Where-Object {
    $_.SkuPartNumber -match 'COPILOT|SHAREPOINT_ADVANCED|SPE_E5'
} | Select-Object SkuPartNumber, ConsumedUnits, @{n='Available';e={$_.PrepaidUnits.Enabled - $_.ConsumedUnits}}

# 2) Audit ingestion enabled
$cfg = Get-AdminAuditLogConfig
if (-not $cfg.UnifiedAuditLogIngestionEnabled) { throw 'Audit ingestion DISABLED' }

# 3) SharePoint admin role assignment (deterministic, by role definition)
$role = Get-MgDirectoryRole -Filter "displayName eq 'SharePoint Administrator'"
Get-MgDirectoryRoleMember -DirectoryRoleId $role.Id -All |
    ForEach-Object { Get-MgUser -UserId $_.Id | Select-Object UserPrincipalName, DisplayName }

# 4) Audit retention policy presence
Get-RetentionCompliancePolicy -ErrorAction SilentlyContinue |
    Where-Object { $_.Workload -match 'SharePoint' } |
    Select-Object Name, Enabled, Workload

# 5) Smoke test: paginated audit search returns > 5,000 in active tenants
$sessionId = [guid]::NewGuid().ToString()
$count = 0
do {
    $batch = Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) `
        -RecordType SharePoint -SessionId $sessionId -SessionCommand ReturnLargeSet -ResultSize 5000
    $count += $batch.Count
} while ($batch.Count -eq 5000)
Write-Host "7-day SharePoint event count: $count"
```

---

## Verification Evidence

| Evidence Type | Location | Capture Cadence | Retention |
|---|---|---|---|
| Audit ingestion screenshot | Purview > Audit | Quarterly | Per regulatory window |
| Dashboard screenshot | SharePoint Admin Home | Weekly (Zone 2) / Daily (Zone 3) | Per regulatory window |
| Agent insights CSV export | Reports > Agent insights | Monthly (Z1) / Weekly (Z2) / Daily (Z3) | Per regulatory window |
| DAG site permissions CSV | Reports > Data access governance | Quarterly (Z1) / Monthly (Z2) / Weekly (Z3) | Per regulatory window |
| Advanced Management assessment | Advanced management > Overview | Annually (Z1) / Quarterly (Z2) / Monthly (Z3) | Per regulatory window |
| Alert policy export | Purview > Alert policies | Annually | Per regulatory window |
| Audit retention policy export | Purview > Audit retention | Annually | Per regulatory window |
| Evidence manifest with SHA-256 | Evidence root for each run | Every run | Per regulatory window |

---

## Compliance Attestation Template

```markdown
# SharePoint Monitoring Compliance Attestation

**Control:** 4.5 — SharePoint Security and Compliance Monitoring
**Tenant:** [Tenant ID / Domain]
**Cloud:** [Commercial / GCC / GCC High / DoD]
**Zone Scope:** [Zone 1 / 2 / 3]
**Attestation Period:** [YYYY-MM-DD] to [YYYY-MM-DD]
**Attested By:** [Name / Role]
**Reviewed By:** [Name / Role — must differ from Attested By per FINRA 3110]

## Coverage Confirmed

- [ ] Audit ingestion live (TC-4.5-01)
- [ ] Agent insights reports current
- [ ] DAG baseline + delta reports captured
- [ ] Advanced Management assessments within cadence
- [ ] Alert policies configured for SharePoint and agent events
- [ ] Audit retention policy meets regulatory window (TC-4.5-07)
- [ ] Evidence manifest hashed (TC-4.5-09)
- [ ] Zone 3 SIEM forwarding healthy (if applicable)

## Findings

| ID | Finding | Severity | Owner | Target Remediation Date |
|---|---|---|---|---|

## Evidence Manifest

See `evidence/4.5/<YYYY-MM-DD>/EVIDENCE-MANIFEST.csv` for hashes of every artifact captured this period.

## Sign-Off

Attested By: ____________________  Date: __________
Reviewed By: ____________________  Date: __________
```

---

[Back to Control 4.5](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.4.0*
