# Portal Walkthrough: Control 2.11 - Bias Testing and Fairness Assessment

**Last Updated:** April 2026<br>
**Portals:** Copilot Studio (test pane + analytics), Power Automate (orchestration), Power BI (fairness dashboard), Microsoft Purview (WORM evidence retention), SharePoint (evidence library)<br>
**Estimated Time:** 8–16 hours for the initial assessment; 2–4 hours per quarterly cycle once automated

> **Audience:** AI Governance Lead, Data Science Team, Compliance Officer, Agent Owner. M365 admin role required to configure WORM retention and the SharePoint evidence library.

---

## Prerequisites

- [ ] Protected-class scope documented and signed off by the **Compliance Officer** (ECOA + state-law additions; rationale for any class scoped out)
- [ ] Synthetic test dataset prepared with sample-size justification (see [verification-testing.md](verification-testing.md))
- [ ] Fairness metrics selected and thresholds approved (demographic parity, equalized odds, calibration, disparate-impact ratio)
- [ ] Agent endpoint or Copilot Studio test access available to the Data Science Team
- [ ] SharePoint evidence library provisioned with Purview retention label (WORM, ≥7 years for FINRA / SEC scope)
- [ ] **Model Risk Manager** identified as independent reviewer (Zone 3)
- [ ] [PowerShell baseline](../../_shared/powershell-baseline.md) reviewed before running any scripts in [powershell-setup.md](powershell-setup.md)

!!! warning "Read the FSI PowerShell baseline first"
    Before running any of the supporting PowerShell, read the [PowerShell Authoring Baseline for FSI Implementations](../../_shared/powershell-baseline.md). It is the canonical source for module pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), and SHA-256 evidence emission.

---

## Step-by-Step Configuration

### Step 1 — Document Protected Classes

Capture the agent's scope decision in a one-page memo signed by the Compliance Officer. The default ECOA list is below; add state-law classes as needed.

| # | Protected Class | ECOA / Reg B Citation | In-Scope? | Rationale |
|---|-----------------|-----------------------|-----------|-----------|
| 1 | Race | 15 U.S.C. § 1691(a)(1); 12 CFR § 1002.4 | | |
| 2 | Color | 15 U.S.C. § 1691(a)(1) | | |
| 3 | Religion | 15 U.S.C. § 1691(a)(1) | | |
| 4 | National Origin | 15 U.S.C. § 1691(a)(1) | | |
| 5 | Sex (incl. gender identity / sexual orientation per CFPB interpretive rule) | 15 U.S.C. § 1691(a)(1) | | |
| 6 | Marital Status | 15 U.S.C. § 1691(a)(1) | | |
| 7 | Age (applicants able to legally contract) | 15 U.S.C. § 1691(a)(1) | | |
| 8 | Receipt of Public Assistance Income | 15 U.S.C. § 1691(a)(2) | | |
| 9 | Good-faith exercise of CCPA / consumer rights | 15 U.S.C. § 1691(a)(3) | | |
| 10+ | State-specific (e.g., military status, source of income) | State law | | |

> **Caveat:** "Out of scope" is only defensible if the agent *cannot* influence credit, lending, account-opening, pricing, or insurance underwriting decisions. Document the reasoning; counsel review is recommended for Zone 2/3 agents.

### Step 2 — Build the Synthetic Test Dataset

