# Verification & Testing — Control 1.13: Sensitive Information Types and Pattern Recognition

> **Scope.** Operational verification procedures for Control 1.13 classification and its supported policy consumers in US financial-services tenants. Microsoft 365 Copilot controls do not establish equivalent coverage for every Copilot Studio agent, Power Platform connector, or grounding source.
> **Audience.** Microsoft 365 administrators, Purview engineers, internal auditors, and supervisory examiners at FINRA member firms, SEC-registered investment advisers, OCC/FRB-supervised banks, and CFTC-registered swap dealers.
> **Cross-links.** [Portal walkthrough](portal-walkthrough.md) · [PowerShell setup](powershell-setup.md) · [Troubleshooting](troubleshooting.md) · [Shared PowerShell baseline](../../_shared/powershell-baseline.md)
> **Last Verified:** 2026-10-16 — Microsoft Learn documentation review only; no tenant, PowerShell-session, or UI tests performed.
> **Last UI Verified.** April 2026 (historical record, not reverified).

---

## What this verification catches

Verification of SIT and pattern-recognition coverage exists to surface failure modes that produce silent NPI exposure through agent grounding. The following ten failure modes are explicit targets of this playbook:

1. **Detection mistaken for grounding enforcement.** SIT prompt restriction evaluates typed prompt text, not the contents of grounding files. File/email exclusion uses a sensitivity-label condition in a separate rule. Detected by `1.13-DLP-01..03` and `1.13-IR-01`.
2. **EDM configurable-match mismatch.** Case and delimiters can be intentionally ignored; the primary SIT must still extract the full value. Detected by `1.13-EDM-02`.
3. **Classifier lifecycle drift.** A policy references an unavailable or replaced classifier. A GUID change on every Preview-to-GA promotion is not a documented general rule. Detected by `1.13-NEG-03`.
4. **DLP-for-Copilot scope gap.** The initiating user's policy scope, exclusions, or supported Copilot experience do not cover the test. User targeting is valid; an agent GUID or SharePoint URL is not a substitute for that scope. Detected by `1.13-NEG-05`.
5. **Fabricated SLA reliance.** A runbook says "wait 24 hours for SIT indexing" without a Microsoft-published basis, so testers prematurely declare a pass. Mitigated by §3 (Documented processing windows) which cites only Microsoft-published windows feature-by-feature.
6. **Confidence mapping mistaken for arbitrary firm-defined bands.** Microsoft maps numeric confidence ≤65 to Low, 66–75 to Medium, and 76–100 to High. Which patterns exist and which evidence they require remain SIT-specific. Detected during `1.13-CUSTOM-01..04` review.
7. **No negative corpus.** Only positive matches are tested, so false-positive rate is unknown and Zone 3 block actions create denial-of-service to legitimate agent queries. Detected by every `*-NEG-*` and the `-negative-` half of each pair.
8. **EDM hash drift.** The EDM Upload Agent runs against a stale schema or stale source extract, producing a hash set that no longer matches production data. Detected by `1.13-NEG-02`.
9. **Missing deployment evidence.** A successful local text test is mistaken for stored-file classification, policy enforcement, or retained interaction content. Detected by `1.13-PRE-07`.
10. **Trainable classifier without OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) model-risk evidence.** A custom trainable classifier is deployed without documented training-data lineage, validation set, or model-risk sign-off, breaching the FSI Governance Gate defined in the control spec. Detected by `1.13-TC-01..04`.

---

## §1 Verification cadence

Cadence is **firm-defined** under WSPs (FINRA Rule 3110) and supervisory procedures. Microsoft does not publish a verification cadence for SIT or DLP correctness. The table below is the minimum recommended cadence for FSI tenants; firms may shorten any interval based on risk.

| Cadence | Test scope | Owner (Responsible) | Owner (Accountable) | Regulatory driver |
|---------|------------|---------------------|---------------------|-------------------|
| **Daily** | UAL sampling (`1.13-AUDIT-01..04`); DLP alert queue triage | Purview Compliance Admin | Compliance Officer | FINRA 3110(b), SEC 17a-4(f), SOX ITGC |
| **Weekly** | DLP-for-Copilot match review (`1.13-DLP-01..03`); DSPM for AI surfacing (`1.13-DSPM-01..02`) | Information Protection Admin | CISO | GLBA Safeguards 314.4(d); OCC Heightened Standards |
| **Monthly** | Full BUILTIN (`1.13-BUILTIN-01..08`) and CUSTOM (`1.13-CUSTOM-01..04`) regression with positive + negative corpus | Information Protection Admin | Compliance Officer | FINRA 3110, SEC Reg S-P |
| **Quarterly** | EDM (`1.13-EDM-01..03`), Trainable Classifier (`1.13-TC-01..04`), NER (`1.13-NER-01..04`), Negative-path battery (`1.13-NEG-01..05`)
| **On change** | Any test affected by a tenant change (new SIT, EDM schema rotation, DLP rule edit, classifier promotion preview→GA, role-group change) | Purview Compliance Admin | Compliance Officer | SOX ITGC change-control |
| **On incident** | `1.13-IR-01` controlled reproduction with an approved surrogate; preserve the original under authorized eDiscovery custody (not an execution sandbox) | Incident Response Lead + Compliance Data Administrator | CISO + Compliance Officer | SEC Reg S-P §248.30; state breach laws; NYDFS 500.17 |

**RACI note.** Accountable role per RACI may not match the role with admin permissions. The Compliance Officer is accountable but does not hold Purview Compliance Admin rights; reconcile separation with the role catalog and the firm's policy at `1.13-PRE-04`. Control 1.5 covers DLP and sensitivity labels, not role separation.

---

## §2 Pre-flight (1.13-PRE-01..07)

Pre-flight tests must pass **before** any §4 test is executed. A failed pre-flight blocks the entire verification cycle and is itself a finding.

### 1.13-PRE-01 — License entitlement

**Objective.** Confirm that the tenant holds the licenses required for every detection primitive in scope.

**Preconditions.** Entra Global Reader or License Administrator role; access to `admin.cloud.microsoft` → Billing → Licenses.

**Steps.**
1. In Microsoft 365 admin center, navigate to **Billing → Licenses**.
2. Verify the entitlement for each selected feature against the [Microsoft Purview service description](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description). Advanced classification and the consuming DLP, auto-labeling, DSPM, and eDiscovery features have distinct licensing requirements. Check the actual Microsoft 365 Copilot or Copilot Chat experience; a paid Copilot license is not a universal prerequisite for Copilot Chat.
3. Record SKU GUIDs, enabled service plans, assigned test-user licenses, and feature/rollout availability. Tenant SKU inventory alone does not prove user entitlement. For Audit retention beyond 180 days, check the generating user's eligible license and applicable record-type retention policy; multi-year retention additionally requires the appropriate retention add-on. Copilot records do not automatically inherit E5's default one-year policy for Entra ID, Exchange, OneDrive, and SharePoint records; configure an applicable custom audit policy where needed.

**Expected.** Each test user and selected capability has documented entitlement; do not assign human-user SKU requirements to every agent identity.

**Pass criteria.** Tenant SKU, relevant service plans, assigned-user entitlement, and selected feature availability verified and captured.

**Audit assertion.** None — license check is not a UAL-emitting event. Evidence is the captured admin-center state.

**Evidence collected.** `1.13-PRE-01-licenses.json` (output of `Get-MgSubscribedSku | Select-Object SkuPartNumber, ConsumedUnits, PrepaidUnits`), `1.13-PRE-01-screenshot.png`.

### 1.13-PRE-02 — Unified Audit Log enabled

**Objective.** Confirm UAL ingestion is enabled and that the operations referenced by `1.13-AUDIT-*` are emitted by the tenant.

**Preconditions.** Audit Reader or Audit Manager role.

**Steps.**
1. Open `purview.microsoft.com` → **Audit**.
2. Confirm the banner does not state "Start recording user and admin activity".
3. In **Audit → Search**, use a known activity by the test user in a bounded UTC window. Enter exact documented operation names, such as `CopilotInteraction`, in **Activities - operations names**; dropdown autocomplete is not an audit coverage test. For enabled-state verification, run `Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled` in **Exchange Online PowerShell**, not IPPS (where that property can misleadingly return False).
4. Export results to CSV.

