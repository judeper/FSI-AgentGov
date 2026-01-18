# Troubleshooting: Control 2.11 - Bias Testing and Fairness Assessment

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Insufficient test data | Small sample sizes | Expand test dataset |
| Cannot classify outcomes | Subjective responses | Define clear criteria |
| Persistent bias | Model/prompt issues | Adjust prompts or topics |
| Metrics not meaningful | Wrong metrics for use case | Select appropriate metrics |

---

## Detailed Troubleshooting

### Issue: Test Dataset Too Small

**Symptoms:** Metrics not statistically significant

**Resolution:**

1. Generate more synthetic test cases
2. Ensure minimum 500-1000 per group
3. Balance across all protected classes
4. Document methodology

---

### Issue: Bias Detected in Results

**Symptoms:** Significant disparity between groups

**Resolution:**

1. Analyze response patterns for bias source
2. Review knowledge sources for biased content
3. Adjust system prompts for fairness
4. Add explicit fairness instructions
5. Re-test after changes

---

## Escalation Path

1. **AI Governance Lead** - Testing methodology
2. **Data Science Team** - Statistical analysis
3. **Compliance Officer** - Regulatory alignment
4. **Legal** - Fair lending requirements

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| LLM responses variable | Same input may give different output | Run multiple iterations |
| Synthetic data limitations | May not reflect real patterns | Supplement with production sampling |
| Outcome classification subjective | Inconsistent results | Use multiple reviewers |
| No standard FSI fairness tools | Must build custom | Document methodology |

---

[Back to Control 2.11](../../../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
