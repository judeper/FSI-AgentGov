# Troubleshooting: Control 2.18 - Automated Conflict of Interest Testing

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Tests not running | Schedule misconfigured or auth failure | Check schedule; verify API credentials |
| High false positive rate | Test criteria too strict | Tune evaluation criteria; add context |
| Agent responses inconsistent | Non-deterministic generation | Run multiple iterations; use averages |
| Test coverage gaps | Missing scenarios | Review with compliance; add test cases |
| Results not retained | Storage configuration error | Check storage permissions and paths |

---

## Detailed Troubleshooting

### Issue: Tests Not Executing on Schedule

**Symptoms:** Automated tests don't run at scheduled times

**Diagnostic Steps:**

1. Check automation schedule:
   - Power Automate: Flow run history
   - Custom: Task scheduler logs

2. Verify API authentication:
   - Check credentials are valid
   - Verify API endpoint is accessible

3. Check for execution errors in logs

**Resolution:**

- Correct schedule configuration
- Update expired credentials
- Fix connectivity issues
- Re-enable disabled automations

---

### Issue: High False Positive Rate

**Symptoms:** Tests fail but agent behavior appears acceptable on manual review

**Diagnostic Steps:**

1. Review failure details:
   - What criteria triggered failure?
   - Is the agent response actually problematic?

2. Check test criteria:
   - Are patterns too strict?
   - Is context being considered?

3. Review sample failures with compliance team

**Resolution:**

- Adjust evaluation criteria
- Add more context to test prompts
- Use semantic analysis vs. keyword matching
- Implement confidence thresholds

---

### Issue: Inconsistent Agent Responses

**Symptoms:** Same test sometimes passes, sometimes fails

**Diagnostic Steps:**

1. Understand agent response variability:
   - LLM responses have inherent variability
   - Same prompt may yield different wording

2. Check if meaning is consistent even if wording varies

3. Review test evaluation logic

**Resolution:**

- Run tests multiple times and use aggregate results
- Use semantic similarity vs. exact matching
- Set pass threshold (e.g., 8/10 runs pass)
- Focus on meaning, not specific wording

---

### Issue: Coverage Gaps Identified

**Symptoms:** Compliance identifies COI scenarios not covered by tests

**Diagnostic Steps:**

1. Review current test inventory against regulatory requirements

2. Identify specific missing scenarios

3. Assess risk of gaps

**Resolution:**

- Add test cases for missing scenarios
- Prioritize based on risk
- Review test coverage quarterly with compliance
- Document coverage rationale

---

## How to Confirm Configuration is Active

### Test Automation

1. Check recent execution history
2. Verify results are being captured
3. Confirm alerts are configured

### Test Coverage

1. Review test case inventory
2. Map to COI categories
3. Verify all categories have coverage

### Compliance Reporting

1. Generate a test report
2. Verify data is current
3. Confirm report reaches compliance team

---

## Escalation Path

If issues persist after troubleshooting:

1. **QA/Test Team** - Test framework issues
2. **AI/ML Team** - Agent behavior analysis
3. **Compliance** - Test criteria and coverage
4. **AI Governance Lead** - Policy questions

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| LLM response variability | Test results may vary | Use aggregate scoring |
| No built-in COI detection | Requires custom implementation | Build evaluation criteria |
| Semantic analysis complexity | Hard to detect subtle bias | Combine automated and manual review |
| Test maintenance burden | Tests may become stale | Schedule quarterly test review |

---

[Back to Control 2.18](../../../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
