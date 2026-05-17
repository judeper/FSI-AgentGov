# Verification & Testing — Control 1.13: Sensitive Information Types and Pattern Recognition

> **Scope.** Operational verification procedures for Control 1.13 across Microsoft 365 Copilot, Copilot Studio, Power Platform, and SharePoint-grounded agents in US financial-services tenants.
> **Audience.** Microsoft 365 administrators, Purview engineers, internal auditors, and supervisory examiners at FINRA member firms, SEC-registered investment advisers, OCC/FRB-supervised banks, and CFTC-registered swap dealers.
> **Sovereign coverage.** Commercial · GCC · GCC High · DoD — see §5 for parity caveats.
> **Cross-links.** [Portal walkthrough](portal-walkthrough.md) · [PowerShell setup](powershell-setup.md) · `troubleshooting.md` (sibling playbook — pending publication) · [Shared PowerShell baseline](../../_shared/powershell-baseline.md)
> **Last UI Verified.** April 2026 (Microsoft Purview portal `purview.microsoft.com`, Microsoft 365 Admin Center `admin.cloud.microsoft`).

---

## What this verification catches

Verification of SIT and pattern-recognition coverage exists to surface failure modes that produce silent NPI exposure through agent grounding. The following ten failure modes are explicit targets of this playbook:

1. **Silent SIT miss in Copilot grounding.** A built-in or custom SIT exists in the tenant but is not referenced by an active DLP-for-Copilot policy, so an agent surfaces SSN- or account-bearing content without policy enforcement. Detected by tests `1.13-DLP-01` through `1.13-DLP-03` and the incident reproduction test `1.13-IR-01`.
2. **EDM near-match leakage.** An Exact Data Match classifier is configured for exact-only equality but a downstream regex normalization (whitespace, hyphenation) allows a near-miss row to pass. Detected by `1.13-EDM-02`.
3. **Preview → GA classifier ID drift.** A trainable classifier referenced by ID in a DLP policy is the preview build; Microsoft promotes it to GA with a new GUID and the policy silently stops matching. Detected by `1.13-NEG-03`.
4. **DLP-for-Copilot mistargeting.** A policy is scoped to a *user* group rather than the *agent identity / SharePoint site* containing the grounding source, so the policy never evaluates the grounding query. Detected by `1.13-NEG-05`.
5. **Fabricated SLA reliance.** A runbook says "wait 24 hours for SIT indexing" without a Microsoft-published basis, so testers prematurely declare a pass. Mitigated by §3 (Documented processing windows) which cites only Microsoft-published windows feature-by-feature.
6. **Hard-coded numeric confidence thresholds in operator UX.** Operators are told "≥85 = High" without referencing the custom SIT XML `confidenceLevel` attribute that defines the band; a SIT change silently breaks the assumption. Detected during `1.13-CUSTOM-01..04` review and §8 Anti-Pattern #6.
7. **No negative corpus.** Only positive matches are tested, so false-positive rate is unknown and Zone 3 block actions create denial-of-service to legitimate agent queries. Detected by every `*-NEG-*` and the `-negative-` half of each pair.
8. **EDM hash drift.** The EDM Upload Agent runs against a stale schema or stale source extract, producing a hash set that no longer matches production data. Detected by `1.13-NEG-02`.
9. **Sovereign-cloud false attestation.** A Commercial-tenant attestation is reused for a GCC High tenant where NER, trainable classifiers, or DSPM for AI are not yet at parity. Detected by `1.13-PRE-07` and §5.
10. **Trainable classifier without OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) model-risk evidence.** A custom trainable classifier is deployed without documented training-data lineage, validation set, or model-risk sign-off, breaching the FSI Governance Gate defined in the control spec. Detected by `1.13-TC-01..04`.

---

## §1 Verification cadence

Cadence is **firm-defined** under WSPs (FINRA Rule 3110) and supervisory procedures. Microsoft does not publish a verification cadence for SIT or DLP correctness. The table below is the minimum recommended cadence for FSI tenants; firms may shorten any interval based on risk.

| Cadence | Test scope | Owner (Responsible) | Owner (Accountable) | Regulatory driver |
|---------|------------|---------------------|---------------------|-------------------|
| **Daily** | UAL sampling (`1.13-AUDIT-01..04`); DLP alert queue triage | Purview Compliance Admin | Compliance Officer | FINRA 3110(b), SEC 17a-4(f), SOX ITGC |
| **Weekly** | DLP-for-Copilot match review (`1.13-DLP-01..03`); DSPM for AI surfacing (`1.13-DSPM-01..02`) | Information Protection Admin | CISO | GLBA Safeguards 314.4(d); OCC Heightened Standards |
| **Monthly** | Full BUILTIN (`1.13-BUILTIN-01..08`) and CUSTOM (`1.13-CUSTOM-01..04`) regression with positive + negative corpus | Information Protection Admin | Compliance Officer | FINRA 3110, SEC Reg S-P |
| **Quarterly** | EDM (`1.13-EDM-01..03`), Trainable Classifier (`1.13-TC-01..04`), NER (`1.13-NER-01..04`), Negative-path battery (`1.13-NEG-01..05`), Sovereign parity recheck (§5) | Compliance Data Administrator + Information Protection Admin | CRO | OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7); GLBA Safeguards |
| **On change** | Any test affected by a tenant change (new SIT, EDM schema rotation, DLP rule edit, classifier promotion preview→GA, role-group change, sovereign-cloud feature GA) | Purview Compliance Admin | Compliance Officer | SOX ITGC change-control |
| **On incident** | `1.13-IR-01` reproduction with the actual unredacted incident artifact in a contained eDiscovery workspace | Incident Response Lead + Compliance Data Administrator | CISO + Compliance Officer | SEC Reg S-P §248.30; state breach laws; NYDFS 500.17 |

**RACI note.** Accountable role per RACI may not match the role with admin permissions. The Compliance Officer is accountable but does not hold Purview Compliance Admin rights; that separation is required by the role-separation control (1.5) and audited at `1.13-PRE-04`.

---

## §2 Pre-flight (1.13-PRE-01..07)

Pre-flight tests must pass **before** any §4 test is executed. A failed pre-flight blocks the entire verification cycle and is itself a finding.

### 1.13-PRE-01 — License entitlement

**Objective.** Confirm that the tenant holds the licenses required for every detection primitive in scope.

**Preconditions.** Entra Global Reader or License Administrator role; access to `admin.cloud.microsoft` → Billing → Licenses.

**Steps.**
1. In Microsoft 365 admin center, navigate to **Billing → Licenses**.
2. Confirm presence of: **Microsoft 365 E5** or **E5 Compliance** add-on (required for EDM, NER, trainable classifiers, DSPM for AI), **Microsoft 365 Copilot** (required for DLP-for-Copilot policy type), and **Microsoft Purview Audit (Premium)** (required for 1-year+ UAL retention referenced by `1.13-AUDIT-*`).
3. Record license SKU GUIDs and seat counts in the evidence manifest.

**Expected.** All three SKUs present with sufficient seats to cover every test user and every agent identity referenced by §4.

**Pass criteria.** SKU presence verified; screenshot or `Get-MgSubscribedSku` JSON output captured.

**Audit assertion.** None — license check is not a UAL-emitting event. Evidence is the captured admin-center state.

**Evidence collected.** `1.13-PRE-01-licenses.json` (output of `Get-MgSubscribedSku | Select-Object SkuPartNumber, ConsumedUnits, PrepaidUnits`), `1.13-PRE-01-screenshot.png`.

### 1.13-PRE-02 — Unified Audit Log enabled

**Objective.** Confirm UAL ingestion is enabled and that the operations referenced by `1.13-AUDIT-*` are emitted by the tenant.

**Preconditions.** Audit Reader or Audit Manager role.

**Steps.**
1. Open `compliance.microsoft.com` → **Audit**.
2. Confirm the banner does not state "Start recording user and admin activity".
3. Run a 7-day search filtered to operations: `SitCreated`, `SitUpdated`, `SitDeleted`, `EdmSchemaCreated`, `EdmSchemaUpdated`, `EdmDataUploaded`, `DlpRuleMatch`, `CopilotInteraction`. Verify each operation appears in the dropdown (operation name autocomplete).
4. Export results to CSV.

**Expected.** UAL is enabled; all eight operation names are recognized by the search UI.

**Pass criteria.** UAL banner absent; all eight operations present in autocomplete; CSV exported.

**Audit assertion.** N/A (this test verifies UAL itself).

