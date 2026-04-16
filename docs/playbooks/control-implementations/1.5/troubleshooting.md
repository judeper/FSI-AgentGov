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

### Issue: Virtual Connector Classification Not Enforcing

**Symptoms:** Agent uses blocked connector without triggering DLP error; expected DLP block does not occur

**Solutions:**

1. Verify DLP policy scope includes the target environment:
   - Navigate to PPAC > Policies > Data policies > [Policy] > Environments
   - Confirm target environment is listed in policy scope
   - Note: Policies scoped to "All environments except..." may not apply as expected
2. Check policy propagation timing:
   - Allow 1-2 hours after policy changes for propagation
   - Clear browser cache and retry agent creation/publishing
3. Verify connector is correctly identified:
   - Some connectors have multiple versions or aliases
   - Ensure you've blocked all variants (e.g., "HTTP Webhook" vs "HTTP with no authentication")
4. Check for conflicting policies:
   - Multiple DLP policies may apply to the same environment
   - Higher-priority policy may override expected classification
   - Review all policies via `Get-DlpPolicy` PowerShell cmdlet
5. Verify agent is in target environment:
   - Agents in different environments may have different DLP policies
   - Confirm agent environment matches policy scope

---

### Issue: HTTP Endpoint Filtering Not Blocking Expected URLs

**Symptoms:** Agent successfully calls external API that should be blocked by endpoint filtering; allow list not enforcing

**Solutions:**

1. Verify endpoint filtering is configured:
   - Navigate to PPAC > Policies > Data policies > [Policy] > Connectors
   - Click "HTTP with Microsoft Entra ID" connector
   - Confirm endpoint filtering badge/icon is present
   - Click connector to view configured patterns
2. Check URL pattern syntax:
   - Patterns are case-sensitive for path components (not domain)
   - Wildcards (`*`) must be used correctly: `*.domain.com` (subdomain wildcard) vs `https://domain.com/*` (path wildcard)
   - Verify no typos in domain names
3. Verify filtering mode:
   - Confirm you're using "Allow list" mode (not "Block list") for Zone 3
   - In Allow list mode, only specified patterns are permitted
   - In Block list mode, only specified patterns are denied
4. Allow for propagation delay:
   - Endpoint filtering changes can take 1-2 hours to propagate
   - Test in incognito/private browsing mode to avoid cache
5. Check for pattern overlap:
   - Broader pattern may allow URL you intended to block
   - Example: `*.bank.com` allows `https://external.bank.com` even if you intended only `internal.bank.com`
6. Verify agent is using HTTP with Microsoft Entra ID connector:
   - If agent uses HTTP Webhook (different connector), endpoint filtering for HTTP with Entra ID won't apply
   - Check agent skills/actions to confirm connector type

---

### Issue: Maker Sees No DLP Error When Using Blocked Connector

**Symptoms:** Agent maker can add blocked connector to agent without error message; no DLP notification

**Solutions:**

1. Verify DLP policy applies to maker's user account:
   - Check if maker is in excluded group (some policies exclude admins)
   - DLP policies apply based on environment membership, not user role
2. Confirm environment-level DLP policy scope:
   - Navigate to PPAC > Policies > Data policies > [Policy] > Environments
   - Verify the environment where agent is being created is in policy scope
   - Default environment may have different policies than custom environments
3. Check for "Audit only" mode:
   - If policy is in "Audit only" mode, makers see no blocking errors
   - Verify policy mode in PPAC (should be "Enabled" for enforcement)
4. Test with actual agent execution (not just design-time):
   - DLP enforcement may occur at runtime (when agent executes) rather than design-time (when agent is created)
   - Publish agent and test execution to verify DLP enforcement
5. Check connector classification group:
   - If connector is "Non-Business" (not "Blocked"), maker can use it if not mixing with Business connectors
   - Verify connector is in "Blocked" group for complete prohibition
6. Review Purview Audit Log:
   - Even if maker sees no error, DLP events may be logged
   - Search Purview Audit Log for DLP policy matches with maker's user account

---

## Escalation Path

If issues persist after troubleshooting:

1. **First tier**: Purview Compliance Admin - verify policy configuration
2. **Second tier**: Information Protection Team - review label design
3. **Third tier**: Microsoft Support - platform-level issues

[Back to Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

---

*Updated: April 2026 | Version: v1.3*
