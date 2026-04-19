# Verification & Testing: Control 2.23 - User Consent and AI Disclosure Enforcement

**Last Updated:** April 2026
**Estimated Time:** 30–45 minutes (full pass)
**Re-test cadence:** After each tenant configuration change, after each Copilot Studio agent publish, and at minimum quarterly for Zone 3.

## Test Scope

This playbook verifies that the configuration produced by the Portal Walkthrough and PowerShell Setup playbooks delivers the user-facing, data-layer, and audit-trail outcomes required by Control 2.23. Each test maps to one or more verification criteria from the control document.

| # | Test | Verifies | Required for |
|---|---|---|---|
| 1 | Tenant disclaimer appears in supported surfaces | Tenant policy is **On**, font correct, custom URL surfaced | Zone 1+ |
| 2 | Tenant disclaimer absent from unsupported surfaces | Scope expectation is correct | All zones |
| 3 | Agent-level disclosure renders | Greeting / Conversation Start displays zone-appropriate text | Zone 1+ |
| 4 | Consent acknowledgment branch (Yes path) | Conversation continues; Dataverse row created | Zone 3 |
| 5 | Consent acknowledgment branch (No path) | Conversation ends with contact path; no agent functionality reached | Zone 3 |
| 6 | Dataverse record completeness and immutability posture | All required columns; restricted write path | Zone 3 |
| 7 | Re-acknowledgment after 90 days | `Check-AIConsent` re-prompts when stale | Zone 3 |
| 8 | Cross-channel consistency | Disclosure renders in Teams desktop, web, mobile | Zone 2+ |
| 9 | Custom URL accessibility (internal + guest) | URL resolves without auth errors for both populations | Zone 2+ |
| 10 | Audit log evidence | Configuration changes and consent flow visible in Purview | Zone 3 |

---

## Pre-test Setup

- [ ] Two test users provisioned: `pilot-int@<tenant>` (member) and `pilot-ext@<partnerdomain>` (guest)
- [ ] Test users have the appropriate Copilot license assigned
- [ ] One Zone 3 test agent published with the Conversation Start topic from Portal Walkthrough Step 6
- [ ] `fsi_aiconsent` table deployed and table-level auditing enabled
- [ ] Output directory exists for evidence: local path under `maintainers-local/tenant-evidence/2.23/`
- [ ] Screen-capture tool ready (screenshots are local-only — never committed to the repo)

---

## Test 1 — Tenant disclaimer appears in supported surfaces

**Steps**
1. Sign in as the test user in an InPrivate / Incognito browser.
2. Open Copilot Chat (`https://m365.cloud.microsoft/chat`).
3. Open Word for the web and a desktop Outlook session.
4. In each surface, look for the disclaimer string under the Copilot input.

**Expected**
- Disclaimer is present in Copilot Chat, Word, Excel, PowerPoint, Outlook, OneNote.
- Font matches the configured style (Standard or Bold).
- The info icon's tooltip exposes the configured custom URL.

**Pass if** all six supported surfaces display the disclaimer with the correct font and tooltip.

---

## Test 2 — Tenant disclaimer absent from unsupported surfaces

**Steps**
1. Open SharePoint, OneDrive, Whiteboard, and Forms as the same test user.
2. Trigger any Copilot affordance available in those surfaces.

**Expected**
- No tenant Copilot AI Disclaimer string appears (the toggle is **out of scope** for these surfaces per Microsoft Learn).

**Pass if** absence is confirmed for all four. Capture this in evidence to pre-empt audit questions about coverage gaps.

---

## Test 3 — Agent-level disclosure renders

**Steps**
1. Start a new conversation with the Zone 3 test agent in its default channel (typically Microsoft Teams).
2. Capture the first message rendered by the agent.

**Expected (Zone 3)**
- Disclosure text matches the approved Zone 3 template, including: AI identification, "responses must be reviewed" statement, retention period, supervisory-review notice, privacy contact, compliance contact, full policy URL, and explicit acknowledgment question.
- `DisclosureVersion` token resolves to the current approved version.

**Pass if** the rendered text exactly matches the approved Zone 3 disclosure for the current `DisclosureVersion`.

---

## Test 4 — Consent acknowledgment (Yes path)

**Steps**
1. Continue from Test 3.
2. Respond `Yes` to the consent question.
3. Note the time of acknowledgment.
4. Run `Get-ConsentRecords.ps1 -EnvironmentUrl <env> -DaysBack 1`.

**Expected**
- Conversation proceeds; a normal agent turn follows.
- A new row exists in `fsi_aiconsents` with: matching `fsi_userupn`, `fsi_useraadid`, `fsi_agentid`, `fsi_consenttimestamp` within ±2 minutes of the acknowledgment, current `fsi_disclosureversion`, `fsi_acknowledgmentstatus = true`, and a `fsi_sourcechannel` value.

**Pass if** all eight column values are populated correctly.

---

## Test 5 — Consent acknowledgment (No path)

**Steps**
1. Start a fresh conversation as a different test user.
2. Respond `No` to the consent question.

