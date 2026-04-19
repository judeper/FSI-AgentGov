# Control 4.2: Site Access Reviews and Certification — Verification & Testing

> Verification guidance and audit evidence collection for [Control 4.2 — Site Access Reviews and Certification](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md).

This playbook covers manual portal verification, scripted health checks, the artifact set to retain for SEC 17a-4 / FINRA 4511 evidence, and a Purview audit-log cross-check.

---

## Manual verification

### Test 1 — DAG reports refreshed and accessible

1. Open SharePoint Admin Center → **Reports** → **Data access governance**.
2. Confirm the following reports each have a **Last refreshed** timestamp within the last 30 days:
   - Content shared with EEEU
   - Sharing links
   - Site permissions
   - Oversharing baseline using permissions
   - Agent Insights, Agent Access Insights
3. Open the EEEU report and confirm it returns rows. **Expected:** report opens, rows render, export to CSV completes.

### Test 2 — Site Attestation Policy active and scoped

1. Navigate to **Policies** → **Site lifecycle management** → **Site attestation policies**.
2. Confirm at least one policy is in **Active** status, scoped to the `Confidential` and `Highly Confidential` sensitivity labels.
3. Open the policy and verify:
   - Cadence matches zone requirement (Quarterly for Zone 3, Semi-annual for Zone 2)
   - Reminder days configured (30 / 14 / 7 / 1)
   - Custom email template renders the organization compliance footer
   - Non-compliance action set to **Make site read-only** for Zone 3
4. **Expected:** policy is active and scoped; preview email contains custom content.

### Test 3 — Site Access Review reaches the reviewer

1. From the EEEU DAG report, initiate a Site Access Review on a low-impact test site you own.
2. Switch to the site owner mailbox and confirm receipt of the notification.
3. Open the review pane, choose **Keep access** for one user and **Stop sharing with EEEU**, save with justification.
4. **Expected:** notification received, decisions accepted, EEEU principal removed from the test site within 24 hours.

### Test 4 — Entra Access Review schedule active

1. Open Microsoft Entra Admin Center → **Identity governance** → **Access reviews**.
2. Locate "FSI SharePoint Site Access Review — Quarterly".
3. Confirm:
   - Status is **Initialized** or **InProgress**
   - Recurrence is **Quarterly**
   - **Auto-apply decisions** = On
   - **Default decision if no response** = **Deny / Remove access**
4. **Expected:** review schedule visible; first instance present in the **History** tab.

### Test 5 — Sites.Selected service principals enumerated

1. Run the enumeration block from **PowerShell Setup §2b**.
2. Confirm every production AI agent service principal that holds Sites.Selected appears in `sites-selected-agents.csv`.
3. Confirm each has a corresponding entry in the access review for the agent governance group.
4. **Expected:** counts match between the enumeration CSV and the access review scope.

### Test 6 — Non-compliance action observed

1. Identify a non-production test site under attestation.
2. Allow the attestation deadline to lapse without response (or use a short-cycle test policy).
3. Verify the site enters read-only state and that the audit log records the change.
4. **Expected:** site is read-only; site owner notified; event appears in Purview audit log.

### Test 7 — Evidence covered by retention

1. Open Microsoft Purview → **Data lifecycle management** → **Retention policies** (or **Retention labels**).
2. Confirm a policy / label covers the evidence repository with a retention period ≥ 6 years.
3. For Zone 3, confirm **Preservation Lock** is enabled (the policy cannot be shortened or deleted).
4. **Expected:** retention coverage in place; lock status appropriate to zone.

---

## Test case matrix

| Test ID | Scenario | Expected Result | Pass/Fail |
|---|---|---|---|
| TC-4.2-01 | DAG report set refreshed within 30 days | All listed reports show recent timestamps | |
| TC-4.2-02 | Site Attestation Policy active for Confidential labels | Policy visible, active, custom email template applied | |
| TC-4.2-03 | Site Access Review initiated from EEEU row | Reviewer receives notification, decisions accepted | |
| TC-4.2-04 | Entra Access Review on M365 Groups quarterly | Schedule visible with Auto-apply + Deny default | |
| TC-4.2-05 | Sites.Selected service principal review configured | Agent SPs enumerated and in scope of review | |
| TC-4.2-06 | Non-compliance action triggers read-only | Test site becomes read-only after deadline | |
| TC-4.2-07 | Decisions exported and SHA-256 emitted | CSV + `.sha256` manifest in evidence directory | |
| TC-4.2-08 | Retention coverage on evidence library ≥ 6 years | Purview policy/label confirmed; lock on for Zone 3 | |
| TC-4.2-09 | Audit log records `AccessReviewDecisionApplied` | Event present for the test instance | |
| TC-4.2-10 | Within tenant 1,000-review monthly limit | Initiated review count ≤ 1,000 in trailing 30 days | |

---

## Evidence to retain

### Configuration evidence

