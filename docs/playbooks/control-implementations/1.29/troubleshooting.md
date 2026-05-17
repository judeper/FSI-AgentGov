# Control 1.29 — Troubleshooting: Global Secure Access Network Controls

**Playbook Type:** Troubleshooting
**Control:** 1.29 — Global Secure Access: Network Controls for Copilot Studio Agents
**Audience:** Power Platform Administrators, Security Operations, Platform Engineers
**Estimated Resolution Time:** Varies by issue — most common issues resolve in 15–60 minutes
**Prerequisites:** Access to Power Platform admin center, Entra admin center, and GSA traffic logs

!!! warning "Preview Feature"
    This is a preview feature. Preview features aren't meant for production use and may have restricted functionality. Features may change before becoming generally available. Subject to the [Microsoft Azure Preview Supplemental Terms of Use](https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/). Known issues and behaviors described in this playbook reflect the March 2026 preview state. Some issues may be resolved in later releases; some workarounds may become unnecessary.

---

## How to Use This Playbook

Locate the symptom that matches your issue, follow the diagnostic steps in order, and apply the indicated resolution. Each issue section includes:

- **Symptom**: What you observe
- **Likely Causes**: Ordered from most to least common
- **Diagnostic Steps**: How to confirm the cause
- **Resolution**: How to fix it
- **Escalation Path**: What to do if the resolution does not work
- **Evidence Note**: Whether this issue should be documented as a control gap

---

## Issue 1: Agent Traffic Not Appearing in GSA Traffic Logs

**Symptom:** After enabling GSA forwarding for a Copilot Studio environment and triggering agent requests to external destinations, no entries appear in GSA traffic logs. The agent may or may not be completing its tasks successfully.

### Likely Causes (check in order)

**Cause 1A: GSA forwarding toggle not saved correctly**

The most common cause. The toggle may appear ON in the UI but was not actually persisted due to a save failure or UI session issue.

*Diagnostic steps:*
1. Navigate to Power Platform admin center > Environments > [environment] > Settings > Features.
2. Close and reopen the Settings panel (navigate away and return).
3. Re-check the Global Secure Access toggle state — does it still show ON?
4. If it shows OFF, the previous save did not persist.

*Resolution:*
1. Set the toggle to ON again.
2. Click Save and wait for the confirmation indicator.
3. Navigate away and return to confirm the setting persisted.
4. Wait 30 minutes and re-test.

**Cause 1B: Propagation delay not yet complete**

GSA forwarding configuration changes take 15–30 minutes to propagate globally to all agent execution nodes. Testing immediately after enabling will show no logs.

*Diagnostic steps:*
1. Check when the toggle was enabled (review change record or admin audit log).
2. If less than 30 minutes have elapsed, wait and re-test.

*Resolution:* Wait the full 30 minutes before concluding that forwarding is not working.

**Cause 1C: Custom connectors not updated after GSA enablement**

Custom connectors that were already deployed before GSA forwarding was enabled may need to be re-saved or republished for their traffic to be captured by the GSA forwarding layer.

*Diagnostic steps:*
1. In Power Apps maker portal, navigate to the custom connector used by the agent.
2. Check the connector's last modified date — is it older than the GSA enablement date?
3. Make a minor update to the connector definition (add a description line, then remove it) and save.
4. Re-test agent traffic.

*Resolution:*
1. Re-save each custom connector in the affected environment.
2. For connectors deployed via solution, re-import the solution.
3. Re-test and confirm traffic appears in logs.

**Cause 1D: Agent traffic type not yet supported in preview**

During the preview, not all traffic types may be captured. Confirm which traffic types are currently supported against the latest Microsoft Learn documentation.

*Diagnostic steps:*
1. Check the current Microsoft Learn documentation for "Global Secure Access for agents supported traffic types."
2. Compare the traffic type your agent uses against the supported list.

*Resolution:* If the traffic type is not yet supported, document this as a control gap with compensating control (e.g., connector-level DLP policy per Control 1.4). Monitor Microsoft roadmap for support expansion.

**Cause 1E: Log latency**

GSA traffic logs have a processing latency. Entries may take 2–15 minutes to appear after the request.

*Diagnostic steps:*
1. Trigger a test request.
2. Wait 15 minutes.
3. Refresh the log view and use a time filter that includes the request window.

*Resolution:* Account for log latency in operational procedures. Real-time log visibility is not guaranteed in the current preview.

### Escalation Path

