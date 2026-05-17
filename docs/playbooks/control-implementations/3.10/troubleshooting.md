# Troubleshooting: Control 3.10 - Hallucination Feedback Loop

**Last Updated:** April 2026
**Troubleshooting Level:** Control Implementation

> This playbook provides troubleshooting guidance for [Control 3.10](../../../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md). Issues are grouped by failure point: capture, intake, triage, escalation, reporting, and retention.

---

## Capture Layer (Copilot Studio)

### Issue 1: Thumbs Down Not Available to Users

**Symptoms:**
- Users report no feedback control appears on agent responses
- CSAT analytics show zero responses despite agent traffic

**Root Causes:**
1. CSAT toggle disabled at the agent level
2. Agent published before CSAT was enabled (changes not yet propagated)
3. Channel-specific renderer does not support CSAT (older Teams clients, custom Direct Line clients)
4. Tenant-level Copilot Studio analytics setting disabled

**Resolution Steps:**

1. **Confirm the agent setting:**
   - Copilot Studio → agent → **Settings** → **Customer satisfaction**
   - Confirm **Allow users to provide feedback** is **On**
2. **Republish:** Click **Publish**, wait 5 minutes, then test in an incognito session
3. **Test in the Copilot Studio test pane** first to isolate channel issues — if feedback appears in the test pane but not in Teams, the channel client is the issue
4. **For Teams:** Verify users are on a current Teams desktop or web client; mobile clients have historically lagged in CSAT support
5. **For custom Direct Line clients:** CSAT events must be implemented client-side; consult your client developer

---

### Issue 2: `Report Inaccurate Response` Topic Not Triggering

**Symptoms:**
- Trigger phrases like `report a hallucination` route to the default fallback or a different topic

**Root Causes:**
1. Topic not published after edits
2. Trigger phrase collision with a higher-priority topic
3. Generative orchestration enabled and overriding classic topic triggers

**Resolution Steps:**

1. Confirm topic status is **Published** (not just Saved)
2. In Copilot Studio → **Topics**, search for the trigger phrase across all topics; consolidate or re-prioritize
3. If generative orchestration is enabled, add an explicit description to the topic that emphasizes user intent ("User wants to report that the agent gave an incorrect answer") so the orchestrator selects it reliably
4. Test with each trigger phrase variant; add more variants if any miss

---

## Intake Layer (Power Automate)

### Issue 3: Intake Flow Returns 401 / 403 from SharePoint

**Symptoms:**
- Flow run history shows `Create item` action failing with `401 Unauthorized` or `403 Forbidden`

**Root Causes:**
1. Connection used by the flow does not have **Contribute** access on the AI Governance site
2. Connection token expired or revoked
3. Flow owner removed from the site

**Resolution Steps:**

1. Identify the SharePoint connection used by the flow (Flow → **Connections**)
2. As **SharePoint Site Owner**, ensure the connection's account has at minimum **Contribute** access on the site
3. Re-authenticate the connection from Power Automate
4. If using a **service account**, document the account in your WSP and apply Conditional Access exclusion if required for unattended flow runs (coordinate with Identity governance)

---

### Issue 4: Duplicate Items Created from a Single Report

**Symptoms:**
- Two or more identical items appear in `Hallucination Tracking` for the same `ConversationId`

**Root Causes:**
1. Both the CSAT path and the `Report Inaccurate Response` topic posted to intake
2. User clicked the topic action multiple times
3. Flow retried after a transient SharePoint failure

**Resolution Steps:**

1. **Decide deduplication policy:** Most firms tolerate duplicates and resolve them at triage to avoid losing distinct user signal. Document the chosen policy in your run-sheet.
2. **If automated dedup is required:** Add a **Get items** step at the start of the intake flow filtered by `ConversationId` from the last 5 minutes; if a match exists, append a comment to the existing item rather than creating a new one
3. **Disable one path** if you only want a single intake (typically prefer the topic path because it captures category and severity)

---

### Issue 5: Critical Escalation Did Not Fire

**Symptoms:**
- A `Severity = Critical` item was created but no Teams card and no Control 3.4 incident appeared

**Root Causes:**
1. Condition branch evaluating the wrong field (`Severity` vs `ConfirmedSeverity`)
2. Teams connector unauthorized or channel deleted
3. Control 3.4 intake URL changed
4. Severity submitted as lowercase `critical` while condition checks for `Critical`

**Resolution Steps:**

1. Inspect the failed run in **Flow runs** → click the Condition step to see actual evaluated values
2. Normalize severity values at intake (`toLower(triggerBody()?['severity'])`)
3. Validate the Control 3.4 incident endpoint with a manual HTTP test
4. Re-create the Teams connection if the connector shows a red exclamation icon

---

## Reporting Layer (Power BI)

### Issue 6: Dashboard Shows Stale or Incomplete Data

**Symptoms:**
- KPIs lag the SharePoint list by hours or days
- Refresh history shows failures

