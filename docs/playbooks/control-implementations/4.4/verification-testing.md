# Control 4.4: Guest and External User Access Controls — Verification & Testing

> This playbook provides verification and testing guidance for [Control 4.4](../../../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md). Every verification step below produces evidence that supports FINRA 4511, SEC 17a-4(f), GLBA 501(b), and SOX 404 obligations.

---

## Verification Strategy

The control is verified across three layers; all three must pass for the control to be considered effective:

1. **Configuration verification** — tenant and site settings match the documented zone baseline.
2. **Behavioral verification** — actual sharing attempts produce the expected allow / block / expire outcomes.
3. **Evidence verification** — exports and audit-log captures exist, are integrity-hashed, and are stored in WORM-eligible storage.

---

## Test Procedure

### Step 1 — Verify tenant settings

1. Open the [SharePoint Admin Center](https://admin.sharepoint.com) > **Policies** > **Sharing**.
2. Confirm:
   - **External sharing** for SharePoint is set to **Existing guests** or more restrictive.
   - **OneDrive external sharing** is set equal to or more restrictive than SharePoint.
   - **Default link type** is **Specific people**.
   - **Guest access expiration** is enabled with the zone-appropriate value.
   - **Anyone link expiration** is configured (or Anyone links are disabled).
3. Capture a screenshot. Record the screenshot path and SHA-256 hash in your evidence log.

### Step 2 — Verify site-level settings (sample)

1. Open **Sites** > **Active sites** and select a sample site from each zone (minimum: 5 Zone 3, 5 Zone 2, 3 Zone 1).
2. For each site, open the **Settings** tab and confirm **External file sharing** matches the zone baseline.
3. Use the PowerShell read-only inventory from the [PowerShell Setup playbook](powershell-setup.md) to enumerate **all** sites and reconcile against the zone CSV. The PowerShell export is the evidence artifact; the portal sample is the spot-check.

### Step 3 — Verify Conditional Access for external users

See [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) for full CA verification. For Control 4.4 confirm at minimum:

- A Conditional Access policy targets **Guest or external users** with **MFA required** and **block legacy authentication**.
- The policy is in **On** state (not Report-only), unless your organization's policy lifecycle requires a Report-only stage with a documented promotion plan.

### Step 4 — Verify Data Access Governance reports

1. Open **Reports** > **Data access governance**.
2. Confirm the following reports are accessible and current:
   - **Sharing links**
   - **Sites shared with everyone** / **Anyone links**
   - **Sites with sensitivity labels applied**
3. Export each report. Compute and record the SHA-256 hash of each export.

---

## Behavioral Tests

These tests confirm that policy configuration produces the intended user-visible outcomes. Run from a non-admin test account that is **not** a member of any sensitivity-label privileged group.

| Test ID | Scenario | Expected Result |
|---------|----------|-----------------|
| TC-4.4-01 | On a Zone 3 site, attempt to share a file with `external.user@partner.com` | Sharing UI does not offer external option; or share fails with policy message |
| TC-4.4-02 | On a Zone 2 site, attempt to invite a **new** external user | Invitation blocked; UI offers only existing-guest selection |
| TC-4.4-03 | On a Zone 2 site, share with a previously-invited guest | Share succeeds; audit log records `SharingSet` with target email |
| TC-4.4-04 | Inspect site posture via PowerShell | `SharingCapability` matches zone baseline for every site in scope |
| TC-4.4-05 | Inspect tenant settings via PowerShell | `ExternalUserExpirationRequired = True`, `ExternalUserExpireInDays` matches policy |
| TC-4.4-06 | Wait 24 hours past `ExternalUserExpireInDays` for a test guest grant; attempt access | Guest is denied; audit log records expiration event |
| TC-4.4-07 | Attempt to share with a non-allow-listed domain | Share blocked; audit log records `SharingPolicyChanged` or `SharingDenied` |
| TC-4.4-08 | Conditional Access: guest signs in from non-compliant device | Sign-in blocked or MFA prompted per policy |
| TC-4.4-09 | Run `Search-UnifiedAuditLog` for `SharePointSharingOperation` over the last 30 days | Returns events with no policy-evasion patterns (e.g., burst Anyone-link creation) |
| TC-4.4-10 | Quarterly access certification completed for Zone 2 + Zone 3 sites | Certification artifact exists, is signed, and lists action taken per guest |

Record pass/fail and evidence reference for each test.

---

## Zone-Specific Verification

### Zone 1 (Personal Productivity)

- [ ] Tenant default sharing applies; site-level overrides documented per exception
- [ ] Sharing capability: `ExternalUserSharingOnly` or more restrictive
- [ ] Guest expiration: 90 days
- [ ] Sample of 3 sites verified manually

### Zone 2 (Team Collaboration)

- [ ] Sharing capability: `ExistingExternalUserSharingOnly`
- [ ] Guest expiration: 30 days
- [ ] `DisableSharingForNonOwnersStatus = True`
- [ ] Site owner identified and approval trail documented for each active guest
- [ ] Domain allow-list applied where domain restrictions are in scope

### Zone 3 (Enterprise Managed)

- [ ] Sharing capability: `Disabled`
- [ ] Zero active external users associated with site (verified via `Get-SPOExternalUser -SiteUrl`)
- [ ] Any change to sharing posture covered by a CAB-approved change ticket
- [ ] Continuous monitoring alerts configured (see [Control 4.5](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md))

---

## Evidence Artifacts and Retention

| Evidence Type | Source | Format | Retention | Regulatory Driver |
|---------------|--------|--------|-----------|-------------------|
| Tenant sharing settings snapshot | `Get-SPOTenant` JSON export + screenshot | `.json` + `.png` | 7 years | SEC 17a-4(f), FINRA 4511 |
| Per-site sharing posture | `Get-SPOSite` CSV export | `.csv` | 7 years | SEC 17a-4(f), FINRA 4511 |
| External user inventory | `Get-SPOExternalUser` paged export | `.csv` | 7 years | GLBA 501(b), FINRA 4511 |
| Sharing-event audit log | `Search-UnifiedAuditLog` over `SharePointSharingOperation` | `.csv` | 7 years (longer if litigation hold) | SEC 17a-4(a), FINRA 4511 |
| Behavioral test screenshots | Manual capture per test ID | `.png` | 1 year minimum, 7 years if used as primary evidence | SOX 404 |
| Conditional Access policy summary | Entra portal export | `.json` | 7 years | SOX 404, OCC Bulletin 2026-13 (formerly OCC 2011-12) |
| Quarterly access certification | Output of [Control 4.2](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | `.pdf` or signed `.docx` | 7 years | FINRA 3110, SOX 404 |
| `manifest.json` (SHA-256 hashes) | Generated alongside every artifact | `.json` | Same as longest-retained artifact | Evidence integrity (SEC 17a-4(f)) |

!!! tip "WORM storage requirement"
    SEC 17a-4(f) requires that records be preserved in a non-rewriteable, non-erasable format. Land all evidence artifacts in storage configured with **Microsoft Purview Data Lifecycle Management retention lock** or **Azure Storage immutability policies**. Plain network-share storage does not satisfy WORM requirements.

---

## PowerShell Validation Snippets

```powershell
# Validate tenant baseline
$expected = @{
    SharingCapability                  = 'ExistingExternalUserSharingOnly'
    ExternalUserExpirationRequired     = $true
    ExternalUserExpireInDays           = 30
    DefaultLinkPermission              = 'View'
    PreventExternalUsersFromResharing  = $true
}
$tenant = Get-SPOTenant
$expected.GetEnumerator() | ForEach-Object {
    $actual = $tenant.($_.Key)
    $pass = ($actual -eq $_.Value)
    [pscustomobject]@{ Property = $_.Key; Expected = $_.Value; Actual = $actual; Pass = $pass }
}

# Find Zone 3 sites that drifted from Disabled
$zone3 = Import-Csv .\zone3-sites.csv
$drift = $zone3 | ForEach-Object {
    $s = Get-SPOSite -Identity $_.Url -ErrorAction SilentlyContinue
    if ($s -and $s.SharingCapability -ne 'Disabled') { $s | Select-Object Url, SharingCapability }
}
if ($drift) { $drift | Format-Table; throw "Zone 3 drift detected" } else { Write-Host "PASS: no Zone 3 drift" }
```

---

## Compliance Attestation Template

```markdown
# Control 4.4 Quarterly Attestation

**Control:** 4.4 — Guest and External User Access Controls
**Attestation Period:** Qx YYYY
**Attested By:** [Name, Title]
**Reviewed By:** [Compliance Officer Name]

## Configuration Status
- [ ] Tenant sharing settings match documented baseline (evidence: `tenant-after-<ts>.json`)
- [ ] All Zone 3 sites configured to Disabled (evidence: `site-posture-<ts>.csv`)
- [ ] All Zone 2 sites configured to ExistingExternalUserSharingOnly (evidence: same)
- [ ] Guest expiration enabled and tested
- [ ] Conditional Access for external users in On state

## Behavioral Test Results
| Test ID | Result | Evidence Reference |
|---------|--------|--------------------|
| TC-4.4-01 |   |   |
| TC-4.4-02 |   |   |
| ...       |   |   |

## Evidence Integrity
- [ ] All artifacts have SHA-256 entries in `manifest.json`
- [ ] Artifacts landed in WORM-eligible storage (location: ____________________)

## Findings & Remediation
[Document gaps, remediation owners, and target dates]

## Sign-off
Attested By: __________________________  Date: ____________
Reviewed By: __________________________  Date: ____________
```

---

[Back to Control 4.4](../../../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
