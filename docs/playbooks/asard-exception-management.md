# Agent Sharing Exception Management

## Purpose

This playbook describes how to manage time-bound exceptions for agent sharing compliance violations in the Agent Sharing Access Restriction Detector (ASARD) solution. Exceptions support scenarios where agents legitimately require sharing configurations that would otherwise be flagged as non-compliant against zone-based rules.

**Scope:**
- Manual exception entry and approval (ASARD v1)
- Exception lifecycle management (creation, renewal, expiration)
- Automated exception review and expiration handling
- Monitoring and reporting

**Version:** 1.0.0  
**Last Updated:** 2026-02-13

---

## Overview

### What Are Exceptions?

Exceptions are time-bound approvals that allow specific agents to maintain sharing configurations that violate zone-based rules. The ASARD solution supports compliance with regulatory requirements by:

- Tracking exceptions with justification, approver, and expiration date
- Excluding agents with active exceptions from remediation actions
- Automatically resetting expired exceptions to trigger re-evaluation
- Sending Teams notifications when exceptions approach expiration

### Exception Data Model

Exceptions are tracked in the `gov_asardexception` Dataverse table:

| Column | Type | Description |
|--------|------|-------------|
| `gov_expirationdate` | DateTime | Expiration date for the exception (UTC) |
| `gov_justification` | Memo | Business justification for the exception (max 1MB) |
| `gov_approvedby` | String | Name or email of the approver (max 256 chars) |
| `gov_approvedat` | DateTime | Timestamp when exception was approved (UTC) |
| `gov_reviewdate` | DateTime | Optional: Next review date for the exception (UTC) |

When `gov_status = 2` (Active) **AND** `gov_expirationdate >= now()`, the agent is considered to have an active exception.

---

## Exception Criteria

### When to Grant an Exception

Exceptions support legitimate business needs where sharing configurations cannot comply with zone rules. Common scenarios include:

**Zone 1 (Personal Productivity):**
- Cross-functional collaboration requiring named security group access
- Temporary project teams needing shared agent access

**Zone 2 (Team Collaboration):**
- Enterprise-wide communication agents (e.g., IT help desk bots)
- Temporary public-facing pilots or demos

**Zone 3 (Enterprise Managed):**
- Migration periods during approved group provisioning
- Emergency access scenarios pending security group creation

### When NOT to Grant an Exception

Do not grant exceptions for:
- Permanent violations that should be remediated (update approved groups policy instead)
- Agents with no documented business justification
- Expired exceptions without renewal approval
- Agents that can be reconfigured to comply with zone rules

---

## Exception Lifecycle

### 1. Exception Creation (Manual)

ASARD v1 uses manual exception entry via direct Dataverse record updates. No Canvas app UI is provided in this release.

**Procedure:**

1. **Identify the agent:** Obtain `gov_agentid` and `gov_environmentid` from detection scan output (CSV or Dataverse query)

2. **Navigate to Dataverse:** Open the `gov_asardexception` table in Power Apps (make.powerapps.com → Dataverse → Tables)

3. **Locate the record:** Filter by `gov_agentid` and `gov_environmentid`

4. **Update exception fields:**
   - `gov_status`: Set to `2` (Active)
   - `gov_expirationdate`: Set expiration date (e.g., 90 days from now)
   - `gov_justification`: Document business justification (required)
   - `gov_approvedby`: Enter approver name/email (required)
   - `gov_approvedat`: Set to current UTC timestamp
   - `gov_reviewdate`: Optional, set for mid-term review (e.g., 45 days)

5. **Save the record**

**Example Dataverse update payload (via Web API):**

```json
{
  "gov_status": 2,
  "gov_expirationdate": "2026-05-15T00:00:00Z",
  "gov_justification": "Cross-functional project team collaboration (Project Omega). Approved by PMO for Q2 2026 duration. Requires access from Sales, Marketing, and Engineering security groups.",
  "gov_approvedby": "Jane Doe (jane.doe@contoso.com)",
  "gov_approvedat": "2026-02-13T10:30:00Z",
  "gov_reviewdate": "2026-04-01T00:00:00Z"
}
```

### 2. Exception Renewal

To renew an expiring exception:

1. **Review justification:** Confirm that the business need still exists
2. **Update `gov_expirationdate`:** Extend to new expiration date
3. **Update `gov_reviewdate`:** Optional, set next review milestone
4. **Document renewal:** Update `gov_justification` with renewal note (append to existing text)

**Example renewal justification:**

```
[ORIGINAL] Cross-functional project team collaboration (Project Omega)...

[RENEWAL 2026-05-01] Project extended through Q3 2026 per PMO approval. Security groups remain required for cross-team access. Renewed by Jane Doe.
```

### 3. Exception Expiration

Expired exceptions are automatically handled by the **Exception Review Workflow** (Power Automate flow):

**Daily Process (08:00 UTC):**