If none of the above causes resolve the issue:
1. Open a Microsoft support case through the Power Platform admin center (Help + Support).
2. Reference: "Global Secure Access for Copilot Studio agents — agent traffic not appearing in GSA logs (Preview)."
3. Provide: environment ID, date/time of test requests, agent flow IDs, and tenant ID.
4. While escalated, treat the control as non-operational and document as a control gap with risk acceptance.

### Evidence Note

If GSA logs are not capturing agent traffic, document this as an active control gap. Record: date identified, diagnostic steps taken, escalation opened (if applicable), compensating controls in place (e.g., network firewall rules, connector-level DLP), and risk acceptance signed by CISO. Review weekly until resolved.

---

## Issue 2: Legitimate Connector or External Destination Incorrectly Blocked

**Symptom:** An agent that was working correctly before GSA was enabled now fails with connection errors when calling a legitimate external API or service. GSA traffic logs show the destination being blocked by the web content filtering or network file filtering policy.

### Likely Causes

**Cause 2A: Destination falls within a blocked content category**

The external service your agent calls is categorized in a blocked content category. For example, a vendor API hosted on a domain that shares infrastructure with social media services, or a document storage endpoint categorized as "file sharing" when a consumer service would be blocked by that category.

*Diagnostic steps:*
1. Identify the blocked destination FQDN from the GSA traffic log (action = Block, policy = web content filtering policy name).
2. In Entra admin center, look up the URL categorization of the FQDN (Global Secure Access > Secure > Web content filtering > check URL categorization lookup if available, or use an external URL categorization tool).
3. Confirm which category is causing the block.

*Resolution:*
1. Assess whether the destination is legitimately needed by the agent for a business purpose.
2. If yes, submit a formal allowlist addition request per your change management process.
3. In Entra admin center > web content filtering policy, add an explicit **Allow** rule for the specific FQDN or URL pattern.
4. Document: FQDN, business justification, agent name(s), data classification of information transmitted, approver names, approval date.
5. Re-test agent connectivity after 15–30 minutes for policy propagation.

!!! warning "Zone 3 Allowlist Change Control"
    For Zone 3 environments, allowlist additions require Security team approval and must be tracked in the change management system. Do not add allowlist exceptions directly without completing the formal change process, even under time pressure.

**Cause 2B: Destination FQDN matches an explicit URL block rule**

An explicit URL block rule in the web content filtering policy is matching the destination.

*Diagnostic steps:*
1. In the GSA traffic log, note the policy rule ID or name referenced in the block event.
2. Navigate to the web content filtering policy and review explicit URL rules.
3. Identify the rule matching the destination.

*Resolution:*
1. Assess whether the rule is incorrectly scoped (too broad a wildcard, for example).
2. If the destination should be allowed: add a higher-priority explicit Allow rule for the specific FQDN.
3. If the block rule itself is too broad: narrow the rule scope and document the change.

**Cause 2C: Network file filtering policy blocking a file transfer operation**

A file upload or download that is a normal part of the agent's operation is being caught by the network file filtering policy.

*Diagnostic steps:*
1. Review GSA logs for the file filtering Block event — note destination and file type if visible.
2. Review the network file filtering policy rules to identify which rule is matching.

*Resolution:*
1. Assess whether the file transfer is a legitimate business operation.
2. If yes: add an Allow rule for the specific destination and/or file type to the network file filtering policy.
3. Document as above (business justification, agent, data classification, approver).

**Cause 2D: Post-policy-update propagation delay**

A policy update (e.g., allowlist addition) was saved but has not yet propagated. The block continues until propagation is complete.

*Diagnostic steps:*
1. Check when the allowlist addition was saved.
2. If less than 30 minutes have elapsed, wait and re-test.

*Resolution:* Wait the full propagation window (15–30 minutes) after any policy change before concluding the change did not take effect.

### Escalation Path

If the destination is correctly allowlisted but continues to be blocked after 45 minutes:
1. Verify the allow rule is syntactically correct (check for wildcards, trailing slashes, or protocol prefixes that might prevent matching).
2. Try an exact FQDN match rather than a wildcard pattern.
3. Open a Microsoft support case if the issue persists after policy correction attempts.

### Evidence Note

Document all allowlist additions in the allowlist change register. At minimum quarterly, review all allowlist entries and remove any entries where the underlying business need no longer exists or the agent using that destination has been decommissioned.

---

## Issue 3: Baseline Profile Changes Not Taking Effect

