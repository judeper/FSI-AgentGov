# Control 1.9 — Verification & Testing: Data Retention and Deletion Policies

**Control:** 1.9 — Data Retention and Deletion Policies
**Pillar:** Pillar 1 — Security
**Audience:** Purview Records Manager, Purview Compliance Admin, Compliance Officer, Internal Audit, External Examiner liaison
**Companion playbooks:** [Portal walkthrough](./portal-walkthrough.md) · [PowerShell setup](./powershell-setup.md) · [Troubleshooting](./troubleshooting.md)

> This playbook validates that retention, immutability, and disposition for [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) actually work as designed — not just that the policies were created. Run end-to-end before declaring the control implemented and on a documented cadence (at minimum **quarterly** for Zone 3) thereafter.
>
> **Hedging note.** Passing this verification helps meet, and is recommended to support compliance with, SEC 17 CFR 240.17a-4, FINRA 4511, SOX §404 / §802, GLBA 501(b), CFTC 1.31, and IRS recordkeeping rules. It does **not by itself** satisfy 17a-4(f) — see the parent control's "SEC 17a-4(f) caveat."

---

## Verification checklist

Run each item; record PASS / FAIL / N/A and capture the named evidence artifact.

| # | Verification step | Method | Pass criterion | Evidence artifact |
|---|---|---|---|---|
| 1 | Retention schedule is signed off by counsel and references regulations | Document review | Signed PDF references 17a-4, FINRA 4511, SOX §802, GLBA 501(b), CFTC 1.31, IRS | `retention-schedule-signed-YYYYMM.pdf` |
| 2 | All FSI labels exist with planned duration and flags | PS: `Get-ComplianceTag` | `IsRecordLabel`/`Regulatory` match design; `RetentionDuration` matches schedule | `labels-YYYYMMDD.csv` |
| 3 | Label policy distribution status is **Success** | Portal: Records management > Label policies | All FSI label policies show **Success** | Screenshot + `policies-YYYYMMDD.csv` |
| 4 | Three AI-experience retention policies exist and are distributed | PS: `Get-RetentionCompliancePolicy` | `FSI-Copilot-AIExperiences-Retention`, `FSI-EnterpriseAIApps-Retention`, `FSI-OtherAIApps-Retention` all `DistributionStatus = Success` | `policies-YYYYMMDD.csv` |
| 5 | Preservation Lock applied to Zone 3 retention policies | PS: `Get-RetentionCompliancePolicy | Where RetentionComplianceLockType -eq 'Lock'` | All Zone 3 policies show `Lock` | `lock-<policy>-YYYYMMDD.json` |
| 6 | Test deletion is blocked during retention | Test scenario T-1 below | Deletion attempt fails with retention block; audit log records the block | Audit search export |
| 7 | Disposition review fires at retention end and produces reviewer audit trail | Test scenario T-2 below | Item appears in disposition queue; reviewer decision recorded | Disposition decision CSV export |
| 8 | eDiscovery hold preserves content past retention disposition | Test scenario T-3 below | Item retained even though retention would dispose; release of hold restores normal behavior | Hold inventory export |
| 9 | Audit log captures retention/deletion event types | Portal: Audit > Search | Event types in §5 of [PowerShell setup](./powershell-setup.md) all return results | Audit search CSV export |
| 10 | Dataverse long-term retention is configured for Copilot Studio environments | PPAC > Environments > Long-term retention | Policy exists for `botcomponent`, `conversationtranscript`, `botsession`/`botinteraction` | PPAC screenshot + Dataverse policy export |
| 11 | Storage tiering plan documents hot → cool transition at year 2 | Document review | Plan names tier, retrieval SLA, who owns retrieval | `storage-tiering-plan-YYYYMM.md` |
| 12 | D3P arrangement exists if any 17a-4(f) attestation is claimed | Vendor contract review | Signed Designated Third Party undertaking on file | `d3p-undertaking-YYYY.pdf` (or "N/A — no 17a-4(f) claim") |

---

## Test scenarios

Each scenario uses a **disposable test tenant container** (test SharePoint site, test mailbox, test Copilot Studio environment) so production data is never used as the test specimen.

