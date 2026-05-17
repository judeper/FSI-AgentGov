# Portal Walkthrough: Control 2.23 - User Consent and AI Disclosure Enforcement

**Last Updated:** April 2026
**Portals:** Microsoft 365 Admin Center, Copilot Studio, Power Apps (Dataverse)
**Estimated Time:** 30–45 minutes

## Prerequisites

- [ ] **AI Administrator** role for Copilot AI Disclaimer configuration (preferred — least privilege per Microsoft Learn)
- [ ] Entra Global Admin role available for break-glass / initial enablement only
- [ ] Power Platform Admin or Environment Admin role for the target Dataverse environment (Zone 3)
- [ ] Copilot Studio Maker access (assigned via the relevant security group / environment)
- [ ] Approved organizational AI policy URL (intranet or public site) — reviewed by Compliance / Legal
- [ ] Approved Zone 3 disclosure language (see Troubleshooting playbook, Issue 9 for required elements)
- [ ] Agent governance zone classification confirmed (Zone 1 / 2 / 3) per Control 1.2 registry

> **Hedged-language reminder.** Configuring this control supports — but does not by itself ensure — compliance with FINRA 3110, FINRA 2210, GLBA 501(b), SEC 17a-4, and SOX 302/404. Always pair tenant configuration with documented policy, training, and supervisory review.

---

## Part 1 — Tenant-Wide AI Disclaimer (Microsoft 365 Admin Center)

### Step 1: Navigate to the Copilot AI disclaimer policy

