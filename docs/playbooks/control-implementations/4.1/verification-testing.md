# Control 4.1: SharePoint Information Access Governance (IAG) — Verification & Testing

> Verification, test scenarios, and auditor-ready evidence collection for [Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md).

---

## Verification Checklist

Work through this list end-to-end before signing off the control as **In Place**.

1. [ ] Microsoft 365 Copilot license is assigned to at least one user (RCD prerequisite).
2. [ ] DAG **Sites shared with "Everyone except external users"** report exported and reviewed.
3. [ ] Every Zone 3 site in the governance inventory shows `RestrictContentOrgWideSearch = True` via `Get-SPOSite`.
4. [ ] Every Zone 2 sensitive site (per inventory) shows the same.
5. [ ] RCD toggle confirmed visible and **On** in SharePoint admin center → Active sites → Settings for a sample of 5+ sites.
6. [ ] RSS allow-list (if used) is enabled at tenant scope and contains only approved sites; documented exit plan exists.
7. [ ] RAC is enabled on each ethical-wall site with the correct Entra security groups (≤10 per site).
8. [ ] Site owners are not silently retaining access where they should not — owner list reviewed for RAC sites.
9. [ ] Unified Audit Log search returns `SiteRestrictedFromOrgSearch` and `RestrictedAccessControlPolicyUpdated` events for all changes in the change window.
10. [ ] Quarterly attestation (Zone 3) is scheduled and assigned to a named Compliance Officer.
11. [ ] Reindex completion confirmed (allow up to ~72 hours after RCD enable) before functional Copilot tests are run.

---

## Test Scenarios

### TC-4.1-01 — RCD enabled in portal

**Steps:** SharePoint admin center → Sites → Active sites → {restricted site} → Settings.
**Expected:** "Restrict content from Microsoft 365 Copilot" toggle is **On**.
**Evidence:** Screenshot of the Settings panel.

### TC-4.1-02 — RCD enforced in Copilot (post-reindex)

**Steps:** Sign in as a user with direct permission to the restricted site. In Microsoft 365 Copilot Chat (work scope), ask a question whose answer would otherwise be retrieved from a known document on that site.
**Expected:** Copilot does not return the document or quote its content as a citation. Direct browse access on the site still works (RCD does not change permissions).
**Caveat:** If the user has *recently interacted* with the document, Copilot may still surface it via interaction history — document this exception.

### TC-4.1-03 — Copilot returns content from non-restricted site

**Steps:** Same user, ask a question that targets a known document on a non-restricted site they have permission to.
**Expected:** Copilot returns the content with a citation.
**Purpose:** Confirms Copilot is working and the negative result in TC-4.1-02 is attributable to RCD.

### TC-4.1-04 — RAC blocks user outside the security group

**Steps:** Sign in as a user **not** in any RAC security group. Browse to the RAC-protected site URL directly.
**Expected:** Access denied page; user cannot enumerate the site.
**Evidence:** Screenshot of the access-denied page with timestamp.

### TC-4.1-05 — RAC permits user inside the security group

**Steps:** Sign in as a user in an authorised RAC group. Browse to the same URL.
**Expected:** Access granted; site loads normally.

### TC-4.1-06 — RSS allow-list scoping (only when RSS is in use)

**Steps:** Sign in as a Copilot user. Pose a query that targets a non-allow-listed site the user has permission to.
**Expected:** Copilot does not retrieve from that site. Allow-listed sites are reachable.

### TC-4.1-07 — Audit-log capture

**Steps:** Microsoft Purview → Audit → New search. Operations: `SiteRestrictedFromOrgSearch`, `RestrictedAccessControlPolicyUpdated`. Date range covers your test changes.
**Expected:** Each change you made is logged with user UPN, site URL, timestamp, and (where applicable) justification text.

### TC-4.1-08 — RCD disable + re-enable produces audit trail with justification

**Steps:** Toggle RCD off and back on for one test site, providing distinct justifications. Re-run the audit search.
**Expected:** Two audit events with the supplied justification text — required for FINRA 4511 / SEC 17a-4(f) recordkeeping.

---

## Auditor Evidence Pack

Assemble and retain the following artifacts. Recommended retention: align with your firm's records-retention schedule (typically **6 years** for SEC 17a-4(f) / FINRA 4511 evidence).

### Configuration evidence

- [ ] `Get-SPOSite` CSV export showing `RestrictContentOrgWideSearch`, `RestrictedAccessControl`, `RestrictedAccessControlGroups`, `SensitivityLabel` for every Zone 3 site (with SHA-256)
- [ ] DAG report exports (oversharing, sharing-link inventory)
- [ ] Screenshots: per-site RCD toggle state, RAC policy detail, tenant RSS settings (if used)
- [ ] Bulk-apply results CSV from any PowerShell rollouts (with SHA-256)

### Functional test evidence

- [ ] Copilot screenshots for TC-4.1-02 (no result) and TC-4.1-03 (positive result), same date, same user
- [ ] Access-denied screenshots for TC-4.1-04
- [ ] Note describing reindex wait time observed before tests were executed

### Audit-log evidence

- [ ] Purview audit search export covering RCD/RAC operations across the change window (with SHA-256)
- [ ] Justification text from delegated changes (cross-referenced to change tickets)

### Governance documentation

- [ ] Restricted-site register: site URL, owner, classification, justification, approving authority, next review date
- [ ] Quarterly attestation records (Zone 3)
- [ ] Exit plan from RSS to RCD + Purview (if RSS is in use)

---

## Automated Validation Snippet

```powershell
# Goal: confirm every site in the governance manifest is RCD-protected
$Manifest = Import-Csv .\rcd-manifest.csv      # Url, Zone, Justification

$pass = 0; $fail = 0; $rows = foreach ($row in $Manifest) {
    try {
        $s = Get-SPOSite -Identity $row.Url -ErrorAction Stop
        $ok = ($s.RestrictContentOrgWideSearch -eq $true)
        if ($ok) { $pass++ } else { $fail++ }
        [pscustomobject]@{
            Url = $row.Url; Zone = $row.Zone
            RCD = $s.RestrictContentOrgWideSearch
            Result = if ($ok) { 'PASS' } else { 'FAIL' }
        }
    } catch {
        $fail++
        [pscustomobject]@{ Url = $row.Url; Zone = $row.Zone; RCD = $null; Result = 'ERROR' }
    }
}

$rows | Format-Table -AutoSize
$out = ".\IAG-Validation-{0:yyyyMMdd}.csv" -f (Get-Date)
$rows | Export-Csv $out -NoTypeInformation -Encoding UTF8
Write-Host ("Pass={0} Fail={1} :: Evidence: {2} (SHA-256 {3})" -f $pass, $fail, $out, (Get-FileHash $out -Algorithm SHA256).Hash)
```

---

## Evidence Retention Reference

| Evidence type | Storage location | Retention guidance |
|---|---|---|
| Configuration CSV exports | Governance evidence store | Align with SEC 17a-4(f) schedule (commonly 6 years) |
| Functional test screenshots | Compliance records | 1 year minimum, longer if cited in audit |
| Audit-log search exports | Records-management WORM store | Per firm records-retention policy |
| Quarterly attestations | Compliance archive | 6 years recommended |

---

[Back to Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.4.0*
