# Roadmap: Quality & Consistency Polish (v12)

## Overview

Closes 16 gaps identified by codebase mapping analysis after v11 Technical Remediation. Targets user-facing broken links, residual Azure AD / Tier terminology, quality automation infrastructure, and housekeeping. All gaps are polish-level — no new controls, solutions, or external URL work.

**Gap source:** Codebase mapping analysis (2026-02-11) across tech, architecture, quality, and concern dimensions.

**Execution model:** Each phase has two plans (A/B) targeting non-overlapping file sets for parallel worktree execution.

## Phases

- [x] **Phase 1: Broken Links & Content Consistency** — Fix excluded-doc links, publish missing nav entries, complete Azure AD rename and Zone normalization *(6/7 criteria passed; ~80 Tier→Zone conversions remain in ~35 files — gap closure available)*
- [ ] **Phase 2: Quality Automation & Infrastructure** — Create language linter, add CI validation, sync template conventions, enhance playbook verification
- [ ] **Phase 3: Housekeeping** — Remove stale output files, create missing EXPECTED.md specs, fix Excel count, update milestone history

## Phase Details

### Phase 1: Broken Links & Content Consistency
**Goal:** Resolve user-facing broken links caused by exclude_docs and complete the Azure AD / Tier→Zone terminology sweeps started in v11
**Depends on:** Nothing (highest user impact)
**Requirements:** BLK-01 through BLK-03, CSW-01 through CSW-04
**Success Criteria:**
  1. No docs link to files excluded via exclude_docs (or exclusions removed)
  2. regulatory-mappings.md reachable from site navigation (or all inbound links removed)
  3. CONTROL-INDEX.md reachable from site navigation (or linking docs updated)
  4. Zero "Azure AD" instances remain in published docs
  5. Zero "Tier 1/2/3" or "Level 1/2/3" instances remain without mapping note
  6. solutions-integration.md statuses and versions match solutions-index.md
  7. Cross-Solution Integration status updated from WIP to Completed
**Plans:** 2 (A = Navigation/config + solution sync, B = Terminology sweep — no file overlap)

Plans:
- [x] 01-01-PLAN.md — Navigation & Solution Doc Sync (BLK-01 through BLK-03, CSW-03, CSW-04) — Worktree A ✅
- [x] 01-02-PLAN.md — Terminology Sweep (CSW-01, CSW-02) — Worktree B ✅ *(gap: ~80 additional Tier→Zone instances discovered)*
- [ ] 01-03-PLAN.md — Control File Tier→Zone Sweep + Minor Fixes (CSW-02 gap closure) — Wave 1
- [ ] 01-04-PLAN.md — Playbook File Tier→Zone Sweep (CSW-02 gap closure) — Wave 1

### Phase 2: Quality Automation & Infrastructure
**Goal:** Build automated quality gates (language linter, CI integration) and align templates/validation scripts with current conventions
**Depends on:** Nothing (independent of Phase 1)
**Requirements:** QAI-01 through QAI-05
**Success Criteria:**
  1. scripts/verify_language_rules.py exists and catches prohibited FSI phrases
  2. CI workflow includes verify_controls.py step
  3. control-setup-template.md uses "Implementation Playbooks" heading and current footer
  4. verify_templates.py checks current canonical footer values
  5. verify_controls.py validates that 4 standard playbook files exist per control
**Plans:** 2 (A = Linter + CI, B = Templates + validation — no file overlap)

Plans:
- [ ] 02-01-PLAN.md — Language Linter & CI Integration (QAI-01, QAI-02) — Worktree A
- [ ] 02-02-PLAN.md — Template & Validation Script Updates (QAI-03, QAI-04, QAI-05) — Worktree B

### Phase 3: Housekeeping
**Goal:** Clean up stale artifacts, create missing screenshot specs, fix Excel validation count, and update milestone history
**Depends on:** Phase 1 (terminology sweep may touch some overlapping files)
**Requirements:** HSK-01 through HSK-04
**Success Criteria:**
  1. Stale root output files deleted or gitignored (build_*.txt, verify_*.txt)
  2. EXPECTED.md files exist for all 10 missing controls (1.22–1.24, 2.17–2.21, 3.10, 4.7)
  3. v11 REQUIREMENTS.md checkboxes reflect actual delivery status
  4. verify_excel_templates.py expects 62 controls (not 61)