**Expected**
- Agent responds with the configured contact-path message.
- Conversation ends immediately (no further user input is accepted into the agent's normal flow).
- No new row appears in `fsi_aiconsents` for that user/agent (the flow only logs accepted consent). Optional: design the flow to also log declines with `fsi_acknowledgmentstatus = false` — verify behavior matches design.

**Pass if** the conversation terminates and Dataverse state matches the documented design.

---

## Test 6 — Dataverse record completeness and immutability posture

**Steps**
1. As a non-service-principal user (e.g., a Maker), attempt to create a row directly in `fsi_aiconsents` via Power Apps or the Web API.
2. As the same user, attempt to update or delete an existing row.

**Expected**
- All three operations (create, update, delete) are rejected as **Insufficient privileges**.
- The Dataverse table audit log captured your attempts.

**Pass if** the restricted security role is correctly preventing direct writes and updates from anyone other than the consent-logging service principal.

> **Hedged-language note.** Native Dataverse does not provide cryptographic immutability. The combination of (a) restricted write permissions, (b) table-level auditing, and (c) periodic export to a WORM store under Control 2.13 is what supports — not guarantees — record-keeping obligations under SEC 17a-4(f).

---

## Test 7 — Re-acknowledgment after 90 days

**Steps**
1. With Environment Admin privileges, manually backdate a known consent record's `fsi_consenttimestamp` to 91 days ago.
2. Sign in as that user and start a new conversation with the Zone 3 agent.

**Expected**
- The `Check-AIConsent` flow returns `consentValid = No`.
- The agent re-displays the disclosure and the consent question.
- After accepting, a **new** row is added (the backdated row is left intact for the audit trail).

**Pass if** re-prompt occurs and a new row is added without modifying the historical row.

---

## Test 8 — Cross-channel consistency

**Steps**
1. With the same test user, open the Zone 3 agent in: Microsoft Teams desktop, Microsoft Teams web, Microsoft Teams mobile (iOS or Android), and any custom web embed.
2. Inspect the first agent message in each channel.

**Expected**
- Disclosure text is identical across channels.
- Consent question accepts the same `Yes` / `No` responses.
- `fsi_sourcechannel` is populated correctly per channel (Teams / Web / Mobile).

**Pass if** the disclosure text and consent flow are identical across all channels and the source channel is captured correctly.

---

## Test 9 — Custom URL accessibility (internal + guest)

**Steps**
1. Internal user: click the tenant disclaimer info icon → tooltip URL.
2. Guest user (off corporate network): repeat.
3. Internal and guest: click the AI policy link inside the agent disclosure.

**Expected**
- Both populations reach the same authoritative AI policy page.
- No "access denied" or unexpected sign-in prompts for the guest user (a normal guest sign-in is acceptable).
- The page shows a `Last Updated` date that matches the current `DisclosureVersion`.

**Pass if** both populations reach the policy page and the version is consistent.

---

## Test 10 — Audit log evidence

**Steps**
1. Make a benign tenant change (toggle the disclaimer off and back on, or change the custom URL and revert).
2. Wait 60 minutes for unified audit log indexing.
3. Run `Search-DisclosureAuditEvidence.ps1 -StartDate (Get-Date).AddDays(-1)`.

**Expected**
- The exported CSV contains entries for the configuration change with the admin's UPN, ClientIP, and timestamp.
- CSV contains entries for the consent-flow Power Automate runs (visible as Power Automate / Dataverse operations).

**Pass if** both categories of events are present. If not, investigate per Troubleshooting Issue 5.

---

## Evidence Bundle

For each test, capture and store under the local tenant-evidence path:

```
maintainers-local/tenant-evidence/2.23/
    portal/        screenshots, .png
    powershell/    CSV/JSON outputs and .sha256 sidecars
    audit/         Search-UnifiedAuditLog exports
    consent/       Get-ConsentRecords exports
    summary.md     test-by-test pass/fail with timestamps and evidence filenames
```

Naming convention: `2.23-test{NN}-{short-description}-YYYYMMDD-HHMMSS.{ext}`.

> Screenshots and tenant-specific evidence are **never** committed to this repository. They live only in the gitignored maintainers-local tree, with cryptographic hashes for integrity.

---

## Compliance Validation Checklist

- [ ] Test 1 — Tenant disclaimer present on all supported surfaces
- [ ] Test 2 — Tenant disclaimer absent on unsupported surfaces (documented)
- [ ] Test 3 — Agent disclosure matches approved Zone 3 template
- [ ] Test 4 — Yes path: Dataverse row created with all required columns
- [ ] Test 5 — No path: conversation ends with contact-path message
- [ ] Test 6 — Restricted write path enforced; auditing captures attempts
- [ ] Test 7 — 90-day re-acknowledgment triggers; historical row preserved
- [ ] Test 8 — Cross-channel parity confirmed
- [ ] Test 9 — Custom URL accessible to internal and guest users
- [ ] Test 10 — Purview audit evidence retrievable for both config and consent events
- [ ] Evidence bundle assembled with SHA-256 sidecars and stored locally
- [ ] Test summary reviewed and signed off by AI Governance Lead and Compliance Officer

---

[Back to Control 2.23](../../../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
