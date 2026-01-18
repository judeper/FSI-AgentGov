# Control 4.6: Grounding Scope Governance - Verification & Testing

> This playbook provides verification and testing guidance for [Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md).

---

## Test Procedure

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Run grounding scope audit script | Inventory generated |
| 2 | Verify draft sites are excluded | RestrictContentOrgWideSearchAndCopilot = true |
| 3 | Test Copilot query against excluded site | Content not returned |
| 4 | Test Copilot query against included site | Content returned appropriately |
| 5 | Verify CopilotReady metadata (if implemented) | Property bag values set |
| 6 | Review audit logs for scope changes | Changes logged |

---

## Expected Results Checklist

- [ ] Site inventory completed with Copilot status
- [ ] Draft content excluded from grounding
- [ ] Archive content excluded from grounding
- [ ] Personal content policy documented
- [ ] CopilotReady tagging implemented (Level 2+)
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
Get-SPOSite -Identity "https://tenant.sharepoint.com/sites/DraftDocs" |
    Select-Object Url, RestrictContentOrgWideSearchAndCopilot

# Count indexed vs excluded sites
$sites = Get-SPOSite -Limit All | Where-Object { $_.Template -notlike "*SPSPERS*" }
$indexed = ($sites | Where-Object { -not $_.RestrictContentOrgWideSearchAndCopilot }).Count
$excluded = ($sites | Where-Object { $_.RestrictContentOrgWideSearchAndCopilot }).Count

Write-Host "Indexed: $indexed | Excluded: $excluded"

# Find draft sites that are NOT excluded (potential gap)
$draftNotExcluded = $sites | Where-Object {
    $_.Url -like "*draft*" -and -not $_.RestrictContentOrgWideSearchAndCopilot
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

*Updated: January 2026 | Version: v1.1*
