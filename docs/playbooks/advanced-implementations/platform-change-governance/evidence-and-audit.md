# Platform Change Governance - Evidence and Audit

**Status:** January 2026 - FSI-AgentGov v1.2
**Related Controls:** 2.3 (Change Management), 2.10 (Patch Management), 2.13 (Documentation)

---

## Overview

This document maps Platform Change Governance artifacts to FSI regulatory requirements and evidence standards. All governance decisions must be retained and available for regulatory examination.

---

## Regulatory Alignment

### Primary Regulations

| Regulation | Requirement | How PCG Addresses |
|------------|-------------|-------------------|
| **FINRA 4511** | Books and records of business activities for 6 years | DecisionLog table with immutable records, Dataverse auditing captures all field changes |
| **SEC 17a-3/4** | Records preservation in WORM or audit-trail alternative format | Dataverse change tracking provides audit trail; quarterly export to compliant storage |
| **SOX 302/404** | Internal control assessment and management certification | Documented approval workflows with segregation of duties |
| **GLBA 501(b)** | Administrative safeguards for customer information systems | Controlled change process protects customer-impacting platform changes |

### Secondary Regulations

| Regulation | Applicability | Evidence Required |
|------------|---------------|-------------------|
| **OCC 2011-12** | Model risk if AI/ML components affected | Decision rationale for changes impacting AI systems |
| **Fed SR 11-7** | Model risk management | Change assessment documentation |
| **CFTC 1.31** | Electronic recordkeeping (if applicable) | Same evidence as SEC 17a-4 |

---

## Evidence Categories

### Primary Evidence

| Evidence Type | Source | Capture Method | Retention |
|---------------|--------|----------------|-----------|
| **Governance Decisions** | DecisionLog table | Automatic (Dataverse record) | 6 years |
| **Decision Rationale** | DecisionLog.dl_decisionrationale | Automatic (required field) | 6 years |
| **Assessment History** | AssessmentLog table | Automatic (user-created records) | 6 years |
| **State Transitions** | Dataverse Audit Logs | Automatic (auditing enabled) | 3 years + archive |
| **Approver Identity** | DecisionLog.dl_decidedby | Automatic (system-captured) | 6 years |

### Secondary Evidence

| Evidence Type | Source | Capture Method | Retention |
|---------------|--------|----------------|-----------|
| **Original Post Content** | MessageCenterPost.mc_body | Automatic (ingestion flow) | 3 years |
| **Timing Evidence** | Timestamps on all records | Automatic (system fields) | Per record retention |
| **ADO Execution (Path B)** | dl_ado_workitem_url | Automatic (sync flow) | Per ADO retention |
| **Flow Run History** | Power Automate | Automatic (28 days) | Manual export for longer |

---

## Evidence Collection Procedures

### Daily Operations (Automatic)

No manual intervention required for daily evidence collection:

- Dataverse automatically timestamps all record operations
- Audit logs capture field-level changes
- DecisionLog records are immutable after creation

### Quarterly Evidence Export

Execute quarterly to ensure long-term retention compliance:

**Step 1: Export DecisionLog Records**

1. Open model-driven app
2. Navigate to **Decision Log** → **All Decision Logs**
3. Filter: Created On within quarter
4. Click **Export to Excel**
5. Save as: `PCG-DecisionLog-{Environment}-{YYYYQQ}.xlsx`

**Step 2: Export Audit Logs**

1. Go to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Select environment → **Audit** → **Audit Summary View**
3. Filter:
   - Entity: Message Center Post, Assessment Log, Decision Log
   - Date range: Quarter dates
4. Export to CSV
5. Save as: `PCG-AuditLog-{Environment}-{YYYYQQ}.csv`

**Step 3: Export MessageCenterPost Records**

1. Export posts with State = Closed during quarter
2. Save as: `PCG-ClosedPosts-{Environment}-{YYYYQQ}.xlsx`

**Step 4: Archive to Compliant Storage**

1. Create folder in SharePoint compliance library: `PCG-Evidence/{YYYY}/{QQ}/`
2. Upload all exports
3. Apply retention label: `FSI-6Year-Retention`
4. Document export completion in evidence log

### Annual Evidence Verification