1. **Query for expired exceptions:**  
   `gov_status eq 2 AND gov_expirationdate < today`

2. **Auto-reset records:**
   - Set `gov_status = 1` (Expired)
   - Clear all exception-related fields

3. **Send Teams notification:**  
   Post expired exception list to governance leads channel

4. **Trigger re-scan:**  
   Next detection run will re-evaluate agents and flag as non-compliant if still violating zone rules

---

## Monitoring Expiring Exceptions

### Automated Notifications

The Exception Review Workflow sends Teams notifications for:

**Expiring Exceptions (14-day threshold):**
- Adaptive card with list of exceptions expiring within 14 days
- Includes agent name, environment, days remaining, approver, justification preview
- Action buttons: "View Compliance Dashboard", "Exception Management Playbook"

**Expired Exceptions:**
- Adaptive card with list of exceptions that were reset to NonCompliant
- Includes agent name, environment, expired date, previous justification
- Notice about auto-remediation trigger

**Channel Configuration:**

The workflow posts to a Teams channel specified during deployment. Default: Same channel as main ASARD alert notifications.

### Manual Queries

To check for expiring exceptions manually:

**Dataverse FetchXML:**

```xml
<fetch>
  <entity name="gov_asardexception">
    <attribute name="gov_agentname" />
    <attribute name="gov_environmentname" />
    <attribute name="gov_expirationdate" />
    <attribute name="gov_approvedby" />
    <attribute name="gov_justification" />
    <filter type="and">
      <condition attribute="gov_status" operator="eq" value="2" />
      <condition attribute="gov_expirationdate" operator="ge" value="@{utcNow()}" />
      <condition attribute="gov_expirationdate" operator="le" value="@{addDays(utcNow(), 14)}" />
    </filter>
    <order attribute="gov_expirationdate" />
  </entity>
</fetch>
```

