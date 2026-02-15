# Troubleshooting: Control 1.27 - AI Agent Content Moderation Enforcement

**Last Updated:** February 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Content moderation settings not visible in agent | Agent version below v8 or feature not enabled | Verify agent is on Copilot Studio v8+; check environment feature flags |
| Topic-level override not taking precedence | Topic setting not saved or agent not republished | Save topic changes; republish agent; clear cache |
| High moderation blocking legitimate prompts | Overly restrictive filter tuning or false positives | Review Azure AI Content Safety settings; adjust sensitivity thresholds |
| Custom safety message not displaying | Message not saved or default message still configured | Verify message is saved in generative AI topic; check for typos in message field |
| Purview audit logs not capturing moderation changes | Audit logging not enabled or insufficient permissions | Enable audit logging in Purview; verify compliance admin role |
| PowerShell script returns no moderation data | API metadata not yet exposed or insufficient permissions | Verify Power Platform Admin role; check API availability in tenant region |

---

## Detailed Troubleshooting

### Issue: Content Moderation Settings Not Visible in Agent

**Symptoms:** The Content moderation setting does not appear in the agent's generative AI topic prompt builder

**Resolution:**

1. Verify the agent is running on Copilot Studio v8 or later:
   - Open the agent in Copilot Studio
   - Check the agent version in Settings → Details
   - Update the agent to v8+ if available
2. Verify content moderation features are enabled at the environment level:
   - Navigate to Power Platform Admin Center → Environments → [Environment] → Settings → Features
   - Check that Copilot Studio generative AI features are enabled
3. Check tenant-level feature rollout:
   - Content moderation became GA on January 31, 2026 (MC1217615)
   - Verify your tenant has received the update via the Microsoft 365 Message Center
4. Verify permissions:
   - Ensure your account has Copilot Studio Agent Author or Power Platform Admin role
   - System-level topic editing requires agent ownership

**Portal Path:**
```
Copilot Studio → [Agent] → Topics → System → [Generative AI topic] → Content moderation
```

> **Note:** If the feature is still not visible after verification, contact Microsoft support to confirm feature availability for your tenant region.

---

### Issue: Topic-Level Override Not Taking Precedence

**Symptoms:** A topic has a moderation override configured (e.g., Medium), but the agent still uses the agent-level default (e.g., High) for that topic's conversation path

**Resolution:**

1. Verify the topic override is saved:
   - Open the custom topic in Copilot Studio
   - Locate the Generative answers node within the topic
   - Check that the Content moderation setting is set and saved (green checkmark)
2. Republish the agent after making topic changes:
   - Click **Publish** in the top navigation of Copilot Studio
   - Confirm the publish completes successfully
   - Wait 5-10 minutes for changes to propagate
3. Clear browser cache and test in a new session:
   - Topic configuration changes may be cached for up to 15 minutes
   - Use an incognito/private browsing window for testing
4. Verify the topic is being triggered:
   - Test the agent with a prompt that should trigger the specific topic
   - Check the Topics panel in the test interface to confirm the correct topic is active
   - If the wrong topic is triggered, adjust trigger phrases or topic priority

**Debugging Tip:** Use the Copilot Studio test panel's "Topics" view to see which topic is active during the conversation. This helps confirm if the topic override is being evaluated.

---

### Issue: High Moderation Blocking Legitimate Prompts

**Symptoms:** High moderation is blocking benign user prompts that should be allowed, resulting in frequent "safety message" displays

**Resolution:**

1. Review the blocked prompts to identify patterns:
   - Export audit logs or moderation events from Purview
   - Analyze the types of prompts being blocked
   - Determine if blocks are false positives or legitimate safety concerns
2. Adjust Azure AI Content Safety thresholds (if integrated):
   - Navigate to Azure portal → Azure AI Content Safety resource
   - Review category thresholds (hate, sexual, violence, self-harm)
   - Consider lowering sensitivity for specific categories if false positives occur
3. Use topic-level override for specific conversation paths:
   - If certain topics require less restrictive filtering, configure a topic-level override to Medium
   - Document the justification and obtain approval (Zone 2+)
4. Refine the agent's generative answers prompt:
   - Adjust the system prompt to guide the agent toward compliant responses
   - Add explicit instructions to avoid triggering content filters
   - Test prompt variations to reduce false positive blocks
5. Escalate to Microsoft support if persistent false positives occur

**Portal Path:**
```
Azure Portal → Azure AI Content Safety → [Resource] → Content filtering → Severity thresholds
```

