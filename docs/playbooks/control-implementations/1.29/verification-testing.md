# Control 1.29 — Verification Testing: Global Secure Access Network Controls

**Playbook Type:** Verification Testing
**Control:** 1.29 — Global Secure Access: Network Controls for Copilot Studio Agents
**Audience:** Security Engineers, Quality Assurance, Internal Audit
**Estimated Duration:** 90–120 minutes for full test suite execution
**Prerequisites:** GSA forwarding enabled per Portal Walkthrough; all three filtering policies created and linked to baseline profile; access to a non-production Copilot Studio environment for testing

!!! warning "Preview Feature"
    This is a preview feature. Preview features aren't meant for production use and may have restricted functionality. Features may change before becoming generally available. Subject to the [Microsoft Azure Preview Supplemental Terms of Use](https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/). Conduct all verification tests in a **non-production** environment before applying and testing in production environments.

!!! warning "Use Non-Production Environments for Testing"
    All functional tests described in this playbook should be performed in a dedicated test or development Copilot Studio environment. Do not use production agents or production data when executing blocked-destination tests. Never use real malware, real C2 infrastructure, or real sensitive data in verification testing.

---

## Overview

This verification testing playbook provides a structured set of test procedures for confirming that Control 1.29 is correctly implemented and functioning. Tests are organized into five categories:

- **VT-01**: GSA Forwarding Active Confirmation
- **VT-02**: Web Content Filtering Validation
- **VT-03**: Threat Intelligence Filtering Validation
- **VT-04**: Network File Filtering Validation
- **VT-05**: Log Completeness and Agent Metadata Validation

Each test includes: objective, preconditions, test procedure, expected result, evidence capture, and pass/fail criteria.

!!! info "Internal Audit Use"
    This playbook is designed to produce verifiable, documentable evidence suitable for internal audit review, FINRA examination responses, and SOX ITGC testing. Each test includes an evidence capture step. Complete the evidence checklist at the end of this playbook and retain with your ITGC documentation.

---

## Test Environment Setup

Before executing any tests, confirm the following preconditions:

```
Test Environment Checklist
──────────────────────────
[ ] Test environment name: ___________________________
[ ] Test environment ID:   ___________________________
[ ] Zone classification for test environment: _______________
[ ] GSA forwarding enabled for this environment (verified in PPAC): YES / NO
[ ] Web content filtering policy linked to baseline profile: YES / NO
[ ] Threat intelligence filtering enabled (Block mode): YES / NO
[ ] Network file filtering policy linked to baseline profile: YES / NO
[ ] Test agent name and solution: ___________________________
[ ] Tester name and role: ___________________________
[ ] Test execution date: ___________________________
[ ] Test execution approved by: ___________________________
```

---

## VT-01: GSA Forwarding Active Confirmation

**Objective:** Confirm that agent-originated traffic from the test environment is being forwarded through Global Secure Access and is appearing in GSA traffic logs with agent-specific metadata.

**Risk if failing:** All other tests are inconclusive — if forwarding is not active, filtering policies cannot function and traffic is not being logged.

### VT-01-A: Verify forwarding toggle state in PPAC

**Procedure:**

