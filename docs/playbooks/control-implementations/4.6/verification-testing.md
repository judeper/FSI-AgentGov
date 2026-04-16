# Control 4.6: Grounding Scope Governance - Verification & Testing

> This playbook provides verification and testing guidance for [Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md).

---

## Test Procedure

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Run grounding scope audit script | Inventory generated |
| 2 | Verify draft sites are excluded | RestrictContentOrgWideSearch = true |
| 3 | Test Copilot query against excluded site | Content not returned |
| 4 | Test Copilot query against included site | Content returned appropriately |
| 5 | Verify CopilotReady metadata (if implemented) | Property bag values set |
| 6 | Verify Restricted Search configuration (if enabled) | Test cases RSS-01/02/03 pass |
| 7 | Review audit logs for scope changes | Changes logged |

---

## Restricted Search Test Cases

### RSS-01: Verify Restricted Search is Enabled at Tenant Level

**Objective:** Confirm Restricted Search is properly configured

**Test Steps:**
```powershell
Get-SPOTenant | Select-Object EnableRestrictedSearchAllList
```

**Expected Outcome:**
- `EnableRestrictedSearchAllList: True`

**Evidence Collection:**
- Screenshot of PowerShell output
- Export timestamp and administrator account

**Test Frequency:** After initial configuration; quarterly thereafter

---

### RSS-02: Verify Copilot Cannot Ground on Non-Allowed Sites

**Objective:** Confirm Restricted Search enforces positive governance

**Test Steps:**

1. Identify a site NOT in the allowed list that the test user has access to
2. Verify site is not in allowed list:
   ```powershell
   Get-SPOTenantRestrictedSearchAllowedList | Where-Object { $_ -like "*TestSiteName*" }
   ```
   (Should return no results)
3. Query Microsoft 365 Copilot for content known to exist only on this non-allowed site
4. Example prompt: "Summarize the Q4 draft budget document from the Finance site"

**Expected Outcome:**
- Copilot responds that it cannot find the requested content
- Copilot may suggest checking permissions, but should NOT return content from non-allowed site
- User can still access the site directly via SharePoint, but Copilot cannot ground on it

**Evidence Collection:**
- Screenshot of PowerShell verification (site not in allowed list)
- Screenshot of Copilot response showing no results
- Screenshot of direct SharePoint access (proving user has permissions)

**Test Frequency:** After initial configuration; quarterly thereafter

**Propagation Note:** Allow 24-48 hours after adding/removing sites from allowed list before testing

---

### RSS-03: Verify Copilot CAN Ground on Allowed Sites

**Objective:** Confirm allowed sites remain accessible for grounding

**Test Steps:**

1. Identify a site IN the allowed list that the test user has access to
2. Verify site is in allowed list:
   ```powershell
   Get-SPOTenantRestrictedSearchAllowedList | Where-Object { $_ -like "*ApprovedSiteName*" }
   ```
   (Should return the site URL)
3. Query Microsoft 365 Copilot for content known to exist on this allowed site
4. Example prompt: "Summarize the product documentation from the Knowledge Base site"

**Expected Outcome:**
- Copilot successfully retrieves and grounds responses on content from allowed site
- Copilot citations reference the allowed site
- Response quality matches pre-Restricted-Search behavior for allowed content

**Evidence Collection:**
- Screenshot of PowerShell verification (site in allowed list)
- Screenshot of Copilot response with grounded content
- Screenshot showing citations to allowed site

**Test Frequency:** After initial configuration; quarterly thereafter

---

## Expected Results Checklist

- [ ] Site inventory completed with Copilot status
- [ ] Draft content excluded from grounding
- [ ] Archive content excluded from grounding
- [ ] Personal content policy documented
- [ ] CopilotReady tagging implemented (Level 2+)
- [ ] Restricted Search configured (Zone 3 environments)
- [ ] Restricted Search test cases RSS-01/02/03 passed
- [ ] Allowed list governance process documented
- [ ] Quarterly review process established
- [ ] Change control for scope modifications (Level 4)
- [ ] Audit evidence retained

---

## Verification Evidence

| Evidence Type | Location | Retention |
|---------------|----------|-----------|
| Site inventory with Copilot status | Export CSV | Monthly |
| Exclusion configuration screenshots | SharePoint Admin | Quarterly |
| CopilotReady approval records | Governance register | 6 years |
| Scope change audit logs | Purview Audit | Per regulation |

---

## Zone-Specific Verification

### Zone 1 (Personal Productivity)

- [ ] Personal OneDrive excluded by default
- [ ] Personal site policy documented
- [ ] Minimal configuration verified

### Zone 2 (Team Collaboration)

- [ ] Draft and archive sites excluded
- [ ] CopilotReady tagging implemented
- [ ] Monthly grounding scope review scheduled
- [ ] Evidence retained

### Zone 3 (Enterprise Managed)

- [ ] Explicit approval for all indexed content
- [ ] All sources CopilotReady tagged
- [ ] Sensitivity label integration verified
- [ ] Quarterly owner attestation
- [ ] Change control for modifications

---

## PowerShell Validation

```powershell
# Verify specific site exclusion
Get-SPOSite -Identity "https://contoso.sharepoint.com/sites/DraftDocs" |
    Select-Object Url, RestrictContentOrgWideSearch

# Count indexed vs excluded sites
$sites = Get-SPOSite -Limit All | Where-Object { $_.Template -notlike "*SPSPERS*" }
$indexed = ($sites | Where-Object { -not $_.RestrictContentOrgWideSearch }).Count
$excluded = ($sites | Where-Object { $_.RestrictContentOrgWideSearch }).Count

Write-Host "Indexed: $indexed | Excluded: $excluded"

# Find draft sites that are NOT excluded (potential gap)
$draftNotExcluded = $sites | Where-Object {
    $_.Url -like "*draft*" -and -not $_.RestrictContentOrgWideSearch
}
if ($draftNotExcluded.Count -gt 0) {
    Write-Host "WARNING: $($draftNotExcluded.Count) draft sites not excluded!" -ForegroundColor Red
}
```

---

## Compliance Attestation Template

```markdown
# Grounding Scope Governance Attestation

**Control:** 4.6 - Grounding Scope Governance
**Attestation Date:** [Date]
**Attested By:** [Name/Role]

## Configuration Status

- [ ] Site inventory completed
- [ ] Draft sites excluded
- [ ] Archive sites excluded
- [ ] CopilotReady metadata implemented
- [ ] Quarterly review scheduled

## Evidence Collected

| Item | Date Collected | Location |
|------|---------------|----------|
| Site inventory export | [Date] | [Path] |
| Exclusion screenshots | [Date] | [Path] |
| CopilotReady register | [Date] | [Path] |

## Findings

[Document any gaps or issues identified]

## Remediation Actions

[Document any required remediation]

## Sign-Off

Attested By: _________________ Date: _________
Reviewed By: _________________ Date: _________
```

---

[Back to Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.3*
