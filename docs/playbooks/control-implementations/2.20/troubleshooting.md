# Troubleshooting: Control 2.20 - Adversarial Testing and Red Team Framework

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Test environment has production data | Improper setup or data leak | Wipe and recreate environment; review data handling |
| Agent behaving differently than production | Configuration drift | Re-sync from production; document differences |
| High false positive rate | Test criteria too strict | Tune detection patterns; add context |
| Vulnerabilities not being remediated | Process gap or resource constraint | Escalate to security leadership; prioritize |
| Test results not captured | Logging configuration error | Verify audit logging; fix connection |

---

## Detailed Troubleshooting

### Issue: Test Environment Has Production Data

**Symptoms:** Production customer data visible in test environment

**Diagnostic Steps:**

1. Immediately stop all testing

2. Identify data scope:
   - What data is present?
   - How did it get there?
   - Who has accessed it?

3. Document for incident response

**Resolution:**

- Treat as potential data incident
- Wipe test environment completely
- Recreate with synthetic data only
- Review data handling procedures
- Implement data validation checks

---

### Issue: Agent Behavior Different from Production

**Symptoms:** Test results may not reflect production vulnerabilities

**Diagnostic Steps:**

1. Compare agent configurations:
   - Topics
   - Knowledge sources
   - Settings

2. Check environment configuration:
   - DLP policies
   - Managed Environment settings

3. Verify agent version matches production

**Resolution:**

- Document and accept differences, or
- Re-deploy exact production configuration
- Create synchronization process
- Consider production testing with safeguards

---

### Issue: Too Many False Positives

**Symptoms:** Tests flag as "vulnerable" but agent behaves appropriately

**Diagnostic Steps:**

1. Review test evaluation criteria:
   - Are patterns too broad?
   - Is context being ignored?

2. Manual review of flagged responses:
   - Is the response actually problematic?
   - What triggered the flag?

3. Refine detection patterns

**Resolution:**

- Tune success/failure indicators
- Add negative indicators (things that prove defense worked)
- Use semantic analysis vs. keyword matching
- Review with security team

---

### Issue: Vulnerabilities Not Remediated

**Symptoms:** Known vulnerabilities remain open past SLA

**Diagnostic Steps:**

1. Check remediation tracking:
   - Is vulnerability assigned?
   - What is the blocker?

2. Review resource allocation:
   - Is team aware of SLA?
   - Are resources available?

3. Assess risk of open vulnerabilities

**Resolution:**

- Escalate to security leadership
- Re-prioritize based on risk
- Consider compensating controls
- Accept risk formally if necessary (document)

---

## How to Confirm Configuration is Active

### Test Environment

1. Access test environment
2. Verify no production data
3. Confirm test agent is current

### Attack Scenarios

1. Review scenario library
2. Verify scenarios are up to date
3. Confirm coverage across categories

### Testing Schedule

1. Check schedule documentation
2. Verify last test date
3. Confirm next scheduled test

---

## Escalation Path

If issues persist after troubleshooting:

1. **Security Team** - Vulnerability assessment
2. **AI Governance Lead** - Program questions
3. **CISO** - Critical vulnerabilities
4. **External Security Firm** - Additional expertise

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| No native red team tools | Must build custom framework | Develop or acquire testing tools |
| LLM unpredictability | Same attack may work sometimes | Run multiple iterations |
| Test coverage never complete | New attacks emerge | Stay current on threat landscape |
| Resource intensive | Testing takes time and expertise | Prioritize based on risk |
| Production testing risky | May expose vulnerabilities | Use isolated test environment |

---

[Back to Control 2.20](../../../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