1. Navigate to [https://admin.powerplatform.microsoft.com](https://admin.powerplatform.microsoft.com).
2. Select **Environments** > [test environment] > **Settings** > **Features**.
3. Confirm the **Global Secure Access** toggle is set to **On**.

**Expected result:** Toggle is in the ON/enabled position.

**Evidence capture:** Screenshot of the GSA toggle in the enabled state, showing the environment name and toggle state clearly in the same frame.

**Pass criteria:** Toggle confirmed ON.

### VT-01-B: Confirm agent traffic appears in GSA logs

**Procedure:**

1. In the test Copilot Studio environment, trigger a test agent that makes an outbound HTTP call to a known, benign, and approved external URL. Use a simple HTTP action node or a tool calling a known public REST API (e.g., a weather service, public API endpoint) that is on your approved allowlist.
2. Note the exact time of the trigger (UTC).
3. Wait 3–5 minutes.
4. Navigate to Entra admin center > **Global Secure Access** > **Monitor** > **Traffic logs**.
5. Filter logs to the time window starting 1 minute before and ending 10 minutes after the trigger time.
6. Filter by source environment or traffic type (agent) if filter controls are available.
7. Search for the destination FQDN you triggered the agent to connect to.

**Expected result:** A log entry appears for the destination FQDN with:
- Traffic type indicating agent/Copilot Studio origin
- Source environment identifier matching the test environment
- Action: Allow (since this is an approved destination)
- Timestamp within the expected window

**Evidence capture:** Screenshot of the matching log entry showing traffic type, source, destination, action, and timestamp fields.

**Pass criteria:** Log entry present within 10 minutes of the triggered request, with agent-specific metadata fields populated.

!!! note "Log Latency"
    GSA traffic logs may have a latency of 2–10 minutes from request time to log appearance. If no entry appears after 15 minutes, proceed to the [Troubleshooting](troubleshooting.md) playbook — VT-01-B failure is the most important issue to resolve before proceeding.

---

## VT-02: Web Content Filtering Validation

**Objective:** Confirm that the web content filtering policy correctly blocks agent requests to destinations in blocked categories and correctly allows requests to approved destinations.

**Prerequisite:** VT-01 passed — GSA forwarding confirmed active and logging.

### VT-02-A: Blocked category test

**Procedure:**

1. Identify a specific URL that definitively falls within one of your configured blocked categories (e.g., a well-known social media site if social media is a blocked category in your policy). Use a URL that is clearly in the blocked category but is not a real threat or illegal site — the goal is to confirm the category filter fires.
2. Create a test agent action that makes an HTTP GET request to the identified URL. This can be a simple HTTP node in the agent flow.
3. Trigger the test agent.
4. Observe the agent flow result — the HTTP request should fail with an error indicating the connection was refused or blocked.
5. Wait 3–5 minutes.
6. Navigate to GSA traffic logs and search for the blocked URL in the time window.

**Expected result:**
- The agent flow HTTP action returns an error (not a successful 200 response)
- GSA traffic logs show a log entry for the destination with action = **Block** and the web content filtering policy name referenced in the policy match field

**Evidence capture:**
- Screenshot of the agent flow showing the failed HTTP action (error response or blocked status)
- Screenshot of the GSA traffic log entry showing action = Block, destination FQDN, and policy name

**Pass criteria:** Both the agent flow failure AND the blocking log entry are present.

### VT-02-B: Allowlisted destination test

**Procedure:**

1. Identify a destination that is in a blocked category but has been explicitly added to the allowlist (exceptions list) in the web content filtering policy.
2. Create a test agent action that makes an HTTP GET request to the allowlisted destination.
3. Trigger the test agent.
4. Verify the agent flow HTTP action succeeds (200 response or expected response code).
5. Check GSA traffic logs for the log entry — action should be Allow.

**Expected result:** Agent flow succeeds; GSA log shows action = Allow.

**Evidence capture:** Screenshot of successful agent flow response; screenshot of GSA Allow log entry.

**Pass criteria:** Allowlisted destination is reachable by the agent; traffic is logged with Allow action.

### VT-02-C: URL-based explicit block test (if URL rules are configured)

**Procedure:**

1. If you have configured explicit URL-based block rules (not just category blocks), identify one of the explicitly blocked URLs.
2. Create a test agent HTTP action targeting the explicitly blocked URL.
3. Trigger, observe failure, and verify in logs as per VT-02-A steps.

**Expected result:** Agent flow fails; GSA log shows Block with the URL rule (or policy name) referenced.

**Pass criteria:** Explicit URL block rule is enforced.

---

## VT-03: Threat Intelligence Filtering Validation

**Objective:** Confirm that the threat intelligence filtering policy is active in Block mode and that known-malicious destinations are blocked before the agent can connect.

**Prerequisite:** VT-01 passed.

!!! warning "Test URL Selection"
    Do NOT use real malware domains, actual C2 infrastructure, or any URL that would make a genuine outbound connection to attacker infrastructure for this test. Use Microsoft-provided test URLs if available, or coordinate with your security vendor for an approved test domain that is in the threat intelligence feed but is a known test indicator. Check with your SOC or threat intelligence team for approved test methodology.

### VT-03-A: Threat intelligence blocking confirmation (using approved test indicator)

**Procedure:**

1. Obtain an approved test domain or URL that is known to be in Microsoft's threat intelligence feed as a test/demonstration indicator, or that is confirmed in your threat intel policy's block list. Coordinate with your SOC or use a vendor-provided test indicator.
2. Create a test agent HTTP action targeting the test threat indicator URL.
3. Trigger the test agent.
4. Observe the agent flow — the HTTP action should fail.
5. Wait 3–5 minutes and check GSA traffic logs.

**Expected result:**
- Agent flow HTTP action fails with a connection error
- GSA traffic logs show a log entry with action = Block and the threat intelligence policy referenced as the matching policy

**Evidence capture:**
- Screenshot of agent flow failure
- Screenshot of GSA log entry showing Block + threat intelligence policy reference

**Pass criteria:** Threat intelligence filter actively blocks the test indicator and logs the event.

### VT-03-B: Threat intelligence policy mode verification

**Procedure:**

1. Navigate to Entra admin center > **Global Secure Access** > **Secure** > **Threat intelligence**.
2. Verify the policy action is set to **Block** (not Audit-only).
3. Verify the policy state is **Enabled**.

**Expected result:** Policy shows Enabled + Block action.

**Evidence capture:** Screenshot of threat intelligence policy settings showing enabled state and Block action.

**Pass criteria:** Policy is in active Block mode, not Audit mode.

!!! warning "Audit-Only Mode is Insufficient for Zone 2/3"
    If threat intelligence filtering is set to Audit-only, threats are logged but not blocked. This is insufficient for Zone 2 and Zone 3 environments. If you find audit-only mode, treat this as a failing test and raise a remediation finding. Audit mode may only be acceptable during initial deployment in Zone 1 environments.

---

## VT-04: Network File Filtering Validation

**Objective:** Confirm that the network file filtering policy correctly blocks unauthorized file uploads and file downloads per the configured rules.

**Prerequisite:** VT-01 passed.

### VT-04-A: Blocked file upload test

**Procedure:**

1. Identify a file upload destination that is in your blocked list (e.g., a consumer file sharing service that is not on the organizational approved destinations list).
2. Create a test agent action that attempts to upload a small, benign test file (e.g., a text file containing only the word "TEST") to the blocked destination via HTTP POST.
3. Trigger the test agent.
4. Observe the agent flow — the upload action should fail.
5. Check GSA traffic logs for the event.

**Expected result:**
- Agent flow upload action fails
- GSA log shows Block with the network file filtering policy referenced

**Evidence capture:** Screenshot of upload failure in agent flow; screenshot of GSA Block log entry.

**Pass criteria:** File upload to blocked destination is blocked and logged.

### VT-04-B: Blocked file type download test

**Procedure:**

1. Identify a URL that would serve a file type blocked by your network file filtering policy (e.g., an executable file type if `.exe` downloads are blocked). Use a benign, organization-controlled URL serving a file of the blocked type — do not download actual malware.
2. Create a test agent HTTP action that performs a GET request to the file URL.
3. Trigger the test agent.
4. Observe the agent flow — the download should be blocked.
5. Check GSA traffic logs.

**Expected result:**
- Agent flow fails to retrieve the file
- GSA log shows Block with file filtering policy referenced

**Evidence capture:** Screenshot of download failure; screenshot of GSA Block log entry.

**Pass criteria:** Blocked file type download is prevented and logged.

### VT-04-C: Approved file transfer test

**Procedure:**

1. Identify an approved file transfer destination and file type that should be permitted by your network file filtering policy.
2. Create a test agent action performing the approved file transfer.
3. Trigger the test agent and confirm the transfer succeeds.
4. Check GSA traffic logs — action should be Allow.

**Expected result:** Approved file transfer succeeds; GSA log shows Allow.

**Pass criteria:** Permitted file transfers are not incorrectly blocked.

---

## VT-05: Log Completeness and Agent Metadata Validation

**Objective:** Confirm that GSA traffic logs for agent traffic contain all required metadata fields, that logs are queryable for the required retention period, and that log quality is sufficient for examination evidence purposes.

### VT-05-A: Agent metadata field completeness

**Procedure:**

1. Using traffic logs captured during VT-01 through VT-04, examine 5 representative log entries (mix of Allow and Block events).
2. For each log entry, verify the following fields are populated:

| Field | Required | Acceptable Null? |
|---|---|---|
| Timestamp (UTC) | Yes | No |
| Traffic type / source type | Yes | No — must identify traffic as agent-originated |
| Source environment identifier | Yes | No |
| Destination FQDN or IP | Yes | No |
| Action (Allow / Block) | Yes | No |
| Policy name (for blocked events) | Yes for blocked | No for blocked events |
| Transaction ID | Recommended | Yes — but note absence |
| Agent ID | Recommended | Yes during preview — note if absent |
| Protocol | Recommended | Yes |

**Expected result:** All required fields are populated in examined log entries. Recommended fields populated where available.

**Evidence capture:** Screenshot of representative log entries with field values visible. Annotate any missing fields.

**Pass criteria:** All required fields populated in all examined entries. Missing recommended fields documented as known gaps with preview limitation note.

### VT-05-B: Log retention and queryability

**Procedure:**

1. Determine your organization's required log retention period for GSA traffic logs (minimum: per FINRA Rule 4511 and SEC 17a-4 schedules — typically 3–6 years for records that may be relevant to examinations).
2. In Entra admin center > GSA Traffic logs, attempt to query logs from the earliest available date.
3. Note the oldest log date available in the default GSA log retention window.
4. If the default retention is insufficient for regulatory requirements, confirm that logs are being exported to a log analytics workspace / Microsoft Sentinel (per Control 3.9) with appropriate retention configuration.

**Expected result:** Either (a) native GSA log retention meets regulatory retention requirement, OR (b) logs are exported to Sentinel/Log Analytics with confirmed retention period meeting regulatory requirement.

**Evidence capture:** Screenshot of oldest available log date in GSA console; screenshot of Sentinel log export configuration showing retention policy (if applicable).

**Pass criteria:** Total log retention meets organizational regulatory retention requirement. Document the retention path (native GSA or Sentinel export) and the configured retention period.

!!! warning "Default GSA Log Retention May Be Insufficient"
    Microsoft's default GSA traffic log retention window may be shorter than FINRA/SEC regulatory retention requirements (which can extend to 3–6 years depending on record type). Ensure logs are exported to Azure Log Analytics / Microsoft Sentinel with a retention period configured to meet your regulatory obligations. See Control 3.9 for Sentinel integration configuration.

### VT-05-C: Blocked event discoverability test

**Procedure:**

1. Using the block events generated during VT-02 through VT-04, verify that you can:
    - Search for all blocked events in a given time period
    - Filter blocked events by destination FQDN
    - Filter blocked events by policy name
    - Export blocked events to CSV for offline analysis
2. Document which filter and export capabilities are available in the current UI.

**Expected result:** Blocked events are discoverable and exportable through the GSA traffic log interface.

**Pass criteria:** Block events can be queried, filtered, and exported. Document any gaps in search/filter capability as known limitations.

---

## Test Results Summary and Sign-Off

Complete this summary after all tests are executed.

```
Control 1.29 — Verification Test Results Summary
=================================================
Test Environment    : ___________________________
Test Date           : ___________________________
Tester Name         : ___________________________
Tester Role         : ___________________________
Review / Approver   : ___________________________

Test Results:
  VT-01-A  GSA forwarding toggle confirmed ON        : PASS / FAIL / N/A
  VT-01-B  Agent traffic appears in GSA logs         : PASS / FAIL / N/A
  VT-02-A  Blocked category test                     : PASS / FAIL / N/A
  VT-02-B  Allowlisted destination test              : PASS / FAIL / N/A
  VT-02-C  Explicit URL block test                   : PASS / FAIL / N/A
  VT-03-A  Threat intelligence blocking (test indic.): PASS / FAIL / N/A
  VT-03-B  Threat intelligence Block mode confirmed  : PASS / FAIL / N/A
  VT-04-A  Blocked file upload test                  : PASS / FAIL / N/A
  VT-04-B  Blocked file type download test           : PASS / FAIL / N/A
  VT-04-C  Approved file transfer test               : PASS / FAIL / N/A
  VT-05-A  Agent metadata field completeness         : PASS / FAIL / N/A
  VT-05-B  Log retention meets regulatory requirement: PASS / FAIL / N/A
  VT-05-C  Blocked event discoverability             : PASS / FAIL / N/A

Overall Result      : PASS / FAIL / CONDITIONAL PASS

Failures and remediation items:
  [List any FAIL items and planned remediation action with owner and date]

Known limitations accepted (Preview):
  [List any gaps accepted as preview limitations, with risk acceptance sign-off]

Evidence package location:
  [Path or reference to evidence screenshots and exports]

Sign-off:
  Tester signature / approval:  ___________________________  Date: ____________
  Security approver signature:  ___________________________  Date: ____________
```

---

## Evidence Checklist for FINRA/SEC Examination Package

| Evidence Item | Test Source | Status |
|---|---|---|
| Screenshot: GSA forwarding toggle ON (PPAC) | VT-01-A | |
| Screenshot: GSA traffic log entry showing agent metadata | VT-01-B | |
| Screenshot: GSA log Block entry — web content filtering | VT-02-A | |
| Screenshot: Web content filtering policy configuration | VT-02-A | |
| Screenshot: Threat intelligence policy — Enabled + Block mode | VT-03-B | |
| Screenshot: GSA log Block entry — threat intelligence | VT-03-A | |
| Screenshot: Network file filtering policy configuration | VT-04-A / VT-04-B | |
| Screenshot: GSA log Block entry — file filtering | VT-04-A / VT-04-B | |
| Screenshot: GSA baseline profile showing all three linked policies | Manual capture | |
| Log export: Sample agent traffic log entries (CSV) | VT-05-A | |
| Documentation: Log retention configuration | VT-05-B | |
| Completed test results summary with approver signature | This playbook | |

---

[Back to Control 1.29](../../../controls/pillar-1-security/1.29-global-secure-access-network-controls.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

*Updated: April 2026 | Version: v1.3*