**Evidence collected.** `1.13-PRE-02-ual-search.csv`, `1.13-PRE-02-screenshot.png`.

> **Verify on Microsoft Learn at execution time.** Operation-name spelling for `SitCreated`/`SitUpdated`/`EdmSchemaCreated`/`EdmDataUploaded`/`DlpRuleMatch`/`CopilotInteraction` is subject to change. Confirm against `learn.microsoft.com/purview/audit-log-activities` before signing the attestation in §7.

### 1.13-PRE-03 — PowerShell modules pinned

**Objective.** Confirm verifier workstation has the pinned module versions defined in the shared baseline.

**Preconditions.** Workstation with PowerShell 7.4+; access to PSGallery (or sovereign equivalent).

**Steps.** Follow [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) §2. Pinned modules: `ExchangeOnlineManagement`, `Microsoft.Graph`, `Microsoft.Graph.Beta`, `PnP.PowerShell`, `Microsoft.PowerApps.Administration.PowerShell`. Capture `Get-Module -ListAvailable | Where-Object { $_.Name -in @(...) } | Select Name, Version` output.

**Expected.** All five modules present at the version pinned by the shared baseline.

**Pass criteria.** Module table matches baseline; no module is at "latest" / unpinned.

**Audit assertion.** N/A.

**Evidence collected.** `1.13-PRE-03-modules.json`.

### 1.13-PRE-04 — Role separation

**Objective.** Confirm SIT-management, DLP-management, and audit-review roles are held by separate principals (separation of duties per Control 1.5).

**Preconditions.** Entra Global Reader.

**Steps.**
1. Enumerate members of: **Information Protection Admin**, **Purview Compliance Admin**, **Compliance Data Administrator**, **Audit Manager**.
2. Confirm no single human principal holds more than one of {Information Protection Admin, Purview Compliance Admin, Audit Manager}.
3. Confirm no service principal holds Information Protection Admin without an approved exception ticket.

**Expected.** Each role group has ≥1 member; no overlap among the three sensitive groups.

**Pass criteria.** Membership matrix exported; overlap check passes.

**Audit assertion.** Role-group membership change events emit `Add member to role` in UAL; out of scope for this test but referenced by Control 1.5.

**Evidence collected.** `1.13-PRE-04-role-matrix.csv`.

### 1.13-PRE-05 — EDM Upload Agent installed and IPPS connectivity

**Objective.** Confirm the EDM Upload Agent is installed on the designated secure workstation and can authenticate to Information Protection PowerShell (IPPS).

**Preconditions.** Workstation hardened per Control 1.7; Compliance Data Administrator role.

**Steps.**
1. On the EDM workstation, confirm `EdmUploadAgent.exe` is present at the documented install path.
2. Run `Connect-IPPSSession` (use sovereign endpoint per §5 for non-Commercial clouds).
3. Run `Get-DlpEdmSchema` and confirm the existing schema list returns without error.

**Expected.** Agent present; IPPS session established; schema list returned.

**Pass criteria.** Agent version recorded; `Get-DlpEdmSchema` returns ≥1 schema (or `0` if none yet defined — record either way).

**Audit assertion.** `EdmSchemaCreated` / `EdmSchemaUpdated` events emit when schemas are mutated; verified in `1.13-AUDIT-02`.

**Evidence collected.** `1.13-PRE-05-edm-agent-version.txt`, `1.13-PRE-05-schema-list.json`.

### 1.13-PRE-06 — Test corpus staged with SHA-256 manifest

**Objective.** Confirm the synthetic positive + negative test corpus exists at `tests/1.13/corpus/` and that every file's SHA-256 hash is recorded in `1.13-corpus-manifest.json`.

**Preconditions.** Repository checkout; `Get-FileHash` available.

**Steps.**
1. List corpus directory: `Get-ChildItem tests/1.13/corpus/ -Recurse -File`.
2. Verify naming convention `1.13-{TYPE}-{positive|negative}-{NNN}.{ext}` (e.g., `1.13-SSN-positive-001.txt`, `1.13-CC-negative-014.docx`).
3. Recompute SHA-256 for every file and compare to `1.13-corpus-manifest.json` shipped with the repo.
4. Confirm the corpus contains **no** real customer NPI. Acceptable test values include the Luhn-valid card test PAN `4111-1111-1111-1111` and SSA-published test SSNs from the 987-65-4xxx range. The string `123-45-6789` must **not** be used as an SSA-invalid example for positive cases.

**Expected.** Every corpus file present; every SHA-256 matches manifest; no real NPI.

**Pass criteria.** Hash diff is empty; manual sample of 10 files confirms synthetic content.

**Audit assertion.** N/A.

**Evidence collected.** `1.13-PRE-06-corpus-hash-diff.txt`.

### 1.13-PRE-07 — Three named test agents and sovereign parity check

**Objective.** Confirm the three named test agents exist and that the sovereign-cloud feature parity matrix (§5) has been refreshed in the last 30 days.

**Preconditions.** Power Platform Admin; Copilot Studio access; SharePoint admin for the controlled test site.

**Steps.**
1. Confirm three Copilot Studio agents exist: `agent-fsi-test-Z1`, `agent-fsi-test-Z2`, `agent-fsi-test-Z3`. Each must be grounded on the controlled SharePoint site `https://{tenant}.sharepoint.com/sites/fsi-test-1.13`.
2. Confirm each agent is published to a single test user (not org-wide).
3. Confirm the sovereign parity matrix (§5) has a "Last verified" timestamp within 30 days of the current run.

**Expected.** Three agents present, correctly scoped; sovereign matrix current.

**Pass criteria.** Agent inventory matches; sovereign matrix timestamp ≤30 days old.

**Audit assertion.** Agent-creation events emit `CopilotAgentCreated` (verify spelling on Learn at execution); referenced by Control 4.6.

**Evidence collected.** `1.13-PRE-07-agent-inventory.json`, `1.13-PRE-07-sovereign-matrix-timestamp.txt`.

---

## §3 Documented processing windows

The windows below are **the only** windows cited by Microsoft Learn at the date of last UI verification (April 2026). No other "wait N hours" instruction in this playbook is permitted. If a feature has no published window, the playbook says **"no committed SLA — verify by audit event, not by elapsed time."**

| Feature | Microsoft-published window | Source anchor (verify at execution) | Test usage |
|---------|---------------------------|-------------------------------------|------------|
| DLP-for-Copilot policy enforcement after publish | Up to ~1 hour | `learn.microsoft.com/purview/dlp-copilot-learn-about` | `1.13-DLP-01..03` polling window |
| Trainable classifier seed-site indexing (initial) | At least 1 hour | `learn.microsoft.com/purview/classifier-learn-about` | `1.13-TC-01..04` |
| DSPM for AI data collection | ~24 hours | `learn.microsoft.com/purview/dspm-for-ai` | `1.13-DSPM-01..02` |
| Role-group membership propagation | ~30 minutes | `learn.microsoft.com/purview/microsoft-365-compliance-center-permissions` | `1.13-PRE-04` re-test after change |
| EDM data upload → match availability | No committed SLA — verify by `EdmDataUploaded` UAL event then test match | `learn.microsoft.com/purview/sit-create-edm-classifier` | `1.13-EDM-01..03` |
| Custom SIT publish → match availability | No committed SLA — verify by `SitCreated`/`SitUpdated` UAL event | `learn.microsoft.com/purview/sit-get-started` | `1.13-CUSTOM-01..04` |
| Built-in SIT match in Copilot grounding | No committed SLA — verify by `DlpRuleMatch` UAL event tied to `CopilotInteraction` | `learn.microsoft.com/purview/sit-defn-overview` | `1.13-BUILTIN-01..08` |

> **Anti-pattern.** Operator-mediated waits ("the analyst waited 24h then re-tested") are not evidence. Pass criteria for every §4 test require an **audit-event assertion**, not an elapsed-time assertion.

---

## §4 Test catalog

Every test below uses the structure: **Objective · Preconditions · Steps · Expected · Pass criteria · Audit assertion · Evidence collected.** Test IDs are stable and referenced by the evidence manifest (§6) and the attestation block (§7).

### Built-in SITs (1.13-BUILTIN-01..08)

#### 1.13-BUILTIN-01 — US SSN positive

**Objective.** Confirm the built-in `U.S. Social Security Number (SSN)` SIT matches an SSA-format compliant test value when present in a SharePoint document grounded by `agent-fsi-test-Z3`.

