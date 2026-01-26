# Control 3.9: Microsoft Sentinel Integration - Verification & Testing

> This playbook provides verification and testing procedures for [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

---

## Verification Steps

### 1. Data Connector Status

- Verify all connectors show "Connected"
- Confirm data flowing (check last log received)
- Validate required tables populated

### 2. Analytics Rules

- Verify rules are enabled
- Test rules trigger on test data
- Confirm alerts create correctly

### 3. Workbook Display

- Verify workbook loads without errors
- Confirm visualizations show data
- Test time range filters work

### 4. Automation Rules

- Trigger test alert
- Verify automation executes
- Confirm notification received

---

## Compliance Checklist

| Item | Required For | Status |
|------|--------------|--------|
| Sentinel workspace deployed | Security monitoring | |
| M365 Defender connector enabled | Threat detection | |
| Agent analytics rules active | Anomaly detection | |
| DLP violation detection rule | Data protection | |
| Automated response configured | Incident response | |
| Workbook created and shared | Visibility | |
| Hunting queries saved | Proactive investigation | |

---

## Test Cases

### Test Case 1: Alert Generation

**Objective:** Verify analytics rules generate alerts

**Steps:**

1. Trigger unusual agent activity (test environment)
2. Wait for rule execution cycle
3. Check Incidents for new alert
4. Verify alert details are correct

**Expected Result:** Alert created with accurate details

### Test Case 2: Automated Response

**Objective:** Verify automation rules execute

**Steps:**

1. Generate high-severity test alert
2. Verify automation rule triggers
3. Confirm action executes (e.g., email sent)
4. Check incident assignment

**Expected Result:** Automated actions complete successfully

### Test Case 3: Workbook Accuracy

**Objective:** Verify workbook data is accurate

**Steps:**

1. Run KQL query manually
2. Compare to workbook visualization
3. Verify counts match
4. Test different time ranges

**Expected Result:** Workbook displays accurate data

---

## Evidence Collection

For audits, collect:

- Data connector status screenshots
- Analytics rule configuration export
- Sample incident records
- Automation rule execution logs
- Workbook export

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.2*
