# Control 2.5 — Verification & Testing Playbook (Meta-Validation)

**Control:** 2.5 — Testing, Validation, and Quality Assurance  
**Pillar:** 2 — Management  
**Audience:** AI Governance Lead, QA Lead, Compliance Officer, Power Platform Admin, Pipeline Admin, Internal Audit, Model Risk Manager  
**Sovereign-cloud scope:** Microsoft 365 Commercial, GCC, GCC High, DoD. 21Vianet is **out of scope** for this playbook (see PRE-06 / BLK-07).  
**Last UI verified:** April 2026

---

## Regulatory hedging notice

This playbook helps support FSI organizations in meeting expectations from FINRA Rule 3110 (supervision), SEC Rule 17a-4 (records retention), SOX §404 (internal control over financial reporting), GLBA Safeguards Rule 501(b), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) (model risk management), CFTC Regulation 1.31, NIST AI RMF (Measure function), ISO/IEC 42001, and NYDFS 23 NYCRR 500 where applicable.

A clean run of this playbook **does not guarantee legal or regulatory compliance**, does not replace independent validation, and does not substitute for written supervisory procedures. Implementation requires organization-specific risk assessment, legal review, and integration with the firm's broader compliance program. Organizations should verify current Microsoft Learn documentation, sovereign-cloud feature parity, and tenant-specific entitlements at each cycle. Numeric thresholds in this playbook are **calibrated to the tenant baseline captured in PRE-04**; they are not portable between tenants without recalibration.

This playbook is **meta-validation**: its job is to verify that the testing program for Microsoft 365 AI agents is itself operating effectively, not to test any specific agent. Agent-level testing belongs in the per-release QA plan that this playbook governs.

---

## Audience and how to use this playbook

| Role | What you do here |
|---|---|
| **AI Governance Lead** | Owns the cycle, signs as **Validator**, and ensures cadence, evidence retention, and exception expiry are enforced. |
| **QA Lead** | Runs the cycle, assembles the evidence pack, and signs as **Developer**. |
| **Compliance Officer** | Reviews the evidence pack from a supervisory and regulatory-readiness perspective and signs as **Compliance**. |
| **Power Platform Admin / Pipeline Admin** | Confirms that the §4 PIPE and HOLD tests reflect the actual platform-enforced gating behavior. |
| **Internal Audit** | Uses the evidence pack and three-signature attestation chain as the testable artifact for SOX-style and FINRA-supervision walkthroughs. |
| **Model Risk Manager** | Reviews EVAL, KPI, and PYRIT evidence under Fed SR 26-2 (formerly SR 11-7) / OCC Bulletin 2026-13 (formerly OCC 2011-12) model-risk expectations. |

Run order each cycle: **Section 0 blockers → Section 2 PRE gates → Section 4 tests → Section 5 evidence pack assembly → Section 6 validator → Section 7 attestation**. Anything earlier returning a blocker, a PRE FAIL, or a validator exit code 2 halts the cycle.

---

## Cross-links

This playbook depends on, and is depended on by, the following framework controls and playbooks. Operators should open these alongside this document during a cycle:

- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Control 1.19 — eDiscovery for Agent Interactions (verification playbook)](../1.19/verification-testing.md)
- [Control 1.21 — Adversarial Input Logging (verification playbook)](../1.21/verification-testing.md)
- [Control 2.1 — Managed Environments (verification playbook)](../2.1/verification-testing.md)
- [Control 2.3 — Change Management and Release Planning (verification playbook)](../2.3/verification-testing.md)
- [Control 2.13 — Documentation and Record Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md)
- [Control 2.20 — Incident Response (verification playbook)](../2.20/verification-testing.md)
- [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md)

---

## What this playbook catches

This playbook is designed to detect defects in the **testing program**, not just defects in any one agent. It is built to surface:

1. **Gate present, but not enforced** — a promotion gate exists in policy but the pipeline allows release without the underlying evidence.
2. **Undersized or stale golden dataset** — the evaluation corpus is too small, expired, or unrepresentative of in-scope scenarios.
3. **Pass-rate denominator gaming** — errored cases silently dropped from the denominator to inflate the pass rate.
4. **Role collision in approval** — the same natural person prepares, validates, and approves the cycle.
5. **Model or provider change not retested** — a behavior-surface change was not paired with a fresh evaluation cycle.
6. **Ephemeral pipeline artifacts** — evidence kept only in transient CI workspaces that expire before audit.
7. **PyRIT or equivalent omitted** — the adversarial test plane is skipped without a documented compensating control.
8. **No explicit Compliance or SME review for sensitive prompts** — disclosure, fairness, or refusal scenarios approved only by the builder.
9. **Cherry-picked dashboards** — KPI views that hide failure categories or reorder cohorts to look favorable.
10. **Silent sovereign-cloud gaps** — Commercial-cloud feature assumptions leaking into GCC High / DoD evidence.
11. **Permanent exceptions instead of re-validation** — temporary waivers that quietly become standing waivers.
12. **Tamper-prone evidence with no manifest or attestation chain** — evidence that cannot be independently re-verified.

---

## What this playbook does NOT claim

This playbook **does not** prove future agent perfection, **does not** replace human supervision or independent model validation, **does not** make one good cycle into permanent evidence, **does not** assume universal sovereign-cloud feature parity, and **does not** guarantee legal or regulatory compliance merely because the cycle returns a clean validator exit code. A clean cycle is one defensible data point against the firm's broader supervisory and risk-management obligations; it is not a substitute for them.

---

---

## Section 0 — Pre-flight blockers (BLK-01 through BLK-07)

This playbook mirrors Control 4.7's fail-closed posture: if any blocker remains unresolved, the cycle halts and the validator returns exit code **2**.

### BLK-01 — No approved QA governance charter or promotion-gate standard
- **Why this is a blocker.** The organization cannot verify that the testing program is operating as intended if the intended gate design, required evidence, accountable owners, and approval thresholds are undocumented or expired. The playbook should require a current signed testing standard that maps Gate 1 through Gate 4, zone logic, and escalation rules.
- **Required evidence.** `blk-01-governance-charter.json` referencing the policy ID, effective date, review date, owner, and sign-off roster.
- **Resolution rule.** Block the cycle until the charter is signed by AI Governance Lead and Compliance Officer or until a dated temporary exception exists with explicit expiry.
- **Recommended attestation note.** "BLK-01 was reviewed at cycle start and found to be resolved or explicitly excepted with a signed expiry date. The exception, if any, does not by itself waive the need for the affected §4 tests."

### BLK-02 — No production-equivalent test environment under managed governance
- **Why this is a blocker.** If the test environment does not materially match the production DLP posture, connector set, data-scope boundaries, and environment tiering expected by Control 2.1, then the test cycle cannot help demonstrate production readiness. Environment drift is a design deficiency, not a minor note.
- **Required evidence.** `blk-02-environment-equivalence.json` with environment IDs, managed-environment status, DLP version, connector inventory hash, and variance summary.
- **Resolution rule.** Do not proceed until the variance is closed or a named, time-bound exception is approved at the correct zone authority.
- **Recommended attestation note.** "BLK-02 was reviewed at cycle start and found to be resolved or explicitly excepted with a signed expiry date. The exception, if any, does not by itself waive the need for the affected §4 tests."

### BLK-03 — Golden dataset / evaluation corpus absent, undersized, or contaminated
- **Why this is a blocker.** The testing program itself is not defensible if the corpus is too small, stale, or contains real customer or employee PII. Zone 2 should have a meaningful dataset and Zone 3 should have a larger, curated, periodically refreshed corpus covering disclosures, edge cases, refusals, and out-of-scope prompts.
- **Required evidence.** `blk-03-corpus-integrity.json` with dataset version, entry counts by category, synthetic-fixture check, and last review date.
- **Resolution rule.** Halt until a versioned corpus exists and the PII check passes.
- **Recommended attestation note.** "BLK-03 was reviewed at cycle start and found to be resolved or explicitly excepted with a signed expiry date. The exception, if any, does not by itself waive the need for the affected §4 tests."

### BLK-04 — Evaluation or adversarial toolchain not operational
- **Why this is a blocker.** This playbook treats Copilot Studio Evaluation, PyRIT (or a documented equivalent), Solution Checker, and the promotion pipeline as part of the control surface. If one of the required toolchain elements is unavailable without a compensating control, the cycle should not be reported as complete.
- **Required evidence.** `blk-04-toolchain-health.json` listing tool versions, endpoint reachability, and fallback methods if any.
- **Resolution rule.** Stop the cycle unless the gap is explicitly mapped to a compensating control and the affected tests are recorded as justified Skip values.
- **Recommended attestation note.** "BLK-04 was reviewed at cycle start and found to be resolved or explicitly excepted with a signed expiry date. The exception, if any, does not by itself waive the need for the affected §4 tests."

### BLK-05 — Evidence retention or immutable storage path missing
- **Why this is a blocker.** A QA program cannot support books-and-records requirements if the evaluation exports, pipeline logs, approvals, and test artifacts expire with the CI workspace. This playbook makes this a hard blocker, not a best practice.
- **Required evidence.** `blk-05-retention-path.json` with storage target, immutability setting, retention period, and manifest location.
- **Resolution rule.** Block until the evidence store is reachable and the retention label / WORM-equivalent setting is documented.
- **Recommended attestation note.** "BLK-05 was reviewed at cycle start and found to be resolved or explicitly excepted with a signed expiry date. The exception, if any, does not by itself waive the need for the affected §4 tests."

### BLK-06 — Role separation and reviewer independence not established
- **Why this is a blocker.** If the same natural person can act as author, tester, and approver, the validation program is not independent enough for SOX-style control evidence or defensible FINRA supervision. This playbook positions this as a cycle-stopping issue.
- **Required evidence.** `blk-06-role-separation.json` showing Developer, Validator, Compliance role holders and overlap analysis.
- **Resolution rule.** No cycle should continue when role collision exists unless a co-signed exception is documented for a lower zone and expires immediately after the run.
- **Recommended attestation note.** "BLK-06 was reviewed at cycle start and found to be resolved or explicitly excepted with a signed expiry date. The exception, if any, does not by itself waive the need for the affected §4 tests."

### BLK-07 — Unsupported or ambiguous sovereign-cloud posture
- **Why this is a blocker.** This playbook refuses to assert results when the cloud classification is unclear, unsupported, or materially different from the feature assumptions used by the validator. 21Vianet should be treated as out of scope unless a dedicated local validator exists.
- **Required evidence.** `blk-07-cloud-guard.json` with tenant ID, primary domain, cloud classification, and parity-check timestamp.
- **Resolution rule.** Halt the cycle on ambiguity, or route to a separate cloud-specific validation path.
- **Recommended attestation note.** "BLK-07 was reviewed at cycle start and found to be resolved or explicitly excepted with a signed expiry date. The exception, if any, does not by itself waive the need for the affected §4 tests."

---

## Section 1 — Required **11 × 3 cadence matrix**

This playbook includes a cadence table using the 11 namespaces below as rows and the three governance zones as the primary frequency columns.

