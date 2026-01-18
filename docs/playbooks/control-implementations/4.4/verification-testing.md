# Control 4.4: Guest and External User Access Controls - Verification & Testing

> This playbook provides verification and testing guidance for [Control 4.4](../../../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md).

---

## Test Procedure

### Step 1: Verify Site-Level Settings

1. Navigate to SharePoint Admin Center > Sites > Active sites
2. Select a regulated/sensitive site and check Settings panel
3. Verify "External file sharing" is set to internal only
4. Repeat for a sample of sites in each zone

### Step 2: Verify Organization Policies

1. Navigate to Policies > Sharing
2. Verify organization-level sharing settings match requirements
3. Confirm guest access expiration is configured
4. Verify link expiration requirements are set

### Step 3: Verify Data Access Governance Reports

1. Navigate to Reports > Data access governance
2. Run sharing reports
3. Identify any unauthorized sharing links
4. Document findings

---

## Expected Results Checklist

- [ ] Regulated/sensitive sites have external sharing disabled
- [ ] Organization defaults restrict external sharing
- [ ] Guest access expiration is configured (30 days recommended)
- [ ] No unauthorized sharing links exist
- [ ] Sharing reports accessible for monitoring

---

## Verification Evidence

| Evidence Type | Location | Retention |
|---------------|----------|-----------|
| Site sharing settings screenshot | Active sites > Settings | 1 year |
| Organization sharing policy screenshot | Policies > Sharing | 1 year |
| Sharing links report export | Data access governance | 1 year |
| Guest access review records | Governance documentation | 6 years |

---

## Zone-Specific Verification

### Zone 1 (Personal Productivity)

- [ ] Baseline minimum applied where tenant-wide safety requires
- [ ] Exceptions documented for personal agents
- [ ] Sharing capability: ExternalUserSharingOnly or less

### Zone 2 (Team Collaboration)

- [ ] Sharing capability: ExistingExternalUserSharingOnly
- [ ] Guest expiration: 30 days
- [ ] Evidence retained (screenshots/exports/logs)
- [ ] Owner identified and approval trail documented

### Zone 3 (Enterprise Managed)

- [ ] Sharing capability: Disabled
- [ ] No external sharing exceptions
- [ ] Changes controlled (change ticket + documented testing)
- [ ] Continuous audit monitoring enabled

---

## PowerShell Validation

```powershell
# Validate tenant settings
Get-SPOTenant | Select-Object SharingCapability, ExternalUserExpirationRequired, ExternalUserExpireInDays

# Find sites with external sharing enabled that should be restricted
Get-SPOSite -Limit All | Where-Object {
    $_.SharingCapability -ne "Disabled" -and
    $_.Url -like "*regulated*"
} | Select-Object Url, SharingCapability

# Count external users
$externalUsers = Get-SPOExternalUser -PageSize 50
Write-Host "Total external users: $($externalUsers.Count)"
```

---

## Compliance Attestation Template

```markdown
# Guest Access Controls Compliance Attestation

**Control:** 4.4 - Guest and External User Access Controls
**Attestation Date:** [Date]
**Attested By:** [Name/Role]

## Configuration Status

- [ ] Tenant sharing settings configured
- [ ] Zone 3 sites have external sharing disabled
- [ ] Zone 2 sites restricted to existing guests
- [ ] Guest expiration enabled

## Evidence Collected

| Item | Date Collected | Location |
|------|---------------|----------|
| Tenant settings screenshot | [Date] | [Path] |
| Site sharing report | [Date] | [Path] |
| External user inventory | [Date] | [Path] |

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
