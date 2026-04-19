# Troubleshooting: Control 2.18 — Automated Conflict of Interest Testing

**Last Updated:** April 2026

This playbook covers operational failures of the COI testing pipeline configured in [portal-walkthrough.md](portal-walkthrough.md) and run with the scripts in [powershell-setup.md](powershell-setup.md). For evaluation methodology issues (graders, sample size, thresholds), see [verification-testing.md](verification-testing.md).

---

## Quick-Reference Table

| Symptom | Most Likely Cause | First Action |
|---------|--------------------|--------------|
| Scheduled evaluation does not run | Disabled flow, expired credential, or service-principal token revoked | Check Power Automate run history; verify SP secret expiry in Azure |
| Evaluation runs but every test passes — including known-fail seeds | Wrong agent endpoint or wrong tenant (sovereign-cloud mismatch) | Re-validate endpoint and `-Environment` against [PowerShell baseline](../../_shared/powershell-baseline.md) |
| Evaluation runs but every test fails | Auth token expired or agent endpoint returning error responses scored as "no fee disclosure" | Inspect raw response payloads; refresh token |
| High false-positive rate on classification grader | Grader rubric too narrow; threshold not calibrated | Re-calibrate against a Compliance-labelled set |
| Inconsistent pass / fail across runs of the same scenario | LLM non-determinism | Switch from exact-match to similarity / classification graders; aggregate over n runs |
| Coverage gap surfaced by Compliance | Methodology memo out of date | Refresh memo; expand test set; re-baseline |
| Evidence register hash drift | Artefact edited or replaced after capture | Treat as integrity incident; do **not** edit further; escalate to AI Governance Lead |
| Audit log missing evaluation events | Audit (Premium) not enabled or wrong workload filter | Verify Purview audit configuration |

---

## Detailed Scenarios

### A. Tests Not Executing on Schedule

**Symptoms.** No new entries in evidence library; Power Automate flow shows no recent runs or repeated failures.