**Cadence rule.** Monthly cycles have a 35-day grace window, quarterly cycles have a 100-day grace window, and annual cycles have a 400-day grace window. A family that fails in two consecutive cycles should automatically escalate one tier until two clean cycles are observed.

| Namespace | What the family governs | Zone 1 | Zone 2 | Zone 3 | Owner | Reviewer | Grace window | Why it matters |
|---|---|---:|---:|---:|---|---|---|---|
| **VAL** | Validation design and traceability | Annual | Quarterly | Monthly | QA Lead | AI Governance Lead | 35d / 100d / 400d | Confirms the testing standard itself remains complete, mapped, and enforceable. |
| **HOLD** | Release hold and gated promotion enforcement | Quarterly | Monthly | Monthly | Power Platform Admin | Compliance Officer | 35d / 100d / 400d | Proves that failed evidence can actually stop promotion and cannot be hand-waved away. |
| **REG** | Regression and reproducibility | Annual | Quarterly | Monthly | QA Lead | Business Owner | 35d / 100d / 400d | Shows the program learns from incidents and replays prior failures after change. |
| **EVAL** | Copilot Studio Evaluation program quality | Quarterly | Monthly | Monthly | QA Lead | AI Governance Lead | 35d / 100d / 400d | Verifies the evaluation framework, scoring math, and export trail. |
| **PYRIT** | Adversarial / red-team testing | Annual | Quarterly | Monthly | Security Test Lead | AI Governance Lead | 35d / 100d / 400d | Confirms prompt-injection, jailbreak, and unsafe-behavior suites are actually run. |
| **SCHK** | Schema, checksum, and provenance integrity | Quarterly | Monthly | Monthly | QA Automation Engineer | FSI Internal Audit | 35d / 100d / 400d | Protects the integrity of the evidence pack and prevents silent metric or artifact tamper. |
| **PIPE** | Pipeline enforcement and deployment controls | Quarterly | Monthly | Monthly | Pipeline Admin | Power Platform Admin | 35d / 100d / 400d | Ensures the CI/CD layer implements the policy as code, not only as prose. |
| **PANE** | Panel review and human adjudication evidence | Annual | Quarterly | Monthly | Business Owner | Compliance Officer | 35d / 100d / 400d | Adds human review for high-risk prompts, disclosures, fairness, and appeals. |
| **KPI** | Quality KPI thresholding and drift monitoring | Quarterly | Monthly | Monthly | AI Governance Lead | Compliance Officer | 35d / 100d / 400d | Tracks whether the QA program is improving, drifting, or gaming its own numbers. |
| **SOV** | Sovereign-cloud parity and compensating controls | Annual | Semi-annual | Quarterly | AI Governance Lead | Compliance Officer | 35d / 200d / 400d | Prevents Commercial-only assumptions from leaking into sovereign assertions. |
| **IR** | Incident response and validation-escape handling | Annual | Annual | Quarterly | Incident Response Lead | Compliance Officer + AI Governance Lead | 35d / 400d / 400d | Verifies the organization can respond when the testing program misses a meaningful issue. |

---

## Section 2 — Pre-flight gates (PRE-01 through PRE-07)

All PRE gates should pass before any §4 test runs. A PRE failure should halt the cycle and return exit code **2**.

### PRE-01 — Toolchain version pinning
- **Objective.** Confirm the operator workstation and build agent are using pinned, supportable versions of PowerShell, Python, `pac`, required Graph / Exchange / PnP modules, and PyRIT or its documented equivalent.
- **How to verify.** Export version inventory for PowerShell modules plus Python package versions; capture Authenticode signature status for Microsoft modules and SHA-256 for the locally pinned validator and PyRIT requirement file.
- **Evidence.** `pre-01-toolchain.json`, `pre-01-python-freeze.txt`, `module.sha256`
- **Pass criteria.** All required versions meet the pinned minimum and no unsigned or unknown modules are in the execution path.
- **Audit assertion.** "The validator and its dependencies were version-pinned and traceable at cycle start; the toolchain used for this cycle can be reproduced later for audit or incident review."

### PRE-02 — Role separation and privileged-access posture
- **Objective.** Confirm the same natural person does not occupy the attestation roles of Developer, Validator, and Compliance, and that any elevated admin access used during the cycle is time-bound and ticketed.
- **How to verify.** Query role assignment records and pipeline approver rosters; verify PIM activation or equivalent JIT elevation where applicable; confirm co-signer requirements for any exception.
- **Evidence.** `pre-02-role-separation.json`
- **Pass criteria.** Three roles are distinct, no standing privileged overlap exists for the same cycle, and any exception is explicit and time-limited.
- **Audit assertion.** "The verification cycle was run under segregated duties consistent with supervisory and internal-control expectations."

### PRE-03 — License and environment floor
- **Objective.** Confirm the tenant has the required feature entitlements for Copilot Studio Evaluation, Managed Environments, pipeline gating, Purview Audit, and any other services the testing program relies on.
- **How to verify.** Capture tenant SKUs, environment classification, Managed Environment status, and evaluation feature availability; if a feature is absent in a sovereign cloud, record the compensating manual path.
- **Evidence.** `pre-03-licensing-and-env.json`
- **Pass criteria.** All exercised features are entitled and reachable, or a compensating control is documented and tied to the relevant SOV test.
- **Audit assertion.** "The cycle only relied on features the tenant is actually entitled to use in the declared cloud."

### PRE-04 — Baseline and numeric provenance capture
- **Objective.** Establish the tenant-specific baseline for latency, pass-rate trend, hallucination rate, grading scores, and alert timing before any release candidate is judged.
- **How to verify.** Pull the trailing cycle history, calculate p50/p95 where applicable, and write a baseline file with a stable `baselineId` that every KPI test references.
- **Evidence.** `pre-04-baseline.json`
- **Pass criteria.** A current baseline exists, references enough historical data, and is the sole source for the numeric thresholds cited later in the cycle.
- **Audit assertion.** "All numerical assertions in this cycle trace back to a documented tenant baseline rather than copied values from another tenant or an older release."

### PRE-05 — Change freeze and release-candidate integrity
- **Objective.** Confirm that the release candidate under test is frozen for the duration of the cycle so that the evidence represents a stable object rather than a moving target.
- **How to verify.** Compare commit ID, solution package hash, environment variable set, connector inventory, and model provider version between cycle start and cycle end.
- **Evidence.** `pre-05-freeze.json`
- **Pass criteria.** The artifact under test is unchanged during the cycle or any change is explicitly recorded and forces a re-run.
- **Audit assertion.** "The evidence pack corresponds to one stable release candidate and can therefore support defensible promotion or hold decisions."

### PRE-06 — Cloud guard and sovereign parity pre-check
- **Objective.** Confirm the tenant cloud is correctly classified as Commercial, GCC, GCC High, or DoD, and refuse to run if the cloud is unsupported or ambiguous for this playbook's assumptions.
- **How to verify.** Query organization metadata, connection endpoints, and cloud instance; compare to the declared cloud in the cycle manifest.
- **Evidence.** `pre-06-cloud-guard.json`
- **Pass criteria.** The declared cloud and the observed cloud match exactly; unsupported clouds halt.
- **Audit assertion.** "No cross-cloud assumptions were made silently, and the cycle executed in the environment it claims to describe."

### PRE-07 — Fixture integrity and corpus hash pinning
- **Objective.** Confirm the golden dataset, negative-test set, disclosure prompts, fairness scenarios, accessibility cases, and PyRIT prompt corpus are all versioned, hashed, synthetic where required, and approved for the cycle.
- **How to verify.** Compute SHA-256 on all fixture files, validate naming conventions, run PII screen on the corpus, and record the approved version IDs.
- **Evidence.** `pre-07-fixtures.json`, `manifest.sha256`
- **Pass criteria.** Every fixture matches the expected hash, the corpus is synthetic or approved, and the test IDs referenced later are resolvable to an actual stored file.
- **Audit assertion.** "The cycle's test inputs are stable, traceable, and free from accidental live-customer data contamination."

---

## Section 3 — Documented processing windows

This playbook includes a short timing table, but it must keep the same disciplined language used in 1.19, 1.21, and 4.7: **do not invent SLAs**. Where Microsoft documentation is qualitative or eventual-consistency based, say so plainly and use the tenant-specific PRE-04 baseline as the operative threshold for the current cycle.

| Signal or operation | Documentation-safe statement | Used by |
|---|---|---|
| Copilot Studio set-level evaluation run completion | No universal published SLA should be asserted; use the tenant baseline from PRE-04 and the tool's current export behavior observed in the cycle | EVAL-01 through EVAL-03 |
| Power Platform / Managed Environment pipeline stage result visibility | Treat as near-real-time in the platform UI but record the tenant-observed delay rather than a hard-coded time claim | PIPE-01 through PIPE-03 |
| Purview or UAL visibility of evaluation and promotion events | Use Microsoft-documented eventual consistency language; do not promise a fixed minute count | REG-03, EVAL-03, HOLD-01, IR-01 |
| PyRIT batch run duration | Local or build-agent dependent; use PRE-04 baseline and capture the actual runtime in the evidence file | PYRIT-01 through PYRIT-03 |
| Dashboard KPI refresh / reporting visibility | No hard-coded SLA; rely on measured tenant refresh cadence | KPI-01 through KPI-03 |
| Approval workflow reflection in pipeline / evidence store | Should generally be visible within the same release window but still record actual observed timing | VAL-03, HOLD-03, PIPE-03 |
| WORM / immutable storage handoff confirmation | Treat as near-real-time for the storage action but validate by evidence presence and hash match rather than elapsed minutes | HOLD-01, SCHK-02, IR-01 |

---

## Section 4 — Test catalog (**33 tests across 11 namespaces**)

This playbook present the test catalog in the same disciplined style used by the gold-standard verification playbooks: each test has a stable ID, one clear objective, specific preconditions, operator-runnable steps, expected behavior, a Boolean pass condition, an audit assertion, and named evidence artifacts.

### Namespace expansion
- **VAL** — Validation design and traceability  
- **HOLD** — Release hold and gated promotion enforcement  
- **REG** — Regression and reproducibility  
- **EVAL** — Copilot Studio Evaluation program quality  
- **PYRIT** — Adversarial / red-team testing  
- **SCHK** — Schema, checksum, and provenance integrity  
- **PIPE** — Pipeline enforcement and deployment controls  
- **PANE** — Panel review and human adjudication evidence  
- **KPI** — Quality KPI thresholding and drift monitoring  
- **SOV** — Sovereign-cloud parity and compensating controls  
- **IR** — Incident response and validation-escape handling

### 4.VAL — Validation design and traceability

This family verifies that the testing program is mapped, traceable, and evidence-backed from control objective through promotion decision.

#### 2.5-VAL-01 — Zone-based coverage of mandatory test domains

