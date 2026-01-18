# Control 3.3: Compliance and Regulatory Reporting - Verification & Testing

> This playbook provides verification and testing procedures for [Control 3.3](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md).

---

## Verification Steps

### 1. Report Generation

- Execute weekly control status report
- Verify all 60 controls appear with accurate status
- Confirm pillar scores calculate correctly

### 2. Distribution Workflow

- Send test report to distribution list
- Verify approval workflow triggers
- Confirm archive to SharePoint succeeds

### 3. Regulatory Alignment

- Review control-to-regulation mapping
- Verify evidence links are valid
- Test examination package generation

### 4. Dashboard Accuracy

- Compare dashboard metrics to source data
- Verify trend calculations are correct
- Test drill-down functionality

---

## Compliance Checklist

| Item | Required For | Status |
|------|--------------|--------|
| Weekly control status reports | Internal governance | |
| Monthly executive dashboard | SOX 302/404 | |
| Quarterly audit packages | External audit | |
| Examination ready packages | FINRA/SEC/OCC | |
| 7-year report retention | FINRA 4511, SEC 17a-4 | |
| Executive sign-off workflow | SOX 302 | |
| Automated report generation | Operational efficiency | |

---

## Test Cases

### Test Case 1: Weekly Report Generation

**Objective:** Verify automated weekly report generates correctly

**Steps:**

1. Trigger weekly report flow manually
2. Verify report contains all four pillars
3. Check compliance scores are calculated
4. Confirm report is saved to SharePoint

**Expected Result:** Report generates with accurate data and archives successfully

### Test Case 2: Approval Workflow

**Objective:** Verify monthly report requires CCO approval

**Steps:**

1. Generate monthly regulatory report
2. Verify approval request sent to CCO
3. Approve the report
4. Confirm report distributes to recipients

**Expected Result:** Report held until approval, then distributed

### Test Case 3: Examination Package

**Objective:** Verify regulator-specific packages include correct documents

**Steps:**

1. Generate FINRA examination package
2. Verify all 8 required documents listed in manifest
3. Generate SEC package
4. Verify different document set

**Expected Result:** Each regulator package contains appropriate documents

---

## Evidence Collection

For regulatory examinations, collect:

- Screenshot of Compliance Manager dashboard
- Export of control status report
- SharePoint archive showing report retention
- Power Automate flow run history
- Approval workflow completion records

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.1*
