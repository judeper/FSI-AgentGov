# Verification & Testing: Control 2.11 - Bias Testing and Fairness Assessment

**Last Updated:** April 2026

This playbook is the audit-facing companion to [portal-walkthrough.md](portal-walkthrough.md) and [powershell-setup.md](powershell-setup.md). It defines what evidence to produce, how to test it, and how to attest to the result.

---

## ECOA / Regulation B Protected Classes Reference

The Equal Credit Opportunity Act (ECOA) and Regulation B (12 CFR Part 1002) prohibit discrimination on a prohibited basis in any aspect of a credit transaction. The nine federally protected classes are:

| # | Protected Class | ECOA Citation | Testing Considerations |
|---|-----------------|---------------|------------------------|
| 1 | **Race** | 15 U.S.C. § 1691(a)(1) | Use Census categories; test race proxies (ZIP code, surname) for indirect bias |
| 2 | **Color** | 15 U.S.C. § 1691(a)(1) | Distinct from race; test skin-tone proxies where present |
| 3 | **Religion** | 15 U.S.C. § 1691(a)(1) | Include major religions and non-religious applicants |
| 4 | **National Origin** | 15 U.S.C. § 1691(a)(1) | Country of birth, ancestry, ethnicity; language preference can be a proxy |
| 5 | **Sex** | 15 U.S.C. § 1691(a)(1) | CFPB interpretive rule treats sexual orientation and gender identity as covered |
| 6 | **Marital Status** | 15 U.S.C. § 1691(a)(1) | Single, married, divorced, widowed, separated |
| 7 | **Age** | 15 U.S.C. § 1691(a)(1) | Protect applicants who can legally contract |
| 8 | **Receipt of Public Assistance Income** | 15 U.S.C. § 1691(a)(2) | Recipients of any public assistance program |
| 9 | **Good-faith exercise of CCPA / Consumer Credit Protection Act rights** | 15 U.S.C. § 1691(a)(3) | Applicants who previously exercised consumer credit rights |

> **State-law overlay:** Many states extend protected classes (e.g., sexual orientation in NY/CA, military status in OH, source of income in many jurisdictions). Counsel should confirm the controlling list for each agent's customer footprint.

---

## Cadence by Zone

| Zone | Frequency | Trigger | Primary Owner |
|------|-----------|---------|---------------|
| **Zone 1** | Annual self-attestation | Calendar | Agent Owner |
| **Zone 2** | Pre-deployment + on material change | Release gate / change ticket | Data Science Team |
| **Zone 3** | Pre-deployment + quarterly + on material change | Release gate / Q-end + 30 days / change ticket | AI Governance Lead with independent Model Risk Manager review |

### Zone 3 Quarterly Calendar

| Quarter | Due Date | Activities | Owner |
|---------|----------|------------|-------|
| Q1 | April 30 | Full assessment across all in-scope classes; intersectional pairs | AI Governance Lead |
| Q2 | July 31 | Statistical-parity review; remediation follow-up; trend chart | Compliance Officer |
| Q3 | October 31 | Full assessment; year-to-date trend analysis | AI Governance Lead |
| Q4 | January 31 (next year) | Statistical-parity review; annual summary; independent attestation refresh | Compliance Officer + Model Risk Manager |

---

## Sample-Size and Statistical-Test Guidance

A "±5% threshold" gate is meaningless without a sample-size justification. Use the table below as a floor and document the actual power calculation in the methodology memo.

| Variable Type | Example | Minimum n per Group | Statistical Test |
|---------------|---------|---------------------|------------------|
| Binary | sex (M/F)              | 100  | Chi-square or Fisher's exact |
| Multi-category | race (5 groups)        | 50 per category | Chi-square (omnibus) + pairwise Fisher's exact with Bonferroni correction |
| Continuous | age (years)            | 200 total | Logistic regression with age as predictor |
| Intersectional | race × sex             | 50 per cell | Stratified analysis or interaction term in regression |

> Pair every threshold breach with a significance test (p < 0.05 typical) **and** the disparate-impact ratio. Statistical significance without effect size — or vice versa — produces misleading conclusions.

---

## Manual Verification Steps

### Test 1 — Verify Protected-Class Scope

1. Locate the methodology memo in the SharePoint evidence library.
2. Confirm signature by Compliance Officer, dated within the cadence window.
3. Verify all nine ECOA classes are addressed (in-scope **or** explicitly scoped out with rationale).
4. Verify state-specific classes are addressed for each customer footprint.
5. **Expected:** Signed memo present; every class either tested or has documented out-of-scope rationale.

### Test 2 — Verify Test Dataset

1. Review the synthetic dataset referenced in the latest results envelope (`datasetPath` field).
2. Confirm sample-size minimums per group (table above).
3. Confirm the dataset uses synthetic personas — **no production customer PII**.
4. Verify the dataset itself is stored with the WORM retention label (Purview).
5. **Expected:** Balanced dataset, synthetic origin, retention label applied.

### Test 3 — Review Bias Testing Results

1. Open the most recent `2.11-fairness-metrics-*.json` file.
2. For each protected class, review:
    - Per-group positive-outcome rate
    - Demographic parity gap (≤5 pp threshold)
    - Disparate impact ratio (≥0.80 four-fifths rule)