**Root Causes:**
1. Scheduled refresh disabled or beyond Power BI Pro daily limit (8/day)
2. Dataset credentials expired
3. SharePoint list view exceeds 5,000 items and triggers throttling
4. Column type mismatch after a list schema change

**Resolution Steps:**

1. Power BI workspace → dataset → **Settings** → **Scheduled refresh**: confirm enabled and within license limits
2. Re-authenticate **Data source credentials**
3. For lists > 5,000 items, switch to **incremental refresh** keyed on `ReportDate`, or migrate the dataset to **Dataverse**
4. After any list schema change, refresh the dataset's **Power Query** definition; remove and re-add the changed column

---

### Issue 7: Hallucination Rate Calculation Is Implausibly High or Low

**Symptoms:**
- Trend detector fires constantly or never fires
- Reported rates do not match perceived agent quality

**Root Causes:**
1. Conversation count denominator pulled from the wrong source (e.g., counting only sessions vs. counting turns)
2. Test traffic included in production conversation counts
3. Multiple feedback items per conversation inflate the numerator

**Resolution Steps:**

1. Define and document a single canonical denominator (e.g., distinct `ConversationId` per day per agent from Dataverse)
2. Tag synthetic / test traffic with a marker prompt or test user account, and exclude it from both numerator and denominator
3. For numerator, dedupe by `ConversationId` if your policy is one-report-per-conversation, or accept multiple reports per conversation and document the choice

---

## Retention and Evidence Layer

### Issue 8: Retention Label Not Applying to New Items

**Symptoms:**
- `Compliance details` on a new list item shows no label
- Records Manager cannot see items in disposition review

**Root Causes:**
1. Retention label policy not yet published to the site (publish can take up to 24 hours)
2. Label scoped to a different site collection
3. Label requires manual application and the intake flow does not apply it

**Resolution Steps:**

1. **Purview portal** → **Records management** → **Label policies** → confirm the policy targets the AI Governance site
2. Wait up to 24 hours after publish, then test with a new item
3. If labels must be applied automatically, configure an **auto-apply policy** with a keyword or location condition, or have the intake flow call the **Set retention label** SharePoint action
4. Engage **Purview Records Manager** to validate the label configuration before relying on it for SEC 17a-4 evidence

---

### Issue 9: Conversation Transcript Not Retrievable for Audit

**Symptoms:**
- Audit asks for the full conversation around a hallucination report; only the single user query and agent response are available

**Root Causes:**
1. Dataverse conversation transcript table not retained long enough
2. `ConversationId` not captured at intake
3. Application Insights retention shorter than SEC 17a-4 minimum

**Resolution Steps:**

1. Verify intake flow captures `ConversationId` for every report (see Test Case 1)
2. Configure Dataverse table retention or export conversation transcripts on a schedule to long-term storage (Azure Storage with immutability policy is one option — coordinate with Records Management)
3. Increase Application Insights retention to at least 730 days and export to long-term storage for the remaining 4+ years
4. Consider Control 4.x (SharePoint pillar) for archival landing zone

---

## Diagnostic Commands

```powershell
# Recent reports (last 7 days)
Get-PnPListItem -List "Hallucination Tracking" -Query @"
<View>
  <Query>
    <Where>
      <Geq>
        <FieldRef Name='Created'/>
        <Value Type='DateTime'><Today OffsetDays='-7'/></Value>
      </Geq>
    </Where>
  </Query>
</View>
"@ | Select-Object Id, FieldValues

# Open critical issues
Get-PnPListItem -List "Hallucination Tracking" |
    Where-Object {
        $_["Status"] -ne "Closed" -and
        $_["ConfirmedSeverity"] -eq "Critical"
    } |
    Select-Object Id, @{N='IssueID';E={$_["IssueID"]}}, @{N='Agent';E={$_["AgentName"]}}

# Flow status — replace with your environment GUID
Get-AdminFlow -EnvironmentName "<environment-GUID>" |
    Where-Object { $_.DisplayName -like "*HFL*" -or $_.DisplayName -like "*Hallucination*" } |
    Select-Object DisplayName, Enabled, LastModifiedTime
```

> All commands above assume you have read the [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md) and pinned module versions. Sovereign-cloud tenants must add the appropriate `-Endpoint` / `-Environment` parameters.

---

## Escalation Path

| Issue Severity | Escalate To | Response Time |
|----------------|-------------|---------------|
| Active customer harm or regulatory exposure | AI Governance Lead + Compliance Officer + Legal | Immediate |
| Tracking system down or evidence at risk | AI Administrator + Power Platform Admin | 4 hours |
| High-volume backlog (> 50 open Critical/High) | AI Governance Lead | 24 hours |
| Repeat critical hallucination (same root cause within 30 days) | Model Risk Manager + AI Governance Lead | 24 hours |
| Retention or audit evidence gap | Purview Records Manager + Compliance Officer | 1 business day |

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) — Initial configuration
- [PowerShell Setup](./powershell-setup.md) — Automation scripts
- [Verification & Testing](./verification-testing.md) — Test procedures

---

[Back to Control 3.10](../../../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