1. Sign in to the [Microsoft 365 Admin Center](https://admin.microsoft.com) as an **AI Administrator**.
2. In the left navigation, expand **Copilot**.
3. Select **Settings**.
4. Click **View all** (top of the settings list) and then choose **Copilot AI disclaimer**.

> **UI verified April 2026.** Microsoft moved this setting from `Settings → Org settings` into the dedicated **Copilot → Settings** surface. If the option is missing, confirm: (1) tenant has Microsoft 365 Copilot or Copilot Chat licenses, (2) signed-in user has the AI Administrator role, and (3) Message Center confirms the rollout has reached your region.

### Step 2: Enable the disclaimer

1. Toggle **Copilot AI disclaimer** to **On**. This creates the tenant-level policy named `Copilot AI Disclaimer`.
2. Choose the **font style**:
   - **Standard** — acceptable for Zone 1 only
   - **Bold** — required for Zone 2 and Zone 3 (improves visibility)
3. (Optional) Enter a **Custom URL** pointing to your organization's AI policy. The URL is surfaced as a tooltip from the info icon next to the disclaimer string.

> **Required for FSI Zone 2/3:** Bold style + custom URL pointing to a versioned AI policy page. Default Microsoft transparency content alone is not sufficient for regulated workloads.

### Step 3: Confirm scope and save

1. Review the supported surfaces shown in the panel: Word, Excel, PowerPoint, Outlook, OneNote, and Copilot Chat.
2. Note the surfaces **not** covered by this toggle: SharePoint, OneDrive, Whiteboard, Forms (these require workload-specific disclosure if used for AI-assisted features).
3. Click **Save**.
4. Allow up to 24 hours for global propagation; new sign-ins typically see the change within minutes.

### Step 4: Validate disclaimer presentation

1. From an InPrivate / Incognito browser session, sign in as a non-admin test user with a Copilot license.
2. Open Copilot Chat (`https://m365.cloud.microsoft/chat`) and a Word document.
3. Confirm:
   - The disclaimer string appears below the Copilot input box.
   - The font matches your selection (Standard or Bold).
   - Hovering the info icon reveals a tooltip with your custom URL (when configured).
4. Capture screenshots and store them under `maintainers-local/tenant-evidence/2.23/` per the screenshot evidence convention (local only — never committed).

---

## Part 2 — Agent-Level Disclosure (Copilot Studio)

### Step 5: Open the target agent

1. Sign in to [Copilot Studio](https://copilotstudio.microsoft.com) as a maker with edit rights on the agent.
2. Select the correct **environment** (top-right environment picker) — confirm zone classification before proceeding.
3. Open the agent.

### Step 6: Edit the system Conversation Start topic

1. In the left navigation, click **Topics**.
2. Switch to the **System** tab.
3. Open **Conversation Start** (this is the canonical entry topic in current Copilot Studio; older agents may have a "Greeting" topic — treat both the same way).
4. Replace or extend the existing message node with the AI disclosure message appropriate for the agent's zone (templates below).

#### Disclosure templates by zone

**Zone 1 (Personal Productivity):**
```
Hi — I'm {AgentName}, an AI assistant from {Organization}.
Responses are AI-generated and should be reviewed before use.
See our AI policy: {AIPolicyURL}
```

**Zone 2 (Team Collaboration):**
```
Hi — I'm {AgentName}, an AI assistant from {Organization} for {AgentPurpose}.
- Responses are AI-generated and should be reviewed before action.
- This conversation may be retained and reviewed for quality, supervision, and compliance.
- Read our AI policy: {AIPolicyURL}
```

**Zone 3 (Enterprise Managed — regulated workloads):**
```
{AgentName} — AI Disclosure ({DisclosureVersion})

I'm an AI assistant operated by {Organization}. Before we continue:

1. Responses are generated by AI and must be reviewed by a qualified person before any decision affecting customers, accounts, or financial reporting.
2. This conversation is retained for {RetentionPeriod} in {DataLocation} for supervisory review per FINRA Rule 3110 and SEC 17a-4 record-keeping obligations.
3. To request access to or deletion of your conversation data, contact {PrivacyContact}.
4. To raise a concern about AI usage, contact {ComplianceContact}.

Full policy: {AIPolicyURL}

Do you acknowledge these terms? (Yes / No)
```

> **Approval gate.** Zone 3 disclosure language must be approved by Legal and Compliance before publication. Record the approval and the `DisclosureVersion` value in your governance documentation system.

### Step 7: Add consent acknowledgment branch (Zone 3 only)

1. After the disclosure message, add a **Question** node:
   - **Identify:** create a closed-list option entity `ConsentResponse` with values `Yes` / `No`.
   - **Save response as:** `Topic.UserConsent`.
2. Add a **Condition** branch on `Topic.UserConsent`:
   - **Yes branch:** Call an action that invokes the `Log-AIConsent` Power Automate flow (see Step 9). Continue the conversation.
   - **No branch:** Send message: *"Thanks — I can't continue without your acknowledgment. Please contact {ComplianceContact} if you need help."* Then add an **End conversation** node.
3. Save and **Publish** the agent.

### Step 8: Re-acknowledgment frequency

- **Zone 1:** Display disclosure on first conversation only (use a topic variable persisted via Power Automate or the `Global.LastConsentDate` global variable pattern).
- **Zone 2:** Display on first conversation per quarter.
- **Zone 3:** Display every conversation; record consent each time. Re-acknowledgment cadence ≤ 90 days enforced by the Dataverse query in Step 9.

---

## Part 3 — Consent Tracking (Dataverse, Zone 3)

### Step 9: Deploy the `fsi_aiconsent` table

This control depends on a custom Dataverse table. The PowerShell Setup playbook provides a `pac` CLI script to deploy a managed solution; the portal alternative is below.

1. Open [Power Apps](https://make.powerapps.com) → select the Zone 3 environment.
2. **Tables → New table → New table**.
3. Configure:
   - **Display name:** `AI Consent`
   - **Plural display name:** `AI Consents`
   - **Schema name:** `fsi_aiconsent` (publisher prefix must match your FSI solution publisher; adjust if different)
   - **Primary column:** `Name` (text)
4. Add columns:
   | Display name | Schema name | Type | Required | Notes |
   |---|---|---|---|---|
   | User UPN | `fsi_userupn` | Single line of text | Required | Lower-case, max 320 chars |
   | User AAD Object ID | `fsi_useraadid` | Single line of text | Required | Stable user identifier |
   | Agent Name | `fsi_agentname` | Single line of text | Required | |
   | Agent ID | `fsi_agentid` | Single line of text | Required | Copilot Studio bot ID |
   | Consent Timestamp | `fsi_consenttimestamp` | Date and time (UTC) | Required | |
   | Disclosure Version | `fsi_disclosureversion` | Single line of text | Required | e.g., `v1.3.3-2026-04` |
   | Acknowledgment Status | `fsi_acknowledgmentstatus` | Yes/No | Required | |
   | Source Channel | `fsi_sourcechannel` | Choice | Optional | Teams / Web / Mobile / API |
5. Set **Auditing** = **On** at the table level (Settings → Advanced options) so updates and deletes are captured in the Dataverse audit log.
6. Restrict write access via a custom Dataverse security role; only the consent-logging service principal should have **Create** privilege. Compliance / audit roles get **Read** only — this approximates immutability without requiring custom plug-ins.

### Step 10: Build the `Log-AIConsent` flow

1. In [Power Automate](https://make.powerautomate.com), create an **Instant cloud flow** with the trigger **"When Power Virtual Agents calls a flow"** (works for Copilot Studio).
2. Inputs (text): `userUpn`, `userAadId`, `agentName`, `agentId`, `disclosureVersion`, `acknowledgmentStatus` (Yes/No as text → cast).
3. Action: **Add a new row (Dataverse)** → table `AI Consents`. Map inputs to columns; set `fsi_consenttimestamp = utcNow()`.
4. Authentication: use a **service principal** (Entra app registration) with a Dataverse application user assigned the restricted security role from Step 9. Avoid personal connections.
5. Add a **terminate** step on failure that returns `Failed` so Copilot Studio can route the user to the contact path.
6. Save and test with a sample payload.

### Step 11: Re-acknowledgment query

1. Add a second flow **`Check-AIConsent`** that the agent calls at the start of every Zone 3 conversation:
   - Input: `userAadId`, `agentId`
   - Action: **List rows (Dataverse)** on `fsi_aiconsents` with filter `fsi_useraadid eq '{userAadId}' and fsi_agentid eq '{agentId}' and fsi_acknowledgmentstatus eq true` ordered by `fsi_consenttimestamp desc`, top 1.
   - Return: `consentValid` (Yes if most-recent record is < 90 days old).
2. The agent shows the disclosure + question only when `consentValid = No`.

---

## Part 4 — Documentation and Sign-Off

### Step 12: Record the configuration

Capture the following in your governance repository (SharePoint or equivalent):

| Item | Value |
|---|---|
| AI Disclaimer toggle status | On / Off |
| Font style | Standard / Bold |
| Custom URL | `https://...` |
| Disclosure version | `v…` |
| Approval (Legal / Compliance) | Names + date |
| Last verified | Date + admin |
| Zone 3 agents in scope | List |
| `fsi_aiconsent` deployment evidence | Solution import log / SHA-256 (see PowerShell Setup) |

### Step 13: Hand off to verification

Run the [Verification & Testing playbook](verification-testing.md) end-to-end before declaring this control implemented.

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---|---|---|---|
| Tenant AI Disclaimer toggle | Recommended | Required | Required |
| Disclaimer font style | Standard | Bold | Bold |
| Custom disclosure URL | Optional | Required | Required (versioned, Legal-approved) |
| Agent-level disclosure | Recommended | Required | Required, Zone 3 template |
| Consent tracking in Dataverse | Not required | Optional | Required |
| Re-acknowledgment cadence | First use | Quarterly | ≤ 90 days, per session |
| Purview audit coverage of consent flow | Not required | Recommended | Required |
| Disclosure version tracking | Not required | Recommended | Required |

---

## Validation Checklist

- [ ] `Copilot AI Disclaimer` policy is **On** with **Bold** style for Zone 2/3 (Microsoft 365 admin center)
- [ ] Custom URL resolves for both internal and external (guest) users
- [ ] Every in-scope agent's Conversation Start topic shows the zone-appropriate disclosure
- [ ] Zone 3 agents call `Log-AIConsent` on every accepted consent
- [ ] Zone 3 agents call `Check-AIConsent` and re-prompt when last consent > 90 days
- [ ] `fsi_aiconsent` table has table-level auditing enabled
- [ ] Service-principal-only write path verified (no human user can insert rows)
- [ ] Disclosure version + approval recorded in governance documentation
- [ ] Screenshots stored locally under `maintainers-local/tenant-evidence/2.23/`

---

[Back to Control 2.23](../../../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