**Plans:** 2 (A = Stale files + Excel fix, B = EXPECTED.md + history — no file overlap)

Plans:
- [ ] 03-01-PLAN.md — Stale File Cleanup & Excel Fix (HSK-01, HSK-04) — Worktree A
- [ ] 03-02-PLAN.md — Screenshot Specs & Milestone History (HSK-02, HSK-03) — Worktree B

## Progress

| Phase | Plans Complete | Status |
|-------|---------------|--------|
| 1. Broken Links & Content Consistency | 2/4 | Gap closure plans ready (01-03, 01-04) |
| 2. Quality Automation & Infrastructure | 0/2 | Not started |
| 3. Housekeeping | 0/2 | Not started |

## Parallel Execution Guide

Each phase's two plans target **non-overlapping files** and can run in parallel worktrees:

| Phase | Plan A (Worktree A) | Plan B (Worktree B) |
|-------|---------------------|---------------------|
| 1 | mkdocs.yml, docs/reference/solutions-integration.md, docs/reference/solutions-index.md, docs/getting-started/quick-start.md, docs/getting-started/faq.md, docs/reference/solutions-coverage-gaps.md | docs/reference/portal-paths-quick-reference.md, docs/scripts/script-validation-guide.md, docs/playbooks/control-implementations/2.15/*, 2.14/*, 1.8/*, 1.18/*, 4.1/*, 3.2/*, docs/framework/governance-fundamentals.md, docs/playbooks/control-implementations/2.17/* |
| 2 | scripts/verify_language_rules.py (new), .github/workflows/publish_docs.yml | docs/templates/control-setup-template.md, scripts/verify_templates.py, scripts/verify_controls.py |
| 3 | .gitignore, scripts/verify_excel_templates.py, root *.txt files (delete) | docs/images/{1.22,1.23,1.24,2.17,2.18,2.19,2.20,2.21,3.10,4.7}/EXPECTED.md (new), .planning/milestones/v11-REQUIREMENTS.md |

**Worktree setup:**
```bash
git worktree add ../FSI-AgentGov-WTA -b v12/phase-N-track-a
git worktree add ../FSI-AgentGov-WTB -b v12/phase-N-track-b
```

## Coverage

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| BLK-01 | 1 | 01-01 | Fix 5 docs linking to exclude_docs files |
| BLK-02 | 1 | 01-01 | Add regulatory-mappings.md to nav (or remove inbound links) |
| BLK-03 | 1 | 01-01 | Add CONTROL-INDEX.md to nav (or redirect links) |
| CSW-01 | 1 | 01-02 | Complete Azure AD → Microsoft Entra ID rename |
| CSW-02 | 1 | 01-02 | Complete Tier/Level → Zone normalization |
| CSW-03 | 1 | 01-01 | Sync solutions-integration.md with solutions-index.md |
| CSW-04 | 1 | 01-01 | Update Cross-Solution Integration status to Completed |
| QAI-01 | 2 | 02-01 | Create verify_language_rules.py linter |
| QAI-02 | 2 | 02-01 | Add verify_controls.py to CI workflow |
| QAI-03 | 2 | 02-02 | Sync control-setup-template.md with conventions |
| QAI-04 | 2 | 02-02 | Update verify_templates.py for current footers |
| QAI-05 | 2 | 02-02 | Add playbook existence check to verify_controls.py |
| HSK-01 | 3 | 03-01 | Delete/gitignore stale root output files |
| HSK-02 | 3 | 03-02 | Create 10 missing EXPECTED.md files |
| HSK-03 | 3 | 03-02 | Update v11 REQUIREMENTS.md checkboxes |
| HSK-04 | 3 | 03-01 | Fix Excel expected count 61→62 |

**Total: 16/16 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-11*
*Depth: comprehensive*
*Phases: 3 (links+consistency -> automation -> housekeeping)*
