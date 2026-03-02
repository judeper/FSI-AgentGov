# Control 1.6: Microsoft Purview DSPM for AI - Verification & Testing

> This playbook provides verification and testing guidance for [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md).

---

## Verification Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to purview.microsoft.com > DSPM for AI | Dashboard displayed |
| 2 | Check Get Started completion | All steps show completed |
| 3 | Review Recommendations | Actions tracked with status |
| 4 | Access Reports | Interaction data visible |
| 5 | Check Policies | Required policies enabled |
| 6 | Open Activity explorer | AI interactions logged |
| 7 | Review Data risk assessments | Assessment capability available |

---

## Get Started Verification

### Step 1: Audit Activation

- [ ] DSPM Get started shows Step 1 completed
- [ ] Purview Audit page indicates logging is enabled
- [ ] Recent audit events are present

### Steps 2-4: Extended Visibility

- [ ] Browser extension deployed (if applicable)
- [ ] Devices onboarded (if applicable)
- [ ] Extended insights enabled (if applicable)

---

## Reports Verification

1. Navigate to **DSPM for AI > Reports**
2. Verify data is populating:
   - Total interactions trend chart shows data
   - Sensitive interactions per AI app shows breakdown
   - User interaction metrics are visible

---

## Activity Explorer Verification

1. Navigate to **DSPM for AI > Activity explorer**
2. Apply filters:
   - Date range: Last 7 days
   - AI app category: Copilot experiences & agents
3. Verify:
   - AI interaction events are logged
   - User information is captured
   - Sensitive info types are detected (if applicable)
4. Test export function

---

## Data Risk Assessment Verification

### Weekly Assessment Functionality

| Test | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to DSPM for AI dashboard | All four tabs (Overview, Identify, Protect, Monitor) load with data |
| 2 | Check default assessment status | Weekly assessment shows recent run date and site count (top 100 sites) |
| 3 | Review Protect tab for oversharing | Sites with broad permissions are flagged with remediation options |
| 4 | Create custom assessment for specific site | Assessment queues and produces results within 4 days |
| 5 | Verify assessment covers sensitivity label detection | Unlabeled content flagged in Identify tab |

### Dashboard Tab Verification

1. **Overview Tab:**
   - [ ] Sites scanned count displayed
   - [ ] Sensitive items found summary visible
   - [ ] Risk score per site/workspace shown

2. **Identify Tab:**
   - [ ] Coverage percentage displayed (data scanned vs. not scanned)
   - [ ] Unscanned volumes identified
   - [ ] Unlabeled content flagged

3. **Protect Tab:**
   - [ ] Sites with organization-wide sharing flagged
   - [ ] Sites with external sharing flagged
   - [ ] Remediation options available

4. **Monitor Tab:**
   - [ ] Sharing breakdown by access type displayed
   - [ ] Specific people access shown
   - [ ] External and organization-wide access tracked
   - [ ] Group-based access visible

### Assessment Schedule Verification

1. Navigate to **DSPM for AI > Data risk assessments**
2. Verify default assessment runs successfully
3. Review results for:
   - Assessment run date (weekly schedule)
   - Sites scanned (top 100 by usage)
   - Overshared items count
   - Severity levels
   - Affected sites/users
4. Confirm timing:
   - Initial results appeared within 4 days
   - Subsequent results refresh within 48 hours

### Evidence Collection

**Export DSPM assessment summary as PDF** for compliance documentation. Include:

- Assessment date
- Sites scanned count
- Findings count by severity
- Remediation status
- Dashboard screenshots showing all four tabs
- Assessment configuration showing weekly schedule

---

## Enhanced DSPM AI Observability Verification (Preview)

!!! warning "Preview Feature — Tenant Availability Varies"
    Enhanced DSPM AI Observability capabilities are rolling out gradually. Not all tenants have preview access. If your tenant does not have unified DSPM experience, these test cases will not be applicable until GA (June 2026).

### Test Case: DSPM-01 - Verify Unified DSPM Experience Accessibility

**Objective:** Confirm tenant has access to unified DSPM experience (preview) or confirm classic DSPM for AI is available

**Prerequisites:**
- E5 or E5 Compliance license active
- Purview Compliance Admin role assigned
- DSPM for AI Get Started wizard completed

**Test Steps:**

