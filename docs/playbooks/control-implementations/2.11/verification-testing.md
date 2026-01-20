# Verification & Testing: Control 2.11 - Bias Testing and Fairness Assessment

**Last Updated:** January 2026

## ECOA Protected Classes Reference

The Equal Credit Opportunity Act (ECOA) and Regulation B prohibit discrimination based on the following **9 protected classes**. All bias testing must evaluate agent outputs across these categories:

| # | Protected Class | ECOA Citation | Testing Considerations |
|---|-----------------|---------------|------------------------|
| 1 | **Race** | 15 U.S.C. § 1691(a)(1) | Include all racial categories per Census definitions |
| 2 | **Color** | 15 U.S.C. § 1691(a)(1) | Distinct from race; test skin tone proxies |
| 3 | **Religion** | 15 U.S.C. § 1691(a)(1) | Include major religions and non-religious |
| 4 | **National Origin** | 15 U.S.C. § 1691(a)(1) | Include country of birth, ancestry, ethnicity |
| 5 | **Sex** | 15 U.S.C. § 1691(a)(1) | Include gender identity per recent guidance |
| 6 | **Marital Status** | 15 U.S.C. § 1691(a)(1) | Single, married, divorced, widowed, separated |
| 7 | **Age** | 15 U.S.C. § 1691(a)(1) | Protect applicants who can legally contract |
| 8 | **Public Assistance** | 15 U.S.C. § 1691(a)(2) | Recipients of public assistance income |
| 9 | **Good Faith Exercise of CCPA Rights** | 15 U.S.C. § 1691(a)(3) | Applicants who exercised consumer rights |

**Note:** State laws may add additional protected classes (e.g., sexual orientation, gender identity, military status). Consult legal counsel for your jurisdiction.

---

## Quarterly Testing Requirements

For Zone 3 agents making or influencing credit/lending decisions, conduct **quarterly** bias assessments:

### Quarterly Testing Checklist

| Quarter | Due Date | Activities | Owner |
|---------|----------|------------|-------|
| Q1 | March 31 | Full bias assessment across all 9 classes | AI Governance Lead |
| Q2 | June 30 | Statistical parity review + remediation follow-up | Compliance Officer |
| Q3 | September 30 | Full bias assessment + annual trend analysis | AI Governance Lead |
| Q4 | December 31 | Statistical parity review + annual summary report | Compliance Officer |

### Minimum Sample Sizes per Protected Class

| Class Category | Minimum n per Group | Statistical Test |
|----------------|---------------------|------------------|
| Binary (e.g., sex) | 100 | Chi-square, Fisher's exact |
| Multi-category (e.g., race) | 50 per category | ANOVA, Kruskal-Wallis |
| Continuous (e.g., age) | 200 total | Regression analysis |

---

## Manual Verification Steps

### Test 1: Verify Protected Classes Documented

1. Request protected class documentation
2. Verify all 9 ECOA classes are included
3. Verify any additional state-specific classes
4. **EXPECTED:** All 9 ECOA classes + applicable state classes documented

### Test 2: Verify Test Dataset

1. Review test dataset composition
2. Verify demographic representation across all 9 protected classes
3. Verify minimum sample sizes per group (see table above)
4. **EXPECTED:** Balanced dataset with minimum counts per group

### Test 3: Review Bias Testing Results

1. Request most recent quarterly bias testing report
2. Review fairness metrics: demographic parity, equalized odds
3. Verify statistical significance testing was performed
4. **EXPECTED:** Report with statistical analysis for each protected class

### Test 4: Verify Remediation Process

1. Check for any identified bias issues
2. Verify remediation plans exist with specific actions
3. Verify remediation timeline (max 90 days for material issues)
4. **EXPECTED:** Issues tracked with remediation timeline and owner

### Test 5: Verify Quarterly Cadence (Zone 3)

1. Request testing schedule documentation
2. Verify quarterly assessments are scheduled
3. Review last 4 quarters of testing evidence
4. **EXPECTED:** Consistent quarterly testing with documented results

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-2.11-01 | Protected classes documented | ECOA alignment | |
| TC-2.11-02 | Test dataset representative | Balanced groups | |
| TC-2.11-03 | Demographic parity | Within ±5% | |
| TC-2.11-04 | Equalized odds | Within ±5% | |
| TC-2.11-05 | Remediation tracked | Plans documented | |

---

## Evidence Collection Checklist

- [ ] Document: Protected class definitions
- [ ] Document: Test dataset methodology
- [ ] Export: Bias testing results (CSV)
- [ ] Document: Fairness metrics report
- [ ] Document: Remediation plan (if issues found)

---

## Attestation Statement Template

```markdown
## Control 2.11 Attestation - Bias Testing

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Protected classes are documented per ECOA requirements
2. Test dataset includes representative demographic distribution:
   - Total test cases: [Count]
   - Groups tested: [Count]
3. Bias testing was executed with the following results:
   - Demographic Parity: [Pass/Fail]
   - Equalized Odds: [Pass/Fail]
   - Issues Identified: [Count]
4. Remediation plans exist for identified bias issues
   - SLA: [Days]
   - Status: [In progress/Complete]

**Last Test Date:** [Date]
**Next Scheduled Test:** [Date]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 2.11](../../../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