- [ ] Screenshot or export of each DAG report header (with last-refresh timestamp)
- [ ] Site Attestation Policy export (PowerShell or screenshot)
- [ ] Custom email template body (text or screenshot)
- [ ] Entra Access Review definition export (`Get-MgIdentityGovernanceAccessReviewDefinition | ConvertTo-Json -Depth 10`)
- [ ] Sites.Selected service principal enumeration CSV

### Operational evidence (per cycle)

- [ ] Attestation completion CSV with timestamps and reviewer identity
- [ ] Access review decision export (`access-review-decisions.csv` from PowerShell §3)
- [ ] SHA-256 manifest for each CSV (`.sha256` file)
- [ ] Remediation records for any access changes applied
- [ ] Exception register with named approver for any out-of-policy decision

### Compliance evidence (audit-ready)

- [ ] Quarterly attestation completion rate report
- [ ] Escalation records for non-responsive sites
- [ ] Purview audit log search results for `AccessReview*` operations
- [ ] WSP / SOP language describing the program (FINRA Rule 3110 supervisory documentation)
- [ ] Retention policy or label proving the evidence repository is covered for ≥ 6 years (Preservation Lock screenshot for Zone 3)

---

## Automated validation script

```powershell
# Control 4.2 lightweight validation — run quarterly during evidence collection
Write-Host "=== Control 4.2 Validation ===" -ForegroundColor Cyan

Connect-MgGraph -Scopes 'AccessReview.Read.All','Sites.Read.All','Application.Read.All' | Out-Null
Connect-SPOService -Url 'https://contoso-admin.sharepoint.com'

$pass = 0; $warn = 0; $fail = 0

# Check 1 — at least one access review exists and is active
$reviews = Get-MgIdentityGovernanceAccessReviewDefinition -All
$active  = $reviews | Where-Object Status -in @('InProgress','Initialized')
if ($active.Count -ge 1) {
    Write-Host "[PASS] $($active.Count) active access review definition(s)" -ForegroundColor Green; $pass++
} else {
    Write-Host "[FAIL] No active access review definitions found" -ForegroundColor Red; $fail++
}

# Check 2 — orphaned sites (no Owner) cannot be attested
$sites    = Get-SPOSite -Limit All -IncludePersonalSite:$false | Where-Object Template -notlike 'SPSPERS*'
$orphans  = $sites | Where-Object { [string]::IsNullOrWhiteSpace($_.Owner) }
if ($orphans.Count -eq 0) {
    Write-Host "[PASS] All sites have an owner assigned" -ForegroundColor Green; $pass++
} else {
    Write-Host "[WARN] $($orphans.Count) site(s) without owner — cannot be attested" -ForegroundColor Yellow; $warn++
}

# Check 3 — sensitivity-labeled sites used by attestation scope
$labeled = $sites | Where-Object { -not [string]::IsNullOrWhiteSpace($_.SensitivityLabel) }
if ($labeled.Count -ge 1) {
    Write-Host "[PASS] $($labeled.Count) site(s) carry a sensitivity label" -ForegroundColor Green; $pass++
} else {
    Write-Host "[WARN] No labeled sites — Site Attestation Policy scoping by label is not effective" -ForegroundColor Yellow; $warn++
}

# Check 4 — Sites.Selected service principal inventory present
$graphSp     = Get-MgServicePrincipal -Filter "appId eq '00000003-0000-0000-c000-000000000000'"
$ssRoleId    = ($graphSp.AppRoles | Where-Object Value -eq 'Sites.Selected').Id
$ssAssigned  = Get-MgServicePrincipal -All |
    Where-Object {
        Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $_.Id -ErrorAction SilentlyContinue |
            Where-Object { $_.AppRoleId -eq $ssRoleId -and $_.ResourceId -eq $graphSp.Id }
    }
if ($ssAssigned.Count -ge 0) {
    Write-Host "[PASS] $($ssAssigned.Count) Sites.Selected service principal(s) inventoried" -ForegroundColor Green; $pass++
}

Write-Host "`nSummary: PASS=$pass WARN=$warn FAIL=$fail" -ForegroundColor Cyan
```

---

## Evidence retention table

| Evidence Type | Source | Minimum Retention | Storage Recommendation |
|---|---|---|---|
| DAG report exports (CSV) | SharePoint Admin Center → Data access governance | 1 year (Zone 1), 6 years (Zone 3) | SharePoint library with retention label |
| Site Attestation Policy export | SAM portal or PowerShell | Life of policy + 1 year | SharePoint library |
| Attestation responses | SAM site lifecycle management | 6 years | Purview retention label, Preservation Lock for Zone 3 |
| Access review decisions | Entra ID Governance → CSV export | 6 years | Purview retention label, Preservation Lock for Zone 3 |
| Sites.Selected enumeration | PowerShell §2b | 6 years | Same evidence repository |
| Remediation records | Service Now / change tickets | 6 years | Ticketing system + Purview |

---

[Back to Control 4.2](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.4.0*
