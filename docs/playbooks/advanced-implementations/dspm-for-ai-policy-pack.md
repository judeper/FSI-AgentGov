# Template: DSPM for AI Policy Pack (Copilot + Agents)

**Purpose:** Standardize the DSPM for AI “baseline” posture (prereqs + one-click policies + evidence) so you can consistently monitor and protect AI interactions across Copilot and agents.  
**Applies to:** Zone 2/3 by default; optionally scoped to high-risk users/groups first, then expanded.  
**Microsoft grounding:** DSPM for AI requires appropriate permissions, Purview auditing enabled (needed for monitoring Copilot and agents), and (for some scenarios) collection policies to capture prompts/responses. [page:15]  
**Policy grounding:** DSPM for AI can create default policies (DLP, insider risk, communication compliance, collection policies) including “Protect items with sensitivity labels from Microsoft 365 Copilot and agent processing.” [page:15]  
**Implementation note:** The “AI interaction” event may not always display prompt/response text, and for collection policies prompt/response isn’t displayed unless content capture is enabled. [page:15]

---

## 1) Prerequisites checklist (must be true before “policy pack” rollout)

### 1.1 Permissions
- [ ] Required Purview roles/permissions are assigned to the DSPM for AI operators. [page:15]

### 1.2 Auditing (required for Copilot + agents monitoring)
- [ ] Microsoft Purview auditing is enabled for the organization (verify). [page:15]

### 1.3 Licensing
- [ ] Users who will be monitored for Microsoft 365 Copilot and agents are assigned a Microsoft 365 Copilot license. [page:15]

### 1.4 Device/browser requirements (if monitoring third-party AI usage)
- [ ] Devices onboarded to Microsoft Purview (for visibility and endpoint DLP enforcement). [page:15]
- [ ] Browser extension deployed where required (Edge/Chrome scenarios). [page:15]

---

## 2) Rollout strategy (recommended)

### Phase 1 (Pilot)
- Scope: Zone 3 agent owners, compliance, and a small set of power users.
- Goal: Validate signal quality, confirm audit event availability, and tune DLP actions.

### Phase 2 (Regulated users/groups)
- Scope: regulated lines of business; elevated risk users (Adaptive Protection).
- Goal: enforce “block-with-override” where appropriate.

### Phase 3 (Broad adoption)
- Scope: all Copilot users (with exceptions documented).
- Goal: consistent monitoring + posture measurement.

---

## 3) Default “one-click” policies to enable (baseline pack)

> DSPM for AI lists default policies for data discovery and data security, including DLP, insider risk, communication compliance, and collection policies. [page:15]

### 3.1 Data discovery / visibility (baseline)
Enable (or equivalent):
- **DLP (audit mode):** “Detect sensitive info added to AI sites.” [page:15]
- **Insider risk:** “Detect when users visit AI sites.” [page:15]
- **Insider risk:** “Detect risky AI usage.” [page:15]
- **Communication compliance:** “Unethical behavior in AI apps.” [page:15]

### 3.2 Protection controls (enforcement)
Enable (or equivalent):
- **DLP:** “Block sensitive info from AI sites.” [page:15]
- **DLP:** “Block elevated risk users from submitting prompts to AI apps in Microsoft Edge.” [page:15]
- **DLP:** “Block sensitive info from AI apps in Edge.” [page:15]
- **DLP:** “Protect items with sensitivity labels from Microsoft 365 Copilot and agent processing.” [page:15]
- **Information protection:** sensitivity labels and label policies (if not already configured). [page:15]

### 3.3 Collection policies (content capture where justified)
Enable only where required and approved:
- “Capture interactions for Copilot experiences.” [page:15]
- “Capture interactions for enterprise AI apps.” [page:15]
- “Detect sensitive info shared with AI via network” (note: content capture is not selected by default and must be enabled manually if required). [page:15]

---

## 4) Scoping and exceptions

### 4.1 Scoping rules
- Zone 3 users/groups: always in scope.
- Zone 2: in scope where agents touch Confidential/Restricted data.
- Zone 1: optional, but recommended for baseline visibility.

### 4.2 Exceptions policy
- Any excluded user/group requires:
  - business justification
  - risk sign-off
  - time-bounded expiration
  - compensating controls

---

## 5) Evidence and reporting (what to collect monthly)

DSPM for AI’s Activity explorer events include:
- “AI interaction”
- “AI website visit”
- “DLP rule match”
- “Sensitive info types” [page:15]

For monthly governance reporting, capture:
- counts of AI interactions by app/agent category
- top DLP rule matches (by SIT type)
- policy blocks vs overrides
- risky AI usage detections (insider risk)
- coverage metrics: % of Copilot users monitored, % of Zone 3 owners monitored

---

## 6) Known issues and operational cautions

DSPM for AI notes that “AI interaction” doesn’t always display prompt/response text, and for collection policies prompt/response won’t display unless content capture is enabled. [page:15]  
This means governance evidence should not depend exclusively on “full transcript visibility”; instead, treat DSPM content capture as an approved, scoped capability and rely on structured decision logs + audit event metadata for core evidence. [page:15]

---

## 7) Approvals and change control

- **Policy pack owner:** (Compliance/SecOps)
- **Approved by (Compliance):**
- **Approved by (Security):**
- **Approved by (Privacy):**
- **Effective date:**
- **Review cadence:** quarterly
- **Change record (ticket/PR):**

---

*FSI Agent Governance Framework v1.2 - January 2026*