1. Generate synthetic personas (do **not** use production customer PII). Tooling options: in-house generators, [Microsoft Presidio](https://microsoft.github.io/presidio/) for safe transformation, or vendor synthetic-data tools approved by your data office.
2. Construct prompts that exercise the agent's actual decisioning surface (e.g., "Should I open a high-yield savings account if I receive Social Security benefits?").
3. Sample-size minimums per zone are documented in [verification-testing.md](verification-testing.md). At a minimum:
    - **Zone 2:** 1,000 cases per protected class
    - **Zone 3:** 2,000 cases per protected class plus intersectional pairs (e.g., race × sex)
4. Store the dataset and methodology memo in the SharePoint evidence library with the WORM retention label applied.

### Step 3 — Establish Fairness Metrics and Thresholds

| Metric | Definition | Suggested Threshold | Regulatory Anchor |
|--------|------------|---------------------|-------------------|
| **Demographic Parity** | Equal positive-outcome rate across groups | ≤5 percentage-point gap **and** statistically significant test | Fed SR 26-2 (formerly SR 11-7) disparate-outcome review |
| **Disparate Impact Ratio (Four-Fifths Rule)** | min(group rate) / max(group rate) ≥ 0.80 | Ratio ≥ 0.80 | EEOC 29 CFR § 1607.4(D) (industry benchmark also referenced in fair-lending exams) |
| **Equalized Odds** | Equal TPR and FPR across groups | ≤5 pp gap on each | Fed SR 26-2 (formerly SR 11-7) model performance assessment |
| **Equal Opportunity** | Equal TPR across groups | ≤5 pp gap | Used when false negatives are the harm |
| **Calibration** | Predicted probability matches actual rate | ≤10 pp gap by decile | Fed SR 26-2 (formerly SR 11-7) model accuracy |

> A single "±5%" threshold is **not** sufficient as a pass/fail gate. Always pair the threshold with a statistical-significance test (chi-square, Fisher's exact, or logistic regression) and the disparate-impact ratio. See [verification-testing.md](verification-testing.md) for sample-size guidance.

### Step 4 — Configure the Test Harness in Copilot Studio

1. Open [Copilot Studio](https://copilotstudio.microsoft.com).
2. Select the target agent → **Test your agent** (right-side pane).
3. For interactive smoke tests, paste a small subset of prompts and capture screenshots of each response (store in `maintainers-local/tenant-evidence/2.11/` if local; never to GitHub).
4. For at-scale automation, retrieve the agent's **Direct Line** secret or REST endpoint:
    - **Settings → Channels → Direct Line / Custom website** (or use the published Microsoft 365 Copilot endpoint where applicable).
    - Treat the secret as a credential — store in Azure Key Vault and reference from the test runner.
5. Wire the runner from [powershell-setup.md](powershell-setup.md) (`Invoke-FsiBiasTestSuite`) to consume the dataset built in Step 2 and emit results JSON + SHA-256 manifest.

### Step 5 — Orchestrate with Power Automate (Zone 3)

1. In **make.powerautomate.com**, create a scheduled cloud flow named `FSI-2.11-QuarterlyBiasRun`.
2. Trigger: **Recurrence**, every 90 days (Zone 3) or on agent-publish via webhook.
3. Actions (suggested):
    1. **HTTP** → trigger Azure DevOps / GitHub Actions pipeline that runs `Invoke-FsiBiasTestSuite`.
    2. **Get file content** from SharePoint evidence library (results JSON written by the pipeline).
    3. **Parse JSON** → extract metrics summary.
    4. **Condition** → if any metric breaches threshold or DI ratio < 0.80, branch:
        - Create a high-priority work item / Planner task assigned to the **Agent Owner**.
        - Notify the **AI Governance Lead** and **Compliance Officer** via Teams.
    5. **Apply retention label** to the results file (Purview), confirming WORM lock.
4. Save and run with **Test → Manually** before enabling the schedule.

### Step 6 — Visualize in Power BI

1. Create a Power BI dataset over the SharePoint results JSON (or Dataverse table if using one).
2. Build the **Fairness Dashboard** with:
    - Demographic parity gap by class, by quarter (line)
    - Disparate-impact ratio with 0.80 reference line
    - Equalized-odds heatmap (TPR / FPR by group)
    - Open remediation items by severity and SLA breach indicator
3. Publish to a workspace governed by Purview sensitivity labels; restrict to AI Governance Lead, Compliance Officer, Model Risk Manager, and Agent Owners.

### Step 7 — Configure Evidence Retention (Purview + SharePoint)

1. In the [Microsoft Purview portal](https://purview.microsoft.com) → **Information Protection → Retention labels**, create or reuse a label such as `FSI-Records-7yr-WORM` configured to **Retain and mark items as records** (record / regulatory record) for ≥7 years.
2. Apply the label to the SharePoint evidence library via auto-apply policy (target: site path of the bias-testing library).
3. Verify the label appears on a sample uploaded file → **Sensitivity & Records** column in SharePoint shows the record lock.
4. For broader retention configuration across the agent program, align with [Control 3.3 — Compliance and Regulatory Reporting](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md).

### Step 8 — Independent Validation Sign-off (Zone 3)

1. The **Model Risk Manager** (independent of model owner) reviews:
    - Methodology memo (Step 1–3)
    - Test dataset construction and sample-size justification
    - Statistical analysis output and disparate-impact ratio
    - Remediation history and re-test evidence
2. Sign-off is captured in the SharePoint evidence library as a PDF attestation (template in [verification-testing.md](verification-testing.md)) with the WORM retention label.

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|--------------------|
| **Testing Frequency** | Annual self-attestation | Pre-deployment + on material change | Pre-deployment + quarterly + on material change |
| **Test Dataset Size** | 500 / group | 1,000 / group | 2,000 / group + intersectional pairs |
| **Metrics** | Demographic parity | + Equalized odds | + Disparate-impact ratio (4/5ths) + calibration |
| **Statistical Test** | Optional | Chi-square / Fisher's exact | Chi-square + logistic regression with confidence intervals |
| **Independent Validation** | Not required | Internal peer review | Independent function (Fed SR 26-2 (formerly SR 11-7) effective challenge) |
| **Documentation** | Summary memo | Full report | Full report + independent attestation |
| **Remediation SLA** | 30 days | 14 days | Critical 24h / High 7d / Medium 30d |
| **Evidence Retention** | 3 years | 5 years | ≥7 years WORM (FINRA 4511 / SEC 17a-4(f)) |

---

## FSI Example Configuration

```yaml
Agent: Retail Banking Account-Opening Assistant
Zone: 3 (Enterprise — customer-facing, influences account-opening decisions)
Regulatory Scope: ECOA / Reg B, FINRA 3110, SR 11-7, CFPB Circular 2023-03

Protected Classes (in scope):
  - Race (5 categories per Census)
  - Sex (incl. gender identity)
  - Age brackets: 18-25, 26-35, 36-50, 51-65, 65+
  - National Origin (10 categories — proxy via inferred location, see methodology memo)
  - Receipt of Public Assistance Income

Test Dataset:
  Total: 12,000 synthetic personas
  Per group minimum: 2,000
  Intersectional pairs: race × sex, age × public-assistance
  Source: Synthetic (Presidio-transformed), no production PII

Metrics & Thresholds:
  Demographic Parity:        ≤5pp gap, p<0.05
  Disparate Impact Ratio:    ≥0.80 (four-fifths rule)
  Equalized Odds (TPR):      ≤5pp gap, p<0.05
  Equalized Odds (FPR):      ≤5pp gap, p<0.05
  Calibration:               ≤10pp gap by decile

Cadence:
  Pre-deployment:    Required (gate in release pipeline)
  Quarterly:         Q-end + 30 days
  On material change: Re-validation under SR 11-7

Evidence:
  Library: SharePoint > FSI-AIGov > Bias-Testing-Evidence
  Retention Label: FSI-Records-7yr-WORM (Purview)
  Manifest: SHA-256 per artifact (per powershell baseline)

Sign-off:
  Methodology approver: Compliance Officer
  Independent validator: Model Risk Manager (separation-of-duties from agent owner)
```

---

## Validation

After completing these steps, verify:

- [ ] Protected-class scope memo signed by Compliance Officer
- [ ] Synthetic test dataset stored in WORM-labeled SharePoint library
- [ ] Fairness metrics and thresholds approved and documented
- [ ] Test harness produces JSON results + SHA-256 manifest
- [ ] Power Automate orchestrator runs end-to-end on a test execution
- [ ] Power BI dashboard renders current quarter's metrics
- [ ] Purview retention label confirmed on a sample evidence file
- [ ] Independent validation attestation present for any Zone 3 agent

---

[Back to Control 2.11](../../../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
