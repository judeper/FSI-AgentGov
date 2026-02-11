# Requirements: SSPM Control Coverage Remediation (v14)

## Requirement Categories

| Code | Category | Count |
|------|----------|-------|
| CTL | Control SSPM Alignment | 3 |
| PLB | Playbook Remediation | 3 |
| HBL | Hardening Baseline Production | 3 |
| REF | Reference & Catalog Updates | 2 |
| VAL | Validation & Quality | 2 |
| **Total** | | **13** |

## CTL - Control SSPM Alignment

- [ ] **CTL-01:** Bump Control 3.7 (PPAC Security Posture Assessment) to v1.3 — the only SSPM-mapped control still at v1.2; align footer, verify hardening section completeness with other v1.3 controls
- [ ] **CTL-02:** Verify all 27 SSPM alert configuration points have matching verification criteria in their parent controls (1.1, 1.7, 1.8, 1.18, 2.1, 3.7, 3.8) — audit each alert from sspm-alert-mapping.md against the control's Section 9 (Verification Criteria) and add any missing items
- [ ] **CTL-03:** Add GLIC cross-reference advisory to Control 1.11 (Conditional Access / MFA) and Control 1.1 — the SSPM scanner flags MFA enforcement (Ref 41) and Guest User access (Ref 39) as valid posture checks that fall outside the current Copilot agent governance perimeter; add advisory notes acknowledging these as complementary identity controls

## PLB - Playbook Remediation

- [ ] **PLB-01:** Audit 7 portal-walkthrough playbooks (1.1, 1.7, 1.8, 1.18, 2.1, 3.7, 3.8) against the 27-item hardening checklist and remediate any SSPM-detectable settings not covered by explicit portal steps
- [ ] **PLB-02:** Update 7 verification-testing playbooks with SSPM-informed test cases — add test steps that validate the specific SSPM-flagged settings (e.g., "verify authentication is not set to No Authentication" for Control 1.1, "verify audit retention ≥ 180 days" for Control 1.7)
- [ ] **PLB-03:** Add hardening baseline cross-links to the Implementation Playbooks section (Section 8) of all 7 SSPM-mapped controls — ensure each control links to the Configuration Hardening Baseline advanced implementation as a supplementary reference

## HBL - Hardening Baseline Production

- [ ] **HBL-01:** Add automation feasibility classification column to the 27-item hardening baseline checklist — categorize each item as **Automated** (API-queryable via Power Platform Admin Connector or Graph), **Semi-Automated** (requires Copilot Studio management API, currently limited), or **Manual Attestation** (no API; screenshot + attestation required)
- [ ] **HBL-02:** Create PowerShell verification script (`scripts/governance/Invoke-HardeningBaselineCheck.ps1`) that validates the automatable subset of the 27-item checklist (items 7–9 audit logging, items 14–17 environment provisioning) via Power Platform Admin Connector and Graph API — output pass/fail per item with evidence export
- [ ] **HBL-03:** Add evidence export procedures and zone-specific review cadence guidance to the hardening baseline — document how organizations export baseline check results for regulatory examination evidence (following the SHA-256 hash pattern used by other solutions)

## REF - Reference & Catalog Updates

- [ ] **REF-01:** Add Configuration Hardening Baseline to solutions-index.md catalog and solutions-coverage-gaps.md — update solutions coverage for Controls 1.1, 1.7, 1.8, 1.18, 2.1, 3.7, 3.8 to reflect the new hardening baseline as coverage enhancement
- [ ] **REF-02:** Update CONTROL-INDEX.md control descriptions for the 7 SSPM-mapped controls to note v1.3 enhancements (SSPM-aligned configuration points and verification criteria additions)

## VAL - Validation & Quality

- [ ] **VAL-01:** All 7 SSPM-mapped controls pass `verify_controls.py` with v1.3 footer validation and `mkdocs build --strict` produces 0 errors
- [ ] **VAL-02:** Run `verify_language_rules.py` across all 7 updated controls + 7 updated playbooks + hardening baseline to confirm zero prohibited FSI phrases

## Out of Scope

| Item | Reason |
|------|--------|
| Configuration Hardening Baseline Validator solution (full Power Automate + Dataverse) | Planned for future milestone; this milestone creates the script-level foundation only |
| GLIC controls (MFA, Guest access) as new framework controls | Outside Copilot agent governance perimeter; advisory cross-reference only |
| Excluded SSPM alerts (D365, Power Pages — 15 items) | Out of scope per framework boundary decisions |
| Real-time SSPM integration | Framework uses batch/daily feeds; no SSPM webhook integration |
| Third-party SSPM tool naming in published docs | Design decision: no vendor names in published documentation |

## Traceability

| Requirement | SSPM Alert Refs | Controls Affected |
|-------------|----------------|-------------------|
| CTL-01 | All 27 (via hardening table) | 3.7 |
| CTL-02 | 2–6, 9, 11, 14, 18, 20–21, 23–38, 40, 42 | 1.1, 1.7, 1.8, 1.18, 2.1, 3.7, 3.8 |
| CTL-03 | 39, 41 (excluded GLIC) | 1.1, 1.11 |
| PLB-01 | All 27 | 1.1, 1.7, 1.8, 1.18, 2.1, 3.7, 3.8 |
| PLB-02 | All 27 | 1.1, 1.7, 1.8, 1.18, 2.1, 3.7, 3.8 |
| PLB-03 | — | 1.1, 1.7, 1.8, 1.18, 2.1, 3.7, 3.8 |
| HBL-01 | All 27 | 3.7 (baseline host) |
| HBL-02 | 7–9, 14–17 (automatable) | 1.7, 2.1 |
| HBL-03 | All 27 | 3.7 (baseline host) |
| REF-01 | — | All 7 + solutions catalog |
| REF-02 | — | All 7 |
| VAL-01 | — | All 7 |
| VAL-02 | — | All 7 + playbooks + baseline |

---
*Requirements defined: 2026-02-11*
*Source: SSPM alert-to-control mapping analysis (maintainers-local/sspm-alert-mapping.md) — 42 alerts analyzed, 27 in-scope*
