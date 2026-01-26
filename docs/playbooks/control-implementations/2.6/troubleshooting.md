# Control 2.6: Model Risk Management - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md).

---

## Common Issues and Solutions

| Issue | Symptoms | Root Cause | Solution |
|-------|----------|------------|----------|
| Unclear model classification | Difficulty determining if agent is a "model" | Ambiguous use case | Review OCC 2011-12 definition; when in doubt, treat as model |
| Limited validation resources | Cannot perform independent validation | Resource constraints | Identify internal teams not involved in development; engage external validators |
| Performance data unavailable | Cannot measure model performance | Logging not enabled | Enable conversation logging; configure Dataverse analytics |
| Manifest reconstruction fails | Cannot reproduce historical configuration | Version control gaps | Implement comprehensive manifest versioning |

---

## Detailed Troubleshooting

### Issue 1: Unclear Model Classification

**Symptoms:** Difficulty determining if agent qualifies as a "model" under OCC 2011-12

**Resolution:**

1. **Review OCC 2011-12 model definition:**
   > A model is a quantitative method, system, or approach that applies statistical, economic, financial, or mathematical theories, techniques, and assumptions to process input data into quantitative estimates.

2. **Assess agent characteristics:**
   - Does it provide quantitative estimates?
   - Does it influence business decisions?
   - Does it affect customer outcomes?

3. **Evaluate impact:**
   - What happens if the agent provides incorrect output?
   - Could errors result in financial loss or regulatory violation?

4. **Consult Model Risk Management team:**
   - Discuss borderline cases with MRM committee
   - Document rationale for classification

5. **When in doubt, treat as model:**
   - More governance is better than less
   - Can reclassify later if justified

---

### Issue 2: Limited Validation Resources

**Symptoms:** Cannot perform independent validation due to resource constraints

**Resolution:**

1. **Identify internal teams not involved in development:**
   - Internal audit
   - Risk management
   - Compliance team
   - Other business units

2. **Consider second-line risk functions:**
   - Operational risk
   - Model risk management
   - Compliance

3. **Engage external validators for Tier 1:**
   - Third-party assessment firms
   - Consulting firms with MRM expertise
   - Consider Cohasset Associates for recordkeeping compliance

4. **Use automated validation tools:**
   - Copilot Studio built-in analytics
   - Golden dataset regression testing
   - Automated bias testing

5. **Document resource constraints:**
   - Note limitations in validation report
   - Request additional resources if needed

---

### Issue 3: Performance Data Unavailable

**Symptoms:** Cannot measure model performance

**Resolution:**

1. **Enable conversation logging:**
   - Copilot Studio > Settings > Analytics
   - Ensure logging is enabled for all conversations

2. **Configure Dataverse analytics:**
   - Set up Dataverse tables for conversation data
   - Configure retention policies

3. **Implement user feedback collection:**
   - Add thumbs up/down to conversations
   - Configure CSAT surveys
   - Track escalation rates

4. **Create manual sampling process:**
   - Random sample review of conversations
   - SME quality assessment
   - Document sampling methodology

5. **Document data limitations:**
   - Note in model documentation
   - Identify gaps for future improvement

---

### Issue 4: Manifest Reconstruction Fails

**Symptoms:** Cannot reproduce agent configuration for a specific date

**Resolution:**

1. **Review version control history:**
   - Check Git history for manifest files
   - Look for SharePoint version history
   - Check solution export archives

2. **Identify gap in versioning:**
   - Determine what changes were not captured
   - Document missing time periods

3. **Implement comprehensive versioning:**
   - Export manifest before every change
   - Use Git with branch protection
   - Configure automated export pipelines

4. **Test reconstruction capability:**
   - Conduct reconstruction drill
   - Verify can retrieve configuration for any date
   - Document procedure

5. **Establish remediation plan:**
   - Create process to prevent future gaps
   - Set up automated manifest export

---

### Issue 5: Model Change Impact Assessment

**Symptoms:** Unclear if change requires revalidation

**Resolution:**

1. **Review change classification criteria:**
   - Material change = Full revalidation
   - Non-material change = Abbreviated review
   - Emergency change = Expedited process

2. **Assess output impact:**
   - Will outputs change significantly?
   - Could customer decisions be affected?
   - Is there regulatory impact?

3. **Compare performance baselines:**
   - Run golden dataset against new version
   - Compare accuracy metrics
   - Identify any degradation

4. **Consult MRM guidelines:**
   - Review organization's MRM policy
   - Align with existing change criteria

5. **Document decision:**
   - Record rationale for classification
   - Get MRM approval for material changes

---

### Issue 6: Multi-Agent Validation Complexity

**Symptoms:** Unclear how to validate agent orchestration chains

**Resolution:**

1. **Map complete delegation chain:**
   - Identify all agents in the chain
   - Document interaction points
   - Note data flows

2. **Apply highest tier to chain:**
   - If any agent is Tier 1, treat chain as Tier 1
   - Document risk inheritance

3. **Validate end-to-end:**
   - Test complete user journeys
   - Validate combined outputs
   - Test failure scenarios

4. **Configure circuit breakers:**
   - Limit delegation depth
   - Implement fallback procedures
   - Monitor for cascade failures

5. **Document as single model:**
   - Register orchestration as model
   - Reference component agents
   - Maintain combined documentation

---

## Escalation Path

If issues cannot be resolved using this guide:

1. **Level 1:** AI Governance Lead - Classification and policy questions
2. **Level 2:** Model Risk Manager - Validation and MRM framework
3. **Level 3:** Compliance Officer - Regulatory requirements
4. **Level 4:** External consultants - Third-party validation

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Validation procedures

---

*Updated: January 2026 | Version: v1.2*