**Diagnostics.**
1. In [Power Automate](https://make.powerautomate.com), open the COI evaluation flow → **Run history**.
2. Inspect the most recent failed run — note the exact step and error.
3. If the failure is on the auth step, check the service principal's client secret expiry in Entra (`App registrations → {sp} → Certificates & secrets`).
4. If the failure is on the HTTP step, manually call the agent endpoint with the same payload and token from a workstation to isolate network vs auth vs payload.

**Resolution.**
- Rotate the SP secret; update the Key Vault binding; re-test.
- If the flow is owned by a personal account and the owner has changed roles, transfer ownership to a service principal or shared mailbox account before the next scheduled window. Personal-account ownership is a FINRA Rule 3110 supervisory-continuity gap.
- Re-enable any flow that has been auto-disabled by Power Platform after consecutive failures.

---

### B. False-Clean Results (every test passes — including seeded failures)

**Why this matters.** A false-clean evaluation is the worst outcome of this control. It produces evidence that the agent is compliant when it is not, and the evidence will look authentic to an examiner.

**Most common causes.**
1. **Wrong agent endpoint.** The script ran against a stub or a non-production agent.
2. **Sovereign-cloud mismatch.** Script authenticated against commercial endpoints in a GCC / GCC High / DoD tenant — silently returns success-shaped responses without actually exercising the production agent.
3. **Grader threshold set so low it cannot fail.** Calibration error.
4. **Test set deployed without expected-failure seeds.** The suite never tests the failure path.

**Diagnostics.**
1. Confirm the endpoint URL in the most recent run matches the production agent (compare with the agent's published endpoint in Copilot Studio).
2. Re-run the [PowerShell validator](powershell-setup.md#4-validate-control-218-configuration-read-only) and review the `Cloud` property.
3. Add a deliberate fail-seed scenario (e.g., a prompt that should produce an unsolicited cross-sell pitch); confirm the grader flags it.
4. Inspect grader configuration — confirm the threshold is the value documented in the methodology memo.

**Resolution.** Treat any historical false-clean window as evidence-gap. Do not silently overwrite. Open a remediation ticket, document the cause and corrective action, and re-run for the affected period if feasible.

---

### C. Universal Failure (every test fails)

**Symptoms.** Pass rate drops to ~0% in a single run.

**Likely causes.** Expired bearer token (every response is a 401 / 403); agent endpoint returning an error envelope that the grader scores as "no fee disclosure"; agent decommissioned and traffic going to a placeholder.

**Diagnostics.**
1. Open the detail JSON from the most recent run; inspect the `Response` field for any single test.
2. If the response body looks like an error message, the agent call itself failed — the graders are scoring an error string.
3. Check token expiry / Key Vault rotation policy.

**Resolution.** Refresh credentials; re-run; confirm a healthy mix of pass/fail is restored before declaring the control operational again.

---

### D. High False-Positive Rate on Classification Grader

**Symptoms.** Classification grader flags responses that Compliance, on manual review, considers acceptable.

**Diagnostics.**
1. Pull a sample of 10–20 flagged responses.
2. Review with Compliance — bucket as `true positive`, `borderline`, or `false positive`.
3. If false-positive rate > 10%, the grader rubric is not capturing the conflict signal precisely enough.

**Resolution.**
- Refine the classification rubric with Compliance — add explicit examples of `acceptable` outputs alongside `unacceptable` ones.
- Consider switching from keyword-based to AI-based classification, or layering an AI quality grader to catch subtle signal.
- Re-baseline after changes and document the rubric revision in the methodology memo (this is a controlled change, not a tweak).

---

### E. Non-Deterministic Pass / Fail

**Symptoms.** The same scenario passes some runs and fails others without any agent change.

**Why.** LLM responses are stochastic; exact-match grading on free-text outputs will always have variance.

**Resolution.**
- Replace exact-match graders with similarity or classification graders that operate on meaning, not wording.
- Aggregate per scenario over n runs (the Microsoft Learn iterative framework recommends ≥ 3 runs per critical scenario at the operationalize stage).
- Define pass at the aggregate level (e.g., scenario passes if ≥ 8 of 10 runs pass).
- Document the aggregation method in the methodology memo. An undocumented "best-of-3" rule looks like cherry-picking to an examiner.

---

### F. Coverage Gap Identified

**Symptoms.** Compliance review or examination identifies a conflict scenario not covered by the current test set.

**Diagnostics.**
1. Map the gap to the conflict-type matrix in [verification-testing.md](verification-testing.md).
2. Determine whether the gap is `missing scenario`, `insufficient sample size`, or `missing conflict type`.
3. Assess customer / regulatory exposure of the gap.

**Resolution.** Add scenarios; re-baseline; reflect the addition in the methodology memo with a dated change note. Quarterly coverage review with Compliance is the long-term mitigation.

---

### G. Evidence Register Hash Drift

**Symptoms.** The validator reports `HashDriftCount > 0`.

**Treat as an integrity incident.** Do not edit further. Do not regenerate the register from current files (that would launder the drift).

**Diagnostics.**
1. Identify which file(s) drifted.
2. Check SharePoint version history (or backup) for the original artefact.
3. Determine whether the change was a benign re-export or a substantive edit.

**Resolution.**
- Restore the original from version history if possible.
- If not possible, document the incident in the WSPs, retain both the registered hash and the current artefact, and explain the gap in the next attestation.
- Strengthen access controls on the evidence library so artefacts cannot be silently overwritten in future.

---

### H. Audit Log Missing Evaluation Events

**Symptoms.** Purview audit search for `Operation = AgentEvaluationRun` (or equivalent) returns no rows for a period when runs are known to have happened.

**Diagnostics.**
1. Confirm Audit (Premium) is enabled (Microsoft Purview portal → Audit → Settings).
2. Confirm Copilot interactions are in audit scope.
3. Verify the search uses the correct workload (`MicrosoftCopilotStudio` or as documented in your tenant).
4. Check audit retention — entries older than retention are gone.

**Resolution.** Re-enable audit if disabled; broaden the search filter; raise a Microsoft support case if entries are missing within the configured retention. The exported result files remain authoritative; the audit log is corroborating evidence.

---

## How to Confirm the Control is Genuinely Active

A "green dashboard" is not enough. To confirm the control is doing its job:

1. **Recent run within cadence window** — validator returns `RecentRunOk = $true`.
2. **Healthy mix of pass / fail** — a 100% pass rate over many runs is suspicious; either the test set is too easy or the graders are too lenient.
3. **At least one fail-seed scenario in the suite** — proves the graders can actually fail.
4. **Evidence register integrity** — `HashDriftCount = 0`.
5. **Recent material agent change triggered a re-evaluation** — confirm by correlating change-management tickets with run timestamps.
6. **Independent reviewer (Zone 3) has signed off** within the quarter.

---

## Escalation Path

| Owner | When to Engage |
|-------|----------------|
| Agent Owner | Test failures attributable to agent prompt / configuration |
| AI Governance Lead | Threshold or grader-design questions; cadence misses; evidence drift |
| Compliance Officer | Methodology changes; coverage gaps; threshold revisions; attestation exceptions |
| Model Risk Manager (Zone 3) | Independent validation; methodology approval; cross-control issues with 2.6 / 2.11 |
| Microsoft Support | Platform-level evaluation framework or audit log defects |

---

## Known Limitations (April 2026)

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| LLM response variability | Pass / fail can vary on identical inputs | Use similarity / classification graders; aggregate over n runs |
| No platform-native COI rubric | Each firm builds its own rubric | Anchor rubric in WSPs; review quarterly with Compliance |
| Subtle bias hard to detect with automation alone | Some conflicts only surface in manual review | Combine automated suite with sampled human review under FINRA Rule 3110 |
| Test-set staleness | Customer language and product mix evolve | Quarterly refresh with sanitized authentic queries |
| Evaluation framework feature evolution | Microsoft Learn surfaces change between releases | Re-validate `Last UI Verified` date on the control doc each quarter |

---

[Back to Control 2.18](../../../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)