- **Objective.** Confirm that the QA plan covers all mandatory domains required by Control 2.5 for the agent's zone: functional, security, regression, performance, UAT, and—where applicable—bias, accessibility, and adversarial testing.
- **Preconditions.** PRE-03 and PRE-07 PASS; the agent is classified to a zone and has a current risk classification in the agent inventory or release record.
- **Steps.**
  1. Retrieve the release-candidate test plan and normalize it into a matrix of test families versus zone requirements. Confirm that Zone 1, Zone 2, and Zone 3 rows align to the control's stated minimums rather than an ad hoc local checklist.
  2. Cross-check the matrix against actual evidence artifacts already generated for the candidate release. The test must distinguish between a planned case and an executed case; a placeholder row does not count as coverage.
  3. Verify that the plan explicitly identifies regulatory disclosure scenarios, out-of-scope refusal scenarios, and negative security scenarios for any Zone 2 or Zone 3 agent. Where the agent has customer-facing or regulated use cases, ensure those scenarios are marked as required rather than optional.
- **Expected.** The release-candidate plan shows complete test-family coverage for the agent's zone with no unexplained omissions and no misclassified 'optional' items for regulated scenarios.
- **Pass criteria.** Every mandatory domain for the applicable zone has at least one executed test, at least one retained artifact, and a named owner. Missing coverage without an exception reference is FAIL.
- **Audit assertion.** "The testing program for this release candidate covered the mandatory validation domains required by Control 2.5 for the agent's zone and retained traceable evidence for each domain."
- **Evidence.** `2.5-VAL-01_coverage-matrix.json`, `2.5-VAL-01_zone-requirements.csv`

#### 2.5-VAL-02 — Requirement-to-test-to-gate traceability

- **Objective.** Confirm that every promotion gate requirement has a linked test or review artifact, and that the gate cannot be represented as complete while its underlying evidence remains absent or unresolved.
- **Preconditions.** PRE-01 through PRE-05 PASS; gate definitions for Design > Build, Build > Evaluate, Evaluate > Deploy, and Deploy > Monitor are documented.
- **Steps.**
  1. Parse the gate record and map each requirement line—business justification, prompt-injection resistance, performance threshold, sign-off, rollback readiness—to at least one test ID in this playbook. The mapping must be specific and machine-readable rather than free text only.
  2. Force a sample trace from one requirement in each gate to the underlying evidence file and the sign-off or decision artifact. A reviewer must be able to start from the gate record and reach the evidence without human interpretation or inbox archaeology.
  3. Check whether any requirement is satisfied only by narrative prose with no linked evidence artifact, or whether the same artifact is reused to satisfy unrelated gate requirements without justification.
- **Expected.** The gate framework is fully traceable and each gate requirement resolves to one or more concrete test records or approval artifacts in the evidence pack.
- **Pass criteria.** 100 percent of gate requirements have explicit test IDs or approval references; zero orphan requirements; zero 'trust me' narrative assertions.
- **Audit assertion.** "Promotion-gate decisions for this release were grounded in specific QA evidence and not in undocumented judgment alone."
- **Evidence.** `2.5-VAL-02_traceability.json`, `2.5-VAL-02_gate-map.csv`

#### 2.5-VAL-03 — Independent reviewer and approval integrity

- **Objective.** Confirm that the testing program enforces a meaningful separation between the person who assembled the evidence, the person who validated the quality of that evidence, and the person who approved release from a compliance or supervisory perspective.
- **Preconditions.** PRE-02 PASS and attestation roles are assigned for the cycle.
- **Steps.**
  1. Retrieve the approver list from the release system, evidence manifest, and attestation draft. Normalize the identities to UPN or object ID so collisions are detectable even when display names vary.
  2. Compare Developer, Validator, and Compliance roles across the current cycle, and confirm none of the three roles is occupied by the same natural person. If the cycle includes a co-signed lower-zone exception, verify the exception is time-bound and references the ticket that approved it.
  3. Verify the sign-off occurs after the underlying evidence exists and after the relevant test timestamps. A signature that predates the tests, or a template signature reused from a prior cycle, should be treated as FAIL.
- **Expected.** All signatories are distinct, their sign-off chronology makes sense, and the evidence they sign for already exists in the pack.
- **Pass criteria.** Distinct natural-person separation across all three attestation roles and no pre-signed or stale approvals.
- **Audit assertion.** "The release decision for this cycle was independently reviewed and approved under a role-separated supervisory model."
- **Evidence.** `2.5-VAL-03_signoff-integrity.json`

### 4.HOLD — Release hold and gated promotion enforcement

This family proves that the QA program can actually stop deployment. A regulated testing standard is weak if every control can be bypassed with a manual promotion or a subjective 'ship anyway' decision. This playbook make this family central to its meta-validation intent.

#### 2.5-HOLD-01 — Mandatory evidence absence triggers release hold

- **Objective.** Confirm that a missing required artifact—such as the golden dataset replay result, evaluation export, or UAT sign-off—automatically places the release candidate on hold and records the reason.
- **Preconditions.** PRE-05 PASS; a non-production release candidate is available for deliberate fail-closed testing.
- **Steps.**
  1. Run a controlled dry-run promotion with one required evidence artifact intentionally withheld or renamed so the pipeline cannot resolve it. Use a synthetic candidate and never do this against the live production branch.
  2. Observe whether the promotion stage blocks automatically and whether the hold reason is written to the release log, evidence manifest, or approval record with a stable identifier.
  3. Verify that the hold status persists until the missing artifact is restored and the validation is re-run. Manual override without recorded justification should be treated as a test failure.
- **Expected.** The release candidate is blocked from promotion and the reason is clearly recorded in machine-readable evidence.
- **Pass criteria.** Gate blocks on missing evidence; no unlogged bypass path exists; hold reason is retained.
- **Audit assertion.** "The testing program enforces a release hold when mandatory pre-deployment evidence is incomplete."
- **Evidence.** `2.5-HOLD-01_hold-trigger.json`, `2.5-HOLD-01_pipeline-log.txt`

#### 2.5-HOLD-02 — High-severity findings prevent promotion until disposition

- **Objective.** Confirm that high-severity unresolved findings from evaluation, security testing, fairness review, or PyRIT are not silently downgraded or ignored during release approval.
- **Preconditions.** PRE-04 and PRE-07 PASS; at least one seeded high-severity defect or synthetic failure condition exists for a deliberate gate challenge.
- **Steps.**
  1. Inject a synthetic High-severity result into the test summary using the normal defect-triage path, not by editing raw files after the fact. The point is to validate governance behavior, not to tamper with evidence.
  2. Observe whether the release pipeline or promotion checklist moves to blocked status and whether the release note references the open finding ID, owner, and target closure date.
  3. Confirm that only a time-bound exception signed by Compliance can move the release forward, and that the exception itself is referenced in the cycle manifest and hold ledger.
- **Expected.** A High-severity unresolved test result automatically holds the release and creates a visible, retained governance record.
- **Pass criteria.** No promotion without closure or exception; exception must be signed and expiring.
- **Audit assertion.** "The QA program stops releases when material unresolved findings remain and requires documented supervisory disposition before any exception is granted."
- **Evidence.** `2.5-HOLD-02_finding-block.json`, `2.5-HOLD-02_exception-check.json`

#### 2.5-HOLD-03 — Override expiry and re-validation control

- **Objective.** Confirm that a release override is temporary, scoped, and automatically returns the agent to mandatory re-validation on the next eligible cycle rather than becoming a standing waiver.
- **Preconditions.** At least one historical exception or simulated override record is available.
- **Steps.**
  1. Enumerate open and historical QA exceptions for the last four cycles and inspect whether they include expiry date, owner, rationale, and required follow-up cycle.
  2. Verify that an expired exception forces the next run into a mandatory re-validation state and cannot silently carry forward as 'previously accepted'.
  3. Check whether the evidence pack records the exception reference in the affected test rows and whether the attestation summary lists it among open findings or accepted risks.
- **Expected.** Exceptions are finite, visible, and self-expiring; the program compels a new validation cycle once the waiver window closes.
- **Pass criteria.** Zero indefinite overrides; every exception has expiry and re-test linkage.
- **Audit assertion.** "Release overrides in the QA program are explicitly time-bound and do not replace future validation cycles."
- **Evidence.** `2.5-HOLD-03_override-ledger.json`

### 4.REG — Regression and reproducibility

This family confirms the testing program can replay prior issues, prove fixes, and prevent recurrence.

#### 2.5-REG-01 — Golden-dataset replay reproducibility

- **Objective.** Confirm that the same versioned golden dataset can be replayed against the current and prior release candidate with stable scoring logic and preserved denominator integrity.
- **Preconditions.** PRE-04 and PRE-07 PASS; at least two adjacent release candidates or model versions exist for comparison.
- **Steps.**
  1. Run the full golden dataset or a documented representative subset against both releases using the same scoring rubric, same environment classification, and same evaluation version.
  2. Compare pass/fail, hallucination, citation, decline, and latency distributions side by side; ensure the comparison excludes no cases and records all error conditions rather than hiding them in an 'unscored' bucket.
  3. Preserve the side-by-side export and make sure the report records the dataset version, model version, prompt bundle version, and any known changes between runs.
- **Expected.** The program can prove that a new release did not regress materially against the prior baseline, or it can clearly explain and hold on a regression.
- **Pass criteria.** Deterministic replay works and the comparison report is complete, denominator-stable, and attributable to a specific release candidate.
- **Audit assertion.** "The QA program preserved a replayable, versioned baseline and used it to evaluate regression risk before promotion."
- **Evidence.** `2.5-REG-01_replay-report.json`, `2.5-REG-01_score-diff.csv`

#### 2.5-REG-02 — Issue-to-test feedback loop

- **Objective.** Confirm that meaningful production defects, audit findings, or customer complaints are converted into permanent regression tests within a defined service window.
- **Preconditions.** Access to the issue register or a synthetic defect log for the prior quarter.
- **Steps.**
  1. Sample a set of significant incidents or complaints involving incorrect content, missed refusal, disclosure omission, or unsafe prompt handling. Trace each item to the regression suite and confirm whether a durable test case was added.
  2. Review the age of the regression additions and whether they reference the originating incident or ticket number. This must be more than a narrative promise that 'we will remember to add it later'.
  3. Confirm that the next release candidate re-runs the newly added regression case and that the evidence pack retains both the defect linkage and the validation result.
- **Expected.** Important real-world failures are transformed into enduring regression cases and replayed against subsequent releases.
- **Pass criteria.** Sampled findings show a documented incident-to-test linkage and a replay record in a later cycle.
- **Audit assertion.** "The testing program converts production learning into durable regression coverage rather than relying on memory or informal retest."
- **Evidence.** `2.5-REG-02_feedback-loop.json`

#### 2.5-REG-03 — Material-change retesting trigger

- **Objective.** Confirm that material changes to model provider, system prompt, knowledge source, connector scope, or environment variables automatically trigger re-testing and evidence refresh.
- **Preconditions.** PRE-05 PASS; access to change-management history and release metadata.
- **Steps.**
  1. Enumerate the changes recorded since the previous cycle and classify them as material or non-material using the release-planning standard from Control 2.3.
  2. For each material change, verify the release pipeline or change workflow required replay of the appropriate test families—evaluation, regression, adversarial testing, and approvals—and did not allow promotion to reuse the older evidence pack.
  3. Check whether the final evidence manifest references the exact change record IDs and whether any material change lacks a corresponding retest or exception.
