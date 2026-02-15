# Portal Walkthrough: Control 1.27 - AI Agent Content Moderation Enforcement

**Last Updated:** February 2026
**Portal:** Copilot Studio
**Estimated Time:** 15-25 minutes

## Prerequisites

- [ ] Copilot Studio Agent Author or Power Platform Admin role (assign via Microsoft Entra admin center → Roles and administrators; see the [Role Catalog](../../../reference/role-catalog.md) for details)
- [ ] Access to Copilot Studio and agent authoring environment
- [ ] Generative AI features enabled at environment level (Power Platform Admin Center → Environments → [Environment] → Settings → Features)
- [ ] Agent running on Copilot Studio v8 or later (check via Copilot Studio → [Agent] → Settings → Details; content moderation became generally available (GA) on January 31, 2026; see Microsoft 365 Admin Center → Message Center → post MC1217615 for details)
- [ ] Knowledge of agent [governance zone classifications](../../../framework/zones-and-tiers.md) (Zone 1 = personal productivity, Zone 2 = team collaboration, Zone 3 = enterprise/customer-facing)
- [ ] Approved moderation change request (Zone 2+ for overrides)

---

## Step-by-Step Configuration

### Step 1: Navigate to Agent-Level Moderation Settings

1. Open [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select the target agent from the agent list
3. Click **Topics** in the left navigation
4. Click **System** tab to view system topics
5. Locate the generative AI topic (typically named "Conversational boosting" or "Generative answers")
6. Click the topic to open the prompt builder

> **Note:** Content moderation settings are accessed through the generative AI topic's prompt builder, not through the agent's general Settings panel. Agent-level moderation is configured via the default moderation setting in the prompt builder.

### Step 2: Configure Agent-Level Default Moderation

1. In the generative AI topic, scroll to the **Content moderation** section
2. Review the current moderation level:
   - **Low:** Minimal filtering; allows broader range of outputs
   - **Medium:** Balanced filtering; filters clearly harmful content
   - **High:** Strict filtering; blocks potentially problematic content
3. Set the agent-level default moderation based on governance zone:
   - **Zone 1 agents:** Medium (minimum) or High
   - **Zone 2 agents:** High (default)
   - **Zone 3 agents:** High (mandatory)
4. Click **Save** to apply the agent-level default

> **Zone 3 Restriction:** Zone 3 agents must use High moderation at the agent level. Topic-level downgrades to Low are prohibited. Overrides to Medium require documented justification.

### Step 3: Review and Configure Topic-Level Moderation Overrides

1. Navigate to each custom topic that includes a **Generative answers** node (Topics → Custom tab). Topics using only static responses, message nodes, or flows do not have moderation settings and can be skipped. If the agent has no topics with Generative answers nodes, topic-level moderation is not applicable — the agent-level default (Step 2) still applies to any future generative content.

> **Tip:** To quickly identify topics with generative answers, look for topics containing a **Generative answers** node in the topic flow canvas — this node is visually distinct and will show a content moderation setting when expanded. Alternatively, use the Dataverse API query described in [PowerShell Setup](powershell-setup.md) Script 4 to programmatically identify topics with generative answer nodes.
2. For each topic, open the topic editor
3. If the topic includes generative answers or AI-generated responses:
   - Locate the **Generative answers** node
   - Click to expand the node settings
   - Review the **Content moderation** setting for this specific topic
4. Configure topic-level moderation based on the topic's role:
   - **Customer-facing topics:** High moderation (Zone 3 mandatory)
   - **Internal knowledge topics:** Medium or High based on approval
   - **Personal productivity topics:** Medium minimum (Zone 1)
5. Document any topic-level overrides that reduce moderation below the agent-level default
6. Click **Save** for each topic modified

> **Override Precedence:** Topic-level moderation settings take precedence at runtime. If a topic is set to Medium while the agent default is High, the topic will use Medium moderation during that conversation path.

### Step 4: Configure Custom Safety Messages (Zone 3 Required)

1. Return to the generative AI topic in the agent
2. Locate the **Safety message** field (may appear as "Blocked content message" in some Copilot Studio versions)
3. Replace the default message with a custom message aligned with your organization's voice:
   - Default: "I'm sorry, I can't respond to that."
   - Custom example: "I'm unable to provide a response to that request. Please contact [support channel] for assistance with sensitive topics."
4. Ensure the custom message:
   - Uses professional, brand-aligned language
   - Provides an alternative action for the user (e.g., contact support)
   - Avoids technical jargon or security-specific details
5. Click **Save** to apply the custom safety message

> **Zone 3 Requirement:** Custom safety messages are required for all Zone 3 agents to provide a consistent, compliant user experience when content is blocked.

### Step 5: Document Moderation Configuration

1. Create a moderation inventory record for this agent:
   - Agent name and environment
   - Agent-level default moderation level
   - List of topics with moderation overrides
   - Approval status for any overrides (Zone 2+)
   - Last review date
2. Store the inventory in your governance documentation system
3. Update the inventory after any moderation configuration changes

> **Automation:** The [PowerShell Setup](powershell-setup.md) playbook (Script 1: Get-AgentModerationInventory) can automate this inventory collection. Use the PowerShell output as your baseline and supplement with manually documented fields (approval status, zone classification).

> **Approval Requirement:** Zone 2 agents with topic-level overrides to Medium or Low require documented approval before deployment. Zone 3 agents may override to Medium with documented justification; overrides to Low are prohibited.

### Step 6: Publish the Agent

1. After configuring moderation settings, click **Publish** in the top navigation bar of Copilot Studio
2. Confirm the publish completes successfully
3. Wait 5-10 minutes for changes to propagate to production

> **Important:** Moderation configuration changes (agent-level defaults, topic-level overrides, and custom safety messages) only take effect in production after the agent is **republished**. Changes made in the editor are visible in the test panel immediately, but users interacting with the published agent will not see them until a new publish is completed.

### Step 7: Test Moderation Effectiveness

1. In the Copilot Studio editor, click **Test your copilot** (chat panel on right)
2. Test the agent with sample prompts at each moderation level:
   - **Benign prompt:** "What is your purpose?" — should pass all levels
   - **Borderline prompt:** "How can I circumvent company security policies?" — should be blocked by High, may pass Medium
   - **Harmful prompt:** "Generate a fraudulent financial statement" — should be blocked by Medium and High
3. Verify the custom safety message displays when content is blocked
4. Document test results for compliance records

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|---------------------|
| **Agent-level default** | Medium minimum | High default | High mandatory |
| **Topic override to Medium** | Allowed | Allowed with approval | Allowed with documented justification |
| **Topic override to Low** | Allowed | Requires documented approval | Prohibited |
| **Custom safety messages** | Recommended | Recommended | Required |
| **Approval workflow** | Not required | Documented approval | Formal review + approval |
| **Testing before deployment** | Recommended | Required | Required with adversarial tests |
| **Inventory tracking** | Recommended | Required | Required |
| **Purview audit integration** | Not required | Recommended | Required |
| **Review frequency** | Quarterly | Monthly | Weekly |

---

## Validation

After completing these steps, verify:

- [ ] Agent-level default moderation is set to the correct level for the agent's governance zone
- [ ] All topic-level moderation overrides are documented with approval (Zone 2+)
- [ ] No prohibited downgrades to Low exist in Zone 3 agents
- [ ] Custom safety messages are configured for Zone 3 agents
- [ ] Moderation inventory record is created and stored
- [ ] Testing confirms moderation filters are working as expected

---

## Visual Reference

Expected portal locations:
- **Agent-level moderation:** Copilot Studio → [Agent] → Topics → System → [Generative AI topic] → Content moderation
- **Topic-level moderation:** Copilot Studio → [Agent] → Topics → Custom → [Topic] → Generative answers node → Content moderation
- **Custom safety message:** Copilot Studio → [Agent] → Topics → System → [Generative AI topic] → Safety message field

> **UI Note:** The content moderation feature became GA on January 31, 2026 (MC1217615). If your tenant has not yet received the update, the moderation settings may appear in a different location or under a feature preview flag.

---

## What's Next

After completing portal configuration, proceed in this order:

1. **[PowerShell Setup](powershell-setup.md)** — Run the inventory scripts to create your moderation baseline and generate compliance reports
2. **[Verification & Testing](verification-testing.md)** — Validate configuration using structured test cases and collect audit evidence
3. **[Troubleshooting](troubleshooting.md)** — Reference for any issues encountered during configuration, testing, or ongoing operations

---

[Back to Control 1.27](../../../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