**Symptom:** After linking a new policy to the GSA baseline profile or modifying a policy that is already linked, the expected change in behavior (new blocks or new allows) is not observed. Agent traffic continues to behave as it did before the change.

### Likely Causes

**Cause 3A: Propagation delay**

This is the most common cause. Global Secure Access distributes policies across a globally distributed proxy infrastructure. Policy changes at the baseline profile level typically take 15–30 minutes to propagate fully.

*Diagnostic steps:*
1. Check when the policy change was saved (admin audit log or change record).
2. If less than 30 minutes have elapsed, wait and re-test.

*Resolution:* Wait the full propagation window. Do not make additional policy changes while waiting — layered changes during propagation make it harder to identify which change is effective.

**Cause 3B: Policy not correctly linked to baseline profile**

The policy was created but not linked to the baseline profile, or the link was not saved correctly.

*Diagnostic steps:*
1. Navigate to Entra admin center > Global Secure Access > Connect > Traffic forwarding > Baseline profile.
2. Review the linked policies section — confirm each of the three policy types (web content filtering, threat intelligence, file filtering) shows the correct policy name.
3. If a policy is missing from the baseline profile, it is not active.

*Resolution:*
1. If a policy link is missing, click Link policy and select the correct policy.
2. Save the baseline profile.
3. Wait 15–30 minutes for propagation.
4. Re-test.

**Cause 3C: Policy saved in disabled/draft state**

The policy itself was created but left in a disabled or draft state.

*Diagnostic steps:*
1. Navigate to the policy in Entra admin center.
2. Check the **State** field — it should be **Enabled**.

*Resolution:* Set policy state to Enabled. Save. Wait for propagation. Re-test.

**Cause 3D: Conditional Access-linked profile used instead of baseline profile**

The policies were linked to a Conditional Access-based profile rather than the baseline profile. Conditional Access-linked profiles are not supported for agent traffic in the current preview.

*Diagnostic steps:*
1. In Entra admin center > Global Secure Access > Connect > Traffic forwarding, review the profile list.
2. Confirm that the policies are linked to the **Baseline profile**, not a profile that has a Conditional Access policy association.

*Resolution:* Move policy links to the baseline profile. Conditional Access-linked profiles will not apply to agent traffic in the current preview state.

!!! note "Conditional Access Profile Support"
    This is a known preview limitation. Conditional Access-linked profiles for agent traffic are on the Microsoft roadmap but not yet available. When this capability becomes available, it will enable more granular per-agent or per-environment policy scoping. Until then, all agent traffic policies must be linked to the baseline profile.

### Escalation Path

If propagation takes more than 60 minutes after confirmed correct configuration:
1. Open a Microsoft support case.
2. Reference: "GSA baseline profile policy not propagating after 60+ minutes (Preview)."

---

## Issue 4: Missing Agent-Specific Metadata in Traffic Logs

**Symptom:** GSA traffic logs show entries that appear to correspond to agent traffic (destinations match), but agent-specific metadata fields (traffic type, agent ID, source environment identifier) are missing or show generic values rather than agent-specific values.

### Likely Causes

**Cause 4A: Traffic not being forwarded through GSA agent path**

If agent traffic is flowing through a non-agent forwarding path, it may be logged but without agent metadata. This can happen if the traffic is routed through a general network forwarding profile rather than the agent-specific forwarding mechanism.

*Diagnostic steps:*
1. Confirm GSA forwarding toggle is ON in PPAC for the specific environment (see Issue 1, Cause 1A).
2. Check whether your tenant has other Global Secure Access configurations that might be capturing this traffic under a different profile.

*Resolution:* Ensure the environment-specific GSA forwarding toggle is the active routing mechanism, not a general network-level GSA configuration.

**Cause 4B: Preview limitation — agent metadata fields not yet fully populated**

During the preview, some agent-specific metadata fields may not be fully populated for all traffic types. This is a known preview limitation.

*Diagnostic steps:*
1. Check current Microsoft Learn documentation for the list of metadata fields available in the current preview version.
2. Identify which specific fields are missing.

*Resolution:*
1. Document the missing fields as a known preview limitation.
2. Note which fields are available and use those for log review purposes.
3. Include the missing field gap in your control gap register with the note: "Known preview limitation — monitor for GA release resolution."
4. For examination evidence, annotate log screenshots with a note explaining which fields are not yet available in preview.

**Cause 4C: Log query filter excluding agent traffic type**

The log query filter in the GSA traffic log UI may be filtering out agent-type entries.

