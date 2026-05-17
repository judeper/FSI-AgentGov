# Verification & Testing: Control 2.14 — Training and Awareness Program

**Last Updated:** April 2026

This playbook describes how to confirm that Control 2.14 is operating as documented and that the evidence is examination-defensible under FINRA / SEC / GLBA. The tests below verify the platform configuration, the curriculum delivery, the completion data, and the supervisory linkage.

---

## Test Plan

| Test ID | Scenario | Method | Pass Criteria |
|---|---|---|---|
| TC-2.14-01 | Knowledge Admin role assignment limited and reviewed | Entra audit log review | Role assignments are named individuals; PIM-eligible where applicable |
| TC-2.14-02 | Viva Learning content sources match approved list | Teams admin center inspection | Only approved sources enabled; SharePoint and LMS sources match policy |
| TC-2.14-03 | SharePoint custom content ingested | Pilot user search in Viva Learning | All approved files searchable within 24 h of upload (≤1,000 file ceiling) |
| TC-2.14-04 | LMS connector (if used) syncs assignments and completions | Pilot user assignment + completion | Assignment appears in Viva Learning ≤24 h; completion reflected ≤48 h |
| TC-2.14-05 | Roster generation script produces deterministic output | Run Script 1 twice | Same user count; SHA-256 manifest produced; transcript captured |
| TC-2.14-06 | Compliance reconciliation flags expired completions | Run Script 2 with backdated completion | User with completion older than `ValidityDays` is `Expired`, not `Compliant` |
| TC-2.14-07 | Approval workflow blocks publishing for non-compliant maker (Zone 3) | Submit publish request as test maker | Approval task returns "training incomplete" outcome and logs the decision |
| TC-2.14-08 | Reminder script honors `-WhatIf` | Run Script 3 with `-WhatIf` | No mail sent; log records `WhatIf` status for each recipient |
| TC-2.14-09 | Training evidence retained per policy | Purview policy inspection | Retention policy / records label scoped to the SharePoint site and notification mailbox |
| TC-2.14-10 | Curriculum aligned to current FINRA guidance | Curriculum review against FINRA RN 25-07 | Curriculum addresses AI capabilities, limitations, bias, hallucination, escalation |

Record outcomes against the test ID for the audit file.

---

## Manual Verification Steps

### Test 1 — Knowledge Admin Role Hygiene

1. Sign in to the [Microsoft Entra admin center](https://entra.microsoft.com).
2. Open **Identity > Roles & admins > Roles & admins** and select **Knowledge Admin**.
3. Confirm assignments are named individuals (not groups of broad scope) with a documented business justification.
4. If Entra PIM is in use, confirm assignments are **eligible** rather than **active** wherever feasible.

### Test 2 — Viva Learning Content Sources

1. Sign in to the [Microsoft Teams admin center](https://admin.teams.microsoft.com).
2. Open **Viva > Viva Learning > Content sources**.
3. Confirm the enabled sources match the firm's approved list. Disable any unintended sources (for example, third-party providers added during a trial).
4. Take an evidence screenshot for the audit file.

### Test 3 — SharePoint Source Ingestion

1. As **Knowledge Admin**, upload a known new file to the SharePoint learning site.
2. Wait 24 hours.
3. As a non-admin pilot user, open Viva Learning and search for the file by title.
4. **Pass:** the new file appears with a Viva Learning preview.

### Test 4 — LMS Connector (Where Used)

1. As the LMS owner, assign a known course to a pilot user.
2. As the pilot user, open Viva Learning and confirm the assignment is visible.
3. Complete the course in the LMS.
4. Confirm the completion reflects in Viva Learning within 48 hours and appears in the LMS export used by Script 2.

### Test 5 — Approval Workflow Block (Zone 3)

1. As a test maker without a current training completion, attempt to submit an agent for publishing in a Zone 3 environment.
2. **Pass:** the approval workflow rejects (or holds) the submission and records the reason as "training incomplete or expired."
3. Capture the workflow run history as evidence.

### Test 6 — Curriculum Currency Review

Review the curriculum against the current FINRA guidance set:

- FINRA Rule 3110(a)(7)
- FINRA Regulatory Notice 25-07
- FINRA 2026 Annual Regulatory Oversight Report — GenAI section

The curriculum should explicitly address: AI capabilities, AI limitations, bias / fairness, hallucination, prompt-injection awareness, escalation, and recordkeeping. Evidence: a dated curriculum review memo signed by the AI Administrator and the Purview Compliance Admin.

---

## Evidence Collection Checklist

### Configuration

- [ ] Screenshot: Entra Knowledge Admin assignment list
- [ ] Screenshot: Teams admin center > Viva Learning > Content sources
- [ ] Screenshot: SharePoint learning site permissions (M365 Group / Security Group only)
- [ ] Screenshot: LMS connector configuration (if applicable, with secrets redacted)

### Completion data

- [ ] Export: LMS or Viva Learning completion CSV (covering the reporting period)
- [ ] Output: Script 1 roster JSON + CSV + manifest (SHA-256)
- [ ] Output: Script 2 compliance JSON + CSV + summary + manifest (SHA-256)
- [ ] Output: Script 3 reminder log (CSV) for any reminders sent

### Process linkage

- [ ] Workflow run history showing approval-flow blocks for non-compliant maker (Zone 3)
- [ ] Curriculum review memo dated within the last 12 months
- [ ] Purview retention policy scope showing training evidence locations
- [ ] Records-label evidence (where SEC 17a-4(f) WORM applies)

---

## Evidence Artifact Naming Convention

```
Control-2.14_[ArtifactType]_[YYYYMMDDTHHMMSSZ].[ext]

Examples:
  Control-2.14_Roster_20260415T143000Z.json
  Control-2.14_Roster_20260415T143000Z.csv
  Control-2.14_Compliance_20260415T143200Z.json
  Control-2.14_Manifest_20260415T143200Z.json   # SHA-256 hashes
  Control-2.14_VivaSources_20260415T143500Z.png
  Control-2.14_CurriculumReviewMemo_20260415.pdf
```

Store artifacts in WORM-locked storage (Purview Records Management label, or Azure Storage immutability policy) where they evidence FINRA / SEC-impacting activity.

---

## Attestation Statement Template

```markdown
## Control 2.14 Attestation — Training and Awareness Program

**Organization:** [Firm Name]
**Control Owner (Primary):** [AI Administrator name / role]
**Compliance Sign-off:** [Purview Compliance Admin name / role]
**Reporting Period:** [YYYY-MM-DD to YYYY-MM-DD]

I attest that, for the period above:

1. The AI governance curriculum was current and addressed the topics listed in
   FINRA Regulatory Notice 25-07 and the 2026 Annual Regulatory Oversight Report.
2. Training was assigned to all in-scope personnel based on their Entra role
   and business function.
3. Completion data was collected from [LMS / Viva Learning], reconciled against
   the in-scope roster, and exported to evidence storage with SHA-256 manifests.
4. For Zone 3 environments, the agent publishing approval workflow blocked
   non-compliant or expired makers; exceptions were reviewed and documented.
5. Training evidence is retained in [WORM-locked location] per the firm's
   record-retention schedule.

**Compliance Rate (Zone 3 in-scope):** [X]%
**Compliance Rate (overall in-scope):** [X]%
**Open Exceptions:** [N] — see exception register

Signed: __________________________  Date: __________
Counter-signed: ___________________  Date: __________
```

---

[Back to Control 2.14](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