### T-1: Retention prevents deletion within window

**Goal:** Prove that retention actually blocks deletion.

1. **Setup.** Create a SharePoint document library scoped to the `FSI-Agent-Labels-Publish-Zone3` policy. Wait for label availability (≤24 h).
2. **Apply.** Upload a test file `T1-retention-test.docx`. Apply the `FSI-Agent-BooksRecords-6Year` label.
3. **Verify label applied.**
    - Portal: file properties show the retention label and "Retain until <created+6yr>".
    - PS:
      ```powershell
      Get-PnPListItem -List 'Documents' -PageSize 10 |
          Where-Object { $_.FieldValues.FileLeafRef -eq 'T1-retention-test.docx' } |
          Select-Object @{n='Label';e={$_.FieldValues._ComplianceTag}}, @{n='RetainUntil';e={$_.FieldValues._ComplianceTagWrittenTime}}
      ```
4. **Attempt deletion.** Delete the file from SharePoint and from the second-stage Recycle Bin.
5. **Expected.** Site collection administrators cannot permanently delete the file; it remains in the Preservation Hold Library. Audit log records `FileDeleted` followed by retention enforcement.
6. **Capture.** Export an audit search filtered to the test file showing the retention block.

### T-2: Disposition review fires and is auditable

**Goal:** Prove the disposition workflow produces examiner-ready evidence.

1. **Setup.** Create a temporary "smoke test" label `FSI-AgentTest-7Day` (7-day retention, action **Start a disposition review**, reviewer = test mailbox). Publish to a test site.
2. **Apply** the test label to a test document.
3. **Wait** 7 days (or accelerate by setting the `_ComplianceTagWrittenTime` to 8 days prior in a test-only environment — never in production).
4. **Verify** the item appears in **Records management > Disposition** queue.
5. **Reviewer action.** As Stage 1 reviewer, choose **Approve disposal** with a justification.
6. **Expected.** Item is disposed within ~1 day. The disposition record (item name, reviewer, justification, decision date) appears in the **Disposition** > **Disposed items** view and persists for the disposition retention period.
7. **Capture.** Export the disposition decision row as CSV.
8. **Cleanup.** Delete the smoke-test label and policy.

### T-3: Legal hold beats retention

**Goal:** Prove eDiscovery hold preserves an item that would otherwise be disposed.

1. **Setup.** Use a test mailbox and test SharePoint site. Apply `FSI-AgentTest-7Day` (from T-2).
2. **Hold.** Create an eDiscovery (Standard) case `Matter-Test-1.9-T3` and add a hold scoped to the test mailbox + site with no query (preserve everything).
3. **Wait** past the 7-day retention.
4. **Expected.** Item is **not** disposed. The Disposition queue may show the item but disposition is suppressed. Hold detail panel shows the item count.
5. **Release hold.** Document the release decision in the test case file.
6. **Expected.** Normal disposition resumes; item flows into the disposition queue (or auto-deletes per label action).

### T-4: Preservation Lock prevents weakening (Zone 3)

**Goal:** Prove a locked policy cannot be relaxed.

1. **Pick** a locked Zone 3 policy.
2. **Attempt to disable:**
    ```powershell
    Set-RetentionCompliancePolicy -Identity 'FSI-Copilot-AIExperiences-Retention' -Enabled:$false
    ```
3. **Expected.** Cmdlet fails with an error indicating the policy is locked.
4. **Attempt to shorten retention:**
    ```powershell
    Set-RetentionComplianceRule -Identity 'FSI-Copilot-AIExperiences-6Year' -RetentionDuration 30
    ```
5. **Expected.** Cmdlet fails for the same reason.
6. **Confirm permitted action — extend retention:**
    ```powershell
    Set-RetentionComplianceRule -Identity 'FSI-Copilot-AIExperiences-6Year' -RetentionDuration 2920  # 8 years
    ```
7. **Expected.** Succeeds. Capture the new value, then revert by extending again to your design value (because reducing back to 6 years is **not** allowed once extended).

!!! warning "Do not run T-4 step 6 in production"
    Extending retention on a locked policy is itself irreversible. Run T-4 only against a dedicated test policy in a non-production tenant.