- **Expected.** Material changes cause automatic retest obligations and new evidence artifacts; old evidence is never recycled as if it applies to a new configuration.
- **Pass criteria.** All material changes have linked retests or valid exceptions; zero stale evidence re-use.
- **Audit assertion.** "The testing program required fresh validation when the release candidate changed in ways that could materially alter agent behavior."
- **Evidence.** `2.5-REG-03_change-trigger.json`

### 4.EVAL — Copilot Studio Evaluation program quality

This family validates set-level grading, threshold discipline, and export retention for the evaluation plane.

#### 2.5-EVAL-01 — Versioned test-set and grader configuration

- **Objective.** Confirm that evaluation test sets, grading dimensions, expected-answer rules, and threshold settings are versioned and attached to the exact release candidate under review.
- **Preconditions.** PRE-03 and PRE-07 PASS; the agent uses Copilot Studio Evaluation or a documented equivalent in the current cloud.
- **Steps.**
  1. Export the evaluation configuration, including test-set identifier, grader definitions, threshold floor, and any custom scoring logic. Record the release candidate and model version to which the configuration applies.
  2. Verify that the program does not run free-form or ad hoc evaluation sets whose origin cannot later be reconstructed. The test set should be pinned and recoverable from storage or version control.
  3. Compare the configuration to the prior cycle and highlight any changes in grader logic or threshold floor. Changes should require reviewer acknowledgment rather than silent adoption.
- **Expected.** Evaluation settings are versioned, attributable, and reproducible; the cycle can explain what was measured and how.
- **Pass criteria.** Evaluation configuration exported and tied to the release candidate; no undocumented grader changes.
- **Audit assertion.** "The release candidate's evaluation run used a versioned and reviewable grading configuration rather than a transient ad hoc setup."
- **Evidence.** `2.5-EVAL-01_eval-config.json`, `2.5-EVAL-01_grader-export.json`

#### 2.5-EVAL-02 — Defensible scoring math and denominator completeness

- **Objective.** Confirm that the reported pass rate, groundedness score, citation score, refusal rate, and other KPI numerics are calculated on the full submitted set and not on a cherry-picked or error-excluded denominator.
- **Preconditions.** A completed evaluation run exists for the release candidate.
- **Steps.**
  1. Compare total cases submitted, cases scored, cases errored, cases skipped, and cases passed. Operators should instruct that any omitted or errored case remains part of the denominator unless the methodology explicitly and defensibly states otherwise.
  2. Validate that the threshold rules used in gate approval align to Control 2.5's stated targets and the tenant baseline, while still remaining hedged and not presented as universal truths.
  3. Review whether the evidence report exposes raw counts, percentages, and exclusions in one place so an auditor does not need to reverse-engineer the math from screenshots.
- **Expected.** The evaluation report is mathematically transparent and cannot be manipulated by omitting inconvenient cases.
- **Pass criteria.** Reported percentages reconcile to raw counts; error and skip behavior is visible; no denominator manipulation detected.
- **Audit assertion.** "The QA program calculated release-readiness metrics using a complete and reviewable denominator, improving the defensibility of the gate decision."
- **Evidence.** `2.5-EVAL-02_score-math.json`, `2.5-EVAL-02_counts.csv`

#### 2.5-EVAL-03 — Evaluation export retention and audit trace

- **Objective.** Confirm that evaluation outputs, reviewer comments, and release decisions are preserved in the firm's retained evidence store and can be correlated later to the release candidate and cycle attestation.
- **Preconditions.** PRE-05 PASS and a completed evaluation cycle exists.
- **Steps.**
  1. Export the evaluation result set and save it to the cycle evidence directory, then verify the export is listed in the SHA-256 manifest and copied to the immutable retention target.
  2. Confirm that the export includes enough metadata to reconstruct the run later: agent ID, environment, model version, dataset version, grader version, operator, and run timestamp.
  3. Where Purview or audit logging captures the evaluation activity, confirm the activity record is present within the tenant baseline and record its identifier as a correlation point rather than as the sole evidence source.
- **Expected.** The evaluation run leaves a durable books-and-records trail that survives the pipeline workspace and can support later review or incident investigation.
- **Pass criteria.** Export exists, hash is recorded, retention copy confirmed, and correlation metadata is sufficient.
- **Audit assertion.** "Evaluation evidence for this release was retained in a durable, reviewable form and correlated to the cycle manifest."
- **Evidence.** `2.5-EVAL-03_export.json`, `2.5-EVAL-03_retention-proof.json`

### 4.PYRIT — Adversarial / red-team testing

This family brings adversarial validation into the QA-program control model and verifies that its results affect release governance.

#### 2.5-PYRIT-01 — Direct prompt-injection corpus executed per release candidate

- **Objective.** Confirm that a current prompt-injection / jailbreak corpus is run against in-scope release candidates at the required zone cadence and before promotion.
- **Preconditions.** PRE-01 and PRE-07 PASS; PyRIT or an approved equivalent is available for the cycle.
- **Steps.**
  1. Execute the direct-attack corpus against a test fixture for the current release candidate, recording the tool version, corpus hash, and scenario IDs.
  2. Verify that the run is tied to the exact release candidate rather than a prior candidate or a generic shared dev bot. The release note should identify the tested artifact by package or build hash.
  3. Review whether the resulting issues are triaged and categorized by severity, and whether unresolved High findings feed the HOLD family automatically.
- **Expected.** The adversarial suite is executed for the candidate itself and its outcomes feed gate logic.
- **Pass criteria.** Current corpus executed; output retained; unresolved High findings block promotion or require exception.
- **Audit assertion.** "The QA program included a current adversarial prompt-injection run for the release candidate and incorporated the result into release governance."
- **Evidence.** `2.5-PYRIT-01_direct-run.json`, `2.5-PYRIT-01_corpus.sha256`

#### 2.5-PYRIT-02 — Indirect, encoded, and evasion-style adversarial coverage

- **Objective.** Confirm that the security test program includes more than obvious direct injections by covering encoded, nested, indirect, and instruction-smuggling scenarios relevant to grounded agents.
- **Preconditions.** PRE-07 PASS and the corpus includes encoded / indirect cases.
- **Steps.**
  1. Review the attack corpus for coverage of indirect prompt injection, instruction hierarchy abuse, embedded policy evasion, and encoded payload variants. The playbook should call out that direct-only coverage is inadequate for regulated use cases.
  2. Run a representative sample of these cases and confirm the evidence distinguishes between safe refusal, partial containment, and unsafe compliance.
  3. Ensure the disposition writes enough detail to support later triage: scenario ID, expected behavior, actual behavior, severity, and reference to the associated mitigation work item.
- **Expected.** The program covers layered adversarial techniques and records them in a structured, auditable format.
- **Pass criteria.** Non-trivial adversarial cases are present, executed, and dispositioned; zero evidence that the security suite is 'happy-path only'.
- **Audit assertion.** "The QA program extended beyond simple jailbreak prompts and included indirect and evasion-oriented adversarial scenarios relevant to grounded AI behavior."
- **Evidence.** `2.5-PYRIT-02_evasion-run.json`

#### 2.5-PYRIT-03 — Model/provider change forces adversarial retest

- **Objective.** Confirm that any material shift in model provider, model family, prompt architecture, or safety setting triggers a fresh adversarial run rather than reuse of stale results.
- **Preconditions.** A change history exists for the current or prior cycle.
- **Steps.**
  1. Check the model and provider metadata for the current release and compare it with the previous cycle. Include provider shifts such as GPT-family changes or Anthropic-related reasoning path changes where relevant under Microsoft's current service architecture.
  2. Verify that the pipeline or release workflow forced a rerun of the adversarial suite and updated the evidence files. Reuse of a prior adversarial result should be treated as a control failure unless a justified exception exists.
  3. Confirm that any unresolved high-risk result from the fresh run feeds both HOLD and IR handling, not merely a backlog note.
- **Expected.** A model or provider change cannot ride to production on borrowed adversarial evidence.
- **Pass criteria.** Fresh PYRIT evidence exists for every material model change; no stale reuse.
- **Audit assertion.** "The QA program re-ran adversarial validation when the underlying model behavior surface changed materially."
- **Evidence.** `2.5-PYRIT-03_model-change.json`

### 4.SCHK — Schema, checksum, and provenance integrity

This family protects evidence integrity through schema validation, manifest checks, and fail-closed provenance controls.

#### 2.5-SCHK-01 — Cycle evidence validates against the shared JSON envelope

- **Objective.** Confirm that the cycle's root JSON document and per-test records conform to a schema that is envelope-compatible with Controls 1.14, 1.19, 1.21, and 4.7.
- **Preconditions.** The cycle directory exists and the schema file for Control 2.5 is present.
- **Steps.**
  1. Run schema validation against the root `cycle.json` artifact and a representative sample of per-test records. Confirm required fields such as `controlId`, `cycleId`, `tenant`, `preflightGates`, `tests`, `manifest`, and `attestation` are populated.
  2. Check that the `testId` pattern covers all eleven namespaces and that the per-test records include zone, cloud, result, evidence hash, audit assertion, and regulatory-driver references.
  3. Confirm that a schema failure causes the validator to exit code 2 and does not allow the run to continue as a soft warning.
- **Expected.** Evidence structure is standardized, auditable, and compatible with the framework's broader verification ecosystem.
- **Pass criteria.** Schema validation passes with zero missing mandatory fields; failure is fail-closed.
- **Audit assertion.** "The QA evidence pack for this cycle conformed to the shared FSI envelope and can be consumed by downstream audit-side validation tooling."
- **Evidence.** `2.5-SCHK-01_schema-validation.json`

#### 2.5-SCHK-02 — SHA-256 manifest and validator module hash integrity

- **Objective.** Confirm every artifact in the cycle is covered by a line-per-file SHA-256 manifest and that the validator module used for the cycle matches the pinned hash recorded at run start.
- **Preconditions.** PRE-01 and PRE-07 PASS; evidence directory populated.
- **Steps.**
  1. Generate or re-check `manifest.sha256` across the cycle directory and compare the recorded hash for each file to the live file hash at review time.
  2. Check `module.sha256` against the validator file or package used for the run. A mismatch should be treated as potential tamper or unapproved mid-cycle change.
  3. Verify that the attestation and manifest themselves are also hashed and included in the evidence set so that the integrity chain closes over the whole pack.
- **Expected.** All files reconcile to the manifest and the validator itself has not changed invisibly during the cycle.
- **Pass criteria.** Zero hash mismatches and zero unpinned validator changes.
- **Audit assertion.** "Evidence artifacts and the validator used to produce them were integrity-checked through a SHA-256 manifest and module pinning model."
- **Evidence.** `2.5-SCHK-02_manifest-check.json`, `manifest.sha256`, `module.sha256`

#### 2.5-SCHK-03 — Metric provenance, timestamps, and naming discipline

