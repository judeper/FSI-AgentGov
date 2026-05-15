# Troubleshooting: Control 2.11 - Bias Testing and Fairness Assessment

**Last Updated:** April 2026

This playbook covers common operational and methodological issues encountered when running the Control 2.11 program. For setup, see [portal-walkthrough.md](portal-walkthrough.md); for scripts, see [powershell-setup.md](powershell-setup.md).

---

## Quick Reference

| Issue | Likely Cause | Resolution |
|-------|--------------|------------|
| Insufficient test data | Sample sizes below power-calculation floor | Expand synthetic dataset; recompute power |
| Cannot classify outcomes | Free-text responses with no rubric | Define explicit rubric; consider LLM-judge with human spot-check |
| Persistent bias after fix | Knowledge-source contamination or system-prompt leakage | Audit knowledge sources and system prompt; widen test scope |
| "Pass" but feels wrong | Threshold without significance test | Pair threshold with chi-square / Fisher / regression |
| Disparate impact ratio close to 0.80 | Small effect plus small sample | Increase n; report CI for the ratio |
| Manifest hash mismatch | Evidence file edited after emission | Re-run pipeline; do not edit emitted files in place |
| Quarterly cadence missed | No automated reminder; ownership gap | Wire Power Automate reminder; assign in RACI |
| Intersectional bias hidden | Marginal analysis only | Add intersectional cells (race × sex, age × income source) |
| Synthetic data too "clean" | Generator under-represents real variation | Calibrate generator against population statistics; add noise |
| Re-validation skipped after model change | No release gate | Add CI gate that calls `Validate-Control-2.11.ps1` |

---

## Detailed Troubleshooting

### Issue 1 — Test Dataset Too Small (Inconclusive Results)

**Symptoms:** Chi-square / Fisher tests return p-values that fluctuate run-to-run; confidence intervals on the disparate-impact ratio span both above and below 0.80.

**Diagnosis:** Sample sizes per group are below what the power calculation requires for the effect size you want to detect.

**Resolution:**

1. Recompute statistical power for the smallest effect you care about (e.g., a 5 pp parity gap at α = 0.05, power = 0.80).
2. Generate additional synthetic cases for under-powered groups; rebalance the dataset.
3. Re-run `Invoke-FsiBiasTestSuite` and `Get-FsiFairnessMetrics`.
4. Document the new sample sizes in the methodology memo and replace the old version in the WORM library (the previous version is preserved by the retention label).

---

### Issue 2 — Outcome Classification Is Subjective

**Symptoms:** Two reviewers classify the same agent response differently; pass/fail varies by who runs the analysis.

**Diagnosis:** Outcome rubric is not specific enough. Free-text agent responses do not map cleanly to "Positive" / "Negative" without explicit criteria.

**Resolution:**

