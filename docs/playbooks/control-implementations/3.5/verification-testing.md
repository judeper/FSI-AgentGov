# Control 3.5: Cost Allocation and Budget Tracking - Verification & Testing

> This playbook provides verification and testing procedures for [Control 3.5](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md).

---

## Verification Steps

### 1. Capacity Visibility

- Access Power Platform Admin Center capacity view
- Verify all environments visible with correct sizing
- Confirm business unit tagging is accurate

### 2. Cost Allocation Accuracy

- Generate cost report by business unit
- Verify costs align with actual usage
- Confirm rate card is applied correctly

### 3. Budget Alerts

- Create test budget with low threshold
- Verify alert emails are received
- Confirm escalation chain is notified

### 4. Chargeback Process

- Generate monthly chargeback report
- Verify cost center mapping
- Confirm Finance receives report

---

## Compliance Checklist

| Item | Required For | Status |
|------|--------------|--------|
| Cost tracking by business unit | SOX 404 | |
| Monthly chargeback reports | Internal governance | |
| Budget alerts configured | Cost management | |
| License utilization tracking | Asset management | |
| 12-month cost trend data | Planning | |
| Approval workflow for overages | Budget control | |

---

## Test Cases

### Test Case 1: Cost Visibility

**Objective:** Verify all AI costs are captured and attributed

**Steps:**

1. Generate cost report for all business units
2. Compare total to Azure and M365 billing
3. Verify variance is <5%

**Expected Result:** Complete cost capture with accurate attribution

### Test Case 2: Budget Alert Triggering

**Objective:** Verify budget alerts fire at configured thresholds

**Steps:**

1. Set test budget at $100
2. Generate usage exceeding $50 (50%)
3. Verify 50% alert received
4. Continue to 75% and 100%

**Expected Result:** Alerts received at each threshold

### Test Case 3: Chargeback Report Accuracy

**Objective:** Verify chargeback reports align with actual costs

**Steps:**

1. Generate chargeback report for prior month
2. Compare to Azure Cost Management export
3. Verify totals match within 1%

**Expected Result:** Chargeback accurately reflects actual costs

### Test Case 4: License Utilization

**Objective:** Verify license utilization tracking works

**Steps:**

1. Generate license utilization report
2. Compare active users to assigned licenses
3. Identify under-utilized licenses (>30 days inactive)

**Expected Result:** Clear view of license efficiency

---

## Evidence Collection

For audits, collect:

- Monthly chargeback reports (12 months)
- Budget vs. actual variance reports
- License utilization trends
- Cost allocation methodology documentation
- Finance approval of rate cards

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.1*