*Diagnostic steps:*
1. Clear all filters from the GSA traffic log view.
2. Re-query without any traffic type filter.
3. Search for the specific destination FQDN.

*Resolution:* Adjust query filters to include all traffic types. The agent metadata may be present but not visible when a restrictive filter is applied.

### Evidence Note

Missing agent metadata is a verification gap for VT-05-A in the verification testing playbook. Document the gap, the specific missing fields, the preview limitation justification, and the planned resolution timeline (follow Microsoft release notes for GA availability).

---

## Issue 5: GSA Log Export to Sentinel Not Functioning

**Symptom:** GSA traffic logs are visible in Entra admin center but are not appearing in the Microsoft Sentinel workspace as expected for Zone 3 environments (per Control 3.9 requirements).

### Likely Causes

**Cause 5A: Diagnostic settings not configured**

GSA traffic logs are not automatically exported to Sentinel — a diagnostic settings configuration is required to stream logs to a Log Analytics workspace.

*Diagnostic steps:*
1. In Entra admin center, navigate to your Entra tenant's Diagnostic Settings.
2. Check whether a diagnostic setting exists that routes Global Secure Access traffic logs to the target Log Analytics workspace.

*Resolution:*
1. In the Azure portal, navigate to Microsoft Entra ID > Diagnostic settings.
2. Click **+ Add diagnostic setting**.
3. Select the **NetworkAccessTrafficLogs** log category (or equivalent GSA log category name in current UI).
4. Set destination to the target Log Analytics workspace.
5. Save the diagnostic setting.
6. Wait 30 minutes for logs to begin appearing in Sentinel.
7. See Control 3.9 playbooks for full Sentinel integration configuration.

**Cause 5B: Incorrect Log Analytics workspace selected**

Logs are being exported to a different workspace than where Sentinel is deployed.

*Diagnostic steps:*
1. Check the diagnostic setting destination workspace ID.
2. Compare to the workspace ID where Sentinel is deployed.

*Resolution:* Update the diagnostic setting to point to the correct Sentinel workspace.

**Cause 5C: Log retention policy on workspace insufficient**

Logs are arriving in the workspace but are being pruned before the required retention period.

*Diagnostic steps:*
1. In the Azure portal, navigate to the Log Analytics workspace.
2. Check the retention setting for the GSA traffic log table.

*Resolution:* Update workspace retention policy per Control 3.9 configuration requirements and organizational regulatory retention schedule.

### Escalation Path

For Sentinel-specific issues, refer to Control 3.9 (Microsoft Sentinel Integration) troubleshooting resources. If the diagnostic settings appear correctly configured but logs are not arriving, open a Microsoft support case referencing the specific GSA log category and workspace ID.

---

## Quick Diagnostic Reference

| Symptom | Most Likely Cause | First Check |
|---|---|---|
| No traffic in GSA logs at all | Toggle not saved / propagation delay | PPAC toggle state; wait 30 min |
| Only some traffic visible | Custom connector not updated post-enablement | Re-save custom connectors |
| Blocked destination not in logs | Destination bypassing GSA path | Confirm traffic type is supported |
| Legitimate destination blocked | Destination in blocked category | Check GSA log policy rule; add to allowlist |
| Policy change not taking effect | Propagation delay / not linked to baseline | Wait 30 min; check baseline profile links |
| No agent metadata in logs | Preview limitation or non-agent forwarding path | Check MS Learn for current preview scope |
| Logs not in Sentinel | Missing diagnostic setting | Add Entra diagnostic setting for GSA logs |
| Threat intel not blocking | Policy in Audit mode | Confirm policy action = Block |

---

## Escalation and Support Contacts

| Issue Type | First Escalation | Second Escalation |
|---|---|---|
| Power Platform admin center / GSA toggle | Microsoft Power Platform support (admin.powerplatform.microsoft.com > Help + Support) | Microsoft account team |
| Entra admin center / GSA policies | Microsoft Entra support (entra.microsoft.com > Help + Support) | Microsoft Security FastTrack |
| Preview product behavior / bugs | Microsoft Feedback Hub (Power Platform category, GSA for agents tag) | Microsoft account team + preview PM contact if available |
| Sentinel log integration | Microsoft Sentinel support | Control 3.9 internal owner |
| Active security incident (agent exfiltrating data) | Internal SOC escalation (Control 1.8) | Microsoft DART (Detection and Response Team) if Microsoft involvement required |

---

[Back to Control 1.29](../../../controls/pillar-1-security/1.29-global-secure-access-network-controls.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
