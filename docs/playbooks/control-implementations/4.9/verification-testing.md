# Control 4.9 — Verification Testing: Embedded File Content Governance

**Playbook Type:** Verification Testing
**Control:** [4.9 — Embedded File Content Governance](../../../controls/pillar-4-sharepoint/4.9-embedded-file-content-governance.md)
**Audience:** Compliance Officers, Internal Audit, Security Teams, M365 Administrators
**Estimated Time:** 2–3 hours (full test suite); 45 minutes (quarterly verification)
**Last UI Verified:** April 2026
**Test Environment Requirement:** Test agent with embedded files; test user accounts; a configured production-like tenant

!!! danger "Critical: IB Bypass Is Expected Behavior — Document It, Do Not Attempt to Fix It in Platform"
    One of the verification tests in this playbook (Test 4) explicitly **confirms that Information Barriers do NOT block content from embedded files**. This is not a test you expect to pass — it is a test that confirms a known Microsoft platform limitation exists in your environment. The correct outcome is to document this confirmed limitation as a known, assessed, and mitigated risk.

    **Do not report the IB bypass as an open finding that requires Microsoft to fix it.** Your mitigation is the Zone 3 prohibition and Zone 2 IB assessment procedure, not platform enforcement.

## Overview

This playbook defines the verification tests for all Control 4.9 effectiveness criteria. Tests are organized into five categories:

1. **Inventory completeness** — All agents with embedded files are identified and registered
2. **Sensitivity label enforcement** — Labels are present and access blocking functions correctly
3. **IB bypass documentation** — The known IB limitation is confirmed and documented
4. **Container integrity** — No orphaned or broken containers exist
5. **Agent inventory compliance** — Control 3.1 agent inventory is complete and current

---

## Test Environment Setup

Before running verification tests, prepare the following:

| Requirement | Details |
|---|---|
| Test agent with embedded files | Create a test agent via Agent Builder with at least 2 embedded files: one labeled (e.g., "Confidential"), one unlabeled |
| Test file — labeled | Any .docx or .pdf with a Confidential or higher sensitivity label applied |
| Test file — unlabeled | Any .docx or .pdf with no sensitivity label |
| Test user A — authorized | User account with extract rights to the sensitivity label applied to the test agent |
| Test user B — restricted | User account WITHOUT extract rights to the sensitivity label (e.g., external user or user in a different label scope) |
| Test user C — IB-separated | User account in an IB segment that is separated from the segment that owns the embedded content |
| Compliance officer reviewer | Individual to review and sign off IB bypass test results |
| Agent inventory (Control 3.1) | Access to the organization's agent inventory to verify record completeness |

!!! warning "Test in Non-Production Tenant if Possible"
    The IB bypass test (Test 4) involves deliberately querying an agent for IB-sensitive content to confirm the bypass occurs. If your test tenant does not have IB policies configured, you can document the test as "not applicable — IB not configured in this environment; mitigated by Zone 3 prohibition" and rely on Microsoft's published documentation of the limitation.

---

## Test 1: Embedded File Agent Inventory Completeness

**Criterion:** All agents with embedded files identified via M365 Admin Center "Embedded files" filter.
**Expected Result:** 100% of agents using embedded file knowledge sources appear in the filter results.
**Evidence Type:** Screenshot of filtered agent list; reconciliation with known agent count.

### Procedure

**Step 1.1 — Apply the Embedded Files Filter**

1. Navigate to: **M365 Admin Center › Copilot › Agents › All Agents**
2. Apply the **"Embedded files"** filter.
3. Take a screenshot of the filtered results showing all agents in the list.
4. Record the total count of agents shown.

**Step 1.2 — Reconcile with Known Agent Inventory**

1. Open the agent inventory (Control 3.1).
2. Query all inventory records where "Embedded Files = Y".
3. Compare the count and names from the M365 Admin Center filter against the inventory records.

**Step 1.3 — Record Results**

| Metric | Value |
|---|---|
| Agents in M365 Admin Center filter | ___ |
| Agents in Control 3.1 inventory with Embedded Files = Y | ___ |
| Discrepancy count | ___ |

