# Portal Walkthrough: Control 2.11 - Bias Testing and Fairness Assessment

**Last Updated:** January 2026
**Portal:** Custom testing environment, Power BI for analysis
**Estimated Time:** 8-16 hours for initial assessment

## Prerequisites

- [ ] Protected class definitions documented per ECOA
- [ ] Test dataset with demographic distribution
- [ ] Fairness metrics defined
- [ ] Data science team engagement

---

## Step-by-Step Configuration

### Step 1: Define Protected Classes

Document protected classes per ECOA and state law:

| Protected Class | Attribute | Data Source |
|-----------------|-----------|-------------|
| Race | Demographics | Customer profile |
| National Origin | Demographics | Customer profile |
| Sex | Demographics | Customer profile |
| Age | Date of birth | Customer profile |
| Marital Status | Demographics | Customer profile |
| Public Assistance | Income source | Application data |

### Step 2: Create Test Dataset

1. Build representative test dataset:
   - Minimum 1,000 test cases per protected class
   - Balance across demographic groups
   - Use synthetic data (not production customer data)
2. Create standard prompt templates for testing
3. Document dataset methodology

### Step 3: Establish Fairness Metrics

Define metrics to measure:

| Metric | Definition | Threshold |
|--------|------------|-----------|
| Demographic Parity | Equal positive outcome rate across groups | ±5% |
| Equalized Odds | Equal true positive/false positive rates | ±5% |
| Calibration | Predicted probability matches actual outcomes | ±10% |

### Step 4: Execute Bias Testing

1. Run each test case through agent
2. Capture agent response
3. Classify response as positive/negative outcome
4. Calculate metrics by demographic group

### Step 5: Document and Remediate

1. Generate bias testing report with statistics
2. Identify significant disparities
3. Create remediation plan for bias issues
4. Re-test after remediation

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **Testing Frequency** | Annual | Pre-deployment | Pre-deployment + Quarterly |
| **Test Dataset Size** | 500/group | 1,000/group | 2,000/group |
| **Metrics** | Demographic parity | + Equalized odds | Comprehensive |
| **Documentation** | Summary | Full report | Independent validation |
| **Remediation SLA** | 30 days | 14 days | 7 days critical |

---

## FSI Example Configuration

```yaml
Bias Testing: Investment Advisory Bot

Protected Classes:
  - Race (5 categories)
  - Sex (2 categories)
  - Age (4 brackets: 18-35, 36-50, 51-65, 65+)

Test Dataset:
  Total Size: 8,000 cases
  Per Group: 1,000 minimum
  Source: Synthetic generated

Fairness Metrics:
  - Demographic Parity: Pass/Fail at ±5%
  - Equalized Odds: Pass/Fail at ±5%
  - Calibration: Pass/Fail at ±10%

Testing Schedule:
  - Pre-deployment: Required
  - Quarterly: Required for Zone 3
  - After significant changes: Required
```

---

## Validation

After completing these steps, verify:

- [ ] Protected classes documented per ECOA
- [ ] Test dataset created with representation
- [ ] Fairness metrics established
- [ ] Initial bias testing completed
- [ ] Results documented with remediation plan

---

[Back to Control 2.11](../../../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