**Expected.** Ingestion is enabled and a known, supported activity is returned. Audit availability is not immediate.

**Pass criteria.** Enabled-state output, search criteria, known activity, and CSV are captured. Empty results alone are inconclusive.

**Audit assertion.** N/A (this test verifies UAL itself).

**Evidence collected.** `1.13-PRE-02-ual-search.csv`, `1.13-PRE-02-screenshot.png`.

> **Audit contract.** `SitCreated`, `SitUpdated`, `SitDeleted`, `EdmSchemaCreated`, `EdmSchemaUpdated`, and `EdmDataUploaded` are not established operation names in the cited audit catalog. Do not make them pass conditions. Capture administrative cmdlet activity where supported and observed, plus before/after configuration and EDM Upload Agent session evidence. See [Audit search](https://learn.microsoft.com/en-us/purview/audit-search) and [Copilot audit properties](https://learn.microsoft.com/en-us/purview/audit-copilot).

### 1.13-PRE-03 — PowerShell modules pinned

**Objective.** Confirm verifier workstation has the pinned module versions defined in the shared baseline.

**Preconditions.** Workstation with PowerShell 7.4+; access to PSGallery.

**Steps.** Follow the [shared PowerShell baseline](../../_shared/powershell-baseline.md). Record installed/imported versions and a compatible runtime: `ExchangeOnlineManagement` 3.5.0–3.9.2 requires PowerShell 7.4+, while 3.10.0+ requires 7.6+ in PowerShell 7 ([compatibility matrix](https://learn.microsoft.com/en-us/powershell/exchange/exchange-online-powershell-v2)). Record needed Graph submodules. PnP, Graph Beta, and Power Apps modules are optional when separate tests need them. Use `Get-Module -ListAvailable` for installed modules and `Get-Module` for imported modules; IPPS is not currently supported on PowerShell 7 Linux/macOS.

**Expected.** Only the modules required for the cycle are installed and imported at approved, compatible versions.

**Pass criteria.** Module table matches baseline; no module is at "latest" / unpinned.

**Audit assertion.** N/A.

**Evidence collected.** `1.13-PRE-03-modules.json`.

### 1.13-PRE-04 — Role separation

**Objective.** Confirm SIT-management, DLP-management, and audit-review roles are held by separate principals; reconcile the role catalog and the firm's separation-of-duties policy.

**Preconditions.** Directory membership read permissions plus the relevant Purview role-group membership read permissions; Entra Global Reader alone does not establish both.

**Steps.**
1. Enumerate members of: **Information Protection Admin**, **Purview Compliance Admin**, **Compliance Data Administrator**, **Audit Manager**.
2. Confirm no single human principal holds more than one of {Information Protection Admin, Purview Compliance Admin, Audit Manager}.
3. Confirm no service principal holds Information Protection Admin without an approved exception ticket.

**Expected.** Each role group has ≥1 member; no overlap among the three sensitive groups.

**Pass criteria.** Membership matrix exported; overlap check passes.

**Audit assertion.** This is a read-only membership check. Directory roles and Purview role groups are distinct; capture each relevant membership and PIM activation. Do not assume one universal operation name covers both.

**Evidence collected.** `1.13-PRE-04-role-matrix.csv`.

### 1.13-PRE-05 — EDM Upload Agent installed and IPPS connectivity

**Objective.** Confirm the EDM Upload Agent is installed and the administrator can open Security & Compliance PowerShell (IPPS). Agent authorization is a separate documented work/school-user flow, not an IPPS session.

**Preconditions.** Approved hardened workstation; relevant Purview permissions and EDM_DataUploaders membership for upload/session operations.

**Steps.**
1. On the EDM workstation, confirm `EdmUploadAgent.exe` is present at the documented install path.
2. Run `Connect-IPPSSession`.
3. Run `Get-DlpEdmSchema` and confirm the existing schema list returns without error.

**Expected.** Agent present; IPPS session established; schema list returned.

**Pass criteria.** Agent version recorded; `Get-DlpEdmSchema` returns ≥1 schema (or `0` if none yet defined — record either way).

**Audit assertion.** No mutation is performed. Capture schema inventory and, for an existing data store, `EdmUploadAgent.exe /GetDataStore` and `/GetSession /DataStoreName <name>` output separately; schema existence does not prove data upload or indexing.

**Evidence collected.** `1.13-PRE-05-edm-agent-version.txt`, `1.13-PRE-05-schema-list.json`.

### 1.13-PRE-06 — Test corpus staged with SHA-256 manifest

**Objective.** Confirm the firm-maintained synthetic positive + negative test corpus and its SHA-256 manifest are available. `tests/1.13/corpus/` is a suggested path, not a fixture pack shipped by this repository.

**Preconditions.** Repository checkout; `Get-FileHash` available.

**Steps.**
1. List corpus directory: `Get-ChildItem tests/1.13/corpus/ -Recurse -File`.
2. Verify naming convention `1.13-{TYPE}-{positive|negative}-{NNN}.{ext}` (e.g., `1.13-SSN-positive-001.txt`, `1.13-CC-negative-014.docx`).
3. Recompute SHA-256 for every file and compare to the firm's `1.13-corpus-manifest.json`.
4. Confirm the corpus contains **no** real customer NPI. Do not assume reserved SSNs or payment test PANs are positive matches: the SSN detector has format/context requirements and the credit-card SIT explicitly excludes reserved test numbers. Prevalidate approved synthetic examples in the classifier before setting expected policy outcomes.

**Expected.** Every corpus file present; every SHA-256 matches manifest; no real NPI.

**Pass criteria.** Hash diff is empty; manual sample of 10 files confirms synthetic content.

**Audit assertion.** N/A.

**Evidence collected.** `1.13-PRE-06-corpus-hash-diff.txt`.

### 1.13-PRE-07 — Deployment and evidence boundaries

Record the initiating user, host/app, agent type, policy/rule IDs, mode, scope, classifier IDs, labels, and supported workload for each test. A text-classification pass is not a stored-file or Copilot-enforcement pass. Existing SharePoint/OneDrive content may need reclassification; an EDM text test does not refresh historical file classification.

For retention tests, record the policy location, user mailbox, retention start/expiry, applicable holds, and eDiscovery results. Newly created AI retention policies use **Microsoft Copilot experiences**, separate from Teams chats. Prompts/responses are copied into hidden user-mailbox folders; visible chat history is not retention evidence. A timer typically runs in 1–7 days, and items remain in SubstrateHolds for at least one day before eligible permanent deletion. Litigation Hold, delay hold, eDiscovery hold, and another applicable retention policy can suspend deletion. Audit-log retention and content retention are separate controls. [Retention for Copilot & AI apps](https://learn.microsoft.com/en-us/purview/retention-policies-copilot).

**Pass criteria.** Capture the deployment inventory and evidence access. Mark unavailable features `blocked` or justified `n/a`; do not invent successful UI tests or treat an eDiscovery case as an isolated Copilot execution environment.


## §3 Documented processing windows

These are feature-specific documented expectations, not contractual SLAs. Record observed readiness and results; elapsed time alone is not a pass, and an administrative audit event alone does not prove runtime readiness.

| Feature | Microsoft-published window | Source anchor (verify at execution) | Test usage |
|---------|---------------------------|-------------------------------------|------------|
| DLP-for-Copilot policy update | Up to four hours | [Copilot DLP availability](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about#availability) | `1.13-DLP-01..03` |
| Trainable classifier seed-site indexing (initial) | At least 1 hour | `learn.microsoft.com/purview/classifier-learn-about` | `1.13-TC-01..04` |
| DSPM for AI (classic) new policies/reporting | Allow at least 24 hours; not a maximum event-delivery SLA | [Classic DSPM for AI](https://learn.microsoft.com/en-us/purview/dspm-for-ai) | `1.13-DSPM-01..02`; record whether classic or new DSPM is used |
| EDM schema additions | 10–60 minutes | [Create EDM schema](https://learn.microsoft.com/en-us/purview/sit-get-started-exact-data-match-create-schema) | `1.13-EDM-03` |
| EDM test readiness | Test an hour after upload and indexing complete; wait at least an hour after EDM SIT changes | [Test EDM](https://learn.microsoft.com/en-us/purview/sit-get-started-exact-data-match-test) | `1.13-EDM-01..03` |
| Custom SIT on existing SharePoint/OneDrive content | Existing content must be recrawled; no universal fixed window | [Create custom SIT](https://learn.microsoft.com/en-us/purview/sit-create-a-custom-sensitive-information-type) | `1.13-CUSTOM-01..04` |
| Audit record availability | Typically 60–90 minutes for core services; other services can take longer, with no committed specific time | [Audit search](https://learn.microsoft.com/en-us/purview/audit-search) | `1.13-AUDIT-*`; record incomplete searches |

> **Anti-pattern.** Waiting is not evidence of enforcement. Preserve classification results, policy state, runtime outcomes, and applicable telemetry. A bounded search with no event is inconclusive without a positive control and demonstrated ingestion coverage.

---

## §4 Test catalog

Every test below uses the structure: **Objective · Preconditions · Steps · Expected · Pass criteria · Audit assertion · Evidence collected.** Test IDs are stable and referenced by the evidence manifest (§5) and the attestation block (§6).

### Classification and enforcement are separate tests

For BUILTIN, CUSTOM, EDM, NER, TC, and regex regression tests, first test detection in the Purview classifier's **Test** workflow or, for text SIT tests, `Test-DataClassification -ClassificationNames <name-or-guid> -TextToClassify (Get-Content <synthetic-text-file> -Raw)`. Save `ClassificationResults`; do not assume undocumented result-property names. Binary-document tests use portal file upload, not invented `-DocumentData`, `-DocumentName`, or `-TestTextFile` parameters. Then test each supported consuming workload separately, recording scope, mode, count, and confidence.

The [Microsoft 365 Copilot and Copilot Chat location](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about) distinguishes:

- **Typed prompt text:** out-of-the-box and custom SITs with **Prevent Copilot from processing content → Processing prompts** (preview, tenant rollout dependent). This does not scan uploaded file contents or grounding files.
- **External web search:** SITs in typed prompts can restrict **Performing Web Searches** while permitted internal grounding can still produce a response.
- **Grounding files/emails:** a **Sensitivity labels** condition with **Prevent Copilot from processing content**, in a separate rule from SIT conditions. Excluded items can still appear as citations. Emails must have been sent on or after January 1, 2025; calendar invites are unsupported. In Word, Excel, and PowerPoint evaluation occurs at file open; reopen after applying a label mid-session.

Do not infer EDM, fingerprint, NER, or trainable-classifier prompt support from another DLP location. Record documented/selectable types; use supported source-workload DLP/auto-labeling and a separate label-based Copilot rule where needed. Copilot Studio connector policies are a separate boundary.

**Test prerequisites and artifact naming.** Microsoft documents at least one Exchange Online license in the tenant for SIT testing. Keep direct classifier evidence distinct from telemetry. Legacy artifact names below containing `ual` do not make classifier output an audit record: record each file's actual origin/type, and save available UAL exports separately. The corpus/regression paths are firm-maintained examples, not shipped fixtures.

### Built-in SITs (1.13-BUILTIN-01..08)

#### 1.13-BUILTIN-01 — US SSN positive

**Objective.** Confirm the SSN SIT detects approved synthetic text at the intended confidence.

**Preconditions.** PRE-01..07 passed; `1.13-SSN-positive-001.txt` prevalidated against the [SSN definition](https://learn.microsoft.com/en-us/purview/sit-defn-us-social-security-number). High uses formatted pre-2011 function matches plus an SSN keyword within 300 characters; unformatted and randomized functions have different confidence levels. Reserved/example numbers are not automatically High-confidence positives.

**Steps.**
1. Test synthetic file/text in the classification workflow above.
2. Record SIT identity, count, confidence, and context.
3. Test the source-workload consumer separately; use DLP-03 for Copilot enforcement.

**Expected.** Detection at the documented confidence, not automatic grounding exclusion or response redaction.

**Pass criteria.** Identity/count/confidence match the corpus expectation and separately tested consumer threshold.

**Audit assertion.** Save classification output and applicable consumer telemetry. Direct classification does not require a paired `DlpRuleMatch`/`CopilotInteraction`.

**Evidence collected.** `1.13-BUILTIN-01-ual.json`, `1.13-BUILTIN-01-agent-response.txt`, `1.13-BUILTIN-01-file-hash.txt`.

#### 1.13-BUILTIN-02 — US SSN negative

**Objective.** Confirm the SSN SIT does **not** match a non-SSN nine-digit string (e.g., a phone-number-shaped value) — guards against false-positive denial-of-service.

**Preconditions.** Same as BUILTIN-01.

**Steps.** Repeat BUILTIN-01 substituting `1.13-SSN-negative-001.txt` (e.g., `(987) 654-3201` or random digit string failing SSA range rules).

**Expected.** No SSN detection at the tested threshold.

**Pass criteria.** Direct negative result with a successful paired positive control.

**Audit assertion.** Save the negative classification result; missing policy telemetry alone is not a negative pass.

**Evidence collected.** `1.13-BUILTIN-02-ual-negative.json`.

#### 1.13-BUILTIN-03 — US Bank Account positive

**Objective.** Confirm bank-account detection: 6–17 consecutive digits with a bank-account keyword within 300 characters, at Medium confidence. No checksum or ABA routing number is required. [Definition](https://learn.microsoft.com/en-us/purview/sit-defn-us-bank-account-number).

**Preconditions.** PRE-01..07 passed; synthetic file `1.13-USBANK-positive-001.txt` includes context; consumer threshold does not demand a nonexistent High pattern.

**Steps.** Classify the corpus; test the supported consumer separately.

**Expected.** Medium-confidence match; notification behavior depends on the consumer.

**Pass criteria.** Detection and consumer result agree with the recorded expectations.

**Audit assertion.** Save actual telemetry, not fabricated `Action` values or correlation fields.

**Evidence collected.** `1.13-BUILTIN-03-ual.json`, `1.13-BUILTIN-03-banner-screenshot.png`.

#### 1.13-BUILTIN-04 — US Bank Account negative

**Objective.** Confirm no detection for an out-of-pattern value or an in-format number without the required keyword. ABA checksum failure is not a valid negative oracle.

**Preconditions.** Same as BUILTIN-03.

**Steps.** Substitute `1.13-USBANK-negative-001.txt`.

**Expected.** No bank-account classifier match.

**Pass criteria.** Direct negative result with a paired positive control.

**Audit assertion.** Save direct classification output and applicable consumer evidence.

**Evidence collected.** `1.13-BUILTIN-04-ual-negative.json`.

#### 1.13-BUILTIN-05 — Credit Card positive (Luhn-valid)

**Objective.** Confirm credit-card detection on approved synthetic, non-reserved positives: 14–19 digits, supported brand format, and Luhn validation. Reserved payment test numbers are excluded, so `4111-1111-1111-1111` is not a reliable positive. High requires context within 300 characters; Low does not. [Definition](https://learn.microsoft.com/en-us/purview/sit-defn-credit-card-number).

**Preconditions.** PRE-01..07 passed; prevalidated synthetic positive; separate consumer configured for intended alert behavior.

**Steps.** Classify `1.13-CC-positive-001.txt`, then test the consumer and capture configured DLP alerts.

**Expected.** Detection at the intended confidence; alert behavior verified separately.

**Pass criteria.** Detection agrees with the corpus expectation; consumer evidence identifies the actual rule.

**Audit assertion.** Save classification and actual consumer/alert records.

**Evidence collected.** `1.13-BUILTIN-05-ual.json`, `1.13-BUILTIN-05-alert-id.txt`.

#### 1.13-BUILTIN-06 — Credit Card negative (Luhn-invalid)

**Objective.** Confirm CC SIT does not match a 16-digit string failing Luhn checksum.

**Preconditions.** Same as BUILTIN-05.

**Steps.** Substitute `1.13-CC-negative-001.txt` by altering the prevalidated positive's checksum, retaining context.

**Expected.** No credit-card classifier match.

**Pass criteria.** Direct negative result with the paired positive control.

**Audit assertion.** Save the direct result; event absence alone is not proof.

**Evidence collected.** `1.13-BUILTIN-06-ual-negative.json`.

#### 1.13-BUILTIN-07 — ITIN positive

**Objective.** Confirm ITIN detection against the [Microsoft definition](https://learn.microsoft.com/en-us/purview/sit-defn-us-individual-taxpayer-identification-number): nine digits beginning with 9, fourth/fifth digits 50–65, 70–88, 90–92, or 94–99. High requires formatted text and a keyword within 300 characters; Medium uses unformatted text with context.

**Preconditions.** Zone 3 policy with ITIN SIT at High confidence.

**Steps.** Classify `1.13-ITIN-positive-001.txt`, then test its supported consumer separately.

**Expected.** ITIN detection at the selected confidence.

**Pass criteria.** Direct detection and applicable consumer outcome recorded.

**Audit assertion.** Save classification output and actual consumer telemetry.

**Evidence collected.** `1.13-BUILTIN-07-ual.json`.

#### 1.13-BUILTIN-08 — EIN positive

**Objective.** Verify whether an EIN detector is available. Do not assume a Microsoft built-in `U.S. Employer Identification Number (EIN)` SIT exists: check the [current catalog](https://learn.microsoft.com/en-us/purview/sit-sensitive-information-type-entity-definitions), tenant inventory, and publisher. If absent, validate a custom EIN SIT before testing it.

**Preconditions.** Inventoried EIN detector with documented pattern/context; otherwise mark `blocked`.

**Steps.** Classify positive/negative synthetic EIN samples; test its supported consumer separately.

**Expected.** Results agree with the selected detector's definition.

**Pass criteria.** Detector identity, publisher, definition, and results captured, or absence recorded.

**Audit assertion.** Save classification output and applicable consumer evidence.

**Evidence collected.** `1.13-BUILTIN-08-ual.json`.

### Custom SITs (1.13-CUSTOM-01..04)

#### 1.13-CUSTOM-01 — FINRA CRD positive

**Objective.** Confirm a custom SIT matching the FINRA Central Registration Depository (CRD) number format (6–7 digits with firm-specific prefix or contextual keywords like `CRD#`, `CRD No`) detects positive samples in Zone 3.

**Preconditions.** Custom SIT defined per [portal walkthrough](portal-walkthrough.md) Step 4. Record actual pattern confidence and consumer threshold; 85 maps to High, not a firm-defined band. The walkthrough's example uses Medium, so do not demand High unless a separately validated High pattern exists.

**Steps.** Classify `1.13-CRD-positive-001.txt` with synthetic CRD-format values and context, then test its supported consumer separately.

**Expected.** Detection at the authored confidence; runtime enforcement is a separate test.

**Pass criteria.** The selected SIT GUID and results agree with the exported definition and expected count/confidence.

**Audit assertion.** Save classifier output, definition, and any supported administrative/consumer records. No `SitUpdated` event is required.

**Evidence collected.** `1.13-CUSTOM-01-ual.json`, `1.13-CUSTOM-01-sit-xml.xml` (export of current SIT definition), `1.13-CUSTOM-01-sit-id.txt`.

#### 1.13-CUSTOM-02 — FINRA CRD negative

**Objective.** Confirm CRD SIT does not match a generic 7-digit number lacking the contextual keyword (false-positive guard).

**Preconditions.** Same as CUSTOM-01.

**Steps.** Substitute `1.13-CRD-negative-001.txt` containing seven-digit numbers without `CRD` keyword.

**Expected.** No match.

**Pass criteria.** No CRD match at the policy's selected threshold. If a Low regex-only pattern exists, bare numbers may legitimately match Low.

**Audit assertion.** Save direct results and the paired positive control.

**Evidence collected.** `1.13-CUSTOM-02-ual-negative.json`.

#### 1.13-CUSTOM-03 — Internal account number positive

**Objective.** Confirm a firm-defined internal account number SIT (e.g., format `ACCT-NNNNNNNN`) matches positive samples in Zone 2.

**Preconditions.** Custom SIT defined; separately supported consumer configured.

**Steps.** Classify `1.13-ACCT-positive-001.txt`; test the consumer separately.

**Expected.** Detection at the intended count/confidence.

**Pass criteria.** Results agree with the exported SIT definition and corpus expectations.

**Audit assertion.** Save classification and applicable consumer output.

**Evidence collected.** `1.13-CUSTOM-03-ual.json`, `1.13-CUSTOM-03-sit-xml.xml`.

#### 1.13-CUSTOM-04 — Internal account number negative

**Objective.** Confirm internal account SIT does not match `ACCT-NNNN` (too short) or `INVOICE-NNNNNNNN` (wrong prefix).

**Preconditions.** Same as CUSTOM-03.

**Steps.** Substitute `1.13-ACCT-negative-001.txt`.

**Expected.** No match.

**Pass criteria.** No direct match for the named SIT; paired positive succeeds.

**Audit assertion.** Save direct negative output; event absence alone is inconclusive.

**Evidence collected.** `1.13-CUSTOM-04-ual-negative.json`.

### Exact Data Match (1.13-EDM-01..03)

#### 1.13-EDM-01 — EDM exact match

**Objective.** Confirm an EDM classifier built from a hashed customer-account extract matches a row that exists exactly in the source extract.

**Preconditions.** EDM schema, rule package, and synthetic source table uploaded per [PowerShell setup](powershell-setup.md) §7. Capture Upload Agent `/GetDataStore` and `/GetSession /DataStoreName <name>`; observe §3 test readiness. Daily refresh is a firm-defined cadence, not a Microsoft requirement.

**Steps.**
1. Select an approved synthetic row in the uploaded table.
2. Include its primary value and every required supporting element in `1.13-EDM-positive-exact-001.txt`, respecting proximity.
3. Run the EDM classifier test, then a supported source-workload consumer test. A primary value alone is insufficient when supporting fields are required.

**Expected.** EDM and its primary SIT detect the sample; do not mistake a primary-SIT-only result for an EDM match.

**Pass criteria.** Specific EDM SIT detected with expected evidence/count/confidence; upload/session evidence identifies the tested dataset version.

**Audit assertion.** Capture direct results, Upload Agent session evidence, and actual consumer telemetry; no invented upload operation.

**Evidence collected.** `1.13-EDM-01-ual.json`, `1.13-EDM-01-edm-dataset-version.txt`, `1.13-EDM-01-source-row-hash.txt`.

#### 1.13-EDM-02 — EDM near-miss negative

**Objective.** Verify [EDM configurable-match semantics](https://learn.microsoft.com/en-us/purview/sit-get-started-exact-data-match-create-schema): altered significant values must not match; ignored delimiters/case may match intentionally, provided the primary SIT extracts the entire candidate value.

**Preconditions.** Same as EDM-01.

**Steps.** Construct `1.13-EDM-negative-near-001.txt` containing the row 142 account number with one digit altered (`ACCT-12345679`) and a separate file with the exact account number but with hyphenation removed (`ACCT12345678`).

**Expected.** Direct results show no EDM match on the digit-altered sample. The normalization variant follows the documented schema and primary-SIT extraction; record the actual EDM identity, not merely a primary-SIT match.

**Pass criteria.** Behavior matches the documented EDM normalization rules in the firm's EDM design document. Any unexpected match is a finding.

**Audit assertion.** Absence (or expected presence per documented normalization).

**Evidence collected.** `1.13-EDM-02-ual.json`, `1.13-EDM-02-design-doc-ref.txt`.

#### 1.13-EDM-03 — EDM schema rotation

**Objective.** Confirm an approved EDM schema change and dependent rule-package/data refresh preserve detection.

**Preconditions.** EDM-01 passed; change-control ticket approved for schema rotation.

**Steps.**
1. Modify the schema XML (e.g., add a non-primary column).
2. Update schema through the supported portal or `Set-DlpEdmSchema -FileData` workflow; re-export `EdmSchemaXML`.
3. Refresh dependent rule packages and hash/upload data as required; record session completion and the documented schema/test windows.
4. Re-run EDM-01 test against the rotated schema.

**Expected.** Updated schema matches the approved XML; EDM-01 passes after required refreshes.

**Pass criteria.** Before/after XML, upload/session output, and regression results captured.

**Audit assertion.** Preserve observed administrative audit activity without assuming schema-version or GUID-change fields.

**Evidence collected.** `1.13-EDM-03-schema-updated-ual.json`, `1.13-EDM-03-rerun-of-edm-01.json`.

### Named Entity Recognition (1.13-NER-01..04)

#### 1.13-NER-01 — PERSON entity positive

**Objective.** Confirm the named-entity SIT **All full names** detects approved synthetic names in its documented language/region scope. Named entities are complex dictionary/pattern-based SITs, not a generic entity-extraction API. [Named entities](https://learn.microsoft.com/en-us/purview/sit-named-entities-learn).

**Preconditions.** Advanced-classification entitlement and supported workload; record the exact SIT and policy. For bundled SITs in Endpoint DLP, enable Advanced classification scanning and protection.

**Steps.** Test `1.13-NER-PERSON-positive-001.txt` in the classifier and supported source-workload consumer.

**Expected.** Detection consistent with the chosen SIT definition.

**Pass criteria.** Classifier result and separately observed policy outcome recorded.

**Audit assertion.** Save classifier results and available workload evidence, not assumed Copilot prompt support.

**Evidence collected.** `1.13-NER-01-ual.json`.

#### 1.13-NER-02 — ORG entity positive

**Objective.** Check whether the tenant has a supported detector for organization names. The named-entity documentation lists names, addresses, and medical terms/conditions, not a generic built-in `Organization` NER SIT.

**Preconditions.** A documented, inventoried detector; otherwise record `n/a` with the catalog/inventory evidence.

**Steps.** If supported, test synthetic organization-name positives and negatives in that detector's supported workload.

**Expected.** Behavior agrees with the actual selected detector.

**Pass criteria.** Supported detector and results documented, or justified non-applicability captured.

**Audit assertion.** No fabricated ORG identifier or mandatory match event.

**Evidence collected.** `1.13-NER-02-ual.json`.

#### 1.13-NER-03 — ADDRESS entity positive

**Objective.** Confirm **All physical addresses** or **U.S. physical addresses** detects synthetic US addresses in its documented scope.

**Preconditions.** Same as NER-01.

**Steps.** Test `1.13-NER-ADDRESS-positive-001.txt` in the classifier and supported workload.

**Expected.** Detection consistent with the selected SIT.

**Pass criteria.** Direct results and applicable consumer outcome captured.

**Audit assertion.** Save actual classifier/workload output.

**Evidence collected.** `1.13-NER-03-ual.json`.

#### 1.13-NER-04 — NER false-positive control

**Objective.** Measure false positives on ambiguous synthetic narrative appropriate to each named-entity SIT; do not assume generic PERSON/ORG model semantics.

**Preconditions.** Same as NER-01.

**Steps.** Test `1.13-NER-negative-001.txt` alongside the paired positive in the classifier and supported consumer.

**Expected.** No match at the selected policy threshold.

**Pass criteria.** Direct results agree with expectations, or false positives are recorded for review.

**Audit assertion.** Capture actual output; no assumed flat UAL `Confidence` field.

**Evidence collected.** `1.13-NER-04-ual.json`, `1.13-NER-04-banner-absent-screenshot.png`.

### Trainable Classifiers (1.13-TC-01..04)

> **FSI Governance Gate.** Trainable classifiers are model artifacts subject to OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) and Federal Reserve SR 26-2 (formerly SR 11-7) (Model Risk Management). Each classifier deployed for Zone 2/3 enforcement requires: documented training-data lineage, validation set with measured precision/recall, model-risk committee sign-off, and re-validation cadence. Tests below assume that gate has been passed; absence of evidence is itself a finding.

#### 1.13-TC-01 — Customer Complaints classifier positive

**Objective.** Validate the **Customer complaints** classifier or a documented custom equivalent against held-out synthetic complaint narratives in a supported consumer, not an assumed Copilot SIT-prompt condition.

**Preconditions.** Record classifier identity/status, supported languages and workload from the [classifier definitions](https://learn.microsoft.com/en-us/purview/trainable-classifiers-definitions); model-risk evidence on file. Custom classifiers support English only; pretrained language coverage varies. Classifiers work only on unencrypted items.

**Steps.** Run the classifier validation workflow and separate supported consumer test using `1.13-TC-COMPLAINT-positive-001.txt` and the held-out set.

**Expected.** Detection and measured precision/recall meet the firm's recorded acceptance criteria.

**Pass criteria.** Results, current identity, language, and consumer binding captured; lifecycle changes reviewed in NEG-03.

**Audit assertion.** Preserve validation results and available consumer records; no mandatory Copilot pair.

**Evidence collected.** `1.13-TC-01-ual.json`, `1.13-TC-01-classifier-guid.txt`, `1.13-TC-01-model-risk-evidence-ref.txt`.

#### 1.13-TC-02 — Customer Complaints classifier negative

**Objective.** Confirm classifier does not match generic customer-service narrative without complaint indicators.

**Preconditions.** Same as TC-01.

**Steps.** Run the same validation and consumer workflow on `1.13-TC-COMPLAINT-negative-001.txt` and the held-out negatives.

**Expected.** Negative predictions within the recorded false-positive tolerance.

**Pass criteria.** Negative predictions and aggregate metrics captured, not merely a missing banner.

**Audit assertion.** Save validation output and applicable consumer evidence.

**Evidence collected.** `1.13-TC-02-ual.json`.

#### 1.13-TC-03 — Mergers & Acquisitions classifier

**Objective.** Validate a documented deal-confidential classifier. Confirm the actual catalog name (such as **Mergers and acquisitions files**) and supported workload rather than assuming `Mergers & Acquisitions` is a universal identifier.

**Preconditions.** Classifier published with model-risk evidence; Zone 3 policy active.

**Steps.** Run classifier validation and a supported source-workload consumer test on `1.13-TC-MA-positive-001.txt`.

**Expected.** Detection and consumer behavior match the documented configuration.

**Pass criteria.** Classifier identity, results, and consumer evidence recorded.

**Audit assertion.** Save actual validation/consumer evidence.

**Evidence collected.** `1.13-TC-03-ual.json`.

#### 1.13-TC-04 — Source code classifier

**Objective.** Validate **Source code** against representative supported-language samples and negatives. A small snippet does not establish accuracy across whole documents.

**Preconditions.** Classifier published; Zone 2 policy active.

**Steps.** Run classifier validation and a supported consumer test on representative synthetic code documents.

**Expected.** Detection and aggregate validation metrics agree with the intended use.

**Pass criteria.** Validation and supported consumer evidence captured.

**Audit assertion.** Save actual output, not an assumed Copilot match.

**Evidence collected.** `1.13-TC-04-ual.json`.

### DLP-for-Copilot policy enforcement (1.13-DLP-01..03)

#### 1.13-DLP-01 — Zone 1 alert

**Objective.** Confirm the firm's Zone 1 pilot/simulation policy records matches without enforcing a block. Alerts and notifications are supported but must be explicitly configured and tested.

**Preconditions.** Copilot-location custom policy scoped to the pilot users, configured in simulation mode; use a supported built-in/custom SIT in typed prompt text.

**Steps.** Enter the prevalidated synthetic positive directly in a prompt as the scoped test user; capture response, simulation match, and any configured alert. Do not substitute uploading the file.

**Expected.** No enforced block in simulation; expected simulation/alert evidence captured.

**Pass criteria.** Policy/rule mode, scope, runtime outcome, and available simulation/alert records agree.

**Audit assertion.** Save actual rule-match and interaction records where emitted; no fabricated `Action == "Alert"` field.

**Evidence collected.** `1.13-DLP-01-ual.json`, `1.13-DLP-01-alert-id.txt`.

#### 1.13-DLP-02 — Zone 2 educate

**Objective.** Confirm the policy-tip compliance URL for a supported Copilot block; this is not an independent generic "educate-only" enforcement action.

**Preconditions.** Validated blocking rule with Policy Tips enabled and **Provide a compliance URL for the end user to learn more about your organization's policies** configured with a full HTTPS URL accessible to test users.

**Steps.** Trigger a supported typed-prompt or label-based block as a scoped user; open **Learn about access restrictions** and verify the configured destination.

**Expected.** The standard block message/link text remains unchanged; only the link destination changes. Preview messaging in Word, Excel, and PowerPoint can be less explicit.

**Pass criteria.** Runtime restriction and accessible configured URL captured; do not require custom block-message text.

**Audit assertion.** Save actual available records and screenshot; no invented notify-action value.

**Evidence collected.** `1.13-DLP-02-banner-screenshot.png`, `1.13-DLP-02-ual.json`.

#### 1.13-DLP-03 — Zone 3 block

**Objective.** Confirm Zone 3 enforcement separately for sensitive typed prompts and labeled grounding files.

**Preconditions.** Copilot-location custom policy turned on for test users; separate SIT-prompt and sensitivity-label rules. SIT prompt restriction is preview and rollout-dependent. Allow up to four hours for policy updates.

**Steps.** (a) Enter prevalidated synthetic SIT text directly in a prompt: expect prompt-processing restriction. (b) Ask about a labeled file in SharePoint/OneDrive that the user otherwise can access: expect the content excluded, although a citation can remain. (c) Test permitted negatives. (d) If configured, test the distinct web-search restriction: internal-grounded answers can still be returned.

**Expected.** Each configured action behaves as documented. Label exclusion is not a promise to redact all sensitive text from every response or connector.

**Pass criteria.** Each scenario has the correct rule/action, scope, positive/negative controls, and runtime evidence; unsupported rollout is `blocked`, not `pass`.

**Audit assertion.** Preserve raw available audit/activity records. Copilot `AccessedResources.PolicyDetails` can describe restrictions; a universal shared DLP/Copilot correlation field is not documented.

**Evidence collected.** `1.13-DLP-03-agent-response.txt`, `1.13-DLP-03-ual.json`.

### DSPM for AI (1.13-DSPM-01..02)

#### 1.13-DSPM-01 — DSPM surfacing

**Objective.** Confirm supported AI interaction/SIT telemetry is visible in the tenant's DSPM experience. [DSPM for AI (classic)](https://learn.microsoft.com/en-us/purview/dspm-for-ai) is replaced by [new DSPM](https://learn.microsoft.com/en-us/purview/data-security-posture-management-learn-about); do not assume the dashboards or event counts are identical.

**Preconditions.** The selected classic/new DSPM experience is configured and collecting; DLP-03 executed in its supported coverage. Allow the documented initial setup window and record actual readiness, not a universal 24-hour event delay.

**Steps.** Record the actual experience. For classic, use **Solutions → DSPM for AI (classic) → Reports / Activity explorer**; filter by app, user, time, and relevant activity. Newly activated policies need at least 24 hours to collect data; that is not a maximum delivery SLA.

**Expected.** Events visible with correct attribution.

**Pass criteria.** Expected supported telemetry is attributable to the test; explain aggregation, filters, latency, and coverage differences rather than requiring one-to-one UAL counts.

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

#### 1.13-AUDIT-01 — Custom SIT create/delete evidence

**Objective.** Capture supported administrative activity and before/after state for a test custom SIT, without assuming a `SitCreated` operation.

**Preconditions.** Audit Reader; Information Protection Admin (separate principal — see PRE-04).

**Steps.**
1. Information Protection Admin creates a temporary throwaway custom SIT named `1.13-audit-temp-{timestamp}`.
2. Audit Reader searches the UTC change window and actor for supported administrative activity, preserving actual operation names and raw records.
3. Information Protection Admin deletes the unused test SIT; capture before/after inventory and actual deletion activity if emitted.

**Expected.** Configuration changes are evidenced; available audit records agree with the actor/change window.

**Pass criteria.** Snapshots and change transcript captured; missing expected audit coverage is recorded as a gap, not manufactured evidence.

**Audit assertion.** Record actual operation, actor, record ID, and timestamp, or the documented coverage limitation.

**Evidence collected.** `1.13-AUDIT-01-ual.json`.

#### 1.13-AUDIT-02 — EDM schema creation evidence

**Objective.** Confirm the approved EDM schema exists and preserve supported administrative activity.

**Preconditions.** Compliance Data Administrator; Audit Reader.

**Steps.** An authorized administrator creates a throwaway EDM schema (no real data) named `1.13-audit-edm-{timestamp}`; the reviewer captures actual supported audit activity and before/after configuration.

**Expected.** `Get-DlpEdmSchema` read-back agrees with the approved XML; no invented schema-created operation.

**Pass criteria.** Schema snapshot and change transcript captured; applicable observed activity has the correct actor.

**Audit assertion.** Record actual supported administrative operation if emitted, not `EdmSchemaCreated`.

**Evidence collected.** `1.13-AUDIT-02-ual.json`.

#### 1.13-AUDIT-03 — SIT update evidence

**Objective.** Confirm an approved custom SIT pattern change through definition read-back and regression tests.

**Preconditions.** Same as AUDIT-01.

**Steps.** Information Protection Admin modifies a pattern confidence on a non-production custom SIT; the reviewer captures actual supported audit activity and before/after configuration.

**Expected.** Definition delta and runtime classification agree with the change.

**Pass criteria.** Before/after package, direct test results, and supported activity captured.

**Audit assertion.** Preserve actual supported administrative operations; `SitUpdated` is not a required operation.

**Evidence collected.** `1.13-AUDIT-03-ual.json`.

#### 1.13-AUDIT-04 — DLP and AI-interaction evidence reconciliation

**Objective.** Establish the available telemetry for the exact Copilot/agent scenario, without assuming a universal DLP-to-interaction join.

**Preconditions.** Any §4 BUILTIN/CUSTOM/EDM/TC test executed in the last hour.

**Steps.** Search the bounded UTC window/user. Inspect actual `Operation`, `RecordType`, `AppIdentity`, `AppHost`, `AgentId`, `Messages`, and `AccessedResources` where present. Microsoft-developed Copilots use `CopilotInteraction`; custom-built/registered AI applications can use `ConnectedAIAppInteraction`; third-party AI applications can use `AIAppInteraction`. Do not confuse record types with operation names. Inspect resource `PolicyDetails` and any DLP activity available for the scenario.

**Expected.** Records describe the actual app/user/resource/policy test. Audit metadata is not the retained prompt/response content.

**Pass criteria.** Preserve raw records, observed identifiers, and correlation method/limitations. Shared IDs are strong evidence when present; user/time proximity alone is not a proven one-to-one join.

**Audit assertion.** Apply the [Copilot audit schema](https://learn.microsoft.com/en-us/purview/audit-copilot), not assumed flat `SensitiveInformationTypeName`, `Confidence`, or `Action` fields.

**Evidence collected.** `1.13-AUDIT-04-correlation-pivot.csv`.

### Negative-path battery (1.13-NEG-01..05)

#### 1.13-NEG-01 — Schema drift

**Objective.** Detect a custom SIT whose XML in production no longer matches the version-controlled definition in the SIT-as-code repository.

**Preconditions.** SIT-as-code repository (e.g., Azure DevOps repo with exported SIT XML); read access to production SIT definitions via IPPS.

**Steps.**
1. Inventory SITs with `Get-DlpSensitiveInformationType`; export the actual definition package with `Get-DlpSensitiveInformationTypeRulePackage`. `Export-Clixml` serializes returned objects and is not the authorable SIT XML. Use the documented package export procedure in [custom SIT PowerShell](https://learn.microsoft.com/en-us/purview/sit-create-a-custom-sensitive-information-type-in-scc-powershell).
2. Diff against the SIT-as-code repo HEAD.

**Expected.** Diff is empty.

**Pass criteria.** Empty diff (or every difference is associated with an approved change-control ticket).

**Audit assertion.** Observed supported administrative changes must correspond to approved tickets.

**Evidence collected.** `1.13-NEG-01-sit-diff.txt`, `1.13-NEG-01-ticket-list.csv`.

#### 1.13-NEG-02 — EDM hash mismatch

**Objective.** Detect source/schema/refresh drift. A local source-file hash does not prove which dataset is uploaded, and unchanged source bytes need not yield identical salted upload hashes.

**Preconditions.** Source-file and schema hashes, approved refresh record, Upload Agent version, and session evidence recorded per the EDM procedure.

**Steps.** Recompute hash of current source extract; compare to recorded hash.

**Expected.** Source/schema hashes agree with the approved refresh; `/GetDataStore` and `/GetSession` identify the corresponding completed upload.

**Pass criteria.** Refresh provenance and known synthetic EDM match verified; local hashes alone are insufficient.

**Audit assertion.** Capture uploader/session evidence; no invented `EdmDataUploaded` operation or remotely exposed source hash.

**Evidence collected.** `1.13-NEG-02-hash-chain.txt`.

#### 1.13-NEG-03 — Preview → GA classifier ID delta

**Objective.** Detect missing, retired, replaced, or unapproved classifier references. Preview-to-GA promotion does not universally imply a GUID change.

**Preconditions.** Inventory of all DLP policy references to trainable classifiers and NER classifiers (exported from `Get-DlpCompliancePolicy` / `Get-DlpComplianceRule`).

**Steps.**
1. Enumerate all classifier IDs referenced by policies.
2. Compare with actual portal/catalog identities, lifecycle status, and supported workloads; do not assume `IsPreview` or `LifecycleState` PowerShell properties.
3. Review relevant Microsoft Learn/service notices and regression-test bindings after lifecycle changes; re-point only when an actual identity change requires it.

**Expected.** Zero policies reference a deprecated preview GUID.

**Pass criteria.** Inventory clean; any deprecated reference is a finding.

**Audit assertion.** Preserve actual administrative change records and policy before/after exports.

**Evidence collected.** `1.13-NEG-03-classifier-inventory.csv`.

#### 1.13-NEG-04 — Regex regression

**Objective.** Detect a custom SIT whose regex no longer matches a previously-known positive sample (indicates an unintended pattern edit or library upgrade behavior change).

**Preconditions.** Per-custom-SIT regression corpus stored at `tests/1.13/regression/{sit-name}/`.

**Steps.** For each custom SIT, run BUILTIN-style positive test against the regression sample.

**Expected.** All historical positives still match.

**Pass criteria.** Regression battery 100% pass.

**Audit assertion.** Preserve direct classifier results and applicable workload telemetry; direct text tests do not require a DLP audit event.

**Evidence collected.** `1.13-NEG-04-regression-results.csv`.

#### 1.13-NEG-05 — DLP-for-Copilot scope and experience coverage

**Objective.** Confirm initiating-user scope, exclusions, supported experience, and the distinction between prompt-SIT and labeled-grounding controls. User targeting is valid; the Copilot location does not support administrative units.

**Preconditions.** Inventory of all DLP-for-Copilot policy scopes.

**Steps.**
1. Export `Get-DlpCompliancePolicy` and `Get-DlpComplianceRule` without an unverified `Workload` filter; compare to **Data Loss Prevention → Policies** and the **Microsoft 365 Copilot and Copilot Chat** location.
2. Verify included/excluded users/groups, mode, rule conditions/actions, feature rollout, and the initiating user's access to labeled grounding content.
3. Test included and excluded users separately. Do not replace user targeting with an agent GUID or source-site URL, or infer Copilot Studio connector coverage.

**Expected.** Intended users and supported experiences are covered, exclusions justified, and actual enforcement demonstrated.

**Pass criteria.** Inventory clean.

**Audit assertion.** N/A (configuration check).

**Evidence collected.** `1.13-NEG-05-policy-scope-inventory.csv`.

### Incident reproduction (1.13-IR-01)

#### 1.13-IR-01 — SIT misses real SSN in Copilot grounding (full reproduction)

**Objective.** Reproduce a real or hypothetical incident where a SIT failed to match an SSN-bearing document grounded by an agent. Used to validate root-cause analysis and to drive corrective-action SIT updates.

**Preconditions.** Firm-approved isolated replay environment and restricted evidence custody; incident artifact handled per firm's incident-handling SOP; Compliance Officer authorization on file. eDiscovery preserves/searches evidence but is not a Copilot sandbox. See [Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) for eDiscovery.

**Steps.**
1. In the contained workspace, replay the original prompt against a copy of the agent configuration at the time of incident.
2. Capture the agent response and UAL events.
3. Identify which SIT, classifier, or policy *should* have matched and did not.
4. Document root cause: missing SIT? wrong confidence band? wrong policy scope (NEG-05)? preview classifier GUID drift (NEG-03)? EDM hash mismatch (NEG-02)?
5. Propose corrective action and create a change-control ticket.

**Expected.** Root cause identified and documented; corrective action proposed.

**Pass criteria.** Root-cause document signed by Compliance Officer; corrective-action ticket linked.

**Audit assertion.** Preserve supported tenant audit records for the actual replay app; do not invent a case/workspace-specific interaction audit log.

**Evidence collected.** `1.13-IR-01-rca.md`, `1.13-IR-01-corrective-action-ticket.txt`, `1.13-IR-01-replay-ual.json`.

---


## §5 Evidence pack

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
    "cloud",
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
    "cloud": {
      "type": "string",
      "const": "Commercial"
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
      "minItems": 45,
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
      "description": "SHA-256 of the exact UTF-8 (no BOM) JSON text with this field's 64 hex characters replaced by 64 zeros. Builder emits compressed JSON with no trailing newline; do not parse/reserialize for hashing."
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
$rawJson = Get-Content $ManifestPath -Raw
$manifest = $rawJson | ConvertFrom-Json

# 2. Schema validation (requires Test-Json with -SchemaFile, PS 7.4+)
if (-not (Test-Json -Json $rawJson -SchemaFile $SchemaPath)) {
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
$recordedHash = $manifest.manifestSha256
$hashField = [regex]'("manifestSha256"\s*:\s*")[a-fA-F0-9]{64}(")'
if ($hashField.Matches($rawJson).Count -ne 1) {
    throw 'Expected exactly one manifestSha256 field.'
}
$canonical = $hashField.Replace($rawJson, '${1}' + ('0' * 64) + '${2}')
$bytes = [System.Text.Encoding]::UTF8.GetBytes($canonical)
$recomputed = [Convert]::ToHexString(
    [System.Security.Cryptography.SHA256]::HashData($bytes)
).ToLowerInvariant()
if ($recomputed -ne $recordedHash.ToLowerInvariant()) {
    $failures += "MANIFEST SELF-HASH MISMATCH: expected $recordedHash, got $recomputed"
}

# 5. Coverage assertion
$counts = [ordered]@{
    PRE = 7; BUILTIN = 8; CUSTOM = 4; EDM = 3; NER = 4; TC = 4
    DLP = 3; DSPM = 2; AUDIT = 4; NEG = 5; IR = 1
}
$expectedIds = foreach ($prefix in $counts.Keys) {
    1..$counts[$prefix] | ForEach-Object { '1.13-{0}-{1:00}' -f $prefix, $_ }
}
$presentIds = $manifest.tests.testId
$missing = $expectedIds | Where-Object { $_ -notin $presentIds }
if ($missing.Count -gt 0) {
    $failures += "MISSING TEST IDS: $($missing -join ', ')"
}
$unexpected = $presentIds | Where-Object { $_ -notin $expectedIds }
$duplicates = $presentIds | Group-Object | Where-Object Count -gt 1
if ($unexpected -or $duplicates) {
    $failures += 'Unexpected or duplicate test IDs.'
}

if ($failures.Count -gt 0) {
    Write-Error ($failures -join "`n")
    exit 1
}
Write-Host "OK: manifest valid; $($manifest.tests.Count) tests; all hashes verified."
exit 0
```

### 6.3 Manifest builder

Builder pattern (sketch to implement in the firm's evidence tooling; not a shipped repository script):

```powershell
# Build-EvidenceManifest.ps1 (sketch)
$manifest = [ordered]@{
    controlId       = '1.13'
    controlVersion  = 'v1.6.2'
    tenantId        = (Get-MgContext).TenantId
    cloud           = 'Commercial'
    cycleId         = "1.13-cycle-$(Get-Date -Format 'yyyyMMdd-HHmm')"
    cycleStart      = (Get-Date).ToUniversalTime().ToString('o')
    cycleEnd        = $null
    executor        = @{ upn = $env:FSI_EXECUTOR_UPN; role = $env:FSI_EXECUTOR_ROLE }
    approver        = @{ upn = $env:FSI_APPROVER_UPN; role = $env:FSI_APPROVER_ROLE }
    tests           = @()
    manifestSha256  = '0' * 64
}
# ... append per-test entries with hashes ...
# At end: set cycleEnd, then finalize using the same serialization as the validator.
$manifest.cycleEnd = (Get-Date).ToUniversalTime().ToString('o')
$manifest.manifestSha256 = '0' * 64
$canonical = $manifest | ConvertTo-Json -Depth 50 -Compress
$manifest.manifestSha256 = [Convert]::ToHexString(
    [System.Security.Cryptography.SHA256]::HashData(
        [System.Text.Encoding]::UTF8.GetBytes($canonical)
    )
).ToLowerInvariant()
$manifest | ConvertTo-Json -Depth 50 -Compress |
    Set-Content -Path '.\1.13-evidence-manifest.json' -Encoding utf8NoBOM -NoNewline
```

### 6.4 Evidence artifacts (per cycle)

| Artifact | Origin | Format | Retention |
|----------|--------|--------|-----------|
| `1.13-evidence-manifest.json` | `Build-EvidenceManifest.ps1` | JSON | 6 years (FINRA 4511) — WORM |
| `1.13-{testId}-ual.json` | `Search-UnifiedAuditLog` exports | JSON | 6 years — WORM |
| `1.13-{testId}-screenshot.png` | Portal capture | PNG | 6 years — WORM |
| `1.13-{testId}-agent-response.txt` | Test transcript | UTF-8 | 6 years — WORM |
| `1.13-corpus-manifest.json` | Repo-controlled | JSON | Source control retention |
| `1.13-PRE-04-role-matrix.csv` | Directory-role assignments and Purview role-group membership exports | CSV | 6 years — WORM |
| `1.13-NEG-01-sit-diff.txt` | `git diff` of SIT-as-code | Text | Source control retention |

### 6.5 Retention and WORM placement

Evidence is retained per **FINRA Rule 4511** (general books and records, 6 years) and **SEC Rule 17a-4(f)** (WORM media or electronic equivalent with required attestations). The evidence root must be either: (a) an immutable Azure Storage container with time-based retention policy locked, (b) a hierarchical-namespace/Data Lake storage account using supported **container-level immutable Blob Storage** configuration, or (c) a third-party WORM-attested archive. The path and storage account ID are recorded once per tenant in `docs/reference/evidence-retention.md` (firm-specific) and referenced by every cycle's manifest via `evidenceRoot` metadata in the executor's run log.

**Do not** treat Content Explorer screenshots as proof of runtime enforcement; they are supplementary. Primary evidence includes direct classifier results, actual policy/runtime observations, applicable audit exports, and manifest entries hashing those artifacts.

**Product boundary.** The evidence-archive requirements above are distinct from Microsoft 365 content and audit-log retention. Azure immutable storage uses immutable Blob Storage policies; do not assume an arbitrary Data Lake folder has an `Immutable` switch. Validate the storage account's supported immutability configuration and locked policy separately. See [immutable storage for Azure Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview) and [audit retention policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies). The named firm-specific evidence-root register is an organization-maintained artifact, not a file supplied by this repository.

For direct classifier tests, the primary technical evidence is the test output plus the input hash and definition. For supported runtime controls, add actual audit/activity records. An unavailable event or unsupported feature must not be represented as `auditAssertion.verified: true`; use `blocked`/`n/a` with the reason in `notes`. Schema validity and intact hashes do not by themselves make every test a pass or authorize attestation.

---

## §6 Attestation block

The attestation below is signed at the end of every test cycle. RACI alignment: Compliance Officer is **Accountable**, Information Protection Admin (or Purview Compliance Admin executing the cycle) is **Responsible**, CISO is **Consulted**, Internal Audit is **Informed**.

```
=============================================================
FSI Control 1.13 — Verification Cycle Attestation
=============================================================
Control ID:           1.13
Control Version: v1.6.2
Tenant ID:            ____________________________________
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
synthetic testing
=============================================================
```

> **Single-role attestation is a finding.** A cycle signed only by the Executor (without Compliance Officer counter-signature) does not satisfy the control. See §7 Anti-Pattern #14.

---

## §7 Anti-patterns

The following 15 patterns are **non-conformance** to Control 1.13 and must be remediated before the cycle can be signed.

1. **Synthetic-only testing without real-incident replay.** No `1.13-IR-01` execution against an actual past incident or hypothetical incident artifact within the last 12 months.
2. **Ignoring confidence bands.** Accepting a detection without reconciling actual classifier confidence/count with the consuming policy; do not assume a flat UAL `Confidence` property.
3. **No false-positive corpus.** Every `*-positive-*` test executed without the matching `*-negative-*` test.
4. **Inline test data in playbook prose.** Test SSNs, PANs, or account numbers pasted into Markdown rather than referenced from `tests/1.13/corpus/` with hash manifest.
5. **Fabricated SLAs.** Phrases such as "wait 24 hours for indexing" outside the §3 table of Microsoft-published windows.
6. **Invented confidence bands.** Ignoring Microsoft's mapping (≤65 Low, 66–75 Medium, 76–100 High), or assuming every SIT offers all three patterns.
7. **EDM with no near-miss test.** EDM classifiers deployed to Zone 3 without `1.13-EDM-02` having ever been run.
8. **DLP-for-Copilot scope confusion.** Replacing valid initiating-user scope with an agent GUID/site URL, or mistaking prompt-SIT inspection for file grounding inspection (NEG-05).
9. **Training trainable classifiers with production documents.** Seed sites containing real customer NPI (violates Control 1.7 secure-handling and OCC Bulletin 2026-13 (formerly OCC 2011-12) model-risk standards).
10. **Skipping classifier lifecycle checks.** Leaving policies bound to an actually retired/replaced classifier; do not assume every GA transition changes its GUID (NEG-03).
11. **Screenshots without manifest hash entry.** Evidence files omitted from `evidenceArtifacts`. The sample validator checks listed artifacts only; reconcile the evidence directory with the manifest separately.
12. **Unsupported tests recorded as pass.** Unavailable classifier types, rollout gaps, missing fixtures, and incomplete audit ingestion must be explicit.
13. **Operator-mediated waits substituted for audit-event verification.** "We waited 2 hours and re-tested" with no UAL event capture.
14. **Single-role attestation.** Cycle signed only by Executor, without Compliance Officer counter-signature.
15. **Treating a dashboard as universal evidence.** Preserve raw supported telemetry and direct test results; Content Explorer is supplementary, and a universal DLP/Copilot shared correlation ID is not promised.

---

## §8 Cross-links

- **Sibling 1.13 playbooks**
  - [`portal-walkthrough.md`](portal-walkthrough.md) — portal configuration steps for SITs, EDM, classifiers, DLP-for-Copilot
  - [`powershell-setup.md`](powershell-setup.md) — module pinning, IPPS connect, EDM Upload Agent, manifest builder
  - [Troubleshooting](troubleshooting.md) — common failure modes for this catalog
- **Shared baseline**
  - [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) — pinned module versions
- **Related controls**
  - [Control 1.5 — DLP and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)
  - [Control 1.6 — DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)
  - [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
  - [Control 1.19 — eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md)
  - [Control 4.6 — Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md)
- **Framework**
  - AI Incident Response Playbook — invoked by `1.13-IR-01`
  - FSI Governance Gate (control spec §3) — gates trainable-classifier deployment per OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)

---

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Needs Review — documentation verified; tenant UI not tested*