**Verification Checklist:**

- [ ] All quarters have complete evidence exports
- [ ] No gaps in audit log coverage
- [ ] Retention labels applied to all evidence files
- [ ] Access permissions verified (Compliance + Legal only)
- [ ] Sample verification: Pull 5 random decisions, verify complete audit trail
- [ ] Reconcile: DecisionLog count matches closed MessageCenterPost count

---

## Evidence Naming Convention

All evidence files follow this naming pattern:

```
PCG-{EvidenceType}-{Environment}-{DateRange}.{extension}
```

| Component | Values | Example |
|-----------|--------|---------|
| Prefix | PCG (Platform Change Governance) | PCG |
| Evidence Type | DecisionLog, AuditLog, ClosedPosts, Assessment | DecisionLog |
| Environment | Prod, Test, Dev | Prod |
| Date Range | YYYYMMDD or YYYYQQ | 2026Q1 |
| Extension | xlsx, csv, pdf, json | xlsx |

**Examples:**

- `PCG-DecisionLog-Prod-2026Q1.xlsx`
- `PCG-AuditLog-Prod-20260101-20260331.csv`
- `PCG-Assessment-Prod-MC123456.pdf`

---

## Audit Trail Configuration

### Dataverse Auditing

Ensure auditing is properly configured:

**Environment-Level Settings:**

1. Power Platform Admin Center → Environment → Settings
2. **Audit and logs** → **Audit settings**
3. Enable:
   - [x] Start Auditing
   - [x] Audit user access

**Table-Level Settings:**

For MessageCenterPost, AssessmentLog, DecisionLog:

1. Open table → **Properties** (gear icon)
2. **Advanced options** → Enable **Audit changes to its data**

**Column-Level Settings (Optional):**

For sensitive columns, enable explicit column auditing:

1. Open column properties
2. Enable **Auditing**

### Audit Log Retention

| Retention Period | Storage Location | Access |
|------------------|------------------|--------|
| 0-90 days | Dataverse (online) | All authorized users |
| 90 days - 3 years | Dataverse (archived) | Admin query |
| 3-6 years | SharePoint compliance library | Compliance + Legal |

---

## Microsoft Purview Integration

### Retention Labels

Create and apply retention labels for PCG evidence:

**Label 1: FSI-PCG-6Year**

```
Name: FSI-PCG-6Year
Description: Platform Change Governance evidence - 6 year retention
Retention period: 6 years from creation
At end of retention: Delete automatically
Apply to: SharePoint, OneDrive
```

**Label 2: FSI-PCG-DecisionLog**

```
Name: FSI-PCG-DecisionLog
Description: Immutable governance decision records
Retention period: 6 years from creation
Disposition: Review required
Apply to: Dataverse exports
```

### Auto-Labeling Policy (Optional)

Configure auto-labeling for PCG evidence:

