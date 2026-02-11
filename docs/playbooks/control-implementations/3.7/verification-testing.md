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

## SSPM Configuration Verification

!!! abstract "Security Posture Assessment Test Cases"

    The following test cases validate configuration points flagged by security posture assessments. Each test maps to a specific setting in the [Configuration Hardening Baseline](../../advanced-implementations/configuration-hardening-baseline/index.md).

| Test ID | Configuration Point | Expected Result | Portal Path | Evidence |
|---------|-------------------|-----------------|-------------|----------|
| SSPM-3.7-01 | Hardening baseline review | Review completed per documented cadence (weekly Zone 3, bi-weekly Zone 2, monthly Zone 1) | N/A (process-based) | Review log |
| SSPM-3.7-02 | Configuration drift | No unresolved configuration drift items | N/A (process-based) | Drift report |
| SSPM-3.7-03 | Evidence archival | Evidence archived with SHA-256 hash per review cycle | N/A (process-based) | Hash manifest |

### Test Procedures

**SSPM-3.7-01: Hardening Baseline Review Cadence**

1. Locate the most recent hardening baseline review record (see [Configuration Hardening Baseline](../../advanced-implementations/configuration-hardening-baseline/index.md))
2. Verify the review was completed within the required cadence:
    - Zone 1 (Personal Productivity): Monthly review
    - Zone 2 (Team Collaboration): Bi-weekly review
    - Zone 3 (Enterprise Managed): Weekly review
3. **Pass criteria:** Most recent review date falls within the cadence window for each applicable zone
4. **Evidence:** Review log showing reviewer name, date, and zone coverage

**SSPM-3.7-02: Configuration Drift**

1. Review the most recent hardening baseline assessment output
2. Identify any configuration items flagged as drifted from expected values
3. Verify all drift items have either been remediated or have documented exceptions
4. **Pass criteria:** No unresolved configuration drift items — all findings are remediated or accepted with documented risk
5. **Evidence:** Drift report showing all items in compliant or accepted-risk state

**SSPM-3.7-03: Evidence Archival**

1. Locate the evidence archive for the most recent review cycle
2. Verify each archived evidence file has a SHA-256 hash recorded
3. Verify the hash manifest is stored alongside the evidence package
4. **Pass criteria:** Evidence package is complete with SHA-256 hash manifest for the current review cycle
5. **Evidence:** Hash manifest file showing filenames and corresponding SHA-256 values

---

*Updated: February 2026 | Version: v1.3 | Classification: Verification Testing*
