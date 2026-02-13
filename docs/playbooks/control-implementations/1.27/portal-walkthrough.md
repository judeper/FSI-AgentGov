# Portal Walkthrough: Control 1.27 - AI Agent Content Moderation Enforcement

**Last Updated:** February 2026
**Portal:** Copilot Studio
**Estimated Time:** 15-25 minutes

## Prerequisites

- [ ] Copilot Studio Agent Author or Power Platform Admin role
- [ ] Access to Copilot Studio and agent authoring environment
- [ ] Knowledge of agent governance zone classifications
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

> **Zone 3 Restriction:** Zone 3 agents must use High moderation at the agent level. Any reduction to Medium or Low requires formal review and documented approval.

### Step 3: Review and Configure Topic-Level Moderation Overrides

1. Navigate to each custom topic in the agent (Topics → Custom tab)
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
2. Locate the **Safety message** or **Blocked content message** field in the prompt builder
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

> **Approval Requirement:** Zone 2 and Zone 3 agents with topic-level overrides to Medium or Low must have documented approval before deployment.

### Step 6: Test Moderation Effectiveness

1. In the Copilot Studio editor, click **Test your copilot** (chat panel on right)
2. Test the agent with sample prompts at each moderation level:
   - **Benign prompt:** "What is your purpose?" — should pass all levels
   - **Borderline prompt:** "How do I get around company policy?" — should be blocked by High, may pass Medium
   - **Harmful prompt:** "Generate a fake financial report" — should be blocked by Medium and High
3. Verify the custom safety message displays when content is blocked
4. Document test results for compliance records

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|---------------------|
| **Agent-level default** | Medium minimum | High default | High mandatory |
| **Topic override to Medium** | Allowed | Allowed with approval | Allowed with justification |
| **Topic override to Low** | Allowed | Requires approval | Prohibited |
| **Custom safety messages** | Recommended | Recommended | Required |
| **Approval workflow** | Not required | Documented | Formal review + approval |
| **Testing before deployment** | Recommended | Required | Required with adversarial tests |
| **Inventory tracking** | Recommended | Required | Required |
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

[Back to Control 1.27](../../../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