**Dataverse Web API** (replace `contoso` with your organization's Dataverse domain)**:**

```
GET https://contoso.crm.dynamics.com/api/data/v9.2/gov_asardexceptions
?$select=gov_agentname,gov_environmentname,gov_expirationdate,gov_approvedby
&$filter=gov_status eq 2 and gov_expirationdate ge @now and gov_expirationdate le @fourteendays
&$orderby=gov_expirationdate asc
```

---

## Validation

### Verify Exception Is Active

**Test Criteria:**
- Detection script excludes agent from non-compliant count
- Remediation script skips agent with message: "Agent X has active exception (expires YYYY-MM-DD) — skipping remediation"

**Verification Steps:**

1. Grant exception via Dataverse record update (see Exception Creation procedure)

2. Run detection script in dry-run mode:
   ```powershell
   python scripts/detect_agent_sharing_violations.py --dry-run --verbose
   ```

3. Verify console output:
   - Agent is marked as "Exception" (not "NonCompliant")
   - Summary shows exception count incremented

4. Run remediation script in WhatIf mode:
   ```powershell
   python scripts/remediate_agent_sharing.py --whatif --from-dataverse --verbose
   ```

5. Verify console output:
   - Agent is skipped with message: "Agent X has active exception (expires YYYY-MM-DD) — skipping remediation"
   - Summary shows "Skipped (active exceptions): 1"

### Verify Exception Expiration

**Test Criteria:**
- Expired exceptions are auto-reset to NonCompliant
- Teams notification is sent with expired exception list
- Next detection scan flags agent as non-compliant

**Verification Steps:**

1. Create test exception with expiration date in the past:
   ```json
   {
     "gov_status": 2,
     "gov_expirationdate": "2026-01-01T00:00:00Z",
     "gov_justification": "Test expired exception",
     "gov_approvedby": "Test User"
   }
   ```

2. Manually trigger Exception Review Workflow via Power Automate portal

3. Verify workflow output:
   - "Query Expired Exceptions" action returns test record
   - "Update Expired Exception To NonCompliant" action executes
   - "Post Expired Notification" action sends Teams card

4. Query Dataverse record:
   - Verify `gov_status = 1` (Expired)
   - Verify all exception-related fields are null

5. Run detection script:
   ```powershell
   python scripts/detect_agent_sharing_violations.py --dry-run
   ```

6. Verify console output:
   - Agent is marked as "NonCompliant" (no active exception)

---

## Troubleshooting

### Exception Not Recognized by Detection Script

**Symptoms:**
- Agent with exception is still marked as "NonCompliant"
- Exception count in summary is 0

**Diagnosis:**

1. Verify record has active exception:
   - `gov_status = 2`
   - `gov_expirationdate >= current UTC date`

2. Check detection script logs:
   ```powershell
   python scripts/detect_agent_sharing_violations.py --verbose --log-file detect.log
   ```

3. Search logs for exception check messages:
   ```
   Agent X has active exception (expires YYYY-MM-DD) — preserving exception fields
   ```

**Resolution:**

- If `gov_status ≠ 2`: Update to `2` (Active)
- If `gov_expirationdate` is null or past: Set valid future date
- If logs show no exception check: Verify detection script is Phase 4 version (includes exception logic in `upsert_compliance_record` function)

### Remediation Script Still Remediates Agent with Exception

**Symptoms:**
- Agent with active exception is remediated despite skip logic
- No "skipping remediation" message in logs

**Diagnosis:**

1. Verify remediation script is Phase 4 version:
   ```powershell
   grep -n "active exception" scripts/remediate_agent_sharing.py
   ```
   Expected: Line with "Agent X has active exception (expires ...)"

2. Check remediation logs:
   ```powershell
   python scripts/remediate_agent_sharing.py --whatif --from-dataverse --verbose --log-file remediate.log
   ```

3. Search logs for exception check messages

**Resolution:**

- If exception check code missing: Update to Phase 4 version of remediation script
- If exception expired: Verify `gov_expirationdate >= now()`
- If Dataverse query fails: Check connection string and permissions

### Exception Review Workflow Not Triggering

**Symptoms:**
- No Teams notifications for expiring/expired exceptions
- Expired exceptions not auto-reset

**Diagnosis:**

1. Verify workflow is enabled:
   - Navigate to Power Automate portal → My flows
   - Check "ASARD Exception Review Workflow" status (should be "On")

2. Check workflow run history:
   - Click workflow → "28-day run history"
   - Verify daily runs at 08:00 UTC

3. Check for errors in run history:
   - Click failed run → View action details

**Resolution:**

- If workflow disabled: Enable via Power Automate portal
- If query action fails: Verify Dataverse connection reference
- If Teams action fails: Verify Teams connection reference and channel ID
- If no expiring/expired exceptions: Test with manual exception (set gov_expirationdate to past date)

### Teams Notification Not Received

**Symptoms:**
- Workflow runs successfully but no adaptive card appears in Teams

**Diagnosis:**

1. Verify Teams channel ID in workflow:
   - Edit workflow → "Post_Expiring_Notification" action
   - Check `location` parameter (should be Teams channel GUID)

2. Verify adaptive card template URL:
   - Edit workflow → "Load_Expiring_Card_Template" action
   - Check `uri` parameter (should resolve to valid JSON file)

3. Test adaptive card rendering:
   - Copy adaptive card JSON to Adaptive Cards Designer (adaptivecards.io/designer)
   - Verify card renders without errors

**Resolution:**

- If channel ID invalid: Update workflow with correct Teams channel GUID
- If template URL fails: Host templates in accessible location (GitHub raw, Azure Blob)
- If card rendering fails: Fix JSON syntax errors in adaptive card template

---

## Related Documentation

- **ASARD Deployment Playbook:** `docs/playbooks/asard-deployment-guide.md` (Phase 5)
- **ASARD Detection Script:** `scripts/detect_agent_sharing_violations.py`
- **ASARD Remediation Script:** `scripts/remediate_agent_sharing.py`
- **Exception Review Workflow:** `agent-sharing-access-restriction-detector/src/asard-exception-review-workflow.json` (in FSI-AgentGov-Solutions)
- **Adaptive Card Templates:** (in FSI-AgentGov-Solutions)
  - Expiring: `agent-sharing-access-restriction-detector/src/adaptive-card-asard-exception-expiring.json`
  - Expired: `agent-sharing-access-restriction-detector/src/adaptive-card-asard-exception-expired.json`

---

## Appendix: Exception Approval Template

Use this template for documenting exception approvals in `gov_justification` field:

```
EXCEPTION REQUEST

Agent: [Agent Display Name]
Environment: [Environment Name]
Requested By: [Requestor Name/Email]
Approved By: [Approver Name/Email]
Approval Date: [YYYY-MM-DD]
Expiration Date: [YYYY-MM-DD]

BUSINESS JUSTIFICATION:
[Detailed explanation of why agent requires broader sharing than zone rules allow. Include:
- Specific business scenario or project
- Why zone-compliant sharing is not feasible
- Security mitigations in place
- Expected duration of need]

COMPLIANCE IMPACT:
- Zone: [1/2/3]
- Violation Type: [Everyone/Public/UnapprovedGroup/ExcessiveIndividual/CrossTenant]
- Current Sharing: [Description of current principals]
- Approved Sharing: [Description of approved principals for exception period]

REVIEW SCHEDULE:
- Mid-term Review: [YYYY-MM-DD or "N/A"]
- Expiration Review: [YYYY-MM-DD]

RENEWAL HISTORY:
[Leave blank for new exceptions. Update during renewals with:
- Renewal Date: [YYYY-MM-DD]
- Renewed By: [Name/Email]
- Justification: [Updated business need or confirmation of ongoing need]]
```

---

**Document Version:** 1.0.0  
**Phase:** 4 (Exception Management)  
**Requirements:** EXC-01, EXC-02
