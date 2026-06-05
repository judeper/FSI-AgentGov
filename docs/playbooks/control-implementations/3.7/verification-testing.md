# Control 3.7: PPAC Security Posture Assessment — Verification & Testing

> Verification procedures and test cases for [Control 3.7](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md). Audience: M365 administrators producing audit evidence for FINRA / SEC / SOX / GLBA / OCC examinations.

---

## Verification Strategy

Verification for Control 3.7 has three layers. Auditors typically expect evidence at all three:

| Layer | What it proves | Frequency |
|-------|----------------|-----------|
| **Layer 1 — Tooling enabled** | The Security area and Actions page are accessible and populated; tenant-level analytics is on | Once per quarter |
| **Layer 2 — Recommendations addressed** | High-severity recommendations are remediated, snoozed with reason, or dismissed with documented justification | Per zone cadence |
| **Layer 3 — Configuration hardening** | Settings invisible to PPAC recommendations (Privacy + Security per-environment, agent settings) are reviewed and not drifted | Per zone cadence |

---

## Layer 1 — Tooling Verification

### V1-01 — Tenant-level analytics enabled

1. Sign in to PPAC as Power Platform Admin.
2. Navigate to **Security > Overview**.
3. **Pass:** Security score displays a percentage and qualitative label.
4. **Fail (deferrable):** Page shows "Calculating security score" — confirm tenant-level analytics is enabled and re-test in 24 hours.
5. **Fail (action required):** Page shows an error or empty state after 24 hours — see [Troubleshooting](troubleshooting.md).
6. **Evidence:** Screenshot showing score, label, and timestamp.

### V1-02 — Security navigation accessible

1. In PPAC, expand **Security**.
2. Verify all four pages are visible and load: **Overview**, **Data protection and privacy**, **Identity and access management**, **Compliance**.
3. **Pass:** All four pages load without permission errors.
4. **Evidence:** Screenshot of the expanded navigation.

### V1-03 — Actions page accessible

1. Navigate to **Actions** (formerly Power Platform Advisor).
2. Verify **Recommendations**, **Snoozed recommendations**, **Dismissed recommendations**, and **Action history** tabs are present.
3. **Pass:** All tabs render; Recommendations tab shows at least one item or a documented "no recommendations" state.
4. **Evidence:** Screenshot of the Actions page.

---

## Layer 2 — Recommendation Remediation Verification

### V2-01 — High-severity recommendations within SLA

1. Open **Actions > Recommendations**, filter Severity = High.
2. For each item record: title, severity, refresh frequency, first-seen date, current status.
3. Compare first-seen dates against zone-aligned SLA:
    - Zone 3: ≤ 7 days to remediation, snooze, or documented dismissal
    - Zone 2: ≤ 14 days
    - Zone 1: ≤ 30 days
4. **Pass:** All High-severity items either Completed, currently being remediated within SLA, snoozed with reason, or dismissed with justification.
5. **Evidence:** Export of recommendations list (CSV or screenshot) plus the dismissed/snoozed log.

### V2-02 — Dismissed recommendations have documented justification

1. Open **Actions > Dismissed recommendations**.
2. For each dismissed item confirm an entry in the **Dismissed recommendations log** containing:
    - Recommendation title and severity
    - Business justification (compensating control or non-applicability rationale)
    - Approver (named individual; FINRA 3110 expects supervisory sign-off)
    - Review-by date (recommend ≤ 12 months)
3. **Pass:** 100% of dismissed items have a complete log entry.
4. **Fail:** Any dismissed item missing justification or approver — re-activate the recommendation or complete the log entry.
5. **Evidence:** Dismissed recommendations log (Excel/CSV or governance system export).

### V2-03 — Snoozed recommendations are within snooze window

1. Open **Actions > Snoozed recommendations**.
2. For each snoozed item verify the snooze expiry date is in the future and ≤ 60 days from snooze creation (Microsoft caps snooze at two months).
3. Confirm an entry in the **Snoozed recommendations log** with reason and unsnooze plan.
4. **Pass:** All snoozed items within window with logged reason.
5. **Evidence:** Snoozed log plus screenshot.

### V2-04 — Action history aligns with remediation tickets

1. Open **Actions > Action history**.
2. For a sample of 5 completed items in the last 30 days, confirm a corresponding change ticket (CAB) or governance system entry exists.
3. **Pass:** 100% of sampled items traceable to a ticket.
4. **Evidence:** Sample mapping (action history entry → ticket ID).

---

## Layer 3 — Configuration Hardening Verification

### V3-01 — Hardening baseline review cadence

1. Locate the most recent hardening baseline review record (see [Configuration Hardening Baseline](../../advanced-implementations/configuration-hardening-baseline/index.md)).
2. Verify the review was completed within the required cadence:
    - Zone 1: monthly
    - Zone 2: bi-weekly
    - Zone 3: weekly
3. **Pass:** Most recent review date falls within the cadence window for each in-scope zone.
4. **Evidence:** Review log showing reviewer name, date, zone coverage, and SHA-256 hash of evidence package.

### V3-02 — Configuration drift remediation

1. Review the most recent hardening baseline assessment output.
2. Identify items flagged as drifted from expected values.
3. Confirm each drift item is either remediated or has a documented accepted-risk exception with approver and review-by date.
4. **Pass:** No unresolved drift items.
5. **Evidence:** Drift report showing all items in compliant or accepted-risk state.

### V3-03 — Evidence archival integrity

