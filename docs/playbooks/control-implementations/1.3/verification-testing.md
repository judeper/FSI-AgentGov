# Verification & Testing: Control 1.3 - SharePoint Content Governance and Permissions

**Last Updated:** May 2026
**Audience:** SharePoint Admin, AI Governance Lead, Compliance Officer
**Run cadence:** monthly spot-check (Zone 3), quarterly full pass (Zone 2), annually (Zone 1)

---

## What "good" looks like

A control 1.3 implementation is operating as intended when **all** of the following are true for every site in the agent grounding inventory:

1. Tenant `SharingCapability` matches the documented zone baseline (`Disabled` for Zone 3, `ExistingExternalUserSharingOnly` for Zone 2 with vetted partner allow-list).
2. The site has a container sensitivity label applied that matches the site's zone classification.
3. No `Everyone` or `Everyone except external users` claim appears in `Get-SPOUser` output for the site.
4. For Zone 3: Restricted Access Control is enabled and bound to a small named group set (the platform allows up to 10 Microsoft 365 / Entra security groups; FSI hardening prefers a single group for least privilege); Restricted Content Discovery is enabled unless the site is intentionally part of the Copilot grounding surface.
5. A least-privileged test user cannot retrieve content from any unauthorized site through Microsoft 365 Copilot or a Microsoft Copilot Studio agent.
6. The most recent Entra access review on the M365 group backing the site completed within the documented cadence with documented outcomes.
7. SharePoint Advanced Management Data Access Governance reports show no unexpected oversharing for the site.
8. A Purview DLP policy targeting agent-relevant sensitive information types covers the site and is in `Enforce` for Zone 3.

---

## Manual verification checklist

### Test 1 — Tenant sharing baseline

1. SharePoint admin center → **Policies** → **Sharing**.
2. Confirm sliders match the documented zone baseline.
3. Cross-check via PowerShell: `Get-SPOTenant | Select-Object SharingCapability, DefaultSharingLinkType, DefaultLinkPermission, RequireAnonymousLinksExpireInDays`.
4. **Expected:** values match the values in the Portal Walkthrough Step 1 table for the in-scope zone.

### Test 2 — Site permission audit (per agent grounding site)

1. Open the site → **Settings (gear)** → **Site permissions** → **Advanced permissions settings**.
2. Open each SharePoint group and review members.
3. Run `Get-SPOUser -Site $url -Limit All | Where-Object LoginName -match 'spo-grid-all-users|^c:0\(\.s\|true$'`.
4. **Expected:** zero rows returned. Every other grant has a documented business justification in the evidence store.

### Test 3 — Container sensitivity label applied

1. SharePoint admin center → **Active sites** → select site → **Settings** flyout → **Sensitivity**.
2. Cross-check via PowerShell: `(Get-SPOSite -Identity $url -Detailed).SensitivityLabel`.
3. **Expected:** label matches the documented zone classification (e.g. `Confidential-FSI` for Zone 3 customer NPI sites).

### Test 4 — Restricted Access Control (Zone 3)

1. SharePoint admin center → site → **Settings** flyout → **Restricted access control** → confirm **On** with the bound group(s).
2. Cross-check via PowerShell: `Get-SPOSite -Identity $url | Select-Object RestrictedAccessControl, RestrictedAccessControlGroups`.
3. **Expected:** `RestrictedAccessControl` is `True` and `RestrictedAccessControlGroups` lists the sanctioned group GUID(s) (at most 10; FSI recommends a single group).
4. **Negative test:** sign in as a user **not** in any bound group; attempt to open the site URL directly.
5. **Expected:** access denied even if the user has direct site permissions; the site does not appear in the user's Microsoft 365 Copilot grounding results.

### Test 5 — Restricted Content Discovery (where applicable)

1. SharePoint admin center → site → **Settings** flyout → **Restrict content discovery** → confirm **On**.
2. As a user with **direct** site permissions, open Microsoft 365 Copilot (Business Chat) and ask a query that should match content on the RCD site.
3. **Expected:** Copilot does not surface that content via grounding (it is suppressed from organization-wide search). The user can still open the site directly.

### Test 6 — Microsoft 365 Copilot grounding boundary