**Preconditions.** PRE-01..07 passed; corpus file `1.13-SSN-positive-001.txt` (containing SSA test value such as `987-65-4320`) uploaded to the controlled test site; Zone 3 DLP-for-Copilot policy active with `U.S. SSN` SIT at confidence "High" and action "Block".

**Steps.**
1. Upload `1.13-SSN-positive-001.txt` to `/sites/fsi-test-1.13/Shared Documents/`.
2. Wait for `DlpRuleMatch` event referencing the file (poll UAL every 5 minutes; do not assume a fixed window).
3. From the published test user, prompt `agent-fsi-test-Z3`: *"Summarize any documents in the test library that mention the customer."*
4. Capture the agent response and the corresponding `CopilotInteraction` UAL event.

**Expected.** Agent response is blocked or redacted; `DlpRuleMatch` UAL event correlates the SIT, the file, the policy, and the `CopilotInteraction` event ID.

**Pass criteria.** Agent does not surface the SSN string; `DlpRuleMatch.SensitiveInformationTypeName == "U.S. Social Security Number (SSN)"`; `DlpRuleMatch.PolicyId` matches the Zone 3 policy GUID.

**Audit assertion.** `DlpRuleMatch` and `CopilotInteraction` events both present, correlated by `CorrelationId` or shared `SessionId`.

**Evidence collected.** `1.13-BUILTIN-01-ual.json`, `1.13-BUILTIN-01-agent-response.txt`, `1.13-BUILTIN-01-file-hash.txt`.

#### 1.13-BUILTIN-02 — US SSN negative

**Objective.** Confirm the SSN SIT does **not** match a non-SSN nine-digit string (e.g., a phone-number-shaped value) — guards against false-positive denial-of-service.

**Preconditions.** Same as BUILTIN-01.

**Steps.** Repeat BUILTIN-01 substituting `1.13-SSN-negative-001.txt` (e.g., `(987) 654-3201` or random digit string failing SSA range rules).

**Expected.** No `DlpRuleMatch` event for SSN SIT against the negative file; agent surfaces the file content normally.

**Pass criteria.** Zero `DlpRuleMatch` events with `SensitiveInformationTypeName == "U.S. Social Security Number (SSN)"` referencing the negative file's `ObjectId`.

**Audit assertion.** `CopilotInteraction` event present; **absence** of `DlpRuleMatch` is itself the assertion (recorded as a negative-evidence row in the manifest).

**Evidence collected.** `1.13-BUILTIN-02-ual-negative.json`.

#### 1.13-BUILTIN-03 — US Bank Account positive

**Objective.** Confirm `U.S. Bank Account Number` SIT matches an ABA-routing + account-number combination at "High" confidence in Zone 2 (Educate action).

**Preconditions.** PRE-01..07 passed; corpus file `1.13-USBANK-positive-001.txt`; Zone 2 policy active with action "Notify user" (educate).

**Steps.** Upload corpus file; prompt `agent-fsi-test-Z2`; capture educate notification surfaced to the user; capture UAL.

**Expected.** Agent surfaces an educate banner referencing the firm's policy URL; `DlpRuleMatch` event present with `Action == "Notify"`.

**Pass criteria.** Educate banner displayed; `DlpRuleMatch.Action` is `Notify` or `NotifyUser` (verify exact spelling on Learn).

**Audit assertion.** `DlpRuleMatch` with notify action; `CopilotInteraction` event correlated.

**Evidence collected.** `1.13-BUILTIN-03-ual.json`, `1.13-BUILTIN-03-banner-screenshot.png`.

#### 1.13-BUILTIN-04 — US Bank Account negative

**Objective.** Confirm the bank-account SIT does not match a random 9-digit + 10-digit string lacking ABA checksum.

**Preconditions.** Same as BUILTIN-03.

**Steps.** Substitute `1.13-USBANK-negative-001.txt`.

**Expected.** No `DlpRuleMatch` for bank-account SIT.

**Pass criteria.** Zero matching `DlpRuleMatch` events.

**Audit assertion.** Absence of `DlpRuleMatch`; `CopilotInteraction` present.

**Evidence collected.** `1.13-BUILTIN-04-ual-negative.json`.

#### 1.13-BUILTIN-05 — Credit Card positive (Luhn-valid)

**Objective.** Confirm `Credit Card Number` SIT matches the Luhn-valid test PAN `4111-1111-1111-1111` in Zone 1 (alert-only).

**Preconditions.** PRE-01..07 passed; Zone 1 policy with action "Generate alert".

**Steps.** Upload `1.13-CC-positive-001.txt`; prompt `agent-fsi-test-Z1`; capture alert in Defender / Purview alert queue.

**Expected.** Agent surfaces content (alert-only zone); alert appears within firm-defined supervisory window.

**Pass criteria.** Alert created; `DlpRuleMatch.SensitiveInformationTypeName == "Credit Card Number"`.

**Audit assertion.** `DlpRuleMatch` with alert action; `CopilotInteraction` correlated.

**Evidence collected.** `1.13-BUILTIN-05-ual.json`, `1.13-BUILTIN-05-alert-id.txt`.

#### 1.13-BUILTIN-06 — Credit Card negative (Luhn-invalid)

**Objective.** Confirm CC SIT does not match a 16-digit string failing Luhn checksum.

**Preconditions.** Same as BUILTIN-05.

**Steps.** Substitute `1.13-CC-negative-001.txt` containing `4111-1111-1111-1112` (last digit changed to break Luhn).

**Expected.** No `DlpRuleMatch` for CC SIT.

**Pass criteria.** Zero matching events.

**Audit assertion.** Absence; `CopilotInteraction` present.

**Evidence collected.** `1.13-BUILTIN-06-ual-negative.json`.

#### 1.13-BUILTIN-07 — ITIN positive

**Objective.** Confirm `U.S. Individual Taxpayer Identification Number (ITIN)` SIT matches an IRS-format test value (`9NN-7N-NNNN` where NN is in the 70–88 range per IRS publication).

**Preconditions.** Zone 3 policy with ITIN SIT at High confidence.

**Steps.** Upload `1.13-ITIN-positive-001.txt`; prompt `agent-fsi-test-Z3`; capture block.

**Expected.** Agent blocked; `DlpRuleMatch` for ITIN SIT.

**Pass criteria.** Block enforced; UAL event present.

**Audit assertion.** `DlpRuleMatch` with `SensitiveInformationTypeName == "U.S. Individual Taxpayer Identification Number (ITIN)"`.

**Evidence collected.** `1.13-BUILTIN-07-ual.json`.

#### 1.13-BUILTIN-08 — EIN positive

**Objective.** Confirm `U.S. Employer Identification Number (EIN)` SIT matches a 2-7 IRS-format value.

**Preconditions.** Zone 2 educate policy with EIN SIT.

**Steps.** Upload `1.13-EIN-positive-001.txt`; prompt `agent-fsi-test-Z2`.

**Expected.** Educate banner; `DlpRuleMatch` for EIN.

**Pass criteria.** Banner; UAL event.

**Audit assertion.** `DlpRuleMatch` for EIN SIT.

**Evidence collected.** `1.13-BUILTIN-08-ual.json`.

### Custom SITs (1.13-CUSTOM-01..04)

#### 1.13-CUSTOM-01 — FINRA CRD positive

**Objective.** Confirm a custom SIT matching the FINRA Central Registration Depository (CRD) number format (6–7 digits with firm-specific prefix or contextual keywords like `CRD#`, `CRD No`) detects positive samples in Zone 3.

**Preconditions.** Custom SIT defined per playbook `portal-walkthrough.md` §4 with `confidenceLevel="85"` (High band per the custom SIT XML schema — note: the band is firm-defined in XML, not a Microsoft universal threshold). Zone 3 policy references the custom SIT.

**Steps.** Upload `1.13-CRD-positive-001.txt` containing five distinct CRD-format values with surrounding context (`CRD# 1234567`); prompt `agent-fsi-test-Z3`; capture block + UAL.

**Expected.** Block enforced; `DlpRuleMatch` references the custom SIT GUID.

**Pass criteria.** UAL event references the **GUID** (not display name); GUID matches the value recorded in `1.13-CUSTOM-01-sit-id.txt`.

**Audit assertion.** `DlpRuleMatch` with `SensitiveInformationTypeId` matching custom SIT GUID; `SitUpdated` event present in change-history audit if SIT was last modified within the test window.

**Evidence collected.** `1.13-CUSTOM-01-ual.json`, `1.13-CUSTOM-01-sit-xml.xml` (export of current SIT definition), `1.13-CUSTOM-01-sit-id.txt`.

