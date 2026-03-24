# Template: DSPM for AI Policy Pack (Copilot + Agents)

**Purpose:** Standardize the DSPM for AI "baseline" posture (prereqs + one-click policies + evidence) so you can consistently monitor and protect AI interactions across Copilot and agents.  
**Applies to:** Zone 2/3 by default; optionally scoped to high-risk users/groups first, then expanded.  
**Microsoft grounding:** DSPM for AI requires appropriate permissions, Purview auditing enabled (needed for monitoring Copilot and agents), and (for some scenarios) collection policies to capture prompts/responses.  
**Policy grounding:** DSPM for AI can create default policies (DLP, insider risk, communication compliance, collection policies) including "Protect items with sensitivity labels from Microsoft 365 Copilot and agent processing."  
**Implementation note:** The "AI interaction" event may not always display prompt/response text, and for collection policies prompt/response isn't displayed unless content capture is enabled.

---

## 1) Prerequisites checklist (must be true before "policy pack" rollout)

### 1.1 Permissions
- [ ] Required Purview roles/permissions are assigned to the DSPM for AI operators.

### 1.2 Auditing (required for Copilot + agents monitoring)
- [ ] Microsoft Purview auditing is enabled for the organization (verify).

### 1.3 Licensing
- [ ] Users who will be monitored for Microsoft 365 Copilot and agents are assigned a Microsoft 365 Copilot license.

### 1.4 Device/browser requirements (if monitoring third-party AI usage)
- [ ] Devices onboarded to Microsoft Purview (for visibility and endpoint DLP enforcement).
- [ ] Browser extension deployed where required (Edge/Chrome scenarios).

---

## 2) Portal deployment steps

### Step 1: Access DSPM for AI

1. Navigate to [Microsoft Purview](https://purview.microsoft.com)
2. In the left navigation, go to **Solutions** > **DSPM for AI**
3. If this is the first access, you may see a setup wizard — follow the on-screen guidance to initialize DSPM for AI
4. Verify the **Overview** dashboard loads and shows your tenant's AI activity summary

!!! tip "Control 1.6 Portal Walkthrough"
    For detailed DSPM for AI portal navigation and policy configuration steps, see the [Control 1.6 portal walkthrough](../control-implementations/1.6/portal-walkthrough.md). This policy pack builds on the foundational configuration covered there.

### Step 2: Enable One-Click Policies

1. In the DSPM for AI dashboard, navigate to **Policies**
2. Review the list of default policies available under **Data discovery** and **Data security** categories
3. For each policy in the baseline pack (see Section 3 below):
   - Click the policy name to open configuration
   - Review the default scope and conditions
   - Click **Enable** (or **Turn on policy**)
   - Adjust scope to target Zone 2/3 users/groups as needed per your rollout phase
4. Verify enabled policies appear with **Active** status in the policy list

### Step 3: Verify Policy Activation

1. Return to the DSPM for AI **Overview** dashboard
2. Confirm the enabled policies appear under **Active policies**
3. Navigate to **Activity explorer** to verify data is being collected:
   - Filter by **Activity type** = "AI interaction"
   - Confirm events are appearing (may take up to 24 hours for initial data)
4. Check **Alerts** for any policy-triggered notifications
5. Document the activation date and enabled policies in your governance records

---

## 3) Rollout strategy (recommended)

### Phase 1 (Pilot)
- Scope: Zone 3 agent owners, compliance, and a small set of power users.
- Goal: Validate signal quality, confirm audit event availability, and tune DLP actions.

### Phase 2 (Regulated users/groups)
- Scope: regulated lines of business; elevated risk users (Adaptive Protection).
- Goal: enforce "block-with-override" where appropriate.

### Phase 3 (Broad adoption)
- Scope: all Copilot users (with exceptions documented).
- Goal: consistent monitoring + posture measurement.

---

## 4) Default "one-click" policies to enable (baseline pack)

> DSPM for AI lists default policies for data discovery and data security, including DLP, insider risk, communication compliance, and collection policies.

### 4.1 Data discovery / visibility (baseline)
Enable (or equivalent):
- **DLP (audit mode):** "Detect sensitive info added to AI sites."
- **Insider risk:** "Detect when users visit AI sites."
- **Insider risk:** "Detect risky AI usage."
- **Communication compliance:** "Unethical behavior in AI apps."

### 4.2 Protection controls (enforcement)
Enable (or equivalent):
- **DLP:** "Block sensitive info from AI sites."
- **DLP:** "Block elevated risk users from submitting prompts to AI apps in Microsoft Edge."
- **DLP:** "Block sensitive info from AI apps in Edge."
- **DLP:** "Protect items with sensitivity labels from Microsoft 365 Copilot and agent processing."
- **Information protection:** sensitivity labels and label policies (if not already configured).

### 4.3 Collection policies (content capture where justified)
Enable only where required and approved:
- "Capture interactions for Copilot experiences."
- "Capture interactions for enterprise AI apps."
- "Detect sensitive info shared with AI via network" (note: content capture is not selected by default and must be enabled manually if required).

---

## 5) Scoping and exceptions

### 5.1 Scoping rules
- Zone 3 users/groups: always in scope.
- Zone 2: in scope where agents touch Confidential/Restricted data.
- Zone 1: optional, but recommended for baseline visibility.

### 5.2 Exceptions policy
- Any excluded user/group requires:
  - business justification
  - risk sign-off
  - time-bounded expiration
  - compensating controls

---

## 6) Evidence and reporting (what to collect monthly)

DSPM for AI’s Activity explorer events include:
- "AI interaction"
- "AI website visit"
- "DLP rule match"
- "Sensitive info types"

For monthly governance reporting, capture:
- counts of AI interactions by app/agent category
- top DLP rule matches (by SIT type)
- policy blocks vs overrides
- risky AI usage detections (insider risk)
- coverage metrics: % of Copilot users monitored, % of Zone 3 owners monitored

---

## 7) Known issues and operational cautions

DSPM for AI notes that "AI interaction" doesn't always display prompt/response text, and for collection policies prompt/response won't display unless content capture is enabled.  
This means governance evidence should not depend exclusively on "full transcript visibility"; instead, treat DSPM content capture as an approved, scoped capability and rely on structured decision logs + audit event metadata for core evidence.

---

## 8) Approvals and change control

- **Policy pack owner:** (Compliance/SecOps)
- **Approved by (Compliance):**
- **Approved by (Security):**
- **Approved by (Privacy):**
- **Effective date:**
- **Review cadence:** quarterly
- **Change record (ticket/PR):**

---

*FSI Agent Governance Framework v1.2.53 - March 2026*