1. Define a written rubric with concrete examples for each outcome class.
2. For Zone 3, use **two independent reviewers** plus inter-rater agreement (Cohen's kappa ≥ 0.80) before declaring results final.
3. If using an LLM-judge, document the judge model, prompt, and version; spot-check ≥10% of classifications by a human reviewer.
4. Capture the rubric and reviewer agreement statistics in the evidence library.

---

### Issue 3 — Persistent Bias After Remediation

**Symptoms:** A second test run after a fix shows the same disparate impact.

**Diagnosis:** Common root causes:

- **Knowledge-source contamination** — RAG sources contain biased framing.
- **System-prompt leakage** — the system prompt steers the model toward certain outcomes.
- **Training data inheritance** — the underlying foundation model carries bias the prompt cannot override.
- **Proxy variables** — the agent infers protected attributes from non-protected fields (ZIP code, language, name).

**Resolution:**

1. Audit knowledge sources for biased phrasing; reword or remove.
2. Review the system prompt for words / framing that imply outcomes for specific groups.
3. Add explicit fairness instructions to the system prompt; re-test.
4. If the underlying model carries the bias, escalate to model selection — a different foundation model may be required for the use case.
5. Material model changes invoke re-validation under Fed SR 26-2 (formerly SR 11-7). Capture the change ticket and re-validation memo in the evidence library.
6. **Do not** declare the issue closed without a passing re-test cycle.

---

### Issue 4 — Threshold "Pass" Without Significance

**Symptoms:** Demographic parity gap is 4 pp (under the 5 pp threshold) — but with only 50 cases per group.

**Diagnosis:** The threshold check passed but the result is statistically meaningless.

**Resolution:**

1. Always pair a threshold check with a significance test. The PowerShell scripts emit metrics; run a Python (Fairlearn + scipy) or R worker for chi-square / Fisher / regression.
2. Report **both** point estimate and 95% confidence interval for parity gap and disparate-impact ratio.
3. If the CI for the disparate-impact ratio crosses 0.80, treat as inconclusive — increase n and re-run.

---

### Issue 5 — Disparate Impact Ratio Hovering at 0.80

**Symptoms:** DI ratio reports 0.81 one quarter, 0.78 the next. Hard to declare a stable result.

**Diagnosis:** Borderline disparate impact with high variance.

**Resolution:**

1. Treat 0.80 as a *floor*, not a target. Borderline values warrant remediation even if technically "passing."
2. Increase sample size to tighten the CI.
3. Consider whether the underlying outcome variable is the right one — e.g., recommendation rate vs. recommended product class may give different signals.
4. Document the borderline status in the attestation; do not paper over it.

---

### Issue 6 — Intersectional Bias Hidden by Marginal Analysis

**Symptoms:** Each protected class passes individually, but customer complaints suggest bias for specific intersections (e.g., older women, Black men).

**Diagnosis:** Marginal (one-class-at-a-time) analysis can hide intersectional patterns.

**Resolution:**

1. Add intersectional cells to the test dataset for high-risk pairs (race × sex, age × public-assistance, national-origin × sex).
2. Compute fairness metrics at the cell level, not just the marginal level.
3. Sample-size requirement applies *per cell* — e.g., 50 per cell, not 50 per marginal group.
4. Report intersectional results separately in the Power BI dashboard.

---

### Issue 7 — Manifest SHA-256 Mismatch

**Symptoms:** `Validate-Control-2.11.ps1` reports a hash mismatch.

**Diagnosis:** An evidence file was edited (or re-saved by a viewer) after emission. WORM retention prevents this in production but local working copies can drift.

**Resolution:**

1. Never edit emitted JSON files in place — re-run the pipeline.
2. Confirm Purview WORM retention is applied to the SharePoint library (prevents post-emission edits).
3. If a legitimate correction is needed, emit a new version, update the manifest, and document the supersession in the methodology memo.

---

### Issue 8 — Quarterly Cadence Missed

**Symptoms:** Last results file is more than 100 days old; `Validate-Control-2.11.ps1` flags cadence.

**Diagnosis:** No automation, no reminder, or unclear ownership.

**Resolution:**

1. Wire the Power Automate orchestrator (Step 5 in [portal-walkthrough.md](portal-walkthrough.md)) with a 90-day recurrence trigger.
2. Add a 30-day prior reminder to the AI Governance Lead and Compliance Officer.
3. Confirm the RACI for this control names a single accountable owner per quarter.
4. For the missed quarter, run a catch-up assessment and document the gap and remediation in the next attestation.

---

## Escalation Path

1. **Agent Owner** — initial triage, prompt / knowledge-source remediation
2. **Data Science Team** — methodology, statistical analysis, threshold tuning
3. **AI Governance Lead** — methodology approval, cross-agent patterns
4. **Compliance Officer** — regulatory interpretation (ECOA / Reg B applicability, fair-lending exam posture)
5. **Model Risk Manager** — independent challenge, Fed SR 26-2 (formerly SR 11-7) effective challenge
6. **Legal** — fair-lending counsel for material findings or examination prep

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| LLM responses are stochastic | Same input may yield different outputs | Run each prompt ≥3 times; report variance; consider deterministic settings (`temperature=0`) where supported |
| Synthetic data may not reflect real-world distributions | False sense of fairness | Calibrate generator against population statistics; supplement with anonymized production sampling per privacy review |
| Outcome classification is subjective | Inter-rater drift | Two-reviewer model + Cohen's kappa; document rubric |
| No regulator-blessed FSI fairness toolkit | Methodology open to challenge | Document methodology thoroughly; align with NIST AI RMF MEASURE-2.11 and Fed SR 26-2 (formerly SR 11-7); use Microsoft Responsible AI Toolbox / Fairlearn as reference |
| Single foundation-model dependency | Model-level bias hard to remediate via prompts | Track at model-selection level; escalate to model risk |
| Disparate-impact ratio sensitive to small denominators | Volatile near-floor | Require minimum group n in methodology; report CIs |

---

[Back to Control 2.11](../../../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