**Pass criteria:** Zero discrepancy. Every agent appearing in the M365 Admin Center embedded files filter must have a corresponding record in Control 3.1 agent inventory.

**Fail action:** For each agent in the filter without an inventory record, immediately create the inventory record and complete the IB assessment. For each inventory record marked Embedded Files = Y that does not appear in the filter, verify the agent still exists and update the inventory record accordingly.

---

## Test 2: Sensitivity Label Presence — All Embedded File Agents

**Criterion:** Sensitivity labels applied to all embedded file containers (verified in agent Overview tab).
**Expected Result:** 100% of agents in the embedded files filter have a non-null sensitivity label in the Overview tab.
**Evidence Type:** Per-agent screenshot of Overview tab showing sensitivity label field; or PowerShell export confirming label presence.

### Procedure

**Step 2.1 — Review Each Agent's Overview Tab**

For each agent in the embedded files filter list:

1. Click the agent name to open the detail view.
2. Navigate to the **Overview** tab.
3. Locate the **Sensitivity label** field.
4. Record: Agent name, sensitivity label value (or "None" if blank).

**Step 2.2 — Run PowerShell Label Audit (Recommended)**

Use the PowerShell script from the [PowerShell Setup playbook](powershell-setup.md) Section 3.2 to generate the `03-unlabeled-files-GAPS.csv` output. Review the file for any unlabeled entries.

**Step 2.3 — Record Results**

| Metric | Value |
|---|---|
| Total agents in embedded files filter | ___ |
| Agents with sensitivity label present | ___ |
| Agents with NO sensitivity label (GAP) | ___ |
| Percentage with labels | ___% |

**Pass criteria:** 100% of agents have a sensitivity label. Zero agents with a blank or null sensitivity label.

**Fail action:** For each agent with no sensitivity label:
  - Identify whether uploaded files are labeled. If not, apply labels to files and verify the container label updates.
  - Verify that a default sensitivity label policy is configured (see Portal Walkthrough Section 6 and PowerShell Setup Section 6).
  - Document the gap, remediation action, and closure date.

---

## Test 3: Sensitivity Label Access Control — User Without Extract Rights

**Criterion:** Users without extract rights to the applied sensitivity label cannot access the agent.
**Expected Result:** Test User B (without extract rights) is blocked from accessing the test agent.
**Evidence Type:** Screenshot of access denied or error message when Test User B attempts agent interaction.

### Procedure

**Step 3.1 — Configure Test Agent with a Restricting Label**

1. Create or use a test agent with embedded files.
2. Confirm the agent's sensitivity label requires extract rights that Test User B does not possess (e.g., the label is scoped to a specific group or requires a specific IRM permission).
3. Record the sensitivity label name and the extract rights requirement.

**Step 3.2 — Test Access as Authorized User (Test User A)**

1. Log in as Test User A (with extract rights).
2. Navigate to the test agent in M365 Copilot.
3. Interact with the agent — ask a question that would be answered by the embedded file content.
4. Verify the agent responds with grounded content from the embedded files.
5. Screenshot the successful interaction.

**Step 3.3 — Test Access as Restricted User (Test User B)**

