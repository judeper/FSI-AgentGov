# Control 4.5: SharePoint Security and Compliance Monitoring - Verification & Testing

> This playbook provides verification and testing guidance for [Control 4.5](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md).

---

## Test Procedure

### Step 1: Verify Dashboard Access

1. Navigate to SharePoint Admin Center > Home
2. Verify dashboard cards are displaying data
3. Confirm no errors or missing data

### Step 2: Verify Agent Insights

1. Navigate to Reports > Agent insights
2. Click "View reports" for both agent reports
3. Verify agent inventory is populated
4. Confirm agent access patterns are visible

### Step 3: Verify Data Access Governance

1. Navigate to Reports > Data access governance
2. Run "Site permissions across your organization" report
3. Verify report generates successfully
4. Export sample data for validation

### Step 4: Verify Advanced Management

1. Navigate to Advanced management
2. Review assessment results
3. Confirm oversharing assessment data is available

---

## Expected Results Checklist

- [ ] Home dashboard displays current metrics
- [ ] Agent insights reports show agent inventory
- [ ] Agent access report shows content access patterns
- [ ] Data access governance reports generate successfully
- [ ] Advanced management assessments complete

---

## Verification Evidence

| Evidence Type | Location | Retention |
|---------------|----------|-----------|
| Dashboard screenshot | Home page | Weekly |
| Agent insights report export | Agent insights | Monthly |
| Permissions report export | Data access governance | Monthly |
| Assessment results | Advanced management | Quarterly |

---

## Zone-Specific Verification

### Zone 1 (Personal Productivity)

- [ ] Baseline monitoring applied where tenant-wide safety requires
- [ ] Monthly review of Agent insights
- [ ] Weekly dashboard review

### Zone 2 (Team Collaboration)

- [ ] Weekly Agent access report review
- [ ] Monthly data access governance reports
- [ ] Alert on high severity events
- [ ] Evidence retained (screenshots/exports/logs)

### Zone 3 (Enterprise Managed)

- [ ] Daily agent access monitoring
- [ ] Continuous security dashboard review
- [ ] SIEM/SOC integration configured
- [ ] Automated response enabled

---

## PowerShell Validation

```powershell
# Verify licensing for SharePoint Advanced Management
Get-MgSubscribedSku | Where-Object {
    $_.SkuPartNumber -like "*SPE_E5*" -or
    $_.SkuPartNumber -like "*SHAREPOINTENTERPRISE*"
}

# Check audit logging status
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled

# Verify SharePoint Admin access
Get-MgUserMemberOf -UserId "admin@contoso.com" |
    Where-Object { $_.AdditionalProperties.displayName -like "*SharePoint*" }

# Test audit log search
$testSearch = Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-1) -EndDate (Get-Date) `
    -RecordType SharePoint -ResultSize 10
Write-Host "Audit log search returned $($testSearch.Count) events"
```

---

## Compliance Attestation Template

```markdown
# SharePoint Monitoring Compliance Attestation

**Control:** 4.5 - SharePoint Security and Compliance Monitoring
**Attestation Date:** [Date]
**Attested By:** [Name/Role]

## Monitoring Status

- [ ] Agent insights reports accessible
- [ ] Data access governance reports configured
- [ ] Advanced management assessments running
- [ ] Unified audit logging enabled

## Evidence Collected

| Item | Date Collected | Location |
|------|---------------|----------|
| Dashboard screenshot | [Date] | [Path] |
| Agent insights export | [Date] | [Path] |
| Permissions report | [Date] | [Path] |
| Audit log sample | [Date] | [Path] |

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
