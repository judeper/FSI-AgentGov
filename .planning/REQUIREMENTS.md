# Requirements: Quality & Consistency Polish (v12)

## Requirement Categories

| Code | Category | Count |
|------|----------|-------|
| BLK | Broken Link Fixes | 3 |
| CSW | Consistency Sweep | 4 |
| QAI | Quality Automation & Infrastructure | 5 |
| HSK | Housekeeping | 4 |
| **Total** | | **16** |

## BLK - Broken Link Fixes

- [ ] **BLK-01:** Fix 5 documents that link to files excluded via exclude_docs (CONTROL-INDEX.md, regulatory-mappings.md) - either remove from exclude_docs or update linking documents to use alternative references
- [ ] **BLK-02:** Add regulatory-mappings.md to published site navigation (or remove all inbound links from Control 1.7 and nist-ai-rmf-crosswalk.md)
- [ ] **BLK-03:** Add CONTROL-INDEX.md to published site navigation (or update quick-start.md, faq.md, and solutions-coverage-gaps.md to link to the existing controls/index.md instead)

## CSW - Consistency Sweep

- [ ] **CSW-01:** Complete Azure AD to Microsoft Entra ID rename across remaining 10+ instances (portal-paths-quick-reference.md, script-validation-guide.md, 2.15 troubleshooting, 2.14 powershell-setup, 1.8 powershell-setup, 1.18 portal-walkthrough, and any others found)
- [ ] **CSW-02:** Complete Tier 1/2/3 to Zone 1/2/3 normalization in remaining 10+ instances (solutions-index.md, solutions-coverage-gaps.md, 1.8 verification-testing, 4.1 portal-walkthrough, 3.2 verification-testing, and any others), plus fix 3 Level instances in governance-fundamentals.md and 2.17 portal-walkthrough
- [ ] **CSW-03:** Sync solutions-integration.md solution statuses and version numbers with solutions-index.md (at minimum: CAA, Scope Drift Monitor, DEC - update WIP to Completed, version numbers, directory tree annotations)
- [ ] **CSW-04:** Update Cross-Solution Integration solution status from WIP to Completed in solutions-integration.md and solutions-index.md where applicable

## QAI - Quality Automation & Infrastructure

- [ ] **QAI-01:** Create scripts/verify_language_rules.py - scans all docs/**/*.md for prohibited FSI phrases (ensures compliance, guarantees, will prevent, eliminates risk) and fails with exit code 1 if any found
- [ ] **QAI-02:** Add verify_controls.py as a step in the CI publish_docs.yml workflow so structural regressions block deployment
- [ ] **QAI-03:** Sync docs/templates/control-setup-template.md with actual control conventions - change Implementation Guides to Implementation Playbooks, update footer version/date to current canonical values
- [ ] **QAI-04:** Update scripts/verify_templates.py to check for current canonical footer values (not stale v1.1 / January 2026)
- [ ] **QAI-05:** Add playbook existence validation to scripts/verify_controls.py - for each control X.Y, verify the 4 standard playbook files exist under docs/playbooks/control-implementations/X.Y/

## HSK - Housekeeping

- [ ] **HSK-01:** Delete or .gitignore stale root output files: verify_output.txt, build_output.txt, build_out2.txt, build_err.txt, build_validation_p5.txt, verify_out2.txt
- [ ] **HSK-02:** Create missing docs/images/{id}/EXPECTED.md screenshot specification files for 10 controls: 1.22, 1.23, 1.24, 2.17, 2.18, 2.19, 2.20, 2.21, 3.10, 4.7
- [ ] **HSK-03:** Update .planning/REQUIREMENTS.md (v11) checkboxes from unchecked to checked to match actual delivery status (cosmetic fix for historical accuracy)
- [ ] **HSK-04:** Correct Excel dashboard expected control count from 61 to 62 in scripts/verify_excel_templates.py

## Out of Scope

| Item | Reason |
|------|--------|
| New control authoring | v12 is polish-only |
| New solution development | Companion repo scope |
| External URL validation (456+ Learn URLs) | Deferred - requires infrastructure investment |
| Pseudocode cmdlet replacement | Blocked until Microsoft ships agent management APIs |
| Preview feature date updates (3.8, 3.1, 1.5) | Deferred to quarterly review cadence |
| Phase directory archival (.planning/phases/) | Low risk, defer to future housekeeping |

---
*Requirements defined: 2026-02-11*
*Source: Codebase mapping analysis (4 dimensions: tech, arch, quality, concerns)*