1. Provision a test user with **only** the permissions a frontline agent operator should have.
2. Sign in to Microsoft 365 Copilot Business Chat as that user.
3. Issue a prompt designed to retrieve content from a Zone 3 site the test user is **not** authorized for (e.g. "summarize the Q4 board minutes").
4. **Expected:** Copilot returns "no information found" or surfaces only authorized content. Capture a screenshot for evidence.

### Test 7 — Copilot Studio agent grounding boundary

1. In Copilot Studio, open an agent that uses one of the inventoried sites as a knowledge source.
2. Sign in to the agent as the same least-privileged test user.
3. Ask the agent to retrieve content from a site that is **not** in the agent's configured knowledge sources.
4. **Expected:** the agent does not return that content. The agent's response is security-trimmed to the user's effective SharePoint permissions and the agent's configured grounding sources.

### Test 8 — DLP enforcement

1. As a member user of a Zone 3 site, attempt to share a document containing a synthetic SSN externally.
2. **Expected:** DLP blocks the share with a policy tip referencing the FSI policy ID; an incident is recorded in Purview DLP.

### Test 9 — Access review cycle

1. Entra admin center → **Identity Governance** → **Access reviews** → **Reviews**.
2. Filter to the reviews created for agent grounding M365 groups.
3. **Expected:** most recent instance status is `Completed` within the documented cadence; auto-apply executed for Zone 3; per-decision justifications captured.

### Test 10 — Data Access Governance (DAG) reports

1. SharePoint admin center → **Reports** → **Data access governance** → run / open each of:
    - Sites shared with `Everyone except external users`
    - Sites shared with people in the org
    - Permissions state for sites
2. Filter the export to the agent grounding inventory.
3. **Expected:** zero unexpected entries for Zone 3 sites.

---

## Test case matrix

| Test ID | Scenario | Method | Expected | Pass/Fail |
|---|---|---|---|---|
| TC-1.3-01 | Tenant sharing baseline | Portal + `Get-SPOTenant` | Matches zone baseline | |
| TC-1.3-02 | Per-site `Everyone` claims removed | `Get-SPOUser` | Zero matches | |
| TC-1.3-03 | Container label applied | `Get-SPOSite -Detailed` | `SensitivityLabel` set | |
| TC-1.3-04 | Default library label applied | Library settings | Label set; new files inherit | |
| TC-1.3-05 | RAC enabled on Zone 3 | Portal + `Get-SPOSite \| Select RestrictedAccessControl, RestrictedAccessControlGroups` | Bound to ≤10 named groups (FSI: one); non-members denied | |
| TC-1.3-06 | RCD enabled where required | Portal + `Get-SPOSite` | Site suppressed from search/Copilot | |
| TC-1.3-07 | M365 Copilot boundary | Test user prompt | No unauthorized content surfaced | |
| TC-1.3-08 | Copilot Studio agent boundary | Test user prompt | Security-trimmed correctly | |
| TC-1.3-09 | DLP block on external share | Synthetic SSN | Share blocked, incident recorded | |
| TC-1.3-10 | Access review completion | Entra portal | Completed in cadence with auto-apply | |
| TC-1.3-11 | DAG oversharing reports | Portal export | No unexpected entries | |
| TC-1.3-12 | Restricted SharePoint Search (if used) | `Get-SPOTenantRestrictedSearchMode` + `Get-SPOTenantRestrictedSearchAllowedList` | Mode `Enabled`; allow-list ≤ 100 sites; flagged for sunset (RSS retiring 2026-07-31) | |
| TC-1.3-13 | Drift detection job | Scheduled run output | Exit 0 with no violations | |

---

## Evidence to capture for auditors

### Tenant configuration
- [ ] Screenshot: SharePoint admin center → Policies → Sharing (sliders + advanced settings)
- [ ] CSV export: full active-sites inventory with sharing posture (`SHA256` emitted)
- [ ] Output: `Get-SPOTenant | Format-List` redacted to relevant fields

### Per-site posture (each agent grounding site)
- [ ] Screenshot: site **Settings** flyout (Sensitivity, RAC, RCD)
- [ ] Output: `Get-SPOSite -Identity $url -Detailed | Format-List`
- [ ] Output: `Get-SPOUser -Site $url -Limit All` filtered to broad claims (showing zero matches)
- [ ] Documented justification table for every remaining grant

### Sensitivity labels and DLP
- [ ] Screenshot: published label policy in Purview with target audience
- [ ] Screenshot: DLP policy `FSI-DLP-SharePoint-AgentGrounding` in `Enforce` mode with location scope
- [ ] Sample DLP incident report (synthetic) showing block + policy tip

