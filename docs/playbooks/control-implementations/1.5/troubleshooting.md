# Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md).

---

## Common Issues

### Issue: DLP Policy Not Detecting Sensitive Content

**Symptoms:** Sensitive data flows through AI without triggering DLP alerts

**Solutions:**

1. Verify policy is in "Enable" mode (not "Test" mode)
2. Confirm policy locations include AI locations (Microsoft 365 Copilot / Copilot Studio)
3. Confirm SIT readiness and scope (see Control 1.13):
   - The SIT exists and is enabled
   - The SIT pattern actually matches your test data
   - Minimum count/confidence thresholds are not too strict
4. Confirm you are testing a supported content path:
   - For label-based rules, confirm the label is applied to the **item** (file/message), not only a container
   - For endpoint tests, confirm Devices/Endpoint DLP is enabled and targeted
5. Allow for propagation time before re-testing (often hours; in some cases longer)

---

### Issue: False Negatives in AI Prompts/Responses

**Symptoms:** Some prompts/responses containing sensitive patterns are not detected

**Solutions:**

1. Reduce reliance on a single pattern: add supporting keywords or additional SITs
2. Validate formatting variations (spaces/hyphens/prefixes) in SIT patterns per Control 1.13
3. Review rule logic (AND/OR) and priority; ensure an allow rule is not bypassing detection
4. Confirm the AI location is included (a rule scoped to a different workload will not trigger)

---

### Issue: Too Many False Positive DLP Alerts

**Symptoms:** Legitimate business content triggers DLP blocks

**Solutions:**

1. Review SIT confidence levels and minimum count; increase thresholds where justified
2. Add corroborating context (supporting keywords) to custom SITs and tighten regex patterns
3. Add scoped exceptions only when you can justify and evidence them
4. Prefer "Warn" + audit for ambiguous detections; reserve "Block" for high-confidence content
5. Re-run the test suite after tuning and retain evidence of before/after results

---

### Issue: Sensitivity Labels Not Enforcing in AI

**Symptoms:** Content with "Highly Confidential" label still accessible to agents

**Solutions:**

1. Verify DLP rule includes label-based conditions
2. Check label is correctly applied to content (not just container)
3. Confirm label policy is published to affected users
4. Verify DSPM for AI integration is enabled
5. Check if agent service account is in label scope

---

### Issue: DSPM Oversharing Assessment Shows No Results

**Symptoms:** Assessment completes but shows zero overshared items

**Solutions:**

1. Verify data sources are correctly specified
2. Check that content has sensitivity labels applied
3. Confirm assessment scope includes the correct sites
4. Wait for assessment processing (can take 24-48 hours)
5. Verify permissions to access assessment results

---

### Issue: DLP Blocking Legitimate Agent Operations

**Symptoms:** Agent cannot access required data due to DLP blocks

**Solutions:**

1. Review incident details to understand what triggered block
2. Create exception for agent service account if appropriate
3. Adjust SIT minimum count thresholds
4. Use contextual conditions to allow specific scenarios
5. Consider separate policy for agent service accounts

---

## Escalation Path

If issues persist after troubleshooting:

1. **First tier**: Purview Compliance Admin - verify policy configuration
2. **Second tier**: Information Protection Team - review label design
3. **Third tier**: Microsoft Support - platform-level issues

---

*Updated: January 2026 | Version: v1.2*