- **Objective.** Confirm that the KPIs cited in the release decision resolve back to the PRE-04 baseline and that artifacts use stable naming and chronology that can be followed without guesswork.
- **Preconditions.** PRE-04 PASS and at least one full cycle result exists.
- **Steps.**
  1. Inspect the metric files and ensure they reference the current cycle's `baselineId`; verify the numerics in the dashboard or summary are sourced from those files rather than hand-entered values.
  2. Review timestamps across test records, manifest generation, retention copy, and attestation. Chronology should follow a logical order: tests run, results emitted, manifest built, attestation signed.
  3. Check file naming against the pattern `2.5-<FAMILY>-<NN>_<descriptor>.<ext>` so that evidence can be located reliably by auditors and automation alike.
- **Expected.** The cycle's metrics are traceable to source data, and the evidence set follows a predictable chronology and naming convention.
- **Pass criteria.** No metric provenance gaps, no broken chronology, and no ambiguous artifact naming.
- **Audit assertion.** "The numerical and temporal integrity of this cycle's evidence pack is traceable and reproducible."
- **Evidence.** `2.5-SCHK-03_provenance.json`

### 4.PIPE — Pipeline enforcement and deployment controls

This family proves the policy is encoded in the release mechanism rather than left to honor-system review.

#### 2.5-PIPE-01 — Deliberate-fail pipeline run proves gate blocking

- **Objective.** Confirm that the CI/CD path truly blocks on a failed evaluation or missing approval rather than merely displaying a warning.
- **Preconditions.** A safe non-production branch or synthetic release candidate is available.
- **Steps.**
  1. Trigger a deliberate-fail run using a known broken threshold or a withheld approval in the non-production path. The key is to observe the control's operating effectiveness, not just review its configuration.
  2. Record the pipeline exit code, blocked stage, and any release note that references the hold reason. The evidence should show unambiguously that the candidate could not reach the next stage.
  3. Confirm that the failure also writes a durable artifact outside the pipeline's transient console output so the evidence survives normal retention limits.
- **Expected.** The deployment path blocks and records the hold in a durable, attributable way.
- **Pass criteria.** Observed fail-closed block with exit code or status indicating non-promotion; no silent bypass.
- **Audit assertion.** "The release pipeline demonstrated actual blocking behavior when QA policy conditions were not satisfied."
- **Evidence.** `2.5-PIPE-01_deliberate-fail.json`, `2.5-PIPE-01_console.txt`

#### 2.5-PIPE-02 — Environment equivalence and configuration parity

- **Objective.** Confirm that the test environment and the production target use materially aligned configuration for connectors, DLP, environment variables, and security settings so the test results are meaningful.
- **Preconditions.** BLK-02 resolved and PRE-03 PASS.
- **Steps.**
  1. Export configuration inventories from the non-production and production target environments and compare them by hash or structured diff.
  2. Review the variance list to see whether any difference could materially alter agent behavior or safety posture. Where such differences exist, the playbook should direct the validator to fail or require an explicit exception.
  3. Ensure the comparison result is preserved as evidence and referenced in the release decision, especially for Zone 3 agents.
- **Expected.** The release candidate is tested under production-equivalent conditions or any meaningful variance is visible and dispositioned.
- **Pass criteria.** No unexplained material variance between tested and targeted environments.
- **Audit assertion.** "The release candidate's QA evidence was produced in an environment materially consistent with the intended production target."
- **Evidence.** `2.5-PIPE-02_env-diff.json`

#### 2.5-PIPE-03 — Approval, service principal, and artifact retention hardening

- **Objective.** Confirm that the pipeline itself respects segregation of duties, uses governed identities, and exports its logs and artifacts to the retained evidence store.
- **Preconditions.** PRE-02 and PRE-05 PASS.
- **Steps.**
  1. Inspect the pipeline identity and confirm it uses a governed service principal or managed identity aligned to Control 2.8, with no broad undocumented permissions.
  2. Review the pipeline approval model and ensure at least one approval step requires a person outside the developer role for higher-risk zones or regulated releases.
  3. Verify artifact export and retention: console logs, result JSON, coverage reports, and approval records must all land in the cycle evidence directory and then in the immutable evidence store.
- **Expected.** The release pipeline uses least privilege, enforces the right approvals, and preserves its artifacts beyond the native short-term build log retention window.
- **Pass criteria.** Governed identity, proper approver separation, and durable artifact export all confirmed.
- **Audit assertion.** "The pipeline used for QA enforcement operated with governed permissions and preserved its own evidence trail appropriately."
- **Evidence.** `2.5-PIPE-03_pipeline-governance.json`

### 4.PANE — Panel review and human adjudication evidence

This family requires targeted human review where judgment, disclosure, fairness, or accessibility concerns are materially relevant.

#### 2.5-PANE-01 — Business SME panel review of high-risk use cases

- **Objective.** Confirm that a business subject-matter panel reviews a sample of high-risk and edge-case prompts before promotion, especially where the agent influences customer communications or regulated workflows.
- **Preconditions.** A sampled set of high-risk prompts has been flagged from the evaluation run.
- **Steps.**
  1. Select a representative sample of high-impact prompts—rate disclosures, eligibility questions, complaint handling, exception language, and complex edge cases—and present them to the Business Owner or designated SME reviewers.
  2. Require reviewers to record an explicit disposition such as Accept, Accept with edits, Reject, or Escalate. Free-text only feedback is less useful than structured verdicts.
  3. Ensure the panel outcome is retained as an artifact and linked back to the release candidate and the underlying prompt set.
- **Expected.** Business SMEs review material prompts and leave a durable record of their approval or concerns.
- **Pass criteria.** Required sample reviewed, structured dispositions present, and unresolved concerns fed to HOLD or REG families.
- **Audit assertion.** "Business-domain experts participated in the release-readiness review for high-risk prompt scenarios and their decisions were retained as evidence."
- **Evidence.** `2.5-PANE-01_sme-panel.json`

#### 2.5-PANE-02 — Compliance panel review of regulatory and disclosure scenarios

- **Objective.** Confirm that disclosure-sensitive, regulated, or examination-relevant prompts receive explicit Compliance review rather than relying entirely on automated scoring.
- **Preconditions.** Zone 2 or Zone 3 release candidate and a compliance-tagged prompt subset.
- **Steps.**
  1. Prepare a compliance-tagged sample from the golden dataset, including out-of-scope advice requests, disclosure prompts, records questions, and escalation scenarios.
  2. Have Compliance review the sample for adequacy of refusal, disclosure, escalation, and wording. This playbook say that this review helps support, but does not replace, human supervisory obligations.
  3. Record the panel verdict and any required remediation items, then confirm the release cannot claim completion while those items remain unresolved.
- **Expected.** Compliance review occurs for the regulated sample and creates a retained decision record.
- **Pass criteria.** Compliance panel artifact present with at least one natural-person reviewer and documented verdicts.
- **Audit assertion.** "Compliance-sensitive prompt outcomes were subject to human review before release and were not left solely to automated scoring logic."
- **Evidence.** `2.5-PANE-02_compliance-panel.json`

#### 2.5-PANE-03 — Fairness, accessibility, and appeal adjudication loop

- **Objective.** Confirm that the testing program includes a human adjudication path for fairness and accessibility concerns and that disputed outcomes are not silently marked as known issues.
- **Preconditions.** At least one accessibility or fairness review input exists, whether from testing or prior incidents.
- **Steps.**
  1. Sample test cases tied to accessibility expectations, language clarity, biased treatment concerns, or disparate handling of equivalent scenarios. Confirm that reviewer notes include a clear disposition and remediation owner.
  2. Review whether appealed or disputed cases are kept in the evidence pack and linked to the next regression cycle rather than disappearing after an email thread.
  3. Check that any fairness or accessibility remediation results in an updated test case or review rubric in subsequent cycles.
- **Expected.** Human adjudication exists for quality issues that cannot responsibly be reduced to one machine score.
- **Pass criteria.** Appeal or adjudication evidence exists and is linked to remediation and future regression coverage.
- **Audit assertion.** "The QA program maintained a human adjudication path for fairness and accessibility concerns and carried the results forward into later validation work."
- **Evidence.** `2.5-PANE-03_adjudication.json`

### 4.KPI — Quality KPI thresholding and drift monitoring

This family turns benchmark tables into provenance-aware metrics suitable for leadership and audit review.

#### 2.5-KPI-01 — KPI threshold calibration by zone

- **Objective.** Confirm that the QA program uses zone-appropriate KPI floors for accuracy, groundedness, citation fidelity, decline behavior, and latency, while still tying those floors to local baselines and risk appetite.
- **Preconditions.** PRE-04 baseline exists and the release candidate has completed an evaluation run.
- **Steps.**
  1. Compare the KPI table used in the release decision to the control's published threshold guidance and the tenant baseline. Ensure the thresholds are neither unreasonably low nor blindly copied from another tenant without calibration.
  2. Specifically verify that latency expectations reflect the control's stated target (<3 seconds for Zone 1–2 standard queries, <2 seconds for Zone 3 where applicable) without presenting them as universal service guarantees.
  3. Check that the quality dashboard or summary report exposes both the threshold and the observed value so the decision logic is transparent.
- **Expected.** KPI thresholds are explicit, zone-aware, and attributable to the baseline and policy standard.
- **Pass criteria.** Thresholds exist, are calibrated, and are visible in the release evidence with no unexplained magic numbers.
- **Audit assertion.** "Quality thresholds used for this release were zone-aware, baseline-backed, and transparently documented."
- **Evidence.** `2.5-KPI-01_thresholds.json`

#### 2.5-KPI-02 — Trend and drift escalation

- **Objective.** Confirm that the QA program tracks KPI movement over time and escalates additional scrutiny when results degrade or become unstable across consecutive cycles.
- **Preconditions.** At least three historical cycles or equivalent trend records are available.
- **Steps.**
  1. Pull the trend data for pass rate, groundedness, hallucination rate, and decline accuracy over multiple cycles. Review whether the program is improving, flat, or degrading.
  2. Confirm that meaningful deterioration triggers a required action such as hold, deeper review, or increased cadence rather than being explained away in narrative commentary.
  3. Verify that the trend chart includes both successful and failed cycles so the program cannot hide deterioration by reporting only the good releases.
- **Expected.** Metric drift is visible and results in action rather than quiet acceptance.
- **Pass criteria.** Trend reporting includes failed cycles and contains an escalation path for degradation.
- **Audit assertion.** "The QA program monitored quality drift across cycles and used the trend to inform supervision and release readiness."
- **Evidence.** `2.5-KPI-02_trends.json`, `2.5-KPI-02_chart.csv`

#### 2.5-KPI-03 — Dashboard provenance and anti-cherry-picking check

- **Objective.** Confirm that published KPI dashboards or release summaries match the raw evidence artifacts and do not suppress failed cohorts, outliers, or inconvenient categories.
- **Preconditions.** A dashboard, scorecard, or release summary is available for the current cycle.
- **Steps.**
  1. Take the KPI counts reported to approvers and reconcile them to the raw evaluation export and manifest-listed files for the cycle. Differences should be explainable and documented.
  2. Check that the dashboard includes high-risk categories, out-of-scope refusals, and error counts rather than only aggregate success metrics. A polished dashboard that hides its own failure channels is not a defensible control instrument.
  3. Confirm the dashboard references the cycle ID, dataset version, and release candidate so it cannot be reused across unrelated cycles.
