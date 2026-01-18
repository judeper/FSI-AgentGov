# Control 1.12: Insider Risk Detection and Response - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md).

---

## Prerequisites

- Microsoft 365 E5 or E5 Insider Risk Management add-on
- Insider Risk Management roles assigned
- HR data connector configured (recommended)
- Investigation team trained
- Privacy settings reviewed with Legal

---

## Step 1: Enable Insider Risk Management

**Portal Path:** Microsoft Purview > Insider risk management > Settings

1. Navigate to [Microsoft Purview Compliance Portal](https://compliance.microsoft.com)
2. Go to **Insider risk management**
3. Complete initial setup wizard:
   - Accept terms and conditions
   - Configure basic settings
4. Navigate to **Settings** for detailed options

---

## Step 2: Configure Analytics

**Portal Path:** Insider risk management > Settings > Analytics

1. Go to **Settings** > **Analytics**
2. Enable **Insider risk analytics**
3. Wait 24-48 hours for initial analysis
4. Review analytics dashboard for:
   - Potential data leaks
   - Security policy violations
   - Risky user activity patterns

---

## Step 3: Create Insider Risk Policies

**Portal Path:** Insider risk management > Policies > + Create policy

### Policy 1: Data Theft by Departing Users

1. Click **+ Create policy**
2. **Template:** Data theft by departing users
3. **Policy name:** `FSI-DepartingUser-DataTheft`
4. **Users and groups:** All users or Priority user groups
5. **Priority content:**
   - SharePoint sites (sensitive sites)
   - Sensitivity labels (Confidential, MNPI)
   - Sensitive info types (Financial SITs)
6. **Triggering event:** HR connector (resignation date) or Azure AD deletion
7. **Indicators:**
   - Downloading content from SharePoint
   - Sending email with attachments outside org
   - Uploading files to cloud storage
   - Printing documents
   - Copying to USB
8. Click **Create policy**

### Policy 2: Data Leaks (General)

1. Click **+ Create policy**
2. **Template:** Data leaks
3. **Policy name:** `FSI-DataLeaks-General`
4. **Users:** All users
5. **Priority content:** Sensitivity labels, Sensitive info types
6. **Indicators:**
   - Email to external recipients
   - File sharing externally
   - Endpoint exfiltration
   - Cumulative exfiltration
7. **Policy settings:** Include DLP policy matches as risk indicators
8. Click **Create policy**

### Policy 3: Security Policy Violations

1. Click **+ Create policy**
2. **Template:** Security policy violations
3. **Policy name:** `FSI-SecurityViolations`
4. **Indicators:**
   - Security alert indicators
   - Defender for Endpoint alerts
   - Failed authentication attempts
   - Risky sign-in behavior
5. **Users:** Priority users (agent administrators, developers)
6. Click **Create policy**

### Policy 4: Agent-Related Insider Risk

1. Click **+ Create policy**
2. **Template:** Custom policy
3. **Policy name:** `FSI-AgentRelated-InsiderRisk`
4. **Triggering event:** Activity-based
5. **Indicators:**
   - Access to sensitive SharePoint sites (agent knowledge sources)
   - Bulk download of agent-related content
   - Modification of agent configurations
   - Sharing agent access with unauthorized users
6. **Priority content:** Agent knowledge base sites, Copilot Studio projects
7. Click **Create policy**

---

## Step 4: Configure Priority User Groups

**Portal Path:** Insider risk management > Settings > Priority user groups

1. Go to **Settings** > **Priority user groups**
2. Click **+ Create priority user group**
3. Create groups:

| Group Name | Users | Purpose |
|------------|-------|---------|
| FSI-HighRiskUsers | Departing + PIP users | Enhanced monitoring |
| FSI-AgentAdmins | Power Platform admins | Agent access monitoring |
| FSI-TradingFloor | Trading staff | MNPI protection |
| FSI-CustomerData | Client-facing staff | NPI protection |

---

## Step 5: Configure Data Connectors

**Portal Path:** Insider risk management > Settings > Data connectors

1. Go to **Settings** > **Data connectors**
2. Configure HR connector:
   - Configure Azure Logic App or API
   - Map fields (user ID, resignation date, termination date)
   - Test connection
3. Configure additional connectors as needed

---

## Step 6: Configure Investigation Settings

**Portal Path:** Insider risk management > Settings > Investigation

1. Go to **Settings** > **Investigation**
2. Configure:
   - **Case name format:** Auto-generate or custom
   - **Reviewer notifications:** Email on new alerts
   - **Investigation duration:** Track SLAs
3. **Evidence collection:**
   - Collect activity explorer data
   - Preserve audit logs
   - Enable content preview (with privacy controls)

---

## Step 7: Set Up Alert Workflow

**Portal Path:** Insider risk management > Alerts

1. Navigate to **Alerts** tab
2. Configure alert triage:
   - **Needs review:** Initial state
   - **Confirmed:** Escalate to case
   - **Dismissed:** False positive (document reason)
   - **Resolved:** No further action needed

3. Configure escalation SLAs:
   - Low/Medium alerts: 48-hour review
   - High/Critical alerts: 4-hour review
   - Confirmed: Create case with investigator assignment

---

*Updated: January 2026 | Version: v1.1*