### T-5: Dataverse long-term retention archives a transcript

**Goal:** Prove Dataverse archival fires for Copilot Studio transcripts.

1. Pick a test environment hosting a sandbox Copilot Studio agent.
2. Generate a handful of test transcripts (run a few utterances).
3. Open PPAC > **Environments** > the test environment > **Settings** > **Data management** > **Long-term retention** > the policy on `conversationtranscript`.
4. Force the archive trigger by adjusting the test policy to "older than 1 day" temporarily.
5. **Expected.** After the next archive job (review **Job history**), the test rows appear in the Long-Term Retention pane and are no longer in the operational table.
6. Restore the policy's production trigger value before leaving the environment.

---

## Auditor evidence package

Bundle these artifacts under `evidence/1.9/YYYY-Q#/` for examination response:

1. **Schedule** — `retention-schedule-signed-YYYYMM.pdf`
2. **Inventory** — `labels-YYYYMMDD.csv`, `policies-YYYYMMDD.csv`, `rules-YYYYMMDD.csv` (from PowerShell §7)
3. **Lock proof** — `lock-<policy>-YYYYMMDD.json` for every Zone 3 locked policy + portal screenshot per policy
4. **Distribution proof** — Purview > Label policies > policy > Distribution status screenshot
5. **AI-experience locations** — Purview > Data lifecycle management > Policies > each AI policy screenshot showing the AI-experience location enabled
6. **T-1 evidence** — audit log export showing retention block on the test file
7. **T-2 evidence** — disposition decision row export
8. **T-3 evidence** — hold inventory + release record
9. **T-4 evidence** — PowerShell transcript showing locked-policy failures (steps 2 and 4)
10. **T-5 evidence** — PPAC archive job history screenshot
11. **Audit log retention** — Purview > Audit > Audit retention policies showing the FSI deletion-events policy
12. **D3P** — `d3p-undertaking-YYYY.pdf` (or signed memo stating "no 17a-4(f) attestation claimed")
13. **SHA-256 manifest** — `evidence-manifest-YYYYMMDD.csv` from PowerShell §7

---

## Zone-specific verification

### Zone 1 (Personal Productivity)

- Conversation retention: 1-year minimum
- Configuration retention: 6 months
- Disposition: automatic deletion (no review queue expected)
- Preservation Lock: not required
- Run scenarios T-1 (verify deletion at end of retention) and T-2 are not applicable; document waiver

### Zone 2 (Team Collaboration)

- Conversation retention: 3 years (matches communications floor)
- Configuration retention: 3 years
- Disposition: manager + records-management approval
- Preservation Lock: not required (CAB-controlled changes)
- Run scenarios T-1, T-2, T-3

### Zone 3 (Enterprise Managed)

- Conversation retention: 6 years (books-and-records floor)
- Audit retention: 7–10 years
- Disposition: full Stage 1/2/3 reviewer chain
- Preservation Lock: applied to every retention policy
- D3P undertaking on file if any 17a-4(f) attestation is made
- Run scenarios T-1 through T-5; T-4 in non-production only

---

## Cadence

| Activity | Frequency | Owner |
|---|---|---|
| Re-export label/policy/rule inventory CSVs | Monthly | Purview Records Manager |
| Re-run T-1 (retention block) | Quarterly | Purview Compliance Admin |
| Re-run T-2 (disposition) | Quarterly | Compliance Officer |
| Re-run T-3 (hold beats retention) | Semi-annually | Purview eDiscovery Roles + Legal |
| Confirm Preservation Lock state | Monthly | Purview Compliance Admin |
| Validate Dataverse long-term retention | Quarterly | Power Platform Admin |
| Reconcile schedule against new regulations | Annually + on significant rule changes | Compliance Officer + Counsel |

---

## Cross-references

- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md): the audit trail this control depends on.
- [Control 4.3 — Site and Document Retention Management](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md): SharePoint-specific verification.

---

[Back to Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) · [Portal walkthrough](./portal-walkthrough.md) · [PowerShell setup](./powershell-setup.md) · [Troubleshooting](./troubleshooting.md)

---

*Updated: April 2026 | Version: v1.6.2*