- **Expected.** The dashboard is a truthful view of the cycle rather than a marketing summary.
- **Pass criteria.** Reported numbers reconcile to evidence and no material category is hidden.
- **Audit assertion.** "Published QA metrics for this cycle reconciled to the raw evidence set and did not exclude material failures or outlier conditions."
- **Evidence.** `2.5-KPI-03_dashboard-reconcile.json`

### 4.SOV — Sovereign-cloud parity and compensating controls

This family verifies cloud-specific feature parity and requires explicit compensating controls for gaps.

#### 2.5-SOV-01 — Feature parity verification for evaluation and pipeline surfaces

- **Objective.** Confirm which QA-related features are available in the declared cloud—Copilot Studio Evaluation, export capability, managed environments, audit visibility, and pipeline gating—and whether the cycle relied only on supported surfaces.
- **Preconditions.** PRE-06 PASS and the sovereign parity matrix is current for the cycle.
- **Steps.**
  1. Walk the feature list relevant to the current cycle and confirm availability in the cloud using current platform behavior and, where necessary, current Microsoft documentation captured at `lastVerifiedUtc`.
  2. Record each feature as Available, Limited, Confirm, or Not Supported. Where the value is not Available, bind the gap to a compensating control or force the affected test to justified Skip with explicit explanation.
  3. Verify that the final attestation does not overstate parity beyond what this matrix actually confirms.
- **Expected.** The cycle accurately describes what the cloud can and cannot do for the QA program.
- **Pass criteria.** Feature status recorded for all exercised surfaces; no silent parity assumptions.
- **Audit assertion.** "The QA program's cloud-specific feature dependencies were reviewed and recorded before the cycle's results were asserted."
- **Evidence.** `2.5-SOV-01_parity.json`

#### 2.5-SOV-02 — Retention and evidence path parity by cloud

- **Objective.** Confirm that the evidence store, audit trail, and artifact export path used by the QA program are valid in the declared cloud and meet the control's retention expectations.
- **Preconditions.** BLK-05 resolved.
- **Steps.**
  1. Verify the storage and export path for the current cloud—Purview-governed SharePoint, immutable Azure Blob, or equivalent—and confirm the evidence copy succeeded for the current cycle.
  2. Check whether the same retention label, legal hold, or immutability behavior exists in the sovereign cloud if the organization claims a common control posture across tenants.
  3. Where a difference exists, require the evidence pack to record the variance and the compensating process rather than calling the control uniformly implemented.
- **Expected.** Evidence storage and retention claims are true for the declared cloud, not just for the Commercial reference tenant.
- **Pass criteria.** Current cloud evidence path validated; any variance is documented with a compensating control.
- **Audit assertion.** "QA evidence retention and export controls for this cycle were verified against the declared cloud's actual capabilities and storage path."
- **Evidence.** `2.5-SOV-02_retention-path.json`

#### 2.5-SOV-03 — Compensating-control governance for cloud gaps

- **Objective.** Confirm that any cloud-limited feature is paired with a documented fallback method, approval, and retest rule rather than being ignored.
- **Preconditions.** At least one feature in the sovereign matrix is marked Limited, Confirm, or Not Supported, or else mark this as Pass with no gaps found.
- **Steps.**
  1. Review the compensating control register and confirm each gap has an owner, a rationale, a fallback method, and a next review date.
  2. Ensure the affected test cases reference the compensating control by ID and that the attestation summary mentions the existence of the gap where material.
  3. Verify that a cloud gap cannot remain unresolved forever without re-review; the fallback must be refreshed on the next cycle.
- **Expected.** Cloud gaps are governed explicitly and do not disappear into tribal knowledge.
- **Pass criteria.** All gaps have documented compensating controls and next review dates.
- **Audit assertion.** "Cloud-specific limitations affecting QA validation were controlled through explicit compensating controls rather than silent assumption."
- **Evidence.** `2.5-SOV-03_comp-controls.json`

### 4.IR — Incident response and validation-escape handling

This family covers what happens when the testing program itself fails or is bypassed.

#### 2.5-IR-01 — QA-control failure routes to incident or exception register

- **Objective.** Confirm that a material failure in the testing program—missed sign-off, broken gate, corrupted evidence, or severe post-deploy defect—creates a logged governance event with owner and closure target.
- **Preconditions.** A prior failed cycle, a synthetic failure event, or a sampled exception record is available.
- **Steps.**
  1. Select one material QA-control failure and trace it into the incident, risk, or exception register. Confirm the record identifies the control family, severity, owner, and target closure date.
  2. Verify the issue references the exact cycle ID and affected release candidate so the supervisory trail is precise.
  3. Confirm the resolution path requires an updated regression or process fix rather than only a narrative lesson learned.
- **Expected.** Material QA-control failures are tracked like control failures, not buried as informal improvement notes.
- **Pass criteria.** Incident or exception record exists with owner, due date, and cycle linkage.
- **Audit assertion.** "Material defects in the testing program were routed into a tracked remediation workflow with accountable ownership."
- **Evidence.** `2.5-IR-01_issue-register.json`

#### 2.5-IR-02 — Annual tabletop for a validation-escape scenario

- **Objective.** Confirm the organization has rehearsed a realistic scenario in which an inadequately tested agent reaches a user population and creates a disclosure, fairness, or content-quality incident.
- **Preconditions.** A tabletop record for the last 12 months is available or the current cycle includes the exercise.
- **Steps.**
  1. Review the tabletop artifact and ensure the scenario specifically references a testing-program failure such as stale corpus, bypassed hold, or missing adversarial run—not only a generic cyber incident.
  2. Confirm the exercise includes participants from QA, AI Governance, Compliance, and the relevant Business Owner function. For a higher-risk scenario, Legal should also be referenced.
  3. Verify the after-action record contains lessons learned, remediation owners, and any updates required to the regression or gating logic.
- **Expected.** The organization has practiced responding to a validation escape and has turned the exercise into actionable control improvements.
- **Pass criteria.** Current or recent tabletop exists, signed, and contains specific QA remediation actions.
- **Audit assertion.** "The organization rehearsed its response to a testing-program escape scenario and documented follow-up improvements to the QA control environment."
- **Evidence.** `2.5-IR-02_tabletop.json`

#### 2.5-IR-03 — Rollback or quarantine drill after failed validation escape

- **Objective.** Confirm that if a release is later found to be unsafe or inadequately validated, the organization can quickly hold, roll back, or quarantine the agent and preserve the associated evidence.
- **Preconditions.** A non-production drill path or recent incident response artifact exists.
- **Steps.**
  1. Run or review a controlled rollback or quarantine drill showing how the team disables or withdraws the release candidate, stops new promotion, and preserves the evidence pack and runtime logs.
  2. Confirm the drill records who initiated the rollback, how long it took, what evidence was preserved, and whether the release remained discoverable for later review.
  3. Check that the exercise ties back to change-management and release-planning controls, not merely an operational runbook with no QA linkage.
- **Expected.** The firm can contain a validation escape and preserve a defensible trail of the decision and evidence.
- **Pass criteria.** Rollback or quarantine drill documented, timed, and linked to the evidence-retention path.
- **Audit assertion.** "The organization demonstrated an operational path to contain a release when QA evidence later proved insufficient or incorrect."
- **Evidence.** `2.5-IR-03_rollback-drill.json`

---

## Section 5 — Evidence pack layout

This playbook includes a concrete evidence-directory layout so operators and auditors know exactly what a completed cycle produces.

```text
evidence/2.5/<cycleId>/
  blockers.json
  pre-01-toolchain.json
  pre-02-role-separation.json
  pre-03-licensing-and-env.json
  pre-04-baseline.json
  pre-05-freeze.json
  pre-06-cloud-guard.json
  pre-07-fixtures.json
  tests/
    2.5-VAL-01_coverage-matrix.json
    2.5-VAL-02_traceability.json
    2.5-VAL-03_signoff-integrity.json
    2.5-HOLD-01_hold-trigger.json
    2.5-HOLD-02_finding-block.json
    2.5-HOLD-03_override-ledger.json
    2.5-REG-01_replay-report.json
    2.5-REG-02_feedback-loop.json
    2.5-REG-03_change-trigger.json
    2.5-EVAL-01_eval-config.json
    2.5-EVAL-02_score-math.json
    2.5-EVAL-03_export.json
    2.5-PYRIT-01_direct-run.json
    2.5-PYRIT-02_evasion-run.json
    2.5-PYRIT-03_model-change.json
    2.5-SCHK-01_schema-validation.json
    2.5-SCHK-02_manifest-check.json
    2.5-SCHK-03_provenance.json
    2.5-PIPE-01_deliberate-fail.json
    2.5-PIPE-02_env-diff.json
    2.5-PIPE-03_pipeline-governance.json
    2.5-PANE-01_sme-panel.json
    2.5-PANE-02_compliance-panel.json
    2.5-PANE-03_adjudication.json
    2.5-KPI-01_thresholds.json
    2.5-KPI-02_trends.json
    2.5-KPI-03_dashboard-reconcile.json
    2.5-SOV-01_parity.json
    2.5-SOV-02_retention-path.json
    2.5-SOV-03_comp-controls.json
    2.5-IR-01_issue-register.json
    2.5-IR-02_tabletop.json
    2.5-IR-03_rollback-drill.json
  cycle.json
  manifest.sha256
  module.sha256
  attestation.json
```

### Evidence design rules
1. Every evidence file should carry the `cycleId` and `controlId` in either filename or internal metadata.
2. Every material file in the directory must appear in `manifest.sha256`.
3. `cycle.json` is the root envelope and references the blocker ledger, PRE results, test results, manifest, and attestation.
4. Evidence should be retained in a WORM-equivalent or immutable store for the firm's required horizon; the playbook should mention 7 years where the organization uses the evidence to support SOX-style or regulatory recordkeeping assertions.
5. The validator should refuse to treat the run as complete until `attestation.json` is present with three distinct signatures.

---

## Section 6 — JSON Schema and PowerShell validator requirements

This playbook explicitly states that Control 2.5 adopts the same family envelope pattern used by Controls 1.14, 1.19, 1.21, and 4.7. This makes the output auditable in a shared way and allows future orchestration or assessment tooling to consume it consistently.

### 6.1 JSON Schema — envelope-compatible design

The schema below is the Control 2.5 root envelope. It is intentionally compatible with the other verification playbooks in this framework: same overall object shape, same attestation model, same manifest discipline, and explicit namespace patterning.

