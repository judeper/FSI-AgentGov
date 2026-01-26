# Control 1.10: Communication Compliance Monitoring - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md).

---

## Prerequisites

- Microsoft 365 E5 or E5 Compliance add-on
- Communication Compliance roles assigned
- Compliance reviewers identified and trained
- Detection scenarios defined

---

## Step 1: Assign Communication Compliance Roles

**Portal Path:** Microsoft Purview > Permissions > Microsoft Purview solutions > Roles

1. Navigate to Purview Compliance Portal
2. Go to **Permissions** > **Microsoft Purview solutions** > **Roles**
3. Assign roles:

| Role | Purpose | Assign To |
|------|---------|-----------|
| Communication Compliance Admin | Full policy management | Compliance team leads |
| Communication Compliance Analyst | Review and triage alerts | Compliance analysts |
| Communication Compliance Investigator | Investigate and remediate | Senior compliance |
| Communication Compliance Viewer | Read-only access | Audit team |

---

## Step 2: Create Communication Compliance Policies

**Portal Path:** Purview > Communication compliance > Policies > + Create policy

### Policy 1: Agent Inappropriate Content Detection

1. Navigate to **Communication compliance** > **Policies**
2. Click **+ Create policy**
3. **Template:** Detect inappropriate content
4. **Policy name:** `FSI-Agent-InappropriateContent`
5. **Users and groups:** Select users who interact with agents
6. **Locations:**
   - Teams chat (if agents use Teams)
   - Copilot for Microsoft 365 (if available)
   - Exchange email (for email-based agents)
7. **Conditions:**
   - Detect threats and harassment
   - Detect discrimination
   - Detect profanity
8. **Review frequency:** Ongoing monitoring
9. **Reviewers:** Assign compliance analysts
10. Click **Create policy**

### Policy 2: Financial Regulatory Violations

1. Click **+ Create policy**
2. **Template:** Custom policy
3. **Policy name:** `FSI-Agent-RegulatoryViolations`
4. **Users:** All users with agent access
5. **Locations:** All applicable channels
6. **Conditions - Sensitive information:**
   - Custom SIT: MNPI Indicators
   - Custom SIT: Unsuitable Investment Recommendations
   - Financial data patterns
7. **Conditions - Keywords:**
   - "guaranteed return", "risk free", "can't lose"
   - "inside information", "before announcement"
   - "don't tell anyone", "keep this quiet"
8. **Direction:** Inbound and outbound
9. **Reviewers:** Compliance (primary) + Legal (escalation)
10. Click **Create policy**

### Policy 3: Customer Data Protection

1. Click **+ Create policy**
2. **Template:** Detect sensitive information
3. **Policy name:** `FSI-Agent-CustomerDataProtection`
4. **Users:** All agent users
5. **Conditions - Sensitive information types:**
   - Credit card numbers
   - Social Security numbers
   - Bank account numbers
   - Custom: Customer account numbers
6. **Threshold:** Start with low for initial tuning
7. **Direction:** Outbound (agent responses)
8. **Reviewers:** Data protection team
9. Click **Create policy**

### Policy 4: Conflict of Interest Detection

1. Click **+ Create policy**
2. **Template:** Custom policy
3. **Policy name:** `FSI-Agent-ConflictOfInterest`
4. **Conditions - Keywords:**
   - "my personal account", "trade for myself"
   - "front running", "before the client"
   - "proprietary trading", "house account"
5. **Reviewers:** Compliance + Ethics
6. Click **Create policy**

---

## Step 3: Configure Detection Classifiers

**Portal Path:** Purview > Communication compliance > Settings > Classifiers

1. Go to **Settings** > **Classifiers**
2. Enable relevant trainable classifiers:
   - Threats
   - Harassment
   - Discrimination
   - Adult content
   - Profanity
   - Regulatory collusion (if available)
   - Gifts & entertainment (if available)

---

## Step 4: Set Up OCR for Image Detection

**Portal Path:** Purview > Communication compliance > Settings > OCR

1. Go to **Settings** > **OCR**
2. Enable OCR for communication compliance
3. Configure:
   - Process images in Teams
   - Process attachments
   - Apply SIT detection to OCR text

---

## Step 5: Configure Priority User Groups

**Portal Path:** Purview > Communication compliance > Settings > Priority user groups

1. Create priority groups:
   - **Group 1:** Registered representatives
   - **Group 2:** Investment advisers
   - **Group 3:** Executives
   - **Group 4:** IT administrators with agent access

2. Configure alert routing:
   - High severity: Immediate email + Teams notification
   - Medium severity: Daily digest
   - Low severity: Weekly review queue

---

## Step 6: Create Review Workflow

**Portal Path:** Purview > Communication compliance > Alerts

1. Navigate to **Alerts** tab
2. For each policy, configure:
   - **Initial review:** Analyst triage (24 hours)
   - **Escalation:** Investigator (if confirmed)
   - **Remediation options:**
     - Resolve (no violation)
     - Escalate to HR/Legal
     - Remediation required

3. Review workflow:
   - Alert Generated > Analyst Review (24h)
   - Confirmed Violation? No > Resolve + Document
   - Confirmed Violation? Yes > Escalate to Investigator
   - Investigation (48h) > Remediation Action

---

## Validation

After completing the configuration, verify:

1. [ ] Communication Compliance roles assigned to appropriate users (Admin, Analyst, Investigator, Viewer)
2. [ ] At least one policy created and enabled (Inappropriate Content, Regulatory Violations, or Customer Data)
3. [ ] Trainable classifiers enabled in Settings > Classifiers
4. [ ] Priority user groups configured with alert routing rules

**Expected Result:** Communication Compliance policies monitor agent interactions and generate alerts for review in the Alerts queue.

---

[Back to Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