#### 1.13-CUSTOM-02 — FINRA CRD negative

**Objective.** Confirm CRD SIT does not match a generic 7-digit number lacking the contextual keyword (false-positive guard).

**Preconditions.** Same as CUSTOM-01.

**Steps.** Substitute `1.13-CRD-negative-001.txt` containing seven-digit numbers without `CRD` keyword.

**Expected.** No match.

**Pass criteria.** Zero `DlpRuleMatch` events for CRD SIT.

**Audit assertion.** Absence; `CopilotInteraction` present.

**Evidence collected.** `1.13-CUSTOM-02-ual-negative.json`.

#### 1.13-CUSTOM-03 — Internal account number positive

**Objective.** Confirm a firm-defined internal account number SIT (e.g., format `ACCT-NNNNNNNN`) matches positive samples in Zone 2.

**Preconditions.** Custom SIT defined; Zone 2 educate policy active.

**Steps.** Upload `1.13-ACCT-positive-001.txt`; prompt `agent-fsi-test-Z2`.

**Expected.** Educate banner; `DlpRuleMatch`.

**Pass criteria.** UAL event references custom SIT GUID; banner displayed.

**Audit assertion.** `DlpRuleMatch` with custom SIT GUID.

**Evidence collected.** `1.13-CUSTOM-03-ual.json`, `1.13-CUSTOM-03-sit-xml.xml`.

#### 1.13-CUSTOM-04 — Internal account number negative

**Objective.** Confirm internal account SIT does not match `ACCT-NNNN` (too short) or `INVOICE-NNNNNNNN` (wrong prefix).

**Preconditions.** Same as CUSTOM-03.

**Steps.** Substitute `1.13-ACCT-negative-001.txt`.

**Expected.** No match.

**Pass criteria.** Zero matching events.

**Audit assertion.** Absence.

**Evidence collected.** `1.13-CUSTOM-04-ual-negative.json`.

### Exact Data Match (1.13-EDM-01..03)

#### 1.13-EDM-01 — EDM exact match

**Objective.** Confirm an EDM classifier built from a hashed customer-account extract matches a row that exists exactly in the source extract.

**Preconditions.** EDM schema and data uploaded per `powershell-setup.md` §5; daily refresh job verified by `EdmDataUploaded` event in the last 24 hours; Zone 3 policy references the EDM classifier.

**Steps.**
1. Select a known row from the source extract (e.g., row 142 — account `ACCT-12345678`, customer `Smith, J.`, branch `B-014`).
2. Place the row's primary value into `1.13-EDM-positive-exact-001.txt`.
3. Upload to test site; prompt `agent-fsi-test-Z3`; capture block + UAL.

**Expected.** Block enforced; `DlpRuleMatch` references the EDM classifier ID.

**Pass criteria.** UAL event references EDM classifier; `EdmDataUploaded` event for current dataset present within the published feature window (no committed SLA — verified by event presence per §3).

**Audit assertion.** `DlpRuleMatch` with EDM classifier ID; `EdmDataUploaded` event correlated to the dataset version.

**Evidence collected.** `1.13-EDM-01-ual.json`, `1.13-EDM-01-edm-dataset-version.txt`, `1.13-EDM-01-source-row-hash.txt`.

#### 1.13-EDM-02 — EDM near-miss negative

**Objective.** Confirm EDM does **not** match a value that differs by a single character or whitespace from a source row (verifying exact-equality semantics and detecting any unintended fuzzy normalization in the regex layer).

**Preconditions.** Same as EDM-01.

**Steps.** Construct `1.13-EDM-negative-near-001.txt` containing the row 142 account number with one digit altered (`ACCT-12345679`) and a separate file with the exact account number but with hyphenation removed (`ACCT12345678`).

**Expected.** No `DlpRuleMatch` for EDM classifier on either file (or, if normalization is intentional and documented, the normalized form matches and the digit-altered form does not — record which behavior is observed).

**Pass criteria.** Behavior matches the documented EDM normalization rules in the firm's EDM design document. Any unexpected match is a finding.

**Audit assertion.** Absence (or expected presence per documented normalization).

**Evidence collected.** `1.13-EDM-02-ual.json`, `1.13-EDM-02-design-doc-ref.txt`.

#### 1.13-EDM-03 — EDM schema rotation

**Objective.** Confirm an EDM schema rotation (column add/remove or primary-key change) emits `EdmSchemaUpdated` and that downstream policies continue to match correctly.

**Preconditions.** EDM-01 passed; change-control ticket approved for schema rotation.

**Steps.**
1. Modify the schema XML (e.g., add a non-primary column).
2. Re-upload schema via EDM Upload Agent.
3. Confirm `EdmSchemaUpdated` event in UAL.
4. Re-run EDM-01 test against the rotated schema.

**Expected.** `EdmSchemaUpdated` present; EDM-01 still passes against rotated schema.

**Pass criteria.** Both UAL events present; rotation does not regress EDM-01.

**Audit assertion.** `EdmSchemaUpdated` event with new schema version; subsequent `DlpRuleMatch` events reference the updated classifier ID (if classifier ID changes on rotation — verify behavior on Learn).

**Evidence collected.** `1.13-EDM-03-schema-updated-ual.json`, `1.13-EDM-03-rerun-of-edm-01.json`.

### Named Entity Recognition (1.13-NER-01..04)

#### 1.13-NER-01 — PERSON entity positive

**Objective.** Confirm the built-in NER `Person Name` (or current Microsoft naming) classifier surfaces person-name entities in unstructured text.

**Preconditions.** E5 NER feature enabled in the tenant (verify on Learn — NER availability differs across sovereign clouds, see §5); Zone 2 educate policy referencing the NER classifier.

**Steps.** Upload `1.13-NER-PERSON-positive-001.txt` containing distinct person-name examples in narrative context; prompt `agent-fsi-test-Z2`; capture banner + UAL.

**Expected.** Educate banner; `DlpRuleMatch` referencing NER classifier ID.

**Pass criteria.** UAL event references NER classifier; banner shown.

**Audit assertion.** `DlpRuleMatch` with NER classifier identifier (verify exact field name on Learn).

**Evidence collected.** `1.13-NER-01-ual.json`.

#### 1.13-NER-02 — ORG entity positive

**Objective.** Confirm `Organization` NER classifier matches organization names.

**Preconditions.** Same as NER-01.

**Steps.** Upload `1.13-NER-ORG-positive-001.txt`; prompt `agent-fsi-test-Z2`.

**Expected.** Educate banner; UAL match.

**Pass criteria.** UAL references ORG NER classifier ID.

**Audit assertion.** `DlpRuleMatch` for ORG classifier.

**Evidence collected.** `1.13-NER-02-ual.json`.

#### 1.13-NER-03 — ADDRESS entity positive

**Objective.** Confirm `Physical Address` NER matches US street addresses.

**Preconditions.** Same as NER-01.

**Steps.** Upload `1.13-NER-ADDRESS-positive-001.txt`; prompt `agent-fsi-test-Z2`.

**Expected.** Banner; UAL match.

**Pass criteria.** UAL event present.

**Audit assertion.** `DlpRuleMatch` for ADDRESS classifier.

**Evidence collected.** `1.13-NER-03-ual.json`.

#### 1.13-NER-04 — NER false-positive control

**Objective.** Confirm NER does not surface educate banner for narrative text containing common nouns that NER may mis-classify (e.g., "Bill" used as verb, "Apple" used as fruit). Validates that the NER confidence band configured in policy is appropriate.

**Preconditions.** Same as NER-01.

**Steps.** Upload `1.13-NER-negative-001.txt`; prompt `agent-fsi-test-Z2`.

**Expected.** Either no match, or match below the policy's confidence band (no banner surfaced).

**Pass criteria.** Banner not displayed; if `DlpRuleMatch` event is present, its `Confidence` field is below the policy threshold.

**Audit assertion.** Absence of banner is the test outcome; UAL event presence is informational.

**Evidence collected.** `1.13-NER-04-ual.json`, `1.13-NER-04-banner-absent-screenshot.png`.

### Trainable Classifiers (1.13-TC-01..04)

> **FSI Governance Gate.** Trainable classifiers are model artifacts subject to OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) and Federal Reserve SR 26-2 (formerly SR 11-7) (Model Risk Management). Each classifier deployed for Zone 2/3 enforcement requires: documented training-data lineage, validation set with measured precision/recall, model-risk committee sign-off, and re-validation cadence. Tests below assume that gate has been passed; absence of evidence is itself a finding.