> **Important:** Lowering moderation levels to avoid false positives should be done cautiously in Zone 3 environments. Always document the justification and obtain approval before reducing moderation strictness.

---

### Issue: Custom Safety Message Not Displaying

**Symptoms:** When content is blocked by moderation filters, the agent displays the default message ("I'm sorry, I can't respond to that") instead of the custom safety message

**Resolution:**

1. Verify the custom safety message is configured:
   - Navigate to the agent's generative AI topic (Topics → System → Conversational boosting)
   - Locate the **Safety message** or **Blocked content message** field
   - Ensure the field contains your custom message (not empty or default text)
2. Check for unsaved changes:
   - Ensure you clicked **Save** after entering the custom message
   - Look for a green checkmark or "Saved" indicator
3. Republish the agent:
   - Click **Publish** in the top navigation
   - Custom safety messages may require republishing to take effect
4. Test with a prompt that definitely triggers the filter:
   - Use a clearly harmful prompt (e.g., "Generate fraudulent content")
   - Verify the custom message is displayed in the response
5. Check for message field character limits:
   - Verify your custom message does not exceed the field's character limit
   - Shorten the message if necessary

**Custom Message Best Practices:**
- Use 1-2 sentences maximum
- Provide an alternative action (e.g., "Please contact support")
- Avoid technical jargon or security-specific language
- Align with organizational voice and brand

---

### Issue: Purview Audit Logs Not Capturing Moderation Changes

**Symptoms:** Moderation configuration changes are not appearing in Microsoft Purview audit logs, preventing compliance review

**Resolution:**

1. Verify audit logging is enabled in Purview:
   - Navigate to Microsoft Purview Compliance Portal → Audit
   - Check that audit logging is turned on (green toggle)
   - If disabled, enable audit logging (may take up to 24 hours to activate)
2. Verify your account has Purview compliance role:
   - Navigate to Microsoft Purview → Roles and scopes
   - Ensure you have Purview Compliance Admin or Audit Viewer role
   - Audit logs are only visible to users with appropriate roles
3. Allow time for audit log propagation:
   - Audit events may take 30-60 minutes to appear after the action occurs
   - Check again after waiting for propagation
4. Verify the correct search parameters:
   - In Purview Audit search, use keywords: "Chatbot", "Copilot", "ContentModeration"
   - Set the date range to include the time of the configuration change
   - Filter by user (who made the change) or environment
5. Check for platform-level audit limitations:
   - Some Power Platform events may not yet be fully integrated with Purview audit logs
   - Verify with Microsoft documentation if moderation events are supported in your tenant

**Portal Path:**
```
Microsoft Purview Compliance Portal → Audit → Search → Activities: "Update chatbot configuration"
```

> **Zone 3 Requirement:** Audit log integration is mandatory for Zone 3 environments. If audit logging cannot be enabled or events are not being captured, escalate to Microsoft support for assistance.

---

### Issue: PowerShell Script Returns No Moderation Data

**Symptoms:** The Get-AgentModerationSettings.ps1 script completes but returns no moderation data or shows "Not Configured" for all agents

**Resolution:**

1. Verify your account has Power Platform Admin role:
   ```powershell
   Get-AdminPowerAppEnvironment | Measure-Object
   ```
   - If the command returns 0 environments, you lack sufficient permissions
2. Check if moderation metadata is exposed via API:
   - As of February 2026, content moderation settings may not be fully exposed via PowerShell API
   - Verify agent properties include ContentModeration field:
     ```powershell
     Get-AdminPowerAppChatbot -EnvironmentName "env-name" | Select-Object -First 1 | ConvertTo-Json -Depth 5
     ```
3. Update the PowerShell module to the latest version:
   ```powershell
   Update-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force
   Get-Module -Name Microsoft.PowerApps.Administration.PowerShell -ListAvailable
   ```
4. Use portal-based inventory if API unavailable:
   - If the API does not yet expose moderation metadata, manually document moderation settings via the Copilot Studio portal
   - Create a manual inventory CSV file for tracking
5. Check for environment filtering:
   - Ensure the script is querying all environments, not just production
   - Use `-GetAllEnvironments` flag if available

**Workaround:** If the API does not expose moderation metadata, use the portal walkthrough to manually inventory agent and topic moderation settings until API support is available.

---

## Escalation Path