Use `fsi-agentgov.example` as a placeholder identifier only (placeholder — replace with your tenant) before publishing an internal schema endpoint.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://fsi-agentgov.example/schema/fsi-2.5-evidence.schema.json",
  "title": "FSI Control 2.5 QA Program Verification Evidence Pack",
  "type": "object",
  "required": [
    "controlId", "version", "cycleId", "tenant", "windowUtc",
    "blockers", "preflightGates", "tests", "manifest", "attestation"
  ],
  "additionalProperties": false,
  "properties": {
    "controlId": { "const": "2.5" },
    "version": { "const": "v1.4" },
    "cycleId": {
      "type": "string",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6}Z-(z1|z2|z3|all)$"
    },
    "tenant": {
      "type": "object",
      "required": ["tenantId", "primaryDomain", "cloudInstance"],
      "properties": {
        "tenantId": { "type": "string", "format": "uuid" },
        "primaryDomain": { "type": "string" },
        "cloudInstance": { "enum": ["Commercial", "GCC", "GCCHigh", "DoD"] }
      }
    },
    "windowUtc": {
      "type": "object",
      "required": ["startUtc", "endUtc", "lastVerifiedUtc"],
      "properties": {
        "startUtc": { "type": "string", "format": "date-time" },
        "endUtc": { "type": "string", "format": "date-time" },
        "lastVerifiedUtc": { "type": "string", "format": "date-time" }
      }
    },
    "blockers": {
      "type": "array",
      "minItems": 7,
      "maxItems": 7,
      "items": {
        "type": "object",
        "required": ["id", "status", "evidenceFile"],
        "properties": {
          "id": { "pattern": "^BLK-0[1-7]$" },
          "status": { "enum": ["resolved", "exception", "open"] },
          "evidenceFile": { "type": "string" },
          "exceptionRef": { "type": "string" }
        }
      }
    },
    "preflightGates": {
      "type": "object",
      "required": ["PRE-01", "PRE-02", "PRE-03", "PRE-04", "PRE-05", "PRE-06", "PRE-07"],
      "patternProperties": {
        "^PRE-0[1-7]$": {
          "type": "object",
          "required": ["status", "evidenceFile", "sha256"],
          "properties": {
            "status": { "enum": ["PASS", "FAIL"] },
            "evidenceFile": { "type": "string" },
            "sha256": { "type": "string", "pattern": "^[A-Fa-f0-9]{64}$" },
            "notes": { "type": "string" }
          }
        }
      }
    },
    "tests": {
      "type": "array",
      "minItems": 33,
      "maxItems": 33,
      "items": {
        "type": "object",
        "required": [
          "testId", "namespace", "status", "zone", "completedUtc",
          "ownerUpn", "evidenceFile", "sha256", "auditAssertion"
        ],
        "properties": {
          "testId": {
            "type": "string",
            "pattern": "^2\\.5-(VAL|HOLD|REG|EVAL|PYRIT|SCHK|PIPE|PANE|KPI|SOV|IR)-0[1-3]$"
          },
          "namespace": {
            "enum": ["VAL", "HOLD", "REG", "EVAL", "PYRIT", "SCHK", "PIPE", "PANE", "KPI", "SOV", "IR"]
          },
          "status": { "enum": ["PASS", "FAIL", "SKIP", "ERROR"] },
          "zone": { "enum": ["Z1", "Z2", "Z3"] },
          "completedUtc": { "type": "string", "format": "date-time" },
          "ownerUpn": { "type": "string", "format": "email" },
          "evidenceFile": { "type": "string" },
          "sha256": { "type": "string", "pattern": "^[A-Fa-f0-9]{64}$" },
          "findingId": { "type": "string" },
          "exceptionRef": { "type": "string" },
          "auditAssertion": { "type": "string", "minLength": 24 }
        }
      }
    },
    "manifest": {
      "type": "object",
      "required": ["manifestSha256", "moduleSha256", "fileCount"],
      "properties": {
        "manifestSha256": { "type": "string", "pattern": "^[A-Fa-f0-9]{64}$" },
        "moduleSha256": { "type": "string", "pattern": "^[A-Fa-f0-9]{64}$" },
        "fileCount": { "type": "integer", "minimum": 40 }
      }
    },
    "attestation": { "$ref": "#/$defs/attestation" }
  },
  "$defs": {
    "attestation": {
      "type": "object",
      "required": [
        "cycleSha256", "attestationSha256", "previousCycleAttestationSha256",
        "signatures", "statement"
      ],
      "properties": {
        "cycleSha256": { "type": "string", "pattern": "^[A-Fa-f0-9]{64}$" },
        "attestationSha256": { "type": "string", "pattern": "^[A-Fa-f0-9]{64}$" },
        "previousCycleAttestationSha256": {
          "type": "string",
          "pattern": "^([A-Fa-f0-9]{64}|GENESIS)$"
        },
        "signatures": {
          "type": "array",
          "minItems": 3,
          "maxItems": 3,
          "items": {
            "type": "object",
            "required": ["role", "principalUpn", "signedUtc", "signatureValue"],
            "properties": {
              "role": { "enum": ["Developer", "Validator", "Compliance"] },
              "principalUpn": { "type": "string", "format": "email" },
              "signedUtc": { "type": "string", "format": "date-time" },
              "signatureValue": { "type": "string", "minLength": 64 }
            }
          }
        },
        "statement": { "type": "string", "minLength": 64 }
      }
    }
  }
}
```

### 6.2 PowerShell validator — fail-closed skeleton

This playbook contains a validator skeleton or reference contract substantially like the following. It should use the same 0 / 1 / 2 exit-code semantics already established elsewhere in the framework and explicitly validate blockers, PRE gates, manifest integrity, schema conformance, and attestation chaining before reporting clean success.

```powershell
#requires -Version 7.4
# Exit codes:
#   0 = PASS (all blockers resolved, PRE gates pass, and in-scope tests pass)
#   1 = FAIL (one or more tests fail or have unjustified skip)
#   2 = BLOCKED (unresolved BLK, PRE failure, schema failure, or manifest / attestation tamper)

