# Control 4.3: Site and Document Retention Management - Verification & Testing

> This playbook provides verification and testing guidance for [Control 4.3](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md).

---

## Test Procedure

### Step 1: Verify Site Lifecycle Policies

1. Navigate to SharePoint Admin Center > Policies > Site lifecycle management
2. Verify inactive site policy exists and is enabled
3. Check site ownership policy configuration
4. Review policy notification settings

### Step 2: Verify Organization Settings

1. Navigate to Settings in SharePoint Admin Center
2. Verify OneDrive retention setting matches requirements
3. Review version history settings

### Step 3: Test Policy Operation

1. Review the notification queue for policy actions
2. Verify notifications are being sent to site owners
3. Confirm policy actions execute as configured

---

## Expected Results Checklist

- [ ] Inactive site policy configured and enabled
- [ ] Site ownership policy configured (recommended)
- [ ] Notification templates customized appropriately
- [ ] OneDrive retention set per requirements
- [ ] Policy actions align with governance requirements

---

## Verification Evidence

| Evidence Type | Location | Retention |
|---------------|----------|-----------|
| Policy configuration screenshots | Site lifecycle management | 1 year |
| Policy execution logs | Site lifecycle management | Per policy |
| Retention settings screenshot | Settings page | 1 year |
| Site disposition records | Governance documentation | 6 years |

---

## PowerShell Validation Commands

```powershell
# Verify retention policy status
Get-RetentionCompliancePolicy -Identity "FSI-Agent-Knowledge-Retention-7Years" |
    Select-Object Name, Enabled, Mode, DistributionStatus

# Check retention rule configuration
Get-RetentionComplianceRule -Policy "FSI-Agent-Knowledge-Retention-7Years" |
    Select-Object Name, RetentionDuration, RetentionComplianceAction

# Verify label publication status
Get-RetentionCompliancePolicy -Identity "FSI-Retention-Labels-Policy" |
    Select-Object Name, Enabled, PublishComplianceTag

# Check for policy distribution errors
Get-RetentionCompliancePolicy | Where-Object { $_.DistributionStatus -ne "Success" } |
    Select-Object Name, DistributionStatus, DistributionResults
```

---

## Zone-Specific Verification

### Zone 1 (Personal Productivity)

- [ ] Baseline retention policies applied where applicable
- [ ] Exceptions documented for personal agents
- [ ] Minimal scope beyond user's own data

### Zone 2 (Team Collaboration)

- [ ] Agent knowledge sources follow retention rules
- [ ] Identified owner and approval trail
- [ ] Configuration validated in pilot environment
- [ ] Evidence of label/policy assignment retained

### Zone 3 (Enterprise Managed)

- [ ] Strictest retention configuration enforced via policy
- [ ] Changes controlled (change ticket + documented testing)
- [ ] Evidence retained (screenshots/exports/logs)

---

## Compliance Attestation Template

```markdown
# Retention Management Compliance Attestation

**Control:** 4.3 - Site and Document Retention Management
**Attestation Date:** [Date]
**Attested By:** [Name/Role]

## Policy Status

- [ ] Inactive site policies configured
- [ ] Site ownership policies configured
- [ ] Retention labels published
- [ ] Zone-specific policies applied

## Evidence Collected

| Item | Date Collected | Location |
|------|---------------|----------|
| Policy screenshots | [Date] | [Path] |
| Export of retention configuration | [Date] | [Path] |
| Site retention mapping | [Date] | [Path] |

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
