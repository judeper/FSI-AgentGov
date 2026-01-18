# Verification & Testing: Control 2.11 - Bias Testing and Fairness Assessment

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Protected Classes Documented

1. Request protected class documentation
2. Verify alignment with ECOA requirements
3. **EXPECTED:** All required classes documented

### Test 2: Verify Test Dataset

1. Review test dataset composition
2. Verify demographic representation
3. **EXPECTED:** Balanced dataset with minimum counts per group

### Test 3: Review Bias Testing Results

1. Request most recent bias testing report
2. Review fairness metrics results
3. **EXPECTED:** Report with statistical analysis

### Test 4: Verify Remediation Process

1. Check for any identified bias issues
2. Verify remediation plans exist
3. **EXPECTED:** Issues tracked with remediation timeline

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