1. Log in as Test User B (without extract rights to the agent's sensitivity label).
2. Navigate to the same test agent in M365 Copilot.
3. Attempt to interact with the agent.
4. Verify the outcome:
   - Expected: Access denied, agent not visible, or agent interaction blocked.
   - Document the exact error message or UI behavior observed.
5. Screenshot the blocked interaction.

**Step 3.4 — Record Results**

| Metric | Value |
|---|---|
| Test agent name | ___ |
| Sensitivity label applied | ___ |
| Test User A (authorized) — access result | Granted / Denied |
| Test User B (restricted) — access result | Granted / **Denied** (expected) |

**Pass criteria:** Test User A can access and interact with the agent. Test User B is blocked.

**Fail action:** If Test User B can access the agent despite lacking extract rights, escalate to Microsoft support. Review sensitivity label configuration for the label applied to the container. Verify the label's protection settings include the expected usage rights restrictions. Document as an open finding with severity rating.

---

## Test 4: IB Bypass Confirmation and Documentation

**Criterion:** Confirmed that IB policies do NOT block embedded file content delivery; limitation documented as known, assessed, and mitigated risk.
**Expected Result:** Test User C (IB-separated from the content owner segment) CAN receive agent responses grounded in the embedded content — confirming the IB bypass. This is the expected, documented behavior.
**Evidence Type:** Screenshot of Test User C receiving grounded content + signed compliance documentation of known limitation.

!!! danger "This Test Confirms a Compliance Risk — It Is Not a Pass/Fail Test in the Traditional Sense"
    Passing this test means you have successfully confirmed that the IB bypass exists in your environment and that you have documented it correctly. If Test User C is unexpectedly blocked by IB (i.e., IB somehow does enforce on embedded containers), that would be an anomalous result requiring investigation — but do not assume IB is enforcing; verify with a second test and contact Microsoft support before relying on that behavior.

### Procedure

**Step 4.1 — Confirm IB Policy Configuration**

1. Verify that your tenant has IB policies configured that segment Test User C from the business line that owns the embedded file content.
2. Navigate to: **Microsoft Purview › Information Barriers › Policies** and confirm the relevant IB policy is active.
3. Record: IB policy name, segments involved, Test User C's segment assignment.

**Step 4.2 — Verify IB Enforcement on Normal SharePoint Content (Control Test)**

Before testing the bypass, confirm IB is working correctly on standard SharePoint content:

1. Place a test document in a standard SharePoint site accessible only to Segment A users.
2. Attempt to access that document as Test User C (Segment B, separated from Segment A by IB).
3. Verify Test User C cannot access the document — confirming IB enforcement works on standard SharePoint content.
4. Screenshot the access denied result.

This establishes that your IB configuration is correct and that the subsequent embedded file bypass is a platform limitation, not a configuration error.

**Step 4.3 — Test Embedded File Content Access as IB-Separated User**

1. Create or use a test agent with embedded files where the file content originates from Segment A (IB-restricted from Test User C in Segment B).
2. Share the agent with Test User C (or ensure Test User C's segment has agent access).
3. Log in as Test User C.
4. Navigate to the test agent.
5. Ask the agent a question that would be answered by the embedded file content from Segment A.
6. Observe and document the result:
   - If the agent responds with content from the embedded files: **IB bypass confirmed** — document as expected behavior.
   - If the agent is blocked or returns no grounded response: **Anomalous** — investigate and contact Microsoft support.
7. Screenshot the result.

**Step 4.4 — Document the Known Limitation**

Complete the following documentation for your examination file:

```
Control 4.9 — IB Bypass Confirmation Record

Date tested:      ___________________
Tested by:        ___________________
Reviewed by:      ___________________ (Compliance Officer)

Test environment:
  - IB policy name:           ___________________
  - Segment A (content owner): ___________________
  - Segment B (Test User C):  ___________________
  - Test agent name:          ___________________

Test results:
  - Standard SharePoint IB enforcement: CONFIRMED (Test User C blocked from Segment A SharePoint content)
  - Embedded file IB bypass:            CONFIRMED (Test User C received grounded response from Segment A content)

Platform limitation confirmation:
  Microsoft Purview Information Barriers are NOT supported on SharePoint Embedded containers
  used by M365 Copilot Agent Builder knowledge files. References:
    - https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-file-upload
    - https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-registry
    - https://learn.microsoft.com/en-us/sharepoint/dev/embedded/overview
  (Confirm current Microsoft documentation at audit time; the absence of IB enforcement on
   SharePoint Embedded containers is the platform behavior assessed in this control.)

Mitigation in effect:
  [ ] Zone 3 prohibition: No agents serving cross-IB-segment user populations are permitted to
      use embedded file knowledge sources.
  [ ] Zone 2 controls: IB assessment procedure is required before any file upload; no IB-restricted
      content is permitted in embedded files for Zone 2 agents.
  [ ] Compliance sign-off: Any exception to the above requires written sign-off from the
      Chief Compliance Officer.

Signed: ___________________ (Compliance Officer)   Date: ___________________
```

**Step 4.5 — Record Results**

| Metric | Value |
|---|---|
| Standard SharePoint IB enforcement confirmed | Yes / No |
| Embedded file IB bypass confirmed | Yes / No |
| Known limitation documentation complete | Yes / No |
| Mitigation controls verified in effect | Yes / No |
| Compliance officer sign-off obtained | Yes / No |

**Pass criteria:** All fields above are "Yes". The known limitation is documented with compliance officer sign-off. Mitigation controls (Zone 3 prohibition, Zone 2 IB assessment) are verified to be in effect.

---

## Test 5: Container Integrity — No Orphaned or Broken Containers

**Criterion:** No containers deleted outside of proper agent deletion workflow; no orphaned containers.
**Expected Result:** All containers in SharePoint Admin Center correspond to active agents; no containers show broken or orphaned status.
**Evidence Type:** Container reconciliation report; SharePoint audit log review.

### Procedure

**Step 5.1 — Run Container Reconciliation**

1. Export the container list from SharePoint Admin Center (Declarative Agent filter) — see Portal Walkthrough Section 3.
2. Export the agent list from M365 Admin Center (embedded files filter) — see Portal Walkthrough Section 1.
3. For each container, confirm a corresponding active agent exists using the container ID cross-reference.

**Step 5.2 — Check for Broken Agent References**

1. For each agent in the embedded files filter, verify the agent is still functional:
   - Open the agent.
   - Confirm the Data & tools tab shows the expected files.
   - If the tab shows no files or an error where files were previously present, the container may have been deleted.

**Step 5.3 — Review Audit Log for Unauthorized Deletions**

1. Navigate to: **Microsoft Purview › Audit**
2. Search for SharePoint container deletion events in the audit period.
3. For any deletion events found, determine:
   - Was the deletion triggered by the agent deletion workflow in M365 Admin Center? (Expected — acceptable)
   - Was the deletion a direct SharePoint admin action? (Unauthorized — requires investigation)

**Step 5.4 — Record Results**

| Metric | Value |
|---|---|
| Total containers in SharePoint Admin Center | ___ |
| Containers with matching active agent | ___ |
| Orphaned containers (no active agent match) | ___ |
| Containers with broken agent references | ___ |
| Unauthorized deletion events in audit log | ___ |

**Pass criteria:** Zero orphaned containers. Zero broken agent references. Zero unauthorized deletion events.

**Fail action:** For orphaned containers, review content and consult Compliance before taking any action. Do not delete without confirming no legal hold or retention obligation. For broken agent references, check the SharePoint recycle bin for the container — if within the 93-day window, restore it. See Troubleshooting playbook Section 3.

---

## Test 6: Agent Inventory (Control 3.1) Completeness

**Criterion:** Agent inventory (Control 3.1) includes embedded file metadata for all applicable agents.
**Expected Result:** Every agent in the M365 Admin Center embedded files filter has a complete inventory record with all required embedded file fields populated.
**Evidence Type:** Inventory completeness report.

### Procedure

**Step 6.1 — Pull Inventory Records for All Embedded File Agents**

1. From the agent inventory system (Control 3.1), extract all records where "Embedded Files = Y".
2. For each record, verify the following fields are populated:

| Field | Required | Notes |
|---|---|---|
| Agent Name | Yes | Must match M365 Admin Center name |
| Container ID | Yes | Must match Data & tools tab container ID |
| Embedded File Names | Yes | All files listed |
| Embedded File Sensitivity Labels | Yes | Label for each file; "Unlabeled" if no label (gap flag) |
| Zone | Yes | 1 / 2 / 3 |
| IB Assessment Status | Yes | Assessed — No Conflict / Assessed — IB-Exempt / Pending |
| IB Assessment Date | Yes | Must be within the last 12 months |
| Last Container Audit Date | Yes | Must be within the last 90 days (quarterly) |

**Step 6.2 — Identify Incomplete Records**

Flag any records with:
- Missing Container ID
- Missing or incomplete file list
- IB Assessment Status = "Pending" for agents in Zone 2 or Zone 3
- IB Assessment Date older than 12 months
- Last Container Audit Date older than 90 days

**Step 6.3 — Record Results**

| Metric | Value |
|---|---|
| Total embedded file agents in inventory | ___ |
| Records fully complete | ___ |
| Records with missing Container ID | ___ |
| Records with pending IB assessment (Zone 2/3) | ___ |
| Records with stale IB assessment (>12 months) | ___ |
| Records with stale container audit (>90 days) | ___ |

**Pass criteria:** 100% of records fully complete. Zero records with pending IB assessment for Zone 2/3 agents. Zero records with audit dates exceeding quarterly or annual thresholds.

---

## Test 7: Default Sensitivity Label Policy Verification

**Criterion:** Default sensitivity label policy configured and verified to apply to unlabeled uploaded files.
**Expected Result:** Uploading an unlabeled file to an agent automatically results in a baseline sensitivity label being applied to the container.
**Evidence Type:** Test upload screenshot showing label applied to container; Microsoft Purview label policy configuration screenshot.

### Procedure

**Step 7.1 — Verify Policy Configuration**

1. Navigate to: **Microsoft Purview › Information Protection › Label policies**
2. Identify the default label policy.
3. Confirm a default document label is configured (see Portal Walkthrough Section 6).
4. Screenshot the policy settings.

**Step 7.2 — Test Label Application on Unlabeled File Upload**

1. Create a test agent or use an isolated test agent.
2. Upload an unclassified test document (no sensitivity label applied to the file).
3. After upload, wait up to 24 hours (or at least 30 minutes) for label policy propagation.
4. Navigate to: **M365 Admin Center › Copilot › Agents › [Test Agent] › Overview tab**
5. Verify the Sensitivity label field shows the expected default label.
6. Screenshot the result.

**Step 7.3 — Record Results**

| Metric | Value |
|---|---|
| Default label policy configured | Yes / No |
| Default document label setting | ___ (label name) |
| Label applied to test unlabeled file upload | Yes / No |
| Label applied value | ___ |

**Pass criteria:** Default label policy is configured. Test unlabeled file upload results in the expected default label being applied to the container.

---

## Verification Test Summary Sheet

Use the following summary sheet for quarterly audit sign-off:

```
Control 4.9 — Quarterly Verification Summary
Quarter: ___________   Audit Date: ___________   Auditor: ___________

Test 1: Inventory Completeness          PASS / FAIL / PARTIAL   Notes: ___________________
Test 2: Sensitivity Label Presence      PASS / FAIL / PARTIAL   Notes: ___________________
Test 3: Label Access Control            PASS / FAIL / PARTIAL   Notes: ___________________
Test 4: IB Bypass Documentation         DOCUMENTED / NOT DOC'D  Signed by: _______________
Test 5: Container Integrity             PASS / FAIL / PARTIAL   Notes: ___________________
Test 6: Agent Inventory Completeness    PASS / FAIL / PARTIAL   Notes: ___________________
Test 7: Default Label Policy            PASS / FAIL / PARTIAL   Notes: ___________________

Overall Control Status:
[ ] EFFECTIVE — All tests passed or IB limitation properly documented
[ ] PARTIALLY EFFECTIVE — Open items noted above; remediation in progress
[ ] INEFFECTIVE — Critical failure requiring immediate escalation

Open items requiring remediation:
1. ___________________________________________  Target date: ___________
2. ___________________________________________  Target date: ___________
3. ___________________________________________  Target date: ___________

Compliance Officer sign-off: ___________________   Date: ___________

This report is prepared for examination readiness. Retain in compliance file per recordkeeping policy.
```

---
[Back to Control 4.9](../../../controls/pillar-4-sharepoint/4.9-embedded-file-content-governance.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
