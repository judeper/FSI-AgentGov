# Control 3.7: PPAC Security Posture Assessment - Verification & Testing

> This playbook provides verification and testing procedures for [Control 3.7](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md).

---

## Verification Steps

### 1. Security Dashboard Access

- Navigate to PPAC > Security
- Verify all four tabs are accessible
- Confirm recommendations are displayed

### 2. Recommendation Accuracy

- Review each recommendation
- Verify status reflects actual configuration
- Confirm risk levels are appropriate

### 3. Report Generation

- Run posture assessment script
- Verify scores calculate correctly
- Confirm report includes all environments

---

## Compliance Checklist

| Item | Required For | Status |
|------|--------------|--------|
| Monthly posture review | Governance policy | |
| All high-risk recommendations addressed | Security baseline | |
| Managed environments enabled | Zone 2-3 | |
| DLP policies applied to all environments | Data protection | |
| Security scores tracked over time | Trend analysis | |

---

## Test Cases

### Test Case 1: Recommendation Status Update

**Objective:** Verify recommendations update when addressed

**Steps:**

1. Note a specific recommendation
2. Implement the recommended change
3. Refresh Security dashboard
4. Verify status changed to "Completed"

**Expected Result:** Recommendation reflects completed status

### Test Case 2: Score Calculation

**Objective:** Verify security score accuracy

**Steps:**

1. Run security posture assessment
2. Manually verify each security control
3. Compare calculated score to expected

**Expected Result:** Scores accurately reflect configuration

### Test Case 3: DLP Coverage Detection

**Objective:** Verify DLP coverage analysis

**Steps:**

1. Create environment without DLP
2. Run DLP coverage check
3. Verify environment flagged as uncovered
4. Apply DLP policy
5. Re-run check

**Expected Result:** Coverage detection is accurate

---

## Evidence Collection

For audits, collect:

- Monthly security posture reports
- Recommendation completion history
- Security score trend data
- DLP coverage documentation

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.2*