1. Locate the evidence archive for the most recent review cycle.
2. Verify each archived file has a SHA-256 hash recorded in `manifest.json` (emitted by [PowerShell setup](powershell-setup.md) `Write-FsiEvidence`).
3. Confirm storage is WORM-protected (Purview retention lock or Azure Storage immutability policy) per SEC 17a-4(f) and FINRA 4511.
4. **Pass:** Manifest present, all hashes verifiable, storage immutability enabled.
5. **Evidence:** `manifest.json` plus storage configuration screenshot.

### V3-04 — Blocked attachment extensions

1. Navigate to **PPAC > Environments > [Environment] > Settings > Privacy + Security**.
2. Locate **Blocked Attachments**.
3. Verify the extension list includes at minimum: `ade;adp;app;asa;asp;bat;cdx;cmd;com;cpl;crt;csh;dll;exe;hta;inf;ins;jar;js;jse;lnk;mda;mdb;mde;msc;msi;msp;mst;pcd;pif;reg;scr;sct;shb;shs;tmp;url;vb;vbe;vbs;ws;wsc;wsf;wsh`.
4. **Pass criterion:** List present and includes the critical file types listed above.
5. **Evidence:** Screenshot of the blocked attachments configuration. Repeat per environment.

### V3-05 — Blocked MIME types

1. Same path as V3-04, locate **Blocked MIME Types**.
2. Verify list includes at minimum: `application/javascript`, `application/x-javascript`, `text/javascript`, `application/hta`, `application/msaccess`, `text/scriplet`, `application/xml`, `application/prg`.
3. **Pass criterion:** List present and includes the high-risk types above.
4. **Evidence:** Screenshot per environment.

### V3-06 — Inactivity timeout

1. Same path, locate **Inactivity Timeout**.
2. Verify enabled with duration ≤ 120 minutes (Zone 3: ≤ 60 minutes).
3. **Pass criterion:** Enabled and within zone limit.
4. **Evidence:** Screenshot per environment.

### V3-07 — Session expiration

1. Same path, locate **Session Expiration**.
2. Verify "Set custom session timeout" enabled with maximum session length ≤ 1440 minutes (Zone 3: ≤ 720 minutes).
3. **Pass criterion:** Enabled and within zone limit.
4. **Evidence:** Screenshot per environment.

### V3-08 — Content Security Policy enforcement

1. Same path, locate **Content security policy** under **Model Driven**.
2. Verify "Enforce content security policy" is enabled.
3. **Pass criterion:** Enabled.
4. **Evidence:** Screenshot per environment.

---

## Compliance Checklist (Quick Reference)

| Item | Required for | Status |
|------|--------------|--------|
| Tenant-level analytics enabled | All zones | |
| Security score visible (not "Calculating") | All zones | |
| Per-zone hardening review cadence met | All zones | |
| All High-severity recommendations within SLA | All zones | |
| Dismissed recommendations have documented justification | FINRA 3110, SOX 404 | |
| Snoozed recommendations within window with reason | Governance hygiene | |
| Action history traceable to change tickets | SOX 404, OCC 2023-17 | |
| Managed Environments enabled (in-scope) | Zone 2/3 | |
| DLP policies applied to in-scope environments | GLBA 501(b), FINRA 4511 | |
| Privacy + Security per-environment hardening verified | All zones | |
| Evidence package SHA-256 hashed and WORM-stored | SEC 17a-4(f), FINRA 4511 | |

---

## Test Cases (End-to-End)

### TC-3.7-01 — Score recalculates after remediation

**Objective:** Confirm score reflects configuration changes.

**Steps:**

1. Note current score and an open Medium/High recommendation.
2. Implement the recommendation in a test environment via the inline action or settings page.
3. Wait up to 24 hours.
4. Reopen Security > Overview.

**Expected result:** Score increases or label improves and the recommendation moves to Completed in Action history.

**Evidence:** Before/after screenshots, action history entry.

### TC-3.7-02 — Dismissed recommendation re-surfaces if condition recurs

**Objective:** Confirm dismiss is not a permanent suppression.

**Steps:**

1. Dismiss a recommendation that is currently met.
2. Re-introduce the trigger condition in a non-production environment.
3. Wait for the next refresh (per recommendation; some are real-time, some weekly).
4. Confirm the recommendation reappears in the active list.

**Expected result:** Recommendation re-activates when the condition is re-detected.

**Evidence:** Screenshot of recommendation status before, after dismissal, and after recurrence.

---

## Evidence Package — What to Archive

| Artifact | Source | Frequency |
|----------|--------|-----------|
| Security score screenshot with timestamp | PPAC > Security > Overview | Per posture report |
| Recommendations export (CSV) | PPAC > Actions > Recommendations | Per posture report |
| Dismissed recommendations log | Local governance system | Continuously updated; snapshot per report |
| Snoozed recommendations log | Local governance system | Continuously updated; snapshot per report |
| Action history export | PPAC > Actions > Action history | Per posture report |
| `environment-posture-*.json` (+ SHA-256) | PowerShell collector | Per posture report |
| `dlp-coverage-*.json` (+ SHA-256) | PowerShell collector | Per posture report |
| `tenant-settings-*.json` (+ SHA-256) | PowerShell collector | Per posture report |
| `control-3.7-summary-*.json` (+ SHA-256) | PowerShell collector | Per posture report |
| Per-environment Privacy + Security screenshots | Manual review (V3-04..08) | Per zone cadence |
| Hardening baseline review log | Local governance system | Per zone cadence |
| `manifest.json` (SHA-256 manifest of all artifacts) | `Write-FsiEvidence` helper | Per posture report |

Store under WORM (Purview retention lock or Azure Storage immutability) per SEC 17a-4(f) and FINRA 4511.

---

[Back to Control 3.7](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