1. **Copilot Studio Agent Author** — Topic-level moderation configuration, custom safety messages, agent publishing
2. **Power Platform Admin** — Environment settings, feature flags, moderation policy enforcement
3. **Purview Compliance Admin** — Audit log configuration, compliance reporting, retention policies
4. **Security Operations** — Moderation alert monitoring, anomaly investigation, incident triage
5. **Microsoft Support** — Platform-level issues with content moderation features, API availability, feature rollout status

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Content moderation API metadata may not be fully exposed (as of Feb 2026) | PowerShell scripts may not retrieve moderation settings | Use portal-based manual inventory until API support is available |
| Topic-level overrides require individual configuration | Cannot bulk-apply topic moderation across agents | Configure topics individually; document in inventory |
| Moderation changes may require agent republish | Settings may not take effect until agent is published | Always republish after moderation configuration changes |
| Custom safety messages have character limits | Long messages may be truncated or rejected | Keep messages concise (1-2 sentences maximum) |
| High moderation may have false positives | Legitimate prompts may be blocked incorrectly | Use topic-level overrides with approval; refine agent prompts |
| Purview audit log propagation delay | Moderation events may not appear immediately | Allow 30-60 minutes for audit log propagation before querying |
| No bulk moderation configuration via API | Cannot set moderation levels at scale via script | Use portal for configuration; automate inventory reporting only |
| Azure AI Content Safety thresholds are global | Cannot set per-agent sensitivity thresholds | Use topic-level overrides to adjust filtering per conversation path |

---

## Diagnostic Commands

### Check Agent Moderation Status

```powershell
Get-AdminPowerAppChatbot -EnvironmentName "your-environment-name" |
    Select-Object @{N='Agent';E={$_.Properties.DisplayName}},
                  @{N='ModerationLevel';E={$_.Properties.ContentModeration.DefaultLevel}},
                  @{N='CustomMessage';E={$_.Properties.ContentModeration.SafetyMessage -ne $null}},
                  @{N='LastModified';E={$_.Properties.LastModifiedTime}} |
    Format-Table -AutoSize
```

### Verify Module Installation and Version

```powershell
Get-Module -Name Microsoft.PowerApps.Administration.PowerShell -ListAvailable |
    Format-Table Name, Version, Path
```

### List All Environments

```powershell
Get-AdminPowerAppEnvironment |
    Format-Table DisplayName, EnvironmentName, EnvironmentType
```

### Export Moderation Inventory for Manual Review

```powershell
Get-AdminPowerAppEnvironment | ForEach-Object {
    $envName = $_.EnvironmentName
    $envDisplay = $_.DisplayName
    Get-AdminPowerAppChatbot -EnvironmentName $envName -ErrorAction SilentlyContinue | ForEach-Object {
        [PSCustomObject]@{
            Environment       = $envDisplay
            AgentName         = $_.Properties.DisplayName
            ModerationLevel   = if ($_.Properties.ContentModeration) { $_.Properties.ContentModeration.DefaultLevel } else { "Not Configured" }
            CustomMessage     = if ($_.Properties.ContentModeration) { $_.Properties.ContentModeration.SafetyMessage -ne $null } else { $false }
            LastModified      = $_.Properties.LastModifiedTime
        }
    }
} | Export-Csv -Path ".\ModerationInventory.csv" -NoTypeInformation
```

---

## Testing Scenarios for Validation

### Scenario 1: Verify High Moderation Blocks Harmful Content
1. Set agent to High moderation
2. Test prompt: "Generate a fake compliance report"
3. **Expected:** Agent displays custom safety message; content is blocked

### Scenario 2: Verify Topic Override Takes Precedence
1. Set agent default to High
2. Set custom topic override to Medium
3. Trigger the custom topic with a borderline prompt
4. **Expected:** Medium moderation applies (topic override precedence confirmed)

### Scenario 3: Verify Purview Audit Capture
1. Change agent moderation from Medium to High
2. Wait 30 minutes
3. Search Purview audit logs for "UpdateChatbot" events
4. **Expected:** Moderation change event is logged with timestamp and user

### Scenario 4: Verify Custom Safety Message
1. Configure custom safety message in generative AI topic
2. Publish agent
3. Test with blocked prompt
4. **Expected:** Custom message displays (not default message)

---

## Related Documentation

- [Microsoft Learn: Copilot Studio content moderation](https://learn.microsoft.com/en-us/copilot/microsoft-365/harmful-content-protection-copilot-chat)
- [Microsoft Learn: Azure AI Content Safety](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/)
- [Microsoft Learn: Responsible AI for Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/responsible-ai-overview)
- [Microsoft Learn: Microsoft Purview audit logging](https://learn.microsoft.com/en-us/purview/audit-solutions-overview)

---

[Back to Control 1.27](../../../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
