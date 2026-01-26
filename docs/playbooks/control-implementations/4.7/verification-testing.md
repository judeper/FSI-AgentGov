# Control 4.7: Microsoft 365 Copilot Data Governance - Verification & Testing

> This playbook provides verification and testing guidance for [Control 4.7](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md).

---

## Test Procedure

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Access M365 Copilot in Word/Excel | Copilot functional for licensed user |
| 2 | Query for excluded site content | Content not returned |
| 3 | Attempt to use blocked plugin | Plugin not available |
| 4 | Review usage analytics | Data visible in Admin Center |
| 5 | Verify sensitivity labels honored | Labeled content appropriately restricted |
| 6 | Test audit logging | Copilot interactions logged |

---

## Expected Results Checklist

- [ ] Copilot licenses inventoried and tracked
- [ ] Sensitive sites excluded via RCD
- [ ] Plugin governance established (approval workflow)
- [ ] Web search configured per policy
- [ ] Acceptable use policy published
- [ ] Training program deployed
- [ ] Output review processes documented
- [ ] Usage monitoring configured
- [ ] Graph Connector ACL mappings validated (if applicable)
- [ ] Quarterly review schedule established
- [ ] Audit retention configured (6+ years)

---

## Verification Evidence

| Evidence Type | Location | Retention |
|---------------|----------|-----------|
| Site Copilot status export | PowerShell output | Monthly |
| Plugin inventory | M365 Admin Center | Quarterly |
| Usage analytics report | M365 Admin Center | Monthly |
| Acceptable use policy | Published location | 6 years |
| Training completion records | LMS | 6 years |

---

## Zone-Specific Verification

### Zone 1 (Personal Productivity)

- [ ] Standard M365 Copilot access enabled
- [ ] Self-review of outputs expected
- [ ] Basic acceptable use guidance provided

### Zone 2 (Team Collaboration)

- [ ] RCD configured for sensitive team sites
- [ ] Peer review for shared outputs documented
- [ ] Plugin approval workflow for team integrations
- [ ] Monthly usage review scheduled

### Zone 3 (Enterprise Managed)

- [ ] Comprehensive content exclusions applied
- [ ] Strict plugin allowlist enforced
- [ ] Mandatory review for external communications
- [ ] Full audit logging enabled
- [ ] Quarterly compliance attestation scheduled

---

## PowerShell Validation

```powershell
# Verify site exclusions
Get-SPOSite -Limit All | Where-Object {
    $_.RestrictContentOrgWideSearch -eq $true
} | Select-Object Url, Title | Format-Table

# Count licensed users
$licensedUsers = Get-MgUser -Filter "assignedLicenses/any()" -All
Write-Host "Users with licenses: $($licensedUsers.Count)"

# Check for sensitive sites not excluded
$sensitivePatterns = @("executive", "legal", "hr", "confidential")
Get-SPOSite -Limit All | Where-Object {
    $url = $_.Url.ToLower()
    ($sensitivePatterns | Where-Object { $url -like "*$_*" }) -and
    $_.RestrictContentOrgWideSearch -ne $true
} | Select-Object Url
```

---

## Compliance Attestation Template

```markdown
# M365 Copilot Data Governance Attestation

**Control:** 4.7 - Microsoft 365 Copilot Data Governance
**Attestation Date:** [Date]
**Attested By:** [Name/Role]

## Configuration Status

- [ ] Copilot licenses inventoried
- [ ] Sensitive sites excluded
- [ ] Plugin governance configured
- [ ] Acceptable use policy published
- [ ] Usage monitoring enabled

## Evidence Collected

| Item | Date Collected | Location |
|------|---------------|----------|
| Site exclusion report | [Date] | [Path] |
| Plugin inventory | [Date] | [Path] |
| Usage analytics export | [Date] | [Path] |
| Policy publication | [Date] | [URL] |

## Findings

[Document any gaps or issues identified]

## Remediation Actions

[Document any required remediation]

## Sign-Off

Attested By: _________________ Date: _________
Reviewed By: _________________ Date: _________
```

---

*Updated: January 2026 | Version: v1.2*
