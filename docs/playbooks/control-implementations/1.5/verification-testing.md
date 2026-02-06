# Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels - Verification & Testing

> This playbook provides verification and testing guidance for [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md).

---

## Verification Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Purview > DLP > Policies | Policies listed |
| 2 | Verify AI locations selected | Copilot/Copilot Studio included |
| 3 | Confirm SIT readiness (Control 1.13) | SITs exist and match sanitized test data |
| 4 | Create sanitized test content + apply labels | Files/messages prepared; labels applied |
| 5 | Run AI test prompts and agent scenarios | Blocked/warned/audited per tier |
| 6 | (Optional) Run Endpoint DLP tests | Endpoint actions enforce as configured |
| 7 | Check DSPM for AI > Policies | AI-related DLP policies visible |
| 8 | Check audit logs / incident reports | DLP events and reports captured |

---

## Test Cases (Copilot/Agent; U.S.-Only)

Use non-production, sanitized data. Do not use real customer data.

| Test ID | Scenario | Input | Expected |
|---------|----------|-------|----------|
| AI-01 | Prompt includes SSN | Prompt text includes SSN-formatted value | Tier 2: warning + log; Tier 3: block + incident |
| AI-02 | Prompt includes ABA routing | Prompt includes routing-formatted value | Same as AI-01 |
| AI-03 | Retrieval from labeled content | Agent grounds on Highly Confidential file | Block per label rule; event logged |
| AI-04 | Retrieval from Confidential content | Agent grounds on Confidential content | Warn or allow-with-audit; event logged |
| AI-05 | Attempted sensitive output | Agent summarizes doc with bank account numbers | Output blocked/redacted; event logged |

---

## Test Cases (Virtual Governance Connectors)

Verify that DLP policies enforce virtual governance connector classification rules. Use a non-production environment for testing.

### Zone 3 Virtual Connector Test Cases (Required)

| Test ID | Scenario | Action | Expected Result |
|---------|----------|--------|-----------------|
| VC-01 | Agent creation with blocked connector | Create Copilot Studio agent that uses HTTP Webhook connector (blocked in Zone 3) | Agent creation blocked with DLP policy error; event logged in audit log |
| VC-02 | HTTP call to non-allowlisted endpoint | Configure agent skill to call external API not in HTTP endpoint allow list (e.g., `https://api.external-service.com`) | Agent skill execution fails with DLP violation; error message displays to user; event logged in Purview audit log |
| VC-03 | Verify all 11 connectors classified | Navigate to PPAC > DLP policy > Connectors tab | All 11 virtual governance connectors appear with correct Zone 3 classification (see table below) |
| VC-04 | Knowledge Source connector with approved SharePoint | Create agent using Copilot Studio Knowledge connector pointing to approved SharePoint site (after Control 1.3 implemented) | Access allowed; agent successfully indexes knowledge source; no DLP error |
| VC-05 | Channel connector enforcement | Attempt to publish agent to Custom Website Channel (blocked in Zone 3) | Publishing blocked with DLP error; user receives notification "This connector is blocked by DLP policy" |
| VC-06 | AI Builder GPT connector usage | Create agent using AI Builder GPT connector for text generation | If Business-classified: allowed; agent creates successfully and generates text |
| VC-07 | Zone 3 connector classifications match recommended settings | Export DLP policy configuration via PowerShell (see PowerShell Setup playbook) | All 11 connectors match Zone 3 recommended classifications from Control 1.5 |
| VC-08 | HTTP endpoint filtering blocks non-allowlisted external APIs | Create agent skill that calls `https://api.twitter.com/2/tweets` (social media API, not in allow list) | Agent skill fails with HTTP endpoint filtering error; event logged with blocked URL |
| VC-09 | DLP audit log captures connector classification violations | Review Purview Audit Log for past 7 days; search for DLP events related to virtual connectors | Audit log entries show DLP violations with connector name, user, timestamp, and policy name |

**Expected Zone 3 Classifications (for VC-03 verification):**

| Connector | Expected Classification | Verification Method |
|-----------|------------------------|-------------------|
| AI Builder (GPT) | Business | Visible in Business group in PPAC |
| AI Builder (Document Processing) | Business | Visible in Business group in PPAC |
| Copilot Studio Topics | Business | Visible in Business group in PPAC |
| Copilot Studio Skills | Business | Visible in Business group in PPAC |
| Copilot Studio Knowledge | Business | Visible in Business group in PPAC |
| HTTP with Microsoft Entra ID | Business (with endpoint filtering) | Visible in Business group; endpoint filtering badge present |
| HTTP Webhook | **Blocked** | Visible in Blocked group in PPAC |
| Direct Line | Business | Visible in Business group in PPAC |
| Microsoft Teams Channel | Business | Visible in Business group in PPAC |
| SharePoint Channel | **Blocked** | Visible in Blocked group in PPAC |
| Custom Website Channel | **Blocked** | Visible in Blocked group in PPAC |

