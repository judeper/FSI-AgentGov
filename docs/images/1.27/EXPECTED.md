# Control 1.27: AI Agent Content Moderation Enforcement

## Expected Screenshots

### Screenshot 1: Agent-Effective Default Moderation Setting (High)
**Portal Path:** Microsoft Copilot Studio → [Agent] → Topics → System → [Conversational boosting / Generative AI topic] → Generative answers node → Content moderation
**What to capture:**
- Per-prompt content moderation slider showing "High" selected
- Agent name visible in the header or breadcrumb
- Prompt builder context showing this is the system topic (acts as the agent-effective default)
- Save button visible

### Screenshot 2: Agent-Effective Default Moderation Setting (Moderate)
**Portal Path:** Copilot Studio → [Agent] → Topics → System → [Conversational boosting / Generative AI topic] → Generative answers node → Content moderation
**What to capture:**
- Per-prompt content moderation slider showing "Moderate" selected (some UI builds may label this position **Medium** — capture either label and note in the caption)
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

### Screenshot 6: Per-Prompt Moderation Level Options
**Portal Path:** Copilot Studio → [Agent] → Topics → System → [Conversational boosting / Generative AI topic] → Generative answers node → Content moderation slider
**What to capture:**
- Per-prompt content moderation slider expanded showing all three options:
  - Low
  - Moderate (labelled "Medium" in some UI builds — note in caption)
  - High
- Descriptions or tooltips if visible
- Agent context visible
- This is the **per-prompt** slider (3 positions). The separate **agent-level** slider at Settings → Generative AI → Content moderation has **5 positions** and is captured under Control 1.8 screenshots.

### Screenshot 7: Purview Audit Log for Moderation Change
**Portal Path:** Microsoft Purview portal → Audit → Search results
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
  - Per-prompt moderation levels (Low/Moderate/High; UI may show "Medium" in place of "Moderate")
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
- Content moderation settings are located in the generative AI topic's prompt builder, not in the agent's general Settings panel (the agent-level slider in Settings → Generative AI is a separate 5-position surface — see Control 1.8)
- Capture both agent-effective default (system topic) and per-topic override (custom topic Generative answers node) per-prompt settings to show the dual-control model
- Demonstrate the difference between Low, Moderate, and High per-prompt moderation levels where possible (these are the 3 positions on the per-prompt slider)
- For Zone 3 documentation, ensure custom safety messages are captured

---

## Feature Availability Note

Per-prompt content moderation levels (Low, Moderate, High) with agent-effective-default and per-topic configuration became GA on January 31, 2026 (MC1217615). If your tenant has not yet received this update:

- Moderation settings may appear in a different location
- Feature may be under preview or feature flag
- Contact Microsoft support to confirm rollout status for your tenant region
- Screenshots should be updated once the feature is available in your environment

---

## Screenshot Organization

Organize screenshots in this directory as:
- `1.27-01-moderation-high.png` — Agent-effective default per-prompt moderation set to High
- `1.27-02-moderation-moderate.png` — Agent-effective default per-prompt moderation set to Moderate (labelled "Medium" in some UI builds)
- `1.27-03-topic-moderation-override.png` — Per-topic moderation override
- `1.27-04-custom-safety-message.png` — Custom safety message configuration
- `1.27-05-safety-message-test.png` — Safety message in test panel
- `1.27-06-moderation-level-options.png` — Per-prompt moderation slider options (Low / Moderate / High)
- `1.27-07-audit-log-moderation.png` — Purview audit log for moderation change
- `1.27-08-moderation-inventory.png` — PowerShell moderation inventory output
- `1.27-09-topic-override-report.png` — PowerShell topic override report
- `1.27-10-moderation-test-results.png` — Moderation test results in test panel