### Microsoft 365 Copilot grounding test
- [ ] Screen recording or annotated screenshots of the Test 6 / Test 7 sessions
- [ ] Test user identity, timestamp, and the exact prompts used

### Access reviews
- [ ] Screenshot: review definition (cadence, reviewers, auto-apply)
- [ ] Export: most recent completed instance with decisions and justifications

### Data Access Governance
- [ ] Monthly DAG report exports for the trailing 3 months
- [ ] Tickets / remediation evidence for any flagged Zone 3 sites

### Drift detection
- [ ] Last 30 days of scheduled-job exit codes / log entries
- [ ] Any drift CSVs and their remediation status

### Attestation
- [ ] Signed statement from the control owner (typically SharePoint Admin) confirming:
    - Tenant baseline matches documented zone configuration
    - All agent grounding sites have least-privilege permissions and applied labels
    - Zone 3 sites have RAC and (where applicable) RCD
    - DLP is in `Enforce` mode for Zone 3 sites
    - Access reviews completed on cadence with documented outcomes
    - DAG reports reviewed monthly with no unresolved Zone 3 oversharing

> Retain the above evidence per your firm's records-retention policy. For records covered by FINRA 4511 / SEC 17 CFR 240.17a-4(b)(4), preserve in WORM storage for the regulated retention period (typically 6+ years; verify against your firm's WSPs).

---

## Automated validation snippet

```powershell
# Returns PASS/FAIL per check; suitable for invocation from the FSI assessment engine.
$inventory = Import-Csv 'C:\Governance\1.3\agent-grounding-sites.csv'
$results   = foreach ($row in $inventory) {
    $site  = Get-SPOSite -Identity $row.Url -Detailed -ErrorAction Stop
    $broad = Get-SPOUser -Site $row.Url -Limit All | Where-Object LoginName -match 'spo-grid-all-users|^c:0\(\.s\|true$'

    [PSCustomObject]@{
        Url                = $row.Url
        Zone               = $row.Zone
        SharingCheck       = if ($row.Zone -eq 'Zone3') { $site.SharingCapability -eq 'Disabled' } else { $true }
        BroadClaimCheck    = -not $broad
        LabelCheck         = [string]::IsNullOrEmpty($row.ExpectedLabel) -or $site.SensitivityLabel -eq $row.ExpectedLabel
        RACCheck           = if ($row.Zone -eq 'Zone3') { [bool]$site.RestrictedAccessControl -and ($site.RestrictedAccessControlGroups | Measure-Object).Count -ge 1 } else { $true }
        OverallPass        = $true
    }
}
$results | ForEach-Object { $_.OverallPass = $_.SharingCheck -and $_.BroadClaimCheck -and $_.LabelCheck -and $_.RACCheck }
$results | Format-Table -AutoSize
$results | Where-Object { -not $_.OverallPass } | ForEach-Object { Write-Warning "FAIL: $($_.Url)" }
```

---

## Zone-specific verification cadence

### Zone 1 (Personal Productivity)

| Check | Frequency | Method |
|---|---|---|
| Tenant baseline drift | Quarterly | `Get-SPOTenant` snapshot diff |
| Site sensitivity labels | Annual | Spot check (10% sample) |
| Access reviews | Annual | Self-review via Entra |

### Zone 2 (Team Collaboration)

| Check | Frequency | Method |
|---|---|---|
| Per-site permission audit | Quarterly | PowerShell §6 report |
| Container labels | Quarterly | Inventory CSV review |
| DLP incidents | Monthly | Purview incident dashboard |
| Access reviews | Semi-annual | Entra access reviews |
| DAG reports | Quarterly | Portal export |

### Zone 3 (Enterprise Managed)

| Check | Frequency | Method |
|---|---|---|
| Drift detection job | Nightly | Scheduled PowerShell §8 |
| Per-site permission audit | Monthly | PowerShell §6 + manual sign-off |
| Container labels | Monthly | Inventory CSV review |
| DLP incidents | Weekly | Purview dashboard + Sentinel |
| Access reviews | Quarterly w/ auto-remove | Entra |
| DAG reports | Monthly | Portal export + Compliance review |
| Copilot grounding boundary test | Quarterly | Test 6 / Test 7 manual |

---

[Back to Control 1.3](../../../controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