#### 1.13-TC-01 — Customer Complaints classifier positive

**Objective.** Confirm the built-in or custom `Customer Complaints` trainable classifier surfaces an educate banner when a Zone 2 agent grounds on complaint-pattern text.

**Preconditions.** Classifier published (preview or GA — record state); model-risk evidence on file; Zone 2 policy references classifier by **GA GUID** if GA, or with documented preview-acceptance approval if preview.

**Steps.** Upload `1.13-TC-COMPLAINT-positive-001.txt` containing complaint-pattern narrative; prompt `agent-fsi-test-Z2`.

**Expected.** Educate banner; `DlpRuleMatch` for classifier.

**Pass criteria.** UAL event references the **current** classifier GUID; if classifier was promoted preview→GA in last 90 days, NEG-03 must also have passed.

**Audit assertion.** `DlpRuleMatch` for TC classifier; classifier GUID matches the value in the model-risk inventory.

**Evidence collected.** `1.13-TC-01-ual.json`, `1.13-TC-01-classifier-guid.txt`, `1.13-TC-01-model-risk-evidence-ref.txt`.

#### 1.13-TC-02 — Customer Complaints classifier negative

**Objective.** Confirm classifier does not match generic customer-service narrative without complaint indicators.

**Preconditions.** Same as TC-01.

**Steps.** Substitute `1.13-TC-COMPLAINT-negative-001.txt` (e.g., positive testimonial text).

**Expected.** No banner; either no match or match below confidence band.

**Pass criteria.** Banner absent.

**Audit assertion.** Absence.

**Evidence collected.** `1.13-TC-02-ual.json`.

#### 1.13-TC-03 — Mergers & Acquisitions classifier

**Objective.** Confirm `Mergers & Acquisitions` (or firm-defined deal-confidential) classifier surfaces in Zone 3 with block action.

**Preconditions.** Classifier published with model-risk evidence; Zone 3 policy active.

**Steps.** Upload `1.13-TC-MA-positive-001.txt`; prompt `agent-fsi-test-Z3`.

**Expected.** Block enforced; `DlpRuleMatch`.

**Pass criteria.** UAL event references classifier GUID.

**Audit assertion.** `DlpRuleMatch` for MA classifier.

**Evidence collected.** `1.13-TC-03-ual.json`.

#### 1.13-TC-04 — Source code classifier

**Objective.** Confirm `Source Code` trainable classifier matches code snippets in narrative documents (Zone 2 educate).

**Preconditions.** Classifier published; Zone 2 policy active.

