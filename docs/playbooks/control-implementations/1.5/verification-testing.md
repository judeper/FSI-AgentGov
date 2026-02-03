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

| Test ID | Scenario | Action | Expected Result |
|---------|----------|--------|-----------------|
| VC-01 | Agent creation with blocked connector | Create Copilot Studio agent that uses HTTP Webhook connector (if blocked) | Agent creation blocked with DLP policy error; event logged |
| VC-02 | HTTP call to non-allowlisted endpoint | Configure agent skill to call external API not in HTTP endpoint allow list | Agent skill execution fails with DLP violation; event logged in audit log |
| VC-03 | Verify all 11 connectors classified | Navigate to PPAC > DLP policy > Connectors tab | All 11 virtual governance connectors appear with correct Business/Non-Business/Blocked classification |
| VC-04 | Knowledge Source connector with approved SharePoint | Create agent using Copilot Studio Knowledge connector pointing to approved SharePoint site | Access allowed; agent successfully indexes knowledge source |
| VC-05 | Channel connector enforcement | Attempt to publish agent to Custom Website Channel (if blocked) | Publishing blocked with DLP error; user receives notification |
| VC-06 | AI Builder GPT connector usage | Create agent using AI Builder GPT connector for text generation | If Business-classified: allowed; if Blocked: creation fails with DLP error |

**Evidence Collection:**

- Screenshot of PPAC DLP policy showing all 11 virtual governance connectors with classifications
- Screenshot of HTTP endpoint filtering configuration (allow list or block list)
- Audit log entries showing DLP enforcement events for virtual connectors
- Test execution results with timestamps and actual vs expected outcomes

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