[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $CyclePath,
    [Parameter(Mandatory)] [string] $SchemaPath,
    [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string] $Cloud = 'Commercial',
    [ValidateSet('Z1','Z2','Z3','All')] [string] $Zone = 'All'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-CycleLog {
    param([string]$Level, [string]$Message)
    $entry = @{ ts = (Get-Date).ToUniversalTime().ToString('o'); level = $Level; msg = $Message } | ConvertTo-Json -Compress
    Add-Content -Path (Join-Path $CyclePath 'validator.log') -Value $entry -Encoding UTF8
}

function Test-Blockers {
    $ledger = Get-Content (Join-Path $CyclePath 'blockers.json') | ConvertFrom-Json
    foreach ($b in $ledger.blockers) {
        if ($b.status -eq 'open') {
            Write-CycleLog -Level 'ERROR' -Message "Unresolved blocker: $($b.id)"
            return $false
        }
    }
    return $true
}

function Test-Preflight {
    foreach ($pre in @('PRE-01','PRE-02','PRE-03','PRE-04','PRE-05','PRE-06','PRE-07')) {
        $obj = (Get-Content (Join-Path $CyclePath ($pre.ToLower() + '.json')) -ErrorAction Stop) | ConvertFrom-Json
        if ($obj.status -ne 'PASS') {
            Write-CycleLog -Level 'ERROR' -Message "$pre failed"
            return $false
        }
    }
    return $true
}

function Test-Manifest {
    $manifest = Get-Content (Join-Path $CyclePath 'manifest.sha256')
    foreach ($line in $manifest) {
        $parts = $line -split '\s+', 2
        if ($parts.Count -lt 2) { continue }
        $expected = $parts[0].ToLower()
        $relPath  = $parts[1]
        $filePath = Join-Path $CyclePath $relPath
        if (-not (Test-Path $filePath)) {
            Write-CycleLog -Level 'ERROR' -Message "Missing file from manifest: $relPath"
            return $false
        }
        $observed = (Get-FileHash -Path $filePath -Algorithm SHA256).Hash.ToLower()
        if ($observed -ne $expected) {
            Write-CycleLog -Level 'ERROR' -Message "Hash mismatch: $relPath"
            return $false
        }
    }
    return $true
}

function Test-Schema {
    $cycle = Get-Content (Join-Path $CyclePath 'cycle.json') -Raw
    if (-not (Test-Json -Json $cycle -SchemaFile $SchemaPath)) {
        Write-CycleLog -Level 'ERROR' -Message 'Cycle schema validation failed'
        return $false
    }
    return $true
}

function Test-AttestationChain {
    $att = Get-Content (Join-Path $CyclePath 'attestation.json') | ConvertFrom-Json
    if ($att.signatures.Count -ne 3) { return $false }
    $roles = $att.signatures.role | Sort-Object -Unique
    if ($roles.Count -ne 3) {
        Write-CycleLog -Level 'ERROR' -Message 'Attestation role collision'
        return $false
    }
    if ($att.previousCycleAttestationSha256 -ne 'GENESIS' -and [string]::IsNullOrWhiteSpace($att.previousCycleAttestationSha256)) {
        Write-CycleLog -Level 'ERROR' -Message 'Attestation chain pointer missing'
        return $false
    }
    return $true
}

try {
    if (-not (Test-Blockers))         { exit 2 }
    if (-not (Test-Preflight))        { exit 2 }
    if (-not (Test-Manifest))         { exit 2 }
    if (-not (Test-Schema))           { exit 2 }
    if (-not (Test-AttestationChain)) { exit 2 }

    $cycle = Get-Content (Join-Path $CyclePath 'cycle.json') | ConvertFrom-Json
    $failed = $cycle.tests | Where-Object { $_.status -in @('FAIL','ERROR') }
    $badSkips = $cycle.tests | Where-Object { $_.status -eq 'SKIP' -and -not $_.exceptionRef }

    if ($failed.Count -gt 0 -or $badSkips.Count -gt 0) {
        Write-CycleLog -Level 'WARN' -Message 'Cycle completed with open findings'
        exit 1
    }

    Write-CycleLog -Level 'INFO' -Message 'Cycle completed cleanly'
    exit 0
}
catch {
    Write-CycleLog -Level 'FATAL' -Message $_.Exception.Message
    exit 2
}
```

### Validator design notes

- The validator must be **fail-closed** by default.
- Any unresolved blocker, PRE failure, schema failure, manifest mismatch, or attestation-chain break should produce **exit code 2**.
- A normal cycle with open findings should still be archived and should return **exit code 1**, not 0.
- The validator should write a durable `validator.log` to the evidence directory.
- The validator must not allow a cycle to appear green merely because a missing implementation returned `Skip`; unjustified skip behavior should count as a failure condition.
- The manifest should include the validator output files themselves, not only the test artifacts.

---

## Section 7 — Three-signature hash-chain attestation

This playbook reuse the excellent chain-of-custody style already visible in 1.19 and 4.7, with role labels adapted to the QA-program context.

### Attestation specimen

```json
{
  "controlId": "2.5",
  "version": "v1.4",
  "cycleId": "2026-04-18T143000Z-z3",
  "cycleSha256": "<sha256-of-canonicalized-cycle.json>",
  "attestationSha256": "<sha256-of-attestation-json-before-signatures>",
  "previousCycleAttestationSha256": "<sha256-of-prior-attestation-or-GENESIS>",
  "summary": {
    "blockersResolved": 7,
    "preflightGatesPass": 7,
    "testsTotal": 33,
    "testsPass": 33,
    "testsFail": 0,
    "testsSkip": 0,
    "openFindings": []
  },
  "evidenceManifestSha256": "<sha256-of-manifest.sha256-file>",
  "validatorModuleSha256": "<sha256-of-Invoke-Control25Verification.ps1>",
  "signatures": [
    {
      "role": "Developer",
      "principalUpn": "qa.lead@example.com",
      "signedUtc": "2026-04-18T15:05:14Z",
      "signatureValue": "<base64 detached signature over cycleSha256>"
    },
    {
      "role": "Validator",
      "principalUpn": "ai.governance.lead@example.com",
      "signedUtc": "2026-04-18T15:21:47Z",
      "signatureValue": "<base64 detached signature over cycleSha256>"
    },
    {
      "role": "Compliance",
      "principalUpn": "compliance.officer@example.com",
      "signedUtc": "2026-04-18T15:44:59Z",
      "signatureValue": "<base64 detached signature over cycleSha256>"
    }
  ],
  "statement": "We attest that the verification cycle described herein was executed under role-separated access; that all seven BLK blockers were resolved and all seven PRE gates returned PASS before the §4 tests were run; that the §4 test results recorded in cycle.json reflect the actual QA-program state observed at cycleCompletedUtc; that the evidence pack was committed to the retained evidence path required by this playbook; and that this attestation is intended to support compliance with the regulations named in the hedging notice and does not guarantee legal compliance."
}
```

### Hash-chain rules
1. `previousCycleAttestationSha256` must point to the prior cycle of the **same cadence or scope**; do not chain unlike cycles casually.
2. The first cycle may use `GENESIS`, but the next cycle should resolve back to the genesis attestation within the normal cadence window.
3. `Developer`, `Validator`, and `Compliance` must be **three distinct natural persons**; the same UPN cannot sign twice under different labels.
4. The `Compliance` signer should be the **Compliance Officer** or written supervisory designee for the relevant line of business.
5. Detached signatures are preferred; a verifiable immutable-journal entry may be acceptable if the firm uses that pattern consistently and documents it.
6. A broken chain, missing prior pointer, role collision, or unverifiable signature should itself open a finding and should prevent a clean pass.

### Canonical role mapping

| Attestation role | Canonical job role in the framework | Responsibility |
|---|---|---|
| `Developer` | QA Lead | Runs the cycle and assembles the evidence pack |
| `Validator` | AI Governance Lead | Reviews the evidence for completeness and methodological soundness |
| `Compliance` | Compliance Officer | Approves the result from a supervisory and regulatory-readiness perspective |

---

## Section 8 — Anti-pattern catalog (**22 entries**)

This playbook includes a numbered anti-pattern table modeled after the stronger verification playbooks. This is important because a good test suite not only says what to do; it also documents the most common ways teams accidentally or intentionally weaken the methodology.

| # | Anti-pattern | Why it fails defensibility | Detected by |
|---|---|---|---|
| AP-01 | Golden dataset below zone minimum but still reported as representative | Undersized samples undermine repeatability and can make the pass rate look stronger than the real control posture. | VAL-01, EVAL-02 |
| AP-02 | Gate documented in policy but not encoded in pipeline behavior | This is a classic design-versus-operating-effectiveness gap: the rule exists on paper but not in practice. | VAL-02, PIPE-01 |
| AP-03 | Pass rate calculated against only scored cases while errored cases disappear | Denominator gaming creates a false-clean narrative and weakens audit defensibility. | EVAL-02, KPI-03 |
| AP-04 | PyRIT omitted for Zone 2 because the agent is internal only | Internal team agents can still mishandle sensitive data or unsafe instructions; lower public exposure does not eliminate risk. | PYRIT-01 |
| AP-05 | Adversarial suite run once at design time and never again | Material changes can reopen old failure modes; stale security evidence is not current control evidence. | PYRIT-03, REG-03 |
| AP-06 | Solution Checker or policy checker left in notify-only mode indefinitely | Notifications without enforcement produce the appearance of governance without the consequence of governance. | SCHK-01, PIPE-01 |
| AP-07 | Business Owner sign-off performed by the builder or QA Lead | Authority is misrepresented and supervisory accountability becomes blurred. | VAL-03, PANE-01 |
| AP-08 | Bias or fairness testing deferred until after deployment | This pushes risk discovery into production and weakens pre-release supervision. | PANE-03, REG-01 |
| AP-09 | Non-production test environment materially differs from target production | A clean result from a different configuration does not meaningfully support production readiness. | BLK-02, PIPE-02 |
| AP-10 | Evidence stored only in transient CI workspace | Pipeline logs often expire too quickly for FSI books-and-records expectations. | BLK-05, PIPE-03 |
| AP-11 | Model or provider changed but old evaluation results were reused | The evidence is stale relative to the behavior surface under review. | REG-03, PYRIT-03 |
| AP-12 | Dashboard reports only aggregate success and hides failure categories | Cherry-picked presentation can mislead approvers and weakens the truthfulness of management reporting. | KPI-03 |
| AP-13 | Commercial-cloud features assumed to exist in GCC High or DoD | Silent parity assumptions are a chronic source of false-clean evidence in sovereign environments. | SOV-01, PRE-06 |
| AP-14 | Compensating control mentioned vaguely with no owner or review date | A gap without accountable fallback is not a control; it is a known weakness. | SOV-03 |
| AP-15 | Same person executes, validates, and approves the cycle | This collapses the separation-of-duties intent of the entire QA control environment. | PRE-02, VAL-03 |
| AP-16 | Metrics copied from another tenant or prior year without baseline recalibration | Static borrowed thresholds can produce both false passes and false failures. | PRE-04, KPI-01 |
| AP-17 | Exception remains open for multiple cycles with no re-test | A temporary override becomes a de facto permanent waiver and erodes the testing program. | HOLD-03, IR-01 |
| AP-18 | Validator module modified mid-cycle without new hash pin | Tamper of the verification instrument itself undermines the credibility of all downstream evidence. | SCHK-02 |
| AP-19 | Release hold reason exists only in email or chat and not in the evidence pack | The hold happened, but its rationale is not retained in a defensible location. | HOLD-01, PIPE-03 |
| AP-20 | SME or Compliance panel review happens verbally with no structured disposition | Human review without retained verdicts is difficult to supervise and nearly impossible to audit. | PANE-01, PANE-02 |
| AP-21 | QA incident occurs but no regression test is added | The organization learns once, then forgets; control maturity stalls. | REG-02, IR-01 |
| AP-22 | Chain attestation signed by fewer than three distinct people | The hash chain may exist technically, but the supervisory value collapses when roles are not actually independent. | Section 7, SCHK-02 |

---

## Section 9 — Sovereign parity matrix

The sovereign matrix below is explicit and practical. It does not assert permanent feature parity. Status values are **Available**, **Confirm**, **Limited**, or **Out of scope**. Cycle owners must re-verify at `lastVerifiedUtc` against the current platform behavior and any current Microsoft Learn references.

| Feature or capability | Commercial | GCC | GCC High | DoD | Compensating control if not fully available |
|---|---|---|---|---|---|
| Copilot Studio core authoring and deployment | Available | Available | Confirm current parity | Confirm current parity | If limited, scope this playbook to available release surfaces only and record the gap in SOV-01. |
| Copilot Studio Agent Evaluation — set-level grading | Available | Confirm | Confirm | Confirm | Use manual scored golden-dataset review with retained rubric if feature not available. |
| Evaluation import / export for version control | Available | Confirm | Confirm | Confirm | Retain exported CSV/JSON and hash it manually if native export differs by cloud. |
| Managed Environments and promotion-gate governance | Available | Available | Confirm | Confirm | Use explicit environment-approval workflow if the managed-environment path differs. |
| Purview Audit visibility for QA and release artifacts | Available | Available | Confirm | Confirm | Where the signal surface is weaker, rely on pipeline artifacts plus immutable retention rather than claiming identical UAL depth. |
| Purview or records retention path for evidence storage | Available | Available | Confirm | Confirm | Use immutable Azure storage or equivalent if local retention scope differs. |
| PyRIT installation and execution | Available | Available | Available | Available with offline packaging if required | Vendor and hash-pin dependencies where internet egress is restricted. |
| Pipeline-native gating and exit-code enforcement | Available | Available | Available | Available | Fallback to a manual approval gate only with explicit documentation and short expiry. |
| Agent 365 SDK testing support | Preview or confirm | Preview or confirm | Likely limited or confirm | Likely limited or confirm | Do not make the playbook depend exclusively on preview features; provide pipeline-native alternatives. |
| Dashboard and KPI telemetry export | Available | Confirm | Confirm | Confirm | If dashboard export differs, store raw metric files and rebuild the scorecard from source evidence. |
| 21Vianet handling | Out of scope for this spec | Out of scope | Out of scope | Out of scope | Run a separate validator; PRE-06 should halt rather than pretend parity exists. |

---

## Section 10 — Required cross-links (**12 entries**)

| Control or playbook | Why it links to 2.5 verification | Reference path |
|---|---|---|
| **1.5 — Data Loss Prevention (DLP) and Sensitivity Labels** | Test data classification, disclosure cases, and evidence handling should align to label and DLP posture so QA scenarios reflect the real protection model. | `docs/controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md` |
| **1.6 — Microsoft Purview DSPM for AI** | DSPM for AI can help identify high-risk scenarios that should enter the golden dataset and can inform post-release quality drift reviews. | `docs/controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md` |
| **1.7 — Comprehensive Audit Logging and Compliance** | QA program evidence relies on durable audit trails, UAL visibility, and retention logic; 2.5 should not reinvent that dependency. | `docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md` |
| **1.14 — Data Minimization and Agent Scope Control** | The testing program should verify that datasets, prompts, and test fixtures remain appropriately scoped and do not overreach into unnecessary sensitive content. | `docs/controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md` |
| **1.19 — eDiscovery for Agent Interactions** | Where evaluation and QA artifacts may support examinations or investigations, the retention and discovery posture matters; 2.5 should align its evidence discipline with 1.19. | `docs/controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md` |
| **1.21 — Adversarial Input Logging** | PyRIT and adversarial suites in 2.5 should align with the threat categories, evidence logic, and safe-language framing used in 1.21. | `docs/controls/pillar-1-security/1.21-adversarial-input-logging.md` |
| **2.1 — Managed Environments** | Release validation only means something when the test environment is actually governed and tiered correctly; this is a direct dependency for PIPE and BLK logic. | `docs/controls/pillar-2-management/2.1-managed-environments.md` |
| **2.3 — Change Management and Release Planning** | Material changes should force retesting, new evidence, and fresh approval. 2.5 should map directly to 2.3's change-governance expectations. | `docs/controls/pillar-2-management/2.3-change-management-and-release-planning.md` |
| **2.8 — Access Control and Segregation of Duties** | The QA program itself needs separation of duties for release approval, evidence review, and pipeline permissions. | `docs/controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md` |
| **2.11 — Bias Testing and Fairness Assessment** | The fairness and accessibility review elements of 2.5 should cross-link here so the human adjudication path is consistent across controls. | `docs/controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md` |
| **3.1 — Agent Inventory and Metadata Management** | Every test cycle should resolve to a known agent ID, zone, environment, and owner in the central inventory. Traceability starts here. | `docs/controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md` |
| **3.8 — Copilot Hub and Governance Dashboard** | KPI and dashboard assertions in 2.5 should align to the reporting, oversight, and supervisory dashboard logic used in 3.8. | `docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md` |

---


---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