**Steps.** Upload `1.13-TC-CODE-positive-001.txt` containing a representative code block (Python, C#, etc.); prompt `agent-fsi-test-Z2`.

**Expected.** Educate banner; UAL match.

**Pass criteria.** UAL event present.

**Audit assertion.** `DlpRuleMatch` for source-code classifier.

**Evidence collected.** `1.13-TC-04-ual.json`.

### DLP-for-Copilot policy enforcement (1.13-DLP-01..03)

#### 1.13-DLP-01 — Zone 1 alert

**Objective.** Confirm a Zone 1 (Personal) DLP-for-Copilot policy generates an alert without blocking or notifying the user.

**Preconditions.** Zone 1 policy scoped to `agent-fsi-test-Z1` agent identity (not user identity — see NEG-05 for the mistargeting failure mode).

**Steps.** Upload `1.13-SSN-positive-001.txt`; prompt `agent-fsi-test-Z1`; verify agent surfaces content; verify alert generated in Defender / Purview alert queue.

**Expected.** Content surfaced; alert created.

**Pass criteria.** Alert ID captured; `DlpRuleMatch` with alert action.

**Audit assertion.** `DlpRuleMatch` with `Action == "Alert"` (verify spelling on Learn).

**Evidence collected.** `1.13-DLP-01-ual.json`, `1.13-DLP-01-alert-id.txt`.

#### 1.13-DLP-02 — Zone 2 educate

**Objective.** Confirm Zone 2 policy surfaces educate banner with policy URL link.

**Preconditions.** Zone 2 policy with notify action and policy tip URL configured.

**Steps.** Upload `1.13-USBANK-positive-001.txt`; prompt `agent-fsi-test-Z2`; verify banner with link.

**Expected.** Banner displayed; clicking link goes to firm's policy page.

**Pass criteria.** Banner content matches configured policy tip; UAL match present.

**Audit assertion.** `DlpRuleMatch` with notify action.

**Evidence collected.** `1.13-DLP-02-banner-screenshot.png`, `1.13-DLP-02-ual.json`.

#### 1.13-DLP-03 — Zone 3 block

**Objective.** Confirm Zone 3 policy blocks agent response on High-confidence match.

**Preconditions.** Zone 3 policy with block action.

**Steps.** Upload `1.13-CRD-positive-001.txt`; prompt `agent-fsi-test-Z3`; verify response is blocked or fully redacted.

**Expected.** No NPI surfaced in response.

**Pass criteria.** Agent response contains no SIT-matched substring; UAL event with block action.

**Audit assertion.** `DlpRuleMatch` with block action; `CopilotInteraction` correlated.

**Evidence collected.** `1.13-DLP-03-agent-response.txt`, `1.13-DLP-03-ual.json`.

### DSPM for AI (1.13-DSPM-01..02)

#### 1.13-DSPM-01 — DSPM surfacing

**Objective.** Confirm DSPM for AI surfaces the Zone 3 block events from DLP-03 in the DSPM dashboard within the documented ~24-hour collection window (§3).

**Preconditions.** DSPM for AI enabled; DLP-03 executed ≥24h prior (or executed and then DSPM checked at next available collection cycle — whichever comes later).

**Steps.** Open Purview → DSPM for AI → Reports; confirm the Zone 3 block events appear with correct agent identity and SIT name.

**Expected.** Events visible with correct attribution.

**Pass criteria.** Event count in DSPM matches UAL count for the same window.

**Audit assertion.** N/A (DSPM is a derived view; underlying assertion is the UAL event already captured in DLP-03).

**Evidence collected.** `1.13-DSPM-01-screenshot.png`, `1.13-DSPM-01-export.csv`.

#### 1.13-DSPM-02 — DSPM trend

**Objective.** Confirm DSPM trend view shows expected weekly cadence of test events (no gaps, no duplicates).

**Preconditions.** ≥4 weeks of test history.

**Steps.** Open DSPM trend view; export 4-week trend; reconcile against expected test execution log.

**Expected.** No unexplained gaps; no duplicates.

**Pass criteria.** Reconciliation log signed by Compliance Data Administrator.

**Audit assertion.** N/A.

**Evidence collected.** `1.13-DSPM-02-trend.csv`, `1.13-DSPM-02-reconciliation.md`.

### Audit operations (1.13-AUDIT-01..04)

#### 1.13-AUDIT-01 — SitCreated emission

**Objective.** Confirm `SitCreated` UAL event emits when a new custom SIT is created.

**Preconditions.** Audit Reader; Information Protection Admin (separate principal — see PRE-04).

**Steps.**
1. Information Protection Admin creates a temporary throwaway custom SIT named `1.13-audit-temp-{timestamp}`.
2. Audit Reader queries UAL for `SitCreated` filtered to the SIT name.
3. Information Protection Admin deletes the throwaway SIT (verifies `SitDeleted`).

**Expected.** Both `SitCreated` and `SitDeleted` events present.

**Pass criteria.** Events visible in UAL within firm-defined supervisory window; user principal name on event matches the Information Protection Admin who performed the action.

**Audit assertion.** `SitCreated` and `SitDeleted` events with correct `UserId`.

**Evidence collected.** `1.13-AUDIT-01-ual.json`.

#### 1.13-AUDIT-02 — EdmSchemaCreated emission

**Objective.** Confirm `EdmSchemaCreated` emits when a new EDM schema is uploaded.

**Preconditions.** Compliance Data Administrator; Audit Reader.

**Steps.** Compliance Data Administrator uploads a throwaway EDM schema (no real data) named `1.13-audit-edm-{timestamp}`; Audit Reader confirms event.

**Expected.** `EdmSchemaCreated` event present.

**Pass criteria.** Event present with correct `UserId`.

**Audit assertion.** `EdmSchemaCreated`.

**Evidence collected.** `1.13-AUDIT-02-ual.json`.

#### 1.13-AUDIT-03 — SitUpdated emission

**Objective.** Confirm `SitUpdated` emits when a custom SIT's confidence threshold or pattern is modified.

**Preconditions.** Same as AUDIT-01.

**Steps.** Information Protection Admin modifies the confidence band on a non-production custom SIT; Audit Reader confirms event.

**Expected.** `SitUpdated` event present.

**Pass criteria.** Event present with correct `UserId` and `ObjectId` referencing the SIT GUID.

**Audit assertion.** `SitUpdated`.

**Evidence collected.** `1.13-AUDIT-03-ual.json`.

#### 1.13-AUDIT-04 — DlpRuleMatch emission with CopilotInteraction correlation

**Objective.** Confirm `DlpRuleMatch` and `CopilotInteraction` events can be correlated for the same agent prompt (foundational for every other §4 test's audit assertion).

**Preconditions.** Any §4 BUILTIN/CUSTOM/EDM/TC test executed in the last hour.

**Steps.** Pull the most recent `CopilotInteraction` event; extract correlation field (e.g., `CorrelationId`, `SessionId`, `InteractionId` — verify exact field on Learn); pull `DlpRuleMatch` events filtered by the same correlation field.

**Expected.** ≥1 `DlpRuleMatch` event correlated to the `CopilotInteraction`.

**Pass criteria.** Correlation field matches in both events; pivot table of correlation field → event count is non-zero.

**Audit assertion.** Self-asserting (this test verifies the correlation mechanism itself).

**Evidence collected.** `1.13-AUDIT-04-correlation-pivot.csv`.

### Negative-path battery (1.13-NEG-01..05)

#### 1.13-NEG-01 — Schema drift

**Objective.** Detect a custom SIT whose XML in production no longer matches the version-controlled definition in the SIT-as-code repository.

**Preconditions.** SIT-as-code repository (e.g., Azure DevOps repo with exported SIT XML); read access to production SIT definitions via IPPS.

**Steps.**
1. Export current production SIT XML for every custom SIT: `Get-DlpSensitiveInformationType | Export-Clixml`.
2. Diff against the SIT-as-code repo HEAD.

**Expected.** Diff is empty.

**Pass criteria.** Empty diff (or every difference is associated with an approved change-control ticket).

**Audit assertion.** `SitUpdated` events in the diff window must each correspond to an approved ticket.

**Evidence collected.** `1.13-NEG-01-sit-diff.txt`, `1.13-NEG-01-ticket-list.csv`.

#### 1.13-NEG-02 — EDM hash mismatch

**Objective.** Detect EDM dataset whose hash digest no longer matches the hash recorded at last upload (indicates either a successful unauthorized re-upload or an Upload Agent failure).

**Preconditions.** EDM dataset hash recorded at last upload (recorded in `1.13-EDM-dataset-hash.txt` per `powershell-setup.md` §5).

**Steps.** Recompute hash of current source extract; compare to recorded hash.

**Expected.** Hash matches expected scheduled refresh hash; if changed, `EdmDataUploaded` event in UAL within last 24h corresponds to the new hash.

**Pass criteria.** Hash chain valid; every change correlated to an `EdmDataUploaded` event with a known `UserId`.

**Audit assertion.** `EdmDataUploaded` events in window correspond to known principals.

**Evidence collected.** `1.13-NEG-02-hash-chain.txt`.

#### 1.13-NEG-03 — Preview → GA classifier ID delta

**Objective.** Detect trainable-classifier or NER references in DLP policies that point to a preview GUID after Microsoft has promoted the classifier to GA (the GUID changes on promotion, silently breaking the policy match).

**Preconditions.** Inventory of all DLP policy references to trainable classifiers and NER classifiers (exported from `Get-DlpCompliancePolicy` / `Get-DlpComplianceRule`).

**Steps.**
1. Enumerate all classifier IDs referenced by policies.
2. For each, query the current classifier definition and confirm `IsPreview` / `LifecycleState` (verify exact field on Learn) is current.
3. Cross-check Microsoft Learn / Message Center for any classifier promoted preview→GA in the last 90 days; confirm policies were re-pointed to GA GUID.

**Expected.** Zero policies reference a deprecated preview GUID.

**Pass criteria.** Inventory clean; any deprecated reference is a finding.

**Audit assertion.** `DlpPolicyUpdated` (verify spelling) events in window for any re-pointing.

**Evidence collected.** `1.13-NEG-03-classifier-inventory.csv`.

#### 1.13-NEG-04 — Regex regression

**Objective.** Detect a custom SIT whose regex no longer matches a previously-known positive sample (indicates an unintended pattern edit or library upgrade behavior change).

**Preconditions.** Per-custom-SIT regression corpus stored at `tests/1.13/regression/{sit-name}/`.

**Steps.** For each custom SIT, run BUILTIN-style positive test against the regression sample.

**Expected.** All historical positives still match.

**Pass criteria.** Regression battery 100% pass.

**Audit assertion.** `DlpRuleMatch` per regression sample.

**Evidence collected.** `1.13-NEG-04-regression-results.csv`.

#### 1.13-NEG-05 — DLP-for-Copilot user-scope mistargeting

**Objective.** Detect DLP-for-Copilot policies scoped to a *user* group rather than the *agent identity* or *SharePoint site* hosting grounding sources (a common misconfiguration that produces silent non-enforcement).

**Preconditions.** Inventory of all DLP-for-Copilot policy scopes.

**Steps.**
1. Enumerate every DLP-for-Copilot policy: `Get-DlpCompliancePolicy | Where-Object { $_.Workload -like "*Copilot*" }` (verify property name on Learn).
2. For each, inspect the scope: it must reference an agent identity, agent group, or SharePoint site URL — **not** a user group.
3. Any policy scoped to a user group is a finding (unless explicitly approved as a user-targeted educate policy with documented justification).

**Expected.** Zero unjustified user-scoped policies.

**Pass criteria.** Inventory clean.

**Audit assertion.** N/A (configuration check).

**Evidence collected.** `1.13-NEG-05-policy-scope-inventory.csv`.

### Incident reproduction (1.13-IR-01)

#### 1.13-IR-01 — SIT misses real SSN in Copilot grounding (full reproduction)

**Objective.** Reproduce a real or hypothetical incident where a SIT failed to match an SSN-bearing document grounded by an agent. Used to validate root-cause analysis and to drive corrective-action SIT updates.

**Preconditions.** Contained eDiscovery workspace per Control 1.10; incident artifact present (real document with NPI, handled per firm's incident-handling SOP); Compliance Officer authorization on file.

**Steps.**
1. In the contained workspace, replay the original prompt against a copy of the agent configuration at the time of incident.
2. Capture the agent response and UAL events.
3. Identify which SIT, classifier, or policy *should* have matched and did not.
4. Document root cause: missing SIT? wrong confidence band? wrong policy scope (NEG-05)? preview classifier GUID drift (NEG-03)? EDM hash mismatch (NEG-02)?
5. Propose corrective action and create a change-control ticket.

**Expected.** Root cause identified and documented; corrective action proposed.

**Pass criteria.** Root-cause document signed by Compliance Officer; corrective-action ticket linked.

**Audit assertion.** `CopilotInteraction` from incident replay present in workspace audit log.

**Evidence collected.** `1.13-IR-01-rca.md`, `1.13-IR-01-corrective-action-ticket.txt`, `1.13-IR-01-replay-ual.json`.

---

## §5 Sovereign cloud variant matrix

> **Update cadence.** This matrix must be re-verified within 30 days of every test cycle (asserted by `1.13-PRE-07`). Sovereign feature parity is fluid; cells marked "Verify per release" indicate features that historically lag commercial GA. **Last verified: April 2026 (refresh on every test cycle).**

| Test class | Commercial | GCC | GCC High | DoD | Notes |
|------------|-----------|-----|----------|-----|-------|
| BUILTIN-01..08 (built-in SITs) | GA | GA | Verify per release | Verify per release | Built-in SIT *availability* is generally at parity; *new built-in SITs* lag in GCC High / DoD |
| CUSTOM-01..04 (custom SITs) | GA | GA | GA | GA | Customer-defined SITs portable across clouds |
| EDM-01..03 | GA | GA | Verify per release | Verify per release | Confirm EDM Upload Agent build supports the sovereign endpoint |
| NER-01..04 | GA | Verify per release | Verify per release | Not available (verify) | NER lags commercial; do not assume parity |
| TC-01..04 (trainable classifiers) | GA | Verify per release | Verify per release | Verify per release | Pre-trained classifier inventory differs by cloud |
| DLP-01..03 (DLP-for-Copilot) | GA | Verify per release | Verify per release | Verify per release | Copilot itself has differential availability |
| DSPM-01..02 | GA | Verify per release | Verify per release | Not available (verify) | DSPM for AI typically lags Copilot GA in sovereign clouds |
| AUDIT-01..04 | GA | GA | GA | GA | UAL operations available in all clouds; specific operation names may differ — verify on Learn |
| NEG-01..05 | N/A | N/A | N/A | N/A | Negative-path tests are tenant-internal and apply uniformly |
| IR-01 | GA | GA | GA | GA | Incident reproduction uses contained workspace per Control 1.10 |

**Sovereign endpoints.** PowerShell connections must use the sovereign-specific endpoint per [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) §3 (e.g., `Connect-IPPSSession -ConnectionUri https://ps.compliance.protection.office365.us/powershell-liveid/` for GCC High).

---

## §6 Evidence pack

### 6.1 Evidence manifest schema

Every test cycle produces a single `1.13-evidence-manifest.json` conforming to the schema below. The manifest is the canonical index into the evidence artifacts and is the file submitted to the supervisory examiner.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "FSI Control 1.13 Evidence Manifest",
  "type": "object",
  "required": [
    "controlId",
    "controlVersion",
    "tenantId",
    "sovereignCloud",
    "cycleId",
    "cycleStart",
    "cycleEnd",
    "executor",
    "approver",
    "tests",
    "manifestSha256"
  ],
  "properties": {
    "controlId": { "type": "string", "const": "1.13" },
    "controlVersion": { "type": "string", "pattern": "^v\\d+\\.\\d+(\\.\\d+)?$" },
    "tenantId": { "type": "string", "format": "uuid" },
    "sovereignCloud": {
      "type": "string",
      "enum": ["Commercial", "GCC", "GCCHigh", "DoD"]
    },
    "cycleId": { "type": "string" },
    "cycleStart": { "type": "string", "format": "date-time" },
    "cycleEnd": { "type": "string", "format": "date-time" },
    "executor": {
      "type": "object",
      "required": ["upn", "role"],
      "properties": {
        "upn": { "type": "string", "format": "email" },
        "role": {
          "type": "string",
          "enum": [
            "Information Protection Admin",
            "Purview Compliance Admin",
            "Compliance Data Administrator"
          ]
        }
      }
    },
    "approver": {
      "type": "object",
      "required": ["upn", "role"],
      "properties": {
        "upn": { "type": "string", "format": "email" },
        "role": {
          "type": "string",
          "enum": ["Compliance Officer", "CISO", "CRO"]
        }
      }
    },
    "tests": {
      "type": "array",
      "minItems": 38,
      "items": {
        "type": "object",
        "required": [
          "testId",
          "outcome",
          "executedAt",
          "evidenceArtifacts",
          "auditAssertion"
        ],
        "properties": {
          "testId": {
            "type": "string",
            "pattern": "^1\\.13-(PRE|BUILTIN|CUSTOM|EDM|NER|TC|DLP|DSPM|AUDIT|NEG|IR)-\\d{2}$"
          },
          "outcome": {
            "type": "string",
            "enum": ["pass", "fail", "blocked", "n/a"]
          },
          "executedAt": { "type": "string", "format": "date-time" },
          "evidenceArtifacts": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "object",
              "required": ["path", "sha256", "sizeBytes"],
              "properties": {
                "path": { "type": "string" },
                "sha256": {
                  "type": "string",
                  "pattern": "^[a-f0-9]{64}$"
                },
                "sizeBytes": { "type": "integer", "minimum": 0 }
              }
            }
          },
          "auditAssertion": {
            "type": "object",
            "required": ["operation", "verified"],
            "properties": {
              "operation": { "type": "string" },
              "verified": { "type": "boolean" },
              "correlationId": { "type": "string" }
            }
          },
          "notes": { "type": "string" }
        }
      }
    },
    "manifestSha256": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$",
      "description": "SHA-256 of the manifest file with this field set to all zeros, computed at finalization."
    }
  }
}
```

### 6.2 Manifest validator (`Invoke-EvidenceManifestValidation.ps1`)

```powershell
# Invoke-EvidenceManifestValidation.ps1
# Validates a 1.13 evidence manifest against schema, recomputes artifact hashes,
# and verifies the manifest's own SHA-256 self-hash.
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $ManifestPath,
    [Parameter(Mandatory)] [string] $SchemaPath,
    [Parameter(Mandatory)] [string] $EvidenceRoot
)