3. Confirm a downstream statistical-significance file accompanies the metrics file (chi-square / Fisher / regression output).
4. **Expected:** All metrics within threshold OR open remediation items tracked with SLA.

### Test 4 — Verify Statistical Significance

1. Open the worker output (Python Fairlearn / R) referenced in the manifest.
2. Confirm p-values for each protected-class comparison.
3. Confirm confidence intervals are reported, not just point estimates.
4. **Expected:** Significance test executed; p-values and CIs documented.

### Test 5 — Verify Remediation Process

1. List open remediation items in the Power BI dashboard or work-item tracker.
2. For each, verify owner, severity, SLA target, and current status.
3. For closed items, verify re-test evidence (a follow-up `2.11-bias-results-*.json` post-fix).
4. Confirm material model changes triggered Fed SR 26-2 (formerly SR 11-7) re-validation.
5. **Expected:** Open items within SLA; closed items have re-test evidence.

### Test 6 — Verify Independent Validation (Zone 3)

1. Locate the independent validation attestation PDF (template below).
2. Confirm the validator is independent of the agent owner (separation of duties).
3. Confirm attestation is dated within the last 12 months.
4. **Expected:** Signed attestation present, ≤12 months old, validator independent.

### Test 7 — Verify Evidence Integrity

1. Run `Validate-Control-2.11.ps1` (see [powershell-setup.md](powershell-setup.md)).
2. Confirm the SHA-256 manifest matches every file on disk.
3. Confirm Purview retention label present on a sample evidence file.
4. **Expected:** Manifest integrity passes; retention label confirmed.

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-2.11-01 | Protected-class scope memo signed | Memo present, signed by Compliance Officer | |
| TC-2.11-02 | Synthetic dataset, no production PII | Verified synthetic origin | |
| TC-2.11-03 | Sample size meets minimums | All groups ≥ table minimum | |
| TC-2.11-04 | Demographic parity within threshold | Gap ≤ 5 pp | |
| TC-2.11-05 | Disparate-impact ratio (4/5ths) | Ratio ≥ 0.80 | |
| TC-2.11-06 | Equalized-odds gap | TPR and FPR gaps ≤ 5 pp | |
| TC-2.11-07 | Statistical significance reported | Chi-square / Fisher / regression p-value present | |
| TC-2.11-08 | Remediation items within SLA | All open items meet SLA | |
| TC-2.11-09 | Independent validation attestation (Zone 3) | Signed, ≤12 months | |
| TC-2.11-10 | Evidence WORM retention | Purview label applied; manifest hashes match | |

---

## Evidence Collection Checklist

- [ ] Document: Protected-class scope memo (signed PDF)
- [ ] Document: Test dataset methodology and power calculation
- [ ] File: Synthetic test dataset (CSV)
- [ ] File: `2.11-bias-results-*.json` (raw responses)
- [ ] File: `2.11-fairness-metrics-*.json` (computed metrics)
- [ ] File: Statistical-significance output (Python / R)
- [ ] File: `manifest.json` (SHA-256 integrity)
- [ ] Document: Remediation register / Power BI snapshot
- [ ] Document: Independent validation attestation (Zone 3)
- [ ] Confirmation: Purview WORM retention label applied to library

---

## Attestation Statement Template

```markdown
## Control 2.11 Attestation — Bias Testing and Fairness Assessment

**Organization:** [Organization Name]
**Agent / Scope:** [Agent name(s), zone, business function]
**Reporting Period:** [Q# YYYY]
**Control Owner:** [Name, role]
**Independent Validator (Zone 3):** [Name, role — must be independent of agent owner]

I attest that, for the period indicated:

1. Protected classes were documented per ECOA / Regulation B and applicable state law,
   with rationale for any class scoped out (memo signed [date]).

2. The test dataset used [n] synthetic personas across [k] protected classes,
   with minimum [n_min] per group, satisfying the documented power calculation.

3. Bias testing was executed on [date] with the following summary results:
    - Demographic Parity:        [Pass / Fail by class]
    - Disparate Impact Ratio:    [min ratio observed] vs. four-fifths floor (0.80)
    - Equalized Odds:            [Pass / Fail]
    - Calibration:               [Pass / Fail]
    - Statistical significance:  [test, p-values]

4. [n] remediation items were identified at severity:
    - Critical: [count] (24h SLA)
    - High:     [count] (7d SLA)
    - Medium:   [count] (30d SLA)
   All were tracked, [n_closed] closed with re-test evidence, [n_open] open within SLA.

5. Material model changes during the period [were / were not] triggered;
   if triggered, Fed SR 26-2 (formerly SR 11-7) re-validation [is / is not] complete.

6. Evidence is retained in [SharePoint library URL] with Purview WORM retention
   label `[label name]` and SHA-256 integrity manifest.

**Last Test Date:** [Date]
**Next Scheduled Test:** [Date]

**Owner Signature:** _______________________  **Date:** ___________
**Independent Validator Signature (Zone 3):** _______________________  **Date:** ___________
```

---

[Back to Control 2.11](../../../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
