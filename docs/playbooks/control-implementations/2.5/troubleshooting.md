# Control 2.5: Testing, Validation, and Quality Assurance - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 2.5](../../../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md).

---

## Common Issues and Solutions

| Issue | Symptoms | Root Cause | Solution |
|-------|----------|------------|----------|
| Test environment mismatch | Tests pass in test but fail in production | Configuration drift | Compare and sync environment settings |
| Intermittent test failures | Same test passes sometimes, fails other times | Race conditions | Add wait times, retry logic |
| UAT delays | Business users not completing UAT | Unclear expectations | Provide clear scenarios, schedule dedicated time |
| Golden dataset outdated | Regression tests failing on valid responses | Knowledge sources updated | Update golden dataset entries |
| Hallucination rate increase | Groundedness scores declining | Knowledge source gaps | Review and expand knowledge base |

---

## Detailed Troubleshooting

### Issue 1: Test Environment Not Matching Production

**Symptoms:** Tests pass in test but fail in production

**Resolution:**

1. **Compare environment configurations:**
   - DLP policies
   - Security roles
   - Connection references
   - Environment variables

2. **Verify DLP policies match:**
   - Export DLP from both environments
   - Compare connector allowances
   - Sync any differences

3. **Check data source connectivity:**
   - Verify test environment can reach same data sources
   - Check authentication methods match

4. **Review security role differences:**
   - Compare role assignments
   - Verify service accounts exist in both

5. **Sync solution versions:**
   - Export from production
   - Import to test environment

---

### Issue 2: Automated Tests Failing Intermittently

**Symptoms:** Same test passes sometimes, fails other times

**Resolution:**

1. **Add appropriate wait times:**
   ```powershell
   # Add delay between requests
   Start-Sleep -Milliseconds 500
   ```

2. **Check for race conditions:**
   - Review async operations
   - Add proper synchronization

3. **Review test data dependencies:**
   - Ensure test data is reset between runs
   - Check for data state dependencies

4. **Increase timeout values:**
   ```powershell
   $response = Invoke-RestMethod -Uri $endpoint -TimeoutSec 60
   ```

5. **Add retry logic:**
   ```powershell
   $maxRetries = 3
   for ($i = 0; $i -lt $maxRetries; $i++) {
       try {
           $response = Invoke-RestMethod -Uri $endpoint
           break
       }
       catch {
           if ($i -eq $maxRetries - 1) { throw }
           Start-Sleep -Seconds 2
       }
   }
   ```

---

### Issue 3: UAT Delays

**Symptoms:** Business users not completing UAT

**Resolution:**

1. **Provide clear test scenarios:**
   - Write step-by-step instructions
   - Include expected outcomes
   - Provide example inputs

2. **Schedule dedicated UAT time:**
   - Block calendars for testing
   - Remove competing priorities
   - Set clear deadlines

3. **Offer testing support:**
   - Assign QA resource to assist
   - Provide FAQ document
   - Hold office hours for questions

4. **Simplify test documentation:**
   - Use screenshots
   - Create video walkthroughs
   - Reduce required documentation

5. **Set firm deadlines with escalation:**
   - Communicate consequences of delay
   - Escalate to management if needed

---

### Issue 4: Golden Dataset Outdated

**Symptoms:** Valid agent responses failing regression tests

**Resolution:**

1. **Review failed test cases:**
   - Identify why expected response no longer matches
   - Determine if agent response is actually correct

2. **Update golden dataset:**
   - Modify expected_answer_contains patterns
   - Add new acceptable variations

3. **Establish update process:**
   - Schedule quarterly reviews
   - Assign ownership for maintenance
   - Track knowledge source updates

4. **Version golden datasets:**
   - Tag with date and version
   - Maintain history of changes
   - Document reasons for updates

---

### Issue 5: Hallucination Rate Increasing

**Symptoms:** Groundedness scores declining, inaccurate responses

**Resolution:**

1. **Analyze failed responses:**
   - Review specific hallucinations
   - Identify patterns or topics

2. **Check knowledge sources:**
   - Verify sources are current
   - Look for gaps in coverage
   - Check for conflicting information

3. **Review agent prompts:**
   - Check system prompts for clarity
   - Ensure grounding instructions are clear
   - Add constraints if needed

4. **Expand knowledge base:**
   - Add missing topics
   - Update outdated content
   - Improve source quality

5. **Adjust agent settings:**
   - Increase grounding strictness
   - Add fallback behaviors for uncertain topics

---

### Issue 6: Performance Degradation

**Symptoms:** Response times exceeding thresholds

**Resolution:**

1. **Check concurrent usage:**
   - Review usage patterns
   - Identify peak times

2. **Review knowledge source size:**
   - Large knowledge bases slow responses
   - Consider chunking or filtering

3. **Check connector performance:**
   - Test individual connectors
   - Look for slow data sources

4. **Review agent complexity:**
   - Complex topic flows increase latency
   - Simplify where possible

5. **Monitor environment resources:**
   - Check Dataverse performance
   - Review environment limits

---

### Issue 7: Security Tests Failing

**Symptoms:** Prompt injection or data leakage detected

**Resolution:**

1. **Review agent configuration:**
   - Check system prompt safeguards
   - Verify content moderation settings

2. **Strengthen prompts:**
   - Add explicit security instructions
   - Include boundary definitions

3. **Enable content filtering:**
   - Configure Azure AI Content Safety
   - Block harmful patterns

4. **Test additional attack vectors:**
   - Expand security test cases
   - Include new injection techniques

5. **Document and escalate:**
   - Log security findings
   - Involve security team

---

## Escalation Path

If issues cannot be resolved using this guide:

1. **Level 1:** QA Lead - Test methodology and execution
2. **Level 2:** AI Governance Lead - Policy and standards
3. **Level 3:** Compliance Officer - Regulatory requirements
4. **Level 4:** Microsoft Support - Product-level issues

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures

---

*Updated: January 2026 | Version: v1.2*