$ErrorActionPreference = 'Stop'

# 1. Load
$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$schema   = Get-Content $SchemaPath   -Raw

# 2. Schema validation (requires Test-Json with -SchemaFile, PS 7.4+)
if (-not (Test-Json -Json (Get-Content $ManifestPath -Raw) -SchemaFile $SchemaPath)) {
    throw "Schema validation failed for $ManifestPath"
}

# 3. Verify every artifact hash
$failures = @()
foreach ($test in $manifest.tests) {
    foreach ($artifact in $test.evidenceArtifacts) {
        $full = Join-Path $EvidenceRoot $artifact.path
        if (-not (Test-Path $full)) {
            $failures += "MISSING: $($test.testId) -> $($artifact.path)"
            continue
        }
        $actual = (Get-FileHash $full -Algorithm SHA256).Hash.ToLower()
        if ($actual -ne $artifact.sha256.ToLower()) {
            $failures += "HASH MISMATCH: $($test.testId) -> $($artifact.path) (expected $($artifact.sha256), got $actual)"
        }
    }
}

# 4. Verify the manifest self-hash
$tempCopy = [System.IO.Path]::GetTempFileName()
try {
    $copy = $manifest | ConvertTo-Json -Depth 50 | ConvertFrom-Json
    $recordedHash = $copy.manifestSha256
    $copy.manifestSha256 = '0' * 64
    ($copy | ConvertTo-Json -Depth 50) | Set-Content -Path $tempCopy -NoNewline
    $recomputed = (Get-FileHash $tempCopy -Algorithm SHA256).Hash.ToLower()
    if ($recomputed -ne $recordedHash.ToLower()) {
        $failures += "MANIFEST SELF-HASH MISMATCH: expected $recordedHash, got $recomputed"
    }
} finally {
    Remove-Item $tempCopy -ErrorAction SilentlyContinue
}

# 5. Coverage assertion
$expectedIds = @(
  ('PRE',     1..7),
  ('BUILTIN', 1..8),
  ('CUSTOM',  1..4),
  ('EDM',     1..3),
  ('NER',     1..4),
  ('TC',      1..4),
  ('DLP',     1..3),
  ('DSPM',    1..2),
  ('AUDIT',   1..4),
  ('NEG',     1..5),
  ('IR',      1..1)
) | ForEach-Object {
    $prefix = $_[0]
    $_[1] | ForEach-Object { '1.13-{0}-{1:00}' -f $prefix, $_ }
}
$presentIds = $manifest.tests.testId
$missing = $expectedIds | Where-Object { $_ -notin $presentIds }
if ($missing.Count -gt 0) {
    $failures += "MISSING TEST IDS: $($missing -join ', ')"
}