### Zone 1-2 Virtual Connector Test Cases (Optional)

| Test ID | Scenario | Action | Expected Result |
|---------|----------|--------|-----------------|
| VC-10 | Zone 1 HTTP Webhook usage | Create agent with HTTP Webhook connector (Non-Business or Blocked in Zone 1) | If Non-Business: allowed but cannot mix with Business connectors; If Blocked: creation fails |
| VC-11 | Zone 2 Custom Website publishing | Attempt to publish agent to Custom Website Channel (Blocked in Zone 2) | Publishing blocked with DLP error |
| VC-12 | Zone 1 HTTP endpoint block list enforcement | Create agent skill calling blocked social media API (e.g., `https://api.twitter.com/*`) | Agent skill fails with HTTP endpoint filtering error |

### HTTP Endpoint Filtering Test Cases (Zone 3 Required)

!!! warning "Zone 3 Requirement"
    HTTP endpoint filtering test cases (VC-08, VC-13, VC-14, VC-15) are mandatory for Zone 3 environments. Failure to configure endpoint filtering creates data exfiltration risk.

| Test ID | Scenario | Action | Expected Result |
|---------|----------|--------|-----------------|
| VC-13 | Allow list permits internal API | Create agent skill calling internal API in allow list (e.g., `https://api.internal.yourbank.com/customer`) | Agent skill executes successfully; API call completes; response returned to agent |
| VC-14 | Allow list permits regulatory data source | Create agent skill calling SEC EDGAR API `https://api.sec.gov/submissions/` (in allow list) | Agent skill executes successfully; regulatory data retrieved |
| VC-15 | Allow list blocks unapproved external API | Create agent skill calling unapproved market data API `https://api.unknown-vendor.com/data` (not in allow list) | Agent skill fails with HTTP endpoint filtering error; no API call made |
| VC-16 | HTTP endpoint filtering audit log | Review Purview Audit Log for HTTP endpoint filtering events | Audit log shows blocked URL, user, agent name, timestamp |

### Evidence Collection

For audit readiness, collect and retain the following evidence:

- [ ] **Screenshot:** PPAC DLP policy showing all 11 virtual governance connectors with zone-appropriate classifications
- [ ] **Screenshot:** HTTP endpoint filtering configuration (allow list patterns) for HTTP with Microsoft Entra ID connector
- [ ] **PowerShell Export:** CSV file of virtual connector classifications (from PowerShell Setup playbook)
- [ ] **Audit Log:** Purview Audit Log query results showing DLP enforcement events for virtual connectors (past 30 days)
- [ ] **Test Results:** Test execution log with test ID, timestamp, tester account, expected vs actual outcome, and screenshots of errors
- [ ] **Change Record:** IT change control ticket documenting DLP policy configuration and dual approval (Zone 3 requirement per Control 2.1)

---

## Test Cases (Endpoint DLP; Optional)

Run only if Devices/Endpoint DLP is in scope.

| Test ID | Scenario | Action | Expected |
|---------|----------|--------|----------|
| EP-01 | Copy/paste exfiltration | Copy SSN text, paste into AI prompt in browser | Block or warn; event logged |
| EP-02 | File exfiltration | Upload Highly Confidential file to AI web experience | Block or warn; event logged |
| EP-03 | Removable media | Copy file with bank account numbers to USB | Block or warn; event logged |

---

## Evidence to Retain (Audit-Ready)

- [ ] DLP policy export (policy + rules) and change record
- [ ] Screenshot evidence showing AI locations selected and rule conditions
- [ ] SIT validation evidence per Control 1.13
- [ ] Label taxonomy decision + label publication configuration
- [ ] Test execution log: test ID, timestamp, account used, expected vs actual
- [ ] Incident report samples and notification configuration
- [ ] Unified audit log evidence for representative DLP events
- [ ] DSPM for AI policy visibility and oversharing assessment outputs

---

## Confirmation Checklist

- [ ] DLP policies created with AI locations (Copilot, Copilot Studio)
- [ ] All 11 virtual governance connectors classified in Power Platform DLP policy
- [ ] HTTP endpoint filtering configured and tested (Zone 3 requirement)
- [ ] Virtual connector test cases executed with expected results (VC-01 through VC-06)
- [ ] Sensitivity labels created and published
- [ ] Label-based DLP rules configured
- [ ] SITs validated per Control 1.13
- [ ] Standard AI test cases executed (AI-01 through AI-05)
- [ ] Audit logs capture DLP events including virtual connector enforcement
- [ ] DSPM integration verified (if applicable)
- [ ] Evidence artifacts collected and stored

---

*Updated: January 2026 | Version: v1.2*
