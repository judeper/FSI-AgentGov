# Control 1.27: AI Agent Content Moderation Enforcement

## Expected Screenshots

### Screenshot 1: Agent-Level Content Moderation Setting (High)
**Portal Path:** Copilot Studio → [Agent] → Topics → System → [Generative AI topic] → Content moderation
**What to capture:**
- Content moderation dropdown or selector showing "High" selected
- Agent name visible in the header or breadcrumb
- Prompt builder context showing this is the agent-level default
- Save button visible

### Screenshot 2: Agent-Level Content Moderation Setting (Medium)
**Portal Path:** Copilot Studio → [Agent] → Topics → System → [Generative AI topic] → Content moderation
**What to capture:**
- Content moderation dropdown or selector showing "Medium" selected
- Agent name visible in the header
- Demonstration of Zone 1 configuration

### Screenshot 3: Topic-Level Moderation Override
**Portal Path:** Copilot Studio → [Agent] → Topics → Custom → [Topic Name] → Generative answers node → Content moderation
**What to capture:**
- Custom topic editor with a topic-specific moderation setting visible
- Moderation level different from agent default (demonstrating override)
- Topic name visible in the header or node
- Generative answers node context

### Screenshot 4: Custom Safety Message Configuration
**Portal Path:** Copilot Studio → [Agent] → Topics → System → [Generative AI topic] → Safety message field
**What to capture:**
- Safety message or "Blocked content message" text field
- Custom message entered (not the default "I'm sorry, I can't respond to that")
- Example: "I'm unable to provide a response to that request. Please contact support for assistance with sensitive topics."
- Agent name visible in the header

### Screenshot 5: Custom Safety Message Displayed in Test Panel
**Portal Path:** Copilot Studio → [Agent] → Test your copilot panel
**What to capture:**
- Agent test chat interface
- User prompt that triggered content moderation (e.g., "Generate a fake financial report")
- Agent response displaying the custom safety message
- Timestamp and conversation context visible

### Screenshot 6: Moderation Level Options
**Portal Path:** Copilot Studio → [Agent] → Topics → System → [Generative AI topic] → Content moderation dropdown
**What to capture:**
- Content moderation dropdown expanded showing all three options:
  - Low
  - Medium
  - High
- Descriptions or tooltips if visible
- Agent context visible

### Screenshot 7: Purview Audit Log for Moderation Change
**Portal Path:** Microsoft Purview Compliance Portal → Audit → Search results
**What to capture:**
- Audit log entry showing a moderation configuration change
- Event details including:
  - Timestamp
  - User who made the change
  - Agent name
  - Operation (e.g., "Update chatbot configuration")
- Search filters showing "Chatbot" or "Copilot" keyword

### Screenshot 8: Agent Moderation Inventory (PowerShell Output)
**What to capture:**
- Terminal/PowerShell window showing output from Get-AgentModerationSettings.ps1 script
- Table or list displaying:
  - Environment names
  - Agent names
  - Moderation levels (Low/Medium/High)
  - Custom safety message status (True/False)
  - Last modified dates
- Summary counts (total agents, compliant agents, non-compliant agents)

### Screenshot 9: Topic Moderation Override Report (PowerShell Output)
**What to capture:**
- Terminal/PowerShell window showing output from topic override export script
- Table displaying:
  - Agent names
  - Topic names
  - Agent-level moderation
  - Topic-level moderation (override)
  - Override direction (Stricter/Permissive/Moderate)
- Highlighting any "Low" overrides requiring approval

### Screenshot 10: Moderation Test Results (Blocked Content)
**Portal Path:** Copilot Studio → [Agent] → Test your copilot panel
**What to capture:**
- Test panel showing multiple prompts and responses:
  - Benign prompt → Successful response
  - Borderline prompt → Blocked or allowed based on level
  - Harmful prompt → Blocked with safety message
- Moderation level indicator if visible
- Demonstration of moderation filtering in action

---

## Verification Focus

- Capture from pre-production or test environment when possible
- Use non-sensitive agent names and prompts for screenshots
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates
- Content moderation settings are located in the generative AI topic's prompt builder, not in the agent's general Settings panel
- Capture both agent-level and topic-level moderation settings to show the dual-control model
- Demonstrate the difference between Low, Medium, and High moderation levels where possible
- For Zone 3 documentation, ensure custom safety messages are captured

---

## Feature Availability Note

Content moderation levels (Low, Medium, High) with agent-level and topic-level configuration became GA on January 31, 2026 (MC1217615). If your tenant has not yet received this update:

- Moderation settings may appear in a different location
- Feature may be under preview or feature flag
- Contact Microsoft support to confirm rollout status for your tenant region
- Screenshots should be updated once the feature is available in your environment