if ($failures.Count -gt 0) {
    Write-Error ($failures -join "`n")
    exit 1
}
Write-Host "OK: manifest valid; $($manifest.tests.Count) tests; all hashes verified."
exit 0
```

### 6.3 Manifest builder

Builder pattern (sketch — full implementation in `powershell-setup.md` §8):

```powershell
# Build-EvidenceManifest.ps1 (sketch)
$manifest = [ordered]@{
    controlId       = '1.13'
    controlVersion  = 'v1.4'
    tenantId        = (Get-MgContext).TenantId
    sovereignCloud  = $env:FSI_SOVEREIGN_CLOUD  # 'Commercial' | 'GCC' | 'GCCHigh' | 'DoD'
    cycleId         = "1.13-cycle-$(Get-Date -Format 'yyyyMMdd-HHmm')"
    cycleStart      = (Get-Date).ToUniversalTime().ToString('o')
    cycleEnd        = $null
    executor        = @{ upn = $env:FSI_EXECUTOR_UPN; role = $env:FSI_EXECUTOR_ROLE }
    approver        = @{ upn = $env:FSI_APPROVER_UPN; role = $env:FSI_APPROVER_ROLE }
    tests           = @()
    manifestSha256  = '0' * 64
}
# ... append per-test entries with hashes ...
# At end: $manifest.cycleEnd = ...; compute self-hash; write file.
```

### 6.4 Evidence artifacts (per cycle)

| Artifact | Origin | Format | Retention |
|----------|--------|--------|-----------|
| `1.13-evidence-manifest.json` | `Build-EvidenceManifest.ps1` | JSON | 6 years (FINRA 4511) — WORM |
| `1.13-{testId}-ual.json` | `Search-UnifiedAuditLog` exports | JSON | 6 years — WORM |
| `1.13-{testId}-screenshot.png` | Portal capture | PNG | 6 years — WORM |
| `1.13-{testId}-agent-response.txt` | Test transcript | UTF-8 | 6 years — WORM |
| `1.13-corpus-manifest.json` | Repo-controlled | JSON | Source control retention |
| `1.13-PRE-04-role-matrix.csv` | `Get-MgDirectoryRole` export | CSV | 6 years — WORM |
| `1.13-NEG-01-sit-diff.txt` | `git diff` of SIT-as-code | Text | Source control retention |

### 6.5 Retention and WORM placement

Evidence is retained per **FINRA Rule 4511** (general books and records, 6 years) and **SEC Rule 17a-4(f)** (WORM media or electronic equivalent with required attestations). The evidence root must be either: (a) an immutable Azure Storage container with time-based retention policy locked, (b) an Azure Data Lake with `Immutable` policy applied, or (c) a third-party WORM-attested archive. The path and storage account ID are recorded once per tenant in `docs/reference/evidence-retention.md` (firm-specific) and referenced by every cycle's manifest via `evidenceRoot` metadata in the executor's run log.

**Do not** treat Content Explorer screenshots as primary evidence; they are supplementary. Primary evidence is the UAL JSON export and the manifest entry hashing it.

---

## §7 Attestation block

The attestation below is signed at the end of every test cycle. RACI alignment: Compliance Officer is **Accountable**, Information Protection Admin (or Purview Compliance Admin executing the cycle) is **Responsible**, CISO is **Consulted**, Internal Audit is **Informed**.

```
=============================================================
FSI Control 1.13 — Verification Cycle Attestation
=============================================================
Control ID:           1.13
Control Version: v1.6.2
Tenant ID:            ____________________________________
Sovereign Cloud:      [ ] Commercial  [ ] GCC  [ ] GCC High  [ ] DoD
Cycle ID:             ____________________________________
Cycle Start (UTC):    ____________________________________
Cycle End (UTC):      ____________________________________
Manifest SHA-256:     ____________________________________
Validator Run Log:    ____________________________________ (path)
Evidence Root (WORM): ____________________________________

Test Counts:
  Pre-flight (PRE-01..07)              passed: ___ / 7
  Built-in SITs (BUILTIN-01..08)       passed: ___ / 8
  Custom SITs (CUSTOM-01..04)          passed: ___ / 4
  EDM (EDM-01..03)                     passed: ___ / 3
  NER (NER-01..04)                     passed: ___ / 4
  Trainable Classifiers (TC-01..04)    passed: ___ / 4
  DLP-for-Copilot (DLP-01..03)         passed: ___ / 3
  DSPM for AI (DSPM-01..02)            passed: ___ / 2
  Audit operations (AUDIT-01..04)      passed: ___ / 4
  Negative path (NEG-01..05)           passed: ___ / 5
  Incident reproduction (IR-01)        passed: ___ / 1
                                       TOTAL : ___ / 45

Findings opened this cycle: ____
Findings closed this cycle: ____
Open findings carried:      ____

-------------------------------------------------------------
Responsible (Executor)
  Name:       ____________________________________________
  Role:       [ ] Information Protection Admin
              [ ] Purview Compliance Admin
              [ ] Compliance Data Administrator
  UPN:        ____________________________________________
  Signature:  ____________________________________________
  Date (UTC): ____________________________________________

Accountable (Approver)
  Name:       ____________________________________________
  Role:       Compliance Officer
  UPN:        ____________________________________________
  Signature:  ____________________________________________
  Date (UTC): ____________________________________________

Consulted (Security)
  Name:       ____________________________________________
  Role:       CISO (or designated Security Officer)
  UPN:        ____________________________________________
  Signature:  ____________________________________________
  Date (UTC): ____________________________________________

Informed (Audit)
  Name:       ____________________________________________
  Role:       Internal Audit / Audit Manager
  UPN:        ____________________________________________
  Acknowledged (Date UTC): ___________________________________
-------------------------------------------------------------

I attest that the verification cycle described above was
executed in accordance with the firm's WSPs (FINRA Rule 3110)
and that the evidence artifacts referenced by the manifest
hash above are complete, unaltered, and stored on WORM media
per FINRA Rule 4511 / SEC Rule 17a-4(f). I further attest
that no operator-mediated waits were substituted for audit-
event verification, that no real customer NPI was used in
synthetic testing, and that the sovereign-cloud parity matrix
(§5) was re-verified within 30 days of cycle start.
=============================================================
```

> **Single-role attestation is a finding.** A cycle signed only by the Executor (without Compliance Officer counter-signature) does not satisfy the control. See §8 Anti-Pattern #14.

---

## §8 Anti-patterns

The following 15 patterns are **non-conformance** to Control 1.13 and must be remediated before the cycle can be signed.

1. **Synthetic-only testing without real-incident replay.** No `1.13-IR-01` execution against an actual past incident or hypothetical incident artifact within the last 12 months.
2. **Ignoring confidence bands.** Treating any positive `DlpRuleMatch` as a pass without recording the `Confidence` field and reconciling against the policy's configured band.
3. **No false-positive corpus.** Every `*-positive-*` test executed without the matching `*-negative-*` test.
4. **Inline test data in playbook prose.** Test SSNs, PANs, or account numbers pasted into Markdown rather than referenced from `tests/1.13/corpus/` with hash manifest.
5. **Fabricated SLAs.** Phrases such as "wait 24 hours for indexing" outside the §3 table of Microsoft-published windows.
6. **Numeric thresholds in policy UX prose.** Documenting "≥85 = High" as if it were a Microsoft universal rule rather than a per-SIT XML `confidenceLevel` attribute.
7. **EDM with no near-miss test.** EDM classifiers deployed to Zone 3 without `1.13-EDM-02` having ever been run.
8. **DLP-for-Copilot user-scope mistargeting.** Policies scoped to user groups instead of agent identities or grounding-source SharePoint sites (detected by `1.13-NEG-05`).
9. **Training trainable classifiers with production documents.** Seed sites containing real customer NPI (violates Control 1.7 secure-handling and OCC Bulletin 2026-13 (formerly OCC 2011-12) model-risk standards).
10. **Skipping the preview → GA classifier ID re-pointing check.** Policies left referencing preview GUIDs after Microsoft has GA'd the classifier (detected by `1.13-NEG-03`).
11. **Screenshots without manifest hash entry.** Evidence files present in the evidence root but absent from the manifest's `evidenceArtifacts` list (validator will fail).
12. **No sovereign-cloud parity check.** Reusing a Commercial-tenant attestation in GCC / GCC High / DoD without §5 re-verification (detected by `1.13-PRE-07`).
13. **Operator-mediated waits substituted for audit-event verification.** "We waited 2 hours and re-tested" with no UAL event capture.
14. **Single-role attestation.** Cycle signed only by Executor, without Compliance Officer counter-signature.
15. **Treating Content Explorer screenshots as primary audit evidence.** Content Explorer is a derived view; primary evidence is the UAL JSON export of `DlpRuleMatch` / `CopilotInteraction` events with correlation IDs.

---

## §9 Cross-links

- **Sibling 1.13 playbooks**
  - [`portal-walkthrough.md`](portal-walkthrough.md) — portal configuration steps for SITs, EDM, classifiers, DLP-for-Copilot
  - [`powershell-setup.md`](powershell-setup.md) — module pinning, IPPS connect, EDM Upload Agent, manifest builder
  - `troubleshooting.md` — common failure modes for the tests in this catalog (sibling playbook — pending publication)
- **Shared baseline**
  - [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) — pinned module versions and sovereign endpoints
- **Related controls**
  - Control 1.5 — Role separation (audited by `1.13-PRE-04`)
  - Control 1.6 — Information Protection labels (downstream consumer of SITs)
  - Control 1.7 — Secure handling of training data (gates trainable classifier deployment)
  - Control 1.10 — eDiscovery and incident workspace containment (used by `1.13-IR-01`)
  - Control 4.6 — Agent identity inventory (referenced by DLP-for-Copilot scoping in `1.13-DLP-*` and `1.13-NEG-05`)
- **Framework**
  - AI Incident Response Playbook — invoked by `1.13-IR-01`
  - FSI Governance Gate (control spec §3) — gates trainable-classifier deployment per OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
