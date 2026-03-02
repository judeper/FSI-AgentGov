# Control 1.26: Agent File Upload and File Analysis Restrictions

## Expected Screenshots

### Screenshot 1: Copilot Studio File Upload Toggle (Enabled)
**Portal Path:** Copilot Studio → [Agent] → Settings → Security → File Upload
**What to capture:**
- File Upload toggle in the enabled state
- Agent name visible in the header
- Security settings panel context

### Screenshot 2: Copilot Studio File Upload Toggle (Disabled)
**Portal Path:** Copilot Studio → [Agent] → Settings → Security → File Upload
**What to capture:**
- File Upload toggle in the disabled state
- Agent name visible in the header
- Security settings panel context

### Screenshot 3: Uploaded Files as Knowledge Sources
**Portal Path:** Copilot Studio → [Agent] → Knowledge
**What to capture:**
- List of files uploaded as knowledge sources
- File names, types, and sizes visible
- Sensitivity label display if applicable

### Screenshot 4: Sensitivity Label Inheritance
**Portal Path:** Copilot Studio → [Agent] → Settings or Knowledge
**What to capture:**
- Agent displaying the inherited sensitivity label from uploaded files
- Label name and classification level visible

### Screenshot 5: SPE Container in Power Platform Admin Center
**Portal Path:** Power Platform Admin Center → Environments → [Environment] → Settings
**What to capture:**
- SharePoint Embedded container configuration or reference
- Environment name visible in the header
- Access control or retention policy indicators

### Screenshot 6: Agent File Upload Inventory Output
**What to capture:**
- Terminal output from the Get-AgentFileUploadStatus PowerShell script
- Environment names, agent names, and file upload toggle states
- Summary counts (total agents, upload enabled, upload disabled)

---

## Verification Focus
- Capture from pre-production environment when possible
- Ensure agent and environment names are representative but not sensitive
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates
- The File Upload toggle is located under the agent's Security settings in Copilot Studio (not in PPAC)
- Capture both enabled and disabled states to demonstrate toggle functionality

---

## Screenshot Organization

Organize screenshots in this directory as:
- `1.26-01-file-upload-enabled.png` — File upload toggle enabled
- `1.26-02-file-upload-disabled.png` — File upload toggle disabled
- `1.26-03-uploaded-knowledge-sources.png` — Uploaded files as knowledge sources
- `1.26-04-sensitivity-label-inheritance.png` — Sensitivity label inheritance
- `1.26-05-spe-container.png` — SPE container in PPAC
- `1.26-06-file-upload-inventory.png` — PowerShell file upload inventory output