1. Navigate to Microsoft Purview (https://purview.microsoft.com)
2. In left navigation, select **Solutions**
3. Look for **Data Security Posture Management** (unified) OR **DSPM for AI** (classic)
4. If unified experience: Verify single dashboard with both AI and non-AI data security metrics
5. If classic experience: Document tenant is not yet in preview ring; test cases DSPM-02/03 deferred until GA

**Expected Outcome (Preview-Enabled Tenant):**
- Unified DSPM experience accessible with integrated dashboard
- Navigation shows "Data Security Posture Management" (not separate "DSPM for AI")
- Dashboard displays agent risk observability section
- Activity Explorer includes enhanced filtering options

**Expected Outcome (Non-Preview Tenant):**
- Classic DSPM for AI experience remains available
- Navigation shows separate "DSPM for AI" section
- Weekly risk assessments and Activity Explorer function as documented in existing test cases
- Monitor Message Center for MC1191257 availability notification

**Evidence to Collect:**
- Screenshot: Purview navigation showing unified DSPM OR classic DSPM for AI
- Screenshot: Dashboard showing unified experience OR classic dashboard
- Note: Tenant preview ring status (enabled/not enabled)

---

### Test Case: DSPM-02 - Verify Agent Risk Observability Data

**Objective:** Confirm agent risk observability dashboards are populating with per-agent risk scores

**Prerequisites:**
- Unified DSPM experience accessible (tenant in preview ring)
- At least one Copilot Studio or Agent Builder agent deployed and active
- Agent has generated interactions (minimum 10 events in last 7 days)
- DSPM for AI Get Started wizard completed

**Test Steps:**

1. Navigate to **Purview > Data Security Posture Management > AI Risk Dashboard** (or equivalent unified dashboard tab)
2. Verify agent risk summary displays with agent names and risk scores
3. Select a high-risk agent (if none present, select any agent with risk score data)
4. Review contributing factors:
   - Data sensitivity accessed
   - Access pattern analysis
   - Policy violations (if any)
   - Oversharing assessment findings
5. Export agent risk summary to CSV
6. Verify export includes: AgentName, RiskScore, RiskFactors, LastAssessed timestamp

**Expected Outcome:**
- Agent risk dashboard displays active agents with risk scores (High/Medium/Low)
- Risk scores are based on actual agent activity (not placeholder data)
- Contributing factors explain risk score rationale
- Export generates valid CSV with all expected columns
- Risk scores update at least weekly (check LastAssessed timestamp)

**Expected Outcome (No Risk Data):**
- If risk data not populating: Verify Application Insights integration configured (see troubleshooting DSPM-02)
- If agents deployed <7 days ago: Risk scoring may require 7-14 days of activity baseline
- Data latency: Risk scores update weekly; new agents may show "Insufficient Data" until baseline established

**Evidence to Collect:**
- Screenshot: Agent risk dashboard showing risk scores
- Screenshot: Contributing factors for one high/medium risk agent
- Export: Agent risk summary CSV file
- Documentation: Risk score calculation methodology (from Purview portal help text)

---

### Test Case: DSPM-03 - Verify Activity Explorer Enhanced Filters

**Objective:** Confirm Activity Explorer enhanced filters for AI-specific event data are functional

**Prerequisites:**
- Unified DSPM experience accessible (tenant in preview ring)
- Activity Explorer has AI interaction events (minimum 50 events in last 30 days)
- DSPM for AI Get Started wizard completed

**Test Steps:**

1. Navigate to **Purview > Data Security Posture Management > Activity explorer**
2. Test multi-agent selection filter:
   - Click "Agent" filter dropdown
   - Select 2+ agents using shift-click or ctrl-click
   - Verify results show events for all selected agents
3. Test data classification filter:
   - Click "Sensitivity Label" filter
   - Select "Confidential" or "Highly Confidential"
   - Verify results show only events with selected sensitivity labels
4. Test advanced search:
   - Enter search query: `Agent:"[AgentName]" AND SensitivityLabel:"Confidential"`
   - Verify results match combined criteria
5. Test enhanced export:
   - Select 7-day date range
   - Click **Export** > **Enhanced CSV**
   - Open exported file and verify columns include: EventTimestamp, User, AgentName, ActivityType, DataSource, SensitivityLabel, PolicyActions
6. Compare enhanced export to classic export:
   - Note additional metadata fields (RiskScore, AccessPattern) present in enhanced export

**Expected Outcome:**
- Multi-agent filter works (simultaneous selection of multiple agents)
- Data classification filter correctly narrows results to labeled events
- Advanced search with operators (AND, OR) functions correctly
- Enhanced CSV export includes additional metadata fields beyond classic export
- Export completes within 60 seconds for 5000 events or fewer

**Expected Outcome (Filter Not Available):**
- If enhanced filters missing: Verify unified DSPM experience is active (not classic DSPM for AI)
- If advanced search not functioning: Check preview feature flag in tenant; may require Microsoft support to enable

**Evidence to Collect:**
- Screenshot: Activity Explorer with multi-agent filter applied
- Screenshot: Advanced search query with results
- Export: Enhanced CSV file showing additional metadata columns
- Documentation: Comparison of classic vs enhanced export column list

---

## Evidence Artifacts to Retain

### DSPM Setup Evidence

- [ ] Screenshot: DSPM Get started with all steps completed
- [ ] Screenshot: Purview Audit enabled
- [ ] Export: Sample audit results

### Reports Evidence

- [ ] Screenshot: Reports page with filters visible
- [ ] Screenshot: Total interactions trend
- [ ] Screenshot: Sensitive interactions summary

### Activity Explorer Evidence

- [ ] Export: Activity explorer CSV
- [ ] Screenshot: Filters showing scoping

### Oversharing Assessment Evidence

- [ ] Screenshot: Assessment list with status and completion time
- [ ] Screenshot: Results summary showing overshared items count
- [ ] Change evidence: Remediation tickets

### Policy Evidence

- [ ] Screenshot: DLP policies as displayed in DSPM Policies
- [ ] Screenshot: Policy details showing scope and mode

---

## Confirmation Checklist

- [ ] DSPM for AI is accessible
- [ ] All Get Started steps completed
- [ ] Recommendations are tracked
- [ ] Reports show AI interaction data
- [ ] Policies are configured and enabled
- [ ] Activity explorer logs AI interactions
- [ ] Data risk assessments can run
- [ ] Evidence artifacts collected and stored

[Back to Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
