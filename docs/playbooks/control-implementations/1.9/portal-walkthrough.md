# Control 1.9: Data Retention and Deletion Policies - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

---

## Prerequisites

- Microsoft 365 E5 or E3 + Compliance add-on
- Purview Records Manager role assigned
- Regulatory retention schedule documented and approved
- Disposition reviewers identified

---

## Step 1: Create Retention Labels for Agent Data

**Portal Path:** Microsoft Purview > Data lifecycle management > Microsoft 365 > Labels

### Label 1: Agent Conversations - 7 Year

1. Navigate to [Microsoft Purview Compliance Portal](https://compliance.microsoft.com)
2. Go to **Data lifecycle management** > **Microsoft 365**
3. Select **Labels** tab > **+ Create a label**
4. Configure:
   - **Name:** `FSI-AgentConversations-7Year`
   - **Description:** "Agent conversation logs - FINRA/SEC 7-year retention"
5. **Retention settings:**
   - Retain items for: 7 years
   - Start retention based on: When items were created
   - At end of retention period: Start a disposition review
6. **Disposition reviewers:** Compliance team, Records Management
7. Click **Create**

### Label 2: Agent Configuration - 6 Year

1. **Name:** `FSI-AgentConfig-6Year`
2. **Description:** "Agent configuration and settings history"
3. **Retention settings:**
   - Retain items for: 6 years
   - At end of retention period: Delete items automatically
4. Click **Create**

### Label 3: Agent Audit Logs - 10 Year

1. **Name:** `FSI-AgentAudit-10Year`
2. **Description:** "Agent audit and compliance logs - extended retention"
3. **Retention settings:**
   - Retain items for: 10 years
   - At end of retention period: Start disposition review
   - Mark as regulatory record: Yes (immutable)
4. Click **Create**

---

## Step 2: Publish Retention Labels

**Portal Path:** Purview > Data lifecycle management > Microsoft 365 > Label policies

1. Click **+ Publish labels**
2. **Choose labels:** Select all FSI agent labels
3. **Choose locations:**
   - Exchange email
   - SharePoint sites
   - OneDrive accounts
   - Microsoft 365 Groups
   - Teams channel messages (if applicable)
4. **Policy name:** `FSI-AgentData-RetentionLabels`
5. Click **Publish**

---

## Step 3: Create Retention Policies for Agent Platforms

**Portal Path:** Purview > Data lifecycle management > Microsoft 365 > Retention policies

### Policy 1: Copilot Studio Conversation Logs

1. Click **+ New retention policy**
2. **Name:** `FSI-CopilotStudio-ConversationRetention`
3. **Description:** "Retain Copilot Studio agent conversations"
4. **Locations:**
   - Dataverse (where Copilot Studio logs are stored)
   - Copilot interactions (if available as a location)
5. **Retention settings:**
   - Retain items for: 7 years
   - At end of retention period: Delete items automatically
6. Click **Create**

### Policy 2: Power Platform Activity Logs

1. Click **+ New retention policy**
2. **Name:** `FSI-PowerPlatform-ActivityRetention`
3. **Locations:**
   - Power Platform logs (via Dataverse)
   - Microsoft 365 audit log (Power Platform activities)
4. **Retention settings:**
   - Retain items for: 7 years
5. Click **Create**

---

## Step 4: Configure Dataverse Retention

**Portal Path:** Power Platform Admin Center > Environments > [Environment] > Settings > Data management

1. Navigate to Power Platform Admin Center
2. Select environment > **Settings**
3. Under **Data management**, configure:

**For Agent Activity Logs:**
- Table: msdyn_copilotinteraction
- Retention Period: 7 years
- Archive: After 1 year
- Delete: After retention period

**For Agent Sessions:**
- Table: msdyn_copilotsession
- Retention Period: 3 years
- Archive: After 6 months

---

## Step 5: Set Up Disposition Review Workflow

**Portal Path:** Purview > Records management > Disposition

1. Navigate to **Records management** > **Disposition**
2. Configure reviewers for FSI labels:
   - **Stage 1:** Records Management team (initial review)
   - **Stage 2:** Compliance Officer (regulatory check)
   - **Stage 3:** Legal (if litigation concerns)

3. For each disposition item:
   - **Approve:** Item deleted per policy
   - **Extend:** Add additional retention period
   - **Relabel:** Apply different retention label
   - **Export:** Generate evidence of disposition

---

## Step 6: Configure Legal Hold

**Portal Path:** Purview > eDiscovery > Core or Premium > Holds

1. Navigate to **eDiscovery** > **Core** (or Premium)
2. Create or select a case
3. Click **Holds** > **+ Create**
4. Configure:
   - **Name:** `FSI-AgentData-LegalHold-[CaseName]`
   - **Locations:** Relevant mailboxes, SharePoint sites, Dataverse
5. Click **Create**

**Note:** Legal hold overrides retention policies - content won't be deleted until hold is released.

---

## Step 7: Enable Audit Logging for Deletion Events

**Portal Path:** Purview > Audit > Audit retention policies

1. Navigate to **Audit**
2. Create retention policy for deletion events:
   - **Name:** `FSI-DeletionAudit-10Year`
   - **Record types:** File deleted, Message deleted, Dataverse record deleted
   - **Duration:** 10 years
3. Click **Save**

---

[Back to Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