1. Go to [Microsoft Purview Compliance Portal](https://compliance.microsoft.com)
2. **Information protection** → **Auto-labeling**
3. Create policy:
   - Name: `PCG Evidence Auto-Label`
   - Conditions: File name contains "PCG-" AND location is compliance library
   - Label: FSI-PCG-6Year

### eDiscovery Considerations

PCG evidence may be subject to legal hold:

1. **Content Search:** DecisionLog and related records searchable via Purview
2. **Legal Hold:** Apply hold to compliance SharePoint site during litigation
3. **Export:** Use Purview eDiscovery for examination requests

---

## Examination Response Guide

### Pre-Examination Preparation

**30 Days Before Expected Examination:**

1. Run quarterly evidence export (if not current)
2. Verify evidence completeness checklist
3. Test evidence retrieval procedures
4. Brief designated custodians on PCG evidence locations

### Common Examiner Requests

| Request Type | Evidence Source | Response Time |
|--------------|-----------------|---------------|
| "Show us how platform changes are tracked" | Live demo of model-driven app | Immediate |
| "Provide decision records for Q3" | PCG-DecisionLog export | Same day |
| "Show audit trail for specific decision" | Dataverse audit log + screenshot | Same day |
| "Evidence of segregation of duties" | Security role configuration export | Same day |
| "Historical change records (2+ years)" | SharePoint compliance library | 1-2 days |

### Sample Examiner Questions and Evidence

| Question | Evidence to Provide |
|----------|---------------------|
| "How do you ensure changes are approved before implementation?" | DecisionLog records showing Decision + Rationale fields, workflow state machine documentation |
| "Who has authority to approve platform changes?" | Security role assignments, segregation of duties configuration |
| "How long do you retain decision records?" | Retention label configuration, evidence export schedule |
| "Can users modify decisions after the fact?" | Organization-owned table configuration (read-only), audit log showing no modifications |
| "How do you handle urgent changes?" | Decision records with State = Escalate, approval workflow for escalated decisions |

---

## Quarterly Evidence Export Script

PowerShell script for automated evidence export:

```powershell
<#
.SYNOPSIS
    Exports Platform Change Governance evidence for quarterly retention.
.DESCRIPTION
    Connects to Dataverse, exports DecisionLog, AssessmentLog, and closed posts,
    then uploads to SharePoint compliance library.
.PARAMETER EnvironmentUrl
    Dataverse environment URL (e.g., https://org.crm.dynamics.com)
.PARAMETER Quarter
    Quarter to export (e.g., 2026Q1)
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentUrl,

    [Parameter(Mandatory=$true)]
    [string]$Quarter
)

# Parse quarter to date range
$year = [int]$Quarter.Substring(0,4)
$q = [int]$Quarter.Substring(5,1)
$startDate = Get-Date -Year $year -Month (($q-1)*3+1) -Day 1
$endDate = $startDate.AddMonths(3).AddDays(-1)

Write-Host "Exporting PCG evidence for $Quarter ($startDate to $endDate)"

# Connect to Dataverse (requires Microsoft.PowerApps.Administration.PowerShell)
Connect-CrmOnline -ServerUrl $EnvironmentUrl

# Export DecisionLog
$decisionLogs = Get-CrmRecords -EntityLogicalName "mc_decisionlog" `
    -FilterAttribute "createdon" `
    -FilterOperator "between" `
    -FilterValue @($startDate, $endDate) `
    -Fields @("dl_decision", "dl_decisionrationale", "dl_decidedby", "dl_decidedon")

$decisionLogs | Export-Csv "PCG-DecisionLog-Prod-$Quarter.csv" -NoTypeInformation

# Export AssessmentLog
$assessmentLogs = Get-CrmRecords -EntityLogicalName "mc_assessmentlog" `
    -FilterAttribute "createdon" `
    -FilterOperator "between" `
    -FilterValue @($startDate, $endDate)

$assessmentLogs | Export-Csv "PCG-AssessmentLog-Prod-$Quarter.csv" -NoTypeInformation

# Export closed MessageCenterPosts
$closedPosts = Get-CrmRecords -EntityLogicalName "mc_messagecenterpost" `
    -FilterAttribute "mc_state" `
    -FilterOperator "eq" `
    -FilterValue "Closed"

$closedPosts | Export-Csv "PCG-ClosedPosts-Prod-$Quarter.csv" -NoTypeInformation

Write-Host "Evidence export complete. Files ready for upload to compliance library."
```

---

## Evidence Retention Schedule

| Evidence Category | Dataverse (Hot) | SharePoint (Warm) | Archive (Cold) | Total |
|-------------------|-----------------|-------------------|----------------|-------|
| DecisionLog | 3 years | 3 years | - | 6 years |
| AssessmentLog | 3 years | 3 years | - | 6 years |
| MessageCenterPost | 2 years | 1 year | - | 3 years |
| Audit Logs | 90 days | 2.75 years | 3 years | 6 years |
| Flow Run History | 28 days | Manual export | - | As needed |
| ADO Work Items | Per ADO policy | - | - | Per ADO |

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [Evidence Standards](../../../reference/evidence-standards.md) | Framework-wide evidence standards |
| [Overview](index.md) | Playbook introduction |
| [Architecture](architecture.md) | Technical design including audit configuration |
| [Control 2.13 - Documentation](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Record-keeping requirements |
| [Evidence Pack Assembly](../../compliance-and-audit/evidence-pack-assembly.md) | Examination evidence assembly |

---

*FSI Agent Governance Framework v1.2 - January 2026*
